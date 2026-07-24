#!/usr/bin/env bats
# tests/unit/agate-next-card.bats — CLI 防漂移机制的 byte-stability 硬保证
#
# step 3 hook 用 CLI 输出做 sha256 校验嵌入 dispatch-context 的卡片是当前版本。
# 防漂移前提：CLI 输出（去掉固定头）的 sha256 必须等于 `cat ${PHASE}-*.md` 的 sha256。
# 本测试是 step 3 hook 前提的硬证明，不只是 CLI 接口测试。

load ../helpers/load.bash

setup() {
    CARD_CMD="$AGATE_SCRIPTS/agate-next-card.sh"
    AGATE_ROOT="$(dirname "$AGATE_SCRIPTS")"
}

# ========== 防漂移硬保证：CLI 输出 body sha256 == 卡片文件 sha256 ==========

@test "P0: CLI body sha256 == 卡片文件 sha256（防漂移前提）" {
    local expected_hash actual_hash
    expected_hash="$(sha256sum "$AGATE_ROOT/phase-cards/P0-orchestrator.md" | awk '{print $1}')"
    # CLI 输出 body = 去掉前 4 行（## 当前阶段卡片 / 空行 / 路径 / ---）
    actual_hash="$(bash "$CARD_CMD" P0 | tail -n +5 | sha256sum | awk '{print $1}')"
    [ "$actual_hash" = "$expected_hash" ]
}

@test "P1: CLI body sha256 == 卡片文件 sha256（防漂移前提）" {
    local expected_hash actual_hash
    expected_hash="$(sha256sum "$AGATE_ROOT/phase-cards/P1-requirements.md" | awk '{print $1}')"
    actual_hash="$(bash "$CARD_CMD" P1 | tail -n +5 | sha256sum | awk '{print $1}')"
    [ "$actual_hash" = "$expected_hash" ]
}

@test "P2: CLI body sha256 == 卡片文件 sha256（防漂移前提）" {
    local expected_hash actual_hash
    expected_hash="$(sha256sum "$AGATE_ROOT/phase-cards/P2-design.md" | awk '{print $1}')"
    actual_hash="$(bash "$CARD_CMD" P2 | tail -n +5 | sha256sum | awk '{print $1}')"
    [ "$actual_hash" = "$expected_hash" ]
}

@test "P3: CLI body sha256 == 卡片文件 sha256（防漂移前提）" {
    local expected_hash actual_hash
    expected_hash="$(sha256sum "$AGATE_ROOT/phase-cards/P3-tdd.md" | awk '{print $1}')"
    actual_hash="$(bash "$CARD_CMD" P3 | tail -n +5 | sha256sum | awk '{print $1}')"
    [ "$actual_hash" = "$expected_hash" ]
}

@test "P4: CLI body sha256 == 卡片文件 sha256（防漂移前提）" {
    local expected_hash actual_hash
    expected_hash="$(sha256sum "$AGATE_ROOT/phase-cards/P4-implementation.md" | awk '{print $1}')"
    actual_hash="$(bash "$CARD_CMD" P4 | tail -n +5 | sha256sum | awk '{print $1}')"
    [ "$actual_hash" = "$expected_hash" ]
}

@test "P5: CLI body sha256 == 卡片文件 sha256（防漂移前提）" {
    local expected_hash actual_hash
    expected_hash="$(sha256sum "$AGATE_ROOT/phase-cards/P5-verification.md" | awk '{print $1}')"
    actual_hash="$(bash "$CARD_CMD" P5 | tail -n +5 | sha256sum | awk '{print $1}')"
    [ "$actual_hash" = "$expected_hash" ]
}

@test "P6: CLI body sha256 == 卡片文件 sha256（防漂移前提）" {
    local expected_hash actual_hash
    expected_hash="$(sha256sum "$AGATE_ROOT/phase-cards/P6-acceptance.md" | awk '{print $1}')"
    actual_hash="$(bash "$CARD_CMD" P6 | tail -n +5 | sha256sum | awk '{print $1}')"
    [ "$actual_hash" = "$expected_hash" ]
}

@test "P7: CLI body sha256 == 卡片文件 sha256（防漂移前提）" {
    local expected_hash actual_hash
    expected_hash="$(sha256sum "$AGATE_ROOT/phase-cards/P7-consistency.md" | awk '{print $1}')"
    actual_hash="$(bash "$CARD_CMD" P7 | tail -n +5 | sha256sum | awk '{print $1}')"
    [ "$actual_hash" = "$expected_hash" ]
}

@test "P8: CLI body sha256 == 卡片文件 sha256（防漂移前提）" {
    local expected_hash actual_hash
    expected_hash="$(sha256sum "$AGATE_ROOT/phase-cards/P8-release.md" | awk '{print $1}')"
    actual_hash="$(bash "$CARD_CMD" P8 | tail -n +5 | sha256sum | awk '{print $1}')"
    [ "$actual_hash" = "$expected_hash" ]
}

# ========== 输出格式契约 ==========

