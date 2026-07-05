---
review_date: 2026-07-05
reviewer: protocol-alignment-review
change_summary: 两变更 — (1) commit-msg self-gate ^ 行锚假阴性修复 (9ce2eda, 已含在 v0.9.0 内), (2) dispatch-context 强制化范围收窄为仅产出 commit (a25512c, post-v0.9.0)
files_changed:
  - agate/scripts/commit-msg-self-gate.sh (^ anchor fix)
  - agate/scripts/pre-commit-gate.sh (scope narrowing: STAGED_IN_TASK + PHASE_OUTPUT)
  - agate/tests/integration/dispatch-context-card.bats (DC.4/DC.5 更新)
  - agate/tests/integration/pre-commit-hook.bats (IT.2/6/8/10 dispatch-context fixtures)
---

# 协议-脚本对齐审查

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | NEEDS_HUMAN_REVIEW |
| A4 | 测试覆盖 | ALIGNED |
| A5 | 下游影响 + 文档传播 | NEEDS_HUMAN_REVIEW |
| A6 | 锚点表覆盖 | ALIGNED |

## 关键证据

### 实跑验证

| 检查 | 结果 |
|------|------|
| bats 全量 | **221/221 OK** |
| check-protocol-consistency.py | **0 ERROR** (1 WARNING: YAML quoting, 无关) |
| shellcheck (2 scripts) | **0 error** (1 info: SC1091, 无关) |
| ^ anchor 实跑 | 行首 `self-gate-review:` match ✓ / 行中 `refs self-gate-review:` no-match ✓ / OLD pattern 行中 MATCHES (false positive confirmed) |
| scope narrowing 5a | P2 state-only → pruning blocked (NOT dispatch-context) ✓ |
| scope narrowing 5b | P2 + P2-design.md → dispatch-context barrier "需提供 P2-dispatch-context.md" ✓ |
| scope narrowing 5c | P5 → 不触发 dispatch-context ✓ |
| DC.4 bats | P2 产出缺 DC → exit 1 ✓ |
| DC.5 bats | P5 缺 DC → 不拦截 ✓ |
| IT.2/6/8/10 bats | dispatch-context fixture 化后全通过 ✓ |

---

## 逐项审查

### A1: 文档→脚本对齐

**变更 1: ^ anchor fix (9ce2eda)**

**文档声明** (SELF-GATE.md:8):
> commit message 须含 `self-gate-review:` 路径（或 `self-gate-skip:` 理由），否则 WARNING

**脚本实现** (commit-msg-self-gate.sh:23,26):
```bash
if echo "$COMMIT_MSG" | grep -qE '^self-gate-skip:\s*\S+'; then
if echo "$COMMIT_MSG" | grep -qE '^self-gate-review:\s*\S+'; then
```

**结论**: ALIGNED — ^ 锚是 grep 实现细节，文档描述「须含」语义一致。文档未指定必须行首，但示例用法（echo 输出格式 L32-35）均以行首展示，隐含行首语义。

---

**变更 2: scope narrowing (a25512c)**

**文档声明** — 无直接协议文档描述此粒度的 hook 行为。dispatch-protocol.md L259-276 描述 dispatch-context.md 的用途（客观信息落盘），不描述 hook enforcement 条件。

**脚本实现** (pre-commit-gate.sh:165-185):
```bash
STAGED_IN_TASK=$(git diff --cached --name-only 2>/dev/null | grep "^${TASK_REL}/" || true)
case "$PHASE" in
    P1) PHASE_OUTPUT="P1-requirements\.md" ;;
    P2) PHASE_OUTPUT="P2-design\.md" ;;
    P3) PHASE_OUTPUT="P3-test-cases\.md" ;;
    P6) PHASE_OUTPUT="P6-acceptance\.md" ;;
esac
if [ -n "$PHASE_OUTPUT" ] && echo "$STAGED_IN_TASK" | grep -q "$PHASE_OUTPUT"; then
    # barrier fires only when output file is staged
```

**结论**: ALIGNED — 无文档漂移。dispatch-context barrier 的触发条件是 hook 层面的实现细节，协议文档未描述此粒度。

---

### A2: 脚本→文档对齐

两个变更均为脚本行为变更，不涉及协议文档语义变更。无文档需同步。

**结论**: ALIGNED

---

### A3: 一致性连锁 + 反向传播

#### A3a: 连锁（已知衍生改动）

| 改了 | 衍生改动 | 状态 |
|------|---------|------|
| commit-msg-self-gate.sh ^ anchor | 无 — 纯脚本 bugfix，不影响其他文件 | N/A |
| pre-commit-gate.sh scope narrowing | DC.4/DC.5 bats 测试更新 | 已实现 ✓ |
| pre-commit-gate.sh scope narrowing | IT.2/6/8/10 bats 加 dispatch-context fixture | 已实现 ✓ |

#### A3b: 反向传播（应被影响但未在 diff 中的文件）

