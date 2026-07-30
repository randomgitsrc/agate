---
review_date: 2026-07-31
reviewer: protocol-alignment-review
change_summary: 阶段卡片措辞加固（P2.50）+ gate_commands.P3 自动读取测试运行器（P2.49），消灭模糊措辞，P2 review 不存在时 exit 1
files_changed:
  - agate/scripts/check-gate.sh
  - agate/scripts/check-tdd-red.sh
  - agate/tests/unit/check-gate.bats
  - agate/tests/unit/check-tdd-red.bats
  - agate/tests/helpers/fixtures.bash
  - agate/tests/integration/pre-commit-hook.bats
  - agate/phase-cards/P0-orchestrator.md
  - agate/phase-cards/P1-requirements.md
  - agate/phase-cards/P2-design.md
  - agate/phase-cards/P3-tdd.md
  - agate/phase-cards/P4-implementation.md
  - agate/phase-cards/P5-verification.md
  - agate/phase-cards/P6-acceptance.md
  - agate/phase-cards/P7-consistency.md
  - agate/phase-cards/P8-release.md
  - agate/dispatch-protocol.md
  - agate/assets/templates/dispatch-prompt.md
  - agate/assets/templates/task-files.md
  - agate/assets/execution-roles/architect.md
  - agate/assets/execution-roles/verifier.md
  - agate/assets/review-roles/plan-eng-review.md
  - agate/role-system.md
  - agate/rules/review-mapping.md
  - agate/state-machine.md
  - docs/hardening-roadmap.md
---

# 协议-脚本对齐审查

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | NEEDS_HUMAN_REVIEW |
| A4 | 测试覆盖 | ALIGNED |
| A5 | 下游影响 + 文档传播 | NEEDS_HUMAN_REVIEW |
| A6 | 锚点表覆盖 | ALIGNED |
| A7 | 设计原则一致性 | ALIGNED |

## 逐项审查

### A1: 文档→脚本对齐

**A1a: P2-review.md 不存在时 exit 1**

**文档声明**（P2-design.md:104）：
> P2-review.md 存在且 status: approved（agent≠main）— 不存在 → gate exit 1

**脚本实现**（check-gate.sh:101-103）：
```bash
if [ ! -f "$P2_REVIEW" ]; then
    echo "GATE P2: P2-review.md 不存在（P2 评审不可裁剪，必须派发独立 subagent 产出）" >&2
    exit 1
fi
```

**结论**：ALIGNED
**说明**：原逻辑是文件存在时才检查 status/agent，不存在时跳过整个 review 检查（exit 2）。修复后不存在直接 exit 1，与文档"P2 评审不可裁剪"语义一致。state-machine.md:85 转移规则也要求 `P2-review.md 有效 AND status==approved AND agent≠main`，与脚本一致。

---

**A1b: gate_commands.P3 自动读取**

**文档声明**（P3-tdd.md:50）：
> 测试运行器探测链：`$TEST_RUNNER` 环境变量 → `gate_commands.P3`（P2-design.md 声明）→ `which pytest` → exit 3

**脚本实现**（check-tdd-red.sh:64-94）：
```bash
if [ -n "${TEST_RUNNER:-}" ]; then
    RUNNER="$TEST_RUNNER"
elif [ -n "${TASK_DIR:-}" ] && [ -f "$TASK_DIR/P2-design.md" ]; then
    P3_CMD=$(GATE_FILE="$TASK_DIR/P2-design.md" python3 -c '...' 2>/dev/null || true)
    if [ -n "$P3_CMD" ]; then
        RUNNER="$P3_CMD"
    elif command -v pytest &>/dev/null; then
        RUNNER="pytest"
    else
        echo "TDD_CHECK: no test runner found..." >&2
        exit 3
    fi
elif command -v pytest &>/dev/null; then
    RUNNER="pytest"
else
    echo "TDD_CHECK: no test runner found..." >&2
    exit 3
fi
```

**结论**：ALIGNED
**说明**：探测链顺序（TEST_RUNNER → gate_commands.P3 → pytest → exit 3）与文档完全一致。check-gate.sh:140 调用时 `exec "$SCRIPT_DIR/check-tdd-red.sh" "$TASK_DIR"`，传递 TASK_DIR 位置参数。

---

**A1c: P0 四字段（移除 pruning_tendency）**

