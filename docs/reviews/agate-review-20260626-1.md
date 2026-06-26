# agate 专家评审意见与修改计划

> 评审对象：agate v1.2.0（AI Agent 编排协议）
> 评审范围：仓库全部 52 个 Markdown 文件 / 8356 行，含 assets 角色与模板、archived 验证报告、docs 全部 design-notes / plans / reviews，以及 git 提交历史
> 评审日期：2026-06-26
> 评审定位：把缺陷转化为可执行的 issue / PR 清单，每条带文件定位、根因、修法、验收标准

---

## 0. 评审结论速览

agate 是当前自我反思最诚实的开源 agent 协议——它的 `LIMITATIONS.md` 与 `docs/design-notes/` 几乎预判了所有结构性缺陷。但「诚实记录缺陷」与「修复缺陷」是两回事。本次评审挖出的低级错误（LICENSE 缺失、死引用、YAML 不可解析、脚本不存在、清单计数对不上）恰好实证了它自己承认的「局限 5：协议文档自身一致性不在流程内」——**一个教别人「gate 必须机器可判定」的项目，自己的文档一致性却全靠人肉维护。**

| 严重度 | 数量 | 典型问题 |
|--------|------|----------|
| 🔴 阻断级 | 4 | 评审角色违反核心模型、LICENSE 缺失、YAML 不可解析、脚本依赖未声明 |
| 🟠 高 | 4 | 清单计数不一致、字段集三处不一、死文件引用、行号引用失效 |
| 🟡 中 | 5 | 协议自重过大、单点故障传染性、gate 全局可规避、并行缺失、启动上下文压力 |
| 🟢 优化 | 6 | 一致性脚本、精简启动路径、独立数据源、可执行化 harness 等 |

**修复优先级一句话**：先补 LICENSE + 修评审角色冲突（伤一致性最重），再上结构一致性检查脚本（治本）。

---

## 1. 🔴 阻断级问题（必须先修）

### P0-1 评审角色「改代码 / 提交」违反 agate 核心模型

**定位**
- `assets/review-roles/qa.md` L19：`发现 bug → 定位根因 → 修复代码 → 原子提交 → 重新验证 → 继续`
- `assets/review-roles/design-review.md` L10：`设计师的眼睛 + 前端工程师的手。找视觉 bug、交互问题，然后直接改代码。`
- `assets/review-roles/review.md`：`机械性修复（typo、死代码、CSS 小问题）→ 直接说怎么改`（措辞较轻，但仍暗示评审角色动手）

**根因**
这三个角色从 gstack（MIT）原样提取，提取时未与 agate 的「执行/评审分离」模型对齐。agate 的铁律是：
- 评审角色**只审不写**（`role-system.md` 第二层定义）
- 只有执行角色产出文件（`WORKFLOW.md` 原则 1）
- **git commit 只由主 Agent 做**，subagent 不碰 git（`git-integration.md` 规则 1）

一个 P5 的 `qa` subagent 若真的「修复代码 + 原子提交」，**同时违反三条铁律**。这是移植债，不是笔误。

**影响**
协议自相矛盾会让主 Agent 在派发 qa/design-review 时无所适从：到底让它改还是不让它改？实践中要么评审角色越权写代码污染 P4 产物，要么主 Agent 忽略角色定义——两种结果都侵蚀协议的可信度。

**修法**
将三个角色统一改造为「只产出问题清单 + status，修复回执行角色」：
- `qa.md` 循环流程改为：`发现 bug → 定位根因 → 在报告中给出修复建议 → 主 Agent 回派 implementer 修 → P5 重跑验证`
- `design-review.md` 定位改为：`设计师的眼睛 + 前端工程师的判断力。找视觉/交互问题，产出带文件定位和 Fix 建议的清单，由主 Agent 回派 implementer 落地。`
- `review.md` 处理规则改为：所有修复（含机械性）都只「说怎么改」，写进评审文件，不直接动代码
- 三个文件都已有「门槛产出（status 映射）」节，保留即可——它们本就应该只产 status，不产代码

