---
phase: P1
task_id: TAG0020-independent-judge
type: problems
parent: P0-brief.md
trace_id: TAG0020-P1-20260822
status: draft
created: 2026-08-22
agent: analyst
risk_level: medium
phases: [P1, P2, P3, P4, P5, P6, P7, P8]
packages: [agate]
domains: [backend]
capability_requirements: []
---

# P1 需求基线 — 独立 Judge 机制（RM-AG0032）

[NO_NEED_CONFIRM]

> 本文件是 TAG0020 的需求基线（活基线，后续阶段以 `[SCOPE+]` 回写）。任务：P6.5 新增验收独立裁判（judge），解决 `LIMITATIONS.md` 局限 3 的 self-authored gate 弱点。

## 1. 需求复述

TAG0020（RM-AG0032，P0-brief 已锁定，设计文档 `design-independent-judge.md` 为分析基础）要在 agate 协议中新增 **P6.5 独立 Judge 机制**：

- **新增评审角色 `judge`**（`assets/review-roles/judge.md`）：在 P6 验收之后、P7 一致性之前（阶段编号 **P6.5**）以 **fresh context** 只凭标准（P1 BDD + P2 验收设计）逐条重验**所有** BDD（含 P6 已判 PASS 项），只信证据文件与 git log，不信实现者自述。
- **三层防造假**：① 信息隔离白名单（judge 的 dispatch-context 仅允许白名单输入、禁含黑名单路径引用集——`P6-acceptance.md` 等 verifier/implementer 自述与派发上下文文件，`check-judge-verdict.py` 机械校验，锚点见 BDD-4）② 证据交叉核对（BDD 计数对照 / 证据引用存在性 / md5 去重 / 执行留痕 / git 留痕）③ append-only 事件账本 `gate-events.jsonl`（行间哈希链防改写，`check-events.py` 审计）。
- **三档预算**：轮次 ≤ 2 / token 100k（`judge_token_budget` 可覆盖）/ 时间 30 min；超限诚实降级 `partial: true` 判 `needs-revision`，不静默放行。
- **挂靠现有机制**：status 门槛映射沿用（`passed → approved` / `needs-revision → needs-revision` / `rejected → rejected`）、dispatch-prompt 模板、专家组机制——零新架构。
- **设计红线**：不引入"LLM 当 gate 主判据"——judge 的 verdict 叠加机械核对，**exit code 才是门槛**（agate 哲学红线）。
- **历史兼容**：旧任务无 judge 字段 → P6.5 gate 跳过（只对新任务生效，存量不挂）。

交付物主体（M1-M2）：新角色 `judge.md`；新脚本 `check-judge-verdict.py` / `check-events.py`；`agate_common.py` 新增 `append_event()` / `read_judge_verdict()`；`check-gate.py` 增加 P6.5 分支；`WORKFLOW.md` / `state-machine.md`（P6.5 转移 + 重试表）/ `dispatch-protocol.md`（信息隔离节）/ `phase-cards/P6-acceptance.md`（P6.5 门槛）/ `assets/templates/dispatch-prompt.md`（Judge 追加节）同步更新；新增测试 `test_check_judge_verdict.py` / `test_check_events.py` + 回归用例。

## 2. P0-brief 时效性质疑

**已核对 P0-brief 时效性，无漂移。** 核对记录：

