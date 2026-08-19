---
phase: P2
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0016
role: architect
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

把 P1-requirements.md 的 19 条 BDD（RM-AG0025 协议文档去重 8 条 + RM-AG0026 测试证据引用 8 条 +
回归/平台 2 条 + 防复发落地入口 1 条）转成可实现的技术方案，产出
{AGATE_WORKSPACE}/tasks/TAG0016-protocol-hygiene/P2-design.md。

本任务是**协议自身**的改造：改动对象是 `agate/` 目录下的 Markdown 协议文档 + 2 个 Python gate
脚本（`check-protocol-consistency.py` 新增 CHECK / `check-p6-provenance.py` 新增审计），不是产品
代码，没有前端/UI，`ui_affected` 必为 `false`。

### 约束

1. **不是所有 BDD 都是 design_trivial**。BDD-9/BDD-10（防复发 CHECK 的具体检测算法，如何区分
   "内容真复制"与"合法引用/摘要"）和 BDD-12（P5 通过 commit hash 记录在哪、如何设计 schema
   变更）是需要真实候选方案权衡的设计决策，不能只填 1 个候选方案敷衍了事——按 architect.md
   「方案探索方法论」，这两处属于"设计模式"或"系统架构"场景类型，先列 2-3 个候选思路（如
   BDD-9 的检测算法：整段文本相似度 vs 结构化"权威表格标记"扫描 vs 关键词+行数阈值），再选一个
   深入，不能是稻草人陪衬。BDD-1~8/13~19 若确实是常规改动（沿用既有"权威源+指针"模式的机械应用）
   可以走 `follows_existing_pattern`（参照 3.4 节已验证的正确模式：`dispatch-protocol.md`/
   `state-machine.md`/`git-integration.md` 对 WORKFLOW.md Pre-commit 清单的指针写法）+ 1 个候选，
   但要在 P2-design.md 里显式说明"本方案的哪部分走 follows_existing_pattern、哪部分需要真实候选
   权衡"，不能笼统一刀切。
2. **`ui_affected: false`**（无 UI/渲染改动），不需要 UI 设计节。
3. **`candidate_count` 与正文候选方案数必须一致**——如果整体方案里有多个子决策点各自有候选，
   按 architect.md 惯例，`candidate_count` 反映的是"整体方案"层面的候选数（如"方案 A：CHECK 12
   用整段相似度检测 + 一次性迁移所有重复内容"vs"方案 B：CHECK 12 用结构化标记扫描 + 分批迁移，
   高风险重复项优先"这种整体路线级别的候选），不是每条 BDD 各自数一遍。
4. **影响面梳理必须建立在 P1 已完成的"同类扫描"结论之上**（P1-requirements.md 第 3 节，含 6 类
   判定结论 + 3.8 结论汇总表），不要重新做一遍全仓 grep——P1 已经给出命中数量、文件清单、逐条
   处理判定，P2 在这个基础上做**候选方案级**的细化（具体改哪个文件的哪个小节、迁移后的指针句
   长什么样、CHECK 12 的检测算法伪代码级细化）。
5. **批次设计（`dispatch_plan`）大概率需要**：本任务改动面覆盖 ≥5 个协议文档（WORKFLOW.md /
   dispatch-protocol.md / platform-notes.md / state-machine.md / rules/state-transitions.md /
   8 张 phase-cards）+ 2 个 gate 脚本改动（各自需要 TDD 先红后绿）+ 至少 1 处 P8 脚本调整 +
   xdist CI 配置改动，risk_level=high。按 architect.md「批次设计」硬规则，若你的工作量评估任一
   维度落 high，必须设计拆批（不允许单发）。RM-AG0025（协议文档去重 + CHECK 12）与
   RM-AG0026（跨阶段证据引用机制 + P8 精简 + xdist）在文件层面基本不重叠（前者动 Markdown 协议文
   档为主，后者动 2 个 Python gate 脚本 + CI 配置为主），是天然的批次边界候选，但具体怎么拆、拆
   几批、每批 complexity 如何，由你按工作量评估决定，不是我替你决定。
6. **回归底线是硬约束**：`gate_commands.P5` 必须能验证 916 pytest 全绿这条底线不被打破（新增测试
   只增不减用例总数），`gate_commands` 里要把 consistency 脚本的 `--strict` 检查也纳入（P0-brief
   env_constraints.test_cmd 已给出三条验证命令：pytest / check-protocol-consistency.py --strict /
   count-tests.sh）。
