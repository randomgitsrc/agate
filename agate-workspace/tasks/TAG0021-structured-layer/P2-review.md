---
phase: P2
task_id: TAG0021-structured-layer
type: review
parent: P2-design.md
trace_id: TAG0021-P2-20260822
status: approved
created: 2026-08-22
agent: plan-eng-review
---

# P2 方案评审 — TAG0021 协议结构化层（RM-AG0022）

## 评审范围与方法

- **评审对象**：`P2-design.md`（392 行，candidate_count: 3，推荐 C1「内聚最小面」，dispatch_plan serial M0-M3）
- **输入文件**：P2-design.md（主对象）/ P1-requirements.md（16 BDD + 决策 D1-D3）/ P1-review.md（approved）/ P0-brief.md / design-structured-layer.md（§3-§5 权威方案参考）/ phase-cards/P2-design.md（随 dispatch-context 注入）
- **独立评审声明**：只依据客观标准与评审对象文件作判断；不采信实现者自述。`[PROD_NOT_TOUCHED]`：全程只读主 checkout 协议文件与稳定版角色/卡片；唯一写操作是本文件与 P2-review-progress.md，均在 worktree `agate-workspace/` 内。
- **证据核验方式**：行号/基线/文件存在性逐项用 grep/read/bash 实查（rglob 扫描面、is_gate_meta_key 实现、check-gate P2 分支、pre-commit 2j 区域、WORKFLOW 总览表、count-tests 基线、dist/ptmp 可写性、HANDOFF 硬约束），非印象判定。

## 逐项核验结论（对照派发指引评审要点 1-6）

### 1. 候选方案与权衡 — ✅ 通过

- **证据基**：P2-design.md §2 含 C1（内聚最小面）/ C2（拆分专职脚本组 + 扩展 YAML 面）/ C3（并入 check-protocol-consistency，D1 否决项验证），frontmatter `candidate_count: 3` 与正文三候选一致（gate 按字段校验，不解析标题）。
- §2.4 权衡表 8 维度（M0 增量面/回退粒度/S 编号自校验/对账实现一致性/单测隔离/YAML 面覆盖/主 Agent gate 数/P1 决策契合度），C1/C2/C3 各维度差异真实：C2 在单测隔离列优于 C1（每检查独立文件）、C1 在 M0 增量面/回退粒度/对账一致性列优于 C2，非稻草人对照；C3 的"单一入口"优点被三条硬约束（HANDOFF「只加不改」/回退粒度/BDD-2/5/10 独立判定语义）否决，属于 D1 否决理由的形式化固化而非凑数。
- 选择理由成立（§2.4）：(1) HANDOFF 硬约束排除 C3/压低 C2；(2) 消灭"同一规则多处实现"是任务核心动机，C1 对账 hub 恰好不重演该反模式，而 C2 消费点级对账再造 3 份重复逻辑；(3) C1 与 P1 决策及 BDD-1..16 验收面对齐，C2 扩展面超验收范围（YAGNI）。C2 单测隔离优势经函数级分离保留大部分，理由自洽。

### 2. 影响面梳理 — ✅ 通过

- **三部分齐全且写在候选方案之前**（§1 在 §2 前，符合 P2 卡「先影响面后候选」顺序要求）。
- **改什么（1.1）**：按 M0-M3 组织，落点精确到文件/小节/函数且逐行关联 BDD——M0-1..M0-11 / M1-1..M1-5 / M2-1..M2-7 / M3-1..M3-5，如 M0-7「WORKFLOW.md 阶段总览表（§阶段总览，行 285-300 区域）」、M1-3「check-pruning.py（_md_field 调用点）」、M2-4「pre-commit-gate.py（流水线 2j 区域，行 399 附近）」、M3-1「agate-inject-card.py（114 行，全文）」。无"相关代码"类模糊表述。
- **不改什么（1.2）**：N-1..N-9 每项含理由。N-1 的关键实证**已复核成立**：check-protocol-consistency.py 扫描面确为 `rglob("*.md")`（实查行 120 / 行 830），新增 `rules/*.yaml` 不在其扫描面，P1 H5 疑虑解除成立。N-2（既有 rules md 不并入对账面）、N-9（数据边界不扩展到 P1 标记/P6 行格式，YAGNI）均显式给出范围边界。
- **风险在哪（1.3）**：R1-R10 每条配缓解；高频风险项全覆盖——双源漂移（R1→S-1/S-2 双向 gate + S-3 单源）、跨模块引用（R7→S-6）、schema 变更（R5→S-5 常开 + schema 自检）、工具链自举（R4→双工作区纪律 + BDD-13 隔离测试）、对账静默失效（R2→BDD-6 可观测出口）。本任务无并发/资源竞争，判定正确。
- 证据基底（§1 引言）引用 P1 §4.1-4.3 三组扫描 + 本轮逐文件实查（gate_commands 正则 4 处实现、check-gate P2 分支读取点、count-tests 基线 749 等），非凭印象列。

