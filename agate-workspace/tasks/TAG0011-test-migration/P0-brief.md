task: "agate 测试框架迁移（阶段二，TAG0010 完成后）：58 个 .bats（727 @test）+ 526 行 helpers 迁移到 pytest，配合产品逻辑 Python 化（TAG0010）达成 agate 全面 Python 化。同时完成协议文档全量重写与 CI 同步（用户确认归本任务）。依赖 TAG0010"

issues:
  - "背景：TAG0010 完成产品逻辑 Python 化后，bats 测试仍调 py 脚本。阶段二把 58 个 .bats → pytest（727 @test），达成 '全 Python'——测试代码也平台无关 + 统一生态"
  - "范围：58 个 .bats（727 @test）→ pytest 用例；526 行 helpers（load.bash/fixtures.bash/git-helper.bash）→ pytest fixture；Windows 冒烟机制（check-windows-smoke.sh）评估保留或退役"
  - "协议文档全量重写（用户确认归本任务）：platform-notes Windows 章节（5 处 .sh 引用/bash install-hook.sh/copy 模式前提）、SETUP.md、UPGRADING.md 破坏性变更章节、dispatch/git-integration 中 bash 相关引用、CI workflow（protocol-tests.yml 从 bats 改 pytest 调用）"
  - "验收：pytest 全绿替代 bats；consistency 0 ERROR；ruff/pyflakes 静态检查；Windows CI 冒烟通过；扫描器覆盖 .py（扩展 check-platform-assumptions 规则集）"

known_risks:
  - "727 个 bats 断言链重写为 pytest 是数周密集工作 + 高回归风险——按模块分批迁移，每批 pytest 绿 + 原 bats 对照"
  - "bats 的 @test 语义（setup/teardown/run/$output）vs pytest fixture 语义映射复杂——写迁移映射表，避免逐条硬翻译"
  - "Windows 冒烟机制（check-windows-smoke.sh）若 pytest 全平台可跑，评估退役；若 Windows 性能仍需，保留"
  - "协议文档全量重写影响面大（用户/外部直接调用脚本的项目是破坏性变更）——UPGRADING 必列，按 AGENTS.md 版本清单"
  - "【强制要求】同类扫描 + 影响面梳理：P1 必须梳理 58 个 .bats 的分组（按被测脚本）做迁移批次 + 文档引用全清单。用户明确：不愿意一轮一轮来回改"
  - "【2026-08-14 用户确认】两个 task 做完（TAG0010 产品 + TAG0011 测试）达成全 Python；文档/CI 同步归 TAG0011；hook 保留 sh 薄壳（理由已核实充足）"

executor_env:
  platform: "opencode"
  has_task_tool: true
  has_local_runtime: true
  network: "full"
  git: true

env_constraints:
  debug_env: "本环境为 Linux；pytest 全平台（Linux 全量 + Windows CI 冒烟）；依赖 TAG0010 完成后的 Python 产品逻辑"
  test_cmd: "pytest agate/tests/（阶段二目标）；bats agate/tests/（迁移期对照）；python3 agate/scripts/check-protocol-consistency.py --strict"
  workspace_path: "{AGATE_WORKSPACE}/tasks/TAG0011-test-migration/"
  # 依赖 TAG0010 完成后启动；分析报告 §6 阶段二建议：先保留 bats 测 py，只有测试代码平台问题成瓶颈才迁 pytest——但用户明确要全转 Python，故本任务做完整迁移
