import subprocess
import sys
import json
import os
import tempfile
import shutil


def _set_resource_limits():
    """Cap memory and file writes at the OS level. Only runs on Unix."""
    try:
        import resource
        mem = 512 * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (mem, mem))
        resource.setrlimit(resource.RLIMIT_FSIZE, (2 * 1024 * 1024, 2 * 1024 * 1024))
    except Exception:
        pass


_PREEXEC = _set_resource_limits if sys.platform != "win32" else None

_BLOCKED_MODULES = frozenset({
    "os", "subprocess", "socket", "requests", "urllib", "http",
    "ftplib", "smtplib", "telnetlib", "shutil", "pathlib", "glob",
    "tempfile", "fnmatch", "importlib", "ctypes", "multiprocessing",
    "threading", "concurrent", "asyncio", "signal", "resource", "mmap",
    "pty", "tty", "termios", "readline", "code", "codeop",
    "pdb", "cProfile", "profile", "pickle", "pickletools", "shelve",
    "sqlite3", "dbm", "_thread", "zipfile", "tarfile", "gzip",
    "ssl", "hashlib", "hmac", "secrets",
})

_SANDBOX_PRELUDE = """
import builtins as _builtins
import os as _os

_BLOCKED = {blocked_set!r}
_real_import = _builtins.__import__

def _safe_import(name, *args, **kwargs):
    top = name.split('.')[0]
    if top in _BLOCKED:
        raise ImportError(f"Module '{{name}}' is not available in the sandbox")
    return _real_import(name, *args, **kwargs)

_builtins.__import__ = _safe_import

_real_open = _builtins.open
_sandbox_dir = _os.path.realpath({sandbox_dir!r})

def _safe_open(file, mode='r', *args, **kwargs):
    try:
        if not _os.path.realpath(str(file)).startswith(_sandbox_dir):
            raise PermissionError("File access outside the sandbox is not allowed")
    except PermissionError:
        raise
    except Exception:
        raise PermissionError("File access is restricted in the sandbox")
    return _real_open(file, mode, *args, **kwargs)

_builtins.open = _safe_open
"""

# Raw strings so JS braces don't need escaping. __ENTRY_MODULE__ / __ENTRY_FUNCTION__
# are replaced at runtime via str.replace().
_DEEP_EQUAL_JS = r"""
function deepEqual(a, b) {
  if (a === b) return true;
  if (a === null || b === null || typeof a !== typeof b) return false;
  if (Array.isArray(a) !== Array.isArray(b)) return false;
  if (Array.isArray(a)) {
    if (a.length !== b.length) return false;
    return a.every((v, i) => deepEqual(v, b[i]));
  }
  if (typeof a === 'object') {
    const ka = Object.keys(a).sort(), kb = Object.keys(b).sort();
    return ka.length === kb.length &&
      ka.every((k, i) => k === kb[i] && deepEqual(a[k], b[k]));
  }
  return false;
}

function formatError(e) {
  if (!e.stack) return e.message;
  return e.stack.split('\n')
    .filter((l, i) => i === 0 || (l.trim().startsWith('at ') && !l.includes('node:') && !l.includes('_test_runner') && !l.includes('node_modules')))
    .join('\n')
    .trim();
}
"""

_JS_RUNNER_TEMPLATE = r"""'use strict';
const fs = require('fs');

const testCases = JSON.parse(fs.readFileSync('_test_cases.json', 'utf8'));

__DEEP_EQUAL__

let entryFn;
try {
  const mod = require('./__ENTRY_MODULE__');
  entryFn = typeof mod['__ENTRY_FUNCTION__'] === 'function'
    ? mod['__ENTRY_FUNCTION__']
    : mod.default;
  if (typeof entryFn !== 'function') {
    throw new Error('"__ENTRY_FUNCTION__" is not exported as a function');
  }
} catch (e) {
  process.stdout.write(JSON.stringify(testCases.map(tc => ({
    passed: false, got: null, expected: tc.expected, input: tc.args,
    error: 'Import error: ' + formatError(e)
  }))) + '\n');
  process.exit(0);
}

const results = testCases.map(tc => {
  try {
    const args = JSON.parse(JSON.stringify(tc.args));
    const got = entryFn(...args);
    return { passed: deepEqual(got, tc.expected), got, expected: tc.expected, input: tc.args, error: null };
  } catch (e) {
    return { passed: false, got: null, expected: tc.expected, input: tc.args, error: formatError(e) };
  }
});

process.stdout.write(JSON.stringify(results) + '\n');
"""

