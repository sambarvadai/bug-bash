# Issue: NameError for JSON values in runner subprocess

## Affected questions
- easy_02: Find the Maximum (NameError: name 'null' is not defined)
- easy_04: Leap Year (NameError: name 'true' is not defined)

## Root cause
`backend/runner.py` builds a Python script as a string and runs it via `subprocess -c`. The test cases are loaded from `challenge.json` by Python's `json.load()` (which correctly converts `null` → `None`, `true` → `True`, `false` → `False`), but then `json.dumps()` converts them back to JSON format. When that JSON string gets embedded directly into the Python script, `null`/`true`/`false` appear as bare Python identifiers, causing a NameError.

## What was tried
1. Wrapping embedded JSON with `json.loads(...)` — fix is correct but server not picking it up
2. Switching to `repr()` instead of `json.dumps()` — same result
3. Writing test cases to a temp file and reading from subprocess — server still not reloading

## Current state of backend/runner.py
The file has the file-based fix (test cases written to `_test_cases.json` in tmpdir, read by subprocess via `_real_open`). The fix is confirmed correct when `run_challenge` is called directly. The server appears to not be picking up the changes — likely a process/reload issue to investigate tomorrow.

## Next steps
- Confirm the fix works by running `run_challenge` directly (see test command below)
- Investigate why the running server doesn't reflect file changes (stale process, __pycache__, etc.)

## Test command
```
cd F:\bug-bash\backend
python -c "
import json, sys, os
sys.path.insert(0, '.')
import runner

with open('../challenges/easy/04_leap_year/challenge.json') as f:
    ch = json.load(f)
ch['_dir'] = os.path.abspath('../challenges/easy/04_leap_year')
for fi in ch['files']:
    with open('../challenges/easy/04_leap_year/' + fi['name']) as f:
        fi['initial_code'] = f.read()

result = runner.run_challenge(ch, {})
print(result.get('error') or 'No error - fix is working')
"
```
