---
phase: P1
task_id: TAG0015
type: problems
parent: P0-brief.md
trace_id: TAG0015-P1-20260819
status: draft
created: 2026-08-19
agent: analyst
# ── v2.0 机器字段 ──
risk_level: medium
phases: [P1, P2, P3, P4, P5, P6, P7, P8]
packages: [assets/templates, scripts, state-machine, phase-cards, docs-reviews-migration, core-protocol-docs]
domains: [process]
implicit_coupling: true
# 跳过风险: 本任务不裁剪任何阶段。理由见「裁剪说明」节——BDD-9/10/11/17/18/19/20 涉及脚本行为
#   变化，按 AGENTS.md「改脚本的工作流」必须先红后绿（P3 不可裁）；phases 是任务级字段，不支持
#   按 BDD 拆分裁剪，若为迁就纯文档 BDD 整体裁 P3，会连带裁掉脚本改动的 TDD 红灯，故声明全阶段。
capability_requirements:
  - need: repo-wide-text-search
    why: 同类扫描与影响面梳理需要 grep/rg 扫描全仓协议文件、脚本、历史复盘存量文档
    available:
      - "Bash grep/rg（agate 环境标配工具，本次 P1 已实际使用）"
    status: available
  - need: python-script-authoring-with-tdd
    why: check-retrospective.py 路径文案/触发条件改动 + 新增 agate-feedback.py 均需配单元测试（先红后绿）
    available:
      - "implementer 执行角色（agate 内置执行角色，负责 P4 实现）"
      - "test-designer 执行角色（agate 内置执行角色，负责 P3 TDD 红灯）"
    status: available
---

# P1-requirements.md — TAG0015 agate 复盘与反馈机制统一

## 0. P0-brief 时效性质疑

`[P0_STALE: HANDOFF-TAG0015.md/P0-brief.md 隐含的 pytest 基线数字（893 全绿）是 2026-08-16 立项时的旧数字；worktree 此后已 rebase 上 TAG0012 的合并，主 Agent 派发 P1 前重新验证得 909 passed + 2 skipped（新增 16 个测试），check-protocol-consistency.py --strict 得 0 ERROR / 279 WARNING，与 TAG0012 合并后的基线一致——轻微漂移，已按最新基线数字记录，不需要回 P0]`

严重漂移判据（task 目标方案不再成立 / executor_env 平台前提不再成立 / known_risks 已解决前提实际未解决或已被他任务解决）逐条排查：均不命中——AG0020/AG0021 的目标方案、Linux worktree 执行环境前提、known_risks 列出的"已解决前提"（如 postmortem-template.md 现状、check-retrospective.py 路径矛盾、orchestrator-log 无强制力）均在本次 P1 自行核实中原样成立（见「同类扫描」节的逐条 grep 证据）。除上述 pytest 数字刷新外未发现其他局部漂移（路径/依赖版本/env_constraints 具体值均未变）。结论：**轻微漂移，已记录，不阻塞，继续 P1**。

## 1. 需求复述

TAG0015 把"复盘"和"跨项目反馈"从临场发挥变成 agate 协议机制，分两阶段合并为一份需求基线：

- **AG0020（核心）**：复盘模板从项目资料区（`docs/reviews/postmortem-template.md`）迁入协议本体（`agate/assets/templates/`），补齐正文结构、内容价值标准、归因分层（机制缺口 vs 执行错误）、产出流向约定、项目资产沉淀追问；复盘产出路径从 `docs/reviews/` 统一到 `tasks/{Txxx}/retrospective.md`；`check-retrospective.py` 的路径提示与触发标的同步修正；`orchestrator-log.md` 扩展"决策 + 依据"语义，并设计 L2 会话 checkpoint 作为新的事实源层。
- **AG0021（增量，建立在 AG0020 结构化产出上）**：复盘文档加机器可解析的 frontmatter 字段与「## agate 反馈」结构化节；新增 `agate-feedback.py` 做提取 + 匿名化 + 生成待提交内容；`AGATE_FEEDBACK` 开关默认 off（opt-in）；触发方式是"用户/agate 项目组推动"而非"项目自发"。

## 2. 隐含需求识别

