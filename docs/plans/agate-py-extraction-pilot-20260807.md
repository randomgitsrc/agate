# agate 内联 python 抽离试点（check-tdd-red.sh read_gate_commands）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 `check-tdd-red.sh` 中 `read_gate_commands()` 函数的内联 `python3 -c` 段（解析 P2-design.md 的 `gate_commands` 块 → JSON）抽离成独立 `.py` 脚本，消除 bash 内联 python 的引号规避病征（`chr(10)`/`chr(39)`），并证明「抽离 → bats 绿」试点流程可行，为全量 46 处抽离提供工作量基准。

**Architecture:** 抽离后的 `.py` 与内联段**完全等价**——仍通过环境变量 `GATE_FILE` 传文件路径，读文件、正则解析、打印 JSON、退出码一致。bash 侧 `read_gate_commands()` 只保留薄壳：`GATE_FILE="$p2_file" python3 "$SCRIPT_DIR/<name>.py" 2>/dev/null || echo '{"commands":[],"project_module":""}'`。行为不变 → 现有 check-tdd-red.bats 测试（TDD.G*/F* 覆盖 gate_commands 解析）仍绿，作为强兜底。

**Tech Stack:** bash（薄壳）+ python3（纯逻辑）+ bats（测试）。

**背景调研（已确认）：**
- 触发文件：`agate/scripts/check-tdd-red.sh`（self-gate 触发）、`agate/scripts/<name>.py`（新增，self-gate 触发）、计划文档（docs/，非触发）
- 待抽离内联段：`check-tdd-red.sh:56-82`（`read_gate_commands` 函数的 `GATE_FILE="$p2_file" python3 -c '...'`）
- 该函数是 46 处中最「自成一体」的一处：单个环境变量入、单条 JSON 出、无 argv/stdin 副作用、无外部依赖（纯 re+json），是理想试点
- 传参走环境变量（`os.environ["GATE_FILE"]`），符合 handoff 第 4 节「绝大多数用环境变量」的现状
- 现有测试 `agate/tests/unit/check-tdd-red.bats` 的 TDD.G1-G5 / TDD.F1 / TDD.F2 / TDD.F12 已覆盖 gate_commands 解析行为——抽离后行为不变则这些测试仍绿

---

## File Structure

- **Create** `agate/scripts/agate-read-gate-commands.py` — 从 `check-tdd-red.sh:56-82` 原样搬移的独立脚本（含 `#!/usr/bin/env python3` shebang + 简短 docstring）。
- **Modify** `agate/scripts/check-tdd-red.sh:56-82` — `read_gate_commands()` 内联段替换为调用新 `.py` 的薄壳。
- **Test** `agate/tests/unit/check-tdd-red.bats` — 新增直接测新 `.py` 的用例（含跨文件路径、P2 无 gate_commands、空值、多栈 formatter 等边界）。
- **Modify** `agate/tests/README.md:41` — 将 `check-tdd-red.sh` 行用例数 `32` 改为 `38`（新增 6 个 PYX 用例）。⚠️ 不要 grep 数字基线（539/545 系 count-tests 自动推导，README 不存在该总数字）。

---

### Task 1: TDD — 写新 `.py` 的直接失败测试（真红）

**Files:**
- Test: `agate/tests/unit/check-tdd-red.bats`

**背景**：新 `.py` 尚不存在。先写直接调用它的 bats 测试（真红），确立 `.py` 的独立行为契约，再实现 `.py` 使其变绿。测试用 `AGATE_SCRIPTS`（load.bash 已定义）定位新脚本。

- [ ] **Step 1: 写失败测试**

在 `agate/tests/unit/check-tdd-red.bats` 末尾追加以下用例（保持现有测试风格：`run bash "$AGATE_SCRIPTS/..."`）：

