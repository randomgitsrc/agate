---
phase: P4
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0021
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

实现 TAG0021「协议结构化层（RM-AG0022）」C1 方案（P2-design.md §3），让 P3 的 34 个红灯测试（6 个测试文件）全部变绿。按 P2 dispatch_plan **serial：M0 → M1 → M2 → M3**，每里程碑完成对应 BDD 的测试变绿后停一下（主 Agent 核查后派下一里程碑），**本次只做 {MILESTONE} 里程碑**。

### 里程碑-交付物映射（P2-design §3.5 里程碑清单）

- **M0（数据层就位，只加不改）**：`agate/rules/{phases,dispatch,roles}.yaml` + `agate/rules/schema/*.json` + `agate/scripts/check-structure-consistency.py`（S-1~S-6）+ `agate/scripts/check-yaml-schema.py` + WORKFLOW.md 阶段总览 S-1/S-2 锚点 → 变绿：test_check_yaml_schema.py（BDD-1）、test_check_structure_consistency.py（BDD-2/3/5）
- **M1（双跑对账）**：agate-read-gate-commands / check-pruning / check-gate 三脚本接入对账模式（读 YAML vs grep 结果，不一致 WARNING + 差异计数不阻断）→ 变绿：test_check_reconcile.py（BDD-6/7）
- **M2（切换权威源 + 阻断提升）**：三脚本切换读 YAML（含 agate-md-field-get 统一入口迁移消费方）、删除已迁移 grep 逻辑、check-structure-consistency 提升阻断 + pre-commit/CI 接入、fixture 同步构造、UPGRADING 章节 → 变绿：test_structure_migration.py（BDD-8/9/10）+ 回归（BDD-11）
- **M3（卡片渲染化）**：phase-cards 从 YAML 渲染（模板 + 数据）、agate-inject-card.py 改造（render_card）→ 变绿：test_card_render.py（BDD-12/13）+ 回归（BDD-14）
- 跨里程碑：BDD-15（count-tests 只增不减）/ BDD-16（平台无关）全程维护

### 上游输入（按序读取，每读完一个追加 progress）

1. {AGATE_WORKSPACE}/tasks/TAG0021-structured-layer/P2-design.md（C1 方案 §3.1-3.7 + files_to_read 导航 + gate_commands + dispatch_plan §5）
2. {AGATE_WORKSPACE}/tasks/TAG0021-structured-layer/P3-test-cases.md（1:1 映射表 + 测试代码路径 + test_code_dir）
3. {AGATE_WORKSPACE}/tasks/TAG0021-structured-layer/P2-review.md（非阻塞发现 1-5——实现期闭环）
4. {AGATE_WORKSPACE}/tasks/TAG0021-structured-layer/P0-brief.md（约束）
5. worktree 下既有测试代码 agate/tests/unit/（P3 新增 6 文件 + _rules_test_utils.py）

路径说明：{AGATE_WORKSPACE} = `/home/kity/oclab/agate/.worktrees/agate-TAG0021/agate-workspace`；{agate_root}（读卡片/角色/脚本） = `/home/kity/oclab/agate/agate`（= ~/.agate 稳定版）；改造对象（写代码）= worktree `/home/kity/oclab/agate/.worktrees/agate-TAG0021`。

### 实现硬约束

- **只实现 P2 C1 方案里的东西，不擅自扩大范围**；最小实现原则（写最简单代码让测试通过，不重构无关代码）
- **让 P3 红灯测试变绿，不改测试迁就实现**；测试断言与 P1 BDD 矛盾 → 标 `[DESIGN_GAP]` 不改测试
- **YAML 只承载可判定规则**（门槛/产出/状态转移/重试上限/角色映射）；叙事留 md
- **双工作区纪律**：读卡片/角色用 ~/.agate 稳定版；gate 用稳定版跑；改代码在 worktree；主 checkout 禁止改动
- **平台无关（BDD-16）**：新代码/测试不引入裸 python3、硬编码 PATH、/tmp、-L 软链假设、POSIX 语义假设
- **SELF-GATE 触发**：改动 agate/scripts/*.py + agate/**/*.md → commit 需 self-gate-review/skip（commit 由主 Agent 做，你在产出里按新增文件核对表登记）
- **代码规范**：set -euo pipefail（脚本）；Python 用 os.environ；grep -c || echo 0 后 | tail -1；utf-8 显式；py38 兼容（无 match/removeprefix）
- bash 一律外层 timeout（30-300s 按命令）；读文件优先 read/grep/glob 工具；单步串行不并行 bash

### 自查命令（每里程碑完成自查，非 gate）

```bash
python3 -m pytest agate/tests/unit/test_<本里程碑文件>.py -q -p no:cacheprovider --basetemp=/home/kity/oclab/agate/.worktrees/agate-TAG0021/dist/
# + 全量 pytest 回归（防跨文件破坏，M2/M3 必跑）
python3 -m pytest agate/tests/ -q -p no:cacheprovider --basetemp=/home/kity/oclab/agate/.worktrees/agate-TAG0021/dist/
```

### 产出

- 代码改动：worktree 下（agate/scripts/、agate/rules/、agate/phase-cards/、agate/WORKFLOW.md、agate/tests/ 等）
- `{AGATE_WORKSPACE}/tasks/TAG0021-structured-layer/P4-implementation.md`：**只写一次/每里程碑追加一节**（implementation_dir: agate/ + 本里程碑改动文件清单 + 变绿的测试 + [DESIGN_GAP]/[SCOPE+]/[CLARIFY] 声明 + 新增文件核对表）
- 状态标记：`[PROD_NOT_TOUCHED]`
- 分阶段落盘：`{AGATE_WORKSPACE}/tasks/TAG0021-structured-layer/P4-progress.md`

### 返回

只返回两行：① P4-implementation.md 路径（或本里程碑追加节）；② 一句话摘要（≤30 字，含本里程碑变绿用例数）。
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