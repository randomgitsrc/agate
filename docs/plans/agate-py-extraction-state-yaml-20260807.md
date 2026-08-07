# agate IPC 抽离批次 4：状态 YAML 共享工具 + 5 脚本清零 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 创建共享工具 `agate/scripts/agate-state-get.py`（读 .state.yaml 的 phase/task_id/retries）+ 专用 `agate/scripts/agate-retreat-state.py`（agate-retreat-to 的 check/write）+ 扩展 `agate-json-get.py` 加 `escape` 子命令，完成 `check-state-transition.sh`(3)、`gate-result.sh`(3)、`check-retrospective.sh`(1)、`agate-retreat-to.sh`(3)、`pre-commit-gate.sh`(1) 共 **11 处**内联 python 抽离。

**Architecture:** （1）`agate-state-get.py` 从 `STATE_FILE` 环境变量读 .state.yaml，按子命令输出：`phase FILE`、`phase_stdin`（从 stdin 读 git show 的内容）、`task_id FILE`、`retries_over FILE MAP`（首个超限阶段）。（2）`agate-retreat-state.py` 处理 agate-retreat-to 的两处独特逻辑：`check_retreat FILE MAP CUR TGT`（回退路径超限检查）、`write_retreat FILE NEW_PHASE REASON`（追加 retry + 改 phase + 回写 yaml）。（3）`agate-json-get.py` 加 `escape` 子命令（`json.dumps(sys.stdin.read())`，用于 gate-result:26 的输出转义）。行为等价 → 既有测试（check-state-transition 26、check-retrospective 11、agate-retreat-to 5、pre-commit-hook 41、check-gate 101）是强兜底。

**Tech Stack:** bash（薄壳）+ python3（共享工具 + 专用工具）+ bats（测试）。

**背景调研（已确认）：**
- 触发文件：`agate/scripts/agate-state-get.py`（新增）、`agate/scripts/agate-retreat-state.py`（新增）、`agate/scripts/agate-json-get.py`（改）、5 个 .sh（改）、bats（改）→ self-gate 触发
- **11 处内联分布与模式**：
  - `读取 phase（STATE_FILE 文件）`：check-state-transition:42、gate-result:39、agate-retreat-to:23 — 三者逐字相同
    ```python
    import yaml, os
    with open(os.environ['STATE_FILE']) as f:
        data = yaml.safe_load(f)
    print(data.get('phase', '') if data else '')
    ```
  - `读取 phase（git show stdin）`：check-state-transition:30、pre-commit-gate:76 — 逐字相同
    ```python
    import yaml, sys
    try:
        data = yaml.safe_load(sys.stdin)
        print(data.get('phase', '') if data else '')
    except:
        print('')
    ```
  - `读取 task_id（STATE_FILE 文件）`：gate-result:50 — `data.get('task_id','') if data else ''`
  - `retries 超限检查`：check-state-transition:84（map 来自 MAX_RETRY_MAP env）、check-retrospective:16（map 硬编码 P1:3,...）
    ```python
    # 首个 len(attempts) >= phase_max 的阶段
    max_map = dict(p.split(':') for p in MAP.split(','))
    if isinstance(retries, dict):
        for phase, attempts in retries.items():
            phase_max = int(max_map.get(phase, 3))
            if isinstance(attempts, list) and len(attempts) >= phase_max:
                print(f'{phase}={len(attempts)} (MAX={phase_max})')
                break
    ```
  - `回退路径超限检查`：agate-retreat-to:51（CUR/TGT 范围，count+1 > limit）
  - `写 retry + 改 phase + 回写`：agate-retreat-to:80（yaml.safe_dump 回写）
  - `json.dumps 输出转义`：gate-result:26（`json.dumps(sys.stdin.read())`）
- `max_map` 差异：check-state-transition 从 `MAX_RETRY_MAP` env 读，check-retrospective 硬编码 `'P1:3,P2:3,P3:2,P4:3,P5:2,P6:2,P7:2,P8:2'`。共享工具 `retries_over` 接受 MAP 参数，bash 侧两脚本各自传（check-retrospective 显式传硬编码串，check-state-transition 传 `$MAX_RETRY_MAP`）。

---

## File Structure

