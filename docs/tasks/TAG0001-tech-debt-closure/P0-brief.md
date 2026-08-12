task: "agate 技术债登记闭环（Phase 1-3）：模板 + schema 校验 + 回退强制登记 + P8 确认留痕，用 T001 既有条目回填验证；tech-debt.md 落独立 debt/ 目录（修正 TAG0003 agents/ 归类）——基于 TAG0003 工作区 + TAG0002 refactor 之后的协议实现"

known_risks:
  - "技术债登记闭环依赖'主 Agent 自觉'的环节（评审/复盘自愿通道）可能退化——用回退事件强制登记对冲，但自愿通道失效风险仍在"
  - "回退事件召回极低（全仓库历史仅 2 条），该信号只能发现已爆雷的债，无法发现正在腐烂的债（评审 §8.3 诚实标注）"
  - "七态状态机无 gate 强制会僵死——采用三态（open/in_progress/closed）"
  - "如果 P8 的债务确认退化成无脑打勾，该强制应移除（止损条件 4）"
  - "T001 复盘 T1-T4 回填是模板设计的试金石——若回填失败说明模板设计错误"
  - "【2026-08-12 更新】tech-debt.md 落独立 debt/ 目录（{AGATE_WORKSPACE}/debt/tech-debt.md）——TAG0003 工作区规范把 tech-debt 归入 agents/（WORKFLOW.md L85 agents/ # agent 知识（project.md / memory / tech-debt））是粗略归类，用户确认本次修正：agents/ 只放 agent 输入知识（project.md/memory），tech-debt 是流程产出的项目状态记录（有状态机/schema/被脚本读写），归独立 debt/ 目录"
  - "【2026-08-12 更新】修正 TAG0003 agents/ 归类属于本次新发现的问题（原 P0-brief 范围外，用户确认纳入）——需同步 WORKFLOW.md 目录图（agents/ 注释去 tech-debt + 新增 debt/ 子目录）+ 工作区初始化 mkdir 8 子目录变 9（或按设计）+ SETUP/UPGRADING 同步；TAG0003 的 BDD-1（8 子目录）验收口径随本次变更需重验"
  - "【2026-08-12 更新】change_type: refactor 已由 TAG0002 实现——TAG0001 不需要再做该字段，但要基于最新协议构建，不得回退"
  - "【2026-08-12 更新】本任务在 dev/workspace 分支上继续——协议文件已被 TAG0003/TAG0002 改动，P4 实现须在其上增量，不改动已验收功能（除本次显式修正的 tech-debt 归类）"

executor_env:
  platform: "opencode"
  has_task_tool: true
  has_local_runtime: true
  network: "limited"
  git: true

env_constraints:
  debug_env: "bash agate/scripts/check-state-yaml.sh docs/tasks/TAG0001-tech-debt-closure/.state.yaml"
  test_cmd: "bats agate/tests/unit/agate-debt-check.bats"
  workspace_path: "{AGATE_WORKSPACE}/debt/tech-debt.md（独立 debt/ 目录，用户确认修正 TAG0003 agents/ 归类；协议侧模板 assets/templates/tech-debt-template.md 在 agate/ 内）"
