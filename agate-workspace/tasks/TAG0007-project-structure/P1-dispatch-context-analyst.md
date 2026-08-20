---
phase: P1
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0007
role: analyst
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

## 【第 2 轮：修复轮，增量模式】

- **上轮产出路径**：{AGATE_WORKSPACE}/tasks/TAG0007-project-structure/P1-requirements.md（已存在，
  在此基础上**修改**，不要重写整份文件）
- **上轮 dispatch-context**：本文件下方「目标/约束/上游关联/输入文件」原样有效，复用其约束，
  不要重新分析一遍
- **评审意见**：{AGATE_WORKSPACE}/tasks/TAG0007-project-structure/P1-review.md
  （status: needs-revision，结论列出 3 处具体待修点）

### 本轮修复目标（只改这 3 处，不触碰 BDD 语义/不做基线重写）
1. **同类扫描命中计数误差**：`骨架|skeleton` 关键词 grep 实际命中 6 处，正文第4节表格漏写
   `dispatch-protocol.md:435`（"极简结构骨架（用于快速对照，非完整正文，实际派发以权威源为准）"）
   这一行。补充该行 + 判定（预期：与 WORKFLOW.md:3 同类，属流程/派发模板结构的泛化用法，非项目
   目录骨架机制，不影响"全新增补"结论），命中数量由 5 处改为 6 处。
2. **边界维度遗漏并发场景**：CODE-MAP.md 是项目全生命周期单一维护物，多任务/多 worktree（本仓库
   自身即多 worktree 结构）并行执行 P4 阶段时对同一份 CODE-MAP.md 的并发更新/合并冲突风险未被
   提及。在「隐含需求识别」或「机制一致性/候选接入点盘点」节补充声明该边界情形存在（哪怕只写
   "存在该风险，具体合并策略留给 P2 设计"即满足要求，不要求本轮给出解决方案）。
3. **BDD-4 与 BDD-7 场景叠加未声明关系**：两条 BDD 都以"P4 实现阶段新增文件"为同一触发场景，
   分别要求骨架目录归属与 CODE-MAP 更新两个独立义务，但未声明二者是否需要同时满足。在 BDD-4
   或 BDD-7 后（或两者之间）补充一句显式说明，如："BDD-4 与 BDD-7 分属骨架与 CODE-MAP 两个独立
   机制，同一文件新增事件需同时满足两条验收标准，无优先级/替代关系"。

修改完成后，把改动追加进 P1-progress.md（哪几行改了、为什么），然后返回。**其余内容（BDD-1/2/3/5/
6/8/9/10/11、frontmatter、需求复述、能力需求声明等）本轮不动**，review 已判定这些部分 PASS。

---

## 首轮派发指引（背景，供理解上下文，不必重新执行）

### 目标
产出 TAG0007 的 P1-requirements.md：为 agate 协议新增两个机制——RM-AG0008（0→1 项目骨架脚手架）+
RM-AG0009（CODE-MAP 架构演进纪律）——建立需求基线（含 BDD 验收条件）。这是**新增机制**（"建"，
不是"修 bug"），要把两个机制的落地方式（放哪个阶段、产出什么、怎么验收、怎么接入既有 gate/角色/
卡片体系）用 BDD 定义清楚。

### 约束
1. 两个机制都要走完整 P0-P8，不能因为"是新机制"而裁剪阶段（P0-brief known_risks 已锁定）。
2. 不破坏已有协议语义——骨架/code-map 落地会触碰既有机制（P7 一致性检查、P2 架构评审、TAG0002
   的 change_type: refactor 分流），需求阶段就要识别这些交叉点，避免新旧机制口径冲突。用户明确
   表达"不愿意一轮一轮来回改"，即：本轮 P1 就要把交叉点扫清楚，不要留到 P2/P4 才发现。
3. Linux 现状是基线——现有 1011 pytest 测试全绿是回归底线（本阶段是需求阶段，不动代码，但要在
   BDD 里体现"改动不能破坏现有测试"这条隐含约束）。
4. 范围锁定：若分析发现需改动超出 P0-brief 锁定范围（RM-AG0008 骨架机制 + RM-AG0009 CODE-MAP
   机制），不要擅自扩大范围，标 `[NEED_CONFIRM]` 交主 Agent 确认，不自行决定。
5. 【强制】同类扫描：按 P1 卡片「同类扫描」节的规则，对"骨架/skeleton"、"CODE-MAP/code-map"、
   "架构演进/依赖方向"等关键符号做过 grep 全仓扫描（结果见下方 objective_info），已确认协议库内
   当前**无**同名机制/文件——即"已确认只此一处（新增）"这一结论需要在 P1 正文显式写出，不能空白。
6. 【强制】机制一致性扫描：RM-AG0009 提到的"P7 一致性检查""P2 架构评审""gate 检测依赖偏离"要
   落在现有协议体系的哪个位置，P1 阶段先做一次盘点（现有 phase-cards/execution-roles/review-roles/
   scripts 清单见 objective_info），标出候选接入点（哪张卡片、哪个角色、哪个 gate 脚本可能要改），
   为 P2 设计做铺垫（P1 只需盘点候选接入点 + 隐含需求，不做具体设计）。
7. RM-AG0008（骨架）和 RM-AG0009（code-map）虽同属"项目结构管理"主题但落地时机不同（骨架是
   0→1 一次性产出，code-map 是持续演进维护物），P1 的 BDD 需要能体现两者不同的生命周期，不要
   合并成一条笼统的 BDD。
