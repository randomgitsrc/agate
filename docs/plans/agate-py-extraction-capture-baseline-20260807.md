# agate IPC 抽离批次 3：agate-capture-env-baseline.sh + 共享工具扩展 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 完成 `agate/scripts/agate-capture-env-baseline.sh`（8 处内联 python）的抽离：新增专用 `agate-read-p5-commands.py`（P5 gate_commands 解析器），扩展共享工具 `agate-json-get.py` 增加 `list` 子命令，把 8 处内联全部换为调用新工具。

**Architecture:** （1）`agate-read-p5-commands.py` 从 `P2_DESIGN` 环境变量读 P2-design.md，解析 `gate_commands.P5*` 键，输出 `{"commands":[{cmd,formatter,suffix}]}`；**无 `gate_commands:` 块时输出空**（供 bash `[ -z "$P5_DATA" ]` 判定跳过，保持第 48 行语义）；有块但无 P5 命令键时输出 `{"commands":[]}`（非空，与 ORIG 一致）。（2）`agate-json-get.py` 新增 `list KEY` 子命令（逐行打印 `d.get(KEY,[])` 每个元素，用于 failed_tests 迭代）。（3）capture-env-baseline.sh 的 8 处内联分别映射到 `get`/`len`/`index`/`list` 子命令。行为等价 → 既有 agate-capture-env-baseline.bats（15 测试）是强兜底。

**Tech Stack:** bash（薄壳）+ python3（专用解析器 + 共享工具）+ bats（测试）。

**背景调研（已确认）：**
- 触发文件：`agate/scripts/agate-read-p5-commands.py`（新增）、`agate/scripts/agate-json-get.py`（改）、`agate/scripts/agate-capture-env-baseline.sh`（改）、`agate/tests/*.bats`（改）→ self-gate 触发
- 8 处内联分布：
  - 第 25-47 行：P5 gate_commands 解析（多行，输出**裸数组** `[...]`，无 P5 块时 `sys.exit(0)` 输出空）
  - 第 64 行：`len(json.load(sys.stdin))`（**顶层数组长度**）
  - 第 68-69 行：`d[$idx]['cmd']` / `d[$idx]['formatter']`（**顶层数组索引**）
  - 第 84 行：`d.get("exit_code",0)` → `get exit_code 0`
  - 第 91-96 行：`for t in d.get("failed_tests",[]): print(t)` → 需新 `list` 子命令
  - 第 98-99 行：`d.get("failed",0)` / `d.get("errors",0)` → `get`
- **关键设计决策**：P5 解析器输出从「裸数组」改为「对象 `{"commands":[...]}`」，与 P3 解析器（`agate-read-gate-commands.py`）输出结构一致，从而复用共享工具现有的 `len commands` / `index commands IDX cmd` 子命令，无需为顶层数组新增 `alen`/`aindex`。**无 P5 块仍输出空**（保持第 48 行 `[ -z "$P5_DATA" ]` 语义）。P5_DATA 形状变化仅影响内部缓存 key（第 51 行 sha256），无测试断言其形状，安全。
- 现已有工具与解析器：`agate-json-get.py`（get/len/index/set/count_prefix）、`agate-read-gate-commands.py`（P3）。本批新增 `list` 子命令 + 专用 P5 解析器。

---

## File Structure

- **Create** `agate/scripts/agate-read-p5-commands.py` — P5 gate_commands 解析器（输出对象 `{"commands":[...]}`，无 P5 块输出空）。
- **Modify** `agate/scripts/agate-json-get.py` — 新增 `list KEY` 子命令。
- **Modify** `agate/scripts/agate-capture-env-baseline.sh` — 8 处内联替换。
- **Test** `agate/tests/unit/agate-read-p5-commands.bats`（新建）— 专用解析器直接测试。
- **Test** `agate/tests/unit/agate-json-get.bats` — 新增 `list` 子命令测试。
- **Modify** `agate/tests/README.md` — 新增 `agate-read-p5-commands.py` 行。

---

### Task 1: TDD — 写 `agate-read-p5-commands.py` 直接失败测试（真红）

**Files:**
- Test: `agate/tests/unit/agate-read-p5-commands.bats`（新建）

**背景**：新解析器尚不存在。先写直接调用它的 bats 测试（真红），确立输出对象契约 + 无 P5 块输出空，再实现。