1. **模板迁移后引用点必须同步**——不只是加正文结构，旧模板"游离于协议本体外"（无任何 `agate/` 核心协议文件引用它）本身是问题，迁移后必须在协议本体挂一个引用点，否则新模板同样会游离（见 BDD-8）。
2. **check-retrospective.py 的三处路径矛盾是三个独立坐标**（`docs/reviews/` 模板现址、`docs/releases/` 脚本提示、`tasks/{Txxx}/` 目标路径）——统一到目标路径不是改一处文案就完，配套单测目前对这行文案零断言，改了不会被测试拦截，必须同时补断言（见 BDD-9/BDD-11）。
3. **orchestrator-log 语义扩展不是只改 state-machine.md 一处**——`orchestrator-log` 关键词在核心协议文件命中 4 个文件 6 处（state-machine.md/loop-orchestration.md/agate/assets/templates/task-files.md/WORKFLOW.md），扩展"决策+依据"语义若只改 state-machine.md，其余 3 文件的旧措辞会与新语义产生文档漂移（见 BDD-14）。
4. **AGENTS.md:11 的"复盘在 docs/，使用者无需阅读"是过期声明**——复盘产出路径改为 `tasks/{Txxx}/` 后这句话与目标方案矛盾，不属于 P0-brief 列出的 8+4 条缺口清单，但属于同一批文件改动会牵连到的直接措辞冲突，必须在本任务处理（不是新范围，是既有目标方案的必然连带，见 BDD-15）。
5. **存量 4 份复盘文档需要一个明确决策**（迁移 / 标注 / 不动三选一），不能留白让下游各自猜（见 BDD-16）。
6. **AG0021 的脚本不能假设自动触发**——P0-brief 已用 TPV0093 实证纠偏，BDD 的 Given 必须显式写"手动触发"，否则 P6 验收会错误地去构造"自动触发"场景（见 BDD-17~20）。
7. **check-retrospective.py 保持"只提醒不阻断"的既有设计哲学**——统一触发标的（issue③）不应该变成新的阻断式 gate，否则改变了脚本的契约（exit 0 恒成立），这是隐含的兼容性约束（见 BDD-10）。

## 3. 同类扫描（强制节）

对 `retrospective|复盘|postmortem|orchestrator-log|postmortem-template|AGATE_FEEDBACK|agate-feedback` 等关键符号做了 grep 全仓扫描（不含 `agate-workspace/archived/` 历史归档、不含各任务目录存量产出，按 P0-brief 约束 4 锁定范围）。

