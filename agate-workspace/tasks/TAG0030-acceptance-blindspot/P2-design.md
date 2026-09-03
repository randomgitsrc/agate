---
phase: P2
task_id: TAG0030
type: design
parent: P1-requirements.md
trace_id: TAG0030-P2-20260904
status: draft
created: 2026-09-04
agent: architect
candidate_count: 2
packages: [agate-phase-cards, agate-assets-roles, agate-assets-templates]
domains: [backend]
ui_affected: false
dispatch_plan: {mode: static-batch, parallel_limit: 3, batches: [{id: phase-cards, complexity: medium}, {id: assets-roles, complexity: medium}, {id: templates-tests-meta, complexity: low}]}
---

# P2-design — TAG0030 验收盲区机制批（RM-AG0057 四类 + DEBT0024/25/26）

> 纯协议文档面改造，不涉及生产环境 `[PROD_NOT_TOUCHED]`。本任务不产出业务 UI，
> `ui_affected: false`——Phase 2/3 条文约束的是**下游 frontend 任务**行为，不是本任务产线。

## 0. 影响面梳理（候选方案之前，带 grep 证据）

### 0.1 改什么（Modify：文件 + 落笔位 + 关联 BDD）

| # | 文件 | 落笔位 | 关联 BDD | 改动一句话 |
|---|------|--------|----------|-----------|
| 1 | `agate/phase-cards/P3-tdd.md` | step0「测试前基线」之后补「创建型测试清理钩子」要求段 | BDD-1/3 | 创建即注册 + 无条件删除 + 接受 200/204/404（afterEach 清理队列模式），锚词「清理钩子/创建即注册/无条件删除/200/204/404」 |
| 2 | `agate/phase-cards/P4-implementation.md` | step0 基线行（行 8）之后镜像补同要求段 | BDD-2 | 与 P3 卡同源同锚词，杜绝只修一处复发 |
| 3 | `agate/phase-cards/P6-acceptance.md` | 验收流程补 post-test 环境残留检查步骤 | BDD-4 | 快照比对或清理钩子验证二选一，锚词「残留检查/post-test」 |
| 4 | `agate/phase-cards/P1-requirements.md` | 产出规格补「人工体验路径验收」节 | BDD-7/9 | seed 影响页面内容 → 强制补「Given seed 数据 → 页面有内容」BDD，锚词「人工体验/seed」 |
| 5 | `agate/assets/execution-roles/analyst.md` | 输出节补同源要求句 | BDD-8 | 与 P1 卡同源，锚词「人工体验/seed」 |
| 6 | `agate/assets/review-roles/plan-design-review.md` | 「评分维度」节改形态分派头 + 维度组 + ≥2 候选要求 | BDD-10~15 | 先读 `ui_render_shape` 再加载维度组；布局型三组 / 渲染组件型渲染正确性 + 动效时序并交叉引用 architect checklist；0-10 输出 + status 映射原样保留；无声明回落布局型 |
| 7 | `agate/assets/execution-roles/architect.md` | 视觉 checklist 头部定义视觉契约 + 提及 DOM 度量 | BDD-16/17 | 「视觉契约断言 = 可表达子集（宽度/高度/对齐/重叠/溢出五类 DOM 度量，不收主观视觉）」单源定义 |
| 8 | `agate/assets/execution-roles/verifier.md` | 证据形式指南补 DOM 度量量化证据句 | BDD-18 | E2E DOM 度量断言可作截图之外的非截图量化证据（举例 getBoundingClientRect 置于代码围栏/示例句） |
| 9 | `agate/assets/templates/dispatch-context.md` | 约束节补环境清理/还原条目位 + 拆小默认指导条目位 | BDD-5/21 | 锚词「清理/残留/环境还原」+「拆小/>5 文件/体量」 |
| 10 | `agate/tests/README.md` | 「何时更新」节补真实 gate 语义句 | BDD-19 | 锚词「真实 gate 语义」 |
| 11 | `AGENTS.md`（worktree 根） | 「改脚本的工作流」节首补第 0 步 | BDD-20 | 锚词「全量扫描/新增 CHECK」 |
| 12 | `agate/role-system.md` 行 47 | 七维描述同步形态驱动口径 | 连带同步点 | 保留维度名，改扁平罗列为形态分组表述（结论见 §5） |
| 13 | `agate/UPGRADING.md` + `CHANGELOG.md` | 新增 v0.68 版本章节 + Unreleased 同步 | P1 §9 | 无破坏性声明 + 新条文摘要 |
| 14 | `agate/tests/unit/test_tag0030_assertions.py`（新建） | grep 断言审计单测 | BDD-6 | 锁定 #1~13 全部锚词，条文被删即转红 |

