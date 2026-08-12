---
phase: P5
task_id: TAG0001
type: test-results
parent: P2-design.md
trace_id: TAG0001-P5-20260813
agent: verifier
---

# TAG0001 — P5 技术验证结果（gate_commands.P5 全量）

> 角色：verifier（P5 模式）。执行环境：worktree `/home/kity/oclab/agate/.worktrees/agate-dev`，从仓库根执行。
> 验证对象：worktree `agate/`（TAG0001 P4 实现，HEAD=006c3e6）。
> 环境标记：`[PROD_NOT_TOUCHED]`——本次仅只读验证 + bats 临时目录，未触碰 `~/.agate`、未修改任何 `agate/` 文件。

## 0. 结论摘要

| 命令 | 结果 | 说明 |
|---|---|---|
| 全量 bats（gate_commands.P5） | **1 次 flaky 失败 / 4 次全量级运行** | `test_bdd_15_real_retreat_records_fixture_reproducible` 偶发红（1/4 全量运行；3 次全量绿 + 单文件/单目录绿）。根因已定位为 **TAG0001 新交付代码的边界 bug**（详见 §2），非预存失败、非环境问题。 |
| consistency | 0 ERROR（exit 0） | CHECK 1/2/3/4/6/7/8/9 全 PASS，含新 check-debt.sh CHECK 9 锚点 |
| shellcheck | 0 error（exit 0） | `shellcheck -S warning agate/scripts/*.sh` |
| count-tests | 676（exit 0） | 670（unit/regression/integration）+ 6（sanity）；`agate-debt-check.bats` 20 个 @test 计入 |

**failed 计数：1**（flaky，详见 §2）。主 Agent 需判定：test_bdd_15 偶发失败根因是 P4 交付代码 `agate-debt-check.py::serialize_evidence` 的 YAML int 边界——按 P5 卡片「真 bug → 回 P4 修复」处理，或先登记 flaky。

## 1. 全量 bats（gate_commands.P5）

命令（worktree 根执行）：
```bash
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
```

运行记录（4 次全量级 + 2 次子集复跑）：

| # | 范围 | 命令 | exit | ok | not ok | 备注 |
|---|---|---|---|---|---|---|
| R1 | 全量 | 上述 | 0 | 676 | 0 | 首次运行 |
| R2 | 全量 | 上述 | 1 | 675 | **1** | `not ok 47 test_bdd_15_...` |
| R3 | 全量 | 上述 | 0 | 676 | 0 | 复跑确认 |
| R4 | 全量（重排） | unit/ 前置 | 0 | 676 | 0 | 排除文件顺序依赖 |
| R5 | 单文件 | `bats agate/tests/unit/agate-debt-check.bats` | 0 | 20 | 0 | 隔离复跑绿 |
| R6 | 单目录 | `bats agate/tests/unit/`（3 次） | 0 | 全绿 | 0 | 3/3 绿 |

- 测试输出签名：`ok N` 行（R2 为 675，绿跑为 676），`not ok` 行（仅 R2 为 1），正常 skip 2（含于 ok 行）。
- 通过总数：676（unit 632 + regression 17 + integration 21 + sanity 6；skip 计 2）。

## 2. 失败项与根因分析（test_bdd_15，flaky）

**失败 id**：`test_bdd_15_real_retreat_records_fixture_reproducible`（`agate/tests/unit/agate-debt-check.bats:475-534`）
**失败断言**：L533 `[[ "$output" != *"GATE DEBT WARNING"* ]]`——回退覆盖比对方向 B（条目已建且 evidence 引用提交哈希）误报 WARNING。

**根因（已实测定界，属 TAG0001 交付代码缺陷，非测试问题）**：
1. 测试用 `s2=$(git -C "$repo" rev-parse --short HEAD~1)` 生成 7 位短哈希，写入 DEBT-R2 的 `evidence: - path: 7008516`（**全数字** hex）。
2. `agate-debt-check.py` 的 `yaml.safe_load` 把 `7008516` 解析为 **`int`**（全数字标量），而非 str。
3. `serialize_evidence()`（`agate-debt-check.py:64-76`）只拼接 `isinstance(v, str)` 的 path/note/ref 值 → **int 被丢弃** → `--covered-hashes` 提取不到该哈希 → `check-debt.sh --retreat-coverage`（`check-debt.sh:45`）判定未覆盖 → 误报 `GATE DEBT WARNING`。
4. 复现概率 = 短哈希 7 位全为数字 ≈ (10/16)^7 ≈ 0.74%/哈希，两条哈希约 1.4%/次运行——与 1/4 全量运行观察到的一致。独立 200/500 次循环复现脚本在固定日期的确定性输入下成功复现（ITER 19，s2=7008516），且输出 `--covered-hashes` 仅含 `ad90aca` 缺 `7008516`，证实 int 丢弃路径。

**影响面**：`--retreat-coverage` 对「evidence 引用全数字哈希」的条目漏提取覆盖集合 → 对已登记的回退债误报「未登记」WARNING。schema 校验模式（FILE）不受影响（evidence 非空 list 校验通过，int 值不触发类型错误，因为 `evidence` 是 list 容器非 str 字段）。closed 准入的 P5/P6 引用若引用全数字哈希同样会被 `serialize_evidence` 丢弃——建议 P4 修复 `serialize_evidence` 对 int（及数字 str）做 `str()` 归一。

**处置建议**：这是**本任务引入的缺陷**（非预存失败、非环境问题）——按 P5 判定规则「真 bug → 回 P4 修复」处理；修复后重跑 gate_commands.P5 全量。若主 Agent 选择容忍 flaky，须登记 known-failures.md 并在 CI 中可观测。

## 3. consistency（gate_commands.P5 补充）

命令：`python3 agate/scripts/check-protocol-consistency.py`
结果：**exit 0，0 ERROR**（CHECK 1/2/3/4/6/7/8/9 全 PASS，含 CHECK 9 新 `check-debt.sh` 锚点）。
输出签名：`🎉 全部检查通过，协议结构一致性无问题。`

## 4. shellcheck（gate_commands.P5 补充）

命令：`shellcheck -S warning agate/scripts/*.sh`
结果：**exit 0，0 error**（含新 `check-debt.sh`）。

## 5. count-tests（gate_commands.P5 补充）

命令：`bash agate/tests/scripts/count-tests.sh`
结果：**exit 0，总计 670 个测试用例**（unit/regression/integration）+ sanity 6 = **676**，与 P2 §8「654 既有 + 22 新增」基线一致；`agate-debt-check.bats` 20 个 @test 已计入。无文档漂移提示。

## 6. 环境与隔离

- `[PROD_NOT_TOUCHED]`——验证全程仅读文件 + bats/mktemp 临时目录；未改任何 `agate/` 文件、未动 `~/.agate`（稳定版 v0.40.2 开发工具）。
- 全量 bats 从 worktree 根执行（`bats agate/tests/...`），未 cd 进 `agate/tests`（consistency `--root` 默认当前目录）。
- 无 `[NEED_CONFIRM]` 项，无不可逆操作。

## 7. 预存失败说明

未观察到 ARCH.4（agate-archive-stale-outputs.bats）flaky——4 次全量级运行 ARCH.4 均绿。唯一失败 test_bdd_15 为本任务新交付代码缺陷（§2），**不属于预存失败**。
