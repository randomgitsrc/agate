# pre-push hook 抽成独立脚本（软链统一）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 pre-push hook 从 install-hook.sh 内嵌的写死复制模板，改为独立的 `pre-push-gate.sh` 脚本 + 软链安装，与 pre-commit/commit-msg 统一。

**Architecture:** 新建 `agate/scripts/pre-push-gate.sh`（内容 = 当前 heredoc 模板，修正 grep -c 双输出 bug），`install-hook.sh` 的 pre-push 安装从 `cat > heredoc` 改为 `ln -sf` 软链。测试从内嵌 heredoc 副本改为指向真实脚本。副作用分析已确认：cwd 无差异（git 以仓库根为 cwd 执行 hook）、stdin 参数无差异、不引用 `$AGATE_ROOT`/项目路径，可安全独立。

**Tech Stack:** bash + bats。

---

### Task 1: 新建 pre-push-gate.sh 独立脚本

**Files:**
- Create: `agate/scripts/pre-push-gate.sh`

- [ ] **Step 1: 创建脚本**（内容 = 当前 heredoc 模板，含 grep -c bug 修复）

```bash
#!/usr/bin/env bash
# pre-push-gate.sh — pre-push hook：协议文件（agate/*.md）大改动自动提示 alignment-review
# 由 install-hook.sh 以软链方式安装到 .git/hooks/pre-push
# git 以仓库根为 cwd 执行（与 pre-commit-gate.sh 相同），stdin 收 local_ref/local_sha/remote_ref/remote_sha
# exit 0 = 不阻断 push；仅提示。

set -euo pipefail

THRESHOLD="${AGATE_ALIGNMENT_REVIEW_THRESHOLD:-20}"
ZERO_SHA="0000000000000000000000000000000000000000"

while read -r local_ref local_sha remote_ref remote_sha; do
    [ -z "$local_sha" ] && continue
    if [ "$remote_sha" = "$ZERO_SHA" ]; then
        echo "ℹ️  新分支首次推送，跳过 agate/*.md 改动量检测（无远端基线可比较）"
        continue
    fi
    CHANGED_LINES=$(git diff "$remote_sha".."$local_sha" -- 'agate/*.md' 2>/dev/null | grep -cE '^[+-]' || true)
    CHANGED_LINES="${CHANGED_LINES:-0}"
    if [ "$CHANGED_LINES" -gt "$THRESHOLD" ]; then
        echo "⚠️  本次 push（${local_ref}）对 agate/*.md 的改动达 ${CHANGED_LINES} 行（阈值 ${THRESHOLD}）"
        echo "    建议先派发一次 protocol-alignment-review，确认改动未破坏协议文件间的语义一致性。"
        echo "    忽略本提示继续 push：git push --no-verify"
    fi
done

exit 0
```

> 注意保持 `set -euo pipefail`（与其他 gate 脚本一致）。**关键**：`grep -cE` 零匹配时 exit 1，在 `set -e` 下会终止脚本（`${VAR:-0}` 无法阻止——errexit 在命令替换赋值处就中断）。必须加 `|| true` 让管道 exit 0，再用 `:${VAR:-0}` 兜底。这是独立评审发现的 critical bug，原稿漏了 `|| true`。

- [ ] **Step 2: 验证可执行 + shellcheck**

```bash
chmod +x agate/scripts/pre-push-gate.sh
shellcheck -S warning agate/scripts/pre-push-gate.sh
```
预期：clean。

- [ ] **Step 3: Commit**

```bash
git add agate/scripts/pre-push-gate.sh
git commit -m "feat: 新建 pre-push-gate.sh 独立脚本 (v0.32.0)

从 install-hook.sh 内嵌 heredoc 模板抽出，便于软链安装 + 独立测试。
内容与模板一致（含 grep -c 双输出 bug 修复）。下一步 install-hook.sh 改软链。

self-gate-review: agate/scripts/pre-push-gate.sh"
```

