#!/usr/bin/env bats
# tests/unit/agate-md-field-get.bats — MD 字段提取共享工具单元测试
# T001 v2.0 流 A（P2-design.md §3.1.2）：双读改造——frontmatter 优先 + 无 key 正则回退。
# 6 个既有用例改写为 BDD-1/3/9/10 覆盖（详见 P3-test-cases.md）。
# +4（TAG0002）：MDF.7-10 覆盖 change_type（BDD-1）与 regression_pass（BDD-4）新 op。
load ../helpers/load.bash

@test "MDF.1 BDD-1: risk_level 从 frontmatter 块读取（字段级 presence 优先）" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/md-XXXXXX")
    printf -- '---\nagent: test\nrisk_level: high\n---\nbody\n' > "$dir/P1.md"
    run bash -c "FILE='$dir/P1.md' python3 '$AGATE_SCRIPTS/agate-md-field-get.py' risk_level"
    [ "$status" -eq 0 ]; [[ "$output" == "high" ]]
}

@test "MDF.2 BDD-9: 旧格式（frontmatter 无 risk_level，只在正文）仍通过正则回退正确读取" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/md-XXXXXX")
    printf -- '---\nagent: test\n---\nrisk_level: medium\n' > "$dir/P1.md"
    run bash -c "FILE='$dir/P1.md' python3 '$AGATE_SCRIPTS/agate-md-field-get.py' risk_level"
    [ "$status" -eq 0 ]; [[ "$output" == "medium" ]]
}

@test "MDF.3 BDD-10: frontmatter 带引号字符串值优先于正文同名字段（证明非文本首现巧合、而是 dict 优先）" {
    # 正文（body）声明 risk_level: low（现有正则 risk_level:\s*(low|medium|high) 可直接匹配）；
    # frontmatter 声明 risk_level: "high"（带引号）——旧版纯正则对带引号值不匹配，
    # 若仍走正则会误取正文的 low；新逻辑须经 yaml.safe_load 解析 frontmatter dict 取得 "high"。
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/md-XXXXXX")
    printf -- '---\nagent: test\nrisk_level: "high"\n---\nrisk_level: low\n' > "$dir/P1.md"
    run bash -c "FILE='$dir/P1.md' python3 '$AGATE_SCRIPTS/agate-md-field-get.py' risk_level"
    [ "$status" -eq 0 ]; [[ "$output" == "high" ]]
}

@test "MDF.4 BDD-3: phases 在 frontmatter 内以块式列表（每行 - Pn）声明 → 解析为空格连接列表" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/md-XXXXXX")
    printf -- '---\nagent: test\nphases:\n  - P1\n  - P2\n---\nbody\n' > "$dir/P1.md"
    run bash -c "FILE='$dir/P1.md' python3 '$AGATE_SCRIPTS/agate-md-field-get.py' phases"
    [ "$status" -eq 0 ]; [[ "$output" == "P1 P2" ]]
}

@test "MDF.5 BDD-1: 新增 op candidate_count 从 P2 frontmatter 读取（int → str）" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/md-XXXXXX")
    printf -- '---\nagent: test\ncandidate_count: 2\n---\nbody\n' > "$dir/P2.md"
    run bash -c "FILE='$dir/P2.md' python3 '$AGATE_SCRIPTS/agate-md-field-get.py' candidate_count"
    [ "$status" -eq 0 ]; [[ "$output" == "2" ]]
}

@test "MDF.6 BDD-1: 新增 op packages 从 frontmatter 列表读取（空格连接）" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/md-XXXXXX")
    printf -- '---\nagent: test\npackages: [agate, other-pkg]\n---\nbody\n' > "$dir/P2.md"
    run bash -c "FILE='$dir/P2.md' python3 '$AGATE_SCRIPTS/agate-md-field-get.py' packages"
    [ "$status" -eq 0 ]; [[ "$output" == "agate other-pkg" ]]
}

# ========== TAG0002 refactor 一等任务：change_type / regression_pass 新 op（BDD-1/BDD-4） ==========

@test "MDF.7 test_bdd_1_change_type_frontmatter: P1 frontmatter 声明 change_type 读取为字符串" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/md-XXXXXX")
    printf -- '---\nagent: test\nrisk_level: high\nchange_type: refactor\n---\nbody\n' > "$dir/P1.md"
    run bash -c "FILE='$dir/P1.md' python3 '$AGATE_SCRIPTS/agate-md-field-get.py' change_type"
    [ "$status" -eq 0 ]; [[ "$output" == "refactor" ]]
}

@test "MDF.8 test_bdd_1_change_type_body_fallback: frontmatter 无 change_type 时正文正则回退（与 risk_level 同模式）" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/md-XXXXXX")
    printf -- '---\nagent: test\n---\nchange_type: refactor\n' > "$dir/P1.md"
    run bash -c "FILE='$dir/P1.md' python3 '$AGATE_SCRIPTS/agate-md-field-get.py' change_type"
    [ "$status" -eq 0 ]; [[ "$output" == "refactor" ]]
}

@test "MDF.9 test_bdd_4_regression_pass_frontmatter: P6 frontmatter 声明 regression_pass: true 读取为 true" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/md-XXXXXX")
    printf -- '---\nagent: test\npass: 1\nfail: 0\nui_affected: false\nregression_pass: true\n---\nbody\n' > "$dir/P6.md"
    run bash -c "FILE='$dir/P6.md' python3 '$AGATE_SCRIPTS/agate-md-field-get.py' regression_pass"
    [ "$status" -eq 0 ]; [[ "$output" == "true" ]]
}

@test "MDF.10 test_bdd_4_regression_pass_no_fallback: P6 frontmatter 无 regression_pass 时输出空（不做正文回退，防正文伪造陷阱）" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/md-XXXXXX")
    # 正文写 regression_pass: false 陷阱行——若错误回退会读到 false；正确行为是空串（无回退语义，调用方判定）
    printf -- '---\nagent: test\npass: 1\nfail: 0\nui_affected: false\n---\nregression_pass: false\n' > "$dir/P6.md"
    run bash -c "FILE='$dir/P6.md' python3 '$AGATE_SCRIPTS/agate-md-field-get.py' regression_pass"
    [ "$status" -eq 0 ]; [[ "$output" == "" ]]
}