# P4-dispatch-context-review — TAG0023 实现评审

> 派发对象：review（P4 实现评审，偏执 Staff Engineer 视角）。这是本轮的强制指令，不是参考信息。
> 任务目录：`{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/`
> 触发依据（C8 机械映射）：`domains: [backend]` → review；`risk_level: high` → P4 实现评审不可省（同一角色，去重只派 1 个）。单评审角色，无需组长汇总，产出直接写 `P4-review.md`。

## 目标

独立评审 4 批实现（`agate/scripts/check-state-transition.py`/`check-gate.py`/`check-debt.py`/`agate-frontmatter-check.py` + `dispatch-prompt.md` + 3 个协议文档措辞同步 + roadmap.md 数据补记 + CI 配置），产出 `P4-review.md`，结论 approved/rejected。

## 约束（按角色文件「评审流程」逐项审）

**Pass 1（CRITICAL）**：
- 新增的正则/字符串匹配逻辑有没有边界条件漏洞（如 batch A 的 `_BDD1_REVIEW_RETRY_RE`/`_BDD3_EMPTY_RETURN_KEYWORDS` 扫描、batch B 的 roadmap 表格解析、batch C 的 `_short_hash()`）
- 状态读取（`.state.yaml`/`roadmap.md`）有没有 TOCTOU 风险（读的时候和用的时候数据是否可能不一致）
- 新增函数的异常路径处理（文件不存在/解析失败/git 命令失败）是否会导致误报或漏报
- batch A 的 `old_retries_len>0` 守卫是 implementer 在实现过程中发现的 DESIGN_GAP（P2-design.md 原文字面表述未显式要求这个守卫），检查这个修正是否合理，有没有引入新的漏判

**Pass 2（代码健康）**：
- batch B 的 `_check_roadmap_done()` 解析 `roadmap.md` 表格是否用了脆弱的字符串分割（如简单 `.split("|")` 对表格分隔符行/表头行是否有防护）
- batch C 保留 `full` 全量兜底比对 + 新增动态 `_short_hash()` 是否有重复计算/性能问题（非阻塞项可提但不应是 BLOCKER）
- batch D 的错误消息增强是否可能意外改变了其他依赖旧错误文案的调用方行为（搜索是否有代码/测试断言旧文案的精确匹配）

## 关键决策核实（不是走过场，需要实际读代码验证）

1. **H3/D4 分批边界是否真的没有交叉**：核实 batch A（check-state-transition.py + 4 个文档）与 batch B（check-gate.py + roadmap.md）确实没有改动同一文件
2. **RM-AG0032 时序调整决策**（见 `P4-implementation.md`「编排决策记录」）：这是主 Agent 的编排层面决策（不等 P8，提前到 P4 补记），检查这个决策的理由是否站得住、是否真的不构成 BDD 语义变更（只是执行时机提前）
3. **BDD-1 校验强度 WARNING**（batch A 实现）：核实代码确实是 `sys.stderr.write` + 不 `sys.exit(1)`，不是误把 WARNING 实现成阻断
4. **check-state-transition.py 新增的"检查3"是否可能与既有检查1/2/4 产生交互副作用**（如检查3 的 WARNING 输出会不会影响检查1/2/4 的 exit code 判定——应该不会，因为 WARNING 分支不调用 sys.exit，但请验证）

## 上游关联

- `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P4-implementation.md`（本次实现总结 + 编排决策记录）
- `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P2-design.md`（方案设计，核对实现是否偏离设计）
- `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P1-requirements.md`（BDD 原文）
- `{agate_root}/assets/review-roles/review.md`（角色定义）

## 输入文件（按批次读，每读完一批追加 progress）

1. `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P4-implementation.md`
2. `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P2-design.md`（§2.1~2.4 + §4 完成标准表）
3. `git diff HEAD -- agate/scripts/check-state-transition.py agate/rules/state-transitions.md agate/state-machine.md agate/dispatch-protocol.md agate/WORKFLOW.md`（batch A 全部 diff）
4. `git diff HEAD -- agate/scripts/check-gate.py agate-workspace/roadmap/roadmap.md`（batch B 全部 diff）
5. `git diff HEAD -- agate/scripts/check-debt.py .github/workflows/protocol-tests.yml`（batch C 全部 diff）+ `agate/tests/ENV-SENSITIVE-TESTS.md`（新文件全文）
6. `git diff HEAD -- agate/assets/templates/dispatch-prompt.md agate/scripts/agate-frontmatter-check.py`（batch D 全部 diff）
7. 按需核对测试文件（不评审测试本身，只用于理解验收契约）：`agate/tests/unit/test_check_state_transition.py`（L495-713）、`agate/tests/unit/test_check_gate.py`（L1531-1580）、`agate/tests/unit/test_agate_debt_check.py`（L616-635）、`agate/tests/unit/test_check_frontmatter.py`（L405-483）

## 验证命令（可自行复核，非强制重跑）

```bash
python3 -m pytest agate/tests/ -q -p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp_review
```
主 Agent 已独立确认：1234 passed, 2 skipped（较 P3 基线净增 10，全部转绿，无回归）；ruff/consistency 均通过。

## 产出

`{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P4-review.md`

Header（`---` 分隔，不用代码围栏）：
```
---
phase: P4
task_id: TAG0023-mechanism-checks
type: review
parent: P4-implementation.md
trace_id: TAG0023-P4-review-20260825
status: <approved|rejected>
created: 2026-08-25
agent: review
---
```

按角色文件「输出格式」逐条列出 CRITICAL/INFORMATIONAL 发现（无则写"无"），结论三选一映射：approved（无 CRITICAL/BLOCKER）/ rejected（有 CRITICAL 或 BLOCKER）/ needs-revision（需补充但非阻断）。

## 门槛

- P4-review.md 存在且非空，status 明确
- 引用具体文件/行号的发现（无发现也要写"无"，不能裸 approved）
- agent 字段为 review（非 main）

## 返回给我

只返回两行：① 产出文件路径；② 一句话摘要（结论 + 若非approved则含核心理由，≤40字）。绝不返回文件全文。

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
