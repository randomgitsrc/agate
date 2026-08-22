---
phase: P2
task_id: TAG0020-independent-judge
type: design
parent: P1-requirements.md
trace_id: TAG0020-P2-20260822
status: draft
created: 2026-08-22
agent: architect
candidate_count: 3
packages: [agate]
domains: [backend]
ui_affected: false
dispatch_plan: {mode: serial, parallel_limit: 1}
---

# P2 方案设计 — 独立 Judge 机制（RM-AG0032）：P6.5 挂载与三层防造假

> 输入权威：P1-requirements.md（10 条 BDD approved）+ P0-brief.md + 设计文档 `design-independent-judge.md`（§7 文件改动清单）。
> 本文件是 TAG0020 的 P6.5 落地设计与实现导航。状态标记：`[PROD_NOT_TOUCHED]`。

## 0. 设计输入与固定项（P1 已固化，本设计不重新开放）

| 固定项 | 内容 | 出处 |
|---|---|---|
| 黑名单路径引用集 | `P6-acceptance.md` / `P6-dispatch-context-*.md` / `P5-dispatch-context-*.md` / `P4-dispatch-context-*.md` / `P4-implementation.md` / `P4-review.md` / `P5-test-results/` | BDD-4 |
| 白名单输入 | `P1-requirements.md` / `P2-design.md` / `P6-evidence/` / `.state.yaml` / `gate-events.jsonl` / `P6.5-judge-verdict.md` + git log 查询权 | BDD-4 |
| verdict Header 字段 | `status`（passed/rejected/needs-revision）+ `criteria_total` + `criteria_passed` + `verdict_evidence`；passed ⇒ 三数全等 | BDD-5 |
| 预算 | 轮次 ≤2 / token 100k（`judge_token_budget` 可覆盖）/ 时间 30min；超限 `partial: true` ⇒ needs-revision | BDD-8 |
| 哲学红线 | 不引入"LLM 当 gate 主判据"——机械核对（check-judge-verdict + check-events）exit code 才是门槛 | BDD-9 |
| 历史兼容 | 旧任务无 judge 字段 → P6.5 全链跳过 | BDD-2 |
| 一致性与回归 | consistency 0 ERROR + pytest 全绿 + count-tests 不漂移 | BDD-10 |

---

## 1. 影响面梳理（强制节，候选方案之前）

客观证据 = 对 worktree（`/home/kity/oclab/agate/.worktrees/agate-TAG0020`）的 grep/read 命中，逐条标注文件行号。

### 1.1 改什么（Modify）——逐文件/改动落点/BDD 映射

