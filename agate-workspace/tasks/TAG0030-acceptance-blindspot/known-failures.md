---
task_id: TAG0030
generated_by: verifier (P5)
---
# 已知失败登记

> **语义边界**：本文件只登记**预存失败**（P5 之前就存在的、与当前任务无关的失败）。
> 当前任务引入的失败用 P5-test-results/ 记录，不写本文件。

## 预存失败（非本任务引入）

| # | 测试文件 | 失败数 | 根因 | 与本任务相关 | 处理计划 |
|---|---------|--------|------|-------------|---------|
| 1 | `agate/tests/unit/test_agate_next_card.py::test_nc_byte_stability_two_calls_sha256_equal` | 1（仅全量 `-n auto` 并行下；串行全量 1313 全绿） | TAG0011 遗留并行竞争：`test_agate_inject_card.py` IC_IDEMPOTENT.2 用例临时改写真实 `phase-cards/P3-tdd.md`（try/finally 必还原），与 next-card 双读同文件 sha256 并发竞争——中间时刻文件被临时追加改写，两次哈希不同。本任务新增 21 断言审计用例改变了 xdist 调度时序使该窗口稳定命中（6 组对照实验：单例/文件级/配对/排除新测试/串行全量均通过，仅全量并行含新测试复现 3/3） | 否 | 推迟（CI 已含 `--reruns 1` flaky 兜底，TAG0023 RM-AG0044；根因修复 = 让 inject-card IC_IDEMPOTENT.2 用临时副本而非改写真实卡，属 TAG0011 测试面，不在本任务范围——建议登记 DEBT 由后续任务处理） |

## 说明

- P5 判定依据：verifier 6 组对照实验（详见 `P5-test-results/unit.md`）——失败仅在"全量并行（含 test_tag0030_assertions.py）"下稳定出现；串行全量 1313 passed 证明无功能性回归。
- 本任务改动面（协议文档条文 + 断言审计只读测试）不涉及这两个测试文件，也不涉及 phase-cards 写入机制。
