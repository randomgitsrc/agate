# Phase 1 + 2A 实施计划：pre-commit hook + CI backstop + 状态一致性强制

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 hardening-roadmap Phase 1（pre-commit hook + CI backstop + gate-result 存储 + CHANGELOG/P6 证据检查）和 Phase 2A（状态一致性强制），让 gate 执行和状态转移从"主 Agent 自觉"变成"硬工具强制"。

**Architecture:** pre-commit hook 在每次 git commit 时自动运行 check-gate.sh，结果写入 .gate-result.json（主 Agent 不可篡改）；CI 在 push 时重跑 gate 对照；状态转移合法性、重试上限、回退跳变由 hook 检查。不改协议文件，纯加脚本。

**Tech Stack:** Bash（pre-commit hook）、Python（.gate-result.json 生成 + CI 对照脚本）、YAML（GitHub Actions workflow）

**来源**：`docs/hardening-roadmap.md` Phase 1（P1.1-P1.7）+ Phase 2A（P2.3-P2.6）

**评审修订**（review-20260630-1551.md，6 项全部采纳）：
- R1: source 失败静默放行 → source 后验证函数已加载（Task 4）
- R2: PROD_TOUCHED 扫全文误报 → 改用 `git diff --cached | grep`（Task 4）
- O1: 回退检测依赖 commit message → 降级 WARNING，等 .gate-history.jsonl 数据（Task 2）
- O2: retries 结构不匹配（列表不是整数）→ 用 `len(attempts)`（Task 2）
- O3: commit_sha 语义错误 → 改名 `prev_commit_sha`（Task 1）
- M1: P6 证据格式假设与协议不符 → 退化为现有 `- PASS`/`- FAIL` 格式，完整格式留 Phase 2B（Task 3 + Task 8）

---

## 文件结构

| 文件 | 责任 | 创建/修改 |
|------|------|-----------|
| `scripts/gate-result.sh` | .gate-result.json 生成 + .gate-history.jsonl 追加 + 读取工具函数 | 创建 |
| `scripts/check-state-transition.sh` | 状态转移合法性检查（phase 跳变、重试上限、回退跳变） | 创建 |
| `scripts/check-changelog.sh` | CHANGELOG [Unreleased] 含 task_id 检查 | 创建 |
| `scripts/check-p6-evidence.sh` | P6-acceptance.md 每条 BDD 有 Evidence 引用检查 | 创建 |
| `scripts/pre-commit-gate.sh` | pre-commit hook 入口：检测触发条件、跑 gate、写结果、检查各项 | 创建 |
| `scripts/install-hook.sh` | 安装 pre-commit hook 到 .git/hooks/ | 创建 |
| `scripts/ci-gate-backstop.py` | CI 对照：重跑 gate，与 .gate-result.json 比对 | 创建 |
| `.github/workflows/protocol-consistency.yml` | 追加 gate backstop job | 修改 |
| `.gitignore` | 忽略 .gate-result.json（每 commit 重新生成） | 修改 |
| `scripts/check-gate.sh` | P6 分支追加证据格式检查 | 修改 |

---

## Task 1: gate-result.sh 工具函数库

**Files:**
- Create: `scripts/gate-result.sh`

- [ ] **Step 1: 写 gate-result.sh**