| 文件 | 改动落点（到文件内小节/函数） | 关联 BDD |
|---|---|---|
| `agate/assets/review-roles/judge.md`（**新**） | 角色定义全文；frontmatter 沿用 review-roles 统一模式 `role_id: judge / type: review / phases: [P6.5] / agent: judge`（实证：qa.md/review.md frontmatter 即此模式，`phases:` 为自由 token——P4-after/pre-commit/any 等已存在，无需枚举变更）；含「输入=只传路径、禁止输入=黑名单集、产出格式、认知模式（逐条重验全部 BDD/只信证据与 git log/每条结论引证据）、三档预算与 partial 降级、返回约定（File+Status）」 | BDD-3/5/8 |
| `agate/scripts/check-judge-verdict.py`（**新**） | verdict 门槛判定：① Header 字段完备性与取值合法（BDD-5）② criteria_total == P1 BDD 标题数（计数口径复用 check-p6-provenance.py 审计 3：`^#### BDD-[0-9]`，L371）+ 正文逐条结论覆盖全部 BDD 编号（BDD-3）③ passed ⇒ 三数全等（BDD-5）④ 证据交叉核对：存在性/非空/相互 md5 去重/引用对称（复用 check-p6-evidence.py `_md5_entries` 思路 L96-106 + L314-327；仿审计 1 的 1a/1c 对称，L263-316）（BDD-6）⑤ 信息隔离白名单扫描（复用审计 2 的 AGATE_CARD + frontmatter 双排除与 `^\s*- (PASS|FAIL)\b` 行首预判，L318-355；新增两节黑名单串与白名单外路径扫描）（BDD-4）⑥ partial:true ⇒ status≠passed、账本 budget_exhausted ⇒ needs-revision+partial（BDD-8）⑦ 校验通过后 append_event 记录 judge_verdict（脚本自记，事件写入收敛单点） | BDD-1/3/4/5/6/8/9 |
| `agate/scripts/check-events.py`（**新**） | 账本审计：逐行 JSON 可解析 / 首行 prev_hash==GENESIS_HASH / 逐行 prev_hash==sha256(上一行) 链完整性 / 时间戳单调不减 / judge_verdict 事件计数 ≤2（轮次预算机械兜底）；空文件与缺失为合法态 | BDD-7/8 |
| `agate/scripts/agate_common.py` | 新增 `append_event(task_dir, event)`（读账本尾行算 prev_hash，ts=UTC 微秒，首行 prev_hash=GENESIS_HASH，ts 单调兜底）+ `read_judge_verdict(task_dir)`（解析 verdict frontmatter 返回 dict，缺失返回 None）+ 模块级 `GENESIS_HASH` 常量；**MAX_RETRY_MAP（L43）不动**（避免 CHECK 12 重试表锚点漂移） | BDD-7/8 |
| `agate/scripts/check-gate.py` | `main()` 的 `handlers` dict（L1082-1092）增 `"P6.5": gate_p65`；新增 `gate_p65(task_dir)`：judge 未启用（.state.yaml 无 `judge.enabled: true`）→ 早退 0（历史兼容）；启用但 verdict 缺失 → exit 1；否则依次调 check-judge-verdict.py / check-events.py，任一 exit 1 → exit 1。**gate_p6（L791-840）不改**（P6 行为不回归） | BDD-1/2/9/10 |
| `agate/scripts/pre-commit-gate.py` | ① 2i（L334，provenance 注入）之后并列新增 P6.5 注入：`judge.enabled==true` 且 `P6.5-judge-verdict.md` 存在于工作树 → 依次跑 check-judge-verdict.py + check-events.py，任一 exit 1 → sys.exit(1)（commit-time 硬边界）② write_gate_result 处（L331）追加 `gate_run` 事件（append_event）③ phase 变更处（old_phase 已由 L236-238 机制可得）追加 `state_transition` 事件 | BDD-1/7/9 |
| `agate/scripts/ci-gate-backstop.py` | provenance 兜底（L234-244）后新增 judge/events 兜底（同 pre-commit 注入条件；`--no-verify` 绕过时 backstop 层补跑） | BDD-1/10 |
| `agate/WORKFLOW.md` | 阶段总览表（L288-296 形态）增 `P6.5` 行（执行角色 judge（强制）；门槛 = verdict 存在 + check-judge-verdict/check-events 双 exit 0）；角色清单树（L63-68）登记 judge.md；P6 节补「P6.5 judge 复核」说明 | BDD-1/10 |
| `agate/state-machine.md` | L134 P6→P7 规则增 judge 条件（judge 启用任务须 verdict + 两脚本通过）；转移规则新增 P6.5 描述行：`P6 → P6.5(judge 重验全部 BDD，只信证据与 git log) → P7`；`P6.5(needs-revision/rejected) → P6 重验`（轮次 ≤2，账本事件计数兜底）；**状态集合（L72）不加 P6.5**（见候选 A），并显式声明"P6.5 是挂载于 P6→P7 转移上的强门槛子阶段，非独立 phase 值；.state.yaml phase 保持 P6 至 P7"（防主 Agent 误写 phase: P6.5） | BDD-1/2/8/10 |
| `agate/dispatch-protocol.md` | 新增「Judge 信息隔离」节（白名单/黑名单路径引用集、AGATE_CARD 排除、`agate-extract-context.py` 在 P6.5 禁用或净化为仅白名单路径——上游关联注入面防泄漏）+ P6.5 派发流程小节（P6 commit 后派发、dispatch-context 命名 `P6.5-dispatch-context-judge.md`、沿用 L380 派发后冻结语义） | BDD-4 |
| `agate/phase-cards/P6-acceptance.md` | 派发步骤区（L9-20）增 P6.5 步（P6 commit 后派 judge）；门槛区（L172-183 形态）增「P6.5 judge 复核（强制）」；推进条件（L199）增 judge 条件 | BDD-1/8 |
| `agate/assets/templates/dispatch-prompt.md` | 「阶段特定提示（L105-160）」增「Judge 派发追加」节（信息隔离清单 + 三档预算声明 + verdict 产出格式 + 只信证据/git log 认知约束 + 预算耗尽 partial 诚实降级指令） | BDD-3/4/5/8 |
| `agate/role-system.md` | 第二层评审名册表（L37-51）增 judge 行；L108-116 status 三值映射表注明 judge verdict 三值复用（passed→approved / needs-revision→needs-revision / rejected→rejected）；L52-66 C8 表确认 judge **不进**（"强制所有任务"与 domain/risk 触发语义不同） | BDD-1/5 |
| `agate/AGENTS.md`（协议本体入口的角色清单） | 角色文件清单登记 judge.md（P1 §4.1 多端隐含需求） | BDD-10 |
| `agate/LIMITATIONS.md`（采纳 P1 `[SUGGEST:]`） | 局限 3「现状」段补 judge 引用（self-authored gate 缓解链增 P6.5 独立复核） | BDD-10（文档同步） |
| `agate/tests/unit/test_check_judge_verdict.py`（**新**）+ `test_check_events.py`（**新**）+ `test_check_gate.py` 增补 | 见 §3.8 测试要点 | BDD-10 |
| 既有回归（test_check_p6_provenance / test_check_p6_evidence / test_check_gate 等） | 不改，作为 BDD-10 回归锚点 | BDD-10 |

### 1.2 不改什么（Not Modify）——显式边界 + 理由

| 文件/范围 | 决定不改 | 理由 |
|---|---|---|
| `check-p6-provenance.py` 审计 1-7 逐条逻辑 | 不改（仅"复用其口径"到新脚本） | P6 行为不回归（BDD-10）；审计 2 是白名单扫描先例，先例本身不动 |
| `check-p6-provenance.py` L504 协作规范 glob `P[0-8]-*.md` | 不改（不扩到 P6.5-*） | verdict 的字段完备性由 check-judge-verdict 独立校验；双源校验口径分叉风险 > 覆盖收益 |
| `check-p6-evidence.py` / `check-p6-format.py` | 不改 | md5 去重只"复用思路"不进原脚本；P6-acceptance 格式归一化不管 verdict |
| `check-state-transition.py` / `agate-state-yaml-check.py` | 不改（含 valid_phases L17、retries key 正则 L49-50） | 候选 A 不新增 phase 值、不使用 `retries.P6.5`（改用 judge.rounds + 账本事件计数兜底轮次），两个校验脚本零触及 |
| `agate_common.MAX_RETRY_MAP`（L43） | 不改 | CHECK 12 重试表锚点（state-machine「## 重试上限」表 + 内联值文件）保持对齐，零漂移面 |
| 新增 `phase-cards/P6.5-*.md` 卡片 | 不新增 | P6.5 门槛写在 P6-acceptance.md 卡片内节（dispatch-context 文件清单即如此规定的落点），卡片文件数不变 |
| `agate-archive-stale-outputs.py` | 不改 | 候选 A 下 P6.5 无独立阶段产物归档诉求；verdict 弹回重验由新轮覆盖 + 账本事件留痕 |
| double-judge 机器强制 | 不做 | BDD 无此要求（YAGNI）；judge.md 文档声明为高风险任务的人工可选路径（复用专家组/组长机制），本轮不新增机器校验 |
| .state.yaml phase 合法值集合 | 不改（不放 "P6.5"） | 候选 A 核心；改动它即变候选 B 的连锁面 |

