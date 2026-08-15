# T075 复盘机制化修复 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 T075 复盘的 3 个效率问题从"角色文件规则"升级为"机械化机制/脚本"，不增加 agent 认知负担：P2.61 gate 命令可执行性检查、P2.62 P3 自检注入 + 失败归类提示、P2.63 修复轮 dispatch-context 模板。

**Architecture:** 三个机制全部是"脚本/模板注入"，不依赖 agent 自觉：
- P2.61: check-gate.sh P2 分支解析 gate_commands 命令的第一个 token，`command -v` 验证存在性（WARNING 不阻断）
- P2.62: dispatch-prompt.md 新增 P3 派发追加块（强制自检步骤）+ check-tdd-red.sh 经典红灯分支输出断言矛盾提示
- P2.63: dispatch-prompt.md 新增修复轮派发追加块（主 Agent 模板：引用上轮 + 只写增量）

**Tech Stack:** Bash（gate 脚本）, Markdown（模板/角色文件）, Bats（测试）

---

## 背景

### 问题（T075 复盘）

1. **P2.61**（0.5h 损耗）：architect 声明的 gate_commands 命令不可执行（`python` 不存在，应 `.venv/bin/python`）。P3 gate exit 127 才发现。
2. **P2.62**（1.5h 损耗，最大损耗源）：test-designer 手写魔数断言与测试数据矛盾（7 条），P3 红灯被放行（经典红灯无法区分"实现未写"vs"断言数据矛盾"），P5 才发现。
3. **P2.63**（0.5h 损耗）：dispatch-context 多轮修复重复写完整约束（20 个文件）。

### 为什么用机制而非规则

角色文件规则依赖 agent 自觉（agent 本能：不是必须的就不做）。机制/脚本是结构性的——流程迫使做对。

### 关键设计约束

- **P2.61 用 WARNING 不阻断**：P2 阶段环境可能未就绪（如 venv 未建），硬拦截会误伤。WARNING 提前暴露，P3 才有真实执行。
- **P2.62 经典红灯提示也是 WARNING**：经典红灯在 P3 也正常（实现未写时断言失败）。不能硬拦截，只提示主 Agent 检查测试输出。
- **P2.63 是给主 Agent 的模板**：dispatch-context 引用上轮文件 + 只写增量，不是给 subagent 的规则。

---

## 文件结构

### 修改文件

| 文件 | 改动 |
|------|------|
| `agate/scripts/check-gate.sh` | P2 分支加命令可执行性检查（P2.61） |
| `agate/scripts/check-tdd-red.sh` | 经典红灯分支加断言矛盾提示（P2.62） |
| `agate/scripts/agate-render-dispatch-prompt.sh` | 新增 P3 case 分支（接线 P3 派发追加块） |
| `agate/assets/templates/dispatch-prompt.md` | 新增 P3 派发追加块 + 修复轮派发追加块（P2.62/P2.63） |
| `agate/tests/unit/check-gate.bats` | P2 命令可执行性测试 |
| `agate/tests/unit/check-tdd-red.bats` | 经典红灯提示测试 |
| `agate/tests/unit/agate-render-dispatch-prompt.bats` | P3 render 测试 |
| `agate/tests/README.md` | 用例数表更新 |
| `docs/hardening-roadmap.md` | P2.61/P2.62/P2.63 状态更新 |

---

## Task 1: check-gate.sh P2 命令可执行性检查 (P2.61)

**Files:**
- Modify: `agate/scripts/check-gate.sh`
- Modify: `agate/tests/unit/check-gate.bats`

- [ ] **Step 1: 先写失败测试**

在 `check-gate.bats` 追加：

```bash
@test "G_CMD_EXEC.1: P2 gate_commands 命令不可执行 → WARNING 不阻断 (exit 2)" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：方案一
### 候选方案 B：方案二
## 权衡
A 更简单，B 更稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands:
  P3: "definitely-nonexistent-cmd --flag"
  P5: "echo hi"
EOF
    cat > "$dir/P2-review.md" <<'EOF'
---
agent: test
status: approved
---
通过。
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
    [[ "$output" == *"definitely-nonexistent-cmd"* ]]
}

@test "G_CMD_EXEC.2: P2 gate_commands 命令均可执行 → 无 WARNING (exit 2)" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：方案一
### 候选方案 B：方案二
## 权衡
A 更简单，B 更稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands:
  P3: "true"
  P5: "echo hi"
EOF
    cat > "$dir/P2-review.md" <<'EOF'
---
agent: test
status: approved
---
通过。
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
    [[ "$output" != *"不存在"* ]]
}
```

- [ ] **Step 2: 运行测试验证失败**

