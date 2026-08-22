# P4 实现进度（TAG0020 — implementer：scripts 批 + docs 批）

> 本文件由 implementer 分阶段追加（每读完 1 个输入文件 / 每写完 1 个实现文件立即落盘）。
> 批次：serial 第①层 脚本层（已完成，见下方 scripts 批节）+ 第②层 docs 批（本轮：ci-gate-backstop 兜底 + 协议文档 8 处）。
> 产出路径：worktree `agate/` 各文件。

## docs 批输入读取（已完成）

1. ✅ P4-dispatch-context-implementer-docs.md（强制指令：judge.md 先行 / 文档与 scripts 批实现一致 / 纯增量 / 每处追加进度 / 返回两行）
2. ✅ design-independent-judge.md（§3 角色设计 / §4 三层防造假 / §5 三档预算 / §6 状态机与 judge 字段——注意其 §6 `retries.P6.5` 已被 P2 候选 1 否决：不新增 retries.P6.5 键/重试表行，judge 轮次以 prose + judge.rounds + 账本事件计数承载）
3. ✅ ci-gate-backstop.py（worktree 全文：main() 结构、provenance 兜底 L234-244 注入点、_run_python 模式）
4. ✅ 文档格式先例：qa.md（review-role frontmatter/产出/status 门槛映射）、role-system.md（L37-51 评审名册 + L104-118 status 三值映射）、WORKFLOW.md（L282-301 总览表 + L61-68 角色清单树）、state-machine.md（L71-144 转移规则 + L386-463 重试上限/每任务状态文件）、dispatch-protocol.md（L306-383 dispatch-context 规范 + AGATE_CARD 注入 + 冻结语义）、dispatch-prompt.md（L105-174 阶段特定提示结构）、P6-acceptance.md（L9-20 派发步骤 + L169-182 gate 规则 + L199-204 推进条件）、LIMITATIONS.md（L21-48 局限 3 现状/降级缓解段）

## 输入读取（已完成）

1. ✅ 角色定义 `agate/assets/execution-roles/implementer.md`（P4 只实现 P2 方案、不改测试、自查≠gate、[SCOPE_GAP]/[DESIGN_GAP] 标注纪律）
2. ✅ P4-dispatch-context-implementer-scripts.md（强制指令：5 文件实现顺序 + 测试驱动 + 每写完 1 文件追加 progress + 环境纪律）
3. ✅ P0-brief.md + AGENTS.md（项目约定：平台无关、测试约定、bash timeout 90s、单步串行）
4. ✅ P2-design.md（候选 1+3a；§3.2 事件 schema / §3.3 check-judge-verdict 9 步链 / §3.4 check-events 审计链 / §3.5 gate_p65 + pre-commit 注入伪代码；§4 串行批次；files_to_read 导航）
5. ✅ P1-requirements.md（10 条 BDD 权威定义；BDD-4 黑名单/白名单路径引用集）
6. ✅ P3-test-cases.md（BDD→测试文件 1:1 映射）
7. ✅ 测试代码：test_check_judge_verdict.py（29 用例）/ test_check_events.py（12 用例）/ test_check_gate.py 增补（6 用例）/ test_agate_common.py 增补（5 用例）/ conftest.py（fixtures：task_dir/agate_scripts/python_exe/run_cli/add_p1_bdd）
8. ✅ 源脚本：agate_common.py（write_gate_result 模式 / MAX_RETRY_MAP 不动）/ check-p6-provenance.py 审计 2（AGATE_CARD+frontmatter 双排除 + 行首预判 L318-355）与审计 3（`^#### BDD-[0-9]` 计数 L371）/ check-p6-evidence.py `_md5_entries`（L96-106）/ check-gate.py（gate_p6 L791-840 不改 + handlers L1082-1092 + _read_text/_frontmatter 等 helper）/ pre-commit-gate.py（2h.1 gate 运行 L324-331 / 2i provenance L333-335 / 2p L350-398 / phase_changed+old_phase 机制 L213-248）

## 关键设计裁决（实现时落定）

