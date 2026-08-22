---
phase: P5
task_id: TAG0019
type: verification
agent: verifier
created: 2026-08-21
updated: 2026-08-21（P8 发布前重跑轮，audit7 reuse_blocked → 完整重跑）
---

# P5-test-results — unit.md（TAG0019-risk-routing）

> P5 技术验证：P2-design.md gate_commands.P5 四条命令执行结果汇总（**P8 发布前重跑轮**：audit7 判定 reuse_blocked，P7→P8 有发布文件改动 → 按 P8 卡完整重跑）。验证对象 = HEAD `44ed200`（P8 release commit，tag v0.58.0 已建已推）。
> 环境：worktree `/home/kity/oclab/agate/.worktrees/agate-TAG0019`；解释器 `/usr/bin/python3`；basetemp `/home/kity/oclab/agate/.ptmp-scratch`（可写；/tmp 与 ptmp 只读 Errno30）。
> [PROD_NOT_TOUCHED]　[NO_NEED_CONFIRM]（P5 无数据删除/迁移等不可逆操作）

## 运行签名（pytest 汇总，供主 Agent grep 校验）

passed: 1099
failed: 1
skipped: 2

## 四条命令逐条结果（P8 重跑轮）

| 命令 | 结果 | exit | 备注 |
|------|------|------|------|
| P5 全量测试（`agate/tests/`，`-q --tb=no -p no:cacheprovider --basetemp=...`，timeout 300s） | **FAIL** | 1 | 1 failed / 1099 passed / 2 skipped，105.74s；与重试轮完全一致（passed 1099），无回归 |
| P5_consistency（worktree 自己的 `check-protocol-consistency.py --strict-errors-only`） | **PASS** | 0 | 0 ERROR，318 WARNING；**CHECK 7（badge vs git tag）✅ PASS**——tag v0.58.0 时序正确 |
| P5_platform（`check-platform-assumptions.py` 扫 7 文件变更集） | **PASS** | 0 | 变更文件集 R1-R5 0 命中（BLK-1 口径） |
| P5_count_tests（`bash agate/tests/scripts/count-tests.sh`） | **PASS** | 0 | 总计 1102 用例 ≥ 749 基线，只增不减 |

## failed 计数

- **failed = 1**（环境前提 I1，非缺陷；本任务引入 = 0）
- **预存失败 = 0**（无改动前即存在的失败，不登记 known-failures.md）

## failed 清单 + 归因（详见 fail-list.txt）

1. `test_check_routing.py::test_bdd_7_thin_score_anomaly_git_ok_false_exit_1`
   - **环境前提 I1**（非缺陷）：设计意图在"非 git 上下文"触发 git_ok:false，但本沙箱可写 basetemp 全在 git 仓库内 → `run_git` 必成功（exit 0 而非 1）。实现已两轮 `GIT_DIR=/nonexistent` 探针验证 git_ok:false + thin → exit 1 fail-closed 正确，非实现缺陷。三轮 P5 中该用例持续为唯一失败，性质恒定。

## 回归确认（三轮一致性）

- P5 首次：3 failed（2 本任务引入 + 1 I1）→ P4 修复后重试轮：1 failed（I1）→ P8 轮：1 failed（I1），passed 恒为 1099，无回归。
- `test_sg_6_check9`（锚点表）与 `test_bdd_8_clean_tree`（/tmp 注释）修复后持续转绿。
- CHECK 7（README badge vs git tag v0.58.0）本轮 ✅ PASS——bump 后 tag 已建，时序正确（此前 bump 后 tag 未建的误报场景不再发生）。

## 附注

- 全量测试覆盖 `agate/tests/` 全部子目录（unit / regression / integration / scripts / sanity）。
- P5 不可逆操作：无。`[NO_NEED_CONFIRM]`。
- 判定权归属：本文件只产出验证结果（exit code 客观事实），READY/发布判定由主 Agent 执行。