- [ ] **Step 1: 新建测试文件**

创建 `agate/tests/unit/agate-read-p5-commands.bats`：

```bash
#!/usr/bin/env bats
# tests/unit/agate-read-p5-commands.bats — P5 gate_commands 解析器单元测试
load ../helpers/load.bash

@test "P5C.1 P2 含 P5 + P5_formatter + P5_js → 输出对象含 commands" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/p5-XXXXXX")
    cat > "$dir/P2-design.md" <<'EOF'
---
agent: test
---
gate_commands:
  P5: pytest
  P5_formatter: pytest.sh
  P5_js: vitest run
  P5_js_formatter: vitest.sh
EOF
    run bash -c "P2_DESIGN='$dir/P2-design.md' python3 '$AGATE_SCRIPTS/agate-read-p5-commands.py'"
    [ "$status" -eq 0 ]
    [[ "$output" == *'"cmd": "pytest"'* ]]
    [[ "$output" == *'"formatter": "pytest.sh"'* ]]
    [[ "$output" == *'"cmd": "vitest run"'* ]]
    [[ "$output" == *'"commands"'* ]]
}

@test "P5C.2 P2 无 gate_commands.P5 → 输出空（供 bash -z 判定）" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/p5-XXXXXX")
    cat > "$dir/P2-design.md" <<'EOF'
---
agent: test
---
gate_commands: {}
EOF
    run bash -c "P2_DESIGN='$dir/P2-design.md' python3 '$AGATE_SCRIPTS/agate-read-p5-commands.py'"
    [ "$status" -eq 0 ]
    [ -z "$output" ]
}

@test "P5C.3 P2 无 gate_commands 块 → 输出空" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/p5-XXXXXX")
    cat > "$dir/P2-design.md" <<'EOF'
---
agent: test
---
无 gate_commands
EOF
    run bash -c "P2_DESIGN='$dir/P2-design.md' python3 '$AGATE_SCRIPTS/agate-read-p5-commands.py'"
    [ "$status" -eq 0 ]
    [ -z "$output" ]
}

@test "P5C.4 P5 键双引号值被去除 + suffix/formatter 关联" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/p5-XXXXXX")
    cat > "$dir/P2-design.md" <<'EOF'
---
agent: test
---
gate_commands:
  P5: "pytest -q"
  P5_html_formatter: vitest.sh
  P5_html: "npx vitest"
EOF
    run bash -c "P2_DESIGN='$dir/P2-design.md' python3 '$AGATE_SCRIPTS/agate-read-p5-commands.py'"
    [ "$status" -eq 0 ]
    [[ "$output" == *'"cmd": "pytest -q"'* ]]
    [[ "$output" == *'"cmd": "npx vitest"'* ]]
    [[ "$output" == *'"formatter": "vitest.sh"'* ]]
}
```

> **红/绿说明**：`agate-read-p5-commands.py` 尚不存在 → 每个用例 `python3 "$AGATE_SCRIPTS/agate-read-p5-commands.py"` 报「No such file」→ 全部 FAIL（红）。实现后 → 全 PASS（绿）。

- [ ] **Step 2: 运行测试确认当前失败（红）**

```bash
bats agate/tests/unit/agate-read-p5-commands.bats
```

Expected: 4 个 @test 全部 FAIL（`agate-read-p5-commands.py: No such file or directory`）。

---

### Task 2: TDD — 实现 `agate-read-p5-commands.py`（绿）

**Files:**
- Create: `agate/scripts/agate-read-p5-commands.py`

**背景**：把 capture-env-baseline.sh 第 25-47 行内联 P5 解析抽离。逻辑一行不改，仅输出从裸数组改为对象 `{"commands":[...]}`（复用共享工具 `len`/`index` 子命令），无 P5 块仍输出空。

- [ ] **Step 1: 创建 `.py`**

