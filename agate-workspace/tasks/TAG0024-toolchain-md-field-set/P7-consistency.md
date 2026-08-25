---
phase: P7
task_id: TAG0024
type: consistency
parent: P2-design.md
trace_id: TAG0024-P7-20260825
status: draft
created: 2026-08-25
agent: consistency-reviewer
blocker_count: 0
deviation_count: 0
deviation_critical_count: 0
design_gap_count: 1
design_gap_reviewed_count: 1
---

# P7 一致性交叉检查 —— TAG0024 toolchain-md-field-set

## 1. DESIGN_GAP 配对（BDD-16）

转抄 `P4-implementation-md-field-set-tool.md` 第 59-85 行的原始声明：

> [DESIGN_GAP] BDD-16 测试用例数据缺陷（非实现问题，已诊断，未改测试）
> `test_bdd_16_zero_protocol_knowledge_walkthrough_converges` 失败于最后一步
> `check-gate.py P2 $TASK_DIR` 返回 1，stderr：`GATE P2: P2-design.md 有 ≥2 候选方案但缺
> '权衡'或'选择理由'描述`。根因：`task_dir(phases=["P1","P2"])` fixture 自动生成的
> `P2-design.md` 初始正文为空，不含 `gate_p2()` 要求的"权衡/选择理由"关键词——这是一条与
> task_fields 无关的正文散文 nudge，`agate-md-field-set.py` 按最小实现原则只写 frontmatter
> 字段与 `gate_commands` 正文块，不应替测试注入散文文案。implementer 判定为 P3-test-cases
> 对 BDD-16 fixture 数据的遗漏，未修改测试文件，也未在 set 工具里加超出 P2 设计范围的功能。