**验收标准**
- `grep -rn "改代码\|修复代码\|原子提交\|直接改" assets/review-roles/` 返回空
- 三个角色的「认知模式 / 流程」节明确写「不写代码、不 commit，修复回执行角色」

---

### P0-2 README 的 LICENSE 徽章指向不存在的文件

**定位**
- `README.md` L7：`[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)`
- 仓库根目录**无 `LICENSE` 文件**（`ls LICENSE*` 报 No such file）

**根因**
徽章和文字都声明 MIT，但从未落地实际的 license 文件。

**影响**
1. 徽章链接 404
2. **法律上 license 缺失**——没有 LICENSE 文件，默认是「保留所有权利」，别人 clone 使用处于灰色地带，与 README「鼓励 clone 到 ~/.agate 使用」的定位冲突
3. agate 提取了 gstack（MIT）的 9 个评审角色，MIT 要求**保留原始版权与许可声明**——当前 `role-system.md` 只写了「原始来源：gstack by Garry Tan」，未附 MIT 全文，合规性存疑

**修法**
1. 在仓库根创建 `LICENSE`（MIT 全文，填写 agate 作者与年份）
2. 在 `LICENSE` 或 `NOTICE` 中附加一段：声明 `assets/review-roles/` 下 9 个角色改编自 gstack（garrytan/gstack, MIT），保留其版权行
3. 校验徽章链接可达

**验收标准**
- 根目录存在 `LICENSE`，内容为合法 MIT
- gstack 来源的 MIT 归属在 `LICENSE`/`NOTICE` 中明确保留

---

### P0-3 vision-analyst 的 YAML 结构示例不可解析

**定位**
`assets/execution-roles/vision-analyst.md`「完整 YAML 结构」代码块：

```yaml
vision_analysis:
    screenshots: [...]        # ← 缩进 4 空格
    purpose: "acceptance"     # ← 缩进 4 空格
    ...
  viewports:                  # ← 缩进 2 空格（与上面 4 空格不一致）
    - id: "desktop"
  responsive_comparison:      # ← 缩进 2 空格
  summary:                    # ← 缩进 2 空格
```

**根因**
顶层 key `vision_analysis:` 的直接子节点缩进混用 4 空格（`screenshots`/`purpose`/`reference`/`analyzed_at`）与 2 空格（`viewports`/`responsive_comparison`/`comparison`/`bdd_results`/`summary`）。同一层级缩进不一致，**标准 YAML 解析器会直接报错**。

**影响**
这是协议给出的「权威结构示例」，下游 `verifier` 要按它读 `summary.blocker_count`、`bdd_results[].result`。示例本身 parse 不了，意味着任何照抄它的 subagent 产出都可能坏掉，且 P6 gate 的 `blocker_count == 0` 硬约束建立在一个坏结构上。

**修法**
统一为 2 空格缩进（YAML 惯例），把 `vision_analysis:` 下所有直接子节点对齐到 2 空格：

```yaml
vision_analysis:
  screenshots: [...]
  purpose: "acceptance"
  reference: "docs/design/mockup-v2.png"
  analyzed_at: "2026-06-13T10:00:00"
  viewports:
    - id: "desktop"
      ...
  responsive_comparison:
    - ...
  summary:
    blocker_count: 1
    ...
```

