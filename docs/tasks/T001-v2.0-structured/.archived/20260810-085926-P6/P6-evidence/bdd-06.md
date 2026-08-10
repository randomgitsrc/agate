# BDD-6: 缺必填字段时 gate 拦截

## P5 测试证据
- `ok 153 CF.4 BDD-6: P1 frontmatter 缺 risk_level（其余必填齐全）→ 校验失败`
- `ok 154 CF.5 BDD-6: P2 frontmatter 缺 candidate_count（其余必填齐全）→ 校验失败`
- `ok 155 CF.6 BDD-6+FIND-1: P7 frontmatter 只含 blocker_count（无任何流 A 字段）仍按 P7 schema 校验，缺 design_gap_count → 报错`

P3-test-cases.md 把 BDD-6 拆成 P1/P2/P7 三类 schema 场景（CF.4/CF.5/CF.6），本次逐一独立复现。

## 本次验收独立复现（三个 schema 场景）

### P1 缺 risk_level
```
$ bash agate/scripts/check-frontmatter.sh .../P1-requirements.md   # frontmatter 无 risk_level，其余必填齐全
GATE FRONTMATTER: .../P1-requirements.md frontmatter 格式错误：
  - P1-requirements.md:risk_level: 缺必填字段 risk_level
exit=1
```

### P2 缺 candidate_count
```
$ bash agate/scripts/check-frontmatter.sh .../P2-design.md   # frontmatter 无 candidate_count，其余必填齐全
GATE FRONTMATTER: .../P2-design.md frontmatter 格式错误：
  - P2-design.md:candidate_count: 缺必填字段 candidate_count
exit=1
```

### P7 只含 blocker_count（FIND-1 判别契约边界场景）
```
$ bash agate/scripts/check-frontmatter.sh .../P7-consistency.md   # frontmatter 只有 blocker_count: 0
GATE FRONTMATTER: .../P7-consistency.md frontmatter 格式错误：
  - P7-consistency.md:deviation_count: 缺必填字段 deviation_count
  - P7-consistency.md:deviation_critical_count: 缺必填字段 deviation_critical_count
  - P7-consistency.md:design_gap_count: 缺必填字段 design_gap_count
  - P7-consistency.md:design_gap_reviewed_count: 缺必填字段 design_gap_reviewed_count
exit=1
```
这条同时验证了 P2-design.md FIND-1 判别契约：文件只含该 schema 迁移字段集的其中一个
（`blocker_count`）就已经被判定为"新格式"并触发完整必填校验，而不是被误判为旧格式豁免校验——
这正是 FIND-1 要解决的"流 B/C 文件只有自身字段时仍需正确校验"的问题。

三种场景 exit code 均为 1（拦截），"门禁退出非零，不依赖主 Agent 人工判断"，符合 BDD-6 Then。

## 判定
PASS
