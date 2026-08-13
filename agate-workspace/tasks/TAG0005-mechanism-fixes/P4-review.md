---
phase: P4
task_id: TAG0005-mechanism-fixes
type: review
parent: P4-implementation.md
trace_id: TAG0005-mechanism-fixes-P4-20260813
status: approved
created: 2026-08-13
agent: review
---

# P4 实现评审 — agate 机制修复批（TAG0005）

**结论：approved**（无 CRITICAL/BLOCKER；2 处 INFORMATIONAL 见文末，均不阻塞推进）。

评审方式：逐项对照 dispatch-context 评审重点（6 组）+ 实测脚本行为 + 全量回归（726 bats 全绿、consistency 0 ERROR --strict、shellcheck 0 error、count-tests.sh 720）。

## Pass 1/2 核验结果

### 1. count.py 双值输出 vs check-gate.sh 消费（RM-AG0011）— 一致

- `agate/scripts/agate-gate-p5-count.py:22-23`：`main = len(re.findall(r"^  P5:", block, re.MULTILINE))` 精确匹配 `P5:`（不匹配 `P5_*` 键）；`aux = [k for k in re.findall(r"^  (P5_\w+):", block, ...) if not k.endswith("_formatter")]`。输出单行双值 `"%s %s"`（L24），无块时 `0 0`（L18-19）。与 P2-design §2.2 方案 A 逐字吻合。
- `agate/scripts/check-gate.sh:253-260`：`P5_CMD_DATA=$(... || echo "0 0")`（count.py 失败兜底）→ `tail -1`（L254）→ `awk '{print $1}' | tail -1` 拆主（L255）、`awk '{print $2}' | tail -1` 拆辅（L256）→ `P5_TOTAL=$((P5_MAIN + P5_AUX))`（L257）→ `> 1` 才输出 WARNING（L258-259）。与双值格式、`tail -1` 约定、`awk` 拆字段完全一致。
- **aux 排除 `_formatter` 正确**：与 `agate/scripts/agate-read-p5-commands.py:29-30`（`if key.endswith("_formatter"): continue`）执行枚举语义对齐，实测 `P5+P5_formatter` → `1 0`（GPC.3 绿）。
- 实测：对 TAG0005 自身 P2-design.md（P5/P5_consistency/P5_shellcheck）输出 `1 2`（1 主 2 辅），in-situ 验证 P2-design §3 的样例声明成立。
- 脚本断言 GPC.1/2/3、G5_CMD.1/2/3/4/5 全绿（check-gate.bats 124 用例全过）。

### 2. render 条件注入（RM-AG0012①）— 按 ROLE_DIR 分叉正确

- `agate/assets/templates/dispatch-prompt.md:83-92`：主代码块（L6-81）已移除「Review 角色特别指令」；在 `## 阶段特定提示` 下新增 `### Review 角色特别指令` 子节（L85-92），含完整 status draft→approved/rejected/needs-revision 语义代码块。模板为唯一内容源。
- `agate/scripts/agate-render-dispatch-prompt.sh:80-83`：`ROLE_DIR=review-roles` 时以 `sed -n '/^### Review 角色特别指令$/,/^### /p' | sed '/^### /d' | extract_first_code_block` 提取 review_appendix；execution 角色 review_appendix 为空（L80 初始化 + L81 条件）。
- **组装顺序**（L108-114）：main_block → review_appendix → phase appendix。实测 design-review 渲染结果中「Review 角色特别指令」位于「P2 最小验证」（阶段追加）之前；architect（execution）渲染不含该节。既有 P2/P3/P4/P5/P6/P8 追加未被破坏（RP.13 无残留占位符、RP.16 P3 追加、RP.18/19 全绿）。
- **BDD-9 守卫**：测试以 `--include='*.md'` 限定文档文件（check-gate.bats:1358-1363），实测全仓 `Review 角色特别指令` 仅命中 `assets/templates/dispatch-prompt.md` 单文件。render 脚本 L82 的 sed 模式字面量在 .sh 文件，不计入；`agate/dispatch-protocol.md:438` 内联模板备注用「评审角色专用节的 status 字段语义说明」措辞避开字面量，语义一致不分叉（I7 满足）。

### 3. check-debt.sh 依赖加载失败 exit 0→2（BDD-15/16）— 无调用方受影响

- `agate/scripts/check-debt.sh:26-31`：source 失败 → stderr + exit 2（L27-28）；文件缺失 → stderr「缺少 agate-workspace-resolve.sh，无法解析工作区，回退覆盖比对无法执行」+ exit 2（L30-31）。删去「跳过回退覆盖比对」措辞（避免 BDD-15 扫描误判为有意跳过）。
- 头注释 L5/L8/L14 同步为「覆盖模式：依赖加载失败 exit 2（需主 Agent 自判），无 retreat 提交等有意跳过分支仍 exit 0」。
- 「有意跳过」分支（无 retreat 提交 → exit 0）L37-39 保留，test_bdd_13/14/15 全绿。
- **调用方 grep 核验**：全仓 `check-debt.sh` 无脚本/hook 调用（仅 `agate/scripts/agate-retreat-to.sh:72` 注释 + README/UPGRADING/state-transitions 文档引用）；`pre-commit-gate.sh`/`pre-push-gate.sh`/`check-gate.sh`/`ci-gate-backstop.py` 均未调用 → exit 0→2 无 hook 波及面（与 P2-design §2.6 背景声明一致）。
- BDD-15 实测：`rg -n '>&2;\s*exit 0' agate/scripts/*.sh` 仅剩 agate-capture-env-baseline.sh 三处显式「跳过」语义行。BDD-16 用例（依赖缺失 → exit 2 + stderr）绿。
- `agate/scripts/README.md:23` 描述同步正确。

