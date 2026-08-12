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

这是 P4 实现阶段的**第一个子派发**（共 4 个，按流 A→B→C→D 串行）。本次只做**流 A**：P1/P2 frontmatter 字段迁移 + 双读工具改造 + 新增 frontmatter schema 校验器 + pre-commit 挂载 + CHECK 9 锚点表校准。流 B/C/D 后续单独派发，本次不做。

### 约束

1. **范围锁定为流 A，严禁越界改动**。允许改动的文件（且仅这些）：
   - `agate/scripts/agate-md-field-get.py`（双读核心改造）
   - `agate/scripts/agate-frontmatter-check.py`（新建）
   - `agate/scripts/check-frontmatter.sh`（新建）
   - `agate/scripts/pre-commit-gate.sh`（仅新增挂载点，不动其他逻辑）
   - `agate/scripts/check-gate.sh`（**只改 P2 分支，约 100-173 行区域**——P1 的 NEED_CONFIRM 分支/P6 分支/P7 分支不属于流 A，禁止改动）
   - `agate/scripts/check-pruning.sh`（约 16-103 行区域，10 个 P1 字段读取点）
   - `agate/scripts/check-protocol-consistency.py`（约 439-713 行区域，CHECK 9 锚点表）
   - **不改**：`agate/scripts/check-p6-*.sh`、`agate/scripts/check-scope-resolved.sh`、`agate/scripts/check-changelog.sh`、`agate/scripts/agate-state-yaml-check.py`（流 B/C/D 的事，后续派发）
   - **不改**：`agate/assets/templates/task-files.md`、`agate/assets/execution-roles/{analyst,architect,verifier}.md`、`agate/phase-cards/*.md`——BDD-24（模板/角色卡贴可复制样例）设计上归入流 C（P2-design.md §3.3.3），本次不做，即使 P2 的 files_to_read 清单里出现这些文件也不要动
   - **不改**：`agate/tests/**`（测试已由 P3 test-designer 写好并 commit，本次只让红灯转绿，不得为了让测试通过而修改测试断言本身；如发现测试确有 bug，标 `[SCOPE+]` 报告，不要私自改测试）
2. **实现依据是 P2-design.md §3.1（3.1.1-3.1.4）**，不是你自己重新设计。伪代码、schema 规则、判别契约（字段级 presence 检测，非文件级）都已经定死，照做。
3. **agate-frontmatter-check.py 要支持全部 4 种 schema（P1/P2/P6/P7）**，不是只做 P1/P2。原因：P3 已写的 `check-frontmatter.bats` 里 `CF.6` 就是测 P7 schema 校验（含 FIND-1 边界情况），流 A 自己的测试就需要 P7 规则先能跑，不能留到流 B 再补——P6/P7 字段本身要到流 B 才会被真正写入产出物，但校验器的判定逻辑现在就要完整实现。
4. **FIND-5 硬拦截必须做**：frontmatter 块存在但 `yaml.safe_load` 解析结果不是 dict（例如单行全角冒号、无 `key: value` 结构）→ 必须报错，即使没有抛 `YAMLError`。这是 `CF.6` 之外另一个必测点。
5. **归一化契约**：`ui_affected` 等 bool 字段的 `_format_value` 必须输出恰好 `"true"`/`"false"`（小写），不能输出 Python 的 `"True"`/`"False"`——下游 `check-p6-evidence.sh`/`check-p6-provenance.sh` 做的是精确字符串匹配。
6. **验收目标（不是你自己判断"差不多了"，是下面这份清单）**：`docs/tasks/T001-v2.0-structured/P3-test-cases.md` §2"流 A"表里所有标"**红**"的用例必须转绿：`CF.1`~`CF.10`（10 条，`check-frontmatter.bats`）、`MDF.3`（`agate-md-field-get.bats`）。标"绿（characterization）"的用例（`MDF.1`/`MDF.2`/`MDF.4`、`G_BDD1.1`/`G_BDD9.1`/`G_BDD10.1`、`P2.5`/`P2.6c`/`P2.7a`、`R4.2`/`R4.3`、`R3.2`、`TDD.G1`+`PYX.*`）**必须继续保持绿**——这些是回归安全网，不是"顺便也测一下"，改坏了就是引入回归。
7. **不要求流 B/C/D 的红灯变绿**：`G_BDD16.1`/`F_BDD18.1`/`PV_BDD19.1`/`PV_BDD20.1`（流B）、`RT_BDD21.1`/`SC_BDD22.1`（流C）、`SY.1`/`CL.6`/`CL.7`/`CL.8`（流D）目前是红的，本次不需要管，后续派发会处理。你只需要保证**不要让它们从"红（预期的，还没实现）"变成"因为你的改动导致的新型崩溃"**（比如 Python import 报错影响到不相关脚本）。
8. **自查用命令**（自查不是 gate，P5 才是 gate；这里只是让你确认自己没做错）：
   ```
   cd /home/kity/oclab/agate/.worktrees/v2.0
   bats agate/tests/unit/check-frontmatter.bats agate/tests/unit/agate-md-field-get.bats agate/tests/unit/check-gate.bats agate/tests/unit/check-pruning.bats agate/tests/regression/v060-p8-internal-only.bats agate/tests/regression/v060-r4-cached.bats agate/tests/unit/check-tdd-red.bats
   ```
   （这条命令由你自己跑；我会在你返回后自己重跑一次全量 `unit/ + regression/` 独立验证，不会只信你的自查结果。）
