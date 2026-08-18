> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。

---
phase: P1
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0012
role: analyst
retry: 2
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

## 重试 #2（gate 格式微调，本节优先于下方所有内容）

`check-gate.py P1` exit 1，根因见
`{AGATE_WORKSPACE}/tasks/TAG0012-protocol-mechanism-fixes/P1-gate-diagnosis.md`：
第 4 节「待确认清单」第 243 行的散文表述里含字面子串 `[NEED_CONFIRM]`（非行首标记，只是在说"没有
这类项"），触发了 gate 脚本的子串误判（脚本逻辑：全文出现 `"[NEED_CONFIRM]"` 但行首正则匹配数为 0
→ 判定格式不合规）。

**只需改这一处措辞**，不改变任何实质内容（不改 BDD、frontmatter、裁剪结论、review 已 approved
的判定语义）：把第 243 行"无阻塞性 `` `[NEED_CONFIRM]` ``。"这类含裸字面子串的表述，改为不含
`[NEED_CONFIRM]` 这个方括号子串的等价表述（如"待确认清单为空，无阻塞性未决项"），第 241 行的
`` `[NO_NEED_CONFIRM]` `` 行首声明保持不变（这是唯一应该存在的正式标记）。

修改后本地跑一次 `grep -c '\[NEED_CONFIRM\]' P1-requirements.md`（在任务目录下）确认只有第 241 行
`[NO_NEED_CONFIRM]` 因子串包含关系被计入（若担心误判，也可直接确认全文不再含裸 `[NEED_CONFIRM]`
子串，只保留 `[NO_NEED_CONFIRM]` 和 `[SUGGEST: ...]`）。写回同一路径，不重写其他内容。

---

## 重试 #1（needs-revision 修订，历史记录，已完成，本轮无需再处理）

requirements-review 对你上一版 P1-requirements.md 的判定是 `needs-revision`（22 条 BDD 中 19 条
PASS，3 条需修订：BDD-13、BDD-16、BDD-21），完整评审见
`{AGATE_WORKSPACE}/tasks/TAG0012-protocol-mechanism-fixes/P1-review.md`「发现（需修订项，共 3 处）」节。
只需按下述 3 点修订，不要重写全文，不要改动已 PASS 的 19 条 BDD 的判定实质（可微调措辞但不改变
Given/When/Then 的验收语义）：

1. **BDD-13 拆分/明确"规范性主文本 vs 场景示例"编辑目标 + 补层级区分要求**：
   `dispatch-protocol.md` L462（全阶段通用「分阶段落盘」模板，规范正文）和 L521（「非阶段产出的路径
   规范」节下 self-gate/alignment-review 场景的示例代码块）不是同级文本，不能并列要求"两节都新增
   同一段内容"。修订方向：L462 是必改的规范正文；L521 示例块是否需要同步新增，取决于"非阶段产出"
   场景是否也存在 bash 命令挂起风险——若是，应改为"引用 L462 规则"而非重复展开（与 BDD-17/BDD-19
   的引用模式保持一致）。同时 Then 子句要新增一条：新增内容须与 L790-879「Playwright/长时操作」
   既有硬超时机制（层级 2）建立显式的文档内引用区分，避免读者/P4 implementer 混淆"本次新增的
   bash 命令级超时兜底"与"既有 Node 脚本内部硬超时机制"。

2. **BDD-16/BDD-21 补第 4 个子问题——新字段与既有 `AGATE_TDD_TIMEOUT`（P3 层）的关系**：
   `agate_common.py:408` 的 `AGATE_TDD_TIMEOUT`（默认 120s，`check-tdd-red.py` 消费）已经是
   `gate_commands.P3` key 现有的权威超时机制。BDD-16 需补充第 4 个子问题："新增 `timeout_seconds`
   字段是否适用于 `gate_commands.P3`；若适用，与既有 `AGATE_TDD_TIMEOUT` env var 是互斥
   （`timeout_seconds` 存在时优先覆盖）、叠加、还是字段本身排除 P3（P3 继续用 env var，
   `timeout_seconds` 只服务 P5/P6/其他新 key）"——具体决定仍留给 P2 architect，本 BDD 只要求
   "问题清单必须完整覆盖这一层级关系"，不要替 P2 拍板答案。BDD-21（task-files.md 样例块）联动
   同步：字段注释若涉及 P3 key，需附带指向 BDD-16 该关系说明的引用。这正是你自己在 P1-requirements.md
   第 0 节第 1 点已经发现的"层级 1 vs 层级 4"区分——上一版只停留在你的分析认知里，没有落进 BDD 的
   Then 判据，这次要补上。

