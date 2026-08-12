---
phase: P4
generated_by: agate-inject-card.sh + 主 Agent
task_id: TAG0003
role: review
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
独立评审 TAG0003 P4 实现（worktree agate/ 的 6 脚本 + 16 文档 + 7 测试 fixture + 3 修复轮脚本改动），产出 docs/tasks/TAG0003-workspace-architecture/P4-review.md（status: approved / rejected / needs-revision）。你是偏执 Staff Engineer（C8 映射：domains=[backend,cli] + risk=high → review，P4 实现评审不可省）。

### 约束
- **只审不写**：不直接修改实现文件，只产出评审意见。
- 本任务是 **agate 协议自身改造**（dogfooding）：评审对象是 worktree `agate/`（新版协议），`~/.agate` 是稳定版 v0.40.2 开发工具（禁止改动）。
- 评审重点（review 角色清单 + 本任务特有风险）：
  1. **数据安全与正确性（Pass 1 CRITICAL）**：迁移工具 `agate-migrate-workspace.sh` 的 git mv / fallback mv / 自动 commit 逻辑——是否可能误删/覆盖数据？空源/冲突/仓库外边界是否安全？自动 commit 的全量 index 风险是否被正确标注与缓解？
  2. **路径解析正确性（Pass 1）**：`agate-workspace-resolve.sh` 解析优先级（.agate.env > AGATE_TASKS_DIR > 默认）、相对/绝对路径、含空格、项目外路径——输出是否与 BDD-2/3/4/5 一致？pre-commit-gate.sh 消费绝对路径时是否避免 REPO_ROOT 重复拼接（P2-review 非阻塞项 2）？
  3. **去硬编码完整性（Pass 1）**：check-state-transition.sh（dirname!=REPO_ROOT 语义）、check-pruning.sh（工作区 tasks 相对路径）、check-protocol-consistency.py（PATH_IGNORE_SUBSTRINGS 白名单）——是否仍有 `docs/tasks` 残留硬编码导致行为错误？（允许文档侧示例/旧布局兼容的保留引用，但要区分）
  4. **代码健康（Pass 2 INFORMATIONAL）**：脚本 set -euo pipefail、shellcheck、错误处理、资源清理；ci-gate-backstop.py 与 bash 解析器的一致性。
  5. **行为不变回归（BDD-13）**：既有 gate 逻辑语义是否保持（只是路径来源变化）？既有 603/624 用例数是否不漂移？
  6. **SCOPE_GAP 闭环**：check-protocol-consistency.py / install-hook.sh / agate-render-dispatch-prompt.sh 补做是否到位？
  7. **DESIGN_GAP 审查**：迁移工具自动 commit（已标记 [DESIGN_GAP_REVIEWED: 已确认]）——复核该决策是否有更安全的替代，若同意保持，标注确认；若不同意，标 BLOCKER。
  8. **文档一致性**：orchestrator-template 路径切换、WORKFLOW 内容边界判据、roadmap 循环规范是否与 P2 设计一致、是否可在 P6 验收。
- 结论必须引用实质锚点（文件路径 + 行号/函数/决策编号），不引用锚点的裸 "approved" 会被 gate 判假完成。
- 产出文件 Header 必须含 `status:` 字段（approved/rejected/needs-revision），与返回摘要一致。
- 禁止行首 `- PASS` / `- FAIL` 格式（provenance 审计拦截）。

### 上游关联
- implementer-core：解析器+迁移工具新增、4 脚本改造；P3 目标 47/47 转绿；shellcheck 0 error；[DESIGN_GAP] 迁移工具自动 commit（主 Agent 已标记 REVIEWED 已确认）。
- implementer-docs：16 文档换血完成，WORKFLOW 内容边界判据 + roadmap 循环规范落地，orchestrator 路径切换完成。
- implementer-tests：8 文件 392 处换血，用例数 624 无漂移；[SCOPE_GAP] 2 脚本 + RP.13 红灯交接。
- implementer-fix：SCOPE_GAP 白名单/提示路径重校准 + RP.13 补 {AGATE_WORKSPACE} 替换，三处全绿（consistency 0 ERROR / render-dispatch-prompt.bats 16/16 / install-hook.bats 5/5 / shellcheck 0 / count-tests 624）。
- 主 Agent 自跑：resolve+migrate 17/17 绿、check-state-transition 47 ok、consistency 0 ERROR。

