task: "agate 工作区架构：设计 agate-workspace/ 目录规范（含 roadmap 项目级任务管理循环）+ .agate.env 位置配置 + 从 docs/tasks 强制迁移工具"

known_risks:
  - "破坏性变更：现有项目 docs/tasks/ 等强制迁移到 agate-workspace/——需迁移工具 + 指引（A 策略已确认，现有项目不多成本可接受）"
  - "涉及 6 脚本 + 16 文档 + 75 处 docs/tasks 引用（已核实）——改动面广，需完整 P0-P8 + 全量测试"
  - "orchestrator-template 的 project.md 路径（{project_root}/docs/agents/project.md）需改为工作区内路径——影响所有接入项目"
  - "roadmap 任务管理循环是新增机制（agate 现在无项目级规划层）——需设计'roadmap→待开始→立项→回写'流程"
  - "工作区内容边界：agate 编排状态（tasks/agents/archived/reviews/decisions/plans/logs/roadmap）进工作区；项目文档（README/产品文档）留项目 docs/——需明确判据防混"

executor_env:
  platform: "opencode"
  has_task_tool: true
  has_local_runtime: true
  network: "limited"
  git: true

env_constraints:
  debug_env: "bash agate/scripts/check-state-yaml.sh docs/tasks/TAG0003-workspace-architecture/.state.yaml"
  test_cmd: "bats agate/tests/unit/"
