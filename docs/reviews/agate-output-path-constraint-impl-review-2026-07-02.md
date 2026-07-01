---
date: 2026-07-02
reviewer: protocol-alignment-review
scope: subagent 产出路径约束实施评审（设计文档 agate-output-path-constraint-design-2026-07-02 的实施结果）
design_doc: docs/plans/agate-output-path-constraint-design-2026-07-02.md
files:
  - agate/dispatch-protocol.md (L317-324 "## 输出"节, L345-364 "非阶段产出的路径规范"节)
  - agate/assets/templates/dispatch-prompt.md (L35-43 "## 输出"节, L161 "关键提醒"节)
  - SELF-GATE.md (L131-136, L177-182 两个派发模板的"## 产出"节)
verification:
  - python3 agate/scripts/check-protocol-consistency.py: 0 ERROR, 3 WARNING (均预先存在，与本次改动无关)
  - CHECK 9 PASS（新增"非阶段产出的路径规范"节未破坏脚本结构对齐）
---

# 实施评审结论汇总

| # | 设计改动 | 实施位置 | 结论 |
|---|---------|---------|------|
| 1 | dispatch-protocol.md "## 输出"节加路径约束 | L317-324 | **ALIGNED** |
| 1 | dispatch-prompt.md "## 输出"节加路径约束 | L35-43 | **ALIGNED** |
| 2 | dispatch-protocol.md 新增"非阶段产出的路径规范"节 | L345-364 | **ALIGNED** |
| 3 | SELF-GATE.md 变更触发模板"## 产出"节加约束 | L135 | **ALIGNED** |
| 3 | SELF-GATE.md 全量审查模板"## 产出"节加约束 | L181 | **ALIGNED** |
| 4 | dispatch-prompt.md "关键提醒"节补一条 | L161 | **ALIGNED** |
| 5 | orchestrator-template.md 确认无需同步 | L52（只引用不内联） | **ALIGNED** |

**总体结论：ALIGNED**

---

# 逐项审查详情

## 改动 1：dispatch-protocol.md "## 输出"节加路径约束

**设计要求**（设计文档 L35-46）：在"## 输出"节加禁止性约束，标题改为"## 输出（路径约束）"，含 3 条约束 + 1 条 /tmp 区分说明。

**实际实施**（dispatch-protocol.md L317-324）：
```
## 输出（路径约束）
产出文件：docs/tasks/{Txxx}/{本阶段产出文件}

⚠️ 路径是硬约束，不是建议：
- 必须用 Write 工具写入上述路径
- 不得将产出文件写入 /tmp、工作区根目录、或其他自选路径
- 写到其他位置 = 未产出，主 Agent 只检查上述路径
- /tmp 可用于中间临时文件（如 gate-runner 落盘 traceback），但产出文件必须写入约定路径
```

**核对**：
- 标题改为"## 输出（路径约束）" ✓
- 3 条核心约束逐字一致 ✓
- 第 4 条 /tmp 区分：设计文档 L47 将此作为节外"注意"说明，实施时整合进约束列表第 4 条。合理整合，语义无损 ✓
- 措辞精确区分"产出文件"（必须写入约定路径）与"中间临时文件"（可入 /tmp）✓

**结论：ALIGNED**

## 改动 1（续）：dispatch-prompt.md "## 输出"节加路径约束

**实际实施**（dispatch-prompt.md L35-43）：
```
## 输出（路径约束）
产出文件：docs/tasks/{Txxx}/{本阶段产出文件}
（Txxx 是完整目录名...）

⚠️ 路径是硬约束，不是建议：
- 必须用 Write 工具写入上述路径
- 不得将产出文件写入 /tmp、工作区根目录、或其他自选路径
- 写到其他位置 = 未产出，主 Agent 只检查上述路径
- /tmp 可用于中间临时文件，但产出文件必须写入上述路径
```

**核对**：
- 4 条约束齐全 ✓
- 第 4 条与 dispatch-protocol.md 有细微措辞差异（见下"一致性检查"）

**结论：ALIGNED**

## 改动 2：dispatch-protocol.md 新增"非阶段产出的路径规范"节

**设计要求**（设计文档 L49-71）：新增一节，含 3 条规则 + /tmp 区分说明 + self-gate 审查派发示例。

