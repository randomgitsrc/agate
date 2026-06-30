# agate — 子 Agent 编排工作流

> 适用：OpenCode / Claude Code / Codex 等支持 subagent 的 Agent 平台
> 完整规则文档，从此文件开始阅读。
> 当前版本见 `git describe --tags` 或 README.md badge。
>
> 版本说明：规则新增/调整升 minor（v1.1.0），破坏性变更升 major（v2.0.0）

---

## agate 是什么

agate 是一套「主 Agent 编排、子 Agent 执行」的开发流程。主 Agent 不亲自写代码或文档，而是把每个阶段派发给独立上下文的 subagent，自己只做四件事：读状态、派发、验门槛、更新状态。任务状态全部落盘到文件，会话中断也能恢复。

agate 建立在两条主线上：

**编排主线（已被真实任务验证）**
- **P0 任务简报**：主 Agent 在派发任何 subagent 前亲自写 P0-brief.md，注入环境约束和风险判断
- 可执行的派发协议：用 task 工具派发 subagent，只传文件路径不传内容，门槛机器可判定，状态落盘
- 双层角色体系：执行角色（execution-roles）+ 评审角色（review-roles），收拢在 `assets/`
- 状态机落盘 + 可选的 /loop 自动编排

**需求与验收主线**
- **P1 需求基线**：先质疑需求、识别隐含依赖、用 BDD 写验收条件，建立一条"活的"需求基线
- **SCOPE+ 贯穿反馈**：任何阶段的 subagent 发现新的隐含需求，都能向上反馈、增补基线，而非憋着或擅自扩大
- **P6 验收**：把 BDD 条件逐条实际跑一遍，结果翻译成人能看懂的行为描述
- **NEED_CONFIRM 按需介入**：需求明确时 Agent 自走并始终产出可见文件；只有判断拿不准方向时才停下找人



---

## 目录结构

```
~/.agate/                        # 标准安装位置（软链接 → 仓库的 agate/ 子目录）
├── AGENTS.md                    # 协议本体入口指引（角色清单 + 升级/卸载）—— Agent 找路从这里开始
├── WORKFLOW.md                  # 本文件：主流程（入口）
├── dispatch-protocol.md         # 派发协议、gate 表、特殊事件处理
├── role-system.md               # 双层角色体系说明
├── loop-orchestration.md        # /loop 自动编排设计
├── state-machine.md             # 状态机落盘设计
├── git-integration.md           # git 持久化（多 agent 协作）
├── platform-notes.md            # 各平台适配说明
├── orchestrator-template.md     # 新项目接入模板
├── LIMITATIONS.md               # 已知局限（使用前建议先读）
└── assets/
    ├── review-roles/            # 评审角色库（从 gstack 提取）
    │   ├── review.md            # /review 偏执 Staff Engineer
    │   ├── plan-ceo-review.md   # /plan-ceo-review 创始人/CEO
    │   ├── plan-eng-review.md   # /plan-eng-review 工程经理
    │   ├── design-review.md     # /design-review 高级设计师+前端
    │   ├── plan-design-review.md
    │   ├── qa.md                # /qa QA 工程师
    │   ├── investigate.md       # /investigate 调试专家
    │   ├── office-hours.md      # /office-hours YC 合伙人
    │   └── cso.md               # /cso 安全官
    ├── execution-roles/         # 执行角色库
    │   ├── analyst.md           # P1 需求分析师（需求质疑 + BDD 基线 + 能力预检）
    │   ├── architect.md         # P2 方案设计师（设计 + P7 一致性检查）
    │   ├── test-designer.md     # P3 测试设计师（TDD + E2E）
    │   ├── implementer.md       # P4 实现工程师（实现 + P8 多包发布）
    │   ├── verifier.md          # P5 技术验证 / P6 验收（BDD 实跑）
    │   └── vision-analyst.md    # UI 视觉结构分析（被 P6 verifier 按需派发）
    └── templates/
        ├── active-tasks-template.md # active-tasks.md 看板模板
        ├── custom-role.md       # 自定义角色模板
        ├── dispatch-prompt.md   # 派发 prompt 模板
        └── task-files.md        # 各阶段产出文件模板
```

---

## 任务目录命名约定（重要）

任务目录名是 **`Txxx-描述`** 格式，不是纯编号。实际例子：
```
docs/tasks/T001-mcp-namespace-map/
docs/tasks/T002-fix-db-migration/
```

