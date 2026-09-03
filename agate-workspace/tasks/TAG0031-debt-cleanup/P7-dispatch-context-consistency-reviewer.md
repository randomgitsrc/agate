---
phase: P7
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0031
role: consistency-reviewer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
对 P0-P6.5 全部产出做跨文件一致性审查，产出 `P7-consistency.md`。本任务不裁剪 P7（risk_level: medium，受影响脚本数 ≥5，P1 已判定不满足裁剪前提）。

### 约束
- **DESIGN_GAP 配对（硬门槛）**：`P4-implementation-version-mgmt.md:31` 有且仅有 1 条 `[DESIGN_GAP: ...]`——P2-design.md §1.3 R1 未明确说明如何在"install-offline.py 不能顶层无条件 import agate_common"约束下让 `test_offline_bundle_roundtrip.py` 的 identity 断言成立，实现采用"模块级探测 yaml 可用性折中方案"。你必须在 P7-consistency.md 里**逐字转抄**这条 DESIGN_GAP，并给出 `[DESIGN_GAP_REVIEWED: ...]` 判定（是否接受这一实现细化、理由是什么）——不接受也可以，但要写明理由，不是走过场。
- **SCOPE+ 闭环核对**：P1-requirements.md 有一条 `[BASELINE_CHANGE: ...]` + 一条 `[SCOPE_RESOLVED: ...]`（P2 阶段发现的 R1 pyyaml checksum 顺序问题回补），对照 P2-design.md `[SCOPE+]` 声明确认闭环完整（发现→回补→解决→测试覆盖，链条完整无缺口）。
- **跨文件一致性核对项**（具体到本任务）：
  1. P2 声明 `packages: [agate-scripts, agate-tests, agate-docs]` 与实际改动文件（`agate/scripts/*.py` + `agate/UPGRADING.md`/`agate/scripts/README.md` + `agate/tests/*`）是否一致
  2. P1 的 15 条 BDD 与 P6 的验收 PASS 数（15/15）是否逐条对应，不只是数量对——抽查至少 3 条核实 BDD 编号与 P6-acceptance.md 对应行的描述语义一致（不是凑数量）
  3. P4 的实现路径（三簇改动文件清单）与 P2 §4 files_to_read/§1.1 改动点表是否吻合，有无未声明的额外改动
  4. debt/tech-debt.md 的 7 条闭合 + 2 条新登记与 P1 BDD-7/14/15 的要求是否吻合
- **CODE-MAP 核对**：`agate-workspace/agents/CODE-MAP.md` 机制已采用，但本次三簇 P4 实现**无新增文件**（全部是对既有文件的修改），P4-implementation.md 已声明"无新增文件核对表可省略"——确认这一判定属实（`git log` 或 `git show` 核对 P4 commit 的文件改动类型，全部应为 M 而非 A），标 `[CODE_MAP_SYNC: 本次无新增文件，核对表义务不适用]`。
- **未决项清零核对**：确认 P1-requirements.md 无残留行首 `[NEED_CONFIRM]`（应只有 `[NO_NEED_CONFIRM]`）；P6-acceptance.md 无 `[BLOCKER]`/`[DEVIATION-CRITICAL]`。
- **禁止行首 PASS/FAIL 格式**：正文禁止 `^\s*- (PASS|FAIL)` 行首列表格式（触发 provenance 类审计的通用禁令，本阶段虽非 P6.5，但延续同一纪律）。

### 上游关联
- P6.5 judge 独立复核 passed（15/15 criteria，fresh context 无锚定，见 P6.5-judge-verdict.md）
- P4 review approved（backend 域），SELF-GATE protocol-alignment-review 全 ALIGNED
- P2-review approved（2 轮），P1-review approved（2 轮）

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0031-debt-cleanup/P0-brief.md
- {AGATE_WORKSPACE}/tasks/TAG0031-debt-cleanup/P1-requirements.md
- {AGATE_WORKSPACE}/tasks/TAG0031-debt-cleanup/P2-design.md
- {AGATE_WORKSPACE}/tasks/TAG0031-debt-cleanup/P4-implementation.md（+ 三份 -version-mgmt/-test-isolation/-gate-robustness 分文件）
- {AGATE_WORKSPACE}/tasks/TAG0031-debt-cleanup/P6-acceptance.md
- {AGATE_WORKSPACE}/tasks/TAG0031-debt-cleanup/P6.5-judge-verdict.md
- {AGATE_WORKSPACE}/debt/tech-debt.md
- {AGATE_WORKSPACE}/agents/CODE-MAP.md
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
5. **CODE-MAP 核对**：对照 `{AGATE_WORKSPACE}/agents/CODE-MAP.md` 与 P4「新增文件核对表」逐条核对，发现依赖方向偏离标 `[CODE_MAP_DRIFT:]`（WARNING 级，不阻断）；核对通过标 `[CODE_MAP_SYNC:]`

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
`design_gap_reviewed_count`/`code_map_new_files_count`/`code_map_reviewed_count` 写在文件头
**frontmatter**（`---` 分隔块），不写正文；正文
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
code_map_new_files_count: 0        # int ≥0（可选，仅骨架/CODE-MAP 机制已采用时填）
code_map_reviewed_count: 0         # int ≥0（可选，语义对应 design_gap_reviewed_count）
---
```

## gate 规则

```bash
check-gate.py P7 $TASK_DIR
```

- [BLOCKER] 存在 → exit 1
- [DEVIATION-CRITICAL] 存在 → exit 1
- DESIGN_GAP 未配对（P4 有但 P7 无 REVIEWED）→ exit 1
- CODE-MAP 未配对（code_map_reviewed_count < code_map_new_files_count，或 P4 实际标记数 > code_map_new_files_count）→ exit 1（两字段均缺失时机制未采用，跳过）
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
- 环境状态：worktree 分支 feat/TAG0031-debt-cleanup（P6.5 已 commit），工作目录 /home/kity/oclab/agateon/.worktrees/agate-TAG0031
- 关键标识：DESIGN_GAP 精确位置 P4-implementation-version-mgmt.md:31；[SCOPE_RESOLVED] 位置 P1-requirements.md「P2 阶段 [SCOPE+] 回补」节
- 查证结果：本节不预查证一致性结论——由你自行交叉核对
</objective_info>
