---
phase: P4
task_id: TAG0030
type: implementation
parent: P2-design.md
trace_id: TAG0030-P4-20260904
status: draft
created: '2026-09-04'
agent: implementer
implementation_dir: agate/phase-cards/ + agate/assets/templates/ + agate/tests/
  + worktree根(AGENTS.md) + agate/(UPGRADING.md, CHANGELOG.md)
  + agate/assets/execution-roles/ + agate/assets/review-roles/ + agate/role-system.md
---

# P4-implementation — TAG0030 验收盲区机制批（templates-tests-meta 批落笔）

> 批次声明：P2 dispatch_plan batches[2]（id: templates-tests-meta, complexity: low）。
> 纯协议文档面改造，不涉及生产环境 `[PROD_NOT_TOUCHED]`。本批只改 5 个文件（dispatch-context.md
> 模板 / tests/README.md / worktree 根 AGENTS.md / UPGRADING.md / CHANGELOG.md），
> 未触碰 phase-cards/、assets/（除 dispatch-context.md 模板）、execution-roles/、review-roles/、
> check-gate.py、check-protocol-consistency.py、rules/、dispatch-prompt.md。

## 本批改动文件清单

| # | 文件 | 落笔位 | BDD 关联 | 锚词（逐字复用 P3 §2） | 状态 |
|---|------|--------|----------|------------------------|------|
| 1 | `agate/assets/templates/dispatch-context.md` | 约束节（子派发能力声明位之后）补环境清理/环境还原条目位 | BDD-5（RM-AG0057-① 派发模板面） | 环境还原 + 残留检查 | 已落笔 |
| 2 | `agate/assets/templates/dispatch-context.md` | 约束节补拆小默认指导条目位 | BDD-21（DEBT0026） | 拆小 + 体量（「改动体量 >5 文件」，P2-review N4 与 dispatch-prompt.md 行 49「输入文件 >5」区分） | 已落笔 |
| 3 | `agate/tests/README.md` | 「何时更新」节首条后补真实 gate 语义句 | BDD-19（DEBT0024） | 真实 gate 语义 | 已落笔 |
| 4 | `AGENTS.md`（worktree 根） | 「改脚本的工作流」节首补第 0 步 | BDD-20（DEBT0025） | 全量扫描 + 新增 CHECK | 已落笔 |
| 5 | `agate/UPGRADING.md` | 「## 3. 已知破坏性变更」节 v0.67.0 之前新增 v0.68.0 版本章节 | P1 §9（版本章节） | 无破坏性声明 + 四 phase 新条文摘要（仿 v0.67.0 节格式） | 已落笔 |
| 6 | `agate/CHANGELOG.md` | `## [0.67.0]` 之前新建 `## [Unreleased]` 节 | P1 §9（版本章节） | 按既有条目格式，不编造版本号（当前最新 [0.67.0] - 2026-09-03，P2-review N3） | 已落笔 |

## 新增文件核对表

| 新增文件路径 | 骨架归属 | CODE-MAP 处理 |
|--------------|----------|---------------|
| 无新增文件（本批只改既有模板/文档） | — | — |

## 自查结果（自查≠gate，未声称 P5 已过）

- 命令：`timeout 240s python3 -m pytest agate/tests/unit/test_tag0030_assertions.py -q --tb=short`
- 结果：**11 passed / 10 failed**——本批相关用例 BDD-5/19/20/21 全绿（单独筛选
  `-k "bdd_5 or bdd_19 or bdd_20 or bdd_21"` → 4 passed）。
- 10 个失败用例全部属于 phase-cards / assets-roles 批的目标文件（analyst.md、
  plan-design-review.md、architect.md、verifier.md）——本批未触碰这些文件，非本批引入，
  待并行批次落笔后转绿（P3 假绿核实表中这些文件当前本就为红）。
- 本批 5 文件落笔后，P3 假绿核实表对应行（dispatch-context.md / tests/README.md /
  AGENTS.md）由「0 命中」转「已命中」，与设计预期一致。

## 平台词护栏（CHECK14/15）

- 新增叙述段未含裸平台词（OpenCode / Claude Code / DSH / workflow / ralph / goal / task），
  长句用「subagent / 派发 / 主 Agent」表述；无代码示例，无需进代码围栏。
- dispatch-context.md 新增条目以 `- {…}` 占位符形式落笔，无行首 `- PASS` / `- FAIL`
  （check-p6-provenance 预判检测兼容）。

## P2-review 落笔注意落实

