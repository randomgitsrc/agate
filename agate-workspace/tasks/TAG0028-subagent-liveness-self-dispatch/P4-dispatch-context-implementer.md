---
phase: P4
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0028
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

按 P2-design.md 方案 A 实现 TAG0028 四 phase 的代码与文档改动（M1-M8），让 P3 红灯测试（38 个）转绿（4 个长期不变量用例已绿，须保持）。实现顺序按 P2-design §8 实现完成标志的 Phase 1→4 推进：

- **Phase 1（M1/M2）**：`agate/scripts/agate-cmdstream-ir.py`（CommandRecord IR + 字段契约校验 + JSON 序列化）+ `agate/scripts/agate-cmdstream-adapters.py`（适配器基类 + 三平台适配器 + 显式注册表）
- **Phase 2（M3/M4）**：`agate/scripts/agate-cmdstream-detect.py`（检测引擎 + CLI 子命令）+ `agate-workspace/maintainability.yaml` 新增 `cmdstream_detection:` 节（阈值可配置 + 全兜底）
- **Phase 3（M5/M8）**：`agate/dispatch-protocol.md` 改写（951 行存活检查节 + 心跳文件生命周期子节 + 自主再派发节）+ `agate/scripts/check-p6-provenance.py` 心跳豁免显式登记（注释/常量级，不改枚举逻辑与 7 道审计结构）
- **Phase 4（M6/M7）**：`agate/role-system.md` 新增「子派发权限边界」节 + `agate/assets/templates/dispatch-context.md` 补「不启用子派发能力」声明位

### 约束

1. **TDD 转绿不改测试**：P3 测试是验收契约（42 用例：38 红待转绿 + 4 绿保持）。实现让红灯转绿；测试断言与 P1 BDD 矛盾 → 标 `[DESIGN_GAP]` 不改测试；不确定 → 按 investigate 诊断不猜。
2. **最小实现原则**：写最简单的代码让测试通过，不加额外功能、不重构无关代码、不"顺便改进"。
3. **上下文控制**：读代码文件以 P2-design.md §5 files_to_read 清单为准（标了行号范围的只读片段），不要在项目里盲目搜索或整目录全读。
4. **verify_cmdstream_detection.py 锚不改**（BDD-22/N7）：检测引擎以其判据为参考实现，9 场景断言保持；阈值常量同源（300/900/60/300/10/5 + REPEAT_UNIQUE_MIN=3 + expected×2 下限 30s）。
5. **DSH zstd 解压隔离**（BDD-4）：解压经由 spawn node 单行脚本 `node:zlib.zstdDecompress` 在 dsh 适配器内部完成，不硬依赖 python zstandard；探测 node 可用性并报清晰错误。
6. **检测输出平台无关**（BDD-24）：判定类别 + 原因 + 阈值依据 + 建议动作方向，不含平台工具名；检测定位"证据 + 触发核查、不自动判死"（BDD-23）。
7. **阈值配置全兜底**（BDD-19/20/21）：复用 check-maintainability.py:88-148 `_load_config` 模式（缺失/损坏/类型坏 → 协议默认值不报错、不静默跳过）。
8. **SELF-GATE**：本批改 `agate/scripts/*.py` + `agate/*.md`（dispatch-protocol.md / role-system.md / dispatch-context.md 模板 / check-p6-provenance.py）→ **触发 SELF-GATE**，P4 commit 由主 Agent 写 `self-gate-review:` 标记；协议文档改动需跑 `check-protocol-consistency.py --strict-errors-only` 确认 0 ERROR（P5 gate 会再验）。
9. **范围锁定**：实现超 P0-brief/设计文档锁定范围 → 停下报告主 Agent；新隐含需求标 `[SCOPE+]`，prompt 漏 P2 已声明的事标 `[SCOPE_GAP]`，方案歧义标 `[CLARIFY]`/`[DESIGN_GAP]`（格式见 implementer.md）。
10. **fixture 脱敏**（BDD-7/I-14）：三平台 fixture 仅用已入库脱敏样例，不读取其他用户会话。
11. **自查≠gate**：写完自跑测试确认基本功能，但自查≠P5 gate；不声称"P5 已过"。
12. **code style**：遵循既有 agate/scripts 惯例（`agate_common.py` import 模式、`set -euo pipefail` 不适用于 py、ruff 用 `~/.venvs/agate-dev/bin/ruff`）；新增 py 脚本跑 ruff 自查（`ruff check` 无 error）。

