---
phase: P4
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0016
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

实现 P2-design.md `dispatch_plan` 声明的第 1 批次 **`doc-dedup`**（RM-AG0025 协议文档去重，
complexity: high）：§0 职责声明表落地（M3/M7/M10/M12）+ M1/M2/M4/M5/M6/M8/M9/M11，对应
BDD-1~8。**本批次只改 Markdown 协议文档，不碰 `agate/scripts/*.py`**（CHECK 12/审计 7 是后续
批次的工作）。

本批次目标是让 `agate/tests/unit/test_protocol_dedup_audit.py` 里对应 BDD-1~5/7 的红灯测试
变绿（BDD-6/8 由本批次不直接覆盖测试，见下）。

### 约束

1. **严格按 P2-design.md §1.1 改动清单的 M1-M13 逐行执行**，每行已写明"文件·小节 / 改动 /
   关联 BDD"，不要自己另创方案。M1-M13 具体内容你自己读 P2-design.md §1.1（不在此重复摘录，
   避免和权威源产生第二份可能漂移的摘要）。
2. **指针句措辞统一沿用 3.4 节已验证的正确句式**："详见 {file}《{标题}》——权威唯一来源，本文件
   不重复维护"这类句式（P1-requirements.md 3.4 节 / P2-design.md §0 已引用具体例句，直接抄用
   这个句式风格，不要自创新句式，保持全仓风格一致，也方便后续测试断言"含指针短语"时可靠匹配）。
3. **§0 职责边界声明行格式固定**：`> 职责边界：{一句话职责描述}（详见职责声明表，
   P2-design.md §0）`，插入位置是文件头 H1 主标题下方（`test_protocol_dedup_audit.py` 的
   `test_bdd_1_19_responsibility_boundary_declared` 断言"文件头 20 行内含 '职责边界' 声明"，
   注意插入位置要在前 20 行内）。四个文件（WORKFLOW.md/dispatch-protocol.md/state-machine.md/
   platform-notes.md）各自的"一句话职责描述"直接抄 P2-design.md §0 职责声明表对应列，不要
   自己改写措辞（测试断言会核对内容与 §0 表一致）。
4. **M8（`assets/templates/dispatch-prompt.md` 文件头矛盾声明修正）**：删除"本模板与
   dispatch-protocol.md 保持同步，协议文件为权威来源"，改为"本文件是派发 prompt 的权威来源；
   dispatch-protocol.md 仅保留极简结构提示 + 指针"（P2 §1.1 M8 已给出确切措辞，直接用）。
5. **M6（dispatch-protocol.md「派发 prompt 模板」内联版收窄）**：把当前完整内联模板代码块收窄为
   极简结构提示（阶段名/角色/dispatch-context/输出路径 4 行骨架）+ 显式指针，P2 §1.1 M6 已给出
   措辞方向。收窄后指向 `assets/templates/dispatch-prompt.md` 作为唯一权威源（对应 M8）。
6. **M11（`rules/state-transitions.md`「## 重试上限」改指针）**：删除完整数值表格，改为
   "详见 `state-machine.md`《重试上限》——权威唯一来源，本文件不重复维护"这类指针句（与该文件
   文件头已有的"权威源：state-machine.md"声明保持行为一致）。
7. **M13（8 张阶段卡片的 MAX= 内联行）**：**保留原样，不要改动**——P1/P2 已判定这是"阅读体验
   需要就近可见"，去重方案不动它，留给下一批次的 CHECK 12 纳入检测范围。
8. **不要改动 P1-requirements.md/P2-design.md 判定为"不改"的三处正确指针位置**
   （`dispatch-protocol.md` L972 附近 / `state-machine.md` Pre-commit 指针 / `git-integration.md`
   L162）——这是 BDD-7 的回归防护对象，改了会让 `test_bdd_7_precommit_pointers_unchanged`
   （当前绿）变红。
9. **不改动测试代码**（`agate/tests/unit/*.py`）——P3 红灯是权威判据，不能通过改测试让它变绿。
10. **不涉及 `agate/scripts/*.py`**——CHECK 12（BDD-9/10）和审计 7（BDD-12/13）是后续批次
    `check12-anti-recurrence` / `test-evidence-provenance` 的工作，本批次不要提前实现或改动。
11. **SELF-GATE 提醒（供你自查，不要求你自己跑 protocol-alignment-review）**：本批次改动
    `agate/*.md` 会触发 SELF-GATE，主 Agent 会在全部 3 个批次完成后统一跑一次
    protocol-alignment-review（覆盖完整变更集，而不是逐批次审）。你只需确保改动准确对应
    P2 设计，不需要自己派发语义审查。

### 上游关联

P2-design.md 已 approved（第 2 轮）。P3-test-cases.md 已产出 24 个红灯测试（本批次相关：
`test_protocol_dedup_audit.py` 里的 BDD-1/2/3/4/5/7/19 用例）。dispatch_plan 声明本批次
complexity: high、无前置依赖（第一批）。

### 输入文件

- {AGATE_WORKSPACE}/tasks/TAG0016-protocol-hygiene/P2-design.md（§0 职责声明表 + §1.1 改动
  清单 M1-M13 + §1.2 不改什么 + §1.3 风险表，本批次的完整技术依据）
- {AGATE_WORKSPACE}/tasks/TAG0016-protocol-hygiene/P1-requirements.md（3.1-3.8 同类扫描结论，
  理解每处改动的背景判定）
- agate/tests/unit/test_protocol_dedup_audit.py（P3 红灯测试，实现时对照断言写法确认能让它们
  变绿，尤其字符串匹配的确切措辞要求）
- agate/WORKFLOW.md、agate/dispatch-protocol.md、agate/state-machine.md、
  agate/platform-notes.md、agate/rules/state-transitions.md、
  agate/assets/templates/dispatch-prompt.md（去重对象，读 worktree 自己这份，不要读 ~/.agate）

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
- worktree HEAD：96ee5bd（P3 commit），工作区干净。
- `agate/tests/unit/test_protocol_dedup_audit.py` 当前红灯命令：
  `python3 -m pytest agate/tests/unit/test_protocol_dedup_audit.py -v`（本批次完成后单独跑这个
  文件确认相关用例变绿，不需要等全部 3 批次都完成——BDD-6/8/11/14/15/16/18 相关用例本批次不会变绿，
  这是预期的，不是本批次的失败）。
</objective_info>
