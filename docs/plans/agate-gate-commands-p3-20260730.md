# gate_commands.P3 — check-tdd-red.sh 自动读取测试运行器 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** check-tdd-red.sh 在无 `TEST_RUNNER` 环境变量时，自动从 P2-design.md 的 `gate_commands.P3` 字段读取测试运行器命令，消除测试运行器命令（TEST_RUNNER）的重复声明。

**Architecture:** 在 gate_commands 中新增 `P3` 键（可选），architect 在 P2 声明测试运行命令。check-tdd-red.sh 回退链从 `$TEST_RUNNER → which pytest → exit 3` 扩展为 `$TEST_RUNNER → gate_commands.P3 → which pytest → exit 3`。P3 键声明的是"测试运行器 + 参数"（如 `npx vitest run`），与 P5 的紧凑输出命令（如 `npx vitest run --reporter=dot`）分离——P3 红灯检查需要 verbose 输出来区分 A/B 类错误。

**Tech Stack:** Bash, Python3 (内联于 bash 脚本), Bats (测试框架)

---

## 背景

### 问题

T076 复盘发现：非 pytest 项目（如 vitest）在 P3 跑 check-tdd-red.sh 时，需要主 Agent 手动设置 `TEST_RUNNER` 等环境变量。但 P2-design.md 的 `gate_commands.P5` 已经声明了同一项目的测试命令——同一个项目的测试命令声明了两次。

### 方案选择

**方案 A（已否决）**：check-tdd-red.sh 从 `gate_commands.P5` 提取 runner。
- 问题：P5 命令带紧凑输出 flags（`--tb=no`、`--reporter=dot`），P3 红灯检查需要 verbose 输出区分 A/B 类错误，两者输出模式冲突
- 提取 runner 需要去掉 P5 的 flags 再拼 P3 的 flags，解析逻辑复杂且脆弱

**方案 B（本计划）**：gate_commands 新增 `P3` 键。
- architect 在 P2 声明 `gate_commands.P3: "npx vitest run"`（不带紧凑输出 flags）
- check-tdd-red.sh 自动读取，与环境变量 `TEST_RUNNER` 功能一致
- P3 和 P5 的命令分离（P3 要 verbose，P5 要紧凑），各取所需

### 设计原则

- **P3 键是可选的**：不声明时行为与现有完全一致（`$TEST_RUNNER → which pytest → exit 3`），向后兼容
- **环境变量优先级最高**：`TEST_RUNNER` 环境变量始终优先于 `gate_commands.P3`，手动覆盖始终可用
- **不增加必填字段**：gate_commands 的必填键仍为 P5/P5_e2e/P6，P3 是可选增强
- **技术栈无关**：P3 键的值由 architect 根据项目技术栈声明，agate 不硬编码任何技术栈

---

## 文件结构

| 文件 | 操作 | 职责 |
|------|------|------|
| `agate/scripts/check-tdd-red.sh` | 修改 | 新增 gate_commands.P3 回退源 |
| `agate/scripts/check-gate.sh` | 修改 | P3 分支传递 TASK_DIR 给 check-tdd-red.sh |
| `agate/assets/execution-roles/architect.md` | 修改 | gate_commands 示例增加 P3 键 |
| `agate/assets/templates/task-files.md` | 修改 | gate_commands 模板增加 P3 键 |
| `agate/phase-cards/P3-tdd.md` | 修改 | 说明 check-tdd-red.sh 自动读取 gate_commands.P3 |
| `agate/phase-cards/P2-design.md` | 修改 | gate_commands 示例增加 P3 键 |
| `agate/assets/execution-roles/verifier.md` | 修改 | 更新非 pytest 技术栈说明 |
| `agate/phase-cards/P5-verification.md` | 修改 | 更新非 pytest 技术栈说明（与 verifier.md 同一段落） |
| `agate/state-machine.md` | 修改 | TDD 红灯检查设计说明代码块更新回退链 |
| `agate/scripts/check-protocol-consistency.py` | 修改 | CHECK 4 不对 P3 键报缺失（P3 是可选键） |
| `agate/tests/unit/check-tdd-red.bats` | 修改 | 新增 gate_commands.P3 读取测试 |

---

## Task 1: check-tdd-red.sh 新增 gate_commands.P3 回退源

**Files:**
- Modify: `agate/scripts/check-tdd-red.sh:49-57`（runner 探测逻辑）
- Modify: `agate/scripts/check-tdd-red.sh:25-27`（注释更新回退链）
- Modify: `agate/scripts/check-tdd-red.sh:32-38`（注释更新 vitest 示例）
- Test: `agate/tests/unit/check-tdd-red.bats`

### 步骤

- [ ] **Step 1: 写失败测试 — gate_commands.P3 存在时自动读取**

在 `agate/tests/unit/check-tdd-red.bats` 末尾新增测试：

