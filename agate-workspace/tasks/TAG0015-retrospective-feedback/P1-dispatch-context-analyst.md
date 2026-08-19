> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。

---
phase: P1
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0015
role: analyst
retry: 1
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

## 重试 #1（路径引用订正，本节优先于下方原始派发指引）

requirements-review 对你上一版 P1-requirements.md 的判定是 `needs-revision`（20 条 BDD 中 19 条
approved，仅 BDD-14 needs-revision），完整评审见
`{AGATE_WORKSPACE}/tasks/TAG0015-retrospective-feedback/P1-review.md`「BLOCKER：task-files.md
路径引用不准确」节。**只需订正一处路径引用错误**，不要重写全文，不要改动已 approved 的 19 条
BDD 的判定实质（Given/When/Then 的行为要求不变）：

**问题**：全文 7 处把 `task-files.md` 当裸文件名引用，并归类为与 `state-machine.md`／
`loop-orchestration.md`／`AGENTS.md`／`WORKFLOW.md` 同级的"核心协议文件"，但该文件真实路径是
`agate/assets/templates/task-files.md`（review 已用 `find . -iname "task-files*"` 独立核实，
`agate/` 根目录下不存在同名文件）。裸名引用导致 BDD-14 的 Then 子句可执行性打折扣（P4 implementer
按裸名可能在错误目录找/建文件），也导致 packages 边界模糊（该文件物理上应归 `assets/templates`
包，却被放进 `core-protocol-docs` 包）。

**需订正的 7 处**（行号为订正前版本，订正后行号可能小幅偏移，以内容定位为准）：
1. 第 52 行（隐含需求识别 3）："state-machine.md/loop-orchestration.md/task-files.md/WORKFLOW.md"
2. 第 69 行（同类扫描表格第6行）：同样裸名引用
3. 第 150 行（4.4 节标题）："orchestrator-log 跨文件同步（loop-orchestration.md / task-files.md）"
4. 第 154/155 行（**BDD-14 正文** Given/Then）：`loop-orchestration.md:168,173、task-files.md:45`
5. 第 219 行（裁剪说明 risk_level 理由）："AGENTS.md/state-machine.md/loop-orchestration.md/task-files.md"
6. 第 225 行（packages 范围声明）：`core-protocol-docs` 包对 task-files.md 的归属说明

**修订方式**：以上 7 处凡引用 `task-files.md` 的地方，一律改为完整路径
`agate/assets/templates/task-files.md`。同时在第 8 节裁剪说明 / 第 9 节 packages 范围声明中，
明确该文件计入 `assets/templates` 包还是保留在 `core-protocol-docs` 包并说明理由（review 已明确
"二选一即可，不要求特定答案，但需自洽且路径准确"——建议：该文件本身是"任务产出文件命名规范"
参考表而非流程规则文件，物理上归 `assets/templates` 包更贴切，但若你判断它在本任务语境下更适合
留在 `core-protocol-docs` 包，需给出理由，两种选择都可接受）。

修订完成后自检：`grep -n "task-files.md" P1-requirements.md` 确认所有命中都带 `agate/assets/
templates/` 前缀（不再有裸名引用），且 20 条 BDD 的编号/Given/When/Then 语义未被意外改动。修订后
仍写回同一路径 `{AGATE_WORKSPACE}/tasks/TAG0015-retrospective-feedback/P1-requirements.md`
（覆盖原文件）。

---

### 目标（原始派发指引，重试时仍适用于未涉及修订的部分）

把 P0-brief.md 中已核实的两条 roadmap 缺口（RM-AG0020 复盘机制统一 + RM-AG0021 跨项目反馈机制）
转成一份**按"文件 → 改动"归并**的需求基线，含可验证的 BDD 验收条件、能力声明、裁剪声明。这是
agate 自身的协议机制改动（不是常规业务功能）：BDD 描述的是"复盘机制/反馈机制应该长什么样、
触发什么、约束什么"，不是"用户点了什么按钮"。

