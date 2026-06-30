# Phase 2B-2+2B-3 计划评审

> 评审对象：`docs/plans/hardening-phase2b2-2b3-2026-06-30.md`
> 评审日期：2026-06-30
> 评审方法：逐 Task 通读 + 逻辑推演 + 与现有协议对照

---

## 总体判断

**方向正确，覆盖全面。但有 2 个 🔴 阻断级 bug（shell 变量注入 Python + 裁剪检测逻辑反转），2 个 🟠 高优先级（触发条件缺口 + author 检查的路径问题），2 个 🟡 中优先级。**

---

## 🔴 阻断级

### R1：check-pruning.sh 和 check-p2-review.sh 的 Python 代码用 shell 变量直接拼接文件路径——含空格或特殊字符路径会崩溃

**位置**：Task 1 `check-pruning.sh` Step 1, Task 2 `check-p2-review.sh` Step 1

```bash
# check-pruning.sh
RISK_LEVEL=$(python3 -c "
import re
with open('$P1_FILE') as f:
    text = f.read()
...
" 2>/dev/null || echo "")
```

**问题**：`$P1_FILE` 是绝对路径（如 `/home/kity/.agate/docs/tasks/T001/P1-requirements.md`），直接 shell 展开到 Python 字符串里。如果路径含单引号或空格，Python 代码语法错误。

Phase 2A 补充计划已经修过这个问题（M2：用环境变量传参），但 Phase 2B-2 的脚本又犯了同样的错误。

**修法**：所有 Python 调用统一用环境变量传参（和 check-state-yaml.sh 一致）：

```bash
RISK_LEVEL=$(P1_FILE="$P1_FILE" python3 -c "
import re, os
with open(os.environ['P1_FILE']) as f:
    text = f.read()
...
" 2>/dev/null || echo "")
```

**影响范围**：check-pruning.sh 有 4 处 Python 调用，check-p2-review.sh 有 1 处，check-retrospective.sh 有 1 处。全部需要改。

### R2：check-pruning.sh 裁剪检测逻辑反转——`grep -qvE '\bP2\b'` 在 P2 **存在**于 phases 列表时返回 0（通过），导致"声明了 P2 但被认为裁剪了"

**位置**：Task 1 `check-pruning.sh` Step 1

```bash
# 检查 2：裁剪 P2 的条件
if echo "$PHASES_DECLARED" | grep -qvE '\bP2\b'; then
    # P2 被裁剪
```

**问题**：`grep -qvE '\bP2\b'` 的语义是"如果 PHASES_DECLARED 不匹配 P2，返回 0"。但 `PHASES_DECLARED` 的值是 `P1 P3 P4 P5 P6`（空格分隔）。当 phases 包含 P2 时（`P1 P2 P4 P5`），`grep -qvE '\bP2\b'` 会逐行检查——如果输出只有一行且包含 P2，`grep -v` 返回 1（不匹配），整个 `grep -qvE` 返回非 0。**这恰好是对的**——P2 存在时不进入"被裁剪"分支。

等等，让我重新分析。`echo "P1 P2 P4 P5" | grep -qvE '\bP2\b'`：grep -v 输出不匹配的行。`echo` 输出一行 `P1 P2 P4 P5`，这一行匹配 `\bP2\b`，所以 `grep -v` 没有输出，返回 1。`grep -q` 不输出，返回 1。`if` 条件为 false。**所以 P2 存在时不进入裁剪分支——这是正确的。**

但 `echo "P1 P3 P4 P5" | grep -qvE '\bP2\b'`：这一行不匹配 `\bP2\b`，`grep -v` 输出这一行，返回 0。`if` 条件为 true。**进入裁剪分支——这也是正确的。**

**经重新分析，逻辑正确。R2 撤销。** 但 `\b` 在某些 grep 实现里不支持（POSIX grep 用 `\<` 和 `\>`）。建议用 `grep -qw` 更可移植：

```bash
if echo "$PHASES_DECLARED" | grep -qw 'P2'; then
    : # P2 存在，不被裁剪
else
    # P2 被裁剪
fi
```

**修正为 🟡 中优先级**：`\b` 可移植性问题。

---

## 🟠 高优先级

### O1：Task 5 集成位置——新检查在 `write_gate_result` 之后，但 `write_gate_result` 之后紧跟 `# 8. gate 结果处理` 的 case 语句，新检查插入后会改变 exit 语义

**位置**：Task 5 Step 1

```bash
write_gate_result "$PHASE" "$TASK_ID" "$GATE_EXIT" "$GATE_OUTPUT"

# 5.5 裁剪条件检查（P2.7-P2.9）
if [ -n "$TASK_ID" ] && [ -d "$TASK_DIR" ]; then
    bash "$REPO_ROOT/scripts/check-pruning.sh" "$TASK_DIR" || exit 1
fi

...

# 8. gate 结果处理
case "$GATE_EXIT" in
    0) echo "GATE $PHASE: 通过" >&2; exit 0 ;;
    1) echo "GATE $PHASE: 未通过" >&2; echo "$GATE_OUTPUT" >&2; exit 1 ;;
    2) echo "GATE $PHASE: 需主 Agent 手动判断" >&2; echo "$GATE_OUTPUT" >&2; exit 0 ;;
esac
```

