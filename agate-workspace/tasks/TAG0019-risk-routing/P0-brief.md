task: "风险分路由（ceremony routing，RM-AG0031）：把任务仪式深度从'agent 自报复杂度'改为'客观信号脚本算分'——压 agate 的成本曲线而不降质量地板。来源：2026-08-21 用户反馈（成本高/速度慢）+ TAG0018 实证成本账（4 场 LLM 评审≈0 净收益、机械 gate 全胜）。设计文档：dsh-workspace/agate-research/design-risk-routing.md（M1-M4 落地节奏）"

issues:
  - "成本结构实证（TAG0018，2026-08-21）：subagent 派发轮次串行固有；4 场 LLM 评审 17 条非阻塞 + 1 条真实发现（机械检查也能抓）≈0 净收益；机械 gate（扫描器/校验/审计）便宜且承担全部真实价值——昂贵部分不干活、干活部分不贵"
  - "根因 = self-authorization 陷阱（komina 命名）：复杂度/风险分级若由 agent 自报，就是'同一个概率模型提出行动又评判它能否进行'。TAG0018 实证：analyst 声明 risk_level: low 后 P5 仍抓出真实违规（R2/R4）；agent 一把梭哈倾向系统性"
  - "修复三原则：①客观信号路由（agate-risk-score.py 脚本算分：文件类型/敏感路径/改动规模对齐 pruning 源码数≤5 先例/域映射/影响面，analyst 只解释不决定）②fail-closed 默认（thin 档=申请+逐信号 checklist+跳过风险评估，缺一不可回退 standard；不声明=standard）③requirements-review 增'审声明'职责（P1 后最便宜独立复核点）"

known_risks:
  - "算分规则被 exploit（agent 学会凑低分）——信号来自 git diff 客观事实不可伪造 + 降级需 checklist + requirements-review 独立审声明"
  - "thin 档漏真实问题——fail-closed 默认 + 机械 gate 全部保留（TAG0018 已证机械 gate 是主力）+ P5/P6 不可裁"
  - "改动面：P1 卡（ceremony 字段）+ P2 卡（档位表）+ check-pruning.py 扩展（check-routing）+ requirements-review 角色 + agate_common/新脚本 agate-risk-score.py → 触发 SELF-GATE"
  - "【强制要求】同类扫描：grep check-pruning.py 现有'源码数≤5/耦合清单/跳过风险'判定逻辑直接复用；grep 全仓 risk_level/裁剪/ceremony 消费点（P1 卡/P2 卡/state-machine/check-gate）；grep 平台差异（openCode/Claude Code/DSH）对 gate 语义的影响"
  - "M3（thin 档跳过 LLM 评审）需实证验收锚：以 TAG0018 'LLM 评审≈0 净收益'为基线，前后对比评审轮数 vs 真实发现数，不达标回滚"

executor_env:
  platform: "opencode"
  has_task_tool: true
  has_local_runtime: true
  network: "full"
  git: true

env_constraints:
  debug_env: "本环境为 Linux；/tmp 只读（pytest 需 --basetemp + -p no:cacheprovider）；权限为 danger-full-access"
  test_cmd: "python3 -m pytest agate/tests/；python3 agate/scripts/check-protocol-consistency.py --strict-errors-only；bash agate/tests/scripts/count-tests.sh"
  workspace_path: "{AGATE_WORKSPACE}/tasks/TAG0019-risk-routing/"