### 上游关联

- P2-design.md（方案 A + §5 files_to_read + §8 实现完成标志——本批权威导航）
- P3-test-cases.md + `agate/tests/unit/test_agate_cmdstream_*.py`（验收契约，38 红待转绿）
- P0-brief.md（env_constraints：SELF-GATE / 双工作区 / DSH 脱敏 / 阈值保守）
- verify_cmdstream_detection.py（9 场景判据参考 + BDD-22 锚）

### 输入文件（按顺序读）

1. `agate-workspace/tasks/TAG0028-subagent-liveness-self-dispatch/P2-design.md`（方案 A + files_to_read + 实现完成标志）
2. `agate-workspace/tasks/TAG0028-subagent-liveness-self-dispatch/P3-test-cases.md`（测试设计 + test_code_dir）
3. `agate/tests/unit/test_agate_cmdstream_*.py`（验收契约，逐文件读）
4. `agate-workspace/tasks/TAG0028-subagent-liveness-self-dispatch/P0-brief.md`（env_constraints）
5. P2-design.md §5 files_to_read 清单中列出的文件（按需，标行号范围的只读片段）
6. `docs/design-notes/260903-design-subagent-liveness-and-self-dispatch/verify-heartbeat-cmdstream/verify_cmdstream_detection.py`（9 场景判据）
7. `AGENTS.md`（项目约定）

### 产出文件字段

