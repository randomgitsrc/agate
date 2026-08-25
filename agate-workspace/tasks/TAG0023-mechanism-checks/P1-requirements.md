---
phase: P1
task_id: TAG0023-mechanism-checks
type: problems
parent: P0-brief.md
trace_id: TAG0023-P1-20260824
status: draft
created: 2026-08-24
agent: analyst
# ── v2.0 机器字段 ──
risk_level: high            # 改动面：check-gate.py / check-state-transition.py / P1/P2/P8 卡 / check-debt.py / CI 配置 / 测试；触发 SELF-GATE；同簇互扰（0042/0043 同触碰 check-gate.py）
ceremony: standard          # 缺省档位，fail-closed；本任务非 thin 候选
phases: [P1, P2, P3, P4, P5, P6, P7, P8]   # 全保留，不裁剪（理由见 §8）
packages: [agate]           # agate 协议本体单一版本单元；4 子项改动面见 §5
domains: [backend]          # 纯协议/脚本/CI/测试改造，无 frontend、无 security 域
implicit_coupling: true     # RM-AG0042 与 RM-AG0043 均触碰 check-gate.py 的不同分支（见 §3 H3），P4 需分批 commit
---

# P1 需求基线 — TAG0023 机制校验补强批（RM-AG0042 ~ RM-AG0045）

> 状态标记：[PROD_NOT_TOUCHED]（本阶段仅读取 P0-brief / HANDOFF / 复盘文档 / 稳定版角色卡片 / worktree 脚本源码，无任何写操作落在 worktree 之外）

## 1. 需求复述

**任务一句话**：修复 TAG0019-21 复盘独立评审（`dsh-workspace/agate-research/retrospective-tag0019-21.md`，2026-08-23 approved）确认的 3 个 agate 机制缺口（RM-AG0042/0043/0044）+ 2026-08-23 并入本 task 的 RM-AG0045（声明写时校验），四条同属"gate/校验补强"簇（check-gate.py / check-state-transition.py / check-debt.py / CI / 测试卫生改动面重叠），合并一个 task，P1 起按 4 子项分组。

**动机（P0-brief issues 锚定，逐条验收锚）**：

| # | 问题 | 证据 | 验收锚（P0-brief 原文） |
|---|------|------|------------------------|
| RM-AG0042 | 门槛失败事件强制记录 retries | 复盘问题 10：TAG0019/20/21/22 四任务 `.state.yaml` `retries` 全为 `{}`，而 requirements-review 3 轮/plan-eng-review 1 轮 rejected、P5→P4 回退 3 次（TAG0019/21/22）、子代理空返回重派均真实发生且未记录；`check-state-transition.py`（L146-154）有 `retries_over → PAUSED` 上限机制但无对应性校验，MAX_RETRY 被静默绕过 | 新任务评审 rejected 后 retries 必有对应条目（对应性校验拦截空记录）|
| RM-AG0043 | P8 roadmap 回写 done 校验 | roadmap.md 核实 RM-AG0032（独立 Judge）两行状态为 `backlog`（L30）/`scheduled`（L31），均非 `done`，而 v0.59.0 已发布、PR #184 已合并；`check-gate.py` 全文 grep `roadmap` 仅 1 处命中且与 P8 无关（L871，P4 门禁注释）——确认 P8 gate 当前无任何 roadmap done 校验 | 新任务 P8 后 roadmap RM 自动 done；RM-AG0032 手工补记验证 |
| RM-AG0044 | 环境敏感测试集中治理 | 第三例：roadmap.md L43 实证记录——PR #188 同 commit 双 CI run 一过一挂（push 事件过 / pull_request 事件挂：`test_bdd_14_retreat_entry_present_no_warning` 的 `GATE DEBT WARNING` 断言失败），重跑即过，本地 3/3 过；与 RM-0041（test_bdd_7/25 basetemp）同类不同根因 | test_bdd_14 连续 5 次 CI 稳定 + 环境敏感测试集中清单 |
| RM-AG0045 | 声明写时校验 | TAG0019 实证：`coupling_checklist` 流式声明/半角冒号/源码数 6>5 均在 commit 时才由 pre-commit gate 暴露，每轮折返一次 subagent 往返；写路径（生成器/编辑器/formatter 层）无 schema 校验 | 声明格式错误写入即报、commit 折返归零 |

**达成形态（验收口径）**：4 个问题各自闭环——① retries 与门槛失败事件（评审 rejected / P5→P4 回退 / 子代理空返回）对应性校验落地，空记录被阻断/高优 WARNING；② P8 gate 新增 roadmap done 反查校验 + RM-AG0032 历史数据补记为 done；③ test_bdd_14 根因定位（或本阶段交付复现定位计划+已知证据基线）+ 环境敏感测试集中清单 + CI flaky 自动重跑机制；④ P1/P2 声明写时即由 schema 校验，错误信息含具体行+修复提示，commit 时格式折返归零。

## 2. P0-brief 时效性质疑

**结论：已核对 P0-brief 时效性，无漂移。** 立项日 2026-08-23，今日 2026-08-24，间隔 1 天。逐条对照 P0 卡「时效性自检」严重判据：

