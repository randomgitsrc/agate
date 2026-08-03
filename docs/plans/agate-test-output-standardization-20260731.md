# 测试输出标准化（Tech-Stack Neutral Test Result Format）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 check-tdd-red.sh 和 agate-capture-env-baseline.sh 从"硬编码 pytest 输出解析"改为"解析标准 JSON 格式 + 可替换 formatter 适配层"，使 agate 协议真正技术栈无关。

**Architecture:** gate_commands.P3/P5 扩展可选 `formatter` 键。测试命令执行后，原始输出通过 formatter 脚本转为标准 JSON。agate 脚本只解析标准 JSON，不接触原始输出格式。不提供 formatter 时退化为 exit-code-only（所有红灯 = 可推进）。内置 6 个 formatter 模板覆盖主流框架，项目可自定义。同时修复 P6 截图 PNG-only 限制和文档中的 pytest 软绑定。

**Tech Stack:** Bash, Python 3 (formatter 内联), Bats (测试)

---

## 背景

### 问题

check-tdd-red.sh 有 4 个技术栈硬绑定：
1. pytest 作为最终回退（L81-89, L88-89）
2. `-q` 默认 flag（L96）
3. FAIL/ERROR/IMPORT pattern 默认值是 pytest 格式（L100-102）
4. agate-capture-env-baseline.sh `grep '^FAILED '` 提取失败列表（L59）

非 pytest 项目要配置 5+ 个环境变量（`TEST_RUNNER_FLAGS`、`TEST_FAIL_PATTERN`、`TEST_ERROR_PATTERN`、`TEST_IMPORT_PATTERN`、`PROJECT_MODULE`）才能工作。T079 中 vitest 因 `-q` flag 崩溃。

### 方案

**标准格式 + 可替换 formatter：**

```
test_command (gate_commands.P3/P5)
  → 原始输出
  → formatter 脚本
  → .test-result.json (标准格式)
  → check-tdd-red.sh / agate-capture-env-baseline.sh 解析
```

**标准 JSON 格式：**

```json
{
  "exit_code": 1,
  "total": 5,
  "passed": 0,
  "failed": 3,
  "errors": 1,
  "failed_tests": ["test_foo", "test_bar"],
  "import_errors": [
    {"module": "myapp.foo", "message": "ModuleNotFoundError: No module named 'myapp.foo'"}
  ],
  "syntax_errors": [
    {"file": "test_bar.py", "message": "SyntaxError: invalid syntax at line 10"}
  ]
}
```

**formatter 契约：**
- 输入：stdin = 测试命令原始输出，`$1` = exit code
- 输出：stdout = 一行 JSON
- exit 0 = 解析成功 / exit 1 = 解析失败（调用方退化为 exit-code-only）

**内置 formatter 模板（`agate/assets/formatters/`）：**
- `pytest.sh` — pytest 文本输出
- `vitest.sh` — vitest/jest 文本输出
- `go-test.sh` — go test / cargo test 文本输出
- `generic-tap.sh` — TAP 格式（bats/prove 等）
- `generic-junit-xml.sh` — JUnit XML（Maven/Gradle 等）
- `generic-exit-only.sh` — 只用 exit code（退路）

**gate_commands 扩展（P2-design.md）：**

```yaml
gate_commands:
  P3: "pytest"
  P3_formatter: "pytest.sh"          # 可选
  P5: "pytest -q --tb=no"
  P5_formatter: "pytest.sh"          # 可选
  P5_e2e: "playwright test ..."
  project_module: "myapp"             # 可选，B 类检测用
```

**check-tdd-red.sh 新逻辑：**

1. 从 gate_commands.P3 读取 test_command + formatter 路径
2. 执行 test_command（不加任何默认 flag），捕获原始输出 + exit code
3. 如果有 formatter：执行 `echo "$OUTPUT" | formatter $EXIT_CODE`
4. 如果没有 formatter：只看 exit code（0→绿/非0→红灯）
5. 解析 JSON：
   - exit_code == 0 → exit 2（绿灯）
   - syntax_errors 非空 → exit 1（A 类）
   - import_errors 中 module 匹配 project_module → exit 0（B 类）
   - import_errors 中 module 不匹配 project_module → exit 1（A 类）
   - 有 failed 但无 errors → exit 0（经典红灯）
   - 无 formatter 时退化为 exit-code-only

**多技术栈支持：** gate_commands 支持多个 P3* 键（如 P3、P3_js），每个独立跑+独立 format，结果汇总。

### A/B 类区分的保留逻辑

| 场景 | 判定 | 依据 |
|------|------|------|
| exit_code=0 | 绿灯 exit 2 | 所有测试通过 |
| 有 syntax_errors | A 类 exit 1 | 测试代码自身语法错误 |
| import_errors 的 module 匹配 project_module | B 类 exit 0 | 被测代码未实现 |
| import_errors 的 module 不匹配 project_module | A 类 exit 1 | 测试代码 import 了不存在的第三方 |
| 有 failed 但无 errors | 经典红灯 exit 0 | assertion failure |
| 无 formatter | exit-code-only | 退化为最简模式 |

