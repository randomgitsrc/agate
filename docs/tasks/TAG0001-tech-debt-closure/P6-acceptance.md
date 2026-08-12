---
phase: P6
task_id: TAG0001-tech-debt-closure
type: acceptance
parent: P5-verification.md
trace_id: TAG0001-P6-20260812
status: draft
created: 2026-08-12
agent: verifier
# ── v2.0 机器汇总 ──
pass: 20
fail: 0
ui_affected: false
---

# TAG0001 — P6 验收报告（tech-debt 登记闭环 + debt/ 归类修正）

> 角色：verifier（P6 验收模式）。执行环境：worktree `/home/kity/oclab/agate/.worktrees/agate-dev`（分支 dev/workspace，HEAD=5bdcd90，含 P5 serialize_evidence 修复）。
> 验收对象：worktree `agate/`（TAG0001 P4 实现 + P5 修复）。`~/.agate`（v0.40.2 稳定版）未触碰。
> 方法：20 条 BDD 逐条对照 P1-requirements.md（§3）在 worktree 实测/grep/fixture 模拟，每条产出证据文件（P6-evidence/{bdd-nn}.log，末行含 EXIT_CODE）。
> 环境标记：`[PROD_NOT_TOUCHED]`——本次仅只读验证 + /tmp/opencode 下临时 fixture 仓库，未修改任何 `agate/` 文件、未动 `~/.agate`。
> BDD 验收路径对照 P2-design.md §3（BDD 覆盖映射 20/20）。

**Summary**: 20/20 PASS，0 FAIL（BDD 全覆盖，无中间态）。

## 功能组 A：debt/ 归类修正（BDD-1..4）

- PASS BDD-1: WORKFLOW.md 目录规范 tech-debt 归独立 debt/ 目录——目录图含 `debt/`（L86），`agents/` 注释为「agent 输入知识（project.md / memory）」（L85），不再含 tech-debt（grep 无匹配）(bdd-01.log)
- PASS BDD-2: 工作区初始化 mkdir 建含 debt/ 的 9 个子目录——SETUP.md:114 / orchestrator-template.md:102 / state-machine.md:40 三处均为同一 9 集字面量 `{roadmap,tasks,agents,archived,reviews,decisions,plans,logs,debt}`，实测 mkdir 建出 9 个目录；全 worktree 无 8 集残留(bdd-02.log)
- PASS BDD-3: SETUP/UPGRADING 中 tech-debt 路径与独立 debt/ 目录一致——UPGRADING.md:97/99 指向 `{AGATE_WORKSPACE}/debt/tech-debt.md` 且说明「不再指向 agents/」，SETUP.md:114 含 debt，无 `agents/tech-debt` 过期路径(bdd-03.log)
- PASS BDD-4: 既有 TAG0003 工作区验收口径重验（8→9）——TAG0003 P1-requirements.md:88 与 P6-acceptance.md:26 均含「9 子目录」修订注；三处 mkdir 与目录图一致为 9；consistency 0 ERROR 无回归(consistency.log, bdd-04.log)

## 功能组 B：DEBT 条目 schema 校验（BDD-5..10）

- PASS BDD-5: 合法 DEBT 条目（open 无 task_id + closed 含 task_id 与 P5/P6 证据引用）通过 schema 校验，exit 0 无输出(bdd-05.log)
- PASS BDD-6: evidence 缺失的 DEBT 条目被拦截——`缺必填字段 evidence`，exit 1(bdd-06.log)
- PASS BDD-7: 非法枚举值被拦截——`category: bug` 与 `status: accepted`（第四态）均报非法值，exit 1(bdd-07.log)
- PASS BDD-8: closed 缺 task_id 或证据引用被拦截——closed 缺 task_id → `closed 条目必须含 task_id`；closed 有 task_id 但 evidence 无 P5/P6 → `evidence 须引用 task_id 与 P5/P6 证据`，均 exit 1(bdd-08.log)
- PASS BDD-9: 三态状态机落地——`status: open + task_id` 合法（视为 in_progress）exit 0；schema 枚举仅 open/in_progress/closed（第四态 accepted 被拦截，见 bdd-07）；模板三态表明示「task_id 非空即视为 in_progress」(bdd-09.log)
- PASS BDD-10: 无 tech-debt.md / 空文件 / 纯正文旧格式均 no-op——三态 exit 0 无输出（向后兼容不破坏存量项目）(bdd-10.log)

