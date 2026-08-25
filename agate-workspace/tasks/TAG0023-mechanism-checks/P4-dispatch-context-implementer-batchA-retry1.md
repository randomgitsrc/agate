# P4-dispatch-context-implementer-batchA-retry1 — TAG0023（P4 修复，batch A 专属）

> 派发对象：implementer（P4 修复，batch A，其余批次不受影响）。这是本轮的强制指令，不是参考信息。
> 任务目录：`{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/`

## 上一轮评审结论

`P4-review.md` status: **rejected**（独立评审，见 `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P4-review.md` 全文，**必读**）。4 条 CRITICAL 全部集中在 batch A（`check-state-transition.py`），均已用本仓库真实数据核实为真实缺陷，不是误报。batch B/C/D **无需任何改动**，本轮只修 batch A。

## 改动范围（硬边界）

**只改**：`agate/scripts/check-state-transition.py` + `agate/tests/unit/test_check_state_transition.py`（**本轮允许改测试**，但只能：①新增回归用例 ②给 `test_st_archive_1/2/3/6` 四个既有测试的 fixture 补充非空 retries 声明——不改变这 4 个测试的断言语义/意图，只是让它们的输入数据不再意外依赖"两侧 retries 皆为空即放行"这个即将被移除的隐含假设）

**不要改**：batch B/C/D 涉及的任何文件（`check-gate.py`/`check-debt.py`/`agate-frontmatter-check.py`/`dispatch-prompt.md`/CI/roadmap.md/协议文档）

## 4 条 CRITICAL 逐条修复要求

### CRITICAL 1（范围决策，采用方案 A）：BDD-2 old_retries_len>0 守卫漏判首次违规

**主 Agent 决策：采用 review 给出的方案 A**——去掉 `old_retries_len > 0` 守卫，让 BDD-2 按 P1-requirements.md 原文字面语义实现："回退（含单步）+ retries[目标阶段] 未同步增长" 即拦截，不要求"此前必须已有过记录"这个前提。理由：这个前提恰好排除了 RM-AG0042 的立项证据本身（"四任务 retries 全为 {}"，即从未记录过的场景），若不修，本任务号称修复的问题在最常见的场景下仍然修不到，属于自相矛盾。

**具体改法**：
```python
if old_num > 0 and new_num > 0 and old_num > new_num:
    old_retries_len = get_old_retries_len(state_file, state_basename, new_phase)
    new_retries_len = _retries_len(current_state_data, new_phase)
    if new_retries_len <= old_retries_len:   # 去掉 old_retries_len > 0 这个 and 条件
        ...sys.exit(1)
```

**连带修复既有测试**（这是本次唯一允许改测试的地方）：`agate/tests/unit/test_check_state_transition.py` 中以下 4 个测试目前隐含依赖"两侧 retries 皆为空则不拦截"，去掉守卫后 BDD-2 检查（在检查4之前执行）会提前 `sys.exit(1)`，导致这些测试的 exit code/输出断言失败——**不是这些测试错了，是它们的 fixture 需要显式声明非空 retries，避免被新的 BDD-2 检查意外短路**：
- `test_st_archive_1_p6_to_p5_unarchived_exit_1`（L335）：`_write_state(task / ".state.yaml", "P6")` 处补 retries 声明（如 `retries: {P5: [{attempt: 1}]}`），保证 HEAD 版本 `retries[P5]` 非空；暂存版本（改成 P5 那次 `_write_state` 调用）也补相同或更长的 retries，使其长度关系满足"未回退违规"（`new_retries_len > old_retries_len` 或至少不触发 BDD-2），这样 check3-BDD2 不拦截，请求能继续走到 check4 触发预期的"P6 自撰产出未归档"逻辑，测试断言（exit 1 + "P6 的自撰产出" + "agate-archive-stale-outputs.py"）保持不变
- `test_st_archive_2_p6_to_p5_archived_exit_0`（L352）：同上补 retries fixture，保证 BDD-2 不拦截，让测试仍按原意图（P6 已归档 → exit 0）验证 check4 逻辑
- `test_st_archive_3_p5_to_p4_not_self_authored_exit_0`（L366）：同上
- `test_st_archive_6_p2_to_p1_review_still_in_place_exit_1`（L410）：同上，保证走到 check4 的"P2-review.md"断言

