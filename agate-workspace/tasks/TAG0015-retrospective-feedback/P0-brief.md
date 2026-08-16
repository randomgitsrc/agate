task: "agate 复盘与反馈机制统一（RM-AG0020 + RM-AG0021）：复盘模板进协议本体（正文结构 + 归因分层 + 事实依据 + 项目资产沉淀）、复盘产出归 task 产物、check-retrospective 路径同步、orchestrator-log 扩展决策依据 + 会话 checkpoint、复盘→agate 项目组反馈（结构化 agate 反馈节 + 匿名化 + 开关 + 触发方式修正）。AG0020 是核心（复盘机制），AG0021 建立在 AG0020 的结构化产出上（反馈机制）"

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
  - "RM-AG0020 项目资产沉淀（2026-08-17 用户补充）：复盘'做得好的/可复用模式'节要区分两类可复用资产并明确流向——①agate 机制可复用 → 回馈 agate（RM-AG0021）②项目可复用资产（临时命令/脚本如 make/run-e2e、经验教训如 xdist flaky/timeout 陷阱）→ 提炼到项目基础设施（Makefile/scripts/）+ 项目记忆（agents.md/project.md）。复盘模板强制问：'本次产生的临时命令/脚本/经验，哪些该沉淀为项目固定资产？沉淀到哪？'——解决'agent 很难自主发现可提炼资产'的盲区（TPV0093：run-e2e-tests.sh 无 timeout 是临时脚本，应提炼为项目基础设施并加防护；flaky 应记 agents.md）"
  - "RM-AG0021 触发方式修正（2026-08-17）：TPV0093 回流实证——回流是**用户主动要求外部项目写复盘**才触发，非项目自发回馈。外部项目通常不会主动为 agate 写复盘（无动机）。反馈机制的触发源主要是**用户/agate 项目组推动**（要求外部项目复盘时提醒其登记 agate 反馈节），而非'项目自动回馈'假设。agate-feedback.py 的价值在'把复盘里散落的 agate 归因条目结构化提取'，降低回馈成本，但不解决'外部项目没动机复盘'的根因——后者靠用户推动 + 反馈节模板引导"

known_risks:
  - "postmortem-template.md 现在 docs/reviews/（项目资料），应进协议本体 agate/assets/templates/（retrospective-template.md）——但既有复盘文档引用旧位置，迁移需处理存量"
  - "复盘产出位置从 docs/reviews/ 迁到 tasks/{Txxx}/retrospective.md——存量复盘（TAG0013/0014 等）需迁移或标记旧布局"
  - "orchestrator-log 扩展（决策+依据）+ 会话 checkpoint 是新机制——需定义落盘时机/内容/防 compact 策略，P2 需设计"
  - "反馈机制（AG0021）依赖 AG0020 的复盘结构化产出——本任务按 AG0020 核心 + AG0021 增量两阶段做，避免一次过大"
  - "项目资产沉淀是'复盘模板设计'而非'沉淀本身'——本任务定义复盘模板要求'区分 agate 回馈 vs 项目提炼'，实际提炼是项目侧行为，不由本任务做"
  - "反馈触发方式：TPV0093 实证回流是用户推动非项目自发——P2 设计反馈机制时不要假设'项目自动回馈'，按'用户推动 + 反馈节引导'设计"
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
