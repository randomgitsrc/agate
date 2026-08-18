---
phase: P2
task_id: TAG0015
type: design
parent: P1-requirements.md
trace_id: TAG0015-P2-20260819
status: draft
created: 2026-08-19
agent: architect
# ── v2.0 机器字段 ──
candidate_count: 2
packages: [assets/templates, scripts, state-machine, phase-cards, docs-reviews-migration, core-protocol-docs]
domains: [process]
ui_affected: false
dispatch_plan: {mode: single}
---

[PROD_NOT_TOUCHED]

# P2 方案设计 — agate 复盘与反馈机制统一（TAG0015，RM-AG0020 + RM-AG0021）

> 本文件把 P1-requirements.md 的 20 条 BDD 转成可实现方案。P1 已按"改哪个文件"归并成 6 大类
> （4.1 模板迁移 BDD-1~8 / 4.2 check-retrospective.py BDD-9~11 / 4.3 state-machine.md BDD-12~13 /
> 4.4 跨文件同步 BDD-14 / 4.5 AGENTS.md BDD-15 / 4.6 docs/reviews 存量决策 BDD-16 /
> 4.7 agate-feedback.py 新增 BDD-17~20），本设计按这 6 类逐条给出改动落点，并对 dispatch-context
> 点名的两处"真分叉"决策（L2 checkpoint 落点 / agate-feedback.py 匿名化深度）做候选方案权衡。

## 1. 影响面梳理（改什么 / 不改什么 / 风险在哪，先于候选方案）

### 1.1 改什么（Modify，按 6 大类分组，逐条关联 BDD）

**类 4.1 — `docs/reviews/postmortem-template.md` 物理迁移为
`agate/assets/templates/retrospective-template.md`**（git mv，不留旧路径 stub——同类扫描已确认
唯一活引用点是 `agate-workspace/roadmap/roadmap.md`，随 BDD-8 一并同步；TAG0013 相关历史任务
产物按 P1 第 7 节判定不追溯改写，不受影响）：

- **BDD-1**：新文件正文加"事实基线 / 做得好的 + 可复用模式 / 发现的问题 / 改进措施"四个小节标题
  + 每节一行填写说明
- **BDD-2**：新增「内容价值标准」小节（放在文件靠前的"填写前必读"位置，不是产出文档要填的正文
  节——因为 BDD-2 的 Given/Then 检查的是模板文件本身是否定义标准，不是复盘产出文档），枚举
  三条：机制缺口 / 可复用模式 / 归因到可行动层面的问题
- **BDD-3**：「发现的问题」节的填写说明里，每条问题模板行强制带 `归因层面: 机制缺口 / 执行错误`
  字段 + 一句二值语义说明（不允许"两者都是"）+ 一个填写示例
- **BDD-4**：沿用旧模板已有的"技术债登记"核对清单行（`postmortem-template.md:70`），在其"未触发
  后果"列旁加显式强制说明："标记为'是'时，本列必须填写具体 DEBT 编号或 roadmap RM 编号，不允许
  留空或写'待定'"；check-retrospective.py 侧不新增语义解析（沿用只提醒不阻断）
- **BDD-5**：「做得好的 / 可复用模式」节加两类去向标注模板行（①回馈 agate ②项目资产沉淀+具体
  位置）+ 强制追问句原文"本次产生的临时命令/脚本/经验，哪些该沉淀为项目固定资产？沉淀到哪？"
- **BDD-6**：frontmatter 样例块加 `mechanism_issues: []` / `execution_issues: []` /
  `feedback_ready: false` 三字段 + 一行说明（类型 list/list/bool）
- **BDD-7**：新增「## agate 反馈」小节骨架 + 内容边界声明（"只列出归因到 agate 机制/执行层面的
  条目，不涉及项目敏感信息"），置于`feedback_ready: true` 时填写的引导语下
- **BDD-8**：挂钩点落在 `agate/phase-cards/P8-release.md`（不是 `dispatch-protocol.md`——
  P1 §9 packages 范围声明已把"模板挂钩点"显式归入 `phase-cards` 包，非 `core-protocol-docs`）。
  `P8-release.md:86`「READY 收尾检查」节新增一条核对项，显式引用
  `agate/assets/templates/retrospective-template.md` 路径字符串（供 P7 grep 校验命中）
- 关联但不计入以上编号：`agate-workspace/roadmap/roadmap.md` 中 `docs/reviews/postmortem-template.md`
  路径引用同步更新为新路径（并入 BDD-8 的 When 子句，见 1.1 末尾说明）

`roadmap.md` 具体改动点（grep 命中 4 处，行号见本文件"输入文件"章节核实结果）：
`roadmap.md:313` 与 `roadmap.md:316` 描述模板"现状"与"应留在 docs/reviews/ 合理"的历史结论，
`roadmap.md:322` 重复同一结论——三处均是 2026-08-16 立项讨论时的历史记录（早于本任务把决策改为
"迁移进协议本体"）。**处理方式**：不重写整段历史叙述（叙述性文字保留，避免过度编辑决策日志），
只对三处literal 路径字符串 `docs/reviews/postmortem-template.md` 追加一个行内脚注式更正
（如 `（→ 已于 TAG0015 迁移至 agate/assets/templates/retrospective-template.md）`），不删除原叙述——
兼顾 BDD-8 "同步引用"要求与"历史讨论记录不应被静默篡改结论"的档案完整性。

**类 4.2 — `agate/scripts/check-retrospective.py`**：

- **BDD-9**：第 93 行 `sys.stderr.write("  请在版本 bump 前写简版复盘（docs/releases/v{version}-retrospective.md）\n")`
  改为指向 `tasks/{Txxx}/retrospective.md`（`{Txxx}` 是字面占位符文本，不做实际任务号替换——
  沿用现有第 93 行本就是提示文案而非动态插值的写法，`{version}` 同理是字面占位符）
- **BDD-10**：新增独立检测分支 `_scan_debt_roadmap_signal(task_dir, state_file)`：
  1. 复用既有 `_retries_over` 的 subprocess 调用模式，新增调用
     `agate-state-get.py task_id STATE_FILE`（`agate-state-get.py:37-39` 已支持 `task_id` op，
     无需新增该脚本任何代码）取得 `tid`；`tid` 为空则该检测直接跳过（无信号）
  2. 工作区根路径推导：`workspace = os.path.dirname(os.path.dirname(os.path.abspath(task_dir.rstrip(os.sep))))`
     （对应生产环境固定约定 `{AGATE_WORKSPACE}/tasks/{Txxx}/`——`P0-brief.md` 的
     `workspace_path` 字段与 `dispatch-protocol.md` 全文均按此两层约定书写，非本任务新造假设）
  3. 检查 `{workspace}/debt/tech-debt.md` 是否存在，若存在则正则搜索
     `re.search(r'task_id:\s*"?' + re.escape(tid) + r'"?\s*$', text, re.MULTILINE)`
  4. 检查 `{workspace}/roadmap/roadmap.md` 是否存在，若存在则正则搜索
     `re.search(r'\|\s*' + re.escape(tid) + r'\s*\|', text)`（命中"关联任务"表格列）
  5. 两处任一命中 → 追加**独立于** `warnings` 列表的第二个 stderr 消息块，标题区分为
     `GATE RETRO: 建议复盘 — 发现机制缺口信号：`（与异常模式标题
     `GATE RETRO: 建议复盘 — 检测到异常模式：` 文案上可区分），内容
     `  - {tid} 关联的 DEBT/roadmap 条目已登记（可能存在机制缺口，建议复盘归因）`
  6. exit code 不变（仍是 `sys.exit(0)`，两个消息块可同时输出，互不排斥）
