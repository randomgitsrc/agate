# Plan: 标记二值声明 + 行首锚点 + git diff 扫描修复

> 日期：2026-07-22
> 版本影响：minor bump（v0.16.0 → v0.17.0）
> 破坏性变更：PROD_TOUCHED / NEED_CONFIRM 标记格式变更

---

## 问题

gate 脚本用字面量 grep 匹配标记（如 `[PROD_TOUCHED]`、`[NEED_CONFIRM]`），不区分"声明性出现"和"引用性出现"。subagent 在产出文件中写"无 [PROD_TOUCHED]"或"所有 [NEED_CONFIRM] 已解决"时，grep 仍匹配 → gate 误拦。

当前无任何脚本做否定语境排除。

## 方案

### 核心原则

**协议就是协议——gate 拦的不是"否定语境"，拦的是"不合规的写法"。** subagent 写了协议没定义的格式，被拦是正确行为。

### 四层设计

1. **二值声明**（PROD_TOUCHED / NEED_CONFIRM）：协议定义合法格式为正向/负向二选一
2. **不合规格式检测**（PROD_TOUCHED / NEED_CONFIRM）：标记文本出现但不是合法声明格式 → gate 拦截
3. **行首锚点**（SCOPE+ / DESIGN_GAP 等）：所有标记 grep 加 `^\s*-?\s*` 前缀，排除句中引用
4. **git diff 只扫新增行**：pre-commit-gate.sh 的 PROD_TOUCHED 检测只扫 `^+` 行

### 二值标记的三步检测逻辑

对 PROD_TOUCHED 和 NEED_CONFIRM，gate 按以下顺序检测：

```
1. 正向声明存在？（行首 [MARKER]）→ 触发（PROD_TOUCHED→中止 / NEED_CONFIRM→计数>0→exit 1）
2. 不合规格式？（标记文本出现但不是正向/负向声明）→ exit 1 + "不合规格式"消息
3. PROD_TOUCHED：正向负向都没有 → 静默通过（安全网，缺失≠风险）
   NEED_CONFIRM：正向负向都没有 → WARNING（语义缺失，subagent 可能忘了做确认判断）
```

**不合规格式检测**：先用无锚点 grep 检查标记文本是否出现，若出现但不在行首声明位置 → 不合规。

---

## 第一部分：二值声明（PROD_TOUCHED / NEED_CONFIRM）

### 1.1 PROD_TOUCHED

**当前格式**：
```
[PROD_TOUCHED] 接触了生产环境：{描述}
```

**新格式（二选一）**：
```
[PROD_TOUCHED] 接触了生产环境：{描述}    ← 触发了
[PROD_NOT_TOUCHED]                        ← 未触发
```

**脚本改动**（pre-commit-gate.sh:107，三步检测）：

```bash
# 当前：
git diff --cached -- "$TASK_REL" | grep -q '\[PROD_TOUCHED\]'

# 改为（三步）：
DIFF_ADDED=$(git diff --cached -- "$TASK_REL" | grep '^+[^+]' | sed 's/^+//' || true)

# 步骤 1：正向声明（行首）→ 中止
if echo "$DIFF_ADDED" | grep -qE '^\s*-?\s*\[PROD_TOUCHED\]'; then
    echo "GATE: [PROD_TOUCHED] 检测到生产环境接触，commit 中止" >&2
    exit 1
fi

# 步骤 2：不合规格式（标记文本出现但非行首声明）→ 中止
if echo "$DIFF_ADDED" | grep -q '\[PROD_TOUCHED\]'; then
    echo "GATE: 不合规的 PROD_TOUCHED 标记格式（须用行首 [PROD_TOUCHED] 或 [PROD_NOT_TOUCHED] 声明）" >&2
    exit 1
fi

# 步骤 3：正向负向都没有 → 静默通过（不阻断，不 WARNING）
# 理由：PROD_TOUCHED 是安全网，缺失声明 ≠ 有风险。真正有风险的是步骤 1（触发）和步骤 2（不合规）。
# 每次暂存任务文件都 WARNING 会造成 WARNING 疲劳，降低 WARNING 的信号价值。
# : <<'SKIP_STEP3'
# if ! echo "$DIFF_ADDED" | grep -qE '^\s*-?\s*\[PROD_NOT_TOUCHED\]'; then
#     echo "GATE WARNING: 未检测到 PROD_TOUCHED 声明（[PROD_TOUCHED] 或 [PROD_NOT_TOUCHED]）" >&2
# fi
# SKIP_STEP3
```

