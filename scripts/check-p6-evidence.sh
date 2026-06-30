#!/usr/bin/env bash
# check-p6-evidence.sh — P6 证据格式检查（P1.7）
# 检查 P6-evidence/ 目录非空（现有协议已支持）
# 注意：完整的"每条 BDD 有 Evidence 引用"检查需要协议定义
# ## BDD-NN 标题和 Evidence: 字段格式，这属于 Phase 2B 协议改动。
# 当前退化为：BDD 条目数（- PASS/- FAIL 行）= 证据文件数（M1 修复）
# exit 0 = 通过; exit 1 = 证据缺失; exit 2 = 无 P6 文件

set -euo pipefail

TASK_DIR="${1:?用法: check-p6-evidence.sh TASK_DIR}"
P6_FILE="$TASK_DIR/P6-acceptance.md"

[ ! -f "$P6_FILE" ] && exit 2

# 用现有协议约定的格式计数（- PASS / - FAIL 行）
BDD_COUNT=$(grep -cE '^\s*- (PASS|FAIL)' "$P6_FILE" || echo 0)

if [ "$BDD_COUNT" -eq 0 ]; then
    echo "GATE P6-EVIDENCE: P6-acceptance.md 无 BDD 条目（- PASS/- FAIL 格式）" >&2
    exit 1
fi

# 检查 P6-evidence/ 目录非空
EVIDENCE_DIR="$TASK_DIR/P6-evidence"
if [ ! -d "$EVIDENCE_DIR" ] || [ -z "$(ls -A "$EVIDENCE_DIR" 2>/dev/null)" ]; then
    echo "GATE P6-EVIDENCE: P6-evidence/ 目录不存在或为空" >&2
    exit 1
fi

echo "GATE P6-EVIDENCE: ${BDD_COUNT} 条 BDD，证据目录非空" >&2
exit 0
