task: "agate 协议机制增强批：RM-AG0013（阶段卡缺'同类扫描/影响面梳理'机制层要求）+ RM-AG0014（跨平台/外部环境验证的机制边界 + 环境准备职责）+ RM-AG0019（P0-brief 时效性验证缺失）+ **RM-AG0016 运行时管控（TPV0093 回流：命令超时兜底/资源密集串行/progress 心跳）**。同属'协议机制增强'簇，改动域重叠（phase-cards/dispatch-protocol/state-machine/角色文件），合并一个 task（RM-AG0019 于 2026-08-15 并入；RM-0016 运行时管控于 2026-08-17 并入——TAG0014 已完成 v0.49.0 未含该新增内容，且与 RM-0014 文件重叠高）"

issues:
  - "RM-AG0013 阶段卡缺'同类扫描/影响面梳理'机制层要求：P0-P8 阶段卡均无'同类扫描/全仓 grep/影响面梳理/联动'要求。agate 历史多次栽在'修一处漏同类'（M4/M5 的 [:：] 只修一处、Q2 只修 P5 卡、TPV0090 backend 域反复踩 P2 契约）。'同类扫描强制要求'只存在于部分 task 的 P0-brief（局部一次性），机制层缺失。修复=①P0 卡加'同类/影响面预判' ②P1 卡加'同类扫描' ③P2 卡加'影响面梳理'"
  - "RM-AG0014 verification_env 机制边界：TAG0009 Windows CI 排障拉 11.7 小时，复盘归因于机制误用+协议空白。核实①机制误用——协议已有 verification_env（dispatch-protocol.md L881-886）专用于'环境依赖'场景，TAG0009 实际标成了 supplementable（能力缺失三态，用错机制）。核实②真协议空白——verification_env 只定义'如何声明环境'，无'环境验证失败后怎么办'（无 CI 轮次预算/止损轮次/批处理要求/READY 后外部问题归属）。修复=①P1 卡+analyst 角色加 supplementable vs verification_env 边界注 ②补 verification_env 失败处理协议（可验证/不可验证清单、每轮多假设批处理、止损轮次、READY 后问题归属）③CI 轮次预算进 P1"
  - "RM-AG0019 P0-brief 时效性验证缺失（2026-08-15 用户提问立项，并入本任务）：P0-brief 是立项时点快照，状态机当恒真前提——任务搁置再启动时前提漂移（TAG0008 实证：8-13 立项写 .sh 路线，8-15 启动时 TAG0010 已全量 Python 化，靠人工发现才避免按错误前提实施）。现有 P0 环境自检只查运行时工具（P0-orchestrator.md L29-34）不查内容过时；P1 在过时基础上工作；env_state 一致性验证只覆盖运行时资源不覆盖立项前提。修复=①P0→P1 前提校验（对照当前项目状态核对四字段，漂移则更新 P0-brief 标注变更点）②漂移严重（技术路线全变）→ 重新立项/可行性分析而非直接 P1 ③P1 analyst 需求质疑前先校验前提，过时标记 [P0_STALE] ④落点：P0/P1 卡 + state-machine P0→P1 转移条件"
  - "RM-AG0016 运行时管控（2026-08-17 TPV0093 回流并入，来源 RM-AG0023）：PeekView TPV0093 复盘 3 次 subagent 卡死（`cat` 命令挂 3.1h、`make test-quick` 挂 188min）暴露——subagent bash 命令无超时兜底、遇 flaky 偏离约束、并行资源竞争、progress 心跳在命令执行中失效。修复=①gate_commands/dispatch_plan 加 `timeout_seconds` 字段（声明命令预期时长，派发时硬编码；**阈值须合理**——pytest 全量 ~70s/CDP E2E 需更大，不能低到长命令误判失败 + **执行留痕**）②dispatch-prompt 加'命令超时兜底'标准节（每个 bash 命令必须设 timeout ≤预期时长×1.5；超时→停止+写 progress 返回；遇非预期失败→记录后返回主 Agent，禁止自行深入诊断）③P5 卡加'资源密集型默认串行'（backend 全量 pytest xdist + frontend 全量 vitest 默认串行，需并行时评估 CPU/IO 竞争）④progress 心跳扩展（每个 bash 命令**前**写 progress，主 Agent 可判断是否卡在命令中）"
  - "RM-AG0014 环境准备职责边界（2026-08-17 补充）：verification_env 定义'如何声明环境'，还要补'谁负责准备环境'——P5/P6 需运行环境（debug server/测试数据库）时：主 Agent（P0-brief debug_env 声明，负责启动/维护/关停）还是 subagent（自启无防护→卡死）？多 subagent（前端+后端）各启各的→冲突/资源竞争。建议：环境启动/维护/关停归主 Agent（或 P0-brief 明确单一方），subagent 只消费不启动；多 subagent 需共享环境时主 Agent 统一启动 + dispatch-context 注入访问方式。落点：dispatch-protocol verification_env 节 + P5/P6 卡片"

known_risks:
  - "五条都改 phase-cards/dispatch-protocol/state-machine/角色文件 → 触发 SELF-GATE"
  - "RM-AG0013 改 P0-P2 卡片，RM-AG0014 改 dispatch-protocol + P1 卡 + analyst，RM-AG0019 改 P0/P1 卡 + state-machine，RM-0016 运行时管控改 dispatch-prompt + P5 卡 + gate_commands——改动面高度重叠于 phase-cards/dispatch-protocol，P1 需按'哪些卡/哪些节'组织 BDD，避免重复改（同文件两轮改是本批要治的反模式，自己不能犯）"
  - "RM-AG0014 的'失败处理协议'是新增机制设计——P2 需定义止损轮次/批处理要求的具体规则，不是简单补文档"
  - "RM-AG0019 的'重新立项判断'边界需 P2 设计——漂移严重到什么程度算'需重新立项'而非'更新 P0-brief'，需可判定标准"
  - "RM-0016 运行时管控的 timeout_seconds 设计是关键——阈值过低会误杀长命令（TPV0093 教训：时间短但 CDP E2E 需大阈值）；P2 需定义合理阈值基准（命令类型→默认时长）"
  - "【强制要求】同类扫描 + 影响面梳理：本任务自身就是'同类扫描'的示范——P1 必须 grep 全仓 phase-cards 确认'哪些卡片缺同类扫描要求'、grep verification_env 确认'哪些文件消费该字段'、grep P0-brief 确认'消费点'、grep timeout/os.execv 确认'运行时管控同类风险'。用户明确：不愿意一轮一轮来回改"

executor_env:
  platform: "opencode"
  has_task_tool: true
  has_local_runtime: true
  network: "full"
  git: true

env_constraints:
  debug_env: "本环境为 Linux；Windows 靠 CI matrix（pytest -m windows_smoke）"
  test_cmd: "python3 -m pytest agate/tests/；python3 agate/scripts/check-protocol-consistency.py --strict；bash agate/tests/scripts/count-tests.sh"
  workspace_path: "{AGATE_WORKSPACE}/tasks/TAG0012-protocol-mechanism-fixes/"
