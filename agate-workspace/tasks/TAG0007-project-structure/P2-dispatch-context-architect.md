---
phase: P2
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0007
role: architect
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

## 【第 2 轮：修复轮，增量模式】

- **上轮产出路径**：{AGATE_WORKSPACE}/tasks/TAG0007-project-structure/P2-design.md（已存在，
  在此基础上**修改**，不要重写整份文件——4 个决策组的技术方向均已锁定，只修复具体缺陷）
- **上轮 dispatch-context**：本文件下方「目标/约束/上游关联/输入文件」原样有效，复用其约束
- **评审意见**：{AGATE_WORKSPACE}/tasks/TAG0007-project-structure/P2-review.md
  （agent: plan-eng-review, status: rejected，1 个阻塞问题 + 2 个非阻塞措辞建议）

### 本轮修复目标（只改评审指出的问题，不推翻已锁定的 4 组技术方向）

**阻塞项（必须修复）**：决策组3（CODE-MAP 一致性核对）的 `gate_p7` pairing 校验逻辑描述不完整，
且 `code_map_new_files_count` 字段声明了但从未被使用。评审已逐行核实 `check-gate.py` 现有
`gate_p7` 源码（L807-903），确认 DESIGN_GAP pairing 是**两层校验**：
  (a) 内部一致性：`design_gap_reviewed_count < design_gap_count` → exit 1（L840-848）
  (b) 转抄核对：P4 正文 regex 实际计数的 `[DESIGN_GAP:]` 数量 与 P7 的 `design_gap_count`
      （**不是** reviewed_count）比较 → exit 1（L873-893）
而 P2-design.md 当前只描述了单层校验（P4 实际计数直接比 `code_map_reviewed_count`），且声明的
`code_map_new_files_count` 字段从未被任何判定分支引用。**二选一修复**（architect 自行判断哪个
更合适，不要求特定选择）：
  ① **补全两层校验**，与 DESIGN_GAP 结构真正对齐：新增
     `code_map_reviewed_count < code_map_new_files_count` 内部一致性检查，且转抄交叉核对应比较
     `code_map_new_files_count`（而非 `code_map_reviewed_count`）；
  ② **明确声明为有意简化的单层校验**：删除未使用的 `code_map_new_files_count` 字段声明（或明确
     写出它仅作展示/文档用途、不参与 gate 判定），并把 §5 minimal_validation 第 1 条的 `result`
     从 `confirmed` 改为准确反映"结构非完全对称，已知简化点为 X"的表述（不能继续声称"结构完全
     对称，可原样套用"）。
需要修改的位置：§1.1（P7-consistency.md 行、`agate/scripts/check-gate.py` `gate_p7` 函数行）、
§2.3（候选 A 描述）、§5 minimal_validation 第 1 条。

**非阻塞项（建议一并修复，不强制但应处理）**：
1. §1.3 R5 与 §1.2「不改什么」里"比照 CHANGELOG.md [Unreleased] 现有处理方式"的类比过于精确化
   （暗示两者冲突形态类似）。CHANGELOG 冲突是纯追加型，CODE-MAP.md 含结构化字段，多方并发改写
   同一条目更接近"同一行被两方各自改写"，git 无法自动合并，比 CHANGELOG 追加冲突更难处理。改写
   措辞为诚实反映这一差异（如"比照 CHANGELOG.md 处理方式，但需承认 CODE-MAP.md 的结构化字段
   更新比纯追加冲突更难自动合并"）。
2. §7 末段"本 P2-design.md 已完整声明五字段标题名与格式要求"的表述过于绝对——实际只声明了字段
   **类别名**（模块/层/依赖方向/关键文件/约定），未声明具体标题的 markdown markup 形式。改写为
   "已声明字段名称，具体标题 markup 由各批次自行决定，不强制两批次产出的 markup 完全一致"。

**评审同时指出的测试缺口（供 P3 阶段参考，本轮 P2 不必现在补测试用例，但若顺手能在 P4 核对表
描述中提升骨架归属列的强制力可一并说明，不强制）**：BDD-4（骨架归属列）目前只有 WARNING 级"表
标题存在性"检查，逐行是否真填写没有 gate 捕获，强制力明显弱于 BDD-7（CODE-MAP 列，有 exit 1 硬
校验）。不要求本轮解决，但如果修复阻塞项时顺手能补一句说明也可以，不强制。

