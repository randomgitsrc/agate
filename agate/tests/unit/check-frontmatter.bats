#!/usr/bin/env bats
# tests/unit/check-frontmatter.bats — agate-frontmatter-check.py / check-frontmatter.sh
# T001 v2.0 流 A 新交付物（P2-design.md §3.1.3）：frontmatter schema 校验器。
# 范式仿 agate-state-yaml-check.py / check-state-yaml.sh（见 tests/unit/agate-state-yaml-check.bats）。
#
# 594 配平（P2-design.md §3.1.5 FIND-7）：本文件新增 10 个 @test（CF.1..CF.10），
# 由以下 15 文件内各移减/合并 1 条重复覆盖的既有断言配平（N=10=M，详见 P3-test-cases.md
# §594 配平表）：check-gate.bats(G2.12→G2.27, G6.8→G6.7, G2.23→G2.21, G2.15→G2.14)、
# check-p6-format.bats(F7→F9, F11→F12)、check-p6-provenance.bats(PV.5→PV.5b,
# PROV_MULTI.3→PV.18)、check-scope-resolved.bats(SC.5b→SC.5)、check-retrospective.bats(RT.3→RT.7)。
#
# 覆盖 BDD-2/4/5/6/7/8/12（P1-requirements.md）+ FIND-1（presence 判别契约边界）+
# FIND-5（单行全角冒号块非 dict 硬拦截）。

load ../helpers/load.bash

setup() {
    # TAG0009 BDD-16/17：harness shim——产品脚本内部裸 python3 在"仅 python 可解析"环境解析到真解释器
    local shim
    shim=$(create_python_shim_bin) || return 1
    if [ -n "$shim" ]; then
        export PATH="$shim:$PATH"
    fi
}

# ========== BDD-2: 全角冒号不再导致字段静默缺失（校验失败并报错，可定位） ==========

@test "CF.1 BDD-2: P1 frontmatter risk_level 用全角冒号（risk_level：high）→ 校验失败且报错含 risk_level" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/cf-XXXXXX")
    cat > "$dir/P1-requirements.md" <<'EOF'
---
phase: P1
task_id: T001
agent: analyst
risk_level：high
phases: [P1, P2]
packages: [agate]
domains: [backend]
---
#### BDD-1: test
- Given x
- When y
- Then z
EOF
    run bash -c "FILE='$dir/P1-requirements.md' $PYTHON '$AGATE_SCRIPTS/agate-frontmatter-check.py'"
    [ -n "$output" ]
    [[ "$output" == *"risk_level"* ]]
}

# ========== BDD-4: 缩进错误被校验器拦截（错误信息含字段名或行号） ==========

@test "CF.2 BDD-4: P1 frontmatter coupling_checklist 列表项缩进错误 → 校验失败且报错可定位" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/cf-XXXXXX")
    # coupling_checklist 列表项比父 key 少 3 空格缩进 → YAML 解析结构错误（v0.6 yaml-indent 类回归）
    printf -- '---\nphase: P1\ntask_id: T001\nagent: analyst\nrisk_level: high\nphases: [P1]\npackages: [agate]\ndomains: [backend]\ncoupling_checklist:\n- api-schema: checked\n   - data-model: checked\n---\n#### BDD-1: test\n- Given x\n- When y\n- Then z\n' > "$dir/P1-requirements.md"
    run bash -c "FILE='$dir/P1-requirements.md' $PYTHON '$AGATE_SCRIPTS/agate-frontmatter-check.py'"
    [ -n "$output" ]
    [[ "$output" == *"coupling_checklist"* || "$output" == *"line"* || "$output" == *"行"* ]]
}

# ========== BDD-5: 枚举字段非法值被类型校验拦截（提示合法值） ==========

@test "CF.3 BDD-5: P1 frontmatter risk_level 枚举外的值（HIGH）→ 校验失败且提示 low/medium/high" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/cf-XXXXXX")
    cat > "$dir/P1-requirements.md" <<'EOF'
---
phase: P1
task_id: T001
agent: analyst
risk_level: HIGH
phases: [P1]
packages: [agate]
domains: [backend]
---
#### BDD-1: test
- Given x
- When y
- Then z
EOF
    run bash -c "FILE='$dir/P1-requirements.md' $PYTHON '$AGATE_SCRIPTS/agate-frontmatter-check.py'"
    [ -n "$output" ]
    [[ "$output" == *"low"* ]]
    [[ "$output" == *"medium"* ]]
    [[ "$output" == *"high"* ]]
}

# ========== BDD-6: 缺必填字段时 gate 拦截（P1/P2/P6/P7 四类 schema 各一例） ==========

