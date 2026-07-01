---
task_id: agate-output-path-constraint
agent: main
date: 2026-07-02
status: 设计文档（v2，自行评审修订已纳入）
来源: 用户反馈——subagent 产出文件路径不匹配导致返工浪费
---

# 设计：subagent 产出路径约束

## 问题

现状：派发模板告知了 subagent "产出文件：docs/tasks/{Txxx}/{文件名}"，但缺少禁止性约束。subagent 可能：

1. 把文件写到 `/tmp/opencode/xxx.md`（OpenCode 默认临时目录）
2. 写到工作区根目录
3. 写到其他自选路径

后果：主 Agent 校验 `docs/tasks/{Txxx}/P{N}-*.md` → 文件不存在 → 判定"空返回"→ 计入重试 → 浪费一轮 subagent 调用。

对于非阶段产出（self-gate 审查报告 `docs/reviews/`、设计文档 `docs/plans/` 等），路径完全靠主 Agent 在 prompt 里手写，没有统一约束模板。

## 根因分析

| 根因 | 现状 | 影响 |
|------|------|------|
| 派发模板只有"正向告知"（写到哪），无"反向禁止"（不得写到哪） | subagent 知道路径但不觉得是硬约束 | 阶段产出偶尔写错位置 |
| 非阶段产出（审查/评审/设计文档）无统一路径模板 | 每次手写，容易遗漏 | subagent 无路径可循 → 写到临时目录 |
| 主 Agent 校验逻辑只检查约定路径 | 写到其他位置 = 文件不存在 = 空返回 | 浪费一轮重试 |

## 设计

### 1. 派发模板加路径约束（阶段产出）

在 dispatch-protocol.md 和 dispatch-prompt.md 的"## 输出"节，加禁止性约束：

```markdown
## 输出（路径约束）
产出文件：docs/tasks/{Txxx}/{本阶段产出文件}

⚠️ 路径是硬约束，不是建议：
- 必须用 Write 工具写入上述路径
- 不得将产出文件写入 /tmp、工作区根目录、或其他自选路径
- 写到其他位置 = 未产出，主 Agent 只检查上述路径
```

注意：`/tmp` 可用于中间临时文件（如 gate-runner 落盘 traceback 供修复 subagent 读取），但**产出文件**（主 Agent 校验的那个）必须写入约定路径。

### 2. 非阶段产出路径规范（通用约束）

在 dispatch-protocol.md 新增一节"## 非阶段产出的路径规范"，覆盖 self-gate 审查、设计评审、计划文档等场景：

```markdown
## 非阶段产出的路径规范

主 Agent 派发非阶段 subagent（如 self-gate 审查、设计评审、计划编写）时，
prompt 的"## 输出"节必须：

1. 给出**具体路径**（用 `{project_root}/docs/reviews/xxx.md` 格式，不用纯占位符也不用绝对路径）
2. 声明路径硬约束（同阶段产出："不得写入 /tmp 或其他路径"）
3. 区分留痕文件（bash 追加）和成果文件（Write 工具一次写出）——不要混用

示例（self-gate 审查派发）：
  ## 产出（成果文件）
  路径：{project_root}/docs/reviews/agate-alignment-review-{date}.md
  用 Write 工具写入此路径。不得写入 /tmp 或其他路径。

  ## 分阶段落盘（留痕文件）
  路径：{project_root}/docs/reviews/agate-alignment-{date}-{NN}.progress.md
  用 bash 追加：echo "- [文件名] 摘要" >> {留痕文件路径}
```

### 3. self-gate 派发模板同步

SELF-GATE.md 的两个派发模板（变更触发 + 全量审查）的"## 产出"节已有路径，但缺少路径硬约束声明。补加"不得写入 /tmp 或其他路径"。

### 4. "关键提醒"节同步

dispatch-prompt.md 的"关键提醒"节补一条：

```markdown
- **产出路径是硬约束**：subagent 必须写入 prompt 指定的路径，不得将产出文件写到 /tmp 或其他位置。主 Agent 只检查约定路径，写错位置 = 未产出 = 重试浪费
```

### 5. orchestrator-template.md 检查

orchestrator-template.md 引用 dispatch-protocol.md 的派发模板（L52："见 dispatch-protocol.md「输入导航原则」"），不内联模板内容，无需同步。确认即可。

## 变更文件清单

| 文件 | 改动 |
|------|------|
| `agate/dispatch-protocol.md` | "## 输出"节加路径约束 + 新增"非阶段产出的路径规范"节 |
| `agate/assets/templates/dispatch-prompt.md` | "## 输出"节加路径约束 + "关键提醒"节补一条 |
| `SELF-GATE.md` | 两个派发模板的"## 产出"节加路径约束 |

## 不做的事

- 不加脚本检查（产出路径由主 Agent 校验，不需要 gate 脚本介入）
- 不改测试（纯文档约束，不涉及脚本行为）
- 不改角色文件（角色文件不涉及产出路径，路径由派发 prompt 指定）
