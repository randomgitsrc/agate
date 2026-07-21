---
review_date: 2026-07-21
reviewer: protocol-alignment-review
change_summary: 复盘发现 3 个 bug（agate-inject-card 静默成功、SCOPE+ 误匹配 dispatch-context、CHANGELOG 全路径搜索）+ 1 项 P5 全量测试 WARNING 设计改进
files_changed: [agate/scripts/agate-inject-card.sh, agate/scripts/check-scope-resolved.sh, agate/scripts/check-changelog.sh, agate/scripts/check-gate.sh, agate/tests/unit/agate-inject-card.bats, agate/tests/unit/check-scope-resolved.bats, agate/tests/unit/check-changelog.bats, agate/tests/unit/check-gate.bats]
---

# 协议-脚本对齐审查

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | MISALIGNED |
| A2 | 脚本→文档对齐 | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | ALIGNED |
| A4 | 测试覆盖 | NEEDS_HUMAN_REVIEW |
| A5 | 下游影响 + 文档传播 | ALIGNED |
| A6 | 锚点表覆盖 | ALIGNED |
| A7 | 设计原则一致性 | ALIGNED |

## 逐项审查

### A1: 文档→脚本对齐

**A1.1 Bug 1（agate-inject-card.sh 静默成功）**

**脚本现状**（agate-inject-card.sh:49-53）：
> `re.sub()` returns original string when pattern doesn't match — no error check, always prints "AGATE_CARD 已注入".

**计划修复**（plan:58-67）：
> Add `if new_text == text: print(...) + sys.exit(1)` — exit 1 on missing placeholder.

**协议文档声明**：
- `scripts/README.md:50`：描述为"主 Agent 调 agate-next-card.sh P{N} 拿到对应阶段卡片全文，嵌入 dispatch-context-{role}.md"——未提及占位符缺失行为
- 现有测试（`agate-inject-card.bats:140-148,150-158`）已建立"错误应 exit 1"的惯例（文件不存在/缺参数等场景）

**结论**：ALIGNED。这是 bug 修复——把静默成功改为显式报错，符合脚本已有的错误处理惯例。无协议语义变更。

---

**A1.2 Bug 2（SCOPE+ 误匹配 dispatch-context 约束指令）**

**脚本现状**（check-scope-resolved.sh:16-21）：
> `for f in "$TASK_DIR"/*.md` — scans ALL .md files, excludes AGATE_CARD blocks via sed but NOT dispatch-context files.

**计划修复**（plan:118-126）：
> Add `basename "$f" | grep -q 'dispatch-context' && continue` — skip dispatch-context files.

**协议文档声明**：
- `state-machine.md:211`：「任意阶段 Pn **产出**含 [SCOPE+] → 主 Agent 增补 P1 基线」（强调"产出"，dispatch-context 是编排指令，非阶段产出）
- `dispatch-protocol.md:812`（pre-commit 全景）：「阶段级 P2.11 | check-scope-resolved.sh | [SCOPE+] 标记追踪」——描述不区分阶段产出 vs dispatch-context

**结论**：ALIGNED。dispatch-context 文件是编排者的指令文件，不是 subagent 的阶段产出。SCOPE+ 语义（state-machine.md:211）明确指"阶段产出"中的发现。修复将脚本行为对齐到此语义。

---

**A1.3 Bug 3（check-changelog.sh 全路径搜索 task_id）**

**计划描述**（plan:162）：
> 「在脚本内提取 `T\d+` 前缀作为搜索关键词，**同时保留原完整字符串作为 fallback**（搜索关键词也支持 `T060` 前缀和 `T060-xxx` 全名两种格式）」

**计划代码 diff**（plan:163-175）：
```diff
  TASK_ID="${1:?用法: check-changelog.sh TASK_ID}"
+
+ # 提取 task_id 短前缀（T\d+）作为 CHANGELOG 搜索关键词
+ # .state.yaml 的 task_id 可能是完整目录名（T060-archived-visibility-auth-refresh），
+ # 但 CHANGELOG 条目通常只写短前缀（T060）
+ TASK_ID_SHORT=$(echo "$TASK_ID" | grep -oE 'T[0-9]+' | head -1)
+ [ -z "$TASK_ID_SHORT" ] && TASK_ID_SHORT="$TASK_ID"

  ...

- if echo "$UNRELEASED_CONTENT" | grep -qF "$TASK_ID"; then
+ if echo "$UNRELEASED_CONTENT" | grep -qE "(^|[^0-9])${TASK_ID_SHORT}( |:|$|,)"; then
```