```python
#!/usr/bin/env python3
"""解析 P2-design.md 的 gate_commands.P5 块，输出 JSON 对象。

从 agate-capture-env-baseline.sh 内联 python 抽离（py 抽离批次 3）。
值传递走环境变量 P2_DESIGN（文件路径）。输出：
  {"commands":[{"cmd":...,"formatter":...,"suffix":...}]}
无 gate_commands.P5 块时输出空（供 bash [ -z "$P5_DATA" ] 判定跳过）。

注：无 `gate_commands:` 块时输出空；有块但仅 formatter 键（无 P5 命令键）时输出
{"commands": []}（非空）——均与内联 ORIG 行为一致。
"""

import json
import os
import re
import sys

content = open(os.environ["P2_DESIGN"]).read()
if not content.endswith(chr(10)):
    content += chr(10)
m = re.search(r"^gate_commands:[ \t]*\n((?:  .*\n|\s*\n)*)", content, re.MULTILINE)
if not m:
    sys.exit(0)
block = m.group(1)
entries = []
for line in re.findall(r"^  (P5\w*):\s*(.+)$", block, re.MULTILINE):
    key = line[0]
    val = line[1].strip().strip(chr(34)).strip(chr(39))
    if key.endswith("_formatter"):
        continue
    suffix = key[2:] if len(key) > 2 else ""
    fmt_key = "P5" + suffix + "_formatter"
    fmt_val = ""
    for line2 in re.findall(r"^  (" + re.escape(fmt_key) + r"):\s*(.+)$", block, re.MULTILINE):
        fmt_val = line2[1].strip().strip(chr(34)).strip(chr(39))
    entries.append({"cmd": val, "formatter": fmt_val, "suffix": suffix})
print(json.dumps({"commands": entries}))
```

> **等价性**：正则、`suffix`/`fmt_key` 逻辑、`strip` 与原内联逐字一致。仅差分：原 `print(json.dumps(entries))` → 新 `print(json.dumps({"commands": entries}))`（对象包装）。无 P5 块 `sys.exit(0)` 输出空（保持第 48 行语义）。

- [ ] **Step 2: 运行测试确认通过（绿）**

```bash
chmod +x agate/scripts/agate-read-p5-commands.py
bats agate/tests/unit/agate-read-p5-commands.bats
```

Expected: 4 个 @test 全 PASS。

---

### Task 3: TDD — 扩展 `agate-json-get.py` 加 `list` 子命令（真红→绿）

**Files:**
- Modify: `agate/scripts/agate-json-get.py`
- Test: `agate/tests/unit/agate-json-get.bats`

**背景**：capture-env-baseline.sh 第 91-96 行需要「逐行打印 failed_tests 数组每个元素」。为此给工具加 `list KEY` 子命令。先加失败测试再实现。

- [ ] **Step 1: 写失败测试**

在 `agate/tests/unit/agate-json-get.bats` 末尾追加：

```bash
@test "JGET.7 list 逐行打印数组每个元素" {
    run bash -c "echo '{\"failed_tests\":[\"a\",\"b\",\"c\"]}' | python3 '$AGATE_SCRIPTS/agate-json-get.py' list failed_tests"
    [ "$status" -eq 0 ]
    [[ "$output" == *"a"* ]]
    [[ "$output" == *"b"* ]]
    [[ "$output" == *"c"* ]]
    run bash -c "echo '{}' | python3 '$AGATE_SCRIPTS/agate-json-get.py' list missing"
    [ "$status" -eq 0 ]
    [ -z "$output" ]
}
```

> **红/绿说明**：工具当前无 `list` → 运行报 `unknown op list` + exit 2 → JGET.7 FAIL（红）。加 `list` 分支后 → PASS（绿）。

- [ ] **Step 2: 运行测试确认当前失败（红）**

```bash
bats agate/tests/unit/agate-json-get.bats --filter 'JGET.7'
```

Expected: FAIL（`agate-json-get: unknown op list`）。

- [ ] **Step 3: 实现 `list` 子命令**

在 `agate-json-get.py` 的 `elif op == "count_prefix":` 分支后追加：

```python
    elif op == "list":
        key = sys.argv[2]
        for e in data.get(key, []):
            print(e)
```

同步更新 `agate-json-get.py` 顶部 docstring 的用法说明，新增一行：

```
  list KEY              逐行打印 d.get(KEY, []) 每个元素（用于 failed_tests 迭代）
```

- [ ] **Step 4: 运行测试确认通过（绿）**

```bash
bats agate/tests/unit/agate-json-get.bats
```

Expected: 7 个 @test 全 PASS（JGET.1-7）。

---

### Task 4: 改造 `agate-capture-env-baseline.sh` 8 处内联（薄壳）