本文档及模板中的 `{Txxx}` / `{task_id}` 是占位简写，**实际拼路径时必须用完整目录名**（含描述后缀）。主 Agent 派发时，要先确认实际目录名（`ls docs/tasks/`），不要假设是纯 `T002`——按 `docs/tasks/T002/` 拼路径会找不到文件。

## 运行环境前提

**agate 的完整执行依赖两个能力：**

| 能力 | 说明 | 缺失时的影响 |
|------|------|------------|
| `task` 工具 | 派发独立上下文的 subagent | 无法编排，所有阶段由主 Agent 直接执行 |
| 本地开发环境 | 语言运行时、测试框架、浏览器 | gate 命令无法执行，P5/P6 无法验证 |

**已知适用环境：**

| 平台 | task 工具 | 本地环境 | agate 完整度 |
|------|----------|---------|---------|
| OpenCode | ✅ | ✅ | 完整 P0-P8 |
| Claude Code | ✅ | ✅ | 完整 P0-P8 |
| Codex | ✅ | ✅ | 完整 P0-P8 |
| Claude Project 会话 | ❌ | ❌（网络受限）| 仅 P0-P2 设计规划 |

**Claude Project 会话的定位：**
- 适合：P0-P2（设计决策、需求基线、方案评审）、代码审查、文档任务
- 不适合：P3-P6 技术验证、E2E 测试、发布准备
- 建议工作方式：用 Claude Project 完成 P0-P2 并 push 到 main，再切换到 OpenCode/Claude Code 执行 P3-P8

**执行环境在 P0-brief 的 `executor_env` 字段里声明**（见 task-files 模板），后续所有阶段的 gate 判定和 subagent 派发以此为依据。

---

## 适用边界（agate 不适合什么）

agate 的派发机制有固定开销——每次派发约需写 25 行派发 prompt。**只有当"被隔离的内容量" > "派发开销"时，走 agate 才划算。**

| 任务类型 | 建议 |
|----------|------|
| 微任务（typo、文案、单行配置、debug 后的精确修复）| 直接做，不走 agate |
| 小任务（明确的 bug 修复、加一个字段）| 裁剪流程：P1 + P3 + P4 + P5（+ P6 若有 BDD 验收条件），跳过 P2/P7；P3 仅在满足可跳条件时才跳 |
| 中任务（新功能）| 完整 P1-P8 |
| 中任务（Claude Project 会话）| P0-P2 设计 + 交接给 OpenCode/Claude Code 执行 P3-P8 |
| 大任务（跨模块重构）| P1 拆成多个子任务，各自走 P1-P8 |

### 可裁剪的阶段

- **核心阶段（不可跳）**：P1 需求基线、P4 实现、P5 技术验证
- **可选阶段（按需加）**：P7 一致性（多文件改动时）
- **P2 设计+评审默认保留，方案明确时才可跳过**：
  可跳过的情形：改动是纯实现层（修一个已知 bug、改一行配置），方案无需设计，P1 已足够清晰
  「方案不明确」是**必须走 P2** 的信号，不是可选的条件——方案不明确就进 P4，实现什么都不知道
- **P3 TDD 测试先行默认保留**：P3 不是「需要 TDD 时才加」，默认保留，有明确理由才跳过。
  可跳过的情形只有两种：
  ① 纯文档/配置类任务——没有可测试的行为（如更新 README、调整配置文件）
  ② 极小改动（≤3 行）且 P1 能明确指出哪条现有回归测试已覆盖该改动
  跳过 P3 须在 P1 裁剪说明里写明理由，由主 Agent 确认（「任务简单」不是合法理由）
  **单 Agent 模式**（`has_task_tool: false`）：P3 和 P4 由同一 Agent 执行，独立视角消失。
  此时 P3 的价值从「独立验证」变为「提前定义行为契约」——先写测试让自己明确"完成标准"，
  而不是边实现边定义。须在 P1 裁剪说明里声明 `single_agent_mode: true`。
- **P6 验收默认保留**：P6 是质量保障的最后防线，默认不裁剪。仅微任务（直接做不走 agate）可免于 P6；小任务裁剪 P6 必须在 P1 裁剪说明里写明充分理由，并由主 Agent 独立判断是否接受
- P8 发布准备：涉及发布的任务必做
- **裁剪必须附理由**：P1 分析师判定复杂度后，在 `P1-requirements.md` 的「裁剪说明」节写明每个跳过阶段的理由；主 Agent 按声明推进，不强制全 8 阶段
- **裁剪不等于跳过需求质疑**：无论任务大小，P1 的需求基线（哪怕一句话）都要建立，因为隐含需求的识别不依赖任务规模

