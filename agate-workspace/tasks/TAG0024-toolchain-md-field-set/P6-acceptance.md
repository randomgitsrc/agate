---
phase: P6
task_id: TAG0024
type: acceptance
parent: P5-verification.md
trace_id: TAG0024-P6-20260825
status: draft
created: 2026-08-25
agent: verifier
pass: 30
fail: 0
ui_affected: false
---

# P6 验收 —— TAG0024 toolchain-md-field-set

本文件为**汇总整合产出**：由三个证据并行批次（`md-field-set-tool` / `check-gate-debt-fixes` /
`phases-yaml-consistency`）各自独立实跑并产出的 `results.md` 转抄整合而成。汇总 verifier 不重新
执行测试，仅做格式统一 + 交叉核对；三批次的 PASS/FAIL 结论已经过主 Agent 逐条独立复核。

## 交叉核对结论

- P1-requirements.md 共声明 **30 条** BDD（BDD-1~30，`grep -c "^#### BDD-"` = 30，已核实）。
- 三批次 BDD 编号覆盖范围：
  - `md-field-set-tool`：BDD-1~19（连续，19 条）
  - `check-gate-debt-fixes`：BDD-20~24（连续，5 条）+ BDD-30（1 条，`[SCOPE+ from P4]`）
  - `phases-yaml-consistency`：BDD-25~29（连续，5 条）
- 三批次编号合集 = {1,2,...,29,30} = P1 全部 BDD-1~30，**无重复、无遗漏**（19+6+5=30，与 P1 声明总数精确对应）。
- 每条 PASS 引用的证据文件均已核实存在于 `P6-evidence/{batch}/` 对应目录下（逐一 `find` 核对，见下方产出自查）。
- 三批次结论：30 PASS / 0 FAIL。

## BDD 逐条结果

### 批次：md-field-set-tool（BDD-1~19）

- PASS BDD-1: 合法 key（`packages`）与合法 value 写入成功，`agate-md-field-get.py` 读回同值，`check-gate.py P2` 不再因该字段被阻断 (P6-evidence/md-field-set-tool/bdd-1.log)
- PASS BDD-2: 非法 key（`risks_level`）被拒绝，exit 非 0，输出含真实白名单成员 `risk_level` (P6-evidence/md-field-set-tool/bdd-2.log)
- PASS BDD-3: 合法 key 非法值（`status Approve`）被拒绝，输出含合法枚举 `approved`、字段归属角色、下一步建议 (P6-evidence/md-field-set-tool/bdd-3.log)
- PASS BDD-4: `agent: implementer`（非 review 角色）文件上写 `status approved` 被拒绝，输出提示字段归属角色 (P6-evidence/md-field-set-tool/bdd-4.log)
- PASS BDD-5: `--list` 输出包含 P2 阶段 phases.yaml 声明的全部 5 个 task_fields，与阶段 schema 一致 (P6-evidence/md-field-set-tool/bdd-5.log)
- PASS BDD-6: 写入 `candidate_count` 后输出含"剩余缺失"字段清单（而非仅报告写入成功） (P6-evidence/md-field-set-tool/bdd-6.log)
- PASS BDD-7: `agate-md-field-set-gate-commands.py` 写入合法 YAML 块 exit 0，`parse_gate_commands_block` 能正确解析写回文本，条目值与写入值一致 (P6-evidence/md-field-set-tool/bdd-7.log)
- PASS BDD-8: gate_commands 非法块（未声明阶段 key / 非法 `_timeout_seconds`）均被拒绝，exit 非 0，输出点名具体非法 key，文件保持写入前原样（2 个参数化用例） (P6-evidence/md-field-set-tool/bdd-8.log)
- PASS BDD-9: 10 个证据字段（9 个 `NO_FALLBACK_INT_FIELDS` + `regression_pass`）逐个 set 均被拒绝，exit 非 0，输出提示"该字段由验证脚本产出，不可手动填写"语义（首次共享 basetemp 出现 1 次瞬时假失败，改用批次专属隔离 basetemp 重跑全部 10 个参数化用例及失败用例本身各 2 次均 100% 稳定 PASS，与实现本身无关） (P6-evidence/md-field-set-tool/bdd-9.log)
- PASS BDD-10: monkeypatch `os.replace` 模拟写入中断后调用 `main()`，目标文件字节内容与写入前完全一致，未出现半成品 frontmatter (P6-evidence/md-field-set-tool/bdd-10.log)
- PASS BDD-11: FILE 指向不存在路径，exit 非 0，输出含"请先 Write 产出文件，再 set 字段"，且未创建该文件 (P6-evidence/md-field-set-tool/bdd-11.log)
- PASS BDD-12: 无 `---` frontmatter 块的文件写入字段后，新文件以 `---\n` 开头且以原正文全文结尾，正文逐字节保留 (P6-evidence/md-field-set-tool/bdd-12.log)
- PASS BDD-13: frontmatter 已存在、正文残留同名旧格式声明的文件上写入该 key，写入成功、输出含"残留"/"清理"提示、正文残留原样保留，get 读回值以 frontmatter 为准 (P6-evidence/md-field-set-tool/bdd-13.log)
- PASS BDD-14: 在真实 `P2-design.md` 基准文件上补齐最后一个必填字段后，`check-frontmatter.py` 校验 exit 0 (P6-evidence/md-field-set-tool/bdd-14.log)
- PASS BDD-15: 直接调用 `agate-frontmatter-check.py` 真实 `_check()` 取得期望错误列表，set CLI 的接受/拒绝结论与之一致，拒绝时 CLI 输出逐字包含 `_check()` 原始错误字符串（2 个参数化用例） (P6-evidence/md-field-set-tool/bdd-15.log)
- PASS BDD-16: 零协议知识模拟调用序列按 `--list` 输出逐项 set 直至无缺失，最终 `--list` 无剩余缺失且 `check-gate.py P2` 不再阻断 (P6-evidence/md-field-set-tool/bdd-16.log)
- PASS BDD-17: 白盒调用 `_writable_keys(rules_root)`，返回值等于 `GENERIC_HEADER_KEYS` ∪ 从真实 `phases.yaml` 动态计算的全部 `task_fields` 并集；`bump_type` 命中，虚构 key 不命中 (P6-evidence/md-field-set-tool/bdd-17.log)
- PASS BDD-18: 6 个追加/嵌套语义字段（`NO_FALLBACK_LIST_FIELDS` 5 个 + `dispatch_plan`）逐个 set 均被拒绝，exit 非 0，输出含"追加/嵌套/暂不支持"语义（6 个参数化用例） (P6-evidence/md-field-set-tool/bdd-18.log)
- PASS BDD-19: `dispatch-prompt.md`/`dispatch-context.md` 模板原文均提及 `agate-md-field-set`，旧的"直接复制 Header 代码围栏"字面指引已不存在 (P6-evidence/md-field-set-tool/bdd-19.log)

