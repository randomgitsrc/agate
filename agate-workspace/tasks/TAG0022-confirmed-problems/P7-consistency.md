---
phase: P7
task_id: TAG0022-confirmed-problems
type: consistency
parent: P2-design.md
trace_id: TAG0022-P7-20260822
status: draft
created: 2026-08-22
agent: consistency-reviewer
# ── v2.0 机器计数 ──
blocker_count: 0
deviation_count: 0
deviation_critical_count: 0
design_gap_count: 2
design_gap_reviewed_count: 2
code_map_new_files_count: 1
code_map_reviewed_count: 1
---

# P7 一致性审查 — TAG0022 三连任务确认问题修复批（RM-AG0037~RM-AG0041）

> 状态标记：[PROD_NOT_TOUCHED]（只读消费 P1-P6 产出、worktree 协议/脚本与稳定版 `~/.agate`；写操作仅落 P7-consistency.md 与 P7-progress.md）
> 审查对象：P1-requirements / P2-design / P3-test-cases / P4-implementation / P5-test-results / P6-acceptance / P6.5-judge-verdict / CODE-MAP / gate-events.jsonl / .state.yaml
> 方法：逐条交叉核对，每条结论引用源文件节名锚点（非裸「一致」）；DESIGN_GAP 逐条转抄 + REVIEWED。

## 1. DESIGN_GAP 配对（硬门槛）

P4-implementation.md 声明 2 条 [DESIGN_GAP]（L289 / L291），P7 逐条转抄原始标记行 + REVIEWED 标记行如下。判定依据（全部成立）：主 Agent 采纳（P4-review approved，L23「2 条 DESIGN_GAP 已由主 Agent 采纳」）+ protocol-alignment-review 独立核实（docs/reviews/agate-alignment-review-2026-08-23-TAG0022.md，L99/L101 `[KNOWN_DEVIATION: ... 主 Agent 采纳，理由核实成立]`）+ P3 用例全绿（S-3a/S-3b 漂移用例 + 静态扫描用例）+ P6 BDD-3/5 PASS（P6-acceptance L28-29，test_md_parse_scan 命中=0 / S-3 13 passed）。

### 1.1 DESIGN_GAP #1（P4§implementation-L289，batch C 节「自主决策声明」）

[DESIGN_GAP: P2 §4.2.2 例「P5→gate_commands.P5」在真实树上不可达——P5 卡 `## gate 规则` 节无 gate_commands.P5 token，而 S-3a 要求 YAML 命令串须在卡节出现；R4 的"补卡片"路径因 phase-cards/ 不在 C 批文件集（禁越界）不可执行。实现取 S-3a/S-3b 双侧一致约束为硬锚：P5 gates 散文改「P2 声明的验证命令全部 exit 0 AND failed==0」（去 token）+ 增补 check-gate.py P5 $TASK_DIR，与卡片对齐后真实树 S-3 exit 0。]

[DESIGN_GAP_REVIEWED: 已确认] —— 判定依据：① 主 Agent 采纳（P4-review approved，L23）；② protocol-alignment-review 独立核实成立（A1-5 + L101 `[KNOWN_DEVIATION: 来源 TAG0022 P4-implementation.md DESIGN_GAP 1，主 Agent 采纳，理由核实成立]`——P5 gates 散文去 token 保语义，`gate_commands.P5` 实际命令仍在 P2-design.md §6 gate_commands 块，check-gate gate_p5 照常消费，语义无降级，真实树 S-3 exit 0）；③ P3 用例全绿（test_check_structure_consistency.py S-3a/S-3b 漂移用例 + 双侧一致用例，P3-test-cases §3 BDD-5 三用例）；④ P6 BDD-5 PASS（test_check_structure_consistency.py 13 passed，P6-acceptance L29）。

### 1.2 DESIGN_GAP #2（P4§implementation-L291，batch C 节「自主决策声明」）

[DESIGN_GAP: P2 §4.2.2 未指定 S-3a/S-3b 的匹配粒度。实现定案：机器可判定命令按 **token 提取**（`check-gate.py P{n}` / `gate_commands.P{n}` / `check-*.py`）做子串包含判定（非整串/整行比对）；S-3a 扫描卡片 gate 规则节（缺节回退推进条件），S-3b 仅扫描 gate 规则节（推进条件不纳入）。P3 三用例（s3a/s3b/双侧一致）对该口径全绿，真实树 10 阶段 0 ERROR。]

