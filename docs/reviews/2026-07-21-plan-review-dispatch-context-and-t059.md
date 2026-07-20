# 独立评审：dispatch-context plan v8 + t059-retro-improvements plan

> 评审者：主 Agent（换模型后重新独立评审）
> 日期：2026-07-21
> 基线：283 bats 全绿 / consistency 0 ERROR / shellcheck 0
> 评审方式：逐行读 plan，对照当前仓库文件验证断言（行号/文件存在性/逻辑）

---

## Plan A: dispatch-context single-source v8

### BLOCKER

**A-B1: Task 5 Step 3 基于错误假设**（P6:63/P7:75 不是 `dispatch-context.md`）

Plan 写："P6:63 和 P7:75 的 `dispatch-context.md` -> `dispatch-context-{role}.md`"

实际：
- P6:63 = `check-p6-provenance.sh $TASK_DIR # 证据-结论对应 / dispatch-context审计 / BDD对照`（机制描述，无 `.md`）
- P7:75 = `3. dispatch-context 为 subagent 提供摘要，无需逐文件全文注入`（无 `.md`）

两个位置都不是 `dispatch-context.md` 旧格式引用，无需替换。Plan A 自己的"全文替换策略"节明确说"机制描述不需要改文件名格式"，但 Task 5 Step 3 违反了这条原则。

**修复**：删除 Task 5 Step 3，或改为"确认 P6:63 和 P7:75 是机制描述，不改"。

### MAJOR

**A-M1: Task 8 说"7 个执行角色文件"但实际只有 6 个有 dispatch-context 引用**

Plan 写："执行角色（7 个文件）- 每个文件：1. 删除'输入'节中 dispatch-context 路径引用"

实际：7 个执行角色文件中，`vision-analyst.md` 无 dispatch-context 引用（grep 0 匹配）。只需改 6 个：analyst/architect/consistency-reviewer/implementer/test-designer/verifier。

**修复**：Task 8 Step 1 改为"6 个文件"，注明 vision-analyst.md 无引用只需确认。

**A-M2: Task 11 Step 1 DC.5 语义反转描述不够明确测试文件路径**

Plan 写："DC.5 改为 P5 强制测试（语义反转：从'不拦截'变为'拦截'）"

但未说明 DC.5 当前测试的是什么场景。实施者需要先读现有 DC.5 才能理解"反转"的含义。

**修复**：Task 11 Step 1 DC.5 补充当前测试内容描述。

**A-M3: Task 2 Step 1 "输入节（行 22-27）"行号需验证**

Plan 写 dispatch-prompt.md "输入"节在行 22-27。实际行 22-27 确实是"输入"节。但 plan 同时说"删除 P0-brief/上一阶段产出/WORKFLOW.md/dispatch-context 4 行"，这 4 行在 23-26 行。OK，行号正确。

**修复**：无需修复，确认正确。

**A-M4: Task 6 Step 1 P4 逻辑描述模糊**

Plan 写："P4 用代码文件判定（已有逻辑不变）"

实际 pre-commit-gate.sh 第 190-194 行 P4 判定逻辑：`grep -qvE '\.(md|yaml)$|^\.state'`。Plan 说"不变"但未明确引用现有逻辑位置，实施者可能误改。

**修复**：Task 6 Step 1 P4 补充"见 pre-commit-gate.sh 第 190-194 行现有逻辑"。

### MINOR

**A-m1: Task 3 Step 6 行号 694/716/910/575 已验证正确**

确认无误。

**A-m2: Task 4 Step 1 行号 56/64/99 已验证正确**

确认无误。但 plan 说"第 56 行裸引用 dispatch-context"实际第 56 行是"不追加到 dispatch-context"（机制描述），应改为"dispatch-context"（无 `.md`）。Plan 描述方向正确但用词"按上下文更新"模糊。

**修复**：Task 4 Step 1 第 56 行明确改为"机制描述不改，保留 dispatch-context 无 `.md` 后缀"。

**A-m3: v7->v8 变更摘要提到"Task 3 Step 7 删除排除说明"但 Task 3 Step 7 仍提到"手动检查"**

变更摘要说"删除排除说明（评审 MINOR：排除无必要）"，但 Task 3 Step 7 仍写"替换后手动检查 282-340 行确认无误替换即可"。这是残留的排除说明痕迹。

**修复**：Task 3 Step 7 删除"替换后手动检查 282-340 行"句。

### 评审结论

Plan A 有 1 个 BLOCKER（Task 5 Step 3 错误假设）+ 3 个 MAJOR + 3 个 MINOR。修复后可执行。

---

## Plan B: t059-retro-improvements

### BLOCKER

**B-B1: Task 5 行号完全错误（check-gate.sh 第 232-271 行不存在）**

Plan 写："文件：`agate/scripts/check-gate.sh`（第 232-271 行 P8 分支）"

实际：check-gate.sh 总共 219 行，P8 分支在第 177-215 行。Plan 的所有行号引用（246-256、252-256）都超出文件范围。

