---
phase: P1
generated_by: agate-inject-card.sh + 主 Agent
task_id: TAG0010-python-migration
role: requirements-review
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
独立评审 {AGATE_WORKSPACE}/tasks/TAG0010-python-migration/P1-requirements.md，产出 {AGATE_WORKSPACE}/tasks/TAG0010-python-migration/P1-review.md。你是独立视角，发现 analyst 的作者盲区：遗漏的隐含需求、不可判定的 BDD、混入的解决方案设计。

### 约束
- **只审不写**——不直接修改 P1-requirements.md；评审意见由主 Agent 回派 analyst 修改。
- 按角色文件检查清单逐项审：BDD 可二值判定（Given/When/Then 可明确 PASS/FAIL、`#### BDD-NN:` 格式连续不跳号、单条 Given-When-Then）、隐含需求覆盖（数据/前端/多端/边界/兼容逐维度）、BDD 跨条一致性、裁剪合理性（risk_level/phases/capability_requirements 三态）、P1 纯净性（无解决方案设计/实现细节）。
- **实质锚点要求**：结论必须引用具体产物锚点（BDD 编号 + 覆盖维度清单），不引用 BDD 编号的裸 "approved" 是假完成——gate 检查锚点存在性。
- 本任务背景：agate 产品逻辑 Python 化（30 个 sh → py，hook 保留 sh 薄壳）。评审时注意影响面映射表（表 A-E）是否真的摸全——这是本任务的核心交付，漏表 = 需求不完整。
- 产出 Header 的 `status:` 初始为 draft，评审完成后改为 approved / rejected / needs-revision。gate 读的是 Header 的 status 字段。
- 禁止行首 `- PASS`/`- FAIL` 格式（provenance 审计拦截）。

### 上游关联
- analyst 已产出 P1-requirements.md：10 条 BDD、5 个 [SUGGEST:]、影响面映射表 A-E（30 sh 清单/文档引用/锚点关键字/受影响 bats/迁移批次）、risk_level=high、phases 全 8 阶段、domains=[backend, cli]、change_type=refactor。
- 需求权威来源：docs/reviews/agate-python-migration-analysis-20260814.md（§9 立项建议 + 5 条验收标准）。

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0010-python-migration/P1-requirements.md（被审对象）
- {AGATE_WORKSPACE}/tasks/TAG0010-python-migration/P0-brief.md（任务简报与风险声明）
- {AGATE_WORKSPACE}/tasks/TAG0010-python-migration/P1-dispatch-context-analyst.md（analyst 的派发指引——评审约束来源）
- {project_root}/docs/reviews/agate-python-migration-analysis-20260814.md（定稿分析报告）
- {project_root}/agate/scripts/（按需核实脚本清单/调用关系）

### 产出要求
P1-review.md 必须含：
- Header（phase: P1 / task_id: TAG0010-python-migration / type: review / parent: P1-requirements.md / trace_id: TAG0010-P1-20260814 / status: approved|rejected|needs-revision / agent: requirements-review）
- BDD 评审（逐条：判定 + 覆盖维度标注）
- 隐含需求覆盖（逐维度：覆盖/遗漏）
- 裁剪评审（risk_level / phases / capability_requirements）
- 影响面映射表核查结论（表 A-E 是否全量、有无漏网脚本/文档/锚点）
- P1 纯净性检查
- 总体结论（approved / rejected / needs-revision + 理由）
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
4. git add {AGATE_WORKSPACE}/tasks/{Txxx}/（含 .state.yaml + 产出文件，若 .gitignore 忽略需 git add -f）
   ⚠️ 此时 .state.yaml 的 phase 保持 P1，不要提前写 P2——phase = 本 commit 的产出阶段
5. git commit -m "wf({Txxx}-P1): {摘要}"（phase=P1，P1 产出含 P1-requirements.md + P1-review.md）
6. P1 commit 完成后进入 P2：**phase 推进 P2 随 P2 产出 commit 一起**（P2-design.md + P2-review.md 就绪后），不是单独 phase commit

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

`risk_level`/`phases`/`packages`/`domains` 写在文件头 **frontmatter**（`---` 分隔块），不写正文。
**可直接复制的完整样例**：
```yaml
---
phase: P1
task_id: TAG0001           # 替换为实际任务编号
type: problems
parent: P0-brief.md
trace_id: T001-P1-20260101 # {task_id}-P1-{YYYYMMDD}
status: draft
created: 2026-01-01
agent: analyst
# ── v2.0 机器字段 ──
risk_level: low             # low / medium / high，必填
phases: [P1, P4, P5, P6, P8]   # list of P\d+，必填
packages: [pkg-a]           # list，必填
domains: [backend, frontend]  # list，必填
# 可选字段：override / implicit_coupling / coupling_checklist / internal_only /
# internal_only_reason / 跳过风险 / design_trivial / follows_existing_pattern
# ── v2.0 refactor 任务类型声明（可选，缺省 = 功能任务）──
# change_type: refactor   # 当前仅支持 refactor；枚举非法值由 frontmatter schema 拦截
# ── v2.0 标记"已解决/已确认"状态（可选，仅标记存在时写）──
# need_confirm_resolved: []   # list[str]：已解决的 NEED_CONFIRM 项描述（逐条匹配正文）
# suggest_resolved: []        # list[str]：已采纳的 SUGGEST 项描述
# scope_resolved: []          # list[str]：已解决的 SCOPE+ 项描述
---
```

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
- 环境：Linux；python3 3.12.3 + pyyaml 6.0.3 + ruff 0.16.3；bats 1.10.0
- worktree 根：/home/kity/oclab/agate/.worktrees/agate-TAG0010（改造对象）；~/.agate = 稳定版 v0.45.0（禁止改动）
- 脚本清单：agate/scripts/ 下 30 个 .sh + 18 个 .py（check-gate.sh 488 行 + pre-commit-gate.sh 404 行最重）
- 测试基线：733 bats 全绿 + consistency 0 ERROR（--strict）
</objective_info>
