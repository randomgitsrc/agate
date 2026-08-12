> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。

---
phase: P4
generated_by: agate-inject-card.sh + 主 Agent
task_id: T001
role: test-designer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 背景（为什么现在派你，不是 implementer）

流 D（任务编号规则硬切，`agate-state-yaml-check.py` 的 task_id 正则 `^T\d+$` → `^T[A-Z]{2}\d+$`）已经实现完成、代码本身正确（已核对匹配 P2-design.md §3.4 设计），但触发了一个implementer 权限范围外的连带问题：**33 个此前一直绿灯、与任务编号规则本身无关的既有测试**，因为它们的 fixture `.state.yaml` 里用 `T001`/`T999` 等旧格式当"随便找个 task_id 占位"，现在被新正则拒绝，导致这些测试里真实要跑的 `git commit`（经过真实 pre-commit hook）在 `.state.yaml` 校验这一步就失败退出，测试要验证的行为（PROD_TOUCHED 扫描、phase span 校验、dispatch-context hash 等）根本没机会被断言到。implementer 的改动范围明确禁止碰 `agate/tests/**`，所以这个问题需要你（test-designer 角色）来处理——这是修 fixture 数据，不是改测试逻辑或断言。

已独立核实（主 Agent 用 `git stash` 验证过）：这 33 个测试在流 D 改动之前是绿的，回归确系流 D 引入，不是环境问题；流 D 的代码改动本身不需要撤销或修改（硬切是 P0-brief 已定的设计要求，不能因为这个问题放宽正则或加兼容分支）。

### 目标

只改这 3 个文件里失败的具体测试用例，把它们 fixture 里作为"随便占位"用的旧格式 `task_id`（`T001`/`T001a`/`T002`/`T003`/`T999` 等）换成符合新格式 `^T[A-Z]{2}\d+$` 的占位值（如 `TXX0001`/`TXX0002`/`TXX0003`/`TXX0999`），让这 33 个测试重新变绿——**不改变任何测试的断言逻辑/期望结果**，只改 fixture 里那个具体的 task_id 字符串。

### 约束

1. **只允许改这 3 个文件**：
   - `agate/tests/integration/pre-commit-hook.bats`（26 个失败用例）
   - `agate/tests/integration/dispatch-context-card.bats`（6 个失败用例）
   - `agate/tests/unit/check-state-yaml.bats`（1 个失败用例：`SY.8`）
   - **不改**任何其他文件（含 `agate/tests/helpers/fixtures.bash`——它的默认 `task_id: T001` 目前经验证不会导致其他测试真的经过真实 hook 校验失败，改它风险大于收益，本次不动；含流 A/B/C/D 的实现代码；含 `agate/scripts/**` 任何文件）。
2. **先精确定位这 33 个失败用例，不要盲目全局替换**：先跑
   ```
   cd /home/kity/oclab/agate/.worktrees/v2.0
   bats agate/tests/integration/pre-commit-hook.bats agate/tests/integration/dispatch-context-card.bats agate/tests/unit/check-state-yaml.bats
   ```
   看哪些 `not ok`，对照失败用例名字去文件里找对应的 `@test` 块，只改那个块内的 `task_id` 字面值。