### 3. 四字段 — ✅ 通过

- **frontmatter**：`packages: [agate]` / `domains: [backend]` / `ui_affected: false`，与 P1 frontmatter 继承一致；`dispatch_plan: {mode: serial, batches: [{id: M0, complexity: high}, ...]}` 合法（serial ∈ 契约枚举 {single, static-batch, parallel, recon-then-split, serial}，serial 模式无需 parallel_limit）。
- **gate_commands**（§4）：9 个 key 全部独立声明、**无 && 拼接**（P3/P5/P5_consistency/P5_structure/P5_schema/P5_count/P5_platform/P5_ruff，无短路链）；P3 与 P5 均含 `-p no:cacheprovider --basetemp=/home/kity/oclab/agate/.worktrees/agate-TAG0021/dist/` 适配 /tmp 只读——**dist/ 可写性已实查确认（dist WRITABLE；ptmp NOT writable，SCOPE+3 实证成立）**；`P5_timeout_seconds: 300` vs 其余各 120 分档存在（P5 为全量 pytest 含新脚本，300s 档合理；P5_platform 按 check-platform-assumptions 判定 BDD-16），`{key}_timeout_seconds` 命名符合 per-key 惯例；**未给 P3 声明 timeout_seconds**（符合「timeout_seconds 排除 P3、P3 走 AGATE_TDD_TIMEOUT」规则）。
- **files_to_read**：15 项全部为 path + why，覆盖实现全部上下文（consistency 参照样本 / frontmatter-check schema 先例 / md-field-get 对账 hub / 三消费点 / inject-card / next-card / WORKFLOW 锚点 / agate_common / 既有测试参照）。**逐项实查行号命中**：check-protocol-consistency.py:70-130（含 rglob 行 120）✓、agate-frontmatter-check.py:27-160（文件 245 行）✓、agate-md-field-get.py:1-120（文件 238 行）✓、agate-read-gate-commands.py:1-50（文件 41 行）✓、check-pruning.py:84-182（文件 182 行）✓、check-gate.py:590-700（P2 分支 599-641 命中）✓、agate-inject-card.py:1-114（文件恰 114 行）✓、agate-next-card.py:60-114（文件 104 行）✓、agate_common.py:79-110（is_gate_meta_key 行 79 命中）✓、WORKFLOW.md:285-300（总览表 287-299 命中）✓。P4 上下文可控。
- **env_constraints 与 gate_commands 边界**：§4 env_constraints 注明"声明性字段，真正被执行的是 gate_commands"，sandbox/interpreter/dual_workspace/bash_discipline/platform_neutral 五条声明与 gate_commands 执行面不混；可强制约束（BDD-16 平台无关）已落 P5_platform 执行 key，未止步于声明——符合「env_constraints 无强制力、需强制须落 gate_commands」边界原则。
- **minimal_validation**：声明"纯代码逻辑，无外部系统依赖"+ rationale（依赖内部函数/数据转换链：yaml.safe_load / json.load / is_gate_meta_key / md-field-get 双读机制 / rep 输出机制 / frontmatter-check SCHEMAS 模式）+ method 6 项实测 + result: confirmed，符合 P2 卡 P2 最小验证要求（纯代码逻辑须声明 + 附理由）。

### 4. 方案与 P1 / 设计文档一致性 — ✅ 通过

