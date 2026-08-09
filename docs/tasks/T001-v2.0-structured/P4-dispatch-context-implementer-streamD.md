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

P4 实现阶段的**第 4 个、也是最后一个子派发**（流 A/B/C 已完成并 commit）。本次做**流 D**：任务编号规则硬切——`agate-state-yaml-check.py` 的 task_id 正则从 `^T\d+$` 改为 `^T[A-Z]{2}\d+$`（新格式如 `TAG0001`），`check-changelog.sh` 去短前缀提取（直接匹配完整 task_id），以及协议文档里的 task_id 示例同步。完成本次后 P4 全部 4 个流结束，进入 C8 评审 + 最终 gate。

### 约束

1. **范围锁定为流 D，允许改动的文件（且仅这些）**：
   - `agate/scripts/agate-state-yaml-check.py`（约第 39 行，task_id 正则）
   - `agate/scripts/check-changelog.sh`（约第 14 行，去短前缀提取）
   - **全库 grep 核对下游消费点**：`agate-summary.sh`、`active-tasks.md` 相关脚本、`check-changelog.sh` 之外其他若有用 `T[0-9]+`/`grep -oE 'T[0-9]+'` 这类"提取任务短号"模式的地方，都要同步改成直接匹配完整 task_id——**先 grep 全库确认范围，再动手改**，不要漏改也不要过度改（只改"提取任务短号"这个具体模式，不要碰其他无关的 `T[0-9]+` 用法，比如 phases 字段里的 `P\d+` 或注释里举例用的 T001 字符串，那些是示例文本不是提取逻辑）
   - `agate/assets/templates/active-tasks-template.md`（第 4 条规则，编号规则说明文字）
   - `agate/state-machine.md`、`agate/dispatch-protocol.md`、`agate/role-system.md`（task_id 示例从 `T001` 风格改为新格式示例，如 `TAG0001`——**只改举例文本，不改这些文件里的其他内容**）
   - **不改**：`agate/scripts/agate-md-field-get.py`、`agate/scripts/agate-frontmatter-check.py`、`check-frontmatter.sh`、`check-gate.sh`、`check-p6-*.sh`、`check-scope-resolved.sh`（流 A/B/C 已完成，与流 D 无关）
   - **不改**：`agate/tests/**`（测试已由 P3 test-designer 写好并 commit；发现测试有 bug 标 `[SCOPE+]`，不要私自改）
   - **绝对不要碰**：`docs/tasks/T001-v2.0-structured/` 下任何本任务自身的产出文件（`.state.yaml`/`P0-brief.md`/`P1-requirements.md` 等）——**本任务自身编号 T001 不受影响**，全程按 v0.35 旧格式跑 gate 直到发布（BDD-28 自举边界，P0-brief 已定）。你改的新校验器会拒绝 `T001` 这种格式，但那是**未来任务**的事，不影响本任务——本任务的 gate 校验一直走 `~/.agate`（v0.35 稳定版，未受此次改造影响），不是你改的这份 worktree 内代码。
2. **实现依据是 P2-design.md §3.4（3.4.1-3.4.3）**，改动内容已经定死，照做。
3. **硬切，不做双格式兼容**（F19，P0-brief 已定）：新校验器**只认新格式** `^T[A-Z]{2}\d+$`，旧格式 `T001` 类必须被拒绝，不要写成"两种格式都接受"的兼容逻辑——这是本流唯一一处和其他三个流"双读兼容"原则不同的地方，故意如此，不是疏漏。
4. **check-changelog.sh 改动要点**：把 `TASK_ID_SHORT=$(echo "$TASK_ID" | grep -oE 'T[0-9]+' | head -1)` 改为 `TASK_ID_SHORT="$TASK_ID"`（直接用完整 task_id，不再截取短前缀）。确认下游两处匹配逻辑在改动后仍正确：`grep -qE "(^|[^0-9])${TASK_ID_SHORT}( |:|$|,|-)"` 对 `TAG0001` 这种"字母+数字"完整 id 仍能正确加边界；`grep -qF "$TASK_ID"` fallback 保留不动。
5. **验收目标**：`docs/tasks/T001-v2.0-structured/P3-test-cases.md` §5"流 D"表里标"**红**"的用例必须转绿：`SY.1`（`agate-state-yaml-check.bats`，前半段 `TAG0001` 应通过、后半段 `T001` 应报错）、`CL.6`/`CL.7`/`CL.8`（`check-changelog.bats`，全部重写为 `TAG0001` 场景）。**流 A/B/C 已转绿的用例必须继续保持绿**——尤其注意 `agate-state-yaml-check.bats` 里除 `SY.1` 外的其他用例、以及 `check-changelog.bats` 里除 `CL.6/7/8` 外的其他用例不能被你的正则改动破坏。
6. **自查用命令**（不是 gate；我会独立重跑验证）：
   ```
   cd /home/kity/oclab/agate/.worktrees/v2.0
   bats agate/tests/unit/agate-state-yaml-check.bats agate/tests/unit/check-changelog.bats
   ```
   另外自己跑一遍全量 `bats agate/tests/unit/ agate/tests/regression/`，确认这是流 D 完成后**全部 594 个用例应该全绿**（这是四个流里唯一一个"完成后本地红灯应该清零"的流——前三个流完成时还有后续流的红灯没处理，这次是最后一个）。
