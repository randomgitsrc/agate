task: "agate 机制修复批：4 个已核实的机制/契约缺陷——RM-AG0010（P2 gate vs C8 契约矛盾）、RM-AG0011（P5 gate_commands 计数语义）、RM-AG0012（自定义角色两瑕疵）、RM-AG0003（短命会话自动重试）。均为'现有东西错了/不完整'的修复，无新机制"

known_risks:
  - "RM-AG0010 有方案决策（二选一：C8 补 backend P2 评审 vs gate 豁免）——P1 需先定方案再改，若涉及'backend P2 是否必须派评审'的产品判断，需用户确认"
  - "四处改动互不耦合，但都涉及 agate/scripts/*.sh + agate/*.md → 触发 SELF-GATE，每处 commit 需 self-gate-review/skip 标记"
  - "RM-AG0003 短命会话重试是对已有恢复策略（dispatch-protocol.md L105）的增量，改动明确但需确认不破坏现有重试语义"
  - "RM-AG0012 渲染脚本 exit code 改动（角色不存在 exit 0 → 非零）可能影响依赖该脚本的其他调用方——需 grep 确认调用处"

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