3. **RM-AG0013 在 analyst.md（BDD-7）与 architect.md 之间的覆盖不对称，需二选一处理**：
   `architect.md` 全文 grep "影响面"/"同类" 零命中，P2-design.md 卡片被 BDD-15 要求新增"影响面梳理"
   强制节，但 architect.md（P2 执行角色文件）没有对应 BDD 要求同步新增检查项——不同于 analyst.md
   得到"卡片 + 角色文件"两处落地，P2 侧只有卡片一处。二选一：①补一条 BDD（可并入 BDD-15 或新增
   BDD-15b）要求 architect.md 同步新增"影响面梳理"检查项，与 analyst.md 处理方式对称；②若你认为
   architect 的"影响面梳理"本来就该完全靠 P2-design.md 卡片驱动、不需要角色文件层重复（这是合理
   的设计选择，但必须显式说明理由），则在第 7 节「范围外观察」或 BDD-15 的 Given 中明确写出这一
   设计选择及理由，不要留空。

修订完成后，重新自检：3 条修订项是否已解决、19 条 PASS 的 BDD 判定语义未被破坏、frontmatter/
NEED_CONFIRM 状态是否仍然一致。修订后仍写回同一路径
`{AGATE_WORKSPACE}/tasks/TAG0012-protocol-mechanism-fixes/P1-requirements.md`（覆盖原文件）。

---

### 目标（原始派发指引，重试时仍适用于未涉及修订的部分）

产出 P1-requirements.md：把 P0-brief.md 中已核实的 5 条协议机制缺口（RM-AG0013 同类扫描机制缺失 /
RM-AG0014 verification_env 边界+失败处理协议+环境准备职责 / RM-AG0019 P0-brief 时效性验证 /
RM-AG0016(原 RM-AG0023) 运行时管控）转成一份**按"文件 → 改动"归并**的需求基线，含可验证的
BDD 验收条件、能力声明、裁剪声明。这四条本身是"协议机制增强"，产出物是**协议文档/阶段卡片/脚本
的行为规格**，不是常规业务功能——BDD 描述的是"协议使用者（主 Agent/subagent）应该被要求做什么"，
不是"用户点了什么按钮"。

### 约束

1. **合并规划，不按 RM 编号平铺写四份需求**——P0-brief known_risks 已指出五条改动面高度重叠于
   `agate/phase-cards/*.md`、`agate/dispatch-protocol.md`、`agate/state-machine.md`、
   `agate/assets/execution-roles/analyst.md`、`agate/assets/execution-roles/verifier.md`。
   BDD 组织方式必须先按"改哪个文件"分组，再在每个文件分组下列清楚该文件承接哪几条 RM 的哪些改动点，
   避免同一文件在不同 BDD 里被分别描述导致后续阶段重复改、改漏。
2. **【强制】同类扫描已部分由主 Agent 预跑**（见下方 objective_info 客观查证结果），但这只是起点
   覆盖面，不是完整结论——analyst 必须自己针对每条 RM 补充验证/深挖，不能只搬用 objective_info 的
   结论。若发现 objective_info 遗漏的同类文件（如某个未被 grep 到但语义相关的角色文件/模板），
   必须补进 BDD 的影响面。用户明确要求：这一批任务本身要做"同类扫描"的示范，不接受"改一处漏同类"。
3. **不得扩大范围**——P0-brief 已锁定 5 条问题（RM-AG0013/RM-AG0014 主体/RM-AG0014 环境准备职责补充/
   RM-AG0019/RM-AG0016）。分析中若发现范围之外但相关的协议缺口，记录在 P1-requirements.md 的
   "范围外观察"小节，不纳入本任务 BDD，不擅自扩大 packages/domains。
4. **RM-AG0014 的失败处理协议、RM-AG0019 的重新立项判定标准、RM-AG0016 的 timeout_seconds
   阈值基准**——这三个是"新增机制设计"，P1 只需要把"要设计什么、设计必须满足什么约束/边界条件"
   写成 BDD（可验证：文档里能查到该规则 + 规则覆盖到 P0-brief 列出的场景），具体规则数值/文案
   由 P2 architect 设计，P1 不要越权写死具体阈值（如"CI 轮次预算=3 轮"），但可以写清楚设计必须回答
   哪些问题（如"止损轮次是多少、由谁判定、超限后状态转移到哪"）。