```bash
@test "TDD.G1: gate_commands.P3 in P2-design.md → auto-read as TEST_RUNNER" {
    local fake
    fake=$(make_fake_pytest "2 failed, 5 passed" 1)
    # 创建一个带 gate_commands.P3 的 P2-design.md
    local task_dir="$BATS_TEST_TMPDIR/task-g1"
    mkdir -p "$task_dir"
    cat > "$task_dir/P2-design.md" <<EOF
## gate_commands
gate_commands:
  P3: "$fake"
  P5: "pytest -q --tb=no"
EOF
    # 不设 TEST_RUNNER，不装 pytest → 应该从 gate_commands.P3 读取
    run env -u TEST_RUNNER PATH="/usr/bin:/bin" TASK_DIR="$task_dir" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 0 ]
    [[ "$output" == *"classic red-light"* ]]
}
```

- [ ] **Step 2: 跑测试确认失败**

Run: `bats agate/tests/unit/check-tdd-red.bats --filter "TDD.G1"`
Expected: FAIL（当前 check-tdd-red.sh 不读 gate_commands.P3，无 TEST_RUNNER 时回退到 `which pytest`，PATH 中无 pytest 则 exit 3）

- [ ] **Step 3: 实现 — check-tdd-red.sh 新增 gate_commands.P3 读取**

在 `agate/scripts/check-tdd-red.sh` 中，修改 runner 探测逻辑（L49-57）。

旧代码：
```bash
if [ -n "${TEST_RUNNER:-}" ]; then
    RUNNER="$TEST_RUNNER"
elif command -v pytest &>/dev/null; then
    RUNNER="pytest"
else
    echo "TDD_CHECK: no test runner found. Set TEST_RUNNER env var or install pytest." >&2
    echo "  (本脚本是 pytest 参考实现，非 Python 项目请提供适配脚本)" >&2
    exit 3
fi
```

新代码：
```bash
if [ -n "${TEST_RUNNER:-}" ]; then
    RUNNER="$TEST_RUNNER"
elif [ -n "${TASK_DIR:-}" ] && [ -f "$TASK_DIR/P2-design.md" ]; then
    # 从 P2-design.md 的 gate_commands.P3 读取测试运行器（可选键，architect 在 P2 声明）
    P3_CMD=$(GATE_FILE="$TASK_DIR/P2-design.md" python3 -c '
import re, os, sys
content = open(os.environ["GATE_FILE"]).read()
if not content.endswith(chr(10)):
    content += chr(10)
m = re.search(r"^gate_commands:[ \t]*\n((?:  .*\n|\s*\n)*)", content, re.MULTILINE)
if not m:
    sys.exit(0)
for line in re.findall(r"^  (P3):\s*(.+)$", m.group(1), re.MULTILINE):
    print(line[1].strip().strip("\"").strip(chr(39)))
' 2>/dev/null || true)
    if [ -n "$P3_CMD" ]; then
        RUNNER="$P3_CMD"
    elif command -v pytest &>/dev/null; then
        RUNNER="pytest"
    else
        echo "TDD_CHECK: no test runner found. Set TEST_RUNNER env var, declare gate_commands.P3, or install pytest." >&2
        echo "  (本脚本是 pytest 参考实现，非 Python 项目请在 P2 gate_commands.P3 声明测试命令)" >&2
        exit 3
    fi
elif command -v pytest &>/dev/null; then
    RUNNER="pytest"
else
    echo "TDD_CHECK: no test runner found. Set TEST_RUNNER env var, declare gate_commands.P3, or install pytest." >&2
    echo "  (本脚本是 pytest 参考实现，非 Python 项目请在 P2 gate_commands.P3 声明测试命令)" >&2
    exit 3
fi
```

> **注意**：Python `re.findall` 匹配 `P3:` 键最多一次（gate_commands 块中 P3 只出现一次），无需 `tail -1` 过滤多行输出。

- [ ] **Step 4: 跑测试确认通过**

