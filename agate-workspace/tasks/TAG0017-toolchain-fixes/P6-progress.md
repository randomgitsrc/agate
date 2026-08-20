# P6 Progress Log - TAG0017-toolchain-fixes
Started: 2026-08-20T12:53:42+08:00

## BDD-1/2/3/4 (fg1-parser-scripts)
pytest agate/tests/unit/test_gate_key_suffix_audit.py test_agate_common.py test_check_tdd_red.py test_agate_gate_missing_cmds.py test_agate_gate_p5_count.py test_agate_read_p5_commands.py -v
结果: 71 passed, exit 0 (P6-evidence/bdd-1-2-3-4.log)
BDD-4 专用审计用例 test_bdd_4_formatter_excluding_scripts_also_exclude_timeout_seconds PASSED（line 10）

## BDD-5/6/9(doc half)
pytest agate/tests/unit/test_p2p4_boundary_docs.py -v
结果: 5 passed, exit 0 (P6-evidence/bdd-5-6-9doc.log)

## BDD-7/8
pytest agate/tests/unit/test_self_gate_naming_docs.py -v
结果: 8 passed, exit 0 (P6-evidence/bdd-7-8.log)

## BDD-9 (code half)
pytest agate/tests/unit/test_check_protocol_consistency.py -k strict_errors_only -v
结果: 3 passed, exit 0 (P6-evidence/bdd-9-code.log)
补充实跑链路证据: check-protocol-consistency.py --strict-errors-only && echo NEXT_STEP_REACHED
结果: 0 ERROR/314 WARNING, exit 0, NEXT_STEP_REACHED 打印（P6-evidence/bdd-9-chain-behavior.log），证明链路未短路

## BDD-10/11
pytest agate/tests/integration/test_pre_commit_hook.py -k "bdd_10_probe or bdd_11_agate_python" -v
结果: 6 passed (3 hooks x 2 BDD), exit 0 (P6-evidence/bdd-10-11.log)

## BDD-12
pytest agate/tests/unit/test_windows_python_probe_docs.py -v
结果: 5 passed, exit 0 (P6-evidence/bdd-12.log)

## 结论
全部 12 条 BDD 实跑确认 PASS，0 FAIL。所有证据文件非空、含实质 pytest 输出。
