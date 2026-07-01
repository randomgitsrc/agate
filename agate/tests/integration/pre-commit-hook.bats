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