1. **`task` 目标方案成立性**：设计文档 `/home/kity/oclab/dsh-workspace/agate-research/design-independent-judge.md` 就绪且内容与 P0-brief 描述一致（角色设计 / 三层防造假 / 预算 / 状态机 P6→P6.5→P7 / §7 文件改动清单 / oh-my-agent 对标）。任务目标方案未变。
2. **`executor_env` 平台前提**：opencode + task 工具 + 本地运行时 + 网络 + git 均满足（本次 P1 即以 subagent 派发执行，TAG0019 的 gate 链在 worktree 可用）。平台前提成立。
3. **`known_risks` 前提（联动背景 TAG0019）**：P0-brief issue 7 依赖"TAG0019 风险分路由（thin 档）已合并"——已用 git log 实测验证：worktree HEAD 首提交 `4604836 "merge: 同步 main（TAG0019 v0.58.0）进 TAG0020"`，v0.58.0 含 `check-routing.py` / `agate-risk-score.py`（thin 档四要素校验），与本任务"thin 档跳过 LLM 评审后 judge 为质量兜底"的联动前提一致。
4. **P0-brief 四字段齐全**：task / issues / known_risks / executor_env + env_constraints 均在，无缺字段。

无 `[P0_STALE]` 标记，继续 P1。

## 3. 隐含需求识别

逐维度过一遍（analyst 认知模式——用户没说但技术上必须做）：

| 维度 | 隐含需求 | 为什么必须 |
|------|---------|-----------|
| 同类/影响面 | P6.5 挂载须与既有 phase 校验体系兼容（`agate-state-yaml-check.py` 的 `valid_phases` 无 "P6.5"、`check-state-transition.py` 的 `_DEFAULT_MAX_RETRY_MAP` / `_PHASE_OUTPUTS` 无 P6.5、`agate-next-card.py` / `agate-render-dispatch-prompt.py` 的 PHASE 枚举仅 P0-P8） | 不处理则 P6.5 阶段产物 commit 会被 hook/校验拦截或无法派发（详见第 4 节同类扫描命中清单） |
| 数据 | `gate-events.jsonl` 是新增数据文件；首行事件、空文件、历史任务缺失该文件均为合法态 | 校验须定义边界态（空链合法、无账本的任务跳过），否则存量任务/首次运行误报 |
| 前端 | 无 UI 变化（纯协议/脚本/文档任务，`domains: backend`，不声明 `ui_render_shape`） | — |
| 多端 | ① `pre-commit-gate.py` / `ci-gate-backstop.py` 的 gate 调度链需扩展（P6.5 阶段调用 check-judge-verdict + check-events，与现 P6 provenance 调用并列）② `role-system.md` 评审角色清单与 C8 映射说明需登记 judge（设计文档 §7 未列 role-system.md，挂靠机制要求）③ `dispatch-prompt.md` 模板需加 Judge 追加节 | 不扩展调度链则 hook 不执行 P6.5 校验，"gate 硬边界"落空；不登记角色则角色体系文档与实现脱节 |
| 边界 | 预算超限（轮次/token/时间）、verdict 字段缺失、partial 降级、criteria 计数不符、证据引用缺失——全部必须机器可判定且 fail-closed | 这些正是防造假机制要拦的漂移场景，BDD 须覆盖 |
| 兼容 | ① 历史任务无 judge 字段 → 跳过 ② 现有 P6 七道审计（审计 1-7，check-p6-provenance）行为不回归 ③ 既有 check-gate P0-P8 分支不破坏 | P0-brief known_risks 明示"存量任务全挂"是必须避免的回归 |

另有两项倾向性建议（不阻塞推进，主 Agent 可径自采纳）：

- `[SUGGEST: LIMITATIONS.md 局限 3 节"现状"段追加 judge 机制引用——机制落地后将其"self-authored gate 只能缓解无法根治"的现状描述更新为引用 P6.5 judge 独立复核，理由：协议文档与已实现机制同步，防 P7 一致性/文档自洽漂移]`
- `[SUGGEST: P6.5 挂载优先采用"P6 门槛内嵌强制判定 + retries.P6.5 独立计数"（不把 P6.5 写入 .state.yaml 的 phase 值），理由：避免扩展 valid_phases/回退表/卡片枚举的连锁改动面；是否采纳属 P2 设计决策，本建议仅供 architect 参考]`

## 4. 同类扫描结论（强制节）

> 扫描对象 = worktree 仓库本体 `/home/kity/oclab/agate/.worktrees/agate-TAG0020`（已含 TAG0019 v0.58.0 合并内容），grep 工具执行，命中数量 + 文件清单 + 逐条判定如下。

