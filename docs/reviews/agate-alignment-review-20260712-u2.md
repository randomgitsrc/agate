---
review_date: 2026-07-12
reviewer: protocol-alignment-review
change_summary: U2: P5/P7/P8 subagent化, N3⑨ consistency-reviewer实质锚点, N5 P5 commit→push窗口风险标注
files_changed:
  - agate/WORKFLOW.md
  - agate/assets/execution-roles/consistency-reviewer.md
  - agate/assets/execution-roles/verifier.md
  - agate/dispatch-protocol.md
  - agate/orchestrator-template.md
  - agate/phase-cards/P5-verification.md
  - agate/phase-cards/P7-consistency.md
  - agate/phase-cards/P8-release.md
  - agate/scripts/check-protocol-consistency.py
  - agate/state-machine.md
---

# 协议-脚本对齐审查

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | MISALIGNED |
| A2 | 脚本→文档对齐 | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | ALIGNED |
| A4 | 测试覆盖 | ALIGNED |
| A5 | 下游影响 + 文档传播 | ALIGNED |
| A6 | 锚点表覆盖 | MISALIGNED |

## 逐项审查

### A1: 文档→脚本对齐

#### A1.1: dispatch-protocol.md 角色映射

**文档声明**（dispatch-protocol.md:223）：
> P1→analyst, P2→architect, P3→test-designer, P4→implementer, P5→verifier, P7→consistency-reviewer, P8→implementer(P8模式)

**结论**：ALIGNED — P7→consistency-reviewer, P8→implementer(P8模式) 映射行存在且正确。

#### A1.2: P5-verification.md "verifier subagent" → dispatch-protocol.md + verifier.md 确认

**文档声明**（P5-verification.md:9）：
> 主 Agent 派发 verifier subagent（P5 模式）执行 gate_commands.P5

**dispatch-protocol.md**（:394）：
> P5 由主 Agent 派发 verifier subagent 执行

**verifier.md**（:48-52）：
> P5 subagent 化说明：P5 由主 Agent 派发 verifier subagent 执行

**结论**：ALIGNED — 三处一致。

#### A1.3: P7-consistency.md "consistency-reviewer subagent" → consistency-reviewer.md 匹配

**文档声明**（P7-consistency.md:9）：
> 主 Agent 派发 consistency-reviewer subagent 执行交叉检查

**consistency-reviewer.md**（:2-6）：
> role_id: consistency-reviewer, phases: [P7], mode: 一致性交叉检查

**结论**：ALIGNED — role_id 匹配，phases 匹配。

#### A1.4: P8-release.md "releaser subagent" → dispatch-protocol.md 确认

**文档声明**（P8-release.md:9）：
> 主 Agent 派发 releaser subagent（implementer P8 模式）执行发布准备

**dispatch-protocol.md**（:223）：
> P8→implementer(P8模式)

**结论**：ALIGNED — P8 用 implementer P8 模式，P8-release.md 称 "releaser subagent（implementer P8 模式）"语义一致。

#### A1.5: WORKFLOW.md P7 行 "consistency-reviewer（subagent 派发）" → P7-consistency.md

**文档声明**（WORKFLOW.md:199）：
> P7 | 一致性检查 | consistency-reviewer（subagent 派发）

**P7-consistency.md**（:5）：
> ⑨ P7 subagent 化

**结论**：ALIGNED。

#### A1.6: WORKFLOW.md P5 行 "N5 最小校验" → P5-verification.md N5 节

**文档声明**（WORKFLOW.md:197）：
> P5 | 技术验证 | verifier（P5 模式，subagent 派发）| gate 自检 + N5 最小校验（test runner 输出签名）

**P5-verification.md**（:72-82）：
> P5 commit→push 窗口残余风险（N5）…grep -cE '^(PASSED|FAILED|passed|failed|ok|not ok)' P5-test-results/unit.md

**结论**：ALIGNED — N5 节存在且描述匹配。