### 向后兼容

- `TEST_RUNNER` 环境变量保留（最高优先级覆盖，退化为 exit-code-only，**不再有 A/B 类检测**——A/B 类检测移至 formatter 路径。迁移建议：项目在 gate_commands 中声明 P3_formatter 恢复 A/B 类检测）
- `gate_commands.P3` 保留（声明 test_command）
- `PROJECT_MODULE` 环境变量保留（向后兼容），新推荐在 gate_commands 中声明 `project_module`
- `TEST_RUNNER_FLAGS` / `TEST_FAIL_PATTERN` / `TEST_ERROR_PATTERN` / `TEST_IMPORT_PATTERN` 废弃
- 不提供 formatter 时退化为 exit-code-only，不会比旧方案更差
- pytest 回退保留（向后兼容，但不再推荐，不作为主要路径，退化为 exit-code-only）

### 关键设计约束：gate_commands 正则排除 formatter 键

`P3_formatter` / `P5_formatter` 键会被 `P3\w*` / `P5\w*` 正则匹配为命令键。**必须在读取 gate_commands 的 Python 代码中排除 `*_formatter` 键**，否则 formatter 文件名会被当作测试命令执行。

实现方式：在 Python 正则中用 `P3(?!_formatter)\w*` 负向先行断言，或在读取后用 `if not key.endswith('_formatter')` 过滤。

---

## 文件结构

### 新增文件

| 文件 | 职责 |
|------|------|
| `agate/assets/formatters/pytest.sh` | pytest 输出 → 标准 JSON |
| `agate/assets/formatters/vitest.sh` | vitest/jest 输出 → 标准 JSON |
| `agate/assets/formatters/go-test.sh` | go test / cargo test 输出 → 标准 JSON |
| `agate/assets/formatters/generic-tap.sh` | TAP 格式 → 标准 JSON |
| `agate/assets/formatters/generic-junit-xml.sh` | JUnit XML → 标准 JSON |
| `agate/assets/formatters/generic-exit-only.sh` | 只用 exit code → 标准 JSON |
| `agate/assets/formatters/README.md` | formatter 契约说明 + 速查表 |
| `agate/tests/unit/check-tdd-red-formatter.bats` | formatter 单元测试 |

### 修改文件

| 文件 | 改动 |
|------|------|
| `agate/scripts/check-tdd-red.sh` | 重写：去默认 flag/pattern 默认值，改为 formatter+JSON 解析 |
| `agate/scripts/agate-capture-env-baseline.sh` | 改 fail-list 提取：用 formatter+JSON 代替 `grep '^FAILED '` |
| `agate/scripts/check-p6-evidence.sh` | 放宽截图格式检查：PNG magic → `file` 命令判断任意图片格式 |
| `agate/scripts/check-protocol-consistency.py` | CHECK 9 关键字从 `pytest` 改为 `formatter` |
| `agate/scripts/check-gate.sh` | P7 DESIGN_GAP 正则放宽（附带修复 T083） |
| `agate/phase-cards/P3-tdd.md` | 更新 gate 规则说明：formatter 探测链 |
| `agate/phase-cards/P5-verification.md` | 更新 fail-list.txt 产出说明 |
| `agate/phase-cards/P0-orchestrator.md` | 环境自检：pytest/vitest → 通用"测试框架" |
| `agate/assets/execution-roles/architect.md` | gate_commands 示例 + formatter 速查表 |
| `agate/assets/execution-roles/verifier.md` | 更新非 pytest 技术栈说明 |
| `agate/assets/execution-roles/test-designer.md` | 加 vitest mock hoisting 反模式清单（T079） |
| `agate/assets/templates/task-files.md` | gate_commands 模板更新 + 修正"pytest 为准"文档 bug |
| `agate/state-machine.md` | 更新嵌入式 check-tdd-red.sh 代码块 |
| `agate/tests/unit/check-tdd-red.bats` | 适配新逻辑：废弃 pattern 环境变量测试，加 formatter 测试 |
| `agate/tests/unit/agate-capture-env-baseline.bats` | 适配新逻辑 |
| `docs/hardening-roadmap.md` | 新增 P2.51 条目 |

---

## Task 1: 创建 formatter 契约说明 + 速查表

**Files:**
- Create: `agate/assets/formatters/README.md`

- [ ] **Step 1: 写 formatter 契约文档**

内容包含：formatter 契约（输入 stdin + $1 exit code，输出一行 JSON）、标准 JSON 格式字段说明（exit_code/total/passed/failed/errors/failed_tests/import_errors/syntax_errors）、速查表（pytest→pytest.sh, vitest→vitest.sh, go test→go-test.sh, cargo test→go-test.sh, bats→generic-tap.sh, Maven/Gradle→generic-junit-xml.sh, 其他→generic-exit-only.sh）、在 gate_commands 中声明的示例、formatter 路径解析规则（相对路径先找 .agate/formatters/ 再找 agate/assets/formatters/，绝对路径直接用）、多技术栈声明示例（P3 + P3_js）、自定义 formatter 说明。

