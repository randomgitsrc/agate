---
phase: P7
task_id: TAG0010-python-migration
type: consistency
parent: P2-design.md
trace_id: TAG0010-P7-20260815
status: approved
created: 2026-08-15
agent: consistency-reviewer
# ── v2.0 机器计数 ──
blocker_count: 0
deviation_count: 0
deviation_critical_count: 0
design_gap_count: 5
design_gap_reviewed_count: 5
---

# P7 一致性审查结论 — TAG0010（agate 产品逻辑 Python 化）

> 审查执行：consistency-reviewer subagent；时间：2026-08-15；对照 P1-P6 产出做跨文件交叉检查。
> **结论：初始发现 1 个 [BLOCKER]（SCOPE+ 未闭环），已于 2026-08-15 由主 Agent 闭环修复后复核为通过**。DESIGN_GAP 5 条全部配对 REVIEWED；P2 packages / P1 BDD / P4 实现路径跨文件一致。

## 1. DESIGN_GAP 配对（P4 §DESIGN_GAP 5 条 → P7 逐条转抄 + REVIEWED）

> 来源：`P4-implementation.md` L72 / L128 / L181 / L236 / L392（5 条，`grep -rh '\[DESIGN_GAP:'` 实测 5，与 gate R2.3 交叉核对一致）。

- [DESIGN_GAP: P2 §3.1 写 "gate-result.json（6 字段结构不变）"，但 gate-result.sh 实际写 7 字段（phase/task_id/exit_code/timestamp/output/runner/prev_commit_sha）。实现按 sh 实际结构保留 7 字段（CLI 契约"结构不变"的判定对象是 sh 现状，ci-gate-backstop 读 phase/exit_code/timestamp/prev_commit_sha 均不受影响），未按"6 字段"裁剪]
  - [DESIGN_GAP_REVIEWED: 合理——以 sh 现状（gate-result.sh 实写 7 字段）为准实现，CLI 契约判定对象一致；ci-gate-backstop 消费字段不受影响；P2 §3.1 的"6 字段"为设计笔误，实现选择正确，无行为偏离。P4§impl-path（批次 0 边界与实现说明）佐证。]
- [DESIGN_GAP: 批次 1a 的 bats 自查发现并处理一个 sh→py 语义差异——sh 命令替换 $(...) 会剥掉子进程输出尾部换行，而 Python subprocess capture 不剥。check-scope-resolved.py 的 agate-md-field-get scope_resolved 空结果时 print 仍输出 "\n"，sh 版 $(...) 收尾为空串落到正文回退判定，py 版若直接判非空会误走 frontmatter 分支（SC.4 红）。实现采用 .rstrip("\n") 等价 sh $(...) 语义；check-changelog.py 的 agate-changelog-unreleased 输出同样处理]
  - [DESIGN_GAP_REVIEWED: 合理——这是 sh `$(...)` 与 Python subprocess 的真实语义差异，实现用 `.rstrip("\n")` 等价还原 sh 行为，属忠实迁移；check-scope-resolved.py 空结果路径实测（`_scope_resolved_frontmatter` 尾部 `rstrip("\n")`）与该决策一致。P4§impl-path（批次 1a 偏离点）佐证。]
- [DESIGN_GAP: 新 py 的 usage/错误消息中脚本名后缀改 .sh → .py（如 "用法: agate-extract-context.py PHASE TASK_DIR [--write]"、"未找到 P1-dispatch-context-*.md"）——sh 版消息写的是 .sh 后缀；为与新脚本名一致而改（batch 1a check-changelog.py 同款先例）。bats 只断言 exit code 不断言消息正文，P5 可复验]
  - [DESIGN_GAP_REVIEWED: 合理——消息脚本名与新命名一致是自然选择；bats 断言不依赖消息正文（P6 全量回归 733 ok 实测佐证），无测试破坏；属展示层变更，P2 §3.2「CLI 契约不变」以 exit code / 结构契约为准，不违背。P4§impl-path（批次 1b 偏离点）佐证。]