_TS_RUNNER_TEMPLATE = r"""const fs = require('fs');

const testCases: any[] = JSON.parse(fs.readFileSync('_test_cases.json', 'utf8'));

__DEEP_EQUAL__

let entryFn: Function;
try {
  const mod = require('./__ENTRY_MODULE__');
  entryFn = typeof mod['__ENTRY_FUNCTION__'] === 'function'
    ? mod['__ENTRY_FUNCTION__']
    : mod.default;
  if (typeof entryFn !== 'function') {
    throw new Error('"__ENTRY_FUNCTION__" is not exported as a function');
  }
} catch (e: any) {
  process.stdout.write(JSON.stringify(testCases.map((tc: any) => ({
    passed: false, got: null, expected: tc.expected, input: tc.args,
    error: 'Import error: ' + formatError(e)
  }))) + '\n');
  process.exit(0);
}

const results = testCases.map((tc: any) => {
  try {
    const args: any[] = JSON.parse(JSON.stringify(tc.args));
    const got = (entryFn as Function)(...args);
    return { passed: deepEqual(got, tc.expected), got, expected: tc.expected, input: tc.args, error: null };
  } catch (e: any) {
    return { passed: false, got: null, expected: tc.expected, input: tc.args, error: formatError(e) };
  }
});

process.stdout.write(JSON.stringify(results) + '\n');
"""

_TS_CONFIG = """{
  "compilerOptions": {
    "module": "commonjs",
    "target": "es2020",
    "esModuleInterop": true,
    "strict": false,
    "skipLibCheck": true
  }
}"""

_NODE_MEMORY_MB = os.getenv("BUG_BASH_NODE_MEMORY_MB", "128")


def _node_env() -> dict:
    env = os.environ.copy()
    node_opts = env.get("NODE_OPTIONS", "").strip()
    memory_opt = f"--max-old-space-size={_NODE_MEMORY_MB}"
    env["NODE_OPTIONS"] = f"{node_opts} {memory_opt}".strip() if node_opts else memory_opt
    return env


def _resolve_node_command(language: str) -> tuple[list[str] | None, str | None]:
    node_bin = shutil.which("node")
    if not node_bin:
        return None, "JavaScript/TypeScript runner is unavailable: Node.js is not installed on the backend."

    if language == "javascript":
        return [node_bin], None

    ts_node_bin = shutil.which("ts-node")
    if ts_node_bin:
        return [ts_node_bin, "--transpile-only", "--skip-project"], None

    return None, (
        "TypeScript runner is unavailable: `ts-node` is not installed on the backend. "
        "Install `typescript` and `ts-node` in the Railway service."
    )


def _run_node_challenge(challenge: dict, user_code: dict, language: str) -> dict:
    challenge_dir = challenge["_dir"]
    entry_module = challenge["entry_module"]
    entry_function = challenge["entry_function"]
    is_ts = language == "typescript"
    base_cmd, runtime_error = _resolve_node_command(language)
    if runtime_error:
        return {"passed": False, "error": runtime_error, "results": []}

    with tempfile.TemporaryDirectory() as tmpdir:
        for file_info in challenge["files"]:
            fname = file_info["name"]
            dst = os.path.join(tmpdir, fname)
            if fname in user_code:
                with open(dst, "w", encoding="utf-8") as f:
                    f.write(user_code[fname])
            else:
                src = os.path.join(challenge_dir, fname)
                if os.path.exists(src):
                    shutil.copy(src, dst)

        test_cases_path = os.path.join(tmpdir, "_test_cases.json")
        with open(test_cases_path, "w", encoding="utf-8") as f:
            json.dump(challenge["test_cases"], f)

        if is_ts:
            with open(os.path.join(tmpdir, "tsconfig.json"), "w", encoding="utf-8") as f:
                f.write(_TS_CONFIG)
            runner_filename = "_test_runner.ts"
            template = _TS_RUNNER_TEMPLATE
        else:
            runner_filename = "_test_runner.js"
            template = _JS_RUNNER_TEMPLATE

        runner_content = (
            template
            .replace("__DEEP_EQUAL__", _DEEP_EQUAL_JS)
            .replace("__ENTRY_MODULE__", entry_module)
            .replace("__ENTRY_FUNCTION__", entry_function)
        )
        with open(os.path.join(tmpdir, runner_filename), "w", encoding="utf-8") as f:
            f.write(runner_content)

        cmd = [*base_cmd, runner_filename]

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
                cwd=tmpdir,
                preexec_fn=_PREEXEC,
                env=_node_env(),
            )

            if not proc.stdout.strip():
                return {
                    "passed": False,
                    "error": proc.stderr.strip() or "No output from runner",
                    "results": [],
                }

            results = json.loads(proc.stdout.strip())
            return {
                "passed": all(r["passed"] for r in results),
                "error": None,
                "results": results,
            }

        except subprocess.TimeoutExpired:
            return {"passed": False, "error": "Time limit exceeded (10s)", "results": []}
        except Exception as e:
            return {"passed": False, "error": str(e), "results": []}


