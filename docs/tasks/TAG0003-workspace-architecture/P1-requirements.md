---
phase: P1
task_id: TAG0003-workspace-architecture
type: problems
parent: P0-brief.md
trace_id: TAG0003-P1-20260812
status: draft
created: 2026-08-12
agent: analyst
# ── v2.0 机器字段 ──
risk_level: high             # 破坏性变更（docs/tasks 强制迁移）+ orchestrator 路径改动影响所有接入项目 + 75+ 处协议引用 + 测试换血
phases: [P1, P2, P3, P4, P5, P6, P7, P8]
packages: [agate]            # 协议本体单一包（改的是 worktree 的 agate/）
domains: [backend, cli]      # backend=gate 脚本/迁移工具/配置解析；cli=orchestrator 读取层。无 frontend、无 security
---

# TAG0003 — agate 工作区架构：P1 需求基线

> 输入：P0-brief.md（任务简报/风险/约束）+ P1-dispatch-context-analyst.md（派发指引）+ AGENTS.md（项目约定）+ docs/reviews/review-design-20260812-1428.md（主动架构演进方案，roadmap 思路来源）+ docs/reviews/agate-project-lifecycle-design-discussion-20260811.md（项目生命周期讨论稿）。
> 修订输入（2026-08-12）：P1-review.md（status: needs-revision，阻塞项 A + 建议 B + 观察项）+ P1-dispatch-context-analyst-revision.md（修订派发指引）。
> 角色：analyst（需求质疑，见 `~/.agate/assets/execution-roles/analyst.md`）。
> 范围说明：本任务改造对象是 **worktree 的 `agate/`（协议本体）**，不是 `~/.agate`（稳定版开发工具，禁止改动）。本基线定义"做什么 + 做完什么样算对"，不写实现方案（P2 的活）。

## 1. 需求复述

**一句话需求**（来自 P0-brief task 字段）：为 agate 设计**工作区架构**——`agate-workspace/` 目录规范（含 roadmap 项目级任务管理循环）+ `.agate.env` 工作区位置配置 + 从 `docs/tasks/` **强制迁移**的迁移工具与指引。

**P0-brief 已确认的关键决策**（作为需求输入，不得推翻）：

1. **破坏性变更方向已定（A 策略）**：现有项目的 `docs/tasks/` 等**强制迁移**到 `agate-workspace/`。需求必须覆盖迁移工具 + 迁移指引。
2. **工作区目录规范**：`roadmap/` + `tasks/` + `agents/`（project/memory/tech-debt）+ `archived/` + `reviews/` + `decisions/` + `plans/` + `logs/`。
3. **roadmap 项目级任务管理循环**：新需求/讨论 → roadmap → 拆任务 → active-tasks「待开始」→ 立项 → 实施 → 回写 roadmap。这是**新增机制**（agate 现无项目级规划层），本基线只定义循环与产出，不设计实现。
4. **`.agate.env` 配置工作区位置**：默认项目内 `agate-workspace/`，可配置指向项目外。

**改动面（主 Agent 已核实，本基线确认覆盖完整范围）**：
- 6 脚本 + 16 文档 + 75 处 `docs/tasks` 引用（主 Agent 口径）。
- orchestrator-template 的 project.md 路径（`{project_root}/docs/agents/project.md`）需改为工作区内路径——**影响所有接入项目**（orchestrator.md 经符号链接接入，路径改动传播到下游）。

**独立复核补充**（analyst 查证，供 P2 预算范围时参考）：`grep -rn "docs/tasks" agate/` 实测 **43 个文件 / 516 处字符串出现**，其中非测试文档 131 处（29 个 .md 文件）、`scripts/` 8 处（6 脚本）、**bats 测试 377 处**。主 Agent 的"75 处"口径未含测试引用——测试 fixture 是最大改动面，P2/P4 必须按此预算，不得按 75 处收窄。

## 2. 隐含需求识别

> 用户没说但技术上必须做的依赖。逐条给"为什么必须"。

1. **数据——存量任务目录与历史状态必须完整迁移**
   为什么必须：强制迁移（A 策略）下，现有项目的 `docs/tasks/`（含 active-tasks.md 看板 + 各任务目录 + `.state.yaml` + P0-P8 产出）整体迁入工作区 `tasks/`。任何文件丢失都破坏任务可追溯性。迁移工具需覆盖"看板 + 任务目录 + 状态文件 + 阶段产出"四类对象。
