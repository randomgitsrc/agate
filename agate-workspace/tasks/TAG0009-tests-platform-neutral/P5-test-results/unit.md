---
phase: P5
task_id: TAG0009-tests-platform-neutral
type: test-results
parent: P4-implementation.md
trace_id: TAG0009-tests-platform-neutral-P5-20260813
status: draft
created: 2026-08-13
agent: verifier
---

# P5 技术验证结果 — TAG0009 测试套件平台无关化

> 验证环境：worktree `/home/kity/oclab/agate/.worktrees/agate-TAG0005-0009`（Linux，UTF-8）；全部命令在 worktree 根执行；Windows 分支由测试内模拟环境覆盖（Linux 全量覆盖，真 Windows CI 作最终确认，I7）。
> 验证对象：P2-design.md §5 固化的 `gate_commands.P5` 四条命令全量执行。

## 判定汇总

四条命令全部 exit 0，failed = 0。本次改动相关测试与全量回归基线均绿，无新增失败、无预存失败。

| # | 命令 | 结果 | 签名 |
|---|------|------|------|
| 1 | `bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/` | exit 0 | ok 733 / not ok 0 |
| 2 | `python3 agate/scripts/check-protocol-consistency.py --strict` | exit 0 | 0 ERROR 0 WARNING |
| 3 | `shellcheck -S warning agate/scripts/*.sh` | exit 0 | 0 error |
| 4 | `bash agate/scripts/check-platform-assumptions.sh` | exit 0 | 零命中 |

## 命令 1：全量 bats 回归（BDD-28）

运行器：bats 1.10.0。执行完整日志见 `bats.log`，末行 `EXIT_CODE: 0`。

测试运行器输出签名（行首，供 N5 签名校验）：
```
ok 733
not ok 0
```

- ok 计数：733
- not ok 计数：0
- failed = 0

任务特定覆盖确认（Windows 分支模拟，dispatch 约束逐项核对，均绿）：
- helpers-python.bats bdd-13/15/17（探测优先/回退/shim 不静默放行）：`ok 623`、`ok 624`、`ok 625`
- install-hook.bats 复制模式（ln→cp 模拟）bdd-18/19：`ok 630`、`ok 631`；integration/pre-push-hook.bats 复制模式：`ok 723`
- cp1252 编码模拟 bdd-23/26：`ok 608`
- CRLF 归一化 bdd-22：ci-gate-backstop.bats 相关断言随套件全绿
- 无 bc 求和 bdd-24（agate-extract-context.sh bc→awk）：EC.16 系列随套件全绿
- shellcheck 探测 bdd-25/34：`ok 621`
- 扫描器行为测试 14 例（check-platform-assumptions.bats）：随套件全绿（R1/R2/R3 不被 scan-exempt 豁免的负向用例含在内）
- `PATH="/usr/bin:/bin"` 字面为 0（bdd-10）、全树 R2 零命中（bdd-14）：由命令 4 佐证

## 命令 2：协议一致性（BDD-28）

`python3 agate/scripts/check-protocol-consistency.py --strict`（worktree 自己的脚本，I13 双工作区纪律）。完整日志见 `consistency.log`，末行 `EXIT_CODE: 0`。

- CHECK 1/2/3/4/6/7/8/9 全部 PASS
- ERROR = 0，WARNING = 0

## 命令 3：shellcheck（BDD-28）

`shellcheck -S warning agate/scripts/*.sh`。完整日志见 `shellcheck.log`，末行 `EXIT_CODE: 0`。

- error = 0

## 命令 4：平台假设扫描器（BDD-8 闭环）

`bash agate/scripts/check-platform-assumptions.sh`（无参数，默认扫 `agate/tests/` 全树）。完整日志见 `scan.log`，末行 `EXIT_CODE: 0`。

- 零命中（无输出），exit 0——修复后全树无 Unix 平台假设，BDD-8 闭环成立

## 结论

- 四条命令全部 exit 0，failed = 0 → P5 通过
- 全量测试已执行（sanity + unit + regression + integration 全部套件）
- 无新增失败、无预存失败
- 命令执行日志：bats.log / consistency.log / shellcheck.log / scan.log（均含末行 `EXIT_CODE: <n>`）
- 无行首 `- PASS`/`- FAIL` 格式
