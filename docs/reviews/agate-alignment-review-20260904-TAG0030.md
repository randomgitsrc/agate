---
date: 2026-09-04
task_id: TAG0030
scope: commit e39c897
reviewer: protocol-alignment-review
conclusion: aligned
---

# 协议-脚本对齐审查 — TAG0030（commit e39c897）

> 变更触发模式正式自审。审查对象 = commit e39c897（P4 落笔：14 个协议文件批量改动，
> 1626 行新增），意图 = 补强验收盲区机制（RM-AG0057 ①~④ + DEBT0024/25/26，纯协议文档面改造）。
> 本任务无脚本改动，审查重心在协议-协议对齐、反向传播、测试覆盖、锚点表与 ADR 一致性。
> `[PROD_NOT_TOUCHED]`——本审查不修改任何协议文件，只产出本报告 + 留痕文件。

## 意图分析（SELF-GATE 第一步）

本次变更的意图是**补强协议验收盲区机制**：① 测试副作用/环境还原 gate（P3/P4 卡创建型测试
清理钩子条文 + P6 卡 post-test 环境残留检查步骤 + dispatch-context 模板环境清理条目位）；
② P1 人工体验路径验收节（用户可见页面 + 内容受 seed 影响 → 强制「Given seed 数据 → 页面有
内容」BDD）；③ plan-design-review 形态驱动化（先读 `ui_render_shape` 再加载维度组 + ≥2 候选
权衡要求）；④ 视觉契约可表达子集（宽度/高度/对齐/重叠/溢出五类 DOM 度量，不收主观视觉）；
⑤ DEBT0024/25/26 三连（真实 gate 语义 / 新 CHECK 上线前全量扫描 / 拆小派发指导）。全部为
协议文档条文层改造，不改变任何脚本控制流。

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | ALIGNED |
| A4 | 测试覆盖 | ALIGNED |
| A5 | 下游影响 + 文档传播 | ALIGNED |
| A6 | 锚点表覆盖 | ALIGNED |
| A7 | 设计原则一致性 | ALIGNED |

**总结论：aligned**（无 MISALIGNED / 无 NEEDS_HUMAN_REVIEW 项，可 commit）。

## 逐项审查

### A1: 文档→脚本对齐

**文档声明**：

- plan-design-review.md:15-17（形态分派头）：
  > 评审开始先读受评任务 frontmatter 的 `ui_render_shape` 声明（layout / render_component /
  > temporal_effects；缺失或未声明 = **回落布局型默认**）

**脚本实现**：

- agate-md-field-get.py:30-31（ui_render_shape 字段语义）：
  > ui_render_shape  frontmatter 字符串（P1 渲染形态声明，规范值 layout/render_component/
  > temporal_effects）/ 正文 "ui_render_shape: <值>"（presence 语义，缺失即布局型默认）
- agate-md-field-get.py:154-157（字段登记）：`ui_render_shape（TAG0006 P2 §2.15.1）：P1 渲染
  形态声明可选字段（规范值，开放集合）` 已入 `agate-md-field-get.py` 字段清单

**结论**：ALIGNED。**差异**：无。角色文件引用的字段名、值域、缺省语义与脚本既有定义
（TAG0006 机制）逐字一致；`缺失或未声明 = 回落布局型默认` 与 `agate-md-field-get.py` 的
「缺失即布局型默认」presence 语义完全对齐。

**A1 补充（CHECK11 三锚词 ↔ 白名单）**：

- 脚本（check-protocol-consistency.py:907-908 UIUX_DOC_ANCHORS）：
  `("agate/assets/review-roles/plan-design-review.md", ("视觉设计", "交互设计", "渲染正确性与时序"))`
- 文档（plan-design-review.md:39/40/41）：三锚词逐字俱在（「视觉设计」行 39、「交互设计细节」
  行 40 含「交互设计」锚词、「渲染正确性与时序」行 41）——本次 +20 行纯新增，维度行零移动。
