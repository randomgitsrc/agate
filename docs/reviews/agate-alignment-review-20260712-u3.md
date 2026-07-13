---
review_date: 2026-07-12
reviewer: protocol-alignment-review
change_summary: U3 实现 ⑪ dispatch-context 扩展（任务上下文节+P2结构化字段grep+回退诊断引用）+ ⑫ gate 诊断落盘 P{N}-gate-diagnosis.md + N2 诊断格式禁令
files_changed:
  - agate/dispatch-protocol.md
  - agate/assets/templates/dispatch-prompt.md
  - agate/orchestrator-template.md
  - agate/state-machine.md
---

# 协议-脚本对齐审查

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | NEEDS_HUMAN_REVIEW |
| A4 | 测试覆盖 | NEEDS_HUMAN_REVIEW |
| A5 | 下游影响 + 文档传播 | ALIGNED |
| A6 | 锚点表覆盖 | NEEDS_HUMAN_REVIEW |

## 逐项审查

### A1: 文档→脚本对齐

**A1.1 dispatch-protocol.md "dispatch-context.md 规范"节含任务上下文子节**

**文档声明**（dispatch-protocol.md:287-299）：
> ## 任务上下文（主 Agent 从 P0-brief + gate + 摘要积累）
> - 目标：本阶段要解决什么问题
> - 关注点：从上游产出/gate 诊断中提取的关键约束
> - 已知风险：P0-brief 的 known_risks 中与本阶段相关的
> - 上游关键决策：上一阶段 subagent 摘要中提到的关键选择
> - 上游结构化字段（从 P2-design.md grep 提取，非读全文）：
>   - packages: {值}
>   - domains: {值}
>   - ui_affected: {值}
>   - gate_commands.P5: {值}（P5/P6/P8 派发时）
>   - files_to_read: {值}（P4 派发时）
> - 回退诊断（仅回退时）：见 P{N}-gate-diagnosis.md（路径引用，不 inline 内容）

**结论**：ALIGNED — 结构完整，含目标/关注点/已知风险/上游决策/结构化字段/回退诊断六项。

**A1.2 dispatch-protocol.md "派发 prompt 模板"含结构化"## 任务"节**

**文档声明**（dispatch-protocol.md:399-403）：
> ## 任务
> 目标：{一句话：本阶段要产出什么}
> 关注点：{从 dispatch-context.md 任务上下文节提取，2-5 条}
> 已知约束：{从 P0-brief + 上游产出提取}
> 与上阶段关联：{上一阶段 subagent 摘要中的关键信息}

**结论**：ALIGNED — 四字段结构化任务节存在。

**A1.3 dispatch-prompt.md 含相同结构化任务节**

**文档声明**（dispatch-prompt.md:29-33）：
> ## 任务
> 目标：{一句话：本阶段要产出什么}
> 关注点：{从 dispatch-context.md 任务上下文节提取，2-5 条}
> 已知约束：{从 P0-brief + 上游产出提取}
> 与上阶段关联：{上一阶段 subagent 摘要中的关键信息}

**结论**：ALIGNED — 与 dispatch-protocol.md 内联版完全一致。

**A1.4 dispatch-protocol.md "gate 诊断落盘"节存在且含 P{N}-gate-diagnosis.md 结构**

**文档声明**（dispatch-protocol.md:328-370）：
> gate 失败后，主 Agent 的诊断结果**写入单独的 `P{N}-gate-diagnosis.md`**，不追加到 dispatch-context.md
> 诊断信息结构含 frontmatter（phase/date/trigger）+ gate 结果 + 失败项 + 诊断 + 路由 + 修复方向
> 落盘时机表（重试/退回上游/PAUSED 三场景）

**结论**：ALIGNED — 结构完整，含 frontmatter 模板 + 诊断结构 + 落盘时机表。

**A1.5 N2 格式禁令已文档化**

**文档声明**（dispatch-protocol.md:349-361）：
> `gate-diagnosis.md` 和 `dispatch-context.md` 回退诊断节**禁止使用 `^\s*- (PASS|FAIL)` 行首格式**
> 允许格式：`失败项：B03, B07` / `- 失败BDD: B03 ...` / `gate 结果：FAIL=3, NC=0`
> 禁止格式：`- FAIL B03: ...` / `- PASS B01: ...`