**Files:**
- Modify: `agate/scripts/agate-capture-env-baseline.sh`

**背景**：把 8 处内联替换为调用专用解析器 + 共享工具。`SCRIPT_DIR` 已有（第 15 行）。

- [ ] **Step 1: 替换 P5 解析器（第 25-47 行）**

原（第 25-47 行，多行 `python3 -c '...'`）：
```bash
P5_DATA=$(P2_DESIGN="$P2_FILE" python3 -c '
import re, sys, os, json
...（整段 P5 解析）...
print(json.dumps(entries))
')
```
新：
```bash
P5_DATA=$(P2_DESIGN="$P2_FILE" python3 "$SCRIPT_DIR/agate-read-p5-commands.py")
```

> **注意**：原第 48 行 `[ -z "$P5_DATA" ]` 判定「无 P5 → 跳过」依赖新解析器无 P5 块时**输出空**。新解析器已保证此语义（Task 2）。

- [ ] **Step 2: 替换第 64 行（顶层数组长度）**

原：
```bash
ENTRY_COUNT=$(echo "$P5_DATA" | python3 -c 'import sys,json; print(len(json.load(sys.stdin)))')
```
新（P5_DATA 现为 `{"commands":[...]}`，取 commands 长度）：
```bash
ENTRY_COUNT=$(echo "$P5_DATA" | python3 "$SCRIPT_DIR/agate-json-get.py" len commands)
```

> **等价性**：P5_DATA 从裸数组 `[...]` 变为对象 `{"commands":[...]}`，`len(json)` → `len(data["commands"])`。共享工具 `len` 用 `.get("commands",[])`，缺失返回 0，等价。

- [ ] **Step 3: 替换第 68-69 行（顶层数组索引）**

原：
```bash
cmd=$(echo "$P5_DATA" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d[$idx]['cmd'])")
fmt_val=$(echo "$P5_DATA" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d[$idx]['formatter'])")
```
新：
```bash
cmd=$(echo "$P5_DATA" | python3 "$SCRIPT_DIR/agate-json-get.py" index commands "$idx" cmd)
fmt_val=$(echo "$P5_DATA" | python3 "$SCRIPT_DIR/agate-json-get.py" index commands "$idx" formatter)
```

> **等价性**：`d[$idx]['cmd']` → `d["commands"][$idx]["cmd"]`。共享工具 `index` 用 `d[KEY][int(IDX)][SUBKEY]`，`$idx` 已加引号。

- [ ] **Step 4: 替换第 84、98-99 行（get）**

原：
```bash
JSON_EXIT_CODE=$(echo "$json_result" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("exit_code",0))')
```
新：
```bash
JSON_EXIT_CODE=$(echo "$json_result" | python3 "$SCRIPT_DIR/agate-json-get.py" get exit_code 0)
```

原：
```bash
JSON_FAILED=$(echo "$json_result" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("failed",0))')
JSON_ERRORS=$(echo "$json_result" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("errors",0))')
```
新：
```bash
JSON_FAILED=$(echo "$json_result" | python3 "$SCRIPT_DIR/agate-json-get.py" get failed 0)
JSON_ERRORS=$(echo "$json_result" | python3 "$SCRIPT_DIR/agate-json-get.py" get errors 0)
```

- [ ] **Step 5: 替换第 91-96 行（failed_tests 迭代）**

原（多行 `python3 -c '...'`）：
```bash
CMD_FAIL_LIST=$(echo "$json_result" | python3 -c '
import sys, json
d = json.load(sys.stdin)
for t in d.get("failed_tests", []):
    print(t)
')
```
新：
```bash
CMD_FAIL_LIST=$(echo "$json_result" | python3 "$SCRIPT_DIR/agate-json-get.py" list failed_tests)
```

- [ ] **Step 6: 验证 capture-env-baseline 全部测试仍绿**

```bash
bats agate/tests/unit/agate-capture-env-baseline.bats agate/tests/unit/agate-read-p5-commands.bats agate/tests/unit/agate-json-get.bats
```

Expected: 全部 PASS（15 EB + 4 P5C + 7 JGET = 26）。

---

### Task 5: 全量回归 + 一致性 + 用例数 + shellcheck

**Files:**（无改动，仅验证）

- [ ] **Step 1: 全量 bats**

```bash
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
```

Expected: 全部 PASS（干净汇总）。

