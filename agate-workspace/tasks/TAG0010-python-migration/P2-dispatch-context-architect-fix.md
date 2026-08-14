---
phase: P2
generated_by: agate-inject-card.sh + 主 Agent
task_id: TAG0010-python-migration
role: architect
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）
> 本文件是**修复轮（incremental）**派发指引——复用上轮 dispatch-context（P2-dispatch-context-architect.md）的约束，本文件只给修复目标。不要重写完整目标/约束/上游关联。

### 修复目标（plan-eng-review 判定 rejected，3 个 BLOCKER + 2 个非阻塞）
修订 {AGATE_WORKSPACE}/tasks/TAG0010-python-migration/P2-design.md，**其余内容不动**（评审已锁定：方案 A、ruff 规则集、consistency 锚点同步 4 项、gate_commands、非 hook 删档/同名换后缀/扫描器扩展/ruff CI 独立 job 均 approved）：

1. **BLOCKER-1：BDD-6 前置验证缺失**（评审 §BLOCKER-1）
   - 实测证据：扩展扫描器后对既有 18 py 命中 4 行 R2——`agate-json-get.py:5`（docstring 内 `echo "$x" | python3 -c ...`）、`check-protocol-consistency.py:23-25`（docstring 内 `python3 scripts/check-protocol-consistency.py` 等）。当前 `r2_exempt` 只豁免 `#`/`@test`/`command -v`/`env` 形态（check-platform-assumptions.sh:43-55），对 docstring 不豁免。
   - **主 Agent 决策（已确认方向，写死进设计）**：扫描器 py 版（批次 1 check-platform-assumptions.py）的 `r2_exempt` 语义**扩展到 `"""` docstring 块**（docstring 内示例命令不命中 R2），并同步在 §3.6 的 check-platform-assumptions.bats 断言级变更中新增两类用例：①docstring 内 python3 引用不命中 R2；②真 R2 命中仍被检出。
   - 设计须新增"对既有 18 py 跑扩展后扫描器确认洁净度"的执行方案（预期违规清单 + 处理方式：docstring 豁免后零命中）。

2. **BLOCKER-2：批次 0 依赖自相矛盾**（评审 §BLOCKER-2）
   - 问题：批次 0 声称删除 `_find_bash`/`_bash_cmd` + 改调 check-gate.py，但 check-gate.py 批次 2 才产出；`_bash_cmd` 还被 check-tdd-red.sh / check-p6-provenance.sh（均批次 2 py 化）调用。
   - **主 Agent 决策（已确认方向，写死进设计）**：批次 0 收窄为「ci-gate-backstop.py 的 resolve_tasks_dir 改调 agate_common.resolve_workspace」；`_bash_cmd` 保留到批次 2 随各被调脚本 py 化逐个删除；`run_gate` 的 check-gate.sh → check-gate.py 切换移入批次 2（与 check-gate.py 产出同批）。批次 0 验证 = 仅 workspace-resolve.bats + helpers-python.bats + ci-gate-backstop.bats（断言仅 workspace 解析相关）改后绿。

3. **BLOCKER-3：hook 薄壳 fallback 语义**（评审 §BLOCKER-3）
   - **主 Agent 决策（已确认，BASELINE_CHANGE 已批准并标注到 P1 BDD-9）**：采纳方案 Y——**fail-closed 阻断**。python 不可探测/exec 失败时薄壳输出明确 GATE ERROR + exit 非 0，**不运行 sh 兜底逻辑**（pyyaml 强制依赖下 python 是硬前提；保 sh 逻辑需双份维护 gate 判定）。
   - 修订 §3.3：fallback 语义改为 fail-closed（当前代码已是 echo + exit 1，需把注释和描述改准确——删掉"保留 sh 逻辑 fallback"表述，明确"fail-closed 阻断（非静默放行）"）；薄壳描述改为"python 探测 + exec + 失败 fail-closed 阻断"；同时补充 P1 BDD-9 BASELINE_CHANGE 的引用。

4. **非阻塞-1：pyproject.toml 死 ignore 条目**：`E501`（select 只含 E4/E7/E9，E501 未被选中）、`PLR0911/0912/0915/2004` 与 `PLC0415`（select 只含 PLW，PLR/PLC 未选中）是死条目——清理或显式注明。

5. **非阻塞-2：files_to_read 补 pre-push-gate.sh / commit-msg-self-gate.sh**（批次 3 薄壳化的独立迁移源：pre-push 的 AGATE_ALIGNMENT_REVIEW_THRESHOLD 关键字保留、commit-msg 的 self-gate 触发面 grep）。

### 上游关联
- 上轮 architect 产出：P2-design.md（方案 A 推荐，3 候选，批次 0-4）
- plan-eng-review 评审：P2-review.md（status: rejected，§BLOCKER-1/2/3 + 非阻塞 2 项——修复依据）
- 主 Agent 已批准 BASELINE_CHANGE 到 P1 BDD-9（fail-closed 语义）

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0010-python-migration/P2-design.md（被修订对象）
- {AGATE_WORKSPACE}/tasks/TAG0010-python-migration/P2-review.md（评审结论——修复依据）
- {AGATE_WORKSPACE}/tasks/TAG0010-python-migration/P2-dispatch-context-architect.md（上轮派发指引，约束继续生效）
- {AGATE_WORKSPACE}/tasks/TAG0010-python-migration/P1-requirements.md（BDD-9 已含 BASELINE_CHANGE 标注）
- {project_root}/agate/scripts/check-platform-assumptions.sh（r2_exempt 现状——BLOCKER-1 设计依据）
- {project_root}/agate/scripts/ci-gate-backstop.py（_bash_cmd/run_gate 调用现状——BLOCKER-2 设计依据）

### 产出要求
修订 P2-design.md（仅 3 BLOCKER + 2 非阻塞相关处），完成后保持：
- frontmatter 不变（candidate_count: 3 / packages / domains / ui_affected: false）
- 方案 A 锁定不动；候选方案 B/C 表述不动
- gate_commands / minimal_validation（已 confirmed 项不动）/ env_constraints 不动
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
  P3: "pytest"                  # 可选：测试运行器（verbose 输出，供 check-tdd-red.sh 自动读取）
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
- 扫描器实测：扩展 .py 后对既有 18 py 命中 4 行 R2（docstring 内 python3 引用，check-platform-assumptions.sh r2_exempt 只豁免 #/@test/command -v/env 形态）
- ci-gate-backstop.py：_bash_cmd 调 check-tdd-red.sh(:181-184)、check-p6-provenance.sh(:267-270)；run_gate 调 check-gate.sh(:51-58)
- 环境：Linux；python3 3.12.3 + pyyaml 6.0.3 + ruff 0.16.3；bats 1.10.0
- worktree 根：/home/kity/oclab/agate/.worktrees/agate-TAG0010（改造对象）；~/.agate = 稳定版 v0.45.0（禁止改动）
</objective_info>
