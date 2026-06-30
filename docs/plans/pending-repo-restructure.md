# 待办：GitHub 仓库目录结构重构

> 来源：2026-06-30 讨论
> 前置：v2 降级方案实施完成后启动
> 不涉及改动协议本体，只动 GitHub 仓库文件结构

## 问题

`~/.agate/` 既是协议执行本体，又是 GitHub 仓库根目录。导致使用者看到 `docs/plans/`、`docs/reviews/`、`.github/`、`CHANGELOG.md` 等项目开发文件，对使用者是噪音。

## 方案

GitHub 仓库分两层：项目资料 + 协议本体（子目录）。

```
~/oclab/agate/                    # GitHub 仓库（项目资料）
├── README.md                     # 项目介绍、安装说明
├── docs/                         # 项目文档（设计、评审、路线图）
├── CHANGELOG.md
├── .github/
├── agate/                        # 协议本体（纯净）
│   ├── WORKFLOW.md
│   ├── dispatch-protocol.md
│   ├── state-machine.md
│   ├── role-system.md
│   ├── loop-orchestration.md
│   ├── git-integration.md
│   ├── platform-notes.md
│   ├── orchestrator-template.md
│   ├── LIMITATIONS.md
│   ├── scripts/
│   └── assets/
└── install.sh                    # 安装脚本

~/.agate/ → ~/oclab/agate/agate  # 软链接
```

## 安装命令

原：`git clone https://github.com/randomgitsrc/agate.git ~/.agate`

改：`git clone https://github.com/randomgitsrc/agate.git /tmp/agate-repo && ln -s /tmp/agate-repo/agate ~/.agate`

或 install.sh 自动化。

## 影响

- 协议本体内部引用路径不变（`{agate_root}/WORKFLOW.md` 等）
- `{agate_root}` 解析为软链接目标，对读取透明
- 项目开发在 `~/oclab/agate/` 里正常做
- 需更新：README.md 安装说明、install-hook.sh 中 REPO_ROOT 解析、CI workflow 路径
- 本体目录名待确认：`agate` / `agate-core` / 其他