### 1.3 风险在哪（Risk）——每条配缓解

| # | 风险 | 缓解 |
|---|---|---|
| R1 | **事件账本与既有 gate 兼容**（P0 风险 2）：gate_run/state_transition 事件与 check-p6-provenance 审计 5（EXIT_CODE 尾行）、审计 7（p5_pass_commit 双写语义）交集 | 事件 schema 字段交集设计（`ts/event/phase/cmd/exit/runner` 与审计 5 同源不同层：账本=全阶段统一事件源+哈希链，审计 5=P6 证据目录内文件约定，不互相替代）；.state.yaml 仍为权威状态源，state_transition 事件只记录不改写；回归测试保审计 1-7 行为不变（BDD-10） |
| R2 | **历史任务兼容**：旧任务无 judge 字段，误拦存量 | 双守卫：check-gate gate_p65 早退（`judge.enabled` falsy → exit 0）+ pre-commit 注入条件（marker && verdict 存在才跑）+ BDD-2 专项回归（无 marker 任务全链跳过） |
| R3 | **信息隔离白名单误报/漏报**：AGATE_CARD 块含协议标准文本、路径引用改写（相对路径/大小写）绕过 | 复用审计 2 的 AGATE_CARD + frontmatter 双排除（provenance L318-355 同款）；黑名单/白名单扫描限定『输入文件』『上游关联』两节（匹配面窄）；黑名单串用大小写不敏感正则 + 归一化匹配；行首预判全文扫描继承审计 2 语义 |
| R4 | **文档先行引用未创建文件**（P2/P3 引用 judge.md 等新文件）触发 CHECK 2 假阳性 | 协议文档改动集中在 P4 implementer 同批落地（新文件与引用同 commit）；CHECK 2 扫描面 PROTOCOL_DIRS = agate/assets+phase-cards+rules，tasks/ 产出不在面内（实证 check-protocol-consistency.py L68）→ 本任务 P2/P3 产出不触发 |
| R5 | **P6 卡变更与 2p 卡片 hash 校验交互**：P6 卡增 P6.5 节后，既有 P6-dispatch-context-verifier.md 嵌入旧卡 → hash mismatch | 同任务内 P4 先改卡、P6 派发时注入新卡（P6-verifier dispatch-context 在卡更新后创建）→ 一致；`P6.5-dispatch-context-judge.md` 不在 2p glob（`phase+"-dispatch-context-*"`，L353，phase=P6 时不匹配 P6.5-*）→ 卡片内容合规由 check-judge-verdict 白名单扫描承担，**不扩展 2p glob**（保持 pre-commit 改动最小） |
| R6 | **P6 阶段非证据文件拦截**（2n.2，L439-454）：verdict/dispatch-context 是否被当作源码拦截 | 实证排除：两者是 .md，`_NON_MD_YAML_RE`（L77）不匹配 → 不进入 all_nonmd → 不拦截；`_P_OUTPUT_RE`（L78）与 step3 正则（L487）不匹配 P6.5-* → 无假警告（见 minimal_validation 静态验证） |
| R7 | **时间戳单调与并发写**：多进程同秒写入 → ts 抖动破坏单调 | 单任务单进程顺序写入（pre-commit 钩子串行）+ append_event 内部 ts 单调兜底（`max(now, 尾行 ts)` 微秒级递增）；check-events 判定用 ≤ 而非 < 放宽精度 |
| R8 | **轮次预算依赖账本事件计数**：judge 轮次绕过记账 | judge_verdict 事件由 check-judge-verdict.py **校验通过后自动追加**（脚本自记，不依赖主 Agent 手工）；事件写入全收敛 append_event 单点（候选 C1） |
| R9 | **"P6.5 非 phase 值"语义模糊**（候选 A 固有）：主 Agent 误写 `phase: P6.5` 触发 state-yaml 拦 / 文档与状态机不一致 | state-machine.md 显式声明子阶段语义 + P6.5 门槛节写明"推进 P7 时 phase 直接从 P6 到 P7"；agate-state-yaml-check 的 valid_phases 不含 P6.5 即天然防误写（写错会被拦，fail-closed） |
| R10 | **CHECK 12 重试表锚点漂移**：新增 P6.5 重试数值被一致性检查拦截 | 候选 A 不新增 `| P6.5 | N |` 表行（`_RETRY_TABLE_ROW_RE = \|\s*(P\d+)\s*\|` 不匹配 P6.5，实证 L924）+ 不动 MAX_RETRY_MAP → 零漂移；judge 轮次预算以 prose + 账本事件计数呈现 |
| R11 | **verdict 被 P4/P6 产出覆盖或漏生成**：verdict 与 P1 计数漂移 | check-judge-verdict 的 criteria_total 每次与 P1 `^#### BDD-[0-9]` 实时对照（不缓存）；BDD-3 集相等校验（P1 全部编号 ⊆ verdict 结论 ⊆ P1 编号） |

---

## 2. 候选方案与权衡（candidate_count: 3）

场景类型：系统架构（多组件交互、状态机转移、跨文件改动）→ 先画数据流（§3.1），再对挂载点与事件写入主体两个轴出方案。

### 候选方案 1（推荐）：P6.5 作为「P6→P7 转移上的强门槛子阶段」——不新增 phase 值（采纳 P1 §3 SUGGEST）

**机制**：
- `.state.yaml` phase 保持 `P6` 直至 P7；P6 commit 后主 Agent 派发 judge（写 `P6.5-dispatch-context-judge.md`，白名单输入）。
- judge 以 fresh context 逐条重验全部 BDD，产出 `P6.5-judge-verdict.md`。
- 推进判定：主 Agent 跑 `check-gate.py P6.5 TASK_DIR`（内部依次调 check-judge-verdict + check-events，见 §3.5）；通过后写 `phase: P7` 随 P7 commit。
- commit-time 强制：pre-commit-gate 注入（`judge.enabled==true` 且 verdict 存在 → 两个脚本任一 exit 1 → commit 阻断），在任何后续 phase commit（含 P7 commit）都生效 → P6→P7 硬边界不依赖主 Agent 自觉。
- 轮次预算：`judge.rounds`（.state.yaml）+ 账本 judge_verdict 事件计数 ≤2（机械兜底）；**不使用 `retries.P6.5`**（规避 agate-state-yaml-check.py L49 `^P\d+$` retries key 校验）。