grep 证据（现状 0 命中确认缺口真实）：`清理钩子/残留检查/post-test` 在 phase-cards + assets 0 命中；
`人工体验` 在 analyst.md + P1 卡 0 命中；`ui_render_shape` 在 plan-design-review.md 0 命中；
`DOM 度量/视觉契约` 全树 0 命中；`真实 gate 语义` 在 tests/README 0 命中；
`全量扫描` 在 AGENTS.md 0 命中；`拆小` 默认指导在 dispatch-context 模板 0 命中。

### 0.2 不改什么（Not Modify：看起来该改但不改 + 理由）

| # | 文件/范围 | 不改的理由 |
|---|----------|-----------|
| 1 | `agate/scripts/check-gate.py` 既有判据（含 `_gate_p1_ui_shape`） | P0 out-of-scope + P1 约束 1；BDD-10~15 只约束评审角色条文 |
| 2 | `agate/scripts/check-protocol-consistency.py`（CHECK11/14/15 口径） | 不新增 CHECK；BDD-6 审计载体是 `agate/tests/` 单测而非新 CHECK |
| 3 | `agate/rules/` 全树 | 本任务无数据面改动；CHECK15 无触达（最小验证已确认） |
| 4 | `agate/rules/review-mapping.md` + `WORKFLOW.md` + P2 卡引用 | 只引用角色名与产出文件名，映射机制不变 |
| 5 | `agate/assets/execution-roles/vision-analyst.md` | 被动截图翻译定位不变，仅作可表达子集表述对接，不做概念改造 |
| 6 | `agate/phase-cards/P6-acceptance.md` 证据形态机制 | 帧序列/时序截图/渲染输出对比机制已完备，BDD-18 只需 verifier.md 提及一句，不重复定义 |
| 7 | `plan-design-review.md` 0-10 权重语义 + status 映射 | P0 out-of-scope（只加形态分组内部逻辑）；门槛读 status 契约冻结 |
| 8 | 具体项目 E2E spec（如 peekview teams-page.spec.ts） | P0 out-of-scope：只把 afterEach 清理队列模式收进协议卡/模板 |
| 9 | `dispatch-prompt.md` 行 49 既有分批硬规则 | BDD-21 只补 dispatch-context 模板面默认指导，不删不重复既有条目 |
| 10 | `state-transitions.md` 行 54 READY 收尾口径 | P8 后收尾语义，与测试运行期残留检查非同一问题 |

### 0.3 风险在哪（Risk + 缓解）

| # | 风险 | 缓解 |
|---|------|------|
| 1 | 改 plan-design-review 维度表述误删 CHECK11 三锚词（「视觉设计/交互设计/渲染正确性与时序」，consistency 行 910-911 白名单）→ consistency ERROR | P4 落笔 checklist 逐锚词核对；P5 `P5_consistency` 独立 key 常驻校验；BDD-6 审计单测同锁三锚词 |
| 2 | 视觉契约三处重复定义未来漂移（若选分散式） | 选方案 A 单源定义（§1），verifier.md/P6 侧只交叉引用一句话 |
| 3 | 评审角色行为变更破坏 0-10/status 门槛契约 | 方案 A 只加形态分派头，评分行原文保留；P3 审计单测锁定「0-10」+「status」锚词（BDD-14） |
| 4 | 四 phase 同批改卡触发多轮 consistency/pytest 回归 | BDD-6 断言审计单测一次锁定（TAG0027 批量 TDD 策略），P5 分片回归独立 key |
| 5 | 与 TAG0029/TAG0031 三路并行 merge 冲突 | 文件域不重叠（本任务面见 §0.1；解析器归 TAG0029、check-gate 健壮性归 TAG0031）；冲突即停报主 Agent |
| 6 | 平台词护栏（CHECK14/15）误触 | CHECK14 扫描面仅 `agate/*.md` 顶层，本任务改动面（phase-cards/assets）不在扫描面内；落笔仍避免裸平台词，新增长句优先用「subagent/派发」表述，示例代码一律进围栏 |

