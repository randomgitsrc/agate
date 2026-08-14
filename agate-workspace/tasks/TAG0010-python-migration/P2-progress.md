# P2 进度（architect）

## 输入读取
- [x] P2-dispatch-context-architect.md（派发指引）
- [x] architect.md 角色定义
- [x] AGENTS.md 项目约定
- [x] P0-brief.md（env_constraints / known_risks）
- [ ] P1-requirements.md
- [ ] P1-review.md
- [ ] 分析报告 docs/reviews/agate-python-migration-analysis-20260814.md
- [ ] 现有代码：check-gate.sh / pre-commit-gate.sh / gate-result.sh / agate-workspace-resolve.sh / check-protocol-consistency.py

## 关键发现
（待填）
- [x] P1-requirements.md（10 BDD + 表 A-E 全读完）

## P1 关键要点（P2 设计输入）
- 表 A：30 sh，批次 0-4；表 C：CHECK8/9 锚点映射 + 4 项结构性同步点
- 约束：同名换后缀、非 hook 不保留薄壳、py3.8+、encoding=utf-8 强制、pyyaml 强制
- ruff 规则集是 P2 交付物（默认 70 错误基线）
- minimal_validation 必须产出
- [x] P1-review.md（approved，3 修复项确认）
- [x] 分析报告 docs/reviews/agate-python-migration-analysis-20260814.md（§3.1 hook 薄壳设计依据 + §9 验收标准）

## 分析报告要点
- hook 薄壳 ~15 行：shebang + AGATE_ROOT 自定位 + 复制模式 .agate-root 恢复 + exec python3
- Windows 命令名 python 非 python3；git 自带 bash
- [x] gate-result.sh（105 行全读：write_gate_result / read_state_phase / read_state_task_id / has_staged_phase_change / has_staged_phase_output / resolve_formatter / run_test_with_formatter）
- [x] agate-workspace-resolve.sh（57 行）

## gate-result.sh 函数库要点（→ agate_common.py）
- write_gate_result: .gate-result.json 生成 + .gate-history.jsonl 追加；依赖 agate-json-get.py escape + git rev-parse HEAD
- read_state_phase/task_id: 通过 agate-state-get.py 读 state 文件字段
- has_staged_phase_change: git diff --cached --name-only + tr -d '\r' + grep '^\+.*phase:'
- has_staged_phase_output: git diff --cached --name-only + grep 'P[0-9]+-.*\.(md|yaml)$'
- resolve_formatter / run_test_with_formatter: formatter 解析 + timeout 包装 + JSON 结构（AGATE_TDD_TIMEOUT）

## 恢复会话继续（2026-08-14）
已完成（上次会话）：
- [x] check-gate.sh（488 行全读：P0-P8 case 分支 / CRLF 容错 sed 模式 / grep -c | tail -1 / FILE= python3 调用）
- [x] pre-commit-gate.sh（404 行全读：AGATE_ROOT 自定位 + 复制模式 .agate-root 恢复 L31-38 / 调度 12 子脚本 / PROD_TOUCHED 三步检测 / dispatch-context hash 校验 / write_gate_result）
- [x] check-protocol-consistency.py（L430-769：V06_KEYWORD_ASSERTIONS + SCRIPT_ALIGNMENT_ANCHORS + GATE_SCRIPT_EXEMPT + check_anchor_coverage glob=check-*.sh + CHECKS 列表）
- [x] 其余 hook：commit-msg-self-gate.sh（37 行）/ pre-push-gate.sh（28 行）/ install-hook.sh（93 行）
- [x] check-platform-assumptions.sh（扫描器规则 R1-R5 + 扩展名过滤）
- [x] check-tdd-red.sh（216 行：read_gate_commands / judge_result A/B 类 / resolve_formatter）
- [x] ci-gate-backstop.py（282 行：_find_bash/_bash_cmd WSL 规避 → 需 py 化直接调用）
- [x] 表 D bats：check-platform-assumptions.bats(14) / env-adapt-docs.bats(9) / agate-scripts-encoding.bats(2) / helpers-python.bats(3) / agate-workspace-resolve.bats(10)
- [x] fixtures.bash（detect_python / create_python_shim_bin / py_path）+ count-tests.sh + protocol-tests.yml

