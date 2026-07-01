# agate 竞品分析报告

> 分析对象：`agate`(https://github.com/randomgitsrc/agate)——面向软件工程的 AI Agent 工作流协议
> 报告日期：2026-07-01
> 方法：结合项目源码/评审历史的既有理解 + 对各竞品的最新网络调研(2026 年 7 月前信息)
> 定位：本报告不是学术综述，是面向 agate 后续演进决策的实用参考

---

## 一、agate 自身定位速记

agate 是一套**纯 Markdown 协议**，运行在 Claude Code / OpenCode 这类已有 subagent 派发能力的编程 agent 之上，核心机制：

- **P0-P8 阶段流转**：主 Agent 派发 subagent、阶段 gate 验收、状态落盘(`.state.yaml`)
- **上下文隔离**：subagent 只按路径读取文件，不共享主 Agent 上下文
- **机器可判定 gate**：exit code 判定（不是自然语言报告），区分"外部产出 gate"（不可伪造）和"自写文件 gate"（可伪造，需缓解措施）
- **诚实自我文档化**：`LIMITATIONS.md` 主动列出协议局限，不做营销式包装

项目自己的定位声明——"agate 是一套轻量文档协议，不是代码框架……这条路线选择带来了真实价值（零基础设施、Agent 能读文件就能用），也继承了这条路线结构性的弱点"——是理解本报告所有对比的前提：**agate 不和"构建 AI 应用的运行时框架"同场竞争，它和"让编程 agent 更可靠地工作"这一类工具同场竞争。**

截至本报告撰写时，v0.6（P2 不可裁剪 + superpowers 借鉴）已从设计文档演进为实际代码提交，经过 7 轮迭代评审（覆盖设计层论证、hook 实现细节、全文一致性同步），过程本身即是协议工程严谨度的证据。

---

## 二、竞品全景分类

```
                    同源移植但架构分叉
                    ┌─────────────┐
                    │   gstack    │  单实例角色切换，非真正多 agent
                    └─────────────┘

  纪律层（互补，非竞争）           协议层（真正的同类竞品）
  ┌─────────────┐              ┌─────────────────┐
  │ Superpowers  │              │  GitHub Spec Kit │ ← 最值得关注
  └─────────────┘              │ agentic-dev-process│
                                └─────────────────┘

  应用运行时框架（不同战场，参考价值 > 竞争关系）
  ┌───────────┐  ┌─────────┐  ┌─────────────┐
  │ LangGraph │  │ CrewAI  │  │Augment Cosmos│
  └───────────┘  └─────────┘  └─────────────┘
```

---

## 三、逐项分析

### 3.1 gstack — 血缘最近，但已分道扬镳

agate 的 9 个评审角色（investigate、cso、qa 等）直接移植自 gstack，但两者现在是不同物种。

**核心事实**：
- Y Combinator CEO Garry Tan 于 2026 年 3 月开源个人 Claude Code 配置，几周内 6.6 万 star，打包 23 个专家技能、8 个强力工具，截至 4 月已是 v0.15.14.0，204 次提交，9100 fork，MIT 协议
- **架构本质**：gstack 用单个 Claude Code 实例根据调用哪个 SKILL.md 切换角色，是"人工编排的角色专业化"，不是"自主多 agent 协调"——需要人来手动串联每一步
- 并行能力依赖外部工具 Conductor（跑多个隔离 git worktree 的 Mac 应用），不是 gstack 自身特性

**与 agate 的本质差异**：agate 是真的派发独立 subagent（各自隔离上下文窗口），gstack 是单实例换人设。

**结论**：不算直接竞品——解决的是不同层的问题（gstack 优化"怎么把一个 agent 装扮成一个团队"，agate 优化"怎么让多个真正独立的 agent 互相制衡"）。gstack 的体量证明了"单实例角色切换"路线可以做得很大，但那是完全不同的赌注。

---

### 3.2 Superpowers — 互补关系，结论稳固

8.9 万+ star 的 agentic 技能框架，强制 TDD、结构化规划、subagent 驱动开发。

**核心机制**：技能按场景自动触发（brainstorming → writing-plans → TDD → systematic-debugging），也有类似 agate 的隔离机制：为计划里每个任务派发全新 agent，只接收任务描述和相关上下文，不接收完整对话历史。

**与 agate 的分野**：Superpowers 是"指令说做什么不说怎么做"的技能触发系统，靠关键词/场景自动激活，依赖单个 agent 会话内的"纪律"；agate 是**外部状态机**驱动，`.state.yaml` + gate exit code 判定，不依赖 agent"记得要遵守"。

**结论**：纪律层 vs 结构层的正交关系，互补而非竞争。v0.6 计划已打算在文档里正式写"推荐伴侣：superpowers"。

---

### 3.3 LangGraph — 应用运行时框架，非直接竞品，但揭示 agate 能力天花板

**规模**：v1.0 于 2025 年底 GA，3 万+ star，Klarna、LinkedIn、Uber、Replit 等生产环境使用；DeltaChannel 优化号称把 checkpoint 存储压缩最多 7.3 万倍；LangGraph Studio 提供图可视化调试、逐节点执行、任意 checkpoint 回放。

**架构本质**：低层级编排框架，把 agent 逻辑建模成状态机（图）——节点代表动作，边定义条件转移逻辑。这是一个**要导入并用 Python 编程的库**，不是**部署给 agent 读的协议文档**。

**概念对应关系**：

| LangGraph 概念 | agate 对应物 | 差距 |
|---|---|---|
| StateGraph + 条件边 | P0-P8 阶段流转 + gate exit code | LangGraph 是编译期图对象，agate 是 grep/bash 脚本判定 |
| Checkpointing（Postgres/SQLite） | `.state.yaml` | LangGraph 支持崩溃后精确恢复，agate 是纯文本约定，无事务保证 |
| `interrupt()` 人机协作暂停 | PAUSED 状态 + 人工介入 | 概念一致，LangGraph 有运行时原生支持 |
| LangSmith 追踪 | 无 | 对应 agate 自认的"局限 4：subagent 活动不可观测" |

**战略判断**：agate 的 dispatch-protocol + state-machine 本质上是"用 Markdown 和 shell 脚本手写实现了 LangGraph 用编译型状态机原生提供的东西"。**真正的风险不是被 LangGraph 抢用户（场景完全不同），而是：如果 agate 想要真正的并行、真正的崩溃恢复、真正的可观测性，那条路径的终点很可能是"重新发明 LangGraph"，而不是继续往协议里加 bash 脚本。** 这是"零基础设施"承诺的天花板，值得在协议演进规划里明确写下来。

---

### 3.4 CrewAI — 角色模型高度相似，隔离粒度是关键分野

**规模**：10 万+ 开发者通过社区课程认证；企业版 AMP Factory 支持私有化部署、SSO（MS Entra/Okta）、RBAC、专属 VPC；2026 年新增 SOC 2 Type II 认证，标志着从"开发者玩具"跨入"生产基础设施"；号称某些任务上比 LangGraph 快 5.76 倍。

**架构**：Crews（角色化 agent 自主协作）+ Flows（事件驱动精确工作流控制）。五个核心构件：Agent（role/goal/backstory）、Task、Tool、Crew、Flow。

**角色模型对比（最值得细看的一点）**：CrewAI 给每个 agent 一个 role/goal/backstory，backstory 塑造 agent 如何推理和沟通——这和 agate 的 `architect.md`/`implementer.md` 角色文件是同一个直觉：给 agent 稳定人设减少行为漂移。但**隔离粒度不同**：

- CrewAI 的 agent 是同一 Python 进程内的对象，共享解释器状态，"记忆"是框架层维护的向量存储，不是真正独立的上下文窗口
- agate 的 subagent 是宿主 CLI 工具原生派发的独立实例，真正拥有隔离的上下文窗口

**结论**：这一点上 agate 的隔离保证实际比 CrewAI 更硬——不是设计更精巧，而是 CrewAI 要在单进程里模拟"团队协作"天然做不到进程级隔离，agate 直接借用宿主工具的原生 subagent 机制白捡了这个保证。但 CrewAI 在产品化程度上远超 agate（可视化构建、企业 IAM、合规认证、执行速度基准）——这些不是 agate 现阶段该追的方向，但反映了"角色化协作"概念一旦要产品化需要补多少工程量。

---

### 3.5 Augment Cosmos — 不同量级的参照系

**定位**：组织级云 agent 平台，2026 年 5 月公开预览，$200/开发者/月（MAX 套餐）或企业定价，协调人、agent、代码、工具、策略和记忆。

**核心差异维度**：Cosmos 解决的是"跨任务、跨会话的知识复用"——agate 的 `.state.yaml` 是单任务状态机，任务结束后知识不沉淀。Cosmos 的 Expert Registry 想解决"下次遇到类似问题怎么办"，这是 agate 完全没碰的维度。

**结论**：不构成竞争，但提示了一个方向参照——如果 agate 未来要做跨任务知识复用，会牺牲"零基础设施"的核心卖点，需要想清楚要不要付这个代价。

---

### 3.6 agentic-development-process — 同类定位但工程化程度更浅

Master Orchestrator 协调多个并行 agent，用 git worktree 做真并行开发。这套流程 2025 年 10 月独立总结自真实生产开发，后来发现和 Anthropic 发布的《Effective Harnesses for Long-Running Agents》高度相似。

**与 agate 差异**：它是协调约定（worktree + 状态文件 + Master 审查合并），没有 agate 的 gate 分类体系（可判定 vs 需人工判断）、没有 self-authored gate 风险意识、没有 P6/P7 那种"证据存在性 + 一致性双重防伪"设计。工程严谨度明显浅于 agate 现阶段。

---

### 3.7 GitHub Spec Kit — 本报告最重要的结论：唯一真实同类竞品，且优势正被追赶

#### 规模（不是一个量级）

截至 2026 年 6 月 11 日，111k star、9.8k fork，MIT 开源，2 月底以来发布 55+ 版本——对 GitHub 官方维护项目来说迭代速度不寻常。支持 30 多个 AI 编程 agent 集成（Copilot、Claude Code、Cursor、Gemini CLI、Codex CLI 等），agent 无关是最强定位优势。

#### 架构高度重合

Spec → Plan → Tasks → Implement 四阶段，每阶段产出 Markdown 产物喂给下一阶段——和 agate"阶段产出物驱动下一阶段"的核心直觉完全一致。也有类似 P3 红灯门槛的强制：TDD 未通过（红灯）前不允许写实现代码。

#### 关键发现：Spec Kit 社区正在公开请求 agate 已经原生具备的能力

这是本轮调研最重要的一条。Spec Kit 的 GitHub Issue/Discussion 里有用户明确提出：Claude Code 的每个 subagent 运行在独立隔离的上下文窗口里——这是解决上下文问题的关键，当前斜杠命令编排复杂工作流会拖累主 agent、弄乱对话历史。另一处讨论描述了几乎和 agate 设计动机逐字重复的痛点：多轮 spec 修订后上下文窗口变长，需要让 subagent 实际干活、只向主 agent 汇报摘要。

GitHub 目前的回应还只是局部的——最近版本加了"让 `/analyze` 在 fork 出的 subagent 里跑"，只解决了**一个命令**，不是 agate 那种**贯穿全部 8 个阶段**的系统性隔离。

**这意味着 Spec Kit 现在处于"知道这个问题、正在补、但还没补完"的阶段，而这恰恰是 agate 从第一天就内置的核心机制。如果 GitHub 团队（资源远超一个人维护的开源协议）把这块补齐，agate 相对 Spec Kit 剩下的差异化优势会进一步收窄。**

#### Spec Kit 独立评测指出的弱点

- CLI 表面频繁变动——v0.10.0 直接移除整个 `--ai` flag 系列，之前的教程/脚本大量失效
- spec 开销可能超过收益——多模块存量系统上"产出体量而非准确度"
- 对探索性工作太僵硬——阶段化门槛适合需求明确的功能，研究型工作会和结构打架
- **串行执行，没有原生多 agent 并行化**——这条 agate 自己也有同样短板，不是差异化优势，是两者共同的问题

#### 生态背景（间接相关但影响战略判断）

这一整类"agentic 协议/技能"品类过去四个月从实验变成基础设施——官方市场、六位数安装量、SKILL.md 被约 40 家客户端采用。核心理念（工作流门槛、subagent 隔离、渐进式披露）都赢了，剩下的未解决问题是规模化之后的问题：内容审核、安全、多 agent 协调标准。

**安全维度已从"值得关注"变成"危机"**：市场上超过 13% 的技能包含关键漏洞，某项研究在某技能市场里发现 36% 的技能存在 prompt injection，安全研究者已绕过多家平台的自动化恶意技能扫描器。这和 agate 现在的形态关系不大（还没做成市场化分发），但如果未来考虑做成可安装插件市场，是必须提前设计的风险。

---

## 四、对比矩阵

| 维度 | **agate** | gstack | Superpowers | Spec Kit | LangGraph | CrewAI | Cosmos |
|---|---|---|---|---|---|---|---|
| 类别 | 编程 agent 协议 | 角色切换技能包 | 行为纪律技能包 | 编程 agent 协议 | 应用运行时框架 | 应用运行时框架 | 企业级 agent 平台 |
| 执行模型 | 多 subagent 真派发，上下文隔离 | 单实例角色切换，人工串联 | 单会话+技能触发，支持 subagent 派发 | 文档驱动，agent 自选如何执行 | Python 状态图 | 单进程内 Crew 协作 | 云端多 agent 协调 |
| 状态持久化 | `.state.yaml` 状态机 | 会话内隐式+JSONL 日志 | 无独立状态文件 | Markdown 产物链 | Postgres/SQLite checkpointing | 向量记忆+SqliteProvider | 组织级持久记忆 |
| Gate 机制 | 机器可判定 exit code + self-authored gate 分类 | 无 | 技能内软约定 | `/speckit.analyze` 非硬拦截 | 无（需自建） | Task guardrails | 平台内置策略控制 |
| subagent 隔离粒度 | 全阶段原生隔离 | 无（单实例） | 有 | 仅 1 个命令（`/analyze`），社区仍在请求全面隔离 | N/A（自建） | 同进程内，非真隔离 | 平台层隔离 |
| 并行执行 | 无（纯串行） | 依赖外部 Conductor | 有限 | 无（社区评测明确指出的弱点） | 原生支持 | 原生支持 | 原生支持 |
| 可观测性 | 无（自认局限 4） | 会话追踪+操作日志 | 无独立体系 | 无独立体系 | LangSmith 全链路追踪 | AMP 实时追踪 | 内置 |
| 许可/成本 | 未标注（仓库无 LICENSE 声明冲突待查） | MIT，免费 | 开源免费 | MIT，免费 | MIT，平台付费 | 开源免费，AMP 企业付费 | $200/人/月起 |
| 规模（2026-06） | 个人项目量级 | 数万 star | 8.9 万+ star | **11.1 万 star** | 3 万+ star | 10 万+开发者认证 | 企业级预览产品 |
| 自我局限文档 | **有**（`LIMITATIONS.md` 主动写局限） | 无 | 无 | 无 | 无 | 无 | 无（营销向） |

---

## 五、综合判断

**判断一：agate 和 LangGraph/CrewAI 不是同一战场的竞品，但需要在文档里主动划清这条界限。** 两者解决"怎么写一个 agent 驱动的应用"，agate 解决"怎么让编程 agent 可靠地写你的代码"。这个边界 agate 已经在 `LIMITATIONS.md` 里隐含划清，但 README 目前只说"不需要 Python/数据库/部署服务"，没有正面提及这两个最容易被误认为同类的项目——容易被浅层对比的人问"为什么不用 LangGraph 重写"。

**判断二：GitHub Spec Kit 是目前唯一一个规模、路线、架构都和 agate 高度重合的真实竞品，而且它的差距正在被主动补上。** 111k star 对 agate 现在的体量不是一个数量级。agate 相对它的核心优势——贯穿全阶段的 subagent 隔离、机器可判定的 gate（不是分析报告）、self-authored gate 风险分类意识——都是真实、可验证的优势，但都不是长期稳固的护城河，因为 Spec Kit 社区已经在明确要求第一条，GitHub 的工程资源足够快速补齐。

**判断三：agate 的角色隔离保证在架构上比多数框架（尤其 CrewAI）更硬，这一点被低估，应该主动作为卖点讲清楚。** 不是设计更精巧，是白捡了宿主 CLI 工具的原生能力——但这也意味着这个优势依赖 Claude Code/OpenCode 这类宿主工具持续提供原生 subagent 能力，本身是一种依赖风险，值得留意。

**判断四："纯串行、无并行"是 agate 和 Spec Kit 共同的短板，且市场正在往并行方向收敛。** Cosmos、agentic-development-process、gstack+Conductor、LangGraph、CrewAI 全部原生支持并行，Spec Kit 独立评测也把"没有原生并行"列为明确弱点。agate 如果长期不动，会从"和 Spec Kit 打平"变成"落后于两个方向"。

**判断五：可观测性是全品类的标配，agate 是少数几个完全空白的。** LangGraph 有 LangSmith，CrewAI 有 AMP 实时追踪，gstack 有会话追踪+操作学习日志。agate 的"局限 4：subagent 活动不可观测"已经写了很久但没有对应的补强计划。

---

## 六、建议与路线

### 优先级：高

1. **把"gate 防伪造体系"确立为 agate 最外显的卖点，写进 README 首屏，而不是藏在实现细节里。** 这是目前唯一一条 Spec Kit（靠分析报告）、CrewAI/LangGraph（靠框架层 guardrail，非协议层 gate）都没有对应物的能力。如果 Spec Kit 先把 subagent 隔离补齐，这条会是 agate 剩下能打的核心差异化点。

2. **在 README/`AGENTS.md` 里主动划清和 LangGraph/CrewAI 的边界。** 明确写"我们不是这两者的替代品，而是运行在 Claude Code/OpenCode 之上的工作方法论"，减少被浅层对比误判为竞品、进而被质疑"为什么不用现成框架重写"的概率。

3. **持续跟踪 Spec Kit 的 subagent 隔离进展**（issue #752、discussion #912、以及 `/analyze` 已经 fork 到 subagent 这条 PR 线）。这是唯一一个"竞品正在明确补齐 agate 核心优势"的可验证信号，值得设一个定期复查节奏（比如每次 pull agate 主分支时顺带查一次）。

### 优先级：中

4. **规划一个最小化的可观测性方案，不违反"零基础设施"原则。** 不需要 LangSmith 级别的全链路追踪，哪怕是一个纯读 `.state.yaml` 生成时间线的脚本（本地跑、无外部依赖），也能补上"局限 4"这个长期存在但一直没动的空白。

5. **正视纯串行的短板，评估一个轻量并行方案的可行性。** 不需要照搬 Cosmos/CrewAI 的运行时并行，可以参考 gstack+Conductor、agentic-development-process 的思路——用 git worktree 做任务级并行，主 Agent 仍然串行判定 gate，但允许多个独立任务的 subagent 同时跑在不同 worktree 里。这个方向和"纯文档协议、零基础设施"原则不冲突（worktree 是 git 原生能力）。

### 优先级：低（暂不建议投入）

6. **不建议现在就卷"技能市场分发"这条路。** 观察到的安全危机（13%+ 技能含关键漏洞、部分市场 36% prompt injection）说明这条路线现在踩坑代价很高。agate 保持"仓库 clone + 软链接"的朴素分发方式，短期内反而是相对安全的选择。

7. **不建议因为 LangGraph/CrewAI 的产品化程度（可视化构建、企业 IAM、合规认证）而跟进对应功能。** 这些是不同战场的军备竞赛，agate 的核心用户画像（单开发者/小团队、用编程 agent 写自己的代码）不需要这些能力，跟进只会稀释"零基础设施"的核心卖点。

---

## 七、一句话总结

**agate 现在最大的机会窗口，是在 Spec Kit 把 subagent 全阶段隔离补齐之前，把"机器可判定 gate + self-authored gate 风险分类"这条护城河明确讲清楚、讲响亮；最大的隐患，是纯串行和可观测性缺失这两个全品类都在补的短板，agate 目前都还没有对应计划。**
