# P5-test-results — TAG0028 subagent 存活可观测性与自主再派发（RM-AG0055）· round 2

> 阶段：P5 技术验证（重跑 round 2）· 角色：verifier · 日期：2026-09-03
> 执行依据：P2-design.md §4 gate_commands（命令权威来源，逐 key 独立执行，不拼接 `&&`）
> worktree：`.worktrees/agate-TAG0028`（HEAD=34366ab wf(TAG0028-P4) fix3：R2 回归修复——cmdstream
> fixture/断言裸 python3 17 处改 env python3 豁免形态，恢复 TAG0011 bdd-8 tests 树 0 命中）
> 环境隔离：[PROD_NOT_TOUCHED] 只读验证，未触碰生产环境/其他用户 DSH 会话（fixture 已脱敏）
> 待确认项：[NO_NEED_CONFIRM] 无不可逆操作
> 自查≠gate：本文件为 verifier 产出，主 Agent 验 gate（产出存在 + failed 计数 + 签名校验），CI backstop 兜底。

## 汇总

| key | 命令 | exit code | failed 计数 | 判定 |
|-----|------|-----------|------------|------|
| P5 | `python3 -m pytest agate/tests/ -q --tb=no -n auto` | 0 | 0 | **PASS** |
| P5_consistency | `python3 agate/scripts/check-protocol-consistency.py --strict-errors-only` | 0 | 0 ERROR | PASS |
| P5_cmdstream_verify | `python3 docs/design-notes/260903-design-subagent-liveness-and-self-dispatch/verify-heartbeat-cmdstream/verify_cmdstream_detection.py` | 0 | 0 | PASS（9 场景全 PASS） |
| P5_shellcheck | `shellcheck -S warning agate/scripts/pre-commit-gate.sh agate/scripts/commit-msg-self-gate.sh agate/scripts/pre-push-gate.sh` | 0 | 0 | PASS |
| P5_count_tests | `bash agate/tests/scripts/count-tests.sh` | 0 | 0 | PASS（1436 ≥ 749） |

## 逐 key 记录

### P5 — 全量 pytest（三片 unit/regression/integration 合跑 + `-n auto` 并行）

- 命令：`timeout 900s python3 -m pytest agate/tests/ -q --tb=no -n auto`
- exit code：**0**
- test runner 输出签名行：`1434 passed, 2 skipped in 41.31s`
- 行首签名：passed 1434, failed 0, skipped 2
- FAILED 行计数：0（`grep -E '^FAILED'` = 0）
- 全量测试：已运行（round 1 的 1 failed（bdd-8 R2 回归）经 fix3 修复后恢复全绿，round 2 全量重跑验证无回归）

passed 1434, failed 0, skipped 2

### P5_consistency — 协议一致性检查

- 命令：`timeout 180s python3 agate/scripts/check-protocol-consistency.py --strict-errors-only`
  （worktree 自己的脚本，双工作区纪律）
- exit code：**0**
- 输出签名：`仅有 329 个 WARNING，无 ERROR。`（329 WARNING 为既有基线，WARNING 不判失败）
- failed 计数：0 ERROR → **PASS**

passed 0, failed 0 (consistency: 329 WARNING 基线 / 0 ERROR)

### P5_cmdstream_verify — 命令流检测 9 场景验证（BDD-22 锚）

- 命令：`timeout 180s python3 docs/design-notes/260903-design-subagent-liveness-and-self-dispatch/verify-heartbeat-cmdstream/verify_cmdstream_detection.py`
- exit code：**0**
- 输出签名：`结论：全部断言通过——命令流日志可机械区分九种状态`（PASS/通过 计数 10 = 9 场景 + 结论行）
- failed 计数：0 → **PASS**

### P5_shellcheck — 3 个 hook 薄壳静态检查

- 命令：`timeout 180s shellcheck -S warning agate/scripts/pre-commit-gate.sh agate/scripts/commit-msg-self-gate.sh agate/scripts/pre-push-gate.sh`
- exit code：**0**
- 输出：0 行（无 warning 级及以上问题）→ **PASS**

### P5_count_tests — 用例数不漂移

- 命令：`timeout 180s bash agate/tests/scripts/count-tests.sh`
- exit code：**0**
- 输出签名：`总计：1436 个测试用例（pytest collect-only 口径）`（≥ 749 基线；1436 = 1434 passed + 2 skipped，口径自洽）
- failed 计数：0 → **PASS**

## 结论

- round 2 全部 5 key 通过（P5 全量 pytest exit 0 / 0 failed；consistency 0 ERROR；cmdstream 9 场景全 PASS；
  shellcheck 0 输出；count-tests 1436 ≥ 749）。
- round 1 记录的 1 failed（`test_bdd_8_clean_tree_zero_detection`，fix3 前为新增 fixture 裸 python3
  触发 R2 的回归）经 fix3 修复后不再出现，全量重跑无回归。
- P5 推进条件满足（gate_commands.P5 全部命令 exit 0 + failed=0），由主 Agent 验 gate 后推进 P6。