- 该分支实现细节详见 §3.1

**类 4.3 — `agate/state-machine.md`**：

- **BDD-12**：第 481 行原文
  `不写思考过程、不写文件内容摘要、不写 subagent 返回原文——只写决策和下一步`
  改为
  `不写思考过程、不写文件内容摘要、不写 subagent 返回原文——只写决策、下一步和触发决策的简要依据
  （依据示例：gate 输出摘要 / BDD 编号 / 文件路径引用；不等同于展开的思考过程）`
  ——三项既有排除原样保留（"不写思考过程/不写文件内容摘要/不写 subagent 返回原文"逐字未动），
  只在"只写决策和下一步"后追加"和简要依据"分句 + 一句依据定义，满足 BDD-12 Then 子句的对照
  可校验性
- **BDD-13**：在 `orchestrator-log.md 防无响应` 小节之后（第 491 行"commit 被 hook 拦截"一行前
  或后均可，选择放在其后以保持"防无响应"主题的连贯性不被打断）新增一个平级小节
  `**L2 会话 checkpoint（两件套）——P{n}-checkpoint.md + task-session-summary.md**`（P2 重试
  #1 修订：恢复 roadmap.md 原始两件套设计，非单一文件），正文显式回答四问，见 §3.2 展开

**类 4.4 — 跨文件同步（`loop-orchestration.md` / `agate/assets/templates/task-files.md`）**：

- **BDD-14**：`grep -n "orchestrator-log" agate/loop-orchestration.md` 命中第 168、173 行，
  `grep -n "orchestrator-log" agate/assets/templates/task-files.md` 命中第 45 行——三处原文
  分别为"…+ orchestrator-log.md）"（纯落盘清单式提及）、"`orchestrator-log.md` 防无响应——长
  操作前写 `NEXT: ...`，写下去就完成使命，不需要再读回来"（防无响应用途摘要）、"防无响应锚点
  （长操作前写 NEXT:），详见 state-machine.md「orchestrator-log.md 防无响应」节"（指针式引用）。
  **核实结论：三处均未逐字复述被 BDD-12 扩展的旧限制性表述"只写决策和下一步"**，语义上不与
  扩展后的新规则矛盾（新规则是"只写决策和下一步"的超集，不是替换），按 P1 BDD-14 Then 子句
  "不要求逐字重复新语义"的免于强制改字条款，**本次不改这三处文本**，改动动作是"确认不矛盾"
  （即本条 BDD 的验收方式是核实结论，不是文本 diff——已在本节写明核实过程供 P7 复核）
- 三处引用点的 anchor 目标（`state-machine.md`「orchestrator-log.md 防无响应」小节标题）
  保持不变（BDD-13 新增小节是平级新增，不改这个既有标题），故第 45 行的"详见"指针依然有效，
  无需连带更新

**类 4.5 — `agate/AGENTS.md`**：

- **BDD-15**：第 11 行原文
  `仓库根的 docs/ 目录存放 agate 项目的开发资料——设计文档、评审记录、路线图、复盘。这些都是
  仓库维护者（author）写的，使用者无需阅读。`
  改为区分历史/新复盘两支：
  `仓库根的 docs/ 目录存放 agate 项目的开发资料——设计文档、评审记录、路线图，以及迁移前旧布局下
  的历史复盘（docs/reviews/，2026-08-19 前）。这些都是仓库维护者（author）写的，使用者无需阅读。
  新复盘归 tasks/{Txxx}/retrospective.md（模板见 agate/assets/templates/retrospective-template.md），
  同样是维护者产物，使用者无需阅读，但路径不在 docs/ 下。`
  ——只改这一行所在段落，不触碰"入口导航"表或文件其余部分（收窄范围，遵守约束 8）

**类 4.6 — `docs/reviews/` 存量 5 份复盘文件顶部标注**（BDD-16 决策已在 P1 定案，P2 只设计标注
实现方式）：

- **BDD-16**：对以下 5 个文件（P1 计为"4 份"，因 tag0010-0011 一组含 2 个物理文件）逐一在文件
  第 1 行前插入统一标注行，模板文案沿用 P1 已给出的原文（逐字复用，不另起措辞）：
  `> 历史复盘（迁移前旧布局），新复盘请见 \`tasks/{Txxx}/retrospective.md\`（模板：
  \`agate/assets/templates/retrospective-template.md\`）`
  - `docs/reviews/retrospective-tag0008-docs-20260817.md`
  - `docs/reviews/retrospective-tag0010-0011-docs-20260815.md`
  - `docs/reviews/retrospective-tag0010-0011-docs-20260815-review.md`
  - `docs/reviews/retrospective-tag0013-docs-20260816.md`
  - `docs/reviews/retrospective-tag0014-docs-20260816.md`
  文件位置本身不变（不物理迁移），`roadmap.md` 对这 5 份文件的路径引用保持不变（P1 已确认）

**类 4.7 — `agate/scripts/agate-feedback.py`（新增）**：

- **BDD-17**：解析入口，读取传入的 `retrospective.md`，用与 `agate-frontmatter-check.py:128-136`
  `_extract_frontmatter_block` 等价的正则（文件头 `---\n...\n---` 块提取，本地实现一份等价函数，
  不 import 该脚本——理由见 §4 minimal_validation）+ `yaml.safe_load` 取
  `mechanism_issues`/`execution_issues`/`feedback_ready`；`## agate 反馈` 节用标题正则
  `^## agate 反馈\s*$` 定位起点，到下一个 `^## ` 或文件尾为止取节内文本
- **BDD-18**：见 §2 候选方案 B，采纳"轻量正则脱敏"
- **BDD-19**：`AGATE_FEEDBACK` 读取用 `os.environ.get("AGATE_FEEDBACK", "off")`（沿用仓库
  `os.environ.get("AGATE_XXX", 默认值)` 既有惯例，如 `agate_common.py:408` 的
  `AGATE_TDD_TIMEOUT`），值非 `"on"` → stderr 输出"agate-feedback: 功能未启用（设置
  AGATE_FEEDBACK=on 启用）"，`sys.exit(2)`（2 = 功能性跳过，区别于 1 = 真实错误，如文件不存在/
  解析失败），不产生任何 stdout/JSON
