# agate IPC 抽离批次 5：MD 字段提取共享工具 + 5 脚本专用 .py Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 创建共享工具 `agate/scripts/agate-md-field-get.py`（从 P1/P2 markdown 提取 risk_level/ui_affected/phases 字段）+ 5 个专用 `.py`（state-yaml 校验、changelog Unreleased、inject-card、vision blocker、evidence 一致性），完成 `check-p6-provenance.sh`(4)、`check-pruning.sh`(2)、`check-state-yaml.sh`(1)、`check-changelog.sh`(1)、`agate-inject-card.sh`(1) 共 **9 处**内联 python 抽离。

**Architecture:** （1）`agate-md-field-get.py` 从文件（env 传路径）正则提取字段：`risk_level FILE`（`risk_level:\s*(low|medium|high)`）、`ui_affected FILE`（`ui_affected:\s*(true|false)`）、`phases FILE`（`phases:\s*\[...\]` 或块式列表）。覆盖 check-p6-provenance:23/:156、check-pruning:14/:22 四处相同模式。（2）5 个专用 `.py` 复刻各自独立逻辑：`agate-state-yaml-check.py`（完整校验）、`agate-changelog-unreleased.py`、`agate-card-inject.py`、`agate-vision-blocker.py`、`agate-evidence-consistency.py`。行为等价 → 既有测试（check-p6-provenance 38、check-pruning 29、check-state-yaml 9、check-changelog 8、agate-inject-card 11）是强兜底。

**Tech Stack:** bash（薄壳）+ python3（共享工具 + 专用工具）+ bats（测试）。

**背景调研（已确认）：**
- 触发文件：`agate/scripts/agate-md-field-get.py`（新增）、5 个专用 .py（新增）、5 个 .sh（改）、bats（改）→ self-gate 触发
- **9 处内联分布与模式**：
  - `risk_level 字段提取`：check-p6-provenance:23、check-pruning:14 — 逐字相同
    ```python
    import re, os
    with open(os.environ['P1_F']) as f:
        text = f.read()
    m = re.search(r'risk_level:\s*(low|medium|high)', text)
    print(m.group(1) if m else '')
    ```
  - `ui_affected 字段提取`：check-p6-provenance:156、check-p6-evidence:59（check-p6-evidence 属批 6，本批只收 provenance:156）— 逐字相同
    ```python
    m = re.search(r'ui_affected:\s*(true|false)', text)
    print(m.group(1) if m else '')
    ```
  - `phases 字段提取`：check-pruning:22（`phases:\s*\[([^\]]+)\]` 或块式列表）
  - `state-yaml 完整校验`：check-state-yaml:14（大段，含 yaml 解析 + 必填字段 + 格式校验）
  - `changelog Unreleased 提取`：check-changelog:18（`##\s*\[Unreleased\](.*?)(?=##\s*\[|\Z)`）
  - `vision blocker`：check-p6-provenance:189（读 vision_analysis.summary.blocker_count）
  - `evidence 一致性`：check-p6-provenance:260（大段，glob json + bdd_results 比对）
  - `inject-card`：agate-inject-card:42（读 DC + CARD，替换占位符，写回 DC）
- **re.search 的 `\s*` vs 原文件名参数**：各内联段传 env 变量（`P1_F`、`P2_FILE`、`YAML_PATH`、`EVIDENCE_DIR`+`P6_FILE`、`CHANGELOG_FILE`、`DC_FILE`+`CARD_FILE`）。共享工具 `risk_level/ui_affected/phases` 统一用 `FILE` env。

---

## File Structure

- **Create** `agate/scripts/agate-md-field-get.py` — risk_level/ui_affected/phases 子命令。
- **Create** `agate/scripts/agate-state-yaml-check.py`、`agate-changelog-unreleased.py`、`agate-card-inject.py`、`agate-vision-blocker.py`、`agate-evidence-consistency.py`。
- **Modify** `agate/scripts/check-p6-provenance.sh`、`check-pruning.sh`、`check-state-yaml.sh`、`check-changelog.sh`、`agate-inject-card.sh` — 9 处替换。
- **Test** `agate/tests/unit/agate-md-field-get.bats`、`agate-state-yaml-check.bats`、`agate-changelog-unreleased.bats`、`agate-inject-card.bats`、`agate-vision-blocker.bats`、`agate-evidence-consistency.bats`（新建）。
- **Modify** `agate/tests/README.md`。

---

### Task 1: TDD — 写 `agate-md-field-get.py` 直接失败测试（真红）

**Files:**
- Test: `agate/tests/unit/agate-md-field-get.bats`（新建）

**背景**：新工具尚不存在。写直接测试确认 risk_level/ui_affected/phases 契约。

- [ ] **Step 1: 新建测试文件**

创建 `agate/tests/unit/agate-md-field-get.bats`：

