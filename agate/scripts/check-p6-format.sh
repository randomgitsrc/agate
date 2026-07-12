#!/usr/bin/env bash
set -euo pipefail

MODE="check"
FILE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --fix) MODE="fix" ;;
        --check) MODE="check" ;;
        *) FILE="$1" ;;
    esac
    shift
done

if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
    exit 0
fi

basename_check="$(basename "$FILE")"
if [[ "$basename_check" != P6-acceptance.md ]]; then
    exit 0
fi

CONTENT=$(cat "$FILE")
FIXED="$CONTENT"
CHANGES=0

FIXED=$(printf '%s' "$FIXED" | sed -E 's/^([[:space:]]*)-\s+(pass)([[:space:]]+)/\1- PASS\3/' | sed -E 's/^([[:space:]]*)-\s+(fail)([[:space:]]+)/\1- FAIL\3/' | sed -E 's/^([[:space:]]*)(pass)([[:space:]]+)/\1- PASS\3/' | sed -E 's/^([[:space:]]*)(fail)([[:space:]]+)/\1- FAIL\3/')
if [ "$FIXED" != "$CONTENT" ]; then
    CHANGES=1
fi
CONTENT="$FIXED"

FIXED=$(printf '%s' "$FIXED" | sed -E 's/^[[:space:]]+(- (PASS|FAIL) )/\1/')
if [ "$FIXED" != "$CONTENT" ]; then
    CHANGES=1
fi
CONTENT="$FIXED"

if [ "$MODE" = "fix" ]; then
    if [ "$CHANGES" -eq 1 ]; then
        printf '%s' "$FIXED" > "$FILE"
    fi
    exit 0
fi

if [ "$CHANGES" -eq 1 ]; then
    echo "P6 format deviations found (use --fix to auto-fix):" >&2
    diff <(printf '%s' "$(cat "$FILE")") <(printf '%s' "$FIXED") >&2 || true
    exit 1
fi

exit 0
