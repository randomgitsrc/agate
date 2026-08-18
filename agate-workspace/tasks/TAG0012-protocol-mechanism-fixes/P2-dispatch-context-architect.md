> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心输入源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。

---
phase: P2
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0012
role: architect
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

把 P1-requirements.md 的 23 条 BDD（11 个文件分组 A-K，覆盖 RM-AG0013/RM-AG0014（主体+补充）/
RM-AG0019/RM-AG0016）转成 P2-design.md：候选方案 + 权衡 + 影响域 + `files_to_read` + 逐文件改动
落点表 + `gate_commands` 固化 + （若适用）`dispatch_plan` 批次设计。

### 约束

1. **P1 已把"改哪个文件、改动要回答哪些问题"锁定得很细**（11 个文件分组，每条 BDD 都有具体行号/
   小节定位），P2 的核心工作不是"要不要改"，而是**给出具体怎么写**——尤其 3 类"新增机制设计"：
   - BDD-10：verification_env 失败处理协议的 4 个问题（可/不可重试清单、批处理要求、止损轮次归属、
     READY 后问题归属）——**必须给出具体规则**（不能只重复 P1 的问题清单），如"止损轮次 = N 轮"
     "止损后转 PAUSED"这类可执行的具体值/流程。
   - BDD-16/21：`timeout_seconds` 与既有 `AGATE_TDD_TIMEOUT`（P3 层，`agate_common.py:408`，默认
     120s）的关系必须选定一个具体方案（互斥/叠加/排除 P3 三选一），并给出各类命令的默认阈值基准
     （单元测试类/E2E 类/构建类）。
   - RM-AG0019：P0-brief 漂移判定标准需要"轻微漂移 vs 严重漂移"两档具体判据（不能只写"視情况而定"）。
   这三类是本 P2 唯一需要真正做设计探索的地方，候选方案应重点花在这里（可参照 TAG0014 的
   P2-design.md 组织方式——按"设计维度"分候选方案，而不是按 RM 编号分）。其余 BDD（如"新增小节 +
   可 grep 命中"类）设计空间很小，可归为 `follows_existing_pattern`（既有"权威定义 + 卡片/角色文件
   引用"惯例）处理，不必为每条都写 2 个候选方案，但仍需在 `files_to_read`/落点表里逐条覆盖 23 条 BDD
   （不能遗漏），避免 P1 已经做好的"文件→改动"归并到 P2 又打散重复。
2. **`dispatch_plan` 大概率需要声明**——`risk_level: high` + 改动横跨 6 类文件（phase-cards /
   dispatch-protocol / state-machine / execution-roles / templates / scripts），按
   architect.md「批次设计（强制节）」的硬规则"high 复杂度必须拆分"，需要先做工作量五维评估（见
   dispatch-protocol.md「派发编排机制」），若判定 high → 必须设计 `dispatch_plan`（mode 从
   single/static-batch/parallel/recon-then-split/serial 中选，参考 P1 已经做好的 11 个文件分组
   A-K 作为批次候选边界）。若评估后判定不需要拆批（如认为文档改动量虽多但每处改动量很小、无需
   真正并行/分批派发），需在文中明确给出五维评估结论，不能跳过评估直接不写。
3. **`gate_commands` 需要处理"是否需要新脚本测试"的分支决定**——P1 BDD-22 把这个问题交给你：若
   决定 `timeout_seconds` 需要 `check-gate.py` 脚本硬校验，`gate_commands.P3` 需指向该脚本的新
   pytest 用例（沿用 TDD 红→绿）；若决定只做文档约定不做脚本硬校验，仍需按 P1 裁剪说明第 2 点的
   要求，为本次大批量协议文档改动设计至少一个"grep 断言审计"测试（新建测试文件，逐条断言 23 处
   新增内容的关键词/章节确实落盘），作为回归拦截——**这个测试无论 BDD-22 走哪个分支都需要**，不是
   可选项。仓库目前没有现成的"grep 断言审计"测试文件可直接复用，需要新建（可参照
   `agate/tests/unit/test_check_protocol_consistency.py` 的组织方式，但断言内容是"新增小节/关键词
   是否存在"而非该文件本身的一致性逻辑）。
4. **`ui_affected: false`**（本任务纯协议文档 + 脚本 schema 改动，无 UI），不需要 UI 设计节。
5. **`minimal_validation`**：本任务是协议文档改动 + 可能的 `check-gate.py` schema 校验扩展，均为
   纯代码逻辑（无浏览器/外部系统依赖），按 architect.md 要求声明"纯代码逻辑，无外部系统依赖"，并
   写明依赖了哪些内部函数/数据结构（如 `_md_field_get`/frontmatter 解析管线，若涉及）。
6. **候选方案数**：设计维度（如"止损轮次/阈值基准"“timeout_seconds 与 AGATE_TDD_TIMEOUT 关系”
   "P0-brief 漂移判据"三个维度各自 ≥2 候选）合并计入 `candidate_count`（参照 TAG0014 P2-design.md
   "候选方案分三个设计维度展开，每维度 ≥2 个候选"的组织方式），不要为 23 条 BDD 逐条写候选。
