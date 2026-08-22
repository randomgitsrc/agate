# P5 技术验证结果（TAG0021「协议结构化层 RM-AG0022」）— 重试 #1

- phase: P5（重试 #1，P4 ruff 修复后全量重跑）
- task_id: TAG0021
- agent: verifier
- 日期: 2026-08-22
- 状态标记: [PROD_NOT_TOUCHED]（未接触生产环境/主 checkout；只读验证 worktree，未改动任何代码/协议文件）
- 被验证对象: worktree `/home/kity/oclab/agate/.worktrees/agate-TAG0021`（branch feat/TAG0021-structured-layer）
  - HEAD `14aa44f` = P4 实现 commit；**P4 ruff 修复（纯 lint 行为等价重构，8 脚本，111+/83-）位于未提交工作区**（`git status` 可见，均为 agate/scripts/ 下脚本，无协议/文档改动）——本重试各 gate 跑的就是修复后的有效状态
- 判定口径: 2 项 pytest 失败为 P4 已登记环境假象（CAPABILITY_GAP），非本任务回归；ruff 首轮真失败（70 errors）已由 P4 修复，本轮转绿

## 汇总

- **全量 pytest：2 failed, 1198 passed, 2 skipped**（111.94s）——failed 全部 = 已登记环境假象（隔离复跑复核确认，CI 均通过）
- **failed 计数：pytest 2 项（环境假象）**；ruff gate 首轮 70 errors → 本轮 **All checks passed（0 error）**
- 七条 gate_commands 全部执行（非子集）：P5 / P5_consistency / P5_structure / P5_schema / P5_count / P5_platform / P5_ruff

## 逐命令结果签名

| # | gate key | 命令（P2-design §4 原文） | exit | 输出签名 | 判定 |
|---|----------|---------------------------|------|----------|------|
| 1 | P5 | `python3 -m pytest agate/tests/ -q --tb=no -p no:cacheprovider --basetemp=/home/kity/oclab/agate/.worktrees/agate-TAG0021/dist/` | 1 | **2 failed, 1198 passed, 2 skipped in 111.94s**；隔离复跑 test_bdd_7 仍红 + test_bdd_25 转绿 | 红×2 → 环境假象（见归类） |
| 2 | P5_consistency | `python3 agate/scripts/check-protocol-consistency.py --strict-errors-only`（worktree 自己的） | 0 | 0 ERROR，318 WARNING（--strict-errors-only 放行） | ✅ passed |
| 3 | P5_structure | `python3 agate/scripts/check-structure-consistency.py`（worktree 自己的） | 0 | S1-phases/S2-workflow/S3-cards/S4-scripts/S5-schema/S6-references/S0-numbers 全 OK | ✅ passed |
| 4 | P5_schema | `python3 agate/scripts/check-yaml-schema.py` | 0 | SCHEMA-phases / SCHEMA-dispatch / SCHEMA-roles 全 OK | ✅ passed |
| 5 | P5_count | `bash agate/tests/scripts/count-tests.sh` | 0 | 总计 1202 用例 ≥ 749 立项基线（只增不减） | ✅ passed |
| 6 | P5_platform | `python3 agate/scripts/check-platform-assumptions.py` | 0 | 0 命中（BDD-16 平台无关扫描，无新增） | ✅ passed |
| 7 | P5_ruff | `/home/kity/.local/bin/ruff check agate/scripts/ agate/tests/`（ruff 不在 PATH，绝对路径；scope 同 P2 声明） | 0 | **All checks passed**（首轮 70 errors → P4 修复 → 0 error） | ✅ passed |

> P5 命令注：dispatch-context 摘要写 `--tb=line`，P2-design §4 原文为 `--tb=no`；硬约束「用 P2 声明的命令原文」，实测以 `--tb=no` 执行（输出汇总签名一致，均含 passed/failed 计数）。

## 失败归类

### 仅 pytest 2 项，均为环境假象（非真失败、非本任务回归，CI 均通过）——与 P4 登记一致，重试复跑复核确认

