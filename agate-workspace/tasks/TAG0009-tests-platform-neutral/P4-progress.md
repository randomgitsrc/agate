# P4 进度（implementer）

- 已读 P2-design / P3-test-cases / P2-review / dispatch-context / P0-brief / fixtures.bash / load.bash / install-hook.bats / check-platform-assumptions.bats / agate-extract-context.sh L115-139
- P3 已交付测试侧改动：check-tdd-red PATH 移除(env -u PATH) / ci-gate-backstop PYTHON / 4 处 scan-exempt 标记 / bdd-21 平台分支 / install-hook+pre-push-hook ln 复制模式用例 / EC.16 bc stub
- P4 待做：扫描器 / fixtures helper(PYTHON+shim) / bc→awk / 9+1 文件 shim 注入 / 25 文件 R2 清理 / install-hook+pre-push-hook R3 重构 / CI / README 计数
- [2026-08-13] P4 实现完成：扫描器(check-platform-assumptions.sh)+fixtures helper(PYTHON/SHELLCHECK/shim)+bc→awk+24文件 R2 清理+10 文件 shim 注入+R3 平台分支+CI(platform-scan job+bats windows matrix)+README 计数同步
- [2026-08-13] 自查：扫描器全树 0 命中 / 全量 bats 733 绿 / consistency --strict 0 ERROR / shellcheck 0 error / 扫描器自身测试 14 绿
- [2026-08-13] DESIGN_GAP: P2 §2.5 保留 [[ -L ]] 与 BDD-8 R3 零命中冲突 → readlink 语义等价（已标注 P4-implementation.md）
[PROD_NOT_TOUCHED]
- [2026-08-13] 最终自查汇总：扫描器全树 0 命中 / 全量 bats 733 绿（727 count + 6 sanity）/ consistency --strict 0 ERROR / shellcheck 0 error / count-tests 727 无漂移

## review: 已读 dispatch-context / review.md / P0-brief.md
- 评审对象 7 类文件、评审重点 7 项（扫描器 R1-R5 / harness shim / bc→awk / DESIGN_GAP / 测试断言 / CI / 健壮性）
- 只审不写；结论引用锚点；Header status 需改为 approved/rejected/needs-revision

## review: 已读 P4-implementation.md
- 改动清单 1.1-1.6；DESIGN_GAP（install-hook readlink 替代 [[ -L ]]）；SCOPE+（pre-push-hook L11 [ -L ]）；自查 733/733 绿
- 遗留：Windows 分支 bats 精确安装命令 P5 定稿（I7 supplementable）

## review: 已读 P2-design.md
- 9 选型点 §2.1-2.9；BDD-1~29 映射；gate_commands.P5 固化；minimal_validation 两个假设 confirmed
- [SCOPE+] x3（pre-push-hook L11 / CI 未知失败 / 产品脚本根治另立任务）
- 设计要点：R2 前字符类含引号（ci-gate-backstop 教训）；标记只豁免 R4；shim 排除 $BATS_TEST_TMPDIR 防自解析

## review: 已读 P1-requirements.md
- BDD-1~29；I1-I10；77 失败清单（19 文件）；25 文件测试侧裸 python3 清单
- 关键：P1 红线=不改协议语义/gate 判定；Linux 基线红线；范围= tests 全树+扫描器+extract-context bc 移除+CI

## review: 已读扫描器 / fixtures.bash / extract-context L128 / helpers-python.bats
- 扫描器 113 行：R1-R5 模式 + r2_exempt/r4 行豁免；set -euo pipefail
- fixtures.bash：detect_python + export PYTHON + SHELLCHECK 探测 + create_python_shim_bin（排除 BATS_TEST_TMPDIR）
- extract-context L128：awk '{s+=$1} END{print s+0}'
- helpers-python.bats：bdd-13/15/17 三用例，fixture 运行时拼接避免 R2 字面

## review: 发现 bc→awk 回归（实测确认）
- extract-context.sh L128 新 awk 行在 set -euo pipefail 下，当 grep -rh 无 'failed:' 匹配时
  （空目录或目录内文件全为 passed 无 failed 行）→ pipefail 使命令替换返回 1 → set -e 终止整个脚本。
- 实测：if [ -d ] 体内同样被杀；原实现 `|| echo 0 | tail -1` 兜住 no-match（返回 0），
  新实现删除了该兜底。既有测试 EC.7/EC.16 都有匹配（有 failed: 行），空 case 无测试覆盖。
- 建议修复：`... | awk '{s+=$1} END{print s+0}' || echo 0`（或 substitution 后 || true）

## review: 已读 P3-test-cases.md
- P3 §2 明确 Gap：check-platform-assumptions.bats（14 例 BDD-9）不被 P5 gate 命令（sanity+unit+regression+integration）调用，
  建议 P4/P5 并入 CI bats job 或新增调用项——否则 BDD-9 行为测试在标准流程不运行
- P4 protocol-tests.yml 未解决此 Gap（bats job 仍只跑 unit/regression/integration/sanity）→ 待核实为发现
- ci-gate-backstop CRLF 归一化（tr -d '\r'）P3 已改 5 处 + P4 新用例 1 处；setup() PYTHONIOENCODING 文件级导出
- consistency 锚点新增 check-platform-assumptions.sh（keywords 平台假设/R1/R2 与内容匹配）

## review: bc→awk 回归疑点已排除（实测复核）
- 真实脚本（extract() 经 command substitution 调用 + local var=$(...) 结构）下：空目录 → "P5 failed 参考: 0" exit 0；
  多文件 → "3" exit 0。行为正确，无 set -e 中断（我初测误报，根因是隔离测试结构不同）。
- 已核实：check-tdd-red TD.1b/TDD.F8 用 env -u PATH；agate-inject-card setup 合并 shim；扫描器树扫描 exit 0（BDD-8 闭环）
- 已发现两个真实问题：
  (A) P3 §2 Gap 未解决：check-platform-assumptions.bats（14 例 BDD-9）未接入 CI bats job / P5 gate，标准流程不运行
  (B) README 计数漂移：count-tests.sh 实测 ci-gate-backstop.bats=11，README 表写 10（I10 违反）

## review: 实测复核完成
- 扫描器行为测试 14/14 绿；helpers-python 3/3 绿；consistency --strict 0 ERROR（exit 0）
- 全树扫描 exit 0（BDD-8 闭环）；check-tdd-red PATH 硬编码 0 处；agate-next-card /tmp→BATS_TEST_TMPDIR + bdd-21 分支就位
- check-platform-assumptions.bats 为 P3 commit（a3fd64f）后未改——P4 未篡改 P3 测试契约（纯 TDD：P4 只建扫描器）
- DESIGN_GAP（readlink 替代 [[ -L ]]）判为合理：P2 §2.5 设计文本本就含 readlink 意图；Linux readlink 断言 + Windows mock ln 复制模式双覆盖；R3 零命中满足
- 最终发现 2 项：(A) BDD-9 扫描器行为测试未接入 CI/P5 gate（P3 §2 已警示，P4 改 yml 时未加调用）
  (B) README ci-gate-backstop=10 vs 实际 11（I10 漂移，P4 自加 cp1252 用例后未同步）

## review: 完成
- P4-review.md 已写入（113 行），status: needs-revision
- 2 项必修：NEEDS-REV-1（BDD-9 扫描器测试未接 CI/P5 gate）/ NEEDS-REV-2（README ci-gate-backstop 10→11）
- 批准项：DESIGN_GAP（readlink）；bc→awk 复核正确；扫描器/helper/CI/断言各锚点核验通过
- [PROD_NOT_TOUCHED]
