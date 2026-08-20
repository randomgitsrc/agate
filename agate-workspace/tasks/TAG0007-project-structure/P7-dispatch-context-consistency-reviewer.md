---
phase: P7
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0007
role: consistency-reviewer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令。P7 是输入文件数量限制的例外（模式 1 单发，不拆分）。

### 目标
对照 P1-P6 全部产出做跨文件一致性审查，产出 P7-consistency.md。重点：DESIGN_GAP 配对、
CODE-MAP 核对（本任务新增的第 5 条检查项）、跨文件一致性、未决项清零。

### 约束（逐条核查，含主 Agent 已发现的一处需要你独立判断的问题）

1. **DESIGN_GAP 配对**：`P4-implementation.md` 含 2 条 `[DESIGN_GAP:]`（gate-script-both 批次）：
   - 第 1 条：`_md_field_get` 因新字段未注册 allowlist 改用本地 `_frontmatter_field`
   - 第 2 条：`{AGATE_WORKSPACE}/agents/CODE-MAP.md` 路径本地推导未复用
     `agate_common.resolve_workspace`
   两条均已在 P4-review.md（approved）中给出明确判定（第 1 条接受+补充边界说明；第 2 条判定
   非阻塞已登记 DEBT0016）。你需要在 P7-consistency.md 中**逐条转抄原始 `[DESIGN_GAP:]` 行 +
   写 `[DESIGN_GAP_REVIEWED:]` 标记**（引用 P4-review.md 的判定结论作为 REVIEWED 理由）——
   check-gate.py 只扫描 P7-consistency.md，不会去读 P4-review.md，不转抄 = gate 静默放过。

2. **【重点、需要你独立判断】CODE-MAP 核对（检查清单第 5 条，本任务自己新增的机制）**：
   主 Agent 已发现一个需要你核实并给出判断的问题：
   - `gate_p4` 的 WARNING 判定逻辑是：`(P2-skeleton.md 存在 OR agents/CODE-MAP.md 存在) AND
     "## 新增文件核对表" 不在 P4-implementation.md 文本中 → WARNING`。
   - TAG0007 自己的 `dogfood-bootstrap` 批次创建了 `{AGATE_WORKSPACE}/agents/CODE-MAP.md`
     （即 `agate-workspace/agents/CODE-MAP.md`），这意味着 OR 条件对 TAG0007 自己的 P4 commit
     也成立。
   - 但 TAG0007 自己的 `P4-implementation.md` 正文并**没有**一份真正填写的「新增文件核对表」
     （逐个新文件填骨架归属列 + CODE-MAP 处理列）——它只是在描述"这个机制该怎么实现"时，
     文字里出现了 `## 新增文件核对表` 这个字符串（作为对新增功能的说明，如"标题逐字为
     `## 新增文件核对表`"），这让 `"## 新增文件核对表" not in text` 的子串判定**被字面文本
     误判为"已满足"**（实际是自指/dogfooding 场景下的假阴性——WARNING 该触发却没触发）。
   - **请你独立核实**：① 确认这个字面匹配问题是否属实（自己读 P4-implementation.md 全文 +
     实际跑一次 `grep -c "## 新增文件核对表" P4-implementation.md` 看命中的是不是描述性文字
     而非真实表格）；② 判断 TAG0007 作为"构建 CODE-MAP 机制本身的任务"，是否应该**自我应用**
     该机制——即回填一份真正的「新增文件核对表」，逐条列出本任务实际新增的文件（
     `skeleton-template.md`、`code-map-template.md`、`agate-workspace/agents/CODE-MAP.md`、
     3 个测试文件等）+ 骨架归属判断 + CODE-MAP 处理标记；③ 若判断"不需要自我应用"（如理由是
     "本任务是元任务，机制服务于未来任务，不追溯适用于构建机制的任务自身"），需要在
     P7-consistency.md 中**显式写出这个判断 + 理由**，不能沉默略过——这正是"跨文件一致性
     必须引用具体锚点，不做裸'一致'判断"这条质量门槛要求的场景。
   - 无论你判断"需要回填"还是"不需要回填"，都请标注 `[CODE_MAP_SYNC:]`（若判定当前状态可接受）
     或 `[CODE_MAP_DRIFT:]`（若判定存在真实偏离，需要 implementer 回 P4 补一份核对表）。这是
     P7-consistency.md 需要新增的、本任务自己引入的检查产出，务必落笔。