**优点**：① 零 phase 枚举连锁面——valid_phases / MAX_RETRY_MAP / 状态集合 / 回退表 / 卡片枚举五处全不动，P1 §3 点名的四项同步压力消失；② 历史兼容天然（marker 缺失 → 全链 skip，BDD-2）；③ 改动集中 = 2 个新脚本 + check-gate/pre-commit 两个挂载点 + 文档 5 处；④ 机械核对（两脚本 exit code）即门槛，LLM verdict 只作行为描述输入（BDD-9 落地）。

**缺点**：P6.5 不是状态机实体，文档需显式声明"子阶段/门槛"语义（R9）；verdict 无独立 phase commit，commit 归属约定为「由主 Agent 在 P6 阶段补充 commit（phase=P6，hook 在 verdict 存在后自动验）或随 P7 commit 暂存」，enforcement 与 commit 位置解耦（注入条件不依赖 phase 值）。

**工作量**：低-中。**风险**：低。

### 候选方案 2：P6.5 作为真实 state-machine 阶段（phase 枚举全面扩展）

**机制**：valid_phases / MAX_RETRY_MAP（"P6.5:2"）/ 状态集合 / 回退表全部加 P6.5；verdict 以 `phase: P6.5` commit，hook 天然跑 `check-gate.py P6.5`；retry 走 retries_over（MAX "P6.5:2"）。

**优点**：状态机实体与文档完全一致；verdict commit 的 hook 即 gate（因果直接）；重试上限由状态机机械强制。

**缺点（连锁面，实证）**：
- `agate-state-yaml-check.py` L17 valid_phases 加 "P6.5"；且 retries key 正则 L49 `^P\d+$` 必须扩为 `P\d+(\.\d+)?$`（否则 `retries.P6.5` 被拦）；
- `agate_common.MAX_RETRY_MAP` L43 + state-machine「## 重试上限」表 + CHECK 12 锚点三处须同步核对（R10 变为真实改动面）；
- `pre-commit-gate.py` 2p（L353 glob）+ `_PHASE_OUTPUT`（L66）+ `_P_OUTPUT_RE`（L78）语义需逐处复核（"P6.5" 作为 phase 值时 `agate-next-card.py P6.5` 需支持、产出-阶段警告正则需适配）；
- `check-state-transition.py` `phase_num("P6.5")==6` 与 P6 在数字提取上不可区分（P6↔P6.5 diff=0），检查 1/4 的回退检测语义需复核（P6.5 弹回 P6 与 P6→P6.5 同值，恰好不互拦，但需测试固化）；
- UPGRADING.md 需记破坏性变更（phase 枚举变化对新任务影响）。

**优点 vs 缺点**：候选 2 的"commit-time 天然强制"收益，候选 1 已用 pre-commit 注入等价获得（注入条件是 marker+verdict 存在，与 phase 值无关）；候选 2 的连锁风险（枚举遗漏导致某个 `P[0-8]` 正则静默漏过/误拦）正是 P1 §3 明确点名要避开的（"避免扩展 valid_phases/回退表/卡片枚举的连锁改动面"）→ **不选**。

**工作量**：高。**风险**：中-高。

### 候选方案 3：事件账本写入主体（append 收敛）

- **3a（推荐）**：事件写入全收敛 `agate_common.append_event()` 单点，**门禁脚本自动调**——pre-commit-gate 在 write_gate_result 处（L331 旁）追加 `gate_run`、phase 变更处追加 `state_transition`；check-judge-verdict 校验通过后追加 `judge_verdict`（含 partial/reason）。
  - 优点：机械、防漏写、防主 Agent 自写自卖（append-only 防改写机制不依赖台账方诚实，与 BDD-9"机械核对是门槛"精神一致）；与 P1 §4.3 交集分析"账本=全阶段统一事件源"相符。
  - 缺点：pre-commit-gate / check-judge-verdict 各增加调用点（文件内少量代码）。
- **3b**：主 Agent 在推进时手工调 append_event（bash）记录关键事件。
  - 优点：脚本调用面最小（只加 agate_common 两个函数）。
  - 缺点：信任模型差——防改写机制依赖最该被防的对象（主 Agent 自身）自觉写事件；每推进多一步手工操作易漏写 → 账本缺事件、审计无法交叉核对；与"机械核对是门槛"的哲学红线相悖。
  - **不选**。

**权衡结论**：挂载轴选候选 1（最小脚本面 + commit-time 强制等价物），写入轴选候选 3a（机械、防漏、信任模型正确）。两者正交组合为最终方案（§3）。

---

## 3. 选定方案细化（候选 1 + 3a）

### 3.1 总览数据流

```
P6 commit (phase=P6, P6-acceptance+P6-evidence, pre-commit 跑既有 P6 gate+provenance)
  → 主 Agent 写 P6.5-dispatch-context-judge.md（白名单输入 + AGATE_CARD 注入 + 派发后冻结）
  → 派发 judge（fresh context，禁 agate-extract-context 注入/净化，只读标准与证据与 git log）
  → judge 逐条重验全部 BDD → P6.5-judge-verdict.md（Header status/criteria_total/criteria_passed/verdict_evidence[/partial]）
  → 主 Agent 跑 check-gate.py P6.5（= check-judge-verdict 全链校验 + check-events 账本审计；通过后 append judge_verdict 事件）
  → verdict（+dispatch-context）随 commit 落库（phase=P6；hook 在 verdict 存在后自动重验两脚本）→ 通过 → 写 phase=P7 → P7 commit
  → needs-revision / rejected → 弹回 P6 重验（judge 轮次+1，账本 judge_verdict 事件计数 ≤2；超限 → 人工接管）
  → 历史任务（无 judge.enabled）→ gate_p65 早退 + hook 注入条件不成立 → 全程跳过（BDD-2）
```

