#!/usr/bin/env bats
# tests/unit/check-gate.bats — 41 用例覆盖 check-gate.sh

load ../helpers/load.bash

# ========== P0 (立项阶段，无需脚本 gate) ==========

@test "G0 check-gate.sh P0 立项阶段 期望 exit 2（输出不含『未知』）" {
    local dir
    dir=$(create_task_dir)
    run bash "$AGATE_SCRIPTS/check-gate.sh" P0 "$dir"
    [ "$status" -eq 2 ]
    [[ "$output" != *"未知"* ]]
}

# ========== P1 (需 P1-review.md) ==========

@test "G1 check-gate.sh P1 缺 P1-review.md 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    run bash "$AGATE_SCRIPTS/check-gate.sh" P1 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"P1-review.md"* ]]
}

# ========== P2 多方案探索（5 用例） ==========

@test "G2.1 check-gate.sh P2 0 个候选方案 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
## 设计
无候选方案。
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"需至少 2 个候选方案"* ]]
}

@test "G2.2 check-gate.sh P2 1 个候选方案 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：方案一
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 1 ]
}

@test "G2.3 check-gate.sh P2 2 个候选方案 期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：方案一
### 候选方案 B：方案二
## 权衡
A 更简单，B 更稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G2.4 check-gate.sh P2 h4 候选方案不识别（regex 边界）" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
#### 候选方案 A：方案一
#### 候选方案 B：方案二
EOF
    # h4 不被 ^###? 匹配
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 1 ]
}

@test "G2.5 check-gate.sh P2 无 P2 文件 期望 exit 1" {
    local dir
    dir=$(create_task_dir P0 P1 P3 P4 P5 P6 P7 P8)  # P2 不在
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"P2-design.md"* ]]
}

@test "G2.8 check-gate.sh P2 候选方案 ≥2 但无权衡 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：方案一
### 候选方案 B：方案二
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"权衡"* ]]
}

@test "G2.9 check-gate.sh P2 候选方案 ≥2 + 含权衡 期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：方案一
### 候选方案 B：方案二
## 权衡
方案 A 更简单但性能差，方案 B 复杂但性能好。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G2.9a check-gate.sh P2 design_trivial + 1 候选方案 + 含权衡 期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    add_p1_field "$dir" "design_trivial" "true"
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：方案一
## 权衡
简单修改，无需多方案。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G2.9b check-gate.sh P2 follows_existing_pattern + 1 候选方案 + 含权衡 期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    add_p1_field "$dir" "follows_existing_pattern" "[src/foo.py]"
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：照搬已有模式
## 权衡
照搬 src/foo.py 模式。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G2.10 check-gate.sh P2 有候选方案+权衡+四字段，P2-review.md frontmatter status:rejected 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：方案一
### 候选方案 B：方案二
## 权衡
A 更简单，B 更稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    cat > "$dir/P2-review.md" <<'EOF'
---
agent: test
status: rejected
---
## 裁决
未通过。
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"非 approved"* ]]
}

@test "G2.10a check-gate.sh P2 frontmatter rejected + 正文含 status: approved 字面串 期望 exit 1（对抗绕过）" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：方案一
### 候选方案 B：方案二
## 权衡
A 更简单，B 更稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    cat > "$dir/P2-review.md" <<'EOF'
---
agent: test
status: rejected
---
## 裁决说明

gate 规则要求 status: approved 才放行，本次评审未通过。
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"非 approved"* ]]
}

@test "G2.11 check-gate.sh P2 有候选方案+权衡+四字段+frontmatter status:approved 期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：方案一
### 候选方案 B：方案二
## 权衡
A 更简单，B 更稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    cat > "$dir/P2-review.md" <<'EOF'
---
agent: test
status: approved
---
通过。
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G2.12 check-gate.sh P2-design.md 缺字段（<4）期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：方案一
### 候选方案 B：方案二
## 权衡
A 更简单，B 更稳健。
packages: [pkg-a]
domains: [backend]
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"缺字段"* ]]
}

