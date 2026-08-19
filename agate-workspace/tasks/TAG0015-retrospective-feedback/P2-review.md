---
phase: P2
task_id: TAG0015
type: review
parent: P2-design.md
trace_id: TAG0015-P2-review-20260819-r1
status: approved
created: 2026-08-19
agent: plan-eng-review
---

# P2-review.md — TAG0015 工程评审（plan-eng-review，重试 #1 复核）

## 结论

**approved**。本轮为重试 #1 聚焦复核（不重新全篇评审），针对上一轮 `needs-revision` 判定的
AP-1（候选方案 A / L2 checkpoint 落点）+ AP-2（files_to_read 行号），architect 已按 dispatch-context
「重试 #1」节 4 点复核清单逐条修订，核查如下：均已妥善解决。

## 复核结果（对照重试 #1 四点清单）

### 复核点 1：§2/§3.2/§3.3/§6 四处是否联动一致（无半吊子状态）

**通过**。四处均一致描述"`P{n}-checkpoint.md`（每阶段 gate 通过后落盘）+
`task-session-summary.md`（P8 gate 通过后一次性落盘）"两件套机制：

- **§2 候选方案 A1**（第 210-272 行）：标题即改为"两件套专用文件"，第 215-224 行明确落盘时机
  两件套（①每阶段 gate 通过时落盘 `P{n}-checkpoint.md` ②P8 gate 通过后落盘
  `task-session-summary.md`），第 237-243 行给出两个文件各自的路径与命名，第 253-259 行给出
  两者各自的防 compact 落盘策略。
- **§3.2**（第 361-386 行）：小节标题即为"L2 会话 checkpoint（两件套）"，正文①②③④四点分别
  覆盖"与 orchestrator-log 关系"「`P{n}-checkpoint.md` 子机制」「`task-session-summary.md`
  子机制」「两者共同覆盖的防 compact 范围」，与 §2 的表述一一对应。
- **§3.3**（第 388-397 行）：标题显式标注"由 1 行改为 2 行"，`task-files.md` 辅助文件表新增
  两行，分别对应两个文件，内容措辞（"每阶段 gate 通过后落盘"/"任务完成时一次性落盘"）与
  §2/§3.2 一致。
- **§6**（第 562-565、570 行）：「实现完成的标志」明确要求 `state-machine.md` 新增小节正文
  "同时含 `P{n}-checkpoint.md`（阶段级，每阶段 gate 通过后落盘）与 `task-session-summary.md`
  （任务级，P8 gate 通过后一次性落盘）两个机制的说明"，并要求 `test_bdd_13_l2_checkpoint_docs`
  断言两个文件名字符串均出现在该小节正文内、通过。

四处措辞、落盘时机、文件路径完全一致，未发现只改一处、其余三处仍停留在旧设计（单一
`task-session-summary.md`）的遗留痕迹。

### 复核点 2：是否解决"P4/P5 附近 session compact 时 L2 是否有非空落点"这一核心问题

**通过**。§2 A1 第 1 点（第 219-221 行）明确"每阶段 gate 通过时落盘 `P{n}-checkpoint.md`……
这是防'任务中途 compact'的核心保障：它在任务生命周期的每一个阶段边界都留下一个非空的 L2
落点，不依赖任务跑到 P8 才产生第一次 L2 记录"；第 233-236 行进一步显式对比"若只保留②
（task-session-summary.md），L2 唯一落点在 P8 完成后：任务中途（如 P4/P5）发生 session
compact 时，L2 尚未产生任何一次落盘……恢复①后，即使 compact 发生在任何阶段之间，最近一次
`P{n}-checkpoint.md` 都是一个非空的 L2 事实源"——这正是上一轮 AP-1 指出的核心缺口，本轮已
用建议 a)（恢复每阶段 checkpoint）方式解除，且论证过程不再依赖上一版"P{n}-progress.md +
orchestrator-log.md 已覆盖同等颗粒度"这一未经内容比对的断言（第 226-232 行显式说明"本次修订
不再依赖这个未经验证的断言"，并给出了为何该断言不成立的具体理由：progress.md 是 subagent
产出、orchestrator-log 是逐决策颗粒度，两者都不等同于 checkpoint 想保留的"本阶段异常/关键
判断/subagent 表现"这种阶段级、主 Agent 视角的评估）。