- **BDD-20**：产出到 stdout 的结构化 JSON（`mechanism_issues`/`execution_issues`/脱敏后的
  `## agate 反馈` 节文本）+ 一段 Markdown 格式的 issue/PR 正文片段（同一次调用两者都打印，用
  分隔行区分，或用 `--format json|markdown|both`，默认 `both`）；脚本内不 `import subprocess`
  调用任何 `git push`/`gh` 命令（P4 实现后 `grep -n "subprocess\|gh \|git push"
  agate-feedback.py` 应为空，作为该 BDD 的验收方式之一）

### 1.2 不改什么（Not Modify）

- **`docs/hardening-roadmap.md:200` P2.68**——P1 第 7 节已判定为历史提案讨论文档，不属本任务
  协议改动对象，本设计同样不碰，是否标注 superseded 留给 roadmap 维护者
- **`agate-workspace/archived/` 历史归档**——P1 第 7 节已判定不扫描细节、不作改动对象，本设计
  同样不碰（不因为要设计 L2 checkpoint / 复盘机制就回头改历史归档里的旧提法）
- **`agate-workspace/tasks/TAG0013-script-consistency/{P1-requirements.md,P0-brief.md}` 与
  `HANDOFF-TAG0013.md`**——P1 第 7 节已判定是完成时点存证记录，不追溯改写，本设计同样不碰
- **`agate/WORKFLOW.md:91`**——目录树注释里的一行路径级提及（"logs/ # 运行日志（orchestrator-log
  等）"），P1 同类扫描已判定不含语义描述、扩展语义不影响其正确性，本设计不改
- **`agate/WORKFLOW.md:318`（2.12 行）**——虽然是 check-retrospective.py 的另一处描述锚点，但
  该行文案是"异常模式提醒（重试超限/SCOPE+/override）→ 写复盘；不阻塞 commit"，只描述触发条件
  类别，不含具体路径字符串，BDD-9 改的是脚本内 stderr 文案不是 WORKFLOW.md 表格描述，且该行
  未被 P1 列入任何 BDD 的处理对象，故不改（模板挂钩点已选定 `phase-cards/P8-release.md` 承载，
  见 1.1 类 4.1 BDD-8）
- **`agate/state-machine.md:361`**（gate 失败后追加 orchestrator-log 一行的既有用法）——P1 同类
  扫描已确认是"记录 gate 失败"的既有用法，与本任务扩展的"决策+依据"是并存关系，不需要改
  （BDD-12 只改第 481 行的规则说明句，不改第 361 行的用法示例）
- **`agate/dispatch-protocol.md`**——grep `postmortem|retrospective|复盘` 零命中，本任务未把
  它选为 BDD-8 的模板挂钩点（挂钩点已定为 `phase-cards/P8-release.md`，见 1.1），不新增引用
- **`agate/assets/templates/task-files.md` 的"各阶段文件清单"表**（非"辅助文件"表）——不新增
  `retrospective.md` 作为强制阶段产出行，因为 P1 BDD 均未要求复盘成为阻断式门槛产物（沿用
  "只提醒不阻断"哲学），只在"辅助文件"表补充两行说明性质的引用（`P{n}-checkpoint.md` +
  `task-session-summary.md`，见 §3.3），不动阶段门槛表结构
- **`docs/reviews/agate-alignment-review-*.md`、`opencode-session-extraction-guide.md`**——
  P1 同类扫描已判定是评审/指南类文档，不是复盘正文，不在存量迁移对象范围
- **`check-retrospective.py` 的 exit code 契约（恒为 0）**——BDD-10 新增检测分支不改变这个
  契约，只新增一段 stderr 输出

### 1.3 风险在哪（Risk，每条配缓解措施）

| # | 风险 | 缓解措施 |
|---|------|---------|
| R1 | BDD-10 的工作区路径推导（`task_dir` 两级向上）在真实部署路径成立，但若某任务的 `task_dir` 传参不遵循 `{AGATE_WORKSPACE}/tasks/{Txxx}/` 约定（如测试环境／未来路径重构），推导会指向错误目录 | 推导失败时静默无信号（不报错、不新增 warning），因为 `_scan_debt_roadmap_signal` 内部对 `os.path.isdir`/`os.path.isfile` 做存在性检查，目录不存在直接跳过——退化行为等价于"未检测到信号"，不影响脚本恒 exit 0 的契约，不会因路径推导错误而误报或崩溃 |
| R2 | agate-feedback.py 的正则脱敏（候选 B1）存在"脱敏遗漏"——某些项目特定信息（如内部代号、非标准路径格式、用户名）不在"项目名/绝对路径"两类规则覆盖范围内 | ①BDD-20 已把"脚本不自动提交"作为强制边界，产出物是待人工提交内容，人工复核是最终防线；②在 agate-feedback.py 的 stdout 输出末尾追加一行固定提示"请提交前人工复核以下内容是否包含未预期的项目特定信息"，把"最终把关"责任显式移交人工，不依赖脚本自身完备性 |
| R3 | 跨文件路径字符串一致性（BDD-9/BDD-10/BDD-16 共享 `tasks/{Txxx}/retrospective.md` 字符串，P1 §5 已声明 P7 需交叉核对）——三处若字面拼写不一致（如漏了尾部 `/` 或大小写），会造成新的"三处不一致"问题（正是本任务要修的那个问题） | P7 一致性检查逐字比对三处字符串（`check-retrospective.py` stderr 文案 / `retrospective-template.md` 内文档路径引用 / `AGENTS.md:11` 新文案），新增文档结构测试（`test_retrospective_protocol_docs.py`）里对三处做同一个 grep 断言 `tasks/{Txxx}/retrospective.md`（字面量整体匹配，非拆开的子串），三处任一拼写漂移会导致该测试组红灯 |
| R4 | `state-machine.md` 新增的「L2 会话 checkpoint」小节（含 `P{n}-checkpoint.md` + `task-session-summary.md` 两件套）与既有 `orchestrator-log.md` 防无响应小节紧邻，未来维护者可能误以为三者是同一机制的不同叫法，产生概念混淆 | 新小节开篇第一句显式声明"与 orchestrator-log.md 的关系"（三者互补，非替代/包含，见 §3.2 问题①的回答），并在 orchestrator-log.md 小节末尾加一句"另见下方「L2 会话 checkpoint」（阶段级 `P{n}-checkpoint.md` + 任务级 `task-session-summary.md`）"形成双向指针，降低概念混淆概率 |
| R5 | `docs/reviews/postmortem-template.md` 物理 git mv 后，仓库里可能存在未被本次 grep 扫描覆盖的第三方脚本/CI 配置硬编码旧路径（P1 同类扫描已限定范围为 `agate/*.md`、`phase-cards/*.md`、`assets/**/*.md`、`scripts/*.py`、`scripts/*.sh`，未覆盖 CI yaml/其它工具配置） | P4 实现完成后跑一次全仓兜底 grep（`grep -rn "docs/reviews/postmortem-template" . --include="*.yml" --include="*.yaml" --include="*.json"`），若有命中转入 P7 DEVIATION 处理；本设计不预先假设零命中，把这一步列为 P4 实现完成标志之一（见 §5） |
| R6 | check-retrospective.py 新增分支读取 `tech-debt.md`/`roadmap.md` 两个文件，若这两个文件因故内容极大（不太可能，但作为防御性设计考虑），正则全文扫描可能有轻微性能影响 | 两文件当前规模（roadmap.md ~350 行、tech-debt.md 条目制）远低于需要流式处理的量级，且该分支只在 `os.path.isfile` 判定后触发一次全文 `re.search`（非循环重复扫描），性能风险可忽略，不做额外优化设计（YAGNI） |