**修复**：Task 5 所有行号更新：232-271 -> 177-215，246-256 -> 190-201，252-256 -> 198-201。

**B-B2: Task 5 实现代码块缩进混乱导致不可执行**

Plan Task 5 的实现代码块（第 213-241 行）混合了空格和 tab 缩进，且 `CACHED_VERSION` 行用空格、`RECENT_VERSION` 块用 4 空格。直接复制会因缩进不一致导致 bash 语法错误。

**修复**：统一代码块缩进为 2 空格或 tab，明确这是伪代码非可直接执行。

### MAJOR

**B-M1: Task 4 代码块残缺（python 代码片段未包裹在代码块内）**

Plan Task 4 第 170-178 行：`用 python3 替换 AGATE_CARD 块...` 后直接跟 `with open(dc) as f: text = f.read()` 等 python 代码，但这些代码没有包裹在 ```bash 或 ```python 代码块中，且缺少开头的 `python3 -c "`。实施者无法判断这是伪代码还是完整脚本。

**修复**：Task 4 重新组织代码块，明确区分 bash 脚本体和 python 内嵌逻辑，用完整可执行的 heredoc 或临时文件方式。

**B-M2: Task 7 "所有 exit 1 必须输出错误消息"范围过大**

Plan 写"审计所有 gate 脚本的 exit 1 路径"，但 agate 有 10+ 个 gate 脚本，每个可能有多个 exit 1。Plan 只列了 5 个重点增强位置，其余脚本的审计方式未说明。

**修复**：Task 7 明确"重点增强这 5 个位置，其余脚本只做 grep 审计确认有 stderr 输出"。

**B-M3: Task 1 行号 46-58 实际是 42-63**

Plan 写"第 46-58 行的 PASS 行解析逻辑"，实际解析逻辑在 42-63 行（46-58 是核心但不是全部）。

**修复**：Task 1 行号更新为 42-63。

**B-M4: Task 2 行号 73-83 实际是 73-83（正确）但 76-83 描述不准**

Plan 写"第 76-83 行对所有 ≤1024 字节文件 exit 1"。实际 76-79 是循环统计，80-83 是判定 exit 1。描述模糊。

**修复**：Task 2 明确"76-79 统计 EMPTY_COUNT，80-83 判定 exit 1"。

**B-M5: Task 8 与 Task 13 重复且依赖关系混乱**

Task 8 (G8) 说"P8 subagent 不 commit + bump 由主 Agent 执行"。Task 13 (P5) 说"bump 推迟到 gate 后"。两者都改 P8-release.md 和 dispatch-protocol.md，范围重叠。

Plan 在 Task 13 说"Task 13 只补充 bump 时机（gate 后），Task 8 已覆盖 subagent 不 commit + bump 由主 Agent 执行"，但实际 Task 8 已经说了"bump-version 由主 Agent 亲自执行"。Task 13 没有新增内容。

**修复**：合并 Task 8 和 Task 13，或 Task 13 明确只改 P8-release.md 的执行方式描述（不重复 Task 8 的内容）。

### MINOR

**B-m1: Task 6 行号 14-20 实际是 14-20（正确）**

确认无误。

**B-m2: Plan 标题写"v7"但正文引用"v8"**

Plan 第 13 行"本计划独立于 dispatch-context plan v7"，第 19 行"与 dispatch-context plan v8 的交叉"。应统一为 v8。

**修复**：第 13 行 v7 -> v8。

**B-m3: Task 10 依赖 Task 1 但 Task 1 改的是解析逻辑不是格式规范**

Plan 写"Task 10 依赖 Task 1（G1 provenance 解析改进后，PASS 行格式可更灵活）"。但 Task 10 是"P6 PASS 行格式标准化"（文档规范），Task 1 是脚本解析逻辑。文档规范不依赖脚本实现。

**修复**：Task 10 依赖改为"无（文档规范独立）"。

### 评审结论

Plan B 有 2 个 BLOCKER（行号错误 + 代码块残缺）+ 5 个 MAJOR + 3 个 MINOR。修复后可执行。

---

## 交叉依赖评审

Plan B Task 4 (G4 inject-card) 与 Plan A 的文件名变更强耦合。Plan B 已标注此依赖，处理方式合理（glob 匹配）。

**建议实施顺序**：Plan A 先（文件名变更），Plan B 后（基于新文件名）。这样 Plan B Task 4 直接写 glob 版本，无需过渡期兼容。

---

## 总评审结论

| Plan | BLOCKER | MAJOR | MINOR | 结论 |
|------|---------|-------|-------|------|
| A (dispatch-context v8) | 1 | 3 | 3 | 修复后可执行 |
| B (t059-retro) | 2 | 5 | 3 | 修复后可执行 |

**实施顺序**：Plan A 先 -> Plan B 后。

**修复优先级**：BLOCKER 必须修复，MAJOR 建议修复，MINOR 可选。