**文档声明**（P0-orchestrator.md:11, 27）：
> P0-brief.md 四字段 ... 四字段是 agate 要求的最小集

**脚本实现**（check-gate.sh:39）：
```bash
echo "GATE P0: 立项阶段无需脚本 gate（仅 P0-brief.md）。主 Agent 确认 P0-brief 四字段齐全即可推进 P1。" >&2
```

**结论**：ALIGNED
**说明**：P0 gate 是 exit 2（主 Agent 自判），不检查字段数量。提示文本已同步更新为"四字段"。state-machine.md:76 转移规则也改为"四字段自查通过"。

---

**A1d: minimal_validation 强制声明**

**文档声明**（P2-design.md:47）：
> minimal_validation：验证结果 或 声明"纯代码逻辑，无外部系统依赖"（声明时须附理由）

**脚本实现**：check-gate.sh P2 分支不检查 minimal_validation 字段（exit 2，主 Agent 自判）。

**结论**：ALIGNED
**说明**：minimal_validation 是语义判断（内容是否实质），不可脚本化。文档措辞从"若方案依赖外部行为"改为强制声明，与 plan-eng-review.md:22 检查项一致。

---

**A1e: "可选"/"若有触发"/"nudge" 等模糊措辞消灭**

**文档声明**：所有阶段卡片推进条件改为 AND checklist，"可选"改为"条件触发"。

**脚本验证**：
```bash
grep -rn '若方案依赖\|若.*可选\|若有触发\|可以考虑' agate/phase-cards/*.md
# No ambiguous wording found

grep -rn '可选.*并行\|并行.*可选' agate/phase-cards/*.md
# All changed
```

**结论**：ALIGNED

---

### A2: 脚本→文档对齐

**A2a: check-gate.sh P3 exec 传 $TASK_DIR**

**脚本实现**（check-gate.sh:140）：
```bash
exec "$SCRIPT_DIR/check-tdd-red.sh" "$TASK_DIR" ;;
```

**文档声明**（P3-tdd.md:42）：
```bash
check-tdd-red.sh $TASK_DIR
```

**结论**：ALIGNED

---

**A2b: check-tdd-red.sh 探测链文档化**

**脚本实现**（check-tdd-red.sh:33）：
```
# 测试运行器探测链：$TEST_RUNNER → gate_commands.P3（P2-design.md）→ which pytest → exit 3
```

**文档声明**：
- P3-tdd.md:50 — 完整探测链描述
- state-machine.md:290 — 探测链 + 环境变量说明
- architect.md:47 — P3 键说明
- verifier.md:158 — 非 pytest 技术栈引用
- task-files.md:215-217 — P3 键说明
- P5-verification.md:39 — 非 pytest 技术栈引用

**结论**：ALIGNED
**说明**：脚本探测链在 6 处文档中同步记录，措辞一致。

---

**A2c: check-gate.sh P0 提示文本**

**脚本实现**（check-gate.sh:39）：
```
主 Agent 确认 P0-brief 四字段齐全即可推进 P1
```

**文档声明**：P0-orchestrator.md:11, P1-requirements.md:27, state-machine.md:76, dispatch-protocol.md:203, rules/state-transitions.md:15 — 均写"四字段"

**结论**：ALIGNED

---

### A3: 一致性连锁 + 反向传播

#### A3a: 连锁（已知的衍生改动）

**P0 删除 pruning_tendency → 传播链**：
- P0-orchestrator.md ✅（五→四字段）
- P1-requirements.md ✅（前置条件改四字段）
- state-machine.md ✅（转移规则改四字段）
- dispatch-protocol.md ✅（自查改四字段，删除 pruning_tendency 行）
- task-files.md ✅（P0 文件清单删除，模板删除）
- architect.md ✅（输入节删除"裁剪倾向"）
- rules/state-transitions.md ✅（P0→P1 条件改四字段）

**结论**：ALIGNED — 所有已知的衍生改动已完成。

---

**gate_commands.P3 新增 → 传播链**：
- P2-design.md ✅（gate_commands 声明节 + gate 规则 + 推进条件）
- P3-tdd.md ✅（探测链文档化 + gate 命令示例）
- architect.md ✅（输出字段 + P3 键说明）
- task-files.md ✅（P2 模板 gate_commands 节）
- verifier.md ✅（非 pytest 技术栈引用）
- P5-verification.md ✅（非 pytest 技术栈引用）
- state-machine.md ✅（check-tdd-red.sh 设计块）
- check-tdd-red.sh ✅（脚本实现）
- check-gate.sh ✅（注释 + exec 传参）

