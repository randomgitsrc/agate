#!/usr/bin/env bash
# check-gate.sh PHASE TASK_DIR
# exit 0 = gate 通过; exit 1 = gate 未通过; exit 2 = 需主 Agent 自判（含动态 gate_commands 或语义判断）
#
# 可脚本化的 gate（exit 0/1）：P3 / P4 / P7
# 需主 Agent 自判的 gate（exit 2）：P0 / P1 / P2 / P5 / P6 / P8
#
# 本脚本的判定逻辑与 state-machine.md 步骤 5 保持同步。
# 步骤 5 变更时必须同步更新本脚本。一致性检查脚本覆盖本文件。

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PHASE="${1:?用法: check-gate.sh PHASE TASK_DIR}"
TASK_DIR="${2:?用法: check-gate.sh PHASE TASK_DIR}"

case "$PHASE" in
  P0)
      echo "GATE P0: 立项阶段无需脚本 gate（仅 P0-brief.md）。主 Agent 确认 P0-brief 五字段齐全即可推进 P1。" >&2
      exit 2 ;;
  P1)
      P1_REVIEW="$TASK_DIR/P1-review.md"
      if [ ! -f "$P1_REVIEW" ]; then
          echo "GATE P1: P1-review.md 不存在——P1 评审不可裁，所有任务都需独立 requirements-review" >&2
          exit 1
      fi
      P1_REVIEW_STATUS=$(sed -n '/^---$/,/^---$/p' "$P1_REVIEW" | { grep '^status:' || true; } | sed 's/^status:\s*//' | head -1)
      if [ "$P1_REVIEW_STATUS" != "approved" ]; then
          echo "GATE P1: P1-review.md frontmatter status 非 approved（当前: ${P1_REVIEW_STATUS:-缺失}）" >&2
          exit 1
      fi
      P1_REVIEW_AGENT=$(sed -n '/^---$/,/^---$/p' "$P1_REVIEW" | { grep '^agent:' || true; } | sed 's/^agent:\s*//' | head -1)
      if [ -z "$P1_REVIEW_AGENT" ]; then
          echo "GATE P1: P1-review.md status:approved 但缺 agent 字段" >&2
          exit 1
      fi
      if [ "$P1_REVIEW_AGENT" = "main" ]; then
          echo "GATE P1: P1-review.md status:approved 但 agent=main（主 Agent 不可自行批准评审）" >&2
          exit 1
      fi
      if ! grep -qE 'BDD-|B[0-9]' "$P1_REVIEW" 2>/dev/null; then
          echo "GATE P1: P1-review.md 不含 BDD 编号引用（裸 approved 极可能是假完成，review 结论须引用具体 BDD 编号）" >&2
          exit 1
      fi
      # P1 NEED_CONFIRM 检查（与 P6 对称）——v0.17 三步检测
      P1_FILE="$TASK_DIR/P1-requirements.md"
      NC=$(grep -cE '^\s*-?\s*\[NEED_CONFIRM\]' "$P1_FILE" 2>/dev/null || echo 0)
      NC=$(echo "$NC" | tail -1)
      if [ "$NC" -gt 0 ]; then
          echo "GATE P1: $NC 个未解决的 NEED_CONFIRM 项" >&2
          exit 1
      fi
      if grep -q '\[NEED_CONFIRM\]' "$P1_FILE" 2>/dev/null; then
          echo "GATE P1: 不合规的 NEED_CONFIRM 标记格式（须用行首 [NEED_CONFIRM] 或 [NO_NEED_CONFIRM] 声明）" >&2
          exit 1
      fi
      if ! grep -qE '^\s*-?\s*\[NO_NEED_CONFIRM\]' "$P1_FILE" 2>/dev/null; then
          echo "GATE P1 WARNING: 未检测到 NEED_CONFIRM 声明（[NEED_CONFIRM] 或 [NO_NEED_CONFIRM]）" >&2
      fi
      echo "GATE P1: P1-review.md approved + agent≠main + 含 BDD 锚点。BDD 编号格式不固定，需主 Agent 自行判定" >&2
      exit 2 ;;
  P2)
      # v0.6：多方案探索检查（nudge 强度）
      # P2 不可裁剪，不存在 P2-design.md 时直接报错
      P2_FILE="$TASK_DIR/P2-design.md"
      if [ -f "$P2_FILE" ]; then
          CANDIDATE_COUNT=$(grep -cE '^###?\s*(候选方案|方案\s*[A-Za-z0-9一二三四五]|Alternative|Option)' "$P2_FILE" 2>/dev/null || echo 0)
          CANDIDATE_COUNT=$(echo "$CANDIDATE_COUNT" | tail -1)
          P1_FILE="$TASK_DIR/P1-requirements.md"
          MIN_CANDIDATES=2
          if [ -f "$P1_FILE" ]; then
              if grep -qE '^(design_trivial|follows_existing_pattern):\s*\S' "$P1_FILE" 2>/dev/null; then
                  MIN_CANDIDATES=1
              fi
          fi
          if [ "$CANDIDATE_COUNT" -lt "$MIN_CANDIDATES" ]; then
              echo "GATE P2: P2-design.md 需至少 ${MIN_CANDIDATES} 个候选方案 + 权衡 + 选择理由（design_trivial/follows_existing_pattern 时可只写 1 个）" >&2
              exit 1
          fi
          P2_REVIEW="$TASK_DIR/P2-review.md"
          if [ -f "$P2_REVIEW" ]; then
              P2_REVIEW_STATUS=$(sed -n '/^---$/,/^---$/p' "$P2_REVIEW" | { grep '^status:' || true; } | sed 's/^status:\s*//' | head -1)
              if [ "$P2_REVIEW_STATUS" != "approved" ]; then
                  echo "GATE P2: P2-review.md frontmatter status 非 approved（当前: ${P2_REVIEW_STATUS:-缺失}）" >&2
                  exit 1
              fi
              P2_REVIEW_AGENT=$(sed -n '/^---$/,/^---$/p' "$P2_REVIEW" | { grep '^agent:' || true; } | sed 's/^agent:\s*//' | head -1)
              if [ -z "$P2_REVIEW_AGENT" ]; then
                  echo "GATE P2: P2-review.md status:approved 但缺 agent 字段（向后兼容 WARNING）" >&2
                  exit 2
              fi
              if [ "$P2_REVIEW_AGENT" = "main" ]; then
                  echo "GATE P2: P2-review.md status:approved 但 agent=main（主 Agent 不可自行批准评审）" >&2
                  exit 1
              fi
          fi
          FIELD_COUNT=$(grep -cE '^(packages|domains|ui_affected|gate_commands):' "$P2_FILE" 2>/dev/null || echo 0)
          FIELD_COUNT=$(echo "$FIELD_COUNT" | tail -1)
          if [ "$FIELD_COUNT" -lt 4 ]; then
              echo "GATE P2: P2-design.md 缺字段（需 packages/domains/ui_affected/gate_commands 四字段，实际 ${FIELD_COUNT}）" >&2
              exit 1
          fi
          if grep -qE '权衡|选择理由|取舍|考量|trade-?off|理由与权衡' "$P2_FILE" 2>/dev/null; then
              :
          elif grep -qE '选择' "$P2_FILE" 2>/dev/null && grep -qE '理由|原因|因为' "$P2_FILE" 2>/dev/null; then
              :
          else
              echo "GATE P2: P2-design.md 有 ≥2 候选方案但缺'权衡'或'选择理由'描述" >&2
              exit 1
          fi
      else
          echo "GATE P2: P2-design.md 不存在——P2 不可裁剪，方案设计是必经阶段" >&2
          exit 1
      fi
      echo "GATE P2: 需从 P2-design.md gate_commands 动态读取，主 Agent 自行判定" >&2
      exit 2 ;;
  P3)
      exec "$SCRIPT_DIR/check-tdd-red.sh" ;;
  P4)
      # pre-commit 阶段：检查暂存区有代码文件（非纯文档/状态文件）
      # N1 修复：原来查 git log，但 pre-commit 时 commit 还没创建，第一条 P4 commit 永远无法通过
      git diff --cached --name-only | grep -qvE '(^|/)P[0-8]-.*\.md$|(^|/)\.state\.yaml$' && exit 0 || exit 1 ;;
  P5)
      echo "GATE P5: 需从 P2-design.md gate_commands.P5 动态读取，主 Agent 自行判定" >&2
      # WARNING: 如果 P2 声明了多个 gate_commands.P5 命令（单元+集成+E2E），
      # 提醒主 Agent 确认是否全部执行（T060 教训：只跑子集可能掩盖预存失败）
      if [ -f "$TASK_DIR/P2-design.md" ]; then
          P5_CMD_COUNT=$(grep -cE '^\s+- ' "$TASK_DIR/P2-design.md" 2>/dev/null || echo 0)
          P5_CMD_COUNT=$(echo "$P5_CMD_COUNT" | tail -1)
          if [ "$P5_CMD_COUNT" -gt 1 ]; then
              echo "GATE P5 WARNING: P2 声明了 ${P5_CMD_COUNT} 个 gate_commands.P5 命令，请确认已全部执行（非子集）。" >&2
              echo "  T060 教训：只跑子集可能掩盖预存失败（T056 venv 遗漏跨 4 个任务周期无人发现）。" >&2
          fi
      fi
      exit 2 ;;
  P6)
      # P6 PASS/FAIL regex: 大小写不敏感计数（formatter 归一化在前，此为最后防线）
      TOTAL=$(grep -ciE '^\s*- (PASS|FAIL)' "$TASK_DIR/P6-acceptance.md" 2>/dev/null || echo 0)
      TOTAL=$(echo "$TOTAL" | tail -1)
      FAIL=$(grep -ciE '^\s*- FAIL([[:space:]:：]|$)' "$TASK_DIR/P6-acceptance.md" 2>/dev/null || echo 0)
      FAIL=$(echo "$FAIL" | tail -1)
      NC=$(grep -cE '^\s*-?\s*\[NEED_CONFIRM\]' "$TASK_DIR/P6-acceptance.md" 2>/dev/null || echo 0)
      NC=$(echo "$NC" | tail -1)
      if [ "$NC" -gt 0 ]; then
          echo "GATE P6: FAIL=$FAIL, NEED_CONFIRM=$NC, TOTAL=$TOTAL" >&2
          exit 1
      fi
      if grep -q '\[NEED_CONFIRM\]' "$TASK_DIR/P6-acceptance.md" 2>/dev/null; then
          echo "GATE P6: 不合规的 NEED_CONFIRM 标记格式（须用行首 [NEED_CONFIRM] 或 [NO_NEED_CONFIRM] 声明）" >&2
          exit 1
      fi
      if ! grep -qE '^\s*-?\s*\[NO_NEED_CONFIRM\]' "$TASK_DIR/P6-acceptance.md" 2>/dev/null; then
          echo "GATE P6 WARNING: 未检测到 NEED_CONFIRM 声明（[NEED_CONFIRM] 或 [NO_NEED_CONFIRM]）" >&2
      fi
      if [ "$FAIL" -ne 0 ] || [ "$TOTAL" -eq 0 ]; then
          echo "GATE P6: FAIL=$FAIL, TOTAL=$TOTAL" >&2
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
      # v0.6：用显式 if/elif/else 替代链式写法——每加一个检查都要在链路里加新项，if 更易读易扩展
      # grep -c 无匹配时返回 exit 1，|| echo 0 处理此情况
      P7_FILE="$TASK_DIR/P7-consistency.md"
      BLOCKERS=$(grep -E '^\s*-?\s*\[BLOCKER\]' "$P7_FILE" 2>/dev/null | grep -cvE '\[BLOCKER\][:：]?[[:space:]]*[0-9]+[[:space:]]*条?[[:space:]]*$' || echo 0)
      DEVCRIT=$(grep -E '^\s*-?\s*\[DEVIATION-CRITICAL\]' "$P7_FILE" 2>/dev/null | grep -cvE '\[DEVIATION-CRITICAL\][:：]?[[:space:]]*[0-9]+[[:space:]]*条?[[:space:]]*$' || echo 0)
      BLOCKERS=$(echo "$BLOCKERS" | tail -1)
      DEVCRIT=$(echo "$DEVCRIT" | tail -1)
      if [ "$BLOCKERS" -gt 0 ] || [ "$DEVCRIT" -gt 0 ]; then
          echo "GATE P7: BLOCKER=$BLOCKERS, DEVIATION-CRITICAL=$DEVCRIT" >&2
          exit 1
      fi
      # DESIGN_GAP 配对检查（v0.6：未配对 REVIEWED 标记的 DESIGN_GAP → 不通过）
      DESIGN_GAP_COUNT=$(grep -cE '^\s*-?\s*\[DESIGN_GAP:' "$P7_FILE" 2>/dev/null || echo 0)
      DESIGN_GAP_REVIEWED=$(grep -cE '^\s*-?\s*\[DESIGN_GAP_REVIEWED' "$P7_FILE" 2>/dev/null || echo 0)
      DESIGN_GAP_COUNT=$(echo "$DESIGN_GAP_COUNT" | tail -1)
      DESIGN_GAP_REVIEWED=$(echo "$DESIGN_GAP_REVIEWED" | tail -1)
      UNREVIEWED=$((DESIGN_GAP_COUNT - DESIGN_GAP_REVIEWED))
      if [ "$UNREVIEWED" -gt 0 ]; then
          echo "GATE P7: 有 ${UNREVIEWED} 条 [DESIGN_GAP] 未配对 [DESIGN_GAP_REVIEWED]——主 Agent 需审查 implementer 的自主决策" >&2
          exit 1
      fi
      # R2.3 修复：P4/P7 DESIGN_GAP 数量交叉核对
      # architect 忘记把 P4 的 DESIGN_GAP 转抄到 P7 → 之前静默放过
      P4_DESIGN_GAP_COUNT=$(grep -rh '\[DESIGN_GAP:' "$TASK_DIR"/P4-implementation.md "$TASK_DIR"/P4-implementation/ 2>/dev/null | grep -cE '^\s*-?\s*\[DESIGN_GAP:' 2>/dev/null || true)
      P4_DESIGN_GAP_COUNT=$(echo "$P4_DESIGN_GAP_COUNT" | tail -1)
      [ -z "$P4_DESIGN_GAP_COUNT" ] && P4_DESIGN_GAP_COUNT=0
      if [ "$P4_DESIGN_GAP_COUNT" -gt "$DESIGN_GAP_COUNT" ]; then
          echo "GATE P7: P4 声明了 ${P4_DESIGN_GAP_COUNT} 条 [DESIGN_GAP]，P7 只转抄了 ${DESIGN_GAP_COUNT} 条——architect 遗漏转抄" >&2
          exit 1
      fi
      # N3: review 实质锚点 WARNING——P7 有 DESIGN_GAP_REVIEWED 但缺跨文件引用
      if [ "$DESIGN_GAP_REVIEWED" -gt 0 ]; then
          if ! grep -qE 'P1.*BDD|P2.*packages|P4.*implementation' "$P7_FILE" 2>/dev/null; then
              echo "WARNING P7: P7-consistency.md 有 DESIGN_GAP_REVIEWED 但缺跨文件引用关键词（P1 BDD / P2 packages / P4 implementation）——review 可能未做实质性交叉检查" >&2
          fi
      fi
      exit 0 ;;
  P8)
      # P8 部分检查可脚本化，其余需主 Agent 自判
      # 注意：version 文件路径和 CHANGELOG 文件名因项目而异，
      # 主 Agent 应从 P2-design.md packages 字段读取具体路径。
      # 以下检查使用通用模式，可能需要主 Agent 补充验证。
      # 用 git diff --cached（暂存区），不用 HEAD~1——pre-commit 时本次变更还没进 HEAD
      # 与 P4/P7 同款修复（v0.6 hardening R4 chicken-and-egg 教训）
       # 检查 bump_type 字段
       if ! grep -q 'bump_type:' "$TASK_DIR/P8-release.md" 2>/dev/null; then
           echo "GATE P8: P8-release.md 缺 bump_type 字段" >&2
           exit 1
       fi
       # 检查 version 文件变更（路径 A: 暂存区 + 路径 B: 最近 commit）
       VERSION_PATTERN="${AGATE_VERSION_FILES:-version|__version__|package.json|Cargo.toml|pyproject.toml|go.mod|pom.xml|gemspec|csproj}"
       CACHED_VERSION=no
       if git diff --cached --stat 2>/dev/null | grep -qiE "$VERSION_PATTERN"; then
           CACHED_VERSION=yes
       fi
       RECENT_VERSION=no
       if [ "$CACHED_VERSION" = "no" ]; then
           LOOKBACK="${AGATE_P8_LOOKBACK:-5}"
           if git rev-parse "HEAD~${LOOKBACK}" >/dev/null 2>&1; then
               if git diff "HEAD~${LOOKBACK}..HEAD" --stat 2>/dev/null | grep -qiE "$VERSION_PATTERN"; then
                   RECENT_VERSION=yes
               fi
           fi
       fi
       if [ "$CACHED_VERSION" = "no" ] && [ "$RECENT_VERSION" = "no" ]; then
           echo "GATE P8 WARNING: 暂存区和最近 ${LOOKBACK} 个 commit 均无 version 文件变更" >&2
       fi
       # 检查 CHANGELOG 变更（双路径，降级为 WARNING）
       CHANGELOG_FILE="${CHANGELOG_FILE:-CHANGELOG.md}"
       CACHED_CHANGELOG=no
       if git diff --cached -- "$CHANGELOG_FILE" 2>/dev/null | grep -q .; then
           CACHED_CHANGELOG=yes
       fi
       RECENT_CHANGELOG=no
       if [ "$CACHED_CHANGELOG" = "no" ]; then
           LOOKBACK="${AGATE_P8_LOOKBACK:-5}"
           if git rev-parse "HEAD~${LOOKBACK}" >/dev/null 2>&1; then
               if git diff "HEAD~${LOOKBACK}..HEAD" -- "$CHANGELOG_FILE" 2>/dev/null | grep -q .; then
                   RECENT_CHANGELOG=yes
               fi
           fi
       fi
       if [ "$CACHED_CHANGELOG" = "no" ] && [ "$RECENT_CHANGELOG" = "no" ]; then
           echo "GATE P8 WARNING: 暂存区和最近 ${LOOKBACK} 个 commit 均无 ${CHANGELOG_FILE} 变更" >&2
       fi
      # 检查 tag 存在性（WARNING，不阻断——tag 通常在 gate 通过后才打）
      VERSION_TAG_PREFIX="${VERSION_TAG_PREFIX:-v}"
      CHANGELOG_DIFF=$(git diff --cached -- "$CHANGELOG_FILE" 2>/dev/null || true)
      TAG_VERSION=$(echo "$CHANGELOG_DIFF" | grep -oE '\[[0-9]+\.[0-9]+\.[0-9]+[a-zA-Z0-9.-]*\]' | head -1 | tr -d '[]' || true)
      if [ -n "$TAG_VERSION" ]; then
          if ! git tag -l "${VERSION_TAG_PREFIX}${TAG_VERSION}" 2>/dev/null | grep -q .; then
              echo "GATE P8 WARNING: tag ${VERSION_TAG_PREFIX}${TAG_VERSION} 不存在。打 tag 后再推进到 READY。若 tag 前缀非 v，设置 VERSION_TAG_PREFIX 环境变量。" >&2
          fi
      fi
      echo "GATE P8: 脚本化检查通过。仍需主 Agent：① 从 P2 gate_commands 逐包读取发布检查命令 ② 重跑 P5 gate ③ 用 git log 对照 CHANGELOG 无遗漏 ④ 从 P2 packages 验证 version 文件路径" >&2
      exit 2 ;;
  *)
      echo "未知阶段: $PHASE" >&2
      exit 2 ;;
esac