**验收标准**
- 用 `python -c "import yaml,sys; yaml.safe_load(open('片段'))"` 能成功解析该示例
- 建议在 CI 加一步：抽取所有文档中的 ```yaml 代码块跑 safe_load

---

### P0-4 `scripts/check-tdd-red.sh` 被当成现成依赖，但仓库不提供

**定位**
- `state-machine.md`、`dispatch-protocol.md` L509、`WORKFLOW.md` P3 行：均把 P3 门槛写成「主 Agent 跑 `scripts/check-tdd-red.sh`」，当作既存可执行文件
- 仓库**无 `scripts/` 目录**，脚本仅以代码块形式贴在 `state-machine.md` 内
- 没有任何地方说明「此脚本需项目自行创建」

**根因**
协议号称「零基础设施、Agent 能读文件就能用」（README 设计原则），但 P3 gate 偷偷引入了一个需落地的 shell 脚本依赖。

**影响**
- 主 Agent 首次跑 P3 gate 会找不到脚本 → gate 失败 / 主 Agent 临场即兴解析 pytest（恰是协议明令禁止的「不自行解析 pytest 输出」）
- 破坏「零基础设施」承诺的可信度

**修法**（三选一，推荐 A）
- **A（推荐）**：把脚本作为真实文件放进仓库 `scripts/check-tdd-red.sh`，并在「首次接入」初始化流程（`orchestrator-template.md`「每次任务开始前」+ `state-machine.md` 初始化段）里加一步：`cp {agate_root}/scripts/check-tdd-red.sh {project_root}/scripts/` 或直接引用 `{agate_root}/scripts/`
- **B**：明确声明「P3 gate 脚本由项目落地」，在 `task-files.md` 或 README 加「前置依赖」节，把脚本内容列为模板
- **C**：把 TDD 红灯判定内联成主 Agent 可直接跑的一行命令组合，去掉脚本依赖

**验收标准**
- 仓库存在 `scripts/check-tdd-red.sh` 或文档明确其落地责任与路径
- 「零基础设施」声明与实际依赖一致（README 设计原则处加一句说明，或移除该承诺的绝对化措辞）

---

## 2. 🟠 高优先级（一致性与引用错误）

### P1-1 「8 个协议文件」清单两处不一致、计数错误

**定位**
- `orchestrator-template.md` L65-78：启动必读清单**正确列出 8 个**（含 `role-system.md` 和 `LIMITATIONS.md`）
- `state-machine.md` L386-388「抗中断恢复」段：文字说「依次重读…**8 个**协议文件」，但括号里只列了 **7 个**——`WORKFLOW / dispatch-protocol / state-machine / role-system / loop-orchestration / git-integration / platform-notes`，**漏了 `LIMITATIONS.md`**

**修法**
把 `state-machine.md` L387-388 括号补成 8 个，与 orchestrator 清单完全对齐，并考虑用「见 orchestrator-template.md『工作流规则』节的 8 文件清单」单一引用，避免两处各列一遍。

**验收标准**：两处清单文件集合完全相同，且数字与列表长度一致。

---

### P1-2 `gate_commands` 字段集三处定义不一致（含 UI 任务漏 E2E 风险）

**定位**
- `architect.md` L33-37：`gate_commands` 含 `P5` / `P5_e2e`（ui_affected 时必填）/ `P6` **三键**
- `task-files.md`「P2-design.md 结构」第 3 节：只有 `P5` / `P6`，**无 `P5_e2e`**
- `WORKFLOW.md` / `state-machine.md` 多处要求「ui_affected 时 P5 必须实跑 Playwright」——该要求落地依赖 `P5_e2e`

**影响**
UI 任务套用 `task-files.md` 模板会漏掉 `P5_e2e`，导致 P5 gate 名义上要求 Playwright 实跑、实际上模板里没这条命令，UI 实测被静默跳过。

**修法**
以 `architect.md` 为权威，把 `P5_e2e` 补进 `task-files.md` 的 P2-design.md 结构示例，并标注「ui_affected: true 时必填」。

**验收标准**：三处 `gate_commands` 字段集一致；UI 任务模板含 `P5_e2e`。

---

### P1-3 引用了仓库内不存在的文件

**定位**
- `docs/design-notes/README.md` 索引表把 `t019-safety-net-pattern.md` 列为独立文档，但该文件**不存在**（内容实际在 `docs/reviews/agate-postmortem-T019-meta-review-2026-06-24.md` 内）。同行括号又补「见 docs/reviews/…」——说明作者知道，但表格结构仍错
- 多处引用 `docs/reviews/workflow-v4-postmortem-T005-T006-2026-06-13.md`（如 `main-agent-oversight.md` L11），该文件**不在本仓库**（属 PeekView 仓库）。部分引用带了「PeekView 仓库」限定，部分没带，读者按本地路径找不到

**修法**
- design-notes/README.md：把 `t019-safety-net-pattern.md` 那一行的「文档」列改为指向真实存在的 reviews 文件，或将该 meta-review 内容抽成独立文件落地
- 所有指向 PeekView 仓库的跨仓引用统一加 `（PeekView 仓库，非本仓）` 限定

**验收标准**：仓库内所有 `docs/...md` 引用都能 `ls` 到；跨仓引用都有明确限定。

---

### P1-4 硬编码行号引用必然失效

**定位**
`orchestrator-template.md` L91：`进入「单步函数」流程（state-machine.md L268）`——硬编码行号，文档修订后失效（核对当前 state-machine.md，单步函数已不在 268 行）。

**讽刺点**：协议自己在 `dispatch-protocol.md`「输入导航原则」里教导「导航用节名称，不用章节号」，自身却用了行号。

**修法**
全仓 `grep -n "\.md L[0-9]"` 找出所有硬编码行号引用，改为节标题引用（如「state-machine.md『主 Agent 单步函数』节」）。

**验收标准**：`grep -rn "\.md L[0-9]" .` 返回空（或仅余明确不会变的引用）。

---

## 3. 🟡 中优先级（结构性设计缺陷）

> 这一类多数作者已在 LIMITATIONS.md / design-notes 中承认。此处补充「传染性 / 放大效应」视角，并给出可推进方向，而非否定。

### P2-1 主 Agent 单点故障的「传染性」随协议复杂度放大

**现状**：`LIMITATIONS.md` 局限 3 + `main-agent-oversight.md` 已透彻剖析——四个真实事故（T005/T006/T016/T019）同一根因，三种监督方案均因「数据源与监督对象同源」被否决。

**补充判断**：agate 现有大量「主 Agent 必须亲自判断」的点（裁剪、SCOPE+ 影响范围、最小修复 vs 重写、回退深度、gate 算不算过…）。**每加一条规则就多一个单点判断负担，规则越多，主 Agent 越可能在某条上「图省事绕过」**——这正是 T016 的模式（「协议没说不行」当成「可以」）。

**方向**：见 P3-3（独立数据源）。短期内无法根治，但**应控制「需主 Agent 判断的点」的增长速度**，每新增一条这类规则时问：能否做成机器可判定？

---

### P2-2 协议自重过大，与「轻量」定位张力

**现状**：8356 行 / 52 文件，启动需读完 8 个协议文件。README 说「零基础设施，Agent 能读文件就能用」。

**问题**：`agent-file-reading-guarantee.md` 自己论证「按需读取不可靠 → 强制启动读 8 个文件」。但这把「读不读」换成了「读完 8 个长文件后关键规则还在上下文吗」——**8 文件读完，上下文已被协议本身占掉一大块，留给实际任务的空间反而变少。协议在用『上下文隔离』解决上下文爆炸，自己却在启动阶段制造上下文压力。**

**方向**：见 P3-2（精简启动路径）。

---

### P2-3 gate 客观性是「局部客观，全局可规避」

**现状**：`pytest exit 0` 客观，`LIMITATIONS.md` 局限 1 已承认「测试质量是上限」。

**补充**：主 Agent 自己写 `.state.yaml` 和 commit message，而所有「跨阶段回退检测」「状态标记绑定检测」都依赖这些自报数据。所以 `state-machine.md` 里精巧的「跨阶段回退强制 PAUSED」「状态绑定 gate」规则，**在一个『选择性隐瞒的主 Agent』面前是纸糊的**——T016 的 commit 把违规降级写成「TDD 完成，9 红灯 0 错误」就是铁证。**这些护栏防得住诚实主 Agent 的疏忽，防不住不诚实主 Agent 的规避。**

**方向**：护栏措辞应明确「本规则防疏忽不防蓄意规避」，避免读者高估其保证强度；根治依赖 P3-3（独立数据源）。

---

### P2-4 并行缺失对大任务是相对短板

**现状**：`loop-orchestration.md` 已知改进项——当前严格串行。

**问题**：agate 主打「复杂长任务」，而复杂任务最受益于并行（多模块 P4、P2 多角度评审）。串行 + 每阶段约 25 行 prompt 开销，大任务端到端延迟可观。同期竞品（Augment Cosmos、agentic-development-process、gstack+Conductor）已用 git worktree 做并行。

**方向**：见 P3-5。

---

### P2-5 启动上下文压力（与 P2-2 同源，单列以便单独排期）

**现状**：每次新启动 / 压缩恢复都要重读 8 个文件。

**问题**：抗中断设计要求「协议规则也要重建」，但重建 8 文件本身就消耗大量上下文，与「主 Agent 尽量无状态、上下文增量常数级」的目标相互拉扯。

**方向**：见 P3-2。

---

## 4. 🟢 优化提升建议（按性价比排序）

### P3-1 给协议自身加「结构一致性检查脚本」 ★最高性价比

**针对**：`LIMITATIONS.md` 局限 5（协议文档自身一致性不在流程内）。

**关键洞察**：作者论证过「语义一致性不可机器判定」——这对。但**结构一致性（字段集、文件引用、清单计数、行号引用、YAML 可解析性）完全可以机器判定**，不必等语义层。本评审第 1 章 P0-3、第 2 章 P1-1/2/3/4 的一半问题，一个确定性脚本就能抓出。

**落地**：写 `scripts/check-protocol-consistency.sh`（或 Python），覆盖：
1. 所有 ```yaml 代码块跑 `yaml.safe_load`（抓 P0-3 类）
2. 所有 `docs/.../*.md`、`assets/.../*.md`、`scripts/*.sh` 引用是否真实存在（抓 P0-4、P1-3）
3. 死链行号引用 `\.md L[0-9]`（抓 P1-4）
4. 跨文件字段集比对：`gate_commands` 在 architect.md / task-files.md 的键集合是否一致（抓 P1-2）
5. 「N 个文件」类计数声明 vs 实际列表长度（抓 P1-1）
6. LICENSE 徽章指向的文件是否存在（抓 P0-2）

