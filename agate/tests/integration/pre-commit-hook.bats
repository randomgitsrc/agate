#!/usr/bin/env bats
# tests/integration/pre-commit-hook.bats — 5 用例覆盖 pre-commit-gate.sh
# 计划：7.1 / 实际 5 行 / 与附录 A 一致
# T001 v2.0（BDD-8/23）：本文件属 integration/，P3 gate（unit+regression）不跑它，
# 由 P5/P6 验证。BDD-8 的 check-frontmatter.sh pre-commit 挂载点验证及 BDD-23
# 发现性标记（[SCOPE+]/[PROD_TOUCHED]/[DESIGN_GAP]）保持散文的回归覆盖见下方
# IT_PT_* / IT_PT_T6.* 系列（未改动，继续验证 v0.35 行为一致）。@test 数保持 42 不变。

load ../helpers/load.bash

# 注意：pre-commit-gate.sh 在 agate 仓库的 .git/hooks/ 下才生效
# 测试方法：把 hook 复制到临时 repo，触发 pre-commit，验证行为

setup() {
    REPO=$(git_init)
    cd "$REPO"
    # 安装 pre-commit hook
    HOOK_PATH="$REPO/.git/hooks/pre-commit"
    ln -sf "$AGATE_ROOT/scripts/pre-commit-gate.sh" "$HOOK_PATH"
    chmod +x "$HOOK_PATH"
}

_write_min_valid_dispatch_context() {
    local dir="$1" phase="$2" role="$3"
    cat > "$dir/${phase}-dispatch-context-${role}.md" << 'DCTPL'
---
phase: PH_PLACEHOLDER
generated_by: agate-next-card.sh + 主 Agent
task_id: T001
role: ROLE_PLACEHOLDER
---

<dispatch_guide>
### 目标
测试

### 约束
无

### 上游关联
无

### 输入文件
- agate-workspace/tasks/T001/P0-brief.md
</dispatch_guide>

<!-- AGATE_CARD_START -->
DCTPL
    "$PYTHON" "$AGATE_SCRIPTS/agate-next-card.py" "$phase" 2>/dev/null >> "$dir/${phase}-dispatch-context-${role}.md"
    cat >> "$dir/${phase}-dispatch-context-${role}.md" << 'DCTPL'
<!-- AGATE_CARD_END -->

<objective_info>
- 环境状态：正常
</objective_info>
DCTPL
    sed -i "s/PH_PLACEHOLDER/${phase}/" "$dir/${phase}-dispatch-context-${role}.md"
    sed -i "s/ROLE_PLACEHOLDER/${role}/" "$dir/${phase}-dispatch-context-${role}.md"
}

@test "IT.1 pre-commit-hook 无 .state.yaml 变更 不触发" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    # 首次 commit，.state.yaml 暂存列表里没有
    run git -C "$REPO" commit -m "init"
    # exit 0（hook 没拦）
    [ "$status" -eq 0 ]
}

@test "IT.2 pre-commit-hook phase 变更 + gate 通过" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    cat > "$REPO/.state.yaml" <<'EOF'
task_id: TXX0001
phase: P1
status: active
retries: {}
EOF
    mkdir -p "$REPO/agate-workspace/tasks/T001"
    cat > "$REPO/agate-workspace/tasks/T001/P1-requirements.md" <<'EOF'
---
agent: test
---
risk_level: medium
phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]
- Given test precondition
EOF
    cat > "$REPO/agate-workspace/tasks/T001/P1-review.md" <<'EOF'
---
phase: P1
task_id: TXX0001
status: approved
agent: requirements-review
---
## BDD 评审
- BDD-1: PASS + 覆盖维度：数据✓
EOF
    git -C "$REPO" add .state.yaml agate-workspace/tasks/T001/
    _write_min_valid_dispatch_context "agate-workspace/tasks/T001" "P1" "analyst"
    git -C "$REPO" add "agate-workspace/tasks/T001/P1-dispatch-context-analyst.md"
    run git -C "$REPO" commit -m "phase change to P1"
    [ "$status" -eq 0 ]
}

@test "IT.3 pre-commit-hook 句中提及 [PROD_TOUCHED]（非行首声明）→ 不中止（T090 修复）" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    # 创建任务目录 + 句中提及 [PROD_TOUCHED] 的产出文件
    mkdir -p "$REPO/agate-workspace/tasks/T001"
    echo "do something to production [PROD_TOUCHED]" > "$REPO/agate-workspace/tasks/T001/P5-verification.md"
    # 同时改 .state.yaml phase，触发 gate
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF'
task_id: TXX0001
phase: P5
status: active
retries: {}
EOF
    git -C "$REPO" add agate-workspace/tasks/T001/P5-verification.md agate-workspace/tasks/T001/.state.yaml
    run git -C "$REPO" commit -m "mention not declaration"
    [ "$status" -eq 0 ]
}

@test "IT.4 pre-commit-hook .state.yaml phase 变更触发 state-yaml 校验" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    # 故意写错格式的 .state.yaml
    cat > "$REPO/.state.yaml" <<'EOF'
task_id: T001a
phase: P1
EOF
    git -C "$REPO" add .state.yaml
    run git -C "$REPO" commit -m "bad state yaml"
    [ "$status" -ne 0 ]
    [[ "$output" == *"task_id 格式错误"* ]]
}

@test "IT.5 pre-commit-hook .state.yaml 格式校验（任何变更都触发）" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    # 任意 .state.yaml 变更（不一定是 phase）→ 也触发格式校验
    cat > "$REPO/.state.yaml" <<'EOF'
task_id: TXX0001
phase: P1
status: active
retries: {}
EOF
    git -C "$REPO" add .state.yaml
    # .state.yaml 格式正确 → commit 通过（因为没改 phase）
    run git -C "$REPO" commit -m "state format check"
    [ "$status" -eq 0 ]
}

# ========== 多任务架构测试 ==========

@test "IT.6 pre-commit-hook 多任务：任务级 .state.yaml + P1 产出 → 正常 commit" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/agate-workspace/tasks/T001"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF'
task_id: TXX0001
phase: P1
status: active
retries: {}
EOF
    cat > "$REPO/agate-workspace/tasks/T001/P1-requirements.md" <<'EOF'
---
agent: test
---
risk_level: medium
phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]
- Given test precondition
EOF
    cat > "$REPO/agate-workspace/tasks/T001/P1-review.md" <<'EOF'
---
phase: P1
task_id: TXX0001
status: approved
agent: requirements-review
---
## BDD 评审
- BDD-1: PASS + 覆盖维度：数据✓
EOF
    git -C "$REPO" add agate-workspace/tasks/T001/
    _write_min_valid_dispatch_context "agate-workspace/tasks/T001" "P1" "analyst"
    git -C "$REPO" add "agate-workspace/tasks/T001/P1-dispatch-context-analyst.md"
    run git -C "$REPO" commit -m "T001 P1"
    [ "$status" -eq 0 ]
}

