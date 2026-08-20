---
phase: P4
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0007
role: review
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令。C8 机械映射：domains=[backend] → review；risk_level=high
（P1 frontmatter）→ 同一映射已覆盖，不额外触发其他角色。本任务是单评审角色场景，你的产出直接写
P4-review.md，无需组长汇总。

### 目标
独立评审 P4-implementation.md 记录的全部实现改动（4 个并行批次：skeleton-docs / code-map-docs /
gate-script-both / dogfood-bootstrap），判定 approved / rejected，产出 P4-review.md。本任务是
协议脚本 + 协议文档改动（不是典型 Web 应用后端代码），评审重点相应调整——不是查 SQL 注入/前端
AI slop，而是查 gate 判定逻辑的正确性、边界条件、与既有机制（DESIGN_GAP pairing）的一致性。

### 约束（评审重点，按下列具体项逐条检查，不要套用角色定义里 Web 应用场景的检查项）

1. **`check-gate.py` 三处新增分支的正确性核查（最高优先级）**：
   - `gate_p2` 的 `project_phase: bootstrap` 判定：字段缺失/`established` 时是否真的完全不触发
     新分支（回归安全）；`bootstrap` 声明时缺 `P2-skeleton.md` 或缺标题是否正确 exit 1
   - `gate_p7` 的两层 pairing 校验：**逐行核对字段对应关系**——内部一致性层比较
     `code_map_reviewed_count < code_map_new_files_count`；转抄核对层比较 P4 实际标记数与
     `code_map_new_files_count`（**不是** `code_map_reviewed_count`）。这是 P2 review 第一轮
     曾打回的错误点（P2-design.md §5 minimal_validation 记录了修复过程），P4 实现必须严格遵循
     修复后的对应关系，若发现写反或混淆，判 CRITICAL 级问题
   - `gate_p4` 的 WARNING 分支：是否真的不阻断（exit code 仍为 0）、`change_type: refactor`
     是否真的不影响判定（BDD-10 要求）
   - **TOCTOU/竞态角度**：gate 脚本读取暂存区文件状态（`git diff --cached`）与读取工作区文件
     （`P2-skeleton.md`/`P4-implementation.md`/`P7-consistency.md`）是否存在时序不一致的风险
     （如暂存区已 add 但工作区文件后续被改动）——若existing 代码本就有这类假设，不苛求本次改动
     解决，但新增分支不应引入新的更严重的不一致
   - **状态枚举完整性**：`project_phase` 目前只有 `bootstrap`/`established` 两个枚举值，若未来
     新增第三个值，当前实现是否会静默误判为其中一个（防御性检查）

2. **DESIGN_GAP 重点核查（implementer 已标注 2 条，你必须逐条给出明确判定，不能只是"已阅读"）**：
   - **第 1 条**（`_md_field_get` 因新字段未注册 `KNOWN_OPS` 会静默失败，改用本地
     `_frontmatter_field` 替代）：核查 `_frontmatter_field` 与 `_md_field_get` 的实际行为差异
     是否真的等价（尤其对"字段存在但值为空字符串"、"frontmatter 块格式异常"等边界情形），若
     发现两者语义不完全等价，需明确指出差异点
   - **第 2 条**（`{AGATE_WORKSPACE}/agents/CODE-MAP.md` 路径解析用"task_dir 向上两级"简化
     推导，未使用 `agate_common.py` 现有的 `resolve_workspace(project_root)` 权威解析函数）：
     **主 Agent 已核实 `resolve_workspace` 函数确实存在**（`agate/scripts/agate_common.py`
     L461-489），签名 `resolve_workspace(project_root) -> (workspace, tasks_dir)`，解析优先级
     `.agate.env(AGATE_WORKSPACE=)` → env `AGATE_TASKS_DIR` → 默认
     `{project_root}/agate-workspace`——这意味着若项目通过 `.agate.env` 自定义了工作区位置，
     implementer 当前"task_dir 向上两级"的简化推导会得出**错误路径**，导致
     `{AGATE_WORKSPACE}/agents/CODE-MAP.md` 存在性误判（骨架/CODE-MAP 机制已采用但被判定为
     未采用，WARNING 不会触发）。**请你独立判断**：这个问题是否足以构成 rejected 的理由（影响
     范围仅限于 WARNING 分支且只是"少触发一次提醒"，不阻断任何 commit，本身不是 BLOCKER 级
     数据安全问题），还是可以作为非阻塞的技术债登记（`{AGATE_WORKSPACE}/debt/tech-debt.md`，
     标准 DEBT 格式，`evidence` 引用 `resolve_workspace` 函数位置）而 approve。给出你的判断
     + 理由，不要回避这个问题。

