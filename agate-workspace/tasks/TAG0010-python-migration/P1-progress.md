[PROD_NOT_TOUCHED]
# P1-progress（analyst）

## 2026-08-14 开始
- 读取 dispatch-context：任务目标 = 30 sh → py 全量影响面梳理（同类扫描），产出 P1-requirements.md
- 读取 analyst.md 角色定义：先质疑再定义、隐含需求逐维度、BDD 可二值判定、不掺方案
- 读取 P0-brief.md：范围锁定（30 sh → py，hook 保留 sh 薄壳，阶段一不做文档全量重写）；5 条验收标准；4 条 known_risks（consistency 锚点、hook 回退、pyyaml 强制、编码规范）
[PROD_NOT_TOUCHED]
## 读取分析报告
- 报告定稿：30 sh(3813 行) + 18 py(2293 行)；19/30 已调 python；0 个关联数组；调 git 的 14 个
- 函数库：gate-result.sh(105行, source 方=pre-commit-gate/check-tdd-red/agate-capture-env-baseline)；agate-workspace-resolve.sh(57行, source 方=pre-commit-gate/check-debt/agate-migrate-workspace)
- 5 条验收标准 + 强制 gate 4 项（encoding=urf-8 / py3.8+ / ruff / 扫描器覆盖 .py）
- 受影响的 bats：check-platform-assumptions 17、env-adapt-docs 9、agate-scripts-encoding 2、helpers-python 3、agate-workspace-resolve 若干（共约 30-40 用例）
- hook 薄壳约 15 行/个：shebang + AGATE_ROOT 自定位 + 复制模式恢复 + exec python
[PROD_NOT_TOUCHED]
## 脚本全量清单核实
- 30 sh 核实：行数总和 3813（与报告一致）；最大 check-gate.sh 488 行、pre-commit-gate.sh 404 行
- 18 py 核实：check-protocol-consistency.py 35KB 最大；ci-gate-backstop.py 11405B 次之
- sh→sh 真实调用：gate-result.sh 被 capture-env-baseline/check-tdd-red/pre-commit-gate source；workspace-resolve.sh 被 migrate-workspace/check-debt/pre-commit-gate source；pre-commit-gate 用 bash ... 调 12 个子脚本；inject-card 调 next-card；retreat-to 调 archive-stale-outputs
- 分类：报告口径纯 bash 11 个（archive/changes/extract/migrate/next-card/render/summary/p6-format/commit-msg/install-hook/pre-push）；混合 19 个
[PROD_NOT_TOUCHED]
## 读取 scripts/ 目录与部分 sh 依赖
- 已核实 sh→sh/source/py 调用关系（30 个逐个 grep）
[PROD_NOT_TOUCHED]
## consistency 锚点核实（CHECK 8/9）
- CHECK8：check-gate.sh 需含 DESIGN_GAP + --cached；check-pruning.sh 需含 P2 不可裁剪 + --cached
- CHECK9 SCRIPT_ALIGNMENT_ANCHORS 涉 sh 的锚点 40 条（check-gate 7 条、check-pruning 6 条、check-p6-evidence 4 条、check-p6-provenance 3 条、check-state-transition 2、pre-commit-gate 1、pre-push-gate 1、check-tdd-red 1、check-frontmatter 1、check-debt 1、check-platform-assumptions 1、check-state-yaml 1、check-retrospective 1、check-changelog 1、check-scope-resolved 1、check-p6-format 1）
- GATE_SCRIPT_EXEMPT 白名单：gate-result.sh / install-hook.sh / agate-changes.sh / agate-summary.sh / agate-init.sh
- check_anchor_coverage 反向检查 glob check-*.sh + pre-commit-gate.sh + ci-gate-backstop.py——迁移后 glob 若找不到 .sh 会空转（静默通过），P2 需同步改 glob
[PROD_NOT_TOUCHED]
## 测试目录盘点
- tests/unit/ 46 个 bats；tests/regression/ 6 个；tests/integration/ 6 个；sanity.bats 1 个 = 59（报告口径 58，差 1 为 agate-init 或新加）
- 下一步：读取受影响的 5 个 bats 文件核实用例数与断言
[PROD_NOT_TOUCHED]
## 受影响 bats 核实
- check-platform-assumptions.bats：14 个真实 @test（grep 计数 17 含注释/局部变量 2 处）；断言 bash $AGATE_SCRIPTS/check-platform-assumptions.sh（13 处 run）→ 迁 py 后调用方式 + 目录扫描扩展名过滤（*.bats/*.bash/*.sh）需扩 .py
- env-adapt-docs.bats 9 用例：bdd-34 shellcheck *.sh 0 error（迁移后只剩薄壳 sh）；bdd-25/32 不变
- agate-scripts-encoding.bats 2 用例：bdd-5 扫描 *.py encoding 守卫（迁移后覆盖面扩大为防御性加强，断言本身可复用）；bdd-8 不变
- helpers-python.bats 3 用例：bdd-17 断言 check-state-transition.sh 经 shim 行为（python3 stub/shim 路径语义）——迁移后 py 自举不再依赖 bash shim，断言需重构
- agate-workspace-resolve.bats 10 用例：全部 run bash $AGATE_SCRIPTS/agate-workspace-resolve.sh（10 处）→ 迁移后改调 py
[PROD_NOT_TOUCHED]
## 文档引用扫描（表 B 输入）
- 涉 sh 引用的关键协议文档：dispatch-protocol（7 处）、orchestrator-template（5）、platform-notes（4）、UPGRADING（7）、WORKFLOW（5）、state-machine（10）、SETUP（7）、P6-acceptance（1）、templates/handoff（3）、task-files（2）、tech-debt（2）、LIMITATIONS（1）、scripts/README.md（全表）
- git-integration.md：仅文字提及 check-gate.sh/check-p6-provenance.sh（无 scripts/ 前缀路径），低影响
- CI：protocol-tests.yml 含 shellcheck *.sh（Linux+Windows 双跑）、check-platform-assumptions.sh（2 处）、consistency、ci-gate-backstop、check-windows-smoke.sh——CI 同步部分归 TAG0011，但 shellcheck 目标与扫描器调用需阶段一内同步
[PROD_NOT_TOUCHED]
## WORKFLOW.md 需求与验收机制已读
- 需求基线/BDD/SCOPE+/定向回补/NEED_CONFIRM 机制确认；P1 基线保护（BASELINE_CHANGE）
[PROD_NOT_TOUCHED]
## bats 调用面统计
- 全 tests 树 grep 各 .sh 引用：46 个 bats 文件引用至少一个 .sh（含注释/变量名）；直接运行断言集中在 unit/ + integration/ + regression/ + scripts/
- 验收标准①"全量 bats（bats 调 py）全绿"确认：测试侧调用方式将从 bash xxx.sh 改为调 py
[PROD_NOT_TOUCHED]
## 测试调用面量化
- 29 个 bats 文件 / 413 个 bash $AGATE_SCRIPTS/*.sh 直接运行点——迁移后（仅 hook 留薄壳）需机械改调用方式；断言级变更仅集中在 5 个专门文件（约 30-40 用例）
[PROD_NOT_TOUCHED]
## pre-commit-gate.sh 薄壳关键结构已核实
- 复制模式 .agate-root 恢复：L31-38（readlink -f 解析软链 → dirname 两次 → 非软链时读 .agate-root 标记 + tr -d chr）
- L42-54 source workspace-resolve + gate-result 并验证函数已加载
- L190/207/224/284/290/298 等 bash 调 12 个子脚本；L101 python3 直接调用
[PROD_NOT_TOUCHED]
## 受影响 5 文件精确统计（^@test 法）
- check-platform-assumptions 14 + env-adapt-docs 9 + agate-scripts-encoding 2 + helpers-python 3 + agate-workspace-resolve 10 = 38 用例
- 全库 count-tests.sh 权威计数 = 727（不含 tests/scripts/）；含 tests/scripts 计 733+（dispatch 口径）
[PROD_NOT_TOUCHED]
## 反向依赖发现
- ci-gate-backstop.py（现有 py）经 bash subprocess 调 check-gate.sh（L54-55）与 agate-workspace-resolve.sh（L93-96）——这两个 sh 迁 py 后，ci-gate-backstop 需改为直接 python 调用（消除 _find_bash/WSL 规避逻辑的依赖面）
[PROD_NOT_TOUCHED]
## 数据收集完毕，开始撰写 P1-requirements.md
[PROD_NOT_TOUCHED]
## 撰写 P1-requirements.md（frontmatter 校验前置核实）
- P1 schema migrated_keys 含 change_type（refactor）；capability_requirements/requires_minimal_validation 非迁移键、被校验器忽略（无 unknown-key 拒绝），可安全写入
- 嵌套深度 MAX_DEPTH=3：capability_requirements 为 list[dict]（深度 2），合规
[PROD_NOT_TOUCHED]
## 自检通过：Header 完整 / 10 条 BDD（编号连续）/ NEED_CONFIRM 阻塞项 0 / 表 A-E 齐全 / 表 A 覆盖 30 个 sh 全量（差集空）
[PROD_NOT_TOUCHED]
## 完成：P1-requirements.md 已落盘并通过 frontmatter schema 校验（worktree check-frontmatter.sh exit 0）
[PROD_NOT_TOUCHED]
## requirements-review 开始
- 已读 dispatch-context（requirements-review）、角色定义、P0-brief、P1-dispatch-context-analyst、P1-requirements、分析报告
- 已核实：30 sh + 18 py 存在；行数总和 3813 与表 A 一致
- 已核实表 A 纯 bash/混合分类（11/19）与 source/调用关系（gate-result 3 方 source、workspace-resolve 3 方 source、pre-commit-gate 调 12 子脚本、retreat-to 依赖 archive + MAX_RETRY_MAP 文本耦合、inject-card 调 next-card）
- 已核实表 C CHECK 8 四行与 V06_KEYWORD_ASSERTIONS 完全一致；CHECK 9 涉 sh 锚点 32 条全量映射（含 2 个保留薄壳锚点）
- 已核实表 D：受影响断言文件 5 个计数 14/9/2/3/10=38 准确；机械调用面实为 30 个 bats 文件 / 379 处直接 bash run（314 AGATE_SCRIPTS + 65 AGATE_ROOT/scripts），"约 400" 成立
[PROD_NOT_TOUCHED]
## 表 B 核查发现（重点缺陷）
- dispatch-protocol：表 B 记 5 脚本/7 次，实际 10 脚本/22 次（漏 check-p6-format、check-state-transition、agate-inject-card、agate-archive-stale-outputs、agate-retreat-to；check-gate 6 vs 3、check-p6-provenance 4 vs 1）
- WORKFLOW：表 B 记 4 脚本，实际 12 脚本（漏 check-scope-resolved、check-state-transition、check-changelog、check-state-yaml、check-pruning、check-retrospective、agate-workspace-resolve、pre-commit-gate；check-gate 7 vs 2）
- state-machine：check-gate 5 vs 3、check-tdd-red 6 vs 4、check-p6-provenance 2 vs 1、漏 check-state-transition
- SETUP：install-hook 3 vs 2、agate-summary 4 vs 2、漏 agate-next-card
- UPGRADING：install-hook 3 vs 1、漏 check-gate(3)、check-p6-evidence、check-debt、pre-commit-gate
- LIMITATIONS：check-p6-provenance 3 vs 1、漏 check-gate(3)、check-p6-evidence、check-pruning
- orchestrator-template：漏 check-gate、agate-inject-card；task-files 漏 check-p6-provenance、check-scope-resolved；handoff 漏 agate-workspace-resolve；P6-acceptance 5 vs 1；tech-debt 3 vs 2
- 结论：表 B 系统性低估，核心交付不完整
[PROD_NOT_TOUCHED]
## BDD 判定核查发现
- BDD-3（ruff 扫 agate/scripts/*.py exit 0）：现有 18 py 用默认规则集有 70 个错误（ci-gate-backstop 14 / agate-debt-check 14 / agate-frontmatter-check 11 …，UP032×35/BLE001×9/PLW1510×6 等）——与「18 个既有 py 不改写」范围冲突，BDD-3 不可满足
- BDD-4/install-hook 去留歧义：表 C 同步点 3「install-hook.sh 保留」与「30 sh→py + shellcheck 收敛到 3 hook」潜在冲突
- BDD-6 扫描范围含 18 既有 py，其扫描洁净度未验证（风险项）
- BDD 编号连续 1-10、单 GWT、无中间态——格式合格
[PROD_NOT_TOUCHED]
## 评审结论起草：needs-revision
- 主缺陷：①表 B 系统性漏映射 ②BDD-3 不可满足（现有 py 70 ruff 错误）③install-hook 去留歧义 + BDD-6 扫描范围
- 优点：表 A/C/D/E 核实通过；隐含需求逐维度覆盖充分；裁剪/能力声明与 P0+分析报告一致

[PROD_NOT_TOUCHED]
## 修复轮启动（requirements-review → needs-revision → 3 项 must-revise）
- 已读修复轮 dispatch-context + P1-review.md + 上轮 dispatch-context + P0-brief
- 已按评审口径对 worktree 全部相关文档逐次实测（rg -o）：dispatch-protocol 10 脚本/22 次（含 check-p6-evidence 2——评审头条 22 的还原项）；WORKFLOW 12 脚本/22 次（评审组件逐项合计即 22）；state-machine 6/17；SETUP 4/11；UPGRADING 8/14；LIMITATIONS check-p6-provenance 按行计 3（第 118 行同行两次，逐次计 4，本表按评审口径记 3）；orchestrator 6/7；task-files 4/6；handoff 4/4；P6-acceptance 5；tech-debt 3

[PROD_NOT_TOUCHED]
## 修复项 1（表 B 系统性低估）已落盘
- 按评审逐文档实测全面更新表 B：dispatch-protocol 10 脚本/22 次、WORKFLOW 12 脚本/22 次（组件合计与评审一致，评审头条 21 为算术笔误）、state-machine 6/17、SETUP 4/11、UPGRADING 8/14、LIMITATIONS 4/8（p6-provenance 按行口径 3，第 118 行同行两次已注脚）、orchestrator 6/7、task-files 4/6、handoff 4/4、P6-acceptance 5、tech-debt 3
- 迁后目标列与表 C 命名一致（同名换后缀 .py；3 个 hook 保留薄壳；install-hook.sh → install-hook.py）；git-integration / scripts/README.md / CI 定性描述维持不构成问题

[PROD_NOT_TOUCHED]
## 修复轮完成自检
- BDD-1..10 编号连续；frontmatter 未变（risk_level: high / phases 全 / packages / domains: [backend, cli] / change_type: refactor / capability_requirements）
- 无 [NEED_CONFIRM]；[NO_NEED_CONFIRM] 保持
- 仅改动 3 项 must-revise 相关处：表 B（实测数据更新）、BDD-3（ruff 全量范围 + P2 pyproject.toml 交付）、install-hook 去留（BDD-4/BDD-6/BDD-9 Given + 表 C 同步点 3 + §2.5 ruff 边界 + §2.6 前置验证）
- 表 A/C（除同步点 3）/D/E、§2.1-2.4、裁剪三态未动
- 未改生产代码（仅任务产物文件）

[PROD_NOT_TOUCHED]
## requirements-review 复评（round 2）完成 → approved
- 已读：上轮 P1-review.md、修订后 P1-requirements.md、修复轮 dispatch-context-analyst-fix、P0-brief、requirements-review 角色
- 修复项1（表 B）：11 文档逐格独立重扫（rg -o）全与修订表一致（dispatch 10/22、WORKFLOW 12/22、state-machine 6/17、SETUP 4/11、UPGRADING 8/14、LIMITATIONS 4/8 按行口径 3 已注脚、orchestrator 6/7、task-files 4/6、handoff 4/4、P6-acceptance 5、tech-debt 3）；WORKFLOW「21 次」系上轮头条算术笔误，实测 22
- 修复项2（BDD-3）：全量 py 范围/P2 pyproject.toml 交付/既有 py 最小调整边界三决策全落盘（:266-269、:80-81）
- 修复项3（install-hook+BDD-4/6）：install-hook.py 化、3 hook 保留薄壳、BDD-4 Then 与 3 薄壳一致（:274）、BDD-6 P2 前置（:283、:89）全显式
- 抽查：BDD 1-10 连续、frontmatter 未变、表 C CHECK9 仍 32 锚点、无 NEED_CONFIRM
- 产出：P1-review-round2.md status=approved