### 3.2 事件账本 schema 与 append_event / read_judge_verdict

- 路径：`{AGATE_WORKSPACE}/tasks/{Txxx}/gate-events.jsonl`（任务级，与 .state.yaml 同目录）
- 行 schema（JSON 对象，追加行间哈希链）：
  ```json
  {"ts":"2026-08-22T10:00:01.123456Z","event":"gate_run","phase":"P6","cmd":"check-gate.py P6","exit":2,"runner":"pre-commit","prev_hash":"<sha256 hex>"}
  {"ts":"...","event":"judge_verdict","phase":"P6.5","verdict":"needs-revision","criteria_total":10,"criteria_passed":9,"partial":true,"reason":"budget_exhausted","prev_hash":"..."}
  {"ts":"...","event":"state_transition","phase":"P6.5","from":"P6","to":"P7","prev_hash":"..."}
  ```
- `prev_hash` = sha256(上一条**原始行** UTF-8) 的 hex；**首行** prev_hash = `GENESIS_HASH` = sha256(b"")（模块级常量，append_event 与 check-events 同源定义，放 agate_common）
- `append_event(task_dir, event: dict)`：自动补 `ts`（UTC ISO8601 微秒）+ `prev_hash`；文件不存在 → 直接写首事件（prev_hash=GENESIS_HASH）；ts 单调兜底（`max(now, 尾行 ts)` 微秒递增）；以追加模式写一行（带 `\n`）。失败（IOError）→ 打印 WARNING 不抛（gate 主判定不依赖写账本成功，账本审计是辅助防线；但 judge_verdict 事件写入失败也仅告警——verdict 校验本身已通过）
- `read_judge_verdict(task_dir)`：解析 `P6.5-judge-verdict.md` frontmatter（`---` 块），返回 `{status, criteria_total, criteria_passed, verdict_evidence, partial}`；文件缺失/解析失败 → None
- 合法态：账本缺失或空文件 → 合法（BDD-7）；"仅有起始行" = 只有一条事件行且其 prev_hash == GENESIS_HASH → 合法
- 字段交集（P1 §4.3）：`ts/event/phase/cmd/exit/runner` 与审计 5 的 EXIT_CODE 尾行约定**同源不同层**；`state_transition` 事件与 .state.yaml 状态**双写**（.state.yaml 仍权威）；账本独有能力 = 哈希链 + 时间戳单调（审计 1-7 无此机制，无冲突）

### 3.3 check-judge-verdict.py 校验链（CLI：`check-judge-verdict.py TASK_DIR`，exit 0/1）

逐项（顺序执行，任一 exit 1 即停）：
1. `P6.5-judge-verdict.md` 存在且非空（BDD-1 fail-closed）
2. `P6.5-dispatch-context-judge.md` 存在且非空（缺 → 无法验证隔离 → exit 1，BDD-4）
3. Header 字段：`status ∈ {passed, rejected, needs-revision}`；`criteria_total` / `criteria_passed` 为整数；`verdict_evidence` 存在（BDD-5）
4. BDD 对照（BDD-3）：`criteria_total ==` P1 `^#### BDD-[0-9]` 标题数（审计 3 计数口径）；正文结论条目 `- (PASS|FAIL|NEEDS-REVISION) BDD-NN:` 的编号**集相等**于 P1 全部 BDD 编号，且条目数 == criteria_total（P1 有 N 条 → verdict 须 N 条，零挑验，含已 PASS 项重验）
5. status==passed ⇒ `criteria_total == criteria_passed ==` P1 BDD 数（BDD-5）；`partial: true` ⇒ status ∈ {needs-revision, rejected}（passed+partial → exit 1，BDD-8 机械落地）
6. 证据交叉核对（BDD-6）：frontmatter `verdict_evidence` 每条 → 存在于 P6-evidence/ 下 + 非空 + 相互 md5 不同（同一物理文件不得被多条结论引为不同证据）；正文每条 BDD 结论的引用 ⊆ verdict_evidence；verdict_evidence 每条被 ≥1 条结论引用（对称，仿审计 1 的 1a/1c）
7. 信息隔离白名单（BDD-4）：对 P6.5-dispatch-context-judge.md：
   - 『输入文件』『上游关联』两节黑名单串扫描（大小写不敏感）：`P6-acceptance.md` / `P6-dispatch-context-*.md` / `P5-dispatch-context-*.md` / `P4-dispatch-context-*.md` / `P4-implementation.md` / `P4-review.md` / `P5-test-results/`
   - 两节白名单外任务产出路径引用扫描：按任务产出文件命名模式（`P[0-9][0-9.]*-*.md` / `P[0-9]-test-results/`）提取路径，逐条归一化后不在白名单（`P1-requirements.md` / `P2-design.md` / `P6-evidence/` / `.state.yaml` / `gate-events.jsonl` / `P6.5-judge-verdict.md`）→ exit 1
   - 全文（排除 AGATE_CARD 块 + frontmatter，复用审计 2 双排除 L318-355）行首 `^\s*- (PASS|FAIL)\b` 预判扫描
8. 预算交叉（BDD-8）：账本存在 `judge_verdict` 事件且任一 `reason == budget_exhausted` → verdict 必须 `partial: true` 且 `status == needs-revision`（否则 exit 1）
9. 全部通过 → `append_event(task_dir, {event: "judge_verdict", phase: "P6.5", verdict: status, criteria_total, criteria_passed, partial, [reason]})` → exit 0

不校验项（边界声明）：verdict 正文结论的行格式细节（PASS/FAIL/NEEDS-REVISION 语义）由 judge.md 产出规范约束；脚本只做编号集/计数/字段/证据/隔离的机械核对（BDD-9：LLM 结论不单独构成放行依据）。

### 3.4 check-events.py 校验链（CLI：`check-events.py [TASK_DIR]`，exit 0/1）

