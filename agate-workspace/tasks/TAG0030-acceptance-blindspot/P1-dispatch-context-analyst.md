---
phase: P1
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0030
role: analyst
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

产出 `P1-requirements.md`：把 P0-brief 的一句话任务（验收盲区机制批，RM-AG0057 四类 + DEBT0024/25/26）展开为含 BDD 验收条件（计划 ≥15 条）的需求基线，供 P2 设计与 P6 验收使用。范围严格锁定 P0-brief 的 scope 四 phase：

- **Phase 1（测试副作用/环境还原 gate，RM-AG0057-①）**：P3 卡补"创建型测试清理钩子"要求（创建即注册、无条件删除、接受 200/204/404——afterEach 清理队列模式）；P6 补 post-test 环境残留检查步骤（快照比对或清理钩子验证）；dispatch-context 模板补对应要求
- **Phase 2（P1 人工体验路径验收节，RM-AG0057-②）**：P1 卡/analyst 角色补"人工体验验收"节——凡涉及用户可见页面且数据源（seed）影响其内容，强制补"Given seed 数据 → 页面有内容"BDD
- **Phase 3（plan-design-review 形态驱动化，RM-AG0057-③）**：`plan-design-review.md` 改形态驱动评分——先读受评任务 `ui_render_shape` 再加载对应维度组评分细则（布局型 → 布局/交互/视觉三组；渲染组件型 → 渲染正确性/动效时序）；每个启用维度要求布局方案 ≥2 候选 + 权衡（架构级 candidate_count 下沉 UI 布局层）；渲染组件型评审 checklist 对接 architect 渲染正确性 checklist
- **Phase 4（视觉契约断言收录 + TAG0027 三连，RM-AG0057-④ + DEBT0024/25/26）**：视觉契约断言（DOM 度量：宽度/高度/对齐/重叠/溢出）收录为可表达子集，P2 视觉 checklist/P6 指南提及；P3 测试夹具真实 gate 语义要求（DEBT0024）；新 CHECK 上线前全量扫描流程（DEBT0025）；大任务拆小派发指引（DEBT0026，核对 TAG0028 自主再派发落地后的剩余缺口）

### 约束

1. **范围锁定**（P0-brief 核心约束 6）：若需求分析发现需改动超出 P0-brief 锁定范围（如必须重构形态声明机制本身、必须改 check-gate.py 的既有判据、必须实现清理钩子运行器），立即停下报告主 Agent，不擅自扩范围。
2. **不破坏已有协议语义**（核心约束 2）：plan-design-review 保持 0-10 评分输出格式 + `status` 字段（门槛读 status），只加形态分组内部逻辑；P1/P2 形态声明机制（已有 ui_render_shape/ui_ux_dimensions，TAG0006 交付）**不重构**——本任务只让评审角色"读形态"。
3. **卡文件批量改动用 grep 断言审计 TDD 策略**（核心约束 3 / TAG0027 教训）：不为每处小改动单独 TDD，先写"断言审计"（grep 协议文件确认新增要求存在）再批量改。P1 需求里要把可 grep 的锚文本（协议文件必须出现的关键词/句式）作为 BDD 的可验证断言载体——让 P4 implementer 知道要写断言审计测试。
4. **视觉契约是"可表达子集"**（核心约束 4）：只收可量化 DOM 度量（宽度/高度/对齐/重叠/溢出），不收主观视觉。P2/P6 指南要防"所有视觉都必须断言"误解。
5. **DEBT0026 与 TAG0028 §4 边界**（核心约束 5）：本任务只补派发模板默认指导（>5 文件/大文档任务按体量拆小），不重复实现内部自主拆。**先核对 TAG0028 交付**（role-system.md「子派发权限边界」节 + dispatch-protocol.md §4 自主再派发节）再写 DEBT0026 缺口 BDD——dispatch-protocol.md 行 989-1003 已有 §4.1 两条边界 + judge 例外 + 五模式编排并存声明，须确认剩余缺口是"派发模板缺 >5 文件拆小默认指导"。
6. **同类扫描不可省**（P1 卡片强制节）：下方客观查证信息 F 已给扫描线索，按 P1 卡片「同类扫描」节逐条判定"本次处理/本次不处理 + 理由"并写进 P1-requirements.md 正文。
7. **P0-brief 时效性质疑必做**：P0-brief 写于 2026-09-03，主 Agent 启动前已核对无漂移（TAG0028 已完成 READY 属预期前提——P0-brief Phase 4 明确要求"核对 TAG0028 落地后的剩余缺口"，不是失效）；analyst 仍须独立质疑一次并写一行结论（"已核对 P0-brief 时效性，无漂移"或 `[P0_STALE: 具体漂移点]`），空白不算做过。
8. **BDD 可二值判定**：每条 BDD 的 Given/When/Then 必须可明确 PASS/FAIL，禁止中间态。BDD 是"协议机制行为"视角（读协议文件是否含该要求 + 断言审计测试是否覆盖 + check-*.py 是否校验），不是"调用哪个函数"的实现细节。BDD 编号连续不跳号。
9. **frontmatter 声明参考**（本任务为协议文档面改造，参考先例 TAG0006/TAG0024/TAG0026 的包/域声明）：
   - `packages`: 建议按受影响协议文件面拆（如 `[agate-phase-cards, agate-assets-roles, agate-assets-templates]` 或更细粒度），与 P7 一致性检查配对
   - `domains`: 本任务不产出业务 UI，属协议/工具链改造——用 `[backend]`（TAG0024/26 先例）不含 frontend（无用户可见页面产线）；**若你认为某 Phase 落点属 frontend 域须在正文声明理由**
   - `risk_level`/`ceremony`/`phases`：按实际复杂度声明（协议文档面批量改动，参考 TAG0026 risk_level: high + ceremony: standard 先例）；本任务改造面是纯文档/模板/卡（不新增脚本运行时行为面），可裁的只有"若 P4 无新脚本仅文档+测试断言"则 P3 视 TDD 策略定
