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

# 为派发阶段产出 commit 生成最小有效的 dispatch-context.md
_add_dispatch_ctx() {
    local dir="$1" phase="$2"
    cat > "$dir/${phase}-dispatch-context.md" << 'DCTPL'
---
phase: PH_PLACEHOLDER
generated_by: agate-next-card.sh
---

<!-- AGATE_CARD_START -->
DCTPL
    bash "$AGATE_SCRIPTS/agate-next-card.sh" "$phase" 2>/dev/null >> "$dir/${phase}-dispatch-context.md"
    cat >> "$dir/${phase}-dispatch-context.md" << 'DCTPL'
<!-- AGATE_CARD_END -->
DCTPL
    sed -i "s/PH_PLACEHOLDER/${phase}/" "$dir/${phase}-dispatch-context.md"
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
    # 添加 .state.yaml + .state.yaml 含 P1
    cat > "$REPO/.state.yaml" <<'EOF'
task_id: T001
phase: P1
status: active
retries: {}
EOF
    # 添加 task 目录
    mkdir -p "$REPO/docs/tasks/T001"
    cat > "$REPO/docs/tasks/T001/P1-requirements.md" <<'EOF'
---
agent: test
---
risk_level: medium
phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]
- Given test precondition
EOF
    git -C "$REPO" add .state.yaml docs/tasks/T001/
    _add_dispatch_ctx "docs/tasks/T001" "P1"
    git -C "$REPO" add "docs/tasks/T001/P1-dispatch-context.md"
    run git -C "$REPO" commit -m "phase change to P1"
    [ "$status" -eq 0 ]
}

@test "IT.3 pre-commit-hook [PROD_TOUCHED] 中止 commit" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    # 创建含 [PROD_TOUCHED] 标记的文件
    echo "do something to production [PROD_TOUCHED]" > "$REPO/prod.log"
    # 同时改 .state.yaml phase，触发 gate
    cat > "$REPO/.state.yaml" <<'EOF'
task_id: T001
phase: P1
status: active
retries: {}
EOF
    git -C "$REPO" add prod.log .state.yaml
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
    # 任务级 .state.yaml（多任务架构）
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
    _add_dispatch_ctx "docs/tasks/T001" "P1"
    git -C "$REPO" add "docs/tasks/T001/P1-dispatch-context.md"
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

@test "IT.8 pre-commit-hook 多任务：phase 变更无产出 → 不拦截不 WARNING" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    # 先 commit P1 状态（P1 产出 + phase=P1 一致）
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
    _add_dispatch_ctx "docs/tasks/T001" "P1"
    git -C "$REPO" add "docs/tasks/T001/P1-dispatch-context.md"
    git -C "$REPO" commit -qm "T001 P1"
    # 改 phase 到 P2 但无 P2 产出（P2 gate exit 2 不拦截）
    cat > "$REPO/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P2
status: active
retries: {}
EOF
    git -C "$REPO" add docs/tasks/T001/.state.yaml
    run git -C "$REPO" commit -m "T001 phase P2" 2>&1
    [ "$status" -eq 0 ]
}

@test "IT.9 pre-commit-hook 多任务：裁剪跳阶 P2→P5 无 P3/P4 产出 → 不拦截" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    # P2 状态 + 声明裁剪 P3/P4
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
phases: [P0, P1, P2, P5, P6, P7, P8]
跳过风险: 低
EOF
    git -C "$REPO" add docs/tasks/T001/
    git -C "$REPO" commit -qm "T001 P2"
    # 跳到 P5（裁剪 P3/P4）
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

@test "IT.10 pre-commit-hook 向后兼容：根 .state.yaml 仍工作" {
    echo "init" > "$REPO/README.md"
    git -C "$REPO" add README.md
    git -C "$REPO" commit -qm "init"
    # 根 .state.yaml（单任务架构）
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
    git -C "$REPO" add .state.yaml docs/tasks/T001/
    _add_dispatch_ctx "docs/tasks/T001" "P1"
    git -C "$REPO" add "docs/tasks/T001/P1-dispatch-context.md"
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
