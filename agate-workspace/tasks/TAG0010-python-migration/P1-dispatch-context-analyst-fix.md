---
phase: P1
generated_by: agate-inject-card.sh + 主 Agent
task_id: TAG0010-python-migration
role: analyst
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）
> 本文件是**修复轮（incremental）**派发指引——复用上轮 dispatch-context 的约束（P1-dispatch-context-analyst.md 仍在生效），本文件只给修复目标。不要重写完整目标/约束/上游关联，引用上轮文件。

### 修复目标（requirements-review 判定 needs-revision，3 项 must-revise）
在 {AGATE_WORKSPACE}/tasks/TAG0010-python-migration/P1-requirements.md 上修订以下 3 项，**其余内容不动**（评审已核查通过的部分：表 A/C/D/E、隐含需求五维度、裁剪三态、P1 纯净性）：

1. **表 B 系统性低估/漏列**（评审 §4 表 B 逐文档实测数据）：以评审提供的逐文档实测为准全面更新表 B。关键差距：
   - dispatch-protocol.md：实测 10 脚本/22 次（原表 5/7）——补 check-p6-format(1)、check-state-transition(2)、agate-inject-card(3)、agate-archive-stale-outputs(1)、agate-retreat-to(1)；修正 check-gate 3→6、check-p6-provenance 1→4
   - WORKFLOW.md：实测 12 脚本/21 次（原表 4/5）——补 check-scope-resolved、check-state-transition、check-changelog、check-state-yaml、check-pruning(2)、check-retrospective、agate-workspace-resolve、pre-commit-gate；修正 check-gate 2→7、check-p6-provenance 1→3、check-p6-evidence 1→2
   - state-machine.md：修正 check-gate 3→5、check-tdd-red 4→6、check-p6-provenance 1→2；补 check-state-transition(2)
   - SETUP.md：修正 install-hook 2→3、agate-summary 2→4；补 agate-next-card(1)
   - UPGRADING.md：修正 install-hook 1→3；补 check-gate(3)、check-p6-evidence(1)、check-debt(1)、pre-commit-gate(1)
   - LIMITATIONS.md：修正 check-p6-provenance 1→3；补 check-gate(3)、check-p6-evidence(1)、check-pruning(1)
   - orchestrator-template.md：补 check-gate(1)、agate-inject-card(1)
   - assets/templates/task-files.md：补 check-p6-provenance(1)、check-scope-resolved(1)
   - assets/templates/handoff-template.md：补 agate-workspace-resolve(1)
   - phase-cards/P6-acceptance.md：p6-format 修正 1→5
   - assets/templates/tech-debt-template.md：check-debt 修正 2→3
   - git-integration.md（无 scripts/ 前缀纯文字提及）与 scripts/README.md、CI 定性描述维持不构成问题
   - 更新后表 B 标注"迁移后目标"列时，注意保持与表 C 命名一致（同名换后缀或保留薄壳）

2. **BDD-3 ruff 不可满足**（评审 §1）：现有 18 个 py 默认规则集 70 个错误（UP032×35 / BLE001×9 / PLW1510×6 为主，ci-gate-backstop.py 14、agate-debt-check.py 14、agate-frontmatter-check.py 11、agate-state-yaml-check.py 7）。
   - **主 Agent 决策（已确认方向，写死进 BDD-3）**：ruff 检查范围 = **全部 `agate/scripts/*.py`（既有 18 个 + 迁移新增）**，与 shellcheck 扫全部 *.sh 的"外部客观 gate 覆盖全代码"纪律一致；规则集选择（select 子集）由 P2 设计交付（pyproject.toml），目标是让既有 py 在选定规则集下零违规。BDD-3 改为：When 运行 `ruff check`（按 P2 交付的 pyproject.toml 规则集，target-version py38）扫 `agate/scripts/*.py`，Then exit 0 无 error。
   - 同时把"pyproject.toml 规则集是 P2 交付物，须让既有 18 个 py 在选定规则集下可过"写入隐含需求（§2 兼容维度或边界维度），明确"既有 py 不改功能但可加注释/极小调整以满足规则集"的边界——如规则集选完后仍有既有 py 违规，允许最小调整（不改变行为），但 P1 只声明这个边界，不列具体调整。

3. **install-hook.sh 去留 + BDD-4/BDD-6 澄清**（评审 §4 缺陷 2、观察项 2）：
   - **主 Agent 决策（已确认方向）**：install-hook.sh 一并 py 化（→ install-hook.py，安装器本身不是 hook 入口，无 shebang 解析硬约束）；保留 sh 薄壳的**只有 3 个 hook 入口**（pre-commit-gate.sh / commit-msg-self-gate.sh / pre-push-gate.sh）。BDD-4 的 Then 明确为"受扫 .sh 文件集合与 3 个保留薄壳一致"；表 C 同步点 3 的 GATE_SCRIPT_EXEMPT 调整说明相应更新（install-hook.sh 条目随 py 化移除）。
   - **BDD-6 前置验证**：明确"P2 须先行对既有 18 个 py 跑扩展后的扫描器确认洁净度（或列出预期违规并规划处理）"作为 BDD-6 的前置条件，写入 BDD-6 或 §2.6。

### 上游关联
- 上轮 analyst 产出：P1-requirements.md（10 BDD + 表 A-E）
- requirements-review 评审：P1-review.md（status: needs-revision，评审 §4 含表 B 逐文档实测数据——本修复轮的直接输入）

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0010-python-migration/P1-requirements.md（被修订对象）
- {AGATE_WORKSPACE}/tasks/TAG0010-python-migration/P1-review.md（评审结论——修复依据）
- {AGATE_WORKSPACE}/tasks/TAG0010-python-migration/P1-dispatch-context-analyst.md（上轮派发指引，约束继续生效）
- {AGATE_WORKSPACE}/tasks/TAG0010-python-migration/P0-brief.md（任务简报与风险声明）
- {project_root}/docs/reviews/agate-python-migration-analysis-20260814.md（定稿分析报告）

### 产出要求
修订 P1-requirements.md（仅 3 项 must-revise 相关处），完成后保持：
- frontmatter 不变（risk_level: high / phases 全 / packages / domains / change_type: refactor）
- 10 条 BDD 编号连续（BDD-1..10），修订处不改变已核查通过条目的语义
- 无 [NEED_CONFIRM]（保持 [NO_NEED_CONFIRM]；主 Agent 已决策项不再标 NEED_CONFIRM）
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
- 评审实测基线：ruff 默认规则集对现有 18 个 py 报 70 错误（UP032×35 / BLE001×9 / PLW1510×6）；bats 机械调用面实测 30 文件/379 处直接 run
- 环境：Linux；python3 3.12.3 + pyyaml 6.0.3 + ruff 0.16.3；bats 1.10.0
- worktree 根：/home/kity/oclab/agate/.worktrees/agate-TAG0010（改造对象）；~/.agate = 稳定版 v0.45.0（禁止改动）
</objective_info>
