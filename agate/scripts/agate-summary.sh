#!/usr/bin/env bash
# agate-summary.sh — 输出当前 agate 版本 + 启动必读 + 防护状态
# 用法：bash ~/.agate/scripts/agate-summary.sh
# 用途：agent 启动时快速知道当前用什么协议版本，是否需要升级等

set -euo pipefail

# 当前路径（用 PWD 解析，避免依赖 $0）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || true)"
if [ -z "$SCRIPT_DIR" ]; then
    echo "GATE: 无法解析脚本路径（非 git 仓库或非标准安装？）" >&2
    exit 1
fi

# agate 仓库根：从脚本路径向上找 git 仓库（不是当前工作目录的仓库）
AGATE_REPO="$(git -C "$SCRIPT_DIR/../.." rev-parse --show-toplevel 2>/dev/null || echo "")"
if [ -z "$AGATE_REPO" ]; then
    echo "GATE: 无法找到 agate git 仓库——脚本不在 agate 仓库内？" >&2
    exit 1
fi

# 当前最新 tag（在 agate 仓库里查，不是项目仓库）
CURRENT_TAG="$(git -C "$AGATE_REPO" describe --tags --abbrev=0 2>/dev/null || echo "untagged")"
BRANCH="$(git -C "$AGATE_REPO" branch --show-current 2>/dev/null || echo "?")"
HEAD_SHA="$(git -C "$AGATE_REPO" rev-parse --short HEAD 2>/dev/null || echo "?")"

# 最近 3 commits（agate 仓库的，不是项目仓库的）
RECENT_COMMITS="$(git -C "$AGATE_REPO" log --oneline -3 2>/dev/null | sed 's/^/  /')"

# 防护机制清单（用于 agent 快速理解当前协议能力）
GUARDS=""
for script in check-state-yaml.sh check-gate.sh check-changelog.sh check-p6-evidence.sh check-p6-provenance.sh check-state-transition.sh check-pruning.sh check-scope-resolved.sh check-retrospective.sh; do
    if [ -f "$SCRIPT_DIR/$script" ]; then
        GUARDS="$GUARDS  ✓ $script\n"
    fi
done
if [ -x "$SCRIPT_DIR/pre-commit-gate.sh" ]; then
    GUARDS="$GUARDS  ✓ pre-commit-gate.sh（hook 入口）\n"
fi
if [ -x "$SCRIPT_DIR/ci-gate-backstop.py" ]; then
    GUARDS="$GUARDS  ✓ ci-gate-backstop.py（CI 兜底）\n"
fi

cat <<EOF
=== agate 当前状态 ===

版本：$CURRENT_TAG
分支：$BRANCH
HEAD：$HEAD_SHA

最近 3 commits：
$RECENT_COMMITS

防护机制（pre-commit + CI）：
$(printf '%b' "$GUARDS")

快速版本对比：bash ~/.agate/scripts/agate-changes.sh [since-tag]
默认输出自上一个 tag 起的 commit + 受影响的协议文件。
例：bash ~/.agate/scripts/agate-changes.sh ${CURRENT_TAG}
查远端更新：bash ~/.agate/scripts/agate-changes.sh --check-upstream

=== 启动时建议 ===

1. 第一行：上面这一段（确认协议版本 + 防护机制就位）
2. 读 ~/.agate/AGENTS.md（协议本体入口指引）
3. 读 ~/.agate/CHANGELOG.md（$CURRENT_TAG 段，了解自上次会话以来发生了什么）
4. 按 orchestrator-template.md 列的 8 文件必读顺序读规则

EOF
