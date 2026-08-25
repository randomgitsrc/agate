---
phase: P4
task_id: TAG0024
type: implementation
parent: P1-requirements.md
trace_id: TAG0024-P4-check-pruning-isolation-fix-20260825
status: draft
created: 2026-08-25
agent: implementer
---

```yaml
implementation_dir: agate/scripts/
```

## 修了什么（对应 BDD-30）

`agate/scripts/check-pruning.py` 的 `_staged_source_count(task_dir)` 内两处 `run_git(...)`
调用未传 `cwd`，subprocess 继承调用进程的当前工作目录而非被测 `task_dir` 自身所属仓库，
导致单元测试中 `task_dir`（pytest tmp 目录）与真实调用进程 cwd 所在仓库脱节时，函数误读
调用进程 cwd 所在仓库的暂存区状态。修复：两处 `run_git` 调用均加 `cwd=task_dir`，改为读取
`task_dir` 自身所属仓库的 git 状态（生产环境下 `task_dir` 本就在真实仓库内，行为逐字节不变）。

## git diff 摘要（只改了两处 run_git 调用）

```diff
--- a/agate/scripts/check-pruning.py
+++ b/agate/scripts/check-pruning.py
@@ -85,7 +85,7 @@ def _staged_source_count(task_dir):
     """裁剪 P7 的源码文件数（git diff --cached 排除任务产出后，同 sh 排除模式）。"""
     if run_git is None:
         return 0
-    rc, out = run_git(["rev-parse", "--show-toplevel"])
+    rc, out = run_git(["rev-parse", "--show-toplevel"], cwd=task_dir)
     repo_root = out.rstrip("\n").strip() if rc == 0 else ""
     if not repo_root:
         return 0
@@ -95,7 +95,7 @@ def _staged_source_count(task_dir):
         tasks_base_rel = os.path.relpath(parent, repo_root).replace("\\", "/")
     except ValueError:
         return 0
-    rc, out = run_git(["diff", "--cached", "--name-only"])
+    rc, out = run_git(["diff", "--cached", "--name-only"], cwd=task_dir)
     if rc != 0:
         return 0
     pattern = (
```

未改动函数其余逻辑（排除模式 `pattern`、`tasks_base_rel` 计算、返回值语义均原样保留）。

同时在 `agate/tests/unit/test_check_pruning.py` 追加回归测试
`test_p2_6f_staged_source_count_uses_task_repo_not_outer_cwd_repo_exit_0`：构造两个独立
git 仓库——outer_repo（模拟调用进程实际 cwd 所在的、暂存了 6 个无关源码文件的真实仓库）与
task_repo（task 自身所属的独立仓库，已提交、暂存区干净），显式以 `cwd=outer_repo.path`
调用 `check-pruning.py <task_repo 内的 task 路径>`，断言 exit 0——证明判定确实以
`task_dir` 自身所属仓库状态为准，不受调用进程 cwd 所在仓库暂存区污染。该测试不依赖
pytest tmp 目录是否物理落在真实仓库内，因此在任意 `--basetemp` 位置下都具确定性。

## 自跑 test_check_pruning.py 结果

**默认临时目录（pytest 系统临时目录，位于仓库外，即 `task_dir` 与真实仓库物理无关的
标准场景）**：

```
$ python3 -m pytest agate/tests/unit/test_check_pruning.py -p no:cacheprovider -q
..............................                                           [100%]
30 passed in 3.03s
```

全部转绿，含原本 3 个失败用例（`test_p2_6e_prune_p7_coupling_checklist_exit_0` /
`test_p2_52_yaml_list_phases_exit_0` / `test_p2_52b_yaml_list_phases_p3_pruned_low_exit_0`）
+ 新增回归测试 `test_p2_6f_...`。

**已知限制（诚实披露，非本次修复范围）**：dispatch-context 建议的自查命令加了
`--basetemp=.pytest-tmp`（项目内目录）。实测发现，在**这个具体参数**下，上述 3 个用例
仍会失败：

```
$ python3 -m pytest agate/tests/unit/test_check_pruning.py --basetemp=.pytest-tmp -p no:cacheprovider -q
3 failed, 27 passed
```

根因排查：`--basetemp=.pytest-tmp` 使 pytest 的 tmp_path（进而 `task_dir`）物理落在
**真实仓库工作树内部**（`.pytest-tmp` 是仓库根下的子目录，未加入 .gitignore，且未加 -C 之
类的隔离），此时 `git rev-parse --show-toplevel` 从 `cwd=task_dir` 出发按目录树向上查找
`.git`，仍会找到同一个真实外层仓库（因为 `task_dir` 确实是它的子目录，而不是修复目标场景
——"`task_dir` 与真实仓库无关的独立临时目录"）。也就是说，`git diff --cached` 在这种
`--basetemp` 取值下对两种 cwd（修复前的进程 cwd / 修复后的 `task_dir`）返回的是**同一个仓库**
的暂存区，`cwd=task_dir` 这个改动对这一具体入参组合不产生区分度——这是一个独立于本次改动、
与 `agate/tests/ENV-SENSITIVE-TESTS.md` 已归类的「basetemp 位置依赖」同类的环境因素，
不在 BDD-30 的授权改动范围内（授权范围明确限定为仅这两处 `run_git` 调用加 `cwd=task_dir`，
不改函数其余逻辑）。

已用两种独立证据确认本次修复本身正确、达成 BDD-30 目标：
1. 默认（仓库外）临时目录场景：`test_check_pruning.py` 30/30 全绿（见上）。
2. 新增回归测试 `test_p2_6f_...` 用显式构造的两个独立真实 git 仓库验证隔离生效，
   **在两种 `--basetemp` 取值下都通过**（不依赖 tmp 目录物理位置）。