7. **TDD 策略**：P1 隐含需求节已建议"批量机械改动用一个'grep 断言审计'测试作为回归拦截，不为每个
   小改动单独写测试"——这个策略需要在 P2 `gate_commands.P3` 或 `minimal_validation` 里落实为具体
   可执行的测试设计方向，供 P3 test-designer 承接。
8. **BDD-15/16（xdist 试点）的 minimal_validation**：本地单核环境测不出加速效果，`minimal_validation`
   字段不能声称"已本地验证 xdist 加速"，应声明"纯代码逻辑变更（pytest 命令行参数），效果验证
   延后到 CI 阶段"这类诚实表述，不要伪造本地验证结果。
9. **files_to_read 精简但要覆盖关键锚点**：P1 已经给出了具体文件+小节标题（不是行号，因为行号会
   漂移），P2 的 files_to_read 应该直接复用这些文件名+小节标题定位，不需要重新探索。

### 上游关联

P1-requirements.md 已 approved（19 条 BDD，2 轮 requirements-review 迭代后通过；第 1 轮指出
BDD-12 表述有"既成事实语气"问题，analyst 修订后第 2 轮通过）。P1 frontmatter：
`risk_level: high`，`phases: [P0...P8]`（无裁剪），`domains: [protocol-docs, gate-scripts,
test-infra]`，`packages: [workflow, dispatch-protocol, state-machine, platform-notes,
state-transitions, phase-cards, dispatch-prompt-template, gate-scripts]`。P1 「同类扫描」3.8
节结论汇总表（P0-brief 6 处已知重复中 ①②③⑤成立需处理、④不成立不处理、⑥定性问题需处理；另有
新发现的第三类重复"8 张阶段卡片内联 MAX 数字散落"）是本阶段影响面梳理的直接输入。

按 C8 映射表：`risk_level: high` 触发 `plan-eng-review` 硬规则（必须派独立 subagent 评审）；
domains 不含 frontend，不触发 plan-design-review；P1 无 `[NEED_CONFIRM]`，不触发 plan-ceo-review。
单评审角色，不需要组长汇总。

### 输入文件

- {AGATE_WORKSPACE}/tasks/TAG0016-protocol-hygiene/P1-requirements.md（需求基线，重点读第 3 节
  「同类扫描」全文 + 第 4 节全部 19 条 BDD + 第 2 节「隐含需求识别」）
