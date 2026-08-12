# agate 整改建议与多平台适配指南

> **评审裁决（2026-06-28）**：已评审。第一节（context 机制调研）有价值，已提取到 `docs/design-notes/subagent-context-mechanism.md` 作为设计参考。第二/三/四节的整改建议**不采纳**：
> - 阶段状态文件 `.running/.done/.failed` 重复 gate 机制且是 subagent 自我报告（违反 C7 规则）
> - context 边界声明"忽略历史"不可执行（prompt 无法控制已注入的压缩摘要）
> - orchestrator context 重置节点触发条件不可判定（`/context` 是 OpenCode 特有命令）
> - Claude Code `.claude/agents/` frontmatter 格式是项目级配置，不属于 agate 协议规范范围
> - 方法 B 标准化已在 dispatch-prompt.md 模板落地
>
> 第五节（不建议改的部分）判断准确，保留作为参考。
>
> 基于对 agate v1.2.0 的结构分析，以及对 OpenCode/Claude Code subagent 底层机制的深入调研。
> 覆盖三个部分：subagent context 真实机制、OpenCode 平台整改、Claude Code 适配。

---

## 一、subagent context 的真实状态

理解这个是所有整改的前提。agate 的"角色隔离"在不同平台上的实际效果差异很大。

### OpenCode 的 subagent context 构成

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

### Claude Code 的 subagent context 构成

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

## 二、OpenCode 平台：现有问题与整改建议

### 问题 1：subagent 被截断后协议无处理路径

**现象**：subagent 还在推理/执行阶段，SSE 连接在模型思考间隙被 upstream idle timeout 断掉，进程被 kill。`active-tasks.md` 里该阶段状态未更新，orchestrator 收到空值，不知道该 pass 还是 fail。

**根因**：OpenCode 的 stream idle timeout 在模型推理的静默期触发，没有 heartbeat 机制保活。这是 OpenCode 的基础设施 bug，不是 agate 的配置问题，prompt 层面无法根除。

**整改方向：引入阶段级状态文件**

在 `docs/tasks/phases/` 目录下，用文件的存在性替代 Task tool 返回值作为阶段完成的判断依据：

```
docs/tasks/phases/
  P2-architect.running      # subagent 启动时写（第一个 bash 动作）
  P2-architect.done         # subagent 正常完成时写（最后一个 bash 动作）
  P2-architect.failed       # gate 不通过或 subagent 报告失败时写
```

**subagent dispatch prompt 里加强制要求**：

```markdown
## 执行规范（不可省略）

**第一步（收到任务后立即执行，优先于任何分析）**：
bash: echo '{"phase":"P2","started_at":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' \
  > docs/tasks/phases/P2-architect.running

**最后一步（所有工作完成后执行）**：
成功时：
bash: echo '{"phase":"P2","status":"done","artifacts":["<产出文件路径>"],"summary":"<一句话摘要>"}' \
  > docs/tasks/phases/P2-architect.done

失败时：
bash: echo '{"phase":"P2","status":"failed","reason":"<失败原因>"}' \
  > docs/tasks/phases/P2-architect.failed
```

**orchestrator 空值处理规则（加入 dispatch-protocol.md）**：

```markdown
## 空值处理规则

Task tool 返回空字符串时，orchestrator 不重新派发，先执行诊断：

1. 检查 docs/tasks/phases/{phase}.done 是否存在
   → 存在：视为完成，读取文件内容继续，Task tool 返回值可忽略

2. 检查 docs/tasks/phases/{phase}.failed 是否存在
   → 存在：读取原因，按 gate 失败流程处理

3. 检查 docs/tasks/phases/{phase}.running 是否存在
   → 存在且时间戳 < 10 分钟：subagent 可能仍在运行，等待 30s 后重新检查
   → 存在且时间戳 ≥ 10 分钟：判定为截断，清除 .running 文件，重新派发

4. .running 也不存在：判定为 subagent 未启动，直接重新派发
```

---

### 问题 2：context 污染随任务推进累积

**现象**：P4/P5 阶段的 subagent 会带入前三个阶段的压缩摘要，与角色定义产生干扰，导致 implementer 可能受 analyst 的分析框架影响。

**整改方向：dispatch prompt 显式 context 清洗**

在每次派发的 prompt 头部加标准化的 context 边界声明：

```markdown
## Context 边界（严格遵守）

你是 P{N} {角色名}，此次任务的完整输入是以下内容，忽略其他：

**必须读取的文件**：
- {明确列出的文件路径，不超过3个}

**不需要了解的内容**：
- 本次任务启动前的所有对话历史
- 其他阶段的实现细节
- orchestrator 的内部判断过程

你的输出格式：[明确规定]
你的完成标志：写入 docs/tasks/phases/P{N}-{role}.done
```

