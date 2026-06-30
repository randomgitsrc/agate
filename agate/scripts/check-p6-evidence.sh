#!/usr/bin/env bash
# check-p6-evidence.sh — P6 证据格式检查（P1.7）
# 检查 P6-evidence/ 目录非空（现有协议已支持）
# 注意：完整的"每条 BDD 有 Evidence 引用"检查需要协议定义
# ## BDD-NN 标题和 Evidence: 字段格式，这属于 Phase 2B 协议改动。
# 当前退化为：BDD 条目数（- PASS/- FAIL 行）= 证据文件数（M1 修复）
# exit 0 = 通过; exit 1 = 证据缺失; exit 2 = 无 P6 文件

set -euo pipefail

TASK_DIR="${1:?用法: check-p6-evidence.sh TASK_DIR}"
P6_FILE="$TASK_DIR/P6-acceptance.md"

[ ! -f "$P6_FILE" ] && exit 2

# 用现有协议约定的格式计数（- PASS / - FAIL 行）
BDD_COUNT=$(grep -cE '^\s*- (PASS|FAIL)' "$P6_FILE" || echo 0)

if [ "$BDD_COUNT" -eq 0 ]; then
    echo "GATE P6-EVIDENCE: P6-acceptance.md 无 BDD 条目（- PASS/- FAIL 格式）" >&2
    exit 1
fi

# 检查 P6-evidence/ 目录非空
EVIDENCE_DIR="$TASK_DIR/P6-evidence"
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
        while IFS= read -r -d '' img; do
            SIZE=$(stat -c%s "$img" 2>/dev/null || stat -f%z "$img" 2>/dev/null || echo 0)
            if [ "$SIZE" -le 1024 ]; then
                EMPTY_COUNT=$((EMPTY_COUNT + 1))
            fi
        done < <(find "$SCREENSHOTS_DIR" -type f -not -name '.*' -print0 2>/dev/null)
        if [ "$EMPTY_COUNT" -gt 0 ]; then
            echo "GATE P6-EVIDENCE: P6-evidence/screenshots/ 有 ${EMPTY_COUNT} 个文件 ≤ 1KB（疑似空 png 充数）" >&2
            exit 1
        fi
    fi
fi

exit 0