修改完成后，把改动追加进 P2-progress.md（哪几节改了、依据评审哪条意见），然后返回。**其余内容
（决策组1/2/4的方向、§1 影响面梳理的改什么/不改什么、§3 完成标志、§4 env_constraints、§6
gate_commands、§7 dispatch_plan 的批次划分本身、§8 files_to_read）本轮不动**，review 已判定这些
部分方向确认/合规。

---

## 首轮派发指引（背景，供理解上下文）

### 目标
把 P1-requirements.md 的 11 条 BDD（RM-AG0008 骨架脚手架 BDD-1~5 + RM-AG0009 CODE-MAP 架构演进
纪律 BDD-6~11）转化为可实现的技术方案，产出 P2-design.md。核心决策：骨架/CODE-MAP 产出物落哪个
阶段/角色/目录、以何种格式表达、gate 如何校验、如何接入既有 P2 设计规格/P7 一致性检查/角色体系
而不产生新旧机制口径冲突。

### 约束
1. **两个机制方案要分开设计但共享一次影响面梳理**：RM-AG0008（骨架，一次性产出物）与 RM-AG0009
   （CODE-MAP，持续演进维护物）生命周期不同，候选方案应分别探索（各自 ≥2 候选，除非能证明
   design_trivial/follows_existing_pattern 成立），但两者改动面高度重叠（都可能touching
   P2-design.md 产出规格、P7-consistency.md 检查项、templates/ 新模板），影响面梳理需统一做一次
   避免两组方案各自重复梳理同一批文件。
2. **ADR-003（不绑定技术栈）是硬约束**：骨架模板设计（对应 BDD-2）不能把具体语言/框架的目录名
   写死进协议本体，必须是参数化形式（候选目录集合 + 项目侧声明）。这是 P1 review 已确认的评审
   重点，P2 方案违反会被 plan-eng-review 打回。
3. **候选角色优先复用**：P1 隐含需求第 4 条已标出 role-system.md 既定原则"角色清单最小化"——
   architect（P2 职责，天然贴合骨架设计+架构合规检查）与 consistency-reviewer（P7 职责，天然贴合
   CODE-MAP 漂移核对）是候选复用对象，新增专属角色需要有明确理由才能选择（不是默认选项）。
4. **BDD-4/BDD-7 累加关系已在 P1 声明**：P4 新增文件时，骨架目录归属（BDD-4）与 CODE-MAP 更新
   义务（BDD-7）是同一触发场景下的两个独立累加验收标准，P2 设计需要让这两条能被同一实现动作
   （P4 implementer 新增文件时的一次性检查/更新流程）自然满足，不要设计成两套互相独立、需要
   implementer 分别记两遍的机制。
5. **CODE-MAP 并发更新边界（P1 已声明，留给 P2 判断）**：多任务/多 worktree 并行 P4 阶段更新同一
   CODE-MAP.md 存在合并冲突风险（P1-requirements.md 隐含需求第 8 条）。P2 需要给出方向性判断——
   哪怕只是"本轮方案不解决并发合并，声明为已知限制/留待未来任务"也要显式说明，不能沉默略过。
6. **BDD-10（change_type: refactor 不豁免 CODE-MAP 更新义务）需要具体落点**：P2 设计需要说明
   refactor 类任务的 CODE-MAP 更新义务具体在哪个阶段卡片、以什么形式呈现（如 P4-implementation.md
   或 P6-acceptance.md 的 refactor 口径小节新增一句话约束），不能只在需求层面提及、设计层面空缺。
7. **gate_commands 声明遵循本仓库既有惯例**（objective_info 给出 TAG0017 的 P2-design.md 作参照
   样例）：拆独立 key（不要塞进 `&&` 链路）、非 P3 的长命令按需声明 `{key}_timeout_seconds`。本仓库
   P5 的标准三件套是 pytest / check-protocol-consistency.py / shellcheck，三者应各自独立 key。
8. **回归底线**：`gate_commands.P5`（或等效 key）必须能验证"改动前 1011 个测试仍全部通过 + 一致性
   检查仍 0 ERROR"这一条（对应 P1 的 BDD-5/BDD-11），不能只验证新增内容。