1. `task` 目标方案是否仍成立 → **成立**。4 个 issue 与 retrospective-tag0019-21.md 的问题 10（retries）/机制触发核对清单/技术债登记核对清单（RM-AG0032 记录缺口）逐条一致；RM-AG0044 的 test_bdd_14 flaky 证据（roadmap.md L43，2026-08-23 当日实证）仍是最新状态，未被后续任务处理。
2. `executor_env` 平台前提是否仍成立 → **成立**。opencode / `has_task_tool: true` / `has_local_runtime: true` / `network: full` / `git: true` 均成立（本会话可读写 worktree、可跑 git）；`env_constraints`（`/tmp` 只读、ruff 0.16.4、pytest basetemp 约束）与 HANDOFF-TAG0023.md §4 验证命令一致，无冲突。
3. `known_risks`「已解决前提」是否变化 → **无变化**。SELF-GATE 触发面仍在（改动 check-gate.py/check-state-transition.py/P1/P2/P8 卡/check-debt.py/CI/测试）；RM-AG0032 状态未变（仍非 done，本 task 内待补记）；RM-AG0044 的 flaky 根因仍未定位（本阶段先复现定位再定 BDD，不盲改，符合已知风险声明）。

`[P0_STALE: 派发指引（P1-dispatch-context-analyst.md 第 37 行）给出的复盘文档路径为 /home/kity/oclab/dsw-workspace/agate-research/retrospective-tag0019-21.md（"dsw" 拼写），实际路径为 /home/kity/oclab/dsh-workspace/...（"dsh"，与 P0-brief 一致）——轻微漂移，属派发指引路径拼写误差，非 P0-brief 内容本身漂移；已用正确路径读取复盘文档并核实内容，不阻塞 P1]`

## 3. 隐含需求识别

逐维度快速过（本任务无数据/前端/多端的常规面，协议面隐含依赖密集）：

| # | 隐含需求 | 为什么必须 |
|---|---------|-----------|
| H1 | 本任务全部改动面触发 SELF-GATE | 改动面含 check-gate.py / check-state-transition.py / P1/P2/P8 卡 / check-debt.py / CI 配置 / 测试 → 后续每个含触发文件的 commit message 须含 `self-gate-review:` 路径或 `self-gate-skip:` 理由（HANDOFF §5 硬约束） |
| H2 | RM-AG0042 需先定义可机器判定的事件源，判定实现留 P2 | P0-brief known_risks 已列三类事件源（评审 status=rejected / P5→P4 回退证据 / subagent 空返回记录），P1 只把事件源判定规则转成 BDD 的 Given 前提（见 §6 BDD-1~3），避免"事件源怎么判"这个真正的设计问题被 P1 抢先拍板 |
| H3 | RM-AG0042 与 RM-AG0043 同触碰 check-gate.py 但分支不同 | 0042 的对应性校验落点可能在阶段级 gate 分支（P1/P2/P4 门槛处）、0043 的 roadmap 校验落点在 P8 分支——两者互不冲突但同文件多处改动，P4 需分批 commit（或至少不同改动块），避免同一文件多轮大改冲突（HANDOFF §7 已知风险；`implicit_coupling: true` 已在 frontmatter 声明）|
| H4 | RM-AG0043 需处理历史 RM 与多 RM 关联一个 task 的情况 | P0-brief known_risks 明示：历史 RM（done 但无 task 关联）与"多 RM 关联一个 task_id"的匹配规则留 P2 定义；P1 BDD（§6 BDD-5/6）只锚定"有关联必须 done / 无关联不误拦"两个边界，不预设匹配算法 |
| H5 | RM-AG0044 先复现定位根因再定 BDD，不盲改 | P0-brief known_risks 明示；本阶段已核实的证据基线（PR #188 同 commit push 过/pull_request 挂 + `check-debt.py._retreat_coverage()` 的 `full[:7]` 固定切片 vs 测试 fixture `git rev-parse --short HEAD` 动态长度的潜在 mismatch 候选机制）写入 §4.3 与 BDD-8，根因最终结论留 P2/P4 复现验证 |
| H6 | RM-AG0044 根治不得破坏测试平台无关原则 | agate 测试核心约定：不允许裸 `PATH=`/裸 `python3`/POSIX 假设/`/tmp` 等 Unix-only 路径；环境敏感测试判定标准与集中清单机制须在不引入新的单平台假设前提下设计 |
| H7 | RM-AG0045 的 schema 校验接入写路径需覆盖"生成器/编辑器/formatter 层"，不是 commit-time 校验的简单复制 | 若只是把 pre-commit gate 的校验逻辑原样搬到写时调用，等价于新增一次相同粒度的检查点，价值有限；P2 需设计"写入即触发"的具体挂载方式（如 agate 内部写文件工具封装、或独立 formatter 脚本） |
| H8 | 本任务 P6 验收须含 P6.5 judge 复核 | `.state.yaml` 已由主 Agent 写入 `judge.enabled: true`（本任务 P1 created 2026-08-24 ≥ `judge_required_since` 2026-08-22，`agate/rules/dispatch.yaml:17` 已核实取值，机制强制适用）；P1 无需重复声明该字段本身 |
| H9 | count-tests 只增不减（用例数冻结） | 仓库硬约定；RM-AG0042/43/44/45 均会新增测试或 gate 校验用例 |
| H10 | pytest 环境约束 | `/tmp` 只读 → 全量 pytest 须 `--basetemp=/home/kity/oclab/dsh-workspace/ptmp -p no:cacheprovider`；ruff 用 `~/.venvs/agate-dev/bin/ruff`（0.16.4 对齐 CI）；consistency 用 worktree 自己的脚本（双工作区纪律）|
| H11 | RM-AG0045 与 RM-0022（schema 基建）/RM-0038（check-gate YAML 迁移）联动 | P0-brief 原文明示关联；本任务不重做 RM-0022/0038 已完成的 M0-M3 基建，只在写路径接入既有 schema 能力（复用已有校验器，不新造一套 schema 语言）|
| H12 | RM-AG0042 的"高优 WARNING"与"阻断"两种校验强度均可能满足验收锚 | 参照 TAG0022 BDD-6 的先例（判据双路径可判），本 P1 的 BDD-1~3 不预设具体强度，由 P2 定案，只锚定"被拦截"这一可观测结果 |

