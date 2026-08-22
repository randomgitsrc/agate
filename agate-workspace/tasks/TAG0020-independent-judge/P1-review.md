---
phase: P1
task_id: TAG0020-independent-judge
type: review
parent: P1-requirements.md
trace_id: TAG0020-P1-20260822
status: approved
created: 2026-08-22
agent: requirements-review
---

# P1 需求基线评审（复审·修改轮 1 后 approved）— 独立 Judge 机制（TAG0020 / RM-AG0032）

评审对象：`P1-requirements.md` 修订版（215 行，status: draft，agent: analyst）
本文件为**复审轮**：首轮结论 needs-revision（R1：BDD-4 "自述摘要"无机械检测锚点；R2：§4.3 标题"六道审计"口径不一致），analyst 已完成修改轮 1（修复声明见 P1-progress.md「修改轮 1」节）。本文件复核修复 + 全量复评。

**结论：approved**（R1/R2 均正确修复，无新引入问题；BDD-1~10 全部可二值判定）

---

## 一、R1 复核：BDD-4 黑名单路径引用集固化（approved）

### 1.1 修复落点核实（独立 grep 复核，非依据 analyst 自述）

| 复核项 | 修复后内容（实测） | 判定 |
|---|---|---|
| 禁项 2 "自述摘要"替换 | 全文 grep "自述摘要" **零残留**；BDD-4 标题改为"judge 的 dispatch-context 仅允许白名单输入，禁项为可机械匹配的黑名单路径引用集" | ✓ 已替换 |
| 黑名单路径模式（机械匹配锚点） | BDD-4 Then ①：`P6-acceptance.md` / `P6-dispatch-context-*.md` / `P5-dispatch-context-*.md` / `P4-dispatch-context-*.md` / `P4-implementation.md` / `P4-review.md` / `P5-test-results/` 七模式，声明"字符串/正则匹配" | ✓ 具体路径模式齐备 |
| 白名单（准入） | BDD-4 Then ②：`P1-requirements.md` / `P2-design.md` / `P6-evidence/` / `.state.yaml` / `gate-events.jsonl` / `P6.5-judge-verdict.md`（自产出）+ git log 查询权；"白名单外任务文件路径引用即违规" | ✓ 判定规则完整 |
| 继承先例 | BDD-4 Then ③：行首 `- PASS`/`- FAIL` 预判，正则 `^\s*- (PASS|FAIL)\b`，继承 check-p6-provenance 审计 2（实测审计 2 L318-355 同款正则已确认） | ✓ 有先例锚点 |
| 上游关联禁注入 | BDD-4 Then ④：『上游关联』节禁注入禁项——主 Agent 派发与 `agate-extract-context.py` 注入在 P6.5 均不得传黑名单路径/verifier 产出结论（禁用或净化） | ✓ 覆盖 §4.2 识别的主防泄漏点 |
| 扫描范围 | 检测限定为 judge dispatch-context 的『输入文件』与『上游关联』两节路径扫描 + 全文行首预判扫描，均排除 AGATE_CARD 块与 frontmatter（复用审计 2 排除逻辑） | ✓ 扫描边界可机器实现 |
| 无"P2 定义"开放项 | §4.2 结论声明："黑名单路径引用集同时是 BDD-4 机械判定的**权威定义**，禁入项在 P1 全部固化、**不在 P2 再议**；P2 只负责 check-judge-verdict.py 的扫描实现与黑名单 schema 的机器化落地" | ✓ 验收判据已闭环，仅实现留 P2（合法） |

### 1.2 §4.2 表与 BDD-4 一致性核对

§4.2 白名单反推结论四行表与 BDD-4 Then 逐项对应：

| §4.2 结论表行 | BDD-4 Then 项 | 一致 |
|---|---|---|
| 黑名单（自述文件路径）七模式 | ①七模式 | ✓ 完全相同（含 `P5-test-results/` 尾斜杠目录模式） |
| 黑名单语义（禁注入：上游关联禁 verifier 产出结论，extract P6.5 禁用/净化） | ④禁注入禁项 | ✓ 语义一致 |
| 黑名单（继承先例：行首 PASS/FAIL） | ③行首预判正则 | ✓ 一致 |
| 白名单（准入）五类 + git log + 自产出允许 | ②白名单六项 + git log 权 | ✓ 一致（`P6.5-judge-verdict.md` 已纳入） |

L28 需求复述防造假①与 L98 §4.2 审计 2 行措辞已同步为"黑名单路径引用集"表述 —— 三处（复述 / 扫描表 / BDD-4）口径统一。

**R1 判定：已修复，可机械二值判定，验收标准无开放项。**

## 二、R2 复核：审计编号口径统一（approved）

| 位置 | 修复后内容（实测） | 判定 |
|---|---|---|
| §3 兼容行 | "现有 P6 **七道审计（审计 1-7，check-p6-provenance）**行为不回归" | ✓ |
| §4.3 标题 | "组 3：check-p6-provenance **七道审计（审计 1-7）**与事件账本交集" | ✓ |
| §4.3 命中数量 | "1 个审计脚本（**七道审计**）+ 2 个联动脚本" | ✓ |
| §4.3 结论 | "账本与**七道审计（审计 1-7）**配合关系……审计 1/3/5 复用/同源，审计 6 无交集，审计 2 提供白名单校验先例" | ✓ |

grep 全文 "六道" **零残留**，与实测 check-p6-provenance 的七道审计（审计 1-7，审计 7 为 TAG0016 新增 P5 证据复用）口径完全一致。

