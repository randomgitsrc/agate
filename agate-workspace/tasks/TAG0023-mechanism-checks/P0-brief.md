task: "机制校验补强批（RM-AG0042 + RM-AG0043 + RM-AG0044 合并一个 task）：TAG0019-21 复盘独立评审（2026-08-23 approved）确认的 3 个 agate 机制缺口，同属'gate/校验补强'簇（check-gate/check-state-transition/测试卫生），合并一个 task。复盘：dsh-workspace/agate-research/retrospective-tag0019-21.md"

issues:
  - "RM-AG0042 门槛失败事件强制记录 retries：四任务 .state.yaml retries 全为 {}（评审拒-修-批 3+1 轮、P5→P4 回退 3 次、子代理空返回均未记录）；check-state-transition.py 有重试上限机制（retries_over → PAUSED，L146-154）但无任何检查强制'门槛失败事件必须记录进 retries'——记录自选，不记录则 MAX_RETRY→PAUSED 被静默绕过。修复=①gate 校验 retries 与门槛失败事件对应性（失败事件存在而 retries 为空 → 阻断/高优 WARNING）②P1/P2 卡明确评审被拒须写 retries；验收锚=新任务评审 rejected 后 retries 必有对应条目"
  - "RM-AG0043 P8 roadmap 回写 done 校验：RM-AG0032（独立 Judge）v0.59.0 已发布、PR #184 已合并，但 roadmap 至今无 done 行（记录缺口实证）；check-gate.py P8 无任何 roadmap 回写 done 校验。修复=①P8 gate 增加 roadmap 校验（按 task_id 反查关联 RM 条目状态必须 done）②补记 RM-AG0032 → done（历史数据修正）；验收锚=新任务 P8 后 roadmap RM 自动 done"
  - "RM-AG0044 环境敏感测试集中治理：第三例 test_bdd_14（check-debt retreat-coverage）CI flaky 实证——同 commit 双 run 一过一挂、重跑即过、本地 3/3 过；与 RM-0041（test_bdd_7/25 basetemp）同类不同根因（git short-SHA/runner 环境）。修复=①排查 check-debt.py --retreat-coverage 的 git 环境敏感点（short SHA 比较确定性）②建立环境敏感测试判定标准+集中清单+CI flaky 自动重跑机制；验收锚=test_bdd_14 连续 5 次 CI 稳定 + 环境敏感测试集中清单"

known_risks:
  - "改动面：check-gate.py / check-state-transition.py / P1/P2 卡 / P8 卡 / check-debt.py / CI 配置 / 测试 → 触发 SELF-GATE"
  - "RM-0042 的'门槛失败事件判定'需定义事件源（评审 status=rejected、P5→P4 回退证据、subagent 空返回记录）——P2 需设计可机器判定的对应性规则，避免误报"
  - "RM-0043 的 roadmap 反查需处理历史 RM（done 但无 task 关联）与多 RM 关联一个 task 的情况——P2 需定义匹配规则"
  - "RM-0044 的 flaky 根治可能牵出 check-debt.py 的 git 环境假设（short SHA/runner git config）——P1 需先复现定位根因再定 BDD"
  - "【强制要求】同类扫描：grep retries 全部消费点（check-state-transition/state-machine/check-gate）；grep roadmap 回写消费点（check-gate P8/state-machine/check-retrospective）；grep 环境敏感测试已知清单（test_bdd_7/25/14 + known-failures 登记）"

executor_env:
  platform: "opencode"
  has_task_tool: true
  has_local_runtime: true
  network: "full"
  git: true

env_constraints:
  debug_env: "本环境为 Linux；/tmp 只读（pytest 需 --basetemp + -p no:cacheprovider）；权限 danger-full-access；ruff 0.16.4（~/.venvs/agate-dev/bin/ruff）"
  test_cmd: "python3 -m pytest agate/tests/；python3 agate/scripts/check-protocol-consistency.py --strict-errors-only；bash agate/tests/scripts/count-tests.sh；~/.venvs/agate-dev/bin/ruff check agate/"
  workspace_path: "{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/"
