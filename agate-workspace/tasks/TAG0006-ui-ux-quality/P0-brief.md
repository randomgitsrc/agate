task: "agate UI/UX 验收质量机制：解决'agate 保证工程质量但不保证 UX 质量'——RM-AG0007（UX 需求/评审/验收机制）、RM-AG0004（视觉验收能力边界，能力识别不写死）、RM-AG0006（GUI 自动化框架评估）。新增机制/能力，跨 P1/P2/P6 协议增强"

issues:
  - "RM-AG0007 UX 质量机制缺失（qtcalc 对比实证）：走 agate 的 qtcalc 架构/测试/治理领先但表达式次显示/键盘输入/UI 样式三项 UX 反而不如没走的 qtcalc-basic。根因：ui_affected 只触发 E2E 功能测试（state-machine.md:89-94）不要求视觉/交互质量；P2 plan-design-review 审架构不审视觉稿；P6 视觉验收看'渲染成功'无美观/易用维度；全部 gate 是 exit code 无用户主观体验验收。修复=①P1/P2 加 UX 需求基线（键盘/显示/样式写成 BDD 可测项+视觉验收项）②frontend 任务 plan-design-review 增视觉/交互维度 ③P6 对 UI 任务强制双证据+视觉质量 checklist"
  - "RM-AG0004 P6 视觉验收能力边界（2026-08-17 修正：能力识别不写死 + subagent 能力自查）：视觉验收能力**运行时探测，不写死具体工具**——项目可能有 vision-engine/多模态模型/其他视觉能力，也可能没有。修复=①ui_affected 任务的 P1 **capability_requirements 必须声明 vision 能力三态**：available（有视觉能力→P6 真实视觉验收）/ supplementable（可注入 skill/外部工具→派发时指引注入）/ GAP（无→降级：双证据截图+行为日志 + 像素检测 + 人工复核）；②available 时 P6 真实视觉分析（本机 vision-engine 可用，但别的项目可换）；③**subagent 能力自查**：视觉验收常由 vision-analyst subagent 执行，派发时 prompt 要求它**先自查能否调 vision 能力**（不能就报告，不静默假设）——主 Agent 能力 ≠ subagent 能力，能力传递机制见 RM-0014（supplementable 扩展）；④输入态变化类用例加人工复核；⑤雷同截图自动降级待复核（不只 WARNING）。**关键：不写死 vision-engine 或任何具体工具，靠 P1 能力识别 + subagent 自查 + 降级链**"
  - "RM-AG0006 GUI 自动化框架评估：Windows 环境无 Playwright 等 GUI 自动化框架，UI e2e 用 QTest offscreen 信号级模拟+截图（TQC0001 Q9）。修复=P2 设计时评估 WinAppDriver/AutoIt 是否补真实 GUI 交互路径，可能产出'保持现状'结论（技术选型调研，非纯实现）"

known_risks:
  - "RM-AG0007 跨 P1/P2/P6 三阶段——改动面大（analyst/architect/verifier 角色 + phase-cards + state-machine），需 P1 拆 BDD 时按阶段组织"
  - "RM-AG0004 视觉验收依赖项目声明的视觉能力（2026-08-17 修正：不写死 vision-engine，能力靠 P1 capability_requirements 三态识别）——available 时真实视觉验收（本机 vision-engine 可用）；GAP 时降级（双证据 + 像素 + 人工复核）。能力边界诚实标注，不假设有或无"
  - "RM-AG0006 是技术选型调研（WinAppDriver/AutoIt）——非纯实现，P2 设计时需先出评估结论再定方向，可能产出'建议保持现状'"
  - "三处都涉及协议文档增强（phase-cards/*.md、assets/execution-roles/*.md、state-machine.md）→ 触发 SELF-GATE"
  - "【2026-08-13 用户确认】本任务走完整 task（非 plan）——UI/UX 质量是真实能力缺口，值得 P0-P8 完整流程"
  - "【强制要求】同类扫描 + 联动面梳理：P1/P2 阶段必须梳理'UX 机制影响面'——ui_affected/plan-design-review/vision-analyst 在 64 处文件被消费，改一处须同步所有联动点（state-machine 转移条件、verifier 角色、vision-analyst 角色、P2 卡片 C8 表）。P2 设计先画影响面图再动手，避免'改了 P6 漏了 P2'的多轮返工。用户明确：不愿意一轮一轮来回改"

executor_env:
  platform: "opencode"
  has_task_tool: true
  has_local_runtime: true
  network: "full"
  git: true

env_constraints:
  debug_env: "本环境为 Linux（UTF-8 locale），无真实 Windows GUI；GUI 框架评估基于调研非实测；视觉验收能力 vision-engine 可用（本机，P1 能力识别确认）"
  test_cmd: "python3 -m pytest agate/tests/；python3 agate/scripts/check-protocol-consistency.py --strict；bash agate/tests/scripts/count-tests.sh"
  workspace_path: "{AGATE_WORKSPACE}/tasks/TAG0006-ui-ux-quality/"
  # 机制增强类任务：新增能力，需 P1 需求基线 + P2 方案设计（含 UI 验收口径决策 + vision 能力三态识别）
