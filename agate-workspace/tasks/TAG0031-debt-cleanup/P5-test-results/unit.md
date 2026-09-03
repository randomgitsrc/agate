# P5 技术验证结果 — TAG0031-debt-cleanup

- 执行时间：2026-09-04
- 工作目录：/home/kity/oclab/agateon/.worktrees/agate-TAG0031
- 执行方式：四条 gate_commands.P5 独立执行（不用 `&&` 串联），逐条记录 exit code
- [PROD_NOT_TOUCHED]（`ls -la ~/.agate` 前后快照对比一致，`find /home/kity/oclab/agateon/agate -maxdepth 1` mtime 快照无差异）
- [NO_NEED_CONFIRM]（无涉及数据删除/迁移等不可逆操作）

## 签名行（test runner 计数，逐 key 独立重跑得出）

passed: 1435
failed: 0
skipped: 2
passed: 1
failed: 0

## P5（全量单元/回归/集成测试）

命令：`timeout 200s python3 -m pytest agate/tests/unit/ agate/tests/regression/ agate/tests/integration/ -n auto -q --tb=no`

- exit code: **0**
- 汇总：**1435 passed, 2 skipped, 0 failed**（33.37s）
- 与 P4 阶段实测数字（1435 passed/2 skipped/0 failed）一致，本轮为独立重跑确认，非复用
- 原始 test runner 输出签名（verbatim tail）：
```
1435 passed, 2 skipped in 33.37s
```

## P5_consistency（协议一致性检查，strict-errors-only）

命令：`timeout 90s python3 agate/scripts/check-protocol-consistency.py --strict-errors-only`（worktree 自己的脚本，非 `~/.agate` 稳定版）

- exit code: **0**
- 汇总：**0 ERROR，329 WARNING**（"仅有 329 个 WARNING，无 ERROR。"）——`--strict-errors-only` 模式下 WARNING 不阻断，全部为既存的"叙事文件引用不存在（可能是引述旧问题）"类提示，与本次改动无关

## P5_shellcheck（shell 脚本静态检查）

命令：`timeout 90s shellcheck -S warning agate/scripts/*.sh`

- exit code: **0**
- 汇总：**无警告/错误输出**（空输出，全部脚本通过 warning 级别检查）

## P5_offline_bundle（离线包往返回归）

命令：`timeout 150s python3 -m pytest agate/tests/regression/test_offline_bundle_roundtrip.py -q --tb=no`

- exit code: **0**
- 汇总：**1 passed, 0 failed**（0.03s）
- 原始 test runner 输出签名（verbatim tail）：
```
1 passed in 0.03s
```

## 总体判定

四条 gate_commands.P5 命令 exit code 全部为 0，failed 计数全部为 0。**全部通过**，未发现预存失败，无需 known-failures.md。
