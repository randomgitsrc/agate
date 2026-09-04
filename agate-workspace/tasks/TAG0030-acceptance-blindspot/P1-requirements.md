---
phase: P1
task_id: TAG0030
type: problems
parent: P0-brief.md
trace_id: TAG0030-P1-20260904
status: draft
created: 2026-09-04
agent: analyst
risk_level: high
ceremony: standard
phases:
- P1
- P2
- P3
- P4
- P5
- P6
- P7
- P8
packages:
- agate-phase-cards
- agate-assets-roles
- agate-assets-templates
domains:
- backend
---

# P1-requirements — TAG0030 验收盲区机制批（RM-AG0057 四类 + DEBT0024/25/26）

## 0. P0-brief 时效性质疑结论

已核对 P0-brief 时效性，无漂移。逐条复核：① `task` 目标方案（四 phase 文档面改造）仍成立——plan-design-review.md 仍为唯一未接形态体系的评审角色、P3/P6 卡仍无 post-test 残留检查、P1 卡/analyst 角色仍无人工体验验收节、派发模板仍无拆小默认指导（证据见「同类扫描」各锚点计数）；② `executor_env` 平台前提（worktree + merge 模式）无变化，TAG0028 完成 READY 属 Phase 4「核对 TAG0028 落地后的剩余缺口」的预期前提而非前提失效；③ `known_risks` 四条"已解决前提"（grep 断言审计 TDD / 0-10 格式保持 / 可表达子集边界 / DEBT0026 与 TAG0028 §4 边界）均已独立查证仍成立（见 §2 与 §8）。

## 1. 需求复述

把 P0-brief 的一句话任务（TPV0095 复盘 RM-AG0057 四类验收盲区 + TAG0027 复盘 DEBT0024/25/26）结构化重述为四 phase，均为**协议文档面改造**（改 worktree 的 `agate/`：phase-cards + assets/roles + assets/templates + tests/README），不涉及生产环境 `[PROD_NOT_TOUCHED]`：

- **Phase 1（测试副作用/环境还原 gate，RM-AG0057-①）**：创建型 E2E（建团队/条目）跑完不清理会累积污染共享环境，P6 全 PASS 时环境尚干净、残留验收后才暴露。修复 = ① P3 卡补「创建型测试清理钩子」要求（创建即注册、无条件删除、接受 200/204/404——afterEach 清理队列模式）；② P6 卡补 post-test 环境残留检查步骤（快照比对或清理钩子验证）；③ dispatch-context 模板补对应要求条目位。
- **Phase 2（P1 人工体验路径验收节，RM-AG0057-②）**：排除 seed/数据改动时 BDD 全用 fixture 验收，「用户按文档 seed 后页面应有内容」成隐性无人验路径（peekview DEBT0009：make debug-seed 后 Teams tab 空）。修复 = P1 卡 + analyst 角色补「人工体验验收」节——凡涉及用户可见页面且数据源（seed）影响其内容，强制补「Given seed 数据 → 页面有内容」BDD。
- **Phase 3（plan-design-review 形态驱动化，RM-AG0057-③）**：形态机制（ui_render_shape：layout/render_component/temporal_effects → ui_ux_dimensions 维度选择 → 按形态 checklist）已在 P1 analyst / P2 architect / gate（_gate_p1_ui_shape）全链落地，但评审角色文件 plan-design-review.md 未接形态体系（固定 7 维 + 一行条件启用，评审者拿布局维度评 Canvas 渲染任务或漏评）。修复 = ① 先读受评任务 ui_render_shape 再加载对应维度组评分细则（布局型 → 布局/交互/视觉三组；渲染组件型 → 渲染正确性/动效时序）；② 每个启用维度要求布局方案 ≥2 候选 + 权衡（架构级 candidate_count 下沉 UI 布局层）；③ 渲染组件型评审 checklist 对接 architect 渲染正确性 checklist。
- **Phase 4（视觉契约断言收录 + TAG0027 三连，RM-AG0057-④ + DEBT0024/25/26）**：①「dropdown ≥ trigger」类可量化协调性无 BDD 表达机制——收录**可表达子集**（E2E DOM 度量断言：宽度/高度/对齐/重叠/溢出），P2 视觉 checklist / P6 指南提及；② P3 测试夹具真实 gate 语义要求（DEBT0024，不 mock 假 exit）；③ 新 CHECK 上线前全量扫描存量流程（DEBT0025）；④ 大任务拆小派发默认指导（DEBT0026，补派发模板，不重复实现 TAG0028 §4 内部自主拆）。