### 裁剪风险维度（T005/T006 教训）

**裁剪决策必须同时考虑「复杂度」和「风险程度」。** 以下情况，无论任务看起来多简单，对应阶段均不可跳过：

**基本原则：开发全程在测试环境进行，生产环境不在 agate 编排范围内。**
生产部署属于 `make publish` 之后的运维范畴，不属于 P1-P8 流程。

| 风险特征 | 不可跳过的阶段 | 原因 |
|---------|--------------|------|
| 涉及数据 schema 变更或迁移（测试环境）| P6 验收 | 迁移逻辑需要完整验收，schema 问题在测试环境就要发现 |
| 涉及数据删除操作 | P6 验收 + `[NEED_CONFIRM]` 硬中断 | 即使在测试环境，批量删除也需人工确认范围 |
| 涉及安全相关改动（权限、认证、加密）| P6 + P7 | 安全改动的行为验收和一致性检查缺一不可 |
| 涉及 ≥2 个改动端（如 API + CLI + 客户端）| P6 + P7 | 多端联动行为需要整体验收 |
| 主 Agent 对任务范围有不确定感 | 默认走完整 P1-P8 | 不确定时保守是对的 |

**裁剪的最终拍板权在主 Agent，不是 P1 analyst。**
P1 analyst 可以建议裁剪，但主 Agent 必须结合 P0-brief.md 里声明的已知风险做独立判断，不能直接接受 P1 的裁剪建议。

### 风险矩阵（P2.13）

任务分类应该是"复杂度 × 风险"的矩阵，不是只看复杂度：

| | 低风险 | 高风险（安全/数据/权限）|
|---|--------|----------------------|
| 微改动 | 直接做 | 精简 agate：P1 + P4 + P5 |
| 小改动 | 裁剪 agate：P1 + P3 + P4 + P5 | 完整 agate（至少到 P6）|
| 中改动 | 完整 P1-P8 | 完整 P1-P8 + P6 不可裁剪 |

"直接做"的最低要求（P2.14）：commit message 必须声明改了什么 + 为什么安全。

### 测试/调试环境隔离原则（项目级责任）

agate 要求开发全程在测试环境进行，但「如何保证隔离」是项目的责任，不是 agate 硬编码的。每个项目应实现：

- **强制隔离**：测试运行时自动将存储路径重定向到临时目录，不依赖开发者手动配置（最强保障）
- **调试模式自动隔离**：启动调试环境的命令（如 `make debug` 或 `npm run dev:test`）自动使用独立的数据目录
- **启动前状态检查**：调试/测试启动脚本应检查生产数据是否存在异常（如近期记录数突变、含测试特征的数据），异常时阻止启动并警告
- **不依赖文档规则**：文档说明是最弱的隔离保障，上述三条才是真正可靠的机制

agate 在 P0-brief 的 `env_constraints.debug_env` 字段里要求写明测试环境命令，是项目实现上述隔离机制的约定读取点。
P5 gate 要求「测试环境隔离正常（无 [PROD_TOUCHED]）」，是流程层面的验证触发点。
具体隔离机制由项目自行实现，agate 不硬编码路径或检查方式。

---

## P1-P8 阶段总览

