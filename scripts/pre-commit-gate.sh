#!/usr/bin/env bash
# pre-commit-gate.sh — pre-commit hook 入口
# 安装到 .git/hooks/pre-commit，每次 git commit 自动触发。
#
# Phase 1: P1.1 跑 gate 写 .gate-result.json
#          P1.2 PROD_TOUCHED 检测
#          P1.6 CHANGELOG 检查
#          P1.7 P6 证据格式检查
# Phase 2A: P2.3-P2.5 状态转移检查
#
# 触发条件：.state.yaml phase 变更 OR 阶段产出文件变更

set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)

# R1 修复：source 后验证函数已加载，防止静默放行
source "$REPO_ROOT/scripts/gate-result.sh" \
    || { echo "GATE ERROR: 无法加载 gate-result.sh" >&2; exit 1; }
type write_gate_result >/dev/null 2>&1 \
    || { echo "GATE ERROR: gate-result.sh 加载不完整（write_gate_result 未定义）" >&2; exit 1; }

STATE_FILE="$REPO_ROOT/.state.yaml"
AGATE_TASKS_DIR="${AGATE_TASKS_DIR:-docs/tasks}"

# 0. 检测是否需要触发 gate
NEEDS_GATE=false
has_staged_phase_change "$STATE_FILE" && NEEDS_GATE=true
[ "$NEEDS_GATE" = false ] && has_staged_phase_output && NEEDS_GATE=true

if [ "$NEEDS_GATE" = false ]; then
    exit 0
fi

# 1. 读取当前状态
PHASE=$(read_state_phase "$STATE_FILE")
TASK_ID=$(read_state_task_id "$STATE_FILE")

[ -z "$PHASE" ] && exit 0

TASK_DIR="$REPO_ROOT/$AGATE_TASKS_DIR/$TASK_ID"

# 2. PROD_TOUCHED 检测（P1.2）
# R2 修复：扫描暂存 diff 内容，不扫文件全文（协议文件本身含 PROD_TOUCHED 字样）
if git diff --cached | grep -q '\[PROD_TOUCHED\]'; then
    echo "GATE: 检测到 [PROD_TOUCHED] 标记，中止 commit" >&2
    exit 1
fi

# 3. 状态转移检查（P2.3-P2.5）
if [ -f "$STATE_FILE" ]; then
    bash "$REPO_ROOT/scripts/check-state-transition.sh" "$STATE_FILE" || exit 1
fi

# 4. 运行 gate（P1.1）
GATE_OUTPUT=""
GATE_EXIT=2

if [ "$PHASE" != "PAUSED" ] && [ "$PHASE" != "READY" ] && [ "$PHASE" != "DONE" ] && [ -d "$TASK_DIR" ]; then
    GATE_OUTPUT=$(bash "$REPO_ROOT/scripts/check-gate.sh" "$PHASE" "$TASK_DIR" 2>&1) && GATE_EXIT=0 || GATE_EXIT=$?
fi

write_gate_result "$PHASE" "$TASK_ID" "$GATE_EXIT" "$GATE_OUTPUT"

# 5. CHANGELOG 检查（P1.6）——警告不中止
if [ -n "$TASK_ID" ]; then
    bash "$REPO_ROOT/scripts/check-changelog.sh" "$TASK_ID" 2>/dev/null || \
        echo "GATE CHANGELOG: 警告 — [Unreleased] 未记录 ${TASK_ID}" >&2
fi

# 6. P6 证据格式检查（P1.7）——中止
if [ "$PHASE" = "P6" ] || [ "$PHASE" = "P7" ]; then
    if [ -d "$TASK_DIR" ]; then
        bash "$REPO_ROOT/scripts/check-p6-evidence.sh" "$TASK_DIR" || exit 1
    fi
fi

# 7. gate 结果处理
case "$GATE_EXIT" in
    0) echo "GATE $PHASE: 通过" >&2; exit 0 ;;
    1) echo "GATE $PHASE: 未通过" >&2; echo "$GATE_OUTPUT" >&2; exit 1 ;;
    2) echo "GATE $PHASE: 需主 Agent 手动判断" >&2; echo "$GATE_OUTPUT" >&2; exit 0 ;;
esac