**分析**：

计划代码 diff 中，`...` 跳过的中间行是 `check-changelog.sh:11-25`（CHANGELOG_FILE 检查 + Python 提取 [Unreleased] 区域），不包含任何 fallback 逻辑。最终的 grep 只有一条 regex 匹配，完全替换了原来的 `grep -qF "$TASK_ID"` 固定字符串搜索。

**矛盾点**：

1. 计划文字（plan:162）声称「同时保留原完整字符串作为 fallback」，但代码 diff 没有实现 fallback——原来的 `grep -qF "$TASK_ID"` 被完全移除

2. 短前缀 regex `(^|[^0-9])${TASK_ID_SHORT}( |:|$|,)` 无法匹配完整 task_id 格式 `T060-archived-visibility-auth-refresh`，因为 `T060` 后跟 `-`，不在后缀字符集 `( |:|$|,)` 中

3. 测试用例 3（plan:216-230）「CHANGELOG 含完整 task_id 时固定字符串 fallback 生效」期望 CHANGELOG 行 `- T060-archived-visibility-auth-refresh: 条目` 被匹配到并 exit 0——但计划代码无法匹配此行

**验证**：
- CHANGELOG 行：`- T060-archived-visibility-auth-refresh: 条目`
- TASK_ID_SHORT = `T060`
- Regex 匹配：`T060` 前是空格（`[^0-9]` 匹配 ✓），后是 `-`（不在 `( |:|$|,)` 中 ✗）
- 结果：**不匹配**。测试 3 会失败。

**结论**：**MISALIGNED**。计划文字声称实现 fallback（支持两种格式），但代码 diff 仅实现了短前缀匹配。测试用例 3 依赖 fallback 行为，无法通过计划代码。需修复：要么补齐 fallback（短前缀匹配失败后尝试完整 `grep -qF "$TASK_ID"`），要么扩展 regex 后缀集包含 `-`（如 `( |:|-|$|,)`）。

**建议**：补齐 fallback 更安全——先试短前缀 regex，失败后 fallback 到 `grep -qF "$TASK_ID"`。这样既覆盖「CHANGELOG 只写 T060」又覆盖「CHANGELOG 写全名」。

---

**A1.4 Bug 4（P5 全量测试 WARNING）**

**计划修复**（plan:248-257）：P5 分支后追加 WARNING 代码块，计数 `grep -cE '^\s+- ' "$TASK_DIR/P2-design.md"` 中的 bullet 行数。

**协议文档声明**：
- `phase-cards/P5-verification.md:48`：「全量测试 WARNING：P5 阶段建议运行全量测试套件（含非本任务测试），若发现预存失败...」
- `dispatch-protocol.md:786`（P5→P6 门檻）：「从 P2-design.md gate_commands.P5 读取命令执行 → exit 0 AND failed==0」——含「全量」隐含语义
- `state-machine.md:99`（P5→P6 转移）：「P2 gate_commands.P5 命令 exit 0 AND failed==0」

**结论**：ALIGNED。文档已描述"全量测试 WARNING"，Script 层面补上检测逻辑。WARNING 级不改变 gate 通过条件（P5 恒 exit 2），与文档中的"建议"语义一致。

**附注**：grep 模式 `^\s+- ` 计数所有 bullet 行而非精确 gate_commands.P5 内的命令行——计划自身已承认此局限（plan:259）。

---

### A2: 脚本→文档对齐

计划声明需更新的文档（plan:308-316）：
| 文档 | 计划声明的同步 |
|------|---------------|
| `phase-cards/P5-verification.md` | 文档已有 WARNING 描述，脚本补检测逻辑——不冲突 |
| `dispatch-protocol.md:786` | 无变更（P5 恒 exit 2） |
| `CHANGELOG.md` | 标注 4 项改动 |
| `scripts/README.md` | check-changelog.sh 描述更新（搜索方式变更） |
| `AGENTS.md` | 无变更 |

**逐项验证**：

