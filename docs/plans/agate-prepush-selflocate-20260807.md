# pre-commit-gate.sh AGATE_ROOT 自定位（支持 worktree）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让 `pre-commit-gate.sh` 自定位 AGATE_ROOT（不再依赖 `~/.agate` 软链），使其在 worktree 中作为 hook 运行时可指向 worktree 自己的协议本体，而非主 checkout。

**Architecture:** 当前 `pre-commit-gate.sh:23` 硬编码 `AGATE_ROOT="${AGATE_ROOT:-$HOME/.agate}"`。改为自定位：`AGATE_ROOT="${AGATE_ROOT:-$(readlink -f "$(dirname "${BASH_SOURCE[0]}")/..")}"`，与其他脚本（agate-inject-card.sh 等）一致。`install-hook.sh:14` **不改**（它是安装脚本，应默认全局 `~/.agate`，且已支持 `$1` 参数覆盖）。

**Tech Stack:** bash + bats。

**背景调研（已确认）：**
- 25 个脚本中，仅 `pre-commit-gate.sh:23` 硬编码 `~/.agate` 作为 hook 运行时的 AGATE_ROOT 默认值
- 其余脚本（agate-inject-card、agate-next-card、agate-extract-context、agate-render-dispatch-prompt、gate-result）均用 `BASH_SOURCE`/`$0` 自定位，天然支持 worktree
- `install-hook.sh:14` 虽也默认 `~/.agate`，但它是**安装脚本**，应指向全局软链，且接受 `$1` 参数覆盖——**不是债，不改**
- 被 `bash "$AGATE_ROOT/scripts/xxx.sh"` 调用的子脚本（check-gate、check-p6-evidence 等）不自行定位 AGATE_ROOT，由调用方传入，无需改

---

## File Structure

- **Modify** `agate/scripts/pre-commit-gate.sh:23` — AGATE_ROOT 从 `$HOME/.agate` 改为自定位。
- **Test** `agate/tests/integration/pre-commit-hook.bats` — 新增 worktree 场景测试。
- **Modify** `agate/tests/README.md` — 用例数同步。

---

### Task 1: TDD — 写失败测试（worktree 场景下踩 `~/.agate`）

**Files:**
- Test: `agate/tests/integration/pre-commit-hook.bats`

**背景**：当前 pre-commit-gate.sh 在 `AGATE_ROOT` 未设置时回落 `~/.agate`。worktree 场景：hook 软链指向 worktree 的 pre-commit-gate.sh，但运行时若不设 `AGATE_ROOT`，会误用主 checkout 本体。测试模拟：把 pre-commit-gate.sh 复制到"worktree"位置，不设 AGATE_ROOT 运行，断言它自定位到自身所在目录的 `..`（而非 `~/.agate`）。

- [ ] **Step 1: 写失败测试（真红）**

在 `agate/tests/integration/pre-commit-hook.bats` 末尾追加。**思路**：隔离本体放一个**被 source 时会打印标记**的 gate-result.sh，主 checkout 的 gate-result.sh 不打印。当前代码（走 `~/.agate`）sources 主 checkout 版 → 无标记；新代码（自定位）sources 隔离体版 → 有标记。这是真红/真绿可区分测试。

```bash
@test "pre-commit hook: AGATE_ROOT 未设时自定位到脚本自身本体（worktree 支持，T086）" {
    local repo workflow_root
    repo=$(git_init)

    # 模拟 worktree：隔离协议本体目录
    workflow_root="$BATS_TEST_TMPDIR/workflow-root"
    mkdir -p "$workflow_root/scripts"
    cp "$AGATE_ROOT/scripts/pre-commit-gate.sh" "$workflow_root/scripts/"
    chmod +x "$workflow_root/scripts/pre-commit-gate.sh"

    # 隔离本体的 gate-result.sh：被 source 时打印标记（主 checkout 版不打印）
    cat > "$workflow_root/scripts/gate-result.sh" <<'EOF'
# 隔离本体专用 gate-result.sh —— 被 source 时打印 WORKTREE_SOURCED 标记
echo "WORKTREE_SOURCED"
EOF

    # 构造最小可 gate 场景（P1 阶段，无 P1-review.md → 会走 gate-result 加载路径）
    mkdir -p "$repo/docs/tasks/TX/workflow-test"
    cat > "$repo/docs/tasks/TX/workflow-test/.state.yaml" <<EOF
task_id: TX
phase: P1
status: active
retries: {}
EOF

    # 模拟真实 worktree hook 场景：hook 是软链 → 隔离本体的 pre-commit-gate.sh
    # 用软链调用，使 BASH_SOURCE[0] 是软链路径，验证 readlink -f 能解析到隔离本体
    ln -sf "$workflow_root/scripts/pre-commit-gate.sh" "$repo/.git/hooks/pre-commit"

    # 不设 AGATE_ROOT，通过软链运行 → 应自定位到隔离本体，source 到带标记的 gate-result.sh
    run bash -c "unset AGATE_ROOT; cd '$repo' && bash '$repo/.git/hooks/pre-commit' 2>&1"

    [[ "$output" == *"WORKTREE_SOURCED"* ]]
}
```