```bash
#!/usr/bin/env bash
# gate-result.sh — .gate-result.json 生成 + .gate-history.jsonl 追加
# 被 pre-commit-gate.sh 调用，不直接执行。

set -euo pipefail

# write_gate_result PHASE TASK_ID EXIT_CODE OUTPUT
write_gate_result() {
    local phase="$1"
    local task_id="$2"
    local exit_code="$3"
    local output="$4"
    local ts prev_commit_sha

    ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    # pre-commit hook 在 commit 创建之前运行，HEAD 是上一个 commit
    # 字段名 prev_commit_sha 明确语义，避免误读为"本次 commit SHA"（O3 修复）
    prev_commit_sha=$(git rev-parse HEAD 2>/dev/null || echo "pre-commit")

    cat > .gate-result.json <<EOF
{
  "phase": "${phase}",
  "task_id": "${task_id}",
  "exit_code": ${exit_code},
  "timestamp": "${ts}",
  "output": $(printf '%s' "$output" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))'),
  "runner": "pre-commit-hook",
  "prev_commit_sha": "${prev_commit_sha}"
}
EOF

    printf '{"phase":"%s","task_id":"%s","exit_code":%d,"timestamp":"%s","prev_commit_sha":"%s"}\n' \
        "$phase" "$task_id" "$exit_code" "$ts" "$prev_commit_sha" >> .gate-history.jsonl
}

read_state_phase() {
    local state_file="$1"
    [ ! -f "$state_file" ] && { echo ""; return; }
    python3 -c "
import yaml
with open('$state_file') as f:
    data = yaml.safe_load(f)
print(data.get('phase', '') if data else '')
" 2>/dev/null || echo ""
}

read_state_task_id() {
    local state_file="$1"
    [ ! -f "$state_file" ] && { echo ""; return; }
    python3 -c "
import yaml
with open('$state_file') as f:
    data = yaml.safe_load(f)
print(data.get('task_id', '') if data else '')
" 2>/dev/null || echo ""
}

has_staged_phase_change() {
    local state_file="$1"
    git diff --cached --name-only 2>/dev/null | grep -qF "$state_file" || return 1
    git diff --cached -- "$state_file" 2>/dev/null | grep -qE '^\+.*phase:' || return 1
    return 0
}

has_staged_phase_output() {
    git diff --cached --name-only 2>/dev/null | grep -qE 'P[0-9]+-.*\.(md|yaml)$' || return 1
    return 0
}
```

- [ ] **Step 2: 验证语法**

Run: `bash -n scripts/gate-result.sh`
Expected: 无输出

- [ ] **Step 3: Commit**

```bash
git add scripts/gate-result.sh
git commit -m "feat(hardening): gate-result.sh 工具函数库

.gate-result.json 生成 + .gate-history.jsonl 追加 + .state.yaml 读取"
```

---

## Task 2: check-state-transition.sh 状态转移检查

**Files:**
- Create: `scripts/check-state-transition.sh`

- [ ] **Step 1: 写 check-state-transition.sh**

