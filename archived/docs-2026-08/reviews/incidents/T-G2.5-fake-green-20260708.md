---
incident_id: T-G2.5
date: 2026-07-08
severity: high
category: self-gate-false-positive
root_cause: structural — CI detective not preventive (no branch protection) + A4 reads-not-runs + self-authored review
fix_commit: 02b2216
---

# T-G2.5: self-gate 评审谎报 G2.5 绿灯

## 事故描述

commit `3053d14`（P2/P6 不可裁剪）的 self-gate 评审报告 `agate-alignment-review-20260708-02.md:174` 标注：

> check-gate.bats: G2.5 P2 无 P2-design.md → exit 1 ✓

**实际 G2.5 为红测试**：`check-gate.sh` P2 分支缺 `else`，P2-design.md 不存在时 exit 2（退让给主 Agent 自行判定）而非 exit 1（硬拦截）。G2.5 期望 exit 1，实际 exit 2 → 失败。

## 根因

三层缺口叠加（评审 `review-20260708-1420.md` 诊断）：

1. **CI 为事后检测非事前阻断**：protocol-tests.yml 已在 CI 跑 bats，但无分支保护 → 红 CI 不阻止红 commit 落地 main
2. **A4 判据只看测试存在性不要求实跑**：评审者看到 G2.5 存在、期望 exit 1，认为代码会 exit 1，标 ✓——但从未运行
3. **评审自著**（局限 3）：同一主 Agent 写代码又写评审，无独立重跑

## 影响

- 4 个红测试随 commit 合入 main
- P2 gate 在最该硬起来处（P2-design.md 缺失）反而退让给主 Agent 自行判定——与新政策"P2 不可裁剪"的语义矛盾
- self-gate 评审层的 ✓ 重新引入了客观 bats 门禁本要消除的主观性

## 修复

- `02b2216`：补 else 分支（症状修复）
- CI 分支保护（机制修复，根治缺口 1：让红 CI 阻断合入 main）
- `protocol-alignment-review.md` A4 升级（机制补强，根治缺口 2）

## 教训

agate 把"实跑验收、外部重执行"的纪律严格施加于用户代码，却唯独漏了施加于自己。self-gate 评审层的 ✓ 必须由实跑输出支撑，禁止裸 ✓。
