---
review_date: 2026-08-15
reviewer: protocol-alignment-review
change_summary: WORKFLOW.md「适用边界」节新增「规划层与执行层的关系（roadmap / plan / task 如何挂接）」小节：roadmap=需求登记簿、plan=task 实施方案（非独立执行通道、有 plan ≠ 裁剪阶段）、三条执行路径。
files_changed: [agate/WORKFLOW.md]
---

# 协议-脚本对齐审查

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | ALIGNED（附 2 条建议传播项）|
| A4 | 测试覆盖 | ALIGNED |
| A5 | 下游影响 + 文档传播 | **MISALIGNED** |
| A6 | 锚点表覆盖 | ALIGNED |
| A7 | 设计原则一致性 | NEEDS_HUMAN_REVIEW |

## 逐项审查

### A1: 文档→脚本对齐

**文档声明**（WORKFLOW.md:188-208）：本次变更是纯文档性小节——roadmap/plan 两个概念均不引入新的机器字段、不引入新的 gate 脚本、不改变任何脚本的判定分支。

**脚本实现**：无对应脚本改动。核查 `agate/scripts/*.py` 无任何脚本读取「plan 是否存在」「roadmap 条目状态」作为 gate 判定输入；`check-gate.py` 各阶段 gate 不因 plan 存在与否改变（「有 plan ≠ 裁剪阶段」是编排层约定，不是脚本判定项——即使没有本节，既有 P1/P2 gate 依然强制 P1-requirements.md / P2-design.md 产出与 P2-review.md approved）。

**结论**：ALIGNED
**差异**：无。

### A2: 脚本→文档对齐

**脚本实现**：本次 diff 无任何脚本改动。
**文档声明**：无脚本逻辑需要反向同步到文档。

**结论**：ALIGNED
**差异**：无。

### A3: 一致性连锁 + 反向传播

**A3a 连锁**：本次变更不新增 frontmatter 字段、不改 gate 行为、不改状态机转移，无衍生脚本改动。

**A3b 反向传播**（列出「应被影响但未在 diff 中」的文件逐一核验）：

| 文件 | 是否存在影响 | 判断 |
|------|-------------|------|
| `agate/dispatch-protocol.md` | 无。全文件无「plan 作为执行通道」概念（仅 plan-* 评审角色引用，L1179）；派发流程不受 roadmap/plan 影响 | **无需改** |
| `agate/state-machine.md` | 无。`plans/` 仅出现在工作区 9 子目录清单（L40-41）；状态机转移不含 plan | **无需改** |
| `agate/orchestrator-template.md` / `agate/SETUP.md` | 无矛盾。两处仅列出 `plans/` 目录（orchestrator-template.md:22,102；SETUP.md:134），未定义其语义——本节首次规范化 plan 定位，属补充而非冲突 | **无需改**（可选：加一行「plans/ 为 task 参考输入」指针，非强制）|
| `agate/assets/templates/roadmap-template.md` | 弱影响。新规则「微任务/直接做可记录后直接改、不必拆完整 task」（WORKFLOW.md:194）在模板的循环规范（roadmap-template.md:29-33）中没有对应的状态迁移说明：直接做型条目从 backlog 直达 done、不经过 scheduled，模板只描述了「拆任务→scheduled」路径 | **建议补**（低优先级；模板已声明以 WORKFLOW.md 为权威，非矛盾）|
| `CHANGELOG.md` | 弱影响。本节把「所有改动都应留痕（RM 条目）」「plan 不是独立执行通道」升级为协议通用规则（此前仅存在于 RM-AG0016 条目详情与计划文件头部）| **建议补**（下个 release 记 Unreleased；当前无 [Unreleased] 节，非阻断）|

**结论**：ALIGNED（无必须修复的连锁缺失；2 条建议传播项为非阻断的文档补充）

### A4: 测试覆盖

**文档声明**：纯文档变更，无脚本/字段逻辑改动，不新增可测试行为。受影响面核查：`test_agate_debt_check.py:40-51` 读取 WORKFLOW.md 工作区 9 目录清单——`plans/` 未变，不受影响；`test_commit_msg_self_gate_integration.py:107` 仅以 WORKFLOW.md 作样例文件，不受影响。

**最近一次 pytest 全量实跑输出**：
```
749 passed, 2 skipped in 70.94s (0:01:10)
```
（`python3 -m pytest agate/tests/ -q`，749 passed / 2 skipped = 751 collected）

**一致性检查**：`python3 agate/scripts/check-protocol-consistency.py` → 0 ERROR（277 个 WARNING 均为叙事文件引用已归档 `archived/docs-2026-08/plans/agate-test-plan-2026-07-01.md` 的既有警告，与本次变更无关）。

**用例计数**：`bash agate/tests/scripts/count-tests.sh` → 751 个（≥749 基线），无漂移。

**结论**：ALIGNED

### A5: 下游影响 + 文档传播

**RM-AG0016 交互**（与既有 approved plan 使用方式核对）：一致。roadmap.md:247 与计划文件头部（`agate-workspace/plans/agate-dispatch-orchestration-20260815.md:5`）均已声明「有实施计划 ≠ 裁剪阶段 / 参考输入、不替代任务流程」——本节是把该条目的实例声明上升为协议通用规则，语义完全一致，不构成理解歧义。

**本节声明与 WORKFLOW.md 其他节的一致性**：