2. **数据——`.state.yaml` 常被 gitignore，迁移时不可被漏掉**
   为什么必须：`.state.yaml` 是单任务权威状态，既有约定"git add 需 `-f` 强制暂存"（install-hook.sh 已提示）。迁移工具若按普通文件处理，可能因 .gitignore 排除而静默遗漏——迁移必须显式处理这类文件（与 git 跟踪状态解耦）。
3. **多端——协议本体与下游接入项目双面改动**
   为什么必须：orchestrator-template.md 的 project.md 路径改动影响**所有接入项目**（orchestrator.md 是符号链接指向协议本体，路径规则一变全部跟着变）。下游项目需重新初始化/迁移才能继续使用；需求必须覆盖"新项目从零初始化"与"旧项目升级迁移"两条路径。
4. **多端——本地 hook 与 CI 的工作区解析必须一致**
   为什么必须：`pre-commit-gate.sh` 与 `ci-gate-backstop.py` 均已支持 `AGATE_TASKS_DIR` 环境变量（默认 `docs/tasks`）作为配置缝隙。`.agate.env` 引入后，本地 hook 与 CI backstop 必须解析到**同一工作区路径**，否则本地过 CI 红（或反向）——一致性是硬要求。
5. **前端/展示——任务看板与 roadmap 的格式/入口变化**
   为什么必须：任务看板（active-tasks.md）路径、orchestrator 的"接入"步骤（`mkdir -p docs/tasks`）、阶段产出表里的 `docs/tasks/` 结构描述全部要改；roadmap 是新增产物，需定义其存在形式与入口（工作区 `roadmap/`）。这些是"用户能看到/维护者要维护"的界面层改动。
6. **边界——空工作区（无既有 docs/tasks）也能从零初始化**
   为什么必须：新项目接入 agate 时可能完全没有 `docs/tasks/`。初始化必须能在空项目上直接建出规范工作区，不因"无旧目录可迁移"而失败。迁移工具对"无迁移源"与"有迁移源"都必须正确（幂等 + 空源 OK）。验收见 BDD-19（空源迁移）+ BDD-9（幂等）。
7. **边界——无 `.agate.env` / 路径含空格 / 项目外路径**
   为什么必须：`.agate.env` 是可选文件，缺失时走默认（项目内 `agate-workspace/`）；路径含空格、指向项目外、相对/绝对路径混用等边界都必须被正确解析，否则换项目即坏（T005 漏 MCP 端教训同构：配置文件缺失时默认行为必须定义清楚）。
8. **兼容——旧 docs/tasks 项目的迁移路径与升级指引**
   为什么必须：强制迁移对存量项目是破坏性变更。必须提供**迁移工具 + 明确指引**（UPGRADING.md/SETUP.md 同步），让存量项目可自迁移；协议自身也应能检测"仍在用旧布局"的项目并引导迁移（不静默继续、不静默失败）。
9. **兼容——协议文档、测试、检查器白名单全量同步**
   为什么必须：43 文件 / 516 处引用（含 377 处测试）整体切换。check-protocol-consistency.py 的目录排除白名单（含 `"docs/tasks/"`、`"docs/agents/"` 示例）需重新校准，否则一致性检查红；bats fixture 全部重写且用例数不得漂移（count-tests.sh 基线校验）。验收见 BDD-20（一致性检查白名单 + 用例数基线全绿）。
10. **数据——归档历史（docs/archived/）与工作区 archived/ 的关系**
    为什么必须：工作区规范含 `archived/`。现有 `docs/archived/tasks/` 的存量归档（如 T001-v2.0 完整归档，主 checkout 实测存在）需有明确去向（迁入工作区 archived/），避免归档历史割裂在两处。验收见 BDD-18（归档迁移目标 + 幂等）。
11. **内容边界——编排状态 vs 项目文档必须可二值判定**
    为什么必须：P0-brief 明确"agate 编排状态（tasks/agents/archived/reviews/decisions/plans/logs/roadmap）进工作区；项目文档（README/产品文档）留项目 docs/"。必须有**可二值判定的判据**防混（否则每个文件都要人拍板，边界必烂）。判据方向：**文件是否由 agate 编排流程生成/消费**（任务产出、评审、决策、计划、日志、状态、看板、roadmap、agent 知识 → 工作区）；**是否描述产品/项目本身而非任务编排**（README、产品文档 → 项目 docs/）。
12. **roadmap 循环的可追溯性**
    为什么必须：roadmap 是新增的项目级规划层，要求"需求→roadmap→任务→看板→实施→回写"闭环。无闭环则 roadmap 沦为一次性清单（讨论稿 §5.1 方案 A 的教训）。需求必须定义**条目状态**与**回写时机**（任务完成 → 对应条目状态更新），但不设计实现。

