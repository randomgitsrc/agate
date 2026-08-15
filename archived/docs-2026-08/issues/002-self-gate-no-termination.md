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

### 实证：CON.9 反例

self-gate 评审（`docs/reviews/agate-self-gate-docs-cleanup-2026-07-02.md` §1）发现：
- CON.9 测试锁定"md5 缺口存在"→ md5 在 commit `949055c` 实现后测试永久失败
- 改 `check-p6-evidence.sh`（gate 脚本）完全落在 self-gate 触发条件里
- 如果当时走了 self-gate，A3b 反向传播应该推到 CON.9
- 实际没推到——证明"依赖主 Agent 自觉"确实会漏

## 解决方向

| 方案 | 实现 | 强制力 | 状态 |
|------|------|--------|------|
| A | `commit-msg` hook：检测 self-gate 改动时，要求 commit message 含 review 报告路径 | WARNING（不拦截） | ✅ 已实施 |
| B | CI 兜底：检查最近 self-gate 改动是否伴随 review 报告 | 中（事后警告） | 待实现 |
| C | CHECK 10：`check-protocol-consistency.py` 加"self-gate 改动必有 review"结构检查 | 中 | 待实现 |
| D | 终止条件：审查报告全 ALIGNED = 自然终止 | 弱（但自然） | ✅ 已实施（简化为自然终止，砍掉 `[NO_FURTHER_FIXES_NEEDED]` 标记） |

## 已实施的改动

- `agate/scripts/commit-msg-self-gate.sh`：commit-msg hook，暂存区含触发文件时 commit message 须含 `self-gate-review:` 路径或 `self-gate-skip:` 理由，否则 WARNING
- `agate/scripts/install-hook.sh`：同时安装 commit-msg hook
- `SELF-GATE.md`：补"强制力边界"声明 + "递归终止"条件（审查报告全 ALIGNED = 终止）
- 测试：CSG.1-CSG.6 + SG.7/SG.8

## 相关

- `SELF-GATE.md` §递归适用与终止条件
- `agate/scripts/commit-msg-self-gate.sh`
- CON.9 反例（self-gate 评审 §1）

## 状态

**已实施**（commit-msg hook WARNING + 自然终止）。CI 兜底（方案 B/C）待后续迭代。