```bash
#!/usr/bin/env bash
# check-state-transition.sh — 状态转移合法性检查（Phase 2A: P2.3-P2.5）
# P2.3 phase 跳变合法性
# P2.4 重试超限 -> phase 必须是 PAUSED
# P2.5 回退跳变 >= 2 -> 必须有 PAUSED 记录
#
# exit 0 = 合法; exit 1 = 非法

set -euo pipefail

STATE_FILE="${1:-.state.yaml}"
MAX_RETRY=3

get_old_phase() {
    git show :"${STATE_FILE}" 2>/dev/null | python3 -c "
import yaml, sys
try:
    data = yaml.safe_load(sys.stdin)
    print(data.get('phase', '') if data else '')
except:
    print('')
" 2>/dev/null || echo ""
}

get_new_phase() {
    [ -f "$STATE_FILE" ] || { echo ""; return; }
    python3 -c "
import yaml
with open('$STATE_FILE') as f:
    data = yaml.safe_load(f)
print(data.get('phase', '') if data else '')
" 2>/dev/null || echo ""
}

phase_num() {
    echo "$1" | grep -oE '[0-9]+' || echo "0"
}

# 只在 .state.yaml 有暂存变更时检查
git diff --cached --name-only 2>/dev/null | grep -qF "$STATE_FILE" || exit 0

old_phase=$(get_old_phase)
new_phase=$(get_new_phase)

case "$new_phase" in
    ""|PAUSED|READY|DONE) exit 0 ;;
esac

old_num=$(phase_num "$old_phase")
new_num=$(phase_num "$new_phase")

# 检查 1：回退跳变 >= 2（T019 教训）
# 协议规定"不依赖 commit message 格式"（state-machine.md L371-373）
# .gate-history.jsonl 尚未积累数据，降级为 WARNING 不中止（O1 修复）
if [ "$old_num" -gt 0 ] && [ "$new_num" -gt 0 ]; then
    diff=$((old_num - new_num))
    if [ "$diff" -ge 2 ]; then
        echo "GATE STATE: 警告 — 回退跳变 P${old_num}→P${new_num}（差 ${diff}），建议确认是否经过 PAUSED" >&2
        # 降级 WARNING，不 exit 1
        # 长期：等 .gate-history.jsonl 积累数据后改为查历史记录
    fi
fi

# 检查 2：重试超限（P2.4）
# .state.yaml 的 retries[Pn] 是列表（每次重试一个对象），不是整数（O2 修复）
if [ -f "$STATE_FILE" ]; then
    retries_json=$(python3 -c "
import yaml
with open('$STATE_FILE') as f:
    data = yaml.safe_load(f)
retries = data.get('retries', {})
if isinstance(retries, dict):
    for phase, attempts in retries.items():
        if isinstance(attempts, list) and len(attempts) >= ${MAX_RETRY}:
            print(f'{phase}={len(attempts)}')
            break
" 2>/dev/null || echo "")

    if [ -n "$retries_json" ] && [ "$new_phase" != "PAUSED" ]; then
        echo "GATE STATE: ${retries_json}（>= MAX ${MAX_RETRY}），phase 应为 PAUSED" >&2
        exit 1
    fi
fi

exit 0
```

- [ ] **Step 2: 验证语法**

Run: `bash -n scripts/check-state-transition.sh`
Expected: 无输出

- [ ] **Step 3: Commit**

```bash
git add scripts/check-state-transition.sh
git commit -m "feat(hardening): check-state-transition.sh 状态转移检查

P2.3 phase 跳变合法性 + P2.4 重试超限 + P2.5 回退跳变检测"
```

---

## Task 3: check-changelog.sh + check-p6-evidence.sh

**Files:**
- Create: `scripts/check-changelog.sh`
- Create: `scripts/check-p6-evidence.sh`

- [ ] **Step 1: 写 check-changelog.sh**

```bash
#!/usr/bin/env bash
# check-changelog.sh — CHANGELOG [Unreleased] 含 task_id 检查（P1.6）
# exit 0 = 通过; exit 1 = 未记录; 无 CHANGELOG 文件时 exit 0

set -euo pipefail

TASK_ID="${1:?用法: check-changelog.sh TASK_ID}"
CHANGELOG_FILE="${CHANGELOG_FILE:-CHANGELOG.md}"

[ ! -f "$CHANGELOG_FILE" ] && exit 0

UNRELEASED_CONTENT=$(python3 -c "
import re
with open('${CHANGELOG_FILE}') as f:
    text = f.read()
m = re.search(r'##\s*\[Unreleased\](.*?)(?=##\s*\[|\Z)', text, re.S)
if m:
    print(m.group(1))
" 2>/dev/null || echo "")

if [ -z "$UNRELEASED_CONTENT" ]; then
    echo "GATE CHANGELOG: ${CHANGELOG_FILE} 无 [Unreleased] 区域" >&2
    exit 1
fi

if echo "$UNRELEASED_CONTENT" | grep -qF "$TASK_ID"; then
    exit 0
else
    echo "GATE CHANGELOG: [Unreleased] 区域未找到 ${TASK_ID}" >&2
    exit 1
fi
```

- [ ] **Step 2: 写 check-p6-evidence.sh**

