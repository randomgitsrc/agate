# BDD-10 独立实跑证据：check-retrospective.py DEBT/roadmap 机制缺口信号

## Then 子句逐项核对

Then 要求：
1. 无 retry 超限/SCOPE+/override 异常，但 `agate-workspace/` 下存在关联该 task_id 的新增
   DEBT 登记条目或 roadmap 条目 → 同样输出"建议复盘"提醒
2. 消息文案说明触发原因为"发现机制缺口"，与异常模式的提醒文案可区分
3. exit code 仍为 0

## 构造场景（独立于测试代码，本轮手动搭建）

两级嵌套目录（不复用 pytest fixture）：
```
$WORK/agate-workspace/tasks/T999/.state.yaml   （phase: P8, retries: {} 空——无异常）
$WORK/agate-workspace/debt/tech-debt.md        （task_id: T999）
$WORK/agate-workspace/roadmap/roadmap.md       （| RM-9999 | T999 | open |）
```

`.state.yaml`:
```yaml
task_id: T999
phase: P8
retries: {}
```

`tech-debt.md`:
```
# 技术债登记

## DEBT0099
task_id: T999
description: 测试用假 DEBT 条目
```

`roadmap.md`:
```
# roadmap

| RM | task_id | status |
|----|---------|--------|
| RM-9999 | T999 | open |
```

## 实际运行命令与输出

```
$ cd $WORK/agate-workspace/tasks/T999
$ python3 agate/scripts/check-retrospective.py $WORK/agate-workspace/tasks/T999 .state.yaml

GATE RETRO: 建议复盘 — 发现机制缺口信号：
  - T999 关联的 DEBT/roadmap 条目已登记（可能存在机制缺口，建议复盘归因）
EXIT_CODE: 0
```

## 判定

1. **无 retry/SCOPE+/override 异常，仅 DEBT/roadmap 信号 → 仍触发提醒**：满足——`.state.yaml`
   的 `retries: {}` 为空、task_dir 内无任何含 `[SCOPE+]` 行首标记的文件、无 `override:` 字段，
   即上游 `warnings` 列表为空（不会打印"检测到异常模式："块），但脚本仍独立输出了第二个消息块。
2. **文案区分**：异常模式标题固定是 `GATE RETRO: 建议复盘 — 检测到异常模式：`（本次未触发，
   因为没有异常模式），本次触发的是 `GATE RETRO: 建议复盘 — 发现机制缺口信号：`——两个标题
   逐字不同，可区分。
3. **exit code**：`EXIT_CODE: 0`，与 BDD-10 要求一致。

**结论：满足**——三点全部在本轮独立实跑中被客观观察到，非转抄 P3/P4/P5 测试断言。

## 源码定位

`agate/scripts/check-retrospective.py:66-90`（`_scan_debt_roadmap_signal`）+
`agate/scripts/check-retrospective.py:144-150`（`main()` 内独立第二段 stderr 输出，未并入
`warnings` 列表）。