- [ ] **Step 2: Commit**

```bash
git add agate/assets/formatters/README.md
git commit -m "docs: add formatter contract and lookup table for test result standardization"
```

---

## Task 2: 创建 generic-exit-only.sh formatter

**Files:**
- Create: `agate/assets/formatters/generic-exit-only.sh`
- Create: `agate/tests/unit/check-tdd-red-formatter.bats`

- [ ] **Step 1: 写 generic-exit-only.sh**

脚本逻辑：读 `$1` 作为 exit_code，stdin 忽略，输出 `{"exit_code":N,"total":0,"passed":0,"failed":0,"errors":0,"failed_tests":[],"import_errors":[],"syntax_errors":[]}`。用内联 python3 生成 JSON。

- [ ] **Step 2: 写测试 — 创建 check-tdd-red-formatter.bats**

FMT.1: generic-exit-only.sh exit 1 → JSON with exit_code=1, empty arrays
FMT.2: generic-exit-only.sh exit 0 → JSON with exit_code=0

- [ ] **Step 3: 运行测试验证通过**

Run: `bats agate/tests/unit/check-tdd-red-formatter.bats`
Expected: PASS (2 tests)

- [ ] **Step 4: Commit**

---

## Task 3: 创建 pytest.sh formatter

**Files:**
- Create: `agate/assets/formatters/pytest.sh`
- Modify: `agate/tests/unit/check-tdd-red-formatter.bats`（追加）

- [ ] **Step 1: 写 pytest.sh**

脚本用内联 python3 解析 pytest 输出：
- 摘要行：`(\d+) passed`, `(\d+) failed`, `(\d+) error`
- 失败测试 ID：`^FAILED (\S+)` 行
- import 错误：`(?:ImportError|ModuleNotFoundError)` 行，提取模块名
- 语法错误：`(SyntaxError|IndentationError)` 行

- [ ] **Step 2: 追加测试**

FMT.3: pytest.sh classic red-light (2 failed, 5 passed) → failed=2, passed=5, errors=0, failed_tests 含 2 项
FMT.4: pytest.sh B-class (ImportError from project module myapp.foo) → import_errors[0].module == "myapp.foo"
FMT.5: pytest.sh A-class (SyntaxError) → syntax_errors 非空
FMT.6: pytest.sh all passed (exit 0) → passed=5, failed=0

- [ ] **Step 3: 运行测试验证通过**

Run: `bats agate/tests/unit/check-tdd-red-formatter.bats`
Expected: PASS (6 tests)

- [ ] **Step 4: Commit**

---

## Task 4: 创建 vitest.sh formatter

**Files:**
- Create: `agate/assets/formatters/vitest.sh`
- Modify: `agate/tests/unit/check-tdd-red-formatter.bats`（追加）

- [ ] **Step 1: 写 vitest.sh**

脚本用内联 python3 解析 vitest/jest 输出：
- 摘要行：`Tests\s+(\d+)\s+failed`, `Tests\s+(\d+)\s+passed`, `Failed Suites\s+(\d+)`
- 失败测试名：`^FAIL\s+(\S+)` 行
- import 错误：`Cannot find (?:module|package) ['"]([^'"]+)` 
- 语法错误：`(SyntaxError|ParseError|Unexpected token)`

- [ ] **Step 2: 追加测试**

FMT.7: vitest.sh pure assertion failure (11 failed, 6 passed) → failed=11, errors=0, import_errors=[]
FMT.8: vitest.sh B-class (Cannot find module '../src/bar') → import_errors[0].module == "../src/bar"
FMT.9: vitest.sh A-class (Cannot find module 'react') → import_errors[0].module == "react"

- [ ] **Step 3: 运行测试验证通过**

Run: `bats agate/tests/unit/check-tdd-red-formatter.bats`
Expected: PASS (9 tests)

- [ ] **Step 4: Commit**

---

## Task 5: 创建 go-test.sh + generic-tap.sh + generic-junit-xml.sh

**Files:**
- Create: `agate/assets/formatters/go-test.sh`
- Create: `agate/assets/formatters/generic-tap.sh`
- Create: `agate/assets/formatters/generic-junit-xml.sh`
- Modify: `agate/tests/unit/check-tdd-red-formatter.bats`（追加）

- [ ] **Step 1: 写 go-test.sh**

解析 go test / cargo test 输出：
- 摘要：`(\d+)\s+passed`, `(\d+)\s+failed`
- 失败行 go：`--- FAIL:\s+(\S+)`；cargo：`test\s+(\S+)\s+\.\.\.\s+FAILED`
- import 错误：`cannot find "([^"]+)"`, `unresolved import\s+(\S+)`
- 语法错误：`syntax error`, `parse error`

