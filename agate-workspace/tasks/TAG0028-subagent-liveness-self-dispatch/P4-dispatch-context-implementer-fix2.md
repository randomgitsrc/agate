---
phase: P4
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0028
role: implementer
round: fix2
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 修复轮（增量模式，仅 CRITICAL-4 残留）

- 上轮产出路径：`agate-workspace/tasks/TAG0028-subagent-liveness-self-dispatch/P4-implementation.md` + 代码文件
- 上轮 dispatch-context：`P4-dispatch-context-implementer.md` + `P4-dispatch-context-implementer-fix1.md`（**均继续有效**，本文件只写本轮增量）
- 复审结论：`P4-review.md`（fix1 复审）status=rejected——7 CRITICAL 中 6 项已彻底修复（代码锚点 + 新测试双确认），**CRITICAL-4（Claude 解析崩溃链）未彻底修复，残留 2 条崩溃链（运行时实验复现）**；3 个 DESIGN_GAP 决策均评估合理；53 测试全绿

### 修复目标（唯一一项：CRITICAL-4 残留 2 条崩溃链，修法见 P4-review.md CRITICAL-4 节，本轮照做）

**[残留崩溃链 1] `_iso8601_to_epoch_ms`（agate-cmdstream-adapters.py:73-82）非字符串 timestamp**
- 现象：入口 `ts.endswith("Z")` 对 int/None 输入抛 AttributeError，而 `_build_record` 的
  `except (ValueError, TypeError)`（adapters.py:212/235）**不含 AttributeError** → 传播到
  read_commands 整体崩溃。实验复现：tool_use `timestamp:1788400860000`(int) / `timestamp:null` /
  tool_result `timestamp` 为 int → 均 AttributeError 崩溃。
- 修法（评审已给）：`_iso8601_to_epoch_ms` 入口加 `if not isinstance(ts, str): raise TypeError`
  （或 `try: ts = str(ts)` 归一），使非字符串输入落入既有 except 分支。

**[残留崩溃链 2] `_build_record`（agate-cmdstream-adapters.py:261-263）非 dict toolUseResult**
- 现象：`(r.get("toolUseResult") or {}).get("isImage", False)`——toolUseResult 为非空非 dict
  （如字符串）时 `"str".get` → AttributeError，无守卫。实验复现。
- 修法（评审已给）：`tr = r.get("toolUseResult"); truncated = bool(r.get("truncated", False)) or
  (isinstance(tr, dict) and bool(tr.get("isImage", False)))`。

**[测试缺口补齐]**
- `test_bdd_2_claude_malformed_lines_no_crash` 目前只覆盖 timestamp「缺失」与「非法字符串」，
  未覆盖「非法类型」（int/null）与 toolUseResult 非 dict 形态——**补这两类畸形输入的回归用例
  （先红后绿）**，确认修复后合法配对保留、畸形输入不崩溃。

### 约束（延续上轮，重点重申）

1. **只修 CRITICAL-4 残留两处 + 补对应回归测试**——不动已通过评审的 6 项修复（CRITICAL-1/2/3/5/6/7）、
   不动阈值数值锚、不动 verify 脚本、不改 P1 基线、不削弱既有断言
2. **P3 测试是验收契约**：补测试引用既有 BDD 编号（test_bdd_2_*），先红后绿
3. **SELF-GATE**：本批仍改 `agate/scripts/*.py` → P4 commit 须含 `self-gate-review:`
4. **范围锁定**：只修上述两处；发现新问题标 `[DESIGN_GAP]`/`[SCOPE+]` 报告，不擅自扩
5. **自查≠gate**：写完自跑确认（cmdstream 套件全绿 + verify 9 场景 + consistency 0 ERROR +
   全量 unit 无回归 + ruff），但自查≠P5 gate
6. **修复后在 P4-implementation.md「## 修复轮记录（fix1）」下追加「### fix2：CRITICAL-4 残留修复」小节**：
   两处崩溃链（现象 → 修法 → 验证）+ 测试补充记录

### 上游关联

- `P4-review.md`（fix1 复审）CRITICAL-4 节——本轮修复依据（修法原文照做）
- `P4-implementation.md`「## 修复轮记录（fix1）」——上轮修复记录（追加 fix2 小节）
- `agate/scripts/agate-cmdstream-adapters.py`（修改对象）
- `agate/tests/unit/test_agate_cmdstream_adapters.py`（补测试对象）
- 验证记录（Q6/Q7 事实依据，不变）

### 输入文件（按顺序读）

1. `agate-workspace/tasks/TAG0028-subagent-liveness-self-dispatch/P4-review.md`（重点 CRITICAL-4 节 76-100 行）
2. `agate/scripts/agate-cmdstream-adapters.py`（重点 `_iso8601_to_epoch_ms` 73-82 / `_build_record` 261-263 / read_commands 140-178）
3. `agate/tests/unit/test_agate_cmdstream_adapters.py`（test_bdd_2_claude_malformed_lines_no_crash 补测）
4. `agate-workspace/tasks/TAG0028-subagent-liveness-self-dispatch/P4-implementation.md`（追加 fix2 小节）
5. `AGENTS.md`（项目约定）

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
### A. 修复锚点（评审原文，本轮照做）
- 链 1：`_iso8601_to_epoch_ms` 入口 `if not isinstance(ts, str): raise TypeError`（或 str(ts) 归一）——
  使 int/None timestamp 落入既有 `except (ValueError, TypeError)`（adapters.py:212/235）
- 链 2：`tr = r.get("toolUseResult"); truncated = bool(r.get("truncated", False)) or
  (isinstance(tr, dict) and bool(tr.get("isImage", False)))`——非 dict toolUseResult 不再 AttributeError

### B. 现状基线（fix1 已验证）
- cmdstream 套件 53 passed（42 既有 + 11 新增，含 4 长期不变量）
- verify 9 场景全 PASS；consistency 0 ERROR；ruff 全过；全量 unit 1292 passed / 2 skipped
- 6 项 CRITICAL（1/2/3/5/6/7）已修复，勿动

### C. retries 状态
- `.state.yaml` 已记录 retries[P4] round 1 + round 2（P4 MAX=3，当前 2/3）——本轮修完复审通过则不再追加
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
