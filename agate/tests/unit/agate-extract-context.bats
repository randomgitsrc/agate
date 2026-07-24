#!/usr/bin/env bats

load ../helpers/load.bash

setup() {
    TEST_TASK_DIR="$(mktemp -d "${BATS_TEST_TMPDIR}/task-XXXXXX")"
}

teardown() {
    rm -rf "$TEST_TASK_DIR" 2>/dev/null || true
}

@test "EC.1: rejects missing arguments" {
    run bash "$AGATE_ROOT/scripts/agate-extract-context.sh"
    [ "$status" -eq 1 ]
}

@test "EC.2: rejects invalid phase" {
    run bash "$AGATE_ROOT/scripts/agate-extract-context.sh" P9 "$TEST_TASK_DIR"
    [ "$status" -eq 2 ]
}

@test "EC.3: rejects nonexistent task dir" {
    run bash "$AGATE_ROOT/scripts/agate-extract-context.sh" P1 "/nonexistent"
    [ "$status" -eq 2 ]
}

@test "EC.4: P1 extracts P0-brief fields" {
    cat > "$TEST_TASK_DIR/P0-brief.md" <<'EOF'
---
task: fix login timeout
known_risks: [session_expiry]
---
EOF
    run bash "$AGATE_ROOT/scripts/agate-extract-context.sh" P1 "$TEST_TASK_DIR"
    [ "$status" -eq 0 ]
    [[ "$output" == *"task: fix login timeout"* ]]
}

@test "EC.5: P2 extracts P1 domains and BDD count" {
    cat > "$TEST_TASK_DIR/P1-requirements.md" <<'EOF'
---
domains: [backend]
risk_level: high
---
#### BDD-1: user can log in
#### BDD-2: session expires after timeout
EOF
    run bash "$AGATE_ROOT/scripts/agate-extract-context.sh" P2 "$TEST_TASK_DIR"
    [ "$status" -eq 0 ]
    [[ "$output" == *"domains: [backend]"* ]]
    [[ "$output" == *"risk_level: high"* ]]
    [[ "$output" == *"BDD 条件数: 2"* ]]
}

@test "EC.6: P3 extracts P2 structured fields" {
    cat > "$TEST_TASK_DIR/P2-design.md" <<'EOF'
packages: [pkg-a, pkg-b]
domains: [backend, frontend]
ui_affected: true
gate_commands:
  P5: "pytest -q"
EOF
    run bash "$AGATE_ROOT/scripts/agate-extract-context.sh" P3 "$TEST_TASK_DIR"
    [ "$status" -eq 0 ]
    [[ "$output" == *"packages: [pkg-a, pkg-b]"* ]]
    [[ "$output" == *"ui_affected: true"* ]]
}

@test "EC.7: P6 extracts BDD count and failed reference" {
    cat > "$TEST_TASK_DIR/P1-requirements.md" <<'EOF'
#### BDD-1: feature works
EOF
    mkdir -p "$TEST_TASK_DIR/P5-test-results"
    echo "failed: 1" > "$TEST_TASK_DIR/P5-test-results/unit.md"
    run bash "$AGATE_ROOT/scripts/agate-extract-context.sh" P6 "$TEST_TASK_DIR"
    [ "$status" -eq 0 ]
    [[ "$output" == *"BDD 条件数: 1"* ]]
    [[ "$output" == *"仅供参考"* ]]
}

@test "EC.8: P7 extracts PASS/FAIL counts" {
    cat > "$TEST_TASK_DIR/P2-design.md" <<'EOF'
packages: [pkg-a]
EOF
    cat > "$TEST_TASK_DIR/P6-acceptance.md" <<'EOF'
- PASS BDD-1: works (evidence.log)
- FAIL BDD-2: broken (evidence2.log)
EOF
    run bash "$AGATE_ROOT/scripts/agate-extract-context.sh" P7 "$TEST_TASK_DIR"
    [ "$status" -eq 0 ]
    [[ "$output" == *"1 PASS"* ]]
    [[ "$output" == *"1 FAIL"* ]]
}

@test "EC.9: --write mode appends to dispatch-context file" {
    cat > "$TEST_TASK_DIR/P0-brief.md" <<'EOF'
---
task: test task
---
EOF
    cat > "$TEST_TASK_DIR/P1-dispatch-context-analyst.md" <<'EOF'
### 上游关联
(none)
EOF
    run bash "$AGATE_ROOT/scripts/agate-extract-context.sh" P1 "$TEST_TASK_DIR" --write
    [ "$status" -eq 0 ]
    [[ "$output" == *"已追加到"* ]]
    run cat "$TEST_TASK_DIR/P1-dispatch-context-analyst.md"
    [[ "$output" == *"task: test task"* ]]
}
