# agate 共享 JSON 提取工具 + 完成 check-tdd-red.sh 抽离 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 创建共享工具 `agate/scripts/agate-json-get.py`，统一散落在各 .sh 里的单行 JSON 提取内联段（`echo "$json" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get(...))'`），并用它完成 `check-tdd-red.sh` 剩余 12 处内联 python 的抽离（该脚本 13 处原内联全部清零：read_gate_commands 已由批 1 抽离，剩 12 处本批清零）。

**Architecture:** `agate-json-get.py` 从 stdin 读 JSON，按子命令（`get`/`len`/`index`/`set`/`count_prefix`）提取或改写字段，输出到 stdout。bash 侧把 `echo "$x" | python3 -c 'import sys,json; ...'` 替换为 `echo "$x" | python3 "$SCRIPT_DIR/agate-json-get.py" get key default` 等。行为等价 → 现有 check-tdd-red.bats 仍是强兜底。该工具后续批次可复用于 agate-capture-env-baseline（8 处）、gate-result.sh（3 处）等。

**Tech Stack:** bash（薄壳）+ python3（共享工具）+ bats（测试）。

**背景调研（已确认）：**
- 触发文件：`agate/scripts/agate-json-get.py`（新增）、`agate/scripts/check-tdd-red.sh`（改）、`agate/tests/*.bats`（改）→ self-gate 触发
- `check-tdd-red.sh` 剩余 12 处内联均为**单行 JSON 提取**，模式高度重复：
  - `d.get("exit_code",1)` / `d.get("failed",0)` / `d.get("errors",0)` / `d.get("project_module","")` → `get`
  - `len(d.get("syntax_errors",[]))` / `len(d["commands"])` → `len`
  - `d['commands'][$i]['cmd']` / `d['commands'][$i]['formatter']` → `index`
  - `d["project_module"]=os.environ["PROJECT_MODULE"]; print(json.dumps(d))` → `set`
  - `sum(1 for e in d.get("import_errors",[]) if e.get("module","").startswith(pm))`（第 90-96 行）→ `count_prefix`
- 12 处分布：`judge_result` 5 处（66-70）+ `judge_result` 1 处（90-96，count_prefix）+ `collect_commands` 2 处（142、145）+ `main` 4 处（165-166、172-173）
- 现已有 `agate/scripts/agate-read-gate-commands.py`（试点，P3 gate_commands 解析）——本批不碰它，仅新增更通用的 JSON 读取工具
- 单行 JSON 提取在 14 个脚本里共约 20+ 处，本批先在本脚本落地证明工具，后续批量复用

---

## File Structure

- **Create** `agate/scripts/agate-json-get.py` — 从 stdin 读 JSON，子命令派发提取/改写。
- **Modify** `agate/scripts/check-tdd-red.sh` — 12 处单行 JSON 提取替换为调用 `agate-json-get.py`（`judge_result` 6 处含 count_prefix、`collect_commands` 2 处、`main` 4 处）。
- **Test** `agate/tests/unit/agate-json-get.bats` — 新增共享工具的独立测试（新文件，count-tests 自动发现）。
- **Test** `agate/tests/unit/check-tdd-red.bats` — 既有测试不改（行为兜底），确认仍绿。
- **Modify** `agate/tests/README.md` — 新增 `agate-json-get.py` 行 + 用例数。

---

### Task 1: TDD — 写 `agate-json-get.py` 直接失败测试（真红）

**Files:**
- Test: `agate/tests/unit/agate-json-get.bats`（新建）

**背景**：新工具尚不存在。先写直接调用它的 bats 测试（真红），确立各子命令的行为契约，再实现工具。测试用 `$AGATE_SCRIPTS` 定位新脚本，通过管道喂 stdin JSON。

- [ ] **Step 1: 新建测试文件**

创建 `agate/tests/unit/agate-json-get.bats`：