- **证据核对以 `P6-evidence/` 目录存在为前提**：`test_bdd_4_frontmatter_excluded_not_flagged_exit_0` 未创建证据目录仍期望 exit 0，而 `test_bdd_6_*` 目录存在时校验严格 → 证据存在性/非空/md5/对称全部 gate 在 `os.path.isdir(P6-evidence)` 之下（测试是验收口径，以此为准）。
- **judge.enabled 读取**：check-gate gate_p65 用本地 `_load_state_yaml` 模式（仿 check-p6-provenance L209-221，yaml 缺失静默回退空 dict）；pre-commit-gate 同样本地实现，不新增 agate_common 公共函数（保持 P2 声明的 agate_common 改动面 = append_event/read_judge_verdict/GENESIS_HASH）。

## 实现记录（scripts 批）

1. ✅ **agate_common.py**（修改）：新增 `import hashlib` + `GENESIS_HASH`（sha256(b"").hexdigest() 模块常量）+ `append_event(task_dir, event)`（自动补 ts UTC 微秒 + prev_hash 行间哈希链续接尾行原始文本 + ts 单调兜底 max(now, 尾行) + IOError 仅 WARNING 不抛）+ `read_judge_verdict(task_dir)`（frontmatter --- 块解析返回 {status, criteria_total, criteria_passed, verdict_evidence, partial}，缺失/解析失败 → None）。MAX_RETRY_MAP 未动。

2. ✅ **check-judge-verdict.py**（新建）：P2 §3.3 九步校验链——① verdict 存在且非空 ② dispatch-context 存在且非空 ③ Header 字段（status 三值/整数计数/verdict_evidence 存在）④ BDD 对照（`^#### BDD-[0-9]` 计数 + 结论编号集相等 + 条目数==criteria_total）⑤ passed 三数全等 + partial+passed 拦截 ⑥ 证据交叉核对（存在/非空/md5 去重/引用对称，gate 在 P6-evidence/ 目录存在前提下）⑦ 信息隔离白名单（两节黑名单串大小写不敏感 + 白名单外路径 + 全文行首预判，AGATE_CARD/frontmatter 双排除复用审计 2）⑧ 账本 budget_exhausted 交叉（须 needs-revision+partial）⑨ 通过后 append_event 记 judge_verdict。

3. ✅ **check-events.py**（新建）：P2 §3.4 审计链——账本缺失/空 → 合法态 exit 0；逐行 JSON 可解析；首行 prev_hash==GENESIS_HASH；逐行 prev_hash==sha256(上一行原始文本)（改写检测）；ts 单调不减；judge_verdict 事件计数 ≤2（轮次预算兜底）；未知 event 类型不拦截。

4. ✅ **check-gate.py**（修改）：新增 `_load_state_yaml`（仿 provenance L209-221）+ `_run_gate_script`（子脚本 stderr 透传 + fail-closed）+ `gate_p65`（judge 未启用 → 早退 0 含「跳过」输出；启用缺 verdict → exit 1；否则依次调 check-judge-verdict/check-events 任一 exit 1 → exit 1）；handlers 注册 `"P6.5": gate_p65`。gate_p6 未改。

5. ✅ **pre-commit-gate.py**（修改）：① import 增 `append_event` ② 新增 `_judge_enabled(task_dir)`（读 .state.yaml judge.enabled，缺失/解析失败 → False，BDD-2）③ 2h.1 write_gate_result 后追加 `gate_run` 事件（append_event，异常仅 WARNING 不阻断）④ phase_changed 时追加 `state_transition` 事件（from=old_phase/to=phase，双写不改写）⑤ 2i 后新增 2i.1 P6.5 注入（gate_exit!=1 && _judge_enabled && verdict 存在 → check-judge-verdict/check-events 任一 exit 1 → sys.exit(1)，commit-time 硬边界与 commit 位置解耦）。

## 实现记录（docs 批）

1. ✅ **judge.md**（新建 `agate/assets/review-roles/judge.md`）：review-role 统一 frontmatter（role_id: judge / type: review / phases: [P6.5] / agent: judge）；定位 = P6.5 fresh context 逐条重验所有 BDD（零挑验）；认知模式四条（全量重验/只信证据与 git log/每条结论引证据/禁"看起来没问题"式结论）；白名单输入 5 项 + git log 查询权；黑名单禁项与 check-judge-verdict.py 实现一致（P6-acceptance.md / P[4-6]-dispatch-context-* / P4-implementation / P4-review / P5-test-results/ / 行首 PASS|FAIL 预判 / agate-extract-context 禁用或净化）；verdict 产出格式（Header 四字段 + partial + 正文结论行）；三档预算与诚实降级（轮次≤2 + token 100k + 30min → partial:true + needs-revision）；机械核对红线（双脚本 exit 0 才是门槛）；status 三值映射；double-judge 可选（文档级）。

