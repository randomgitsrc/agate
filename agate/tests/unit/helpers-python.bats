#!/usr/bin/env bats
# tests/unit/helpers-python.bats — PYTHON 探测 helper + harness shim（TAG0009 BDD-13/15/17）
# 被测对象：tests/helpers/fixtures.bash 的 detect_python / create_python_shim_bin
#
# 平台无关原则：本文件自身不得引入 R1-R5 字面命中（fixture 用运行时 fragment 拼接），
# 否则扫描器对全树扫描（BDD-8）会误报本文件。

load ../helpers/load.bash

@test "bdd-13 detect_python 优先 python3，PYTHON 已导出且可执行（BDD-13）" {
    [ -n "$PYTHON" ]
    run "$PYTHON" --version
    [ "$status" -eq 0 ]
    [[ "$output" == *"Python"* ]]
}

@test "bdd-15 PATH 仅含 python 无 python3 时 detect_python 回退 python（BDD-15/26）" {
    # 构造仅有 python 包装器的 bin（探测形态拼接，避免 R2 字面命中）
    local fakebin
    fakebin="$BATS_TEST_TMPDIR/pybin"
    mkdir -p "$fakebin"
    local real_py
    real_py=$(command -v python 2>/dev/null || command -v python3 2>/dev/null || true)
    [ -n "$real_py" ] || skip "无 python 解释器"
    printf '#!/usr/bin/env bash\nexec "%s" "$@"\n' "$real_py" > "$fakebin/python"
    chmod +x "$fakebin/python"

    # PATH 仅含 fakebin（无 python3）→ detect_python 回退到 fakebin/python
    local result
    result=$(PATH="$fakebin" detect_python)
    [[ "$result" == "$fakebin/python" ]]
}

@test "bdd-17 无 python3 环境 + shim：非法回退 P4→P2 仍 exit 1 不静默放行（BDD-17/26）" {
    # 模拟"python3 不可用"（Windows 无 python3 命令）：fakebin 放一个 exit 127 的 python3 stub
    local fakebin
    fakebin="$BATS_TEST_TMPDIR/nopy3"
    mkdir -p "$fakebin"
    printf '#!/usr/bin/env bash\nexit 127\n' > "$fakebin/python3"
    chmod +x "$fakebin/python3"
    local shim
    shim=$(create_python_shim_bin) || skip "无 python 解释器"

    # P4→P2 非法回退（差 2 ≥ 跳变阈值）
    local repo
    repo=$(git_init)
    mkdir -p "$repo/agate-workspace/tasks/T001"
    cat > "$repo/.state.yaml" <<'EOF'
task_id: T001
phase: P4
status: active
retries: {}
EOF
    git -C "$repo" add .state.yaml
    git -C "$repo" commit -qm "P4"
    cat > "$repo/.state.yaml" <<'EOF'
task_id: T001
phase: P2
status: active
retries: {}
EOF
    git -C "$repo" add .state.yaml

    # 无 shim：python3 stub 失败 → 读不到 phase → 静默 exit 0（41 例根因复现）
    run env PATH="$fakebin:$PATH" bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-state-transition.sh' .state.yaml"
    [ "$status" -eq 0 ]

    # 有 shim：shim 的 python3 指向真解释器 → 正确 exit 1（不静默放行）
    run env PATH="$shim:$fakebin:$PATH" bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-state-transition.sh' .state.yaml"
    [ "$status" -eq 1 ]
}
