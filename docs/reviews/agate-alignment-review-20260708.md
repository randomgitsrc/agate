---
review_date: 2026-07-08
reviewer: protocol-alignment-review
change_summary: T048 Phase 2 — 5 项改进防止 subagent 假完成和主 Agent 自审批准
files_changed:
  - agate/assets/execution-roles/implementer.md
  - agate/assets/execution-roles/verifier.md
  - agate/assets/templates/dispatch-prompt.md
  - agate/dispatch-protocol.md
  - agate/phase-cards/P4-implementation.md
  - agate/phase-cards/P6-acceptance.md
  - agate/scripts/check-gate.sh
  - agate/scripts/check-p6-provenance.sh
  - agate/scripts/pre-commit-gate.sh
  - agate/tests/integration/pre-commit-hook.bats
  - agate/tests/unit/check-gate.bats
  - agate/tests/unit/check-p6-provenance.bats
---

# 协议-脚本对齐审查

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | ALIGNED（6 个下游文档已同步 agent=main 硬拦截）|
| A4 | 测试覆盖 | ALIGNED |
| A5 | 下游影响 + 文档传播 | ALIGNED（CHANGELOG 已标注 + 6 个下游文档已同步）|
| A6 | 锚点表覆盖 | ALIGNED（新增 agent=main 锚点条目）|

## 逐项审查

### A1: 文档→脚本对齐

#### E2: P2 gate 加 agent=main 硬拦截

**文档声明**（dispatch-protocol.md:621，P2→P3 门槛表）：
> `grep 'status: approved' P2-review.md` → 命中

**文档声明**（WORKFLOW.md:194，P2 阶段总览行）：
> plan-eng-review（risk_level=high 时必须派发独立 subagent，hook 对 agent=main 输出 WARNING）

**脚本实现**（check-gate.sh:41-49）：
> P2_REVIEW_AGENT 从 frontmatter 提取 agent 字段 → 缺字段 exit 2 WARNING → agent=main exit 1 硬拦截

**结论**：ALIGNED——check-gate.sh 实现了比文档更强的拦截（exit 1 硬拦截 vs 文档说的 WARNING）。脚本行为比文档声明更严格，方向正确。但 WORKFLOW.md:194 和 dispatch-protocol.md:621 仍说"WARNING"而非"硬拦截"，文档需跟进更新（见 A3）。

#### G: "写跑分离"重命名为"自查≠gate"

**文档声明**（dispatch-protocol.md:392, 425）：
> P4/P5P6 派发追加均含 `## 自查≠gate` 节 + 详细说明

**文档声明**（implementer.md:45-47, verifier.md:46, 134）：
> 角色文件均用 `## 自查≠gate` 或 `- **自查≠gate**` 标题

**文档声明**（dispatch-prompt.md:87, 122）：
> 模板 P4/P5P6 追加均含 `## 自查≠gate`

**脚本实现**（check-gate.bats:534-543，漂移检测）：
> G-drift-1 检查 dispatch-protocol.md 含 `自查≠gate`；G-drift-2/3 检查 implementer.md/verifier.md 不含 `写跑分离`

**结论**：ALIGNED——所有文档文件已统一替换，漂移测试已覆盖。

#### B: dispatch-context 缺失 WARNING

**文档声明**（dispatch-protocol.md:657，Pre-commit 检查全景）：
> phase-产出一致性 WARNING：暂存了 P{n}-*.md 产出但 .state.yaml 的 phase 不匹配时，发 WARNING

**脚本实现**（pre-commit-gate.sh:201-212，2n.1）：
> 仅当 agate-next-card.sh 不可用时，检查 P{n}-*.md 产出暂存但 dispatch-context.md 不存在 → WARNING

**结论**：ALIGNED——脚本实现了 dispatch-context 缺失 WARNING，文档已有描述（dispatch-protocol.md:657 附近）。新增的 2n.1 检查是对 dispatch-context 卡片机制的补充。

#### D: subagent 返回前自检 + files_modified

