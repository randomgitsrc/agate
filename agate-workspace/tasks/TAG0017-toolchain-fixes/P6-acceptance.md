---
phase: P6
task_id: TAG0017-toolchain-fixes
type: acceptance
parent: P5-verification.md
trace_id: TAG0017-P6-20260820
status: draft
created: 2026-08-20
agent: verifier
pass: 12
fail: 0
ui_affected: false
---

[NO_NEED_CONFIRM]

[PROD_NOT_TOUCHED]

本任务无 UI 受影响面（domains 不含 frontend），无需 vision-analyst/Playwright/截图，遵 dispatch-context 指引以定向 pytest 输出作为证据。

## 功能分组 1：gate_commands 是执行机制、env_constraints 是声明性字段（DEBT0010 + DEBT0015）

- PASS BDD-1: P2 阶段声明 `{key}_timeout_seconds`（如 `P5_timeout_seconds: 120`）不再被 4 个解析脚本（`agate-read-gate-commands.py`/`agate-gate-missing-cmds.py`/`agate-gate-p5-count.py`/`agate-read-p5-commands.py`）误判为待核实命令，`test_gmc_3_bdd_1_timeout_seconds_key_not_treated_as_missing_command`、`test_p5c_5_bdd_1_3_timeout_seconds_not_treated_as_command`、`test_pyx_7_bdd_1_timeout_seconds_excluded_from_commands` 均实跑通过 (P6-evidence/bdd-1-2-3-4.log)
- PASS BDD-2: 同时声明 `P3_timeout_seconds` 与真实失败的 P3 命令时，`check-tdd-red.py` 判定结果仍为 A 类真实失败，未因新增排除逻辑被放宽，`test_bdd_2_timeout_seconds_declared_real_a_class_failure_stays_a_class` 实跑通过 (P6-evidence/bdd-1-2-3-4.log)
- PASS BDD-3: `agate-gate-p5-count.py` 对 `P5:` 主命令 + `P5_timeout_seconds` 辅助键统计为"1 主命令 + 0 辅助命令"，`test_gpc_4_bdd_3_timeout_seconds_excluded_from_aux_count` 实跑通过 (P6-evidence/bdd-1-2-3-4.log)
- PASS BDD-4: 同类遗漏拦截机制已落地为共享判据函数 `agate_common.is_gate_meta_key()` + 专用审计用例，`test_bdd_4_formatter_excluding_scripts_also_exclude_timeout_seconds` 实跑通过（验证仓库内所有排除 `_formatter` 后缀的脚本同时排除 `_timeout_seconds` 后缀，能捕获未来新增遗漏点） (P6-evidence/bdd-1-2-3-4.log)
- PASS BDD-5: `env_constraints` 声明性字段与 `gate_commands` 执行机制的语义边界已文档化于 `P2-design.md`「gate_commands 声明」节与 `architect.md`，`test_bdd_5_p2_design_gate_commands_section_states_env_constraints_is_declarative`、`test_bdd_5_architect_role_states_env_constraints_is_declarative` 实跑通过，断言文档明确给出"env_constraints 仅信息注入，需强制执行的约束必须落到 gate_commands 或 P4/P8 checklist"的结论 (P6-evidence/bdd-5-6-9doc.log)
- PASS BDD-6: `phase-cards/P4-implementation.md`「自查≠gate」节已新增"UI/需构建任务 P4 后应构建并确认 dist 类产物存在"的显式提醒条目，`test_bdd_6_p4_implementation_self_check_section_has_dist_build_reminder` 实跑通过 (P6-evidence/bdd-5-6-9doc.log)

## 功能分组 2：SELF-GATE 审查文件命名去重（DEBT0011）

- PASS BDD-7: 命名模板已补 `{task_id}`（留痕文件 `agate-alignment-{date}-{task_id}-{NN}.progress.md`、成果文件 `agate-alignment-review-{date}-{task_id}.md`），同日不同任务生成文件名不再相同，`test_bdd_7_naming_template_produces_distinct_filenames_for_different_task_ids` 等 6 条实跑通过 (P6-evidence/bdd-7-8.log)
- PASS BDD-8: `protocol-alignment-review.md` 已新增 Write 前存在性检查段落，区分"同一任务复核轮可覆盖"与"别的任务遗留不可覆盖"两分支，`test_bdd_8_protocol_alignment_review_has_write_precheck_logic`、`test_bdd_8_write_precheck_distinguishes_same_task_vs_other_task` 实跑通过 (P6-evidence/bdd-7-8.log)

## 功能分组 3：check-protocol-consistency --strict 与 && 链路短路修复（DEBT0012）

- PASS BDD-9: 新增 `--strict-errors-only` 互斥模式，WARNING-only（0 ERROR、314 条历史 WARNING）场景下 exit 0，`test_strict_errors_only_zero_error_n_warning_exit_0_with_hint` 等 3 条单测实跑通过 (P6-evidence/bdd-9-code.log)；另实跑模拟 `gate_commands.P5` 链路 `check-protocol-consistency.py --strict-errors-only && echo NEXT_STEP_REACHED`，实测输出 0 ERROR/314 WARNING、exit 0、`NEXT_STEP_REACHED` 被打印，证明链路后续步骤确实被执行到、未被短路跳过 (P6-evidence/bdd-9-chain-behavior.log)。文档半（P2-design.md 新增 `--strict` 反模式指引）见 BDD-5 同批证据 (P6-evidence/bdd-5-6-9doc.log)

## 功能分组 4：Windows Store python3 占位符命中 hook 探测循环（DEBT0014）

- PASS BDD-10: 探测循环命中不可执行候选（`python3`）时能跳过并继续尝试下一候选（`python`），最终解析到可执行解释器，3 个 hook 薄壳（pre-commit/commit-msg/pre-push）各自的 `test_bdd_10_probe_skips_unexecutable_candidate` 用例（Linux 上构造模拟不可执行候选的回归测试）实跑全部通过，Windows 真实场景由 CI matrix `pytest -m windows_smoke` 冒烟兜底（本地无法真实复现，未夸大声称已在真实 Windows 环境实测通过） (P6-evidence/bdd-10-11.log)
- PASS BDD-11: 显式指定 `AGATE_PYTHON` 环境变量时 3 个 hook 薄壳直接使用该路径、跳过 `command -v` 探测循环，`test_bdd_11_agate_python_explicit_override_skips_probe_loop`（3 hook 各一条）实跑全部通过 (P6-evidence/bdd-10-11.log)
- PASS BDD-12: `platform-notes.md`「已知限制（Windows 原生）」表与 `AGENTS.md`「Gate 脚本分层」节已记录 Store 占位符现象说明 + `AGATE_PYTHON` 显式指定路径机制的文档条目，且经断言确认文案不含"已在 Windows 实测通过"一类夸大表述，`test_bdd_12_platform_notes_documents_store_placeholder`、`test_bdd_12_platform_notes_no_overclaim`、`test_bdd_12_agents_md_documents_agate_python_probe_enhancement`、`test_bdd_12_agents_md_no_overclaim` 等 5 条实跑通过 (P6-evidence/bdd-12.log)

**Summary**: 12/12 PASS, 0 FAIL