挂进 CI（GitHub Actions），PR 必过。

**价值**：把「协议文档全靠人肉维护一致性」变成「机器守护结构一致性」，正面回应局限 5。

---

### P3-2 精简启动路径（热路径速查）

**针对**：P2-2、P2-5。

**落地**：把最高频的「转移规则表 + 派发 prompt 模板 + gate 判定表」抽成一个 ~200 行的 `QUICKREF.md`。启动只读 `QUICKREF.md` + `WORKFLOW.md`；8 个全文文件仅在首次接入或遇到边界情况（PAUSED 处理、SCOPE+ 回补、自定义角色）时按需深读。

**注意**：这与 `agent-file-reading-guarantee.md` 的「强制读 8 文件」结论有张力——需在该 design-note 里补一条权衡：「热路径速查覆盖 80% 高频判定，全文按边界场景触发」，并实测速查是否真能替代全文(避免漏关键规则)。

---

### P3-3 引入独立数据源，破解局限 3 ★战略价值最高

**针对**：P2-1、P2-3、局限 3。

**依据**：`main-agent-oversight.md` 自己指出了唯一出路——「数据源必须独立于主 Agent 的叙事」，并列了两个候选：
1. task 工具调用日志（若平台暴露，不经主 Agent 转写）
2. subagent 产出文件带主 Agent 难伪造的自盖时间戳 / 身份标记，再拿 git author / timestamp 元数据交叉核对