### 4.1 组 1：review-roles 现状与 status 门槛映射（judge 如何挂靠）

**命中数量**：10 个评审角色文件 + 2 处 status 映射表权威源 + 1 处评审迭代表 + 1 处 C8 机械映射表。

文件清单与逐条判定：

| 命中 | 判定 |
|------|------|
| `agate/assets/review-roles/` 共 10 文件：cso / design-review / investigate / plan-ceo-review / plan-design-review / plan-eng-review / protocol-alignment-review / qa / review / requirements-review | **本次处理**：新增 `judge.md` 成为第 11 个；frontmatter 沿用统一模式（`role_id: judge` / `type: review` / `phases: [P6.5]` / `agent: judge`） |
| `agate/role-system.md` L108-116（评审结论 → status 三值映射表：approved / rejected / needs-revision） | **本次处理**：judge verdict 的 `passed/rejected/needs-revision` 复用同一映射（`passed → approved`，`needs-revision` 计入重试）；judge 是"所有任务强制"的常态门槛评审，插入点固定为 P6 之后，**不进 C8 表**（C8 表 L52-66 按 domain/risk 触发，与"强制所有任务"语义不同；在 WORKFLOW.md 阶段总览 P6.5 行声明"评审角色 judge（强制）"） |
| `agate/rules/review-mapping.md` L38-42（评审产出统一 status 字段表） | **本次处理**：judge verdict 文件 Header 的 `status` 遵守同一规范，供主 Agent 只读 status 判定 |
| `agate/dispatch-protocol.md` L575-577（P1/P2/P4 评审迭代表） | **本次处理**：增加 P6.5 行（judge 复核 → needs-revision → verifier 修订 → 再复核，计入 P6.5 retry 预算 ≤2 轮） |
| 各评审角色文件尾统一"返回给主 Agent 时同时报告 File + Status"句 | **本次处理**：judge.md 沿用该报告约定 |
| `agate/role-system.md` 第二层评审角色清单（L37 起）+ `agate/AGENTS.md` 角色文件清单 | **本次处理**：两份角色清单均登记 `judge.md`（隐含需求，见第 3 节多端维度） |

结论：judge 全部挂靠在既有评审机制上，无新建架构；需新增的仅 4 类触点（角色文件 / status 映射复用 / 迭代表加行 / 角色清单登记）。

### 4.2 组 2：dispatch-context 现有注入内容 → 信息隔离白名单反推

**命中数量**：1 个 dispatch-context 模板 + 3 个注入/校验脚本 + 1 处既有内容约束先例。

文件清单与逐条判定：

| 命中 | 判定 |
|------|------|
| `agate/assets/templates/dispatch-context.md`（frontmatter + dispatch_guide 目标/约束/上游关联/输入文件 + AGATE_CARD 注入块 + objective_info 环境状态/关键标识/查证结果） | **本次处理**：白名单反推的基准——judge 的 dispatch-context 只允许含白名单输入文件路径与标准描述；`objective_info` 的"查证结果"节不得含验收结论叙述 |
| `agate/scripts/pre-commit-gate.py`（2p：各阶段强制 dispatch-context 存在 + 嵌入卡片 hash 校验，L350-397） | **本次处理**：P6.5 阶段同样强制 `P6.5-dispatch-context-*.md` 存在；judge 派发沿用同一机制 |
| `agate/scripts/agate-inject-card.py` / `agate-card-inject.py`（AGATE_CARD 注入） | **本次处理**：judge 的 dispatch-context 也含 AGATE_CARD 块——白名单校验须排除该块（复用审计 2 的 AGATE_CARD 排除逻辑，见下） |
| `agate/scripts/agate-extract-context.py`（从上游产出提取结构化字段注入 dispatch-context 上游关联节） | **本次处理**：P6.5 的上游是 P6 验收——extract 注入会带 verifier 产出摘要 → **judge 派发禁用该注入**或净化为"仅注入文件路径不含结论"（P2 设计定型）；这是"上游关联"注入面的主要防泄漏点 |
| `agate/scripts/check-p6-provenance.py` 审计 2（L318-355：扫描 `P6-dispatch-context-*.md` 禁含行首 `- PASS|FAIL` 验收结论预判，排除 AGATE_CARD 块 + frontmatter） | **本次处理**：这是信息隔离白名单校验的**直接先例**——P6.5 扩展同款扫描到 judge 的 dispatch-context，并加"黑名单路径引用集"禁引项（`P6-acceptance.md` / `P4·P5·P6-dispatch-context-*.md` 等，权威定义见下方结论表与 BDD-4）；既有审计 2 不动（P6 行为不回归） |

