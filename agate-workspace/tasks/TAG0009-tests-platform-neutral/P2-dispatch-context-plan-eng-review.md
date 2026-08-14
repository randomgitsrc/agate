> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。

---
phase: P2
generated_by: agate-inject-card.sh + 主 Agent
task_id: TAG0009
role: plan-eng-review
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

评审 `P2-design.md`（TAG0009 测试平台无关化方案），产出 `P2-review.md`（status: approved / rejected，结论引用具体锚点：设计方案节编号 / 候选方案 / minimal_validation / files_to_read）。

### 约束

- **评审对象**：`agate-workspace/tasks/TAG0009-tests-platform-neutral/P2-design.md`（architect 新产出，9 个设计选型点 + 2 个候选方案整体架构）
- **评审重点**（plan-eng-review 角色检查清单 + 本任务特殊性）：
  1. **整体架构取舍**：候选 A（harness shim + 扫描器 gate + 批量修测试）vs 候选 B（改 17 产品脚本）——shim 方案是否真的覆盖 41 例 script-side 失败、是否引入复杂度过高的测试基建
  2. **静态扫描器设计**（§2.1）：模式集 R1-R5 是否准确（豁免规则 / `# scan-exempt:` 标记机制）；扫描范围（tests/ 全树）与阻断方式（CI job）是否合理；扫描器自身平台无关性（POSIX ERE）设计是否成立
  3. **harness shim 设计**（§2.3）：包装器内嵌绝对路径避免自解析循环——正确性；9 文件 setup 注入是否有遗漏；BDD-17（Linux 不劣化）论证是否成立
  4. **PYTHON 探测 helper**（§2.2）：detect_python + PYTHON 导出设计；回退分支测试（BDD-15）可否行
  5. **symlink 平台分支**（§2.5 + [SCOPE+] pre-push-hook）：[SCOPE+] 是否属 BDD-8 同类扫描闭环范围内（不改 P1 范围）；复制模式 mock 复用 L43 先例是否充分
  6. **bc→awk**（§2.8）：唯一产品脚本改动——awk 求和正确性、消除管道优先级隐患的论证；是否引入 Linux 回归风险
  7. **CI 设计**（§2.9）：bats job 增 windows-latest 的安装步骤「P5 验证时定稿」——设计是否留下未决项（I7 supplementable 是否已显式声明）
  8. **gate_commands**（§5）：P5 = 全量 bats + consistency + shellcheck + 扫描器（1 主 + 多辅）；P3 = "bats" 配合 TEST_RUNNER 逐文件红灯确认——是否可执行
  9. **实现就绪度**：files_to_read（§6）是否覆盖 29 BDD 实现所需全部上下文
- **多方案探索（nudge）**：整体架构有 2 候选；各选型点内部应有两方案权衡（§2 已列，核对是否形式满足）
- **技术债**：若提出「后续应重构/存在架构债」，用标准 DEBT 条目格式登记 `agate-workspace/debt/tech-debt.md`
- **格式约束**：评审文件避免行首 `- PASS`/`- FAIL`。结论引用锚点。

### 上游关联

- `P2-design.md`（评审对象）
- `P1-requirements.md`（29 BDD）
- `P0-brief.md`（范围基准）

### 输入文件

- `agate-workspace/tasks/TAG0009-tests-platform-neutral/P2-design.md`（评审对象）
- `agate-workspace/tasks/TAG0009-tests-platform-neutral/P1-requirements.md`（需求基线对照）
- `agate-workspace/tasks/TAG0009-tests-platform-neutral/P0-brief.md`（范围基准）
- 按需核验：
  - `agate/tests/helpers/fixtures.bash` / `load.bash`（helper 挂载点）
  - `agate/tests/unit/check-tdd-red.bats`（PATH 15 处）、`agate/tests/unit/install-hook.bats`（L43 mock）、`agate/tests/integration/pre-push-hook.bats`（L11 [SCOPE+]）
  - `agate/scripts/agate-extract-context.sh`（L128 bc）、`agate/scripts/check-state-transition.sh`（script-side python3）
  - `.github/workflows/protocol-tests.yml`（CI 现状）
  - `agate/tests/scripts/check-platform-assumptions.bats`（若已存在，应不存在——P4 新建）
- `{agate_root}/assets/review-roles/plan-eng-review.md`（角色定义）
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
- 环境状态：worktree `/home/kity/oclab/agate/.worktrees/agate-TAG0005-0009`；TAG0005 已 READY；TAG0009 P1 已 commit（29 BDD）
- 本任务自身是 backend 域 + medium → 按 C8 新规则 P2 评审映射 plan-eng-review
- P2 设计含 [SCOPE+]：pre-push-hook.bats L11 symlink 断言（BDD-8 同类闭环，不改 P1 范围）
- minimal_validation 已实测：harness shim CONFIRMED（3 步验证）+ 扫描器模式集 CONFIRMED（真实树实测 R1-R5）
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