- `phase-cards/P5-verification.md`（phase-cards/P5-verification.md:48）：已有「全量测试 WARNING：P5 阶段建议运行全量测试套件...」——脚本新增 WARNING 对应此文档描述。**不冲突**，但 plan 意图是"同步"而非"不冲突"。实际上文档先于脚本存在，脚本是补上实现——属于 A1 方向而非 A2。
- `dispatch-protocol.md:786`：P5→P6 gate 条件「从 P2-design.md gate_commands.P5 读取命令执行 → exit 0 AND failed==0」——WARNING 不改变此门槛，确实无需同步。**ALIGNED**。
- `scripts/README.md`：当前 `check-changelog.sh` 描述（scripts/README.md:14）为「`[Unreleased]` 含 task_id | 0=通过, 1=未记录」。修复后搜索行为从 `grep -qF "$TASK_ID"` 变为 `grep -qE "(^|[^0-9])${TASK_ID_SHORT}( |:|$|,)"`。描述层面"含 task_id"仍成立（行为更灵活但不改变"含"的语义），但精确度有提升。计划声称需更新描述——属合理优化，不更新也不算 align 失败。**ALIGNED**。
- `CHANGELOG.md`：需标注 4 项改动——此为实施步骤，非协议文档语义。**ALIGNED**。

**额外发现**：
- `agate-inject-card.sh` 未列入 `scripts/README.md` 的「脚本清单」表格。这是预存问题（脚本已存在但 README 遗漏），非本次计划引入。不阻断。

**结论**：ALIGNED。计划声明的文档同步项覆盖合理，无遗漏。

---

### A3: 一致性连锁 + 反向传播

#### A3a 连锁（已知衍生改动）

| 改动 | 应传播到 | 验证结果 |
|------|---------|----------|
| Bug 4 P5 WARNING | `phase-cards/P5-verification.md` | 文档已有对应描述（line 48），不冲突 |
| Bug 4 P5 WARNING | `dispatch-protocol.md` P5 gate 表 | 无变更（WARNING 不改变 exit 2 语义） |
| Bug 4 P5 WARNING | `state-machine.md` P5→P6 转移 | 无变更（转移规则不变） |
| Bug 4 P5 WARNING | `WORKFLOW.md` P5 gate 表 | 无变更（门槛条件不变） |
| Bug 3 search change | `scripts/README.md` | 已纳入 A2 同步 |
| Bug 1-4 全部改动 | `CHANGELOG.md` | 已纳入 A2 同步 |

**结论**：ALIGNED。所有明确连锁传播路径均已处理或确认无需处理。

#### A3b 反向传播（主动推断的应被影响路径）

| 改了 X | 推导的传播 | 分析 |
|--------|-----------|------|
| Bug 2: check-scope-resolved.sh skip dispatch-context | `check-retrospective.sh` 同样扫描 `$TASK_DIR/*.md` 检查 `[SCOPE+]`（check-retrospective.sh:35-41），不含 AGATE_CARD 排除也不含 dispatch-context 排除 | **低影响**：retrospective 是提醒级（exit 0 永不过），dispatch-context 含字面 SCOPE+ 只会多一条无害建议。不修也可，但若追求一致性可与 Bug 2 同步修复 |
| Bug 2: SCOPE+ scan | `check-p6-provenance.sh` — 类似 dispatch-context 扫描 | **已排除**：provenance 审计 2（check-p6-provenance.sh:112）只扫描 `P6-dispatch-context-*.md` 做内容预判检查，不涉及 SCOPE+；agent 字段扫描（check-p6-provenance.sh:221-234）用 `P[0-8]-*.md` glob 但 case 语句已显式 skip dispatch-context 文件（line 227） |
| Bug 2: SCOPE+ scan | `check-pruning.sh` 的 `$TASK_DIR/${phase}-*.md` scan | **不相关**：pruning.sh 不扫描 SCOPE+ |
| Bug 1: inject-card 新增 exit 1 | `pre-commit-gate.sh` 的卡片 hash 校验段（pre-commit-gate.sh:154-207）| **不相关**：inject-card 不在此调用链中，它是独立 CLI 工具 |
| Bug 4: P5 WARNING | `pre-commit-gate.sh` 或 `gate-result.sh` | **无需修改**：check-gate.sh 被 pre-commit-gate.sh 调用，内部 WARNING 新增不改变调用接口 |

**结论**：ALIGNED。除 check-retrospective.sh 的一个低影响潜在一致性改进外，无遗漏传播路径。

---

### A4: 测试覆盖

计划提供 6 个新测试用例：