### 复核点 3：`test_bdd_13_l2_checkpoint_docs` 验收锚点是否合理

**通过**。该锚点断言 `state-machine.md`「L2 会话 checkpoint」小节标题之后的正文同时含
`P{n}-checkpoint.md` 与 `task-session-summary.md` 两个字符串（§5 第 456-460 行、§6 第
565/570 行）。核对 P1-requirements.md BDD-13 原文（第 145-148 行）：其 Then 子句要求的是
"P2-design.md 必须显式回答四问"，落到实现层面即"协议文档（state-machine.md）是否真的落字
描述了设计好的两件套机制"，而不是"某个具体任务运行 P1-P8 时该文件是否真的在磁盘上出现"——
后者属于跨阶段的运行时行为验证，无法用 P3 阶段的静态 pytest 单测覆盖（需要真实跑一次完整任务
编排循环，超出本任务范围，也超出既有 `test_review_role_docs.py` 类测试的惯例颗粒度）。因此
该测试是在 BDD-13 实际验收范围内可行、且与既有测试风格（grep 断言协议文档字符串）一致的恰当
锚点，不是摆样子式的空断言。

### 复核点 4：AP-2 files_to_read 行号是否已订正为覆盖 `AGATE_TDD_TIMEOUT`

**基本通过**。§5 files_to_read 中 `agate_common.py` 条目（第 499-500 行）行号范围已从
`455-482` 改为 `400-482`；经 `grep -n AGATE_TDD_TIMEOUT agate/scripts/agate_common.py` 复核，
实际定义在第 408 行，落在新范围内，P4 implementer 按此行号窗口可以看到该用法参照，AP-2 指出的
问题已解决。唯一遗留的极小瑕疵：`why` 说明文字写"第 407 行"，与实际第 408 行相差 1 行（笔误，
不影响行号范围本身已覆盖该行的事实），不构成阻塞，不要求二次修订。

## 架构问题（阻塞级）

无。上一轮 AP-1（阻塞）已解除。

## 架构问题（非阻塞）

无新增。上一轮 AP-2（非阻塞，files_to_read 行号）已订正解决（见复核点 4），遗留的"407→408"
笔误级别极低，不登记为新问题。

## 测试缺口

无新增测试缺口。§5/§6 已按 AP-1 修订同步补上 `test_bdd_13_l2_checkpoint_docs` 验收锚点，覆盖
恢复后的两件套机制在协议文档层面的落地验证。

## 锁定决策

延续上一轮已核查确认成立的基线（本轮未重新核对，见 dispatch-context 重试 #1 节"不必重新逐条
核对"部分），并新增本轮确认项：

1. 候选方案 B（`agate-feedback.py` 匿名化，B1 轻量正则脱敏）——沿用上一轮核查结论，成立。
2. 20 条 BDD 全覆盖——沿用上一轮核查结论，成立。
3. "不改什么"节完整回应 P1 第 7 节三项范围外观察——沿用上一轮核查结论，成立。
4. gate_commands 声明可执行、非"待定"——沿用上一轮核查结论，成立。
5. minimal_validation 的读代码验证均属实——沿用上一轮核查结论，成立。
6. dispatch_plan: {mode: single} 判据合理——沿用上一轮核查结论，成立。
7. **（本轮新增）候选方案 A / L2 checkpoint 落点**——已恢复 roadmap.md RM-AG0020 原始两件套
   设计（`P{n}-checkpoint.md` 每阶段 + `task-session-summary.md` 任务级），§2/§3.2/§3.3/§6
   四处联动一致，核心防 compact 目的（BDD-13/P0-brief 问题⑦）已被覆盖，AP-1 解除。

## 返回给主 Agent

status: approved + 阻塞问题数量：0（AP-1 已按建议 a 恢复每阶段 checkpoint 机制解除，
§2/§3.2/§3.3/§6 四处联动一致；AP-2 files_to_read 行号已订正覆盖 AGATE_TDD_TIMEOUT 第 408 行；
`test_bdd_13_l2_checkpoint_docs` 验收锚点在 BDD-13 实际验收范围内合理有效）