```bash
#!/usr/bin/env bats
# tests/unit/agate-md-field-get.bats — MD 字段提取共享工具单元测试
load ../helpers/load.bash

@test "MDF.1 risk_level 提取 low/medium/high" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/md-XXXXXX")
    echo "risk_level: high" > "$dir/P1.md"
    run bash -c "FILE='$dir/P1.md' python3 '$AGATE_SCRIPTS/agate-md-field-get.py' risk_level"
    [ "$status" -eq 0 ]; [[ "$output" == "high" ]]
}

@test "MDF.2 risk_level 无匹配 → 空" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/md-XXXXXX")
    echo "no risk" > "$dir/P1.md"
    run bash -c "FILE='$dir/P1.md' python3 '$AGATE_SCRIPTS/agate-md-field-get.py' risk_level"
    [ "$status" -eq 0 ]; [ -z "$output" ]
}

@test "MDF.3 ui_affected 提取 true/false" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/md-XXXXXX")
    echo "ui_affected: true" > "$dir/P2.md"
    run bash -c "FILE='$dir/P2.md' python3 '$AGATE_SCRIPTS/agate-md-field-get.py' ui_affected"
    [ "$status" -eq 0 ]; [[ "$output" == "true" ]]
}

@test "MDF.4 ui_affected 无匹配 → 空" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/md-XXXXXX")
    echo "no ui" > "$dir/P2.md"
    run bash -c "FILE='$dir/P2.md' python3 '$AGATE_SCRIPTS/agate-md-field-get.py' ui_affected"
    [ "$status" -eq 0 ]; [ -z "$output" ]
}

@test "MDF.5 phases 行内列表 [a, b, c] → 空格连接" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/md-XXXXXX")
    echo "phases: [P0, P1, P2]" > "$dir/P1.md"
    run bash -c "FILE='$dir/P1.md' python3 '$AGATE_SCRIPTS/agate-md-field-get.py' phases"
    [ "$status" -eq 0 ]; [[ "$output" == "P0 P1 P2" ]]
}

@test "MDF.6 phases 块式列表 → 空格连接" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/md-XXXXXX")
    printf 'phases:\n  - P0\n  - P1\n' > "$dir/P1.md"
    run bash -c "FILE='$dir/P1.md' python3 '$AGATE_SCRIPTS/agate-md-field-get.py' phases"
    [ "$status" -eq 0 ]; [[ "$output" == "P0 P1" ]]
}
```

> **红/绿说明**：`agate-md-field-get.py` 尚不存在 → 全 FAIL（红）。实现后 → 全 PASS（绿）。

- [ ] **Step 2: 运行测试确认当前失败（红）**

```bash
bats agate/tests/unit/agate-md-field-get.bats
```

Expected: 6 个 @test 全部 FAIL。

---

### Task 2: TDD — 实现 `agate-md-field-get.py`（绿）

**Files:**
- Create: `agate/scripts/agate-md-field-get.py`

**背景**：实现 3 个子命令。统一用 `FILE` env 读文件。`phases` 需同时支持行内列表与块式列表（复刻 check-pruning:22 双分支）。

- [ ] **Step 1: 创建 `.py`**

```python
#!/usr/bin/env python3
"""从 P1/P2 markdown 提取字段（py 抽离共享工具）。

从 FILE 环境变量读文件路径，按子命令正则提取。FILE 不存在/不可读时
抛异常→非零退出（由 bash 调用方 2>/dev/null || echo 兜底）。

用法：
  risk_level   提取 risk_level:\s*(low|medium|high)，无匹配输出空
  ui_affected  提取 ui_affected:\s*(true|false)，无匹配输出空
  phases       提取 phases:\s*[...]（行内）或块式列表（- Pn），空格连接
"""

import os
import re
import sys


def _read():
    with open(os.environ["FILE"]) as f:
        return f.read()


def main():
    op = sys.argv[1]
    text = _read()
    if op == "risk_level":
        m = re.search(r"risk_level:\s*(low|medium|high)", text)
        print(m.group(1) if m else "")
    elif op == "ui_affected":
        m = re.search(r"ui_affected:\s*(true|false)", text)
        print(m.group(1) if m else "")
    elif op == "phases":
        m = re.search(r"phases:\s*\[([^\]]+)\]", text)
        if m:
            phases = [p.strip() for p in m.group(1).split(",")]
            print(" ".join(phases))
        else:
            m = re.search(r"phases:\s*\n((?:[ \t]+-[ \t]+\S+[ \t]*\n)+)", text)
            if m:
                phases = re.findall(r"-\s+(\S+)", m.group(1))
                print(" ".join(phases))
    else:
        sys.stderr.write("agate-md-field-get: unknown op {}\n".format(op))
        sys.exit(2)


if __name__ == "__main__":
    main()
```

