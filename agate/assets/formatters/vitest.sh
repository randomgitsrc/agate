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

failed = extract_count(r"Tests\s+(\d+)\s+failed")
passed = extract_count(r"Tests\s+(\d+)\s+passed")
errors = extract_count(r"Failed Suites\s+(\d+)")
total = passed + failed + errors

failed_tests = re.findall(r"^FAIL\s+(\S+)", output, re.MULTILINE)

import_errors = []
for m in re.finditer(r"Cannot find (?:module|package) ['\"]([^'\"]+)", output):
    import_errors.append({"module": m.group(1), "message": m.group(0)})

syntax_errors = []
for m in re.finditer(r".*(?:SyntaxError|ParseError|Unexpected token).*", output):
    line = m.group(0).strip()
    file_match = re.search(r"(\S+\.(?:js|ts|jsx|tsx|mjs|cjs))", line)
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
