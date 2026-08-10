---
phase: P1
generated_by: agate-inject-card.sh + 主 Agent
task_id: T091
role: analyst
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

产出 `docs/tasks/T091-v2.0-structured/P1-requirements.md`——agate v2.0 结构化数据改造的需求基线。系统性列出 v2.0 要消除的"正则摩擦"清单，把改造范围固化为可验收的 BDD 条件。

### 约束

1. **这是用 agate 改造 agate（dogfooding）**：改造对象是 worktree 里的 `agate/` 协议本体；开发工具是 `~/.agate`（v0.35.0 稳定版）。两个路径分清，不可混用。
2. **范围（已定，不可扩大）**：只迁移候选数/裁剪类字段——`risk_level`/`phases`/`candidate_count`/`packages`/`domains`/`ui_affected`（及 P1 的 `override`/`implicit_coupling`/`coupling_checklist`/`internal_only`/`internal_only_reason`/`design_trivial`/`follows_existing_pattern` 等裁剪字段）从"正文内嵌 YAML"并入产出物已有的 frontmatter 块。
3. **`gate_commands` 暂留正文**（scope 决策已定）：`agate-read-gate-commands.py`/`agate-gate-missing-cmds.py`/`agate-read-p5-commands.py` 仍从正文正则读，移入 frontmatter 会失配。不列入本任务范围。
4. **硬约束**（评估 §6.3）：`count-tests.sh` 数字不能漂移（当前 594 + sanity 6）；frontmatter 禁止 >3 层嵌套；角色卡必须贴可复制模板；在途任务**双读**（frontmatter 优先 + 旧正则回退）；CHECK 9 锚点表（33 条）全量过一遍。
5. **语义真实性边界（诚实声明，必须写进需求基线）**：结构化解决"格式摩擦"（全角冒号、缩进、PROD_TOUCHED 误报），**不解决"内容真实性"**（BDD-8 单侧/双侧歧义、candidate_count 虚报、权衡关键词）。BDD 设计不得声称"gate 变强"。
6. **风险等级判定**：这是协议级重构（约 25-30 个文档/角色卡/模板 + 14 个脚本 + 15 个测试文件受影响），风险等级应为 high 或 medium-high。
7. **frontmatter schema 校验器**是新交付物（仿 `.state.yaml` 的 `agate-state-yaml-check.py` 模式），BDD 必须覆盖"subagent 写坏格式 → gate 拦截"的机制。
8. P1 产出物本身**按 v0.35 当前格式写**（能过当前 gate），不要用"新格式"写 P1（新格式的读取正确性由 P3/P5 的 fixture 覆盖）。

### 上游关联

- P0-brief.md 已写（任务一句话、known_risks、executor_env、env_constraints 齐全）
- 可行性评估全文（字段清单 §1、方案对比 §3、风险 §5、路线 §6）——核心输入
- HANDOFF-V2.0.md（交接文档，含 scope 决策与硬约束）
- 既有 v2.0 Phase1 plan（已过时但含字段清单，供参考）

### 输入文件

- docs/tasks/T091-v2.0-structured/P0-brief.md（任务简报和风险声明）
- ~/.agate/WORKFLOW.md（协议主流程）
- ~/.agate/assets/execution-roles/analyst.md（角色定义）
- 可行性评估全文：/tmp/opencode/feasibility.md（评估人已落盘的副本）
- HANDOFF-V2.0.md（worktree 根目录，交接文档）
- 当前协议本体（读现状，判断隐含依赖）：
  - ~/.agate/scripts/agate-md-field-get.py（核心改造点：正则 → pyyaml frontmatter + 回退）
  - ~/.agate/scripts/agate-state-yaml-check.py（frontmatter 校验器范式）
  - ~/.agate/scripts/check-gate.sh（P1/P2 门禁读取点）
  - ~/.agate/scripts/check-pruning.sh（裁剪字段读取点）
  - ~/.agate/assets/templates/task-files.md（P1/P2 模板，frontmatter 并入点）
  - ~/.agate/assets/execution-roles/analyst.md、architect.md（角色卡，frontmatter 并入点）
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
- 环境状态：worktree 分支 feat/v2.0 = e5540fc（= main = v0.35.0），bats 1.10.0 / py3.12 / pyyaml / shellcheck 可用
- 测试基线：count-tests.sh 输出 594（sanity.bats 6 另算）
- 版本：~/.agate = v0.35.0（主 checkout /home/kity/oclab/agate，勿动）
- 关键路径：改造对象 = /home/kity/oclab/agate/.worktrees/v2.0/agate/；开发工具 = ~/.agate/
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
