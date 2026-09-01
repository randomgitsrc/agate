---
phase: P1
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0026
role: analyst
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

产出 `P1-requirements.md`：把 P0-brief 的一句话任务（维护性反模式 gate，RM-AG0046）展开为
含 13 条 BDD 验收条件的需求基线，供 P2 设计与 P6 验收使用。范围严格锁定 G0 两条
（god-file 跨越 + fuzzy-boundary）落地 + check-gate.py **P4 三重门槛挂载** + known-violations
模板 + P4/P6 phase card 自查提醒 + pytest 覆盖 13 条 BDD。**只挂 P4，不挂 P6**。

### 约束

1. **挂载阶段必须是 P4，不是 P6**（v3 评审 B1 修正，血泪教训）：检测器数据源是
   `git diff --cached`，代码在 P4 阶段才 staged；P6 提交的是验收文档，`git diff --cached`
   已不含代码 diff → 挂 P6 是永远零命中的死代码。**所有 BDD 必须体现"P4 挂载"**，且必须含
   BDD-13（数据源与挂载阶段对齐验证：P4 commit 代码后 P6 只 commit 验收文档 → 验证检测器在
   P4 被调用时能读到代码 diff）。禁止出现任何"P6 挂载"或"P4/P6 均可"的措辞。
2. **三重门槛必须守住，不得退回"登记即放行"**（v3 评审 B3 修正，最深的一处）：known-violations
   登记的是"本任务自己引入的反模式"，与 known-failures（登记预存失败）语义相反。放行条件是
   「登记存在 + 数量对齐 + P4 评审 approve（agent≠main）」三者齐全。只要求"数量对齐"就放行
   是错误方向。BDD-7/8/9/10 逐条对应：7=登记缺失阻断、8=数量不足阻断、9=数量对齐但评审未
   approve 仍阻断、10=三重门槛全满足才放行。
3. **不新增第八道 provenance 审计**（v3 评审 B2 修正）：本次不改 `check-p6-provenance.py`，
   known-violations 登记内容不进现有七道审计范围。BDD-10 不得写"登记进审计"。
4. **阈值 N=1000 无实证依据**（来自 Cursor skill）：文档/配置必须明确"默认值仅供参考可配置"，
   不造成"协议断言该阈值"的错觉。配置路径是 `agate-workspace/maintainability.yaml`
   （**不用 `.agate/`**，ADR-009 界定该前缀是用户级命名空间）。
5. **fuzzy-boundary 正则集只覆盖 Python/TS**：其它语言（Go interface{}、Java
   @SuppressWarnings）不在本版范围，需求里明确写"协议参考实现覆盖 Python/TS，其它语言项目经
   gate_commands 自行补充"。禁止写"支持所有语言"这类超出范围的 BDD。
6. **移动代码假阳性是已知行为，不是缺陷**：不引入跨行移动检测。BDD-12 验证的是"含裸 except 的
   代码块被移动 → 判定为 violation（已知假阳性），known-violations 三重门槛能正常处理这种
   '合理但需登记+需评审确认'的场景"，不是验证"移动代码能被正确识别"。
7. **check-gate.py 是核心 gate，回归风险最高**：所有任务 P0-P8 都经它判定。gate_p4 新增一步须
   保持返回约定（1/2）与既有调用链兼容。这是需求层的约束，P2 设计细化。
8. **known-violations 模板复用 `count_kf_entries` 计数算法**（agate_common.py:1015-1017）：
   必须用 `| N |` 行首表格格式，P4 评审确认列不参与机械计数。这是 BDD-8 依赖的格式约定，
   P1 需求里把"模板格式与 count_kf_entries 对齐"写成显式要求。
9. **同类扫描不可省**：下方客观查证信息 D 已给出相关扫描线索，analyst 需按 P1 卡片「同类扫描」
   节要求逐条判定"本次处理/本次不处理 + 理由"并写进 P1-requirements.md 正文。
10. **P0-brief 时效性质疑必做**：P0-brief 已自检"已核对，无漂移"（立项与计划定稿同日），但
    analyst 仍须独立质疑一次并写一行结论（"已核对 P0-brief 时效性，无漂移"或 `[P0_STALE: 具体漂移点]`），
    空白不算做过。
11. **范围锁定**：若分析发现需改动超出 P0-brief/设计文档锁定范围（如必须动 G1/G2、必须新增
    第 8 道审计、必须动 RM-AG0022 结构化层），立即停下报告主 Agent，不擅自扩范围。
12. **BDD 可二值判定**：每条 BDD 的 Given/When/Then 必须可明确 PASS/FAIL，禁止中间态。
    BDD 是"系统行为"视角（check_maintainability 函数返回值 / check-gate.py exit code /
    模板文件存在性 / 配置生效性），不要写成"调用哪个函数"的实现细节。

### 上游关联

- P0-brief.md 已锁定范围与 known_risks 七条（check-gate 消费方、挂载阶段对齐、阈值无实证、
  fuzzy-boundary 语言覆盖、移动代码假阳性、known-violations 语义、模板格式）
- 落地计划 `docs/design-notes/rm-ag0046-maintainability-gate-plan.md`（v3，2026-08-30 独立评审
  修复 2 BLOCKER + 1 WARNING + 2 NIT 后定稿）是**本任务 BDD 清单的直接来源**——其第 4 节
  「BDD 验收标准」给出了 13 条 BDD 的完整语义，P1 需逐条转为 Given/When/Then