[DESIGN_GAP_REVIEWED: 已确认] —— 判定依据：① 主 Agent 采纳（P4-review approved，L23）；② protocol-alignment-review 独立核实成立（A1-5 + L99 `[KNOWN_DEVIATION: 来源 TAG0022 P4-implementation.md DESIGN_GAP 2，主 Agent 采纳，理由核实成立]`——token 提取三模式与 P2 §4.2.2 一致，子串包含判定不弱于整串比对，P3 三用例 + 真实树 10 阶段 0 ERROR 验证，语义按原则 6 不计入需修复项）；③ P3 用例全绿（BDD-5 三用例 + BDD-3 静态扫描用例）；④ P6 BDD-3/BDD-5 PASS（P6-acceptance L27/L29）。

**配对结论**：design_gap_count=2（P4 实际行首 [DESIGN_GAP:] 计数，grep 核对 L289/L291 恰 2 条），design_gap_reviewed_count=2，全部 REVIEWED 配对。

## 2. SCOPE+ 闭环

- SCOPE+ 条目：P2§design-1.4 [SCOPE+] —— check-protocol-consistency.py `iter_md_files`（L119-138）新增 opt-in 排除钩子 env `AGATE_CONSISTENCY_SKIP_DIRS`（默认关闭、行为不变），M15 进入改动面；理由 = BDD-9「任意 basetemp 位置全量 0 失败」的必要使能（仓库内 basetemp 坏引用 fixture 污染根因，TAG0020 known-failures 条目 2 实证）。
- 闭环标记：P1§requirements-7 [SCOPE_RESOLVED]（P1-requirements.md L163，主 Agent 采纳 + 归属 BDD-9 验收口径内、不新增 BDD）。
- 实现落地：P4§implementation-batchD（check-protocol-consistency.py `_env_skip_dir_prefixes()` + 排除链追加，分量级前缀匹配、默认逐字节不变）；P6§BDD-9 PASS（仓库内 `agate/.bt-p6-verify` 与仓库外 ptmp 两位置均 1213 passed / 2 skipped / 0 failed，P6-acceptance L33）。
- **SCOPE+ 闭环成立**：条目 → SCOPE_RESOLVED → 实现 → 验收，全链一致。

## 3. 跨文件一致性

### 3.1 packages 单版本单元（P1§packages ↔ P2§packages ↔ P8 bump 范围）

- P1§packages=[agate]（P1-requirements.md L14：agate 协议本体为单一版本单元）；P2§packages=[agate]（P2-design.md L12）。两处一致。
- P8 bump 范围：P8-release.md 尚未产出（当前 phase=P7），无法与 P8 对照；按 P1/P2 一致声明 + P1 §5 范围表（五子项全部落在 `agate/` 单一版本单元 + .github/workflows）推断 P8 bump 为单版本单元，一致前提成立，留 P8 阶段以 `packages: [agate]` 为 bump 范围核对。

### 3.2 BDD 数量匹配（P1§BDD ↔ P6§pass/fail）

- P1§BDD=10（P1-requirements.md §6，BDD-1..BDD-10 编号连续）；P6§pass/fail=10/0（P6-acceptance.md frontmatter pass: 10 / fail: 0）。
- 编号集合一致：P6 正文逐条 PASS BDD-1（L25）→ BDD-10（L34），与 P1 §6.1-6.5 五组十项一一对应（0037→BDD-1/2；0038→BDD-3/4/5；0039→BDD-6/7；0040→BDD-8；0041→BDD-9/10），无错映射（对照 P7 卡「常见错误 2」逐条核对内容而非仅数量）。
- P6.5 judge 复核 criteria_total=10 / criteria_passed=10（P6.5-judge-verdict.md L10-11），与 P6 数量一致。

### 3.3 P4 四批实现 ↔ P2 方案设计（P4§impl ↔ P2§design）

