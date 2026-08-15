---
task_id: agate-self-gate-enforcement
agent: main
date: 2026-07-02
status: 实施计划
来源: docs/issues/002-self-gate-no-termination.md + self-gate 评审实证
---

# self-gate 强制触发 + 递归终止 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 给 self-gate 加 commit-msg hook 强制触发 + 自然终止条件，消除"依赖主 Agent 自觉"的强制力缺口。

**Architecture:** commit-msg hook 检测 self-gate 触发文件改动 → commit message 必须含 `self-gate-review:` 路径 → 否则 WARNING。审查报告全 ALIGNED = 自然终止，§9 写明终止条件。install-hook.sh 同时装 commit-msg hook。

**Tech Stack:** bash, bats, git hooks

---

## 文件结构

| 文件 | 职责 |
|------|------|
| `agate/scripts/commit-msg-self-gate.sh` | **新建**：commit-msg hook，检测 self-gate 触发文件改动 |
| `agate/scripts/install-hook.sh` | **修改**：同时安装 commit-msg hook |
| `SELF-GATE.md` | **修改**：§9 补终止条件 + 开头补强制力边界声明 |
| `agate/tests/integration/commit-msg-self-gate.bats` | **新建**：commit-msg hook 集成测试 |
| `agate/tests/integration/protocol-alignment-review.bats` | **修改**：加 SG.7/SG.8 测试 |
| `CHANGELOG.md` | **修改**：标注变更 |

---

### Task 1: commit-msg-self-gate.sh

**Files:**
- Create: `agate/scripts/commit-msg-self-gate.sh`

- [ ] **Step 1: 写脚本**

```bash
#!/usr/bin/env bash
# commit-msg-self-gate.sh — commit-msg hook
# 检测 self-gate 触发文件的改动，要求 commit message 含 self-gate-review: 路径
# WARNING 不拦截——遵循 hook 鲁棒性优先原则

set -euo pipefail

COMMIT_MSG_FILE="${1:?用法: commit-msg-self-gate.sh COMMIT_MSG_FILE}"
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)

# 检查暂存区是否含 self-gate 触发文件
SELF_GATE_TRIGGERED=false
STAGED_FILES=$(git diff --cached --name-only 2>/dev/null || true)
if echo "$STAGED_FILES" | grep -qE '^(agate/scripts/.*\.sh|agate/scripts/check-protocol-consistency\.py|agate/[^/]+\.md|agate/.+/.*\.md|SELF-GATE\.md)$'; then
    SELF_GATE_TRIGGERED=true
fi

if [ "$SELF_GATE_TRIGGERED" = "false" ]; then
    exit 0
fi

# 检查 commit message 是否含 self-gate-review: 路径 或 self-gate-skip: 理由
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE" 2>/dev/null || true)
if echo "$COMMIT_MSG" | grep -qE 'self-gate-skip:\s*\S+'; then
    exit 0
fi
if echo "$COMMIT_MSG" | grep -qE 'self-gate-review:\s*\S+'; then
    exit 0
fi

echo "GATE SELF-GATE: 暂存区含 self-gate 触发文件（agate/scripts/*.sh / agate/*.md / SELF-GATE.md），" >&2
echo "  但 commit message 未含 self-gate-review: 路径。" >&2
echo "  请先派发 protocol-alignment-review subagent，审查报告路径写入 commit message：" >&2
echo "    self-gate-review: docs/reviews/agate-alignment-review-{date}.md" >&2
echo "  或如果本次改动确实不需要 self-gate（如纯 typo），在 commit message 加：" >&2
echo "    self-gate-skip: 理由" >&2

exit 0
```

- [ ] **Step 2: chmod +x**

```bash
chmod +x agate/scripts/commit-msg-self-gate.sh
```

- [ ] **Step 3: shellcheck**

```bash
shellcheck agate/scripts/commit-msg-self-gate.sh
```

Expected: 0 error

- [ ] **Step 4: 手动验证——不触发场景**

在 agate 仓库里暂存一个非触发文件（如 README.md），跑脚本，应 exit 0 无输出。