产出 `P4-implementation.md` 到任务目录（frontmatter 用 `agate-md-field-set` 填写：phase=P4 /
task_id=TAG0028 / type=implementation / parent=P2-design.md / trace_id=TAG0028-P4-20260903 /
status=draft / created=2026-09-03 / agent=implementer / **implementation_dir: agate/scripts/**）。
正文须含：`implementation_dir` 声明、新增文件核对表（CODE-MAP 机制已采用——
`agate-workspace/agents/CODE-MAP.md` 存在，须填"新增文件路径 / 骨架归属 / CODE-MAP 处理"三列）、
实现摘要（每 phase 关键改动 + 关联 BDD）。
代码文件写在 worktree 的 `agate/scripts/` 与 `agate-workspace/maintainability.yaml` 等（见目标）。
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
### A. 路径拓扑（worktree 场景）
- worktree 根 = `/home/kity/oclab/agateon/.worktrees/agate-TAG0028`（本任务 project_root）
- AGATE_WORKSPACE = `/home/kity/oclab/agateon/.worktrees/agate-TAG0028/agate-workspace`
- 任务目录 = `agate-workspace/tasks/TAG0028-subagent-liveness-self-dispatch/`
- 协议本体（改造对象）= worktree 的 `agate/`（主 checkout `/home/kity/oclab/agateon/agate` 禁止改动，
  `~/.agate` 软链指向它是稳定版 gate 工具）
- 双工作区纪律：改代码/写产出在 worktree；`check-protocol-consistency.py` 用 worktree 自己的；编排/派发类工具用 `~/.agate` 稳定版

### B. 实现要点速查（P2-design §3 展开）
- **M1 agate-cmdstream-ir.py**：CommandRecord dataclass 十字段（platform/session_id/tool/command/ts_start/ts_end/exit/exit_signal/output_hash/truncated）+ 类型契约（ts_start/ts_end epoch 毫秒 int、exit int|null、truncated bool、output_hash truncated 时 null）+ to_json/from_json
- **M2 agate-cmdstream-adapters.py**：`CommandStreamAdapter` 基类（probe/list_sessions/read_commands）+ ClaudeCodeAdapter（JSONL + tool_use/tool_result 配对 + "Exit code N" 文本前缀 + sidecar 子 agent）/ OpenCodeAdapter（SQLite opencode.db + part.data.state + metadata.exit 整数 + truncated 显式）/ DSHAdapter（JSONL.zstd + spawn node zstd + "Error:" 前缀 + delegationDepth 层级）+ `ADAPTERS` 显式注册表
- **M3 agate-cmdstream-detect.py**：detect(records, now) → verdict（FROZEN 调用冻结 expected×2/300/900、FROZEN 活动冻结 60/300、SPIN 窗口 10 ≥5、NORMAL 含 REPEAT_UNIQUE_MIN=3 信息级、截断排除、轮询标注）+ CLI（list-sessions/read-commands/detect）+ 平台无关输出
- **M4 maintainability.yaml**：新增 `cmdstream_detection:` 节（call_freeze_alert/suspect、activity_freeze_alert/suspect、spin_window/threshold、repeat_unique_min、expected_multiplier/lower_bound）
- **M5 dispatch-protocol.md**：951 行存活检查节改写（命令流日志承担存活/卡死判定、progress.md 保留语义进展）+ 心跳文件生命周期子节（.heartbeat/.heartbeat.child-{n} 命名、审计豁免、清理时机）+ 自主再派发节（与五模式关系、§4.1 两边界、产出收敛）
- **M6 role-system.md**：「子派发权限边界」节（执行角色可被授予、两硬边界、judge 例外）
- **M7 dispatch-context.md 模板**：补「不启用子派发能力」声明位（judge 类角色）
- **M8 check-p6-provenance.py**：`_find_files`（85-93 行）隐藏文件过滤天然跳过 `.heartbeat*`——登记显式确认（注释 + 常量说明），不改枚举逻辑、不改 7 道审计

### C. 测试契约速查（P3，38 红待转绿）
- `test_agate_cmdstream_ir.py`（3 红：字段契约/exit null/JSON 往返）
- `test_agate_cmdstream_adapters.py`（三平台解析 + 注册表 + fixture 脱敏）
- `test_agate_cmdstream_detect.py`（9 场景 + 阈值兜底 + 截断 + 轮询 + 平台无关 + 不判死）
- `test_agate_cmdstream_heartbeat.py`（命名/豁免/清理/两信号，含文档断言）
- `test_agate_cmdstream_dispatch.py`（边界/子集/judge 例外/收敛，含 role-system/模板文档断言）
- 4 个长期不变量用例已绿（须保持）：测试先读具体文件确认哪些是长期不变量（通常为文档/机制存在性断言）

### D. 环境事实
- python3 3.12.3 / pytest 9.0.3 / pyyaml 6.0.1 / node v24.15.0（zlib.zstdDecompress 为 function，验证记录已确认）
- ruff：`~/.venvs/agate-dev/bin/ruff`（0.16.4）
- 测试自跑：`timeout 180s python3 -m pytest agate/tests/unit/test_agate_cmdstream_*.py -q --tb=short`
- 一致性：`timeout 180s python3 agate/scripts/check-protocol-consistency.py --strict-errors-only`（0 ERROR）
- 检测锚：`timeout 120s python3 docs/design-notes/260903-.../verify-heartbeat-cmdstream/verify_cmdstream_detection.py`（9 场景全 PASS）

### E. 新增文件核对表预期（CODE-MAP 已采用）
- `agate/scripts/agate-cmdstream-ir.py` / `agate-cmdstream-adapters.py` / `agate-cmdstream-detect.py` → 须在 P4-implementation.md 新增文件核对表登记（CODE-MAP 处理：更新 `agate-workspace/agents/CODE-MAP.md` 或标 EXEMPT + 理由）
- 骨架机制未采用（P1 无 project_phase: bootstrap）→ 骨架归属列标 N/A 或 within agate/scripts
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