> **等价性**：三个子命令逐字复刻 check-p6-provenance:23/:156、check-pruning:14/:22 内联逻辑。`phases` 双分支（行内 `\[([^\]]+)\]` split 逗号，块式 `- Pn` findall）与原一致。

- [ ] **Step 2: 运行测试确认通过（绿）**

```bash
chmod +x agate/scripts/agate-md-field-get.py
bats agate/tests/unit/agate-md-field-get.bats
```

Expected: 6 个 @test 全 PASS。

---

### Task 3: TDD — 写 5 个专用 .py 的直接失败测试（真红）

**Files:**
- Test: `agate/tests/unit/agate-state-yaml-check.bats`、`agate-changelog-unreleased.bats`、`agate-inject-card.bats`、`agate-vision-blocker.bats`、`agate-evidence-consistency.bats`（均新建）

**背景**：5 个专用工具尚不存在。各写直接测试确立契约。

- [ ] **Step 1: 新建 `agate-state-yaml-check.bats`**

```bash
#!/usr/bin/env bats
# tests/unit/agate-state-yaml-check.bats — state-yaml 校验专用工具
load ../helpers/load.bash

@test "SY.1 合法 .state.yaml → 无输出" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/sy-XXXXXX")
    cat > "$dir/.state.yaml" <<'EOF'
task_id: T001
phase: P3
status: active
retries: {}
EOF
    run bash -c "STATE_FILE='$dir/.state.yaml' python3 '$AGATE_SCRIPTS/agate-state-yaml-check.py'"
    [ "$status" -eq 0 ]; [ -z "$output" ]
}

@test "SY.2 缺必填字段 → 缺必填字段: xxx" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/sy-XXXXXX")
    echo "task_id: T1" > "$dir/.state.yaml"
    run bash -c "STATE_FILE='$dir/.state.yaml' python3 '$AGATE_SCRIPTS/agate-state-yaml-check.py'"
    [ "$status" -eq 0 ]; [[ "$output" == *"缺必填字段"* ]]
}

@test "SY.3 phase 非法值 → phase 非法值" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/sy-XXXXXX")
    cat > "$dir/.state.yaml" <<'EOF'
task_id: T001
phase: ZZZ
status: active
EOF
    run bash -c "STATE_FILE='$dir/.state.yaml' python3 '$AGATE_SCRIPTS/agate-state-yaml-check.py'"
    [ "$status" -eq 0 ]; [[ "$output" == *"phase 非法值"* ]]
}
```

- [ ] **Step 2: 新建 `agate-changelog-unreleased.bats`**

```bash
#!/usr/bin/env bats
# tests/unit/agate-changelog-unreleased.bats — Changelog Unreleased 提取
load ../helpers/load.bash

@test "CL.1 提取 Unreleased 区域内容" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/cl-XXXXXX")
    cat > "$dir/CHANGELOG.md" <<'EOF'
## [Unreleased]
### Added
- T001 fix

## [v0.33.0]
- old
EOF
    run bash -c "CHANGELOG_FILE='$dir/CHANGELOG.md' python3 '$AGATE_SCRIPTS/agate-changelog-unreleased.py'"
    [ "$status" -eq 0 ]; [[ "$output" == *"T001 fix"* ]]
}

@test "CL.2 无 Unreleased → 空" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/cl-XXXXXX")
    echo "## [v0.33.0]" > "$dir/CHANGELOG.md"
    run bash -c "CHANGELOG_FILE='$dir/CHANGELOG.md' python3 '$AGATE_SCRIPTS/agate-changelog-unreleased.py'"
    [ "$status" -eq 0 ]; [ -z "$output" ]
}
```

- [ ] **Step 3: 新建 `agate-inject-card.bats`**

```bash
#!/usr/bin/env bats
# tests/unit/agate-inject-card.bats — 卡片注入专用工具
load ../helpers/load.bash

@test "IC.1 注入卡片到占位符之间" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/ic-XXXXXX")
    printf 'pre\n<!-- AGATE_CARD_START -->\nold\n<!-- AGATE_CARD_END -->\npost\n' > "$dir/dc.md"
    echo "newcard" > "$dir/card.md"
    run bash -c "DC_FILE='$dir/dc.md' CARD_FILE='$dir/card.md' python3 '$AGATE_SCRIPTS/agate-card-inject.py'"
    [ "$status" -eq 0 ]
    run cat "$dir/dc.md"
    [[ "$output" == *"newcard"* ]]
    [[ "$output" != *"old"* ]]
}

@test "IC.2 无占位符 → 非零退出" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/ic-XXXXXX")
    echo "no placeholder" > "$dir/dc.md"
    echo "card" > "$dir/card.md"
    run bash -c "DC_FILE='$dir/dc.md' CARD_FILE='$dir/card.md' python3 '$AGATE_SCRIPTS/agate-card-inject.py'"
    [ "$status" -ne 0 ]
}
```

