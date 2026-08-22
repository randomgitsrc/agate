---
phase: P2
task_id: TAG0021-structured-layer
type: design
parent: P1-requirements.md
trace_id: TAG0021-P2-20260822
status: draft
created: 2026-08-22
agent: architect
# ── v2.0 机器字段 ──
candidate_count: 3                # 3 个候选方案（C1 推荐 / C2 对照 / C3 D1 否决项验证），与正文 §2 一致
packages: [agate]                 # 协议本体单一版本单元（P1 frontmatter 继承）
domains: [backend]                # 纯协议/脚本/数据层改造，无 frontend/security（P1 frontmatter 继承）
ui_affected: false                # 无显示/交互变化（P1 frontmatter 继承）
# ── v2.0 派发编排字段（可选）──
dispatch_plan: {mode: serial, batches: [{id: M0, complexity: high}, {id: M1, complexity: high}, {id: M2, complexity: high}, {id: M3, complexity: medium}]}
---

# P2 方案设计 — TAG0021 协议结构化层（RM-AG0022）

> 状态标记：[PROD_NOT_TOUCHED]（仅读主 checkout 协议文件与 ~/.agate 角色/卡片；全部写操作落在 worktree `agate-workspace/` 内）

## 0. 设计输入与本方案要回答的问题

输入基线：P1-requirements.md（16 BDD，M0-M3 分组，决策 D1/D2/D3）+ P1-review.md（approved，7 项核验口径）+ P0-brief.md（issues/known_risks/env_constraints）+ design-structured-layer.md（§3 schema 草案 / §4 S-1~S-6 / §5 M0-M3 / §8 风险）+ HANDOFF-TAG0021.md（硬约束）。

**本方案回答派发指引的 5 个设计问题**（对应 §3 小节）：

| 问题 | 落点 |
|------|------|
| YAML 权威源的数据边界（哪些规则进 YAML、哪些留 md 叙事层） | §3.1 |
| schema 设计（枚举约束、校验机制） | §3.2 |
| S-1~S-6 六条 gate 的判定口径与触发点（pre-commit/CI） | §3.3 |
| M0-M3 各里程碑的落地文件清单与回退边界 | §3.5 |
| 对账模式（M1）的差异可观测出口（WARNING + 计数，BDD-6） | §3.4 |

**对齐 P1 决策（前置声明）**：本方案严格执行 D1（S-1~S-6 独立脚本 `check-structure-consistency.py` + 独立 S 前缀编号，不并入 check-protocol-consistency 的 CHECKS）/ D2（BDD 连续数字编号 BDD-1..16，P1 已定，本文件不新增 BDD）/ D3（M1 首批三脚本 = agate-read-gate-commands / check-pruning / check-gate）。涉及 P2 候选方案的取舍均在 D1 已定的编号空间框架内展开，不重新打开已定决策（C3 候选包含对 D1 的否决理由固化，见 §2.3）。

---

## 1. 影响面梳理（候选方案之前）

> 证据基 = P1 §4.1-4.3 三组同类扫描结论 + 本轮对 worktree 的逐文件实查（gate_commands 正则 4 处实现、check-gate.py P2 分支读取点、check-pruning.py 读取链、check-protocol-consistency.py 扫描面、agate-frontmatter-check.py schema 机制、agate-inject-card.py/agate-next-card.py 注入链、agate_common.py 公共函数、CI workflow、count-tests 基线 749）。三处同源、逐级细化。

### 1.1 改什么（Modify）

按 M0-M3 里程碑组织，逐落点标注关联 BDD。

**M0 — 数据层就位（只加不改）**

| # | 落点（文件/小节/函数） | 改动内容 | 关联 BDD |
|---|------------------------|---------|---------|
| M0-1 | `agate/rules/phases.yaml`（新增） | 阶段定义权威源：`schema_version: 1` + `phases:` 列表（P0-P8 + P6.5，字段见 §3.1） | BDD-1/2/5 |
| M0-2 | `agate/rules/dispatch.yaml`（新增） | 派发定义权威源：三铁律/模板字段/gate 表/五模式编排（字段见 §3.1） | BDD-1 |
| M0-3 | `agate/rules/roles.yaml`（新增） | 角色定义权威源：双层角色 + 机械映射表（字段见 §3.1） | BDD-1/3 |
| M0-4 | `agate/rules/schema/{phases,dispatch,roles}.schema.json`（新增） | draft-07 子集 schema（type/required/enum/properties/items，见 §3.2） | BDD-1/3 |
| M0-5 | `agate/scripts/check-yaml-schema.py`（新增） | 手写 draft-07 子集校验器（参照 agate-frontmatter-check.py 的 SCHEMAS 实现风格，不依赖 jsonschema 包） | BDD-1 |
| M0-6 | `agate/scripts/check-structure-consistency.py`（新增） | S-1~S-6 六条检查（CHECK 编号风格仿 check-protocol-consistency 的 rep 机制，见 §3.3）；含 S 编号自校验（新增 S 与既有 CHECK 1-12 / S-1~S-6 不重复） | BDD-2/3/5/10/12/14 |
| M0-7 | `agate/WORKFLOW.md` 阶段总览表（§阶段总览，行 285-300 区域） | 表头/表尾各加一行 S-1/S-2 锚点声明（表内每行 phase 与 phases.yaml 定义对齐） | BDD-2 |
| M0-8 | 仓库根 `README.md` + `agate/AGENTS.md` 目录结构图 | 新增 `rules/` 一层（`rules/*.yaml` + `rules/schema/`），与既有 md 文件（review-mapping.md/state-transitions.md）并列标注 | H4（BDD-3 引用完整性间接） |
| M0-9 | `UPGRADING.md` 新增 v0.57 章节（M0） | 声明 M0 纯增量不破坏存量项目；预告 M1/M2 行为变化 | H3 |
| M0-10 | `agate/rules/schema/*.json` 与 `agate/rules/*.yaml` 自动进入 SELF-GATE 触发面 | 无文件改动，机制自生效（H2：改协议本体文件的 commit 须含 self-gate 声明） | — |
| M0-11 | 新增 pytest：`agate/tests/unit/test_check_yaml_schema.py` + `test_check_structure_consistency.py` | 先红的失败测试（schema 校验/S-1~S-6 双向一致/引用完整性） | BDD-1/2/3/5 |

