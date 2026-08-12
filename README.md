# agate

> 面向软件工程的 AI Agent 工作流协议。
> 通过阶段 gate、状态落盘、角色隔离编排 subagent。

[![version](https://img.shields.io/badge/version-v0.42.0-blue)](https://github.com/randomgitsrc/agate)
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

把仓库克隆到任意目录（在示例里我们用 `~/oclab/agate`，你也可以换任何路径）：

```bash
git clone https://github.com/randomgitsrc/agate.git ~/oclab/agate
ln -sfn ~/oclab/agate/agate ~/.agate
```

或使用安装脚本（一键完成上面两步）：

```bash
curl -sSL https://raw.githubusercontent.com/randomgitsrc/agate/main/install.sh | bash
```

安装脚本支持环境变量定制路径：

```bash
AGATE_REPO_DIR=~/.local/share/agate bash install.sh   # 指定仓库克隆位置
AGATE_SYMLINK=~/.my-agate bash install.sh             # 指定软链接位置
```

**目录结构怎么理解**

agate 是「项目开发协议」——它本身有开发资料（设计文档、评审记录、路线图、CHANGELOG 等）。这些和你**使用** agate 无关，混在一起会让你的项目仓库目录看起来很乱。

所以目录结构是：
- `<仓库根>/` = 仓库根（含开发资料 + `agate/` 子目录）
- `<仓库根>/agate/` = **协议本体**（你实际用的东西）
- `~/.agate` = 软链接指向协议本体，让你跨项目统一访问

软链接的**唯一约定**是必须指向 `<仓库根>/agate/` 协议本体子目录，仓库根路径随意。

**2. 把 orchestrator 注册成 OpenCode / Claude Code 能调用的 agent**

`orchestrator-template.md` 对所有项目内容完全一致，不需要拷贝改字段——**符号链接到你项目的 agent 目录即可**，agate 升级模板会自动跟着生效。项目特定信息（如果有）另放一个可选的 `project.md`，不动 orchestrator 本体。

完整步骤（含 Claude Code / OpenCode 具体命令、Windows 无符号链接权限的退化方案、要不要设默认 agent）见 **`agate/SETUP.md`**——这一步是平台相关、最容易卡住的一步，单独写了篇指南，不在这里展开。

**3. 第一次用，`docs/tasks/` 是空的，这是正常的**

不需要手动创建 `docs/tasks/active-tasks.md`——Agent 启动后会自己检查这个文件是否存在，不存在就从 `assets/templates/active-tasks-template.md` 复制结构、建好目录，再开始第一个任务（T001）。这个初始化逻辑写在 `orchestrator-template.md` 和 `state-machine.md` 里，不需要人工介入。

---

## 常见误区

1. **「我以为要 `cd` 到 agate 仓库根才开始」** —— **不要**。agate 仓库是协议的开发目录，**你只用到 `~/.agate` 这个软链接**。所有工作都在你自己的项目仓库里做。
2. **「我要按文件结构图把所有文件复制过来」** —— **不要**。只需要把 `orchestrator-template.md` 符号链接进平台的 agent 目录（见 `agate/SETUP.md`），不需要拷贝、不需要改任何字段，其余逻辑从 `~/.agate/` 实时读。
3. **「我需要 Python/数据库/部署服务」** —— 不需要。agate 是**纯文档协议**，没有任何运行时服务。所有 gate 检查都是 git pre-commit 钩子 + bash/Python 脚本。
4. **「装了就要放 `~/oclab/agate`」** —— 不是。仓库克隆路径随便，**只有 `~/.agate` 软链接是约定**。

## 升级

```bash
# 进入你克隆 agate 的目录（不一定是 ~/oclab/agate）
cd <你克隆 agate 的目录> && git pull
```

例如你当初克隆到 `~/.local/share/agate`：

```bash
cd ~/.local/share/agate && git pull
```

无需重装 hook——软链接会自动指向最新代码。

**已有 agate 项目（跑过任务）升级前，先读 `agate/UPGRADING.md`**——它讲清楚旧任务数据（active-tasks.md/.state.yaml/任务编号）如何处理，以及各版本的破坏性变更（如 v0.40.0 任务编号硬切，旧 `.state.yaml` 不兼容）。新接入项目直接读 `agate/SETUP.md`。

## 卸载

```bash
rm ~/.agate                          # 删软链接
rm -rf <你克隆 agate 的目录>          # 删仓库
```

你的项目里 `.claude/agents/orchestrator.md`、`.opencode/agents/orchestrator.md`（符号链接）与 `docs/agents/project.md`（如果创建了）等文件**不会**被删（它们独立于 agate）。

---

## 文件结构

```
agate-repo/                      # GitHub 仓库
├── README.md                    # 项目说明（本文件）
├── CHANGELOG.md
├── LICENSE
├── .github/                     # CI workflow
├── docs/                        # 项目文档（设计、评审、路线图）
├── archived/                    # 历史验证文档
├── agate/                       # 协议本体 ← ~/.agate 软链接指向这里
│   ├── AGENTS.md                # 协议本体入口指引（角色清单 + 升级/卸载）
│   ├── WORKFLOW.md              # P0-P8 核心规则、裁剪判断、阶段定义 ← 主入口
│   ├── dispatch-protocol.md     # 派发协议、gate 表、特殊事件处理
│   ├── state-machine.md         # 状态转移规则
│   ├── loop-orchestration.md    # /loop 自动编排（可选）
│   ├── git-integration.md       # git 提交规范
│   ├── role-system.md           # 角色体系说明
│   ├── platform-notes.md        # 各平台适配说明（OpenCode/Claude Code 等）
│   ├── SETUP.md                 # 首次接入指南（怎么注册成可调用的 agent）← 新项目从这里开始
│   ├── orchestrator-template.md # 主 Agent 提示词，对所有项目内容一致，符号链接接入
│   ├── LIMITATIONS.md           # 已知局限（使用前建议先读）
│   ├── assets/
│   │   ├── execution-roles/     # analyst/architect/implementer/verifier 等
│   │   ├── review-roles/        # review/cso/design-review/qa 等评审角色
│   │   └── templates/           # P0-brief、active-tasks、dispatch-prompt、project.md 等模板
│   └── scripts/                 # gate 检查脚本（pre-commit hook 安装源）
└── install.sh                   # 自动化安装脚本

~/.agate → <仓库根>/agate          # 软链接
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

### gate 判定对象分类

gate 按判定对象分为两类，可信度天然不同：

| 类型 | 阶段 | 判定对象 | 可信度 |
|------|------|----------|--------|
| **外部产出 gate** | P3, P4, P5 | 外部工具输出（test runner exit code, type checker, git log） | 高——主 Agent 无法伪造外部产出 |
| **自写文件 gate** | P1, P2, P6, P7 | 主 Agent 写的文件内容 | 需缓解——作者和裁判同一人，有造假风险 |

自写文件 gate 的缓解措施：证据存在性检查 + provenance 客观行为审计 + BDD 总数对照——**提高造假成本 + 留痕审计**，而非硬保证。详见 `agate/LIMITATIONS.md` 局限 3。

### 渐进采纳

不必用全流程才能受益。agate 支持裁剪，按需启用：

| 风险等级 | 推荐阶段 | 说明 |
|----------|----------|------|
| low | P0-P6 | P7 一致性可裁剪，P3 TDD 可裁剪（仅 low 风险） |
| medium | P0-P6 | 标准流程，P7 可裁剪，P3 不可裁（必须走 TDD 红灯） |
| high | P0-P8 | 全流程 + 人工终审 |

在 `P1-requirements.md` 设 `risk_level: low` 即可裁剪后续阶段，无需改协议。

---

## 已知局限

agate 是文档协议路线，这条路线有结构性的能力边界——测试质量上限、角色隔离的真实独立性、主 Agent 判断力的单点风险。详见 `agate/LIMITATIONS.md`，使用前建议先读一遍，避免误以为协议解决了所有问题。