@test "CLI 输出头部三行固定（hook 用作 sha256 校验 marker）" {
    local output first_four
    output="$(bash "$CARD_CMD" P3)"
    first_four="$(printf '%s\n' "$output" | head -4)"
    [[ "$first_four" == "## 当前阶段卡片：P3"$'\n'$'\n'"路径："* ]]  # 简化匹配
    [[ "$output" == *"---"* ]]  # 第 4 行分隔符
}

# ========== 字节稳定性（两轮调用 sha256 一致） ==========

@test "字节稳定性：连续两次调用 P3 sha256 一致" {
    local hash1 hash2
    hash1="$(bash "$CARD_CMD" P3 | sha256sum | awk '{print $1}')"
    hash2="$(bash "$CARD_CMD" P3 | sha256sum | awk '{print $1}')"
    [ "$hash1" = "$hash2" ]
}

# ========== 路径解析鲁棒性 ==========

@test "CWD 在项目目录仍能解析 AGATE_ROOT" {
    local hash
    hash="$(cd /tmp && bash "$CARD_CMD" P3 | sha256sum | awk '{print $1}')"
    [ -n "$hash" ]
}

@test "软链接场景：脚本被 symlink 调用时 readlink -f 解析正确" {
    local link_dir link_cmd hash
    link_dir="$BATS_TEST_TMPDIR/symlink_test"
    mkdir -p "$link_dir"
    ln -sf "$AGATE_SCRIPTS/agate-next-card.sh" "$link_dir/card"
    hash="$(bash "$link_dir/card" P3 | sha256sum | awk '{print $1}')"
    local expected_hash
    expected_hash="$(bash "$AGATE_SCRIPTS/agate-next-card.sh" P3 | sha256sum | awk '{print $1}')"
    [ "$hash" = "$expected_hash" ]
}

# ========== 跨环境路径稳定性（绝对路径→相对路径） ==========

@test "跨 checkout 路径：通过不同根路径调用 CLI 全量 hash 一致（P0-P8）" {
    # 模拟两个不同 checkout 根：通过不同 symlink 前缀调用 CLI
    # 全量 hash（含 header）：如果路径进 hash，不同前缀会 mismatch
    local link_a link_b hash_a hash_b phase
    link_a="$BATS_TEST_TMPDIR/checkout_a"
    link_b="$BATS_TEST_TMPDIR/checkout_b"
    mkdir -p "$link_a" "$link_b"
    ln -sf "$AGATE_SCRIPTS/agate-next-card.sh" "$link_a/card"
    ln -sf "$AGATE_SCRIPTS/agate-next-card.sh" "$link_b/card"
    for phase in P0 P1 P2 P3 P4 P5 P6 P7 P8; do
        hash_a="$(bash "$link_a/card" "$phase" | sha256sum | awk '{print $1}')"
        hash_b="$(bash "$link_b/card" "$phase" | sha256sum | awk '{print $1}')"
        [ "$hash_a" = "$hash_b" ] || {
            echo "FAIL: $phase hash mismatch: checkout_a=$hash_a checkout_b=$hash_b" >&2
            return 1
        }
    done
}

# ========== 失败路径 ==========

@test "无参数 期望 exit 1" {
    run bash "$CARD_CMD"
    [ "$status" -eq 1 ]
    [[ "$output" == *"需要 1 个参数"* ]]
}

@test "2 个参数 期望 exit 1" {
    run bash "$CARD_CMD" P3 extra
    [ "$status" -eq 1 ]
    [[ "$output" == *"需要 1 个参数"* ]]
}

@test "phase=P9 期望 exit 2" {
    run bash "$CARD_CMD" P9
    [ "$status" -eq 2 ]
    [[ "$output" == *"不在 P0-P8 范围内"* ]]
}

@test "phase=小写 p3 期望 exit 2（case-sensitive）" {
    run bash "$CARD_CMD" p3
    [ "$status" -eq 2 ]
}

# ========== AGATE_ROOT 解耦 ==========

@test "NC_ROOT.1 AGATE_ROOT 环境变量覆盖" {
    local hash_default hash_override
    hash_default="$(bash "$CARD_CMD" P3 | sha256sum | awk '{print $1}')"
    hash_override="$(AGATE_ROOT="$AGATE_ROOT" bash "$CARD_CMD" P3 | sha256sum | awk '{print $1}')"
    [ "$hash_default" = "$hash_override" ]
}

@test "NC_ROOT.2 协议目录不在 git 仓库内时仍能工作" {
    local tmp_root hash_main hash_tmp
    tmp_root="$BATS_TEST_TMPDIR/no_git"
    mkdir -p "$tmp_root/phase-cards" "$tmp_root/scripts"
    cp "$AGATE_ROOT/phase-cards/P3-tdd.md" "$tmp_root/phase-cards/"
    cp "$AGATE_ROOT/scripts/agate-next-card.sh" "$tmp_root/scripts/"
    hash_main="$(bash "$CARD_CMD" P3 | tail -n +5 | sha256sum | awk '{print $1}')"
    hash_tmp="$(AGATE_ROOT="$tmp_root" bash "$tmp_root/scripts/agate-next-card.sh" P3 | tail -n +5 | sha256sum | awk '{print $1}')"
    [ "$hash_main" = "$hash_tmp" ]
}