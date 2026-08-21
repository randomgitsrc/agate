task: "agate 原生支持 DSH 平台（deepseek-harness）：RM-AG0030。把 DSH 变成 agate 官方支持的第三个平台——assets/templates/dsh/ 提供 orchestrator agent-preset（agent.cordis.yml + preset.yml）与 agate-protocol skill（SKILL.md）模板，SETUP.md 增加「步骤 2-DSH」符号链接接入章节，platform-notes.md 增加 DSH 平台条目，tests/unit/test_dsh_preset.py 回归测试守护 preset 必填配置。实机验证（2026-08-21，DSH GUI）已确认：preset 热发现、挂载成功、新会话以 agate 编排者人格启动（含修复 tool-fs-search 缺 sampleOverCapGlobResults 配置导致的挂载失败）"

issues:
  - "DSH 平台身份注册机制与 Claude/OpenCode 不同：无 .claude/agents/*.md 等价物，身份注册用 agent-preset（agent.cordis.yml + preset.yml 声明式组合，会话级挂载）——需提供模板并文档化符号链接安装（身份薄、协议厚：persona 指向 {agate_root}/orchestrator-template.md，模板随 ~/.agate 升级自动更新，等价官方符号链接性质）"
  - "DSH 工具面与 task 工具不同：派发用 subagent/subagent_fork（spawn/fork 两种上下文模式）、gate 用 bash exit code 标记、批量并行派发可用 workflow 脚本、fresh-context 复核可用 ralph、跨轮续跑可用 goal——需在 SKILL.md 提供工具映射 + DSH 平台注意（sandbox 只读区/审批策略/bash 纪律）"
  - "回归测试缺失：实机发现 agent.cordis.yml 的 tool-fs-search 行缺必填配置 sampleOverCapGlobResults 导致 preset 挂载失败（DSH schemastery 必填无默认值，fail-closed 拒绝创建会话）——tests/unit/test_dsh_preset.py 固化该缺陷（5 用例，已 TDD 红/绿验证）"

known_risks:
  - "DSH 是新兴平台（v0.1.0-rc.8）：机制细节可能随版本变化（preset schema、skill 发现、session hooks）；文档标注'待实机验证'项，CI 无法覆盖真实 DSH 实例（测试只校验仓库内模板文件）"
  - "DSH sandbox 默认 workspace-write：协议本体目录对 DSH 会话只读（Errno 30）——gate 脚本若写仓库文件会失败，任务工作区需放可写位置（SKILL.md 平台注意已标注）"
  - "改动面：assets/templates/dsh/（新）+ SETUP.md + platform-notes.md + tests/ → 触发 SELF-GATE"
  - "【强制要求】同类扫描：P1 必须 grep 全仓确认无其他平台目录先例可复用（无 platforms/ 目录、install 脚本仅 install-hook.py 一个）——本任务自身就是'按 agate 现有原则做平台支持'的示范，不得发明新结构（install-dsh.py 已废弃：平台接入 = SETUP.md 文档化符号链接 + 唯一 install-hook.py）"

executor_env:
  platform: "opencode"
  has_task_tool: true
  has_local_runtime: true
  network: "full"
  git: true

env_constraints:
  debug_env: "本环境为 Linux；DSH 实机验证已完成（preset 挂载 + 会话人格，2026-08-21）；CI 无 DSH 实例，测试只校验仓库内模板文件"
  test_cmd: "python3 -m pytest agate/tests/；python3 agate/scripts/check-protocol-consistency.py --strict-errors-only"
  workspace_path: "{AGATE_WORKSPACE}/tasks/TAG0018-dsh-platform/"