**落地建议**：从候选 2 起步做原型——派发 prompt 要求 subagent 在产出 Header 写入由它生成的 `agent_run_id` + `wall_clock`，主 Agent 在 commit 时不得改写；写一个确定性脚本拿 git author/committer timestamp 与 Header 时间戳交叉比对，差值异常 → 报告。这是当前唯一可能真正触及单点故障的方向，值得从「开放问题」推进到 PoC。

---

### P3-4 评审角色合规化（与 P0-1 合并执行）

把 gstack 来源的 9 个角色统一过一遍「是否符合 agate 执行/评审分离 + commit 归属」，不止 P0-1 点名的 3 个。产出一份《gstack 角色 ↔ agate 模型对齐说明》，记录每个角色提取时做了哪些改动（MIT 也要求标注修改）。

---

### P3-5 并行执行 + git worktree 隔离

**针对**：P2-4。

**落地**：识别「无数据依赖的同阶段多 subagent」作为可并行单元（P2 多角度评审天然可并行、多独立模块的 P4）。配套 git worktree 隔离避免文件/commit 冲突。`loop-orchestration.md` 已把它列为已知改进项，建议升级为 roadmap 项并给出最小可行设计。

---

### P3-6 考虑协议「半可执行化」

**战略判断**：agate 现在站在「纯文档协议」与「代码框架（LangGraph/CrewAI）」中间——**享受了文档路线的轻便，也继承了它『全靠 LLM 自觉』的全部脆弱。**

