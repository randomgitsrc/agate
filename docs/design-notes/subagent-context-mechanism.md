# subagent context 的真实状态

> 本文记录 OpenCode / Claude Code 平台 subagent context 的实际构成，供 agate 协议设计参考。
> 来源：`docs/archived/reviews/agate-improvement-guide.md` 第一节（平台机制调研部分，事实性信息）。

---

## OpenCode 的 subagent context 构成

当 orchestrator 通过 Task tool 派发一个 subagent 时，子 session 拿到的 context 是：

```
子 session context
├── subagent 的 system prompt（角色文件内容）
├── Task tool 派发时传入的 prompt（orchestrator 写的指令）
├── 子 session 目录下的 AGENTS.md（如存在）
└── 父 session 的压缩摘要（关键：不是空白，也不是完整历史）
```

**"压缩摘要"的含义**：OpenCode 在触发 Task tool 时，会对父 session 的对话历史做一次 compaction，把压缩后的版本注入子 session。压缩程度和质量随父 session 的 token 量变化，不受 agate 协议控制。

实际影响：
- P1 之后的阶段，subagent 会"看到"前面所有阶段的摘要，不是真正的空白 slate
- 父 session 越长，注入的噪音越多，后期阶段的角色隔离效果越差
- agate 协议本身无法控制这个注入行为

**agate 的缓解**：铁律 2（只传路径不传内容）让 subagent 在独立上下文读文件，不依赖父 session 的历史摘要。压缩摘要即使注入了噪音，subagent 的主要输入仍是从文件读取的，角色定义文件约束其行为。

---

## Claude Code 的 subagent context 构成

```
子 session context
├── subagent 的 system prompt（.claude/agents/*.md 的 body）
├── Task tool 派发时传入的 prompt
├── 项目 CLAUDE.md（自动加载）
└── 仅摘要文本回传父 session（不反向污染）
```

关键差异：Claude Code 采用 **sidechain transcript** 机制，subagent 只把摘要回传给父 session，父 session 的 context 不会因为 subagent 的工作内容膨胀。这是 Claude Code 在 agate 场景下比 OpenCode 更可靠的结构性原因。

另外，Claude Code 的 Task tool 是同进程调用，没有 Go TUI → JS server 的 HTTP/SSE 中间层，subagent 在推理间隙被 SSE idle timeout 截断的问题在架构上不存在。

---

## 对 agate 设计的启示

1. **角色隔离是认知层面的，不是物理隔离**——与 LIMITATIONS.md 局限 2 一致。OpenCode 的压缩摘要注入进一步削弱了隔离效果，但 agate 的"只传路径 + 角色定义文件约束"是可用的缓解
2. **平台差异是结构性**，不可在协议层消除。agate 选择"文档协议，非代码框架"路线意味着接受这种平台差异（见 README 设计原则）
3. **OpenCode SSE 截断风险**——subagent 可能被 idle timeout kill，导致空返回。agate 的缓解是空返回恢复策略（dispatch-protocol.md「空返回的恢复策略」）+ 分阶段落盘