**脚本实现**（check-p6-provenance.sh:100-108）：
> DISPATCH_CTX="$TASK_DIR/P6-dispatch-context.md"
> PREJUDICE=$(grep -cE '^\s*- (PASS|FAIL)\b' "$DISPATCH_CTX" 2>/dev/null || echo 0)
> if [ "$PREJUDICE" -gt 0 ]; then exit 1; fi

**结论**：ALIGNED — N2 禁令的 regex `^\s*- (PASS|FAIL)\b` 与审计 2 的 grep pattern `^\s*- (PASS|FAIL)\b` 完全一致。允许的格式确实不匹配该 pattern（`失败BDD` 前缀不匹配 `(PASS|FAIL)\b`，`FAIL=3` 等号后不匹配行首列表格式）。

**A1.6 dispatch-protocol.md 信息来源表存在**

**文档声明**（dispatch-protocol.md:301-309）：
> | 来源 | 何时写入 | 写什么 |
> | P0-brief | 首次派发 P1 时 | 目标 + 已知风险 |
> | subagent 返回摘要 | 每次收到 subagent 返回时 | 上游关键决策 |
> | gate 诊断 | gate 失败时 | 关注点 + 回退诊断 |
> | 主 Agent 查证 | 派发前查证客观信息时 | 客观信息节 |
> | P2-design.md 结构化字段 | P4/P5/P6/P8 派发时 | packages/domains/gate_commands/files_to_read |

**结论**：ALIGNED — 五行信息来源表完整。

**A1.7 dispatch-protocol.md 描述生命周期**

**文档声明**（dispatch-protocol.md:311-315）：
> - 每个阶段一个文件：`P{N}-dispatch-context.md`
> - 主 Agent 在派发前写，派发后**冻结**
> - 重试/回退时的诊断信息**不追加到 dispatch-context.md**，写入单独的 `P{N}-gate-diagnosis.md`
> - 回退时：新写目标阶段的 dispatch-context.md，包含回退诊断信息

**结论**：ALIGNED — 生命周期四条规则完整。

**A1.8 orchestrator-template.md 提及任务上下文**

**文档声明**（orchestrator-template.md:58）：
> 派发前查证客观信息 + 任务上下文（目标/关注点/已知约束/上游决策/P2结构化字段grep），落盘成 `P{N}-dispatch-context.md`

**结论**：ALIGNED — orchestrator-template.md 已同步更新，提及任务上下文及五项内容。

**A1.9 state-machine.md 含诊断注解**

**文档声明**（state-machine.md:111）：
> （gate 失败后主 Agent 诊断落盘 P{N}-gate-diagnosis.md，见 ⑫）

**文档声明**（state-machine.md:577）：
> （回退时携带诊断：新写目标阶段 dispatch-context.md + 引用 gate-diagnosis.md 路径，诊断内容不 inline 到 dispatch-context，见 ⑪⑫）

**结论**：ALIGNED — 两处注解已添加。

### A2: 脚本→文档对齐

**A2.1 check-p6-provenance.sh 是否需要适配任务上下文节**

**脚本实现**（check-p6-provenance.sh:97-108）：
审计 2 只检查 `P6-dispatch-context.md` 是否含 `^\s*- (PASS|FAIL)\b` 行首格式。任务上下文节的内容（目标/关注点/已知风险/上游决策/结构化字段/回退诊断引用）不含 PASS/FAIL 行首格式，不会触发审计 2。

**结论**：ALIGNED — 不需要适配。任务上下文节的字段名（目标/关注点/已知风险/上游关键决策/packages/domains/ui_affected/gate_commands/files_to_read/回退诊断）均不匹配 `^\s*- (PASS|FAIL)\b`。

**A2.2 N2 禁令与审计 2 实际检查的一致性**

**文档声明**（dispatch-protocol.md:351）：
> `check-p6-provenance.sh` 审计 2 grep `^\s*- (PASS|FAIL)\b` 于 dispatch-context.md

**脚本实现**（check-p6-provenance.sh:102）：
> grep -cE '^\s*- (PASS|FAIL)\b' "$DISPATCH_CTX"

**结论**：ALIGNED — 文档描述的 regex 与脚本实际使用的 regex 完全一致。N2 禁令的允许/禁止格式示例与该 regex 的匹配行为一致。

### A3: 一致性连锁 + 反向传播

**A3a: 已知衍生改动（diff 中已包含）**

