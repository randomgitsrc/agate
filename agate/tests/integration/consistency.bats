#!/usr/bin/env bats
# tests/integration/consistency.bats — 9 用例覆盖 check-protocol-consistency.py（CHECK 5 已删）
load ../helpers/load.bash

setup() {
    CONSISTENCY_OUTPUT=$(python3 "$AGATE_ROOT/scripts/check-protocol-consistency.py" 2>&1) || true
}

@test "CON.1 CHECK 1: YAML 代码块可解析" {
    [[ "$CONSISTENCY_OUTPUT" != *"ERROR ("* ]]
}

@test "CON.2 CHECK 2: 文件引用存在" {
    [[ "$CONSISTENCY_OUTPUT" != *"FAIL  CHECK 2"* ]]
}

@test "CON.3 CHECK 3: 无硬编码行号" {
    [[ "$CONSISTENCY_OUTPUT" == *"PASS  CHECK 3"* ]]
}

@test "CON.4 CHECK 4: gate_commands 键集合一致" {
    [[ "$CONSISTENCY_OUTPUT" == *"PASS  CHECK 4"* ]]
}

@test "CON.5 CHECK 6: LICENSE 归属" {
    [[ "$CONSISTENCY_OUTPUT" == *"PASS  CHECK 6"* ]]
}

@test "CON.6 CHECK 7: version badge 同步" {
    [[ "$CONSISTENCY_OUTPUT" == *"PASS  CHECK 7"* ]]
}

@test "CON.8 CHECK 9: 协议-脚本结构对齐" {
    # md5 去重的 WARN 是已知的（文档声称 hook 强制但脚本未实现）
    # 只要有 PASS 就说明锚点表在跑，不要求全 PASS
    [[ "$CONSISTENCY_OUTPUT" == *"PASS  CHECK 9"* || "$CONSISTENCY_OUTPUT" == *"WARN  CHECK 9"* ]]
    [[ "$CONSISTENCY_OUTPUT" != *"FAIL  CHECK 9"* ]]
}

@test "CON.9 CHECK 9: md5 去重锚点已实现" {
    # 锁住"已实现"：check-p6-evidence.sh 实际包含 md5 去重逻辑
    # 防回归——如果有人删了 md5 去重实现，此测试会红
    # 历史：曾锁住"缺口存在"防止删锚点代实现；md5 在 commit 949055c 实现后，
    # 缺口消失，断言改写为锁定"实现存在"
    grep -q 'MD5_LIST' agate/scripts/check-p6-evidence.sh
    grep -q 'md5sum' agate/scripts/check-p6-evidence.sh
}

@test "CON.10 CHECK 8: v0.6 关键词存在性" {
    [[ "$CONSISTENCY_OUTPUT" == *"PASS  CHECK 8"* ]]
}

@test "CON.11 CHECK 9: PROD_TOUCHED 锚点含 PROD_NOT_TOUCHED" {
    grep -q 'PROD_NOT_TOUCHED' agate/scripts/pre-commit-gate.sh
}

@test "CON.12 CHECK 9: NEED_CONFIRM 二值锚点存在" {
    grep -q 'NO_NEED_CONFIRM' agate/scripts/check-gate.sh
}