## 2. 候选方案与权衡（两个"真分叉"设计维度，按 dispatch-context 约束 2 展开）

### 候选方案 A：L2 会话 checkpoint 落点（BDD-13 四问）

**方案 A1（采纳）：两件套专用文件 `P{n}-checkpoint.md`（每阶段）+ `task-session-summary.md`
（任务级），均不叠加进 orchestrator-log.md**

具体设计（回答 BDD-13 的四问）：

1. **落盘时机（两件套，恢复 roadmap.md 原始设计——本节为 P2 重试 #1 修订，替换上一版"只在 P8
   落盘一次"的设计）**：L2 会话 checkpoint 由两个互补的落盘动作组成，缺一不可，对应
   `agate-workspace/roadmap/roadmap.md` RM-AG0020 详情节第 5 点"事实依据三层"原文里明确并列的
   两件套：
   ①**每阶段 gate 通过时落盘 `P{n}-checkpoint.md`**（本阶段异常/关键判断/subagent 表现，极简
   颗粒度，2-4 行即可）——这是防"任务中途 compact"的核心保障：它在任务生命周期的每一个阶段边界
   都留下一个非空的 L2 落点，不依赖任务跑到 P8 才产生第一次 L2 记录；
   ②**P8 gate 通过后一次性落盘 `task-session-summary.md`**（任务级过程摘要，颗粒度更完整，允许
   展开因果链叙述）——沿用 roadmap.md"复盘时机前置"决策（2026-08-16 定稿），在 session 仍完整
   时抢先写出摘要，正式复盘在 merge main 后基于摘要写。

   **为什么不能只保留②（上一版设计的问题，本次修订不再依赖同一断言）**：上一版理由是"每阶段
   结束时的颗粒度已经由既有 `P{n}-progress.md`（分阶段落盘）+ `orchestrator-log.md`（逐决策
   追加）覆盖，属 L1，不需要 L2 再重复一份"——但这个等价性断言没有做内容层面的逐项比对：
   `P{n}-progress.md` 是 **subagent** 产出的过程中间产物（`task-files.md:41`"分阶段落盘的中间
   产物"），不是**主 Agent**对本阶段的评估；`orchestrator-log.md` 经 BDD-12 扩展后是"决策+简要
   依据"，颗粒度是逐决策，也不等同于 roadmap.md 定义的"本阶段异常/关键判断/subagent 表现"这种
   阶段级总结。两者是否真的覆盖了 `P{n}-checkpoint.md` 想保留的信息，此前未经比对即采纳为前提，
   本次修订不再依赖这个未经验证的断言。若只保留②，L2 唯一落点在 P8 完成后：任务中途（如
   P4/P5）发生 session compact 时，L2 尚未产生任何一次落盘——这恰好是 P0-brief 问题⑦要解决的
   失效场景本身没有被保护到，与 BDD-13 的核心目的（防 session compact）相悖。恢复①后，即使
   compact 发生在任何阶段之间，最近一次 `P{n}-checkpoint.md` 都是一个非空的 L2 事实源。
2. **落盘文件路径与命名**：
   - `{AGATE_WORKSPACE}/tasks/{Txxx}/P{n}-checkpoint.md`（`{n}` 为实际阶段号，如
     `P4-checkpoint.md`）——沿用 roadmap.md RM-AG0020 详情节的既有命名，与 `P{n}-*.md` 系列
     阶段产出文件并列，是任务目录下的顶层文件，但**不是阶段门槛产出**（gate 不要求其存在，属
     「辅助文件」，见 §3.3），缺失不阻断阶段推进
   - `{AGATE_WORKSPACE}/tasks/{Txxx}/task-session-summary.md`——同样沿用 roadmap.md 既有命名；
     与其它阶段产出文件并列，不嵌套进 `orchestrator-log.md`
3. **与 BDD-12 扩展后的 orchestrator-log 语义关系**：**三者互补，不是相互替代/包含**。
   `orchestrator-log.md` 是 L1（P0-brief 的三层事实源模型已把 orchestrator-log 明确归入 L1：
   "L1 仓库落盘（git log/产出/orchestrator-log/progress）"），特点是持续追加、逐决策颗粒度、
   只写"决策+简要依据"不写展开的思考过程；`P{n}-checkpoint.md` 是 L2 的**阶段级**颗粒度，比
   orchestrator-log 更粗（一阶段一条，不是逐决策一条）、比 progress.md 更贴近主 Agent 的判断
   视角（progress.md 是 subagent 中间产物，checkpoint 是主 Agent 对本阶段的评估）；
   `task-session-summary.md` 是 L2 的**任务级**颗粒度，一次性落盘，允许包含更完整的"为什么这么
   做"因果链叙述（弥补 orchestrator-log 明确排除的"思考过程"缺口）。P7/正式复盘写作时交叉引用
   三者，不是二选一或三选一
4. **防 session compact 的落盘策略**：
   - `P{n}-checkpoint.md`：主 Agent 在**每个阶段 gate 通过后、派发下一阶段之前**写盘（与该
     阶段的 phase commit 同一时间窗口内完成，是"session 仍完整"的高频锚点），沿用
     orchestrator-log 的"写下去就完成使命"原则——不要求写完后再读回验证
   - `task-session-summary.md`：由主 Agent 在 P8 gate 通过、进入 `phase-cards/P8-release.md`
     「READY 收尾检查」节之前主动写盘（该检查节本就是"gate 通过后、主 Agent 亲自执行"的既定
     收尾动作），同样写完即完成使命，不回读校验