```bash
#!/usr/bin/env bats
# tests/unit/agate-json-get.bats — 共享 JSON 提取工具单元测试
load ../helpers/load.bash

@test "JGET.1 get 取标量键 + 默认值" {
    run bash -c "echo '{\"exit_code\":2,\"failed\":3}' | python3 '$AGATE_SCRIPTS/agate-json-get.py' get exit_code 1"
    [ "$status" -eq 0 ]
    [[ "$output" == "2" ]]
    run bash -c "echo '{\"exit_code\":2,\"failed\":3}' | python3 '$AGATE_SCRIPTS/agate-json-get.py' get missing 0"
    [[ "$output" == "0" ]]
}

@test "JGET.2 get 字符串键默认空串" {
    run bash -c "echo '{\"a\":\"b\"}' | python3 '$AGATE_SCRIPTS/agate-json-get.py' get project_module \"\""
    [ "$status" -eq 0 ]
    [[ "$output" == "" ]]
}

@test "JGET.3 len 取数组长度（默认 0）" {
    run bash -c "echo '{\"commands\":[{\"cmd\":\"a\"},{\"cmd\":\"b\"}]}' | python3 '$AGATE_SCRIPTS/agate-json-get.py' len commands"
    [ "$status" -eq 0 ]
    [[ "$output" == "2" ]]
    run bash -c "echo '{\"commands\":[]}' | python3 '$AGATE_SCRIPTS/agate-json-get.py' len commands"
    [[ "$output" == "0" ]]
    run bash -c "echo '{}' | python3 '$AGATE_SCRIPTS/agate-json-get.py' len missing"
    [[ "$output" == "0" ]]
}

@test "JGET.4 index 取嵌套数组元素字段" {
    run bash -c "echo '{\"commands\":[{\"cmd\":\"pytest\",\"formatter\":\"pytest.sh\"},{\"cmd\":\"pytest\",\"formatter\":\"pytest.sh\"}]}' | python3 '$AGATE_SCRIPTS/agate-json-get.py' index commands 0 cmd"
    [ "$status" -eq 0 ]
    [[ "$output" == "pytest" ]]
    run bash -c "echo '{\"commands\":[{\"cmd\":\"pytest\",\"formatter\":\"pytest.sh\"}]}' | python3 '$AGATE_SCRIPTS/agate-json-get.py' index commands 0 formatter"
    [[ "$output" == "pytest.sh" ]]
}

@test "JGET.5 set 改写键并重排 JSON" {
    run bash -c "echo '{\"commands\":[{\"cmd\":\"pytest\"}],\"project_module\":\"\"}' | PROJECT_MODULE=mymod python3 '$AGATE_SCRIPTS/agate-json-get.py' set project_module PROJECT_MODULE"
    [ "$status" -eq 0 ]
    [[ "$output" == *'"project_module": "mymod"'* ]]
}

@test "JGET.6 count_prefix 统计 module 前缀匹配数" {
    run bash -c "echo '{\"import_errors\":[{\"module\":\"mymod.foo\"},{\"module\":\"other.bar\"},{\"module\":\"mymod.baz\"}]}' | PROJECT_MODULE=mymod python3 '$AGATE_SCRIPTS/agate-json-get.py' count_prefix import_errors module PROJECT_MODULE"
    [ "$status" -eq 0 ]
    [[ "$output" == "2" ]]
}
```

> **红/绿说明**：`agate-json-get.py` 尚不存在 → 每个用例 `python3 "$AGATE_SCRIPTS/agate-json-get.py"` 报「No such file」→ 全部 FAIL（红）。实现后 → 全 PASS（绿）。

- [ ] **Step 2: 运行测试确认当前失败（红）**

```bash
bats agate/tests/unit/agate-json-get.bats
```

Expected: 6 个 @test 全部 FAIL（`agate-json-get.py: No such file or directory`）。

---

### Task 2: TDD — 实现 `agate-json-get.py`（绿）

**Files:**
- Create: `agate/scripts/agate-json-get.py`

**背景**：实现子命令派发。stdin 读 JSON，`sys.argv[1]` 为子命令。`get`/`set`/`count_prefix` 的默认值语义与各内联段一致。

- [ ] **Step 1: 创建 `.py`**

