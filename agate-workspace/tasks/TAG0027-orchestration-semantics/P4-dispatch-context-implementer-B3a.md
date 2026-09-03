---
phase: P4
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0027
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

**P4 批次 B3a（docs-clean）实现**：按 P2-design.md §3.8 存量清理面 + P1 D-2 表 + A3 定案①，
清理/挂注记协议文档平台名污染，使后续 B3b 的 CHECK 14 上线首跑 = 0 命中。**本批只改文档不
改脚本**——清理面 = 顶层 `agate/*.md` 语义叙述文档（**排除 loop-orchestration.md**——归 B1 已
改）+ `agate/assets/` 两文件命中段挂注记（execution-roles/architect.md / templates/custom-role.md）。

### 约束

1. **B3a 范围（P2 §8 + §3.8 存量面）**：给平台名命中段挂「实现注记」标记或清理语义表述。
   **assets/templates/dsh/ 平台食谱目录不在此批**（结构豁免，A3 定案①）。**不越批**：
   phases.yaml/schema（B1）、渲染注入（B2）、S-1/S-2 加列 + CHECK 14/15 脚本（B3b）、
   loop-orchestration.md（B1 独占）。
2. **处理方式（三分类，P1 D-2 表 + P2 §6③）**：
   - **语义定义面**（协议语义小节含平台名作语义陈述）→ 改写去平台化 or 标注平台适配属实现
     注记；不可让平台名出现在"语义定义"表述中
   - **实现注记面**（平台适配说明/坑位/升级记录）→ 段落挂 `> 实现注记：` 标记行（统一格式，
     段首任一行含即可豁免 CHECK 14）
   - **元信息面**（WORKFLOW.md「已知适用环境」表 141-148 + 文档适用平台声明 5/168 行等）→
     **整表/整文件豁免区**（CHECK 14 实现侧处理，文档不需改）或按现有结构保留
3. **具体清理清单（platform-name 命中实证，P2-progress + 主 Agent 复核 2026-09-02）**：
   - `agate/adr.md`：ADR-008（233/248 行 OpenCode/Claude Code 接入细节）——决策叙事记录当时
     平台语境 → 段挂 `> 实现注记：`（P2 §6④ 定案：不做协议区整文件豁免）
   - `agate/AGENTS.md:30`：入口表"不同平台适配 → platform-notes.md"指针——元信息指针，指向
     平台适配权威源 → 表格行豁免或挂注记（判断：平台名出现在"指向 platform-notes"的指针行，
     属元信息导航——CHECK 14 豁免结构含平台适配权威源指针语义？P3 测试 test_tag0027_b3a_*
     会锁定判定口径，按测试期望实现）
   - `agate/dispatch-protocol.md`：铁律 1（17/19 行 "task 工具"作派发动词宾语——**数据面禁词
     语义延伸**，改"subagent"或注明 task 是平台工具实现注记）；166/179 行（单 Agent 模式 =
     平台适配实现注记）；1108 行（OpenCode 坑位 = 实现注记）；261 行（task 工具引用 = 上下文
     已注）
   - `agate/role-system.md`：138/141/146/178 行（OpenCode 自定义角色 = 平台适配实现注记）
   - `agate/UPGRADING.md`：303-311（DSH 平台支持版本条目 = 升级说明元信息，挂注记或按升级
     记录语义豁免——判断后处理）
   - `agate/WORKFLOW.md`：5/138/143-146/153/155/168 行（平台适用声明/已知适用环境表/建议工作
     方式——已知适用环境表 141-148 = 整表豁免区；其余 = 元信息或挂注记）
   - `agate/dispatch-protocol.md:164`「执行模式」表（语义依赖平台但无直接平台名，P1 待复核项）
   - `agate/assets/execution-roles/architect.md:229` + `agate/assets/templates/custom-role.md:
     45-60`（平台适配说明段 → 挂 `> 实现注记：`）
4. **P3 测试锁定判定口径**：`agate/tests/unit/test_tag0027_b3a_platform_name_docs.py`（5 用例）
   是本批 TDD 目标——测试断言了各文件的期望处理方式（豁免/注记/清理），按测试期望实现文档
   改动，**不得改测试**。先读测试理解每文件期望，再改文档。
