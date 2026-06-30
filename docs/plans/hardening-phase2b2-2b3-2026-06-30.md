# Phase 2B-2 + 2B-3 实施计划：流程选择硬约束 + 非 agate 任务门槛

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 hardening-roadmap Phase 2B-2（P2.7-P2.12 流程选择硬约束）和 2B-3（P2.13-P2.14 非 agate 任务门槛），让裁剪决策、P2 评审派发、SCOPE+ 处理、复盘触发从"主 Agent 自觉"变成"协议字段 + hook 检查"。

**Architecture:** P1-requirements.md 增加 `risk_level` 字段；WORKFLOW.md 适用边界表增加"复杂度 × 风险"矩阵；hook 检查裁剪条件与 risk_level 匹配；hook 检查 high risk 任务的 P2 评审 author 非主 Agent；SCOPE+ 追踪用 [SCOPE_RESOLVED] 标记；复盘异常触发用脚本检测异常模式。

**来源**：`docs/hardening-roadmap.md` Phase 2B-2 (P2.7-P2.12) + 2B-3 (P2.13-P2.14)

**评审修订**（hardening-phase2b2-2b3-plan-review-20260630.md，5 项全部采纳）：
- R1: Python 代码 shell 变量注入 → 所有 Python 调用用环境变量传参（Task 1-4）
- O1: 新检查插入位置改变 exit 语义 → gate 失败时不跑裁剪检查（Task 5）
- O2: git log 绝对路径 → 用相对路径（Task 2）
- M1: `\b` 可移植性 → 改用 `grep -qw`（Task 1）
- M2: SCOPE+ 扫描遗漏非 P 前缀文件 → 扫描 `*.md`（Task 3）

**涉及协议文件**：
- `WORKFLOW.md` — 适用边界表（L109-157）、P2 评审角色（L180）
- `dispatch-protocol.md` — 门槛表（L568-577）、SCOPE+ 扫描（L609）
- `state-machine.md` — 裁剪跳过转移（L158-175）、SCOPE+ 转移（L177-186）
- `assets/templates/task-files.md` — P1-requirements.md 模板（L119-161）
- `scripts/pre-commit-gate.sh` — 集成新检查
- `scripts/check-pruning.sh` — 新建：裁剪条件检查
- `scripts/check-p2-review.sh` — 新建：P2 评审 author 检查
- `scripts/check-scope-resolved.sh` — 新建：SCOPE+ 追踪检查
- `scripts/check-retrospective.sh` — 新建：复盘异常触发

---

## 文件结构

| 文件 | 责任 | 创建/修改 |
|------|------|-----------|
| `scripts/check-pruning.sh` | 裁剪条件检查：P1 risk_level + phases 声明匹配 | 创建 |
| `scripts/check-p2-review.sh` | high risk 任务的 P2 评审 author 非主 Agent | 创建 |
| `scripts/check-scope-resolved.sh` | SCOPE+ 有对应 [SCOPE_RESOLVED] 标记 | 创建 |
| `scripts/check-retrospective.sh` | 异常模式检测 → 复盘提醒 | 创建 |
| `scripts/pre-commit-gate.sh` | 集成 4 个新检查 | 修改 |
| `WORKFLOW.md` | 适用边界表加风险矩阵 + P2 评审派发条件 | 修改 |
| `dispatch-protocol.md` | 门槛表加 risk_level + 裁剪条件 + SCOPE_RESOLVED | 修改 |
| `state-machine.md` | 裁剪跳过规则加 risk_level 条件 + SCOPE_RESOLVED 转移 | 修改 |
| `assets/templates/task-files.md` | P1 模板加 risk_level + override 字段 | 修改 |

---

## Task 1: check-pruning.sh 裁剪条件检查

**Files:**
- Create: `scripts/check-pruning.sh`

**协议依据**（roadmap P2.7-P2.8 + P2.9）：
- P1-requirements.md 必须有 `risk_level: low|medium|high` 字段
- 裁剪 P2 需 risk_level=low AND BDD ≤ 10
- 裁剪 P6 不可（除非 no_behavior_change: true）
- 裁剪 P7 需改动文件数 ≤ 5
- 裁剪声明与实际执行不一致时 P1 必须有 override 字段

