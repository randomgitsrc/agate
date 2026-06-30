#!/usr/bin/env bash
# check-pruning.sh — 裁剪条件检查（P2.7-P2.9）
# 检查 P1-requirements.md 的 risk_level + phases 声明是否符合裁剪条件
# exit 0 = 通过; exit 1 = 裁剪条件不满足; exit 2 = 无 P1 文件

set -euo pipefail

TASK_DIR="${1:?用法: check-pruning.sh TASK_DIR}"
P1_FILE="$TASK_DIR/P1-requirements.md"

[ ! -f "$P1_FILE" ] && exit 2

# R1 修复：所有 Python 调用用环境变量传参，避免 shell 变量注入
RISK_LEVEL=$(P1_FILE="$P1_FILE" python3 -c "
import re, os
with open(os.environ['P1_FILE']) as f:
    text = f.read()
m = re.search(r'risk_level:\s*(low|medium|high)', text)
print(m.group(1) if m else '')
" 2>/dev/null || echo "")

PHASES_DECLARED=$(P1_FILE="$P1_FILE" python3 -c "
import re, os
with open(os.environ['P1_FILE']) as f:
    text = f.read()
m = re.search(r'phases:\s*\[([^\]]+)\]', text)
if m:
    phases = [p.strip() for p in m.group(1).split(',')]
    print(' '.join(phases))
" 2>/dev/null || echo "")

HAS_OVERRIDE=$(grep -c '^override:' "$P1_FILE" 2>/dev/null || echo 0)

ERRORS=""

# 检查 1：risk_level 必须存在
if [ -z "$RISK_LEVEL" ]; then
    ERRORS="${ERRORS}P1-requirements.md 缺 risk_level 字段\n"
fi

# M1 修复：用 grep -qw 替代 \b，更可移植
# 检查 2：裁剪 P2 的条件
# C2 修复：BDD ≤ 10 从 hook 移到流程层（BDD 格式不固定，hook 无法可靠计数）
if ! echo "$PHASES_DECLARED" | grep -qw 'P2'; then
    if [ "$RISK_LEVEL" != "low" ]; then
        ERRORS="${ERRORS}裁剪 P2 需 risk_level=low，实际=${RISK_LEVEL}\n"
    fi
fi

# 检查 3：裁剪 P6 的条件（不可裁，除非 no_behavior_change）
if ! echo "$PHASES_DECLARED" | grep -qw 'P6'; then
    if ! grep -q 'no_behavior_change:\s*true' "$P1_FILE" 2>/dev/null; then
        ERRORS="${ERRORS}P6 不可裁剪（除非 no_behavior_change: true）\n"
    fi
fi

# 检查 4：裁剪 P3 的条件
if ! echo "$PHASES_DECLARED" | grep -qw 'P3'; then
    if [ "$RISK_LEVEL" = "high" ]; then
        ERRORS="${ERRORS}高风险任务不可裁剪 P3\n"
    fi
fi

if [ -n "$ERRORS" ]; then
    echo "GATE PRUNING: 裁剪条件不满足：" >&2
    printf "$ERRORS" | while IFS= read -r line; do
        [ -n "$line" ] && echo "  - $line" >&2
    done
    exit 1
fi

exit 0
