# P6-progress — TAG0022 验收（verifier）

> 状态标记：[PROD_NOT_TOUCHED]（仅读协议/代码文件；写操作全部落在 P6-evidence/、P6-acceptance.md、P6-progress.md）
> 环境：Linux；/tmp 只读 → pytest `-p no:cacheprovider --basetemp=<可写目录>`；双工作区纪律
> 验收对象：worktree `/home/kity/oclab/agate/.worktrees/agate-TAG0022`，HEAD `712bb0c`（wf(TAG0022-P5)）

## BDD 验收进度（逐条落盘）

- [x] BDD-1（ruff job + 配置步骤文档）：workflow L106-117 稳定 `name: ruff` + `ruff==0.16.4` 锁版本；UPGRADING.md L97-109 required check 配置步骤 + AGENTS.md L157 → PASS（证据 bdd-01-workflow-docs.log）
- [x] BDD-2（ruff 零违规）：`~/.venvs/agate-dev/bin/ruff check agate/` 双跑均 exit 0（All checks passed!，ruff 0.16.4）→ PASS（证据 bdd-02-ruff.log）
- [x] BDD-3（静态扫描清零）：`pytest agate/tests/unit/test_md_parse_scan.py` 1 passed exit 0（A/B/C/D 组命中=0 断言通过）→ PASS（证据 bdd-03-scan.log）
- [x] BDD-5（S-3 双向收紧）：`pytest agate/tests/unit/test_check_structure_consistency.py` 13 passed exit 0（含 S-3a/S-3b 漂移 + 双侧一致用例）→ PASS（证据 bdd-05-s3.log）
- [x] BDD-6/7（judge P1 校验 + 历史跳过）：`pytest agate/tests/unit/test_check_gate.py` 172 passed exit 0（judge P1 六用例 + gate_p65 三态）→ PASS（证据 bdd-06-07-judge.log）
- [x] BDD-4 子项 2/3/4：count-tests 1215 ≥ 1202（exit 0）；consistency 0 ERROR（321 WARNING 历史类）；structure S0-S6 全 OK → 已落证据 bdd-04-gates.log
- [x] BDD-4 子项 1：全量 pytest（外部 basetemp ptmp）1213 passed, 2 skipped, exit 0 → 证据 bdd-04-full-pytest.log
- [x] BDD-10（平台无关）：check-platform-assumptions.py exit 0（R1-R5 0 命中）+ 修改点 diff 人工核对无单平台假设 → PASS（证据 bdd-10-platform.log）
- [x] BDD-8（实证计划落盘）：P2-design.md §4.4.1 L203-211 四要素 + 触发条件齐全、各可二值判定；已知边界 L213 → PASS（证据 bdd-08-plan-check.md）
- [x] BDD-9 双位置全量 pytest：位置 1（外部 ptmp）1213 passed, 2 skipped, 0 failed exit 0；位置 2（仓库内 agate/.bt-p6-verify）1213 passed, 2 skipped, 0 failed exit 0（跑完 rm -rf 已清理，git 状态干净）→ PASS（证据 bdd-09-dual-position.log, bdd-09-pytest-inrepo.log）
- [x] BDD 验收汇总：10/10 PASS，0 FAIL（frontmatter pass: 10 / fail: 0 / ui_affected: false）
- [x] gate 预检（稳定版 ~/.agate scripts）：check-p6-format.py --fix exit 0；check-p6-evidence.py exit 0（10 BDD，证据目录非空）；check-p6-provenance.py exit 0；check-gate.py P6 exit 2（FAIL=0，NC=0，P6_TOTAL=10，标准"通过-需主 Agent 自判"态）
- [ ] 返回主 Agent：P6-acceptance.md 路径 + 摘要（10 PASS / 0 FAIL）