8. domains 声明：本任务改动对象是 agate 协议本体（phase-cards / templates / gate 脚本），不是
   面向最终用户的 UI，判断是否需要 `frontend` domain 时按"协议开发者作为使用者"的视角判断，不要
   套用最终用户 UI 的 UX 框架。

### 上游关联
P0-brief.md 已锁定任务范围（issues 两条 = RM-AG0008 + RM-AG0009，均给出"修复="的方向性思路，
但方向性思路不是最终设计——P1 要把"修复="里的方案要素转成可验证的 BDD 和隐含需求，不要照抄
P0-brief 的"修复="文字当 BDD。known_risks 六条已标出本任务的关键决策点（骨架放哪个阶段验证 /
CODE-MAP 放哪维护 / 与 TAG0002 change_type: refactor 的兼容 / SELF-GATE 触发面），P1 需求要
覆盖或至少标注这些决策点的需求侧含义（P2 设计阶段才做具体方案选型）。

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0007-project-structure/P0-brief.md（任务简报，issues/known_risks/
  env_constraints 是本次分析的起点）
- /home/kity/oclab/agate/.worktrees/agate-TAG0007/AGENTS.md（项目通用开发约定——repo 布局、
  阶段纪律、脚本约定）
- /home/kity/oclab/agate/.worktrees/agate-TAG0007/agate/WORKFLOW.md（尤其"需求与验收机制"节，
  理解 P0-P8 现有流程骨架，判断骨架/code-map 两机制该嵌在哪）
- /home/kity/oclab/agate/.worktrees/agate-TAG0007/agate/role-system.md（双层角色体系，判断新机制
  是否需要新角色/复用现有角色）
- /home/kity/oclab/agate/.worktrees/agate-TAG0007/agate/dispatch-protocol.md（派发协议，判断新
  机制产出是否要走既有 dispatch-context 流程）
- /home/kity/oclab/agate/.worktrees/agate-TAG0007/agate/adr.md（既有架构决策记录，理解 agate
  "不硬编码技术栈、只定协议流程骨架"的既定原则——RM-AG0008 骨架模板设计需与此原则相容，
  即骨架模板要按技术栈参数化，不能反向硬编码具体技术栈进协议本体）
- /home/kity/oclab/agate/.worktrees/agate-TAG0007/HANDOFF-TAG0007.md（交接单，含双工作区纪律
  和已完成 setup 状态，理解当前 worktree 环境）
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
- 环境状态：worktree 基线已验证 1011 pytest passed + consistency 0 ERROR（默认模式 exit 0）；
  本阶段（P1）不改代码，不需要重新跑基线，但需求里若涉及"骨架产出验证方式"，可参考这条基线
  作为"新增验证不能拖慢/破坏现有基线"的隐含约束依据。
- 同类扫描结果（"骨架/skeleton"关键词，`grep -rniE "骨架|skeleton" --include="*.md" agate/`，
  排除 agate-workspace/）：命中 5 处，均为既有文档中"骨架"作泛化比喻使用（role-system.md:80
  "最简骨架"指 prompt 示例简化版；adr.md:81/85 "流程骨架"指 P0-P8 阶段流程本身；WORKFLOW.md:3
  同义；vision-analyst.md:168 `skeleton_visible` 是视觉分析字段，与项目目录骨架无关）——**协议库
  内当前无"项目目录骨架脚手架"这一机制**，RM-AG0008 是全新增补，无同类实例需处理。
- 同类扫描结果（"CODE-MAP/code-map/code_map"关键词，同范围 grep）：**0 命中**——协议库内当前无
  CODE-MAP 或同义维护物，RM-AG0009 是全新增补。
- 同类扫描结果（"架构演进/架构评审/依赖方向"关键词，同范围 grep）：**0 命中**——协议库内当前无
  显式的"架构演进检查"或"依赖方向"校验机制。
- 机制盘点（供"候选接入点"分析用，非最终设计）：
  - phase-cards/：P0-orchestrator, P1-requirements, P2-design, P3-tdd, P4-implementation,
    P5-verification, P6-acceptance, P7-consistency, P8-release, README（共 9 张业务卡 + 1 README）
  - execution-roles/：analyst, architect, consistency-reviewer, implementer, test-designer,
    verifier, vision-analyst（7 个执行角色，无"骨架设计"或"架构评审"专属角色）
  - review-roles/：cso, design-review, investigate, plan-ceo-review, plan-design-review,
    plan-eng-review, protocol-alignment-review, qa, requirements-review, review（10 个评审角色）
  - scripts/ 中 gate/consistency/state 相关：check-gate.py（阶段门槛判定）、
    check-protocol-consistency.py（协议自身一致性，TAG0007 若新增 gate 规则大概率要触碰这个脚本
    或类似的新脚本）、check-state-transition.py、check-state-yaml.py、
    agate-evidence-consistency.py、agate-frontmatter-check.py（这几个是当前"一致性/校验"类脚本
    家族，RM-AG0009 的"gate 检测依赖偏离"若要落地，大概率是新增同家族脚本或扩展其一）
  - templates/：active-tasks-template, custom-role, dispatch-context, dispatch-prompt,
    handoff-template, known-failures-template, project.md, retrospective-template,
    roadmap-template, task-files, tech-debt-template（当前无"项目骨架模板"或"CODE-MAP 模板"）
  - TAG0002（重构一等任务）落地的 `change_type: refactor` 机制在 P1 frontmatter 声明，P2/P6
    走不同评审/验收口径——RM-AG0009 的架构演进纪律需求里应说明与该机制的关系（是否 refactor 类
    任务也要过架构合规检查、还是豁免）
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