#### A1.7: state-machine.md ⑨ annotations for P5/P7/P8

**文档声明**：
- P5 ⑨: state-machine.md:108 — `⑨ P5 subagent 化：verifier subagent 从 P2-design.md gate_commands.P5 读取命令执行，主 Agent 验 gate + N5 最小校验`
- P7 ⑨: state-machine.md:127 — `⑨ P7 subagent 化：consistency-reviewer subagent 执行交叉检查，N3⑨ 实质锚点校验`
- P8 ⑨: state-machine.md:132 — `⑨ P8 subagent 化：releaser subagent 执行发布准备，主 Agent 仍亲自做 READY 收尾`

**结论**：ALIGNED — 三个 ⑨ 注解全部存在。

#### A1.8: N5 window risk — P5-verification.md vs dispatch-protocol.md

**P5-verification.md**（:72-82）：
> 残余风险：verifier subagent 产出 P5-test-results/ 后…伪造的 P5-test-results 可在此窗口内流向下游。缓解：grep -cE '^(PASSED|FAILED|passed|failed|ok|not ok)' P5-test-results/unit.md

**dispatch-protocol.md**（:626, P5→P6 门槛）：
> N5 最小校验（grep -cE '^(PASSED|FAILED|passed|failed|ok|not ok)' P5-test-results/unit.md → 计数 >0）

**结论**：ALIGNED — 两处描述的 grep 命令和语义一致。

#### A1.9: N3⑨ — P7-consistency.md anchor requirements vs consistency-reviewer.md

**P7-consistency.md**（:32-38）：
> 实质锚点要求（N3⑨）：BLOCKER=0 → DESIGN_GAP 配对项 + REVIEWED 标记; CRITICAL=0 → 跨文件检查项 + 源文件节名; SCOPE+ 闭环 → 条目 + SCOPE_RESOLVED

**consistency-reviewer.md**（:30-38）：
> 实质锚点要求（N3）：BLOCKER=0 → 逐条 DESIGN_GAP 配对项 + [DESIGN_GAP_REVIEWED:] 标记; CRITICAL=0 → 跨文件检查项 + 引用源文件节名; SCOPE+ 闭环 → 列出 SCOPE+ 条目 + 对应 [SCOPE_RESOLVED]

**结论**：ALIGNED — 两处锚点要求语义一致。

#### A1.10: P7 input file exception in dispatch-protocol.md → P7-consistency.md

**dispatch-protocol.md**（:474）：
> P7 例外：一致性检查天然需要跨文件对照，不受输入文件数限制。consistency-reviewer 角色文件明确列出输入文件和关注点

**P7-consistency.md**（:68-73）：
> P7 输入文件数量：P7 是输入文件数量限制的例外，不拆分

**结论**：ALIGNED。

#### A1.11: CHECK 9 anchor for consistency-reviewer → check-protocol-consistency.py

**check-protocol-consistency.py**（:539-543, U2 新增）：
```python
{
    "desc": "P7 consistency-reviewer 实质锚点",
    "script": "agate/scripts/check-gate.sh",
    "keywords": ["DESIGN_GAP_REVIEWED"],
},
```

**check-gate.sh**（:122）：
> DESIGN_GAP_REVIEWED=$(grep -cE '\[DESIGN_GAP_REVIEWED' "$P7_FILE" 2>/dev/null || echo 0)

**结论**：ALIGNED — CHECK 9 锚点关键词 `DESIGN_GAP_REVIEWED` 在 check-gate.sh 中存在。

#### A1.12: P7 跨文件引用 WARNING — 文档声明 vs 脚本实现

**consistency-reviewer.md**（:40）：
> gate 脚本校验：check-gate.sh P7 检查——P7-consistency.md 含 DESIGN_GAP_REVIEWED 标记时，须同时含跨文件引用关键词（`P1.*BDD\|P2.*packages\|P4.*implementation`），不含则 WARNING。