- verifier.md / P6-acceptance.md 白名单锚词（consistency:916-923：available/supplementable/
  GAP/人工复核/输入态/帧序列/时序截图/渲染输出对比/渲染形态）：本次 diff 未删任何一词，
  consistency --strict-errors-only 实跑 0 ERROR 为实证。

### A2: 脚本→文档对齐

**结论**：ALIGNED。**差异**：无。本次 diff 14 个文件全部为 `.md` 文档条文，无任何
`agate/scripts/*.py` / `*.sh` 改动（git show --stat 实证），无脚本行为变化需要反向同步到文档。

### A3: 一致性连锁 + 反向传播

**A3a（连锁——已知衍生改动）**：

- role-system.md:47 连带 Modify（P2-design §4 决策：plan-design-review 改形态分派后七维扁平
  罗列必须同步为形态分组口径）——已落笔：行 47 现文「形态分组：布局型三组 = 布局/交互/视觉——
  交互状态覆盖/交互设计细节/可访问性/移动端/组件完整性/AI Slop/视觉设计；渲染组件型/时序特效型 =
  渲染正确性与时序 + 动效时序」，维度名原文保留，与 plan-design-review 分派头（行 19-25）一致。
- UPGRADING.md（+22，v0.68.0 章节，含无破坏性声明）与 CHANGELOG.md（+30，Unreleased 节）——
  已同步（P2-design §0.1 #13）。

**A3b（反向传播——应被影响但 diff 未列的文件逐一验证）**：

| 候选文件 | 应改/不必改 | 理由（引用原文） |
|---------|------------|-----------------|
| agate/rules/review-mapping.md | 不必改 | 全文 55 行只引用角色名（行 19「plan-design-review」）+ 产出文件名 + status 字段语义（行 36-44），无维度清单/形态细节；形态驱动化不改映射机制（P2-design §0.2 #4 同判） |
| agate/WORKFLOW.md | 不必改 | 行 60 仅目录树列文件名；行 311 评审角色描述「审视觉/交互/渲染形态适配维度」——仍是角色职责概述，形态分组内部逻辑不改变该概述语义；gate 表无维度清单 |
| agate/assets/templates/task-files.md | 不必改 | 行 331-346 已含渲染形态声明机制 + 按形态 checklist（「布局/交互/视觉 或 渲染正确性/动效时序」，与分派头维度组一致）；行 332 声明「形态声明必须与 P1 frontmatter 的 ui_render_shape/ui_ux_dimensions 一致」——与 plan-design-review 分派头读取行为自洽 |
| agate/assets/execution-roles/vision-analyst.md | 不必改 | grep 全文无「视觉契约/DOM 度量/可表达子集」词；architect.md:93-94 视觉契约将「主观视觉」归入「截图人工复核或 vision-analyst 描述」——与 vision-analyst 被动截图翻译定位互补（P2-design §0.2 #5 明示不改） |
| agate/assets/templates/dispatch-prompt.md | 不必改 | 行 49 已有分批硬规则「产出文件 >3 个或输入文件 >5 个时，必须分批派发或在本节明确说明为何不分批」；新增 dispatch-context.md:33 条目是「改动体量 >5 文件按体量评估拆小」的**默认指导**（「外部拆小兜底，与 subagent 内部自主拆互补」），是互补层而非重复（P2-design §0.2 #9 同判） |

**结论**：ALIGNED。**差异**：无——五个反向传播候选全部验证为「不必改」，理由均引用原文，
无遗漏的应传播文件。

### A4: 测试覆盖

**测试存在性**：agate/tests/unit/test_tag0030_assertions.py（11.8KB，P3 commit 新建，
BDD-1~21 锚词 grep 断言，任一条文被删即转红）+ 既有双保险 test_review_role_docs.py /
test_protocol_mechanism_anchors.py（CHECK11 三锚词同锁）。

**最近一次实跑输出（本人复核，非仅采信自查）**：