- [ ] **Step 2: 写 generic-tap.sh**

解析 TAP 格式：
- 统计 `^ok` 和 `^not ok` 行数
- 失败测试名：`^not ok\s+\d+\s*-?\s*(.+)`

- [ ] **Step 3: 写 generic-junit-xml.sh**

解析 JUnit XML：
- 从属性提取：`tests="N"`, `failures="N"`, `errors="N"`
- 失败 testcase：`<testcase>` 含 `<failure>` 或 `<error>`

- [ ] **Step 4: 追加测试**

FMT.10: go-test.sh cargo test format (2 passed, 1 failed) → passed=2, failed=1, failed_tests 含 "foo::test_bar"
FMT.11: generic-tap.sh bats output (2 ok, 1 not ok) → passed=2, failed=1, failed_tests 含 "test gamma"
FMT.12: generic-junit-xml.sh basic XML (tests=3, failures=1, errors=1) → total=3, failed=1, errors=1, passed=1

- [ ] **Step 5: 运行测试验证通过**

Run: `bats agate/tests/unit/check-tdd-red-formatter.bats`
Expected: PASS (12 tests)

- [ ] **Step 6: shellcheck 所有 formatter**

Run: `shellcheck -S warning agate/assets/formatters/*.sh`
Expected: 0 errors

- [ ] **Step 7: Commit**

---

## Task 5.5: 在 gate-result.sh 中提取公共 formatter 函数

**Files:**
- Modify: `agate/scripts/gate-result.sh`

- [ ] **Step 1: 新增 resolve_formatter() 和 run_test_with_formatter() 函数**

在 gate-result.sh 末尾追加。

> **语义冲突说明**：`gate-result.sh` 当前在 `check-protocol-consistency.py` 的 `GATE_SCRIPT_EXEMPT` 白名单中标注为"无 gate 逻辑，不需要锚点"。新增的 formatter 公共函数是 A/B 类判定链路的核心逻辑，但函数本身受 check-tdd-red.sh / agate-capture-env-baseline.sh 的测试覆盖，不需要独立锚点。执行 Task 9 时更新 `GATE_SCRIPT_EXEMPT` 旁的注释，说明"本文件也承载 formatter 公共函数，受调用方测试覆盖"。

```bash
# --- formatter 公共函数 ---
resolve_formatter() {
    local fmt="$1"
    local task_dir="${2:-}"
    local agate_root="${AGATE_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]})/.." && pwd)}"
    [ "${fmt:0:1}" = "/" ] && { [ -f "$fmt" ] && echo "$fmt" || return 1; }
    if [ -n "$task_dir" ] && [ -f "$task_dir/.agate/formatters/$fmt" ]; then
        echo "$task_dir/.agate/formatters/$fmt"
    elif [ -f "$agate_root/assets/formatters/$fmt" ]; then
        echo "$agate_root/assets/formatters/$fmt"
    else
        return 1
    fi
}

run_test_with_formatter() {
    local cmd="$1"
    local fmt_path="$2"  # 可空
    local exit_code output
    output=$(eval "$cmd" 2>&1) && exit_code=0 || exit_code=$?
    if [ -z "$fmt_path" ]; then
        echo "{\"exit_code\":$exit_code,\"total\":0,\"passed\":0,\"failed\":0,\"errors\":0,\"failed_tests\":[],\"import_errors\":[],\"syntax_errors\":[]}"
    else
        local json_result
        json_result=$(echo "$output" | bash "$fmt_path" "$exit_code" 2>/dev/null) || {
            echo "{\"exit_code\":$exit_code,\"total\":0,\"passed\":0,\"failed\":0,\"errors\":0,\"failed_tests\":[],\"import_errors\":[],\"syntax_errors\":[]}"
        }
        echo "$json_result"
    fi
}
```

- [ ] **Step 2: Commit**

---

## Task 6: 重写 check-tdd-red.sh — formatter + JSON 解析

**Files:**
- Modify: `agate/scripts/check-tdd-red.sh`（重写）
- Modify: `agate/tests/unit/check-tdd-red.bats`（适配 + 追加 formatter 测试）

> **关键设计约束**：read_gate_commands() 的 Python 正则必须排除 `*_formatter` 键。用 `^  (P3(?!_formatter)\w*):` 或读取后 `if not key.endswith('_formatter')` 过滤。否则 `P3_formatter` 的值（如 `pytest.sh`）会被当作测试命令执行。

- [ ] **Step 1: 先写失败测试 — TDD.F 系列（formatter 集成）**

在 `check-tdd-red.bats` 末尾追加 10 个新测试：