- [ ] **Step 4: 新建 `agate-vision-blocker.bats`**

```bash
#!/usr/bin/env bats
# tests/unit/agate-vision-blocker.bats — vision YAML blocker_count 读取
load ../helpers/load.bash

@test "VB.1 读 vision_analysis.summary.blocker_count" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/vb-XXXXXX")
    cat > "$dir/vision.yaml" <<'EOF'
vision_analysis:
  summary:
    blocker_count: 2
EOF
    run bash -c "YAML_PATH='$dir/vision.yaml' python3 '$AGATE_SCRIPTS/agate-vision-blocker.py'"
    [ "$status" -eq 0 ]; [[ "$output" == "2" ]]
}

@test "VB.2 无 blocker_count → -1" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/vb-XXXXXX")
    echo "vision_analysis: {}" > "$dir/vision.yaml"
    run bash -c "YAML_PATH='$dir/vision.yaml' python3 '$AGATE_SCRIPTS/agate-vision-blocker.py'"
    [ "$status" -eq 0 ]; [[ "$output" == "-1" ]]
}
```

- [ ] **Step 5: 新建 `agate-evidence-consistency.bats`**

```bash
#!/usr/bin/env bats
# tests/unit/agate-evidence-consistency.bats — evidence JSON 与 P6 一致性
load ../helpers/load.bash

@test "EC.1 PASS 但 evidence 标 FAIL → 输出不一致" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/ec-XXXXXX")
    mkdir -p "$dir/P6-evidence"
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1 (result.json)
EOF
    cat > "$dir/P6-evidence/result.json" <<'EOF'
{"bdd_results": [{"id": "BDD-1", "status": "fail"}]}
EOF
    run bash -c "EVIDENCE_DIR='$dir/P6-evidence' P6_FILE='$dir/P6-acceptance.md' python3 '$AGATE_SCRIPTS/agate-evidence-consistency.py'"
    [ "$status" -eq 0 ]; [[ "$output" == *"BDD-1"* ]]
}

@test "EC.2 无不一致 → 空" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/ec-XXXXXX")
    mkdir -p "$dir/P6-evidence"
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1 (result.json)
EOF
    cat > "$dir/P6-evidence/result.json" <<'EOF'
{"bdd_results": [{"id": "BDD-1", "status": "pass"}]}
EOF
    run bash -c "EVIDENCE_DIR='$dir/P6-evidence' P6_FILE='$dir/P6-acceptance.md' python3 '$AGATE_SCRIPTS/agate-evidence-consistency.py'"
    [ "$status" -eq 0 ]; [ -z "$output" ]
}
```

> **红/绿说明**：5 个工具均不存在 → 各用例全 FAIL（红）。实现后 → 全 PASS（绿）。

- [ ] **Step 6: 运行 5 个测试文件确认当前失败（红）**

```bash
bats agate/tests/unit/agate-state-yaml-check.bats agate/tests/unit/agate-changelog-unreleased.bats agate/tests/unit/agate-inject-card.bats agate/tests/unit/agate-vision-blocker.bats agate/tests/unit/agate-evidence-consistency.bats
```

Expected: 全部 FAIL（工具不存在）。

---

### Task 4: TDD — 实现 5 个专用 .py（绿）

**Files:**
- Create: `agate/scripts/agate-state-yaml-check.py`、`agate-changelog-unreleased.py`、`agate-card-inject.py`、`agate-vision-blocker.py`、`agate-evidence-consistency.py`

**背景**：逐个复刻内联逻辑。

- [ ] **Step 1: 创建 `agate-state-yaml-check.py`**

```python
#!/usr/bin/env python3
"""校验 .state.yaml 格式（py 抽离批次 5）。

从 STATE_FILE env 读文件。输出错误行（每行一个），无错误输出空。
"""

import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.stderr.write("agate-state-yaml-check: 需要 pyyaml\n")
    sys.exit(1)

valid_phases = "P0 P1 P2 P3 P4 P5 P6 P7 P8 PAUSED READY DONE".split()

state_file = os.environ["STATE_FILE"]
try:
    with open(state_file) as f:
        data = yaml.safe_load(f)
except yaml.YAMLError as e:
    print("YAML 解析错误: {}".format(e))
    sys.exit(0)

errors = []

if data is None:
    errors.append("文件为空")
    print("\n".join(errors))
    sys.exit(0)

for field in ("task_id", "phase", "status"):
    if field not in data:
        errors.append("缺必填字段: {}".format(field))

task_id = data.get("task_id", "")
if task_id and not re.match(r"^T\d+$", str(task_id)):
    errors.append("task_id 格式错误: {}（应为 T + 数字，如 T001）".format(task_id))

phase = str(data.get("phase", ""))
if phase and phase not in valid_phases:
    errors.append("phase 非法值: {}（合法值: {}）".format(phase, " ".join(valid_phases)))

retries = data.get("retries", {})
if retries:
    if not isinstance(retries, dict):
        errors.append("retries 应为 dict，实际为 {}".format(type(retries).__name__))
    else:
        for key, val in retries.items():
            if not re.match(r"^P\d+$", str(key)):
                errors.append("retries key 格式错误: {}（应为大写 P + 数字，如 P2）".format(key))
            if not isinstance(val, list):
                errors.append("retries[{}] 应为列表，实际为 {}".format(key, type(val).__name__))

if errors:
    print("\n".join(errors))
```