@test "G2.13 check-gate.sh P2 有候选方案+权衡+四字段，无 P2-review.md 期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：方案一
### 候选方案 B：方案二
## 权衡
A 更简单，B 更稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

# ========== P3 check-tdd-red.sh 委托（7 个子用例） ==========
# G3.1-G3.7 见 check-tdd-red.bats（独立文件覆盖）
# 这里只验证 check-gate.sh P3 委托给了 check-tdd-red.sh

@test "G3 check-gate.sh P3 委托 check-tdd-red.sh（不直接执行测试）" {
    # 通过设置 TEST_RUNNER 验证委托关系
    local dir
    dir=$(create_task_dir)
    local fake_pytest="$BATS_TEST_TMPDIR/fake-pytest"
    cat > "$fake_pytest" <<'EOF'
#!/bin/bash
echo "5 passed"
exit 0
EOF
    chmod +x "$fake_pytest"
    TEST_RUNNER="$fake_pytest" run bash "$AGATE_SCRIPTS/check-gate.sh" P3 "$dir"
    # check-tdd-red.sh 输出 "tests pass, no red-light" → exit 2
    [ "$status" -eq 2 ]
}

# ========== P4 (4 用例) ==========

@test "G4.1 check-gate.sh P4 暂存区仅 .md 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md" && git_commit "$repo" "init"
    cp -r "$dir" "$repo/task"
    echo "doc" > "$repo/task/P4-implementation.md"
    git -C "$repo" add "task/P4-implementation.md"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-gate.sh' P4 'task'"
    [ "$status" -eq 1 ]
}

@test "G4.2 check-gate.sh P4 暂存区有 .py 代码 期望 exit 0" {
    local dir
    dir=$(create_task_dir)
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md" && git_commit "$repo" "init"
    cp -r "$dir" "$repo/task"
    echo "def hello(): pass" > "$repo/src.py"
    git -C "$repo" add "src.py"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-gate.sh' P4 'task'"
    [ "$status" -eq 0 ]
}

@test "G4.3 check-gate.sh P4 暂存区 .md + .yaml + .py 混合 期望 exit 0" {
    local dir
    dir=$(create_task_dir)
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md" && git_commit "$repo" "init"
    cp -r "$dir" "$repo/task"
    echo "doc" > "$repo/task/P4-implementation.md"
    echo "code" > "$repo/src.py"
    echo "yaml: 1" > "$repo/config.yaml"
    git -C "$repo" add .
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-gate.sh' P4 'task'"
    [ "$status" -eq 0 ]
}

@test "G4.4 check-gate.sh P4 暂存区 .py 排除 .md 期望 exit 0" {
    local dir
    dir=$(create_task_dir)
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md" && git_commit "$repo" "init"
    cp -r "$dir" "$repo/task"
    # .py 不在排除列表
    echo "code" > "$repo/src.py"
    git -C "$repo" add "src.py"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-gate.sh' P4 'task'"
    [ "$status" -eq 0 ]
}

# ========== P5 (固定 exit 2) ==========

@test "G5 check-gate.sh P5 期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    run bash "$AGATE_SCRIPTS/check-gate.sh" P5 "$dir"
    [ "$status" -eq 2 ]
}

@test "G5.1 T060: P2 gate_commands.P5 多命令时 P5 输出 WARNING" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
---
phase: P2
task_id: T001
agent: architect
---

gate_commands:
  P5: "pytest -q --tb=no"
  P5_e2e: "playwright test --reporter=line tests/e2e/"
EOF

    run bash "$AGATE_SCRIPTS/check-gate.sh" P5 "$dir"
    [ "$status" -eq 2 ]  # P5 恒 exit 2
    [[ "$output" == *"gate_commands.P5"* || "$output" == *"子集"* || "$output" == *"全量"* ]]
}