| # | 扫描目标 | 命中数 | 命中清单 | 本次处理判定 |
|---|---------|--------|---------|-------------|
| 1 | `retrospective\|复盘\|postmortem` 在 `agate/*.md`、`phase-cards/*.md`、`assets/**/*.md`、`scripts/*.py`、`scripts/*.sh` | 14 文件 | adr.md、AGENTS.md（agate/ 内）、handoff-template.md、roadmap-template.md、tech-debt-template.md、git-integration.md、agate_common.py、agate-debt-check.py、agate-summary.py、check-protocol-consistency.py、check-retrospective.py、pre-commit-gate.py、UPGRADING.md、WORKFLOW.md | 逐条见下：`agate/AGENTS.md:11`（BDD-15，本次处理）；`check-retrospective.py`（BDD-9/10/11，本次处理）；其余 11 个文件经核实均为一次性提及（如 adr.md 的历史决策记录、handoff-template.md 的模板占位符、tech-debt-template.md 的 source 枚举值），不含"复盘路径/触发标的"这类会被本任务改动语义直接破坏的表述——**本次不处理**，原因是这些文件把"复盘"当作既有词汇引用而非定义复盘机制本身，语义不受路径迁移影响 |
| 2 | `check-retrospective.py` 硬编码路径提示（第 93 行） | 1 处 | `docs/releases/v{version}-retrospective.md` | 本次处理（BDD-9），三处路径矛盾（`docs/reviews/` 模板现址 / `docs/releases/` 此处提示 / 目标 `tasks/{Txxx}/`）坐实 P0-brief 问题④ |
| 3 | `agate/tests/unit/test_check_retrospective.py` 对路径文案的断言 | 0 处 | `grep -n "docs/releases\|docs/reviews\|tasks/{"` 零命中（脚本共 242 行、12 个 `test_` 用例，均围绕 retries_over/SCOPE+/override 三个既有触发点，未覆盖提示文案本身与新触发条件） | 本次处理（BDD-11），必须新增断言否则 P3 无法形成有效红灯 |
| 4 | `state-machine.md` 对 `retrospective\|复盘\|postmortem` | 0 处 | 无命中 | 确认现状：复盘机制目前完全不在状态机转移规则里出现，本任务通过 BDD-12/13 把 orchestrator-log 语义扩展写入该文件，不新增"复盘"关键词本身进状态机（复盘机制的落点是模板+脚本+task 产物清单，不是状态转移规则），**本次不在 state-machine.md 新增"复盘"关键词**，只扩展 orchestrator-log 一节 |
| 5 | `postmortem-template.md` 全仓引用点（不含 archived/） | 8 处 | `HANDOFF-TAG0015.md`、`agate-workspace/roadmap/roadmap.md`、`agate-workspace/tasks/TAG0015-retrospective-feedback/{P1-dispatch-context-analyst.md,P1-progress.md,P0-brief.md}`（本任务自身产出，随任务推进自然更新，非独立处理项）、`agate-workspace/tasks/TAG0013-script-consistency/{P1-requirements.md,P0-brief.md}`、`HANDOFF-TAG0013.md` | `agate-workspace/roadmap/roadmap.md`：**本次处理**——模板迁移后路径引用需同步更新指向新路径（并入 BDD-8）。`TAG0013-script-consistency/*` 与 `HANDOFF-TAG0013.md`：**本次不处理**——历史任务产物是完成时点的存证记录，不追溯改写（同 git 历史不改写的惯例），且这两处引用的是"当时存在的模板"这一事实陈述，不因模板搬家而失真 |
| 6 | `orchestrator-log` 在核心协议文件 | 4 文件 6 处 | `loop-orchestration.md:168,173`、`state-machine.md:361,475,477`、`WORKFLOW.md:91`、`agate/assets/templates/task-files.md:45` | `state-machine.md:475,477`：**本次处理**（BDD-12，扩展"决策+依据"语义）。`loop-orchestration.md:168,173` 与 `agate/assets/templates/task-files.md:45`：**本次处理**（BDD-14，同步措辞不矛盾）。`WORKFLOW.md:91`：**本次不处理**——是目录树注释里的一行"logs/ # 运行日志（orchestrator-log 等）"，纯路径级提及，不含语义描述，扩展语义不影响这行文本的正确性。`state-machine.md:361`（gate 失败后追加 orchestrator-log 一行）：**本次不处理**——这是既有"记录 gate 失败"用法，与本任务扩展的"决策+依据"是并存关系不是替换关系，不需要改 |
| 7 | `docs/reviews/` 目录现存文件 | 11 个 | 4 份存量复盘正文（tag0008/tag0010-11+同名 review/tag0013/tag0014）+ postmortem-template.md + 2 份 agate-alignment-review 系列 + opencode-session-extraction-guide.md | 4 份存量复盘：**本次处理**（BDD-16，决策为"保留 + 标注，不物理迁移"）。postmortem-template.md：**本次处理**（BDD-1~8，迁移+重写）。`agate-alignment-review-*.md`、`opencode-session-extraction-guide.md`：**本次不处理**——这些是评审/指南类文档，不是"复盘正文"，不在 P0-brief 锁定的存量迁移对象范围内 |
| 8 | `AGATE_FEEDBACK` / `agate-feedback` 全仓 | 0 处（脚本层面） | 仅 `agate-workspace/roadmap/roadmap.md` 已有设计段落 + `HANDOFF-TAG0015.md`（本任务文件）+ `docs/hardening-roadmap.md:200` P2.68（历史前身讨论） | roadmap.md 设计段落：作为本任务的设计参考输入，不是本次改动对象本身。`docs/hardening-roadmap.md:200` P2.68：**本次不处理，纳入「范围外观察」**（历史提案，方向已被 RM-AG0020/AG0021 承接，但 hardening-roadmap.md 是独立的路线图讨论文档，不属于本任务协议改动对象，标注 superseded 与否留给主 Agent/roadmap 维护者判断） |
| 9 | `AGENTS.md` 中"复盘"相关措辞 | 1 处 | `agate/AGENTS.md:11`："docs/ 目录存放……复盘。这些都是仓库维护者写的，使用者无需阅读" | **本次处理**（BDD-15），与本任务目标方案（复盘归 tasks/{Txxx}/）直接措辞冲突 |

