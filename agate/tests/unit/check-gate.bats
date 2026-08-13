#!/usr/bin/env bats
# tests/unit/check-gate.bats — 覆盖 check-gate.sh（@test 数以 count-tests.sh 为准）

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
    add_p2_review "$dir"
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
    add_p2_review "$dir"
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
    add_p2_candidate_count "$dir" 2
    add_p2_review "$dir"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G2.4 check-gate.sh P2 h5 候选方案不识别（regex 边界）" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
##### 候选方案 A：方案一
##### 候选方案 B：方案二
EOF
    # h5 不被 ^#{2,4} 匹配
    add_p2_review "$dir"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 1 ]
}

@test "G2.25 check-gate.sh P2 #### 候选方案识别（h4 支持）" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
#### 候选方案 A：方案一
#### 候选方案 B：方案二
## 权衡
A 更简单，B 更稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    add_p2_candidate_count "$dir" 2
    add_p2_review "$dir"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G2.26 check-gate.sh P2 全角冒号标题 + candidate_count 字段 期望 exit 2（纯强制）" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 方案：方案一
### 方案：方案二
## 权衡
A 更简单，B 更稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    add_p2_candidate_count "$dir" 2
    add_p2_review "$dir"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G2.27 check-gate.sh P2 缺 candidate_count 字段 期望 exit 1（纯强制）" {
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
    add_p2_review "$dir"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"candidate_count"* ]]
}

@test "G2.5 check-gate.sh P2 无 P2 文件 期望 exit 1" {
    local dir
    dir=$(create_task_dir P0 P1 P3 P4 P5 P6 P7 P8)  # P2 不在
    add_p2_review "$dir"
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
    add_p2_candidate_count "$dir" 2
    add_p2_review "$dir"
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
    add_p2_candidate_count "$dir" 2
    add_p2_review "$dir"
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
    add_p2_candidate_count "$dir" 1
    add_p2_review "$dir"
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
    add_p2_candidate_count "$dir" 1
    add_p2_review "$dir"
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
    add_p2_candidate_count "$dir" 2
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
    add_p2_candidate_count "$dir" 2
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
    add_p2_candidate_count "$dir" 2
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

@test "G_BDD1.1 BDD-1: check-gate.sh P2 四字段经 frontmatter 声明（非正文）仍被门禁正确读取判定" {
    # T001 v2.0 流 A：packages/domains/ui_affected 迁入 frontmatter 块后，
    # check-gate.sh 的判定结果须与声明一致（BDD-1"门禁基于 frontmatter 声明值完成判定"）。
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
---
phase: P2
task_id: T001
agent: architect
packages: [pkg-a]
domains: [backend]
ui_affected: false
---
# P2 design
### 候选方案 A：方案一
### 候选方案 B：方案二
## 权衡
A 更简单，B 更稳健。
gate_commands: {}
EOF
    add_p2_candidate_count "$dir" 2
    add_p2_review "$dir"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G2.13 check-gate.sh P2 有候选方案+权衡+四字段，无 P2-review.md 期望 exit 1" {
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
    add_p2_candidate_count "$dir" 2
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"P2-review.md"* ]]
}

@test "PG.P2REVIEW: P2-review.md not found → exit 1" {
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
    add_p2_candidate_count "$dir" 2
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"P2-review.md 不存在"* ]]
}

@test "G_CMD_EXEC.1: P2 gate_commands 命令不可执行 → WARNING 不阻断 (exit 2)" {
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
gate_commands:
  P3: "definitely-nonexistent-cmd --flag"
  P5: "echo hi"
EOF
    add_p2_candidate_count "$dir" 2
    cat > "$dir/P2-review.md" <<'EOF'
---
agent: test
status: approved
---
通过。
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
    [[ "$output" == *"definitely-nonexistent-cmd"* ]]
}

@test "G_CMD_EXEC.2: P2 gate_commands 命令均可执行 → 无 WARNING (exit 2)" {
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
gate_commands:
  P3: "true"
  P5: "echo hi"
EOF
    add_p2_candidate_count "$dir" 2
    cat > "$dir/P2-review.md" <<'EOF'
---
agent: test
status: approved
---
通过。
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
    [[ "$output" != *"不存在"* ]]
}