- [DESIGN_GAP: 新 py 的渲染产物 header / usage 错误消息中脚本名后缀改 .sh → .py（"用法: agate-render-dispatch-prompt.py ..."、"本文件是 agate-render-dispatch-prompt.py 的渲染产物"、"GATE: agate-next-card.py ..."）——sh 版写 .sh 后缀；为与新脚本名一致而改（batch 1a/1b check-changelog.py / agate-extract-context.py 同款先例）。bats 只断言 exit code 与子串，不断言脚本名，P5 可复验]
  - [DESIGN_GAP_REVIEWED: 合理——与第 3 条同款先例；渲染产物 header 脚本名随新命名更新，bats 断言（exit code + 子串）不受影响；P6 回归全绿佐证。P4§impl-path（批次 1c 偏离点 + 非 DESIGN_GAP 实现说明）佐证。]
- [DESIGN_GAP: check-state-transition.py 检查 4 的提示消息保留 sh 原文「退回前须先跑：bash agate/scripts/agate-archive-stale-outputs.sh P{old} {task_dir}」——sh 版消息指向 .sh（.sh 保留、仍可跑），且 `unit/check-state-transition.bats` ST_ARCHIVE.1 断言 `[[ "$output" == *"agate-archive-stale-outputs.sh"* ]]`；改为 .py 会破坏 bats 断言。保持 CLI 契约（消息字节不变），后续随文档同步批次（表 B）一并更新]
  - [DESIGN_GAP_REVIEWED: 方向合理（保 bats 断言 + CLI 契约字节不变），但**延后修复未按承诺执行**——批次 4d 已删档 agate-archive-stale-outputs.sh，而 check-state-transition.py L170 提示消息仍指向 `bash agate/scripts/agate-archive-stale-outputs.sh`（已删文件），check-state-transition.bats L500 断言仍锁定 .sh 字串。用户按提示执行将失败。见 §4 未决项（与 [BLOCKER] 关联的非阻塞观察）。]

**DESIGN_GAP 配对统计**：P4 声明 5 条 → P7 转抄 5 条 + REVIEWED 5 条（design_gap_count=5, design_gap_reviewed_count=5）✓

## 2. SCOPE+ 闭环 —— 已解决（原 BLOCKER-1）

**检查项**：P1-requirements.md 是否有 [SCOPE_RESOLVED] 标记（P7 卡 §执行方式第 2 条）。

**初始结果**：**未闭环** → BLOCKER-1（P4 声明 4 条 [SCOPE+]、P1 无 [SCOPE_RESOLVED]、check-scope-resolved exit 1）。

**闭环修复（2026-08-15，主 Agent）**：
- P1-requirements.md 追加 `## 7. SCOPE+ 处理` 节，4 条行首 `[SCOPE_RESOLVED: ...]`（tests/README.md 两处已同步为 .py；两处 setup() shim 有意保留已记录）
- `agate/tests/README.md` 覆盖度表格 + R2.4 已知风险段 18 处 `.sh` → `.py` 实际同步（count-tests.sh / check-windows-smoke.sh 保留）
- `check-state-transition.py` L170 提示消息 `agate-archive-stale-outputs.sh` → `.py`（DESIGN_GAP 5 的延后修复执行）；`check-state-transition.bats` L500 断言同步；该文件 30/30 绿
- 复核：`python3 agate/scripts/check-scope-resolved.py <task_dir>` exit 0（P4 的 4 条 SCOPE+ 全部被 P1 SCOPE_RESOLVED 覆盖）

**结果**：**已闭环** ✓

## 3. 跨文件一致性（P2 packages / P1 BDD / P4 实现路径 / 文档同步）

