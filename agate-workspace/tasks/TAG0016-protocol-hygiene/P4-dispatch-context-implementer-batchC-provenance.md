---
phase: P4
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0016
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

实现 P2-design.md `dispatch_plan` 第 3 批次（最后一批）**`test-evidence-provenance`**
（RM-AG0026 测试重跑审计与跨阶段证据引用，complexity: medium，与批次 1/2 文件不重叠，本批次
独立）：M16-M23，对应 BDD-11~19。这是本任务实现阶段的最后一批，完成后进入全批次汇总 + 一次性
protocol-alignment-review + P4-review（C8 评审）。

### 约束（对照 P2-design.md §1.1 逐条，具体内容自己读表格，这里只强调关键点）

1. **M16：`dispatch-protocol.md` 新增「## 全量重跑点审计」小节**（建议插入位置：「派发编排机制」
   节之前）。内容直接誊写 P2-design.md §10「全量重跑点审计表（BDD-11 落点内容预览）」的四行表格
   （P5 首跑/P5 失败重跑/P6 refactor regression/P8 bump-version 重跑），P2 已经给出可直接誊写的
   完整内容，不要重新设计表格结构。
2. **M17：`check-p6-provenance.py` 新增审计 7**（`audit7_p5_evidence_reuse`，对应 BDD-12/13）。
   实现依据是 P2-design.md §3.5 的伪代码 + §3.2「边界条件与残余风险（修复轮补充）」的 R9 缓解
   措施说明。函数契约（三态返回值 `no_reuse_claim_possible`/`reuse_blocked`/`reuse_allowed`）
   已在 P3 测试里被断言，必须精确匹配这三个字符串。`EXCLUDE_PRODUCE_PREFIX =
   "agate-workspace/tasks/"` 前缀已经过 P2 minimal_validation 真实 git 命令验证，直接复用。
   注意 P3 测试用例用真实 git 仓库（conftest `GitRepo` fixture）构造 commit 历史，不是 mock
   subprocess——你的实现要跑真实 `git diff <commit>..HEAD --name-only`，不要用 mock 数据绕过。
3. **M18**：M17 对应的测试已在 P3 阶段写好（`test_check_p6_provenance.py` 4 条：
   `test_bdd_12_audit7_no_changes_reuse_allowed` / `test_bdd_13_audit7_non_produce_change_reuse_blocked`
   / `test_bdd_12_audit7_missing_field_no_reuse_claim_possible` /
   `test_bdd_13_audit7_only_produce_dirs_excluded_active_tasks_board`），本批次让它们变绿，不新写
   测试、不改测试断言。
4. **M19：`.state.yaml` schema 文档落点**——在 `agate/state-machine.md`「每任务独立状态文件」
   小节的 YAML 样例里补充 `p5_pass_commit`（可选字段）的文档说明（字段可选、缺失回退强制重跑，
   P2 §3.4 已给出确切措辞）。**这是文档补充，不是脚本改动**——`agate-state-yaml-check.py`
   已确认不需要改（P2 minimal_validation 已验证该脚本无 unknown-field 拒绝）。
5. **M20：`agate/phase-cards/P5-verification.md` 写入点**——在「如果是首次进入本阶段」步骤
   4-5 之间插入一句：主 Agent 在 `git add` 前先 `git rev-parse HEAD` 取父提交哈希，写入
   `.state.yaml` 的 `p5_pass_commit` 字段（P2 §3.4 已给出确切写入时机说明）。**同时按 P2
   §3.2 修复轮补充**，附近要写明"P5 commit 不得混入非产出文件改动，若发现顺手修复的必要性，
   应先回 P4 走正常流程，不要混入 P5 commit"这条操作纪律（R9 缓解措施，不能漏掉，这是
   plan-eng-review 第一轮阻塞项修复方案的一部分，属于本任务已承诺的交付物）。
6. **M21：`agate/phase-cards/P6-acceptance.md` 新增"引用 P5 证据、不重跑"分支**——含产出规格
   变化 + gate 规则更新（含审计 7 的门槛描述）。这是 BDD-12/13 在流程层面的落地，具体措辞你按
   P2 §3.5 审计 7 的判定逻辑（无改动→允许引用 P5-test-results/ 路径而不产出独立 regression.log；
   有改动→仍要求独立 regression.log）撰写清楚的操作步骤。
