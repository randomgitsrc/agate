---
phase: P6
task_id: TAG0002-refactor-first-class
type: acceptance
parent: P5-verification.md
trace_id: TAG0002-P6-20260812
status: draft
created: 2026-08-12
agent: verifier
# ── v2.0 机器汇总 ──
pass: 8
fail: 0
ui_affected: false
---

# TAG0002 — 重构一等任务（Phase A）：P6 验收报告（verifier）

> 验收对象：worktree `agate/` 的 refactor 机制改动（change_type frontmatter + P6 gate 分流 + CI backstop refactor 感知 + 文档同步）。
> 验收依据：P1-requirements.md 8 条 BDD（BDD-1..8）+ P2-design.md §5 BDD 覆盖对照 + P5-test-results/unit.md（全量 654 ok / 0 not ok）。
> 验收方法：BDD 逐条实跑（fixture 任务目录 + check-gate.sh/ci-gate-backstop.py/agate-md-field-get.py 实测 + 文档锚点 grep + 相关 bats 用例复跑），证据全部落 P6-evidence/。
> 本任务自身是**功能型任务**（做 refactor 机制），P6 走**功能 BDD 口径**——8 条 BDD 逐条二值对照；refactor 口径（行为不变 + 回归双证）是本次交付机制，作为 BDD-3/4/6/7 的验收对象，不是本任务自己的验收方式。
> 环境隔离：[PROD_NOT_TOUCHED] 只读验证 + fixture 实测，未修改任何 agate/ 文件，未触碰 `~/.agate`（稳定版 v0.40.2），未触任何生产环境。

## BDD 逐条验收结果

- PASS BDD-1: P1 frontmatter 声明 change_type: refactor 时 P1 gate 通过且不报错（fixture 实测 gate exit 2，输出不含 change_type 报错）(bdd-01.log, bats-check-gate-test-bdd.log)
- PASS BDD-2: 未声明 change_type 的任务验收行为与改造前一致——缺省走既有功能口径 P6 gate exit 2；正文提及/否定式提及 change_type 均不误入 refactor 分支（frontmatter-only，agate-md-field-get.py 实测正文输出空）(bdd-02.log, bdd-02b.log, bdd-02-md-field-get.log, bats-check-gate-test-bdd.log)
- PASS BDD-3: refactor 任务按回归口径验收——regression_pass: true + P6-evidence/regression.log + 关键路径 PASS，P6 gate exit 2，无功能 BDD 不被拦 (bdd-03.log, bats-check-gate-test-bdd.log)
- PASS BDD-4: 全量回归未全绿 → refactor 验收不通过——缺 regression.log 或缺 regression_pass: true 任一即 gate exit 1（关键路径 PASS 不能豁免回归双证）(bdd-04a.log, bdd-04b.log, bats-check-gate-test-bdd.log)
- PASS BDD-5: refactor 口径文档明确禁止伪造功能 BDD——P6 卡片含 refactor 回归口径分支（行为不变声明 + 全量回归全绿 + 关键路径 BDD 逐条 + "禁止为凑验收数量新增功能性质 BDD"）(bdd-05.log, bats-check-gate-test-bdd.log)
- PASS BDD-6: refactor 口径独立于 no_behavior_change——声明 no_behavior_change 不豁免回归双证（缺 regression.log 仍 gate exit 1）；双证齐备时 gate exit 2（口径仍为回归口径）(bdd-06a.log, bdd-06b.log, bats-check-gate-test-bdd.log)
- PASS BDD-7: 真实历史重构回填走 P1-P6 全程 gate 通过——fixture（建模 c182dc3 orchestrator-template 重构产物形状）P1/P3/P6 三处 gate 均 exit 2，全程无功能 BDD 要求；CI backstop P3 对 refactor 任务跳过 check-tdd-red（SKIP 而非 FAIL，mock exit 2 绿灯不误杀）(bdd-07.log, bdd-07-ci-backstop.log, bats-backstop-p3.log, bats-check-gate-test-bdd.log)
- PASS BDD-8: refactor 任务 P3 测试设计为回归测试口径——P3 卡片含回归测试口径分支（复用/保留既有用例、不新增功能行为断言、跳过 check-tdd-red 红灯步骤），可被 P6 逐条对照 (bdd-08.log, bats-check-gate-test-bdd.log)

## 覆盖完整性核对

- P1 共 8 条 BDD（BDD-1..8），本报告 8 条逐条对照，无挑验、无遗漏、无中间态。
- refactor 口径不豁免 BDD 编号机制（P1 §2.4）：P6 PASS+FAIL 总数 = 8 ≥ P1 BDD 数 8，check-p6-provenance.sh 审计 3 可正常通过。
- 证据引用路径全部相对 P6-evidence/，15 个证据文件均被 PASS 行引用（审计 1c 覆盖）。

## 关键行为描述（非技术口吻）

1. 重构任务在 P1 需求基线上声明 `change_type: refactor`，P1 验收照常通过，任务可正常推进（BDD-1）。
2. 不声明该字段的普通任务，从需求到验收的判定方式与改造前一模一样，不会被新机制误伤（BDD-2）。
3. 声明了 refactor 的任务，P6 验收改为"行为不变 + 全量回归全绿 + 关键路径验收"三件套：只要回归全绿证据（`regression_pass: true` + 回归日志）齐备、关键路径 PASS，就能通过，不需要编造功能测试来凑数（BDD-3/5）。
4. 如果回归结果有失败（缺证据），即使关键路径都过了，验收也过不了——回归是硬要求（BDD-4）。
5. 即使任务同时写了"无行为变更"声明，refactor 的回归双证要求也不会被豁免（BDD-6）。
6. 用 agate 一次真实的历史重构（orchestrator-template 整理）按 refactor 类型回填走完整流程，各阶段 gate 都能过，且 CI 不会误杀（重构比直接改不多一点麻烦）（BDD-7）。
7. refactor 任务在测试设计阶段就走"回归测试"口径（沿用既有用例、不新增行为断言），这个口径写进了 P3 指引，不是设计者临时发挥（BDD-8）。

**Summary**: 8/8 PASS, 0 FAIL（本次验收为功能 BDD 口径，记录验收时事实；gate 判定由主 Agent 亲跑 check-gate.sh P6 + check-p6-evidence.sh + check-p6-provenance.sh 确认）
