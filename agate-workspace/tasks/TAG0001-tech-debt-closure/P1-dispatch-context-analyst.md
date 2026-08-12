---
phase: P1
generated_by: agate-inject-card.sh + 主 Agent
task_id: TAG0001
role: analyst
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
产出 docs/tasks/TAG0001-tech-debt-closure/P1-requirements.md——把 P0-brief 的"agate 技术债登记闭环（Phase 1-3）+ tech-debt.md 落独立 debt/ 目录"转化为需求基线：需求复述 + 隐含需求识别 + BDD 验收条件（Given/When/Then，每条可二值判定）+ 待确认清单 + 裁剪说明 + 能力需求声明。

### 约束
- 本任务是 **agate 协议自身改造**（dogfooding）：改造对象是 worktree `agate/` 目录（**已含 TAG0003 工作区架构 + TAG0002 refactor 机制的完整改动**），`~/.agate` 是稳定版 v0.40.2 开发工具（禁止改动）。P1 产出属于需求层，不写实现方案。
- **任务内容（Phase 1-3 + 归类修正，P0-brief 已确认）**：
  - **Phase 1**：`assets/templates/tech-debt-template.md`（下游项目放 `{AGATE_WORKSPACE}/debt/tech-debt.md`）+ `agate-debt-check.py` + `check-debt.sh` schema 校验（必填字段、枚举、`evidence` 非空、`closed` 必须有 `task_id` 与证据引用）+ review 角色卡追加"提债须用标准 DEBT 条目格式" + **T001 复盘 T1-T4 回填验证模板**
  - **Phase 2**：回退事件强制建条目——`git log` 提取 `retreat:` 提交与 `tech-debt.md` 中 `source: retreat` 条目比对，缺失 WARNING；`phase-cards/` 回退卡片 + `rules/state-transitions.md` 明确"回退落地后必须建 DEBT 条目"
  - **Phase 3**：P8 锚定——`phase-cards/P8-release.md` 增加"确认债务清单"一步（结果写入 P8-release.md，**只查留痕不查内容达标**）；`check-gate.sh` P8 分支增加留痕检查
  - **归类修正（本次新发现问题，用户确认纳入）**：tech-debt.md 落**独立 `debt/` 目录**（`{AGATE_WORKSPACE}/debt/tech-debt.md`）——修正 TAG0003 把 tech-debt 归入 agents/ 的粗略归类。**agents/ 只放 agent 输入知识（project.md/memory）；tech-debt 是流程产出的项目状态记录（有状态机/schema/被脚本读写），归独立 debt/ 目录**。同步：WORKFLOW.md 目录图（agents/ 注释去 tech-debt + 新增 debt/ 子目录）、工作区初始化 mkdir（8 子目录 → 9，或按设计决策）、SETUP/UPGRADING 同步。
- **P0-brief 2026-08-12 更新（必须遵守，不得推翻）**：
  1. **tech-debt.md 落独立 debt/ 目录**（见上，用户确认）
  2. **change_type: refactor 已由 TAG0002 实现**——TAG0001 不需要再做该字段；但要基于最新协议构建（agate-frontmatter-check.py 已有 change_type schema），不得回退
  3. **在 dev/workspace 分支上增量**：协议文件已被 TAG0003/TAG0002 改动，P4 实现须在其上增量，不改动已验收功能（**除本次显式修正的 tech-debt 归类**）
- **关键设计决策（review-20260812-1204.md，需求必须覆盖）**：
  - 唯一新增硬强制 = 回退事件必须建 DEBT 条目（客观事件，逻辑上不可能误报）
  - 三态状态机（open/in_progress/closed），不用七态
  - `evidence` 必填（schema 强制）
  - 债 vs 缺陷判据："不修它，当前任务的验收声明会不会变成假的？"——会→缺陷走任务内；不会但让未来变更更贵→登记 DEBT；都不影响→不登记
  - P8 只强制"看过并留痕"，不阻断发布（防 Goodhart）
  - 止损：T001 回填失败=模板设计错；P8 空确认连续 3 次=移除强制
