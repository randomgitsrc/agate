---
phase: P4
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0026
role: review
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

独立评审 P4 实现（M1-M8 落地），产出 `P4-review.md`：判定 approved / rejected /
needs-revision，只审不改。你是单评审角色（C8 映射：backend → review；risk=high 实现
评审不可省），直接产出 P4-review.md。Header `agent: review`（≠main，硬要求）。

### 约束

1. **只审不写**：不得修改实现与测试文件；发现问题写进 P4-review.md，交主 Agent 回派
   implementer 修改。
2. **重点核查项（本任务特有，逐条核查并给锚点）**：
   - **返回约定兼容（最高风险）**：读 check-gate.py gate_p4 现体，核对新步骤（三重门槛）
     是否只产生 return 1 或继续向下、未新增 return 2；三种跳过场景（violations 为空 /
     检测未部署 ImportError / git_ok False）是否与改动前行为一致；挂载点是否在④步之后、
     骨架 WARNING 之前；门槛 c 是否复用既有①②③（未重复实现）
   - **挂载处注释字面 `check-maintainability.py`**（R6：callers 字面 basename 校验）
   - **检测器契约**（对照 P2-design §3.1 与 P1 BDD）：dict 四键；violation 条目键；
     before/after 行数计算（git show HEAD: / git show :path，A/M 过滤跳 D）；fuzzy 只取
     新增行、行号取 @@ c 列、按扩展名路由；_norm_rel 单源；配置全兜底（缺失/坏值用默认，
     BDD-6）；CLI exit 0/1 语义
   - **M3/M4 一致性配套**：SCRIPT_ALIGNMENT_ANCHORS 锚点登记（keywords/callers）+
     _DRIFT_SCRIPTS 追加——实测跑 worktree 的
     `python3 agate/scripts/check-protocol-consistency.py --strict-errors-only` 应 0 ERROR
   - **模板（M5）**：与 known-failures-template 语义反转正确；样例行首 `| # |`（R8）；
     「P4 评审确认」列不参与机械计数
   - **卡片改动（M6/M7）**：P4 卡评审 checklist + gate 规则 exit 1 条目；P6 卡自查提醒
     （非阻断）——措辞与实际 gate 行为严格对应（协议-实现一致性）
   - **DESIGN_GAP 处理**（P4-implementation.md §3.1）：连字符文件名 import 兜底是否为
     正确解法（对照 agate-risk-score _load_script 机制）；是否留档合规
   - **测试修复授权范围**（P4-progress + §3.2）：主 Agent 授权只修"探测路径/机械笔误/
     场景构造"，断言语义与实现零改动——核对测试 diff 是否越权（改断言凑绿 = BLOCKER）
   - **自查证据**：27 passed（两文件）+ 182 passed（test_check_gate.py 回归）+ ruff 0 error
     ——主 Agent 已独立复核过这三个数字，评审时抽查关键断言与实现对应关系即可
   - **SCOPE+**：P4-implementation.md 声明"无 [SCOPE+]"——核对实现是否严格限于 M1-M8
3. **实质锚点要求**：结论必须引用具体锚点（文件:行号 / BDD 编号 / 用例名）。
4. **DEBT 格式强制**：若提"后续应重构/架构债"，给标准 DEBT 条目内容（evidence 必填）。

### 上游关联

- P1-requirements.md（13 BDD）/ P2-design.md（契约与 M 清单）/ P2-review.md（锁定决策）
- P3 测试（27 用例 = 实现的机器可执行规格）/ P4-implementation.md（实现自述 + 申报）
- P4-progress.md（修复轨迹：探测路径缺陷 → 三类定因 → NameError 收尾）

### 输入文件（按顺序读）

1. `agate-workspace/tasks/TAG0026-maintainability-gate/P4-implementation.md`（评审对象）
2. `agate-workspace/tasks/TAG0026-maintainability-gate/P2-design.md`（§1/§3 契约）
3. `agate-workspace/tasks/TAG0026-maintainability-gate/P1-requirements.md`（BDD 对照）
4. `agate/scripts/check-maintainability.py`（M1 实现全文）
5. `agate/scripts/check-gate.py`（gate_p4 现体 + import 区，对照 P2-review 实测锚点
   :25-58 / :870-927 / :930-985）
6. `agate/scripts/check-protocol-consistency.py`（锚点登记处）
7. `agate/scripts/agate-summary.py`（_DRIFT_SCRIPTS）
8. `agate/assets/templates/known-violations-template.md`
9. `agate/phase-cards/P4-implementation.md` / `P6-acceptance.md`（改动处）
10. `agate/tests/unit/test_check_maintainability.py` +
    `test_check_gate_p4_maintainability.py`（抽查断言-实现对应）
11. `AGENTS.md`

### 产出文件字段

用 `FILE={AGATE_WORKSPACE}/tasks/TAG0026-maintainability-gate/P4-review.md agate-md-field-set --list`
查看字段；逐个写入；不要手写 frontmatter。Header 关键字段：`status`（评审后
approved/rejected/needs-revision）、`agent: review`、`phase: P4`、`task_id: TAG0026`。
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

<objective_info>
### 客观查证信息（主 Agent 已独立复核的事实）
- **测试终态**（主 Agent 实跑）：`pytest test_check_maintainability.py
  test_check_gate_p4_maintainability.py -q` → **27 passed**；
  `pytest test_check_gate.py -q` → **182 passed**；ruff（~/.venvs/agate-dev/bin/ruff）0 error
- **修复轨迹**：P3 测试探测路径少算一级 parent（13 sentinel failed + 14 skipif skipped）→
  主 Agent 定夺授权修探测机制（断言语义不动）→ 三类定因（cwd 根因/机械笔误/场景机制）→
  最终 7 个失败同根因 = `_repo_with_staged` 返回改名 `_td` 后 6 处使用点漏改的 NameError →
  修正后 27/27。全程记录在 P4-progress.md
- **DESIGN_GAP**（P4-implementation.md §3.1）：check-maintainability.py 连字符文件名 vs
  裸 import 模块名——实现侧已在 except 内加 importlib 按路径加载兜底（_load_script 同源
  机制），保留 try/except 形态；182 回归验证。主 Agent 已采纳留档
- **实现自述**：M1-M8 全落地、无 [SCOPE+]（严格限 M1-M8）、未改 conftest / P3 断言 /
  gate_p4 既有四步 / check-p6-provenance.py / WORKFLOW.md / rules/*.yaml
- **环境**：worktree dogfooding；git 写操作全程由主 Agent 执行；ruff 锁 0.16.4
  （~/.venvs/agate-dev/bin/ruff）
- **已知债务**：DEBT0023（P3* 键收集，P2 登记在案，与本实现无关但 gate_commands 不得声明
  P3_xxx 键——已遵守）
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
