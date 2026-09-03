---
phase: P3
task_id: TAG0031
parent: P2-design.md
trace_id: TAG0031-P3-test-isolation-20260904
created: '2026-09-04'
test_code_dir: agate/tests/unit/
agent: test-designer
---
# P3-test-cases（测试隔离簇，DEBT0007）— TAG0031

> 本文件仅覆盖三簇并行拆批中的「测试隔离」簇（batch id: test-isolation，BDD-6/7）。
> 版本管理域（DEBT0002/3/4）与 check-gate.py 健壮性（DEBT0016/17/18）两簇的测试用例
> 由各自 test-designer 产出，不在本文件范围内。

## 本簇特殊性说明

`check-pruning.py:84-100` 的 `_staged_source_count` 隔离修复已由 **TAG0024 commit
`e2357fc`** 落地（两处 `run_git(...)` 调用均已传入 `cwd=task_dir`，见
`agate/scripts/check-pruning.py` L84/L96）。本簇**不改生产代码**，只做两件事：

1. **BDD-6**：确认既有 4 个回归用例仍稳定 PASS（验证性质，非新写红灯测试）。
2. **BDD-7**：为 DEBT0007 的 debt 登记闭合动作设计一个可判定的验证点（真正的红灯，
   因为 `debt/tech-debt.md` 中 DEBT0007 `status` 现状仍为 `open`）。

---

## BDD-6：三个原始用例在暂存区含大量无关文件时稳定 PASS（含既有修复的显式回归覆盖）

- 对应 P1 `#### BDD-6`
- **不新写红灯测试** —— 此四例现状已绿，本次不新增红灯测试，验证动作见 P5/P6 证据。
- 覆盖的既有用例（均在 `agate/tests/unit/test_check_pruning.py`）：
  1. `test_p2_6e_prune_p7_coupling_checklist_exit_0`（L214）
  2. `test_p2_52_yaml_list_phases_exit_0`（L338）
  3. `test_p2_52b_yaml_list_phases_p3_pruned_low_exit_0`（L354）
  4. `test_p2_6f_staged_source_count_uses_task_repo_not_outer_cwd_repo_exit_0`（L370）——
     本用例是 TAG0024 修复的显式回归覆盖：构造 outer_repo（6 个无关暂存源码文件，
     模拟 TAG0015 报告场景）+ task_repo（暂存区干净），断言 `_staged_source_count`
     以 `task_dir` 自身所属仓库（`cwd=task_dir`）为准，不被外层仓库暂存区污染。

### 复跑结果（本次 P3 阶段实测，2026-09-04）

命令：

```bash
/usr/bin/python3 -m pytest agate/tests/unit/test_check_pruning.py \
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

**4/4 全绿，与 P0-brief/P1/P2 记录的现状一致，未发现异常，不做任何"修复"动作。**
附加回归确认：`test_check_pruning.py`（全量 30 例）+ `test_agate_debt_check.py`（21
例）合计 **52 passed**，未破坏 TAG0024 已修复的既有测试，也未影响相邻 debt 登记校验器
测试。

---

## BDD-7：DEBT0007 debt 登记闭合

- 对应 P1 `#### BDD-7`
- Given `check-pruning.py` 的 `_staged_source_count` 隔离修复（TAG0024 commit
  `e2357fc`）与 BDD-6 补充验证均已确认生效（见上节复跑结果）
- When 在 `agate-workspace/debt/tech-debt.md` 更新 DEBT0007 条目
- Then `status` 改为 `closed`，追加 `closed_at` 与 closure 说明，`evidence` 追加指向
  `e2357fc`/`test_p2_6f_...` 与本任务 BDD-6 验证记录，登记格式与既有 DEBT0005/DEBT0006
  closed 条目一致（status/closed_at/evidence 补充块，先例见 `tech-debt.md` L108-158）

### 测试代码

新文件：`agate/tests/unit/test_debt_registry_closure.py`

- 测试函数：`test_bdd_7_debt0007_status_closed_with_closure_fields(agate_root)`
- 实现方式：读取 `agate_root.parent / "agate-workspace" / "debt" / "tech-debt.md"`，
  用正则提取 `## DEBT0007` 章节下的 ```yaml fence 块，断言：
  1. `status:` 字段值为 `closed`（当前为 `open` → 断言失败，真红灯来源）
  2. `status` 已为 `closed` 时，进一步核对 `closed_at:` 字段存在
  3. `evidence` 块内出现 `e2357fc` / `TAG0031` / `BDD-6` 三者之一的引用（与
     DEBT0005/DEBT0006 先例的 closure note 写法一致，避免格式漂移）

之所以写成独立 pytest 用例而非纯文档化 grep 步骤：本簇需要一个可被 P4/P5/CI 自动
拾取的红→绿判定点（`agate/tests/unit/` 下的用例会被 `pytest agate/tests/unit/` 全量
回归命令自动收录），比人工核对步骤更适配本项目既有的"check-tdd-red.py 自动探测红灯"
机制。

### 当前红灯确认（本次 P3 阶段实测，2026-09-04）

命令：

```bash
/usr/bin/python3 -m pytest agate/tests/unit/test_debt_registry_closure.py -v
```

结果：**FAIL**（`AssertionError: DEBT0007 status 现状为 'open'，closure 动作尚未执行`，
`assert 'open' == 'closed'`）——属 B 类错误（断言失败，非 SyntaxError/第三方 import
失败），是真红灯，非假红灯。

### P4 完成判据

P4 在 `agate-workspace/debt/tech-debt.md` 完成 DEBT0007 登记闭合动作
（status→closed + closed_at + evidence 追加块，参照 DEBT0005/DEBT0006 先例）后，
重跑同一命令应转为 **PASS**，作为 BDD-7 的自动化验收证据（P5/P6 引用）。

---

## 门槛自检

- [x] BDD-6：4 个既有用例复跑结果已记录（4 passed）
- [x] BDD-7：设计了一个当前 FAIL（DEBT0007 status:open）、P4 完成后 PASS 的验证点
- [x] 未破坏 TAG0024 已修复的既有测试（附加回归 52 passed）
- [x] 未改动任何生产代码（`agate/scripts/check-pruning.py` 未触碰）