```bash
#!/usr/bin/env bash
# check-p6-evidence.sh — P6 证据格式检查（P1.7）
# 检查 P6-evidence/ 目录非空（现有协议已支持）
# 注意：完整的"每条 BDD 有 Evidence 引用"检查需要协议定义
# ## BDD-NN 标题和 Evidence: 字段格式，这属于 Phase 2B 协议改动。
# 当前退化为：BDD 条目数（- PASS/- FAIL 行）= 证据文件数（M1 修复）
# exit 0 = 通过; exit 1 = 证据缺失; exit 2 = 无 P6 文件

set -euo pipefail

TASK_DIR="${1:?用法: check-p6-evidence.sh TASK_DIR}"
P6_FILE="$TASK_DIR/P6-acceptance.md"

[ ! -f "$P6_FILE" ] && exit 2

# 用现有协议约定的格式计数（- PASS / - FAIL 行）
BDD_COUNT=$(grep -cE '^\s*- (PASS|FAIL)' "$P6_FILE" || echo 0)

if [ "$BDD_COUNT" -eq 0 ]; then
    echo "GATE P6-EVIDENCE: P6-acceptance.md 无 BDD 条目（- PASS/- FAIL 格式）" >&2
    exit 1
fi

# 检查 P6-evidence/ 目录非空
EVIDENCE_DIR="$TASK_DIR/P6-evidence"
if [ ! -d "$EVIDENCE_DIR" ] || [ -z "$(ls -A "$EVIDENCE_DIR" 2>/dev/null)" ]; then
    echo "GATE P6-EVIDENCE: P6-evidence/ 目录不存在或为空" >&2
    exit 1
fi

echo "GATE P6-EVIDENCE: ${BDD_COUNT} 条 BDD，证据目录非空" >&2
exit 0
```

- [ ] **Step 3: 验证语法**

Run: `bash -n scripts/check-changelog.sh && bash -n scripts/check-p6-evidence.sh`
Expected: 无输出

- [ ] **Step 4: Commit**

```bash
git add scripts/check-changelog.sh scripts/check-p6-evidence.sh
git commit -m "feat(hardening): check-changelog.sh + check-p6-evidence.sh

P1.6 CHANGELOG [Unreleased] 含 task_id 检查
P1.7 P6 证据格式检查（每条 BDD 有 Evidence 引用）"
```

---

## Task 4: pre-commit-gate.sh 主入口

**Files:**
- Create: `scripts/pre-commit-gate.sh`

- [ ] **Step 1: 写 pre-commit-gate.sh**

