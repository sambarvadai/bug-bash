import subprocess
import sys
import json
import os
import tempfile
import shutil


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

        test_cases_path = os.path.join(tmpdir, "_test_cases.json")
        with open(test_cases_path, "w", encoding="utf-8") as f:
            json.dump(challenge["test_cases"], f)

        runner_script = f"""
import sys, json, copy
null = None; true = True; false = False
sys.path.insert(0, {json.dumps(tmpdir)})

with open({repr(test_cases_path)}, encoding="utf-8") as _f:
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