# ========== P3 check-tdd-red.sh 委托（7 个子用例） ==========
# G3.1-G3.7 见 check-tdd-red.bats（独立文件覆盖）
# 这里只验证 check-gate.sh P3 检查文件存在性（不跑测试）

@test "G3 check-gate.sh P3 检查 P3-test-cases.md 存在（不跑测试）" {
    local dir
    dir=$(create_task_dir)
    # 无 P3-test-cases.md → exit 1
    run bash "$AGATE_SCRIPTS/check-gate.sh" P3 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"P3-test-cases.md 不存在"* ]]

    # 有 P3-test-cases.md → exit 2
    echo '## P3 test cases' > "$dir/P3-test-cases.md"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P3 "$dir"
    [ "$status" -eq 2 ]
    [[ "$output" == *"check-tdd-red.sh"* ]]
}

# ========== P4 (7 用例) ==========

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
    cat > "$repo/task/P4-review.md" <<'EOF'
---
status: approved
agent: reviewer-subagent
---
reviewed, approved.
EOF
    echo "def hello(): pass" > "$repo/src.py"
    git -C "$repo" add "src.py" "task/P4-review.md"
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
    cat > "$repo/task/P4-review.md" <<'EOF'
---
status: approved
agent: reviewer-subagent
---
reviewed, approved.
EOF
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
    cat > "$repo/task/P4-review.md" <<'EOF'
---
status: approved
agent: reviewer-subagent
---
reviewed, approved.
EOF
    # .py 不在排除列表
    echo "code" > "$repo/src.py"
    git -C "$repo" add "src.py" "task/P4-review.md"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-gate.sh' P4 'task'"
    [ "$status" -eq 0 ]
}

@test "G4.5 check-gate.sh P4 无 P4-review.md → exit 1（评审不可跳过）" {
    local dir
    dir=$(create_task_dir)
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md" && git_commit "$repo" "init"
    cp -r "$dir" "$repo/task"
    echo "code" > "$repo/src.py"
    git -C "$repo" add "src.py"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-gate.sh' P4 'task'"
    [ "$status" -eq 1 ]
    [[ "$output" == *"P4-review.md"* ]]
}

@test "G4.6 check-gate.sh P4 P4-review.md status 非 approved → exit 1" {
    local dir
    dir=$(create_task_dir)
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md" && git_commit "$repo" "init"
    cp -r "$dir" "$repo/task"
    cat > "$repo/task/P4-review.md" <<'EOF'
---
status: rejected
agent: reviewer-subagent
---
reviewed, found issues.
EOF
    echo "code" > "$repo/src.py"
    git -C "$repo" add "src.py" "task/P4-review.md"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-gate.sh' P4 'task'"
    [ "$status" -eq 1 ]
    [[ "$output" == *"非 approved"* ]]
}

@test "G4.7 check-gate.sh P4 P4-review.md agent=main → exit 1（不可自批）" {
    local dir
    dir=$(create_task_dir)
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md" && git_commit "$repo" "init"
    cp -r "$dir" "$repo/task"
    cat > "$repo/task/P4-review.md" <<'EOF'
---
status: approved
agent: main
---
self-approved.
EOF
    echo "code" > "$repo/src.py"
    git -C "$repo" add "src.py" "task/P4-review.md"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-gate.sh' P4 'task'"
    [ "$status" -eq 1 ]
    [[ "$output" == *"agent=main"* ]]
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

@test "G6.10 check-gate.sh P6 含 [NEED_CONFIRM] 不再拦截（v0.30.3 语义修正）" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1
- [NEED_CONFIRM] some text
EOF
    mkdir -p "$dir/P6-evidence"
    echo "log" > "$dir/P6-evidence/result.log"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P6 "$dir"
    [ "$status" -eq 2 ]
}

@test "G6.11 check-gate.sh P6 无 [NO_NEED_CONFIRM] 不再 WARNING（v0.30.3）" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1 (result.log)
EOF
    mkdir -p "$dir/P6-evidence"
    echo "log" > "$dir/P6-evidence/result.log"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P6 "$dir"
    [ "$status" -eq 2 ]
    [[ "$output" != *"NEED_CONFIRM"* ]]
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

