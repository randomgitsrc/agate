---
review_date: 2026-07-05
reviewer: main (self)
review_target: docs/plans/agate-commit-strategy-2026-07-05.md (四轮修订后)
type: self-review
---

# commit 策略 self-review

## 总判定：PASS（3 处实施时要处理的 gap）

评审 F0-F4 全部正确落实，伪代码无残留 bug。但实施层面有 3 处伪代码未覆盖的 gap，每个都能在实施时解决——不是设计问题，是计划完整性不够。

## G1: `$TASK_REL` 变量域缺口

伪代码 line 42/49 用 `$TASK_REL`，但 `check-state-transition.sh` 不存在此变量。`TASK_REL` 在 `pre-commit-gate.sh` 的 for 循环内计算（line 89: `realpath --relative-to=...`），不在 check-state-transition.sh 的作用域。

**修法**：check-state-transition.sh 从 `$TASK_DIR`（由调用方 pre-commit-gate.sh 传入）自己算出 `TASK_REL`。或者把 `$TASK_REL` 作为第三个参数传入。

## G2: P5 目录级检查不可靠

`_phase_output_for P5` 返回 `P5-test-results`（目录），不是单一文件。`git ls-files "docs/tasks/T001/P5-test-results"` 对目录只返回目录路径，不返回目录下文件列表。目录存在 ≠ 内容已 commit。

**修法**：P5 改 `git ls-files "${TASK_REL}/P5-test-results/"`（带尾 `/`，匹配目录下文件）。但更简单——`[ -d "$TASK_DIR/P5-test-results" ]` 确认目录存在即可（gate 通过时 P5-test-results 应已有内容，目录为空时 P5 gate 自己会拦）。

## G3: 伪代码未覆盖 `$TASK_DIR` / `$TASK_REL` 的来源

伪代码假设 `$TASK_DIR` 已定义，但未说明从哪里来。check-state-transition.sh 的现有参数是 `STATE_FILE`（.state.yaml 的完整路径），TASK_DIR 应从中提取。

**修法**：伪代码开头补一行 `TASK_DIR=$(dirname "$STATE_FILE")`。

## 不阻塞的观察

- **P0-brief.md 路径**：确认在 `docs/tasks/Txxx/` 下（与 P1-P8 产出同目录），映射正确
- **P5 directory P1-dispatch-context**：dispatch-context 强制化只需 P1/P2/P3/P4/P6，不涉及 P5——不冲突
- **"拦截后处理策略" 节** 与 commit gate 逻辑正交——一个是用户指南，一个是 hook 逻辑——放在同一 plan 里没问题

## 建议

| # | 建议 | severity |
|---|------|----------|
| G1 | 补 `$TASK_REL` 计算（从 TASK_DIR 自主算） | 中（实施必经） |
| G2 | P5 目录检查改用存在性验证 | 低 |
| G3 | 补 `TASK_DIR=$(dirname "$STATE_FILE")` | 低 |
