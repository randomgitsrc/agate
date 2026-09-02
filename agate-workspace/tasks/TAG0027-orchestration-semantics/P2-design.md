---
phase: P2
task_id: TAG0027
type: design
parent: P1-requirements.md
trace_id: TAG0027-P2-20260902
status: draft
created: 2026-09-02
agent: architect
candidate_count: 2
packages:
- agate-protocol
domains:
- backend
- cli
- api
ui_affected: false
dispatch_plan: {mode: static-batch, parallel_limit: 4, batches: [{id: B1-core-rules-cli, complexity: high}, {id: B2-render-audit, complexity: high}, {id: B3a-docs-clean, complexity: medium}, {id: B3b-guardrail-scripts, complexity: high}]}
---

# TAG0027 方案设计 — 编排语义统一落地（RM-AG0054）

> 设计对象 = worktree `agate/` 协议本体（分支 feat/TAG0027-orchestration-semantics）。
> 上游 = P1-requirements.md（25 BDD 语义权威）+ design v3b §4/§5/§6（形态来源）+ P1 评审 4 条
> 边界观察（§6 显式处理）。影响面梳理的落点全部经实读代码确认（P2-progress.md 调查记录，
> 重试轮采信）。

## 1. 影响面梳理（改什么 / 不改什么 / 风险在哪）

### 1.1 改什么（Modify）

| 文件（worktree `agate/` 下）| 改动落点（小节/函数）| 内容 | 关联 BDD |
|------|------|------|------|
| `rules/phases.yaml` | 9 个主线条目（P0-P8）| 每条目新增 `next:` / `retreat:` 键（值域见 §3.1）| BDD-1/3/5 |
| `rules/phases.yaml` | P6.5 条目（92-101 行）| 新增 `gate_subphase:` 结构（不写 next/retreat）| BDD-2 |
| `rules/schema/phases.schema.json` | items.properties（14-63 行）| 声明 `next` / `retreat` / `gate_subphase` 三个新属性（additionalProperties:false 现状必须同步，否则 S-5 ERROR）| BDD-1/2/5 |
| `WORKFLOW.md` | S1S2-ANCHOR 内阶段总览表（287-304 行）| 表加 `next` / `retreat` 两列（P6.5 行列 `—（gate_subphase）`；READY 行不加）| BDD-1/4 |
| `WORKFLOW.md` | 「已知适用环境」表（141-148 行）等平台名元信息行 | 护栏 1 豁免结构标注（§3.8），不改内容 | BDD-16/17 |
| `scripts/check-structure-consistency.py` | `_parse_workflow_rows`（116-131 行）→ 返回 `(id, name, role, next, retreat)`；`_check_s1`（153-171 行）| 扩展 S-1：YAML next/retreat ↔ 总览表 4/5 列；P6.5 gate_subphase 形态语义检查（§3.2）| BDD-1/3/4 |
| `scripts/check-gate.py` | **不改返回约定**；P6.5 分发函数若需读 gate_subphase 只做消费（§3.1 兼容声明）| 如需，仅按需读取新字段，exit 0/1/2 语义原样 | BDD-13 |
| `scripts/agate-next.py`（新增）| 推进 CLI（exit 0/1/2 三态分支）| §3.4 契约 | BDD-6/7/8/9/11 |
| `scripts/agate-advance.py`（新增）| 手动/多阶回退引导 CLI | §3.4 契约 | BDD-7/10 |
| `scripts/agate-dispatch.py`（新增）| 渲染时注入单命令 CLI | §3.5 契约 | BDD-18/20/25 |
| `scripts/check-p6-provenance.py` | 审计 2（318-355 行）| 双锚点剥离（CARD-SOURCE 行起物理块优先 + START..END 兜底，A2 定案 (a)，§3.6）| BDD-20/21 |
| `scripts/check-judge-verdict.py` | P6.5 校验逻辑 | 复核范围含 exit2-resolution（§3.3 挂载点）+ `_strip_card`（98-111 行）双锚点剥离同步（CARD-SOURCE 行起物理块优先，A2 消费方同步面 §3.6）| BDD-12/20 |
| `scripts/check-protocol-consistency.py` | 新增 CHECK（护栏 1 机械化）| §3.8 段落级判据 CHECK 14 + 数据面 CHECK 15 | BDD-15/16/22/24 |
| `loop-orchestration.md` | 档位 C 推进点（227-243 行）| 推进改走 `agate next`（§3.7）| BDD-11 |
| `assets/templates/dispatch-context.md` | 模板 | 增渲染来源说明 + 占位符注释（§3.5）| BDD-18/20/25 |
| `agate/*.md` 平台名存量（9 文件）| P1 D-2 三分类清单 | 清理 / 挂「实现注记」/ 豁免（§3.8 + §6③）| BDD-16/17 |
| `agate/tests/` | 新增 pytest 文件（按 §9 dispatch_plan 分 4 批）| 覆盖 25 BDD | BDD-1~25 |

### 1.2 不改什么（Not Modify）

| 对象 | 理由 |
|------|------|
| `scripts/check-gate.py` 返回约定（exit 0/1/2）| P1 约束 1 + BDD-13 硬边界；新 CLI 只做**消费方**（子进程读 exit code）|
| `scripts/check-state-transition.py` 返回约定（exit 0/1）与检查语义 | 同上；`agate next` 推进的合法性校验由 commit 时 pre-commit hook 消费暂存 diff 完成（不复制校验逻辑）|
| `scripts/agate-retreat-to.py` / `agate-retreat-state.py` | 既有单步回退自动化（逐阶归档 + retry + 独立 commit）；`agate next` exit 1 分支**调用**而非重写（BDD-7/10）|
| `scripts/agate-next-card.py`（不改名、不改 CLI 契约）| D-6 防混淆靠文档 + CLI 帮助区分；`agate dispatch` 以子进程方式**复用**它取卡片（M3 渲染）|
| 存量任务 dispatch-context（591 处物理占位符）| 约束 5：本次**不迁移**；手工兜底 + 审计 2 文件版逻辑继续覆盖（BDD-19/21/25）|
| P6.5 judge 机制本身（check-judge-verdict / check-events 主体）| out-of-scope（P0）；exit2-resolution 只挂到 judge **复核范围**，不加独立机制（BDD-12）|
| `agate-render-dispatch-prompt.py` 既有 CLI 契约（PHASE ROLE TASK_DIR [--rollback]，exit 0/1/2）| BDD-23；独立渲染场景（P{N}-dispatch-prompt-{role}.md）与方案 A 路径互不替代 |
| dispatch-protocol 五模式本体（511-519 行）| out-of-scope：不重构、不发明"workflow 模式 / ralph 模式"概念（BDD-14）|
| 平台食谱产品化 / 门户 | P0 out-of-scope |
| `rules/dispatch.yaml` law-1 的 task 指代行 | 属 Phase 3 文档清理对象（§6②），**不是**改数据面 schema |
| schema_version: 1 / retry_cap enum [2,3] | 无版本/枚举变更需求，避免连带破坏 |

### 1.3 风险在哪（Risk）

