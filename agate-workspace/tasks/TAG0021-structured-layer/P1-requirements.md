---
phase: P1
task_id: TAG0021-structured-layer
type: problems
parent: P0-brief.md
trace_id: TAG0021-P1-20260822
status: draft
created: 2026-08-22
agent: analyst
# ── v2.0 机器字段 ──
risk_level: high              # 改动面极大（协议本体 md + 全部 gate 脚本 + 卡片渲染 + 新目录）+ 工具链自举风险
ceremony: standard            # 缺省档位，fail-closed
phases: [P1, P2, P3, P4, P5, P6, P7, P8]   # 全保留，不裁剪（理由见「裁剪说明」）
packages: [agate]             # agate 协议本体为单一版本单元；四改动面（docs/scripts/cards/rules）见正文 §5
domains: [backend]            # 纯协议/脚本/数据层改造，无 frontend、无 security 域
---

# P1 需求基线 — TAG0021 协议结构化层（RM-AG0022）

> 状态标记：[PROD_NOT_TOUCHED]（仅读稳定版 `~/.agate` 角色/卡片文件与主 checkout 协议文件，写操作全部落在 worktree `agate-workspace/` 内）

## 1. 需求复述

**任务一句话**：把 agent 消费的协议规则从 8000+ 行自由文本 markdown 抽成机器可读的 YAML 权威源（`agate/rules/{phases,dispatch,roles}.yaml` + `agate/rules/schema/*.json`），用 S-1~S-6 双向一致性 gate 防漂移，gate 脚本从「grep markdown」逐步迁移到「读 YAML」，phase-cards 从「手写」迁移到「YAML 渲染」。

**动机（P0-brief issues 锚定）**：

- 规则散落：同一规则（如 P2 门槛）在 WORKFLOW / dispatch-protocol / state-machine / phase-cards 多处表述，agent 交叉阅读拼全貌——文本层收敛（TAG0016）已做但仍是自由文本。
- 解析靠 grep：gate 脚本大量用正则解析 markdown 字段，脆弱易漂移（DEBT0010：`_timeout_seconds` 键解析遗漏致 P2/P3/P5 误判是真实教训）。
- agent 上下文开销：orchestrator 每轮「读状态 → 查卡片 → 查规则」跨文档查表成本高；RM-AG0031 写时校验、RM-AG0036 双语锚点均依赖本条目落地。

**达成形态（design-structured-layer.md 锚定）**：YAML 承载**可判定规则**（门槛命令、产出文件、状态转移、重试上限、角色映射）；markdown 保留为**人类叙事层**（why/示例/注意事项）；S-1~S-6 双向 gate 阻断漂移；M0-M3 渐进迁移、每阶段独立可回退。

## 2. P0-brief 时效性质疑

**结论：轻微漂移 1 处，记录不阻塞（不命中严重判据 1-3）。**

逐条对照 P0 卡「时效性自检」判据：

1. `task` 目标方案是否仍成立 → **成立**。design-structured-layer.md §2/§4/§5（YAML 权威源 + S-1~S-6 + M0-M3）与 P0-brief 完全一致；改造对象 worktree 已合并 TAG0019（ceremony/check-routing）与 TAG0020（judge/check-events/check-judge-verdict），与设计文档 §6「独立 judge 与结构化层正交」表述一致，不构成方案冲突。
2. `executor_env` 平台前提是否仍成立 → **成立**。opencode / `has_task_tool: true` / `has_local_runtime: true` / `network: full` / `git: true` 均成立。
3. `known_risks`「已解决前提」是否变化 → **无变化**。双工作区纪律（稳定版跑 gate、worktree 改）仍在生效；工具链自举风险仍在。

`[P0_STALE: P0-brief env_constraints.debug_env 声明"权限为 danger-full-access"，实际执行环境为 workspace-write 沙箱且 /tmp、ptmp 只读（dispatch-context 客观查证：pytest 须 `-p no:cacheprovider --basetemp=<可写目录>`）——轻微漂移，已记录，按"环境约束具体值"处理，不阻塞 P1；相关测试命令声明以 HANDOFF §4 与 dispatch-context 客观查证为准]`

