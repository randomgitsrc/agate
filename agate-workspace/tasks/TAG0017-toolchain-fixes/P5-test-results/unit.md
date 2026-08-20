---
phase: P5
task_id: TAG0017-toolchain-fixes
type: test-results
trace_id: TAG0017-P5-20260820
status: draft
created: 2026-08-20
agent: verifier
---

# P5 技术验证结果 — TAG0017-toolchain-fixes

[PROD_NOT_TOUCHED]
[NO_NEED_CONFIRM]

对应父提交（P4 实现完成后的 HEAD）：`17a3a5d6ea00f968352dbeba1c5bf5b22488e786`

严格按 P2-design.md §5 `gate_commands` 原文逐条独立执行（不 `&&` 拼接，DEBT0012 以身作则），4 条全部执行，如实记录。

## 命令1: P5（pytest 全量）

```
python3 -m pytest agate/tests/ -q --tb=no
```

- exit code: 0
- 结果签名: `1011 passed, 2 skipped in 89.74s (0:01:29)`
- failed=0
- 判定: PASSED

pytest 原始输出签名行（test runner 输出，供 N5 签名校验）：
```
passed=1011 skipped=2 failed=0
```

## 命令2: P5_consistency（协议一致性检查，--strict-errors-only）

```
python3 agate/scripts/check-protocol-consistency.py --strict-errors-only
```

- exit code: 0
- 结果: `0 ERROR`，`WARNING (314)` — 输出尾行 `仅有 314 个 WARNING，无 ERROR。`
- 与 dispatch-context `<objective_info>` 声明的历史基线「314 条历史 WARNING（叙事文件死链，非本任务引入）」完全一致
- 预存失败登记：314 条 WARNING 属预存（P5 之前就存在，与本次改动无关，均为历史叙事文件死链引用），不阻断 `--strict-errors-only` 模式判定（该模式仅 ERROR 非零）
- 判定: PASSED（0 ERROR）

## 命令3: P5_count_tests（用例覆盖度自检）

```
bash agate/tests/scripts/count-tests.sh
```

- exit code: 0
- 结果: `总计：1013 个测试用例（pytest collect-only 口径）`，目标 `≥ 749`（TAG0011 迁移基线）——达标
- 说明：1013（collect-only 含 skip 用例）与命令1 的 `1011 passed, 2 skipped`（1011+2=1013）口径一致
- 判定: PASSED

## 命令4: P5_shellcheck（shell 脚本静态检查）

```
shellcheck -S warning agate/scripts/*.sh
```

- exit code: 0
- 结果: 无输出（0 warning，0 error）
- 判定: PASSED

## 汇总

- 4/4 命令全部 exit=0
- failed=0（pytest 0 failed；consistency 0 ERROR；count-tests 达标；shellcheck 0 warning）
- 预存失败：0 条新增失败；314 条 WARNING 属预存基线（与本次改动无关），已在命令2 结果段声明，不需登记 `known-failures.md`（`--strict-errors-only` 模式设计目的即为容忍此类预存 WARNING 不阻断链路，属本任务 DEBT0012 修复对象本身，非需修复项）
- **Summary**: PASSED: 4, FAILED: 0