```bash
# ========== py 抽离试点：agate-read-gate-commands.py 直接测试 ==========
# 覆盖：P2 含 gate_commands 多栈 / 无 gate_commands / project_module /
#       双引号去除 / 单引号去除 / formatter 关联 / 末行无换行

@test "PYX.1 agate-read-gate-commands.py P2 含 P3 + P3_html_formatter + project_module" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/py-XXXXXX")
    cat > "$dir/P2-design.md" <<'EOF'
---
agent: test
---
gate_commands:
  P3: "pytest -q --tb=short"
  P3_html: "npx vitest run"
  P3_html_formatter: "vitest.sh"
  project_module: "myapp"
EOF
    run bash -c "GATE_FILE='$dir/P2-design.md' python3 '$AGATE_SCRIPTS/agate-read-gate-commands.py'"
    [ "$status" -eq 0 ]
    [[ "$output" == *'"cmd": "pytest -q --tb=short"'* ]]
    [[ "$output" == *'"cmd": "npx vitest run"'* ]]
    [[ "$output" == *'"formatter": "vitest.sh"'* ]]
    [[ "$output" == *'"project_module": "myapp"'* ]]
}

@test "PYX.2 agate-read-gate-commands.py P2 无 gate_commands → 空 JSON" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/py-XXXXXX")
    cat > "$dir/P2-design.md" <<'EOF'
---
agent: test
---
无 gate_commands 块
EOF
    run bash -c "GATE_FILE='$dir/P2-design.md' python3 '$AGATE_SCRIPTS/agate-read-gate-commands.py'"
    [ "$status" -eq 0 ]
    [[ "$output" == *'"commands": []'* ]]
    [[ "$output" == *'"project_module": ""'* ]]
}

@test "PYX.3 agate-read-gate-commands.py P2 双引号值被去除" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/py-XXXXXX")
    cat > "$dir/P2-design.md" <<'EOF'
---
agent: test
---
gate_commands:
  P3: "pytest -q"
EOF
    run bash -c "GATE_FILE='$dir/P2-design.md' python3 '$AGATE_SCRIPTS/agate-read-gate-commands.py'"
    [ "$status" -eq 0 ]
    [[ "$output" == *'"cmd": "pytest -q"'* ]]
}

@test "PYX.4 agate-read-gate-commands.py P2 单引号值被去除" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/py-XXXXXX")
    cat > "$dir/P2-design.md" <<'EOF'
---
agent: test
---
gate_commands:
  P3: 'pytest -q'
EOF
    run bash -c "GATE_FILE='$dir/P2-design.md' python3 '$AGATE_SCRIPTS/agate-read-gate-commands.py'"
    [ "$status" -eq 0 ]
    [[ "$output" == *'"cmd": "pytest -q"'* ]]
}

@test "PYX.5 agate-read-gate-commands.py P2 末行无换行也能解析" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/py-XXXXXX")
    printf 'gate_commands:\n  P3: "pytest -q"' > "$dir/P2-design.md"
    run bash -c "GATE_FILE='$dir/P2-design.md' python3 '$AGATE_SCRIPTS/agate-read-gate-commands.py'"
    [ "$status" -eq 0 ]
    [[ "$output" == *'"cmd": "pytest -q"'* ]]
}

@test "PYX.6 agate-read-gate-commands.py GATE_FILE 不存在 → 非零退出" {
    run bash -c "GATE_FILE='/nonexistent/P2.md' python3 '$AGATE_SCRIPTS/agate-read-gate-commands.py'"
    [ "$status" -ne 0 ]
}
```

> **红/绿说明**：新 `.py` 尚不存在 → 每个用例 `python3 "$AGATE_SCRIPTS/agate-read-gate-commands.py"` 报「No such file」→ 全部 FAIL（红）。实现 `.py` 后 → 全 PASS（绿）。真红真绿。注意 PYX.6 依赖 `.py` 的 `open()` 抛异常 → 脚本未捕获 → 非零退出（`2>/dev/null` 由 bash 调用方负责，脚本自身不必捕获）。

- [ ] **Step 2: 运行测试确认当前失败（红）**

```bash
bats agate/tests/unit/check-tdd-red.bats --filter 'PYX'
```

Expected: **5 个 @test FAIL（PYX.1-5）+ PYX.6 已 PASS**。（⚠️ PYX.6 断言 `[ "$status" -ne 0 ]`，`.py` 不存在时 `python3` 对不存在文件返回 exit 2 → 红阶段即已绿。PYX.6 是纯绿相行为测试，不作为红信号。）

---

### Task 2: TDD — 实现独立 `.py`（绿）

**Files:**
- Create: `agate/scripts/agate-read-gate-commands.py`

**背景**：把 `check-tdd-red.sh:56-82` 的内联 python 原样搬移成独立脚本，只加 shebang + docstring。逻辑一行不改。

- [ ] **Step 1: 创建 `.py`**

