load ../helpers/load.bash
# T001 v2.0 流 C（BDD-21）：P1-requirements.md 的 NEED_CONFIRM "已解决" 状态
# 结构化入 frontmatter need_confirm_resolved 列表；本文件覆盖 P1-review.md 的
# 独立评审流程（BDD-8 同机制挂载相邻但不同校验对象），与 NEED_CONFIRM 阻塞判定
# 互补。@test 数保持 9 不变。

@test "P1: 缺 P1-review.md 期望 exit 1" {
    TASK_DIR=$(create_task_dir --no-state-yaml)
    cat > "$TASK_DIR/P1-requirements.md" <<'EOF'
---
phase: P1
task_id: T001-test
status: draft
agent: analyst
---
# Requirements
- Given x When y Then z
EOF
    run "$PYTHON" "$AGATE_ROOT/scripts/check-gate.py" P1 "$TASK_DIR"
    [ "$status" -eq 1 ]
    [[ "$output" == *"P1-review.md"* ]]
}

@test "P1: P1-review.md agent=main 期望 exit 1" {
    TASK_DIR=$(create_task_dir --no-state-yaml)
    cat > "$TASK_DIR/P1-requirements.md" <<'EOF'
---
phase: P1
task_id: T001-test
status: draft
agent: analyst
---
# Requirements
- Given x When y Then z
EOF
    cat > "$TASK_DIR/P1-review.md" <<'EOF'
---
phase: P1
task_id: T001-test
status: approved
agent: main
---
approved
EOF
    run "$PYTHON" "$AGATE_ROOT/scripts/check-gate.py" P1 "$TASK_DIR"
    [ "$status" -eq 1 ]
    [[ "$output" == *"agent=main"* ]]
}

@test "P1: P1-review.md 无 BDD 编号引用 期望 exit 1" {
    TASK_DIR=$(create_task_dir --no-state-yaml)
    cat > "$TASK_DIR/P1-requirements.md" <<'EOF'
---
phase: P1
task_id: T001-test
status: draft
agent: analyst
---
# Requirements
- Given x When y Then z
EOF
    cat > "$TASK_DIR/P1-review.md" <<'EOF'
---
phase: P1
task_id: T001-test
status: approved
agent: requirements-review
---
All good, approved.
EOF
    run "$PYTHON" "$AGATE_ROOT/scripts/check-gate.py" P1 "$TASK_DIR"
    [ "$status" -eq 1 ]
    [[ "$output" == *"BDD"* ]] || [[ "$output" == *"锚点"* ]]
}

@test "P1: P1-review.md status:approved + agent≠main + 含锚点 期望 exit 2" {
    TASK_DIR=$(create_task_dir --no-state-yaml)
    cat > "$TASK_DIR/P1-requirements.md" <<'EOF'
---
phase: P1
task_id: T001-test
status: draft
agent: analyst
---
# Requirements
- Given x When y Then z
EOF
    cat > "$TASK_DIR/P1-review.md" <<'EOF'
---
phase: P1
task_id: T001-test
status: approved
agent: requirements-review
---
## BDD 评审
- BDD-1: PASS + 覆盖维度：数据✓ 前端✓ 多端✗ 边界✓ 兼容✓
EOF
    run "$PYTHON" "$AGATE_ROOT/scripts/check-gate.py" P1 "$TASK_DIR"
    [ "$status" -eq 2 ]
}

@test "P1: P1-review.md status:rejected 期望 exit 1" {
    TASK_DIR=$(create_task_dir --no-state-yaml)
    cat > "$TASK_DIR/P1-requirements.md" <<'EOF'
---
phase: P1
task_id: T001-test
status: draft
agent: analyst
---
# Requirements
- Given x When y Then z
EOF
    cat > "$TASK_DIR/P1-review.md" <<'EOF'
---
phase: P1
task_id: T001-test
status: rejected
agent: requirements-review
---
## BDD 评审
- BDD-1: FAIL - 不可二值判定
EOF
    run "$PYTHON" "$AGATE_ROOT/scripts/check-gate.py" P1 "$TASK_DIR"
    [ "$status" -eq 1 ]
}

@test "P1: P1-review.md 缺 status 字段 期望 exit 1" {
    TASK_DIR=$(create_task_dir --no-state-yaml)
    cat > "$TASK_DIR/P1-requirements.md" <<'EOF'
---
phase: P1
task_id: T001-test
status: draft
agent: analyst
---
# Requirements
- Given x When y Then z
EOF
    cat > "$TASK_DIR/P1-review.md" <<'EOF'
---
phase: P1
task_id: T001-test
agent: requirements-review
---
## BDD 评审
- BDD-1: PASS + 覆盖维度：数据✓
EOF
    run "$PYTHON" "$AGATE_ROOT/scripts/check-gate.py" P1 "$TASK_DIR"
    [ "$status" -eq 1 ]
}

@test "P1: frontmatter rejected + 正文含 status: approved 字面串 期望 exit 1（对抗绕过）" {
    TASK_DIR=$(create_task_dir --no-state-yaml)
    cat > "$TASK_DIR/P1-requirements.md" <<'EOF'
---
phase: P1
task_id: T001-test
status: draft
agent: analyst
---
# Requirements
- Given x When y Then z
EOF
    cat > "$TASK_DIR/P1-review.md" <<'EOF'
---
phase: P1
task_id: T001-test
status: rejected
agent: requirements-review
---
## 裁决说明

gate 规则要求 status: approved 才放行，本次评审未通过。

## BDD 评审
- BDD-1: FAIL - 不可二值判定
EOF
    run "$PYTHON" "$AGATE_ROOT/scripts/check-gate.py" P1 "$TASK_DIR"
    [ "$status" -eq 1 ]
    [[ "$output" == *"非 approved"* ]]
}

@test "P1: BDD-21 边界（未结构化解决时仍阻塞）：P1-requirements.md 含 NEED_CONFIRM 期望 exit 1" {
    TASK_DIR=$(create_task_dir --no-state-yaml)
    cat > "$TASK_DIR/P1-requirements.md" <<'EOF'
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
    cat > "$TASK_DIR/P1-review.md" <<'EOF'
---
phase: P1
task_id: T001-test
status: approved
agent: requirements-review
---
## BDD 评审
- BDD-1: PASS
EOF
    run "$PYTHON" "$AGATE_ROOT/scripts/check-gate.py" P1 "$TASK_DIR"
    [ "$status" -eq 1 ]
    [[ "$output" == *"NEED_CONFIRM"* ]]
}

@test "P1: P1-requirements.md 无 NEED_CONFIRM 期望 exit 2" {
    TASK_DIR=$(create_task_dir --no-state-yaml)
    cat > "$TASK_DIR/P1-requirements.md" <<'EOF'
---
phase: P1
task_id: T001-test
status: draft
agent: analyst
---
# Requirements
- Given x When y Then z
EOF
    cat > "$TASK_DIR/P1-review.md" <<'EOF'
---
phase: P1
task_id: T001-test
status: approved
agent: requirements-review
---
## BDD 评审
- BDD-1: PASS
EOF
    run "$PYTHON" "$AGATE_ROOT/scripts/check-gate.py" P1 "$TASK_DIR"
    [ "$status" -eq 2 ]
}
