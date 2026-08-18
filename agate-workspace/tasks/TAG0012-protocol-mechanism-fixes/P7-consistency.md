---
phase: P7
task_id: TAG0012-protocol-mechanism-fixes
type: consistency
parent: P2-design.md
trace_id: TAG0012-P7-20260818
status: approved
created: 2026-08-18
agent: consistency-reviewer
# ── v2.0 机器计数 ──
blocker_count: 0
deviation_count: 0
deviation_critical_count: 0
design_gap_count: 0
design_gap_reviewed_count: 0
---

[PROD_NOT_TOUCHED]

# P7 一致性检查 — TAG0012 协议机制增强批

> 本文件对照 P0-P6 全部产出做跨文件一致性审查。dispatch-context 明确要求"预期干净也要逐项实质核查"，
> 下面每一项均给出独立核实的具体动作（grep 命令 / 文件行号 / diff 比对），不满足于转抄 P4/P6 的自述。

## 1. DESIGN_GAP 配对核查

**P4-implementation.md 自报 0 条 `[DESIGN_GAP:]`。独立核实（不采信自述）：**

```
git show 27509a2 | grep -nE '^\+\s*(\[DESIGN_GAP:|\[SCOPE\+\])'   → 零命中
grep -rnE '^\s*\[DESIGN_GAP:|^\s*-\s*\[DESIGN_GAP:' agate-workspace/tasks/TAG0012-protocol-mechanism-fixes/*.md → 零命中
```

对 P4 实际改动的 12 个文件全文 grep `\[DESIGN_GAP` 有若干命中（`dispatch-protocol.md:1042/1045/1046/1194`、
`architect.md:184-187`、`task-files.md:436/443`、`state-machine.md:143`），但逐条核对后确认这些**全部是
描述"DESIGN_GAP 处理机制本身"的既有协议正文/角色规则文本**（v0.6 既有机制的说明，非本任务新增的偏差
声明），不是行首格式的 `[DESIGN_GAP: 具体描述]` 真实标记。

**结论：BLOCKER=0（P4 自报 0 条 DESIGN_GAP 属实，独立核实通过，无需 REVIEWED 配对）。**
锚点：`P4§implementation` 决策标注第 3 节 + 本次 `git show 27509a2` 全文 grep 复核。

**附加说明**：预跑 `check-gate.py P7` 校验本文件时产出 1 条非阻塞 WARNING——"P4 检测到设计偏差相关关键词
但 `[DESIGN_GAP:]` 计数为 0"。核实为脚本启发式粗筛的误报：`P4-implementation.md` 决策标注第 3 节 /
implementer.md 读完清单等处正常提及"DESIGN_GAP"字样是在描述该机制本身（本任务恰好是"协议机制增强批"，
P4 正文内容天然会涉及机制名称），并非真实偏差声明。exit code 仍为 0（gate 通过），不构成 BLOCKER。

## 2. SCOPE+ 闭环核查

**P4-implementation.md 自报 0 条 `[SCOPE+]`。独立核实：**

```
git show 27509a2 | grep -nE '^\+\s*\[SCOPE\+\]'  → 零命中
grep -rn 'SCOPE+' P0-brief.md P1-requirements.md P2-design.md P4-implementation.md P6-acceptance.md
```
命中的 3 处（`P4-implementation.md:110`、`P2-design.md:402/404`）均为"声明 0 条"的自述文本本身，不是
真实 `[SCOPE+]` 标记。

P1-requirements.md §2 第 6 点存在 1 条 `[SUGGEST: 同类扫描机制不追溯历史产出]`——核实这是 **SUGGEST 不是
SCOPE+**（P1 §4 待确认清单已明确"方向明确、不涉及破坏性变更/业务判断，主 Agent 可直接采纳"），语义上是
"P1 对自己 §2.6 隐含需求识别问题给出的建议性回答"，不是"P1 之外发现的范围外必做事项"，因此不适用
`[SCOPE_RESOLVED]` 配对机制（该机制服务于 `[SCOPE+]`，不服务于 `[SUGGEST]`）。全仓 grep 无 `[SCOPE_RESOLVED]`
标记，与"无真实 SCOPE+"的结论一致（无 SCOPE+ 就不需要 SCOPE_RESOLVED）。