@test "G5_CMD.1 P2 gate_commands 声明 P5+P5_e2e（2 键），其他节含 20 个 bullet -> WARNING 含 2 而非 22" {
    local dir
    dir=$(create_task_dir)
    {
        echo "---"
        echo "phase: P2"
        echo "---"
        echo ""
        echo "候选方案："
        for i in $(seq 1 20); do echo "- 要点 $i"; done
        echo ""
        echo "gate_commands:"
        echo '  P5: "pytest -q"'
        echo '  P5_e2e: "playwright test"'
    } > "$dir/P2-design.md"

    run bash "$AGATE_SCRIPTS/check-gate.sh" P5 "$dir"
    [ "$status" -eq 2 ]
    [[ "$output" == *"2 个 gate_commands.P5"* ]]
    [[ "$output" != *"22 个"* ]]
}

@test "G5_CMD.2 P2 gate_commands 只声明 P5（1 键），其他节含 10 个 bullet -> 无 WARNING" {
    local dir
    dir=$(create_task_dir)
    {
        echo "---"
        echo "phase: P2"
        echo "---"
        echo ""
        for i in $(seq 1 10); do echo "- 要点 $i"; done
        echo ""
        echo "gate_commands:"
        echo '  P5: "pytest -q"'
    } > "$dir/P2-design.md"

    run bash "$AGATE_SCRIPTS/check-gate.sh" P5 "$dir"
    [ "$status" -eq 2 ]
    [[ "$output" != *"gate_commands.P5 命令"* ]]
}

@test "G5_CMD.3 P2 无 gate_commands 块 -> 无 WARNING，无崩溃" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
---
phase: P2
---
候选方案：无 gate_commands 声明
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P5 "$dir"
    [ "$status" -eq 2 ]
    [[ "$output" != *"gate_commands.P5 命令"* ]]
}

@test "G5_CMD.4 P2 gate_commands 声明 P5+P6（1 个 P5 键）-> 无 WARNING（P6 不算 P5 命令）" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
---
phase: P2
---
gate_commands:
  P5: "pytest -q"
  P6: "pytest tests/acceptance"
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P5 "$dir"
    [ "$status" -eq 2 ]
    [[ "$output" != *"gate_commands.P5 命令"* ]]
}

@test "G5_CMD.5 gate_commands 块位于文件末尾且无尾随换行 -> 仍正确计数 2 个 P5 键（回归：末尾换行边界）" {
    local dir
    dir=$(create_task_dir)
    printf 'gate_commands:\n  P5: "pytest"\n  P5_e2e: "playwright"' > "$dir/P2-design.md"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P5 "$dir"
    [ "$status" -eq 2 ]
    [[ "$output" == *"2 个 gate_commands.P5"* ]]
}

# ========== P6 (5 用例) ==========

@test "G6.1 check-gate.sh P6 含 FAIL 行 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1
- FAIL BDD-2
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P6 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"FAIL="* ]]
}

@test "G6.2 check-gate.sh P6 含 NEED_CONFIRM 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1
- [NEED_CONFIRM] BDD-2
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P6 "$dir"
    [ "$status" -eq 1 ]
}

@test "G6.3 check-gate.sh P6 全 PASS 但无 BDD 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
无 BDD 条目
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P6 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"TOTAL=0"* ]]
}

@test "G6.4 check-gate.sh P6 全 PASS 但无证据目录 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1
- PASS BDD-2
EOF
    # 没有 P6-evidence/ 目录
    run bash "$AGATE_SCRIPTS/check-gate.sh" P6 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"P6-evidence"* ]]
}

@test "G6.5 check-gate.sh P6 全 PASS + 证据目录非空 期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1
- PASS BDD-2
EOF
    mkdir -p "$dir/P6-evidence"
    echo "log" > "$dir/P6-evidence/result.log"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P6 "$dir"
    [ "$status" -eq 2 ]
}

@test "G6.7 check-gate.sh P6 小写 fail: 被计为 FAIL（大小写不敏感）" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1
- fail: BDD-2 broken
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P6 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"FAIL=1"* ]]
}

@test "G6.8 check-gate.sh P6 小写 fail（空格）被计为 FAIL" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1
- fail BDD-2: timeout
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P6 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"FAIL=1"* ]]
}