@test "G_BDD16.1 BDD-16: check-gate.sh P6 frontmatter 声明 pass/fail 汇总时门禁基于该汇总判定（非正文 grep 计数）" {
    # T001 v2.0 流 B：正文无任何 "- PASS/FAIL" 行（旧版 grep 计数会得 TOTAL=0 → exit 1），
    # 但 frontmatter 声明 pass:1/fail:0 → 门禁应基于 frontmatter 汇总判定为 exit 2。
    # 这是区分"新逻辑基于 frontmatter" vs "旧逻辑从正文 grep 计数"的关键场景。
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
---
phase: P6
task_id: T001
agent: verifier
pass: 1
fail: 0
ui_affected: false
---
逐条结果见 P6-evidence/ 详细记录（本文件正文不复述逐条 PASS/FAIL 行）。
EOF
    mkdir -p "$dir/P6-evidence"
    echo "log" > "$dir/P6-evidence/result.json"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P6 "$dir"
    [ "$status" -eq 2 ]
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

# ========== P6 refactor 一等任务分流（TAG0002，BDD-1/2/3/4/6/7 + BDD-5/8 文档锚点） ==========

@test "test_bdd_1_p1_gate_accepts_change_type_refactor" {
    # BDD-1: P1 frontmatter 声明 change_type: refactor 不因该字段报错，gate exit 2（任务可推进 P2）
    local dir
    dir=$(create_task_dir)
    add_p1_field "$dir" change_type refactor
    cat > "$dir/P1-review.md" <<'EOF'
---
status: approved
agent: requirements-review
---
## BDD 评审
- BDD-1: PASS
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P1 "$dir"
    [ "$status" -eq 2 ]
    [[ "$output" != *"change_type"* ]]
}

@test "test_bdd_2_p6_gate_default_no_change_type_unchanged" {
    # BDD-2: 未声明 change_type（缺省）→ P6 走既有功能口径（功能 BDD 计数 + 证据目录），行为与改造前一致
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

@test "test_bdd_2b_p6_gate_default_body_mentions_change_type_still_functional" {
    # BDD-2 回归（P4-review §2.1 BLOCKER）：功能任务 frontmatter 无 change_type，
    # 仅正文散文提及 `change_type: refactor` 关键字 → P6 仍走既有功能口径（exit 2），不误拦
    local dir
    dir=$(create_task_dir)
    printf '\nchange_type: refactor 是可选字段，缺省为功能任务（本文档仅作说明，本任务不采用 refactor 口径）\n' >> "$dir/P1-requirements.md"
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1
- PASS BDD-2
EOF
    mkdir -p "$dir/P6-evidence"
    echo "log" > "$dir/P6-evidence/result.log"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P6 "$dir"
    [ "$status" -eq 2 ]
}

@test "test_bdd_3_p6_gate_refactor_with_regression_evidence" {
    # BDD-3: change_type=refactor + regression_pass:true + P6-evidence/regression.log + 关键路径 PASS → gate 通过
    local dir
    dir=$(create_task_dir)
    add_p1_field "$dir" change_type refactor
    cat > "$dir/P6-acceptance.md" <<'EOF'
---
phase: P6
task_id: TAG0002
agent: verifier
pass: 1
fail: 0
ui_affected: false
regression_pass: true
---
- PASS BDD-1: 全量回归全绿（重构后完整测试套件 0 失败）(P6-evidence/regression.log)
EOF
    mkdir -p "$dir/P6-evidence"
    printf 'bats ... 0 failures\nEXIT_CODE: 0\n' > "$dir/P6-evidence/regression.log"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P6 "$dir"
    [ "$status" -eq 2 ]
}

@test "test_bdd_4_p6_gate_refactor_missing_regression_log" {
    # BDD-4: refactor 任务回归失败 → gate 不通过——regression.log 缺失即拦截（关键路径 PASS 不能豁免）
    local dir
    dir=$(create_task_dir)
    add_p1_field "$dir" change_type refactor
    cat > "$dir/P6-acceptance.md" <<'EOF'
---
phase: P6
task_id: TAG0002
agent: verifier
pass: 1
fail: 0
ui_affected: false
regression_pass: true
---
- PASS BDD-1: 全量回归全绿（重构后完整测试套件 0 失败）(P6-evidence/regression.log)
EOF
    mkdir -p "$dir/P6-evidence"
    echo "other" > "$dir/P6-evidence/result.log"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P6 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"regression.log"* ]]
}

