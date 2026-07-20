#!/usr/bin/env bash
# check-p6-evidence.sh — P6 证据格式检查（P1.7）
# 检查 P6-evidence/ 目录非空 + UI 截图实质检查（R1a）
# 查询类 BDD 可不截图，但须有断言记录证据（response.json / assert.log 等）
# exit 0 = 通过; exit 1 = 证据缺失; exit 2 = 无 P6 文件

set -euo pipefail

TASK_DIR="${1:?用法: check-p6-evidence.sh TASK_DIR}"
P6_FILE="$TASK_DIR/P6-acceptance.md"

[ ! -f "$P6_FILE" ] && exit 2

# 用现有协议约定的格式计数（- PASS / - FAIL 行）
BDD_COUNT=$(grep -cE '^\s*- (PASS|FAIL)' "$P6_FILE" || echo 0)
BDD_COUNT=$(echo "$BDD_COUNT" | tail -1)

if [ "$BDD_COUNT" -eq 0 ]; then
    echo "GATE P6-EVIDENCE: P6-acceptance.md 无 BDD 条目（- PASS/- FAIL 格式）" >&2
    exit 1
fi

# 检查 P6-evidence/ 目录非空
# 所有 PASS 都必须有文件引用（hook 强制）
# 文件形式不限：截图、日志、JSON、文本都行——不绑定技术栈
# 查询类 BDD 可不截图，但须有断言记录文件（response.json / assert.log 等）
EVIDENCE_DIR="$TASK_DIR/P6-evidence"

# 检查每条 PASS 行是否含文件引用（括号内路径）
PASS_WITHOUT_REF=0
while IFS= read -r line; do
    if ! echo "$line" | grep -qE '\([a-zA-Z0-9_/.-]+\.(png|jpg|log|json|html|txt|yaml|yml)[^)]*\)'; then
        PASS_WITHOUT_REF=$((PASS_WITHOUT_REF + 1))
    fi
done < <(grep -E '^\s*- PASS\b' "$P6_FILE" 2>/dev/null || true)

if [ "$PASS_WITHOUT_REF" -gt 0 ]; then
    echo "GATE P6-EVIDENCE: 有 ${PASS_WITHOUT_REF} 条 PASS 缺文件证据引用（每条 PASS 必须引用证据文件，形式不限：截图/日志/JSON/文本）" >&2
    exit 1
fi

if [ ! -d "$EVIDENCE_DIR" ] || [ -z "$(ls -A "$EVIDENCE_DIR" 2>/dev/null)" ]; then
    echo "GATE P6-EVIDENCE: P6-evidence/ 目录不存在或为空" >&2
    exit 1
fi

echo "GATE P6-EVIDENCE: ${BDD_COUNT} 条 BDD，证据目录非空" >&2

# UI 截图实质检查（R1a：T045 评审 v5）
# 仅当 P6-acceptance.md 含截图引用时才检查（兼容查询类 BDD 可不截图规则）
P2_FILE="$TASK_DIR/P2-design.md"
UI_AFFECTED=""
if [ -f "$P2_FILE" ]; then
    UI_AFFECTED=$(P2_FILE="$P2_FILE" python3 -c "
import re, os
with open(os.environ['P2_FILE']) as f:
    text = f.read()
m = re.search(r'ui_affected:\s*(true|false)', text)
print(m.group(1) if m else '')
" 2>/dev/null || echo "")
fi

if [ "$UI_AFFECTED" = "true" ]; then
    HAS_SCREENSHOT_REF=$(grep -cE '\(screenshots/' "$P6_FILE" 2>/dev/null || echo 0)
    HAS_SCREENSHOT_REF=$(echo "$HAS_SCREENSHOT_REF" | tail -1)

    if [ "$HAS_SCREENSHOT_REF" -gt 0 ]; then
        SCREENSHOTS_DIR="$EVIDENCE_DIR/screenshots"
        if [ ! -d "$SCREENSHOTS_DIR" ] || [ -z "$(find "$SCREENSHOTS_DIR" -type f -not -name '.*' 2>/dev/null)" ]; then
            echo "GATE P6-EVIDENCE: ui_affected=true 且 PASS 引用了截图，但 P6-evidence/screenshots/ 目录不存在或为空" >&2
            exit 1
        fi
        EMPTY_COUNT=0
        PNG_WARNING=0
        while IFS= read -r -d '' img; do
            SIZE=$(stat -c%s "$img" 2>/dev/null || stat -f%z "$img" 2>/dev/null || echo 0)
            if [ "$SIZE" -le 1024 ]; then
                # PNG header check: 前 8 字节 = \x89PNG\r\n\x1a\n
                HEADER=$(head -c 8 "$img" 2>/dev/null | od -A n -t x1 | tr -d ' ')
                EXPECTED='89504e470d0a1a0a'
                if [ "$HEADER" = "$EXPECTED" ]; then
                    PNG_WARNING=$((PNG_WARNING + 1))
                else
                    EMPTY_COUNT=$((EMPTY_COUNT + 1))
                fi
            fi
        done < <(find "$SCREENSHOTS_DIR" -type f -not -name '.*' -print0 2>/dev/null)
        if [ "$EMPTY_COUNT" -gt 0 ]; then
            echo "GATE P6-EVIDENCE: P6-evidence/screenshots/ 有 ${EMPTY_COUNT} 个非 PNG 文件 ≤ 1KB（疑似充数）" >&2
            exit 1
        fi
        if [ "$PNG_WARNING" -gt 0 ]; then
            echo "GATE P6-EVIDENCE WARNING: P6-evidence/screenshots/ 有 ${PNG_WARNING} 个合法 PNG ≤ 1KB（元素级小截图，不阻断但请确认非充数）" >&2
            exit 2
        fi
        MD5_LIST=$(find "$SCREENSHOTS_DIR" -type f -not -name '.*' -exec md5sum {} \; 2>/dev/null | cut -d' ' -f1 | sort)
        MD5_TOTAL=$(echo "$MD5_LIST" | wc -l)
        MD5_UNIQUE=$(echo "$MD5_LIST" | sort -u | wc -l)
        if [ "$MD5_TOTAL" -gt "$MD5_UNIQUE" ]; then
            MD5_DUPES=$((MD5_TOTAL - MD5_UNIQUE))
            echo "GATE P6-EVIDENCE WARNING: P6-evidence/screenshots/ 有 ${MD5_DUPES} 个 md5 重复截图（行为差异类 BDD 截图可能视觉相同，不阻断但请在 acceptance report 说明原因）" >&2
            exit 2
        fi
    fi
fi

exit 0