9. **复杂度评估与 dispatch_plan**：本任务改动面横跨 phase-cards / execution-roles / review-roles /
   scripts / templates 五类文件，两个机制叠加，按「派发编排机制」工作量五维评估，大概率落在 high
   复杂度区间——P2 卡片规则"high 复杂度必须拆分"，若评估结果确实是 high，必须在 frontmatter 声明
   `dispatch_plan`（mode 从 single/static-batch/parallel/recon-then-split/serial 中选，若拆分方案
   本身依赖先梳理清楚改动落点，可选 recon-then-split）。拆批边界必须对齐「影响面梳理」的改什么/
   不改什么分组，同一文件不能被两个批次各改一次（TAG0017 的 P2-design.md §0 有一个真实的"同文件
   跨批冲突需合并批次"案例，可参考其处理方式）。
10. **本任务 domains: [backend]，risk_level: high**——按 C8 机械映射会自动触发 plan-eng-review
    （backend 命中一次，risk_level:high 硬规则命中一次，去重只派一次）。不涉及 frontend，无需
    plan-design-review；P1 无涉及业务方向的 NEED_CONFIRM，无需 plan-ceo-review。

### 上游关联
P1-requirements.md（approved）已交付：
- 11 条 BDD（RM-AG0008 组 BDD-1~5：骨架存在性/模板参数化/不重复触发/P4落点+偏离说明/回归基线；
  RM-AG0009 组 BDD-6~11：CODE-MAP存在与初始化/P4更新义务/P7同步核对/依赖偏离可见信号/refactor
  不豁免/回归基线）
- 「机制一致性/候选接入点盘点」节已给出候选接入点清单：P2-design.md 字段扩展（类比 packages/
  domains/ui_affected 的 frontmatter 字段模式）、P7-consistency.md 现有第3条一致性检查项的扩展点、
  architect/consistency-reviewer 角色复用候选、check-protocol-consistency.py 同家族脚本新增/扩展
  候选、templates/ 新增骨架模板+CODE-MAP模板候选、WORKFLOW.md 工作区目录规范的落点空白
- 隐含需求第1条已点名：骨架/CODE-MAP 产出物落哪个目录未定义（工作区 9 固定子目录不含此二类）——
  这是本轮 P2 必须给出具体答案的决策点
- P0-brief known_risks 六条仍然全部有效（P1 未推翻任何一条，只是转化为需求侧含义）

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0007-project-structure/P1-requirements.md（需求基线，核心输入）
- {AGATE_WORKSPACE}/tasks/TAG0007-project-structure/P0-brief.md（任务简报）
- {AGATE_WORKSPACE}/tasks/TAG0007-project-structure/P1-review.md（评审关注点，尤其 ADR-003
  一致性、BDD-4/7 关系、并发边界三处曾被打回的问题，P2 设计不应重蹈）
- /home/kity/oclab/agate/.worktrees/agate-TAG0007/AGENTS.md（项目约定、改脚本工作流）
- /home/kity/oclab/agate/.worktrees/agate-TAG0007/agate/WORKFLOW.md（P0-P8 流程骨架 + 工作区
  目录规范）
- /home/kity/oclab/agate/.worktrees/agate-TAG0007/agate/role-system.md（角色体系、机械映射表）
- /home/kity/oclab/agate/.worktrees/agate-TAG0007/agate/dispatch-protocol.md（尤其「派发编排机制」
  工作量五维评估 + 五种编排模式，「do→review 迭代循环」）
- /home/kity/oclab/agate/.worktrees/agate-TAG0007/agate/adr.md（ADR-003 不绑定技术栈、ADR-005
  机制交叉级别改动判据）
- /home/kity/oclab/agate/.worktrees/agate-TAG0007/agate/rules/review-mapping.md（C8 评审映射表
  权威定义）
- /home/kity/oclab/agate/.worktrees/agate-TAG0007/agate/phase-cards/P7-consistency.md（P7 现有
  一致性检查项的确切内容，供设计 CODE-MAP 核对如何接入）
- /home/kity/oclab/agate/.worktrees/agate-TAG0007/agate/phase-cards/P4-implementation.md（P4
  现有产出规格，供设计"新增文件触发骨架/CODE-MAP 更新义务"如何接入）
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

