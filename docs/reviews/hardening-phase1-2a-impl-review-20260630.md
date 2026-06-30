# Phase 1 + 2A 实施评审

> 评审对象：`58e2a2f` → `aa2b471`，14 次提交
> 评审日期：2026-06-30
> 评审定位：实现后代码评审，找出会导致静默失效或语义错误的 bug

---

## 总体判断

**架构正确，6 项评审修订全部落地，端到端验证通过。但有 2 个 🔴 级 bug 与之前 `has_staged_phase_change` 同根——绝对路径 vs 相对路径不匹配——导致 `check-state-transition.sh` 完全失效（永远 exit 0，状态转移检查从未运行）。另有 2 个 🟠 影响可靠性，1 个 🟡 需对齐协议。**

---

## 🔴 阻断级（必须修）

### R1：`check-state-transition.sh` 路径不匹配——状态转移检查从未运行

**位置**：`scripts/check-state-transition.sh:40`

```bash
git diff --cached --name-only 2>/dev/null | grep -qF "$STATE_FILE" || exit 0
```

**问题**：`pre-commit-gate.sh:52` 传入的 `$STATE_FILE` 是绝对路径（`$REPO_ROOT/.state.yaml`），但 `git diff --cached --name-only` 返回相对路径（`.state.yaml`）。`grep -qF` 用绝对路径匹配相对路径输出，永远不命中，脚本直接 `exit 0`。

**影响**：P2.3（phase 跳变合法性）、P2.4（重试超限）、P2.5（回退跳变检测）**全部从未执行过**。端到端验证通过是因为验证只测了 gate 执行和 PROD_TOUCHED，没测状态转移检查。

**这是 `has_staged_phase_change` 同一个 bug 的翻版**——那个在实现中被发现并修复了（用 `basename`），但 `check-state-transition.sh` 没有同步修复。

**修法**：与 `has_staged_phase_change` 相同，用 `basename` 匹配：

```bash
local basename
basename=$(basename "$STATE_FILE")
git diff --cached --name-only 2>/dev/null | grep -qF "$basename" || exit 0
```

### R2：`check-state-transition.sh` 的 `get_old_phase()` 用绝对路径调用 `git show`——永远返回空

**位置**：`scripts/check-state-transition.sh:15`

```bash
git show :"${STATE_FILE}" 2>/dev/null | python3 -c "..."
```

**问题**：`git show :<path>` 的 `<path>` 是 pathspec，不是文件系统路径。`git show :/home/kity/.agate/.state.yaml` 返回空（实测确认），`git show :.state.yaml` 正常返回。`$STATE_FILE` 是绝对路径，所以 `get_old_phase()` 永远返回空字符串。

**影响**：即使 R1 修了，`old_phase` 永远是空字符串，`phase_num` 返回 `"0"`，回退跳变检测的 `old_num=0` 导致条件 `old_num -gt 0` 不满足，检查 1 永远不触发。

**修法**：用 `basename` 或相对路径：

```bash
get_old_phase() {
    local basename
    basename=$(basename "${STATE_FILE}")
    git show :"$basename" 2>/dev/null | python3 -c "..."
}
```

**同理 `get_new_phase()` 的 `python3 -c "with open('$STATE_FILE')"` 用绝对路径是没问题的**（Python 的 `open()` 接受绝对路径），但 `git show` 不接受。

---

## 🟠 高优先级

### O1：`check-state-transition.sh` 的 `git diff --cached -- "$STATE_FILE"` 也用绝对路径

**位置**：`scripts/gate-result.sh:63`（`has_staged_phase_change` 函数）

```bash
git diff --cached -- "$state_file" 2>/dev/null | grep -qE '^\+.*phase:' || return 1
```

**问题**：虽然 `basename` 修复让第一个 `grep` 匹配成功了，但这一行的 `git diff --cached -- "$state_file"` 仍然用绝对路径。实测 `git diff --cached -- /home/kity/.agate/.state.yaml` 返回空（git 不认绝对路径作为 pathspec）。

**影响**：`has_staged_phase_change` 即使 `basename` 匹配成功（文件在暂存区），这一行也会因为 `git diff` 返回空而 `return 1`。整个函数返回"未检测到 phase 变更"，gate 不触发。

**验证**：端到端测试时 gate 确实触发了——但那是因为 `has_staged_phase_output` 也匹配了（`.state.yaml` 被误匹配？不，实测 `.state.yaml` 不匹配 `P[0-9]+-` 正则）。**需要重新验证**：端到端测试时 gate 触发是因为 `has_staged_phase_change` 返回 true 还是 `has_staged_phase_output` 返回 true？

**修法**：

```bash
has_staged_phase_change() {
    local state_file="$1"
    local basename
    basename=$(basename "$state_file")
    git diff --cached --name-only 2>/dev/null | grep -qF "$basename" || return 1
    git diff --cached -- "$basename" 2>/dev/null | grep -qE '^\+.*phase:' || return 1
    return 0
}
```

### O2：`.gate-history.jsonl` 包含测试数据，已提交到仓库

**位置**：`.gate-history.jsonl`（已提交）

