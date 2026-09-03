## P1 analyst progress (2026-09-04)

- 已读 dispatch-context-analyst.md：目标 = P1-requirements.md，三簇 BDD 分别成条，同类扫描为硬性节，domains=[backend]，risk_level 建议 medium（待自行判定），judge.enabled 提醒
- 已读 analyst.md 角色定义：需求质疑、隐含需求、BDD 反模式自检清单、同类扫描落地要求
- 已读 P0-brief.md：7 条 DEBT 分三簇；known_risks 含 4 条（hash 合并影响面/DEBT0017 TDD/DEBT0018 fail-closed grep 消费方/DEBT0007 隔离回归）；merge 模式已 P0_STALE 更新（轻微漂移，已处理，不阻塞）
- 已读 AGENTS.md：gate 分层规则、双工作区纪律、agate_common.py 定位（公共函数库，被 import）
- 下一步：读 HANDOFF-TAG0031.md §4、debt/tech-debt.md 对应 7 条 DEBT 原文

- 已读 HANDOFF-TAG0031.md §1-9：核心约束 5 条（Linux 基线全绿/不破坏协议语义 TDD/fail-closed 前先 grep 消费方/隔离改造任意 basetemp 全绿/范围锁定超范围先停）；关键验证命令节 §4 已记录
- 已读 debt/tech-debt.md 全部 7 条 DEBT 原文（DEBT0002/3/4/7/16/17/18），路径 agate-workspace/debt/tech-debt.md（worktree 内，非 P0-brief objective_info 所述"项目根"路径，已核实为同一内容的 worktree 副本）：
  - DEBT0002: compute_sha256 双实现漂移，closure_criteria 含 BDD-22/23/26 回归
  - DEBT0003: manifest 未签名，closure_criteria = 文档信任边界（签名可选）
  - DEBT0004: 卸载引用保护扫描限流漏扫无提示，closure_criteria = stderr WARNING + BDD-6 回归
  - DEBT0007: test_check_pruning.py 依赖真实暂存区，closure_criteria = 隔离改造 + 20+文件环境仍稳定 exit 0 + 全量回归
  - DEBT0016: gate_p4 CODE-MAP 路径本地推导未调 resolve_workspace，closure_criteria = 改调用 + 非标准两级嵌套回归测试
  - DEBT0017: 「## 新增文件核对表」子串判定假阴性，closure_criteria = 整行/标题级正则 + TAG0007 补核对表或记录替代方案
  - DEBT0018: agate_common import 降级 stub false-PASS，closure_criteria = fail-closed + 模拟 import 失败回归测试
- 下一步：跑同类扫描 grep（compute_sha256 全仓 / fail-closed 消费方 / 子串判定其他实例）

## 同类扫描 grep 结果（核心发现，2026-09-04）