7. **CHECK 9 锚点表**：`agate-state-yaml-check.py`（task_id 锚点）、`check-changelog.sh`（CHANGELOG 锚点）已在 CHECK 9 锚点表里有条目（流 A 未新增这两个的锚点，它们是既有条目）——确认你的改动没有让这两个既有锚点的关键词消失（比如如果你把变量名/关键提示语整个改掉，可能导致锚点关键词匹配不上）。跑 `python3 agate/scripts/check-protocol-consistency.py` 自查一下 CHECK 9 仍是 0 ERROR。
8. **生产环境隔离**：不适用。
9. **追加产出 `docs/tasks/T001-v2.0-structured/P4-implementation.md` 的"## 流 D"小节**（追加，不覆盖已有"## 流 A/B/C"小节）。这是本文件最后一节，追加完之后这份 P4-implementation.md 就是 P4 阶段的完整交付记录了。发现设计外必须做的改动标 `[SCOPE+]`；发现设计要求的做法有问题，用 `[DESIGN_GAP: 描述 + 判断依据]` 标记声明，不要自己决定跳过。

### 上游关联

- P2-design.md §3.4 全节是本次唯一设计依据。
- P3-test-cases.md §5"流 D"表是验收清单。
- 流 A/B/C 均已交付且相互独立（P3-test-cases.md §6 已确认流 D 红灯"只依赖 `agate-state-yaml-check.py:39` 正则 + `check-changelog.sh:14` 短前缀提取两处局部改动，与流 A/B/C 完全独立"）——本次不依赖前三流的任何代码，但同一份 P4-implementation.md 文件已有三个小节，注意追加方式。

### 输入文件（自己读）

- `agate/assets/execution-roles/implementer.md`（角色定义）
- `docs/tasks/T001-v2.0-structured/P2-design.md` §3.4 全节
- `docs/tasks/T001-v2.0-structured/P3-test-cases.md` §5（流 D 验收清单）
- `docs/tasks/T001-v2.0-structured/P4-implementation.md`（流 A/B/C 已交付内容，了解追加格式惯例）
- `agate/scripts/agate-state-yaml-check.py`（当前 task_id 正则位置）
- `agate/scripts/check-changelog.sh`（当前短前缀提取逻辑）
- `agate/assets/templates/active-tasks-template.md`
- `agate/state-machine.md` / `dispatch-protocol.md` / `role-system.md`（task_id 示例位置，自己 grep `T001\|T0[0-9][0-9]` 定位）
- `agate/tests/unit/agate-state-yaml-check.bats`（`SY.1` 用例，确认正则的确切期望）
- `agate/tests/unit/check-changelog.bats`（`CL.6`/`CL.7`/`CL.8` 用例，确认边界匹配的确切期望）
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
- 环境状态：worktree `feat/v2.0`，`.state.yaml` phase=P4 status=active。流 A commit 3754e9d，流 B commit ebda17e，流 C commit 901f61d（`git log --oneline -8` 可查）。流 C 独立验证：594 用例、4 个预期流D红灯（本次要处理的正是这 4 个）、0 意外回归、CHECK9 0 ERROR、shellcheck 干净。
- 完成流 D 后，`bats agate/tests/unit/ agate/tests/regression/` 应该是 516/516 全绿（0 个 not ok）——这是判断流 D 是否真正完成的直接信号。
- 本任务自身（T001）的 gate 校验全程用 `~/.agate`（主 checkout，v0.35.0，不受本次任务任何改动影响），不用你正在改的 worktree 内脚本——所以你改的新校验器拒绝 `T001` 格式，不会影响本任务自身的 commit/gate 流程。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
