---
phase: P5
task_id: TAG0005-mechanism-fixes
type: test-results
parent: P4-implementation.md
trace_id: TAG0005-mechanism-fixes-P5-20260813
status: draft
created: 2026-08-13
agent: verifier
---

# P5 技术验证结果 — agate 机制修复批（TAG0005）

## 结论

三条 P5 命令全部 exit 0，全量测试全绿，无失败。`fail-list.txt` 为空。

| 命令 | 结果 | exit code |
|------|------|-----------|
| P5（bats 全量） | 726 ok / 0 not ok | 0 |
| P5_consistency（--strict） | 8/8 CHECK PASS，0 ERROR，0 WARNING | 0 |
| P5_shellcheck（-S warning） | 0 error | 0 |

## P5：bats 全量（sanity + unit + regression + integration）

命令（P2-design.md §3 gate_commands.P5）：

```
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
```

日志：`P5-test-results/bats.log`（末行 `EXIT_CODE: 0`）

测试运行器输出签名（ok/not ok 计数）：

```
ok 726（726 ok，0 not ok）
```

- 全量执行，未跳过任何测试文件（sanity.bats + unit/ + regression/ + integration/）。
- 分片明细：unit 619 + regression 17 + integration 84 + sanity 6 = 726，与 P4-implementation.md 自查数一致，且为独立重跑确认（external-output-gate，非复用 P4 自查）。
- 未发现预存失败（known-failures.md 无需登记）。
- 各修复相关测试均绿：GPC.1/2/3（RM-AG0011 主/辅计数）、G5_CMD.1/5 主/辅文案、RP.17/18/19（RM-AG0012）、test_bdd_13/14/15/16（check-debt.sh exit 2 守卫）、文档断言（BDD-1/2/9/12/13/14/15 文本断言）。

## P5_consistency：协议结构一致性检查

命令（P2-design.md §3 gate_commands.P5_consistency，worktree 自己的脚本）：

```
python3 agate/scripts/check-protocol-consistency.py --strict
```

日志：`P5-test-results/consistency.log`（末行 `EXIT_CODE: 0`）

结果：CHECK 1/2/3/4/6/7/8/9 全部 PASS，0 ERROR，0 WARNING（--strict 下 WARNING 亦阻断，无输出即全绿）。

## P5_shellcheck：脚本静态检查

命令（P2-design.md §3 gate_commands.P5_shellcheck）：

```
shellcheck -S warning agate/scripts/*.sh
```

日志：`P5-test-results/shellcheck.log`（末行 `EXIT_CODE: 0`）

结果：0 error（-S warning 级别）。

## 附加客观查证（in-situ 验证，非 P5 命令集）

1. **RM-AG0011 WARNING 新文案 in-situ 验证**：worktree 自己的 `agate/scripts/check-gate.sh P5` 输出
   `GATE P5 WARNING: P2 声明了 1 个主命令 + 2 个辅助命令（共 3 条 gate_commands.P5 命令），请确认已全部执行（非子集）。`
   ——与本任务 P2-design.md 声明的「1 主 + 2 辅」完全一致，BDD-3/4 落地确认。
2. **BDD-15 同类扫描守卫**：`rg -n '>&2;\s*exit 0' agate/scripts/*.sh` 仅剩 3 处
   （均为 agate-capture-env-baseline.sh 的有意跳过语义行），与 P2-design.md §7.6 预期一致。
3. **check-gate.sh P5 门禁**：worktree 脚本 exit 2（WARNING 级，主 Agent 自判），符合「1 主 + 2 辅」需人工确认的预期；stable `~/.agate` 版仍显示旧文案（旧工具），属工具版本差异，非缺陷。

## 环境隔离

`[PROD_NOT_TOUCHED]`——全程仅在 worktree 内运行 bats / consistency / shellcheck / check-gate，未接触生产环境。

## 门槛确认

- 三条 P5 命令全部实际执行且 exit 0（bats.log / consistency.log / shellcheck.log 证据）。
- unit.md 含测试运行器输出签名（ok/not ok 计数）。
- fail-list.txt 为空文件（无失败）。
- 无行首 `- PASS`/`- FAIL` 格式。