@test "CF.4 BDD-6: P1 frontmatter 缺 risk_level（其余必填齐全）→ 校验失败" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/cf-XXXXXX")
    cat > "$dir/P1-requirements.md" <<'EOF'
---
phase: P1
task_id: T001
agent: analyst
phases: [P1]
packages: [agate]
domains: [backend]
---
#### BDD-1: test
- Given x
- When y
- Then z
EOF
    run bash -c "FILE='$dir/P1-requirements.md' $PYTHON '$AGATE_SCRIPTS/agate-frontmatter-check.py'"
    [ -n "$output" ]
    [[ "$output" == *"risk_level"* ]]
}

@test "CF.5 BDD-6: P2 frontmatter 缺 candidate_count（其余必填齐全）→ 校验失败" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/cf-XXXXXX")
    cat > "$dir/P2-design.md" <<'EOF'
---
phase: P2
task_id: T001
agent: architect
packages: [agate]
domains: [backend]
ui_affected: false
---
# P2 design
EOF
    run bash -c "FILE='$dir/P2-design.md' $PYTHON '$AGATE_SCRIPTS/agate-frontmatter-check.py'"
    [ -n "$output" ]
    [[ "$output" == *"candidate_count"* ]]
}

@test "CF.6 BDD-6+FIND-1: P7 frontmatter 只含 blocker_count（无任何流 A 字段）仍按 P7 schema 校验，缺 design_gap_count → 报错" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/cf-XXXXXX")
    # 关键：本文件 frontmatter 不含 risk_level/phases/packages/domains 等流 A 字段，
    # 只含流 B/C 字段（blocker_count）。FIND-1 要求判别契约按"该文件 schema 的迁移字段集"
    # 命中，而非按全集判定为旧格式回退——本例应仍触发 P7 schema 校验（而非 exit 0 静默放行）。
    cat > "$dir/P7-consistency.md" <<'EOF'
---
phase: P7
task_id: T001
agent: consistency-reviewer
blocker_count: 0
deviation_count: 0
deviation_critical_count: 0
---
一致性检查完成。
EOF
    run bash -c "FILE='$dir/P7-consistency.md' $PYTHON '$AGATE_SCRIPTS/agate-frontmatter-check.py'"
    [ -n "$output" ]
    [[ "$output" == *"design_gap_count"* ]]
}

# ========== BDD-7: 校验错误信息可定位修复（字段名/行号）——类型错误场景 ==========

@test "CF.7 BDD-7: P2 frontmatter candidate_count 类型错误（字符串而非 int）→ 报错含字段名 candidate_count" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/cf-XXXXXX")
    cat > "$dir/P2-design.md" <<'EOF'
---
phase: P2
task_id: T001
agent: architect
candidate_count: two
packages: [agate]
domains: [backend]
ui_affected: false
---
# P2 design
EOF
    run bash -c "FILE='$dir/P2-design.md' $PYTHON '$AGATE_SCRIPTS/agate-frontmatter-check.py'"
    [ -n "$output" ]
    [[ "$output" == *"candidate_count"* ]]
}

# ========== BDD-12: frontmatter 无超过 3 层的嵌套结构 ==========

@test "CF.8 BDD-12: P1 frontmatter 字段嵌套深度 > 3 层 → 校验失败" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/cf-XXXXXX")
    cat > "$dir/P1-requirements.md" <<'EOF'
---
phase: P1
task_id: T001
agent: analyst
risk_level: high
phases: [P1]
packages: [agate]
domains: [backend]
coupling_checklist:
  level1:
    level2:
      level3:
        level4: too-deep
---
#### BDD-1: test
- Given x
- When y
- Then z
EOF
    run bash -c "FILE='$dir/P1-requirements.md' $PYTHON '$AGATE_SCRIPTS/agate-frontmatter-check.py'"
    [ -n "$output" ]
    [[ "$output" == *"coupling_checklist"* ]]
}

# ========== FIND-5: 单行全角冒号块（无 key:value 结构）→ 非 dict 硬拦截 ==========

@test "CF.9 FIND-5: P1 frontmatter 块仅一行全角冒号纯量（非 dict，无 YAMLError）→ 仍被硬拦截" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/cf-XXXXXX")
    # 整个 --- ... --- 块只有一行文本，且含全角冒号但不构成 key: value 结构，
    # yaml.safe_load 对此返回 str 而非 dict，且不抛 YAMLError（P2-review 已实测复现）。
    printf -- '---\n风险等级：高\n---\n#### BDD-1: test\n- Given x\n- When y\n- Then z\n' > "$dir/P1-requirements.md"
    run bash -c "FILE='$dir/P1-requirements.md' $PYTHON '$AGATE_SCRIPTS/agate-frontmatter-check.py'"
    [ -n "$output" ]
    [[ "$output" != *"No such file"* ]]
    [[ "$output" == *"映射"* || "$output" == *"必须为"* || "$output" == *"dict"* ]]
}