**同类扫描结论**：8+4 条已核实缺口涉及的文件改动面共 **7 个核心协议文件 + 1 个模板迁移 + 1 个新脚本 + 4 份存量文档决策**，均已逐条给出处理判定；本次不处理的实例分两类——① 一次性词汇引用不受语义改动影响（如 adr.md/handoff-template.md）② 历史任务存证不追溯改写（TAG0013 相关文件），均已写明理由，不留白。

## 4. BDD 验收条件（按"改哪个文件"分组）

### 4.1 `docs/reviews/postmortem-template.md` → 迁移为 `agate/assets/templates/retrospective-template.md`

#### BDD-1: 模板补齐正文结构
- Given 新建的复盘文档基于新模板起草
- When 按模板骨架填写
- Then 复盘文档模板文件本身定义"事实基线/做得好的/发现的问题/改进措施"四个正文小节的标题与填写说明（可用 grep 校验这四个标题在模板文件中存在）

#### BDD-2: 模板声明内容价值标准
- Given 新模板文件
- When 检查模板是否定义"什么值得写"
- Then 模板文件包含一个明确小节，枚举三条内容价值标准（机制缺口 / 可复用模式 / 归因到可行动层面的问题），可通过 grep 该小节标题与三条枚举文本校验存在性

#### BDD-3: 归因分层字段
- Given 复盘"发现的问题"节的每条问题条目
- When 撰写该问题条目
- Then 每条问题标注"归因层面：机制缺口 / 执行错误"二选一字段，模板对该字段做强制说明 + 示例（二值语义，不允许留空或标注"两者都是"）

#### BDD-4: 产出流向强制约定
- Given 复盘"技术债登记"核对清单行标记为"是"（存在机制缺口）
- When 复盘定稿提交
- Then 该行"未触发后果/原因"列必须填写具体的 DEBT 编号或 roadmap RM 编号（不允许留空或写"待定"），模板对该字段的必填性做出显式强制说明；check-retrospective.py 侧不做内容语义解析（沿用「只提醒不阻断」既有边界，不新增阻断逻辑）

#### BDD-5: 项目资产沉淀强制追问
- Given 复盘"做得好的/可复用模式"节
- When 撰写该节内容
- Then 每条可复用项标注两类去向之一：①"回馈 agate"（关联 BDD-7 的「## agate 反馈」节）②"项目资产沉淀"（并注明具体沉淀位置，如 Makefile/scripts/ 或 agents.md/project.md）；模板强制包含追问句"本次产生的临时命令/脚本/经验，哪些该沉淀为项目固定资产？沉淀到哪？"作为该节填写引导语（可通过 grep 该追问句原文校验模板含此引导）

#### BDD-6: frontmatter 机器字段（AG0021 依赖）
- Given 新模板 retrospective-template.md
- When 一份基于该模板的复盘文档定稿
- Then 该文档 frontmatter 含 `mechanism_issues`（list）/`execution_issues`（list）/`feedback_ready`（bool）三个字段，字段存在性可用 YAML 解析校验；模板文件本身声明这三个字段的样例与填写说明

#### BDD-7: 「## agate 反馈」结构化节（AG0021 依赖）
- Given 新模板 retrospective-template.md
- When 复盘文档定稿且 `feedback_ready: true`
- Then 文档含标题为「## agate 反馈」的独立小节，模板对该节的内容边界做出显式声明（只列出归因到 agate 机制/执行层面的条目，不涉及项目敏感信息）

#### BDD-8: 模板挂入协议本体（解决"游离"问题）
- Given 旧模板 `postmortem-template.md` 当前不被任何 `agate/` 核心协议文件引用（游离于协议本体外，只是项目资料区文档）
- When 模板迁移进 `agate/assets/templates/retrospective-template.md`，`agate-workspace/roadmap/roadmap.md` 中对旧路径的引用同步更新为新路径
- Then 至少一个核心协议文件（如 `dispatch-protocol.md` 或对应的 `phase-cards/P8-release.md`）显式引用新模板路径，使模板成为协议本体的一部分而非游离资料（可通过 grep 新路径字符串在该协议文件中命中校验）

### 4.2 `agate/scripts/check-retrospective.py`

#### BDD-9: 路径提示文案同步
- Given `check-retrospective.py` 第 93 行现有提示文案 `docs/releases/v{version}-retrospective.md`
- When 触发任一异常提醒（retry 超限 / SCOPE+ / override）
- Then stderr 提示文案改为指向 `tasks/{Txxx}/retrospective.md`（`{Txxx}` 为实际 task_id 占位符，不是字面量），不再提及 `docs/releases/` 路径

