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

@test "install-hook: pre-push 是软链指向 pre-push-gate.sh" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-pp1")
    run bash -c "cd '$repo' && AGATE_ROOT='$AGATE_ROOT' bash '$AGATE_SCRIPTS/install-hook.sh' '$AGATE_ROOT'" 2>&1
    [[ -L "$repo/.git/hooks/pre-push" ]]
    [[ "$(readlink "$repo/.git/hooks/pre-push")" == "$AGATE_SCRIPTS/pre-push-gate.sh" ]]
}

@test "install-hook: 已有非软链 pre-push → 备份并替换为软链" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-pp2")
    local hook="$repo/.git/hooks/pre-push"
    mkdir -p "$(dirname "$hook")"
    printf '#!/usr/bin/env bash\nexit 0\n' > "$hook"
    run bash -c "cd '$repo' && AGATE_ROOT='$AGATE_ROOT' bash '$AGATE_SCRIPTS/install-hook.sh' '$AGATE_ROOT'" 2>&1
    [[ "$output" == *"已备份现有 pre-push hook"* ]]
    [[ -L "$hook" ]]
    [[ "$(readlink "$hook")" == "$AGATE_SCRIPTS/pre-push-gate.sh" ]]
    [[ -n "$(ls "$(dirname "$hook")"/pre-push.bak.* 2>/dev/null | head -1)" ]]
}