@test "IT.7 pre-commit-hook 多任务：P4 产出但 phase 仍 P3 → WARNING 不拦截" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    # 先 commit 一个 P3 状态
    mkdir -p "$REPO/agate-workspace/tasks/T001"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P3
status: active
retries: {}
EOF
    cat > "$REPO/agate-workspace/tasks/T001/P1-requirements.md" <<'EOF'
---
agent: test
---
risk_level: medium
phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]
- Given test precondition
EOF
    git -C "$REPO" add agate-workspace/tasks/T001/
    git -C "$REPO" commit --no-verify -qm "T001 P3"
    # 现在 commit P4 产出但忘改 phase
    echo "implementation" > "$REPO/agate-workspace/tasks/T001/P4-implementation.md"
    git -C "$REPO" add agate-workspace/tasks/T001/P4-implementation.md
    run git -C "$REPO" commit -m "T001 P4 output only" 2>&1
    [ "$status" -eq 0 ]
    [[ "$output" == *"WARNING"* || "$output" == *"phase"* ]]
}

@test "IT.8 pre-commit-hook 多任务：phase 变更到 P2 但无 P2-design.md → 拦截" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/agate-workspace/tasks/T001"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF'
task_id: TXX0001
phase: P1
status: active
retries: {}
EOF
    cat > "$REPO/agate-workspace/tasks/T001/P1-requirements.md" <<'EOF'
---
agent: test
---
risk_level: medium
phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]
- Given test precondition
EOF
    cat > "$REPO/agate-workspace/tasks/T001/P1-review.md" <<'EOF'
---
phase: P1
task_id: TXX0001
status: approved
agent: requirements-review
---
## BDD 评审
- BDD-1: PASS + 覆盖维度：数据✓
EOF
    git -C "$REPO" add agate-workspace/tasks/T001/
    _write_min_valid_dispatch_context "agate-workspace/tasks/T001" "P1" "analyst"
    git -C "$REPO" add "agate-workspace/tasks/T001/P1-dispatch-context-analyst.md"
    git -C "$REPO" commit -qm "T001 P1"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF'
task_id: TXX0001
phase: P2
status: active
retries: {}
EOF
    git -C "$REPO" add agate-workspace/tasks/T001/.state.yaml
    run git -C "$REPO" commit -m "T001 phase P2" 2>&1
    [ "$status" -ne 0 ]
    [[ "$output" == *"P2-design.md 不存在"* || "$output" == *"P2 不可裁剪"* ]]
}

@test "IT.9 pre-commit-hook 多任务：裁剪跳阶 P2→P5 无 P3 产出（low 风险）→ 不拦截" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/agate-workspace/tasks/T001"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF'
task_id: TXX0001
phase: P2
status: active
retries: {}
EOF
    cat > "$REPO/agate-workspace/tasks/T001/P1-requirements.md" <<'EOF'
---
agent: test
---
risk_level: low
phases: [P0, P1, P2, P4, P5, P6, P7, P8]
跳过风险: 低
EOF
    cat > "$REPO/agate-workspace/tasks/T001/P2-design.md" <<'EOF'
---
agent: test
phase: P2
task_id: TXX0001
type: design
parent: P1-requirements.md
trace_id: T001-P2-20260708
status: approved
created: 2026-07-08
---
### 候选方案 A：方案一
### 候选方案 B：方案二
## 权衡
A 简单 B 稳健
candidate_count: 2
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    cat > "$REPO/agate-workspace/tasks/T001/P2-review.md" <<'EOF2'
---
status: approved
agent: reviewer-subagent
---
P2 review approved.
EOF2
    git -C "$REPO" add agate-workspace/tasks/T001/
    _write_min_valid_dispatch_context "agate-workspace/tasks/T001" "P2" "architect"
    git -C "$REPO" add "agate-workspace/tasks/T001/P2-dispatch-context-architect.md"
    git -C "$REPO" commit -qm "T001 P2"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF'
task_id: TXX0001
phase: P5
status: active
retries: {}
EOF
    cat > "$REPO/agate-workspace/tasks/T001/P5-verification.md" <<'EOF'
---
agent: test
---
EOF
    git -C "$REPO" add agate-workspace/tasks/T001/
    run git -C "$REPO" commit -m "T001 skip to P5"
    [ "$status" -eq 0 ]
}

@test "IT.9b pre-commit-hook 裁剪跳阶 P3 medium 风险 → 拦截（P1-8: 仅 low 可裁 P3）" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/agate-workspace/tasks/T001"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF'
task_id: TXX0001
phase: P2
status: active
retries: {}
EOF
    cat > "$REPO/agate-workspace/tasks/T001/P1-requirements.md" <<'EOF'
---
agent: test
---
risk_level: medium
phases: [P0, P1, P2, P4, P5, P6, P7, P8]
跳过风险: 低
EOF
    cat > "$REPO/agate-workspace/tasks/T001/P2-design.md" <<'EOF'
---
agent: test
phase: P2
task_id: TXX0001
type: design
parent: P1-requirements.md
trace_id: T001-P2-20260708
status: approved
created: 2026-07-08
---
### 候选方案 A：方案一
### 候选方案 B：方案二
## 权衡
A 简单 B 稳健
candidate_count: 2
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    cat > "$REPO/agate-workspace/tasks/T001/P2-review.md" <<'EOF2'
---
status: approved
agent: reviewer-subagent
---
P2 review approved.
EOF2
    git -C "$REPO" add agate-workspace/tasks/T001/
    _write_min_valid_dispatch_context "agate-workspace/tasks/T001" "P2" "architect"
    git -C "$REPO" add "agate-workspace/tasks/T001/P2-dispatch-context-architect.md"
    run git -C "$REPO" commit -m "T001 P2 medium skip P3"
    [ "$status" -ne 0 ]
    [[ "$output" == *"P3 不可裁剪"*"仅 low"* ]]
}

@test "IT.10 pre-commit-hook 向后兼容：根 .state.yaml 仍工作" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    cat > "$REPO/.state.yaml" <<'EOF'
task_id: TXX0001
phase: P1
status: active
retries: {}
EOF
    mkdir -p "$REPO/agate-workspace/tasks/T001"
    cat > "$REPO/agate-workspace/tasks/T001/P1-requirements.md" <<'EOF'
---
agent: test
---
risk_level: medium
phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]
- Given test precondition
EOF
    cat > "$REPO/agate-workspace/tasks/T001/P1-review.md" <<'EOF'
---
phase: P1
task_id: TXX0001
status: approved
agent: requirements-review
---
## BDD 评审
- BDD-1: PASS + 覆盖维度：数据✓
EOF
    git -C "$REPO" add .state.yaml agate-workspace/tasks/T001/
    _write_min_valid_dispatch_context "agate-workspace/tasks/T001" "P1" "analyst"
    git -C "$REPO" add "agate-workspace/tasks/T001/P1-dispatch-context-analyst.md"
    run git -C "$REPO" commit -m "root state P1"
    [ "$status" -eq 0 ]
}