**白名单反推结论**（反向推导出的禁入/准入项——黑名单路径引用集同时是 BDD-4 机械判定的**权威定义**，禁入项在 P1 全部固化、不在 P2 再议；P2 只负责 check-judge-verdict.py 的扫描实现与黑名单 schema 的机器化落地）：

| 类别 | 项 | 机械判定方式 |
|------|----|-------------|
| 黑名单（自述文件路径） | `P6-acceptance.md` / `P6-dispatch-context-*.md` / `P5-dispatch-context-*.md` / `P4-dispatch-context-*.md` / `P4-implementation.md` / `P4-review.md` / `P5-test-results/`（verifier/implementer 自述、其派发上下文、实现与验收产出） | 字符串/正则匹配路径引用（扫描 judge dispatch-context 的『输入文件』与『上游关联』两节） |
| 黑名单语义（禁注入） | 『上游关联』节禁注入 verifier 产出结论——`agate-extract-context.py` 注入在 P6.5 禁用或净化为仅白名单路径；主 Agent 派发时同样不得传入 | 主 Agent 派发约定 + 两节扫描兜底（BDD-4 且句） |
| 黑名单（继承先例） | 行首 `- PASS|FAIL` 验收结论预判 | 正则 `^\s*- (PASS|FAIL)\b`（继承审计 2，全文扫描排除 AGATE_CARD/frontmatter） |
| 白名单（准入） | `P1-requirements.md`（BDD 标准）/ `P2-design.md`（仅验收相关节）/ `P6-evidence/` 目录 / `.state.yaml` / `gate-events.jsonl`，外加 git log 查询权；judge 自身产出声明 `P6.5-judge-verdict.md` 允许出现 | 白名单外任务文件路径引用即违规 |

### 4.3 组 3：check-p6-provenance 七道审计（审计 1-7）与事件账本交集

**命中数量**：1 个审计脚本（七道审计）+ 2 个联动脚本（check-p6-evidence / agate-evidence-consistency）。

文件清单与逐条判定：

| 命中 | 判定 |
|------|------|
| `agate/scripts/check-p6-provenance.py`（审计 1 证据-结论对应 / 审计 2 dispatch-context 内容约束 / 审计 3 BDD 总数对照 / 审计 4 vision YAML / 审计 5 日志 EXIT_CODE 一致性 / 审计 6 evidence JSON 一致性 / 审计 7 P5 证据复用） | **本次处理**（交集分析）：① 审计 3 的 BDD 计数口径（P1 `#### BDD-NN:` 标题数 vs P6 声明数）→ judge 的 `criteria_total` 复用同一口径 ② 审计 1 的证据存在性/引用逻辑 → `check-judge-verdict.py` 复用（可调 check-p6-evidence 或同款实现）③ 审计 5 消费 `P6-evidence/*.log` 的 `EXIT_CODE` 尾行 → 账本 `gate_run` 事件同记 exit code，**同源不同层**：账本 = 全阶段统一事件源 + 哈希链防改写，审计 5 = P6 证据目录内文件约定；两者不冲突、不互相替代，P2 需设计字段交集（事件 schema 含 `event`/`phase`/`cmd`/`exit`/`runner`） ④ 审计 7 消费 `.state.yaml` 的 `p5_pass_commit` → 账本 `state_transition` 事件与 `.state.yaml` 状态**双写**，同步语义（事件写入时机/谁写）由 P2 定义，`.state.yaml` 仍为权威状态源 ⑤ 哈希链 + 时间戳单调为账本独有能力，审计 1-7 无此机制 → 无冲突，是新增防线 |
| `agate/scripts/check-p6-evidence.py`（证据目录非空 / 截图实质 / md5 去重 / avg-hash 雷同） | **本次处理**：md5 去重逻辑为 judge 证据交叉核对复用；该脚本本身不改动（P6 行为不回归） |
| `agate/scripts/agate-evidence-consistency.py`（evidence JSON vs P6 声明） | **本次不处理**：judge 不消费 evidence JSON，审计 6 保持 P6 专属；账本不与其交集。理由：judge 的判据是 P1 BDD 标准 + 证据文件，不依赖 P6 声明文件（信息隔离） |