## 3. 隐含需求识别

逐维度快速过（本任务无数据/前端/多端/边界/兼容的常规面，但协议面隐含依赖密集）：

| # | 隐含需求 | 为什么必须 |
|---|---------|-----------|
| H1 | `agate/rules/*.yaml` 必须同时配 JSON Schema + `check-yaml-schema.py` | 无 schema 的 YAML 与自由文本同病——没人校验就是没人判定；YAML 可信的前提是合法性可机器校验（design §3，转 BDD-1） |
| H2 | 新目录 `agate/rules/` + 2 个新脚本自动进入 SELF-GATE 触发面 | 改协议本体文件（`agate/**/*.md`、`agate/scripts/*.py`）的所有 commit 须含 `self-gate-review:` 或 `self-gate-skip:` 声明；HANDOFF §5 硬约束 |
| H3 | `UPGRADING.md` 新增章节 | M0 纯增量需说明不破坏存量项目；M2 切换权威源属脚本行为变化（破坏性变更逐条列）；AGENTS.md 版本发布清单第 3 条强制 |
| H4 | `README.md` / `AGENTS.md` 目录结构图新增 `rules/` 一层 | 文档面一致性——`check-protocol-consistency` CHECK 2 会扫描协议文件引用，新路径/新引用必须真实存在 |
| H5 | `check-protocol-consistency` 扫描面（协议目录 rglob）会纳入 `rules/*.yaml` | CHECK 1（```yaml 代码块可解析）与 CHECK 2（引用存在性）需确认对新增 YAML 文件不误报；必要时调整豁免清单/NARRATIVE_DIRS（P8 卡已有对应检查项） |
| H6 | M3 卡片渲染化的双工作区自举纪律 | `agate-inject-card.py` 类编排/派发工具只能用 `~/.agate` 稳定版跑（TAG0016 教训）；worktree 里改渲染器不得让未发布 YAML 注入稳定版流程（转 BDD-13） |
| H7 | M2 删除 grep 逻辑的既有测试兼容 | 既有 pytest fixture（含 825 基线）构造的是 md 文本任务夹具；切 YAML 后需 fixture 同步构造 YAML 或由对账模式桥接，回归面大但必须全绿——TDD 先红后绿（转 BDD-11） |
| H8 | count-tests 基线冻结 | count-tests 用例数只增不减是仓库硬约定；TAG0021 立项时点用例数记为基线，M0-M3 每个里程碑血糖（转 BDD-15） |
| H9 | 测试平台无关延续 | 新脚本/测试不得引入裸 `python3` / `PATH=` / `/tmp` 等 Unix 假设（agate 测试核心约束）；pyyaml 已在依赖（转 BDD-16） |
| H10 | P6 验收口径按本任务形态声明 | 本任务 domains 不含 frontend，无 UI/视觉验收；P6 以脚本/数据证据验收（pytest / consistency / gate exit code），vision 能力声明不适用（见 §9 能力自查） |
| H11 | P1/P2/P6/P7 frontmatter schema 与字段读取链随 M2 迁移 | `agate-frontmatter-check.py` / `agate-md-field-get.py` 是字段读取链枢纽；迁移后者等于迁全部消费方（check-pruning/check-gate/check-p6-* 等）——M1 对账选脚本的依据见扫描 1 |
| H12 | 对账模式需要"差异可观测出口" | M1 告警不阻断的前提是差异能被看见并计数（stderr WARNING + 计数、可进日志），否则"对账稳定"无法被判定（转 BDD-6/7） |

## 4. 同类扫描结论（强制）

> 三组扫描对象按 dispatch-context 强制清单执行（扫描以 worktree `agate/` 为准，含 TAG0019/TAG0020 合并内容）。逐条判定写在本节正文，progress 里的原始记录仅作过程痕迹。

### 4.1 扫描 1：grep 脚本对 markdown 的解析点

**统计**：`agate/scripts/` 共 57 个 `.py`（含 `agate_common.py` / `resolve-entry.py` / `install-hook.py` 等基础设施）；其中 29 个含正则解析，约 25 个对 markdown 内容做字段/行级 grep 式解析（占 44%）。按解析对象分 6 组：

| 组 | 解析对象 | 脚本清单（命中） | 判定 |
|----|---------|----------------|------|
| A | 任务产出 frontmatter/正文字段（risk_level / phases / packages / domains / ui_affected / candidate_count / override / 跳过风险 / ui_render_shape 等） | `agate-md-field-get.py`（唯一统一读取器）+ 消费方：`check-pruning.py`、`check-gate.py`、`check-p6-evidence.py`、`check-p6-provenance.py`、`ci-gate-backstop.py`、`agate-risk-score.py`、`check-routing.py`、`agate-frontmatter-check.py`（frontmatter YAML 校验，已结构化）、`agate-feedback.py` | **本次处理（M1/M2）**：A 组是"agent 读规则"摩擦的直接受益面；`agate-md-field-get` 是统一入口，M1 对账首选（check-pruning 消费链最典型） |
| B | `gate_commands` 块（P2-design.md 正文） | 同源正则 `^gate_commands:[ \t]*\n((?:  .*\n|\s*\n)*)` 实现 4 处：`agate-read-gate-commands.py`、`agate-read-p5-commands.py`、`agate-gate-p5-count.py`、`agate-gate-missing-cmds.py`；另 `check-protocol-consistency.py` CHECK 4 有独立键抽取实现 | **本次处理（M1 首批）**：同一块语法 ≥5 处实现 = 漂移高危（DEBT0010 同族，扫描 3 佐证）；YAML 后收敛为单一读取 |
| C | P6/BDD 行格式（`- PASS\|FAIL BDD-N`、截图/vision/manual-review 引用） | `check-p6-evidence.py`、`check-p6-provenance.py`、`check-p6-format.py`、`agate-evidence-consistency.py`、`check-judge-verdict.py`、`check-gate.py`（P6 分支）、`agate-archive-stale-outputs.py` | **本次处理（M2 二期）**：P6 行格式本身是可结构化候选（入 schema）；随 check-gate P6 分支一起迁移，不单独立项 |
| D | P1/P7 行首标记（`[SCOPE+]` / `[BLOCKER]` / `[DEVIATION-CRITICAL]` / `[DESIGN_GAP]` / `NEED_CONFIRM` / `[SUGGEST:]`） | `check-pruning.py`（override/coupling_checklist/internal_only 正文行）、`check-routing.py`（coupling_checklist）、`check-scope-resolved.py` + `check-retrospective.py`（`[SCOPE+]`）、`check-gate.py`（P7 标记 + P1 待确认标记） | **本次处理（M2 三期）**：标记协议可进 `roles.yaml`/`dispatch.yaml` 的标记声明节或独立标记 schema；随迁 |
| E | 协议本体一致性（YAML 代码块 / 引用路径 / 行号 / 权威数值） | `check-protocol-consistency.py`（CHECK 1 代码块提取、CHECK 2 REF_RE、CHECK 3 LINEREF_RE、CHECK 4 gate_commands 键、CHECK 12 权威数值） | **本次处理（M0 边界内）**：仅需与 S-1~S-6 编号空间协调（决策 D1，见 §5）；其自身不迁到读 YAML（设计 §6 保持并存） |
| F | 非自由文本解析（.state.yaml / git 暂存区 / commit message / CHANGELOG 标题 / ```yaml 债务块） | `check-state-yaml.py`、`agate-state-yaml-check.py`、`pre-commit-gate.py`（路径正则 + diff `phase:` 行）、`commit-msg-self-gate.py`、`check-changelog.py`、`agate-changelog-unreleased.py`、`agate-debt-check.py` | **本次不处理**：`.state.yaml` 已是 YAML 结构化；git/commit/CHANGELOG 解析读的是任务/状态数据而非协议规则，不是"agent 读 8000+ 行 md"的摩擦源；CHANGELOG 结构化如需再做，另行立项 |