- **Create** `agate/scripts/agate-state-get.py` — phase/phase_stdin/task_id/retries_over 子命令。
- **Create** `agate/scripts/agate-retreat-state.py` — check_retreat/write_retreat 子命令。
- **Modify** `agate/scripts/agate-json-get.py` — 加 `escape` 子命令。
- **Modify** `agate/scripts/check-state-transition.sh`、`gate-result.sh`、`check-retrospective.sh`、`agate-retreat-to.sh`、`pre-commit-gate.sh` — 11 处替换。
- **Test** `agate/tests/unit/agate-state-get.bats`（新建）、`agate/tests/unit/agate-retreat-state.bats`（新建）。
- **Test** `agate/tests/unit/agate-json-get.bats` — 加 `escape` 测试。
- **Modify** `agate/tests/README.md` — 新增 2 行。

---

### Task 1: TDD — 写 `agate-state-get.py` 直接失败测试（真红）

**Files:**
- Test: `agate/tests/unit/agate-state-get.bats`（新建）

**背景**：新工具尚不存在。写直接调用测试确立契约（phase/phase_stdin/task_id/retries_over）。

- [ ] **Step 1: 新建测试文件**

创建 `agate/tests/unit/agate-state-get.bats`：

```bash
#!/usr/bin/env bats
# tests/unit/agate-state-get.bats — 状态 YAML 读取共享工具单元测试
load ../helpers/load.bash

@test "STGET.1 phase 读 .state.yaml 的 phase" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/st-XXXXXX")
    cat > "$dir/.state.yaml" <<'EOF'
task_id: T001
phase: P3
status: active
EOF
    run bash -c "STATE_FILE='$dir/.state.yaml' python3 '$AGATE_SCRIPTS/agate-state-get.py' phase"
    [ "$status" -eq 0 ]
    [[ "$output" == "P3" ]]
}

@test "STGET.2 phase 空状态文件 → 空串" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/st-XXXXXX")
    echo "" > "$dir/.state.yaml"
    run bash -c "STATE_FILE='$dir/.state.yaml' python3 '$AGATE_SCRIPTS/agate-state-get.py' phase"
    [ "$status" -eq 0 ]
    [ -z "$output" ]
}

@test "STGET.3 phase_stdin 从 stdin 读 phase" {
    run bash -c "echo 'task_id: T1
phase: P5' | python3 '$AGATE_SCRIPTS/agate-state-get.py' phase_stdin"
    [ "$status" -eq 0 ]
    [[ "$output" == "P5" ]]
}

@test "STGET.4 task_id 读 .state.yaml 的 task_id" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/st-XXXXXX")
    cat > "$dir/.state.yaml" <<'EOF'
task_id: T042
phase: P1
EOF
    run bash -c "STATE_FILE='$dir/.state.yaml' python3 '$AGATE_SCRIPTS/agate-state-get.py' task_id"
    [ "$status" -eq 0 ]
    [[ "$output" == "T042" ]]
}

@test "STGET.5 retries_over 首个超限阶段" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/st-XXXXXX")
    cat > "$dir/.state.yaml" <<'EOF'
task_id: T1
phase: P3
retries:
  P1:
    - {attempt: 1}
    - {attempt: 2}
    - {attempt: 3}
EOF
    run bash -c "STATE_FILE='$dir/.state.yaml' python3 '$AGATE_SCRIPTS/agate-state-get.py' retries_over 'P1:3,P2:3,P3:2,P4:3,P5:2,P6:2,P7:2,P8:2'"
    [ "$status" -eq 0 ]
    [[ "$output" == "P1=3 (MAX=3)"* ]]
}

@test "STGET.6 retries_over 无超限 → 空输出" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/st-XXXXXX")
    cat > "$dir/.state.yaml" <<'EOF'
task_id: T1
phase: P3
retries:
  P1:
    - {attempt: 1}
EOF
    run bash -c "STATE_FILE='$dir/.state.yaml' python3 '$AGATE_SCRIPTS/agate-state-get.py' retries_over 'P1:3,P2:3,P3:2,P4:3,P5:2,P6:2,P7:2,P8:2'"
    [ "$status" -eq 0 ]
    [ -z "$output" ]
}
```

> **红/绿说明**：`agate-state-get.py` 尚不存在 → 全 FAIL（红）。实现后 → 全 PASS（绿）。

- [ ] **Step 2: 运行测试确认当前失败（红）**

```bash
bats agate/tests/unit/agate-state-get.bats
```

Expected: 6 个 @test 全部 FAIL。

---

### Task 2: TDD — 实现 `agate-state-get.py`（绿）

**Files:**
- Create: `agate/scripts/agate-state-get.py`

**背景**：实现 4 个子命令。`retries_over` 接受 MAP 参数（以 `,` 分隔的 `P:max` 对）。