- [ ] **Step 1: 写 check-pruning.sh**

```bash
#!/usr/bin/env bash
# check-pruning.sh — 裁剪条件检查（P2.7-P2.9）
# 检查 P1-requirements.md 的 risk_level + phases 声明是否符合裁剪条件
# exit 0 = 通过; exit 1 = 裁剪条件不满足; exit 2 = 无 P1 文件

set -euo pipefail

TASK_DIR="${1:?用法: check-pruning.sh TASK_DIR}"
P1_FILE="$TASK_DIR/P1-requirements.md"

[ ! -f "$P1_FILE" ] && exit 2

# R1 修复：所有 Python 调用用环境变量传参，避免 shell 变量注入
# 从 P1 提取 risk_level 和 phases
RISK_LEVEL=$(P1_FILE="$P1_FILE" python3 -c "
import re, os
with open(os.environ['P1_FILE']) as f:
    text = f.read()
m = re.search(r'risk_level:\s*(low|medium|high)', text)
print(m.group(1) if m else '')
" 2>/dev/null || echo "")

PHASES_DECLARED=$(P1_FILE="$P1_FILE" python3 -c "
import re, os
with open(os.environ['P1_FILE']) as f:
    text = f.read()
m = re.search(r'phases:\s*\[([^\]]+)\]', text)
if m:
    phases = [p.strip() for p in m.group(1).split(',')]
    print(' '.join(phases))
" 2>/dev/null || echo "")

# override 字段（裁剪声明与执行不一致时回写）
HAS_OVERRIDE=$(grep -c '^override:' "$P1_FILE" 2>/dev/null || echo 0)

# BDD 条目数（从 ## 3. BDD 验收条件 区提取 AC 条目）
BDD_COUNT=$(P1_FILE="$P1_FILE" python3 -c "
import re, os
with open(os.environ['P1_FILE']) as f:
    text = f.read()
m = re.search(r'## 3\. BDD 验收条件(.*?)(?=## 4\.|## 5\.|\Z)', text, re.S)
if m:
    items = re.findall(r'^- (?:AC|BDD-)\d+', m.group(1), re.M)
    print(len(items))
else:
    print(0)
" 2>/dev/null || echo 0)

ERRORS=""

# 检查 1：risk_level 必须存在
if [ -z "$RISK_LEVEL" ]; then
    ERRORS="${ERRORS}P1-requirements.md 缺 risk_level 字段\n"
fi

# M1 修复：用 grep -qw 替代 \b，更可移植
# 检查 2：裁剪 P2 的条件
if ! echo "$PHASES_DECLARED" | grep -qw 'P2'; then
    # P2 被裁剪
    if [ "$RISK_LEVEL" != "low" ]; then
        ERRORS="${ERRORS}裁剪 P2 需 risk_level=low，实际=${RISK_LEVEL}\n"
    fi
    if [ "$BDD_COUNT" -gt 10 ]; then
        ERRORS="${ERRORS}裁剪 P2 需 BDD ≤ 10，实际=${BDD_COUNT}\n"
    fi
fi

# 检查 3：裁剪 P6 的条件（不可裁，除非 no_behavior_change）
if ! echo "$PHASES_DECLARED" | grep -qw 'P6'; then
    if ! grep -q 'no_behavior_change:\s*true' "$P1_FILE" 2>/dev/null; then
        ERRORS="${ERRORS}P6 不可裁剪（除非 no_behavior_change: true）\n"
    fi
fi

# 检查 4：裁剪 P3 的条件
if ! echo "$PHASES_DECLARED" | grep -qw 'P3'; then
    if [ "$RISK_LEVEL" = "high" ]; then
        ERRORS="${ERRORS}高风险任务不可裁剪 P3\n"
    fi
fi

if [ -n "$ERRORS" ]; then
    echo "GATE PRUNING: 裁剪条件不满足：" >&2
    printf "$ERRORS" | while IFS= read -r line; do
        [ -n "$line" ] && echo "  - $line" >&2
    done
    exit 1
fi

exit 0
```