**回归拦截声明**：M0-M3 期间及之后，脚本新增"对协议规则 md 字段的正则解析"一律拦截——M2 起由 S-4（YAML→scripts 字段声明一致）+ 静态扫描（已迁移解析点在 `agate/scripts/` 零命中，见 BDD-9）兜底；任何新脚本想读协议规则必须先入 YAML 再读。

### 4.2 扫描 2：phase-cards 门槛/产出/派发字段清单

**统计**：`agate/phase-cards/` 共 9 张卡（P0-P8；目录内 `README.md` 非卡）。9 张卡结构高度一致：`首次进入 / 重试 / 前置条件 / 派发 / 产出规格 / gate 规则 / 推进条件 / 常见错误 / 下游影响`（P0 卡例外：`做什么 / P0-brief 四字段 / 同类预判 / 时效自检 / 环境自检 / 任务粒度 / 推进条件`）。

**字段清单（逐卡抽取，M0 phases.yaml 数据面 + M3 渲染数据源）**：

| 字段类 | 内容 | 命中卡 |
|--------|------|--------|
| 前置条件（checkbox 门槛） | 如 P1：`P0-brief.md 完成（四字段齐全）`；P8：`P1-P6 全部产出就绪` | P1-P8 |
| 派发角色 | P1 analyst + requirements-review；P2 architect + plan-eng-review（high）/ plan-design-review（frontend）/ plan-ceo-review（可选）；P3 test-designer；P4 implementer + C8 评审；P5 verifier；P6 verifier + vision-analyst（UI）+ judge（P6.5 强制）；P7 consistency-reviewer；P8 releaser | P1-P8 |
| 产出文件 | P0-brief.md / P1-requirements.md+P1-review.md / P2-design.md+P2-review.md（+P2-skeleton.md，bootstrap）/ P3-test-cases.md+测试代码 / P4-implementation.md+代码（+P4-review.md）/ P5-test-results/ / P6-acceptance.md+P6-evidence/（+P6.5-judge-verdict.md）/ P7-consistency.md / P8-release.md | P1-P8 |
| gate 规则 | check-gate.py Pn + 辅助（check-tdd-red / check-p6-evidence / check-p6-provenance / check-judge-verdict / check-events / check-pruning / check-routing / check-state-transition / check-scope-resolved / check-retrospective） | P1-P8 |
| retry 上限 | P1=3、P2=3、P3=2、P4=3、P5=2、P6=2、P7=2、P8=2（P6.5 走事件账本 ≤2，不占 `retries.P6.5`） | P1-P8 |
| 卡片特有机器字段 | P1：frontmatter schema 键集；P2：candidate_count / 四字段 / gate_commands 声明 / dispatch_plan；P6：pass/fail/ui_affected/regression_pass；P7：blocker_count 等 5 字段 | P1/P2/P6/P7 |