- 优点：与 roadmap.md RM-AG0020 原始两件套设计一致，不需要论证"为什么收窄"；L2 在任务生命周期
  的每个阶段边界都有非空落点，真正覆盖"中途 compact"场景（BDD-13/P0-brief 问题⑦的核心目的）；
  L1/L2 边界清晰（L2 的两个子机制分别对应阶段级/任务级颗粒度，均不与 L1 的逐决策颗粒度重叠）；
  沿用 roadmap.md 已有命名，跨文档降低认知负担；与 orchestrator-log.md 的"仅追加不编辑"纪律
  解耦，两个 L2 文件都可以是一次性完整写入（不需要遵守追加式写法约束）
- 缺点：新增两类文件（`P{n}-checkpoint.md` 逐阶段 + `task-session-summary.md` 一次性），
  `task-files.md`「辅助文件」表需要补两行说明；`P{n}-checkpoint.md` 要求主 Agent 在每个阶段
  gate 通过后都执行一次额外写盘动作，比"只在 P8 写一次"多了 P1-P7 共 7 次执行点（改动面与
  执行负担均比上一版设计大，但换来的是"中途 compact 有保护"这个 BDD-13 的核心诉求，权衡后
  判定值得）
- 工作量：`state-machine.md` 新增约 20-30 行小节（含两个子机制说明）+ `task-files.md` 辅助
  文件表新增 2 行

**方案 A2：扩展 orchestrator-log.md 语义直接覆盖 L2 checkpoint 内容（不采纳）**

- 实现：不新开文件，在 `orchestrator-log.md` 的既有"必须记录的事件"列表里新增一类事件
  `TASK_SUMMARY: {任务完成时的完整摘要}`，任务完成时追加写入这一条（内容可以比其它事件行长
  得多，包含因果链叙述）
- 优点：零新文件类型，`task-files.md` 不需要改动，实现改动面理论上最小
- 缺点：①P0-brief 的三层事实源模型已经把 orchestrator-log.md 明确归为 L1，若 L2 内容也塞进
  同一个文件，L1/L2 在**物理文件**层面就没有边界了，P1 第 2 节隐含需求 3 强调的"跨文件耦合需要
  P7 逐条核对"反而变成"同一文件内部两种语义混杂"，更难核对而不是更容易；②orchestrator-log.md
  的既有纪律是"仅追加不编辑不整理"+"不写文件内容摘要"，L2 恰恰需要写"任务级完整摘要"，这与
  orchestrator-log 自身的既有排除项（"不写文件内容摘要"）**直接语义冲突**——若把摘要塞进去，
  等于打破了 orchestrator-log 现有的"保持轻量"设计初衷（该文件当前定位是"防无响应锚点"，内容
  故意做得短，混入长摘要会让该文件本身的"扫一眼确认还活着"用途退化）；③`orchestrator-log.md`
  在 TAG0014 复盘中已被实测"目录里经常不存在"（P0-brief known_risks 已引用此教训）——若把 L2
  这个新机制的可靠性绑定在一个本身就有"是否被创建"不确定性的既有文件上，新机制从设计起点就
  继承了旧机制的可靠性问题，不是一个干净的起点
- 选择理由：A2 的"零新文件"收益，被"L1/L2 语义边界在物理文件层面消失 + 与
  orchestrator-log 现有排除项直接冲突 + 继承旧机制可靠性问题"三项成本抵消。**采纳 A1**

### 候选方案 B：`agate-feedback.py` 的匿名化实现深度（BDD-18）

**方案 B1（采纳）：轻量正则脱敏（项目名字符串替换 + 绝对路径截断/移除）**

具体规则：

1. **项目名替换**：脚本接受可选参数 `--project-name`；未提供时默认取
   `os.path.basename(os.getcwd())`（脚本预期在项目根或其子目录下运行，与仓库内其它脚本"cwd 即
   项目根"的既有假设一致，如 `agate_common.py` 的 `project_root` 参数模式）。对提取出的
   `mechanism_issues`/`execution_issues`/`## agate 反馈` 节文本做大小写不敏感全词匹配替换为
   `<PROJECT>`
2. **绝对路径处理**：正则 `re.compile(r'(?:[A-Za-z]:\\|/)[^\s\'"`]+')` 匹配类 Unix 绝对路径
   （以 `/` 开头）与类 Windows 绝对路径（`C:\` 开头）连续 token。命中后：若路径以当前项目根
   （`os.getcwd()` 或 `--project-name` 对应的推导根路径）为前缀，截断前缀只保留仓库内相对部分；
   若不以项目根为前缀（如 `/home/xxx/.other-tool/...` 这类项目外路径），整体替换为 `<PATH>`
3. 两条规则应用顺序：先做路径处理（避免路径里恰好包含项目名字符串时被路径规则和项目名规则
   重复处理，路径规则优先命中并整体替换/截断，截断后的剩余相对路径部分若仍包含项目名字符串
   则不再二次替换——因为截断后的相对路径本身就不再是可识别的"项目位置"信息）
4. 已知局限（不视为设计缺陷，见风险表 R2 的缓解措施）：不覆盖用户名、内部代号等未落在"项目名/
   绝对路径"两类范畴内的敏感信息；`AGATE_FEEDBACK` 默认 off + BDD-20 强制"不自动提交、待人工
   提交" 的既有边界已经把最终把关责任放在人工复核这一步，脚本侧脱敏是第一道防线不是唯一防线

- 优点：实现简单（~30-40 行，两条正则规则），可单元测试覆盖具体输入输出对（如"路径含项目根 →
  截断为相对路径"/"路径不含项目根 → 整体替换"两个用例），符合 BDD-18 Given 子句字面描述的场景
  （"「## agate 反馈」节内容包含项目名/绝对文件路径等项目特定信息"——这个 Given 明确预设内容是
  自由文本形态，需要从文本里"识别并替换"，与正则方案直接对应）
- 缺点：脱敏覆盖面有限，理论上存在"没被两条规则捕获的敏感信息"漏网风险
- 工作量：`agate-feedback.py` 内一个 `_anonymize(text, project_root)` 函数 + 2-3 个单测用例

**方案 B2：结构化字段白名单提取（不采纳）**

- 实现：不处理自由文本，只从 frontmatter 提取 `mechanism_issues`/`execution_issues` 列表项
  原样输出（假设这些列表项本身已经是"可安全外泄颗粒度"的短描述，不含路径/项目名），`## agate
  反馈` 节要求作者在撰写时就把内容组织成与 frontmatter 列表一一对应的结构化条目（不允许自由
  叙述段落），脚本只做"结构完整性校验"（条目数与 frontmatter 列表数一致）而不做文本内容改写
- 优点：脚本侧不需要维护正则规则，理论上"没有脱敏遗漏"这个失败模式（因为压根不接触自由文本）
- 缺点：①这个方案的安全性建立在一个未被 BDD-6 实际约束的假设上——BDD-6 对 `mechanism_issues`/
  `execution_issues` 只声明了"list"类型，没有任何"内容颗粒度必须安全"的 schema 约束，撰写者
  完全可能在列表项里写入类似"backend/services/auth.py 里 /home/alice/secrets 硬编码"这种仍
  包含绝对路径的条目——B2 的"结构化=安全"前提在当前 BDD-6 定义下并不成立，需要的话还要再叠加
  一层内容脱敏，退化成"B2 的复杂度 + B1 的脱敏逻辑"两者都要，得不到对应的额外安全保证；
  ②BDD-18 的 Given 子句字面描述的是"「## agate 反馈」节内容包含项目名/绝对文件路径"这种自由
  文本场景，B2 要求作者重新组织该节为结构化条目，等于变相修改了 BDD-7 已经定案的"节内容边界"
  定义（BDD-7 只要求"内容边界"，未要求"结构化格式"），P2 阶段不应该借实现方案反向收紧上游
  BDD-7 已经拍板的验收标准
- 选择理由：B2 承诺的"更安全"建立在 BDD-6 当前定义不成立的前提上，实际实现时仍需要叠加 B1 同款
  的文本脱敏逻辑才能兑现安全承诺，属于"更复杂但不换来对应保证"。**采纳 B1**（YAGNI：先满足
  BDD-17/18 字面要求的最小可行实现，脱敏覆盖面不足的风险已有人工复核这道既定防线兜底）

## 3. 方案设计细化

### 3.1 check-retrospective.py 新增分支实现要点（BDD-9/10/11）

```
_scan_debt_roadmap_signal(task_dir, state_file):
    tid = 调 agate-state-get.py task_id STATE_FILE（同 _retries_over 的 subprocess 模式）
    if not tid: return ""
    workspace = 两级向上推导（见 1.1 类 4.2 第 2 点）
    debt_file = workspace/debt/tech-debt.md
    roadmap_file = workspace/roadmap/roadmap.md
    命中 debt_file 或 roadmap_file 的 task_id 正则 → 返回 tid（供主流程判断是否输出第二个消息块）
    否则 → 返回 ""
