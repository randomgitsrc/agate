---
task_id: agate-audit-fixes-C-design-review
agent: main
date: 2026-07-01
status: 评审完成
评审对象: docs/plans/agate-audit-fixes-C-design-2026-07-01.md
来源: docs/plans/agate-audit-fixes-2026-07-01.md §C + docs/reviews/agate-audit-fixes-plan-review-2026-07-01.md §C
---

# C 组设计文档评审

## 评审方法

逐条对照设计文档的 #5/#7/#8/#10 项，结合以下源文件验证：

- `agate/scripts/check-pruning.sh`（#7/#8 修改对象）
- `agate/scripts/check-gate.sh`（#10 修改对象）
- `agate/state-machine.md:160-175`（裁剪条件表）
- `agate/assets/templates/task-files.md:140-170`（P1 模板）
- `agate/tests/unit/check-pruning.bats`（现有测试）
- `agate/tests/unit/check-gate.bats`（现有测试）
- `agate/tests/regression/v060-p8-internal-only.bats`（回归测试）
- `agate/tests/helpers/fixtures.bash`（测试辅助函数）
- `docs/plans/agate-audit-fixes-2026-07-01.md` §C（原始计划）
- `docs/reviews/agate-audit-fixes-plan-review-2026-07-01.md` §C（计划评审）
- `agate/scripts/check-protocol-consistency.py:486-511`（CHECK 9 锚点）

---

## #5 P3 裁剪条件：改文档对齐脚本

### 设计决策

**PASS** — 方向正确。

脚本 check-pruning.sh:70-74 只在 `risk_level=high` 时拦截，medium 放行。测试 P2.5b（check-pruning.bats:96-103）注释明确写"medium 风险 + P3 裁剪是允许的"。脚本行为已被测试固化，是文档措辞滞后。

### 代码片段

**PASS** — 纯文档改动，无代码风险。

state-machine.md:165 改为"high 风险不可裁"正确。WORKFLOW.md 风险矩阵只有"低风险/高风险"两列无 medium 列，不构成"medium 不可裁"的反证。

### 测试计划

**PASS** — 无需新增测试（脚本行为不变，现有 P2.5b 已覆盖 medium 放行）。

### 隐藏依赖

**NOTE** — state-machine.md:165 改动后需跑 consistency check 确认 CHECK 9 锚点不受影响。当前 CHECK 9 P3 锚点关键词是 `risk_level`（L494-496），改动不涉及脚本，锚点不受影响。

---

## #7 检查 7 跳过风险条件加 P6

### 设计决策

**PASS** — 逻辑正确。

文档 state-machine.md:170 写"每条裁剪须含'跳过风险:'评估"，P6 裁剪（no_behavior_change: true）也应写跳过风险。脚本条件漏了 P6。

### 代码片段

**PASS** — 语法正确，逻辑完整。

在 L104 的 `||` 链中追加 `|| ! echo "$PHASES_DECLARED" | grep -qw 'P6'` 正确。`||` 链的语义是"任一阶段被裁剪则进入检查"，加 P6 不改变其他阶段的逻辑。

### 测试计划

**ISSUE（一般）** — 缺少 P6 裁剪 + 有"跳过风险"的 happy path 测试。

测试计划只列了 P2.12（P6 裁剪无"跳过风险" → exit 1），没有 happy path（P6 裁剪 + no_behavior_change: true + 有"跳过风险" → exit 0）。虽然现有 P2.4a 已覆盖 P6 裁剪 + no_behavior_change 的放行场景，但 P2.4a 没有显式验证"跳过风险"条件——它用 `add_pruning_excuse` 自动加了跳过风险行。改后检查 7 条件变了，应有一个显式测试验证"P6 裁剪 + 跳过风险"组合通过。

**建议**：补 P2.12a（P6 裁剪 + no_behavior_change + 跳过风险 → exit 0），或确认 P2.4a 已隐式覆盖并在测试注释中标注。

### 隐藏依赖

**PASS** — 无隐藏依赖。改动仅影响 check-pruning.sh 一行条件。

---

## #8 P8 裁剪加 internal_only_reason 理由字段检查

### 设计决策

**PASS** — 方向正确。

文档 state-machine.md:168 写"需声明 internal_only: true + 理由"，脚本只查 internal_only 不查理由，是遗漏。建立 `internal_only_reason:` 字段名并同步更新文档和模板，解决了计划评审 C.3 指出的"字段名未建立"问题。

### 代码片段

**ISSUE（严重）** — if/elif 结构逻辑反转，会导致 P8 裁剪时跳过检查、P8 未裁剪时误查。

设计文档代码：
```bash
if ! echo "$PHASES_DECLARED" | grep -qw 'P8'; then
    : # P8 未裁剪，跳过
elif ! grep -qE '^internal_only:\s*true' "$P1_FILE" 2>/dev/null; then
    ERRORS="${ERRORS}裁剪 P8 需声明 internal_only: true\n"
elif ! grep -qE '^internal_only_reason:' "$P1_FILE" 2>/dev/null; then
    ERRORS="${ERRORS}裁剪 P8 需 internal_only: true + 理由（internal_only_reason: 字段缺失）\n"
fi
```

