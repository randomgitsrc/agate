> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。

---
phase: P7
generated_by: agate-inject-card.sh + 主 Agent
task_id: TAG0009
role: consistency-reviewer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

对照 P1-P6 产出做跨文件一致性审查，产出 `P7-consistency.md`（无 BLOCKER / DEVIATION-CRITICAL，DESIGN_GAP 全部 REVIEWED 配对）。

### 约束

- **检查清单**（consistency-reviewer 角色）：
  1. **DESIGN_GAP 配对**：P4-implementation.md §4 声明 1 个 [DESIGN_GAP]（install-hook.bats Linux 分支用 readlink 替代 `[[ -L ]]`）——P7 必须转抄 + `[DESIGN_GAP_REVIEWED:]` 配对（P4-review 已批准该决策）
  2. **SCOPE+ 闭环**：P1 有 scope_resolved（产品脚本 python3 根治另立 TAG0010+）；P2-design [SCOPE+] pre-push-hook L11 归 BDD-8 同类闭环——P7 确认 P1 scope_resolved 覆盖 + P2 SCOPE+ 处理
  3. **跨文件一致性**（引用具体锚点）：
     - P1 29 BDD ↔ P6 29 验收结果数量匹配 + 编号对齐
     - P2 packages [agate-tests, agate-scripts, ci-workflow] ↔ P4 实际改动文件归属
     - P4 实现 ↔ P2 §2.1-2.9 方案吻合（扫描器/helper/shim/bc→awk/CI/批量修）
     - P2 gate_commands ↔ P5 执行结果（4 命令全绿）
     - 扫描器模式集（P2 §2.1）↔ 实际 check-platform-assumptions.sh ↔ P6 验收 ↔ BDD-8 零命中
  4. **未决项清零**：P1 无 [NEED_CONFIRM]；P6 无 [BLOCKER]/[DEVIATION-CRITICAL]
  5. **SELF-GATE 一致性**：本任务是 agate 协议本体相关（新增脚本 + 改 product script + CI + 测试）——额外检查扫描器/helper 与 P2 设计的一致性
- **frontmatter 计数**：blocker_count / deviation_count / deviation_critical_count / design_gap_count / design_gap_reviewed_count 写入文件头（本任务预期 0/0/0/1/1）
- **格式约束**：约束节避免行首 `- PASS`/`- FAIL`。

### 上游关联

- `P1-requirements.md`（29 BDD + scope_resolved）
- `P2-design.md`（packages / 方案 / gate_commands + [SCOPE+]）
- `P4-implementation.md`（DESIGN_GAP 声明 / 改动清单）
- `P6-acceptance.md`（验收结果）
- `P5-test-results/`（验证结果）

### 输入文件

- `agate-workspace/tasks/TAG0009-tests-platform-neutral/P1-requirements.md`
- `agate-workspace/tasks/TAG0009-tests-platform-neutral/P2-design.md`
- `agate-workspace/tasks/TAG0009-tests-platform-neutral/P4-implementation.md`
- `agate-workspace/tasks/TAG0009-tests-platform-neutral/P4-review.md`
- `agate-workspace/tasks/TAG0009-tests-platform-neutral/P6-acceptance.md`
- `agate-workspace/tasks/TAG0009-tests-platform-neutral/P5-test-results/unit.md`
- 按需核验实际改动文件：`agate/scripts/check-platform-assumptions.sh`、`agate/scripts/agate-extract-context.sh`、`agate/scripts/check-protocol-consistency.py`、`agate/tests/helpers/fixtures.bash`、`.github/workflows/protocol-tests.yml`
- `{agate_root}/assets/execution-roles/consistency-reviewer.md`（角色定义）
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
4. 预跑 check-gate.sh P7
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
check-gate.sh P7 $TASK_DIR
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

P7 是输入文件数量限制的例外，不拆分。原因：
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
- 环境状态：worktree `/home/kity/oclab/agate/.worktrees/agate-TAG0005-0009`；TAG0009 P1-P6 已 commit
- P1: 29 BDD；P2: packages 3 项；P3: 29 用例；P4: 7 类文件改动，1 个 [DESIGN_GAP]（readlink，P4-review 批准）；P5: 4 命令全绿；P6: 29/29 PASS
- 本任务含协议本体相关改动（新增扫描器脚本 + 改 product script + CI）——SELF-GATE 一致性检查
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
