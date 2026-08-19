# BDD-13 证据：L2 会话 checkpoint 设计问题声明

文件：`agate/state-machine.md`「L2 会话 checkpoint（两件套）——P{n}-checkpoint.md +
task-session-summary.md」小节

## 验收范围说明（dispatch-context 约束 2）

本任务的 BDD-13 验收对象是**协议文档本身**是否定义了 L2 checkpoint 两件套规则，不要求本任务
期间真的产出过 `P{n}-checkpoint.md` 运行时文件（该机制留给未来任务落地使用，本轮只核对
state-machine.md 是否把四问回答清楚）。

## Then 子句逐项核对（P2-design.md 已明确 BDD-13 的四问）

| 问题 | 是否回答 | 依据（原文摘录） |
|------|---------|-----------------|
| ① 落盘时机 | 是 | `P{n}-checkpoint.md`："落盘时机：主 Agent 在**每个阶段 gate 通过后、派发下一阶段之前**写盘"；`task-session-summary.md`："落盘时机：任务完成、P8 gate 通过后，进入「READY 收尾检查」节之前" |
| ② 落盘文件路径与命名 | 是 | `{AGATE_WORKSPACE}/tasks/{Txxx}/P{n}-checkpoint.md`（`{n}` 为实际阶段号，如 `P4-checkpoint.md`）+ `{AGATE_WORKSPACE}/tasks/{Txxx}/task-session-summary.md`——均为新开文件类型，不是扩展 orchestrator-log.md 覆盖 |
| ③ 与 BDD-12 扩展后 orchestrator-log 语义的关系 | 是 | 小节开篇①"与 orchestrator-log.md 的关系"：明确"三者互补，不是相互替代/包含"，逐条区分 L1（orchestrator-log 逐决策）/ L2-阶段级（P{n}-checkpoint.md）/ L2-任务级（task-session-summary.md）三者颗粒度差异 |
| ④ 防 session compact 的落盘策略 | 是 | `P{n}-checkpoint.md`："防 compact 策略：沿用 orchestrator-log 的'写下去就完成使命'原则——写完即完成使命，不回读校验"；`task-session-summary.md`："P8 gate 通过后主 Agent 亲自写盘，写完即完成使命，不需回读校验" |

## 原文摘录（`agate/state-machine.md`，「L2 会话 checkpoint（两件套）」小节全文）

```
**L2 会话 checkpoint（两件套）——P{n}-checkpoint.md + task-session-summary.md**：

①**与 orchestrator-log.md 的关系**：三者互补，不是相互替代/包含。...

②**`P{n}-checkpoint.md` 子机制**：
- 落盘时机：主 Agent 在**每个阶段 gate 通过后、派发下一阶段之前**写盘
- 文件路径：`{AGATE_WORKSPACE}/tasks/{Txxx}/P{n}-checkpoint.md`...
- 内容颗粒度：本阶段异常/关键判断/subagent 表现，2-4 行极简记录，不要求完整叙述
- 防 compact 策略：沿用 orchestrator-log 的"写下去就完成使命"原则——写完即完成使命，不回读校验

③**`task-session-summary.md` 子机制**：
- 落盘时机：任务完成、P8 gate 通过后，进入「READY 收尾检查」节之前
- 文件路径：`{AGATE_WORKSPACE}/tasks/{Txxx}/task-session-summary.md`
- 内容颗粒度：任务级过程摘要，颗粒度更完整，允许展开因果链叙述
- 防 compact 策略：P8 gate 通过后主 Agent 亲自写盘，写完即完成使命，不需回读校验

④**两者共同覆盖的防 compact 范围**：...
```

## 本轮独立 grep 核实（静态锚点）

```
$ grep -n "L2 会话 checkpoint" agate/state-machine.md
483:- 另见下方「L2 会话 checkpoint」（阶段级 `P{n}-checkpoint.md` + 任务级 `task-session-summary.md`）
494:**L2 会话 checkpoint（两件套）——P{n}-checkpoint.md + task-session-summary.md**：

$ grep -n "P{n}-checkpoint.md\|task-session-summary.md" agate/state-machine.md
483, 494, 497, 500, 504, 506, 511, 513, 517, 518
```

（第 483 行是「orchestrator-log.md 防无响应」小节末尾指向 L2 checkpoint 的双向指针，第 494 行
起才是「L2 会话 checkpoint（两件套）」小节本体标题，两个文件名字符串在标题之后反复出现，
`test_bdd_13_l2_checkpoint_docs` 用 `content.find("L2 会话 checkpoint")` 定位标题起点后校验
两个文件名在其后出现——本轮独立 grep 确认该断言逻辑成立。）

两个文件名字符串均出现在「L2 会话 checkpoint」小节标题之后（非之前误配到别处），满足 P4
implementer 自查记录 `test_bdd_13_l2_checkpoint_docs` 断言的同款检查点（本轮独立复核，非
转抄）。

## 判定

**满足**——四问在 state-machine.md 正文全部有具体、可执行的回答（非空泛承诺），且落盘时机/
路径/关系/防compact策略四项内容均具体到"谁在什么时机写什么路径的文件"级别，符合 P2-design.md
候选方案 A1 的设计意图，验收对象（协议文档定义）与实际文本一致。