- **BDD-1..16 全覆盖**（落点见 §1.1 各行 + §3.7 完成标志 1-7）：BDD-1→M0-4/5 + §3.2；BDD-2→M0-6/7 + §3.3 S-1/S-2；BDD-3→M0-6 S-5/S-6；BDD-4→§3.5 M0 gate + M0 回退边界；BDD-5→§3.3 S-3/S-4；BDD-6→§3.4 出口（WARNING + SUMMARY + 退出码 0/2 不变）；BDD-7→§3.4 三类解析点 + 脚本数 3；BDD-8→M2 门槛「差异数为 0 才切换」；BDD-9→M2-1/M2-2 + SCOPE+2（A 组消费方随 md-field-get 生效，以 BDD-9 判据为准）；BDD-10→M2-3/4/5 + §3.3 触发点时间线（pre-commit + CI + 脚本三处阻断）；BDD-11→M2-6/7；BDD-12→M3-1..4 + §3.6；BDD-13→§3.6 稳定版隔离 + M3-5 隔离测试；BDD-14→§3.5 M3 gate；BDD-15→R8 + §3.5 每里程碑血糖（749 基线，实查 count-tests 当前 1168 ≥ 749 成立）；BDD-16→R9 + P5_platform。无遗漏、无悬空。
- **D1**（S-1~S-6 独立脚本 + 独立编号）：M0-6 + N-1 + C3 候选固化否决理由，落实 ✓。
- **D3**（M1 首批三脚本）：§3.4 覆盖 agate-read-gate-commands / check-pruning / check-gate 三类解析点 ✓。
- **design-structured-layer §3-§5 对齐**：§3 schema 草案 → §3.2 draft-07 子集展开（phase id 含 P6.5、review_roles/outputs/prune_rules 结构一致）；§4 S-1~S-6 → §3.3 六条口径 + 触发点时间线（设计文档仅有口径表，P2 补足 M0-M1/M2/M3 三段触发）；§5 M0-M3 → §3.5 落地清单 + 回退边界。唯一结构性调整（design §3.1 把 gate_commands 语法声明挂 phases.yaml P2 节点，P2 移至 dispatch.yaml 全局）方向合理——gate_commands 语法是跨阶段全局规则，非 P2 专属，非漂移。

### 5. 工程性专项（工程评审职责）— ✅ 通过（3 项非阻塞发现见下）

