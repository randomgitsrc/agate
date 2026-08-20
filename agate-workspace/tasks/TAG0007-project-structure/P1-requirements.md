---
phase: P1
task_id: TAG0007
type: problems
parent: P0-brief.md
trace_id: TAG0007-P1-20260820
status: draft
created: 2026-08-20
agent: analyst
# ── v2.0 机器字段 ──
risk_level: high
phases: [P1, P2, P3, P4, P5, P6, P7, P8]
packages: [phase-cards, execution-roles, review-roles, scripts, templates]
domains: [backend]
capability_requirements: []
# 跳过风险: 本任务不裁剪任何阶段，见「裁剪说明」节
---

[NO_NEED_CONFIRM]

已核对 P0-brief 时效性，无漂移。P0-brief.md 的 `env_constraints` 已自带一条 2026-08-18 时效性更新记录（bats→pytest 迁移、network 改为 full），本次核对未发现该记录之后再产生的新漂移；对照 P0 卡片严重判据三条（task 目标方案不再成立 / executor_env 平台前提不再成立 / known_risks 已解决前提失效）均不命中，`HANDOFF-TAG0007.md` 确认的 worktree 基线（1011 pytest passed + consistency 0 ERROR）与 P0-brief 描述一致。

## 1. 需求复述

给 agate 协议新增两个机制，均属"建"（新增机制）而非"修 bug"：

- **RM-AG0008（0→1 项目骨架脚手架）**：项目从零开始时，agate 当前流程（P1 分析需求 / P2 设计本次任务方案）不产出"整个项目目录布局"这一层级的产出物，导致源码/测试/文档/构建产物散落、阶段产出与工程文件不同步。新增机制要求：0→1 项目在早期某个阶段产出一份显式的、按技术栈参数化的目录骨架，作为后续阶段产出的组织依据。
- **RM-AG0009（CODE-MAP + 架构演进纪律）**：agate 当前每阶段（P2/P4）只针对本次任务的局部设计/实现，P7 一致性检查也只核对本次任务范围内的文件，缺少"项目当前架构全貌"的维护物和"新增代码是否符合既定架构"的约束，架构会随版本演进而无防护地漂移。新增机制要求：维护一份 CODE-MAP.md（模块/层/依赖方向/关键文件/约定），在实现阶段随新增文件更新，在一致性检查阶段核对漂移，并对依赖方向偏离给出可见信号。

两者同属"项目结构管理"主题，但生命周期不同：骨架是 0→1 阶段的一次性产出物，CODE-MAP 是伴随项目全生命周期持续更新的维护物。本 P1 的 BDD 因此分两组独立编号，不合并成一条笼统条款。

## 2. 隐含需求识别