1. 文件缺失或空 → exit 0（合法态，BDD-7）
2. 逐行 JSON 可解析（坏行 → exit 1）
3. 首行 `prev_hash == GENESIS_HASH`（不符 → exit 1）
4. 逐行 `prev_hash == sha256(上一行原始内容)`（链断裂 → exit 1 = 历史行被改写检测）
5. `ts` 单调不减（微秒精度，UTF-8 字典序即可比较同格式）→ 违例 exit 1
6. （3+4+5 组合判定"仅允许行尾追加"：改写任何历史行 → 后续行 prev_hash 断裂；删除尾部无法由哈希链检测，由 ts 单调 + judge_verdict 计数部分兜底）
7. `judge_verdict` 事件计数 ≤ 2（超出 → exit 1，轮次预算机械兜底，BDD-8）
8. 未知 event 类型不拦截（向后兼容；`gate_run/judge_verdict/state_transition` 为已知类型）

账本审计是 P6.5 gate 前置（BDD-7）；账本本身不要求特定事件必须存在（只校验存在内容的完整性）。

### 3.5 check-gate.py P6.5 分支与 pre-commit 注入

```python
# check-gate.py main() handlers（L1082-1092）增：
"P6.5": gate_p65,

def gate_p65(task_dir):
    state_yaml = _load_state_yaml(task_dir)          # 仿 check-p6-provenance._load_state_yaml（L209-221）
    if not (state_yaml or {}).get("judge", {}).get("enabled"):
        sys.stderr.write("GATE P6.5: judge 机制未启用（历史任务），跳过\n"); return 0   # BDD-2
    verdict = os.path.join(task_dir, "P6.5-judge-verdict.md")
    if not os.path.isfile(verdict):
        sys.stderr.write("GATE P6.5: 缺 P6.5-judge-verdict.md（judge 未产出），P6→P7 阻断\n"); return 1  # BDD-1
    for script in ("check-judge-verdict.py", "check-events.py"):
        if subprocess 调 {SCRIPT_DIR}/{script} [task_dir] 返回非 0:
            sys.stderr.write(f"GATE P6.5: {script} 未通过\n"); return 1                # BDD-9
    return 0
```

```python
# pre-commit-gate.py 2i（L334）之后新增（与 provenance 并列）：
if (gate_exit != 1
        and _judge_enabled(task_dir)                      # 读 .state.yaml judge.enabled
        and os.path.isfile(os.path.join(task_dir, "P6.5-judge-verdict.md"))):
    if (_run_script_rc("check-judge-verdict.py", [task_dir]) == 1
            or _run_script_rc("check-events.py", [task_dir]) == 1):
        sys.exit(1)
# L331 write_gate_result 处追加：
#   append_event(task_dir, {"event": "gate_run", "phase": phase, "cmd": "check-gate.py " + phase, "exit": gate_exit, "runner": "pre-commit"})
# phase 变更处（old_phase/new_phase 可得）追加 state_transition 事件
```

`gate_p6`（L791-840）不加 judge 逻辑——P6 语义不变（BDD-10)；P6.5 judge/events 由 gate_p65（推进判定）+ pre-commit 注入（commit-time 强制）双路径承载（BDD-1 门槛条件完整）。

### 3.6 .state.yaml judge 块与历史兼容

```yaml
judge:
  enabled: true        # 机制启用标记（judge 机制生效任务在 P1 初始化时主 Agent 写入；缺失/false = 历史任务，全链跳过——BDD-2）
  rounds: 1            # 已用复核轮次（主 Agent 维护；机械兜底 = 账本 judge_verdict 事件计数 ≤2）
  last_verdict: passed # 上次 verdict status（信息用途）
  partial: false       # 是否 partial 降级
  # 可选（高风险任务人工指定）：double_judge: true —— 文档级可选，本轮无机器校验
```

实证：agate-state-yaml-check.py 只校验 task_id/phase/status/retries（L29-53），未知顶层键 `judge:` 不告警、不拦截；`retries` 键仍须 `^P\d+$`（L49-50）→ 本设计**不使用 retries.P6.5**（轮次预算由 judge.rounds + 账本事件计数承载），agate-state-yaml-check / check-state-transition 零改动（BDD-10）。

### 3.7 status 门槛映射与挂靠机制（BDD-3/5 复用）

- judge verdict `status` 三值沿用 role-system.md L108-116 映射：`passed → approved`（P6→P7 放行）/ `needs-revision → needs-revision`（弹回 P6 重验，轮次+1）/ `rejected → rejected`（弹回 P6 或交人工）
- 主 Agent 只读 verdict Header `status` 判定（judge.md + dispatch-prompt 追加节写明）；check-judge-verdict 只验字段合法性与机械约束，不做"LLM 结论放行"（BDD-9）
- 派发沿 dispatch-prompt.md 模板 + 方法 B（general subagent + 角色文件注入）；judge 是**所有任务强制**的常态门槛评审 → 不进 C8 表（与 domain/risk 触发语义不同，P1 §4.1 已判定）

### 3.8 测试设计要点（P3 输入，BDD-10）

- `test_check_judge_verdict.py`（同 test_check_p6_provenance.py 的 task_dir/agate_scripts/python_exe/run_cli fixtures 模式）：
  - BDD-4：黑名单串命中（P6-acceptance.md 等）→ exit 1；白名单外路径 → exit 1；行首 `- PASS` 预判 → exit 1；AGATE_CARD 块内含 PASS/FAIL 不误报；前后置 frontmatter 排除
  - BDD-3：criteria_total ≠ P1 BDD 数 → exit 1；漏验某 BDD（编号集不相等）→ exit 1
  - BDD-5：status 非法值 / 字段缺失 / passed 但 criteria_passed < criteria_total → exit 1
  - BDD-6：证据引用不存在 / 空文件 / md5 重复充数 / 引用不在 verdict_evidence 清单 → exit 1
  - BDD-8：partial + passed → exit 1；账本 budget_exhausted 但 verdict 非 needs-revision → exit 1
  - BDD-9：status=passed 但证据缺失 → 机械核对 exit 1（LLM 结论不单独放行）