Run: `bats agate/tests/unit/check-tdd-red.bats --filter "TDD.G1"`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add agate/scripts/check-tdd-red.sh agate/tests/unit/check-tdd-red.bats
git commit -m "feat(check-tdd-red): auto-read gate_commands.P3 as test runner fallback"
```

---

## Task 2: 更多 gate_commands.P3 边界测试

**Files:**
- Test: `agate/tests/unit/check-tdd-red.bats`

### 步骤

- [ ] **Step 1: 写失败测试 — gate_commands.P3 不存在时回退到 TEST_RUNNER（验证 P3 缺失不影响现有行为）**

```bash
@test "TDD.G2: no gate_commands.P3 → TEST_RUNNER still works (backward compat)" {
    local task_dir="$BATS_TEST_TMPDIR/task-g2"
    mkdir -p "$task_dir"
    cat > "$task_dir/P2-design.md" <<EOF
## gate_commands
gate_commands:
  P5: "pytest -q --tb=no"
EOF
    # 有 P2-design.md 但无 P3 键 + 设了 TEST_RUNNER → 用 TEST_RUNNER
    local fake
    fake=$(make_fake_pytest "2 failed, 5 passed" 1)
    run env TEST_RUNNER="$fake" TASK_DIR="$task_dir" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 0 ]
    [[ "$output" == *"classic red-light"* ]]
}
```

- [ ] **Step 2: 写失败测试 — TEST_RUNNER 优先于 gate_commands.P3**

```bash
@test "TDD.G3: TEST_RUNNER env var takes priority over gate_commands.P3" {
    local fake_env
    fake_env=$(make_fake_pytest "2 failed, 5 passed" 1)
    local fake_p3
    fake_p3=$(make_fake_pytest "all passed" 0)
    local task_dir="$BATS_TEST_TMPDIR/task-g3"
    mkdir -p "$task_dir"
    cat > "$task_dir/P2-design.md" <<EOF
gate_commands:
  P3: "$fake_p3"
  P5: "pytest -q --tb=no"
EOF
    # TEST_RUNNER 指向 assertion failure runner，gate_commands.P3 指向 all-pass runner
    # 应该用 TEST_RUNNER（exit 0 classic red-light），不是 gate_commands.P3（exit 2 green）
    run env TEST_RUNNER="$fake_env" TASK_DIR="$task_dir" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 0 ]
    [[ "$output" == *"classic red-light"* ]]
}
```

- [ ] **Step 3: 写失败测试 — 无 TASK_DIR 时跳过 gate_commands 读取**

```bash
@test "TDD.G4: no TASK_DIR → skip gate_commands read, fall back to pytest" {
    local fake
    fake=$(make_fake_pytest "2 failed, 5 passed" 1)
    # 不设 TASK_DIR，只设 TEST_RUNNER → 应正常工作（向后兼容）
    run env TEST_RUNNER="$fake" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 0 ]
    [[ "$output" == *"classic red-light"* ]]
}
```

- [ ] **Step 4: 写失败测试 — gate_commands.P3 带引号的值正确解析**

```bash
@test "TDD.G5: gate_commands.P3 with double-quoted value → strip quotes" {
    local task_dir="$BATS_TEST_TMPDIR/task-g5"
    mkdir -p "$task_dir"
    # P3 值带双引号（YAML 字符串），脚本应 strip 引号后使用
    local fake
    fake=$(make_fake_pytest "2 failed, 5 passed" 1)
    cat > "$task_dir/P2-design.md" <<EOF
gate_commands:
  P3: "$fake"
  P5: "pytest -q --tb=no"
EOF
    run env -u TEST_RUNNER PATH="/usr/bin:/bin" TASK_DIR="$task_dir" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 0 ]
    [[ "$output" == *"classic red-light"* ]]
}
```

- [ ] **Step 5: 跑全部新测试**

Run: `bats agate/tests/unit/check-tdd-red.bats --filter "TDD.G"`
Expected: TDD.G1 PASS（Task 1 已实现），TDD.G2-G5 PASS（向后兼容路径，无需额外实现）

注意：TDD.G2-G5 可能直接通过——它们验证的是现有行为不被破坏。如果某个失败，说明 Step 3 的实现有回归。

- [ ] **Step 6: 跑全量 check-tdd-red 测试确认无回归**

Run: `bats agate/tests/unit/check-tdd-red.bats`
Expected: 全部 PASS（TD.1-TD.8, TDD.N1-N4, TDD.G1-G5）

- [ ] **Step 7: Commit**

```bash
git add agate/tests/unit/check-tdd-red.bats
git commit -m "test(check-tdd-red): add edge cases for gate_commands.P3 fallback"
```

---

## Task 3: check-gate.sh P3 分支传递 TASK_DIR

**Files:**
- Modify: `agate/scripts/check-gate.sh:137-138`（P3 分支）
- Test: `agate/tests/unit/check-gate.bats`

### 背景

当前 `check-gate.sh` P3 分支是 `exec "$SCRIPT_DIR/check-tdd-red.sh"`，不传递 TASK_DIR。P3-tdd.md 的 gate 规则示例已写 `check-tdd-red.sh $TASK_DIR`，但脚本未实现接收位置参数——文档先于实现。本 Task 修复此偏差，并让 check-tdd-red.sh 能读取 P2-design.md 的 gate_commands.P3。

### 步骤

- [ ] **Step 1: 写失败测试 — check-gate.sh P3 传递 TASK_DIR to check-tdd-red.sh**

注意：check-gate.bats 和 check-tdd-red.bats 是独立的 bats 文件，helper 函数不共享。需在测试内联创建 fake runner。

```bash
@test "PG.P3DIR: check-gate.sh P3 passes TASK_DIR to check-tdd-red.sh" {
    # 创建一个 fake runner 输出 assertion failure
    local task_dir="$BATS_TEST_TMPDIR/task-p3dir"
    mkdir -p "$task_dir"
    local fake="$BATS_TEST_TMPDIR/fake-pytest-p3dir"
    cat > "$fake" <<'RUNNER'
#!/bin/bash
cat <<'OUT'
2 failed, 5 passed
OUT
exit 1
RUNNER
    chmod +x "$fake"
    cat > "$task_dir/P2-design.md" <<EOF
gate_commands:
  P3: "$fake"
  P5: "pytest -q --tb=no"
EOF
    run env -u TEST_RUNNER PATH="/usr/bin:/bin" bash "$AGATE_SCRIPTS/check-gate.sh" P3 "$task_dir"
    [ "$status" -eq 0 ]
}
```

- [ ] **Step 2: 跑测试确认失败**

Run: `bats agate/tests/unit/check-gate.bats --filter "PG.P3DIR"`
Expected: FAIL（当前 P3 分支不传 TASK_DIR，check-tdd-red.sh 无法读取 gate_commands.P3）

- [ ] **Step 3: 实现 — check-gate.sh P3 分支传递 TASK_DIR**

旧代码（check-gate.sh L137-138）：
```bash
  P3)
      exec "$SCRIPT_DIR/check-tdd-red.sh" ;;