@test "G6.9 check-gate.sh P6 'failure' 不被计为 FAIL" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1
- failure mode detected
EOF
    mkdir -p "$dir/P6-evidence"
    echo "log" > "$dir/P6-evidence/result.log"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P6 "$dir"
    [ "$status" -eq 2 ]
    [[ "$output" == *"FAIL=0"* ]]
}

# ========== P7 (5 用例) ==========

@test "G7.1 check-gate.sh P7 含 [BLOCKER] 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P7-consistency.md" <<'EOF'
- [BLOCKER] arch flaw
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P7 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"BLOCKER="* ]]
}

@test "G7.2 check-gate.sh P7 含 [DEVIATION-CRITICAL] 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P7-consistency.md" <<'EOF'
- [DEVIATION-CRITICAL] ui break
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P7 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"DEVIATION-CRITICAL="* ]]
}

@test "G7.3 check-gate.sh P7 DESIGN_GAP 未配对 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P7-consistency.md" <<'EOF'
- [DESIGN_GAP: P2 未指定错误处理]
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P7 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"DESIGN_GAP"*"未配对"* ]]
}

@test "G7.4 check-gate.sh P7 DESIGN_GAP 已配对 期望 exit 0" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P7-consistency.md" <<'EOF'
- [DESIGN_GAP: P2 未指定错误处理]
- [DESIGN_GAP_REVIEWED: 已确认]
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P7 "$dir"
    [ "$status" -eq 0 ]
}

@test "G7.5 check-gate.sh P7 2 GAP + 1 REVIEWED 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P7-consistency.md" <<'EOF'
- [DESIGN_GAP: A]
- [DESIGN_GAP: B]
- [DESIGN_GAP_REVIEWED: A 已确认]
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P7 "$dir"
    [ "$status" -eq 1 ]
}

@test "G7.6 check-gate.sh P7 空文件 期望 exit 0" {
    local dir
    dir=$(create_task_dir)
    : > "$dir/P7-consistency.md"  # 空
    run bash "$AGATE_SCRIPTS/check-gate.sh" P7 "$dir"
    [ "$status" -eq 0 ]
}

@test "G7.7 check-gate.sh P7 P4 有 DESIGN_GAP 但 P7 未转抄 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P4-implementation.md" <<'EOF'
---
agent: test
---
- [DESIGN_GAP: P2 未指定错误处理]
EOF
    cat > "$dir/P7-consistency.md" <<'EOF'
---
agent: test
---
一致性检查完成。
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P7 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"P4"*"DESIGN_GAP"*"P7"* ]]
}

# ========== P8 (5 用例) ==========

@test "G8.1 check-gate.sh P8 缺 bump_type 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P8-release.md" <<'EOF'
无 bump_type
EOF
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md" && git_commit "$repo" "init"
    cp -r "$dir" "$repo/task"
    echo "v0.1.0" > "$repo/package.json"
    echo "## [Unreleased]" > "$repo/CHANGELOG.md"
    git -C "$repo" add package.json CHANGELOG.md
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-gate.sh' P8 'task'"
    [ "$status" -eq 1 ]
    [[ "$output" == *"bump_type"* ]]
}

@test "G8.2 check-gate.sh P8 无 version 文件变更（暂存区）期望 WARNING（不阻断）" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P8-release.md" <<'EOF'
bump_type: minor
EOF
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md" && git_commit "$repo" "init"
    cp -r "$dir" "$repo/task"
    # 不改 version 文件
    echo "doc" > "$repo/some.md"
    echo "## [Unreleased]" > "$repo/CHANGELOG.md"
    git -C "$repo" add some.md CHANGELOG.md
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-gate.sh' P8 'task'"
    # P1-6: version 不匹配降级为 WARNING（不设 RC=1），但 CHANGELOG 已变更 → RC=0 → exit 2
    [ "$status" -eq 2 ]
    [[ "$output" == *"WARNING"*"version"* ]]
}

