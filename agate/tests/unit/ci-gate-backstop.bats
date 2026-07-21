#!/usr/bin/env bats
# tests/unit/ci-gate-backstop.bats — ci-gate-backstop.py 平台探测

load ../helpers/load.bash

@test "detect_ci_platform: Gitea 优先于 GitHub 被识别" {
    local repo
    repo=$(git_init)
    cd "$repo"
    export GITEA_ACTIONS=true
    export GITHUB_ACTIONS=true
    run bash -c "python3 '$AGATE_SCRIPTS/ci-gate-backstop.py' 2>/dev/null || true"
    [[ "$output" == *"gitea"* ]]
}

@test "detect_ci_platform: GitLab CI 正确识别" {
    local repo
    repo=$(git_init)
    cd "$repo"
    export GITLAB_CI=true
    unset GITEA_ACTIONS GITHUB_ACTIONS
    run bash -c "python3 '$AGATE_SCRIPTS/ci-gate-backstop.py' 2>/dev/null || true"
    [[ "$output" == *"gitlab"* ]]
}

@test "detect_ci_platform: 无可识别平台时 SKIP 而非误判" {
    local repo
    repo=$(git_init)
    cd "$repo"
    unset GITEA_ACTIONS GITLAB_CI GITHUB_ACTIONS
    run bash -c "python3 '$AGATE_SCRIPTS/ci-gate-backstop.py' 2>/dev/null || true"
    [[ "$output" == *"SKIP"* || "$output" == *"None"* ]]
}