## 4. 同类扫描结论（强制，3 组，均已执行）

> 每条命中标"本次处理 / 本次不处理 + 理由"；"已确认只此一处"也显式写出。原始记录见 P1-progress.md，结论落盘于本节。

### 4.1 扫描 1：grep `retries` 全部消费点

**统计**：全仓命中 **28 个文件**（协议/规则/文档面 7 + 生产脚本 6 + 测试面 15［14 个 `test_*.py` + `conftest.py`］），口径：`grep -rl "retries" --include="*.py" --include="*.md" agate/`，无排除项，逐条判定如下（上一轮误报 25，遗漏 `agate/rules/state-transitions.md`/`agate/tests/conftest.py`/`agate/phase-cards/P1-requirements.md` 三个文件，本轮已补全）：

| # | 命中文件 | 判定 |
|---|---------|------|
| 1 | `agate/scripts/check-state-transition.py`（L146-154，`retries_over` → `MAX_RETRY` 判定，调 `agate-state-get.py`） | **本次处理（RM-AG0042 核心消费点）**：现状只判定"超限→PAUSED"，无"失败事件↔retries 记录"对应性校验；本任务在此增加或新增独立校验点补足对应性 |
| 2 | `agate/scripts/agate-state-get.py`（`retries_over` 操作实现） | **本次处理**：`retries_over` 的读取逻辑是对应性校验复用的基础操作，不改语义，供新校验点调用 |
| 3 | `agate/scripts/agate-state-yaml-check.py`（`retries` 字段格式校验，`^P\d+$` key 校验） | **本次不处理**：只校验格式合法性（是否为合法 dict/list 结构），非对应性校验，职责不重叠，保留 |
| 4 | `agate/scripts/agate-retreat-state.py`（P5→P4 等回退操作实现） | **本次处理（事件源之一）**：回退动作发生点，是 BDD-2 的"回退证据"的候选判定来源之一，P2 需确认该脚本是否已留痕（如 commit message/`.gate-history.jsonl`），供对应性校验读取 |
| 5 | `agate/scripts/check-retrospective.py` | **本次不处理**：该脚本处理复盘阶段的 DEBT/roadmap 登记信号扫描（`_scan_debt_roadmap_signal`），与 retries 对应性校验是不同机制，不构成同类实现面 |
| 6 | `agate/scripts/check-protocol-consistency.py` | **本次不处理**：仅做协议文档间字段一致性核对，不涉及 retries 值本身的对应性判定 |
| 7 | `agate/rules/state-transitions.md`（L60「重试记录按阶段独立存储于 `.state.yaml` 的 `retries` 字段」+ L97「读 .state.yaml → 确认 phase + retries」） | **本次处理（文档面，权威规则来源，上一轮遗漏）**：定义 `retries` 字段权威语义与重试上限规则的协议规则文档，与 RM-AG0042 要修复的对象（`check-state-transition.py` 的 `retries_over`/`MAX_RETRY` 判定）直接同源；本任务新增的"门槛失败事件必须写 retries"强制表述需同步写入本文件，与下方 8/9 的 `state-machine.md`/`dispatch-protocol.md`/`WORKFLOW.md` 一并做措辞更新 |
| 8 | `agate/state-machine.md`（L420/454/489-490/589-594/688-714，retries 结构定义 + 主 Agent 写入规程） | **本次处理（文档面）**：现状明确"重试记录不能存在 LLM 记忆里，写进 `.state.yaml` 的 retries 字段"（L589）——但只是行为规程，无机械强制；本任务需在此补充"门槛失败事件必须写 retries"的强制表述，与 gate 校验联动 |
| 9 | `agate/dispatch-protocol.md` / `agate/WORKFLOW.md` | **本次处理（文档面，随 7/8 一并）**：P1/P2 卡须明确"评审被拒必须写 retries"（P0-brief 修复项②），归入此三文档相关小节的措辞更新 |
| 10 | `agate/phase-cards/P1-requirements.md`（L168/172，`retries[Pn]`/`retries[P5]` 占位，用于 verification_env 止损轮次预算说明的计数口径旁注） | **本次不处理（上一轮遗漏，本轮显式列出）**：仅提及"与阶段 `retries[Pn]` 独立计数"作止损轮次预算的计数口径说明，未涉及 RM-AG0042 对应性校验语义本身，不构成同类实现面 |
| 11 | `agate/scripts/README.md` / `agate/tests/README.md` | **本次不处理**：仅为脚本清单/测试说明文档，非消费点 |
| 12 | `agate/tests/conftest.py`（L95，共享 fixture `create_task_dir` 硬编码写入 `retries: {}`） | **本次处理（上一轮遗漏，本轮显式列出）**：本任务多处测试用内联覆写 `.state.yaml` 构造非空 retries 场景（如 `test_pre_commit_hook.py` L1127 `retries:\n  P2:\n    - round: 1\n      failure_mode: test`），而共享 helper `create_task_dir` 目前只能生成空 `retries: {}`；P3 新增 BDD-1~4 对应性校验用例大概率需要构造"有门槛失败事件但 retries 为空/非空"的多种 `.state.yaml`，届时或扩展本 helper 支持参数化 retries 内容，或继续沿用测试内联覆写——本节判定为"本次处理"，具体是否改动此文件留 P3 落地决定 |
| 13 | 测试文件（4 个，随 1/2/4 同步新增用例）：`test_check_state_transition.py`（对应 1）/`test_agate_state_get.py`（对应 2）/`test_agate_retreat_state.py`（对应 4）/`test_agate_retreat_to.py`（回退动作候选实现之一，BDD-2"回退证据判定来源"未定案前先随事件源候选一并标记，具体是否落点于此由 P2 定） | **本次处理（对应文件随生产代码同步新增用例，P3 落地）**：既有用例保持不动，新增对应性校验用例 |
| 14 | 测试文件（10 个，均只用 `retries: {}` 搭建 `.state.yaml` 前置场景，未测 retries 语义本身）：`test_agate_state_yaml_check.py`/`test_check_state_yaml.py`（对应 3，格式校验测试）/`test_check_retrospective.py`（对应 5）/`test_check_gate.py`（`check-gate.py` 生产源码本身不含 `retries` 字样，测试仅用 `retries: {}` 搭建 fixture）/`test_agate_scripts_encoding.py`（遍历脚本编码检测，`retries` 字样仅为被扫描内容之一）/`test_ci_gate_backstop.py`/`test_dispatch_context_card.py`/`test_dispatch_context_warning.py`/`test_pre_commit_hook.py`/`test_agate_migrate_workspace.py` | **本次不处理**：均为既有测试用 `retries: {}` 搭建前置 `.state.yaml` 样板场景的辅助代码，不测 retries 对应性语义本身，保留不动 |

