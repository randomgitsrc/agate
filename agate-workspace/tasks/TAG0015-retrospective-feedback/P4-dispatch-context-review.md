> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心输入源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。

---
phase: P4
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0015
role: review
retry: 1
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

## 重试 #1（复核 SELF-GATE 修复轮，本节优先于下方原始派发指引）

你上一轮已判定 approved（7 条约束全部核实属实）。此后 SELF-GATE 语义对齐审查发现 3 项
MISALIGNED + 1 项 NEEDS_HUMAN_REVIEW（见 `docs/reviews/agate-alignment-review-2026-08-19.md`），
implementer 已修复：① `agate-feedback.py` 改为调用 `agate-md-field-get.py`（新注册
`mechanism_issues`/`execution_issues`/`feedback_ready` 三字段，ADR-007 合规）② 订正
`test_bdd20_source_contains_no_network_submit_calls` 断言（原禁"subprocess"字面词过窄，改为
精确禁 `git push`/`gh ` 网络提交调用）③ 三处文档同步（`WORKFLOW.md:318` / `agate/scripts/README.md`
/ `agate/tests/README.md`）。

本轮复核**只需聚焦这 4 处改动**，不必重新走一遍原 7 条约束（除非改动意外波及了原实现的其他
部分）：

1. `agate-md-field-get.py` 的三字段注册是否正确（`NO_FALLBACK_LIST_FIELDS`/`NO_FALLBACK_BOOL_FIELDS`
   语义是否与既有同类字段一致，未破坏该工具服务的 P1/P2/P6/P7 既有字段行为——可用
   `timeout 60s python3 -m pytest agate/tests/unit/test_agate_md_field_get.py -q` 验证该工具
   自身测试仍全绿）
2. `agate-feedback.py` 的 `_md_field_get()` 调用是否正确还原了列表/布尔值（`mechanism_issues`/
   `execution_issues` 用换行分割还原列表；`feedback_ready` 用 `== "true"` 还原布尔），行为
   是否与订正前等价（同样的输入产出同样的 JSON payload）
