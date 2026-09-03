---
phase: P5
task_id: TAG0030
trace_id: TAG0030-P5-20260904
agent: verifier
status: draft
---

# P5 regression 分片结果（TAG0030）

## 测试命令

```bash
timeout 450s python3 -m pytest agate/tests/regression/ -q --tb=no -n auto
```

## 汇总输出

```
28 passed in 1.08s
```

- passed: 28
- failed: **0**
- skipped: 0

## 备注

无失败，无预存失败。回归面全部通过。

EXIT_CODE: 0