```

新代码：
```bash
  P3)
      exec "$SCRIPT_DIR/check-tdd-red.sh" "$TASK_DIR" ;;
```

同时修改 check-tdd-red.sh 接收位置参数（在 `set -euo pipefail`（L47）之后、runner 探测逻辑（L49）之前插入）：

```bash
# 接收可选的 TASK_DIR 位置参数（由 check-gate.sh 传递）
# 也可通过 TASK_DIR 环境变量提供
if [ -z "${TASK_DIR:-}" ] && [ $# -gt 0 ]; then
    TASK_DIR="$1"
fi
```

- [ ] **Step 4: 跑测试确认通过**

Run: `bats agate/tests/unit/check-gate.bats --filter "PG.P3DIR"`
Expected: PASS

- [ ] **Step 5: 跑全量 check-tdd-red 测试确认位置参数不破坏现有行为**

Run: `bats agate/tests/unit/check-tdd-red.bats`
Expected: 全部 PASS（现有测试不传位置参数，TASK_DIR 环境变量优先，位置参数是回退）

- [ ] **Step 6: Commit**

```bash
git add agate/scripts/check-gate.sh agate/scripts/check-tdd-red.sh agate/tests/unit/check-gate.bats
git commit -m "feat(check-gate): pass TASK_DIR to check-tdd-red.sh for gate_commands.P3"
```

---

## Task 4: 协议文档更新 — gate_commands 增加 P3 键

**Files:**
- Modify: `agate/assets/execution-roles/architect.md:39-49`（gate_commands 示例 + 说明）
- Modify: `agate/assets/templates/task-files.md:209-217`（gate_commands 模板）
- Modify: `agate/phase-cards/P2-design.md:51-59`（gate_commands 示例）
- Modify: `agate/phase-cards/P3-tdd.md:40-51`（gate 规则说明）
- Modify: `agate/assets/execution-roles/verifier.md:158`（非 pytest 说明）
- Modify: `agate/scripts/check-tdd-red.sh:25-38`（注释更新）

### 步骤

- [ ] **Step 1: 更新 architect.md — gate_commands 示例增加 P3 键**

在 `agate/assets/execution-roles/architect.md` 的 gate_commands 示例中增加 P3 键。

旧代码（L39-45）：
```markdown
  - `gate_commands:` — **P5/P6 的 gate 命令集，在 P2 固化，后续阶段不得修改**：
    ```yaml
    gate_commands:
      P5: "pytest -q --tb=no"                 # 紧凑输出（见下方规范）
      P5_e2e: "playwright test --reporter=line tests/e2e/"   # ui_affected 时必填
      P6: "pytest -q --tb=no tests/acceptance/"
    ```
```

新代码：
```markdown
  - `gate_commands:` — **P3/P5/P6 的 gate 命令集，在 P2 固化，后续阶段不得修改**：
    ```yaml
    gate_commands:
      P3: "pytest"                            # 可选：测试运行器（不带紧凑输出 flags，P3 红灯检查需 verbose 输出）
      P5: "pytest -q --tb=no"                 # 紧凑输出（见下方规范）
      P5_e2e: "playwright test --reporter=line tests/e2e/"   # ui_affected 时必填
      P6: "pytest -q --tb=no tests/acceptance/"
    ```
    **P3 键说明**（可选）：声明后 check-tdd-red.sh 自动读取作为测试运行器，无需主 Agent 手动设置 TEST_RUNNER 环境变量。P3 用 verbose 输出（区分 A/B 类错误），P5 用紧凑输出（只判过没过），两者分离。非 pytest 项目建议声明此键。
```

- [ ] **Step 2: 更新 task-files.md — gate_commands 模板增加 P3 键**

旧代码（L209-217）：
```markdown
## 3. gate 命令（在 P2 固化，后续不得修改）
gate_commands:
  P5: "pytest -q --tb=no"          # 紧凑输出模式（见下）
  P5_e2e: "playwright test --reporter=line tests/e2e/"   # ui_affected: true 时必填
  P6: "pytest -q --tb=no tests/acceptance/"
# 紧凑输出要求：gate 命令只供主 Agent 判断「过没过」，须用工具的汇总/安静模式
# （pytest --tb=no / cargo --quiet / dotnet --verbosity quiet / vitest --reporter=dot
#  / go test | tail -30 / mvn -q），保留通过失败汇总+失败清单，去掉逐项 traceback。
# 工具无紧凑模式时用 shell 兜底：命令 2>&1 | tail -N（语言无关）。
```

新代码：
```markdown
## 3. gate 命令（在 P2 固化，后续不得修改）
gate_commands:
  P3: "pytest"                     # 可选：测试运行器（verbose 输出，供 check-tdd-red.sh 区分 A/B 类错误）
  P5: "pytest -q --tb=no"          # 紧凑输出模式（见下）
  P5_e2e: "playwright test --reporter=line tests/e2e/"   # ui_affected: true 时必填
  P6: "pytest -q --tb=no tests/acceptance/"
# P3 键（可选）：声明后 check-tdd-red.sh 自动读取，无需主 Agent 手动设 TEST_RUNNER。
# P3 用 verbose 输出（区分 A/B 类错误），P5 用紧凑输出（只判过没过），两者分离。
# 非 pytest 项目建议声明此键（如 P3: "npx vitest run"）。
# 紧凑输出要求：P5/P6 gate 命令只供主 Agent 判断「过没过」，须用工具的汇总/安静模式
# （pytest --tb=no / cargo --quiet / dotnet --verbosity quiet / vitest --reporter=dot
#  / go test | tail -30 / mvn -q），保留通过失败汇总+失败清单，去掉逐项 traceback。
# 工具无紧凑模式时用 shell 兜底：命令 2>&1 | tail -N（语言无关）。
```

- [ ] **Step 3: 更新 P2-design.md — gate_commands 示例增加 P3 键**

旧代码（L55-59）：
```markdown
```yaml
gate_commands:
  P5: "pytest -q --tb=no"       # 紧凑输出模式
  P5_e2e: "playwright test --reporter=line tests/e2e/"  # ui_affected: true 时必填
```
```

新代码：
```markdown
```yaml
gate_commands:
  P3: "pytest"                  # 可选：测试运行器（verbose 输出，供 check-tdd-red.sh 自动读取）
  P5: "pytest -q --tb=no"       # 紧凑输出模式
  P5_e2e: "playwright test --reporter=line tests/e2e/"  # ui_affected: true 时必填
```
```

同时更新 P2-design.md 的 gate_commands 四字段检查（L102）。P3 是可选键，不纳入必填检查：

旧代码（L102）：
```markdown
- 四字段齐全（packages/domains/ui_affected/gate_commands）
```

保持不变——P3 是 gate_commands 的子键，gate_commands 本身仍是必填的四字段之一。但增加一行说明：

在 L102 后增加：
```markdown
- gate_commands.P3 可选（非 pytest 项目建议声明，供 check-tdd-red.sh 自动读取测试运行器）
```

- [ ] **Step 4: 更新 P3-tdd.md — gate 规则说明**

旧代码（L40-51）：
```markdown
## gate 规则（check-tdd-red.sh）

```bash
check-tdd-red.sh $TASK_DIR
```

- **exit 0**：真红灯（assertion 失败 / 项目内 import 失败 = B类错误）— 测试正确但因实现未写而失败
- **exit 1**：假红灯（SyntaxError / 第三方 import 失败 = A类错误）— 测试代码自身错误
- **exit 2**：绿了 — 实现先于测试，违反 TDD
- **exit 3**：无可用测试运行器

**非 pytest 技术栈**：设置 `TEST_RUNNER` 环境变量指向项目实际测试命令（如 `TEST_RUNNER="npm test"`），check-tdd-red.sh 会使用该命令而非默认的 pytest 探测。这是 agate 协议保持技术栈无关的标准接入点，不需要绕过脚本手动验证。
```

新代码：
```markdown
## gate 规则（check-tdd-red.sh）

```bash
check-tdd-red.sh $TASK_DIR
```

- **exit 0**：真红灯（assertion 失败 / 项目内 import 失败 = B类错误）— 测试正确但因实现未写而失败
- **exit 1**：假红灯（SyntaxError / 第三方 import 失败 = A类错误）— 测试代码自身错误
- **exit 2**：绿了 — 实现先于测试，违反 TDD
- **exit 3**：无可用测试运行器

**测试运行器探测链**：`$TEST_RUNNER` 环境变量 → `gate_commands.P3`（P2-design.md 声明）→ `which pytest` → exit 3。非 pytest 项目在 P2 gate_commands 声明 `P3` 键后，check-tdd-red.sh 自动读取，无需手动设置环境变量。`$TEST_RUNNER` 环境变量始终优先（手动覆盖）。
```

- [ ] **Step 5: 更新 verifier.md — 非 pytest 技术栈说明**

旧代码（L158）：
```markdown
- **非 pytest 技术栈**：若 gate_commands 包含 check-tdd-red.sh，设置 `TEST_RUNNER` 环境变量指向项目实际测试命令（如 `TEST_RUNNER="npm test"`），check-tdd-red.sh 会使用该命令而非默认的 pytest 探测。这是 agate 协议保持技术栈无关的标准接入点。
```

新代码：
```markdown
- **非 pytest 技术栈**：若 P2 gate_commands 声明了 `P3` 键，check-tdd-red.sh 自动读取测试运行器命令。也可通过 `TEST_RUNNER` 环境变量手动覆盖（优先级最高）。这是 agate 协议保持技术栈无关的标准接入点。
```

- [ ] **Step 5b: 更新 P5-verification.md — 非 pytest 技术栈说明（与 verifier.md 同一段落）**

旧代码（P5-verification.md L39）：
```markdown
**非 pytest 技术栈**：若 P5 gate_commands 包含 check-tdd-red.sh（重跑 TDD 红灯检查），设置 `TEST_RUNNER` 环境变量指向项目实际测试命令（如 `TEST_RUNNER="npm test"`），check-tdd-red.sh 会使用该命令而非默认的 pytest 探测。这是 agate 协议保持技术栈无关的标准接入点。
```

新代码：
```markdown
**非 pytest 技术栈**：若 P2 gate_commands 声明了 `P3` 键，check-tdd-red.sh 自动读取测试运行器命令。也可通过 `TEST_RUNNER` 环境变量手动覆盖（优先级最高）。这是 agate 协议保持技术栈无关的标准接入点。
```

- [ ] **Step 5c: 更新 state-machine.md — TDD 红灯检查设计说明代码块**

state-machine.md L278-300 含 check-tdd-red.sh 的简化版设计说明代码块，描述的回退链不含 `gate_commands.P3`。更新注释和回退链。

旧注释（L290-291）：
```bash
# 环境变量 TEST_RUNNER：主 Agent 从 P0-brief.md env_constraints.debug_env 提取。
# 环境变量 PROJECT_MODULE：项目模块前缀（用于 B 类检测），未设置则退化为启发式。
```

新注释：
```bash
# 测试运行器探测链：$TEST_RUNNER → gate_commands.P3（P2-design.md 声明）→ which pytest → exit 3
# 环境变量 TEST_RUNNER：最高优先级，手动覆盖。
# 环境变量 TASK_DIR：任务目录路径，用于读取 P2-design.md 的 gate_commands.P3（可选键）。
# 环境变量 PROJECT_MODULE：项目模块前缀（用于 B 类检测），未设置则退化为启发式。
```

旧回退链代码（L293-300）：
```bash
if [ -n "$TEST_RUNNER" ]; then
    RUNNER="$TEST_RUNNER"
elif command -v pytest &>/dev/null; then
    RUNNER="pytest"
else
    echo "TDD_CHECK: no test runner found. Set TEST_RUNNER env var." >&2
    exit 3
fi
```

新回退链代码：
```bash
if [ -n "$TEST_RUNNER" ]; then
    RUNNER="$TEST_RUNNER"
elif [ -n "${TASK_DIR:-}" ] && [ -f "$TASK_DIR/P2-design.md" ]; then
    # 从 gate_commands.P3 读取（可选键，见 scripts/check-tdd-red.sh 完整实现）
    P3_CMD=$(GATE_FILE="$TASK_DIR/P2-design.md" python3 -c '
import re, os, sys
content = open(os.environ["GATE_FILE"]).read()
m = re.search(r"^gate_commands:.*\n((?:  .*\n)*)", content, re.MULTILINE)
if m:
    for k, v in re.findall(r"^  (P3):\s*(.+)$", m.group(1), re.MULTILINE):
        print(v.strip().strip("\""))
' 2>/dev/null || true)
    if [ -n "$P3_CMD" ]; then
        RUNNER="$P3_CMD"
    elif command -v pytest &>/dev/null; then
        RUNNER="pytest"
    else
        echo "TDD_CHECK: no test runner found. Set TEST_RUNNER, declare gate_commands.P3, or install pytest." >&2
        exit 3
    fi
elif command -v pytest &>/dev/null; then
    RUNNER="pytest"
else
    echo "TDD_CHECK: no test runner found. Set TEST_RUNNER, declare gate_commands.P3, or install pytest." >&2
    exit 3
fi
```

> 注意：state-machine.md 中的代码块是设计说明性质（简化版），完整实现在 `scripts/check-tdd-red.sh`。此处更新保持设计说明与实际实现的回退链一致。

- [ ] **Step 6: 更新 check-tdd-red.sh 注释**

旧注释（L25-38）：
```bash
# 环境变量：
#   TEST_RUNNER — 测试运行器命令（主 Agent 从 P0-brief.md env_constraints.debug_env 提取）
#                 回退链：$TEST_RUNNER → which pytest → exit 3
#   PROJECT_MODULE — 项目模块前缀（用于 B 类检测，如 "myapp"、"webapp"）
#                    若未设置，B 类检测退化为启发式（所有 ImportError 视为 B 类）
#                    非 Python 项目应设置此变量以匹配项目内模块路径
#
# 已验证的非 pytest runner 适配示例：
#   vitest 项目示例（已验证）：
#     TEST_RUNNER="npx vitest run"
#     TEST_RUNNER_FLAGS="--reporter=default"   # 必须显式设置为非 -q 值，vitest 不识别 -q
#     TEST_ERROR_PATTERN="Failed Suites [0-9]+"  # vitest 的 collection-error 摘要不含 "N error" 文本
#     TEST_IMPORT_PATTERN="Cannot find (module|package) '"  # vitest 的 import 错误格式不含 "ImportError:"，需覆盖
#     PROJECT_MODULE="{项目内模块前缀}"
```

新注释：
```bash
# 环境变量：
#   TEST_RUNNER — 测试运行器命令（最高优先级，手动覆盖）
#   TASK_DIR — 任务目录路径（用于读取 P2-design.md 的 gate_commands.P3）
#              也可通过位置参数 $1 传入（check-gate.sh 调用时传递）
#   PROJECT_MODULE — 项目模块前缀（用于 B 类检测，如 "myapp"、"webapp"）
#                    若未设置，B 类检测退化为启发式（所有 ImportError 视为 B 类）
#                    非 Python 项目应设置此变量以匹配项目内模块路径
#
# 测试运行器探测链：$TEST_RUNNER → gate_commands.P3（P2-design.md）→ which pytest → exit 3
#
# gate_commands.P3（可选键，architect 在 P2 声明）：
#   非 pytest 项目在 P2-design.md 声明 gate_commands.P3 后，本脚本自动读取，无需主 Agent 手动设环境变量。
#   P3 键用 verbose 输出（区分 A/B 类错误），P5 键用紧凑输出（只判过没过），两者分离。
#
# 已验证的非 pytest runner 适配示例：
#   vitest 项目示例（已验证）：
#     方式一（推荐）：在 P2-design.md 声明 gate_commands.P3: "npx vitest run"
#     方式二（手动）：TEST_RUNNER="npx vitest run"
#     以下环境变量两种方式都需设置：
#     TEST_RUNNER_FLAGS="--reporter=default"   # 必须显式设置为非 -q 值，vitest 不识别 -q
#     TEST_ERROR_PATTERN="Failed Suites [0-9]+"  # vitest 的 collection-error 摘要不含 "N error" 文本
#     TEST_IMPORT_PATTERN="Cannot find (module|package) '"  # vitest 的 import 错误格式不含 "ImportError:"，需覆盖
#     PROJECT_MODULE="{项目内模块前缀}"
```

- [ ] **Step 7: 跑 consistency 检查确认无 ERROR**

Run: `python3 agate/scripts/check-protocol-consistency.py`
Expected: 0 ERROR（可能有 WARNING 关于 P3 新键——如果 CHECK 4 对 P3 报缺失，需要在 Task 5 修复）

- [ ] **Step 8: 跑 shellcheck**

Run: `shellcheck -S warning agate/scripts/check-tdd-red.sh`
Expected: 无 error

- [ ] **Step 9: 跑全量 bats**

Run: `bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/`
Expected: 全部 PASS

- [ ] **Step 10: Commit**

```bash
git add agate/assets/execution-roles/architect.md agate/assets/templates/task-files.md agate/phase-cards/P2-design.md agate/phase-cards/P3-tdd.md agate/phase-cards/P5-verification.md agate/assets/execution-roles/verifier.md agate/state-machine.md agate/scripts/check-tdd-red.sh
git commit -m "docs: add gate_commands.P3 key to protocol docs"
```

---

## Task 5: check-protocol-consistency.py — 确认 CHECK 4 对 P3 键的行为

**Files:**
- Verify: `agate/scripts/check-protocol-consistency.py:267-336`（CHECK 4 gate_commands 键集合检查）

### 背景

CHECK 4 检查 gate_commands 键集合跨文件一致：以 architect.md 为权威源，其他文件（task-files.md, dispatch-prompt.md）的键集合必须是 architect.md 的子集。新增 P3 键后，需要确认行为正确。

CHECK 4 的行为是可预测的：
- architect.md 加了 P3 键 → 权威源键集含 P3
- task-files.md 加了 P3 键（Task 4 Step 2）→ 键集含 P3 → 不报缺失
- dispatch-prompt.md 无 gate_commands YAML 块（只有文本引用 `{build_command}`）→ `_extract_gate_keys` 返回空 set → 在 `present` 字典中被过滤掉（`present = {k: v for k, v in sources.items() if v}`）→ 不参与比对 → 不报缺失

因此 CHECK 4 不会因 P3 键报 ERROR，无需修改 `check-protocol-consistency.py`。

### 步骤

- [ ] **Step 1: 确认 CHECK 4 不报 ERROR**

在 Task 4 完成后跑 consistency 检查：
```bash
python3 agate/scripts/check-protocol-consistency.py
```

Expected: 0 ERROR（CHECK 4 应报 OK）

- [ ] **Step 2: 如果 CHECK 4 报 ERROR（说明 task-files.md 的 P3 键缩进不正确）**

检查 task-files.md 的 gate_commands 块中 P3 键缩进是否与 P5/P6 键一致（2 空格缩进）。修复缩进后重跑。

- [ ] **Step 3: 无需 commit（本 Task 是验证步骤，不修改文件）**

---

## Task 6: check-gate.sh P3 注释更新 + 端到端验证

**Files:**
- Modify: `agate/scripts/check-gate.sh:9`（注释更新）
- Test: 全量 bats

### 步骤

- [ ] **Step 1: 更新 check-gate.sh 注释**

旧注释（L9）：
```bash
# 可脚本化的 gate（exit 0/1）：P3 / P4 / P7
```

新注释：
```bash
# 可脚本化的 gate（exit 0/1）：P3（check-tdd-red.sh，自动读取 gate_commands.P3）/ P4 / P7
```

- [ ] **Step 2: 全量验证**

Run:
```bash
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
python3 agate/scripts/check-protocol-consistency.py
shellcheck -S warning agate/scripts/*.sh
bash agate/tests/scripts/count-tests.sh
```

Expected:
- bats: 全部 PASS
- consistency: 0 ERROR
- shellcheck: 无 error
- count-tests: 用例数与文档一致

- [ ] **Step 3: Commit**

```bash
git add agate/scripts/check-gate.sh
git commit -m "docs: update check-gate.sh P3 comment for gate_commands.P3"
```

---

## Task 7: 更新 hardening-roadmap.md

**Files:**
- Modify: `docs/hardening-roadmap.md`

### 步骤

- [ ] **Step 1: 在 roadmap 中记录本次改进**

在 `docs/hardening-roadmap.md` 的 v0.25.0 版本节（或新建）中添加：

```markdown
### P2.49: gate_commands.P3 — check-tdd-red.sh 自动读取测试运行器

**状态**：已实施
**来源**：T076 复盘（非 pytest 项目测试命令重复声明问题）
**改动**：
- gate_commands 新增可选 P3 键（architect 在 P2 声明测试运行器命令）
- check-tdd-red.sh 回退链扩展：`$TEST_RUNNER → gate_commands.P3 → which pytest → exit 3`
- P3 键用 verbose 输出（区分 A/B 类错误），P5 键用紧凑输出（只判过没过），两者分离
**不修理由**（P3 e2e 质量闸门）：
- "选择器写得好不好"不是机器可判定的，gate 不做语义判断
- P5 实跑 e2e 已经是正确的防线，T076 也在 P5 发现并修复了
- test-designer.md 已有指导，执行不到位是 subagent 质量问题
```

- [ ] **Step 2: Commit**

```bash
git add docs/hardening-roadmap.md
git commit -m "docs: record P2.49 gate_commands.P3 in hardening roadmap"
```

---

## Self-Review

### Spec coverage

- [x] check-tdd-red.sh 自动读取 gate_commands.P3 — Task 1
- [x] check-gate.sh 传递 TASK_DIR — Task 3
- [x] 协议文档更新（architect/task-files/P2/P3/P5-verification/verifier/state-machine）— Task 4
- [x] consistency 检查不报 P3 缺失 — Task 5
- [x] 注释更新 — Task 4 Step 6 + Task 6
- [x] roadmap 记录 — Task 7
- [x] P3 e2e 质量闸门不修的理由记录 — Task 7

### Placeholder scan

无 placeholder——所有步骤包含完整代码。

### Type consistency

- `gate_commands.P3` 在所有文件中命名一致
- check-tdd-red.sh 的 `TASK_DIR` 环境变量与位置参数 `$1` 两种传入方式一致
- Python 解析逻辑使用环境变量 `GATE_FILE`（与 check-gate.sh P5 分支一致），agate-capture-env-baseline.sh 使用 `P2_DESIGN`——两者命名不同但功能相同，不在本计划范围内统一