| # | 风险 | 缓解 |
|---|------|------|
| R1 | phases.yaml 加键但 schema 未同步 → S-5（additionalProperties:false）全量 pytest 红 | BDD-1/5：schema 扩展与 phases.yaml 改动同批原子落地（B1）；gate_commands.P5_schema 独立 key 拦截 |
| R2 | WORKFLOW 总览表加列破坏 S-1/S-2 既有解析 | 实证：`_TABLE_ROW_RE` 不锚行尾、只取前 3 列 → 加列天然兼容（§3.2 实证结论）；加列时同步扩展 `_parse_workflow_rows` 取 4/5 列并加回归测试（故意不一致 → S-1 ERROR）|
| R3 | `agate next` 直接改 .state.yaml 绕过 check-state-transition 校验 | 设计为：CLI **只改工作区 .state.yaml 并 git add**，合法性与 retry 同步由 pre-commit hook 的 check-state-transition（git diff --cached）拦截——与手动推进同一条机械路径，不复制校验 |
| R4 | exit 1 回退的 retry 记录与既有语义不一致（RM-AG0042 要求单步回退追加 retries[target]）| 回退一律走 `agate-retreat-to.py`（其内部逐阶 write_retreat 已同步 retries + commit，state-machine.md:615-658 + check-state-transition BDD-2 拦截）；CLI 不自己写 retries |
| R5 | P6 exit 2 特例被误泛化到其它 phase | 特例判定硬编码 `phase == "P6" and FAIL==0 and provenance exit 0`（state-machine.md:139），其余 phase exit 2 一律通用暂停语义；回归测试锁 P6 与非 P6 两分支（BDD-8/9）|
| R6 | MAX_RETRY_MAP（agate_common:44）无 P6.5 键，P6.5 重试上限易读错 | P6.5 的 retry 上限**不依赖 map**，读 phases.yaml P6.5 条目 `retry_cap: 2`（与 judge 轮次 ≤2 一致）；新 CLI 的 P6 分支按 A1 裁决跑 gate_p65 判定 judge 复核（.state.yaml phase 仍是 P6，复核通过才推 P7，§3.1/§3.4）|
| R7 | 渲染产物 dispatch-context 破坏 pre-commit-gate.py 2p 卡片 hash 校验 / provenance 冻结 | `agate dispatch` 输出与模板结构一致：frontmatter phase/generated_by/task_id/role + AGATE_CARD_START/END 内完整卡片（与 agate-next-card.py 输出逐字一致）→ 2p 抽取的物理块可 hash；**CARD-SOURCE 标记置于 START 前（块外），不进 `_extract_card` 抽取区间（A2 定案 (a)）**；审计 2 双锚点剥离（§3.6）|
| R8 | 护栏 1 CHECK 上线即对存量全红（0 处实现注记）| CHECK 与存量清理**同批落地**（B3a 先清/标 → B3b 上 CHECK）；豁免结构先行（platform-notes/SETUP 整文件 + WORKFLOW 适用环境表 + **assets/templates/dsh/ 平台食谱目录（A3）**）；上线首跑 = 0 命中基线 |
| R9 | `task` 禁词误伤数据面既有键（task_fields 等）| 词边界正则 + 数据面豁免词典（§3.8.2）：豁免 = 既有键名/值域上下文（task_fields/task_id/tasks 目录引用），豁免清单**从 schema + phases.yaml 机械生成**，不手抄 |
| R10 | adr.md 豁免理由错误（评审观察④）| §6④：ADR-008 平台名按**实现注记**挂载（决策叙事），不做整文件豁免；docs/reviews NARRATIVE 豁免面与 agate/ 协议区分开声明 |
| R11 | BDD-10 示例误导（P7→P4 跨 3 阶）| 约束 8①：P2/§3.4 明确示例语义 = P6→P4（diff=2，retreat 表值 P4，机械落地由 retreat-to 逐阶 P6→P5→P4——每步 diff=1 独立 commit，CLI 不预判 diff，不触发 check-state-transition 拦截）；人工直接跳转 diff≥2 一律先 PAUSED（check-state-transition 拦截）|
| R12 | 档位 C 硬中断点被 retry 语义覆盖 | loop-orchestration.md 硬中断点（50-63 行）语义保持：exit 2 → 转主 Agent + exit2-resolution，不自动 retry；档位 C 更新只替换推进判定调用点（§3.7）|
| R13 | 双工作区工具面混淆（worktree 脚本 vs ~/.agate 稳定版）| env_constraints + files_to_read 显式标注：编排/派发工具用 ~/.agate（I-16），check-protocol-consistency 用 worktree 版本；commit 消息 self-gate-review 标注（I-15）|

## 2. 候选方案与权衡

P1 把 8 个设计决策面（objective_info B 节）留给 P2。经方案探索，整体实现路线收敛为 2 个候选：

### 候选 A（采纳）— 数据面权威 + 薄 CLI 消费方（最小侵入）

形态组合：
- 转移表：`phases.yaml` 每条目加 `next`/`retreat`（P8 `next: null`），P6.5 用 `gate_subphase` 表达非独立门槛，schema 值域枚举锁定；S-1/S-2 复用扩展（不新开检查）。
- CLI：新增 3 个**薄脚本** `agate-next.py` / `agate-advance.py` / `agate-dispatch.py`，各自消费既有资产（check-gate.py 子进程 exit code、retreat-to 子进程调用、next-card 子进程取卡），不复制、不重写既有语义。
- exit 2：任务目录落盘 `{phase}-exit2-resolution.md`；复核挂载 = check-judge-verdict.py 既有校验扩展（不新增机制）。
- 渲染：`agate dispatch` = 模板骨架 + Lazy Injection（卡片在渲染时拼装 + CARD-SOURCE 标记）；手工路径（inject-card 占位符）保留。
- 护栏 1：进既有 check-protocol-consistency.py（CHECK 14/15），结构性判据 + 豁免结构。

**优点**：每个改动落在既有消费链的"新增消费方"位置，check-gate / check-state-transition / retreat-to / next-card / inject 均不改语义 → 回归面最小；SELF-GATE 触发面可控；符合 P1 全部 out-of-scope（不新开检查、不改返回约定、judge 机制不动）。
**缺点/风险**：CLI 入口分散（3 个脚本 vs 1 个总控）；推进的可观测性靠每次 commit + gate-events 事件累积（需 BDD-11 证据约定）；judge 挂载需动 check-judge-verdict.py 一处校验。

### 候选 B（陪衬）— 中心编排控制器（agate-flow 单一入口）

形态组合：新建一个 `agate-flow.py` 总控，把推进决策、回退、retry、exit2 落盘、渲染注入全部内聚成单一 CLI 状态机；内部自维护转移表副本与 retry 账本。
**优点（真实维度上更好）**：单一可观测控制点，CLI 面最少，档位 C 对接只改一处。
**缺点**：与 P1 约束 1/约束 5 直接冲突——要么复制 check-state-transition/check-gate 语义（双源漂移风险，违反"不新开独立检查"精神），要么改写既有脚本返回约定（BDD-13 禁止）；转移表副本与 phases.yaml 双源同步是高频漂移源（state-machine.md 权威源纪律）；SELF-GATE 回归面放大一个数量级；worktree 并行批实现互相踩同一文件。
**否决理由**：候选 B 的唯一真实优势（单一入口）可用候选 A 的薄 CLI + 事件账本（append_event）等价获得，而候选 B 的代价全部落在 P1 硬约束上 → 不可行。

**选择**：候选 A。设计决策面 §3 的每个"形态定案"给出被否形态与理由，形成逐面诚实权衡。

> 注：8 个设计决策面的其余备选形态（如 P8 next 用 READY、exit2-resolution 塞 .state.yaml、审计 2 只认标记不留物理兜底等）在 §3 各节以「备选形态（否决）」呈现，避免稻草人。

## 3. 设计决策面定案（8 项）

### 3.1 决策面 ①：next/retreat schema 形态（BDD-1/2/3）

**定案（形态 D1-A）**：主线 P0-P8 每条目新增两键；P6.5 条目新增 `gate_subphase`（不写 next/retreat）：

```yaml
# phases.yaml 主线条目新增（示例 P5 条目）：
- id: P5
  name: 技术验证
  exec_role: verifier
  outputs: [{file: P5-test-results/unit.md, required: true}]
  gates: [...]
  retry_cap: 2
  task_fields: []
  next: P6
  retreat: P4        # P5/P6 gate 失败 → P4（state-machine.md:132/148）
# P8 条目（无后继例外）：
  next: null         # P8 无自动后继：exit 0 后转 READY 由人/发布流程处理（值域含 null）
  retreat: null      # P8 失败无跨阶回退：exit 1 → 重试 P8（retry+1 本阶段）

# P6.5 条目（92-101 行，新增 gate_subphase 结构，非独立转移边）：
- id: P6.5
  name: 独立 Judge 复核
  exec_role: judge
  outputs: [{file: P6.5-judge-verdict.md, required: true}]
  gates: [...]
  retry_cap: 2
  task_fields: [status, criteria_total, criteria_passed, verdict_evidence]
  gate_subphase:
    hosted_on: P6          # .state.yaml phase 保持 P6 直至 P7（state-machine.md:74-78）
    forward_to: P7         # judge 通过 → P7
    needs_revision_to: P6  # needs-revision → P6 重验（judge 轮次 ≤2，state-machine.md:151-157）
```