- 设计地基 `docs/design-notes/design-maintainability-gate.md`（G0-G3 分级 + 决策 1/2/3：
  diff 驱动 / 跨越≠超过 / 判定权在 gate）提供模式层语义
- check-gate.py `gate_p4`（agate_common 路径见下方客观查证信息）是挂载点现状
- known-failures 机制（`agate_common.count_kf_entries` + P5 判定）是三重门槛中"数量对齐"
  的算法来源

### 输入文件（按顺序读）

1. `agate-workspace/tasks/TAG0026-maintainability-gate/P0-brief.md`
2. `docs/design-notes/rm-ag0046-maintainability-gate-plan.md`（重点第 0/2/4/4.1 节，BDD 清单来源）
3. `docs/design-notes/design-maintainability-gate.md`（重点 §2/§6 决策 1/2/3）
4. `agate/scripts/check-gate.py`（重点 `gate_p4` 函数 ~870-927 行 + P5 known-failures 判定 ~972-981 行）
5. `agate/scripts/agate_common.py`（重点 `count_kf_entries` ~1015-1017 行）
6. `agate/assets/templates/known-failures-template.md`（登记模板格式参照）
7. `{agate_root}/WORKFLOW.md`「需求与验收机制」一节（按需）
8. `AGENTS.md`（项目约定）

### 产出文件字段

用 `FILE={AGATE_WORKSPACE}/tasks/TAG0026-maintainability-gate/P1-requirements.md agate-md-field-set --list`
查看本阶段应填字段；`FILE=... agate-md-field-set <key> <value>` 逐个写入；写入失败照错误提示
修正，不要手写 frontmatter；仍失败则报告主 Agent，不要绕开 set。
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
- worktree 根 = `/home/kity/oclab/agateon/.worktrees/agate-TAG0026`（本任务 project_root，含 .git）
- AGATE_WORKSPACE = `/home/kity/oclab/agateon/.worktrees/agate-TAG0026/agate-workspace`
- 任务目录 = `agate-workspace/tasks/TAG0026-maintainability-gate/`
- 协议本体（改造对象）= worktree 的 `agate/`（主 checkout `/home/kity/oclab/agateon/agate` 禁止改动，
  `~/.agate` 软链指向它，是稳定版 gate 工具）
- 双工作区纪律：改代码/写产出在 worktree，跑 gate 用 `~/.agate` 稳定版；但
  `check-protocol-consistency.py` 必须用 worktree 自己的（检查对象是 worktree 里的协议文件）

### B. check-gate.py gate_p4 现状（挂载点，v3 B1 修正依据）
```
gate_p4(task_dir) 现有检查（check-gate.py:870-927）：
1. P4-review.md 存在（不存在 → exit 1）
2. P4-review.md frontmatter status == approved（非 → exit 1）
3. agent 字段存在且 != main（缺失 → exit 2 WARNING；== main → exit 1）
4. pre-commit 阶段查 `git diff --cached --name-only` 含代码文件（_STAGED_EXCLUDE_RE 排除，
   无代码文件 → exit 1）——这正是"P4 阶段代码已 staged"的证据
5. 骨架/CODE-MAP 机制 WARNING（不阻断）
gate 分发映射：{"P4": gate_p4, ...}（check-gate.py:1340）
```
P4 新增一步的位置：在现有检查基础上追加"调 check_maintainability(task_dir) + 三重门槛"。
返回约定（1=阻断 / 2=WARNING 不阻断 / 0=通过）必须与既有调用链兼容。

### C. count_kf_entries 计数算法（known-violations 复用）
```
agate_common.py:1015-1017
def count_kf_entries(text):
    return sum(1 for line in text.splitlines() if re.search(r"^\|\s*[0-9]+\s*\|", line))
```
→ known-violations.md 登记表必须用 `| N |` 行首表格格式（模板字段「P4评审确认」列不参与计数）。

### D. 同类/影响面扫描线索（analyst 须补全并逐条判定）
- `check-gate.py` 消费方（P4 新增一步会影响的调用链）：pre-commit-gate.py / ci-gate-backstop /
  check-judge-verdict / agate_common / rules/ 多处引用 check-gate —— analyst 需 grep 确认命中
  数量 + 文件清单，判定"本次处理/不处理 + 理由"
- `count_kf_entries` 消费方：known-failures.md 登记计数（P5 判定用）——新增 known-violations
  复用同一函数，须确认不改动既有 P5 语义
- `known-violations` 相关：全仓 grep 确认无既有 known-violations 机制（首次引入）
- `maintainability.yaml` 相关：全仓 grep 确认无既有配置（首次引入）
- `check-maintainability.py` 相关：确认不存在（新增文件）
- fuzzy-boundary 相关：确认 ruff 规则（如 E722 裸 except）是否已覆盖部分语义——设计文档
  §9 指出 ruff 是"模糊边界"一类的一个平台实现，不冲突，但 P1 需说明二者关系

### E. 测试基线（P0-brief 已核实）
- 全量 pytest 全绿（worktree 基线）
- consistency 0 ERROR（--strict-errors-only）
- count-tests 1308（2026-08-30 实测）
- 新增 pytest 用例数：设计文档要求对齐既有覆盖惯例，13 条 BDD → 对应测试文件

### F. judge 启用
- `.state.yaml` 已写 `judge.enabled: true`（RM-AG0039 强制，机制后新任务），P1-requirements.md
  的 frontmatter 无需重复，但正文不要与 judge 机制冲突。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