- [ ] **Step 1: 创建 `.py`**

```python
#!/usr/bin/env python3
"""读 .state.yaml 的字段（py 抽离共享工具）。

从 STATE_FILE 环境变量读 .state.yaml，按子命令输出。STATE_FILE 不存在/不可读时
抛异常→非零退出（由 bash 调用方 2>/dev/null || echo 兜底）。

用法：
  phase         打印 STATE_FILE 的 data.get('phase', '')（data 为 None 时打印空）
  phase_stdin   从 stdin 读 yaml（git show 场景），打印 phase
  task_id       打印 STATE_FILE 的 data.get('task_id', '')
  retries_over MAP  打印首个 len(attempts) >= phase_max 的阶段 "PHASE=N (MAX=M)"
"""

import os
import sys

try:
    import yaml
except ImportError:
    sys.stderr.write("agate-state-get: 需要 pyyaml。pip install pyyaml\n")
    sys.exit(1)


def _load(path):
    with open(path) as f:
        return yaml.safe_load(f)


def main():
    op = sys.argv[1]
    if op == "phase":
        data = _load(os.environ["STATE_FILE"])
        print(data.get("phase", "") if data else "")
    elif op == "phase_stdin":
        data = yaml.safe_load(sys.stdin)
        print(data.get("phase", "") if data else "")
    elif op == "task_id":
        data = _load(os.environ["STATE_FILE"])
        print(data.get("task_id", "") if data else "")
    elif op == "retries_over":
        state_file = os.environ["STATE_FILE"]
        max_map_str = sys.argv[2]
        data = _load(state_file)
        retries = data.get("retries", {}) if data else {}
        max_map = dict(p.split(":") for p in max_map_str.split(","))
        if isinstance(retries, dict):
            for phase, attempts in retries.items():
                phase_max = int(max_map.get(phase, 3))
                if isinstance(attempts, list) and len(attempts) >= phase_max:
                    print(f"{phase}={len(attempts)} (MAX={phase_max})")
                    break
    else:
        sys.stderr.write("agate-state-get: unknown op {}\n".format(op))
        sys.exit(2)


if __name__ == "__main__":
    main()
```

> **等价性**：`phase`/`task_id` 复刻各内联段 `data.get(...,'') if data else ''`。`phase_stdin` 复刻 check-state-transition:30 / pre-commit-gate:76 的 `yaml.safe_load(sys.stdin)` + try/except（工具让异常上抛，bash 侧 `2>/dev/null || echo ""` 兜底，行为等价）。`retries_over` 复刻 check-state-transition:84 / check-retrospective:16 逻辑。
> **注意**：`phase_stdin` 原内联有 try/except 捕获，工具改为不捕获（异常上抛→非零退出→bash `|| echo ""` 兜底），行为等价。

- [ ] **Step 2: 运行测试确认通过（绿）**

```bash
chmod +x agate/scripts/agate-state-get.py
bats agate/tests/unit/agate-state-get.bats
```

Expected: 6 个 @test 全 PASS。

---

### Task 3: TDD — 写 `agate-retreat-state.py` 直接失败测试（真红）

**Files:**
- Test: `agate/tests/unit/agate-retreat-state.bats`（新建）

**背景**：agate-retreat-to 的两处独特逻辑（回退路径检查 + 写回退）抽成专用工具。写直接测试确立契约。

- [ ] **Step 1: 新建测试文件**

创建 `agate/tests/unit/agate-retreat-state.bats`：

