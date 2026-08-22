---
phase: P5
task_id: TAG0020
type: technical-verification
parent: P2-design.md
trace_id: TAG0020-P5-20260822-r3
status: draft
created: 2026-08-22
agent: verifier
---
# P5 技术验证结果（TAG0020 独立 Judge 机制）— P8 发布前重跑（r3）

[PROD_NOT_TOUCHED]
[NO_NEED_CONFIRM]

> 本轮为 P8 发布前 P5 全量重跑（audit7 判定 reuse_blocked——P7→P8 间有发布文件改动，P8 卡要求完整重跑）。release tag **v0.59.0（500e1ea）已创建并推送**，CHECK 7（badge vs tag）时序正确。此前 r1/r2 结果见 git 历史（P5 commit 741727d），本文件为覆盖后的当前有效版本。

## 运行签名（pytest 全量汇总，r3）

PASSED 1164
FAILED 2
SKIPPED 2
ok 1164（passed）
not ok 2（failed）

- 总计：1168 用例（2 failed + 1164 passed + 2 skipped），`2 failed, 1164 passed, 2 skipped in 112.84s`
- 完整实跑日志：`P5-test-results/full-run-4.log`（`pytest -q --tb=no --basetemp=agate-workspace/.pytest-tmp agate/tests/`，worktree 根，跑前已清理 scratch）
- git 基线：HEAD=500e1ea（P8 发布 commit），worktree 干净；test_bdd_5 保持绿（P4 修复已随 commit 741727d 落地）

## 命令逐条结果（r3）

| 命令 | exit | 结果 | 判定 |
|------|------|------|------|
| P5 全量 pytest（`python3 -m pytest -q --tb=no -p no:cacheprovider --basetemp=agate-workspace/.pytest-tmp agate/tests/`）| 1 | 2 failed / 1164 passed / 2 skipped | **FAIL（2 预存环境失败，0 本次引入）** |
| P5_consistency（`python3 agate/scripts/check-protocol-consistency.py --strict-errors-only`，worktree 自身脚本）| 0 | **0 ERROR**，318 WARNING（非阻断），**CHECK 7 PASS**（badge v0.59.0 vs tag v0.59.0） | PASS（干净协议态）|
| P5_count_tests（`bash agate/tests/scripts/count-tests.sh`）| 0 | 1168 用例 ≥ 749 基线，无漂移 | PASS |

> P5_consistency 两态对照（与 r1/r2 一致）：原样运行（`.pytest-tmp` 含全量会话残留）exit=1，ERROR(12) 全部指向 `agate-workspace/.pytest-tmp/test_*/` 下 pytest 生成的 fixture .md（扫描面误收测试临时目录，环境干扰非协议不一致）；清理 scratch 后重跑 = **0 ERROR / 318 WARNING / exit 0**（含 CHECK 7 badge-vs-tag 通过）。脏态日志 `consistency-dirty-3.log`、干净态日志 `consistency-clean-3.log`。

## failed 计数与分类（r3）

**failed = 2**（全部预存环境失败，0 本次改动引入）：

1. `test_check_routing.py::test_bdd_7_thin_score_anomaly_git_ok_false_exit_1` —— **预存失败（环境前提，非缺陷）**：
   "非 git 上下文→git_ok:false→exit 1" 前提在 basetemp 位于 worktree git 仓库内时失效（git_ok 实测 true → exit 0）。routing 代码未被本次改动触碰；TAG0019 先例 + P5-dispatch-context 客观查证已预告。隔离重跑仍失败（环境归属确认）。CI（basetemp 在仓库外）通过。已登记 known-failures.md 条目 1。
2. `test_env_adapt_docs.py::test_bdd_25_consistency_zero_error` —— **预存失败（环境干扰，非缺陷）**：
   全量会话中预存测试在 `.pytest-tmp` 生成含坏引用的 fixture .md，被一致性 CHECK 2 扫描面误收 → 12 ERROR → exit≠0。**清理 scratch 后隔离重跑 PASS**（环境归属实证）；一致性脚本扫描范围未被本次改动。CI（basetemp 在仓库外）通过。已登记 known-failures.md 条目 2。

> **P8 发布门槛状态**：本次改动引入失败 = 0；2 条预存环境失败已在 known-failures.md 登记并三轮（r1/r2/r3）复证归属不变（非缺陷，CI 全绿兜底）；consistency 0 ERROR（CHECK 7 badge/tag 时序正确）；count 1168 无漂移。

## 环境前提记录（本机约束）

- /tmp 只读 → basetemp 强制 `agate-workspace/.pytest-tmp`（worktree git 仓库内）→ 影响 bdd_7（非 git 上下文）与 bdd_25（一致性扫描面）两类用例，判定为环境前提，非产品缺陷（TAG0019 先例）。

## 签名行（gate 校验用）

PASSED 1164
FAILED 2
passed: 1164
failed: 2