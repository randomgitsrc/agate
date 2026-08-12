---
phase: P1
generated_by: agate-inject-card.sh + 主 Agent
task_id: T001
role: analyst
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

产出 `docs/tasks/T001-v2.0-structured/P1-requirements.md`——agate v2.0 结构化数据改造的**完整需求基线**，覆盖 A+B+C+D 四流（不是只做流 A）。

### 范围（四流全做，不可收窄）

- **流 A（P1/P2 格式迁移 + schema 校验器）**：
  - P1 字段：`risk_level` / `phases` / `override` / `implicit_coupling` / `coupling_checklist` / `internal_only` / `internal_only_reason` / `跳过风险` / `design_trivial` / `follows_existing_pattern` / `domains` / `packages` 迁入 frontmatter
  - P2 字段：`candidate_count` / `packages` / `domains` / `ui_affected` 迁入 frontmatter
  - 交付：`agate-md-field-get.py` 双读改造（pyyaml frontmatter 优先 + 正则回退）+ 新增 `agate-frontmatter-check.py` / `check-frontmatter.sh` 校验器挂 pre-commit
- **流 B（P6/P7 结果结构化）**：P6 汇总（pass/fail/ui_affected）入 frontmatter + 逐条 PASS/FAIL 格式从严（行首 `- PASS|FAIL BDD-NN:`）；P7 BLOCKER/DEVIATION/DESIGN_GAP_REVIEWED 状态入 frontmatter
- **流 C（标记状态收尾）**：NEED_CONFIRM/SUGGEST/SCOPE_RESOLVED 状态结构化；**SCOPE+/PROD_TOUCHED/DESIGN_GAP 发现性标记本体保持散文**（评估 §5.5）
- **流 D（任务编号规则改造）**：新编号 `T{项目代号}{编号}`（如 `TAG0001`），校验器 `^T\d+$` → `^T[A-Z]{2}\d+$`，**硬切**不兼容旧格式；`check-changelog.sh` 去掉短前缀提取摩擦（`grep -oE 'T[0-9]+'` → 直接匹配完整 task_id）

### 约束

1. **本 task 自身用旧协议**（自举原则）：本 task 编号 `T001`，全程按 v0.35 格式产出、能过 v0.35 gate。新编号规则是流 D 的**产物**，不是本 task 的运行时约束。
2. **gate_commands 暂留正文**：4 个读取工具 `agate-read-gate-commands.py` / `agate-gate-missing-cmds.py` / `agate-read-p5-commands.py` / `agate-gate-p5-count.py` 仍从正文正则读，不迁移。
3. **语义真实性不升不降**：结构化只提高解析可靠性，不改变 gate 对内容真实性的判断。BDD-8 单侧/双侧歧义、candidate_count 虚报在结构化后依旧。BDD 不得声称"gate 变强"。
4. **硬约束**（P0-brief 已列 9 条）：count-tests.sh 594 不漂移；frontmatter 禁 >3 层嵌套；角色卡贴可复制模板；在途任务双读；CHECK 9 锚点表 37 条全量校准；设计文档写明语义真实性边界；gate_commands 暂留；每流先写 regression；流 D 硬切。
5. **BDD 分组**：按流 A/B/C/D 分组编号（如 BDD-A1.. / BDD-B1.. / BDD-C1.. / BDD-D1..），或连续编号但标注所属流。每条单一 Given/When/Then。
6. **摩擦清单**：必须系统性列全（F1-F10 已有 + 新增流 D 编号摩擦、流 B 总结行误判等），不能只列流 A 的。

### 客观查证信息（主 Agent 亲手核证，必须引用这些数字，不得自行编造）