## 最小验证已完成（上次会话实测）
1. hook 薄壳 exec 失败回退：python 存在 → exec py 成功；python3 stub exit 127 + python 缺失 → 回退 sh fallback（非静默）✓
2. 复制模式 .agate-root 恢复：readlink 解析到副本 → scripts/ 不存在 → 读 .agate-root 恢复 AGATE_ROOT ✓
3. ruff 规则集：select=[E4,E7,E9,F,W,I,UP,B,SIM,C4,RUF,PLW] + ignore 列表 → 既有 18 py 经 --fix(54 个行为保持) + 6 个行为保持重构 → 0 违规 ✓
4. py38 语法：ast.parse(feature_version=(3,8)) 拒绝 match ✓；ruff target-version py38 拒 match ✓；str.removeprefix 两种方式都查不出 → 需 grep 守卫

## 补充验证（恢复会话）
- gate_commands 解析格式确认：agate-read-gate-commands.py 读 P3* + project_module（2 空格缩进、`key: val`）；agate-gate-p5-count.py 读 P5/P5_*（_formatter 排除）
- ruff 最终基线（0.16.3）：68 错误 = UP032×35/BLE001×9/PLW1510×6/SIM115×4/FURB167×3/F541×2 + 单数（UP031/SIM905/SIM103/SIM102/S112/S110/RUF059/I001/F401）——P1 说 70 系 ruff 版本差异
- **发现（表 C 同步点 4 的边界）**：glob 改 `check-*.py` 后 `check-protocol-consistency.py` 自身无锚点 → 必加 GATE_SCRIPT_EXEMPT 或专用锚点，否则 CHECK9-coverage WARNING → --strict 挂（BDD-2 破坏）
- 锚点表涉 sh 条目 16 个（check-gate×6/check-pruning×6/pre-commit-gate×1/pre-push-gate×1 + 其余各 1）
- GATE_SCRIPT_EXEMPT 现含 stale agate-init.sh（目录无此文件）；迁移后仅需 check-protocol-consistency.py + pre-commit-gate.py
- formatter 目录有 generic-tap.sh（bats TAP 输出可复用）

## P2-design.md 已产出
- [x] 写出 P2-design.md（candidate_count: 3，含权衡/选择理由）
- 自检中（frontmatter 四字段 / minimal_validation / gate_commands / files_to_read）

## 自检通过
- frontmatter 四字段齐全（candidate_count: 3 / packages 6 项 / domains / ui_affected: false）✓
- gate_commands 已声明（P3 bats + formatter + P5 主命令 + 4 辅助）✓
- minimal_validation 5 条（2 confirmed + 2 confirmed + not_needed）✓
- files_to_read 12 项（含行号范围）✓
- 候选方案 3 个 + 权衡表 + 选择理由 ✓
- 无行首 PASS/FAIL ✓
- 381 行非空 ✓

## plan-eng-review 进度
- 读 dispatch-context（强制指令）✓
- 读角色文件 plan-eng-review.md ✓
- 读 P0-brief.md ✓
- 读 P1-requirements.md（10 BDD + 表 A-E）✓
- 读 P2-design.md（被审对象，381 行）✓
- 读分析报告 §1-10 ✓
- 核实 gate-result.sh / agate-workspace-resolve.sh / pre-commit-gate.sh / ci-gate-backstop.py / check-platform-assumptions.sh / check-protocol-consistency.py（锚点表）✓
- ruff 实测：pyproject.toml 建议规则集对既有 18 py 报 60 错误（54 自动修复 + 6 unsafe），--fix --unsafe-fixes 后 0 剩余 ✓ 设计 §3.4 声明成立
- py38 target 实测：`match` 被拒（invalid-syntax）✓ BDD-8 成立
- 死 ignore 实测：E501/PLR0911/PLC0415 等不在 select 内，无告警、不影响规则集
- 扫描器实测：扩展 .py 后既有 18 py 有 3 处 R2 命中（docstring 示例，均非 # 注释行）——BDD-6 前置验证缺口
- 发现批次 0 依赖矛盾：ci-gate-backstop.py 在批次 0 即改调 check-gate.py（批次 2 才产出）+ 删除 _bash_cmd（check-tdd-red.sh / check-p6-provenance.sh 批次 2 才 py 化）→ 批次 0 验证自相矛盾
- 发现 hook 薄壳 fallback 与 P1 BDD-9「回退到保留的 sh 逻辑」字面冲突：设计选择 fail-closed（error+exit 1），非运行旧 sh 逻辑
- 评审结论：rejected（2 个阻塞级 + 2 个非阻塞级）

