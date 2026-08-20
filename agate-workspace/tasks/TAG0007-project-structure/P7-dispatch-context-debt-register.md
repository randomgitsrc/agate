---
phase: P7
generated_by: 主 Agent（小型登记任务）
task_id: TAG0007
role: consistency-reviewer
---

<dispatch_guide>
### 背景
P7 一致性检查（`P7-consistency.md`，approved）第 2 节「CODE-MAP 核对」独立确认了一处真实发现：
`check-gate.py` 的 `gate_p4` 函数用子串判定 `"## 新增文件核对表" not in text` 检查
P4-implementation.md 是否已补充新增文件核对表——这个判定在**自指/dogfooding 场景**下存在假
阴性：TAG0007 自己的 P4-implementation.md 里出现了"## 新增文件核对表"这个字符串，但只是描述
"给协议卡片新增了一个标题叫这个的小节"的**说明性文字**，不是 TAG0007 自己为自己新增的文件
（`skeleton-template.md`/`code-map-template.md`/`agate-workspace/agents/CODE-MAP.md`/3 个测试
文件）真正填写的核对表。WARNING 该触发却未触发。

P7 给出两种处理路径（均不要求打回已 approved 的 P4/P6）：① 补一份真正的核对表附录 ② 登记技术债。
主 Agent 已决定采用②（与 DEBT0016 同等处理方式，避免重开已完成阶段，同时把根因（gate_p4 判定
逻辑健壮性）和自我应用缺口都记录在案）。

### 目标
登记一条新的 DEBT 条目（编号取当前最大编号+1）到 `{AGATE_WORKSPACE}/debt/tech-debt.md`，内容
覆盖两点：① `gate_p4` 的子串判定在自指场景下的假阴性风险（根因：应改用整行匹配
`^## 新增文件核对表\s*$` 而非子串包含）② TAG0007 自身的 P4-implementation.md 未对自己新增的
文件使用标准 `[CODE_MAP_UPDATED]`/`[CODE_MAP_EXEMPT]` 标记（自我应用缺口）。

### 约束
- 先读 `{AGATE_WORKSPACE}/debt/tech-debt.md` 确认当前最大 DEBT 编号，新条目编号 = 最大+1
- 严格按 `assets/templates/tech-debt-template.md` 字段表登记（id/category/title/status/
  priority/evidence/impact/recommendation/closure_criteria/source/created_at/task_id 全部
  必填字段）
- `category: technical`，`priority: low`（影响仅限一处 WARNING 分支的假阴性，不阻断任何
  commit，性质与 DEBT0016 同级）
- `evidence` 至少引用：`agate/scripts/check-gate.py`（`gate_p4` 函数子串判定行）+
  `agate-workspace/tasks/TAG0007-project-structure/P7-consistency.md`（第2节完整论证，本次
  发现的原始出处）
- `source: review`（P7 一致性检查中发现）
- `task_id: TAG0007`
- `closure_criteria` 至少两条：① `gate_p4` 改用整行匹配（或等价的健壮判定方式）② TAG0007（或
  后续任一涉及 CODE-MAP 机制自指场景的任务）补齐自己新增文件的标准 CODE-MAP 标记，或确认无需
  补齐的替代方案
- 只追加新增这一条 DEBT，不改动 tech-debt.md 已有的其他条目（含 DEBT0016）

### 输入文件
- {AGATE_WORKSPACE}/debt/tech-debt.md（确认最大编号 + DEBT0016 的登记格式作为参照样式）
- {AGATE_WORKSPACE}/tasks/TAG0007-project-structure/P7-consistency.md（第2节完整论证，登记
  内容的权威来源）
- /home/kity/oclab/agate/.worktrees/agate-TAG0007/agate/assets/templates/tech-debt-template.md
  （字段表权威定义）

### 验证
登记后跑 `python3 agate/scripts/agate-debt-check.py`（`FILE={AGATE_WORKSPACE}/debt/tech-debt.md`
环境变量方式调用）确认 schema 校验 exit 0。
</dispatch_guide>

<!-- AGATE_CARD_START -->
## 当前阶段卡片：P7

路径：phase-cards/P7-consistency.md
---
# P7 — 一致性检查