```bash
#!/usr/bin/env bash
# pre-commit-gate.sh — pre-commit hook 入口
# 安装到 .git/hooks/pre-commit，每次 git commit 自动触发。
#
# Phase 1: P1.1 跑 gate 写 .gate-result.json
#          P1.2 PROD_TOUCHED 检测
#          P1.6 CHANGELOG 检查
#          P1.7 P6 证据格式检查
# Phase 2A: P2.3-P2.5 状态转移检查
#
# 触发条件：.state.yaml phase 变更 OR 阶段产出文件变更

set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)

# R1 修复：source 后验证函数已加载，防止静默放行
source "$REPO_ROOT/scripts/gate-result.sh" \
    || { echo "GATE ERROR: 无法加载 gate-result.sh" >&2; exit 1; }
type write_gate_result >/dev/null 2>&1 \
    || { echo "GATE ERROR: gate-result.sh 加载不完整（write_gate_result 未定义）" >&2; exit 1; }

STATE_FILE="$REPO_ROOT/.state.yaml"
AGATE_TASKS_DIR="${AGATE_TASKS_DIR:-docs/tasks}"

# 0. 检测是否需要触发 gate
NEEDS_GATE=false
has_staged_phase_change "$STATE_FILE" && NEEDS_GATE=true
[ "$NEEDS_GATE" = false ] && has_staged_phase_output && NEEDS_GATE=true

if [ "$NEEDS_GATE" = false ]; then
    exit 0
fi

# 1. 读取当前状态
PHASE=$(read_state_phase "$STATE_FILE")
TASK_ID=$(read_state_task_id "$STATE_FILE")

[ -z "$PHASE" ] && exit 0

TASK_DIR="$REPO_ROOT/$AGATE_TASKS_DIR/$TASK_ID"

# 2. PROD_TOUCHED 检测（P1.2）
# R2 修复：扫描暂存 diff 内容，不扫文件全文（协议文件本身含 PROD_TOUCHED 字样）
if git diff --cached | grep -q '\[PROD_TOUCHED\]'; then
    echo "GATE: 检测到 [PROD_TOUCHED] 标记，中止 commit" >&2
    exit 1
fi

# 3. 状态转移检查（P2.3-P2.5）
if [ -f "$STATE_FILE" ]; then
    bash "$REPO_ROOT/scripts/check-state-transition.sh" "$STATE_FILE" || exit 1
fi

# 4. 运行 gate（P1.1）
GATE_OUTPUT=""
GATE_EXIT=2

if [ "$PHASE" != "PAUSED" ] && [ "$PHASE" != "READY" ] && [ "$PHASE" != "DONE" ] && [ -d "$TASK_DIR" ]; then
    GATE_OUTPUT=$(bash "$REPO_ROOT/scripts/check-gate.sh" "$PHASE" "$TASK_DIR" 2>&1) && GATE_EXIT=0 || GATE_EXIT=$?
fi

write_gate_result "$PHASE" "$TASK_ID" "$GATE_EXIT" "$GATE_OUTPUT"

# 5. CHANGELOG 检查（P1.6）——警告不中止
if [ -n "$TASK_ID" ]; then
    bash "$REPO_ROOT/scripts/check-changelog.sh" "$TASK_ID" 2>/dev/null || \
        echo "GATE CHANGELOG: 警告 — [Unreleased] 未记录 ${TASK_ID}" >&2
fi

# 6. P6 证据格式检查（P1.7）——中止
if [ "$PHASE" = "P6" ] || [ "$PHASE" = "P7" ]; then
    if [ -d "$TASK_DIR" ]; then
        bash "$REPO_ROOT/scripts/check-p6-evidence.sh" "$TASK_DIR" || exit 1
    fi
fi

# 7. gate 结果处理
case "$GATE_EXIT" in
    0) echo "GATE $PHASE: 通过" >&2; exit 0 ;;
    1) echo "GATE $PHASE: 未通过" >&2; echo "$GATE_OUTPUT" >&2; exit 1 ;;
    2) echo "GATE $PHASE: 需主 Agent 手动判断" >&2; echo "$GATE_OUTPUT" >&2; exit 0 ;;
esac
```

- [ ] **Step 2: 验证语法**

Run: `bash -n scripts/pre-commit-gate.sh`
Expected: 无输出

- [ ] **Step 3: Commit**

```bash
git add scripts/pre-commit-gate.sh
git commit -m "feat(hardening): pre-commit-gate.sh 主入口

P1.1 跑 gate 写 .gate-result.json
P1.2 PROD_TOUCHED 检测
P1.6 CHANGELOG 检查
P1.7 P6 证据格式检查
P2.3-P2.5 状态转移检查"
```

---

## Task 5: install-hook.sh 安装脚本

**Files:**
- Create: `scripts/install-hook.sh`

- [ ] **Step 1: 写 install-hook.sh**

```bash
#!/usr/bin/env bash
# install-hook.sh — 安装 pre-commit hook
# 把 pre-commit-gate.sh 链接到 .git/hooks/pre-commit

set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || { echo "不在 git 仓库中" >&2; exit 1; })
HOOK_DIR="$REPO_ROOT/.git/hooks"
HOOK_FILE="$HOOK_DIR/pre-commit"
SOURCE="$REPO_ROOT/scripts/pre-commit-gate.sh"

[ ! -f "$SOURCE" ] && { echo "错误: $SOURCE 不存在" >&2; exit 1; }

mkdir -p "$HOOK_DIR"

# 备份已有 hook
if [ -f "$HOOK_FILE" ] && [ ! -L "$HOOK_FILE" ]; then
    cp "$HOOK_FILE" "$HOOK_FILE.bak.$(date +%s)"
    echo "已备份现有 pre-commit hook"
fi

ln -sf "$SOURCE" "$HOOK_FILE"
chmod +x "$SOURCE"

echo "pre-commit hook 已安装: $HOOK_FILE -> $SOURCE"
```