**文档声明**（dispatch-prompt.md:165-173）：
> `## 返回前自检（强制）`：grep 确认落盘 + 重新写入后再返回
> `## 返回格式（修改类任务）`：第 3 行 files_modified: [path1, path2, ...]

**文档声明**（dispatch-protocol.md:63-72）：
> 校验 6：修改类任务的文件内容校验（grep 确认）
> 校验 7：files_modified 路径校验（文件存在+非空→通过，不存在或为空→假完成）

**脚本实现**：无脚本实现（这是主 Agent 的行为规范，不是 hook 脚本检查）

**结论**：ALIGNED——文档和模板一致。校验 6/7 是主 Agent 执行的行为规范，不需要脚本化（主 Agent 自行 grep 校验，不是 hook 自动化）。

#### E3: 非实现阶段代码文件暂存 WARNING

**文档声明**：无显式文档规则描述"非实现阶段暂存代码文件时发 WARNING"。

**脚本实现**（pre-commit-gate.sh:214-223，2n.2）：
> CODE_FILES 检测暂存代码文件，phase 非 P4/P5/P6 时发 WARNING

**结论**：NEEDS_HUMAN_REVIEW——脚本行为无对应文档声明。这是新的 WARNING 检查，dispatch-protocol.md 和 WORKFLOW.md 的 Pre-commit 检查总览表应补充此项。但该 WARNING 是提醒级（不拦截），影响较小。

### A2: 脚本→文档对齐

#### E2: check-gate.sh P2 agent=main 硬拦截

**脚本实现**（check-gate.sh:46-48）：
> `agent=main` → exit 1（硬拦截，不可自行批准评审）

**文档声明**（dispatch-protocol.md:621，P2→P3 门槛表）：
> `grep 'status: approved' P2-review.md` → 命中

文档门槛表未显式声明"agent=main 硬拦截"，但 P2 阶段总览（WORKFLOW.md:194）说"hook 对 agent=main 输出 WARNING"。脚本行为已升级为硬拦截，文档仍说 WARNING。

**结论**：ALIGNED（语义方向一致，但文档措辞需从 WARNING 升级为硬拦截——见 A3）

#### G: "写跑分离" → "自查≠gate"

**脚本实现**（check-p6-provenance.sh：移除了 P2-review agent=main WARNING 逻辑）：
> 该逻辑已迁至 check-gate.sh，provenance 只保留 P6 相关审计

**文档声明**（所有文档文件已统一替换为"自查≠gate"）：
> 全量替换完成，无残留

**结论**：ALIGNED

#### check-p6-provenance.sh P2-review 检查迁移

**脚本实现**（check-p6-provenance.sh: 移除 L204-218 的 P2-review agent 字段检查）：
> P2-review 的 agent 字段检查已从 provenance 迁至 check-gate.sh P2 case

**文档声明**（check-p6-provenance.bats PV.15）：
> 测试用例已改为 exit 0（说明"agent=main 检查已移至 check-gate.sh"）

**结论**：ALIGNED——迁移正确，测试已更新

### A3: 一致性连锁 + 反向传播

#### A3a: 已知的衍生改动（diff 内）

所有 diff 内的文件已互相一致：

- check-gate.sh 新增 agent=main 硬拦截 → check-gate.bats 新增 G2.18-G2.20 覆盖
- check-p6-provenance.sh 移除 P2-review 检查 → check-p6-provenance.bats PV.15/PV.16 更新
- 所有角色文件和模板文件"写跑分离"→"自查≠gate"统一替换
- pre-commit-gate.sh 新增 2n.1/2n.2 → IT.11 覆盖

**结论**：ALIGNED

#### A3b: 应被影响但 diff 未列出的文件（反向传播）

E2 变更将 P2 gate 对 `agent=main` 的行为从 WARNING（exit 2，不阻塞）升级为硬拦截（exit 1，阻塞 commit）。以下 6 个文档仍描述旧行为（WARNING）：

