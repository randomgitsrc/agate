---
phase: P3
task_id: TAG0024
type: test-cases
parent: P2-design.md
trace_id: TAG0024-P3-check-gate-debt-fixes-20260825
status: draft
created: 2026-08-25
agent: test-designer
---

# P3 测试用例说明 —— 批次 check-gate-debt-fixes（DEBT0019 + DEBT0020，BDD-20~24）

test_code_dir: agate/tests/unit/test_check_gate.py（既有文件追加，未新建文件）

## BDD-20: 描述列含字面 `|` 时不误判

- 测试函数：`test_bdd_20_p8_roadmap_literal_pipe_in_title_not_misjudged`
- 断言：roadmap.md 数据行标题列含字面 `|`（split 后产生 10 列，`>=8` 但 `!=9`），修复后的精确列数校验应整行跳过该行，`gate_p8()` 不因此行阻断（exit 2，输出不含伪匹配的 RM 编号）。

## BDD-21: 既有合法表格判定结果不变

- 测试函数：`test_bdd_21_regression_existing_valid_roadmap_unchanged`（参数化，3 组，对应既有 `test_bdd_5/6/7` 三场景）
- 断言：列数恰为精确 9 列的既有合法 roadmap.md，在「非 done 且匹配阻断 / 无匹配行不阻断 / done 且匹配不阻断」三种场景下，DEBT0019 列数精确匹配修复前后判定结果（exit code + 输出是否含 RM 编号）保持一致。

## BDD-22: 非仓库根 CWD 下仍能正确定位

- 测试函数：`test_bdd_22_p8_non_root_cwd_locates_roadmap`
- 断言：CWD 为 `repo/task`（非仓库根）时，修复后的 `gate_p8()` 应按仓库根（`git rev-parse --show-toplevel`）而非 CWD 相对拼接定位到 `repo/agate-workspace/roadmap/roadmap.md`，正确执行状态检查并阻断（exit 1，输出含 RM 编号）。

## BDD-23: 仓库根不可得时给出区分性提示

- 测试函数：`test_bdd_23_p8_repo_root_unavailable_distinct_warning`
- 断言：用 `GIT_CEILING_DIRECTORIES` 环境变量阻止 git 向上穿越找到外层仓库，模拟"仓库根不可得"（非 git 仓库环境）；修复后 `gate_p8()` 应在 stderr 输出含"仓库根不可得"的区分性提示，而非静默跳过检查。

## BDD-24: 既有合法场景（仓库根 CWD）判定结果不变

- 测试函数：`test_bdd_24_regression_existing_repo_root_cwd_unchanged`
- 断言：CWD 恰为仓库根（既有唯一调用路径）时，DEBT0020 仓库根锚定修复（`git rev-parse --show-toplevel` 替代 CWD 相对拼接）不改变既有正常调用路径的判定结果（阻断行为/rm_id/status 与修复前一致，exit 1 + 输出含 RM 编号）。

## 红灯确认（2026-08-25）

命令：`timeout 120s python3 -m pytest agate/tests/unit/test_check_gate.py --basetemp=.pytest-tmp -p no:cacheprovider -v -k "bdd_20 or bdd_21 or bdd_22 or bdd_23 or bdd_24"`

- BDD-20 / BDD-22 / BDD-23：3 个用例均 FAILED，失败原因均为 `AssertionError`（真红灯，B 类：断言失败，非语法/import 错误）。
- BDD-21（3 组参数化）+ BDD-24（1 组）：共 4 个用例 PASSED——回归口径用例，验证修复前后既有合法场景判定结果不变，不要求本身处于红灯。
- 全量回归：`python3 -m pytest agate/tests/unit/test_check_gate.py --basetemp=.pytest-tmp -p no:cacheprovider -q` → `3 failed, 179 passed`，既有用例（含 `test_bdd_5/6/7`、G8 系列等）全部保持绿色，未被本次追加破坏。
- `git diff --stat agate/tests/unit/test_check_gate.py` → `156 insertions(+)`，0 处删除，确认是纯追加。