@test "IT.11 pre-commit-hook P2 阶段暂存代码文件 → WARNING" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/agate-workspace/tasks/T001"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF'
task_id: TXX0001
phase: P2
status: active
retries: {}
EOF
    cat > "$REPO/agate-workspace/tasks/T001/P1-requirements.md" <<'EOF'
---
agent: test
---
risk_level: medium
phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]
- Given test precondition
EOF
    git -C "$REPO" add agate-workspace/tasks/T001/
    git -C "$REPO" commit --no-verify -qm "T001 P2 setup"
    echo "print('hello')" > "$REPO/hack.py"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF'
task_id: TXX0001
phase: P2
status: active
retries:
  P2:
    - round: 1
      failure_mode: test
EOF
    git -C "$REPO" add hack.py agate-workspace/tasks/T001/.state.yaml
    run bash -c "cd '$REPO' && bash '$AGATE_ROOT/scripts/pre-commit-gate.sh'" 2>&1 || true
    [[ "$output" == *"代码文件"* ]]
}

# ========== 标记二值声明：PROD_TOUCHED ==========

@test "IT_PT_BINARY.1 暂存 diff 含行首 [PROD_TOUCHED] 描述 → 中止 commit（步骤 1）" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/agate-workspace/tasks/T001"
    echo "[PROD_TOUCHED] 接触了生产环境：修改了线上配置" > "$REPO/agate-workspace/tasks/T001/P5-verification.md"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF'
task_id: TXX0001
phase: P5
status: active
retries: {}
EOF
    git -C "$REPO" add agate-workspace/tasks/T001/P5-verification.md agate-workspace/tasks/T001/.state.yaml
    run git -C "$REPO" commit -m "should fail"
    [ "$status" -ne 0 ]
    [[ "$output" == *"PROD_TOUCHED"* ]]
}

@test "IT_PT_BINARY.2 暂存 diff 含 [PROD_NOT_TOUCHED] → 不中止" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/agate-workspace/tasks/T001"
    echo "[PROD_NOT_TOUCHED]" > "$REPO/agate-workspace/tasks/T001/P5-verification.md"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF'
task_id: TXX0001
phase: P5
status: active
retries: {}
EOF
    git -C "$REPO" add agate-workspace/tasks/T001/P5-verification.md agate-workspace/tasks/T001/.state.yaml
    run git -C "$REPO" commit -m "should pass"
    [ "$status" -eq 0 ]
}

@test "IT_PT_BINARY.3 暂存 diff 含删除行 [PROD_TOUCHED] → 不中止（只扫 ^+ 行）" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/agate-workspace/tasks/T001"
    echo "[PROD_TOUCHED] 旧内容" > "$REPO/agate-workspace/tasks/T001/P5-verification.md"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P5
status: active
retries: {}
EOF
    git -C "$REPO" add agate-workspace/tasks/T001/P5-verification.md agate-workspace/tasks/T001/.state.yaml
    git -C "$REPO" commit --no-verify -qm "setup with PROD_TOUCHED"
    echo "clean content" > "$REPO/agate-workspace/tasks/T001/P5-verification.md"
    git -C "$REPO" add agate-workspace/tasks/T001/P5-verification.md
    run git -C "$REPO" commit -m "remove PROD_TOUCHED"
    [ "$status" -eq 0 ]
}

@test "IT_PT_BINARY.4 暂存 diff 含句中引用 [PROD_TOUCHED]（非行首声明）→ 不中止（T090 修复）" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/agate-workspace/tasks/T001"
    echo "无 [PROD_TOUCHED] 需要报告" > "$REPO/agate-workspace/tasks/T001/P5-verification.md"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF'
task_id: TXX0001
phase: P5
status: active
retries: {}
EOF
    git -C "$REPO" add agate-workspace/tasks/T001/P5-verification.md agate-workspace/tasks/T001/.state.yaml
    run git -C "$REPO" commit -m "should pass"
    [ "$status" -eq 0 ]
}

@test "IT_PT_BINARY.5 暂存 diff 含句中引用 [PROD_TOUCHED]（非行首声明）→ 不中止（T090 修复）" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/agate-workspace/tasks/T001"
    echo "检查了 [PROD_TOUCHED] 标记" > "$REPO/agate-workspace/tasks/T001/P5-verification.md"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF'
task_id: TXX0001
phase: P5
status: active
retries: {}
EOF
    git -C "$REPO" add agate-workspace/tasks/T001/P5-verification.md agate-workspace/tasks/T001/.state.yaml
    run git -C "$REPO" commit -m "should pass"
    [ "$status" -eq 0 ]
}

@test "IT_PT_BINARY.6 暂存 diff 既无正向也无负向 → 不中止 + 无 WARNING（步骤 3 静默通过）" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/agate-workspace/tasks/T001"
    echo "normal content without any marker" > "$REPO/agate-workspace/tasks/T001/P5-verification.md"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF'
task_id: TXX0001
phase: P5
status: active
retries: {}
EOF
    git -C "$REPO" add agate-workspace/tasks/T001/P5-verification.md agate-workspace/tasks/T001/.state.yaml
    run git -C "$REPO" commit -m "should pass"
    [ "$status" -eq 0 ]
    [[ "$output" != *"WARNING"* ]]
}

# ========== Phase-span WARNING 方向检查 ==========

@test "IT_PHASE_SPAN.1 新增 P1/P2 产出文件 phase=P3（历史产出晚提交）→ 不报 WARNING" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/agate-workspace/tasks/T001"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P3
status: active
retries: {}
EOF
    echo '## P3 test cases' > "$REPO/agate-workspace/tasks/T001/P3-test-cases.md"
    _write_min_valid_dispatch_context "agate-workspace/tasks/T001" "P3" "test-designer"
    git -C "$REPO" add agate-workspace/tasks/T001/
    git -C "$REPO" commit --no-verify -qm "T001 P3 setup"
    # Now add P1/P2 as late commits
    cat > "$REPO/agate-workspace/tasks/T001/P1-requirements.md" <<'EOF'
---
agent: test
---
risk_level: medium
phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]
- Given test precondition
EOF
    cat > "$REPO/agate-workspace/tasks/T001/P2-design.md" <<'EOF'
---
agent: test
phase: P2
task_id: T001
type: design
parent: P1-requirements.md
trace_id: T001-P2-20260708
status: approved
created: 2026-07-08
---
### 候选方案 A：方案一
EOF
    git -C "$REPO" add agate-workspace/tasks/T001/P1-requirements.md agate-workspace/tasks/T001/P2-design.md
    run git -C "$REPO" commit -m "T001 late commit P1/P2 outputs" 2>&1
    [ "$status" -eq 0 ]
    [[ "$output" != *"WARNING"*"P1"* ]]
    [[ "$output" != *"WARNING"*"P2"* ]]
}

@test "IT_PHASE_SPAN.2 已存在 P1 产出被重新暂存 phase=P3 → 报 WARNING（真实过期）" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/agate-workspace/tasks/T001"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P1
status: active
retries: {}
EOF
    cat > "$REPO/agate-workspace/tasks/T001/P1-requirements.md" <<'EOF'
