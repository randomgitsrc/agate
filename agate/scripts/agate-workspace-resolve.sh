#!/usr/bin/env bash
# agate-workspace-resolve.sh — 工作区路径单点解析器（TAG0003 v2.0）
# 解析优先级（P2-design.md §3.1）：
#   1. 项目根 .agate.env 的 AGATE_WORKSPACE=（相对路径相对项目根解析 / 绝对路径原样 / 可含空格）
#   2. 环境变量 AGATE_TASKS_DIR（二级，向后兼容：允许直接指定 tasks 目录）
#   3. 默认 {project_root}/agate-workspace，tasks_base = 工作区根/tasks
#
# 用法：
#   执行模式：bash agate-workspace-resolve.sh [PROJECT_ROOT]   # PROJECT_ROOT 默认 $PWD
#     输出两行：AGATE_WORKSPACE=<绝对路径> / AGATE_TASKS_DIR=<绝对路径>
#   复用模式：source agate-workspace-resolve.sh [PROJECT_ROOT] # export 同名变量，不输出
#
# 边界：解析器不创建任何目录；全程引号包裹 + realpath -m 归一（含空格路径，BDD-5）。

set -euo pipefail

PROJECT_ROOT="${1:-$PWD}"

# 归一为绝对路径（相对/绝对、含空格均安全）
resolve_abs() {
    local base="$1" p="$2"
    case "$p" in
        /*) realpath -m "$p" ;;
        *) realpath -m "$base/$p" ;;
    esac
}

PROJECT_ROOT=$(realpath -m "$PROJECT_ROOT")

# 1) .agate.env 显式配置（最高优先）
WS_VALUE=""
if [ -f "$PROJECT_ROOT/.agate.env" ]; then
    WS_VALUE=$(grep -E '^AGATE_WORKSPACE=' "$PROJECT_ROOT/.agate.env" 2>/dev/null | tail -1 | sed 's/^AGATE_WORKSPACE=//' || true)
fi

if [ -n "$WS_VALUE" ]; then
    AGATE_WORKSPACE=$(resolve_abs "$PROJECT_ROOT" "$WS_VALUE")
    AGATE_TASKS_DIR="$AGATE_WORKSPACE/tasks"
else
    # 2) 环境变量 AGATE_TASKS_DIR（二级，向后兼容）
    if [ -n "${AGATE_TASKS_DIR:-}" ]; then
        AGATE_TASKS_DIR=$(resolve_abs "$PROJECT_ROOT" "$AGATE_TASKS_DIR")
        AGATE_WORKSPACE=$(dirname "$AGATE_TASKS_DIR")
    else
        # 3) 默认 agate-workspace/
        AGATE_WORKSPACE="$PROJECT_ROOT/agate-workspace"
        AGATE_TASKS_DIR="$AGATE_WORKSPACE/tasks"
    fi
fi

export AGATE_WORKSPACE AGATE_TASKS_DIR

# 执行模式：输出两行供 python subprocess / CLI 消费；复用模式（source）只 export
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
    printf 'AGATE_WORKSPACE=%s\n' "$AGATE_WORKSPACE"
    printf 'AGATE_TASKS_DIR=%s\n' "$AGATE_TASKS_DIR"
fi
