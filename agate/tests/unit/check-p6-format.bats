load ../helpers/load.bash

@test "F1 check-p6-format.sh --check: clean file → exit 0" {
    TASK_DIR=$(create_task_dir)
    cat > "$TASK_DIR/P6-acceptance.md" <<'EOF'
- PASS BDD-1: verified (evidence/log.json)
- PASS BDD-2: confirmed (evidence/result.json)
EOF
    run bash "$AGATE_ROOT/scripts/check-p6-format.sh" --check "$TASK_DIR/P6-acceptance.md"
    [ "$status" -eq 0 ]
}

@test "F2 check-p6-format.sh --check: lowercase pass → exit 1" {
    TASK_DIR=$(create_task_dir)
    cat > "$TASK_DIR/P6-acceptance.md" <<'EOF'
- pass BDD-1: verified (evidence/log.json)
EOF
    run bash "$AGATE_ROOT/scripts/check-p6-format.sh" --check "$TASK_DIR/P6-acceptance.md"
    [ "$status" -eq 1 ]
}

@test "F3 check-p6-format.sh --fix: lowercase pass → auto-fix → exit 0" {
    TASK_DIR=$(create_task_dir)
    cat > "$TASK_DIR/P6-acceptance.md" <<'EOF'
- pass BDD-1: verified (evidence/log.json)
EOF
    run bash "$AGATE_ROOT/scripts/check-p6-format.sh" --fix "$TASK_DIR/P6-acceptance.md"
    [ "$status" -eq 0 ]
    grep -q '^\- PASS BDD-1' "$TASK_DIR/P6-acceptance.md"
}

@test "F5 check-p6-format.sh --check: no P6 file → exit 0" {
    TASK_DIR=$(create_task_dir)
    run bash "$AGATE_ROOT/scripts/check-p6-format.sh" --check "$TASK_DIR/P6-acceptance.md"
    [ "$status" -eq 0 ]
}

@test "F_BDD17.1 BDD-17: check-p6-format.sh --check 行首 - PASS|FAIL BDD-NN: 格式被识别为有效逐条结果" {
    # T001 v2.0 流 B：逐条结果行首须为 `- PASS BDD-NN:` 或 `- FAIL BDD-NN:`（带 BDD 编号）
    # 才算有效逐条结果；不带 BDD 编号的行（如纯 `- PASS: 16` 总结行）不算。
    TASK_DIR=$(create_task_dir)
    cat > "$TASK_DIR/P6-acceptance.md" <<'EOF'
- PASS BDD-1: verified (evidence/a.json)
- FAIL BDD-2: broken (evidence/b.json)
EOF
    run bash "$AGATE_ROOT/scripts/check-p6-format.sh" --check "$TASK_DIR/P6-acceptance.md"
    [ "$status" -eq 0 ]
    grep -qE '^- (PASS|FAIL) BDD-[0-9]+:' "$TASK_DIR/P6-acceptance.md"
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
- fail BDD-3: timeout
EOF
    run bash "$AGATE_ROOT/scripts/check-p6-format.sh" --fix "$TASK_DIR/P6-acceptance.md"
    [ "$status" -eq 0 ]
    grep -q '^\- FAIL BDD-3' "$TASK_DIR/P6-acceptance.md"
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

@test "F_BDD18.1 BDD-18: check-gate.sh P6 审计口径不把总结行（- PASS: 16，无 BDD 编号）计入逐条 PASS/FAIL 总数" {
    # T001 v2.0 流 A→B 边界：check-gate.sh 的 P6 逐条计数须只统计行首
    # `- PASS|FAIL BDD-NN:` 的行；总结行（`- PASS: 16` 无 BDD 编号）不应计入，
    # 消除 F11"总结行误判"（旧版 `grep -ciE '^\s*- (PASS|FAIL)'` 会把总结行也计入）。
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1
- PASS: 16
- FAIL: 0
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P6 "$dir"
    # 旧版口径：grep -ciE '^\s*- (PASS|FAIL)' 会命中 3 行（含总结行）→ FAIL 计数被总结行污染。
    # 新版口径：只 1 条真实 PASS BDD-1，无证据目录 → 应因 P6-evidence 缺失而 exit 1，
    # 而不是被总结行的 "- FAIL: 0" 误判出多余 FAIL。
    [ "$status" -eq 1 ]
    [[ "$output" == *"P6-evidence"* ]]
}

@test "F12 check-p6-format.sh --fix: summary line - PASS：34 → **Summary**: PASS: 34" {
    TASK_DIR=$(create_task_dir)
    cat > "$TASK_DIR/P6-acceptance.md" <<'EOF'
- PASS BDD-1: verified (evidence/log.json)
- PASS：34
- FAIL：0
EOF
    run bash "$AGATE_ROOT/scripts/check-p6-format.sh" --fix "$TASK_DIR/P6-acceptance.md"
    [ "$status" -eq 0 ]
    grep -q '^\*\*Summary\*\*: PASS: 34' "$TASK_DIR/P6-acceptance.md"
    grep -q '^\*\*Summary\*\*: FAIL: 0' "$TASK_DIR/P6-acceptance.md"
    ! grep -q '^- PASS：34' "$TASK_DIR/P6-acceptance.md"
}
