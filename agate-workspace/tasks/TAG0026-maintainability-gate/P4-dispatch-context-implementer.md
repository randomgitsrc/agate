---
phase: P4
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0026
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

按 P2-design.md 选定方案（候选 A）实现 TAG0026 维护性反模式 gate，使 P3 的 27 条红灯
测试转绿。改动清单以 P2-design.md §1.1（M1-M10）为准：

- M1 新增 `agate/scripts/check-maintainability.py`（检测器，§3.1 契约）
- M2 修改 `agate/scripts/check-gate.py`（gate_p4 三重门槛挂载，§3.2；import 兜底区 :25-58 同型）
- M3 修改 `agate/scripts/check-protocol-consistency.py`（SCRIPT_ALIGNMENT_ANCHORS 登记锚点，
  §3.6 / R6：gate_p4 挂载处注释必须含字面 `check-maintainability.py`）
- M4 修改 `agate/scripts/agate-summary.py`（_DRIFT_SCRIPTS 追加一行）
- M5 新增 `agate/assets/templates/known-violations-template.md`（§3.3 完整内容）
- M6 修改 `agate/phase-cards/P4-implementation.md`（评审 checklist + gate 规则 exit 1 条目，§3.4）
- M7 修改 `agate/phase-cards/P6-acceptance.md`（自查≠gate 节复跑提醒，§3.4）
- M8 新增 `agate-workspace/maintainability.yaml`（§3.5 示例配置）
- 测试文件（P3 已交付，勿动）：`agate/tests/unit/test_check_maintainability.py` +
  `agate/tests/unit/test_check_gate_p4_maintainability.py`

产出还包括 `P4-implementation.md`（声明 implementation_dir + 实现说明）。

### 约束

1. **TDD 驱动**：实现以 P3 测试为准——实现完成后两个测试文件全绿。不得修改 P3 测试文件的
   断言语义；若发现测试与 P2 契约矛盾，停下报告主 Agent（不得自行改测试凑绿）。
