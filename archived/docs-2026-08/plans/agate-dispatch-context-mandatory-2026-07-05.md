---
task_id: agate-dispatch-context-mandatory
agent: main
date: 2026-07-05
status: 实施计划
来源: Phase Card 防漂移机制 step 2-3 后续强化
---

# dispatch-context.md 强制化 — 从 nudge 变 barrier

## 问题

`pre-commit-gate.sh` 2p 节在 dispatch-context.md 存在时才做 hash 校验，不存在则静默跳过。Agent 绕过路径极简单：不生成 dispatch-context，直接 commit。

`self-gate-skip` 频繁使用已实证：WARNING 被 Agent 当不存在。唯一有效手段是 exit 1。

## 方案

**对 subagent 派发阶段强制要求 dispatch-context.md 存在。**

原理：`if [ -f "$DC_FILE" ] → hash 校验` 改为 `if [ -f ] → hash 校验; else → exit 1（限定派发阶段）`

## 改动

### pre-commit-gate.sh 2p 节（3 文件行改）

```bash
# 2p. dispatch-context.md 卡片 hash 校验（防漂移）
DC_FILE="$TASK_DIR/${PHASE}-dispatch-context.md"
if [ -x "$AGATE_ROOT/scripts/agate-next-card.sh" ]; then
    if [ -f "$DC_FILE" ]; then
        EXPECTED=$(bash "$AGATE_ROOT/scripts/agate-next-card.sh" "$PHASE" 2>/dev/null) || true
        if [ -n "$EXPECTED" ]; then
            EXPECTED_HASH=$(printf '%s' "$EXPECTED" | sha256sum | awk '{print $1}')
            EMBEDDED=$(sed -n '/<!-- AGATE_CARD_START -->/,/<!-- AGATE_CARD_END -->/p' "$DC_FILE" | sed '1d;$d')
            EMBEDDED_HASH=$(printf '%s' "$EMBEDDED" | sha256sum | awk '{print $1}')
            if [ "$EMBEDDED_HASH" != "$EXPECTED_HASH" ]; then
                echo "GATE: dispatch-context.md 卡片内容与 CLI 输出不一致（hash mismatch）" >&2
                exit 1
            fi
        fi
    else
        case "$PHASE" in
            P1|P2|P3|P4|P6)
                echo "GATE: subagent 派发阶段需提供 ${PHASE}-dispatch-context.md" >&2
                echo "      提示：调 agate-next-card.sh ${PHASE} 嵌入 dispatch-context 模板" >&2
                exit 1 ;;
        esac
    fi
fi
```

**逻辑**：
- CLI 可用 + 文件存在 → hash 校验（现有行为）
- CLI 可用 + 文件不存在 + phase 在派发列表 → exit 1（强制 barrier）
- CLI 可用 + 文件不存在 + phase 不在派发列表（P0/P5/P7/P8）→ 跳过（这些阶段不派 subagent，dispatch-context 不适用）
- CLI 不可用 → 整个 2p 跳过（向后兼容，不破坏 agate-next-card.sh 未装的环境）

### dispatch-context 模板（1 行改）

模板开头追加一行提示：

```diff
+ > 本文件在 P1/P2/P3/P4/P6 阶段为强制要求——commit 前必须存在且卡片 sha256 与 CLI 输出一致的 dispatch-context。
```

### 测试（2 个新测试）

`agate/tests/integration/dispatch-context-card.bats` 追加：

```bash
@test "DC.4 派发阶段 (P2) 缺 dispatch-context.md → exit 1" {
    local dir="$REPO/task"
    _setup_task_with_state "$dir" "P2"
    # 不生成 dispatch-context.md
    git add "$dir"
    run git commit -m "test: missing dispatch-context"
    [ "$status" -ne 0 ]
    [[ "$output" == *"需提供 P2-dispatch-context.md"* ]]
}

@test "DC.5 非派发阶段 (P5) 缺 dispatch-context.md → 不拦截" {
    local dir="$REPO/task"
    _setup_task_with_state "$dir" "P5"
    # 不生成 dispatch-context.md，但 P5 不派 subagent
    git add "$dir"
    run git commit -m "test: no dispatch-context in P5"
    [[ "$output" != *"需提供"* ]]
}
```

### 不涉及

- gate 脚本
- 角色文件
- Phase Card 内容
- orchestrator-template 或 mapping 表
- CHANGELOG（更新单独 commit）

## 验证

- `bats` 全量 + 2 新测试（DC.4, DC.5）
- `check-protocol-consistency.py` 0 ERROR
- `shellcheck pre-commit-gate.sh` 0 error
- 实跑：P2 阶段无 dispatch-context → commit 被拦
- 实跑：P5 阶段无 dispatch-context → commit 成功（不派 subagent）

## 优先级

高（patch）。把 Phase Card 防漂移的最后一个 nudge→barrier 缺口填上。
