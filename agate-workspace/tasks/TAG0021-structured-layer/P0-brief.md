task: "协议结构化层（RM-AG0022）：把 agent 消费的协议规则从 8000+ 行自由文本 markdown 抽成机器可读的结构化定义（rules/phases.yaml + dispatch.yaml + roles.yaml + JSON Schema），双向一致性 gate 防漂移，gate 脚本从 grep markdown 迁移到读 YAML。来源：TAG0014 复盘（agent 读 8000+ 行 md 理解规则的摩擦）+ DEBT0010 实证（grep 解析缺陷）。设计文档：dsh-workspace/agate-research/design-structured-layer.md（M0-M3 渐进迁移）"

issues:
  - "规则散落：同一规则（如 P2 门槛）在 WORKFLOW/dispatch-protocol/state-machine/phase-cards 多处表述，agent 交叉阅读拼全貌（TAG0016 已做文档层收敛，仍是文本层）"
  - "解析靠 grep：53 个脚本大量依赖对 markdown 的正则解析（如 grep -cE '^(packages|domains|ui_affected|gate_commands):'）——脆弱、易漂移；DEBT0010（_timeout_seconds 键解析遗漏致 P2/P3/P5 误判）是真实教训"
  - "agent 上下文开销：orchestrator 每轮读状态→查卡片→查规则，跨文档查表成本高；RM-AG0031 写时校验、RM-AG0036 双语锚点均依赖本条目"
  - "设计：YAML 为可判定规则权威源 + markdown 保留为人类叙事层 + S-1~S-6 双向一致性 gate（YAML↔md 无漂移，进 CI + pre-commit）+ M0-M3 渐进迁移（纯增量→双跑对账→切换权威源→卡片渲染化），全程 TDD + 可回退"

known_risks:
  - "双份维护（md + YAML）漂移——S-1~S-4 双向 gate 阻断 + CI 强制"
  - "一次性迁移爆炸——M0-M3 渐进，每阶段独立可回退"
  - "YAML 过深失去可读性——schema 限制字段枚举；叙事留 md；YAML 只承载可判定规则"
  - "工具链自举风险（用新 gate 判自己）——双工作区纪律：~/.agate 稳定版跑 gate，worktree 改"
  - "【强制要求】同类扫描：grep 53 个脚本对 markdown 的解析点（grep -cE 模式清单）；grep phase-cards 门槛/产出/派发字段；grep check-protocol-consistency 现有 CHECK 编号空间（防合并冲突）"
  - "改动面极大（协议文档 + 脚本 + 卡片渲染）——建议按 M0-M3 分批 commit，P1 BDD 按迁移阶段组织"

executor_env:
  platform: "opencode"
  has_task_tool: true
  has_local_runtime: true
  network: "full"
  git: true

env_constraints:
  debug_env: "本环境为 Linux；/tmp 只读（pytest 需 --basetemp + -p no:cacheprovider）；权限为 danger-full-access"
  test_cmd: "python3 -m pytest agate/tests/；python3 agate/scripts/check-protocol-consistency.py --strict-errors-only；bash agate/tests/scripts/count-tests.sh"
  workspace_path: "{AGATE_WORKSPACE}/tasks/TAG0021-structured-layer/"