| # | 隐含需求 | 为什么必须 |
|---|---------|-----------|
| 1 | 骨架/CODE-MAP 产出物需要一个明确的落盘目录 | WORKFLOW.md「工作区目录规范」当前固定 9 个子目录（roadmap/tasks/agents/debt/archived/reviews/decisions/plans/logs），没有"骨架"或"CODE-MAP"专属位置；也没有明确说这两类产出物该落工作区还是项目根——这是 P0-brief known_risks 已点名的关键决策，P1 需求层面必须显式承认这一空白点存在，具体选址留给 P2（不越权判断） |
| 2 | 骨架模板必须按技术栈参数化，不能把具体技术栈写死进协议本体 | ADR-003「最小约定——不绑定技术栈」是既定架构原则：agate 不硬编码测试框架/语言/部署方式，技术栈相关内容通过项目声明注入。若骨架模板直接写死 `src/components/hooks`（Web）或 `src/include/tests`（C++）作为协议强制目录名，会破坏这条原则，导致非该技术栈的项目无法使用 |
| 3 | "0→1"触发边界需要一个可判定的判据，否则骨架机制会对已有结构的项目重复触发 | RM-AG0008 明确限定"0→1 项目"，agate 自身仓库这类已有既定结构的项目不应被要求重新产出骨架；边界判据是 P2 的设计参数，但 P1 必须先声明"触发边界必须存在且可判定"这一约束，否则 P2 可能遗漏 |
| 4 | 骨架/CODE-MAP 是否需要新执行角色，或复用既有角色 | 现有 execution-roles 只有 7 个（analyst/architect/test-designer/implementer/verifier/vision-analyst/consistency-reviewer），role-system.md 明确"UI 设计节由 architect 兼任产出，不新增 designer 角色，保持角色清单最小化"——这一既定原则同样适用于骨架/架构评审：新机制应优先评估复用 architect（P2 设计职责天然贴合骨架设计与架构合规检查）与 consistency-reviewer（P7 跨文件核对职责天然贴合 CODE-MAP 漂移核对），是否新增角色是 P2 决策，但 P1 必须标出这条既定原则作为约束 |
| 5 | 新增 gate/一致性检测脚本必须遵循 AGENTS.md「改脚本的工作流」（先写失败测试再改绿） | RM-AG0009 的"gate 或 WARNING 检测依赖方向偏离"大概率落地为新脚本或扩展 `check-protocol-consistency.py` 一类既有脚本，这类改动受 AGENTS.md TDD 纪律约束，且触发 SELF-GATE（改 `agate/scripts/*.py`）——这是隐含的过程约束，未来阶段（P3/P4）必须遵守 |
| 6 | 回归底线：现有 1011 pytest 全绿必须在两个机制的实现改动后保持不变 | dispatch-context 约束 3 已明确列出，属"兼容"维度隐含需求——新机制不能以破坏现有测试为代价落地 |
| 7 | change_type: refactor 任务与两个新机制的关系必须被显式检查，不能被默认排除在外 | P1-requirements.md 现有 frontmatter 已支持 `change_type: refactor`（P3/P6 换用不同口径），P0-brief known_risks 第 5 条已点名"code-map 的架构演进纪律要兼容 refactor 类任务"——这是必须被需求层面覆盖的交叉点，具体整合方式（豁免/不豁免/换口径）是 P2 决策，但 P1 需先给出方向性判定（见 BDD-10/BDD-11） |
| 8 | CODE-MAP.md 是项目全生命周期单一维护物，存在多任务/多 worktree 并发更新的边界情形 | CODE-MAP.md 按 RM-AG0009 设计为持续演进、全项目共享的单一维护物；本仓库自身即多 worktree 结构（如当前 TAG0007 worktree），多个任务可能在不同 worktree 并行执行 P4 阶段并各自尝试更新同一份 CODE-MAP.md，存在并发更新/合并冲突风险。P1 层面只声明该边界情形存在，不擅自判断是否属于本次范围；**具体合并策略（锁机制/分段合并/仅主分支可写等）留给 P2 设计**，P1 不越权决定 |

**同类/影响面维度**：见下方「同类扫描」专节（强制节，已单独展开，不在此重复）。

**数据/多端维度**：agate 是纯文档 + 脚本协议，无数据库、无 CLI/API/MCP 多端消费者需要同步——两个新机制的"消费者"是协议自身的 gate 脚本和 subagent 角色，已在隐含需求 4/5 中覆盖，不单列。

**前端维度**：domains 不含 frontend，理由见下方「能力需求声明」节。

## 3. BDD 验收条件

### RM-AG0008：0→1 项目骨架脚手架（一次性生命周期）

#### BDD-1: 0→1 项目产出骨架的存在性
- Given 一个任务被判定为"0→1 新项目"（触发判据由 P2 设计确定，P1 只要求判据存在且可判定）
- When 该任务走完骨架产出所在的阶段
- Then 工作区中存在一份显式的项目目录骨架产出物（目录树声明文件），且该产出物与本项目声明的技术栈相关联

#### BDD-2: 骨架模板技术栈参数化，不硬编码进协议本体
- Given 协议新增的骨架模板文件（`assets/templates/` 下）
- When 检查该模板文件的内容
- Then 模板不出现将具体语言/框架的目录名（如 `src/components`、`src/include`）作为协议强制要求的写法，而是以"按技术栈可选的候选目录集合 + 项目侧声明"的参数化形式表达，具体技术栈的目录选择由项目自己决定

