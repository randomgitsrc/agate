---
phase: P6
task_id: TAG0027
type: acceptance
parent: P5-verification.md
trace_id: TAG0027-P6-20260903
status: draft
created: 2026-09-03
agent: verifier
# ── v2.0 机器汇总 ──
pass: 26
fail: 0
ui_affected: false
---

# P6 验收报告 — 编排语义统一落地（RM-AG0054）

> 验收对象：worktree `agate/` 协议本体（HEAD bc93c67 = P5 commit，P4 实现 commit fcf3fd2 已含全部改动）。P5→P6 之间无非产出文件改动（审计 7 reuse_allowed）。功能型任务（非 refactor），ui_affected=false，26 条 BDD（BDD-1~26，含 exit2fix 回改语义与 BDD-26 新增）全量对照，无挑验。验收方法：tag0027 批 48 个 pytest 用例分阶段实跑（全部 PASSED exit 0）+ worktree 数据真值实读 + 结构/协议一致性脚本实跑。证据文件均在 P6-evidence/ 下，见各 PASS 行括号引用。[PROD_NOT_TOUCHED]

## Phase 1：转移表结构化（BDD-1~5）+ gate_pass_exit 机器字段（BDD-26）

- PASS BDD-1: phases.yaml 主线 P0-P8 全部含 next/retreat 键、schema 声明校验通过（S-5 check-yaml-schema exit 0 + 数据真值 + pytest 2 用例 PASSED）(schema-phases-validation.log, data-truth-phases.yaml.txt, phase1-transfer-s1s2.log)
- PASS BDD-2: P6.5 条目以 gate_subphase 建模（hosted_on=P6/forward_to=P7/needs_revision_to=P6）且无 next/retreat 键、非独立转移边（数据真值 + pytest 用例 PASSED）(data-truth-phases.yaml.txt, phase1-transfer-s1s2.log)
- PASS BDD-3: retreat 目标与 state-machine 一致——P5/P6 retreat=P4、P5 next=P6、P6 next=P7、P6.5 needs_revision_to=P6（数据真值 + pytest 用例 PASSED）(data-truth-phases.yaml.txt, phase1-transfer-s1s2.log)
- PASS BDD-4: next/retreat 纳入 S-1/S-2——不一致场景（YAML vs WORKFLOW 表 retreat/next mismatch）S-1 exit 1、一致场景 exit 0；实跑 worktree check-structure-consistency S-1/S-2 OK（pytest 3 用例 PASSED + 脚本 exit 0）(phase1-transfer-s1s2.log, s1s2-structure-consistency.log)
- PASS BDD-5: 新增字段未破坏既有消费方——worktree check-protocol-consistency --strict-errors-only exit 0（0 ERROR）+ 全量回归全绿（复用 P5 证据：1381 passed, 2 skipped, failed=0，审计 7 reuse_allowed）+ 回归守卫用例 PASSED (protocol-consistency-guardrail.log, ../P5-test-results/unit.md, phase1-transfer-s1s2.log, tag0027-batch-48-summary.log)
- PASS BDD-26: phases.yaml 全部条目声明 gate_pass_exit（P0-P3/P5/P6/P8=2、P4/P7/P6.5=0）且与 check-gate.py 各 gate_p* 真实 return 码一致（实读 L583/704/889/898/996/1054/1099/1126/1247/1382），pytest 2 用例断言 PASSED，agate next 按 pass_set 判定 (bdd26-gate-pass-exit-mapping.log, phase1-transfer-s1s2.log, tag0027-batch-48-summary.log)

## Phase 2：推进侧 CLI（BDD-6~13）

- PASS BDD-6: agate next 在 gate exit ∈ gate_pass_exit（含 P5 正常通过码 exit 2）时按 next 字段推进到 P6 且经 check-state-transition 跳变校验（pytest 2 用例 PASSED：exit2 pass 推进 + P6 judge 未启用直推 P7 锚点）(phase2-cli-judge.log)
- PASS BDD-7: agate next 在 gate exit 1 时按 retreat 目标委托 agate-retreat-to 回退（P5→P4、P6→P4 逐阶 diff=1 独立 commit）且 retries 记录（pytest 2 用例 PASSED）(phase2-cli-judge.log)
- PASS BDD-8: 真暂停（exit ∉ gate_pass_exit 且 ≠ 1）不推进、落盘 {phase}-exit2-resolution.md 且 frontmatter 机器可读（phase/task_id/type=exit2-resolution/parent，pytest 2 用例 PASSED）(phase2-cli-judge.log)
- PASS BDD-9: P6 exit 2（FAIL=0/证据非空 + provenance exit 0）保持前进特例——judge 未启用直推 P7 不落盘 resolution；judge 启用 gate_p65 exit 0 推 P7、exit 1 停留 P6 均不落盘（pytest 3 用例 PASSED，A1 闭环正/反向）(phase2-cli-judge.log)
- PASS BDD-10: agate advance 与回退侧 CLI 对接——diff≥2 人工直跳提示须先 PAUSED（不自行回退）、diff=1 委托 agate-retreat-to 单步（pytest 2 用例 PASSED）(phase2-cli-judge.log)
- PASS BDD-11: 档位 C 可观测证据——两次推进后 gate-events.jsonl 含 state_transition 事件；健康任务（gate_run exit:2 ∈ pass_set）全程推进不落 resolution（pytest 2 用例 PASSED）(phase2-cli-judge.log)
- PASS BDD-12: exit2-resolution 纳入 judge 复核——健康账本（无 resolution 文件）复核通过不误拦、已存在 resolution 格式非法复核失败、格式完整复核通过（pytest 3 用例 PASSED，Fix C 谓词）(phase2-cli-judge.log)
- PASS BDD-13: 既有脚本返回约定未改造——check-gate.py 三态 exit 0/1/2 与 check-state-transition.py 二态 exit 0/1 回归守卫 PASSED（pytest 2 用例；真实 return 实读见映射 log）(phase2-cli-judge.log, bdd26-gate-pass-exit-mapping.log)