---
agent: test
---
risk_level: medium
phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]
- Given test precondition
EOF
    git -C "$REPO" add agate-workspace/tasks/T001/
    git -C "$REPO" commit --no-verify -qm "T001 P1 setup"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P3
status: active
retries: {}
EOF
    echo '## P3 test cases' > "$REPO/agate-workspace/tasks/T001/P3-test-cases.md"
    git -C "$REPO" add agate-workspace/tasks/T001/.state.yaml agate-workspace/tasks/T001/P3-test-cases.md
    git -C "$REPO" commit --no-verify -qm "T001 P3 setup"
    echo "updated requirements" >> "$REPO/agate-workspace/tasks/T001/P1-requirements.md"
    git -C "$REPO" add agate-workspace/tasks/T001/P1-requirements.md
    run git -C "$REPO" commit -m "T001 modify P1 while phase=P3" 2>&1
    [ "$status" -eq 0 ]
    [[ "$output" == *"WARNING"*"P1"* ]]
}

@test "IT_PHASE_SPAN.3 新增 P4 产出文件 phase=P3（提前产出）→ 报 WARNING" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/agate-workspace/tasks/T001"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P3
status: active
retries: {}
EOF
    cat > "$REPO/agate-workspace/tasks/T001/P1-requirements.md" <<'EOF'
---
agent: test
---
risk_level: medium
phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]
- Given test precondition
EOF
    git -C "$REPO" add agate-workspace/tasks/T001/
    git -C "$REPO" commit --no-verify -qm "T001 P3 setup"
    echo "implementation" > "$REPO/agate-workspace/tasks/T001/P4-implementation.md"
    git -C "$REPO" add agate-workspace/tasks/T001/P4-implementation.md
    run git -C "$REPO" commit -m "T001 P4 output while phase=P3" 2>&1
    [ "$status" -eq 0 ]
    [[ "$output" == *"WARNING"*"P4"* ]]
}

@test "IT_PHASE_SPAN.4 多任务场景：T001 历史产出晚提交不 WARNING / T002 已存在产出修改报 WARNING / T003 提前产出报 WARNING" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    # T001: phase=P3, 新增 P1 产出（历史产出晚提交）→ 不 WARNING
    mkdir -p "$REPO/agate-workspace/tasks/T001"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P3
status: active
retries: {}
EOF
    cat > "$REPO/agate-workspace/tasks/T001/P1-requirements.md" <<'EOF'
---
agent: test
---
risk_level: medium
phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]
- Given test precondition
EOF
    cat > "$REPO/agate-workspace/tasks/T001/P2-design.md" <<'EOF'
---
agent: test
phase: P2
task_id: T001
type: design
parent: P1-requirements.md
trace_id: T001-P2-20260708
status: approved
created: 2026-07-08
---
### 候选方案 A：方案一
EOF
    cat > "$REPO/agate-workspace/tasks/T001/P3-test-cases.md" <<'EOF'
---
agent: test
---
test cases
EOF
    cat > "$REPO/agate-workspace/tasks/T001/P1-review.md" <<'EOF'
---
phase: P1
task_id: T001
status: approved
agent: requirements-review
---
## BDD 评审
- BDD-1: PASS + 覆盖维度：数据✓
EOF
    git -C "$REPO" add agate-workspace/tasks/T001/
    _write_min_valid_dispatch_context "agate-workspace/tasks/T001" "P3" "test-designer"
    git -C "$REPO" add "agate-workspace/tasks/T001/P3-dispatch-context-test-designer.md"
    git -C "$REPO" commit --no-verify -qm "T001 P3 setup"
    # T002: phase=P3, 已存在 P1 产出被修改 → WARNING
    mkdir -p "$REPO/agate-workspace/tasks/T002"
    cat > "$REPO/agate-workspace/tasks/T002/.state.yaml" <<'EOF'
task_id: T002
phase: P1
status: active
retries: {}
EOF
    cat > "$REPO/agate-workspace/tasks/T002/P1-requirements.md" <<'EOF'
---
agent: test
---
risk_level: medium
phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]
- Given test precondition
EOF
    git -C "$REPO" add agate-workspace/tasks/T002/
    git -C "$REPO" commit --no-verify -qm "T002 P1 setup"
    cat > "$REPO/agate-workspace/tasks/T002/.state.yaml" <<'EOF'
task_id: T002
phase: P3
status: active
retries: {}
EOF
    echo '## P3 test cases' > "$REPO/agate-workspace/tasks/T002/P3-test-cases.md"
    git -C "$REPO" add agate-workspace/tasks/T002/.state.yaml agate-workspace/tasks/T002/P3-test-cases.md
    git -C "$REPO" commit --no-verify -qm "T002 P3 setup"
    echo "updated" >> "$REPO/agate-workspace/tasks/T002/P1-requirements.md"
    # T003: phase=P3, 新增 P4 产出（提前产出）→ WARNING
    mkdir -p "$REPO/agate-workspace/tasks/T003"
    cat > "$REPO/agate-workspace/tasks/T003/.state.yaml" <<'EOF'
task_id: T003
phase: P3
status: active
retries: {}
EOF
    cat > "$REPO/agate-workspace/tasks/T003/P1-requirements.md" <<'EOF'
---
agent: test
---
risk_level: medium
phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]
- Given test precondition
EOF
    echo '## P3 test cases' > "$REPO/agate-workspace/tasks/T003/P3-test-cases.md"
    git -C "$REPO" add agate-workspace/tasks/T003/
    git -C "$REPO" commit --no-verify -qm "T003 P3 setup"
    echo "implementation" > "$REPO/agate-workspace/tasks/T003/P4-implementation.md"
    git -C "$REPO" add agate-workspace/tasks/T002/P1-requirements.md agate-workspace/tasks/T003/P4-implementation.md
    run git -C "$REPO" commit -m "multi-task phase-span" 2>&1
    [ "$status" -eq 0 ]
    [[ "$output" != *"WARNING"*"T001"*"P1"* ]]
    [[ "$output" == *"WARNING"*"P1"* ]]
    [[ "$output" == *"WARNING"*"P4"* ]]
}

@test "IT_PHASE_SPAN.5 phase=PAUSED 暂存阶段号不符文件 → 不崩溃、报 WARNING、无 integer expression expected" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/agate-workspace/tasks/T001"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF'
task_id: TXX0001
phase: PAUSED
status: active
retries: {}
EOF
    cat > "$REPO/agate-workspace/tasks/T001/P1-requirements.md" <<'EOF'
---
agent: test
---
risk_level: medium
phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]
- Given test precondition
EOF
    git -C "$REPO" add agate-workspace/tasks/T001/
    run git -C "$REPO" commit -m "T001 PAUSED with P1 output" 2>&1
    [ "$status" -eq 0 ]
    [[ "$output" != *"integer expression expected"* ]]
}

# ========== 标记二值声明：PROD_TOUCHED ==========