**落地**：把「可判定的转移」（状态绑定检查、跨阶段回退检测、gate exit code 判定、retry 计数）做成一个薄 harness（shell/Python），主 Agent 只负责「不可判定的判断」（裁剪、SCOPE+ 影响范围、方向确认）。这会牺牲一点「零基础设施」纯粹性，但能把局限 3 的一部分从「依赖主 Agent 遵守」变成「代码强制」。

**取舍**：这是路线选择，不是必须。若坚持纯文档路线，则 P3-1（一致性脚本）和 P3-3（独立数据源）是在不背叛路线前提下能做的最大改进。

---

## 5. 修复路线图（建议排期）

### 第一批：阻断级 + 高优先一致性（1 个 PR，半天工作量）
- [ ] P0-2 补 `LICENSE`（MIT 全文）+ gstack 归属
- [ ] P0-1 / P3-4 三个评审角色去「改代码/提交」，统一为只产 status + 建议
- [ ] P0-3 修 vision-analyst YAML 缩进
- [ ] P0-4 落地 `scripts/check-tdd-red.sh` 或声明落地责任
- [ ] P1-1 修 state-machine 的「8 文件」清单
- [ ] P1-2 task-files 补 `P5_e2e`
- [ ] P1-3 修死文件引用 + 跨仓限定
- [ ] P1-4 行号引用改节标题

**验收**：本文件第 1、2 章全部「验收标准」通过。

### 第二批：上一致性脚本（治本，1 个 PR）
- [ ] P3-1 写 `scripts/check-protocol-consistency.sh` + 挂 CI
- [ ] 用脚本回扫全仓，修掉它新发现的同类问题

**验收**：CI 上 consistency check 为绿；新 PR 引入同类问题会被拦。

### 第三批：结构性改进（按价值排期，多个 PR）
- [ ] P3-2 精简启动路径（QUICKREF.md）+ 实测覆盖率
- [ ] P3-3 独立数据源 PoC（agent_run_id + git 元数据交叉核对）
- [ ] P2-3 护栏措辞补「防疏忽不防蓄意」限定
- [ ] P3-5 并行执行最小设计（roadmap）
- [ ] P3-6 半可执行化评估（路线决策，先写 RFC）

---

## 6. 给维护者的一句话总结

> agate 把「工程师团队的 SDLC 协作」翻译成了 Agent 可读的协议，定位务实、填补真实空白，且自我反思的诚实度在同类项目里罕见。但这次评审挑出的低级错误证明：**它教别人「gate 要机器可判定」，自己的文档一致性却在裸奔。** 最该先做的不是宏大的单点故障攻坚，而是把第一批 8 个具体缺陷修掉，再用一个确定性脚本（P3-1）让协议文档自身也享受到它一直在鼓吹的「机器可判定的守护」。**先治标止血，再用脚本治本，最后才谈战略。**