```bash
#!/usr/bin/env bats
# tests/unit/agate-retreat-state.bats — 回退状态读写专用工具单元测试
load ../helpers/load.bash

@test "RSTATE.1 check_retreat 路径上阶段超限 → 输出 phase:count:limit" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/rs-XXXXXX")
    cat > "$dir/.state.yaml" <<'EOF'
task_id: T1
phase: P4
retries:
  P3:
    - {attempt: 1}
    - {attempt: 2}
EOF
    run bash -c "STATE_FILE='$dir/.state.yaml' CUR=4 TGT=2 python3 '$AGATE_SCRIPTS/agate-retreat-state.py' check_retreat 'P1:3,P2:3,P3:2,P4:3,P5:2,P6:2,P7:2,P8:2'"
    [ "$status" -eq 0 ]
    [[ "$output" == "P3:3:2" ]]
}

@test "RSTATE.2 check_retreat 无超限 → 空输出" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/rs-XXXXXX")
    cat > "$dir/.state.yaml" <<'EOF'
task_id: T1
phase: P4
retries:
  P3:
    - {attempt: 1}
EOF
    run bash -c "STATE_FILE='$dir/.state.yaml' CUR=4 TGT=2 python3 '$AGATE_SCRIPTS/agate-retreat-state.py' check_retreat 'P1:3,P2:3,P3:2,P4:3,P5:2,P6:2,P7:2,P8:2'"
    [ "$status" -eq 0 ]
    [ -z "$output" ]
}

@test "RSTATE.3 write_retreat 追加 retry + 改 phase + 回写" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/rs-XXXXXX")
    cat > "$dir/.state.yaml" <<'EOF'
task_id: T1
phase: P4
status: active
retries:
  P3:
    - {attempt: 1, reason: x}
EOF
    run bash -c "STATE_FILE='$dir/.state.yaml' NEW_PHASE=P3 RETREAT_REASON='test reason' python3 '$AGATE_SCRIPTS/agate-retreat-state.py' write_retreat"
    [ "$status" -eq 0 ]
    run cat "$dir/.state.yaml"
    [[ "$output" == *"phase: P3"* ]]
    [[ "$output" == *"attempt: 2"* ]]
    [[ "$output" == *"test reason"* ]]
}
```

> **红/绿说明**：`agate-retreat-state.py` 尚不存在 → 全 FAIL（红）。实现后 → 全 PASS（绿）。

- [ ] **Step 2: 运行测试确认当前失败（红）**

```bash
bats agate/tests/unit/agate-retreat-state.bats
```

Expected: 3 个 @test 全部 FAIL。

---

### Task 4: TDD — 实现 `agate-retreat-state.py`（绿）

**Files:**
- Create: `agate/scripts/agate-retreat-state.py`

**背景**：复刻 agate-retreat-to:51（check_retreat）与 :80（write_retreat）逻辑。

- [ ] **Step 1: 创建 `.py`**

```python
#!/usr/bin/env python3
"""agate-retreat-to.sh 的状态读写专用工具（py 抽离批次 4）。

从 STATE_FILE 环境变量读写 .state.yaml。

用法：
  check_retreat FILE MAP  回退路径超限检查。遍历 CUR-1..TGT，若某阶段
                          len(attempts)+1 > limit，输出 "PHASE:COUNT+1:LIMIT" 并 break。
  write_retreat           追加一条 retry 到 NEW_PHASE、把 phase 改为 NEW_PHASE、
                          回写 .state.yaml（allow_unicode/sort_keys=False）。
"""

import os
import sys

try:
    import yaml
except ImportError:
    sys.stderr.write("agate-retreat-state: 需要 pyyaml。pip install pyyaml\n")
    sys.exit(1)


def main():
    op = sys.argv[1]
    state_file = os.environ["STATE_FILE"]
    if op == "check_retreat":
        max_map_str = sys.argv[2]
        with open(state_file) as f:
            data = yaml.safe_load(f) or {}
        retries = data.get("retries", {}) or {}
        max_map = dict(p.split(":") for p in max_map_str.split(","))
        cur, tgt = int(os.environ["CUR"]), int(os.environ["TGT"])
        for n in range(cur - 1, tgt - 1, -1):
            phase = f"P{n}"
            attempts = retries.get(phase, [])
            count = len(attempts) if isinstance(attempts, list) else 0
            limit = int(max_map.get(phase, 3))
            if count + 1 > limit:
                print(f"{phase}:{count + 1}:{limit}")
                break
    elif op == "write_retreat":
        with open(state_file) as f:
            data = yaml.safe_load(f) or {}
        retries = data.setdefault("retries", {})
        new_phase = os.environ["NEW_PHASE"]
        attempts = retries.setdefault(new_phase, [])
        attempts.append({"attempt": len(attempts) + 1, "reason": os.environ["RETREAT_REASON"]})
        data["phase"] = new_phase
        with open(state_file, "w") as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
    else:
        sys.stderr.write("agate-retreat-state: unknown op {}\n".format(op))
        sys.exit(2)


if __name__ == "__main__":
    main()
```

> **等价性**：`check_retreat` 复刻 agate-retreat-to:51 的 `range(cur-1, tgt-1, -1)` 循环 + `count+1 > limit`。`write_retreat` 复刻 :80 的 `setdefault` + append + `data['phase']=new_phase` + `safe_dump(allow_unicode=True, sort_keys=False)`。