3. `test_bdd20_...` 断言订正是否忠实反映 BDD-20 真实意图（P1-requirements.md 原文"不调用
   gh/git push 等网络提交命令"）——核实新断言 `re.search(r"subprocess\.\w+\(\s*\[[^\]]*\b(git|gh)\b", source)`
   逻辑是否真的能在"脚本被人恶意/误改为调用 git push"时报红，不是形同虚设的宽松断言
4. 三处文档同步内容是否准确（用例数字是否是重新数出的准确值，不是照抄审查报告的旧数字——
   可自行 `grep -c "^def test" agate/tests/unit/test_check_retrospective.py
   agate/tests/unit/test_agate_feedback.py agate/tests/unit/test_retrospective_protocol_docs.py`
   核对）

若以上 4 点均已妥善解决 → status: approved；若仍有缺口 → 明确指出具体哪一点。

---

### 目标（原始派发指引，重试时仍适用于未涉及修订的部分）

独立评审 implementer 产出的实现（P4-implementation.md + 12 处文件改动：1 个新脚本
`agate-feedback.py`、1 个模板 git mv 迁移、`check-retrospective.py` 新增分支、
`state-machine.md`/`AGENTS.md`/`task-files.md`/`P8-release.md`/`roadmap.md` 协议文档改动、
5 份 `docs/reviews/` 存量复盘文件加标注）。评审角色选定依据：`domains: [process]` 无字面 C8
映射行，沿用本仓库先例（TAG0012 P4 同样用 `review` 角色，产出 `P4-review.md`）。只审不改，产出
P4-review.md，交主 Agent 判定门槛。

### 约束

1. **核实实现是否忠实对照 P2-design.md §1.1 的七类改动落点**，不是自行发挥。重点抽查：
   a. `agate-feedback.py` 的匿名化实现是否真的是 P2 候选方案 B1（轻量正则脱敏：项目名替换 +
      绝对路径截断/移除），没有偷懒简化成不满足 BDD-18 验收要求的版本。
   b. `check-retrospective.py` 新增的 `_scan_debt_roadmap_signal` 分支是否保持了脚本"只提醒
      不阻断"的既有 exit code 契约（恒为 0），P2 §1.2 已明确这是不可破坏的边界。
   c. `state-machine.md` 新增的「L2 会话 checkpoint（两件套）」小节是否同时包含
      `P{n}-checkpoint.md` 与 `task-session-summary.md` 两个字面字符串，且四问（与
      orchestrator-log 关系/两个子机制各自的落盘时机与路径/防 compact 策略）均已回答（对照
      P2-design.md §3.2 四点）。
2. **[DESIGN_GAP] 偏差声明是否合理、是否真的解除了它所声称要解决的问题**——P4-implementation.md
   有一条 `[DESIGN_GAP: ...]`，声明 P2 未预见"物理 git mv 后 check-protocol-consistency.py
   CHECK 2 会把 roadmap.md 里的连续路径字符串误判为死链引用"，implementer 采用"拆开字符串"的
   方式规避误判，同时声称保留了原叙述内容未删减一字。**核实**：①这个偏差是否真的是"P2 没预见的
   gate 机制副作用"而不是"implementer 图省事的借口"（可用 `git diff
   agate-workspace/roadmap/roadmap.md` 独立核查文本改动是否真的只是"拆字符串"而非删减语义）；
   ②CHECK 2 分类判断（narrative dirs 名单不含 `agate-workspace/roadmap/` 与 `agate/assets/`）
   是否属实（可读 `check-protocol-consistency.py` 源码核实 `NARRATIVE_DIRS` 定义）。
3. **既有测试基线是否真的未受破坏**——独立核实 `test_check_retrospective.py` 原有 12 个用例
   仍在（不是被静默删改凑数），可用 `git diff agate/tests/unit/test_check_retrospective.py`
   核对（P4 阶段本不应改动测试文件，若发现测试文件有改动需要说明为什么）。
4. **P2 §1.2「不改什么」清单是否被严格遵守**——用 `git status --porcelain` 或
   `git diff --stat` 核对改动文件清单是否恰好落在 P2-design.md §1.1 七类改动范围内，没有
   意外触碰 `docs/hardening-roadmap.md`/`agate-workspace/archived/`/`dispatch-protocol.md`/
   `agate/WORKFLOW.md`/`agate/state-machine.md:361`（既有用法示例行）等范围外文件。
5. **agate-feedback.py 的"不含网络提交调用"是否真的成立**——独立 `grep -n "subprocess\|gh \|git push"
   agate/scripts/agate-feedback.py` 核实零命中（不只信实现自报）。
6. **5 份 docs/reviews/ 存量文件标注是否逐字复用了 P1/P2 已定案的文案**，没有各自发挥出不一致
   的措辞（会破坏 P1 §5 声明的"路径字符串三处必须逐字一致"要求的姊妹一致性）。
7. 评审产出需给出明确 approved/rejected/needs-revision 判定 + 具体依据，不允许裸 "approved"。

### 上游关联

- P3 阶段已确认真红灯；主 Agent 已独立复核：`pytest agate/tests/unit/test_check_retrospective.py
  agate/tests/unit/test_agate_feedback.py agate/tests/unit/test_retrospective_protocol_docs.py -v`
  → 35 passed；全量 `pytest agate/tests/` → 932 passed + 2 skipped（基线 909+2，净增 23，
  无回归）；`check-protocol-consistency.py --strict` → 0 ERROR（298 WARNING，基线 279）。这些
  是主 Agent 独立验证的客观事实，评审可信赖复用，不需要重新跑一遍（除非怀疑某个具体断言有问题，
  可针对性重跑单个测试函数核实）。
- P0-brief known_risks 已预警本任务改动触发 SELF-GATE——评审不需要额外做 SELF-GATE 自审工作
  （那是主 Agent commit 时的职责），但可以在评审意见里提示这一点供主 Agent 不遗漏。

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0015-retrospective-feedback/P4-implementation.md（评审对象）
- {AGATE_WORKSPACE}/tasks/TAG0015-retrospective-feedback/P2-design.md（§1.1/§1.2/§2/§3 是
  实现应忠实对照的权威规格）
- 实际改动文件（`git diff --cached` 或 `git diff HEAD` 可看到暂存区全部改动，评审应实际读
  diff 而不是只读 implementer 的文字描述）
- {agate_root}/assets/review-roles/review.md（角色定义）

### 门槛（什么算完成）
P4-review.md 含：Header 完整、`status:` 从 draft 改为最终判定；结论需引用具体文件/行号支撑，
不允许笼统评价；`agent` 字段非 main。
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
- 改动文件清单（`git status --porcelain` 实测）：新增 `agate/scripts/agate-feedback.py`；
  修改 `agate/AGENTS.md`、`agate/assets/templates/task-files.md`、
  `agate/phase-cards/P8-release.md`、`agate/scripts/check-retrospective.py`、
  `agate/state-machine.md`、`agate-workspace/roadmap/roadmap.md`、5 份
  `docs/reviews/retrospective-*.md`；重命名 `docs/reviews/postmortem-template.md` →
  `agate/assets/templates/retrospective-template.md`（git rename，非新建+删除）。
- 本次是首次进入 P4 评审（retry: 0）。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