| 检查项 | 对照 | 结果 |
|--------|------|------|
| P2§packages 与 P4 实现范围 | P2 声明 packages = [agate-scripts, agate-hooks, agate-consistency, agate-tests, agate-protocol-docs, agate-ci]（与 P1 frontmatter 一致）；P4 批次 0-4 覆盖：scripts（30 sh→py）、hooks（3 薄壳 + 3 py 主程序）、consistency（批次 4a/3f 锚点表同步）、tests（bats 调用点 + 断言级）、protocol-docs（4c-1/4c-2/4e 文档引用）、ci（4c-3 CI workflow） | **一致** ✓ |
| P1§BDD 数量 vs P6 验收数量 | P1 声明 10 条 BDD（BDD-1..10）；P6 frontmatter pass=10 / fail=0，正文 PASS BDD-1..BDD-10 逐条对应 | **一致** ✓（数量与内容均匹配，非只数标题） |
| P4§impl-path 与 P2 §3.2 批次方案 | P2 §3.2 设计批次 0（公共库）→1（自足叶 13）→2（复合 11）→3（hook 链 4）→4（收尾）；P4 实测执行批次 0、1a-1c、1e、2a-2f、3a-3f、4a-4e-fix，覆盖全部 30 个 sh 迁移目标；成品 47 py（18 既有 + 29 新增）+ 3 个 hook sh 薄壳，`ls agate/scripts/*.sh` 实测仅剩 3 个 hook 薄壳 | **一致** ✓ |
| 文档引用同步（表 B + 批次 4e SCOPE+） | 表 B 9 文档（4c-1）+ 5 重写文档（4c-2）+ rules/assets（4e）逐名 grep 复核 .sh 残留 0（P4 自查 + 本次抽查）；**例外见观察 2** | **基本一致**，见观察 2 ⚠ |

**观察 1**：P2 §3.4 写「既有 18 py 报 60 错误（P1 记 70 系版本差异）」——P1 §2.5 写 70，两处版本口径不一致，但 P1 已注明系 ruff 版本差异，P2 §3.4 亦注明「实测 68/60 系版本差异」，属记录口径差异非方案偏离，不构成 BLOCKER。

**观察 2**：`agate/tests/README.md` 覆盖度表格曾引用已删档的 17 个 `.sh` 脚本名——**已于闭环修复中同步为 .py**（见 §2），不再残留。

## 4. 未决项清零

- **P1-requirements.md**：无行首 `[NEED_CONFIRM]` / `[BLOCKER]` / `[DEVIATION-CRITICAL]` 残留（实测仅 `[NO_NEED_CONFIRM]` + 5 条 `[SUGGEST]`，均非阻塞）✓
- **P6-acceptance.md**：10 PASS / 0 FAIL，无 NEED_CONFIRM ✓
- **未闭环项**：无（SCOPE+ 已闭环见 §2；DESIGN_GAP 5 的延后修复已在闭环修复中执行——check-state-transition.py 消息改指 .py）✓

## 5. 总结

跨文件一致性整体良好：P2§packages（6 包）与 P4 实现范围吻合、P1§BDD（10 条）与 P6 验收（10 PASS）数量与内容双匹配、P4§impl-path（47 py + 3 薄壳）与 P2 §3.2 批次方案吻合、DESIGN_GAP 5 条全部 REVIEWED 配对。

**结论：P7 通过**（初始 BLOCKER-1 已于闭环修复后消除）。跨文件一致性整体良好：P2§packages（6 包）与 P4 实现范围吻合、P1§BDD（10 条）与 P6 验收（10 PASS）数量与内容双匹配、P4§impl-path（47 py + 3 薄壳）与 P2 §3.2 批次方案吻合、DESIGN_GAP 5 条全部 REVIEWED 配对、SCOPE+ 全部闭环。

（本文件为审查结论，未修改任何代码/测试/阶段文件；自查≠gate，P7 gate 结果由主 Agent 预跑 check-gate.sh 确认。）
