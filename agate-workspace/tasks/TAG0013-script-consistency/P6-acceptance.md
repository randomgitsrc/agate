---
phase: P6
task_id: TAG0013-script-consistency
type: acceptance
parent: P5-test-results/unit.md
trace_id: TAG0013-P6-20260816
status: draft
created: 2026-08-16
agent: verifier
# ── v2.0 机器汇总 ──
pass: 11
fail: 0
ui_affected: false
---

# P6 验收报告 — agate 脚本一致性批（RM-AG0015 / RM-AG0017 / RM-AG0018 剩余）

> 验收依据：P1-requirements.md 的 11 条 BDD（BDD-1..11，含 SCOPE+ 从 P4）。逐条实跑验收，只读，未修改任何代码/测试/文档。

## BDD 逐条验收结果

- PASS BDD-1: 协议文档面脚本引用无漂移时 CHECK 10 通过——worktree 实跑 0 ERROR，CHECK 10 无漂移（仅 1 条 CHANGELOG 叙事聚合 WARNING，属 BDD-5 设计内）(P6-evidence/bdd-1.log)
- PASS BDD-2: 协议文件引用不存在的脚本名 → CHECK 10 ERROR——假协议树 phase-cards 含 `check-nonexistent-script.py`，实跑报 ERROR「引用了不存在的脚本: check-nonexistent-script.py」loc=`agate/phase-cards/P3-tdd.md:1`，exit 1 (P6-evidence/bdd-2.log)
- PASS BDD-3: 豁免清单 5 类引用不报漂移——假协议树构造 ①UPGRADING 整文件 ②formatters ③3 hook 薄壳 ④count-tests.sh ⑤scripts/README 退役名，实跑 CHECK 10 0 ERROR/0 WARNING/通过 (P6-evidence/bdd-3.log)
- PASS BDD-4: phase-cards/rules 纳入 PROTOCOL 严格检查——PROTOCOL_DIRS=('agate/assets/', 'agate/phase-cards/', 'agate/rules/')，CHECK 2/3 对 phase-cards/rules 0 ERROR（回归验证成立）(P6-evidence/bdd-4.log)
- PASS BDD-5: 叙事文件脚本名引用不升 ERROR、docs/ 非扫描面无输出——假协议树含 docs/superpowers + archived 旧名 + CHANGELOG，实跑仅 CHANGELOG 聚合 1 WARNING，docs/archived 无输出 (P6-evidence/bdd-5.log)
- PASS BDD-6: 暂存 README.md 变更触发 self-gate WARNING——临时 git 仓库 git add README.md，commit-msg-self-gate.sh 实跑 stderr 含「GATE SELF-GATE:」+「README.md / AGENTS.md」文案，exit 0 不阻断 (P6-evidence/bdd-6.log)
- PASS BDD-7: 暂存 AGENTS.md 变更触发 self-gate WARNING——git add AGENTS.md，实跑 stderr 含「GATE SELF-GATE:」，exit 0 不阻断 (P6-evidence/bdd-7.log)
- PASS BDD-8: 暂存 CHANGELOG.md 变更不触发 self-gate——git add CHANGELOG.md，实跑 stdout/stderr 均为 0 字节（CHANGELOG 豁免），exit 0 (P6-evidence/bdd-8.log)
- PASS BDD-9: 既有 self-gate 触发面不回归——test_commit_msg_self_gate.py + test_commit_msg_self_gate_integration.py 实跑 14 passed（含既有 4 用例），exit 0 (P6-evidence/bdd-9.log)
- PASS BDD-10: 有异常模式时输出 DEBT/roadmap 登记提醒——.state.yaml P2 重试 3 次超限，check-retrospective.py 实跑 stderr 含「复盘发现的新缺口请登记 DEBT/roadmap」，DEBT/roadmap 各命中 1 次，exit 0 (P6-evidence/bdd-10.log)
- PASS BDD-11: 无异常模式时输出为空——无异常任务目录实跑 stdout/stderr 均 0 字节（RT.1 不回归），exit 0 (P6-evidence/bdd-11.log)

**Summary**: PASS: 11 / FAIL: 0（BDD-1..11 全覆盖，无挑验）

## 客观查证对照（dispatch-context 执行基准）

- 全量 pytest 768 passed / 2 skipped / 0 failed（P5 记录，本阶段仅复跑相关子集确认 BDD-9）
- consistency 0 ERROR（279 WARNING 基线，含 CHECK 10 对 CHANGELOG 的聚合 WARNING 1 条）
- count-tests.sh = 770（≥ P2 §5 基线 751，无计数漂移）

## 环境隔离

[PROD_NOT_TOUCHED] 只读验收；假协议树全部在 /tmp 临时目录；临时 git 仓库 /tmp/p6-bdd678 独立于 worktree；未修改任何代码/测试/文档；未 commit。

## 备注

- SCOPE+（P1 §8，从 P4）：integration 测试 test_csg_1_readme_triggers_warning 已随实现更新断言为「README.md 变更触发 self-gate WARNING」，本阶段实跑 14 passed 覆盖。
- 自查≠gate：本文件为 verifier 产出，最终 gate 判定由主 Agent 执行（check-gate.py P6 + check-p6-evidence.py + check-p6-provenance.py）。