---

### Task 2: install-hook.sh pre-push 安装改为软链

**Files:**
- Modify: `agate/scripts/install-hook.sh:52-75`

- [ ] **Step 1: 替换 pre-push 安装逻辑**

把当前 `cat > "$PRE_PUSH_HOOK" << 'HOOK_EOF' ... HOOK_EOF` 整段（L52-76，含最后的 `echo "pre-push hook 已安装..."`）替换为：

```bash
# 安装 pre-push hook（协议文件大改动自动提示 alignment-review）
# v0.32.0：与 pre-commit/commit-msg 统一为软链，bug 修复自动分发，无需重装
PRE_PUSH_HOOK="$HOOK_DIR/pre-push"
PRE_PUSH_SOURCE="$AGATE_ROOT/scripts/pre-push-gate.sh"

# 备份已有 pre-push hook（与 pre-commit/commit-msg 一致：仅备份非软链的既有 hook）
if [ -f "$PRE_PUSH_HOOK" ] && [ ! -L "$PRE_PUSH_HOOK" ]; then
    cp "$PRE_PUSH_HOOK" "$PRE_PUSH_HOOK.bak.$(date +%s)"
    echo "已备份现有 pre-push hook"
fi

[ ! -f "$PRE_PUSH_SOURCE" ] && { echo "错误: $PRE_PUSH_SOURCE 不存在（AGATE_ROOT=$AGATE_ROOT）" >&2; exit 1; }
ln -sf "$PRE_PUSH_SOURCE" "$PRE_PUSH_HOOK"
chmod +x "$PRE_PUSH_SOURCE"
echo "pre-push hook 已安装: $PRE_PUSH_HOOK -> $PRE_PUSH_SOURCE (协议文件大改动自动提示)"
```

> 补充（独立评审第 5 点）：pre-push 原有的 `cat >` 无备份逻辑，本方案顺手补上与 pre-commit/commit-msg 一致的 `[ -f ] && [ ! -L ]` 备份 guard，并加 `pre-push-gate.sh` 存在性检查（避免软链到缺失目标产生 dangling symlink）。

- [ ] **Step 2: 验证无残留预言 + shellcheck + 一致性**

```bash
grep -n 'HOOK_EOF\|CHANGED_LINES' agate/scripts/install-hook.sh   # 应无 HOOK_EOF / CHANGED_LINES
shellcheck -S warning agate/scripts/install-hook.sh
python3 agate/scripts/check-protocol-consistency.py
```
预期：无 HOOK_EOF/CHANGED_LINES 残留；shellcheck clean；consistency 0 ERROR。

- [ ] **Step 3: Commit**

```bash
git add agate/scripts/install-hook.sh
git commit -m "refactor: install-hook.sh pre-push 改软链统一 (v0.32.0)

与 pre-commit/commit-msg 统一为 ln -sf 软链。pre-push-gate.sh 独立脚本，
bug 修复自动分发，消除写死复制导致的升级滞后（T086 grep -c bug 教训）。

self-gate-review: agate/scripts/install-hook.sh"
```

---

### Task 3: 更新 pre-push-hook.bats 测试指向真实脚本

**Files:**
- Modify: `agate/tests/integration/pre-push-hook.bats`

**背景**：现有测试内嵌 heredoc 副本（会漂移）。改为通过 install-hook.sh 安装（软链到真实脚本），或直接 `bash "$AGATE_ROOT/scripts/pre-push-gate.sh"`。

- [ ] **Step 1: 重写测试 1（新分支首次推送）**

把内嵌 heredoc + 手动 `cat >` 改为通过 install-hook.sh 安装真实脚本：

