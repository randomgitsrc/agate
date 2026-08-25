---
phase: P6-evidence
task_id: TAG0024
batch: check-gate-debt-fixes
type: evidence-results
parent: P6-dispatch-context-verifier-check-gate-debt-fixes.md
agent: verifier
created: 2026-08-25
---

# P6 证据批次结果 —— check-gate-debt-fixes（BDD-20~24 + BDD-30）

本文件为**证据并行批次**产出，不是最终验收文件。汇总 verifier 将在整合阶段把以下结论转抄进
唯一的 `P6-acceptance.md`。

## 执行环境

- 命令统一加 `--basetemp=.pytest-tmp -p no:cacheprovider`，超时兜底 `timeout 90s`。
- 全部命令在本批次 verifier 内串行执行（发现一次并行执行导致的瞬时假失败，见 BDD-21 说明）。

## 逐条结果

- PASS BDD-20: 描述列含字面 `|` 时不误判——`test_bdd_20_p8_roadmap_literal_pipe_in_title_not_misjudged` 1 passed (bdd-20.log)
- PASS BDD-21: 既有合法表格判定结果不变（3 组参数化：not_done_matched_blocked / no_matching_row_not_blocked / done_matched_not_blocked）——`test_bdd_21_regression_existing_valid_roadmap_unchanged` 3 passed，串行复测一致（bdd-21.log）
- PASS BDD-22: 非仓库根 CWD 下仍能正确定位——`test_bdd_22_p8_non_root_cwd_locates_roadmap` 1 passed (bdd-22.log)
- PASS BDD-23: 仓库根不可得时给出区分性提示——`test_bdd_23_p8_repo_root_unavailable_distinct_warning` 1 passed (bdd-23.log)
- PASS BDD-24: 既有合法场景（仓库根 CWD）判定结果不变——`test_bdd_24_regression_existing_repo_root_cwd_unchanged` 1 passed (bdd-24.log)
- PASS BDD-30: check-pruning.py 的 staged 文件计数在测试环境下应隔离——`test_p2_6f_staged_source_count_uses_task_repo_not_outer_cwd_repo_exit_0` 1 passed (bdd-30-p2-6f.log)；第二轮修复（GIT_CEILING_DIRECTORIES 兼容）后既有 3 用例保持绿：`test_p2_6e_prune_p7_coupling_checklist_exit_0` / `test_p2_52_yaml_list_phases_exit_0` / `test_p2_52b_yaml_list_phases_p3_pruned_low_exit_0` 均 PASSED (bdd-30-regression.log)

## 说明：BDD-21 一次瞬时假失败的排查记录

首次执行时，BDD-21（`-k bdd_21`）与 BDD-22（`-k bdd_22`）在同一条 Bash 消息中并行发起、共享同一
`--basetemp=.pytest-tmp` 目录。该次运行中 `test_bdd_21_regression_existing_valid_roadmap_unchanged
[no_matching_row_not_blocked]` 出现 `AssertionError: assert 1 == 2`（returncode 1，预期 2）。
随后：
1. 单独重跑该参数化用例（`-k "bdd_21 and no_matching_row_not_blocked"`）→ PASSED。
2. 串行重跑 BDD-21 全部 3 组参数化，连续 3 次（含落盘证据的最终一次）→ 均 3 passed。

结论：该失败为两个 pytest 进程并发写入同一 `--basetemp` 目录产生的临时目录/夹具竞争，与
DEBT0019/DEBT0020 代码改动无关，不构成真实回归。落盘的 `bdd-21.log` 为最终串行确认结果
（3 passed），为本条 BDD 的正式证据。

**Summary**: PASS: 6, FAIL: 0（BDD-20/21/22/23/24/30 全部 PASS）
