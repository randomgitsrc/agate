#!/usr/bin/env bats
# tests/sanity.bats — 框架 sanity check
# 验证 helpers/load.bash、fixtures.bash、git-helper.bash 都能正常 load 并执行
#
# 这个文件不算"覆盖度"里的测试用例（计划 119 个不包括），
# 是基础设施正确性自检，CI 跑前先确认 framework 本身没坏。

load helpers/load.bash

@test "load.bash: AGATE_ROOT 解析正确" {
    [ -d "$AGATE_ROOT/scripts" ]
    [ -d "$AGATE_ROOT/assets" ]
    [ -d "$AGATE_ROOT/tests" ]
}

@test "fixtures.bash: create_task_dir 默认全阶段" {
    local dir
    dir=$(create_task_dir)
    [ -f "$dir/.state.yaml" ]
    [ -f "$dir/P0-brief.md" ]
    [ -f "$dir/P1-requirements.md" ]
    [ -f "$dir/P2-design.md" ]
    [ -f "$dir/P8-release.md" ]
}

@test "fixtures.bash: create_task_dir 自定义 phases" {
    local dir
    dir=$(create_task_dir P0 P1 P3 P4 P5 P6 P7 P8)
    [ -f "$dir/P0-brief.md" ]
    [ ! -f "$dir/P2-design.md" ]  # P2 不在
}

@test "fixtures.bash: add_pruning_excuse 正确写入" {
    local dir
    dir=$(create_task_dir P0 P1 P3 P4 P5 P6 P7 P8)
    add_pruning_excuse "$dir" P2 "无设计必要" "低风险"
    grep -q "裁剪 P2" "$dir/P1-requirements.md"
    grep -q "跳过风险" "$dir/P1-requirements.md"
}

@test "git-helper.bash: git_init 创建有效 repo" {
    local repo
    repo=$(git_init)
    [ -d "$repo/.git" ]
}

@test "git-helper.bash: git_commit + git_stage 工作" {
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md"
    git_commit "$repo" "init commit"
    git_log=$(git -C "$repo" log --oneline | wc -l)
    [ "$git_log" -eq 1 ]
}