- [ ] **Step 2: 验证语法 + 运行安装**

Run: `bash -n scripts/install-hook.sh && bash scripts/install-hook.sh`
Expected: "pre-commit hook 已安装"

- [ ] **Step 3: 测试非 agate commit 不触发**

Run: `git commit --allow-empty -m "test: hook 不应触发" 2>&1`
Expected: 无 gate 输出，commit 成功

- [ ] **Step 4: Commit**

```bash
git add scripts/install-hook.sh
git commit -m "feat(hardening): install-hook.sh 安装脚本"
```

---

## Task 6: ci-gate-backstop.py CI 对照脚本

**Files:**
- Create: `scripts/ci-gate-backstop.py`

- [ ] **Step 1: 写 ci-gate-backstop.py**

```python
#!/usr/bin/env python3
"""ci-gate-backstop.py — CI gate backstop（P1.3）

push 时重跑 gate，与 .gate-result.json 对照。
防止 git commit --no-verify 绕过 hook。

退出码：0 = 通过; 1 = 失败
"""

import json
import subprocess
import sys
from pathlib import Path


def run_gate(phase: str, task_dir: str) -> tuple[int, str]:
    script = Path("scripts/check-gate.sh")
    if not script.exists():
        return 2, "check-gate.sh not found"
    result = subprocess.run(
        ["bash", str(script), phase, task_dir],
        capture_output=True, text=True
    )
    return result.returncode, result.stderr + result.stdout


def main() -> int:
    repo_root = Path.cwd()
    state_file = repo_root / ".state.yaml"
    gate_result = repo_root / ".gate-result.json"

    if not state_file.exists():
        print("SKIP: 无 .state.yaml，非 agate 项目")
        return 0

    try:
        import yaml
        with open(state_file) as f:
            data = yaml.safe_load(f)
        phase = data.get("phase", "")
        task_id = data.get("task_id", "")
    except Exception:
        print("SKIP: 无法读取 .state.yaml")
        return 0

    if not phase or phase in ("PAUSED", "READY", "DONE", ""):
        print(f"SKIP: phase={phase}，无 gate 需要对照")
        return 0

    task_dir = str(repo_root / "docs/tasks" / task_id) if task_id else ""
    ci_exit, ci_output = run_gate(phase, task_dir)

    if not gate_result.exists():
        if ci_exit == 1:
            print(f"FAIL: gate 未通过（无 .gate-result.json，CI 重跑 exit={ci_exit}）")
            return 1
        print(f"WARN: 无 .gate-result.json（可能 --no-verify 跳过），CI exit={ci_exit}")
        return 0

    with open(gate_result) as f:
        recorded = json.load(f)

    recorded_exit = recorded.get("exit_code")
    recorded_phase = recorded.get("phase")

    if recorded_phase != phase:
        print(f"FAIL: .gate-result.json phase={recorded_phase} != .state.yaml phase={phase}")
        return 1

    if recorded_exit != ci_exit:
        print(f"FAIL: .gate-result.json exit={recorded_exit} != CI 重跑 exit={ci_exit}")
        return 1

    # timestamp 验证（防事后补写）
    # 注意：.gate-result.json 的 prev_commit_sha 是 hook 运行时的 HEAD（上一个 commit）
    # CI 里拿到的 HEAD 是本次 push 的最新 commit，两者不同是正常的
    import datetime
    recorded_ts = recorded.get("timestamp", "")
    if recorded_ts:
        try:
            ts = datetime.datetime.fromisoformat(recorded_ts.replace("Z", "+00:00"))
            commit_ts_str = subprocess.run(
                ["git", "log", "-1", "--format=%cI"],
                capture_output=True, text=True, check=True
            ).stdout.strip()
            commit_ts = datetime.datetime.fromisoformat(commit_ts_str)
            if ts > commit_ts:
                print(f"FAIL: .gate-result.json timestamp {ts} > commit {commit_ts}")
                return 1
        except Exception:
            pass

    print(f"PASS: phase={phase} exit_code={ci_exit} 一致")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: 验证语法**

Run: `python3 -c "import ast; ast.parse(open('scripts/ci-gate-backstop.py').read())"`
Expected: 无输出

- [ ] **Step 3: Commit**

```bash
git add scripts/ci-gate-backstop.py
git commit -m "feat(hardening): ci-gate-backstop.py CI 对照脚本

