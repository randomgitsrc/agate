---
phase: P1
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0027
role: analyst
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

产出 `P1-requirements.md`：把 P0-brief 的一句话任务（编排语义统一落地，RM-AG0054）展开为含
**≥16 条 BDD** 的需求基线，供 P2 设计与 P6 验收使用。范围 = **全量四 phase，不分后续任务**：

- **Phase 1（转移表结构化）**：`rules/phases.yaml` 增 `next`/`retreat` 字段，对齐
  `state-machine.md` 既有转移语义（P5/P6→P4、P6.5→P6、diff≥2→PAUSED、P6 exit 2→P6.5
  前进特例）；新增字段纳入既有 S-1/S-2 双向一致性 gate（`check-structure-consistency.py`），
  **不新开独立一致性检查**
- **Phase 2（推进侧 CLI）**：新增 `agate next` / `agate advance`（消费
  `check-state-transition.py` 跳变校验 + `check-gate.py` exit 三态 0 直推 / 1 回退 /
  2 暂停转主 Agent + exit 2 落盘 `exit2-resolution` 机器可读产物）；与 `agate-retreat-to.py`
  回退侧对接；`loop-orchestration.md` 档位 C 自动推进改走 `agate next`（CLI = 档位 C 的
  **可观测层**）；补 BDD"档位 C 全程用 agate next 推进，主 Agent 未自行判断进入下一 phase"
- **Phase 3（编排心智统一文档化）**：dispatch-protocol 五模式为唯一语义锚点，平台差异
  （workflow/ralph/goal）全部挂「实现注记」标记（4.3 结构性判据格式约定：`> 实现注记：`
  标记行）；排查协议文档语义小节平台名污染
- **Phase 4（渲染层 + 注入自动化，方案 A：渲染时注入）**：派发 = 单命令自动注入渲染
  （`agate dispatch P{phase} {role}`），**主 Agent 不直接调用 `agate-inject-card.py`**——
  dispatch 上下文渲染时动态拼装 phase-card（Lazy Injection），消灭"占位符缺失→注入失败→
  手动修"环节；审计 2 联动走 **A1 路线**：`check-p6-provenance.py` 审计 2 扫描对象从
  "静态文件"改为"渲染产物"（卡片块在渲染层标记来源，排除逻辑不变）；
  `agate-card-inject.py` / `agate-inject-card.py` 保留纯手工写上下文场景兜底
- **护栏 1 机械化**：`check-protocol-consistency.py` 增加"markdown 段落含平台名但无
  「实现注记」标记"扫描（结构性判据，非文件名单）进 CI 硬校验

### 约束

1. **范围锁定**：全量四 phase 已纳入本任务，不分后续任务。若分析发现需改动超出
   P0-brief/设计 v3b 锁定范围（如新开独立一致性检查、P6.5 改独立 phase、重构 dispatch-protocol
   五模式本体、重写 check-gate/check-state-transition 返回约定），立即停下报告主 Agent，
   不擅自扩范围。
2. **S-1/S-2 复用，不新开**（P0-brief out-of-scope）：Phase 1 新增 next/retreat 字段纳入
   既有 S-1/S-2 双向一致性 gate（`check-structure-consistency.py`，md 侧锚点 = WORKFLOW.md
   阶段总览表，行 7-11）。字段命名须与既有 task_fields/gates 结构兼容、过 JSON Schema
   （`rules/schema/phases.schema.json`）。
3. **P6.5 口径（state-machine.md:74-78）**：P6.5 是挂载于 P6→P7 转移上的**强门槛子阶段，
   非独立 phase 值**——.state.yaml 的 phase 保持 P6 直至 P7。phases.yaml 已有 P6.5 条目，
   新增 next/retreat 字段不得把它写成独立转移边。
4. **转移表语义唯一权威 = state-machine.md**，照抄不搞双套判定：P1/P2 review rejected →
   回自身（retry+1）；P5/P6 gate 失败 → 回 **P4**（retry+1）；P6.5 needs-revision → 回
   **P6** 重验（judge 轮次 ≤2）；回退 diff≥2 → 强制 PAUSED + 人工批准（
   check-state-transition.py 机械拦截，转移表与之一致）；P6 exit 2 → **P6.5 前进特例**
   （唯一"exit 2 直通"例外，不泛化）。
5. **exit 2 三态建模**：exit code 0=直推下一 phase / 1=按转移表回退（retry+1）/ 2=暂停转
   主 Agent（多数阶段通用语义）。转移表为 exit 2 定义"下一动作"字段；exit 2 分支的解决
   必须落盘**机器可读产物**（`exit2-resolution`，记录"何时/依据什么客观证据/由谁解决"），
   纳入 P6.5 judge / provenance 审计复核范围。**不假装消灭模型自判**——CLI 在 exit 2
   分支暂停转主 Agent 是设计意图而非缺陷，文档须明确标注（设计诚实边界）。