**回归拦截声明**：对应性校验落地后，新任务门槛失败事件（评审 rejected / P5→P4 回退 / 子代理空返回）缺 retries 记录时被 gate 拦截/WARNING（转 BDD-1~4）；历史任务（机制前）不受影响（判定范围由 P2 定，若涉及历史任务豁免同样归入 P2 设计）。

### 4.2 扫描 2：grep `roadmap` 回写消费点

**统计**：`check-gate.py` 全文 grep `roadmap` 仅 1 处命中（L871，P4 门禁注释"roadmap 补 gap"，与 P8 无关）；确认现状 **P8 gate（`gate_p8`，L1181-1259）函数体内无任何 roadmap 读取**。全仓 `.py` 命中 5 个文件：

| # | 命中文件 | 判定 |
|---|---------|------|
| 1 | `agate/scripts/check-gate.py`（L871，P4 门禁注释） | **本次不处理**：与 roadmap 回写无关，仅注释提及"roadmap 补 gap"字样，命中但不构成同类问题 |
| 2 | `agate/scripts/check-gate.py`（`gate_p8` 函数体，L1181-1259） | **本次处理（RM-AG0043 核心落点）**：P8 gate 新增分支——按 task_id 反查 roadmap.md 关联 RM 条目，状态必须为 `done` |
| 3 | `agate/scripts/check-retrospective.py`（`_scan_debt_roadmap_signal`，L66，检测 DEBT/roadmap 登记信号，用于复盘归因提示） | **本次不处理**：这是复盘阶段的"提示是否登记过技术债/roadmap"信号扫描，与 P8 的"roadmap RM 状态是否为 done"是不同判定维度（一个问"登记了没"，一个问"状态对不对"），不构成同类实现，保留不动 |
| 4 | `agate/tests/unit/test_retrospective_protocol_docs.py` / `test_check_retrospective.py` | **本次不处理**：对应 check-retrospective.py 现状测试，不在本次改动面 |
| 5 | `agate/tests/unit/test_agate_debt_check.py` | **本次不处理**：DEBT 登记闭环测试，与 P8 roadmap done 校验是不同机制 |

**关键佐证**：`agate-workspace/roadmap/roadmap.md` 核实 RM-AG0032 两行（L30 `backlog`/L31 `scheduled`）均非 `done`，与 P0-brief 描述一致，确认记录缺口真实存在。

**回归拦截声明**：RM-AG0043 之后，新任务 P8 完成时若关联 RM 条目非 done → 被拦截（转 BDD-5）；无关联 RM 记录的任务不误拦（转 BDD-6）；RM-AG0032 历史数据独立手工补记（转 BDD-7）。

### 4.3 扫描 3：grep 环境敏感测试已知清单（test_bdd_7/25/14 + known-failures 登记机制）

**统计**：`known-failures`/`known_failures` 命中 9 个文件（生产脚本 2 + 测试 3 + 文档 2 + 编译缓存 1，缓存文件不计入判定）。