@test "IT_PT_BINARY.7 暂存 diff 含 [PROD_NOT_TOUCHED] 确认未接触（负向+描述）→ 不中止" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/agate-workspace/tasks/T001"
    echo "[PROD_NOT_TOUCHED] 确认未接触" > "$REPO/agate-workspace/tasks/T001/P5-verification.md"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF'
task_id: TXX0001
phase: P5
status: active
retries: {}
EOF
    git -C "$REPO" add agate-workspace/tasks/T001/P5-verification.md agate-workspace/tasks/T001/.state.yaml
    run git -C "$REPO" commit -m "should pass"
    [ "$status" -eq 0 ]
}

@test "IT_PT_MENTION.1 正文句中提及 [PROD_TOUCHED]（非行首声明）→ 不误报（T090 修复）" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/agate-workspace/tasks/T001"
    echo "说明：本任务无生产接触，不需要写 [PROD_TOUCHED] 声明" > "$REPO/agate-workspace/tasks/T001/P5-verification.md"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF'
task_id: TXX0001
phase: P5
status: active
retries: {}
EOF
    git -C "$REPO" add agate-workspace/tasks/T001/P5-verification.md agate-workspace/tasks/T001/.state.yaml
    run git -C "$REPO" commit -m "mention not declaration"
    [ "$status" -eq 0 ]
}

# ========== P6 self-authored gate 代码直改硬拦截 ==========

@test "IT_P6_CODE.1 phase=P6，暂存 P6-evidence/ 下截图 → 不拦（证据文件例外）" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/agate-workspace/tasks/T001/P6-evidence/screenshots"
    touch "$REPO/agate-workspace/tasks/T001/P6-evidence/screenshots/a.png"
    echo "- PASS BDD-1: ok (screenshots/a.png)" > "$REPO/agate-workspace/tasks/T001/P6-acceptance.md"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF2'
task_id: T001
phase: P6
status: active
retries: {}
EOF2
    _write_min_valid_dispatch_context "$REPO/agate-workspace/tasks/T001" "P6" "verifier"
    git -C "$REPO" add agate-workspace/tasks/T001/
    run git -C "$REPO" commit -m "p6 evidence only"
    [[ "$output" != *"暂存了项目源码"* ]]
    [[ "$output" != *"不应直接改代码"* ]]
}

@test "IT_P6_CODE.1b phase=P6，暂存 evidences/ 下截图 → 不拦（T090 白名单修复）" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/agate-workspace/tasks/T001/evidences"
    touch "$REPO/agate-workspace/tasks/T001/evidences/desktop.png"
    echo "- PASS BDD-1: ok (screenshots/a.png)" > "$REPO/agate-workspace/tasks/T001/P6-acceptance.md"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF2'
task_id: T001
phase: P6
status: active
retries: {}
EOF2
    _write_min_valid_dispatch_context "$REPO/agate-workspace/tasks/T001" "P6" "verifier"
    git -C "$REPO" add agate-workspace/tasks/T001/
    run git -C "$REPO" commit -m "evidences dir only"
    [[ "$output" != *"暂存了项目源码"* ]]
    [[ "$output" != *"不应直接改代码"* ]]
}

@test "IT_P6_CODE.2 phase=P6，暂存项目源码文件 → exit 1 硬拦截" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/agate-workspace/tasks/T001/P6-evidence/screenshots" "$REPO/src"
    touch "$REPO/agate-workspace/tasks/T001/P6-evidence/screenshots/a.png"
    echo "- PASS BDD-1: ok (screenshots/a.png)" > "$REPO/agate-workspace/tasks/T001/P6-acceptance.md"
    echo "print('fix')" > "$REPO/src/app.py"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF2'
task_id: TXX0001
phase: P6
status: active
retries: {}
EOF2
    _write_min_valid_dispatch_context "$REPO/agate-workspace/tasks/T001" "P6" "verifier"
    git -C "$REPO" add src/app.py agate-workspace/tasks/T001/
    run git -C "$REPO" commit -m "should be blocked"
    [ "$status" -ne 0 ]
    [[ "$output" == *"不应直接改代码"* ]]
}

@test "IT_P6_CODE.3 phase=P4，暂存源码文件 → 不拦（回归）" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/agate-workspace/tasks/T001" "$REPO/src"
    echo "print('impl')" > "$REPO/src/app.py"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF2'
task_id: T001
phase: P4
status: active
retries: {}
EOF2
    git -C "$REPO" add src/app.py agate-workspace/tasks/T001/.state.yaml
    run git -C "$REPO" commit -m "p4 impl"
    [[ "$output" != *"不应直接改代码"* ]]
}

@test "IT_P6_CODE.4 phase=P5，暂存源码文件 → 不拦（回归）" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/agate-workspace/tasks/T001" "$REPO/src"
    echo "print('fix')" > "$REPO/src/app.py"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF2'
task_id: T001
phase: P5
status: active
retries: {}
EOF2
    git -C "$REPO" add src/app.py agate-workspace/tasks/T001/.state.yaml
    run git -C "$REPO" commit -m "p5 fix"
    [[ "$output" != *"不应直接改代码"* ]]
}

@test "IT_P6_CODE.5 phase=P2，暂存源码文件 → WARNING 而非硬拦截（回归，现有行为不变）" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/agate-workspace/tasks/T001" "$REPO/src"
    echo "print('early')" > "$REPO/src/app.py"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF2'
task_id: TXX0001
phase: P2
status: active
retries: {}
EOF2
    git -C "$REPO" add src/app.py agate-workspace/tasks/T001/.state.yaml
    run git -C "$REPO" commit -m "p2 early code"
    [[ "$output" == *"是否在非实现阶段直接改代码"* ]]
    [[ "$output" != *"不应直接改代码"* ]]
}

# ========== agate-retreat-to.sh 与真实 pre-commit hook 的集成 ==========

@test "IT_RETREAT.1 agate-retreat-to.sh 在装了真实 hook 的仓库里，每一步都真的过 hook 校验" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/agate-workspace/tasks/T001/P6-evidence/screenshots"
    echo "- PASS BDD-1: ok (screenshots/x.png)" > "$REPO/agate-workspace/tasks/T001/P6-acceptance.md"
    touch "$REPO/agate-workspace/tasks/T001/P6-evidence/screenshots/x.png"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF2'
task_id: TXX0001
phase: P6
status: active
retries: {}
EOF2
    _write_min_valid_dispatch_context "$REPO/agate-workspace/tasks/T001" "P6" "verifier"
    git -C "$REPO" add agate-workspace/tasks/T001/
    git -C "$REPO" commit -qm "setup P6 state"

    run bash -c "cd '$REPO' && bash '$AGATE_SCRIPTS/agate-retreat-to.sh' agate-workspace/tasks/T001 P4 '集成测试诊断'"
    [ "$status" -eq 0 ]
    [[ "$output" == *"共 2 步"* ]]

    # 关键：确认每一步 commit 真的经过了装好的 hook（而不是绕过了 hook）——
    # 用 hook 里必定会打印的一段特征文本来确认 hook 真的跑过
    run bash -c "cd '$REPO' && git log -p -2 --format=''"
    run bash -c "cd '$REPO' && git log --oneline"
    [[ "$output" == *"retreat: P6 -> P5"* ]]
    [[ "$output" == *"retreat: P5 -> P4"* ]]
}