@test "test_bdd_4b_p6_gate_refactor_missing_regression_pass" {
    # BDD-4: refactor 任务回归失败 → gate 不通过——regression_pass 未声明 true 即拦截
    local dir
    dir=$(create_task_dir)
    add_p1_field "$dir" change_type refactor
    cat > "$dir/P6-acceptance.md" <<'EOF'
---
phase: P6
task_id: TAG0002
agent: verifier
pass: 1
fail: 0
ui_affected: false
---
- PASS BDD-1: 全量回归全绿（重构后完整测试套件 0 失败）(P6-evidence/regression.log)
EOF
    mkdir -p "$dir/P6-evidence"
    printf 'bats ... 0 failures\nEXIT_CODE: 0\n' > "$dir/P6-evidence/regression.log"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P6 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"regression_pass"* ]]
}

@test "test_bdd_6_p6_gate_refactor_no_behavior_change_not_waived" {
    # BDD-6: refactor 独立于 no_behavior_change——声明 no_behavior_change 不豁免回归双证，缺 regression.log 仍 exit 1
    local dir
    dir=$(create_task_dir)
    add_p1_field "$dir" change_type refactor
    printf '\nno_behavior_change: 预期无行为变更\n' >> "$dir/P1-requirements.md"
    cat > "$dir/P6-acceptance.md" <<'EOF'
---
phase: P6
task_id: TAG0002
agent: verifier
pass: 1
fail: 0
ui_affected: false
regression_pass: true
---
- PASS BDD-1: 全量回归全绿（重构后完整测试套件 0 失败）(P6-evidence/regression.log)
EOF
    mkdir -p "$dir/P6-evidence"
    echo "other" > "$dir/P6-evidence/result.log"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P6 "$dir"
    [ "$status" -eq 1 ]
}

@test "test_bdd_6b_p6_gate_refactor_no_behavior_change_with_evidence" {
    # BDD-6 正向: refactor + no_behavior_change + 回归双证齐备 → gate 通过（口径仍为回归口径）
    local dir
    dir=$(create_task_dir)
    add_p1_field "$dir" change_type refactor
    printf '\nno_behavior_change: 预期无行为变更\n' >> "$dir/P1-requirements.md"
    cat > "$dir/P6-acceptance.md" <<'EOF'
---
phase: P6
task_id: TAG0002
agent: verifier
pass: 1
fail: 0
ui_affected: false
regression_pass: true
---
- PASS BDD-1: 全量回归全绿（重构后完整测试套件 0 失败）(P6-evidence/regression.log)
EOF
    mkdir -p "$dir/P6-evidence"
    printf 'bats ... 0 failures\nEXIT_CODE: 0\n' > "$dir/P6-evidence/regression.log"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P6 "$dir"
    [ "$status" -eq 2 ]
}

@test "test_bdd_7_refactor_backfill_walk_p1_p3_p6" {
    # BDD-7: 真实重构回填（fixture 建模 c182dc3 产物形状）走 P1→P3→P6，各阶段 gate 通过且不要求功能 BDD
    local dir
    dir=$(create_task_dir)
    add_p1_field "$dir" change_type refactor
    cat >> "$dir/P1-requirements.md" <<'EOF'
#### BDD-2: 关键路径行为不变
- Given 重构后的协议状态
- When 执行关键路径
- Then 行为与重构前一致
EOF
    cat > "$dir/P1-review.md" <<'EOF'
---
status: approved
agent: requirements-review
---
## BDD 评审
- BDD-1: PASS
- BDD-2: PASS
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P1 "$dir"
    [ "$status" -eq 2 ]
    echo '## P3 test cases（回归测试口径，不新增功能行为断言）' > "$dir/P3-test-cases.md"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P3 "$dir"
    [ "$status" -eq 2 ]
    cat > "$dir/P6-acceptance.md" <<'EOF'
---
phase: P6
task_id: TAG0002
agent: verifier
pass: 2
fail: 0
ui_affected: false
regression_pass: true
---
- PASS BDD-1: 全量回归全绿（重构后完整测试套件 0 失败）(P6-evidence/regression.log)
- PASS BDD-2: 关键路径行为不变（重构前后关键路径结果一致）(P6-evidence/regression.log)
EOF
    mkdir -p "$dir/P6-evidence"
    printf 'bats ... 0 failures\nEXIT_CODE: 0\n' > "$dir/P6-evidence/regression.log"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P6 "$dir"
    [ "$status" -eq 2 ]
}