### 约束

1. **合并规划，不按 RM 编号平铺写两份需求**——P0-brief 已指出 RM-AG0020 的八项残缺（模板正文结构 /
   内容价值标准 / 触发标的 / 落盘路径 / 归因分层 / 产出流向 / 事实依据三层源 / 时机前置）+ 项目
   资产沉淀增量，和 RM-AG0021 的四项修复（frontmatter 机器字段 + `## agate 反馈` 节 /
   agate-feedback.py / AGATE_FEEDBACK 开关 / 回传通道），高度重叠于同一批文件（见下方
   objective_info 的命中清单）。BDD 组织方式必须先按"改哪个文件"分组，再在每个文件分组下列清楚
   该文件承接哪几条缺口的哪些改动点，避免同一文件在不同 BDD 里被分别描述导致后续阶段重复改、改漏。
2. **AG0020 核心 + AG0021 增量两阶段，但仍是一份 P1-requirements.md**——AG0021 建立在 AG0020 的
   结构化产出（复盘 frontmatter 机器字段）之上，BDD 顺序/依赖关系需要在正文里显式声明这种先后关系
   （如"BDD-X 的 frontmatter 字段是 BDD-Y 的 agate-feedback.py 提取依赖"），不要求 P2/P4 拆两个
   子任务，但需求基线要让下游知道哪些 BDD 互相依赖。
3. **【强制】同类扫描已由主 Agent 预跑（见下方 objective_info），但这只是起点覆盖面，不是完整
   结论**——analyst 必须自己针对每条缺口补充验证/深挖，尤其是：
   - postmortem-template.md 当前只被 docs/reviews/ 内部文档 + 少数任务 P0-brief/P1-requirements +
     两份 HANDOFF 引用，**未被任何核心协议文件（dispatch-protocol.md/WORKFLOW.md/state-machine.md）
     引用**——需判断这本身是否也是问题（模板"游离于协议本体之外"），要不要在 BDD 里要求补齐引用点。
   - docs/reviews/ 下现存 4 份存量复盘文档（tag0008/tag0010-0011/tag0013/tag0014）+ 1 份
     tag0010-0011 的 review 文档，是本次"路径迁移到 tasks/{Txxx}/retrospective.md"决策的直接
     存量对象，需求需明确：迁移 / 保留旧文件加标注 / 只对新复盘生效不动存量，三选一并给理由
     （P0-brief known_risks 已说"需迁移或标记旧布局"，但决策留给 analyst 提炼成可验证 BDD）。
   - `agate/scripts/test_check_retrospective.py`（单元测试，见 objective_info）当前对
     `docs/releases/v{version}-retrospective.md` 这行提示文案**没有专门断言**（grep 零命中），
     说明改这行文案不会被现有测试拦截——BDD 需要求新增/更新断言覆盖新路径提示文案，否则 P3 无法
     形成有效红灯。
   用户明确要求：这一批任务本身要做"同类扫描"的示范，不接受"改一处漏同类"。
4. **不得扩大范围**——P0-brief 已锁定 RM-AG0020（含项目资产沉淀增量）+ RM-AG0021（含触发方式
   修正）。分析中若发现范围之外但相关的协议缺口（如"复盘"关键词在 agate-workspace/archived/
   历史归档文档中的大量存量提及），记录在 P1-requirements.md 的"范围外观察"小节，**不纳入本任务
   BDD**，不擅自扩大 packages/domains——归档文档是历史记录，不是本任务的迁移/改动对象。