## 功能组 C：T001 回填验证模板（BDD-11）

- PASS BDD-11: T001 复盘 T1-T4（+A5 协议原因）回填为 DEBT 条目并通过 schema 校验——5 条 `source: retrospective` 条目 exit 0 无输出；复盘源 `docs/reviews/T001-retrospective-2026-08-10.md` 中 T1-T4/A5 行存在（grep -c=5），evidence 引用复盘出处，无损回填（止损条件 1 未触发）(bdd-11.log)

## 功能组 D：回退事件强制登记（BDD-12..15）

- PASS BDD-12: 协议文档明确「回退落地后必须建 DEBT 条目」——rules/state-transitions.md:84（TAG0001 强制节）、phase-cards/P6-acceptance.md:144、phase-cards/P4-implementation.md:27 均含强制语；agate-retreat-to.sh:73 打印 `GATE RETREAT: ... 建立 source: retreat 的 DEBT 条目` 提醒(bdd-12.log)
- PASS BDD-13: git 历史含 retreat 提交但无对应条目 → 报 `GATE DEBT WARNING`（exit 0 不阻断 commit/发布）——fixture 仓库建 retreat 提交后实测(bdd-13.log)
- PASS BDD-14: 已建 `source: retreat` 条目且 evidence 引用该提交 → 无缺失提示（NO WARNING）(bdd-14.log)
- PASS BDD-15: 回退覆盖检查用真实 retreat 记录消息格式（023b28b P5->P4 / 29301ad P6->P5 诊断文本）构造 fixture 可复现——方向 A（未建条目）报 2 条缺失 WARNING；方向 B（已建条目引用两提交）NO WARNING；P5 修复的 YAML int 边界回归单独验证通过（全数字哈希 7008516 不再被 serialize_evidence 丢弃）(bdd-15.log, bdd-15-int-regression.log)

## 功能组 E：P8 锚定留痕（BDD-16..18）

- PASS BDD-16: P8 发布阶段确认债务清单并留痕——P8-release.md:27 含「确认债务清单」步骤，:48 产出规格含 `debt_check: none / reviewed`（none 为合法选项）(bdd-16.log)
- PASS BDD-17: P8 债务确认只查留痕存在、不查内容、不阻断发布——check-gate.sh P8 分支实测：缺 debt_check → exit 1（`缺 debt_check 字段`）；`debt_check: none` → exit 2 脚本化检查通过；`debt_check: reviewed`（含未关闭债务场景）→ exit 2 不因内容拦截(bdd-17.log)
- PASS BDD-18: P8 空确认次数可观测——P8-release.md:48 明示 `debt_check: none` 为合法留痕值，可跨发布 grep 计数（止损条件 4 数据形态）(bdd-18.log)

## 功能组 F：债 vs 缺陷判据（BDD-19..20）

- PASS BDD-19: 判据文档化且含「不登记」合法出口——tech-debt-template.md:9-13 明示三分法问句「不修它，当前任务的验收声明会不会变成假的？」+ 三条款，第 3 条「都不影响 → 不登记（合法出口，防止登记簿变成垃圾场）」(bdd-19.log)
- PASS BDD-20: 登记 DEBT 不得豁免当前任务——tech-debt-template.md:15 硬规则「登记 DEBT 不豁免当前任务」；plan-eng-review.md:20 强制「提'后续应重构/存在架构债'须用标准 DEBT 条目格式（强制格式，不强制产出）」——P7 人工核对的判据锚点就位(bdd-20.log)

## 补充验证（非 BDD，佐证回归面）

- `bats agate/tests/unit/agate-debt-check.bats`：20/20 ok（BDD-1..20 与 @test 1:1 映射，含此前 flaky 的 test_bdd_15）
- `python3 agate/scripts/check-protocol-consistency.py`：exit 0，0 ERROR（CHECK 1-9 全 PASS，含新 check-debt.sh CHECK 9 锚点）
- P5 全量基线（unit.md）：bats 676 绿 + consistency 0 ERROR + shellcheck 0，无回归

## 环境标记

`[PROD_NOT_TOUCHED]`——验收过程仅只读 grep/读文件 + /tmp/opencode 临时 fixture 仓库（bdd-05..11 fixture、bdd-13..15 git 仓库），未修改任何 `agate/` 文件、未触碰 `~/.agate`。