3. **SCOPE+ 闭环**：主 Agent 已 grep 全部任务文件，未发现任何行首 `[SCOPE+]` 声明（含 P1-P6
   全部产出文件），只有 dispatch-context 模板里的通用指令文字提及这个标记格式，没有实际触发。
   判定：SCOPE+ 闭环天然满足（无 SCOPE+ 需要闭环），仍需在 P7-consistency.md 中显式写出这条
   核查结论（"已核查，无 SCOPE+ 声明，闭环天然满足"），不能空白。

4. **跨文件一致性**：
   - P1 BDD 数量（11 条）与 P6 验收结果数量（11 条 PASS）匹配——已核对，需你引用具体锚点
     确认（P1-requirements.md 的 BDD-1~11 编号 vs P6-acceptance.md 的 11 条 PASS 行）
   - P2 packages（`[phase-cards, execution-roles, templates, scripts]`）与 P8 release 的 bump
     范围一致——**P8 尚未产出**，本项暂不适用，在报告中注明"待 P8 阶段核对，本轮不适用"，不要
     编造 P8 数据
   - P4 实现路径与 P2 方案设计吻合——核对 P4-implementation.md 的 4 批次改动文件清单是否与
     P2-design.md §1.1「改什么」表逐条对应（文件路径、关联 BDD 编号）

5. **未决项清零**：已核查 P1-requirements.md 全文（`[NO_NEED_CONFIRM]`）+ P4/P6 无残留
   `[NEED_CONFIRM]`/`[BLOCKER]`/`[DEVIATION-CRITICAL]`，需你独立复核一次（grep 全部任务产出
   文件，不只信主 Agent 的转述）。

### 上游关联
P1-requirements.md（approved，11 BDD）→ P2-design.md（approved，4 决策组）→
P3-test-cases.md（17 用例）→ P4-implementation.md（approved，2 DESIGN_GAP）→
P5-test-results/unit.md（4 命令全绿）→ P6-acceptance.md（11/11 PASS）。

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0007-project-structure/P1-requirements.md
- {AGATE_WORKSPACE}/tasks/TAG0007-project-structure/P2-design.md
- {AGATE_WORKSPACE}/tasks/TAG0007-project-structure/P4-implementation.md
- {AGATE_WORKSPACE}/tasks/TAG0007-project-structure/P4-review.md（DESIGN_GAP 判定结论来源）
- {AGATE_WORKSPACE}/tasks/TAG0007-project-structure/P6-acceptance.md
- /home/kity/oclab/agate/.worktrees/agate-TAG0007/agate/scripts/check-gate.py:658-717
  （`gate_p4` 函数，CODE-MAP OR 条件 + 「## 新增文件核对表」子串判定逻辑）
- /home/kity/oclab/agate/.worktrees/agate-TAG0007/agate-workspace/agents/CODE-MAP.md
  （dogfooding 实例）
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

<objective_info>
- P4-implementation.md 含 2 条 `[DESIGN_GAP:]`（第 166、168 行附近），P4-review.md（approved）
  已给出判定结论
- `grep -c "## 新增文件核对表" P4-implementation.md` 命中 1 处，但该命中是描述性文字（"标题
  逐字为 `## 新增文件核对表`"），不是真实填写的核对表——主 Agent 已核实这一点，交给你独立复核
  并给出正式判断
- `{AGATE_WORKSPACE}/agents/CODE-MAP.md`（即 `agate-workspace/agents/CODE-MAP.md`）确认存在
- 全仓 grep 未发现任何 `[SCOPE+]` 实际声明（仅 dispatch-context 模板文字提及格式）
- P1 BDD 数 = 11，P6 PASS 数 = 11（frontmatter pass: 11, fail: 0）
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