**[DESIGN_GAP_REVIEWED: BDD-16 fixture 缺陷已由后续 test-designer 修复轮解决]**——该缺陷未落在
implementer 自己修复，而是由主 Agent 派发 test-designer 定向修复轮处理（`P4-implementation.md`
第 50 行「主 Agent 独立复核记录」：*"主 Agent 诊断确认该 BDD-16 失败是 P3 测试设计遗留的 fixture
数据缺陷（非实现问题），已派 test-designer 角色定向修复（只改 `test_bdd_16_*` 函数 5 行，其余
34 个测试函数逐字节未变），复核后 35/35 转绿"*）。修复结果证据：`P6-evidence/md-field-set-tool/
bdd-16.log` 文件已核实存在（`ls` 确认）；`P6-acceptance.md` 第 51 行 PASS BDD-16 引用同一
证据文件（"零协议知识模拟调用序列按 `--list` 输出逐项 set 直至无缺失，最终 `--list` 无剩余缺失
且 `check-gate.py P2` 不再阻断"）；`P6.5-judge-verdict.md` 第 101 行独立复核同样 PASS BDD-16
并引用 `md-field-set-tool/bdd-16.log`。三方（P4 声明缺陷 → P6 证据转绿 → P6.5 独立复核 PASS）
形成完整闭环，无残留 BLOCKER。

## 2. SCOPE+ 闭环核对（BDD-30）

- **SCOPE+ 声明**：`P1-requirements.md` 第 262-263 行 `[SCOPE+ from P4]`：P4 阶段 SELF-GATE
  语义对齐审查（`docs/reviews/agate-alignment-review-2026-08-25-TAG0024.md` A4 项）独立实跑
  全量 pytest 发现 `test_check_pruning.py` 三个用例假失败，根因为 `check-pruning.py.
  _staged_source_count()` 读取真实外层仓库暂存区而非隔离 `task_dir` 自身仓库，经用户
  `[HUMAN_CONFIRMED]` 明确要求本任务内一并修复，新增第 6 项 issue（批次
  `check-pruning-isolation-fix`）与 BDD-30。
- **SCOPE_RESOLVED 标记**：`P1-requirements.md` 第 270 行
  `[SCOPE_RESOLVED: from docs/reviews/agate-alignment-review-2026-08-25-TAG0024.md]`，直接
  紧跟 BDD-30 之后，标记该 SCOPE+ 已纳入基线。
- **流转完整性核查**（逐阶段锚点，非仅"已通过"结论）：
  - P4：`P4-implementation.md` 第 36-40 行「第四批次」显式列出该批次改动文件
    （`dispatch-context.md`/`check-pruning.py`/`test_check_pruning.py`/`adr.md`），
    `P4-implementation-check-pruning-isolation-fix.md` 给出完整根因、diff、两轮修复过程与
    全仓回归证据（`1285 passed, 2 skipped in 146.88s`，0 failed）。
  - P6：`P6-acceptance.md` 第 65 行批次 `check-gate-debt-fixes` 下 `PASS BDD-30`，引用
    `P6-evidence/check-gate-debt-fixes/bdd-30-p2-6f.log` 与 `bdd-30-regression.log` 两个
    证据文件；第 24 行"三批次编号合集 = {1,...,30}"的统计口径已把 BDD-30 计入总数（19+6+5=30，
    其中 6 = check-gate-debt-fixes 批次 5 条常规 BDD + BDD-30）。
  - P6.5：`P6.5-judge-verdict.md` 第 115 行独立复核 PASS BDD-30，交叉核实
    `git diff check-pruning.py 两处 run_git() 补 cwd=task_dir`，`criteria_total`/
    `criteria_passed` 均含此条（30/30）。
  - 客观工具核验：`python3 agate/scripts/check-scope-resolved.py agate-workspace/tasks/
    TAG0024-toolchain-md-field-set` 本次实跑 **exit=0**（非仅采信 P4 自述的"已通过"）。
- **结论**：SCOPE+ 闭环完整，P1 声明 → P4 定向实现 → P6 证据 PASS → P6.5 独立复核 PASS →
  check-scope-resolved.py exit 0，五环节全部有锚点，无缺口。

## 3. CODE-MAP 核对结论

**先纠正 P4 的不准确表述**：`P4-implementation.md` 第 44 行称"本仓库未采用骨架或 CODE-MAP
机制，本节可省略新增文件核对表"——**该说法不准确**。本 agent 实际读取
`agate-workspace/agents/CODE-MAP.md`（94 行），确认该文件真实存在，且是本仓库（agate 协议
本体自身）TAG0007 起持续维护的活跃架构文档，文件开头即声明"P4 implementer 应更新本文件；
P7 consistency-reviewer 核对本文件记录与实际新增文件是否同步"——机制是采用的，P4 判断有误。

**实质核对**：`CODE-MAP.md`「模块」节「scripts」条目（第 23-30 行）把脚本分为 gate 族 /
一致性族 / 状态族 / 编排辅助脚本（`agate-inject-card.py`/`agate-render-dispatch-prompt.py`/
`agate-next-card.py`/`agate_common.py` 等）/ ceremony 路由族 / judge 机制族六类，用代表性
举例 + "等" 兜底，非逐文件穷举。本次新增的 `agate-md-field-set.py`/
`agate-md-field-set-gate-commands.py` 属于"任务产出文件字段读写 CLI"这一类，功能上与既有的
`agate-md-field-get.py`（读端，`agate/assets/execution-roles/*.md` 与 dispatch 模板广泛依赖）
是同一层的读/写两面。**关键实测**：`grep -n "md-field" agate-workspace/agents/CODE-MAP.md`
命中 0 次——已存在多年、被全流程依赖的 `agate-md-field-get.py` 本身也从未被
CODE-MAP.md 任何一类脚本族点名收录（既不在"编排辅助脚本"举例里，也不在其余四族），说明
"字段读写 CLI"这一类工具在 CODE-MAP.md 现有粒度下本就是系统性未点名的一类，不是本任务
新引入的记录缺口。

综合两点（六大脚本族均为代表性举例而非穷举 + 同类的既有 get 工具本身也未被点名），判定：

**[CODE_MAP_DRIFT: CODE-MAP.md「scripts」模块现有六族举例均未提及"任务产出文件字段读写 CLI"
这一类（get/set/set-gate-commands 三个工具），本次新增的 2 个脚本延续了这一既有未点名状态，
非本任务引入的新增偏离，但确实是一处可以让 CODE-MAP.md 更准确反映现状的缺口——建议后续
（不要求本任务内处理）在「scripts」节追加一句"字段读写 CLI（`agate-md-field-get.py`/
`agate-md-field-set.py`/`agate-md-field-set-gate-commands.py`）供 subagent 结构化读写任务
产出文件 frontmatter/gate_commands 正文块，供 phase-cards/execution-roles 引导使用"。
WARNING 级，不阻断本任务 gate。]**

不复述 P4 原话"机制未采用"，本判定明确为"机制已采用、六族举例非穷举、本次新增延续既有未
点名状态、建议后续补充"。

## 4. 跨文件一致性核对

### 4.1 BDD 总数 / pass 字段 / judge criteria 三方一致

- `P1-requirements.md`：`grep -c "^#### BDD-"` = **30**（BDD-1~30，含跨 issue 约束 BDD-29 与
  SCOPE+ 增补 BDD-30），已实核对（第 105-268 行逐条编号连续无跳号）。
- `P6-acceptance.md` frontmatter：`pass: 30`、`fail: 0`；正文第 24-28 行给出编号合集校验
  "三批次编号合集 = {1,2,...,29,30} = P1 全部 BDD-1~30，无重复、无遗漏（19+6+5=30）"。
- `P6.5-judge-verdict.md` frontmatter：`criteria_total: 30`、`criteria_passed: 30`；正文
  逐条列出 BDD-1~30 全部 PASS（第 86-115 行）。
- **三方一致**：30 = 30 = 30/30，且逐条 BDD 编号在三份文件中一一对应（未发现"数量对但内容
  错位映射"的情况——已抽查 BDD-16/BDD-29/BDD-30 三条在 P1 Given/When/Then、P6 PASS 描述、
  P6.5 复核描述三处的语义均精确对应同一验收点）。

### 4.2 packages 归属一致

`P2-design.md` frontmatter 声明 `packages: [agate-scripts, agate-rules, agate-docs,
agate-tests]`（与 `P1-requirements.md` frontmatter 一致）。实跑
`git diff --stat main..HEAD -- agate/scripts agate/rules agate/assets/templates agate/tests
agate/adr.md` 命中的全部 12 个改动文件：

```
agate/adr.md                                       → agate-docs
agate/assets/templates/dispatch-context.md         → agate-docs
agate/assets/templates/dispatch-prompt.md          → agate-docs
agate/rules/phases.yaml                            → agate-rules
agate/scripts/agate-md-field-set-gate-commands.py  → agate-scripts
agate/scripts/agate-md-field-set.py                → agate-scripts
agate/scripts/check-gate.py                        → agate-scripts
agate/scripts/check-pruning.py                     → agate-scripts
agate/tests/unit/test_agate_md_field_set.py        → agate-tests
agate/tests/unit/test_check_gate.py                → agate-tests
agate/tests/unit/test_check_pruning.py             → agate-tests
agate/tests/unit/test_check_structure_consistency.py → agate-tests
```

全部 12 个改动文件落在声明的 4 个 packages 内，无越界改动（无 frontend/domains 之外的文件）。

### 4.3 P4 实现路径与 P2 方案设计吻合

- `P2-design.md` §1.1「改什么」表格（第 29-41 行）声明的落点：`agate/scripts/
  agate-md-field-set.py`（新增）、`agate-md-field-set-gate-commands.py`（新增）、
  `check-gate.py._check_roadmap_done()`/`gate_p8()`、`phases.yaml`「P4 outputs」/「P6.5」块、
  `dispatch-prompt.md`/`dispatch-context.md`。
- `P4-implementation.md` 第 24-29 行「三批次改动分布」逐一对应：
  `agate-md-field-set.py`/`agate-md-field-set-gate-commands.py`（批次 md-field-set-tool）、
  `check-gate.py`（批次 check-gate-debt-fixes）、`phases.yaml`（批次 phases-yaml-consistency）、
  `dispatch-prompt.md`/`dispatch-context.md`（批次 md-field-set-tool，BDD-19）——逐文件
  路径与 P2 §1.1 表格逐字对应，无偏离。
- 具体函数级落点核实（BDD-29 关联）：实跑 `git diff main..HEAD -- agate/scripts/check-gate.py`
  确认改动仅为：新增 `_ROADMAP_EXPECTED_COLS = 9` 常量 + `_check_roadmap_done()` 内
  `len(cols) < 8` → `len(cols) != _ROADMAP_EXPECTED_COLS`（对应 P2 §3.6）+ `gate_p8()` 内
  `roadmap_path` 从相对 CWD 拼接改为 `_git(["rev-parse","--show-toplevel"])` 仓库根锚定
  + 非 git 环境 stderr 提示（对应 P2 §3.7）——与设计逐字节吻合，无额外改动。`git diff
  main..HEAD -- agate/scripts/check-events.py` 命中 0 行，确认 BDD-29"除 roadmap_path
  定位相关行外无其他判定逻辑变更"的验收标准成立。

### 4.4 dispatch_plan 4 批次零交叉核对

`P2-design.md` frontmatter 声明 `dispatch_plan: {mode: static-batch, parallel_limit: 3,
batches: [md-field-set-tool, check-gate-debt-fixes, phases-yaml-consistency]}`——**3 个并行
批次**，`P2-review.md` 已核验其文件零交叉（dispatch-context 已确认）。第 4 批
`check-pruning-isolation-fix` 是 P4 阶段因 SELF-GATE 语义对齐审查发现问题后，经用户
`[HUMAN_CONFIRMED]` 追加的**顺序执行批次**（时间上晚于前 3 批完成之后，非与之并行派发），
本 agent 逐批文件核对如下：

| 批次 | 改动文件 |
|---|---|
| md-field-set-tool | agate-md-field-set.py / agate-md-field-set-gate-commands.py / dispatch-prompt.md / dispatch-context.md / test_agate_md_field_set.py |
| check-gate-debt-fixes | check-gate.py / test_check_gate.py |
| phases-yaml-consistency | phases.yaml / test_check_structure_consistency.py |
| check-pruning-isolation-fix（第 4 批，顺序） | dispatch-context.md（二次修改） / check-pruning.py / test_check_pruning.py / adr.md |

- 前 3 批（并行派发）彼此之间：文件集合两两不相交，零交叉，与 P2-review.md 结论一致。
- 第 4 批与前 3 批之间：`check-pruning.py`/`test_check_pruning.py`/`adr.md` 三个文件不与前
  3 批任何文件重叠；唯一重叠点是 `dispatch-context.md`——批次 md-field-set-tool 首次写入
  "引导使用 set 工具"的指引（BDD-19），第 4 批对同一文件做**二次修正**（SELF-GATE 语义对齐
  审查 A1/A2 MISALIGNED：修复 FILE 调用语法从位置参数误写为 env var 语法）。这不构成"批次
  交叉"意义上的并发冲突——第 4 批在时间上严格晚于前 3 批全部完成并已提交之后才被发现问题
  并追加派发（P4-implementation.md 第 54-57 行"SELF-GATE 触发 protocol-alignment-review...
  独立实跑发现两处真实问题"的记录顺序确认了这一点），是对同一文件的**顺序纠错**而非**并行
  写冲突**。P2 candidate_count/dispatch_plan 声明的"零交叉"约束语义本身针对的是"3 个并行
  批次互不冲突"，未涵盖事后顺序追加的 SCOPE+ 批次，因此该顺序性重叠不违反 P2 设计约束，
  判定为一致。

## 5. 未决项清零确认

实跑 `grep -rn "\[BLOCKER\]\|\[DEVIATION-CRITICAL\]" agate-workspace/tasks/
TAG0024-toolchain-md-field-set/*.md` 与 `grep -rn "\[NEED_CONFIRM\]" 同目录`：

- 全部命中行核对后，**无一处是实际标记**——`[BLOCKER]`/`[DEVIATION-CRITICAL]` 的全部命中均
  出自 `P7-dispatch-context-consistency-reviewer.md` 本身（角色规则说明文字，非产出声明）。
- `[NEED_CONFIRM]` 的全部命中分两类：(a) 各阶段 dispatch-context 模板中的规则说明/模板占位
  文字（"若发现...写 [NEED_CONFIRM]"），(b) `P1-requirements.md`/`P1-review-progress.md`/
  `P1-progress.md` 中对"无 [NEED_CONFIRM]"这一结论的复述——`P1-requirements.md` 第 25 行、
  第 302 行实际标记均为 **`[NO_NEED_CONFIRM]`**，与角色红线"应只有 `[NO_NEED_CONFIRM]`"
  一致，无残留待确认阻塞项。
- 结论：全任务无残留 `[NEED_CONFIRM]`/`[BLOCKER]`/`[DEVIATION-CRITICAL]` 标记，未决项清零。

## 6. 结论

- BLOCKER = 0，DEVIATION-CRITICAL = 0（逐项跨文件核对均未发现偏离设计的实现问题）。
- DESIGN_GAP 1 条（BDD-16）已配对转抄 + `[DESIGN_GAP_REVIEWED]` + 引用 `P6-evidence/
  md-field-set-tool/bdd-16.log` 修复证据。
- SCOPE+（BDD-30）闭环完整，`check-scope-resolved.py` 实跑 exit 0。
- CODE-MAP 核对判定为 `[CODE_MAP_DRIFT]`（WARNING，不阻断），并已纠正 P4"机制未采用"的
  不准确表述。
- 跨文件一致性（BDD 总数/packages/实现路径/dispatch_plan 4 批次）逐项引用具体源文件节名
  核实一致，无裸"一致"结论。
- 未决项清零，P7 可放行推进 P8。
