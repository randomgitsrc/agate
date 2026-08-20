---
phase: P2
task_id: TAG0017-toolchain-fixes
type: review
parent: P2-design.md
trace_id: TAG0017-P2review-20260820-retry1
status: approved
created: 2026-08-20
agent: plan-eng-review
---

# P2-review.md — plan-eng-review（工程经理评审，复评轮 retry1）

## 复评范围声明

本轮为增量复评轮，dispatch-context 明确：上轮（P2-review.md 原始版本，trace_id `TAG0017-P2review-20260820`）已确认方案主体（4 功能分组候选方案选择、5 批 dispatch_plan、gate_commands、测试覆盖、数据流/状态机/接口契约/错误边界/最小验证/多方案探索）全部通过，唯一阻塞项是 BLOCKER-1（`SELF-GATE.md` 路径前缀自相矛盾）。本轮只复核该项是否已解决 + 是否有未授权改动，不重新逐项评审已通过内容。

## BLOCKER-1 复核（独立核验）

独立执行命令：
```
$ /usr/bin/grep -n "agate/SELF-GATE" P2-design.md
（无命中）
$ /usr/bin/grep -n "SELF-GATE" P2-design.md
40:| `SELF-GATE.md` L53/54（文件类型表）、L133/143、L183/193（两处派发模板） | ...
149:- `SELF-GATE.md`/`protocol-alignment-review.md` 命名模板含 `{task_id}`；...
189:| `fg2-self-gate-naming` | DEBT0011：命名模板 + 写入前检查 | `SELF-GATE.md`、`assets/review-roles/protocol-alignment-review.md` | low |
216:- `SELF-GATE.md:48-60,125-145,175-195`（文件类型表 + 两处派发模板）— BDD-7 命名模板改动落点
246:  - assumption: "DEBT0011：SELF-GATE.md 命名模板改动 + 写入前检查逻辑是纯文档/文本改动，无外部系统依赖"
```

结果：`agate/SELF-GATE.md` 字符串全文档零命中；`SELF-GATE.md` 出现的全部 5 处（L40/149/189/216/246）均无 `agate/` 前缀，写法统一。逐一核对上轮标记的两处错误落点：
- L40（§1.1「改什么」表格）：已由 `agate/SELF-GATE.md` 订正为 `SELF-GATE.md`。
- L216（§7 files_to_read，`fg2-self-gate-naming` 批次）：已由 `agate/SELF-GATE.md:48-60,125-145,175-195` 订正为 `SELF-GATE.md:48-60,125-145,175-195`。

行号范围（L53/54、L133/143、L183/193、L48-60/125-145/175-195）与订正前保持一致，未发现订正过程中顺带改动引用行号的情况。

**判定：BLOCKER-1 已解决。**

## 未授权改动核查

对照 `P2-dispatch-context-architect-retry1.md`「不要做的事」（不得改动候选方案/影响面梳理其余部分/gate_commands/dispatch_plan/minimal_validation/frontmatter，只做路径前缀字符串订正），逐项核对当前 P2-design.md：

- **frontmatter**：`candidate_count: 8`、`packages: [gate-scripts, hooks-shell, phase-cards, self-gate-template, platform-notes, agent-roles]`、`domains: [protocol-docs, gate-scripts]`、`ui_affected: false`、`dispatch_plan`（5 批 static-batch、parallel_limit: 5，批次 id/complexity 与上轮一致）—— 与上轮评审记录逐字一致，未改动。
- **§2 候选方案**：4 功能分组各 2 候选、选择理由文字与上轮评审引用内容一致，未改动。
- **§5 gate_commands**：`P3`/`P5`/`P5_consistency`/`P5_count_tests`/`P5_shellcheck` 五个 key 及命令内容与上轮一致，未改动。
- **§6 dispatch_plan 说明**：5 批文件边界表格与上轮核验记录（fg1-parser-scripts / fg1-doc-boundary / fg2-self-gate-naming / fg3-strict-mode-code / fg4-windows-python-probe 五批文件集合）逐字一致，未改动。
- **§8 minimal_validation**：4 条 assumption（DEBT0012 实测 / DEBT0014 stub 探测循环实测 / DEBT0010 声明 / DEBT0011 声明）文字与上轮一致，未改动。
- **§1.1/§1.2/§1.3 影响面梳理**：除 L40 一行的路径前缀订正外，其余改动点/不改什么/风险清单文字未见变化。

未发现方案主体被意外改动，订正范围与授权范围（仅 SELF-GATE.md 路径前缀）一致。

## 架构问题（阻塞级）

无。BLOCKER-1 已解决，未发现新增阻塞级问题。

## 架构问题（非阻塞）

无。本次复评未提出"后续应重构/存在架构债"判断，不适用标准 DEBT 条目格式。

## 测试缺口

沿用上轮结论：未发现结构性测试缺口（本轮未改动测试相关内容，无需重新核实）。

## 锁定决策

沿用上轮锁定决策，本轮追加：
- BLOCKER-1（`SELF-GATE.md` 路径前缀）已订正并复核通过，方案主体（候选方案选择、批次划分、gate_commands、minimal_validation、frontmatter）在两轮评审间保持不变，可进入下一阶段。

**结论：approved。**