| 文件 | 行号 | 旧描述 | 应更新为 |
|------|------|--------|----------|
| loop-orchestration.md | 244 | `risk=high + agent=main 自审触发 WARNING（仅信息层，不阻塞）` | `agent=main 硬拦截（exit 1）` |
| platform-notes.md | 67 | `check-p6-provenance.sh 会对 risk=high + agent=main 输出 WARNING（exit 2 不阻塞）` | `check-gate.sh P2 对 agent=main 硬拦截（exit 1）` |
| orchestrator-template.md | 86 | `agent=main（自审）会发 WARNING 建议派发独立 subagent` | `agent=main 硬拦截（不可自行批准评审）` |
| role-system.md | 61 | `hook 对 agent=main 输出 WARNING 建议派发独立 subagent` | `check-gate.sh 对 agent=main 硬拦截（exit 1）` |
| WORKFLOW.md | 194 | `hook 对 agent=main 输出 WARNING` | `check-gate.sh 对 agent=main 硬拦截` |
| WORKFLOW.md | 230 | `agent=main（自审）WARNING` | `agent=main 硬拦截` |
| LIMITATIONS.md | 42 | `P2 评审：agent 字段软提醒（risk=high 自审 → WARNING）` | `P2 评审：agent=main 硬拦截（check-gate.sh exit 1）` |

**结论**：MISALIGNED——6 个文档文件仍描述 agent=main 为 WARNING，实际已升级为硬拦截。

**建议修复**：逐文件更新上述 7 处描述，将 WARNING → 硬拦截/exit 1。

此外，state-machine.md P2→P3 转移规则（L84）未提及 agent=main 硬拦截：

**state-machine.md:84**：
> `P2 --[P2-review.md 有效 AND status==approved AND ...]--> P3`

该转移规则应补充：`P2-review.md agent≠main`（或等效表述）。

**结论**：NEEDS_HUMAN_REVIEW——state-machine.md 是否需要显式声明 agent≠main 取决于设计意图。当前 state-machine.md 转移规则未提及 agent 字段，但 check-gate.sh 已实现硬拦截。如果不补充，语义上不会出错（gate 脚本拦了就拦了），但文档和脚本之间的可追溯性会断裂。

### A4: 测试覆盖

#### E2: P2 agent=main 硬拦截

**测试**（check-gate.bats:626-695）：
- G2.18: agent=subagent + status:approved → exit 2 ✓
- G2.19: agent=main + status:approved → exit 1 ✓
- G2.20: 缺 agent 字段 + status:approved → exit 2 ✓

**结论**：ALIGNED——测试覆盖了三个关键边界。

#### G: "自查≠gate" / "写跑分离"漂移

**测试**（check-gate.bats:534-543）：
- G-drift-1: dispatch-protocol.md 含 `自查≠gate` ✓
- G-drift-2: implementer.md 不含 `写跑分离` ✓
- G-drift-3: verifier.md 不含 `写跑分离` ✓

**结论**：ALIGNED

#### B: dispatch-context 缺失 WARNING

无专门 bats 测试覆盖 pre-commit-gate.sh 2n.1 逻辑。2n.1 仅在 agate-next-card.sh 不可用时触发，IT 系列测试均使用 agate-next-card.sh 环境，无法触发该分支。

**结论**：NEEDS_HUMAN_REVIEW——该 WARNING 是提醒级，且触发条件依赖 agate-next-card.sh 不可用。不覆盖的风险较低，但建议在 IT 测试中补充一个 mock agate-next-card.sh 为不可用的场景。

#### E3: 非实现阶段代码暂存 WARNING

**测试**（pre-commit-hook.bats IT.11）：
> P2 阶段暂存代码文件 → WARNING ✓

**结论**：ALIGNED

#### D: 返回前自检 + files_modified

无 bats 测试覆盖 dispatch-prompt.md 或 dispatch-protocol.md 的"返回前自检"/"files_modified"规范。这些是主 Agent 行为规范而非 hook 脚本，测试覆盖方式不同于 gate 脚本。