> **注意**：原内联 `re.match(r'^T\d+\$')` 里 `\$` 是 bash 转义，独立 .py 应写 `^T\d+$`。`f'...{\" \".join(valid_phases)}'` 的 `\"` 转义在独立 .py 中无需（用 `{}`.format 或 f-string 正常引号）。

- [ ] **Step 2: 创建 `agate-changelog-unreleased.py`**

```python
#!/usr/bin/env python3
"""从 CHANGELOG_FILE 提取 [Unreleased] 区域内容（py 抽离批次 5）。"""

import os
import re
import sys

with open(os.environ["CHANGELOG_FILE"]) as f:
    text = f.read()
m = re.search(r"##\s*\[Unreleased\](.*?)(?=##\s*\[|\Z)", text, re.S)
if m:
    print(m.group(1))
```

- [ ] **Step 3: 创建 `agate-card-inject.py`**

```python
#!/usr/bin/env python3
"""把卡片内容注入 dispatch-context 的 AGATE_CARD 占位符之间（py 抽离批次 5）。

从 DC_FILE / CARD_FILE env 读路径。替换后写回 DC_FILE。
无占位符 → stderr 提示 + exit 1（由 bash 调用方处理）。
"""

import os
import re
import sys

dc = os.environ["DC_FILE"]
with open(dc) as f:
    text = f.read()
with open(os.environ["CARD_FILE"]) as f:
    card = f.read()
pattern = r"(<!-- AGATE_CARD_START -->\n)(.*?)(<!-- AGATE_CARD_END -->)"
if not re.search(pattern, text, flags=re.DOTALL):
    sys.stderr.write("AGATE_CARD 注入失败: {} 中未找到 AGATE_CARD_START/END 占位符\n".format(os.path.basename(dc)))
    sys.exit(1)


def _repl(m):
    return m.group(1) + card.rstrip("\n") + "\n" + m.group(3)


new_text = re.sub(pattern, _repl, text, flags=re.DOTALL)
with open(dc, "w") as f:
    f.write(new_text)
```

- [ ] **Step 4: 创建 `agate-vision-blocker.py`**

```python
#!/usr/bin/env python3
"""读 vision_analysis.summary.blocker_count（py 抽离批次 5）。

从 YAML_PATH env 读文件。无 blocker_count 或解析失败输出 -1。
"""

import os
import sys

try:
    import yaml
except ImportError:
    sys.stderr.write("agate-vision-blocker: 需要 pyyaml\n")
    sys.exit(1)

try:
    with open(os.environ["YAML_PATH"]) as f:
        data = yaml.safe_load(f)
    va = data.get("vision_analysis", {}) if data else {}
    summary = va.get("summary", {})
    print(summary.get("blocker_count", -1))
except Exception:
    print(-1)
```

- [ ] **Step 5: 创建 `agate-evidence-consistency.py`**

```python
#!/usr/bin/env python3
"""检查 evidence JSON 与 P6-acceptance.md 的 PASS/FAIL 一致性（py 抽离批次 5）。

从 EVIDENCE_DIR / P6_FILE env 读。P6 标 PASS 但 evidence JSON 显示 FAIL 的 BDD，
逐行输出 "BDD-x: P6 标 PASS 但 evidence JSON 显示 FAIL"。
"""

import glob
import json
import os
import re
import sys

evidence_dir = os.environ["EVIDENCE_DIR"]
p6_file = os.environ["P6_FILE"]

if not os.path.isfile(p6_file):
    sys.exit(0)

pass_bdds = set()
with open(p6_file) as f:
    for line in f:
        m = re.match(r"^\s*-\s*PASS\s+(BDD-\d+)", line, re.IGNORECASE)
        if m:
            pass_bdds.add(m.group(1))

fail_in_evidence = set()
for json_path in glob.glob(os.path.join(evidence_dir, "**/*.json"), recursive=True):
    try:
        with open(json_path) as f:
            data = json.load(f)
        if not isinstance(data, dict):
            continue
        results = data.get("bdd_results", data.get("results", []))
        if isinstance(results, list):
            for r in results:
                if isinstance(r, dict):
                    bdd_id = r.get("id", r.get("bdd", ""))
                    status = r.get("status", "").lower()
                    if status == "fail" and bdd_id:
                        fail_in_evidence.add(bdd_id)
    except Exception:
        continue

inconsistent = pass_bdds & fail_in_evidence
for bdd in sorted(inconsistent):
    print("{}: P6 标 PASS 但 evidence JSON 显示 FAIL".format(bdd))
```