```

`main()` 内在现有 `warnings` 列表输出逻辑之后，新增独立的第二段 stderr 输出（不并入
`warnings` 列表，因为 BDD-10 要求消息文案与异常模式"可区分"，用两个独立标题块实现区分，而
不是共享同一个 `warnings:` 列表前缀）。

### 3.2 state-machine.md 新增小节草案要点（BDD-13，供 P4 落字，非最终文案）

小节标题：`L2 会话 checkpoint（两件套）——P{n}-checkpoint.md + task-session-summary.md`
（P2 重试 #1 修订：恢复 roadmap.md RM-AG0020 详情节原始两件套设计，不再是单一
`task-session-summary.md` 小节）

正文须覆盖：
①**与 orchestrator-log.md 的关系**（三者互补，见候选方案 A1 第 3 点原文——L1 逐决策 /
L2-阶段级 `P{n}-checkpoint.md` / L2-任务级 `task-session-summary.md`，三者颗粒度不同、不互相
替代）
②**`P{n}-checkpoint.md` 子机制**：落盘时机（每个阶段 gate 通过后、派发下一阶段之前）+ 文件
路径（`{AGATE_WORKSPACE}/tasks/{Txxx}/P{n}-checkpoint.md`，`{n}` 为实际阶段号）+ 内容颗粒度
（本阶段异常/关键判断/subagent 表现，2-4 行极简记录，不要求完整叙述）+ 防 compact 策略（主
Agent 写盘即完成使命，不回读校验）
③**`task-session-summary.md` 子机制**：落盘时机（任务完成、P8 gate 通过后，READY 收尾检查
前）+ 文件路径（`{AGATE_WORKSPACE}/tasks/{Txxx}/task-session-summary.md`）+ 防 compact 策略
（P8 gate 通过后主 Agent 亲自写盘，写完即完成使命，不需回读校验）
④**两者共同覆盖的防 compact 范围**：`P{n}-checkpoint.md` 保证任务生命周期每个阶段边界都有
非空 L2 落点（覆盖"中途 compact"场景）；`task-session-summary.md` 补充任务完成时的完整因果链
叙述（覆盖"任务级复盘写作"场景）——两者时间线上互补，不是同一内容的两份拷贝

P2 不规定这两个文件内部的具体字段 schema（BDD-13 的 Then 子句只要求 P2-design.md 回答四问，
不要求定字段格式），字段格式（含 `P{n}-checkpoint.md` 的具体行文模板）留给未来任务或本任务
P4 implementer 视实现便利性决定，若 P4 认为需要具体字段才能落地，按
`[DESIGN_GAP: 需要 P{n}-checkpoint.md / task-session-summary.md 具体字段 schema，P2 未定义]`
标注，交 P7 审查是否需要回 P2 补充。

### 3.3 task-files.md 辅助文件表新增行（配合候选方案 A1，P2 重试 #1 修订：由 1 行改为 2 行）

在「辅助文件（非阶段产出）」表新增两行：

```
| P{n}-checkpoint.md | 主 Agent | L2 会话 checkpoint（每阶段 gate 通过后落盘，本阶段异常/
  关键判断/subagent 表现），详见 state-machine.md「L2 会话 checkpoint」节 |
| task-session-summary.md | 主 Agent | L2 会话 checkpoint（任务完成时一次性落盘），详见
  state-machine.md「L2 会话 checkpoint」节 |
