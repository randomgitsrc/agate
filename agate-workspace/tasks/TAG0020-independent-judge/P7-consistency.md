---
phase: P7
task_id: TAG0020-independent-judge
type: consistency
parent: P2-design.md
trace_id: TAG0020-P7-20260822
status: draft
created: 2026-08-22
agent: consistency-reviewer
# ── v2.0 机器计数 ──
blocker_count: 0
deviation_count: 0
deviation_critical_count: 0
design_gap_count: 0
design_gap_reviewed_count: 0
code_map_new_files_count: 0
code_map_reviewed_count: 0
---

# P7 一致性检查 — 独立 Judge 机制（RM-AG0032）：P6.5 挂载与三层防造假

[PROD_NOT_TOUCHED]

> 检查对象 = P1-P6 全部产出 + worktree 实现（13 个协议/脚本文件改动 + 2 个补丁 + 3 个新增文件）。
> 检查方式：逐条读出源文件并交叉比对，所有结论附具体文件+节名锚点（非裸"一致"）。
> 前置事实：P1/P2/P3/P4/P5/P6 commit 全部存在（git log：0e6bd04/c5ac1f8/606afcb/ae8fe17/741727d/f4cd6b9）；.state.yaml phase=P7。

## 0. 结论摘要（gate 契约）

- **BLOCKER=0** / **DEVIATION-CRITICAL=0** / **deviation_count=0**
- **DESIGN_GAP=0**（P4 无声明，无配对需求；design_gap_count=0 / design_gap_reviewed_count=0）
- **SCOPE+ 闭环（空集）**：P1/P2/P4 均无 [SCOPE+] 增补；[SCOPE_GAP]（ci-gate-backstop）已闭环
- **跨文件一致性全部通过**（锚点见 §3）；**1 项 WARNING 级发现**：CODE-MAP.md 未同步（见 §5，[CODE_MAP_DRIFT:] 不阻断）

---

## 1. DESIGN_GAP 配对

**P4 声明侧**：`P4-implementation.md` 全文**无行首 `[DESIGN_GAP:`**（grep 实测，P4-implementation.md 全部 86 行）；`P4-progress.md` 同样无（其「[SCOPE_GAP]」节 L92-94 为范围缺口声明，非设计偏差）。P4 唯一的实现偏差声明为：

- `[SCOPE_GAP: P2-design §1.1/§4 声明 ci-gate-backstop.py judge/events 兜底，scripts 批 prompt 未列 → docs 批主 Agent 确认后补齐]`（P4-implementation.md §SCOPE_GAP 记录 L78，标注**已闭环**；实现见 P4-implementation.md §实现摘要②「ci-gate-backstop.py（修改，SCOPE_GAP 补齐）」）— 程序性闭环成立。

**评审 INFORMATIONAL R-1/2/3 核查**（dispatch-context 强制项"核查是否需登记 DEVIATION 而非 DESIGN_GAP"）：结论为**无需登记 DEVIATION**，逐条锚点：

- **R-1**（内容寻址去重轮次语义细化）：check-judge-verdict step 9 记 `verdict_hash`（check-judge-verdict.py L419-433）+ check-events 按 hash 去重计轮（check-events.py L104-112）。这是 P4-review CRITICAL-1 评审批准的修复，P4-review.md「CRITICAL-1 复审」表锚定"≤2 语义保持（真实复核才 +1）"——对 P2-design §3.4 step 7 字面"事件计数"的实现细化，方向 = 修复 P2 设计缺陷（正常 gate 流程不再自锁），已复审 approved；非实现偏离。
- **R-2**（黑名单扩展名锁定子串的变形引用绕过）：P2-design §3.3 step 7 原文即扩展名串扫描（"两节黑名单串扫描"），实现忠实于设计（check-judge-verdict.py L143 `_check_blacklist`）；绕过面由全文行首 `- PASS|FAIL` 预判（L188）+ 主 Agent 派发约定兜底，P4-review「PASS 2」明示"风险低"。属 BDD-4 文本层残留，非实现偏差。
- **R-3**（无扩展名证据引用 fail-closed）：I-2 修复方向，judge.md「产出格式」要求证据路径带扩展名；方向安全。非实现偏差。

**P7 gate 交叉核对**：`check-gate.py gate_p7`（L986-994）对 P4-implementation.md 行首 `[DESIGN_GAP:` 计数 = 0 → 与 P7 `design_gap_count=0` 配对无缺失。
**gate 提示（非阻断）**：gate_p7 L966-972 的 T090 WARNING 会触发——P4-implementation.md 含 `[SCOPE_GAP:`（"GAP:" 命中 `gap:` 不敏感正则）且 DESIGN_GAP 计数为 0。属预期 WARNING（源自 SCOPE_GAP 标记文本），不改变 exit code。

