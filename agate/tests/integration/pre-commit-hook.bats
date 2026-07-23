#!/usr/bin/env bats
# tests/integration/pre-commit-hook.bats — 5 用例覆盖 pre-commit-gate.sh
# 计划：7.1 / 实际 5 行 / 与附录 A 一致

load ../helpers/load.bash

# 注意：pre-commit-gate.sh 在 agate 仓库的 .git/hooks/ 下才生效
# 测试方法：把 hook 复制到临时 repo，触发 pre-commit，验证行为

setup() {
    REPO=$(git_init)
    cd "$REPO"
    # 安装 pre-commit hook
    HOOK_PATH="$REPO/.git/hooks/pre-commit"
    cp "$AGATE_ROOT/scripts/pre-commit-gate.sh" "$HOOK_PATH"
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
- docs/tasks/T001/P0-brief.md
</dispatch_guide>

<!-- AGATE_CARD_START -->
DCTPL
    bash "$AGATE_SCRIPTS/agate-next-card.sh" "$phase" 2>/dev/null >> "$dir/${phase}-dispatch-context-${role}.md"
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
task_id: T001
phase: P1
status: active
retries: {}
EOF
    mkdir -p "$REPO/docs/tasks/T001"
    cat > "$REPO/docs/tasks/T001/P1-requirements.md" <<'EOF'
---
agent: test
---
risk_level: medium
phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]
- Given test precondition
EOF
    cat > "$REPO/docs/tasks/T001/P1-review.md" <<'EOF'
---
phase: P1
task_id: T001
status: approved
agent: requirements-review
---
## BDD 评审
- B01: PASS + 覆盖维度：数据✓
EOF
    git -C "$REPO" add .state.yaml docs/tasks/T001/
    _write_min_valid_dispatch_context "docs/tasks/T001" "P1" "analyst"
    git -C "$REPO" add "docs/tasks/T001/P1-dispatch-context-analyst.md"
    run git -C "$REPO" commit -m "phase change to P1"
    [ "$status" -eq 0 ]
}

@test "IT.3 pre-commit-hook [PROD_TOUCHED] 中止 commit" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    # 创建任务目录 + 含 [PROD_TOUCHED] 标记的产出文件
    mkdir -p "$REPO/docs/tasks/T001"
    echo "do something to production [PROD_TOUCHED]" > "$REPO/docs/tasks/T001/P5-verification.md"
    # 同时改 .state.yaml phase，触发 gate
    cat > "$REPO/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P5
status: active
retries: {}
EOF
    git -C "$REPO" add docs/tasks/T001/P5-verification.md docs/tasks/T001/.state.yaml
    run git -C "$REPO" commit -m "should fail"
    [ "$status" -ne 0 ]
    [[ "$output" == *"PROD_TOUCHED"* ]]
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
task_id: T001
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
    mkdir -p "$REPO/docs/tasks/T001"
    cat > "$REPO/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P1
status: active
retries: {}
EOF
    cat > "$REPO/docs/tasks/T001/P1-requirements.md" <<'EOF'
---
agent: test
---
risk_level: medium
phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]
- Given test precondition
EOF
    cat > "$REPO/docs/tasks/T001/P1-review.md" <<'EOF'
---
phase: P1
task_id: T001
status: approved
agent: requirements-review
---
## BDD 评审
- B01: PASS + 覆盖维度：数据✓
EOF
    git -C "$REPO" add docs/tasks/T001/
    _write_min_valid_dispatch_context "docs/tasks/T001" "P1" "analyst"
    git -C "$REPO" add "docs/tasks/T001/P1-dispatch-context-analyst.md"
    run git -C "$REPO" commit -m "T001 P1"
    [ "$status" -eq 0 ]
}

@test "IT.7 pre-commit-hook 多任务：P4 产出但 phase 仍 P3 → WARNING 不拦截" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    # 先 commit 一个 P3 状态
    mkdir -p "$REPO/docs/tasks/T001"
    cat > "$REPO/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P3
status: active
retries: {}
EOF
    cat > "$REPO/docs/tasks/T001/P1-requirements.md" <<'EOF'
