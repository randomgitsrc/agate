---
task_id: T001
type: paused-resolution
parent: P6-gate-diagnosis.md
created: 2026-08-10
agent: main
---

# PAUSED 解决记录 — P6→P4 回退批准

## 触发

P6→P4 回退（diff=2），按 `state-machine.md`「阶段回退规则」需人工批准方可执行。诊断内容见 `P6-gate-diagnosis.md`（BDD-17 FAIL：`check-p6-format.sh --fix` 破坏 `P6-acceptance.md` frontmatter 的 `pass:`/`fail:` 字段，v0.35 潜伏缺陷，被本任务新引入的 frontmatter 字段首次触发，无下游校验拦截）。

## 人工批准

用户在对话中要求先讲清问题原理（`--fix` 的设计意图 / 破坏机制 / 为何未被拦截），主 Agent 已完整说明后，用户明确批复：

> "批准退回P4修复"

[HUMAN_CONFIRMED: 2026-08-10 用户批准 P6→P4 回退，理由：BDD-17 FAIL 是真实、可复现、影响所有未来任务的 v0.35 潜伏缺陷，需要在 P4 定向修复 check-p6-format.sh 的 --fix 逻辑（剥离 frontmatter 块后再对正文做归一化），不接受在 P6 阶段自行改代码绕过]

## 执行计划

1. `bash ~/.agate/scripts/agate-retreat-to.sh docs/tasks/T001-v2.0-structured P4 "BDD-17: check-p6-format.sh --fix 破坏 frontmatter pass/fail 字段，需修复"`
   两步自动化回退（P6→P5→P4，每步独立归档旧产出 + 独立 commit + retry 计数 +1）
2. 在 P4 派发定向修复：`check-p6-format.sh` 的 `--fix` 分支需要先剥离 frontmatter 块（`---...---`），只对正文部分做 5 条归一化 sed，frontmatter 部分原样保留后再拼回；新增回归测试覆盖"P6-acceptance.md 含 frontmatter pass/fail 字段时 --fix 不破坏 frontmatter"这个此前从未被覆盖的场景
3. 独立验证修复后重跑 P5（技术验证）→ P6（重新派发 verifier，产出全新 P6-acceptance.md + P6-evidence/，不沿用旧结论）
