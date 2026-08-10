> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。

---
phase: P4
generated_by: agate-inject-card.sh + 主 Agent
task_id: T001
role: protocol-alignment-review
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

对 T001 P4 阶段（流 A+B+C+D+fixture修复，5 个 commit 的累计 diff）做一次完整的协议-脚本对齐审查（self-gate Layer 1，因改动了 agate 协议本体的脚本和文档）。这是**全量的一次性审查**（不是逐 commit 审查），覆盖 P4 整个实现阶段的完整变更集。

### 第一步：意图分析

本次变更的意图：把 agate 协议里散落在正文（半结构化 YAML/纯散文）的机器读取字段迁移为 frontmatter + pyyaml 解析 + schema 校验，消除长期的"正则摩擦补丁税"。四个子流分别处理：P1/P2 候选数字段迁移+新校验器（流A）、P6/P7 结果结构化（流B）、P1 标记状态结构化+角色卡模板样例（流C）、任务编号规则硬切（流D）。

### 约束

1. **审查范围**：`git diff 293924f..HEAD -- agate/ SELF-GATE.md`（293924f 是 P3 commit，即 P4 开始前的基线；HEAD 是当前最新 commit，即 fixture 修复完成后）。**不要**审查 `docs/tasks/T001-v2.0-structured/` 下的任务产出物本身（那些是本任务自己的阶段文件，不是协议本体）。
2. **逐项走完 A1-A7**，每项要有明确结论（ALIGNED / MISALIGNED / NEEDS_HUMAN_REVIEW），且**逐项引用原文行号**（协议文档行号 + 脚本代码行号），不要写"大概一致"这种模糊结论。
3. **A4 测试覆盖**：必须附最近一次 bats 全量实跑输出（含 passed/failed 计数）。可以直接用这个数字（主 Agent 已独立验证过）：`bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/ agate/tests/sanity.bats` → **600/600 全绿，0 个 not ok**；`count-tests.sh` → 594。你自己也可以重跑一遍确认，不是必须只信这个数字。
4. **重点核对 4 条已知的 `[DESIGN_GAP:]`**（implementer 在实现过程中主动声明、尚未经过 P7 正式裁决的设计偏离，都在 `docs/tasks/T001-v2.0-structured/P4-implementation.md` 里）：
   - 流A：`check-gate.sh`/`check-pruning.sh` 未迁移到双读工具（现有 grep 巧合兼容 frontmatter）
   - 流B：`check-gate.sh` P6 回退正则比设计原文更宽松；P6/P7 新旧格式判定用 AND 语义（设计原文未明确 AND/OR）
   - 流C：`check-scope-resolved.sh` 对"字段存在但空列表"与"字段完全不存在"未做区分
   - 流D：`check-changelog.sh` 移除了设计原文要求"保留"的 `grep -qF` fallback
   这 4 条**不是让你重新裁决对错**（那是 P7 一致性阶段的正式职责），而是请你在 A1（文档→脚本对齐）审查里，对这 4 处明确标注"这是已知声明的偏离，非本次审查新发现"，避免和你自己审查中新发现的对齐问题混在一起。如果你审查后认为这 4 条里有哪条其实是真正的 MISALIGNED（比如实际代码和 DESIGN_GAP 描述的都对不上），才需要单独指出。
5. **A6 锚点表覆盖**：CHECK 9 锚点表流 A 已从 37 条扩到 38 条（新增 `check-frontmatter.sh` 一条），流 B/C/D 未新增锚点条目（复用既有 `check-gate.sh`/`check-p6-*.sh`/`check-changelog.sh`/`agate-state-yaml-check.py` 锚点）。核对这个判断是否正确——即锚点表现在是否完整覆盖了本次改造涉及的脚本。
6. **A5 文档传播重点**：本次实际改了不少文档（`agate/assets/templates/task-files.md`、`agate/assets/execution-roles/{analyst,architect,verifier}.md`、`agate/phase-cards/{P1,P2,P6,P7}*.md`、`agate/state-machine.md`、`agate/dispatch-protocol.md`、`agate/role-system.md`、`agate/assets/templates/active-tasks-template.md`），核对反向传播表里列的"应该被这些改动影响但未列在 diff 中的文件"是否有遗漏——尤其 `agate/WORKFLOW.md`、`agate/orchestrator-template.md`、`agate/LIMITATIONS.md`、`agate/CONTEXT.md`、`agate/adr.md`、`agate/scripts/README.md`、`agate/tests/README.md` 这些在你的角色定义"配套文件提示"和"反向传播常见路径"表里提到的文件本次都**没有改动**——请判断这是否遗漏（比如：`CONTEXT.md` 的术语表要不要补充 frontmatter 相关新术语？`LIMITATIONS.md` 要不要补充"结构化不解决语义真实性"这条边界声明？`adr.md` 要不要为"frontmatter 优于独立 YAML 文件"这个选型新增一条 ADR？）。
7. **不要改代码/文档**，只写审查报告。发现 MISALIGNED 只需在报告里指出，不需要你自己修——主 Agent 会看报告决定是重新派 implementer 修复还是留到 P7。
8. **分阶段落盘**：留痕文件 `docs/reviews/agate-alignment-2026-08-10-01.progress.md`，开始前先 `rm -f` 清空，每读完一个文件/完成一个对比判断就 `echo >>` 追加，不做整理。成果文件 `docs/reviews/agate-alignment-review-2026-08-10.md` 审查完所有 A1-A7 后一次性写出。

### 上游关联

- `docs/tasks/T001-v2.0-structured/P2-design.md` 是本次改造的设计依据（架构决策）。
- `docs/tasks/T001-v2.0-structured/P4-implementation.md` 是 implementer 的完整交付记录（含 4 条 `[DESIGN_GAP:]`），按流 A/B/C/D 分节。
- 这是 T001 任务本身（agate v0.40.0 结构化改造）走完整 P0-P8 流程的一部分，self-gate 审查在这里是"P4 完成后、进入 P5 前"这个时间点做一次（不是每个 commit 都单独审查一次）。

### 输入文件（自己读）

- `agate/assets/review-roles/protocol-alignment-review.md`（你的角色定义，已经注入在这份 dispatch-context 里，但建议再读一遍原文件确认没有遗漏）
- `docs/tasks/T001-v2.0-structured/P2-design.md`（设计依据全文）
- `docs/tasks/T001-v2.0-structured/P4-implementation.md`（实现记录，含 4 条 DESIGN_GAP）
- `git diff 293924f..HEAD -- agate/ SELF-GATE.md`（完整代码/文档 diff，自己跑这个命令读）
- `agate/adr.md`（A7 审查用）
- `agate/CONTEXT.md`、`agate/LIMITATIONS.md`、`agate/WORKFLOW.md`、`agate/orchestrator-template.md`（A5 反向传播核对用）
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
| risk=high | —（plan-eng-review 在 P2 已派）| — |

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
- [ ] 按 C8 映射表触发的评审全部完成：P4-review.md status: approved（无触发评审角色时此项自动满足）
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
- 环境状态：worktree `feat/v2.0`，5 个 P4 相关 commit：3754e9d（流A）/ ebda17e（流B）/ 901f61d（流C）/ 2b56579（流D）/ 68e4173（fixture修复）。基线 commit 293924f（P3）。
- 主 Agent 已独立验证：`bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/ agate/tests/sanity.bats` = 600/600，`count-tests.sh` = 594，`check-protocol-consistency.py` = 0 ERROR，`shellcheck -S warning agate/scripts/*.sh` 未见报错（分散在各流自查中确认，你可以重跑全量确认）。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