7. **C8 评审映射已机械算出**：`domains: [process]` + `risk_level: high` → 命中「任意 domain, high」
   硬规则，必须派 **plan-eng-review**（无 frontend，不派 plan-design-review；无涉及业务方向的
   NEED_CONFIRM，不派 plan-ceo-review）。单一评审角色，产出直接写 P2-review.md，无需组长汇总。

### 上游关联

- P1-requirements.md 已 approved（23 条 BDD，`risk_level: high`，`phases` 全量不裁），frontmatter
  `packages: [phase-cards, dispatch-protocol, state-machine, execution-roles, templates, scripts]`、
  `domains: [process]`。
- P1 第 0 节"同类扫描核实结论"已确认：timeout 概念在协议里已有三层既有机制（P3 的
  `AGATE_TDD_TIMEOUT` / P6 Playwright 脚本内部硬超时 L790-879 / state-machine 的
  `failure_mode: timeout`），RM-AG0016 补第四层（subagent bash 命令级超时兜底）——P2 设计时必须
  在文档里保留/强化这层区分，不能合并成一层。
- P1 第 2 节"隐含需求识别"第 4 点：verification_env 失败重试（环境验证轮次）与阶段 retry
  （`retries[Pn]`）是两套独立计数，P2 必须显式声明两者是否共享预算。

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0012-protocol-mechanism-fixes/P1-requirements.md（需求基线，23 条 BDD，本阶段主要输入）
- {AGATE_WORKSPACE}/tasks/TAG0012-protocol-mechanism-fixes/P0-brief.md（环境约束、已知风险）
- {agate_root}/dispatch-protocol.md（尤其「派发编排机制」「verification_env 条件化」两节）
- {agate_root}/state-machine.md（`.state.yaml` 结构、`env_state` 字段、P0→P1 转移条件）
- {agate_root}/assets/execution-roles/architect.md（角色定义，含「批次设计」强制节完整规则）
- {AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/P2-design.md（同类协议机制任务的 P2 设计
  组织方式参考——"按设计维度分候选方案"+"逐文件改动落点表"两种结构均可直接借鉴，不必重新发明格式）
- {project_root}/AGENTS.md（项目约定）
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
ui_design_section: true           # bool，可选（presence 语义：ui_affected: true 时声明已含 UI 设计节）
---
```

**UI 设计节（`ui_affected: true` 时必含，P2 gate 校验）：** `ui_affected: true` 的 P2-design.md
正文必须包含 `## UI 设计` 节，节内含**渲染形态声明**（`渲染形态:` 声明行，复用 P1 frontmatter
`ui_render_shape` 的规范形态值 + 中文注释，gate 按规范化值比对校验 P1-P2 一致；无 P1 声明时按
布局型默认）+ **维度选择**（`适用维度:` 声明行）+ **按形态适配的 checklist**（常规布局型 =
布局/交互/视觉三类；渲染组件/时序特效型 = 渲染正确性/动效时序等适用维度 checklist；不适用的维度
显式声明"维度不适用"）。缺 UI 设计节 / 缺形态声明 / 缺按形态 checklist / P1-P2 形态声明不一致 →
P2 gate exit 1。结构规格见 `assets/execution-roles/architect.md`「UI 设计节」节（由 architect
兼任产出，不新增 designer 角色）。

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
- 环境状态：worktree 基线已验证（881 pytest 全绿，`check-protocol-consistency.py --strict` 0
  ERROR，P1 commit 36f2502 已落盘），可直接在 worktree 内做只读调研 + 产出设计文档。
- `agate_common.py:408` 确认 `timeout_secs = int(os.environ.get("AGATE_TDD_TIMEOUT", "120"))`，
  被 `check-tdd-red.py` 消费，作用于 `gate_commands.P3`。
- `dispatch-protocol.md` L691-695「4. 并行规则」+ L697「5. 全阶段适用表」是既有权威节（TAG0014
  建立），RM-AG0016 的"资源密集型默认串行"是该节的追加条目，不新建小节。
- `check-gate.py` 当前无 `_gate_p0` 函数（P0 无脚本化 gate，纯人工 checklist）；P2.61（约 L613）
  只做 `gate_commands` 命令 token 可执行性的浅校验，不校验子字段合法性；全仓 `timeout_seconds`
  零命中（P1 第 0 节已确认，纯新增字段，非补全）。
- 参考先例：`{AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/P2-design.md` 是同类"协议机制
  批量改动"任务的已完成 P2 设计（`candidate_count: 3`，按"读取路径/权威节落点/卡片统一策略"三个
  正交设计维度组织候选方案 + 逐文件改动落点表 + `gate_commands.P3` 指向新建测试文件），可直接参照
  其组织结构。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
