---
review_date: 2026-07-26
reviewer: protocol-alignment-review
change_summary: 移除 P0-brief 的 pruning_tendency 字段（五字段→四字段），简化 office-hours 触发条件
files_changed: [agate/WORKFLOW.md, agate/assets/templates/active-tasks-template.md, agate/assets/templates/task-files.md, agate/dispatch-protocol.md, agate/phase-cards/P0-orchestrator.md, agate/phase-cards/P1-requirements.md, agate/rules/state-transitions.md, agate/scripts/check-gate.sh, agate/state-machine.md, docs/hardening-roadmap.md]
---

# 协议-脚本对齐审查

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | MISALIGNED |
| A4 | 测试覆盖 | ALIGNED |
| A5 | 下游影响 + 文档传播 | MISALIGNED |
| A6 | 锚点表覆盖 | ALIGNED |
| A7 | 设计原则一致性 | ALIGNED |

## 逐项审查

### A1: 文档→脚本对齐

**文档声明**（state-machine.md:76）：
> P0 --[P0-brief.md 完成，四字段自查通过（task/known_risks/executor_env/env_constraints）]--> P1

**文档声明**（dispatch-protocol.md:203）：
> P0-brief 完成后，主 Agent 自查四个必填字段是否有实质内容

**脚本实现**（check-gate.sh:39）：
> echo "GATE P0: 立项阶段无需脚本 gate（仅 P0-brief.md）。主 Agent 确认 P0-brief 四字段齐全即可推进 P1。" >&2

**结论**：ALIGNED — 文档声明四字段，脚本消息同步为四字段。P0 是 exit 2（主 Agent 自判），脚本不做字段检查，消息文本与文档一致。

---

### A2: 脚本→文档对齐

**脚本实现**（check-gate.sh:39）：
> 主 Agent 确认 P0-brief 四字段齐全即可推进 P1

**文档同步情况**：
- state-machine.md:76 → 四字段 ✓
- dispatch-protocol.md:203 → 四个必填字段 ✓
- WORKFLOW.md:273 → 四字段自查 ✓
- P0-orchestrator.md:11,27,42 → 四字段 ✓
- P1-requirements.md:27 → 四字段齐全 ✓
- state-transitions.md:15 → 四字段自查通过 ✓
- active-tasks-template.md:44 → 四字段非空 ✓
- task-files.md:25 → task/known_risks/executor_env/env_constraints ✓

**结论**：ALIGNED — 脚本消息变更已同步到所有直接引用"五字段"的协议文件。

---

### A3: 一致性连锁 + 反向传播

#### A3a: 连锁（diff 内文件互检）

diff 内 10 个协议文件互相一致，均已完成 pruning_tendency 移除和五→四字段更新。

**但有一处格式 bug**：

**dispatch-protocol.md:200**（yaml 代码块内）：
```yaml
   env_constraints:
     debug_env: {项目的测试/调试环境路径/命令，从项目约定读取}
     # 不写 prod_env：生产环境不在 agate 开发流程范围内
phase_hint: [P1, P2, ..., P8]  # 主 Agent 预判，P1 analyst 可调整，但须经主 Agent 确认
```

`phase_hint` 原与 `pruning_tendency` 同行缩进（3 空格），删除 `pruning_tendency` 时 `phase_hint` 的缩进也被移除，变成顶格。yaml 块内其他键均缩进 3-4 空格，`phase_hint` 顶格破坏了代码块格式。

**结论**：MISALIGNED
**差异**：dispatch-protocol.md:200 `phase_hint` 缩进丢失（应为 3 空格缩进，实际顶格）
**建议**：恢复 `phase_hint` 行的 3 空格缩进，与 yaml 块内其他键对齐

#### A3b: 反向传播（应被影响但 diff 未列出的文件）

基于反向传播表（改 dispatch-protocol.md / state-machine.md → 角色文件、模板文件），逐一检查：

| 文件 | 是否含残留引用 | 结论 |
|------|---------------|------|
| analyst.md:22 | "环境约束、已知风险、**裁剪倾向**" | MISALIGNED |
| implementer.md:31 | "环境约束、已知风险、**裁剪倾向**" | MISALIGNED |
| architect.md:28 | "环境约束、已知风险、**裁剪倾向**" | MISALIGNED |
| test-designer.md:21 | "环境约束、已知风险、**裁剪倾向**" | MISALIGNED |
| dispatch-protocol.md:217 | T005/T006 教训文本："缺少主 Agent 对环境约束、风险、**裁剪倾向**的判断注入" | NEEDS_HUMAN_REVIEW |
| docs/plans/agate-protocol-maintenance-patch-20260724.md:16 | "P0-brief 已通过 **pruning_tendency**/phase_hint 捕获其下游影响" | MISALIGNED |
| orchestrator-template.md | 无引用 | ALIGNED |
| role-system.md | 无引用 | ALIGNED |
| CONTEXT.md | 无引用 | ALIGNED |
| LIMITATIONS.md | 无引用 | ALIGNED |
| verifier.md / vision-analyst.md | 无引用 | ALIGNED |