- [ ] **Step 2: 运行测试确认通过（绿）**

```bash
chmod +x agate/scripts/agate-retreat-state.py
bats agate/tests/unit/agate-retreat-state.bats
```

Expected: 3 个 @test 全 PASS。

---

### Task 5: TDD — 扩展 `agate-json-get.py` 加 `escape` 子命令（真红→绿）

**Files:**
- Modify: `agate/scripts/agate-json-get.py`
- Test: `agate/tests/unit/agate-json-get.bats`

**背景**：gate-result:26 需要 `json.dumps(sys.stdin.read())`（把原始输出转义成 JSON 字符串）。加 `escape` 子命令。

- [ ] **Step 1: 写失败测试**

在 `agate/tests/unit/agate-json-get.bats` 末尾追加：

```bash
@test "JGET.8 escape json.dumps stdin 原始文本" {
    run bash -c "printf '%s' 'a\"b
c' | python3 '$AGATE_SCRIPTS/agate-json-get.py' escape"
    [ "$status" -eq 0 ]
    [[ "$output" == *'a\"b'* ]]
}
```
> **注意**：断言用 `*'a\"b'*`（**单个**反斜杠）。`json.dumps('a"b\nc')` 输出 `"a\"b\nc"`（一个 `\`）。若写成 `*'a\\"b'*`（两个反斜杠）会永远不匹配（false-red）。

- [ ] **Step 2: 运行测试确认当前失败（红）**

```bash
bats agate/tests/unit/agate-json-get.bats --filter 'JGET.8'
```

Expected: FAIL（`agate-json-get: unknown op escape`）。

- [ ] **Step 3: 实现 `escape` 子命令**

在 `agate-json-get.py` 的 `elif op == "list":` 分支后追加：

```python
    elif op == "escape":
        print(json.dumps(sys.stdin.read()))
```

> **注意**：`escape` 读原始 stdin（非 JSON），所以必须在 `data = json.load(sys.stdin)` 之前处理。当前 `main()` 首行 `data = json.load(sys.stdin)` 会先尝试解析 stdin。需把 `escape` 分支放在 `json.load` 之前。**修改 `main()`：**

`agate-json-get.py` 当前 `main()` 结构：
```python
def main():
    data = json.load(sys.stdin)
    op = sys.argv[1]
    ...
```
改为：
```python
def main():
    op = sys.argv[1]
    if op == "escape":
        print(json.dumps(sys.stdin.read()))
        return
    data = json.load(sys.stdin)
    ...
```

- [ ] **Step 4: 运行测试确认通过（绿）**

```bash
bats agate/tests/unit/agate-json-get.bats
```

Expected: 8 个 @test 全 PASS（JGET.1-8）。

---

### Task 6: 改造 5 个脚本 11 处内联（薄壳）

**Files:**
- Modify: `agate/scripts/check-state-transition.sh`、`gate-result.sh`、`check-retrospective.sh`、`agate-retreat-to.sh`、`pre-commit-gate.sh`

**背景**：逐处替换。各脚本 `SCRIPT_DIR` **并非都已定义**（已核实：仅 agate-retreat-to.sh 有；check-state-transition / check-retrospective / gate-result 三者皆无；pre-commit-gate.sh 有 `AGATE_ROOT` 无 `SCRIPT_DIR`）。因此**替换前必须先保证脚本目录变量可用**，否则 `python3 "$SCRIPT_DIR/agate-state-get.py"` 会展开成 `/agate-state-get.py` 报错。

- [ ] **Step 0: 为缺 `SCRIPT_DIR` 的脚本补定义（前置）**

在以下脚本顶部（`set -euo pipefail` 之后、其他逻辑之前）加一行（与 `agate-retreat-to.sh:12` / `check-tdd-red.sh:47` 一致）：
```bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
```
补到：
- `agate/scripts/check-state-transition.sh`
- `agate/scripts/check-retrospective.sh`
- `agate/scripts/gate-result.sh`（被 source 的工具库，`${BASH_SOURCE[0]}` 指向被 source 文件本身，正确）

`pre-commit-gate.sh` **不加** SCRIPT_DIR（它已有 `AGATE_ROOT`，见 Step 4 用 `$AGATE_ROOT/scripts/`）。

- [ ] **Step 1: check-state-transition.sh 三处**

原（:30，git show stdin 读 phase）：
```bash
    git show "HEAD:$git_path" 2>/dev/null | python3 -c "