@test "G8.3 check-gate.sh P8 有 version 但 CHANGELOG 无变更 期望 exit 2 (WARNING)" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P8-release.md" <<'EOF'
bump_type: minor
EOF
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md" && git_commit "$repo" "init"
    cp -r "$dir" "$repo/task"
    echo "v0.1.0" > "$repo/package.json"
    # CHANGELOG 没改 → WARNING（不阻断）
    git -C "$repo" add package.json
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-gate.sh' P8 'task'"
    [ "$status" -eq 2 ]
    [[ "$output" == *"CHANGELOG"* ]]
}

@test "G8.4 check-gate.sh P8 全合规 期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P8-release.md" <<'EOF'
bump_type: minor
EOF
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md" && git_commit "$repo" "init"
    cp -r "$dir" "$repo/task"
    echo "v0.1.0" > "$repo/package.json"
    echo "## [Unreleased]" > "$repo/CHANGELOG.md"
    git -C "$repo" add package.json CHANGELOG.md
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-gate.sh' P8 'task'"
    [ "$status" -eq 2 ]
}

@test "G8.5 check-gate.sh P8 无 P8 文件 期望 exit 1" {
    local dir
    dir=$(create_task_dir P0 P1 P2 P3 P4 P5 P6 P7)  # P8 不在
    # P8-release.md 不存在 → bump_type 缺失 → exit 1
    run bash "$AGATE_SCRIPTS/check-gate.sh" P8 "$dir"
    [ "$status" -eq 1 ]
}

@test "G8.7 check-gate.sh P8 tag 不存在 期望 WARNING（exit 2，不阻断）" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P8-release.md" <<'EOF'
bump_type: minor
EOF
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md" && git_commit "$repo" "init"
    cp -r "$dir" "$repo/task"
    echo "v0.1.0" > "$repo/package.json"
    printf '## [Unreleased]\n\n## [0.2.0] - 2026-07-20\n' > "$repo/CHANGELOG.md"
    git -C "$repo" add package.json CHANGELOG.md
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-gate.sh' P8 'task'"
    [ "$status" -eq 2 ]
    [[ "$output" == *"tag v0.2.0 不存在"* ]]
}

@test "G8.8 check-gate.sh P8 tag 存在 期望无 tag WARNING" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P8-release.md" <<'EOF'
bump_type: minor
EOF
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md" && git_commit "$repo" "init"
    cp -r "$dir" "$repo/task"
    echo "v0.2.0" > "$repo/package.json"
    printf '## [Unreleased]\n\n## [0.2.0] - 2026-07-20\n' > "$repo/CHANGELOG.md"
    git -C "$repo" add package.json CHANGELOG.md
    git -C "$repo" tag v0.2.0
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-gate.sh' P8 'task'"
    [ "$status" -eq 2 ]
    [[ "$output" != *"tag v0.2.0 不存在"* ]]
}

# ========== 默认 case ==========

@test "D-drift-1: dispatch-prompt.md 含'返回前自检'" {
    grep -q '返回前自检' "$AGATE_ROOT/assets/templates/dispatch-prompt.md"
}

@test "D-drift-2: dispatch-prompt.md 含'files_modified'" {
    grep -q 'files_modified' "$AGATE_ROOT/assets/templates/dispatch-prompt.md"
}

@test "D-drift-4: dispatch-context.md 含 XML 派发指引节（dispatch_guide/目标/约束）" {
    grep -q '<dispatch_guide>' "$AGATE_ROOT/assets/templates/dispatch-context.md"
    grep -q '### 目标' "$AGATE_ROOT/assets/templates/dispatch-context.md"
    grep -q '### 约束' "$AGATE_ROOT/assets/templates/dispatch-context.md"
}

@test "D-drift-4b: dispatch-context.md 含 XML 标记（dispatch_guide/objective_info）" {
    grep -q '<dispatch_guide>' "$AGATE_ROOT/assets/templates/dispatch-context.md"
    grep -q '<objective_info>' "$AGATE_ROOT/assets/templates/dispatch-context.md"
}

@test "G-drift-1: dispatch-protocol.md 含'自查≠gate'关键词" {
    grep -q '自查≠gate' "$AGATE_ROOT/dispatch-protocol.md"
}