| # | 命中 | 判定 |
|---|---------|------|
| 1 | `agate/LIMITATIONS.md`（L45） | **本次不处理（既有基础设施，供复用）**：已有 P5 机械化回归判定机制——任务开始时快照全量测试失败列表（`pre-task-baseline.md`），P5 用 `comm` diff 两次快照，只在"任务后"新增失败即拦截，预存失败需登记 `known-failures.md`。这是"回归判定"机制，不是"环境敏感测试"专门分类清单——两者目的不同（前者判定新增回归，后者需要标注"哪些测试对环境敏感、敏感在什么维度"），确认**未见专门的环境敏感测试分类清单**，与 P0-brief 客观查证一致 |
| 2 | `agate/scripts/agate_common.py`（L815 注释 + L1016 计数函数） | **本次不处理**：`known-failures.md` 登记表条目计数函数，服务于 P5 回归判定机制，非环境敏感专门清单 |
| 3 | `agate/scripts/check-gate.py`（known-failures 相关引用） | **本次不处理**：同上机制的 gate 侧消费，非专门清单 |
| 4 | `agate/phase-cards/P5-verification.md` | **本次不处理**：P5 卡片对既有回归判定机制的条文说明，非本次改动对象 |
| 5 | `agate/tests/unit/test_md_parse_scan.py` / `test_env_adapt_docs.py` / `test_check_gate_p5_diff.py` | **本次不处理**：既有回归判定机制的测试，保留 |

**test_bdd_7 / test_bdd_25**（RM-AG0041，TAG0022 已处理）：basetemp 位置依赖类根因，已根治（探测 git 上下文/强制仓库外 basetemp）。**本次不处理**：不属于本任务改动面，仅作为"环境敏感测试"分类的既有实例，纳入本任务新建集中清单时登记（历史条目）。

**test_bdd_14**（RM-AG0044 本次新例，`agate/tests/unit/test_agate_debt_check.py::test_bdd_14_retreat_entry_present_no_warning`，对应 `check-debt.py --retreat-coverage`）：**本次处理（核心对象）**。已知证据基线（本阶段核实，详见 §6 BDD-8）：

1. roadmap.md（L43）实证记录：PR #188 同 commit 双 CI run 一过一挂——push 事件通过，pull_request 事件挂（`GATE DEBT WARNING` 断言失败），重跑即过，本地 3/3 过。
2. 代码走查发现候选机制：`agate/scripts/check-debt.py` 的 `_retreat_coverage()`（L48-81）用 `short = full[:7]`（固定 7 位前缀切片，L75）判定 retreat 提交是否已登记；而测试 fixture（`test_bdd_14`）用 `git_repo.git("rev-parse", "--short", "HEAD")` 生成登记用的 short hash（长度由 git `core.abbrev` 自动计算，非固定 7 位，理论上可受 repo 对象数量/git 版本/runner 全局配置影响而产生长度不一致）——两者 short hash 的长度来源不一致，构成一个可复现的潜在 mismatch 机制，但尚未在本阶段完成多次 CI 触发观测以确认这就是唯一/主要根因（P0-brief known_risks 已声明"先复现定位根因再定 BDD，不盲改"，故本阶段不据此下最终结论）。

**回归拦截声明**：RM-AG0044 之后，环境敏感测试统一登记进新建集中清单（含判定标准字段），新增判定标准之外的测试若被发现环境敏感需登记同一清单（转 BDD-10）；CI flaky 通过自动重跑机制兜底（触发条件由 P2 定，转 BDD-8/9）。

## 5. 范围声明与关键决策

**范围（`packages: [agate]` 的 4 子项改动面）**：

| 子项 | 改动面（P0-brief 声明） | 归属阶段 |
|------|------------------------|---------|
| RM-AG0042 | check-state-transition.py（或独立校验脚本）新增对应性校验 + state-machine.md/dispatch-protocol.md/WORKFLOW.md 措辞明确 + P1/P2 卡说明 | P2 设计事件源判定规则 / P3 测试 / P4 实现 |
| RM-AG0043 | check-gate.py `gate_p8` 新增 roadmap 校验分支 + roadmap.md 手工补记 RM-AG0032 → done | P2 设计匹配规则 / P3 测试 / P4 实现（与 0042 分批 commit，见 H3）|
| RM-AG0044 | check-debt.py `_retreat_coverage()` 排查 + 环境敏感测试判定标准 + 集中清单 + CI flaky 自动重跑机制 | P2 复现验证与设计 / P3 测试 / P4 实现 |
| RM-AG0045 | 声明写路径（生成器/编辑器/formatter 层）接入 schema 校验 + 错误信息定位与修复提示 | P2 设计写路径挂载方式 / P3 测试 / P4 实现 |

**关键决策（本 P1 基线内定案，无需人工介入）**：

- **D1（RM-AG0042 校验强度）**：BDD-1~3 不预设"阻断"或"高优 WARNING"，两种实现路径均满足"被拦截"锚点，具体强度由 P2 定案（同 TAG0022 BDD-6 先例）。`[SUGGEST: D1]`
- **D2（RM-AG0043 历史/多关联匹配规则）**：P1 只锚定两个边界——有关联必须 done（BDD-5）、无关联不误拦（BDD-6）；"多 RM 关联一个 task_id"与"历史 RM 无 task 关联"的具体匹配算法留 P2 设计。`[SUGGEST: D2]`
- **D3（RM-AG0044 根因交付形态）**：本阶段无法在 P1 内完成多次 CI 触发观测复现，按 P1 卡片约定交付"复现定位计划 + 已知证据基线"（BDD-8）；根因最终结论与修复实现留 P2/P4，`test_bdd_14` 连续 5 次 CI 稳定（BDD-9）与集中清单（BDD-10）是最终验收锚。`[SUGGEST: D3]`
- **D4（0042/0043 同簇分批纪律）**：两者都可能触碰 check-gate.py（0042 落点更可能在阶段级门槛分支或独立脚本，0043 落点在 `gate_p8`），P4 分批 commit 或至少不同改动块，避免同一文件多轮大改（HANDOFF §7 已知风险，H3）。`[SUGGEST: D4]`
- **D5（RM-AG0045 写路径载体）**：P1 不预设写路径的具体技术形式（是否新增独立 formatter 脚本、还是复用现有 schema 校验器插入写钩子），由 P2 设计候选方案与权衡。`[SUGGEST: D5]`