TDD.F1: gate_commands.P3 + P3_formatter → auto-read both, classic red-light exit 0
TDD.F2: gate_commands.P3 without formatter → exit-code-only, red-light exit 0
TDD.F3: formatter detects B-class (import from project_module) → exit 0 + "B-class"
TDD.F4: formatter detects A-class (SyntaxError) → exit 1 + "A-class"
TDD.F5: formatter detects A-class (import NOT from project_module) → exit 1 + "A-class"
TDD.F6: green light (exit 0) → exit 2
TDD.F7: TEST_RUNNER env var still works (backward compat, exit-code-only) → exit 0
TDD.F8: no TEST_RUNNER, no gate_commands.P3, no pytest → exit 3
TDD.F9: no formatter → command runs without -q (验证不追加任何 flag)
TDD.F10: multi-stack P3 + P3_js → both run, combined result → exit 0

每个测试构造 task_dir + P2-design.md（含 gate_commands 声明 P3/P3_formatter/project_module），用 make_fake_pytest 造 mock runner，env -u 清除废弃环境变量。

- [ ] **Step 2: 运行新测试验证失败**

Run: `bats agate/tests/unit/check-tdd-red.bats --filter "TDD.F"`
Expected: FAIL（脚本还没改）

- [ ] **Step 3: 重写 check-tdd-red.sh**

完整替换脚本内容。核心结构：

1. **头部注释**：更新为"技术栈无关"说明，废弃环境变量标注，新 gate_commands 键说明
2. **read_gate_commands()**：读 P2-design.md 的 gate_commands 块，提取所有 P3* 命令 + 对应 formatter + project_module，返回 JSON
3. **source gate-result.sh**：调用 Task 5.5 提取的公共函数 resolve_formatter() 和 run_test_with_formatter()，不重复定义
4. **judge_result()**：解析 JSON 判定——exit_code==0→return 2; syntax_errors 非空→return 1; import_errors 匹配 project_module→return 0; 不匹配→return 1; errors>0 非 import→return 1; failed>0 errors==0→return 0; 兜底→return 0
5. **主逻辑**：收集命令（TEST_RUNNER > gate_commands.P3* > pytest 回退 > exit 3），逐个执行+判定，worst exit wins（2>1>0）

保留的向后兼容：
- TEST_RUNNER 环境变量（退化为 exit-code-only，无 formatter）
- PROJECT_MODULE 环境变量（覆盖 gate_commands 的 project_module）
- pytest 回退（向后兼容，但不再推荐）

删除的：
- `RUNNER_FLAGS="${TEST_RUNNER_FLAGS--q}"` — 不再追加任何 flag
- `FAIL_PATTERN` / `ERROR_PATTERN` / `IMPORT_PATTERN` 默认值和环境变量
- 输出解析逻辑（grep FAIL_PATTERN 等）

- [ ] **Step 4: 适配旧测试**

旧测试适配策略：
- **TD.1**: 保留（TEST_RUNNER 不存在 → exit 1 兜底）
- **TD.1b**: 保留（exit 3）
- **TD.2**: 保留（TEST_RUNNER + exit 0 → exit 2 绿灯）
- **TD.3**: 保留，断言改为 `[[ "$output" == *"red-light"* ]]`（不再有 "classic red-light"）
- **TD.4-TD.8**: 标记 `# DEPRECATED: pattern-based tests, replaced by TDD.F*`。新逻辑 TEST_RUNNER 路径无 formatter → exit-code-only。所有红灯 exit 0。断言改为 `[ "$status" -eq 0 ]`，去掉 B-class/A-class 输出检查
- **TDD.N1**: 保留（验证不加 -q，新逻辑天然满足）
- **TDD.N1b**: 删除（TEST_RUNNER_FLAGS 不再存在）
- **TDD.N2-N4**: 标记废弃，断言改为退化行为（exit 0）
- **TDD.G1**: 断言改为 `[[ "$output" == *"red-light"* ]]`
- **TDD.G2-G5**: 类似适配

- [ ] **Step 5: 运行全部 check-tdd-red 测试验证通过**

Run: `bats agate/tests/unit/check-tdd-red.bats`
Expected: PASS

- [ ] **Step 6: shellcheck**

Run: `shellcheck -S warning agate/scripts/check-tdd-red.sh`
Expected: 0 errors

- [ ] **Step 7: Commit**

---

## Task 7: 修改 agate-capture-env-baseline.sh — 用 formatter 提取 fail-list

**Files:**
- Modify: `agate/scripts/agate-capture-env-baseline.sh`
- Modify: `agate/tests/unit/agate-capture-env-baseline.bats`

- [ ] **Step 1: 先写失败测试 — EB.13-EB.15**

EB.13: gate_commands.P5 + P5_formatter: pytest.sh → fail-list 从 JSON 提取，写入 pre-task-baseline.md
EB.14: gate_commands.P5 无 formatter → WARNING，不写文件
EB.15: vitest P5 + P5_formatter: vitest.sh → fail-list 提取

- [ ] **Step 2: 运行新测试验证失败**

Run: `bats agate/tests/unit/agate-capture-env-baseline.bats --filter "EB.1[345]"`
Expected: FAIL

- [ ] **Step 3: 修改 agate-capture-env-baseline.sh**