- [ ] **Step 6: 运行 5 个测试文件确认通过（绿）**

```bash
chmod +x agate/scripts/agate-state-yaml-check.py agate/scripts/agate-changelog-unreleased.py agate/scripts/agate-card-inject.py agate/scripts/agate-vision-blocker.py agate/scripts/agate-evidence-consistency.py
bats agate/tests/unit/agate-state-yaml-check.bats agate/tests/unit/agate-changelog-unreleased.bats agate/tests/unit/agate-inject-card.bats agate/tests/unit/agate-vision-blocker.bats agate/tests/unit/agate-evidence-consistency.bats agate/tests/unit/agate-md-field-get.bats
```

Expected: 全部 PASS。

---

### Task 5: 改造 5 个脚本 9 处内联（薄壳）

**Files:**
- Modify: `agate/scripts/check-p6-provenance.sh`、`check-pruning.sh`、`check-state-yaml.sh`、`check-changelog.sh`、`agate-inject-card.sh`

**背景**：逐处替换。**已核实**：check-p6-provenance / check-pruning / check-state-yaml / check-changelog 四个脚本**既无 `SCRIPT_DIR` 也无 `AGATE_ROOT`**；agate-inject-card.sh 有 `AGATE_ROOT`（第 10 行）但无 `SCRIPT_DIR`。因此替换前必须先保证脚本目录变量可用，否则 `python3 "$SCRIPT_DIR/..."` 展开成 `/...` 报错被 `2>/dev/null || echo` 静默吞掉，gate 结果被污染。

- [ ] **Step 0: 为缺脚本目录变量的脚本补定义（前置）**

在以下四个脚本顶部（`set -euo pipefail` 之后、其他逻辑之前）加一行（与批次 4 一致）：
```bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
```
补到：
- `agate/scripts/check-p6-provenance.sh`
- `agate/scripts/check-pruning.sh`
- `agate/scripts/check-state-yaml.sh`
- `agate/scripts/check-changelog.sh`

`agate-inject-card.sh` **不加** SCRIPT_DIR——它已有 `AGATE_ROOT`，Step 5 用 `$AGATE_ROOT/scripts/`（与它现有 `$AGATE_ROOT/scripts/agate-next-card.sh` 用法一致）。

- [ ] **Step 1: check-p6-provenance.sh 四处**

原（:23 risk_level）：
```bash
    P1_F="$P1_FILE" python3 -c "
import re, os
with open(os.environ['P1_F']) as f:
    text = f.read()
m = re.search(r'risk_level:\s*(low|medium|high)', text)
print(m.group(1) if m else '')
" 2>/dev/null || echo ""
```
新：
```bash
    P1_F="$P1_FILE" python3 "$SCRIPT_DIR/agate-md-field-get.py" risk_level 2>/dev/null || echo ""
```
> **注意**：共享工具用 `FILE` env，但原内联用 `P1_F`。**需在 bash 调用处把 `P1_F="$P1_FILE"` 改为 `FILE="$P1_FILE"`**（或工具读 `P1_F`）。为最小改动，工具统一读 `FILE`，bash 传 `FILE="$P1_FILE"`。**修正**：
```bash
    FILE="$P1_FILE" python3 "$SCRIPT_DIR/agate-md-field-get.py" risk_level 2>/dev/null || echo ""
```

原（:156 ui_affected）：
```bash
        UI_AFFECTED=$(P2_FILE="$P2_FILE" python3 -c "
import re, os
with open(os.environ['P2_FILE']) as f:
    text = f.read()
m = re.search(r'ui_affected:\s*(true|false)', text)
print(m.group(1) if m else '')
" 2>/dev/null || echo "")
```
新：
```bash
        UI_AFFECTED=$(FILE="$P2_FILE" python3 "$SCRIPT_DIR/agate-md-field-get.py" ui_affected 2>/dev/null || echo "")
```

原（:189 vision blocker）：
```bash
            BLOCKER_COUNT=$(YAML_PATH="$YAML_PATH" python3 -c "
import yaml, os
try:
    with open(os.environ['YAML_PATH']) as f:
        data = yaml.safe_load(f)
    va = data.get('vision_analysis', {}) if data else {}
    summary = va.get('summary', {})
    print(summary.get('blocker_count', -1))
except Exception:
    print(-1)
" 2>/dev/null || echo -1)
```
新：
```bash
            BLOCKER_COUNT=$(YAML_PATH="$YAML_PATH" python3 "$SCRIPT_DIR/agate-vision-blocker.py" 2>/dev/null || echo -1)
```