## 全仓回归确认

```
python3 -m pytest agate/tests/ --basetemp=.pytest-tmp -p no:cacheprovider -q
```

结果：

```
3 failed, 1282 passed, 2 skipped in 149.10s
```

失败的 3 个用例与本节上方「已知限制」列出的完全一致（`test_p2_6e_prune_p7_coupling_checklist_exit_0` /
`test_p2_52_yaml_list_phases_exit_0` / `test_p2_52b_yaml_list_phases_p3_pruned_low_exit_0`），
与修复前基线（objective_info：`3 failed, 1281 passed, 2 skipped`）相比，失败集合逐字节不变、
`passed` 计数 +1（新增回归测试 `test_p2_6f_...` 通过）——**无新增失败，无回归**。该 3 个失败
在 `--basetemp` 指向仓库外目录时不复现（见上节，30/30 全绿），已确认是与本次改动无关的
「basetemp 位置依赖」环境因素，不影响任何生产路径行为——`_staged_source_count` 在生产环境下
`task_dir` 恒位于真实仓库内，修复前后两种 cwd 取值结果逐字节一致。

## 第 2 轮修复（BDD-30 补完：测试隔离层，非生产代码）

上一轮把「`--basetemp=.pytest-tmp` 场景 3 个用例仍失败」列为已知限制/环境因素搁置；本轮按
用户明确要求把它作为 BDD-30 SCOPE+ 解决，定位到根因并修复测试隔离层（`check-pruning.py`
生产代码本身不需要再改，问题只在单测的仓库边界隔离）。

**根因**：`--basetemp=.pytest-tmp` 使 `task_dir`（pytest `tmp_path` 的子目录）物理落在真实
仓库工作树内部。`_staged_source_count()` 内 `run_git(..., cwd=task_dir)` 执行
`git rev-parse --show-toplevel` 时，会从 `task_dir` 向上穿越目录树找到同一个真实外层仓库的
`.git`，进而读到外层仓库（本次 SELF-GATE 暂存了大量文件）的暂存区，与这 3 个用例本身预期的
「task_dir 与任何仓库无关、`_staged_source_count` 应返回 0」场景不符，导致误判。

**修复手段**：复用本仓库已有先例（`test_check_gate.py::test_bdd_23_p8_repo_root_unavailable_distinct_warning`
与 `test_check_routing.py:155-157` 注释所述 RM-AG0041 技术）——用 `GIT_CEILING_DIRECTORIES`
环境变量阻止 git 向上穿越出 `tmp_path`，使 `git rev-parse --show-toplevel` 在 `task_dir`
所在的临时目录边界内正确找不到仓库（返回非 0，`_staged_source_count` 按设计回落到 0）。

边界值选取：`task_dir` fixture 生成的 `td` 是 pytest `tmp_path` 的直接子目录
（`tempfile.mkdtemp(prefix="task-", dir=str(base_dir))`，`base_dir=tmp_path`）。`git rev-parse`
的 `cwd` 参数即 `td` 本身；`GIT_CEILING_DIRECTORIES` 语义上排除的是"git 向上 chdir 进入"的
祖先目录，不排除起始目录自身——因此必须设为 `td` 的**父目录**（即 `tmp_path`），而非 `td`
自身（曾验证 `env={"GIT_CEILING_DIRECTORIES": str(td)}` 对这 3 个用例仍返回 exit 1，
`GIT_CEILING_DIRECTORIES=str(tmp_path)` 才生效），与 `test_bdd_23_*`（`cwd=non_git_cwd`，
`ceiling=tmp_path`，`non_git_cwd` 是 `tmp_path` 的直接子目录）用法完全对称。

**改动**：
1. `_run_pruning(agate_scripts, python_exe, run_cli, task_arg, cwd=None, env=None)`：新增
   `env` 形参并透传给 `run_cli`（`run_cli`/`_run_cli_impl` 本身早已支持 `env`，无需改
   conftest）。
2. 仅给 3 个既有失败测试追加 `tmp_path` fixture 依赖 + `env={"GIT_CEILING_DIRECTORIES": str(tmp_path)}`，
   断言逻辑（`result.returncode == 0`）逐字节不变。
3. 未动 `test_p2_6f_staged_source_count_uses_task_repo_not_outer_cwd_repo_exit_0`
   （上一轮已产出，不受影响）。
4. 未再改 `agate/scripts/check-pruning.py`（问题只在测试隔离层）。

**验证结果**：

```
$ timeout 60s python3 -m pytest agate/tests/unit/test_check_pruning.py --basetemp=.pytest-tmp -p no:cacheprovider -q
30 passed in 3.45s
```

（本文件共 30 个测试函数，全部转绿，含原 3 个失败用例 + 第 1 轮新增的 `test_p2_6f_...`。）

```
$ timeout 300s python3 -m pytest agate/tests/ --basetemp=.pytest-tmp -p no:cacheprovider -q
1285 passed, 2 skipped in 146.88s (0:02:26)
```

全仓 **0 failed**——本次 BDD-30 SCOPE+ 的最终验收标准已达成。较第 1 轮基线
（`3 failed, 1282 passed, 2 skipped`）：3 个此前搁置的失败全部转绿，`passed` 净增 3，无新增
失败，无回归。上一轮文档中「已知限制」一节的披露内容已被本轮修复取代，保留在上方作为
问题演进的历史记录。