**子串安全性**：`[PROD_NOT_TOUCHED]` 不含子串 `[PROD_TOUCHED]`（`PROD_NOT_TOUCHED` ≠ `PROD_TOUCHED`），步骤 2 的无锚点 grep 不会匹配负向声明。

### 1.2 NEED_CONFIRM

**当前格式**：
```
[NEED_CONFIRM] 不可逆操作待确认
操作类型：{...}
```

**新格式（二选一）**：
```
[NEED_CONFIRM] 不可逆操作待确认              ← 有待确认项（可多条）
操作类型：{...}

[NO_NEED_CONFIRM]                             ← 无待确认项
```

**脚本改动**（check-gate.sh P1 分支:47 和 P6 分支:135，三步检测）：

**P1 分支**（:45-52）：NC 检查独立于其他条件，三步模板可直接替换。

**P6 分支**（:129-148）：NC 检查与 FAIL/TOTAL 耦合在联合条件 `if [ "$FAIL" -ne 0 ] || [ "$NC" -ne 0 ] || [ "$TOTAL" -eq 0 ]` 中。拆解方案：

```bash
# P6 分支改动（替换 :135-140）：

# 步骤 1：正向声明计数（行首）→ 独立检查
NC=$(grep -cE '^\s*-?\s*\[NEED_CONFIRM\]' "$TASK_DIR/P6-acceptance.md" 2>/dev/null || echo 0)
NC=$(echo "$NC" | tail -1)
if [ "$NC" -gt 0 ]; then
    echo "GATE P6: FAIL=$FAIL, NEED_CONFIRM=$NC, TOTAL=$TOTAL" >&2
    exit 1
fi

# 步骤 2：不合规格式（标记文本出现但非行首正向声明）
if grep -q '\[NEED_CONFIRM\]' "$TASK_DIR/P6-acceptance.md" 2>/dev/null; then
    echo "GATE: 不合规的 NEED_CONFIRM 标记格式（须用行首 [NEED_CONFIRM] 或 [NO_NEED_CONFIRM] 声明）" >&2
    exit 1
fi

# 步骤 3：正向负向都没有 → WARNING（不阻断）
if ! grep -qE '^\s*-?\s*\[NO_NEED_CONFIRM\]' "$TASK_DIR/P6-acceptance.md" 2>/dev/null; then
    echo "GATE WARNING: 未检测到 NEED_CONFIRM 声明（[NEED_CONFIRM] 或 [NO_NEED_CONFIRM]）" >&2
fi

# FAIL/TOTAL 检查保持不变（步骤 1 exit 1 后不执行，步骤 2/3 后继续）
if [ "$FAIL" -ne 0 ] || [ "$TOTAL" -eq 0 ]; then
    echo "GATE P6: FAIL=$FAIL, TOTAL=$TOTAL" >&2
    exit 1
fi
```

**P1 分支**（替换 :47-52）：

```bash
# 步骤 1：正向声明计数（行首）
NC=$(grep -cE '^\s*-?\s*\[NEED_CONFIRM\]' "$FILE" 2>/dev/null || echo 0)
NC=$(echo "$NC" | tail -1)
if [ "$NC" -gt 0 ]; then
    # 有待确认项 → gate 失败
    ...
fi

# 步骤 2：不合规格式（标记文本出现但非行首正向声明）
if grep -q '\[NEED_CONFIRM\]' "$FILE" 2>/dev/null; then
    echo "GATE: 不合规的 NEED_CONFIRM 标记格式（须用行首 [NEED_CONFIRM] 或 [NO_NEED_CONFIRM] 声明）" >&2
    exit 1
fi

# 步骤 3：正向负向都没有 → WARNING（不阻断）
if ! grep -qE '^\s*-?\s*\[NO_NEED_CONFIRM\]' "$FILE" 2>/dev/null; then
    echo "GATE WARNING: 未检测到 NEED_CONFIRM 声明（[NEED_CONFIRM] 或 [NO_NEED_CONFIRM]）" >&2
fi
```

