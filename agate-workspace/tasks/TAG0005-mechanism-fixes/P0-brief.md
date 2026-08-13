task: "agate 机制修复批：4 个已核实的机制/契约缺陷——RM-AG0010（P2 gate vs C8 契约矛盾）、RM-AG0011（P5 gate_commands 计数语义）、RM-AG0012（自定义角色两瑕疵）、RM-AG0003（短命会话自动重试）。均为'现有东西错了/不完整'的修复，无新机制"

issues:
  - "RM-AG0010 P2 gate 与 C8 映射表契约矛盾：check-gate.sh P2 L155-159 无条件要求 P2-review.md 存在且 status=approved；role-system.md C8 表 backend 域='review（P4 后）' P2 无触发角色；phase-cards/P2-design.md C8 表同样无。后果：backend 域（low/medium）任务 P2 按 C8 不派评审→无 P2-review.md→gate exit 1 拦截→主 Agent 被迫自造评审（TPV0090 实测）。修复=三处同步（二选一：C8 补 backend P2 也派 review，或 gate 对无 C8 触发角色豁免）——P1 需先定方案"
  - "RM-AG0011 check-gate P5 gate_commands 计数语义模糊：实际计数逻辑在 agate-gate-p5-count.py（check-gate.sh L250 调用），WARNING 由 check-gate.sh L253 输出——P1 需先定位两处（py 计数 + sh WARNING）再改。P2 声明 P5/P5_cli_remote/P5_serial 时计数 3，实际是'1 主+2 辅助'，误导主 Agent。修复=区分主/辅命令，WARNING 文案区分"
  - "RM-AG0012 自定义角色两瑕疵：①dispatch-prompt.md L10-13 无条件注入'Review 角色特别指令'（status draft→approved）到执行角色，语义混乱——修复=按角色 type 条件注入；②agate-render-dispatch-prompt.sh L63-67 角色文件不存在时报错到 stderr 但 exit 0，主 Agent 可能忽略→派发失败无声——修复=角色不存在 exit 非零（如 exit 2）"
  - "RM-AG0003 短命会话无制度化重试：TQC0001 实测 P2 49 秒/P3 3 分钟各一次空返回，靠主 Agent 经验性重发。dispatch-protocol.md L105 已有'空返回的恢复策略'+重试机制（L51-57）但全手动。修复=恢复策略加'自动重试一次'+'会话时长 <1min 判定异常告警'（增量增强，不改现有重试语义）"

known_risks:
  - "RM-AG0010 有方案决策（二选一：C8 补 backend P2 评审 vs gate 豁免）——P1 需先定方案再改，若涉及'backend P2 是否必须派评审'的产品判断，需用户确认"
  - "四处改动互不耦合，但都涉及 agate/scripts/*.sh + agate/*.md → 触发 SELF-GATE，每处 commit 需 self-gate-review/skip 标记"
  - "RM-AG0003 短命会话重试是对已有恢复策略（dispatch-protocol.md L105）的增量，改动明确但需确认不破坏现有重试语义"
  - "RM-AG0012 渲染脚本 exit code 改动（角色不存在 exit 0 → 非零）可能影响依赖该脚本的其他调用方——需 grep 确认调用处"
  - "【强制要求】同类扫描：P1 阶段对每个修复做全仓同类模式 grep（如 '静默 exit 0'、'无条件注入评审指令'、'P5 前缀计数'），发现的同类实例一并纳入 BDD——不能只修 roadmap 列的位置（agate 历史多次栽在'修一处漏同类'，如 M4/M5 的 [:：]、Q2 的卡片）。用户明确：不愿意一轮一轮来回改"

executor_env:
  platform: "opencode"
  has_task_tool: true
  has_local_runtime: true
  network: "limited"
  git: true

env_constraints:
  debug_env: "本环境为 Linux（UTF-8 locale）；TAG0004 在 worktree 实施中，本任务若需隔离也用 worktree（见 AGENTS.md dogfooding 工作流）"
  test_cmd: "bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/；python3 agate/scripts/check-protocol-consistency.py --strict"
  workspace_path: "{AGATE_WORKSPACE}/tasks/TAG0005-mechanism-fixes/"
  # 均为修复型改动：现有全量 bats 为回归基线，每处修复后全绿 + 对应新增测试
