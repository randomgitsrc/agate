# Issue #001: PeekView 多任务架构下 commit hook 完全失效

**日期**：2026-07-01
**严重度**：High（hook 等于没装）
**发现场景**：用户检查 PeekView commit hook 是否生效

## 问题描述

`agate/scripts/pre-commit-gate.sh` 第 29 行写死 `STATE_FILE="$REPO_ROOT/.state.yaml"`，只检测仓库根的 `.state.yaml`。

PeekView 仓库根无 `.state.yaml`，任务级 `.state.yaml` 放在 `docs/tasks/{Txxx}/.state.yaml`（如 `T001-mcp-namespace-map/.state.yaml`）。

## 影响

任何 `git commit`：
1. `git diff --cached --name-only | grep -qF ".state.yaml"` → 找不到（任务级 .state.yaml 不在根）
2. `has_staged_phase_change` → false
3. `has_staged_phase_output` → false（除非改了 P{n}-*.md，但 hook 不知道对应哪个任务）
4. `NEEDS_GATE=false` → exit 0 静默通过

**结果**：PeekView 装了 hook 但等于没装，所有 gate 都不跑。

## 实测

```bash
cd /home/kity/oclab/peekview
touch test.txt && cp test.txt . && git add test.txt
bash .git/hooks/pre-commit
# 输出: (空) EXIT=0
```

确认 hook 完全失效。

## 根本原因

`pre-commit-gate.sh` 是为"单任务架构"设计的（仓库根只有一个 `.state.yaml`）。PeekView 用的是"多任务架构"（每个任务独立状态），hook 没适配。

## 修复方向（待选）

| 方案 | 描述 | 改动量 |
|------|------|--------|
| A | hook 扫描 `docs/tasks/*/.state.yaml`，找 phase != DONE 的任务，逐个跑 gate | 中 |
| B | 根目录加全局 `.state.yaml` 记录活跃任务 ID，hook 读这个 + 任务级 | 小（改约定）|
| C | 改了哪个 `P{n}-*.md`，自动匹配所属任务，跑该任务 gate | 中 |

**推荐**：A — 不改约定，纯 hook 端适配。

## 相关

- agate 仓库本身：`agate/.git/hooks/` 没装 hook（设计正确，agate 本体用 self-gate）
- `pre-commit-gate.sh` L42-48：`NEEDS_GATE=false` 时 exit 0，没有"任务级 .state.yaml 存在但未检测"的告警

## 状态

**已修复**（commit 7515f66）——多任务 hook 适配 + phase-产出一致性 WARNING。