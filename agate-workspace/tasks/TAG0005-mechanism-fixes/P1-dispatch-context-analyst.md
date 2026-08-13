> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。

---
phase: P1
generated_by: agate-inject-card.sh + 主 Agent
task_id: TAG0005
role: analyst
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

**修订轮（P1-review 判定 needs-revision，两个阻塞项）**：修订 `P1-requirements.md`，处理 requirements-review 的两个阻塞项。修订后 BDD 编号连续、可二值判定、同类扫描证据与全仓实测一致。

### 约束

- **修订范围（增量模式，引用上轮文件，不重写完整目标/约束）**：
  - 上轮产出：`agate-workspace/tasks/TAG0005-mechanism-fixes/P1-requirements.md`
  - 上轮 dispatch-context：`agate-workspace/tasks/TAG0005-mechanism-fixes/P1-dispatch-context-analyst.md`（复用其约束，以下只列本轮的增量）
  1. **阻塞项 1（必须修订）——同类扫描证据更正 + check-debt.sh 裁定 + BDD-15 收窄**：
     - 上轮 §2 声称「rg 验证无 `>&2` 后紧接 `exit 0` 的匹配」，**与全仓实测不符**——存在 4 处字面匹配：
       - `agate/scripts/check-debt.sh:26`：`source "$SCRIPT_DIR/agate-workspace-resolve.sh" ... || { echo "GATE DEBT: 无法加载 agate-workspace-resolve.sh" >&2; exit 0; }`
       - `agate/scripts/agate-capture-env-baseline.sh:23/26/28`：`{ echo "...跳过基线捕获/跳过..." >&2; exit 0; }`（显式跳过语义）
     - **裁定要求（用户 P0-brief 明确「不能只修 roadmap 列位置」）**：
       - `check-debt.sh:26` 与 RM-AG0012② 原始缺陷**结构同构**（依赖加载失败 → stderr 报错 → exit 0 成功码）。主 Agent 已复核该脚本：`--retreat-coverage` 模式文档声明「只读 WARNING，恒 exit 0（不阻断）」，但依赖加载失败是硬失败而非有意跳过，静默 exit 0 会让回退覆盖比对被无声跳过——**同同类，纳入修复范围**。请把该实例并入 BDD（如新增 BDD 或并入 BDD-15），修法由 P2 定（建议依赖失败改 exit 2 WARNING，与 check-gate.sh 约定一致；恒 exit 0 的「有意跳过」分支保留）。
       - `agate-capture-env-baseline.sh:23/26/28` 三处为**显式跳过语义**（消息含「跳过基线捕获」，best-effort 设计，脚本注释声明「不影响 P3/P4 推进」）——**裁定非同类的有意跳过，不需修复**。在同类扫描结论中明确写出该裁定 + 理由，防止 P6 误判。
     - **BDD-15 收窄**：原 Then「全仓 scripts 同类审计无其他实例」与字面 grep 不符（4 处匹配），不可二值判定。修订为精确标准：错误路径（依赖加载失败/资源缺失等非跳过语义）exit 非零；「显式跳过」语义（消息含跳过/不影响推进声明）除外。修订后 BDD-15 的 Then 必须能让 P6 用 grep 明确判定（给出判定命令/模式）。
  2. **阻塞项 2（必须修订）——I8 引用路径已归档**：
     - I8 声称「须同步更新 docs/plans/agate-test-plan-2026-07-01.md 附录 A」——该文件已归档至 `agate-workspace/archived/plans/agate-test-plan-2026-07-01.md`（fb5b754），**不在库内实时路径**。
     - 库内实时逐脚本计数表在 `agate/tests/README.md`（已核验：L33 `agate-render-dispatch-prompt.sh = 16`，而 bats 实际 17 @test，**已存在 1 漂移**）。
     - `agate/tests/scripts/count-tests.sh` L22 提示仍指向旧路径（pre-existing 陈旧引用，非本任务引入）。
     - 修订：I8 目标改为 `agate/tests/README.md` 逐脚本计数表；可在隐含需求表或 BDD 里顺带标注 count-tests.sh 的陈旧引用为 pre-existing 已知项（不纳入本任务修复范围，避免范围蔓延）。
  2.5 **上轮其余内容为 approved 基调**（BDD-1..14 全部通过复核）——不要重写已通过部分，只修订阻塞项相关 BDD + 隐含需求表对应条目 + 同类扫描结论节。
- **格式约束**：约束节避免行首 `- PASS`/`- FAIL`（被 provenance 预判检测匹配）。改用「通过/失败」或加引号。

### 上游关联

- `P1-review.md`（评审结论，needs-revision，两个阻塞项 F1/F2）
- `P1-requirements.md`（修订对象，上一轮 analyst 产出）
- `P0-brief.md`（任务简报，已知风险含同类扫描强制要求）

### 输入文件

- `agate-workspace/tasks/TAG0005-mechanism-fixes/P1-review.md`（评审结论，阻塞项依据）
- `agate-workspace/tasks/TAG0005-mechanism-fixes/P1-requirements.md`（修订对象）
- `agate-workspace/tasks/TAG0005-mechanism-fixes/P1-dispatch-context-analyst.md`（上轮派发指引，复用）
- 按需核验：
  - `agate/scripts/check-debt.sh`（L24-30 依赖加载 + 有意跳过分支）
  - `agate/scripts/agate-capture-env-baseline.sh`（L20-29 显式跳过语义）
  - `agate/tests/README.md`（L33 逐脚本计数表）
  - `agate/tests/scripts/count-tests.sh`（L22 陈旧引用）
- `{agate_root}/assets/execution-roles/analyst.md`（角色定义）
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
- 环境状态：worktree `/home/kity/oclab/agate/.worktrees/agate-TAG0005-0009`；协议 v0.44.0 基线；714 bats 全绿
- 主 Agent 复核确认：check-debt.sh:26 依赖加载失败静默 exit 0 同同类（纳入修复）；capture-env-baseline 三处为显式跳过（非同类）
- I8 引用路径已归档，实时计数表在 agate/tests/README.md（render=16 vs 实际 17，已有 1 漂移）
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