---
agent: test
---
risk_level: medium
phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]
- Given test precondition
EOF
    git -C "$REPO" add docs/tasks/T001/
    git -C "$REPO" commit -qm "T001 P3"
    # 现在 commit P4 产出但忘改 phase
    echo "implementation" > "$REPO/docs/tasks/T001/P4-implementation.md"
    git -C "$REPO" add docs/tasks/T001/P4-implementation.md
    run git -C "$REPO" commit -m "T001 P4 output only" 2>&1
    [ "$status" -eq 0 ]
    [[ "$output" == *"WARNING"* || "$output" == *"phase"* ]]
}

@test "IT.8 pre-commit-hook 多任务：phase 变更到 P2 但无 P2-design.md → 拦截" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/docs/tasks/T001"
    cat > "$REPO/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P1
status: active
retries: {}
EOF
    cat > "$REPO/docs/tasks/T001/P1-requirements.md" <<'EOF'
---
agent: test
---
risk_level: medium
phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]
- Given test precondition
EOF
    cat > "$REPO/docs/tasks/T001/P1-review.md" <<'EOF'
---
phase: P1
task_id: T001
status: approved
agent: requirements-review
---
## BDD 评审
- B01: PASS + 覆盖维度：数据✓
EOF
    git -C "$REPO" add docs/tasks/T001/
    _write_min_valid_dispatch_context "docs/tasks/T001" "P1" "analyst"
    git -C "$REPO" add "docs/tasks/T001/P1-dispatch-context-analyst.md"
    git -C "$REPO" commit -qm "T001 P1"
    cat > "$REPO/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P2
status: active
retries: {}
EOF
    git -C "$REPO" add docs/tasks/T001/.state.yaml
    run git -C "$REPO" commit -m "T001 phase P2" 2>&1
    [ "$status" -ne 0 ]
    [[ "$output" == *"P2-design.md 不存在"* || "$output" == *"P2 不可裁剪"* ]]
}

@test "IT.9 pre-commit-hook 多任务：裁剪跳阶 P2→P5 无 P3 产出（low 风险）→ 不拦截" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/docs/tasks/T001"
    cat > "$REPO/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P2
status: active
retries: {}
EOF
    cat > "$REPO/docs/tasks/T001/P1-requirements.md" <<'EOF'
---
agent: test
---
risk_level: low
phases: [P0, P1, P2, P4, P5, P6, P7, P8]
跳过风险: 低
EOF
    cat > "$REPO/docs/tasks/T001/P2-design.md" <<'EOF'
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
### 候选方案 B：方案二
## 权衡
A 简单 B 稳健
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    git -C "$REPO" add docs/tasks/T001/
    _write_min_valid_dispatch_context "docs/tasks/T001" "P2" "architect"
    git -C "$REPO" add "docs/tasks/T001/P2-dispatch-context-architect.md"
    git -C "$REPO" commit -qm "T001 P2"
    cat > "$REPO/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P5
status: active
retries: {}
EOF
    cat > "$REPO/docs/tasks/T001/P5-verification.md" <<'EOF'
---
agent: test
---
EOF
    git -C "$REPO" add docs/tasks/T001/
    run git -C "$REPO" commit -m "T001 skip to P5"
    [ "$status" -eq 0 ]
}

@test "IT.9b pre-commit-hook 裁剪跳阶 P3 medium 风险 → 拦截（P1-8: 仅 low 可裁 P3）" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/docs/tasks/T001"
    cat > "$REPO/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P2
status: active
retries: {}
EOF
    cat > "$REPO/docs/tasks/T001/P1-requirements.md" <<'EOF'
---
agent: test
---
risk_level: medium
phases: [P0, P1, P2, P4, P5, P6, P7, P8]
跳过风险: 低
EOF
    cat > "$REPO/docs/tasks/T001/P2-design.md" <<'EOF'
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
### 候选方案 B：方案二
## 权衡
A 简单 B 稳健
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    git -C "$REPO" add docs/tasks/T001/
    _write_min_valid_dispatch_context "docs/tasks/T001" "P2" "architect"
    git -C "$REPO" add "docs/tasks/T001/P2-dispatch-context-architect.md"
    run git -C "$REPO" commit -m "T001 P2 medium skip P3"
    [ "$status" -ne 0 ]
    [[ "$output" == *"P3 不可裁剪"*"仅 low"* ]]
}