## 1. 候选方案

### 方案 A：单源提及式（推荐）

- 视觉契约定义**单源**落在 `architect.md` 视觉 checklist 头部（BDD-16 定义 + BDD-17 提及同一次落笔）；
  `verifier.md`（BDD-18）与 P6 侧只写一句话交叉引用，不重复定义。
- `plan-design-review.md` 做**最小改写**：保留既有七维评分行原文，加「形态分派头」
  （先读受评任务 `ui_render_shape` → 加载维度组）+ 每启用维度「≥2 布局候选 + 权衡」评审要求句
  （BDD-13）+ 渲染组件组对接 architect 渲染 checklist 的引用锚点（BDD-12）。
- 优点：单源无漂移；CHECK11 三锚词与 0-10/status 行零移动，门槛契约风险最低；review diff 最小。
- 风险/代价：P2 卡读者需跳转 architect.md 看完整定义（接受：P2 卡本就不复述角色文件细节）。
- 工作量：中（1 个评审文件节改写 + 12 处条文增补 + 1 个审计单测文件）。

### 方案 B：分散定义式（备选，不选）

- 视觉契约在 P2 卡 + `architect.md` + `verifier.md` 三处各写完整定义；
  `plan-design-review.md` 重写维度体系为形态分组评分表（替换既有七维行）。
- 优点：各角色文件自包含，单文件可读性最好；在某些维度上比方案 A 更“彻底”。
- 风险/代价：三处定义未来漂移需 P7 每次三方核对；大改维度表极易误删 CHECK11 三锚词或
  0-10/status 行（§0.3 风险 1/3 放大）；评审 diff 大，review 打回概率高。
- 工作量：中高。

### 选择理由

选方案 A：本任务是**门槛契约冻结 + 白名单锚点强耦合**场景（CHECK11 三锚词、0-10/status 门槛），
最小改写是风险主导的最优解；方案 B 在可读性单维度更好，但以放大 §0.3 风险 1/2/3 为代价，
且 YAGNI——P1 只要求「提及可表达子集」，不需要三处完整定义。稻草人自检：方案 B 并非陪衬，
它在自包含性上真实优于 A，只是在本任务约束下总账为负。

## 2. 改动详述（按 P1 四 phase）

### Phase 1（BDD-1~6）：测试副作用/环境还原 gate

- P3 卡 step0 后新增段：创建型测试须注册清理钩子——创建即注册、测试结束无条件删除
  （不因响应非 2xx 中止）、删除接受 200/204/404 为已清理（afterEach 清理队列模式）。
- P4 卡 step0（行 8）后镜像同段同锚词。
- P6 卡验收流程新增 post-test 环境残留检查步骤：快照比对或清理钩子验证二选一。
- dispatch-context 模板约束节新增环境清理/还原/残留检查条目位。
- 新建 `agate/tests/unit/test_tag0030_assertions.py`：grep 断言 P3/P4/P6 卡 + 模板锚词（BDD-6）。

### Phase 2（BDD-7~9）：P1 人工体验路径验收节

- P1 卡产出规格新增「人工体验路径验收」节：用户可见页面 + 内容受 seed 影响 →
  强制补「Given seed 数据 → 页面有内容」BDD。
- `analyst.md` 输出节加同源一句：不得只用 fixture 验收。

### Phase 3（BDD-10~15）：plan-design-review 形态驱动化

- 角色文件「评分维度」节首加形态分派头：读受评任务 `ui_render_shape` →
  布局型（layout 或未声明缺省）加载布局/交互/视觉三组；渲染组件型/时序特效型加载
  渲染正确性/动效时序组并引用 architect 渲染正确性 checklist。
- 每启用维度加评审要求句：布局方案须 ≥2 候选 + 权衡说明，否则打回。
- 既有 0-10 分值行与门槛 status 映射行**原文保留**。