**子串安全性**：`[NO_NEED_CONFIRM]` 不含子串 `[NEED_CONFIRM]`（`NO_NEED_CONFIRM` ≠ `NEED_CONFIRM`），步骤 2 的无锚点 grep 不会匹配负向声明。

**注意**：步骤 2 只在步骤 1 的 NC=0 时执行（NC>0 已在步骤 1 exit 1）。

### 1.3 协议文档更新

**dispatch-protocol.md**：
- 行 579-585：`[PROD_TOUCHED]` 标记说明 → 改为二值格式定义
- 行 783：P1→P2 门槛表 `grep -cE '\[NEED_CONFIRM\]'` → 更新为行首锚点格式 `grep -cE '^\s*-?\s*\[NEED_CONFIRM\]'`
- 行 787：P5→P6 门槛表 `grep -rl '\[PROD_TOUCHED\]' {task}/ → 无命中` → 更新为"行首锚点扫描（主 Agent 参照 pre-commit 三步逻辑手动判断：正向→PAUSED / 不合规→修正 / 缺失→静默通过）"
- 行 808：pre-commit 全景表 PROD_TOUCHED 检测描述 → 更新为三步检测（正向→中止 / 不合规→中止 / 缺失→静默通过）
- 行 888：P5 验证方式表 `PROD_TOUCHED | gate 脚本扫描暂存 diff | 客观检查` → 更新为"行首锚点 + 二值声明检测"
- 行 990-1009：`[NEED_CONFIRM]` 输出格式 → 改为二值格式定义
- 新增「标记声明规范」节（放在「不可逆操作保护协议」之后）：
  ```
  ## 标记声明规范

  状态标记采用二值声明——必须写正向或负向之一，不允许第三种写法：

  | 标记 | 正向（触发了）| 负向（未触发）|
  |------|-------------|-------------|
  | PROD_TOUCHED | `[PROD_TOUCHED] {描述}` | `[PROD_NOT_TOUCHED]` |
  | NEED_CONFIRM | `[NEED_CONFIRM] {描述}`（可多条）| `[NO_NEED_CONFIRM]` |

  **禁止**：在产出文件中引用标记文本做否定描述（如"无 [PROD_TOUCHED]"、"所有 [NEED_CONFIRM] 已解决"）。
  要表达"未触发"，写负向格式（`[PROD_NOT_TOUCHED]` / `[NO_NEED_CONFIRM]`）。
  写了协议未定义的格式 → gate 拦截 → 重派修正。
  ```

**dispatch-prompt.md**（派发模板）：
- 在「环境隔离」节追加一行：
  ```
  - 状态标记用二值格式：触发写 `[PROD_TOUCHED] {描述}`，未触发写 `[PROD_NOT_TOUCHED]`。不要写"无 [PROD_TOUCHED]"
  ```

**task-files.md**：
- 行 99：PROD_TOUCHED 说明 → 改为二值格式

**state-machine.md**：
- 行 82：`任意阶段 --[出现 PROD_TOUCHED]--> PAUSED` → 补充"（`[PROD_TOUCHED]` 正向声明触发，`[PROD_NOT_TOUCHED]` 不触发）"
- 行 391：gate 命令 `grep -cE '\[NEED_CONFIRM\]'` → 更新为行首锚点格式 `grep -cE '^\s*-?\s*\[NEED_CONFIRM\]'`
- 行 400：gate 命令 `grep -rl '\[PROD_TOUCHED\]'` → 更新为行首锚点格式

**WORKFLOW.md**：
- 行 217：P1 gate 描述中 `grep -cE '\[NEED_CONFIRM\]'` → 更新为行首锚点格式
- 行 221：P5 gate 门槛列 `grep -rl '\[PROD_TOUCHED\]' → 无命中` → 更新为"行首锚点扫描（主 Agent 参照 pre-commit 三步逻辑手动判断：正向→PAUSED / 不合规→修正 / 缺失→静默通过）"