- [ ] **Step 5: 手动验证——触发但无 review 路径**

暂存 `SELF-GATE.md`，commit message 不含 `self-gate-review:`，跑脚本，应 exit 0 + WARNING 输出。

- [ ] **Step 6: 手动验证——触发且有 review 路径**

暂存 `SELF-GATE.md`，commit message 含 `self-gate-review: docs/reviews/xxx.md`，跑脚本，应 exit 0 无 WARNING。

- [ ] **Step 7: Commit**

```bash
git add agate/scripts/commit-msg-self-gate.sh
git commit -m "feat: commit-msg-self-gate.sh — self-gate 触发文件改动时要求 review 路径"
```

---

### Task 2: commit-msg hook 集成测试

**Files:**
- Create: `agate/tests/integration/commit-msg-self-gate.bats`

- [ ] **Step 1: 写测试**

```bash
#!/usr/bin/env bats
# tests/integration/commit-msg-self-gate.bats — commit-msg-self-gate.sh 测试
load ../helpers/load.bash

setup() {
    REPO=$(git_init)
    cd "$REPO"
    # 先做一次初始 commit
    echo "init" > README.md
    git add README.md
    git commit -qm "init"
    # 复制 commit-msg hook
    HOOK_PATH="$REPO/.git/hooks/commit-msg"
    cp "$AGATE_ROOT/scripts/commit-msg-self-gate.sh" "$HOOK_PATH"
    chmod +x "$HOOK_PATH"
    # 创建 agate 目录结构（模拟 agate 仓库）
    mkdir -p "$REPO/agate/scripts" "$REPO/agate/assets"
    # 复制脚本到仓库内（hook 用 git diff --cached 检查暂存区）
    cp "$AGATE_ROOT/scripts/commit-msg-self-gate.sh" "$REPO/agate/scripts/"
}

@test "CSG.1 非触发文件改动 → 无 WARNING" {
    echo "change" > "$REPO/README.md"
    git add README.md
    # commit message 不含 self-gate-review，但改的不是触发文件
    run git -C "$REPO" commit -m "update readme"
    [ "$status" -eq 0 ]
    [[ "$output" != *"self-gate-review"* ]]
}

@test "CSG.2 触发文件改动 + 无 review 路径 → WARNING" {
    echo "# change" > "$REPO/SELF-GATE.md"
    git add SELF-GATE.md
    run git -C "$REPO" commit -m "update self-gate"
    [ "$status" -eq 0 ]
    [[ "$output" == *"self-gate-review"* ]]
}

@test "CSG.3 触发文件改动 + 有 review 路径 → 无 WARNING" {
    echo "# change" > "$REPO/SELF-GATE.md"
    git add SELF-GATE.md
    run git -C "$REPO" commit -m "update self-gate" -m "self-gate-review: docs/reviews/agate-alignment-review-2026-07-02.md"  # 非本仓
    [ "$status" -eq 0 ]
    [[ "$output" != *"self-gate-review"* ]]
}

@test "CSG.4 触发文件改动 + self-gate-skip → 无 WARNING" {
    echo "# change" > "$REPO/SELF-GATE.md"
    git add SELF-GATE.md
    run git -C "$REPO" commit -m "fix typo" -m "self-gate-skip: 纯 typo 修复"
    [ "$status" -eq 0 ]
    [[ "$output" != *"self-gate-review"* ]]
}

@test "CSG.5 agate/scripts/*.sh 改动触发" {
    echo "# change" > "$REPO/agate/scripts/check-gate.sh"
    git add agate/scripts/check-gate.sh
    run git -C "$REPO" commit -m "update gate script"
    [ "$status" -eq 0 ]
    [[ "$output" == *"self-gate-review"* ]]
}

@test "CSG.6 agate/*.md 改动触发" {
    echo "# change" > "$REPO/agate/WORKFLOW.md"
    git add agate/WORKFLOW.md
    run git -C "$REPO" commit -m "update workflow"
    [ "$status" -eq 0 ]
    [[ "$output" == *"self-gate-review"* ]]
}
```

