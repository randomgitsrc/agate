#!/usr/bin/env bats
# tests/scripts/check-windows-smoke.bats — Windows 冒烟子集脚本行为测试（TAG0009 v0.45 决策）
# 被测对象：agate/tests/scripts/check-windows-smoke.sh
#
# 背景：Windows runner 全量 bats（747 用例）约 11.5 分钟且线性增长，阻塞 CI。
#       v0.45 起 Windows bats 降级为"技术路线冒烟"：功能正确性由 Linux 全量保证；
#       Windows 只验证每条平台敏感机制（py_path/shim/cp1252/CRLF/symlink 等）的代表用例。
# 代表选取规则（机械、无人工清单）：
#   1. 每文件取第 1 个用例：保证 setup/helper 加载在 Windows 可用
#   2. 名称含平台敏感关键词的用例：保证每条平台敏感机制有 Windows 代表
#
# 本文件契约：
#   WSMOKE.1 --list 每文件输出 file<TAB>用例列表（第 1 个 + 平台关键词用例）
#   WSMOKE.2 平台敏感关键词用例被包含（如 cp1252 / CRLF / Windows / symlink / py_path）
#   WSMOKE.3 每个文件至少包含第 1 个用例（== 每文件至少一个代表）
#   WSMOKE.4 全部测试文件都被覆盖（unit+integration+regression+sanity+scripts 有代表）
#   WSMOKE.5 失败传播：mock bats 返回非零 → 脚本 exit 1 且报告失败文件
#   WSMOKE.6 成功传播：mock bats 返回零 → 脚本 exit 0
#   WSMOKE.7 脚本自身平台无关（check-platform-assumptions.sh 扫描 0 命中）

load ../helpers/load.bash
load ../helpers/fixtures.bash

@test "WSMOKE.1 --list 每文件输出 file<TAB>代表用例列表" {
    local script="$AGATE_ROOT/tests/scripts/check-windows-smoke.sh"
    run bash "$script" --list
    [ "$status" -eq 0 ]
    # 至少覆盖 60 个文件（unit 46 + integration 6 + regression 6 + sanity 1 + scripts 1）
    [ "$(printf '%s\n' "$output" | grep -c $'\t')" -ge 60 ]
    # 每行格式：绝对路径\t转义用例
    while IFS= read -r line; do
        [[ "$line" =~ ^/.*\.bats$'\t'.+$ ]]
    done <<< "$output"
}

@test "WSMOKE.2 平台敏感关键词用例被包含（cp1252/CRLF/Windows/symlink）" {
    local script="$AGATE_ROOT/tests/scripts/check-windows-smoke.sh"
    run bash "$script" --list
    [ "$status" -eq 0 ]
    [[ "$output" == *"cp1252"* ]]
    [[ "$output" == *"CRLF"* ]]
    [[ "$output" == *"Windows"* ]]
    [[ "$output" == *"symlink"* ]]
}

@test "WSMOKE.3 每个文件至少包含第 1 个用例（== 每文件至少一个代表）" {
    local script="$AGATE_ROOT/tests/scripts/check-windows-smoke.sh"
    run bash "$script" --list
    [ "$status" -eq 0 ]
    # 代表数 == 文件数：每文件一行（内含 1 个以上用例，用 | 连接）
    local files_lines keys_lines
    files_lines=$(find "$AGATE_ROOT/tests/unit" "$AGATE_ROOT/tests/integration" "$AGATE_ROOT/tests/regression" \
        -name '*.bats' -o -name 'sanity.bats' 2>/dev/null | wc -l | tr -d ' ')
    keys_lines=$(printf '%s\n' "$output" | grep -c $'\t' | tr -d ' ')
    [ "$keys_lines" -ge "$files_lines" ]
    # sanity.bats 必须被覆盖
    [[ "$output" == *"sanity.bats"* ]]
    # scripts/check-platform-assumptions.bats 必须被覆盖
    [[ "$output" == *"check-platform-assumptions.bats"* ]]
}

@test "WSMOKE.4 覆盖全部测试文件（unit+integration+regression 的代表都出现）" {
    local script="$AGATE_ROOT/tests/scripts/check-windows-smoke.sh"
    run bash "$script" --list
    [ "$status" -eq 0 ]
    local unit rep
    unit=$(ls "$AGATE_ROOT"/tests/unit/*.bats | wc -l | tr -d ' ')
    rep=$(printf '%s\n' "$output" | grep -c "tests/unit/" | tr -d ' ')
    [ "$rep" -eq "$unit" ]
    local int rep_i
    int=$(ls "$AGATE_ROOT"/tests/integration/*.bats | wc -l | tr -d ' ')
    rep_i=$(printf '%s\n' "$output" | grep -c "tests/integration/" | tr -d ' ')
    [ "$rep_i" -eq "$int" ]
}

@test "WSMOKE.5 失败传播：mock bats 返回非零 → exit 1 且报告失败文件" {
    local script="$AGATE_ROOT/tests/scripts/check-windows-smoke.sh"
    local mock
    mock=$(mktemp -d "$BATS_TEST_TMPDIR/mockbats-XXXXXX")
    printf '#!/usr/bin/env bash\nexit 1\n' > "$mock/bats"
    chmod +x "$mock/bats"
    run env PATH="$mock:$PATH" BATS_BIN="$mock/bats" bash "$script"
    [ "$status" -eq 1 ]
    [[ "$output" == *"FAILED"* ]]
}

@test "WSMOKE.6 成功传播：mock bats 返回零 → exit 0" {
    local script="$AGATE_ROOT/tests/scripts/check-windows-smoke.sh"
    local mock
    mock=$(mktemp -d "$BATS_TEST_TMPDIR/mockbats-XXXXXX")
    printf '#!/usr/bin/env bash\nexit 0\n' > "$mock/bats"
    chmod +x "$mock/bats"
    run env PATH="$mock:$PATH" BATS_BIN="$mock/bats" bash "$script"
    [ "$status" -eq 0 ]
    [[ "$output" == *"passed"* ]]
}

@test "WSMOKE.7 脚本自身平台无关（check-platform-assumptions.py 扫描 0 命中）" {
    local script="$AGATE_ROOT/tests/scripts/check-windows-smoke.sh"
    run "$PYTHON" "$AGATE_SCRIPTS/check-platform-assumptions.py" "$script"
    [ "$status" -eq 0 ]
    [ -z "$output" ]
}