## 3. BDD 验收条件

> BDD 反模式自检（analyst.md）：Then 不绑定实现细节（脚本名/具体实现路径）、无主观形容词、可二值判定（PASS/FAIL）、每条单一 Given-When-Then、编号连续。
> 说明：BDD 中的 `agate-workspace/`、`docs/tasks/`、`.agate.env`、`project.md`、`active-tasks` 是**已确认的需求对象**（P0-brief 决策 2/4），引用它们是描述规格而非实现细节；BDD 不写具体脚本名。
> P6 逐条验收，PASS/FAIL 总数必须 ≥ 本基线 BDD 总数（20 条）。
> 修订记录（2026-08-12，analyst 修订轮）：按 requirements-review 意见新增 BDD-18（阻塞项 A——归档历史迁移）、BDD-19（建议 B #1——空源迁移）、BDD-20（建议 B #2——一致性检查器白名单/用例数基线）；并为 BDD-6/17 补观察项注释。既有 BDD 语义未改动。

### 工作区初始化与目录规范

#### BDD-1: 新项目初始化创建完整规范工作区
- Given 一个首次接入 agate 的新项目，项目内无既有工作区目录
- When 完成初始化（安装/启动编排）
- Then 项目内出现工作区目录，且包含 roadmap/、tasks/、agents/、archived/、reviews/、decisions/、plans/、logs/ 全部子目录

#### BDD-2: 默认工作区位置为项目内 agate-workspace/
- Given 项目未配置 `.agate.env` 中的工作区位置
- When 编排流程确定工作区路径
- Then 工作区路径为项目根下的 agate-workspace/（默认值生效）

#### BDD-3: `.agate.env` 可将工作区指向项目外路径
- Given 项目 `.agate.env` 声明工作区为项目外绝对路径
- When 编排流程读取配置
- Then 工作区使用该外部路径，且项目根下不新建默认 agate-workspace/

#### BDD-4: 无 `.agate.env` 时不报错、走默认位置
- Given 项目不存在 `.agate.env` 文件
- When 编排流程启动
- Then 正常运行且工作区使用默认位置，不产生配置错误

#### BDD-5: 工作区路径含空格仍正常工作
- Given `.agate.env` 配置的工作区路径含空格（如 "My Project/agate-workspace"）
- When 编排流程读写工作区文件
- Then 文件读写正常，无路径解析错误

### 从 docs/tasks 强制迁移

#### BDD-6: 迁移工具将既有 docs/tasks 内容迁入工作区
- Given 项目存在 docs/tasks/（含 active-tasks.md 与至少一个任务目录）
- When 运行迁移工具
- Then 看板与任务目录迁入工作区 tasks/ 下，原 docs/tasks/ 不再承担编排职责

> 注（2026-08-12 analyst 修订）：Then 中"原 docs/tasks/ 不再承担编排职责"是迁移目标的**推论性表述**，其直接可检落点是 BDD-11/12/13 的读取路径切换。P2 设计需将该推论落到"编排流程不再从 docs/tasks/ 读取"的可检状态，否则 P6 判定将依赖推论。

#### BDD-7: 迁移不丢失任务状态与阶段产出
- Given docs/tasks/ 下有含 `.state.yaml` 与 P0-P8 产出文件的任务目录
- When 运行迁移工具
- Then 所有 `.state.yaml` 与阶段产出文件完整随任务目录迁移，无文件丢失

#### BDD-8: 迁移保留 git 历史（文件移动而非删除重建）
- Given 迁移前的任务文件已纳入 git 跟踪
- When 运行迁移工具
- Then 迁移以文件移动语义完成，git 历史可在新路径追溯原内容（非删除+重建）

#### BDD-9: 迁移幂等——重复运行不产生重复或破坏
- Given 项目已完成迁移
- When 再次运行迁移工具
- Then 无新增迁移动作，不产生重复目录或数据丢失

#### BDD-10: 未迁移的旧布局项目在编排时获得明确迁移指引
- Given 项目仍使用 docs/tasks/（尚未迁移）
- When 编排流程（orchestrator/gate）运行
- Then 检测到旧布局并给出迁移指引，不静默继续使用旧路径、也不静默失败

### orchestrator 工作区感知

#### BDD-11: orchestrator 从工作区内路径读取 project.md
- Given 项目已按工作区规范初始化/迁移
- When orchestrator 会话开始读取项目必读文件
- Then project.md 从工作区内路径读取，不再从项目 docs 目录读取