- [ ] **Step 2: 跑测试确认全过**

```bash
bats agate/tests/integration/commit-msg-self-gate.bats
```

Expected: 6/6 pass

- [ ] **Step 3: Commit**

```bash
git add agate/tests/integration/commit-msg-self-gate.bats
git commit -m "test: commit-msg-self-gate.sh 集成测试 CSG.1-CSG.6"
```

---

### Task 3: install-hook.sh 扩展

**Files:**
- Modify: `agate/scripts/install-hook.sh`

- [ ] **Step 1: 修改 install-hook.sh**

在现有 pre-commit hook 安装逻辑之后，加 commit-msg hook 安装：

```bash
# 安装 commit-msg hook（self-gate 强制触发）
COMMIT_MSG_HOOK="$HOOK_DIR/commit-msg"
COMMIT_MSG_SOURCE="$AGATE_ROOT/scripts/commit-msg-self-gate.sh"

if [ -f "$COMMIT_MSG_SOURCE" ]; then
    # 备份已有 hook
    if [ -f "$COMMIT_MSG_HOOK" ] && [ ! -L "$COMMIT_MSG_HOOK" ]; then
        cp "$COMMIT_MSG_HOOK" "$COMMIT_MSG_HOOK.bak.$(date +%s)"
        echo "已备份现有 commit-msg hook"
    fi
    ln -sf "$COMMIT_MSG_SOURCE" "$COMMIT_MSG_HOOK"
    chmod +x "$COMMIT_MSG_SOURCE"
    echo "commit-msg hook 已安装: $COMMIT_MSG_HOOK -> $COMMIT_MSG_SOURCE"
else
    echo "提示: $COMMIT_MSG_SOURCE 不存在，跳过 commit-msg hook 安装"
fi
```

插入位置：在 `echo "pre-commit hook 已安装: ..."` 之后、脚本末尾之前。

- [ ] **Step 2: shellcheck**

```bash
shellcheck agate/scripts/install-hook.sh
```

- [ ] **Step 3: 手动验证**

在临时仓库跑 `bash agate/scripts/install-hook.sh`，确认 `.git/hooks/commit-msg` 软链接指向 `commit-msg-self-gate.sh`。

- [ ] **Step 4: Commit**

```bash
git add agate/scripts/install-hook.sh
git commit -m "feat: install-hook.sh 同时安装 commit-msg hook"
```

---

### Task 4: SELF-GATE.md 补终止条件 + 强制力边界声明

**Files:**
- Modify: `SELF-GATE.md`

- [ ] **Step 1: 在开头（§触发条件之前）加强制力边界声明**

在 `## 触发条件` 之前插入：

```markdown
## 强制力边界

**本机制目前有 commit-msg hook 辅助提醒**：暂存区含 self-gate 触发文件时，commit message 须含 `self-gate-review:` 路径（或 `self-gate-skip:` 理由），否则 WARNING。

但 WARNING 不拦截——遵循 hook 鲁棒性优先原则。主 Agent 仍可忽略 WARNING 直接 commit。真正的强制力依赖主 Agent 自觉 + CI 兜底（待实现）。详见 issue #002。
```

- [ ] **Step 2: 改写 §9 递归适用**

把现有 §9：

```markdown
## 递归适用

本机制自身的实施也走 self-gate。任何针对 agate 的变更 plan，实施时都必须走本流程。

如果 self-gate 尚未实现（如还在 plan 阶段），实施者至少手动执行等价检查：
1. 跑现有 check-protocol-consistency.py
2. 人工逐项核对"文档描述的规则 vs 脚本实现"是否一致（对照 A1-A6）
3. 跑全量 bats
```

改写为：