逐场景推演：

| 场景 | P8 在 PHASES_DECLARED? | `! grep -qw 'P8'` | 进入分支 | 正确行为 |
|------|----------------------|-------------------|----------|----------|
| P8 被裁剪 | 否 | **true** | `if` 块 → `: # 跳过` → **不检查** | 应检查 internal_only + reason |
| P8 未裁剪 | 是 | **false** | `elif` → 检查 internal_only | 不应检查（P8 未裁剪无需 internal_only） |

**问题根因**：`! echo "$PHASES_DECLARED" | grep -qw 'P8'` 在 P8 被裁剪时为 true（P8 不在声明中），设计文档注释写"P8 未裁剪，跳过"——注释与逻辑矛盾。if/elif 把"P8 被裁剪"这个条件变成了"跳过"分支，后续 elif 在"P8 未裁剪"时才执行——完全反了。

**正确写法**：保持原始嵌套 if 结构，内层改为 if/elif：
```bash
if ! echo "$PHASES_DECLARED" | grep -qw 'P8'; then
    # P8 被裁剪，检查条件
    if ! grep -qE '^internal_only:\s*true' "$P1_FILE" 2>/dev/null; then
        ERRORS="${ERRORS}裁剪 P8 需声明 internal_only: true\n"
    elif ! grep -qE '^internal_only_reason:' "$P1_FILE" 2>/dev/null; then
        ERRORS="${ERRORS}裁剪 P8 需 internal_only: true + 理由（internal_only_reason: 字段缺失）\n"
    fi
fi
```

这与脚本其他检查（检查 2/3/4/5/6）的结构一致：外层 `if ! grep -qw 'Pn'` 判断"阶段被裁剪"，内层检查裁剪条件。

### 测试计划

**ISSUE（一般）** — P2.7a 会变红但未列入测试计划。

设计文档"隐藏依赖"第 2 项正确指出"P2.7a 也会变红"（现有 P2.7a 只加 `internal_only: true` + 跳过风险，改后缺 `internal_only_reason` 会 exit 1），但测试计划只列了 v060-p8-internal-only.bats 的 R4.2/R4.3 修改，没有列 check-pruning.bats P2.7a 的修改。

**必须同步更新 P2.7a**：加 `add_p1_field "$dir" "internal_only_reason" "内部工具"` 使其继续 exit 0。

### 隐藏依赖

**NOTE** — CHECK 9 锚点（check-protocol-consistency.py:508-511）关键词是 `internal_only`，设计文档代码仍含 `internal_only`（elif 条件和错误消息），锚点不受影响。但建议追加 `internal_only_reason` 到锚点关键词列表，防止未来重构误删理由检查。

**PASS** — R4.2 变红已识别并列入修改计划。P2.7a 变红已识别但未列入测试计划（见上）。

---

## #10 P2 候选方案 form check

### 设计决策

**PASS** — 与 nudge 设计一致。

architect.md:24 明确写"多方案是 nudge"，form check 与"跳过风险:"同一设计模式。当前 echo 消息声称检查"权衡 + 选择理由"但实际不查——这才是假锚点。加 grep 检查让消息变诚实。

### 代码片段

**ISSUE（一般）** — 放置位置描述不精确，可能导致变量未定义错误。

设计文档说"放在 CANDIDATE_COUNT >= 2 通过后、exit 2 之前"。但当前代码结构是：

```bash
P2_FILE="$TASK_DIR/P2-design.md"          # L24
if [ -f "$P2_FILE" ]; then                # L25
    CANDIDATE_COUNT=$(grep -cE ... )       # L26
    CANDIDATE_COUNT=$(echo ... | tail -1)  # L27
    if [ "$CANDIDATE_COUNT" -lt 2 ]; then  # L28
        echo "..." >&2                     # L29
        exit 1                             # L30
    fi                                     # L31
fi                                         # L32
echo "GATE P2: ..." >&2                    # L33
exit 2                                     # L34
```

`$CANDIDATE_COUNT` 在 `[ -f "$P2_FILE" ]` 块内定义（L26-27）。如果 P2 文件不存在，`$CANDIDATE_COUNT` 未定义，`set -u`（L11 `set -euo pipefail`）会导致 `if [ "$CANDIDATE_COUNT" -ge 2 ]` 报 unbound variable 错误。

**正确放置**：form check 应在 `[ -f "$P2_FILE" ]` 块内部，紧接 `CANDIDATE_COUNT < 2` 检查之后：