| 应被影响文件 | 理由 | 状态 |
|-------------|------|------|
| CHANGELOG.md L14 (v0.9.0) | 声明 "P1/P2/P3/P4/P6 派发阶段**强制要求** dispatch-context.md 存在，缺则 exit 1" — 收窄后语义变松（仅产出 commit 时强制），v0.9.0 历史记录准确但 [Unreleased] 应标注此变更 | **见 A5** |
| CHANGELOG.md [Unreleased] | 目前为 "(空)"，a25512c scope narrowing 未被记录 | **见 A5** |
| dispatch-protocol.md | 描述 dispatch-context 用途（客观信息落盘），不描述 hook enforcement 粒度，无需同步 | 无需 ✓ |
| SELF-GATE.md | 不描述 dispatch-context barrier 细节，无需同步 | 无需 ✓ |
| LIMITATIONS.md | 无 dispatch-context barrier 描述 | 无需 ✓ |

**结论**: NEEDS_HUMAN_REVIEW — A3a 无问题。A3b 的 CHANGELOG 缺口在 A5 中一并处理。

---

### A4: 测试覆盖

| 变更 | 测试 | 覆盖 |
|------|------|------|
| ^ anchor fix | CSG.1-CSG.6 (commit-msg self-gate bats) + SG.7 (存在性+可执行) | 行为已有测试覆盖，^ anchor 改变的是 grep pattern 精度，原测试仍通过（pattern 精确化不破坏现有行为） |
| scope narrowing | DC.4 更新为"产出 commit 缺 DC → exit 1"，DC.5 保留"P5 不拦截" | 边界覆盖 ✓ |
| scope narrowing | IT.2/6/8/10 补 dispatch-context fixture，确保 phase 变更 commit 不被错拦 | 退化防护 ✓ |
| scope narrowing | 221/221 全量 bats 通过 | 无回归 ✓ |

**结论**: ALIGNED — 测试覆盖了 scope narrowing 的正向（barrier 触发）和负向（barrier 不触发）路径。

---

### A5: 下游影响 + 文档传播

#### 下游影响

| 维度 | 评估 |
|------|------|
| 现有项目 gate 行为 | **后向兼容 relax**：dispatch-context barrier 从"所有派发阶段 commit"收窄为"产出 commit"。已发布 v0.9.0 项目的 gate 变松（更少被拦），不产生新的阻塞 |
| 破坏性变更 | 无 — 宽→严才算破坏性，严→宽是 bugfix |
| 版本 bump | a25512c 是 post-v0.9.0 bugfix，需在 [Unreleased] 标注，下次发版时 bump patch |

#### 文档传播

| 应被传播到 | 状态 | 说明 |
|-----------|------|------|
| CHANGELOG.md [Unreleased] | **缺失** | a25512c scope narrowing 未记录 |
| CHANGELOG.md L14 (v0.9.0) | **准确** | v0.9.0 发布时确为全量 barrier，历史记录无需修改 |

**结论**: NEEDS_HUMAN_REVIEW — CHANGELOG.md [Unreleased] 需补充 a25512c 条目。建议内容：

```
- **dispatch-context 强制化收窄**：从"派发阶段 ALL commits 强制"改为"仅产出 commit 强制"。
  中间 commit / legacy 任务 / 裁剪跳阶不再拦截。pre-commit-gate.sh 2p 加 STAGED_IN_TASK 检查。
```

[HUMAN_CONFIRMED: 待确认]

---

### A6: 锚点表覆盖

| 脚本 | CHECK 9 覆盖 | 说明 |
|------|-------------|------|
| commit-msg-self-gate.sh | 不在锚点表 | 正确 — 这是 hook 脚本，非 gate check 脚本。SG.6 检查的是 `check-*.sh` + `pre-commit-gate.sh` 共 11 个 |
| pre-commit-gate.sh | 在锚点表 ✓ | SG.6 + CHECK 9 PASS 确认 |
| 全量 | 221/221 ✓ | SG.6 确认 11 个 gate 脚本全覆盖 |

**结论**: ALIGNED

---

## 附录：注意事项

### 9ce2eda 不在 "since v0.9.0" 范围内

```
v0.9.0 tag lineage:
  9ce2eda (^ anchor fix)
    → f53e4cc (dispatch-context 强制化 feat)
      → 476224d (v0.9.0 tag)
        → 0276200 (v0.9.0 发布评审 docs)
          → a25512c (scope narrowing)
```

`9ce2eda` 是 v0.9.0 的祖先，已包含在 tag 内。实际 "since v0.9.0" 的变更仅有 `a25512c`（和纯 docs commit `0276200`）。^ anchor fix 在 v0.9.0 CHANGELOG L17 已有记录，无需本次额外处理。

### scope narrowing 实跑验证注记

5a/5c/5d 的完整 e2e 验证受其他 gate（pruning、P4 gate、check-state-yaml）先触发影响，dispatch-context barrier 在这些 case 中未被触发（因其他 gate 先 exit 1）。通过以下方式独立验证 scope narrowing 正确性：

1. **DC.4 bats**：P2 + P2-design.md staged + 缺 DC → barrier fires ✓
2. **DC.5 bats**：P5 不触发 barrier ✓
3. **5b 实跑**：P2 + P2-design.md → dispatch-context barrier 消息正确输出 ✓
4. **代码审查**：`STAGED_IN_TASK` + `PHASE_OUTPUT` 匹配逻辑正确（pre-commit-gate.sh:165-185）