**问题**：如果 GATE_EXIT=1（gate 未通过），新的裁剪检查会在 gate 结果处理之前执行。如果裁剪检查也失败了（exit 1），用户看到的是裁剪错误而不是 gate 错误。但 gate 错误才是更根本的问题。

**更严重的是**：如果 GATE_EXIT=1，gate 已经失败了，但裁剪检查可能因为 P1 文件不存在（如 P1 还没创建）而 exit 2（不拦截）或 exit 1（拦截）。如果裁剪检查 exit 1，用户看到的是"裁剪条件不满足"而不是"gate 未通过"——错误信息误导。

**修法**：新检查应该在 gate 结果处理**之后**（case 语句的 exit 0 分支之后），只在 gate 通过时才检查裁剪条件。或者更简单：把新检查放在 CHANGELOG 检查和 P6 证据检查之间（它们都是 gate 通过后的附加检查）。

但更合理的逻辑是：**裁剪条件检查应该在 gate 运行之前**——因为裁剪决定了哪些阶段需要跑 gate。如果裁剪不合法，不应该跑 gate。但这需要重写触发逻辑。

**建议**：把新检查放在 `write_gate_result` 之后、`# 8. gate 结果处理` 之前，但只在 GATE_EXIT != 1 时执行：

```bash
# 5.5 裁剪条件检查（P2.7-P2.9）——gate 未通过时不检查（gate 错误优先）
if [ "$GATE_EXIT" != "1" ] && [ -n "$TASK_ID" ] && [ -d "$TASK_DIR" ]; then
    bash "$REPO_ROOT/scripts/check-pruning.sh" "$TASK_DIR" || exit 1
fi
```

### O2：check-p2-review.sh 的 `git log -- "$P2_REVIEW"` 路径问题——绝对路径 vs 相对路径

**位置**：Task 2 Step 1

```bash
REVIEW_AUTHOR=$(git log -1 --format='%an' -- "$P2_REVIEW" 2>/dev/null || echo "")
```

**问题**：`$P2_REVIEW` 是 `$TASK_DIR/P2-review.md`，而 `$TASK_DIR` 是 `$REPO_ROOT/$AGATE_TASKS_DIR/$TASK_ID`（绝对路径）。`git log -- <path>` 接受绝对路径吗？

实测：`git log -- /home/kity/.agate/docs/tasks/T001/P2-review.md` 在仓库根目录运行时**可以工作**——git 会把绝对路径转换为相对仓库根的路径。但和 Phase 1+2A 反复出现的路径问题一样，不够健壮。

**修法**：用相对路径。在 pre-commit-gate.sh 里传递相对路径，或在 check-p2-review.sh 里转成相对路径：

```bash
# 转成相对仓库根的路径
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
P2_REVIEW_REL=$(realpath --relative-to="$REPO_ROOT" "$P2_REVIEW" 2>/dev/null || echo "$P2_REVIEW")
REVIEW_AUTHOR=$(git log -1 --format='%an' -- "$P2_REVIEW_REL" 2>/dev/null || echo "")
```

---

## 🟡 中优先级

### M1：check-pruning.sh 的 `\b` word boundary 可移植性

**位置**：Task 1，`grep -qvE '\bP2\b'`

`\b` 在 GNU grep 中支持，但 POSIX grep 不保证。建议用 `grep -qw`（--word-regexp + quiet），更可移植：

```bash
if echo "$PHASES_DECLARED" | grep -qw 'P2'; then
    : # P2 存在
else
    # P2 被裁剪
fi
```

### M2：check-scope-resolved.sh 扫描 `P*.md` 但 SCOPE+ 可能出现在非 P 前缀文件里

**位置**：Task 3 Step 1

```bash
for f in "$TASK_DIR"/P*.md; do
```

**问题**：SCOPE+ 标记可能出现在 task 目录下的任何 .md 文件里（如 dispatch-context.md、PAUSED-resolution.md）。只扫 `P*.md` 会漏掉这些文件。

**修法**：扫描所有 .md 文件，或明确列出可能的文件：

```bash
for f in "$TASK_DIR"/*.md; do
```

---

## 确认正确的部分

**风险等级定义合理**：low/medium/high 三级，与 PeekView 实战数据对齐。

**裁剪条件阈值来自实战**：BDD ≤ 10 可裁 P2，来自 PeekView 数据，有明确标注。

**SCOPE_RESOLVED 格式设计正确**：`[SCOPE_RESOLVED: from P4-implementation.md]` 含来源文件，可追溯。

**复盘异常触发不中止 commit**：正确——复盘是学习行为不是质量 gate。

**协议改动覆盖全面**：P1 模板、WORKFLOW.md、dispatch-protocol.md、state-machine.md 四个文件都有对应改动。

---

## 修复优先级汇总

| # | 问题 | 严重度 | 修复 |
|---|------|--------|------|
| R1 | Python 代码 shell 变量注入 | 🔴 | 所有 Python 调用用环境变量传参 |
| O1 | 新检查插入位置改变 exit 语义 | 🟠 | gate 失败时不跑裁剪检查 |
| O2 | git log 绝对路径 | 🟠 | 用相对路径 |
| M1 | \b 可移植性 | 🟡 | 改用 grep -qw |
| M2 | SCOPE+ 扫描遗漏非 P 前缀文件 | 🟡 | 扫描 *.md |

**建议执行顺序**：R1（全部脚本统一改）→ O1 + O2（集成时改）→ M1 + M2（实现时改）。