> 本节约束为范围/边界决策，不涉及具体实现方案（候选方案与机制设计留 P2 architect）。

## 6. BDD 验收条件

> 编号连续 BDD-1..BDD-13，按 4 子项 + 1 历史补记分组。每条独立可二值判定（PASS/FAIL），Given/When/Then 不绑定实现符号，判定实现细节（事件源具体来源/匹配算法/写路径载体/校验强度）留 P2，本阶段只锚定可观测结果。

### 6.1 RM-AG0042 门槛失败事件强制记录 retries

#### BDD-1: 评审 rejected 类门槛失败事件缺失对应 retries 记录时被拦截
- Given 任务某阶段的评审产出文件（如 requirements-review.md / plan-eng-review.md）状态字段为 `status: rejected`，且 `.state.yaml` 该阶段 `retries[Pn]` 为空列表或缺失该阶段键
- When 运行对应性校验（校验点由 P2 落位，可能在 check-state-transition.py 或独立脚本）
- Then 校验以非 0 退出码（阻断）或高优先级 WARNING 输出提示"评审 rejected 但 retries 无对应记录"（两种拦截强度实现路径均满足本条锚点，具体强度由 P2 定案，见 §5 D1）；`.state.yaml` 含对应 retries 记录时，同一输入 → 校验通过

#### BDD-2: P5→P4 回退类门槛失败事件缺失对应 retries 记录时被拦截
- Given `.state.yaml` 的 phase 变更历史记录了一次从 P5 回退到 P4（回退证据的具体判定来源——如 `.gate-history.jsonl` 或 phase 序列——由 P2 落位），且对应阶段 `retries[P4]` 为空
- When 运行对应性校验
- Then 同 BDD-1 判据：无对应 retries 记录 → 拦截/WARNING；有对应记录 → 通过

#### BDD-3: 子代理空返回重派类门槛失败事件缺失对应 retries 记录时被拦截
- Given 任务的 progress/dispatch 记录（判定来源由 P2 落位）显示某阶段发生过子代理空返回重派，且该阶段 `retries[Pn]` 无对应记录
- When 运行对应性校验
- Then 同 BDD-1 判据：无对应记录 → 拦截/WARNING；有对应记录 → 通过

#### BDD-4: 正常路径不受影响（回归防呆）
- Given 某阶段既无评审 rejected、无 P5→P4 回退、无子代理空返回重派（无门槛失败事件），且 `retries[Pn]` 为空或缺失
- When 运行对应性校验
- Then 校验通过（exit 0，无 WARNING）——空 retries 本身不是错误，只有"失败事件存在而 retries 为空"的对应性缺口才被拦截

### 6.2 RM-AG0043 P8 roadmap 回写 done 校验（含历史补记）

#### BDD-5: P8 完成时关联 roadmap RM 条目未回写 done 被拦截
- Given 任务 `.state.yaml` 的 `task_id` 在 `roadmap.md` 中能反查到至少一条关联 RM 记录（关联字段含该 task_id），且该 RM 记录状态非 `done`
- When 运行 P8 gate 校验（`check-gate.py` `gate_p8` 新增分支）
- Then 非 0 退出（阻断），提示对应 RM 编号与当前状态；全部关联 RM 记录状态均为 `done` 时 → exit 0（放行）

#### BDD-6: 无关联 RM 记录时不误拦（回归防呆）
- Given 任务 `.state.yaml` 的 `task_id` 在 `roadmap.md` 中查不到任何关联 RM 记录
- When 运行 P8 gate 校验
- Then exit 0（不误拦无关联任务）

#### BDD-7: RM-AG0032 历史数据补记为 done（独立 BDD，历史修正）
- Given `roadmap.md` 当前 RM-AG0032 两行状态分别为 `backlog`（L30）/`scheduled`（L31），无 `done` 行，而 v0.59.0 已发布且 PR #184 已合并（独立 Judge 机制已交付）
- When 主 Agent 在 `roadmap.md` 补记一行 RM-AG0032 记录，状态字段为 `done`
- Then `roadmap.md` 中存在至少一行 RM-AG0032 记录，其状态字段值为 `done`；缺失该行 → FAIL

### 6.3 RM-AG0044 环境敏感测试集中治理

