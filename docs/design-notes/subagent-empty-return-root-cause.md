# Subagent 空返回根因分析与缓解

> 日期：2026-06-25
> 状态：已分析，部分可落地

## 问题

主 Agent 派发 general subagent 执行复杂任务（如 10 文件交叉评审），subagent 返回空 `<task_result></task_result>`。中间过程不可见（LIMITATIONS.md 局限 4），无法判断是"卡死"还是"上下文爆了"还是"被平台杀掉"。

## 根因（基于 OpenCode 1.16.2 文档 + `opencode debug agent` 实证）

```bash
$ opencode debug agent general
steps: NOT SET
maxSteps: NOT SET
model: NOT SET - inherits parent
question: false (deny)
```

三个因素叠加：

1. **`steps` 未设置**——按文档："If this is not set, the agent will continue to iterate until the model chooses to stop or the user interrupts"。但实际不是无限跑——上下文窗口满时，模型被强制返回，此时可能产出空内容（不是主动选择停止，是被截断）。
2. **`question` 被 deny**——subagent 卡住时不能问主 Agent"我该怎么办"，也不能向用户求助，只能空返回。
3. **无 timeout**——Task 工具没有平台层超时参数（已验证，dispatch-protocol.md:313 描述正确）。

**最可能的因果链**：
subagent 收到复杂任务 → 开始读 10 个文件（每个 200-700 行）→ 上下文逐渐被文件内容占满 → 没有空间生成回复 → 模型被迫返回 → 返回内容为空（上下文窗口被输入占满，没有空间留给输出）

## 可落地的缓解（OpenCode 配置层）

### 缓解 1：给 general subagent 配 `steps` 上限

在 `~/.config/opencode/opencode.json` 或项目级 `.opencode/opencode.json` 里：

```json
{
  "agent": {
    "general": {
      "steps": 50
    }
  }
}
```

效果：subagent 最多迭代 50 步。到上限后，按文档说"receives a special system prompt instructing it to respond with a summarization of its work"——**被强制产出摘要而非空返回**。

这是最直接的缓解——空返回变为"部分完成 + 摘要"，主 Agent 至少知道 subagent 做了什么。

### 缓解 2：`question` 改为 `allow`

```json
{
  "agent": {
    "general": {
      "permission": {
        "question": "allow"
      }
    }
  }
}
```

效果：subagent 卡住时可以问主 Agent。但注意——subagent 的 question 不是直接问用户，是传回给主 Agent 处理。主 Agent 需要能响应（目前主 Agent 阻塞等待 subagent 返回，question 的交互机制需验证）。

**风险**：如果 question 机制不支持 subagent→主 Agent 的双向通信，改为 allow 也不会有效。需实测验证。

### 缓解 3：prompt 里要求"分阶段落盘"

在派发 prompt 里加：
```
每读完一个文件，把关键发现写入 /tmp/opencode/{task_id}-progress.md（追加模式）。
即使最终无法产出完整报告，progress 文件也能让主 Agent 知道你做了什么。
```

这是 agate 协议层已有的"间接缓解"之一（LIMITATIONS.md 局限 4），但当前没有在 dispatch-prompt 模板里强制要求。可以在模板里加一条。

## 不可落地的（需 OpenCode 平台支持）

| 能力 | 当前状态 | 需要的 |
|------|---------|-------|
| subagent 活动信号 | 不可观测 | Task 工具暴露 subagent 的工具调用日志/输出流 |
| 基于活动的智能超时 | 不存在 | 有活动续期，无活动终止 |
| subagent 上下文使用量 | 不可观测 | 暴露 subagent 当前 context 使用率 |

这些是 LIMITATIONS.md 局限 4 的"根本解决"，超出 agate 协议范围。

## 结论

空返回的**最可能根因**是上下文窗口被输入文件占满、模型被迫返回空内容。`steps` 上限 + 强制摘要产出是最直接的缓解——不解决"上下文不够"的根本问题，但把"空返回"变为"部分完成 + 摘要"，让主 Agent 有信息可用。

`question: allow` 需实测验证交互机制是否支持 subagent→主 Agent 通信。如果不支持，这条路走不通。

**对 agate 的影响**：
- dispatch-protocol.md 的「空返回恢复策略」可以补充："最可能原因是上下文窗口被输入占满，调整策略优先拆分任务减少单次输入量"
- dispatch-prompt 模板可以加"分阶段落盘"要求
- LIMITATIONS.md 局限 4 可补充"`steps` 配置可缓解空返回"的间接手段