```python
#!/usr/bin/env python3
"""从 stdin 读 JSON，按子命令提取/改写字段（py 抽离共享工具）。

统一 .sh 里散落的单行 JSON 提取内联段：
  echo "$x" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get(...))'

用法（JSON 从 stdin 传入）：
  get KEY DEFAULT      打印 d.get(KEY, DEFAULT)（DEFAULT 按字符串原样打印，缺失时返回）
  len KEY              打印 len(d.get(KEY, []))（缺失返回 0）
  index KEY IDX SUBKEY 打印 d[KEY][IDX][SUBKEY]
  set KEY ENVNAME      d[KEY]=os.environ[ENVNAME]；打印 json.dumps(d)
  count_prefix LIST SUBKEY ENVNAME  打印 LIST 中 SUBKEY 以 os.environ[ENVNAME] 开头的元素个数

未知子命令 → stderr 提示 + exit 2。
"""

import json
import os
import sys


def main():
    data = json.load(sys.stdin)
    op = sys.argv[1]

    if op == "get":
        key, default = sys.argv[2], sys.argv[3]
        print(data.get(key, default))
    elif op == "len":
        key = sys.argv[2]
        print(len(data.get(key, [])))
    elif op == "index":
        key, idx, subkey = sys.argv[2], int(sys.argv[3]), sys.argv[4]
        print(data[key][idx][subkey])
    elif op == "set":
        key, envname = sys.argv[2], sys.argv[3]
        data[key] = os.environ[envname]
        print(json.dumps(data))
    elif op == "count_prefix":
        listkey, subkey, envname = sys.argv[2], sys.argv[3], sys.argv[4]
        prefix = os.environ[envname]
        print(sum(1 for e in data.get(listkey, []) if e.get(subkey, "").startswith(prefix)))
    else:
        sys.stderr.write("agate-json-get: unknown op {}\n".format(op))
        sys.exit(2)


if __name__ == "__main__":
    main()
```

> **行为等价性**：`get KEY DEFAULT` 与原 `d.get(KEY, DEFAULT)` 一致——DEFAULT 为默认值字符串，缺失时打印默认值。`len` 用 `.get(KEY, [])`（缺失返回 0，与原 `len(d.get("syntax_errors",[]))` 一致；原 `len(d["commands"])` 用 `d["commands"]` 直接取，但 commands 恒存在，`.get` 行为等价）。`index` 用 `int()` 解析索引（bash 传入的 `$i` 是整数）。`count_prefix` 复刻原 `sum(1 for e in d.get("import_errors",[]) if e.get("module","").startswith(pm))`。

- [ ] **Step 2: 运行测试确认通过（绿）**

```bash
chmod +x agate/scripts/agate-json-get.py
bats agate/tests/unit/agate-json-get.bats
```

Expected: 6 个 @test 全 PASS。

---

### Task 3: 改造 `check-tdd-red.sh` 12 处单行 JSON 提取（薄壳）

**Files:**
- Modify: `agate/scripts/check-tdd-red.sh`

**背景**：把 12 处 `echo "$x" | python3 -c 'import sys,json; ...'` 替换为调用 `agate-json-get.py`。逐处等价替换，`SCRIPT_DIR` 已有（第 47 行）。

- [ ] **Step 1: 替换 `judge_result` 的 5 处（第 66-70 行）**

原：
```bash
    exit_code=$(echo "$json" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("exit_code",1))')
    failed=$(echo "$json" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("failed",0))')
    errors=$(echo "$json" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("errors",0))')
    syntax_count=$(echo "$json" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(len(d.get("syntax_errors",[])))')
    import_count=$(echo "$json" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(len(d.get("import_errors",[])))')
```
新：
```bash
    exit_code=$(echo "$json" | python3 "$SCRIPT_DIR/agate-json-get.py" get exit_code 1)
    failed=$(echo "$json" | python3 "$SCRIPT_DIR/agate-json-get.py" get failed 0)
    errors=$(echo "$json" | python3 "$SCRIPT_DIR/agate-json-get.py" get errors 0)
    syntax_count=$(echo "$json" | python3 "$SCRIPT_DIR/agate-json-get.py" len syntax_errors)
    import_count=$(echo "$json" | python3 "$SCRIPT_DIR/agate-json-get.py" len import_errors)
```

> **注意**：`get exit_code 1` 的默认值 `1` 是字符串，但原 `d.get("exit_code",1)` 默认是 int 1。二者经 bash `[ "$exit_code" -eq 124 ]` 比较时 `-eq` 会做算术（字符串 "1" 与 int 等价），行为一致。缺失时打印 `1`（字符串）与 int 打印 `1` 相同。

- [ ] **Step 2: 替换 `judge_result` 的 count_prefix 段（第 90-96 行）**

