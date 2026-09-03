---
phase: P4
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0028
role: implementer
round: fix1
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 修复轮（增量模式）

- 上轮产出路径：`agate-workspace/tasks/TAG0028-subagent-liveness-self-dispatch/P4-implementation.md` + 代码文件
- 上轮 dispatch-context：`P4-dispatch-context-implementer.md`（**复用其全部目标/约束/上游关联/输入文件/产出规格**，本文件只写本轮增量）
- 评审结论：`P4-review.md` status=rejected（7 个 [CRITICAL]，3 个经运行时实验复现，每个附 Fix 选项 A/B/C 推荐项）

### 修复目标（7 个 CRITICAL 全部必须修复，按评审推荐项落地）

**[CRITICAL-1] CLI detect 时间单位错配**（agate-cmdstream-detect.py:326-357）
- 现象：CLI 构造 events 的 ts 与 --now 均为 epoch 毫秒，detect() 用 age=now-ts 直接比对秒级阈值（300/900/60/300）——实验复现 3 秒无活动即误报 FROZEN「距今 3000s ≥ 300s」
- 修复（评审 Fix A 推荐）：CLI 归一单位——--now 与 events ts 统一转秒（now=int(time.time())，ts 毫秒→秒），detect 语义保持秒阈值，与 verify 脚本/测试同口径

**[CRITICAL-2] DSH zstd 拼接帧容器只解第一帧**（agate-cmdstream-adapters.py:365-389 DSHAdapter._decompress）
- 现象：node 脚本 `z.zstdDecompressSync(buf.subarray(off))` 成功即 off=buf.length 退出循环，未处理帧边界推进——验证记录 Q7 实测 20020 帧 / 28406 条记录，帧 2..N 全部丢弃；实验复现两帧容器只返回帧 1 记录
- 修复（评审 Fix A 推荐）：node 脚本逐帧解压并推进帧边界（zstd 帧 magic 0x28B52FFD 定位或等价逐帧切分），把全部帧解出后拼接，最新命令流（文件尾部帧，边写边落）可见
- 修复后须新增/调整测试覆盖多帧容器（两帧各含完整 call+result 对 → 返回 2 条记录）

**[CRITICAL-3] 「未结束 call」通路在 claude-code/dsh 数据源不可达**（agate-cmdstream-adapters.py:391-440 + agate-cmdstream-detect.py:326-357）
- 现象：ClaudeCodeAdapter/DSHAdapter 仅从配对成功的 result 反查产出记录，无 result 的未结束 call 不产出 IR；CLI detect 事件 id=f"{session_id}:{tool}:{command}" 同会话同命令多次调用 id 相同，call_ids/result_ids 集合运算坍缩——BDD-8/9/10 调用冻结（含 expected×2 主信号）在 claude/dsh CLI 通路永不触发；且 IR 十字段无 expected 字段，CLI 从不注入 expected
- 修复（评审 Fix A 推荐）：① 适配器对未结束 call 产出 exit=None/ts_end=None 的记录（IR 契约本就允许 exit=None）；② CLI 事件 id 加调用序号/时间戳保证唯一（unresolved 集合不再被坍缩）；③ 若 CLI 通路需支持 expected×2 主信号（BDD-8），按 P2-design §3.2 语义把 expected 声明接入 CLI 事件（从 maintainability.yaml 或事件元数据读取——以 BDD-8 语义可达为准，具体接入方式自主决策并在 P4-implementation.md 记录）
- 修复后须新增/调整测试覆盖：适配器对未结束 call 产出 exit=None 记录；CLI 通路未结束 call 可触发调用冻结判定

**[CRITICAL-4] Claude 解析崩溃链**（agate-cmdstream-adapters.py:189-190、72-81）
- 现象：`_iso8601_to_epoch_ms(u.get("timestamp", ""))` timestamp 缺失/非 ISO-8601 → ValueError 无 try 包裹；`obj.get("content")` 前未校验 obj 为 dict → AttributeError（DSH 391-410 同样未校验 obj 类型）
- 修复（评审 Fix A 推荐）：解析循环内 timestamp 缺失/非法返回 None 或跳过该行；_collect_parts 前 `isinstance(obj, dict)` 守卫；异常行跳过并计数告警（防静默吞数据需计数）

