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

@test "bdd-17 probe_python 探测 python3→python 回退 + 失败返回空（fail-closed 阻断，BDD-17/26）" {
    # P2 §3.6 bdd-17 重构：py 自举后不再依赖 bash shim，改为 agate_common.probe_python
    # （python3 → python 顺序探测；无 python 时返回空 → 调用方须 fail-closed 阻断）
    local scripts_py
    scripts_py=$(py_path "$AGATE_SCRIPTS")

    # ① 正常环境：probe_python 解析到可用 python
    run env PYTHONPATH="$scripts_py" "$PYTHON" -c "import agate_common; print(agate_common.probe_python() or '')"
    [ "$status" -eq 0 ]
    [ -n "$output" ]

    # ② PATH 仅含 python（无 python3）→ probe_python 回退 python
    local fakebin real_py
    fakebin="$BATS_TEST_TMPDIR/pyonly"
    mkdir -p "$fakebin"
    real_py=$(command -v python 2>/dev/null || command -v python3 2>/dev/null || true)
    [ -n "$real_py" ] || skip "无 python 解释器"
    printf '#!/usr/bin/env bash\nexec "%s" "$@"\n' "$real_py" > "$fakebin/python"
    chmod +x "$fakebin/python"
    run env PATH="$fakebin" PYTHONPATH="$scripts_py" "$PYTHON" -c "import agate_common; print(agate_common.probe_python() or '')"
    [[ "$output" == *"$fakebin/python"* ]]

    # ③ PATH 无任何 python → probe_python 返回空（调用方 fail-closed 阻断，不静默放行）
    local emptybin
    emptybin="$BATS_TEST_TMPDIR/emptybin"
    mkdir -p "$emptybin"
    run env PATH="$emptybin" PYTHONPATH="$scripts_py" "$PYTHON" -c "import agate_common; print(agate_common.probe_python() or 'NONE')"
    [[ "$output" == *"NONE"* ]]
}