---

## 2. SCOPE+ 闭环

- `P1-requirements.md`：`[NO_NEED_CONFIRM]`（L19/L211）；全文**无行首 `[SCOPE+]`**（grep 实测）；2 条 `[SUGGEST:]`（§3 维度表）由 P2-design §7「标注」节逐条采纳（"[SUGGEST: 采纳]"）——SUGGEST 非 SCOPE+，不影响基线。
- `P2-design.md` L358：「无新隐含需求需 `[SCOPE+]`」。
- `P4-implementation.md` L79：「实现中未发现新的 P2 未预见必须项（无新增 SCOPE+）」。
- `P4-progress.md`：唯一范围追加 = `[SCOPE_GAP]`（ci-gate-backstop 兜底），docs 批已补齐实现（P4-progress「docs 批」节条目 2），闭环。
- 机械印证：`check-scope-resolved.py` L82-84 `scope_found=0 → exit 0`（产出无 [SCOPE+] 扫描命中）。

**结论**：SCOPE+ 闭环 = **空集闭合格**（P1 基线无增补项需回写 `[SCOPE_RESOLVED]`；check-scope-resolved 通过；闭合格引锚 P1§3 / P2§7 / P4§SCOPE_GAP 记录）。

---

## 3. 跨文件一致性

**3.1 P2 packages vs P4 实现路径**：P2-design frontmatter `packages: [agate]`（L11）+ P1 L12 同值；P4-implementation `implementation_dir: agate/scripts` + 协议文档改动全部落在 `agate/*.md`（state-machine/WORKFLOW/dispatch-protocol/P6 卡/LIMITATIONS/AGENTS）+ `agate/assets/`（judge.md / dispatch-prompt.md）→ 单包 agate 内，**吻合**（P1§packages ↔ P4§impl-path）。

**3.2 P1 BDD 数 vs P6 验收数**：P1-requirements §5 `#### BDD-1`~`#### BDD-10`（grep 实测 10 行，L135-186）；P6-acceptance frontmatter `pass: 10 / fail: 0` + Summary「10/10 PASS, 0 FAIL」；P6 验收口径声明确认 grep 计数 = 10（P6-acceptance L24）→ **匹配**（P1§BDD-01 ↔ P6§Summary）。

**3.3 P4 实现 vs P2 方案**（judge 机制 17 文件 = 5 scripts + 10 docs + 2 补丁 vs P2 serial 三批）：
- P2 §3.3 九步校验链 → check-judge-verdict.py（①verdict ②dispatch-context ③Header ④BDD 对照 ⑤三数全等+partial ⑥证据交叉 ⑦白名单 ⑧预算交叉 ⑨append judge_verdict，L310-435）逐项对应；
- P2 §3.4 审计链 → check-events.py（缺失/空合法 / JSON 解析 / GENESIS 首行 / 链断裂 / ts 单调 / judge 轮次 ≤2 / 未知类型不拦截，L50-120）逐项对应；
- P2 §3.5 gate_p65 → check-gate.py L881-905（judge 未启用早退 0 → 缺 verdict exit 1 → 双脚本任一 exit 1 → exit 1）+ handlers `"P6.5": gate_p65`（L1155）；gate_p6 未动（L791-840 区间保留，BDD-10）；
- P2 §4 serial（scripts→docs→测试）→ P4-implementation 三批（①scripts 5 ②docs+backstop 10 ③补丁 2）——测试层按 TDD 在 P3 先行落地（P3 commit 606afcb 含测试代码 5 文件），顺序意图一致、无跨批依赖违约。
- **吻合**（P2§3.5 gate_p65 ↔ P4§impl-path check-gate.py）。

**3.4 P2 dispatch_plan serial vs P4 实际分批**：P2 §4 `mode: serial, parallel_limit: 1`；P4-implementation「实现摘要（三批）」= scripts 批(5) → docs 批(10) → 补丁(2)，串行推进、单 subagent 单批 → **一致**（P2§4 dispatch_plan ↔ P4§实现摘要）。

**3.5 P2 gate_commands vs P5 实际执行**：P2 §5 `P5`（全量 pytest）、`P5_consistency`（`--strict-errors-only`）、`P5_count_tests`（count-tests.sh）共 3 条；P5-progress S1/S2/S3 + P5-test-results/unit.md「命令逐条结果」表（3 行，命令文本逐字一致；r1 与 r2 两轮全执行）→ **一致**（P2§5 gate_commands ↔ P5§unit.md 命令表）。

