#!/usr/bin/env bats
# tests/unit/commit-msg-self-gate.bats — commit-msg-self-gate.sh 正则测试

load ../helpers/load.bash

setup() {
    local repo
    repo=$(git_init)
    cd "$repo"
    mkdir -p agate/scripts
}

@test "commit-msg-self-gate: .sh 文件触发 self-gate WARNING" {
    echo "test" > agate/scripts/test-file.sh
    git add agate/scripts/test-file.sh

    echo "feat: test" > "$BATS_TEST_TMPDIR/commit-msg"
    run bash "$AGATE_SCRIPTS/commit-msg-self-gate.sh" "$BATS_TEST_TMPDIR/commit-msg"
    [[ "$output" == *"self-gate"* ]]
}

@test "commit-msg-self-gate: .py 文件触发 self-gate WARNING" {
    echo "test" > agate/scripts/test-file.py
    git add agate/scripts/test-file.py

    echo "feat: test" > "$BATS_TEST_TMPDIR/commit-msg"
    run bash "$AGATE_SCRIPTS/commit-msg-self-gate.sh" "$BATS_TEST_TMPDIR/commit-msg"
    [[ "$output" == *"self-gate"* ]]
}

@test "commit-msg-self-gate: 非 agate .py 文件不触发" {
    mkdir -p other
    echo "test" > other/test-file.py
    git add other/test-file.py

    echo "feat: test" > "$BATS_TEST_TMPDIR/commit-msg"
    run bash "$AGATE_SCRIPTS/commit-msg-self-gate.sh" "$BATS_TEST_TMPDIR/commit-msg"
    [ "$status" -eq 0 ]
    [ -z "$output" ]
}

@test "commit-msg-self-gate: self-gate-review: 路径消除 WARNING" {
    echo "test" > agate/scripts/test-file.sh
    git add agate/scripts/test-file.sh

    printf 'feat: test\nself-gate-review: docs/reviews/test.md' > "$BATS_TEST_TMPDIR/commit-msg"
    run bash "$AGATE_SCRIPTS/commit-msg-self-gate.sh" "$BATS_TEST_TMPDIR/commit-msg"
    [ "$status" -eq 0 ]
}