```bash
@test "pre-push hook: 新分支首次推送提示跳过检测" {
    local repo
    repo=$(git_init)

    ( cd "$repo" && bash "$AGATE_ROOT/scripts/install-hook.sh" "$AGATE_ROOT" >/dev/null 2>&1 )
    [ -L "$repo/.git/hooks/pre-push" ] || fail "pre-push 应为软链"

    cd "$repo"
    echo "test" > file.txt
    git add file.txt
    git commit -m "init" --no-gpg-sign --no-verify

    run bash -c "echo 'refs/heads/main $(git rev-parse HEAD) refs/heads/main 0000000000000000000000000000000000000000' | bash '$AGATE_ROOT/scripts/pre-push-gate.sh' 2>&1 || true"

    [[ "$output" == *"新分支"* ]]
}
```

> 关键：直接运行 `pre-push-gate.sh` 而非 `$repo/.git/hooks/pre-push`（软链目标即此脚本，等价）。`[ -L ]` 断言软链安装。

- [ ] **Step 2: 重写测试 2（大改动触发提示）**

```bash
@test "pre-push hook: 大改动触发提示" {
    local repo
    repo=$(git_init)

    ( cd "$repo" && bash "$AGATE_ROOT/scripts/install-hook.sh" "$AGATE_ROOT" >/dev/null 2>&1 )

    cd "$repo"
    mkdir -p agate
    cat > "agate/test.md" <<'EOF'
line1
line2
line3
line4
EOF
    git add agate/test.md
    git commit -m "add agate file" --no-gpg-sign --no-verify

    local prev_sha
    prev_sha=$(git rev-parse HEAD)

    cat > "agate/test.md" <<'EOF'
line1-new
line2-new
line3-new
line4-new
line5-new
EOF
    git add agate/test.md
    git commit -m "big change" --no-gpg-sign --no-verify

    local current_sha
    current_sha=$(git rev-parse HEAD)

    run bash -c "echo 'refs/heads/main $current_sha refs/heads/main $prev_sha' | AGATE_ALIGNMENT_REVIEW_THRESHOLD=2 bash '$AGATE_ROOT/scripts/pre-push-gate.sh' 2>&1 || true"

    [[ "$output" == *"改动"* ]]
}
```

> 注意：原测试用 `THRESHOLD=2`（内嵌模板里硬编码）。现在阈值来自环境变量，需在调用时设 `AGATE_ALIGNMENT_REVIEW_THRESHOLD=2`。断言用 `*"改动"*`（脚本输出中文提示 `对 agate/*.md 的改动达 N 行`，不含 "WARNING" 字面量）。

- [ ] **Step 3: 重写测试 3（零匹配回归，T086）**

```bash
@test "pre-push hook: 无 agate/*.md 改动时零匹配 → 不报整数表达式错误（T086 回归）" {
    local repo
    repo=$(git_init)

    ( cd "$repo" && bash "$AGATE_ROOT/scripts/install-hook.sh" "$AGATE_ROOT" >/dev/null 2>&1 )

    cd "$repo"
    echo "test" > file.txt
    git add file.txt
    git commit -m "init" --no-gpg-sign --no-verify
    local prev_sha
    prev_sha=$(git rev-parse HEAD)

    echo "test2" > file.txt
    git add file.txt
    git commit -m "change" --no-gpg-sign --no-verify
    local current_sha
    current_sha=$(git rev-parse HEAD)

    run bash -c "echo 'refs/heads/main $current_sha refs/heads/main $prev_sha' | bash '$AGATE_ROOT/scripts/pre-push-gate.sh' 2>&1 || true"

    [[ "$output" != *"整数表达式"* ]]
    [[ "$output" != *"integer expression"* ]]
    [[ "$status" -eq 0 ]]
}
```

- [ ] **Step 4: 跑测试验证**

```bash
bats agate/tests/integration/pre-push-hook.bats
bats agate/tests/unit/install-hook.bats
```
预期：全部通过。

> 注意：测试 2 的断言已从 `*"WARNING"*` 改为 `*"改动"*`（脚本输出为中文），需确认新脚本输出含该字面量。

- [ ] **Step 5: Commit**

