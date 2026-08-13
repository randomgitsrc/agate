task: "agate UI/UX 验收质量机制：解决'agate 保证工程质量但不保证 UX 质量'——RM-AG0007（UX 需求/评审/验收机制）、RM-AG0004（无多模态视觉验收能力边界）、RM-AG0006（GUI 自动化框架评估）。新增机制/能力，跨 P1/P2/P6 协议增强"

known_risks:
  - "RM-AG0007 跨 P1/P2/P6 三阶段——改动面大（analyst/architect/verifier 角色 + phase-cards + state-machine），需 P1 拆 BDD 时按阶段组织"
  - "RM-AG0004 视觉验收依赖多模态模型能力——若本环境无多模态，只能做'双证据强制 + 雷同截图降级'的机制增强，无法做真实视觉验收（能力边界，诚实标注）"
  - "RM-AG0006 是技术选型调研（WinAppDriver/AutoIt）——非纯实现，P2 设计时需先出评估结论再定方向，可能产出'建议保持现状'"
  - "三处都涉及协议文档增强（phase-cards/*.md、assets/execution-roles/*.md、state-machine.md）→ 触发 SELF-GATE"
  - "【2026-08-13 用户确认】本任务走完整 task（非 plan）——UI/UX 质量是真实能力缺口，值得 P0-P8 完整流程"

executor_env:
  platform: "opencode"
  has_task_tool: true
  has_local_runtime: true
  network: "limited"
  git: true

env_constraints:
  debug_env: "本环境为 Linux（UTF-8 locale），无真实 Windows GUI；GUI 框架评估基于调研非实测"
  test_cmd: "bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/；python3 agate/scripts/check-protocol-consistency.py --strict"
  workspace_path: "{AGATE_WORKSPACE}/tasks/TAG0006-ui-ux-quality/"
  # 机制增强类任务：新增能力，需 P1 需求基线 + P2 方案设计（含 UI 验收口径决策）