5. **orchestrator-log 扩展（决策+依据）+ 会话 checkpoint 是新机制设计**——P1 只需要把"要设计什么、
   设计必须满足什么约束/边界条件"写成 BDD（可验证：文档里能查到该规则 + 规则覆盖 P0-brief 列出的
   L1/L2/L3 三层事实源场景），具体的落盘时机/格式/防 compact 策略由 P2 architect 设计，P1 不要
   越权写死具体格式，但要写清楚设计必须回答哪些问题（如"L2 会话 checkpoint 何时触发落盘、写在
   哪个文件、和现有 orchestrator-log.md『不写思考过程』的既有约束是什么关系——是新开一类文件还是
   扩展 orchestrator-log.md 语义"）。
6. **domains** 用 `[process]`（协议/流程域，不是业务 backend/frontend）；`packages:` 用改动涉及的
   agate 子目录归类（如 `phase-cards`、`assets/templates`、`scripts`、`state-machine`、
   `docs-reviews-migration`）。
7. **risk_level**：本任务改协议文档 + 至少 1 个脚本（check-retrospective.py 路径提示文案，可能
   还有新增 agate-feedback.py）+ 存量文档迁移，改动面广且触发 SELF-GATE，按 protocol 类任务惯例
   定级并说明理由。
8. **phases 裁剪**：check-retrospective.py 的路径文案改动 + 若新增 agate-feedback.py，均涉及
   脚本行为变化，需要 TDD 红灯（不可裁 P3）；纯文档新增/迁移部分（模板正文结构、state-machine.md
   触发描述）无配套脚本时可与 architect 讨论是否可裁剪该子集的 P3——analyst 需先判断范围内哪些
   BDD 有脚本改动、哪些是纯文档，据此声明 phases（不要整体裁剪，防止把脚本改动也裁掉红灯）。
9. **capability_requirements**：本任务是纯文档/协议 + 脚本改动，无需 browser-vision 等特殊能力，
   正常声明 `available`，不需要真实并发/环境验证能力。
10. **AG0021 触发方式修正必须落成 BDD 而非仅正文描述**——P0-brief 已核实：回馈是"用户/agate 项目组
    推动"而非"项目自发"（TPV0093 实证）。agate-feedback.py 的 BDD 验收条件不能假设"外部项目会
    自动运行该脚本"，应验证"结构化提取 + 匿名化 + 生成待提交内容"这条能力本身，触发方式在 BDD 的
    Given 里写清是"用户/agate 项目组要求登记反馈节后手动触发"，不要写成自动化触发流程。

### 输入文件（按顺序读）

1. `{AGATE_WORKSPACE}/tasks/TAG0015-retrospective-feedback/P0-brief.md`（任务目标、8+4 条已核实
   缺口、known_risks、执行环境约束）
2. `HANDOFF-TAG0015.md`（worktree 根，交接单，含双工作区纪律 + 阶段推进纪律，供 analyst 了解
   已完成的 setup 状态，不是需求来源）
3. `agate/scripts/check-retrospective.py`（100 行，短，直接读全文——当前只在异常模式提醒，硬编码
   `docs/releases/v{version}-retrospective.md` 路径提示）
4. `docs/reviews/postmortem-template.md`（现有模板全文，理解"只有机制触发核对清单，无复盘正文"
   的具体现状）
5. `agate/state-machine.md` 第 470-490 行附近（`orchestrator-log.md 防无响应`节，理解"不写思考
   过程"的既有约束原文）
6. `docs/reviews/retrospective-tag0013-docs-20260816.md` 或 `retrospective-tag0014-docs-20260816.md`
   任选一份存量复盘，理解"临场拼出来的正文结构"长什么样（不需要通读，看结构即可）
7. `agate/assets/templates/task-files.md` 第 40-50 行附近（任务产物清单表，理解 orchestrator-log.md
   当前的定位描述）

### 门槛（什么算完成）

