---
phase: P3
task_id: TAG0031
parent: P2-design.md
trace_id: TAG0031-P3-20260904
agent: test-designer
created: 2026-09-04
test_code_dir: agate/tests/unit/,agate/tests/regression/test_offline_bundle_roundtrip.py
---

# P3-test-cases.md — TAG0031 DEBT 存量修复批（三簇合并索引）

> 本文件由主 Agent 轻量拼装（模式 3 并行、无跨簇交叉修改，见 dispatch-protocol「派发编排机制」
> 模式 4 合并流程），三簇 test-designer subagent 各自独立产出，主 Agent 未新增测试内容判断，
> 只做索引汇总 + 全量红灯复核。三份完整批次文件保留在同目录，不重复粘贴全文。

## 三簇批次文件（BDD 全局编号 1~15，无重号，各簇互斥覆盖）

| 批次 | 覆盖 DEBT | 覆盖 BDD | 详情文件 |
|------|-----------|----------|----------|
| version-mgmt | DEBT0002/3/4 | BDD-1~5（+ R1 pyyaml 前置校验 2 条，归属 BDD-2） | `P3-test-cases-version-mgmt.md` |
| test-isolation | DEBT0007 | BDD-6（验证性，4 例已绿）/ BDD-7（真红灯） | `P3-test-cases-test-isolation.md` |
| gate-robustness | DEBT0016/17/18 | BDD-8~15（BDD-14 为登记动作，无自动化测试；BDD-11/13 为设计如此的回归守卫，本就绿） | `P3-test-cases-gate-robustness.md` |

## test_code_dir（三簇合并）

```
agate/tests/unit/                                    # 含 test_agate_common.py / test_agate_pack_offline.py /
                                                       # test_install_offline.py / test_agate_install_uninstall.py（新）/
                                                       # test_debt_registry_closure.py（新）/ test_check_gate.py
agate/tests/regression/test_offline_bundle_roundtrip.py   # 新文件，BDD-2 全流程回归
```

## 主 Agent 全量红灯复核（合并后，2026-09-04 本 worktree 实测）

命令：

```bash
timeout 180 python3 -m pytest agate/tests/unit/ agate/tests/regression/ agate/tests/integration/ -n auto -q --tb=no
```

结果：**21 failed, 1414 passed, 2 skipped**（三簇合计新增测试 23 个函数，其中 21 个为真红灯，
2 个为设计如此的回归守卫绿灯——`test_tag0031_bdd_11_*`/`test_tag0031_bdd_13_*`，见
`P3-test-cases-gate-robustness.md`）。

**一次性小插曲已修复**：首轮全量跑出 22 failed，多出的 1 项
`test_agate_scripts_encoding.py::test_bdd_5_all_test_py_text_io_explicit_encoding` 是
version-mgmt 簇新写测试代码里一处字符串字面量用单引号 `'rb'` 意外触发仓库既有 encoding 守卫
（该守卫只识别双引号 `"rb"`/`"wb"`），已由 test-designer 修正为双引号并复核该守卫测试转绿，
不影响任何 BDD 测试本身的红灯状态（诊断记录见 `P3-gate-diagnosis.md`）。

**逐项失败清单**（与三份批次文件的「实测红灯确认」节交叉核对，全部可追溯到具体 BDD 编号，
无遗漏无多余）：

```
test_agate_pack_offline.py::test_bdd_1_pack_offline_imports_compute_sha256_from_agate_common
test_agate_common.py::test_bdd_1_compute_sha256_file_hash_matches_hashlib
test_agate_common.py::test_bdd_1_compute_sha256_dir_hash_sorted_relpath_concat
test_agate_common.py::test_bdd_1_compute_sha256_single_definition_in_repo
test_agate_common.py::test_bdd_3_upgrading_doc_states_checksum_trust_boundary
test_agate_common.py::test_bdd_3_scripts_readme_states_checksum_trust_boundary
test_agate_install_uninstall.py::test_bdd_4_find_references_and_uninstall_warn_when_scan_limit_hit
test_agate_install_uninstall.py::test_bdd_5_find_references_no_warning_within_scan_bounds
test_check_gate.py::test_tag0031_bdd_8_gate_p4_code_map_uses_resolve_workspace
test_check_gate.py::test_tag0031_bdd_9_gate_p4_non_standard_nesting_resolves_via_agate_env
test_check_gate.py::test_tag0031_bdd_10_gate_p4_self_referential_prose_not_matched
test_check_gate.py::test_tag0031_bdd_12_gate_p1_read_rules_yaml_missing_fail_closed
test_check_gate.py::test_tag0031_bdd_12_gate_p6_count_pass_fail_missing_fail_closed
test_check_gate.py::test_tag0031_bdd_12_gate_p7_count_markers_missing_fail_closed
test_check_gate.py::test_tag0031_bdd_12_gate_p7_count_code_map_lines_missing_fail_closed
test_check_gate.py::test_tag0031_bdd_15_six_debts_registry_closed
test_install_offline.py::test_bdd_1_verify_checksums_uses_agate_common_compute_sha256
test_install_offline.py::test_r1_ensure_agate_common_bootstraps_when_yaml_unavailable
test_install_offline.py::test_r1_ensure_agate_common_rejects_pyyaml_checksum_mismatch_before_pip_install
test_debt_registry_closure.py::test_bdd_7_debt0007_status_closed_with_closure_fields
test_offline_bundle_roundtrip.py::test_bdd_2_pack_install_uninstall_roundtrip_no_behavior_change
```

21 项，与上表三簇分布（version-mgmt 12 - 1 已绿因不在此清单 = 实为按下方核对；test-isolation 1；
gate-robustness 8）逐一核对一致：version-mgmt 12 项测试中 `test_r1_*` 2 项 + `test_bdd_1/3/4/5*`
共 12 项全部在上方清单（无遗漏）；test-isolation 1 项（BDD-7）；gate-robustness 8 项（BDD-8/9/10/
12×4/15）。合计 12+1+8=21，与全量结果 21 failed 逐字对应。

## check-tdd-red.py 结论

见 `.state.yaml`/commit message；主 Agent 执行 `check-tdd-red.py` 的完整记录不落盘本文件正文
（gate 判定结果，非测试设计内容），执行方式与结果见本次 P3 commit 前的 gate 预跑记录。

## 已知设计约束 / 风险披露对照（供 P4 参考，索引指向明细）

- pyyaml checksum 前置校验闭环细节：`P3-test-cases-version-mgmt.md` §「已知设计约束」
- BDD-12 四个消费点的 fixture 构造差异（`count_code_map_lines` 与另外两个相反，字段已声明才调用）：
  `P3-test-cases-gate-robustness.md` §「与 P2-design.md 风险声明的对照」
- BDD-6/7 不改生产代码、DEBT0007 由 TAG0024 已修复的现状：`P3-test-cases-test-isolation.md`