**（review 原文提到的是 test_st_archive_2/3/4，但你自己验证——test_st_archive_4 是"P4→P5"正向转移，`old_num>new_num` 为 False，BDD-2 条件不成立，不受影响，不需要改；test_st_archive_1 和 test_st_archive_6 才是实际会被新逻辑短路的，请以你自己跑测试的实际结果为准，不要盲目照抄任何一方的清单，包括本段列的清单——实际动手跑一遍 `pytest agate/tests/unit/test_check_state_transition.py -k archive` 观察哪些真的失败）**

新增 1 条回归用例：验证"首次单步回退（HEAD 与暂存 retries 均为空）"确实被拦截（exit 1）——这是 CRITICAL 1 要修复的核心场景，也是本任务的立项证据场景。

### CRITICAL 2（机械修复）：`_load_current_state_yaml` 非法编码导致脚本崩溃

`open(state_file, encoding="utf-8")` 只 `except OSError`，`UnicodeDecodeError` 不是 `OSError` 子类不会被捕获。改为：
```python
try:
    with open(state_file, encoding="utf-8", errors="replace") as f:
        text = f.read()
except OSError:
    return {}
```
（加 `errors="replace"` 后实际上不会再抛 `UnicodeDecodeError`，这是最简单的修法，对齐 `_scan_bdd3_keyword_phases` 已有的 `errors="replace"` 风格）

新增 1 条回归用例：`.state.yaml` 含非法 UTF-8 字节时，脚本不崩溃（不要求特定 exit code，只要求不抛未捕获异常）。

### CRITICAL 3（机械修复）：`_scan_bdd1_review_retry_phase` 只返回首个匹配阶段

改成收集全部命中阶段（参照 `_scan_bdd3_keyword_phases` 已有的 set 收集模式），返回类型从 `Optional[str]` 改为 `set[str]`，调用处（BDD-1 分支）改成对 set 里每个阶段分别检查 `retries[Pn]` 是否为空并各自输出 WARNING（参照 BDD-3 分支已有的 for 循环写法）。

新增 1 条回归用例：**直接用本任务自己的 `agate-workspace/tasks/TAG0023-mechanism-checks/` 目录结构**（或合成等价 fixture）验证 P1 和 P2 两个评审重试文件同时存在时，两个阶段的 WARNING 都能各自触发（不只触发第一个）。

### CRITICAL 4（机械修复）：`_scan_bdd3_keyword_phases` 漏扫 `P4-progress-batchX.md` 命名模式

```python
if not (rest.startswith("progress.md") or "dispatch-context-" in name):
```
改成：
```python
if not (rest.startswith("progress") or "dispatch-context-" in name):
```
（`"progress-batchA.md".startswith("progress")` → True，同时不影响原有 `"progress.md".startswith("progress")` → True 的行为）

新增 1 条回归用例：用 `P4-progress-batchA.md`（或等价命名）命中关键词场景，验证扫描到。

## 输入文件

1. `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P4-review.md`（**本轮评审全文，必读，含每条 CRITICAL 的完整论证与代码位置**）
2. `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P1-requirements.md`（BDD-2 原文 Given/When/Then，核对方案 A 是否字面满足）
3. `agate/scripts/check-state-transition.py`（当前实现，本轮在此基础上修改）
4. `agate/tests/unit/test_check_state_transition.py`（L335-425 archive 系列 + L495-713 本任务 BDD 测试，本轮在此基础上补充/修正 fixture）

## 命令超时兜底

```bash
timeout 60s python3 -m pytest agate/tests/unit/test_check_state_transition.py -q -p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp_batchA_fix
```

## 门槛

- 4 条 CRITICAL 全部修复，各配至少 1 条新回归用例
- `test_st_archive_1/2/3/6`（或你实测确认真正受影响的那几条）保持原断言语义通过（fixture 补充非空 retries，不改断言）
- `test_check_state_transition.py` 全文件测试全部通过，无回归
- ruff 通过

## 返回给我

只返回两行：① 改动的文件路径列表；② 一句话摘要（4 条 CRITICAL 修复情况，≤40字）。绝不返回代码全文。

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
