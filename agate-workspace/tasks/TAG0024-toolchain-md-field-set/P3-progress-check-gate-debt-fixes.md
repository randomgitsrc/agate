---
phase: P3
task_id: TAG0024
type: progress
batch: check-gate-debt-fixes
agent: test-designer
---

# P3 进度日志（批次 check-gate-debt-fixes）

## 已读输入
- dispatch-context: P3-dispatch-context-test-designer-check-gate-debt-fixes.md（目标/约束/BDD-20~24 构造要点已消化）
- test-designer.md 角色定义
- P1-requirements.md BDD-20~24（DEBT0019 列数校验 + DEBT0020 仓库根锚定）
- P2-design.md §1.1 改动落点表 / §3.6（`_ROADMAP_EXPECTED_COLS = 9`）/ §3.7（`_repo_root()` + `gate_p8()` 改造）
- agate/tests/unit/test_check_gate.py 1300-1580 区域：既有 fixture（`_run_gate`/`_init_repo_with_task`/`_init_p8_repo`/`_write_p8_release`/`_write_roadmap`）与既有三用例 `test_bdd_5/6/7`
- agate/scripts/check-gate.py 现状确认：`_check_roadmap_done()`（1181-1202 行，`len(cols) < 8`）、`gate_p8()`（1205-1231 行，`roadmap_path = os.path.join("agate-workspace", "roadmap", "roadmap.md")` CWD 相对拼接，1224 行）

## 设计要点
- BDD-20：构造标题列含字面 `|` 的畸形行（split 后 10 列，≥8 但 ≠9），刻意把"来源"列写成 "T001"（默认 task_id），使现有 `< 8` 判据下错位取值后 `related_task` 恰好等于 task_id 而 `status` 被错位成非 done 值 → 现有实现会误判阻断（exit 1）；修复后按精确列数应整行跳过（exit 2，不含 RM 编号）。新增 `_write_roadmap_raw()` helper 写畸形原始行（`_write_roadmap()` 只能生成规整 9 列行，不够用）。
- BDD-21：复用 `_write_roadmap()` + 参照 `test_bdd_5/6/7` 三场景，改写为一个 `pytest.mark.parametrize` 用例，断言列数精确匹配修复不改变既有合法表格三种场景的判定结果（回归口径，非要求红灯）。
- BDD-22：`_init_p8_repo` 已把 task 复制进 `repo/task`；用 `cwd=str(repo / "task")` + `task_arg="."` 模拟非仓库根 CWD，断言修复后仍能定位到 `repo/agate-workspace/roadmap/roadmap.md` 并正确阻断（exit 1）——现有 CWD 相对拼接在此 cwd 下找不到文件，会得 exit 2，构成真红灯。
- BDD-23：用 `GIT_CEILING_DIRECTORIES` 环境变量在非 git 目录场景下阻止 git 向上找到外层 worktree 仓库（本机 basetemp 落在 worktree 内，纯建空目录不足以模拟"非 git 环境"，需要 ceiling 边界兜底，已用 bash 实测确认该技巧有效）；断言输出含"仓库根不可得"区分性提示（现有实现无此提示，真红灯）。
- BDD-24：与 BDD-21 对称，复用同一批既有场景但显式在 `cwd=str(repo)`（仓库根）下运行，断言 DEBT0020 锚定修复不改变既有仓库根 CWD 场景的判定结果（回归口径）。

## 执行结果
- 已在 agate/tests/unit/test_check_gate.py 末尾（`test_bdd_7_...` 之后、`8g:` 分组之前）纯追加 156 行：新增 `_write_roadmap_raw()` helper + 5 个测试函数（BDD-21 为 3 组参数化）。
- 红灯确认：`-k "bdd_20 or bdd_21 or bdd_22 or bdd_23 or bdd_24"` → `3 failed, 4 passed`；BDD-20/22/23 均 AssertionError（真红灯，B 类），BDD-21（3 组）+ BDD-24（1 组）PASSED（回归口径，符合预期不要求红灯）。
- 全量回归：`python3 -m pytest agate/tests/unit/test_check_gate.py --basetemp=.pytest-tmp -p no:cacheprovider -q` → `3 failed, 179 passed`，既有用例（含 test_bdd_5/6/7、G8 系列）全部保持绿色。
- `git diff --stat` 确认 `156 insertions(+)`，0 处删除，纯追加。
- 已写 P3-test-cases-check-gate-debt-fixes.md（含 header + BDD-20~24 逐条测试函数名与断言说明 + 红灯确认记录）。
- 状态：本批次任务完成。
