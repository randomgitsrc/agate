---
phase: P2
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0006
role: architect
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
产出 P2-design.md：为「agate UI/UX 验收质量机制」设计协议增强方案——覆盖 P1 的 15 条 BDD，含候选方案权衡、影响域分析、gate 命令固化、files_to_read、minimal_validation、影响面核对清单、Windows GUI 自动化评估小节。

### 约束
1. **本任务是 agate 协议本体增强**（dogfooding）：改造对象是 worktree 里的协议文件（`{project_root}/agate/` 下的 *.md / assets/**/*.md / phase-cards/*.md / scripts/*.py / tests/**），不是业务 UI 应用。方案设计的是「协议机制如何增强」，产出物是文档条文 + gate 脚本逻辑 + 单测。
2. **已定关键设计决策（P1 不得推翻，P2 必须落实）**：
   - UI 设计产物**并入 P2-design.md 独立节**（`ui_affected: true` 时 P2 必须含"UI 设计"节：布局/交互/视觉 checklist）——注意：这是对**业务任务**的要求（P2 产物规格），不是本任务自己写个 UI 设计节；本任务方案要把这条写进 architect.md / P2 阶段卡片的 P2 产出规格
   - **architect 兼任 UI 设计**（不新造 designer 角色）
   - P6 verifier 以 **UI 设计节为视觉验收依据**
3. **能力三态（RM-AG0004）**：vision 能力运行时探测不写死工具；available → P6 真实视觉分析；supplementable → 派发 prompt 注入获取指引（A3 扩展）；GAP → 降级（像素检测 + 人工复核记录，不要求 vision YAML）——BDD-9 已制入 GAP 分支，方案必须落实该分支的协议条文。
4. **subagent 能力自查（BDD-12）**：dispatch-prompt 模板加"先自查能否调 vision 能力"要求。
5. **雷同截图降级（BDD-14）**：check-p6-evidence.py avg-hash 重复从 WARNING 改为"降级待复核"判定（md5 硬阻断语义不变）。
6. **输入态变化类用例人工复核（BDD-13）**：verifier.md + P6 卡片定义"输入态变化"判定标准 + 人工复核记录要求。
7. **影响面核对清单（BDD-8）**：P2-design.md 必须含影响面节，与 P1 影响面清单（45 文件 + 64 处口径）对齐核对，列出全部联动点与同步动作。用户明确：不愿意一轮一轮来回改，一次到位。
8. **Windows GUI 评估（BDD-7，RM-AG0006）**：P2-design.md 必含"Windows GUI 自动化评估"小节，评估 WinAppDriver/AutoIt 是否补真实 GUI 交互路径；结论可以是"保持现状"（调研非实测）；不得含"已实测 Windows"字样。
9. **兼容策略（P1 §9）**：增量增强不破坏既有 gate 语义——新检查只对新声明生效，不回溯改既有 task 数据；823 基线用例全绿 + 新增用例全绿；count-tests 不漂移。
10. **gate_commands 固化**：本任务 gate 命令以 pytest 为主（`pytest -q --tb=no` 等紧凑模式），P5/P6 全局回归 + 单测。ui_affected 对本任务自身 = false（本任务无 UI 产物），但方案设计的是机制增强——注意 frontmatter 的 `ui_affected:` 是本任务自身的声明（false），BDD-4/9 等说的是"业务任务"的 UI 机制。
11. **候选方案 ≥2 + 权衡 + 选择理由**：每项机制增强（UX 基线落点 / 视觉证据分档 / 雷同截图降级强度）给出候选方案对比。
12. **P1 纯净性延续**：方案设计落实 BDD 时不得新增/篡改需求语义；发现新隐含需求标 [SCOPE+]。

### 上游关联
- P1-requirements.md 已 approved：15 条 BDD（BDD-1/2/3 P1 组；BDD-4/5/6/7/8 P2 组；BDD-9~14 P6 组；BDD-15 兼容回归）+ 45 文件影响面清单 + vision 三态能力声明（visual-analysis supplementable、gui-e2e-framework-win supplementable）。
- 需求基线明确：本任务自身声明 `ui_affected: false`（无 UI 产物），但方案要定义"业务任务 ui_affected: true 时"的协议机制。
- 能力自查：P1 analyst 报告自身无视觉注入能力，本任务 P6 以脚本单测 + 文档内容为证据。

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0006-ui-ux-quality/P1-requirements.md（需求基线——主输入，含 15 BDD + 影响面清单 + 能力声明）
- {AGATE_WORKSPACE}/tasks/TAG0006-ui-ux-quality/P1-review.md（评审结论：approved + 复审记录）
- {AGATE_WORKSPACE}/tasks/TAG0006-ui-ux-quality/P0-brief.md（任务简报：三个 RM + 修复方向 + env_constraints）
- {project_root}/HANDOFF-TAG0006.md（交接单：双工作区纪律、验证命令）
- {project_root}/agate/assets/execution-roles/architect.md（你的角色定义）
- {project_root}/agate/assets/execution-roles/verifier.md、vision-analyst.md、test-designer.md（方案涉及的角色文件现状）
- {project_root}/agate/assets/review-roles/plan-design-review.md（方案要改的评审维度现状）
- {project_root}/agate/phase-cards/P2-design.md、P6-acceptance.md（阶段卡片现状，方案要改）
- {project_root}/agate/dispatch-protocol.md（A3 能力传递规则现状）
- {project_root}/agate/assets/templates/dispatch-prompt.md（模板现状，方案要加自查要求）
- {project_root}/agate/scripts/check-gate.py、check-p6-evidence.py（gate 脚本现状）

> 输入较多（>5）但属 P2 设计必需（方案要精确改这些文件的哪一节）——用 grep 定位相关节，不全文通读。产出 P2-design.md 一个文件。
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
4. 预跑 check-gate.py P2（脚本化检查）
5. git add {AGATE_WORKSPACE}/tasks/{Txxx}/（含 .state.yaml + 产出文件，若 .gitignore 忽略需 git add -f）
   ⚠️ 此时 .state.yaml 的 phase 保持 P2，不要提前写 P3——phase = 本 commit 的产出阶段
6. git commit -m "wf({Txxx}-P2): {摘要}"（phase=P2，P2 产出含 P2-design.md + P2-review.md）
7. P2 commit 完成后进入 P3：**phase 推进 P3 随 P3 产出 commit 一起**（P3-test-cases.md 就绪后），不是单独 phase commit

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

## dispatch_plan 机器字段（可选，TAG0014）

> 本字段是 P2 对**后续阶段编排方案**的机器声明（评估 + 编排模式，见 dispatch-protocol「派发编排机制」），由 architect 在"批次设计"节（execution-roles/architect.md）产出，P2 gate 校验其合法性。

方案含多个独立子任务（多包/多模块/high 复杂度）时，P2-design.md frontmatter 应声明 `dispatch_plan:`（单行 flow YAML，与 candidate_count 同级，**不入 frontmatter-check schema**，缺省不校验）：

```yaml
# ── v2.0 派发编排字段（可选）──
dispatch_plan: {mode: static-batch, parallel_limit: 3, batches: [{id: pkg-a, complexity: medium}, {id: pkg-b, complexity: low}]}
```

字段契约（gate 校验口径）：
- `mode` ∈ {single, static-batch, parallel, recon-then-split, serial}——编排模式（单发/静态拆批/并行/先理解后拆/串行链）
- `parallel_limit` 可选，≥1 整数——并行上限（缺省 3）
- `batches` 可选——mode ∈ {static-batch, parallel} 时每批须含 `id` + `complexity` ∈ {low, medium, high}；批数 ≤ parallel_limit
- 缺字段 / 坏 YAML → P2 gate 跳过校验，行为等同现状（向后兼容，不误拦）

## gate_commands 声明

gate_commands 在 P2 固化，后续阶段按此执行：

```yaml
gate_commands:
  P3: "pytest"                  # 可选：测试运行器（verbose 输出，供 check-tdd-red.py 自动读取）
  P5: "pytest -q --tb=no"       # 紧凑输出模式
  P5_e2e: "playwright test --reporter=line tests/e2e/"  # ui_affected: true 时必填
```

## 评审派发（C8 机械映射）

按 P1 声明的 domains + risk_level 机械映射评审：

| domain | risk_level | 必须派的评审 |
|--------|------------|------------|
| backend | 任意 | plan-eng-review（P2 方案评审） |
| frontend | 任意 | plan-design-review |
| 任意 | high | plan-eng-review（硬规则，必须派独立 subagent） |
| P1-requirements.md 含 [NEED_CONFIRM] 且涉及业务方向 | 任意 | plan-ceo-review |

> **去重说明**：同一任务命中多行且触发同一评审角色时，去重只派发一次（如 backend + high 均命中 plan-eng-review，只派 1 个 plan-eng-review，不重复派发）。

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
5. 组长产出：P2-review.md（统一 status: approved / rejected）。**组长 subagent 产出的 P2-review.md 的 Header agent 字段必须是组长角色名（非 main）——check-gate.py P2 硬拦截 agent=main 的 approved**
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
check-gate.py P2 $TASK_DIR
```

- 候选方案数 ≥2（design_trivial / follows_existing_pattern 时可只写 1 个）
- P2-review.md 存在且 status: approved（agent≠main）— 不存在 → gate exit 1
- 四字段齐全（packages/domains/ui_affected/gate_commands）
- gate_commands.P3 可选（非 pytest 项目建议声明，供 check-tdd-red.py 自动读取测试运行器）
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
- 环境状态：worktree 干净；协议本体与稳定版一致；基线 823 pytest + consistency 0 ERROR。
- 关键现状（已查证）：
  - state-machine.md:89-94 `ui_affected` 现仅要求 E2E 交互点；P2 gate 现查四字段（packages/domains/ui_affected/gate_commands）。
  - analyst.md:78-100 capability_requirements 三态机制已存在；dispatch-protocol.md:1184-1202 A3 supplementable 传递规则已存在。
  - plan-design-review.md 维度表当前五维（无视觉/交互维度）。
  - check-p6-evidence.py 现有 avg-hash WARNING（261 行附近）、md5 硬阻断（provenance 审计）。
  - P6-acceptance.md:35 已有 available 前置检查；verifier.md:104-108 UI 追加约束。
  - vision-analyst 角色已存在（B3/yaml 结构）。
- 影响面：P1 清单 45 协议/脚本/测试文件（含 15 测试夹具）+ 64 处口径（含 docs/roadmap 等非协议文件）。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。