结论：账本与七道审计（审计 1-7）配合关系 = 审计 1/3/5 复用/同源，审计 6 无交集，审计 2 提供白名单校验先例，账本独有防改写能力补齐审计盲区；**无冲突点**，P2 只需定事件 schema 与写入时机。

### 4.4 同类问题未来新增的回归拦截声明

1. **信息隔离类约束的扩展**（未来新增更多需要 fresh context 的评审角色，或审计 2 之外的新派发面）：拦截手段 = 检查脚本扩展 + 既有 `check-protocol-consistency.py` 的 dispatch-context 锚点检查（keywords 命中）→ **转 BDD-4**（白名单校验机制化，后续角色复用同款校验入口）。
2. **事件账本消费方扩展**（未来更多 gate/脚本要读 `gate-events.jsonl` 留痕）：拦截手段 = 统一 `agate_common.append_event()` 单点写入 + `check-events.py` 审计兜底 → **转 BDD-7**。
3. **阶段体系新生枚举**（未来再出现类似 P6.5 的挂载位）：拦截手段 = `valid_phases` / `_DEFAULT_MAX_RETRY_MAP` / `_PHASE_OUTPUTS` / 卡片枚举四处的同步由 `check-protocol-consistency.py`（CHECK 12 重试表一致性）+ 全量 pytest 回归兜底 → **转 BDD-10**。

## 5. BDD 验收条件

> 每条 BDD 独立可二值判定（PASS/FAIL 无中间态）。验证方式：P3 测试设计映射 + P5/P6 实跑。

### 5.1 P6.5 门槛与状态机挂载

#### BDD-1: 新任务 P6 验收后必须经 P6.5 judge 门槛才能进入 P7
- Given 任务在 judge 机制生效后启动（其状态文件含 judge 机制标记），且已完成 P6 验收（P6-acceptance.md 与 P6-evidence/ 就绪，check-gate.py P6 通过）
- When 主 Agent 执行 P6→P7 转移判定
- Then 必须存在 `P6.5-judge-verdict.md` 且 `check-judge-verdict.py` + `check-events.py` 均判定通过，P6→P7 才被允许；verdict 文件缺失或任一校验 exit 1 → 转移被阻断

#### BDD-2: 历史任务（无 judge 字段）跳过 P6.5，存量不挂
- Given 存量任务在 judge 机制落地前创建、其状态文件无 judge 字段（且无 `gate-events.jsonl`）
- When 其完成 P6 验收并推进 P7
- Then P6.5 gate 自动跳过（不要求 `P6.5-judge-verdict.md` / `gate-events.jsonl`），按原有 P6→P7 规则转移，check-gate 不因缺失 judge 产物而拦截

