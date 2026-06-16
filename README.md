# agate

> AI Agent workflow protocol for software engineering.
> Orchestrate subagents with phase gates, state persistence, and role isolation.

[![version](https://img.shields.io/badge/version-v1.0.0-blue)](https://github.com/randomgitsrc/agate)
[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**agate** 是一套面向软件工程的 AI Agent 编排协议。

让 LLM Agent 能可靠完成复杂开发任务——通过「主 Agent 派发 subagent、阶段 gate 验收、状态落盘」的机制，解决单 Agent 在长任务中上下文污染、质量失控的问题。

> agent + gate → agate

---

## 核心思路

```
主 Agent（Orchestrator）
  ↓ 派发
P1 analyst → P2 architect → P3 test-designer → P4 implementer → P5/P6 verifier
  ↓ 每阶段
gate 验收（pytest/npm test exit code，BDD 实跑）
  ↓ 通过
状态落盘（active-tasks.md）→ 进入下一阶段
```

主 Agent 只做四件事：读状态、派发 subagent、验 gate、更新状态。不亲自写代码。

---

## 快速上手

**1. 安装 agate（标准位置 `~/.agate/`）**

```bash
git clone https://github.com/randomgitsrc/agate.git ~/.agate
```

约定使用 `~/.agate/` 作为标准安装位置，所有项目共用一份，orchestrator.md 路径统一，换机器只需重新 clone 到同一位置。

**2. 在你的项目里创建 orchestrator**

```bash
cp ~/.agate/orchestrator-template.md \
   your-project/docs/agents/orchestrator.md
```

**3. 填写项目信息**

打开 `orchestrator.md`，`agate_root` 已预填为 `~/.agate`，只需填写 `project_root` 和项目特定约束。

**4. 把 orchestrator.md 配置给你的 Agent**

在 OpenCode/Claude Code 里将 `orchestrator.md` 设为角色提示词，开始第一个任务。

---

## 文件结构

```
agate/
├── README.md                    # P0-P8 核心规则（本文件）
├── dispatch-protocol.md         # 派发协议、gate 表、特殊事件处理
├── state-machine.md             # 状态转移规则
├── loop-orchestration.md        # /loop 自动编排（可选）
├── git-integration.md           # git 提交规范
├── role-system.md               # 角色体系说明
├── platform-notes.md            # 各平台适配说明（OpenCode/Claude Code 等）
├── orchestrator-template.md     # 新项目接入模板 ← 从这里开始
├── assets/
│   ├── execution-roles/         # analyst/architect/implementer/verifier 等
│   ├── review-roles/            # staff-engineer/security/qa 等评审角色
│   └── templates/               # P0-brief、dispatch-prompt 等模板
└── archived/                    # 历史验证文档
```

---

## 适用平台

| 平台 | task 工具 | 推荐用途 |
|------|----------|---------|
| OpenCode | ✅ | 完整 P0-P8 |
| Claude Code | ✅ | 完整 P0-P8 |
| Claude Project 会话 | ❌ | 仅 P0-P2 设计阶段 |

详见 `platform-notes.md`。

---

## 设计原则

- **文档协议，非代码框架**：零基础设施，Agent 能读文件就能用
- **gate 是硬边界**：pytest/npm test exit code 客观可量化，不靠「看起来对」
- **状态落盘**：任何中断都能从最近的阶段续跑
- **角色隔离**：每个阶段由专职 subagent 执行，主 Agent 不污染上下文