5. **domains** 只会是 `[process]` 或类似的"协议/流程"域（这是 agate 自身的协议机制改动，不是常规
   backend/frontend 代码），不要套用业务项目的 backend/frontend 分类；`packages:` 用改动涉及的
   agate 子目录归类（如 `phase-cards`、`dispatch-protocol`、`state-machine`、`execution-roles`）。
6. **risk_level**：本任务改的是协议文档 + 少量脚本 schema 字段（`timeout_seconds`），无破坏性
   数据迁移，但改动面广（触发 SELF-GATE，多个已有任务/自动化流程依赖这些文件的既有行为）——按
   protocol 类任务惯例定级，并说明理由。
7. **phases 裁剪**：本任务几乎不产出可执行代码变更（只有 gate_commands/dispatch_plan schema 若
   有校验脚本才涉及代码），P3 TDD 阶段是否可裁剪/如何适配"协议文档变更"取决于是否有配套脚本改动
   （如 `timeout_seconds` 字段若被某 gate 脚本读取校验，则该脚本改动仍需 TDD 红灯）。analyst 需
   先判断 RM-AG0016 是否要求脚本层改动（不只是文档描述），据此声明 phases。
8. **capability_requirements**：本任务是纯文档/协议改动，无需 browser-vision 等特殊能力，正常声明
   `available` 或省略，不要因为任务名带"运行时管控"就误判为需要真实并发/超时环境验证能力——
   Linux 静态修复 + 现有 pytest 回归即可验证协议文档描述与脚本行为一致，不需要真实卡死场景复现。
</dispatch_guide>

<!-- AGATE_CARD_START -->
## 当前阶段卡片：P1

路径：phase-cards/P1-requirements.md
---
# P1 — 需求基线