2. ✅ **ci-gate-backstop.py**（修改，SCOPE_GAP 补齐）：新增 `_judge_enabled(task_dir)`（读任务 .state.yaml judge.enabled，缺失/解析失败 → False）+ provenance 兜底后新增 judge/events 兜底（注入条件与 pre-commit 2i.1 一致：judge.enabled && P6.5-judge-verdict.md 存在 → 依次跑 check-judge-verdict/check-events，任一 exit 1 → FAIL return 1；--no-verify 绕过 hook 时 backstop 层补跑，BDD-1/10）。

3. ✅ **state-machine.md**（修改）：① 状态集合注记——显式声明 P6.5 是挂载于 P6→P7 转移的强门槛子阶段、非独立 phase 值（valid_phases/重试表/卡片枚举零扩展）② P6→P7 转移改 P6→P6.5，P6 块后新增 P6.5 转移描述（通过条件 = verdict 存在 + check-judge-verdict/check-events 双 exit 0 → P7；needs-revision/rejected → 弹回 P6 重验，judge.rounds + 账本事件计数 ≤2 兜底；历史任务早退跳过；commit-time 由 pre-commit 2i.1 + ci-gate-backstop 兜底）③ 重试上限节新增 P6.5 轮次预算 prose（**未加 `| P6.5 |` 表行**、未用 retries.P6.5 键，CHECK 12 零漂移，R10）④ .state.yaml 示例新增 judge 字段块（enabled/rounds/last_verdict/partial/judge_token_budget/double_judge 注释）+ 字段说明。

4. ✅ **WORKFLOW.md**（修改）：① 角色清单树 review-roles 登记 judge.md（P6.5 所有任务强制）② 阶段总览表 P6 行后新增 P6.5 行（执行角色 judge 强制；门槛 = verdict 存在 + check-judge-verdict/check-events 双 exit 0；历史任务早退；主 Agent 跑 check-gate.py P6.5 判定），P6 行 self-authored 缓解标注增补"P6.5 judge 独立复核强化缓解" ③ P6/P7 区别段后新增「P6.5 judge 复核（强制）」说明段（fresh context 零挑验/只信证据与 git log/不读 P6-acceptance/预算三档/exit code 才是门槛）。

5. ✅ **dispatch-protocol.md**（修改）：dispatch-context 规范节后新增「Judge 信息隔离（P6.5，TAG0020）」节——白名单输入 5 项 + git log 查询权；黑名单禁注入（与 check-judge-verdict.py 实现同源：P6-acceptance.md / P[4-6]-dispatch-context-* / P4-implementation / P4-review / P5-test-results/ + 行首 PASS|FAIL 预判）；AGATE_CARD + frontmatter 双排除（复用审计 2）；agate-extract-context.py 在 P6.5 禁用或净化为仅白名单路径（上游关联注入面防泄漏）；P6.5 派发流程 6 步（P6 commit 后写 P6.5-dispatch-context-judge.md → 方法 B 派发 → verdict 产出 → check-gate.py P6.5 → 随 commit 落库 phase 保持 P6 → 弹回重验）；沿用派发后冻结语义。

6. ✅ **phase-cards/P6-acceptance.md**（修改）：① 派发步骤区新增步骤 10「P6.5 judge 复核（强制，所有任务）」（P6 commit 后写 P6.5-dispatch-context-judge.md → 派 judge → verdict → check-gate.py P6.5 → 随 commit 落库 phase 保持 P6 → 写 phase: P7）② gate 规则代码块追加 `check-gate.py P6.5`（双脚本 exit 0；历史任务跳过）③ 推进条件新增「P6.5 judge 复核通过（强制）」checkbox。

