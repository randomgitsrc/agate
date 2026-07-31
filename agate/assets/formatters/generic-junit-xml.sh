#!/usr/bin/env bash
set -euo pipefail

EXIT_CODE="${1:-1}"
OUTPUT="$(cat)"
export EXIT_CODE OUTPUT

python3 <<'PYEOF'
import sys, json, re, os

exit_code = int(os.environ.get("EXIT_CODE", "1"))
output = os.environ.get("OUTPUT", "")

def extract_attr(pattern):
    m = re.search(pattern, output)
    return int(m.group(1)) if m else 0

total = extract_attr(r'tests="(\d+)"')
failures = extract_attr(r'failures="(\d+)"')
errors = extract_attr(r'errors="(\d+)"')
passed = total - failures - errors

failed_tests = []
for m in re.finditer(r"<testcase[^>]*>.*?<(?:failure|error)", output, re.DOTALL):
    name_match = re.search(r'name="([^"]*)"', m.group(0))
    cls_match = re.search(r'classname="([^"]*)"', m.group(0))
    name = name_match.group(1) if name_match else ""
    cls = cls_match.group(1) if cls_match else ""
    failed_tests.append(cls + "::" + name if cls else name)

result = {
    "exit_code": exit_code,
    "total": total,
    "passed": passed,
    "failed": failures,
    "errors": errors,
    "failed_tests": failed_tests,
    "import_errors": [],
    "syntax_errors": []
}

print(json.dumps(result, separators=(",", ":")))
PYEOF