## 修复轮（architect-fix，2026-08-14）
- 读修复轮 dispatch-context（3 BLOCKER + 2 非阻塞 + 主 Agent 决策）✓
- 读 P2-review.md（rejected，§BLOCKER-1/2/3 + 非阻塞 2 项）✓
- 读上轮 P2-dispatch-context-architect.md（约束复用）+ P2-design.md（被修订对象）✓
- 读 P1-requirements.md（BDD-9 已含 BASELINE_CHANGE 标注 :302）✓
- 实测复核：扩展 .py 后既有 18 py 命中 4 行 R2（agate-json-get.py:5 docstring、check-protocol-consistency.py:23-25 docstring），与评审证据一致 ✓
- 修复项 1（BLOCKER-1）开始：设计新增 docstring 豁免 + BDD-6 前置验证方案 + §3.6 两类用例
- 修复项 1（BLOCKER-1）完成：§3.2 批次 1 新增 BDD-6 前置验证执行方案（预期违规 4 行 docstring R2 清单 + docstring 豁免处理方式 + 零命中目标）；§3.6 check-platform-assumptions.bats 补⑥docstring 豁免两类用例（14→16 用例，38→40 总用例）
- 修复项 2（BLOCKER-2）完成：§3.2 批次 0 收窄为 resolve_tasks_dir 改调 agate_common.resolve_workspace；_bash_cmd 保留到批次 2；run_gate 切换移入批次 2；批次 0 验证口径更新（仅 workspace 解析相关断言）
- 修复项 3（BLOCKER-3）完成：§3.3 fallback 语义改为 fail-closed（注释/描述/commit-msg grep 承载改准确 + 引用 P1 BDD-9 BASELINE_CHANGE）；§2 风险点表述同步；§8 完成标志 hook 行同步 fail-closed
- 非阻塞-1 完成：§3.4 pyproject.toml 死 ignore 清理（E501/PLR0911-0915-2004/PLC0415 移除 + 说明）
- 非阻塞-2 完成：§5 files_to_read 补 pre-push-gate.sh / commit-msg-self-gate.sh
## 修复轮自检（返回前）
- frontmatter 不变：candidate_count: 3 / packages 6 项 / domains / ui_affected: false ✓
- 方案 A/B/C 表述未动；gate_commands / minimal_validation / env_constraints 未动 ✓
- grep 复核：fail-closed（§3.3/§2/§8）、BLOCKER-1/2/3 修订行、docstring 豁免、run_gate 批次 2 切换、files_to_read 两薄壳源均已落盘 ✓
- 修订处与 P2-review §BLOCKER-1/2/3 + 非阻塞 2 项一致 ✓

## plan-eng-review 复评（round2）
- 读上轮 P2-review.md（3 BLOCKER + 2 非阻塞基准）✓
- 读修订后 P2-design.md（复评对象）+ P2-dispatch-context-architect-fix.md（修复要求）✓
- 实测复核 BLOCKER-1：agate-json-get.py L1-12 / check-protocol-consistency.py L2-26 docstring 内 R2 命中成立 ✓
- 实测复核 BLOCKER-2：ci-gate-backstop.py run_gate(:50-58)/_bash_cmd(:181-184/:267-270) 调用关系成立 ✓
- 实测复核 BLOCKER-3：P1-requirements.md:302 BDD-9 BASELINE_CHANGE 标注确认 ✓
- 锁定部分抽查：frontmatter / 方案 A-C / gate_commands / minimal_validation / env_constraints 未动 ✓
- 复评结论：approved（3 BLOCKER + 2 非阻塞全部修订到位，0 阻塞问题）
