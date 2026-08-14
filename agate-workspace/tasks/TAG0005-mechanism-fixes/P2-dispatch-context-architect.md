> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。

---
phase: P2
generated_by: agate-inject-card.sh + 主 Agent
task_id: TAG0005
role: architect
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

产出 `P2-design.md`，为 agate 机制修复批（TAG0005）设计实现方案。P1 已锁定 16 条 BDD（5 处修复），本阶段为每处修复定设计选型，产出候选方案 + 权衡 + 选择理由，固化 gate_commands / files_to_read / env_constraints。

### 约束

- **设计选型点（每处修复已标注 P1 留下的决策空间）**：
  1. **RM-AG0010（BDD-1/2）——C8 表补 backend P2 评审**：
     - 方向已拍板：C8 补 backend P2 评审（非 gate 豁免），三处 C8 表同步（role-system.md / rules/review-mapping.md / phase-cards/P2-design.md），check-gate.sh 不改。
     - 需设计：**backend 域 P2 触发哪个评审角色**。候选参考：role-system.md 角色表里 P2 阶段的角色（plan-eng-review / plan-design-review / plan-ceo-review / review）——backend 设计评审用哪个最合理；是否要同时在 dispatch-protocol.md 或 P2-design.md 的评审派发节补充说明；新角色是否影响现有 backend high 任务（会同时命中 backend+high 两行 → 评审角色去重）。
     - 注意：本任务自身就是 backend 域任务，P2 评审会按新 C8 规则被 gate 要求——设计要自洽（本任务 P2 也会派该评审角色）。
  2. **RM-AG0011（BDD-3/4/5/6）——P5 主/辅计数**：
     - 需设计：`agate-gate-p5-count.py` 输出格式（保持纯数字但有主/辅两个值？还是结构化？），check-gate.sh L253-258 的 WARNING 消费逻辑同步。
     - P1 隐含需求 I6：输出格式变化须同步消费方 check-gate.sh L253；I5：read-p5-commands.py 不改（执行枚举）。
  3. **RM-AG0012①（BDD-7/8/9）——Review 指令条件注入**：
     - 需设计：实现位置——render 脚本（`agate-render-dispatch-prompt.sh`）在渲染时按 ROLE_DIR（execution vs review）决定是否注入「Review 角色特别指令」节。模板 `dispatch-prompt.md` 是否拆分该节为独立块？render 脚本怎么知道模板中该节的边界（当前 main_block 是模板 L1 到「## 阶段特定提示」之前整块）？
     - 注意 dispatch-protocol.md L427-494 内联模板无该节——修复后 assets 模板条件注入与内联模板语义一致性（P1 隐含需求 I7）。
  4. **RM-AG0012②（BDD-10/11）——回归测试锁定**：
     - 缺陷已修（exit 2），仅补 bats 回归测试。需设计：新用例编号（RP.17?）+ 断言（exit 2 + stderr 含「角色文件不存在」）+ 放哪个测试文件（agate-render-dispatch-prompt.bats）。测试计数漂移处理见 P1 I8（同步 agate/tests/README.md 计数表，render=16→17）。
  5. **RM-AG0003（BDD-12/13/14）——空返回自动重试**：
     - 需设计：dispatch-protocol.md L105-129 空返回恢复策略的增量措辞——「自动重试一次」放哪、与既有「分析→调整→重派」的关系、<1min 异常告警阈值怎么表述、复用 L128 派发耗时弱信号。
  6. **BDD-16——check-debt.sh 依赖加载失败 exit 非零**：
     - P1 裁定同同类，修法由 P2 定（建议依赖失败改 exit 2 WARNING，与 check-gate.sh 约定一致；「有意跳过」分支保留 exit 0）。
- **gate_commands 设计**：本任务是脚本+文档+测试修复，P5 验证命令应为全量 bats + consistency + shellcheck（注意 check-protocol-consistency.py 必须用 worktree 自己的脚本）。P3 可声明 TDD 红灯确认命令。
- **files_to_read**：列出实现需要的文件（P1 已核对的 8 个协议文件 + 2 个测试文件 + count-tests.sh），大文件标行号范围。
- **minimal_validation**：本任务纯代码逻辑（脚本条件分支/文档措辞），无外部系统依赖。须声明「纯代码逻辑，无外部系统依赖」并写明依赖的内部函数/数据转换（如 agate-gate-p5-count.py 的 regex、render 脚本的 sed 提取逻辑）。
- **格式约束**：约束节避免行首 `- PASS`/`- FAIL`（provenance 预判检测）。
- **范围锁定**：若设计发现需改动超出 P1 锁定范围，标注 `[SCOPE+]` 回报，不擅自扩大。

### 上游关联

- `P1-requirements.md`（需求基线，16 BDD + 隐含需求 I1-I14 + 同类扫描结论）
- `P1-review.md`（评审 approved）
- `P0-brief.md`（任务简报）

### 输入文件

- `agate-workspace/tasks/TAG0005-mechanism-fixes/P1-requirements.md`（需求基线，核心输入）
- `agate-workspace/tasks/TAG0005-mechanism-fixes/P0-brief.md`（任务简报）
- 协议文件（按需核验，主 Agent 已核对行号）：
  - `agate/scripts/check-gate.sh`（P2 L157-173 / P5 L253-258 / P5 L249 调用 count.py）
  - `agate/scripts/agate-gate-p5-count.py`（L19 计数）
  - `agate/scripts/agate-read-p5-commands.py`（L26，不改）
  - `agate/scripts/agate-render-dispatch-prompt.sh`（L63-69 角色判断 / L78 main_block / L128-142 sed 替换）
  - `agate/scripts/check-debt.sh`（L21-30 依赖加载 + 有意跳过分支）
  - `agate/assets/templates/dispatch-prompt.md`（L9-13 Review 指令）
  - `agate/role-system.md`（C8 表 L54-61 + 角色表 L40-48）
  - `agate/rules/review-mapping.md`（C8 表 L15-23）
  - `agate/phase-cards/P2-design.md`（C8 表 L93-97）
  - `agate/dispatch-protocol.md`（L105-135 空返回恢复策略 / L427-494 内联模板）
  - `agate/tests/unit/agate-render-dispatch-prompt.bats`（RP.1-16 + 1，无角色缺失用例）
  - `agate/tests/unit/check-gate.bats`（G5_CMD.1/.5 断言旧文案）
  - `agate/tests/README.md`（L33 render=16 计数表）
  - `agate/tests/scripts/count-tests.sh`（L22 陈旧引用）
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
- 环境状态：worktree `/home/kity/oclab/agate/.worktrees/agate-TAG0005-0009`；协议 v0.44.0 基线；714 bats 全绿；P1 已 commit（phase=P1）
- RM-AG0012② 实测已修复（exit 2），仅需补测试
- 本任务自身是 backend 域任务 → P2 评审按新 C8 规则被 gate 强制要求 P2-review.md（现 check-gate.sh 无条件要求）——P2 设计要自洽
- check-debt.sh:26 依赖加载失败静默 exit 0 已裁定同同类（BDD-16）
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