- **YAML 权威源数据边界**：§3.1 三文件「承载/不承载」分表清晰，"可判定规则进 YAML、叙事留 md"原则贯穿（§1.2 N-3 卡片叙事节、明确不进 YAML 清单）；与既有 rules/*.md 并存策略（N-2）防双源同步爆炸，S-4 把 roles.yaml C8 映射表与 review-mapping.md 登记为一致性对，防两处漂移 ✓。
- **schema 设计可校验**：§3.2 draft-07 子集（type/required/enum/properties/items/additionalProperties/minItems，不用 minimum/exclusiveMinimum，防子集实现膨胀）；枚举明确（exec_role/phase id/retry_cap 2 或 3/mode）；check-yaml-schema.py 手写校验（不引 jsonschema 包，与依赖清单 pyyaml+Pillow 一致）+ schema 自身健全性自检（R5）✓。
- **S-1~S-6 判定口径与触发点**：§3.3 六条「方向/判定口径/触发点」表 + 失败语义（ERROR→exit 1，--strict-errors-only 常开，rep 风格输出供机器消费）；触发点时间线三档（M0-M1 仅 P5 gate 手动、M2 起 pre-commit+CI、M3 S-3 渲染化同步）——M0 不接 pre-commit 的理由（初始填充期对存量卡片误拦）成立 ✓。（口径歧义 1 处见非阻塞发现 #1）
- **M1 对账差异可观测出口（BDD-6）**：§3.4 `RECONCILE WARNING: <op> <field>: grep=… structured=…` + `RECONCILE SUMMARY: N mismatches across M fields` + 退出码保持 0/2 不新增阻断（与原 grep 路径判定解耦），stderr 重定向即日志可计数审计 —— 完全满足 BDD-6「含 WARNING 与差异计数、退出码保持原判定」；归一化口径（R10）复用 md-field-get 既有 BOOL/LIST 归一化 + NO_FALLBACK 语义，P3 测试设计固化 ✓。
- **M2 切换破坏性变更识别**：M2-7 UPGRADING v0.57 章节（M2 小节）逐条列「脚本从 grep md 切 YAML 读 + 一致性 gate 提升阻断」；§3.5 M2 行标注"最重回退点：revert 回 M1 形态需 BDD-8 对账清零门槛倒查"，符合 AGENTS.md 版本发布清单「UPGRADING 破坏性变更逐条列」✓。
- **M3 渲染化稳定版隔离（BDD-13）**：§3.6 渲染用 resolve_agate_root 解析到的 YAML（env AGATE_ROOT → 项目声明 → current → 脚本路径上溯，实查 agate_common.py 行 231 存在 resolve_agate_root）；M3-5 隔离测试用 AGATE_ROOT 构造两套 rules/ 差异断言互不污染——满足 BDD-13 双工作区隔离（TAG0016 教训覆盖）✓。
- **dispatch_plan serial 合理性**：§5 批次表四批串行理由成立（M0 是全部先决；M1/M2 因 BDD-8 门槛严格串行；M3 依赖 M0 且与 M1/M2 零文件重叠，声明串行以控复杂度）；**同文件跨批两轮改造**（M1/M2 均改 check-gate.py / check-pruning.py / agate-read-gate-commands.py）处理到位：BDD-8 对账清零门槛作天然边界（M1 提交后对账差异数检查，M2 仅清零后启程），M1+M2 合并单批须在 P3/P4 显式声明且不破坏 BDD-8 二值判定；M3 与 M1/M2 零重叠 ✓。

### 6. SCOPE+ 发现 — ✅ 无越界无遗漏

- **SCOPE+1（命名空间）**：§5 已声明 + §1.2 N-2 落地（rules YAML 与既有 rules md 并存、S-2 锚点范围显式排除既有 rules md），建议 P1 基线无需变更——方案内覆盖 ✓。
- **SCOPE+2（随 md-field-get 生效）**：§5 已声明 A 组消费方（ci-gate-backstop/agate-risk-score/check-routing/agate-feedback）随 md-field-get 一起生效、不单独立 BDD，属 BDD-9 静态零命中覆盖范围——方案内覆盖 ✓。
- **SCOPE+3（basetemp 修正）**：**客观查证成立**——HANDOFF §4 声称 `--basetemp=/home/kity/oclab/dsh-workspace/ptmp`，实测 ptmp 只读（NOT writable）、dist/ 可写（WRITABLE），以本 design 的 dist/ 为权威 basetemp 的修正建议成立 ✓。

## 架构问题（阻塞级）

无。

## 架构问题（非阻塞级）

1. **S-2 判定口径未排除 WORKFLOW 总览表 READY 行**（P2-design §3.3 S-2 行）：总览表（WORKFLOW.md 287-299）末行 `| READY | 待发布 | — | — | ...`（行 299），而 phases.yaml phase id 枚举（§3.2）不含 READY（{P0..P8 + P6.5}）。S-2「表每行 phase id 在 phases.yaml 有定义」若不过滤 READY 行将永远误报漂移。**建议**：P3 test-designer 把"S-2 只匹配 `P\d`/`P6.5` 前缀行，READY/表外行显式排除"写入口径测试（首条失败测试锚点）。
2. **§3.1 dispatch.yaml modes 枚举与既有词表不一致**：§3.1 写"五模式编排枚举（single/parallel/pipeline/understand-then-split/hybrid）"为 design-structured-layer §3.3 遗留词表，而 dispatch-protocol / P2-card dispatch_plan 契约词表为 {single, static-batch, parallel, recon-then-split, serial}（本方案 frontmatter 已用 mode: serial 佐证）。方案内已注释"P4 对齐既有文档词表"，但**建议 §3.1 直接写对齐后词表**，消除同一方案内两处词表并存的 P4 二义。
3. **§3.1 gate_commands 合法 key 判定表述不完整**：写"判定复用 agate_common.is_gate_meta_key"，但实查 is_gate_meta_key（agate_common.py 行 79-87）只精确匹配 `_formatter`/`_timeout_seconds` 两个后缀，`project_module` 不在内；既有实现 agate-gate-missing-cmds.py 行 22 为 `is_gate_meta_key(k) or k == "project_module"`。**建议**口径写全为"is_gate_meta_key OR project_module 特判"，并在 S-4/对账实现时以 agate-gate-missing-cmds.py 为参照。
4. **"825 基线"数字出处未闭合**（§1.2 N-6 / M2-6）：tests/ 下无 825 字面量（grep 实扫），fixture 目录实际 65 文件、count-tests 当前 1168/基线 749。"825"仅在本任务文件间相互引用，疑似某历史统计口径。不影响 N-6/M2-6 行为语义（不删既有 fixture、增补 YAML 构造，判据不依赖具体数字），**建议** P3/P4 核对口径或改为"既有 fixture 集合"表述。
5. **"53 脚本"vs"57 个 .py"口径**：M0 回退边界（§3.5）与 HANDOFF/P0-brief 用"53 脚本"，P1 扫描 1 实查 57 个 .py（含 agate_common/resolve-entry 等基础设施）。同一任务两处数字不同源，**建议**统一注明口径（如"53 个业务脚本 / 57 个 .py 含基础设施"），不影响 BDD-4「既有脚本行为不变」语义。

## 测试缺口

- 无 P2 阶段可判定缺口。S-1/S-2 的 READY 行排除、gate_commands 合法 key 判据（含 project_module）、五模式词表对齐三处口径应在 P3 测试设计的**首批失败测试**中固化（对应非阻塞发现 1-3），防实现期口径漂移。
- 对账归一化规则表（§3.4 R10）已声明"先写对账测试断言再实现（TDD）"，P3 应将其列为输入，覆盖 frontmatter list 空格连接 / 正文内联 / 块式 / 换行连接不回退四类差异形态。

## 锁定决策（本次评审后确定）

- C1「内聚最小面」作为选定方案：2 新脚本 + 6 新数据文件纯增量起步，单文件级回退粒度，对账 hub（md-field-get 一处）+ 薄消费点接入，S-1~S-6 单脚本承载（函数级隔离保留单测隔离优势）。
- M0-M3 串行编排成立，M1/M2 以 BDD-8 对账清零为硬边界；M2 为最重回退点，UPGRADING 破坏性变更节先列后改。
- basetemp 权威路径定为 worktree `dist/`（SCOPE+3 实证，ptmp 只读废弃）；gate_commands 固化后 P4-P6 不得修改。

## 推进条件对照（P2 卡逐项）

| P2 卡推进条件 | 核验结果 |
|---|---|
| P2-design.md 候选方案 ≥2 + 四字段齐全 | ✅ candidate_count: 3（C1/C2/C3）+ packages/domains/ui_affected/gate_commands 齐备 |
| 含「影响面梳理」节（改/不改/风险三部分齐全，且在候选方案之前） | ✅ §1 三部分齐全，先于 §2 候选 |
| P2-review.md 存在且 status: approved（agent≠main） | ✅ 本文件（agent: plan-eng-review） |
| gate_commands.P5_e2e 已声明（ui_affected: true 时） | ✅ N/A——ui_affected: false，不触发 |

## 结论

**status: approved（与 Header 一致）。** P2-design.md 满足 P2 卡全部推进条件：3 候选方案且权衡客观、选择理由成立（candidate_count 与正文一致）；影响面梳理三部分齐全且前置；四字段齐备（gate_commands 独立 key 无 &&、basetemp 已实证、timeout_seconds 分档、files_to_read 精简可控、env_constraints/gate_commands 边界清晰）；BDD-1..16 全部有设计落点（§3.7 完成标志 7 条覆盖 16 条）；D1/D3 与 design-structured-layer §3-§5 落实对齐；工程性专项（数据边界/schema/S-1~S-6 口径与触发点/对账出口/破坏性变更/渲染隔离/dispatch_plan serial）全部成立；SCOPE+1/2 方案内覆盖、SCOPE+3 客观查证修正成立。无阻塞级问题；5 项非阻塞发现（S-2 READY 行口径、五模式词表、project_module 判据、825 基线出处、53/57 口径）均不影响推进，建议在 P3 测试设计与 P4 实现期闭环。