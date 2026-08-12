> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。

---
phase: P4
generated_by: agate-inject-card.sh + 主 Agent
task_id: T001
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

P4 实现阶段的**第 3 个子派发**（共 4 个，流 A/B 已完成并 commit）。本次只做**流 C**：P1 标记"已解决/已确认"状态结构化（NEED_CONFIRM 逐条匹配、SCOPE_RESOLVED 闭环）+ 角色卡/模板贴可复制 frontmatter 样例。流 D 后续单独派发。

### 约束

1. **范围锁定为流 C，允许改动的文件（且仅这些）**：
   - `agate/scripts/agate-md-field-get.py`（追加 `need_confirm_resolved`/`suggest_resolved`/`scope_resolved` 三个 list op，在流 A/B 已有基础上继续追加，不动已有部分）
   - `agate/scripts/check-gate.sh`（**只改 P1 分支约 67-98 行区域**——P2/P6/P7 分支流 A/B 已处理完，不要动）
   - `agate/scripts/check-scope-resolved.sh`
   - `agate/assets/templates/task-files.md`（P1/P2/P6/P7 产出规格节贴可复制 frontmatter 样例，BDD-24）
   - `agate/assets/execution-roles/analyst.md`、`agate/assets/execution-roles/architect.md`、`agate/assets/execution-roles/verifier.md`（同上，角色卡里贴样例）
   - `agate/phase-cards/P1-requirements.md`、`agate/phase-cards/P2-design.md`、`agate/phase-cards/P6-acceptance.md`、`agate/phase-cards/P7-consistency.md`（产出规格节同步新 frontmatter 要求）
   - **不改**：`agate/scripts/check-changelog.sh`、`agate/scripts/agate-state-yaml-check.py`（流 D 的事）
   - **不改**：`agate/scripts/agate-frontmatter-check.py`（流 A 已把 `need_confirm_resolved`/`suggest_resolved`/`scope_resolved` 三个字段登记在 P1 schema 的 `migrated_keys` 里了——它们是**可选字段**，不在 `required` 元组内，不需要新增校验规则；如果你核对后发现校验器这块确实有问题，标 `[DESIGN_GAP]`，不要直接改）
   - **不改**：`agate/scripts/check-gate.sh` 的 P2/P6/P7 分支、`pre-commit-gate.sh`、`check-p6-*.sh`（流 A/B 已完成）
   - **不改**：`agate/tests/**`（测试已由 P3 test-designer 写好并 commit；发现测试有 bug 标 `[SCOPE+]`，不要私自改）
2. **实现依据是 P2-design.md §3.3（3.3.1-3.3.3）**，伪代码/frontmatter 样例/判定逻辑已经定死，照做。
3. **NEED_CONFIRM 判定用逐条匹配，不是数量相减**：正文每条 `- [NEED_CONFIRM] ...` 的描述必须能在 frontmatter `need_confirm_resolved` 列表中找到对应项，未匹配的即阻塞（BDD-21）。这是 F14 教训（避免数量相减的 0-vs-0 歧义）——`need_confirm_resolved` 列表存 5 项、正文有 5 条 NEED_CONFIRM，"数量对但内容对不上"必须能被识别为未解决，不能只比数量。具体的"匹配"定义（描述子串/精确匹配等）自己根据 P3 已写的测试用例反推确切期望（测试断言即真理）。
4. **SUGGEST WARNING 去重**：`suggest_resolved` 里已采纳的项不要重复输出 WARNING（现有 typo 兜底逻辑保留）。
5. **SCOPE_RESOLVED 闭环判定（BDD-22）**：`check-scope-resolved.sh` 的**跨文件 `[SCOPE+]` 散文扫描逻辑保留不变**（发现性标记保持散文，BDD-23）；只改"是否已解决"的判定——读 P1 frontmatter `scope_resolved`（非空列表即已解决 → 通过；有 `[SCOPE+]` 但 `scope_resolved` 为空/不存在 → 拦截）；旧格式（frontmatter 无该字段）→ 回退现有正文 `[SCOPE_RESOLVED]` grep 判定。
6. **BDD-23 边界——绝对不要碰的东西**：`[SCOPE+]`/`[PROD_TOUCHED]`/`[DESIGN_GAP]` 这三个"发现性标记"本体**不迁移 frontmatter**，`pre-commit-gate.sh` 的 PROD_TOUCHED 行首锚定检测、`check-scope-resolved.sh` 的跨文件扫描逻辑**都不改**——本次只结构化"已解决/已确认"的状态字段，不结构化"发现"本身。这是设计明确划的边界（P2-design.md §3.3.2），不是遗漏。
7. **BDD-24 角色卡/模板样例要求**：贴的 frontmatter 样例必须是**能直接复制、且能通过 `yaml.safe_load` 解析**的完整代码块（含流 A/B 已迁移的全部字段：P1 的 risk_level/phases/packages/domains + 可选字段说明、P2 的 candidate_count/packages/domains/ui_affected、P6 的 pass/fail/ui_affected、P7 的 blocker_count/deviation_count/deviation_critical_count/design_gap_count/design_gap_reviewed_count）——直接参考 P2-design.md §3.1.1（P1/P2 样例）+ §3.2.1（P6/P7 样例）里已经写好的 YAML 代码块，照抄过去即可，不要自己重新设计字段名/格式。
8. **验收目标**：`docs/tasks/T001-v2.0-structured/P3-test-cases.md` §4"流 C"表里标"**红**"的用例必须转绿——先在仓库里 `grep -rn "RT_BDD21.1\|SC_BDD22.1" agate/tests/` 定位这两个测试用例实际所在的 `.bats` 文件（P3-test-cases.md 表格文字标注可能和实际文件对不完全一致，以 grep 到的真实文件位置为准），读懂断言后实现。标"绿"的用例（`check-scope-resolved.bats` 的 SC.2/3/4/6/7、`integration/pre-commit-hook.bats` 的 IT_PT_* 系列、`check-gate-p1-review.bats` 里那条"反面回归"用例）必须保持绿。**流 A/B 已转绿的用例也必须继续保持绿**。BDD-24 本身在 P3 阶段无可执行断言（P3-test-cases.md 已说明，P6 阶段人工核对），你不需要为它找测试，但仍要按约束 7 做出可复制样例。
9. **不要求流 D 的红灯变绿**：`SY.1`/`CL.6`/`CL.7`/`CL.8` 本次不管，不能因你的改动让它们从"预期红"变成"意外崩溃"。
10. **自查用命令**（不是 gate；我会独立重跑验证）：
    ```
    cd /home/kity/oclab/agate/.worktrees/v2.0
    bats agate/tests/unit/check-gate.bats agate/tests/unit/check-scope-resolved.bats agate/tests/unit/check-retrospective.bats agate/tests/unit/check-gate-p1-review.bats agate/tests/integration/pre-commit-hook.bats agate/tests/unit/check-frontmatter.bats agate/tests/unit/agate-md-field-get.bats
    ```