| P4§impl 批次 | P2§design 方案节 | 吻合核对 |
|---|---|---|
| batch A-ruff（workflow ruff job 锁版本 + UPGRADING + AGENTS.md） | P2§4.1 RM-AG0037 + P2§5 批表 A-ruff（文件集 3 文件） | 吻合：job name 固化 + `ruff==0.16.4` + required check 配置步骤文档（D1 边界），UPGRADING 占位小节策略（P4 batch A L41-46）与 P2 §5 批表不含 UPGRADING 的批分工一致 |
| batch C-migration（A/B/C/D 组迁移 + S-3 收紧 + test_md_parse_scan） | P2§4.2 逐点映射清单（§4.2.1）+ S-1~S-6 收紧（§4.2.2）+ P2§5 批表 C-migration（6 文件） | 吻合：A 组 9 处调用迁 `_md_field_get` + 新 op 注册（含 created）；B/C/D 组共享读取器落 agate_common；S-3a/S-3b 叠加实现（NB-1/NB-2）；2 条 DESIGN_GAP 属 §1 已配对 |
| batch B-judge（gate_p1 judge 块 + dispatch.yaml + state-machine + P1 卡） | P2§4.3（N1 fail-closed exit 1 + 判别机制 + 文档面）+ P2§5 批表 B-judge（依赖 C，C 后串行） | 吻合：judge 块叠加于 C 批重构后基础（created op + read_rules_yaml 路径），批界声明 L284-285「gate_p65 逐字节未动」与 P2 §1.2 N1 一致 |
| batch D-env-tests（test_bdd_7 GIT_CEILING_DIRECTORIES + test_bdd_25/M15 排除钩子） | P2§4.5.1/4.5.2 子决策定案 + P2§5 批表 D-env-tests（含 M15 [SCOPE+]） | 吻合：GIT_CEILING_DIRECTORIES 定案（§4.5.1）；opt-in 排除钩子定案（§4.5.2）；M15 归属 BDD-9（§1.4 [SCOPE+] 已闭环） |
| RM-AG0040（无代码批，实证计划落 P2） | P2§4.4 实证执行计划（M3 四要素 + 触发条件 + 已知边界） | 吻合：P4 四批均无 RM-AG0040 代码改动，计划交付于 P2§4.4.1；P6§BDD-8 PASS 核对四要素 + 触发条件齐全（P6-acceptance L32） |

批序验证：P4 batch B 声明「时序：叠加于 C-migration 批之后」（L300），与 P2 §5 Wave1={A,C,D} → Wave2={B} 编排一致；C 批先行使 agate-md-field-get.py 单批独占（D3 错开），P2 §5 L243 声明吻合。

### 3.4 ceremony（P1§ceremony ↔ P2）

- P1§ceremony=standard（P1-requirements.md L12：缺省档位 fail-closed，本任务非 thin 候选）；P2 未声明 ceremony 字段（P2 frontmatter 无 ceremony），P2§4.4 RM-AG0040 实证计划明示「ceremony: thin 从未实战」且本 task 不改 thin 机制、仅产出实证计划 + 触发条件（P2§4.4.1 四要素 ⑤ 触发条件 = 下一个 low 风险任务 / 用户指定薄任务真跑 thin）。
- 核对结论：本任务 ceremony=standard（非 thin）与 P1 一致；RM-AG0040 实证计划位于 P2§4.4，P6§BDD-8 PASS（P6-acceptance L32 引用 P2-design.md §4.4.1 L203-211）。

### 3.5 judge 机制链（.state.yaml ↔ P6.5 verdict ↔ 账本事件）

- `.state.yaml`§judge：`enabled: true` / `rounds: 1` / `last_verdict: passed` / `partial: false`（L5-9）。
- P6.5-judge-verdict.md§frontmatter：`criteria_total: 10` / `criteria_passed: 10` / `verdict_evidence` 12 个证据文件 / `status: passed`（L7-12）。
- gate-events.jsonl L17：`{"event":"judge_verdict","verdict":"passed","criteria_passed":10,"criteria_total":10,"partial":false,"phase":"P6.5"}`。
- 三处一致：judge.enabled=true ↔ P6.5 verdict passed 10/10 ↔ 账本 judge_verdict 事件（verdict=passed / partial=false），judge 机制链完整闭环（RM-AG0039 验收锚 BDD-6/7 依赖的 P1 机械校验已在 P4 batch B 落地，P6 BDD-6/7 PASS）。

### 3.6 观察项（非阻断，不构成 DEVIATION）

- P2-design.md frontmatter L16 派发编排字段注释「RM-AG0040 为文档交付，计划落于本文件 §5.4」——正文实际节号为 §4.4（P2§4.4 RM-AG0040）。注释引用节号过期（§5.4 应为早期草稿节号）；实质内容无漂移（P6§BDD-8 PASS 引用 §4.4.1 正确，P4 四批均按「无 RM-AG0040 代码批」执行）。记录供 P2 文档维护参考，不影响本任务一致性结论与任何 BDD 判定。

## 4. 未决项清零

- P1-requirements.md 全文 grep 行首 `[NEED_CONFIRM]` / `[BLOCKER]` / `[DEVIATION-CRITICAL]` → **0 命中**。
- P1§requirements-7 声明 `[NO_NEED_CONFIRM]`（L231：无待确认项，方向性选择以 [SUGGEST] 留痕）与 §7 尾注（L239：无未决 NEED_CONFIRM 项）一致。
- P1-review 非阻塞观察闭环：N1（judge 校验强度）→ P2§4.3.1 fail-closed exit 1 定案（P2-review 锁定决策 2）；N2（basetemp 写可性）→ P2§0/§8 ptmp 实证可写冻结；N3（count-tests 基线）→ P2§0 冻结 1202（P6 实测 1215 只增不减）。
- P4-review 2 条 INFORMATIONAL：I1（批界文档不一致）→ 由 P4-implementation.md batch B 节 [批界偏差] 标注闭环（见 §6）；I2（agate_common import 降级 stub 观察）→ 非阻断，记录在案。