**实际实施**（dispatch-protocol.md L345-364）：
- 3 条规则（具体路径 / 硬约束声明 / 区分留痕文件与成果文件）✓
- /tmp 区分说明（L353）✓
- self-gate 审查派发示例（L355-364，含"## 产出（成果文件）"和"## 分阶段落盘（留痕文件）"两个子节）✓

**位置检查**：该节为 `###` 级别（L345），位于"## 派发 prompt 模板"大节内，紧跟内联模板代码块（L284-343）之后，"### 阶段特定提示"节（L366）之前。位置合理——作为内联模板的补充说明，紧跟模板本身，符合读者阅读流。✓

**结论：ALIGNED**

## 改动 3：SELF-GATE.md 两个派发模板"## 产出"节加约束

**设计要求**（设计文档 L73-75）：两个模板的"## 产出"节补加"不得写入 /tmp 或其他路径"。

**实际实施**：
- 变更触发模板（SELF-GATE.md L135）：`⚠️ 路径是硬约束：必须用 Write 工具写入此路径，不得将产出文件写入 /tmp 或其他路径。`
- 全量审查模板（SELF-GATE.md L181）：同上措辞 ✓

**核对**：
- 两个模板均加了硬约束声明 ✓
- 措辞一致 ✓
- 比设计要求多了一句"必须用 Write 工具写入此路径"——更完整的约束，增强而非偏离 ✓
- SELF-GATE.md 的约束措辞精简（1 行），区别于 dispatch 模板的 4 条列表——合理，因为 self-gate 模板是特定场景，不需要重复通用模板的完整列表 ✓

**结论：ALIGNED**

## 改动 4：dispatch-prompt.md "关键提醒"节补一条

**设计要求**（设计文档 L79-83）：补一条"产出路径是硬约束"提醒。

**实际实施**（dispatch-prompt.md L161）：
```
- **产出路径是硬约束**：subagent 必须写入 prompt 指定的路径，不得将产出文件写到 /tmp 或其他位置。主 Agent 只检查约定路径，写错位置 = 未产出 = 重试浪费
```

**核对**：与设计文档 L82 文本逐字一致 ✓

**结论：ALIGNED**

## 改动 5：orchestrator-template.md 确认无需同步

**设计要求**（设计文档 L85-87）：确认 orchestrator-template.md 只引用 dispatch-protocol.md，不内联模板，无需同步。

**实际验证**（orchestrator-template.md L52）：
```
**派发不是传话**：...（见 dispatch-protocol.md「输入导航原则」）。
```
- 全文无"## 输出（路径约束）"节、无"产出文件："行、无内联派发模板 ✓
- 仅以引用方式指向 dispatch-protocol.md ✓

**结论：ALIGNED**（确认无需同步）

---

# 一致性检查

## dispatch-protocol.md 内联模板 vs dispatch-prompt.md 完整模板的"## 输出"节

dispatch-prompt.md L4 声明："本模板与 dispatch-protocol.md「派发 prompt 模板」节保持同步，协议文件为权威来源"。

| 约束条 | dispatch-protocol.md (L320-324) | dispatch-prompt.md (L39-43) | 一致？ |
|--------|-------------------------------|----------------------------|--------|
| 1 | 必须用 Write 工具写入上述路径 | 必须用 Write 工具写入上述路径 | 逐字一致 ✓ |
| 2 | 不得将产出文件写入 /tmp、工作区根目录、或其他自选路径 | 同左 | 逐字一致 ✓ |
| 3 | 写到其他位置 = 未产出，主 Agent 只检查上述路径 | 同左 | 逐字一致 ✓ |
| 4 | /tmp 可用于中间临时文件**（如 gate-runner 落盘 traceback）**，但产出文件必须写入**约定路径** | /tmp 可用于中间临时文件，但产出文件必须写入**上述路径** | 语义一致，措辞有差异 |

**第 4 条差异分析**：
1. dispatch-protocol.md 有括号举例"（如 gate-runner 落盘 traceback）"，dispatch-prompt.md 无
2. dispatch-protocol.md 用"约定路径"，dispatch-prompt.md 用"上述路径"

**评估**：两处语义完全等价。"上述路径"在 dispatch-prompt.md 上下文中明确指代 L36 的"产出文件：docs/tasks/{Txxx}/{本阶段产出文件}"，与"约定路径"同义。举例的有无不影响约束效力。dispatch-prompt.md 是直接给 subagent 执行的模板，省略举例反而更简洁。

