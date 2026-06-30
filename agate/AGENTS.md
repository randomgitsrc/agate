# agate 协议本体

> 本目录是 **agate 协议的运行时本体**。
> 软链接 `~/.agate` 默认指向这里（你克隆 agate 时指定的仓库根下的 `agate/` 子目录）。
> 路径表述：协议文档内写 `{agate_root}/WORKFLOW.md` 等于 `本目录/WORKFLOW.md`。

---

## 这是什么

`docs/`（仓库根的）目录存放 agate **项目的开发资料**——设计文档、评审记录、路线图、复盘。这些都是仓库维护者（author）写的，**使用者无需阅读**。

你看到 `agate/` 这一层，是**协议本体**——里面是一组编排协议文件，告诉 AI Agent 怎么用 agate 完成一个软件工程任务。**你（使用者）从这里开始**：

| 你要做什么 | 看这里 |
|------|------|
| 第一次接入 agate 到我的项目 | `orchestrator-template.md`（拷贝到你的项目里的入口） |
| 理解 P0-P8 阶段流程 | `WORKFLOW.md`（主流程，主入口） |
| 派发 subagent 的细节 | `dispatch-protocol.md` |
| 状态机/转移规则/重试上限 | `state-machine.md` |
| 角色体系（双层角色） | `role-system.md` |
| 用 git 持久化状态 | `git-integration.md` |
| /loop 自动编排 | `loop-orchestration.md` |
| 不同平台适配（OpenCode/Claude Code） | `platform-notes.md` |
| 已知局限 | `LIMITATIONS.md`（使用前建议先读） |

## 给 Agent 的快速指令

如果你是被主 Agent 派发的 subagent：

1. 读 `dispatch-protocol.md` 了解派发协议
2. 读 `assets/execution-roles/{你的角色}.md`（如 analyst/architect/implementer 等）
3. 按角色文件的指令执行
4. 退出时确保产出了正确的阶段文件（如 `P2-design.md`）

角色文件清单：

```
assets/execution-roles/
├── analyst.md            # P1 需求分析
├── architect.md          # P2 设计
├── test-designer.md      # P3 测试设计
├── implementer.md        # P4 实现
├── verifier.md           # P5/P6 验收
└── vision-analyst.md     # P6 UI/视觉验收

assets/review-roles/
├── review.md             # 通用评审
├── design-review.md      # 设计评审
├── plan-ceo-review.md    # 计划层（产品维度）评审
├── plan-eng-review.md    # 计划层（工程维度）评审
├── plan-design-review.md # 计划层（设计维度）评审
├── cso.md                # 首席安全官评审
├── qa.md                 # 质量保障评审
├── investigate.md        # 事后排查
└── office-hours.md       # 自由提问
```

## 升级 agate

```bash
# 进入你克隆 agate 的目录
cd <你克隆 agate 的目录> && git pull
```

下次 commit 自动用新版本协议。如果你之前安装了 pre-commit hook，无需重装——软链接会自动指向新代码。

## 卸载

```bash
rm ~/.agate                          # 删软链接
rm -rf <你克隆 agate 的目录>          # 删仓库
```

## 更多

仓库根的 `README.md` 有面向**新用户**的接入指南；本目录是面向**深入使用者和 Agent** 的协议本体入口。

有问题看 `LIMITATIONS.md`，别在文档没覆盖的地方反复猜。
