# P4-dispatch-context-implementer-batchB-judge — TAG0022 B 批（RM-AG0039 judge 启用强制化）

> 派发对象：implementer（P4 实现，batch B-judge）。这是本轮的强制指令，不是参考信息。
> **时序约束：本批在 C-migration 批（含 agate-md-field-get 新 op 注册 + gate_p1 解析层重构）完成后派发；叠加于 C 重构后的基础。**
> 任务目录：`{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/`

## 目标

实现 **RM-AG0039（BDD-6/7）**：check-gate.py P1 分支新增 judge 校验（机制后新任务缺 `judge.enabled: true` → exit 1）+ state-machine.md / P1 卡文档面同步。**验收：P3 红测试转绿（judge P1 缺失/falsy exit 1）+ 历史任务不被拦 + 既有 gate_p65 三态用例保持绿。**

## B 批文件集（本批独占，不跨批写入）

1. `agate/scripts/check-gate.py` — gate_p1 新增 judge 校验块（**叠加于 C 重构后的 gate_p1**；仅 P1 分支，其他分支不动）
2. `agate/rules/dispatch.yaml` — 新增 `judge_required_since: "2026-08-22"`（ISO 字符串；YAML 权威判据）+ `agate/rules/schema/dispatch.schema.json` 同步
3. `agate/state-machine.md` — L442-443 judge 模板语义更新（「P1 初始化时主 Agent 写入；缺失/false = 历史任务」→「机制后新任务（P1 created ≥ judge_required_since）必须含 judge.enabled: true（check-gate P1 机械校验）；历史任务（created < 截止或未声明）缺块 → 跳过」）；P6.5 硬边界/早退语义（L153/155）不改
4. `agate/phase-cards/P1-requirements.md` — 产出规格 checklist 新增「judge 启用声明」条（kick 新任务 P1 初始化须写 judge.enabled: true）+ frontmatter 样例注释同步
5. `agate/tests/unit/test_check_gate.py` — P3 已写 judge P1 用例（7 例），本批使红转绿；如实现落点与契约有出入允许按契约微调

## judge 校验规格（P2 §4.3 + P2-review 锁定决策 2 + NB-4 + P3 契约注解 1）

gate_p1 新增逻辑（在既有 P1 判定流程中，建议放在 NEED_CONFIRM 检查附近）：
1. `judge = _load_state_yaml(task_dir).get("judge")`
2. `judge` 为 dict 且 `enabled` truthy → 放行（继续原 P1 判定，exit 2 语义不变）
3. `judge` 为 dict 且 enabled falsy → **读 P1 `created`**（agate-md-field-get `created` op）：created 为 ISO 日期且 ≥ judge_required_since → **exit 1**（「judge 已声明但未启用」）；pre-cutoff / created 缺失或非 ISO → 跳过（历史兼容，fail-open——NB-4 推荐口径）
4. `judge` 缺失 → 读 P1 `created`：created ISO 且 ≥ judge_required_since → **exit 1**（机制后新任务缺 judge 块）；否则 → 跳过（fail-open）
5. `judge` 非 dict（如 `judge: true` bool）→ 按缺失处理（fail-open）
6. `judge_required_since` 从 `read_rules_yaml(dispatch.yaml)` 读取（对齐 C 批的共享读取模式；C 批已建的规则读取路径）

**falsy 与缺失同走 created 判据（NB-4）**：本批的 7 个 P3 用例断言如下（不得与之矛盾）：
- created 2026-08-22 无 judge → exit 1（红转绿）
- created 2026-08-22 + judge.enabled true → exit 2（守卫，保持绿）
- created 2026-08-22 + judge.enabled false → exit 1（红转绿）
- created 2026-08-19 无 judge → exit 2（守卫）
- 无 created 无 judge → exit 2（守卫 fail-open）
- created 2026-08-19 + judge.enabled false → exit 2（守卫，NB-4 falsy pre-cutoff 跳过）
- judge: true（非 dict）+ 无 created → exit 2（守卫 fail-open）

## 约束（硬约束）

1. **只改 P1 分支**：check-gate.py 的 gate_p65 / P2/P3/P4/P5/P7/P8 分支与退出码语义不动（锁定决策 5：gate_p65/2i.1/ci-backstop 消费语义逐字节不变）
2. **C 批基础依赖**：agate-md-field-get 的 `created` op 由 C 批注册（`judge_required_since` 读取走 C 批的规则读取路径）——本批不再写 agate-md-field-get.py/agate_common.py
3. **文档面只改 state-machine L442-443 与 P1 卡**（M8/M9），P6 卡条文不改（N7）
4. **禁改范围外文件**：check-protocol-consistency.py / test_check_routing.py / test_env_adapt_docs.py / workflow / UPGRADING 章节本体 = A/D 批范围
5. **SELF-GATE**：本批触及 `agate/scripts/check-gate.py` + `agate/state-machine.md` + `agate/phase-cards/P1-requirements.md`（均为触发面）——commit message 由主 Agent 处理 self-gate 声明；你在 P4-implementation.md 记录触发面清单
6. 环境：Linux；/tmp 只读（pytest `--basetemp=/home/kity/oclab/dsh-workspace/ptmp -p no:cacheprovider`）；bash 一律 timeout；双工作区纪律

## 输入文件（读相关节，勿全仓扫描）

- `{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/P2-design.md`（§4.3 + §1.1 M7-M9 + §4.2.1 created op 行）
- `{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/P2-review.md`（锁定决策 2/5 + NB-4 + TG-2）
- `{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/P3-test-cases.md`（§5 契约注解 1 + §3 BDD-6/7 映射）
- 现状代码（C 批完成后）：`agate/scripts/check-gate.py`（gate_p1 + gate_p65 参照）+ `agate/scripts/agate_common.py`（read_rules_yaml）+ `agate/rules/dispatch.yaml` + `agate/state-machine.md` L440-448 + `agate/phase-cards/P1-requirements.md` + `agate/tests/unit/test_check_gate.py`

## 验证（自查≠gate）

- `python3 -m pytest agate/tests/unit/test_check_gate.py -q -p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp`（bash timeout）——judge P1 用例红转绿 + gate_p65 三态既有用例保绿
- `python3 agate/scripts/check-structure-consistency.py`（S-* 全绿，dispatch.yaml schema 同步验证）
- `python3 agate/scripts/check-protocol-consistency.py --strict-errors-only`（worktree 自己的；state-machine/P1 卡改动一致性）
- count-tests 不漂移

## 产出

1. 上述 5 文件实际改动
2. `{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/P4-implementation.md`：Header + `implementation_dir:` + 新增文件核对表 + 改动摘要（judge 校验实现 + 文档面同步）+ 自查结果 + 触发面清单

## 分阶段落盘

每完成一个文件改动/每次自跑，追加写 `{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/P4-progress.md`。

## 返回给我

只返回两行：① P4-implementation.md 路径 + 改动文件清单；② 一句话摘要（红转绿 + 兼容性结论）。绝不返回文件全文。
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
