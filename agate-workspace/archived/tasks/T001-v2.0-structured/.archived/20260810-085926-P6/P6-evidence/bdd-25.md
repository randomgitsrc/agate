# BDD-25: 新编号格式 TAG0001 被 v2.0 校验器接受

## P5 测试证据
- `ok 137 SY.1 BDD-25/26: 新格式 TAG0001 校验通过；旧格式 T001 硬切拒绝（不兼容双格式）`

## 本次验收独立复现
```
$ cat .state.yaml
task_id: TAG0001
phase: P1
status: active
retries: {}

$ bash agate/scripts/check-state-yaml.sh .state.yaml; echo "exit=$?"
exit=0
```
`TAG0001`（项目代号 AG + 动态编号 0001）匹配新正则 `^T[A-Z]{2}\d+$`，校验通过，不报
"task_id 格式错误"。

## 关联 DESIGN_GAP 修复确认
P4-implementation.md 流 D 交付时曾报告一个 DESIGN_GAP：硬切正则触发了 33 个既有测试
（`check-state-yaml.bats` SY.8 + 32 个集成测试）连带失败，因为这些测试的 fixture 用旧格式
task_id（如 T999）经真实 pre-commit hook 间接触发新正则拦截。该 DESIGN_GAP 已通过独立的
test-designer 派发（commit `68e4173 wf(T001-P4-streamD-fixturefix): 修复流D硬切引发的33个既有
fixture回归`）修复——P5-test-results/unit.md 本次验收引用的 P5 全量结果（600/600，含
SY.8/IT.2/IT.3 等此前失败用例）已确认全部转绿，本次验收也已独立重跑相关命令确认无残留失败
（见 BDD-26 证据文件的 check-state-yaml.sh 独立复现，以及本文件开头的复现）。

## 判定
PASS
