#!/usr/bin/env bash
# tests/helpers/git-helper.bash — 临时 git 仓库工具
# 用于测试 check-pruning.sh / check-state-transition.sh / pre-commit-hook 等需要真实 git 的脚本
#
# 用法：
#   repo=$(git_init)
#   git_commit $repo "init"
#   git_stage $repo "file.py"
#   git_staged_diff $repo  # 输出当前暂存区的 diff

# git_init [dir]
# 在指定目录（默认 $BATS_TEST_TMPDIR/repo-XXX）初始化 git 仓库
# 返回仓库路径
git_init() {
    local dir="${1:-}"
    if [ -z "$dir" ]; then
        dir=$(mktemp -d "$BATS_TEST_TMPDIR/repo-XXXXXX")
    fi

    mkdir -p "$dir"
    git -C "$dir" init -q
    git -C "$dir" config user.email "test@test.local"
    git -C "$dir" config user.name "Test"
    git -C "$dir" config commit.gpgsign false

    echo "$dir"
}

# git_commit <repo> <message> [files...]
# commit 指定文件（默认 commit 全部已暂存 + 暂存区全部 + 未跟踪文件）
git_commit() {
    local repo="$1"
    local msg="$2"
    shift 2
    local files=("$@")

    if [ ${#files[@]} -gt 0 ]; then
        git -C "$repo" add "${files[@]}"
    else
        # 无指定文件 → 暂存所有已跟踪的变更 + 未跟踪的新文件
        git -C "$repo" add -A
    fi
    git -C "$repo" commit -q -m "$msg"
}

# git_stage <repo> <file>
# git add 指定文件（必须在仓库内）
git_stage() {
    local repo="$1"
    local file="$2"
    git -C "$repo" add "$file"
}

# git_staged_diff <repo>
# 输出当前暂存区 diff（空表示无变更）
git_staged_diff() {
    local repo="$1"
    git -C "$repo" diff --cached
}

# git_staged_files <repo>
# 输出当前暂存区文件名列表
git_staged_files() {
    local repo="$1"
    git -C "$repo" diff --cached --name-only
}
