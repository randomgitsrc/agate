---
phase: P1
task_id: TAG0001-tech-debt-closure
type: problems
parent: P0-brief.md
trace_id: TAG0001-P1-20260812
status: draft
created: 2026-08-12
agent: analyst
# ── v2.0 机器字段 ──
risk_level: medium             # 触及 gate 脚本（check-gate.sh P8 分支）+ 新增 schema 校验脚本 + 协议文档横切 + 工作区初始化目录变更；非破坏性（默认无 tech-debt.md 时行为不变）故不置 high
phases: [P1, P2, P3, P4, P5, P6, P7, P8]   # 全流程，无裁剪（理由见 §5 裁剪说明）
packages: [agate]              # 协议本体单一包（改的是 worktree 的 agate/）
domains: [backend, cli]        # backend=check-gate.sh P8 分支/新 schema 校验器/回退比对脚本/bats；cli=orchestrator 读取层（P8 卡片、state-transitions 回退规则、工作区初始化 mkdir）。无 frontend、无 security
# ── SCOPE+ 已解决（P2 回补，2026-08-12）──
scope_resolved:
  - "P8 gate 加 debt_check 缺失即 exit 1 需同步更新 check-gate.bats 既有 6 处 G8 fixture——已纳入 P2 方案 §9 SCOPE+ #1，P3/P4 同步更新 fixture + 新增用例，不需新增 BDD（BDD-16/17 覆盖）"
  - "check-protocol-consistency.py SCRIPT_ALIGNMENT_ANCHORS 需为 check-debt.sh 加锚点 + scripts/README.md 脚本清单补录——已纳入 P2 方案 §9 SCOPE+ #2，P4 同步处理，不需新增 BDD"
---

# TAG0001 — agate 技术债登记闭环（Phase 1-3）+ tech-debt 归类修正：P1 需求基线

> 输入：P0-brief.md（任务简报/风险/约束）+ P1-dispatch-context-analyst.md（派发指引）+ AGENTS.md（项目约定）+ docs/reviews/review-20260812-1204.md（技术债闭环完整设计 Phase 1-3 + 强制力 + 止损——任务内容来源）。
> 角色：analyst（需求质疑，见 `~/.agate/assets/execution-roles/analyst.md`）。
> 范围说明：本任务改造对象是 **worktree 的 `agate/`（协议本体，分支 dev/workspace，已含 TAG0003 工作区架构 + TAG0002 refactor 机制）**，不是 `~/.agate`（稳定版 v0.40.2 开发工具，禁止改动）。本基线定义"做什么 + 做完什么样算对"，不写实现方案（P2 的活）。本任务为**功能型任务**（为协议新增"技术债登记闭环"机制 + 修正 tech-debt 归类），自身不声明 `change_type: refactor`。

## 1. 需求复述

### 1.1 一句话需求

为 agate 建立项目级**技术债登记闭环**（Phase 1 登记规范 + schema 校验、Phase 2 回退事件强制登记、Phase 3 P8 确认留痕），并用 T001 复盘既有条目回填验证模板；同时修正 TAG0003 工作区规范把 tech-debt 归入 `agents/` 的粗略归类，tech-debt.md 落**独立 `debt/` 目录**。

### 1.2 已确认决策（P0-brief + review-20260812-1204 作为需求输入，不得推翻）

1. **tech-debt.md 落独立 `debt/` 目录**（`{AGATE_WORKSPACE}/debt/tech-debt.md`）：agents/ 只放 agent 输入知识（project.md/memory）；tech-debt 是流程产出的项目状态记录（有状态机/schema/被脚本读写/有生命周期），归独立 debt/ 目录。同步 WORKFLOW.md 目录图、工作区初始化 mkdir（8→9 子目录）、SETUP/UPGRADING。
2. **唯一新增硬强制 = 回退事件必须建 DEBT 条目**（`source: retreat`）：客观事件触发（retreat 是协议定义的事实），逻辑上不可能误报，不需要任何人做价值判断。
3. **三态状态机**（open/in_progress/closed），不用七态——无 gate 强制的复杂状态机会僵死；`task_id` 非 null 即承载"已立项"（视为 in_progress），不需要 accepted/planned 独立成态。
4. **`evidence` 必填**（schema 强制）——讨论稿"不能只写代码不好"的要求，只有设成 schema 必填才真正落地。
5. **债 vs 缺陷判据**："不修它，当前任务的验收声明会不会变成假的？"——会→当前任务缺陷走任务内；不会但让未来变更更贵/更险→登记 DEBT；都不影响→不登记。登记 DEBT 的任务，其验收声明不得包含依赖该问题已解决的表述（P7 人工核对）。
6. **P8 只强制"看过并留痕"，不阻断发布**——一旦某类债能阻断发布，登记该类债就等于给自己找麻烦，结果必然是不登记（Goodhart 最短路径）。
7. **止损**：T001 回填失败 = 模板设计错（重新设计）；P8 空确认连续 3 次 = 移除强制。
8. **change_type: refactor 已由 TAG0002 实现**——TAG0001 不需要再做该字段，但要基于最新协议构建（agate-frontmatter-check.py 已有 change_type schema），不得回退。
9. **在 dev/workspace 分支上增量**：协议文件已被 TAG0003/TAG0002 改动，P4 实现须在其上增量，不改动已验收功能（除本次显式修正的 tech-debt 归类）。

