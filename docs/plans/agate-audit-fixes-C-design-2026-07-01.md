---
task_id: agate-audit-fixes-C
agent: main
date: 2026-07-01
status: 设计文档（已修订 v2，评审修订已纳入）
来源: docs/plans/agate-audit-fixes-2026-07-01.md §C + docs/reviews/agate-audit-fixes-plan-review-2026-07-01.md §C
---

# C 组设计：裁剪条件偏差修复（4 项）

## 变更清单

| # | 问题 | 修改文件 | 修改类型 |
|---|------|----------|----------|
| #5 | P3 裁剪文档 "需 risk_level=low" → 脚本只禁 high | state-machine.md:165 | 文档 |
| #7 | 检查 7 跳过风险条件漏 P6 | check-pruning.sh:104 | 脚本 |
| #8 | P8 裁剪缺 internal_only_reason 理由字段检查 | check-pruning.sh:96-101 + state-machine.md:168 + task-files.md:142-148 + v060-p8-internal-only.bats R4.2 | 脚本+文档+测试 |
| #10 | P2 候选方案缺 form check（权衡/选择理由） | check-gate.sh:28-31 | 脚本 |

## 详细设计

### #5 P3 裁剪条件：改文档对齐脚本

**现状**：state-machine.md:165 写"需 risk_level=low（high 风险不可裁）"，但脚本 check-pruning.sh:70-74 只在 `risk_level=high` 时拦截，medium 放行。测试 P2.5b 明确注释"medium 风险 + P3 裁剪是允许的"。

**决策**：改文档。脚本+测试一致允许 medium，medium 是中间态，允许裁剪 P3（TDD）合理。

**改动**：
```markdown
# state-machine.md:165
# 当前：裁剪 P3：需 risk_level=low（high 风险不可裁）
# 改为：裁剪 P3：high 风险不可裁
```

### #7 检查 7 跳过风险条件加 P6

**现状**：check-pruning.sh:104 条件 `! P2 || ! P3 || ! P7 || ! P8`，漏了 P6。P6 裁剪（no_behavior_change: true）也应写"跳过风险"评估。

**决策**：修脚本加 P6。

**改动**：
```bash
# check-pruning.sh:104
# 当前：
if ! echo "$PHASES_DECLARED" | grep -qw 'P2' || ! echo "$PHASES_DECLARED" | grep -qw 'P3' || ! echo "$PHASES_DECLARED" | grep -qw 'P7' || ! echo "$PHASES_DECLARED" | grep -qw 'P8'; then
# 改为：
if ! echo "$PHASES_DECLARED" | grep -qw 'P2' || ! echo "$PHASES_DECLARED" | grep -qw 'P3' || ! echo "$PHASES_DECLARED" | grep -qw 'P6' || ! echo "$PHASES_DECLARED" | grep -qw 'P7' || ! echo "$PHASES_DECLARED" | grep -qw 'P8'; then
```

### #8 P8 裁剪加 internal_only_reason 理由字段检查

**现状**：check-pruning.sh:96-101 只查 `internal_only: true`，不查理由字段。state-machine.md:168 写"需声明 internal_only: true + 理由"但未指定字段名。task-files.md P1 模板无 `internal_only` 字段。

**决策**：修脚本加 if/elif 理由检查 + 建立字段名 + 更新文档和模板。

**改动**：

1. **check-pruning.sh:96-101**（嵌套 if 结构，评审修订：原 if/elif 逻辑反转）：
```bash
# 当前：
if ! echo "$PHASES_DECLARED" | grep -qw 'P8'; then
    if ! grep -qE '^internal_only:\s*true' "$P1_FILE" 2>/dev/null; then
        ERRORS="${ERRORS}裁剪 P8 需声明 internal_only: true + 理由\n"
    fi
fi

# 改为（嵌套 if，与检查 2/3/4/5/6 结构一致）：
if ! echo "$PHASES_DECLARED" | grep -qw 'P8'; then
    if ! grep -qE '^internal_only:\s*true' "$P1_FILE" 2>/dev/null; then
        ERRORS="${ERRORS}裁剪 P8 需声明 internal_only: true\n"
    elif ! grep -qE '^internal_only_reason:' "$P1_FILE" 2>/dev/null; then
        ERRORS="${ERRORS}裁剪 P8 需 internal_only: true + 理由（internal_only_reason: 字段缺失）\n"
    fi
fi
```