核心改动：
1. 新增读取 P5_formatter 声明（与 P5 命令配对）
2. 缓存 key 加入 formatter 声明
3. 替换 L46-68 的 `grep '^FAILED '` + `FAIL_PATTERN` 逻辑为 formatter+JSON 解析（source gate-result.sh 使用公共函数）
4. 无 formatter → WARNING + skip（与旧逻辑 parse failure 行为一致）

**关键设计约束**：L29 的正则 `^  (P5\w*):` 会匹配 `P5_formatter`。必须排除 formatter 键。修改正则为 `^  (P5(?!_formatter)\w*):` 或读取后过滤 `if not key.endswith('_formatter')`。

具体修改点：
- P5 命令读取（L21-32）保留不动，用于缓存 key
- 缓存 key（L35）加入 P5_formatter 信息
- fail-list 提取（L46-68）整块替换：
  - 对每个 P5 命令，查找对应的 P5_formatter
  - 执行命令，用 formatter 转成 JSON
  - 从 JSON 提取 failed_tests 列表
  - 无 formatter → WARNING + break

- [ ] **Step 4: 适配旧测试 EB.4-EB.10**

旧测试的 P2-design.md 没有声明 `P5_formatter`，新逻辑会 WARNING + skip。需要给这些测试的 P2 内容加上 `P5_formatter: pytest.sh`。

逐个修改 EB.4-EB.10 的 `setup_git_repo_with_p2` 调用，在 P2 内容中加 `P5_formatter: pytest.sh`。EB.10 使用 P5 + P5_e2e，需要两个都加。

- [ ] **Step 5: 运行全部 baseline 测试验证通过**

Run: `bats agate/tests/unit/agate-capture-env-baseline.bats`
Expected: PASS

- [ ] **Step 6: shellcheck**

Run: `shellcheck -S warning agate/scripts/agate-capture-env-baseline.sh`
Expected: 0 errors

- [ ] **Step 7: Commit**

---

## Task 8: 放宽 check-p6-evidence.sh 截图格式

**Files:**
- Modify: `agate/scripts/check-p6-evidence.sh:88-97`

- [ ] **Step 1: 修改 PNG-only 检查为通用图片格式检查**

找到 L88-97 的 PNG header 检查块。将 `HEADER=$(head -c 8 ...)` + `EXPECTED='89504e470d0a1a0a'` 替换为用 `file -b --mime-type` 判断是否为 `image/*` 类型。**加 fallback**：如果 `file` 命令不存在，回退到检查常见图片 magic bytes（PNG/JPEG/GIF/WebP）。

变量名更新：`PNG_WARNING` → `SMALL_IMAGE_WARNING`，`PNG_DETAILS` → `SMALL_IMAGE_DETAILS`。更新后续引用这些变量的行（L128-136）。消息文本更新：`非 PNG 文件 ≤ 1KB` → `非图片文件 ≤ 1KB`，`合法 PNG ≤ 1KB` → `合法图片 ≤ 1KB`。

- [ ] **Step 2: 运行 P6 evidence 测试验证通过**

Run: `bats agate/tests/unit/check-p6-evidence.bats`
Expected: PASS

- [ ] **Step 3: Commit**

---

## Task 9: 更新 check-protocol-consistency.py CHECK 9

**Files:**
- Modify: `agate/scripts/check-protocol-consistency.py:537-538`

- [ ] **Step 1: 更新 CHECK 9 关键字**

将 L538 的 `"keywords": ["pytest"]` 改为 `"keywords": ["formatter", "pytest"]`（双关键字监控：确保脚本包含 formatter 逻辑 + 保留 pytest 回退）

- [ ] **Step 2: 更新 GATE_SCRIPT_EXEMPT 注释**

找到 `gate-result.sh` 在 `GATE_SCRIPT_EXEMPT` 白名单中的条目，更新注释为"无 gate 逻辑 + formatter 公共函数（受调用方测试覆盖），不需要锚点"。

- [ ] **Step 3: 运行一致性检查**

Run: `python3 agate/scripts/check-protocol-consistency.py`
Expected: 0 ERROR

- [ ] **Step 4: Commit**

---

## Task 10: 修复 check-gate.sh P7 DESIGN_GAP 正则（T083 附带修复）

**Files:**
- Modify: `agate/scripts/check-gate.sh:249,260`

- [ ] **Step 1: 先写失败测试 — blockquote 格式 DESIGN_GAP**

在 P7 相关测试文件中追加一个测试用例：P7-consistency.md 中使用 markdown blockquote 格式的 `[DESIGN_GAP:]` 应被正则匹配。这个测试在当前正则下会失败。

- [ ] **Step 2: 放宽 DESIGN_GAP 正则**

L249: `'^\s*-?\s*\[DESIGN_GAP:'` → `'^\s*>?\s*-?\s*\[DESIGN_GAP:'`（加 `>?` 匹配 markdown blockquote）