**[CRITICAL-5] OpenCode SQLite 畸形/损坏库崩溃**（agate-cmdstream-adapters.py:261-281）
- 现象：`sqlite3.connect` + `conn.execute("SELECT data FROM part")` 无 try/except——非 SQLite 文件/缺表/损坏库 → DatabaseError 传播，read_commands 崩溃（DB 文件在用户目录，外部不可信输入）
- 修复（评审 Fix A 推荐）：connect+execute 包 try/except sqlite3.Error，失败返回空列表 + stderr 告警（与 _load_config 全兜底模式同风格）

**[CRITICAL-6] CommandRecord 类型契约校验缺失**（agate-cmdstream-ir.py:49-64 from_dict/from_json）
- 现象：P2-design M1 明确「字段契约校验（ts epoch 毫秒 int、exit int|null、truncated bool）」，实现只查字段存在性不校验类型——from_json 喂入 ts_start="abc" / exit="x" / truncated="yes" 静默接受，坏数据流入 detect 后崩溃或判定失真
- 修复（评审 Fix A/B 推荐，可二选一或并用）：from_dict 逐字段类型校验（ts 须 int、exit 须 int|None、truncated 须 bool、不符抛 ValueError 带字段名）；或 dataclass `__post_init__` 校验（构造路径同样受保护）。BDD-1 Then「类型符合 IR 契约」的直接落点
- 修复后须确认 BDD-1 测试仍绿（类型校验不破坏合法记录构造）

**[CRITICAL-7] DSH truncated 恒 False**（agate-cmdstream-adapters.py:467）
- 现象：适配器硬编码 truncated=False，BDD-17（截断输出不参与无效重复哈希比对）对 DSH 数据源失效；验证记录 Q6 明确 DSH 有截断标记（超大输出会被截断），真实超大输出截断后仍参与 (命令, exit, 输出哈希) 比对 → 多个不同失败截断成同前缀 → 误判 SPIN
- 修复（评审 Fix A 推荐）：解析 DSH result content 的截断标记（验证记录 Q6 指出存在标记），truncated 置 True 并 output_hash=None（与 IR 契约 truncated=True → output_hash=None 一致）
- 修复后须新增/调整测试：DSH fixture 含截断标记记录 → truncated=True + output_hash=None

### 约束（延续上轮，重点重申）

1. **P3 测试是验收契约**：修复 CRITICAL 若需新增/调整测试覆盖（多帧、未结束 call、截断标记），可以补充 P3 测试（`test_agate_cmdstream_*.py`）——但**不得削弱既有 BDD 断言**、不得改 P1 基线；新增测试名引用对应 BDD 编号（如 test_bdd_2_multi_frame / test_bdd_3_unfinished_call）
2. **阈值数值锚不可动**：300/900/60/300/10/5 + expected×2 下限 30s + REPEAT_UNIQUE_MIN=3 与 verify 脚本同源
3. **verify_cmdstream_detection.py 9 场景锚不改**（BDD-22）：修复后须 9 场景仍全 PASS
4. **SELF-GATE**：本批仍改 `agate/scripts/*.py` → P4 commit 须含 `self-gate-review:`
5. **范围锁定**：只修评审 7 CRITICAL + 必要的测试补充；修复中发现新问题标 `[DESIGN_GAP]`/`[SCOPE+]` 报告，不擅自扩
6. **自查≠gate**：写完自跑确认（cmdstream 套件全绿 + verify 9 场景 + consistency 0 ERROR + 全量 unit 无回归），但自查≠P5 gate
7. **修复后在 P4-implementation.md 追加「## 修复轮记录（fix1）」**：逐条对应 7 CRITICAL（现象 → 修法 → 验证），并记录新增/调整的测试

### 上游关联