2. **state-machine.md:168**：
```markdown
# 当前：裁剪 P8：需声明 internal_only: true + 理由
# 改为：裁剪 P8：需声明 internal_only: true + internal_only_reason: <理由>
```

3. **task-files.md:144-148**（P1 模板裁剪说明区补字段示例）：
```markdown
# 在 phases 行后、跳过理由前，补：
# internal_only: true                      # P8 裁剪时必填
# internal_only_reason: 内部工具，无外部用户  # P8 裁剪时必填
```

4. **v060-p8-internal-only.bats R4.2**（同步更新）：
```bash
# 当前：只加 internal_only: true → exit 0
# 改后：加 internal_only: true + internal_only_reason: ... → exit 0
# 只加 internal_only: true 无 reason → exit 1（新测试）
```

### #10 P2 候选方案 form check

**现状**：check-gate.sh:28-31 只查候选方案数量 ≥2，不查"权衡"或"选择理由"。echo 消息声称检查"权衡 + 选择理由"但实际不查——这是假锚点。

**决策**：加 form check（nudge，与"跳过风险:"同一设计模式）。放在 `[ -f "$P2_FILE" ]` 块内部，`CANDIDATE_COUNT < 2` 检查之后（评审修订：`$CANDIDATE_COUNT` 在 if 块内定义，块外 `set -u` 会报 unbound variable）。

**改动**：
```bash
# check-gate.sh P2 case，在 [ -f "$P2_FILE" ] 块内，CANDIDATE_COUNT < 2 检查之后加：
    if ! grep -qE '权衡|选择理由' "$P2_FILE" 2>/dev/null; then
        echo "GATE P2: P2-design.md 有 ≥2 候选方案但缺'权衡'或'选择理由'描述" >&2
        exit 1
    fi
```

注意：C+D 合并修改 check-gate.sh 时，放置顺序为 count check → status:approved（D#13）→ form check（C#10）→ exit 2。C 组先实施 form check，D 组后续补 status:approved 在 form check 之前。

## 测试计划

### check-pruning.bats 新增

| ID | 描述 | 期望 |
|----|------|------|
| P2.12 | P6 裁剪无"跳过风险" | exit 1，含"跳过风险" |
| P2.12a | P6 裁剪 + no_behavior_change + 跳过风险 | exit 0（happy path，评审修订补充） |
| P2.13 | P8 裁剪有 internal_only 无 reason | exit 1，含"internal_only_reason" |
| P2.14 | P8 裁剪有 internal_only + internal_only_reason | exit 0（happy path） |

### check-pruning.bats 修改（变红测试同步更新）

| ID | 变更 |
|----|------|
| P2.7a | 加 `add_p1_field "$dir" "internal_only_reason" "内部工具"` 使其继续 exit 0（评审修订补充） |

### check-gate.bats 新增

| ID | 描述 | 期望 |
|----|------|------|
| G2.8 | P2 候选方案 ≥2 但无"权衡" | exit 1，含"权衡" |
| G2.9 | P2 候选方案 ≥2 + 含"权衡" | exit 2（happy path） |

### v060-p8-internal-only.bats 修改

| ID | 变更 |
|----|------|
| R4.2 | 加 `internal_only_reason: 内部工具` → exit 0 |
| R4.3（新增） | 只加 `internal_only: true` 无 reason → exit 1 |

## 隐藏依赖

1. **R4.2 会变红**：改 P8 理由检查后，现有 R4.2 只加 `internal_only: true` 不再加 reason，会 exit 1。必须在同一次修改中更新。
2. **P2.7a 也会变红**：现有 P2.7a 只加 `internal_only: true` + 跳过风险，改后缺 `internal_only_reason` 会 exit 1。必须同步更新（已列入测试计划）。
3. **C+D 合并 check-gate.sh**：C#10 form check 和 D#13 status:approved 都在 P2 case 内。C 组先放 form check，D 组后续在 form check 前插入 status:approved。
4. **CHECK 9 锚点**：P8 锚点当前关键词 `internal_only`，改后代码仍含 `internal_only`，锚点不受影响。建议后续追加 `internal_only_reason` 到锚点关键词列表。

## 不做的事

- 不改 P3 裁剪脚本逻辑（脚本行为正确，是文档滞后）
- 不改 P6 裁剪条件本身（no_behavior_change: true 门槛不变，只补跳过风险 nudge）
