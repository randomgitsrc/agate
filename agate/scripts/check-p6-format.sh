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

if [ "$MODE" = "check" ]; then
    # T001 v2.0 流 B（BDD-17/18，P2-design.md §3.2.1）：行格式从严校验。
    # 升级前：本脚本只做"归一化 sed"，--check 靠 diff 前后内容判定。
    # 升级后：--check 独立做"行格式校验"——候选行（疑似 PASS/FAIL 逐条声明，大小写
    # 不敏感、含全角/半角冒号变体，用词边界 \b 排除 "failure" 等非目标词）必须严格
    # 匹配行首 `- PASS|FAIL BDD-N`（大写、紧跟一个空格、带 BDD 编号）；总结行（如
    # `- PASS: 16` 无 BDD 编号）、小写（`- pass`）、全角（`- FAIL：`）一律视为格式
    # 偏差，报错要求用 --fix 归一化（--fix 模式的归一化 sed 逻辑原样保留，见下方）。
    INVALID=0
    while IFS= read -r line || [ -n "$line" ]; do
        if echo "$line" | grep -qiE '^[[:space:]]*-[[:space:]]+(pass|fail)\b'; then
            if ! echo "$line" | grep -qE '^[[:space:]]*-[[:space:]]+(PASS|FAIL)[[:space:]]+BDD-[0-9]+'; then
                INVALID=$((INVALID + 1))
            fi
        fi
    done < "$FILE"
    if [ "$INVALID" -gt 0 ]; then
        echo "P6 format deviations found (use --fix to auto-fix): ${INVALID} 行不符合 '- PASS|FAIL BDD-N:' 逐条格式（总结行/小写/全角均须归一化）" >&2
        exit 1
    fi
    exit 0
fi

CONTENT=$(cat "$FILE")
FIXED="$CONTENT"
CHANGES=0

FIXED=$(printf '%s' "$FIXED" | sed -E 's/^([[:space:]]*)-\s+(pass)([[:space:]:：]|$)/\1- PASS\3/' | sed -E 's/^([[:space:]]*)-\s+(fail)([[:space:]:：]|$)/\1- FAIL\3/' | sed -E 's/^([[:space:]]*)(pass)([[:space:]:：]|$)/\1- PASS\3/' | sed -E 's/^([[:space:]]*)(fail)([[:space:]:：]|$)/\1- FAIL\3/')
if [ "$FIXED" != "$CONTENT" ]; then
    CHANGES=1
fi
CONTENT="$FIXED"

FIXED=$(printf '%s' "$FIXED" | sed -E 's/^[[:space:]]+(- (PASS|FAIL) )/\1/')
if [ "$FIXED" != "$CONTENT" ]; then
    CHANGES=1
fi
CONTENT="$FIXED"

# 总结行修正：行首 - PASS/- FAIL 后纯数字结尾（非 BDD 条目）→ 改为 Summary 格式
FIXED=$(printf '%s' "$FIXED" | sed -E 's/^-\s+(PASS|FAIL)\s*[:：]\s*([0-9]+)\s*$/\*\*Summary\*\*: \1: \2/')
if [ "$FIXED" != "$CONTENT" ]; then
    CHANGES=1
fi
CONTENT="$FIXED"

# 到这里 MODE 必为 "fix"（"check" 已在上方独立分支处理并 exit）。
if [ "$CHANGES" -eq 1 ]; then
    printf '%s' "$FIXED" > "$FILE"
fi
exit 0
