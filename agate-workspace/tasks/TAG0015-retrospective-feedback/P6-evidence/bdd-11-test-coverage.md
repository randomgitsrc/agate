# BDD-11 证据：test_check_retrospective.py 新增断言覆盖 BDD-9/10

## Then 子句逐项核对

Then 要求新增/更新至少 2 个单测用例：
1. 一个断言 stderr 输出含 `tasks/{Txxx}/retrospective.md` 且不含 `docs/releases`
2. 一个断言 DEBT/roadmap 关联信号触发"建议复盘"提醒（BDD-10 场景）

## 实际文件核对（agate/tests/unit/test_check_retrospective.py）

`grep -n "docs/releases\|tasks/{Txxx}\|def test"` 命中：

```
249:def test_tag0015_bdd9_stderr_hint_points_to_task_dir(
268:    assert "tasks/{Txxx}/retrospective.md" in result.output
269:    assert "docs/releases" not in result.output

272:def test_tag0015_bdd10_debt_signal_triggers_mechanism_gap_reminder(
   ... assert "发现机制缺口" in result.output / assert "检测到异常模式" not in result.output

305:def test_tag0015_bdd10_roadmap_signal_triggers_mechanism_gap_reminder(
   ... assert "发现机制缺口" in result.output
```

三个新增测试函数，覆盖数量超过 Then 要求的"至少 2 个"（1 个 BDD-9 断言 + 2 个 BDD-10 断言，
分别覆盖 debt 信号面与 roadmap 信号面）。测试内容非平凡断言（构造独立 tmp_path 嵌套目录、
真实写入 .state.yaml/tech-debt.md/roadmap.md、subprocess 实跑脚本、断言 stdout/stderr 文本），
非"断言存在但内容为真"式的空心测试。

## 本轮独立验证：这些新增测试确实全部通过

见 `P6-evidence/shared-p6-command-output.log`（本轮独立实跑的
`pytest agate/tests/unit/test_check_retrospective.py ... -v`，输出含
`test_tag0015_bdd9_stderr_hint_points_to_task_dir PASSED`、
`test_tag0015_bdd10_debt_signal_triggers_mechanism_gap_reminder PASSED`、
`test_tag0015_bdd10_roadmap_signal_triggers_mechanism_gap_reminder PASSED`，
整体 `35 passed`，`EXIT_CODE: 0`）。

## 判定

**满足**——新增 3 个测试用例（超过"至少 2 个"门槛），分别覆盖 BDD-9（路径文案）与 BDD-10
（DEBT 信号面 + roadmap 信号面），断言内容具体、非空心，本轮独立实跑全部转绿，这两处改动
此后受测试保护（回归拦截）的目的达成。