7. ✅ **assets/templates/dispatch-prompt.md**（修改）：阶段特定提示区「P5/P6 派发追加」之后新增「Judge 派发追加（P6.5，强制所有任务）」节——信息隔离清单（白名单输入 5 项 + git log 查询权；黑名单禁项含 P6-acceptance.md / P[4-6]-dispatch-context-* / P4-implementation / P4-review / P5-test-results/）；三档预算声明 + 超限诚实降级（needs-revision + partial: true，禁 passed 静默放行）；认知约束（逐条重验所有 BDD 零挑验 / 只信证据与 git log / 禁"看起来没问题"式结论）；verdict 产出格式（Header 四字段 + partial + 结论行格式 + criteria_total==P1 BDD 数）。

8. ✅ **role-system.md**（修改）：① 第二层评审名册表新增 judge 行（插入阶段 P6.5，所有任务强制，fresh context 重验全部 BDD）② status 三值映射表说明段新增 judge verdict 三值复用（passed→approved / needs-revision→needs-revision / rejected→rejected）+ 明示 judge **不进 C8 表**（强制所有任务与 domain/risk 触发语义不同）。

9. ✅ **LIMITATIONS.md**（修改）：局限 3「现状」段后新增「P6.5 独立 Judge 缓解链（TAG0020 已落地）」段——judge fresh context 零挑验重验 + 信息隔离白名单 + 证据交叉核对/BDD 计数对照 + append-only 事件账本哈希链审计；明示 judge LLM 结论不单独放行（exit code 才是门槛）；**仍声明"缓解而非根治"**（judge 结论语义不受机械核对覆盖，局限 3 结论不变）。
10. ✅ **AGENTS.md**（修改，超出 docs 批 8 处清单但属 P2-design §1.1 声明面 + test_docs_assertions::test_bdd_10_agents_role_list_judge_registered 测试驱动）：协议本体入口角色文件清单 review-roles 登记 judge.md（P6.5 验收独立裁判，所有任务强制）。

## docs 批自跑验证（自查 ≠ P5 gate）

- ✅ test_docs_assertions.py（TAG0020 增补 9 断言全过）+ test_ci_gate_backstop.py + test_review_role_docs.py：**39 passed**（修正 1 处：dispatch-protocol 补 `budget_exhausted` 账本 schema 文档化后转绿）
- ✅ 协议文档回归切片（protocol_mechanism_anchors / self_gate_naming_docs / p2p4_boundary_docs / protocol_dedup_audit / check_protocol_consistency / retrospective_protocol_docs / dispatch_orchestration）：**107 passed**——docs 批零 collateral
- ✅ scripts 批既有绿（41 + 182 + 55 + backstop + 143）不受 docs 批影响；6 脚本 py_compile 全净
- ✅ **consistency 检查（worktree 自身 check-protocol-consistency.py --strict-errors-only）= 0 ERROR**（320 WARNING 不阻断）
- 已知 WARNING（非阻断，供 P7 关注）：check-judge-verdict.py / check-events.py 未纳入 check-protocol-consistency.py 的 CHECK 9 锚点表（SCRIPT_ALIGNMENT_ANCHORS）——该文件不在 P2 改动表内，未改，P7 一致性评审可评估是否回补锚点

## 产出文件清单（docs 批）

- 修改：agate/scripts/ci-gate-backstop.py、agate/state-machine.md、agate/WORKFLOW.md、agate/dispatch-protocol.md、agate/phase-cards/P6-acceptance.md、agate/assets/templates/dispatch-prompt.md、agate/role-system.md、agate/LIMITATIONS.md、agate/AGENTS.md
- 新增：agate/assets/review-roles/judge.md
- 说明：AGENTS.md 登记超出 docs 批 8 处清单但属 P2 §1.1 声明面 + P3 测试 test_bdd_10_agents_role_list_judge_registered 测试驱动（已在进度条目 10 披露）

## 自跑测试（scripts 批）

- ✅ test_check_judge_verdict.py + test_check_events.py（P3 两个新文件）：**41 passed**
- ✅ test_agate_common.py + test_check_gate.py（增补 5+6 用例 + 既有回归）：**182 passed**
- ✅ test_pre_commit_hook.py（integration，真实 hook 全流程）：**55 passed**（修复后）
- ✅ test_ci_gate_backstop.py：passed
- ✅ 邻近回归切片（check_p6_provenance / check_p6_evidence / check_state_yaml / check_state_transition / dispatch_context_warning / sanity）：**143 passed**
- ✅ 5 文件 py_compile 全净（-W error::SyntaxWarning 零警告；docstring 非法转义已修 raw）
- interpreter /usr/bin/python3；basetemp=/home/kity/oclab/agate/.ptmp-scratch（用后清理）；测试未改一字