Run: `bats agate/tests/unit/check-gate.bats --filter "G_CMD_EXEC"`
Expected: FAIL（check-gate.sh 当前无此检查）

- [ ] **Step 3: 修改 check-gate.sh**

在 P2 分支的 `echo "GATE P2: 需从 P2-design.md gate_commands 动态读取，主 Agent 自行判定"` 之前（约 L137），插入命令可执行性检查：

```bash
      # P2.61: gate_commands 命令可执行性检查（WARNING 不阻断）
      # T075 教训：architect 写 `python -m pytest` 但系统无 python 命令，P3 gate exit 127
      # 解析 gate_commands 每个命令的第一个 token，验证存在性
      # 第一个 token 含 / → 跳过（相对/绝对路径如 .venv/bin/python，P2 阶段 venv 可能未建，不误报）
      # 否则 → command -v 验证
      MISSING_CMDS=$(GATE_FILE="$P2_FILE" python3 -c '
import re, os, sys
with open(os.environ["GATE_FILE"]) as f:
    content = f.read()
if not content.endswith(chr(10)):
    content += chr(10)
m = re.search(r"^gate_commands:[ \t]*\n((?:  .*\n|\s*\n)*)", content, re.MULTILINE)
if not m:
    sys.exit(0)
block = m.group(1)
for k, v in re.findall(r"^  (P[0-9]\w*):\s*(.+)$", block, re.MULTILINE):
    if k.endswith("_formatter") or k == "project_module":
        continue
    val = v.strip().strip("\"").strip(chr(39))
    if not val:
        continue
    token = val.split()[0]
    token = token.lstrip("$(").rstrip(")")
    if "/" in token:
        continue
    print(f"{k}:{token}")
' 2>/dev/null || echo "")
      if [ -n "$MISSING_CMDS" ]; then
          while IFS= read -r entry; do
              [ -z "$entry" ] && continue
              key=$(echo "$entry" | cut -d: -f1)
              token=$(echo "$entry" | cut -d: -f2-)
              if ! command -v "$token" &>/dev/null; then
                  echo "GATE P2 WARNING: gate_commands.$key 命令 '$token' 不存在于当前环境——请确认使用完整路径（如 .venv/bin/pytest）或安装依赖。T075 教训：python 不存在导致 P3 gate exit 127" >&2
              fi
          done <<< "$MISSING_CMDS"
      fi
```

**注意**：命令 token 含 `/` 时跳过（相对/绝对路径，如 `.venv/bin/python`——这种路径在 P2 阶段可能还没建，不能误报）。

- [ ] **Step 4: 运行测试验证通过**

Run: `bats agate/tests/unit/check-gate.bats --filter "G_CMD_EXEC"`
Expected: ALL PASS

- [ ] **Step 5: shellcheck**

Run: `shellcheck -S warning agate/scripts/check-gate.sh`
Expected: 0 errors

- [ ] **Step 6: Commit**

```bash
git add agate/scripts/check-gate.sh agate/tests/unit/check-gate.bats
git commit -m "feat: check-gate.sh P2 checks gate_commands executability (P2.61)"
```

---

## Task 2: check-tdd-red.sh 经典红灯断言矛盾提示 (P2.62)

**Files:**
- Modify: `agate/scripts/check-tdd-red.sh`
- Modify: `agate/tests/unit/check-tdd-red.bats`

- [ ] **Step 1: 先写失败测试**

在 `check-tdd-red.bats` 追加：

```bash
@test "TD.FAIL_HINT: classic red-light outputs assertion-mismatch hint" {
    local fake
    fake=$(make_fake_pytest "2 failed, 5 passed
FAILED tests/test_x.py::test_x" 1)
    local task_dir="$BATS_TEST_TMPDIR/task-failhint"
    mkdir -p "$task_dir"
    cat > "$task_dir/P2-design.md" <<EOF
gate_commands:
  P3: "$fake"
  P3_formatter: "pytest.sh"
EOF
    run env -u TEST_RUNNER PATH="/usr/bin:/bin" TASK_DIR="$task_dir" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 0 ]
    [[ "$output" == *"断言"*"数据"* ]]
}
```

- [ ] **Step 2: 运行测试验证失败**

Run: `bats agate/tests/unit/check-tdd-red.bats --filter "TD.FAIL_HINT"`
Expected: FAIL（当前经典红灯分支无此提示）

- [ ] **Step 3: 修改 check-tdd-red.sh**

在 judge_result() 的经典红灯分支（约 L134-138），在 return 0 之前追加提示：

当前代码（L134-138）：
```bash
    if [ "$failed" -gt 0 ]; then
        echo "TDD_CHECK: classic red-light (assertion failures only)"
        return 0
    fi
```