**P6 主线 next 条件式裁决（A1 定案）**：P6 条目 `next: P7`——值域合法（P6 的转移目标就是 P7；
P6.5 非独立 phase 不入 next 值域，schema 不含 P6.5）。但 check-gate.py `gate_p6`（1051-1093 行）
**恒 exit 2**（P6「通过」= FAIL=0/证据非空 + check-p6-provenance exit 0，无 exit 0 分支）→ P6→P7
**不是 exit 0 直推可达**，而是**条件式推进边**：`agate next` 在 `.state.yaml phase == P6` 时按以下
裁决消费 `next: P7`——
1. 子进程跑 check-gate.py P6：exit 2 且 check-p6-provenance.py exit 0 → P6 验收通过
   （state-machine.md:139）；exit 1 → 走 §3.4 exit 1 retreat 分支；
2. 查 .state.yaml `judge.enabled`：未启用（历史任务）→ gate_p65 早退 exit 0（judge 跳过）→
   裁决成立；
3. 启用 → 子进程跑 `check-gate.py P6.5 {TASK_DIR}`（= P6.5-judge-verdict.md 存在 +
   check-judge-verdict.py + check-events.py 双 exit 0）：exit 0 → **裁决成立** → 消费 next:P7、
   更新 .state.yaml phase 为 P7（append_event `state_transition`）+ git add（跳变合法性仍由
   pre-commit check-state-transition 校验，R3 同链）；exit 1 → 裁决不成立 → 停留 P6，输出
   「judge 复核未过（缺 verdict 或 verdict 校验失败；轮次 ≤2 超限人工接管）」提示，不推进。

即：**P6.5 门槛（gate_p65 exit 0）是 P6.next:P7 的前置条件**，CLI（agate-next.py P6 分支，§3.4
exit 2 P6 特例）是 `gate_subphase.forward_to` 的机械消费方；schema 侧无需表达（next: P7 值域
合法），裁决逻辑在 CLI 分支。

schema 声明（phases.schema.json items.properties 增三键）：
- `next`: `{"oneOf": [{"$ref": "#/definitions/phaseId"}, {"type": "null"}]}`（phaseId = `enum [P0..P8]`，**不含 P6.5**——P6.5 不是主线 next 目标，保证不出现 `next: P6.5` 的独立边写法）；required 条件：id ∈ P0-P8 → next/retreat 必填。
- `retreat`: 同 phaseId 联合 null。
- `gate_subphase`: object，必填 hosted_on/forward_to/needs_revision_to，值域 phaseId；required 条件：id = P6.5 → 必填且不得有 next/retreat（schema `not` 或 required-if 表达——draft-07 subset 用 `if/then`）。
- **P6 条目 `next: P7` 合法但推进为条件式**：P6 恒 exit 2 无 exit 0 直推，`next: P7` 由 §3.1「P6 主线 next 条件式裁决」+ §3.4 exit 2 P6 特例消费（gate_p65 exit 0 前置）——schema 只管值域（P7 ∈ phaseId），不管裁决。
- **跨阶回退由 retreat-to 逐阶落地（B1 口径）**：retreat 表值来自 state-machine.md 转移规则——P5→P4（state-machine.md:132，diff=1）、P6→P4（state-machine.md:148，**diff=2**，表内唯二非相邻目标）均写 `retreat: P4`；P6→P4 的 diff=2 不触发 PAUSED，因机械落地走 `agate-retreat-to.py` 逐阶（`while n>target_n: nxt=n-1`，P6→P5→P4 每步 diff=1 独立 commit，state-machine.md:647-654 的 diff≥2→PAUSED 是"人工直接跳转"路径，与 retreat-to 自动化逐阶不同轨）；**CLI 不预判 diff，只按 retreat 表值存在 → 委托 retreat-to**（§3.4）。其余表内不写的多步直退（diff≥2 且无 retreat 表值）由 check-state-transition.py 强制 PAUSED（BDD-3）。

**备选形态（否决）**：a) P8 next 写 `READY`——READY 非 phase id、值域引入状态混入，且 S-1 表行无 READY next 概念 → 用 `null` 更纯；b) 自由字符串值域（不枚举）——S-1/S-2 无物可比、BDD-3 无法机械核对 → 值域枚举 + null 双形态；c) P6.5 也写 `next: P7`——违反 state-machine.md:74-78 非独立口径（BDD-2 直接 FAIL）→ 否决。

### 3.2 决策面 ②：S-1/S-2 md 侧扩展（BDD-1/4）

**实证结论（兼容性）**：`_TABLE_ROW_RE = ^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|` 不锚行尾、group(1..3) 只消费前 3 列 → **总览表追加第 4/5 列不影响既有 S-1（id/name/exec_role 比对）与 S-2（phase 存在性反查）**。加列是向后兼容扩展，无需改正则。

**定案（形态 D2-A，加列位置 = B2 统一为 4/5 列）**：WORKFLOW.md S1S2-ANCHOR 内总览表（287-304 行）
在「执行角色」后加两列（next/retreat 落**第 4/5 列**，既有「评审角色」「门槛」顺延为第 6/7 列）：

```markdown
| 阶段 | 名称 | 执行角色 | next | retreat | 评审角色 | 门槛（…）|
|------|------|----------|------|---------|----------|----------|
| P5 | 技术验证 | verifier（P5 模式，subagent 派发）| P6 | P4 | … | … |
| P8 | 发布准备 | implementer（P8 模式/releaser…）| —（无自动后继）| —（失败重试本阶段）| … | … |
| P6.5 | 独立 Judge 复核 | judge（…）| —（gate_subphase: 通过→P7）| —（needs-revision→P6）| … | … |
```

> 列位语义（S1S2-ANCHOR 注释同步，B2）：第 1-3 列 = 既有 id/name/exec_role（S-1/S-2 比对列，
> `_TABLE_ROW_RE` 只消费前 3 列不受影响）；**第 4/5 列 = 新增 next/retreat**（S-1 扩展比对列）；
> 第 6 列起 = 评审角色/门槛等人类可读列，S-1 不比对。示例/正文/解析器取列三处一致。

- READY 行不加 next/retreat 列内容（S-2 已排除 READY）。
- `_parse_workflow_rows` 扩展返回 5 元组 `(id, name, role, next_cell, retreat_cell)`（行 split 后取 4/5 列，缺列取空）；`_check_s1` 增比对：YAML `next` 规范化（`null` ↔ `—（无自动后继）`/空；P6.5 走 gate_subphase 特判）↔ 表列。
- P6.5 的 S-1 语义检查 = `gate_subphase.hosted_on/forward_to/needs_revision_to` 与表 P6.5 行 next/retreat 列注释一致（形态级校验，不逐字比对注释文本——注释是人类可读，机器判据以 YAML 为准；md 侧仅验证"P6.5 行不出现指向独立后继 phase 的 plain `P7` 值"）。
- WORKFLOW.md「阶段总览」表头锚点注释（288 行）同步说明：第 4/5 列为 next/retreat（执行角色后），评审角色/门槛顺延第 6/7 列（B2 列位语义，见上）。

**备选形态（否决）**：a) 另起一张转移表（放 state-machine.md）——S-1/S-2 锚点是 WORKFLOW 总览表（287-304），另起表 = 双锚点漂移风险且 S-1 脚本要改扫描目标；b) md 侧不表达、只靠 YAML——I-4 要求 md 侧锚点表达新字段否则 S-1 无物可比（BDD-4 制造不一致场景无法检出）→ 均否决。

### 3.3 决策面 ③：exit2-resolution 落盘格式/位置 + judge/provenance 复核挂载点（BDD-8/9/12）

**定案（形态 D3-A）**：
- **位置**：任务目录下 `{phase}-exit2-resolution.md`（与 P{n}-dispatch-context-*.md 同目录同族；文件名可被 pre-commit 强制与归档脚本顺带覆盖）。
- **格式**：frontmatter（机器可读）+ 正文留痕：

