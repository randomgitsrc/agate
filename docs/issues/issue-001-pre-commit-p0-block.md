---
id: ISSUE-001
title: pre-commit-gate.sh 对 P0 阶段无条件运行 check-pruning.sh 导致拦截
status: open
type: bug
severity: medium
affected: pre-commit-gate.sh, check-pruning.sh
date: 2026-07-05
reporter: peekview T047
---

## 问题描述

P0 阶段（任务立项，仅 P0-brief.md）commit 时，pre-commit hook 拦截并 exit 1。
P0 是 agate 的标准阶段（WORKFLOW.md 阶段总览表第 1 行），但 hook 未处理该阶段的无 P1 文件状态。

## 根因

`pre-commit-gate.sh` 第 2j 节（位于 P1.1 gate 检查之后）：

```bash
bash "$AGATE_ROOT/scripts/check-pruning.sh" "$TASK_DIR" || exit 1
```

`check-pruning.sh` 第 11 行：

```bash
[ ! -f "$P1_FILE" ] && exit 2
```

当 `P1-requirements.md` 不存在时（P0 阶段正常状态），`check-pruning.sh` 正确返回 exit 2（"跳过"）。但 hook 用 `|| exit 1` 接收，将 exit 2 等同于 exit 1（硬拦截）。

## 触发条件

1. 新任务在 P0 阶段（仅 P0-brief.md）
2. `.state.yaml` 被暂存（phase=P0）
3. `P1-requirements.md` 不存在

## 预期行为

- 无 P1 文件 → 裁剪检查跳过（exit 2）→ hook 继续，不拦截
- commit 应正常完成

## 实际行为

- exit 2 → `|| exit 1` → commit 中断
- 用户只能通过**不暂存 .state.yaml** 绕过（如 T047 的处理方式）

## 定位过程

1. commit 无输出 → 查 `.gate-result.json` → `exit_code: 2, output: "未知阶段: P0"`
2. `bash -x pre-commit-gate.sh` 逐行追踪 → `check-pruning.sh` 处 exit 1
3. 单独跑 `check-pruning.sh P0 task_dir` → exit 2（文件不存在）
4. 确认 hook 用 `|| exit 1` 把 exit 2 当硬拦截处理

## 影响范围

- 所有需要创建新任务（P0）的用户
- 当前缓解：不暂存 .state.yaml，只 commit P0-brief.md + active-tasks.md（如 T047 做法）
- .state.yaml 推迟到 P1 commit 时再入暂存区

## 修复建议

### 方案 A（推荐，3 行改动）

`pre-commit-gate.sh` 第 2j 节改为区分 exit 2（跳过）和 exit 1（硬拦）：

```bash
# 2j. 裁剪条件检查（P2.7-P2.9）
if [ "$GATE_EXIT" != "1" ]; then
    PRUNE_EXIT=0
    bash "$AGATE_ROOT/scripts/check-pruning.sh" "$TASK_DIR" || PRUNE_EXIT=$?
    if [ "$PRUNE_EXIT" -eq 1 ]; then
        exit 1
    fi
    # exit 2 = 无 P1 文件 = 尚未到裁剪检查阶段，跳过
fi
```

与 2i 节 `check-p6-provenance.sh` 的处理方式一致（`|| PROV_EXIT=$?` + 仅 `-eq 1` 时 exit 1）。

### 方案 B

`check-pruning.sh` 在 exit 2 时改为 exit 0（无 P1 文件视为"没什么可检查的，通过"）。

但方案 B 丢失了语义区分（exit 2 原意是"跳过，不是通过"），建议方案 A。

### 相关模式

同样的 `|| exit 1` 模式在 2k 节 `check-scope-resolved.sh` 也存在：

```bash
bash "$AGATE_ROOT/scripts/check-scope-resolved.sh" "$TASK_DIR" || exit 1
```

但 `check-scope-resolved.sh` 的 exit 2 条件是"TASK_DIR 不存在"（更罕见），目前未触发。
仍建议统一改用 `|| PRUNE_EXIT=$?` 模式防御。

## 附注

- 这是 T047（content-link-fix）立项时遇到的，被拦截两次后才定位
- 当前 .state.yaml 的暂存问题不为空，但不暂存 .state.yaml 绕过是变相鼓励用户绕过其他 gate 检查——建议尽快修复