- [ ] **Step 2: 验证语法 + 测试**

Run: `bash -n scripts/check-pruning.sh`

```bash
# 测试合法裁剪：low risk + BDD ≤ 10 + 裁剪 P2
mkdir -p /tmp/test-task
cat > /tmp/test-task/P1-requirements.md <<'EOF'
## 3. BDD 验收条件
- AC1: Given x When y Then z

## 5. 裁剪说明
risk_level: low
phases: [P1,P3,P4,P5,P6]
- 跳过 P2 理由：纯 UI 小改动
EOF
bash scripts/check-pruning.sh /tmp/test-task
echo "exit: $?"
```

Expected: `exit: 0`

```bash
# 测试非法裁剪：high risk 裁剪 P2
cat > /tmp/test-task/P1-requirements.md <<'EOF'
## 3. BDD 验收条件
- AC1: Given x When y Then z

## 5. 裁剪说明
risk_level: high
phases: [P1,P3,P4,P5,P6]
- 跳过 P2 理由：觉得不需要
EOF
bash scripts/check-pruning.sh /tmp/test-task 2>&1
echo "exit: $?"
```

Expected: exit 1, 输出 "裁剪 P2 需 risk_level=low"

- [ ] **Step 3: Commit**

```bash
git add scripts/check-pruning.sh
git commit -m "feat(hardening): check-pruning.sh 裁剪条件检查

P2.7-P2.8 risk_level + BDD 数 + 裁剪条件 hook 验证
P2.9 override 字段检查"
```

---

## Task 2: check-p2-review.sh P2 评审 author 检查

**Files:**
- Create: `scripts/check-p2-review.sh`

- [ ] **Step 1: 写 check-p2-review.sh**

```bash
#!/usr/bin/env bash
# check-p2-review.sh — P2 评审派发强制（P2.10）
# risk_level=high 时，P2-review.md 的 git author 必须非主 Agent
# exit 0 = 通过; exit 1 = 评审未独立; exit 2 = 无 P2 文件或非 high risk

set -euo pipefail

TASK_DIR="${1:?用法: check-p2-review.sh TASK_DIR}"
P1_FILE="$TASK_DIR/P1-requirements.md"
P2_REVIEW="$TASK_DIR/P2-review.md"

[ ! -f "$P2_REVIEW" ] && exit 2

# R1 修复：用环境变量传参
RISK_LEVEL=$(P1_FILE="$P1_FILE" python3 -c "
import re, os
with open(os.environ['P1_FILE']) as f:
    text = f.read()
m = re.search(r'risk_level:\s*(low|medium|high)', text)
print(m.group(1) if m else '')
" 2>/dev/null || echo "")

# 非 high risk，不检查
[ "$RISK_LEVEL" != "high" ] && exit 0

# O2 修复：用相对路径查 git log（绝对路径在某些 git 版本可能有问题）
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
P2_REVIEW_REL=$(realpath --relative-to="$REPO_ROOT" "$P2_REVIEW" 2>/dev/null || echo "$P2_REVIEW")

# high risk：检查 P2-review.md 的 git author
REVIEW_AUTHOR=$(git log -1 --format='%an' -- "$P2_REVIEW_REL" 2>/dev/null || echo "")

# 取主 Agent 的默认 identity（当前 git config user.name）
ORCHESTRATOR_NAME=$(git config user.name 2>/dev/null || echo "")

if [ -z "$REVIEW_AUTHOR" ]; then
    echo "GATE P2-REVIEW: P2-review.md 无 git log 记录" >&2
    exit 1
fi

if [ "$REVIEW_AUTHOR" = "$ORCHESTRATOR_NAME" ]; then
    echo "GATE P2-REVIEW: high risk 任务的 P2 评审 author 是主 Agent（${ORCHESTRATOR_NAME}），需独立 subagent" >&2
    exit 1
fi

echo "GATE P2-REVIEW: author=${REVIEW_AUTHOR}（非主 Agent ${ORCHESTRATOR_NAME}）" >&2
exit 0
```