| 文件 | 是否在 diff 中 | 状态 |
|------|---------------|------|
| dispatch-protocol.md | ✅ | 已改 |
| dispatch-prompt.md | ✅ | 已改 |
| orchestrator-template.md | ✅ | 已改 |
| state-machine.md | ✅ | 已改 |

**A3b: 反向传播——应被影响但未列在 diff 中的文件**

| 文件 | 是否应改 | 分析 |
|------|---------|------|
| `agate/assets/templates/dispatch-context.md` | **应改** | 模板仍只有 `## 任务上下文` 含 task_id + P0-brief 路径（2 行），缺少 dispatch-protocol.md:287-299 定义的完整结构（目标/关注点/已知风险/上游决策/结构化字段/回退诊断）。模板是主 Agent 实际使用的骨架，与协议规范不一致会导致产出缺字段。 |
| `agate/assets/templates/task-files.md` | **应改** | 辅助文件表（task-files.md:43）描述 dispatch-context.md 为"派发前查证的客观信息（环境状态、URL、选择器等）"，未提及任务上下文节。gate-diagnosis.md 未列入辅助文件表。 |
| `agate/WORKFLOW.md` | **可能应改** | WORKFLOW.md:249 提及 dispatch-context 但描述为"查证客观信息"，未提及任务上下文。需确认是否需同步。 |
| `agate/LIMITATIONS.md` | 不需改 | LIMITATIONS.md:40 提及 dispatch-context 审计，描述仍准确。 |
| `agate/scripts/check-p6-provenance.sh` | 不需改 | 审计 2 逻辑不受影响（见 A2.1）。 |
| `agate/scripts/check-protocol-consistency.py` | 不需改 | CHECK 9 锚点表已有 provenance 审计锚点，无新脚本需加锚点。 |
| `agate/assets/execution-roles/*.md` | 不需改 | 角色文件已引用 dispatch-context.md 路径，不描述其内部结构。 |
| `agate/phase-cards/*.md` | 不需改 | 阶段卡片引用 dispatch-context.md 路径，不描述其内部结构。 |

**结论**：NEEDS_HUMAN_REVIEW — `dispatch-context.md` 模板和 `task-files.md` 辅助文件表与协议规范不一致。模板缺任务上下文完整结构，task-files.md 缺 gate-diagnosis.md 条目和 dispatch-context 描述更新。WORKFLOW.md 是否需同步需人工判断。

### A4: 测试覆盖

**A4.1 PV.17 测试（dispatch-context 含任务上下文节）**

搜索结果：不存在 PV.17 测试。现有 PV.8 测试覆盖 dispatch-context 含 PASS 预判场景，但无测试验证 dispatch-context.md 模板含任务上下文节的完整结构。

**A4.2 D-drift-4 测试（dispatch-prompt.md 结构化任务节）**

搜索结果：不存在 D-drift-4 测试。现有 D-drift-1/D-drift-2 测试覆盖 dispatch-prompt.md 的"返回前自检"和"files_modified"关键词，但无测试验证结构化任务节（目标/关注点/已知约束/与上阶段关联）存在。

**A4.3 N2 禁令测试**

搜索结果：无专门测试验证 gate-diagnosis.md 的 N2 格式禁令。PV.8 测试覆盖 dispatch-context 含 PASS 预判场景，但未覆盖 gate-diagnosis.md 文件（审计 2 只检查 P6-dispatch-context.md，不检查 gate-diagnosis.md——这是正确行为，N2 禁令是文档约束不是脚本强制）。

**A4.4 gate-diagnosis.md 落盘测试**

搜索结果：无测试覆盖 gate-diagnosis.md 的落盘时机（重试/退回/PAUSED）。

**bats 全量实跑结果**：

```
248 passed, 0 failed, 0 skipped
（bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/）
```

**结论**：NEEDS_HUMAN_REVIEW — 缺少 PV.17（dispatch-context 任务上下文节结构验证）和 D-drift-4（dispatch-prompt 结构化任务节验证）测试。N2 禁令和 gate-diagnosis.md 落盘无测试覆盖，但这两项是文档约束（无对应脚本检查），测试优先级低于前两项。现有 248 测试全部通过。

### A5: 下游影响 + 文档传播

**A5.1 任务上下文节对 provenance 审计的影响**

任务上下文节内容（目标/关注点/已知风险/上游决策/结构化字段/回退诊断引用）不含 `^\s*- (PASS|FAIL)\b` 格式，不触发审计 2。P2 结构化字段 grep 提取（`grep -E '^(packages|domains|ui_affected|gate_commands|files_to_read):' P2-design.md`）是读特定字段不是读全文，不违反铁律 2。