- `pytest test_tag0030_assertions.py test_review_role_docs.py test_protocol_mechanism_anchors.py`
  → **63 passed in 0.09s**（21 审计 + 42 双保险）
- `pytest agate/tests/unit/ -n auto` → **1311 passed, 2 failed, 2 skipped**；2 failed 均为
  test_agate_next_card.py 并行干扰 flaky（test_nc_byte_stability_two_calls_sha256_equal /
  test_nc_symlink_script_readlink_resolves），单跑 2 passed、全文件 -n auto 重跑 **22 passed**
  复证为并行干扰而非本次改动回归（本次改动面 14 个 .md 文件，不触及 next-card 脚本与卡片结构）。
- 锚词-落笔逐字对应抽查（与 P4-review §3 表一致）：P3 卡行 11「清理钩子/创建即注册/无条件删除/
  200/204/404」、P4 卡行 12 镜像同锚词、P6 卡行 14「post-test 环境残留检查」、P1 卡行 111-113
  「人工体验/Given seed 数据 → 页面有内容」、analyst.md 行 47「人工体验/seed」、
  dispatch-context.md 行 32-33「清理/残留/拆小/体量」、tests/README.md 行 117「真实 gate 语义」、
  AGENTS.md 行 19「全量扫描/新增 CHECK」、plan-design-review 行 15-32 全组、architect.md 行 90-94
  「视觉契约/可表达子集/DOM 度量/不收主观视觉」、verifier.md 行 85-95（getBoundingClientRect
  示例在代码围栏内）。

**结论**：ALIGNED。**差异**：无。边界（假绿规避 AND 语义、锚词逐字）由 P3 测试设计保障，
实跑全绿实证。

### A5: 下游影响 + 文档传播

**无破坏性变更声明**：UPGRADING.md v0.68.0 章节（行 92-113 区间）明示「本版本无破坏性变更，
零迁移动作——未改 .state.yaml schema / 既有任务文件格式 / 3 个 hook 薄壳」；CHANGELOG.md
Unreleased 节（行 27-53）逐条标注四类机制 + DEBT 三连。

**下游影响评估**：新条文约束的是**下游任务**的测试写法（清理钩子）、P1 产出（人工体验 BDD）、
评审行为（形态分派 + ≥2 候选），不改变既有任务数据格式、gate 判据（0-10/status 冻结）、
hook 行为；对存量任务零影响（UPGRADING 逐条声明）。

**文档传播**：五个反向传播候选全部核查为「不必改」（见 A3b），无遗漏传播文件；被影响面
（14 个文件）本身即 P2-design §0.1 Modify 表 #1~13 全命中，无表外改动（P4-review §1 实证，
本审查以 diff --stat 复证）。

**结论**：ALIGNED。**差异**：无。

### A6: 锚点表覆盖

**CHECK11 三锚词保持**：consistency 行 907-908 白名单（「视觉设计」「交互设计」「渲染正确性
与时序」）↔ plan-design-review.md 行 39/40/41 逐字俱在——本次 diff 为 +20 行纯新增，锚词所在
维度行零移动；`test_review_role_docs.py` 双保险同锁（42 用例含）。

**consistency 复核实跑**：

```
python3 agate/scripts/check-protocol-consistency.py --strict-errors-only
→ 仅有 331 个 WARNING，无 ERROR。EXIT=0
```

331 = 329 存量 + 2 条「成果文件未写出」引用 WARNING（dispatch-context 引用本审查产出文件路径，
写完成果文件后自动回落存量）。CHECK 9 锚点表无需更新（本任务无新字段 schema、无新增校验脚本，
BDD-6 审计载体是 pytest 单测而非新 CHECK——P2-design §0.2 #2 同判）。

**结论**：ALIGNED。**差异**：无。

### A7: 设计原则一致性