原：
```bash
            matched=$(echo "$json" | PROJECT_MODULE="$project_module" python3 -c '
import sys, json, os
d = json.load(sys.stdin)
pm = os.environ["PROJECT_MODULE"]
count = sum(1 for e in d.get("import_errors", []) if e.get("module","").startswith(pm))
print(count)
')
```
新：
```bash
            matched=$(echo "$json" | PROJECT_MODULE="$project_module" python3 "$SCRIPT_DIR/agate-json-get.py" count_prefix import_errors module PROJECT_MODULE)
```

> **等价性**：工具 `count_prefix LIST SUBKEY ENVNAME` 实现为 `sum(1 for e in data.get(LIST,[]) if e.get(SUBKEY,"").startswith(os.environ[ENVNAME]))`，与原内联段逐字一致。`PROJECT_MODULE="$project_module"` 显式传入，保持原语义。

- [ ] **Step 3: 替换 `collect_commands` 的 2 处（第 142、145 行）**

原（第 142 行）：
```bash
        cmd_count=$(echo "$commands_json" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(len(d["commands"]))')
```
新：
```bash
        cmd_count=$(echo "$commands_json" | python3 "$SCRIPT_DIR/agate-json-get.py" len commands)
```

原（第 145 行）：
```bash
                commands_json=$(echo "$commands_json" | python3 -c 'import sys,json,os; d=json.load(sys.stdin); d["project_module"]=os.environ["PROJECT_MODULE"]; print(json.dumps(d))' 2>/dev/null || echo "$commands_json")
```
新：
```bash
                commands_json=$(echo "$commands_json" | PROJECT_MODULE="$PROJECT_MODULE" python3 "$SCRIPT_DIR/agate-json-get.py" set project_module PROJECT_MODULE 2>/dev/null || echo "$commands_json")
```

> **等价性**：原段内联用 `os.environ["PROJECT_MODULE"]`，但 bash 侧已有 `PROJECT_MODULE` 变量（`${PROJECT_MODULE:-}`）。新段显式 `PROJECT_MODULE="$PROJECT_MODULE"` 传入。`2>/dev/null || echo "$commands_json"` 回退保留。
>
> **细微差异**：原内联 `os.environ["PROJECT_MODULE"]` 要求 `PROJECT_MODULE` 已 **export**，否则 KeyError → `2>/dev/null || echo` 回退（JSON 不变）。新段 `PROJECT_MODULE="$PROJECT_MODULE"` 总是注入，总是 set。实际等价（该分支外层已有 `[ -n "${PROJECT_MODULE:-}" ]` 守卫，且所有测试用 `env PROJECT_MODULE=...` 走 export 路径）。

- [ ] **Step 4: 替换 `main` 的 4 处（第 165-166、172-173 行）**

原（第 165-166 行）：
```bash
    project_module=$(echo "$commands_json" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("project_module",""))')
    commands_count=$(echo "$commands_json" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(len(d["commands"]))')
```
新：
```bash
    project_module=$(echo "$commands_json" | python3 "$SCRIPT_DIR/agate-json-get.py" get project_module "")
    commands_count=$(echo "$commands_json" | python3 "$SCRIPT_DIR/agate-json-get.py" len commands)
```

原（第 172-173 行）：
```bash
        cmd=$(echo "$commands_json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['commands'][$i]['cmd'])")
        fmt_val=$(echo "$commands_json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['commands'][$i]['formatter'])")
```
新：
```bash
        cmd=$(echo "$commands_json" | python3 "$SCRIPT_DIR/agate-json-get.py" index commands "$i" cmd)
        fmt_val=$(echo "$commands_json" | python3 "$SCRIPT_DIR/agate-json-get.py" index commands "$i" formatter)
```

> **注意**：`index` 的 `$i` 已加双引号 `"$i"`（bash 变量传参需引号防分词，原内联段用 `$i` 直接拼接进 python 代码，行为等价）。

- [ ] **Step 5: 验证 check-tdd-red 全部测试仍绿**

```bash
bats agate/tests/unit/check-tdd-red.bats agate/tests/unit/check-tdd-red-formatter.bats agate/tests/unit/agate-json-get.bats
```