### env_constraints 与 gate_commands 的边界（不等价）

`env_constraints` 是**声明性字段**——它只做信息确认/注入（写清楚环境约束是什么，供 P4/P8 读取参考），本身不会被自动执行，也没有任何 gate 脚本会去校验 `env_constraints` 里写的条件是否真的成立。真正被执行的机制是 `gate_commands`：P5/P6 只会去跑 `gate_commands` 里声明的命令，不会去"执行" `env_constraints` 的内容。二者不等价，不能互相替代。

**因此**：任何需要被强制执行的约束，必须落到 `gate_commands`（有命令可跑、有 exit code 可判定），或者落到 P4/P8 阶段卡片里的明确 checklist 条目（有人工自查动作可执行）。只写进 `env_constraints` 而不落 `gate_commands`/checklist 的约束，等于没有强制力——architect 设计时若发现某条环境约束必须被强制执行，不要止步于写进 `env_constraints`。

### `--strict` 反模式：不要放进 `&&` 链路中间

`gate_commands` 的每个 key 声明的是**一条完整命令**，若把多个校验命令用 `&&` 拼接成一条命令串塞进同一个 key，会有短路问题——只要前一个命令非零退出，后面的命令（包括 `--strict` 校验）根本不会跑，看似"全部声明了"，实际后半段从未被执行过，问题被掩盖。

**反例（不要这样写）**：
```yaml
gate_commands:
  P5: "pytest -q --tb=no && check-protocol-consistency.py --strict && shellcheck scripts/*.sh"
```
上面这条命令一旦 `pytest` 失败就短路退出，`--strict` 校验和 `shellcheck` 都不会执行，历史上 TAG0004 等任务已经在这类写法上吃过亏。

**正确做法**：把每个校验拆成独立的 key 分别声明，各自独立跑、独立记录 pass/fail，不共享短路关系：
```yaml
gate_commands:
  P5: "pytest -q --tb=no"
  P5_consistency: "check-protocol-consistency.py --strict-errors-only"
  P5_shellcheck: "shellcheck scripts/*.sh"
```
`--strict-errors-only`（仅 ERROR 判失败）适合日常任务默认使用；`--strict`（WARNING-only 也判失败）保留给专门做 WARNING 债务清理的任务主动选用。

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
- P1-requirements.md frontmatter：risk_level=high, phases=[P1..P8]（不裁剪）,
  packages=[phase-cards, execution-roles, review-roles, scripts, templates], domains=[backend],
  capability_requirements=[]
- 验证命令（P0-brief env_constraints.test_cmd）：
  `python3 -m pytest agate/tests/`；`python3 agate/scripts/check-protocol-consistency.py --strict`；
  `bash agate/tests/scripts/count-tests.sh`（HANDOFF-TAG0007.md 补充：日常默认模式用
  `check-protocol-consistency.py`（非 --strict，0 ERROR 才行，314 存量 WARNING 非回归基线）；
  另有 `shellcheck -S warning agate/scripts/*.sh`）
- 回归基线：worktree 已验证 1011 pytest passed + consistency 0 ERROR（默认模式 exit 0）
- 本仓库同类协议改动任务的 P2-design.md gate_commands 参考样例（同 worktree 内 TAG0017 任务，
  同样是"改 gate 脚本/协议文档"类型）：
  `{AGATE_WORKSPACE}/tasks/TAG0017-toolchain-fixes/P2-design.md`——采用 static-batch 编排模式，
  gate_commands 按独立 key 声明（非 `&&` 链路），可作候选方案格式参照（不代表本任务必须照抄同一
  编排模式，工作量评估需针对本任务自己重新做）
- 现有 phase-cards（9 张）/ execution-roles（7 个）/ review-roles（10 个）/ templates（11 个）/
  scripts 中一致性类脚本家族（check-protocol-consistency.py / check-gate.py / check-state-transition.py
  / check-state-yaml.py / agate-evidence-consistency.py / agate-frontmatter-check.py）清单已在 P1
  阶段盘点过（详见 P1-requirements.md 「机制一致性/候选接入点盘点」节表格），P2 可直接复用该清单
  不必重新 ls，聚焦候选方案的具体设计取舍
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