批次小计：19/19 PASS, 0 FAIL（35 个测试项全部通过，含 4 个参数化 BDD 共 16 个子用例）。

### 批次：check-gate-debt-fixes（BDD-20~24, BDD-30）

- PASS BDD-20: 描述列含字面 `|` 时不误判——`test_bdd_20_p8_roadmap_literal_pipe_in_title_not_misjudged` 1 passed (P6-evidence/check-gate-debt-fixes/bdd-20.log)
- PASS BDD-21: 既有合法表格判定结果不变（3 组参数化：not_done_matched_blocked / no_matching_row_not_blocked / done_matched_not_blocked）——`test_bdd_21_regression_existing_valid_roadmap_unchanged` 3 passed，串行复测一致（首次与 BDD-22 并行执行时出现 1 次瞬时假失败，排查为两个 pytest 进程并发写同一 `--basetemp` 目录的临时目录/夹具竞争，与 DEBT0019/DEBT0020 代码改动无关；串行重跑 3 次均 3 passed） (P6-evidence/check-gate-debt-fixes/bdd-21.log)
- PASS BDD-22: 非仓库根 CWD 下仍能正确定位——`test_bdd_22_p8_non_root_cwd_locates_roadmap` 1 passed (P6-evidence/check-gate-debt-fixes/bdd-22.log)
- PASS BDD-23: 仓库根不可得时给出区分性提示——`test_bdd_23_p8_repo_root_unavailable_distinct_warning` 1 passed (P6-evidence/check-gate-debt-fixes/bdd-23.log)
- PASS BDD-24: 既有合法场景（仓库根 CWD）判定结果不变——`test_bdd_24_regression_existing_repo_root_cwd_unchanged` 1 passed (P6-evidence/check-gate-debt-fixes/bdd-24.log)
- PASS BDD-30: check-pruning.py 的 staged 文件计数在测试环境下应隔离——`test_p2_6f_staged_source_count_uses_task_repo_not_outer_cwd_repo_exit_0` 1 passed；第二轮修复（GIT_CEILING_DIRECTORIES 兼容）后既有 3 用例保持绿：`test_p2_6e_prune_p7_coupling_checklist_exit_0` / `test_p2_52_yaml_list_phases_exit_0` / `test_p2_52b_yaml_list_phases_p3_pruned_low_exit_0` 均 PASSED (P6-evidence/check-gate-debt-fixes/bdd-30-p2-6f.log, P6-evidence/check-gate-debt-fixes/bdd-30-regression.log)

