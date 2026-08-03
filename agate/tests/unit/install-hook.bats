#!/usr/bin/env bats
# tests/unit/install-hook.bats — install-hook.sh .gitignore 检测

load ../helpers/load.bash

@test "install-hook: .gitignore 忽略 .state.yaml → WARNING 提醒" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-ig1")
    echo ".state.yaml" > "$repo/.gitignore"
    run bash -c "cd '$repo' && AGATE_ROOT='$AGATE_ROOT' bash '$AGATE_SCRIPTS/install-hook.sh' '$AGATE_ROOT'" 2>&1
    [[ "$output" == *".state.yaml"* ]]
    [[ "$output" == *"忽略"* ]]
}

@test "install-hook: 无 .gitignore → 无 WARNING" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-ig2")
    run bash -c "cd '$repo' && AGATE_ROOT='$AGATE_ROOT' bash '$AGATE_SCRIPTS/install-hook.sh' '$AGATE_ROOT'" 2>&1
    [[ "$output" != *".state.yaml"*"忽略"* ]]
}