**M1 — 双跑对账（读 YAML 与 grep 结果对比，告警不阻断）**

| # | 落点 | 改动内容 | 关联 BDD |
|---|------|---------|---------|
| M1-1 | `agate/scripts/agate_common.py` | 新增对账工具函数：`reconcile_field(op, field, grep_val, structured_val)`（不一致 → stderr `RECONCILE WARNING` + 计数，返回原判定不变）；`read_rules_yaml(rules_root, name)`（读 rules/*.yaml，pyyaml 解析，失败返回 None） | BDD-6/7 |
| M1-2 | `agate/scripts/agate-read-gate-commands.py` | 接入对账：grep 块解析结果 vs dispatch.yaml 的 `gate_commands` 语法声明（合法 key 集 = `is_gate_meta_key` 判据 + `{key}_timeout_seconds`/`_formatter` 后缀规则）对账；任务块内出现未声明 key → WARNING + 计数 | BDD-6/7 |
| M1-3 | `agate/scripts/check-pruning.py` | 接入对账：风险_level/phases 经 agate-md-field-get 读取处（`_md_field` 调用点）增加 frontmatter↔正文回退双读对账；P2/P6/P4/P5 不可裁剪等规则与 phases.yaml `prune_rules` 声明不一致 → WARNING | BDD-6/7 |
| M1-4 | `agate/scripts/check-gate.py` P2 分支（行 599-641 区域） | 接入对账：candidate_count/四字段 raw 正则读取 vs frontmatter 结构化读取（经 agate-md-field-get）对比；gate_commands 命令数/键集与 phases.yaml P2 `gates` 声明对账 | BDD-6/7 |
| M1-5 | 新增 pytest：对账模式夹具（含已知 YAML↔grep 差异的任务夹具） | 对账输出断言（stderr WARNING + 计数行 + 退出码保持 0/2） | BDD-6/7 |

**M2 — 切换权威源（对账清零后）**

| # | 落点 | 改动内容 | 关联 BDD |
|---|------|---------|---------|
| M2-1 | M1 的 3 脚本 + A 组字段读取链（check-gate.py 全脚本、ci-gate-backstop.py、agate-risk-score.py、check-routing.py、agate-feedback.py 等经 agate-md-field-get 的消费方） | 切换为读 YAML 权威源优先（任务 frontmatter 已是结构化，协议规则从 rules/*.yaml 读）；已迁移解析点的 md 正则删除 | BDD-8/9 |
| M2-2 | `agate/scripts/agate-md-field-get.py` | 协议规则类字段读取改读 rules/*.yaml（保留任务数据读取，两类字段在文档头注释区分） | BDD-8/9 |
| M2-3 | `agate/scripts/check-structure-consistency.py` | 提升为阻断：`--strict-errors-only` 语义常开（S-1/S-2 漂移即 exit 1） | BDD-10 |
| M2-4 | `agate/scripts/pre-commit-gate.py`（流水线 2j 区域，行 399 附近的 check-pruning 并列位） | 追加 `check-structure-consistency.py` 调用（与 check-gate 并列的独立 step，不短路） | BDD-10 |
| M2-5 | `.github/workflows/protocol-tests.yml` consistency job（或独立 structure job） | 追加 `python3 agate/scripts/check-structure-consistency.py` 步骤 | BDD-10 |
| M2-6 | 既有 pytest fixture（825 基线） | 对账模式桥接验证通过后：fixture 同步提供 YAML 构造（create_task_dir 增补 frontmatter YAML 任务形态），不删除既有 md 形态 fixture | BDD-11 |
| M2-7 | `UPGRADING.md` v0.57 章节（M2 小节） | 破坏性变更逐条列：脚本从 grep md 切 YAML 读、一致性 gate 提升阻断 | H3/BDD-11 |

**M3 — 卡片渲染化**

| # | 落点 | 改动内容 | 关联 BDD |
|---|------|---------|---------|
| M3-1 | `agate/scripts/agate-inject-card.py`（114 行，全文） | 内嵌渲染函数 `render_card(card_template, phase, yaml_data)`：门槛/产出/派发三节由模板占位符 + phases.yaml 数据渲染；叙事节保持模板静态文本；渲染产物字节稳定（供 agate-next-card sha256 校验） | BDD-12/13 |
| M3-2 | `agate/scripts/agate-next-card.py` | 输出卡片改为经渲染器生成（`_PHASE_CARDS` 映射保留）；渲染用 AGATE_ROOT 解析到的 YAML（稳定版隔离见 §3.6） | BDD-12/13 |
| M3-3 | `agate/phase-cards/P*-*.md`（9 张）门槛/产出/派发节 | 改为渲染产物（render 每次覆盖该三节；叙事节首次进入/常见错误/下游影响等保持手写 md） | BDD-12 |
| M3-4 | `agate/assets/templates/card-template.md`（新增）或代码内模板字符串 | 卡片骨架模板（占位符语法 `{{phases.P2.outputs}}` 等；选代码内模板，理由见 §3.6） | BDD-12 |
| M3-5 | 新增 pytest：渲染一致性测试 | 渲染产物 vs phases.yaml 声明一致；人为篡改 YAML 一个字段 → check-structure-consistency S-3 非 0；稳定版隔离测试（worktree 未发布 YAML 不污染 ~/.agate 注入，用 AGATE_ROOT 环境变量构造隔离） | BDD-12/13/14 |

### 1.2 不改什么（Not Modify）

> 显式列出"看起来该改但决定不改"的范围。P4 implementer 以此为范围边界，禁止顺手改进。

| # | 范围 | 不改的理由 |
|---|------|-----------|
| N-1 | `agate/scripts/check-protocol-consistency.py` 本体（1163 行） | D1 已定：S-1~S-6 独立脚本独立编号，不并入 CHECKS。M0「只加不改」+ 每阶段可回退是硬约束；动它 = 每 commit 自举风险。**已实证其扫描面为 `rglob("*.md")`（行 120 / 行 830），新增 `rules/*.yaml` 不在其扫描面，无新误报**，故 0 改动需求（P1 H5 疑虑解除） |
| N-2 | `agate/rules/review-mapping.md`、`agate/rules/state-transitions.md`（既有 md 提取物） | 不迁移、不删除、不合并进 YAML。YAML 与其并存：YAML 是**本任务三文件的权威源**，既有 md 是 TAG0016 文档层收敛产物；内容若重叠（如 C8 映射表），S-2 只以 WORKFLOW 总览表为 md 侧锚点，不将既有 rules md 纳入 S-1/S-2 对账面（防双源同步爆炸） |
| N-3 | `agate/phase-cards/*.md` 的叙事节（首次进入/重试/常见错误/下游影响） | design §2 关键决策 + P1 扫描 2 判定：YAML 只承载可判定规则，叙事压缩进 YAML 丢失可读性 |
| N-4 | `agate/scripts/*.sh`（3 个 hook 薄壳 + resolve-entry.py） | 工具稳定优先：hook 指向 ~/.agate 稳定版，不指向 worktree；薄壳不承担新逻辑 |
| N-5 | `agate/state-machine.md` / `agate/dispatch-protocol.md` / `agate/role-system.md` 正文规则段落 | 数据面进 YAML，正文保留为叙事层；正文逐段改写 = 双源同步爆炸（R1），S-1/S-2 只锚 WORKFLOW 总览表（P1 范围声明 §5 已定） |
| N-6 | `agate/tests/fixtures/` 既有 825 基线 fixture 内容 | 不删除不改写；M1 对账桥接，M2 增补 YAML 构造（M2-6） |
| N-7 | `agate/scripts/check-state-yaml.py` / git/commit 解析类（P1 扫描 1 F 组） | 解析的是任务/状态数据而非协议规则，不是"agent 读 8000+ 行 md"的摩擦源（P1 §4.1 F 组判定） |
| N-8 | `CHANGELOG.md` / version 文件 / tag | P8 发布期处理，M0-M3 不动 |
| N-9 | `agate/rules/*.yaml` 的**数据边界不扩展**到 P1 标记协议 / P6 行格式（P1 扫描 1 C/D 组"本次处理（M2 二期/三期）"项） | 本任务 P1 基线已把它们列为 M2 二期/三期可选，**不在 BDD-1..16 验收面**；C2 候选（§2.2）含扩展方案作对照，选定 C1 将其排除出本任务范围，防止范围蔓延（YAGNI；若后续需要，另行立项） |

### 1.3 风险在哪（Risk）

> 每条风险配缓解；跨模块引用/双源同步/schema 变更/并发资源竞争为高频项。本任务无并发/资源竞争（纯脚本），跨模块引用与双源同步为主风险。

| # | 风险 | 缓解 |
|---|------|------|
| R1 | 双源漂移（md ↔ YAML）：同一规则两处表述，改一处漏一处 | S-1/S-2 双向 gate 阻断（M0 起手动跑，M2 起进 pre-commit+CI，BDD-10）；M3 渲染化后卡片三节单源（S-3 强制） |
| R2 | 对账模式静默失效：M1 告警无出口，差异看不见 → "对账稳定"无法判定 | BDD-6 固定可观测出口：stderr `RECONCILE WARNING` + 汇总计数行，可重定向进日志；对账覆盖率由 BDD-7 判定（≥3 脚本 + 三类解析点） |
| R3 | M2 切换破坏既有 fixture（825 基线为 md 文本夹具） | M1 对账桥接 → BDD-8「差异数为 0 才切换」硬门槛；M2-6 独立增补 YAML 构造，不改既有 fixture 内容 |
| R4 | 工具链自举：新 gate 判自己 / worktree 未发布 YAML 污染稳定版注入（TAG0016 教训） | 双工作区纪律全程生效；BDD-13 稳定版隔离测试（AGATE_ROOT 指向稳定版，构造 worktree 未发布 YAML 差异，断言注入不被污染）；编排/派发类工具一律 ~/.agate 稳定版 |
| R5 | schema 自身漂移：schema 文件与 YAML 实际字段失配，校验形同虚设 | S-5 常开（check-yaml-schema 每次跑）；check-yaml-schema.py 对 schema 文件自身做结构健全性检查（required/enum/properties 可提取 + 字段集与对应 YAML 顶层键对齐） |
| R6 | S-3 渲染化破坏 agate-next-card 的 sha256 校验（卡片字节稳定契约） | 渲染器输出字节稳定测试；渲染只覆盖门槛/产出/派发三节，其余叙事节静态文本不动，模板字符串固定 |
| R7 | YAML 内跨模块引用失效（角色文件/模板/脚本路径） | S-6 引用完整性（M0 起），引用路径统一用 `{agate_root}` 相对协议根，与 CHECK 2 的 `agate/…` 引文风格一致 |
| R8 | count-tests 用例数漂移（仓库硬约定） | BDD-15 每里程碑血糖（立项基线 749，单调不减） |
| R9 | 新脚本/测试引入平台假设（裸 python3 / /tmp / PATH= / `-L` 软链） | BDD-16 + check-platform-assumptions.py 扫描（gate_commands.P5_platform）+ 测试按平台分支断言 |
| R10 | 对账判定语义分歧：YAML 归一化值与 md 原文不一致（list 连接/换行/引号） | 对账归一化规则表作为 P3 测试设计输入（frontmatter list 空格连接 vs 正文内联/块式；P6 换行连接字段不回退——沿用 agate-md-field-get 既有 BOOL/LIST 归一化口径），先写对账测试断言再实现（TDD） |

---

## 2. 候选方案（candidate_count: 3）

> 方案空间轴：A = YAML 数据边界（最小面 vs 扩展面）；B = S 检查脚本形态（单脚本内聚 vs 拆分专职组）；C = 对账放置（枢纽层 vs 消费点）；D = 渲染器位置（注入器内嵌 vs 独立渲染脚本）。三个候选按整体形态打包，各自在某轴上优于其他。

### 2.1 候选 C1（推荐）：内聚最小面

三 YAML（phases/dispatch/roles）+ 三 schema + 2 新脚本（`check-structure-consistency.py` 单脚本承载 S-1~S-6 六条子检查，仿 check-protocol-consistency 的 rep 编号风格；`check-yaml-schema.py` 手写 draft-07 子集校验器）。数据边界 = P1 扫描 2 判定的 5 类可判定规则（前置条件/产出/派发角色/gate 规则/retry 上限）+ 机械映射表（roles.yaml）。对账（M1）在 agate-md-field-get 枢纽层 + 三消费点接入（hub 为主）；渲染（M3）在 agate-inject-card.py 内嵌 render()。

**优点**：M0 承载面最小（2 新脚本 + 6 新数据文件，全部纯增量）；S 编号自校验单脚本内最简单（P1 扫描 3 回归拦截）；对账 hub 在 md-field-get 一处实现，D3 三脚本消费链收益最大；回退粒度 = 单脚本/单 YAML，任何一步可独立 revert。
**风险**：check-structure-consistency.py 单脚本 6 条检查（行数 ~600+）偏大，但与 check-protocol-consistency.py（1163 行）规模对齐，属仓库既有形态；渲染内嵌使 inject-card 从 114 行膨胀（预计 ~250 行），但保持单一注入入口。
**工作量**：M0 中 / M1 中 / M2 中 / M3 中。

### 2.2 候选 C2（对照）：拆分专职脚本组 + 扩展 YAML 面

S 检查拆 3 脚本（`check-structure-consistency.py` 只管 S-1/S-2 双向；`check-card-consistency.py` 管 S-3；`check-script-consistency.py` 管 S-4；S-5/S-6 并入通用校验）；YAML 面扩到含 P1 标记协议（`[SCOPE+]`/`[BLOCKER]` 等）与 P6 行格式（P1 扫描 1 C/D 组）；对账在每个消费脚本内部双跑（无 hub）；M3 新增独立渲染脚本 `agate-render-card.py`，注入器只读渲染产物。

**优点**：脚本职责单一、可单测隔离（每个 S 检查独立文件）；对账无死角（消费点级双跑，不经 hub）；渲染器独立可离线单测；扩展 YAML 面一次到位。
**风险**：M0 新增脚本 4-5 个（承载面翻倍，违反「只加不改」的增量最小化精神）；S 编号自校验跨脚本（需额外登记表脚本）；对账无 hub 导致 3 脚本各自实现对账逻辑（3 份重复代码，恰是本任务要消灭的漂移形态）；回退单元变大（拆分脚本组 = 一个里程碑 revert 牵扯多文件）；P1 标记/P6 行格式不在 BDD-1..16 验收面（扩展 = 范围蔓延，违反 YAGNI）。
**工作量**：M0 高 / M1 中高 / M2 高 / M3 中。

### 2.3 候选 C3（陪衬：P1 决策 D1 否决项验证）

S-1~S-6 并入 `check-protocol-consistency.py`（单一一致性入口，无新增脚本）。

**优点**：单一一致性 gate 入口、主 Agent 每阶段只跑一个脚本、无新脚本维护面；CHECK 与 S 编号同文档清单可核对。
**风险**：违反 M0「只加不改」硬约束（改 1163 行既有一致性脚本 = 每次 commit 工具链自举风险面扩大）；两条扫描面耦合（md 文档一致性与 YAML↔md 语义一致性生命周期不同步）；回退需 revert 整个一致性脚本；与 BDD-2/5/10 的"结构一致性独立判定"语义冲突（check-gate/CI 需识别新旧两组检查的独立 exit）。
**选择**：**不采纳**。这是 P1 决策 D1 的否决理由固化——D1 已定独立脚本独立编号，C3 在此暴露的正是 D1 要规避的风险（M0 只加不改 + 可回退 + 编号空间隔离）。保留作候选是为了让评审可见"并入"路径曾被完整考量，非凑数。

### 2.4 权衡表与选择理由

| 维度 | C1（推荐） | C2（对照） | C3（D1 否决项） |
|------|-----------|-----------|----------------|
| M0 增量面（硬约束：只加不改） | **最小**（2 新脚本 + 6 数据文件） | 大（4-5 新脚本） | **违反**（改既有一致性脚本） |
| 回退粒度（硬约束：每阶段独立可回退） | **单文件级** | 多文件捆绑 | revert 整个脚本 |
| S 编号自校验复杂度 | **低**（单脚本内 CHECKS 列表） | 高（跨脚本登记表） | 中（并入既有清单） |
| 对账实现一致性 | **好**（hub 一处 + 消费点薄接入） | 差（3 处重复实现） | 不适用 |
| 单测隔离 | 中（6 条检查同文件） | 好（每检查独立文件） | 差 |
| YAML 面覆盖（BDD-7 判定面） | 满足（3 类解析点） | 超量（含非验收面字段） | — |
| 主 Agent 每阶段 gate 数 | 2 个新脚本（structure + schema，P5 gate 分 key 跑） | 4-5 个 | 1 个（并入） |
| P1 决策契合度 | 全契合 | 部分（D1 外延扩大） | 违反 D1 |

**选择理由**：选 C1。决定性依据三条——(1) HANDOFF 硬约束「M0-M3 每阶段独立可回退（纯增量起步）」直接排除 C3（违反只加不改）并压低 C2（承载面翻倍导致回退单元变大）；(2) 本任务核心动机是消灭"同一规则多处实现/解析"的漂移（P1 扫描 1 B 组 5 处正则实证），C1 的对账 hub（md-field-get 一处）+ 薄消费点接入恰好不重演该反模式，而 C2 在消费点级对账等于再造 3 份重复逻辑；(3) C1 与 P1 已定决策（D1/D2/D3）与 BDD 验收面（16 条，扩展面字段不在其中）完全对齐，C2 的扩展面超出 BDD 验收范围，属 YAGNI 违反。C2 的单测隔离优势通过 C1 内"6 条检查按 rep 编号函数级分离 + 每检查独立 pytest"保留大部分（函数级隔离，非文件级）。

---

## 3. 选定方案设计（C1 展开）

### 3.1 YAML 权威源数据边界（改什么进 YAML、什么留 md）

**数据边界总原则（P0-brief 约束 + design §2 关键决策）**：YAML 只承载**可判定规则**（机器校验、无歧义、可枚举）；**叙事层**（why/示例/注意事项/常见错误）一律留 md。本任务三文件边界：

| 文件 | 承载（进 YAML） | 不承载（留 md 叙事层） |
|------|----------------|----------------------|
| `phases.yaml` | 每阶段：`id/name/exec_role/review_roles/outputs(required+status_field)/gates(判定口径可结构化子集)/retry_cap/prune_rules/卡片特有机器字段声明（P1 schema 键集、P2 candidate_count 等）` | 阶段叙事（该阶段为什么存在/注意事项）；检定的散文式说明（如 P2 权衡 nudge 的"或含选择+理由组合"回退口径 → gates 里只放主判据 + 注释指向 md 卡片） |
| `dispatch.yaml` | 派发三铁律（结构化 rule 串）、模板字段清单（目标/约束/上游关联/输入文件）、五模式编排枚举（single/parallel/pipeline/understand-then-split/hybrid ← P1 注：与 dispatch-protocol 用语一致化，P4 对齐既有文档词表）、gate 表（阶段→脚本+exit 语义）、`gate_commands` 语法声明（合法 key 规则：`P{N}`/`{key}_formatter`/`{key}_timeout_seconds`/`project_module`，判定复用 `agate_common.is_gate_meta_key`） | 派发 prompt 模板正文（保留 assets/templates/dispatch-prompt.md 为叙事渲染骨架，YAML 只声明 context_fields） |
| `roles.yaml` | 执行角色（id/phase/file）、评审角色（id/insert_after/mandatory_for/status_mapping）、C8 机械映射表（domain/risk_level→角色数据化，与 review-mapping.md 表同源） | 角色职责散文（assets/execution-roles/*.md / review-roles/*.md 全文不动） |

**明确不进 YAML 的规则**（P1 扫描 2「本次不处理」落实）：卡片常见错误/下游影响/首次进入/重试说明（叙事）；卡片内嵌 frontmatter 样例块（属模板示例）；P1 标记协议与 P6 行格式（见 §1.2 N-9，本任务范围外）。

**与既有 rules/*.md 的关系**：不合并、不复制；三 YAML 与 review-mapping.md/state-transitions.md 并存于 `agate/rules/`（缓存 S-6 引用完整性 / CHECK 扫描面均只扫 md，已实证无冲突）。roles.yaml 的 C8 映射表与 review-mapping.md 同源——S-4 登记表把"roles.yaml 的映射表"与"review-mapping.md"登记为一致性对（M2 起校验），防两处漂移。

### 3.2 schema 设计（draft-07 子集 + 校验机制）

- **schema 文件**：`agate/rules/schema/{phases,dispatch,roles}.schema.json`，声明 `"$schema": "http://json-schema.org/draft-07/schema#"`，**仅使用手写校验器支持的子集**：`type / required / enum / properties / items / additionalProperties(false 于对象层) / minItems`。数值刻度的 `minimum/exclusiveMinimum` 不用（retry_cap 等正整数约束用 type+enum 或 P4 校验器内附加断言，防子集实现膨胀）。
- **check-yaml-schema.py（手写校验，不依赖 jsonschema 包）**：参照 agate-frontmatter-check.py 的 SCHEMAS 机制（required/enums/types/min_values 手写遍历）。校验流：`yaml.safe_load` 每个 rules/*.yaml → 按文件名加载对应 schema JSON（`json.load`）→ 遍历 type/required/enum/properties/items 断言 → ERROR 输出 `SCHEMA-<file>: <path> <msg>`（仿 rep 风格）→ 任一失败 exit 1，全过 exit 0。对 schema 文件自身先做健全性自检（R5）。
- **示例**（phases 层，最小验证已实测可解析，见 §4 minimal_validation）：
  ```yaml
  schema_version: 1
  phases:
    - id: P2
      name: 方案设计层
      exec_role: architect
      review_roles:
        - { role: plan-eng-review, trigger: "risk_level == high" }
      outputs:
        - { file: P2-design.md, required: true }
        - { file: P2-review.md, required: true, status_field: status }
      gates:
        - { check: "P2-review.md status == approved" }
        - { check: "P2-design.md has 4 of [packages,domains,ui_affected,gate_commands]" }
      retry_cap: 3
      prune_rules:
        - { condition: "design_trivial or follows_existing_pattern", allow: "simplify, not omit" }
  ```
- **枚举约束**：`exec_role` ∈ {analyst, architect, test-designer, implementer, verifier, consistency-reviewer, judge, releaser}；`phase id` ∈ {P0,P1,P2,P3,P4,P5,P6,P6.5,P7,P8}；`retry_cap` ∈ {2,3}（P1 扫描 2：P1=3/P2=3/P3=2/P4=3/P5=2/P6=2/P7=2/P8=2）；`mode` ∈ {single, parallel, pipeline, understand-then-split, hybrid}（dispatch-protocol 词表，P4 对齐）。

### 3.3 S-1~S-6 判定口径与触发点

**判定口径**（check-structure-consistency.py 内 6 个 CHECK 函数，rep 编号 S-1..S-6）：

| CHECK | 方向 | 判定口径（可机器校验） | M0 起手动可用 | 触发点（按里程碑） |
|-------|------|----------------------|:---:|-------------------|
| S-1 | YAML→md | phases.yaml 每个 phase（id/name/exec_role）在 WORKFLOW.md 阶段总览表有对应行且 3 字段一致（表行解析：`\| P{N} \| 名称 \| 角色 \| …`） | ✅ | M0-M1：P5 gate + 手动；M2 起：pre-commit + CI（BDD-10） |
| S-2 | md→YAML | WORKFLOW 表每行 phase id 在 phases.yaml 有定义（防文档新增阶段忘入 YAML） | ✅ | 同上 |
| S-3 | YAML→cards | M0-M1：抽检 P2 卡门槛/产出/派发节文本 vs phases.yaml P2 声明（BDD-5 三方一致，P2-design.md + 卡片 + check-gate 判定）；M3 起：渲染产物 vs phases.yaml 声明逐字段比对（BDD-12），人为篡改 YAML → 非 0 | M0 抽检 P2 试点 | M3 渲染后全卡 |
| S-4 | YAML→scripts | 脚本字段读取登记表（读哪个 rules 字段的脚本清单，进 dispatch.yaml `field_readers` 声明）vs phases.yaml 字段集一致；gate_commands 语法声明 vs is_gate_meta_key 判据一致 | M0 初版登记表 | M1 对账接入后逐步增强 |
| S-5 | schema | 全部 rules/*.yaml 过 check-yaml-schema.py（校验器 exit 0 且无 ERROR 输出） | ✅（BDD-1） | 每次跑 structure 时串联（独立进程调用，不内嵌） |
| S-6 | 引用完整性 | YAML 中 `file:`/`template:`/`script:` 引用路径在协议根下真实存在（与 CHECK 2/CHECK 10 的 `agate/…` 引文风格一致；已实证 CHECK 10 只扫 md，YAML 引用由 S-6 独家覆盖） | ✅（BDD-3） | 每次跑 structure 时 |

**失败语义**：任一 S 检查 ERROR → exit 1；`--strict-errors-only` 常开（TAG0017 遗产语义）；输出仿 rep（`S1-phases: ERROR <msg> <loc>` / `S1-phases: OK`），供 check-gate/CI 机器消费。

**触发点时间线**（BDD-10 要求的"三处阻断"）：
- **M0-M1**：仅 P5 gate（gate_commands.P5_structure 手动/主 Agent 跑）+ 开发者手动跑；**不接 pre-commit/CI**（M0 是初始填充，阶段早期若接 pre-commit 会对存量卡片产生误拦；M1 对账期只观测）
- **M2**：pre-commit-gate.py 追加独立 step（与 check-gate 并列，无短路）+ CI consistency job（或独立 job）追加步骤 → 人为制造漂移三处均非 0（BDD-10）
- **M3**：S-3 渲染化生效，同 M2 触发点

### 3.4 M1 对账模式（差异可观测出口）

- **机制**：字段级双跑——现行 grep/md 读取路径（保退出码语义：0/2 不变，BDD-6）+ 结构化读取路径（frontmatter YAML / rules/*.yaml 声明）→ `agate_common.reconcile_field(op, field, grep_val, structured_val)` 对比。
- **可观测出口（BDD-6）**：不一致 → stderr 输出
  ```
  RECONCILE WARNING: <op> <field>: grep=<grep_val> structured=<structured_val>
  RECONCILE SUMMARY: N mismatches across M fields
  ```
  退出码 = 原 grep 路径判定（0/2 不变，**不新增阻断**）；stderr 重定向即日志，差异可被计数审计（H12 落实）。
- **对账归一化口径（R10 缓解）**：复用 agate-md-field-get 既有 BOOL/LIST 归一化（frontmatter list 空格连接 vs 正文内联 `[a, b]`/块式 `- a`；bool 归一化小写 true/false；P6/P7 换行连接字段无正文回退——沿用 NO_FALLBACK 语义）。归一化规则表随 P3 测试设计固化。
- **覆盖三类解析点（BDD-7）**：① gate_commands 块 = agate-read-gate-commands（M1-2）；② P1 裁剪字段 risk_level/phases = check-pruning（M1-3，经 md-field-get 双读 + phases.yaml prune 规则比对）；③ P2 四字段 = check-gate P2 分支（M1-4）。脚本数 = 3（+agate_common 工具函数，不计入覆盖数）。
- **接入开关**：`AGATE_RECONCILE` 环境变量（缺省 on，为 CI/批处理可设 off 降噪；BDD-6 夹具运行时不设即触发告警路径）。

### 3.5 M0-M3 里程碑落地清单与回退边界

| 里程碑 | commit 主题 | 落地文件（§1.1 对应行） | 验证（P5 gate key） | 回退边界 |
|--------|------------|----------------------|--------------------|---------|
| M0 | `wf(TAG0021-M0): rules/ 数据层 + S-1~S-6 + schema 校验（只加不改）` | M0-1..M0-11 | P5_consistency + P5_structure + P5_schema + P5_count + P5_platform + P5（全量 pytest） | revert 该 commit = 回到 0 新增文件状态，既有 53 脚本零依赖 YAML（BDD-4 保证） |
| M1 | `wf(TAG0021-M1): 三脚本对账模式（告警不阻断）` | M1-1..M1-5 | 同上 + 对账夹具测试 | revert 后对账逻辑消失，grep 路径原样（对账是叠加层） |
| M2 | `wf(TAG0021-M2): 切换权威源 + 一致性 gate 提升阻断` | M2-1..M2-7 | 同上（P5_consistency 含既有脚本基线） | **最重回退点**：revert 回 M1 形态需 BDD-8 对账清零门槛倒查；UPGRADING 破坏性变更节先列后改 |
| M3 | `wf(TAG0021-M3): 卡片渲染化 + 稳定版隔离` | M3-1..M3-5 | 同上 + 渲染一致性测试 | revert 后卡片三节回手写文本（渲染器是一次性生成器，产物 git 管理） |

每里程碑 commit 前跑 gate（BDD-4/11/14 每阶段血糖）：全量 pytest + count-tests ≥ 749 + consistency 0 ERROR + structure 0 漂移。

### 3.6 M3 渲染化设计

- **渲染器位置**：`agate-inject-card.py` 内嵌 `render_card()`（选代码内模板而非独立模板文件，理由：少 1 个文件、渲染器可单测、占位符语法只在渲染函数内约定一处；叙事节模板文本 = 卡片现有静态文本原样保留）。
- **渲染范围**：只渲染「前置条件 / 产出规格（产出文件清单）/ 派发（角色 + C8 评审）/ gate 规则 / retry 上限」节（= 可判定规则，与 phases.yaml 一致）；「首次进入 / 重试 / 常见错误 / 下游影响」节静态 md 不动（N-3 边界）。
- **字节稳定**（R6）：渲染器输出确定性（无时间戳/无路径注入），agate-next-card 的 sha256 校验契约保持（嵌入 dispatch-context 的卡片块可被 hash 校验）。
- **稳定版隔离（BDD-13）**：inject-card/next-card 渲染用 `resolve_agate_root` 解析到的 YAML（env AGATE_ROOT → 项目声明 → current → 脚本路径上溯）；worktree 模式下 `~/.agate/scripts/agate-inject-card.py` 读稳定版 YAML，worktree 未发布 rules/*.yaml 改动不影响稳定版注入。隔离测试用 AGATE_ROOT 环境变量构造两套 rules/ 差异断言互不污染。

### 3.7 实现完成标志（P3/P5 可判定标准）

以下为"做到什么程度算完成"的判定标准，P3 test-designer 据此写测试、P5 verifier 据此验证：

1. `agate/rules/*.yaml` + `schema/*.json` 存在且 check-yaml-schema.py exit 0（BDD-1）
2. check-structure-consistency.py 对 S-1/S-2 人为漂移 exit 1、无漂移 exit 0（BDD-2）；S-5/S-6 违规 exit 1（BDD-3）
3. M0 后全量 pytest 全绿 + count-tests ≥ 749 + consistency 0 ERROR（BDD-4）；S-3/S-4 初始一致（BDD-5）
4. M1 对账：3 脚本 stderr 出 WARNING + 计数、退出码 0/2 不变（BDD-6）；覆盖 3 类解析点、脚本数 ≥ 3（BDD-7）
5. M2 切换前对账差异数 = 0（BDD-8）；已迁移解析点静态扫命中 0（BDD-9）；pre-commit + CI + 脚本三处漂移阻断（BDD-10）；切换后回归全绿（BDD-11）
6. M3 渲染产物与 phases.yaml 一致、篡改 YAML → S-3 非 0（BDD-12）；注入与渲染一致 + 稳定版隔离（BDD-13）；渲染化回归全绿（BDD-14）
7. 全程 count-tests 单调不减（BDD-15）；新增脚本/测试过 check-platform-assumptions 扫描（BDD-16）

---

## 4. 四字段声明

### gate_commands（在 P2 固化，后续阶段不得修改；拆独立 key，不用 &&）

> `PY_CACHE_DISABLE` 一并在 env_constraints 说明。/tmp 与 ptmp 只读（实证），pytest 一律 `-p no:cacheprovider --basetemp=/home/kity/oclab/agate/.worktrees/agate-TAG0021/dist/`（已实证可写）。

```yaml
gate_commands:
  P3: "python3 -m pytest agate/tests/ -q --tb=no -p no:cacheprovider --basetemp=/home/kity/oclab/agate/.worktrees/agate-TAG0021/dist/"
  P5: "python3 -m pytest agate/tests/ -q --tb=no -p no:cacheprovider --basetemp=/home/kity/oclab/agate/.worktrees/agate-TAG0021/dist/"
  P5_consistency: "python3 agate/scripts/check-protocol-consistency.py --strict-errors-only"
  P5_structure: "python3 agate/scripts/check-structure-consistency.py"
  P5_schema: "python3 agate/scripts/check-yaml-schema.py"
  P5_count: "bash agate/tests/scripts/count-tests.sh"
  P5_platform: "python3 agate/scripts/check-platform-assumptions.py"
  P5_ruff: "ruff check agate/scripts/ agate/tests/"
  P5_timeout_seconds: 300
  P5_consistency_timeout_seconds: 120
  P5_structure_timeout_seconds: 120
  P5_schema_timeout_seconds: 120
  P5_count_timeout_seconds: 120
  P5_platform_timeout_seconds: 120
  P5_ruff_timeout_seconds: 120
```

### files_to_read（P4 implementer 参考清单，只列确实要参考的）

```yaml
files_to_read:
  - path: agate/scripts/check-protocol-consistency.py:70-130
    why: CHECK 1 代码块解析 + rglob("*.md") 扫描面 + rep 编号输出机制——check-structure-consistency.py 的 S 检查参照样本；确认 rules/*.yaml 不在其扫描面
  - path: agate/scripts/agate-frontmatter-check.py:27-160
    why: SCHEMAS 手写校验（required/enums/types/min_values）先例——check-yaml-schema.py 的实现参照
  - path: agate/scripts/agate-md-field-get.py:1-120
    why: frontmatter→正则回退双读机制——M1 对账 hub（reconcile 归一化口径来源）
  - path: agate/scripts/agate-read-gate-commands.py:1-50
    why: B 组 gate_commands 块正则（5 处同源实现的代表）——M1-2 对账消费点
  - path: agate/scripts/check-pruning.py:84-182
    why: A 组消费点（risk_level/phases 经 md-field-get 读取）——M1-3 对账接入点
  - path: agate/scripts/check-gate.py:590-700
    why: P2 分支 candidate_count/四字段 raw 正则读取——M1-4 对账接入点（本任务不改其余分支）
  - path: agate/scripts/agate-inject-card.py:1-114
    why: M3 渲染化改造对象（内嵌 render_card）
  - path: agate/scripts/agate-next-card.py:60-114
    why: _PHASE_CARDS 映射 + sha256 字节稳定契约——M3 渲染输出侧
  - path: agate/rules/state-transitions.md
    why: 既有 rules md（TAG0016 提取物）——命名空间/内容共存检查，S-2 锚点范围确定（不并入对账面）
  - path: agate/rules/review-mapping.md:1-40
    why: C8 机械映射表既有表述——roles.yaml 同源数据源 + S-4 一致性登记
  - path: agate/WORKFLOW.md:285-300
    why: 阶段总览表——S-1/S-2 md 侧锚点 + phases.yaml 数据来源（P0-P8 + 评审角色列）
  - path: agate/scripts/agate_common.py:79-110
    why: is_gate_meta_key / resolve_agate_root——新脚本公共依赖点
  - path: agate/tests/unit/test_check_pruning.py
    why: 既有消费脚本测试形态——对账/切换测试参照
```

### env_constraints

```yaml
env_constraints:
  # 继承 P0-brief + P1 P0_STALE 修正（P0-brief 声称 danger-full-access，实际为 workspace-write 沙箱）
  sandbox: "workspace-write；/tmp 与 ptmp 只读（实证 Errno30）——任何 pytest 需 -p no:cacheprovider --basetemp=<可写目录>；可写目录 = worktree 下 dist/（已实证可写）"
  interpreter: "/usr/bin/python3；依赖 pyyaml（已装）；无 jsonschema 包依赖（check-yaml-schema.py 手写子集校验，与依赖清单 pyyaml+Pillow 一致；本机 jsonschema 虽可用，不引入为新依赖）"
  dual_workspace: "读卡片/跑 gate 用 ~/.agate 稳定版；check-protocol-consistency 与 check-structure-consistency 用 worktree 自己的（检查 worktree 协议文件）；编排/派发类工具一律 ~/.agate/scripts/ 稳定版"
  bash_discipline: "所有 bash 命令外层 timeout（30-90s）；单步串行；读文件用 read/grep/glob 工具不占 bash 通道"
  platform_neutral: "BDD-16：新增脚本/测试不得引入裸 python3 / 硬编码 PATH= / -L 软链假设 / /tmp 路径；平台差异场景按分支断言或模拟覆盖（check-platform-assumptions.py 扫描兜底）"
  # 注意：env_constraints 为声明性字段，真正被执行的是 gate_commands（上节），本字段只做信息注入
```

### minimal_validation

```yaml
minimal_validation:
  class: "纯代码逻辑，无外部系统依赖"
  rationale: "本任务为 YAML + JSON Schema + Python 检查脚本的文档/代码逻辑，无浏览器/外部服务/网络交互，不依赖外部系统行为。依赖的内部函数与数据转换链：yaml.safe_load（pyyaml 解析 YAML，pyyaml 已在依赖清单）、json.load（schema 文件解析）、agate_common.is_gate_meta_key（gate_commands 键判定，M1-2 对账复用）、agate-md-field-get 的 frontmatter→正则回退双读机制（对账归一化口径来源）、check-protocol-consistency 的 rep 编号输出机制（S 检查输出参照，仅借鉴形态不依赖其运行）、agate-frontmatter-check 的 SCHEMAS 手写校验模式（check-yaml-schema.py 参照实现）"
  method: "/usr/bin/python3 内联脚本实测：① yaml.safe_load 解析 phases.yaml 草案片段（含 P6.5 独立阶段 id、review_roles/outputs/prune_rules 列表、retry_cap int）→ 解析成功且字段断言全过；② schema draft-07 子集结构 json 序列化往返一致、required/enum 可被手写校验器提取；③ 非法 YAML（scanner error）被 safe_load 拒绝；④ 缺 required 键（name/exec_role）可被 required 检查捕获；⑤ jsonschema 包本机可用但不引入为新依赖（依赖清单仅 pyyaml+Pillow）；⑥ basetemp 可写性：worktree dist/ 可写、ptmp 不可写（Errno30 证实）"
  result: "confirmed"
  note: "6 项最小验证全部通过（MINIMAL_VALIDATION_PASS）。关键假设确认：YAML 草案结构可被 pyyaml 解析、schema 子集可机器校验、非法/缺键可被拒绝、basetemp 路径选定 dist/。无外部系统依赖，无需进一步验证。"
```

---

## 5. dispatch_plan（批次设计，TAG0014）

**批次表**（frontmatter 已声明 `{mode: serial, batches: [M0, M1, M2, M3]}`）：

| batch | 内容（§1.1 落点组） | complexity | 串行理由 |
|-------|--------------------|:---:|---------|
| M0 | M0-1..M0-11（数据层 + S 检查 + schema 校验，只加不改） | high | 其余三批全部依赖它（YAML 权威源是先决） |
| M1 | M1-1..M1-5（三脚本对账） | high | 依赖 M0 的 phases/dispatch YAML；与 M3 无文件重叠，但 BDD-8 门槛要求对账清零后才进 M2，M1 与 M2 必须严格串行 |
| M2 | M2-1..M2-7（切权威源 + 提升阻断 + fixture/UPGRADING） | high | 依赖 M1 对账清零（BDD-8）；改动面最大且含破坏性变更（UPGRADING 章节先列） |
| M3 | M3-1..M3-5（卡片渲染化 + 稳定版隔离） | medium | 依赖 M0（渲染数据源）；与 M1/M2 文件不重叠，但为控制并发复杂度和保持每里程碑独立可回退，声明串行执行（不做并行加速——BDD-14 渲染化回归要求结构一致性 0 漂移，串行便于逐批验证） |

**批次边界对齐影响面梳理**：M1 与 M2 均改 check-gate.py / check-pruning.py / agate-read-gate-commands.py（M1 加对账、M2 切权威源），属**同文件跨批两轮改造**——按「同一文件不跨批次被改两轮」原则，M1/M2 之间插入 BDD-8 对账清零门槛作为天然边界（该门槛在代码上表现为 M1 提交后对账差异数检查，M2 仅在清零后启程）；若主 Agent 选择 M1+M2 合并为单批实现，须在 P3/P4 派发时显式声明，且不破坏 BDD-8 的二值判定。M3 与 M1/M2 零文件重叠（inject-card/next-card/cards/templates vs md-field-get/pruning/check-gate/read-gate-commands）。

**[SCOPE+] 发现（供主 Agent 关注，不擅自扩大范围）**：
- SCOPE+1：`agate/rules/{phases,dispatch,roles}.yaml` 与既有 `agate/rules/*.md`（review-mapping.md/state-transitions.md）并存的命名空间与 S-2 锚点范围需显式声明（§1.2 N-2 已处理为"不对账既有 rules md"）——建议 P1 基线无需变更，本方案已覆盖。
- SCOPE+2：M1 对账的"经 agate-md-field-get 的 A 组消费方"（ci-gate-backstop/agate-risk-score/check-routing/agate-feedback）在 M2 切换时随 md-field-get 一起生效，不单独立 BDD——属 BDD-9 静态零命中的覆盖范围，P4 实现时以 BDD-9 判据为准。
- SCOPE+3：HANDOFF §4 的 `--basetemp=/home/kity/oclab/dsh-workspace/ptmp` 已失效（实证 ptmp 只读），权威 basetemp 以本 design 的 dist/ 为准——建议主 Agent 在后续 P3-P8 dispatch-context 的客观查证中引用本 design 的 gate_commands。

---

## 6. 与 P1 决策的对齐复核（自检）

| P1 决策 | 本方案落实 |
|---------|-----------|
| D1（S-1~S-6 独立脚本 + 独立编号，不并入 check-protocol-consistency） | §3.3：check-structure-consistency.py 独立承载；§1.2 N-1 不改 consistency 本体；C3 候选固化否决理由 |
| D2（BDD 连续数字编号） | 本文件不新增/不改 BDD；§3.7 完成标准逐条引用 BDD-1..16 数字编号 |
| D3（M1 首批三脚本） | §3.4 覆盖 agate-read-gate-commands / check-pruning / check-gate 三类解析点（BDD-7 判据） |