---
phase: P4
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0007
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令。本批次是 P2-design.md `dispatch_plan` 声明的
`dogfood-bootstrap` 批次（4 批并行之一，complexity: low）。

### 目标
为 agate 仓库自身初始化 `{AGATE_WORKSPACE}/agents/CODE-MAP.md`（本任务的 dogfooding 实例——
agate 自己就是采用 CODE-MAP 机制的第一个项目），作为 BDD-6"CODE-MAP 存在性"的验收对象（由 P6
acceptance 人工核对存在性，不是自动化测试覆盖对象——`assets/templates/code-map-template.md`
协议本体模板才是自动化测试覆盖对象，那是另一批次 `code-map-docs` 的产出物，与你要写的这份
`agents/CODE-MAP.md` dogfooding 实例是两个不同文件）。

### 约束
1. 文件路径：`{AGATE_WORKSPACE}/agents/CODE-MAP.md`——即本 worktree 的
   `agate-workspace/agents/CODE-MAP.md`（**不是** `~/.agate`，本任务双工作区纪律：worktree 自己
   的 agate-workspace/，见 HANDOFF-TAG0007.md）。若 `agate-workspace/agents/` 目录不存在，先
   创建该目录。
2. 内容须含五类必填字段（与 `code-map-docs` 批次产出的 `assets/templates/code-map-template.md`
   模板结构一致，字段名：模块、层、依赖方向、关键文件、约定），但填**真实内容**（不是占位声明）
   ——描述 agate 协议本体自身的实际架构：
   - **模块**：phase-cards（9 张阶段卡片）/ execution-roles（7 个执行角色）/ review-roles（10 个
     评审角色）/ scripts（gate/一致性/状态脚本家族）/ templates（11 个模板文件）五大模块
   - **层**：协议流程层（phase-cards，定义 P0-P8 各阶段做什么）→ 角色层（execution-roles +
     review-roles，定义谁来做）→ 工具层（scripts，把判定规则脚本化）→ 模板层（templates，
     给角色/主 Agent 提供可复制的产出格式）
   - **依赖方向**：phase-cards 描述流程但不直接依赖角色/脚本实现细节（松耦合，角色/脚本可独立
     演进只要遵守卡片声明的契约）；scripts 消费 phase-cards/templates 声明的字段名做判定
     （如 gate 脚本读 frontmatter 字段）；execution-roles/review-roles 消费 phase-cards 声明的
     职责边界，不反向定义流程
   - **关键文件**：WORKFLOW.md（流程总览）、dispatch-protocol.md（派发协议）、state-machine.md
     （状态转移）、role-system.md（角色体系）、check-gate.py（门槛判定核心脚本）
   - **约定**：新增机制需经 P0-P8 完整流程（不可因"新机制"裁剪阶段）；改协议脚本走 TDD；
     改协议文档/脚本/卡片触发 SELF-GATE 自审
3. 具体标题 markup 形式（`##`/`###`/加粗等）由你自行决定，不强制与 `code-map-template.md` 批次
   产出的 markup 完全一致（P2-design.md §7 已明确两批次并行、不强制 markup 一致）。
4. 本批次不依赖 `code-map-docs` 批次的实际产出物返回即可独立完成（P2-design.md 已完整声明五
   字段类别名，你可直接依据本 dispatch-context 的字段名清单产出，不需要等待另一批次）。

### 不要做
- 不要碰 `assets/templates/code-map-template.md`（`code-map-docs` 批次的产出物，是协议本体
  模板，与你写的 dogfooding 实例是两个不同文件）
- 不要碰任何其他批次范围内的文件（phase-cards/execution-roles/scripts/WORKFLOW.md 等）
- 不需要写测试代码（本批次产出是数据文件，无对应自动化测试，见「目标」节说明）

### 验证
本批次无对应 pytest 用例。自查方式：确认文件存在 + 五个字段名均出现在内容中即可：
```bash
timeout 10s test -f agate-workspace/agents/CODE-MAP.md && \
  grep -c "模块\|层\|依赖方向\|关键文件\|约定" agate-workspace/agents/CODE-MAP.md
```

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0007-project-structure/P2-design.md（§1.1/§3，本批次的权威规格
  来源）
- /home/kity/oclab/agate/.worktrees/agate-TAG0007/agate/WORKFLOW.md:35-75（目录结构树状图，
  填写"模块/层"字段内容的参照）
- /home/kity/oclab/agate/.worktrees/agate-TAG0007/HANDOFF-TAG0007.md（双工作区纪律，确认
  {AGATE_WORKSPACE} 指向本 worktree 的 agate-workspace/，不是 ~/.agate）
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

## 评审派发（C8 机械映射）

**在 P4 实现完成后、gate 前**，按 P1 声明的 domains 和 risk_level 派评审。C8 映射表是机械规则，不靠判断"需不需要"：

| domain | 派哪些评审 | 产出 |
|--------|----------|------|
| backend | review | P4-review.md |
| frontend | design-review | P4-review.md |
| mcp | review（关注 MCP 接口契约）| P4-review.md |
| security | cso | P4-review.md |
| risk=high | P4 实现评审（按 domains 派 review/design-review/cso；P2 plan-eng-review 已审方案，P4 实现评审不可省）| P4-review.md |

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
- 批次范围（P2-design.md §7）：`dogfood-bootstrap`，涉及文件 1 个：
  `{AGATE_WORKSPACE}/agents/CODE-MAP.md`（新建，即本 worktree
  `agate-workspace/agents/CODE-MAP.md`）
- 当前 `agate-workspace/agents/` 目录：{尚未存在，需创建}
- 4 批并行范围两两不相交（P2-design.md §7 已核实），本批次可独立完成，无需等待其他批次
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
