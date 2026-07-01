---
review_date: 2026-07-02
reviewer: protocol-alignment-review
change_summary: 在 dispatch-protocol.md / dispatch-prompt.md / SELF-GATE.md 的派发模板中加 subagent 产出路径硬约束，防止产出文件写到 /tmp 或非约定路径
files_changed:
  - agate/dispatch-protocol.md
  - agate/assets/templates/dispatch-prompt.md
  - SELF-GATE.md
design_plan: docs/plans/agate-output-path-constraint-design-2026-07-02.md
---

# 协议-脚本对齐审查：subagent 产出路径约束

## 第一步：意图分析

本次变更的意图是**堵住"subagent 把产出文件写错位置导致主 Agent 判定空返回"的浪费路径**——给派发模板加禁止性约束（不得写入 /tmp / 工作区根目录 / 自选路径），让产出路径从"正向告知"升级为"正向告知 + 反向禁止"的硬约束。不是单纯改措辞，是改变约束强度。

## 第二步：反向传播——应被影响的文件

基于意图（给所有派发模板加路径硬约束），主动推断应被影响的文件：

| 优先级 | 文件 | 被影响的理由 | 是否在 diff 中 |
|--------|------|------------|---------------|
| P0 | agate/dispatch-protocol.md | 阶段产出派发模板的内联版 + 新增"非阶段产出的路径规范"通用节 | ✅ 已改 |
| P0 | agate/assets/templates/dispatch-prompt.md | 阶段产出派发模板的完整版（权威来源） | ✅ 已改 |
| P0 | SELF-GATE.md | 非阶段产出（self-gate 审查）派发模板 ×2 | ✅ 已改 |
| P1 | agate/orchestrator-template.md | 项目入口文件，引用 dispatch-protocol.md | ❌ 未改（设计 plan 确认无需同步：引用不内联） |
| P1 | agate/assets/execution-roles/*.md | 角色文件，"## 输出"节描述内容结构 | ❌ 未改（设计 plan 确认无需同步：角色文件不含路径） |
| P1 | agate/assets/review-roles/protocol-alignment-review.md | self-gate 审查员角色定义，"## 输出格式"节 | ❌ 未改（路径由派发 prompt 指定，非角色文件职责） |
| P1 | agate/WORKFLOW.md | 主流程文件，引用 dispatch-protocol.md | ❌ 未改（不内联派发模板） |
| P2 | CHANGELOG.md | 协议语义变更应标注 | ❌ 未改 ⚠️ 见 A5 |
| P2 | agate/scripts/check-protocol-consistency.py | CHECK 9 锚点表 | ❌ 未改（纯文档约束无脚本对应，见 A6） |

## 第三步：实际审查范围

已读以下文件全文：
- 变更文件：dispatch-protocol.md、dispatch-prompt.md、SELF-GATE.md
- 反向传播目标：orchestrator-template.md、WORKFLOW.md、protocol-alignment-review.md、execution-roles/*.md（grep 扫描）
- 权威规则源：dispatch-protocol.md（gate 表、派发模板）
- 设计文档：docs/plans/agate-output-path-constraint-design-2026-07-02.md
- 脚本：check-protocol-consistency.py（CHECK 9 锚点表）

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED（纯文档约束，无脚本对应，by design） |
| A2 | 脚本→文档对齐 | ALIGNED（无脚本变更，无文档需同步） |
| A3 | 一致性连锁 + 反向传播 | NEEDS_HUMAN_REVIEW（{project_root} 路径格式不一致 + 措辞详简不一致） |
| A4 | 测试覆盖 | ALIGNED（纯文档约束，设计 plan 明确不改测试，164 bats 全过） |
| A5 | 下游影响 + 文档传播 | MISALIGNED（CHANGELOG 未标注） |
| A6 | 锚点表覆盖 | ALIGNED（纯文档约束无脚本实现，无需锚点） |

**整体结论**：1 个 MISALIGNED（A5：CHANGELOG 未标注）+ 1 个 NEEDS_HUMAN_REVIEW（A3：路径格式 + 措辞一致性）。MISALIGNED 必须修复后方可 commit。

## 逐项审查

### A1: 文档→脚本对齐

**文档声明**（dispatch-protocol.md:317-324）：
```
## 输出（路径约束）
产出文件：docs/tasks/{Txxx}/{本阶段产出文件}

⚠️ 路径是硬约束，不是建议：
- 必须用 Write 工具写入上述路径
- 不得将产出文件写入 /tmp、工作区根目录、或其他自选路径
- 写到其他位置 = 未产出，主 Agent 只检查上述路径
- /tmp 可用于中间临时文件（如 gate-runner 落盘 traceback），但产出文件必须写入约定路径
```

**脚本实现**：无脚本对应。设计 plan（docs/plans/agate-output-path-constraint-design-2026-07-02.md:99）明确声明"不加脚本检查（产出路径由主 Agent 校验，不需要 gate 脚本介入）"。

** Enforcement 机制**：主 Agent 校验逻辑（dispatch-protocol.md:48-65）只检查约定路径——产出文件不存在 → 判定空返回 → 计入 retry。路径约束是软约束（通过空返回机制间接生效），非 gate 脚本硬拦截。

**结论**：ALIGNED
**理由**：路径约束是纯文档/prompt 层约束，设计上明确不引入脚本检查。 enforcement 通过现有"主 Agent 只检查约定路径"机制间接实现。文档声明与设计意图一致。

### A2: 脚本→文档对齐

**脚本变更**：无脚本变更。
**文档同步**：无脚本需同步。

**结论**：ALIGNED
**理由**：本次变更不涉及任何脚本逻辑，A2 不适用。

### A3: 一致性连锁 + 反向传播

#### A3a：一致性连锁（已知的衍生改动）

**阶段产出路径约束措辞**：
- dispatch-protocol.md:320-324（内联版）vs dispatch-prompt.md:39-43（完整版）

逐字对比：两处 4-bullet 块完全一致 ✓

**非阶段产出（SELF-GATE.md）路径约束措辞**：
- SELF-GATE.md:135（变更触发模式）：`⚠️ 路径是硬约束：必须用 Write 工具写入此路径，不得将产出文件写入 /tmp 或其他路径。`
- SELF-GATE.md:181（全量审查模式）：同上，完全一致 ✓

**发现 1（措辞详简不一致）**：阶段产出的路径约束是 4-bullet 块，非阶段产出（SELF-GATE.md）是 1-line 压缩版。1-line 版省略了：
- "工作区根目录"（仅说"/tmp 或其他路径"）
- "写到其他位置 = 未产出，主 Agent 只检查上述路径"
- "/tmp 可用于中间临时文件……但产出文件必须写入约定路径"

设计 plan（line 75）明确说"补加'不得写入 /tmp 或其他路径'"——短形式是设计意图，非遗漏。但"工作区根目录"被省略是个语义缺口：subagent 把文件写到工作区根目录时，1-line 版的"其他路径"虽可覆盖，但不如 4-bullet 版明确。

**结论**：NEEDS_HUMAN_REVIEW
**建议**：可接受短形式，但建议把"工作区根目录"补回 1-line 版（如"不得将产出文件写入 /tmp、工作区根目录或其他路径"），与阶段产出约束的关键禁止项对齐。是否补全由人决定。

#### A3b：反向传播（主动推断的应被影响文件）

**orchestrator-template.md**：
- grep 确认不内联派发模板，引用 dispatch-protocol.md（L52）
- 设计 plan（line 85-87）确认无需同步
- 结论：✓ 无需同步

**角色文件（execution-roles/*.md、review-roles/*.md）**：
- grep 扫描所有角色文件的"## 输出"节：均描述输出**内容结构**（字段、格式），不含输出**路径**
- 路径由派发 prompt（dispatch-prompt.md 模板）指定，非角色文件职责
- 设计 plan（line 101）明确声明"不改角色文件"
- 结论：✓ 无需同步

**protocol-alignment-review.md（self-gate 审查员角色）**：
- "## 输出格式"（line 54-90）描述报告结构（frontmatter + A1-A6 表 + 逐项详情）
- "## 审查原则"item 5（line 45）区分留痕文件/成果文件，但不指定路径
- 路径由 SELF-GATE.md 派发模板指定（含新增的路径约束行）
- 结论：✓ 无需同步（路径来自派发 prompt，非角色文件）

**WORKFLOW.md**：
- grep 确认引用 dispatch-protocol.md，不内联派发模板的"## 输出"节
- 结论：✓ 无需同步

**发现 2（{project_root} 路径格式不一致）**：

新增的"非阶段产出的路径规范"（dispatch-protocol.md:349）规定：
> 给出**具体路径**（用 `{project_root}/docs/reviews/xxx.md` 格式，不用纯占位符也不用绝对路径）

其示例（dispatch-protocol.md:358）：
> 路径：{project_root}/docs/reviews/agate-alignment-review-{date}.md

但 SELF-GATE.md 的实际派发模板（line 132、178）使用：
> docs/reviews/agate-alignment-review-{date}.md

**无 {project_root} 前缀**。这是"非阶段产出的路径规范"与其首要适用对象（SELF-GATE.md）之间的格式不一致。

合理化解释：SELF-GATE.md 是 agate 自身用（工作目录即 agate 仓库根），相对路径 `docs/reviews/...` 足够；`{project_root}/...` 格式面向使用 agate 的外部项目。但"非阶段产出的路径规范"未明确区分这两种场景，导致其声明的格式与其自身示例不匹配。

**结论**：NEEDS_HUMAN_REVIEW
**建议**：二选一——
1. 在"非阶段产出的路径规范"加一句"agate 自身用相对路径，外部项目用 {project_root}/ 前缀"，明确两种场景
2. 把 SELF-GATE.md 的路径也改成 `{project_root}/docs/reviews/...`（但 agate 自身无 {project_root} 配置，可能更混乱）
推荐方案 1。

### A4: 测试覆盖

**测试现状**：本次变更纯文档，无脚本行为变化。
**设计 plan 声明**（line 100）："不改测试（纯文档约束，不涉及脚本行为）"
**bats 验证**：`bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/` → 164 tests 全过，无退化。

**结论**：ALIGNED
**理由**：纯文档约束无需脚本测试。设计上明确不改测试。现有测试无退化。

### A5: 下游影响 + 文档传播

**下游影响**：
- 约束是**增量性**的（给 subagent 新增要求），不改变 gate 行为
- 不破坏现有项目：subagent 被告知写对路径，是质量提升
- 影响等级：低

**文档传播 — CHANGELOG**：
- 检索 CHANGELOG.md [Unreleased] 节：无"路径约束"/"产出路径"/"path constraint"相关条目
- 路径约束是行为性约束（声明"写到其他位置 = 未产出"），属于应标注的协议语义变更
- 设计 plan 的"变更文件清单"（line 89-95）未列 CHANGELOG

**结论**：MISALIGNED
**差异**：CHANGELOG [Unreleased] 未标注本次路径约束变更。
**建议**：在 CHANGELOG.md [Unreleased] > 新增 节加一条：
```
- **subagent 产出路径硬约束**：dispatch-protocol.md / dispatch-prompt.md 派发模板"## 输出"节加路径硬约束（不得写入 /tmp / 工作区根目录 / 自选路径），新增"非阶段产出的路径规范"节。SELF-GATE.md 两个派发模板同步。写错位置 = 未产出 = 重试浪费
```

### A6: 锚点表覆盖

**CHECK 9 锚点表**（check-protocol-consistency.py:486-572）：映射"文档声明的规则 → 对应脚本应含的关键词"。

**路径约束的脚本对应**：无。设计 plan（line 99）明确"不加脚本检查"。

**锚点表是否需要新增条目**：不需要。锚点表针对"有脚本实现"的协议规则。路径约束是 prompt 层约束，enforcement 通过主 Agent 校验机制（检查约定路径 → 不存在则空返回）间接生效，不是 gate 脚本。

**结论**：ALIGNED
**理由**：纯文档/prompt 约束无脚本实现，CHECK 9 锚点表无需新增条目。

## 闭环状态

| # | 审查项 | 结论 | 闭环动作 |
|---|--------|------|---------|
| A1 | 文档→脚本对齐 | ALIGNED | 通过 |
| A2 | 脚本→文档对齐 | ALIGNED | 通过 |
| A3 | 一致性连锁 + 反向传播 | NEEDS_HUMAN_REVIEW | 待人工确认：{project_root} 格式 + 措辞详简是否需统一 |
| A4 | 测试覆盖 | ALIGNED | 通过 |
| A5 | 下游影响 + 文档传播 | MISALIGNED | **必须修复**：CHANGELOG 加条目 |
| A6 | 锚点表覆盖 | ALIGNED | 通过 |

**阻塞 commit 的项**：A5（MISALIGNED，必须补 CHANGELOG 条目后重审）

**待人工确认的项**：A3（NEEDS_HUMAN_REVIEW，需附 `[HUMAN_CONFIRMED: ...]` 标记后方可 commit）
