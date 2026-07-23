#!/usr/bin/env bash
# check-retrospective.sh — 复盘异常触发（P2.12）
# 检测异常模式，输出复盘提醒（不中止 commit）
# exit 0 = 总是通过（只提醒不拦截）

set -euo pipefail

TASK_DIR="${1:?用法: check-retrospective.sh TASK_DIR}"
STATE_FILE="${2:-.state.yaml}"

# 异常模式检测
WARNINGS=""

# 1. gate 重试超限（按阶段差异化 MAX_RETRY，与 check-state-transition.sh 保持同步）
if [ -f "$STATE_FILE" ]; then
    RETRIES_OVER=$(STATE_FILE="$STATE_FILE" python3 -c "
import yaml, os
with open(os.environ['STATE_FILE']) as f:
    data = yaml.safe_load(f)
retries = data.get('retries', {})
max_map = dict(p.split(':') for p in 'P1:3,P2:3,P3:2,P4:3,P5:2,P6:2,P7:2,P8:2'.split(','))
if isinstance(retries, dict):
    for phase, attempts in retries.items():
        phase_max = int(max_map.get(phase, 3))
        if isinstance(attempts, list) and len(attempts) >= phase_max:
            print(f'{phase}={len(attempts)} (MAX={phase_max})')
            break
" 2>/dev/null || echo "")
    [ -n "$RETRIES_OVER" ] && WARNINGS="${WARNINGS}gate 重试超限（${RETRIES_OVER}）\n"
fi

# 2. SCOPE+ 触发
# C3 修复：扫描 *.md（与 check-scope-resolved.sh 一致）
if [ -d "$TASK_DIR" ]; then
    for f in "$TASK_DIR"/*.md; do
        [ -f "$f" ] || continue
        if grep -qE '^\s*-?\s*\[SCOPE\+\]' "$f" 2>/dev/null; then
            WARNINGS="${WARNINGS}SCOPE+ 触发（$(basename "$f")）\n"
            break
        fi
    done
fi

# 3. 裁剪 override 触发
if [ -d "$TASK_DIR" ] && [ -f "$TASK_DIR/P1-requirements.md" ]; then
    if grep -q '^override:' "$TASK_DIR/P1-requirements.md" 2>/dev/null; then
        WARNINGS="${WARNINGS}裁剪声明与执行不一致（override 触发）\n"
    fi
fi

if [ -n "$WARNINGS" ]; then
    echo "GATE RETRO: 建议复盘 — 检测到异常模式：" >&2
    printf '%b' "$WARNINGS" | while IFS= read -r line; do
        [ -n "$line" ] && echo "  - $line" >&2
    done
    echo "  请在版本 bump 前写简版复盘（docs/releases/v{version}-retrospective.md）" >&2
fi

exit 0