3. **不要动测试断言/测试意图**：这些测试的失败原因**全部**是"fixture 里的旧格式 task_id 导致 commit 在到达真正要测的逻辑之前就被拦截"，不是"测试期望值需要更新去适配新行为"。改完 task_id 后，测试原本期望的 exit code / 输出内容都不应该变——如果你发现某个测试改了 task_id 之后还是不通过、且原因不是 task_id 本身，说明情况比预期复杂，标 `[SCOPE+]` 或 `[DESIGN_GAP]` 报告，不要自己改测试逻辑去凑通过。
4. **`agate/tests/unit/check-state-yaml.bats` 的 `task_id: T001a`（约第 39 行）不要动**：这一行不属于 `SY.8`（"全合规"用例），大概率是另一个测试"格式错误的 task_id 应被拒绝"的负向用例，`T001a` 在旧正则 `^T\d+$` 和新正则 `^T[A-Z]{2}\d+$` 下都不合法，这个测试的预期行为不受本次改造影响，不要碰。**只改 `SY.8` 对应那个"全合规/期望 exit 0"的用例块**，把它的 `task_id: T001` 改成一个真正符合新格式的值（如 `TXX0001`），让"全合规"场景在新 schema 下依然成立。
5. **新占位值统一约定**：用 `TXX` 前缀（2 个大写字母，泛指"某项目"，不对应任何真实项目代号）+ 数字，尽量保持数字部分和原值的语义对应关系（如原来是 `T001` → `TXX0001`，`T002` → `TXX0002`，`T003` → `TXX0003`，`T999` → `TXX0999`），方便阅读时看出"这原本对应哪个旧占位"。不要用 `TAG0001` 这个值（那是流 D 自己的测试 `SY.1`/`CL.6/7/8` 专用的代表性样例，混用会造成阅读混淆，虽然功能上不会冲突）。
6. **验收标准**：
   ```
   cd /home/kity/oclab/agate/.worktrees/v2.0
   bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/ agate/tests/sanity.bats
   ```
   改完之后，这条命令应该输出 **600/600 全绿**（594 + sanity 6，且流 A/B/C/D 全部 28 条 BDD 相关红灯此前已全部转绿，本次只是清除流 D 引入的这 33 个意外回归）。
7. **`count-tests.sh` 必须仍是 594**（BDD-11 硬约束，本次不新增/删除任何 `@test`，纯改 fixture 内的字符串值）。
8. **不要碰 `docs/tasks/T001-v2.0-structured/` 下本任务自身的产出文件**——本任务自身 T001 全程用 v0.35 旧格式跑 gate，与本次修的这些测试 fixture 无关（那些 fixture 的 `T001`/`T999` 只是测试代码里"随便找个字符串当 task_id"的占位符，不是本任务本身）。
9. **自查**：改完后自己跑一遍完整验收命令（约束 6），确认 600/600。这不是最终 gate，我会独立重跑验证。
10. **生产环境隔离**：不适用。

### 上游关联

- `docs/tasks/T001-v2.0-structured/P4-implementation.md`"## 流 D"小节末尾的 `[DESIGN_GAP:]` 标记（第二条，关于 33 个回归）是本次派发的直接触发原因，完整问题清单和根因分析都写在那条 DESIGN_GAP 里，先读那个。
- 本次完成后，主 Agent 会在 P4-implementation.md 里追加一条说明本次 fixture 迁移的记录（这部分不需要你写，是主 Agent 的收尾动作）。

### 输入文件（自己读）

- `docs/tasks/T001-v2.0-structured/P4-implementation.md`"## 流 D"小节的 `[DESIGN_GAP:]`（第二条，33 个回归的完整清单和根因）
- `agate/scripts/agate-state-yaml-check.py`（新正则 `^T[A-Z]{2}\d+$`，确认哪些占位值合法）
- `agate/tests/integration/pre-commit-hook.bats`
- `agate/tests/integration/dispatch-context-card.bats`
- `agate/tests/unit/check-state-yaml.bats`
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
- 环境状态：worktree `feat/v2.0`，`.state.yaml` phase=P4 status=active。流 A/B/C/D 均已 commit（`git log --oneline -10` 可查，流 D 是最新一次 commit）。
- 主 Agent 已用 `git stash` 独立核实：33 个失败用例在流 D 改动前全绿，改动后全部因 fixture 旧格式 task_id 在真实 pre-commit hook 里被新正则拦截而失败——根因明确，不是环境问题，不是随机 flaky。
- 失败用例清单（截至本次派发时）：`SY.8`（check-state-yaml.bats）；`pre-commit-hook.bats` 的 `IT.2/IT.3/IT.5/IT.6/IT.8/IT.9/IT.9b/IT.10/IT.11/IT_PT_BINARY.1/2/4/5/6/7/IT_PHASE_SPAN.5/IT_PT_MENTION.1/IT_P6_CODE.2/5/IT_RETREAT.1/2/IT_PT_T6.2/3/IT_CHANGELOG_P54b/IT_GATE_REAL.1/HOOK_EVIDENCE_WARNING`（26 个）；`dispatch-context-card.bats` 的 `DC.2/3/4/5/6/7`（6 个）。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
