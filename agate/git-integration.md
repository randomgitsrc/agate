# Git 集成：状态落盘的持久化

> agate，定义"状态文件何时入 git"——这是状态落盘真正生效的保证

---

## 为什么这是必要机制，不是可选项

v4 强调"状态落盘 + 抗中断恢复"。但有个隐含前提：**这些落盘的文件什么时候提交到 git？**

如果不提交：
- 状态文件只在本地，会话崩溃 / 环境重置后**全部丢失**——抗中断设计失效
- 多 agent 协作时（一台机器多个 agent），其他 agent pull 不到当前进度，重复劳动或冲突

所以 git commit 是状态落盘机制的**必要组成部分**，不是额外的运维步骤。

---

## 三条规则

### 规则 1：commit 由主 Agent 做，不是 subagent

subagent 在独立上下文里只负责产出文件，**不碰 git**。commit 是编排层（主 Agent）的职责。

如果每个 subagent 自己 commit，会产生混乱的提交历史，且 subagent 不知道全局状态，无法写出有意义的 commit message。

### 规则 2：一个阶段 = 一个 commit

不是每个 subagent 的中间操作都 commit（噪音太多），也不是整个任务才 commit 一次（中途崩溃丢进度）。

**粒度：每个阶段门槛通过后，主 Agent commit 一次。** 一个 Pn 阶段的产出是一个原子的进度单位。

```
P2 门槛通过（status==approved）→ 主 Agent commit
  message: "wf(T002-P2): 方案设计通过 — schema_version 表 + 顺序迁移脚本"

P5 门槛通过（failed==0）→ 主 Agent commit
  message: "wf(T002-P5): 验证通过 — 23 测试全绿，P1 问题 5/5 解决"
```

commit message 格式：`wf({task_id}-{phase}): {一句话进度}`，可追溯。

> 注：`wf()` 前缀是 agate 工作流进度提交的专用约定，与项目现有的 Conventional Commits（`feat:`/`fix:`/`docs:` 等）**并行使用，不冲突**。

**两种前缀的判定标准（消除"常规变更"这种模糊说法）**：

| commit 内容 | 前缀 | 例子 |
|---|---|---|
| 某个阶段门槛刚通过，记录"进度到哪了" | `wf({task_id}-{phase}):` | `wf(T011-P2): 方案设计通过` |
| 任务全部完成（P8 之后）或某阶段产出的代码本身，描述"做了什么功能/修了什么问题" | `feat({task_id}):` / `fix({task_id}):` | `feat(T011): 用户管理 API+CLI` |
| 和具体任务无关的变更（依赖升级、格式化、临时脚本）| 标准 Conventional Commits，不带 task_id | `chore: 升级 pytest` |

**实测验证**（实际项目历史 commit 抽样核实）：阶段记录类 commit 基本都正确使用了 `wf()`；功能描述类 commit（即使在同一任务里）自然倒向了 `feat(Txxx):`，这恰好印证了上面的判定标准——**两种前缀本来就对应两种不同的 commit 意图，不是"漏用"，是约定一直隐含存在，只是之前没有写清楚**。本节的修订是把这个隐含约定显式化，不是改变实际行为。

### 规则 3：push 分档位，且 push 前必须 pull --rebase

push 涉及和远端同步，多 agent 并发 push 会频繁冲突。不该每个 commit 都立即 push。

```
档位 A/B（手动/半自动）：
  - 每个任务完成（P8 gate 通过、进入 READY）后 push 一次
  - 或用户明确要求 push 时

档位 C（/loop 全自动）：
  - 默认每个任务完成时 push
  - 可配置 --push-every-phase 改为每阶段 push（多 agent 需要实时同步时）

push 前必须：git pull --rebase origin main
push 失败（远端有新提交）→ pull --rebase → 重新 push，最多重试 3 次
  → 仍失败 → PAUSED 报告人工（可能有冲突需要手动解决）
```

---

## 多 Agent 并发的特别说明

一台机器多个 agent 同时跑不同任务时，git 是共享的。冲突主要来自：

1. **active-tasks.md 并发修改**：多个 agent 同时更新看板 → 冲突高发
2. **同时 push**：A push 成功后 B push 被 reject

### 缓解策略

**策略 1：任务目录隔离**
每个任务的产出在自己的 `docs/tasks/Txxx/` 目录，不同任务的 agent 改不同目录，文件级冲突少。

**策略 2：active-tasks.md 只改自己任务那一行**
看板更新：owner agent 从该任务 `.state.yaml` 派生，**只重写自己负责的那一行**，不整体重写，不碰其他任务的行。`.state.yaml` 是唯一真相源，active-tasks.md 是派生视图。（与 state-machine.md 一致）

**策略 3：push 串行化（推荐）**
多 agent 环境下，push 操作天然串行（git 远端是单点）。每个 agent push 前 pull --rebase，失败就重试。这是 git 的标准并发模型，能 work，只是偶尔要重试（本项目开发过程中已多次验证：rebase 后重推即可）。

**策略 4：高并发时考虑分支**
如果 agent 数量多、冲突频繁，可以每个任务用独立分支，完成后合并。但这增加复杂度，单机 5 个 agent 的规模用 main + rebase 通常够用。