**3.6 judge 机制与既有 gate 一致性**（dispatch-context 强制核查项）：
- **三处 P6.5 注入条件一致**：① check-gate gate_p65（L891-895，`_load_state_yaml → judge.enabled`）② pre-commit-gate 2i.1（L392 `_judge_enabled(task_dir)` && verdict 存在 L393）③ ci-gate-backstop（L268-269 `_judge_enabled` && `Path(...).exists()`）——三处判定同一「judge.enabled && verdict 存在 → 跑同一双脚本集 check-judge-verdict + check-events」；check-gate 对启用任务缺 verdict 显式 exit 1（L897-899）。语义等价，**一致**。
- **append_event 唯一写路径**：grep 全 `agate/scripts`，`gate-events.jsonl` 写入仅经 `agate_common.append_event`（L309）；调用方 = pre-commit-gate（gate_run L359 / state_transition L373）+ check-judge-verdict step 9（L434）；无第二处直接写文件 → **单点收敛**（P2 §3a）。
- **gate-events.jsonl 与 check-p6-provenance 审计共存**：审计 2 glob `P6-dispatch-context-*.md`（check-p6-provenance.py L323）前缀 `P6-` 不匹配 `P6.5-*` → judge dispatch-context 由 check-judge-verdict 白名单扫描承担（不扩展 2p glob，P2 R5）；审计 5 只消费 `P6-evidence/*.log` 的 EXIT_CODE 尾行（L471-488），账本为任务根 `.jsonl` → 无交集；审计 3 协作规范 glob `P[0-8]-*.md`（L504）不匹配 `P6.5-judge-verdict.md`；pre-commit `_NON_MD_YAML_RE` 增 `gate-events\.jsonl$`（L80，retreat 回归修复）→ **共存成立**。

**3.7 新脚本注册完整性（5 处）**：
| 注册点 | 位置 | 状态 |
|---|---|---|
| CHECK 9 锚点（SCRIPT_ALIGNMENT_ANCHORS）| check-protocol-consistency.py L691-692（check-judge-verdict）/ L697-698（check-events）| ✅ 关键词 criteria_total/judge/prev_hash/GENESIS 与脚本命中（P4-progress「CHECK 9」节实证）|
| _DRIFT_SCRIPTS | agate-summary.py L48-49 | ✅ |
| AGENTS.md 角色清单 | AGENTS.md L76 judge.md | ✅ |
| role-system.md 名册 + 三值映射 + 不进 C8 | role-system.md L51 / L119 | ✅ |
| dispatch-prompt.md Judge 追加节 | dispatch-prompt.md L202-217 | ✅ |
→ 全部同步（P4§实现摘要③ + 各文件锚点）。

---

## 4. 未决项清零

- P1-requirements.md：`[NO_NEED_CONFIRM]`（L19/L211），无行首 `[NEED_CONFIRM]`（grep 实测，dispatch-context 所称"分析时无 SUGGEST——P1 [NO_NEED_CONFIRM]"核实属实——实际为 2 条 SUGGEST 倾向项 + [NO_NEED_CONFIRM]，均不阻塞）。
- P1-P6 产出**无行首 `[BLOCKER]` / `[DEVIATION-CRITICAL]`**（P4-review / P1-review 正文"无 BLOCKER/无 CRITICAL"为散文陈述，非行首标记）。
- `known-failures.md`：2 条目（bdd_7 git 仓库内 basetemp 非 git 上下文前提失效 / bdd_25 .pytest-tmp 一致性扫描面误收）经 P5 r2 复现 + P6 BDD-10 复用通过证据，判定**与本任务无关**成立；P5 本次引入真失败（bdd_5 编码）已由 P4 修复轮闭环（P4-progress「P5 回修记录」）。
- **清零**（P1§8 / P6§说明与边界 / known-failures.md 全文）。

---

## 5. CODE-MAP 核对

**发现**：`{AGATE_WORKSPACE}/agents/CODE-MAP.md` **存在**（81 行，TAG0007 落盘的 agate 自身 dogfood 架构维护物，其正文 L3-7 明示契约："后续任务新增/挪动协议文件时，P4 implementer 应更新本文件；P7 consistency-reviewer 核对本文件记录与实际新增文件是否同步（[CODE_MAP_SYNC:]）或偏离（[CODE_MAP_DRIFT:]）"）。
P4-implementation.md「新增文件核对表」声明 `[CODE_MAP_EXEMPT: 无 CODE-MAP 机制]`（L26-28）及其说明"无 CODE-MAP（无 `{AGATE_WORKSPACE}/agents/CODE-MAP.md`）"（L22）经实测**与事实不符**（文件存在）——记入核对结论。