11. **生产环境隔离**：不适用。
12. **追加产出 `docs/tasks/T001-v2.0-structured/P4-implementation.md` 的"## 流 C"小节**（追加，不覆盖已有"## 流 A"/"## 流 B"小节）。发现设计外必须做的改动标 `[SCOPE+]`；发现设计要求的做法有问题/不必要，**必须**用 `[DESIGN_GAP: 描述 + 判断依据]` 标记声明，不要自己决定跳过（流 A 有教训，流 B 已按标准格式做对了，继续保持）。

### 上游关联

- P2-design.md §3.3 全节（3.3.1 P1 标记结构化、3.3.2 发现性标记边界、3.3.3 角色卡/模板样例）是本次唯一设计依据。
- P3-test-cases.md §4"流 C"表是验收清单（测试用例实际所在文件需自己 grep 核实，见约束 8）。
- 流 A/B 已交付：`agate-md-field-get.py` 的 `_read_frontmatter`/`_get`/`_format_value`/`LIST_FIELDS`/`KNOWN_OPS` 基础设施；`agate-frontmatter-check.py` 的 P1 schema 已含 `need_confirm_resolved`/`suggest_resolved`/`scope_resolved` 作为可选迁移字段（无需再改校验器）。

### 输入文件（自己读）

- `agate/assets/execution-roles/implementer.md`（角色定义）
- `docs/tasks/T001-v2.0-structured/P2-design.md` §3.3 全节 + §3.1.1（P1/P2 frontmatter 样例代码块）+ §3.2.1（P6/P7 frontmatter 样例代码块，供 BDD-24 抄样例用）
- `docs/tasks/T001-v2.0-structured/P3-test-cases.md` §4（流 C 验收清单）
- `docs/tasks/T001-v2.0-structured/P4-implementation.md`（流 A/B 已交付内容）
- `agate/scripts/agate-md-field-get.py`（当前状态）
- `agate/scripts/check-gate.sh`（约 67-98 行，P1 分支）
- `agate/scripts/check-scope-resolved.sh`
- `agate/assets/templates/task-files.md`（P1/P2/P6/P7 产出规格节）
- `agate/assets/execution-roles/analyst.md` / `architect.md` / `verifier.md`
- `agate/phase-cards/P1-requirements.md` / `P2-design.md` / `P6-acceptance.md` / `P7-consistency.md`
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
- 环境状态：worktree `feat/v2.0`，`.state.yaml` phase=P4 status=active。流 A commit 3754e9d，流 B commit ebda17e（`git log --oneline -6` 可查）。流 B 独立验证：594 用例、6 个预期流C/D红灯、0 意外回归、CHECK9 0 ERROR。
- 流 A/B 遗留了 4 条 `[DESIGN_GAP:]`（check-gate.sh/check-pruning.sh 未迁移双读工具；check-gate.sh P6 回退正则放宽；P6/P7 新旧格式判定用 AND 语义）——这些不是你本次要处理的，除非你发现的问题和它们有直接冲突。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
