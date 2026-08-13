task: "agate UI/UX 验收质量机制：解决'agate 保证工程质量但不保证 UX 质量'——RM-AG0007（UX 需求/评审/验收机制）、RM-AG0004（无多模态视觉验收能力边界）、RM-AG0006（GUI 自动化框架评估）。新增机制/能力，跨 P1/P2/P6 协议增强"

issues:
  - "RM-AG0007 UX 质量机制缺失（qtcalc 对比实证）：走 agate 的 qtcalc 架构/测试/治理领先但表达式次显示/键盘输入/UI 样式三项 UX 反而不如没走的 qtcalc-basic。根因：ui_affected 只触发 E2E 功能测试（state-machine.md:89-94）不要求视觉/交互质量；P2 plan-design-review 审架构不审视觉稿；P6 视觉验收看'渲染成功'无美观/易用维度；全部 gate 是 exit code 无用户主观体验验收。修复=①P1/P2 加 UX 需求基线（键盘/显示/样式写成 BDD 可测项+视觉验收项）②frontend 任务 plan-design-review 增视觉/交互维度 ③P6 对 UI 任务强制双证据+视觉质量 checklist"
  - "RM-AG0004 P6 视觉验收能力边界：无多模态模型时 vision-analyst 退化为像素分析+OCR（TQC0001 b17 前置态截图仍判 PASS），check-p6-evidence 报 16 组视觉相似 WARNING。修复=无多模态时强制'截图+行为日志'双证据；输入态变化类用例加人工复核；雷同截图自动降级待复核（不只 WARNING）"
  - "RM-AG0006 GUI 自动化框架评估：Windows 环境无 Playwright 等 GUI 自动化框架，UI e2e 用 QTest offscreen 信号级模拟+截图（TQC0001 Q9）。修复=P2 设计时评估 WinAppDriver/AutoIt 是否补真实 GUI 交互路径，可能产出'保持现状'结论（技术选型调研，非纯实现）"

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