**结论：SCOPE+ 闭环成立（0 条 SCOPE+，独立核实通过；1 条 SUGGEST 已被 P1 自身采纳，非 SCOPE+ 误判）。**
锚点：`P1§2.6 SUGGEST` + `P1§4 待确认清单` + `P4§implementation` 决策标注第 2 节。

## 3. 跨文件数量一致性

### 3.1 P1 BDD 总数 vs P6 验收结果数量

```
grep -oE '^#### BDD-[0-9]+b?:' P1-requirements.md | sort -V  → 23 条（BDD-1~22 + BDD-15b）
grep -oE '^- PASS BDD-[0-9]+b?:' P6-acceptance.md | sort -V  → 23 条，编号集合与 P1 完全一致
grep -cE '^- FAIL BDD' P6-acceptance.md → 0
```
两侧编号集合逐一比对（`diff` 无差异），非仅数字巧合相等。

**编号-内容抽查（6 条，覆盖首/中/尾及特殊编号 BDD-15b）：**

| BDD | P1 Then 要点 | P6 PASS 描述要点 | 独立复核（读实际文件） |
|-----|------------|-----------------|----------------------|
| BDD-1 | 新增小节要求填 known_risks 前做"同类/影响面预判"，可 grep 命中 | 新增 `## 同类/影响面预判` 小节，预判三问 | `grep -n '同类/影响面预判' agate/phase-cards/P0-orchestrator.md` → 命中 5 处（含小节标题） |
| BDD-8 | 新增判断树+自问句"缺的是能力还是环境？" | 「三态判断规则」后新增判断树，同一自问句 | `grep -n '缺的是能力还是环境' agate/assets/execution-roles/analyst.md` → 命中 |
| BDD-13 | 5 点：倍数规则/超时三动作/非预期失败同处理/落盘粒度扩展/层级区分 | 5 点全覆盖，×1.5 + 层级 4 对照表 | `grep -n '命令超时兜底\|层级 4\|×1.5' agate/dispatch-protocol.md` → 均命中（L473/476/517/519/526/530/531/534） |
| BDD-15b | architect.md 新增检查项引用 P2 卡影响面梳理，不重复展开，与 analyst.md 对称 | 「批次设计前置检查项」第1条引用 P2 卡，"本节不重复展开" | `grep -n '影响面梳理' agate/assets/execution-roles/architect.md` → L209/210 命中，引用式写法确认 |
| BDD-16 | 4 点：声明粒度/基准来源/向后兼容/P3关系 | 4 点全覆盖，三档基准表 120/300/600s | `grep -n 'timeout_seconds 字段规则\|120s\|300s\|600s' agate/phase-cards/P2-design.md` → 均命中（L134/140-142） |
| BDD-22 | 两分支合法收敛：脚本校验+TDD证据 or P2显式声明理由 | 走第二分支，P2§3.7 显式声明+理由，check-gate.py 未改 | `git show 27509a2 --stat | grep check-gate` → 无输出，确认未改动，与 P6 判定一致 |

未发现编号错位或内容张冠李戴。

### 3.2 P2 packages 与实际改动文件类别

P2 frontmatter `packages: [phase-cards, dispatch-protocol, state-machine, execution-roles, templates, scripts]`。
实际改动 12 文件按目录归类：

- `phase-cards`：P0-orchestrator.md / P1-requirements.md / P2-design.md / P5-verification.md / P6-acceptance.md ✅
- `dispatch-protocol`：dispatch-protocol.md ✅
- `state-machine`：state-machine.md ✅
- `execution-roles`：analyst.md / architect.md / verifier.md ✅
- `templates`：dispatch-prompt.md / task-files.md ✅
- `scripts`：**未见 `agate/scripts/*` 下任何文件被改动**（`git show 27509a2 --stat --name-only | grep 'agate/scripts/'` 零命中）。
  本任务唯一新增"代码"是 `agate/tests/unit/test_protocol_mechanism_anchors.py`，路径属 `agate/tests/`
  而非 `agate/scripts/`。

