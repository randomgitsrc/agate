---
phase: P2
generated_by: agate-inject-card.sh + 主 Agent
task_id: T001
role: plan-eng-review
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

独立评审 `docs/tasks/T001-v2.0-structured/P2-design.md`（方案 A：frontmatter 强化 + 单工具双读扩展 + 新校验器挂 pre-commit，覆盖 A/B/C/D 四流），产出 `P2-review.md`（status: approved / rejected）。

### 触发依据（C8 机械映射）

P1 声明：domains=[backend, cli]（无 frontend，不触发 plan-design-review）、risk_level=**high**（触发 plan-eng-review 硬规则）。无 [NEED_CONFIRM]（不触发 plan-ceo-review）。**单评审角色，直接产出 P2-review.md（无需组长汇总）。**

### 评审重点

1. **方案正确性**：方案 A（`agate-md-field-get.py` 双读 + 通用 op + 新校验器）是否技术上可行？候选方案 B 的排除理由是否成立（迁移半径、薄壳不动、测试影响）？
2. **四流覆盖**：流 A（P1/P2 迁移 + 校验器）、流 B（P6/P7 结构化）、流 C（标记收尾）、流 D（编号硬切）的设计落点是否完整、可实施？
3. **硬约束遵守**：count-tests 594 不漂移、frontmatter 禁 >3 层嵌套、CHECK 9 锚点 37 条校准、gate_commands 暂留正文、流 D 硬切、自举原则
4. **客观数字**：candidate_count=2 与正文一致；37 条锚点 / 4 工具 / 594 / 355 与 P1 一致
5. **语义真实性边界**：§10 是否写明"结构化不解决语义真实性"（BDD-14）
6. **技术风险**：值归一化（ui_affected bool → 小写）、FIELD_COUNT 改动牵动 check-gate.bats 101 测试、CHECK 9 反向覆盖等风险是否识别并给出对策
7. **可实施性**：files_to_read 是否聚焦（不过度膨胀）、gate_commands 是否可执行、minimal_validation 是否真实做了

### 客观查证要求（独立核实，不轻信 architect）

- P2-design.md 的 candidate_count / 四字段 / gate_commands 是否与 gate 要求一致
- 关键声明是否可在 worktree 实测验证（如 pyyaml 解析行为）
- 与 P1 的 28 条 BDD 映射是否真实（不能只在表格里列个编号）

### 上游关联

- P2-design.md（被评审对象）
- P1-requirements.md（28 BDD、判别契约、语义真实性边界）
- P0-brief.md（A+B+C+D 范围、硬约束、流 D 硬切、v0.40.0）
- P1-review.md（approved）
- 可行性评估 /tmp/opencode/feasibility.md

### 输入文件

- docs/tasks/T001-v2.0-structured/P2-design.md（被评审对象，必读）
- docs/tasks/T001-v2.0-structured/P1-requirements.md（需求基线）
- docs/tasks/T001-v2.0-structured/P0-brief.md（立项）
- docs/tasks/T001-v2.0-structured/P1-review.md（P1 评审）
- ~/.agate/assets/review-roles/plan-eng-review.md（角色定义）
- /tmp/opencode/feasibility.md（可行性评估）
- 参考脚本（客观查证用）：~/.agate/scripts/agate-md-field-get.py / agate-state-yaml-check.py / check-gate.sh / check-changelog.sh
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
- 环境状态：worktree 分支 feat/v2.0，bats 1.10.0 / py3.12 / pyyaml / shellcheck 可用
- 测试基线：count-tests.sh 输出 594（sanity.bats 6 另算）
- 已核验事实：CHECK 9 锚点表实际 37 条；读 gate_commands 的工具实际 4 个
- 关键路径：改造对象 = /home/kity/oclab/agate/.worktrees/v2.0/agate/；开发工具 = ~/.agate/
- 任务编号：T001；发布版本 v0.40.0
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
