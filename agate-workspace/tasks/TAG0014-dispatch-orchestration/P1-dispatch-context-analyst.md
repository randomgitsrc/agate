---
phase: P1
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0014
role: analyst
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

修复轮（增量模式）：按 P1-review.md 的 F1-F5 修订 P1-requirements.md，使需求基线通过评审。

### 约束

- **增量模式**：本文件是修复轮派发，引用上轮派发约束：
  - 上轮产出：{AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/P1-requirements.md
  - 上轮 dispatch-context：{AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/P1-dispatch-context-analyst.md（其目标/约束/上游关联/输入文件全部继续有效）
  - 本轮只做评审要求的修订，不重写整个需求基线
- **修复目标（P1-review.md 发现清单）**：
  - **[F1 / BLOCKER 必须修]** I1（self-gate 触发）无 BDD 落点。二选一：
    a) 新增 1 条 BDD（如 `#### BDD-22`：Given 完成涉及 agate/*.md + agate/scripts/*.py + phase-cards 的 commit，When 检查该批 commit message，Then git log 显示均含 `self-gate-review:` 且存在 protocol-alignment-review 派发记录）；或
    b) 在 §4（或待确认/裁剪节）显式声明 self-gate 由 hook + 主 Agent 流程兜底、不进 BDD 验收，须给出理由。
    推荐方案 a（plan 验收标准 6 正是这个口径），但最终判断交给你。
  - **[F2 建议修]** BDD-6 Given 补每批 complexity（`batches: [{id: B1, complexity: low}, ...×4]`），使批数超限校验路径独立可达，与 plan test_dispatch_plan_batch_granularity 结构一致。
  - **[F3 建议修]** BDD-15 Given 显式写 `agate/phase-cards/P1-requirements.md`，避免与任务自身同名文件歧义。
  - **[F4 建议修]** BDD-5 Given 的"缺 complexity 或 非法"双子场景：可拆两条独立 BDD（推荐），或保留合并但 P6 需覆盖两子场景（须在 BDD 内注明）。
  - **[F5 建议修]** BDD-20 基线常数改为"≥ 改造前 count-tests.sh 实测基线 + 8"的动态表述，不硬编码 751+ 估算值。
- **修订后须保持**：BDD 编号连续（若新增 BDD-22 则编号顺延到最新）、全部可二值判定、无 [NEED_CONFIRM]、frontmatter 不变（risk_level/phases/packages/domains 除非确有需要否则不动）、影响面表不因修订而残缺。
- **P1 纯净性保持**：修订只影响 BDD 表述与 self-gate 落点，不掺入方案设计。

### 上游关联

- requirements-review 评审结论：P1-review.md（status: needs-revision，BLOCKER=1 F1 + F2-F5 非阻塞）。

### 输入文件

- {AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/P1-requirements.md（修订对象）
- {AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/P1-review.md（评审意见——本轮修订依据）
- {AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/P1-dispatch-context-analyst.md（上轮派发约束，继续有效）
- {AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/P0-brief.md（任务简报）
- {AGATE_WORKSPACE}/plans/agate-dispatch-orchestration-20260815.md（approved plan，参考）
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
# ── v2.0 标记"已解决/已确认"状态（可选，仅标记存在时写）──
# need_confirm_resolved: []   # list[str]：已解决的 NEED_CONFIRM 项描述（逐条匹配正文）
# suggest_resolved: []        # list[str]：已采纳的 SUGGEST 项描述
# scope_resolved: []          # list[str]：已解决的 SCOPE+ 项描述
---
```

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
3. **capability_requirements 漏声明**：P6 验收时才发现需要但不可用的能力 → 返工
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
- 上轮产出：21 条 BDD，[NO_NEED_CONFIRM]（L248），frontmatter risk_level: high / phases 全阶段
- 评审：F1 为唯一 BLOCKER（self-gate 无 BDD 落点）；F2-F5 非阻塞建议
- 环境：pytest 9.0.3；gate 工具 ~/.agate 稳定版；count-tests.sh 实测基线以 worktree 实际输出为准（评审 F5：勿硬编码 751+）
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