#### BDD-3: 骨架机制不对已有结构的项目重复触发
- Given 一个项目已存在既定的源码/测试/文档目录结构（非 0→1 场景，如 agate 自身仓库、或已进行过多轮迭代的项目）
- When 该项目的新任务进入骨架产出所在阶段
- Then 骨架机制不强制该任务重新产出一份骨架文件，不与该项目已有的目录结构产生冲突性要求

#### BDD-4: 后续阶段产出物落在骨架声明的目录内，偏离需可追溯说明
- Given 项目已产出骨架（BDD-1 已满足）
- When P4 实现阶段新增文件
- Then 新增文件路径落在骨架声明的目录集合内；若确需落在骨架声明范围之外，该偏离在产出物中有显式说明（呼应既有 DESIGN_GAP 机制的可追溯精神，具体是否复用 DESIGN_GAP 由 P2 决定）

#### BDD-5: 骨架机制的实现改动不破坏现有回归基线
- Given 协议为支持骨架机制新增/修改了 phase-cards、execution-roles、scripts 或 templates 下的文件
- When 执行 `python3 -m pytest agate/tests/` 与 `python3 agate/scripts/check-protocol-consistency.py`
- Then 全部现有测试用例（改动前的 1011 个）仍然通过（0 新增失败），一致性检查仍为 0 ERROR

### RM-AG0009：CODE-MAP 架构演进纪律（持续演进维护）

#### BDD-6: CODE-MAP 维护物的存在与初始化
- Given 一个项目采用 CODE-MAP 机制（不限于 0→1，任何采用该机制的项目均适用）
- When 该机制首次启用后（初始化时机由 P2 设计确定）
- Then 工作区中存在一份 CODE-MAP.md，含模块、层、依赖方向、关键文件、约定五类字段，即使初始内容为占位声明也齐全存在

#### BDD-7: P4 新增文件触发 CODE-MAP 更新义务
- Given P4 实现阶段新增了一个不在既有 CODE-MAP.md 记录范围内的文件
- When implementer 完成该 P4 产出
- Then P4 产出中包含对 CODE-MAP.md 的相应更新，或显式声明该新增文件不改变项目架构全貌因而豁免更新的理由；两者必居其一，不允许沉默跳过

**BDD-4 与 BDD-7 关系声明**：两条 BDD 均以"P4 实现阶段新增文件"为同一触发场景，但分属骨架（RM-AG0008）与 CODE-MAP（RM-AG0009）两个独立机制，分别要求满足骨架目录归属与 CODE-MAP 更新两个独立义务。同一文件新增事件需**同时**满足两条验收标准，二者是累加关系，不是互斥或替代关系，不存在"满足其一即可"的情形，也无优先级先后之分。

#### BDD-8: P7 一致性检查核对 CODE-MAP 与实际文件的同步偏离
- Given P4 阶段有文件新增或声明了 CODE-MAP 更新
- When P7 一致性检查执行
- Then 一致性检查逐条核对 CODE-MAP.md 记录与实际新增文件是否同步，未同步的情况被显式标记为需处理项（标记级别——BLOCKER 或 WARNING——由 P2 设计决定，P1 只要求"存在核对动作且结果可见"）

#### BDD-9: 依赖方向偏离检测产生可见信号，不允许静默通过
- Given 新增代码引入了偏离 CODE-MAP.md 已声明的模块依赖方向的改动
- When 相关 gate/一致性检测执行
- Then 至少产生一个可见信号（WARNING 或更强级别，具体级别是 P2 决策），不存在"检测执行了但无任何输出"的静默通过路径