原（:260 evidence 一致性）：
```bash
    INCONSISTENCY=$(EVIDENCE_DIR="$EVIDENCE_DIR" P6_FILE="$TASK_DIR/P6-acceptance.md" python3 -c '
import json, os, glob, re, sys
...（整段）...
print(f"{bdd}: P6 标 PASS 但 evidence JSON 显示 FAIL")
' 2>/dev/null || echo "")
```
新：
```bash
    INCONSISTENCY=$(EVIDENCE_DIR="$EVIDENCE_DIR" P6_FILE="$TASK_DIR/P6-acceptance.md" python3 "$SCRIPT_DIR/agate-evidence-consistency.py" 2>/dev/null || echo "")
```

- [ ] **Step 2: check-pruning.sh 两处**

原（:14 risk_level）：同 provenance:23 → 新：
```bash
RISK_LEVEL=$(FILE="$P1_FILE" python3 "$SCRIPT_DIR/agate-md-field-get.py" risk_level 2>/dev/null || echo "")
```

原（:22 phases）：→ 新：
```bash
PHASES_DECLARED=$(FILE="$P1_FILE" python3 "$SCRIPT_DIR/agate-md-field-get.py" phases 2>/dev/null || echo "")
```

- [ ] **Step 3: check-state-yaml.sh 一处**

原（:14 完整校验）：
```bash
ERRORS=$(STATE_FILE="$STATE_FILE" python3 -c "
import yaml, sys, re, os
...（整段）...
print('\n'.join(errors))
" 2>/dev/null || true)
```
新：
```bash
ERRORS=$(STATE_FILE="$STATE_FILE" python3 "$SCRIPT_DIR/agate-state-yaml-check.py" 2>/dev/null || true)
```

- [ ] **Step 4: check-changelog.sh 一处**

原（:18）：
```bash
UNRELEASED_CONTENT=$(CHANGELOG_FILE="$CHANGELOG_FILE" python3 -c "
import re, os
with open(os.environ['CHANGELOG_FILE']) as f:
    text = f.read()
m = re.search(r'##\s*\[Unreleased\](.*?)(?=##\s*\[|\Z)', text, re.S)
if m:
    print(m.group(1))
" 2>/dev/null || echo "")
```
新：
```bash
UNRELEASED_CONTENT=$(CHANGELOG_FILE="$CHANGELOG_FILE" python3 "$SCRIPT_DIR/agate-changelog-unreleased.py" 2>/dev/null || echo "")
```

- [ ] **Step 5: agate-inject-card.sh 一处**

原（:42）：
```bash
    DC_FILE="$DC_FILE" CARD_FILE="$CARD_FILE" python3 -c "
import os, re, sys
...（整段）...
"
```
新（用 `$AGATE_ROOT/scripts/`，git-inject-card 已定义 AGATE_ROOT 无 SCRIPT_DIR）：
```bash
    DC_FILE="$DC_FILE" CARD_FILE="$CARD_FILE" python3 "$AGATE_ROOT/scripts/agate-card-inject.py"
    rm -f "$CARD_FILE"
```
> **注意**：原第 58 行 `rm -f "$CARD_FILE"`（清理 mktemp 卡片文件）在 python 之后，**必须保留**，否则每轮泄漏临时文件。Step 0 已声明 agate-inject-card 用 `$AGATE_ROOT/scripts/`（勿用未定义的 `$SCRIPT_DIR`）。

- [ ] **Step 6: 验证 5 个脚本相关测试仍绿**

```bash
bats agate/tests/unit/check-p6-provenance.bats agate/tests/unit/check-pruning.bats agate/tests/unit/check-state-yaml.bats agate/tests/unit/check-changelog.bats agate/tests/unit/agate-inject-card.bats agate/tests/unit/agate-md-field-get.bats agate/tests/unit/agate-state-yaml-check.bats agate/tests/unit/agate-changelog-unreleased.bats agate/tests/unit/agate-inject-card.bats agate/tests/unit/agate-vision-blocker.bats agate/tests/unit/agate-evidence-consistency.bats
```

Expected: 全部 PASS。

---

### Task 6: 全量回归 + 一致性 + 用例数 + shellcheck

**Files:**（无改动，仅验证）

- [ ] **Step 0: 验证脚本目录变量已就绪**

```bash
rg -n "SCRIPT_DIR=|AGATE_ROOT=" agate/scripts/check-p6-provenance.sh agate/scripts/check-pruning.sh agate/scripts/check-state-yaml.sh agate/scripts/check-changelog.sh agate/scripts/agate-inject-card.sh
```
Expected: 前四个各有 `SCRIPT_DIR=`；agate-inject-card.sh 有 `AGATE_ROOT=`（Step 0 前置已补）。若缺，回到 Task 5 Step 0 补加。前四个脚本的替换用 `$SCRIPT_DIR`，agate-inject-card.sh 用 `$AGATE_ROOT/scripts/`。