- `test_check_events.py`：
  - BDD-7：合法链 exit 0；篡改中间行 → 链断裂 exit 1；追加模式合法性；空/缺失文件 exit 0；时间戳乱序 exit 1；坏 JSON → exit 1；GENESIS_HASH 常量正确性
  - BDD-8：judge_verdict 事件 3 条 → exit 1（轮次兜底）
- `test_check_gate.py` 增补：gate_p65 历史任务 skip（无 judge.enabled）；marker 有 verdict 缺 → exit 1；verdict 通过 → exit 0
- 回归锚点：既有 test_check_p6_provenance / test_check_p6_evidence / test_check_gate 全绿（审计 1-7 行为不变）；count-tests.sh 用例数变化记录（新增文件数量入账）

---

## 4. 批次设计（dispatch_plan: serial）

- **mode: serial, parallel_limit: 1**。理由：单包（agate）内 12+ 文件的改动高度耦合——测试依赖脚本（test_check_judge_verdict 需 check-judge-verdict.py 存在）、脚本互相调用（check-gate/pre-commit 调新脚本）、协议文档引用脚本与角色文件（CHECK 2 引用存在性）→ 并行拆批会产生跨批依赖；串行链：① 脚本层（agate_common append_event/read_judge_verdict → check-judge-verdict.py → check-events.py → check-gate gate_p65 → pre-commit-gate/ci-gate-backstop 注入）② 协议文档层（judge.md → state-machine/WORKFLOW/dispatch-protocol/P6 卡/dispatch-prompt/role-system/AGENTS/LIMITATIONS）③ 测试层（两个新测试 + check-gate 增补 + 回归）
- 批次粒度：产出 ≤3 / 输入 ≤3（各阶段由主 Agent 按 serial 派发，单 subagent 单批）
- 资源密集：P5 为全量 pytest + consistency + count-tests（非 E2E/构建），串行批次内单跑即可；无并行资源竞争

## 5. 机器字段与声明（P2 固化）

```yaml
gate_commands:
  P3: "python3 -m pytest -p no:cacheprovider --basetemp=agate-workspace/.pytest-tmp agate/tests/unit/test_check_judge_verdict.py agate/tests/unit/test_check_events.py"
  P5: "python3 -m pytest -q --tb=no -p no:cacheprovider --basetemp=agate-workspace/.pytest-tmp agate/tests/"
  P5_consistency: "python3 agate/scripts/check-protocol-consistency.py --strict-errors-only"
  P5_count_tests: "bash agate/tests/scripts/count-tests.sh"
  P5_timeout_seconds: 600
```
> P3/P5 必须带 `-p no:cacheprovider --basetemp=<可写目录>`（/tmp 只读，Errno30；basetemp 用 worktree 下 `agate-workspace/.pytest-tmp`，由 P0-brief env_constraints 继承细化）。P5_consistency 用 worktree 自己的 check-protocol-consistency.py（读 worktree 协议文件）。P5_count_tests 校验用例数未漂移（count-tests.sh 语义）。`--strict-errors-only` 仅 ERROR 判失败（日常默认档）。

```yaml
env_constraints:
  debug_env: "Linux；/tmp 与 ptmp 只读（Errno30）→ pytest 必须 -p no:cacheprovider --basetemp=<可写目录>（如 agate-workspace/.pytest-tmp）；解释器 /usr/bin/python3；任务工作区（agate-workspace）可写、协议本体目录只读 → [PROD_NOT_TOUCHED]"
  test_cmd: "python3 -m pytest agate/tests/；python3 agate/scripts/check-protocol-consistency.py --strict-errors-only；bash agate/tests/scripts/count-tests.sh"
  isolation_check: "测试临时目录一律用 pytest tmp_path fixture（平台无关约定，AGENTS.md 测试约定），不依赖 /tmp；新增测试不硬编码 Unix-only 路径（Windows CI 冒烟兼容）"
  tools_discipline: "跑 gate/读卡片/读角色文件用 ~/.agate（=/home/kity/oclab/agate/agate 稳定版）；check-protocol-consistency.py 必须用 worktree 自己的；bash 一律外层 timeout（30-90s）；单步串行"
```

```yaml
files_to_read:
  - path: agate/scripts/check-p6-provenance.py:318-399
    why: 审计 2 的 AGATE_CARD/frontmatter 双排除 + 行首预判扫描（check-judge-verdict 白名单扫描直接复用）；审计 3 的 BDD 计数口径 `^#### BDD-[0-9]`（criteria_total 对照复用）
  - path: agate/scripts/check-p6-evidence.py:96-106, 314-327
    why: _md5_entries + md5 去重阻断（BDD-6 证据去重复用思路）
  - path: agate/scripts/check-gate.py:791-840, 1063-1097
    why: gate_p6 现状 + main() handlers 结构（gate_p65 挂载参照；gate_p6 不改）
  - path: agate/scripts/pre-commit-gate.py:324-348, 350-398
    why: 2h.1 gate/2i provenance 注入模式（P6.5 注入并列参照）+ 2p glob 语义（P6.5-* 不覆盖，不需扩展）
  - path: agate/scripts/pre-commit-gate.py:236-238, 331
    why: old_phase 获取机制（state_transition 事件写入点）+ write_gate_result 处（gate_run 事件写入点）
  - path: agate/scripts/agate_common.py:244-276
    why: write_gate_result 模式（append_event/read_judge_verdict 新函数参照；MAX_RETRY_MAP 不动）
  - path: agate/scripts/ci-gate-backstop.py:215-244
    why: provenance 兜底模式（judge/events backstop 扩展参照）
  - path: agate/scripts/agate-state-yaml-check.py:17, 29-53
    why: 确认 valid_phases 与 retries key 校验范围（本设计零触及；防 Phase 误写 P6.5 天然 fail-closed）
  - path: agate/state-machine.md:72, 134-150
    why: 状态集合 + P6→P7 转移规则（P6.5 描述行与 judge 条件落点）
  - path: agate/dispatch-protocol.md:306-380
    why: dispatch-context 规范/上游关联/AGATE_CARD 注入/派发后冻结（信息隔离节落点）
  - path: agate/phase-cards/P6-acceptance.md:9-20, 172-183
    why: P6 派发步骤 + 门槛节（P6.5 步/门槛落点）
  - path: agate/assets/templates/dispatch-prompt.md:105-160
    why: 阶段特定提示结构（Judge 追加节落点）
  - path: agate/assets/review-roles/qa.md
    why: review-role frontmatter/产出/status 门槛映射模式（judge.md 模板参照）
  - path: agate/WORKFLOW.md:288-296
    why: 阶段总览表形态（P6.5 行落点）
  - path: agate/role-system.md:37-51, 108-116
    why: 评审名册表 + status 三值映射（judge 登记与复用）
  - path: agate/tests/conftest.py
    why: task_dir/agate_scripts/python_exe/run_cli fixtures（新测试文件复用）