2. **实现范围严格 = P2-design §1.1 M1-M8**：不做任何"顺手改进"（§1.2 不改什么清单逐条遵守：
   不动 gate_p4 既有四步语义与顺序、不动 check-p6-provenance.py、不动 gate_p5 判定、
   不动调用方、不动 ruff 配置、不动 known-failures-template、不动 WORKFLOW.md/rules/*.yaml）。
   发现范围外需求 → P4-implementation.md 标 `[SCOPE+]`（行首声明格式），不直接做。
3. **返回约定兼容（最高风险，P2-review 锁定决策）**：gate_p4 新步骤只产生 return 1（门槛
   a/b 失败）或继续向下；不新增 return 2；violations 为空 / 检测未部署 / git_ok False 三种
   跳过场景下 gate_p4 行为与改动前完全一致。挂载点在④步（:905）之后、骨架 WARNING（:907）
   之前；门槛 c 不重复实现（能走到新步骤即评审检查已过）。
4. **R6 对策必须落实**：gate_p4 挂载处代码注释必须含字面 `check-maintainability.py`
   （callers 字面 basename 校验）；M3 锚点登记的 keywords 至少含 `god_file_count` /
   `fuzzy_boundary_count`（检测器返回 dict 真实键）。
5. **R8**：模板样例行首用 `| # |`（不命中 count_kf_entries 正则）；「P4 评审确认」列不参与
   机械计数。
6. **R2 import 降级**：check-gate.py 侧 `try: from check_maintainability import ...` /
   `except ImportError: None`（:32-41 先例同型）；检测器侧复用链
   `from agate_common import run_git, count_kf_entries` 同样带降级兜底；
   `_load_script("agate-risk-score")` 取 `_norm_rel`（importlib 模式，:46-54 同源）。
7. **平台无关**：路径归一化全部经 `_norm_rel` 单源；不硬编码绝对路径；CLI shebang 与
   解释器探测遵守项目先例（读 agate-risk-score.py 的 main/CLI 形态照做）。
8. **配置读取健壮（BDD-6）**：配置文件缺失 / yaml 不可导入 / 单键缺失 / 单键类型坏 →
   该键用默认值，不抛错不静默跳过（stderr 提示可）。
9. **god-file 行数计算（P2-review 实测锚点）**：before = `git show HEAD:{path}` 行数
   （新增文件 / HEAD 不存在 → 0）；after = `git show :{path}` 行数（staged 版本）；
   `git diff --cached --name-status` 只处理 A/M，跳过 D。
10. **fuzzy-boundary（P2 §3.1）**：`git diff --cached -U0 -- {path}`，只取 `+` 前缀且非
    `+++` 行；行号取 `@@ -a,b +c,d @@` 的 c 列；按扩展名路由正则组（.py → python 组；
    .ts/.tsx/.js/.jsx → typescript 组；其它扩展名不做 fuzzy 只做 god-file）。
11. **卡片 wording（M6/M7）**：措辞含字面 `check-maintainability.py` 脚本名（防 CHECK 10
    引用漂移）；M6 两处落点（评审派发节 checklist + gate 规则节 exit 1 条目）与 M7 一处
    落点见 P2 §3.4。
12. **commit 纪律**：你不做 git commit——主 Agent 统一暂存与提交。你不要跑
    `git add` / `git commit`（worktree 仓库写操作由主 Agent 执行）。
13. **自查**：实现完成后自跑（自查 ≠ gate）：
    `python3 -m pytest agate/tests/unit/test_check_maintainability.py agate/tests/unit/test_check_gate_p4_maintainability.py -x -q`
    全绿；再跑完整两个文件不带 -x 确认 27 条全过。P3 的 skipif/sentinel 机制在实现落地后
    自动解除（M9 整组参与、M10 sentinel 探测到 gate_p4 已含三重门槛）——不要改测试里的
    机制，若 sentinel 探测逻辑与你的实现形态不匹配（例如探测字符串），报告主 Agent。
14. **self-gate 预告**：本次改动含 `agate/scripts/*.py` 与 `agate/phase-cards/*.md`——
    主 Agent commit 时会带 self-gate-review 流程（你不处理，但你须保证实现与协议文档
    一致性：卡片新增 wording 与实际 gate 行为严格对应）。

### 上游关联

- P1-requirements.md：13 条 BDD（实现验收对照）
- P2-design.md：§1 影响面 / §2 候选A / §3 设计细节（含模板全文、gate_commands）/ §6 files_to_read
- P2-review.md：实测锚点（:254-271 评审依据汇总）+ 4 非阻塞 + 2 测试建议
- P3 测试文件：27 条用例（红灯语义即实现规格）

### 输入文件（按 P2 files_to_read 清单为准，重点）

1. `agate-workspace/tasks/TAG0026-maintainability-gate/P2-design.md`（全文，尤其 §3/§6）
2. `agate-workspace/tasks/TAG0026-maintainability-gate/P3-test-cases.md`（测试规格）
3. `agate/scripts/check-gate.py`（:25-58 / :174 / :870-927 / :930-985）
4. `agate/scripts/agate-risk-score.py`（:41-59 / :86-88 / :202-229）
5. `agate/scripts/agate_common.py`（:1015-1017 count_kf_entries；run_git 定义处自行 grep）
6. `agate/scripts/check-protocol-consistency.py`（:697-830 锚点登记位 + callers 校验）
7. `agate/scripts/agate-summary.py`（:42-50 _DRIFT_SCRIPTS）
8. `agate/assets/templates/known-failures-template.md`（格式参照）
9. `agate/tests/unit/test_check_maintainability.py` + `test_check_gate_p4_maintainability.py`
   （实现规格的机器可执行形态）
10. `agate/phase-cards/P4-implementation.md` / `P6-acceptance.md`（改动落点上下文）

### 产出文件字段

P4-implementation.md 的 frontmatter 用 agate-md-field-set 填写（先 `--list`；报错照提示改；
不要手写 frontmatter；仍失败报告主 Agent）。关键字段：`phase: P4` / `task_id: TAG0026` /
`parent: P2-design.md` / `trace_id: TAG0026-P4-20260830` / `status: draft` /
`created: 2026-08-30` / `agent: implementer`；正文声明 `implementation_dir: agate/scripts/`
（实现落点）。
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
### A. 代码锚点（P2-review 实测汇总，:254-271 抄录）
- check-gate.py：import 兜底区 :32-41；`_STAGED_EXCLUDE_RE` :174；`_md_field_get` :230；
  gate_p4 :870-927（①:872-877 ②:879-883 ③:885-891 ④:893-905 ⑤:907-925 ⑥:927）
- agate-risk-score.py：`_load_script` :46-54、`_norm_rel` :86-88、`score_task` :202-229
- agate_common.py：`count_kf_entries` :1015-1017；`run_git` 自行 grep 定位
- check-protocol-consistency.py：SCRIPT_ALIGNMENT_ANCHORS 表尾 :745-751 之后；
  check_script_alignment（callers 字面 basename 校验）:771-785；GATE_SCRIPT_EXEMPT :791-794；
  check_anchor_coverage glob :807-811；CHECK 10 :841-846
- agate-summary.py：_DRIFT_SCRIPTS :42-50（现 7 项）
- agate-read-gate-commands.py :60：P3* 非元键全部被收集为测试命令（禁止声明 P3_xxx 键——
  已在 P2 gate_commands 落实，与你无关但勿破坏）

### B. P2-review 4 条非阻塞项（实现时知晓，不强制处理）
- R3 风险行笔误（文档措辞，非代码）
- 其余 3 条与 2 条测试建议已在 P3 测试中体现
- 详细内容见 P2-review.md 对应小节

### C. 测试与契约关键形态（P3 交付，实现必须匹配）
- M9 检测器测试用 `pytestmark` skipif 探测 `_MOD` 可 import——实现落地后自动解除
- M10 gate 测试用模块级 sentinel `_IMPLEMENTED = _maintainability_gate_implemented()`
  （收集期探测 gate_p4 是否已含三重门槛特征）——若你的实现措辞与其探测规则不匹配，
  报告主 Agent，不得改测试
- violation 条目键名严格：`type` / `file` / `detail`（god-file）；`type` / `file` / `line` /
  `detail`（fuzzy-boundary）——测试按此断言

### D. 环境事实
- worktree dogfooding：改代码在 worktree；git 写操作主 Agent 做；测试命令
  `python3 -m pytest`（worktree 根执行）
- ruff（自查建议）：`~/.venvs/agate-dev/bin/ruff check agate/scripts/`（CI 锁 0.16.4）
- 基线：全量 pytest 全绿 + count-tests 1308（2026-08-30）——新增 27 用例后 count-tests 应 +27
  （以脚本实测为准）
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
