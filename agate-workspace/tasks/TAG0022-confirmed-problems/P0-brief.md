task: "三连任务确认问题修复批（RM-AG0037 + RM-AG0038 + RM-AG0039 + RM-AG0040 + RM-AG0041 合并一个 task）：TAG0019/20/21 全面分析（2026-08-22，基于 main 落地实测）确认的 5 个真实问题，同属'质量门禁与迁移收尾'簇，改动域重叠（CI 配置/check 脚本/gate 逻辑/测试卫生），合并一个 task。完整分析：dsh-workspace/agate-research/tag0019-21-analysis.md"

issues:
  - "RM-AG0037 ruff 检查合并强制：TAG0019(23 处)+TAG0020(12 处) 带 ruff 违规合并进 main（合并后实测 35 处错误），靠事后 PR #183 补修；TAG0021 靠内部 P5 自抓 70 处回修。CI 已有 ruff job（protocol-tests.yml:106）但对 PR 合并非硬性。修复=①ruff job 设为 PR required check（分支保护配置）②可选 pre-merge 前强制 ruff 0 error gate；验收锚=新任务合并时 ruff 零违规无需事后补修"
  - "RM-AG0038 结构化层 M2 迁移闭环（RM-AG0022 剩余工作）：check-gate.py（主 Agent 每阶段总闸）实测仍 22 处 markdown/grep 解析、0 处 YAML；53 脚本大量 grep 残留——'权威源'是并行双源（YAML+md），未真正切换，双份维护漂移风险仍在。修复=check-gate.py 等核心脚本迁移到 rules/*.yaml（对齐 gate_commands 族经 agate-md-field-get 的已迁移模式）+ S-1~S-6 收紧为'YAML 权威、md 禁止承载可判定规则'；验收锚=check-gate.py 零 md 解析 + 全量测试绿"
  - "RM-AG0039 judge 启用强制化：P6 卡宣称'P6.5 judge 复核强制所有任务'，但 judge.enabled 由 P1 主 Agent 自写（state-machine.md:443），未启用则全链跳过（TAG0019/20 无 judge 块）——'与 P6 同不可裁'是软强制，残留半 self-authorization。修复=P1 gate 校验新任务必须 judge.enabled: true（缺失阻断或高优先 WARNING 升级），历史任务（机制前）维持跳过；验收锚=新任务 P1 不写 judge 即被拦"
  - "RM-AG0040 TAG0019 M3 实证收尾（RM-AG0031 只完成一半）：ceremony: thin 档从未实战（全仓无任务跑过 thin），成本下降目标（评审轮数 vs 真实发现数对比，TAG0018 基线）无实证数据；thin 档'跳过评审'是协议/提示词级行为，check-routing 只校验声明格式不校验执行。修复=下个 low 风险任务真跑 thin 档并产出对比实证；收益不达预期回滚 standard；验收锚=实证报告"
  - "RM-AG0041 环境假象测试根治（test_bdd_7/25）：测试依赖 basetemp 位置（git 仓库内/共享污染），TAG0020/21 各复现 2 次，仅登记 known-failures 未根治——反复出现有掩盖真实回归风险。修复=两测试改为探测 git 上下文/强制仓库外 basetemp（或按平台分支断言）；验收锚=任意 basetemp 位置下全量 pytest 0 失败"

known_risks:
  - "改动面：CI 配置（protocol-tests.yml）+ check-gate.py/check-routing.py + state-machine.md/P6 卡/P1 卡 + 测试文件 → 触发 SELF-GATE；CI 配置改动需合并后验证 CI 行为"
  - "RM-AG0038 是最大体量（check-gate.py 迁移），P1 BDD 需按子项分组（ruff/judge/M3/环境测试 各自验收锚）"
  - "RM-AG0040 的实证依赖'下一个 low 风险任务'出现——本 task 内无法自证，需产出'实证执行计划 + 触发条件'作为交付（或经用户指定一个薄任务实战）"
  - "RM-AG0037 的 required check 是 GitHub 分支保护配置——实现侧只能改 workflow，required 标记需维护者（用户）在仓库设置里勾选；P1 需明确边界（实现 vs 配置）"
  - "【强制要求】同类扫描：grep 全仓 ruff 消费点（CI/脚本/pre-commit）；grep check-gate.py 全部 md 解析点清单；grep judge.enabled 消费点（check-gate/pre-commit/state-machine/P6 卡）；grep ceremony 消费点"

executor_env:
  platform: "opencode"
  has_task_tool: true
  has_local_runtime: true
  network: "full"
  git: true

env_constraints:
  debug_env: "本环境为 Linux；/tmp 只读（pytest 需 --basetemp + -p no:cacheprovider）；权限为 danger-full-access；ruff 在 ~/.venvs/agate-dev/bin/ruff（0.16.4 对齐 CI）"
  test_cmd: "python3 -m pytest agate/tests/；python3 agate/scripts/check-protocol-consistency.py --strict-errors-only；bash agate/tests/scripts/count-tests.sh；~/.venvs/agate-dev/bin/ruff check agate/"
  workspace_path: "{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/"