**P7-consistency.md**（:58）：
> 含 DESIGN_GAP_REVIEWED 但缺跨文件引用关键词 → WARNING（不改变 exit code）

**check-gate.sh P7 段**（:108-139）：无此 WARNING 检查。P7 段只检查 BLOCKER/DEVIATION-CRITICAL/DESIGN_GAP 配对/P4 交叉核对，**没有**跨文件引用关键词 WARNING。

**结论**：**MISALIGNED** — consistency-reviewer.md:40 和 P7-consistency.md:58 声明 check-gate.sh P7 应在含 DESIGN_GAP_REVIEWED 但缺跨文件引用关键词时发 WARNING，但 check-gate.sh 未实现此检查。

**差异**：文档声明了 P7 跨文件引用关键词 WARNING（`P1.*BDD|P2.*packages|P4.*implementation`），脚本未实现。

**建议**：在 check-gate.sh P7 段（:139 `exit 0` 之前）添加跨文件引用关键词 WARNING 检查，或在文档中标注此检查为"待实现"。

### A2: 脚本→文档对齐

#### A2.1: U2 是否引入了未文档化的新脚本行为？

U2 diff 中唯一的脚本变更是 check-protocol-consistency.py 新增 CHECK 9 锚点条目（P7 consistency-reviewer 实质锚点），这是文档驱动的变更，已由 A1.11 确认对齐。

**结论**：ALIGNED — 无未文档化的新脚本行为。

#### A2.2: check-gate.sh P7 WARNING 是否与 P7-consistency.md 描述一致？

check-gate.sh P7 段的 WARNING 行为：无 WARNING 输出（只有 exit 1 的硬拦截）。

P7-consistency.md:58 描述的 WARNING：含 DESIGN_GAP_REVIEWED 但缺跨文件引用关键词 → WARNING。

**结论**：同 A1.12，MISALIGNED。

### A3: 一致性连锁 + 反向传播

#### A3a: 已知衍生改动（应被影响且已在 diff 中的文件）

| 文件 | 应被影响原因 | 在 diff 中？ | 影响到位？ |
|------|------------|------------|----------|
| consistency-reviewer.md | N3⑨ 新角色文件 | ✅ | ✅ 新文件，含实质锚点要求 |
| P5-verification.md | P5 subagent化 + N5 | ✅ | ✅ 含⑨注解 + N5 节 |
| P7-consistency.md | P7 subagent化 + N3⑨ | ✅ | ✅ 含⑨注解 + 实质锚点表 |
| P8-release.md | P8 subagent化 | ✅ | ✅ 含⑨注解 + releaser 交接 |
| verifier.md | P5 subagent化说明 | ✅ | ✅ 含 P5 subagent 化说明节 |
| dispatch-protocol.md | 角色映射 + P5 描述 + P7 例外 + N5 + P5 gate 验证方式 | ✅ | ✅ |
| WORKFLOW.md | P5/P7/P8 行 + 角色目录 | ✅ | ✅ P5 行含 N5, P7 行含 consistency-reviewer, P8 行含 releaser, 目录含 consistency-reviewer.md |
| state-machine.md | ⑨ annotations | ✅ | ✅ P5/P7/P8 三处⑨注解 |
| orchestrator-template.md | READY handoff | ✅ | ✅ P8 gate 通过后执行 READY 收尾检查 |
| check-protocol-consistency.py | CHECK 9 anchor | ✅ | ✅ 新增 P7 consistency-reviewer 锚点 |

#### A3b: 反向传播（应被影响但未在 diff 中的文件）

| 文件 | 是否应被影响？ | 理由 |
|------|------------|------|
| implementer.md | 否 | P8 用 implementer P8 模式，但 implementer.md 已有 P8 模式描述（非 U2 新增） |
| role-system.md | 否 | U2 不改变角色体系结构 |
| LIMITATIONS.md | 否 | U2 不新增已知局限 |
| CHANGELOG.md | 否 | 协议语义变更，但 U2 是分支未合并，CHANGELOG 在发布时更新 |

