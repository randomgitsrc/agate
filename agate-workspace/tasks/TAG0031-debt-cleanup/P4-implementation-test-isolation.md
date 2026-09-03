---
phase: P4
task_id: TAG0031
parent: P3-test-cases-test-isolation.md
trace_id: TAG0031-P4-test-isolation-20260904
agent: implementer
created: 2026-09-04
type: implementation
status: draft
---

```yaml
implementation_dir: 无新增改动，见正文说明
```

## 改动摘要

**本簇（test-isolation，DEBT0007）本次无任何代码/文档改动。**

`check-pruning.py:84-100` 的 `_staged_source_count` 隔离修复已由 **TAG0024 commit
`e2357fc`** 落地（两处 `run_git(...)` 均已传入 `cwd=task_dir`）。本簇按
P4-dispatch-context-implementer-test-isolation.md 的明确指引，任务范围仅为
**确认既有回归用例仍绿**，不改任何生产代码（`agate/scripts/check-pruning.py` 未触碰），
也不改 `agate-workspace/debt/tech-debt.md`（DEBT0007 的登记闭合动作——即让
`test_bdd_7_debt0007_status_closed_with_closure_fields` 转绿——按 P2-design.md
§1.1「跨簇共享写入」表，划归**主 Agent 在三簇 implementer 全部返回后统一处理**的范围，
避免与另外两簇（版本管理域 / check-gate.py 健壮性）对 `tech-debt.md` 的登记闭合动作
产生合并冲突）。

## BDD-6 复跑结果（4 个既有用例，本次 P4 阶段实测，2026-09-04）

命令：

```bash
timeout 60s /usr/bin/python3 -m pytest agate/tests/unit/test_check_pruning.py \
  -k "test_p2_6e_prune_p7_coupling_checklist_exit_0 or test_p2_52_yaml_list_phases_exit_0 or test_p2_52b_yaml_list_phases_p3_pruned_low_exit_0 or test_p2_6f_staged_source_count_uses_task_repo_not_outer_cwd_repo_exit_0" \
  -v
```

结果：

```
agate/tests/unit/test_check_pruning.py::test_p2_6e_prune_p7_coupling_checklist_exit_0 PASSED
agate/tests/unit/test_check_pruning.py::test_p2_52_yaml_list_phases_exit_0 PASSED
agate/tests/unit/test_check_pruning.py::test_p2_52b_yaml_list_phases_p3_pruned_low_exit_0 PASSED
agate/tests/unit/test_check_pruning.py::test_p2_6f_staged_source_count_uses_task_repo_not_outer_cwd_repo_exit_0 PASSED

4 passed, 26 deselected in 0.47s
```

**4/4 全绿**，与 P0-brief / P1 / P2 / P3 记录的现状一致，未发现异常，未做任何"修复"动作。

## BDD-7 状态确认（预期红灯，本次未处理）

按约束未改动 `debt/tech-debt.md`，`test_debt_registry_closure.py` 复跑仍为
**FAIL**（预期状态，非本簇 bug）：

```bash
timeout 60s /usr/bin/python3 -m pytest agate/tests/unit/test_debt_registry_closure.py -v
```

```
FAILED agate/tests/unit/test_debt_registry_closure.py::test_bdd_7_debt0007_status_closed_with_closure_fields
AssertionError: DEBT0007 status 现状为 'open'，closure 动作尚未执行（P4 完成后应为 closed，届时本用例转绿）
```

`git status --short` 确认工作区无任何生产代码或 `debt/tech-debt.md` 改动（仅预先存在的
三份 P4-dispatch-context-implementer-*.md 派发指引文件，非本簇产出）。

## 待主 Agent 处理事项

- **DEBT0007 登记闭合**：在三簇 implementer 全部返回后，主 Agent 统一在
  `agate-workspace/debt/tech-debt.md` 的 `## DEBT0007` 章节把 `status` 改为 `closed`，
  追加 `closed_at` 字段与 closure 说明，`evidence` 追加指向 `e2357fc` /
  `test_p2_6f_staged_source_count_uses_task_repo_not_outer_cwd_repo_exit_0` 与本簇
  BDD-6 复跑记录，格式与既有 DEBT0005/DEBT0006 closed 条目一致（`tech-debt.md`
  L108-158 先例）。
- 完成后重跑 `test_bdd_7_debt0007_status_closed_with_closure_fields` 应转为 **PASS**，
  作为 BDD-7 的自动化验收证据（供 P5/P6 引用）。

## 新增文件核对表

无新增文件（本簇本次无代码/文档产出，仅本 P4-implementation 文件自身）。

## 自查结论

- BDD-6：4/4 既有回归用例复跑仍绿，符合预期
- BDD-7：红灯维持，符合设计（登记闭合动作待主 Agent 统一处理）
- 未触碰任何生产代码（`agate/scripts/*.py`）
- 未触碰 `agate-workspace/debt/tech-debt.md`