**结论**：语义同步达成，满足"保持同步"要求。若追求严格逐字一致可补齐举例，但非必须。**不构成 MISALIGNED**。

## SELF-GATE.md 两个模板约束措辞一致性

变更触发模板（L135）与全量审查模板（L181）的约束行逐字一致 ✓

---

# 反向传播检查

## 应被影响但 git diff 可能未列出的文件

基于"subagent 产出路径约束"这一意图，推断应传播的文件：

| 候选文件 | 是否需要同步 | 理由 |
|---------|-------------|------|
| agate/assets/execution-roles/*.md（角色文件） | 否 | 角色文件的"### 输出"节（如 verifier.md L37-40）是角色定义（告诉角色产出哪些文件），不是派发 prompt 的"## 输出"节。路径约束由派发 prompt（主 Agent 用 dispatch-prompt.md 模板填写）携带，角色文件不内联路径约束。设计文档 L103 判断正确。 |
| agate/assets/review-roles/*.md | 否 | 同上。design-review.md L44 的"产出文件路径"是返回格式说明，非路径约束。 |
| agate/assets/templates/task-files.md | 否 | 文件结构模板，定义产出文件的 Header/字段结构，不涉及路径约束。 |
| agate/orchestrator-template.md | 否（改动 5 已确认） | L52 只引用 dispatch-protocol.md，不内联派发模板。 |
| agate/WORKFLOW.md | 否 | L68 仅列出 dispatch-prompt.md 作为模板文件索引，不内联"## 输出"节。 |
| agate/state-machine.md | 否 | 涉及"产出文件"的语境是状态绑定检查（.state.yaml phase 与产出文件匹配），不涉及派发路径约束。 |
| agate/scripts/*.sh | 否 | 设计文档 L99 明确"不加脚本检查，产出路径由主 Agent 校验"。本次为纯文档约束。 |

**结论：反向传播无遗漏。** 所有应被影响的文件均已覆盖，无需同步的文件判断正确。

---

# 措辞精确性检查

设计文档 L47 强调区分"产出文件"与"临时文件"：

| 文件 | 区分表述 | 精确？ |
|------|---------|--------|
| dispatch-protocol.md L324 | "/tmp 可用于中间临时文件（如 gate-runner 落盘 traceback），但产出文件必须写入约定路径" | ✓ 明确 |
| dispatch-protocol.md L353 | "/tmp 可用于中间临时文件...但**产出文件**（主 Agent 校验的那个）必须写入约定路径" | ✓ 明确，加粗强调 |
| dispatch-prompt.md L43 | "/tmp 可用于中间临时文件，但产出文件必须写入上述路径" | ✓ 明确 |
| SELF-GATE.md L135/L181 | "不得将产出文件写入 /tmp 或其他路径"（未提临时文件） | ✓ 合理——self-gate 审查场景不需要中间临时文件 |

**结论：措辞精确，"产出文件"与"临时文件"区分清晰。**

---

# 验证

- `python3 agate/scripts/check-protocol-consistency.py`：**0 ERROR**，3 WARNING（均预先存在：analyst.md YAML 引号、两个旧 plan 引用的脚本不存在——与本次改动无关）
- CHECK 9（协议-脚本结构对齐）：**PASS**——新增"非阶段产出的路径规范"节为纯文档约束，不涉及脚本行为，未破坏结构对齐

---

# 总体结论

**ALIGNED**

设计文档的 5 个改动全部实施，且：
1. dispatch-protocol.md 与 dispatch-prompt.md 的"## 输出"节语义一致（仅第 4 条有细微措辞差异，不影响语义）
2. "非阶段产出的路径规范"节位置合理（内联模板后、阶段特定提示前）
3. SELF-GATE.md 两个模板均加了硬约束，措辞一致
4. 措辞精确区分"产出文件"与"临时文件"
5. 反向传播无遗漏（角色文件/orchestrator-template.md 等判断正确）
6. consistency 检查 0 ERROR，CHECK 9 PASS

**建议（非阻塞）**：dispatch-prompt.md L43 第 4 条可补齐举例"（如 gate-runner 落盘 traceback）"并与 dispatch-protocol.md 统一用"约定路径"，追求严格逐字同步。当前语义已同步，不阻塞 commit。
