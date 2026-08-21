# P5-progress.md — TAG0019-risk-routing (verifier)

> 逐条落盘关键步骤。产出路径：`{AGATE_WORKSPACE}/tasks/TAG0019-risk-routing/P5-test-results/`
> [PROD_NOT_TOUCHED]

## 输入文件确认
- [x] dispatch-context（P5-dispatch-context-verifier.md）已读：4 条命令集 + I1 环境前提
- [x] verifier.md 角色已读（P5 模式）
- [x] P0-brief.md 已读（env_constraints：/tmp 只读 → --basetemp + -p no:cacheprovider）
- [x] P2-design.md gate_commands.P5 已核对（§4）：P5 / P5_consistency / P5_platform / P5_count_tests
- [x] AGENTS.md 项目约定已读（worktree + 主 checkout 双工作区）

## 命令执行记录

### CMD1: P5 全量测试（worktree 根，`python3 -m pytest -q --tb=no -p no:cacheprovider --basetemp=/home/kity/oclab/agate/.ptmp-scratch agate/tests/`，timeout 300s）
- 结果: **3 failed, 1097 passed, 2 skipped**，EXIT_CODE=1，耗时 103.85s
- failed 清单：
  1. `test_check_routing.py::test_bdd_7_thin_score_anomaly_git_ok_false_exit_1` → **环境前提 I1**（dispatch-context 客观查证：沙箱无可写 basetemp 在 git 仓库外 → run_git 必成功；实现已两轮 GIT_DIR=/nonexistent 探针验证 git_ok:false + thin → exit 1 fail-closed，非缺陷）
  2. `test_protocol_alignment_review.py::test_sg_6_check9_anchor_table_covers_all_gate_scripts` → **本任务引入**：新增 `check-routing.py` 未同步进 check-protocol-consistency.py CHECK 9 锚点表（断言输出：`FAIL: check-routing.py 不在 CHECK 9 锚点表中`）；改动前无 check-routing.py 文件，锚点表必然全覆盖 → 预存不可能，属本任务同步缺失
  3. `test_check_platform_assumptions.py::test_bdd_8_clean_tree_zero_detection` → **本任务引入**：tests/ 全树扫描 returncode=1，唯一命中 `test_docs_assertions.py:3` 注释含 `/tmp` 字面量触发 R4（`/tmp([\s/\"']|$)`）；test_docs_assertions.py 为主 checkout 不存在的**本任务 P3 新增文件** → 属本任务文件引入命中（注释误报性质，但 bdd-8 零命中验收被破坏）
- 结论：无预存失败；3 failed = 1 环境前提（I1，非缺陷）+ 2 本任务引入（真失败候选，回 P4 判定交主 Agent）

### CMD2: P5_consistency（worktree 自己的脚本 `check-protocol-consistency.py --strict-errors-only`，timeout 90s）
- 结果: **0 ERROR，319 WARNING，EXIT_CODE=0 → pass**（--strict-errors-only 仅 ERROR 阻断）
- 佐证：输出含 WARNING `gate 脚本 agate/scripts/check-routing.py 未纳入 CHECK 9 锚点表——新增 gate 脚本需在 SCRIPT_ALIGNMENT_ANCHORS 加对应锚点` → 与 CMD1 #2 test_sg_6 同源，确认锚点表遗漏为真实（consistency WARNING 级不阻断，集成测试硬断言级失败）

### CMD3: P5_platform（主 checkout `check-platform-assumptions.py` 扫 7 文件变更集，timeout 90s）
- 结果: **R1-R5 0 命中，EXIT_CODE=0 → pass**（BLK-1 收窄口径：只扫本任务变更文件集；test_docs_assertions.py 不在 7 文件清单，其 /tmp 注释命中由 CMD1 #3 test_bdd_8 单独暴露）

### CMD4: P5_count_tests（`bash agate/tests/scripts/count-tests.sh`，timeout 90s）
- 结果: **总计 1102 个测试用例（≥ 749 基线，只增不减），EXIT_CODE=0 → pass**

## 产出
- [x] `P5-test-results/unit.md`（4 命令汇总 + failed=3 计数 + 签名行 passed/failed + 归因）
- [x] `P5-test-results/fail-list.txt`（3 行 `FAILED ` 前缀 + I1 标注）
- [x] 预存失败 = 0 → 不登记 known-failures.md（P5 卡：只登预存失败）
- [x] basetemp `.ptmp-scratch` 用后清理

## P5 重试轮（P4 修复后，T027 全量重跑）

> 主 Agent 告知：P4 已修复 2 条真失败（check-routing.py 入 CHECK 9 锚点表 / test_docs_assertions.py 注释去 /tmp），2 用例自跑转绿。重跑 4 条命令确认无回归。
> git status 确认：修复在工作树（`M agate/scripts/check-protocol-consistency.py` + `M agate/tests/unit/test_docs_assertions.py`，均未 commit）——验证对象 = 当前工作树状态。

### 重试 CMD1: P5 全量测试（basetemp 同前，timeout 300s）
- 结果: **1 failed, 1099 passed, 2 skipped**，EXIT_CODE=1，102.63s
- 对比前次（3 failed / 1097 passed）：前 2 条真失败转绿（test_sg_6 / test_bdd_8），passed +2，无回归
- 唯一剩余 failed：`test_bdd_7_thin_score_anomaly_git_ok_false_exit_1` = 环境前提 I1（非缺陷，同前判定）

### 重试 CMD2: P5_consistency（worktree 脚本，timeout 90s）
- 结果: **0 ERROR，318 WARNING，EXIT_CODE=0 → pass**；前次"check-routing.py 未纳入 CHECK 9 锚点表"WARNING 已消失（修复生效，319→318）

### 重试 CMD3: P5_platform（7 文件变更集，timeout 90s）
- 结果: **R1-R5 0 命中，EXIT_CODE=0 → pass**

### 重试 CMD4: P5_count_tests（timeout 90s）
- 结果: **1102 用例（≥ 749），EXIT_CODE=0 → pass**

## 重试轮产出
- [x] `P5-test-results/unit.md` 覆盖更新（重试轮结果：failed=1 全为 I1）
- [x] `P5-test-results/fail-list.txt` 覆盖更新（仅 1 条 + I1 标注）
- [x] basetemp `.ptmp-scratch` 用后清理