def _run_compiled_challenge(challenge: dict, user_code: dict, language: str) -> dict:
    challenge_dir = challenge["_dir"]

    if language == "cpp":
        main_file = challenge.get("main_file", "main.cpp")
        compiler = shutil.which("g++") or "g++"
        compile_args = lambda out, src: [compiler, "-o", out, src, "-std=c++17"]
    else:  # rust
        main_file = challenge.get("main_file", "main.rs")
        compiler = shutil.which("rustc") or "rustc"
        compile_args = lambda out, src: [compiler, "-o", out, src]

    with tempfile.TemporaryDirectory() as tmpdir:
        for file_info in challenge["files"]:
            fname = file_info["name"]
            dst = os.path.join(tmpdir, fname)
            if fname in user_code:
                with open(dst, "w", encoding="utf-8") as f:
                    f.write(user_code[fname])
            else:
                src = os.path.join(challenge_dir, fname)
                if os.path.exists(src):
                    shutil.copy(src, dst)

        binary_path = os.path.join(tmpdir, "runner_bin")
        main_path = os.path.join(tmpdir, main_file)

        try:
            compile_proc = subprocess.run(
                compile_args(binary_path, main_path),
                capture_output=True,
                text=True,
                timeout=30,
                cwd=tmpdir,
            )

            if compile_proc.returncode != 0:
                err = compile_proc.stderr.strip() or compile_proc.stdout.strip()
                return {"passed": False, "error": err, "results": []}

            run_proc = subprocess.run(
                [binary_path],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=tmpdir,
                preexec_fn=_PREEXEC,
            )

            if not run_proc.stdout.strip():
                return {
                    "passed": False,
                    "error": run_proc.stderr.strip() or "No output from runner",
                    "results": [],
                }

            results = json.loads(run_proc.stdout.strip())
            return {
                "passed": all(r["passed"] for r in results),
                "error": None,
                "results": results,
            }

        except subprocess.TimeoutExpired:
            return {"passed": False, "error": "Time limit exceeded (10s)", "results": []}
        except Exception as e:
            return {"passed": False, "error": str(e), "results": []}


def _run_python_challenge(challenge: dict, user_code: dict) -> dict:
    challenge_dir = challenge["_dir"]

    with tempfile.TemporaryDirectory() as tmpdir:
        for file_info in challenge["files"]:
            fname = file_info["name"]
            dst = os.path.join(tmpdir, fname)
            if fname in user_code:
                with open(dst, "w", encoding="utf-8") as f:
                    f.write(user_code[fname])
            else:
                src = os.path.join(challenge_dir, fname)
                if os.path.exists(src):
                    shutil.copy(src, dst)

        entry_module = challenge["entry_module"]
        entry_function = challenge["entry_function"]

        test_cases_path = os.path.join(tmpdir, "_test_cases.json")
        with open(test_cases_path, "w", encoding="utf-8") as f:
            json.dump(challenge["test_cases"], f)

        allowed = set(challenge.get("allowed_modules", []))
        active_blocklist = _BLOCKED_MODULES - allowed

        sandbox_prelude = _SANDBOX_PRELUDE.format(
            blocked_set=active_blocklist,
            sandbox_dir=os.path.realpath(tmpdir),
        )

        runner_script = f"""
import sys, json, copy, traceback as _traceback
_TMPDIR = {repr(tmpdir)}
null = None; true = True; false = False
sys.path.insert(0, {json.dumps(tmpdir)})

{sandbox_prelude}

with _real_open({repr(test_cases_path)}, encoding="utf-8") as _f:
    _test_cases = json.load(_f)

try:
    from {entry_module} import {entry_function}
except Exception as import_err:
    results = [
        {{
            "passed": False,
            "got": None,
            "expected": tc["expected"],
            "input": tc["args"],
            "error": f"Import error: {{import_err}}"
        }}
        for tc in _test_cases
    ]
    print(json.dumps(results))
    sys.exit(0)

test_cases = _test_cases
results = []
for tc in test_cases:
    try:
        args = copy.deepcopy(tc["args"])
        result = {entry_function}(*args)
        results.append({{
            "passed": result == tc["expected"],
            "got": result,
            "expected": tc["expected"],
            "input": tc["args"],
            "error": None
        }})
    except Exception as e:
        _tb = _traceback.format_exc().replace(_TMPDIR, '<your code>').replace(_TMPDIR.replace('\\\\', '/'), '<your code>')
        results.append({{
            "passed": False,
            "got": None,
            "expected": tc["expected"],
            "input": tc["args"],
            "error": _tb.strip()
        }})

print(json.dumps(results))
"""

        try:
            proc = subprocess.run(
                [sys.executable, "-c", runner_script],
                capture_output=True,
                text=True,
                timeout=10,
                preexec_fn=_PREEXEC,
            )

            if not proc.stdout.strip():
                return {
                    "passed": False,
                    "error": proc.stderr.strip() or "No output from runner",
                    "results": [],
                }

            results = json.loads(proc.stdout.strip())
            return {
                "passed": all(r["passed"] for r in results),
                "error": None,
                "results": results,
            }

        except subprocess.TimeoutExpired:
            return {"passed": False, "error": "Time limit exceeded (10s)", "results": []}
        except Exception as e:
            return {"passed": False, "error": str(e), "results": []}


def run_challenge(challenge: dict, user_code: dict) -> dict:
    language = challenge.get("language", "python")
    if language in ("javascript", "typescript"):
        return _run_node_challenge(challenge, user_code, language)
    if language in ("cpp", "rust"):
        return _run_compiled_challenge(challenge, user_code, language)
    return _run_python_challenge(challenge, user_code)