# ========== BDD-8: 校验器与 .state.yaml 校验同机制接入 pre-commit（check-frontmatter.sh 薄壳契约） ==========

@test "CF.10 BDD-8: check-frontmatter.sh 与 check-state-yaml.sh 同构——非空校验输出 → exit 1；合规文件 → exit 0" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/cf-XXXXXX")
    # 坏格式：P2 缺 candidate_count
    cat > "$dir/P2-design.md" <<'EOF'
---
phase: P2
task_id: T001
agent: architect
packages: [agate]
domains: [backend]
ui_affected: false
---
# P2 design
EOF
    run bash "$AGATE_SCRIPTS/check-frontmatter.sh" "$dir/P2-design.md"
    [ "$status" -eq 1 ]

    # 合规：四字段齐全
    cat > "$dir/P2-design.md" <<'EOF'
---
phase: P2
task_id: T001
agent: architect
candidate_count: 2
packages: [agate]
domains: [backend]
ui_affected: false
---
# P2 design
EOF
    run bash "$AGATE_SCRIPTS/check-frontmatter.sh" "$dir/P2-design.md"
    [ "$status" -eq 0 ]
}

# ========== TAG0002 refactor 一等任务：change_type / regression_pass schema 校验（BDD-1/BDD-4） ==========

@test "CF.11 test_bdd_1_change_type_enum_valid: P1 frontmatter change_type: refactor（合法枚举）→ 校验通过" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/cf-XXXXXX")
    cat > "$dir/P1-requirements.md" <<'EOF'
---
phase: P1
task_id: T001
agent: analyst
risk_level: medium
phases: [P1, P2, P3, P4, P5, P6, P7, P8]
packages: [agate]
domains: [backend]
change_type: refactor
---
#### BDD-1: test
- Given x
- When y
- Then z
EOF
    run bash -c "FILE='$dir/P1-requirements.md' $PYTHON '$AGATE_SCRIPTS/agate-frontmatter-check.py'"
    [ "$status" -eq 0 ]
    [ -z "$output" ]
}

@test "CF.12 test_bdd_1_change_type_enum_invalid: P1 frontmatter change_type 枚举外值 → 校验失败且提示合法值 refactor" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/cf-XXXXXX")
    cat > "$dir/P1-requirements.md" <<'EOF'
---
phase: P1
task_id: T001
agent: analyst
risk_level: medium
phases: [P1, P2]
packages: [agate]
domains: [backend]
change_type: feature
---
#### BDD-1: test
- Given x
- When y
- Then z
EOF
    run bash -c "FILE='$dir/P1-requirements.md' $PYTHON '$AGATE_SCRIPTS/agate-frontmatter-check.py'"
    [ -n "$output" ]
    [[ "$output" == *"change_type"* ]]
    [[ "$output" == *"refactor"* ]]
}

@test "CF.13 test_bdd_4_regression_pass_type_invalid: P6 frontmatter regression_pass 非 bool → 校验失败且报错含 regression_pass" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/cf-XXXXXX")
    cat > "$dir/P6-acceptance.md" <<'EOF'
---
phase: P6
task_id: T001
agent: verifier
pass: 1
fail: 0
ui_affected: false
regression_pass: "yes"
---
- PASS BDD-1: 全量回归全绿 (P6-evidence/regression.log)
EOF
    run bash -c "FILE='$dir/P6-acceptance.md' $PYTHON '$AGATE_SCRIPTS/agate-frontmatter-check.py'"
    [ -n "$output" ]
    [[ "$output" == *"regression_pass"* ]]
}

@test "CF.14 test_bdd_4_regression_pass_type_valid: P6 frontmatter regression_pass: true（合法 bool）→ 校验通过" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/cf-XXXXXX")
    cat > "$dir/P6-acceptance.md" <<'EOF'
---
phase: P6
task_id: T001
agent: verifier
pass: 1
fail: 0
ui_affected: false
regression_pass: true
---
- PASS BDD-1: 全量回归全绿 (P6-evidence/regression.log)
EOF
    run bash -c "FILE='$dir/P6-acceptance.md' $PYTHON '$AGATE_SCRIPTS/agate-frontmatter-check.py'"
    [ "$status" -eq 0 ]
    [ -z "$output" ]
}
