#!/usr/bin/env bash
set -euo pipefail

EXIT_CODE="${1:-1}"
OUTPUT="$(cat)"
export EXIT_CODE OUTPUT

python3 <<'PYEOF'
import sys, json, re, os

exit_code = int(os.environ.get("EXIT_CODE", "1"))
output = os.environ.get("OUTPUT", "")

def extract_count(pattern):
    m = re.search(pattern, output)
    return int(m.group(1)) if m else 0

passed = extract_count(r"(\d+) passed")
failed = extract_count(r"(\d+) failed")
errors = extract_count(r"(\d+) error")
total = passed + failed + errors

failed_tests = re.findall(r"^FAILED (\S+)", output, re.MULTILINE)
failed_tests += [m.group(1) for m in re.finditer(r"^(\S+) FAILED", output, re.MULTILINE)]

import_errors = []
for m in re.finditer(r".*(?:ImportError|ModuleNotFoundError).*", output):
    line = m.group(0).strip()
    mod_match = re.search(r"cannot import name \S+ from ['\"](\S+?)['\"]", line)
    if not mod_match:
        mod_match = re.search(r"No module named ['\"](\S+?)['\"]", line)
    if not mod_match:
        mod_match = re.search(r"from ['\"](\S+?)['\"]", line)
    module = mod_match.group(1) if mod_match else ""
    import_errors.append({"module": module, "message": line})

syntax_errors = []
for m in re.finditer(r".*(?:SyntaxError|IndentationError).*", output):
    line = m.group(0).strip()
    file_match = re.search(r'File "([^"]+)"', line)
    if not file_match:
        file_match = re.search(r"(\S+\.py)", line)
    file = file_match.group(1) if file_match else ""
    syntax_errors.append({"file": file, "message": line})

result = {
    "exit_code": exit_code,
    "total": total,
    "passed": passed,
    "failed": failed,
    "errors": errors,
    "failed_tests": failed_tests,
    "import_errors": import_errors,
    "syntax_errors": syntax_errors
}

print(json.dumps(result, separators=(",", ":")))
PYEOF
