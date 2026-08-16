---
phase: P5
task_id: TAG0014-dispatch-orchestration
type: test-results
parent: P4-implementation.md
trace_id: TAG0014-P5-20260816
status: draft
created: 2026-08-16
agent: verifier
---

[PROD_NOT_TOUCHED]

# P5 技术验证结果 — agate 派发编排机制（TAG0014-dispatch-orchestration）

> gate_commands 来源：P2-design.md L216-222。执行环境：worktree 根目录，pytest 9.0.3，python3 + pyyaml。

## failed 汇总

**failed 总数：0**（预存失败：无）

## 命令执行结果

### P5 — pytest 全量测试

- 命令：`python3 -m pytest agate/tests/ -q --tb=no`
- **exit code: 0**
- 输出签名：`780 passed, 2 skipped in 66.88s (0:01:06)`
- **failed: 0**，通过 ✓

### P5_consistency — 协议一致性检查（worktree 自身脚本，--strict）

- 命令：`python3 agate/scripts/check-protocol-consistency.py --strict`
- **exit code: 2**
- 输出签名：`仅有 279 个 WARNING，无 ERROR。`
- 判定：**ERROR = 0**（PASS）；exit 2 由 `--strict` 将 WARNING 视为阻断产生——279 个 WARNING 均为既有叙事文件引用（引述旧路径/脚本名），与本次改动无关，属既有基线（dispatch-context 已声明基线 279 WARNING 0 ERROR）。**非本任务引入**。
- 预存失败：无（WARNING 是文档漂移基线，非测试失败）

### P5_count — 测试用例计数

- 命令：`bash agate/tests/scripts/count-tests.sh`
- **exit code: 0**
- 输出签名：`总计：782 个测试用例（pytest collect-only 口径）`，目标 ≥ 749
- **782 ≥ 749**，通过 ✓（符合 P4 修复轮后基线 782）

## test runner 输出签名行

```
780 passed, 2 skipped in 66.88s (0:01:06)
仅有 279 个 WARNING，无 ERROR。
总计：782 个测试用例（pytest collect-only 口径）
```

## 结论

- P5 主命令：exit 0 + failed=0 → 通过
- P5_consistency：0 ERROR（--strict 阻断仅因既有 WARNING 基线）→ 按 dispatch-context 指引如实记录
- P5_count：exit 0，782 用例 → 通过
- 全量测试已运行（非裁剪/未运行子集），无预存失败
- [PROD_NOT_TOUCHED]：P5 只读验证，未修改任何代码/文档/生产环境
