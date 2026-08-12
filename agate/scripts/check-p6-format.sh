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

# frontmatter/正文切分（P6 回退修复：--fix 的归一化 sed 此前对整文件生效，会误伤
# frontmatter 里合法的 pass:/fail: 字段，见 P6-gate-diagnosis.md）。
# 边界判定语义与 agate-frontmatter-check.py::_extract_frontmatter_block 对齐：
# 文件须以恰好一行 "---" 开头，其后第一条以 "---" 起始的行视为闭合边界；
# 找不到闭合边界 → 视为无 frontmatter 块（BDD-9 旧格式兼容，全文本按正文处理，行为不变）。
FM_PART=""
BODY_PART="$CONTENT"
FIRST_LINE=$(printf '%s\n' "$CONTENT" | head -n 1)
if [ "$FIRST_LINE" = "---" ]; then
    CLOSE_LINE=$(printf '%s\n' "$CONTENT" | awk 'NR>1 && index($0,"---")==1 {print NR; exit}')
    if [ -n "$CLOSE_LINE" ]; then
        FM_PART=$(printf '%s\n' "$CONTENT" | sed -n "1,${CLOSE_LINE}p")
        BODY_PART=$(printf '%s\n' "$CONTENT" | sed -n "$((CLOSE_LINE + 1)),\$p")
    fi
fi

FIXED="$BODY_PART"
CHANGES=0

FIXED=$(printf '%s' "$FIXED" | sed -E 's/^([[:space:]]*)-\s+(pass)([[:space:]:：]|$)/\1- PASS\3/' | sed -E 's/^([[:space:]]*)-\s+(fail)([[:space:]:：]|$)/\1- FAIL\3/' | sed -E 's/^([[:space:]]*)(pass)([[:space:]:：]|$)/\1- PASS\3/' | sed -E 's/^([[:space:]]*)(fail)([[:space:]:：]|$)/\1- FAIL\3/')
if [ "$FIXED" != "$BODY_PART" ]; then
    CHANGES=1
fi
BODY_PART="$FIXED"

FIXED=$(printf '%s' "$FIXED" | sed -E 's/^[[:space:]]+(- (PASS|FAIL) )/\1/')
if [ "$FIXED" != "$BODY_PART" ]; then
    CHANGES=1
fi
BODY_PART="$FIXED"

# 总结行修正：行首 - PASS/- FAIL 后纯数字结尾（非 BDD 条目）→ 改为 Summary 格式
# v0.40.3：[:：] bracket expression 在 POSIX/单字节 locale 下无法匹配全角 UTF-8 冒号，
# 导致 --fix 静默失效（exit 0 但文件不变）。改用 alternation (:|：) 规避 POSIX class 歧义。
FIXED=$(printf '%s' "$FIXED" | sed -E 's/^-\s+(PASS|FAIL)\s*(:|：)\s*([0-9]+)\s*$/\*\*Summary\*\*: \1: \3/')
if [ "$FIXED" != "$BODY_PART" ]; then
    CHANGES=1
fi
BODY_PART="$FIXED"

if [ -n "$FM_PART" ]; then
    if [ -n "$BODY_PART" ]; then
        FULL_FIXED="$FM_PART"$'\n'"$BODY_PART"
    else
        FULL_FIXED="$FM_PART"
    fi
else
    FULL_FIXED="$BODY_PART"
fi

# 到这里 MODE 必为 "fix"（"check" 已在上方独立分支处理并 exit）。
if [ "$CHANGES" -eq 1 ]; then
    printf '%s' "$FULL_FIXED" > "$FILE"
fi
exit 0