#### BDD-10: change_type: refactor 任务不豁免 CODE-MAP 更新义务
- Given 一个任务在 P1 frontmatter 声明 `change_type: refactor`
- When 该任务涉及模块边界或依赖方向的实际改动（重构本身就是架构变动的高发场景）
- Then CODE-MAP 更新义务同样适用于该任务，不因其走 P3/P6 的"回归口径"而被默认豁免；`change_type: refactor` 的口径调整只影响验证方式（如何验收），不改变"是否需要同步 CODE-MAP"这一义务本身；具体的口径整合方式（是否复用现有 refactor 验收流程的产出位置）是 P2 设计范围

#### BDD-11: CODE-MAP 机制的实现改动不破坏现有回归基线
- Given 协议为支持 CODE-MAP 机制新增/修改了 phase-cards、execution-roles、review-roles 或 scripts 下的文件
- When 执行 `python3 -m pytest agate/tests/` 与 `python3 agate/scripts/check-protocol-consistency.py`
- Then 全部现有测试用例仍然通过（0 新增失败），一致性检查仍为 0 ERROR

## 4. 同类扫描（强制节）

按 P1 卡片「同类扫描」规则，对本任务涉及的关键符号做了全仓 grep（结果来自 dispatch-context objective_info，范围 `agate/`，排除 `agate-workspace/`）：

| 扫描关键词 | 命中数 | 命中详情 | 判定 |
|-----------|-------|---------|------|
| `骨架\|skeleton`（`grep -rniE "骨架\|skeleton" --include="*.md" agate/`） | 6 处 | role-system.md:80「最简骨架」指 prompt 示例简化版；adr.md:81/85「流程骨架」指 P0-P8 阶段流程本身（非项目目录骨架）；WORKFLOW.md:3 同义；vision-analyst.md:168 `skeleton_visible` 是视觉分析字段，与项目目录骨架无关；dispatch-protocol.md:435「极简结构骨架（用于快速对照，非完整正文，实际派发以权威源为准）」，指派发 prompt 模板的简化对照版，与 WORKFLOW.md:3 同类，属流程/派发模板结构的泛化用法 | 全部 6 处均为既有文档中"骨架"作泛化比喻或无关字段使用，**无一处是"项目目录骨架脚手架"这一机制**。判定：本次不处理（不构成同类实例，是全新增补），不影响"全新增补"结论，无需转入 roadmap |
| `CODE-MAP\|code-map\|code_map` | 0 命中 | 无 | 判定：协议库内当前无 CODE-MAP 或同义维护物，RM-AG0009 是全新增补 |
| `架构演进\|架构评审\|依赖方向` | 0 命中 | 无 | 判定：协议库内当前无显式的"架构演进检查"或"依赖方向"校验机制，RM-AG0009 对应部分是全新增补 |

**结论（显式声明，不留空白）**：**已确认只此一处（新增）**——RM-AG0008（骨架脚手架）与 RM-AG0009（CODE-MAP + 架构演进纪律）在协议库内均无同名或同义机制的既有实例，本次是全新增补，不存在"只修被报告的那一处、遗漏其他同类实例"的风险。

**回归拦截声明**：两个机制一旦落地，未来会持续新增触发点（每个新任务的骨架产出、每次 P4 新增文件的 CODE-MAP 更新）——不是一次性修完的存量问题。回归拦截手段已转化为 BDD-5/BDD-11（gate/一致性检查改动不破坏现有测试基线，属新增测试拦截范畴）与 BDD-7/BDD-8（P4/P7 的持续核对机制本身就是对"未来同类遗漏"的拦截手段）。

## 5. 机制一致性/候选接入点盘点

基于 dispatch-context objective_info 给出的现有机制清单，对 RM-AG0009 提到的"P7 一致性检查""P2 架构评审""gate 检测依赖偏离"以及 RM-AG0008 的骨架落点做候选接入点盘点（P1 只盘点，不做具体设计，为 P2 铺垫）：

