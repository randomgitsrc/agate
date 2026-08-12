---
phase: P2
generated_by: agate-inject-card.sh + 主 Agent
task_id: TAG0001
role: architect
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
产出 docs/tasks/TAG0001-tech-debt-closure/P2-design.md——把 P1 需求基线（20 条 BDD）转化为可实现的"agate 技术债登记闭环 + debt/ 归类修正"方案：候选方案（≥2）与权衡 + 影响域 + gate 命令固化 + files_to_read + minimal_validation。

### 约束
- 本任务是 **agate 协议自身改造**（dogfooding）：改造对象是 worktree `agate/` 目录（**已含 TAG0003 工作区架构 + TAG0002 refactor 机制的完整改动**），`~/.agate` 是稳定版 v0.40.2 开发工具（禁止改动）。P2 设计的是新版协议（worktree agate/ 将改成的样子）。
- **任务内容（Phase 1-3 + 归类修正，P1 已确认 20 BDD）**：
  - **Phase 1**：`assets/templates/tech-debt-template.md`（下游项目放 `{AGATE_WORKSPACE}/debt/tech-debt.md`）+ `agate-debt-check.py` + `check-debt.sh` schema 校验（必填字段、枚举、`evidence` 非空、`closed` 必须有 `task_id` 与证据引用）+ review 角色卡追加"提债须用标准 DEBT 条目格式" + **T001 复盘 T1-T4 回填验证模板**
  - **Phase 2**：回退事件强制建条目——`git log` 提取 `retreat:` 提交与 `tech-debt.md` 中 `source: retreat` 条目比对，缺失 WARNING；`phase-cards/` 回退卡片 + `rules/state-transitions.md` 明确"回退落地后必须建 DEBT 条目"
  - **Phase 3**：P8 锚定——`phase-cards/P8-release.md` 增加"确认债务清单"一步（结果写入 P8-release.md，**只查留痕不查内容达标**）；`check-gate.sh` P8 分支增加留痕检查
  - **归类修正（P1 已确认，用户决策）**：tech-debt.md 落**独立 `debt/` 目录**（`{AGATE_WORKSPACE}/debt/tech-debt.md`）——修正 TAG0003 把 tech-debt 归入 agents/ 的归类。**agents/ 只放 agent 输入知识（project.md/memory）；tech-debt 是流程产出的项目状态记录（有状态机/schema/被脚本读写），归独立 debt/ 目录**。同步：WORKFLOW.md 目录图（agents/ 注释去 tech-debt + 新增 debt/ 子目录）、工作区初始化 mkdir（8 → 9 子目录，涉及 orchestrator-template.md / SETUP.md / active-tasks-template.md 等）、SETUP/UPGRADING 同步。
- **P0-brief 更新（必须遵守）**：change_type 已由 TAG0002 实现（不重复做）；在 dev/workspace 分支上增量（协议文件已被 TAG0003/TAG0002 改动，除本次显式修正的 tech-debt 归类外不改已验收功能）。
- **P1 评审非阻塞观察 4 条**（见 P1-review.md，设计时处理）：
  1. （读 P1-review.md §观察逐条对照）
- **P2 产出规格**（见 architect.md）：frontmatter（candidate_count/packages/domains/ui_affected 必填）+ 正文（候选方案与权衡 + gate_commands/files_to_read/env_constraints/minimal_validation）+ 实现完成标志。gate_commands 在 P2 固化。
- **设计必须解决**：
  - tech-debt.md 的 YAML 块 + 正文混合格式（每条 DEBT 一个 YAML 块供机器校验 + 正文补充供人读）
  - 三态状态机（open/in_progress/closed）与 task_id 承载"是否已立项"
  - `evidence` 必填、`closed` 必须有 task_id + 证据引用的 schema 校验
  - 回退强制：git log 提取 retreat 提交比对 tech-debt.md 的 source: retreat 条目
  - P8 确认债务清单（只查留痕不查内容达标，空确认是合法选项）
  - 工作区 mkdir 8 → 9 子目录的同步面（orchestrator-template.md 初始化、SETUP.md、active-tasks-template.md、UPGRADING.md）