| 相关 ADR | 本次变更符合性 |
|---------|---------------|
| ADR-002 可判定性（gate 门槛机器可判定，行 41-65） | 符合——新条文全部围绕「可量化/可机器判定」强化：五类 DOM 度量（architect.md:91-92）、≥2 候选+权衡打回（plan-design-review:27-29）、0-10/status 门槛冻结（行 31-32 声明原文保留） |
| ADR-005 改动性质决定流程（行 128-162） | 符合——本次为声明性条文改动（不改变任何控制流），走完整 agate 流程属保守执行 |
| ADR-006 双层角色（行 165-191） | 符合——plan-design-review 仍是独立评审角色（agent=plan-design-review），agent≠main 硬拦截语义未动 |
| ADR-010 受控例外（行 304-348） | 符合——verifier DOM 度量量化证据（行 85-95）是**新增证据形式**而非「复用既有证据」机制，与 ADR-010 的判定条件/保守方向无冲突 |
| ADR-011 引导型 CLI（行 352-377） | 不涉及——本任务无新工具/无写入校验逻辑 |
| TAG0006 形态机制（以条文形式散落，非独立 ADR 标题） | 符合——ui_render_shape 值域引用一致（A1）、CHECK11 三锚词保持（A6）、P2 卡「渲染正确性与时序」维度行原文保留（plan-design-review:41） |
| TAG0028 子派发边界（dispatch-protocol.md:989-1003） | 符合——dispatch-context.md:33 拆小条目声明「外部拆小兜底，与 subagent 内部自主拆互补」，与子派发两条硬边界 + judge 例外（行 995-1003）互补无冲突 |

**结论**：ALIGNED。**差异**：无。未发现未记录的架构决策，无需补充新 ADR。

## 反向传播检查（汇总）

| 文件 | 判断 | 依据 |
|------|------|------|
| agate/rules/review-mapping.md | 不必改 | 仅角色名/产出名/status 语义引用（行 9/19/36-44） |
| agate/WORKFLOW.md | 不必改 | 角色职责概述（行 311）仍准确 |
| agate/assets/templates/task-files.md | 不必改 | 形态声明机制已完备（行 331-346）且自洽 |
| agate/assets/execution-roles/vision-analyst.md | 不必改 | 无冲突词，定位互补（P2 §0.2 #5） |
| agate/assets/templates/dispatch-prompt.md | 不必改 | 行 49 硬规则与新增条目位互补（P2 §0.2 #9） |

## DESIGN_GAP 优先核查

本任务 P7 未到，任务目录无 P7-consistency.md，无 `[DESIGN_GAP_REVIEWED: ...]` / REVIEWED-ACCEPTED
记录；本审查也未发现需按 DESIGN_GAP 处理的文档-脚本不一致（A1-A7 全部 ALIGNED），无已知偏离
需要标注。

## 审查原则合规

- 逐项引用原文行号（文档行号取 worktree 当前文件 grep 实证，脚本行号取 check-protocol-consistency.py
  / agate-md-field-get.py 原文）✓
- 语义判断（presence 语义 / 互补 vs 重复 / 冻结 vs 新增）而非关键词匹配 ✓
- 不改任何代码/协议文件，只产报告 + 留痕 ✓
- 无 NEEDS_HUMAN_REVIEW 项，无需 HUMAN_CONFIRMED 配对 ✓
- 结论 aligned，可 commit。

## 附录：实跑命令与输出签名

- `python3 -m pytest agate/tests/unit/test_tag0030_assertions.py agate/tests/unit/test_review_role_docs.py agate/tests/unit/test_protocol_mechanism_anchors.py -q --tb=short` → `63 passed in 0.09s`
- `python3 -m pytest agate/tests/unit/ -q --tb=no -n auto` → `1311 passed, 2 failed, 2 skipped`（2 failed 复证为 next_card 并行 flaky：单跑/全文件重跑 22 passed）
- `python3 agate/scripts/check-protocol-consistency.py --strict-errors-only` → `仅有 331 个 WARNING，无 ERROR。EXIT=0`
- `git show e39c897 --stat` → 23 文件 / 1626 insertions(+), 10 deletions(-)，其中 14 个协议文件与任务目录，无脚本改动