## Phase 3：编排心智统一文档化（BDD-14~17）

- PASS BDD-14: dispatch-protocol 五模式为唯一语义锚点——协议层无 "workflow 模式/ralph 模式/goal 模式" 平台命名概念（pytest 用例 PASSED）(phase34-docs-render-audit-guardrail.log)
- PASS BDD-15: 数据面 rules/*.yaml + schema 平台词表扫描命中数 = 0（CHECK 15 全量实跑 0 ERROR + 插入裸词报 ERROR 用例 PASSED）(protocol-consistency-guardrail.log, phase34-docs-render-audit-guardrail.log)
- PASS BDD-16: markdown 叙述文档平台名仅限带「实现注记」标记段落——CHECK 14 全量面 0 ERROR（豁免结构：platform-notes.md/SETUP.md 整文件 + WORKFLOW 已知适用环境表）+ 实现注记统一格式用例 PASSED (protocol-consistency-guardrail.log, phase34-docs-render-audit-guardrail.log)
- PASS BDD-17: 平台名污染排查完成判定可追溯——结构豁免对象（assets/templates/dsh/ 平台食谱目录实存）用例 PASSED，存量清理由 B3a 批次落地（P4-implementation.md 记录）(phase34-docs-render-audit-guardrail.log)

## Phase 4：渲染层 + 注入自动化 + 护栏 1（BDD-18~25）

- PASS BDD-18: agate dispatch 单命令渲染时注入完整卡片块——产物 START..END 内嵌 hash == agate-next-card stdout hash 且 CARD-SOURCE 来源标记在块外（pytest 2 用例 PASSED）(phase34-docs-render-audit-guardrail.log)
- PASS BDD-19: 手工写上下文 + agate-inject-card.py 注入兜底保留——注入 exit 0、卡片写入占位符块、2p hash 校验通过（pytest 2 用例 PASSED；本任务 P6-dispatch-context-verifier.md 即物理块注入产物）(phase34-docs-render-audit-guardrail.log)
- PASS BDD-20: 审计 2 排除逻辑在渲染产物上生效——CARD-SOURCE 双锚点剥离起点使 START 前预判行被剥净 exit 0（pytest 2 用例 PASSED）(phase34-docs-render-audit-guardrail.log)
- PASS BDD-21: 手工场景审计 2 文件版兜底有效——物理 AGATE_CARD_START/END 块剥离不误报（pytest 用例 PASSED；本任务 dispatch-context 预检 0 预判行）(phase34-docs-render-audit-guardrail.log)
- PASS BDD-22: 护栏 1 机械化（CHECK 14）可判定——协议 md 无注记段插平台名报 ERROR、补注记后通过（pytest 2 用例 PASSED + 全量面 0 ERROR）(phase34-docs-render-audit-guardrail.log, protocol-consistency-guardrail.log)
- PASS BDD-23: agate-render-dispatch-prompt.py 既有 CLI 契约不破坏（pytest 回归守卫用例 PASSED）(phase34-docs-render-audit-guardrail.log)
- PASS BDD-24: 新增协议 md 含平台名无注记自动被 CHECK 14 命中（结构性判据无名单，pytest 用例 PASSED）(phase34-docs-render-audit-guardrail.log)
- PASS BDD-25: 手工/自动两路派发 dispatch-context 均满足 pre-commit 强制与 provenance 冻结——两路产物 START..END 内嵌 hash 相等且 == next-card stdout（pytest 2 用例 PASSED）(phase34-docs-render-audit-guardrail.log)

## 汇总

**Summary**: 26/26 PASS, 0 FAIL

## 验收备注

- 全部 26 条 BDD 实跑验证：tag0027 批 48 个 pytest 用例分 3 组实跑（phase1 10、phase2 18、phase34 20）全 PASSED exit 0，合并汇总 48 passed exit 0（tag0027-batch-48-summary.log）。
- 数据真值证据 data-truth-phases.yaml.txt 实读 phases.yaml（next/retreat/gate_pass_exit/gate_subphase 键与值、P6.5 无独立边、P5/P6 retreat=P4），与 BDD-1/2/3/26 语义逐条对应。
- 支撑脚本实跑：S-1/S-2 结构一致性 exit 0、YAML Schema 校验（S-5）exit 0、worktree 协议一致性 --strict-errors-only exit 0（0 ERROR，324 个历史叙事 WARNING 非本任务引入）。
- BDD-26 独立实证：check-gate.py 各 gate_p* 正常通过 return 码实读与 phases.yaml gate_pass_exit 声明逐 phase 一致。
- 预期全 PASS 达成：P4 实现已全量绿（P5 fcf3fd2 基线），本 P6 独立实跑确认无回归、无 FAIL。
- 自查说明：本文件为 verifier 自查产出，P6 gate（check-gate.py P6 + check-p6-evidence.py + check-p6-provenance.py）由主 Agent 实跑判定，本文件不声称"验收已通过"。