- count-tests.sh 实测 = **594**（sanity 6 另计）
- CHECK 9 锚点表 = **37 条**（AST 解析 `SCRIPT_ALIGNMENT_ANCHORS`）
- gate_commands 读取工具 = **4 个**（含 `agate-gate-p5-count.py`）
- gate 退出码：exit 0=通过 / 1=未通过 / 2=需主 Agent 自判（P1 分支正常完成路径 = exit 2）
- 三层结构：层 1 真 frontmatter（review status/agent）不迁移；层 2 正文内嵌 YAML（P0/P1/P2 约 12-16 字段）流 A 迁；层 3 纯散文标记（P1/P4/P5/P6/P7/P8 约 25 个）流 B/C 处理
- 受影响测试：约 **15 个测试文件、355 个 @test**（占 594 的 60%）
- 迁移字段源（评估 §1.2/§1.4）：P1 的 `risk_level`/`phases` 由 `check-pruning.sh:16,18` → `agate-md-field-get.py` 读；`override`/`implicit_coupling`/`coupling_checklist`/`internal_only`/`internal_only_reason`/`跳过风险`/`design_trivial`/`follows_existing_pattern` 由 `check-pruning.sh`/`check-gate.sh:111` grep；P2 的 `candidate_count` 由 `check-gate.sh:106` grep、四字段由 `check-gate.sh:138` grep、`ui_affected` 由 `check-p6-evidence.sh:61`/`check-p6-provenance.sh:152` 调 `agate-md-field-get.py`

### 上游关联

- P0-brief.md（A+B+C+D 范围、12 条风险、9 条硬约束、流 D 硬切决策）
- HANDOFF-V2.0.md（交接文档：scope 决策 §5.3、硬约束 §5.4、已踩坑 §8）
- 可行性评估全文 /tmp/opencode/feasibility.md（三层结构 §0/§1、方案对比 §3、风险 §5、路线 §6）

### 输入文件

- docs/tasks/T001-v2.0-structured/P0-brief.md（任务简报和风险声明，必读）
- HANDOFF-V2.0.md（交接文档，必读）
- /tmp/opencode/feasibility.md（可行性评估全文，必读）
- ~/.agate/assets/execution-roles/analyst.md（角色定义）
- ~/.agate/phase-cards/P1-requirements.md（阶段卡片，产出规格参考）
</dispatch_guide>

<!-- AGATE_CARD_START -->
## 当前阶段卡片：P1

路径：phase-cards/P1-requirements.md
---
# P1 — 需求基线