- [ ] **Step 2: 验证语法 + Commit**

```bash
bash -n scripts/check-p2-review.sh
git add scripts/check-p2-review.sh
git commit -m "feat(hardening): check-p2-review.sh P2 评审 author 检查

P2.10 high risk 任务的 P2 评审必须由独立 subagent 产出"
```

---

## Task 3: check-scope-resolved.sh SCOPE+ 追踪检查

**Files:**
- Create: `scripts/check-scope-resolved.sh`

- [ ] **Step 1: 写 check-scope-resolved.sh**

```bash
#!/usr/bin/env bash
# check-scope-resolved.sh — SCOPE+ 处理追踪（P2.11）
# 检查产出含 [SCOPE+] 时，P1-requirements.md 有对应 [SCOPE_RESOLVED] 标记
# exit 0 = 通过; exit 1 = SCOPE+ 未处理; exit 2 = 无 task 目录

set -euo pipefail

TASK_DIR="${1:?用法: check-scope-resolved.sh TASK_DIR}"
P1_FILE="$TASK_DIR/P1-requirements.md"

[ ! -d "$TASK_DIR" ] && exit 2

# M2 修复：扫描所有 .md 文件（SCOPE+ 可能出现在非 P 前缀文件里，如 dispatch-context.md）
SCOPE_FOUND=""
for f in "$TASK_DIR"/*.md; do
    [ -f "$f" ] || continue
    if grep -q '\[SCOPE+\]' "$f" 2>/dev/null; then
        SCOPE_FOUND="${SCOPE_FOUND}$(basename "$f") "
    fi
done

# 无 SCOPE+ → 不检查
[ -z "$SCOPE_FOUND" ] && exit 0

# 有 SCOPE+：检查 P1 是否有 [SCOPE_RESOLVED]
if [ ! -f "$P1_FILE" ]; then
    echo "GATE SCOPE: 产出含 [SCOPE+]（${SCOPE_FOUND}），但无 P1-requirements.md" >&2
    exit 1
fi

RESOLVED_COUNT=$(grep -c '\[SCOPE_RESOLVED\]' "$P1_FILE" 2>/dev/null || echo 0)

if [ "$RESOLVED_COUNT" -eq 0 ]; then
    echo "GATE SCOPE: 产出含 [SCOPE+]（${SCOPE_FOUND}），但 P1 无 [SCOPE_RESOLVED] 标记" >&2
    exit 1
fi

echo "GATE SCOPE: ${SCOPE_FOUND}有 [SCOPE+]，P1 有 ${RESOLVED_COUNT} 个 [SCOPE_RESOLVED]" >&2
exit 0
```

- [ ] **Step 2: 验证语法 + Commit**

```bash
bash -n scripts/check-scope-resolved.sh
git add scripts/check-scope-resolved.sh
git commit -m "feat(hardening): check-scope-resolved.sh SCOPE+ 追踪

P2.11 产出含 [SCOPE+] 时 P1 必须有 [SCOPE_RESOLVED] 标记"
```

---

## Task 4: check-retrospective.sh 复盘异常触发

**Files:**
- Create: `scripts/check-retrospective.sh`

- [ ] **Step 1: 写 check-retrospective.sh**

