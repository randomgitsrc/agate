#!/usr/bin/env bats
# tests/unit/dispatch-context-warning.bats — B3 dispatch-context 缺失 WARNING

load ../helpers/load.bash

@test "B3-warning: 产出暂存缺 dispatch-context → WARNING" {
    local repo
    repo=$(mktemp -d "$BATS_TEST_TMPDIR/repo-XXXXXX")
    git init "$repo" > /dev/null 2>&1
    git -C "$repo" config user.email "test@test.local"
    git -C "$repo" config user.name "Test"
    git -C "$repo" config commit.gpgsign false

    echo "init" > "$repo/README.md"
    git -C "$repo" add README.md
    git -C "$repo" commit -m "init" > /dev/null 2>&1

    mkdir -p "$repo/docs/tasks/T001"
    echo "content" > "$repo/docs/tasks/T001/P2-design.md"
    cat > "$repo/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P2
status: active
retries: {}
EOF
    git -C "$repo" add docs/tasks/T001/

    AGATE_ROOT_FAKE=$(mktemp -d "$BATS_TEST_TMPDIR/agate-fake-XXXXXX")
    mkdir -p "$AGATE_ROOT_FAKE/scripts"
    cp "$AGATE_ROOT/scripts/gate-result.sh" "$AGATE_ROOT_FAKE/scripts/"
    cp "$AGATE_ROOT/scripts/check-state-yaml.sh" "$AGATE_ROOT_FAKE/scripts/"
    cp "$AGATE_ROOT/scripts/check-state-transition.sh" "$AGATE_ROOT_FAKE/scripts/"
    cp "$AGATE_ROOT/scripts/check-gate.sh" "$AGATE_ROOT_FAKE/scripts/"
    cp "$AGATE_ROOT/scripts/check-p6-provenance.sh" "$AGATE_ROOT_FAKE/scripts/"
    cp "$AGATE_ROOT/scripts/check-pruning.sh" "$AGATE_ROOT_FAKE/scripts/"
    cp "$AGATE_ROOT/scripts/check-scope-resolved.sh" "$AGATE_ROOT_FAKE/scripts/"
    cp "$AGATE_ROOT/scripts/check-changelog.sh" "$AGATE_ROOT_FAKE/scripts/"
    cp "$AGATE_ROOT/scripts/check-retrospective.sh" "$AGATE_ROOT_FAKE/scripts/"
    cp "$AGATE_ROOT/scripts/check-p6-evidence.sh" "$AGATE_ROOT_FAKE/scripts/"
    cp "$AGATE_ROOT/scripts/pre-commit-gate.sh" "$AGATE_ROOT_FAKE/scripts/"
    cp -r "$AGATE_ROOT/assets" "$AGATE_ROOT_FAKE/"
    # Do NOT copy agate-next-card.sh — simulates it being unavailable

    run bash -c "cd '$repo' && AGATE_ROOT='$AGATE_ROOT_FAKE' bash '$AGATE_ROOT_FAKE/scripts/pre-commit-gate.sh'" 2>&1 || true
    [[ "$output" == *"dispatch-context"* ]]
}