---

### 问题 3：orchestrator context 随任务推进膨胀

**现象**：orchestrator 是单个长 session，每次派发和验收都在积累历史。P8 时的 orchestrator context 可能已经包含了 P1-P7 的全部交互，影响判断质量，并增加 compaction 压力。

**整改建议：在 state-machine.md 里加 context 重置节点**

每 3 个阶段（或 orchestrator 达到 100K token）强制执行一次：

```markdown
## Orchestrator Context 重置规则

触发条件（任一）：
- 完成 P3 / P6 阶段后
- /context 显示超过 100K tokens

重置步骤：
1. 把当前 active-tasks.md 和 .state.yaml 的关键字段存入
   docs/tasks/checkpoint-{timestamp}.md
2. 告知用户需要开新 session
3. 新 session 启动时，orchestrator 第一步读 checkpoint 文件恢复状态
```

---

### 问题 4：OpenCode 自定义角色加载失败（issue #29616）

**现状**：platform-notes.md 已记录，方法 A（`--custom-role`）不可用，必须用方法 B（在 dispatch prompt 里直接写角色文件路径，让 subagent 自己读）。

**整改建议**：把方法 B 标准化为协议规范，不要等 OpenCode 修复。

dispatch prompt 模板统一加入：

```markdown
## 你的角色定义

请立即读取以下文件获取你的完整角色定义，这是你本次任务的行为准则：
`~/.agate/assets/execution-roles/P{N}-{role}.md`

读取后，严格按照该文件的规定执行，不得偏离。
```

---

## 三、Claude Code 平台适配

### 3.1 subagent 定义格式

Claude Code 的 subagent 定义文件放在 `.claude/agents/` 目录，使用特定的 YAML frontmatter 格式。

**目录结构**：

```
your-project/
└── .claude/
    └── agents/
        ├── P1-analyst.md
        ├── P2-architect.md
        ├── P3-test-designer.md
        ├── P4-implementer.md
        ├── P5-verifier.md
        └── P6-reviewer.md       # 可选
```

**frontmatter 字段说明**：

```yaml
---
description: >
  P2 architect。当需要系统设计、技术选型、模块拆分时使用。
  输出：docs/tasks/{task-id}-arch.md
model: anthropic/claude-sonnet-4-6
tools:
  read: true
  write: true
  edit: false
  bash: true        # 需要写阶段状态文件
  glob: true
  grep: true
disallowedTools:
  - WebSearch       # 架构设计不需要搜索
---

# P2 Architect

（原有角色 system prompt 内容，直接放在 frontmatter 之后）
...
```

**字段说明**：

`description` 是 Claude Code 决定何时自动路由到这个 subagent 的依据，写清楚"什么情况下用这个角色"比写角色名称更重要。

`model` 建议：P1/P2（分析/设计）用 `claude-sonnet-4-6`，P4（实现）可以用同一个，P5（验证）可以用 `claude-haiku-4-5` 降低成本。

`tools` 遵循最小权限原则。特别注意：所有角色都需要 `bash: true` 才能写阶段状态文件（`.running` / `.done` / `.failed`）。

---

### 3.2 orchestrator 加载方式

Claude Code 里 orchestrator 有两种加载路径，选其一：

**方式 A：作为项目级 CLAUDE.md（推荐）**

把 `orchestrator.md` 的内容直接写进项目根目录的 `CLAUDE.md`：

```
your-project/
└── CLAUDE.md          ← orchestrator 内容放这里
```

优点：每次 `claude` 启动时自动加载，不需要手动指定。缺点：CLAUDE.md 同时也是项目上下文，内容会变长。

适合场景：agate orchestrator 是这个项目的主要工作模式。

**方式 B：作为 primary agent 文件（推荐多项目场景）**

```
your-project/
└── .claude/
    └── agents/
        └── orchestrator.md     ← mode: primary
```

frontmatter：

```yaml
---
description: agate 编排 Agent，负责读状态、派发 subagent、验 gate、更新状态。
mode: primary
model: anthropic/claude-opus-4-6   # orchestrator 用强模型
---

# Orchestrator — {项目名}
（orchestrator-template.md 的内容）
```

启动方式：在项目目录运行 `claude`，用 `Tab` 键切换到 orchestrator agent。

**方式 C：用户级 agent（跨项目复用）**

如果同一套 orchestrator 逻辑要用在多个项目：

```
~/.claude/
└── agents/
    └── agate-orchestrator.md   ← 通用 orchestrator，不含项目特定配置
```

