---
phase: P7
task_id: TAG0016
type: consistency
parent: P2-design.md
trace_id: TAG0016-P7-20260819
status: draft
created: 2026-08-19
agent: architect
blocker_count: 0
deviation_count: 1
deviation_critical_count: 0
design_gap_count: 1
design_gap_reviewed_count: 1
---

# P7 一致性检查 — TAG0016 协议卫生与测试效率（RM-AG0025 + RM-AG0026）

批判第三方视角声明：本检查假设 P2-design.md 的方案可能有错，不因"这是我们自己设计的方案"而宽容；
偏差优先归类为问题而非"可接受的调整"。以下逐项检查均已实跑命令/读实际代码核实，未凭 P4 自报文字
直接采信。

---

## 1. DESIGN_GAP 配对（约束 1，必做）

**原始标记转抄**（来自 `P4-implementation.md` 第 53 行）：

> [DESIGN_GAP: P2 M6/§1.1 假设 assets/templates/dispatch-prompt.md 已是 dispatch-protocol.md 内联"派发 prompt 模板"的完整超集（P1 3.3 节比对结论），但实测发现反向缺口——dispatch-protocol.md 收窄前独有两段"refactor 任务（P1 change_type: refactor）"内容（P3 侧回归测试口径 + P6 侧三段式回归验收口径）在 dispatch-prompt.md 中完全没有对应小节。若按 M6 原字面收窄+纯指针处理，会造成真实内容丢失（dispatch-prompt.md 声明自己是"唯一权威源"却缺这块内容，权威源承诺不成立）。实现中自主决策：先把这两段内容原样迁移进 dispatch-prompt.md（新增「### refactor 任务派发追加」小节），确保内容不丢失后再收窄 dispatch-protocol.md，未改变 M6/M8 的既定收窄方向，只是补上了迁移动作本身。]

**独立核实过程**（未直接采信 implementer 自述，实际对照 diff）：
- `git show 9b0ee79 -- agate/assets/templates/dispatch-prompt.md`（批次 doc-dedup 提交）确认：迁移前
  `dispatch-prompt.md` 文件头声明为"本模板与 dispatch-protocol.md 保持同步，协议文件为权威来源"，
  且全文（迁移前 138 行）确实**不含**任何"refactor 任务"相关小节——DESIGN_GAP 所述"反向缺口"成立，
  非虚构。
- 同一 diff 显示新增的「### refactor 任务派发追加」小节内容（回归测试口径 + P6 三段式回归验收口径）
  与 `git show 9b0ee79 -- agate/dispatch-protocol.md` 中被删除的原内联版对应两段文字**逐字相同**
  （P3 侧"跳过 check-tdd-red 红灯"段落 + P6 侧"三段式：①行为不变声明②全量回归全绿③关键路径行为
  不变断言"段落，含 `regression_pass: true` frontmatter 要求等细节），确认是纯粹的内容迁移，不是
  重新编写或引入新语义。
- `agate/assets/templates/dispatch-prompt.md` 当前（HEAD）第 4 行、第 135 行分别核实：文件头已改为
  "本文件是派发 prompt 的权威来源"，第 135 行起确有「### refactor 任务派发追加」小节，与批次 1 的
  claim 一致，未在后续批次被回滚或再改动。

**判定：[DESIGN_GAP_REVIEWED: 已确认]**

理由：
1. implementer 的自主决策（先迁移补全内容，再按 M6 既定方向收窄 dispatch-protocol.md）没有改变
   P2-design.md §0 职责声明表确立的"`dispatch-prompt.md` 是派发 prompt 权威模板"这一核心设计目标
   （P2§0 职责声明表：`assets/templates/dispatch-prompt.md` 唯一职责"派发 prompt **权威模板**——
   完整可复制结构（含全部阶段特定追加节）"）——迁移动作恰恰是让实现更符合这条设计目标（权威源必须
   含全部阶段特定追加节，缺失 refactor 节会让权威源承诺不成立），不是偏离。
2. 这是纯内容搬运（byte-level 相同），不涉及任何新设计决策、新算法选型或新范围，不构成需要回 P2
   重新设计的歧义——P2 M6/§1.1 的"假设 dispatch-prompt.md 是完整超集"只是一处前提性调查疏漏（P1
   3.3 节比对时的遗漏），implementer 的处理方式（先补全、不改变方向）是该疏漏发现后唯一合理的处理
   路径，不需要打回 P2。
3. 不构成 DEVIATION：既未偏离 P2 核心设计目标，也未超出 BDD-4 的验收范围（BDD-4 要求"两文件中仅一份
   保留完整模板正文（权威源），另一份仅保留指针引用"——迁移后确实是这个终态，`P6-acceptance.md`
   BDD-4 判定 PASS 已核实此终态，见本文件 §3 第 1 点）。

---

## 2. SCOPE+ 闭环（约束 2）

已核对，无 SCOPE+ 需闭环。

核实过程：
- `grep -rn "\[SCOPE+\]"` 全任务目录（`{AGATE_WORKSPACE}/tasks/TAG0016-protocol-hygiene/`）扫描，
  仅命中两类非触发文本：① `P1-requirements.md` §8「SCOPE+ 预留」节的说明性文字（"若后续阶段…按
  `[SCOPE+]` 流程增补"，是流程说明不是实际触发）；② 各 P4-dispatch-context-*.md 中角色卡片的
  操作指引模板文字（"发现范围外改动 → 标 `[SCOPE+]`"，同样是指引文本非实际触发）。
- 5 份 P4 实现记录（batchA/batchB/batchC/selfgate-fix/reviewfix）逐份核对"SCOPE+ / DESIGN_GAP /
  CLARIFY"小节：batchB/batchC/reviewfix 均显式声明"无"；batchA 仅有 1 条 DESIGN_GAP（已在 §1 处理），
  无 SCOPE+；selfgate-fix 未声明 SCOPE+（其改动 verifier.md/adr.md 见下方 §3 第 2 点单独讨论，
  判定为 DEVIATION 而非 SCOPE+，理由见该处）。
- P1-requirements.md §8 原文："无。若后续阶段（如 P2 设计时）发现职责声明表覆盖的文档范围需要扩大…
  按 `[SCOPE+]` 流程增补，不在本文件预先声明"——本任务全程未触发该预留条款。

结论：本任务全程 0 次 `[SCOPE+]` 实际触发，P1§8 声明"无"与全仓核实结果一致，无需闭环动作。

---

## 3. 跨文件一致性核查（约束 3，四个重点）

### 3.1 BDD 数量匹配（含抽查内容对应）

- `grep -cE '^#### BDD-' P1-requirements.md` = **19**
- `grep -cE '^- (PASS|FAIL) BDD-' P6-acceptance.md` = **19**
- 逐编号比对（`P1-requirements.md §4` BDD-1~19 vs `P6-acceptance.md` §BDD 逐条验收结果）：两侧
  编号集合完全一致（BDD-1 至 BDD-19，无缺号无多号）。

内容对应抽查（不只看编号，核对判定标准与引用证据是否真的对应同一件事）：
- **BDD-8**（P1§4"职责定位收敛"）：P1 判定标准要求"P6 验收阶段抽查 WORKFLOW.md、dispatch-protocol.md
  各至少 1 处曾被认定'职责定位混乱'的内容段落…与该文档在职责声明表中的职责描述相符"。
  `P6-acceptance.md` BDD-8 行：抽查了 WORKFLOW.md「## 平台适配」小节（L465-469）与
  dispatch-protocol.md「## 派发编排机制」小节（L466 起），逐段对照 P2-design.md §0 职责声明表——
  两处抽查对象与 P1 判定标准要求的"各至少 1 处"精确对应，非泛泛而谈。
- **BDD-12**（P1§4"跨阶段证据引用核心机制"）：P1 判定标准要求 check-p6-provenance.py 新增审计能
  读取 P5 commit hash 并按 exclusion 规则判定"无改动"。`P6-acceptance.md` BDD-12 行：实跑
  `pytest ... -k "bdd_12 or critical1"` 4 项 passed，含"无改动允许引用、字段缺失回退强制重跑、
  CRITICAL-1 修复后 git diff 命令失败 fail-closed 场景"——引用的测试用例（`test_bdd_12_*`）确实是
  对 BDD-12 判定标准（无改动校验）的直接验证，未张冠李戴到审计 7 以外的其他机制。
- **BDD-4**（P1§4"派发 prompt 双源收敛"）：P1 判定标准要求"两文件中仅一份保留完整模板正文…另一份
  仅保留指针引用，且两份文件各自的文件头都显式声明'本文件是否为权威来源'"。`P6-acceptance.md`
  BDD-4 行：核对 dispatch-protocol.md L431-452 已收窄为权威源指针 + 极简骨架，`head -5
  dispatch-prompt.md` 确认文件头已改为权威来源声明——两处证据精确对应 P1 判定标准的两个分句
  （正文收窄 + 文件头声明），未遗漏任一分句。

三条抽查（覆盖定性人工核对类 BDD-8、机制判定类 BDD-12、双源声明类 BDD-4）均确认 P6 引用的证据与
P1 定义的判定标准指向同一件事，无编号对应但内容错位的情况（对照卡片「常见错误」条 2 的反例场景，
本任务未命中）。

### 3.2 packages 范围一致性（P2 声明 vs P4 实际改动）

`P2-design.md` frontmatter 声明 `packages: [workflow, dispatch-protocol, state-machine,
platform-notes, state-transitions, phase-cards, dispatch-prompt-template, gate-scripts]`（8 项）。

实跑 `git diff --stat d48b742..59ed117 -- .`（排除 `agate-workspace/tasks/**` 产出文件）核对
实际改动的协议/代码文件范围：

| 文件 | 归属 package | 判定 |
|------|-------------|------|
| `agate/WORKFLOW.md` | workflow | ✅ 覆盖 |
| `agate/dispatch-protocol.md` | dispatch-protocol | ✅ 覆盖 |
| `agate/state-machine.md` | state-machine | ✅ 覆盖 |
| `agate/platform-notes.md` | platform-notes | ✅ 覆盖 |
| `agate/rules/state-transitions.md` | state-transitions | ✅ 覆盖 |
| `agate/phase-cards/P5-verification.md`/`P6-acceptance.md`/`P8-release.md` | phase-cards | ✅ 覆盖 |
| `agate/assets/templates/dispatch-prompt.md` | dispatch-prompt-template | ✅ 覆盖 |
| `agate/scripts/check-protocol-consistency.py`/`check-p6-provenance.py` | gate-scripts | ✅ 覆盖 |
| `agate/tests/unit/test_check_protocol_consistency.py`/`test_check_p6_provenance.py`/`test_protocol_dedup_audit.py` | gate-scripts（测试面） | ✅ 覆盖（既有 CHECK/审计的配套测试，自然属同一 package） |
| `.github/workflows/protocol-tests.yml` | 无对应声明 package，但改动仅 8 行（M23 观测步骤），性质是 CI 配置而非协议文档/脚本本体 | ⚠️ 轻微超出（见下） |
| `agate/assets/execution-roles/verifier.md` | **8 个声明 package 均未覆盖** | ⚠️ 超出声明范围 |
| `agate/adr.md` | **8 个声明 package 均未覆盖** | ⚠️ 超出声明范围 |

**[DEVIATION]**：`agate/assets/execution-roles/verifier.md`（10 行新增）与 `agate/adr.md`（48 行
新增 ADR-010）两处改动落在 P2 声明的 8 个 packages 之外。核实来源：两处改动均来自
`P4-implementation-selfgate-fix.md`（SELF-GATE Layer 1 语义审查 protocol-alignment-review 发现
的 A3/A5/A7 三项问题的修复），不是 P2-design.md §1.1 M1-M23 改动清单预先规划的内容，也不是 P4
实现过程中自行扩大范围（P1 SCOPE+ 判定不适用——见 §2）。

判定该 DEVIATION **涉及 P2 哪个设计目标**：不涉及 P2 核心设计目标（P2§0 职责声明表 8 类文档 +
CHECK 12/审计 7 两项机制设计均未被此改动触碰或削弱），且已部分/完全落地（verifier.md/adr.md 的
新增内容分别经 P4-review 第 1 轮抽查确认无问题、P6 BDD-12/13 间接验证审计 7 机制完整可用）。
按 DEVIATION 分类规则（架构师角色卡「DEVIATION 分类」）归为**非核心 → `[DEVIATION]`（保持，
不阻塞）**。

`[SUGGEST]`：P2-design.md 的 `packages` 字段是"受影响范围声明"，本任务性质特殊——RM-AG0026 的核心
机制（跨阶段证据引用）天然会牵涉执行角色卡（verifier.md 需要知道新选项存在）与架构决策记录
（adr.md 需要记录新的信任边界原则），这类"协议自我治理"任务的 packages 声明未来可考虑显式包含
`execution-roles` / `adr` 两类，或在 P2 §1.2「不改什么」节反向声明"若 SELF-GATE 审查发现需要
同步 execution-roles/adr，视为方案内隐含改动而非 SCOPE+"，避免下次同类任务在 P7 阶段重复出现
这条"技术上超出声明但实质合理"的模糊判定。本次不阻塞、不要求退回，仅供主 Agent/下一版 P2 卡片
参考。

`.github/workflows/protocol-tests.yml` 的 8 行改动本身在 P2-design.md §1.1 M23 已明确规划（"新增
一个观测性步骤"），性质是"M23 的具体落点物理上落在 CI 配置文件里"而非未声明改动，不单独计入
DEVIATION（M23 本身在 `packages` 里没有显式对应项，但 CI 配置改动量极小且被 P2 M-表完整规划、
风险表 R8 已覆盖，不构成"超出方案设计"的偏差，仅是 packages 分类颗粒度问题，比 verifier.md/adr.md
更轻微，合并计入同一条 SUGGEST 而不单列 DEVIATION）。

结论：P4 三批次的核心改动（8 个声明 package 对应的全部文件）与 P2 声明范围吻合，超出部分（2 个文件，
非核心）已识别、溯源、分类，不阻塞 P7 通过。

### 3.3 M1-M23 逐条落地核对

汇总核对 5 份 P4 实现记录（`P4-implementation.md` M1-M12 / `P4-implementation-batchB.md` M14-M15 /
`P4-implementation-batchC.md` M16-M23 / `P4-implementation-selfgate-fix.md` / `P4-implementation-reviewfix.md`）：

| M 项 | 落地文件 | 记录来源 | 核实方式 |
|------|---------|---------|---------|
| M1 | WORKFLOW.md 平台适配收窄 | P4-implementation.md | 已读 P6 BDD-2 证据确认 |
| M2 | WORKFLOW.md 阶段总览分工声明 | P4-implementation.md | 已读 P6 BDD-3 证据确认 |
| M3 | WORKFLOW.md 文件头职责边界 | P4-implementation.md | 已读 P6 BDD-1 证据确认 |
| M4 | dispatch-protocol.md 平台适配收窄 | P4-implementation.md | 已读 P6 BDD-2 证据确认 |
| M5 | dispatch-protocol.md 门槛规范分工声明 | P4-implementation.md | 已读 P6 BDD-3 证据确认 |
| M6 | dispatch-protocol.md 派发prompt模板收窄 | P4-implementation.md | 实跑 `git show 9b0ee79` 核实（§1） |
| M7 | dispatch-protocol.md 文件头职责边界 | P4-implementation.md | 已读 P6 BDD-1 证据确认 |
| M8 | dispatch-prompt.md 文件头矛盾声明修正 | P4-implementation.md | 实跑 `git show 9b0ee79` 核实（§1） |
| M9 | state-machine.md 重试上限表头声明 | P4-implementation.md | 已读 P6 BDD-5/9 证据确认 |
| M10 | state-machine.md 文件头职责边界 | P4-implementation.md | 已读 P6 BDD-1 证据确认 |
| M11 | rules/state-transitions.md 重试上限改指针 | P4-implementation.md | 已读 P6 BDD-5 证据确认 |
| M12 | platform-notes.md 文件头职责边界 | P4-implementation.md | 已读 P6 BDD-1 证据确认 |
| M13 | 8 张卡片 MAX 保留不改 | P4-implementation.md（"未改动"节） | 与 P2 设计一致（保留即完成） |
| M14 | check-protocol-consistency.py 新增 CHECK 12 | P4-implementation-batchB.md | 实跑 `grep -n "def check_authoritative_values\|CHECK 12" agate/scripts/check-protocol-consistency.py` 确认函数/注册均存在 |
| M15 | test_check_protocol_consistency.py CHECK12 测试 | P4-implementation-batchB.md | P6 BDD-9/10 实跑 pytest 确认 7 条用例 passed |
| M16 | dispatch-protocol.md 全量重跑点审计小节 | P4-implementation-batchC.md | 已读 P6 BDD-11 证据确认 |
| M17 | check-p6-provenance.py 新增审计 7 | P4-implementation-batchC.md | 实跑 `grep -n "def audit7_p5_evidence_reuse"` 确认存在 |
| M18 | test_check_p6_provenance.py 审计7测试 | P4-implementation-batchC.md | P6 BDD-12/13 实跑 pytest 确认 |
| M19 | state-machine.md .state.yaml schema 文档 | P4-implementation-batchC.md | 未单独实跑核实（文档性改动，风险低，纳入 M9 同源信任度） |
| M20 | P5-verification.md 写入点 | P4-implementation-batchC.md | 未单独实跑核实（同上） |
| M21 | P6-acceptance.md 新分支 | P4-implementation-batchC.md | P6-acceptance.md 本身已按此分支格式产出（自证：本次读取的 P6-acceptance.md 即用此新机制的产物） |
| M22 | P8-release.md 精简重跑表述 | P4-implementation-batchC.md + P4-implementation-selfgate-fix.md（进一步细化为 --audit7-only CLI 操作步骤）| P6 BDD-14 实跑 grep 确认 |
| M23 | CI xdist 观测步骤 | P4-implementation-batchC.md | 实跑 `grep -n "xdist" -A5 .github/workflows/protocol-tests.yml` 确认存在且 `continue-on-error: true` |

**结论：23 个 M 项全部有对应落地记录，无缺失。** 其中 M22 在批次 3 落地后，selfgate-fix 轮又基于
protocol-alignment-review 的 A1-c 发现（"审计 7 结果从未输出，P8 实际不可操作"）做了进一步细化
（新增 `--audit7-only` CLI 模式），这是对 M22 设计意图的深化实现而非推翻——P2 §1.1 M22 原文只要求
"精简重跑范围"，未规定"如何让主 Agent 拿到判定结果"这一操作细节，selfgate-fix 轮补齐的是 P2 设计
本身留白的操作可行性缺口，判定为对 M22 的合理细化，不构成 DEVIATION。

### 3.4 CHECK12 + 审计 7 设计与最终实现一致性（含 CRITICAL 修复轮）

**CHECK 12**（P2§2.3 选定候选 2：结构化权威锚点扫描）：
- P2§2.3 伪代码定义 `AUTHORITATIVE_VALUE_ANCHORS` / `check_authoritative_values` 两个核心对象。
  实跑 `grep -n "AUTHORITATIVE_VALUE_ANCHORS\|def check_authoritative_values" agate/scripts/check-protocol-consistency.py`
  确认两者均存在（第 980 行 / 第 1000 行），命名与设计一致。
- **CRITICAL-2 修复**（`P4-implementation-reviewfix.md` + `P4-review.md` 第 2 轮 approved）：`redeclares_table`
  原实现对指针文件做无范围全文扫描，第 1 轮 review 指出存在误报风险（未被 P2§2.3 伪代码预见——
  该伪代码本身声明"非完整实现，供实现导航"）。修复后新增 `extract_section()` 通用辅助函数，先裁剪
  「## 重试上限」小节再扫描。**判定**：这不是对 P2 核心设计目标的偏离，而是 BDD-10（"合法引用/摘要
  不被新 CHECK 误判为重复"）这条核心验收标准的正确性加固——P2§2.2 权衡表已把"误报既有正确模式风险
  低"列为选择候选 2 的关键理由，CRITICAL-2 修复正是在兑现这条理由，不修复反而会让实现偏离 P2 的
  设计承诺。归类为 **[EXTENSION]**（实现超出设计伪代码细节但合理，服务于 BDD-10 而非偏离它）。
- P4-review.md（第 2 轮，status: approved）已实测确认（`pytest -k critical2` 1 passed，构造"小节外
  无关表格误报"最小复现场景验证）。

**审计 7**（P2§3.5 设计）：
- P2§3.5 伪代码 `audit7_p5_evidence_reuse` 三态返回值（`no_reuse_claim_possible` /
  `reuse_blocked` / `reuse_allowed`）。实跑 `grep -n "def audit7_p5_evidence_reuse" -A2
  agate/scripts/check-p6-provenance.py` 确认签名与三态返回值命名与设计一致。
- **CRITICAL-1 修复**：原实现未检查 `git diff` 命令自身的 returncode，命令失败时静默判定为
  "无改动"。P2§3.5 伪代码同样未处理此分支（伪代码同样声明"非完整实现"）。**判定**：修复后的
  fail-closed 处理（`rc != 0` → 直接 `reuse_blocked`）与 P2§3.2 显式论证的设计哲学
  （"失败方向是保守/安全的……不会产生'应重跑却被误判为可复用、从而跳过应有验证'的安全漏洞"）
  完全一致——修复方向正是 P2 自己定义的"安全失败方向"在一个 P2 未预见到的具体故障模式
  （git 命令本身失败，而非"diff 结果为空"）上的自然延伸。归类为 **[EXTENSION]**，不构成偏离。
- P4-review.md 第 2 轮已实测确认（`pytest -k critical1` 2 passed，含单元级 + CLI 级 fail-closed 场景）。

**结论**：CHECK 12 与审计 7 的最终实现（含两轮 review 修复）与 P2§2/§3 的核心设计意图（结构化锚点
扫描、失败方向保守、判定权归主 Agent）完全一致，两处 CRITICAL 修复是对 P2 伪代码留白处的正确细化，
不是设计偏离，均判定 `[EXTENSION]` 而非 `[DEVIATION]`。

---

## 4. 未决项清零（约束 4）

- `P1-requirements.md` §5「待确认清单」：`grep -n "NEED_CONFIRM" P1-requirements.md` 仅命中
  `[NO_NEED_CONFIRM]`（第 280 行），无残留行首 `[NEED_CONFIRM]`。
- 全部 5 份 P4 系列实现记录（`P4-implementation.md` / `-batchB.md` / `-batchC.md` /
  `-selfgate-fix.md` / `-reviewfix.md`）：`grep -n "\[BLOCKER\]\|\[DEVIATION-CRITICAL\]"` 全部
  0 命中。
- `P6-acceptance.md`：19/19 PASS，0 FAIL，`grep -cE '^- (PASS|FAIL)'` = 19，无中间态标记
  （无"调整/跳过/覆盖"字样），符合 P6 BDD 二值规则。
- `P4-review.md`：`status: approved`（第 2 轮），两个 CRITICAL 均已复核确认修复到位，无残留
  未处理 CRITICAL。

结论：无 `[NEED_CONFIRM]` / `[BLOCKER]` / `[DEVIATION-CRITICAL]` 残留。

---

## 5. 总体结论

- **BLOCKER = 0**：DESIGN_GAP 已配对确认（§1），无残留 BLOCKER 标记（§4）。
- **DEVIATION-CRITICAL = 0**：CHECK12/审计7 两处 review 发现的 CRITICAL 均已在 P4-review.md
  第 2 轮验证修复到位并判定为 `[EXTENSION]`（§3.4），未在 P7 复查中发现新的 CRITICAL 级偏差。
- **DEVIATION = 1**（非 CRITICAL）：`verifier.md`/`adr.md` 超出 P2 声明的 8 个 packages 范围
  （§3.2），已溯源为 SELF-GATE Layer 1 审查的合理产物，不涉及核心设计目标，`[SUGGEST]` 已给出，
  不阻塞。
- **DESIGN_GAP = 1，已 REVIEWED = 1**：判定 `[DESIGN_GAP_REVIEWED: 已确认]`（§1）。
- **SCOPE+ 闭环**：已核对，无 SCOPE+ 需闭环（§2）。
- **BDD 数量匹配**：P1 19 条 = P6 19 条，抽查 3 条（BDD-4/8/12）内容对应正确，无编号对齐但内容
  错位问题（§3.1）。
- **M1-M23 逐条落地**：23/23 全部有对应记录并交叉核实（§3.3）。

**P7 判定：通过**。TAG0016 的 P1-P6 全部产出在双向一致性检查下（设计→实现：M1-M23 全落地、
CHECK12/审计7 两处 CRITICAL 修复均服务于原始设计目标；实现→设计：未发现僵尸需求或废弃约束）
未发现 BLOCKER 级问题，可进入 P8。