#### BDD-10: 触发标的扩展（统一异常模式与机制缺口发现）
`[SUGGEST: 用 DEBT/roadmap 关联作为"机制缺口已发现"的检测代理，理由：脚本无法语义理解复盘内容本身的价值，只能检测客观副产物（本任务期间是否新增了指向该 task_id 的 DEBT 登记或 roadmap 条目）；"高价值建议"这一档不通过脚本自动检测，改由 BDD-2 的模板内容价值标准引导人主动判断是否值得写复盘，两层机制互补，都不改变脚本 exit 0 恒成立的既有契约]`
- Given 任务目录内无 retry 超限 / SCOPE+ / override 异常，但 `agate-workspace/` 下存在关联该 task_id 的新增 DEBT 登记条目或 roadmap 条目
- When `check-retrospective.py` 在版本 bump 前运行
- Then 同样输出"建议复盘"提醒（消息文案说明触发原因为"发现机制缺口"，与异常模式的提醒文案可区分），exit code 仍为 0

#### BDD-11: 配套单测断言覆盖（回归拦截）
- Given `agate/tests/unit/test_check_retrospective.py` 当前对路径文案与新触发条件均无专门断言（grep 零命中）
- When 本任务完成 BDD-9（路径文案）与 BDD-10（触发条件扩展）的改动
- Then 新增/更新至少 2 个单测用例：一个断言 stderr 输出含 `tasks/{Txxx}/retrospective.md` 且不含 `docs/releases`；一个断言 DEBT/roadmap 关联信号触发"建议复盘"提醒（BDD-10 场景），使这两处改动此后受测试保护

### 4.3 `agate/state-machine.md`（orchestrator-log 防无响应节 + L2 会话 checkpoint）

#### BDD-12: orchestrator-log 语义扩展为"决策 + 依据"
- Given 现有规则文本"不写思考过程、不写文件内容摘要、不写 subagent 返回原文——只写决策和下一步"（state-machine.md 第 481 行）
- When 本任务扩展该规则
- Then 规则文本更新为同时允许/要求记录"决策 + 简要依据"（依据 = 触发该决策的客观信号，如 gate 输出摘要/BDD 编号/文件路径引用，不等同于展开的思考过程），且保留"不写思考过程 / 不写文件内容摘要 / 不写 subagent 返回原文"三项既有排除不变（可通过对照修改前后文本校验排除项未被移除）

#### BDD-13: L2 会话 checkpoint 设计问题声明（P1 定问题，P2 定格式）
- Given P0-brief 已识别 L1（仓库落盘）/L2（会话 checkpoint，新增）/L3（平台导出）三层事实源，其中 L2 目前不存在
- When P2 architect 设计 L2 会话 checkpoint 方案
- Then P2-design.md 必须显式回答以下四个问题（不要求本 P1 阶段定具体格式，但缺一不算完成设计）：① L2 checkpoint 的落盘时机（任务完成时 / 每阶段结束时 / 其他触发点）② 落盘文件路径与命名（新开一类文件，还是扩展 `orchestrator-log.md` 语义覆盖）③ 与 BDD-12 扩展后的 orchestrator-log 语义是什么关系（互补 / 替代 / 包含）④ 防 session compact 的落盘策略（何时确保内容已写盘而非仍在会话上下文里）

### 4.4 orchestrator-log 跨文件同步（loop-orchestration.md / agate/assets/templates/task-files.md）

#### BDD-14: 跨文件描述点同步一致
- Given orchestrator-log 语义在 state-machine.md 完成 BDD-12 扩展后
- When 检查其余引用点（`loop-orchestration.md:168,173`、`agate/assets/templates/task-files.md:45`）
- Then `loop-orchestration.md` 与 `agate/assets/templates/task-files.md` 中对 orchestrator-log 的描述与扩展后的新语义不矛盾——若这两处逐字复述了"只写决策和下一步"这类已被 BDD-12 扩展的旧表述，需同步更新或删除，不要求逐字重复新语义（`WORKFLOW.md:91` 是目录树注释中的一行路径级提及，不含语义描述，本次不处理）

### 4.5 `agate/AGENTS.md`

