#!/usr/bin/env bats
# tests/unit/ci-gate-backstop.bats — ci-gate-backstop.py 平台探测 + P3 兜底
# TAG0002 [SCOPE+]: 新增 change_type=refactor 任务跳过 check-tdd-red 用例（BDD-7/8）

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

# ========== P3 兜底测试 ==========

setup_git_repo_p3() {
    local repo="$1"
    git_init "$repo"
    mkdir -p "$repo/agate-workspace/tasks/T001"
    # 根 .state.yaml（ci-gate-backstop.py 读根目录的）
    cat > "$repo/.state.yaml" <<'EOF'
task_id: T001
phase: P3
status: active
retries: {}
EOF
    echo '## P3 test cases' > "$repo/agate-workspace/tasks/T001/P3-test-cases.md"
    git -C "$repo" add -A
    git -C "$repo" commit -qm "p3"
}

@test "backstop P3: 真红灯（exit 0）→ PASS" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-p3-ok")
    setup_git_repo_p3 "$repo"
    cd "$repo"
    export GITHUB_ACTIONS=true
    local mock="$BATS_TEST_TMPDIR/mock-tdd-ok"
    echo '#!/bin/bash' > "$mock"
    echo 'exit 0' >> "$mock"
    chmod +x "$mock"
    export AGATE_TDD_RED_SCRIPT="$mock"
    run bash -c "python3 '$AGATE_SCRIPTS/ci-gate-backstop.py' 2>&1 || true"
    [[ "$output" == *"真红灯"* ]]
}

@test "backstop P3: 绿灯（exit 2）→ FAIL" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-p3-green")
    setup_git_repo_p3 "$repo"
    cd "$repo"
    export GITHUB_ACTIONS=true
    local mock="$BATS_TEST_TMPDIR/mock-tdd-green"
    echo '#!/bin/bash' > "$mock"
    echo 'exit 2' >> "$mock"
    chmod +x "$mock"
    export AGATE_TDD_RED_SCRIPT="$mock"
    run bash -c "python3 '$AGATE_SCRIPTS/ci-gate-backstop.py' 2>&1 || true"
    [[ "$output" == *"FAIL"* ]]
    [[ "$output" == *"绿灯"* ]]
}

@test "backstop P3: 假红灯（exit 1）→ FAIL" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-p3-afake")
    setup_git_repo_p3 "$repo"
    cd "$repo"
    export GITHUB_ACTIONS=true
    local mock="$BATS_TEST_TMPDIR/mock-tdd-fake"
    echo '#!/bin/bash' > "$mock"
    echo 'exit 1' >> "$mock"
    chmod +x "$mock"
    export AGATE_TDD_RED_SCRIPT="$mock"
    run bash -c "python3 '$AGATE_SCRIPTS/ci-gate-backstop.py' 2>&1 || true"
    [[ "$output" == *"FAIL"* ]]
    [[ "$output" == *"假红灯"* ]]
}

@test "backstop P3: 无运行器（exit 3）→ WARN 不 FAIL" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-p3-norunner")
    setup_git_repo_p3 "$repo"
    cd "$repo"
    export GITHUB_ACTIONS=true
    local mock="$BATS_TEST_TMPDIR/mock-tdd-norunner"
    echo '#!/bin/bash' > "$mock"
    echo 'exit 3' >> "$mock"
    chmod +x "$mock"
    export AGATE_TDD_RED_SCRIPT="$mock"
    run bash -c "python3 '$AGATE_SCRIPTS/ci-gate-backstop.py' 2>&1 || true"
    [[ "$output" == *"WARN"* ]]
    [[ "$output" != *"FAIL"* ]]
}

@test "backstop P3: 无 .gate-result.json（--no-verify）时仍执行 check-tdd-red.sh" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-p3-noverify")
    setup_git_repo_p3 "$repo"
    cd "$repo"
    export GITHUB_ACTIONS=true
    local mock="$BATS_TEST_TMPDIR/mock-tdd-ok2"
    echo '#!/bin/bash' > "$mock"
    echo 'exit 0' >> "$mock"
    chmod +x "$mock"
    export AGATE_TDD_RED_SCRIPT="$mock"
    # 不创建 .gate-result.json（模拟 --no-verify 场景）
    run bash -c "python3 '$AGATE_SCRIPTS/ci-gate-backstop.py' 2>&1 || true"
    [[ "$output" == *"真红灯"* ]]
}

# ========== TAG0002 [SCOPE+]: P3 分支 refactor 感知（BDD-7/8，ci-gate-backstop 不误杀 refactor 任务） ==========

@test "backstop P3: change_type=refactor 任务跳过 check-tdd-red（SKIP 而非 FAIL，即使 mock exit 2 绿灯）" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-p3-refactor")
    setup_git_repo_p3 "$repo"
    # refactor 任务：P1-requirements.md 声明 change_type: refactor（TDD 红灯不适用）
    cat > "$repo/agate-workspace/tasks/T001/P1-requirements.md" <<'EOF'
---
agent: test
risk_level: medium
change_type: refactor
---
#### BDD-1: 关键路径行为不变
- Given 重构后的协议状态
- When 执行关键路径
- Then 行为与重构前一致
EOF
    git -C "$repo" add -A
    git -C "$repo" commit -qm "p3 refactor"
    cd "$repo"
    export GITHUB_ACTIONS=true
    # mock 返回 exit 2（绿灯）——若 backstop 不感知 refactor 会把合法任务误判 FAIL
    local mock="$BATS_TEST_TMPDIR/mock-tdd-refactor"
    echo '#!/bin/bash' > "$mock"
    echo 'exit 2' >> "$mock"
    chmod +x "$mock"
    export AGATE_TDD_RED_SCRIPT="$mock"
    run bash -c "python3 '$AGATE_SCRIPTS/ci-gate-backstop.py' 2>&1 || true"
    [[ "$output" == *"SKIP"* ]]
    [[ "$output" == *"refactor"* ]]
    [[ "$output" != *"FAIL"* ]]
}
