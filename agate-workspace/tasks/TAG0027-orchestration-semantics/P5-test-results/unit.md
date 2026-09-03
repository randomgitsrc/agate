# P5 技术验证结果 — TAG0027 编排语义统一落地（RM-AG0054）

- 验证模式：只读技术验证（不修代码 / 不启动服务 / 不做 git 写操作）→ [PROD_NOT_TOUCHED]
- 执行目录：/home/kity/oclab/agateon/.worktrees/agate-TAG0027（worktree 根，HEAD fcf3fd2 = P4 实现 commit）
- 执行方式：P2-design §4.1 gate_commands.P5 7 键逐条独立执行（每条独立 bash 调用，无 && 链，各自 timeout）；全量 pytest `-n auto` 单次跑完（44.88s < 600s timeout），未分片
- 说明：P2 声明的 `--reruns 1 -n auto` 因本环境无 pytest-rerunfailures 插件，按 dispatch-context 指引改用 `-n auto` 并行（与 CI 同口径）；本次并行无偶发 sha256 漂移，无需串行复核
- **failed 计数：failed=0**（其中预存失败 0）
- 命令结果总览：P5=0 / P5_consistency=0 / P5_structure=0 / P5_schema=0 / P5_shellcheck=0 / P5_counttests=0 / P5_selfgate=0（**7/7 exit 0**）
- 签名行（N5 grep 口径，顶格行）：见下节「签名行」

---

## 签名行（N5 校验）

passed 1381, skipped 2, failed 0（pytest 实际输出 "1381 passed, 2 skipped in 44.88s" 的汇总事实重述）

---

## 1. P5 — 全量 pytest

- 命令：`timeout 600s python3 -m pytest agate/tests/ -q --tb=no -n auto`（worktree 根）
- exit code：**0**
- 耗时：44.88s，未超 600s 上限
- 输出尾部（最后 3 行原样）：

```
.......................................                                                          [100%]
1381 passed, 2 skipped in 44.88s
PYTEST_EXIT=0
```

- failed 计数：**0**（1381 passed + 2 skipped，与 P4 基线完全一致，无新增失败、无预存失败）
- 判定：**pass**（exit 0 + failed=0）

## 2. P5_consistency — 协议一致性（worktree 脚本）

- 命令：`timeout 120s python3 agate/scripts/check-protocol-consistency.py --strict-errors-only`（worktree 自己的脚本，符合 dogfooding 约定）
- exit code：**0**
- 输出尾部（汇总行原样）：

```
  仅有 324 个 WARNING，无 ERROR。

CONSISTENCY_EXIT=0
```

- ERROR 计数：**0**；WARNING 计数：**324**（全部为"引用的文件不存在（叙事文件，可能是引述旧问题）"类历史叙事 WARNING，非本任务引入；`--strict-errors-only` 只按 ERROR 判失败）
- 判定：**pass**（0 ERROR）

## 3. P5_structure — 结构一致性（worktree 脚本）

- 命令：`timeout 120s python3 agate/scripts/check-structure-consistency.py`
- exit code：**0**
- 输出（原样）：

```
S1-phases: OK
S2-workflow: OK
S3-cards: OK
S4-scripts: OK
S5-schema: OK
S6-references: OK
S0-numbers: OK
STRUCTURE_EXIT=0
```

- 判定：**pass**（S0–S6 全 OK；S-1/S-2 转移表加列扩展一致性 gate 通过）

## 4. P5_schema — YAML Schema 校验

- 命令：`timeout 60s python3 agate/scripts/check-yaml-schema.py agate/rules/phases.yaml`
- exit code：**0**
- 输出（原样）：

```
SCHEMA-phases: OK
SCHEMA-dispatch: OK
SCHEMA-roles: OK
SCHEMA_EXIT=0
```

- 判定：**pass**（phases.yaml next/retreat/gate_subphase/gate_pass_exit 字段过 schema 校验）

## 5. P5_shellcheck — shell 脚本静态检查

- 命令：`timeout 60s shellcheck agate/scripts/*.sh`
- exit code：**0**
- 输出：无（零告警）
- 判定：**pass**

## 6. P5_counttests — 用例数自检

- 命令：`timeout 180s bash agate/tests/scripts/count-tests.sh`
- exit code：**0**
- 输出尾部（汇总行原样）：

```
总计：1383 个测试用例（pytest collect-only 口径）

目标：≥ 749（TAG0011 迁移基线，BDD-1）；迁移期数值单调逼近 749。
COUNTTESTS_EXIT=0
```

- 判定：**pass**（collect 1383 = 1381 passed + 2 skipped，与 pytest 运行口径一致，用例数未漂移）

## 7. P5_selfgate — 稳定版一致性（self-gate 双面）

- 命令：`timeout 120s python3 ~/.agate/scripts/check-protocol-consistency.py --strict-errors-only`（~/.agate 稳定版，验证稳定版不被本任务破坏）
- exit code：**0**
- 输出尾部（汇总行原样）：

```
  仅有 324 个 WARNING，无 ERROR。

SELFGATE_EXIT=0
```

- ERROR 计数：**0**；WARNING 计数：**324**（同上，历史叙事 WARNING，非本任务引入）
- 判定：**pass**（0 ERROR——worktree 改动未破坏稳定版一致性）

---

## 汇总

- 7/7 条 gate_commands.P5 命令 exit 0，failed=0，无预存失败、无新增失败、无 flaky 需登记
- 测试输出签名行（N5 校验 grep 计数）：
  - `1381 passed, 2 skipped in 44.88s`（pytest 汇总行）
  - `PYTEST_EXIT=0` / `CONSISTENCY_EXIT=0` / `STRUCTURE_EXIT=0` / `SCHEMA_EXIT=0` / `SHELLCHECK_EXIT=0` / `COUNTTESTS_EXIT=0` / `SELFGATE_EXIT=0`（各命令 exit code 行）
  - 签名行 grep 计数 >0（pytest passed/failed 行 + 7 条 exit 行）→ 产出有效
- [PROD_NOT_TOUCHED]（未触发任何生产环境触达；纯只读技术验证）
- [NO_NEED_CONFIRM]（无数据删除/迁移类不可逆操作）
