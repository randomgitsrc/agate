---
review_date: 2026-07-21
reviewer: protocol-alignment-review
round: 2
change_summary: 复查 round 1 A1.3 MISALIGNED (Bug 3 fallback 缺失) 的修复情况
based_on:
  plan: docs/plans/agate-t060-retro-bugfixes-20260721.md (updated)
  round_1_review: docs/reviews/agate-alignment-review-t060-bugfixes-2026-07-21.md
---

# 协议-脚本对齐审查 (v2, Round 2)

## Round 1 遗留问题

Round 1 发现 **1 MISALIGNED**：A1.3 (Bug 3) — 计划文字声称 fallback，但代码 diff 缺失，regex 后缀集无 `-`，测试 3c 与代码矛盾。

Round 1 建议：「补齐 fallback：短前缀 regex 失败后尝试 `grep -qF "$TASK_ID"`；或扩展 regex 后缀集 `( |:|-|$|,)`」。

## Round 2 复查

### 检查项 1：fallback 逻辑

**Round 1 发现**：原 code diff 仅一条 regex，无 `grep -qF "$TASK_ID"` fallback。

**Updated plan (lines 180-188)**：

```bash
+ if echo "$UNRELEASED_CONTENT" | grep -qE "(^|[^0-9])${TASK_ID_SHORT}( |:|$|,|-)" 2>/dev/null; then
+     exit 0
+ fi
+ # fallback: 尝试完整 task_id 固定字符串匹配（如 CHANGELOG 写了完整目录名）
+ if echo "$UNRELEASED_CONTENT" | grep -qF "$TASK_ID" 2>/dev/null; then
+     exit 0
+ fi
+ echo "GATE CHANGELOG: [Unreleased] 区域未找到 ${TASK_ID_SHORT}（或 ${TASK_ID}）" >&2
+ exit 1
```

**结论**：**已修复**。两步匹配：regex 短前缀 → `grep -qF "$TASK_ID"` fallback。描述文字（line 162）更新为「分两步匹配」，与代码一致。

---

### 检查项 2：regex 后缀含 `-`

**Round 1 发现**：regex 后缀集 `( |:|$|,)` 缺 `-`，`T060-archived-visibility-auth-refresh:` 中 `T060` 后跟 `-` 无法匹配。

**Updated plan (line 180)**：

```
grep -qE "(^|[^0-9])${TASK_ID_SHORT}( |:|$|,|-)"
```

`-` 已添加到后缀字符集中。

**验证**：line 195 明确说明「`-` 在后缀集合中：`T060-archived-visibility-auth-refresh:` 中 `T060` 后的 `-` 会触发匹配」。

**结论**：**已修复**。

---

### 检查项 3：测试 3c 修复

**Round 1 发现**：测试 3c 期望 fallback 匹配 `T060-archived-visibility-auth-refresh: 条目`，但原 regex 无法匹配此行。

**Updated plan (lines 233-247)**：

```bash
@test "CHANGELOG 含 T060-archived-visibility-auth-refresh: 时后缀 - 正确匹配" {
    ...
    - T060-archived-visibility-auth-refresh: 条目
    ...
    [ "$status" -eq 0 ]
}
```

测试名更新为「后缀 `-` 正确匹配」，说明匹配路径改为 regex step 1（`T060` 后跟 `-` 触发 regex 匹配，无需 fallback）。

**匹配路径分析**：
- `T060` 前为空格 → `[^0-9]` 匹配 ✓
- `T060` 后为 `-` → suffix `-` 匹配 ✓
- Step 1 regex 直接匹配 → exit 0 ✓

**结论**：**已修复**。测试逻辑与代码行为一致。

---

### 检查项 4：无新问题

逐项排查：

| 检查维度 | 状态 |
|----------|------|
| Bug 1 diff (inject-card) | 未变更，ALIGNED ✓ |
| Bug 2 diff (SCOPE+ dispatch-context) | 未变更，ALIGNED ✓ |
| Bug 4 diff (P5 WARNING) | 未变更，ALIGNED ✓ |
| Bug 3 描述文字与代码一致性 | 已统一（"分两步匹配"） ✓ |
| `2>/dev/null` 对 grep 非零返回值的安全性 | 正确：exit 2 → if 为 false → 进入下一步或 fallback ✓ |
| regex 特殊字符注入 | 无风险：`TASK_ID_SHORT` 来自 `T[0-9]+` 提取，仅含字母数字 ✓ |
| 测试 3a (短前缀 T060) | `T060:` → `:` in suffix → 匹配 ✓ |
| 测试 3b (T0601 不误匹配) | `T0601` → `1` not in suffix → 不匹配 → fallback 也不匹配 → exit 1 ✓ |
| Bug 5 记录 | 仍列为"不修"，LIMITATIONS.md 局限3 已记录 ✓ |
| 实施顺序 | 未变更 ✓ |

**结论**：**无新问题引入**。

---

## 最终审查结论

### A1-A7 表

| # | 审查项 | Round 1 | Round 2 | 变更说明 |
|---|--------|---------|---------|----------|
| A1 | 文档→脚本对齐 | MISALIGNED (A1.3) | **ALIGNED** | Bug 3 已补 fallback + regex `-` 后缀 |
| A2 | 脚本→文档对齐 | ALIGNED | ALIGNED | 无变更 |
| A3 | 一致性连锁 + 反向传播 | ALIGNED | ALIGNED | 无变更 |
| A4 | 测试覆盖 | NEEDS_HUMAN_REVIEW | NEEDS_HUMAN_REVIEW | 测试 3c 矛盾已解，但仍缺 bats 实跑输出 |
| A5 | 下游影响 + 文档传播 | ALIGNED | ALIGNED | 无变更 |
| A6 | 锚点表覆盖 | ALIGNED | ALIGNED | 无变更 |
| A7 | 设计原则一致性 | ALIGNED | ALIGNED | 无变更 |

### 总体判决

**0 MISALIGNED** — Round 1 的 A1.3 问题全部修复（fallback 补齐、`-` 入 suffix、测试 3c 更新）。无新问题引入。

**1 NEEDS_HUMAN_REVIEW** (A4) — 保持与 round 1 一致：测试代码仍为设计草案，实施后需跑全量 bats 并附 passed/failed 计数。

**计划可推进实施。**

---

## 审查时间

2026-07-21 (round 2)。仅复查 Bug 3 修复 + 全局一致性扫描。
