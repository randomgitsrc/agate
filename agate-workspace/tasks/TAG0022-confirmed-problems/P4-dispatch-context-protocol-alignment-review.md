# P4-dispatch-context-protocol-alignment-review — TAG0022 self-gate 协议对齐审查（C 批后）

> 派发对象：protocol-alignment-review（self-gate 语义审查，P2-design §9 纪律：C-migration 批完成后、B-judge 批开始前）。这是本轮的强制指令，不是参考信息。
> 任务目录：`{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/`

## 背景

TAG0022 的 C-migration 批（RM-AG0038）对协议-脚本面做了最大改动：`check-gate.py` 解析层 A/B/C/D 组迁至 agate_common 共享读取器 + agate-md-field-get 新 op 注册 + check-structure-consistency.py S-3 双向收紧 + rules/phases.yaml gates 命令串增补。按 self-gate 纪律（SELF-GATE.md / P2-design §9），commit 前派发本审查，确认协议条文 ↔ 脚本行为语义一致。

## 审查对象（worktree 当前工作区 diff）

- `agate/scripts/check-gate.py`（迁移后）：A 组 `_frontmatter_field` 删除改走 `_md_field_get`（9 处含 L799/805）；B/C/D 组正则迁 agate_common 共享读取器
- `agate/scripts/agate_common.py`：新增共享读取器（count_markers / extract_bdd_titles / parse_ui_design_section / count_p6_pass_fail / count_p7_markers / count_design_gap / count_code_map_lines / parse_fail_list_block / count_kf_entries / has_keyword / extract_embedded_yaml_blocks）
- `agate/scripts/agate-md-field-get.py`：KNOWN_OPS 新增 status/agent/project_phase/code_map_new_files_count/code_map_reviewed_count/created
- `agate/scripts/check-structure-consistency.py`：S-3 收紧（S-3a/S-3b 叠加，既有 S-3 outputs/orphan/exec_role 保留）
- `agate/rules/phases.yaml`：gates[].check 命令串增补
- `agate/rules/dispatch.yaml` + `agate/rules/schema/dispatch.schema.json`：judge_required_since（若 B 批已落地则一并审）
- `agate/state-machine.md`（L442-443 judge 模板语义，若 B 批已落地）+ `agate/phase-cards/P1-requirements.md`（judge 声明 checklist，若 B 批已落地）
- `agate/UPGRADING.md`（v0.61.0 章节）+ 根 AGENTS.md + `.github/workflows/protocol-tests.yml`（若 A 批已在 diff）

## 审查清单（A1-A7，角色定义逐项）

- A1 文档→脚本对齐：P2-design.md §4.2 逐点映射 + P1 BDD-3/5 声明 vs check-gate.py/agate_common.py/check-structure-consistency.py 实现（如 rules/*.yaml 新规则、S-3 收紧语义）
- A2 脚本→文档对齐：迁移后脚本行为 vs state-machine.md / WORKFLOW.md / dispatch-protocol.md / phase-cards 相关描述
- A3 一致性连锁 + 反向传播：**反向传播重点**——check-gate.py 解析层迁移后，其他读任务 md 的脚本（check-pruning/check-p6-*/agate-risk-score/check-routing/ci-gate-backstop 等）是否受影响需要同步；S-3 收紧是否需同步 WP 的 pre-commit 检查总览；agate-md-field-get KNOWN_OPS 扩展是否需同步 task-files.md / 角色卡样例 / scripts/README.md / conftest helpers（角色定义 table 最后一行列出全部传播路径）
- A4 测试覆盖：**必须附最近一次 pytest 实跑输出（含 passed/failed 计数）**——C 批迁移后全量（或至少目标文件集）；S-3a/S-3b 漂移用例、静态扫描用例、judge P1 用例覆盖
- A5 下游影响 + 文档传播：已有项目 gate 行为是否有变（破坏性变更——check-gate.py 判定口径不变但读取方式变）；CHANGELOG 未更新属正常（版本发布在 P8）；UPGRADING v0.61.0 章节
- A6 锚点表覆盖：CHECK 9 锚点表是否需要更新（check-gate.py 被迁移/新 op 是否需要登记）
- A7 设计原则一致性：对照 agate/adr.md 相关 ADR（结构化层/RM-AG0022 相关）

## 客观查证信息

- P2-design.md §4.2.1 逐点映射清单（迁移预期）；P2-review.md 锁定决策 3（共享读取器架构）
- P3-test-cases.md §5 契约注解（judge 判据 / S-3 叠加 / M15 默认关闭）
- 迁移口径 D2：A/B/C/D 组清零、E/F 组不计入（.state.yaml 读取 + git/CHANGELOG 输出解析不迁移）
- NB-1：既有 S-3 outputs/orphan/exec_role 检查必须保留（S-3a/S-3b 是叠加子检查）；NB-2：P6.5 无卡片阶段沿用跳过模式
- B 批（judge P1 校验）若已在本 diff 内，一并按 0039 判据核对

## 环境约束

Linux；/tmp 只读；bash 一律 timeout；双工作区纪律（只读消费，写操作仅限留痕/成果文件）。状态标记：`[PROD_NOT_TOUCHED]`/`[PROD_TOUCHED]`。

## 产出

1. 留痕文件：`{project_root}/docs/reviews/agate-alignment-{date}-TAG0022-01.progress.md`（原始执行痕迹，逐条追加；开始前 rm -f；Write 前先检查目标路径已存在与否——同一任务可覆盖）
2. 成果文件：`{project_root}/docs/reviews/agate-alignment-review-{date}-TAG0022.md`（A1-A7 七项，每项结论 ALIGNED/MISALIGNED/NEEDS_HUMAN_REVIEW + 逐项引用原文/代码行号；MISALIGNED 附差异+建议；NEEDS_HUMAN_REVIEW 附 [HUMAN_CONFIRMED:] 待补）

## 门槛（什么算完成）

- 成果文件存在且 A1-A7 七项齐全，每项有结论（A1/A2/A3/A4/A5/A6 三态 + A7 两态）
- A4 含最近一次 pytest 实跑输出（passed/failed 计数）
- 所有 MISALIGNED 项有差异描述 + 建议方向

## 返回给我

只返回两行：① 成果文件路径；② 结论汇总（N 项 ALIGNED / M 项 MISALIGNED / K 项 NEEDS_HUMAN_REVIEW）。绝不返回文件全文。

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