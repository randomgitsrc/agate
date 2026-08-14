# P1 progress (analyst)

- [x] 读派发指引 + analyst 角色 + P0-brief + TAG0010 P1/P2 参照
- [x] 现状调研：61 个 .bats（count-tests 口径 58/727 + sanity 6 + scripts 23）/ 526 行 helpers / pyproject.toml（ruff）
- [x] 每个 bats 文件 → 被测脚本映射（含 unit 46 / regression 6 / integration 6 / sanity / scripts 2）
- [x] helpers 迁移映射 + 文档重写清单 + Windows 冒烟评估
- [x] 批次规划：18 批（B0-B17），每批 3-6 文件（B9/B15/B17 单文件例外）

发现要点：
- pytest 9.0.3 在系统 python3 可用；venv 只有 ruff 0.16.3 无 pytest（需 pip install pytest 到 agate-dev venv）
- count-tests.sh 口径 = 58 文件 / 727 @test（unit+regression+integration，不含 sanity 与 scripts/）
- 全量迁移范围 = 61 个 .bats / 756 @test（含 sanity.bats 6 + scripts/check-platform-assumptions 16 + check-windows-smoke 7）
- helpers 迁移到 conftest.py：load.bash→AGATE_ROOT 解析、fixtures.bash→task_dir/git fixture、git-helper.bash→git fixture
- check-gate.bats（124）与 pre-commit-hook.bats（48）是超大批单文件，需内部拆子轮
- pyproject.toml 已有 ruff 规则集（py38 target），pytest 需并入同文件 [tool.pytest.ini_options]