```markdown
---
phase: P6
task_id: TAGxxxx
type: exit2-resolution
parent: .state.yaml
created: 2026-09-02T12:00:00Z
agent: main-agent            # 解决人 = 转交的主 Agent（exit 2 暂停后由主 Agent 决策）
---
# P6 exit2-resolution

## 触发
- 时间: <ISO8601>
- 触发命令: check-gate.py P6（exit 2）
- gate 输出摘要: <非空证据 / FAIL 计数等客观证据>

## 客观证据
- <exit 2 依据：如 check-gate 输出、provenance exit code、证据文件清单>

## 解决
- 解决人: <主 Agent / 角色名>
- 结论: <继续 / 回退 / 修正后重验>
- 依据: <客观证据交叉引用>
```

- **不落 .state.yaml**：.state.yaml 嵌套字段写入一期被 agate-md-field-set 拒绝（NO_FALLBACK_LIST/JSON），且 .state.yaml 的 schema/校验面复杂 → 独立文件 + frontmatter 更稳（机器读取用 agate-md-field-get）。
- **不新增 events 类型**：既有 `gate_run`（exit:2）事件已记录"何时"，exit2-resolution 文件补"依据/由谁"；复核挂载点不扩展 check-events.py 事件账本。
- **复核挂载**：`check-judge-verdict.py` P6.5 校验新增一项：若 gate-events.jsonl 含 `event:gate_run, exit:2` 且 `phase == 当前任务历史 Pn`（P6.5 复核时），则任务目录须存在对应 `{phase}-exit2-resolution.md` 且 frontmatter/必填节完整（触发时间/客观证据/解决人/结论），缺失或格式非法 → judge verdict 不通过（BDD-12）。**P6 自身 exit 2 前进特例不落盘**（BDD-9：FAIL=0/证据非空 + provenance exit 0 时直通，该 gate_run 的 exit:2 不带 exit2-resolution 要求——特例判定在 CLI 分支完成，judge 挂载对 P6 特例豁免）。

**备选形态（否决）**：a) 塞 .state.yaml 新字段——嵌套/追加写入受限 + 状态文件语义膨胀 + pre-commit 2p hash 面扩大；b) check-events.py 扩展 `exit2_resolution` 事件类型——改动事件账本哈希链 + 类型白名单 + ts 单调校验（judge 机制本身不动约束）→ 否决，选 judge verdict 扩展（既有消费面，I-13）。

### 3.4 决策面 ④：agate next / agate advance CLI 契约（BDD-6/7/8/9/10/11/13）

**定案（形态 D4-A）**：两个独立薄脚本（worktree `agate/scripts/` 新增；`~/.agate` 由发布流程同步）：

`agate-next.py [TASK_DIR]`（默认 TASK_DIR = 当前任务目录）：
1. 读 `.state.yaml` 取当前 phase（`read_state_phase`）；phase ∈ {PAUSED, READY, DONE} → 提示并 exit 0（不推进）。
2. 子进程跑 `check-gate.py {phase} {TASK_DIR}`，读 exit code **三态**：
   - **exit 0（通过）**：查 phases.yaml `next` 字段。`next: Pn+1` → 更新 .state.yaml phase 为 Pn+1（保留 judge/retries 块，append_event `state_transition`）+ `git add .state.yaml` + 提示 commit（**不自行 commit**——让 pre-commit hook 对暂存 diff 跑 check-state-transition.py 校验跳变合法性，与手动推进同一机械路径，R3 缓解）。`next: null`（P8）→ 提示转 READY/发布流程，不推进。
   - **exit 1（未通过）**：查 phases.yaml `retreat`。`retreat: Pt` 存在（P5/P6→P4 等，含表内
     diff=2 的 P6→P4）→ **调用 `agate-retreat-to.py {TASK_DIR} {Pt} "gate exit 1 按转移表回退"`**
     ——retreat-to 内部逐阶（P6→P5→P4 每步 diff=1 独立归档 + retry 记录 + commit，state-machine.md
     647-654 的 diff≥2→PAUSED 是人工直接跳转路径，与 retreat-to 逐阶自动化不同轨），**CLI 不预判
     diff**（B1 口径：委托后由 retreat-to 逐阶处理，P6→P4 的 diff=2 天然合规不触发
     check-state-transition 拦截）。`retreat: null` → 提示重试本阶段（retry+1 由主 Agent 走既有流程）。
   - **exit 2（需自判）**：若 `phase == P6` 且满足 state-machine.md:139（FAIL=0 / 证据非空 +
     check-p6-provenance.py exit 0）→ **P6 特例分支（A1 裁决，§3.1「P6 主线 next 条件式裁决」）**：
     ① 查 .state.yaml `judge.enabled`；未启用 → 直接消费 `next: P7`（judge 跳过，gate_p65 早退 0）；
     ② 启用 → 子进程跑 `check-gate.py P6.5 {TASK_DIR}`（= P6.5-judge-verdict.md 存在 +
     check-judge-verdict.py + check-events.py 双 exit 0，即 gate_subphase.forward_to 门槛）：
     exit 0 → **推进裁决成立** → 更新 .state.yaml phase P6→P7（append_event `state_transition`）+
     git add + 提示 commit；exit 1 → 停留 P6，输出「judge 复核未过：缺 verdict 或 verdict 校验
     失败/账本审计未过（judge.rounds ≤2，超限人工接管）」指引，不推进、不落盘 exit2-resolution
     （P6 特例豁免落盘，BDD-9）。若 P6 特例条件不满足（provenance exit 1 / 证据空）→ 按通用
     exit 2 语义处理。否则（非 P6）通用语义：**不推进**，落盘 `{phase}-exit2-resolution.md`（§3.3
     模板，若已存在则提示更新），输出暂停转主 Agent 提示，exit 0（CLI 成功完成"暂停动作"，由主
     Agent 决策后续）。
3. 每步 append_event（`gate_run` 已由 check-gate 自身/或 CLI 记录 + `state_transition`），作为档位 C 可观测证据（BDD-11）。

`agate-advance.py [TASK_DIR] [--to {phase}] [--reason {text}]`：
- 手动/多阶回退引导：`--to` 目标与当前 diff ≥ 2 时提示"diff≥2 须先 PAUSED（check-state-transition 会拦截直退）"，引导跑归档 + 置 PAUSED；diff=1 时等价调用 retreat-to 单步；不传 `--to` 时仅打印转移表建议（当前 phase 的 next/retreat）。
- 与 `agate-retreat-to.py` 边界：advance **不内联**回退实现，只做目标解析 + 合法性提示 + 委托（约束 I-7：复用而非重造）。

**备选形态（否决）**：a) `agate next` 自行 commit——commit message 语义（self-gate-review 标注等）与 hook 链由主 Agent commit 统一管理，CLI 自 commit 会绕过 commit-msg hook 约定 → CLI 只 add 不 commit；b) advance 内联多阶回退循环（逐阶自写归档/retry）——与 retreat-to 双实现漂移 → 委托。

### 3.5 决策面 ⑤：agate dispatch CLI 契约（BDD-18/19/20/23/25）

**定案（形态 D5-A，来源标记位置 = A2 定案 (a)）**：新 `agate-dispatch.py`，CLI：`agate-dispatch.py {phase} {role} [TASK_DIR] [--guide FILE]`（phase ∈ P1-P8，不含 P0/P6.5——与 render-dispatch-prompt 白名单一致）：
1. 读 `assets/templates/dispatch-context.md` 模板骨架。
2. **Lazy Injection**：子进程调 `agate-next-card.py {phase}` 取完整当前阶段卡片（正式卡片原样 / 裸模板卡片 M3 渲染），渲染文件结构为：

   ```markdown
   <dispatch_guide>…（模板骨架 + guide 注入）…</dispatch_guide>

   <!-- CARD-SOURCE: agate-dispatch.py {phase} -->   ← 渲染层来源标记，放 AGATE_CARD_START **之前**（块外）
   <!-- AGATE_CARD_START -->
   ## 当前阶段卡片：{phase} …（agate-next-card.py stdout 全文逐字，含 header + 卡片正文）
   <!-- AGATE_CARD_END -->
   ```

   CARD-SOURCE **不进入** `AGATE_CARD_START..END` 抽取区间 → pre-commit 2p 的 `_extract_card`
   （只抽 START..END 之间）嵌入内容不变 = next-card stdout → **2p hash 不受影响**（A2 机制，
   BDD-25 转绿依据）；CARD-SOURCE 与卡片正文的分隔 = START 标记行。