5. **CHECK 14 未上线**（B3b 才加）——本批靠测试 + 人工核对保证清理完备；B3b 上线后 CHECK 14
   首跑 0 命中（§7 完成标志）。
6. **SELF-GATE**：改 agate/*.md → commit 时须 self-gate 标注（主 Agent commit 处理，implementer
   不 commit）。
7. **文档风格**：`> 实现注记：` 标记行统一格式（设计 v3b §4.3）；改动最小化——只挂注记/改
   必要表述，不改文档结构与其他内容。

### 上游关联

- P2-design.md（§3.8 存量清理面 + §6③ 三面并陈 + §8 B3a 批边界）
- P1-requirements.md D-2 表（9 文件三分类判定：role-system 语义段/UPGRADING 元信息/platform-notes
  + SETUP 豁免/adr 决策叙事/dispatch-protocol 坑位 = 实现注记/loop 前提 = 实现注记/WORKFLOW 元信息）
- P2-progress.md（平台名命中行号实证：adr 233/248、AGENTS 30、dispatch-protocol 17/19/166/179/
  1108、role-system 138/141/146/178、UPGRADING 303-311、WORKFLOW 5/138/141-148/143-146/153/155/
  168、loop 202）
- P3-test-cases.md + test_tag0027_b3a_platform_name_docs.py（5 用例 = 本批 TDD 目标）

### 输入文件（按顺序读）

1. `agate/tests/unit/test_tag0027_b3a_platform_name_docs.py`（5 用例——**本批 TDD 目标**，先读
   理解每文件期望判定）
2. `agate-workspace/tasks/TAG0027-orchestration-semantics/P2-design.md`（§3.8 + §6③）
3. `agate-workspace/tasks/TAG0027-orchestration-semantics/P1-requirements.md`（D-2 表）
4. `agate/adr.md` / `agate/AGENTS.md` / `agate/dispatch-protocol.md` / `agate/role-system.md` /
   `agate/UPGRADING.md` / `agate/WORKFLOW.md`（清理对象——命中段上下文）
5. `agate/assets/execution-roles/architect.md` / `agate/assets/templates/custom-role.md`
   （命中段挂注记）
6. `agate/platform-notes.md`（平台适配权威源参照——豁免文件，看实现注记格式样板，按需）
7. `AGENTS.md`（项目约定）

> ⚠️ 读 worktree 自己的 `agate/`。**不 commit**（主 Agent 统一 commit）。只改上述文档文件，
> 不碰任何 scripts/*.py / rules/*.yaml / tests（测试只读）。

### 产出文件字段

- 文档改动 = worktree `agate/` 下文件（本批清单）。改动记录追加 P4-progress.md。
</dispatch_guide>

<!-- AGATE_CARD_START -->
## 当前阶段卡片：P4

路径：phase-cards/P4-implementation.md
---
# P4 — 代码实现

> 当前状态：[首次 / 重试 #N / 裁剪跳阶]
> 裁剪跳阶 → 确认 P1 phases 不含 P4 且有合规理由（check-pruning.py 已检查）→ 跳过，读 P5 卡片

## 如果是首次进入本阶段

0. 跑 `agate-capture-env-baseline.py $TASK_DIR`（自动捕获环境基线）。
   该步骤不会阻塞流程——任何 stderr 输出（含 WARNING）均可忽略，直接继续步骤 1，
   无需查看结果、无需判断、无需因为看到 WARNING 而停下来处理。
1. 派发 implementer subagent → 产出代码文件
   1.1 写 P4-dispatch-context-implementer.md（派发指引：目标/约束/上游关联/输入文件 + 客观查证信息）
2. 按 P2 的 gate_commands 跑单元测试（非 gate，只是自查）
3. 按 C8 映射表派发评审（见下方）
4. 预跑 check-gate.py P4（确认暂存区有代码文件）
5. git add {AGATE_WORKSPACE}/tasks/{Txxx}/ + 代码文件（含 .state.yaml，若 .gitignore 忽略需 git add -f）
   ⚠️ 此时 .state.yaml 的 phase 保持 P4，不要提前写 P5——phase = 本 commit 的产出阶段
6. git commit -m "wf({Txxx}-P4): {摘要}"（phase=P4，P4 产出含 P4-implementation.md + 代码文件）
7. P4 commit 完成后进入 P5：**phase 推进 P5 随 P5 产出 commit 一起**（P5-test-results/ 就绪后），不是单独 phase commit

## 如果是重试

确认上一轮失败原因（来自 gate 输出 / review rejected 理由）
→ 只修复失败项，不重做已通过的部分
→ 修复后重跑全量测试（T027 教训：修复可能引入回归）
→ 读 agate/rules/state-transitions.md 确认 retry 上限（P4 MAX=3）

**若这次是从 P6（或其他更后的阶段）退回来的**：`{AGATE_WORKSPACE}/tasks/{Txxx}/` 下不会再有旧的 P6-acceptance.md（已被归档），但当初具体是哪条 BDD 失败、失败原因是什么，会摘要在 `{AGATE_WORKSPACE}/tasks/{Txxx}/.retreat-history.md` 里——**重新派发 implementer 时，dispatch-context 必须引用这份摘要**，不能让 implementer 只看到"现有代码"却不知道具体要修哪里。已有代码不会被撤销、也不需要重新实现，是在已有实现基础上定向修复。**回退落地后必须建 DEBT 条目**（`source: retreat`，`evidence` 引用 retreat 提交哈希，模板 `assets/templates/tech-debt-template.md`——TAG0001 强制，见 `agate/rules/state-transitions.md` 回退规则节）。

## 前置条件

- [ ] P2-design.md 存在且 files_to_read 字段完整（导航清单）
- [ ] P2-review.md status: approved（P2 不可裁剪）
- [ ] P3-test-cases.md 存在（测试已设计）
- [ ] check-tdd-red.py 确认红灯（测试先于实现）
- [ ] 未跳过 P4（如有裁剪理由，见上方裁剪跳阶）

## 派发

- **角色**：implementer（`{agate_root}/assets/execution-roles/implementer.md`）
- **输入**：P2-design.md（files_to_read 导航 + gate_commands）+ P3-test-cases.md + P0-brief.md（env_constraints）
- **输出**：代码文件（在 P4-implementation.md 声明的 implementation_dir 下）
- **派发 prompt 模板**：`{agate_root}/assets/templates/dispatch-prompt.md` + 以下阶段特定追加：

```
## 上下文控制
读取代码文件以 P2-design.md 的 files_to_read 清单为准，按需读取（标了行号范围的只读片段）。
不要在项目里盲目搜索或整目录全读。

## 自查≠gate
写完代码后应自跑测试确认基本功能（自查），但自查通过 ≠ P5 gate 通过。
P5 由主 Agent 派发 verifier subagent 执行 gate_commands.P5，主 Agent 验 gate（检查产出 + failed 计数 + N5 最小校验）。
不要在返回中声称"P5 已过"或"全部测试通过"——只返回路径 + 摘要。
UI/前端等需构建任务：单元测试全绿不代表可用，implementer 在 P4 完成后应构建并确认 dist 等构建产物存在，不能只跑单元测试就认为完成。

## 生产环境隔离
任何写入生产环境/生产数据库/生产 API 的操作都必须先 PAUSED 报告人工。
```

## 产出规格

- P4-implementation.md 必须声明 `implementation_dir: {实际路径}`
- 代码文件在声明的目录下
- 遵守 P2-design.md 的方案设计 + 现有项目代码规范

## 新增文件核对表

> 仅当项目已采用骨架（`P2-skeleton.md` 存在）或 CODE-MAP（`{AGATE_WORKSPACE}/agents/CODE-MAP.md`
> 存在）机制时填写；未采用则本节可省略。

implementer 为本阶段**每个新增文件**填一行：

| 新增文件路径 | 骨架归属 | CODE-MAP 处理 |
|------------|---------|--------------|
| {path} | `within <dir>` / `[SKELETON_DEVIATION: 理由]` | `[CODE_MAP_UPDATED]` / `[CODE_MAP_EXEMPT: 理由]` |

- **骨架归属列**：新增文件落在骨架声明的目录内 → `within <dir>`；落在骨架外 → 标
  `[SKELETON_DEVIATION: 理由]`（不阻断，供 P7 核对）
- **CODE-MAP 处理列**：新增文件已同步更新 `agents/CODE-MAP.md` → `[CODE_MAP_UPDATED]`；判断
  该文件不需要更新 CODE-MAP（如临时/测试脚手架）→ `[CODE_MAP_EXEMPT: 理由]`

`change_type: refactor` 同样适用本表（不因换用回归口径而豁免）。

## 评审派发（C8 机械映射）

**在 P4 实现完成后、gate 前**，按 P1 声明的 domains 和 risk_level 派评审。C8 映射表是机械规则，不靠判断"需不需要"：

| domain | 派哪些评审 | 产出 |
|--------|----------|------|
| backend | review | P4-review.md |
| frontend | design-review | P4-review.md |
| mcp | review（关注 MCP 接口契约）| P4-review.md |
| security | cso | P4-review.md |
| risk=high | P4 实现评审（按 domains 派 review/design-review/cso；P2 plan-eng-review 已审方案，P4 实现评审不可省）| P4-review.md |
| full（tier=full 或声明 ceremony: full）| P4 实现评审（按 domains 派 review/design-review/cso，同 risk=high 不可省；P2 plan-eng-review 已审方案）+ cso（security 域）+ P7 不可裁（full 档任务 P7 为强制阶段）| P4-review.md |

多个评审角色 `专家组并行` → 所有返回后派组长汇总 → 统一 P4-review.md（status: approved / rejected）。
详见 `agate/rules/review-mapping.md`。

**并行派发**（多个评审角色时）：
1. 同时派发所有触发的评审 subagent（每个一个 task 调用）
   > **操作方式**：在一个 assistant 消息中连续发起多个 task 工具调用（每个评审角色一个）。
   > 不要等前一个 task 返回再发下一个——那是串行，不是并行。
   > 平台会并行执行多个 task，全部返回后再进入下一步（派发组长汇总）。
2. 每个评审 subagent 各写一个 dispatch-context + 各自产出文件
3. 所有评审返回后，派发组长汇总 subagent（角色：review + 指定为「专家组组长」）
4. 组长产出：P4-review.md。**agent 字段必须非 main**（与 P2 评审同规则，check-gate.py 在 P2 分支硬拦截 agent=main 的 approved）
5. 组长规则：不发表新意见，只汇总；任何 BLOCKER → rejected；分歧 → 交人工；全票无 BLOCKER → approved

**单评审角色时**：直接派发，无需组长汇总，产出直接写 P4-review.md。

**评审 checklist（RM-AG0046）**：`agate/scripts/check-maintainability.py` 检出 violations 非空时，评审角色 approve 前必须读过任务目录 `known-violations.md` 的登记理由——"是否接受该反模式"的判断权在评审角色，登记与数量对齐不单独构成放行依据。

review 不通过 → implementer 修改代码 → 再 review → … → approved（⑩迭代循环，review 和 gate 重试共享 retry 预算）

## 按包拆分并行（条件触发，需额外约束）

> 仅当 P2 packages > 1 且包间无依赖时适用。单包任务跳过本节。
> 并行上限 / 失败批 retry / 共享文件统一后处理见 dispatch-protocol「派发编排机制」并行规则。

当 P2 声明多个 packages 且包间无数据依赖时，P4 可拆分并行，但**有额外约束**：

1. 每个 package 派一个 implementer subagent
2. **各 implementer 只改自己 package 目录下的文件**——跨包的共享文件（类型定义、接口、配置）由主 Agent 在所有并行 implementer 返回后统一处理
3. 各自返回路径 + 摘要
4. 主 Agent 汇总后统一 commit
5. 主 Agent 在所有 implementer 返回后，统一处理共享文件改动（如果有）

**冲突预防**：
- dispatch-context 约束节必须写明：`只改动 {pkg}/ 目录下的文件。共享文件（{列出}）不在本次改动范围内`
- 如果某个 implementer 必须改共享文件 → 该包不能并行，改为串行（主 Agent 先派其他包并行，再串行处理含共享改动的包）
- 无法确定是否有共享改动 → 串行（安全默认值）

**基础设施隔离（并行时强制）**：
- debug server 端口：每个 implementer 的 dispatch-context 约束节分配不同端口（如 pkg-a: 3001, pkg-b: 3002）
- 测试数据库：每个 implementer 用独立数据库路径（如 `test-{pkg}.db`），不共享同一 test.db
- 环境变量：dispatch-context 写明各 subagent 独立的环境变量值（如 `PORT=3001` vs `PORT=3002`）
- 临时文件：各 subagent 写入 `P4-implementation/{pkg}/` 独立目录

主 Agent 在并行派发前**必须**为每个 subagent 的 dispatch-context 分配上述隔离参数。当前无 gate 脚本检查（已知缺口），但未分配导致运行时冲突（端口占用/数据库锁）时计为重试，不算环境问题。

## gate 规则（check-gate.py 会跑）

```bash
check-gate.py P4 $TASK_DIR
```

- **exit 0**：暂存区含非 md/yaml 代码文件（git diff --cached --name-only）
- **exit 1**：暂存区仅 .md/.yaml 文件（无实际代码变更）→ 不能推进
- **exit 1**（RM-AG0046 三重门槛）：检测 violations 非空时，`known-violations.md` 必须存在且登记条目数 ≥ violation 数（评审检查复用上方既有 exit 1 条件；violations 为空 / 检测未部署 / git 通道不可用时不阻断）
- WARNING（不改变 exit code）：骨架/CODE-MAP 机制已采用（P2-skeleton.md 或 agents/CODE-MAP.md 存在）但缺「新增文件核对表」标题

## 推进条件（全部满足才写 phase: P5）

- [ ] 暂存区含代码文件（非 .md/.yaml）
- [ ] 按 C8 映射表触发的评审全部完成：P4-review.md status: approved（所有任务都要求——risk=high 的 P2 plan-eng-review 审方案，P4 实现评审按 domains 另行派发，不可省）
- [ ] SCOPE+ 已处理（若本阶段产生）：P1-requirements.md 有 [SCOPE_RESOLVED]（行首声明格式）
- [ ] git commit 完成

## 常见错误

1. **不读 files_to_read，在项目里乱翻**：implementer 拿到 P2 的 files_to_read 清单后应按清单阅读，不要在项目里全文搜索或整目录全读——上下文会爆炸
2. **自行加范围外改动**：发现需要做但不在 P1 范围内的改动 → 标 [SCOPE+]（行首声明格式）而非直接做
3. **只跑单元测试不验证集成**：单元测试全绿 ≠ 功能可用。P5 会跑 gate_commands 做技术验证，但要确保实现时路径依赖的端点行为已验证
4. **先更新 .state.yaml 再 commit**：state 和产出在同一 commit 里——不要先 commit 产出再单独 commit state
5. **gate 不过 ≠ 你失败了**：红灯指向工作/设计的问题，不指向你。正确动作是诊断→退回/重试/PAUSED，不是修改产出让它变绿。

## 下游影响

- P5 验证依赖：P5 跑 gate_commands.P5 的命令（在 P2 声明），确保你的实现能通过
- P6 验收依赖：实现路径的端点行为必须可验证（确认 API 返回正确的 Content-Type、状态码等）
- 代码改动文件路径：P8 发布时确认版本文件变更需要知道你改动了哪些 package

> 完成 → 读 phase-cards/P5-verification.md

6. **修改 P1 文档**：P4 发现 BDD 矛盾时标 DESIGN_GAP，不直接改 P1-requirements.md。需变更 P1 时标 `[BASELINE_CHANGE: 理由]` 并经主 Agent 批准。
<!-- AGATE_CARD_END -->

<objective_info>
### A. 路径拓扑
- worktree 根 = `/home/kity/oclab/agateon/.worktrees/agate-TAG0027`（分支
  feat/TAG0027-orchestration-semantics）
- 任务目录 = `agate-workspace/tasks/TAG0027-orchestration-semantics/`
- 协议本体（改它）= worktree 的 `agate/`

### B. B3a 批测试（5 用例）转绿目标速查
- 各文档命中段处理到位（豁免结构 / 注记标记 / 语义清理三分类落地），CHECK 14 语义下
  0 命中（测试模拟 CHECK 14 判定逻辑断言文档状态）
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
