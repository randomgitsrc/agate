> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。

---
phase: P1
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0012
role: requirements-review
retry: 1
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

## 重试 #1（复核修订，本节优先于下方原始派发指引）

上一轮你判定 status: needs-revision，给出 3 处发现（BDD-13 规范/示例混淆、BDD-16/21 缺
AGATE_TDD_TIMEOUT 关系问题、RM-AG0013 在 analyst.md/architect.md 覆盖不对称）。analyst 已针对性
修订，不是重写全文。本轮复核范围**只需聚焦以下改动点**，不必重新逐条核对已判 PASS 的 19 条 BDD
（除非你发现修订过程中意外破坏了它们的语义）：

1. **BDD-13**（新文本，L161-170）：确认是否已正确拆分"L462 规范正文必改"vs"L521 示例块条件性引用"，
   且新增了"与 L790-879 层级2 显式区分"的 Then 子句（第 5 点）。
2. **BDD-16**（L191-198）+ **BDD-21**（L226-230）：确认是否新增了"新字段是否适用于 P3 key、与
   `AGATE_TDD_TIMEOUT` 是何关系"的问题（BDD-16 第 4 点），且未替 P2 拍板具体答案；BDD-21 是否正确
   联动引用而非重复展开。
3. **BDD-15b**（新增，L186-189）：确认是否解决了 architect.md 与 analyst.md 的覆盖不对称，判断
   "引用 P2-design.md 权威定义，不在角色文件重复展开"的落点方式是否与既有 BDD-19 引用模式一致、
   是否合理（analyst 选择了方案①"补 BDD"而非方案②"范围外观察说明"，确认这个选择本身站得住）。

若三点均已妥善解决 → status: approved，按角色文件「实质锚点要求」补齐 approved 结论应引用的锚点
（可复用上一轮 approved 的 19 条 BDD 判定，不必重新展开全部理由，但仍需列出 BDD 编号清单）。
若仍有缺口 → 明确指出具体哪一点未解决，避免笼统打回。

---

### 目标（原始派发指引，重试时仍适用于未涉及修订的部分）

独立评审 analyst 产出的 P1-requirements.md（22 条 BDD，按"文件 → 改动"归并组织，覆盖
RM-AG0013/RM-AG0014（主体+补充）/RM-AG0019/RM-AG0016 五条已核实的 agate 协议机制缺口）。
只审不改，产出 P1-review.md，交主 Agent 判定门槛。

### 约束

1. 本任务是 agate 自身的协议机制改动（非常规业务功能）——检查清单中"前端维度/UI/UX"相关项
   （frontend 任务专属检查点）不适用，`domains: [process]`、无 frontend，跳过 UX 类别 BDD /
   `ui_render_shape` / vision 能力声明相关检查，不要因为找不到这些内容而打回。
2. **重点审查以下三类风险点**（P0-brief known_risks 已预警，是本任务最容易出错的地方）：
   a. **BDD 是否真的按"文件 → 改动"归并、无重复定义**——检查是否有两条 BDD 描述同一份文件的
      同一处改动（应引用而非重复展开），检查是否有遗漏的重叠文件（如 P0-brief 提到的
      phase-cards/dispatch-protocol/state-machine/execution-roles 是否都有对应 BDD 覆盖）。
   b. **"新增机制设计"类 BDD（RM-AG0014 失败处理协议 / RM-AG0019 重启判定标准 / RM-AG0016
      阈值基准）是否越权写死具体数值**——P1 只应界定"设计必须回答哪些问题"，不应替 P2 拍板
      具体轮次数/秒数阈值。若发现 BDD 已经写死具体数值（如"止损轮次=3"），应打回。
   c. **BDD 的 Given/When/Then 是否可二值判定**——协议文档类 BDD 常见问题是判据落在"内容读起来
      是否合理"这种主观标准上；核实每条 BDD 的 Then 是否落在"可被 grep 命中的关键词/章节存在性"
      或"字段格式合法性"等客观可判定的锚点上，而非"表述清晰""逻辑合理"这类主观描述。
3. **同类扫描覆盖度是本任务的核心验收点之一**——检查 P1-requirements.md 第 0 节"同类扫描核实
   结论"与第 7 节"范围外观察"是否体现了对 objective_info 起点之外的独立深挖（不是照抄主 Agent
   预跑的 grep 结果），若第 0/7 节内容空洞或只是重复 objective_info，应在评审意见中指出。
4. **裁剪评审**：analyst 声明"不裁剪任何阶段"（`phases` 全量），需要核实裁剪说明中的理由是否
   充分（尤其 P3 的条件化论证——协议文档改动为何仍不裁 P3），不能只看结论。
5. 评审产出必须按角色文件「实质锚点要求」逐条引用 BDD 编号（1-22）+ 覆盖维度标注，不允许裸
   "approved"。

### 上游关联

analyst 在补充同类扫描中发现的关键结论（供评审时交叉核对，不代替自行核实）：
- RM-AG0016（运行时管控）在协议里已有三层既有 timeout 机制（P3 的 `AGATE_TDD_TIMEOUT` / P6
  Playwright 脚本内部硬超时 / state-machine 的 `failure_mode: timeout`），本任务补的是第四层
  （subagent 执行 bash 命令级别的超时兜底）——评审需确认 BDD-13/14/16/21/22 是否清楚地把新机制
  与既有三层区分开，避免混淆。
- RM-AG0016 被拆成"声明层"（timeout_seconds 字段，落 P2-design.md/architect.md/task-files.md）
  和"执行纪律层"（dispatch-prompt 命令超时兜底行为，落 dispatch-protocol.md/dispatch-prompt.md）
  两个独立机制——评审需确认这个拆分在 BDD 里体现清楚，没有两层混写在一条 BDD 里。
- `agate/dispatch-protocol.md` L691-695 已有「4. 并行规则」权威节（TAG0014 建立），RM-AG0016
  的"资源密集型默认串行"被 analyst 定位为该节的**追加条目**而非新建小节——评审需确认 BDD-12
  没有重复定义已有的并行规则内容。

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0012-protocol-mechanism-fixes/P1-requirements.md（评审对象）
- {AGATE_WORKSPACE}/tasks/TAG0012-protocol-mechanism-fixes/P0-brief.md（对照需求是否忠实翻译、有无擅自扩大范围）
- {agate_root}/assets/review-roles/requirements-review.md（评审角色定义，检查清单权威来源）
- {project_root}/AGENTS.md（项目约定）
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
- 环境状态：worktree 基线已验证，评审为纯只读文档审查，无需环境启动。
- 评审对象：P1-requirements.md 含 22 条 BDD（BDD-1 至 BDD-22），11 个文件分组（A-K），
  frontmatter 声明 risk_level: high / phases 全量不裁 / domains: [process] /
  packages: [phase-cards, dispatch-protocol, state-machine, execution-roles, templates, scripts] /
  capability_requirements 三条均 status: available。正文含 `[NO_NEED_CONFIRM]`（第 4 节）+
  1 条已采纳的 `[SUGGEST:]`（第 2 节第 6 点，关于同类扫描机制不追溯历史产出）。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