- **N3**：CHANGELOG.md 当前无 [Unreleased] 节（最新 [0.67.0] - 2026-09-03），本批已新建该节。
- **N4**：BDD-21 落笔用「改动体量 >5 文件」显式区分 dispatch-prompt.md 行 49 既有「输入文件 >5」
  硬规则（P2 §0.2 #9：不删不重复既有条目）。
- **N6**：本批跨包文件（tests/README.md / AGENTS.md / UPGRADING.md / CHANGELOG.md）在 P1 三包面
  之外，已列入本文件清单供 P7 交叉核对。

## 偏差声明

- 无 [DESIGN_GAP]、无 [SCOPE_GAP]、无 [SCOPE+]、无 [CLARIFY]——P2-design §0.1 #9~11 + #13
  与 P3-test-cases §2 锚词表足够明确，实现未做自主决策。

---

# P4-implementation — phase-cards 批（P2 dispatch_plan batches[0]，追加章节）

> 并行三批共享本产出文件：本章节声明 batches[0]（id: phase-cards, complexity: medium）落笔。
> 纯协议文档面改造，不涉及生产环境 `[PROD_NOT_TOUCHED]`。本批只改 4 个卡文件，
> assets-roles / templates-tests-meta 批文件不在本批触碰范围。
> 本批 `implementation_dir: agate/phase-cards/`（与 templates 批 frontmatter 声明并列，P7 交叉核对按章节归属）。

## 本批改动文件清单

| 文件 | 落笔位 | 关联 BDD | 落笔内容 |
|------|--------|---------|---------|
| `agate/phase-cards/P3-tdd.md` | step0「测试前基线」之后 | BDD-1/3 | 补「创建型测试清理钩子（强制要求）」段：创建即注册、测试结束无条件删除（不因响应非 2xx 中止删除）、删除接受 200/204/404 为已清理（afterEach 清理队列模式） |
| `agate/phase-cards/P4-implementation.md` | step0 基线行之后 | BDD-2 | 镜像补同源同锚词段（标注"与 P3 卡同源，只修 P3 卡不修本卡即复发"） |
| `agate/phase-cards/P6-acceptance.md` | 验收流程节（首次进入步骤表） | BDD-4 | 插入步骤 4「post-test 环境残留检查（强制步骤）」：快照比对或清理钩子验证二选一，残留未清不计入 PASS 证据；原步骤 4-10 重编号为 5-11；证据形态机制段落只读未动（P2 §0.2 #6） |
| `agate/phase-cards/P1-requirements.md` | 产出规格节 | BDD-7/9 | 补「人工体验路径验收（强制节）」：「Given seed 数据 → 页面有内容」强制句式，不得只用 fixture 或单测断言替代人工体验验收 |

## 新增文件核对表

| 新增文件路径 | 骨架归属 | CODE-MAP 处理 |
|------------|---------|--------------|
| 无新增文件（本批只改既有卡文件） | — | — |

## 自查结果（自查≠gate，未声称 P5 已过）

- 命令：`timeout 240s python3 -m pytest agate/tests/unit/test_tag0030_assertions.py -q --tb=short`
- 结果：**11 passed / 10 failed**——本批相关用例 BDD-1/2/3/4/7/9 **全部转绿**。
- 剩余 10 个失败（BDD-8/10~18）全部属于 assets-roles 批目标文件（analyst.md /
  plan-design-review.md / architect.md / verifier.md），为该批尚未落笔的预期红灯，本批未引入其他失败。
- 锚词 grep 核实：P3 行 11 / P4 行 12 / P6 行 14-15 / P1 行 111-113 全部命中本批锚词
  （清理钩子/创建即注册/无条件删除/200/204/404/残留检查/post-test/人工体验/seed 数据/页面有内容）。

## 偏差声明

- 无 [DESIGN_GAP]、无 [SCOPE_GAP]、无 [SCOPE+]、无 [CLARIFY]——P2-design §0.1 #1~4 + §2
  Phase 1/2 与 P3-test-cases §2 锚词表足够明确，实现未做自主决策。

---

# P4-implementation — assets-roles 批（P2 dispatch_plan batches[1]，追加章节）

> 并行三批共享本产出文件：本章节声明 batches[1]（id: assets-roles, complexity: medium）落笔。
> 纯协议文档面改造，不涉及生产环境 `[PROD_NOT_TOUCHED]`。本批只改 5 个文件
> （analyst.md / plan-design-review.md / architect.md / verifier.md / role-system.md 行 47），
> 不碰其他批文件（phase-cards/、templates/、tests/README.md、AGENTS.md、UPGRADING/CHANGELOG）。
> 本批 `implementation_dir: agate/assets/ + agate/role-system.md`（与另两批 frontmatter 声明并列，
> P7 交叉核对按章节归属）。

