task: "agate 技术债登记闭环（Phase 1-3）：模板 + schema 校验 + 回退强制登记 + P8 确认留痕，用 T001 既有条目回填验证"

known_risks:
  - "技术债登记闭环依赖'主 Agent 自觉'的环节（评审/复盘自愿通道）可能退化——用回退事件强制登记对冲，但自愿通道失效风险仍在"
  - "回退事件召回极低（全仓库历史仅 2 条），该信号只能发现已爆雷的债，无法发现正在腐烂的债（评审 §8.3 诚实标注）"
  - "七态状态机无 gate 强制会僵死——采用三态（open/in_progress/closed）"
  - "如果 P8 的债务确认退化成无脑打勾，该强制应移除（止损条件 4）"
  - "T001 复盘 T1-T4 回填是模板设计的试金石——若回填失败说明模板设计错误"

executor_env:
  platform: "opencode"
  has_task_tool: true
  has_local_runtime: true
  network: "limited"
  git: true

env_constraints:
  debug_env: "bash agate/scripts/check-state-yaml.sh docs/tasks/TAG0001-tech-debt-closure/.state.yaml"
  test_cmd: "bats agate/tests/unit/agate-debt-check.bats"
