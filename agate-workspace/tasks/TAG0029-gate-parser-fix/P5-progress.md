# P5-progress — TAG0029 verifier

## cmd1 P5全量
- cmd: `python3 -m pytest agate/tests/ -q --tb=no -n auto` (timeout 900s)
- exit: 1
- tail: `1 failed, 1443 passed, 2 skipped in 41.38s`
- failed: `agate/tests/unit/test_agate_archive_stale_outputs.py::test_arch_4_double_archive_keeps_both_histories`

## cmd2 P5_consistency
- cmd: `python3 agate/scripts/check-protocol-consistency.py --strict-errors-only` (timeout 180s, worktree自有脚本)
- exit: 0
- tail: `仅有 329 个 WARNING，无 ERROR。`

## cmd3 P5_shellcheck
- cmd: `shellcheck -S warning agate/scripts/pre-commit-gate.sh agate/scripts/commit-msg-self-gate.sh agate/scripts/pre-push-gate.sh` (timeout 180s)
- exit: 0
- tail: (无输出，干净通过)

## cmd4 P5_count_tests
- cmd: `bash agate/tests/scripts/count-tests.sh` (timeout 180s)
- exit: 0
- tail: `总计：1446 个测试用例（pytest collect-only 口径）`

## cmd5 P5_scanner
- cmd: `python3 agate/scripts/check-platform-assumptions.py agate/tests/` (timeout 180s)
- exit: 0
- tail: (无输出，0命中干净通过)

## cmd6 P3_scanner
- cmd: `python3 agate/scripts/check-platform-assumptions.py agate/tests/` (timeout 180s, P3常驻存在性验证)
- exit: 0
- tail: (无输出，0命中干净通过)

## cmd7 P4_scanner
- cmd: `python3 agate/scripts/check-platform-assumptions.py agate/tests/` (timeout 180s, P4 checklist跑通验证)
- exit: 0
- tail: (无输出，0命中干净通过)

[PROD_NOT_TOUCHED]
[NO_NEED_CONFIRM]

## cmd1-followup 全量复跑（flaky确认）
- cmd: 同cmd1（timeout 900s）
- exit: 0
- tail: `1444 passed, 2 skipped in 37.75s`
- 结论: 首次1 failed为偶发flaky（单跑/整文件/复跑皆绿，改动面无引用）；详情见P5-test-results/unit.md