```bash
#!/usr/bin/env bash
# check-retrospective.sh — 复盘异常触发（P2.12）
# 检测异常模式，输出复盘提醒（不中止 commit）
# exit 0 = 总是通过（只提醒不拦截）

set -euo pipefail

TASK_DIR="${1:?用法: check-retrospective.sh TASK_DIR}"
STATE_FILE="${2:-.state.yaml}"

# 异常模式检测
WARNINGS=""

# 1. gate 重试超限
if [ -f "$STATE_FILE" ]; then
    RETRIES_OVER=$(STATE_FILE="$STATE_FILE" python3 -c "
import yaml, os
with open(os.environ['STATE_FILE']) as f:
    data = yaml.safe_load(f)
retries = data.get('retries', {})
if isinstance(retries, dict):
    for phase, attempts in retries.items():
        if isinstance(attempts, list) and len(attempts) >= 3:
            print(f'{phase}={len(attempts)}')
            break
" 2>/dev/null || echo "")
    [ -n "$RETRIES_OVER" ] && WARNINGS="${WARNINGS}gate 重试超限（${RETRIES_OVER}）\n"
fi

# 2. SCOPE+ 触发
if [ -d "$TASK_DIR" ]; then
    for f in "$TASK_DIR"/P*.md; do
        [ -f "$f" ] || continue
        if grep -q '\[SCOPE+\]' "$f" 2>/dev/null; then
            WARNINGS="${WARNINGS}SCOPE+ 触发（$(basename "$f")）\n"
            break
        fi
    done
fi

# 3. 裁剪 override 触发
if [ -d "$TASK_DIR" ] && [ -f "$TASK_DIR/P1-requirements.md" ]; then
    if grep -q '^override:' "$TASK_DIR/P1-requirements.md" 2>/dev/null; then
        WARNINGS="${WARNINGS}裁剪声明与执行不一致（override 触发）\n"
    fi
fi

if [ -n "$WARNINGS" ]; then
    echo "GATE RETRO: 建议复盘 — 检测到异常模式：" >&2
    printf "$WARNINGS" | while IFS= read -r line; do
        [ -n "$line" ] && echo "  - $line" >&2
    done
    echo "  请在版本 bump 前写简版复盘（docs/releases/v{version}-retrospective.md）" >&2
fi

exit 0
```

- [ ] **Step 2: 验证语法 + Commit**

```bash
bash -n scripts/check-retrospective.sh
git add scripts/check-retrospective.sh
git commit -m "feat(hardening): check-retrospective.sh 复盘异常触发

P2.12 异常模式检测 → 复盘提醒（不中止 commit）"
```

---

## Task 5: 集成进 pre-commit-gate.sh

**Files:**
- Modify: `scripts/pre-commit-gate.sh`

- [ ] **Step 1: 在 gate 运行之后、gate 结果处理之前插入新检查**

在 `write_gate_result` 之后追加（O1 修复：gate 失败时不跑裁剪检查，gate 错误优先）：

```bash
# 5.5 裁剪条件检查（P2.7-P2.9）——gate 未通过时跳过（gate 错误优先）
if [ "$GATE_EXIT" != "1" ] && [ -n "$TASK_ID" ] && [ -d "$TASK_DIR" ]; then
    bash "$REPO_ROOT/scripts/check-pruning.sh" "$TASK_DIR" || exit 1
fi

# 5.6 P2 评审 author 检查（P2.10）——gate 未通过时跳过
if [ "$GATE_EXIT" != "1" ] && [ -n "$TASK_ID" ] && [ -d "$TASK_DIR" ]; then
    bash "$REPO_ROOT/scripts/check-p2-review.sh" "$TASK_DIR" 2>/dev/null || true
    # exit 2 = 无 P2 文件或非 high risk，不拦截
fi

# 5.7 SCOPE+ 追踪检查（P2.11）——gate 未通过时跳过
if [ "$GATE_EXIT" != "1" ] && [ -n "$TASK_ID" ] && [ -d "$TASK_DIR" ]; then
    bash "$REPO_ROOT/scripts/check-scope-resolved.sh" "$TASK_DIR" || exit 1
fi

# 5.8 复盘异常触发（P2.12）——只提醒不中止，gate 失败时也提醒
if [ -n "$TASK_ID" ] && [ -d "$TASK_DIR" ]; then
    bash "$REPO_ROOT/scripts/check-retrospective.sh" "$TASK_DIR" "$STATE_FILE" 2>/dev/null || true
fi
```

- [ ] **Step 2: 验证语法 + Commit**