```

```yaml
minimal_validation:
  assumption: "新增产出 P6.5-judge-verdict.md 与 P6.5-dispatch-context-judge.md 不被既有 P[0-8]-* glob/正则消费面误拦或漏扫，且命名能通过现有校验通道"
  method: "静态 grep 实证（本设计 §1 客观证据）：① pre-commit-gate.py L78 `_P_OUTPUT_RE = P[0-8]-.*\\.md$` 与 L487 step3 正则 `^(.*)/P[0-8]-[^/]+\\.md$` 均不匹配 P6.5-* → verdict commit 不会触发'产出与 phase 不一致'假警告 ② 2n.2 非证据拦截（L439-454）只拦非 .md/.yaml 文件（L77 `_NON_MD_YAML_RE`）→ verdict/dispatch-context 两个 .md 在 phase=P6 暂存不被拦 ③ 2p dispatch-context glob（L353 `phase + \"-dispatch-context-*.md\"`）不覆盖 P6.5-* → 卡片 hash 校验不强制（内容合规由 check-judge-verdict 白名单扫描承担）④ agate-state-yaml-check L17 valid_phases 不含 P6.5 → 误写 phase: P6.5 会被拦（fail-closed）⑤ 既有协作规范 glob `P[0-8]-*.md`（provenance L504）不匹配 verdict → verdict agent 字段检查跳过（由 check-judge-verdict 独立校验，无双源分叉）"
  result: "confirmed"
  note: "本设计为纯代码逻辑/静态判定（Python 脚本 + Markdown 协议文档 + pytest），无外部系统依赖（无浏览器/网络/服务/端口）。依赖的内部函数与数据转换：check-p6-provenance.py 审计 2/3 的扫描与计数口径（AGATE_CARD/frontmatter 双排除、`^#### BDD-[0-9]` 计数）、check-p6-evidence.py._md5_entries（md5 去重）、agate_common.write_gate_result/read_state_phase（事件写入参照）、pre-commit-gate 的 2i/2n 注入模式与 _NON_MD_YAML_RE/_P_OUTPUT_RE、agate-state-yaml-check 的字段校验范围（unknown 顶层键忽略、retries key ^P\\d+$）、check-state-transition.phase_num（数字提取语义）、check-protocol-consistency CHECK 2（PROTOCOL_DIRS 扫描面）/CHECK 12（_RETRY_TABLE_ROW_RE 不匹配 P6.5）"
```

## 6. 实现完成的标志（供 P3 测试设计与 P5 验证）

- [ ] `check-judge-verdict.py` + `check-events.py` + `agate_common.append_event/read_judge_verdict/GENESIS_HASH` 落地，`check-gate.py` 含 `"P6.5": gate_p65` 分支（历史任务早退 / verdict 缺失 exit 1 / 双脚本校验）
- [ ] pre-commit-gate.py 含 P6.5 注入（judge.enabled && verdict 存在 → 两脚本任一失败阻断）+ gate_run/state_transition 事件写入
- [ ] ci-gate-backstop.py 含 judge/events 兜底
- [ ] 协议文档全部落点完成：judge.md / WORKFLOW P6.5 行 / state-machine P6.5 描述行 + judge 条件 / dispatch-protocol 信息隔离节 / P6 卡 P6.5 门槛 / dispatch-prompt Judge 追加节 / role-system 名册 + status 映射说明 / AGENTS 角色清单 / LIMITATIONS 引用
- [ ] 新测试 test_check_judge_verdict.py / test_check_events.py + test_check_gate.py 增补全绿；既有 P6 回归全绿
- [ ] `check-protocol-consistency.py --strict-errors-only` → 0 ERROR；`count-tests.sh` 用例数记录更新（不漂移口径）
- [ ] dogfood 验证（设计文档 §9 Phase 1 对齐）：对启用 judge 的任务全链走通 P6 → P6.5 → P7；对历史任务（无 judge.enabled）确认跳过

## 7. 标注

- `[SUGGEST: 采纳]` P1 §3 两条建议：① LIMITATIONS.md 局限 3 补 judge 引用（列入 §1.1 改动表）② P6.5 挂载优先"P6 门槛内嵌强制判定 + 独立计数"（即选候选 1，本次设计正式采纳，理由见 §2 权衡）
- 无新隐含需求需 `[SCOPE+]`：P1 §3/§4 已覆盖 dispatchers 扩展（ci-gate-backstop 兜底）、角色清单登记（AGENTS.md）、dispatch-prompt 追加节；本设计未发现 P1 未预见的必须项
- 未决点（P3/P4 细化，不阻塞）：① verdict 正文结论行格式细节（PASS/FAIL/NEEDS-REVISION 逐 BDD 行的精确语法，P3 test-designer 定）② 白名单外路径引用的提取正则在 P3 用测试固化误报/漏报边界 ③ judge_token_budget 字段的存放位置（.state.yaml judge 块可选字段，P4 实现时确认）