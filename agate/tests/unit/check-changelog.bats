#!/usr/bin/env bats
# tests/unit/check-changelog.bats — 5 用例覆盖 check-changelog.sh
# 计划：5.8 / 实际 5 行 / 与附录 A 一致

load ../helpers/load.bash

@test "CL.1 check-changelog.sh 无 CHANGELOG 文件 期望 exit 0" {
    local repo
    repo=$(git_init)
    cd "$repo"
    run bash "$AGATE_SCRIPTS/check-changelog.sh" T001
    [ "$status" -eq 0 ]
}

@test "CL.2 check-changelog.sh CHANGELOG 无 [Unreleased] 区域 期望 exit 1" {
    local repo
    repo=$(git_init)
    cd "$repo"
    cat > CHANGELOG.md <<'EOF'
## [v0.5.0] - 2026-01-01
- 已发布
EOF
    run bash "$AGATE_SCRIPTS/check-changelog.sh" T001
    [ "$status" -eq 1 ]
    [[ "$output" == *"无 [Unreleased]"* ]]
}

@test "CL.3 check-changelog.sh [Unreleased] 无 task_id 期望 exit 1" {
    local repo
    repo=$(git_init)
    cd "$repo"
    cat > CHANGELOG.md <<'EOF'
## [Unreleased]
- 其他内容
EOF
    run bash "$AGATE_SCRIPTS/check-changelog.sh" T001
    [ "$status" -eq 1 ]
    [[ "$output" == *"未找到 T001"* ]]
}

@test "CL.4 check-changelog.sh [Unreleased] 含 task_id 期望 exit 0" {
    local repo
    repo=$(git_init)
    cd "$repo"
    cat > CHANGELOG.md <<'EOF'
## [Unreleased]
- T001 任务完成
EOF
    run bash "$AGATE_SCRIPTS/check-changelog.sh" T001
    [ "$status" -eq 0 ]
}

@test "CL.5 check-changelog.sh task_id 在历史版本 期望 exit 1" {
    local repo
    repo=$(git_init)
    cd "$repo"
    cat > CHANGELOG.md <<'EOF'
## [v0.5.0]
- T001 旧版本

## [Unreleased]
- 新内容
EOF
    run bash "$AGATE_SCRIPTS/check-changelog.sh" T001
    # task_id 在历史版本不算在 [Unreleased] → exit 1
    [ "$status" -eq 1 ]
}
