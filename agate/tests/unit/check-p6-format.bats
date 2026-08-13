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

@test "F13 check-p6-format.sh --fix: POSIX locale 下全角冒号总结行仍被归一化（locale 回归）" {
    TASK_DIR=$(create_task_dir)
    cat > "$TASK_DIR/P6-acceptance.md" <<'EOF'
- PASS BDD-1: verified (evidence/log.json)
- PASS：34
- FAIL：0
EOF
    run env LC_ALL=POSIX LANG= bash "$AGATE_ROOT/scripts/check-p6-format.sh" --fix "$TASK_DIR/P6-acceptance.md"
    [ "$status" -eq 0 ]
    grep -q '^\*\*Summary\*\*: PASS: 34' "$TASK_DIR/P6-acceptance.md"
    grep -q '^\*\*Summary\*\*: FAIL: 0' "$TASK_DIR/P6-acceptance.md"
    ! grep -q '^- PASS：34' "$TASK_DIR/P6-acceptance.md"
}

@test "F_P6FMFIX.1 check-p6-format.sh --fix: frontmatter 的 pass:/fail: 字段不被正文归一化 sed 误伤，仍为合法 YAML" {
    # P6 回退修复核心复现场景（P6-gate-diagnosis.md BDD-17）：BDD-16 要求的
    # frontmatter pass:/fail: 字段此前会被 --fix 的整文件 sed 误判为正文散文 pass/fail 行，
    # 改写成 **Summary**: PASS: N，导致 frontmatter 变成非法 YAML。
    TASK_DIR=$(create_task_dir)
    cat > "$TASK_DIR/P6-acceptance.md" <<'EOF'
---
phase: P6
task_id: T001
pass: 28
fail: 0
ui_affected: false
---

- PASS BDD-1: xxx (x.log)
- pass BDD-2: yyy (y.log)
EOF
    run bash "$AGATE_ROOT/scripts/check-p6-format.sh" --fix "$TASK_DIR/P6-acceptance.md"
    [ "$status" -eq 0 ]

    # frontmatter 原样保留：pass: 28 / fail: 0 未被改写为 **Summary**: 形式
    grep -q '^pass: 28$' "$TASK_DIR/P6-acceptance.md"
    grep -q '^fail: 0$' "$TASK_DIR/P6-acceptance.md"
    ! grep -q '\*\*Summary\*\*: PASS: 28' "$TASK_DIR/P6-acceptance.md"
    ! grep -q '\*\*Summary\*\*: FAIL: 0' "$TASK_DIR/P6-acceptance.md"

    # frontmatter 依然是合法 YAML，且 pass/fail 数值未变
    run python3 -c "
import yaml
text = open('$TASK_DIR/P6-acceptance.md').read()
assert text.startswith('---\n'), 'frontmatter 头未保留'
end = text.find('\n---', 4)
assert end > 0, '找不到 frontmatter 闭合边界'
data = yaml.safe_load(text[4:end])
assert data['pass'] == 28, data
assert data['fail'] == 0, data
"
    [ "$status" -eq 0 ]

    # 既有 --fix 归一化行为在正文部分依然生效：小写 pass BDD-2 → PASS BDD-2
    grep -q '^- PASS BDD-2' "$TASK_DIR/P6-acceptance.md"
}

@test "F_P6FMFIX.2 check-p6-format.sh --fix: frontmatter 存在时正文总结行仍被归一化为 **Summary** 格式" {
    TASK_DIR=$(create_task_dir)
    cat > "$TASK_DIR/P6-acceptance.md" <<'EOF'
---
phase: P6
task_id: T001
pass: 2
fail: 0
ui_affected: false
---

- PASS BDD-1: verified (evidence/log.json)
- PASS：2
- FAIL：0
EOF
    run bash "$AGATE_ROOT/scripts/check-p6-format.sh" --fix "$TASK_DIR/P6-acceptance.md"
    [ "$status" -eq 0 ]

    # frontmatter 不受影响，依然合法
    run python3 -c "
import yaml
text = open('$TASK_DIR/P6-acceptance.md').read()
end = text.find('\n---', 4)
data = yaml.safe_load(text[4:end])
assert data['pass'] == 2 and data['fail'] == 0, data
"
    [ "$status" -eq 0 ]

    # 正文总结行按既有行为归一化
    grep -q '^\*\*Summary\*\*: PASS: 2' "$TASK_DIR/P6-acceptance.md"
    grep -q '^\*\*Summary\*\*: FAIL: 0' "$TASK_DIR/P6-acceptance.md"
}

@test "F_P6FMFIX.3 check-p6-format.sh --fix: 无 frontmatter 闭合边界的畸形文件回退按正文整体处理（不误判为已切分）" {
    # 首行是 "---" 但全文找不到第二条以 "---" 起始的行 → 语义上等同旧格式（BDD-9），
    # 全文本按正文处理，既有 pass/fail 归一化行为在这种畸形输入下依然对整个文件生效。
    TASK_DIR=$(create_task_dir)
    cat > "$TASK_DIR/P6-acceptance.md" <<'EOF'
---
phase: P6
- pass BDD-1: verified (evidence/log.json)
EOF
    run bash "$AGATE_ROOT/scripts/check-p6-format.sh" --fix "$TASK_DIR/P6-acceptance.md"
    [ "$status" -eq 0 ]
    grep -q '^- PASS BDD-1' "$TASK_DIR/P6-acceptance.md"
}

# ========== TAG0004 M5 全角冒号 locale（BDD-12/13，GNU sed 下为回归守卫） ==========

@test "bdd-12 check-p6-format.sh --fix LC_ALL=C 小写 fail 全角冒号总结行归一化（line 69 路径，M5）" {
    TASK_DIR=$(create_task_dir)
    cat > "$TASK_DIR/P6-acceptance.md" <<'EOF'
- PASS BDD-1: verified (evidence/log.json)
- fail：3
EOF
    run env LC_ALL=POSIX LANG= bash "$AGATE_ROOT/scripts/check-p6-format.sh" --fix "$TASK_DIR/P6-acceptance.md"
    [ "$status" -eq 0 ]
    grep -q '^\*\*Summary\*\*: FAIL: 3' "$TASK_DIR/P6-acceptance.md"
}

@test "bdd-13 check-p6-format.sh --fix+--check LC_ALL=C 半角冒号总结行行为不变（v0.40.3 回归，M5）" {
    TASK_DIR=$(create_task_dir)
    cat > "$TASK_DIR/P6-acceptance.md" <<'EOF'
- PASS BDD-1: verified (evidence/log.json)
- FAIL: 3
EOF
    run env LC_ALL=POSIX LANG= bash "$AGATE_ROOT/scripts/check-p6-format.sh" --fix "$TASK_DIR/P6-acceptance.md"
    [ "$status" -eq 0 ]
    grep -q '^\*\*Summary\*\*: FAIL: 3' "$TASK_DIR/P6-acceptance.md"
    run env LC_ALL=POSIX LANG= bash "$AGATE_ROOT/scripts/check-p6-format.sh" --check "$TASK_DIR/P6-acceptance.md"
    [ "$status" -eq 0 ]
}
