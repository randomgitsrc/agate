#!/usr/bin/env bash
# check-gate.sh PHASE TASK_DIR [OLD_PHASE]
# exit 0 = gate 通过; exit 1 = gate 未通过; exit 2 = 需主 Agent 自判（含动态 gate_commands 或语义判断）
#
# OLD_PHASE（可选第 3 参数）：上一个 phase。省略时行为与之前完全一致（无回退检测）。
# 提供且数字上大于 PHASE 时，判定为"回退抵达"，跳过该阶段的完成度校验直接 exit 2
# （回退抵达 ≠ 阶段已完成，不该被当"未完成"硬拦截；也不应假装"已通过"）。
#
# 可脚本化的 gate（exit 0/1）：P4 / P7
# 需主 Agent 自判的 gate（exit 2）：P0 / P1 / P2 / P3 / P5 / P6 / P8
# P3 红灯（check-tdd-red.sh）由主 Agent 手动确认 + CI backstop P3 兜底，不在此脚本内执行
#
# 本脚本的判定逻辑与 state-machine.md 步骤 5 保持同步。
# 步骤 5 变更时必须同步更新本脚本。一致性检查脚本覆盖本文件。

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PHASE="${1:?用法: check-gate.sh PHASE TASK_DIR}"
TASK_DIR="${2:?用法: check-gate.sh PHASE TASK_DIR}"
OLD_PHASE="${3:-}"

# 回退到达检测（可选第 3 参数，向后兼容：不传 = 行为与之前完全一致）。
# 背景：本脚本每个阶段分支检查的是"这个阶段的完成度"（文件存在/approved/FAIL=0 等），
# 这个假设只对"正常推进抵达"成立——对"回退抵达"（如 P6→P4 归档后刚落地 P4）不成立，
# 因为退回来的那一刻工作本来就还没重做，不该被当成"没完成"而硬拦截。
# 用 OLD_PHASE 与 PHASE 的数字大小关系判断方向：OLD_PHASE 数字更大 = 回退。
if [ -n "$OLD_PHASE" ]; then
    OLD_NUM=$(echo "$OLD_PHASE" | grep -oE '[0-9]+' || echo "")
    NEW_NUM=$(echo "$PHASE" | grep -oE '[0-9]+' || echo "")
    if [ -n "$OLD_NUM" ] && [ -n "$NEW_NUM" ] && [ "$OLD_NUM" -gt "$NEW_NUM" ]; then
        echo "GATE $PHASE: 检测到回退抵达（上一阶段 $OLD_PHASE → $PHASE），本次 commit 视为回退声明，暂不做完成度校验" >&2
        echo "  该阶段的工作尚待重新进行；重新推进离开 $PHASE 时会再次正常校验" >&2
        exit 2
    fi
fi