| 既有机制 | 候选接入点 | 涉及机制 | 交叉说明 |
|---------|-----------|---------|---------|
| phase-cards/P0-orchestrator.md、P1-requirements.md | 骨架产出放哪个阶段（P0 亲自写 vs P1 analyst 产出）是 P0-brief known_risks 已点名的关键决策 | RM-AG0008 | P1 只需承认这一空白，具体放哪个阶段留 P2 |
| phase-cards/P2-design.md | 新增"架构演进检查"维度（新文件属哪层/依赖合规/复用抽象），可能作为 P2 产出规格新增字段（类比现有 `packages`/`domains`/`ui_affected` 字段模式） | RM-AG0009 | P2-design.md 当前已有结构化字段机制（frontmatter），是新增字段的自然落点 |
| phase-cards/P7-consistency.md「跨文件一致性」检查项（现有第 3 条：packages 与 bump 范围一致 / BDD 与验收数量匹配 / 实现路径与设计吻合） | 候选扩展点：新增第 4 类核对——CODE-MAP.md 记录与 P4 实际新增文件是否同步 | RM-AG0009 | 该检查项当前只覆盖"本次任务范围内"的一致性（P0-brief issue 已指出这一局限），CODE-MAP 核对需要引入"项目全貌"视角，是对现有检查范围的扩展而非替换 |
| execution-roles/architect.md（P2 设计职责） | 候选角色：复用 architect 承担骨架设计 + 架构合规检查产出，理由见「隐含需求识别」第 4 条（role-system.md 既定原则：优先复用已有角色，不轻易新增） | RM-AG0008 + RM-AG0009 | 是否新增专属角色是 P2 决策 |
| execution-roles/consistency-reviewer.md（P7 跨文件核对职责） | 候选角色：CODE-MAP 漂移核对天然贴合该角色现有职责范围 | RM-AG0009 | 同上，P2 决策 |
| review-roles/plan-eng-review.md（domains:backend 机械映射已触发，见 role-system.md 评审角色机械映射表） | "设计模式合理性维度"（P0-brief 修复③）可能落在该评审角色的评审维度扩展 | RM-AG0009 | 本任务 domains 声明为 backend，plan-eng-review 已按机械映射规则自动触发，无需额外声明 |
| scripts/check-protocol-consistency.py、check-gate.py 及同家族一致性/状态脚本（objective_info 已列出：check-state-transition.py、check-state-yaml.py、agate-evidence-consistency.py、agate-frontmatter-check.py） | gate 检测依赖方向偏离，大概率新增同家族脚本或扩展其一 | RM-AG0009 | 新脚本/扩展受 AGENTS.md TDD 纪律约束（见隐含需求第 5 条） |
| assets/templates/（现无"项目骨架模板"或"CODE-MAP 模板"） | 需新增模板文件（如骨架模板、CODE-MAP 模板），需符合 ADR-003 参数化原则 | RM-AG0008 + RM-AG0009 | 见 BDD-2 |
| P1-requirements.md 现有 `change_type: refactor` frontmatter 机制（P3-tdd.md、P6-acceptance.md 已声明的换口径逻辑） | RM-AG0009 架构演进纪律需要声明与该机制的关系（本 P1 判定为"不豁免"，见 BDD-10） | RM-AG0009 | 已在 BDD-10 覆盖需求侧含义，具体口径整合是 P2 决策 |
| WORKFLOW.md「工作区目录规范」（9 固定子目录：roadmap/tasks/agents/debt/archived/reviews/decisions/plans/logs） | CODE-MAP.md / 骨架产出物落哪个目录未定义，是新增决策点（沿用现有「内容边界判据」——是否由 agate 编排流程生成/消费来判断落工作区还是项目 docs/） | RM-AG0008 + RM-AG0009 | 见隐含需求第 1 条 |

## 6. 待确认清单

[NO_NEED_CONFIRM]

本次分析未发现需要人工拍板业务方向的真无方向点。所有识别出的关键决策点（骨架落哪个阶段、CODE-MAP 落哪个目录、是否新增专属角色、gate 检测的具体级别）均属"技术方案选型"范畴，且 P0-brief known_risks 与 dispatch-context 约束已明确这些决策点应由 P2 设计阶段处理，P1 已用 BDD/隐含需求/候选接入点三节显式标出这些决策点的需求侧含义，不构成阻塞。