```bash
git add agate/tests/integration/pre-push-hook.bats
git commit -m "test: pre-push-hook.bats 改为指向真实 pre-push-gate.sh

移除内嵌 heredoc 副本（会漂移），通过 install-hook.sh 软链安装 + 直接运行
真实脚本。断言 [ -L ] 验证软链，阈值改用 AGATE_ALIGNMENT_REVIEW_THRESHOLD 环境变量。

self-gate-review: agate/tests/integration/pre-push-hook.bats"
```

---

### Task 4: 更新测试计数 + 收尾验证

**Files:**
- Modify: `agate/tests/README.md`

- [ ] **Step 1: 更新计数**

```bash
bash agate/tests/scripts/count-tests.sh
```
确认 pre-push-hook.bats 用例数不变（3 个），总数不变。核对 `agate/tests/README.md` 中 pre-push-hook 行（3）。

- [ ] **Step 2: 全量验证**

```bash
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
shellcheck -S warning agate/scripts/*.sh
python3 agate/scripts/check-protocol-consistency.py
```
预期：全绿 / clean / 0 ERROR。

- [ ] **Step 3: 版本 bump v0.32.0 + CHANGELOG**

README.md badge `v0.31.0` → `v0.32.0`。CHANGELOG.md 顶部加 `[v0.32.0]`，记录 pre-push 软链统一（非 BREAKING，内部重构）。

- [ ] **Step 4: Commit**

```bash
git add README.md CHANGELOG.md agate/tests/README.md
git commit -m "chore: v0.32.0

pre-push hook 从写死复制改为软链统一（pre-push-gate.sh 独立脚本），
bug 修复自动分发，消除升级滞后。非 BREAKING。

self-gate-review: agate/scripts/pre-push-gate.sh agate/scripts/install-hook.sh"
```

---

## Self-Review

**1. Spec coverage：**
- 抽独立脚本 → Task 1
- install-hook.sh 改软链 → Task 2
- 测试跟随 → Task 3
- 计数 + 版本 → Task 4
- 副作用分析已内化：cwd 无差异（git 以仓库根执行 hook）、stdin 参数无差异、不引用项目路径

**2. Placeholder scan：** 无 TBD；所有步骤含完整代码。

**3. Type consistency：** `pre-push-gate.sh` 在 Task 1 创建、Task 2 软链、Task 3 测试引用，命名一致。`AGATE_ALIGNMENT_REVIEW_THRESHOLD` 环境变量在脚本（Task 1）与测试（Task 3 Step 2）一致。

**已识别风险：**
- **[评审 critical] `set -euo pipefail + grep -c` 零匹配会终止脚本**：原稿 `grep -cE ...` 无 `|| true`，在 `set -e` 下零匹配退出会中止 pre-push（阻塞所有无 agate/*.md 改动的 push）。已改为 `grep -cE ... || true` + `:${VAR:-0}`（实测验证正确）。
- **[评审] Task 3 Test 2 断言矛盾**：代码块写 `*"WARNING"*` 但注释说 `*"改动"*`，已统一为 `*"改动"*`（脚本输出中文提示）。
- **[评审] pre-push 缺备份逻辑**：已补 `[ -f ] && [ ! -L ]` 备份 guard + 源文件存在性检查（与 pre-commit/commit-msg 一致）。

**评审记录（独立评审 2 轮）：**
- 第 1 轮：✗ CRITICAL：add `set -euo pipefail` 后 `${VAR:-0}` 无法阻止 grep -c 零匹配的 errexit 中止 → 加 `|| true`（Task 1）；✗ Task 3 Step 2 断言 `*"WARNING"*` 与注释 `*"改动"*` 矛盾 → 统一 `*"改动"*`；✗ pre-push 无备份逻辑 → Task 2 补 `[ -f ] && [ ! -L ]` guard
- 第 2 轮（GO）：✓ 3 修复均验证正确；✗ L52-75 vs L52-76 边界 → 改为 L52-76。无阻断项