#!/usr/bin/env bash
# check-gate.sh PHASE TASK_DIR
# exit 0 = gate 通过; exit 1 = gate 未通过; exit 2 = 需主 Agent 自判（含动态 gate_commands 或语义判断）
#
# 可脚本化的 gate（exit 0/1）：P3 / P4 / P7
# 需主 Agent 自判的 gate（exit 2）：P1 / P2 / P5 / P6 / P8
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
      if [ "$FAIL" -ne 0 ] || [ "$NC" -ne 0 ] || [ "$TOTAL" -eq 0 ]; then
          echo "GATE P6: FAIL=$FAIL, NEED_CONFIRM=$NC, TOTAL=$TOTAL" >&2
          exit 1
      fi
      # 证据存在性检查（⚠️ self-authored gate 的缓解措施）
      EVIDENCE_DIR="$TASK_DIR/P6-evidence"
      if [ ! -d "$EVIDENCE_DIR" ] || [ -z "$(ls -A "$EVIDENCE_DIR" 2>/dev/null)" ]; then
          echo "GATE P6: P6-evidence/ 目录不存在或为空" >&2
          exit 1
      fi
      echo "GATE P6: 证据目录非空，FAIL=0，NC=0，P6_TOTAL=$TOTAL。BDD 总数对照需主 Agent 手动核实 P1 条数。" >&2
      exit 2 ;;
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
      # P8 部分检查可脚本化，其余需主 Agent 自判
      # 注意：version 文件路径和 CHANGELOG 文件名因项目而异，
      # 主 Agent 应从 P2-design.md packages 字段读取具体路径。
      # 以下检查使用通用模式，可能需要主 Agent 补充验证。
      # git diff HEAD~1 假设 P8 为单次 commit；若多 commit，主 Agent 需手动验证。
      RC=0
      # 检查 bump_type 字段
      if ! grep -q 'bump_type:' "$TASK_DIR/P8-release.md" 2>/dev/null; then
          echo "GATE P8: P8-release.md 缺 bump_type 字段" >&2
          RC=1
      fi
      # 检查 version 文件变更（通用匹配，主 Agent 应从 P2 packages 补充验证）
      if ! git diff HEAD~1 --stat 2>/dev/null | grep -qiE 'version|__version__|package.json|Cargo.toml|pyproject.toml|go.mod|pom.xml|gemspec|csproj'; then
          echo "GATE P8: HEAD~1 无 version 文件变更（若项目用其他文件管理版本，主 Agent 需从 P2 packages 手动验证）" >&2
          RC=1
      fi
      # 检查 CHANGELOG 变更（默认 CHANGELOG.md，项目可用 CHANGELOG_FILE 环境变量覆盖）
      CHANGELOG_FILE="${CHANGELOG_FILE:-CHANGELOG.md}"
      if ! git diff HEAD~1 -- "$CHANGELOG_FILE" 2>/dev/null | grep -q .; then
          echo "GATE P8: ${CHANGELOG_FILE} 无变更（若项目用其他 changelog 文件，设置 CHANGELOG_FILE 环境变量）" >&2
          RC=1
      fi
      if [ "$RC" -ne 0 ]; then
          exit 1
      fi
      echo "GATE P8: 脚本化检查通过。仍需主 Agent：① 从 P2 gate_commands 逐包读取发布检查命令 ② 重跑 P5 gate ③ 用 git log 对照 CHANGELOG 无遗漏 ④ 从 P2 packages 验证 version 文件路径" >&2
      exit 2 ;;
  *)
      echo "未知阶段: $PHASE" >&2
      exit 2 ;;
esac