| 阶段 | 名称 | 执行角色 | 评审角色 | 门槛（进入下一阶段的条件）|
|------|------|----------|----------|--------------------------|
| P0 | 任务简报 | **主 Agent 亲自写**（非 subagent）| — | P0-brief.md 完成，含 debug_env + known_risks + pruning_tendency |
| P1 | 需求基线 | analyst（需求质疑模式）| office-hours（任务属于"适用边界"表的"大任务（跨模块重构）"档，或 P1-requirements.md 的裁剪说明里 pruning_tendency 标"保守"时追加；判断结果写入 P1-requirements.md）| P1-requirements.md 存在，含 BDD 验收条件；`grep -cE '\[NEED_CONFIRM\]'` → =0；无 `status: GAP`（supplementable 不阻塞） |
| P2 | 方案设计 | architect | plan-eng-review（risk_level=high 时必须派发独立 subagent，hook 对 agent=main 输出 WARNING）/ plan-design-review（domains 含 frontend 时追加）/ plan-ceo-review（涉及商业模式判断时可选）| P2-review.md 的 status == approved；`grep -cE '^(packages|domains|ui_affected|gate_commands):' P2-design.md` → =4 |
| P3 | 测试设计 | test-designer | gate 自检（TDD 红灯）| `scripts/check-tdd-red.sh` exit 0 |
| P4 | 代码实现 | implementer | review（改动跨 ≥3 个文件或涉及核心数据结构）/ cso（涉及认证、权限、密钥、用户输入处理、外部网络请求任一项）/ design-review（domains 含 frontend）；命中任一条件才派发，判断结果写入 .state.yaml | `git log --oneline -1` 含 P4 commit |
| P5 | 技术验证 | verifier | gate 自检（从 P2 gate_commands.P5 读取命令）| P2 `gate_commands.P5` 命令 exit 0 AND failed==0；`grep -rl '\[PROD_TOUCHED\]'` → 无命中 |
| P6 | 验收 | verifier（验收模式）| — | `scripts/check-gate.sh P6` exit 2（FAIL=0/NC=0/证据非空）；`scripts/check-p6-provenance.sh` exit 0 或 exit 2（证据-结论对应 + dispatch-context 审计 + BDD 总数对照）；主 Agent 手动核实 BDD 总数 = P1 BDD 总数（provenance exit 2 时必做）；UI 条件须 vision-analyst YAML `summary.blocker_count==0` ⚠️ self-authored（降级缓解：provenance 审计，根治待 Phase 3） |
| P7 | 一致性检查 | architect | gate 自检（grep BLOCKER + DEVIATION-CRITICAL）| `grep -cE '\[BLOCKER\]' P7-consistency.md` → =0；`grep -cE '\[DEVIATION-CRITICAL\]'` → =0 ⚠️ self-authored |
| P8 | 发布准备 | implementer | gate 自检（发布检查命令）| `scripts/check-gate.sh P8` 脚本化部分通过（exit 2）；P2 `gate_commands` 逐包 exit 0；bump 后重跑 P5 `gate_commands.P5` exit 0；`git log v{prev_version}..HEAD --oneline` 对照 CHANGELOG 无遗漏；P2 `packages` 验证 version 文件路径；`grep -q 'bump_type:' P8-release.md` 命中；`git diff HEAD~1 --stat` 含 version 变更；`git diff HEAD~1 -- ${CHANGELOG_FILE:-CHANGELOG.md}` 非空 |
| READY | 待发布 | — | — | 人手动 `make publish` → DONE |

**P1 与 P6 的关系**：P1 用 BDD（Given/When/Then）写下"做完之后应该表现成什么样"，P6 把这些条件逐条实际跑一遍、把结果翻译成人能看懂的行为描述。P1 是"约定"，P6 是"兑现验证"。

**P6 vs P7 的区别**：P6 验收是"行为对不对"（用户视角，BDD 条件是否满足）；P7 一致性是"实现和设计一致不一致"（技术视角，代码是否偏离 P2）。两者关注点不同，不可互相替代。

详细派发方式见 `dispatch-protocol.md`，角色定义见 `assets/`。

---

## Pre-commit 检查总览（hardening-roadmap Phase 1-2 已落地）

每次 `git commit` 触发 pre-commit hook，按以下顺序自动运行（任何 `exit 1` 中止 commit，`exit 2` 警告不阻塞）：

| # | 检查脚本 | 触发条件 | 阶段/机制 | 行为 |
|---|---------|---------|-----------|------|
| 0 | `check-state-yaml.sh` | `.state.yaml` 暂存变更时（不依赖 phase 变）| 文件级 | 校验格式合法（必填字段、phase 取值、retries 结构）|
| 1 | `check-gate.sh` | `.state.yaml` phase 变更或阶段产出文件变更 | 阶段级 | P1.1 gate 校验 |
| 1.6 | `check-changelog.sh` | gate 通过后 | 文件级 | `[Unreleased]` 含本次 task_id（P1.6）|
| 1.7 | `check-p6-evidence.sh` | 阶段 ∈ {P6, P7} | 阶段级 | P6-evidence/ 非空 + BDD 行数 ≥ 1（P1.7）|
| 2.1 | `check-p6-provenance.sh` | gate 通过后 | 阶段级 | 三道客观审计（证据-结论对应 + dispatch-context 内容约束 + BDD 总数对照）+ agent 字段协作规范；exit 1 硬拦截，exit 2 WARNING（P2.1/P2.10 v2 降级方案）|
| 2.3 | `check-state-transition.sh` | gate 通过后 | 阶段级 | 状态转移合法性 + 重试上限（P2.3-P2.5）|
| 2.7 | `check-pruning.sh` | gate 通过后 | 阶段级 | 裁剪条件与实际执行一致性 + override 校验（P2.7-P2.9）|
| 2.11 | `check-scope-resolved.sh` | gate 通过后 | 阶段级 | `[SCOPE+]` 必须有 `[SCOPE_RESOLVED:...]` 标记（P2.11）|
| 2.12 | `check-retrospective.sh` | gate 任何结果 | 阶段级 | 异常模式提醒（重试超限/SCOPE+/override）→ 写复盘；不阻塞 commit（P2.12）|