**隔离复跑证据**（先清空 dist/ 后单跑两项，`--tb=line`，basetemp=dist/，0.85s）：

```
FAILED agate/tests/unit/test_check_routing.py::test_bdd_7_thin_score_anomaly_git_ok_false_exit_1 (assert 0 == 1)
1 failed, 1 passed
```

- **test_check_routing.py::test_bdd_7_thin_score_anomaly_git_ok_false_exit_1** → **环境假象 [CAPABILITY_GAP]**：沙箱 `--basetemp` 必须在 git 仓库内（/tmp、ptmp 只读，P0-brief/P2 env_constraints 实证）→ 任务临时目录落在仓库内 → git 通道可用 → `git_ok:true` 破坏"git_ok:false → exit 1"预期。**隔离复跑仍红**（该语义随沙箱路径约束固有，P4 已登记 CAPABILITY_GAP，与本任务改动零耦合——check-routing/agate-risk-score 未被触碰）。CI basetemp=/tmp 在仓库外 → 通过。
- **test_env_adapt_docs.py::test_bdd_25_consistency_zero_error** → **环境假象（共享 basetemp 污染）**：全量序下 dist/ 内其他测试产物 md 被 `rglob("*.md")` 一致性扫描纳入 → CHECK 2 ERROR；**清空 dist/ 后隔离复跑通过（转绿）** → 确认为共享 basetemp 污染问题（记入本 unit.md），非代码缺陷。CI /tmp 在仓库外 → 无此污染，通过。

### ruff：首轮真失败已修复，本轮 passed

- 首轮（重试前）：`Found 70 errors`（exit 1），全落 TAG0021 diff 涉及的 8 个脚本（check-structure-consistency 26 / check-yaml-schema 20 / check-gate 10 / agate_common 6 / check-pruning 5 / agate-next-card 1 / agate-read-gate-commands 1 / pre-commit-gate 1；UP031/RUF100/E731/PLW0603/I001/W292/F401/SIM102），main 基线（9557b29）同 scope 0 error → 真失败，主 Agent 回 P4。
- P4 修复（纯 lint 行为等价重构，grep 复核 8 脚本 111+/83-，无任何非脚本文件改动）后，本轮同 scope 同 ruff（0.15.18）实测 **`All checks passed`（exit 0）**——70 errors → 0。

### 预存失败（known-failures.md）

- **无**。2 项 pytest 红为沙箱环境假象（CI 通过），非改动前就存在的代码库失败，故不创建 known-failures.md（派发指引允许以 unit.md 标注替代）。

## 测试全量性声明

- ✅ 全量 pytest 已执行（gate_commands.P5 本身即全量套件，非子集）；1202 collect / 1198 passed / 2 failed / 2 skipped。
- pytest 汇总行（passed/failed 计数）已实录于本文件（上方签名行），供主 Agent grep 校验。
- `[PROD_NOT_TOUCHED]`：全程只读 worktree 代码/协议；唯一写操作 = P5-test-results/（含命令输出 trace：pytest-full-retry1.txt / consistency-retry1.txt / structure-retry1.txt / schema-retry1.txt / count-retry1.txt / platform-retry1.txt / ruff-retry1.txt）+ P5-progress.md（追加）。

## 附：gate 判定汇总（主 Agent 视角）

- ✅ 通过：P5_consistency（0 ERROR）/ P5_structure（S 全 OK）/ P5_schema（全 OK）/ P5_count（1202≥749）/ P5_platform（0 命中）/ **P5_ruff（All checks passed）**
- ⚠️ P5 pytest exit 1：2 failed 均为**已证实环境假象**（test_bdd_7 CAPABILITY_GAP 固有 + test_bdd_25 共享 basetemp 污染，隔离复跑复核一致；CI /tmp 在仓库外均通过）——放行依据沿用 P4 登记，由主 Agent 定夺推进。
- 与首轮差异：ruff 由❌（70 errors 真失败）→ ✅（All checks passed）；其余六条结果与首轮一致（pytest 2 环境假象无变化）。