### 回归修复记录（pre-commit-gate.py）

初次跑 test_pre_commit_hook.py 一例失败：`test_retreat_1_real_hook_each_step`。隔离归因（git stash 基线跑通过 → 我的改动引入）。根因：append_event 在 commit hook 中创建 `gate-events.jsonl`（任务目录内），随 retreat 第二步 `git add -A` 被暂存 → 2p 检查 P4 分支把 `.jsonl` 当作"非 md/yaml 代码文件"误拦 → 要求 P4-dispatch-context → 阻断。
修复：`_NON_MD_YAML_RE` 追加 `gate-events\.jsonl$`（与 `.state.yaml` 同类 = gate 元数据，随任务目录合法落库 audit trail）。修复后 55/55 全绿。无测试断言该正则内容，零测试改动。

## [SCOPE_GAP]

> [SCOPE_GAP: P2-design §1.1 改动表与 §4 脚本层批次声明含 `ci-gate-backstop.py`（provenance 兜底后新增 judge/events 兜底，L234-244 参照），但本次 P4 scripts 批 dispatch-context 目标/执行顺序仅列 5 文件（agate_common / check-judge-verdict / check-events / check-gate gate_p65 / pre-commit-gate 注入），未含 ci-gate-backstop.py；且 P3 测试（test_ci_gate_backstop.py）无 judge 相关用例驱动 → 未实现该文件，交由主 Agent 决定补派或并入后续批次]

## 产出文件清单（本批）

- 修改：agate/scripts/agate_common.py、agate/scripts/check-gate.py、agate/scripts/pre-commit-gate.py
- 新增：agate/scripts/check-judge-verdict.py、agate/scripts/check-events.py
- 本批进度记录：agate-workspace/tasks/TAG0020-independent-judge/P4-progress.md

## CHECK 9 锚点补齐（主 Agent 追加任务）

1. ✅ **check-protocol-consistency.py**（修改）：SCRIPT_ALIGNMENT_ANCHORS 增补 2 条锚点（含 callers 声明）：check-judge-verdict.py（desc「judge verdict 门槛判定（P6.5）」keywords `criteria_total`/`judge`，均与脚本文本实际命中；callers = check-gate/pre-commit-gate/ci-gate-backstop）+ check-events.py（desc「事件账本审计（append-only 哈希链）」keywords `prev_hash`/`GENESIS`，均与脚本文本实际命中；同一 callers）。消除前次记录的 CHECK9-coverage WARNING。
2. ✅ **agate-summary.py**（修改）：`_DRIFT_SCRIPTS` 增补 `check-judge-verdict.py` / `check-events.py`（copy-drift 检测清单——两脚本已是 active gate 链组件，项目本地副本漂移应被检出；无测试断言该清单完备性，纯增量）。

## CHECK 9 补齐后校验

- ✅ py_compile：check-protocol-consistency.py + agate-summary.py 全净
- ✅ test_protocol_alignment_review.py（含 test_sg_6_check9_anchor_table_covers_all_gate_scripts）+ test_check_protocol_consistency.py（锚点表单测）+ test_consistency.py（CON.8 CHECK 9 集成）：**46 passed**
- ✅ consistency 复查（worktree 自身 --strict-errors-only）：**0 ERROR，318 WARNING**（前值 320——2 条 CHECK9-coverage「未纳入锚点表」WARNING 已消除）；grep 确认两脚本不再出现在未覆盖警告中
- 关键词命中核验：check-judge-verdict.py 含 `criteria_total`/`judge`；check-events.py 含 `prev_hash`/`GENESIS`（编写时即与锚点同源，无措辞漂移）

## P4-implementation.md 汇总（主 Agent 追加任务）