---

## commit/push 在状态机里的位置

```
主 Agent 单步函数（见 state-machine.md），补充 git 步骤：

function 执行一步(task_id):
    1. 读 active-tasks.md → 当前状态
    2. 确认输入就绪
    3. 派发 subagent
    4. 接收返回 + 校验
    5. 判定门槛
    6. 更新 active-tasks.md
    7. 【新增】git commit（规则 2：一阶段一 commit）
       git add docs/tasks/{task_id}/ docs/tasks/active-tasks.md
       git commit -m "wf({task_id}-{phase}): {摘要}"
    8. 【新增】按档位决定是否 push（规则 3）
       if 该 push:
           git pull --rebase origin main
           git push（失败则 rebase 重试，最多 3 次）
    9. 返回下一状态
```

---

## 异常处理

| 异常 | 处理 |
|------|------|
| commit 失败（无改动）| 跳过，可能是 subagent 没产出文件，回到门槛检查 |
| push reject（远端更新）| pull --rebase → 重推，最多 3 次 |
| rebase 冲突 | PAUSED，报告人工（自动解冲突风险高，不做）|
| 3 次重推仍失败 | PAUSED，报告人工 |

**rebase 冲突绝不自动解决**——自动解冲突可能丢数据。遇到冲突就停下来交给人。

---

## 与"抗中断恢复"的闭环

git 集成让状态落盘真正闭环：

```
状态写入文件（state-machine）
    ↓
每阶段 commit（git-integration）← 持久化到版本库
    ↓
会话崩溃 / 环境重置
    ↓
重新 clone / pull → 状态文件完整恢复
    ↓
读 active-tasks.md → 接着上次的阶段继续
```

没有 git 集成，"状态落盘"只是写本地文件，崩溃就丢。有了它，状态真正持久、可恢复、可多 agent 共享。

---

## Hardening-roadmap 集成（自 v0.4 引入，持续生效）

git 集成自 v0.4 hardening-roadmap 起承担了新的角色：**阶段 commit 会触发 9 项 pre-commit 检查**（详见 WORKFLOW.md「Pre-commit 检查总览」）。这不是新规则——而是把已有的状态机 gate 检查自动化到了 commit 入口：

| 触发点 | 检查内容 | 拦截行为 |
|--------|---------|---------|
| 暂存 `.state.yaml` 变更时 | 格式合法性（P2.15）| 格式错 → 拦截 commit |
| phase 变更或阶段产出文件变更时 | gate 通过性（P1.1）| gate 失败 → 拦截 commit |
| P6/P7 阶段 commit 时 | 证据目录非空 + BDD 行数 ≥ 1（P1.7）| 缺证据 → 拦截 commit |
| gate 通过后 | 三道客观行为审计（P2.1/P2.10）| 客观审计失败 → exit 1 拦截；agent 字段等协作规范问题 → exit 2 WARNING |
| gate 通过后 | 状态转移合法性 + 重试上限（P2.3-P2.5）| 非法转移 → 拦截 commit |
| gate 通过后 | 裁剪条件一致性（P2.7-P2.9）| 裁剪与执行不一致 → 拦截 commit |
| gate 通过后 | SCOPE+ 已增补并标记（P2.11）| 未标 `[SCOPE_RESOLVED]` → 拦截 commit |
| 任何 commit | 异常模式提醒（P2.12）| 检测到 gate 重试超限（P3/P5/P6/P7/P8 ≥2、P1/P2/P4 ≥3）/ SCOPE+ / override → 提醒写复盘（不阻塞）|
| 任何 commit | CHANGELOG `[Unreleased]` 含 task_id（P1.6）| 缺记录 → 警告（不阻塞）|

**`--cached` vs `HEAD~1`**：pre-commit hook 运行时 commit 尚未创建，所有 `git diff` 必须用 `--cached`（暂存区 vs HEAD），不能用 `HEAD~1`（上一个 commit）。P4/P7/P8 的源文件数检查、version bump 检查、CHANGELOG 检查均遵循此规则。主 Agent 手动验证（commit 后）可用 `HEAD~1`，但 hook 场景下 `--cached` 是唯一正确选择。

**commit message 建议**：虽然是 wf()/feat()/fix() 前缀规则，但 hardening 后建议在 message body 里提"阶段"：

```
wf(T042): P2 review approved
- architect: 完整设计含 gate_commands
- 风险: high，由独立 plan-eng-review 评审通过
```

**禁止 `--no-verify` 绕过 hook**：CI backstop 会重跑 `check-gate.sh` + git blame 单 author WARNING，绕过 hook 的"恶意 commit"会被抓到并在日志暴露。详见 LIMITATIONS.md 局限 3。

**P6 单 author WARNING**：当 P6-acceptance.md git blame 显示只有一个 author（通常是主 Agent 自写而不是独立 verifier），CI 会发 WARNING——这是 provenance 客观审计之外的最后一层可观测性兜底。

---

*git 集成是状态落盘机制的必要组成部分，配合 state-machine.md 和 loop-orchestration.md*
