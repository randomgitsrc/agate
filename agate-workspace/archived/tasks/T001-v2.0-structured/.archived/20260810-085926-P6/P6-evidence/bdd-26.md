# BDD-26: 旧编号格式 T001 被 v2.0 校验器拒绝（硬切）

## P5 测试证据
- `ok 137 SY.1 BDD-25/26: 新格式 TAG0001 校验通过；旧格式 T001 硬切拒绝（不兼容双格式）`（同一用例
  内断言两个方向）
- `ok 438 SY.8 check-state-yaml.sh 全合规 期望 exit 0`（该用例在流 D 硬切后曾一度因用旧格式
  T001 fixture 而失败，经 fixture 修复后转绿，P5 全量已确认——注意 SY.8 现在测的场景已经不是
  "T001 合规"而是流 D 修复后改用新格式 fixture 的"全合规"，与 BDD-26 相关的是它此前失败又转绿
  这段历史，见下方 DESIGN_GAP 说明）

## 本次验收独立复现
```
$ cat .state.yaml
task_id: T001
phase: P1
status: active
retries: {}

$ bash agate/scripts/check-state-yaml.sh .state.yaml
GATE STATE-YAML: .state.yaml 格式错误：
  - task_id 格式错误: T001（应为 T + 2 个大写字母项目代号 + 数字，如 TAG0001）
exit=1
```
`T001` 不匹配新正则 `^T[A-Z]{2}\d+$`（缺少 2 个大写字母的项目代号段），被拒绝，报错信息给出
合法格式提示（`如 TAG0001`）。exit=1，符合 BDD-26 Then："校验失败并提示合法格式，不兼容旧格式
（硬切，无双格式过渡）"。

## DESIGN_GAP 交叉核对（P4-implementation.md 第 448 行）
[DESIGN_GAP]：硬切正则上线时曾额外触发 33 个既有测试（都是"真实 pre-commit hook 间接调用
agate-state-yaml-check.py 拦截旧格式 fixture"导致测试本身要验证的行为没机会被断言）连带失败。
implementer 如实呈报未擅自降级处理，交主 Agent/P7 裁决。该 DESIGN_GAP 已通过 P4 阶段追加派发
（commit 68e4173）修复：test-designer 把相关 fixture 的 task_id 批量迁移为新格式。本次验收
观察：P5-test-results/unit.md 全量 600/600 已确认这批测试全部转绿，属于"已核实并已解决"的
DESIGN_GAP，不影响 BDD-26 当前判定。

## 判定
PASS
