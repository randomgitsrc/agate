---
task_id: agate-commit-strategy
agent: main
date: 2026-07-05
status: 设计方案
---

# 逐阶段 commit 强制执行 + 拦截后处理策略

## 问题

agate 协议写明了"每阶段 commit"（`git-integration.md:31`），但**没有强制执行**。Agent 可以 P0→P1→P2→P3→P4 产出全写完再一次性 commit。

**后果**：
| 后果 | 严重度 | 说明 |
|------|--------|------|
| 中间 gate 绕过 | 高 | P1/P2/P3 gate 从未被 hook 验证——P2 缺评审、P3 红灯变绿全漏 |
| dispatch-context 跳过 | 高 | 中间阶段产出未经卡片 hash 校验 |
| 审计轨迹缺失 | 中 | `.gate-history.jsonl` 只有一条记录，看起来每步都过了 |
| 回退粒度粗 | 中 | 批量 commit 意味着回退时丢所有阶段——无法区分"P2 设计错"vs"P4 实现对" |

## 方案：状态转移级 commit gate

### 核心思路

**不改变 commit 时机**——协议已规定"每阶段完成即 commit"。**在状态转移层面强制这个规**——Agent 推进 phase 到下个阶段前，必须确认当前阶段产出已 commit。

### 实现

`check-state-transition.sh` 加逻辑：

```bash
# 3a. pre-phase-change commit gate：从 P{n-1} → P{n} 推进时，P{n-1} 产出必须已 commit
if [ "$NEW_PHASE" != "$OLD_PHASE" ] && [ "$OLD_PHASE" != "PAUSED" ]; then
    NEW_NUM=$(echo "$NEW_PHASE" | grep -oE '[0-9]+')
    OLD_NUM=$(echo "$OLD_PHASE" | grep -oE '[0-9]+')
    # 向前推进（非回退）
    if [ -n "$NEW_NUM" ] && [ -n "$OLD_NUM" ] && [ "$NEW_NUM" -gt "$OLD_NUM" ]; then
        OLD_OUTPUT=$( _phase_output_for "$OLD_PHASE" )
        # 检查旧阶段产出是否已 commit（不在暂存区 + 在 HEAD 中存在）
        if [ -n "$OLD_OUTPUT" ] && git diff --cached --name-only | grep -q "$OLD_OUTPUT"; then
            echo "GATE: 在推进到 ${NEW_PHASE} 前，${OLD_PHASE} 产出必须已 commit" >&2
            echo "      提示：先 git commit ${OLD_PHASE} 产出再改 phase" >&2
            exit 1
        fi
        # 产出既不在暂存区也不在 HEAD → 从未被 commit
        if [ -n "$OLD_OUTPUT" ] && ! git ls-files "$TASK_REL/$OLD_OUTPUT" >/dev/null 2>&1; then
            echo "GATE: ${OLD_PHASE} 产出 ${OLD_OUTPUT} 尚未 commit" >&2
            echo "      提示：先 commit ${OLD_PHASE} 产出再推进 phase" >&2
            exit 1
        fi
    fi
fi
```

**触发条件**：
- .state.yaml 中 phase 变更（从 Pn-1 → Pn 推进）
- 仅检查**向前推进**，不检查回退（回退有单独的 MAX_RETRY/PAUSED 逻辑）
- 跳过 PAUSED 恢复（PAUSED 恢复时旧产出应已 commit）

### 需检查的文件映射

```bash
_phase_output_for() {
    case "$1" in
        P0) echo "P0-brief.md" ;;
        P1) echo "P1-requirements.md" ;;
        P2) echo "P2-design.md" ;;
        P3) echo "P3-test-cases.md" ;;
        P4) return 0 ;;  # P4 产出是代码文件，不在单一 .md 产物，用暂存区代码检查
        P5) echo "P5-test-results" ;;  # 目录级检查
        P6) echo "P6-acceptance.md" ;;
        P7) echo "P7-consistency.md" ;;
        P8) echo "P8-release.md" ;;
    esac
}
```

## 拦截后的处理策略（补强）

当前 orchestrator-template 已有但散碎。集中到一节：

### 通用流程

```
commit 被拦 → 读错误消息 → 分析根因 → 修复产出 → 重验 gate → 再 commit
```

**绝对不能**：
- `--no-verify` 绕过（CI 会兜底抓到）
- 按错误消息直接凑条件（如缺 risk_level 就随手写 risk_level: low）
- 伪造证据（造 PASS 行/造截图/造 dispatch-context hash）

### 按拦截类型的处理

| 拦截类型 | 处理 |
|----------|------|
| gate 不通过（P2 缺评审 / P3 非红灯 / P6 FAIL） | 回到对应的 subagent 修复产出 |
| 格式缺字段 | 补字段。如果是 subagent 产出的结构性缺陷，回 subagent 重做 |
| dispatch-context 缺失 | `agate-next-card.sh P{N}` → 嵌入 dispatch-context 模板 |
| 未 commit 旧阶段 | 先 commit 旧阶段产出，再推进 phase |
| SCOPE+ 未 resolve | 先处理 P1 增补，标 SCOPE_RESOLVED |
| DESIGN_GAP 未配对 | 回 P7 配 REVIEWED 标记 |
| PROD_TOUCHED | 立即 STOP，人工处置 |

### 多次拦截

**同一阶段累计被拦 3 次** → PAUSED（不要无限重试，agent 明显走进了错误路径）。

## 不解决问题

- Agent 批量 commit 是在**不推进 phase 的情况下**做的（一直在 .state.yaml 写 P3，但实际做了 P4 的工作）→这是 Agent 主动违规，和"写规则但 agent 不读"是同一类问题，不在本方案范围
- 本方案是防御性机制——阻止推进 phase 直到前阶段产出被 commit。Agent 绕过方式是"不修改 .state.yaml 中的 phase 字段"

## 实施

### check-state-transition.sh

- 新增"commit gate"逻辑（加上面的 _phase_output_for 函数 + 主检查）
- 现有转移检查 + 新 commit gate 并存

### 测试

- `check-state-transition.bats` 新增：
  - P1→P2 推进，P1 产出未 commit → exit 1
  - P1→P2 推进，P1 产出已 commit → exit 0
  - P2→P3 推进，P2 产出在暂存区未 commit → exit 1
  - PAUSED→P3 恢复，P2 产出状态由恢复逻辑处理 → 不检查 commit gate
  - P3→P1 回退 → 不触发 commit gate（回退是重试，不是推进）

### orchestrator-template.md

- 加强"commit 被拦截后的处理"节
- 加"commit 时机强制规则"节

### git-integration.md

- 强化 "每阶段 commit" 规则，标记为强制执行

## 范围外

- 批量 commit 检测（暂存区含多个阶段产出）——误检风险大，且与 retry/修订场景冲突
- commit 历史 clean up（squash/fixup）——git 层面已有工具