```bash
bash -n scripts/pre-commit-gate.sh
git add scripts/pre-commit-gate.sh
git commit -m "feat(hardening): pre-commit-gate.sh 集成 P2.7-P2.12

P2.7-P2.9 裁剪条件检查
P2.10 P2 评审 author 检查
P2.11 SCOPE+ 追踪
P2.12 复盘异常触发"
```

---

## Task 6: 协议文件改动 — P1 模板加 risk_level + override

**Files:**
- Modify: `assets/templates/task-files.md`（P1-requirements.md 模板 L119-161）

- [ ] **Step 1: 在 P1 模板的「## 5. 裁剪说明」区追加 risk_level 和 override 字段**

在 `phases: [P1,P2,P4,P5,P6,P8]` 之前追加 `risk_level` 行，在 phases 之后追加 override 说明：

```markdown
## 5. 裁剪说明
risk_level: low                      # low=纯UI/文案/配置 | medium=业务逻辑/API/数据 | high=安全/权限/数据迁移/生产环境
phases: [P1,P2,P4,P5,P6,P8]
- 跳过 P3 理由：...
- 跳过 P7 理由：...
# override（裁剪声明与实际执行不一致时回写，见 dispatch-protocol.md P2.9）
# override: P2 retained (reason: 主 Agent 判断需要方案设计)
```

- [ ] **Step 2: Commit**

```bash
git add assets/templates/task-files.md
git commit -m "docs(hardening): P1 模板加 risk_level + override 字段

P2.7 risk_level: low/medium/high
P2.9 override 字段（裁剪声明与执行不一致时回写）"
```

---

## Task 7: 协议文件改动 — WORKFLOW.md 适用边界表 + P2 评审条件

**Files:**
- Modify: `WORKFLOW.md`（适用边界表 L109-157 + P2 评审角色 L180）

- [ ] **Step 1: 适用边界表增加"复杂度 × 风险"矩阵（P2.13）**

在现有适用边界表之后追加风险矩阵：

```markdown
### 风险矩阵（P2.13）

任务分类应该是"复杂度 × 风险"的矩阵，不是只看复杂度：

| | 低风险 | 高风险（安全/数据/权限）|
|---|--------|----------------------|
| 微改动 | 直接做 | 精简 agate：P1 + P4 + P5 |
| 小改动 | 裁剪 agate：P1 + P3 + P4 + P5 | 完整 agate（至少到 P6）|
| 中改动 | 完整 P1-P8 | 完整 P1-P8 + P6 不可裁剪 |

"直接做"的最低要求（P2.14）：commit message 必须声明改了什么 + 为什么安全。
```

- [ ] **Step 2: P2 评审角色增加派发条件（P2.10）**

在 P2 行的评审角色列改为：

```markdown
| P2 | 方案设计 | architect | plan-eng-review（risk_level=high 时必须派发，author 非主 Agent）/ plan-design-review（domains 含 frontend 时追加）/ plan-ceo-review（涉及商业模式判断时可选）| ... |
```

- [ ] **Step 3: Commit**

```bash
git add WORKFLOW.md
git commit -m "docs(hardening): WORKFLOW.md 风险矩阵 + P2 评审派发条件

P2.13 适用边界表加复杂度 × 风险矩阵
P2.10 P2 评审派发条件明确化
P2.14 直接做的最低要求"
```

---

## Task 8: 协议文件改动 — dispatch-protocol.md 门槛表 + SCOPE_RESOLVED

**Files:**
- Modify: `dispatch-protocol.md`（门槛表 L568-577 + SCOPE+ 扫描 L609）

- [ ] **Step 1: 门槛表 P1→P2 行追加 risk_level 检查**

在 P1→P2 门槛追加：
```
+ grep -qE 'risk_level:\s*(low|medium|high)' P1-requirements.md → 命中
```

- [ ] **Step 2: SCOPE+ 扫描段追加 [SCOPE_RESOLVED] 检查**

在 SCOPE+ / SCOPE_GAP 扫描段之后追加：

