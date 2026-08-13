task: "agate 测试套件平台无关化（Windows 兼容测试基建）：把 78 个 Windows bats 失败按'测试平台无关原则'根治——静态扫描器 gate 拦截 Unix 假设 + 批量修正测测试代码 + Linux 模拟环境覆盖 Windows 分支。目标：测试套件平台无关，Linux 全量覆盖，Windows CI 只作最终确认"

issues:
  - "78 个 Windows bats 失败（PR #127 CI 实测）：绝大多数是测试代码的 Unix 假设——硬编码 PATH='/usr/bin:/bin'（15 处 check-tdd-red.bats）、裸 python3 调用（98 处，20+ 文件）、[[ -L ]] symlink 单平台断言（install-hook.bats 2 处）、/tmp 等 Unix-only 路径。这些在 Linux 跑不出来（Linux 恰好满足），只有 Windows CI 暴露"
  - "根因：测试套件从未在 Windows CI 跑过（protocol-tests.yml 历史全 ubuntu），测试代码隐含单平台假设。'agate 能在 Windows 跑'指脚本产品（Git Bash 设计兼容），不是测试套件"
  - "分层方案（Linux 可覆盖 93%+）：①静态扫描器（check-platform-assumptions）扫描 Unix 假设并 gate 阻断 ②批量修测试（PATH 探测/python3→python|python3/symlink 按平台分支//tmp 替换）③Linux 模拟环境覆盖 Windows 分支（PYTHONIOENCODING/ln mock/PATH 探测）④真 Windows CI 只作最终确认"
  - "3-5 个'待真验证'（symlink/python.exe/cp1252）可归零：产品层显式处理平台差异 + 测试按平台分支断言 + 模拟覆盖——测试套件理论上平台无关，Windows CI 从'必要兜底'降级为'可选最终确认'"
  - "测试平台无关原则已确立（AGENTS.md「测试约定」+ tests/README「何时更新」，v0.44.0 后）：本任务负责把现有 78 个失败按原则改造 + 建静态扫描器 gate 兜底"

known_risks:
  - "批量改 78 个失败涉及 19 个测试文件——每处修改都可能破坏 Linux 行为（Linux 基线是红线），必须先加平台无关的失败测试确认红再改"
  - "静态扫描器本身要平台无关（用 bash + grep 实现，Windows MSYS2 可跑）——不能自己引入 Unix 假设"
  - "symlink 测试按平台分支断言（Linux 断言软链/Windows 断言复制模式）——需确认 install-hook.sh 在 Windows 确实输出'复制模式 WARNING'（platform-notes 声明过，需测试验证）"
  - "python3 探测 helper 要统一（load.bash 或 fixtures.bash 提供 PYTHON=python3|python 探测），所有测试引用 helper 而非裸 python3"
  - "【强制要求】同类扫描 + 平台无关 gate：P1 必须全仓 grep 平台假设（PATH/python3/-L//tmp），列出的实例全部纳入 BDD；本任务产出的静态扫描器接入 CI（Linux 上跑，阻断新 Unix 假设）。用户明确：不愿意一轮一轮来回改"
  - "【2026-08-13 用户确认】'测试无平台假设化'成长为本项目测试原则（已写入 AGENTS.md），本任务是把存量测试改到符合原则 + 建 gate"

executor_env:
  platform: "opencode"
  has_task_tool: true
  has_local_runtime: true
  network: "full"
  git: true

env_constraints:
  debug_env: "本环境为 Linux（UTF-8 locale）；Windows 分支用模拟环境（PYTHONIOENCODING/ln mock/PATH 探测）覆盖，真 Windows CI 作最终确认"
  test_cmd: "bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/；python3 agate/scripts/check-protocol-consistency.py --strict"
  workspace_path: "{AGATE_WORKSPACE}/tasks/TAG0009-tests-platform-neutral/"
  # 原则：AGENTS.md「测试约定」测试平台无关原则；78 失败清单见 TAG0004 研判稿（PR #127 CI 日志）