#### BDD-12: orchestrator 从工作区内路径读取任务看板
- Given 项目工作区已初始化
- When orchestrator 读取任务看板
- Then 看板从工作区内路径读取，不再从项目 docs 目录读取

#### BDD-13: 任务状态机与 gate 以工作区为任务根，行为不变
- Given 项目工作区已配置（含指向项目外）
- When pre-commit/CI 扫描任务 `.state.yaml` 并执行状态校验
- Then 扫描范围是工作区 tasks/ 下的任务，且状态转移/重试/gate 判定行为与迁移前一致

### roadmap 项目级任务管理循环

#### BDD-14: 新需求/讨论进入工作区 roadmap
- Given 项目出现新需求或讨论
- When 纳入项目规划
- Then 工作区 roadmap/ 下产生对应条目，条目含可追溯的状态标识

#### BDD-15: roadmap 条目拆分为任务进入待开始看板
- Given roadmap/ 中存在待实施条目
- When 将其拆分为实施任务
- Then 任务写入工作区 tasks/ 看板的「待开始」区，且与 roadmap 条目存在关联

#### BDD-16: 任务完成回写 roadmap（闭环）
- Given 一个由 roadmap 条目派生的任务已实施完成
- When 同步 roadmap 状态
- Then 对应 roadmap 条目的状态被更新为已完成/关闭，闭环可追溯

### 内容边界

#### BDD-17: 编排状态与项目文档按二值判据分流
- Given 一份待归类的文件（场景一：任务验收记录；场景二：项目 README）
- When 应用工作区内容边界判据
- Then 判据给出二值结论：任务产出/评审/决策/日志/roadmap/看板/agent 知识归入工作区，README 等产品文档保留在项目 docs/，且同一判据对两类文件的结论相反

> 注（设计意图，2026-08-12 analyst 修订）：BDD-17 单条内嵌场景一/场景二是**对偶测试**——同一判据对"编排状态"与"项目文档"两类文件必须给出相反结论，拆分为两条独立 BDD 会丢失对偶断言（无法直接证明判据自洽）。保留单条双场景是有意为之。

### 归档迁移、空源迁移与工具链（修订轮新增）

#### BDD-18: 存量归档迁入工作区 archived/ 且幂等
- Given 项目 docs/archived/ 下存在历史归档（如已归档任务目录，含完整阶段产出）
- When 运行迁移工具（覆盖归档迁移）
- Then 归档整体迁入工作区 archived/ 下、相对目录结构对应保留、无文件丢失，且重复运行不产生重复归档或重复迁移动作

#### BDD-19: 项目从未有过 docs/tasks/ 时迁移工具正常运行
- Given 项目从无 docs/tasks/ 目录（无迁移源）
- When 运行迁移工具
- Then 正常运行不报错、不产生错误动作，工作区 tasks/ 仍可正常初始化（空源被当作合法状态）

#### BDD-20: 迁移后一致性检查白名单与用例数基线全绿
- Given 项目已完成迁移，协议文档/脚本/测试均已切换至工作区路径
- When 运行协议一致性检查与测试用例计数
- Then 一致性检查报告无 ERROR（目录排除白名单已重校准为工作区路径），且测试用例总数与迁移前基线一致（不漂移）

## 4. 待确认清单

[NO_NEED_CONFIRM]

> 方向判断已在 P0-brief 确认（A 策略强制迁移、工作区目录规范、roadmap 循环、.agate.env 位置配置），无真无方向项。以下为倾向项（审计痕迹，主 Agent 可自行采纳，不阻塞推进）：

- [SUGGEST: 迁移工具以 `git mv` 语义实现（目录级移动），理由：BDD-8 要求 git 历史可追溯，cp+rm 会破坏历史；目录级 git mv 一次性迁移整个 docs/tasks/，天然覆盖 .state.yaml 等被 gitignore 文件（git mv 显式指定文件即可，与 .gitignore 无关）]
- [SUGGEST: `.agate.env` 的工作区路径解析优先级为"显式配置 > 环境变量 AGATE_TASKS_DIR > 默认 agate-workspace/"，理由：既有 AGATE_TASKS_DIR 缝隙（pre-commit-gate.sh / ci-gate-backstop.py 已支持）需与 .agate.env 统一，显式文件配置优先于环境变量，默认兜底，保证本地与 CI 一致]
- [SUGGEST: 内容边界判据写入协议文档（WORKFLOW.md 或 SETUP.md）作为正式规则，理由：BDD-17 判据若无文档锚点，跨项目执行会漂移；文档化后 P7 一致性检查可锚定]
- [SUGGEST: 本任务不裁阶段，全流程 P1-P8，理由：破坏性变更 + 协议自身改造（dogfooding）+ 43 文件/516 处引用改动面，self-gate 全流程是协议对自身质量的承诺]

