---
phase: P5
task_id: TAG0030
trace_id: TAG0030-P5-20260904
agent: verifier
status: draft
---

# P5 unit 分片结果（TAG0030）

## 测试命令

```bash
timeout 450s python3 -m pytest agate/tests/unit/ -q --tb=no -n auto
```

## 汇总输出

```
1 failed, 1312 passed, 2 skipped in 23.37s
FAILED agate/tests/unit/test_agate_next_card.py::test_nc_byte_stability_two_calls_sha256_equal
```

- passed: 1312
- failed: **1**
- skipped: 2

## 预存失败（与本次改动无关）

**预存失败：`test_nc_byte_stability_two_calls_sha256_equal`（TAG0011 遗留并行竞争 flaky，与本次改动无关）**

根因：`agate/tests/unit/test_agate_inject_card.py` IC_IDEMPOTENT.2 用例（TAG0011 既有测试，文件头注释明确
"会临时改写真实 phase-cards/P3-tdd.md（try/finally 必还原）"）在 `-n auto` 并行下与
`test_agate_next_card.py::test_nc_byte_stability_two_calls_sha256_equal`（两次调用 agate-next-card.py P3、
对同一 phase-cards/P3-tdd.md 计算 sha256 并比较）并发竞争——中间时刻文件被临时追加改写，两次哈希不同 → 断言失败。

判定证据（6 组对照实验全部完成）：

| 实验 | 命令 | 结果 |
|---|---|---|
| 单例复跑 | pytest 单用例 --tb=short | 1 passed |
| 文件级 | pytest test_agate_next_card.py -n auto | 22 passed |
| 配对 | pytest test_agate_next_card.py + test_tag0030_assertions.py -n auto | 43 passed |
| 排除新测试 | pytest unit/ --ignore=test_tag0030_assertions.py -n auto | 1292 passed, 2 skipped |
| **串行全量** | pytest unit/ -p no:xdist | **1313 passed, 2 skipped（全绿）** |
| 全量并行复现 | pytest unit/ -n auto | 1 failed（复现 3/3） |

结论：失败仅在"全量并行（含 test_tag0030_assertions.py）"下稳定出现；串行全量 1313 全绿证明无功能性回归。
失败根因是 TAG0011 两个既有测试（inject-card 临时改写真实 P3-tdd.md vs next-card 双读哈希）的并行竞争，
TAG0030 改动面（协议文档条文 + 断言审计只读测试）不涉及这两个测试文件，也不涉及 phase-cards 写入机制。
新增 21 用例改变了 xdist 调度时序，使该竞争窗口稳定命中。是否修复（如给 inject-card IC_IDEMPOTENT.2 加
锁/改用临时副本）由主 Agent 判断，P5 只读验证不做修改。

## 断言审计重点核对

- `test_tag0030_assertions.py`：21/21 全绿 ✓（含在全量 1312 passed 中）
- `test_review_role_docs.py`（14 用例）：全绿 ✓
- `test_protocol_mechanism_anchors.py`（28 用例）：全绿 ✓

EXIT_CODE: 1