```

## 4. 批次设计（`dispatch_plan`）

**判断结论：单批派发（`mode: single`），不拆批。**

判据（按「派发编排机制」工作量五维评估）：

- **产出文件数**：单次 P4 implementer 的产出集中在少数几类改动（1 个新模板文件迁移改写、
  1 个脚本改动、1 个新脚本、3 个协议文档改动点、1 个 AGENTS.md 改动点、5 个存量文件标注、
  1 个 roadmap.md 同步点、若干测试文件），虽然文件数不少，但**全部是同一条"复盘路径统一"
  语义线索下的加性文本改动**（新增小节/新增字段/文案替换），没有独立的业务逻辑分支需要拆解
- **跨批共享件风险**：本任务 implicit_coupling: true（P1 已声明），`tasks/{Txxx}/retrospective.md`
  这个路径字符串横跨 check-retrospective.py/模板/AGENTS.md/存量标注 4 处（BDD-9/10/16 共享），
  若拆成多批并行执行，同一字符串在不同批次里可能各自措辞（如漏尾部斜杠），恰好制造出本任务
  要修复的那种"三处不一致"问题——**拆批的跨批一致性风险高于单批的上下文体量风险**，这是选
  单批而非拆批的核心理由
  （对应「批次设计前置检查项」的"跨批共享件单列"要求——本任务没有天然可分离、互不重叠的
  批次边界，勉强拆分会人为制造共享件冲突面）
- **复杂度**：P1 risk_level: medium（非 high），「dispatch_plan 机器字段」规则"high 复杂度必须
  拆分"的硬规则不适用；本任务改动虽多但每处改动的实现复杂度低（文本插入/替换/新增小节），
  没有 high 复杂度的子任务
- **并行收益**：20 条 BDD 里脚本类（BDD-9/10/11/17/18/19/20）与文档类（BDD-1/2/3/5/6/7/8/12/
  13/14/15/16）理论上可并行两批实现，但脚本类与文档类之间存在语义耦合（BDD-6/7 是 BDD-17 的
  输入依赖，P1 §5 已声明），若拆批并行，脚本批次的 implementer 需要"预读"文档批次尚未落地的
  frontmatter 字段名/节标题——这在静态拆批（static-batch）模式下无法保证顺序，parallel 模式
  下更是直接违反依赖关系。改用 serial（先文档批后脚本批）能解决依赖问题，但两批各自的产出/
  输入文件数远低于"派发编排机制"任务粒度基准（产出 ≤3 / 输入 ≤3）的拆分门槛，拆分收益（更小
  的单次上下文）不足以抵消"两次派发协调成本 + serial 模式下批次间交接开销"

**结论**：单发派发一个 implementer subagent，files_to_read（见 §5）已经把 20 条 BDD 涉及的
文件收窄到明确清单，控制单次上下文体量，不需要靠拆批来控制体量。

## 5. 四字段声明

### gate_commands

```yaml
gate_commands:
  P3: "python3 -m pytest agate/tests/unit/test_check_retrospective.py agate/tests/unit/test_agate_feedback.py agate/tests/unit/test_retrospective_protocol_docs.py -v"
  P3_formatter: "pytest.sh"
  P5: "python3 -m pytest agate/tests/ -q --tb=no && python3 agate/scripts/check-protocol-consistency.py --strict"
  P5_formatter: "pytest.sh"
  P5_timeout_seconds: 180
```

- **P3 覆盖脚本类 BDD（BDD-9/10/11/17/18/19/20）**：三个测试文件均新增/扩展，先红后绿，
  `test_check_retrospective.py` 新增 ≥2 用例（路径文案 BDD-9 + DEBT/roadmap 信号 BDD-10，见
  P1 §4.2 BDD-11 Then 子句原文要求），`test_agate_feedback.py` 全新文件覆盖 BDD-17~20
- **P3 同时覆盖纯文档类 BDD（BDD-1/2/3/5/6/7/8/12/14/15/16）**：新增
  `agate/tests/unit/test_retrospective_protocol_docs.py`，风格沿用既有
  `agate/tests/unit/test_review_role_docs.py`（`agate_root` fixture + 逐 BDD 一个
  `test_bdd_N_xxx` 函数 + 文件内容子串断言，不 import 被测协议文档为 Python 模块，纯文本读取
  校验）。这就是 dispatch-context 约束 4 要求的"P5 如何验证纯文档 BDD"的具体答案——不新增独立
  一次性验证脚本，复用 pytest 同一测试运行器，跟脚本类 BDD 共享同一次 `gate_commands.P3`/
  `P5` 调用，不新增第二套工具链
- **BDD-4/13**：BDD-4（技术债登记核对行强制说明文案）与文档类 BDD 一样走
  `test_retrospective_protocol_docs.py` 的 grep 断言；BDD-13 的"四问是否回答完整"这件事本身
  仍由本 P2-design.md（候选方案 A + §3.2）承载，不产生独立可执行测试用例，P6 verifier 读取本
  文件核对。但 P2 重试 #1 恢复 `P{n}-checkpoint.md` 机制后，"两个文件名字符串是否真的落进了
  `state-machine.md` 协议文档正文"是可以静态断言的锚点——`test_retrospective_protocol_docs.py`
  新增 `test_bdd_13_l2_checkpoint_docs`，断言 `state-machine.md` 同时含 `P{n}-checkpoint.md`
  与 `task-session-summary.md` 两个字符串（且在「L2 会话 checkpoint」小节标题之后出现），与
  BDD-4 走同一测试文件、同一 grep 断言模式，不新增第二套工具链
- **P5_timeout_seconds: 180**：`gate_commands.P5` 链式命令（全量 pytest + 协议一致性检查）
  属"单元测试类"，按角色卡三档基准表 120s 起档；`agate-workspace/roadmap/roadmap.md`
  RM-AG0026 条目记录的实测数据"823 用例单次 106-115s"作为经验锚点，当前套件 909 用例 + 2
  skipped 规模相近但略大，加上链式追加的 `check-protocol-consistency.py --strict`（P1 objective_info
  已确认该命令单独可通过），180s 留出约 50-60% 缓冲，避免像 TPV0093 教训那样阈值过低误杀正常
  完成的长命令
- **P3 不声明 `timeout_seconds`**：按角色卡字段规则第 1 条，P3 继续走 `AGATE_TDD_TIMEOUT`
  env var 机制（默认 120s），不与 `timeout_seconds` 声明层混用

### env_constraints

```yaml
env_constraints:
  debug_env: "Linux（P0-brief 继承）；本任务纯 Python 脚本 + Markdown 文档改动，无需启动调试
    服务/浏览器/数据库，pytest 直接对脚本文件 subprocess 调用即可验证"
  isolation_check: "check-retrospective.py 新增的 DEBT/roadmap 检测分支（BDD-10）依赖工作区
    目录结构（两级向上推导 debt/roadmap.md 路径），配套单测须构造独立的两层嵌套目录
    （tmp_path/agate-workspace/tasks/T001/ 作为 task_dir，tmp_path/agate-workspace/debt/、
    tmp_path/agate-workspace/roadmap/ 作为兄弟目录），不能复用共享 task_dir fixture 默认的
    单层 tmp_path/task-XXXXXX/ 布局（该 fixture 布局下两级向上会指向 tmp_path 本身而非虚构的
    debt/roadmap 目录），测试需要自行搭建嵌套结构或用 monkeypatch 隔离，避免读取真实仓库的
    agate-workspace/debt/tech-debt.md 或 roadmap.md 造成测试结果依赖仓库实际数据（不可复现）"