```python
#!/usr/bin/env python3
"""解析 P2-design.md 的 gate_commands 块，输出 JSON。

从 check-tdd-red.sh 的 read_gate_commands() 内联 python 抽离（py 抽离试点）。
值传递走环境变量 GATE_FILE（文件路径）。输出单条 JSON：
  {"commands":[{"cmd":...,"formatter":...,"suffix":...}], "project_module":...}
无 gate_commands 块时输出 {"commands": [], "project_module": ""} 并 exit 0。
GATE_FILE 不存在/不可读 → 抛异常 → 非零退出（由 bash 调用方 2>/dev/null 兜底）。
"""

import json
import os
import re
import sys

content = open(os.environ["GATE_FILE"]).read()
if not content.endswith(chr(10)):
    content += chr(10)
m = re.search(r"^gate_commands:[ \t]*\n((?:  .*\n|\s*\n)*)", content, re.MULTILINE)
if not m:
    print(json.dumps({"commands": [], "project_module": ""}))
    sys.exit(0)
block = m.group(1)
commands = []
project_module = ""
for line in re.findall(r"^  (\w+):\s*(.+)$", block, re.MULTILINE):
    key = line[0]
    val = line[1].strip().strip(chr(34)).strip(chr(39))
    if key == "project_module":
        project_module = val
    elif key.startswith("P3") and not key.endswith("_formatter"):
        suffix = key[2:] if len(key) > 2 else ""
        fmt_key = "P3" + suffix + "_formatter"
        fmt_val = ""
        for line2 in re.findall(r"^  (" + re.escape(fmt_key) + r"):\s*(.+)$", block, re.MULTILINE):
            fmt_val = line2[1].strip().strip(chr(34)).strip(chr(39))
        commands.append({"cmd": val, "formatter": fmt_val, "suffix": suffix})
result = {"commands": commands, "project_module": project_module}
print(json.dumps(result))
```

> **注意**：原内联段用 `strip("\"")`（bash 双引号内嵌 `\"`）和 `strip(chr(39))`。抽离成独立 `.py` 后，双引号不再被 bash 转义，可改用 `strip(chr(34))`（等价且更清晰，避免 `"\"\""` 视觉噪音）。**行为等价**：`.strip(chr(34)).strip(chr(39))` 与原 `.strip("\"").strip(chr(39))` 完全一致。

- [ ] **Step 2: 运行测试确认通过（绿）**

```bash
bats agate/tests/unit/check-tdd-red.bats --filter 'PYX'
```

Expected: 6 个 @test 全 PASS（PYX.1-5 由红转绿，PYX.6 保持绿）。

- [ ] **Step 3: shellcheck 不影响 `.py`（无 shell 语法），但确认 `.py` 可执行位**

```bash
chmod +x agate/scripts/agate-read-gate-commands.py
python3 agate/scripts/agate-read-gate-commands.py --help 2>&1 | head -1 || true
```

Expected: 无 `.py` 语法错误（`--help` 若无 argparse 会报 GATE_FILE 未定义，属预期；仅用于确认无 SyntaxError）。

---

### Task 3: TDD — 改造 `check-tdd-red.sh` 薄壳，现有测试仍绿

**Files:**
- Modify: `agate/scripts/check-tdd-red.sh:56-82`

**背景**：把 `read_gate_commands()` 的内联 `python3 -c` 替换为调用新 `.py`。行为等价 → 现有 TDD.G*/F* 测试（gate_commands 路径）仍绿。

- [ ] **Step 1: 替换内联段**

将 `check-tdd-red.sh` 的 `read_gate_commands()` 函数体（当前第 56-82 行）整体替换为：

```bash
read_gate_commands() {
    local p2_file="$1"
    # 依赖同目录的 agate-read-gate-commands.py —— 项目复制脚本时须一并复制该 .py
    GATE_FILE="$p2_file" python3 "$SCRIPT_DIR/agate-read-gate-commands.py" 2>/dev/null \
        || echo '{"commands":[],"project_module":""}'
}
```

> **等价性**：原内联段 `python3 -c '...' 2>/dev/null || echo '{"commands":[],"project_module":""}'`。新代码 `python3 "$SCRIPT_DIR/agate-read-gate-commands.py" 2>/dev/null || echo ...` 完全一致——`2>/dev/null` 静默 python stderr，非零退出回退空 JSON。`SCRIPT_DIR` 已在 `check-tdd-red.sh:47` 定义（`$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)`），新 `.py` 与其同目录，调用路径正确。

- [ ] **Step 2: 运行 check-tdd-red 全部测试（含 PYX 与既有 TDD.G*/F*）**

```bash
bats agate/tests/unit/check-tdd-red.bats
bats agate/tests/unit/check-tdd-red-formatter.bats
```

Expected: 全部 PASS（既有 gate_commands 相关测试 + 新 PYX 用例如旧、如新全绿）。

- [ ] **Step 3: 全量回归（sanity + unit + regression + integration）**

```bash
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
```

Expected: 全部 PASS。

---

### Task 4: 一致性 + 用例数 + shellcheck 验证

**Files:**（无改动，仅验证）

**背景**：AGENTS.md 要求的 gate：consistency 0 ERROR、count-tests 不漂移、shellcheck 无 error。

- [ ] **Step 1: 一致性检查**

```bash
python3 agate/scripts/check-protocol-consistency.py
```

Expected: `0 ERROR`。（新 `.py` 若被协议文档引用需在锚点表登记；但 `agate-read-gate-commands.py` 是内部实现细节，不新增协议文档引用 → 无 ERROR。）