- 设计中发现新隐含需求 → 标 `[SCOPE+]`（行首声明格式）。
- 禁止行首 `- PASS` / `- FAIL` 格式（provenance 审计拦截）。

### 上游关联
- P1 已通过 gate（exit 2）：20 条 BDD（BDD-1..20），risk_level=medium，phases 全 8 阶段，packages=[agate]，domains=[backend,cli]，4 条 SUGGEST，无 NEED_CONFIRM，无 GAP。requirements-review approved。
- P1 确认：tech-debt.md 落独立 debt/ 目录（修正 TAG0003 agents/ 归类）；TAG0002 change_type 已实现（不重复）。

### 输入文件
- docs/tasks/TAG0001-tech-debt-closure/P1-requirements.md（需求基线 + 20 条 BDD + frontmatter——**必读**）
- docs/tasks/TAG0001-tech-debt-closure/P1-review.md（评审意见——必读，理解评审视角 + 4 条观察）
- docs/tasks/TAG0001-tech-debt-closure/P0-brief.md（任务简报与风险声明——必读）
- AGENTS.md（项目约定：双工作区纪律、测试命令、脚本约定——必读）
- docs/reviews/review-20260812-1204.md（技术债闭环完整设计 Phase 1-3——必读，任务内容来源）
- agate/ 目录本身（了解协议现状：WORKFLOW.md 目录图 L85、check-gate.sh P8 分支、phase-cards/P8-release.md、orchestrator-template.md 初始化 mkdir、agate-frontmatter-check.py schema 模式——设计前必须读现有代码再设计）
</dispatch_guide>

<!-- AGATE_CARD_START -->
## 当前阶段卡片：P2

路径：phase-cards/P2-design.md
---
# P2 — 方案设计