import yaml, sys
try:
    data = yaml.safe_load(sys.stdin)
    print(data.get('phase', '') if data else '')
except:
    print('')
" 2>/dev/null || echo ""
```
新：
```bash
    git show "HEAD:$git_path" 2>/dev/null | python3 "$SCRIPT_DIR/agate-state-get.py" phase_stdin 2>/dev/null || echo ""
```

原（:42，文件读 phase）：
```bash
    STATE_FILE="$STATE_FILE" python3 -c "
import yaml, os
with open(os.environ['STATE_FILE']) as f:
    data = yaml.safe_load(f)
print(data.get('phase', '') if data else '')
" 2>/dev/null || echo ""
```
新：
```bash
    STATE_FILE="$STATE_FILE" python3 "$SCRIPT_DIR/agate-state-get.py" phase 2>/dev/null || echo ""
```

原（:84，retries 超限）：
```bash
    retries_json=$(STATE_FILE="$STATE_FILE" MAX_RETRY="$MAX_RETRY" MAX_RETRY_MAP="$MAX_RETRY_MAP" python3 -c "
import yaml, os
with open(os.environ['STATE_FILE']) as f:
    data = yaml.safe_load(f)
retries = data.get('retries', {})
max_retry = int(os.environ['MAX_RETRY'])
max_map_str = os.environ['MAX_RETRY_MAP']
max_map = dict(p.split(':') for p in max_map_str.split(','))
if isinstance(retries, dict):
    for phase, attempts in retries.items():
        phase_max = int(max_map.get(phase, 3))
        if isinstance(attempts, list) and len(attempts) >= phase_max:
            print(f'{phase}={len(attempts)} (MAX={phase_max})')
            break
" 2>/dev/null || echo "")
```
新：
```bash
    retries_json=$(STATE_FILE="$STATE_FILE" python3 "$SCRIPT_DIR/agate-state-get.py" retries_over "$MAX_RETRY_MAP" 2>/dev/null || echo "")
```
> **注意**：原内联段声明了 `max_retry = int(os.environ['MAX_RETRY'])` 但**未使用**（死代码）。新工具不读 `MAX_RETRY`，仅用 `MAX_RETRY_MAP`。行为等价（max_map.get(phase,3) 才是生效逻辑）。`MAX_RETRY` env 不再传。

- [ ] **Step 2: gate-result.sh 三处**

原（:26，输出转义）：
```bash
  "output": $(printf '%s' "$output" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))'),
```
新：
```bash
  "output": $(printf '%s' "$output" | python3 "$SCRIPT_DIR/agate-json-get.py" escape),
```
> **注意**：gate-result.sh 是**被 source 的工具库**。Step 0 已在该文件顶部加 `SCRIPT_DIR`（`${BASH_SOURCE[0]}` 指向被 source 文件本身，正确）。

原（:39，读 phase）：
```bash
    STATE_FILE="$state_file" python3 -c "
import yaml, os
with open(os.environ['STATE_FILE']) as f:
    data = yaml.safe_load(f)
print(data.get('phase', '') if data else '')
" 2>/dev/null || echo ""
```
新：
```bash
    STATE_FILE="$state_file" python3 "$SCRIPT_DIR/agate-state-get.py" phase 2>/dev/null || echo ""
```

原（:50，读 task_id）：同理替换为：
```bash
    STATE_FILE="$state_file" python3 "$SCRIPT_DIR/agate-state-get.py" task_id 2>/dev/null || echo ""
