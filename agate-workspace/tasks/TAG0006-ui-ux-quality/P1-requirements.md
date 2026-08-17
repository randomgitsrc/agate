---
phase: P1
task_id: TAG0006-ui-ux-quality
type: problems
parent: P0-brief.md
trace_id: TAG0006-P1-20260817
status: draft
created: 2026-08-17
agent: analyst
# ── v2.0 机器字段 ──
risk_level: medium
phases: [P1, P2, P3, P4, P5, P6, P7, P8]
packages: [agate-docs, agate-scripts-py, agate-tests]
domains: [frontend, backend]
implicit_coupling: true
# 跳过风险: 无阶段裁剪——协议本体增强带脚本+测试改动，P2/P4/P5/P6/P7/P8 全保留（P3 因非 low 不可裁）
---

[NO_NEED_CONFIRM]

# P1 需求基线 — agate UI/UX 验收质量机制

> 本任务为 **agate 协议本体增强**（dogfooding）：改造对象是 worktree 里的协议文件（`agate/*.md`、`agate/assets/*.md`、`agate/phase-cards/*.md`、`agate/scripts/*.py`），不是业务 UI 应用。需求基线描述「协议机制应该如何行为」，BDD 验收对象是**协议文档/角色定义/gate 脚本的产出行为**——P6 验收本任务时以"读协议文件是否含该要求 + 跑 check-*.py 单测是否覆盖"为客观证据。

---

## 1. 需求复述

为 agate 补上 UI/UX 验收质量机制，解决「agate 保证工程质量但不保证 UX 质量」：

**RM-AG0007（UX 质量机制缺失）**：`ui_affected` 任务目前只被要求"UI 交互点有 E2E 功能测试"（state-machine.md:89-94），不要求视觉/交互质量；P2 plan-design-review 审架构不审视觉稿；P6 视觉验收看"渲染成功"无美观/易用维度。修复三层：
- ① **P1/P2 UX 需求基线**：键盘输入、显示内容、样式呈现三类 UX 写成 BDD 可测项 + 视觉验收项
- ② **P2 plan-design-review 增视觉/交互维度**：frontend 任务评审设计稿（布局/交互/视觉）
- ③ **P6 UI 任务强制双证据 + 视觉质量 checklist**：运行时证据 + 视觉证据，美观/易用维度核对

**RM-AG0004（视觉验收能力边界）**：视觉验收能力**运行时探测、不写死具体工具**。修复五项：
- ① ui_affected 任务 P1 **capability_requirements 必须声明 vision 能力三态**（available/supplementable/GAP）
- ② available 时 P6 **真实视觉分析**（本机 vision-engine 可用，别的项目可换——需求不写死工具名）
- ③ **subagent 能力自查**：派发时要求先自查能否调 vision，不能就报告降级，不静默假设
- ④ **输入态变化类用例人工复核**
- ⑤ **雷同截图降级待复核**（不只 WARNING）

**RM-AG0006（GUI 自动化框架评估）**：Windows 环境无 GUI 自动化框架，UI e2e 用 QTest offscreen 信号级模拟+截图。P2 设计时评估 WinAppDriver/AutoIt 是否补真实 GUI 交互路径，**可能产出"保持现状"结论**（调研非实测）。

**已定关键设计决策（2026-08-17，P1 不得推翻）**：
- UI 设计产物**并入 P2-design.md 独立节**（`ui_affected: true` 时 P2 必须含"UI 设计"节），不新增文件
- **architect 兼任 UI 设计**（复用现有角色，不新造 designer）
- P6 verifier 以 **UI 设计节为视觉验收依据**

## 2. 隐含需求识别