@test "IT.10 pre-commit-hook 向后兼容：根 .state.yaml 仍工作" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    cat > "$REPO/.state.yaml" <<'EOF'
task_id: T001
phase: P1
status: active
retries: {}
EOF
    mkdir -p "$REPO/docs/tasks/T001"
    cat > "$REPO/docs/tasks/T001/P1-requirements.md" <<'EOF'
---
agent: test
---
risk_level: medium
phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]
- Given test precondition
EOF
    cat > "$REPO/docs/tasks/T001/P1-review.md" <<'EOF'
---
phase: P1
task_id: T001
status: approved
agent: requirements-review
---
## BDD 评审
- B01: PASS + 覆盖维度：数据✓
EOF
    git -C "$REPO" add .state.yaml docs/tasks/T001/
    _write_min_valid_dispatch_context "docs/tasks/T001" "P1" "analyst"
    git -C "$REPO" add "docs/tasks/T001/P1-dispatch-context-analyst.md"
    run git -C "$REPO" commit -m "root state P1"
    [ "$status" -eq 0 ]
}

@test "IT.11 pre-commit-hook P2 阶段暂存代码文件 → WARNING" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/docs/tasks/T001"
    cat > "$REPO/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P2
status: active
retries: {}
EOF
    cat > "$REPO/docs/tasks/T001/P1-requirements.md" <<'EOF'
---
agent: test
---
risk_level: medium
phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]
- Given test precondition
EOF
    git -C "$REPO" add docs/tasks/T001/
    git -C "$REPO" commit --no-verify -qm "T001 P2 setup"
    echo "print('hello')" > "$REPO/hack.py"
    cat > "$REPO/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P2
status: active
retries:
  P2:
    - round: 1
      failure_mode: test
EOF
    git -C "$REPO" add hack.py docs/tasks/T001/.state.yaml
    run bash -c "cd '$REPO' && bash '$AGATE_ROOT/scripts/pre-commit-gate.sh'" 2>&1 || true
    [[ "$output" == *"代码文件"* ]]
}

# ========== 标记二值声明：PROD_TOUCHED ==========

@test "IT_PT_BINARY.1 暂存 diff 含行首 [PROD_TOUCHED] 描述 → 中止 commit（步骤 1）" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/docs/tasks/T001"
    echo "[PROD_TOUCHED] 接触了生产环境：修改了线上配置" > "$REPO/docs/tasks/T001/P5-verification.md"
    cat > "$REPO/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P5
status: active
retries: {}
EOF
    git -C "$REPO" add docs/tasks/T001/P5-verification.md docs/tasks/T001/.state.yaml
    run git -C "$REPO" commit -m "should fail"
    [ "$status" -ne 0 ]
    [[ "$output" == *"PROD_TOUCHED"* ]]
}

@test "IT_PT_BINARY.2 暂存 diff 含 [PROD_NOT_TOUCHED] → 不中止" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/docs/tasks/T001"
    echo "[PROD_NOT_TOUCHED]" > "$REPO/docs/tasks/T001/P5-verification.md"
    cat > "$REPO/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P5
status: active
retries: {}
EOF
    git -C "$REPO" add docs/tasks/T001/P5-verification.md docs/tasks/T001/.state.yaml
    run git -C "$REPO" commit -m "should pass"
    [ "$status" -eq 0 ]
}

@test "IT_PT_BINARY.3 暂存 diff 含删除行 [PROD_TOUCHED] → 不中止（只扫 ^+ 行）" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/docs/tasks/T001"
    echo "[PROD_TOUCHED] 旧内容" > "$REPO/docs/tasks/T001/P5-verification.md"
    cat > "$REPO/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P5
