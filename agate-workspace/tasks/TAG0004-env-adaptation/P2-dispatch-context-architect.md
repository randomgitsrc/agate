> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。

---
phase: P2
generated_by: agate-inject-card.sh + 主 Agent
task_id: TAG0004
role: architect
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

产出 `P2-design.md`——TAG0004（agate 脚本健壮性 + 环境适配）的技术方案设计：把 P1 的 37 条 BDD（S1/S2/S3/M4/M5/M6/M9 + Q1/Q2/Q5 + RM-AG0001/AG0002 + TPV0090-M4）转化为可实现的候选方案 + 权衡 + 选择理由，声明四字段（packages/domains/ui_affected/gate_commands）+ files_to_read + env_constraints + minimal_validation。

### 约束

- **修复对象 = worktree 的 `agate/` 目录**（`/home/kity/oclab/agate/.worktrees/agate-TAG0004/agate/`）。**禁止改主 checkout `/home/kity/oclab/agate` 和 `~/.agate`**（稳定版 v0.43.0，跑 gate 用）。design 中所有路径以 worktree 为基准。
- **Linux 基线不回归**：现有 676 bats 测试全绿是回归底线。每个方案必须显式说明"Linux 行为不变"的验证策略。
- **Windows 兼容是增量**：本环境（Linux）无法实测 Windows——方案不能依赖 Windows 运行时验证；Windows 特有行为靠 CI windows-latest matrix 兜底（protocol-tests.yml 需新增）。
- **多方案探索**：candidate_count ≥2 + 每个方案权衡（优点/风险/工作量）+ 选择理由。M6（frontmatter 容错 vs .gitattributes）、S1（数组化改造方式）、Q1（路径归一化策略）至少各需 2 个候选方案。已有明确倾向的（P1 SUGGEST：M6 走 frontmatter 容错、S3 走 grep 断言审计、RM-AG0002 走保守判定）可作为候选之一，但仍需写出替代方案对比。
- **gate_commands 在 P2 固化**：本任务无 UI（ui_affected: false），不需要 P5_e2e。测试运行器是 bats（非 pytest）——gate_commands.P3 建议声明（如 `bats agate/tests/unit/`）供 check-tdd-red.sh 读取；P5 声明全量回归命令。formatter：bats 无现成 JSON formatter，可声明或不声明——不声明时 check-tdd-red.sh 退化为 exit-code-only（本任务 P3 需写 A/B 判定增强测试，见下）。
- **TPV0090-M4 与 RM-AG0002 同文件（check-tdd-red.sh）同修**：A/B 判定增强一次设计——BDD-30/31（无 formatter 路径）+ BDD-35/36/37（NameError B 类识别）要覆盖完整判定矩阵（formatter 有无 × 错误类型），不能只修一半。
- **S3 13 个 py 加 encoding 的测试策略**：P1 SUGGEST 已采纳 grep 断言审计测试（所有 open() 带 encoding），设计要给出断言审计的具体实现方式（bats 测试内 grep 断言）。
- **Q2 是纯文档修复**：只补注 phase-cards，不改 gate 判定逻辑。design 中 Q2 部分不应引入 gate 逻辑改动。
- **S1 最危险**：改数组后需验证 Linux 全部 commit 场景（根/任务级 .state.yaml 混合、多任务并发）——design 要列出验证场景清单。
- **minimal_validation 必填**：本任务主要改 shell/python 脚本（纯代码逻辑），但需验证关键假设——如 S2 正则字符类加宽在 `LC_ALL=C` 下的实际匹配行为、M4/M5 `[:：]` bracket 在 POSIX locale 下的行为（可跑 `LC_ALL=C` 测试）、Q1 `${CARD_FILE#$AGATE_ROOT/}` 前缀匹配的边界。建议先跑最小验证确认假设再定方案。
- **格式约束**：约束节避免行首 `- PASS`/`- FAIL`（被 provenance 预判检测匹配）。改用"通过/失败"或加引号。

### 上游关联

- P1-requirements.md 已 approved（37 BDD）：S1（BDD-1..4 空格路径 fail-open）、S3（BDD-5..8 encoding）、S2（BDD-9/10 中文证据文件名）、M4/M5（BDD-11..13 全角冒号 locale）、M6（BDD-14..16 CRLF）、M9（BDD-17 路径元字符）、其他（BDD-18..20）、Q1（BDD-21/22 路径归一化）、Q2（BDD-23..25 卡片对齐）、Q5（BDD-26/27 SETUP/gitignore）、RM-AG0001（BDD-28/29 反引号盲区）、RM-AG0002（BDD-30/31 无 formatter A/B）、TPV0090-M4（BDD-35..37 NameError B 类）、全局回归（BDD-32..34）。
- P1 SUGGEST 已采纳：M6 走 frontmatter 容错、S3 走 grep 断言审计、RM-AG0002 走保守判定。
- 审计范围（P1 §6）：46 处代码位置已逐行核验，design 需引用。

### 输入文件

- `agate-workspace/tasks/TAG0004-env-adaptation/P1-requirements.md`（需求基线 + 37 BDD + 审计范围）
- `agate-workspace/tasks/TAG0004-env-adaptation/P0-brief.md`（任务简报：env_constraints / known_risks）
- `HANDOFF-TAG0004.md`（worktree 根：交接单，双工作区纪律、验证命令、阶段推进纪律）
- `AGENTS.md`（项目约定：脚本关键约定、测试约定、SELF-GATE 触发清单）
- 按需核验代码：`agate/scripts/` 下对应脚本（P1 §6 审计范围 46 处位置）、`.gitattributes`、`.gitignore`、`.github/workflows/protocol-tests.yml`、`agate/SETUP.md`、`agate/phase-cards/*.md`
- `{agate_root}/assets/execution-roles/architect.md`（角色定义）
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
6. git add {AGATE_WORKSPACE}/tasks/{Txxx}/（含 .state.yaml + 产出文件，若 .gitignore 忽略需 git add -f）
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
- 环境状态：worktree `/home/kity/oclab/agate/.worktrees/agate-TAG0004`；协议 v0.43.0；基线 676 bats 全绿；依赖 bash 5.2 / python 3.12 / pyyaml / bats 1.10 / shellcheck
- 关键路径：产出 `agate-workspace/tasks/TAG0004-env-adaptation/P2-design.md`
- 查证结果：P1 §6 审计范围已逐行核验 46 处代码位置；P1-review 复审 approved
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