> **红/绿说明**：当前代码 `AGATE_ROOT="${AGATE_ROOT:-$HOME/.agate}"` → 通过软链运行隔离本体的 pre-commit-gate.sh 时，`source "$HOME/.agate/scripts/gate-result.sh"`（主 checkout 版，**不打印标记**）→ 测试 FAIL（红）。改为自定位后 → `readlink -f` 解析软链到隔离本体 → `source "$workflow_root/scripts/gate-result.sh"`（打印标记）→ 测试 PASS（绿）。真红真绿，且通过软链完整覆盖 worktree hook 的 symlink 场景。

- [ ] **Step 2: 运行测试确认当前失败（红）**

```bash
bats agate/tests/integration/pre-commit-hook.bats --filter 'worktree'
```
预期：FAIL（当前走 `~/.agate`，source 不到带标记的 gate-result.sh）。

---

### Task 2: 改 pre-commit-gate.sh 自定位

**Files:**
- Modify: `agate/scripts/pre-commit-gate.sh:23`

- [ ] **Step 1: 修改 AGATE_ROOT 解析**

把：

```bash
AGATE_ROOT="${AGATE_ROOT:-$HOME/.agate}"
```

改为：

```bash
# v0.33.0：AGATE_ROOT 自定位到脚本自身本体的上一级（支持 worktree 隔离）
# hook 被软链到项目 .git/hooks/ 时，readlink -f 解析软链到真实脚本位置 → 本体根
# 顺序关键：先 readlink -f 解析软链，再 dirname 两次取本体根（不能先 dirname 再 /..，会解析到 .git）
AGATE_ROOT="${AGATE_ROOT:-$(dirname "$(dirname "$(readlink -f "${BASH_SOURCE[0]:-$0}")")")}"
```

> **实现要点（评审 + 实测验证）**：
> 1. **`readlink -f` 必须先执行**，再 `dirname` 两次。若先 `dirname "${BASH_SOURCE[0]}"` 再 `readlink -f .../..`，软链场景下会解析到 `.git`（实测复现），错误。
> 2. **`${BASH_SOURCE[0]:-$0}`**：兼容 `bash script.sh`（用 BASH_SOURCE）和直接可执行（用 `$0`）。
> 3. 该模式与既有 `agate-inject-card.sh:10`（`dirname "$(dirname "$(readlink -f "$0")")"`）一致。
> 4. 已实测：软链 `${workflow_root}/scripts/pre-commit-gate.sh` → `.git/hooks/pre-commit`，`bash .git/hooks/pre-commit` 运行，`AGATE_ROOT` 正确解析为 `$workflow_root`（非 `.git`）。

- [ ] **Step 2: 验证**

```bash
bash agate/scripts/pre-commit-gate.sh P8 2>/dev/null | head -1   # 应能正常加载，不报"无法加载 gate-result.sh"
shellcheck -S warning agate/scripts/pre-commit-gate.sh
python3 agate/scripts/check-protocol-consistency.py
```
预期：正常 / clean / 0 ERROR。

- [ ] **Step 3: 跑 Task 1 测试验证绿**

```bash
bats agate/tests/integration/pre-commit-hook.bats --filter 'worktree'
```
预期：PASS。

- [ ] **Step 4: Commit**

```bash
git add agate/scripts/pre-commit-gate.sh agate/tests/integration/pre-commit-hook.bats
git commit -m "refactor: pre-commit-gate.sh AGATE_ROOT 自定位支持 worktree (v0.33.0)

原硬编码 \$HOME/.agate 作为 hook 运行时默认，worktree 场景下会误指向主
checkout 本体。改为 readlink -f 自定位（与其他脚本一致），hook 软链到
worktree 时自动指向 worktree 本体。install-hook.sh 不改（安装脚本应默认全局）。

self-gate-review: agate/scripts/pre-commit-gate.sh"
```

---

### Task 2.5: 既有测试 cp 安装改 ln -sf 软链（卫生改进，非 critical）

**Files:**
- Modify: `agate/tests/integration/pre-commit-hook.bats`
- Modify: `agate/tests/integration/dispatch-context-card.bats`

**背景（评审第 3 轮澄清）**：现有测试用 `cp` 把 pre-commit-gate.sh **复制**到 `.git/hooks/pre-commit`（pre-commit-hook.bats 行 15/1124/1177；dispatch-context-card.bats 行 11）。自定位改造后，**复制**版 hook 在 `AGATE_ROOT` 未设时会解析到 `.git`（错误）。

**但**：测试环境的 `load.bash:30` 会 `export AGATE_ROOT=...`，测试运行 hook 时 `${AGATE_ROOT:-...}` 短路，自定位不触发 → **现有测试不会崩**（第 3 轮实测全 544 绿）。所以这不是 critical 修复，而是**卫生改进**：让测试安装方式与真实 `install-hook.sh:31`（软链）一致，避免将来若测试环境清理 `AGATE_ROOT` 时暴露问题。

