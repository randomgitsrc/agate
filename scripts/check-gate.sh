#!/usr/bin/env bash
# check-gate.sh PHASE TASK_DIR
# exit 0 = gate 通过; exit 1 = gate 未通过; exit 2 = 需主 Agent 自判（含动态 gate_commands 或语义判断）
#
# 可脚本化的 gate（exit 0/1）：P3 / P4 / P6 / P7
# 需动态读取 P2 gate_commands 的 gate（exit 2）：P2 / P5 / P8
# 含语义判断的 gate（exit 2）：P1（BDD 格式不固定）
#
# 本脚本的判定逻辑与 state-machine.md 步骤 5 保持同步。
# 步骤 5 变更时必须同步更新本脚本。一致性检查脚本覆盖本文件。

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PHASE="${1:?用法: check-gate.sh PHASE TASK_DIR}"
TASK_DIR="${2:?用法: check-gate.sh PHASE TASK_DIR}"

case "$PHASE" in
  P1)
      echo "GATE P1: BDD 编号格式不固定，需主 Agent 自行判定" >&2
      exit 2 ;;
  P2)
      echo "GATE P2: 需从 P2-design.md gate_commands 动态读取，主 Agent 自行判定" >&2
      exit 2 ;;
  P3)
      exec "$SCRIPT_DIR/check-tdd-red.sh" ;;
  P4)
      # 查最近 5 条 commit（P4 commit 后可能有 .state.yaml 更新 commit）
      git log --oneline -5 | grep -qE 'P4|wf\(T[0-9]+-P4\)' && exit 0 || exit 1 ;;
  P5)
      echo "GATE P5: 需从 P2-design.md gate_commands.P5 动态读取，主 Agent 自行判定" >&2
      exit 2 ;;
  P6)
      # grep -c 无匹配时返回 exit 1，|| echo 0 处理此情况
      TOTAL=$(grep -cE '^\s*- (PASS|FAIL)' "$TASK_DIR/P6-acceptance.md" 2>/dev/null || echo 0)
      FAIL=$(grep -cE '^\s*- FAIL\b' "$TASK_DIR/P6-acceptance.md" 2>/dev/null || echo 0)
      NC=$(grep -cE '\[NEED_CONFIRM\]' "$TASK_DIR/P6-acceptance.md" 2>/dev/null || echo 0)
      if [ "$FAIL" -eq 0 ] && [ "$NC" -eq 0 ] && [ "$TOTAL" -gt 0 ]; then
          echo "GATE P6: PASS. 注意：BDD 总数对照需主 Agent 在步骤 5 手动验证" >&2
          exit 0
      else
          echo "GATE P6: FAIL=$FAIL, NEED_CONFIRM=$NC, TOTAL=$TOTAL" >&2
          exit 1
      fi ;;
  P7)
      # grep -c 无匹配时返回 exit 1，|| echo 0 处理此情况
      BLOCKERS=$(grep -cE '^\s*-?\s*\[BLOCKER\]' "$TASK_DIR/P7-consistency.md" 2>/dev/null || echo 0)
      DEVCRIT=$(grep -cE '^\s*-?\s*\[DEVIATION-CRITICAL\]' "$TASK_DIR/P7-consistency.md" 2>/dev/null || echo 0)
      if [ "$BLOCKERS" -eq 0 ] && [ "$DEVCRIT" -eq 0 ]; then
          exit 0
      else
          echo "GATE P7: BLOCKER=$BLOCKERS, DEVIATION-CRITICAL=$DEVCRIT" >&2
          exit 1
      fi ;;
  P8)
      echo "GATE P8: 需从 P2-design.md gate_commands 逐包动态读取，主 Agent 自行判定" >&2
      exit 2 ;;
  *)
      echo "未知阶段: $PHASE" >&2
      exit 2 ;;
esac