> 当前状态：[首次 / 重试 #N]
> P1 不可裁剪（核心阶段）

## 如果是首次进入本阶段

1. 派发 analyst subagent → 产出 P1-requirements.md
   1.1 写 P1-dispatch-context-analyst.md（派发指引：目标/约束/上游关联/输入文件 + 客观查证信息）
2. 主 Agent 确认：BDD 验收条件 ≥1 条 + 无未决 NEED_CONFIRM
2.5 派发 requirements-review subagent（角色文件：{agate_root}/assets/review-roles/requirements-review.md）
     2.5.1 写 P1-dispatch-context-requirements-review.md（派发指引：目标/约束/上游关联/输入文件 + 客观查证信息）
    输入：P1-requirements.md
    产出：P1-review.md（agent≠main，含 BDD 编号引用 + 覆盖维度标注）
    review 不通过 → analyst 修改 → 再 review → … → approved（⑩迭代循环）
3. 预跑 check-gate.py P1（exit 2，主 Agent 自判）
4. git add {AGATE_WORKSPACE}/tasks/{Txxx}/（含 .state.yaml + 产出文件，若 .gitignore 忽略需 git add -f）
   ⚠️ 此时 .state.yaml 的 phase 保持 P1，不要提前写 P2——phase = 本 commit 的产出阶段
5. git commit -m "wf({Txxx}-P1): {摘要}"（phase=P1，P1 产出含 P1-requirements.md + P1-review.md）
6. P1 commit 完成后进入 P2：**phase 推进 P2 随 P2 产出 commit 一起**（P2-design.md + P2-review.md 就绪后），不是单独 phase commit

## 如果是重试

确认上一轮失败原因（BDD 不完整 / domains 声明错 / NEED_CONFIRM 未处理）
→ review 不通过时：analyst 修改需求 → 重派 requirements-review → 共享 retry 预算
→ 读 agate/rules/state-transitions.md 确认 retry 上限（P1 MAX=3）

## 前置条件

- [ ] P0-brief.md 完成（四字段齐全）

## 派发

- **角色**：analyst（`{agate_root}/assets/execution-roles/analyst.md`）
- **输入**：P0-brief.md（env_constraints / known_risks / executor_env）
- **输出**：P1-requirements.md
- **派发 prompt 模板**：`{agate_root}/assets/templates/dispatch-prompt.md`

## 复杂需求编排（模式 4，条件触发）

需求复杂（多来源 / 多模块 / 无法预先拆清范围）时，P1 可先派**侦察 subagent**（模式 4 先理解后拆，见 dispatch-protocol「派发编排机制」）读全貌后再拆需求：

1. 侦察 subagent 读 P0-brief + 相关上下文，产出拆分方案（拆成哪些子需求、各子需求的输入/产出/依赖）
2. 按方案派 analyst（并行或串行）分别产出需求基线
3. 合并时定义**合并语义**（在侦察产出中声明，P7 一致性检查依赖）：
   - **BDD 全局编号**：各子需求承接的 BDD 编号全局唯一（`#### BDD-NN:`），不允许各子需求各自从 1 编号
   - **包归属去重**：每个 BDD 明确归属唯一包，跨包的共享件单独列出，不允许两个子需求各写一份

## 产出规格

P1-requirements.md 必须包含：
- BDD 验收条件（至少 1 条，Given/When/Then 格式）
- `domains:` 声明（backend / frontend / mcp / security）
- `packages:` 声明（受影响的包/模块）
- `risk_level:` 声明（low / medium / high）→ 决定 P2 评审强度
- `phases:` 裁剪声明（跳过哪些阶段 + 理由）
- `capability_requirements:` 能力需求声明（available / supplementable / GAP 三态）
- 无未决 `[NEED_CONFIRM]`（有则 PAUSED）；无待确认项时写 `[NO_NEED_CONFIRM]`

`risk_level`/`phases`/`packages`/`domains` 写在文件头 **frontmatter**（`---` 分隔块），不写正文。
**可直接复制的完整样例**：
```yaml
---
phase: P1
task_id: TAG0001           # 替换为实际任务编号
type: problems
parent: P0-brief.md
trace_id: T001-P1-20260101 # {task_id}-P1-{YYYYMMDD}
status: draft
created: 2026-01-01
agent: analyst
# ── v2.0 机器字段 ──
risk_level: low             # low / medium / high，必填
phases: [P1, P4, P5, P6, P8]   # list of P\d+，必填
packages: [pkg-a]           # list，必填
domains: [backend, frontend]  # list，必填
# 可选字段：override / implicit_coupling / coupling_checklist / internal_only /
# internal_only_reason / 跳过风险 / design_trivial / follows_existing_pattern
# ── v2.0 refactor 任务类型声明（可选，缺省 = 功能任务）──
# change_type: refactor   # 当前仅支持 refactor；枚举非法值由 frontmatter schema 拦截
# ── TAG0006 UI/UX 渲染形态声明（可选，presence 语义：缺失 = 常规布局型默认，不红基线）──
# ui_render_shape: render_component   # str，规范形态值：layout（布局型）/ render_component
#                                     # （渲染组件型，仅举例 OpenGL/WebGL/Canvas/图表/模型/特效/
#                                     #  地图/数字地球）/ temporal_effects（时序特效型）；开放集合可扩
# ui_ux_dimensions: [渲染正确性, 动效时序]  # list，从 UX 分类框架选适用维度；渲染组件/时序特效
#                                     # 类形态必填，常规布局型可省略
# ── v2.0 标记"已解决/已确认"状态（可选，仅标记存在时写）──
# need_confirm_resolved: []   # list[str]：已解决的 NEED_CONFIRM 项描述（逐条匹配正文）
# suggest_resolved: []        # list[str]：已采纳的 SUGGEST 项描述
# scope_resolved: []          # list[str]：已解决的 SCOPE+ 项描述
---
```

**UX 类别 BDD 与分类框架（domains 含 frontend 时必做）**：frontend 任务的 P1 必须含至少一条
UX 类别 BDD，并按实际 UI/渲染形态声明 `ui_render_shape` + 从 **UX 分类框架**（布局结构/
渲染正确性/交互行为/动效时序/视觉呈现等示例性开放集合）选 `ui_ux_dimensions` 维度，类别写入
BDD 标题后缀（如 `#### BDD-3: 渲染正确性：...`）。判据必须可量化（渲染正确性 → 渲染结果对比 +
diff 阈值或输出断言；时序 → 帧/时间戳对齐；动效 → 过渡/动画关键帧与结束状态断言；手势交互 →
动作输入的坐标/参数量化），禁主观词。缺失形态声明/维度选择/UX BDD → requirements-review 打回，
P1 gate 在"声明了形态但维度为空"或"维度不在分类框架且未在 BDD 标题声明"时 exit 1。

**NEED_CONFIRM 分级**：
- `[SUGGEST: 推荐 X，理由 Y]` - 有倾向但求确认。主 Agent 可自行采纳倾向（除非涉及破坏性变更/业务方向），不必问用户
- `[NEED_CONFIRM]` - 真无方向需人定夺。阻塞推进，主 Agent 问用户

## gate 规则

check-gate.py P1 → P1-review.md 存在 + status:approved + agent≠main + 含 BDD 编号锚点 → exit 2（BDD 编号格式为 `#### BDD-NN:`）；缺 P1-review.md / agent=main / 无锚点 → exit 1
P1 评审不可裁——所有任务都走独立 requirements-review，无例外

## 推进条件（全部满足才写 phase: P2）

- [ ] P1-requirements.md 含 BDD ≥1 条
- [ ] domains / packages / risk_level / phases 已声明
- [ ] 无 [NEED_CONFIRM] 标记
- [ ] 无 status: GAP（supplementable 不阻，GAP 阻）
- [ ] P1-review.md status: approved（agent≠main，含 BDD 编号锚点）

## 常见错误

1. **BDD 写成技术实现而非用户行为**：BDD 应该描述"用户能看到什么/系统应该做什么"，不是"调用哪个 API"
2. **domains 声明不全**：漏了某个受影响域 → P2 不派该域的评审 → 实现方向错误
3. **capability_requirements 漏声明**：P6 验收时才发现需要但不可用的能力 → 返工。**frontend 任务
   漏声明 vision 视觉能力条目（need 含 visual/vision）→ P1 gate exit 1 硬拦**（check-gate.py
   `_gate_p1_vision_capability`）；声明形态但漏选维度 / 形态声明与 UI/渲染形态不符 →
   同样 exit 1
4. **gate 不过 ≠ 你失败了**：红灯指向工作/设计的问题，不指向你。正确动作是诊断→退回/重试/PAUSED，不是修改产出让它变绿。

## 下游影响

- P2 设计依赖 domains + risk_level 决定评审角色
- P6 验收逐条对照 P1 的 BDD（PASS/FAIL 总数必须 ≥ P1 BDD 总数）
- P7 一致性检查依赖 packages 声明做跨文件交叉核对

## 评审

P1 评审通用必有（所有任务都走 requirements-review），P2/P4 评审是 C8 域触发（见 review-mapping.md）——二者在"是否通用"上不对称，仅在"独立 subagent、agent≠main"上类比。P1 评审不可裁剪。
review 不通过 → analyst 修改需求 → 再 review（⑩迭代循环），直至 approved。

> 完成 → 读 phase-cards/P2-design.md


## P1 基线保护

P1-requirements.md 是需求基线，后续阶段（P2-P8）不应直接修改。如需变更（如 P4 发现 BDD 矛盾需补充注释），必须：
1. 主 Agent 显式批准
2. 在变更处标注 `[BASELINE_CHANGE: 理由]`
3. 不改 BDD 的 Given/When/Then 语义（只补充注释/优先级说明）
<!-- AGATE_CARD_END -->

<objective_info>
- 环境状态：worktree 基线已验证（865 pytest 全绿，`check-protocol-consistency.py --strict` 0 ERROR），
  可直接在 worktree 内做只读 grep/Read 调研，无需额外环境启动。
- 关键路径：
  - 阶段卡片目录：`agate/phase-cards/P0-orchestrator.md` … `P8-release.md`
  - 派发协议权威文件：`agate/dispatch-protocol.md`
  - 状态机权威文件：`agate/state-machine.md`
  - 执行角色文件：`agate/assets/execution-roles/*.md`（analyst.md / verifier.md 等）
  - 派发 prompt 模板：`agate/assets/templates/dispatch-prompt.md`

- 主 Agent 已预跑的同类扫描（起点，非完整结论，analyst 需自行补充深挖）：

  1) RM-AG0013（同类扫描/影响面机制缺失）—— `grep -ln "同类扫描\|影响面\|全仓 grep\|同类风险" agate/phase-cards/*.md`
     **零命中**：P0-P8 全部 9 张阶段卡片均无此类关键词，证实"机制层完全缺失"（不是"部分卡片缺"）。

  2) RM-AG0014（verification_env 边界）—— `grep -rn "verification_env" agate/*.md agate/phase-cards/*.md agate/assets/**/*.md`
     命中仅 3 处，全部集中在：
       - `agate/assets/execution-roles/verifier.md:252`（"verification_env 条件化"，仅描述何时需要声明该字段）
       - `agate/dispatch-protocol.md:952,957`（"verification_env 条件化"节，同样只定义"何时需要声明"）
     即：verification_env 目前**只在 P5/P6 verifier 场景**被提及，且只回答"要不要声明"，完全不涉及
     "声明后验证失败怎么办"、也完全不出现在 P1 analyst 的职责范围/文档中——与 P0-brief 描述的
     "P1 analyst 需加 supplementable vs verification_env 边界注"现状一致（P1 阶段目前对此零覆盖）。

     对照：`grep -rln "supplementable"` 命中 12 个文件（`phase-cards/P1-requirements.md`、
     `dispatch-protocol.md`、`assets/review-roles/requirements-review.md`、
     `phase-cards/P6-acceptance.md`、`assets/execution-roles/verifier.md`、
     `assets/templates/task-files.md`、`LIMITATIONS.md`、`WORKFLOW.md`、
     `assets/execution-roles/analyst.md`、`role-system.md`、
     `assets/templates/dispatch-prompt.md`、`state-machine.md`）——supplementable（能力缺失三态）
     覆盖面远大于 verification_env（环境依赖声明），两个概念当前在文档里没有相互引用/边界说明，
     这正是 TAG0009 用错机制（该用 verification_env 却标 supplementable）的文档层根因。

  3) RM-AG0019（P0-brief 时效性）—— `grep -n "P0.*P1" agate/state-machine.md`
     现状：`state-machine.md:77` 转移条件为
     `P0 --[P0-brief.md 完成，四字段自查通过（task/known_risks/executor_env/env_constraints）]--> P1`
     —— 只检查"四字段是否非空"，不检查"字段内容是否仍反映当前项目状态"，证实"检测口径只查完整性
     不查时效性"的问题描述准确。

     `grep -rln "P0-brief"`（除 orchestrator 相关）命中：`phase-cards/P0-orchestrator.md`、
     `phase-cards/P4-implementation.md`、`phase-cards/P1-requirements.md`、`phase-cards/README.md`、
     `adr.md`、`phase-cards/P2-design.md`、`dispatch-protocol.md`、`orchestrator-template.md`、
     `state-machine.md`、`WORKFLOW.md`——这些都是"消费 P0-brief 内容"的点，RM-AG0019 的修复
     （P0→P1 前提校验 + P1 analyst 过时标记）需要确认改动是否要触达这些消费点，还是只在 P0/P1
     转移节点校验即可（analyst 需判断并写清楚）。

  4) RM-AG0016/RM-AG0023（运行时管控）—— 现状扫描：
     - `grep -rn "timeout_seconds"` 在协议文档/脚本中**零命中**——`gate_commands`/`dispatch_plan`
       目前完全没有超时字段，是纯新增设计，不是"补全既有字段"。
     - `grep -n "progress" agate/assets/templates/dispatch-prompt.md` 现状只有"读完一个输入文件
       追加 progress"（第 30/37 行），**没有"每个 bash 命令执行前写 progress"的要求**——证实
       P0-brief 描述的"progress 心跳在命令执行中失效"缺口成立。
     - `grep -n "并行\|串行\|资源" agate/phase-cards/P5-verification.md` 现状已有"按包拆分并行"节
       （113-128 行）和"基础设施隔离（并行时强制）"要求，但**没有"资源密集型默认串行"的判断标准**
       （即什么情况下即使能并行也应该默认串行，如全量 pytest xdist / CDP E2E）——是在已有并行机制
       基础上的**补充**，不是从零设计。
     - `grep -rln "gate_commands\|dispatch_plan"` 命中较广：`adr.md`、`UPGRADING.md`、
       `git-integration.md`、`WORKFLOW.md`、`dispatch-protocol.md`、
       `phase-cards/{P2,P3,P4,P5,P8}-*.md`、`state-machine.md`、`phase-cards/README.md`——
       `timeout_seconds` 若作为 gate_commands/dispatch_plan 的新增可选字段，需要判断是在
       dispatch-protocol.md 一处定义权威语义、各阶段卡片仅引用，还是需要逐张卡片同步描述
       （沿用 agate 现有"权威定义 + 卡片引用"惯例，analyst 需在 BDD 里明确落点，避免 P2 设计阶段
       对着 6+ 个文件平铺去改）。

- 查证结论摘要（供 analyst 参考，不替代自行核实）：五条问题描述与代码/文档现状一致，均有客观证据
  支撑，无需在 P1 阶段重新验证"问题是否存在"，重点放在"BDD 怎么组织 + 影响面是否有遗漏 + 裁剪判断"。

</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