## 本批改动文件清单

| 文件 | 落笔位 | BDD | 锚词（逐字，以 test_tag0030_assertions.py 为准） |
|------|--------|-----|-------------------------------------------------|
| `agate/assets/execution-roles/analyst.md` | 输出节「BDD 验收条件」第 3 点补「人工体验路径验收」同源句 | BDD-8 | 「人工体验」「seed」 |
| `agate/assets/review-roles/plan-design-review.md` | 「评分维度（0-10）」标题后加形态分派头 + 维度组 + ≥2 候选要求；0-10 维度行与门槛 status 行原文保留 | BDD-10~15 | 「ui_render_shape」「维度组」「布局型」「三组」「渲染组件型」「architect」「候选」「权衡」「原文保留」「回落」 |
| `agate/assets/execution-roles/architect.md` | 视觉 checklist 头部定义视觉契约（单源） | BDD-16/17 | 「视觉契约」「可表达子集」「DOM 度量」「不收主观视觉」 |
| `agate/assets/execution-roles/verifier.md` | 「行为验证证据优先级」节补 DOM 度量量化证据句（getBoundingClientRect 示例进代码围栏） | BDD-18 | 「DOM 度量」「getBoundingClientRect」 |
| `agate/role-system.md` 行 47 | 七维扁平描述同步为形态分组口径（维度名保留） | 连带同步 | 与 plan-design-review 分派头一致（布局型三组 / 渲染组件型渲染正确性 + 动效时序） |

## 新增文件核对表

| 新增文件路径 | 骨架归属 | CODE-MAP 处理 |
|------------|---------|--------------|
| 无新增文件（本批只改既有角色/评审文件） | — | — |

## 落笔要点（对齐 P2-design §2 Phase 2/3/4 + P2-review D2~D5）

1. **plan-design-review 门槛契约冻结**：CHECK11 三锚词「视觉设计」「交互设计」
   「渲染正确性与时序」逐字仍在（维度行未动）；0-10 评分行 + status 映射行（门槛产出节）
   原文保留；只加形态分派头 + 维度组加载逻辑，无形态声明回落布局型默认（BDD-15）。
2. **视觉契约单源定义**（P2 §1 方案 A）：完整定义只落 architect.md 视觉 checklist 头部；
   verifier.md 只写交叉引用句（"可表达子集定义见 architect.md 视觉 checklist 头部，此处只
   交叉引用不重复"），未重复五类 DOM 度量完整定义，防漂移（P2 §0.2 #6 + 风险 2）。
3. **architect.md 渲染 checklist 行 93-99 只读不动**：仅视觉 checklist 头部插入定义块，
   渲染正确性 checklist 未触碰（BDD-12 引用源保持原样）。
4. **role-system 行 47 同步**：保留全部维度名（交互状态覆盖/交互设计细节/可访问性/移动端/
   组件完整性/AI Slop/视觉设计/渲染正确性与时序），改为「形态分组：布局型三组 = 布局/交互/
   视觉 + 渲染组件型/时序特效型 = 渲染正确性与时序 + 动效时序」表述，与 plan-design-review
   分派头一致（P2 §4 Modify 结论，P7 核对项）。
5. 平台词护栏：新增叙述段未引入裸平台词（OpenCode/Claude Code/DSH 等），getBoundingClientRect
   示例置于代码围栏（P2 §0.3 风险 6）。

## 自查结果（自查≠gate，未声称 P5 已过）

- 命令：`timeout 240s python3 -m pytest agate/tests/unit/test_tag0030_assertions.py -q --tb=short`
- 结果：**21 passed（0 failed）**——本批 BDD-8/10~18 全部转绿，且未影响其他批次用例
  （BDD-1~7/9/19~21 保持绿）。
- 既有锚词审计（CHECK11 双保险）：`test_review_role_docs.py` → **14 passed**；
  `test_protocol_mechanism_anchors.py` → **28 passed**。
- `check-protocol-consistency.py --strict-errors-only` → **0 ERROR**
  （329 个 WARNING 为既有陈旧引用，与本次改动无关，基线相同）。
- 全量 unit 目录并行自查（`-n auto`）：结果记录于 P4-progress.md。

## 偏差声明

- 无 [DESIGN_GAP]、无 [SCOPE_GAP]、无 [SCOPE+]、无 [CLARIFY]——P2-design §0.1 #5~8 + #12、
  §2 Phase 2/3/4 与 P3-test-cases §2 锚词表足够明确，实现未做自主决策。