@test "G-drift-2: implementer.md 不含'写跑分离'" {
    ! grep -q '写跑分离' "$AGATE_ROOT/assets/execution-roles/implementer.md"
}

@test "G-drift-3: verifier.md 不含'写跑分离'" {
    ! grep -q '写跑分离' "$AGATE_ROOT/assets/execution-roles/verifier.md"
}

@test "G_OTHER check-gate.sh 未知阶段 期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    run bash "$AGATE_SCRIPTS/check-gate.sh" P9 "$dir"
    [ "$status" -eq 2 ]
    [[ "$output" == *"未知阶段"* ]]
}

@test "G2.14 check-gate.sh P2 方案 A（有空格）+ 方案 B 期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 方案 A
### 方案 B
## 权衡
A 简单，B 稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G2.15 check-gate.sh P2 方案一 + 方案二 期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 方案一
### 方案二
## 权衡
方案一简单，方案二稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G2.16 check-gate.sh P2 候选方案 ≥2 + 含'取舍' 期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：方案一
### 候选方案 B：方案二
## 取舍
A 更简单，B 更稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G2.17 check-gate.sh P2 候选方案 ≥2 + '选择'标题+正文'理由' 期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：方案一
### 候选方案 B：方案二
### 选择：方案 A
**理由**：A 更简单。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G2.18 check-gate.sh P2-review agent=subagent + frontmatter status:approved → exit 2" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：方案一
### 候选方案 B：方案二
## 权衡
A 更简单，B 更稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    cat > "$dir/P2-review.md" <<'EOF'
---
agent: subagent
status: approved
---
通过。
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G2.19 check-gate.sh P2-review agent=main + frontmatter status:approved → exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：方案一
### 候选方案 B：方案二
## 权衡
A 更简单，B 更稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    cat > "$dir/P2-review.md" <<'EOF'
---
agent: main
status: approved
---
通过。
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"agent=main"* ]]
}

@test "G2.20 check-gate.sh P2-review 缺 agent 字段 + frontmatter status:approved → exit 2 (WARNING)" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：方案一
### 候选方案 B：方案二
## 权衡
A 更简单，B 更稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    cat > "$dir/P2-review.md" <<'EOF'
---
status: approved
---
通过。
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
    [[ "$output" == *"agent"* ]]
}

@test "G7.8 check-gate.sh P7 [BLOCKER]: 0 条（声明）期望 exit 0" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P7-consistency.md" <<'EOF'
- [BLOCKER]: 0 条
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P7 "$dir"
    [ "$status" -eq 0 ]
}

@test "G7.9 check-gate.sh P7 [BLOCKER]: 0 条 + 实际 BLOCKER 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P7-consistency.md" <<'EOF'
- [BLOCKER]: 0 条
- [BLOCKER] arch flaw
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P7 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"BLOCKER="* ]]
}

# ========== 额外边界（凑到 33 个用例） ==========

@test "G2.6 check-gate.sh P2 方案 A/B/C 多种命名（regex [ABC123]）" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 方案A
### 方案B
## 权衡
A 简单，B 稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G2.7 check-gate.sh P2 h2 (##) 候选方案也被识别" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
## 候选方案 A
## 候选方案 B
## 权衡
A 简单，B 稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G6.6 check-gate.sh P6 FAIL=0 但 NEED_CONFIRM>0 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1
- [NEED_CONFIRM] BDD-2
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P6 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"NEED_CONFIRM="* ]]
}

@test "G8.6 check-gate.sh P8 CHANGELOG_FILE 环境变量覆盖" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P8-release.md" <<'EOF'
bump_type: minor
EOF
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md" && git_commit "$repo" "init"
    cp -r "$dir" "$repo/task"
    echo "v0.1.0" > "$repo/package.json"
    # 用非默认 changelog 文件
    echo "## [Unreleased]" > "$repo/HISTORY.md"
    git -C "$repo" add package.json HISTORY.md
     CHANGELOG_FILE="HISTORY.md" run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-gate.sh' P8 'task'"
    [ "$status" -eq 2 ]
}