```markdown
## 递归适用与终止条件

本机制自身的实施也走 self-gate。任何针对 agate 的变更 plan，实施时都必须走本流程。

### 递归终止

审查报告结论汇总表里所有项都是 ALIGNED 或 NEEDS_HUMAN_REVIEW（附 `[HUMAN_CONFIRMED: ...]`）→ **本轮终止**。

如果审查发现 MISALIGNED → 必须修复 → 修复后重审 → 直到全 ALIGNED。这是自然终止，不需要额外标记。

### 未实现时的等价检查

如果 self-gate 尚未实现（如还在 plan 阶段），实施者至少手动执行等价检查：
1. 跑现有 check-protocol-consistency.py
2. 人工逐项核对"文档描述的规则 vs 脚本实现"是否一致（对照 A1-A6）
3. 跑全量 bats
```

- [ ] **Step 3: 跑 SG.* 测试确认没破**

```bash
bats agate/tests/integration/protocol-alignment-review.bats
```

Expected: 6/6 pass

- [ ] **Step 4: Commit**

```bash
git add SELF-GATE.md
git commit -m "docs: SELF-GATE.md 补强制力边界声明 + 递归终止条件"
```

---

### Task 5: SG.7/SG.8 测试 + issue #002 状态更新

**Files:**
- Modify: `agate/tests/integration/protocol-alignment-review.bats`
- Modify: `docs/issues/002-self-gate-no-termination.md`

- [ ] **Step 1: 加 SG.7 和 SG.8 测试**

在 `protocol-alignment-review.bats` 末尾追加：

```bash
@test "SG.7 commit-msg-self-gate.sh 存在且可执行" {
    local hook_script="$AGATE_SCRIPTS/commit-msg-self-gate.sh"
    [ -f "$hook_script" ]
    [ -x "$hook_script" ]
}

@test "SG.8 SELF-GATE.md 含递归终止条件" {
    local selfgate_file="$BATS_TEST_DIRNAME/../../../SELF-GATE.md"
    [ -f "$selfgate_file" ]
    grep -q '递归终止' "$selfgate_file"
    grep -q 'ALIGNED' "$selfgate_file"
}
```

- [ ] **Step 2: 跑测试**

```bash
bats agate/tests/integration/protocol-alignment-review.bats
```

Expected: 8/8 pass

- [ ] **Step 3: 更新 issue #002 状态**

在 `docs/issues/002-self-gate-no-termination.md`：
- 把 `**待设计**` 改为 `**已实施**（commit-msg hook WARNING + 自然终止）`
- 在解决方向表里标注 A（commit-msg hook）已实施、D（终止条件）已实施（简化为自然终止，砍掉 `[NO_FURTHER_FIXES_NEEDED]` 标记）
- 补"实证"节：CON.9 反例（self-gate 评审 §1）

- [ ] **Step 4: Commit**

```bash
git add agate/tests/integration/protocol-alignment-review.bats docs/issues/002-self-gate-no-termination.md
git commit -m "test: SG.7/SG.8 + issue #002 状态更新为已实施"
```

---

### Task 6: CHANGELOG + 全量验证

**Files:**
- Modify: `CHANGELOG.md`

- [ ] **Step 1: 更新 CHANGELOG**

在 `[Unreleased]` 下加：

```markdown
### self-gate 强制触发 + 递归终止（issue #002）

- 新增 `commit-msg-self-gate.sh`：暂存区含 self-gate 触发文件时，commit message 须含 `self-gate-review:` 路径或 `self-gate-skip:` 理由，否则 WARNING
- `install-hook.sh` 同时安装 commit-msg hook
- `SELF-GATE.md` 补强制力边界声明 + 递归终止条件（审查报告全 ALIGNED = 终止）
- 砍掉 `[NO_FURTHER_FIXES_NEEDED]` 标记——自然终止，不需要人工声明
```

- [ ] **Step 2: 跑全量测试**

```bash
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
```

Expected: 全过

- [ ] **Step 3: 跑一致性检查**

```bash
python3 agate/scripts/check-protocol-consistency.py
```

Expected: 0 ERROR

- [ ] **Step 4: shellcheck**

```bash
shellcheck agate/scripts/*.sh
```

Expected: 0 error

- [ ] **Step 5: 测试计数**

```bash
bash agate/tests/scripts/count-tests.sh
```

- [ ] **Step 6: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs: CHANGELOG 标注 self-gate 强制触发 + 递归终止"
```