**结论**：ALIGNED — 无破坏性影响。

**A5.2 gate-diagnosis.md 格式对 gate 脚本的影响**

gate-diagnosis.md 是新文件类型，当前无脚本检查其内容。N2 禁令是文档约束，不依赖脚本强制。check-p6-provenance.sh 审计 2 只检查 P6-dispatch-context.md，不检查 gate-diagnosis.md——这是正确的，因为 gate-diagnosis.md 是事后诊断不是预判。

**结论**：ALIGNED — 无破坏性影响。gate-diagnosis.md 不被任何现有脚本检查，N2 禁令通过文档约束 + 允许格式示例实现。

**A5.3 文档传播**

| 应传播文件 | 是否已更新 | 状态 |
|-----------|-----------|------|
| dispatch-protocol.md | ✅ | 已更新 |
| dispatch-prompt.md | ✅ | 已更新 |
| orchestrator-template.md | ✅ | 已更新 |
| state-machine.md | ✅ | 已更新 |
| dispatch-context.md 模板 | ❌ | 未更新（见 A3b） |
| task-files.md | ❌ | 未更新（见 A3b） |
| WORKFLOW.md | ❌ | 未更新（见 A3b） |
| CHANGELOG.md | — | 协议语义变更，需确认是否标注 |

### A6: 锚点表覆盖

**A6.1 CHECK 9 是否有 dispatch-context 任务上下文 → check-p6-provenance.sh 锚点**

检查 `SCRIPT_ALIGNMENT_ANCHORS`（check-protocol-consistency.py:443-539）：

现有锚点：
- `"P6 provenance 审计"` → `check-p6-provenance.sh` → keywords: `["EVIDENCE_DIR"]`

该锚点覆盖 provenance 审计脚本的存在性，但不覆盖 dispatch-context 内容约束（审计 2）的具体规则。新增的 N2 禁令和任务上下文节没有对应锚点。

**是否需要新增锚点**：

1. **dispatch-context 任务上下文 → check-p6-provenance.sh**：审计 2 检查 dispatch-context 不含 PASS/FAIL 预判，这是已有规则（非 U3 新增），只是 U3 扩展了 dispatch-context 的内容结构。新增锚点可提高覆盖度，但现有 provenance 审计锚点已间接覆盖。

2. **gate-diagnosis.md N2 禁令**：无对应脚本检查，无法加锚点（锚点要求脚本含关键词）。

3. **dispatch-context 派发后冻结**：无对应脚本检查，无法加锚点。

**结论**：NEEDS_HUMAN_REVIEW — 现有锚点间接覆盖 provenance 审计，但 dispatch-context 内容约束（审计 2 的 PASS/FAIL 预判检查）无直接锚点。建议新增锚点：`{"desc": "dispatch-context PASS/FAIL 预判检查", "script": "agate/scripts/check-p6-provenance.sh", "keywords": ["dispatch-context", "预判"]}`。gate-diagnosis.md 和冻结约束无对应脚本，不加锚点。

---

## 修复建议汇总

| 优先级 | 项目 | 建议 |
|--------|------|------|
| P1 | dispatch-context.md 模板 | 补充任务上下文完整结构（目标/关注点/已知风险/上游决策/结构化字段/回退诊断），与 dispatch-protocol.md:287-299 一致 |
| P1 | task-files.md | 辅助文件表增加 gate-diagnosis.md 条目；更新 dispatch-context.md 描述含任务上下文 |
| P2 | 测试 | 新增 D-drift-4 测试验证 dispatch-prompt.md 含"目标：/关注点：/已知约束：/与上阶段关联："四字段 |
| P2 | 测试 | 新增 PV.17 测试验证 dispatch-context.md 模板含"## 任务上下文"节及子字段 |
| P3 | CHECK 9 锚点 | 新增 dispatch-context 预判检查锚点 |
| P3 | WORKFLOW.md | 确认是否需同步 dispatch-context 描述（当前仅提"查证客观信息"） |

[HUMAN_CONFIRMED: 2026-07-12 确认：A3b dispatch-context.md 模板和 task-files.md 缺失是真实遗漏，需修复。A4 缺失测试优先级 P2 合理。A6 锚点建议合理。WORKFLOW.md 同步待人工判断。]