**注意**：check-gate.sh P5 分支（:116-128）无 PROD_TOUCHED 检测，直接 exit 2。PROD_TOUCHED 检测只在 pre-commit-gate.sh（commit 时扫暂存 diff）。P5 gate 文档描述的 grep 命令是主 Agent 手动执行的，不是脚本命令。plan 不在 check-gate.sh P5 分支新增 PROD_TOUCHED 检测——保持当前架构（pre-commit 检测 + 主 Agent 手动判断）。

**phase-cards/P5-verification.md**：
- 行 46：PROD_TOUCHED 规则 → 补充二值格式说明

**phase-cards/P7-consistency.md**：
- 行 31：未决项清零 → 补充"检查 `[NO_NEED_CONFIRM]` 存在性"

**角色文件**：
- `assets/execution-roles/verifier.md` 行 154：NEED_CONFIRM 指令 → 改为二值格式
- `assets/execution-roles/consistency-reviewer.md` 行 50：未决项清零 → 补充二值格式检查
- `assets/templates/custom-role.md` 行 40：环境隔离指令 → 补充二值格式

**loop-orchestration.md**：
- 行 53, 106：硬中断信号列表 → 补充"仅正向声明触发"

**CONTEXT.md**：
- 行 25：PROD_TOUCHED 术语定义 → 补充二值格式
- 行 16：NEED_CONFIRM 术语定义 → 补充二值格式

**LIMITATIONS.md**：
- 行 25, 33：PROD_TOUCHED 讨论 → 补充二值格式缓解说明

### 1.4 测试

**新增测试**（`agate/tests/unit/check-gate.bats`）：

| 用例 | 描述 | 期望 |
|------|------|------|
| G_NC_BINARY.1 | P1 含 `[NO_NEED_CONFIRM]` | exit 2（NC=0，通过）|
| G_NC_BINARY.2 | P1 含行首 `[NEED_CONFIRM] 描述` | exit 1（NC>0）|
| G_NC_BINARY.3 | P1 含 `无 [NEED_CONFIRM]`（不合规格式）| exit 1（步骤 2 拦截）|
| G_NC_BINARY.4 | P6 含 `[NO_NEED_CONFIRM]` + 最小有效 fixture（≥1 PASS 行 + P6-evidence/ 非空）| exit 2（NC=0，通过）|
| G_NC_BINARY.5 | P1 既无正向也无负向声明 | exit 2 + WARNING（步骤 3，NEED_CONFIRM 语义缺失）|
| G_NC_BINARY.6 | P1 含 `[NO_NEED_CONFIRM] 确认无不可逆操作`（负向+描述）| exit 2（负向声明允许追加描述）|

**新增测试**（`agate/tests/integration/pre-commit-hook.bats`）：

| 用例 | 描述 | 期望 |
|------|------|------|
| IT_PT_BINARY.1 | 暂存 diff 含 `+ [PROD_TOUCHED] 描述` | 中止 commit（步骤 1）|
| IT_PT_BINARY.2 | 暂存 diff 含 `+ [PROD_NOT_TOUCHED]` | 不中止 |
| IT_PT_BINARY.3 | 暂存 diff 含 `- [PROD_TOUCHED] 旧内容`（删除行）| 不中止（只扫 ^+ 行）|
| IT_PT_BINARY.4 | 暂存 diff 含 `+ 无 [PROD_TOUCHED]`（不合规格式）| 中止（步骤 2）|
| IT_PT_BINARY.5 | 暂存 diff 含 `+ 检查了 [PROD_TOUCHED] 标记`（句中引用）| 中止（步骤 2）|
| IT_PT_BINARY.6 | 暂存 diff 既无正向也无负向 | 不中止 + 无 WARNING（步骤 3 静默通过）|
| IT_PT_BINARY.7 | 暂存 diff 含 `+ [PROD_NOT_TOUCHED] 确认未接触`（负向+描述）| 不中止 |