9. **生产环境隔离**：本任务不涉及生产环境/生产数据库/生产 API，此约束不适用。
10. **不要动 P1/P2/P6/P7 阶段产出物本身**（`docs/tasks/T001-v2.0-structured/P1-requirements.md` 等）——那些文件本任务自身按 v0.35 旧格式写、走 v0.35 gate（BDD-28 自举边界），不受你这次改造影响，不要"顺手"给它们加 frontmatter 新字段。
11. **产出 `docs/tasks/T001-v2.0-structured/P4-implementation.md`**（新建，这是流 A 的产出物，不是代码文件本身）：声明 `implementation_dir: agate/scripts/`；正文按流分节（本次只写"## 流 A"一节），列出本次改动的文件清单 + 每个文件改了什么 + 对应的 BDD/测试用例。**这份文件后续流 B/C/D 派发时会被追加"## 流 B"/"## 流 C"/"## 流 D"小节，不要用会破坏已有小节结构的方式写**（比如不要用"覆盖整个文件"的方式生成，用能追加小节的结构）。若实现中发现设计之外必须做的改动，用行首 `[SCOPE+] 描述` 声明，不要直接做。

### 上游关联

- P2-design.md §3.1 全节是本次唯一的设计依据。
- P3-test-cases.md §2"流 A"表是本次唯一的验收清单（哪些红灯必须转绿、哪些绿灯不能变红）。
- P2-review.md 的 FIND-1（判别契约字段级 presence）、FIND-4（ui_affected 归一化）、FIND-5（str-not-dict 硬拦截）三条已定死的修订必须落地——不是可选项。

### 输入文件（自己读）

- `agate/assets/execution-roles/implementer.md`（你的角色定义，先读这个）
- `docs/tasks/T001-v2.0-structured/P2-design.md` §3.1（3.1.1-3.1.4，实现依据）、§13 FIND-1/4/5（修订详情）
- `docs/tasks/T001-v2.0-structured/P3-test-cases.md` §2（流 A 验收清单，含每条测试当前红/绿状态）
- `agate/scripts/agate-md-field-get.py`（待改造文件本身）
- `agate/scripts/agate-state-yaml-check.py` + `agate/tests/unit/agate-state-yaml-check.bats`（校验器范式参照——新校验器完全仿照这个写）
- `agate/scripts/check-state-yaml.sh`（薄壳参照——`check-frontmatter.sh` 完全仿照这个写）
- `agate/scripts/check-gate.sh`（约 100-173 行，P2 分支）
- `agate/scripts/check-pruning.sh`（约 16-103 行）
- `agate/scripts/pre-commit-gate.sh`（找现有 `check-state-yaml.sh` 调用点，即"2a 步骤区"，在旁边加挂载）
- `agate/scripts/check-protocol-consistency.py`（约 439-713 行，CHECK 9 锚点表结构）
- `agate/tests/unit/check-frontmatter.bats`（新测试文件，读它就知道 `agate-frontmatter-check.py`/`check-frontmatter.sh` 的确切接口/输出格式期望）
- `agate/tests/unit/agate-md-field-get.bats`（`MDF.3` 用例，确认字段级 presence 优先级的确切期望）
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
- 环境状态：worktree `feat/v2.0`，`.state.yaml` phase=P4 status=active；P3 已 commit（593924f 附近，`git log --oneline -1` 可查），`count-tests.sh` = 594，`check-tdd-red.sh` 已确认真红灯（23 个 not ok，unit+regression 范围）。
- P2 §5 固化的 gate_commands（不得修改）：`P3 = "bats agate/tests/unit/ agate/tests/regression/"`，formatter `generic-tap.sh`；P5 用整套 `sanity+unit+regression+integration`。
- CHECK 9 锚点表当前 37 条，本次改造后应为 38 条（新增 `check-frontmatter.sh` 一条：desc=frontmatter schema 校验，keywords=frontmatter，callers=pre-commit-gate.sh）。
- 不要求你自己跑 `count-tests.sh`/`check-protocol-consistency.py` 判定通过与否并写入返回结论——这两项由我（主 Agent）在你返回后独立验证。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
