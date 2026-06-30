#!/usr/bin/env bash
# pre-commit-gate.sh — pre-commit hook 入口
# 安装到 .git/hooks/pre-commit，每次 git commit 自动触发。
#
# Phase 1: P1.1 跑 gate 写 .gate-result.json
#          P1.2 PROD_TOUCHED 检测
#          P1.6 CHANGELOG 检查
#          P1.7 P6 证据格式检查
# Phase 2A: P2.3-P2.5 状态转移检查
#           P2.15 .state.yaml 格式校验
#
# 触发条件：.state.yaml phase 变更 OR 阶段产出文件变更

set -euo pipefail

# REPO_ROOT = 当前 git 仓库根（项目仓库或 agate 仓库本身）
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)

# AGATE_ROOT = 协议本体路径（默认 ~/.agate 软链接 → 你克隆的 agate 仓库的 agate/ 子目录）
# 协议脚本路径用 AGATE_ROOT 解析；项目运行时文件用 REPO_ROOT 解析
AGATE_ROOT="${AGATE_ROOT:-$HOME/.agate}"

# R1 修复：source 后验证函数已加载，防止静默放行
source "$AGATE_ROOT/scripts/gate-result.sh" \
    || { echo "GATE ERROR: 无法加载 gate-result.sh" >&2; exit 1; }
type write_gate_result >/dev/null 2>&1 \
    || { echo "GATE ERROR: gate-result.sh 加载不完整（write_gate_result 未定义）" >&2; exit 1; }

STATE_FILE="$REPO_ROOT/.state.yaml"
AGATE_TASKS_DIR="${AGATE_TASKS_DIR:-docs/tasks}"

# 0. 文件级校验：.state.yaml 有任何变更就跑格式校验（不依赖 phase 变更）
# S1 修复：之前格式校验在 NEEDS_GATE 之后，phase 不变时不触发
STATE_BASENAME=$(basename "$STATE_FILE")
if git diff --cached --name-only 2>/dev/null | grep -qF "$STATE_BASENAME"; then
    if [ -f "$STATE_FILE" ]; then
        bash "$AGATE_ROOT/scripts/check-state-yaml.sh" "$STATE_FILE" || exit 1
    fi
fi

# 1. 检测是否需要触发 gate（阶段级校验）
NEEDS_GATE=false
has_staged_phase_change "$STATE_FILE" && NEEDS_GATE=true
[ "$NEEDS_GATE" = false ] && has_staged_phase_output && NEEDS_GATE=true

if [ "$NEEDS_GATE" = false ]; then
    exit 0
fi

# 2. 读取当前状态
PHASE=$(read_state_phase "$STATE_FILE")
TASK_ID=$(read_state_task_id "$STATE_FILE")

[ -z "$PHASE" ] && exit 0

TASK_DIR="$REPO_ROOT/$AGATE_TASKS_DIR/$TASK_ID"

# 3. PROD_TOUCHED 检测（P1.2）
# R2 修复：扫描暂存 diff 内容，不扫文件全文（协议文件本身含 PROD_TOUCHED 字样）
if git diff --cached | grep -q '\[PROD_TOUCHED\]'; then
    echo "GATE: 检测到 [PROD_TOUCHED] 标记，中止 commit" >&2
    exit 1
fi

# 4. 状态转移检查（P2.3-P2.5）
if [ -f "$STATE_FILE" ]; then
    bash "$AGATE_ROOT/scripts/check-state-transition.sh" "$STATE_FILE" || exit 1
fi

# 5. 运行 gate（P1.1）
GATE_OUTPUT=""
GATE_EXIT=2

if [ "$PHASE" != "PAUSED" ] && [ "$PHASE" != "READY" ] && [ "$PHASE" != "DONE" ] && [ -d "$TASK_DIR" ]; then
    GATE_OUTPUT=$(bash "$AGATE_ROOT/scripts/check-gate.sh" "$PHASE" "$TASK_DIR" 2>&1) && GATE_EXIT=0 || GATE_EXIT=$?
fi

write_gate_result "$PHASE" "$TASK_ID" "$GATE_EXIT" "$GATE_OUTPUT"

# 5.4 P6 客观行为审计（P2.1/P2.10 降级方案 v2）
if [ "$GATE_EXIT" != "1" ] && [ -n "$TASK_ID" ] && [ -d "$TASK_DIR" ]; then
    PROV_EXIT=0
    bash "$AGATE_ROOT/scripts/check-p6-provenance.sh" "$TASK_DIR" || PROV_EXIT=$?
    if [ "$PROV_EXIT" -eq 1 ]; then
        exit 1
    fi
fi

# 5.5 裁剪条件检查（P2.7-P2.9）——gate 未通过时跳过（gate 错误优先）
if [ "$GATE_EXIT" != "1" ] && [ -n "$TASK_ID" ] && [ -d "$TASK_DIR" ]; then
    bash "$AGATE_ROOT/scripts/check-pruning.sh" "$TASK_DIR" || exit 1
fi

# 5.6 SCOPE+ 追踪检查（P2.11）——gate 未通过时跳过
if [ "$GATE_EXIT" != "1" ] && [ -n "$TASK_ID" ] && [ -d "$TASK_DIR" ]; then
    bash "$AGATE_ROOT/scripts/check-scope-resolved.sh" "$TASK_DIR" || exit 1
fi

# 5.7 复盘异常触发（P2.12）——只提醒不中止，gate 失败时也提醒
if [ -n "$TASK_ID" ] && [ -d "$TASK_DIR" ]; then
    bash "$AGATE_ROOT/scripts/check-retrospective.sh" "$TASK_DIR" "$STATE_FILE" 2>/dev/null || true
fi

# 6. CHANGELOG 检查（P1.6）——警告不中止
if [ -n "$TASK_ID" ]; then
    bash "$AGATE_ROOT/scripts/check-changelog.sh" "$TASK_ID" 2>/dev/null || \
        echo "GATE CHANGELOG: 警告 — [Unreleased] 未记录 ${TASK_ID}" >&2
fi

# 7. P6 证据格式检查（P1.7）——中止
if [ "$PHASE" = "P6" ] || [ "$PHASE" = "P7" ]; then
    if [ -d "$TASK_DIR" ]; then
        bash "$AGATE_ROOT/scripts/check-p6-evidence.sh" "$TASK_DIR" || exit 1
    fi
fi

# 8. gate 结果处理
case "$GATE_EXIT" in
    0) echo "GATE $PHASE: 通过" >&2; exit 0 ;;
    1) echo "GATE $PHASE: 未通过" >&2; echo "$GATE_OUTPUT" >&2; exit 1 ;;
    2) echo "GATE $PHASE: 需主 Agent 手动判断" >&2; echo "$GATE_OUTPUT" >&2; exit 0 ;;
esac