| Bug | 测试 | 覆盖内容 |
|-----|------|---------|
| 1 | `dispatch-context 无 AGATE_CARD 占位符时 exit 1（非静默成功）` | 缺失占位符 → exit 1，输出含"未找到"+"占位符" |
| 2 | `dispatch-context 文件中的 [SCOPE+] 字面引用不触发检查` | dispatch-context 含 SCOPE+ → exit 0（被跳过） |
| 3a | `CHANGELOG 含短前缀 T060 但 task_id 为完整目录名时正确匹配` | T060-xxx as task_id, CHANGELOG has `- T060: ...` → exit 0 |
| 3b | `CHANGELOG 含 T0601 时短前缀 T060 不误匹配` | T060-xxx as task_id, CHANGELOG has `- T0601: ...` → exit 1 |
| 3c | `CHANGELOG 含完整 task_id 时固定字符串 fallback 生效` | T060-xxx as task_id, CHANGELOG has `- T060-xxx: ...` → exit 0 |
| 4 | `P2 gate_commands.P5 多命令时 P5 输出 WARNING` | P2-design.md has 3 gate_commands.P5 commands → P5 exit 2 + WARNING output |

**边界分析**：
- Bug 1：只测了"无占位符"一个场景。占位符存在但格式错误（如缺少 END）、多个 dispatch-context 文件时部分缺占位符——未覆盖。但核心场景已覆盖。**可接受**。
- Bug 2：只测了 dispatch-context 有 SCOPE+ 时 skip。未测"dispatch-context 无 SCOPE+ 且阶段产出有 SCOPE+"的正常路径（已有 SC.4/SC.5 覆盖）。
- Bug 3a：测试 T060 前缀匹配 `- T060: 条目` 格式——**可工作**。
- Bug 3b：测试 T0601 不误匹配 T060——**可工作**（`T0601` 中 `T060` 后跟 `1`，不在后缀集中）。
- Bug 3c：测试完整 task_id 在 CHANGELOG 中匹配——**与计划代码矛盾，见 A1.3 MISALIGNED**。计划代码无 fallback，此测试会失败。
- Bug 4：测试 3 个 gate_commands 触发 WARNING。未测 false positive 场景（非 P5 相关 bullet 被计入）。

**关键事项**：角色定义（protocol-alignment-review.md:23）要求「**必须附最近一次 bats 全量实跑输出（含 passed/failed 计数），无实跑输出的 √ 视为无效**」。当前为计划阶段审查，所有测试代码仅为设计草案，尚未实现，无实跑输出。

**结论**：**NEEDS_HUMAN_REVIEW**。测试设计覆盖核心边界，但：(1) 测试 3c 与计划代码矛盾需修复；(2) 无实跑输出——角色规则要求实际 bats 运行结果。实施后必须跑全量 bats 并附上 passed/failed 计数。

`[HUMAN_CONFIRMED: 待实施后补充 bats 实跑输出]`

---

### A5: 下游影响 + 文档传播

**破坏性变更评估**：

| 改动 | 破坏性分析 |
|------|-----------|
| Bug 1: inject-card exit 1 on missing placeholder | **非破坏性**。原行为是 bug（静默成功但实际未注入），修复后正确报错。调用方如果依赖 exit 0 会受影响，但原来"成功"是虚假的——修复暴露问题而非制造问题 |
| Bug 2: SCOPE+ skip dispatch-context | **非破坏性**。原本 dispatch-context 中的 SCOPE+ 被误检拦截（false positive gate block），修复后不再拦截。对用户来说是放松了限制 |
| Bug 3: CHANGELOG 短前缀搜索 | **非破坏性**。原来只接受完整 task_id，修复后也接受短前缀。这是放松限制（更多 CHANGELOG 格式被接受），不是收紧。向后兼容（完整 task_id 仍可匹配——但需见 A1.3 fallback 问题） |
| Bug 4: P5 WARNING | **非破坏性**。新增 WARNING 输出，P5 gate 仍恒 exit 2。对已通过 gate 的项目无影响 |

**版本号判定**（plan:331）：
> 「patch bump：v0.15.0→v0.15.1」

与 WORKFLOW.md:7 的版本语义一致：「规则新增/调整升 minor，破坏性变更升 major」。Bug fix + WARNING 增强属于 patch 范围。**ALIGNED**。

**CHANGELOG 标注**：计划声明需标注 4 项改动。已纳入实施步骤。**ALIGNED**。

**文档传播**：计划未提及 `LIMITATIONS.md`、`orchestrator-template.md`、`role-system.md`、`WORKFLOW.md`、`state-machine.md` 需要修改。经验证，这些文件不涉及本次改动的具体规则描述（P5 WARNING 的文档已经在 phase-cards 中，其他改动是脚本行为的 bug 修复）。**ALIGNED**。

**结论**：ALIGNED。无破坏性变更，版本号判定正确，CHANGELOG 标注计划充分。

---

### A6: 锚点表覆盖

