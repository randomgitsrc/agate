---
phase: P1
task_id: TAG0022-confirmed-problems
type: problems
parent: P0-brief.md
trace_id: TAG0022-P1-20260822
status: draft
created: 2026-08-22
agent: analyst
# ── v2.0 机器字段 ──
risk_level: high              # 改动面大（CI 配置 / check-gate.py / state-machine / P6 卡 / P1 卡 / 测试）+ 同簇互扰 + 触发 SELF-GATE
ceremony: standard            # 缺省档位，fail-closed；本任务非 thin 候选（RM-AG0040 实证对象是另立的 low 薄任务）
phases: [P1, P2, P3, P4, P5, P6, P7, P8]   # 全保留，不裁剪（理由见 §8）
packages: [agate]             # agate 协议本体为单一版本单元；五子项改动面见 §5
domains: [backend]            # 纯协议/脚本/CI/测试改造，无 frontend、无 security 域
---

# P1 需求基线 — TAG0022 三连任务确认问题修复批（RM-AG0037~RM-AG0041）

> 状态标记：[PROD_NOT_TOUCHED]（仅读稳定版 `~/.agate` 角色/卡片文件与主 checkout 协议文件；写操作全部落在 worktree `agate-workspace/` 内）

## 1. 需求复述

**任务一句话**：修复 TAG0019/20/21 全面分析（`dsh-workspace/agate-research/tag0019-21-analysis.md`，2026-08-22，基于 main 落地实测）确认的 5 个真实问题——ruff 合并强制 / 结构化层 M2 迁移闭环 / judge 启用强制化 / TAG0019 M3 实证收尾 / 环境假象测试根治。五个问题同属「质量门禁与迁移收尾」簇，改动域重叠（CI 配置 / check 脚本 / gate 逻辑 / 测试卫生），合并为一个 task，P1 起按子项分组。

**动机（P0-brief issues 锚定，逐条验收锚）**：

| # | 问题 | 证据（分析文档 main 实测） | 验收锚（P0-brief 原文） |
|---|------|--------------------------|------------------------|
| RM-AG0037 | ruff 检查合并强制 | TAG0019(23)+TAG0020(12) 带违规合并，合并后 main 实测 35 处错误，靠事后 PR #183 补修；TAG0021 靠内部 P5 自抓 70 处回修。CI 已有 ruff job（`protocol-tests.yml:106`）但对 PR 合并非硬性 | 新任务合并时 ruff 零违规无需事后补修 |
| RM-AG0038 | 结构化层 M2 迁移闭环 | check-gate.py（主 Agent 每阶段总闸）实测仍 22 处 md/grep 解析、0 处 YAML；「权威源」是并行双源（YAML + md），未真正切换，双份维护漂移风险仍在 | check-gate.py 零 md 解析 + 全量测试绿 |
| RM-AG0039 | judge 启用强制化 | P6 卡宣称「P6.5 judge 复核强制所有任务」，但 `judge.enabled` 由 P1 主 Agent 自写（state-machine.md:443），未启用则全链跳过（TAG0019/20 无 judge 块）——「与 P6 同不可裁」是软强制 | 新任务 P1 不写 judge 即被拦；历史任务跳过 |
| RM-AG0040 | TAG0019 M3 实证收尾 | `ceremony: thin` 从未实战（全仓无任务跑过）；成本下降目标（评审轮数 vs 真实发现数，TAG0018 基线）无实证；thin「跳过评审」是协议/提示词级行为，check-routing 只校验声明格式不校验执行 | 实证报告（可能需经用户指定薄任务实战） |
| RM-AG0041 | 环境假象测试根治 | test_bdd_7/25 依赖 basetemp 位置，TAG0020/21 各复现 2 次，仅登记 known-failures 未根治 | 任意 basetemp 位置下全量 pytest 0 失败 |