6. **不改既有脚本返回约定**：check-gate.py exit 0/1/2、check-state-transition.py exit 0/1
   保持原样；`agate next` / `agate advance` 只新增消费方（读 phases.yaml next/retreat +
   check-state-transition + check-gate exit 三态 + agate-retreat-to.py 回退侧对接）。
   BDD 不得写成"改造 check-gate.py/check-state-transition.py 返回语义"。
7. **档位 C 对接是行为变更**：BDD 细化前须先读 loop-orchestration.md 档位 C 现状执行逻辑
   （主 Agent 逐轮读状态→执行单步→pre-commit gate 兜底），"档位 C 自动推进改走 agate
   next"须验证**不破坏既有 /loop 手动（档位 A）/半自动（档位 B）档位**。CLI 定位 = 档位 C
   的可观测层，复用"硬中断点必停"语义（PAUSED 而非 retry）。
8. **方案 A 两路并存**：渲染时注入（`agate dispatch` 单命令）是新主路径，但纯手工写上下文 +
   `agate-inject-card.py` 注入的**存量用法必须保留**（BDD 覆盖两路）；`agate-render-dispatch-prompt.py`
   现有消费方须先确认现状再改（主 Agent 手拼 prompt 场景）。改派发路径不得破坏手工用法。
9. **审计 2 A1 联动**：check-p6-provenance.py 审计 2（现状 ~318-355 行）现在靠 dispatch-context
   **物理占位符块**排除卡片内容（P6 卡片本身含 PASS/FAIL 模板字样）——改渲染时注入后文件
   里无物理卡片块，须改扫渲染产物（卡片块在渲染层标记来源，**排除逻辑不变**）；手工写
   上下文场景保留文件版兜底。BDD 覆盖"渲染输出含卡片块时排除逻辑仍生效 + 手工场景文件版
   兜底"。
10. **护栏 1 结构性判据**（非文件名单）：凡 `rules/*.yaml` 机器可读数据面禁止出现平台名
    （OpenCode / Claude Code / DSH / workflow / ralph / goal / task）；markdown 叙述文档允许
    平台名但**仅限带「实现注记」标记的小节/表格**（统一格式 `> 实现注记：` 标记行）；
    `platform-notes.md` / `SETUP.md` / WORKFLOW.md「已知适用环境」表（141-148 行）整文件/
    整表豁免（平台适配权威源，平台名集中于此是正确组织）。consistency 扫描对象 = "markdown
    中含平台名但无实现注记标记的段落"，不维护文件名单。
11. **编排心智锚点**：dispatch-protocol 五模式（dispatch-protocol.md:511-519 附近）为唯一
    语义锚点；DSH 的 workflow/ralph/goal 是这些语义的**实现**，不是协议新概念——协议层不
    发明"workflow 模式"/"ralph 模式"。Phase 3 排查协议文档语义小节平台名污染时，将命中
    按"语义定义（须清理/挂注记）vs 实现注记（豁免）vs 元信息（豁免，如 WORKFLOW 已知适用
    环境表）"三分类，逐条判定写进 P1 正文。
12. **同类扫描不可省**：按 P1 卡片「同类扫描」节对下方客观查证信息 D 逐条判定"本次处理 /
    本次不处理 + 理由"，结论写进 P1-requirements.md 正文（"已确认只此一处"也要显式写出）。
13. **P0-brief 时效性质疑必做**：P0-brief 立项与启动同日（2026-09-02），主 Agent 已核对
    无漂移，但 analyst 仍须独立质疑一次并写一行结论（"已核对 P0-brief 时效性，无漂移"或
    `[P0_STALE: 具体漂移点]`），空白不算做过。
14. **BDD 可二值判定**：每条 BDD 的 Given/When/Then 必须可明确 PASS/FAIL，禁止中间态。
    BDD 是"系统行为"视角（CLI exit code / 文件存在性 / 渲染产物内容 / 扫描命中数 /
    schema 校验结果），不要写成"调用哪个函数"的实现细节。
15. **judge 启用**：TAG0027 为机制后新任务（created 2026-09-02 ≥ judge_required_since
    2026-08-22），主 Agent 已在 .state.yaml 写 `judge.enabled: true`。P1-requirements.md
    frontmatter 无需重复，但正文不得与 judge 机制冲突（P6.5 judge 复核范围含
    exit2-resolution 产物）。

### 上游关联

- P0-brief.md 四字段锁定范围与 known_risks 七条（check-gate/check-state-transition 消费方、
  档位 C 对接、转移表防漂移、P6.5 口径、exit 2 模型残留点、审计 2 联动、渲染时注入两路并存）
- 设计文档 v3b `docs/design-notes/design-orchestration-semantics.md`（2026-09-02 三轮独立
  评审闭环定稿）是**本任务 BDD 清单的直接来源**——§4 采纳设计（4.1 心智锚点 / 4.2 三平台
  映射含实现注记示范 / 4.3 三护栏 + 结构性判据 / 4.4 渲染层）、§5 资产衔接（既有资产表 +
  收敛后三个真实缺口）、§6 落地路径（Phase 1-4）逐节转 Given/When/Then
