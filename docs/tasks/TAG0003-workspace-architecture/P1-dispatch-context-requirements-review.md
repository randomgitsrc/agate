---
phase: P1
generated_by: agate-inject-card.sh + 主 Agent
task_id: TAG0003
role: requirements-review
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
独立评审 docs/tasks/TAG0003-workspace-architecture/P1-requirements.md，产出 docs/tasks/TAG0003-workspace-architecture/P1-review.md（status: approved / rejected / needs-revision）。你是独立视角（agent 角色必须是 requirements-review，不是 analyst），发现 analyst 的作者盲区。

### 约束
- **只审不写**：不直接修改 P1-requirements.md，只产出评审意见。
- 本任务是 **agate 协议自身改造**（dogfooding）：改造对象是 worktree `agate/` 目录，不是 `~/.agate`（稳定版开发工具）。P1 只定义问题，不写实现方案。
- 评审检查清单（见 requirements-review.md 角色定义）必须逐项过：
  - BDD 可二值判定（无中间态）、编号 `#### BDD-NN:` 连续不跳号、每条只有一条 Given/When/Then
  - 隐含需求覆盖：数据/前端/多端/边界/兼容五维度
  - BDD 跨条一致性（同场景多条 BDD 的 Then 是否矛盾）
  - 裁剪合理性（risk_level 与实际风险匹配、phases 声明理由充分、capability_requirements 三态正确）
  - P1 纯净性（无掺入解决方案设计、无混入实现细节）
- 结论必须引用实质锚点：approved 时引用每条 BDD 编号 + 覆盖维度清单；不引用 BDD 编号的裸 "approved" 会被 gate 判假完成。
- 产出文件 Header 必须含 `status:` 字段（approved/rejected/needs-revision），且与返回摘要一致。
- 特别注意本任务的关键风险面（P0-brief known_risks）：
  1. 破坏性变更：现有项目 docs/tasks/ 强制迁移到 agate-workspace/——BDD 是否覆盖迁移工具/指引/幂等/历史保留？
  2. 改动面广（6 脚本 + 16 文档 + 75+ 处引用）——需求是否覆盖 orchestrator 路径改动（project.md 位置）与所有受影响接入方？
  3. roadmap 循环是新增机制——BDD 是否覆盖"roadmap→待开始→立项→回写"闭环？
  4. 工作区内容边界——BDD-17 判据是否可判定、是否防混？
- 禁止行首 `- PASS` / `- FAIL` 格式（provenance 审计会拦截）。

### 上游关联
- analyst 返回摘要：需求基线建立，17 条 BDD，0 待确认项。
- P1-requirements.md 已通过主 Agent 门槛初检（Header 合法 / BDD≥1 / frontmatter 四字段 / 无 NEED_CONFIRM / 无 GAP）。

### 输入文件
- docs/tasks/TAG0003-workspace-architecture/P1-requirements.md（评审对象——必读）
- docs/tasks/TAG0003-workspace-architecture/P0-brief.md（任务简报与风险声明——必读，对照评审）
- /home/kity/.agate/assets/review-roles/requirements-review.md（角色定义——必读）
- docs/reviews/review-design-20260812-1428.md（关键设计文档，roadmap/工作区思路来源——选读）
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
3. 预跑 check-gate.sh P1（exit 2，主 Agent 自判）
4. 更新 .state.yaml phase=P1 → P2
5. git add docs/tasks/{Txxx}/（含 .state.yaml + 产出文件，若 .gitignore 忽略需 git add -f）
6. git commit -m "wf({Txxx}-P1): {摘要}"

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

check-gate.sh P1 → P1-review.md 存在 + status:approved + agent≠main + 含 BDD 编号锚点 → exit 2（BDD 编号格式为 `#### BDD-NN:`）；缺 P1-review.md / agent=main / 无锚点 → exit 1
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
- 环境状态：worktree 是改造对象（分支 dev/workspace，HEAD=5a0a0df）；`~/.agate` → 主 checkout 是稳定版 v0.40.2 开发工具。
- 评审对象规模：P1-requirements.md 236 行，17 条 BDD，risk_level=high，phases 全 8 阶段，packages=[agate]，domains=[backend,cli]。
- 已核实查证：agate/ 下 43 个文件引用 `docs/tasks`；`agate/scripts/` 下 6 个脚本引用；orchestrator-template 的 project.md 路径（`{project_root}/docs/agents/project.md`）需改为工作区内路径。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
