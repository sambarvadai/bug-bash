import subprocess
import sys
import json
import os
import tempfile
import shutil


def _set_resource_limits():
    """Cap memory and file writes at the OS level. Only runs on Unix (Railway)."""
    try:
        import resource
        # 512 MB virtual address space — enough for Python + challenge code
        mem = 512 * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (mem, mem))
        # 2 MB max file writes (covers any tmpdir writes user code might do)
        resource.setrlimit(resource.RLIMIT_FSIZE, (2 * 1024 * 1024, 2 * 1024 * 1024))
    except Exception:
        pass  # Silently skip if unsupported (e.g. macOS AS limit quirks)


# Only set preexec on Unix; Windows doesn't support preexec_fn
_PREEXEC = _set_resource_limits if sys.platform != "win32" else None

# Modules blocked inside the sandbox subprocess
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

# Injected at the top of every runner subprocess, before user code is imported.
# Uses double-braces to escape the f-string where needed.
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


def run_challenge(challenge: dict, user_code: dict) -> dict:
    """
    Execute user-edited code against a challenge's test cases in a subprocess.

    Args:
        challenge: challenge dict loaded from challenge.json (with _dir key)
        user_code: {filename: code_string} for each file in the challenge

    Returns:
        {
            "passed": bool,
            "error": str | None,
            "results": [{"input", "expected", "got", "passed", "error"}, ...]
        }
    """
    challenge_dir = challenge["_dir"]

    with tempfile.TemporaryDirectory() as tmpdir:
        # Write user-edited files; fall back to original for non-editable files
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

        # Write test cases to a file so they don't need to be embedded in the script
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
import sys, json, copy
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
        results.append({{
            "passed": False,
            "got": None,
            "expected": tc["expected"],
            "input": tc["args"],
            "error": str(e)
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