- [ ] **Step 1: 全量 bats**

```bash
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
```

Expected: 全部 PASS（干净汇总）。

- [ ] **Step 2: 一致性**

```bash
python3 agate/scripts/check-protocol-consistency.py
```

Expected: `0 ERROR`。

- [ ] **Step 3: 用例数**

```bash
bash agate/tests/scripts/count-tests.sh
```

Expected: 原 566 + 6（MDF.1-6）+ 3（SY.1-3）+ 2（CL.1-2）+ 2（IC.1-2）+ 2（VB.1-2）+ 2（EC.1-2）= **583**。

- [ ] **Step 4: shellcheck**

```bash
shellcheck -S warning agate/scripts/*.sh
```

Expected: 无 error。

- [ ] **Step 5: AST 校验（6 个新 .py）**

```bash
for f in agate-md-field-get agate-state-yaml-check agate-changelog-unreleased agate-inject-card agate-vision-blocker agate-evidence-consistency; do python3 -c "import ast; ast.parse(open('agate/scripts/$f.py').read())"; done
```

Expected: 无输出（语法有效）。

---

### Task 7: 文档同步（README 逐脚本用例数）

**Files:**
- Modify: `agate/tests/README.md`

**背景**：新增 6 个 .bats 文件需登记。

- [ ] **Step 1: 定位 README 逐脚本表 + 插入 6 行**

在 `agate-retreat-state.py` 行附近插入：
```
| agate-md-field-get.py | unit/agate-md-field-get.bats | 6 |
| agate-state-yaml-check.py | unit/agate-state-yaml-check.bats | 3 |
| agate-changelog-unreleased.py | unit/agate-changelog-unreleased.bats | 2 |
| agate-card-inject.py | unit/agate-card-inject.bats | 2 |
| agate-vision-blocker.py | unit/agate-vision-blocker.bats | 2 |
| agate-evidence-consistency.py | unit/agate-evidence-consistency.bats | 2 |
```
> **注意**：总数行是 `以 count-tests.sh 输出为准`，不需改。

---

### Task 8: commit（self-gate）

**Files:**
- 提交：6 个新 .py、6 个新 .bats、5 个 .sh、README

**背景**：触发文件含 `agate/scripts/*.py`、`agate/scripts/*.sh`、`agate/tests/*.bats` → commit-msg-self-gate hook 要求 `self-gate-review:`。

- [ ] **Step 1: 暂存并提交**

```bash
cd /home/kity/oclab/agate/.worktrees/py-extraction
git add agate/scripts/agate-md-field-get.py agate/scripts/agate-state-yaml-check.py agate/scripts/agate-changelog-unreleased.py agate/scripts/agate-card-inject.py agate/scripts/agate-vision-blocker.py agate/scripts/agate-evidence-consistency.py agate/scripts/check-p6-provenance.sh agate/scripts/check-pruning.sh agate/scripts/check-state-yaml.sh agate/scripts/check-changelog.sh agate/scripts/agate-inject-card.sh agate/tests/unit/agate-md-field-get.bats agate/tests/unit/agate-state-yaml-check.bats agate/tests/unit/agate-changelog-unreleased.bats agate/tests/unit/agate-card-inject.bats agate/tests/unit/agate-vision-blocker.bats agate/tests/unit/agate-evidence-consistency.bats agate/tests/README.md
git commit -m "feat(scripts): MD 字段提取共享工具 + 5 脚本专用 .py，9 处内联抽离

新增 agate-md-field-get.py（risk_level/ui_affected/phases）+ 5 个专用 .py
（state-yaml-check / changelog-unreleased / inject-card / vision-blocker /
evidence-consistency）。替换 check-p6-provenance(4) check-pruning(2)
check-state-yaml(1) check-changelog(1) agate-inject-card(1) 共 9 处内联。
行为等价，既有 566 测试全绿。新增 MDF.1-6 SY.1-3 CL.1-2 IC.1-2 VB.1-2 EC.1-2，
总数 566→583。

self-gate-review: docs/plans/agate-py-extraction-md-field-20260807.md"
```

Expected: commit 成功，hook 识别 `self-gate-review:` 无 WARNING。

- [ ] **Step 2: 确认工作区干净**

```bash
git status
```

Expected: clean（仅 HANDOFF-PY-EXTRACTION.md 未跟踪）。

---

## 批次结论记录（实施后填写）

- **5 脚本清零**：check-p6-provenance、check-pruning、check-state-yaml、check-changelog、agate-inject-card 全部内联 python 清零。
- **共享工具复用**：`agate-md-field-get.py` 是 P1/P2 markdown 字段提取的通用工具。
- **遗留**：check-p6-evidence(3，含图像处理)、check-gate(2) = 5 处，下一批（批 6：图像 + gate_commands）。