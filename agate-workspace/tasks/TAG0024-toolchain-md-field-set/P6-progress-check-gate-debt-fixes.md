# P6 进度记录 —— 批次 check-gate-debt-fixes（证据并行子任务）

- 读取 verifier.md 角色定义 + dispatch-context（P6-dispatch-context-verifier-check-gate-debt-fixes.md）+ P1-requirements.md BDD-20~24/BDD-30 + P3-test-cases-check-gate-debt-fixes.md（测试函数映射）。
- BDD-20：`pytest -k bdd_20` → 1 passed。
- BDD-21：首次与 BDD-22 并行跑（同一 `--basetemp=.pytest-tmp`）时，`no_matching_row_not_blocked` 参数化用例出现瞬时 FAILED（returncode 1 != 期望 2）；单独重跑与再次全参数串行重跑（含追加 2 次复测）均 3/3 PASSED，判定为并行进程共享同一 basetemp 目录导致的临时目录/夹具碰撞，非代码缺陷。后续全部串行执行，避免复现。
- BDD-22：`pytest -k bdd_22` → 1 passed。
- BDD-23：`pytest -k bdd_23` → 1 passed。
- BDD-24：`pytest -k bdd_24` → 1 passed。
- BDD-30：`pytest -k test_p2_6f_staged_source_count_uses_task_repo_not_outer_cwd_repo_exit_0` → 1 passed；`pytest -k "test_p2_6e_ or test_p2_52_ or test_p2_52b_"` → 3 passed（第二轮修复后既有 3 用例保持绿）。
- 全部证据文件落盘 `P6-evidence/check-gate-debt-fixes/`，写 results.md。
