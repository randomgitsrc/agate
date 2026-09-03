---
phase: P3
date: 2026-09-04
trigger: unintended_regression
---
# P3 Gate 诊断（三簇测试全量跑后）

- 全量测试结果：22 failed, 1413 passed, 2 skipped（`pytest agate/tests/unit/ agate/tests/regression/ agate/tests/integration/ -n auto -q --tb=no`）
- 21 项失败对应本次新写的 BDD 测试（真红灯，符合预期，逐条核对函数名可追溯到 BDD 编号）
- **1 项意外失败，非本次 BDD 范围**：`agate/tests/unit/test_agate_scripts_encoding.py::test_bdd_5_all_test_py_text_io_explicit_encoding`

## 诊断

version-mgmt 簇新增的 `test_agate_common.py:223` 含字符串字面量
`"print(compute_sha256(p) == hashlib.sha256(open(p, 'rb').read()).hexdigest())"`——这是嵌入在
subprocess 脚本字符串里的 Python 代码文本，用单引号 `'rb'`。仓库既有的 encoding 守卫测试
`test_bdd_5_all_test_py_text_io_explicit_encoding`（`test_agate_scripts_encoding.py:23`）用正则
`re.search(r"(?<!Image\.)\bopen\(", line) and "encoding=" not in line and '"rb"' not in line and
'"wb"' not in line` 逐行扫描 `agate/tests/**/*.py`，只识别**双引号** `"rb"`/`"wb"` 作为二进制模式
豁免，单引号 `'rb'` 不被识别，导致这一行被误判为"文本 I/O 缺 encoding"。

这不是我们要修的 7 条 DEBT 之一，是本次新写测试代码的字符串引号风格意外触发了既有 gate 守卫。
**修复方向**：把 `test_agate_common.py:223` 那一行字符串里的 `'rb'` 改成 `"rb"`（纯引号风格调整，
不改变该字符串作为 subprocess 脚本文本的语义——脚本本体在子进程里执行时 `'rb'`/`"rb"` 完全等价，
只是外层扫描器按字面 grep 识别）。

## 路由

退回 version-mgmt 簇的 test-designer，仅修正这一行引号风格，不改动其余已确认真红灯的测试内容。
