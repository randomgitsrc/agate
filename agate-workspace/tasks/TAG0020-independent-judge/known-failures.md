---
task_id: TAG0020
generated_by: verifier (P5)
---
# 已知失败登记

> **语义边界**：本文件只登记**预存失败**（P5 之前就存在的、与当前任务无关的失败）。
> 当前任务引入的失败用 P5-test-results/ 记录，不写本文件。

## 预存失败（非本任务引入）

| # | 测试文件 | 失败数 | 根因 | 与本任务相关 | 处理计划 |
|---|---------|--------|------|-------------|---------|
| 1 | agate/tests/unit/test_check_routing.py::test_bdd_7_thin_score_anomaly_git_ok_false_exit_1 | 1 | "非 git 上下文→git_ok:false→exit 1" 前提失效：P5 basetemp=`agate-workspace/.pytest-tmp` 位于 worktree git 仓库内（/tmp 只读约束），被测目录实际在 git 仓库中，git_ok 实测 true → routing exit 0 ≠ 期望 1。routing 代码未被 TAG0020 触碰（TAG0019 产物），TAG0019 已有同类先例。CI（basetemp 在仓库外）通过。 | 否 | 推迟（环境约束，非代码缺陷；CI 全绿兜底） |
| 2 | agate/tests/unit/test_env_adapt_docs.py::test_bdd_25_consistency_zero_error | 1 | 环境干扰：全量 pytest 会话中预存测试（test_agate_debt_check.py / test_check_retrospective.py）在 `agate-workspace/.pytest-tmp/test_*/` 生成含坏引用的 fixture .md（tech-debt.md / closed-no-task.md / fourth-state.md 等，引用不存在的 docs 路径）；check-protocol-consistency.py `iter_md_files` 未排除 `agate-workspace/.pytest-tmp` → CHECK 2 扫描面误收 → 12 ERROR → exit≠0。一致性脚本扫描范围未被 TAG0020 改动（diff 仅 +2 条 CHECK 9 锚点）。隔离运行 / 清理 scratch 后 / CI（basetemp 在仓库外）均 PASS。 | 否 | 推迟（环境约束，非代码缺陷；已确认干净协议态 0 ERROR） |

## 重跑确认（r2，P4 修复后 2026-08-22）

- P4 修复 test_agate_common.py BDD-5 编码违规后全量重跑：failed 由 3 → 2（bdd_5 转绿），两条预存环境失败均复现且归属不变：
  - 条目 1（bdd_7）：隔离重跑仍 FAIL（git 仓库内 basetemp，"非 git 上下文"前提失效）——环境前提确认。
  - 条目 2（bdd_25）：清理 scratch 后隔离重跑 **PASS**——环境干扰归属实证；全量会话中仍失败（会话内 .pytest-tmp 复被预存测试填充）。
- 结论：本任务引入的失败已清零；剩余 2 条均为预存环境失败，与本任务无关。

## 重跑确认（r3，P8 发布前 2026-08-22，tag v0.59.0）

- P8 发布前完整重跑（audit7 reuse_blocked）：全量 pytest **2 failed / 1164 passed / 2 skipped**，两条预存环境失败复现且归属不变（隔离复证：bdd_7 仍 FAIL / bdd_25 干净态 PASS）。
- consistency 干净态 **0 ERROR / 318 WARNING**（CHECK 7 badge v0.59.0 vs tag v0.59.0 通过）；count 1168 ≥ 749 无漂移。
- 结论：发布门槛状态不变——本次引入失败 = 0，剩余 2 条预存环境失败（非缺陷，CI 兜底），known-failures 登记完整、三轮（r1/r2/r3）归属一致。