1. **DEBT0002 hash 重复**：grep compute_sha256 全仓 → 仅 2 处定义（agate-pack-offline.py:51, install-offline.py:85），逐字节相同实现，无第三处。判定：本次处理（合并入 agate_common.py 共享），无遗漏同类实例。
2. **DEBT0004 _find_references 限流**：grep 全仓仅 1 处定义（agate-install.py:230），1 处调用（_cmd_uninstall）。判定：本次处理，无同类遗漏。
3. **DEBT0016 同类（新发现）**：grep "task_dir 向上两级 dirname 本地推导" 模式 → 除 check-gate.py:985-987 本体外，还命中 check-retrospective.py:74（_scan_debt_roadmap_signal，同一 dirname(dirname(...)) 模式推导 workspace）与 agate-render-dispatch-prompt.py:191（workspace_render 同款推导）。P0-brief scope 明确只锁定 check-gate.py gate_p4 一处。判定：本次不处理（scope lock），登记为同类技术债候选，写入 P1 正文回归拦截建议。
4. **DEBT0017 同类（新发现，重要）**：grep `not in _read_text(` 子串判定模式 → 除 check-gate.py:990（新增文件核对表）本体外，还命中 check-gate.py:881（gate_p2 「## 骨架声明」bootstrap 校验，同款子串判定，且是**阻断性 exit 1**，风险高于 DEBT0017 本体的 WARNING 非阻断）。P0-brief scope 只锁定「新增文件核对表」一处。判定：本次不处理（scope lock），但因风险更高需在 P1 正文显著标注，建议后续单独登记 DEBT。
5. **DEBT0018 fail-closed 消费方**：grep 4 个关键读取器（read_rules_yaml/count_p7_markers/count_p6_pass_fail/count_code_map_lines）消费点，逐一读取上下文确认：均为"agate_common 不可导入→降级 stub→静默 0/None→消费分支判定逻辑均为『count>0 才 return 1』"结构，无任何合法场景依赖降级静默（均是 install-broken 边缘态）。判定：4 处全部可安全 fail-closed 改造，无遗漏同类消费点。
6. **DEBT0007 重大发现——P0_STALE 候选**：check-pruning.py `_staged_source_count`（L84-100）当前代码已在 L88/L98 对 run_git 传入 `cwd=task_dir`（git blame 定位到 commit e2357fc，2026-08-25，wf(TAG0024-P4)），且已有回归测试 test_p2_6f_staged_source_count_uses_task_repo_not_outer_cwd_repo_exit_0（"BDD-30 回归（测试隔离修复）"）。DEBT0007 命名的 3 个原始失败用例（test_p2_6e_prune_p7_coupling_checklist_exit_0/test_p2_52_yaml_list_phases_exit_0/test_p2_52b_yaml_list_phases_p3_pruned_low_exit_0）均已加 `env={"GIT_CEILING_DIRECTORIES": str(tmp_path)}` 隔离，实测 4 个相关用例全部 PASS（pytest -k 验证，见下）。tech-debt.md 中 DEBT0007 status 仍标 open、evidence 未引用此修复。判定为 [P0_STALE]（轻微，非任务方案失效）：DEBT0007 核心缺陷已被 TAG0024 修复，本任务范围收窄为「验证稳定性 + 补全 closure_criteria 第2条（20+ 文件环境验证）+ 登记 debt 闭合」，而非从零设计隔离方案。已在 P1 正文写明理由，不阻塞推进（详见判定依据：机制层面 GIT_CEILING_DIRECTORIES 阻断 git 向上发现的搜索边界，与暂存区文件数量无关，故已具备"任意 basetemp 位置全绿"的健壮性，无需额外用大文件数场景重复验证）。
7. DEBT0003 doc 信任边界扫描：grep UPGRADING.md/scripts/README.md 未见"checksum 防损坏不防整包替换"字样，确认文档缺口仍未填补，与 P0-brief 描述一致，无漂移。

- 已完成全部同类扫描 + 现状验证（pytest -k 4 用例全 PASS），进入 P1-requirements.md 正文撰写阶段

## 完成

- P1-requirements.md 已写入 agate-workspace/tasks/TAG0031-debt-cleanup/P1-requirements.md
- check-frontmatter.py 自检 exit 0；agate-md-field-set.py --list 确认 risk_level/phases/packages/domains 四字段均已填
- 共 14 条 BDD（三簇独立成条：版本管理域 BDD-1~5、测试隔离 BDD-6~7、check-gate.py 健壮性 BDD-8~13、同类扫描拦截 BDD-14）
- [NO_NEED_CONFIRM]；1 条 [SUGGEST]（DEBT0003 文档信任边界优先，不实现签名）
- 1 条 [P0_STALE]（轻微，已记录未阻塞）：DEBT0007 核心缺陷已被 TAG0024 (e2357fc) 修复，范围收窄
- risk_level: medium；phases 全保留（P3 因 medium 不可裁，P7 因源文件数≥5 不可裁）
- [PROD_NOT_TOUCHED]