CHECK 9 锚点表（check-protocol-consistency.py:444-586）包含以下与本次改动相关的条目：

| 锚点 | 涉及脚本 | 受本次改动影响 |
|------|---------|--------------|
| `"SCOPE+ 追踪"` → `check-scope-resolved.sh` → keyword `SCOPE_RESOLVED` | Bug 2 | `SCOPE_RESOLVED` 关键词仍在文件中 ✓ |
| `"P8 CHANGELOG 检查"` → `check-changelog.sh` → keyword `CHANGELOG` | Bug 3 | `CHANGELOG` 关键词仍在文件中 ✓ |
| `"DESIGN_GAP 配对"` → `check-gate.sh` → keyword `DESIGN_GAP` | Bug 4 | 关键词未移除，新增 WARNING 不违反锚点 ✓ |

**未覆盖项**：
- `agate-inject-card.sh` 未纳入锚点表。它是 CLI 工具（非 `check-*.sh` 模式），CHECK 9 反向覆盖扫描（check-protocol-consistency.py:635-662）只检查 `check-*.sh` + `pre-commit-gate.sh`，故不会 flag 它。新增的 exit 1 行为无需新增锚点——它不是 gate 检查脚本。
- Bug 4 P5 WARNING 在 check-gate.sh 中的新增行为（`P5_CMD_COUNT` / `全量` 关键词）未有独立锚点。这是 check-gate.sh 的内部增强，不改变其归类（已有 4 个 check-gate.sh 锚点覆盖 P2/P1/P7 gate 逻辑）。如果未来 P5 WARNING 升级为 exit 1 硬检查，需要新增锚点。

**结论**：ALIGNED。锚点表无需更新，计划步骤 5 落地后运行 `check-protocol-consistency.py` 确认 0 ERROR 即可。

---

### A7: 设计原则一致性

逐 ADR 检查：

**ADR-001（隔离性）**：Plan:260——Bug 1 的 exit 1 修复使注入脚本更可靠地报告失败，不违反主 Agent 编排职责。Bug 2-4 改进 gate 脚本准确性和覆盖范围，不涉及主 Agent 写产出。**ALIGNED**。

**ADR-002（可判定性）**：Bug 1 从"静默成功"改为"显式 exit 1"——**增强可判定性**（原来假绿灯）。Bug 2 消除 false positive——**提高判定准确性**。Bug 3 从严格固定字符串改为灵活正则——语义上仍是"CHANGELOG 含 task_id"的可判定检查。Bug 4 新增 WARNING——不改变 gate 的 exit 0/1/2 判定框架。**ALIGNED**。

**ADR-003（最小约定）**：改动仅涉及 bash/python（agate 已有依赖），不引入新运行时依赖。Bug 4 的 grep 模式在 P2-design.md 中搜索 `^\s+- `，不绑定任何技术栈。**ALIGNED**。

**ADR-004（安全网分层）**：Bug 4 P5 WARNING 新增 hook 层的检测（pre-commit hook → check-gate.sh → P5 WARNING），加固了 hook 层的提醒能力。Bug 1-3 提高了第一层防线（hook）的准确性。符合多层防线设计。**ALIGNED**。

**ADR-005（改动性质决定流程）**：不相关（本次改动是 agate 协议自身，不是项目任务）。**ALIGNED**。

**ADR-006（双层角色）**：不相关（脚本改动不涉及角色文件）。**ALIGNED**。

**结论**：ALIGNED。所有改动符合已记录的架构决策，无新增 ADR 需求。

---

## 闭环建议

| # | 问题 | 优先级 | 修复方向 |
|---|------|--------|---------|
| A1.3 | Bug 3 计划代码缺少 fallback，测试 3c 会失败 | **必须修** | 补齐 fallback：短前缀 regex 失败后尝试 `grep -qF "$TASK_ID"`；或扩展 regex 后缀集 `( |:|-|$|,)` |
| A4 | 无 bats 实跑输出 | **实施后必做** | 实现测试代码后跑全量 bats，将 passed/failed 计数补入本报告 |

---

## 审查时间

2026-07-21。审查范围：计划文件 + 11 个协议/脚本/测试源文件。

## 最终判定

**1 MISALIGNED**（A1.3：Bug 3 计划代码缺 fallback 与计划文字及测试 3c 矛盾）、**1 NEEDS_HUMAN_REVIEW**（A4：无实跑输出）。其余 5 项 ALIGNED。

修复 A1.3 后 + A4 获得实跑输出确认后，计划可推进实施。