**结论**：ALIGNED — gate_commands.P3 在所有相关文件中同步。

---

**minimal_validation 强制声明 → 传播链**：
- P2-design.md ✅（产出规格 + 派发追加）
- architect.md ✅（输出字段说明）
- task-files.md ✅（P2 模板 §5）
- dispatch-prompt.md ✅（P2 派发追加）
- dispatch-protocol.md ✅（P2 派发追加 + P2 最小验证节）
- plan-eng-review.md ✅（评审重点）

**结论**：ALIGNED — 6 处文档同步更新，措辞一致。

---

**office-hours 触发条件改 → 传播链**：
- P2-design.md:72 ✅（"P1-requirements.md 含 [NEED_CONFIRM] 且涉及业务方向"）
- role-system.md:62 ✅（同上）
- review-mapping.md:23 ✅（同上）
- dispatch-protocol.md:988 ✅（"大任务时"）

**结论**：ALIGNED — 4 处文档同步更新。

---

**"亲自执行"定义统一 → 传播链**：
- P4-implementation.md:50 ✅（"P5 由主 Agent 派发 verifier subagent 执行 gate_commands.P5，主 Agent 验 gate"）
- dispatch-protocol.md:516 ✅（"P5 由主 Agent 派发 verifier subagent 从 P2-design.md 读取 gate_commands.P5 并执行，主 Agent 验 gate"）
- dispatch-prompt.md:99-100 ✅（简化版"自查≠P5 gate"，不含 verifier subagent 细节——模板简化是设计选择）
- P6-acceptance.md:131 ✅（"P6 gate 由主 Agent 亲自跑 gate 脚本"）

**结论**：ALIGNED — 区分了"派 subagent 执行"（P5）和"主 Agent 跑 gate 脚本"（P6），措辞在各自上下文中准确。

---

#### A3b: 反向传播（主动推断的应被影响文件）

| 文件 | 应被影响的原因 | 实际状态 | 结论 |
|------|--------------|---------|------|
| agate/orchestrator-template.md | P0 四字段 / pruning_tendency 引用 | 无引用（已检查） | ALIGNED |
| agate/LIMITATIONS.md | pruning_tendency 引用 | 无引用（已检查） | ALIGNED |
| agate/CONTEXT.md | pruning_tendency / 四字段术语 | 无引用（已检查） | ALIGNED |
| agate/assets/execution-roles/analyst.md | "裁剪倾向"描述 | 无引用（已检查） | ALIGNED |
| agate/assets/execution-roles/implementer.md | pruning_tendency 引用 | 无引用（已检查） | ALIGNED |
| agate/assets/execution-roles/test-designer.md | pruning_tendency 引用 | 无引用（已检查） | ALIGNED |
| agate/rules/state-transitions.md | P0→P1 条件 / P2 不可裁 | 已更新四字段（line 15） | ALIGNED |
| WORKFLOW.md | P0 门槛描述 | 仍写"含 debug_env + known_risks"（line 216） | ALIGNED（语义可接受——debug_env 是 env_constraints 子字段，known_risks 是四字段之一，未用"五字段"术语） |
| dispatch-protocol.md:200 | phase_hint 缩进 | 4 空格，周围 YAML 键 3 空格 | NEEDS_HUMAN_REVIEW |
| CHANGELOG.md | P2.49/P2.50 变更条目 | 仅有 pruning_tendency 移除条目，无 P2.49/P2.50 | NEEDS_HUMAN_REVIEW |

**dispatch-protocol.md:200 缩进问题**：

```yaml
   env_constraints:
     debug_env: {...}
     # 不写 prod_env...
    phase_hint: [P1, P2, ..., P8]  # ← 4 空格，应为 3 空格
   ```