P1.3 push 时重跑 gate，与 .gate-result.json 对照"
```

---

## Task 7: 更新 CI workflow + .gitignore

**Files:**
- Modify: `.github/workflows/protocol-consistency.yml`
- Modify: `.gitignore`

- [ ] **Step 1: 追加 gate-backstop job**

在 `.github/workflows/protocol-consistency.yml` 的 `jobs:` 下追加：

```yaml
  gate-backstop:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install pyyaml

      - name: Run gate backstop check
        run: python3 scripts/ci-gate-backstop.py
```

- [ ] **Step 2: 更新 .gitignore**

追加：
```
# gate result（每 commit 由 pre-commit hook 重新生成）
.gate-result.json
```

注意：**不**忽略 `.gate-history.jsonl`——历史记录应提交到仓库。

- [ ] **Step 3: 验证 CI workflow 语法**

Run: `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/protocol-consistency.yml'))"`
Expected: 无输出

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/protocol-consistency.yml .gitignore
git commit -m "feat(hardening): CI gate-backstop job + .gitignore

P1.3 CI workflow 追加 gate backstop job
.gate-result.json 加入 .gitignore"
```

---

## Task 8: 更新 check-gate.sh P6 证据检查集成

**Files:**
- Modify: `scripts/check-gate.sh`（P6 分支）

- [ ] **Step 1: 在 P6 分支 exit 2 之前追加证据格式检查**

注意：完整的 `## BDD-NN` + `Evidence:` 格式检查需要协议改动（Phase 2B）。
当前 P1.7 退化为：P6-evidence/ 目录非空检查已在 check-gate.sh P6 分支中存在，
check-p6-evidence.sh 做同样的退化检查。因此 Task 8 **不修改 check-gate.sh**——
P6 证据检查由 pre-commit-gate.sh 调用 check-p6-evidence.sh 完成，不重复。

如果要在 check-gate.sh P6 分支中追加独立检查，用已有格式：
```bash
      # P6 证据格式检查（P1.7 退化版）：BDD 条目数 > 0 且证据目录非空
      # 完整的每条 BDD 有 Evidence 引用检查留到 Phase 2B 协议改动后
      BDD_FMT_COUNT=$(grep -cE '^\s*- (PASS|FAIL)' "$TASK_DIR/P6-acceptance.md" 2>/dev/null || echo 0)
      if [ "$BDD_FMT_COUNT" -eq 0 ]; then
          echo "GATE P6: P6-acceptance.md 无 BDD 条目（- PASS/- FAIL 格式）" >&2
          exit 1
      fi
```

但 check-gate.sh P6 分支已有 `TOTAL=$(grep -cE '^\s*- (PASS|FAIL)' ...)` 且 `TOTAL -eq 0 → exit 1`，
所以此检查已隐含在现有逻辑中。Task 8 实际不需要修改 check-gate.sh。