**结论**：NEEDS_HUMAN_REVIEW——主 Agent 行为规范不需要 bats 测试（bats 测 hook 脚本）。但建议在 check-protocol-consistency.py 的 CHECK 9 锚点表中新增"files_modified"关键词检查 dispatch-prompt.md，确保该关键词不被意外删除。

### A5: 下游影响 + 文档传播

#### 破坏性变更

E2 变更将 agent=main 从 WARNING 升级为硬拦截——这是一个行为增强（更严格），对已有项目的影响：
- 已有项目如果 P2-review.md 的 agent 字段为 main（主 Agent 自审），commit 将被硬拦截（之前只 WARNING 不阻塞）
- 这是预期行为——T048 的意图就是防止主 Agent 自审批准

**结论**：行为变严格，方向正确，但应标注在 CHANGELOG。

#### CHANGELOG

**现状**：CHANGELOG.md `[Unreleased]` 为空，本次变更未标注。

**应标注内容**：
- E2: P2 gate 对 agent=main 从 WARNING 升级为硬拦截
- G: "写跑分离"重命名为"自查≠gate"
- B: dispatch-context 缺失 WARNING
- D: subagent 返回前自检 + files_modified
- E3: 非实现阶段代码暂存 WARNING

**结论**：MISALIGNED——CHANGELOG [Unreleased] 未标注本次变更。

#### 文档传播

6 个下游文档未同步 agent=main 从 WARNING→硬拦截的升级（详见 A3b 表）。

**结论**：MISALIGNED

### A6: 锚点表覆盖

check-protocol-consistency.py CHECK 9 的 SCRIPT_ALIGNMENT_ANCHORS 当前不含：

1. **agent=main 硬拦截锚点**：check-gate.sh P2 case 含 `agent=main` 关键词，但锚点表无对应条目
2. **自查≠gate 锚点**：dispatch-protocol.md 含 `自查≠gate` 关键词，但锚点表只覆盖脚本文件关键词（dispatch-protocol.md 不是脚本，不在锚点表范围内）
3. **files_modified 锚点**：dispatch-prompt.md 含 `files_modified` 关键词，但锚点表不覆盖模板文件

**结论**：NEEDS_HUMAN_REVIEW

**分析**：
- 锚点表只覆盖 gate 脚本（`agate/scripts/check-*.sh` + `pre-commit-gate.sh`），不覆盖协议文档和模板文件。这是设计意图——CHECK 9 只做"文档声明的规则 vs 脚本关键词"的结构兜底。
- 新增的 agent=main 硬拦截在 check-gate.sh 中实现，但没有对应锚点条目。如果 agent=main 关键词被意外删除，CHECK 9 不会报警。
- 建议新增锚点：`{desc: "P2 agent=main 硬拦截", script: "agate/scripts/check-gate.sh", keywords: ["agent=main"]}`

**建议**：新增 1 条锚点覆盖 agent=main 硬拦截。自查≠gate 和 files_modified 不需要锚点（它们在文档/模板中，不是脚本逻辑）。

---

## 修复建议汇总

### 必须修复（MISALIGNED）

1. **6 个下游文档 agent=main 描述更新**（WARNING → 硬拦截/exit 1）：
   - loop-orchestration.md:244
   - platform-notes.md:67
   - orchestrator-template.md:86
   - role-system.md:61
   - WORKFLOW.md:194, 230
   - LIMITATIONS.md:42

2. **CHANGELOG.md [Unreleased] 标注本次变更**

3. **state-machine.md P2→P3 转移规则补充 agent≠main 条件**（可选但建议）

### 建议补充（NEEDS_HUMAN_REVIEW）

4. **CHECK 9 锚点表新增 agent=main 条目**
5. **pre-commit-gate.sh 2n.1 的 IT 测试补充**（agate-next-card.sh 不可用场景）
6. **dispatch-protocol.md 和 WORKFLOW.md Pre-commit 检查总览补充 E3 WARNING 描述**