### 输入文件
- docs/tasks/TAG0003-workspace-architecture/P2-design.md（方案设计——必读，对照评审）
- docs/tasks/TAG0003-workspace-architecture/P4-implementation-core.md / -docs.md / -tests.md / -fix.md（实现记录——必读）
- docs/tasks/TAG0003-workspace-architecture/P1-requirements.md（20 条 BDD——必读）
- docs/tasks/TAG0003-workspace-architecture/P3-test-cases.md（测试契约——必读）
- agate/scripts/ 下 9 个改动脚本（agate-workspace-resolve.sh / agate-migrate-workspace.sh / pre-commit-gate.sh / ci-gate-backstop.py / check-state-transition.sh / check-pruning.sh / check-protocol-consistency.py / install-hook.sh / agate-render-dispatch-prompt.sh——必读，逐个审查）
- agate/orchestrator-template.md + agate/WORKFLOW.md（核心文档改动——必读）
- agate/tests/ 下改动 fixture + 新增测试（按需读取）
- AGENTS.md（项目约定/脚本约定——必读）
</dispatch_guide>

<!-- AGATE_CARD_START -->
## 当前阶段卡片：P4

路径：phase-cards/P4-implementation.md
---
# P4 — 代码实现

> 当前状态：[首次 / 重试 #N / 裁剪跳阶]
> 裁剪跳阶 → 确认 P1 phases 不含 P4 且有合规理由（check-pruning.sh 已检查）→ 跳过，读 P5 卡片

## 如果是首次进入本阶段

0. 跑 `agate-capture-env-baseline.sh $TASK_DIR`（自动捕获环境基线）。
   该步骤不会阻塞流程——任何 stderr 输出（含 WARNING）均可忽略，直接继续步骤 1，
   无需查看结果、无需判断、无需因为看到 WARNING 而停下来处理。
1. 派发 implementer subagent → 产出代码文件
   1.1 写 P4-dispatch-context-implementer.md（派发指引：目标/约束/上游关联/输入文件 + 客观查证信息）
2. 按 P2 的 gate_commands 跑单元测试（非 gate，只是自查）
3. 按 C8 映射表派发评审（见下方）
4. 预跑 check-gate.sh P4（确认暂存区有代码文件）
5. 更新 .state.yaml phase=P4 → P5
6. git add docs/tasks/{Txxx}/ + 代码文件（含 .state.yaml，若 .gitignore 忽略需 git add -f）
7. git commit -m "wf({Txxx}-P4): {摘要}"

## 如果是重试

确认上一轮失败原因（来自 gate 输出 / review rejected 理由）
→ 只修复失败项，不重做已通过的部分
→ 修复后重跑全量测试（T027 教训：修复可能引入回归）
→ 读 agate/rules/state-transitions.md 确认 retry 上限（P4 MAX=3）

**若这次是从 P6（或其他更后的阶段）退回来的**：`docs/tasks/Txxx/` 下不会再有旧的 P6-acceptance.md（已被归档），但当初具体是哪条 BDD 失败、失败原因是什么，会摘要在 `docs/tasks/Txxx/.retreat-history.md` 里——**重新派发 implementer 时，dispatch-context 必须引用这份摘要**，不能让 implementer 只看到"现有代码"却不知道具体要修哪里。已有代码不会被撤销、也不需要重新实现，是在已有实现基础上定向修复。

## 前置条件

- [ ] P2-design.md 存在且 files_to_read 字段完整（导航清单）
- [ ] P2-review.md status: approved（P2 不可裁剪）
- [ ] P3-test-cases.md 存在（测试已设计）
- [ ] check-tdd-red.sh 确认红灯（测试先于实现）
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
4. 组长产出：P4-review.md。**agent 字段必须非 main**（与 P2 评审同规则，check-gate.sh 在 P2 分支硬拦截 agent=main 的 approved）
5. 组长规则：不发表新意见，只汇总；任何 BLOCKER → rejected；分歧 → 交人工；全票无 BLOCKER → approved

**单评审角色时**：直接派发，无需组长汇总，产出直接写 P4-review.md。

review 不通过 → implementer 修改代码 → 再 review → … → approved（⑩迭代循环，review 和 gate 重试共享 retry 预算）

## 按包拆分并行（条件触发，需额外约束）

> 仅当 P2 packages > 1 且包间无依赖时适用。单包任务跳过本节。

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

## gate 规则（check-gate.sh 会跑）

```bash
check-gate.sh P4 $TASK_DIR
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
- 环境状态：worktree 是改造对象（分支 dev/workspace，P4 改动未 commit）；`~/.agate` → 主 checkout 是稳定版 v0.40.2 开发工具（禁止改动）。
- 改动面：9 脚本（2 新 + 7 改）+ 16 文档 + 1 新模板 + 7 测试 fixture + 3 实现记录文件。
- 测试基线：全量 bats 624 用例（含 P3 新增 21）；consistency 0 ERROR；shellcheck 0 error；count-tests 624 无漂移。
- 已核实查证：P2 §1.1 明确列出 check-protocol-consistency.py（BDD-20 白名单）+ install-hook.sh（BDD-6 提示）；pre-commit-gate.sh L83 现为 `TASK_DIR="$REPO_ROOT/$AGATE_TASKS_DIR/$TASK_ID"`（绝对路径时不可再拼 REPO_ROOT）。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