#### BDD-15: 复盘位置措辞同步
- Given `agate/AGENTS.md:11` 现有文案"docs/ 目录存放……复盘。这些都是仓库维护者写的，使用者无需阅读"
- When 复盘产出路径迁移到 `tasks/{Txxx}/` 后（BDD-16 已决定存量文档保留原位不动）
- Then `AGENTS.md:11` 更新为区分"历史存量复盘仍在 docs/reviews/（迁移前旧布局）"与"新复盘归 tasks/{Txxx}/retrospective.md"，不再让"复盘在 docs/，使用者无需阅读"作为对新复盘同样成立的过期声明留存（避免被 P7/CI 一致性检查判定为文档漂移）

### 4.6 `docs/reviews/` 存量复盘迁移决策

#### BDD-16: 存量 4 份复盘文档处理方式
`[SUGGEST: 保留原位 + 顶部加标注，不做物理迁移。理由：物理迁移会让 4 份已合并任务（TAG0008/TAG0010-11/TAG0013/TAG0014）的复盘产出脱离其原始 PR/commit 语境，这些任务目录多数已完成生命周期，物理搬迁的收益（路径统一）小于成本（打断历史引用链 + 触发已完结任务目录的二次改动）；只加标注即可让新旧约定并存，新复盘自然长在正确位置，不影响历史可追溯性]`
- Given `docs/reviews/` 现存 4 份存量复盘正文（tag0008/tag0010-11 含同名 review/tag0013/tag0014）
- When 本任务新增"复盘归 `tasks/{Txxx}/`"的路径约定
- Then 存量文件保留在原路径不做物理迁移，每份文件顶部追加一行标注（如"> 历史复盘（迁移前旧布局），新复盘请见 `tasks/{Txxx}/retrospective.md`"），`roadmap.md` 等活文档对这 4 份文件的路径引用保持不变（文件位置未变，引用不需更新）

### 4.7 `agate/scripts/agate-feedback.py`（新增，AG0021）

#### BDD-17: 结构化提取能力（依赖 BDD-6/BDD-7）
- Given 一份复盘文档已包含 BDD-6 定义的 frontmatter 机器字段（`mechanism_issues`/`execution_issues`/`feedback_ready`）与 BDD-7 定义的「## agate 反馈」结构化节
- When 运行 `agate-feedback.py` 指向该复盘文件
- Then 脚本正确解析并输出结构化数据（能提取 `mechanism_issues` 列表内容，不报解析错误）

#### BDD-18: 匿名化
- Given 复盘文档「## agate 反馈」节内容包含项目名 / 绝对文件路径等项目特定信息
- When `agate-feedback.py` 提取
- Then 输出的结构化 JSON 不包含原始项目名 / 绝对路径等可识别项目身份的字段（脱敏规则至少覆盖：项目名替换为占位符、绝对路径截断为相对路径或移除）

#### BDD-19: AGATE_FEEDBACK 开关默认 off
- Given 未设置 `AGATE_FEEDBACK` 环境变量（或显式设为 `off`）
- When 运行 `agate-feedback.py`
- Then 脚本不产生任何提取输出（不生成 JSON、不打印内容），exit code 提示"功能未启用"而非静默失败

#### BDD-20: 触发方式与产出边界（不自动提交）
- Given 用户或 agate 项目组要求某外部项目为其 agate 使用经历登记「## agate 反馈」节后手动运行 `agate-feedback.py`（不存在任何自动触发该脚本的钩子 / CI / cron）
- When 脚本执行完成
- Then 产出物是一份待人工提交的内容（结构化 JSON + 面向 issue/PR 的文本片段），脚本本身不执行任何网络提交动作（不调用 `gh`/`git push` 等提交命令）

## 5. AG0020 → AG0021 依赖关系声明

- BDD-6（frontmatter 机器字段）是 BDD-17（`agate-feedback.py` 解析）的输入依赖——BDD-17 的 Given 直接引用 BDD-6 产出的字段，BDD-6 未完成前 BDD-17 无法验收
- BDD-7（「## agate 反馈」节）是 BDD-17/BDD-18 的解析对象——脚本从该节结构化提取内容
- BDD-5（项目资产沉淀分类）与 BDD-7（agate 反馈节）是同一"做得好的/可复用模式"小节下的两个互斥去向分支，共享同一模板位置，需在 P2 设计模板正文时统一排版
- BDD-9/BDD-10（脚本路径与触发标的）与 BDD-16（存量复盘迁移决策）共享同一路径约定 `tasks/{Txxx}/retrospective.md`，三者的路径字符串必须逐字一致，P7 一致性检查据此做交叉核对