#### BDD-8: 复现定位计划 + 已知证据基线落盘（本阶段交付锚，根因结论留 P2/P4）
- Given 本阶段已核实的证据基线：① `roadmap.md`（L43）记录的 PR #188 同 commit 双 CI run 一过一挂（push 事件通过 / pull_request 事件挂：`test_bdd_14_retreat_entry_present_no_warning` 的 `GATE DEBT WARNING` 断言失败）② 代码走查候选机制：`check-debt.py._retreat_coverage()`（L75）用 `full[:7]` 固定 7 位前缀切片，测试 fixture 用 `git rev-parse --short HEAD`（长度由 git `core.abbrev` 自动计算，非固定 7 位）——两者 short hash 长度来源不一致
- When P2/P4 交付物（P2-design.md 或独立附件）核对是否含以下四要素：①已知证据基线（同上两点原样引用或补充）②环境敏感测试判定标准（如何界定一个测试属于"环境敏感"）③集中清单文件的位置与登记格式 ④CI flaky 自动重跑机制的触发条件
- Then 四要素全部落盘且各自可核对存在性，缺任一 → FAIL；根因最终结论（候选机制是否即为主因）在 P2/P4 完成复现验证后定案，不在本 BDD 判定范围内

#### BDD-9: test_bdd_14 连续 5 次 CI 稳定（最终验收锚）
- Given RM-AG0044 修复实现完成（根因修复方案已实施）
- When 连续触发 5 次 CI（`protocol-tests.yml`，同一 commit 或等价改动内容）
- Then 5 次 run 中 `test_bdd_14_retreat_entry_present_no_warning` 均通过；任一次失败 → FAIL

#### BDD-10: 环境敏感测试集中清单存在（回归拦截）
- Given RM-AG0044 修复完成
- When 检查约定位置（P2 定案的清单文件路径）
- Then 清单文件存在且至少含 `test_bdd_7`、`test_bdd_25`、`test_bdd_14` 三条目（各含根因分类字段）；缺任一条目 → FAIL

### 6.4 RM-AG0045 声明写时校验

#### BDD-11: 声明格式错误在写入时即报（而非等 commit 时才暴露）
- Given 使用声明写入路径（P1/P2 声明的生成/编辑载体，具体形式由 P2 设计）写入一条非法声明（如 `coupling_checklist` 使用全角冒号、或 `phases` 值非法列表格式）
- When 触发写时 schema 校验
- Then 写入动作当次即产生校验错误提示（无需等到 git commit 触发 pre-commit gate 才发现）；写入合法声明时无错误提示

#### BDD-12: 错误信息含具体行号 + 修复提示
- Given 写时 schema 校验捕获一条非法声明
- When 输出校验错误信息
- Then 错误信息包含具体行号（或字段名定位）与修复建议文本；仅报"格式错误"而无定位信息 → FAIL

#### BDD-13: commit 时格式折返归零（同批已知用例验证）
- Given TAG0019 实际触发过 commit 时格式折返的 3 类声明用例（`coupling_checklist` 流式声明错误 / 半角冒号错误 / 源码数 6>5 计数错误）
- When 分别过写时 schema 校验
- Then 全部 3 类在写时即被拦截报错；同一批用例过 commit 阶段的 pre-commit gate 时，不再产生"格式类"的新拦截（因为非法内容已在写时被阻止，未曾落盘）

> 说明：本条 Given 合并了 3 类历史已知错误用例，是**有意的批量回归校验**（三者同属 TAG0019 一次实证中暴露的"commit 时才发现格式错误"根因，验收时天然需要同批次核对是否都已在写时拦截、不留死角），不是遗漏拆分；判定仍是单一二值结果（3 类全部写时拦截才 PASS，任一类漏判即 FAIL），不引入中间态。

## 7. 待确认清单与提案

`[NO_NEED_CONFIRM]` —— 无待确认项。所有方向性选择均已由 P0-brief / 派发指引 / 客观查证定案，倾向项以下列 `[SUGGEST]` 形式留审计痕迹（主 Agent 无异议即采纳，均不阻塞推进）：

- `[SUGGEST: D1 —— RM-AG0042 校验强度（阻断 vs 高优 WARNING）由 P2 定案，BDD-1~3 以"被拦截"为锚双路径可判]`
- `[SUGGEST: D2 —— RM-AG0043 历史 RM/多关联匹配算法留 P2 设计，P1 只锚定"有关联必须 done / 无关联不误拦"两个边界]`
- `[SUGGEST: D3 —— RM-AG0044 本阶段交付"复现定位计划 + 已知证据基线"（BDD-8），根因结论与修复留 P2/P4，最终验收锚为 BDD-9/10]`
- `[SUGGEST: D4 —— RM-AG0042/0043 同触碰 check-gate.py 但分支不同，P4 分批 commit 或不同改动块错开]`
- `[SUGGEST: D5 —— RM-AG0045 写路径的具体技术载体（独立 formatter / 复用现有校验器插入写钩子）由 P2 设计候选方案与权衡]`

本文件不含 GAP 状态声明（不存在任何状态为 GAP 的能力条目，三态明细见 §9）；无未决 NEED_CONFIRM 项（已声明 `[NO_NEED_CONFIRM]`）。

## 8. 裁剪说明

`phases: [P1, P2, P3, P4, P5, P6, P7, P8]` —— **全阶段保留，无跳过**。逐阶段理由：