> **注意**：L260 的 `grep -rh '\[DESIGN_GAP:'` 没有 `^\s*-?\s*` 锚点（它扫描多文件汇总计数，不是单文件逐行判定），本身不受行首格式影响，**不需要同款修改**。

- [ ] **Step 3: 运行 P7 测试**

Run: `bats agate/tests/unit/check-gate.bats`
Expected: PASS

- [ ] **Step 4: Commit**

---

## Task 11: 更新协议文档 — P3-tdd.md / P5-verification.md / P0-orchestrator.md

**Files:**
- Modify: `agate/phase-cards/P3-tdd.md`
- Modify: `agate/phase-cards/P5-verification.md`
- Modify: `agate/phase-cards/P0-orchestrator.md`

- [ ] **Step 1: 更新 P3-tdd.md gate 规则说明**

将 L39-50 替换为：gate 规则说明中"技术栈无关"说明、formatter 探测链、formatter 选择速查表引用（assets/formatters/README.md）

- [ ] **Step 2: 更新 P5-verification.md**

L58-60: fail-list.txt 产出说明改为"使用 gate_commands.P5_formatter 声明的 formatter 提取"
L39: 非 pytest 技术栈说明改为"gate_commands.P5_formatter 声明 formatter（可选），见 assets/formatters/README.md 速查表"

- [ ] **Step 3: 更新 P0-orchestrator.md 环境自检**

L33: `测试框架可用（pytest/vitest --version）` → `测试框架可用（项目使用的测试框架，如 pytest/vitest/go test/cargo test --version）`

- [ ] **Step 4: Commit**

---

## Task 12: 更新角色文件 — architect.md / verifier.md / test-designer.md

**Files:**
- Modify: `agate/assets/execution-roles/architect.md`
- Modify: `agate/assets/execution-roles/verifier.md`
- Modify: `agate/assets/execution-roles/test-designer.md`

- [ ] **Step 1: 更新 architect.md gate_commands 示例**

L41-47: gate_commands 示例加 `P3_formatter`, `P5_formatter`, `project_module` 键
L47: P3 键说明改为 formatter 说明 + 速查表引用 + project_module 说明

- [ ] **Step 2: 更新 verifier.md 非 pytest 技术栈说明**

L158: 替换为"技术栈无关：gate_commands.P5_formatter 声明 formatter（可选），见 assets/formatters/README.md"

- [ ] **Step 3: 更新 test-designer.md — 加 vitest mock hoisting 反模式清单**

在 L43（质量门槛节末尾）追加 vitest mock hoisting 反模式说明（T079 教训）：vi.mock() hoisting 行为、正确做法（字符串字面量、vi.doMock in beforeEach）

- [ ] **Step 4: Commit**

---

## Task 13: 更新模板 — task-files.md + state-machine.md + dispatch-prompt.md

**Files:**
- Modify: `agate/assets/templates/task-files.md`
- Modify: `agate/assets/templates/dispatch-prompt.md`
- Modify: `agate/state-machine.md`

- [ ] **Step 1: 修正 task-files.md 文档 bug + 更新模板**

L33: "gate 以主 Agent 跑 pytest 为准" → "gate 以主 Agent 跑 gate_commands.P5 为准"
L65: "主 Agent 跑 `pytest -q` 验证" → "主 Agent 跑 `gate_commands.P5` 验证"
L210-221: gate_commands 模板加 P3_formatter/P5_formatter/project_module 键 + 注释引用 assets/formatters/README.md

- [ ] **Step 2: 清理 dispatch-prompt.md pytest 引用**

L130: "P6 verifier 交付的验证脚本（Playwright / shell / pytest）应由主 Agent 执行。" → "P6 verifier 交付的验证脚本（Playwright / shell / 测试框架）应由主 Agent 执行。"
验证 dispatch-prompt.md 无 gate_commands YAML 块（只有表格引用），CHECK 4 不受影响。

- [ ] **Step 3: 更新 state-machine.md 嵌入式代码块**

L276-366: 嵌入式 check-tdd-red.sh 代码块更新为新的 formatter+JSON 逻辑摘要（不需要完整复制脚本，只更新关键逻辑描述和判定方式说明）

- [ ] **Step 4: Commit**

---

## Task 14: 更新 hardening-roadmap.md + 全量验证

**Files:**
- Modify: `docs/hardening-roadmap.md`

- [ ] **Step 1: 新增 P2.51 条目**

在 v0.25.0 条目后新增：