- 「机制级/跨模块 → 完整 P0-P8」与 L164（中任务跨模块→完整 P1-P8）、L177（机制交叉→必须走完整 agate）一致。
- 「声明性/缺陷修复 → 记录后直接改」与 L162（微任务声明性→直接做）、L173（声明性→可直接做）一致。
- 「有 plan ≠ 裁剪阶段」与「可裁剪的阶段」节（L210-227）无矛盾——现有规则中没有任何「存在 plan 即可裁剪阶段」的规定，本节是显式补强而非改动。

**⚠️ MISALIGNED（主问题）——WORKFLOW.md:203「或直接做」与既有规则矛盾**：

新增小节执行路径第 2 条（WORKFLOW.md:203）：
> 行为逻辑单点 → 拆 task（裁剪流程）**或直接做**

与以下既有规则直接冲突：
- WORKFLOW.md:176：「**行为逻辑改动**（条件分支、状态转换、数据处理）→ **至少走裁剪 agate**」
- WORKFLOW.md:163：小任务（行为逻辑改动，单点）→ 裁剪流程 P1+P2+P3+P4+P5+P6，跳过 P7
- WORKFLOW.md:257 风险矩阵：微改动低风险 → 直接做，但 L162 明确「微任务（**声明性**改动）→ 直接做」——直接做仅限声明性
- adr.md:142（ADR-005）：「行为逻辑改动（改变控制流）→ 至少走裁剪 agate」

**差异**：行为逻辑改动（含单点）在 ADR-005 与 WORKFLOW.md 现有规则中一律「至少走裁剪 agate」，不存在直接做通道。L203 的「或直接做」为行为逻辑改动打开了直通通道，语义从「至少裁剪 agate」放宽为「可直接做」，两处规则互相矛盾，subagent/主 Agent 读到时会无法判定哪个为准。

**建议**：删除 L203 的「或直接做」（行为逻辑单点一律走裁剪 agate）；若意图是对「极小行为逻辑改动」放行直接做，需在「可裁剪的阶段」节（L219 已有 ≤3 行 + 回归测试覆盖的 P3 跳过条件）显式定义该例外并给出判定条件，同时重新评估 ADR-005（见 A7）。

**⚠️ MISALIGNED（次问题）——WORKFLOW.md:204 hotfix 归类歧义**：

> 声明性/**缺陷修复（hotfix）**→ 记录后直接改 + PR 提交流程

缺陷修复通常属于行为逻辑改动（改变控制流），按 L176 应「至少走裁剪 agate」，不能直接改。把「缺陷修复」与「声明性」并列会让读到的 Agent 误以为所有 bug 修复都可以跳过 agate 直接改。

**建议**：改为「声明性改动 / 声明性缺陷修复（如 typo、配置值）→ 记录后直接改」；行为逻辑缺陷修复显式归入「行为逻辑单点 → 裁剪 agate」。

**CHANGELOG**：本节是协议规则补充（非破坏性变更），建议在下个 release 记入 CHANGELOG Unreleased；无需 UPGRADING.md 章节（无破坏性变更）。

**结论**：MISALIGNED（2 处，同一根因：三条执行路径图把「直接做」权限放宽到了 ADR-005 保留给声明性改动的范围之外）

### A6: 锚点表覆盖

**锚点核查**：CHECK 9 锚点表中 WORKFLOW.md 的锚点为「PAUSED 不是失败」/「正确路由」（check-protocol-consistency.py:614-617），本小节不触碰该关键词；roadmap/plan 概念无对应脚本契约，无需新增锚点。一致性检查实跑 0 ERROR 佐证。

**结论**：ALIGNED

### A7: 设计原则一致性

**符合面**：
- ADR-001（隔离性，主 Agent 只编排）：本节把 roadmap/plan 定位为「输入，不是独立执行通道」，与「主 Agent 只编排、不执行」一致——plan 是分析产物，不构成主 Agent 自行执行的依据。
- ADR-002（可判定性，gate 机器可判定）：「有 plan ≠ 裁剪阶段、P1/P2 仍需独立产出并过 gate」与「门槛必须机器可判定」一致——plan 的存在与否不改变任何 gate 判定。
- 「状态落盘」：roadmap/plan 均为工作区文件，符合状态落盘原则。

**⚠️ 冲突面——ADR-005**（adr.md:128-161）：ADR-005 决策「行为逻辑改动 → 至少走裁剪 agate」，与 WORKFLOW.md:203「行为逻辑单点 → …或直接做」冲突（详见 A5）。若「或直接做」是文档措辞失误，修正即可对齐 ADR-005；若作者有意对行为逻辑微改动放宽直接做，则是对 ADR-005 决策的修改，需先记录新 ADR 决策（含语境/理由/后果），并同步 CHANGELOG/UPGRADING。

**结论**：NEEDS_HUMAN_REVIEW（唯一原因：与 ADR-005 的冲突，需人工裁决是修措辞还是改 ADR）
**建议**：默认按「修措辞对齐 ADR-005」处理（删除 L203「或直接做」、澄清 L204 hotfix 限定声明性），由主 Agent 确认；若确认是要放宽，则补 ADR 记录后重审。

---

## 人工验收清单

- [x] 审查报告含 A1-A7 七项，每项有结论
- [x] MISALIGNED 项有差异描述 + 建议方向（A5：2 处）
- [x] 每条 NEEDS_HUMAN_REVIEW 配 `[HUMAN_CONFIRMED: ...]` —— **待主 Agent 确认**：A7 未确认，等同 MISALIGNED，不允许 commit
- [x] 审查报告落盘到 `docs/reviews/agate-alignment-review-{date}.md`