3. **回归验证核查**：主 Agent 已跑过全量 `python3 -m pytest agate/tests/` → 1028 passed, 2
   skipped, 0 failed；`check-protocol-consistency.py` → 0 ERROR；`shellcheck` → 0 error（见
   objective_info）。你可以直接引用这些结果，不需要重跑，但若怀疑结果不实可自行抽查复核。

4. **跨批次一致性核查**：4 批次产出的字段名/标题名是否真的逐字一致（`code-map-docs` 批次在
   文档中声明的 `code_map_new_files_count`/`code_map_reviewed_count`/`## 新增文件核对表` 字符串
   是否与 `gate-script-both` 批次的实际代码判定字符串完全匹配，不是"大致相似"）。

5. **ADR-003 合规复核**：`skeleton-docs` 批次产出的 `assets/templates/skeleton-template.md` 是否
   真的不含硬编码技术栈目录名（`src/components`/`src/include`/`src/hooks`/`src/pages`），这是
   P1/P2 review 都强调过的关键约束点。

### 输出结构（按本任务实际场景调整，不套用角色定义的 Web 应用格式）
```
架构/正确性问题（阻塞级）：
  - [具体问题 + 文件:行号 + 建议]（若无则写"无"）

架构/正确性问题（非阻塞）：
  - [具体问题 + 记录到 TD-xxx 或建议后续处理]（若无则写"无"）

DESIGN_GAP 逐条判定：
  1. [第 1 条判定 + 理由]
  2. [第 2 条判定 + 理由，含是否需要登记 DEBT]

回归验证确认：
  [引用/复核结果]

跨批次一致性确认：
  [核查结果]

结论：
approved / rejected + 理由
```

### 上游关联
P2-design.md（approved，含 P2 review 曾打回的 pairing 字段对应关系错误 + 修复记录）→
P3-test-cases.md（17 个测试用例，12 个针对 check-gate.py 三处新增分支）→ P4-implementation.md
（4 批次实现记录 + 2 条 DESIGN_GAP）。

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0007-project-structure/P4-implementation.md（评审对象，含 2 条
  DESIGN_GAP）
- {AGATE_WORKSPACE}/tasks/TAG0007-project-structure/P2-design.md（§2.3/§5，pairing 字段对应
  关系的权威规格 + P2 review 修复记录）
- {AGATE_WORKSPACE}/tasks/TAG0007-project-structure/P3-test-cases.md（12 个 check-gate.py 相关
  测试用例的精确断言）
- /home/kity/oclab/agate/.worktrees/agate-TAG0007/agate/scripts/check-gate.py（评审对象代码，
  gate_p2/gate_p4/gate_p7 三个函数的改动后完整源码）
- /home/kity/oclab/agate/.worktrees/agate-TAG0007/agate/scripts/agate_common.py:461-489
  （`resolve_workspace` 函数，DESIGN_GAP 第 2 条的权威判据来源）
- /home/kity/oclab/agate/.worktrees/agate-TAG0007/agate/assets/templates/skeleton-template.md
  （ADR-003 合规复核对象）
- /home/kity/oclab/agate/.worktrees/agate-TAG0007/agate/assets/templates/code-map-template.md
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
- 全量回归（主 Agent 已跑）：`python3 -m pytest agate/tests/ -q --tb=line` → 1028 passed, 2
  skipped, 0 failed
- `python3 agate/scripts/check-protocol-consistency.py` → 0 ERROR（316 WARNING）
- `shellcheck -S warning agate/scripts/*.sh` → 0 error
- `git status --porcelain` 已核实 4 批次改动无跨批文件重叠
- `agate_common.py` 的 `resolve_workspace(project_root)` 函数确认存在（L461-489），可作为
  DESIGN_GAP 第 2 条的权威判据
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