```markdown
### v0.26.0 — 测试输出标准化（Tech-Stack Neutral）

**P2.51: check-tdd-red.sh + agate-capture-env-baseline.sh 技术栈无关化**

**状态**：已实施
**来源**：T079+T082+T083 复盘（check-tdd-red.sh 技术栈绑定问题）
**改动**：
- check-tdd-red.sh 重写：废弃 pytest pattern 默认值/-q flag，改为 formatter+JSON 标准格式
- agate-capture-env-baseline.sh：fail-list 提取改用 formatter+JSON
- 新增 6 个内置 formatter 模板（pytest/vitest/go-test/generic-tap/generic-junit-xml/generic-exit-only）
- gate_commands 扩展：P3_formatter/P5_formatter/project_module 可选键
- 多技术栈支持：P3 + P3_js 多键声明
- check-p6-evidence.sh：截图格式从 PNG-only 放宽为任意图片格式
- check-gate.sh：P7 DESIGN_GAP 正则放宽匹配 markdown blockquote（T083 修复）
- 文档全面去 pytest 软绑定
```

- [ ] **Step 2: 全量测试**

Run: `bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/`
Expected: ALL PASS

- [ ] **Step 3: 一致性检查**

Run: `python3 agate/scripts/check-protocol-consistency.py`
Expected: 0 ERROR

- [ ] **Step 4: shellcheck**

Run: `shellcheck -S warning agate/scripts/*.sh agate/assets/formatters/*.sh`
Expected: 0 errors

- [ ] **Step 5: 测试用例计数 + 更新 tests/README.md 覆盖度表**

Run: `bash agate/tests/scripts/count-tests.sh`
Expected: 计数增加（新加 formatter 测试 + TDD.F 系列）

更新 `agate/tests/README.md` L40 的覆盖度表：`check-tdd-red.sh | unit/check-tdd-red.bats | 9` → 新数字，新增 `check-tdd-red-formatter.bats` 行。

- [ ] **Step 6: Commit**

```bash
git add docs/hardening-roadmap.md
git commit -m "docs: add P2.51 to hardening roadmap — test output standardization"
```

---

## Self-Review

### 评审修改记录

Plan 经过独立评审后修复了以下问题：

| 问题 | 严重度 | 修复 |
|------|--------|------|
| S7/S8: P5_formatter/P3_formatter 被正则匹配为命令 | BLOCKER | 在读取代码中排除 *_formatter 键 |
| B2: TEST_RUNNER 路径丧失 A/B 类检测 | BLOCKER | 接受为有意为之，A/B 检测移至 formatter 路径 |
| S1: formatter 逻辑应提取公共函数 | SHOULD_FIX | 新增 Task 5.5，在 gate-result.sh 中提取 |
| S2: file 命令缺少 fallback | SHOULD_FIX | Task 8 加 command -v file 检查 + magic bytes 回退 |
| S3: tests/README.md 覆盖度表未更新 | SHOULD_FIX | Task 14 加更新步骤 |
| S4: DESIGN_GAP 正则修改缺少 TDD | SHOULD_FIX | Task 10 先写 blockquote 失败测试 |
| S5: dispatch-prompt.md pytest 引用未清理 | SHOULD_FIX | Task 13 加清理步骤 |
| S6: CHECK 9 应保留 pytest 监控 | SHOULD_FIX | 改为 ["formatter", "pytest"] 双关键字 |
| B1: CHECK 4 dispatch-prompt.md | 已验证无风险 | dispatch-prompt.md 无 gate_commands YAML 块 |

### 1. Spec coverage

| 需求 | 对应 Task |
|------|----------|
| check-tdd-red.sh 去 pytest 绑定 | Task 6 |
| agate-capture-env-baseline.sh 去 pytest 绑定 | Task 7 |
| 6 个内置 formatter | Task 2-5 |
| gate_commands 扩展 (P3_formatter 等) | Task 6 (脚本读取) + Task 11-13 (文档) |
| 多技术栈支持 (P3 + P3_js) | Task 6 (TDD.F10 测试) |
| 向后兼容 (TEST_RUNNER, PROJECT_MODULE) | Task 6 (保留) |
| 废弃环境变量 (TEST_RUNNER_FLAGS 等) | Task 6 (删除) + Task 6 测试适配 |
| 公共 formatter 函数 | Task 5.5 |
| P6 截图格式放宽 | Task 8 |
| CHECK 9 关键字更新 | Task 9 |
| P7 DESIGN_GAP 正则修复 (T083) | Task 10 |
| 文档 pytest 软绑定清理 | Task 11-13 |
| dispatch-prompt.md 清理 | Task 13 |
| tests/README.md 更新 | Task 14 |
| roadmap 更新 | Task 14 |
| gate_commands 正则排除 formatter 键 | Task 6 + Task 7 (关键设计约束) |

### 2. Placeholder scan

无 TBD/TODO/"implement later"。所有 step 含具体代码或具体修改指令。

### 3. Type consistency

- `formatter` 路径解析函数在 check-tdd-red.sh 和 agate-capture-env-baseline.sh 中逻辑一致
- 标准 JSON 格式在所有 formatter 中一致
- `project_module` 在 gate_commands 和环境变量中语义一致
- `P3_formatter` / `P5_formatter` 命名规则一致（P{N}_formatter）

---

## Execution Handoff

Plan complete and saved to `docs/plans/agate-test-output-standardization-20260731.md`. Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
