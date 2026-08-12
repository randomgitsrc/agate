# BDD-21/22/23 — 流 C：标记状态收尾实测

独立重跑（非引用旧记录）：

## BDD-21（P1 NEED_CONFIRM 已解决状态结构化）+ BDD-22（SCOPE_RESOLVED 闭环）
```
1..20
ok 1 RT.1 check-retrospective.sh 无异常 期望 exit 0 + 无输出
ok 2 RT.2 check-retrospective.sh retries 超限 期望 exit 0 + 含'重试超限'
ok 3 RT_BDD21.1 BDD-21: check-gate.sh P1 frontmatter need_confirm_resolved 已覆盖具体描述时该 NEED_CONFIRM 项不再阻塞
ok 4 RT.DP1: dispatch-prompt file excluded from SCOPE+ scan
ok 5 RT.4 check-retrospective.sh override 触发 期望 exit 0 + 含'override'
ok 6 RT.5 check-retrospective.sh retries[P3]=2 触发超限（P3 MAX=2）
ok 7 RT.6 check-retrospective.sh retries[P3]=1 不触发（P3 MAX=2 未达）
ok 8 RT.7 句中 [SCOPE+]（非行首）不触发复盘提醒 期望 exit 0 + 无输出
ok 9 RETRO_SCOPE_DC.1 dispatch-context 含 [SCOPE+] 不触发复盘提醒
ok 10 RETRO_SCOPE_CARD.1 AGATE_CARD 块内 [SCOPE+] 不触发复盘提醒
ok 11 SC.1 check-scope-resolved.sh 不存在的 task 目录 期望 exit 2
ok 12 SC.2 check-scope-resolved.sh 无 SCOPE+ 触发 期望 exit 0
ok 13 SC.3 check-scope-resolved.sh 有 SCOPE+ 但无 P1 文件 期望 exit 1
ok 14 P2.53: progress file with [SCOPE+] text does not trigger SCOPE check
ok 15 SC.DP1: dispatch-prompt file excluded from SCOPE+ scan
ok 16 SC.4 check-scope-resolved.sh 有 SCOPE+ 但 P1 无 SCOPE_RESOLVED 期望 exit 1
ok 17 SC.5 check-scope-resolved.sh 有 SCOPE+ + P1 有 [SCOPE_RESOLVED] 期望 exit 0
ok 18 SC_BDD22.1 BDD-22: check-scope-resolved.sh 有 SCOPE+ + P1 frontmatter scope_resolved 非空列表 → 闭环判定通过
ok 19 SC.6 dispatch-context 文件中的 [SCOPE+] 字面引用不触发检查
ok 20 SC.7 句中 [SCOPE+]（非行首）不触发检查 期望 exit 0
```

## BDD-23（发现性标记 SCOPE+/PROD_TOUCHED/DESIGN_GAP 本体保持散文，行为与 v0.35 一致）
散文扫描回归（SC.2/SC.3/SC.4/SC.6/SC.7，已在上方 check-scope-resolved.bats 输出中，全绿）

PROD_TOUCHED 行首锚定回归（integration/pre-commit-hook.bats 的 IT_PT_* 系列）：
```
1..42
ok 13 IT_PT_BINARY.1 暂存 diff 含行首 [PROD_TOUCHED] 描述 → 中止 commit（步骤 1）
ok 14 IT_PT_BINARY.2 暂存 diff 含 [PROD_NOT_TOUCHED] → 不中止
ok 15 IT_PT_BINARY.3 暂存 diff 含删除行 [PROD_TOUCHED] → 不中止（只扫 ^+ 行）
ok 16 IT_PT_BINARY.4 暂存 diff 含句中引用 [PROD_TOUCHED]（非行首声明）→ 不中止（T090 修复）
ok 17 IT_PT_BINARY.5 暂存 diff 含句中引用 [PROD_TOUCHED]（非行首声明）→ 不中止（T090 修复）
ok 18 IT_PT_BINARY.6 暂存 diff 既无正向也无负向 → 不中止 + 无 WARNING（步骤 3 静默通过）
ok 24 IT_PT_BINARY.7 暂存 diff 含 [PROD_NOT_TOUCHED] 确认未接触（负向+描述）→ 不中止
ok 25 IT_PT_MENTION.1 正文句中提及 [PROD_TOUCHED]（非行首声明）→ 不误报（T090 修复）
ok 34 IT_PT_T6.1 P8 dispatch-context 含 AGATE_CARD 注入块（[PROD_TOUCHED] 说明文本）→ 不误拦
ok 35 IT_PT_T6.2 任务产出文件含句中 [PROD_TOUCHED]（非 AGATE_CARD 块内）→ 不拦截（T090 修复）
ok 36 IT_PT_T6.3 任务产出文件含行首 [PROD_TOUCHED]（步骤1）→ 拦截（回归）
ok 37 IT_PT_T6.4 任务产出文件含 [PROD_NOT_TOUCHED]（负向声明）→ 不拦截（回归）
```

DESIGN_GAP 行首锚定回归（check-gate.bats 的 G_DG_ANCHOR 系列）：
```
ok 90 G_DG_ANCHOR.1 P7 句中 [DESIGN_GAP: xxx]（非行首）不计入 GAP 计数
ok 91 G_DG_ANCHOR.2 P7 行首 [DESIGN_GAP: xxx] 计入 GAP 计数
```

## DESIGN_GAP 交叉标注（涉及 BDD-22，P4-implementation.md 流 C 声明，如实转录不裁决）
[DESIGN_GAP: check-scope-resolved.sh 对 P1 frontmatter scope_resolved 字段'存在但为空列表'与'字段完全不存在'两种情况未做区分处理——两者都落入正文 [SCOPE_RESOLVED] grep 回退判定。已有测试覆盖的场景仅'字段存在且非空'(SC_BDD22.1，通过) 与'字段完全不存在'(SC.2/3/4/6/7，通过)，'字段存在但空列表'这一中间态未被 P3 测试覆盖，implementer 已声明该简化的功能后果与风险（见 P4-implementation.md 流 C DESIGN_GAP 全文）。不影响本次已测场景的 PASS 判定，留存供 P7 交叉核对。]

结论：RT_BDD21.1、SC_BDD22.1 实测通过；散文标记回归（SC.2/3/4/6/7 + IT_PT_* 全系列 + G_DG_ANCHOR）实测保持绿灯，行为与 v0.35 一致，符合 BDD-21/22/23 要求。
