> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。

---
phase: P7
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0008
role: consistency-reviewer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
P7 一致性检查：跨 P1-P6 产出做交叉核对，产出 P7-consistency.md（含 DESIGN_GAP 配对 + REVIEWED 标记 + 跨文件检查项 + frontmatter 机器计数）。

### 约束
1. **DESIGN_GAP 配对（gate 硬校验）**：P4 声明了 **8 条 DESIGN_GAP**（见下方完整清单），P7 必须逐条转抄原始标记行 + 配 `[DESIGN_GAP_REVIEWED: 已确认/已打回 P2]` 标记行。P2 plan-eng-review 已评估 3 条 resolve-chain DESIGN_GAP 可接受；install 4 条 + offline 1 条由你独立审查。未配对 → gate exit 1。
2. **SCOPE+ 闭环**：P1-requirements.md 检查有无 [SCOPE_RESOLVED]（本任务 P4 无实际 SCOPE+，P4-implementation-install.md 的声明已修正为非行首格式）。
3. **跨文件一致性**（实质锚点，含源文件节名引用）：
   - P1 BDD 数（31）vs P6 验收结果数（PASS+FAIL ≥31）vs P3 测试用例数
   - P2 packages（[agate]）vs P8 bump 范围（单包）
   - P2 方案 vs P4 实现路径吻合（agate-resolve.py / resolve-entry.py / agate-install.py / agate-pack-offline.py / install-offline.py 是否按方案落地）
   - P2 gate_commands vs P5 执行结果（4 条命令全部执行）
   - 影响面表（P1 §2）vs P4 改动清单（2.1 脚本层 / 2.2 文档层 / 2.3 测试层）——**注意：P4 只做了代码实现，文档层改动（README/SETUP/UPGRADING 等）尚未落地，这是 P8 发布节的事，需在 P7 明确标注**（不阻塞，因为文档联动在本任务按 P8 步骤处理）
4. **未决项清零**：P1 无残留行首 [NEED_CONFIRM]（[NO_NEED_CONFIRM] 已声明）、无 [BLOCKER]、无 [DEVIATION-CRITICAL]。
5. **frontmatter 机器计数**：blocker_count / deviation_count / deviation_critical_count / design_gap_count / design_gap_reviewed_count 必填。
6. **双工作区纪律**：只读审查，不修改任何文件（除 P7-consistency.md 产出）。
7. **结论引用锚点**：每条检查项给结论 + 证据（文件/节/行号），不写裸 "一致"。

### 上游关联
- P1 基线：31 BDD + 影响面表 + [NO_NEED_CONFIRM]
- P2 设计：2 候选方案 + static-batch 3 批 + gate_commands
- P3 测试：6 测试文件 31+ 用例，全部红灯后转绿
- P4 实现：3 批代码 + 8 DESIGN_GAP + P4 评审（review/cso approved）
- P5 验证：全量 823 passed + 单测 29 + consistency 0 ERROR
- P6 验收：31/31 PASS + P6-evidence/ 证据

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0008-version-management/P1-requirements.md
- {AGATE_WORKSPACE}/tasks/TAG0008-version-management/P2-design.md
- {AGATE_WORKSPACE}/tasks/TAG0008-version-management/P3-test-cases.md + 3 个分批文件
- {AGATE_WORKSPACE}/tasks/TAG0008-version-management/P4-implementation.md / P4-implementation-install.md / P4-implementation-offline.md（含 DESIGN_GAP）
- {AGATE_WORKSPACE}/tasks/TAG0008-version-management/P4-review.md / P4-review-eng.md / P4-review-cso.md
- {AGATE_WORKSPACE}/tasks/TAG0008-version-management/P5-test-results/unit.md
- {AGATE_WORKSPACE}/tasks/TAG0008-version-management/P6-acceptance.md
- /home/kity/oclab/agate/.worktrees/agate-TAG0008/AGENTS.md（项目约定）

### P4 DESIGN_GAP 完整清单（8 条，供转抄配对）
1. P4-implementation.md:41 — legacy 软链兜底仅用于 resolve/summary（resolve-entry 用脚本路径上溯 + .agate-root）
2. P4-implementation.md:43 — 3 内联脚本归口保留 import 失败内联兜底
3. P4-implementation.md:45 — 3 hook 薄壳改用 ENTRY_ROOT 防 env 泄漏
4. P4-implementation-install.md:60 — repo URL 默认值（AGATE_REPO_URL 未设 → canonical URL）
5. P4-implementation-install.md:61 — 引用保护扫描限流参数（深度 ≤4 + 跳过隐藏 + mtime 365 天）
6. P4-implementation-install.md:62 — worktree remove 失败兜底（--force + rmtree + prune）
7. P4-implementation-install.md:63 — 最新发布 tag 确定方法（git tag --sort=-version:refname 过滤 vX.Y.Z）
8. P4-implementation-offline.md:48 — sha256 双实现漂移风险（pack/install 两侧各自实现，未共享 agate_common）
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
- 环境状态：worktree 分支 feat/TAG0008-version-management；P6 已过（31/31 PASS）
- 关键路径：AGATE_WORKSPACE=/home/kity/oclab/agate/.worktrees/agate-TAG0008/agate-workspace/tasks/TAG0008-version-management/
- 查证结果：8 条 DESIGN_GAP 已 grep 确认（3 resolve + 4 install + 1 offline）；P6 31 条 PASS 已确认
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