## 2. 隐含需求识别

| 维度 | 隐含需求 | 为什么必须 |
|------|---------|-----------|
| 同类/影响面 | P3/P4 卡都只有测试前基线 capture-env-baseline；Phase 1 条文须**同时**落 P3 与 P4 卡（创建型测试在 P3 设计、P4 实现两处都会跑）；P6 是残留暴露最晚的兜底面（见「同类扫描」#1/#2） | 只改一处 = 复发反模式 |
| 数据 | 无生产数据面；协议文档条文 + grep 断言审计测试是"数据" | 断言审计是 TAG0027 批量改动 TDD 策略的锁定载体 |
| 前端 | 本任务**不产出业务 UI**；Phase 2 的「人工体验验收节」约束的是**下游 frontend 任务**（写进 P1 卡/analyst 角色使其强制）——本任务 domains 用 backend（TAG0024/26 先例，见 §3） | 约束 9：frontend 域声明须在正文声明理由 |
| 多端 | plan-design-review.md 的角色产出命名（P2-review-design.md）与 role-system.md 行 47 / review-mapping.md / P2 卡 / CHECK11 锚点耦合——形态驱动改造若动维度结构，须与「七维」描述同步（本 P1 将 role-system.md 行 47 + CHECK11 锚点列为**连带同步点**，P7 一致性检查捕获） | 改动评审角色文件须确认引用其维度清单的文件（F 扫描线索） |
| 边界 | ① plan-design-review 无形态声明时回落布局型默认（既有行为不变）；② 0-10 评分输出 + status 字段是门槛读的格式契约，只加形态分组内部逻辑不改语义（核心约束 2）；③ 视觉契约只收可量化 DOM 度量五类，不收主观视觉（核心约束 4，防「所有视觉都必须断言」误解） | 约束 2/4 硬边界 |
| 兼容 | ① SELF-GATE：改 phase-cards + plan-design-review + dispatch-context 模板 + analyst.md 触发（P0-brief env_constraints），commit message 须含 self-gate-review/skip——BDD 断言审计含一致性防线；② 改 P1/P6 卡等时新增叙述不得裸用 CHECK 14 平台词（本任务叙述文档面为 phase-cards + assets，非顶层叙述面，但 P4 落笔注意） | P0-brief env_constraints + 协议护栏 |
| 下游可执行性 | P1 把可 grep 锚文本作为 BDD 的可验证断言载体（约束 3）——P4 implementer 据此写断言审计测试；每条新增协议条文都要有可 grep 锁定词 | 约束 3 + DEBT closure「约定写明 X」转 grep 断言 |

范围锁定复核：本 P1 需求分析**未发现需超出 P0-brief 锁定范围**的改动——不重构形态声明机制本身（约束 2）、不改 check-gate.py 既有判据（_gate_p1_ui_shape 等，F 线索）、不实现清理钩子运行器（out-of-scope：只把模式收进协议卡/模板，不写具体项目 spec）、gate 命令解析器归 TAG0029 / check-gate 健壮性归 TAG0031（out-of-scope 确认保持）。若 P4 落笔时发现需触上述任一边界 → 停止报告主 Agent，不擅自扩范围（约束 1）。

## 3. 裁剪说明（phases 全覆盖声明）