- 评审链三份：v1 FAIL（2 BLOCKER）→ v2 独立评审（B1'/W1'/W2'/N1'/N2'）→ v3 落盘复审
  PASS（4 NIT 修复闭环为 v3b）→ 第三轮 meta 评审"时间线指控"经核验不成立但可追溯性已
  采纳——BDD 须体现这些修复的语义（P6.5 非独立、S-1/S-2 纳入、结构性判据、WORKFLOW 豁免）
- state-machine.md 转移规则 / loop-orchestration.md 档位现状 / dispatch-protocol.md 五模式
  / rules/phases.yaml + schema / check-p6-provenance.py 审计 2 现状 / check-structure-consistency.py
  S-1/S-2 —— 均为 Phase 1-4 改动对象或消费方的现状锚点

### 输入文件（按顺序读，路径以 worktree 根为基准）

1. `agate-workspace/tasks/TAG0027-orchestration-semantics/P0-brief.md`
2. `docs/design-notes/design-orchestration-semantics.md`（设计 v3b 全读，重点 §4/§5/§6）
3. `docs/reviews/review-orchestration-semantics-v3-20260902.md`（v3 复审 PASS + 4 NIT 闭环说明）
4. `docs/reviews/review-orchestration-semantics-v2-independent-20260902.md`（v2 发现 B1'/W1'/W2'，按需）
5. `agate/state-machine.md`（重点"状态机定义"节 74-78 P6.5 口径、95-99 PAUSED、132-133/148
   回退规则、139 P6 exit 2→P6.5、151 P6.5→P7）
6. `agate/loop-orchestration.md`（重点档位 A/B/C 定义 15-74 行、gate 处理流程 227-243 行）
7. `agate/dispatch-protocol.md`（重点五模式 511-519 行 + 派发编排机制）
8. `agate/rules/phases.yaml`（Phase 1 扩展对象：现有 P0-P8+P6.5 条目结构）
9. `agate/rules/schema/phases.schema.json`（字段校验现状）
10. `agate/scripts/check-state-transition.py`（消费方现状：exit 0/1 + P2.3-P2.5 检查）
11. `agate/scripts/check-gate.py`（消费方现状：exit 0/1/2 + OLD_PHASE 回退检测）
12. `agate/scripts/agate-retreat-to.py` / `agate-retreat-state.py`（回退侧 CLI 现状）
13. `agate/scripts/check-p6-provenance.py`（审计 2 现状 ~318-355 行）
14. `agate/scripts/check-structure-consistency.py`（S-1/S-2 现状，行 7-11）
15. `agate/scripts/agate-inject-card.py` / `agate-card-inject.py` / `agate-render-dispatch-prompt.py`
    （Phase 4 行为变更对象现状）
16. `agate/scripts/check-protocol-consistency.py`（护栏 1 机械化挂载点现状）
17. `AGENTS.md`（项目约定）+ `docs/guides/worktree-dogfooding-guide.md`（双工作区纪律，按需）

> ⚠️ 协议本体文件（第 5-16 项）读 **worktree 自己的 `agate/`**（改造对象的现状），不是
> `~/.agate`（稳定版主 checkout）。门 gate 用稳定版，改造对象在 worktree——见 P0-brief
> executor_env + AGENTS.md 双工作区纪律。

### 产出文件字段

用 `FILE=agate-workspace/tasks/TAG0027-orchestration-semantics/P1-requirements.md agate-md-field-set --list`
查看本阶段应填字段；`FILE=... agate-md-field-set <key> <value>` 逐个写入；写入失败照错误
提示修正，不要手写 frontmatter；仍失败则报告主 Agent，不要绕开 set。
</dispatch_guide>

<!-- AGATE_CARD_START -->
## 当前阶段卡片：P1

路径：phase-cards/P1-requirements.md
---
# P1 — 需求基线

