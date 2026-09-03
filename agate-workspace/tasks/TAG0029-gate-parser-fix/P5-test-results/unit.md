---
phase: P5
task_id: TAG0029
type: test-results
created: 2026-09-04
agent: verifier
---

# P5-test-results/unit.md — TAG0029 gate-parser-fix 技术验证

[PROD_NOT_TOUCHED]
[NO_NEED_CONFIRM]

> 命令来源：P2-design.md §4 gate_commands（逐条独立跑，不拼 `&&`）。
> 基线（dispatch-context objective_info，SELF-GATE 审查员独立实跑）：全量 1444 passed + 2 skipped；
> consistency 0 ERROR / 329 WARNING；count-tests 1446；扫描器 exit 0。

## cmd1 P5 全量 pytest

- cmd: `python3 -m pytest agate/tests/ -q --tb=no -n auto`（shell `timeout 900s`）
- 首次跑 exit: 1
- 首次跑签名：`1 failed, 1443 passed, 2 skipped in 41.38s`
- 首次 failed=1：`agate/tests/unit/test_agate_archive_stale_outputs.py::test_arch_4_double_archive_keeps_both_histories`
- 复跑（同命令）exit: 0
- 复跑签名：`1444 passed, 2 skipped in 37.75s`
- 复跑 failed=0
- flaky 判定（非预存失败，依据如下）：
  - 该失败单测单跑 exit 0（`1 passed in 1.07s`）；
  - 同文件整跑 exit 0（`7 passed in 1.79s`，`-n auto`）；
  - 全量复跑 exit 0（`1444 passed, 2 skipped`）；
  - 该测试文件内无本任务改动面引用（grep `gate-parser|read-gate-commands|check-tdd-red|platform-assumptions|gate_commands` 零匹配）；
  - 该测试为 archive 双归档时序类（`double_archive_keeps_both_histories`），属典型 xdist 并行时序敏感。
  - 基线为全绿（SELF-GATE 审查员独立实跑 1444 passed），故非"改动前就存在的预存失败"，记为本轮偶发 flaky（P5 卡 flaky 三振记录：失败出现 1 次，后续 3 次同域复跑全绿）。

## cmd2 P5_consistency

- cmd: `python3 agate/scripts/check-protocol-consistency.py --strict-errors-only`（shell `timeout 180s`，worktree 自有脚本）
- exit: 0
- 尾行签名：`仅有 329 个 WARNING，无 ERROR。`
- failed: 0（0 ERROR；WARNING 数 329 与基线一致）

## cmd3 P5_shellcheck

- cmd: `shellcheck -S warning agate/scripts/pre-commit-gate.sh agate/scripts/commit-msg-self-gate.sh agate/scripts/pre-push-gate.sh`（shell `timeout 180s`）
- exit: 0
- 输出签名：（无输出，干净通过）
- failed: 0

## cmd4 P5_count_tests

- cmd: `bash agate/tests/scripts/count-tests.sh`（shell `timeout 180s`）
- exit: 0
- 输出签名：`总计：1446 个测试用例（pytest collect-only 口径）`
- failed: 0（1446 与基线口径一致；1444 passed + 2 skipped = 1446）

## cmd5 P5_scanner

- cmd: `python3 agate/scripts/check-platform-assumptions.py agate/tests/`（shell `timeout 180s`）
- exit: 0
- 输出签名：（无输出，0 命中干净通过）
- failed: 0

## cmd6 P3_scanner

- cmd: `python3 agate/scripts/check-platform-assumptions.py agate/tests/`（shell `timeout 180s`，P3 常驻存在性验证）
- exit: 0
- 输出签名：（无输出，0 命中干净通过）
- failed: 0

## cmd7 P4_scanner

- cmd: `python3 agate/scripts/check-platform-assumptions.py agate/tests/`（shell `timeout 180s`，P4 checklist 跑通验证）
- exit: 0
- 输出签名：（无输出，0 命中干净通过）
- failed: 0

## 汇总

- 各命令 exit 码：cmd1 首次 1 / 复跑 0；cmd2 0；cmd3 0；cmd4 0；cmd5 0；cmd6 0；cmd7 0
- failed 计数：首次全量 1（偶发 flaky，复跑 0）；其余命令 0
- 本轮观察到的失败项见 `fail-list.txt`（1 项，附复跑已绿说明）
- runner 输出签名行：`1444 passed, 2 skipped in 37.75s`（复跑全绿） / `1 failed, 1443 passed, 2 skipped in 41.38s`（首次） / `仅有 329 个 WARNING，无 ERROR。` / `总计：1446 个测试用例（pytest collect-only 口径）`
- passed: 1444（复跑）；failed: 0（复跑）；skipped: 2

EXIT_CODE: 0