**结论**：ALIGNED — 所有应被影响的文件均在 diff 中，无遗漏，无多余。

### A4: 测试覆盖

#### A4.1: bats 全量实跑

```
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
248 tests, all passed
```

#### A4.2: U2 是否引入需要测试的新 gate 逻辑？

U2 唯一的脚本变更是 check-protocol-consistency.py 新增 CHECK 9 锚点条目。此条目被现有 CON.8 测试覆盖（SG.6 验证锚点表覆盖全部 gate 脚本）。

P7 跨文件引用 WARNING（A1.12 发现的 MISALIGNED 项）尚未实现，因此暂无对应测试——但这是缺陷，不是"不需要测试"。

**结论**：ALIGNED — 现有测试覆盖 U2 的脚本变更，无回归。

### A5: 下游影响 + 文档传播

#### A5.1: P5 subagent化是否改变 P6 dispatch？

verifier.md 已有 P5/P6 双模式（:4-8），P5 subagent化不改变 P6 派发方式。P6 仍派发 verifier（验收模式）。

**结论**：无影响。

#### A5.2: P7 subagent化是否改变 P7 gate 行为（exit codes）？

P7 gate exit codes 未变：BLOCKER/DEVIATION-CRITICAL → exit 1, DESIGN_GAP 未配对 → exit 1, 全通过 → exit 0。subagent化改变的是执行者（从主 Agent 变为 consistency-reviewer subagent），不改变 gate 判定逻辑。

**结论**：无影响。

#### A5.3: P8 subagent化是否改变 P8 gate 行为？

P8 gate exit codes 未变：部分脚本化 → exit 2, 缺字段 → exit 1。subagent化改变的是执行者（从主 Agent 变为 releaser subagent），主 Agent 仍亲自做 READY 收尾。

**结论**：无影响。

### A6: 锚点表覆盖

#### A6.1: CHECK 9 是否覆盖 consistency-reviewer 锚点？

check-protocol-consistency.py:539-543 新增锚点：
```python
{
    "desc": "P7 consistency-reviewer 实质锚点",
    "script": "agate/scripts/check-gate.sh",
    "keywords": ["DESIGN_GAP_REVIEWED"],
}
```

**结论**：ALIGNED — 锚点已覆盖。

#### A6.2: 跨文件引用关键词 WARNING 是否需要锚点？

consistency-reviewer.md:40 和 P7-consistency.md:58 声明的跨文件引用关键词 WARNING（`P1.*BDD|P2.*packages|P4.*implementation`）在 check-gate.sh 中未实现。如果实现，应在 CHECK 9 锚点表中新增对应条目。

当前状态：文档声明了此检查，但脚本未实现，锚点表自然也没有对应条目。

**结论**：**MISALIGNED** — 与 A1.12 同一问题。文档声明的 P7 跨文件引用 WARNING 在脚本和锚点表中均缺失。

---

## MISALIGNED 项汇总

| # | 问题 | 严重度 | 修复方向 |
|---|------|--------|---------|
| A1.12/A2.2/A6.2 | consistency-reviewer.md:40 和 P7-consistency.md:58 声明 check-gate.sh P7 应在含 DESIGN_GAP_REVIEWED 但缺跨文件引用关键词时发 WARNING，但 check-gate.sh 未实现此检查 | 中 | 在 check-gate.sh P7 段 exit 0 前添加 WARNING 检查，或在文档中标注"待实现" |

## 人工验收清单

- [x] 审查报告含 A1-A6 六项，每项有结论
- [x] MISALIGNED 项有差异描述 + 建议方向
- [ ] 每条 NEEDS_HUMAN_REVIEW 下面有 `[HUMAN_CONFIRMED: ...]` 标记（无 NEEDS_HUMAN_REVIEW 项）
- [x] 审查报告落盘到 `docs/reviews/agate-alignment-review-{date}.md`