项目特定配置（`project_root`、技术栈约束等）通过项目的 `CLAUDE.md` 或 `.claude/agents/orchestrator.md` override。

---

### 3.3 使用方式

**启动流程**：

```bash
# 进入项目目录
cd your-project

# 启动 Claude Code
claude

# 如果 orchestrator 是 primary agent，Tab 切换到它
# 如果 orchestrator 内容在 CLAUDE.md，直接开始对话

# 第一次使用，触发初始化
> 开始第一个任务：[任务描述]
```

orchestrator 会自动检查 `docs/tasks/active-tasks.md` 是否存在，不存在则初始化（这个逻辑已经在 orchestrator-template.md 里，不需要改）。

**派发 subagent 的方式**：

Claude Code 里 orchestrator 不用 `@mention`，直接用自然语言让模型调用 Task tool：

```
（orchestrator 内部决策）
→ 调用 Task tool，指定 subagent_type="P2-architect"（对应 .claude/agents/P2-architect.md）
→ 传入 dispatch prompt（按 dispatch-protocol.md 规范）
```

Claude Code 会根据 description 字段自动匹配 subagent，也可以在 dispatch prompt 里明确指定角色文件路径。

**gate 验收**：

orchestrator 自己通过 bash tool 执行 gate 命令，不等 subagent 报告：

```bash
cd {project_root} && pytest tests/ --tb=short -q
# exit code 0 → gate pass → 更新 active-tasks.md → 派发下一阶段
# exit code 非0 → gate fail → 按 dispatch-protocol.md 的失败处理路径
```

**手机端监控（Claude Code web）**：

Claude Code 的云端 web 模式（claude.ai/code）支持 subagent，但连接的是 GitHub 仓库而不是本地文件系统。如果需要手机监控本地运行的 agate loop，目前的选项是：

- 用 `cloudcli` 或 `claude-code-web` 第三方项目在局域网暴露 web UI
- 用 Claude Code 的 Remote Control 功能（`/rc` 命令）在同一账号下的手机 App 上查看进度

---

### 3.4 assets 目录的 Claude Code 适配

`assets/execution-roles/` 里的角色文件需要加 YAML frontmatter 才能被 Claude Code 识别。建议保持原有文件不动，在 `.claude/agents/` 里新建包装文件：

```markdown
---
description: P4 implementer。接收 P3 产出的测试用例，实现代码使测试通过（TDD）。
model: anthropic/claude-sonnet-4-6
tools:
  read: true
  write: true
  edit: true
  bash: true
  glob: true
  grep: true
---

<!-- 引用原始角色定义 -->
<!-- Claude Code 不支持 include，直接把内容复制过来，或在下一行写路径让 subagent 自己读 -->

请首先读取你的完整角色定义：
`~/.agate/assets/execution-roles/P4-implementer.md`

然后执行以下任务：
（dispatch prompt 会在 Task tool 调用时注入）
```

这样做的好处：`~/.agate/assets/execution-roles/` 里的原始角色文件继续作为权威定义维护，`.claude/agents/` 里的文件只是适配层，两个平台的角色定义不会漂移。

---

## 四、整改优先级建议

按影响程度排序：

**P0（必须，解决 subagent 截断问题）**
- 在所有平台的 dispatch prompt 里加 `.running` / `.done` / `.failed` 状态文件的写入规范
- 在 dispatch-protocol.md 里加空值处理规则

**P1（重要，减少 context 污染）**
- 所有 dispatch prompt 头部加 context 边界声明
- 在 state-machine.md 里加 orchestrator context 重置节点

**P2（平台适配）**
- Claude Code：创建 `.claude/agents/` 目录，为每个角色写 frontmatter 包装文件
- Claude Code：选择 orchestrator 加载方式（CLAUDE.md 或 primary agent）
- OpenCode：把方法 B 标准化，不再依赖方法 A

**P3（长期优化）**
- 考虑对 OpenCode 场景下超过 P4 的长任务，把 dispatch 层从 Task tool 改为 `opencode run` 子进程调用，从根本上解决 SSE 截断问题

---

## 五、不建议改的部分

agate 的以下设计是对的，不需要动：

- **文档协议路线**：零基础设施依赖，跨平台迁移只改适配层，核心逻辑不动
- **gate 用客观 exit code**：pytest/npm test 不依赖模型自判断，这是整个协议的质量保障
- **状态落盘到 active-tasks.md**：中断续跑能力，保持
- **orchestrator 不亲自写代码**：防止 context 污染的核心隔离，保持
- **`~/.agate/` 标准安装位置**：跨项目复用，保持

---

*文档版本：基于 agate v1.2.0 分析，2026-06-28*
