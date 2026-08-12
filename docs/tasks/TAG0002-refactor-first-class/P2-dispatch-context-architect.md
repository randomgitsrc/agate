---
phase: P2
generated_by: agate-inject-card.sh + 主 Agent
task_id: TAG0002
role: architect
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
产出 docs/tasks/TAG0002-refactor-first-class/P2-design.md——把 P1 需求基线（8 条 BDD）转化为可实现的"重构一等任务（Phase A）"方案：候选方案（≥2）与权衡 + 影响域 + gate 命令固化 + files_to_read + minimal_validation。

### 约束
- 本任务是 **agate 协议自身改造**（dogfooding）：改造对象是 worktree `agate/` 目录（**已含 TAG0003 工作区架构改动**——本任务在 TAG0003 基础上继续改协议），`~/.agate` 是稳定版 v0.40.2 开发工具（禁止改动）。P2 设计的是新版协议（worktree agate/ 将改成的样子）。
- **任务内容（Phase A，方案己，P1 已确认）**：
  1. `P1-requirements.md` 加 `change_type: refactor` 字段（frontmatter 或正文？设计决定——需与既有 frontmatter 机器字段体系协调）
  2. P6 验收口径：**行为不变 + 全量回归全绿 + 关键路径验收**，禁止伪造功能 BDD——`phase-cards/P6-acceptance.md` 增加 refactor 口径分支
  3. `check-gate.sh` P6 分支按 `change_type` 分流（refactor 任务走回归口径而非功能 BDD 口径）
  4. P3 卡片/派发指引含回归测试口径说明（BDD-8）
- **P1 关键结论（需求必须落实）**：
  - risk_level=medium（非破坏性：缺省行为不变，仅新增 refactor 分支）
  - refactor 口径**独立于** no_behavior_change（P1 已确认——需设计独立分支而非复用）
  - BDD-1..8 覆盖：change_type 字段、P6 refactor 口径分支、P6 gate 分流、P3 回归测试口径、回填验证
- **设计必须解决**：
  - `change_type` 字段放在哪（P1-requirements.md frontmatter？）——需与 v2.0 机器字段体系（risk_level/phases/packages/domains 在 frontmatter）协调
  - `check-gate.sh` P6 分支如何读取 change_type 并分流（refactor → 行为不变 + 回归全绿判定；功能 → 现 BDD 计数判定）
  - P6-acceptance.md 的 refactor 口径下验收记录格式（无功能 BDD 时如何逐条对照？用"行为不变声明 + 回归结果 + 关键路径验收记录"？）
  - P3 回归测试设计的 gate 影响（check-tdd-red 是否仍适用？重构无新功能测试，红灯语义怎么处理？）
  - 回填验证路径：用 agate 已有真实重构（如 `refactor: trim orchestrator-template.md`）走一遍 refactor 流程验证 P6 口径可用
- **P2 产出规格**（见 architect.md）：frontmatter（candidate_count/packages/domains/ui_affected 必填）+ 正文（候选方案与权衡 + gate_commands/files_to_read/env_constraints/minimal_validation）+ 实现完成标志。gate_commands 在 P2 固化。
- 设计中发现新隐含需求 → 标 `[SCOPE+]`（行首声明格式）。
- 禁止行首 `- PASS` / `- FAIL` 格式（provenance 审计拦截）。

### 上游关联
- P1 已通过 gate（exit 2）：8 条 BDD（BDD-1..8），risk_level=medium，phases 全 8 阶段，packages=[agate]，domains=[backend,cli]，3 条 SUGGEST，无 NEED_CONFIRM，无 GAP。requirements-review 复审 approved。
- P1 确认：refactor 口径独立于 no_behavior_change。

### 输入文件
- docs/tasks/TAG0002-refactor-first-class/P1-requirements.md（需求基线 + 8 条 BDD + frontmatter——**必读**）
- docs/tasks/TAG0002-refactor-first-class/P1-review.md（评审意见——必读，理解评审视角）
- docs/tasks/TAG0002-refactor-first-class/P0-brief.md（任务简报与风险声明——必读）
- AGENTS.md（项目约定：双工作区纪律、测试命令、脚本约定——必读）
- docs/reviews/review-design-20260812-1428.md（方案己 Phase A——必读，任务内容来源）
- agate/ 目录本身（了解协议现状、P6 卡片/check-gate.sh P6 分支/phase-cards 结构——设计前必须读现有代码再设计）
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
- 环境状态：worktree 是改造对象（分支 dev/workspace，HEAD=TAG0002-P1 commit，已含 TAG0003 工作区架构全部改动）；`~/.agate` → 主 checkout 是稳定版 v0.40.2 开发工具（禁止改动）。
- 版本隔离三条铁律：改协议只改 worktree 的 `agate/`；跑 gate/读卡片用 `~/.agate`（原版规则）；跑测试用 worktree 本体。
- 已核实查证：worktree `agate/phase-cards/P6-acceptance.md` 卡片 L4 有 `no_behavior_change 可简化（快速验收）` 表述但无 refactor 独立分支；worktree `agate/scripts/check-gate.sh` P6 分支（L292 附近）为 BDD 计数 + 证据目录检查，无 change_type 分流；P1-requirements.md frontmatter 已有 v2.0 机器字段体系（risk_level/phases/packages/domains）。
- 测试基线：worktree 全量 bats 631 用例全绿（TAG0003 后）；`bats agate/tests/unit/check-gate.bats` 是 P0-brief 声明的 test_cmd。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