| 阶段 | 保留理由 |
|------|---------|
| P1 | 不可裁（核心阶段）——本文件 |
| P2 | 不可裁：RM-AG0042 事件源判定规则、RM-AG0043 匹配规则、RM-AG0044 复现验证与根因设计、RM-AG0045 写路径载体设计均需候选方案与评审（`risk_level: high` → plan-eng-review 经 C8 强制）|
| P3 | 不可裁：4 子项均可写失败测试（TDD 先红后绿），尤其 RM-AG0044 需先固化 flaky 复现测试 |
| P4 | 实现：4 子项分批 commit（0042/0043 错开 check-gate.py 改动块，见 §5 D4）|
| P5 | 验证：pytest 全绿 + consistency 0 ERROR + ruff 全绿 + count-tests 不漂移（BDD-4/6/9 相关回归验证）|
| P6 | 验收：逐条实跑 BDD-1..13；本任务 domains 不含 frontend，无 UI/视觉证据需求；**须含 P6.5 judge 复核**（`judge.enabled: true` 已写入，H8）|
| P7 | 一致性：改动横跨 check-gate.py / check-state-transition.py / check-debt.py / P1/P2/P8 卡 / state-machine.md / 测试，跨文件交叉核对必要，尤其 0042/0043 同文件不同分支的一致性 |
| P8 | 发布：roadmap 回写 RM-AG0042~0044 → done（含 RM-AG0032 历史补记，BDD-7）；SELF-GATE review；版本引用文件清单 |

不裁理由总述：改动面大（gate 逻辑/状态机/CI/测试卫生四域）+ 同簇互扰（0042/0043 同文件不同分支）+ 工具链自举风险（用未发布的新 gate 判自己），每一阶段 gate 都是兜底闸，不可省。`ceremony: standard`（fail-closed，不声明薄化）——本任务非 thin 候选。

## 9. 能力需求声明与能力自查

**能力自查结论**：本任务为纯协议/脚本/CI/测试类（无 UI 截图、无视觉验收），不涉及视觉能力，无需 `[CAPABILITY_GAP]` 声明，不需 vision 能力条目（P1 卡视觉硬要求仅当 `domains` 含 frontend 时触发，本任务 `domains: [backend]`）。

```yaml
capability_requirements:
  - need: text-analysis-scanning
    why: P1 三组同类扫描（retries/roadmap/环境敏感测试消费点）与 P2-P5 迁移期静态审计（grep/read/glob 大范围、正则模式核对）
    available:
      - "read/grep/glob 工具（独立通道，不占 bash）"
      - "python3 + pyyaml + pytest"
    status: available
  - need: git-log-forensics
    why: RM-AG0044 根因定位需比对 git 提交历史、short hash 长度、CI run 差异（push vs pull_request 事件）
    available:
      - "git CLI（本地仓库只读比对）"
      - "roadmap.md L43 已记录的 PR #188 双 run 实证数据（供 P2/P4 复现验证起点）"
    status: available
  - need: python-testing-and-lint
    why: P3-P6 全量 pytest + ruff 静态检查 + consistency/structure gate（--basetemp 可写目录约束）
    available:
      - "系统 python3 + pytest（/tmp 只读 → --basetemp=/home/kity/oclab/dsh-workspace/ptmp -p no:cacheprovider）"
      - "~/.venvs/agate-dev/bin/ruff（0.16.4 对齐 CI）"
      - "worktree 可写（.worktrees/agate-TAG0023，含 agate-workspace）"
    status: available
  - need: protocol-editing
    why: 产出 P1 基线及后续阶段产出需编辑协议本体 markdown / 脚本源码
    available:
      - "worktree 可写；双工作区纪律（只改 worktree，禁止改动主 checkout 与 ~/.agate）"
    status: available
```

无 supplementable、无 GAP。

**verification_env 声明（RM-AG0044 CI 多次触发观测，环境问题非能力问题，判断树：换谁来做都得先有 GitHub Actions 实际运行环境才能观测 flaky 现象）**：

```yaml
verification_env: "GitHub Actions CI（protocol-tests.yml，push/pull_request 双事件触发），用于 RM-AG0044 test_bdd_14 flaky 复现定位与 BDD-9 的连续 5 次稳定性验收"
verification_env_budget: "止损轮次 2（独立计数，不占 retries[P5]）；轮次追踪由主 Agent 在 dispatch-context 记录当前第几轮 + 历次已排除假设"
```

RM-AG0042/0043/0045 无 verification_env 依赖（测试命令 pytest/consistency/ruff/count-tests 均为主 Agent 标准操作可准备，本地可完成全部验证）。

## 10. 下游影响

- **P2**：依赖 `risk_level: high`（plan-eng-review 经 C8 机械映射强制）+ `domains: [backend]` 决定评审角色；`packages: [agate]` 作方案范围；§4 三组扫描清单作迁移映射/影响面输入（D1-D5）；§5 范围表作分批 commit 骨架；`verification_env` 声明供 P2/P5 复现验证轮次规划起点。
- **P6**：逐条对照 BDD-1..13（PASS/FAIL 总数 ≥ 13）；无 UI 证据需求（domains 不含 frontend）；**P6.5 judge 复核强制**（H8，`.state.yaml` 已写入 `judge.enabled: true`）。
- **P7**：`packages: [agate]` 做跨文件一致性核对；4 子项改动面文件清单做交叉引用检查（check-gate.py 的 0042/0043 不同分支一致性尤为关键）。
- **P8**：roadmap 回写 RM-AG0042~0044 → done（含 RM-AG0032 历史补记，BDD-7）；SELF-GATE review；版本引用文件清单。
- **基线保护**：本文件为需求基线，后续阶段如需变更按 P1 卡「P1 基线保护」流程（主 Agent 显式批准 + `[BASELINE_CHANGE: 理由]`，不改 BDD 的 Given/When/Then 语义）。