```bash
if [ -f "$P2_FILE" ]; then
    CANDIDATE_COUNT=$(grep -cE ... )
    CANDIDATE_COUNT=$(echo ... | tail -1)
    if [ "$CANDIDATE_COUNT" -lt 2 ]; then
        echo "GATE P2: 需至少 2 个候选方案..." >&2
        exit 1
    fi
    # form check（C#10）—— 在 CANDIDATE_COUNT >= 2 确认后
    if ! grep -qE '权衡|选择理由' "$P2_FILE" 2>/dev/null; then
        echo "GATE P2: P2-design.md 有 ≥2 候选方案但缺'权衡'或'选择理由'描述" >&2
        exit 1
    fi
fi
echo "GATE P2: 需从 P2-design.md gate_commands 动态读取..." >&2
exit 2
```

这样 P2 文件不存在时直接跳到 exit 2（与当前行为一致），P2 文件存在时先查数量再查 form。

### 测试计划

**PASS** — happy path + sad path 都有。

G2.8（无"权衡"→ exit 1）和 G2.9（有"权衡"→ exit 2）覆盖了核心场景。

**NOTE** — 建议补一个边界测试：P2 文件不存在（design_trivial 裁剪场景）→ exit 2。现有 G2.5 已覆盖此场景，但改后应确认 form check 不影响该路径。

### 隐藏依赖

**PASS** — C+D 合并修改 check-gate.sh 的放置顺序已说明（count → status:approved → form check → exit 2）。

---

## 跨项检查

### CHECK 9 锚点影响

| 锚点 | 关键词 | #5 影响 | #7 影响 | #8 影响 | #10 影响 |
|------|--------|---------|---------|---------|----------|
| P2 条件 | design_trivial, follows_existing_pattern, legacy_p2_pruned | 无 | 无 | 无 | 无 |
| P3 条件 | risk_level | 无（只改文档） | 无 | 无 | 无 |
| P6 条件 | no_behavior_change | 无 | 无 | 无 | 无 |
| P7 条件 | SOURCE_FILE_COUNT | 无 | 无 | 无 | 无 |
| P8 条件 | internal_only | 无 | 无 | 代码仍含 internal_only，锚点不受影响 | 无 |

**NOTE** — 建议在 #8 实施时追加 `internal_only_reason` 到 P8 锚点关键词列表（L510），防止理由检查被未来重构误删。非阻断。

### P2.7a 变红

设计文档"隐藏依赖"第 2 项正确识别了 P2.7a 会变红，但**未在测试计划中列出修改方案**。这是遗漏——P2.7a 必须同步加 `internal_only_reason` 字段。

### fixtures.bash 影响

`add_pruning_excuse` 函数（fixtures.bash:153-169）自动追加"跳过风险:"行，不涉及 `internal_only` 或 `internal_only_reason`。#7 和 #8 的改动不需要修改 fixtures.bash。

但 #8 需要一个新的辅助操作：在测试中加 `internal_only_reason` 字段。现有 `add_p1_field` 函数（L171-185）可直接复用（`add_p1_field "$dir" "internal_only_reason" "内部工具"`），无需新增辅助函数。

---

## 汇总

| 项 | #5 | #7 | #8 | #10 |
|----|----|----|----|----|
| 设计决策 | PASS | PASS | PASS | PASS |
| 代码片段 | PASS | PASS | **ISSUE（严重）** | **ISSUE（一般）** |
| 测试计划 | PASS | **ISSUE（一般）** | **ISSUE（一般）** | PASS |
| 隐藏依赖 | NOTE | PASS | **ISSUE（一般）** | PASS |

### 结论：需先修以下项再实施

#### 必须修（会导致功能错误）

| 项 | 问题 | 修复 |
|----|------|------|
| #8 代码 | if/elif 结构逻辑反转：P8 被裁剪时跳过检查，P8 未裁剪时误查 | 改为嵌套 if 结构（外层 `if ! grep P8` 判断裁剪，内层 if/elif 检查 internal_only → reason） |

#### 应该修（测试/覆盖不足）

| 项 | 问题 | 修复 |
|----|------|------|
| #8 测试 | P2.7a 会变红但未列入测试计划 | 在测试计划中加 P2.7a 修改：加 `add_p1_field "$dir" "internal_only_reason" "内部工具"` |
| #7 测试 | 缺 P6 裁剪 + 跳过风险 happy path | 补 P2.12a 或确认 P2.4a 隐式覆盖并标注 |
| #10 代码 | 放置位置描述不精确，CANDIDATE_COUNT 可能在 if 块外未定义 | 明确 form check 放在 `[ -f "$P2_FILE" ]` 块内部，CANDIDATE_COUNT 检查之后 |

#### 建议修（完整性）

| 项 | 问题 | 修复 |
|----|------|------|
| CHECK 9 | P8 锚点缺 `internal_only_reason` 关键词 | 追加到 L510 关键词列表 |
| #10 测试 | P2 文件不存在场景未显式验证 form check 不影响 | 确认 G2.5 仍通过即可 |