**修改测试**：
- IT.3（pre-commit-hook.bats:102-119）：更新为二值格式

---

## 第二部分：行首锚点（SCOPE+ / DESIGN_GAP / SCOPE_RESOLVED）

### 2.1 脚本改动

| 文件 | 行号 | 当前 | 改为 |
|------|------|------|------|
| check-retrospective.sh | 37 | `grep -q '\[SCOPE+\]' "$f"` | `grep -qE '^\s*-?\s*\[SCOPE+\]' "$f"` |
| check-scope-resolved.sh | 20 | `sed ... \| grep -q '\[SCOPE+\]'` | `sed ... \| grep -qE '^\s*-?\s*\[SCOPE+\]'` |
| check-gate.sh | 162 | `grep -cE '\[DESIGN_GAP:' "$P7_FILE"` | `grep -cE '^\s*-?\s*\[DESIGN_GAP:' "$P7_FILE"` |
| check-gate.sh | 163 | `grep -cE '\[DESIGN_GAP_REVIEWED' "$P7_FILE"` | `grep -cE '^\s*-?\s*\[DESIGN_GAP_REVIEWED' "$P7_FILE"` |
| check-gate.sh | 173 | `grep -rh '\[DESIGN_GAP:' ... \| grep -cE '\[DESIGN_GAP:'` | 管道第二级改为 `grep -cE '^\s*-?\s*\[DESIGN_GAP:'` |
| check-scope-resolved.sh | 37 | `grep -cE '\[SCOPE_RESOLVED($\|[^a-z])' "$P1_FILE"` | `grep -cE '^\s*-?\s*\[SCOPE_RESOLVED($\|[^a-z])' "$P1_FILE"` |

### 2.2 不改的（已有行首锚点）

| 标记 | 脚本 | 当前正则 | 状态 |
|------|------|---------|------|
| `[BLOCKER]` | check-gate.sh:153 | `^\s*-?\s*\[BLOCKER\]` | ✅ 已有 |
| `[DEVIATION-CRITICAL]` | check-gate.sh:154 | `^\s*-?\s*\[DEVIATION-CRITICAL\]` | ✅ 已有 |
| `PASS`/`FAIL` | 多个脚本 | `^\s*- (PASS\|FAIL)\b` | ✅ 已有 |

### 2.3 协议文档更新

**dispatch-protocol.md**：
- 行 867-869：SCOPE+ 扫描规则 → 补充"行首声明格式"
- 行 874-878：DESIGN_GAP 格式 → 补充"行首声明格式"

**state-machine.md**：
- 行 201-212：SCOPE+ 特殊转移 → 补充行首格式说明

**WORKFLOW.md**：
- 行 329-359：SCOPE+ 专节 → 补充行首格式

**角色文件**：
- `assets/execution-roles/implementer.md` 行 93-95：SCOPE+ 格式 → 补充行首要求
- `assets/execution-roles/architect.md` 行 129-132：SCOPE+ 格式示例 → 补充行首要求

### 2.4 测试

**新增测试**（`agate/tests/unit/check-scope-resolved.bats`）：

| 用例 | 描述 | 期望 |
|------|------|------|
| SC.7 | 句中 `[SCOPE+]`（非行首）| exit 0（不触发）|
| SC.8 | 行首 `- [SCOPE+]` | exit 1（触发，无 RESOLVED）|

**新增测试**（`agate/tests/unit/check-retrospective.bats`）：

| 用例 | 描述 | 期望 |
|------|------|------|
| RT.7 | 句中 `[SCOPE+]`（非行首）| exit 0（不触发复盘提醒）|

**新增测试**（`agate/tests/unit/check-gate.bats`）：

| 用例 | 描述 | 期望 |
|------|------|------|
| G_DG_ANCHOR.1 | P7 句中 `[DESIGN_GAP: xxx]`（非行首）| 不计入 GAP 计数 |
| G_DG_ANCHOR.2 | P7 行首 `[DESIGN_GAP: xxx]` | 计入 GAP 计数 |

---

## 第三部分：git diff 扫描修复

### 3.1 问题

