---
phase: P4
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0016
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 这是 SELF-GATE 修复轮，不是新批次

`docs/reviews/agate-alignment-review-2026-08-19.md`（protocol-alignment-review 对全部 3 个 P4
批次累积 diff 的语义审查）发现 2 项真实 MISALIGNED + 1 项已由主 Agent 裁决的 NEEDS_HUMAN_REVIEW。
本轮只修复这 3 项，不改动其他任何内容。

### 修复目标 1（A1-c，MISALIGNED）：审计 7 在 P8 场景不可操作

`agate/phase-cards/P8-release.md`（M22）和 `agate/dispatch-protocol.md`「全量重跑点审计」（M16）
都描述"读取 `check-p6-provenance.py` 审计 7 判定结果决定 P8 是否可复用证据"，但脚本侧
`audit7_p5_evidence_reuse()` 的返回值从未输出到 stdout，也没有独立 CLI 模式——主 Agent 实际上
拿不到这个判定结果。

**修复方案（已选定，不需要你重新权衡）**：给 `agate/scripts/check-p6-provenance.py` 增加一个
显式模式 `--audit7-only TASK_DIR`：
- 只跑审计 7（`audit7_p5_evidence_reuse`），不跑其余六道审计
- 把三态结果（`reuse_allowed` / `reuse_blocked` / `no_reuse_claim_possible`）打印到 stdout
  （一行，格式如 `AUDIT7_RESULT: reuse_allowed`，供主 Agent `grep` 提取）
- exit code：`reuse_allowed` → 0；`reuse_blocked` → 1；`no_reuse_claim_possible` → 0
  （字段缺失是"无法声明复用"而不是"错误"，静默回退不应算失败退出码，与既有审计 7 主流程里
  `no_reuse_claim_possible` 不报错的语义一致）
- 不改变脚本默认（不带 `--audit7-only` 参数）时的既有行为——六道/七道审计全套逻辑不变，只是
  新增一个可选的独立入口
- 同步更新 `agate/phase-cards/P8-release.md` 和 `agate/dispatch-protocol.md`「全量重跑点审计」
  的措辞，把"读取审计 7 判定结果"这句话改成明确调用
  `python3 agate/scripts/check-p6-provenance.py --audit7-only $TASK_DIR` 并按 stdout 的
  `AUDIT7_RESULT:` 行判定的可执行操作步骤，不再是抽象的"读取判定结果"这种无法落地的表述

### 修复目标 2（A3/A5，MISALIGNED）：verifier.md / dispatch-prompt.md 未同步新机制

审查发现"P5→P6 无代码改动时可引用 P5 证据、不必重跑"这个新选项只落到了
`phase-cards/P6-acceptance.md`（操作卡）和 `check-p6-provenance.py`（脚本），但负责撰写
P6-acceptance.md 的 **verifier 角色卡**（`agate/assets/execution-roles/verifier.md`）和
**派发 prompt 权威源**（`agate/assets/templates/dispatch-prompt.md`「P5/P6 派发追加」节）都完全
没提到这个新选项——verifier subagent 若不靠主 Agent 每次手写 dispatch-context 提醒，根本不知道
有这个选项存在，等于抵消了本任务想要达成的"减少重复测试"效果。

**修复方案**：
1. 在 `agate/assets/execution-roles/verifier.md`「refactor 任务验收口径」小节之后（或 P6 验收
   流程主体部分合适位置）新增一小段（3-5 行）：说明"若 `.state.yaml` 已有 `p5_pass_commit`
   字段且 P5→P6 无代码改动（由主 Agent 跑 `check-p6-provenance.py` 审计 7 判定），verifier 可在
   PASS 行引用 `P5-test-results/` 路径而非独立产出 `regression.log`"。
2. 在 `agate/assets/templates/dispatch-prompt.md`「P5/P6 派发追加」节加一句提示，指向
   verifier.md 的这个新选项（不需要展开完整规则，一句指针即可，避免和 verifier.md 产生第二份
   可能漂移的完整描述——这正是本任务本身在防的反模式）。

### 修复目标 3（A7，已裁决）：新增 ADR-010

审查在 A7 提出"P5→P6/P8 间无代码改动时可复用证据"是一个新的架构原则（在"完整重跑是安全网"的
既有哲学 ADR-004 基础上开的受控例外口子），建议记录为正式 ADR。**主 Agent 已裁决：需要**（这是
工程判断，不是业务方向问题，不需要额外问用户）。

在 `agate/adr.md` 末尾新增 **ADR-010: 受控例外——满足客观可判定条件时允许复用既有验证证据**：
- **语境**：概括 RM-AG0026 的问题（P5→P6→P8 重复全量测试的成本）
- **决策**：允许在"客观可判定条件成立"时复用证据，不重新执行验证；判定标准必须机器可判定
  （呼应 ADR-002），不依赖主观声明（呼应现有"C7 规则：subagent 自我报告不可信"精神）
- **理由**：引用 P2-design.md §3.2 的失败方向保守性论证（不会产生"应重跑却被跳过"的安全漏洞，
  只会产生"该被判定可复用却被误判为需要重跑"这种保守方向的误判）+ R9 残余风险（P5 commit 混入
  非产出文件改动会破坏等价性前提，已有操作纪律缓解）
- **后果**：本次落地为 `check-p6-provenance.py` 审计 7（BDD-12/13）+ P6/P8 两处应用；未来任何
  类似"复用而非重跑"的设计都应参照本 ADR 的判定标准（机器可判定 + 失败方向保守 + 显式声明
  何时不可复用），不是自由发挥的口子
- 具体措辞你自己按 adr.md 现有 ADR-004/ADR-002 的格式风格撰写，不要求逐字照抄本段（本段只是
  内容要点，不是最终文案）

### 不要做的事

- 不要重新审查/质疑 protocol-alignment-review 报告的其余 ALIGNED 结论（A1-a/A1-b/A2/A4/A6 均
  已通过，不需要你重新验证）
- 不要碰批次 1/2/3 已经改对的其余内容
- 不要改动测试代码
- 修完后跑一遍全量 pytest 确认仍然 0 failed（本轮改动不涉及任何测试断言，理论上不会引入新失败）

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
- worktree HEAD：545f45c（批次 3 已 commit），工作区干净。
- 审查报告：docs/reviews/agate-alignment-review-2026-08-19.md（完整读一遍，尤其 A1-c/A3/A5/A7
  四节的原文引用和具体行号）。
- ADR 编号：下一个可用编号是 ADR-010（现有到 ADR-009）。
</objective_info>
