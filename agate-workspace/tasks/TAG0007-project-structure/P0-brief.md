task: "agate 项目结构管理机制：RM-AG0008（0→1 项目目录结构脚手架）+ RM-AG0009（code-map + 架构演进纪律）。新增机制——骨架是'初始结构'、code-map 是'演进维护'，同一主题'项目结构管理'"

known_risks:
  - "RM-AG0008 新增'项目骨架'产出环节——需设计放哪个阶段（P0/P1）、怎么验证（目录树可验收）、配模板（按技术栈）——P2 设计关键决策"
  - "RM-AG0009 新增 CODE-MAP 维护物 + 架构演进纪律——CODE-MAP 放哪（工作区）、P2 怎么查架构合规、gate 怎么检测依赖偏离——设计决策多，P1/P2 需充分"
  - "两个都是'建'（新增机制），不是'修'——需完整 P0-P8，不能 plan 硬做（2026-08-13 用户确认：不为了 hotfix 故意不做 task）"
  - "涉及协议文档 + 模板 + 可能新增脚本（gate 检测依赖偏离）→ 触发 SELF-GATE"
  - "与 TAG0002（重构一等任务）关联：code-map 的架构演进纪律要兼容 refactor 类任务的变更记录"

executor_env:
  platform: "opencode"
  has_task_tool: true
  has_local_runtime: true
  network: "limited"
  git: true

env_constraints:
  debug_env: "本环境为 Linux；可在本仓库自举验证（agate 自己就是 0→1 项目的骨架案例）"
  test_cmd: "bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/；python3 agate/scripts/check-protocol-consistency.py --strict"
  workspace_path: "{AGATE_WORKSPACE}/tasks/TAG0007-project-structure/"
  # 建机制类任务：骨架 + code-map 是协议新增能力，P2 设计核心（放哪阶段/格式/验证口径）
