#!/usr/bin/env bats
# tests/unit/check-retrospective.bats — 4 用例覆盖 check-retrospective.py
# 计划：5.9 / 实际 4 行 / 与附录 A 一致
# 注意：此脚本总是 exit 0，测试只能断言 output 含特定模式

load ../helpers/load.bash

setup() {
    # TAG0009 BDD-16/17：harness shim——产品脚本内部裸 python3 在"仅 python 可解析"环境解析到真解释器
    local shim
    shim=$(create_python_shim_bin) || return 1
    if [ -n "$shim" ]; then
        export PATH="$shim:$PATH"
    fi
}

@test "RT.1 check-retrospective.py 无异常 期望 exit 0 + 无输出" {
    local dir
    dir=$(create_task_dir)
    run "$PYTHON" "$AGATE_SCRIPTS/check-retrospective.py" "$dir" "$dir/.state.yaml"
    [ "$status" -eq 0 ]
    # 无异常时输出为空
    [ -z "$output" ]
}

@test "RT.2 check-retrospective.py retries 超限 期望 exit 0 + 含'重试超限'" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/.state.yaml" <<'EOF'
task_id: T001
phase: PAUSED
status: active
retries:
  P2:
    - attempt: 1
    - attempt: 2
    - attempt: 3
EOF
    run "$PYTHON" "$AGATE_SCRIPTS/check-retrospective.py" "$dir" "$dir/.state.yaml"
    [ "$status" -eq 0 ]
    [[ "$output" == *"重试超限"* ]]
}

@test "RT_BDD21.1 BDD-21: check-gate.sh P1 frontmatter need_confirm_resolved 已覆盖具体描述时该 NEED_CONFIRM 项不再阻塞" {
    # T001 v2.0 流 C：NEED_CONFIRM 的"已解决/已确认"状态结构化入 P1 frontmatter
    # need_confirm_resolved 列表；逐条匹配正文每条 NEED_CONFIRM 描述是否已在该列表
    # 中找到对应项——已匹配则不阻塞，散文标记本身仍保留为人类痕迹。
    local dir
    dir=$(create_task_dir --no-state-yaml)
    cat > "$dir/P1-requirements.md" <<'EOF'
---
phase: P1
task_id: T001-test
status: draft
agent: analyst
need_confirm_resolved: ["z 的边界条件需确认"]
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
    run "$PYTHON" "$AGATE_SCRIPTS/check-gate.py" P1 "$dir"
    [ "$status" -eq 2 ]
}

# ========== P2.53: progress 文件排除 ==========

@test "RT.DP1: dispatch-prompt file excluded from SCOPE+ scan" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P4-dispatch-prompt-implementer.md" <<'EOF'
> render product
- [SCOPE+] this should be ignored
EOF
    run "$PYTHON" "$AGATE_SCRIPTS/check-retrospective.py" "$dir" "$dir/.state.yaml"
    [ "$status" -eq 0 ]
    [[ "$output" != *"SCOPE+"* ]]
}

@test "RT.4 check-retrospective.py override 触发 期望 exit 0 + 含'override'" {
    local dir
    dir=$(create_task_dir)
    sed -i '/^phases:/a override: P2 retained' "$dir/P1-requirements.md"
    run "$PYTHON" "$AGATE_SCRIPTS/check-retrospective.py" "$dir" "$dir/.state.yaml"
    [ "$status" -eq 0 ]
    [[ "$output" == *"override"* ]]
}

@test "RT.5 check-retrospective.py retries[P3]=2 触发超限（P3 MAX=2）" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/.state.yaml" <<'EOF'
task_id: T001
phase: PAUSED
status: active
retries:
  P3:
    - attempt: 1
    - attempt: 2
EOF
    run "$PYTHON" "$AGATE_SCRIPTS/check-retrospective.py" "$dir" "$dir/.state.yaml"
    [ "$status" -eq 0 ]
    [[ "$output" == *"重试超限"* ]]
}

@test "RT.6 check-retrospective.py retries[P3]=1 不触发（P3 MAX=2 未达）" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/.state.yaml" <<'EOF'
task_id: T001
phase: P4
status: active
retries:
  P3:
    - attempt: 1
EOF
    run "$PYTHON" "$AGATE_SCRIPTS/check-retrospective.py" "$dir" "$dir/.state.yaml"
    [ "$status" -eq 0 ]
    [ -z "$output" ]
}

# ========== 行首锚点 ==========

@test "RT.7 句中 [SCOPE+]（非行首）不触发复盘提醒 期望 exit 0 + 无输出" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
检查了 [SCOPE+] 的引用情况
EOF
    run "$PYTHON" "$AGATE_SCRIPTS/check-retrospective.py" "$dir" "$dir/.state.yaml"
    [ "$status" -eq 0 ]
    [ -z "$output" ]
}

# ========== dispatch-context / AGATE_CARD 排除 ==========

@test "RETRO_SCOPE_DC.1 dispatch-context 含 [SCOPE+] 不触发复盘提醒" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-dispatch-context-verifier.md" <<'EOF'
- [SCOPE+] 发现：新增功能需重新验收
EOF
    run "$PYTHON" "$AGATE_SCRIPTS/check-retrospective.py" "$dir" "$dir/.state.yaml"
    [ "$status" -eq 0 ]
    [[ "$output" != *"SCOPE+"* ]]
}

@test "RETRO_SCOPE_CARD.1 AGATE_CARD 块内 [SCOPE+] 不触发复盘提醒" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
设计内容
<!-- AGATE_CARD_START -->
- [SCOPE+] 示例：范围扩展
<!-- AGATE_CARD_END -->
正常设计
EOF
    run "$PYTHON" "$AGATE_SCRIPTS/check-retrospective.py" "$dir" "$dir/.state.yaml"
    [ "$status" -eq 0 ]
    [[ "$output" != *"SCOPE+"* ]]
}