### 1.3 改动面（主 Agent 已核实，本基线确认覆盖完整范围）

| 改动面 | 现状（已查证） | 本任务需要什么 |
|---|---|---|
| 工作区目录规范 | WORKFLOW.md L85 `agents/ # agent 知识（project.md / memory / tech-debt）`；L79 "固定 8 个子目录" | agents/ 注释去掉 tech-debt，新增 debt/ 子目录（9 个） |
| 工作区初始化 mkdir | SETUP.md:114 / orchestrator-template.md:102 / state-machine.md:40 均 `mkdir -p {AGATE_WORKSPACE}/{roadmap,tasks,agents,archived,reviews,decisions,plans,logs}`（8 子目录） | 三处同步为含 debt/ 的 9 子目录 |
| tech-debt 模板 | 无 | `assets/templates/tech-debt-template.md`（下游项目放 `{AGATE_WORKSPACE}/debt/tech-debt.md`） |
| schema 校验 | 无 tech-debt 校验器 | `agate-debt-check.py` + `check-debt.sh`（必填字段、枚举、evidence 非空、closed 须有 task_id+证据引用） |
| review 角色卡 | plan-eng-review.md:19 "技术债有没有记录和计划"（无格式要求） | 追加"提债须用标准 DEBT 条目格式" |
| 回退规则 | rules/state-transitions.md 回退规则 + agate-retreat-to.sh（retreat: 提交格式）存在，无 DEBT 强制 | 回退卡片 + state-transitions 明确"回退落地后必须建 DEBT 条目" |
| 回退覆盖检查 | 无 | 轻量脚本：git log 提取 `retreat:` 提交，与 tech-debt.md `source: retreat` 条目比对，缺失 WARNING |
| P8 发布准备 | phase-cards/P8-release.md（releaser 产出 P8-release.md）+ check-gate.sh P8 分支（bump_type/version/CHANGELOG） | P8-release.md 增加"确认债务清单"一步（结果写入，只查留痕不查内容达标）；check-gate.sh P8 分支加留痕检查 |
| 升级指引 | UPGRADING.md v0.41.0 迁移节（8 子目录） | 同步 9 子目录与 tech-debt 路径 |

## 2. 隐含需求识别

### 2.1 向后兼容：无 tech-debt.md 的项目行为不变——兼容维度

既有项目大概率没有 `debt/tech-debt.md`（登记是**新增可选机制**，不是强制存量项目补账）。schema 校验器、回退比对脚本、P8 留痕检查在 tech-debt.md 不存在/为空时必须 **no-op 不报错**，不得新增任何拦截或 WARNING——否则破坏全部存量项目与既有 654 用例全绿基线。这是"登记机制"与"强制存量迁移"的本质区别，是本任务最重要的兼容约束。

### 2.2 归类修正的同步面比主机制更广——多端维度

tech-debt 归类修正不止改 WORKFLOW 目录图一处，需同步：**① WORKFLOW.md 目录图**（L79 子目录数 + L85 agents/ 注释）；**② 工作区初始化 mkdir 三处**（SETUP.md / orchestrator-template.md / state-machine.md）；**③ SETUP/UPGRADING 相关路径表述**；**④ TAG0003 BDD-1 的验收口径**（"包含 8 个子目录"→9）需随本次变更重验——TAG0003 已验收功能不能被本次修正破坏，若 TAG0003 有"初始化创建 8 子目录"的测试/文档断言，须同步更新。漏掉任何一处，就会重新出现"文档说 9、脚本建 8"的归类漂移。