## 6. 待确认清单

`[NO_NEED_CONFIRM]`

两项 `[SUGGEST:]` 已在 BDD-10、BDD-16 中给出推荐方案与理由，主Agent可直接采纳（不涉及破坏性变更/业务方向判断）：
1. BDD-10：check-retrospective.py 用 DEBT/roadmap 关联作为"机制缺口"检测代理
2. BDD-16：存量 4 份复盘保留原位 + 顶部标注，不物理迁移

## 7. 范围外观察

以下发现与本任务相关但不纳入本次 BDD（按 P0-brief 约束"不得扩大范围"处理）：

1. `docs/hardening-roadmap.md:200` P2.68 条目——2026-08-11 商业分析会话记录的"agate 自进化复盘闭环"历史提案，方向已被 RM-AG0020/RM-AG0021 承接演进，但 hardening-roadmap.md 是独立的路线图讨论文档，不属于本任务协议改动对象，是否标注 superseded 留给 roadmap 维护者另行处理，不在本任务改动清单内。
2. `agate-workspace/archived/` 历史归档文档中"复盘"关键词的大量存量提及——按 P0-brief 约束 4，归档文档是历史记录，不是本任务的迁移/改动对象，未扫描细节，只做范围声明。
3. `agate-workspace/tasks/TAG0013-script-consistency/{P1-requirements.md,P0-brief.md}` 与 `HANDOFF-TAG0013.md` 对 `postmortem-template.md` 旧路径的引用——历史任务产物，是完成时点的存证记录，不追溯改写。

## 8. 裁剪说明

- **risk_level: medium**——本任务改动 6 个核心协议文件（AGENTS.md/state-machine.md/loop-orchestration.md + 迁移后的模板挂钩点）+ 1 处物理归属 `assets/templates` 包的措辞同步点（`agate/assets/templates/task-files.md`，归属理由见第 9 节 packages 范围声明）+ 至少 2 个脚本（`check-retrospective.py` 修改 + `agate-feedback.py` 新增）+ 4 份存量文档的处理决策，改动面广、触发 SELF-GATE，但均为可回归验证的加性变更（无删除/破坏现有状态转移逻辑），不涉及生产系统或不可逆外部调用，故不评为 high；改动面又明显超出单文件/单函数的 low 量级，评为 **medium**。
- **phases: 全阶段不裁剪**——BDD-9/10/11（check-retrospective.py）与 BDD-17~20（agate-feedback.py）涉及脚本行为变化，按 AGENTS.md「改脚本的工作流」必须先写失败测试确认红、再改脚本确认绿，P3 不可裁；`phases` 是任务级字段不支持按 BDD 拆分裁剪，若为迁就纯文档类 BDD（BDD-1~8/12~16）整体裁剪 P3，会连带裁掉脚本改动的 TDD 红灯，因此声明全阶段 `[P1,P2,P3,P4,P5,P6,P7,P8]`，无一裁剪。
- **implicit_coupling: true**——orchestrator-log 语义描述分布在 4 个文件 6 处（BDD-12/14），复盘路径字符串分布在脚本提示文案/模板/存量标注 3 处（BDD-9/10/16），均需要 P7 一致性检查逐条核对是否同步，属于隐式耦合场景。

## 9. 范围声明（`packages`/`domains` 见文件头 frontmatter）

- `packages: [assets/templates, scripts, state-machine, phase-cards, docs-reviews-migration, core-protocol-docs]`——分别对应模板迁移（assets/templates，含 retrospective-template.md 迁移与挂钩点，以及 `agate/assets/templates/task-files.md` 的 BDD-14 措辞同步——该文件是"任务产出文件命名规范"参考表而非流程规则文件，物理路径本就在 `assets/templates/` 下，归入该包比归入 core-protocol-docs 更贴切）、check-retrospective.py + agate-feedback.py（scripts）、orchestrator-log 语义扩展（state-machine）、模板挂钩点（phase-cards）、docs/reviews 存量决策（docs-reviews-migration）、AGENTS.md/loop-orchestration.md 跨文件同步（core-protocol-docs，不再含 `agate/assets/templates/task-files.md`）
- `domains: [process]`——本任务是 agate 自身的协议/流程机制改动，不是业务 backend/frontend 功能