- {AGATE_WORKSPACE}/tasks/TAG0016-protocol-hygiene/P0-brief.md（环境约束、已知风险）
- {project_root}/AGENTS.md（项目开发约定、双工作区纪律、改脚本 TDD 工作流）
- agate/WORKFLOW.md、agate/dispatch-protocol.md、agate/state-machine.md、
  agate/platform-notes.md、agate/rules/state-transitions.md、agate/phase-cards/*.md
  （P1 判定为真实重复源的具体位置：WORKFLOW.md「## 平台适配」/「## P1-P8 阶段总览」/
  「## Pre-commit 检查总览」，dispatch-protocol.md「## 平台适配」/「## 可判定门槛规范」/
  「派发 prompt 模板」，rules/state-transitions.md「## 重试上限」，8 张阶段卡片各自的
  "MAX=" 内联行——读 worktree 自己这份，不要读 ~/.agate）
- agate/assets/templates/dispatch-prompt.md（P1 判定的"派发 prompt 双源"另一端，已确认比
  dispatch-protocol.md 内联版多出若干独立小节）
- agate/scripts/check-protocol-consistency.py（现有 CHECK 1-11 实现，BDD-9 要新增 CHECK 12 的
  落点；重点看现有 CHECK 4"gate_commands 键集合跨文件一致"的实现模式，P1 已指出这是可复用的
  既有跨文件比对模式）
- agate/scripts/check-p6-provenance.py（BDD-12/13 跨阶段证据引用机制的落点）
- agate/phase-cards/P6-acceptance.md、agate/phase-cards/P8-release.md（AG0026 现状：P6 refactor
  口径的 regression_pass 字段、P8 "bump-version 后重跑一次 gate_commands.P5" 的现有规则）
- agate/scripts/*.py（.state.yaml schema 相关：`check-state-yaml.py`，BDD-12 补充说明要求新字段
  可选、缺失回退，需要确认该脚本当前的 schema 校验实现方式）
- HANDOFF-TAG0016.md（关键验证命令、双工作区纪律）

</dispatch_guide>

<!-- AGATE_CARD_START -->
## 当前阶段卡片：P2

路径：phase-cards/P2-design.md
---
# P2 — 方案设计

> 当前状态：[首次 / 重试 #N / 裁剪跳阶]
> 裁剪跳阶 → P2 不可裁剪。design_trivial / follows_existing_pattern 可简化（1 个候选方案），不可省略。

## 如果是首次进入本阶段

1. 派发 architect subagent → 产出 P2-design.md
   1.1 写 P2-dispatch-context-architect.md（派发指引：目标/约束/上游关联/输入文件 + 客观查证信息）
2. 按 C8 映射表派评审（见下方）
3. 评审通过 → P2-review.md status: approved
4. 预跑 check-gate.py P2（脚本化检查）
5. git add {AGATE_WORKSPACE}/tasks/{Txxx}/（含 .state.yaml + 产出文件，若 .gitignore 忽略需 git add -f）
   ⚠️ 此时 .state.yaml 的 phase 保持 P2，不要提前写 P3——phase = 本 commit 的产出阶段
6. git commit -m "wf({Txxx}-P2): {摘要}"（phase=P2，P2 产出含 P2-design.md + P2-review.md）
7. P2 commit 完成后进入 P3：**phase 推进 P3 随 P3 产出 commit 一起**（P3-test-cases.md 就绪后），不是单独 phase commit

## 如果是重试

确认上一轮失败原因（方案选择有误 / 候选方案不足 / 评审 rejected）
→ 读 agate/rules/state-transitions.md 确认 retry 上限（P2 MAX=3）

## 前置条件

- [ ] P1-requirements.md 含 domains / risk_level / phases 声明
- [ ] P0-brief.md env_constraints 可查阅

## 派发

- **角色**：architect（`{agate_root}/assets/execution-roles/architect.md`）
- **输入**：P1-requirements.md + P0-brief.md
- **输出**：P2-design.md
- **派发 prompt 追加**：

```
## P2 最小验证
方案设计前，先用最小验证确认关键假设（10 行 HTML 测试页 / curl 请求 / 20 行脚本）。
验证结果写入 P2-design.md 的 minimal_validation 字段。
- 方案依赖浏览器行为/安全模型/外部系统行为 → 必须做最小验证
- 纯代码逻辑 → 须在 minimal_validation 字段声明 `纯代码逻辑，无外部系统依赖`（须写明依赖了哪些内部函数/数据转换）
```

## 产出规格

P2-design.md 必须包含：
- **候选方案 ≥2** + 权衡 + 选择理由（design_trivial / follows_existing_pattern 时可只写 1 个，见下方）
- **`candidate_count: N` 必填**：本方案候选方案数（≥2，design_trivial/follows_existing_pattern 时可 1），gate 按此字段校验，不再解析标题。你写几个候选就填几个，与正文一致。
- **四字段**：`packages:` `domains:` `ui_affected:` `gate_commands:`
- **files_to_read**：实现时需要参考的文件清单（控制 P4 implementer 上下文）
- **env_constraints**：确认/细化 P0-brief 的环境约束
- **minimal_validation**：验证结果 或 声明"纯代码逻辑，无外部系统依赖"（声明时须附理由）

`candidate_count`/`packages`/`domains`/`ui_affected` 写在文件头 **frontmatter**（`---` 分隔块），
不写正文；`gate_commands:`/`files_to_read:`/`env_constraints:`/`minimal_validation:` 留正文。
**可直接复制的完整样例**：
```yaml
---
phase: P2
task_id: TAG0001           # 替换为实际任务编号
type: design
parent: P1-requirements.md
trace_id: T001-P2-20260101 # {task_id}-P2-{YYYYMMDD}
status: draft
created: 2026-01-01
agent: architect
# ── v2.0 机器字段 ──
candidate_count: 2                # int ≥1，必填
packages: [pkg-a]                 # list，必填
domains: [backend, cli]           # list，必填
ui_affected: false                # bool，必填
ui_design_section: true           # bool，可选（presence 语义：ui_affected: true 时声明已含 UI 设计节）
---
```

**UI 设计节（`ui_affected: true` 时必含，P2 gate 校验）：** `ui_affected: true` 的 P2-design.md
正文必须包含 `## UI 设计` 节，节内含**渲染形态声明**（`渲染形态:` 声明行，复用 P1 frontmatter
`ui_render_shape` 的规范形态值 + 中文注释，gate 按规范化值比对校验 P1-P2 一致；无 P1 声明时按
布局型默认）+ **维度选择**（`适用维度:` 声明行）+ **按形态适配的 checklist**（常规布局型 =
布局/交互/视觉三类；渲染组件/时序特效型 = 渲染正确性/动效时序等适用维度 checklist；不适用的维度
显式声明"维度不适用"）。缺 UI 设计节 / 缺形态声明 / 缺按形态 checklist / P1-P2 形态声明不一致 →
P2 gate exit 1。结构规格见 `assets/execution-roles/architect.md`「UI 设计节」节（由 architect
兼任产出，不新增 designer 角色）。

候选方案简化（须附理由，无理由视为无效声明，要求 ≥2 候选方案）：
- `design_trivial: true` + 理由（为什么 trivial）→ 可只写 1 个候选方案（P2 仍不可省略）
- `follows_existing_pattern: [src/foo.py]`（列出参照文件路径）→ 可只写 1 个候选方案，参照已有模式（P2 仍不可省略）

## dispatch_plan 机器字段（可选，TAG0014）

> 本字段是 P2 对**后续阶段编排方案**的机器声明（评估 + 编排模式，见 dispatch-protocol「派发编排机制」），由 architect 在"批次设计"节（execution-roles/architect.md）产出，P2 gate 校验其合法性。

方案含多个独立子任务（多包/多模块/high 复杂度）时，P2-design.md frontmatter 应声明 `dispatch_plan:`（单行 flow YAML，与 candidate_count 同级，**不入 frontmatter-check schema**，缺省不校验）：

```yaml
# ── v2.0 派发编排字段（可选）──
dispatch_plan: {mode: static-batch, parallel_limit: 3, batches: [{id: pkg-a, complexity: medium}, {id: pkg-b, complexity: low}]}
```

字段契约（gate 校验口径）：
- `mode` ∈ {single, static-batch, parallel, recon-then-split, serial}——编排模式（单发/静态拆批/并行/先理解后拆/串行链）
- `parallel_limit` 可选，≥1 整数——并行上限（缺省 3）
- `batches` 可选——mode ∈ {static-batch, parallel} 时每批须含 `id` + `complexity` ∈ {low, medium, high}；批数 ≤ parallel_limit
- 缺字段 / 坏 YAML → P2 gate 跳过校验，行为等同现状（向后兼容，不误拦）

## 影响面梳理（强制节）

**写候选方案之前**先做影响面梳理——方案的取舍取决于它牵动多大面，先设计再补影响面等于反过来给方案找理由。P0 卡片的「同类/影响面预判」给量级、P1 卡片的「同类扫描」给清单，P2 在这两者基础上做**候选方案级**的影响域分析，三处同源、逐级细化，不重复劳动。

P2-design.md 正文必须含影响面梳理节，覆盖三部分：

1. **改什么（Modify）**：逐文件/逐模块列出改动点 + 关联 BDD 编号；改动落点必须落到"哪个文件的哪个小节/函数"，不写"相关代码"这种模糊表述
2. **不改什么（Not Modify）**：显式列出**看起来该改但决定不改**的文件/范围 + 理由。这一栏比"改什么"更容易漏，也是 P4 implementer 判断范围边界的依据（避免"顺手改进"）
3. **风险在哪（Risk）**：每条风险配一条缓解措施；跨模块引用、双源同步（权威源 + 副本）、schema 变更、并发/资源竞争是高频风险项

梳理动作要有客观证据：grep/rg 命中清单、读过的消费方代码、既有 gate 脚本的校验口径——不是凭印象列。P1 已声明 `follows_existing_pattern` 的任务同样要做（沿用既有模式不等于影响面为零）。

## gate_commands 声明

gate_commands 在 P2 固化，后续阶段按此执行：

```yaml
gate_commands:
  P3: "pytest"                  # 可选：测试运行器（verbose 输出，供 check-tdd-red.py 自动读取）
  P5: "pytest -q --tb=no"       # 紧凑输出模式
  P5_e2e: "playwright test --reporter=line tests/e2e/"  # ui_affected: true 时必填
  P5_timeout_seconds: 120       # 可选：该 key 命令的预期耗时上限（秒），见下方字段规则
  P5_e2e_timeout_seconds: 300   # 可选：per-key 声明，不同命令类型各自取档
```

### `{key}_timeout_seconds` 字段规则

`timeout_seconds` 是 `gate_commands` 块内的**可选声明性字段**，用来给每条 gate 命令声明"预期耗时上限"，供跑命令的一方（主 Agent / subagent）据此设置 shell 层超时。四点规则：

1. **排除 P3**：`gate_commands.P3` 继续走既有 `AGATE_TDD_TIMEOUT` 环境变量机制（默认 120s，由 `agate_common.py` 的 `run_test_with_formatter()` 消费、`check-tdd-red.py` 读取，exit 124 → 超时 JSON，区分 A/B 类错误）。`timeout_seconds` **只服务 P5 / P6 / 其他非 P3 key**，不覆盖 P3。两层不合并：P3 层是运行时代码真实消费的超时，`timeout_seconds` 是给人和 subagent 读的静态声明
2. **per-key 声明**：写成 `{key}_timeout_seconds`（如 `P5_timeout_seconds` / `P5_e2e_timeout_seconds`），每条 key 各自声明，**不设整体共享默认**——单元测试与 E2E 的耗时差 2.5 倍以上，共享一个值起不到分类阈值的作用。命名与既有 `{key}_formatter` / `{key}_e2e` 的 per-key 惯例一致
3. **三档默认基准表**（**建议档位，需按命令类型手动声明，不是自动推断**——没有任何代码去"猜"命令属于哪一类）：

   | 命令类型 | 建议档位 | 依据 |
   |---------|---------|------|
   | 单元测试类（pytest / vitest 等） | 120s | 与 `AGATE_TDD_TIMEOUT` 默认值对齐，同类命令的既有锚点 |
   | E2E 类（Playwright / CDP） | 300s | 覆盖页面加载 + 多步操作；比脚本内部硬超时（HARD 90s/180s）更大——外层命令级预期时长必须留够内层完整走完的余量 |
   | 构建类（编译 / 安装依赖 / 打包） | 600s | 覆盖 `npm install` / 编译等长操作。宁可档位定高，也不要让长命令被误判失败（TPV0093 教训：`make test-quick` 挂 188 分钟） |

4. **向后兼容**：缺字段 → 行为等同现状（沿用 `dispatch_plan` 的"缺字段 / 坏 YAML → gate 跳过校验"先例），不新增强制阻断，老任务无需回填

与运行时超时纪律的关系：本字段是**静态声明**（层级 1），subagent 执行命令时真正去设 shell timeout 的是**层级 4** 的「命令超时兜底」（取值 = 预期耗时 ×1.5；本字段已声明时"预期耗时"直接取该值）。四层超时机制的完整分层见 dispatch-protocol.md「命令超时兜底与既有超时机制的分层关系」。

## 评审派发（C8 机械映射）

按 P1 声明的 domains + risk_level 机械映射评审：

| domain | risk_level | 必须派的评审 |
|--------|------------|------------|
| backend | 任意 | plan-eng-review（P2 方案评审） |
| frontend | 任意 | plan-design-review |
| 任意 | high | plan-eng-review（硬规则，必须派独立 subagent） |
| P1-requirements.md 含 [NEED_CONFIRM] 且涉及业务方向 | 任意 | plan-ceo-review |

> **去重说明**：同一任务命中多行且触发同一评审角色时，去重只派发一次（如 backend + high 均命中 plan-eng-review，只派 1 个 plan-eng-review，不重复派发）。

多个评审角色 `专家组并行` → 组长汇总 → P2-review.md（status: approved / rejected）。
详见 `agate/rules/review-mapping.md`。

**并行派发**（多个评审角色时）：
1. 同时派发所有触发的评审 subagent（每个一个 task 调用）
   > **操作方式**：在一个 assistant 消息中连续发起多个 task 工具调用（每个评审角色一个）。
   > 不要等前一个 task 返回再发下一个——那是串行，不是并行。
   > 平台会并行执行多个 task，全部返回后再进入下一步（派发组长汇总）。
2. 每个评审 subagent 各写一个 dispatch-context + 各自产出文件（示例非穷举，按 C8 映射表触发）：
   - plan-eng-review → P2-review-eng.md
   - plan-design-review → P2-review-design.md
   - plan-ceo-review → P2-review-ceo.md
   - cso → P2-review-cso.md
3. 所有评审返回后，派发组长汇总 subagent（角色：review + 指定为「专家组组长」）
4. 组长输入：所有评审文件路径
5. 组长产出：P2-review.md（统一 status: approved / rejected）。**组长 subagent 产出的 P2-review.md 的 Header agent 字段必须是组长角色名（非 main）——check-gate.py P2 硬拦截 agent=main 的 approved**
6. 组长规则：
   - 不发表新意见，只汇总
   - 任何专家标 BLOCKER → status: rejected
   - 多位专家分歧 → 标「专家组分歧」交人工
   - 全票无 BLOCKER → status: approved

**单评审角色时**：直接派发，无需组长汇总，产出直接写 P2-review.md。

review 不通过 → architect 修改方案 → 再 review → … → approved（⑩迭代循环，review 和 gate 重试共享 retry 预算）

**UI 测试选择器**：涉及前端时，P2 design 建议声明 UI 组件的稳定测试标识清单（如 `data-testid`，而非 class 命名）。P3 test-designer 用稳定标识定位元素，P4 implementer 按清单实现--class 命名可重构，稳定标识不变。具体方案由 P2 architect 决定。

## gate 规则

```bash
check-gate.py P2 $TASK_DIR
```

- 候选方案数 ≥2（design_trivial / follows_existing_pattern 时可只写 1 个）
- P2-review.md 存在且 status: approved（agent≠main）— 不存在 → gate exit 1
- 四字段齐全（packages/domains/ui_affected/gate_commands）
- gate_commands.P3 可选（非 pytest 项目建议声明，供 check-tdd-red.py 自动读取测试运行器）
- 候选方案 ≥2 时含权衡/选择理由

## 推进条件（全部满足才写 phase: P3）

- [ ] P2-design.md 候选方案 ≥2（或 design_trivial/follows_existing_pattern 须附理由时可只写 1 个）+ 四字段齐全
- [ ] 含「影响面梳理」节（改什么 / 不改什么 / 风险在哪 三部分齐全，且写在候选方案之前）
- [ ] P2-review.md 存在且 status: approved（agent≠main）
- [ ] gate_commands.P5_e2e 已声明（ui_affected: true 时）

## 常见错误

1. **忘了最小验证**：方案依赖外部系统行为（API MIME 类型、浏览器 CSP 等）但直接假设前提成立 → 到 P6 才发现不可行。跑一个 curl / 10 行 HTML 就能 5 分钟发现
2. **gate_commands.P5 只列单元测试**：UI 任务时缺少 P5_e2e → P5 不会跑端到端验证
3. **files_to_read 列太多文件**：把所有相关文件都列上 → P4 implementer 上下文爆炸。只列确实需要参考的
4. **忘了派评审**：按 C8 映射机械执行，不靠"觉得不需要"
5. **gate 不过 ≠ 你失败了**：红灯指向工作/设计的问题，不指向你。正确动作是诊断→退回/重试/PAUSED，不是修改产出让它变绿。

## 下游影响

- P4 依赖 files_to_read 导航代码阅读范围
- P5 依赖 gate_commands 执行验证命令
- P6 依赖 ui_affected 判断是否需要 vision-helper
- gate_commands 在 P2 固化后 P4-P6 不能改——设计阶段是声明验证契约的唯一窗口

> 完成 → 读 phase-cards/P3-tdd.md
<!-- AGATE_CARD_END -->

<objective_info>
- worktree 当前 HEAD：546b093（P1 commit 已完成），工作区干净。
- P1-requirements.md frontmatter 关键字段（主 Agent 已核实）：risk_level=high，
  phases=[P0,P1,P2,P3,P4,P5,P6,P7,P8]（无裁剪），domains=[protocol-docs, gate-scripts,
  test-infra]，capability_requirements 4 条均 available（python3-runtime/grep-rg/git-log-diff/
  ruff）。
- P1 BDD 编号与主题对照（主 Agent 已梳理，供快速定位，具体内容仍需读 P1-requirements.md 原文）：
  BDD-1 职责声明表 / BDD-2 平台适配去重 / BDD-3 阶段门槛表去重 / BDD-4 派发 prompt 双源收敛 /
  BDD-5 重试上限表去重（文档级）/ BDD-6 重试上限数值散落收敛（8 张卡片）/ BDD-7 Pre-commit 清单
  模式不误伤 / BDD-8 职责定位收敛 / BDD-9 防复发 CHECK 新增 / BDD-10 合法引用不误判 /
  BDD-11 全量重跑点审计表 / BDD-12 P6 引用 P5 证据的无改动校验标准 / BDD-13 不可复用边界 /
  BDD-14 P8 重跑范围精简 / BDD-15 xdist 试点仅锚定 CI / BDD-16 xdist 不破坏并行隔离规则 /
  BDD-17 Linux 回归基线 / BDD-18 Windows 兼容仅增量声明 / BDD-19 防复发落地入口（职责边界声明行）。
</objective_info>