- `P4-review.md`（7 CRITICAL + Fix 选项——本轮修复依据，逐条对照）
- `P2-design.md`（方案 A + §3 机制语义 + files_to_read）
- `P3-test-cases.md` + `agate/tests/unit/test_agate_cmdstream_*.py`（验收契约）
- 验证记录（Q6 截断标记 / Q7 拼接帧 20020 帧——CRITICAL-2/7 的事实依据）
- verify_cmdstream_detection.py（9 场景锚）

### 输入文件（按顺序读）

1. `agate-workspace/tasks/TAG0028-subagent-liveness-self-dispatch/P4-review.md`（7 CRITICAL + Fix 选项，逐条对照）
2. `agate/scripts/agate-cmdstream-ir.py`（CRITICAL-6 修改）
3. `agate/scripts/agate-cmdstream-adapters.py`（CRITICAL-2/3/4/5/7 修改）
4. `agate/scripts/agate-cmdstream-detect.py`（CRITICAL-1/3 修改）
5. `agate/tests/unit/test_agate_cmdstream_*.py`（按需调整/补充）
6. `agate-workspace/tasks/TAG0028-subagent-liveness-self-dispatch/P2-design.md`（机制语义核对）
7. `docs/design-notes/260903-design-subagent-liveness-and-self-dispatch/verification-cmdstream-datasource-20260903.md`（Q6/Q7 事实核对）
8. `AGENTS.md`（项目约定）

### 产出文件字段

P4-implementation.md frontmatter 沿用（phase=P4 / task_id=TAG0028 / trace_id=TAG0028-P4-20260903 /
status=draft / agent=implementer / implementation_dir=agate/scripts/）。
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

**评审 checklist（RM-AG0046）**：`agate/scripts/check-maintainability.py` 检出 violations 非空时，评审角色 approve 前必须读过任务目录 `known-violations.md` 的登记理由——"是否接受该反模式"的判断权在评审角色，登记与数量对齐不单独构成放行依据。

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
- **exit 1**（RM-AG0046 三重门槛）：检测 violations 非空时，`known-violations.md` 必须存在且登记条目数 ≥ violation 数（评审检查复用上方既有 exit 1 条件；violations 为空 / 检测未部署 / git 通道不可用时不阻断）
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
### A. 评审实证证据（P4-review.md 摘要）
- CRITICAL-1：CLI 通路 ts=now_ms-3000 → 判「活动冻结（suspect）：距今 3000s ≥ 300s」——3 秒无活动误报
- CRITICAL-2：两帧容器（echo early@100 + echo late@200）→ node zstdDecompressSync 只输出帧 1；read_commands 返回 1 条（期望 2）
- CRITICAL-3：claude/dsh CLI 通路 unresolved 恒空（id 坍缩 + 适配器不产未结束记录）；BDD-8 expected×2 仅测试直构事件可达
- CRITICAL-4~7：代码核查（timestamp ValueError / obj 非 dict AttributeError / sqlite3 DatabaseError / from_dict 不验类型 / DSH truncated 恒 False）
- 通过面（不修）：阈值数值锚、spawn node 无注入、yaml 类型校验兜底、协议文档改写、心跳生命周期、DESIGN_GAP(test_bdd_3) 已解决

### B. 数据通路事实（验证记录）
- Q6：DSH「有截断标记（超大输出会被截断，需在哈希前排除或标记）」
- Q7：DSH 会话 20020 帧 / 28406 条记录，最后记录与 mtime 差 0.96ms（拼接帧为常态）；「需扫描帧边界逐个解压后拼接」
- IR 契约（BDD-1）：ts_start/ts_end epoch 毫秒 int、exit int|null、truncated bool、output_hash truncated 时 null

### C. 测试基线
- cmdstream 套件当前 42/42 绿（含 4 长期不变量）；全量 unit 1281 passed / 2 skipped
- verify_cmdstream_detection.py 9 场景全 PASS（不可破坏）
- consistency --strict-errors-only 0 ERROR（329 WARNING 基线）
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
