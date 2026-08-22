---
phase: P5
task_id: TAG0020
type: technical-verification
parent: P2-design.md
trace_id: TAG0020-P5-20260822-r2
status: draft
created: 2026-08-22
agent: verifier
---
# P5 技术验证结果（TAG0020 独立 Judge 机制）— 重跑（r2，P4 修复后）

[PROD_NOT_TOUCHED]
[NO_NEED_CONFIRM]

> 本轮为 P4 修复 `test_agate_common.py` BDD-5 编码违规后的 P5 全量重跑（P5 命令集 3 条全部重执行）。首页（r1）结果见 git 历史，本文件为覆盖后的当前有效版本。

## 运行签名（pytest 全量汇总，r2）

PASSED 1164
FAILED 2
SKIPPED 2
ok 1164（passed）
not ok 2（failed）

- 总计：1168 用例（2 failed + 1164 passed + 2 skipped），`2 failed, 1164 passed, 2 skipped in 112.05s`
- 完整实跑日志：`P5-test-results/full-run-3.log`（`pytest -q --tb=no --basetemp=agate-workspace/.pytest-tmp agate/tests/`，worktree 根，跑前已清理 scratch）
- **test_bdd_5_all_test_py_text_io_explicit_encoding 已转绿** ✓（P4 修复 test_agate_common.py 4 处 open() 补 encoding='utf-8'，工作树已核对）

## 命令逐条结果（r2）

| 命令 | exit | 结果 | 判定 |
|------|------|------|------|
| P5 全量 pytest（`python3 -m pytest -q --tb=no -p no:cacheprovider --basetemp=agate-workspace/.pytest-tmp agate/tests/`）| 1 | 2 failed / 1164 passed / 2 skipped | **FAIL（2 预存环境失败，0 本次引入）** |
| P5_consistency（`python3 agate/scripts/check-protocol-consistency.py --strict-errors-only`，worktree 自身脚本）| 0 | **0 ERROR**，318 WARNING（非阻断） | PASS（干净协议态）|
| P5_count_tests（`bash agate/tests/scripts/count-tests.sh`）| 0 | 1168 用例 ≥ 749 基线，无漂移 | PASS |

> P5_consistency 两态对照（与 r1 一致）：原样运行（`.pytest-tmp` 含全量会话残留）exit=1，ERROR(12) 全部指向 `agate-workspace/.pytest-tmp/test_*/` 下 pytest 生成的 fixture .md（扫描面误收测试临时目录，环境干扰非协议不一致）；清理 scratch 后重跑 = **0 ERROR / 318 WARNING / exit 0**。脏态日志 `consistency-dirty-2.log`、干净态日志 `consistency-clean-2.log`。

## failed 计数与分类（r2）

**failed = 2**（全部预存环境失败，0 本次改动引入）：

1. `test_check_routing.py::test_bdd_7_thin_score_anomaly_git_ok_false_exit_1` —— **预存失败（环境前提，非缺陷）**：
   "非 git 上下文→git_ok:false→exit 1" 前提在 basetemp 位于 worktree git 仓库内时失效（git_ok 实测 true → exit 0）。routing 代码未被本次改动触碰；TAG0019 先例 + P5-dispatch-context 客观查证已预告。隔离重跑仍失败（环境归属确认）。CI（basetemp 在仓库外）通过。已登记 known-failures.md 条目 1。
2. `test_env_adapt_docs.py::test_bdd_25_consistency_zero_error` —— **预存失败（环境干扰，非缺陷）**：
   全量会话中预存测试在 `.pytest-tmp` 生成含坏引用的 fixture .md，被一致性 CHECK 2 扫描面误收 → 12 ERROR → exit≠0。**清理 scratch 后隔离重跑 PASS**（环境归属实证）；一致性脚本扫描范围未被本次改动。CI（basetemp 在仓库外）通过。已登记 known-failures.md 条目 2。

> P4 修复闭环确认：r1 的本次引入真失败（bdd_5 编码违规）已修复转绿，r2 全量 failed 数由 3 降至 2，且 2 项均为预存环境失败（known-failures.md 已登记，与本任务无关）。

## 环境前提记录（本机约束）

- /tmp 只读 → basetemp 强制 `agate-workspace/.pytest-tmp`（worktree git 仓库内）→ 影响 bdd_7（非 git 上下文）与 bdd_25（一致性扫描面）两类用例，判定为环境前提，非产品缺陷（TAG0019 先例）。

## 签名行（gate 校验用）

PASSED 1164
FAILED 2
passed: 1164
failed: 2