3. 渲染文件写入 `{phase}-dispatch-context-{role}.md`（任务目录；无 TASK_DIR 时写当前目录），frontmatter 保持 `phase` / `generated_by: agate-dispatch.py + 主 Agent` / `task_id` / `role`（I-10 兼容——与模板默认 `generated_by: agate-inject-card.py + 主 Agent` 的差异是**机器来源字段**，2p 只看卡片块 hash 不看 generated_by；渲染层来源标记另有 CARD-SOURCE 块外注释，见 §3.6——双轨标记均不影响 2p）。
4. exit 0 = 成功（文件含完整卡片块且与 next-card 输出一致）；exit 1 = 失败（phase 非法 / 卡片缺失）。
5. 与既有链关系：**不替代** `agate-inject-card.py`（手工兜底保留，BDD-19）；`agate-card-inject.py` 仅被 inject-card 调用，不动；`agate-render-dispatch-prompt.py` 独立场景（dispatch-prompt 模板渲染）不动（BDD-23）；`agate-next-card.py` 被 dispatch 以子进程复用。
6. 派发文档（orchestrator-template.md / dispatch-protocol.md 派发节）改指 `agate dispatch` 为新主路径，注明手工兜底（Phase 3 文档批次）。

**备选形态（否决）**：a) 修改 `agate-inject-card.py` 支持渲染模式——单脚本双语义混淆既有 CLI 契约 + 手工路径语义被污染 → 新建独立脚本；b) dispatch 输出不含来源标记（审计 2 仍只剥物理块）——BDD-20 Given 要求"卡片块来源在渲染层可标记" → 必须标记；c) CARD-SOURCE 放 START 之后卡片首行 / 替代 START——进 `_extract_card` 抽取区间或致无 START 可抽 → 2p hash mismatch（A2 实证，见 §3.6 备选 c/d）。

### 3.6 决策面 ⑥：审计 2 剥离锚点（渲染产物标记 + 手工物理块并存，BDD-20/21）

**定案（形态 D6-A，剥离锚点 = A2 定案 (a)）**：来源标记 = CARD-SOURCE 注释置于 `AGATE_CARD_START`
**之前**（块外，§3.5 结构图）——不进 START..END 抽取区间、不影响 pre-commit 2p hash（BDD-25）。
`check-p6-provenance.py` 审计 2（318-355 行）剥卡片块的锚点扩展为**双锚点**：
1. **渲染标记优先**：从 `<!-- CARD-SOURCE: agate-dispatch.py {phase} -->` 所在行起、至匹配的
   `<!-- AGATE_CARD_END -->` 止整段剥离（CARD-SOURCE 行 + START + 卡片正文一起剥——渲染产物块
   = "从 CARD-SOURCE 行起的物理块"）。剥离后文件体不含 CARD-SOURCE/START/END/卡片。
2. **物理块兜底**：无 CARD-SOURCE 时走既有 `AGATE_CARD_START` → `AGATE_CARD_END` 剥离（手工 +
   inject-card 注入路径，BDD-21）。
3. 剥离后逻辑不变（剥 frontmatter → 数 `^\s*- (PASS|FAIL)` 预判）。
4. 审计对象扫描从 glob `P6-dispatch-context-*.md`（静态文件）保持同名——渲染产物也落到该 glob（I-10 文件名兼容），**扫描对象面不变**，只改块剥离锚点。

**消费方同步面（A2 定案 (a) 的三处，P4 实现须同步改，机制统一为"CARD-SOURCE 行起物理块优先 +
START..END 兜底"）**：
- `check-p6-provenance.py` 审计 2 剥离（318-355 行块扫描逻辑）——本面上文；
- `check-judge-verdict.py` `_strip_card`（98-111 行，消费点 396-397 行：verdict 信息隔离白名单
  检查前剥离 dispatch-context）——同步加 CARD-SOURCE 优先分支；
- `pre-commit-gate.py` `_extract_card`（171-189 行，2p hash 嵌入抽取）——**只抽 START..END 区间，
  因 CARD-SOURCE 在块外，无需改动**（对照确认：本方案标记不入抽取区间，2p 天然兼容，改动的只是
  审计侧剥离起点）。

**备选形态（否决）**：a) 只认 CARD-SOURCE、删物理块剥离——手工兜底路径（BDD-21）与存量 591 处文件立即误报 → 双锚点并存；b) 用 generated_by 字段区分来源——generated_by 是 frontmatter 键，剥离按块进行，frontmatter 在块剥离后才剥 → 用块外 CARD-SOURCE 标记更可靠；c) CARD-SOURCE 放 START 之后卡片首行——改变 2p `_extract_card` 抽取内容 → hash mismatch exit 1（A2 实证，否决）；d) CARD-SOURCE 替代 START——`_extract_card` 无 START 可抽 → 嵌入空串 → hash mismatch exit 1（A2 实证，否决）。

### 3.7 决策面 ⑦：档位 C 对接（BDD-11）

**定案（形态 D7-A，文档约定层 + CLI 调用点双层）**：档位 C 是主 Agent 执行模式，`agate next` 由主 Agent（或 /loop 编排器）调用——
- `loop-orchestration.md` 档位 C 定义（46-74 行）与 gate 处理流程（229-243 行）更新：pre-commit exit 0 后的"自动进入下一 phase"动作 = 运行 `agate next {TASK_DIR}`（而非主 Agent 临场改 .state.yaml）；exit 1 → `agate next` 自动走 retreat 分支（与档位 A/B 手动路径不冲突，只替换自动判定点）；exit 2 → 停 PAUSED 转主 Agent（硬中断点 50-63 行语义保持，不 retry）。
- **可观测证据（BDD-11）**：`agate next` 每次推进 append_event（`state_transition`，字段 from/to/ts）+ 对应 .state.yaml commit（git log 可查）→ BDD-11 的"When 检查推进记录"落在 gate-events.jsonl / git log，可二值判定"推进均经 agate next 判定"（事件含 cmd 溯源；`gate_run` exit:0 后跟 `state_transition` 记录即证据）。测试用临时任务目录跑两次推进断言事件流。
- 硬中断点仍必停 PAUSED 而非 retry：CLI exit 2 分支不产生 retry 记录（§3.4），文档同步声明。

**备选形态（否决）**：a) 脚本层自动推进（agate next 由 hook 自动跑）——改变 pre-commit 语义、档位 A/B 无差别触发、绕过主 Agent 判断 → 只做文档约定 + 主 Agent 调用点；b) 纯文档不改（档位 C 文字描述"可调用 agate next"）——BDD-11 要求推进记录可观测且"均经 agate next"，文档层 + CLI 落盘两者缺一不可 → 双层。

### 3.8 决策面 ⑧：护栏 1 机械化（BDD-15/16/22/24）

**定案（形态 D8-A）**：`check-protocol-consistency.py` 新增两个 CHECK（结构性判据，不维护文件名单）：