> 当前状态：[首次 / 重试 #N / 裁剪跳阶]
> 裁剪跳阶 → P2 不可裁剪。design_trivial / follows_existing_pattern 可简化（1 个候选方案），不可省略。

## 如果是首次进入本阶段

1. 派发 architect subagent → 产出 P2-design.md
   1.1 写 P2-dispatch-context-architect.md（派发指引：目标/约束/上游关联/输入文件 + 客观查证信息）
2. 按 C8 映射表派评审（见下方）
3. 评审通过 → P2-review.md status: approved
4. 预跑 check-gate.sh P2（脚本化检查）
5. 更新 .state.yaml phase=P2 → P3
6. git add docs/tasks/{Txxx}/（含 .state.yaml + 产出文件，若 .gitignore 忽略需 git add -f）
7. git commit -m "wf({Txxx}-P2): {摘要}"

## 如果是重试

确认上一轮失败原因（方案选择有误 / 候选方案不足 / 评审 rejected）
→ 读 agate/rules/state-transitions.md 确认 retry 上限（P2 MAX=3）

## 前置条件

- [ ] P1-requirements.md 含 domains / risk_level / phases 声明
- [ ] P0-brief.md env_constraints 可查阅

## 派发

- **角色**：architect（`{agate_root}/assets/execution-roles/architect.md`）
- **输入**：P1-requirements.md + P0-brief.md
- **输出**：P2-design.md
- **派发 prompt 追加**：

```
## P2 最小验证
方案设计前，先用最小验证确认关键假设（10 行 HTML 测试页 / curl 请求 / 20 行脚本）。
验证结果写入 P2-design.md 的 minimal_validation 字段。
- 方案依赖浏览器行为/安全模型/外部系统行为 → 必须做最小验证
- 纯代码逻辑 → 须在 minimal_validation 字段声明 `纯代码逻辑，无外部系统依赖`（须写明依赖了哪些内部函数/数据转换）
```

## 产出规格

P2-design.md 必须包含：
- **候选方案 ≥2** + 权衡 + 选择理由（design_trivial / follows_existing_pattern 时可只写 1 个，见下方）
- **`candidate_count: N` 必填**：本方案候选方案数（≥2，design_trivial/follows_existing_pattern 时可 1），gate 按此字段校验，不再解析标题。你写几个候选就填几个，与正文一致。
- **四字段**：`packages:` `domains:` `ui_affected:` `gate_commands:`
- **files_to_read**：实现时需要参考的文件清单（控制 P4 implementer 上下文）
- **env_constraints**：确认/细化 P0-brief 的环境约束
- **minimal_validation**：验证结果 或 声明"纯代码逻辑，无外部系统依赖"（声明时须附理由）

`candidate_count`/`packages`/`domains`/`ui_affected` 写在文件头 **frontmatter**（`---` 分隔块），
不写正文；`gate_commands:`/`files_to_read:`/`env_constraints:`/`minimal_validation:` 留正文。
**可直接复制的完整样例**：
```yaml
---
phase: P2
task_id: TAG0001           # 替换为实际任务编号
type: design
parent: P1-requirements.md
trace_id: T001-P2-20260101 # {task_id}-P2-{YYYYMMDD}
status: draft
created: 2026-01-01
agent: architect
# ── v2.0 机器字段 ──
candidate_count: 2                # int ≥1，必填
packages: [pkg-a]                 # list，必填
domains: [backend, cli]           # list，必填
ui_affected: false                # bool，必填
---
```

候选方案简化（须附理由，无理由视为无效声明，要求 ≥2 候选方案）：
- `design_trivial: true` + 理由（为什么 trivial）→ 可只写 1 个候选方案（P2 仍不可省略）
- `follows_existing_pattern: [src/foo.py]`（列出参照文件路径）→ 可只写 1 个候选方案，参照已有模式（P2 仍不可省略）

## gate_commands 声明

gate_commands 在 P2 固化，后续阶段按此执行：

```yaml
gate_commands:
  P3: "pytest"                  # 可选：测试运行器（verbose 输出，供 check-tdd-red.sh 自动读取）
  P5: "pytest -q --tb=no"       # 紧凑输出模式
  P5_e2e: "playwright test --reporter=line tests/e2e/"  # ui_affected: true 时必填
```

## 评审派发（C8 机械映射）

按 P1 声明的 domains + risk_level 机械映射评审：

| domain | risk_level | 必须派的评审 |
|--------|------------|------------|
| frontend | 任意 | plan-design-review |
| 任意 | high | plan-eng-review（硬规则，必须派独立 subagent） |
| P1-requirements.md 含 [NEED_CONFIRM] 且涉及业务方向 | 任意 | plan-ceo-review |

多个评审角色 `专家组并行` → 组长汇总 → P2-review.md（status: approved / rejected）。
详见 `agate/rules/review-mapping.md`。

**并行派发**（多个评审角色时）：
1. 同时派发所有触发的评审 subagent（每个一个 task 调用）
   > **操作方式**：在一个 assistant 消息中连续发起多个 task 工具调用（每个评审角色一个）。
   > 不要等前一个 task 返回再发下一个——那是串行，不是并行。
   > 平台会并行执行多个 task，全部返回后再进入下一步（派发组长汇总）。
2. 每个评审 subagent 各写一个 dispatch-context + 各自产出文件（示例非穷举，按 C8 映射表触发）：
   - plan-eng-review → P2-review-eng.md
   - plan-design-review → P2-review-design.md
   - plan-ceo-review → P2-review-ceo.md
   - cso → P2-review-cso.md
3. 所有评审返回后，派发组长汇总 subagent（角色：review + 指定为「专家组组长」）
4. 组长输入：所有评审文件路径
5. 组长产出：P2-review.md（统一 status: approved / rejected）。**组长 subagent 产出的 P2-review.md 的 Header agent 字段必须是组长角色名（非 main）——check-gate.sh P2 硬拦截 agent=main 的 approved**
6. 组长规则：
   - 不发表新意见，只汇总
   - 任何专家标 BLOCKER → status: rejected
   - 多位专家分歧 → 标「专家组分歧」交人工
   - 全票无 BLOCKER → status: approved

**单评审角色时**：直接派发，无需组长汇总，产出直接写 P2-review.md。

review 不通过 → architect 修改方案 → 再 review → … → approved（⑩迭代循环，review 和 gate 重试共享 retry 预算）

**UI 测试选择器**：涉及前端时，P2 design 建议声明 UI 组件的稳定测试标识清单（如 `data-testid`，而非 class 命名）。P3 test-designer 用稳定标识定位元素，P4 implementer 按清单实现--class 命名可重构，稳定标识不变。具体方案由 P2 architect 决定。

## gate 规则

```bash
check-gate.sh P2 $TASK_DIR
```

- 候选方案数 ≥2（design_trivial / follows_existing_pattern 时可只写 1 个）
- P2-review.md 存在且 status: approved（agent≠main）— 不存在 → gate exit 1
- 四字段齐全（packages/domains/ui_affected/gate_commands）
- gate_commands.P3 可选（非 pytest 项目建议声明，供 check-tdd-red.sh 自动读取测试运行器）
- 候选方案 ≥2 时含权衡/选择理由

## 推进条件（全部满足才写 phase: P3）

- [ ] P2-design.md 候选方案 ≥2（或 design_trivial/follows_existing_pattern 须附理由时可只写 1 个）+ 四字段齐全
- [ ] P2-review.md 存在且 status: approved（agent≠main）
- [ ] gate_commands.P5_e2e 已声明（ui_affected: true 时）

## 常见错误

1. **忘了最小验证**：方案依赖外部系统行为（API MIME 类型、浏览器 CSP 等）但直接假设前提成立 → 到 P6 才发现不可行。跑一个 curl / 10 行 HTML 就能 5 分钟发现
2. **gate_commands.P5 只列单元测试**：UI 任务时缺少 P5_e2e → P5 不会跑端到端验证
3. **files_to_read 列太多文件**：把所有相关文件都列上 → P4 implementer 上下文爆炸。只列确实需要参考的
4. **忘了派评审**：按 C8 映射机械执行，不靠"觉得不需要"
5. **gate 不过 ≠ 你失败了**：红灯指向工作/设计的问题，不指向你。正确动作是诊断→退回/重试/PAUSED，不是修改产出让它变绿。

## 下游影响

- P4 依赖 files_to_read 导航代码阅读范围
- P5 依赖 gate_commands 执行验证命令
- P6 依赖 ui_affected 判断是否需要 vision-helper
- gate_commands 在 P2 固化后 P4-P6 不能改——设计阶段是声明验证契约的唯一窗口

> 完成 → 读 phase-cards/P3-tdd.md
<!-- AGATE_CARD_END -->

<objective_info>
- 环境状态：worktree 是改造对象（分支 dev/workspace，HEAD=TAG0001-P1 commit，已含 TAG0003 工作区架构 + TAG0002 refactor 机制）；`~/.agate` → 主 checkout 是稳定版 v0.40.2 开发工具（禁止改动）。
- 版本隔离三条铁律：改协议只改 worktree 的 `agate/`；跑 gate/读卡片用 `~/.agate`（原版规则）；跑测试用 worktree 本体。
- 测试基线：worktree 全量 bats 654 用例全绿（TAG0003 631 + TAG0002 新增）；count-tests.sh 基线 648 + sanity 6。
- 已核实查证：TAG0003 工作区规范 agents/ 含 tech-debt（WORKFLOW.md L85"agent 知识（project.md / memory / tech-debt）"）——本次修正为 agents/ 只留 project.md/memory，tech-debt 归独立 debt/；orchestrator-template.md L102 mkdir 8 子目录（roadmap/tasks/agents/archived/reviews/decisions/plans/logs）；TAG0002 已实现 change_type（agate-frontmatter-check.py P1 schema 含 change_type 枚举）。
- 协议目录结构：agate/ 含 WORKFLOW.md / dispatch-protocol.md / state-machine.md / role-system.md / git-integration.md / platform-notes.md / LIMITATIONS.md / orchestrator-template.md / phase-cards/ / assets/（execution-roles + review-roles + templates）/ scripts/ / tests/ / AGENTS.md / adr.md / CONTEXT.md / SETUP.md / UPGRADING.md / rules/。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