case "$PHASE" in
  P0)
      echo "GATE P0: 立项阶段无需脚本 gate（仅 P0-brief.md）。主 Agent 确认 P0-brief 四字段齐全即可推进 P1。" >&2
      exit 2 ;;
  P1)
      P1_REVIEW="$TASK_DIR/P1-review.md"
      if [ ! -f "$P1_REVIEW" ]; then
          echo "GATE P1: P1-review.md 不存在——P1 评审不可裁，所有任务都需独立 requirements-review" >&2
          exit 1
      fi
      # M6（BDD-14）：frontmatter 提取 CRLF 容错——sed 首命令 s/\r$// 剥行尾 \r（CRLF md 的 ---\r 不匹配 /^---$/），
      # 后接原范围模式。LF 文件 s/\r$// 无匹配，行为不变（BDD-15 回归守卫）。本文件内 8 处 /^---$/ 提取统一此模式。
      P1_REVIEW_STATUS=$(sed -n 's/\r$//; /^---$/,/^---$/p' "$P1_REVIEW" | { grep '^status:' || true; } | sed 's/^status:\s*//' | head -1)
      if [ "$P1_REVIEW_STATUS" != "approved" ]; then
          echo "GATE P1: P1-review.md frontmatter status 非 approved（当前: ${P1_REVIEW_STATUS:-缺失}）" >&2
          exit 1
      fi
      P1_REVIEW_AGENT=$(sed -n 's/\r$//; /^---$/,/^---$/p' "$P1_REVIEW" | { grep '^agent:' || true; } | sed 's/^agent:\s*//' | head -1)
      if [ -z "$P1_REVIEW_AGENT" ]; then
          echo "GATE P1: P1-review.md status:approved 但缺 agent 字段" >&2
          exit 1
      fi
      if [ "$P1_REVIEW_AGENT" = "main" ]; then
          echo "GATE P1: P1-review.md status:approved 但 agent=main（主 Agent 不可自行批准评审）" >&2
          exit 1
      fi
      if ! grep -qE 'BDD-[0-9]' "$P1_REVIEW" 2>/dev/null; then
          echo "GATE P1: P1-review.md 不含 BDD 编号引用（裸 approved 极可能是假完成，review 结论须引用具体 BDD 编号）" >&2
          exit 1
      fi
      # P1 NEED_CONFIRM 检查（v0.30.2 三值分级：[NEED_CONFIRM] 阻塞 / [SUGGEST:] 不阻塞 / [NO_NEED_CONFIRM] 负向）
      # RM-AG0001：行首正则加可选反引号前缀（`[NEED_CONFIRM] 反引号包裹标记不再漏计；含 `- \`[..]` 反引号在 dash 之后的形态）
      P1_FILE="$TASK_DIR/P1-requirements.md"
      NC_BLOCKING=$(grep -cE '^\s*`*-?\s*`*\[NEED_CONFIRM\]' "$P1_FILE" 2>/dev/null || echo 0)
      NC_BLOCKING=$(echo "$NC_BLOCKING" | tail -1)
      NC_SUGGEST=$(grep -cE '^\s*`*-?\s*`*\[SUGGEST:' "$P1_FILE" 2>/dev/null || echo 0)
      NC_SUGGEST=$(echo "$NC_SUGGEST" | tail -1)
      # v2.0 T001 流 C（BDD-21）：NEED_CONFIRM "已解决/已确认"状态结构化——
      # frontmatter need_confirm_resolved 存在时，逐条匹配正文每条 NEED_CONFIRM 的
      # 描述是否已在该列表中找到对应项，未匹配才计入阻塞数（不是数量相减，避免
      # F14 教训的 0-vs-0 歧义）。frontmatter 无该字段（旧格式）→ 沿用整段计数阻塞。
      NC_UNRESOLVED="$NC_BLOCKING"
      if [ "$NC_BLOCKING" -gt 0 ]; then
          NC_RESOLVED_PRESENT=$(sed -n 's/\r$//; /^---$/,/^---$/p' "$P1_FILE" 2>/dev/null | grep -c '^need_confirm_resolved:' || true)
          NC_RESOLVED_PRESENT=$(echo "$NC_RESOLVED_PRESENT" | tail -1)
          if [ "$NC_RESOLVED_PRESENT" -gt 0 ]; then
              NC_RESOLVED_FM=$(FILE="$P1_FILE" python3 "$SCRIPT_DIR/agate-md-field-get.py" need_confirm_resolved 2>/dev/null || echo "")
              NC_UNRESOLVED=0
              while IFS= read -r nc_desc; do
                  [ -z "$nc_desc" ] && continue
                  if ! printf '%s\n' "$NC_RESOLVED_FM" | grep -qFx -- "$nc_desc"; then
                      NC_UNRESOLVED=$((NC_UNRESOLVED + 1))
                  fi
              done < <(grep -E '^\s*`*-?\s*`*\[NEED_CONFIRM\]' "$P1_FILE" | sed -E 's/^\s*`*-?\s*`*\[NEED_CONFIRM\][[:space:]]*//')
          fi
      fi
      if [ "$NC_UNRESOLVED" -gt 0 ]; then
          echo "GATE P1: $NC_UNRESOLVED 个未解决的 NEED_CONFIRM 项（阻塞）" >&2
          exit 1
      fi
      # v2.0 T001 流 C：SUGGEST WARNING 去重——suggest_resolved 已采纳项不重复 WARNING
      NC_SUGGEST_UNACKED="$NC_SUGGEST"
      if [ "$NC_SUGGEST" -gt 0 ]; then
          SG_RESOLVED_PRESENT=$(sed -n 's/\r$//; /^---$/,/^---$/p' "$P1_FILE" 2>/dev/null | grep -c '^suggest_resolved:' || true)
          SG_RESOLVED_PRESENT=$(echo "$SG_RESOLVED_PRESENT" | tail -1)
          if [ "$SG_RESOLVED_PRESENT" -gt 0 ]; then
              SG_RESOLVED_FM=$(FILE="$P1_FILE" python3 "$SCRIPT_DIR/agate-md-field-get.py" suggest_resolved 2>/dev/null || echo "")
              NC_SUGGEST_UNACKED=0
              while IFS= read -r sg_desc; do
                  [ -z "$sg_desc" ] && continue
                  if ! printf '%s\n' "$SG_RESOLVED_FM" | grep -qFx -- "$sg_desc"; then
                      NC_SUGGEST_UNACKED=$((NC_SUGGEST_UNACKED + 1))
                  fi
              done < <(grep -E '^\s*`*-?\s*`*\[SUGGEST:' "$P1_FILE" | sed -E 's/^\s*`*-?\s*`*\[SUGGEST:[[:space:]]*//; s/`[[:space:]]*$//; s/\]\s*$//')
          fi
      fi
      if [ "$NC_SUGGEST_UNACKED" -gt 0 ]; then
          echo "GATE P1 WARNING: $NC_SUGGEST_UNACKED 个 SUGGEST 项（主 Agent 可自行采纳，不阻塞）" >&2
      fi
      # typo 兜底 1：检测旧标记 [NEED_CONFIRM倾向:] 残留
      if grep -qE '\[NEED_CONFIRM倾向:' "$P1_FILE" 2>/dev/null; then
          echo "GATE P1: 检测到旧标记 [NEED_CONFIRM倾向:]。v0.30.2 起已重命名为 [SUGGEST: ...]" >&2
          exit 1
      fi
      # typo 兜底 2：[SUGGEST 开头但不是 [SUGGEST:
      if grep -q '\[SUGGEST' "$P1_FILE" 2>/dev/null && ! grep -q '\[SUGGEST:' "$P1_FILE" 2>/dev/null; then
          echo "GATE P1: SUGGEST 格式不符。合法格式：[SUGGEST: 推荐 X，理由 Y]" >&2
          exit 1
      fi
      if grep -qE '\[NEED_CONFIRM\]' "$P1_FILE" 2>/dev/null && [ "$NC_BLOCKING" -eq 0 ]; then
          echo "GATE P1: 不合规的 NEED_CONFIRM 标记格式（须用行首 [NEED_CONFIRM]、[SUGGEST: ...] 或 [NO_NEED_CONFIRM] 声明）" >&2
          exit 1
      fi
      if [ "$NC_BLOCKING" -eq 0 ] && [ "$NC_SUGGEST" -eq 0 ] && ! grep -qE '^\s*`*-?\s*`*\[NO_NEED_CONFIRM\]' "$P1_FILE" 2>/dev/null; then
          echo "GATE P1 WARNING: 未检测到 NEED_CONFIRM 声明（[NEED_CONFIRM] / [SUGGEST: ...] / [NO_NEED_CONFIRM]）" >&2
      fi
      echo "GATE P1: P1-review.md approved + agent≠main + 含 BDD 锚点。BDD 编号格式为 #### BDD-NN:" >&2
      exit 2 ;;
  P2)
      # v0.6：多方案探索检查（nudge 强度）
      # P2 不可裁剪，不存在 P2-design.md 时直接报错
      P2_FILE="$TASK_DIR/P2-design.md"
      if [ -f "$P2_FILE" ]; then
          # v0.31.0：候选方案数改为显式 candidate_count 字段（纯强制），不再用正则数标题
          # 消除脆弱标题匹配（如全角冒号 # 方案：），gate 只检查字段存在性（自声明 nudge）
          CANDIDATE_COUNT=$(grep -E '^candidate_count:' "$P2_FILE" 2>/dev/null | grep -oE '[0-9]+' | head -1 || true)
          CANDIDATE_COUNT=${CANDIDATE_COUNT:-0}
          P1_FILE="$TASK_DIR/P1-requirements.md"
          MIN_CANDIDATES=2
          if [ -f "$P1_FILE" ]; then
              if grep -qE '^(design_trivial|follows_existing_pattern):\s*\S' "$P1_FILE" 2>/dev/null; then
                  MIN_CANDIDATES=1
              fi
          fi
          if [ "$CANDIDATE_COUNT" -lt "$MIN_CANDIDATES" ]; then
              echo "GATE P2: P2-design.md candidate_count=${CANDIDATE_COUNT}，需至少 ${MIN_CANDIDATES} 个候选方案（design_trivial/follows_existing_pattern 时可只写 1）。请显式声明 candidate_count 字段" >&2
              exit 1
          fi
          P2_REVIEW="$TASK_DIR/P2-review.md"
          if [ ! -f "$P2_REVIEW" ]; then
              echo "GATE P2: P2-review.md 不存在（P2 评审不可裁剪，必须派发独立 subagent 产出）" >&2
              exit 1
          fi
          P2_REVIEW_STATUS=$(sed -n 's/\r$//; /^---$/,/^---$/p' "$P2_REVIEW" | { grep '^status:' || true; } | sed 's/^status:\s*//' | head -1)
          if [ "$P2_REVIEW_STATUS" != "approved" ]; then
              echo "GATE P2: P2-review.md frontmatter status 非 approved（当前: ${P2_REVIEW_STATUS:-缺失}）" >&2
              exit 1
          fi
          P2_REVIEW_AGENT=$(sed -n 's/\r$//; /^---$/,/^---$/p' "$P2_REVIEW" | { grep '^agent:' || true; } | sed 's/^agent:\s*//' | head -1)
          if [ -z "$P2_REVIEW_AGENT" ]; then
              echo "GATE P2: P2-review.md status:approved 但缺 agent 字段（向后兼容 WARNING）" >&2
              exit 2
          fi
          if [ "$P2_REVIEW_AGENT" = "main" ]; then
              echo "GATE P2: P2-review.md status:approved 但 agent=main（主 Agent 不可自行批准评审）" >&2
              exit 1
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
      # P2.61: gate_commands 命令可执行性检查（WARNING 不阻断）
      # T075 教训：architect 写 `python -m pytest` 但系统无 python 命令，P3 gate exit 127
      # 解析 gate_commands 每个命令的第一个 token，验证存在性
      # 第一个 token 含 / → 跳过（相对/绝对路径如 .venv/bin/python，P2 阶段 venv 可能未建，不误报）
      # 否则 → command -v 验证
      MISSING_CMDS=$(GATE_FILE="$P2_FILE" python3 "$SCRIPT_DIR/agate-gate-missing-cmds.py" 2>/dev/null || echo "")
      if [ -n "$MISSING_CMDS" ]; then
          while IFS= read -r entry; do
              [ -z "$entry" ] && continue
              key=$(echo "$entry" | cut -d: -f1)
              token=$(echo "$entry" | cut -d: -f2-)
              if ! command -v "$token" &>/dev/null; then
                  echo "GATE P2 WARNING: gate_commands.$key 命令 '$token' 不存在于当前环境——请确认使用完整路径（如 .venv/bin/pytest）或安装依赖。T075 教训：python 不存在导致 P3 gate exit 127" >&2
              fi
          done <<< "$MISSING_CMDS"
      fi
      echo "GATE P2: 需从 P2-design.md gate_commands 动态读取，主 Agent 自行判定" >&2
      exit 2 ;;
  P3)
      # P3 gate：文件存在性检查（秒级）
      # T085 教训：exec check-tdd-red.sh 会真实跑测试命令 → hook 超时 → --no-verify 绕过全部检查
      # check-tdd-red.sh 独立运行：主 Agent 手动确认红灯 + CI backstop P3 时额外跑兜底
      P3_CASES="$TASK_DIR/P3-test-cases.md"
      if [ ! -f "$P3_CASES" ]; then
          echo "GATE P3: P3-test-cases.md 不存在——P3 产出文件缺失" >&2
          exit 1
      fi
      echo "GATE P3: P3-test-cases.md 存在。TDD 红灯由主 Agent 手动跑 check-tdd-red.sh 确认 + CI backstop P3 兜底。" >&2
      exit 2 ;;
  P4)
      # P4 review 门禁（与 P2 对称，roadmap 补 gap）
      # P4-implementation.md 要求 agent≠main（与 P2 同规则），此前 gate 未强制
      P4_REVIEW="$TASK_DIR/P4-review.md"
      if [ ! -f "$P4_REVIEW" ]; then
          echo "GATE P4: P4-review.md 不存在（P4 评审不可裁剪，必须派发独立 subagent 产出，见 phase-cards/P4-implementation.md C8 机械映射）" >&2
          exit 1
      fi
      P4_REVIEW_STATUS=$(sed -n 's/\r$//; /^---$/,/^---$/p' "$P4_REVIEW" | { grep '^status:' || true; } | sed 's/^status:\s*//' | head -1)
      if [ "$P4_REVIEW_STATUS" != "approved" ]; then
          echo "GATE P4: P4-review.md frontmatter status 非 approved（当前: ${P4_REVIEW_STATUS:-缺失}）" >&2
          exit 1
      fi
      P4_REVIEW_AGENT=$(sed -n 's/\r$//; /^---$/,/^---$/p' "$P4_REVIEW" | { grep '^agent:' || true; } | sed 's/^agent:\s*//' | head -1)
      if [ -z "$P4_REVIEW_AGENT" ]; then
          echo "GATE P4: P4-review.md status:approved 但缺 agent 字段（向后兼容 WARNING）" >&2
          exit 2
      fi
      if [ "$P4_REVIEW_AGENT" = "main" ]; then
          echo "GATE P4: P4-review.md status:approved 但 agent=main（主 Agent 不可自行批准评审）" >&2
          exit 1
      fi
      # pre-commit 阶段：检查暂存区有代码文件（非纯文档/状态文件）
      # N1 修复：原来查 git log，但 pre-commit 时 commit 还没创建，第一条 P4 commit 永远无法通过
      git diff --cached --name-only | grep -qvE '(^|/)P[0-8]-.*\.md$|(^|/)\.state\.yaml$' && exit 0 || exit 1 ;;
  P5)
      echo "GATE P5: 需从 P2-design.md gate_commands.P5 动态读取，主 Agent 自行判定" >&2
      # WARNING: 如果 P2 声明了多个 gate_commands.P5 命令（单元+集成+E2E），
      # 提醒主 Agent 确认是否全部执行（T060 教训：只跑子集可能掩盖预存失败）
      if [ -f "$TASK_DIR/P2-design.md" ]; then
          P5_CMD_COUNT=$(GATE_FILE="$TASK_DIR/P2-design.md" python3 "$SCRIPT_DIR/agate-gate-p5-count.py" 2>/dev/null || echo 0)
          P5_CMD_COUNT=$(echo "$P5_CMD_COUNT" | tail -1)
          if [ "$P5_CMD_COUNT" -gt 1 ]; then
              echo "GATE P5 WARNING: P2 声明了 ${P5_CMD_COUNT} 个 gate_commands.P5 命令，请确认已全部执行（非子集）。" >&2
              echo "  T060 教训：只跑子集可能掩盖预存失败（T056 venv 遗漏跨 4 个任务周期无人发现）。" >&2
          fi
      fi
      # 机械 diff：pre-task-baseline.md vs fail-list.txt
      BASELINE="$TASK_DIR/pre-task-baseline.md"
      POST_FAILS="$TASK_DIR/P5-test-results/fail-list.txt"
      if [ -f "$BASELINE" ] && [ -f "$POST_FAILS" ]; then
          if ! grep -q '^captured_at_commit:' "$BASELINE" 2>/dev/null; then
              echo "GATE P5: pre-task-baseline.md 存在但缺少 captured_at_commit: 标记，视为损坏，" >&2
              echo "  降级为 WARNING-only（exit 2），不做机械 diff——请检查基线文件完整性" >&2
              exit 2
          fi
          PRE_LIST=$(sed -n '/```fail-list/,/```/p' "$BASELINE" | sed '1d;$d' | grep -v '^$' || true)
          NEW_FAILS=$(comm -13 <(echo "$PRE_LIST" | sort -u) <(grep -v '^$' "$POST_FAILS" 2>/dev/null | sort -u || true))
          STILL_FAILING=$(comm -12 <(echo "$PRE_LIST" | sort -u) <(grep -v '^$' "$POST_FAILS" 2>/dev/null | sort -u || true))

          if [ -n "$NEW_FAILS" ]; then
              echo "GATE P5: 检测到基线快照中不存在的新增失败，视为本任务引入的回归，拦截：" >&2
              echo "$NEW_FAILS" | sed 's/^/  - /' >&2
              exit 1
          fi
          if [ -n "$STILL_FAILING" ]; then
              if [ ! -f "$TASK_DIR/known-failures.md" ]; then
                  echo "GATE P5: 检测到 $(echo "$STILL_FAILING" | grep -c . | tail -1) 个预存失败仍未修复，" >&2
                  echo "  基线快照证实这些失败早于本任务存在，但 known-failures.md 不存在——按协议必须登记" >&2
                  exit 1
              fi
              STILL_COUNT=$(echo "$STILL_FAILING" | grep -c . | tail -1)
              KNOWN_ENTRIES=$(grep -cE '^\|\s*[0-9]+\s*\|' "$TASK_DIR/known-failures.md" 2>/dev/null || echo 0)
              KNOWN_ENTRIES=$(echo "$KNOWN_ENTRIES" | tail -1)
              if [ "$KNOWN_ENTRIES" -lt "$STILL_COUNT" ]; then
                  echo "GATE P5: known-failures.md 登记条目数($KNOWN_ENTRIES) < 预存失败数($STILL_COUNT)，" >&2
                  echo "  登记不完整——每个预存失败都应有对应登记行" >&2
                  exit 1
              fi
          fi
      fi
      exit 2 ;;
  P6)
      # T001 v2.0 流 B（BDD-16/18，P2-design.md §3.2.1）：
      # frontmatter 声明 pass/fail 汇总（新格式）→ 门禁基于该汇总判定，不再 grep 正文计数；
      # frontmatter 无该汇总（旧格式）→ 回退正文 grep 计数，但计数口径改严格——只认行首
      # `- PASS|FAIL ... BDD-N` 带 BDD 编号的行，消除总结行（如 `- PASS: 16`）误判（F11）。
      P6_FILE="$TASK_DIR/P6-acceptance.md"
      # ── v2.0 refactor 口径分流（TAG0002 Phase A，P2-design.md §3.3）──
      # 缺省（未声明 change_type）→ 走既有功能口径，行为与改造前一致（BDD-2）
      CHANGE_TYPE=""
      if [ -f "$TASK_DIR/P1-requirements.md" ]; then
          CHANGE_TYPE=$(FILE="$TASK_DIR/P1-requirements.md" python3 "$SCRIPT_DIR/agate-md-field-get.py" change_type 2>/dev/null || echo "")
      fi
      if [ "$CHANGE_TYPE" = "refactor" ]; then
          REGRESSION_PASS=$(FILE="$P6_FILE" python3 "$SCRIPT_DIR/agate-md-field-get.py" regression_pass 2>/dev/null || echo "")
          if [ "$REGRESSION_PASS" != "true" ] || [ ! -f "$TASK_DIR/P6-evidence/regression.log" ]; then
              echo "GATE P6: change_type=refactor 但缺全量回归证据（须 P6-acceptance.md frontmatter regression_pass: true 且 P6-evidence/regression.log 存在）" >&2
              exit 1
          fi
      fi
      # ↓↓ 既有判定（pass/fail 汇总 / 证据目录非空）原样保留，不随 change_type 变化 ↓↓
      PASS_FM=$(FILE="$P6_FILE" python3 "$SCRIPT_DIR/agate-md-field-get.py" pass 2>/dev/null || echo "")
      FAIL_FM=$(FILE="$P6_FILE" python3 "$SCRIPT_DIR/agate-md-field-get.py" fail 2>/dev/null || echo "")
      if [ -n "$PASS_FM" ] && [ -n "$FAIL_FM" ]; then
          # 新格式：frontmatter 汇总判定（BDD-16）
          TOTAL=$((PASS_FM + FAIL_FM))
          FAIL=$FAIL_FM
      else
          # 旧格式回退：正文 grep 计数（BDD-18，行首须含 BDD 编号才计入，大小写不敏感）
          TOTAL=$(grep -ciE '^\s*- (PASS|FAIL)\b.*BDD-[0-9]' "$P6_FILE" 2>/dev/null || echo 0)
          TOTAL=$(echo "$TOTAL" | tail -1)
          FAIL=$(grep -ciE '^\s*- FAIL\b.*BDD-[0-9]' "$P6_FILE" 2>/dev/null || echo 0)
          FAIL=$(echo "$FAIL" | tail -1)
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
      echo "GATE P6: 证据目录非空，FAIL=0，NC=0，P6_TOTAL=$TOTAL。BDD 总数对照由 check-p6-provenance.sh 审计 3 自动执行。" >&2
      exit 2 ;;
  P7)
      # v0.6：用显式 if/elif/else 替代链式写法——每加一个检查都要在链路里加新项，if 更易读易扩展
      # grep -c 无匹配时返回 exit 1，|| echo 0 处理此情况
      #
      # T001 v2.0 流 B（BDD-19/20，P2-design.md §3.2.2）：
      # frontmatter 声明 blocker_count/deviation_critical_count（新格式）→ 门禁基于该结构化
      # 计数判定，不再用 grep 排除"非计数声明行"的正则；design_gap_count/
      # design_gap_reviewed_count 同理改读 frontmatter，不再用数量相减的 0-vs-0 歧义判定（F14）。
      # frontmatter 无这些字段（旧格式）→ 回退现有正文 grep 逻辑。
      P7_FILE="$TASK_DIR/P7-consistency.md"

      BLOCKER_FM=$(FILE="$P7_FILE" python3 "$SCRIPT_DIR/agate-md-field-get.py" blocker_count 2>/dev/null || echo "")
      DEVCRIT_FM=$(FILE="$P7_FILE" python3 "$SCRIPT_DIR/agate-md-field-get.py" deviation_critical_count 2>/dev/null || echo "")
      if [ -n "$BLOCKER_FM" ] && [ -n "$DEVCRIT_FM" ]; then
          # 新格式：frontmatter 结构化计数判定（BDD-19）
          BLOCKERS=$BLOCKER_FM
          DEVCRIT=$DEVCRIT_FM
      else
          # 旧格式回退：正文 grep + 非计数行排除正则（既有逻辑）
          # M4：[:：] bracket 在 POSIX locale 不匹配全角冒号 → 改 alternation (:|：)
          BLOCKERS=$(grep -E '^\s*-?\s*\[BLOCKER\]' "$P7_FILE" 2>/dev/null | grep -cvE '\[BLOCKER\](:|：)?[[:space:]]*[0-9]+[[:space:]]*条?[[:space:]]*$' || echo 0)
          DEVCRIT=$(grep -E '^\s*-?\s*\[DEVIATION-CRITICAL\]' "$P7_FILE" 2>/dev/null | grep -cvE '\[DEVIATION-CRITICAL\](:|：)?[[:space:]]*[0-9]+[[:space:]]*条?[[:space:]]*$' || echo 0)
          BLOCKERS=$(echo "$BLOCKERS" | tail -1)
          DEVCRIT=$(echo "$DEVCRIT" | tail -1)
      fi
      if [ "$BLOCKERS" -gt 0 ] || [ "$DEVCRIT" -gt 0 ]; then
          echo "GATE P7: BLOCKER=$BLOCKERS, DEVIATION-CRITICAL=$DEVCRIT" >&2
          exit 1
      fi

      # DESIGN_GAP 配对检查（v0.6：未配对 REVIEWED 标记的 DESIGN_GAP → 不通过）
      DESIGN_GAP_COUNT_FM=$(FILE="$P7_FILE" python3 "$SCRIPT_DIR/agate-md-field-get.py" design_gap_count 2>/dev/null || echo "")
      DESIGN_GAP_REVIEWED_FM=$(FILE="$P7_FILE" python3 "$SCRIPT_DIR/agate-md-field-get.py" design_gap_reviewed_count 2>/dev/null || echo "")
      if [ -n "$DESIGN_GAP_COUNT_FM" ] && [ -n "$DESIGN_GAP_REVIEWED_FM" ]; then
          # 新格式：reviewed_count >= count 通过，否则拦截（BDD-20，F14 消除数量相减歧义）
          DESIGN_GAP_COUNT=$DESIGN_GAP_COUNT_FM
          DESIGN_GAP_REVIEWED=$DESIGN_GAP_REVIEWED_FM
          if [ "$DESIGN_GAP_REVIEWED" -lt "$DESIGN_GAP_COUNT" ]; then
              echo "GATE P7: 有 $((DESIGN_GAP_COUNT - DESIGN_GAP_REVIEWED)) 条 [DESIGN_GAP] 未配对 [DESIGN_GAP_REVIEWED]（frontmatter: design_gap_count=${DESIGN_GAP_COUNT}, design_gap_reviewed_count=${DESIGN_GAP_REVIEWED}）——主 Agent 需审查 implementer 的自主决策" >&2
              exit 1
          fi
      else
          # 旧格式回退：正文 grep 数量相减判定（既有逻辑）
          DESIGN_GAP_COUNT=$(grep -cE '^\s*>?\s*-?\s*\[DESIGN_GAP:' "$P7_FILE" 2>/dev/null || echo 0)
          DESIGN_GAP_REVIEWED=$(grep -cE '^\s*>?\s*-?\s*\[DESIGN_GAP_REVIEWED' "$P7_FILE" 2>/dev/null || echo 0)
          DESIGN_GAP_COUNT=$(echo "$DESIGN_GAP_COUNT" | tail -1)
          DESIGN_GAP_REVIEWED=$(echo "$DESIGN_GAP_REVIEWED" | tail -1)
          UNREVIEWED=$((DESIGN_GAP_COUNT - DESIGN_GAP_REVIEWED))
          if [ "$UNREVIEWED" -gt 0 ]; then
              echo "GATE P7: 有 ${UNREVIEWED} 条 [DESIGN_GAP] 未配对 [DESIGN_GAP_REVIEWED]——主 Agent 需审查 implementer 的自主决策" >&2
              exit 1
          fi
      fi
      # 问题4 (T090)：P4 含"设计偏差/gap"关键词但 DESIGN_GAP 计数为 0 → WARNING 提醒人工确认
      if [ "$DESIGN_GAP_COUNT" -eq 0 ]; then
          if grep -qiE '设计偏差|design gap|未列入|gap:' "$TASK_DIR/P4-implementation.md" 2>/dev/null; then
              echo "GATE P7 WARNING: P4 检测到设计偏差相关关键词但 [DESIGN_GAP:] 计数为 0——请确认是否真的无偏差，或 P4 未按标准格式声明" >&2
          fi
      fi
      # R2.3 修复：P4/P7 DESIGN_GAP 数量交叉核对
      # P4 侧的 [DESIGN_GAP:] 转抄核对（R2.3 既有机制）不迁移——P4-implementation.md 的
      # [DESIGN_GAP:] 仍从正文 grep（发现性标记保持散文，流 C BDD-23 范畴）。
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
       # 债务清单确认留痕检查（TAG0001 Phase 3）：只查留痕存在，不查内容达标、不阻断发布
       # debt_check 缺失 → exit 1（4A 硬留痕）；字段存在（值任意，含 none / 未关闭债务）→ 放行
       if ! grep -q 'debt_check:' "$TASK_DIR/P8-release.md" 2>/dev/null; then
           echo "GATE P8: P8-release.md 缺 debt_check 字段（须确认债务清单并留痕，可为 none）" >&2
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
