#!/usr/bin/env bash
# agate-changes.sh — 显示与指定 tag 之间的协议变更（commit + 受影响文件）
# 用法：
#   bash ~/.agate/scripts/agate-changes.sh                    # 默认上一个 tag → HEAD
#   bash ~/.agate/scripts/agate-changes.sh v0.4.0..v0.5.0    # 任意范围
#   bash ~/.agate/scripts/agate-changes.sh --check-upstream   # 查远端是否有新版本
#
# 用途：agent 启动时快速掌握协议变化，对比'上次会话知道的版本'和当前版本
# 输出：commits + 受影响的协议文件 + 是否触及 Pre-commit 检查总览

set -euo pipefail

SCRIPT_REAL="$(readlink -f "${BASH_SOURCE[0]:-$0}" 2>/dev/null || echo "${BASH_SOURCE[0]:-$0}")"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_REAL")" 2>/dev/null && pwd || true)"
if [ -z "$SCRIPT_DIR" ]; then
    echo "ERROR: 无法解析脚本路径" >&2
    exit 1
fi

# agate 仓库根：从脚本路径向上逐级找 .git
_find_git_root() {
    local dir="$1"
    while [ "$dir" != "/" ]; do
        if [ -d "$dir/.git" ]; then
            echo "$dir"
            return 0
        fi
        dir=$(dirname "$dir")
    done
    return 1
}

GIT_TOPLEVEL="$(_find_git_root "$SCRIPT_DIR")"
if [ -z "$GIT_TOPLEVEL" ]; then
    echo "ERROR: 无法找到 agate git 仓库——脚本不在 agate 仓库内？" >&2
    exit 1
fi

# --check-upstream：查远端是否有新版本
if [ "${1:-}" = "--check-upstream" ]; then
    LOCAL_TAG="$(git -C "$GIT_TOPLEVEL" describe --tags --abbrev=0 2>/dev/null || echo "untagged")"
    git -C "$GIT_TOPLEVEL" fetch --all --tags --quiet 2>/dev/null || true
    UPSTREAM_TAG="$(git -C "$GIT_TOPLEVEL" tag --sort=-version:refname | head -1)"
    if [ "$LOCAL_TAG" = "$UPSTREAM_TAG" ]; then
        echo "agate 已是最新版本：$LOCAL_TAG"
    else
        echo "agate 有新版本可用：$UPSTREAM_TAG（本地 $LOCAL_TAG）"
        echo "更新方式：cd <agate 仓库> && git pull"
        echo "如果持续落后，检查 git remote 是否指向 https://github.com/randomgitsrc/agate.git"
        RANGE="${LOCAL_TAG}..origin/main"
        COMMIT_COUNT=$(git -C "$GIT_TOPLEVEL" log --oneline "$RANGE" 2>/dev/null | wc -l || echo 0)
        COMMIT_COUNT=$(echo "$COMMIT_COUNT" | tail -1)
        if [ "$COMMIT_COUNT" -gt 0 ]; then
            echo ""
            echo "自 $LOCAL_TAG 以来的变更（$COMMIT_COUNT commits）："
            git -C "$GIT_TOPLEVEL" log --oneline "$RANGE" 2>/dev/null | head -10 | sed 's/^/  /'
            if [ "$COMMIT_COUNT" -gt 10 ]; then
                echo "  ...（共 $COMMIT_COUNT commits，省略）"
            fi
        fi
    fi
    exit 0
fi

# 解析参数：默认 = 上一个 tag → HEAD
RANGE="${1:-}"

if [ -z "$RANGE" ]; then
    CURRENT_TAG="$(git -C "$GIT_TOPLEVEL" describe --tags --abbrev=0 2>/dev/null || echo "")"
    if [ -z "$CURRENT_TAG" ]; then
        echo "ERROR: 无法找到当前 tag——显式指定：bash $0 v0.4.0..HEAD" >&2
        exit 1
    fi
    PREV_TAG="$(git -C "$GIT_TOPLEVEL" tag --sort=-version:refname --merged "${CURRENT_TAG}^" 2>/dev/null | head -1)" || PREV_TAG=""
    if [ -z "$PREV_TAG" ]; then
        RANGE="${CURRENT_TAG}..HEAD"
    else
        RANGE="${PREV_TAG}..HEAD"
    fi
fi

# 单个 tag 参数自动补 ..HEAD
if ! [[ "$RANGE" == *..* ]]; then
    RANGE="${RANGE}..HEAD"
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