**关键设计原则**：

- **0→1→1.6→1.7→2.* 顺序**：每个阶段有"关卡"——0 是格式关、1 是行为关、2.* 是合规/审计关。任何关卡失败 → 中止 commit。
- **agent 字段协作规范（P2.1/P2.10 v2 协作层）**：所有阶段产出文件 Header 含 `agent: <角色>`，缺字段 WARNING 不阻塞（向后兼容），但 `risk_level=high` 时 `agent=main`（自审）WARNING。
- **CI backstop（P1.3）**：push 后 GitHub Actions 重跑 `check-gate.sh` + `ci-gate-backstop.py`，捕获 `--no-verify` 绕过 hook 的恶意提交；git blame 单 author WARNING 作为 provenance 兜底审计。
- **降级方案**（Phase 3 平台接口未实现前的最优方案）：证据-结论对应是**客观行为审计**——伪造 N 个证据文件的成本远高于填写一行 `agent: verifier` 自报字段。详见 `LIMITATIONS.md` 局限 3。

---

## 核心原则

### 原则 1：主 Agent 只编排，不执行

主 Agent 的职责严格限定为四件事：
1. 读状态（active-tasks.md + 当前阶段文件）
2. 派发 subagent（用 task 工具，见 dispatch-protocol.md）
3. 检查门槛（可判定条件）
4. 更新状态

**主 Agent 永远不自己写阶段产出（P1-requirements.md、P2-design.md、代码……）。** 这些都由 subagent 在独立上下文里产出。

**主 Agent 的合法职责（非降级）：**
- 写 P0-brief.md（PM 视角的任务简报，五字段自查）
- 派发前查证客观信息（环境状态、URL、选择器等），落盘成 `P{N}-dispatch-context.md`（信息量 >10 行或同阶段复用时）
- P8 gate 通过后执行 READY 收尾检查（停止调试服务、清理临时数据、还原开发环境、确认生产无残留——见 state-machine.md）
- PAUSED 时写 `PAUSED-resolution.md` 记录人工决策

**降级的硬边界**：降级（主 Agent 亲自执行阶段产出）只在 `has_task_tool: false` 或 `has_local_runtime: false` 时发生。**subagent 执行失败 ≠ 降级信号**——失败时走 retry/PAUSED，不允许"subagent 做不好"为由降级。

### 原则 2：上下文隔离 = 只传路径

派发 subagent 时，prompt 里只写**文件路径**，不塞文件内容。subagent 在自己的上下文窗口里读文件、干活，主 Agent 的上下文只增加"路径 + 一句话摘要"。

这是解决上下文爆炸的核心机制。

### 原则 3：状态在文件里，不在记忆里

任务的当前状态（在哪个阶段、哪些门槛过了）落盘到 `docs/tasks/Txxx/` 和 active-tasks.md。即使会话被压缩、中断、重启，主 Agent 重新读文件就能接着干。

**状态落盘必须配合 git 持久化**（见 git-integration.md）：每阶段门槛通过后主 Agent commit 一次，让状态真正持久、可恢复、可多 agent 共享。只写本地文件不 commit，崩溃就丢。

### 原则 4：门槛必须机器可判定

进入下一阶段的条件必须是文件里可读取的明确值（status==approved、failed==0），不能是"方案足够好"这类模糊判断。

### 原则 5：重试有上限

门槛不通过时打回重做，但有次数上限（按阶段 2-3 次，见 state-machine.md 重试上限表）。超限则停下来报告人工介入，避免无限循环。

---

## 需求与验收机制（agate 核心）

agate 在编排之上加了一层"做对的事并持续校准"。三个机制贯穿全流程。

### 需求基线：活的、向前累加