Expected: 全部 PASS（`check-tdd-red.bats` 38 + `check-tdd-red-formatter.bats` 12 + `agate-json-get.bats` 6 = 56）。

---

### Task 4: 全量回归 + 一致性 + 用例数 + shellcheck

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

Expected: `0 ERROR`。（`agate-json-get.py` 不匹配锚点表 glob（`check-*.sh`/`pre-commit-gate.sh`/`ci-gate-backstop.py`），无新增协议引用 → 无 ERROR。）

- [ ] **Step 3: 用例数**

```bash
bash agate/tests/scripts/count-tests.sh
```

Expected: 原 545 + 6（JGET.1-6）= **551**。

- [ ] **Step 4: shellcheck**

```bash
shellcheck -S warning agate/scripts/*.sh
```

Expected: 无 error（薄壳无新增 shell 复杂度）。

---

### Task 5: 文档同步（README 逐脚本用例数）

**Files:**
- Modify: `agate/tests/README.md`

**背景**：新增 `agate-json-get.bats` 需在 README 逐脚本表登记。`check-tdd-red.sh` 行用例数不变（38，因为新增的是 JGET 进新文件，非 check-tdd-red.bats）。

- [ ] **Step 1: 定位 README 逐脚本表**

```bash
grep -n "check-tdd-red.sh\|ci-gate-backstop\|install-hook" agate/tests/README.md
```

Expected: 命中 `agate/tests/README.md` 逐脚本表邻近行。

- [ ] **Step 2: 新增 `agate-json-get.py` 行**

在 README 逐脚本表（`ci-gate-backstop.py` 行附近）插入：
```
| agate-json-get.py | unit/agate-json-get.bats | 6 |
```

> **注意**：总数行是 `以 count-tests.sh 输出为准`（自动推导），不需改。`check-tdd-red.sh` 行保持 38（JGET 用例进新文件，不改该行）。

---

### Task 6: commit（self-gate）

**Files:**
- 提交：`agate/scripts/agate-json-get.py`、`agate/scripts/check-tdd-red.sh`、`agate/tests/unit/agate-json-get.bats`、`agate/tests/README.md`

**背景**：触发文件含 `agate/scripts/*.py`、`agate/scripts/*.sh`、`agate/tests/*.bats` → commit-msg-self-gate hook 要求 `self-gate-review:`。

- [ ] **Step 1: 暂存并提交**

```bash
cd /home/kity/oclab/agate/.worktrees/py-extraction
git add agate/scripts/agate-json-get.py agate/scripts/check-tdd-red.sh agate/tests/unit/agate-json-get.bats agate/tests/README.md
git commit -m "feat(scripts): 新增共享 JSON 提取工具 agate-json-get.py，完成 check-tdd-red 抽离

新增 agate/scripts/agate-json-get.py：从 stdin 读 JSON，按子命令
(get/len/index/set/count_prefix) 提取/改写字段，统一 .sh 里散落的单行
python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get(...))' 内联段。
用该工具替换 check-tdd-red.sh 剩余 12 处单行 JSON 提取（该脚本 12 处内联清零）。
行为等价，既有 545 测试全绿。新增 JGET.1-6 直接测工具，总数 545→551。

self-gate-review: docs/plans/agate-py-extraction-shared-json-20260807.md"
```

Expected: commit 成功，commit-msg hook 识别 `self-gate-review:` 无 WARNING。

- [ ] **Step 2: 确认工作区干净**

```bash
git status
```

Expected: clean（仅 HANDOFF-PY-EXTRACTION.md 未跟踪，属预期）。

---

## 批次结论记录（实施后填写）

- **工具复用价值**：单行 JSON 提取是 14 脚本里最高频模式（约 20+ 处），`agate-json-get.py` 可批量复用。后续批次：agate-capture-env-baseline（get/len/index）、gate-result.sh（get + json.dumps 输出）、check-p6-provenance 等。
- **工作量**：本批消灭 check-tdd-red 12 处 + 落地共享工具，供后续批量复用。
- **遗留**：多行长块（P5 解析、YAML 解析、图像处理）仍需逐脚本独立 .py 抽离，不在本工具覆盖范围。
- **验证**：bats 全绿（557 ok）、count-tests 551、consistency 0 ERROR、shellcheck 0 error、后置评审 APPROVE（12/12 处等价映射确认）。