**4 个角色文件 MISALIGNED**：analyst.md、implementer.md、architect.md、test-designer.md 的"输入"节仍用"裁剪倾向"描述 P0-brief 内容。pruning_tendency 已移除，这些描述不再准确。

**建议**：将 4 个角色文件的"环境约束、已知风险、裁剪倾向"改为"环境约束、已知风险"（或"环境约束、已知风险、阶段预判"，保留 phase_hint 的提示）。

**dispatch-protocol.md:217 NEEDS_HUMAN_REVIEW**：T005/T006 教训是历史事故描述，"裁剪倾向"在此处是描述当时 P0-brief 包含的内容。可保留（历史记录）或更新（避免暗示该字段仍存在）。需人工裁决。

**docs/plans/agate-protocol-maintenance-patch-20260724.md:16 MISALIGNED**：活跃计划文档，P2.25 DROP 理由写"P0-brief 已通过 pruning_tendency/phase_hint 捕获其下游影响"，引用已删除的字段作为论据。

**建议**：更新为"P0-brief 已通过 phase_hint 捕获其下游影响"。

---

### A4: 测试覆盖

**bats 全量实跑输出**（2026-07-26）：
```
ok 470 SG.8 SELF-GATE.md 含递归终止条件
```
470 个测试全部通过（464 个 @test 定义 + sanity.bats 6 个）。

**P0 gate 测试覆盖**：P0 是 exit 2（主 Agent 自判），check-gate.sh 不做字段检查。本次变更只改了 P0 消息文本（五→四），不影响 exit code 逻辑。现有 P0 测试（check-gate.bats 中 P0 case）覆盖 exit 2 行为，无需新增测试。

**consistency 检查**：`python3 agate/scripts/check-protocol-consistency.py` → 0 ERROR，12 WARNING（均为既有叙事文件死链，非本次引入）。

**结论**：ALIGNED

---

### A5: 下游影响 + 文档传播

**破坏性变更**：无。pruning_tendency 是 P0-brief 的可选声明字段，移除不影响已有任务的 gate 行为（P0 gate 是 exit 2，不检查字段）。

**CHANGELOG**：CHANGELOG.md 最新条目为 v0.20.0（2026-07-24），本次变更无 CHANGELOG 条目。

**结论**：MISALIGNED
**差异**：协议语义变更（P0-brief 字段集从 5 减为 4）未在 CHANGELOG.md 记录
**建议**：在 CHANGELOG.md 新增条目（如 v0.21.0 或 Unreleased），记录 pruning_tendency 移除 + office-hours 触发条件简化

**文档传播**（除 A3b 已列的角色文件外）：
- WORKFLOW.md ✓（已更新）
- dispatch-protocol.md ✓（已更新，但有缩进 bug）
- orchestrator-template.md ✓（无引用）
- role-system.md ✓（无引用）
- 模板文件 ✓（task-files.md、active-tasks-template.md 已更新）
- 角色文件 ✗（4 个文件未更新，见 A3b）

---

### A6: 锚点表覆盖

CHECK 9 锚点表（check-protocol-consistency.py）不含 pruning_tendency 相关锚点。`check-pruning.sh` 的锚点是 P2 裁剪条件检查（P2.7-P2.9），与 P0-brief 的 pruning_tendency 字段无关。

本次变更不新增协议规则，不需要新增锚点。

**结论**：ALIGNED

---

### A7: 设计原则一致性

**ADR-002（可判定性）**：pruning_tendency 是主观偏好（"保守/激进"），不可机器判定。移除它符合 ADR-002"gate 门槛机器可判定"的原则——P0 gate 本就不检查此字段（exit 2），移除后协议更诚实。

**ADR-001（隔离性）**：P0-brief 是主 Agent 的合法职责（编排工作），字段精简不违反隔离性。

**ADR-005（改动性质判断）**：pruning_tendency 与 risk_level（P1）功能重叠，移除消除了重复声明。

**结论**：ALIGNED — 变更符合已有 ADR，无未记录的架构决策。

---

## 修复清单

| # | 文件 | 问题 | 优先级 |
|---|------|------|--------|
| 1 | dispatch-protocol.md:200 | `phase_hint` 缩进丢失（顶格→应 3 空格） | 高（格式 bug） |
| 2 | analyst.md:22 | "裁剪倾向"残留 | 高 |
| 3 | implementer.md:31 | "裁剪倾向"残留 | 高 |
| 4 | architect.md:28 | "裁剪倾向"残留 | 高 |
| 5 | test-designer.md:21 | "裁剪倾向"残留 | 高 |
| 6 | CHANGELOG.md | 缺本次变更条目 | 中 |
| 7 | docs/plans/agate-protocol-maintenance-patch-20260724.md:16 | 引用已删除字段 | 低 |
| 8 | dispatch-protocol.md:217 | T005/T006 教训文本含"裁剪倾向" | 低（NEEDS_HUMAN_REVIEW） |