P1-requirements.md 含：
- ≥1 条 BDD（预期这批范围会产出较多条 BDD，因涉及 8+4 条已核实缺口 + 两个 RM），每条 Given/When/Then
- 同类扫描结论（命中清单 + 逐条"本次处理/本次不处理"判定，"范围外观察"小节收纳不处理项）
- frontmatter：risk_level / phases / packages / domains 齐全
- 无未决 `[NEED_CONFIRM]`（有则按 SUGGEST/NEED_CONFIRM 分级处理，真无方向的写 NEED_CONFIRM 交主
  Agent 判断是否需要问用户）
- AG0020/AG0021 的 BDD 依赖关系已显式声明
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
- `phases:` 裁剪声明（跳过哪些阶段 + 理由）
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
phases: [P1, P4, P5, P6, P8]   # list of P\d+，必填
packages: [pkg-a]           # list，必填
domains: [backend, frontend]  # list，必填
# 可选字段：override / implicit_coupling / coupling_checklist / internal_only /
# internal_only_reason / 跳过风险 / design_trivial / follows_existing_pattern
# ── v2.0 refactor 任务类型声明（可选，缺省 = 功能任务）──
# change_type: refactor   # 当前仅支持 refactor；枚举非法值由 frontmatter schema 拦截
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
<!-- AGATE_CARD_END -->

<objective_info>
- 环境状态：worktree 基线已重新验证（本次派发前刚跑过，非沿用交接单旧数据）——
  `python3 -m pytest agate/tests/` → **909 passed, 2 skipped**；
  `python3 agate/scripts/check-protocol-consistency.py --strict` → **0 ERROR，279 WARNING**
  （与 TAG0012 合并后的基线一致）。交接单 HANDOFF-TAG0015.md 里写的"893 pytest"是 P0 立项时
  （2026-08-16）的旧数字，worktree 分支此后已 rebase 上 TAG0012 的合并（新增 16 个测试），
  属轻微字段刷新，不影响任务技术路线——P0-brief 时效性自检结论：**已核对，无漂移**（严重漂移
  判据 1-3 均不命中：任务目标方案未变，Linux 执行环境前提未变，known_risks 的"已解决前提"
  未见被其他任务解决或失效）。analyst 可直接在此基线上工作，不需要重新怀疑任务前提。

