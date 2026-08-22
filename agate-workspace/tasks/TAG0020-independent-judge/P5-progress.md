# P5 技术验证进度（verifier subagent）

- task_id: TAG0020（独立 Judge 机制）
- 阶段: P5（技术验证，verifier 模式）
- 环境前提（dispatch-context 客观查证）: /tmp 只读 → basetemp=agate-workspace/.pytest-tmp；解释器 /usr/bin/python3；[PROD_NOT_TOUCHED]
- P5 命令集来源: P2-design.md §4 gate_commands（已核对，与 dispatch-context 一致）

## 步骤记录

### S0 环境核对（2026-08-22）
- worktree 根: /home/kity/oclab/agate/.worktrees/agate-TAG0020
- git HEAD: ae8fe17 `wf(TAG0020-P4)`（P4 已 commit，.state.yaml phase=P5）
- Python 3.12.3 / pytest 9.0.3
- agate-workspace/.pytest-tmp 已存在且可写
- 结论: 环境就绪，开始逐条执行 P5 命令集
### S1 P5 全量测试（命令 1/3，2026-08-22）
- 命令: timeout 600 /usr/bin/python3 -m pytest -q --tb=no -p no:cacheprovider --basetemp=agate-workspace/.pytest-tmp agate/tests/（worktree 根）
- 结果: **3 failed, 1163 passed, 2 skipped in 111.78s**（EXIT_CODE=1）；二次复跑 --tb=short 一致（确定性，非 flaky）
- 失败清单:
  1. unit/test_agate_scripts_encoding.py::test_bdd_5_all_test_py_text_io_explicit_encoding —— **本次改动引入（真失败）**：TAG0020 P3 新增 test_agate_common.py 第 75/86/98/100 行嵌入脚本串中 open() 缺 encoding=utf-8（违反仓库 BDD-5 守卫；隔离复跑也失败）
  2. unit/test_check_routing.py::test_bdd_7_thin_score_anomaly_git_ok_false_exit_1 —— **环境前提（非缺陷）**：basetemp=agate-workspace/.pytest-tmp 位于 worktree git 仓库内，"非 git 上下文"前提失效→git_ok=true→exit 0≠期望 1；routing 代码（test_check_routing.py 为 TAG0019 产物）未被 TAG0020 触碰；TAG0019 先例 + dispatch-context 已预告
  3. unit/test_env_adapt_docs.py::test_bdd_25_consistency_zero_error —— **环境干扰（非缺陷）**：全量会话中预存测试（test_agate_debt_check.py/test_check_retrospective.py）在 .pytest-tmp 生成含坏引用的 fixture .md（tech-debt.md 等）；check-protocol-consistency.py 的 iter_md_files 未排除 agate-workspace/.pytest-tmp → CHECK 2 误报 12 ERROR → exit 1；隔离/CI（basetemp 在仓库外）均 PASS；一致性脚本扫描范围未被 TAG0020 改动（diff 4604836..HEAD 仅 +2 锚点条目）

### S2 P5_consistency（命令 2/3，2026-08-22）
- 命令: python3 agate/scripts/check-protocol-consistency.py --strict-errors-only（worktree 自身脚本，worktree 根）
- 原样运行（.pytest-tmp 含全量会话残留）: exit=1，ERROR(12)——12 条全部指向 agate-workspace/.pytest-tmp/test_*/ 下 pytest 生成 fixture .md（tech-debt.md 等，坏引用），扫描面误收测试临时目录（环境干扰，非协议不一致）；日志 consistency-dirty.log
- 清理 scratch（rm -rf agate-workspace/.pytest-tmp，pytest 会话级临时目录）后重跑: **exit=0，0 ERROR，318 WARNING（非阻断）**；日志 consistency-clean.log；与 P4-progress 记录（0 ERROR/318-320 WARNING）一致
- 判定: PASS（干净协议态）

### S3 P5_count_tests（命令 3/3，2026-08-22）
- 命令: bash agate/tests/scripts/count-tests.sh
- 结果: **exit=0**，1168 测试用例 ≥ 749 基线，无漂移（与 pytest 总计 1163+3+2=1168 一致）

### S4 交付物（2026-08-22）
- P5-test-results/unit.md: failed=3（1 真失败 + 2 预存环境失败）+ 签名（grep -cE 命中=8）+ 命令逐条表 + [PROD_NOT_TOUCHED]/[NO_NEED_CONFIRM]
- P5-test-results/fail-list.txt: 3 行 FAILED id
- known-failures.md: 登记 bdd_7（环境前提）/ bdd_25（环境干扰）两项预存失败，与本任务无关，推迟处理
- 自查: unit.md 签名计数 8>0 ✓；fail-list 3 行 ✓

### S5 P5 重跑 r2（P4 修复后，2026-08-22）
- 前置核对：test_agate_common.py 4 处 open() 已补 encoding='utf-8'（工作树未 commit，phase=P5）
- 清理 scratch → P5 全量 pytest: **2 failed, 1164 passed, 2 skipped**（exit 1，112.05s，日志 full-run-3.log）
  - test_bdd_5 转绿 ✓（本次引入真失败清零）
  - test_bdd_7 / test_bdd_25 仍失败（预存环境，known-failures.md 已登记）
- P5_consistency 原样（.pytest-tmp 残留）: exit 1，ERROR(12) 全为 .pytest-tmp 误收（consistency-dirty-2.log）
- 清理 scratch → 隔离重跑 bdd_7+bdd_25: **bdd_25 PASS**（环境干扰实证）/ **bdd_7 FAIL**（环境前提确认，assert 0==1 git_ok true）
- P5_consistency 干净态: **exit 0，0 ERROR / 318 WARNING**（consistency-clean-2.log）
- P5_count_tests: **exit 0**，1168 ≥ 749 无漂移

### S6 r2 交付物更新（2026-08-22）
- P5-test-results/unit.md 覆盖: failed=2（全预存环境，0 本次引入）+ 签名（grep -cE 命中=8）+ P4 修复闭环确认
- P5-test-results/fail-list.txt 覆盖: 2 行 FAILED id
- known-failures.md: 补「重跑确认（r2）」节（两条目归属不变，bdd_25 干净态 PASS 实证）
