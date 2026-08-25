---
phase: P6
task_id: TAG0023-mechanism-checks
type: acceptance
parent: P5-verification.md
trace_id: TAG0023-P6-20260825
status: draft
created: 2026-08-25
agent: verifier
# ── v2.0 机器汇总 ──
pass: 13
fail: 0
ui_affected: false
---

# P6-acceptance.md — TAG0023 机制校验补强批 验收报告

> [PROD_NOT_TOUCHED] 本轮只读运行测试命令，不涉及生产环境。
> BDD-9 已由主 Agent 完成 5 次真实 CI 触发验证，13 条 BDD 全部有结论。

## 6.1 RM-AG0042 门槛失败事件强制记录 retries

- PASS BDD-1: 评审 rejected 类门槛失败事件的对应性校验用例全部通过——`test_check_state_transition.py` 中 `bdd_1` 前缀 6 个用例（缺 retries 记录时 WARNING / 有记录时无 WARNING / 无触发文件不误报 / 两个负面锚点 `implementer-review-fix`、`consistency-reviewer` 均不误命中 / 多阶段命中场景）全部 PASSED (P6-evidence/bdd-1-pytest.log)
- PASS BDD-2: P5→P4 回退类门槛失败事件的对应性校验用例全部通过，含首次单步回退回归用例 `test_bdd_2_first_time_retreat_both_sides_empty_retries_exit_1` (P6-evidence/bdd-2-pytest.log)
- PASS BDD-3: 子代理空返回重派类门槛失败事件的对应性校验用例全部通过，含分批命名回归用例 `test_bdd_3_progress_batch_named_file_detected` (P6-evidence/bdd-3-pytest.log)
- PASS BDD-4: 正常路径回归防呆用例通过——无门槛失败事件 + retries 为空 → exit 0 无 WARNING (P6-evidence/bdd-4-pytest.log)

## 6.2 RM-AG0043 P8 roadmap 回写 done 校验（含历史补记）

- PASS BDD-5: P8 gate 关联 roadmap RM 条目未回写 done 时被拦截（exit 1）用例通过 (P6-evidence/bdd-5-pytest.log)
- PASS BDD-6: 无关联 RM 记录时不误拦（exit 0 继续既有流程）用例通过 (P6-evidence/bdd-6-pytest.log)
- PASS BDD-7: RM-AG0032 历史数据已补记为 done——单测 `test_bdd_7_roadmap_rm_ag0032_backfilled_done` 通过，且直接 grep roadmap.md 实测确认 L32 存在 `RM-AG0032 | ... | done | ... | 2026-08-24 |` 记录行（真实数据 + 测试双证据） (P6-evidence/bdd-7-pytest.log, P6-evidence/bdd-7-roadmap-grep.log)

## 6.3 RM-AG0044 环境敏感测试集中治理

- PASS BDD-8: 复现定位计划 + 已知证据基线四要素齐全断言用例通过，含 `test_bdd_8_recon_plan_and_known_baseline_four_elements`（已知证据基线/判定标准/集中清单位置/CI flaky 重跑触发条件四要素均核对存在） (P6-evidence/bdd-8-pytest.log)
- PASS BDD-9: test_bdd_14 连续 5 次真实 GitHub Actions CI（protocol-tests.yml）触发均 conclusion=success，`gh run view <id> --log | grep -c FAILED` 对每次运行均返回 0（run id 32800038697/32800344966/32800650000/32800954146/32801251214，跨 push 事件、覆盖 ubuntu-latest 与 windows-latest 双平台），RM-AG0044 根因修复（check-debt.py 改用动态 git rev-parse --short 替代固定 full[:7] 切片）已实证生效 (P6-evidence/bdd-9-ci-runs.log)
- PASS BDD-10: 环境敏感测试集中清单存在性用例通过——`agate/tests/ENV-SENSITIVE-TESTS.md` 存在且含 `test_bdd_7`/`test_bdd_25`/`test_bdd_14` 三条目（各含根因分类字段） (P6-evidence/bdd-10-pytest.log)

## 6.4 RM-AG0045 声明写时校验

- PASS BDD-11: dispatch-prompt.md 含"P1/P2 声明写时自检"小节文本的断言用例通过 (P6-evidence/bdd-11-pytest.log)
- PASS BDD-12: 错误信息含具体行号/字段定位与修复提示的断言用例通过，含缺失必填字段错误提示、非法枚举值错误提示两类用例 (P6-evidence/bdd-12-pytest.log)
- PASS BDD-13: commit 时格式折返归零——TAG0019 三类历史用例（coupling_checklist 非 list 声明 / 全角冒号 / 源码数 6>5）在写时全部被拦截的回归用例全部通过 (P6-evidence/bdd-13-pytest.log)

## 证据说明

所有证据文件均为真实跑出的 pytest 命令输出（含 PASSED 签名行），保存于 `P6-evidence/` 目录，
详细命令与结果见 `P6-progress.md`。BDD-7 额外附真实 `grep` roadmap.md 输出作为数据实证；BDD-9
附主 Agent 5 次真实 GitHub Actions CI 触发记录（run id + conclusion + FAILED 计数核实方式）。

**Summary**: 13/13 PASS, 0 FAIL
