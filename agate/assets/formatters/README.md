# Test Output Formatter Contract

agate 协议通过 **formatter 适配层**实现技术栈无关的测试输出解析。每个 formatter 将特定测试运行器的原始输出转换为统一 JSON 格式，供 `check-tdd-red.py` 等 gate 脚本消费。

## 契约

| 项目 | 说明 |
|------|------|
| **输入** | stdin = 测试原始输出（stdout+stderr 合并）；`$1` = 测试运行器 exit code |
| **输出** | stdout = 一行 JSON（紧凑格式，末尾换行） |
| **退出码** | `0` = 解析成功；`1` = 解析失败（formatter 自身出错） |

## 标准 JSON 格式

```json
{
  "exit_code": 1,
  "total": 7,
  "passed": 5,
  "failed": 2,
  "errors": 0,
  "failed_tests": ["tests/test_a.py::test_one", "tests/test_b.py::test_two"],
  "import_errors": [
    {"module": "myapp.foo", "message": "cannot import name 'Bar' from 'myapp.foo'"}
  ],
  "syntax_errors": [
    {"file": "tests/test_x.py", "message": "SyntaxError: invalid syntax"}
  ]
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `exit_code` | `int` | 测试运行器原始退出码（`$1` 传入） |
| `total` | `int` | 测试总数（passed + failed + errors）。formatter 无法从输出中提取时为 `0` |
| `passed` | `int` | 通过的测试数 |
| `failed` | `int` | assertion 失败的测试数 |
| `errors` | `int` | collection/fixture/setup 错误数（非 assertion 失败） |
| `failed_tests` | `string[]` | 失败测试的标识符（文件路径、测试名等） |
| `import_errors` | `object[]` | import/依赖缺失错误，每项含 `module`（缺失模块名）和 `message`（原始错误行） |
| `syntax_errors` | `object[]` | 语法/编译错误，每项含 `file`（文件路径，可为空字符串）和 `message`（原始错误行） |

## 速查表

| 测试运行器 | formatter | 备注 |
|-----------|-----------|------|
| pytest | `pytest.sh` | Python 标准格式 |
| vitest / jest | `vitest.sh` | JS/TS 生态 |
| go test | `go-test.sh` | Go 原生 + cargo test 共用 |
| cargo test | `go-test.sh` | Rust，输出格式与 go test 相似 |
| bats | `generic-tap.sh` | TAP 协议格式 |
| Maven / Gradle | `generic-junit-xml.sh` | JUnit XML surefire 报告 |
| 其他 | `generic-exit-only.sh` | 退路：只用 exit code，不解析输出 |

## gate_commands 声明

在 `P2-design.md` 的 `gate_commands` 中声明 formatter：

```yaml
gate_commands:
  P3: "pytest -q"
  P3_formatter: "pytest.sh"
  P5: "pytest -q --tb=no"
  P5_formatter: "pytest.sh"
  project_module: "myapp"
```

| 键 | 说明 |
|----|------|
| `P3_formatter` / `P5_formatter` | formatter 脚本路径或名称 |
| `project_module` | 项目模块前缀，用于 B 类检测（区分项目内 import vs 第三方 import） |

未声明 `P3_formatter` 时，gate 脚本回退到 `generic-exit-only.sh`。

## formatter 路径解析规则

```
1. 绝对路径（以 / 开头）→ 直接使用
2. 相对路径/纯文件名：
   a. 先找 .agate/formatters/<name>（项目自定义）
   b. 再找 {agate_root}/assets/formatters/<name>（内置）
3. 找不到 → 回退 generic-exit-only.sh
```

项目可在 `.agate/formatters/` 放自定义 formatter 覆盖内置版本。

## 多技术栈声明

多语言项目仍使用单栈精确 `P3` 声明检测命令（历史 `P3_js` / `P3_html` 形态已退役，解析器丢弃未登记后缀）：

```yaml
gate_commands:
  P3: "pytest -q"
  P3_formatter: "pytest.sh"
  project_module: "myapp"
```

`P3` / `P3_formatter` / `project_module` 为当前唯一有效的检测键组合；未来多栈并行需先经协议修订登记收集后缀，未登记的后缀键不被收集执行。

## 自定义 formatter

编写自定义 formatter 只需遵循上述契约：

1. 创建脚本（如 `.agate/formatters/my-runner.sh`）
2. 从 stdin 读原始输出，从 `$1` 读 exit code
3. 输出一行标准 JSON
4. 退出码 0（成功）或 1（解析失败）

内置 formatter 均使用内联 python3 解析，可作为参考实现。

## 内置 formatter 清单

| 脚本 | 解析策略 |
|------|---------|
| `generic-exit-only.sh` | 不解析输出，仅用 exit code 填 `exit_code`，其余字段归零 |
| `pytest.sh` | 正则提取 `N passed/failed/error` + `FAILED` 行 + ImportError/SyntaxError |
| `vitest.sh` | 正则提取 `Tests N failed/passed` + `Failed Suites` + `Cannot find module` |
| `go-test.sh` | 正则提取 `N passed/failed` + `--- FAIL:` / `test ... FAILED` + import/syntax error |
| `generic-tap.sh` | 统计 `^ok` / `^not ok` 行 |
| `generic-junit-xml.sh` | 从 XML 属性提取 `tests/failures/errors` |