**逐条判定**：

- 前置条件 / 产出规格 / 派发 / gate 规则 / retry 上限 → **本次处理**：5 类是"可判定规则"，进 `phases.yaml`/`dispatch.yaml`/`roles.yaml` 数据面；M3 渲染化后由模板 + YAML 数据生成（S-3 强制一致）。
- 常见错误 / 下游影响 / 首次进入 / 重试说明 → **本次不处理（叙事层）**：留 md。理由：YAML 只承载可判定规则（P0 约束），叙事压缩进 YAML 丢失可读性（design §2 关键决策）。
- 卡片内嵌 frontmatter 样例块 → **本次不处理**：属模板/角色文件的示例，M3 渲染模板演进时再评估是否抽为模板变量。
- **回归拦截**：S-3（YAML→卡片）+ S-2（md→YAML）双向强制——未来新增卡片门槛/产出/派发字段必须先入 `phases.yaml`，遗漏即漂移 ERROR（转 BDD-12）。

### 4.3 扫描 3：check-protocol-consistency CHECK 编号空间

**统计**：当前活动编号 = **CHECK 1 / 2 / 3 / 4 / 6 / 7 / 8 / 9 / 10 / 11 / 12**（共 11 个）；**CHECK 5 已退役**（源文件注释：8 文件必读框架不再适用，Phase Card 取代）。编号形态：report id 形如 `CHECK1-yaml` / `CHECK4-gatekeys` / `CHECK10-scriptref`；统计键 = `"CHECK" + title.split()[1]`。

