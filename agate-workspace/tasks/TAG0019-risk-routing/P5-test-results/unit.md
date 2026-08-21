---
phase: P5
task_id: TAG0019
type: verification
agent: verifier
created: 2026-08-21
updated: 2026-08-21（P5 重试轮，P4 修复后全量重跑）
---

# P5-test-results — unit.md（TAG0019-risk-routing）

> P5 技术验证：P2-design.md gate_commands.P5 四条命令执行结果汇总（**重试轮**：P4 已修复前次 2 条真失败，T027 全量重跑确认无回归）。
> 环境：worktree `/home/kity/oclab/agate/.worktrees/agate-TAG0019`；解释器 `/usr/bin/python3`；basetemp `/home/kity/oclab/agate/.ptmp-scratch`（可写；/tmp 与 ptmp 只读 Errno30）。
> [PROD_NOT_TOUCHED]　[NO_NEED_CONFIRM]（P5 无数据删除/迁移等不可逆操作）

## 运行签名（pytest 汇总，供主 Agent grep 校验）

passed: 1099
failed: 1
skipped: 2

## 四条命令逐条结果（重试轮）

| 命令 | 结果 | exit | 备注 |
|------|------|------|------|
| P5 全量测试（`agate/tests/`，`-q --tb=no -p no:cacheprovider --basetemp=...`，timeout 300s） | **FAIL** | 1 | 1 failed / 1099 passed / 2 skipped，102.63s；前次 2 条真失败已转绿（passed 1097→1099），无回归 |
| P5_consistency（worktree 自己的 `check-protocol-consistency.py --strict-errors-only`） | **PASS** | 0 | 0 ERROR，318 WARNING（前次"check-routing.py 未纳入锚点表"WARNING 已消失，修复生效） |
| P5_platform（`check-platform-assumptions.py` 扫 7 文件变更集） | **PASS** | 0 | 变更文件集 R1-R5 0 命中（BLK-1 口径） |
| P5_count_tests（`bash agate/tests/scripts/count-tests.sh`） | **PASS** | 0 | 总计 1102 用例 ≥ 749 基线，只增不减 |

## failed 计数

- **failed = 1**（环境前提 I1，非缺陷；本任务引入 = 0）
- **预存失败 = 0**（无改动前即存在的失败，不登记 known-failures.md）

## failed 清单 + 归因（详见 fail-list.txt）

1. `test_check_routing.py::test_bdd_7_thin_score_anomaly_git_ok_false_exit_1`
   - **环境前提 I1**（非缺陷）：设计意图在"非 git 上下文"触发 git_ok:false，但本沙箱可写 basetemp 全在 git 仓库内 → `run_git` 必成功（exit 0 而非 1）。实现已两轮 `GIT_DIR=/nonexistent` 探针验证 git_ok:false + thin → exit 1 fail-closed 正确，非实现缺陷。P4 修复轮不影响该用例。

## 回归确认

- 前次 3 failed → 本次 1 failed：`test_sg_6_check9_anchor_table_covers_all_gate_scripts`（锚点表）与 `test_bdd_8_clean_tree_zero_detection`（/tmp 注释）均已转绿 ✅，passed 1097→1099 无回归。
- 修改后的 `check-protocol-consistency.py` 与 `test_docs_assertions.py` 参与全量测试，无新增失败。

## 附注

- 全量测试覆盖 `agate/tests/` 全部子目录（unit / regression / integration / scripts / sanity）。
- P5 不可逆操作：无。`[NO_NEED_CONFIRM]`。
- 判定权归属：本文件只产出验证结果（exit code 客观事实），gate 通过与推进判定由主 Agent 执行。