**逐条核对**（3 个新增协议文件 vs CODE-MAP.md）：
- `[CODE_MAP_DRIFT: CODE-MAP.md §模块 review-roles（L19-21）仍列"10 个评审角色（review / plan-ceo-review / ... / requirements-review）"，未登记本次新增 judge.md（现 11 个；AGENTS.md L76 与 role-system.md L51 均已登记）]`
- `[CODE_MAP_DRIFT: CODE-MAP.md §模块 scripts（L22-29）gate/一致性/状态三族描述未提及本次新增 check-judge-verdict.py 与 check-events.py（CHECK 9 锚点与 _DRIFT_SCRIPTS 已登记，见 §3.7）]`

**判定**：`[CODE_MAP_DRIFT:]` 属 **WARNING 级、不阻断**（P7 卡明示）；无依赖方向性偏离（新脚本仍属 scripts 工具层、新角色仍属 review-roles 层，依赖方向合规，CODE-MAP.md §依赖方向 L50-63 未被违反）。frontmatter `code_map_new_files_count: 0` 与 P4 `[CODE_MAP_EXEMPT]` 声明核对（per-task 骨架/CODE-MAP 机制未采用——P2-design 无 code_map 机制字段），P7 gate 转抄核对（P4 行首 `[CODE_MAP_UPDATED]/[CODE_MAP_EXEMPT]` 计数 = 0，表格内标记非行首）通过。
**建议（供主 Agent/P8 决策）**：发布前更新 CODE-MAP.md（review-roles 11 个 + scripts 两新脚本）或登记为技术债；gate_p4 因 CODE-MAP.md 存在会检查「## 新增文件核对表」标题（check-gate.py L749-754）——P4 已含该表，无额外拦截。

---

## 6. 实质锚点汇总（N3）

| 结论 | 锚点 |
|---|---|
| BLOCKER=0 | DESIGN_GAP=0（P4 无声明，§1）；无 [BLOCKER] 标记（§4）|
| CRITICAL=0 | 跨文件检查逐条锚点（§3）：P2§3.5 gate_p65 ↔ check-gate.py L881-905；P1§BDD-01 ↔ P6§Summary；P2§packages ↔ P4§impl-path；P2§5 gate_commands ↔ P5§unit.md；P2§4 dispatch_plan ↔ P4§实现摘要 |
| SCOPE+ 闭环 | P1§3（[SUGGEST] 非 SCOPE+）+ P2§7（无新隐含需求）+ P4§SCOPE_GAP 记录（已闭环）+ check-scope-resolved exit 0 |
| CODE-MAP | 3 个新文件逐条核对 → 2 组 [CODE_MAP_DRIFT:]（WARNING，§5）；与 P4 [CODE_MAP_EXEMPT] 声明核对 frontmatter=0 |

## 7. 结论

- 本任务 P1-P6 产出与 worktree 实现（judge.md + check-judge-verdict/check-events + agate_common 事件账本 + check-gate gate_p65 + pre-commit 2i.1 + ci-gate-backstop 兜底 + 文档 8 处 + CHECK 9/_DRIFT_SCRIPTS 注册）**跨文件一致**，哲学红线（BDD-9 exit code 才是门槛）、历史兼容（BDD-2 三守卫）、信息隔离（BDD-4 白名单）、事件账本（BDD-7 append-only 单点写路径）均锚点核实。
- 无 [BLOCKER] / [DEVIATION-CRITICAL]；DESIGN_GAP 0 条无需配对；SCOPE+ 空集闭环；未决项清零。
- 唯一发现：[CODE_MAP_DRIFT:]（WARNING 级，CODE-MAP.md 未登记 3 个新文件 + P4「无 CODE-MAP.md」事实性误述）——不阻断，供主 Agent 在 P8 发布前处置。
- [PROD_NOT_TOUCHED]：全程只读检查，未改任何协议/脚本/代码。

> gate 预判：`check-gate.py P7 $TASK_DIR` → exit 0（预期输出含 1 条非阻断 WARNING：T090「P4 检测到设计偏差相关关键词（SCOPE_GAP 文本内 "GAP:"）但 DESIGN_GAP 计数为 0」；以及可能 1 条 T090-adjacent 提示）。判定权归主 Agent。