- `risk_level: high`：跨 ≥7 个协议文件（P1/P3/P6 卡 + plan-design-review.md + dispatch-context.md + analyst.md + tests/README + UPGRADING）批量文档改动 + 评审角色行为变更 + SELF-GATE 触发 + 与 TAG0029/TAG0031 merge 并行（TAG0026 high + standard 先例）。
- `ceremony: standard`：文档面批量改动 + 评审角色行为变更，走完整仪式，不薄化（缺省 fail-closed 亦为 standard）。
- `phases: [P1, P2, P3, P4, P5, P6, P7, P8]`：全覆盖、无裁剪。逐阶段理由——P1 需求基线（本文件）；P2 不可裁（形态驱动落点需架构级候选 + 影响面梳理，虽本任务不改脚本仍须设计评审）；P3 保留（本任务采用**断言审计 TDD 策略**——约束 3：不为每处小改动单独 TDD，先写「grep 协议文件确认新增要求存在」的断言审计测试再批量改，测试落在 agate/tests/ 属 P3 交付）；P4 必含（卡/模板/角色落笔 + 断言审计测试代码 + 批量改动）；P5 保留（consistency 0 ERROR + 全量 pytest 回归防线）；P6 保留（验收逐条对照本文件 BDD）；P7 不可裁（packages 三包面跨文件一致性交叉核对）；P8 保留（协议本体随版本发布）。
- 跳过风险：无裁剪，无跳过阶段，不适用。
- **frontend 域说明**：`domains: [backend]` 不含 frontend——本任务不产出用户可见页面产线，只把约束「下游 frontend 任务的人工体验验收」写进协议卡/角色（Phase 2）；Phase 3 的形态驱动评审规则约束的是**下游 P2 评审角色行为**，其本身不是 UI 产线。故无视觉能力声明硬要求（P1 gate 的 vision 条目检查仅 domains 含 frontend 时触发）。

## 4. 能力需求声明

```yaml
capability_requirements: []
```

本任务为纯协议文档面改造（改 md 条文 + 跑 pytest/grep 断言审计），无浏览器行为/安全模型/外部系统/特殊视觉能力依赖。判断树走查：缺能力？否——pytest/grep 在当前环境可用（worktree 基线全绿，`count-tests.sh` 1436 用例实测）。缺运行环境？否——无服务/端口/数据库依赖，无 `verification_env`。

## 5. BDD 验收条件

> BDD 是「协议机制行为」视角（约束 8）：每条 Given/When/Then 以**读协议文件是否含该要求 + 断言审计测试是否覆盖 + check-*.py 是否校验**为可二值判定对象，不绑定实现函数。每条 BDD 下方「可验证载体」给出 P4 implementer 写断言审计测试用的可 grep 锚文本。

### A. Phase 1 — 测试副作用/环境还原 gate（RM-AG0057-①）

#### BDD-1: P3 卡声明创建型测试清理钩子要求
- Given 测试设计者读取 P3 卡片（phase-cards/P3-tdd.md）的产出规格或测试纪律节
- When 创建型测试（建条目/建资源类 E2E）纳入设计
- Then 卡片含「创建型测试须注册清理钩子，测试结束后无条件删除所建资源」的条文（含创建即注册、无条件删除语义），且该条文可由 grep 锚文本断言命中

可验证载体：P3 卡含「清理钩子」或「创建即注册」锚词；断言审计单测 grep 断言存在。

#### BDD-2: P4 卡同步声明创建型测试清理要求（同类补齐）
- Given 实现者读取 P4 卡片（phase-cards/P4-implementation.md）
- When P4 涉及创建型测试/夹具
- Then P4 卡同样含创建型测试清理要求锚词（与 P3 卡同源），杜绝「P3 写了 P4 没有」的只修一处复发

可验证载体：P4 卡含「清理钩子」或「创建即注册」锚词（P3/P4 同 grep 断言）。

#### BDD-3: 清理钩子规则含「无条件删除 + 接受 200/204/404」语义
- Given 协议规定创建型测试清理钩子的删除语义
- When 读取 P3 卡相关条文
- Then 条文写明「无条件删除（不因响应非 2xx 中止清理）+ 接受 200/204/404 三类响应为已清理」的 afterEach 清理队列模式，可由 grep 锚词断言

可验证载体：P3 卡含「200/204/404」与「无条件删除」锚词（afterEach 清理队列模式落点）。

#### BDD-4: P6 卡补 post-test 环境残留检查步骤
- Given 验收者（verifier）读取 P6 卡（phase-cards/P6-acceptance.md）的验收流程
- When P6 阶段对创建型 BDD 逐条验收
- Then P6 卡含「post-test 环境残留检查」步骤（快照比对或清理钩子验证，确认验收未污染共享环境），可由 grep 锚词断言

