# BDD-27: check-changelog 直接匹配完整 task_id

## P5 测试证据
- `ok 147 CL.6 BDD-27: CHANGELOG 含完整新格式 task_id TAG0001 → 直接匹配成功`
- `ok 148 CL.7 BDD-27: CHANGELOG 只含 TAG00012（另一任务的更长编号）时 TAG0001 不误匹配`
- `ok 149 CL.8 BDD-27: 旧版短前缀提取（grep -oE 'T[0-9]+'）对新格式 TAG0001 提取为空——直接匹配已消除该摩擦`

## 本次验收独立复现（两个方向）
### 正向：TAG0001 完整匹配成功
```
$ echo -e "# Changelog\n\n## [Unreleased]\n- TAG0001: proper new-format task entry" > CHANGELOG2.md
$ CHANGELOG_FILE=CHANGELOG2.md bash agate/scripts/check-changelog.sh TAG0001; echo "exit=$?"
exit=0
```

### 反向：TAG0001 不应被 TAG00012（更长编号）误匹配
```
$ echo -e "# Changelog\n\n## [Unreleased]\n- TAG00012: another task's longer id entry" > CHANGELOG.md
$ CHANGELOG_FILE=CHANGELOG.md bash agate/scripts/check-changelog.sh TAG0001; echo "exit=$?"
GATE CHANGELOG: [Unreleased] 区域未找到 TAG0001（或 TAG0001）
exit=1
```
`grep -oE 'T[0-9]+'` 短前缀提取对 `TAG0001`（T 后紧跟字母）本就提取为空，v0.35 逻辑下这条记录
检查会直接失效；v2.0 改为直接匹配完整 task_id 后，TAG0001 被完整识别，且不会被形似但更长的
`TAG00012` 误判为匹配（带单词边界保护）。

## DESIGN_GAP 交叉核对（P4-implementation.md 第 446 行）
[DESIGN_GAP]：check-changelog.sh 额外移除了 P2-design.md §3.4.2 原文要求"保留"的
`grep -qF "$TASK_ID"` 固定字符串 fallback 分支。implementer 给出的理由：`TASK_ID_SHORT` 去短
前缀提取后已恒等于 `TASK_ID`，若保留该 fallback，会对同一字符串做一次无单词边界保护的子串
匹配，导致 `TAG0001` 被 `TAG00012` 误判为已匹配——与本条 BDD-27 明确要求的 CL.7"不误匹配"场景
直接矛盾。implementer 按"测试断言与设计字面表述矛盾时不改测试、标记偏离"处理，移除了该
fallback。
本次验收观察：这个 DESIGN_GAP 恰恰是为了让 BDD-27 三个用例（CL.6/CL.7/CL.8）都能通过而做的
必要调整——若按 P2 原文保留 fallback，CL.7（不误匹配）会失败。移除后是唯一能同时满足全部三个
验收断言的实现方式，本次独立复现的"反向"场景（TAG00012 不误匹配 TAG0001）正是对这个 DESIGN_GAP
决策正确性的直接验证。

## 判定
PASS