10. **SELF-GATE 触发已知**：改 `agate/phase-cards/*.md`（P1/P3/P6 卡）+ `plan-design-review.md` + `dispatch-context.md` + `analyst.md` 触发 SELF-GATE（commit message 须含 self-gate-review/skip）；协议文档变更须跑 `check-protocol-consistency.py` 确认无 ERROR——需求 BDD 可含"consistency 0 ERROR"类回归防线。
11. **关联 DEBT0024/25/26 的 closure 落点**：DEBT closure_criteria 要求"协议开发约定写明 X"，BDD 应把"约定写明"转成可 grep 断言（如"dispatch-protocol 派发模板含拆小默认指导"→ grep 锚）。

### 上游关联

- P0-brief.md 已锁定 scope 四 phase + out-of-scope（gate 命令解析器归 TAG0029、check-gate 健壮性归 TAG0031）+ known_risks 四条 + env_constraints（SELF-GATE 触发面、双工作区纪律、consistency --strict-errors-only）
- RM-AG0057 roadmap 条目（agate-workspace/roadmap/roadmap.md，含 4 类缺陷完整查证）是 BDD 清单的直接来源
- DEBT0024/25/26 条目（agate-workspace/debt/tech-debt.md 行 844-909，含 evidence + closure_criteria）是 Phase 4 BDD 的 closure 判据来源
- TAG0028 交付（role-system.md「子派发权限边界」节、dispatch-protocol.md §4 自主再派发节行 ~989-1003）是 DEBT0026 剩余缺口核对的边界依据
- 形态体系现状（TAG0006 交付）：analyst.md / architect.md / verifier.md / test-designer.md / requirements-review.md / P1/P2/P6 卡 / state-machine.md / rules/state-transitions.md 已全链引用 ui_render_shape/ui_ux_dimensions——**plan-design-review.md 是唯一未接形态体系的评审角色**

### 输入文件（按顺序读）

1. `agate-workspace/tasks/TAG0030-acceptance-blindspot/P0-brief.md`
2. `agate-workspace/roadmap/roadmap.md`（重点 RM-AG0057 行——4 类缺陷完整查证）
3. `agate-workspace/debt/tech-debt.md`（重点 DEBT0024 行 844-864 / DEBT0025 行 866-886 / DEBT0026 行 888-908——含 closure_criteria）
4. `agate/assets/review-roles/plan-design-review.md`（Phase 3 改造对象——现状 38 行固定 7 维）
5. `agate/assets/execution-roles/analyst.md`（Phase 2 改造对象之一；同时是你要遵循的角色定义）
6. `agate/assets/execution-roles/architect.md`（形态声明/UI 设计节/candidate_count 语义——Phase 3 对接对象）
7. `agate/assets/execution-roles/test-designer.md`（渲染组件形态要求——Phase 1/4 关联）
8. `agate/assets/execution-roles/verifier.md`（视觉证据形式——Phase 1/4 关联）
9. `agate/assets/templates/dispatch-context.md`（Phase 1/4 改造对象——模板现状 61 行）
10. `agate/phase-cards/P1-requirements.md`（Phase 2 改造对象；同时是本阶段卡片）
11. `agate/phase-cards/P3-tdd.md`（Phase 1 改造对象——现状 step 0 只跑 capture-env-baseline）
12. `agate/phase-cards/P6-acceptance.md`（Phase 1/4 改造对象——现状无 post-test 残留检查）
13. `agate/dispatch-protocol.md`（重点「派发编排机制」行 ~518-573 + §4 自主再派发节行 ~989-1003——DEBT0026 边界核对）
14. `agate/role-system.md`（子派发权限边界节——DEBT0026 边界核对）
15. `AGENTS.md`（项目约定，worktree 根）
16. `agate/assets/execution-roles/vision-analyst.md`（视觉契约断言的下游消费方现状）