@test "test_bdd_5_p6_card_docs_forbid_fake_functional_bdd" {
    # BDD-5: P6 验收口径文档明确禁止为凑验收数量新增功能性质 BDD（文档锚点测试）
    grep -q '禁止.*伪造' "$AGATE_ROOT/phase-cards/P6-acceptance.md"
}

@test "test_bdd_8_p3_card_docs_regression_test_port" {
    # BDD-8: P3 卡片含 refactor 回归测试口径说明（复用既有用例、不新增功能行为断言）——文档锚点测试
    grep -q '回归测试口径' "$AGATE_ROOT/phase-cards/P3-tdd.md"
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
debt_check: none
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
debt_check: none
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
debt_check: none
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
debt_check: none
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
debt_check: none
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

@test "G8.9 check-gate.sh P8 P8-release.md 缺 debt_check 字段 期望 exit 1" {
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
    [ "$status" -eq 1 ]
    [[ "$output" == *"debt_check"* ]]
}

@test "G8.10 check-gate.sh P8 debt_check 内容任意（debt_check: none）期望 exit 2 不阻断" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P8-release.md" <<'EOF'
bump_type: minor
debt_check: none
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
    [[ "$output" != *"debt_check"* ]]
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

@test "D-drift-5: dispatch-prompt.md 含'P3 自检'" {
    grep -q 'P3 自检' "$AGATE_ROOT/assets/templates/dispatch-prompt.md"
}

@test "D-drift-6: dispatch-prompt.md 含'修复轮派发追加'" {
    grep -q '修复轮派发追加' "$AGATE_ROOT/assets/templates/dispatch-prompt.md"
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
    add_p2_candidate_count "$dir" 2
    add_p2_review "$dir"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G_BDD10.1 BDD-10: check-gate.sh P2 candidate_count 在 frontmatter 与正文声明不同值时以 frontmatter 为准" {
    # T001 v2.0 流 A：正文出现同名字段 "candidate_count: 1"（不足 2，本应 exit 1），
    # 但 frontmatter 声明 candidate_count: 2（配合 2 个候选方案，应 exit 2）——
    # 断言最终判定与 frontmatter 一致，证明 frontmatter 优先于正文同名字段（不再走正则回退）。
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
candidate_count: 1
EOF
    add_p2_candidate_count "$dir" 2
    add_p2_review "$dir"
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
    add_p2_candidate_count "$dir" 2
    add_p2_review "$dir"
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
    add_p2_candidate_count "$dir" 2
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
    add_p2_candidate_count "$dir" 2
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
    add_p2_candidate_count "$dir" 2
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
    add_p2_candidate_count "$dir" 2
    add_p2_review "$dir"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G8.6 check-gate.sh P8 CHANGELOG_FILE 环境变量覆盖" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P8-release.md" <<'EOF'
bump_type: minor
debt_check: none
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
    add_p2_candidate_count "$dir" 2
    add_p2_review "$dir"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G_BDD9.1 BDD-9: check-gate.sh P2-design.md 旧格式（四字段仅在正文、frontmatter 无这些字段）仍被正确读取" {
    # T001 v2.0 流 A：在途任务旧格式（v0.35 正文内嵌）双读回退——P2-design.md frontmatter
    # 不含 packages/domains/ui_affected 时，门禁行为须与 v0.35 一致（正则回退）。
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
    add_p2_candidate_count "$dir" 2
    add_p2_review "$dir"
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
    add_p2_candidate_count "$dir" 2
    add_p2_review "$dir"
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

@test "G_SUGGEST.1 P1 含 [SUGGEST: X] 无阻塞项 → exit 2（不阻塞）" {
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
- [SUGGEST: 推荐方案 A，理由是更安全]
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
    [[ "$output" == *"SUGGEST"* ]]
    [[ "$output" != *"未解决的 NEED_CONFIRM 项（阻塞）"* ]]
}

@test "G_SUGGEST.2 P1 含 [SUGGEST: X] + [NEED_CONFIRM] → exit 1（阻塞项仍在）" {
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
- [SUGGEST: 推荐方案 A，理由是更安全]
- [NEED_CONFIRM] 需用户决策的方向
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
    [[ "$output" == *"阻塞"* ]]
}


@test "G_SUGGEST.3 P1 含旧标记 [NEED_CONFIRM倾向: X] → exit 1（typo 兜底：旧标记重命名）" {
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
- [NEED_CONFIRM倾向: 推荐方案 A]
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
    [[ "$output" == *"重命名为"* ]]
}

@test "G_SUGGEST.4 P1 含 [SUGGEST xxx]（漏冒号）→ exit 1（typo 兜底）" {
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
- [SUGGEST xxx]
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
    [[ "$output" == *"SUGGEST 格式不符"* ]]
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

# ========== TAG0004 M4/M6/RM-AG0001（BDD-11/14/28/29，TDD 红灯） ==========

@test "bdd-11 check-gate.sh P7 LC_ALL=C 全角冒号 [BLOCKER]：3 条 总结行不误计为阻塞（M4）" {
    local dir
    dir=$(create_task_dir --no-state-yaml)
    cat > "$dir/P7-consistency.md" <<'EOF'
- [BLOCKER]：3 条
EOF
    run env LC_ALL=C LANG= bash "$AGATE_SCRIPTS/check-gate.sh" P7 "$dir"
    # 修复前：[:：] bracket 在 POSIX locale 下不匹配全角冒号 → 总结行被计为真实 BLOCKER（exit 1）；修复后：exit 0
    [ "$status" -eq 0 ]
}

@test "bdd-14 check-gate.sh P1 CRLF 行尾 P1-review.md frontmatter 提取不失效（M6）" {
    local dir
    dir=$(create_task_dir --no-state-yaml)
    printf -- '---\r\nphase: P1\r\ntask_id: T001-test\r\nstatus: approved\r\nagent: requirements-review\r\n---\r\n## BDD 评审\r\n- BDD-1: PASS\r\n' > "$dir/P1-review.md"
    printf -- '---\r\nagent: test\r\nrisk_level: medium\r\nphases: [P1,P2,P3,P4,P5,P6,P7,P8]\r\n---\r\n- [NO_NEED_CONFIRM]\r\n' > "$dir/P1-requirements.md"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P1 "$dir"
    # 修复前：sed -n '/^---$/...' 对 CRLF 的 ---\r 不匹配 → status 提取为空 → exit 1；修复后：exit 2
    [ "$status" -eq 2 ]
}

@test "bdd-28 check-gate.sh P1 反引号包裹 [SUGGEST: ...] 计入 SUGGEST WARNING（RM-AG0001）" {
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
- `[SUGGEST: 推荐 X，理由 Y]`
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
    # 修复前：行首正则 ^\s*-?\s*\[SUGGEST: 不匹配反引号前缀 → 漏计（无 SUGGEST WARNING）；修复后：WARNING
    [[ "$output" == *"SUGGEST"* ]]
}

@test "bdd-29 check-gate.sh P1 反引号包裹 [NEED_CONFIRM] 判为未解决阻塞项（RM-AG0001）" {
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
- `[NEED_CONFIRM]` z 的边界条件需确认
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
    # 修复前：走"不合规格式"路径（消息不含"未解决的 NEED_CONFIRM"）；修复后：判未解决阻塞
    [[ "$output" == *"未解决的 NEED_CONFIRM"* ]]
}
