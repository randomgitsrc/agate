# agate × deepseek-harness（DSH）结合可行性方案

> 基于对 DSH 代码库（`/home/kity/oclab/deepseek-harness`，v0.1.0-rc.8）的只读研究 + 本会话实机验证。
> 结论先行：**可行性高**——agate 编排者的四项职责（读状态/派发/跑 gate/更新状态）在 DSH 中全部有原生承载，且有三种集成路线可选。

---

## 1. DSH 是什么（能力画像）

- **形态**：pnpm monorepo + [cordis](https://cordis.js.org/) 插件框架；40+ 独立插件包（`packages/<area>/<leaf>`），由 `packages/bundle/base/cordis.patch.yml` 统一装配
- **工具面**（本会话实机验证）：bash（含 exit code 标记、后台 job、沙箱）、read/write/edit、glob/grep、web_search、subagent/subagent_fork（后台派发）、workflow（JS 脚本多代理编排）、goal（跨轮目标）、ralph（fresh-agent 循环）、skill、job 管理、Web GUI（`http://127.0.0.1:23701`）
- **沙箱/审批**：默认 `workspace-write` 权限模式（`DSH_PERMISSION_MODE`），可升级阶梯 read-only→workspace-write→danger-full-access；审批经 `ctx.approval.request`
- **扩展机制**：无 `.claude/agents/*.md` 式模板注册；最接近的是 **agent-presets**（`agent.cordis.yml` + `preset.yml` 声明式 agent 组合）与 **skills**（SKILL.md + frontmatter，自动进会话技能目录）

## 2. agate 编排者四项职责 × DSH 能力映射

| agate 编排者职责 | DSH 原生工具 | 适配度 | 说明 |
|------------------|--------------|--------|------|
| ① 读状态（active-tasks.md / .state.yaml / 阶段产出）| `read` / `glob` / `grep` + bash 跑 `agate-state-get.py` | 🟢 原生 | 不走 bash 卡死风险（AGENTS.md 工具纪律天然满足）|
| ② 派发 subagent | `subagent` / `subagent_fork`（后台默认）| 🟢 原生 | 等价 Claude Code `task` 工具；`dispatch-prompt.md` 模板可直接作 prompt |
| ③ 跑 gate（exit code 判定）| `bash`（返回 exit code 标记）| 🟢 原生 | `check-gate.py` 等 53 脚本零改动可跑；后台 job 机制适配长时 gate |
| ④ 更新状态（.state.yaml / active-tasks.md）| `write` / `edit` | 🟢 原生 | 状态落盘 + DSH `goal` 工具做跨轮恢复增强 |

**额外红利**（agate 在 Claude Code/OpenCode 上没有的）：
- `workflow` 工具 = 现成的**多批并行派发引擎**（TAG0017 的"5 批并行"在 DSH 里是脚本化的一行调用）
- `goal` 工具 = 编排者跨轮记忆，天然贴合"状态在文件里，不在记忆里"哲学
- `ralph` = fresh-agent 循环，可复用作 **judge 机制的宿主**（judge 需 fresh context）
- 后台 job + 通知 = 长 gate 不阻塞编排者

## 3. 三种集成路线

### 路线 A：agent-preset（身份层）+ skill（适配层）——对齐 agate 原生接入模型【修正版】

> 修正说明：agate 在 Claude Code/OpenCode 的接入本质是「把 orchestrator-template.md 注册成 **primary agent 身份**」（符号链接进平台 agent 目录，`mode: primary`），**不是**把协议当 skill 注入主 agent。DSH 的 faithful 对应是 **agent-preset**（`agent.cordis.yml` 的 `persona.text` = 模板内容，工具行 = 权限，会话级身份），skill 只承担「DSH 适配层」而非身份层。详见「一致性论证」。

- **身份层**：新建 agent-preset `agate-orchestrator`（仿 `apps/cli/config/agent-presets/standard/`），`persona.text` 填 orchestrator-template.md 的 DSH 适配版（四项职责 + 工具映射 + 阶段卡片加载指引），工具行开 bash/subagent/fs——等价 `ln -sf orchestrator-template.md .{claude,opencode}/agents/orchestrator.md`
- **适配层**：`agate-protocol/SKILL.md` 只做 DSH↔agate 工具映射（read/grep/subagent ↔ task/read/run）与平台注意（沙箱/审批/judge 用 ralph），协议本体 `~/.agate` 完全不动
- **优点**：与官方接入模型语义一致（身份=preset、协议=~/.agate、项目信息=project.md 全不变）；DSH 内可复用 Claude Code 的全部经验
- **待验证**：DSH 会话能否把 preset 设为默认身份（对应 Claude Code `settings.json` 的默认 agent），需实机确认

### 路线 B：Workflow 脚本自动化（最重，状态机脚本化）
用 DSH `workflow` 工具写 JS 脚本，把 P0-P8 状态机自动化：脚本读 `.state.yaml` → 按阶段 `agent(prompt)` 派发 → bash 跑 gate → 写状态 → 失败弹回重试。

- 实现要点：
  - 脚本骨架：`while (phase != READY) { const st = readState(); const cards = mapPhase(st.phase); ... }`（DSH workflow 为 worker 线程 JS，无 FS 权限——状态读写必须经 agent 或经 `phase()`/`log()` 钩子驱动的子 agent 完成，**这是关键约束，见风险 1**）
  - 派发：`agent(prompt, {schema})` 传路径；gate：子 agent 内 bash 跑 `check-gate.py` 并回传 exit code
  - 重试：`maxTotalAgents` 默认 1000，足够跑 retry 循环
- 优点：编排者上下文零污染、可复现、崩溃从状态文件恢复
- 缺点：workflow 无文件系统 API，状态机逻辑要么全塞进 agent prompt（退化回 A），要么在子 agent 里做（每次读全量状态，上下文开销大）

### 路线 C：Hybrid（推荐）
**A 的人格层 + C 的批量层**：
1. SKILL 定义 orchestrator 人格（读状态/派发/gate/更新的纪律与工具映射）
2. `workflow` 只用于**批量并行派发**（P3 红灯批、P4 实现批、P6 验收批——TAG0017 的 5 批并行模式），替代手写多路 subagent
3. gate 用 bash + `~/.agate` 稳定版（沿用双工作区纪律）
4. `goal` 工具承载"本任务目标"实现跨轮续跑

## 4. 扩展点清单（具体文件路径）

| 扩展点 | 路径 | 用途 |
|--------|------|------|
| agent-presets（注册 orchestrator agent）| `packages/preset/agent-presets/`；示例 `packages/subagent/subagent-in-process-driver/tests/fixtures/presets/{reviewing,coding}/agent.cordis.yml` | 把 agate orchestrator 声明为 DSH agent 组合 |
| skill 目录（SKILL.md + frontmatter）| `packages/skill/skill/`、`packages/skill/skill-filesystem/src/index.ts` | 打包 agate 协议为技能 |
| workflow 引擎 | `packages/workflow/` | 批量并行派发脚本 |
| 工具插件装配 | `packages/bundle/base/cordis.patch.yml` | 注册自定义 gate 插件行（profile 补丁 `$DSH_HOME/profiles/web/cordis.patch.yml`）|
| Session hooks（gate 自动化）| `packages/hooks/hooks-claude-code`（进程级 hooks.json）+ 强类型扩展点 `packages/core/agent/src/dispatch.ts`、`packages/core/agent-loop` | 在 PostToolUse/Stop 事件上自动跑 agate gate——比 git hook 更实时 |
| 外部 subagent provider | `packages/subagent/subagent-claude-code` / `subagent-codex` / `subagent-acp` | DSH 编排者可派发到 Claude Code/Codex 等外部 agent 当执行角色 |
| ACP 外部驱动 | `packages/acp/acp` + `examples/acp-agent/` | agate 编排者本身可被外部程序经 ACP 驱动（无人值守 CI 场景）|
| GUI 注入 | `packages/web/`（`window.__DSH_BOOT__`）、client 插件 `packages/extensions/cordis-*-runner` | 未来可视化 agate 状态机（阶段卡片、gate 结果面板）|

## 5. 环境适配注意（本会话实测）

1. **沙箱只读区**：`/home/kity/oclab/agate` 主 checkout 对 DSH 沙箱只读（workspace-write 只覆盖 `dsh-workspace`）——**gate 脚本若写仓库内文件会 Errno 30**。解法：agate 任务工作区放 `dsh-workspace` 下，或对 DSH 使用更高权限模式
2. **审批策略**：本会话 `approval` 被禁用 → 沙箱拒绝即终局，不可升级。集成时 gate 命令要设计成不触发需要审批的操作
3. **/tmp 只读**：pytest 等需要 `--basetemp` 指向可写目录（本会话已验证）
4. **bash 纪律**：DSH 环境有"bash 偶发挂起"经验，建议沿用 AGENTS.md 的 timeout 包裹 + read/grep 工具优先原则

## 6. 推荐落地路径

```
Phase 1（1-2 小时）：路线 A —— 写 agate-orchestrator SKILL.md，
   在 dsh-workspace 建一个演示任务跑通 P1→P3（需求→TDD 红灯）
Phase 2（半天）：路线 C 批量层 —— workflow 脚本化 P3/P4 并行派发，
   对照 TAG0017"5 批并行"产出对比
Phase 3（可选）：agent-preset 注册 orchestrator + goal 工具跨轮续跑长任务
Phase 4（远期）：GUI 面板显示 agate 状态机 / gate 结果（packages/web 插件）
```

## 7. 风险与对策

| 风险 | 对策 |
|------|------|
| workflow 无 FS API，状态机自动化受限 | 只自动化"并行派发层"，状态推进仍由 orchestrator（agent）按 skill 纪律执行——这正是 agate"主 Agent 只编排"哲学的本意 |
| 沙箱只读区误伤 gate | 任务工作区放 `dsh-workspace`；文档标注权限要求 |
| 双套纪律冲突（AGENTS.md 的 bash 纪律 vs DSH 工具习惯）| SKILL.md 显式写 DSH 工具映射表，避免 agent 用 bash 读文件 |
| 协议本体改动需 self-gate | 集成只改 DSH 侧（skill/preset），不动 agate 协议本体，不触发 SELF-GATE |

## 8. 与官方接入模型的一致性论证（为何 preset 而非仅 skill）

agate 在 Claude Code / OpenCode 的接入本质（`SETUP.md` 实证）：

```
ln -sf ~/.agate/orchestrator-template.md .{claude,opencode}/agents/orchestrator.md
```

- orchestrator-template.md 是 **`mode: primary` 的会话主 Agent 身份**（系统提示词 + 权限声明），不是"按需注入的说明文档"
- 项目特定信息**只**进 `{AGATE_WORKSPACE}/agents/project.md` + AGENTS.md/CLAUDE.md，模板本身零项目内容
- 阶段角色不预注册，派发用「方法 B」（通用 subagent + 角色文件路径）
- 协议本体 `~/.agate` 与身份模板**分离**，靠运行时路径解析

**DSH 的 faithful 映射**（三层分离，与官方同构）：

| agate 概念（Claude/OpenCode）| DSH 对应物 |
|------------------------------|-----------|
| orchestrator-template.md（primary agent 身份）| agent-preset 的 `persona.text` + 工具行（`packages/preset/agent-presets/`）|
| `.claude/agents/*.md` 符号链接注册 | `<dshHome>/.agent-presets/agate/` 安装 preset |
| `~/.agate` 协议本体（跨平台共享）| 完全不变，路径照旧 |
| `{AGATE_WORKSPACE}/agents/project.md` | 完全不变 |
| platform-notes.md（平台适配）| `agate-protocol/SKILL.md`（DSH 专属适配层）|
| git hooks（pre-commit 等）| 不变 + DSH session hooks（PostToolUse）增强 |

**结论**：Skill 是 DSH 的「打包/分发单元」（适合承载适配层与食谱），但**不是 orchestrator 身份的对应物**——身份对应物是 agent-preset。只做 skill 会得到"主 Agent 临时扮演编排者"的较弱语义（身份易随会话/压缩漂移、无"以 orchestrator 身份开会话"的入口）；preset+skill 才是与官方一致的效果。

## 8.5 DSH 能否鹤立鸡群（如实评估）

**能，但有边界。** 真实的结构性优势（另外两平台没有、且直击 agate 痛点）：

| DSH 机制 | agate 痛点 | 为什么是超集 |
|----------|-----------|-------------|
| `workflow` 工具（脚本化 fan-out）| 并行派发靠编排者手工多路 task | TAG0017 的"5 批并行"在 DSH 是一行 workflow；`agent/pipeline/parallel/phase` + 1000 agent 上限 |
| `ralph`（fresh-agent 循环）| 独立 judge 需手工保证 fresh context | ralph 每轮新 agent + bounded handoff = judge 原生宿主（LIMITATIONS-3 直接缓解）|
| `goal`（跨轮持久目标）| 状态落盘/崩溃恢复 | 自动续轮 + blocked 判定，把"状态在文件里"变成运行时能力 |
| session hooks（PostToolUse）| git hook 只拦 commit | 每步工具调用后实时 gate |
| 沙箱+审批 | gate 命令无执行边界 | gate 在受限环境跑，危险操作被拦 |
| 外部 provider（claude-code/codex/acp）| 平台锁定 | DSH 可当控制面，派发到真实 Claude Code/Codex 执行 |

**不能鹤立鸡群的地方（必须诚实）**：
1. **身份层**：preset 需先对齐，Claude Code 的"primary agent = 会话身份"是原生且成熟的
2. **成熟度**：agate 17 个真实任务全在 OpenCode/Claude Code 上 dogfood 过；DSH **零实绩**，必须先用一个真实任务证明
3. **文档/生态**：SETUP.md / platform-notes.md 未覆盖 DSH，需补文档

**准确表述**：DSH 不是全方位更强，而是在 agate 最痛的两处（并行编排、独立验证）**原生更强**；前提是先把身份层（preset）对齐到官方模型。

## 9. 与其他交付物的联动

- **改名**：SKILL 名建议直接用新品牌（如 `gatewise-orchestrator`），避免迁移期二次改名
- **独立 judge**：DSH 的 `subagent_fork`（继承上下文）与 `ralph`（fresh agent）恰好提供 judge 所需的两种上下文模式——judge 派发在 DSH 上零额外开发
- **结构化层**：DSH workflow 脚本可直接消费 `phases.yaml`（若有），路线 B 的自动化程度随结构化层落地而提升
