# P5 技术验证结果 — TAG0026 维护性反模式 gate（RM-AG0046）

- 验证模式：只读技术验证（不修代码 / 不启动服务 / 不 git 写操作）→ [PROD_NOT_TOUCHED]
- 执行目录：/home/kity/oclab/agateon/.worktrees/agate-TAG0026（worktree 根，HEAD f7e7b9f = P4 实现 commit）
- 执行方式：P2-design §4 gate_commands 5 键逐条独立执行（每条独立 bash 调用，无 && 链）；全量 pytest 单次跑完（150.77s < 600s timeout），未分片，无需分片口径合并
- **failed 计数：failed=0**（其中预存失败 0）
- 命令结果总览：P5=0 / consistency=0 / count_tests=0 / ruff=0 / shellcheck=0（5/5 exit 0）

---

## 1. P5 — 全量 pytest

- 命令：`timeout 600 python3 -m pytest agate/tests/ -q --tb=no`
- exit code：**0**
- 耗时：150.77s（0:02:30），未超 600s 上限
- 输出尾部（最后 4 行原样）：

```
.......................................                                  [100%]
1333 passed, 2 skipped in 150.77s (0:02:30)
```

- 判定：**pass**（exit 0 + failed=0）

## 2. P5_consistency — 协议一致性

- 命令：`timeout 120 python3 agate/scripts/check-protocol-consistency.py --strict-errors-only`（worktree 自己的脚本，符合 dogfooding 约定）
- exit code：**0**
- 耗时：<120s（timeout 未触发）
- 输出尾部（汇总行原样）：

```
  仅有 323 个 WARNING，无 ERROR。
EXIT_CODE:0
```

- ERROR 计数：**0**；WARNING 计数：**323**（全部为"引用的文件不存在（叙事文件，可能是引述旧问题）"类历史叙事 WARNING，非本任务引入；`--strict-errors-only` 只按 ERROR 判失败）
- 判定：**pass**（0 ERROR）

## 3. P5_count_tests — 用例数自检

- 命令：`timeout 60 bash agate/tests/scripts/count-tests.sh`
- exit code：**0**
- 输出（全文原样，未截断）：

```
=== pytest 用例覆盖度自检 ===
总计：1335 个测试用例（pytest collect-only 口径）

目标：≥ 749（TAG0011 迁移基线，BDD-1）；迁移期数值单调逼近 749。
如果此数字与 docs/plans/agate-test-plan-2026-07-01.md 附录 A 的口径不一致
→ 文档漂移，需要更新（附录 A 已归档，口径以 BDD-1 749 为准）。
EXIT_CODE:0
```

- 实测数字：**1335**（pytest collect-only 口径）
- 基线对比：P0 基线 1308（2026-08-30）+ P3 新增 27 用例（test_check_maintainability.py 14 + test_check_gate_p4_maintainability.py 13）= 1335，**只增不减，精确吻合**
- 判定：**pass**（≥749 迁移基线，且相对 P0 基线只增不减）

## 4. P5_ruff — 静态 lint

- 命令：`timeout 60 ~/.venvs/agate-dev/bin/ruff check agate/scripts/ agate/tests/unit/`
- exit code：**0**
- 输出（全文原样）：

```
All checks passed!
EXIT_CODE:0
```

- 问题清单：无（All checks passed）
- 判定：**pass**

## 5. P5_shellcheck — shell 静态检查

- 命令：`timeout 60 shellcheck -S warning agate/scripts/*.sh`
- exit code：**0**
- 输出：无任何输出（warning 及以上级别零发现，纯防回归通过）
- 问题清单：无
- 判定：**pass**

---

## failed 清单

无失败测试。fail-list.txt 为空文件（0 字节）。

## 预存失败

预存失败：无（全量 1335 用例 collected，1333 passed + 2 skipped，0 failed——与本次改动无关的预存失败不存在）

## test runner 输出签名

pytest 汇总行（全量套件实跑输出原样粘贴，`-q` 模式末行不带等号装饰）：

```
1333 passed, 2 skipped in 150.77s (0:02:30)
```

按 dispatch-context 签名行示例格式即：`====== 1333 passed, 2 skipped in 150.77s (0:02:30) ======`

签名计数块（行首关键词格式，供主 Agent `grep -cE '^(PASSED|FAILED|passed|failed)'` 计数验证；
数值为对上方 pytest runner 原文汇总行的如实转录，非 runner 逐字输出）：

passed: 1333
failed: 0
skipped: 2

说明：errors=0（pytest 输出无 errors 字样即 0）；本文档除上述计数块外，无任何行首 PASSED/FAILED
行——本任务失败测试为零，无需逐条失败签名行（TAG0016 先例的逐条 PASSED 行用于核对无遗漏，
本任务由 count-tests 实测 1335 = 全量 collected 数兜底覆盖完整性）。