可验证载体：P6 卡含「残留检查」或「环境残留」或「post-test」锚词。

#### BDD-5: dispatch-context 模板声明环境清理/还原要求条目位
- Given 主 Agent 写 dispatch-context 派发指引（assets/templates/dispatch-context.md 的约束节）
- When 派发涉及创建型测试/验收的阶段
- Then 模板含环境清理/还原/残留检查的约束条目位（占位或示例句），可由 grep 锚词断言

可验证载体：dispatch-context.md 模板含「清理」或「残留」或「环境还原」锚词（约束区）。

#### BDD-6: 断言审计单测锁定 Phase 1 新增条文（回归防线）
- Given 协议测试套件（agate/tests/）
- When 全量 pytest 运行
- Then 断言审计单测 grep 断言 P3/P6 卡含 Phase 1 锚词（BDD-1/2/3/4 载体）及 dispatch-context 模板含 BDD-5 载体锚词（模板锚词同锁），条文一旦被后续改动删除测试转红

可验证载体：新增 `unit/` 或文档条文测试文件含对 P3/P6 卡路径 + 锚词及 dispatch-context.md 模板路径 + 「清理/残留/环境还原」锚词的 grep 断言，pytest 收集后用例数 ≥ 基线。

### B. Phase 2 — P1 人工体验路径验收节（RM-AG0057-②）

#### BDD-7: P1 卡声明「人工体验路径验收」节
- Given 需求分析师（analyst）读取 P1 卡（phase-cards/P1-requirements.md）
- When 任务涉及用户可见页面且页面内容受数据源（seed）影响
- Then P1 卡含「人工体验路径验收」节——声明此类任务强制补「Given seed 数据 → 页面有内容」BDD，可由 grep 锚词断言

可验证载体：P1 卡含「人工体验」锚词 + 「seed」锚词同现。

#### BDD-8: analyst 角色文件声明同一条人工体验验收要求
- Given analyst 读取自己的角色文件（assets/execution-roles/analyst.md）
- When 分析涉及 seed 数据驱动的用户可见页面任务
- Then 角色文件含人工体验验收要求（与 P1 卡同源），写明"数据源（seed）影响页面内容时必须补 seed 数据 BDD，不得只用 fixture 验收"，可由 grep 锚词断言

可验证载体：analyst.md 含「人工体验」+「seed」锚词。

#### BDD-9: 「Given seed 数据 → 页面有内容」成为 BDD 强制句式
- Given 涉及用户可见页面且数据源（seed）影响内容的任务的 P1 产出
- When requirements-review 评审该 P1 的 BDD 清单
- Then 若任务命中上述条件，其 BDD 清单须含「Given …seed… → 页面有内容/数据可见」型 BDD（P1 卡/analyst 条文强制，评审据此打回缺失项）

可验证载体：P1 卡条文含强制句式语义（「页面有内容」或「seed 数据」BDD 必含），断言审计锁定 P1 卡条文。

### C. Phase 3 — plan-design-review 形态驱动化（RM-AG0057-③）

#### BDD-10: plan-design-review 先读受评任务 ui_render_shape 再加载维度组
- Given plan-design-review 角色文件（assets/review-roles/plan-design-review.md）被读取用于 P2 评审
- When 受评任务 P1/P2 声明了渲染形态（ui_render_shape）
- Then 角色文件含「先读受评任务形态声明再加载对应维度组评分细则」的机制条文（形态驱动），可由 grep 锚词断言

可验证载体：plan-design-review.md 含「ui_render_shape」与「形态」锚词（当前 0 命中，见同类扫描 #6）。

#### BDD-11: 布局型形态加载布局/交互/视觉三组评分细则
- Given 受评任务为常规布局型（layout 或未声明回落默认）
- When plan-design-review 评分
- Then 角色文件定义布局型维度组 = 布局/交互/视觉三组（布局一致性、视觉设计、交互设计细节归组，保留 0-10 输出），可由 grep 锚词断言