@test "G2.21 check-gate.sh P2 方案 Alpha（多词方案名）期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 方案 Alpha
### 方案 Beta
## 权衡
Alpha 简单，Beta 稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G2.22 check-gate.sh P2 Alternative A + Option B 期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### Alternative A
### Option B
## 权衡
Alternative A is simpler, Option B is more robust.
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G2.23 check-gate.sh P2 方案 Recommended（多词方案名）期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 方案 Recommended
### 方案 Conservative
## 权衡
Recommended 更激进，Conservative 更保守。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G2.24 check-gate.sh P2 方案 1 + 方案 2（数字编号）期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 方案 1
### 方案 2
## 权衡
方案 1 简单，方案 2 稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

# ========== 标记二值声明：NEED_CONFIRM ==========

@test "G_NC_BINARY.1 P1 含 [NO_NEED_CONFIRM] 期望 exit 2（NC=0，通过）" {
    local dir
    dir=$(create_task_dir --no-state-yaml)
    cat > "$dir/P1-requirements.md" <<'EOF'
---
phase: P1
task_id: T001-test
status: draft
agent: analyst
---
# Requirements
- Given x When y Then z
- [NO_NEED_CONFIRM]
EOF
    cat > "$dir/P1-review.md" <<'EOF'
---
phase: P1
task_id: T001-test
status: approved
agent: requirements-review
---
## BDD 评审
- BDD-1: PASS
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P1 "$dir"
    [ "$status" -eq 2 ]
}

@test "G_NC_BINARY.2 P1 含行首 [NEED_CONFIRM] 描述 期望 exit 1（NC>0）" {
    local dir
    dir=$(create_task_dir --no-state-yaml)
    cat > "$dir/P1-requirements.md" <<'EOF'
---
phase: P1
task_id: T001-test
status: draft
agent: analyst
---
# Requirements
- Given x When y Then z
- [NEED_CONFIRM] z 的边界条件需确认
EOF
    cat > "$dir/P1-review.md" <<'EOF'
---
phase: P1
task_id: T001-test
status: approved
agent: requirements-review
---
## BDD 评审
- BDD-1: PASS
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P1 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"NEED_CONFIRM"* ]]
}

@test "G_NC_BINARY.3 P1 含不合规格式（句中引用）期望 exit 1（步骤 2 拦截）" {
    local dir
    dir=$(create_task_dir --no-state-yaml)
    cat > "$dir/P1-requirements.md" <<'EOF'
---
phase: P1
task_id: T001-test
status: draft
agent: analyst
---
# Requirements
- Given x When y Then z
无 [NEED_CONFIRM] 需要确认
EOF
    cat > "$dir/P1-review.md" <<'EOF'
---
phase: P1
task_id: T001-test
status: approved
agent: requirements-review
---
## BDD 评审
- BDD-1: PASS
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P1 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"不合规"* ]]
}

@test "G_NC_BINARY.4 P6 含 [NO_NEED_CONFIRM] + 最小有效 fixture 期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1
- [NO_NEED_CONFIRM]
EOF
    mkdir -p "$dir/P6-evidence"
    echo "log" > "$dir/P6-evidence/result.log"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P6 "$dir"
    [ "$status" -eq 2 ]
}

@test "G_NC_BINARY.5 P1 既无正向也无负向声明 期望 exit 2 + WARNING" {
    local dir
    dir=$(create_task_dir --no-state-yaml)
    cat > "$dir/P1-requirements.md" <<'EOF'
---
phase: P1
task_id: T001-test
status: draft
agent: analyst
---
# Requirements
- Given x When y Then z
EOF
    cat > "$dir/P1-review.md" <<'EOF'
---
phase: P1
task_id: T001-test
status: approved
agent: requirements-review
---
## BDD 评审
- BDD-1: PASS
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P1 "$dir"
    [ "$status" -eq 2 ]
    [[ "$output" == *"WARNING"* ]]
}

