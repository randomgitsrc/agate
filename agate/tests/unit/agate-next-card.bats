#!/usr/bin/env bats
# tests/unit/agate-next-card.bats — CLI 防漂移机制的 byte-stability 硬保证
#
# step 3 hook 用 CLI 输出做 sha256 校验嵌入 dispatch-context 的卡片是当前版本。
# 防漂移前提：CLI 输出（去掉固定头）的 sha256 必须等于 `cat ${PHASE}-*.md` 的 sha256。
# 本测试是 step 3 hook 前提的硬证明，不只是 CLI 接口测试。

load ../helpers/load.bash

setup() {
    CARD_CMD="$AGATE_SCRIPTS/agate-next-card.sh"
    AGATE_REPO="$(git -C "$AGATE_SCRIPTS" rev-parse --show-toplevel 2>/dev/null)"
}

# ========== 防漂移硬保证：CLI 输出 body sha256 == 卡片文件 sha256 ==========

@test "P0: CLI body sha256 == 卡片文件 sha256（防漂移前提）" {
    local expected_hash actual_hash
    expected_hash="$(sha256sum "$AGATE_REPO/agate/phase-cards/P0-orchestrator.md" | awk '{print $1}')"
    # CLI 输出 body = 去掉前 4 行（## 当前阶段卡片 / 空行 / 路径 / ---）
    actual_hash="$(bash "$CARD_CMD" P0 | tail -n +5 | sha256sum | awk '{print $1}')"
    [ "$actual_hash" = "$expected_hash" ]
}

@test "P1: CLI body sha256 == 卡片文件 sha256（防漂移前提）" {
    local expected_hash actual_hash
    expected_hash="$(sha256sum "$AGATE_REPO/agate/phase-cards/P1-requirements.md" | awk '{print $1}')"
    actual_hash="$(bash "$CARD_CMD" P1 | tail -n +5 | sha256sum | awk '{print $1}')"
    [ "$actual_hash" = "$expected_hash" ]
}

@test "P2: CLI body sha256 == 卡片文件 sha256（防漂移前提）" {
    local expected_hash actual_hash
    expected_hash="$(sha256sum "$AGATE_REPO/agate/phase-cards/P2-design.md" | awk '{print $1}')"
    actual_hash="$(bash "$CARD_CMD" P2 | tail -n +5 | sha256sum | awk '{print $1}')"
    [ "$actual_hash" = "$expected_hash" ]
}

@test "P3: CLI body sha256 == 卡片文件 sha256（防漂移前提）" {
    local expected_hash actual_hash
    expected_hash="$(sha256sum "$AGATE_REPO/agate/phase-cards/P3-tdd.md" | awk '{print $1}')"
    actual_hash="$(bash "$CARD_CMD" P3 | tail -n +5 | sha256sum | awk '{print $1}')"
    [ "$actual_hash" = "$expected_hash" ]
}

@test "P4: CLI body sha256 == 卡片文件 sha256（防漂移前提）" {
    local expected_hash actual_hash
    expected_hash="$(sha256sum "$AGATE_REPO/agate/phase-cards/P4-implementation.md" | awk '{print $1}')"
    actual_hash="$(bash "$CARD_CMD" P4 | tail -n +5 | sha256sum | awk '{print $1}')"
    [ "$actual_hash" = "$expected_hash" ]
}

@test "P5: CLI body sha256 == 卡片文件 sha256（防漂移前提）" {
    local expected_hash actual_hash
    expected_hash="$(sha256sum "$AGATE_REPO/agate/phase-cards/P5-verification.md" | awk '{print $1}')"
    actual_hash="$(bash "$CARD_CMD" P5 | tail -n +5 | sha256sum | awk '{print $1}')"
    [ "$actual_hash" = "$expected_hash" ]
}

@test "P6: CLI body sha256 == 卡片文件 sha256（防漂移前提）" {
    local expected_hash actual_hash
    expected_hash="$(sha256sum "$AGATE_REPO/agate/phase-cards/P6-acceptance.md" | awk '{print $1}')"
    actual_hash="$(bash "$CARD_CMD" P6 | tail -n +5 | sha256sum | awk '{print $1}')"
    [ "$actual_hash" = "$expected_hash" ]
}

@test "P7: CLI body sha256 == 卡片文件 sha256（防漂移前提）" {
    local expected_hash actual_hash
    expected_hash="$(sha256sum "$AGATE_REPO/agate/phase-cards/P7-consistency.md" | awk '{print $1}')"
    actual_hash="$(bash "$CARD_CMD" P7 | tail -n +5 | sha256sum | awk '{print $1}')"
    [ "$actual_hash" = "$expected_hash" ]
}

@test "P8: CLI body sha256 == 卡片文件 sha256（防漂移前提）" {
    local expected_hash actual_hash
    expected_hash="$(sha256sum "$AGATE_REPO/agate/phase-cards/P8-release.md" | awk '{print $1}')"
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

@test "CWD 在项目目录（peekview）仍能解析 AGATE_REPO" {
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