## 5. 裁剪说明

```yaml
risk_level: high            # 破坏性变更（docs/tasks 强制迁移）+ orchestrator 路径影响所有接入项目 + 43 文件/516 处引用（含 377 处测试）+ 新增 roadmap 机制 + 迁移工具新交付物
phases: [P1, P2, P3, P4, P5, P6, P7, P8]
跳过风险: 本次不裁剪任何阶段。迁移工具是新交付物（P3 测试先行、P4 实现、P5 验证）、工作区目录规范与 roadmap 循环需 P2 方案设计、75+ 处引用跨脚本/文档/测试需 P7 双向一致性核对、协议本体发布需 P8。裁剪任一阶段都直接放大破坏性变更回归风险。
```

- **不裁剪理由**：
  - P2 不可裁剪——工作区目录规范、`.agate.env` 配置语义、roadmap 循环、迁移工具设计、边界判据细化都是核心设计，必须 architect 产出。
  - P3 不可裁剪——风险 high；迁移工具与工作区解析逻辑需要测试先行（fixture 重写 + 新用例）。
  - P4 不可裁剪——实现是交付底线（6 脚本 + 文档 + 测试 + 新迁移工具 + 新 roadmap 产物）。
  - P5 不可裁剪——验证是交付底线（全量 bats + shellcheck + consistency，且用例数不漂移）。
  - P6 不可裁剪——验收是质量最后防线（逐条对照本基线 20 条 BDD）。
  - P7 不可裁剪——跨文件交叉核对（协议文档 vs 脚本 vs 测试的路径引用一致性），本任务同时跑 self-gate。
  - P8 不可裁剪——发布新版协议（badge + CHANGELOG + tag + 迁移指引随版本文档发布）。
- 本声明与执行一致，无 `override` 需求。

## 6. 能力需求声明

```yaml
capability_requirements:
  - need: bash 脚本能力（git mv / 文件迁移 / 配置解析）
    why: 迁移工具与 .agate.env 解析是新交付物，协议既有脚本全为 bash 实现
    available:
      - "worktree 环境 bash（既有 6 个待改脚本同语言）"
    status: available

  - need: python3 + pyyaml（配置解析/一致性检查）
    why: 工作区路径解析与 check-protocol-consistency.py 白名单校准依赖
    available:
      - "Python 3.12 + pyyaml（agate-state-yaml-check.py 在用，已核实）"
    status: available

  - need: bats 测试框架
    why: P3/P5/P6 验证 fixture 重写（377 处测试引用换血）与新增迁移工具用例
    available:
      - "bats 1.10.0（worktree 环境已核实）"
    status: available

  - need: shellcheck
    why: P5 对改动的 6 个 .sh 脚本 + 新增迁移工具做静态检查
    available:
      - "shellcheck（worktree 环境已核实）"
    status: available
```

本任务无能力缺口（capability_requirements 全部 available）。本任务非 UI 任务，不需要浏览器/视觉能力。

## 参考

- 任务简报：P0-brief.md（A 策略、工作区目录规范、roadmap 循环、.agate.env 决策）
- 派发指引：P1-dispatch-context-analyst.md（目标/约束/上游关联/输入文件）、P1-dispatch-context-analyst-revision.md（修订轮派发指引）
- 评审意见：P1-review.md（needs-revision：阻塞项 A 归档迁移无 BDD → BDD-18；建议 B 空源/一致性 → BDD-19/20）
- 背景设计：docs/reviews/review-design-20260812-1428.md（方案乙/丙/己，主动架构演进）、docs/reviews/agate-project-lifecycle-design-discussion-20260811.md（方案 B 债务登记、roadmap 循环背景）
- 现状代码：`agate/scripts/` 下 6 个引用 docs/tasks 的脚本（pre-commit-gate.sh / check-state-transition.sh / check-pruning.sh / check-protocol-consistency.py / ci-gate-backstop.py / install-hook.sh）、`agate/orchestrator-template.md`（project.md 路径）、`agate/assets/templates/`（active-tasks / project / task-files 模板）
- 测试基线：`bash agate/tests/scripts/count-tests.sh`（用例数不得漂移）