**达成形态（验收口径）**：五个问题各自闭环——① ruff 合并门禁成为硬性（实现侧 workflow + 配置步骤文档化）；② check-gate.py 的规则权威源切到 rules/*.yaml（对齐 gate_commands 族经 agate-md-field-get 的已迁移模式），S-1~S-6 收紧为「YAML 权威、md 禁止承载可判定规则」；③ 新任务 P1 不写 `judge.enabled: true` 被机械拦，历史任务不挂；④ `ceremony: thin` 实证执行计划 + 触发条件落盘（本 task 内可交付的验收锚）；⑤ 环境假象测试改为探测 git 上下文 / 强制仓库外 basetemp，任意位置全量 0 失败。

## 2. P0-brief 时效性质疑

**结论：无严重漂移；轻微漂移 1 处，记录不阻塞（不命中严重判据）。**

逐条对照 P0 卡「时效性自检」判据：

1. `task` 目标方案是否仍成立 → **成立**。P0-brief 的 5 个 issue 与 tag0019-21-analysis.md 的跨任务问题表（#1-#5）逐条一致，无内容漂移；改造对象 worktree 已含 TAG0019（check-routing/ceremony）、TAG0020（judge 链）、TAG0021（rules/*.yaml + check-structure-consistency + S-1~S-6）落地产物（scripts 目录逐一确认存在），与 P0-brief「修复 5 个确认问题」的假设一致，不构成方案冲突。
2. `executor_env` 平台前提是否仍成立 → **成立**。opencode / `has_task_tool: true` / `has_local_runtime: true` / `network: full` / `git: true` 均成立（本会话在 Linux、可写 worktree、可跑 git/测试）。
3. `known_risks`「已解决前提」是否变化 → **无变化**。① SELF-GATE 触发面仍在（改动 CI/check-gate/state-machine/P6 卡/P1 卡/测试）；② RM-AG0038 最大体量仍在；③ RM-AG0040 外部依赖（薄任务出现）仍未满足；④ RM-AG0037 的 required check 是 GitHub 分支保护配置（用户侧）——实现/配置边界仍在；⑤ 强制同类扫描已完成（见 §4）。另确认 `.state.yaml` 已写入 `judge.enabled: true`（TAG0022 是机制后新任务，P6 走 P6.5 judge——本 task 编排事实成立）。

`[P0_STALE: P0-brief env_constraints.debug_env 声明"权限为 danger-full-access"，实际执行环境为 workspace-write 沙箱且 /tmp、ptmp 只读（dispatch-context 客观查证：pytest 须 `-p no:cacheprovider --basetemp=<可写目录>`）——轻微漂移，已记录，按"环境约束具体值"处理，不阻塞 P1；测试命令声明以 HANDOFF §4 与 dispatch-context 客观查证为准]`

另记录（编排状态推进，非 brief 内容漂移）：HANDOFF 写 `.state.yaml phase=P0`，实际派发本 P1 时 phase 已推进为 P1——属编排正常推进，P0-brief 内容不涉及 phase 值，无需回写。

## 3. 隐含需求识别

逐维度快速过（本任务无数据/前端/多端/边界/兼容的常规面，但协议面隐含依赖密集）：

| # | 隐含需求 | 为什么必须 |
|---|---------|-----------|
| H1 | 本任务全部改动面触发 SELF-GATE | 改动面含 CI 配置 / check-gate.py / state-machine / P6 卡 / P1 卡 / 测试 → 后续每个含触发文件的 commit message 须含 `self-gate-review:` 路径或 `self-gate-skip:` 理由（HANDOFF §5 硬约束；P1 卡第 5 条已知风险）。可在 P2/P4 阶段要求一次协议对齐审查（protocol-alignment-review），后续阶段派发时由主 Agent 落实 |
| H2 | RM-AG0037 必须写清「实现 vs 配置」边界 | required check 是 GitHub 分支保护配置，需维护者（用户）在仓库设置勾选——实现侧只能改 workflow + 文档标注配置步骤；验收以 workflow 改动为准（不能把"设 required check"当实现写进 BDD）（dispatch-context 约束 1） |
| H3 | RM-AG0039 与 RM-AG0038 同簇互扰须区分 | 二者都触碰 check-gate.py：0038 迁移的是该文件读取协议规则的方式，0039 新增的是 P1 分支的 judge 校验。P1 影响面梳理（§4 扫描 2/3 + §5）必须区分，P4 分批 commit 错开文件（HANDOFF §7 已知风险） |
| H4 | RM-AG0040 实证依赖外部薄任务出现 | 本 task 内无法自证「实证对比报告」——交付形态 = 「实证执行计划 + 触发条件」作为 BDD 锚（dispatch-context 约束 1 明示），或经用户指定一个 low 风险任务实战；P1 BDD 锚按计划落盘写（BDD-8） |
| H5 | RM-AG0041 根治不得破坏测试平台无关原则 | agate 测试核心约束：不允许裸 `PATH=`/裸 `python3`/POSIX symlink 假设/`/tmp` 等 Unix-only 路径；「强制仓库外 basetemp」须在不引入 Unix 假设前提下实现（Linux 全量断言 + Windows 分支/模拟覆盖） |
| H6 | 本任务 P6 验收须含 P6.5 judge 复核 | `.state.yaml` 已写入 `judge.enabled: true`（机制后新任务强制）；P6 验收逐条过 BDD-1..10 后走 P6.5 judge（约束 6） |
| H7 | count-tests 只增不减（用例数冻结） | 仓库硬约定；RM-AG0038/0039/0041 都会新增测试，每里程碑血糖（HANDOFF §4 验证命令） |
| H8 | pytest 环境约束 | /tmp 只读 → 全量 pytest 须 `--basetemp=/home/kity/oclab/dsh-workspace/ptmp -p no:cacheprovider`；ruff 用 `~/.venvs/agate-dev/bin/ruff`（0.16.4 对齐 CI）；consistency 用 worktree 自己的脚本（双工作区纪律） |
| H9 | UPGRADING.md 新增本任务章节 | RM-AG0037 的 required check 配置步骤、RM-AG0038 的权威源切换属脚本行为变化（破坏性变更逐条列）、RM-AG0039 的 P1 gate 新校验——AGENTS.md 版本发布清单第 3 条强制（P8 卡「主 Agent 亲自执行」） |
| H10 | RM-AG0038 迁移的既有测试兼容 | 既有 pytest fixture 构造 md 文本任务夹具；迁移权威源后需 fixture 同步或对账桥接，回归面大但必须全绿——TDD 先红后绿（HANDOFF §5） |
| H11 | RM-AG0039 的校验语义要与「历史任务跳过」并存 | 机制前任务（无 judge 块）不得被新 P1 校验误拦——校验须区分机制前后（对齐既有 P6.5 链的 BDD-2 历史兼容语义） |
| H12 | P1 gate 锚点格式不变 | check-gate.py 的 P1 分支既有 BDD 锚点/标记判定语义不得回归（0039 的 judge 校验是新增分支，不破坏既有判定）；P1 需求基线保护（约束 7：不改验收标准） |

## 4. 同类扫描结论（强制）

> 四组扫描按 dispatch-context 强制清单执行（扫描以 worktree `agate/` + `.github/workflows/` + `pyproject.toml` 为准）。逐条判定写在本节正文，progress 里的原始记录仅作过程痕迹。每条命中标「本次处理 / 本次不处理 + 理由」。

### 4.1 扫描 1：ruff 消费点（grep `ruff` 全仓）

**统计**：`.yml`/`.sh` 层无命中（注：`.github/` 为隐藏目录，grep 工具默认跳过，已用 read 直接核实 workflow）；`.py` 命中 2；`.toml` 命中 2（pyproject.toml）；`.md` 命中 460（绝大多数为文档引用与任务历史数据）。

| # | 命中 | 位置 | 判定 |
|---|------|------|------|
| 1 | **CI ruff job（唯一强制执行点）** | `.github/workflows/protocol-tests.yml:106-116`（`ruff:` job，`pip install ruff && ruff check agate/`，ubuntu-latest） | **本次处理（RM-AG0037）**：就是它未作为 PR required check 才导致 3 次漏网。实现侧=workflow 保持稳定 job name（可被分支保护引用）+ UPGRADING/文档写 required check 配置步骤；required 勾选是配置，用户执行 |
| 2 | **ruff 规则集配置** | `pyproject.toml:1,6`（`[tool.ruff]` / `[tool.ruff.lint]`，target py38，src 含 agate/scripts + agate/tests） | **本次不处理**：规则集是运行参数非强制点；TAG0010/0011 已定稿，本 task 无新增规则需求 |
| 3 | **本地测试验证** | `agate/tests/unit/test_env_adapt_docs.py:99-123`（test_bdd_34：`ruff check agate/` 0 error，ruff 未安装时 skip） | **本次不处理**：已有本地验证，保留；与 RM-AG0037 的 CI 强制互补，不重复实现 |
| 4 | **文档引用** | AGENTS.md（依赖/开发环境）、UPGRADING.md、platform-notes.md、tests/README.md、docs/guides/worktree-dogfooding-guide.md、docs/notes/lessons.md | **本次不处理**：非执行点；仅 UPGRADING 需新增配置步骤节（并入 H9，随 RM-AG0037 处理） |
| 5 | **注释/历史** | `agate/scripts/agate-feedback.py:42`（注释提 PLW0603）、任务历史数据（TAG0010/11/14/21 各阶段文件） | **本次不处理**：注释非消费；任务历史数据是记录非代码 |

**关键佐证**：`*.sh` 与 `pre-commit-gate.py` 均无 ruff 调用——**ruff 无 pre-commit 消费**（TAG0010 决策「ruff CI 独立 job，不做 pre-commit hook 子步骤」，P4-dispatch-context-implementer-batch4c3.md:181 佐证）。因此「合并强制」的落点就是 CI ruff job 的 required check，实现侧无 pre-commit 改动。

**回归拦截声明**：RM-AG0037 之后，新任务合并必须过 CI ruff job（required check 生效）——拦截手段 = 分支保护配置 + P5/P6 本地 `ruff check agate/` 全绿（转 BDD-2）。无新增 gate 脚本需求（防「设 required check 当实现」误区，见 §5 D1）。

### 4.2 扫描 2：check-gate.py md/grep 解析点清单（grep `re.`/`_md_field`/`startswith` 等）

**统计**：regex/行解析相关命中 84 处；分析文档 main 实测基线「22 处 md/grep 解析、0 处 rules YAML 权威源读取」。本 worktree 逐行核对按解析对象分 6 组：

| 组 | 解析对象 | 代表位置 | 判定 |
|----|---------|---------|------|
| A | frontmatter/正文字段读取（`_md_field_get` 调 `agate-md-field-get.py` + 本地 sed 等价提取） | 定义 L95/L173-174；调用 ~16 处：domains(L327)、ui_render_shape(L380/471)、ui_ux_dimensions(L381)、ui_affected(L412)、need_confirm_resolved(L533)、suggest_resolved(L554)、dispatch_plan(L606)、change_type(L929)、regression_pass(L931)、pass/fail(L939-940)、blocker_count(L1005)、deviation_critical_count(L1006)、design_gap_count(L1030)、design_gap_reviewed_count(L1031) | **本次处理（RM-AG0038 主面）**：对齐 gate_commands 族经 agate-md-field-get 的已迁移模式——规则声明归 YAML，任务产出字段统一走结构化读取（P2 细化映射清单） |
| B | 行首标记正则（NEED_CONFIRM / SUGGEST / NO_NEED_CONFIRM） | `_NC_RE`/`_SUGGEST_RE`/`_NO_NEED_RE`/`_NC_DESC_RE`/`_SUGGEST_DESC_RE`（L101-110）+ 正文计数（L523-557） | **本次处理**：标记协议可结构化（随 A 组迁） |
| C | 任务产出格式判定正则（BDD 标题 / UI 区块 / P6 旧格式 / P7 标记 / CODE_MAP / fail-list / 表格计数） | BDD 标题 L390；UI 设计区块 L417-462；candidate_count L693-694；design_trivial/follows L703；P6 旧格式 PASS/FAIL L946-954；BLOCKER/DEVIATION-CRITICAL L1015-1023；DESIGN_GAP L1048-1088；CODE_MAP L1127-1128；fail-list 代码块 L875；表格计数 L909；权衡关键词 L736 | **本次处理（M2 二期，随 A 组分批）**：判定对象本身是任务产出 md，读取方式统一结构化；「协议规则」侧（门槛/产出/阶段表等）不再从 md grep |
| D | P1-requirements.md 内嵌 ```yaml 块解析 | L336-338（`re.finditer(r"```(?:yaml\|yml)...")` + yaml.safe_load） | **本次处理**：md 内嵌 YAML 读取属双源残留，迁移后由结构化读取取代 |
| E | .state.yaml 读取 | `_load_state_yaml`（L230-241）+ gate_p65 judge 块（L982-983） | **本次不处理**：`.state.yaml` 已是 YAML 结构化（任务状态，非规则权威源）；`_STAGED_EXCLUDE_RE`（L114）是路径正则非 md 内容 |
| F | git / CHANGELOG 输出解析 | version_re 对 git 输出（L1162-1174）、changelog diff 版本号（L1203）、phase 数字提取（L1229-1230） | **本次不处理**：读的是工具/数据输出而非协议规则 md，非「双源漂移」面 |

**关键佐证**：全文件无 `rules/*.yaml` / `check-structure-consistency` 的读取调用（grep `rules/` 仅 L657 注释提 phases.yaml）——**0 处 YAML 权威源读取**与分析文档一致，双源未切换，RM-AG0038 成立。

**回归拦截声明**：RM-AG0038 之后，脚本新增「从协议规则 md 正则读取可判定规则声明」一律拦截——由 S-4（YAML→scripts 字段声明一致）+ 静态扫描（迁移后解析点在 `agate/scripts/` 零命中，转 BDD-3）兜底；任何新脚本想读规则先入 YAML 再读。

### 4.3 扫描 3：judge.enabled 消费点（grep `judge.enabled` 全仓）

**统计**：命中 53 处。生产代码 8 + 协议文档 9 + 测试 3 + 任务数据/历史 33（含本 task 自身文档）。

| # | 命中 | 位置 | 判定 |
|---|------|------|------|
| 1 | check-gate.py gate_p65 分支 | `agate/scripts/check-gate.py:977/982-983`（读 .state.yaml judge.enabled，未启用早退 0） | **本次处理（仅新增 P1 校验点）**：0039 的新校验落 check-gate.py P1 分支（gate_p1 新增 judge 校验），与 gate_p65 既有消费不冲突 |
| 2 | pre-commit-gate.py 2i.1 注入 | `agate/scripts/pre-commit-gate.py:152/387/390`（`_judge_enabled` + verdict 存在 → 双脚本） | **本次不处理**：P6.5 commit-time 硬边界，机制本身不在本 task issues；保持 |
| 3 | ci-gate-backstop.py 兜底 | `agate/scripts/ci-gate-backstop.py:101/267`（`_judge_enabled` + judge/events 兜底） | **本次不处理**：同上，保持 |
| 4 | state-machine.md 写入模板 | `agate/state-machine.md:153/155`（P6.5 硬边界/早退语义）+ **L442-443**（`judge: enabled: true` 模板，注释「P1 初始化时主 Agent 写入；缺失/false = 历史任务」） | **本次处理（文档面）**：L442-443 是「软强制」源头（自写开关）——0039 需把模板语义改为「机制后新任务必须含 judge.enabled: true」；P1 卡同步（见下） |
| 5 | P6 卡 P6.5 复查节 | `agate/phase-cards/P6-acceptance.md:21/178/209` | **本次不处理**：机制条文保持；0039 是新任务 P1 侧校验，不改变 P6 卡既有「强制所有任务」宣称（那正是软强制的宣称处，靠 P1 机械校验来兑现） |
| 6 | WORKFLOW.md / dispatch-protocol.md / UPGRADING.md | WORKFLOW.md:299；dispatch-protocol.md:406；UPGRADING.md:142 | **本次不处理**：条文引用，保持；如语义措辞需随 0039 微调，属 0039 文档面，P2 定 |
| 7 | 测试 | `agate/tests/unit/test_check_gate.py:2628/2636/2666`（judge 开关三态：无/true/false） | **本次不处理**：既有用例保持；0039 新校验需新增用例（P3） |
| 8 | 任务数据/历史 | roadmap.md、P0-brief、TAG0020 各阶段文件、TAG0021 P6-dispatch-context-verifier | **本次不处理**：历史记录非代码消费 |

**关键佐证**：消费链三处（check-gate gate_p65 / pre-commit 2i.1 / ci-backstop）判定一致（judge.enabled && verdict 存在 → 跑同一双脚本）；缺的正是「谁保证新任务写 judge」——P1 gate 机械校验补上这个缺口（软强制→硬强制）。与 RM-AG0038 同簇互扰：0039 新增的校验点与 0038 的迁移面都在 check-gate.py，但一个在 P1 分支新增逻辑、一个在规则读取层换源，P4 分批 commit 错开（§5 D3）。

**回归拦截声明**：0039 之后，机制后新任务 P1 缺 judge 被机械拦（转 BDD-6）；历史任务（机制前）不受影响（转 BDD-7）。

### 4.4 扫描 4：ceremony 消费点（grep `ceremony` 全仓）

**统计**：agate/ 内命中 110 处（脚本 6 + 测试 6 文件 + 协议文档/角色 11 文件）；任务数据内 `ceremony: thin` 命中 48 处——逐一核对全部为 TAG0019 机制测试 fixture / 文档条文引用，**无任何任务真跑过 `ceremony: thin`**（RM-AG0040 基线成立）。

| # | 命中 | 位置 | 判定 |
|---|------|------|------|
| 1 | check-routing.py（路由校验主体） | `agate/scripts/check-routing.py`（L79-134：读 P1 frontmatter ceremony + 三值校验 + thin 四要素 + 与算分 tier 单向 fail-closed） | **本次处理（仅实证边界标注）**：check-routing **只校验声明格式/要素，不校验「thin 档是否真跳过评审」的执行语义**——这是 M3 未闭环的机械证据，实证计划须把它作为已知边界写明（BDD-8） |
| 2 | pre-commit-gate.py 2j.1 挂载 | `agate/scripts/pre-commit-gate.py:402-403` | **本次不处理**：机制保持 |
| 3 | frontmatter 字段链 | `agate/scripts/agate-frontmatter-check.py:38/44/59`（枚举+三值）、`agate/scripts/agate-md-field-get.py:98`（NO_FALLBACK）、`agate/scripts/check-structure-consistency.py:64`（字段清单）、`agate/scripts/check-protocol-consistency.py:685-687`（gate 注册表描述） | **本次不处理**：字段读/校验链保持；RM-AG0038 迁移 A 组时若涉及 ceremony 读取方式，随迁不改语义 |
| 4 | 测试 | test_check_routing.py（BDD-6..10 主体）、test_check_frontmatter.py（枚举拦截）、test_agate_md_field_get.py（读侧）、test_docs_assertions.py（BDD-12 四要素条文 + BDD-14 full→P7）、test_pre_commit_hook.py（C3 链上） | **本次不处理**：机制测试保持；实证计划可复用 M3 验收锚度量协议四要素定义（P1 卡 BDD-12） |
| 5 | 协议文档/角色/模板 | P1 卡（ceremony checklist 节 L111-120）、P2 卡 L191、P4 卡 L95、review-mapping.md L24-27、role-system.md L64-67、requirements-review.md L54-93、WORKFLOW.md L330、dispatch-protocol.md L958、CONTEXT.md L30、UPGRADING.md L151-152、templates/task-files.md L144、analyst.md 模板 L69 | **本次不处理**：机制条文保持；本 task 5 个 issues 不含 ceremony 机制改造（RM-AG0040 只要求实证收尾，不改机制） |
| 6 | 任务历史数据 | TAG0019 P1-P6 各阶段（thin 全为 fixture） | **本次不处理**：历史记录 |

**回归拦截声明**：ceremony 机制不在本 task 改动面内，无新增回归点；实证计划（BDD-8）将「执行语义无机械校验」记录为已知边界，供薄任务实战时设计观测手段（评审轮数/真实发现数采集），不新增 gate 脚本。

## 5. 范围声明与关键决策

**范围（packages: [agate] 的五子项改动面）**：

| 子项 | 改动面（P0-brief 声明） | 归属阶段 |
|------|------------------------|---------|
| RM-AG0037 | CI 配置（.github/workflows/protocol-tests.yml ruff job 稳定化 + required check 配置步骤文档） | P4（workflow + 文档）/ P8（UPGRADING 章节） |
| RM-AG0038 | check-gate.py 规则读取迁移到 rules/*.yaml + S-1~S-6 收紧 | P2 设计映射 / P3 静态扫描测试 / P4 分批 / P5 验证 |
| RM-AG0039 | check-gate.py P1 分支新增 judge 校验 + state-machine/P1 卡模板语义 | P2 设计 / P3 测试 / P4 实现（与 0038 错开文件） |
| RM-AG0040 | 实证执行计划 + 触发条件（交付物；不改机制） | P2/P4 内嵌计划产出 / P6 验收 |
| RM-AG0041 | test_bdd_7/25 改探测 git 上下文/强制仓库外 basetemp | P3 测试 / P4 实现 |

**关键决策（本 P1 基线内定案，无需人工介入）**：

- **D1（RM-AG0037 实现 vs 配置边界）**：实现侧只交付「workflow 中 ruff job 以稳定 job name 存在 + UPGRADING/AGENTS 标注『将 ruff job 勾选为 PR required check（GitHub 分支保护，维护者配置）』的步骤」；required 勾选本身是配置，由维护者（用户）执行，不写进实现 BDD 的 When（验收锚以 workflow 改动为准）。**禁止**把「设 required check」当作实现侧可完成动作。`[SUGGEST: D1]`
- **D2（RM-AG0038 判定口径）**：「check-gate.py 零 md 解析」= 协议规则类 md/grep 解析点清零（§4.2 A/B/C/D 组；判定对象是"协议规则声明"从 md 读取），任务产出文件校验（C 组 P6/P7 格式判定）统一走结构化读取器、不写裸正则；`.state.yaml`（E 组）与 git/CHANGELOG 输出（F 组）不计入「md 解析」面（它们是 YAML/工具输出，非规则 md）。P2 据此给出逐点映射清单，P3 固化为静态扫描测试。`[SUGGEST: D2]`
- **D3（0038/0039 同簇分批纪律）**：0039 的 P1 校验点与 0038 的规则读取迁移都在 check-gate.py，P4 分两个 commit 批（或至少不同改动块）推进，避免同一文件多轮大改；0039 优先于或并行于 0038 的 P1 分支改造，验证锚互不干扰（HANDOFF §7 已知风险）。`[SUGGEST: D3]`
- **D4（RM-AG0040 交付形态）**：本 task 验收锚 = 「实证执行计划 + 触发条件」落盘（BDD-8，四要素 + 触发条件，全部可二值判定）；实证对比报告在触发条件满足后由薄任务产出，不在本 task 验收内——除非用户显式指定一个 low 薄任务在本 task 窗口实战（此时按 BDD-8 附加报告验收）。`[SUGGEST: D4]`

> 本节约束为范围/边界决策，不涉及具体实现方案（候选方案与机制设计留 P2 architect）。

[SCOPE_RESOLVED: P2-design.md §1.4 [SCOPE+]——M15（check-protocol-consistency.py `iter_md_files` 新增 opt-in 排除钩子 `AGATE_CONSISTENCY_SKIP_DIRS`，默认关闭、行为不变）为主 Agent 采纳：test_bdd_25 在「仓库内 basetemp」位置失败的根因是迭代扫描到 basetemp 下预存测试生成的坏引用 fixture .md（TAG0020 known-failures 条目 2 实证），M15 为 BDD-9「任意 basetemp 位置全量 0 失败」的必要使能；归属 BDD-9 验收口径内、不新增 BDD；该文件进入改动面（P4 期实现，dsh 沙箱 /tmp 只读下的仓库内位置验证口径以 P2 design §8 为准）]

## 6. BDD 验收条件

> 编号连续 BDD-1..BDD-10，按 5 子项分组。每条独立可二值判定（PASS/FAIL），Given/When/Then 不绑定实现符号，全部以「运行命令后观察退出码/输出/文件」为客观判据。组标题标注归属子项。

### 6.1 RM-AG0037 ruff 合并强制

#### BDD-1: CI ruff job 可被 required check 引用且配置步骤文档化
- Given P4 完成时 `.github/workflows/protocol-tests.yml` 存在 `ruff` job（`ruff check agate/`），且仓库文档存在（UPGRADING.md 新增章节或 AGENTS.md）
- When 核对 workflow diff（ruff job name 保持稳定、可被 GitHub 分支保护按 job/check 名引用）并 grep 文档中「required check」「分支保护」「勾选 ruff」配置步骤文本
- Then workflow 中 ruff job 以稳定 job name 存在（无歧义改名），且文档含明确的「将 ruff job 设为 PR required check（维护者在仓库设置勾选）」配置步骤；二者同时成立为 PASS，任一缺失为 FAIL（验收以 workflow + 文档为准，required 勾选本身由维护者配置，不设为本 BDD 的 When 动作）

#### BDD-2: 新任务合并时 ruff 零违规（验收锚，防复发）
- Given RM-AG0037 实现完成（CI ruff job 就位；若用户已完成 required check 勾选则 CI 合并链路生效）
- When 在 P5/P6 验证窗口运行 `~/.venvs/agate-dev/bin/ruff check agate/`（0.16.4 对齐 CI）
- Then 两次运行均 exit 0（All checks passed，0 违规）；任一违规 → FAIL。合并主线上 ruff job 绿为合并前提（配置生效后由 CI 强制）

### 6.2 RM-AG0038 M2 迁移闭环

#### BDD-3: check-gate.py 协议规则类 md 解析清零（验收锚前半）
- Given RM-AG0038 实现完成（规则权威源切到 rules/*.yaml，S-1~S-6 收紧生效）
- When 对 `agate/scripts/check-gate.py` 做静态扫描：§4.2 A/B/C/D 组模式（协议规则声明/任务产出格式从 md 正则读取、md 内嵌 yaml 块解析）是否存在残留
- Then 协议规则类 md 解析点命中数 = 0（判定模式清单由 P2 按 §4.2 细化映射、P3 固化为静态扫描测试、P5 执行）；残留任一 → FAIL。`.state.yaml` 读取（E 组）与 git/CHANGELOG 输出解析（F 组）不计入

#### BDD-4: 迁移后全量测试绿（验收锚后半）
- Given RM-AG0038 提交完成
- When 运行验证命令集：`python3 -m pytest agate/tests/ -p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp`、`bash agate/tests/scripts/count-tests.sh`、`python3 agate/scripts/check-protocol-consistency.py --strict-errors-only`、`python3 agate/scripts/check-structure-consistency.py`
- Then pytest 0 failed（设计内 skip 不计失败）；count-tests 用例总数 ≥ 立项基线且只增不减；consistency 0 ERROR；结构一致性 0 漂移；任一不满足 → FAIL

#### BDD-5: S-1~S-6 收紧为「YAML 权威、md 禁止承载可判定规则」
- Given S-1~S-6 收紧实现完成
- When 人为制造单侧漂移（在协议 md/phase-cards 新增一条可判定规则声明或门槛行而不入 YAML，或改 YAML 不动 md）后运行 `check-structure-consistency.py`
- Then 非 0 退出报告对应 S-* 漂移（md 侧新增可判定规则未入 YAML 即报）；双侧一致时 exit 0

### 6.3 RM-AG0039 judge 启用强制化

#### BDD-6: 机制后新任务 P1 不写 judge 即被拦（验收锚）
- Given RM-AG0039 实现完成（P1 gate 增 judge 校验）
- When 以「机制后新任务」目录（.state.yaml 无 judge 块或 `judge.enabled` 非 true）且 P1 产出齐全，运行 `check-gate.py P1 <task_dir>`
- Then 非 0 退出（阻断）并输出 judge 缺失/未启用提示（校验强度「阻断或高优 WARNING 升级」由 P2 定案，两种实现路径均满足「被拦」锚，二值判定以最终 exit code + stderr 语义为准）；含 `judge.enabled: true` 的同构目录 → exit 0/原语义放行

#### BDD-7: 历史任务（机制前）跳过，存量不挂
- Given 历史任务目录（TAG0019/20 等机制前任务，.state.yaml 无 judge 块）跑 check-gate.py P1
- When 复用既有历史夹具/目录
- Then exit 0 不被拦（向后兼容，与 gate_p65 的 BDD-2 历史兼容语义一致）

### 6.4 RM-AG0040 M3 实证收尾

#### BDD-8: 实证执行计划 + 触发条件落盘（本 task 验收锚）
- Given RM-AG0040 交付物就绪（实证执行计划节位于 P2-design.md 或 P4-implementation.md 或独立附件）
- When 核对交付物是否含 M3 验收锚四要素 + 触发条件：① 评审轮数指标（P2/P4 派发的 LLM 评审 subagent 轮数，含重试）；② 真实发现数指标（评审产出中被采纳/阻止真实问题的条数，排除非阻塞建议与机械可抓项）；③ TAG0018 基线值（4 场 LLM 评审 ≈ 0 净收益：17 条非阻塞 + 1 条真实发现且机械检查可抓）；④ 不达标决策规则（LLM 评审真实发现 ≈ 0 且机械 gate 已覆盖 → 回滚 standard）；⑤ 触发条件（下一个 low 风险任务 / 用户指定薄任务真跑 `ceremony: thin`）
- Then 四要素 + 触发条件全部齐全且各自可二值判定（每项有明确采集/判定口径），缺任一 → FAIL。实证对比报告在触发条件满足后由薄任务产出（用户显式指定薄任务在本 task 窗口实战时，P6 附报告替代本 BDD 验收）

### 6.5 RM-AG0041 环境假象测试根治

#### BDD-9: 任意 basetemp 位置下全量 pytest 0 失败（验收锚）
- Given RM-AG0041 实现完成（test_bdd_7/25 已改为探测 git 上下文 / 强制仓库外 basetemp，按平台分支断言）
- When 分别在「仓库内默认 basetemp」「仓库外显式 `--basetemp=/home/kity/oclab/dsh-workspace/ptmp -p no:cacheprovider`」两种位置运行全量 pytest
- Then 两种位置均 0 failed（test_bdd_7/25 不再依赖 basetemp 位置）；任一位置失败 → FAIL

#### BDD-10: 平台无关原则不破坏（回归拦截）
- Given test_bdd_7/25 修改完成
- When 运行 `python3 agate/scripts/check-platform-assumptions.py` 全树扫描 + 人工核对修改点 diff
- Then 修改不引入裸 `PATH=`/裸 `python3`/POSIX symlink 硬假设/`/tmp` 路径等单平台假设（平台差异按分支断言或模拟环境覆盖）；扫描器 0 R1-R5 命中 → PASS，任一违规 → FAIL

## 7. 待确认清单与提案

`[NO_NEED_CONFIRM]` —— 无待确认项。所有方向性选择均已由 P0-brief / 派发指引 / 客观查证定案，倾向项以下列 `[SUGGEST]` 形式留审计痕迹（主 Agent 无异议即采纳，均不阻塞推进）：

- `[SUGGEST: D1 —— RM-AG0037 实现侧边界 = workflow 稳定 job name + 配置步骤文档；required 勾选由维护者配置，验收以 workflow+文档为准]`
- `[SUGGEST: D2 —— RM-AG0038「零 md 解析」判定口径 = 协议规则类解析点清零（§4.2 A/B/C/D），任务产出校验统一结构化读取，E/F 组不计入；P2 细化映射、P3 固化静态扫描]`
- `[SUGGEST: D3 —— 0039 的 P1 judge 校验与 0038 的规则读取迁移分 commit 批错开文件，避免 check-gate.py 同文件多轮大改]`
- `[SUGGEST: D4 —— RM-AG0040 本 task 验收锚 = 实证计划+触发条件（BDD-8）；若用户可指定一个 low 薄任务实战，则作为实战载体并附对比报告]`
- `[SUGGEST: RM-AG0039 校验强度（阻断 vs 高优 WARNING 升级）由 P2 定案，P1 BDD-6 以「被拦」为锚双路径可判]`

本文件不含 GAP 状态声明（不存在任何状态为 GAP 的能力条目，三态明细见 §9）；无未决 NEED_CONFIRM 项（已声明 `[NO_NEED_CONFIRM]`）。

## 8. 裁剪说明

`phases: [P1, P2, P3, P4, P5, P6, P7, P8]` —— **全阶段保留，无跳过**。逐阶段理由：

| 阶段 | 保留理由 |
|------|---------|
| P1 | 不可裁（核心阶段）——本文件 |
| P2 | 不可裁：check-gate.py 迁移逐点映射清单 + 0039 校验强度 + S-1~S-6 收紧语义需候选方案与评审（risk_level=high → plan-eng-review 经 C8 强制） |
| P3 | 不可裁：0038 静态扫描测试、0039 P1 校验用例、0041 环境测试改造均可写失败测试（TDD 先红后绿） |
| P4 | 实现：五子项分批 commit（0038/0039 错开文件，HANDOFF §5） |
| P5 | 验证：pytest 全绿 + consistency 0 ERROR + ruff 全绿 + count-tests 不漂移（BDD-2/4） |
| P6 | 验收：逐条实跑 BDD-1..10；本任务 domains 不含 frontend，无 UI/视觉证据需求；**须含 P6.5 judge 复核**（judge.enabled: true 已写入，H3） |
| P7 | 一致性：改动横跨 CI 配置 + check-gate.py + state-machine + P6 卡 + P1 卡 + 测试，跨文件交叉核对必要 |
| P8 | 发布：版本 bump + UPGRADING 章节（required check 配置步骤 + 权威源切换破坏性变更）；SELF-GATE review |

不裁理由总述：改动面大（CI/check 脚本/gate 逻辑/测试卫生四域）+ 同簇互扰（0038/0039 同文件）+ 工具链自举风险（用未发布的新 gate 判自己），每一阶段 gate 都是兜底闸，不可省。`ceremony: standard`（fail-closed，不声明薄化）——本任务非 thin 候选，thin 档实证对象是另立的 low 薄任务（RM-AG0040 触发条件）。

## 9. 能力需求声明与能力自查

**能力自查结论**：本任务为纯文档/分析/脚本/CI 类（无 UI 截图、无视觉验收），不涉及视觉能力，无需 `[CAPABILITY_GAP]` 声明，不需 vision 能力条目（P1 卡视觉硬要求仅当 `domains` 含 frontend 时触发，本任务 domains = [backend]）。

```yaml
capability_requirements:
  - need: text-analysis-scanning
    why: P1 四组同类扫描与 P2-P5 迁移期静态审计（grep/read/glob 大范围、正则模式核对）
    available:
      - "read/grep/glob 工具（独立通道，不占 bash）"
      - "python3 + pyyaml + pytest"
    status: available
  - need: python-testing-and-lint
    why: P3-P6 全量 pytest + ruff 静态检查 + consistency/structure gate（--basetemp 可写目录约束）
    available:
      - "系统 python3 + pytest（/tmp 只读 → --basetemp=/home/kity/oclab/dsh-workspace/ptmp -p no:cacheprovider）"
      - "~/.venvs/agate-dev/bin/ruff（0.16.4 对齐 CI）"
      - "worktree 可写（.worktrees/agate-TAG0022，含 agate-workspace）"
    status: available
  - need: protocol-editing
    why: 产出 P1 基线及后续阶段产出需编辑协议本体 markdown / rules YAML
    available:
      - "worktree 可写；双工作区纪律（只改 worktree，禁止改动主 checkout 与 ~/.agate）"
    status: available
```

无 supplementable、无 GAP。`verification_env` 不声明：本任务无 debug server / 数据库 / 外部服务依赖；测试命令（pytest / consistency / ruff / count-tests）为主 Agent 标准操作可准备，仅需遵守 /tmp 只读约束（`-p no:cacheprovider --basetemp=<可写目录>`）与双工作区纪律。RM-AG0037 的 required check 勾选属 GitHub 仓库配置（用户侧操作），非本任务运行环境依赖。

## 10. 下游影响

- **P2**：依赖 `risk_level: high`（plan-eng-review 经 C8 机械映射强制）+ `domains: [backend]` 决定评审角色；`packages: [agate]` 作方案范围；§4 四组扫描清单作迁移映射/影响面输入（D2）；§5 范围表作分批 commit 骨架。
- **P6**：逐条对照 BDD-1..10（PASS/FAIL 总数 ≥ 10）；无 UI 证据需求（domains 不含 frontend）；**P6.5 judge 复核强制**（H3，.state.yaml 已写入 `judge.enabled: true`）。
- **P7**：`packages: [agate]` 做跨文件一致性核对；五子项改动面文件清单做交叉引用检查（CI/check-gate/state-machine/P6 卡/P1 卡/测试）。
- **P8**：UPGRADING 新增章节（RM-AG0037 required check 配置步骤 + RM-AG0038 权威源切换破坏性变更 + RM-AG0039 P1 校验）；SELF-GATE review；版本引用文件清单（README badge/CHANGELOG）。
- **基线保护**：本文件为需求基线，后续阶段如需变更按 P1 卡「P1 基线保护」流程（主 Agent 显式批准 + `[BASELINE_CHANGE: 理由]`，不改 BDD 的 Given/When/Then 语义）。