可验证载体：plan-design-review.md 含「布局型」与三组维度名锚词（布局/交互/视觉）。

#### BDD-12: 渲染组件型形态加载渲染正确性/动效时序组并对接 architect checklist
- Given 受评任务声明渲染组件型（render_component）或时序特效型（temporal_effects）形态
- When plan-design-review 评分
- Then 角色文件定义渲染组件维度组（渲染正确性/动效时序），且评审 checklist 对接 architect 渲染正确性 checklist（锚点同源：渲染结果对比/帧时序/动效起止状态量化判据），可由 grep 锚词断言

可验证载体：plan-design-review.md 含「渲染正确性」「动效时序」「渲染组件」锚词 + 对接 architect checklist 的引用锚点（如「architect」渲染 checklist 交叉引用）。

#### BDD-13: 每个启用维度要求布局方案 ≥2 候选 + 权衡（candidate_count 下沉 UI 布局层）
- Given plan-design-review 评审 UI 布局相关维度（布局结构/交互行为/视觉呈现任一启用）
- When 受评 P2 的 UI 设计节未提供布局方案候选与权衡（如"行 vs 卡"只写一种）
- Then 角色文件含「每个启用维度要求布局方案 ≥2 候选 + 权衡说明」的评审要求（架构级 candidate_count 下沉 UI 布局层），评审据此打回无候选权衡的布局决策

可验证载体：plan-design-review.md 含「2 候选」或「候选」+「权衡」锚词（现 0 命中）。

#### BDD-14: 0-10 评分输出格式与 status 字段保持（门槛读 status 不变）
- Given plan-design-review 作为 P2 阶段门槛评审角色使用
- When 形态驱动化改造后评审
- Then 角色文件仍定义 0-10 评分输出 + 产出文件 Header 含 status 字段（approved/rejected/needs-revision 映射不变），可由 grep 锚词断言——保证 check-gate P2 读 status 判门槛的既有语义不破坏（核心约束 2）

可验证载体：plan-design-review.md 含「0-10」与「status」锚词（既有条文保留）。

#### BDD-15: 无形态声明时回落布局型默认（既有行为兼容）
- Given 受评任务未声明 ui_render_shape（存量任务缺省）
- When plan-design-review 评分
- Then 角色文件写明缺省回落布局型维度组（既有 7 维中的布局/视觉/交互评分路径行为不变），可由 grep 锚词断言

可验证载体：plan-design-review.md 含「缺省/未声明/默认 → 布局型」回落语义锚词。

### D. Phase 4 — 视觉契约断言收录 + DEBT0024/25/26

#### BDD-16: 视觉契约「可表达子集」定义收录（只收五类 DOM 度量）
- Given 协议文档描述 UI 视觉验收的表达机制
- When 涉及可量化协调性（如 dropdown 与 trigger 的几何关系）
- Then 协议含「视觉契约断言 = 可表达子集」定义：只收可量化 DOM 度量（宽度/高度/对齐/重叠/溢出），明确不收主观视觉判断（防「所有视觉都必须断言」误解），可由 grep 锚词断言

可验证载体：落点文档（P2 视觉 checklist 或 verifier/P6 指南所在文件）含「DOM 度量」或「对齐/重叠/溢出」五类锚词（现 0 命中，见同类扫描 #7）。

#### BDD-17: P2 视觉 checklist 提及可量化 DOM 度量断言
- Given architect 编写 P2 UI 设计节视觉 checklist
- When UI 布局含可量化几何协调性设计
- Then architect 角色文件或 P2 卡视觉 checklist 提及「可量化 DOM 度量断言（宽度/高度/对齐/重叠/溢出）可作为视觉质量可表达子集」的指引，可由 grep 锚词断言

可验证载体：architect.md（视觉 checklist 节）或 P2 卡含「DOM 度量」锚词。

#### BDD-18: P6/verifier 指南提及 DOM 度量断言为辅助证据形式
- Given verifier 验收含可量化协调性判据的 UI BDD
- When 选择证据形式（截图/断言记录）
- Then P6 卡或 verifier.md 指南提及「E2E DOM 度量断言可作为该判据的量化证据（截图之外的非截图证据）」的表述，可由 grep 锚词断言

