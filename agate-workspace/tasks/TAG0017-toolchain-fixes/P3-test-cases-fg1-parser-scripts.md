## 批次 fg1-parser-scripts（BDD-1/2/3/4）

test_code_dir: `agate/tests/unit`

### BDD-1: P2 阶段声明 `{key}_timeout_seconds` 不再被误判为待核实命令
- 测试用例：test_bdd_1_is_gate_meta_key_timeout_seconds_suffix_true（agate/tests/unit/test_agate_common.py，参数化 3 例，起始 L38）
- 测试用例：test_pyx_7_bdd_1_timeout_seconds_excluded_from_commands（agate/tests/unit/test_check_tdd_red.py:683）
- 测试用例：test_gmc_3_bdd_1_timeout_seconds_key_not_treated_as_missing_command（agate/tests/unit/test_agate_gate_missing_cmds.py:47）
- 测试用例：test_p5c_5_bdd_1_3_timeout_seconds_not_treated_as_command（agate/tests/unit/test_agate_read_p5_commands.py:18，同时覆盖 BDD-3）
- 预期行为：`gate_commands` 块中以 `_timeout_seconds` 结尾的 key（纯整数字符串值，无路径无 `=`）不被 `agate-read-gate-commands.py` / `agate-gate-missing-cmds.py` / `agate-read-p5-commands.py` 误判为待核实/待执行命令；`is_gate_meta_key(key)` 对该类 key 返回 True。
- 当前状态：红灯（AssertionError——4 个脚本均只排除 `_formatter` 后缀，`_timeout_seconds` 后缀 key 被当作真实命令处理，输出中出现 `"cmd": "120"` / `P5_timeout_seconds:120` 等假命令；`test_agate_common.py` 因 `is_gate_meta_key` 尚不存在，`from agate_common import is_gate_meta_key` 触发 ImportError，属项目内 import 失败的真实红灯）

### BDD-2: P3 阶段声明 timeout_seconds 时真红灯仍正确判定为 A 类失败
- 测试用例：test_bdd_2_timeout_seconds_declared_real_a_class_failure_stays_a_class（agate/tests/unit/test_check_tdd_red.py:718）
- 测试用例：test_bdd_2_is_gate_meta_key_ordinary_key_false（agate/tests/unit/test_agate_common.py，参数化 5 例，起始 L48——含 `P3_timeout`「前缀相似但非完整 `_timeout_seconds` 后缀」的护栏用例，防止判据被放宽为通配匹配）
- 预期行为：P2-design.md 同时声明 `P3_timeout_seconds` 与真实会失败（SyntaxError，非超时）的 P3 测试命令时，`check-tdd-red.py` 判定结果仍为 A 类真实失败（exit 1），且 `_timeout_seconds` key 不应被当作独立命令实际执行（用 `TDD_CHECK:` 输出行数精确验证只有 1 条真实命令被判定，而非仅退出码——本场景下退出码在修复前后巧合地都是 1，无法单独作为红灯信号）。
- 当前状态：红灯（AssertionError：`result.output.count("TDD_CHECK:") == 1` 实测为 2——修复前 `check-tdd-red.py` 的 `main()` 会把 `P3_timeout_seconds: 120` 当作一条 `cmd="120"` 的命令真的 subprocess 执行一遍（`bash: 120: command not found`，exit 127），多打印一行 `TDD_CHECK: A-class error (test runner failed with exit code 127)`，证实这不只是展示问题，而是会执行一条虚假命令的功能性 bug）

### BDD-3: P5 阶段命令计数不含 timeout_seconds 声明键
- 测试用例：test_gpc_4_bdd_3_timeout_seconds_excluded_from_aux_count（agate/tests/unit/test_agate_gate_p5_count.py:54）
- 测试用例：test_p5c_5_bdd_1_3_timeout_seconds_not_treated_as_command（agate/tests/unit/test_agate_read_p5_commands.py:18，与 BDD-1 共用）
- 预期行为：`gate_commands` 块含一条 `P5:` 主命令 + 一条 `P5_timeout_seconds: 120` 时，`agate-gate-p5-count.py` 输出 "1 0"（1 主命令 + 0 辅助命令），`P5_timeout_seconds` 不计入辅助命令。
- 当前状态：红灯（AssertionError：实测输出 "1 1"——当前脚本 `aux = [... if not k.endswith("_formatter")]` 未排除 `_timeout_seconds`，误将其计入辅助命令）

### BDD-4: 同类遗漏拦截——防止未来新增第 5 处未排除 `_timeout_seconds` 的解析点
- 测试用例：test_bdd_4_formatter_excluding_scripts_also_exclude_timeout_seconds（agate/tests/unit/test_gate_key_suffix_audit.py，新建文件）
- 测试用例：test_bdd_4_is_gate_meta_key_formatter_suffix_true（agate/tests/unit/test_agate_common.py，参数化 4 例，起始 L28）
- 预期行为：结构性审计扫描 `agate/scripts/agate-*.py`，任何脚本对 gate_commands key 做了字面量 `"_formatter"` 后缀排除逻辑，必须同时含字面量 `"_timeout_seconds"` 或引用共享判据函数 `is_gate_meta_key`，否则判定为与 DEBT0010 同类的新遗漏点，令 pytest 整体失败。判据用带引号字面量（而非裸子串）精确定位"做 key 后缀排除逻辑"的脚本，已验证不会误伤仅调用 `resolve_formatter`/`run_test_with_formatter` 等公共函数名的间接消费方（如 `agate-capture-env-baseline.py`，P1 3.1 节判定为本次不处理范围）。
- 当前状态：红灯（AssertionError：offenders = ['agate-gate-missing-cmds.py', 'agate-gate-p5-count.py', 'agate-read-gate-commands.py', 'agate-read-p5-commands.py']——4 个目标脚本均命中 `_formatter` 排除逻辑但未命中 `_timeout_seconds`/`is_gate_meta_key`）

## 自跑验证记录

```
python3 -m pytest agate/tests/unit/test_agate_common.py agate/tests/unit/test_gate_key_suffix_audit.py \
  agate/tests/unit/test_agate_gate_missing_cmds.py agate/tests/unit/test_agate_gate_p5_count.py \
  agate/tests/unit/test_agate_read_p5_commands.py agate/tests/unit/test_check_tdd_red.py -q
```
结果：18 个新增用例全部 failed（真红灯，均为 AssertionError / ImportError，非语法错误），53 个既有用例全部 passed（无回归）。
`python3 -m py_compile` 对全部 6 个测试文件通过（排除假红灯风险）。
全量 `agate/tests/unit/` 回归：36 failed（本批次 18 条 + 其余 3 个并行批次各自的真红灯 18 条，非本批次范围）/ 845 passed / 2 skipped——本批次未影响其他批次或既有用例。

## 未修改文件确认

未修改 `agate/scripts/agate_common.py` 及 4 个 `agate-*.py` 解析脚本本身（P4 implementer 工作范围）。