### 2.3 防 Goodhart：P8 只留痕、不达标、不阻断——边界维度

设计核心是"看过并留痕"，**不是**"债务清零才能发布"。BDD 必须写死两个边界：① 留痕结果可为"本次无关注项"（合法选项，不视为空确认失败）；② 存在未关闭 DEBT 条目**不阻断** P8 gate。否则登记机制会激励"为了发布而不登记"。

### 2.4 债 vs 缺陷判据的落地锚点——数据维度

判据（§1.2 第 5 条）三分中，前两条（会→缺陷 / 不会但更贵→DEBT）边界靠人判断，无法完全机器化；但**第三条"都不影响→不登记"必须有合法出口**（否则清单变垃圾场），且**"登记 DEBT 不得豁免当前任务"**必须有硬规则——由 P7 一致性评审人工核对"当前任务验收声明不含依赖已登记 DEBT 解决的表述"，不需新脚本。

### 2.5 止损条件必须被文档引用而非只写进本需求——多端维度

P0-brief known_risks 引用的止损（T001 回填失败=模板错 / P8 空确认 3 次=移除强制）是**机制治理规则**，不是验收行为。需求要求：Phase 1 交付物（模板/校验器/相关文档）必须能让运行方**判断"回填是否无损成功"**；Phase 3 交付物必须能让运行方**统计 P8 空确认次数**——即止损条件要有可观测的数据形态，否则止损条款是空话。

### 2.6 回退信号的可观测性依赖既有格式，零新增埋点——兼容维度

回退比对脚本依赖 `retreat:` 提交前缀 + 诊断文字（agate-retreat-to.sh L63 已强制格式 `retreat: {old_p} -> {new_p}（诊断：...）`，全仓库实测 2 条）。需求不得改变该格式（零新增埋点是设计优点），只做**比对**：git log 提取 retreat 提交 ↔ tech-debt.md `source: retreat` 条目。注意该信号极稀疏（样本 1 起），它只是触发器不是排名工具——本需求不做、也不承诺"发现正在腐烂但未爆雷的债"（设计 §8.3 诚实标注的能力缺口，不粉饰）。

### 2.7 `category` 三分法复用 T001 复盘，不另起枚举——数据维度

设计 §5.1 明确：`category: technical|management|protocol` 复用 T001 复盘的技术/管理/协议三分法（团队已在用），不新造 `type` 七类枚举。这是"复用既有认知负担"而非"设计新分类"。下游单人项目"management"可能无意义——接受该局限（设计 §8.3 第 4 条诚实标注），不在本任务解决。

### 2.8 机制可发现性——多端维度

新机制必须对消费方可见：review 角色卡（至少 plan-eng-review）明写"提债须用标准 DEBT 条目格式"；P8 卡片明写"确认债务清单"步骤；回退规则文档明写"回退落地后必须建 DEBT 条目"。否则 reviewer/releaser 不知道有标准格式与强制要求，机制形同虚设。**强制格式，不强制产出**——review 可不提债，一旦提"后续应重构/存在架构债"必须用标准格式（设计 §7 Q3）。

## 3. BDD 验收条件

### 3.1 功能组 A：debt/ 归类修正（工作区目录）

#### BDD-1: WORKFLOW.md 目录规范中 tech-debt 归独立 debt/ 目录
- Given WORKFLOW.md 的工作区目录规范章节（v2.0 起 8 个子目录）
- When 对照本次归类修正要求检查其目录图
- Then 目录图含 `debt/` 子目录，且 `agents/` 的注释不再包含 tech-debt（agents/ 仅剩 project.md / memory 类 agent 输入知识）