- ✅ **P4-implementation.md**（新建，P4 卡产出规格）：Header（phase: P4 / task_id: TAG0020-independent-judge / type: implementation / parent: P2-design.md / trace_id: TAG0020-P4-20260822 / status: draft / created: 2026-08-22 / agent: implementer）+ `implementation_dir: agate/scripts` + 新增文件核对表（3 新增文件，[SKELETON_DEVIATION: 无骨架机制]/[CODE_MAP_EXEMPT: 无 CODE-MAP 机制]——已 glob 实证无 P2-skeleton.md / agents/CODE-MAP.md）+ 三批实现摘要（scripts 5 / docs+backstop 10 / 补丁 2）+ 测试状态总表（262 核心 + 46 check9 + consistency 0 ERROR/318 WARNING）+ SCOPE_GAP 闭环记录 + 17 文件总清单。
## review 评审记录（review subagent 追加）

- 已读：P4-dispatch-context-review.md / review.md / P2-design.md / P1-requirements.md / P0-brief.md；评审对象 15 文件 + 补丁全读（agate_common/check-judge-verdict/check-events/check-gate gate_p65/pre-commit-gate 2i.1/ci-gate-backstop/judge.md/state-machine/WORKFLOW/dispatch-protocol/P6 卡/dispatch-prompt/role-system/LIMITATIONS/AGENTS/check-protocol-consistency CHECK 9/agate-summary _DRIFT_SCRIPTS）
- 实测：test_check_judge_verdict + test_check_events + test_agate_common 58 passed；test_check_gate -k judge 9 passed；consistency 0 ERROR/318 WARNING
- 复现实验 1（CRITICAL）：同一合规 verdict 连续 3 次跑 check-judge-verdict → 账本 judge_verdict 事件 3 条 → check-events "3 条 > 2" exit 1——正常流程（manual check-gate P6.5 + verdict commit + P7 commit）必触壁
- 复现实验 2（INFORMATIONAL）：dispatch-context 输入文件用绝对路径（仓库既有惯例）→ check-judge-verdict 白名单外误报 exit 1

## P4 修复轮（P4-review rejected → implementer fix，CRITICAL-1 + 次要项）

### 输入读取

1. ✅ P4-dispatch-context-implementer-fix.md（强制指令：CRITICAL-1 内容寻址去重必改 + 次要 ①②建议处理 + ③④⑤记录取舍 + 只改 check-judge-verdict/check-events/agate_common + 测试 + 每文件追加进度）
2. ✅ P4-review.md（评审全文：CRITICAL-1 复现实验（3 次 gate 执行 → check-events 3 条 >2 阻断 P7 commit）+ I-1 白名单绝对路径误报（非对称：黑名单子串不受影响）/ I-2 首个括号 token 误取 / I-3 budget_exhausted 粘性 / I-4 同 BDD 重复行 / I-5 append 非原子 + fail-open）

### 实现记录（修复轮）

1. ✅ **check-judge-verdict.py**（修改，3 处）：① `_is_whitelisted` + `_check_whitelist_outside` 改为 basename/相对路径归一（I-1——绝对路径引用白名单文件不再误报，`p6-evidence/` 前缀保留在完整 token 上匹配）② 结论引用提取收敛到"括号内容整体为文件路径形态"（`_REF_PATH_FULL_RE` fullmatch，可逗号分隔多文件；描述中任意括号如 "(as discussed)" 不再误取为首个引用，I-2）③ step 9 记账事件增 `verdict_hash` 字段 = verdict 全文 sha256（`_verdict_hash` helper，内容寻址，CRITICAL-1 写侧）。

