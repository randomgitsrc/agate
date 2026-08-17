---
phase: P2
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0006
role: architect
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
修复 P2-design.md 以解决双评审（plan-design-review + plan-eng-review）的发现，使方案自洽后重新提交复审。

### 约束
1. **增量修改**：只修 P2-design.md，不碰 P1 产出（P1-requirements.md 是基线，后续阶段不直接改——除非主 Agent 显式批准）。
2. **BLOCKER 级必修（4 项）**：
   - **B1（plan-design-review 问题 1）**：BDD-4 触发条件矛盾——§0.3 风险2 vs §2.3 gate 逻辑。以 §2.3 为准：触发条件仅为 `ui_affected: true`（不读 P1 capabilities）；§0.3 改为"经核实无 P2 gate 测试引用 fixtures/ui-affected（test_check_gate 自建 fixture），故该 fixture 不会被 P2 检查命中，兼容成立"。
   - **B2（plan-eng-review BLOCKER-1）**：GAP 分支缺"P1 无视觉能力声明"默认语义。显式声明：P1 无视觉能力条目（capability_requirements 无 need 含 visual/vision）→ 视为 **available 语义**，保留既有 R1b 强制（截图 PASS 须引 vision YAML）；GAP 分支仅在 P1 显式声明 status: GAP 时触发。补兼容回归用例（ui_affected:true + 无 P1 视觉声明 + 截图无 vision → 断言 exit 1）。
   - **B3（plan-eng-review BLOCKER-2）**：fixtures 实况不符——**vision-blocked/P2-design.md 也是 ui_affected: true**（grep 实测：full-task/high-risk/paused-task = false；ui-affected/vision-blocked = true）。修正 §0.2/§2.3/§6.3/§10 中"既有 P2-design 均 ui_affected:false"的表述，显式列入 vision-blocked（同 ui-affected：ui_affected:true、不用于 P2 gate 测试、P6 专用）；§6.3 夹具行补 vision-blocked 免责说明。
   - **B4（plan-design-review 建议 4）**：minimal_validation 第 3 项"块边界用 '## ' 章节分隔定位"改为"提取 ```yaml 代码围栏块内 YAML"（与 P1 capability_requirements 实际承载格式一致）。
3. **MAJOR 级落实（2 项）**：
   - **M1（plan-design-review 建议 2）**：plan-design-review.md 七维边界注——"交互状态覆盖率=状态存在性，交互设计细节=状态内实现质量"，防 double count。
   - **M2（plan-design-review 建议 3）**：GAP 分支退出码语义——补充"含复核记录放行 exit 0/2 与既有方差 WARNING exit 2 的叠加顺序"（同一截图集既重方差警告又雷同时以哪个为准）。
4. **NOTE 级处理（2 项）**：
   - **N1（plan-eng-review NOTE-2）**：BDD-14 单测构造须满足两道前置门禁（文件 >1KB + 像素方差≥50），测试 PNG 非纯色图。
   - **N2（plan-eng-review NOTE-3）**：基线用例数口径统一——P2 用 **825**（实测 count-tests/pytest collect-only 均为 825）；P1 的 823 属历史过时值，P7 一致性时对齐（P2 本文件用 825）。
5. **不得推翻已 approved 的机制方向**：方案 A（三态硬声明 + P2 UI 设计节门禁 + P6 三态分档消费 + GAP 降级链）本体不变，只修文档内部矛盾与缺失定义。
6. **不写死视觉工具**：任何补写不得绑定具体工具名。
7. **DEBT0005 已登记**（三态解析重复，建议公共 helper——若修订时顺手设计公共 helper 方案可写入设计，但不强制本任务实现）。

### 上游关联
- plan-design-review：needs-revision。发现：B1（触发条件矛盾 BLOCKER）+ 建议 2/3/4（七维边界注 / GAP 退出码 / 块定位描述）。
- plan-eng-review：needs-revision。发现：B2（GAP 默认语义 BLOCKER）+ B3（vision-blocked fixture 遗漏 BLOCKER）+ NOTE-1（三态解析重复，已登记 DEBT0005）+ NOTE-2（ahash 前置门禁）+ NOTE-3（823 vs 825）。
- 双评审均确认：方案 A 机制成立、方向正确，修正后即可 approved。

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0006-ui-ux-quality/P2-design.md（修复对象——主输入）
- {AGATE_WORKSPACE}/tasks/TAG0006-ui-ux-quality/P2-review-design.md（评审意见：B1 + 建议 2/3/4）
- {AGATE_WORKSPACE}/tasks/TAG0006-ui-ux-quality/P2-review-eng.md（评审意见：B2/B3 + NOTE-1/2/3 + DEBT0005）
- {AGATE_WORKSPACE}/tasks/TAG0006-ui-ux-quality/P1-requirements.md（需求基线，P2 设计须对齐）
- {AGATE_WORKSPACE}/tasks/TAG0006-ui-ux-quality/P2-dispatch-context-architect.md（原始派发约束，修复不得违反）
- {project_root}/agate/tests/fixtures/（如需核验 fixtures 实况）
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
- 修复对象：P2-design.md（547 行，candidate_count=4，方案 A 选定）。
- 双评审状态：均 needs-revision。评审发现汇总：B1（§0.3 vs §2.3 BDD-4 触发条件矛盾）、B2（GAP 无声明默认语义未定义）、B3（vision-blocked fixture 遗漏——实测 5 个 fixture 中 ui-affected 和 vision-blocked 均 ui_affected:true）、B4/M1/M2/N1/N2（见约束节）。
- 当前基线用例数：825（pytest collect-only 实测），P1 文字 823 为过时值。
- DEBT0005 已登记（tech-debt.md）。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。