7. **M22：`agate/phase-cards/P8-release.md` 精简重跑表述**——把"主 Agent 必须亲自执行……重跑
   P5 gate"一条改为条件化表述（P2 §1.1 M22 已给出确切措辞："若 BDD-12 无改动校验判定 P8 发起
   时点距 P5 通过点无代码改动 → 复用同一份 P5-test-results/（不重新执行命令）；否则完整重跑
   gate_commands.P5"）。这条不能被理解成"取消这道验证"——保留"至少一次客观验证动作"的底线。
8. **M23：`.github/workflows/protocol-tests.yml` 新增 xdist 观测步骤**（不影响门禁结果）。
   在 pytest job 里新增一步 `pytest -n auto agate/tests/` 记录耗时到 job 日志，**不设置为影响
   job exit code 的判据**（BDD-15 硬约束：本地/CI 都不得把这步的结果当作"已验证加速"的判据，
   这一步纯粹是留痕耗时数字）。需要先确认 CI 环境是否已安装 `pytest-xdist`（若未声明依赖，
   本步骤应加 `continue-on-error: true` 或在依赖安装步骤里补充 `pytest-xdist`，避免因缺依赖
   导致这个"仅观测"步骤本身报错产生噪音——但报错也不能影响 job 整体 exit code，用
   `continue-on-error: true` 是最简单稳妥的做法）。
9. **必须让以下测试变绿**：
   - `test_check_p6_provenance.py` 4 条（审计 7）
   - `test_protocol_dedup_audit.py` 里 BDD-11/BDD-14/BDD-15 共 3 条
   - 全部让这 7 条从红变绿，测试代码本身不改动
10. **不涉及批次 1/2 已完成的文件**（`agate/WORKFLOW.md`/`dispatch-protocol.md`「平台适配」等/
    `check-protocol-consistency.py` 已不需要再动）——dispatch-protocol.md 你只新增 M16 小节，
    不要动批次1已经改过的其他部分。
11. **P3 已知问题（DEBT0010）**：`agate/scripts/agate-read-gate-commands.py` 有个把
    `P3_timeout_seconds` 误判为待执行命令的既有 bug（已登记 DEBT0010）。批次2 implementer
    判断不属于自己范围未修。**本批次同样不要求修复**（超出 M16-M23 范围），除非你判断这个 bug
    与你正在做的 provenance/gate 相关脚本改动有直接交集——大概率没有交集，正常情况下忽略即可。

### 上游关联

批次 1（doc-dedup）HEAD 9b0ee79、批次 2（check12）HEAD b3784b0 均已完成并 commit。全量 pytest
当前 8 failed / 951 passed / 2 skipped，8 个失败全部是本批次范围（+ 1 个与本批次无关的既有
ruff lint 问题，不要求本批次修复）。

### 输入文件

- {AGATE_WORKSPACE}/tasks/TAG0016-protocol-hygiene/P2-design.md（§1.1 M16-M23、§3 BDD-12/13
  完整设计含 §3.2 修复轮补充的 R9 缓解措施、§10 全量重跑点审计表内容、§1.3 风险表）
- agate/scripts/check-p6-provenance.py（现有六道审计实现风格，M17 新增审计 7 需遵循同一风格：
  `sys.stderr.write` + `sys.exit` 语义）
- agate/tests/unit/test_check_p6_provenance.py（4 条 audit7 相关测试的确切断言 + conftest
  `GitRepo` fixture 用法）
- agate/tests/unit/test_protocol_dedup_audit.py（BDD-11/14/15 三条测试的确切断言）
- agate/dispatch-protocol.md（M16 插入点：「派发编排机制」节之前）
- agate/state-machine.md（M19 插入点：「每任务独立状态文件」小节 YAML 样例）
- agate/phase-cards/P5-verification.md（M20 插入点：「如果是首次进入本阶段」步骤 4-5 之间）
- agate/phase-cards/P6-acceptance.md（M21 落点）
- agate/phase-cards/P8-release.md（M22 落点：「主 Agent 必须亲自执行」重跑 P5 一条）
- .github/workflows/protocol-tests.yml（M23 落点：pytest job 结构）

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
- worktree HEAD：b3784b0（批次 1+2 已 commit），工作区干净。
- 全量 pytest：8 failed / 951 passed / 2 skipped。本批次完成后目标：0 failed（不含既有
  ruff lint 问题——该问题独立于本批次，若你顺手能低成本修复也可以，但不是本批次门槛）。
</objective_info>