#### BDD-3: judge 以 fresh context 逐条重验所有 BDD（含已 PASS 项，零挑验）
- Given 主 Agent 派发 judge（全新会话，不继承 verifier / implementer 上下文）
- When judge 产出 `P6.5-judge-verdict.md`
- Then 该文件声明的 `criteria_total` 必须等于 P1-requirements.md 的 BDD 标题数（`#### BDD-NN:`），且每条 BDD（含 P6 已判 PASS 项）都有独立结论条目；`criteria_total` 不符或存在未验 BDD → `check-judge-verdict.py` exit 1

### 5.2 信息隔离与防造假

#### BDD-4: 信息隔离白名单——judge 的 dispatch-context 仅允许白名单输入，禁项为可机械匹配的黑名单路径引用集
- Given 主 Agent 写 `P6.5-dispatch-context-judge.md` 派发 judge（其『输入文件』与『上游关联』节是向 judge 传递输入清单与上游信息的唯一载体）
- When `check-judge-verdict.py` 校验该文件（『输入文件』与『上游关联』两节做路径引用扫描 + 全文做行首预判扫描，均排除 AGATE_CARD 注入块与 frontmatter）
- Then 出现任一情况 → exit 1：① 两节出现黑名单路径模式（字符串/正则匹配）：`P6-acceptance.md` / `P6-dispatch-context-*.md` / `P5-dispatch-context-*.md` / `P4-dispatch-context-*.md` / `P4-implementation.md` / `P4-review.md` / `P5-test-results/` ② 两节出现白名单外任何任务文件路径（白名单 = `P1-requirements.md` / `P2-design.md` / `P6-evidence/` / `.state.yaml` / `gate-events.jsonl` / `P6.5-judge-verdict.md`，另授 git log 查询权）③ 全文含行首 `- PASS`/`- FAIL` 验收结论预判（正则 `^\s*- (PASS|FAIL)\b`，继承 check-p6-provenance 审计 2）；且『上游关联』节声明禁注入禁项——主 Agent 派发与 `agate-extract-context.py` 注入在 P6.5 均不得把黑名单路径 / verifier 产出结论传入 judge（P6.5 禁用该注入或净化为仅白名单路径）

#### BDD-5: verdict 落盘机器可读且字段完备
- Given judge 完成复核
- When 产出 `P6.5-judge-verdict.md` 且 `check-judge-verdict.py` 解析
- Then 该文件 Header 含 `status`（passed / rejected / needs-revision 三值之一）+ `criteria_total` + `criteria_passed` + `verdict_evidence` 字段；字段缺失或取值非法 → exit 1；status=passed 时须 `criteria_total == criteria_passed == P1 BDD 数`，否则 exit 1

#### BDD-6: 证据交叉核对——每条结论的证据引用真实存在且不重复充数
- Given `P6.5-judge-verdict.md` 每条 BDD 结论在 `verdict_evidence` 中引用证据文件
- When `check-judge-verdict.py` 核对
- Then 每条引用须指向真实存在且非空的证据文件（`P6-evidence/` 下）；同一物理文件（md5 相同）不得被多条结论引为不同证据；存在缺失引用 / 空文件 / md5 重复充数 → exit 1

### 5.3 事件账本与预算

#### BDD-7: 事件账本 append-only + 行间哈希链
- Given 关键事件（gate_run / judge_verdict / state_transition 等）经 `agate_common.append_event()` 写入 `{AGATE_WORKSPACE}/tasks/{Txxx}/gate-events.jsonl`
- When `check-events.py` 审计该文件
- Then ① 逐行校验 `prev_hash` 哈希链完整（改写任何历史行 → 链断裂）② 时间戳单调不减 ③ 仅允许行尾追加；任一违反 → exit 1；账本审计通过是 P6.5 gate 的前置条件（空文件 / 仅有起始行的账本为合法态）