- [ ] **Step 1: 把 4 处 `cp` 改为 `ln -sf`**

`agate/tests/integration/pre-commit-hook.bats`：
- 行 15（setup）：`cp ...` → `ln -sf "$AGATE_ROOT/scripts/pre-commit-gate.sh" "$HOOK_PATH"`
- 行 1124：`cp ...` → `ln -sf ...`
- 行 1177：`cp ...` → `ln -sf ...`

`agate/tests/integration/dispatch-context-card.bats`：
- 行 11：`cp ...` → `ln -sf ...`

> 注意：`chmod +x "$HOOK_PATH"` 在软链下 chmod 到目标文件（符合预期）。保留无害。

- [ ] **Step 2: 跑全量测试验证绿**

```bash
bats agate/tests/integration/pre-commit-hook.bats agate/tests/integration/dispatch-context-card.bats
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
```
预期：全部通过。

- [ ] **Step 3: Commit**

```bash
git add agate/tests/integration/pre-commit-hook.bats agate/tests/integration/dispatch-context-card.bats
git commit -m "test: pre-commit hook 安装改 ln -sf 软链（卫生改进）

让测试安装方式与真实 install-hook.sh（软链）一致。自定位改造后软链版
readlink 能正确解析到真实本体。非 critical（load.bash 导出 AGATE_ROOT
使现有测试不触发自定位），但消除潜在环境差异。

self-gate-review: agate/tests/integration/pre-commit-hook.bats agate/tests/integration/dispatch-context-card.bats"
```

---

### Task 3: 更新计数 + 版本 bump v0.33.0

**Files:**
- Modify: `agate/tests/README.md`
- Modify: `README.md`, `CHANGELOG.md`

- [ ] **Step 1: 更新计数**

```bash
bash agate/tests/scripts/count-tests.sh
```
确认 pre-commit-hook.bats 用例数 +1。

- [ ] **Step 2: 全量验证**

```bash
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
shellcheck -S warning agate/scripts/*.sh
python3 agate/scripts/check-protocol-consistency.py
```
预期：全绿 / clean / 0 ERROR。

- [ ] **Step 3: 版本 bump**

README badge `v0.32.0` → `v0.33.0`。CHANGELOG 加 `[v0.33.0]`（非 BREAKING）。

- [ ] **Step 4: Commit**

```bash
git add README.md CHANGELOG.md agate/tests/README.md
git commit -m "chore: v0.33.0

pre-commit-gate.sh AGATE_ROOT 自定位，支持 worktree 隔离。非 BREAKING。

self-gate-review: agate/scripts/pre-commit-gate.sh"
```

---

## Self-Review

**1. Spec coverage：**
- 自定位改造 → Task 1（失败测试）+ Task 2（实现）
- 既有测试 cp→软链卫生改进（评审第 3 轮降级）→ Task 2.5
- 计数 + 版本 → Task 3
- install-hook.sh 明确不改（调研确认是安装脚本应默认全局）

**评审记录（独立评审 3 轮）：**
- 第 1 轮（GO）：测试真红真绿验证；install-hook 不改合理；建议测试走软链（采纳）
- 第 2 轮（NO-GO -> 修复）：报告 cp 安装会崩 85 测试 -> 加 Task 2.5
- 第 3 轮（GO + 纠正）：第 2 轮的"85 测试全崩"是误报--load.bash:30 导出 AGATE_ROOT 使 hook 短路，自定位不触发，实测全 544 绿。Task 2.5 降级为卫生改进（非 critical），补第 4 处 dispatch-context-card.bats:11，理由修正为"匹配真实 install-hook.sh 软链安装"

**2. Placeholder scan：** 无 TBD；测试和实现代码完整。

**3. Type consistency：** `AGATE_ROOT` 变量名一致；测试用 `$workflow_root` 与实现的自定位路径逻辑一致。

**已识别风险：**
- **测试真红已验证**：用「隔离本体放被 source 时打印标记的 gate-result.sh + 软链调用」方案，当前代码走 `~/.agate` 不打印 → 红；改后自定位打印 → 绿。真红真绿，且通过软链完整覆盖 worktree hook 的 symlink 场景。
- **实现模式已实测修正**：初稿 `readlink -f "$(dirname ...)/.."` 在软链场景解析到 `.git`（错误）。已改为 `dirname "$(dirname "$(readlink -f ...)")"`（先 readlink 再 dirname 两次），实测软链场景正确解析到本体根，与 agate-inject-card.sh 模式一致。
- **readlink -f MSYS2/Git Bash**：GNU coreutils 有，但 MSYS2 的 `readlink` 可能无 `-f`。若 `readlink -f` 失败，`${BASH_SOURCE[0]:-$0}` 退化为相对路径（软链场景解析到 `.git`，错误）。这是已记录的 degrade——**主目标 Linux 可用**；Git Bash 若要完整支持 worktree 需另行评估（或改用 `realpath` 或 python 定位）。非本次阻塞。