- 主 Agent 已预跑的同类扫描（起点，非完整结论，analyst 需自行补充深挖）：

  1) `retrospective|复盘|postmortem` 关键词在协议本体核心文件（`agate/*.md`、
     `agate/phase-cards/*.md`、`agate/assets/**/*.md`、`agate/scripts/*.py`、`agate/scripts/*.sh`，
     不含 `agate-workspace/archived/` 历史归档、不含各任务目录存量产出）命中 **14 个文件**：
     `agate/adr.md`、`agate/AGENTS.md`、`agate/assets/templates/handoff-template.md`、
     `agate/assets/templates/roadmap-template.md`、`agate/assets/templates/tech-debt-template.md`、
     `agate/git-integration.md`、`agate/scripts/agate_common.py`、`agate/scripts/agate-debt-check.py`、
     `agate/scripts/agate-summary.py`、`agate/scripts/check-protocol-consistency.py`、
     `agate/scripts/check-retrospective.py`、`agate/scripts/pre-commit-gate.py`、`agate/UPGRADING.md`、
     `agate/WORKFLOW.md`。
     其中 `agate/AGENTS.md:11` 现在的描述是"docs/ 目录存放……复盘。这些都是仓库维护者写的，
     使用者无需阅读"——这条描述与本任务"复盘产出应归 tasks/{Txxx}/"的目标方案存在**潜在措辞冲突**
     （复盘若挪到 tasks/ 下，AGENTS.md 这句"复盘在 docs/"的表述需要同步修订，否则 P7 一致性检查
     会抓到文档漂移）——analyst 需要把这条列进 BDD 影响面，不能漏。

  2) `check-retrospective.py` 全文只有 100 行，硬编码路径提示在第 93 行：
     `sys.stderr.write("  请在版本 bump 前写简版复盘（docs/releases/v{version}-retrospective.md）\n")`
     ——路径指向 `docs/releases/`，既不是模板现在所在的 `docs/reviews/`，也不是本任务目标路径
     `tasks/{Txxx}/`，三处路径互不相同，坐实 P0-brief 描述的"路径矛盾"（问题④）。
     配套单元测试 `agate/tests/unit/test_check_retrospective.py` 对这行文案**没有专门断言**
     （`grep -n "docs/releases\|docs/reviews\|tasks/{"` 零命中）——改这行文案目前不会被测试拦截，
     P3 阶段需要新增断言才能形成有效红灯。

  3) `state-machine.md` 全文对 `retrospective|复盘` 关键词**零命中**——复盘机制目前完全不在状态机
     的转移规则里出现，只有 `orchestrator-log.md` 相关描述（第 470-490 行附近），且明确写着
     "不写思考过程、不写文件内容摘要、不写 subagent 返回原文——只写决策和下一步"——这条既有约束
     与本任务"orchestrator-log 扩展决策依据"的目标**直接相关且可能冲突**：现状是"决策"和"依据"
     被明确排除在外只留"下一步"，P0-brief 问题⑦要求扩展到含"依据"，需要 P1 把这条现状与目标的
     差距写进 BDD 的 Given（而不是默认现状已经支持"决策+依据"）。

  4) `postmortem-template.md` 当前路径 `docs/reviews/postmortem-template.md`，全仓引用点（不含
     `archived/`）：`HANDOFF-TAG0015.md`、`agate-workspace/roadmap/roadmap.md`、
     `agate-workspace/tasks/TAG0013-script-consistency/{P0-brief,P1-requirements}.md`。**没有任何
     `agate/` 核心协议文件（dispatch-protocol.md/WORKFLOW.md/state-machine.md/phase-cards/*）引用
     这个模板**——模板目前完全"游离"于协议本体之外，只是项目资料区的一份文档，这也是它不在
     `agate/assets/templates/` 而在 `docs/reviews/` 的直接后果。

  5) `docs/reviews/` 目录现存 11 个文件，其中 4 份是存量复盘正文（`retrospective-tag0008-docs-
     20260817.md`、`retrospective-tag0010-0011-docs-20260815.md`（+ 同名 `-review.md`）、
     `retrospective-tag0013-docs-20260816.md`、`retrospective-tag0014-docs-20260816.md`），是
     "路径迁移到 tasks/{Txxx}/retrospective.md"决策的直接存量对象——迁移/保留/不动三选一需要
     analyst 定决策方向并转成 BDD（P0-brief 只说"需迁移或标记"，未拍板）。

  6) `orchestrator-log` 关键词在核心协议文件命中 4 处：`task-files.md:45`（产物清单表，一行
     描述）、`WORKFLOW.md:91`（目录树注释）、`loop-orchestration.md:168,173`（"主 Agent 尽量
     无状态"原则 + "防无响应"用法）、`state-machine.md:361,475,477`（同上第 3 点引用的段落）。
     命中面不大（4 个文件），扩展 orchestrator-log 语义需要同步这几处的描述，不是只改
     state-machine.md 一处。

  7) `AGATE_FEEDBACK` / `agate-feedback.py` 全仓 grep **零命中**——RM-AG0021 是纯新增设计，不是
     补全既有字段/脚本，P1 不要假设有任何现成骨架可复用。

- 查证结论摘要（供 analyst 参考，不替代自行核实）：P0-brief 列出的 8+4 条缺口与代码/文档现状一致，
  均有客观证据支撑，无需在 P1 阶段重新验证"问题是否存在"，重点放在"BDD 怎么按文件归并组织 +
  影响面是否有遗漏（尤其 AGENTS.md:11 的措辞冲突 + docs/reviews/ 4 份存量复盘的迁移决策）+
  AG0020/AG0021 依赖顺序声明 + 裁剪判断"。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