### 产出文件字段

用 `FILE={AGATE_WORKSPACE}/tasks/TAG0030-acceptance-blindspot/P1-requirements.md agate-md-field-set --list`
查看本阶段应填字段；`FILE=... agate-md-field-set <key> <value>` 逐个写入；写入失败照错误提示
修正，不要手写 frontmatter；仍失败则报告主 Agent，不要绕开 set。

frontmatter 必填：phase=P1, task_id=TAG0030, type=problems, parent=P0-brief.md,
trace_id=TAG0030-P1-20260904, status=draft, created=2026-09-04, agent=analyst,
risk_level / ceremony / phases / packages / domains 按产出规格声明（judge 已由主 Agent 在
.state.yaml 写 enabled: true，无需在 frontmatter 重复）。
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
- worktree 根 = `/home/kity/oclab/agateon/.worktrees/agate-TAG0030`（本任务 project_root，含 .git 文件）
- AGATE_WORKSPACE = `/home/kity/oclab/agateon/.worktrees/agate-TAG0030/agate-workspace`
- 任务目录 = `agate-workspace/tasks/TAG0030-acceptance-blindspot/`（.state.yaml phase=P1, judge.enabled=true）
- 协议本体（改造对象）= worktree 的 `agate/`（主 checkout `/home/kity/oclab/agateon/agate` 禁止改动）
- 双工作区纪律：改代码/写产出在 worktree；跑 gate 用 `~/.agate` 稳定版；`check-protocol-consistency.py`
  **必须用 worktree 自己的**（`python3 agate/scripts/check-protocol-consistency.py --strict-errors-only`）；
  编排/派发类工具用 `~/.agate` 稳定版
- **注意**：本 worktree 中 `agate/` 是主 checkout 协议文件的完整副本（worktree checkout），
  你在其中读写的是 worktree 的 agate/（改造对象）；不要把 `~/.agate` 或主 checkout 当作改动目标

### B. RM-AG0057 四类缺陷查证（roadmap 行原文浓缩）
- ① 测试副作用/环境还原：peekview DEBT0008 实证 18 个残留团队污染共享 debug DB；BDD 只有正向路径，
  创建型 E2E 跑完不清理 → P6 全 PASS 时环境尚干净、残留验收后才暴露。agate 卡 P3 只有测试前失败
  基线（`agate-capture-env-baseline.py`），**无测试后残留检查/清理钩子要求**
- ② P1 人工体验路径验收节：peekview DEBT0009 实证 make debug-seed 后 Teams tab 空——排除 seed/数据
  改动时 BDD 全用 fixture 验收，"用户按文档 seed 后页面应有内容"成隐性无人验路径
- ③ plan-design-review 形态驱动化：形态适配机制已在 P1 analyst（ui_render_shape/ui_ux_dimensions
  声明）/ P2 architect（UI 设计节：渲染形态声明 + 维度选择 + 按形态 checklist）/ gate（_gate_p1_ui_shape）
  全链落地，**但 plan-design-review.md 未接形态体系**——固定 7 维评分 + 一行条件启用（渲染时序仅
  声明型启用），评审者只读角色文件会拿布局维度评 Canvas 渲染任务或漏评；P2 候选≥2 为架构级
  （candidate_count）不下沉 UI 布局层，"行 vs 卡"布局决策无候选权衡必审
- ④ 视觉契约断言收录：vision-analyst 是被动截图翻译，协议无"可量化 DOM 度量断言"（宽度/高度/对齐/
  重叠/溢出）概念——"dropdown ≥ trigger" 类可量化协调性无 BDD 表达机制

### C. 形态体系现状（TAG0006 交付，勿重构）
- P1 frontmatter 可选字段：`ui_render_shape`（layout / render_component / temporal_effects 开放集合）
  + `ui_ux_dimensions`（维度选择 list；渲染组件/时序特效类形态必填）