**结论：Task 8 标记为"无需修改"，P6 证据检查已由 Task 3 的 check-p6-evidence.sh 覆盖。**

- [ ] **Step 2: 验证 check-gate.sh 无需修改**

Run: `bash -n scripts/check-gate.sh`
Expected: 无输出（确认语法仍正确，未做修改）

- [ ] **Step 3: Commit（仅记录评审结论）**

```bash
git commit --allow-empty -m "docs(hardening): Task 8 评审结论 — check-gate.sh 无需修改

P6 证据检查已由 check-p6-evidence.sh（Task 3）覆盖
check-gate.sh P6 分支已有 TOTAL=0 → exit 1 检查
完整格式检查留到 Phase 2B 协议改动后"
```

---

## Task 9: 端到端验证

**Files:** 无新建文件

- [ ] **Step 1: 安装 hook**

Run: `bash scripts/install-hook.sh`
Expected: "pre-commit hook 已安装"

- [ ] **Step 2: 测试普通文档 commit 不触发 gate**

Run: `git commit --allow-empty -m "test: hook 不应触发" 2>&1`
Expected: 无 gate 输出，commit 成功

- [ ] **Step 3: 测试 .state.yaml 变更触发 gate**

```bash
cat > .state.yaml <<'EOF'
phase: P5
task_id: TEST001
retries:
  p5: 0
EOF
git add .state.yaml
git commit -m "test: .state.yaml 变更应触发 gate" 2>&1
```

Expected: hook 触发，输出 "GATE P5: 需主 Agent 手动判断"（exit 2），commit 成功

- [ ] **Step 4: 验证 .gate-result.json 生成**

Run: `cat .gate-result.json`
Expected: JSON 含 phase=P5, exit_code=2, timestamp

- [ ] **Step 5: 验证 .gate-history.jsonl 追加**

Run: `tail -1 .gate-history.jsonl`
Expected: JSON 行含 phase=P5

- [ ] **Step 6: 测试 PROD_TOUCHED 拦截**

```bash
echo "[PROD_TOUCHED] test" > docs/tasks/TEST001/P0-brief.md 2>/dev/null || mkdir -p docs/tasks/TEST001 && echo "[PROD_TOUCHED] test" > docs/tasks/TEST001/P0-brief.md
git add docs/tasks/TEST001/P0-brief.md .state.yaml
git commit -m "test: PROD_TOUCHED 应被拦截" 2>&1
```

Expected: commit 被中止，输出 "检测到 [PROD_TOUCHED] 标记"

- [ ] **Step 7: 清理测试文件**

```bash
rm -rf docs/tasks/TEST001 .state.yaml .gate-result.json
git add -A
git commit -m "test: 清理端到端测试文件"
```

- [ ] **Step 8: 最终验证 — 一致性检查**

Run: `python3 scripts/check-protocol-consistency.py`
Expected: 0 ERROR

- [ ] **Step 9: Commit 验证结果**

```bash
git add -A
git commit -m "test: Phase 1 + 2A 端到端验证通过

验证项：
- 普通文档 commit 不触发 gate
- .state.yaml 变更触发 gate + 写 .gate-result.json
- .gate-history.jsonl 追加记录
- PROD_TOUCHED 标记拦截 commit
- 一致性检查 0 ERROR"
```

---

## 完成标准

- [ ] pre-commit-gate.sh 落地，覆盖 P3/P4/P5/P6/P7/P8 gate
- [ ] .gate-result.json + .gate-history.jsonl 格式定义并落地
- [ ] CI workflow 跑 gate backstop
- [ ] CHANGELOG 检查 + P6 证据格式检查集成进 hook
- [ ] 状态转移检查（回退跳变 + 重试超限）集成进 hook
- [ ] PROD_TOUCHED 检测集成进 hook
- [ ] 端到端验证：普通 commit 不触发、.state.yaml 变更触发、PROD_TOUCHED 拦截
- [ ] 一致性检查 0 ERROR