批次小计：PASS 6, FAIL 0（BDD-20/21/22/23/24/30 全部 PASS）。

### 批次：phases-yaml-consistency（BDD-25~29）

- PASS BDD-25: `agate/rules/phases.yaml` 中 `id: P4` 条目的 `outputs` 列表现已包含 `{file: P4-review.md, required: true, status_field: status}`，`test_bdd_25_p4_outputs_includes_review_md` 单独执行 PASSED（P3 阶段记录的红灯已由 P4 实现修复转绿） (P6-evidence/phases-yaml-consistency/bdd-25-pytest.log)
- PASS BDD-26: 补全后的 `phases.yaml` 跑真实 `check-structure-consistency.py` 二进制，S-1~S-6 双向一致性检查 exit code 0，未因 P4-review.md 声明产生新的不一致报错，`test_bdd_26_full_consistency_zero_mismatch_after_p4_outputs_fix` 单独执行 PASSED (P6-evidence/phases-yaml-consistency/bdd-26-pytest.log)
- PASS BDD-27: `agate/rules/phases.yaml` 中 `- id: P6.5` 条目前的注释块与 `agate/state-machine.md` 对 P6.5 性质的文字定位口径一致（均表达"P6.5 是挂载于 P6→P7 转移的强门槛子阶段，非独立 `.state.yaml` phase 值"），`test_bdd_27_phases_yaml_p65_comment_matches_state_machine_wording` 单独执行 PASSED（P3 阶段记录的红灯已由 P4 实现修复转绿） (P6-evidence/phases-yaml-consistency/bdd-27-pytest.log)
- PASS BDD-28: 口径统一后（纯注释改动）① `phases.yaml` 中 `P6.5` 条目 `yaml.safe_load` 解析结果字段值与补丁前逐一相等（注释对 YAML 解析器不可见）；② `check-gate.py P6.5 $TASK_DIR` 与 `check-judge-verdict.py` 在真实仓库根 / 补丁后协议树副本两种环境下 exit code 均为 0 且 stderr 逐字节相同，既有判定行为（`.state.yaml phase` 字段语义、事件账本记录、judge 复核轮次预算计数方式）不变，`test_bdd_28_p65_wording_fix_preserves_parsed_structure_and_gate_behavior` 单独执行 PASSED (P6-evidence/phases-yaml-consistency/bdd-28-pytest.log)
- PASS BDD-29: 对本任务 P4 commit `e2357fc` 的 diff 逐行核对，`agate/scripts/check-gate.py` 的改动范围仅限于：新增常量 `_ROADMAP_EXPECTED_COLS = 9`（DEBT0019 列数精确匹配）、`_check_roadmap_done()` 内 `len(cols) < 8` 改为 `len(cols) != _ROADMAP_EXPECTED_COLS`（DEBT0019 精确匹配修复）、`gate_p8()` 内 `roadmap_path` 从 CWD 相对拼接改为 `git rev-parse --show-toplevel` 仓库根锚定并对非 git 仓库环境增加 stderr 提示（DEBT0020 修复）——三处改动均落在 dispatch-context 圈定的 `_check_roadmap_done()`/`gate_p8()` 中 `roadmap_path` 定位相关行范围内，未触及其他判定逻辑；`agate/scripts/check-events.py` 在整条任务分支（`main..HEAD`）上 `git diff` 输出为空，零改动 (P6-evidence/phases-yaml-consistency/bdd-29-diff.log)

批次小计：PASS 5 / FAIL 0（BDD-25~29 全覆盖）。

## 附：批次内部交叉核对（转抄自 phases-yaml-consistency/results.md）

- P1-requirements.md BDD-25~29 共 5 条，本批次结果覆盖 BDD-25/26/27/28/29 共 5 条，PASS 5 / FAIL 0，编号无重复无遗漏。
- BDD-25/26/27/28 证据来源：`agate/tests/unit/test_check_structure_consistency.py` 对应测试函数单独执行（本次为 P6 重新独立实跑，非仅引用 P3 阶段自跑记录）。
- BDD-29 证据来源：`git show e2357fc -- agate/scripts/check-gate.py` + `git diff main..HEAD -- agate/scripts/check-gate.py` + `git diff main..HEAD -- agate/scripts/check-events.py`（跨全部任务提交范围核对，未局限于本批次改动）实际命令输出。

**Summary**: 30/30 PASS, 0 FAIL
