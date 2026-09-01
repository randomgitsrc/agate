2026-08-31 13:59:52 将跑 P5 全量 pytest（python3 -m pytest agate/tests/ -q --tb=no），预期 60-300s，timeout 600
2026-08-31 14:03:05 P5 全量 pytest 完成：exit 0，1333 passed / 2 skipped / 0 failed，耗时 150.77s（未分片，全量一次跑完）
2026-08-31 14:03:05 将跑 P5_consistency（check-protocol-consistency.py --strict-errors-only），预期 <30s，timeout 120
2026-08-31 14:04:07 P5_consistency 完成：exit 0，ERROR=0，WARNING=323（--strict-errors-only 只按 ERROR 判失败 → pass）
2026-08-31 14:04:07 将跑 P5_count_tests（bash agate/tests/scripts/count-tests.sh），预期 <30s，timeout 60
2026-08-31 14:04:59 P5_count_tests 完成：exit 0，总计 1335（≥749 迁移基线；P0 基线 1308 + P3 新增 27 = 1335，只增不减吻合）
2026-08-31 14:04:59 将跑 P5_ruff（~/.venvs/agate-dev/bin/ruff check agate/scripts/ agate/tests/unit/），预期 <15s，timeout 60
2026-08-31 14:05:38 P5_ruff 完成：exit 0，All checks passed!
2026-08-31 14:05:38 将跑 P5_shellcheck（shellcheck -S warning agate/scripts/*.sh），预期 <15s，timeout 60
2026-08-31 14:15:59 产出落盘完成：unit.md（含签名计数块）+ fail-list.txt（空文件，无失败）