- 消费链：analyst.md 行 ~146/253-257 → architect.md 行 ~64-65/106（P2 UI 设计节声明必须与 P1 一致，
  gate 规范化值比对）→ P6 卡行 58-63（证据形式随形态选）→ rules/state-transitions.md 行 21/26
  （P1/P2 gate 拦截缺失）→ requirements-review.md 行 42-43（形态声明随任务适配）
- **plan-design-review.md 现状**（38 行）：评分维度 7 项——交互状态覆盖率 / AI Slop 风险 / 移动端
  考虑 / 可访问性 / 组件完整性 / 视觉设计（常规布局型启用）/ 交互设计细节（frontend 必评）/ 渲染
  正确性与时序（仅渲染组件/时序特效形态声明时启用）。七维边界注防 double count。**无"按 ui_render_shape
  加载维度组评分细则"机制**、**无"布局方案 ≥2 候选 + 权衡"要求**

### D. 视觉契约断言下游现状
- vision-analyst.md：定位"截图翻译成结构化视觉描述"，不主观评价；分析对象按渲染形态适配（布局型
  截图 / 渲染组件型 renders/ + diff 度量 / 时序型时序截图）；purpose=acceptance|design-review|regression
- P6 卡：UI 任务视觉证据按 vision 三态分档 + 渲染形态选形式；有 avg-hash 雷同截图降级；输入态/交互
  形态变化类 BDD 结论须附人工复核记录
- P6 卡行 152-155：md5 完全重复截图硬阻断；雷同截图优先改非截图证据
- **缺口**：无可量化 DOM 度量断言的表达/收录机制（宽度/高度/对齐/重叠/溢出——可在 E2E 里
  `getBoundingClientRect()` 断言）

### E. 测试基线（交接单 §9 已核实）
- 全量 pytest 全绿（worktree 基线）；consistency 0 ERROR（--strict-errors-only）
- shellcheck 0 error；count-tests 用例数不漂移
- 新增 pytest 用例覆盖：断言审计（grep 协议文件锁定新增要求）类测试——见约束 3

### F. 同类/影响面扫描线索（analyst 须补全并逐条判定"本次处理/不处理 + 理由"）
- `capture-env-baseline` / 环境基线：全仓 grep——命中 architect.md / UPGRADING.md / scripts/README.md /
  P4-implementation.md / P3-tdd.md / tests/README.md（Phase 1 须确认 P3 卡与 P4 卡都只讲测试前基线，
  无测试后残留检查；UPGRADING 是否需同步补"创建型测试清理钩子"迁移说明）
- `afterEach` / 清理 / 残留 / 副作用：phase-cards/ + assets/ 零命中（确认 Phase 1 缺口真实）
- `seed` / 人工体验 / fixture 验收：analyst.md / P1 卡 / P6 卡零命中（确认 Phase 2 缺口真实）
- `candidate_count`：命中 architect.md / task-files.md / UPGRADING.md / scripts/README.md / P2-design.md
  ——架构级候选数机制；Phase 3 须确认"下沉 UI 布局层"的落点（plan-design-review.md 评分细则内）
- `plan-design-review`：命中 rules/review-mapping.md / WORKFLOW.md / review-roles/plan-design-review.md /
  templates/dispatch-prompt.md / role-system.md / AGENTS.md / P2-design.md——改角色文件须确认
  review-mapping.md 是否引用其维度清单（P7 一致性 / review-mapping 交叉核对）
- `ui_render_shape` / `ui_ux_dimensions`：命中 analyst/architect/verifier/test-designer/
  requirements-review / P1/P2/P6 卡 / state-machine.md / rules/state-transitions.md / task-files.md /
  UPGRADING.md / LIMITATIONS.md——plan-design-review.md 是唯一评审角色未命中（Phase 3 核心证据）
- `vision` / `视觉`：P6 卡 / verifier.md / vision-analyst.md / dispatch-prompt.md——Phase 4 视觉契约
  断言的落点须与其对齐（P2 视觉 checklist / P6 指南）
- `子派发` / 拆小 / 拆批：dispatch-protocol.md 行 518-573（五模式编排 + 综合定级规则：high 必须拆分）+
  行 989-1003（§4.1 两条边界 + judge 例外 + 与五模式并存）——DEBT0026 剩余缺口核对（见约束 5）
- `_gate_p1_ui_shape` / check-gate.py：形态 gate 判据所在——Phase 3 BDD 不得要求改动既有判据

### G. judge 启用
- `.state.yaml` 已写 `judge.enabled: true`（RM-AG0039 强制，TAG0030 created 2026-09-04 ≥
  judge_required_since 2026-08-22）——P1-requirements.md 的 frontmatter 无需重复；正文不要与
  judge 机制冲突
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