## 5. CODE-MAP 核对

- P4「新增文件核对表」实际新增文件：四批合计仅 **1 个新增文件** `agate/tests/unit/test_md_parse_scan.py`（P3 批新增落盘，C 批仅校准一行平台卫生注释，P4-implementation.md L206 声明；A/B/D 批均无新增代码文件，L31/L103/L316 CODE_MAP_EXEMPT）。
- CODE-MAP.md（agate-workspace/agents/CODE-MAP.md）为**模块级架构图**（五大模块 phase-cards / execution-roles / review-roles / scripts / templates / rules + 层 + 依赖方向），无逐文件登记机制；测试文件（agate/tests/unit/）非协议本体文件，CODE-MAP 顶部声明「后续任务新增/挪动**协议文件**时 P4 implementer 应更新本文件」——test_md_parse_scan.py 新增不触发登记义务。
- 依赖方向核对：新增测试文件不改变 CODE-MAP §依赖方向 声明的单向依赖（phase-cards → roles → templates；rules → scripts 消费），无反向依赖引入。
- **[CODE_MAP_SYNC: test_md_parse_scan.py 新增与 CODE-MAP 记录同步——CODE-MAP 为模块级架构图无逐文件登记要求，新增文件落于既有 agate/tests/unit/ 结构（AGENTS.md 仓库结构声明范围），P4 各批新增文件核对表与 CODE-MAP 无依赖方向偏离]**。
- 机器计数：code_map_new_files_count=1（唯一新增文件），code_map_reviewed_count=1（已核对同步）。

## 6. 批界偏差标注核对（P4-review INFORMATIONAL #1 闭环）

- 标注存在：P4-implementation.md batch B 节末尾「批界偏差标注」（L374-376）`[批界偏差：test_env_adapt_docs.py:172 注释（R4 平台假设扫描自伤修复「无 /tmp 字面」→「无临时目录字面量」）经收尾 implementer 修改，属跨批必要修复（D 批文件集）；根因 = 平台假设扫描器对注释文本中的 `/tmp` 字面量误报，修复不改变测试语义。P7 一致性核对时按此标注处理]`。
- 可追溯链：P4-review.md INFORMATIONAL #1（I1，L87-91：批界文档不一致 + Fix 建议）→ P4-implementation.md batch B 节 [批界偏差] 标注（收尾 implementer 补声明）→ P6 BDD-10 PASS（平台无关回归拦截，check-platform-assumptions.py 0 命中 + 修改点 diff 无单平台假设，P6-acceptance L34）。
- 影响评估：修复为单行注释措辞（消除 `/tmp` 字面量对 R4 扫描器的自伤），不改变测试语义；D 批复核结论（test_env_adapt_docs.py 零改动）为批内复核口径，不涵盖 B 批跨批单行修复——该偏差已被显式标注，**标注存在且可追溯，闭环成立**。

## 7. 结论

- **BLOCKER=0**：无阻断项；**DEVIATION-CRITICAL=0**、deviation_count=0（§3.6 观察项为非阻断文档注释级，不构成 DEVIATION）。
- **DESIGN_GAP 全配对**：design_gap_count=2 / design_gap_reviewed_count=2，P4 2 条 [DESIGN_GAP] 全部转抄 + REVIEWED（判定依据 = 主 Agent 采纳 + protocol-alignment-review 独立核实 + P3 用例全绿 + P6 BDD-3/5 PASS）。
- **SCOPE+ 闭环**：P1§[SCOPE_RESOLVED] ↔ P2§1.4 [SCOPE+] M15 ↔ P4 D 批实现 ↔ P6 BDD-9 PASS。
- **CODE-MAP SYNC**：code_map_new_files_count=1 / code_map_reviewed_count=1，新增文件核对通过。
- **跨文件一致性通过**：packages 单版本单元 / BDD 10 vs 10/0 / 四批实现 ↔ P2 设计逐条吻合 / ceremony standard / judge 机制链三处一致（详见 §3）。
- **未决项清零**：P1 无残留行首 [NEED_CONFIRM]/[BLOCKER]/[DEVIATION-CRITICAL]，[NO_NEED_CONFIRM] 声明在案。
- **批界偏差标注**：存在且可追溯（P4-review I1 → P4-implementation batch B [批界偏差] → P6 BDD-10 PASS）。

**审查结论：P7 一致性检查通过（BLOCKER=0 / CRITICAL=0 / DESIGN_GAP 2/2 配对 / SCOPE+ 闭环 / CODE-MAP SYNC），可提交主 Agent 推进 P8。**