status: active
retries: {}
EOF
    git -C "$REPO" add docs/tasks/T001/P5-verification.md docs/tasks/T001/.state.yaml
    git -C "$REPO" commit --no-verify -qm "setup with PROD_TOUCHED"
    echo "clean content" > "$REPO/docs/tasks/T001/P5-verification.md"
    git -C "$REPO" add docs/tasks/T001/P5-verification.md
    run git -C "$REPO" commit -m "remove PROD_TOUCHED"
    [ "$status" -eq 0 ]
}

@test "IT_PT_BINARY.4 暂存 diff 含不合规格式（句中引用）→ 中止（步骤 2）" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/docs/tasks/T001"
    echo "无 [PROD_TOUCHED] 需要报告" > "$REPO/docs/tasks/T001/P5-verification.md"
    cat > "$REPO/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P5
status: active
retries: {}
EOF
    git -C "$REPO" add docs/tasks/T001/P5-verification.md docs/tasks/T001/.state.yaml
    run git -C "$REPO" commit -m "should fail"
    [ "$status" -ne 0 ]
    [[ "$output" == *"不合规"* ]]
}

@test "IT_PT_BINARY.5 暂存 diff 含句中引用 [PROD_TOUCHED] → 中止（步骤 2）" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/docs/tasks/T001"
    echo "检查了 [PROD_TOUCHED] 标记" > "$REPO/docs/tasks/T001/P5-verification.md"
    cat > "$REPO/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P5
status: active
retries: {}
EOF
    git -C "$REPO" add docs/tasks/T001/P5-verification.md docs/tasks/T001/.state.yaml
    run git -C "$REPO" commit -m "should fail"
    [ "$status" -ne 0 ]
    [[ "$output" == *"不合规"* ]]
}

@test "IT_PT_BINARY.6 暂存 diff 既无正向也无负向 → 不中止 + 无 WARNING（步骤 3 静默通过）" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/docs/tasks/T001"
    echo "normal content without any marker" > "$REPO/docs/tasks/T001/P5-verification.md"
    cat > "$REPO/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P5
status: active
retries: {}
EOF
    git -C "$REPO" add docs/tasks/T001/P5-verification.md docs/tasks/T001/.state.yaml
    run git -C "$REPO" commit -m "should pass"
    [ "$status" -eq 0 ]
    [[ "$output" != *"WARNING"* ]]
}

# ========== Phase-span WARNING 方向检查 ==========

@test "IT_PHASE_SPAN.1 新增 P1/P2 产出文件 phase=P3（历史产出晚提交）→ 不报 WARNING" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/docs/tasks/T001"
    cat > "$REPO/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P3
status: active
retries: {}
EOF
    cat > "$REPO/docs/tasks/T001/P1-requirements.md" <<'EOF'
---
agent: test
---
risk_level: medium
phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]
- Given test precondition
EOF
    cat > "$REPO/docs/tasks/T001/P2-design.md" <<'EOF'
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
    git -C "$REPO" add docs/tasks/T001/
    run git -C "$REPO" commit -m "T001 late commit P1/P2 outputs" 2>&1
    [ "$status" -eq 0 ]
    [[ "$output" != *"WARNING"*"P1"* ]]
    [[ "$output" != *"WARNING"*"P2"* ]]
}

@test "IT_PHASE_SPAN.2 已存在 P1 产出被重新暂存 phase=P3 → 报 WARNING（真实过期）" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/docs/tasks/T001"
    cat > "$REPO/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P1
status: active
retries: {}
EOF
    cat > "$REPO/docs/tasks/T001/P1-requirements.md" <<'EOF'
---
agent: test
---
risk_level: medium
phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]
- Given test precondition
EOF
    git -C "$REPO" add docs/tasks/T001/
    git -C "$REPO" commit --no-verify -qm "T001 P1 setup"
    cat > "$REPO/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P3
status: active
retries: {}
EOF
    echo "updated requirements" >> "$REPO/docs/tasks/T001/P1-requirements.md"
    git -C "$REPO" add docs/tasks/T001/P1-requirements.md docs/tasks/T001/.state.yaml
    run git -C "$REPO" commit -m "T001 modify P1 while phase=P3" 2>&1
    [ "$status" -eq 0 ]
    [[ "$output" == *"WARNING"*"P1"* ]]
}

