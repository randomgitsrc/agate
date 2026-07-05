> **P1/P2/P3/P4/P6 阶段强制要求本文件存在**——commit 前必须含当前阶段卡片且 sha256 与 CLI 一致。其他阶段可选。

---
phase: {P1-P8}
generated_by: agate-next-card.sh
task_id: {Txxx}
---

## 任务上下文
- task_id: {Txxx}
- P0-brief 路径: docs/tasks/{Txxx}/P0-brief.md

## 当前阶段卡片（强制注入）

以下内容由 `agate-next-card.sh P{N}` 输出原样粘贴（CLI 原文直嵌 marker 之间，**禁止添加 ``` fence**）。hook 会校验 sha256 一致——编辑或篡改 card 内容会导致 hash mismatch，commit 被拦截。

<!-- AGATE_CARD_START -->
{CLI 输出原文}
<!-- AGATE_CARD_END -->

## 其他派发上下文
（自由补充：环境状态、URL、选择器等。信息量 >10 行或需复用时落盘）

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