### Phase 4（BDD-16~21 + DEBT 三连）

- BDD-16/17：`architect.md` 视觉 checklist 头部单源定义 + 提及（落点 pin 定见 §4）。
- BDD-18：`verifier.md` 加 DOM 度量量化证据句。
- BDD-19：`tests/README.md`「何时更新」节加真实 gate 语义句。
- BDD-20：`AGENTS.md`「改脚本的工作流」节首加第 0 步（新增 CHECK 上线前全量扫描存量）。
- BDD-21：dispatch-context 模板加「>5 文件/大文档按体量评估拆小」默认指导。

## 3. BDD-16 落点 pin 定（review 打回项 3 落实）

P1 保留「或」表述，P2 pin 定如下（以「提及可表达子集」为度，不新造机制）：

- BDD-16 定义落点：`agate/assets/execution-roles/architect.md` 视觉 checklist 头部。
  理由：与 BDD-17（P2 视觉 checklist 提及）同文件，一次落笔满足两条，天然单源。
- BDD-18 落点：`agate/assets/execution-roles/verifier.md` 证据形式指南。
  理由：BDD-18 约束的是 verifier 选证据行为，verifier.md 是其直接行为文件；
  P6 卡证据形态机制已完备，不重复。

## 4. CHECK11/role-system 连带同步结论：Modify（选边完成）

- `agate/role-system.md` 行 47 列 **Modify**：plan-design-review 改形态分派后，
  「七维：交互状态覆盖/交互设计细节/可访问性/移动端/组件完整性/AI Slop/视觉设计/
  渲染正确性与时序」扁平罗列与新形态分组表述不一致，必须同步为形态驱动口径
  （布局型三组 / 渲染组件型渲染正确性 + 动效时序），维度名原文保留。
- CHECK11 三锚词保持方案：`plan-design-review.md` 内「视觉设计/交互设计/渲染正确性与时序」
  三词只增不删（分派头复用原词），consistency 行 910-911 白名单持续命中——最小验证已确认三词现存，
  P4 落笔禁动此三行（见 files_to_read why 标注）。

## 5. gate_commands（P2 固化，后续阶段只读执行）

```yaml
gate_commands:
  P3: "python3 -m pytest agate/tests/unit/test_tag0030_assertions.py -q --tb=short"
  P3_formatter: "pytest.sh"
  P3_timeout_seconds: 120
  P5_unit: "python3 -m pytest agate/tests/unit/ -q --tb=no -n auto"
  P5_unit_timeout_seconds: 300
  P5_regression: "python3 -m pytest agate/tests/regression/ -q --tb=no -n auto"
  P5_regression_timeout_seconds: 300
  P5_integration: "python3 -m pytest agate/tests/integration/ -q --tb=no -n auto"
  P5_integration_timeout_seconds: 600
  P5_consistency: "python3 agate/scripts/check-protocol-consistency.py --strict-errors-only"
  P5_consistency_timeout_seconds: 120
  P5_shellcheck: "shellcheck agate/scripts/pre-commit-gate.sh agate/scripts/commit-msg-self-gate.sh agate/scripts/pre-push-gate.sh"
  P5_shellcheck_timeout_seconds: 60
  P5_count: "bash agate/tests/scripts/count-tests.sh"
  P5_count_timeout_seconds: 120
```

说明：P3 文件名由本设计 pin 定（`test_tag0030_assertions.py`），P3 test-designer 按此文件名落笔，
不得另起文件名（gate 已固化）；各 key 独立命令，无 `&&` 链路；P3 走 `AGATE_TDD_TIMEOUT` 机制，
`timeout_seconds` 只服务 P5/non-P3 key（P3 key 的值仅作执行方 shell 超时参考）。

## 6. files_to_read（只列 P4 必读，带行号与批次归属）

