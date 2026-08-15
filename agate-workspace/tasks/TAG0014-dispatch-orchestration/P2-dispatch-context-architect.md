---
phase: P2
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0014
role: architect
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

产出 P2-design.md：把 TAG0014「agate 派发编排机制（全阶段）」的需求基线（22 条 BDD）转化为可实现的技术方案——候选方案权衡、影响域分析（改/不改/风险）、gate 命令固化、files_to_read 导航清单、minimal_validation。本任务后续 P3-P8 全部按此方案执行。

### 约束

- **阶段完整性**：本任务有 approved plan（agate-workspace/plans/agate-dispatch-orchestration-20260815.md），它是参考输入不是替代。P2 必须产出本任务自己的方案设计（可引用 plan 内容，不可照抄替代），并覆盖 P1 全部 22 条 BDD。
- **dispatch_plan 字段契约已由 plan 定死**（Task 1「字段契约」节 + P1 BDD-1~7/19 引用）：
  - frontmatter 单行 flow YAML，与 candidate_count 同级；无批次时 `{mode: single}`
  - mode 枚举：single / static-batch / parallel / recon-then-split / serial
  - 读取：agate-md-field-get.py 新 op `dispatch_plan`（须注册 KNOWN_OPS，dict→json.dumps 输出路径）
  - 不入 agate-frontmatter-check.py 的 P2 schema（B3 方案 c）
  - 向后兼容：缺字段时 P2 gate 行为完全等同现状
  - P2 gate 校验：mode 合法 / parallel_limit≥1 / batch 含 id+complexity∈{low,medium,high} / batch 数 ≤ parallel_limit（默认 3）
  - 设计不得重新发明或放宽该契约
- **本任务自身 P2-design.md 的 frontmatter**：只需满足当前 P2 gate（candidate_count/packages/domains/ui_affected）。dispatch_plan 是本次改造要引入的机制，不是本次任务自身的 P2-design.md 必须填的字段——不要在本文件写 dispatch_plan（该机制尚未实现，check-gate 也不要求）；在方案正文中设计它。
- **P1 BDD-22（self-gate）必须纳入设计**：本任务改动面大（agate/*.md + agate/scripts/*.py + phase-cards）→ 触发 SELF-GATE。方案须包含 self-gate 流程设计（P7 派发 protocol-alignment-review + commit message 带 self-gate-review:）。
- **影响域分析**：必须基于 P1 同类扫描影响面表（§3）逐文件设计——dispatch-protocol.md（权威节）、P1-P8 阶段卡、architect.md、dispatch-prompt.md、check-gate.py、agate-md-field-get.py、测试文件、README/CHANGELOG/UPGRADING、tests/README.md。明确列出改什么/不改什么/风险。
- **模式 4 合并语义**：plan Task 3/4 要求——P1 侦察产出定义合并语义（BDD 全局编号、包归属去重）；P8 多包拆批合并机制（P8-release-{pkg}.md → 合并 subagent 整合唯一 P8-release.md）。
- **并行规则**：上限默认 3；失败批 retry 与 state-machine retries[Pn] 对齐（默认整组计 1 次）；共享文件统一后处理（P6 例外：走自身汇总 verifier）。
- **P7 归类**：P7 = 模式 1 单发 + 输入数量豁免特例（非串行链）。
- **minimal_validation 必填**：本任务主要是协议文档 + Python 脚本改造。若方案涉及新机制行为假设（如 op 子进程 JSON 读取、flow YAML 解析），须做最小验证（读现有 agate-md-field-get.py 代码确认 yaml 解析路径可用）或声明"纯代码逻辑"并写明依赖的内部函数。
- **gate_commands 固化**：P3/P5 命令按 P0-brief env_constraints test_cmd 声明（pytest 全量 / consistency --strict / count-tests.sh）。P5_e2e 不需要（ui_affected: false）。
- **输出路径硬约束**：产出必须写入 {AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/P2-design.md。

### 上游关联

- P1-requirements.md（22 条 BDD，[NO_NEED_CONFIRM]；§3 影响面扫描表；§6 阶段职责↔plan 6 Task 映射）
- P1-review.md（requirements-review approved；F1-F5 已解决）
- approved plan 的 File Structure + Task 1-6 + 验收标准 6 条
- P0-brief.md 的 known_risks（阶段完整性 / 契约已定死 / 强制同类扫描）

### 输入文件

- {AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/P1-requirements.md（需求基线 + BDD + 影响面表——P2 主要输入）
- {AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/P0-brief.md（任务简报与风险声明）
- {AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/P1-review.md（评审意见参考）
- {AGATE_WORKSPACE}/plans/agate-dispatch-orchestration-20260815.md（approved plan，参考输入）
- {project_root}/AGENTS.md（agate 仓库开发指引：脚本约定/测试约定/dogfooding）
- {project_root}/agate/dispatch-protocol.md（任务粒度指引 L639 + 派发模板节）
- {project_root}/agate/phase-cards/P2-design.md（本阶段产出规格参考）
- {project_root}/agate/assets/execution-roles/architect.md（角色定义：P2 产出字段要求）
- 影响域分析目标文件（按 P1 §3 影响面表逐一读）：agate/phase-cards/P{1..8}-*.md、agate/assets/templates/dispatch-prompt.md、agate/assets/execution-roles/architect.md、agate/scripts/check-gate.py、agate/scripts/agate-md-field-get.py、agate/tests/unit/test_check_gate.py、agate/tests/README.md
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
- 环境：pytest 9.0.3；check-protocol-consistency.py 当前 0 ERROR；gate 工具 ~/.agate 稳定版（v0.48.0）
- worktree 为改造对象：/home/kity/oclab/agate/.worktrees/agate-TAG0014/agate/
- agate-md-field-get.py 现状：已有 yaml 解析路径（plan L124 引用）与 _format_value 输出逻辑；KNOWN_OPS 注册表待确认（plan N9 修复）
- check-gate.py 现状：P2 分支用 _md_field_get 子进程读 pass/blocker_count（plan N8 修复参照路径）；candidate_count 是正则逐行读取
- count-tests.sh 实测基线：P6 前以实测为准（P1 BDD-20 表述为"≥ 改造前实测基线 + 8"）
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