**R2 判定：已修复。**

## 三、全量复评：10 条 BDD 可判定性 + 编号连续

BDD-1~10 编号连续、格式 `#### BDD-NN:`（实测 L135/140/145/152/157/162/169/174/181/186），无跳号。逐条判定：

| BDD | 判定主体（机械信号） | 可二值 | 覆盖维度 |
|---|---|---|---|
| BDD-1 新任务 P6→P7 必经 P6.5 门槛 | verdict 文件存在性 + check-judge-verdict/check-events exit code | ✓ | 多端（调度链） |
| BDD-2 历史任务跳过 P6.5（存量不挂） | 状态文件无 judge 字段 → gate 不要求 verdict/账本 | ✓ | 兼容 |
| BDD-3 fresh context 零挑验重验所有 BDD | `criteria_total == P1 BDD 标题数` + 每 BDD 独立条目 | ✓ | 数据（计数口径复用审计 3） |
| BDD-4 信息隔离白名单 | 黑名单七模式 + 白名单六项 + 行首预判正则 + 上游禁注入（R1 已固化） | ✓ | 边界/多端 |
| BDD-5 verdict 机器可读字段完备 | Header status 三值 + criteria_total/passed/verdict_evidence 存在性 + passed 时相等断言 | ✓ | 边界 |
| BDD-6 证据交叉核对 | 引用存在 + 非空 + md5 去重 | ✓ | 边界 |
| BDD-7 事件账本 append-only + 哈希链 | prev_hash 链完整 + 时间戳单调 + 仅追加；空文件/起始行合法态已声明 | ✓ | 数据 |
| BDD-8 三档预算诚实降级 | 超限 → status: needs-revision + partial: true + 账本 reason: budget_exhausted；partial → gate 不通过（fail-closed） | ✓ | 边界 |
| BDD-9 哲学红线：exit code 才是门槛 | 机械核对任一 exit 1 → P6.5 gate exit 1、转移阻断；LLM 结论不单独放行 | ✓ | 多端 |
| BDD-10 协议一致性与回归 | consistency 0 ERROR + pytest 全绿 + count-tests 不漂移 + 既有校验不误报 | ✓ | 兼容/多端/数据 |

无中间态（无"⚠️ 调整""部分通过"类表述）；每条 BDD 单条 Given-When-Then，多场景已拆独立编号。

## 四、同类扫描三组 + 哲学红线/历史兼容/三层防造假/预算复核

- **同类扫描三组**：首轮已独立核实全部属实（10 review-roles 文件 / role-system L108-116 status 映射 / review-mapping L38-42 / dispatch-protocol L575-577 迭代表 / C8 表 L52-66；dispatch-context 模板 / pre-commit-gate L350-397 / 双 inject 脚本 / agate-extract-context / 审计 2 L318-355 先例；check-p6-provenance 审计 1-7 / check-p6-evidence / agate-evidence-consistency）。**修改轮 1 仅改措辞/标题/BDD-4 内容，未改动任何扫描命中声明**，无需重验；新引入的"黑名单/白名单"项属需求判据设计而非仓库事实声明，已由 R1 复核覆盖。
- **哲学红线**：BDD-9 判定达标（同首轮，未改动）。
- **历史兼容**：BDD-2 判定达标（同首轮，未改动）；实测 `MAX_RETRY_MAP`/`_PHASE_OUTPUTS`/`valid_phases`/`_PHASES` 均无 P6.5，存量兼容必要面由 BDD-2 + BDD-10 双兜底。
- **三层防造假**：信息隔离（BDD-4，R1 后机械可判定）/ 证据交叉核对（BDD-5/6）/ 事件账本（BDD-7）三层各自有可二值判定主体与 fail-closed 语义 ✓。
- **三档预算**：BDD-8 轮次≤2 / token 100k（judge_token_budget 覆盖）/ 30min，超限诚实降级 partial:true → needs-revision 不静默放行 ✓。

## 五、其余基线要素复核（复评审定不变项）

- **frontmatter 六项**：risk_level: medium（与实际风险匹配）/ phases 全流程无跳过（理由充分）/ packages: [agate] / domains: [backend]（无 UI，不声明 ui_render_shape 正确）/ capability_requirements: []（§7 理由成立，无 supplementable/GAP 项）— 合法。
- **P0-brief 时效性**：§2 四步核对（HEAD 4604836 / check-routing + agate-risk-score 实测存在 / 四字段齐全 / LIMITATIONS-3 原文）已独立复核属实，无 `[P0_STALE]`。
- **P1 纯净性**：交付物清单属范围声明（上游 P0/设计文档锁定）；事件 schema / 扫描实现 / valid_phases 扩展方式显式留 P2；[NO_NEED_CONFIRM] + 2 条 SUGGEST 不阻塞。
- **gate 门槛满足性**：BDD 格式 `#### BDD-NN:` ✓（10 条）；P1-review status: approved + agent: requirements-review（≠main）+ 含 BDD 编号锚点（本文件全文引用 BDD-1~10）✓。

## 六、复评结论

R1（BDD-4 黑名单路径引用集固化 + §4.2 表 + 上游关联禁注入）与 R2（七道审计口径统一）均正确修复并经独立复核；10 条 BDD 全部可二值判定、编号连续；同类扫描三组扎实无虚报；哲学红线/历史兼容/三层防造假/预算四项评审重点全部达标；frontmatter 六项合法、裁剪合理、P1 纯净、无待确认阻塞项。

**P1 需求基线通过评审，可推进 P2。**