> 当前状态：[首次 / 重试 #N]
> P1 不可裁剪（核心阶段）

## 如果是首次进入本阶段

1. 派发 analyst subagent → 产出 P1-requirements.md
   1.1 写 P1-dispatch-context-analyst.md（派发指引：目标/约束/上游关联/输入文件 + 客观查证信息）
2. 主 Agent 确认：BDD 验收条件 ≥1 条 + 无未决 NEED_CONFIRM
2.5 派发 requirements-review subagent（角色文件：{agate_root}/assets/review-roles/requirements-review.md）
     2.5.1 写 P1-dispatch-context-requirements-review.md（派发指引：目标/约束/上游关联/输入文件 + 客观查证信息）
    输入：P1-requirements.md
    产出：P1-review.md（agent≠main，含 BDD 编号引用 + 覆盖维度标注）
    review 不通过 → analyst 修改 → 再 review → … → approved（⑩迭代循环）
3. 预跑 check-gate.sh P1（exit 2，主 Agent 自判）
4. 更新 .state.yaml phase=P1 → P2
5. git add docs/tasks/{Txxx}/（含 .state.yaml + 产出文件，若 .gitignore 忽略需 git add -f）
6. git commit -m "wf({Txxx}-P1): {摘要}"

## 如果是重试

确认上一轮失败原因（BDD 不完整 / domains 声明错 / NEED_CONFIRM 未处理）
→ review 不通过时：analyst 修改需求 → 重派 requirements-review → 共享 retry 预算
→ 读 agate/rules/state-transitions.md 确认 retry 上限（P1 MAX=3）

## 前置条件

- [ ] P0-brief.md 完成（四字段齐全）

## 派发

- **角色**：analyst（`{agate_root}/assets/execution-roles/analyst.md`）
- **输入**：P0-brief.md（env_constraints / known_risks / executor_env）
- **输出**：P1-requirements.md
- **派发 prompt 模板**：`{agate_root}/assets/templates/dispatch-prompt.md`

## 产出规格

P1-requirements.md 必须包含：
- BDD 验收条件（至少 1 条，Given/When/Then 格式）
- `domains:` 声明（backend / frontend / mcp / security）
- `packages:` 声明（受影响的包/模块）
- `risk_level:` 声明（low / medium / high）→ 决定 P2 评审强度
- `phases:` 裁剪声明（跳过哪些阶段 + 理由）
- `capability_requirements:` 能力需求声明（available / supplementable / GAP 三态）
- 无未决 `[NEED_CONFIRM]`（有则 PAUSED）；无待确认项时写 `[NO_NEED_CONFIRM]`

**NEED_CONFIRM 分级**：
- `[SUGGEST: 推荐 X，理由 Y]` - 有倾向但求确认。主 Agent 可自行采纳倾向（除非涉及破坏性变更/业务方向），不必问用户
- `[NEED_CONFIRM]` - 真无方向需人定夺。阻塞推进，主 Agent 问用户

## gate 规则

check-gate.sh P1 → P1-review.md 存在 + status:approved + agent≠main + 含 BDD 编号锚点 → exit 2（BDD 编号格式为 `#### BDD-NN:`）；缺 P1-review.md / agent=main / 无锚点 → exit 1
P1 评审不可裁——所有任务都走独立 requirements-review，无例外

## 推进条件（全部满足才写 phase: P2）

- [ ] P1-requirements.md 含 BDD ≥1 条
- [ ] domains / packages / risk_level / phases 已声明
- [ ] 无 [NEED_CONFIRM] 标记
- [ ] 无 status: GAP（supplementable 不阻，GAP 阻）
- [ ] P1-review.md status: approved（agent≠main，含 BDD 编号锚点）

## 常见错误

1. **BDD 写成技术实现而非用户行为**：BDD 应该描述"用户能看到什么/系统应该做什么"，不是"调用哪个 API"
2. **domains 声明不全**：漏了某个受影响域 → P2 不派该域的评审 → 实现方向错误
3. **capability_requirements 漏声明**：P6 验收时才发现需要但不可用的能力 → 返工
4. **gate 不过 ≠ 你失败了**：红灯指向工作/设计的问题，不指向你。正确动作是诊断→退回/重试/PAUSED，不是修改产出让它变绿。

## 下游影响

- P2 设计依赖 domains + risk_level 决定评审角色
- P6 验收逐条对照 P1 的 BDD（PASS/FAIL 总数必须 ≥ P1 BDD 总数）
- P7 一致性检查依赖 packages 声明做跨文件交叉核对

## 评审

P1 评审通用必有（所有任务都走 requirements-review），P2/P4 评审是 C8 域触发（见 review-mapping.md）——二者在"是否通用"上不对称，仅在"独立 subagent、agent≠main"上类比。P1 评审不可裁剪。
review 不通过 → analyst 修改需求 → 再 review（⑩迭代循环），直至 approved。

> 完成 → 读 phase-cards/P2-design.md


## P1 基线保护

P1-requirements.md 是需求基线，后续阶段（P2-P8）不应直接修改。如需变更（如 P4 发现 BDD 矛盾需补充注释），必须：
1. 主 Agent 显式批准
2. 在变更处标注 `[BASELINE_CHANGE: 理由]`
3. 不改 BDD 的 Given/When/Then 语义（只补充注释/优先级说明）
<!-- AGATE_CARD_END -->

<objective_info>
- 环境状态：worktree 分支 feat/v2.0，bats 1.10.0 / py3.12 / pyyaml / shellcheck 可用
- 测试基线：count-tests.sh 输出 594（sanity.bats 6 另算）
- 已核验事实：CHECK 9 锚点表实际 37 条；读 gate_commands 的工具实际 4 个；gate 退出码 exit 2 = 需主 Agent 自判
- 关键路径：改造对象 = /home/kity/oclab/agate/.worktrees/v2.0/agate/；开发工具 = ~/.agate/
- 任务编号：本 task = T001（agate 改造项目独立编号，不沿用 peekview T090 系列）
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