**CHECK 14（markdown 叙述段落平台名扫描）**：
- 扫描对象：`iter_md_files` 遍历的协议 md（`is_protocol_file` 判定；NARRATIVE_DIRS 豁免区不变——agate-workspace/tasks 等已在豁免）。豁免结构：`platform-notes.md` / `SETUP.md` 整文件（平台适配权威源）+ **`assets/templates/dsh/` 平台食谱目录（A3 定案①结构豁免：SKILL.md 等 DSH 平台食谱资产整目录豁免，属 P0 out-of-scope「平台食谱不产品化」的资产落地，非协议叙述文档）** + WORKFLOW.md「已知适用环境」节表行（表行按行级豁免：命中行以 `|` 开头且在豁免表区域 → 跳过）。
- 段落判据：把 md 按标题行/空行切段（代码围栏 ``` 段整体跳过——避免代码示例内平台名误报）；对非豁免段做平台词表扫描（OpenCode / Claude Code / DSH / workflow / ralph / goal / task 词边界正则）。**语义叙述面 = `agate/*.md` 顶层协议文档**（BDD-16/17 排查面所在；assets/ 其余执行角色/评审角色/模板 md 属协议区但非叙述面，仅命中平台适配说明段时按注记处理，见「存量清理批次面」）。
- 命中段若**段落内**（段首至段尾任一行）含 `> 实现注记：` 标记行 → 豁免；否则 ERROR（exit 1）。`> 实现注记：` 统一格式（设计 v3b §4.3 + BDD-16）。
- 结构性：不维护"哪些段落豁免"的文件名单——豁免 = 整文件/整表/带注记行 三类结构 + 平台食谱目录，新增文档自动覆盖（BDD-24）。

**CHECK 15（数据面平台名扫描）**：
- 对象：`rules/*.yaml` + `rules/schema/*.json`（含注释）。
- 词边界正则 + **豁免词典机械生成**：豁免键 = phases.yaml `task_fields` 并集 + schema property 名 + `dispatch.yaml` 既有键（含 `task` 子串的键如 `task_fields`/`task_id` 与其值域语境，§6②）——豁免清单从 schema + rules 解析生成，不手抄（防"新键加入后误报"）。
- 命中数 = 0 为 pass；phase 3 清理后首跑即 0（BDD-15）。

**存量清理批次面（§6③ + A3 定案①）**：清理面 = **顶层协议 md 9 文件**（按 P1 D-2 三分类全部处理：role-system 语义段清理/UPGRADING 元信息转实现注记/…，BDD-17 逐文件判定）+ **assets/ 平台适配说明命中段**（execution-roles/architect.md:229「无 prompt 派发场景」举例、templates/custom-role.md:49-56 平台适配说明——挂 `> 实现注记：`，属平台适配说明叙事）。**assets/templates/dsh/ 平台食谱目录（SKILL.md 等）结构豁免**（不进清理批，CHECK 14 扫描区豁免，A3 定案①）——三者与 CHECK 同批落地（B3a → B3b）。

**备选形态（否决）**：a) 维护逐段白名单文件——BDD-22/24 明示"不依赖维护文件名单"；b) 只扫数据面不扫 md——BDD-16 主战场是 md 叙述面；c) 段落判据用"行级"（命中平台名行上行必须是注记行）——实现注记挂"段落"（BDD-16 用"小节/段落"），行级过严 → 段落级。

## 4. 机器字段与验证契约

### 4.1 gate_commands（P3/P5 独立 key，不塞 &&）

```yaml
gate_commands:
  P3: "python3 -m pytest agate/tests/ -q --tb=short"        # P3 TDD 红灯读取测试运行器
  P5: "python3 -m pytest agate/tests/ -q --tb=no --reruns 1 -n auto"
  P5_timeout_seconds: 600
  P5_consistency: "python3 agate/scripts/check-protocol-consistency.py --strict-errors-only"
  P5_consistency_timeout_seconds: 120
  P5_structure: "python3 agate/scripts/check-structure-consistency.py"
  P5_structure_timeout_seconds: 120
  P5_schema: "python3 agate/scripts/check-yaml-schema.py agate/rules/phases.yaml"
  P5_schema_timeout_seconds: 60
  P5_shellcheck: "shellcheck agate/scripts/*.sh"
  P5_shellcheck_timeout_seconds: 60
  P5_counttests: "bash agate/tests/scripts/count-tests.sh"
  P5_counttests_timeout_seconds: 60
  P5_selfgate: "python3 ~/.agate/scripts/check-protocol-consistency.py --strict-errors-only"
  P5_selfgate_timeout_seconds: 120
```

- 命令均在 worktree 根跑（`python3 -m pytest agate/tests/` 路径口径），脚本调用显式绝对/相对路径；`P5_consistency`/`P5_structure`/`P5_schema` 用 **worktree 自己的脚本**（I-16），`P5_selfgate` 用 **~/.agate 稳定版**（验证稳定版不被破坏——self-gate 双面）。
- P5 全量 pytest 用 `--reruns 1 -n auto`（存量并行偶发 sha256 漂移 1 例，P0 基线；unit/regression/integration 三片合一命令）。
- `P3` 供 check-tdd-red.py 自动读取（P3 阶段）；P5 各 key 独立判定不短路。
- ui_affected: false → 无 P5_e2e。
- P6 验收 gate（check-gate.py P6 / P6.5 内部链 + P5 命令重跑）由阶段 gate 自身执行，不单列 key（P8 逐包命令在 P8 阶段用本 P5 表 + packages）。

### 4.2 files_to_read（P4 implementer 上下文地图，控制体量）

```yaml
files_to_read:
  - path: agate/rules/phases.yaml
    why: 加 next/retreat/gate_subphase 字段的落点（9 主线 + P6.5 条目）
  - path: agate/rules/schema/phases.schema.json
    why: additionalProperties:false 现状，新增键必先声明否则 S-5 ERROR
  - path: agate/scripts/check-structure-consistency.py:74-181
    why: S-1/S-2 _TABLE_ROW_RE/_parse_workflow_rows/_check_s1 加列扩展点
  - path: agate/WORKFLOW.md:283-304
    why: S1S2-ANCHOR 总览表加列 + 行结构（READY 排除、P6.5 行）
  - path: agate/scripts/check-gate.py:1379-1414
    why: main() exit 三态 + OLD_PHASE 语义（新 CLI 消费方只需知道怎么调）
  - path: agate/scripts/agate-retreat-to.py:1-196
    why: exit 1 分支委托目标：CLI 参数/逐阶归档/retry 同步语义
  - path: agate/scripts/check-p6-provenance.py:318-355
    why: 审计 2 双锚点剥离改动点（CARD-SOURCE + AGATE_CARD 物理块兜底）
  - path: agate/scripts/check-judge-verdict.py:99-130
    why: _strip_card 同款剥离 + P6.5 校验新增 exit2-resolution 复核项
  - path: agate/scripts/agate-next-card.py:1-193
    why: M3 渲染/卡片获取——agate-dispatch 子进程复用对象（含 _PHASE_CARDS 无 P6.5）
  - path: agate/scripts/agate_common.py:637-695
    why: read_rules_yaml/known_phase_ids/append_event/split_frontmatter 公共函数
  - path: agate/assets/templates/dispatch-context.md:1-45
    why: 渲染时注入兼容模板（frontmatter 结构 + 卡片占位）
  - path: agate/scripts/check-protocol-consistency.py:1-200
    why: CHECK 1-13 + iter_md_files/is_protocol_file 分区 + 新 CHECK 14/15 挂载点
  - path: agate/loop-orchestration.md:46-74,227-243
    why: 档位 C 定义与 gate 处理流程更新点（BDD-11）
  - path: agate/scripts/agate-md-field-set.py:80-100
    why: exit2-resolution frontmatter 字段用 field-set 写（白名单来源理解）
```

### 4.3 env_constraints（确认 P0-brief，不弱化）

```yaml
env_constraints:
  SELF_GATE: "改 agate/scripts/* + agate/rules/*.yaml + 协议 md 触发；commit message 须含 self-gate-review:/self-gate-skip: 标注（I-15）"
  system_python: "系统 python3（3.12.3）+ pyyaml 6.0.1 + pytest 9.0.3；不引入新依赖"
  consistency_mode: "P5 用 worktree 脚本 --strict-errors-only（0 ERROR）；不得用 --strict 默认（WARNING 债务非本任务范围）"
  stable_tools: "编排/派发类工具（agate-inject-card/agate-render-dispatch-prompt/agate-next-card/agate-md-field-set 等）运行时用 ~/.agate/scripts/ 稳定版（I-16）；worktree 相对路径会读到未发布协议副本"
  worktree_scope: "改造对象 = worktree agate/；主 checkout 禁止改动；测试基线：pytest 1311（unit 1191 + regression 28 + integration 92）串行全绿、count-tests collect 1335、consistency 0 ERROR"
```

> 边界提醒（P2 卡片 §env_constraints 与 gate_commands 不等价）：SELF_GATE 等条目是**声明性信息**；
> 真正强制 = P5_selfgate（跑稳定版 consistency）+ P5_consistency（worktree 版）两条 gate 命令 +
> P4 阶段 commit 时 commit-msg hook（self-gate 标注硬校验）——不依赖 env_constraints 声明本身。

### 4.4 minimal_validation（纯代码逻辑声明）

```yaml
minimal_validation:
  assumption: "本任务纯 Python/YAML/markdown 代码逻辑，无浏览器/外部系统/网络依赖，无需外部最小验证"
  method: "依赖的内部函数/数据转换清单（P4 实现时按此自检）：① check-gate.py exit 三态（0/1/2）子进程消费；② check-state-transition.py P2.3-P2.5 由 pre-commit hook 在 commit 时对 git diff --cached 校验（新 CLI 只 add 不 commit，跳变合法性依赖此链）；③ agate_common.MAX_RETRY_MAP（P6.5 无键 → 读 phases.yaml retry_cap）；④ check-p6-provenance.py 审计 2 剥离逻辑（AGATE_CARD_START/END + frontmatter 剥除）→ 双锚点扩展（CARD-SOURCE 行起物理块）；⑤ agate-next-card.py M3 渲染（_render_sections 读 outputs/gates/retry_cap，新字段不破坏其读取——S-3 回归）；⑥ _TABLE_ROW_RE 加列兼容性（已实证：不锚行尾、前 3 列不变）；⑦ schema draft-07 if/then（additionalProperties:false 下声明新键）；⑧ P6 judge 后推进裁决链（gate_p65 exit 0 → 消费 P6.next:P7，§3.1/§3.4）；⑨ CARD-SOURCE 块外标记下渲染产物过 pre-commit 2p hash（§3.5/§3.6，A2 机制）"
  result: "not_needed"
  note: "本任务为纯代码逻辑（无浏览器/外部系统/网络依赖），但代码逻辑正确性假设**不豁免失败测试首写**：设计经实读已定位 4 条 P4 实现时必先写失败测试确认红的主线——②'CLI 不 commit、由 hook 校验'、⑥'加列兼容'、⑧'P6 judge 后推进（A1 裁决）'、⑨'CARD-SOURCE 产物过 2p hash（A2 机制）'——先红后绿，避免把实读推断当实现依据（A1/A2 教训：实读可发现却未定案的矛盾，须测试锁死）"
```

## 5. BDD 覆盖映射（设计语义 → 25 条 BDD）

| BDD | 设计落点 | 验证手段 |
|-----|---------|---------|
| BDD-1 | §3.1 next/retreat + schema 声明；9 主线条目均含两键；P8 `next: null` | pytest: schema 校验 exit 0 + 9 条目键齐全（P5_schema）|
| BDD-2 | §3.1 P6.5 gate_subphase（hosted_on/forward_to/needs_revision_to），不写 next/retreat；schema if/then 拦截 `next: P6.5` 独立边 | pytest: schema 反例（P6.5 写 next: P7 → 校验失败）|
| BDD-3 | §3.1 值域 = state-machine.md（P5→P4 diff=1 / P6→P4 diff=2 均 `retreat: P4`（retreat-to 逐阶落地）、P6.5 needs_revision→P6、无 retreat 表值的人工直跳 diff≥2 由 check-state-transition 强制 PAUSED 不入表）| pytest: phases.yaml 各 retreat 与 state-machine.md 锚点核对（测试断言表值）|
| BDD-4 | §3.2 WORKFLOW 表加列 + _check_s1 扩展（复用 S-1/S-2，不新开脚本）| pytest: 制造 YAML/WORKFLOW retreat 不一致 → check-structure-consistency exit 1 |
| BDD-5 | §1.1 + 兼容声明（next-card M3、S-3/S-4 不受影响）| P5_consistency + P5 全量 pytest exit 0 |
| BDD-6 | §3.4 agate-next exit 0 → 按 next 更新 .state.yaml phase + add（check-state-transition 由 hook 校验）| pytest: 临时任务 .state.yaml P5→P6（next: P6，exit 0 直推路径）；**P6 通过路径锚点（A1）**：judge.enabled 未启用（历史任务）→ P6 场景 exit 2 + provenance exit 0 → 直推 P7 |
| BDD-7 | §3.4 exit 1 → 调 retreat-to 到 retreat 目标（P5→P4）+ retry 记录 | pytest: mock check-gate exit 1 → 断言 retreat-to 调用/retries[P4]+1（P6→P4 diff=2 亦委托 retreat-to，不预判 diff）|
| BDD-8 | §3.4 exit 2（非 P6）→ 不推进 + 落盘 {phase}-exit2-resolution.md | pytest: 文件存在 + frontmatter 字段 |
| BDD-9 | §3.4 P6 exit 2 特例（FAIL=0/证据非空 + provenance exit 0）→ 引导 P6.5，不落盘不停等 | pytest: P6 分支无 exit2-resolution 文件生成；**P6 judge 后推进路径锚点（A1）**：judge.enabled=true + P6.5-judge-verdict.md 存在 + gate_p65 exit 0（check-judge-verdict/check-events 双 0）→ phase P6→P7 + state_transition 事件；gate_p65 exit 1（缺 verdict）→ 停留 P6 不推进 |
| BDD-10 | §3.4 advance --to + retreat-to 委托；示例用 P6→P4（§6①）| pytest: diff≥2 人工直跳 --to 提示 PAUSED 拦截（retreat-to 逐阶路径不触发拦截，单测断言逐阶调用）|
| BDD-11 | §3.7 档位 C 文档更新 + agate next 事件证据 | pytest: 两次推进后 gate-events.jsonl 含 state_transition 记录 |
| BDD-12 | §3.3 check-judge-verdict 复核 exit2-resolution | pytest: 有 exit:2 gate_run 无 resolution 文件 → verdict 校验失败 |
| BDD-13 | Not Modify（check-gate/check-state-transition 返回约定不变）| pytest: 两脚本头注释 + exit code 行为回归 |
| BDD-14 | Not Modify（五模式锚点不动）+ Phase 3 文档清理 | P5_consistency + grep 断言无 workflow/ralph 模式概念 |
| BDD-15 | §3.8 CHECK 15 词边界 + 豁免词典 | pytest: 插入裸 task → ERROR；task_fields 键不误报 |
| BDD-16 | §3.8 CHECK 14 段落级判据 + 豁免结构 | pytest: 无注记段含 DSH → ERROR；加 `> 实现注记：` → pass |
| BDD-17 | §6③ 三面并陈：9 文件三分类判定全处理 + assets/ 适配说明命中段挂注记（判定写入 P1 D-2 表已核）| 人工 + CHECK 14 首跑 0 命中；**assets/ 处置锚点（A3）**：pytest 断言 assets/templates/dsh/SKILL.md 属结构豁免（插平台名 → pass）+ architect.md/custom-role.md 命中段带注记 → CHECK 14 pass |
| BDD-18 | §3.5 agate-dispatch 单命令渲染时注入 | pytest: 产物含完整卡片块 + generated_by: agate-dispatch.py + CARD-SOURCE 在 AGATE_CARD_START 之前（块外）|
| BDD-19 | Not Modify（inject-card 手工路径保留）| pytest: 手工占位符 + inject-card exit 0（既有测试回归）|
| BDD-20 | §3.6 审计 2 CARD-SOURCE 剥离（CARD-SOURCE 行起物理块优先）| pytest: 渲染产物含 PASS/FAIL 模板（CARD-SOURCE 在 START 前）→ audit2 exit 0；**剥离起点锚点（A2）**：CARD-SOURCE 行 + START 均在剥离区间（产物含卡片不误报）|
| BDD-21 | §3.6 物理块兜底剥离 | pytest: 手工注入文件 → audit2 exit 0（既有测试回归）|
| BDD-22 | §3.8 CHECK 14（结构性判据）| pytest: 插平台名报 ERROR → 补注记 pass |
| BDD-23 | Not Modify（render-dispatch-prompt CLI 不动）+ 既有单测回归 | P5 全量 pytest（该脚本既有测试）|
| BDD-24 | §3.8 结构性判据无名单 | pytest: 新增临时 md 含平台名 → 自动命中 |
| BDD-25 | §3.5/§3.6 两路生成物同构 + pre-commit 2p hash 通过 | pytest: 两路 dispatch-context 跑 2p hash 校验均通过；**含 CARD-SOURCE 过 2p 锚点（A2）**：渲染产物（CARD-SOURCE 块外 + START..END 内 next-card stdout）嵌入抽取 hash == next-card 期望 hash（CARD-SOURCE 不入抽取区间）|

## 6. P1 评审 4 条非阻断边界观察的显式处理

| # | 观察 | 处理 |
|---|------|------|
| ① | BDD-10 示例"从 P7 按转移表回退到 P4"用边不当（P7 gate 失败回退目标不是 P4）| P1 BDD-10 Given 修正为 **P6 → P4**（state-machine.md:148；P6→P4 diff=2，机械落地由 `agate-retreat-to.py` 逐阶 P6→P5→P4（每步 diff=1 独立 commit），CLI 不预判 diff——§3.4 exit 1 委托语义；state-machine.md:647-654 的 diff≥2→PAUSED 是人工直接跳转路径，与 retreat-to 逐阶自动化不同轨）。跨 ≥2 阶示例仅用于"人工直跳拦截为 PAUSED"语义（BDD-3，P5→P4 diff=1 单步，state-machine.md:132）。P1 正文该句由主 Agent 在 P2 通过后回改（[SCOPE+] 级别文档修正，不新增 BDD）|
| ② | BDD-15 禁词含 task，`rules/dispatch.yaml` 数据面既有 task_fields 等键含 task——误伤风险 | CHECK 15 实现 = **词边界判定**（`\btask\b` 不匹配 `task_fields`/`task_id` 下划线连字符上下文）+ **数据面豁免词典机械生成**（schema property 名 ∪ phases.yaml task_fields ∪ dispatch.yaml 既有键名）；dispatching.yaml law-1 的 `task` 平台指代行属 Phase 3 **文档清理对象**（改写为协议语义词"subagent 派发"，§6/§1.2），不属数据面 schema → 上线即 0 命中（BDD-15 反例测试覆盖）|
| ③ | BDD-17 排查面（9 文件）窄于机械化扫描面（未来扫全部协议 md + assets/）| 排查/扫描/豁免三面并陈（A3 定案①）：**排查面** = P1 D-2 9 文件 + **assets/ 平台适配说明命中段**（execution-roles/architect.md:229「无 prompt 派发场景」举例、templates/custom-role.md:49-56 平台适配说明 → 挂 `> 实现注记：`，Phase 3 完成，BDD-17 逐文件判定可追溯）；**扫描面** = CHECK 14 上线后协议 md（`agate/*.md` 语义叙述面 + assets/ 非豁免 md 适配说明段；iter_md_files 结构性判据，新增自动覆盖，BDD-24）；**结构豁免面** = platform-notes.md/SETUP.md 整文件 + **assets/templates/dsh/ 平台食谱目录**（SKILL.md 等，A3）+ WORKFLOW.md「已知适用环境」表行。排查面是存量一次性清理，扫描面是持续机械拦截——清理（排查面）+ CHECK 上线（扫描面）同批（B3a/B3b），豁免面先行声明，上线首跑 0 命中为基线 |
| ④ | 同类扫描 D-2 称 adr.md 豁免因"docs/reviews 属 NARRATIVE 区"，但 adr.md 本体在 `agate/` 协议区 | 豁免理由修正：adr.md 在 `agate/` 协议区，**不做整文件 NARRATIVE 豁免**；ADR-008 决策记录的平台名属**决策叙事**（记录当时决策语境，adr.md 是 A7 审查锚点），按「实现注记」段落标记处理（挂 `> 实现注记：` 于 ADR-008 平台名所在段），与其它协议文档同规则——CHECK 14 对带注记段豁免，不引入协议区白名单（避免名单机制回潮）|

## 7. 实现完成标志

- phases.yaml 9 主线条目含 next/retreat（P8 为 null）+ P6.5 条目含 gate_subphase；schema 校验通过且反例（P6.5 next: P7）被拒。
- WORKFLOW 总览表含 next/retreat 列；S-1/S-2 扩展后：制造 YAML↔表 retreat 不一致 → check-structure-consistency exit 1（复用既有脚本，无新检查脚本）。
- `agate next` / `agate advance` / `agate dispatch` 三个脚本存在且 CLI 契约符合 §3.4/§3.5；check-gate/check-state-transition/retreat-to/inject-card/render-dispatch-prompt/next-card 六个既有脚本返回约定与 CLI 未被改动（git diff 可证）。
- exit 2 分支：非 P6 落盘 exit2-resolution.md；P6 特例不落盘；check-judge-verdict P6.5 复核含 exit2-resolution 校验。**P6 推进裁决闭环（A1）**：judge.enabled 任务经 gate_p65 exit 0 → agate next 把 phase P6 推 P7（非人工改 .state.yaml）；gate_p65 exit 1 → 停留 P6 有指引。
- 审计 2 双锚点剥离：渲染产物（CARD-SOURCE 行起物理块，CARD-SOURCE 在 AGATE_CARD_START 前）与手工物理块两路均 exit 0；渲染产物过 pre-commit 2p hash（A2：CARD-SOURCE 不入 `_extract_card` 抽取区间）。
- 护栏 1：CHECK 14/15 在 worktree check-protocol-consistency.py 生效；**存量清理（9 顶层 md + assets/ 适配说明命中段注记）后首跑 0 ERROR（--strict-errors-only），assets/templates/dsh/ 平台食谱目录结构豁免（A3）**；插入裸平台名 → exit 1，补注记 → exit 0。
- 全量 pytest（P5 命令）exit 0 + count-tests 用例数不回退 + shellcheck 0 error；档位 C 推进记录可观测（gate-events state_transition）。
- 25 BDD 逐条可映射到测试（§5 表），P6 验收 PASS/FAIL 二值覆盖 BDD-1~25。

## 8. dispatch_plan 机器字段（后续阶段编排）

本任务跨 4 设计域 + 多脚本 + 文档面 → high 复杂度，P4 拆 4 批 static-batch（文件不跨批：同一文件只被一批改）。批间共享 git index（单 worktree）→ 建议主 Agent 顺序执行批或隔离 worktree 并行；`parallel_limit: 4` 为批数上限声明（flow YAML 已入 frontmatter `dispatch_plan:`，本节为批边界叙述）。

- **B1 core-rules-cli（high）**：phases.yaml + phases.schema.json（§3.1）+ agate-next.py/agate-advance.py（§3.4）+ check-judge-verdict.py exit2-resolution 挂载（§3.3）+ loop-orchestration.md 档位 C（§3.7）+ 对应 pytest。独占文件：phases.yaml、schema、两新 CLI、check-judge-verdict.py、loop-orchestration.md。产出 ≤3（rules 数据面 / CLI 脚本组 / 测试组）。
- **B2 render-audit（high）**：agate-dispatch.py（§3.5）+ dispatch-context.md 模板 + check-p6-provenance.py 审计 2 双锚点（§3.6）+ 对应 pytest。独占：agate-dispatch.py、模板、check-p6-provenance.py。
- **B3a docs-clean（medium，先于 B3b）**：顶层 9 文件平台名清理/注记（§3.8 存量面，含 WORKFLOW 总览加列 + 豁免结构标注）+ **assets/ 适配说明命中段挂注记**（execution-roles/architect.md:229、templates/custom-role.md:49-56；A3 定案①）。独占：全部 agate/*.md（除 loop-orchestration.md 归 B1 外）+ assets/ 两文件（architect.md/custom-role.md——architect.md 另属 execution-roles 角色文件，仅挂注记不动语义；assets/templates/dsh/ 平台食谱目录**不在此批**，结构豁免）。产出 = 修改的多 md（每 subagent 输入 ≤3 文件分组拆小任务，assets 命中按文件分别拆给 subagent）。
- **B3b guardrail-scripts（high，依赖 B3a）**：check-structure-consistency.py S-1/S-2 扩展（§3.2）+ check-protocol-consistency.py CHECK 14/15（§3.8）+ 对应 pytest。独占：两脚本。**前置**：B3a 完成（存量清零后 CHECK 首跑不红）→ B3a/B3b 必须串行（B3b 依赖 B3a 产出），主 Agent 编排时 B3a 完成后才派 B3b。
- P3 测试设计先行（全部 BDD 测试点分 4 组对应批）；P4 各批内 TDD 红→实现→绿；P5 全量 gate（§4.1）在所有批返回后统一执行。

> 编排注意（P4 阶段）：B1 与 B2 可并行（文件不冲突）；B3a → B3b 串行；批间共享 worktree git index 时建议全部串行执行批、commit 顺序落地，避免并发 git add/commit 锁冲突（与派发编排机制"资源密集型默认串行"同理）。
