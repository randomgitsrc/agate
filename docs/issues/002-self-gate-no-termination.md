# Issue #002: self-gate 递归触发缺乏终止机制

**日期**：2026-07-01
**严重度**：Medium（设计缺陷，不影响当前功能）
**发现场景**：用户担心"改 self-gate → self-gate 触发 → 改 self-gate → 循环"

## 问题描述

SELF-GATE.md 规定"`agate/scripts/*.sh` / `SELF-GATE.md` / 角色文件 / `agate/*.md` / `agate/**/*.md` 有改动时，主 Agent 主动派发 protocol-alignment-review subagent"。

这是**主动触发**，不是 commit hook 自动触发。当前没有：
1. commit hook 检测 self-gate 改动
2. CI 兜底检查 review 报告
3. 递归终止条件（"无需再修"标记）

## 影响

- 主 Agent 自觉 → self-gate 工作
- 主 Agent 偷懒 → self-gate 形同虚设
- 理论上可以无限循环（改 self-gate → 审查 → 修复 → 又改 → 又审查）

## 实测

agate 仓库 commit `133c7b4`（改 SELF-GATE.md 加反向传播）和 commit `7766fd0`（反向传播命中 4 处遗漏）：
- `pre-commit-gate.sh` 静默通过（hook 不检测 `.state.yaml` 改动）
- self-gate 是主 Agent（我）手动派发 subagent 跑的，**不是自动**

如果主 Agent 偷懒跳过 self-gate，这两个 commit 不会被审查。

## 解决方向（待选）

| 方案 | 实现 | 强制力 |
|------|------|--------|
| A | `commit-msg` hook：检测 self-gate 改动时，要求 commit message 含 review 报告路径 | 强（commit 被拦） |
| B | CI 兜底：检查最近 self-gate 改动是否伴随 review 报告 | 中（事后警告） |
| C | CHECK 10：`check-protocol-consistency.py` 加"self-gate 改动必有 review"结构检查 | 中 |
| D | 终止条件：review 报告标 `[NO_FURTHER_FIXES_NEEDED]` 才能不附修复对应 | 弱 |

**推荐**：A + D 组合——commit-msg hook 强制附路径，review 报告标 `[NO_FURTHER_FIXES_NEEDED]` 自然终止。

## 相关

- `SELF-GATE.md` §9 递归适用：本机制自身的实施也走 self-gate
- 现状：依赖主 Agent 自觉，无强制机制

## 状态

**待设计**——可以纳入下次 self-gate 机制改进。