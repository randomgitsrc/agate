# BDD-14 证据：跨文件描述点同步一致（loop-orchestration.md / task-files.md）

## Then 子句逐项核对

Then 要求：`loop-orchestration.md` 与 `agate/assets/templates/task-files.md` 中对
orchestrator-log 的描述与 BDD-12 扩展后的新语义不矛盾——若逐字复述了"只写决策和下一步"这类
已被扩展的旧表述，需同步更新或删除，不要求逐字重复新语义（`WORKFLOW.md:91` 不处理）。

## 本轮独立核实

```
$ grep -n "orchestrator-log" agate/loop-orchestration.md
168:**原则：主 Agent 尽量无状态。** 因为状态全部落盘（`{AGATE_WORKSPACE}/tasks/active-tasks.md` + 任务目录 + orchestrator-log.md），...
173:- **`orchestrator-log.md` 防无响应**——长操作前写 `NEXT: ...`，写下去就完成使命，不需要再读回来

$ grep -n "orchestrator-log" agate/assets/templates/task-files.md
45:| orchestrator-log.md | 主 Agent | 防无响应锚点（长操作前写 NEXT:），详见 state-machine.md「orchestrator-log.md 防无响应」节 |

$ grep -n "只写决策和下一步" agate/loop-orchestration.md agate/assets/templates/task-files.md
（零命中——两文件均未逐字复述该旧表述）
```

## 逐项核对

| 文件 | 原有描述内容 | 是否复述"只写决策和下一步" | 是否与 BDD-12 新语义矛盾 |
|------|-------------|---------------------------|--------------------------|
| `loop-orchestration.md:168,173` | "状态全部落盘（...+orchestrator-log.md）"（落盘清单式提及）+ "防无响应——长操作前写 NEXT:，写下去就完成使命，不需要再读回来"（防无响应用途摘要） | 否 | 不矛盾——只描述"防无响应"用途，未涉及内容颗粒度限制 |
| `task-files.md:45` | "防无响应锚点（长操作前写 NEXT:），详见 state-machine.md「orchestrator-log.md 防无响应」节"（指针式引用） | 否 | 不矛盾——纯指针引用，无内容颗粒度描述 |

两处均未包含"只写决策和下一步"这一被 BDD-12 扩展的旧限制性表述，语义上是"防无响应"用途的
摘要/指针，与扩展后的新规则（新增"简要依据"）是超集关系而非替代关系，不矛盾。

## 附带核实：指针目标仍有效

`task-files.md:45` 指向的 `state-machine.md「orchestrator-log.md 防无响应」` 节标题在当前
文件中确实存在（`grep -n "orchestrator-log.md.*防无响应" agate/state-machine.md` 命中该
小节标题行），BDD-13 新增的「L2 会话 checkpoint」是平级新增小节，未改动该既有标题，指针依然
有效。

## 判定

**满足**——两处引用点本轮独立读取原文核实，均未逐字复述被 BDD-12 扩展的旧限制性表述，语义
不矛盾（新规则是旧规则的超集，非替代），符合 Then 子句"不要求逐字重复新语义，但不能矛盾"
的验收口径。
