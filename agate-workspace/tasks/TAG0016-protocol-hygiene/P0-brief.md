task: "agate 协议卫生与测试效率（RM-AG0025 + RM-AG0026）：协议文档职责边界与去重（WORKFLOW/dispatch-protocol/state-machine/platform-notes 交叉重复 + 内容归属约定）+ 测试重跑审计与跨阶段证据引用（P5/P6/P8 全量最坏 4-5 遍 + P6 regression 复用机制 + P8 放宽）。同属'协议成熟化'簇，合并一个 task（2026-08-17 规划）"

issues:
  - "RM-AG0025 协议文档职责边界与去重：agate 协议文档渐进叠加（每版本/任务往顺手文件追加），无职责边界审计——交叉重复：①平台适配三份（WORKFLOW L461/dispatch-protocol L1207/platform-notes）②阶段门槛两份（WORKFLOW 阶段总览表 vs dispatch-protocol 可判定门槛规范）③派发 prompt 双源（dispatch-protocol L429-628 vs assets/templates/dispatch-prompt.md，N6 修过的双源仍在）④Pre-commit 清单两份（WORKFLOW L303 vs state-machine L215）⑤重试上限两份（state-machine vs dispatch-protocol）⑥职责定位混乱（WORKFLOW 塞 gate 命令/Pre-commit/平台适配；dispatch-protocol 塞派发编排机制）。根因：无每份文档唯一职责 + 无内容归属约定（LIMITATIONS 局限 5）。**系统排查要求（用户强调）**：不只修已知 6 处，P1 做关键词交叉扫描（每条规则 grep 全仓确认出现次数 >1 即潜在双源）/职责声明表（每文档一句话职责）/内容归属审计/生成性扫描（新内容塞错文件）/防复发（consistency 加同一关键词多处出现检测）"
  - "RM-AG0026 测试重跑审计与跨阶段证据引用（外部 agent 分析）：同一任务全量测试最坏 4-5 遍——P5 首跑 + P5 重试全量（T027 教训）+ P6 refactor 独立 regression.log（regression_pass 硬校验，P6-acceptance.md L108）+ P8 重跑 P5（P8-release.md L82/118）。823 用例单次 106-115s，4-5 遍 = 500+s 花在重复确认。修复=①审计全量重跑点（逐任务统计）②跨阶段证据引用协议（核心机制改进：P5 全绿 + P6 验收前无代码改动（git log 校验）→ P6 regression 可引用 P5 产物；provenance 审计支持引用前序证据 + 无改动声明）③P8 放宽（bump 后跑一次而非完整重跑）④xdist 试点（P5 单发场景 -n auto，真实 CI 4 核验证，不与并行派发叠加）"

known_risks:
  - "AG0025 改动面大（WORKFLOW/dispatch-protocol/state-machine/platform-notes/role-system 等）→ 触发 SELF-GATE + consistency 锚点可能失效（CHECK 3/9 引用）"
  - "AG0025 去重是'改文档结构'——先定义每文档唯一职责，再迁移内容，避免边改边乱"
  - "AG0026 跨阶段证据引用是协议机制改进（check-p6-provenance.py 支持引用前序证据）——P2 需设计'无改动校验'的可判定标准（git log 对比范围）"
  - "AG0026 P6 regression 复用的边界：P6 验收前有代码改动（回 P4 修 bug）则不能复用——P2 需定义'何时不可复用'"
  - "xdist 试点需真实 CI（4 核）验证——本环境 1 核测不出加速，P5 阶段在 CI 上验证，不在本地空测"
  - "【强制要求】同类扫描 + 影响面梳理：AG0025 自身就是'职责边界'的示范——P1 必须 grep 全仓每条协议规则的出现次数建影响面表；AG0026 统计各任务实际全量重跑次数。用户明确：不愿意一轮一轮来回改"

executor_env:
  platform: "claude-code"  # [P0_STALE] 原值 opencode，本次会话实际以 Claude Code 启动；orchestrator 双平台已注册（.opencode + .claude 均软链同一模板），能力字段不受影响，轻微漂移（判据4），更新后继续
  has_task_tool: true
  has_local_runtime: true
  network: "full"
  git: true

env_constraints:
  debug_env: "本环境为 Linux；xdist 加速需真实 CI（ubuntu-latest 4 核）验证"
  test_cmd: "python3 -m pytest agate/tests/；python3 agate/scripts/check-protocol-consistency.py --strict；bash agate/tests/scripts/count-tests.sh"
  workspace_path: "{AGATE_WORKSPACE}/tasks/TAG0016-protocol-hygiene/"
