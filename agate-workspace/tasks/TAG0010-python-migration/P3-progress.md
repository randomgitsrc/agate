# P3 进度（test-designer，回归测试口径）

## 输入读取
- [x] P3-dispatch-context-test-designer.md（派发指引：refactor 回归口径 / 表 D / count-tests 不减少 / gate_commands）
- [x] test-designer.md 角色定义（refactor 节：回归口径 + 不跑 TDD 红灯 + 不新增功能行为断言）
- [x] AGENTS.md 项目约定（count-tests 口径 / fixtures / 平台无关原则）
- [x] P0-brief.md（任务简报：30 sh → py / 表 D 受影响 bats）
- [x] P1-requirements.md（10 BDD + 表 A-E 全读完）
- [x] P2-design.md（方案 A + §3.6 bats 断言改动方案 + gate_commands 全读）
- [x] fixtures.bash（detect_python/$PYTHON 约定：PYTHON 导出 + create_python_shim_bin + py_path）
- [x] 受影响 bats 文件核实（5 断言级逐文件 + 机械调用面 grep 实测）

## 基线核实
- count-tests.sh 实测：727 个 @test（58 文件 = unit 46 + regression 6 + integration 6；**count-tests 只数 unit/regression/integration，不含 sanity 6 + scripts/ 21**）
- 5 个断言级文件当前 @test 数：check-platform-assumptions 14 / env-adapt-docs 9 / agate-scripts-encoding 2 / helpers-python 3 / agate-workspace-resolve 10 = 38
- P2 §3.6 计划 check-platform-assumptions 14→16（+2 docstring 豁免用例）→ 断言级合计 38→40
- 关键：count-tests 口径 = `^@test` 行数，P4 改造后不得低于 727（count-tests 范围内）

## 关键发现（实测）
- 机械调用面：30 bats 文件直接 run（AGATE_SCRIPTS 272 + AGATE_ROOT/scripts 55，含全部 bash 调用形态 409+74）
- 受影响 bats 全树：34 文件直接 bash 调 .sh；51 文件含 AGATE_SCRIPTS 引用；合计 40 联动文件
- 断言级 5 文件逐条已核实（check-platform-assumptions 14 用例 / env-adapt-docs 9 / agate-scripts-encoding 2 / helpers-python 3 / agate-workspace-resolve 10）
- BDD→用例映射已梳理（BDD-1 全量 / BDD-2 consistency.bats+env-adapt-docs bdd-25 / BDD-3+4 env-adapt-docs bdd-34 改造 / BDD-5 check-windows-smoke.bats 7 / BDD-6 check-platform-assumptions.bats 14→16 / BDD-7 agate-scripts-encoding bdd-5 / BDD-8 agate-scripts-encoding bdd-8+ruff / BDD-9 pre-commit-hook bdd-19+install-hook+pre-push / BDD-10 agate-workspace-resolve 10+ci-gate-backstop）
- 批次→bats 清单已映射（批次 0-4，见 P3-test-cases.md §5）

## P3-test-cases.md 已产出
- 路径：agate-workspace/tasks/TAG0010-python-migration/P3-test-cases.md
- 自检：test_code_dir 声明 ✓ / 回归口径声明 ✓ / 覆盖映射表 ✓ / BDD 映射表 ✓ / 批次对应 ✓ / 用例数对照 ✓ / 无行首 PASS/FAIL ✓