2. ✅ **check-events.py**（修改）：judge 轮次计数 = `verdict_hash` 去重（`judge_verdict_hashes` set）+ 无 hash 旧事件各计 1（`judge_verdict_legacy`，向后兼容既有无 hash 用例）；`MAX_JUDGE_VERDICT_EVENTS=2` 语义保持（真实复核 = 新 hash 才 +1；同一 verdict 多次 gate 重跑不增轮，CRITICAL-1 计侧）；docstring 审计链第 6 项同步更新。
3. ✅ **agate_common.py**（不改，决策记录）：`append_event` 保持通用（`row = dict(event)` 透传 verdict_hash），verdict_hash 计算归属 check-judge-verdict（它拥有 verdict 文件内容）——评审方案 A 的等价实现（内容寻址去重落在写侧事件字段 + 计侧去重），不把账本函数变成 verdict 感知。
4. ✅ **测试增补（5 用例，评审 CRITICAL-1 Fix 强制"补生命周期用例"）**：
   - test_check_events.py +2：`test_bdd_8_judge_verdict_same_hash_dedupe_exit_0`（3 事件 2 个不同 hash → 去重轮次=2 → exit 0）/ `test_bdd_8_judge_verdict_three_distinct_hashes_exit_1`（3 个不同 hash = 3 次真实复核 → exit 1）
   - test_check_judge_verdict.py +3：`test_bdd_8_rerun_same_verdict_round_not_increment`（同一 verdict 连跑 2 次 judge → 账本 2 事件同 hash、等于 sha256(verdict 文件内容)，check-events 去重轮次=1 → exit 0，生命周期路径）/ `test_bdd_4_whitelist_abs_path_not_flagged_exit_0`（I-1 绝对路径白名单不误报）/ `test_bdd_6_desc_parens_not_misparsed_exit_0`（I-2 描述括号不误取引用）

## 修复轮验证

- ✅ py_compile：check-judge-verdict.py + check-events.py 全净
- ✅ test_check_judge_verdict.py + test_check_events.py（29+12 既有 + 5 新回归）：**46 passed**
- ✅ 回归套件：test_check_gate + test_agate_common + test_pre_commit_hook（integration）：**237 passed**（gate_p65/账本/真实 hook 无 collateral）
- ✅ **评审复现实验转绿**：合规 fixture 连跑 3 次 check-judge-verdict（等价 manual check-gate P6.5 + verdict commit + P7 commit）→ 账本 3 条 judge_verdict（同 verdict_hash）→ check-events「judge 轮次×1」exit 0——CRITICAL-1 自锁消除（修复前该实验 exit 1）
- ✅ count-tests.sh：1168 用例 ≥ 749 下限，无漂移；consistency 复查 0 ERROR / 318 WARNING（CHECK 9 锚点关键词 criteria_total/judge/prev_hash/GENESIS 均仍在脚本中命中）

## 次要项处理（③④⑤ 记录设计取舍，未改代码）

- **I-3 budget_exhausted 粘性**（记录，未改）：step 8 扫全账本任一 `reason == budget_exhausted` 即强制本轮 needs-revision+partial——与 P2-design §3.3 步 8 原文一致（实现忠实于设计）；一轮超限后后续轮次无法 passed 属 P2 语义副作用，如需改为"轮次区分配对"（事件带 round/最近一轮比对）属 P2 变更，不在本修复轮范围，交主 Agent 决定。
- **I-4 同 BDD 重复结论行**（记录，未改）：concl_ids 去重后编号集相等 + 条目数==criteria_total 仍成立——BDD-3 最小合规（每条 ≥1 独立结论）满足，冗余行不拦截为可选增强（按编号分组断"每组恰 1 行"），交主 Agent 决定。
- **I-5 append_event 非原子写 + fail-open**（记录，未改）：P2 R7 已声明的缓解（单任务单进程顺序写入，pre-commit 钩子串行）+ P2 明确"账本=辅助防线"取舍；CRITICAL-1 修复后"清空/写失败账本"逃生门动机消失（正常流程不再触壁），fail-open 属性保持 P2 语义不变。

## review 复审记录（review subagent 追加）

- CRITICAL-1 独立复核：写侧 verdict_hash（check-judge-verdict.py L423-431）+ 计侧 hash 去重（check-events.py L104-112）确认；复现实验转绿——同 verdict 连跑 3 次 → judge 轮次×1 exit 0；3 异 hash → exit 1；2 异 hash 边界 → exit 0
- 次要项：I-1 绝对路径白名单 exit 0 + 绝对路径黑名单仍 exit 1（无放水）；I-2 括号描述不误取（exit 0）；I-3/4/5 取舍记录合理
- 测试：63（judge/events/common）+ 165（check_gate 全量）+ 55（pre_commit_hook integration）；consistency 0 ERROR/318 WARNING；count-tests 1168 无漂移
- 复评结论：approved（无 CRITICAL/BLOCKER；3 条 INFORMATIONAL 残留 R-1/R-2/R-3 见 P4-review.md PASS 2）