```yaml
files_to_read:
  - path: agate/phase-cards/P3-tdd.md
    why: "[phase-cards 批] BDD-1/3 落笔位 step0（测试前基线行之后）；只读 step0 周边"
  - path: agate/phase-cards/P4-implementation.md:1-40
    why: "[phase-cards 批] BDD-2 落笔位 step0（行 8 之后镜像补段）"
  - path: agate/phase-cards/P6-acceptance.md
    why: "[phase-cards 批] BDD-4 落笔位验收流程节；证据形态机制只读不动"
  - path: agate/phase-cards/P1-requirements.md
    why: "[phase-cards 批] BDD-7/9 落笔位产出规格节；人工体验节插入点"
  - path: agate/assets/review-roles/plan-design-review.md
    why: "[assets-roles 批] BDD-10~15 全量改写对象；CHECK11 三锚词 + 0-10/status 行禁动"
  - path: agate/assets/execution-roles/architect.md
    why: "[assets-roles 批] BDD-16/17 落笔位视觉 checklist 头部；BDD-12 引用源渲染 checklist 行 93-99 只读不动"
  - path: agate/assets/execution-roles/analyst.md
    why: "[assets-roles 批] BDD-8 落笔位输出节"
  - path: agate/assets/execution-roles/verifier.md:70-95
    why: "[assets-roles 批] BDD-18 落笔位证据形式指南（DOM 结构验证节周边）"
  - path: agate/role-system.md:40-52
    why: "[assets-roles 批] 行 47 连带同步改写位"
  - path: agate/assets/templates/dispatch-context.md
    why: "[templates-tests-meta 批] BDD-5/21 落笔位约束节（61 行全读）"
  - path: agate/tests/README.md:114-121
    why: "[templates-tests-meta 批] BDD-19 落笔位何时更新节"
  - path: AGENTS.md:17-24
    why: "[templates-tests-meta 批] BDD-20 落笔位改脚本的工作流节首"
  - path: agate/UPGRADING.md
    why: "[templates-tests-meta 批] P1 §9：新增 v0.68 版本章节；CHANGELOG Unreleased 同步只读本文件惯例"
```

## 7. env_constraints

```yaml
env_constraints:
  debug_env: "沿用 P0-brief：系统 python 跑 pytest/pyyaml；ruff 用 ~/.venvs/agate-dev/bin/ruff；编排/派发类工具用 ~/.agate 稳定版；consistency 用 worktree 自己的脚本"
  isolation_check: "纯协议文档面改造，无服务/端口/数据库依赖；P5 gate 即隔离 validation（consistency 0 ERROR + 全量 pytest），无需独立隔离探针"
```

`ui_affected: false` 理由：本任务不产出用户可见页面，只把约束下游 frontend 任务的条文写进
协议卡/角色；无 E2E 交互点，故无 `P5_e2e` key。

## 8. minimal_validation

```yaml
minimal_validation:
  assumption: "拟新增 21 个中文锚词不触发 CHECK14/15 平台词护栏；CHECK11 三锚词保持方案可行；P2 不碰 rules/ 故 CHECK15 无触达"
  method: "grep 级最小验证：平台词正则对 21 个锚词逐词扫描 + plan-design-review.md 三锚词存在性确认"
  result: "confirmed"
  note: "21 词零冲突（含 ui_render_shape：下划线属词字符，天然不命中 task 词边界；200/204/404 为数字斜杠无冲突）；CHECK11 三锚词 + 0-10 + status 五词俱在；CHECK14 扫描面仅 agate/*.md 顶层，本任务改动面在其外。纯文档 + pytest/grep 改造，无浏览器/外部系统依赖"
```

## 9. 实现完成的标志（供 P3/P5/P6 使用）

1. §0.1 #1~13 全部落笔，锚词可 grep 命中（BDD-1~5/7~21 条文存在性）。
2. `test_tag0030_assertions.py` 新建并全绿；删任一条文即转红（BDD-6，P3 红灯确认）。
3. worktree `check-protocol-consistency.py --strict-errors-only` 0 ERROR（尤其 CHECK11 三锚词保持）。
4. 全量 pytest（unit/regression/integration 分片）回退零失败；用例数较基线 +N（N = 新增审计用例数）。
5. `UPGRADING.md` v0.68 章节 + `CHANGELOG.md` Unreleased 同步；commit message 含 `self-gate-review:`。
6. P7 按 packages 三包面交叉核对条文同步；role-system 行 47 口径与 plan-design-review 分派头一致。
