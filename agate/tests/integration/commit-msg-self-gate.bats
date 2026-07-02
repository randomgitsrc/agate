#!/usr/bin/env bats
# tests/integration/commit-msg-self-gate.bats — commit-msg-self-gate.sh 测试
load ../helpers/load.bash

setup() {
    REPO=$(git_init)
    cd "$REPO"
    echo "init" > README.md
    git add README.md
    git commit -qm "init"
    HOOK_PATH="$REPO/.git/hooks/commit-msg"
    cp "$AGATE_ROOT/scripts/commit-msg-self-gate.sh" "$HOOK_PATH"
    chmod +x "$HOOK_PATH"
    mkdir -p "$REPO/agate/scripts" "$REPO/agate/assets"
    cp "$AGATE_ROOT/scripts/commit-msg-self-gate.sh" "$REPO/agate/scripts/"
}

@test "CSG.1 非触发文件改动 → 无 WARNING" {
    echo "change" > "$REPO/README.md"
    git add README.md
    run git -C "$REPO" commit -m "update readme"
    [ "$status" -eq 0 ]
    [[ "$output" != *"self-gate-review"* ]]
}

@test "CSG.2 触发文件改动 + 无 review 路径 → WARNING" {
    echo "# change" > "$REPO/SELF-GATE.md"
    git add SELF-GATE.md
    run git -C "$REPO" commit -m "update self-gate"
    [ "$status" -eq 0 ]
    [[ "$output" == *"self-gate-review"* ]]
}

@test "CSG.3 触发文件改动 + 有 review 路径 → 无 WARNING" {
    echo "# change" > "$REPO/SELF-GATE.md"
    git add SELF-GATE.md
    run git -C "$REPO" commit -m "update self-gate" -m "self-gate-review: docs/reviews/agate-alignment-review-2026-07-02.md"
    [ "$status" -eq 0 ]
    [[ "$output" != *"self-gate-review"* ]]
}

@test "CSG.4 触发文件改动 + self-gate-skip → 无 WARNING" {
    echo "# change" > "$REPO/SELF-GATE.md"
    git add SELF-GATE.md
    run git -C "$REPO" commit -m "fix typo" -m "self-gate-skip: typo"
    [ "$status" -eq 0 ]
    [[ "$output" != *"self-gate-review"* ]]
}

@test "CSG.5 agate/scripts/*.sh 改动触发" {
    echo "# change" > "$REPO/agate/scripts/check-gate.sh"
    git add agate/scripts/check-gate.sh
    run git -C "$REPO" commit -m "update gate script"
    [ "$status" -eq 0 ]
    [[ "$output" == *"self-gate-review"* ]]
}

@test "CSG.6 agate/*.md 改动触发" {
    echo "# change" > "$REPO/agate/WORKFLOW.md"
    git add agate/WORKFLOW.md
    run git -C "$REPO" commit -m "update workflow"
    [ "$status" -eq 0 ]
    [[ "$output" == *"self-gate-review"* ]]
}