@test "IT_RETREAT.2 中途一步的 commit 被 hook 拒绝时，agate-retreat-to.sh 明确报告停在哪步且不继续" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/agate-workspace/tasks/T001/P6-evidence/screenshots"
    echo "- PASS BDD-1: ok (screenshots/x.png)" > "$REPO/agate-workspace/tasks/T001/P6-acceptance.md"
    touch "$REPO/agate-workspace/tasks/T001/P6-evidence/screenshots/x.png"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF2'
task_id: TXX0001
phase: P6
status: active
retries: {}
EOF2
    _write_min_valid_dispatch_context "$REPO/agate-workspace/tasks/T001" "P6" "verifier"
    git -C "$REPO" add agate-workspace/tasks/T001/
    git -C "$REPO" commit -qm "setup P6 state"

    # 故意在工作区留一个行首 [PROD_TOUCHED] 声明的文件（真声明，phase 无关，
    # 会被 pre-commit-gate.sh 的一值声明步骤 1 硬拦截）。agate-retreat-to.sh 的
    # git add "$TASK_DIR" 会在第一步（P6->P5）把它一并带上，验证中途拒绝时脚本
    # 能正确报告"已停在 P6"且不会继续尝试后续步骤
    echo "[PROD_TOUCHED] 意外接触了生产环境" > "$REPO/agate-workspace/tasks/T001/note.md"

    run bash -c "cd '$REPO' && bash '$AGATE_SCRIPTS/agate-retreat-to.sh' agate-workspace/tasks/T001 P4 '集成测试：中途拒绝'"
    [ "$status" -eq 1 ]
    [[ "$output" == *"未通过 pre-commit hook 校验"* ]]
    [[ "$output" == *"已停在 P6"* ]]

    # 确认没有任何一步真的成功提交（P6 仍是当前 phase，没有 retreat commit 落地）
    run bash -c "cd '$REPO' && git log --oneline"
    [[ "$output" != *"retreat:"* ]]
}

# ========== T6: PROD_TOUCHED 步骤2 不再误拦 AGATE_CARD 注入文本 ==========

@test "IT_PT_T6.1 P8 dispatch-context 含 AGATE_CARD 注入块（[PROD_TOUCHED] 说明文本）→ 不误拦" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/agate-workspace/tasks/T001"
    _write_min_valid_dispatch_context "$REPO/agate-workspace/tasks/T001" "P8" "releaser"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF2'
task_id: T001
phase: P8
status: active
retries: {}
EOF2
    git -C "$REPO" add agate-workspace/tasks/T001/
    run git -C "$REPO" commit -m "p8 dispatch-context with AGATE_CARD"
    [[ "$output" != *"不合规的 PROD_TOUCHED"* ]]
    [[ "$output" != *"检测到生产环境接触"* ]]
}

@test "IT_PT_T6.2 任务产出文件含句中 [PROD_TOUCHED]（非 AGATE_CARD 块内）→ 不拦截（T090 修复）" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/agate-workspace/tasks/T001"
    echo "记录：曾经不小心碰到了 [PROD_TOUCHED] 生产环境" > "$REPO/agate-workspace/tasks/T001/note.md"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF2'
task_id: TXX0001
phase: P5
status: active
retries: {}
EOF2
    git -C "$REPO" add agate-workspace/tasks/T001/
    run git -C "$REPO" commit -m "mention not declaration"
    [ "$status" -eq 0 ]
}

@test "IT_PT_T6.3 任务产出文件含行首 [PROD_TOUCHED]（步骤1）→ 拦截（回归）" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/agate-workspace/tasks/T001"
    echo "[PROD_TOUCHED] 意外接触生产环境" > "$REPO/agate-workspace/tasks/T001/note.md"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF2'
task_id: TXX0001
phase: P5
status: active
retries: {}
EOF2
    git -C "$REPO" add agate-workspace/tasks/T001/
    run git -C "$REPO" commit -m "should be blocked"
    [ "$status" -ne 0 ]
    [[ "$output" == *"检测到生产环境接触"* ]]
}

@test "IT_PT_T6.4 任务产出文件含 [PROD_NOT_TOUCHED]（负向声明）→ 不拦截（回归）" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/agate-workspace/tasks/T001"
    echo "[PROD_NOT_TOUCHED] 未接触生产环境" > "$REPO/agate-workspace/tasks/T001/note.md"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF2'
task_id: T001
phase: P5
status: active
retries: {}
EOF2
    git -C "$REPO" add agate-workspace/tasks/T001/
    run git -C "$REPO" commit -m "should not be blocked by PROD_TOUCHED check"
    [[ "$output" != *"不合规的 PROD_TOUCHED"* ]]
    [[ "$output" != *"检测到生产环境接触"* ]]
}

# ========== P2.54: CHANGELOG 检查限制到 P8 ==========

@test "IT_CHANGELOG_P54: P4 commit without CHANGELOG → no CHANGELOG WARNING" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-p54")
    git -C "$repo" commit -q --allow-empty -m "init"
    mkdir -p "$repo/agate-workspace/tasks/T001"
    cat > "$repo/agate-workspace/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P4
status: active
retries: {}
EOF
    cat > "$repo/CHANGELOG.md" <<'EOF'
# Changelog

## [Unreleased]

### Fixed
- T999: other task
EOF
    echo 'task: test' > "$repo/agate-workspace/tasks/T001/P0-brief.md"
    git -C "$repo" add agate-workspace/tasks/T001/.state.yaml agate-workspace/tasks/T001/P0-brief.md
    run bash -c "cd '$repo' && bash '$AGATE_ROOT/scripts/pre-commit-gate.sh'" 2>&1 || true
    [[ "$output" != *"CHANGELOG"* ]]
}

@test "IT_CHANGELOG_P54b: P8 commit without CHANGELOG → CHANGELOG WARNING" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-p54b")
    git -C "$repo" commit -q --allow-empty -m "init"
    mkdir -p "$repo/agate-workspace/tasks/T001"
    cat > "$repo/agate-workspace/tasks/T001/.state.yaml" <<'EOF'
task_id: TXX0001
phase: P8
status: active
retries: {}
EOF
    cat > "$repo/CHANGELOG.md" <<'EOF'
# Changelog

## [Unreleased]

### Fixed
- T999: other task
EOF
    echo 'task: test' > "$repo/agate-workspace/tasks/T001/P0-brief.md"
    git -C "$repo" add agate-workspace/tasks/T001/.state.yaml agate-workspace/tasks/T001/P0-brief.md
    run bash -c "cd '$repo' && bash '$AGATE_ROOT/scripts/pre-commit-gate.sh'" 2>&1 || true
    [[ "$output" == *"CHANGELOG"* ]]
}

