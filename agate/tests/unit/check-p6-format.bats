load ../helpers/load.bash

@test "F1 check-p6-format.sh --check: clean file → exit 0" {
    TASK_DIR=$(create_task_dir)
    cat > "$TASK_DIR/P6-acceptance.md" <<'EOF'
- PASS B01: verified (evidence/log.json)
- PASS B02: confirmed (evidence/result.json)
EOF
    run bash "$AGATE_ROOT/scripts/check-p6-format.sh" --check "$TASK_DIR/P6-acceptance.md"
    [ "$status" -eq 0 ]
}

@test "F2 check-p6-format.sh --check: lowercase pass → exit 1" {
    TASK_DIR=$(create_task_dir)
    cat > "$TASK_DIR/P6-acceptance.md" <<'EOF'
- pass B01: verified (evidence/log.json)
EOF
    run bash "$AGATE_ROOT/scripts/check-p6-format.sh" --check "$TASK_DIR/P6-acceptance.md"
    [ "$status" -eq 1 ]
}

@test "F3 check-p6-format.sh --fix: lowercase pass → auto-fix → exit 0" {
    TASK_DIR=$(create_task_dir)
    cat > "$TASK_DIR/P6-acceptance.md" <<'EOF'
- pass B01: verified (evidence/log.json)
EOF
    run bash "$AGATE_ROOT/scripts/check-p6-format.sh" --fix "$TASK_DIR/P6-acceptance.md"
    [ "$status" -eq 0 ]
    grep -q '^\- PASS B01' "$TASK_DIR/P6-acceptance.md"
}

@test "F4 check-p6-format.sh --fix: leading whitespace on PASS line → auto-fix" {
    TASK_DIR=$(create_task_dir)
    cat > "$TASK_DIR/P6-acceptance.md" <<'EOF'
  - PASS B01: verified (evidence/log.json)
EOF
    run bash "$AGATE_ROOT/scripts/check-p6-format.sh" --fix "$TASK_DIR/P6-acceptance.md"
    [ "$status" -eq 0 ]
    grep -q '^\- PASS B01' "$TASK_DIR/P6-acceptance.md"
}

@test "F5 check-p6-format.sh --check: no P6 file → exit 0" {
    TASK_DIR=$(create_task_dir)
    run bash "$AGATE_ROOT/scripts/check-p6-format.sh" --check "$TASK_DIR/P6-acceptance.md"
    [ "$status" -eq 0 ]
}

@test "F6 check-p6-format.sh --fix: bare path without brackets NOT fixed (semantic)" {
    TASK_DIR=$(create_task_dir)
    cat > "$TASK_DIR/P6-acceptance.md" <<'EOF'
- PASS B01: verified evidence/log.json
EOF
    run bash "$AGATE_ROOT/scripts/check-p6-format.sh" --fix "$TASK_DIR/P6-acceptance.md"
    [ "$status" -eq 0 ]
    grep -q 'evidence/log.json' "$TASK_DIR/P6-acceptance.md"
    ! grep -q '(evidence/log.json)' "$TASK_DIR/P6-acceptance.md"
}

@test "F7 check-p6-format.sh --fix: lowercase fail: (colon, no space) → auto-fix to FAIL:" {
    TASK_DIR=$(create_task_dir)
    cat > "$TASK_DIR/P6-acceptance.md" <<'EOF'
- fail: BDD-2 broken
EOF
    run bash "$AGATE_ROOT/scripts/check-p6-format.sh" --fix "$TASK_DIR/P6-acceptance.md"
    [ "$status" -eq 0 ]
    grep -q '^\- FAIL:' "$TASK_DIR/P6-acceptance.md"
}

@test "F8 check-p6-format.sh --check: lowercase fail: → exit 1" {
    TASK_DIR=$(create_task_dir)
    cat > "$TASK_DIR/P6-acceptance.md" <<'EOF'
- fail: BDD-2 broken
EOF
    run bash "$AGATE_ROOT/scripts/check-p6-format.sh" --check "$TASK_DIR/P6-acceptance.md"
    [ "$status" -eq 1 ]
}

@test "F9 check-p6-format.sh --fix: lowercase fail with space → auto-fix" {
    TASK_DIR=$(create_task_dir)
    cat > "$TASK_DIR/P6-acceptance.md" <<'EOF'
- fail B03: timeout
EOF
    run bash "$AGATE_ROOT/scripts/check-p6-format.sh" --fix "$TASK_DIR/P6-acceptance.md"
    [ "$status" -eq 0 ]
    grep -q '^\- FAIL B03' "$TASK_DIR/P6-acceptance.md"
}

@test "F10 check-p6-format.sh --fix: 'failure' NOT matched (word boundary)" {
    TASK_DIR=$(create_task_dir)
    cat > "$TASK_DIR/P6-acceptance.md" <<'EOF'
- failure mode detected in production
EOF
    run bash "$AGATE_ROOT/scripts/check-p6-format.sh" --fix "$TASK_DIR/P6-acceptance.md"
    [ "$status" -eq 0 ]
    grep -q 'failure mode' "$TASK_DIR/P6-acceptance.md"
}
