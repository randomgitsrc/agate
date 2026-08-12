#!/usr/bin/env bats
# tests/unit/agate-workspace-resolve.bats — 工作区路径解析器单元测试（TAG0003）
# 被测：agate/scripts/agate-workspace-resolve.sh（P4 实现，当前不存在 → P3 红灯）
#
# 接口契约（P2-design.md §3.1，P4 实现必须满足）：
#   bash agate-workspace-resolve.sh [PROJECT_ROOT]   # PROJECT_ROOT 默认 $PWD
#   输出两行：AGATE_WORKSPACE=<绝对路径> 与 AGATE_TASKS_DIR=<绝对路径>
#   解析优先级：.agate.env 显式配置(AGATE_WORKSPACE=) > 环境变量 AGATE_TASKS_DIR > 默认 agate-workspace/

load ../helpers/load.bash

# 从解析器输出中提取 AGATE_WORKSPACE 值
ws_out() {
    echo "$output" | grep -E '^AGATE_WORKSPACE=' | head -1 | sed 's/^AGATE_WORKSPACE=//'
}

# 从解析器输出中提取 AGATE_TASKS_DIR 值
tasks_out() {
    echo "$output" | grep -E '^AGATE_TASKS_DIR=' | head -1 | sed 's/^AGATE_TASKS_DIR=//'
}

# 在指定项目根上运行解析器（未配置任何环境变量）
run_resolve() {
    local project="$1"
    run bash -c "bash '$AGATE_SCRIPTS/agate-workspace-resolve.sh' '$project'"
}

@test "WR.1 [BDD-2] 默认工作区位置为项目内 agate-workspace/" {
    local project
    project=$(mktemp -d "$BATS_TEST_TMPDIR/ws-XXXXXX")
    run_resolve "$project"
    [ "$status" -eq 0 ]
    [ "$(ws_out)" = "$(realpath -m "$project/agate-workspace")" ]
    [ "$(tasks_out)" = "$(realpath -m "$project/agate-workspace/tasks")" ]
}

@test "WR.2 [BDD-4] 无 .agate.env 时不报错、走默认位置" {
    local project
    project=$(mktemp -d "$BATS_TEST_TMPDIR/ws-XXXXXX")
    run_resolve "$project"
    [ "$status" -eq 0 ]
    [[ "$(ws_out)" == *"/agate-workspace" ]]
    [[ "$(tasks_out)" == *"/agate-workspace/tasks" ]]
}

@test "WR.3 [BDD-3] .agate.env 将工作区指向项目外绝对路径" {
    local project ext_ws
    project=$(mktemp -d "$BATS_TEST_TMPDIR/ws-XXXXXX")
    ext_ws=$(mktemp -d "$BATS_TEST_TMPDIR/ext-XXXXXX")
    printf 'AGATE_WORKSPACE=%s\n' "$ext_ws" > "$project/.agate.env"
    run_resolve "$project"
    [ "$status" -eq 0 ]
    [ "$(ws_out)" = "$(realpath -m "$ext_ws")" ]
    [ "$(tasks_out)" = "$(realpath -m "$ext_ws/tasks")" ]
    [ ! -d "$project/agate-workspace" ]
}

@test "WR.4 [BDD-3] .agate.env 相对路径相对项目根解析" {
    local project
    project=$(mktemp -d "$BATS_TEST_TMPDIR/ws-XXXXXX")
    printf 'AGATE_WORKSPACE=my-ws\n' > "$project/.agate.env"
    run_resolve "$project"
    [ "$status" -eq 0 ]
    [ "$(ws_out)" = "$(realpath -m "$project/my-ws")" ]
    [ "$(tasks_out)" = "$(realpath -m "$project/my-ws/tasks")" ]
}

@test "WR.5 [BDD-5] 工作区路径含空格仍正常解析" {
    local project
    project=$(mktemp -d "$BATS_TEST_TMPDIR/ws-XXXXXX")
    printf 'AGATE_WORKSPACE=My Project/agate-workspace\n' > "$project/.agate.env"
    run_resolve "$project"
    [ "$status" -eq 0 ]
    [ "$(ws_out)" = "$(realpath -m "$project/My Project/agate-workspace")" ]
    [ "$(tasks_out)" = "$(realpath -m "$project/My Project/agate-workspace/tasks")" ]
}

@test "WR.6 [BDD-13] 环境变量 AGATE_TASKS_DIR 作为二级解析源（向后兼容）" {
    local project tasks_base
    project=$(mktemp -d "$BATS_TEST_TMPDIR/ws-XXXXXX")
    tasks_base=$(realpath -m "$project/legacy-tasks")
    run env AGATE_TASKS_DIR="$tasks_base" bash -c "bash '$AGATE_SCRIPTS/agate-workspace-resolve.sh' '$project'"
    [ "$status" -eq 0 ]
    [ "$(tasks_out)" = "$tasks_base" ]
}

@test "WR.7 [BDD-13] .agate.env 显式配置优先于 AGATE_TASKS_DIR 环境变量" {
    local project
    project=$(mktemp -d "$BATS_TEST_TMPDIR/ws-XXXXXX")
    printf 'AGATE_WORKSPACE=env-wins\n' > "$project/.agate.env"
    run env AGATE_TASKS_DIR="$(realpath -m "$project/ignored-tasks")" bash -c "bash '$AGATE_SCRIPTS/agate-workspace-resolve.sh' '$project'"
    [ "$status" -eq 0 ]
    [ "$(ws_out)" = "$(realpath -m "$project/env-wins")" ]
    [ "$(tasks_out)" = "$(realpath -m "$project/env-wins/tasks")" ]
}

@test "WR.8 [BDD-11] orchestrator 从工作区内路径读取 project.md（解析输出锚定）" {
    local project
    project=$(mktemp -d "$BATS_TEST_TMPDIR/ws-XXXXXX")
    run_resolve "$project"
    [ "$status" -eq 0 ]
    local ws
    ws=$(ws_out)
    [ -n "$ws" ]
    [ "$(realpath -m "$ws/agents/project.md")" = "$(realpath -m "$project/agate-workspace/agents/project.md")" ]
}

@test "WR.9 [BDD-12] orchestrator 从工作区 tasks/ 读取任务看板（解析输出锚定）" {
    local project
    project=$(mktemp -d "$BATS_TEST_TMPDIR/ws-XXXXXX")
    run_resolve "$project"
    [ "$status" -eq 0 ]
    local tasks
    tasks=$(tasks_out)
    [ -n "$tasks" ]
    [ "$(realpath -m "$tasks/active-tasks.md")" = "$(realpath -m "$project/agate-workspace/tasks/active-tasks.md")" ]
}
