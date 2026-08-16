task: "agate 复盘与反馈机制统一（RM-AG0020 + RM-AG0021）：复盘模板进协议本体（正文结构 + 归因分层 + 事实依据）、复盘产出归 task 产物、check-retrospective 路径同步、orchestrator-log 扩展决策依据 + 会话 checkpoint、复盘→agate 项目组反馈（结构化 agate 反馈节 + 匿名化 + 开关）。AG0020 是核心（复盘机制），AG0021 建立在 AG0020 的结构化产出上（反馈机制）"

issues:
  - "RM-AG0020 复盘机制统一（六项残缺）：
    ①模板缺正文结构——postmortem-template.md（docs/reviews/）只有机制触发核对清单，无复盘正文（做得好的/发现的问题/改进措施）——正文靠临场拼（TAG0013 复盘 84 行是拼的，非模板定义）
    ②内容无价值标准——易沦为流水账/自我表扬；有价值的是机制缺口 + 可复用模式 + 归因到可行动层面的问题
    ③标的矛盾——check-retrospective.py（P2.12）只在异常模式（retry 超限/SCOPE+/override）提醒；但正常任务（TAG0013 无 retry）也写复盘（因发现机制缺口）——无统一标的
    ④路径矛盾——复盘是绑定 task 的产物（与 P1-review.md 同类）应放 tasks/{Txxx}/retrospective.md；实际先例在 docs/reviews/；check-retrospective 提示 docs/releases/——三处不一致（2026-08-16 用户判断：放 tasks/{Txxx}/）
    ⑤归因纪律缺失——不区分执行错误（agent 没遵守规则→修纪律）vs 机制缺口（协议没定义→修协议）——归因错层措施落空
    ⑥产出流向缺失——复盘发现机制缺口应流向 roadmap（RM）/DEBT，无强制约定
    ⑦事实依据缺失——机理分析（为什么这么做）的因果链在主 Agent/subagent 的 session 里，session compact 就丢；orchestrator-log 明确不写思考过程，且无强制力（TAG0014 目录实测无 orchestrator-log.md）——三层事实源：L1 仓库落盘（git log/产出/orchestrator-log/progress）L2 会话 checkpoint（任务期间落盘，新增）L3 平台导出（补充）
    ⑧时机前置——过程摘要（L2）在任务完成时立即落盘（趁 session 完整），正式复盘在 merge main 后基于摘要写"
  - "RM-AG0021 跨项目反馈机制（建立在 AG0020 结构化产出上）：其他项目用 agate 实施时，复盘归因到 agate 机制/执行层的问题对 agate 项目组有价值，但无机制回馈（协议零遥测）。内容边界：只回传 agate 归因条目，不涉项目敏感信息。修复=①复盘文档加 frontmatter 机器字段（mechanism_issues/execution_issues/feedback_ready）+ ## agate 反馈 结构化节 ②agate-feedback.py 提取+匿名化+生成 JSON+提示提交（手动触发）③AGATE_FEEDBACK 开关默认 off（opt-in 隐私优先）④回传通道（issue/PR）"

known_risks:
  - "postmortem-template.md 现在 docs/reviews/（项目资料），应进协议本体 agate/assets/templates/（retrospective-template.md）——但既有复盘文档引用旧位置，迁移需处理存量"
  - "复盘产出位置从 docs/reviews/ 迁到 tasks/{Txxx}/retrospective.md——存量复盘（TAG0013/0014 等）需迁移或标记旧布局"
  - "orchestrator-log 扩展（决策+依据）+ 会话 checkpoint 是新机制——需定义落盘时机/内容/防 compact 策略，P2 需设计"
  - "反馈机制（AG0021）依赖 AG0020 的复盘结构化产出——本任务按 AG0020 核心 + AG0021 增量两阶段做，避免一次过大"
  - "改动触发 SELF-GATE（改 agate/assets/templates/ + state-machine.md + check-retrospective.py）——commit message 需 self-gate-review"
  - "【强制要求】同类扫描 + 影响面梳理：P1 必须 grep 全仓 '复盘/retrospective/postmortem/orchestrator-log' 引用点（check-retrospective.py 提示、交接单、AGENTS.md、state-machine.md、复盘模板），建影响面表。用户明确：不愿意一轮一轮来回改"

executor_env:
  platform: "opencode"
  has_task_tool: true
  has_local_runtime: true
  network: "full"
  git: true

env_constraints:
  debug_env: "本环境为 Linux；Windows 靠 CI matrix（pytest -m windows_smoke）"
  test_cmd: "python3 -m pytest agate/tests/；python3 agate/scripts/check-protocol-consistency.py --strict；bash agate/tests/scripts/count-tests.sh"
  workspace_path: "{AGATE_WORKSPACE}/tasks/TAG0015-retrospective-feedback/"
