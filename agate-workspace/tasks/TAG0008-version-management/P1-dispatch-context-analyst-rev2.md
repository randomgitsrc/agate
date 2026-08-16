> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。

---
phase: P1
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0008
role: analyst
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
修复轮（rev2）：按 P1-review.md 的评审意见修订 P1-requirements.md，消除全部 needs-revision 项，使后续 requirements-review 可转 approved。

### 约束
1. **增量模式**：上轮目标/约束/上游关联/输入文件全部复用 P1-dispatch-context-analyst.md（rev1），本文件只列修复项。逐条落实：
   - 修订 1（BDD-28 legacy 回退机制语义）：Then 显式定义"`~/.agate` 本身即软链时直接解析软链目标为 AGATE_ROOT"的兜底规则（或等价的无 current/latest 场景解析规则），消除 P4 实现歧义。注意不要破坏 BDD 二值判定。
   - 修订 2（I-8 打包失败路径无 BDD）：补 1 条 BDD 覆盖 pack-offline 失败路径（目标版本 tag 不存在 / pip download 网络失败 / 目标平台 wheel 缺失），确保 I-8 后半句在 P6 可验收。
   - 修订 3（BDD-23 Then 双可选项）：收敛为单一可测信号（如"输出平台不匹配警告（须含 platform 字段值）且 exit 码非 0"，或"输出警告 + 交互确认后继续"择一固定）。
   - 修订 4（I-1 空文件场景）：BDD-13 Given 补充空文件变体，或注明空文件归入"非法格式"统一处理，确保 I-1 三要素（非法格式/空文件/未知工具前缀）全验收。
   - 修订 5（I-11 引用保护无 BDD）：补 1 条 BDD 或在 §5 明确"引用保护为 P2 设计约束、P6 人工核对"——卸载时项目仍引用该版本应拒绝/警告（防误删被锁版本）。
   - 影响面表 §2.1 补 3 个 AGATE_ROOT 消费脚本：agate-inject-card.py / agate-next-card.py / agate-render-dispatch-prompt.py（均含内联 `_agate_root()`，env → 脚本真实路径上溯两级；至少列"复核"：是否统一走 agate_common.resolve_agate_root）
   - 影响面表 §2.2 补 2 个 `~/.agate` 引用文档：agate/adr.md（L241 ADR-008 论据"~/.agate 软链接自动跟随升级"——v1 后变 resolve-entry 需复核）+ agate/assets/templates/project.md（"默认安装位置 ~/.agate"语义随目录化变化需复核）
   - 影响面表 §2.3 路径前缀修正：test_pre_commit_hook.py / test_commit_msg_self_gate_integration.py / test_pre_push_hook.py / test_dispatch_context_card.py 实际在 `agate/tests/integration/`（不是 unit/）
   - 影响面表 §2.3 test_agate_summary.py 表述修正：全仓无 summary 相关测试（grep `agate-summary` 于 tests/ 零命中），直接标"新增"，删"需查"含糊表述
2. 修订后 BDD 编号保持全局连续（若新增 BDD，重排后续编号并更新反模式自检、评审锚点提示）；不改 P0-brief 锁定范围。
3. 其余 rev1 约束全部保持有效（先扫描后定义、范围锁定、Python 路线、向后兼容、v2 边界、双工作区只读扫描、不掺方案、frontmatter 必填）。
4. 修订完成后自检：所有评审修订项已落实、BDD 编号连续、无 [NEED_CONFIRM]、无 GAP。

### 上游关联
- 上轮 analyst 产出 P1-requirements.md（356 行，29 BDD）
- requirements-review 评审 P1-review.md status=needs-revision（5 处修订 + 影响面表 4 处缺口，全文见输入文件）

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0008-version-management/P1-review.md（评审意见——本次修复目标）
- {AGATE_WORKSPACE}/tasks/TAG0008-version-management/P1-requirements.md（待修订对象）
- {AGATE_WORKSPACE}/tasks/TAG0008-version-management/P0-brief.md（范围来源）
- /home/kity/oclab/agate/.worktrees/agate-TAG0008/AGENTS.md（项目约定）
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
3. 预跑 check-gate.py P1（exit 2，主 Agent 自判）
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

## 复杂需求编排（模式 4，条件触发）

需求复杂（多来源 / 多模块 / 无法预先拆清范围）时，P1 可先派**侦察 subagent**（模式 4 先理解后拆，见 dispatch-protocol「派发编排机制」）读全貌后再拆需求：

1. 侦察 subagent 读 P0-brief + 相关上下文，产出拆分方案（拆成哪些子需求、各子需求的输入/产出/依赖）
2. 按方案派 analyst（并行或串行）分别产出需求基线
3. 合并时定义**合并语义**（在侦察产出中声明，P7 一致性检查依赖）：
   - **BDD 全局编号**：各子需求承接的 BDD 编号全局唯一（`#### BDD-NN:`），不允许各子需求各自从 1 编号
   - **包归属去重**：每个 BDD 明确归属唯一包，跨包的共享件单独列出，不允许两个子需求各写一份

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

check-gate.py P1 → P1-review.md 存在 + status:approved + agent≠main + 含 BDD 编号锚点 → exit 2（BDD 编号格式为 `#### BDD-NN:`）；缺 P1-review.md / agent=main / 无锚点 → exit 1
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
- 环境状态：worktree 分支 feat/TAG0008-version-management；P1-review.md status=needs-revision
- 关键路径：AGATE_WORKSPACE=/home/kity/oclab/agate/.worktrees/agate-TAG0008/agate-workspace
- 查证结果：评审实查——agate-inject-card.py / agate-next-card.py / agate-render-dispatch-prompt.py 含内联 `_agate_root()`；agate/adr.md L241 有 ~/.agate 引用；tests 实际在 integration/
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