| # | 隐含需求 | 为什么必须 |
|---|---------|-----------|
| I1 | UI 设计节并入 P2-design.md → P2 gate 需检查该节存在 | 决策已定"并入独立节"，缺检查则 architect 可漏写，P6 验收无依据 |
| I2 | vision 三态声明要能**被 P1 gate 消费**（缺声明/非法值拦截） | RM-AG0004① 要求"必须声明"，没有 gate 校验就是软约束 |
| I3 | supplementable 传递需扩展：A3 规则（dispatch-protocol.md:1184-1202）须覆盖视觉能力语境的派发注入 | 现有规则讲"P6 需要 vision"，但未绑定 ui_affected 的 P1 声明来源 |
| I4 | subagent 自查要求写入 **dispatch-prompt 模板**，而非仅在角色文档 | 派发 prompt 不注入，subagent 不知道要自查 → 静默假设（RM-AG0004③ 失败模式） |
| I5 | 雷同截图降级需改 **check-p6-evidence.py 逻辑**（avg-hash 重复从 WARNING 改判定）+ 单测 | RM-AG0004⑤ 明说"不只 WARNING" |
| I6 | 输入态变化类用例人工复核 → 需在 verifier 角色文档 + P6 卡片定义"输入态变化"判定标准 | 无判据则 verifier 无法区分是否需要人工复核 |
| I7 | 影响面联动（64 处消费）→ P2 须产出**影响面核对清单**，P7 一致性检查按清单核对 | 用户强制要求：不愿一轮一轮来回改 |
| I8 | 新增 gate 检查的**单测遵循平台无关原则**（不可硬编码 Unix 假设） | 违反会让 Windows CI 冒烟挂掉（AGENTS.md 测试约定，TAG0009 gate 兜底） |
| I9 | 改动触发 SELF-GATE → commit 必须带 `self-gate-review:` | 触发文件包括 agate/*.md + scripts/**.py（AGENTS.md 清单） |
| I10 | 基线回归：823 pytest 全绿 + consistency 0 ERROR + 用例计数不漂移 | 协议本体增强的回归底线（P0-brief env_constraints/test_cmd） |
| I11 | RM-AG0006 评估不得宣称"已实测 Windows" | 环境无真实 Windows GUI（env_constraints），诚实边界约束 |
| I12 | 既有 P6 vision-helper/blocker_count/R1b 审计语义不破坏 | 兼容策略：新机制是增强现有约束，不改变既有 PASS/FAIL/blocker_count 二值判定 |

## 3. BDD 验收条件

> 验收方式统一约定：本任务 P6 的客观证据 = ① 对应协议文档/角色文件是否含该行为要求（read/grep）；② 对应 gate 脚本单测（pytest）是否覆盖并断言该行为。二者兼备才允许 PASS。以下 BDD 按阶段分组。

### P1 组 — UX 需求基线（RM-AG0007①）与能力识别（RM-AG0004①）

#### BDD-1: frontend 任务 P1 必须含 UX 类别 BDD
- Given 某任务的 P1-requirements.md 声明 domains 含 frontend（预示 P2 将标记 ui_affected）
- When 主 Agent 按协议要求检查该 P1 产出
- Then 协议明文规定该 P1 必须含至少一条 UX 类别 BDD（覆盖键盘可用性/显示内容正确性/样式呈现中至少一类用户可观测行为），且该要求被明文写入 analyst.md 与 P1 阶段卡片（缺失时 requirements-review 打回）
- 验收方式：读修改后 analyst.md + phase-cards/P1-requirements.md 含该要求

#### BDD-2: UX 类别 BDD 必须可二值判定且不绑定实现
- Given 前述 UX 类别 BDD 已写入 P1 基线
- When 检查该 BDD 的 Given/When/Then
- Then 其 Then 子句可二值判定（PASS/FAIL）、不含主观形容词（"可读/美观"）、不绑定 CSS 类名/组件名/工具名，且每条 BDD 独立编号
- 验收方式：analyst.md 的 BDD 反模式自检清单覆盖 UX 维度（读文档确认）

#### BDD-3: ui_affected 任务 P1 必须声明 vision 能力三态
- Given 某任务 P1-requirements.md 的 domains 含 frontend（或将产生 ui_affected 任务）
- When 主 Agent 运行 P1 gate 检查该文件的 capability_requirements
- Then 该文件必须含一条 vision 能力条目且 status ∈ {available, supplementable, GAP}，缺失声明或 status 为其它值 → P1 gate 拦截
- 验收方式：check-gate.py P1 新增该检查 + 对应单测（构造缺失/非法态 fixture 断言 exit 1）

### P2 组 — UI 设计节 / 评审维度 / GUI 评估 / 影响面（RM-AG0007①② + RM-AG0006 + 联动面）

#### BDD-4: ui_affected 任务 P2-design.md 必须含"UI 设计"节
- Given P2-design.md 声明 `ui_affected: true`
- When 主 Agent 运行 P2 gate
- Then 该文件必须含独立"UI 设计"节，节内至少覆盖布局、交互、视觉三类 checklist，缺失任一 → P2 gate 拦截
- 验收方式：check-gate.py P2 新增该节检查 + 单测（构造缺节 fixture 断言 exit 1）

#### BDD-5: UI 设计节由 architect 兼任产出（不新增 designer 角色）
- Given 前端任务进入 P2
- When 检查 architect 角色定义与 P2 产出规格
- Then architect.md 明文声明"ui_affected: true 时由 architect 兼任产出 UI 设计节"，且角色文件清单（role-system.md）不新增 designer 角色
- 验收方式：读 architect.md + role-system.md

#### BDD-6: plan-design-review 评审维度含视觉与交互设计
- Given frontend 任务触发 plan-design-review
- When 评审产出 P2-review-design.md
- Then plan-design-review.md 的评分维度表含"视觉设计"与"交互设计"维度（布局一致性/键盘可达/输入态反馈/样式呈现等），且每维度有 0-10 可判定评分项
- 验收方式：读 plan-design-review.md 维度表已扩容 + 维度名 grep 命中

#### BDD-7: P2 必须执行 Windows GUI 自动化框架评估（RM-AG0006）
- Given P2 设计涉及 Windows 平台 UI 交互验证路径
- When architect 产出 P2-design.md
- Then P2-design.md 必含"Windows GUI 自动化评估"小节，给出结论（补真实 GUI 路径 / 保持现状 + 理由），且结论不得包含"已实测 Windows"字样（基于调研）
- 验收方式：P2-design.md 含该节 + grep 无实测声称

#### BDD-8: P2-design.md 必须含影响面核对清单
- Given 本任务（TAG0006）影响面覆盖 64 处消费文件
- When architect 产出 P2-design.md
- Then P2-design.md 含"影响面核对清单"，列出全部受联动影响的文件/角色/阶段卡片/转移条件及对应同步动作
- 验收方式：P2-design.md 含影响面节 + 与 P1 影响面清单对齐核对

### P6 组 — 双证据 / 视觉质量 / 能力消费 / 降级链（RM-AG0007③ + RM-AG0004②③④⑤）

#### BDD-9: P6 UI 任务强制双证据 + 视觉质量 checklist（视觉证据按 vision 能力三态分档）
- Given P6 验收 ui_affected 任务
- When verifier 产出 P6-acceptance.md
- Then verifier 角色文档与 P6 卡片明文要求：每条 UI 类 PASS 必须同时含运行时证据（截图/行为日志）与视觉证据；视觉证据的形式按该任务 P1 声明的 vision 能力状态分档——available/supplementable 时须为 vision YAML 引用，GAP 时降级为"像素检测 + 人工复核记录"且不要求 vision YAML 引用；且 P6 验收须对照 P1 UX 类别 BDD / P2 UI 设计节核对视觉质量 checklist（美观/易用维度），不止"渲染成功"
- 验收方式：读 verifier.md + P6 卡片含该要求（含 vision 能力 GAP 分支的降级路径条文）

#### BDD-10: vision 能力 available 时 P6 必须真实视觉分析
- Given P1 声明 vision 能力 status: available
- When P6 verifier 验收 UI 类 BDD
- Then 协议明文要求 P6 必须执行真实视觉分析（截图 → 结构化描述 → 判定），不得仅用程序化指标（naturalWidth>0 / complete / HTTP 200）断言视觉 PASS；且该要求写入 P6 卡片 / verifier.md
- 验收方式：读 P6 卡片 + verifier.md 含该要求

#### BDD-11: vision 能力 supplementable 时派发 prompt 注入获取指引
- Given P1 声明 vision 能力 status: supplementable
- When 主 Agent 派发需要视觉能力的后续阶段
- Then 主 Agent 派发 prompt 必须按 A3 规则注入能力获取指引（如何调用视觉能力/角色），且 dispatch-prompt 模板含该指引的注入位置声明
- 验收方式：读 dispatch-protocol.md A3 节扩展 + dispatch-prompt.md 模板含指引节

#### BDD-12: 派发 prompt 强制 subagent 能力自查
- Given 主 Agent 派发可能涉及视觉能力的 subagent（如 P6 verifier / vision-analyst）
- When 派发 prompt 生成
- Then dispatch-prompt.md 模板必须含"先自查能否调用视觉能力，不能则明确报告并走降级路径、不静默假设"的自查要求
- 验收方式：读 dispatch-prompt.md 模板含自查要求

#### BDD-13: 输入态变化类用例人工复核
- Given P6 验收包含输入态变化类 UI 用例（用户输入导致界面状态变化）
- When verifier 判定该类 BDD 结果
- Then 协议明文要求该类 BDD 结论必须附带人工复核记录（复核人/复核时间/结论），不能仅由自动断言通过；判定标准写入 verifier.md / P6 卡片
- 验收方式：读 verifier.md + P6 卡片含该要求 + P6 产出含复核记录

#### BDD-14: 雷同截图降级待复核
- Given P6 验收中两条不同操作类 BDD 的截图视觉高度相似（average hash 相同）
- When 主 Agent 运行 check-p6-evidence.py
- Then 该情况被判定为"降级待复核"（触发人工复核要求或显式阻断，需在 P6-acceptance.md 记录复核结论），不能仅以 WARNING 放行
- 验收方式：check-p6-evidence.py 平均哈希判定逻辑改造 + 单测（构造两张同 content 不同文件名的截图 fixture，断言行为改变）

### 兼容/回归组

#### BDD-15: 基线回归不破坏既有 gate 语义
- Given 机制增强实施完成后
- When 运行全量 pytest + consistency 检查
- Then 既有 823 基线用例全绿 + 新增用例全绿、consistency 0 ERROR、count-tests 计数无漂移，既有 P6 vision-helper/blocker_count/R1b/二值 PASS/FAIL 语义保持不变
- 验收方式：pytest + consistency + count-tests 实跑

## 4. 待确认清单

[NO_NEED_CONFIRM]

P0-brief 与 2026-08-17 讨论已锁定全部方向（三层修复方向 / 五项能力边界修复 / GUI 评估调研定位 / UI 设计节并入 P2-design / architect 兼任 / P6 以 UI 设计节为依据），无真无方向的待决策项。

[SUGGEST: BDD-14 降级语义激进程度由 P2 定夺——建议"avg-hash 重复 → 强制人工复核记录+阻断条款"为默认，若 P2 评估成本过高可退化为"要求说明原因+复核记录"（仍非纯 WARNING）；主 Agent 可自行采纳倾向，涉及 gate 拦截强度变化属实现层不属业务方向，不阻塞]

## 5. 裁剪说明

`phases: [P1, P2, P3, P4, P5, P6, P7, P8]`——**零裁剪**，理由逐项：

- **P1 需求**（不可裁）：核心阶段，产出本基线
- **P2 设计**（不可裁）：本任务 1/3 改动在 P2（UI 设计节、评审维度、GUI 评估、影响面图），且需出架构方案
- **P3 TDD**：risk_level=medium 非 low，不可裁；且 gate 脚本改动（P1 新检查、P2 新检查、check-p6-evidence 降级）必须走先红后绿
- **P4 实现**（不可裁）：实际改动协议文档与脚本
- **P5 验证**（不可裁）：全量回归确认不破坏基线
- **P6 验收**（不可裁）：逐条对照本基线 15 条 BDD
- **P7 一致性**（不可裁）：`implicit_coupling: true`（64 处联动），仅 P7 能查联动遗漏
- **P8 发布**（不可裁）：agate 协议本体，走版本发布流程（badge/CHANGELOG/UPGRADING/tag）

## 6. 范围声明

- **packages**（frontmatter）：`agate-docs`（agate/*.md + assets/**/*.md + phase-cards/*.md）、`agate-scripts-py`（scripts/*.py）、`agate-tests`（tests/**）
- **domains**（frontmatter）：`frontend`（UI/UX 机制主体，触发 C8 映射 plan-design-review，恰合本任务改评审维度）、`backend`（gate 脚本/状态机逻辑）

## 7. 能力需求声明

```yaml
capability_requirements:
  - need: pytest-test-runner
    why: 机制验收的核心工具——gate 脚本单测（P3/P5/P6）基于 pytest（ANTEST basing 823 用例环境）
    available: ["本机 python3 + pytest（P0-brief env_constraints 确认）"]
    status: available

  - need: pyyaml
    why: capability_requirements/gate 脚本需读取 frontmatter（三态声明、UI 设计节标记）
    available: ["本机 python3 + pyyaml"]
    status: available

  - need: visual-analysis
    why: RM-AG0004 机制验收可选路径——available 分支若做端到端演示需真实视觉分析；本任务交付物为协议文档+脚本，无 UI 产物，P6 验收以脚本单测+文档内容一致性为主，不依赖真实截图
    available:
      - "agate 内置 vision-analyst 执行角色（P6 验收 UI 截图时首选，运行时探测）"
      - "视觉分析 skill（派发时按 RM-AG0004③ 先自查能否调用，本 worktree 环境有可用项，但不硬编码工具名）"
    status: supplementable

  - need: gui-e2e-framework-win
    why: RM-AG0006 涉及 Windows GUI 自动化框架评估——本任务仅做 P2 调研评估（读框架能力文档），不实跑
    available: []
    status: supplementable
    gap_note: "本环境无真实 Windows GUI，P2 评估基于文档调研（WinAppDriver/AutoIt 能力资料），结论不得宣称已实测；如需实测属运行环境限制，由 P2 评估小节明确标注"
```

> 说明：本任务自身无 UI 产出，`visual-analysis` 仅在"验证 available 分支机制行为"的可选端到端演示时使用，P6 验收硬依赖是脚本单测 + 文档内容，故标 supplementable 而非 GAP；`gui-e2e-framework-win` 的"评估"动作本身可完成（文档/网络调研，executor_env.network=full），运行验证缺失不阻断评估产出。

## 8. 影响面清单（同类扫描产物 — 强制）

> 扫描方式：对 worktree `agate/` 全树 `rg -l 'ui_affected|vision-analyst|plan-design-review|vision-helper'` 得 **45 个文件**（含 15 个测试/夹具文件）；P0-brief 所述"64 处文件"按 P2 设计时再次全量核对（含 docs/roadmap 等非协议文件）。改动一处必须同步全部联动点，P2 设计先画影响面图再动手。

### 8.1 协议文档（agate-docs）

| 文件 | 联动点 | 改动同步要求 |
|------|--------|------------|
| `state-machine.md` | P2/P3/P5/P6 的 ui_affected 转移条件（89-94 行 P2 声明+E2E 交互点、101 行 P5 E2E、323/326/330/333 行 gate 摘要） | 新增 P2"UI 设计节"检查与 P1 vision 三态检查的转移条件 |
| `rules/state-transitions.md` | 21 行 P2 四字段、25/32 行 UI 任务段 | 同步 UI 设计节 + vision 三态约束 |
| `WORKFLOW.md` | 286 行 P2 评审映射（frontend→plan-design-review）、290 行 P6 验收 | 同步评审维度与双证据描述 |
| `role-system.md` | 31/44/45/57 行角色-阶段映射 | 确认不新增 designer；vision-analyst 角色标注稳定 |
| `assets/execution-roles/analyst.md` | 168 行 frontend→P2 ui_affected；能力三态机制（78-104） | 新增 BDD-1/3 的 UX 维度要求与 vision 三态声明要求 |
| `assets/execution-roles/architect.md` | 39 行 ui_affected 字段、116 行三字段、191 行复杂交互 | 新增"UI 设计节"产出职责（BDD-4/5） |
| `assets/execution-roles/verifier.md` | 104-108 行 UI 追加约束、175-182 行 UI 处理流程 | 新增双证据+视觉质量 checklist+输入态人工复核（BDD-9/10/13） |
| `assets/execution-roles/test-designer.md` | 18/29/33/40 行 UI 任务用例要求、30-33 行 viewport 规范 | 确认不变（现有即可），仅核对联动 |
| `assets/execution-roles/vision-analyst.md` | 角色定位/B3/yaml 结构 | 新增能力自查要求（若不自行自查则派发提示覆盖） |
| `assets/review-roles/plan-design-review.md` | 13-21 行五维度 | 新增视觉/交互维度（BDD-6） |
| `assets/review-roles/design-review.md` | P4 后 UI 问题评审 | 核对是否复用视觉效果（联动不新增） |
| `assets/review-roles/requirements-review.md` | 38 行 capability_requirements 三态判断 | 新增 UX 维度 BDD 是否齐备的评审要点 |
| `phase-cards/P1-requirements.md` | 52-57 行 capability_requirements、109 行漏声明常见错误 | 新增 UX BDD 要求条文（BDD-1/2/3） |
| `phase-cards/P2-design.md` | 48/53/70/103/113/129/155/163/177 行 | 新增 UI 设计节字段 + gate 检查（BDD-4） |
| `phase-cards/P3-tdd.md` | 49 行 UI E2E 用例 | 核对（现有已含 UI 用例要求） |
| `phase-cards/P5-verification.md` | 40 行 E2E 命令、55/66/89/95 行 | 核对（现有已含 E2E 实跑要求） |
| `phase-cards/P6-acceptance.md` | 11-12/35/40 行派发、50-51 行证据、126-130 行 vision 绑定、164/169-172 行 | 新增双证据+视觉质量 checklist+输入态人工复核+雷同降级条文（BDD-9/10/13/14） |
| `phase-cards/README.md` | 15 行 P6 卡片索引 | 无实质改动（核对） |
| `dispatch-protocol.md` | 294/381 行 P2 字段、571 行 md5/avg-hash 规则、910/913/914 行 gate 表、950-957 行验证环境、1163-1204 行 A3 能力传递 | A3 扩展视觉能力语境 + P6 gate 表同步 RB 14 降级语义 |
| `assets/templates/dispatch-prompt.md` | 69 行能力注入、92 行评审角色、106 行 P3_e2e | 新增 subagent 能力自查要求段（BDD-12）+ supplementable 指引注入位（BDD-11） |
| `assets/templates/task-files.md` | 27/244/267/271/329/354-356 行 | P2/P6 模板同步 UI 设计节 + 双证据样例 |
| `LIMITATIONS.md` | 97-106 行局限7（视觉验收依赖外部基础设施） | 更新：三态识别+降级链缓解局限7 的程度描述 |
| `loop-orchestration.md` | 84 行示例 | 无实质改动（核对） |
| `scripts/README.md` | 114/122 行脚本索引、199-203 行 WARNING 说明 | 新增脚本/行为说明 |

### 8.2 Gate 脚本（agate-scripts-py）

| 脚本 | 联动点 | 改动要求 |
|------|--------|---------|
| `check-gate.py` | P1/P2/P6 三阶段检查 | 新增：P1 vision 三态声明检查（BDD-3）、P2 UI 设计节检查（BDD-4） |
| `check-p6-evidence.py` | 156-181 行 ui_affected 证据类型、261 行 avg-hash WARNING | avg-hash 雷同从 WARNING 改为降级待复核判定（BDD-14） |
| `check-p6-provenance.py` | 277-313 行 R1b vision YAML 审计 | 核对双证据规则（现有已含截图→vision 引用强约束，兼容保留） |
| `agate-md-field-get.py` | 175-176 行 ui_affected op | 新增 op（若 UI 设计节用 frontmatter 字段承载） |
| `agate-frontmatter-check.py` | 56-74 行 P2/P6 schema | 新增 P2 可选字段（UI 设计节标记） |
| `agate-vision-blocker.py` | 读取 blocker_count | 核对（兼容保留） |
| `agate-extract-context.py` | 126-133 行 P2 字段提取 | 核对（如需 UI 设计节标记则加字段） |
| `check-protocol-consistency.py` | 355 行 P5_e2e 模板、542 行 ui_affected 关键词 | 新增一致性规则（UI 设计节/vision 三态约束在文档族内一致） |
| `ci-gate-backstop.py` | 无直接命中 | 核对（若 P2 改动影响 gate 复跑则确认兼容） |

### 8.3 测试与夹具（agate-tests）

| 文件 | 联动点 | 改动要求 |
|------|--------|---------|
| `tests/unit/test_check_gate.py` | P1/P2 gate 检查现有用例 | 新增 P1 vision 三态 + P2 UI 设计节用例（BDD-3/4） |
| `tests/unit/test_check_p6_evidence.py` | 现有 avg-hash WARNING 用例 | 改/增雷同降级用例（BDD-14，TDD 先红） |
| `tests/unit/test_check_p6_provenance.py` | 240 行 vision blocker 用例 | 核对（兼容） |
| `tests/unit/test_agate_md_field_get.py` | ui_affected op 用例 | 新增 op 用例（若加字段） |
| `tests/unit/test_check_frontmatter.py` | P2/P6 schema 用例 | 新增 P2 可选字段用例 |
| `tests/unit/test_agate_vision_blocker.py` | 2 用例 | 核对（兼容） |
| `tests/unit/test_agate_extract_context.py` | P2 字段提取 | 核对（如需加字段则补用例） |
| `tests/unit/test_agate_capture_env_baseline.py` | 环境基线 | 核对（无关则不动） |
| `tests/integration/test_pre_commit_hook.py` | hook 集成 | 核对（若 pre-commit gate 行为变则补用例） |
| `tests/unit/test_dispatch_orchestration.py` | 派发编排/A3 | 补 supplementable 视觉语境注入用例（BDD-11） |
| `tests/fixtures/{full-task,ui-affected,vision-blocked,paused-task,high-risk}/P2-design.md` | 既有夹具 | 按最新 schema 核对/迁移（新增可选字段不破坏旧夹具） |
| `tests/README.md`（58 行 vision-blocker 计数表）+ `tests/scripts/count-tests.sh` | 用例计数 | 用例数变化后必须更新计数脚本期望值 |

### 8.4 外部联动（非协议文件，P8 阶段处理）

- `docs/roadmap*`：RM-AG0004/0006/0007 状态回写 done（P8）
- `CHANGELOG.md` / `README.md`（版本 badge） / `agate/UPGRADING.md`：版本发布三件套（P8）

## 9. 兼容策略（不破坏既有 gate 语义）

- **增量增强**：所有新检查只对"新声明"生效，不回溯改既有 task 数据；新增可空字段（UI 设计节标记）不破坏既有 P2 fixture schema（可选字段 presence 语义）
- **P6 双证据**：现有 check-p6-provenance.py R1b 已要求"截图 PASS → 必须含 vision YAML 引用"，新机制在此基础上叠加视觉质量 checklist 核对，不改变既有二值 PASS/FAIL 与 blocker_count=0 语义
- **雷同截图**：avg-hash 判定从 WARNING 升级为降级待复核，md5 逐字节去重硬阻断语义不变
- **回归底线**：823 基线用例必须全绿，新增用例只增不减（count-tests 同步）