#### BDD-8: 三档预算与诚实降级——超限不静默放行
- Given judge 复核轮次超过 2 轮，或 token 消耗超过 `judge_token_budget`（默认 100k），或 wall-clock 超过 30 min
- When 预算耗尽时 judge 结束复核并落盘 verdict
- Then `P6.5-judge-verdict.md` 必须 `status: needs-revision` 且标注 `partial: true`（不得 `status: passed` 静默放行）；`gate-events.jsonl` 记录 `reason: budget_exhausted` 事件；P6.5 gate 对该 verdict 判定不通过

### 5.4 哲学红线与协议一致性

#### BDD-9: 不引入"LLM 当 gate 主判据"——exit code 才是门槛
- Given judge verdict 声明 `status: passed`（LLM 自述全过）
- When 机械核对执行（`check-judge-verdict.py` 的 BDD 计数对照 / 证据引用 / 白名单校验 + `check-events.py` 账本审计）
- Then 任一机械核对 exit 1 → P6.5 gate exit 1、P6→P7 转移阻断；judge 的 LLM 结论不单独构成放行依据（只作行为描述输入）

#### BDD-10: 协议一致性与回归——P6.5 挂载不破坏现有体系
- Given 实施完成（协议文档 + 脚本 + 测试全部改动落地，含 state-machine 重试表 / WORKFLOW 总览 / dispatch-protocol 信息隔离节 / P6 卡片门槛 / dispatch-prompt Judge 追加节 / 角色清单登记）
- When 运行 `python3 agate/scripts/check-protocol-consistency.py --strict-errors-only` 与全量 pytest（`-p no:cacheprovider --basetemp=<可写目录>`）
- Then consistency 0 ERROR 且 pytest 全绿（含新增 `test_check_judge_verdict.py` / `test_check_events.py` 与既有 P6 相关回归用例；`count-tests.sh` 用例数不漂移；valid_phases / MAX_RETRY_MAP 等既有校验对 P6.5 挂载方式不再误报）

## 6. 裁剪说明

`phases: [P1, P2, P3, P4, P5, P6, P7, P8]` — 全流程，无跳过。判定依据：

- **风险等级 medium**：改动面大（协议文档 + 脚本 + 测试 12+ 文件，全触发 SELF-GATE）、机制核心（P6.5 影响此后所有任务）、历史兼容风险；但非安全/数据/生产环境直接改动，不升 high。
- P2 不可裁（方案设计必经；P6.5 挂载方式 / 事件 schema / 白名单校验机制需 architect 定候选方案）。
- P3 不可裁（medium 风险；BDD-1~10 需 TDD 红灯映射，机械判定是"gate 章 哲学红线"的落地验证）。
- P7 不可裁（多文件跨文件一致性：协议文档与脚本同步是本次改动的核心风险面）。
- P8 不可裁（协议本体改造需走发布流程 + SELF-GATE review）。

## 7. 能力需求声明

`capability_requirements: []` — 无特殊能力需求：

- 本任务全部实现为 Python 脚本（pyyaml 已有）+ Markdown 协议文档 + pytest 测试，运行环境（python3 + pyyaml + pytest）当前即具备 → 无 supplementable / GAP 项。
- judge 角色本身是 LLM，但其结论被机械核对兜底（BDD-9），不属于本任务**运行期**需要额外注入的能力（它是机制产品的一部分，非本任务实现所需的输入能力）。
- 无视觉 / 浏览器 / 外部系统依赖；无需 `verification_env` 声明（无服务需起、无端口需通）。

## 8. 待确认清单

`[NO_NEED_CONFIRM]` — 无未决待确认项：

- 方向性决策（P6.5 强制所有任务、三层防造假、三档预算、挂靠现有机制）均由 P0-brief 锁定，P1 不重新开放。
- 两条 `[SUGGEST:]` 倾向项（LIMITATIONS.md 同步、P6.5 挂载方式偏好）不阻塞推进，主 Agent 可径自采纳（见第 3 节）。
- 技术性选择（事件 schema 字段、白名单校验的具体扫描粒度、valid_phases 扩展方式）属 P2 设计决策，P1 只声明约束，不越界设计。