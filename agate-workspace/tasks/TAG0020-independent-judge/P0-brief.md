task: "独立 Judge 机制（RM-AG0032）：P6.5 新增验收独立裁判——fresh context 只给标准（P1 BDD + P2 验收设计）、信息隔离白名单禁传实现者自述，三层防造假（信息隔离/证据交叉核对/append-only 事件账本），三档预算，挂靠现有评审机制。来源：TAG0018 实证（4 场 LLM 评审≈0 净收益、机械 gate 全胜）+ 竞品研究（oh-my-agent 独立 judge）+ LIMITATIONS-3（自写 gate 作者与评判者同为一人）。设计文档：dsh-workspace/agate-research/design-independent-judge.md（含文件级改动清单）"

issues:
  - "TAG0018 实证：4 场 LLM 评审（requirements-review/plan-eng-review/review/alignment-review）17 条非阻塞 + 1 条真实发现（README 缺 DSH 行，机械检查也能抓）——评审失手根因是'评审者与作者同信任链/同上下文'，LLM 评审对结构性任务≈噪声"
  - "LIMITATIONS-3 自认最弱环节：P6/P7 的 gate 判定对象是主 Agent/subagent 自己写的文件，现有缓解（证据存在性/provenance 六道审计/BDD 计数对照）只提高造假成本非硬保证"
  - "修复设计：①新增 review 角色 judge（assets/review-roles/judge.md）：fresh context 逐条重验所有 BDD（含已 PASS 项），只信证据文件与 git log ②三层防造假：信息隔离白名单（dispatch-context 禁含实现者自述）/证据交叉核对（BDD 计数对照·md5 去重·git 留痕）/append-only 事件账本 gate-events.jsonl（行间哈希链防改写）③三档预算（轮次≤2/token 100k/时间 30min，超限诚实降级 partial 不静默放行）④挂靠现有机制（status 门槛映射/专家组评审/dispatch-prompt 模板，零新架构）"
  - "与 RM-AG0031 联动：thin 档跳过 LLM 评审后 judge 为质量兜底（非替代）——P6.5 强制所有任务"

known_risks:
  - "改动面：role-system.md + state-machine.md（P6.5 转移行/重试表）+ WORKFLOW.md（P6 节）+ dispatch-protocol.md（信息隔离节）+ phase-cards/P6 + dispatch-prompt 模板 + 新角色 judge.md + 新脚本 check-judge-verdict.py/check-events.py + agate_common.py（append_event）→ 全部触发 SELF-GATE"
  - "事件账本与既有 gate 兼容性：gate-events.jsonl 哈希链需与 check-p6-provenance 审计共存，P2 需设计字段交集"
  - "预算阈值合理性：token 100k/时间 30min 是设计初值，需 dogfood 校准（P5 实测）"
  - "历史任务兼容：旧任务无 judge 字段 → gate 对历史任务跳过 P6.5 要求（只对新任务生效），避免存量任务全挂"
  - "【强制要求】同类扫描：grep 全仓 review-roles 现状与 status 门槛映射；grep dispatch-context 现有注入内容（白名单反向推导禁入项）；grep check-p6-provenance 六道审计实现（事件账本与其交集）"

executor_env:
  platform: "opencode"
  has_task_tool: true
  has_local_runtime: true
  network: "full"
  git: true

env_constraints:
  debug_env: "本环境为 Linux；/tmp 只读（pytest 需 --basetemp + -p no:cacheprovider）；权限为 danger-full-access"
  test_cmd: "python3 -m pytest agate/tests/；python3 agate/scripts/check-protocol-consistency.py --strict-errors-only；bash agate/tests/scripts/count-tests.sh"
  workspace_path: "{AGATE_WORKSPACE}/tasks/TAG0020-independent-judge/"
