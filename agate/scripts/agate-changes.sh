#!/usr/bin/env bash
# agate-changes.sh — 显示与指定 tag 之间的协议变更（commit + 受影响文件）
# 用法：
#   bash ~/.agate/scripts/agate-changes.sh                    # 默认上一个 tag → HEAD
#   bash ~/.agate/scripts/agate-changes.sh v0.4.0            # v0.4.0 → HEAD
#   bash ~/.agate/scripts/agate-changes.sh v0.4.0..v0.5.0    # 任意范围
#
# 用途：agent 启动时快速掌握协议变化，对比'上次会话知道的版本'和当前版本
# 输出：commits + 受影响的协议文件 + 是否触及 Pre-commit 检查总览

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || true)"
if [ -z "$SCRIPT_DIR" ]; then
    echo "ERROR: 无法解析脚本路径" >&2
    exit 1
fi

# 找仓库根（处理 ~/.agate 软链接）
GIT_TOPLEVEL="$(git rev-parse --show-toplevel 2>/dev/null || echo "")"
if [ -z "$GIT_TOPLEVEL" ]; then
    echo "ERROR: 无法找到 git 仓库根" >&2
    exit 1
fi

# 解析参数：默认 = 上一个 tag → HEAD
RANGE="${1:-}"

if [ -z "$RANGE" ]; then
    CURRENT_TAG="$(git -C "$GIT_TOPLEVEL" describe --tags --abbrev=0 2>/dev/null || echo "")"
    if [ -z "$CURRENT_TAG" ]; then
        echo "ERROR: 无法找到当前 tag——显式指定：bash $0 v0.4.0..HEAD" >&2
        exit 1
    fi
    # 找当前 tag 的前一个 tag：列出当前 tag 的所有祖先 commit 能到达的 tag
    PREV_TAG="$(git -C "$GIT_TOPLEVEL" tag --sort=-version:refname --merged "${CURRENT_TAG}^" 2>/dev/null | head -1)" || PREV_TAG=""
    if [ -z "$PREV_TAG" ]; then
        # 没有 更早的 tag，从当前 tag 开始
        RANGE="${CURRENT_TAG}..HEAD"
    else
        RANGE="${PREV_TAG}..HEAD"
    fi
fi

# 检查范围格式
if ! [[ "$RANGE" == *..* ]]; then
    echo "ERROR: 范围需 A..B 格式，例 v0.4.0..v0.5.0 或 v0.4.0..HEAD" >&2
    exit 1
fi

# 检查两端 tag 是否存在（用 git rev-parse 验证）
START="${RANGE%%..*}"
END="${RANGE##*..}"
if ! git -C "$GIT_TOPLEVEL" rev-parse "$START" >/dev/null 2>&1; then
    echo "ERROR: '$START' 不是有效 ref（tag/commit）" >&2
    exit 1
fi
if ! git -C "$GIT_TOPLEVEL" rev-parse "$END" >/dev/null 2>&1; then
    echo "ERROR: '$END' 不是有效 ref（tag/commit）" >&2
    exit 1
fi

cat <<EOF
=== agate 协议变化 ===
范围：$RANGE

EOF

# 1. 列出 commits
echo "--- commits ---"
git -C "$GIT_TOPLEVEL" log --oneline "$RANGE" | sed 's/^/  /'

# 2. 受影响的协议/脚本/工作流文件（过滤删除的，只看当前 HEAD 还存在的）
echo ""
echo "--- 协议文件改动 ---"
# --diff-filter=acm: added/copied/modified（排除 deleted，但保留 rename 的新路径——rename 在 git 里是 D+A，acm 能拿到新路径）
CHANGED_FILES="$(git -C "$GIT_TOPLEVEL" diff --name-only --diff-filter=acm "$RANGE" | sort -u)"
if [ -z "$CHANGED_FILES" ]; then
    echo "  （无文件改动）"
else
    echo "$CHANGED_FILES" | sed 's/^/  /'
fi

# 3. 分组提示——哪些是高频影响
echo ""
echo "--- 重要性分类 ---"
echo "$CHANGED_FILES" | grep -E "^agate/WORKFLOW\.md$|^agate/state-machine\.md$|^agate/dispatch-protocol\.md$" >/dev/null && \
    echo "  ⚠️  触及核心流程文件——orchestrator 必须仔细读"
echo "$CHANGED_FILES" | grep -E "^agate/scripts/.*\.sh$|^agate/scripts/.*\.py$" >/dev/null && \
    echo "  ⚙️  触及 gate 检查脚本——commit 时行为可能变化"
echo "$CHANGED_FILES" | grep -E "^agate/assets/execution-roles/|^agate/assets/review-roles/" >/dev/null && \
    echo "  🎭  触及角色定义——subagent 行为可能变化"
echo "$CHANGED_FILES" | grep -E "^agate/AGENTS\.md$|^agate/orchestrator-template\.md$" >/dev/null && \
    echo "  📖  触及入口/模板——orchestrator 启动行为可能变化"
echo "$CHANGED_FILES" | grep -E "^README\.md$|^CHANGELOG\.md$" >/dev/null && \
    echo "  📜  触及对外文档"

# 4. 推荐决策表（给 agent 判断要不要重读）
echo ""
echo "--- 快速决策 ---"
# 用 grep -c 但要捕获单行整数（用 echo | grep 避免多行问题）
HIGH_IMPACT=$(echo "$CHANGED_FILES" | grep -cE "^agate/(WORKFLOW|state-machine|dispatch-protocol|orchestrator-template|AGENTS)\.md$|^agate/assets/execution-roles/|^agate/assets/review-roles/|^agate/scripts/.*\.(sh|py)$" || echo 0)
# HIGH_IMPACT 可能含换行，取最后一个值
HIGH_IMPACT=$(echo "$HIGH_IMPACT" | tail -1)
if [ "$HIGH_IMPACT" -eq 0 ]; then
    echo "  当前变更影响小（无核心文件改动）——可只读 CHANGELOG.md 即可"
elif [ "$HIGH_IMPACT" -lt 3 ]; then
    echo "  中等变更（$HIGH_IMPACT 个核心文件）——重读变更的 8 个必读文件中受影响的那几份"
else
    echo "  重大变更（$HIGH_IMPACT 个核心文件）——完整重读 8 个必读文件"
fi

echo ""
echo "=== 完毕 ==="
