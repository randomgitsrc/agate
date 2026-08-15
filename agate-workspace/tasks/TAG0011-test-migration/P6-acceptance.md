---
phase: P6
task_id: TAG0011-test-migration
type: acceptance
parent: P5-test-results/unit.md
trace_id: TAG0011-P6-20260815
status: draft
created: 2026-08-15
agent: verifier
# ── v2.0 机器汇总 ──
pass: 12
fail: 0
ui_affected: false
regression_pass: true
---

# P6 验收报告 — TAG0011 测试框架迁移（阶段二，bats → pytest）

> 任务：TAG0011（agate 测试框架迁移阶段二，bats → pytest；`change_type: refactor`）
> 阶段：P6 验收（refactor 回归验收口径，三段式）
> verifier：只读验证，未修改任何代码/测试/文档文件（仅产出本文件 + P6-evidence/）
> 时间：2026-08-15
> 工作目录：`/home/kity/oclab/agate/.worktrees/agate-TAG0010`（worktree 根）

## 一、行为不变声明

本次重构（bats → pytest）仅改变测试运行载体与内部实现，**不改变 agate 协议/产品脚本的外部行为**：
产品脚本（agate/scripts/*.py、薄壳 *.sh）在 TAG0010 已 py 化，本任务只迁移测试断言载体
（bats `@test` + `run/$status/$output` → pytest 用例 + conftest fixture），CLI 输出契约
（exit 0/1/2、`GATE ...:` 前缀、`AGATE_WORKSPACE=`/`AGATE_TASKS_DIR=` 两行输出、gate-result.json 结构、
sha256 字节稳定性）为固定断言对象，本任务不改契约只改载体。

判定依据 = **全量回归全绿（BDD-1）+ 关键路径行为不变断言 BDD-2~BDD-12 逐条 PASS**。
未新增任何功能性质 BDD（禁止伪造功能 BDD——refactor 任务的 BDD 全部是关键路径行为不变断言）。

## 二、全量回归全绿

- PASS BDD-1: 全量回归全绿——`python3 -m pytest agate/tests/ -q --tb=no` 实跑 748 passed / 2 skipped / 0 失败，尾行 `EXIT_CODE: 0`；`--collect-only` 收集 750 tests ≥ 749 迁移基线（60 .bats / 749 @test 全迁移 + check-windows-smoke.bats 退役，收集覆盖不减少）(P6-evidence/regression.log, P6-evidence/collect-only.log)

## 三、关键路径行为不变断言（逐条对照 P1 §7 BDD 条件）

- PASS BDD-2: consistency 0 ERROR 0 WARNING——`check-protocol-consistency.py --strict` 实跑 exit 0，CHECK 1-9 全部 PASS，`🎉 全部检查通过`；协议文档重写（§5 表 E）后一致性成立（对应 P1 BDD-2）(P6-evidence/consistency-strict.log)
- PASS BDD-3: ruff 静态检查覆盖全部 py 0 error——`~/.venvs/agate-dev/bin/ruff check agate/`（0.16.3）实跑 `All checks passed!` exit 0，src 含 `["agate/scripts", "agate/tests"]`（对应 P1 BDD-3）(P6-evidence/ruff.log)
- PASS BDD-4: count-tests.sh 改写为 pytest 收集计数——`bash agate/tests/scripts/count-tests.sh` 实跑 `总计：750 个测试用例（pytest collect-only 口径）`，退出 0，守护职责（≥ 749 基线）延续（对应 P1 §6.3）(P6-evidence/count-tests.log)
- PASS BDD-5: Windows CI 冒烟机制就位（minimal_validation 兜底）——`-m windows_smoke` 收集 78/750 代表用例；pyproject 已注册 marker；CI Windows 分支执行 `python -m pytest agate/tests/ -m windows_smoke`（protocol-tests.yml:38）。**本地 Linux 无法真机验证 windows-latest 实跑，按 P1 `requires_minimal_validation: true` + P2 §4.4 minimal_validation 兜底，标「待 Windows CI 确认」**（对应 P1 BDD-4，详见说明文件）(P6-evidence/windows-smoke-collect.log, P6-evidence/bdd5-windows-ci-note.md)
- PASS BDD-6: helpers fixture 行为等价——conftest 体系（AGATE_ROOT 反推 / task_dir / git_repo / run_cli）自检 `test_sanity.py` 6 + `test_helpers_python.py` 3 全绿（9 passed），全部依赖 fixture 的用例在全量回归中 0 失败（对应 P1 BDD-10）(P6-evidence/helpers-fixture.log)
- PASS BDD-7: 测试代码显式 encoding=utf-8——`test_agate_scripts_encoding.py`（encoding 守卫，扫 agate/tests/**/*.py 无 `open()/read_text()/subprocess.run(text=True)` 缺 encoding= 违规）2 passed（对应 P1 BDD-7）(P6-evidence/encoding-guard.log)
- PASS BDD-8: 测试代码兼容 Python 3.8+ 且平台无关——pyproject `target-version = "py38"`；`ast.parse(feature_version=(3,8))` 实扫 agate/tests + agate/scripts 共 108 文件 0 语法违规；`check-platform-assumptions.py` 对全树 0 R1-R5 命中（exit 0 干净树），且其自身行为测试 16 passed（非空转）（对应 P1 BDD-8）(P6-evidence/py38-compat.log, P6-evidence/ruff.log, P6-evidence/platform-scan.log)
- PASS BDD-9: CLI 输出契约与既有数据兼容——代表性契约用例实跑 179 passed（workspace-resolve 两行输出 10 / check-gate 124 / next-card sha256 字节稳定 22 / json-get stdin 8 / capture-env-baseline gate-result.json 15），断言对象（exit 0/1/2、`GATE ...:` 前缀、两行输出、gate-result.json、sha256）与 bats 时代一致（对应 P1 BDD-9）(P6-evidence/cli-contract.log)
- PASS BDD-10: pytest 全平台可跑——pytest 9.0.3 原生收集 750 tests，`-m windows_smoke` 选 78 代表用例（672 deselected）无收集错误，无 PytestUnknownMarkWarning（marker 已注册）（对应 P1 §6.2 评估结论）(P6-evidence/windows-smoke-collect.log)
- PASS BDD-11: 文档/CI 同步——`test_env_adapt_docs.py`（文档/CI 断言：shellcheck 收敛 3 薄壳 / ruff / windows-latest matrix / .gitattributes）9 passed；CI workflow 实测引用 pytest job + Windows `-m windows_smoke` 冒烟（对应 P1 §2.6 env-adapt-docs 迁移 + §5 表 E）(P6-evidence/env-adapt-docs.log)
- PASS BDD-12: Windows 冒烟机制决策落地——check-windows-smoke.sh / .bats 全仓库 0 残留，tests/ 下 0 个 .bats，`bats ` 二进制引用 0；CI Windows 冒烟 job 用 `python -m pytest agate/tests/ -m windows_smoke`，冒烟机制无 bats 依赖（对应 P1 BDD-12）(P6-evidence/windows-smoke-retired.log, P6-evidence/windows-smoke-collect.log)

## 总结

**Summary**: 12/12 PASS, 0 FAIL

- 全量回归：748 passed / 2 skipped（Pillow 可选分支 skipif，设计行为非失败）/ 0 failed，收集 750 ≥ 749
- 关键路径 BDD-2~BDD-12 全部 PASS，无 FAIL，无「调整/跳过/覆盖」中间态
- BDD-5（Windows CI 冒烟）按 `requires_minimal_validation: true` + P2 §4.4 minimal_validation 处理：
  本地验证 marker 机制/注册/CI 配置/Linux 全绿，**windows-latest 真机实跑待 CI 确认**（说明见
  `P6-evidence/bdd5-windows-ci-note.md`）；若 CI 失败将回退修复重验
- `ui_affected: false`（P1/P2 声明一致，无 UI，无 vision 需求）