```

### files_to_read

```yaml
files_to_read:
  - path: docs/reviews/postmortem-template.md
    why: 迁移+重写的源文件全文，BDD-1~5 的骨架基础（核对清单表格原样保留）
  - path: agate/scripts/check-retrospective.py
    why: BDD-9/10 改动对象，第 93 行路径文案 + main() 现有 warnings 输出结构
  - path: agate/tests/unit/test_check_retrospective.py
    why: BDD-11 新增用例的既有测试结构与 fixture 用法参照（run_cli/task_dir/agate_scripts）
  - path: agate/scripts/agate-state-get.py:29-40
    why: task_id op 已存在，BDD-10 直接复用，不新增该脚本代码
  - path: agate/scripts/agate-frontmatter-check.py:128-136
    why: "_extract_frontmatter_block 正则模式参照，agate-feedback.py 本地实现等价函数（不 import）"
  - path: agate/scripts/agate_common.py:400-482
    why: "AGATE_TDD_TIMEOUT 的 os.environ.get 读取惯例（第 407 行）+ resolve_workspace() 函数体（455-482），BDD-19 的 AGATE_FEEDBACK 开关沿用同款 os.environ.get 模式"
  - path: agate/state-machine.md:470-495
    why: orchestrator-log 防无响应节原文，BDD-12 改动第 481 行 + BDD-13 新增小节的插入位置
  - path: agate/loop-orchestration.md:160-175
    why: BDD-14 核实对象，三处 orchestrator-log 提及原文，用于确认"不改"判断的准确性
  - path: agate/assets/templates/task-files.md:39-48
    why: BDD-14 指针目标 + 候选方案 A1 需要新增的辅助文件表行落点
  - path: agate/AGENTS.md:1-15
    why: BDD-15 改动对象，第 11 行原文与所在段落上下文
  - path: agate/phase-cards/P8-release.md:86-115
    why: BDD-8 挂钩点，READY 收尾检查节新增核对项的插入位置
  - path: agate-workspace/roadmap/roadmap.md:305-333
    why: BDD-8 需要同步的旧路径引用（第 313/316/322 行）+ RM-AG0020 详情节里 L2 checkpoint 的既有设计讨论（候选方案 A1 的命名依据来源）
  - path: agate/tests/unit/test_review_role_docs.py
    why: 新增 test_retrospective_protocol_docs.py 的风格与 fixture 用法参照（agate_root + 逐 BDD 断言函数）
  - path: agate/tests/conftest.py:76-160
    why: create_task_dir 工厂函数实现，BDD-10/11 新增用例若需要自定义嵌套目录结构时参照现有 fixture 写法边界
```

### minimal_validation

```yaml
minimal_validation:
  declaration: "纯代码逻辑，无外部系统依赖"
  reasons:
    - "check-retrospective.py 新增分支复用既有 _retries_over 的 subprocess 调用模式（新增
      对 agate-state-get.py task_id op 的同款调用，该 op 已存在不需新增代码）+ 新增
      _scan_debt_roadmap_signal 两个纯文本正则匹配（tech-debt.md 的 task_id: {tid} 行 /
      roadmap.md 的 | {tid} | 表格单元格），均为内存内字符串处理，无网络/无外部进程（除已有的
      agate-state-get.py 子进程调用模式本身，该模式已在生产使用，非本任务新引入的风险面）"
    - "agate-feedback.py 依赖 yaml.safe_load（仓库既有依赖 pyyaml，多个脚本已使用，无需新增
      依赖）+ 本地实现的 frontmatter 正则提取（参照 agate-frontmatter-check.py 既有实现模式，
      非首次在本仓库出现的技术）+ json.dumps（stdlib）+ 两条正则脱敏规则（候选方案 B1，纯字符
      串处理）"
    - "protocol 文档改动（BDD-1/2/3/5/6/7/8/12/13/14/15/16）是纯文本插入/替换，不涉及运行时
      代码执行路径变化"
  verified_by_reading_code:
    - "agate-state-get.py:37-39 确认 task_id op 已存在——不需要新增该脚本任何代码（读代码验证，
      非假设）"
    - "pre-commit-gate.py:397 确认 check-retrospective.py 当前唯一调用点，调用签名是
      [task_dir, state_file] 两个位置参数——BDD-10 新增功能不改变这两个位置参数的顺序/数量，
      新增的工作区路径推导是脚本内部从 task_dir 派生而非新增第三个必需参数，保持调用方
      pre-commit-gate.py:397 不需要同步改动（T086 B1 教训要求核实的'删除/移动路由后请求流向
      哪个兜底分支'——此处是'新增路径而非删除'，但同样核实了调用点向后兼容，不会因签名变化
      导致 pre-commit-gate.py 的调用失效）"
    - "agate/assets/templates/tech-debt-template.md:70 与 agate-workspace/roadmap/roadmap.md
      的表格列格式确认 task_id 在两个文件里的实际书写格式（yaml 块内 task_id: TAG0003 /
      表格单元格 | TAG0015 |），BDD-10 的两条正则据此设计，非凭空假设格式"
  result: not_needed
  note: "上述三类改动均为纯代码逻辑/纯文本改动，已通过读代码方式核实关键假设（task_id op 存在性、
    调用点签名兼容性、debt/roadmap 文件实际格式），无需额外的最小验证脚本/curl/浏览器测试"
```

## 6. 实现完成的标志

- `agate/assets/templates/retrospective-template.md` 存在且含 BDD-1~7 要求的全部小节标题与
  frontmatter 样例；`docs/reviews/postmortem-template.md` 已被 git mv（不再以旧内容存在于
  原路径）
- `check-retrospective.py` 第 93 行不再含 `docs/releases`；`_scan_debt_roadmap_signal` 存在
  且被 `main()` 调用；`test_check_retrospective.py` 新增 ≥2 用例全部通过
- `agate-feedback.py` 存在，`test_agate_feedback.py` 覆盖 BDD-17~20 全部通过；
  `grep -n "subprocess" agate/scripts/agate-feedback.py` 不含 `git push`/`gh ` 调用
- `state-machine.md` 第 481 行三项排除原样保留 + 新增"依据"分句；新增「L2 会话 checkpoint」
  小节回答四问，且小节正文同时含 `P{n}-checkpoint.md`（阶段级，每阶段 gate 通过后落盘）与
  `task-session-summary.md`（任务级，P8 gate 通过后一次性落盘）两个机制的说明；
  `test_bdd_13_l2_checkpoint_docs` 断言两个文件名字符串均出现在该小节正文内，通过
- `AGENTS.md:11` 区分历史/新复盘措辞；`phase-cards/P8-release.md` 含
  `retrospective-template.md` 路径字符串；5 份存量文件均含统一标注行；
  `roadmap.md` 三处旧路径引用均带更正脚注
- `test_retrospective_protocol_docs.py` 覆盖 BDD-1/2/3/4/5/6/7/8/12/14/15/16 全部通过；
  `test_bdd_13_l2_checkpoint_docs`（BDD-13 静态锚点，见 §5）通过
- `python3 -m pytest agate/tests/ -q --tb=no` 全绿；
  `python3 agate/scripts/check-protocol-consistency.py --strict` 0 ERROR
- 全仓兜底 grep（见风险表 R5）确认无遗漏的旧模板路径硬编码引用

## 7. SCOPE+ 增补区（后续阶段回写）

（本阶段无新增隐含需求，保留占位区供后续阶段使用）