@test "IT_GATE_REAL.1: hook runs check-gate.sh and writes real .gate-result.json" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-gatereal1")
    ln -sf "$AGATE_ROOT/scripts/pre-commit-gate.sh" "$repo/.git/hooks/pre-commit"
    chmod +x "$repo/.git/hooks/pre-commit"
    mkdir -p "$repo/agate-workspace/tasks/T001"
    cat > "$repo/agate-workspace/tasks/T001/.state.yaml" <<'EOF'
task_id: TXX0001
phase: P2
status: active
retries: {}
EOF
    cat > "$repo/agate-workspace/tasks/T001/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：方案一
### 候选方案 B：方案二
## 权衡
A 更简单，B 更稳健。
candidate_count: 2
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    cat > "$repo/agate-workspace/tasks/T001/P2-review.md" <<'EOF'
---
agent: test
status: approved
---
通过。
EOF
    # embed real card content via agate-next-card.py
    local card_content
    card_content=$("$PYTHON" "$AGATE_ROOT/scripts/agate-next-card.py" P2 2>/dev/null || true)
    cat > "$repo/agate-workspace/tasks/T001/P2-dispatch-context-architect.md" <<EOF
---
agent: test
---
## 任务
设计 P2

<!-- AGATE_CARD_START -->
$card_content
<!-- AGATE_CARD_END -->
EOF
    git -C "$repo" add agate-workspace/tasks/T001/
    run git -C "$repo" commit -m "P2"
    [ "$status" -eq 0 ]
    [ -f "$repo/.gate-result.json" ]
    grep -q 'pre-commit-hook' "$repo/.gate-result.json"
}

@test "HOOK_EVIDENCE_WARNING: P6 截图触发低方差 WARNING → commit 不应被拦截（T086 修复）" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-evid-warn")
    HOOK_PATH="$repo/.git/hooks/pre-commit"
    ln -sf "$AGATE_ROOT/scripts/pre-commit-gate.sh" "$HOOK_PATH"
    chmod +x "$HOOK_PATH"
    mkdir -p "$repo/agate-workspace/tasks/T086"
    cat > "$repo/agate-workspace/tasks/T086/.state.yaml" <<EOF2
task_id: TXX0086
phase: P6
status: active
retries: {}
EOF2
    cat > "$repo/agate-workspace/tasks/T086/P6-acceptance.md" <<EOF2
---
agent: test
---
- PASS BDD-1 (screenshots/test.png)
EOF2
    cat > "$repo/agate-workspace/tasks/T086/P2-design.md" <<EOF2
---
agent: test
---
ui_affected: true
EOF2
    mkdir -p "$repo/agate-workspace/tasks/T086/P6-evidence/screenshots"
    # 生成 100x100 极低方差图（全浅色，variance=0，触发 WARNING）
    $PYTHON -c "
import struct, zlib
w, h = 100, 100
raw = b'\x00' + b'\xff\xff\xff' * w
raw = raw * h
ihdr = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
idat = zlib.compress(ihdr + raw if False else raw)
def chunk(typ, data):
    return struct.pack('>I', len(data)) + typ + data + struct.pack('>I', zlib.crc32(typ + data) & 0xffffffff)
png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) + chunk(b'IDAT', idat) + chunk(b'IEND', b'')
import sys; sys.stdout.buffer.write(png)
" > "$repo/agate-workspace/tasks/T086/P6-evidence/screenshots/test.png"
    # 写 dispatch-context 模板 + 注入 P6 卡片（与现有 helper 一致）
    cat > "$repo/agate-workspace/tasks/T086/P6-dispatch-context-verifier.md" <<DCEND
---
phase: P6
generated_by: agate-next-card.sh + 主 Agent
task_id: TXX0086
role: verifier
---

<!-- AGATE_CARD_START -->
<!-- AGATE_CARD_END -->
DCEND
    "$PYTHON" "$AGATE_ROOT/scripts/agate-inject-card.py" P6 "$repo/agate-workspace/tasks/T086"
    git -C "$repo" add agate-workspace/tasks/T086/
    # 不绕过 hook — 期望 commit 成功（exit 0），不因 WARNING 拦截
    run git -C "$repo" -c user.name=test -c user.email=test@test commit -m "T086 evidence warning test"
    [ "$status" -eq 0 ]
    [[ "$output" == *"WARNING"* ]]
}

@test "pre-commit hook: AGATE_ROOT 未设时自定位到脚本自身本体（worktree 支持，T086）" {
    local repo workflow_root
    # Windows Git Bash 的 ln -sf 退化为复制（无 POSIX 软链语义），readlink 自定位无法验证
    # ——worktree 软链 hook 自定位是 POSIX 特性，Windows 上由 install-hook 复制模式 + .agate-root 标记兜底
    if [[ "$(uname -s)" == *MINGW* || "$(uname -s)" == *MSYS* ]]; then
        skip "Windows 无 POSIX 软链，软链 hook 自定位场景无法验证（install-hook 复制模式已覆盖 Windows 语义）"
    fi
    repo=$(git_init)

    # 模拟 worktree：隔离协议本体目录
    workflow_root="$BATS_TEST_TMPDIR/workflow-root"
    mkdir -p "$workflow_root/scripts"
    cp "$AGATE_ROOT/scripts/pre-commit-gate.sh" "$workflow_root/scripts/"
    chmod +x "$workflow_root/scripts/pre-commit-gate.sh"

    # 隔离本体的 gate-result.sh：被 source 时打印标记（主 checkout 版不打印）
    cat > "$workflow_root/scripts/gate-result.sh" <<'EOF'
# 隔离本体专用 gate-result.sh -- 被 source 时打印 WORKTREE_SOURCED 标记
echo "WORKTREE_SOURCED"
EOF

    # 构造最小可 gate 场景（P1 阶段，无 P1-review.md -> 会走 gate-result 加载路径）
    mkdir -p "$repo/agate-workspace/tasks/TX/workflow-test"
    cat > "$repo/agate-workspace/tasks/TX/workflow-test/.state.yaml" <<EOF
task_id: TX
phase: P1
status: active
retries: {}
EOF

    # 模拟真实 worktree hook 场景：hook 是软链 -> 隔离本体的 pre-commit-gate.sh
    ln -sf "$workflow_root/scripts/pre-commit-gate.sh" "$repo/.git/hooks/pre-commit"

    # 不设 AGATE_ROOT，通过软链运行 -> 应自定位到隔离本体，source 到带标记的 gate-result.sh
    run bash -c "unset AGATE_ROOT; cd '$repo' && bash '$repo/.git/hooks/pre-commit' 2>&1"

    [[ "$output" == *"WORKTREE_SOURCED"* ]]
}

# ========== TAG0004 S1 空格路径 fail-open 修复（BDD-1/2/3/4）+ M9（BDD-17）+ 复制模式（BDD-19） ==========
# TDD 红灯：以下用例在修复实现前应红（S1 空格切词 fail-open / M9 正则元字符静默绕过 / BDD-19 复制模式 AGATE_ROOT 解析失败）。
# 参照：IT.2（合法 P1 全流程）、IT.4（task_id 格式错误）。