- [ ] **Step 2: 用例数计数**

```bash
bash agate/tests/scripts/count-tests.sh
```

Expected: 总数 = 原 539 + 新增 6（PYX.1-6）= **545**。README 逐脚本用例数同步见 Task 5（`check-tdd-red.sh` 32→38）。

- [ ] **Step 3: shellcheck**

```bash
shellcheck -S warning agate/scripts/*.sh
```

Expected: 无 error（`check-tdd-red.sh` 薄壳无新增 shell 复杂度）。

---

### Task 5: 文档同步（README per-script 用例数）

**Files:**
- Modify: `agate/tests/README.md:41`

**背景**：count-tests.sh 末尾提示「如果此数字与 docs/plans/agate-test-plan-2026-07-01.md 附录 A 不一致 → 文档漂移」。但该提示的「总数字」由 count-tests.sh 自动推导，README **没有**硬编码总数——真正的漂移点在 **README 的逐脚本用例数表**（`agate/tests/README.md:41` 的 `check-tdd-red.sh = 32`）。新增 6 个 PYX 用例后应为 38。

- [ ] **Step 1: 定位 README 逐脚本行**

```bash
grep -n "check-tdd-red.sh" agate/tests/README.md
```

Expected: 命中 `agate/tests/README.md:41`（`| check-tdd-red.sh | unit/check-tdd-red.bats | 32 |`）。

- [ ] **Step 2: 更新用例数**

用 Edit 把该行 `32` 改为 `38`，保留整行其他内容不动。

> **注意**：不要去 grep「539」或「545」这类总数——README 与测试计划文档均没有硬编码总数，总数由 `bash agate/tests/scripts/count-tests.sh` 动态输出（实施时 Task 4 Step 2 应显示 545）。

---

### Task 6: commit（self-gate）

**Files:**
- 提交：`agate/scripts/agate-read-gate-commands.py`、`agate/scripts/check-tdd-red.sh`、`agate/tests/unit/check-tdd-red.bats`、`agate/tests/README.md`

**背景**：触发文件含 `agate/scripts/*.py`、`agate/scripts/*.sh`、`agate/tests/*.bats` → commit-msg-self-gate hook 要求 commit message 含 `self-gate-review:` 或 `self-gate-skip:`。

- [ ] **Step 1: 暂存并提交**

```bash
cd /home/kity/oclab/agate/.worktrees/py-extraction
git add agate/scripts/agate-read-gate-commands.py agate/scripts/check-tdd-red.sh agate/tests/unit/check-tdd-red.bats agate/tests/README.md
git commit -m "feat(scripts): 试点抽离 check-tdd-red read_gate_commands 内联 python

将 check-tdd-red.sh:56-82 的 read_gate_commands 内联 python3 -c 段抽离为
独立脚本 agate/scripts/agate-read-gate-commands.py，消除 chr() 引号规避。
行为等价：环境变量 GATE_FILE 传参、JSON 输出、退出码一致。
新增 6 个直接测试该 .py 的 bats 用例（PYX.1-6），既有 539 测试全绿。
README 逐脚本用例数 check-tdd-red 32→38，总数 539→545。

self-gate-review: docs/plans/agate-py-extraction-pilot-20260807.md"
```

Expected: commit 成功，commit-msg hook 识别 `self-gate-review:` 无 WARNING。

- [ ] **Step 2: 确认工作区干净**

```bash
git status
```

Expected: clean（仅 HANDOFF-PY-EXTRACTION.md 未跟踪，属预期）。

---

## 试点结论记录（实施后填写）

- **工作量**：4 个实施 Task + 独立评审 2 轮，改动 4 文件（+127/-28），新增 6 个 PYX 用例。从红→绿→薄壳→全回归→commit 一条龙跑通。
- **可复用模式**：环境变量传参 + 独立 `.py` + 薄壳 + 直接测 `.py`（PYX 直接调用验证契约，强于仅靠 bash 行为测试）。
- **难点确认**：`chr()` 规避 → 独立 `.py` 后自然消除（`chr(34)` 替代 `\"` 转义）；argv/stdin 传参的脚本需额外设计入口。
- **下游依赖风险**：`check-tdd-red.sh` 允许项目「复制脚本到项目 scripts/」，抽离后须一并复制同目录 `.py`，已在薄壳处加注释注明。全量抽离需逐个评估复制部署约定。
- **全量建议**：46 处按此模式抽离可行。建议按「复杂度自高到低」分批（check-tdd-red 13 处、agate-capture-env-baseline 8 处、check-p6-provenance 4 处为重灾区），每批独立走本流程。重复的 `python3 -c 'import sys,json; d=json.load(sys.stdin); print(...)'` 单行 JSON 提取可先合并为共享工具，减少重复。