可验证载体：verifier.md 或 P6 卡含「DOM 度量」或「getBoundingClientRect」类锚词（说明文字可含浏览器 API 举例）。

#### BDD-19: 协议测试设计约定写明「gate 消费方测试夹具走真实 gate 语义」（DEBT0024 closure）
- Given 测试设计者编写测试 gate 消费方的用例（check-gate.py 等 gate 脚本消费方）
- When 构造夹具让 gate 产出 exit 码
- Then 协议测试设计约定（tests/README「何时更新」或维护者约定文件）写明「gate 消费方测试夹具须走真实 gate 语义，构造真实前置产物让 check-gate 产 exit，而非 stub/mock 假 exit」，DEBT0024 closure_criteria 满足

可验证载体：tests/README.md 或约定文件含「真实 gate 语义」或「真实 check-gate」锚词（现 0 命中，见同类扫描 #8a）。

#### BDD-20: 开发约定写明「新增 CHECK 上线前先全量扫描存量」（DEBT0025 closure）
- Given 协议维护者新增 check-protocol-consistency.py 的 CHECK
- When CHECK 上线前
- Then 项目开发约定（AGENTS.md「改脚本的工作流」或等价权威源）写明「新增 CHECK 上线前先跑一次全量扫描确认存量零命中（或登记已知命中 + 分批清理计划），再合并启用」，DEBT0025 closure_criteria 满足

可验证载体：AGENTS.md 含「全量扫描」与「CHECK 上线」/「新增 CHECK」锚词（现 0 命中，见同类扫描 #8b）。

#### BDD-21: dispatch-context 模板派发指引含大任务拆小默认指导（DEBT0026 closure）
- Given 主 Agent 写 dispatch-context 派发指引（模板「约束」或「目标」区）
- When 任务体量 >5 文件或属大文档清理类（上下文重）
- Then 模板含「>5 文件/大文档类任务按体量评估拆小派发」的默认指导（外部拆小现状兜底，与 TAG0028 §4 内部自主拆互补不重复），DEBT0026 closure_criteria 满足，可由 grep 锚词断言

可验证载体：dispatch-context.md 模板含「拆小」或「>5 文件」或「体量」锚词（现 0 命中，见同类扫描 #8c；dispatch-prompt.md 行 49 已有产出/输入数分批，此为模板面补充默认指导，不删既有条目）。

## 6. 待确认清单

[NO_NEED_CONFIRM]——无阻塞待确认项：四 phase 范围由 P0-brief 锁定并经本文件 §2 范围复核无越界；形态驱动细节按核心约束 2「只加形态分组内部逻辑、不改 0-10 语义」方向明确，无业务方向分叉；可表达子集边界按核心约束 4「只收五类 DOM 度量、不收主观视觉」明确；DEBT0026 剩余缺口经 TAG0028 交付核对（dispatch-protocol §4.1 两条边界 + judge 例外 + 五模式并存声明已落地，见同类扫描 #8）确认 = 派发模板缺「>5 文件/大文档拆小默认指导」。均非"真无方向需人定夺"，不触发 NEED_CONFIRM。

## 7. 同类扫描结论

扫描动作：对 Phase 1-4 涉及的关键锚词在 worktree `agate/` 全树 grep（正确 ERE 交替口径），命中清单 + 逐条判定如下：