- **归类修正的设计依据（需求须体现）**：tech-debt 是项目状态记录（有状态机/schema/被脚本读写/有生命周期），不是 agent 输入知识（project.md/memory 是静态配置/记忆）。`debt/` 是独立命名空间，与 agents/（知识）、roadmap/（前瞻规划）、reviews/（评审本身）语义分离；当前只放 tech-debt.md 单文件（YAML 块 + 正文，便于人读全貌），目录为未来扩展留空间（拆条目/归档/统计）。
- BDD 描述用户/系统行为，不绑定实现细节；可二值判定；隐含需求过数据/多端/边界/兼容维度。
- 拿不准方向标 `[NEED_CONFIRM]` 或 `[SUGGEST: ...]`；无待确认写 `[NO_NEED_CONFIRM]`。
- capability_requirements 三态判断：本任务能力均可用（bash/python3/pyyaml/bats 环境齐全），无 GAP。
- 禁止行首 `- PASS` / `- FAIL` 格式（provenance 审计拦截）。

### 上游关联
- P0-brief 已完成（四字段齐全，2026-08-12 两次更新：① 对齐 TAG0003/TAG0002 最新协议 ② tech-debt 落独立 debt/ 目录 + 修正 agents/ 归类），phase 状态机在 P0，本任务是 P1 首次派发。
- 无上一阶段 subagent 摘要（P0 由主 Agent 亲自写）。

### 输入文件
- docs/tasks/TAG0001-tech-debt-closure/P0-brief.md（任务简报与风险声明——**P1 主要输入**）
- docs/reviews/review-20260812-1204.md（技术债闭环完整设计 Phase 1-3 + 强制力 + 止损——**必读**，任务内容来源）
- AGENTS.md（项目约定：双工作区纪律、测试命令、commit 规范——必读）
- agate/WORKFLOW.md（工作区目录规范——必读，tech-debt 归类修正的落点）
- agate/orchestrator-template.md（工作区路径语义——选读）
- agate/ 目录本身（了解协议现状：frontmatter-check.py 已有 change_type、check-gate.sh P8 分支、phase-cards/P8-release.md 结构——按需读取，不要整目录全读）
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
- 环境状态：worktree 是改造对象（分支 dev/workspace，HEAD=TAG0002-READY commit，已含 TAG0003 工作区架构 + TAG0002 refactor 机制）；`~/.agate` → 主 checkout 是稳定版 v0.40.2 开发工具（禁止改动）。
- 版本隔离三条铁律：改协议只改 worktree 的 `agate/`；跑 gate/读卡片用 `~/.agate`（原版规则）；跑测试用 worktree 本体（load.bash 反推 AGATE_ROOT 到 worktree）。
- 测试基线：worktree 全量 bats 654 用例全绿（TAG0003 631 + TAG0002 新增）；count-tests.sh 基线 648 + sanity 6。
- 已核实查证：TAG0003 工作区规范 agents/ 含 tech-debt（WORKFLOW.md L85"agent 知识（project.md / memory / tech-debt）"）——本次修正为 agents/ 只留 project.md/memory，tech-debt 归独立 debt/；TAG0002 已实现 change_type（agate-frontmatter-check.py P1 schema 含 change_type 枚举）；worktree 全量 654 用例绿。
- 任务编号：TAG0001（本任务），DEBT 条目编号格式 DEBT0001（设计文档 §5.1）。
- 协议目录结构：agate/ 含 WORKFLOW.md / dispatch-protocol.md / state-machine.md / role-system.md / git-integration.md / platform-notes.md / LIMITATIONS.md / orchestrator-template.md / phase-cards/ / assets/（execution-roles + review-roles + templates）/ scripts/ / tests/ / AGENTS.md / adr.md / CONTEXT.md / SETUP.md / UPGRADING.md / rules/。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