@test "G_NC_BINARY.6 P1 含 [NO_NEED_CONFIRM] 确认无不可逆操作（负向+描述）期望 exit 2" {
    local dir
    dir=$(create_task_dir --no-state-yaml)
    cat > "$dir/P1-requirements.md" <<'EOF'
---
phase: P1
task_id: T001-test
status: draft
agent: analyst
---
# Requirements
- Given x When y Then z
- [NO_NEED_CONFIRM] 确认无不可逆操作
EOF
    cat > "$dir/P1-review.md" <<'EOF'
---
phase: P1
task_id: T001-test
status: approved
agent: requirements-review
---
## BDD 评审
- BDD-1: PASS
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P1 "$dir"
    [ "$status" -eq 2 ]
}

# ========== 行首锚点：DESIGN_GAP ==========

@test "G_DG_ANCHOR.1 P7 句中 [DESIGN_GAP: xxx]（非行首）不计入 GAP 计数" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P7-consistency.md" <<'EOF'
# P7 一致性检查
检查了 [DESIGN_GAP: xxx] 的引用
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P7 "$dir"
    [ "$status" -eq 0 ]
}

@test "G_DG_ANCHOR.2 P7 行首 [DESIGN_GAP: xxx] 计入 GAP 计数" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P7-consistency.md" <<'EOF'
# P7 一致性检查
- [DESIGN_GAP: xxx] 未配对
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P7 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"DESIGN_GAP"* ]]
}

# ========== 回退抵达检测（OLD_PHASE 可选第 3 参数）==========

@test "G_RETREAT.1 P1 无 OLD_PHASE（省略）→ 行为不变，P1-review.md 缺失仍 exit 1" {
    local dir
    dir="$BATS_TEST_TMPDIR/g_retreat1"
    mkdir -p "$dir"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P1 "$dir"
    [ "$status" -eq 1 ]
}

@test "G_RETREAT.2 P1 OLD_PHASE=P2（回退抵达）→ exit 2，跳过完成度校验" {
    local dir
    dir="$BATS_TEST_TMPDIR/g_retreat2"
    mkdir -p "$dir"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P1 "$dir" P2
    [ "$status" -eq 2 ]
    [[ "$output" == *"回退抵达"* ]]
}

@test "G_RETREAT.3 P4 OLD_PHASE=P6（回退抵达，本次 plan 的核心场景）→ exit 2" {
    local dir
    dir="$BATS_TEST_TMPDIR/g_retreat3"
    mkdir -p "$dir"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P4 "$dir" P6
    [ "$status" -eq 2 ]
    [[ "$output" == *"回退抵达"* ]]
}

@test "G_RETREAT.4 P6 OLD_PHASE=P7（回退抵达）→ exit 2，即使证据目录不存在" {
    local dir
    dir="$BATS_TEST_TMPDIR/g_retreat4"
    mkdir -p "$dir"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P6 "$dir" P7
    [ "$status" -eq 2 ]
}

@test "G_RETREAT.5 P4 OLD_PHASE=P3（正常推进方向，非回退）→ 仍按原逻辑要求代码文件" {
    local dir
    dir="$BATS_TEST_TMPDIR/g_retreat5"
    mkdir -p "$dir"
    cd "$dir"
    git init -q
    run bash "$AGATE_SCRIPTS/check-gate.sh" P4 "$dir" P3
    # 暂存区没有代码文件，仍应 exit 1（不因为传了 OLD_PHASE 就被误判成回退而放行）
    [ "$status" -eq 1 ]
}

@test "G_RETREAT.6 OLD_PHASE 与 PHASE 相同（非法/无意义输入）→ 不触发回退检测，走原逻辑" {
    local dir
    dir="$BATS_TEST_TMPDIR/g_retreat6"
    mkdir -p "$dir"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P1 "$dir" P1
    # OLD_NUM 不大于 NEW_NUM，不判定为回退，走原有 P1 逻辑（P1-review.md 缺失 exit 1）
    [ "$status" -eq 1 ]
    [[ "$output" != *"回退抵达"* ]]
}
