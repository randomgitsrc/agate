task: "重构一等任务（Phase A）：P1 加 change_type: refactor 字段 + P6 重构验收口径（行为不变 + 全量回归全绿 + 关键路径验收，禁止伪造功能 BDD）+ check-gate.sh P6 按 change_type 分流"

known_risks:
  - "重构验收口径（行为不变+回归）与既有 P6 gate 可能冲突——止损：回填真实重构发现难以调和则停，重新设计而非硬塞"
  - "重构在 agate 已发生 20 次（19 次不挂任务编号），机制是把既有实践纳入轨道，不是引入新行为——但需避免'形式化后重构反而不做了'"
  - "P6 已有 no_behavior_change 简化口径可作基础，但需确认它是否等价于 refactor 口径，还是需要独立分支"
  - "重构任务无新功能 BDD，P3 测试设计需改为回归测试设计（不新增行为断言）——P3 卡片可能需同步说明"

executor_env:
  platform: "opencode"
  has_task_tool: true
  has_local_runtime: true
  network: "limited"
  git: true

env_constraints:
  debug_env: "bash agate/scripts/check-state-yaml.sh docs/tasks/TAG0002-refactor-first-class/.state.yaml"
  test_cmd: "bats agate/tests/unit/check-gate.bats"