`pre-commit-gate.sh:107` 扫 `git diff --cached` 全量输出（含删除行 `-`、上下文行 ` `），导致：
- 删除 `[PROD_TOUCHED]` 行 → 误匹配
- 上下文含 `[PROD_TOUCHED]` → 误匹配

### 3.2 修复

已合并到 1.1 节的三步检测逻辑中（`grep '^+' | sed 's/^+//'` 先过滤新增行再检测）。

核心变化：`git diff --cached` 全量输出 → 只取 `^+` 新增行，排除删除行和上下文行。

### 3.3 测试

已在 1.4 节的 IT_PT_BINARY.3 覆盖（删除行不中止）。

---

## 第四部分：一致性检查锚点

### 4.1 check-protocol-consistency.py 更新

**修改锚点**：

| 锚点 | 当前 keywords | 改为 |
|------|-------------|------|
| PROD_TOUCHED 检测 (行 486-488) | `["PROD_TOUCHED"]` | `["PROD_TOUCHED", "PROD_NOT_TOUCHED"]` |

**新增锚点**：

| 锚点 | script | keywords |
|------|--------|----------|
| NEED_CONFIRM 二值声明 | check-gate.sh | `["NEED_CONFIRM", "NO_NEED_CONFIRM"]` |
| 标记声明规范 | dispatch-protocol.md | `["标记声明规范", "PROD_NOT_TOUCHED", "NO_NEED_CONFIRM"]` |

### 4.2 测试

**新增测试**（`agate/tests/integration/consistency.bats`）：

| 用例 | 描述 | 期望 |
|------|------|------|
| CON.11 | CHECK 9: PROD_TOUCHED 锚点含 PROD_NOT_TOUCHED | 通过 |
| CON.12 | CHECK 9: NEED_CONFIRM 二值锚点存在 | 通过 |

---

## 第五部分：版本与 CHANGELOG

### 5.1 版本 bump

v0.16.0 → v0.17.0（minor bump）

理由：PROD_TOUCHED / NEED_CONFIRM 标记格式变更是破坏性变更（旧格式 `无 [PROD_TOUCHED]` 会被 gate 拦截），按 semver 惯例走 minor。

### 5.2 CHANGELOG

```markdown
## [0.17.0]

### 新增
- 标记二值声明：PROD_TOUCHED / NEED_CONFIRM 采用正向/负向二选一格式
- `[PROD_NOT_TOUCHED]` / `[NO_NEED_CONFIRM]` 负向声明格式
- 缺失声明 WARNING（NEED_CONFIRM 两个都没写时提醒；PROD_TOUCHED 缺失静默通过）
- 标记声明规范节（dispatch-protocol.md）

### 变更
- **BREAKING**：`[PROD_TOUCHED]` / `[NEED_CONFIRM]` 标记必须行首声明，句中引用会被 gate 拦截
- **BREAKING**：`无 [PROD_TOUCHED]` 等否定语境写法不再被接受，须用 `[PROD_NOT_TOUCHED]`
- pre-commit-gate.sh PROD_TOUCHED 检测只扫 git diff 新增行（`^+`），不再匹配删除行/上下文行
- SCOPE+ / DESIGN_GAP / SCOPE_RESOLVED grep 加行首锚点
- NEED_CONFIRM grep 加行首锚点

### 修复
- pre-commit-gate.sh 扫描 git diff 删除行/上下文行导致 PROD_TOUCHED 误判
```

---