P1 不是把需求一次性定死，而是建立一条**基线**：质疑原始需求、识别隐含依赖、用 BDD 写出验收条件。这条基线是"活的"——后续任何阶段都能向它增补，它永远是最新最全的需求真相源（写在 `P1-requirements.md`，后续增补也回写到这里）。

BDD 验收条件用 Given/When/Then 描述行为，例如：

```
Given 用户创建 entry 不指定过期时间
When  查询该 entry
Then  过期时间是创建时刻起 15 天后
```

写不出 BDD 条件，说明需求本身还不清楚——这本身就是需要 `[NEED_CONFIRM]` 的信号。

### [SCOPE+]：任何阶段都能向上反馈新需求

P1 不可能预见所有隐含需求。P2 设计、P4 实现时，subagent 常会发现"前序阶段没覆盖、但技术上必须做"的事。这时 subagent 在产出文件中标注：

```
[SCOPE+] 发现：createEntry 和 publishFiles 的 expires 参数类型不一致
         必须做的理由：不统一会导致 MCP 两个工具行为分叉
         影响：P1 基线需新增一条 BDD；涉及 packages: [pkg-b]
```

主 Agent 看到 `[SCOPE+]` → 把它翻译成 BDD 形式 → 增补进 P1 基线（标记 `[SCOPE+ from Pn]`）→ 按"定向回补"决定哪些已完成阶段需要局部更新。

**与 `[SCOPE_GAP]` 的区别**：`[SCOPE+]` 是"发现了所有人都没想到的新需求"（向上涨）；`[SCOPE_GAP]` 是"主 Agent 的 prompt 漏了 P2 已声明的东西"（向下漏，见 dispatch-protocol.md）。

### 定向回补：不全重跑，只补受影响的部分

`[SCOPE+]` 触发后，**不是回到 P1 重走一遍**，而是：

1. **基线增补**：新需求写进 P1-requirements.md（唯一真相源，永远最新）
2. **判断影响范围**：主 Agent 对照新需求，看已完成的阶段里哪些产出需要跟着改
3. **定向局部回补**：受影响的阶段**增量更新**对应文件，未受影响的阶段和未来阶段自然消费最新基线

回补深度由"这条新需求实际需要哪些阶段"决定，不机械从 P1 重来。回补的转移规则见 `state-machine.md`。

### [NEED_CONFIRM]：默认自走，拿不准才找人

需求明确时，Agent 自走，**但每个阶段的产出文件始终生成**（人随时可看）。只有当 subagent 或主 Agent 判断"拿不准方向"时，才标注 `[NEED_CONFIRM]` 停下问人。

触发 `[NEED_CONFIRM]` 的条件（写进角色定义，不靠临场感觉）：
- 原始需求有多种合理理解，选哪种会显著影响结果
- `[SCOPE+]` 的新需求改动较大、伤及已确认内容
- 隐含需求涉及业务方向决策（"这个功能到底要不要做"）
- 安全、数据迁移、外部资源等不可逆或高风险操作

**人确认的是"行为/方向对不对"（能判断），不是"代码/技术对不对"（Agent 负责）。** BDD 条件由 Agent 起草，人只做加/删/改。条件写漏是 Agent 的责任，不是确认人的责任。

---

## 三种使用方式

### 方式 A：手动逐阶段（最稳）

人工逐个触发每个阶段的派发。主 Agent 派发一个 subagent，检查门槛，等人确认后派发下一个。适合关键任务、需要人工把关的场景。

### 方式 B：半自动（推荐）

主 Agent 连续派发，每过一个门槛自动推进，只在门槛失败或重试超限时停下来问人。详见 `loop-orchestration.md`。

### 方式 C：全自动 /loop（增强）

主 Agent 自动跑完 P1-P8，全程不需人工介入，只在最终发布前汇报。仅在方式 B 稳定后启用。详见 `loop-orchestration.md`。

---

## 平台适配

不同 Agent 平台的 subagent 机制不同，派发协议的具体调用方式见 `dispatch-protocol.md` 的平台适配章节。已覆盖：

- **OpenCode**：`task` 工具派发。**经 validation-report 验证：自定义 subagent（方法 A）因 issue #29616 不可用，统一用 general subagent + prompt 注入角色文件（方法 B）**。custom-role.md 模板走方法 B 路径。
- **Claude Code**：Agent Teams（2026-02 起）+ Task 工具
- **Codex**：spawn_agent / wait / close_agent 工具套件

---

*主流程文档，详细机制见同目录其他文件*