> 当前状态：[首次 / 重试 #N]
> P1 不可裁剪（核心阶段）

## 如果是首次进入本阶段

1. 派发 analyst subagent → 产出 P1-requirements.md
   1.1 写 P1-dispatch-context-analyst.md（派发指引：目标/约束/上游关联/输入文件 + 客观查证信息）
2. 主 Agent 确认：BDD 验收条件 ≥1 条 + 无未决 NEED_CONFIRM
2.5 派发 requirements-review subagent（角色文件：{agate_root}/assets/review-roles/requirements-review.md）
     2.5.1 写 P1-dispatch-context-requirements-review.md（派发指引：目标/约束/上游关联/输入文件 + 客观查证信息）
    输入：P1-requirements.md
    产出：P1-review.md（agent≠main，含 BDD 编号引用 + 覆盖维度标注）
    review 不通过 → analyst 修改 → 再 review → … → approved（⑩迭代循环）
3. 预跑 check-gate.py P1（exit 2，主 Agent 自判）
4. git add {AGATE_WORKSPACE}/tasks/{Txxx}/（含 .state.yaml + 产出文件，若 .gitignore 忽略需 git add -f）
   ⚠️ 此时 .state.yaml 的 phase 保持 P1，不要提前写 P2——phase = 本 commit 的产出阶段
5. git commit -m "wf({Txxx}-P1): {摘要}"（phase=P1，P1 产出含 P1-requirements.md + P1-review.md）
6. P1 commit 完成后进入 P2：**phase 推进 P2 随 P2 产出 commit 一起**（P2-design.md + P2-review.md 就绪后），不是单独 phase commit

## 如果是重试

确认上一轮失败原因（BDD 不完整 / domains 声明错 / NEED_CONFIRM 未处理）
→ review 不通过时：analyst 修改需求 → 重派 requirements-review → 共享 retry 预算
→ 读 agate/rules/state-transitions.md 确认 retry 上限（P1 MAX=3）

## 前置条件

- [ ] P0-brief.md 完成（四字段齐全）

## 派发

- **角色**：analyst（`{agate_root}/assets/execution-roles/analyst.md`）
- **输入**：P0-brief.md（env_constraints / known_risks / executor_env）
- **输出**：P1-requirements.md
- **派发 prompt 模板**：`{agate_root}/assets/templates/dispatch-prompt.md`

## 复杂需求编排（模式 4，条件触发）

需求复杂（多来源 / 多模块 / 无法预先拆清范围）时，P1 可先派**侦察 subagent**（模式 4 先理解后拆，见 dispatch-protocol「派发编排机制」）读全貌后再拆需求：

1. 侦察 subagent 读 P0-brief + 相关上下文，产出拆分方案（拆成哪些子需求、各子需求的输入/产出/依赖）
2. 按方案派 analyst（并行或串行）分别产出需求基线
3. 合并时定义**合并语义**（在侦察产出中声明，P7 一致性检查依赖）：
   - **BDD 全局编号**：各子需求承接的 BDD 编号全局唯一（`#### BDD-NN:`），不允许各子需求各自从 1 编号
   - **包归属去重**：每个 BDD 明确归属唯一包，跨包的共享件单独列出，不允许两个子需求各写一份

## 产出规格

P1-requirements.md 必须包含：
- BDD 验收条件（至少 1 条，Given/When/Then 格式）
- `domains:` 声明（backend / frontend / mcp / security）
- `packages:` 声明（受影响的包/模块）
- `risk_level:` 声明（low / medium / high）→ 决定 P2 评审强度
- `ceremony:` 声明（thin / standard / full）→ 仪式深度档位（可选，缺省 standard，fail-closed：不声明或声明要素不满足一律按 standard 处理，不做薄化）
- `phases:` 裁剪声明（跳过哪些阶段 + 理由）
- `judge:` 启用声明（RM-AG0039 强制）：机制后新任务（P1 `created` ≥ `judge_required_since`，见 `agate/rules/dispatch.yaml`）P1 初始化须在 `.state.yaml` 写 `judge.enabled: true`——check-gate P1 机械校验（缺失/未启用 → exit 1）；历史任务（created < 截止或未声明）缺块 → 跳过
- `capability_requirements:` 能力需求声明（available / supplementable / GAP 三态）
- 无未决 `[NEED_CONFIRM]`（有则 PAUSED）；无待确认项时写 `[NO_NEED_CONFIRM]`

`risk_level`/`phases`/`packages`/`domains` 写在文件头 **frontmatter**（`---` 分隔块），不写正文。
**可直接复制的完整样例**：
```yaml
---
phase: P1
task_id: TAG0001           # 替换为实际任务编号
type: problems
parent: P0-brief.md
trace_id: T001-P1-20260101 # {task_id}-P1-{YYYYMMDD}
status: draft
created: 2026-01-01
agent: analyst
# ── v2.0 机器字段 ──
risk_level: low             # low / medium / high，必填
ceremony: standard          # thin / standard / full，可选；缺省 standard（fail-closed）
phases: [P1, P4, P5, P6, P8]   # list of P\d+，必填
packages: [pkg-a]           # list，必填
domains: [backend, frontend]  # list，必填
# 可选字段：override / implicit_coupling / coupling_checklist / internal_only /
# internal_only_reason / 跳过风险 / design_trivial / follows_existing_pattern
# ── RM-AG0039 judge 启用声明（写在 .state.yaml，非 P1 frontmatter）──
# 机制后新任务（P1 created ≥ judge_required_since，rules/dispatch.yaml "2026-08-22"）必须
# 在 .state.yaml 写 judge.enabled: true——check-gate P1 机械校验，缺失/未启用 → exit 1
# ── v2.0 refactor 任务类型声明（可选，缺省 = 功能任务）──
# change_type: refactor   # 当前仅支持 refactor；枚举非法值由 frontmatter schema 拦截
# ── TAG0007 项目阶段声明（可选，缺省 = established，向后兼容）──
# project_phase: bootstrap   # bootstrap（0→1 新项目）/ established（既有项目，缺省值）；
#                             # bootstrap 时 P2 architect 需额外产出 P2-skeleton.md（骨架声明）
# ── TAG0006 UI/UX 渲染形态声明（可选，presence 语义：缺失 = 常规布局型默认，不红基线）──
# ui_render_shape: render_component   # str，规范形态值：layout（布局型）/ render_component
#                                     # （渲染组件型，仅举例 OpenGL/WebGL/Canvas/图表/模型/特效/
#                                     #  地图/数字地球）/ temporal_effects（时序特效型）；开放集合可扩
# ui_ux_dimensions: [渲染正确性, 动效时序]  # list，从 UX 分类框架选适用维度；渲染组件/时序特效
#                                     # 类形态必填，常规布局型可省略
# ── v2.0 标记"已解决/已确认"状态（可选，仅标记存在时写）──
# need_confirm_resolved: []   # list[str]：已解决的 NEED_CONFIRM 项描述（逐条匹配正文）
# suggest_resolved: []        # list[str]：已采纳的 SUGGEST 项描述
# scope_resolved: []          # list[str]：已解决的 SCOPE+ 项描述
---
```

**UX 类别 BDD 与分类框架（domains 含 frontend 时必做）**：frontend 任务的 P1 必须含至少一条
UX 类别 BDD，并按实际 UI/渲染形态声明 `ui_render_shape` + 从 **UX 分类框架**（布局结构/
渲染正确性/交互行为/动效时序/视觉呈现等示例性开放集合）选 `ui_ux_dimensions` 维度，类别写入
BDD 标题后缀（如 `#### BDD-3: 渲染正确性：...`）。判据必须可量化（渲染正确性 → 渲染结果对比 +
diff 阈值或输出断言；时序 → 帧/时间戳对齐；动效 → 过渡/动画关键帧与结束状态断言；手势交互 →
动作输入的坐标/参数量化），禁主观词。缺失形态声明/维度选择/UX BDD → requirements-review 打回，
P1 gate 在"声明了形态但维度为空"或"维度不在分类框架且未在 BDD 标题声明"时 exit 1。

**NEED_CONFIRM 分级**：
- `[SUGGEST: 推荐 X，理由 Y]` - 有倾向但求确认。主 Agent 可自行采纳倾向（除非涉及破坏性变更/业务方向），不必问用户
- `[NEED_CONFIRM]` - 真无方向需人定夺。阻塞推进，主 Agent 问用户

## ceremony fail-closed 声明 checklist（TAG0019，BDD-7/8/9）

`ceremony:` 声明仪式深度档位（thin / standard / full），缺省 standard（fail-closed——不声明或声明要素不满足一律按 standard 处理）。声明 **thin**（薄仪式）时，P1 必须连同以下四要素一起声明，缺一 → check-routing exit 1，档位回退 standard：

1. **申请**：`ceremony: thin` 显式声明
2. **逐信号 checklist**：`coupling_checklist: [...]` 流式声明（判据 `^coupling_checklist:\s*\[`，复用 check-pruning）
3. **跳过风险评估**：`跳过风险:` 声明（复用 check-pruning 判据）
4. **P5/P6 保留**：`phases` 含 P5 与 P6（薄化仪式不薄化验证，P5/P6 由 check-routing / check-pruning 双闸兜底）

不声明（存量/新任务缺 ceremony 字段）→ standard，不拦截。`ceremony: full` 的任务 `phases` 必须含 P7（P7 不可裁，缺失由 requirements-review 审声明拦截，BDD-14）。

### M3 验收锚度量协议（BDD-12，机制文档供提取）

thin 档跳过 LLM 评审的 M3 验收锚四要素：

1. **评审轮数**指标：任务在 P2/P4 阶段派发的 LLM 评审 subagent 轮数（含重试轮）
2. **真实发现数**指标：评审产出中被采纳或阻止了真实问题的条数（排除非阻塞建议、排除机械检查可抓项）
3. **TAG0018 基线值**：4 场 LLM 评审 ≈0 净收益（17 条非阻塞 + 1 条真实发现且机械检查可抓）
4. **不达标决策规则**：「LLM 评审真实发现 ≈ 0 且机械 gate 已覆盖 → 回滚 standard」

## 同类扫描（强制节）

需求基线必须含一次**同类扫描**结论——被报告的那一处几乎从来不是唯一的一处。P0 卡片的「同类/影响面预判」给出粗粒度量级，P1 在此基础上把清单做实：

1. **扫描动作**：对问题涉及的关键符号（函数名、字段名、配置键、协议节标题、错误文案）用 grep/rg 扫全仓，记录**命中数量 + 文件清单**
2. **逐条判定**：每个命中标"本次处理 / 本次不处理 + 理由"。本次不处理的同类实例要么进 roadmap，要么写清为何不构成同一问题
3. **回归拦截**：若同类问题未来还会新增（不是一次性修完的存量），需求里要声明拦截手段（新增测试 / gate 脚本 / 文档约定），并转成对应 BDD
4. **结论落盘**：扫描结论写进 P1-requirements.md 正文（不是只写在 progress 里）；即使结论是"已确认只此一处"也要显式写出，空白不算做过

同类扫描缺失 → requirements-review 打回（"只修被报告的那一处"是 agate 反复复发的反模式）。P2 的「影响面梳理」在本节结论上继续做候选方案级的影响域分析，三处（P0 预判 / P1 同类扫描 / P2 影响面梳理）同源、逐级细化，不重复劳动。

## verification_env vs supplementable 边界判断树

`capability_requirements` 三态（available / supplementable / GAP）和 `verification_env`（运行环境声明）经常被混用——TAG0009 的 11.7 小时就是把一个环境问题错标成 `supplementable` 导致的。P1 声明时按下面的判断树走：

```
先问：缺的是能力还是环境？
├─ 缺的是「agent 侧的能力」（看不见图 / 不会用某工具 / 没有某技能）
│   └─ 走 capability_requirements 三态：
│      ├─ 当前就有 ................................. available
│      ├─ 当前没有，但能通过派发子角色 / 注入 skill / 换工具补上 ... supplementable
│      │   （必须在需求里写清补充方式，否则等同 GAP）
│      └─ 当前没有且补不上 ......................... GAP（阻塞，PAUSED 交人工）
└─ 缺的是「运行环境」（服务没起 / 端口没通 / 数据库没建 / 依赖没装 / 平台不支持）
    └─ 走 verification_env 声明（不是 supplementable）：
       ├─ 环境可由主 Agent 用标准操作准备好 → P1 声明 verification_env，
       │   由主 Agent 按 dispatch-protocol.md「环境准备职责边界」统一准备
       └─ 环境本质不可得（权限/凭据/平台原生不支持）→ 这是不可重试类，
           按 dispatch-protocol.md「verification_env 失败处理协议」立即升级人工
```

**判别口诀**：换个更强的模型/角色就能做 → 能力问题（supplementable）；换谁来做都得先把服务起起来 → 环境问题（verification_env）。**把环境问题标成 `supplementable` 属于机制误用**，不算"环境故障"，不消耗验证轮次预算，应立即改正声明方式。

**环境验证轮次预算占位声明位**：声明了 `verification_env` 的任务，P1 需求里留一行轮次预算占位（默认止损轮次 = 2 轮，与阶段 `retries[Pn]` 独立计数），供 P5/P6 派发时由主 Agent 在 dispatch-context 中接续记录"当前第几轮 + 历次已排除假设"。数值与完整规则的权威定义在 dispatch-protocol.md「verification_env 失败处理协议」，本卡片不重写：

```yaml
verification_env: "debug server http://127.0.0.1:3001 + tests/fixtures/test.db"
verification_env_budget: "止损轮次 2（独立计数，不占 retries[P5]）；轮次追踪由主 Agent 在 dispatch-context 记录"
```

## P0-brief 时效性质疑

analyst 拿到 P0-brief 后不默认它仍然成立——立项与实际启动之间可能已经漂移（跨会话恢复、任务搁置后重启、从 PAUSED 恢复）。P1 阶段必须做一次时效性质疑，判据（严重 3 条 / 轻微 2 条）的权威定义见 P0 卡片「P0-brief 时效性自检（漂移判据）」，本节只定标记规则与处理方式：

**标记格式**（行首声明，一个漂移点一行，必须写出**具体漂移点**，不允许只写标记裸词）：

```
[P0_STALE: executor_env 声明的 CI 镜像已下线，当前实际跑在 ubuntu-24.04]
[P0_STALE: task 描述的 .sh 路线已全量 Python 化，目标方案本身不再成立]
```

**阻塞 / 记录二选一**（按漂移严重程度分流，不允许"既不阻塞也不记录"地含糊推进）：

| 漂移程度 | 处理 | 落盘 |
|---------|------|------|
| **严重**（命中 P0 卡判据 1-3 任一条） | **阻塞**：停止 P1，回 P0 重新立项 / 重做可行性分析 | P1-requirements.md 写 `[P0_STALE: 具体漂移点]` + 说明为何判定严重；主 Agent 按 PAUSED 或回 P0 流程处理 |
| **轻微**（不命中判据 1-3） | **记录**：更新 P0-brief 对应字段后继续 P1，不阻塞 | P1-requirements.md 写 `[P0_STALE: 具体漂移点]` + 已更新哪个字段 |
| 无间隔 / 已核对无漂移 | 继续 | 写一行"已核对 P0-brief 时效性，无漂移"，空白不算做过 |

## gate 规则

check-gate.py P1 → P1-review.md 存在 + status:approved + agent≠main + 含 BDD 编号锚点 → exit 2（BDD 编号格式为 `#### BDD-NN:`）；缺 P1-review.md / agent=main / 无锚点 → exit 1
P1 评审不可裁——所有任务都走独立 requirements-review，无例外

## 推进条件（全部满足才写 phase: P2）

- [ ] P1-requirements.md 含 BDD ≥1 条
- [ ] 含「同类扫描」结论（命中清单 + 逐条处理判定，"只此一处"也要写出）
- [ ] P0-brief 时效性已质疑：无漂移则记录已核对；有漂移则含 `[P0_STALE: 具体漂移点]` 且已按阻塞/记录二选一处理
- [ ] domains / packages / risk_level / phases 已声明
- [ ] 无 [NEED_CONFIRM] 标记
- [ ] 无 status: GAP（supplementable 不阻，GAP 阻）
- [ ] P1-review.md status: approved（agent≠main，含 BDD 编号锚点）

## 常见错误

1. **BDD 写成技术实现而非用户行为**：BDD 应该描述"用户能看到什么/系统应该做什么"，不是"调用哪个 API"
2. **domains 声明不全**：漏了某个受影响域 → P2 不派该域的评审 → 实现方向错误
3. **capability_requirements 漏声明**：P6 验收时才发现需要但不可用的能力 → 返工。**frontend 任务
   漏声明 vision 视觉能力条目（need 含 visual/vision）→ P1 gate exit 1 硬拦**（check-gate.py
   `_gate_p1_vision_capability`）；声明形态但漏选维度 / 形态声明与 UI/渲染形态不符 →
   同样 exit 1
4. **gate 不过 ≠ 你失败了**：红灯指向工作/设计的问题，不指向你。正确动作是诊断→退回/重试/PAUSED，不是修改产出让它变绿。

## 下游影响

- P2 设计依赖 domains + risk_level 决定评审角色
- P6 验收逐条对照 P1 的 BDD（PASS/FAIL 总数必须 ≥ P1 BDD 总数）
- P7 一致性检查依赖 packages 声明做跨文件交叉核对

## 评审

P1 评审通用必有（所有任务都走 requirements-review），P2/P4 评审是 C8 域触发（见 review-mapping.md）——二者在"是否通用"上不对称，仅在"独立 subagent、agent≠main"上类比。P1 评审不可裁剪。
review 不通过 → analyst 修改需求 → 再 review（⑩迭代循环），直至 approved。

> 完成 → 读 phase-cards/P2-design.md


## P1 基线保护

P1-requirements.md 是需求基线，后续阶段（P2-P8）不应直接修改。如需变更（如 P4 发现 BDD 矛盾需补充注释），必须：
1. 主 Agent 显式批准
2. 在变更处标注 `[BASELINE_CHANGE: 理由]`
3. 不改 BDD 的 Given/When/Then 语义（只补充注释/优先级说明）
4. **隐含扩展同样要授权**（TAG0025 教训）：P3/P4 的实现细节若事实上扩展了 P1 验收标准的范围（新增豁免条件、放宽/收紧某条 BDD 的判定边界等），即使当下未产生"矛盾"，也视为需要`[BASELINE_CHANGE]` 授权的情形——授权内容必须回写 P1-requirements.md 正文，不得只存在于下游阶段的 dispatch-context 口头引用中
<!-- AGATE_CARD_END -->

<objective_info>
### A. 路径拓扑（worktree 场景）
- worktree 根（project_root）= `/home/kity/oclab/agateon/.worktrees/agate-TAG0027`（含 .git，分支
  `feat/TAG0027-orchestration-semantics`）
- AGATE_WORKSPACE = `/home/kity/oclab/agateon/.worktrees/agate-TAG0027/agate-workspace`
- 任务目录 = `agate-workspace/tasks/TAG0027-orchestration-semantics/`
- 协议本体（改造对象）= worktree 的 `agate/`；主 checkout `/home/kity/oclab/agateon/agate`
  禁止改动（`~/.agate` 软链指向它，是稳定版 gate 工具）
- 编排/派发类工具（agate-inject-card.py / agate-render-dispatch-prompt.py 等）调用用
  `~/.agate/scripts/` 稳定版（TAG0016 教训：worktree 相对路径调用会读到正在被改的协议副本）

### B. 测试基线（P0-brief §2 已核实）
- 全量 pytest 1311 passed（串行：unit 1191 + regression 28 + integration 92）
- count-tests collect-only 口径 = 1335 用例（2026-09-02 worktree 实测）
- consistency 0 ERROR（--strict-errors-only；324 存量 WARNING 为历史叙事死链，DEBT0012 语义）
- 存量并行偶发 1 例（`test_agate_next_card.py` sha256 漂移，xdist 调度干扰；CI 用 --reruns 1
  兜底）——新增用例若触碰 agate-next-card.py 渲染注意串行验证
- 环境：python 3.12.3 / pyyaml 6.0.1 / pytest 9.0.3 / ruff（~/.venvs/agate-dev/bin/ruff）

### C. 现状锚点（主 Agent 2026-09-02 实测，供查证起步；analyst 须核实关键行号）
- `rules/phases.yaml`：现有 `- id: P0`…`P8` + `P6.5` 条目（92-101 行，带"非独立 phase"注释
  于 ~100 行）；**无 next/retreat 字段**；每条目含 id/name/exec_role/outputs/gates/retry_cap/
  task_fields；schema `rules/schema/phases.schema.json` 顶层 properties 仅
  `['schema_version', 'phases']`，需在 JSON Schema 层新增 next/retreat 字段声明
- `state-machine.md` 转移锚点：74-78（P6.5 挂载于 P6→P7，非独立 phase 值，.state.yaml phase
  保持 P6 至 P7）；95-99（PAUSED 汇合：NEED_CONFIRM / GAP / PROD_TOUCHED / retry>=MAX）；
  132-133（P5 failed → P4 retry+1）、148（P6 FAIL → P4 retry+1）、139（P6 exit 2 + provenance
  exit 0 → P6.5 judge 复核）、151（P6.5 verdict exit 0 → P7）
- `check-gate.py` 头注释：`exit 0 = gate 通过; exit 1 = gate 未通过; exit 2 = 需主 Agent
  自判（含动态 gate_commands 或语义判断）`；第 3 参 OLD_PHASE 提供且大于当前 → 判定"回退
  抵达"直接 exit 2
- `check-state-transition.py`：`exit 0 = 合法; exit 1 = 非法`；P2.3 phase 跳变合法性 /
  P2.4 retry 超限→PAUSED / P2.5 回退跳变≥2→强制 PAUSED；MAX_RETRY_MAP 从 agate_common
  导入（单一数据源）
- `agate-retreat-to.py` / `agate-retreat-state.py` 已存在（回退侧 CLI 不是缺口）
- `loop-orchestration.md`：档位 A（手动逐步，17 行）/ 档位 B（半自动，30 行）/ 档位 C
  （全自动 /loop，46 行）；227-243 行"每次阶段 commit 都要先过 pre-commit hook" + gate 处理
  流程 + 硬中断点（PAUSED 而非 retry）
- `dispatch-protocol.md`：五模式定义位于 ~511-519 行（模式 1 单发 / 2 静态拆批 / 3 并行 /
  4 先理解后拆 / 5 串行链）
- `check-p6-provenance.py` 审计 2（~318-355 行）：现状靠 dispatch-context **物理占位符块**
  （`<!-- AGATE_CARD_START -->`…`<!-- AGATE_CARD_END -->`）排除卡片内容（P6 卡片本身含
  PASS/FAIL 模板字样）——A1 改渲染产物扫描的对象与排除锚点
- `check-structure-consistency.py` S-1/S-2（行 7-11）：S-1 YAML→md 以 WORKFLOW.md 阶段总览
  表为 md 侧锚点；S-2 md→YAML 反向
- 平台名 grep（worktree agate/*.md）：命中 9 文件 = adr.md / AGENTS.md / dispatch-protocol.md
  / loop-orchestration.md / platform-notes.md / role-system.md / SETUP.md / UPGRADING.md /
  WORKFLOW.md；`WORKFLOW.md:141`「已知适用环境：」表（141-148 行，元信息豁免区）；
  **全协议 0 处「实现注记」标记**（Phase 3/4 全新引入）
- `agate-inject-card.py` CLI：`agate-inject-card.py PHASE TASK_DIR`（两参简单接口，主 Agent
  手工派发路径的现状）

### D. 同类/影响面扫描线索（analyst 须补全并逐条判定）
- `next` / `retreat` 字段：全仓 grep 确认 phases.yaml / phases.schema.json / state-machine.md /
  WORKFLOW.md / check-structure-consistency.py 现有引用——确认"首增 + 须纳入哪些既有检查"
- 平台名污染：对上述 9 个命中文件逐文件判定语义小节 vs 实现注记 vs 元信息（本任务 Phase 3
  清理面 + Phase 4 机械化的扫描基线——机械检查上线前需存量先清或豁免，否则新检查即全红；
  记录命中数量与段落清单，判定"本次处理/不处理 + 理由"）
- `agate-inject-card.py` / `agate-card-inject.py` / `agate-render-dispatch-prompt.py`
  消费方：全仓 grep（scripts/ + agate-workspace/）确认谁在调、手工场景有哪些（Phase 4 两路
  并存的存量用法清单）
- `check-p6-provenance.py` 审计 2 的物理占位符锚点：grep `AGATE_CARD_START` 全仓命中数
  （dispatch-context 模板 / 注入脚本 / 审计脚本 / 存量任务 dispatch-context）——A1 改造后
  哪些仍靠物理锚点
- `exit2-resolution` 相关：全仓 grep 确认无既有机制（首增）
- `agate next` / `agate advance` 命名冲突：全仓 grep 确认无既有同名命令/脚本
- judge / P6.5 复核范围扩展：确认 check-judge-verdict.py / check-events.py 现状（exit2-resolution
  产物纳入复核范围的挂载点）

### E. judge 启用
- `.state.yaml` 已写 `judge.enabled: true`（RM-AG0039 强制，机制后新任务 created 2026-09-02 ≥
  2026-08-22）——P1-requirements.md frontmatter 无需重复，正文不得与 judge 机制冲突
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
