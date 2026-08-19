---
phase: P4
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0016
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 这是 P4-review 修复轮

`P4-review.md` 发现 2 个 CRITICAL + 4 个 INFORMATIONAL。本轮**必须修复 2 个 CRITICAL**（否则
P4 门槛不通过），INFORMATIONAL 4 条按你的判断处理（成本低的建议顺手修，不强制）。

### 修复目标 1（CRITICAL-1）：`audit7_p5_evidence_reuse` 未检查 `git diff` 返回码

`check-p6-provenance.py:179` 附近，`_run_git` 返回 `(stdout, returncode)`，但调用方只用了
`stdout`，从未检查 `returncode`。当 `p5_commit` 是 `git diff` 无法解析的哈希（历史被 rebase/
squash 移除、`.state.yaml` 手工写错、CI 浅克隆导致该 commit 不在本地历史）时，`git diff` 失败
返回空 stdout + 非 0 返回码，当前实现把空 stdout 误判为"无改动"→`reuse_allowed`——本该强制重跑
的场景被静默放行。review 已用真实构造（伪造不存在的 40 位哈希）复现此问题。

**修复方案（选项 A，fail-closed，review 推荐，请采用）**：检查 `_run_git` 返回的 returncode，
非 0 时不能走"无改动"分支，判定为 `"reuse_blocked"`（与 `no_reuse_claim_possible` 的保守语义
一致：宁可多跑不可少跑），并向 stderr 写清楚的诊断信息（区分"git 命令失败"与"确实检测到改动"，
方便排查，不要让两种不同性质的失败混在同一条 stderr 消息里）。

修复后需要新增至少 1 条测试覆盖"git diff 命令本身失败"这个路径（用不存在的伪造 commit 哈希构造
场景，断言返回 `reuse_blocked`），review 已指出现有 4 条核心测试都没有覆盖这条路径。

### 修复目标 2（CRITICAL-2）：`redeclares_table` 无范围全文扫描的误报风险

`check-protocol-consistency.py:944-956`（`redeclares_table`）对指针文件做全文无范围
`finditer` 扫描，而同一 CHECK 里的姊妹函数 `extract_md_table_int_column`（行 922-941）已经用
"限定在 `## 重试上限` 小节内"的策略规避了"误吞同形态但语义无关表格行"的问题（P2 批次 B 实现记录
里差点误吞 `state-machine.md` L30 任务追踪表行的真实案例）。`redeclares_table` 没有同样的限定，
存在潜在误报风险（虽然当前 `rules/state-transitions.md` 恰好没有触发，review 明确指出这是"目前
运气好，不是结构上不会发生"）。

**修复方案**：让 `redeclares_table` 采用与 `extract_md_table_int_column` 一致的小节限定策略——
调用前先用同样的"定位 `## 重试上限`（或指针文件里的等价小节，若指针文件根本没有该级别标题，
则维持对全文的扫描但至少复用同一个"小节裁剪"辅助函数，保持两处逻辑一致，不要出现两套不同的
裁剪实现）"逻辑裁剪出对应文本范围，再传给 `redeclares_table` 扫描，而不是直接传整个文件全文。
（若你判断"要求命中行必须连续"是更简单且同样有效的替代方案，也可以采用，但优先尝试与
`extract_md_table_int_column` 复用同一套小节定位逻辑，减少两份可能漂移的实现。）

修复后需要新增至少 1 条测试覆盖"指针文件里存在与重试上限无关、但行形状恰好命中阈值的表格"这一
用例，断言不会被误判为"重新声明权威表格"。

### INFORMATIONAL（非阻塞，按你判断处理，成本低可以顺手做）

- INFO-1：`must_not_redeclare_table` 锚点配置 key 从未被实际读取（死配置）——建议要么实际使用
  该 key 决定是否调用 `redeclares_table`，要么去掉这个 key
- INFO-2：`main()` 无顶层 try/except，文件系统竞态（exists 后 read_text 前文件被删）会导致
  未捕获异常崩溃——可选加固，非本次必须
- INFO-3：`_load_state_yaml` 的 `except Exception` 同时吞掉 ImportError 和 YAML 格式错误两种
  不同性质的失败，无诊断信号——可选区分处理
- INFO-4：`MAX=(\d+)` 正则不限定上下文，未来若阶段卡片新增无关的 `MAX=` 用法可能取错匹配——
  可选加上下文锚定或改用 findall+唯一性校验

### 不要做的事

- 不要碰批次 1/2/3 及 SELF-GATE 修复轮已经改对的其余内容
- 不要改动已有测试的既有断言逻辑（新增测试可以）
- 修完后跑一遍全量 pytest 确认仍然全绿

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
- worktree HEAD：6dd8d6a，工作区干净。
- P4-review.md：{AGATE_WORKSPACE}/tasks/TAG0016-protocol-hygiene/P4-review.md（完整读一遍，
  含具体复现步骤和行号引用）。
- 全量 pytest 当前基线：963 passed / 0 failed / 2 skipped。
</objective_info>