**逐条判定**：

- S-1~S-6 编号 → **本次处理**：design §4 已定义 S-1~S-6 独立编号前缀，与 CHECK 1-12 天然不冲突（决策 D1，见 §5）。
- CHECK 5 退役位 → **本次不处理**：不复活也不占用；S 前缀已规避编号冲突，无需动既有 CHECKS 列表（M0「只加不改」约束）。
- **回归拦截**：新增 CHECK/S 编号不得与既有 1-12 或 S-1~S-6 重复——S 编号由 check-structure-consistency.py 内 CHECKS 列表自校验，若未来并入 check-protocol-consistency 需过其文档头 CHECK 清单核对（对应 P0 卡/B2 的 CHECK 表自洽）。

## 5. 范围声明与关键决策

**范围（packages: [agate] 的四改动面）**：

| 改动面 | 路径 | 归属里程碑 |
|--------|------|-----------|
| 协议文档（人类叙事层，少量增补） | `agate/WORKFLOW.md`（阶段总览表增 S-1/S-2 锚点）等 | M0 |
| gate 脚本（解析点迁移） | `agate/scripts/*.py`（A-E 组） | M0-M2 |
| 卡片（渲染化） | `agate/phase-cards/*.md` + `agate-inject-card.py` | M0（数据面）/ M3（渲染） |
| 新增结构化层 | `agate/rules/{phases,dispatch,roles}.yaml` + `agate/rules/schema/*.json` + `check-structure-consistency.py` + `check-yaml-schema.py` | M0 |

**关键决策（本 P1 基线内定案，无需人工介入）**：

- **D1（编号空间）**：S-1~S-6 放在**独立脚本** `check-structure-consistency.py` + 独立 S 前缀编号空间，**不并入** `check-protocol-consistency` 的 CHECKS 列表（design §6「可考虑」留白项）。理由：M0「只加不改」+ 每阶段可回退是硬约束，并入即耦合两个脚本的扫描面与生命周期；合并评估推迟到 M2 一致性 gate 提升阻断时，若 CI job 与 pre-commit 触发点趋同再合并不迟。倾向项，主 Agent 无异议即采纳 `[SUGGEST: D1]`。
- **D2（BDD 编号）**：BDD 用**连续数字**（BDD-1..BDD-16）+ 标题后缀 `(M0)`/`(M1)`/`(M2)`/`(M3)` + `###` 组标题标注阶段归属（派发指引「或注释标注阶段归属」分支）。理由：`check-gate.py`（`BDD-[0-9]` 锚点）、`check-p6-provenance.py`（`^#### BDD-[0-9]` 计数）、`check-judge-verdict.py`（`^#### BDD-([0-9]+)` 提取）的机械正则只认数字编号——前缀式（如 BDD-M0-1）会让 P1 gate 锚点检查与 P6/P6.5 计数失效。`[SUGGEST: D2]`。
- **D3（M1 对账首批）**：`agate-read-gate-commands` / `check-pruning` / `check-gate` 三脚本（design §7 与 HANDOFF 已指定）。扫描 1 佐证：B 组 5 处重复正则（DEBT0010 同族）+ A 组消费链最广，收益最大。`[SUGGEST: D3]`。