| # | 锚词 | 命中（文件数/面） | 本次处理/不处理 + 理由 |
|---|------|------------------|------------------------|
| 1 | `capture-env-baseline` | 12 文件 24 处（architect.md/UPGRADING/scripts/README/P4 卡/P3 卡/tests/README/脚本/测试） | **处理**：P3 卡 + P4 卡 step0 处补「创建型测试清理钩子」要求（BDD-1/2/3）。判定：capture-env-baseline 是**测试前失败基线**，与「测试后残留检查/清理钩子」互补不冲突——P3/P4 都只讲测试前基线，无测试后残留检查（缺口真实）。architect.md/scripts/README/UPGRADING 命中为工具机制说明（非阶段执行步骤语义），**不处理**。UPGRADING 迁移说明：本任务为无破坏性文档条文新增，需新增版本章节说明（见 §9 注，v0.68 节），**处理**（BDD 不单列，随 P4 版本章节落笔） |
| 2 | `afterEach`/`清理钩子`/`残留检查`/`环境还原`/`post-test` | phase-cards + assets **0 命中**；全树仅 state-transitions.md 行 54「READY 收尾检查：测试环境清理/开发环境还原」 | **处理**：Phase 1 条文新增（BDD-1~5）。state-transitions.md 命中为任务 READY 收尾口径（P8 后），非阶段 gate 步骤——**不处理**（不构成同一问题：残留暴露点在测试运行期而非 READY）。缺口真实确认 |
| 3 | `seed`/`人工体验`/`fixture 验收` | analyst.md + P1 卡 + P6 卡 **0 命中**；tests/ 命中均为 PNG 随机种子（测试夹具内部变量） | **处理**：Phase 2 条文新增（BDD-7/8/9）。tests/ 的 seed 为图像测试随机种子参数，与数据 seed 语义不同——**不处理**。缺口真实确认 |
| 4 | `candidate_count` | 23 文件（gate/脚本/architect/task-files/P2 卡/UPGRADING/大量测试） | **处理**：plan-design-review 评分细则内下沉 UI 布局层「≥2 候选 + 权衡」（BDD-13）。**不处理**：check-gate.py/agate_common.py/frontmatter-check/phases.yaml task_fields 等 gate 机器字段面（核心约束 2：不改既有判据；架构级 candidate_count 机制保持，仅评审角色新增 UI 层要求）；architect.md 等既有机制说明不重复 |
| 5 | `plan-design-review` | 11 文件（角色文件/review-mapping/role-system/WORKFLOW/P2 卡/AGENTS/dispatch-prompt/consistency 脚本/测试） | **处理**：角色文件本身形态驱动化（BDD-10~15）。**不处理**：review-mapping.md / role-system.md 行 47 / WORKFLOW.md / P2 卡引用的是角色名与产出文件名（P2-review-design.md），映射机制不变。**连带同步点**：role-system.md 行 47「七维：交互状态覆盖/…/渲染正确性与时序」描述与 CHECK11 锚点（consistency 脚本行 910-911：plan-design-review.md 须含「视觉设计/交互设计/渲染正确性与时序」）——P4 改动若使维度结构表述变化，须保持 CHECK11 三锚词仍在（BDD-12 载体），role-system 行 47 描述同步为形态驱动口径（P7 一致性检查核对） |
| 6 | `ui_render_shape`/`ui_ux_dimensions` | 20 文件（analyst/architect/verifier/test-designer/requirements-review/P1/P2/P6 卡/state-machine/state-transitions/task-files/UPGRADING/LIMITATIONS/check-gate/check-p6-evidence/字段工具/测试）——**plan-design-review.md 唯一评审角色未命中** | **处理**：plan-design-review.md 接入形态体系（BDD-10/11/12/15，Phase 3 核心证据）。其余 20 文件为已接形态链消费方——**不处理** |
| 7 | `视觉契约`/`DOM 度量`/`getBoundingClientRect` | **0 命中**（vision-analyst 现为被动截图翻译，协议无可量化 DOM 度量断言概念） | **处理**：Phase 4 收录为可表达子集（BDD-16/17/18）。vision-analyst.md / P6 卡 / verifier.md 为对接面——本 P1 将落点定为 P2 视觉 checklist + verifier/P6 指南（提及性），vision-analyst 被动翻译定位不变（不做概念改造，仅作可表达子集表述对接），具体落点文件由 P2 影响面梳理定，P7 核对 |
| 8 | `拆小`/`>5 文件`/`大文档`（DEBT0026 边界核对） | dispatch-context.md 模板 + dispatch-prompt.md 模板 + role-system + dispatch-protocol **0 命中「拆小默认指导」**；dispatch-prompt.md 行 49 已有「产出 >3/输入 >5 分批」硬规则 | **处理**：dispatch-context.md 模板补「>5 文件/大文档类任务按体量评估拆小」默认指导（BDD-21）。**不处理（边界保持，约束 5）**：TAG0028 已交付 role-system「子派发权限边界」节 + dispatch-protocol §4.1 两条硬边界 + judge 例外 + 与五模式并存声明（行 989-1003）——内部自主拆已落地；dispatch-prompt.md 行 49 的产出/输入数分批为既有硬规则不重复；本任务只补 dispatch-context 模板面的默认指导。DEBT0026 剩余缺口确认 = 派发模板缺默认指导 |
| 8a | DEBT0024 载体：tests/README「何时更新」节 | 无「真实 gate 语义」表述（现为「改 gate 规则 → 先加失败测试」） | **处理**：tests/README「何时更新」或等价维护者约定补「gate 消费方测试夹具走真实 gate 语义」（BDD-19） |
| 8b | DEBT0025 载体：AGENTS.md「改脚本的工作流」 | 无「新增 CHECK 上线前全量扫描」表述 | **处理**：AGENTS.md「改脚本的工作流」补「新增 CHECK 上线前先全量扫描存量」第 0 步（BDD-20）；UPGRADING 版章节随 P4 记录 |
| 9 | `_gate_p1_ui_shape`/check-gate.py 形态判据 | check-gate.py + 测试 | **不处理**：Phase 3 BDD 不得要求改动既有形态 gate 判据（约束 5/F 线索）——本 P1 BDD-10~15 均只约束评审角色文件条文，不含 gate 判据改动 |
| 10 | CHECK 14/15 平台词（护栏） | 改 phase-cards/assets 属非叙述面（固定结构），新增叙述段不得裸用平台词 | **不处理（P4 落笔注意）**：P4 批量改动时新增叙述遵守 CHECK 14/15（挂实现注记或避免平台词）；本文件 BDD 无平台词依赖 |