> 当前状态：[首次 / 重试 #N / 裁剪跳阶]
> 裁剪跳阶 → 确认 P1 phases 不含 P7 + 源文件数 ≤5 + 无 implicit_coupling + 有 coupling_checklist（须列出至少 2 个已检查的耦合点，空清单不合规）→ 跳过，读 P8 卡片
> ⑨ P7 subagent 化

## 如果是首次进入本阶段

1. 主 Agent 派发 consistency-reviewer subagent 执行交叉检查
   1.1 写 P7-dispatch-context-consistency-reviewer.md（派发指引：目标/约束/上游关联/输入文件 + 客观查证信息）
2. 对照 P1-P6 产出做跨文件一致性审查
3. 产出 P7-consistency.md
4. 预跑 check-gate.py P7
5. git add {AGATE_WORKSPACE}/tasks/{Txxx}/（含 .state.yaml + 产出文件，若 .gitignore 忽略需 git add -f）
   ⚠️ 此时 .state.yaml 的 phase 保持 P7，不要提前写 P8——phase = 本 commit 的产出阶段
6. git commit -m "wf({Txxx}-P7): {摘要}"（phase=P7，P7 产出含 P7-consistency.md）
7. P7 commit 完成后进入 P8：**phase 推进 P8 随 P8 产出 commit 一起**（P8-release.md 就绪后），不是单独 phase commit

## 如果是重试

→ 读 agate/rules/state-transitions.md 确认 retry 上限（P7 MAX=2）

## 前置条件

- [ ] P1-P6 全部产出文件就绪

## 执行方式

consistency-reviewer subagent 执行。检查清单：

1. **DESIGN_GAP 配对**：P4-implementation.md 中的 DESIGN_GAP 声明 → 必须在 P7-consistency.md 中逐条转抄 + 配 REVIEWED 标记。未配对 → gate 不通过
2. **SCOPE+ 闭环**：P1-requirements.md 有 [SCOPE_RESOLVED] 标记，确认所有 SCOPE+ 增补已纳入基线
3. **跨文件一致性**：P2 声明的 packages 与 P8 release 的 bump 范围一致？P1 的 BDD 和 P6 的验收结果数量匹配？P4 的实现路径和 P2 的方案设计吻合？
4. **未决项清零**：P1-requirements.md 无残留行首 [NEED_CONFIRM]（P6 不再有 NEED_CONFIRM）、[BLOCKER]、[DEVIATION-CRITICAL]

## 实质锚点要求（N3⑨）

| gate 断言 | 实质锚点（P7 产出须包含） |
|-----------|--------------------------|
| BLOCKER=0 | DESIGN_GAP 配对项 + REVIEWED 标记 |
| CRITICAL=0 | 跨文件检查项 + 源文件节名 |
| SCOPE+ 闭环 | 条目 + SCOPE_RESOLVED |

gate 脚本校验说明：
- DESIGN_GAP_REVIEWED：P4 声明的每条 DESIGN_GAP 在 P7 产出中须有对应行含 `DESIGN_GAP_REVIEWED`
- 跨文件引用关键词：P7 产出中须含源文件节名（如 `P2§packages`、`P4§impl-path`），否则 WARNING

## 产出规格

- P7-consistency.md：一致性审查结论
- 逐条检查结果，无 [BLOCKER] 标记

`blocker_count`/`deviation_count`/`deviation_critical_count`/`design_gap_count`/
`design_gap_reviewed_count` 写在文件头 **frontmatter**（`---` 分隔块），不写正文；正文
`[BLOCKER]`/`[DEVIATION-CRITICAL]`/`[DESIGN_GAP]`/`[DESIGN_GAP_REVIEWED]` 散文标记保留为
人类痕迹（不迁移），gate 判定改读 frontmatter 结构化计数。**可直接复制的完整样例**：
```yaml
---
phase: P7
task_id: TAG0001           # 替换为实际任务编号
type: consistency
parent: P2-design.md
trace_id: T001-P7-20260101 # {task_id}-P7-{YYYYMMDD}
status: draft
created: 2026-01-01
agent: consistency-reviewer
# ── v2.0 机器计数 ──
blocker_count: 0                  # int ≥0
deviation_count: 0                # int ≥0
deviation_critical_count: 0       # int ≥0
design_gap_count: 0                # int ≥0
design_gap_reviewed_count: 0       # int ≥0
---
```

## gate 规则

```bash
check-gate.py P7 $TASK_DIR
```

- [BLOCKER] 存在 → exit 1
- [DEVIATION-CRITICAL] 存在 → exit 1
- DESIGN_GAP 未配对（P4 有但 P7 无 REVIEWED）→ exit 1
- 含 DESIGN_GAP_REVIEWED 但缺跨文件引用关键词 → WARNING（不改变 exit code）
- 全部通过 → exit 0

BLOCKER → consistency-reviewer 修改 → 再验 gate → … → 通过（⑩迭代循环，review 和 gate 重试共享 retry 预算）

## 推进条件（全部满足才写 phase: P8）

- [ ] P7-consistency.md 存在
- [ ] 无 [BLOCKER] / [DEVIATION-CRITICAL]
- [ ] DESIGN_GAP 全部 REVIEWED 配对
- [ ] SCOPE+ 闭环（P1 有 [SCOPE_RESOLVED]）

## P7 输入文件数量

P7 是输入文件数量限制的例外（模式 1 单发 + 输入数量豁免特例，见 dispatch-protocol「派发编排机制」全阶段适用表），不拆分。原因：
1. 跨文件一致性比较需要全部源文件同时可见
2. 角色文件（consistency-reviewer）已列出所需输入清单
3. dispatch-context 为 subagent 提供摘要，无需逐文件全文注入

## 常见错误

1. **漏转抄 P4 的 DESIGN_GAP**：P4 implementer 声明了实现偏差但 P7 没转抄 → gate 拦截
2. **一致性检查只看标题不对内容**：P1 BDD 数 = 15，P6 PASS 数 = 15 → 数量对，但 BDD-8 的内容在 P6 里被映射到错误的验收结果
3. **裸 'BLOCKER=0' 不引用锚点**：未做实质交叉检查，只写 '一致' → gate WARNING 提醒

gate 不过 ≠ 你失败了。红灯指向工作/设计的问题，不指向你。正确动作是诊断→退回/重试/PAUSED，不是修改产出让它变绿。

## 下游影响

- P8 发布前最后一道质量门——P7 通过后进入机械发布步骤

> 完成 → 读 phase-cards/P8-release.md
<!-- AGATE_CARD_END -->

## 返回给我
只返回两行：
  1. 新登记的 DEBT 编号
  2. `agate-debt-check.py` 复跑结果（exit 0 确认）
