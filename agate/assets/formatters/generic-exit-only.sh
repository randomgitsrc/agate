#!/usr/bin/env bash
set -euo pipefail

EXIT_CODE="${1:-1}"
OUTPUT="$(cat)"
export EXIT_CODE OUTPUT

python3 <<'PYEOF'
import sys, json, os

exit_code = int(os.environ.get("EXIT_CODE", "1"))

result = {
    "exit_code": exit_code,
    "total": 0,
    "passed": 0,
    "failed": 0,
    "errors": 0,
    "failed_tests": [],
    "import_errors": [],
    "syntax_errors": []
}

print(json.dumps(result, separators=(",", ":")))
PYEOF