#### BDD-2: 工作区初始化 mkdir 创建含 debt/ 的 9 个子目录
- Given 一个首次接入 agate 的新项目，初始化工作区
- When 初始化过程执行工作区目录创建
- Then 工作区根出现 9 个子目录（roadmap/tasks/agents/archived/reviews/decisions/plans/logs/**debt**），且 SETUP.md / orchestrator-template.md / state-machine.md 三处 mkdir 命令同步为同一 9 子目录集（无一处残留 8 子目录）

#### BDD-3: SETUP/UPGRADING 中 tech-debt 路径表述与独立 debt/ 目录一致
- Given 下游项目按 SETUP.md 接入、按 UPGRADING.md 升级
- When 查询 tech-debt 登记文件的存放位置指引
- Then 相关文档指向 `{AGATE_WORKSPACE}/debt/tech-debt.md`，不存在指向 agents/ 的过期路径表述

#### BDD-4: 既有 TAG0003 工作区验收口径随本次修正重验通过
- Given TAG0003 已验收的"工作区初始化创建规范子目录"行为
- When 重跑与工作区子目录集合相关的既有断言/测试
- Then 验收口径已从"8 子目录"更新为"9 子目录（含 debt/）"且通过，未因本次修正产生回归

### 3.2 功能组 B：DEBT 条目 schema 校验（Phase 1）

#### BDD-5: 合法 DEBT 条目通过 schema 校验
- Given tech-debt.md 含一条 DEBT 条目，其必填字段齐全、枚举值合法、evidence 非空、含 impact/recommendation/closure_criteria（status=closed 时含 task_id 与 P5/P6 证据引用）
- When 对该文件执行 schema 校验
- Then 校验通过，无拦截输出

#### BDD-6: evidence 缺失的 DEBT 条目被拦截
- Given tech-debt.md 含一条 DEBT 条目，其 evidence 字段缺失或为空
- When 对该文件执行 schema 校验
- Then 校验拦截该条目，报"evidence 必填"（evidence 为空不能通过）

#### BDD-7: 非法枚举值被拦截
- Given tech-debt.md 含一条 DEBT 条目，其 category/status/priority 中任一取枚举外值（category 限 technical|management|protocol；status 限 open|in_progress|closed；priority 限 high|medium|low）
- When 对该文件执行 schema 校验
- Then 校验拦截并报非法值

#### BDD-8: closed 状态缺 task_id 或证据引用被拦截
- Given tech-debt.md 含一条 status=closed 的 DEBT 条目，但未填 task_id 或未引用关联任务的 P5/P6 证据
- When 对该文件执行 schema 校验
- Then 校验拦截该条目（closed 准入条件 = task_id + 证据引用，缺一不可）

#### BDD-9: 三态状态机落地——task_id 非空即视为 in_progress
- Given 一条 status=open 的 DEBT 条目被立项、填入 task_id
- When 按状态机语义判定该条目状态
- Then 该条目视为 in_progress（不需额外的 accepted/planned 中间态）；schema 仅允许 open/in_progress/closed 三值

#### BDD-10: 无 tech-debt.md（或为空）时校验器 no-op 不报错
- Given 项目未创建 debt/tech-debt.md（或文件为空）
- When 对该项目执行 schema 校验
- Then 校验器 no-op 正常退出（exit 0），不产生任何拦截或 WARNING（向后兼容，不破坏存量项目）

### 3.3 功能组 C：T001 回填验证模板（Phase 1 试金石）

#### BDD-11: T001 复盘 T1-T4 条目可无损回填为 DEBT 条目并通过校验
- Given T001 复盘（docs/reviews/T001-retrospective-2026-08-10.md）技术原因表的 T1-T4 条目（各含问题/根因/影响）
- When 按 tech-debt 模板回填为 DEBT 条目
- Then 全部条目回填成功并通过 schema 校验，且根因与影响信息无丢失（evidence 引用复盘出处；若连既有条目都填不进模板，即模板设计错误——止损条件 1 的可观测判据）

### 3.4 功能组 D：回退事件强制登记（Phase 2）

#### BDD-12: 协议文档明确"回退落地后必须建 DEBT 条目"
- Given 一次协议内正式回退（`retreat:` 提交，如 P6→P4）完成落地
- When 查阅回退相关协议文档（phase-cards 回退相关卡片 + rules/state-transitions.md 回退规则）
- Then 文档明确要求该回退必须建立 `source: retreat` 的 DEBT 条目（客观事件强制，不依赖任何人判断）

#### BDD-13: git 历史存在 retreat 提交但无对应条目时报 WARNING
- Given 项目 git 历史含 `retreat:` 提交，且 tech-debt.md 中无任何 `source: retreat` 条目与之对应
- When 运行回退覆盖比对检查
- Then 检查报 WARNING 提示缺失的 retreat 提交（不阻断 commit/发布——回退比对是提醒，不是 gate）

#### BDD-14: 已建对应条目时不报
- Given 项目 git 历史含 `retreat:` 提交，且 tech-debt.md 中存在 `source: retreat` 条目并引用该提交
- When 运行回退覆盖比对检查
- Then 检查通过，无缺失提示

#### BDD-15: 回退覆盖检查用真实 retreat 记录做 fixture 可复现
- Given 用全仓库 2 条真实 retreat 提交（023b28b / 29301ad）构造 fixture 场景
- When 分别测试"未建条目"与"已建条目"两种状态
- Then 未建条目时报出缺失、已建条目时通过，两个方向都可复现判定（为 P3 测试提供 fixture 依据）

### 3.5 功能组 E：P8 锚定留痕（Phase 3）

#### BDD-16: P8 发布阶段确认债务清单并留痕
- Given 一个任务进入 P8 发布准备（releaser 按 P8 卡片执行）
- When releaser 产出 P8-release.md
- Then P8 阶段指引要求确认债务清单，且确认结果写入 P8-release.md（含"本次无关注项"这一合法选项）

#### BDD-17: P8 债务确认只查留痕存在、不查内容达标、不阻断发布
- Given P8-release.md 已记录债务确认结果，但存在未关闭的 DEBT 条目（或确认为"无关注项"）
- When 执行 P8 gate 检查
- Then gate 通过（仅验证"确认留痕存在"，不因存在未关闭债务或"无关注项"而拦截发布）

#### BDD-18: P8 空确认次数可观测（止损条件 4 的数据形态）
- Given P8-release.md 连续多次记录"本次无关注项"且无任何后续动作
- When 统计最近发布的债务确认记录
- Then 可观测到"连续 N 次空确认"这一状态（无新增计数脚本也可，但须能通过 P8-release.md 留痕判定，使"连续 3 次空确认=移除强制"可执行）

### 3.6 功能组 F：债 vs 缺陷判据（cross-cutting）

#### BDD-19: 判据文档化且含"不登记"合法出口
- Given 评审/复盘发现质量问题，需决定走"任务内缺陷 / 登记 DEBT / 不登记"
- When 参照协议中的债 vs 缺陷判据
- Then 判据文档明确三分法（"不修它，当前任务的验收声明会不会变成假的？"——会→缺陷走任务内；不会但让未来变更更贵→登记 DEBT；都不影响→不登记），且"都不影响→不登记"是合法出口（防止垃圾场）

#### BDD-20: 登记 DEBT 不得豁免当前任务修复
- Given 某问题被登记为 DEBT 条目
- When P7 一致性评审核对当前任务验收声明
- Then 验收声明不得包含依赖该问题已解决的表述（硬规则由 P7 人工核对，不需新脚本）

## 4. 待确认清单

[NO_NEED_CONFIRM]

- [SUGGEST: T001 回填范围按设计 §6 取技术债 T1-T4（核心试金石）+ 协议原因 A5/A6（扩充 category: protocol 覆盖）——T1-T4 由 P0-brief known_risks[4] 锚定，A5/A6 顺带回填可验证 protocol 分类可用性，成本零；管理原因 M1-M5 不回填（多数是单次事件，非持续债务）]
- [SUGGEST: debt/ 目录的 mkdir 采用静态 9 子目录清单（与既有 8 子目录模式一致），而非懒创建。理由：静态清单与既有 SETUP/orchestrator-template/state-machine 三处模式一致，可 grep 校验；懒创建需要额外逻辑与测试面]
- [SUGGEST: `agate-debt-check.py` 校验器采用与 `agate-frontmatter-check.py` 相同的"stdout 输出错误行 + 薄壳判非空拦截"模式。理由：复用 v0.40.0 已落地的 fail-closed wrapper 模式，不新造轮子（设计 §6 Phase 1 明确"复用既有机制"）]
- [SUGGEST: 回退覆盖比对检查只做 WARNING 不挂 gate。理由：设计 §4.1 把强制点放在"回退落地时建条目"（过程强制），回退比对是事后提醒；挂 gate 会引入"条目格式折腾 commit"的风险，与设计意图不符]

## 5. 裁剪说明

**全流程 P1-P8，无裁剪。** 理由：

- **P2 不可裁**：debt/ 归类修正的同步面清单、schema 字段集合与必填规则、三态状态机到 task_id 的映射、回退比对脚本的判定口径、P8 留痕的检查落点——都是真实设计决策，需要候选方案与独立评审。
- **P3 不可裁**：risk_level=medium；新增 `agate-debt-check.py`/`check-debt.sh` 是真实脚本逻辑，须先写失败 bats 测试（AGENTS.md 工作流：先加失败测试确认红）；回退比对、P8 留痕检查同理。
- **P4/P5 不可裁**：交付底线——模板 + schema 校验器 + 回退比对 + P8 留痕检查 + 文档同步是本任务可发布产物。
- **P6 不可裁**：验收含 T001 回填验证（BDD-11）与向后兼容验证（BDD-10），是本任务质量最后防线。
- **P7 不可裁**：改动横切 WORKFLOW/SETUP/UPGRADING/state-transitions/P8 卡片/check-gate.sh/tests，需一致性交叉核对（含对 TAG0003 已验收行为的回归确认，BDD-4）。
- **P8 不可裁**：本任务产出是 agate 新协议版本的一部分，需版本发布流程。
- **跳过风险评估**：无裁剪，不适用。缺省行为由 BDD-10 保证，非破坏性变更。

## 6. 能力需求声明

```yaml
capability_requirements:
  - need: bash 脚本能力（schema 校验薄壳 + 回退比对 + check-gate.sh P8 分支改动 + bats fixture）
    why: 校验器薄壳、回退比对脚本、gate 分支是核心交付物，协议既有脚本全为 bash 实现
    available:
      - "worktree 环境 bash（既有 check-gate.sh / check-frontmatter.sh / agate-retreat-to.sh 同语言）"
    status: available

  - need: python3 + pyyaml（agate-debt-check.py schema 校验器）
    why: DEBT 条目 schema 校验需 YAML 解析与字段校验，协议既有校验器（agate-frontmatter-check.py / agate-state-yaml-check.py）均为 python3+pyyaml 实现
    available:
      - "Python 3.12 + pyyaml（agate-frontmatter-check.py 在用，已核实）"
    status: available

  - need: bats 测试框架
    why: P3/P5/P6 验证新增校验器/比对脚本/P8 留痕检查的用例（P0-brief test_cmd 指向 agate/tests/unit/agate-debt-check.bats）+ 既有 654 用例回归
    available:
      - "bats ≥1.2.0（worktree 环境已核实，P0-brief test_cmd 基线）"
    status: available

  - need: shellcheck
    why: P5 对改动的 .sh 脚本做静态检查
    available:
      - "shellcheck（worktree 环境已核实）"
    status: available

  - need: git（retreat 提交历史读取）
    why: 回退覆盖比对需从 git log 提取 retreat: 提交；agate 本身依赖 git
    available:
      - "git（worktree 仓库已核实，全仓库 2 条 retreat 记录可作 fixture）"
    status: available
```

本任务无能力缺口（capability_requirements 全部 available）。非 UI 任务，不需要浏览器/视觉能力，无 `requires_minimal_validation`。

## 参考

- 任务简报：P0-brief.md（Phase 1-3 + 归类修正、known_risks 六项、2026-08-12 三次更新）
- 派发指引：P1-dispatch-context-analyst.md（目标/约束/上游关联/输入文件）
- 背景设计：docs/reviews/review-20260812-1204.md（技术债闭环 Phase 1-3、§5 具体规范、§4 强制力、§8 止损——任务内容来源）
- 讨论稿：docs/reviews/agate-project-lifecycle-design-discussion-20260811.md（问题定义与缺口）
- 现状代码：`agate/WORKFLOW.md`（L79-91 工作区目录规范）、`agate/SETUP.md:114` / `agate/orchestrator-template.md:102` / `agate/state-machine.md:40`（mkdir 8 子目录）、`agate/assets/review-roles/plan-eng-review.md:19`（技术债评审提示）、`agate/rules/state-transitions.md`（回退规则）、`agate/scripts/agate-retreat-to.sh:63`（retreat 提交格式）、`agate/phase-cards/P8-release.md`、`agate/scripts/check-gate.sh`（P8 分支 L413-471）、`agate/scripts/agate-frontmatter-check.py`（change_type schema + fail-closed wrapper 模式）、`agate/scripts/check-frontmatter.sh`（薄壳范式）、`agate/scripts/check-p6-format.sh:82`（locale bug 修复参考，v0.40.3 已修）
- 既有任务样例：docs/tasks/TAG0002-refactor-first-class/P1-requirements.md、docs/tasks/TAG0003-workspace-architecture/P1-requirements.md（frontmatter/BDD 风格）