- [ ] **Step 2: 一致性**

```bash
python3 agate/scripts/check-protocol-consistency.py
```

Expected: `0 ERROR`。（`agate-read-p5-commands.py` 不匹配锚点表 glob，无 ERROR。）

- [ ] **Step 3: 用例数**

```bash
bash agate/tests/scripts/count-tests.sh
```

Expected: 原 551 + 4（P5C.1-4）+ 1（JGET.7）= **556**。

- [ ] **Step 4: shellcheck**

```bash
shellcheck -S warning agate/scripts/*.sh
```

Expected: 无 error（薄壳无新增 shell 复杂度）。

---

### Task 6: 文档同步（README 逐脚本用例数）

**Files:**
- Modify: `agate/tests/README.md`

**背景**：新增 `agate-read-p5-commands.bats` 需在 README 逐脚本表登记。

- [ ] **Step 1: 定位 README 逐脚本表**

```bash
grep -n "agate-json-get.py\|check-p6-provenance\|ci-gate-backstop" agate/tests/README.md
```

- [ ] **Step 2: 新增 `agate-read-p5-commands.py` 行**

在 README 逐脚本表（`agate-json-get.py` 行附近）插入：
```
| agate-read-p5-commands.py | unit/agate-read-p5-commands.bats | 4 |
```

> **注意**：总数行是 `以 count-tests.sh 输出为准`（自动推导），不需改。`agate-json-get.py` 行由 6 改 7（新增 JGET.7）。

---

### Task 7: commit（self-gate）

**Files:**
- 提交：`agate/scripts/agate-read-p5-commands.py`、`agate/scripts/agate-json-get.py`、`agate/scripts/agate-capture-env-baseline.sh`、`agate/tests/unit/agate-read-p5-commands.bats`、`agate/tests/unit/agate-json-get.bats`、`agate/tests/README.md`

**背景**：触发文件含 `agate/scripts/*.py`、`agate/scripts/*.sh`、`agate/tests/*.bats` → commit-msg-self-gate hook 要求 `self-gate-review:`。

- [ ] **Step 1: 暂存并提交**

```bash
cd /home/kity/oclab/agate/.worktrees/py-extraction
git add agate/scripts/agate-read-p5-commands.py agate/scripts/agate-json-get.py agate/scripts/agate-capture-env-baseline.sh agate/tests/unit/agate-read-p5-commands.bats agate/tests/unit/agate-json-get.bats agate/tests/README.md
git commit -m "feat(scripts): agate-capture-env-baseline 8 处内联抽离 + 共享工具扩展

新增 agate/scripts/agate-read-p5-commands.py：解析 P2-design.md 的
gate_commands.P5 块，输出对象 {\"commands\":[...]}（无 P5 块输出空）。
扩展 agate/scripts/agate-json-get.py 新增 list 子命令（逐行打印数组元素）。
替换 agate-capture-env-baseline.sh 8 处内联 python（get/len/index/list）。
行为等价，既有 551 测试全绿。新增 P5C.1-4 + JGET.7，总数 551→556。

self-gate-review: docs/plans/agate-py-extraction-capture-baseline-20260807.md"
```

Expected: commit 成功，commit-msg hook 识别 `self-gate-review:` 无 WARNING。

- [ ] **Step 2: 确认工作区干净**

```bash
git status
```

Expected: clean（仅 HANDOFF-PY-EXTRACTION.md 未跟踪，属预期）。

---

## 批次结论记录（实施后填写）

- **工具复用**：`list` 子命令通用（failed_tests 迭代在许多脚本出现）。P5 解析器作为「多行长块独立 .py」模式又一实例。
- **遗留**：`agate-read-gate-commands.py`（P3）与 `agate-read-p5-commands.py`（P5）结构相近，未来可考虑合并为带 prefix 参数的单个解析器（需处理 P3 带 project_module、P5 不带且输出空的差异）——本批不合并，避免风险。
- **下游依赖**：capture-env-baseline.sh 现在依赖同目录两个 .py（agate-read-p5-commands.py + agate-json-get.py），复制部署时须一并复制。
- **验证**：bats 全绿（562 ok）、count-tests 556、consistency 0 ERROR、shellcheck 0 error、后置评审 APPROVE（8/8 处等价映射 + 无匹配路径语义确认）。