按 dispatch-context 约束 3 第二条明示"P8 尚未执行，无法核对 P8 bump 范围，这一项在本次 P7 标注'待 P8
核对'而非强行判定"——**本项不判 BLOCKER，仅标注供 P8 核对**：P8 release 若按 `packages` 逐类 bump
CHANGELOG，需注意 `scripts` 类别实际无对应文件改动，`tests` 类别（新增测试文件）未被 packages 列出，
P8 需据此决定 CHANGELOG 分类是否需要调整措辞（如把 `scripts` 改述为"含测试新增"或补充说明），不属于
本任务范围内的设计缺陷。

锚点：`P2§packages`（frontmatter）+ `P4§implementation` §5 范围核对。

### 3.3 P4 实现路径 与 P2§2.1 改动落点表

`P2§2.1` 表格实际统计（非采信 dispatch-context 给出的"13 行"）：

```
awk '/^### 2.1/,/^### 2.2/' P2-design.md | grep -cE '^\| `agate/'  → 16 行
```

**发现与 dispatch-context 描述不一致之处**：dispatch-context 称"13 行"，实际逐行统计为 **16 行**——
原因是 `dispatch-protocol.md` 一个文件因涉及 4 个不同小节（verification_env 失败处理协议 / 环境准备
职责边界 / 并行规则§4 / 派发 prompt 模板正文+L521 示例块）被拆成 4 行分别描述改动点，行数≠文件数。
这是 dispatch-context 客观查证信息的一处表述不准确（非 BLOCKER，不影响下方文件级核对结论）。

**改用 unique 文件层面核对**（更贴合 P4"12 个文件"的统计口径）：

```
P2§2.1 表 unique 文件（去重）= 13 个（12 个待 P4 落地 + 1 个 test_protocol_mechanism_anchors.py 属 P3 产出）
P4§implementation §5「范围核对」实际改动 12 个文件（git status --short 记录）
```

逐一比对：P2 表 13 个 unique 文件中，除 `test_protocol_mechanism_anchors.py`（P3 阶段已产出，P4 明确
标注"不改"）外，其余 12 个与 P4 实际改动的 12 个文件**一一对应，无遗漏无多余**：

| P2§2.1 unique 文件 | P4 是否改动 |
|---|---|
| P0-orchestrator.md | ✅ |
| state-machine.md | ✅ |
| P1-requirements.md | ✅ |
| analyst.md | ✅ |
| dispatch-protocol.md | ✅ |
| dispatch-prompt.md | ✅ |
| P2-design.md | ✅ |
| architect.md | ✅ |
| P5-verification.md | ✅ |
| verifier.md | ✅ |
| P6-acceptance.md | ✅ |
| task-files.md | ✅ |
| test_protocol_mechanism_anchors.py | 不改（P3 已产出，P4 §1 首段已声明） |

锚点：`P2§2.1` 改动落点表 + `P4§implementation` §1/§5。

## 4. 未决项清零

```
grep -rnE '^\s*\[NEED_CONFIRM\]|^\s*\[BLOCKER\]|^\s*\[DEVIATION-CRITICAL\]' agate-workspace/tasks/TAG0012-protocol-mechanism-fixes/*.md
→ 零命中（覆盖 P0-brief.md / P1-requirements.md / P2-design.md / P4-implementation.md / P6-acceptance.md
  及全部 dispatch-context / review / progress / evidence 文件）
```

P1 §4「待确认清单」为 `[NO_NEED_CONFIRM]`；P6 frontmatter `[NO_NEED_CONFIRM]` + `[PROD_NOT_TOUCHED]`。

**结论：未决项清零，无残留。**

## 5. RM-AG0013 自证闭环观察（dispatch-context 约束 5，非独立检查项）

本任务自身对"同类扫描/影响面梳理"机制的自洽性：

- P1-requirements.md §0「同类扫描核实结论」6 点，均标注已实际读取源码/协议文件验证（如 `timeout`
  四层机制辨析、`gate_commands`/`dispatch_plan` 权威 schema 定位、`并行规则`既有权威节确认等），非空转声明。
- P2-design.md §0「影响面梳理」4 点，均给出可复核的 grep/读代码动作（`verification_env` 全仓 4 处 /
  `timeout_seconds` 零命中复核 / `check-protocol-consistency.py` 扫描面确认 / 重试上限表参照）。

两处均留有可独立复核的证据链，符合"新机制在真实任务里最后被验证"的自洽性预期。

## 6. SELF-GATE 语义对齐审查 HUMAN_CONFIRMED 裁决核实（dispatch-context 约束 6）

`docs/reviews/agate-alignment-review-TAG0012.md` A4/A7 两条 NEEDS_HUMAN_REVIEW 已附 `[HUMAN_CONFIRMED:]`
裁决，核实与 P1-P2 设计文档口径的一致性（不重复 A1-A7 全套审查本身）：

- **A4**（测试覆盖止步存在性锚点）：`[HUMAN_CONFIRMED]` 引用"P2-design.md §3.6 已论证并经
  plan-eng-review approved 的设计取舍"——核对 `P2-design.md §3.6` 确实写明锚点测试是"存在性回归拦截"、
  语义正确性由人工评审兜底，口径一致。P6-acceptance.md §2 观察 2 也独立记录了同一取舍并给出相同理由，
  三处（P2/alignment-review/P6）互相印证，未发现新的不一致。
- **A7**（止损轮次不入 `.state.yaml`）：`[HUMAN_CONFIRMED]` 引用"P0-brief 约束 4（范围锁定）+
  P2-design.md §2.3 风险表已显式记录该取舍"——核对 `P2-design.md §1 候选方案 A` 缺点栏与 §2.3 风险表
  第 3 行确实写明"止损轮次无脚本强制...属范围约束下的合理取舍"，口径一致，未发现新的不一致。

**结论：两条 HUMAN_CONFIRMED 裁决与 P1/P2 设计文档口径一致，未引入新的不一致。**
锚点：`docs/reviews/agate-alignment-review-TAG0012.md` A4/A7 + `P2§3.6` + `P2§1候选A` + `P2§2.3`。

## 7. P6 证据文件完整性核验（附加动作）

```
ls agate-workspace/tasks/TAG0012-protocol-mechanism-fixes/P6-evidence/ | wc -l  → 24
```
= 23 条 BDD 逐条证据文件（`bdd-01-*.md` ~ `bdd-22-*.md` + `bdd-15b-*.md`）+ 1 个共享命令输出 log
（`shared-p6-command-output.log`），与 P6-acceptance.md 声明的 23 条一一对应，无缺失。

## 8. 总结

| 检查项 | 结果 |
|--------|------|
| DESIGN_GAP 配对 | BLOCKER=0（0 条 DESIGN_GAP，独立核实通过） |
| SCOPE+ 闭环 | 0 条 SCOPE+，1 条 SUGGEST 已被 P1 自身采纳，非误判 |
| P1 BDD 总数 vs P6 验收结果 | 23=23，编号集合完全一致，6 条抽查内容对应无错位 |
| P2 packages vs 改动文件类别 | 5/6 类完全命中，`scripts` 类别无对应文件改动（待 P8 核对，不判 BLOCKER） |
| P4 实现路径 vs P2§2.1 表 | unique 文件层面 12=12 完全吻合；发现 dispatch-context"13 行"表述不准确（实际 16 行，行数≠文件数），已记录但不影响结论 |
| 未决项清零 | 全任务目录 grep 零残留 `[NEED_CONFIRM]`/`[BLOCKER]`/`[DEVIATION-CRITICAL]` |
| SELF-GATE HUMAN_CONFIRMED 一致性 | A4/A7 裁决与 P1/P2 设计口径一致 |
| P6 证据文件完整性 | 24 个文件，23 BDD + 1 共享 log，与声明一致 |

**BLOCKER=0，DEVIATION-CRITICAL=0，DESIGN_GAP 未配对=0（无 DESIGN_GAP 声明，无需配对）。全部检查项通过，
无跨文件不一致发现构成阻塞。唯二记录但不影响通过的观察点：① dispatch-context 对 P2§2.1 表行数的
"13 行"表述与实际 16 行不符（行数统计口径问题，文件级结论不受影响）；② P2 packages 声明的 `scripts`
类别本任务实际无对应文件改动，留待 P8 核对 bump/CHANGELOG 分类措辞。**

推进条件（对照 phase-cards/P7-consistency.md）全部满足：P7-consistency.md 已产出、无 BLOCKER/
DEVIATION-CRITICAL、DESIGN_GAP 全部 REVIEWED 配对（0 条无需配对）、SCOPE+ 闭环（0 条无需 SCOPE_RESOLVED）。
可进入 P8。
