## 批次 fg3-strict-mode-code（BDD-9代码半）

test_code_dir: `agate/tests/unit`

对应 P1 `#### BDD-9: WARNING-only 场景下 gate_commands.P5 链路后续步骤仍会被执行到` 的代码半实现落点：`agate/scripts/check-protocol-consistency.py` main()（约 L1076-1134）新增 `--strict-errors-only` 互斥模式。

### BDD-9（代码半）：`check-protocol-consistency.py` 新增 `--strict-errors-only` 互斥模式

三条场景对应 P2-design.md §1.1/§2.3 声明的场景矩阵：仅 ERROR 非零（exit 1），WARNING-only 打印提示但 exit 0；既有 `--strict`（WARNING-only 也非零）行为不变、并列不冲突。

| 用例 | 场景 | Given | When | Then | 测试函数 |
|---|---|---|---|---|---|
| BDD-9-code-1 | 0 ERROR + 0 WARNING | 一致性检查结果 0 ERROR、0 WARNING | 以 `--strict-errors-only` 跑 `main()` | exit 0，输出含"🎉 全部检查通过" | `test_strict_errors_only_zero_error_zero_warning_exit_0` |
| BDD-9-code-2 | 0 ERROR + N WARNING（N>0） | 一致性检查结果 0 ERROR、3 条 WARNING | 以 `--strict-errors-only` 跑 `main()` | exit 0，且打印提示信息"仅有 3 个 WARNING，无 ERROR。"（沿用现有非 JSON 分支已有提示，`--strict-errors-only` 不压制它） | `test_strict_errors_only_zero_error_n_warning_exit_0_with_hint` |
| BDD-9-code-3 | N ERROR（N>0） | 一致性检查结果 1 条 ERROR | 以 `--strict-errors-only` 跑 `main()` | exit 1，输出含该 ERROR 消息 | `test_strict_errors_only_n_error_exit_1` |

### 测试方法说明

- 沿用文件既有惯用法（`test_bdd_2_blocker_check1_independent_when_check10_error/warning`）：`_load_cpc()` 用 `importlib` 装载真实脚本 → `monkeypatch.setattr(cpc, "CHECKS", ...)` + `monkeypatch.setattr(cpc, "run_all_checks", _fake_run)` 构造确定的 `Report` 状态 → `monkeypatch.setattr("sys.argv", [...])` 注入 `--root`/`--strict-errors-only` → 驱动 real `cpc.main()` → 用 `capsys` 断言 stdout + exit code。
- 命名前缀改用 `test_strict_errors_only_*`（避开文件内已存在的 `test_bdd_9_*`——那组前缀属于历史 CHECK9/CHECK12 任务遗留编号，与本次 BDD-9 撞号但语义无关，dispatch-context 已指明按此避让）。

### 红灯确认（真红灯，非测试代码写错）

当前 `check-protocol-consistency.py` 的 argparse 只定义 `--root`/`--strict`/`--json`，未定义 `--strict-errors-only`。三条用例在 `code = cpc.main()` 这一行统一触发：

```
check-protocol-consistency.py: error: unrecognized arguments: --strict-errors-only
SystemExit: 2
```

实测：

```
$ python3 -m pytest agate/tests/unit/test_check_protocol_consistency.py -k "strict_errors_only" -v
FAILED test_strict_errors_only_zero_error_zero_warning_exit_0
FAILED test_strict_errors_only_zero_error_n_warning_exit_0_with_hint
FAILED test_strict_errors_only_n_error_exit_1
3 failed, 24 deselected
```

三个失败均为 argparse `unrecognized arguments`（B 类：CLI 接口缺失，真红灯），非测试代码本身语法/断言错误。

### 既有 `--strict` 矩阵回归确认（不受影响）

```
$ python3 -m pytest agate/tests/unit/test_check_protocol_consistency.py -k "not strict_errors_only" -v
24 passed, 3 deselected
```

`test_bdd_2_blocker_check1_independent_when_check10_error` / `test_bdd_2_blocker_check1_independent_when_check10_warning`（既有 `--strict` 相关驱动 real `main()` 的用例）及其余 22 条既有用例全部继续通过，未受本批次新增用例影响。

### 范围确认

- 未修改 `agate/scripts/check-protocol-consistency.py` 本身（P4 implementer 的工作）。
- 未碰 `agate/phase-cards/P2-design.md` / `architect.md` / `P4-implementation.md`（fg1-doc-boundary 批次范围）。
- 本批次唯一改动文件：`agate/tests/unit/test_check_protocol_consistency.py`（新增 3 个测试函数，追加在文件末尾）。