## 7. 裁剪说明

**不裁剪任何阶段**，`phases: [P1, P2, P3, P4, P5, P6, P7, P8]`（frontmatter 已声明）。理由：

- 两个机制均为协议新增（"建"而非"修"），P0-brief known_risks 已明确"两个都是'建'（新增机制），不是'修'——需完整 P0-P8，不能 plan 硬做"
- 按 WORKFLOW.md「改动性质判断」，本任务属于**机制交叉**（触及 P2 架构评审设计、P7 一致性检查、TAG0002 的 `change_type: refactor` 分流三处既有机制），机制交叉级别的改动"必须走完整 agate"，无裁剪空间（ADR-005）
- P1/P2/P4/P5/P6 本身是核心阶段，协议规则下不可裁
- P3（TDD）保留：新增/扩展 gate 一致性脚本受 AGENTS.md「改脚本的工作流」（先写失败测试再改绿）约束，跳过 P3 无正当理由
- P7（一致性）保留：本任务改动横跨 phase-cards / execution-roles / review-roles / scripts / templates 五类文件，天然需要跨文件一致性核对；且改动主题本身就是"一致性/架构核对机制"，若本任务自己跳过 P7 会削弱说服力
- P8（发布准备）保留：协议本体改动涉及 version bump + CHANGELOG 更新，触发 SELF-GATE，需走完整发布流程

`risk_level: high` 的理由：改动影响面覆盖协议核心的多个既有机制（P2 设计规格、P7 一致性检查、角色体系、gate 脚本家族），且落地后会影响所有后续任务的执行方式（每个 0→1 任务的骨架产出、每次 P4 实现的 CODE-MAP 更新义务），属于协议自身的机制性变更，不是局部功能改动；`risk_level: high` 触发 P2 阶段 plan-eng-review 必须独立派发（check-gate.py 对 `agent=main` 硬拦截），与「不愿意一轮一轮来回改」的用户诉求相符（P2 设计从一开始就走最严格评审强度）。

`domains: [backend]`：本任务改动对象是 agate 协议本体（phase-cards / execution-roles / review-roles / scripts / templates），不是面向最终用户的可视化 UI；按"协议开发者作为使用者"的视角判断，协议开发者与新机制的交互方式是读 Markdown 文档、跑命令行 gate 脚本，不涉及浏览器渲染、视觉呈现、交互动效等 UI/UX 范畴，因此不声明 `frontend`。也不声明 `mcp`（无 MCP 接口改动）或 `security`（无认证/权限/加密改动）。`domains: [backend]` 按 role-system.md 评审角色机械映射表将自动触发 P2 的 plan-eng-review 与 P4 后的 review，与 `risk_level: high` 共同构成本任务的评审强度基线。

## 8. 能力需求声明

```yaml
capability_requirements: []
```

理由：本任务是协议文档（phase-cards/execution-roles/review-roles/templates）与 gate/一致性脚本（scripts/*.py）的改动，不涉及浏览器行为、视觉渲染、外部系统交互或其他需要特殊验证能力的场景。验证方式是标准的 `pytest` 单元/回归测试 + `check-protocol-consistency.py` 一致性检查（均为命令行文本输出，当前执行环境已具备）。不适用 `requires_minimal_validation: true`（无浏览器安全模型/外部系统行为依赖）。domains 不含 frontend，因此不适用 P1 gate 的 vision 能力硬性声明要求（`_gate_p1_vision_capability`）。

`env_constraints.debug_env` 已声明"本环境为 Linux；可在本仓库自举验证（agate 自己就是 0→1 项目的骨架案例）"，`HANDOFF-TAG0007.md` 确认 worktree 环境已完整就绪（依赖齐全、基线全绿），不存在"环境未准备好"的缺口，因此不声明 `verification_env`（缺的不是环境，是设计方案本身——落哪个阶段/落哪个角色，这些是 P2 设计范畴，不是环境准备范畴）。