## 6. BDD 验收条件

> 编号为连续数字 + 阶段后缀（决策 D2）。每条独立可二值判定（PASS/FAIL），无中间态；Given/When/Then 不绑定实现符号，全部以"运行命令后观察退出码/输出/文件"为客观判据。

### 6.1 M0 — 数据层就位（只加不改）

#### BDD-1: (M0) rules/ 结构化目录通过 schema 校验
- Given M0 提交完成，`agate/rules/{phases,dispatch,roles}.yaml` 与 `agate/rules/schema/*.json` 存在
- When 运行 `python3 agate/scripts/check-yaml-schema.py` 校验全部 YAML
- Then 全部 YAML 通过 JSON Schema 校验且退出码为 0；任一非法字段/错误枚举/错误类型 → 退出码非 0

#### BDD-2: (M0) S-1/S-2 双向一致（阶段总览 ↔ phases.yaml）
- Given M0 产物就绪（phases.yaml 与 WORKFLOW.md 阶段总览表共存）
- When 人为在 phases.yaml 增删一个阶段定义（或改动 WORKFLOW.md 总览表一行，另一侧不动）后运行 `check-structure-consistency.py`
- Then 以非 0 退出码报告 S-1 或 S-2 漂移；两侧无差异时退出码为 0

#### BDD-3: (M0) S-5/S-6 schema 与引用完整性
- Given rules/*.yaml 存在
- When YAML 引用不存在的角色文件/模板/脚本路径（S-6），或 YAML 违反 schema 枚举（S-5）
- Then `check-structure-consistency.py` 以非 0 退出码报告对应项；全部合法时退出码为 0

#### BDD-4: (M0) 存量行为不变（纯增量）
- Given M0 提交完成
- When 运行全量 pytest、`count-tests.sh`、`check-protocol-consistency.py --strict-errors-only`
- Then pytest 全绿；count-tests 用例总数 ≥ 立项基线；consistency 0 ERROR（既有脚本仍走 grep md，行为不变）

#### BDD-5: (M0) S-3/S-4 初始一致（卡片/脚本字段声明）
- Given phases.yaml 对 P2 的产出（P2-design.md / P2-review.md）与门槛（四字段等）已有声明
- When 对照 phase-cards/P2-design.md 文本与 check-gate.py 的 P2 判定逻辑运行 `check-structure-consistency.py`
- Then 三方一致且退出码为 0；任一处不一致 → 非 0 退出

### 6.2 M1 — 双跑对账

#### BDD-6: (M1) 对账模式告警不阻断
- Given M1 实现完成，`agate-read-gate-commands` / `check-pruning` / `check-gate` 接入对账模式
- When 用含已知 YAML↔grep 差异的夹具任务运行对账
- Then 脚本在 stderr 输出不一致告警（含 WARNING 与差异计数），且退出码保持原判定（0/2 语义不变，不新增阻断）

#### BDD-7: (M1) 对账覆盖面达标
- Given M1 对账实现完成
- When 统计接入对账的脚本数与覆盖的解析类型
- Then 脚本数 ≥ 3，且覆盖 gate_commands 块、P1 裁剪字段（risk_level/phases）、P2 四字段（packages/domains/ui_affected/gate_commands）三类解析点

### 6.3 M2 — 切换权威源

#### BDD-8: (M2) 对账清零后才切换
- Given M1 对账期结束
- When 用全量既有 fixture/测试对比 YAML 读取结果与 grep 结果
- Then 差异数为 0；存在残留差异 → 禁止切换，回退 M1 继续对账

#### BDD-9: (M2) 已迁移解析点静态零命中
- Given M2 切换完成
- When 静态扫描 `agate/scripts/*.py` 中已迁移的解析模式（如 `^(packages|domains|ui_affected|gate_commands):`、gate_commands 块正则）
- Then 已迁移脚本中对应 md 正则解析点的命中数为 0

#### BDD-10: (M2) 一致性 gate 提升为阻断并纳入 CI + pre-commit
- Given M2 完成
- When 人为制造 S-1/S-2 漂移，分别运行 `check-structure-consistency.py`、pre-commit gate、CI 一致性 job
- Then 三处均以非 0 退出阻断，漂移不放行

#### BDD-11: (M2) 迁移后回归全绿
- Given M2 提交完成
- When 运行全量 pytest、`count-tests.sh`、`check-protocol-consistency.py --strict-errors-only`
- Then pytest 全绿；count-tests 只增不减；consistency 0 ERROR

### 6.4 M3 — 卡片渲染化

#### BDD-12: (M3) 卡片门槛/产出/派发字段渲染一致（S-3 强制）
- Given M3 渲染器就位（phase-cards 门槛/产出/派发节由模板 + YAML 数据渲染）
- When 渲染后逐卡与 phases.yaml 声明对账（含人为篡改 YAML 中一个字段）
- Then 渲染产物与 YAML 声明一致；篡改后 `check-structure-consistency.py` 非 0 退出

#### BDD-13: (M3) agate-inject-card.py 渲染化兼容且稳定版隔离
- Given `agate-inject-card.py`（或新渲染器）改造完成
- When 以 P1/P2 派发流程注入 dispatch-context 卡片块；并在 worktree 存在未发布 YAML 改动时用 `~/.agate` 稳定版工具重复同一注入
- Then worktree 注入的卡片块与 YAML 渲染结果一致；稳定版注入结果不被 worktree 未发布 YAML 污染（双工作区隔离成立）

#### BDD-14: (M3) 渲染化回归全绿
- Given M3 提交完成
- When 运行全量 pytest、`count-tests.sh`、`check-protocol-consistency.py --strict-errors-only`、`check-structure-consistency.py`
- Then 全部通过：pytest 全绿、count-tests 只增不减、consistency 0 ERROR、结构一致性 0 漂移

### 6.5 跨里程碑回归

#### BDD-15: (M0-M3 全程) count-tests 只增不减
- Given 任意里程碑 commit 前
- When 运行 `bash agate/tests/scripts/count-tests.sh`
- Then 用例总数 ≥ TAG0021 立项时基线，且随新增测试单调不减

#### BDD-16: (M0-M3 全程) 测试平台无关
- Given 本任务新增/修改的脚本与测试
- When 运行 `check-platform-assumptions.py`（或人工静态审查）
- Then 不含裸 `python3`、硬编码 `PATH=...`、`-L` 软链假设、`/tmp` 路径等单平台假设；平台差异场景按分支断言或模拟环境覆盖

## 7. 待确认清单与提案

`[NO_NEED_CONFIRM]` —— 无待确认项。所有方向性选择均已由设计文档/派发指引/客观判据定案，倾向项以下列 `[SUGGEST]` 形式留审计痕迹（主 Agent 无异议即采纳，均不阻塞推进）：

`[SCOPE_RESOLVED: P4-M0 实现期 SCOPE+——check-protocol-consistency.py 锚点表（SCRIPT_ALIGNMENT_ANCHORS）追加 2 条纯数据登记以满足 tests/integration/test_protocol_alignment_review.py::test_sg_6 既有不变式（scripts/ 全部 check-*.py 须在锚点表登记）；无检查逻辑改动，P2 §1.2 N-1 表述修订为「除锚点数据登记外不改动一致性脚本」]`

- `[SUGGEST: 决策 D1 —— S-1~S-6 独立脚本 + 独立编号空间，不并入 check-protocol-consistency CHECKS；理由：M0 纯增量/可回退优先，合并评估留 M2]`
- `[SUGGEST: 决策 D2 —— BDD 连续数字编号 + (M0)-(M3) 标题后缀 + 组标题标注阶段；理由：gate 机械正则只认数字编号（scan 3/B2 佐证），前缀式会破坏 P1 gate 锚点与 P6/P6.5 计数]`
- `[SUGGEST: 决策 D3 —— M1 对账首批 = agate-read-gate-commands / check-pruning / check-gate；理由：B 组 5 处重复正则（DEBT0010 同族）+ A 组消费链最广]`

本文件不含 GAP 状态声明（不存在任何状态为 GAP 的能力条目，三态明细见 §9）；无未决 NEED_CONFIRM 项（已声明 `[NO_NEED_CONFIRM]`，见 §7）。

## 8. 裁剪说明

`phases: [P1, P2, P3, P4, P5, P6, P7, P8]` —— **全阶段保留，无跳过**。逐阶段理由：

| 阶段 | 保留理由 |
|------|---------|
| P2 | 不可裁：架构/schema 草案需展开为候选方案 + 评审（risk_level=high → plan-eng-review 经 C8 强制） |
| P3 | 不可裁：schema 校验 / S-1~S-6 双向一致性 / 对账模式均可写失败测试（TDD 先红后绿是设计 §5 硬约束） |
| P4 | 实现：M0-M3 分批 commit（新 YAML + 2 新脚本 + 渲染器） |
| P5 | 验证：pytest 全绿 + consistency 0 ERROR + count-tests 不漂移（每里程碑血糖） |
| P6 | 验收：逐条实跑 BDD-1..16；domains 不含 frontend，无 UI/视觉证据需求 |
| P7 | 一致性：改动横跨协议文档 + 全部 gate 脚本 + 卡片 + 新目录，跨文件交叉核对必要 |
| P8 | 发布：版本 bump + UPGRADING 章节 + tag；M2 属脚本行为变化须列入破坏性变更清单 |

不裁理由总述：改动面极大（P0-brief「改动面极大——建议按 M0-M3 分批 commit」）+ 工具链自举风险（用未发布的新 gate 判自己），每一阶段 gate 都是自举风险的兜底闸，不可省。

## 9. 能力需求声明与能力自查

**能力自查结论**：本任务为纯文档/分析/脚本类（无 UI 截图、无视觉验收），不涉及视觉能力，无需 `[CAPABILITY_GAP]` 声明，不需 vision 能力条目（P1 卡视觉硬要求仅当 `domains` 含 frontend 时触发，本任务 domans = [backend]）。

```yaml
capability_requirements:
  - need: text-analysis-scanning
    why: P1 三组同类扫描与 M0-M3 全程需要大规模文本扫描/正则分析（grep / read / glob）
    available:
      - "read/grep/glob 工具（独立通道，不占 bash）"
      - "python3 + pyyaml + pytest"
    status: available
  - need: protocol-editing
    why: 产出 P1 基线及后续阶段产出需编辑协议本体 markdown
    available:
      - "worktree 可写（.worktrees/agate-TAG0021，含 agate-workspace）"
    status: available
```

无 supplementable、无 GAP。`verification_env` 不声明：本任务无 debug server / 数据库 / 外部服务依赖；测试命令（pytest / consistency / count-tests）为主 Agent 标准操作可准备，仅需遵守 /tmp 只读约束（`-p no:cacheprovider --basetemp=<可写目录>`）与双工作区纪律。

## 10. 下游影响

- **P2**：依赖 `risk_level: high`（plan-eng-review 经 C8 机械映射强制）+ `domains: [backend]` 决定评审角色；`packages: [agate]` 作方案范围；四改动面（§5）作为方案候选的输入。
- **P6**：逐条对照 BDD-1..16（PASS/FAIL 总数 ≥ 16）；无 UI 证据需求（domains 不含 frontend）。
- **P7**：`packages: [agate]` 做跨文件一致性核对；四改动面文件清单做交叉引用检查。
- **基线保护**：本文件为需求基线，后续阶段如需变更按 P1 卡「P1 基线保护」流程（主 Agent 显式批准 + `[BASELINE_CHANGE: 理由]`，不改 BDD 的 Given/When/Then 语义）。