```

原版 `pruning_tendency` 和 `phase_hint` 都在 3 空格缩进。删除 `pruning_tendency` 行时，`phase_hint` 的缩进从 3 改为 4。这是 Markdown 代码块内的示例 YAML，不被任何脚本解析，纯属 cosmetic 问题。

**CHANGELOG 遗漏**：

CHANGELOG.md `[Unreleased]` 节有 pruning_tendency 移除条目，但缺少：
- P2.49: gate_commands.P3 新增（check-tdd-red.sh 自动读取测试运行器）
- P2.50: 阶段卡片措辞加固（AND checklist / 消灭模糊措辞 / P2 review exit 1 / design_trivial 须附理由 / 基础设施隔离"必须"）

这两个变更是 v0.25.0 的核心内容，应在 CHANGELOG 中记录。

---

### A4: 测试覆盖

**bats 全量实跑结果**：

```
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
476 tests passed, 0 failed
```

**新增测试覆盖**：

| 测试 | 覆盖的变更 | 边界 |
|------|----------|------|
| check-gate.bats G2.13 | P2-review 不存在 → exit 1（原 exit 2） | 改了期望 exit code |
| check-gate.bats PG.P2REVIEW | P2-review 不存在 → exit 1 + 错误消息 | 新增用例 |
| check-tdd-red.bats TDD.G1 | gate_commands.P3 自动读取 | 正向：P3 键存在 → 自动读取 |
| check-tdd-red.bats TDD.G2 | 无 P3 键 → TEST_RUNNER 向后兼容 | 回退：P3 不存在不破坏 |
| check-tdd-red.bats TDD.G3 | TEST_RUNNER 优先于 gate_commands.P3 | 优先级：环境变量 > P3 键 |
| check-tdd-red.bats TDD.G4 | 无 TASK_DIR → 跳过 P3 读取 | 回退：无 TASK_DIR 不崩溃 |
| check-tdd-red.bats TDD.G5 | P3 双引号值 → strip quotes | 边界：引号处理 |
| fixtures.bash add_p2_review | P2-review.md fixture helper | 所有 P2 gate 测试使用 |
| pre-commit-hook.bats | P2-review.md fixture in integration | 集成测试同步 |

**结论**：ALIGNED
**说明**：5 个新 TDD.G 测试覆盖了 gate_commands.P3 的正常路径、回退路径、优先级和边界。P2 review exit 1 有 2 个测试覆盖（改期望 + 新增）。所有现有 P2 gate 测试已通过 `add_p2_review` 适配。476 tests 全部通过。

---

### A5: 下游影响 + 文档传播

**破坏性变更**：

1. **P2-review.md 不存在 → exit 1（原 exit 2）**：破坏性变更。原有项目如果在 P2 阶段没有 P2-review.md 就 commit（利用 exit 2 跳过），现在会被 exit 1 拦截。但 P2 评审本就不可裁剪（state-machine.md:169），语义上 review 文件必须存在。此变更是 bug fix（修复"文件不存在时跳过检查"的逻辑漏洞），不违反协议语义。

2. **pruning_tendency 移除**：已在之前的 review（agate-alignment-review-20260726.md）中确认无破坏性影响。P0 gate 是 exit 2，不检查字段。

3. **gate_commands.P3 新增**：可选键，向后兼容。不声明 P3 键的现有项目行为不变。

**文档传播**：

| 应被影响的文档 | 实际状态 | 结论 |
|--------------|---------|------|
| hardening-roadmap.md v0.25.0 节 | ✅ 已记录 P2.49 + P2.50 | ALIGNED |
| CHANGELOG.md [Unreleased] | ❌ 缺 P2.49/P2.50 条目 | NEEDS_HUMAN_REVIEW |
| SELF-GATE.md | 无需改动（不涉及触发文件变化） | ALIGNED |

**结论**：NEEDS_HUMAN_REVIEW
**差异**：CHANGELOG.md `[Unreleased]` 节缺少 P2.49（gate_commands.P3）和 P2.50（措辞加固）的变更条目。建议在 commit 前补充。
**建议**：在 CHANGELOG.md `[Unreleased]` 节新增：
```markdown
- **gate_commands.P3**：新增可选 P3 键（测试运行器），check-tdd-red.sh 自动读取，探测链扩展为 TEST_RUNNER → gate_commands.P3 → pytest → exit 3
- **阶段卡片措辞加固**：推进条件改为 AND checklist，消灭"可选"/"nudge"等模糊措辞，P2 review 不存在时 exit 1（bug fix），design_trivial 须附理由，minimal_validation 强制声明，基础设施隔离"必须"
```

---

### A6: 锚点表覆盖

**CHECK 9 锚点表检查**（check-protocol-consistency.py）：

| 新增/变更的规则 | 是否有对应锚点 | 说明 |
|--------------|-------------|------|
| gate_commands.P3 自动读取 | 无专门锚点 | 现有"TDD 红灯检查"锚点检查 check-tdd-red.sh 含 `"pytest"` 关键词，仍通过。P3 键是可选功能，非协议硬约束，不需要专门锚点。 |
| P2 review 不存在 → exit 1 | 无专门锚点 | "P2 agent=main 硬拦截"锚点仍覆盖 check-gate.sh P2 分支。exit 1 vs exit 2 是行为变更，锚点只检查关键词存在性，不检查 exit code 语义。 |
| P0 四字段 | 无专门锚点 | P0 gate 是 exit 2（主 Agent 自判），不检查字段。锚点表不覆盖 P0。 |
| minimal_validation 强制声明 | 无专门锚点 | 语义判断，不可脚本化。plan-eng-review 角色检查，非 gate 脚本检查。 |

**consistency checker 实跑结果**：
```
python3 agate/scripts/check-protocol-consistency.py
仅有 12 个 WARNING，无 ERROR。
```

**结论**：ALIGNED
**说明**：新增的 gate_commands.P3 和措辞加固变更不需要新增 CHECK 9 锚点。这些变更要么是可选功能（P3 键），要么是语义层面的措辞改进（AND checklist），不涉及新的脚本关键词检查。现有锚点仍全部通过。

---

### A7: 设计原则一致性

**ADR-001（隔离性——主 Agent 不写产出）**：

P4 自查节从"P5 由主 Agent 亲自执行 P2-design.md 的 gate_commands"改为"P5 由主 Agent 派发 verifier subagent 执行 gate_commands.P5，主 Agent 验 gate"。这更符合 ADR-001——主 Agent 只编排不执行，测试运行由 verifier subagent 在独立上下文完成。

**结论**：ALIGNED

---

**ADR-002（可判定性——gate 门槛机器可判定）**：

P2-review.md 不存在 → exit 1 是可判定的硬门槛（文件存在性检查）。推进条件改为 AND checklist 使门槛更明确，减少主 Agent 主观判断空间。

**结论**：ALIGNED

---

**ADR-003（最小约定——不绑定技术栈）**：

gate_commands.P3 新增增强了技术栈无关性——非 pytest 项目现在可以在 P2 声明测试运行器命令，无需依赖 TEST_RUNNER 环境变量手动覆盖。探测链的设计（环境变量 > P3 键 > pytest > exit 3）保证了向后兼容。

**结论**：ALIGNED

---

**ADR-005（改动性质判断）**：

pruning_tendency 移除消除了与 P1 risk_level 的功能重叠。P0 阶段无足够信息判断裁剪倾向（裁剪决策在 P1 做基于 risk_level），移除是正确的。

**结论**：ALIGNED

---

## 人工确认项

### NEEDS_HUMAN_REVIEW #1: dispatch-protocol.md:200 phase_hint 缩进

**位置**：agate/dispatch-protocol.md:200
**问题**：`phase_hint` 行缩进为 4 空格，周围 YAML 键为 3 空格。删除 `pruning_tendency` 行时引入。
**影响**：无功能影响（Markdown 代码块内示例，不被脚本解析）。纯 cosmetic。
**建议**：将 `    phase_hint` 改为 `   phase_hint`（3 空格，与 `env_constraints` 对齐）。

`[HUMAN_CONFIRMED: 待确认]`

---

### NEEDS_HUMAN_REVIEW #2: CHANGELOG.md 遗漏 P2.49/P2.50 条目

**位置**：CHANGELOG.md `[Unreleased]` 节
**问题**：仅有 pruning_tendency 移除条目，缺少 P2.49（gate_commands.P3）和 P2.50（措辞加固）的变更记录。
**影响**：协议语义变更未在 CHANGELOG 标注，A5 下游影响不完整。
**建议**：在 `[Unreleased]` 节补充 P2.49 和 P2.50 的变更条目。

`[HUMAN_CONFIRMED: 待确认]`

---

## 留痕文件

原始审查痕迹见：`docs/reviews/agate-alignment-20260731-01.progress.md`