## 第六部分：文档传播清单

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| dispatch-protocol.md | 格式定义 + 新增节 | 二值格式 + 标记声明规范 + 行 783/787/888 更新 |
| dispatch-prompt.md | 追加指令 | 环境隔离节追加二值格式 + SCOPE+ 行首 |
| state-machine.md | 格式更新 | PROD_TOUCHED 转移条件 + gate 命令 + 行 391 NEED_CONFIRM |
| WORKFLOW.md | 格式更新 | P1 gate 描述 |
| task-files.md | 格式更新 | PROD_TOUCHED 说明 |
| rules/state-transitions.md | 格式更新 | NEED_CONFIRM(:18) + PROD_TOUCHED(:31,:86-88) + SCOPE+(:72) 行首/二值格式 |
| git-integration.md | 格式更新 | SCOPE+(:167-168) 行首锚点格式 |
| phase-cards/P1-requirements.md | 补充 | NEED_CONFIRM 二值格式 + 推进条件 |
| phase-cards/P4-implementation.md | 补充 | SCOPE+(:88,:94) 行首格式 |
| phase-cards/P5-verification.md | 补充 | 二值格式说明 |
| phase-cards/P6-acceptance.md | 补充 | NEED_CONFIRM(:77,:83,:90) 二值格式 + SCOPE+(:28) 行首 |
| phase-cards/P7-consistency.md | 补充 | NO_NEED_CONFIRM 检查 |
| phase-cards/P8-release.md | 补充 | PROD_TOUCHED 二值格式 |
| loop-orchestration.md | 补充 | 硬中断信号"仅正向声明触发" |
| CONTEXT.md | 术语更新 | PROD_TOUCHED / NEED_CONFIRM 定义 |
| LIMITATIONS.md | 补充 | 二值格式缓解说明 |
| role-system.md | 补充 | 标记声明规范引用 |
| assets/execution-roles/analyst.md | 格式更新 | NEED_CONFIRM 二值（analyst 是主要使用者）|
| assets/execution-roles/verifier.md | 格式更新 | NEED_CONFIRM 二值 |
| assets/execution-roles/consistency-reviewer.md | 格式更新 | 未决项清零 + 二值 |
| assets/execution-roles/implementer.md | 格式更新 | SCOPE+ 行首 |
| assets/execution-roles/architect.md | 格式更新 | SCOPE+ 行首 |
| assets/templates/custom-role.md | 格式更新 | 环境隔离 + 二值 |
| assets/templates/dispatch-prompt.md | 格式更新 | PROD_TOUCHED(:24) 二值 + SCOPE+(:113) 行首 |
| assets/templates/active-tasks-template.md | 格式更新 | P1 gate 摘要 |
| scripts/README.md | 更新 | 脚本行为变更说明 |
| SELF-GATE.md | 无改动 | 触发条件不变 |
| AGENTS.md | 无改动 | 依赖不变 |

### 6.2 已知局限

**check-retrospective.sh 不剥离 AGATE_CARD 块**：check-scope-resolved.sh 用 sed 剥离卡片嵌入块后再 grep `[SCOPE+]`，但 check-retrospective.sh 直接 grep。加行首锚点后风险降低（卡片模板中的 `[SCOPE+]` 通常不在行首），但仍可能误触发复盘提醒。由于 check-retrospective.sh 始终 exit 0（WARNING-only），可接受。**实施者注意**：check-retrospective.sh:37 的行首锚点改动与 check-scope-resolved.sh:20 不同——后者先 sed 剥离 AGATE_CARD 再 grep，前者不剥离。

---

## 第七部分：不改的

| 标记 | 理由 |
|------|------|
| `[UPGRADE]` | 纯协议层，无脚本检测，无 grep 误判风险 |
| `[CAPABILITY_GAP]` | 纯协议层，无脚本检测，无 grep 误判风险 |
| `[BLOCKER]` / `[DEVIATION-CRITICAL]` | 已有行首锚点 + 汇总行排除，够用 |
| `PASS` / `FAIL` | 已有 `^\s*- PASS\b` 行首+词边界，够用 |
| `[SCOPE_GAP]` | 无脚本检测（主 Agent 语义判断），无 grep 误判风险 |

---

## 第八部分：实施顺序

1. 先写失败测试（确认红）
2. 脚本改动（确认绿）
3. 跑全量测试确认无回归
4. 协议文档更新（dispatch-protocol.md 标记声明规范节 → 其他文档）
5. 一致性检查锚点更新
6. CHANGELOG + README badge
7. `python3 agate/scripts/check-protocol-consistency.py` 确认 0 ERROR
8. `bash agate/tests/scripts/count-tests.sh` 确认用例数
9. `shellcheck -S warning agate/scripts/*.sh`
10. self-gate：派发 protocol-alignment-review