@test "IT_PHASE_SPAN.3 新增 P4 产出文件 phase=P3（提前产出）→ 报 WARNING" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/docs/tasks/T001"
    cat > "$REPO/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P3
status: active
retries: {}
EOF
    cat > "$REPO/docs/tasks/T001/P1-requirements.md" <<'EOF'
---
agent: test
---
risk_level: medium
phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]
- Given test precondition
EOF
    git -C "$REPO" add docs/tasks/T001/
    git -C "$REPO" commit --no-verify -qm "T001 P3 setup"
    echo "implementation" > "$REPO/docs/tasks/T001/P4-implementation.md"
    git -C "$REPO" add docs/tasks/T001/P4-implementation.md
    run git -C "$REPO" commit -m "T001 P4 output while phase=P3" 2>&1
    [ "$status" -eq 0 ]
    [[ "$output" == *"WARNING"*"P4"* ]]
}

@test "IT_PHASE_SPAN.4 多任务场景：T001 历史产出晚提交不 WARNING / T002 已存在产出修改报 WARNING / T003 提前产出报 WARNING" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    # T001: phase=P3, 新增 P1 产出（历史产出晚提交）→ 不 WARNING
    mkdir -p "$REPO/docs/tasks/T001"
    cat > "$REPO/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P3
status: active
retries: {}
EOF
    cat > "$REPO/docs/tasks/T001/P1-requirements.md" <<'EOF'
---
agent: test
---
risk_level: medium
phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]
- Given test precondition
EOF
    cat > "$REPO/docs/tasks/T001/P2-design.md" <<'EOF'
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
    cat > "$REPO/docs/tasks/T001/P3-test-cases.md" <<'EOF'
---
agent: test
---
test cases
EOF
    cat > "$REPO/docs/tasks/T001/P1-review.md" <<'EOF'
---
phase: P1
task_id: T001
status: approved
agent: requirements-review
---
## BDD 评审
- B01: PASS + 覆盖维度：数据✓
EOF
    git -C "$REPO" add docs/tasks/T001/
    _write_min_valid_dispatch_context "docs/tasks/T001" "P3" "test-designer"
    git -C "$REPO" add "docs/tasks/T001/P3-dispatch-context-test-designer.md"
    git -C "$REPO" commit --no-verify -qm "T001 P3 setup"
    # T002: phase=P3, 已存在 P1 产出被修改 → WARNING
    mkdir -p "$REPO/docs/tasks/T002"
    cat > "$REPO/docs/tasks/T002/.state.yaml" <<'EOF'
task_id: T002
phase: P1
status: active
retries: {}
EOF
    cat > "$REPO/docs/tasks/T002/P1-requirements.md" <<'EOF'
---
agent: test
---
risk_level: medium
phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]
- Given test precondition
EOF
    git -C "$REPO" add docs/tasks/T002/
    git -C "$REPO" commit --no-verify -qm "T002 P1 setup"
    cat > "$REPO/docs/tasks/T002/.state.yaml" <<'EOF'
task_id: T002
phase: P3
status: active
retries: {}
EOF
    echo "updated" >> "$REPO/docs/tasks/T002/P1-requirements.md"
    # T003: phase=P3, 新增 P4 产出（提前产出）→ WARNING
    # .state.yaml 已在上一 commit 提交，本次只暂存 P4 产出
    mkdir -p "$REPO/docs/tasks/T003"
    cat > "$REPO/docs/tasks/T003/.state.yaml" <<'EOF'
task_id: T003
phase: P3
status: active
retries: {}
EOF
    cat > "$REPO/docs/tasks/T003/P1-requirements.md" <<'EOF'
---
agent: test
---
risk_level: medium
phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]
- Given test precondition
EOF
    git -C "$REPO" add docs/tasks/T003/
    git -C "$REPO" commit --no-verify -qm "T003 P3 setup"
    echo "implementation" > "$REPO/docs/tasks/T003/P4-implementation.md"
    git -C "$REPO" add docs/tasks/T002/ docs/tasks/T003/P4-implementation.md
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
    mkdir -p "$REPO/docs/tasks/T001"
    cat > "$REPO/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: PAUSED