回归拦截声明：本任务同类问题（协议验收盲区）未来仍会新增，拦截手段 = ① BDD 断言审计单测（BDD-6：新增条文一经删除测试转红）→ P4 落笔并随全量 pytest 常驻；② P7 一致性检查按 packages 三包面（agate-phase-cards / agate-assets-roles / agate-assets-templates）跨文件核对条文同步。两手段已转成对应 BDD，非一次性存量修复。

## 8. BDD 反模式自检

- [x] Then 子句未绑定 CSS 类名/HTML 属性（断言对象为协议条文锚词 + gate/测试行为）
- [x] 无主观形容词（可读/美观/流畅——本任务非 UI 产线任务，无渲染正确性类 BDD；UX 类判据以 grep 锚词 + 测试覆盖为可量化锚点）
- [x] 每条 Given/When/Then 可二值判定（条文存在性 = grep 命中/未命中；测试覆盖 = pytest 红/绿）
- [x] Given/When 不绑定实现函数（载体锚词是协议文件关键词，非代码 API）
- [x] 每条仅一条 Given-When-Then
- [x] BDD 编号连续（BDD-1 ~ BDD-21，无跳号）
- [x] 覆盖正常流/异常流/边界流分组（A 组机制补强 / B 组强制句式 / C 组评审行为 / D 组概念收录 + closure），每 phase 独立编号

## 9. 下游落笔注意（非 BDD，供 P2/P4 参考）

- P2 影响面梳理须确认 Phase 4 视觉契约落点文件（P2 视觉 checklist 在 architect.md 或 P2 卡、P6/verifier 指南在 verifier.md 或 P6 卡——以「提及可表达子集」为度，不新造机制）；Phase 3 对接点（architect.md 渲染正确性 checklist 行 93-99）为评审细则引用源，不改动。
- P4 批量改动完成后：① 跑 worktree `check-protocol-consistency.py --strict-errors-only` 确认 0 ERROR（尤其 CHECK11 的 plan-design-review 锚点行 910-911 保持）；② UPGRADING.md 新增 v0.68 版本章节（含无破坏性声明 + 新条文摘要）；③ commit message 含 `self-gate-review:`（SELF-GATE 触发面）；④ CHANGELOG [Unreleased] 同步；⑤ 若改 plan-design-review 维度结构表述，同步 role-system.md 行 47「七维」描述为形态驱动口径（连带同步点）。