@test "bdd-1 pre-commit-gate 空格路径任务 gate 实际不通过时拦截（S1 fail-open 修复）" {
    echo init > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm init
    # 任务目录路径含空格 + 该阶段 gate 实际不通过（P1 缺 P1-review.md）
    mkdir -p "$REPO/agate-workspace/tasks/Task Space"
    cat > "$REPO/agate-workspace/tasks/Task Space/.state.yaml" <<'EOF'
task_id: TXX0001
phase: P1
status: active
retries: {}
EOF
    git -C "$REPO" add "agate-workspace/tasks/Task Space/.state.yaml"
    run git -C "$REPO" commit -m "space path gate fail"
    # 修复前：空格切词 → 该 .state.yaml 被静默跳过 → fail-open（exit 0）；修复后：gate 拦截（exit 1）
    [ "$status" -eq 1 ]
}

@test "bdd-2 pre-commit-gate 多个 .state.yaml 含空格路径逐个处理（不因切词丢失文件）" {
    echo init > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm init
    # 正常路径任务：.state.yaml 格式合法（phase=P0，gate exit 2 手动判定不阻塞）
    mkdir -p "$REPO/agate-workspace/tasks/T001"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF'
task_id: TXX0001
phase: P0
status: active
retries: {}
EOF
    git -C "$REPO" add agate-workspace/tasks/T001/.state.yaml
    # 空格路径任务：.state.yaml 格式非法（task_id 格式错）→ 格式校验应拦截
    mkdir -p "$REPO/agate-workspace/tasks/Task Space"
    cat > "$REPO/agate-workspace/tasks/Task Space/.state.yaml" <<'EOF'
task_id: T001a
phase: P0
status: active
retries: {}
EOF
    git -C "$REPO" add "agate-workspace/tasks/Task Space/.state.yaml"
    run git -C "$REPO" commit -m "space state invalid"
    # 修复前：空格任务被跳过 → 格式校验不触发 → exit 0；修复后：exit 1
    [ "$status" -eq 1 ]
}

@test "bdd-3 pre-commit-gate 空格目录 PROCESSED_DIRS 不拆段 gate 正常执行（输出含 GATE P1）" {
    echo init > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm init
    mkdir -p "$REPO/agate-workspace/tasks/Task Space"
    cat > "$REPO/agate-workspace/tasks/Task Space/.state.yaml" <<'EOF'
task_id: TXX0001
phase: P1
status: active
retries: {}
EOF
    cat > "$REPO/agate-workspace/tasks/Task Space/P1-requirements.md" <<'EOF'
---
agent: test
---
risk_level: medium
phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]
- Given test precondition
EOF
    cat > "$REPO/agate-workspace/tasks/Task Space/P1-review.md" <<'EOF'
---
phase: P1
task_id: TXX0001
status: approved
agent: requirements-review
---
## BDD 评审
- BDD-1: PASS
EOF
    git -C "$REPO" add "agate-workspace/tasks/Task Space/"
    _write_min_valid_dispatch_context "agate-workspace/tasks/Task Space" "P1" "analyst"
    git -C "$REPO" add "agate-workspace/tasks/Task Space/P1-dispatch-context-analyst.md"
    run git -C "$REPO" commit -m "space valid P1"
    [ "$status" -eq 0 ]
    # 修复前：主循环空格切词跳过 → 该任务 gate 从未执行（输出无 GATE P1）；修复后：gate 正常执行
    [[ "$output" == *"GATE P1"* ]]
}

@test "bdd-4 pre-commit-gate 无空格路径单任务 gate 行为不变（Linux 回归）" {
    echo init > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm init
    mkdir -p "$REPO/agate-workspace/tasks/T001"
    cat > "$REPO/agate-workspace/tasks/T001/.state.yaml" <<'EOF'
task_id: TXX0001
phase: P1
status: active
retries: {}
EOF
    cat > "$REPO/agate-workspace/tasks/T001/P1-requirements.md" <<'EOF'
---
agent: test
---
risk_level: medium
phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]
- Given test precondition
EOF
    cat > "$REPO/agate-workspace/tasks/T001/P1-review.md" <<'EOF'
---
phase: P1
task_id: TXX0001
status: approved
agent: requirements-review
---
## BDD 评审
- BDD-1: PASS
EOF
    git -C "$REPO" add agate-workspace/tasks/T001/
    _write_min_valid_dispatch_context "agate-workspace/tasks/T001" "P1" "analyst"
    git -C "$REPO" add "agate-workspace/tasks/T001/P1-dispatch-context-analyst.md"
    run git -C "$REPO" commit -m "normal P1"
    [ "$status" -eq 0 ]
    [[ "$output" == *"GATE P1"* ]]
}

@test "bdd-17 pre-commit-gate 任务目录含 [ 元字符时 PROD_TOUCHED 检测不静默绕过（M9）" {
    echo init > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm init
    # 目录名含正则元字符 [ ]（TASK_REL 拼入 grep -E 的位置）
    mkdir -p "$REPO/agate-workspace/tasks/T[1]"
    cat > "$REPO/agate-workspace/tasks/T[1]/.state.yaml" <<'EOF'
task_id: TXX0001
phase: P5
status: active
retries: {}
EOF
    cat > "$REPO/agate-workspace/tasks/T[1]/P5-verification.md" <<'EOF'
[PROD_TOUCHED] 生产环境被接触
EOF
    git -C "$REPO" add "agate-workspace/tasks/T[1]/"
    run git -C "$REPO" commit -m "metachar prod touched"
    # 修复前：grep -E 把 [1] 当字符类 → 前缀不匹配 → PROD_TOUCHED 检测被静默绕过（exit 0）；修复后：exit 1
    [ "$status" -eq 1 ]
}

@test "bdd-19 pre-commit-gate 复制模式 hook 经 .agate-root 标记正确解析 AGATE_ROOT（其他-b）" {
    local repo
    repo=$(git_init)
    # 复制模式安装（Windows 无符号链接权限）：hook 是副本，非软链
    cp "$AGATE_ROOT/scripts/pre-commit-gate.sh" "$repo/.git/hooks/pre-commit"
    chmod +x "$repo/.git/hooks/pre-commit"
    # 复制模式安装时 install-hook.sh 写入的 AGATE_ROOT 兜底标记（修复后生效）
    printf '%s\n' "$AGATE_ROOT" > "$repo/.git/hooks/.agate-root"
    cd "$repo"
    echo init > README.md
    git add README.md
    git commit -qm init
    mkdir -p agate-workspace/tasks/T001
    cat > agate-workspace/tasks/T001/.state.yaml <<'EOF'
task_id: TXX0001
phase: P0
status: active
retries: {}
EOF
    git add agate-workspace/tasks/T001/
    # 需 unset AGATE_ROOT：load.bash 已 export，会掩盖 readlink 解析路径；复制模式故障仅在无 env 覆盖时暴露
    run env -u AGATE_ROOT git commit -m "copy mode hook"
    # 修复前：readlink 解析到 .git/hooks → AGATE_ROOT 错 → gate-result.sh 加载失败 exit 1；修复后：exit 0
    [ "$status" -eq 0 ]
}