status: active
retries: {}
EOF
    cat > "$REPO/docs/tasks/T001/P1-requirements.md" <<'EOF'
---
agent: test
---
risk_level: medium
phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]
- Given test precondition
EOF
    git -C "$REPO" add docs/tasks/T001/
    run git -C "$REPO" commit -m "T001 PAUSED with P1 output" 2>&1
    [ "$status" -eq 0 ]
    [[ "$output" != *"integer expression expected"* ]]
}

# ========== 标记二值声明：PROD_TOUCHED ==========

@test "IT_PT_BINARY.7 暂存 diff 含 [PROD_NOT_TOUCHED] 确认未接触（负向+描述）→ 不中止" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/docs/tasks/T001"
    echo "[PROD_NOT_TOUCHED] 确认未接触" > "$REPO/docs/tasks/T001/P5-verification.md"
    cat > "$REPO/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P5
status: active
retries: {}
EOF
    git -C "$REPO" add docs/tasks/T001/P5-verification.md docs/tasks/T001/.state.yaml
    run git -C "$REPO" commit -m "should pass"
    [ "$status" -eq 0 ]
}

# ========== P6 self-authored gate 代码直改硬拦截 ==========

@test "IT_P6_CODE.1 phase=P6，暂存 P6-evidence/ 下截图 → 不拦（证据文件例外）" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/docs/tasks/T001/P6-evidence/screenshots"
    touch "$REPO/docs/tasks/T001/P6-evidence/screenshots/a.png"
    echo "- PASS BDD-1: ok (screenshots/a.png)" > "$REPO/docs/tasks/T001/P6-acceptance.md"
    cat > "$REPO/docs/tasks/T001/.state.yaml" <<'EOF2'
task_id: T001
phase: P6
status: active
retries: {}
EOF2
    _write_min_valid_dispatch_context "$REPO/docs/tasks/T001" "P6" "verifier"
    git -C "$REPO" add docs/tasks/T001/
    run git -C "$REPO" commit -m "p6 evidence only"
    [[ "$output" != *"暂存了项目源码"* ]]
    [[ "$output" != *"不应直接改代码"* ]]
}

@test "IT_P6_CODE.2 phase=P6，暂存项目源码文件 → exit 1 硬拦截" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/docs/tasks/T001/P6-evidence/screenshots" "$REPO/src"
    touch "$REPO/docs/tasks/T001/P6-evidence/screenshots/a.png"
    echo "- PASS BDD-1: ok (screenshots/a.png)" > "$REPO/docs/tasks/T001/P6-acceptance.md"
    echo "print('fix')" > "$REPO/src/app.py"
    cat > "$REPO/docs/tasks/T001/.state.yaml" <<'EOF2'
task_id: T001
phase: P6
status: active
retries: {}
EOF2
    _write_min_valid_dispatch_context "$REPO/docs/tasks/T001" "P6" "verifier"
    git -C "$REPO" add src/app.py docs/tasks/T001/
    run git -C "$REPO" commit -m "should be blocked"
    [ "$status" -ne 0 ]
    [[ "$output" == *"不应直接改代码"* ]]
}

@test "IT_P6_CODE.3 phase=P4，暂存源码文件 → 不拦（回归）" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/docs/tasks/T001" "$REPO/src"
    echo "print('impl')" > "$REPO/src/app.py"
    cat > "$REPO/docs/tasks/T001/.state.yaml" <<'EOF2'
task_id: T001
phase: P4
status: active
retries: {}
EOF2
    git -C "$REPO" add src/app.py docs/tasks/T001/.state.yaml
    run git -C "$REPO" commit -m "p4 impl"
    [[ "$output" != *"不应直接改代码"* ]]
}

@test "IT_P6_CODE.4 phase=P5，暂存源码文件 → 不拦（回归）" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/docs/tasks/T001" "$REPO/src"
    echo "print('fix')" > "$REPO/src/app.py"
    cat > "$REPO/docs/tasks/T001/.state.yaml" <<'EOF2'