```markdown
**SCOPE+ 处理追踪（P2.11）**：产出含 [SCOPE+] 时，主 Agent 必须在 P1-requirements.md 增补对应条目并标记 [SCOPE_RESOLVED: 来源文件]。未标记 [SCOPE_RESOLVED] 的 [SCOPE+] → gate 不通过。

格式：
[SCOPE_RESOLVED: from P4-implementation.md] 新需求已增补为 AC-N，影响范围已评估
```

- [ ] **Step 3: Commit**

```bash
git add dispatch-protocol.md
git commit -m "docs(hardening): dispatch-protocol.md 门槛表 + SCOPE_RESOLVED

P2.7 P1 门槛追加 risk_level 检查
P2.11 SCOPE+ 处理追踪格式定义"
```

---

## Task 9: 协议文件改动 — state-machine.md 裁剪规则 + SCOPE_RESOLVED 转移

**Files:**
- Modify: `state-machine.md`（裁剪跳过规则 L158-175 + SCOPE+ 转移 L177-186）

- [ ] **Step 1: 裁剪跳过规则追加 risk_level 条件**

在「可跳过的阶段」段之前追加：

```markdown
  **裁剪条件（hook 验证，见 scripts/check-pruning.sh）**：
  - 裁剪 P2：需 risk_level=low AND BDD ≤ 10
  - 裁剪 P3：需 risk_level=low（high 风险不可裁）
  - 裁剪 P6：不可裁（除非 no_behavior_change: true）
  - 裁剪 P7：需改动文件数 ≤ 5
  
  **裁剪声明回写（P2.9）**：若主 Agent 决定不执行 P1 声明的裁剪（保留被裁剪的阶段），
  必须在 P1-requirements.md 追加 override 字段。
```

- [ ] **Step 2: SCOPE+ 转移追加 [SCOPE_RESOLVED] 标记要求**

在 SCOPE+ 转移规则中追加：

```markdown
  **[SCOPE_RESOLVED] 标记（P2.11）**：主 Agent 增补 P1 基线时，必须标记 [SCOPE_RESOLVED: from {来源文件}]。
  未标记的 [SCOPE+] → gate 拦截（scripts/check-scope-resolved.sh）。
```

- [ ] **Step 3: Commit**

```bash
git add state-machine.md
git commit -m "docs(hardening): state-machine.md 裁剪条件 + SCOPE_RESOLVED

P2.7-P2.8 裁剪条件 hook 验证
P2.9 裁剪声明回写
P2.11 SCOPE_RESOLVED 标记要求"
```

---

## Task 10: 更新 roadmap 状态 + 一致性检查

**Files:**
- Modify: `docs/hardening-roadmap.md`

- [ ] **Step 1: 更新 2B-2 和 2B-3 表格状态**

将 P2.7-P2.12 和 P2.13-P2.14 的状态从"待实现"改为"已实现"。

- [ ] **Step 2: 一致性检查**

Run: `python3 scripts/check-protocol-consistency.py`
Expected: 0 ERROR

- [ ] **Step 3: Commit**

```bash
git add docs/hardening-roadmap.md
git commit -m "docs: roadmap 2B-2 + 2B-3 状态更新 — P2.7-P2.14 已实现"
```

---

## 完成标准

- [ ] check-pruning.sh 落地：risk_level + BDD 数 + 裁剪条件验证
- [ ] check-p2-review.sh 落地：high risk 任务的 P2 评审 author 检查
- [ ] check-scope-resolved.sh 落地：SCOPE+ 有对应 [SCOPE_RESOLVED]
- [ ] check-retrospective.sh 落地：异常模式检测 + 复盘提醒
- [ ] 4 个检查集成进 pre-commit-gate.sh
- [ ] P1 模板加 risk_level + override 字段
- [ ] WORKFLOW.md 加风险矩阵 + P2 评审派发条件
- [ ] dispatch-protocol.md 门槛表加 risk_level + SCOPE_RESOLVED 格式
- [ ] state-machine.md 裁剪条件 + SCOPE_RESOLVED 转移
- [ ] roadmap 状态更新
- [ ] 一致性检查 0 ERROR
