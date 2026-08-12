#!/usr/bin/env bats
# tests/unit/agate-migrate-workspace.bats — 工作区迁移工具单元测试（TAG0003）
# 被测：agate/scripts/agate-migrate-workspace.sh（P4 实现，当前不存在 → P3 红灯）
#
# 接口契约（P2-design.md §3.2，P4 实现必须满足）：
#   在项目根运行；可选 --to <workspace> 覆盖目标
#   docs/tasks → {workspace}/tasks、docs/archived → {workspace}/archived（git mv 目录级）
#   空源 no-op exit 0；迁移幂等；仓库外目标 fallback 普通 mv + WARNING

load ../helpers/load.bash

@test "MW.1 [BDD-6] docs/tasks 内容迁入工作区 tasks/ 下" {
    local repo
    repo=$(git_init)
    mkdir -p "$repo/docs/tasks/T001"
    echo "## 看板" > "$repo/docs/tasks/active-tasks.md"
    echo "# P1" > "$repo/docs/tasks/T001/P1-requirements.md"
    git_commit "$repo" "init"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/agate-migrate-workspace.sh'"
    [ "$status" -eq 0 ]
    [ -f "$repo/agate-workspace/tasks/active-tasks.md" ]
    [ -f "$repo/agate-workspace/tasks/T001/P1-requirements.md" ]
    [ ! -e "$repo/docs/tasks" ]
}

@test "MW.2 [BDD-7] .state.yaml 与阶段产出完整随任务目录迁移（含 gitignore 文件）" {
    local repo
    repo=$(git_init)
    printf '*.state.yaml\n' > "$repo/.gitignore"
    mkdir -p "$repo/docs/tasks/T001"
    cat > "$repo/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P1
status: active
retries: {}
EOF
    echo "# P1" > "$repo/docs/tasks/T001/P1-requirements.md"
    echo "# P2" > "$repo/docs/tasks/T001/P2-design.md"
    echo "# P7" > "$repo/docs/tasks/T001/P7-consistency.md"
    git_commit "$repo" "init"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/agate-migrate-workspace.sh'"
    [ "$status" -eq 0 ]
    [ -f "$repo/agate-workspace/tasks/T001/.state.yaml" ]
    [ -f "$repo/agate-workspace/tasks/T001/P1-requirements.md" ]
    [ -f "$repo/agate-workspace/tasks/T001/P2-design.md" ]
    [ -f "$repo/agate-workspace/tasks/T001/P7-consistency.md" ]
    [ "$(find "$repo/agate-workspace/tasks/T001" -type f | wc -l)" -eq 4 ]
}

@test "MW.3 [BDD-8] 迁移保留 git 历史（文件移动而非删除重建）" {
    local repo
    repo=$(git_init)
    mkdir -p "$repo/docs/tasks/T001"
    echo "unique-content-for-history" > "$repo/docs/tasks/T001/P1-requirements.md"
    git_commit "$repo" "orig task file"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/agate-migrate-workspace.sh'"
    [ "$status" -eq 0 ]
    local history
    history=$(git -C "$repo" log --follow --oneline -- agate-workspace/tasks/T001/P1-requirements.md 2>/dev/null)
    [[ "$history" == *"orig task file"* ]]
}

@test "MW.4 [BDD-9] 迁移幂等——重复运行无新增迁移动作" {
    local repo
    repo=$(git_init)
    mkdir -p "$repo/docs/tasks/T001"
    echo "# P1" > "$repo/docs/tasks/T001/P1-requirements.md"
    git_commit "$repo" "init"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/agate-migrate-workspace.sh'"
    [ "$status" -eq 0 ]
    local before
    before=$(find "$repo/agate-workspace/tasks" -type f | sort)
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/agate-migrate-workspace.sh'"
    [ "$status" -eq 0 ]
    [ "$(find "$repo/agate-workspace/tasks" -type f | sort)" = "$before" ]
    [ ! -e "$repo/docs/tasks" ]
}

@test "MW.5 [BDD-10] 旧布局迁移输出明确指引（不静默完成）" {
    local repo
    repo=$(git_init)
    mkdir -p "$repo/docs/tasks/T001"
    echo "# P1" > "$repo/docs/tasks/T001/P1-requirements.md"
    git_commit "$repo" "init"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/agate-migrate-workspace.sh'"
    [ "$status" -eq 0 ]
    [ -n "$output" ]
    [[ "$output" == *"迁移"* ]]
}

@test "MW.6 [BDD-18] 存量归档迁入工作区 archived/ 且相对结构保留、幂等" {
    local repo
    repo=$(git_init)
    mkdir -p "$repo/docs/archived/tasks/T009-archive"
    echo "# P7" > "$repo/docs/archived/tasks/T009-archive/P7-consistency.md"
    echo "# P8" > "$repo/docs/archived/tasks/T009-archive/P8-release.md"
    git_commit "$repo" "init"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/agate-migrate-workspace.sh'"
    [ "$status" -eq 0 ]
    [ -f "$repo/agate-workspace/archived/tasks/T009-archive/P7-consistency.md" ]
    [ -f "$repo/agate-workspace/archived/tasks/T009-archive/P8-release.md" ]
    [ ! -e "$repo/docs/archived" ]
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/agate-migrate-workspace.sh'"
    [ "$status" -eq 0 ]
    [ "$(find "$repo/agate-workspace/archived" -type f | wc -l)" -eq 2 ]
}

@test "MW.7 [BDD-19] 项目从无 docs/tasks 时迁移工具正常运行（空源 no-op）" {
    local repo
    repo=$(git_init)
    echo "readme" > "$repo/README.md"
    git_commit "$repo" "init"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/agate-migrate-workspace.sh'"
    [ "$status" -eq 0 ]
    [ ! -e "$repo/docs/tasks" ]
    [ ! -d "$repo/agate-workspace/tasks" ]
}

@test "MW.8 [BDD-8] 仓库外目标 fallback 普通 mv + WARNING（git 历史限制标注）" {
    local repo ext_ws
    repo=$(git_init)
    ext_ws=$(mktemp -d "$BATS_TEST_TMPDIR/ext-ws-XXXXXX")
    mkdir -p "$repo/docs/tasks/T001"
    echo "# P1" > "$repo/docs/tasks/T001/P1-requirements.md"
    git_commit "$repo" "init"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/agate-migrate-workspace.sh' --to '$ext_ws'"
    [ "$status" -eq 0 ]
    [ -f "$ext_ws/tasks/T001/P1-requirements.md" ]
    [[ "$output" == *"WARNING"* ]]
}