### 4. 三处 C8 表同步（RM-AG0010）— 一致自洽

- `agate/role-system.md:56`：`| backend | 任意 | plan-eng-review（P2 方案评审）+ review（P4 后）|`；L63 去重说明。
- `agate/rules/review-mapping.md:17-18`：backend 拆两行（plan-eng-review | P2 / review | P4 后）；L26 去重说明。
- `agate/phase-cards/P2-design.md:95`：`| backend | 任意 | plan-eng-review（P2 方案评审） |`；L100 去重说明。
- 三处 backend P2 触发（plan-eng-review）一致，去重说明措辞一致（backend+high 均命中 plan-eng-review → 只派 1 个）；与 `agate/role-system.md:150-153`「角色选择决策」节（涉及架构/技术方案 → plan-eng-review）自洽。
- BDD-1 测试（check-gate.bats:1347-1351）绿；BDD-2（check-gate.sh P2 分支无条件要求 P2-review.md 保留）绿。P4 卡片 C8 表（phase-cards/P4-implementation.md:71 backend→review）保持 P4 后 review，两阶段职责清晰不冲突。

### 5. dispatch-protocol.md 自动重试（RM-AG0003）— 不改变 retry/PAUSED 语义

- `agate/dispatch-protocol.md:111-127`：第 1 次空返回改写为 a-e 步骤（a 自动重试一次不占槽位 + <1min 告警；b 计入 retries[Pn]；c-e 分析/调整/记录）；「禁止」段 L127 补豁免说明（仅限首次、单次、原样重发）。
- MAX_RETRY / PAUSED 段（L121-123）未改；「自动重试仍空返回 → 进入步骤 b」使 retries[Pn] 计数时机后移一拍但上限判定点不变（与 P2-design §2.5 方案 A 逐字吻合，BDD-14 最强满足）。
- BDD-12/13/14 测试（check-gate.bats:1366-1378）绿（「自动重试一次」「会话时长异常短」「<1min」「MAX_RETRY」「PAUSED 报告人工」均命中）。

### 6. 脚本健壮性（set -euo pipefail）— 异常输入安全

- `agate/scripts/check-gate.sh:253`：`python3 ... 2>/dev/null || echo "0 0"` 兜底 count.py 失败；L254 `tail -1` 保证取最后一行；L255-256 awk 拆字段。count.py 失败/无块 → `0 0` → TOTAL=0 → 无 WARNING 无崩溃（G5_CMD.2/3 绿）。
- `agate/scripts/check-debt.sh:27,31`：exit 2 路径均在 `set -euo pipefail` 下显式退出，不触发未捕获错误；`git log ... || true`（L36）、`python3 ... || true`（L42）兜底只读工具失败。

## 回归证据

- 全量 `bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/` → **726 全绿**（与 P4-implementation.md 自查一致）。
- `python3 agate/scripts/check-protocol-consistency.py --strict` → 0 ERROR（CHECK 1/2/3/4/6/7/8/9 全过）。
- `shellcheck -S warning agate/scripts/check-gate.sh agate/scripts/check-debt.sh agate/scripts/agate-render-dispatch-prompt.sh` → 0 error。
- `bash agate/tests/scripts/count-tests.sh` → 720（不含 sanity 6，与 tests/README.md 口径一致）。
- tests/README.md 计数表：check-gate 100→124、render 16→20、p5-count 2→3，与 count-tests.sh 实际数（124/20/3）一致。

## 范围与格式

- 改动清单 11 文件全部落在 dispatch-context 评审对象内；无 [SCOPE+]/[DESIGN_GAP] 声明；测试断言由 P3 固化为本阶段实测通过。
- 本文件无行首 `- PASS`/`- FAIL` 格式。

## INFORMATIONAL（不阻塞推进，建议顺手修正）

1. `agate/tests/unit/agate-debt-check.bats:6` 头注释仍写「check-debt.sh --retreat-coverage = 回退覆盖比对（只读 WARNING，恒 exit 0）」——与新的 exit 2 语义不符。测试行为断言（test_bdd_16 断言 exit 2）正确，仅注释陈旧，不影响行为；建议后续同步为「依赖加载失败 exit 2」。
2. `agate-workspace/tasks/TAG0005-mechanism-fixes/P4-implementation.md:86` 备注称 check-gate.bats / agate-gate-p5-count.bats 两行计数「按『最小实现』原则未动」，但实际 diff 显示这两行已同步（100→124、2→3）。实际改动正确且必要（与 P3-test-cases.md 计数变更表一致），仅实现说明备注表述失真，建议修正避免 P6/P7 混淆。

## 环境隔离

`[PROD_NOT_TOUCHED]`——评审全程仅在 worktree 内读取/运行本地 bats/shellcheck/consistency，未接触生产环境。