修改为：
```bash
    if [ "$failed" -gt 0 ]; then
        echo "TDD_CHECK: classic red-light (assertion failures only)"
        echo "TDD_CHECK 提示: 测试能运行但断言失败。若失败原因是断言与测试数据矛盾（如行数/列数/页数不符），这是测试代码 bug，应退回 P3 修正断言——不是 P4 实现问题。T075 教训：7 条魔数断言与数据矛盾到 P5 才暴露。" >&2
        return 0
    fi
```

- [ ] **Step 4: 运行测试验证通过**

Run: `bats agate/tests/unit/check-tdd-red.bats`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add agate/scripts/check-tdd-red.sh agate/tests/unit/check-tdd-red.bats
git commit -m "feat: check-tdd-red.sh classic red-light hints assertion-mismatch (P2.62)"
```

---

## Task 3: dispatch-prompt.md P3 派发追加 + 修复轮派发追加 (P2.62/P2.63)

**Files:**
- Modify: `agate/assets/templates/dispatch-prompt.md`
- Modify: `agate/tests/unit/check-gate.bats`

- [ ] **Step 1: 在阶段特定提示区新增 P3 派发追加块**

在 dispatch-prompt.md 的 `## 阶段特定提示` 节下、`### P4 派发追加` 之前，插入：

```markdown
### P3 派发追加
```
## P3 自检（强制）
产出测试代码后，必须自跑测试，确认每个红灯的失败原因都是"被测模块未实现"（import 失败 / 模块不存在 / 组件未导出）。
如果某个红灯的失败原因是"断言与测试数据矛盾"（如断言行数/列数/页数与 fixture 不符）——这是测试代码 bug，先修正断言再交付，不要交付给 P5。
手写魔数断言（`expect(x).toBe(100)` 但数据实际 50 行）与数据矛盾是 T075 的教训，P3 阶段就要发现。
```
```

- [ ] **Step 2: 接线 render 脚本 P3 case 分支（BLOCKER-1 修复）**

`agate-render-dispatch-prompt.sh` 的 case（L81-98）当前只有 P2/P4/P5|P6/P8，没有 P3 分支——P3 派发时 P3 追加块会被静默丢弃。在 case 中追加：

```bash
    P3)
        appendix="$(sed -n '/^### P3 派发追加$/,/^### /p' "$TEMPLATE" | sed '/^### /d' | extract_first_code_block)"
        ;;
```

**注意**：`### P3 派发追加` 块在模板中位于 `### P2 派发追加` 之后、`### P4 派发追加` 之前。sed 区间 `^### P2 派发追加$` 到 `^### /` 的终点会从 P4 头变为 P3 头——P2 内容完整保留。

- [ ] **Step 3: 追加 P3 render 测试（TDD）**

在 `agate/tests/unit/agate-render-dispatch-prompt.bats` 追加（`setup()` 已创建 `$TEST_TASK_DIR`，直接用）：

```bash
@test "RP.16: P3 renders P3 self-check appendix" {
    local output
    output=$(AGATE_ROOT="$AGATE_ROOT" bash "$AGATE_SCRIPTS/agate-render-dispatch-prompt.sh" P3 test-designer "$TEST_TASK_DIR")
    [[ "$output" == *"P3 自检"* ]]
}
```

先运行确认失败（当前 render 脚本无 P3 case → 无 "P3 自检"），再接线后通过。

- [ ] **Step 4: 在阶段特定提示区新增修复轮派发追加块**

在 `### P4 回退派发追加` 之后、`### P8 派发追加` 之前，插入：

```markdown
### 修复轮派发追加（review needs-revision / 修复轮时使用，给主 Agent 的模板）

主 Agent 修复轮派发时，dispatch-context 用增量模式：
- 上轮产出路径：{P{N}-产出文件.md 路径}
- 上轮 dispatch-context：{P{N}-dispatch-context-{role}.md 路径}（复用其约束）
- 修复目标：{具体要修复的问题}
- 不要重写完整目标/约束/上游关联——引用上轮文件即可
```

- [ ] **Step 5: 追加 drift 测试**

在 `check-gate.bats` 的 drift 测试区域（D-drift-1/D-drift-2 附近），追加：

```bash
@test "D-drift-5: dispatch-prompt.md 含'P3 自检'" {
    grep -q 'P3 自检' "$AGATE_ROOT/assets/templates/dispatch-prompt.md"
}

@test "D-drift-6: dispatch-prompt.md 含'修复轮派发追加'" {
    grep -q '修复轮派发追加' "$AGATE_ROOT/assets/templates/dispatch-prompt.md"
}
```

