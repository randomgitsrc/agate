#!/usr/bin/env bash
set -euo pipefail

EXIT_CODE="${1:-1}"
OUTPUT="$(cat)"
export EXIT_CODE OUTPUT

python3 <<'PYEOF'
import sys, json, re, os

exit_code = int(os.environ.get("EXIT_CODE", "1"))
output = os.environ.get("OUTPUT", "")

passed = len(re.findall(r"^ok\b", output, re.MULTILINE))
failed = len(re.findall(r"^not ok\b", output, re.MULTILINE))
total = passed + failed

failed_tests = []
for m in re.finditer(r"^not ok\s+\d+\s*-?\s*(.+)", output, re.MULTILINE):
    failed_tests.append(m.group(1).strip())

result = {
    "exit_code": exit_code,
    "total": total,
    "passed": passed,
    "failed": failed,
    "errors": 0,
    "failed_tests": failed_tests,
    "import_errors": [],
    "syntax_errors": []
}

print(json.dumps(result, separators=(",", ":")))
PYEOF