```

- [ ] **Step 3: check-retrospective.sh 一处**

原（:16，retries 超限，map 硬编码）：
```bash
    RETRIES_OVER=$(STATE_FILE="$STATE_FILE" python3 -c "
import yaml, os
with open(os.environ['STATE_FILE']) as f:
    data = yaml.safe_load(f)
retries = data.get('retries', {})
max_map = dict(p.split(':') for p in 'P1:3,P2:3,P3:2,P4:3,P5:2,P6:2,P7:2,P8:2'.split(','))
if isinstance(retries, dict):
    for phase, attempts in retries.items():
        phase_max = int(max_map.get(phase, 3))
        if isinstance(attempts, list) and len(attempts) >= phase_max:
            print(f'{phase}={len(attempts)} (MAX={phase_max})')
            break
" 2>/dev/null || echo "")
```
新：
```bash
    RETRIES_OVER=$(STATE_FILE="$STATE_FILE" python3 "$SCRIPT_DIR/agate-state-get.py" retries_over 'P1:3,P2:3,P3:2,P4:3,P5:2,P6:2,P7:2,P8:2' 2>/dev/null || echo "")
```

- [ ] **Step 4: agate-retreat-to.sh 三处**

原（:23，读 phase）：
```bash
CURRENT_PHASE=$(STATE_FILE="$STATE_FILE" python3 -c "
import yaml, os
with open(os.environ['STATE_FILE']) as f:
    print((yaml.safe_load(f) or {}).get('phase', ''))
")
```
新：
```bash
CURRENT_PHASE=$(STATE_FILE="$STATE_FILE" python3 "$SCRIPT_DIR/agate-state-get.py" phase)
```
> **注意**：原 `(yaml.safe_load(f) or {}).get('phase','')` 与工具 `data.get('phase','') if data else ''` 等价（data None → 空串）。

原（:51，回退路径检查）：
```bash
CHECK_RESULT=$(STATE_FILE="$STATE_FILE" MAX_RETRY_MAP="$MAX_RETRY_MAP" CUR="$cur_num" TGT="$tgt_num" python3 -c "
import yaml, os
with open(os.environ['STATE_FILE']) as f:
    data = yaml.safe_load(f) or {}
retries = data.get('retries', {}) or {}
max_map = dict(p.split(':') for p in os.environ['MAX_RETRY_MAP'].split(','))
cur, tgt = int(os.environ['CUR']), int(os.environ['TGT'])
for n in range(cur - 1, tgt - 1, -1):
    phase = f'P{n}'
    attempts = retries.get(phase, [])
    count = len(attempts) if isinstance(attempts, list) else 0
    limit = int(max_map.get(phase, 3))
    if count + 1 > limit:
        print(f'{phase}:{count+1}:{limit}')
        break
")
```
新：
```bash
CHECK_RESULT=$(STATE_FILE="$STATE_FILE" CUR="$cur_num" TGT="$tgt_num" python3 "$SCRIPT_DIR/agate-retreat-state.py" check_retreat "$MAX_RETRY_MAP")
```

原（:80，写回退）：
```bash
    STATE_FILE="$STATE_FILE" NEW_PHASE="$new_p" RETREAT_REASON="$REASON" python3 -c "
import yaml, os
with open(os.environ['STATE_FILE']) as f:
    data = yaml.safe_load(f) or {}
retries = data.setdefault('retries', {})
new_phase = os.environ['NEW_PHASE']
attempts = retries.setdefault(new_phase, [])
attempts.append({'attempt': len(attempts) + 1, 'reason': os.environ['RETREAT_REASON']})
data['phase'] = new_phase
with open(os.environ['STATE_FILE'], 'w') as f:
    yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
"
```
新：
```bash
    STATE_FILE="$STATE_FILE" NEW_PHASE="$new_p" RETREAT_REASON="$REASON" python3 "$SCRIPT_DIR/agate-retreat-state.py" write_retreat
```

- [ ] **Step 5: pre-commit-gate.sh 一处**

原（:76，git show stdin 读 phase）：
```bash
    OLD_PHASE=$(git show "HEAD:$STATE_REL" 2>/dev/null | python3 -c "
import yaml, sys
try:
    data = yaml.safe_load(sys.stdin)
    print(data.get('phase', '') if data else '')
except Exception:
    print('')
" 2>/dev/null || echo "")
```
新：
```bash
    OLD_PHASE=$(git show "HEAD:$STATE_REL" 2>/dev/null | python3 "$AGATE_ROOT/scripts/agate-state-get.py" phase_stdin 2>/dev/null || echo "")
```
> **注意**：pre-commit-gate.sh **无 `SCRIPT_DIR`**，但有 `AGATE_ROOT`（第 26 行，Batch 1 自定位修复）。用 `$AGATE_ROOT/scripts/agate-state-get.py` 定位（同目录），勿依赖未定义的 `SCRIPT_DIR`。

- [ ] **Step 6: 验证 5 个脚本相关测试仍绿**

```bash
bats agate/tests/unit/check-state-transition.bats agate/tests/unit/check-retrospective.bats agate/tests/unit/agate-retreat-to.bats agate/tests/unit/agate-state-get.bats agate/tests/unit/agate-retreat-state.bats agate/tests/unit/agate-json-get.bats agate/tests/integration/pre-commit-hook.bats
```

Expected: 全部 PASS。

---

### Task 7: 全量回归 + 一致性 + 用例数 + shellcheck

**Files:**（无改动，仅验证）

- [ ] **Step 0: 验证脚本目录变量已就绪**

```bash
rg -n "SCRIPT_DIR=" agate/scripts/check-state-transition.sh agate/scripts/check-retrospective.sh agate/scripts/gate-result.sh agate/scripts/agate-retreat-to.sh
rg -n "AGATE_ROOT=" agate/scripts/pre-commit-gate.sh
```
Expected: 前 4 个各有 `SCRIPT_DIR=`；pre-commit-gate.sh 有 `AGATE_ROOT=`（Step 0 前置已补）。若缺，回到 Task 6 Step 0 补加。

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

Expected: 原 556 + 6（STGET.1-6）+ 3（RSTATE.1-3）+ 1（JGET.8）= **566**。

- [ ] **Step 4: shellcheck**

```bash
shellcheck -S warning agate/scripts/*.sh
```

Expected: 无 error。

- [ ] **Step 5: AST 校验**

```bash
python3 -c "import ast; ast.parse(open('agate/scripts/agate-state-get.py').read())"
python3 -c "import ast; ast.parse(open('agate/scripts/agate-retreat-state.py').read())"
```

Expected: 无输出（语法有效）。

---

### Task 8: 文档同步（README 逐脚本用例数）

**Files:**
- Modify: `agate/tests/README.md`

**背景**：新增 `agate-state-get.bats`、`agate-retreat-state.bats` 需登记。

- [ ] **Step 1: 定位 README 逐脚本表 + 插入 2 行**

在 `agate-json-get.py` / `agate-read-p5-commands.py` 行附近插入：
```
| agate-state-get.py | unit/agate-state-get.bats | 6 |
| agate-retreat-state.py | unit/agate-retreat-state.bats | 3 |
```
同时把 `agate-json-get.py` 行由 7 改 8（新增 JGET.8）。

> **注意**：总数行是 `以 count-tests.sh 输出为准`，不需改。

---

### Task 9: commit（self-gate）

**Files:**
- 提交：新增 2 个 .py、2 个 .bats、改 agate-json-get.py、5 个 .sh、README

**背景**：触发文件含 `agate/scripts/*.py`、`agate/scripts/*.sh`、`agate/tests/*.bats` → commit-msg-self-gate hook 要求 `self-gate-review:`。

- [ ] **Step 1: 暂存并提交**

```bash
cd /home/kity/oclab/agate/.worktrees/py-extraction
git add agate/scripts/agate-state-get.py agate/scripts/agate-retreat-state.py agate/scripts/agate-json-get.py agate/scripts/check-state-transition.sh agate/scripts/gate-result.sh agate/scripts/check-retrospective.sh agate/scripts/agate-retreat-to.sh agate/scripts/pre-commit-gate.sh agate/tests/unit/agate-state-get.bats agate/tests/unit/agate-retreat-state.bats agate/tests/unit/agate-json-get.bats agate/tests/README.md
git commit -m "feat(scripts): 状态 YAML 共享工具，5 脚本 11 处内联抽离

新增 agate/scripts/agate-state-get.py（phase/phase_stdin/task_id/retries_over）
与 agate/scripts/agate-retreat-state.py（check_retreat/write_retreat），
扩展 agate-json-get.py 加 escape 子命令。
替换 check-state-transition(3) gate-result(3) check-retrospective(1)
agate-retreat-to(3) pre-commit-gate(1) 共 11 处内联 python。
行为等价，既有 556 测试全绿。新增 STGET.1-6 RSTATE.1-3 JGET.8，总数 556→566。

self-gate-review: docs/plans/agate-py-extraction-state-yaml-20260807.md"
```

Expected: commit 成功，hook 识别 `self-gate-review:` 无 WARNING。

- [ ] **Step 2: 确认工作区干净**

```bash
git status
```

Expected: clean（仅 HANDOFF-PY-EXTRACTION.md 未跟踪）。

---

## 批次结论记录（实施后填写）

- **5 脚本清零**：check-state-transition、gate-result、check-retrospective、agate-retreat-to、pre-commit-gate 全部内联 python 清零。
- **共享工具复用**：`agate-state-get.py` 的 phase/task_id/retries_over 是 .state.yaml 场景最高频模式，已在 5 脚本落地。
- **遗留**：check-p6-provenance(4)、check-p6-evidence(3)、check-pruning(2)、check-gate(2)、check-state-yaml(1)、check-changelog(1)、agate-inject-card(1) = 14 处，下一批（regex 字段提取 + 图像处理 + YAML 校验）。