> **注意**：D-drift-4 已被既有测试占用（dispatch-context.md 含 XML 派发指引节），故新测试从 D-drift-5 开始。

- [ ] **Step 6: 运行测试验证通过**

Run: `bats agate/tests/unit/check-gate.bats --filter "D-drift"` 和 `bats agate/tests/unit/agate-render-dispatch-prompt.bats`
Expected: ALL PASS

- [ ] **Step 7: Commit**

```bash
git add agate/assets/templates/dispatch-prompt.md agate/scripts/agate-render-dispatch-prompt.sh agate/tests/unit/agate-render-dispatch-prompt.bats agate/tests/unit/check-gate.bats
git commit -m "feat: add P3 self-check + revision-round dispatch templates, wire P3 render (P2.62/P2.63)"
```

---

## Task 4: 更新 roadmap + 全量验证

**Files:**
- Modify: `docs/hardening-roadmap.md`

- [ ] **Step 1: 更新 P2.61-P2.63 状态**

将 `docs/hardening-roadmap.md` 中 T075 复盘的三行表格替换为标题块格式 + 已实施：

```markdown
**P2.61: architect gate_commands 校验清单 → 升级为 gate 脚本检查**

**状态**：已实施
**来源**：T075 复盘 AGATE-M1（gate_commands 声明不可执行命令）
**改动**：
- architect 角色文件增加 gate_commands 校验清单（规则层）
- check-gate.sh P2 分支增加命令可执行性检查（机制层，WARNING 不阻断）

**P2.62: test-designer 量化断言 → P3 自检注入 + 失败归类提示**

**状态**：已实施
**来源**：T075 复盘 EXEC-1（手写魔数断言与测试数据矛盾）
**改动**：
- dispatch-prompt.md 新增 P3 派发追加块（强制自检步骤，机械注入每次 P3 派发）
- check-tdd-red.sh 经典红灯分支输出断言矛盾提示（WARNING）

**P2.63: dispatch-context 修复轮增量模式**

**状态**：已实施
**来源**：T075 复盘 AGATE-M2（dispatch-context 维护负担）
**改动**：
- dispatch-prompt.md 新增修复轮派发追加块（主 Agent 模板：引用上轮 + 只写增量）
```

- [ ] **Step 2: 更新 tests/README.md 用例数表**

`agate/tests/README.md` 覆盖度表当前已漂移（check-gate 表列 34 实际 91、check-tdd-red 表列 28 实际 30、render-dispatch-prompt 行缺失）。本次改动后：
- check-gate.bats：91 → **95**（+G_CMD_EXEC.1/2 + D-drift-5/6）
- check-tdd-red.bats：30 → **31**（+TD.FAIL_HINT）
- agate-render-dispatch-prompt.bats：**新增行**，值 15 → **16**（+RP.16）
- 总计：**513**（+6）

以 `count-tests.sh` 实际输出为准修正表。

- [ ] **Step 3: 全量验证**

Run: `bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/`
Expected: ALL PASS

Run: `python3 agate/scripts/check-protocol-consistency.py`
Expected: 0 ERROR

Run: `shellcheck -S warning agate/scripts/*.sh`
Expected: 0 errors

Run: `bash agate/tests/scripts/count-tests.sh`
Expected: 总计 513（507+6）

- [ ] **Step 4: Commit**

```bash
git add docs/hardening-roadmap.md agate/tests/README.md
git commit -m "docs: mark P2.61-P2.63 as implemented (mechanism layer)"
```

---

## Self-Review

### 1. Spec coverage

| 需求 | Task |
|------|------|
| P2.61 命令可执行性检查（gate 脚本） | Task 1 |
| P2.62 P3 自检注入 + 失败归类提示 | Task 2 + Task 3 Step 1 |
| P2.62 render 脚本 P3 接线 | Task 3 Step 2-3 |
| P2.63 修复轮 dispatch-context 模板 | Task 3 Step 4 |
| tests/README.md + roadmap 更新 + 验证 | Task 4 |

### 2. 不增加 agent 负担的验证

- P2.61: 脚本自动检查，主 Agent 只看 WARNING
- P2.62: dispatch-prompt 机械注入自检步骤 + 脚本提示，subagent/主 Agent 不需要额外记忆
- P2.63: 模板给主 Agent 填空，不需要从零构思

### 3. Placeholder scan

无 TBD/TODO。

### 4. 向后兼容

- P2.61 WARNING 不阻断（exit 2 不变），不影响现有 P2 gate 通过
- P2.62 经典红灯仍 exit 0，只加 WARNING
- P2.63 模板是新增块，不影响现有派发
- render 脚本 P3 case 是新增分支，不影响 P2/P4/P5/P6/P8 现有分支