```json
{"phase":"P6","task_id":"TEST001","exit_code":2,"timestamp":"2026-06-30T08:35:00Z","prev_commit_sha":"0675a2729b0e85d7395349ac4a3cb86914153736"}
```

**问题**：端到端测试产生的测试数据被提交到了仓库的 `.gate-history.jsonl`。这个文件应该是运行时累积的历史记录，不是仓库内容。测试数据会污染真实审计链。

**修法**：清空 `.gate-history.jsonl`（保留空文件或删除），加入 `.gitignore`——与 `.gate-result.json` 同理，每次运行由 hook 追加。

**但 roadmap 设计说 `.gate-history.jsonl` 应该进 git 作为审计链**。这需要重新考虑：如果进 git，测试数据需要清理；如果不进 git，审计链就不完整。

**建议**：`.gate-history.jsonl` 加入 `.gitignore`（不进 git），因为它的内容是项目运行时数据，不是协议内容。审计链在本地保留，CI 通过 `.gate-result.json` 对照即可。

---

## 🟡 中优先级

### M1：`.gitignore` 缺少 `.state.yaml`

**位置**：`.gitignore`

**问题**：端到端测试创建了 `.state.yaml` 并提交了它（commit `0675a27`），后来又删除了。但 `.gitignore` 没有加入 `.state.yaml`。`.state.yaml` 是项目运行时状态文件，不是 agate 协议仓库的内容——agate 仓库本身不应该有 `.state.yaml`。

**修法**：`.gitignore` 追加：

```
# agate 运行时状态（项目级，不是协议仓库内容）
.state.yaml
```

### M2：测试 commit 混入主分支历史

**位置**：`git log` — 有 4 个 `test:` 前缀的 commit（`4b87eb9`、`0675a27`、`2c6cbd7`、`09a4eac`）在 main 分支上

**问题**：端到端验证的测试 commit 不应该在 main 分支上。它们包含了测试用的 `.state.yaml` 和测试数据，虽然后来清理了，但 git 历史里留下了痕迹。

**影响**：不影响功能，但历史不够干净。对于 agate 这种协议仓库，历史可读性有一定价值。

**建议**：不需要 `git rebase` 清理（风险大于收益），但未来验证应该在单独的分支上进行。

---

## 设计层面确认正确的部分

**R1 修复（source 验证）正确落地。** `pre-commit-gate.sh:18-21` 在 `source` 后用 `type write_gate_result` 验证函数已加载。如果 `gate-result.sh` 不存在或语法错误，hook 会明确报错并 `exit 1`，不会静默放行。

**R2 修复（PROD_TOUCHED 扫 diff）正确落地。** `pre-commit-gate.sh:45` 用 `git diff --cached | grep -q '\[PROD_TOUCHED\]'`，只扫描暂存变更内容，不扫文件全文。修改含 PROD_TOUCHED 字样的协议文件不会被误拦。

**O1 修复（回退检测降级 WARNING）正确落地。** `check-state-transition.sh:58` 输出警告但不 `exit 1`，与协议"不依赖 commit message"的原则一致。

**O2 修复（retries 列表结构）正确落地。** `check-state-transition.sh:74` 用 `isinstance(attempts, list) and len(attempts) >= MAX_RETRY`，与 `.state.yaml` 的列表结构匹配。

**O3 修复（prev_commit_sha）正确落地。** `gate-result.sh:18` 字段名为 `prev_commit_sha`，注释明确"pre-commit hook 在 commit 创建之前运行，HEAD 是上一个 commit"。

**M1 修复（P6 证据退化为现有格式）正确落地。** `check-p6-evidence.sh` 用 `- PASS/- FAIL` 行计数 + `P6-evidence/` 目录非空检查，不依赖未定义的 `## BDD-NN` 格式。

**exit code 语义贯穿一致。** exit 0 = 通过，exit 1 = 中止 commit，exit 2 = 允许 commit 但记录"需判断"——与 check-gate.sh 语义对齐。

**CI workflow 正确追加。** `gate-backstop` job 独立于 `check` job，不会因为一致性检查 WARNING 而被阻塞。

---

## 修复优先级汇总

| # | 问题 | 严重度 | 影响 | 修复位置 |
|---|------|--------|------|---------|
| R1 | check-state-transition.sh 路径不匹配 | 🔴 | 状态转移检查从未运行 | check-state-transition.sh:40 |
| R2 | get_old_phase() git show 用绝对路径 | 🔴 | old_phase 永远为空 | check-state-transition.sh:15 |
| O1 | has_staged_phase_change 的 git diff -- 用绝对路径 | 🟠 | phase 变更检测可能失效 | gate-result.sh:63 |
| O2 | .gate-history.jsonl 含测试数据 | 🟠 | 审计链污染 | .gate-history.jsonl + .gitignore |
| M1 | .gitignore 缺 .state.yaml | 🟡 | 测试残留 | .gitignore |
| M2 | 测试 commit 在 main 分支 | 🟡 | 历史不干净 | —（不修，记录教训） |

**建议执行顺序**：R1 + R2（同一文件，一起修）→ O1 → O2 + M1（一起修）→ 重新验证状态转移检查。