task_id: T001
phase: P5
status: active
retries: {}
EOF2
    git -C "$REPO" add src/app.py docs/tasks/T001/.state.yaml
    run git -C "$REPO" commit -m "p5 fix"
    [[ "$output" != *"不应直接改代码"* ]]
}

@test "IT_P6_CODE.5 phase=P2，暂存源码文件 → WARNING 而非硬拦截（回归，现有行为不变）" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/docs/tasks/T001" "$REPO/src"
    echo "print('early')" > "$REPO/src/app.py"
    cat > "$REPO/docs/tasks/T001/.state.yaml" <<'EOF2'
task_id: T001
phase: P2
status: active
retries: {}
EOF2
    git -C "$REPO" add src/app.py docs/tasks/T001/.state.yaml
    run git -C "$REPO" commit -m "p2 early code"
    [[ "$output" == *"是否在非实现阶段直接改代码"* ]]
    [[ "$output" != *"不应直接改代码"* ]]
}

# ========== agate-retreat-to.sh 与真实 pre-commit hook 的集成 ==========

@test "IT_RETREAT.1 agate-retreat-to.sh 在装了真实 hook 的仓库里，每一步都真的过 hook 校验" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    mkdir -p "$REPO/docs/tasks/T001/P6-evidence/screenshots"
    echo "- PASS BDD-1: ok (screenshots/x.png)" > "$REPO/docs/tasks/T001/P6-acceptance.md"
    touch "$REPO/docs/tasks/T001/P6-evidence/screenshots/x.png"
    cat > "$REPO/docs/tasks/T001/.state.yaml" <<'EOF2'
task_id: T001
phase: P6
status: active
retries: {}
EOF2
    _write_min_valid_dispatch_context "$REPO/docs/tasks/T001" "P6" "verifier"
    git -C "$REPO" add docs/tasks/T001/
    git -C "$REPO" commit -qm "setup P6 state"

    run bash -c "cd '$REPO' && bash '$AGATE_SCRIPTS/agate-retreat-to.sh' docs/tasks/T001 P4 '集成测试诊断'"
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
    mkdir -p "$REPO/docs/tasks/T001/P6-evidence/screenshots"
    echo "- PASS BDD-1: ok (screenshots/x.png)" > "$REPO/docs/tasks/T001/P6-acceptance.md"
    touch "$REPO/docs/tasks/T001/P6-evidence/screenshots/x.png"
    cat > "$REPO/docs/tasks/T001/.state.yaml" <<'EOF2'
task_id: T001
phase: P6
status: active
retries: {}
EOF2
    _write_min_valid_dispatch_context "$REPO/docs/tasks/T001" "P6" "verifier"
    git -C "$REPO" add docs/tasks/T001/
    git -C "$REPO" commit -qm "setup P6 state"

    # 故意在工作区留一个句中引用 [PROD_TOUCHED] 的文件（不合规格式，phase 无关，
    # 会被 pre-commit-gate.sh 的二值声明步骤 2 硬拦截）。agate-retreat-to.sh 的
    # git add "$TASK_DIR" 会在第一步（P6->P5）把它一并带上，验证中途拒绝时脚本
    # 能正确报告"已停在 P6"且不会继续尝试后续步骤
    echo "记录：曾经不小心碰到了 [PROD_TOUCHED] 生产环境" > "$REPO/docs/tasks/T001/note.md"

    run bash -c "cd '$REPO' && bash '$AGATE_SCRIPTS/agate-retreat-to.sh' docs/tasks/T001 P4 '集成测试：中途拒绝'"
    [ "$status" -eq 1 ]
    [[ "$output" == *"未通过 pre-commit hook 校验"* ]]
    [[ "$output" == *"已停在 P6"* ]]

    # 确认没有任何一步真的成功提交（P6 仍是当前 phase，没有 retreat commit 落地）
    run bash -c "cd '$REPO' && git log --oneline"
    [[ "$output" != *"retreat:"* ]]
}
