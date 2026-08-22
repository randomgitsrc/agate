# P2 设计进度（TAG0020-independent-judge）— agent: architect

> 分阶段落盘记录。Header 规格见 dispatch-context；最终产出 P2-design.md。

## 2026-08-22 进度

### 步骤 1-2：dispatch-context + 角色定义已读
- dispatch-context（P2-dispatch-context-architect.md）：强制指令，目标 = 产出 P2-design.md 覆盖 M1-M2 文件级改动清单（judge.md / check-judge-verdict.py / check-events.py / agate_common append_event+read_judge_verdict / check-gate P6.5 分支 / 5 个协议文档 / 测试）。约束：agate 哲学红线（BDD-9）、历史兼容（BDD-2）、机械可判定（BDD-1/4/5/6/7）、三层防造假、三档预算（BDD-8）、挂靠现有机制、事件账本与 provenance 共存（P0 风险 2）。
- 角色文件 architect.md（稳定版）：影响域分析三部分（改什么/不改什么/风险在哪）、候选方案 ≥2 + 权衡 + 选择理由、四字段 frontmatter、files_to_read / env_constraints / minimal_validation、批次设计（dispatch_plan）、[SCOPE+] 标注、README 反例（先读代码再设计）。

### 步骤 3：P1-requirements + P0-brief 已读
- P1 10 条 BDD（BDD-1~10）approved，权威基线。关键固定项：
  - BDD-4 黑名单路径引用集已固化：P6-acceptance.md / P6·P5·P4-dispatch-context-*.md / P4-implementation.md / P4-review.md / P5-test-results/ 禁入 judge dispatch-context；白名单 = P1-requirements.md / P2-design.md / P6-evidence/ / .state.yaml / gate-events.jsonl / P6.5-judge-verdict.md + git log 查询权。
  - BDD-3：criteria_total == P1 BDD 标题数（`#### BDD-NN:`），含已 PASS 项全验。
  - BDD-5：Header status（passed/rejected/needs-revision）+ criteria_total + criteria_passed + verdict_evidence；passed 时须全等。
  - BDD-7：gate-events.jsonl append-only + prev_hash 哈希链 + 时间戳单调；空/仅起始行合法。
  - BDD-8：轮次≤2 / token 100k（judge_token_budget 覆盖）/ 时间 30min；超限 partial:true → needs-revision；账本记 reason: budget_exhausted。
  - BDD-10：consistency 0 ERROR + pytest 全绿 + count-tests 不漂移。
  - P1 §3 隐含需求：valid_phases / _DEFAULT_MAX_RETRY_MAP / _PHASE_OUTPUTS / 卡片枚举同步；P1 §3 有 [SUGGEST: P6.5 挂载优先采用"P6 门槛内嵌强制判定 + retries.P6.5 独立计数"（不把 P6.5 写入 .state.yaml phase 值）]——P2 设计决策点。
  - P1 §4.2 白名单反推：agate-extract-context.py 注入在 P6.5 禁用或净化；审计 2 的 AGATE_CARD 排除逻辑复用。
  - P1 §4.3 交集分析：审计 3 BDD 计数口径复用；审计 1 证据引用逻辑复用；审计 5 与账本同源不同层；审计 7 与 state_transition 事件双写（.state.yaml 仍权威）。
- P0-brief：known_risks（改动面 12+ 文件全触发 SELF-GATE、账本与 provenance 交集、预算需 dogfood 校准、历史任务兼容）+ env_constraints（/tmp 只读 --basetemp、test_cmd）。

### 步骤 3 续：design-independent-judge.md 设计提案已读
- §3 角色设计（judge.md 字段表：输入只传路径、禁止输入 P6-acceptance.md + implementer/verifier dispatch-context、产出 P6.5-judge-verdict.md）。
- §4 三层防造假（信息隔离/证据交叉核对/append-only 账本）；§5 三档预算（轮次≤2 超限→rejected 交人工、token 100k partial、时间 30min）；§6 状态机（.state.yaml 新增 judge: 字段 + retries.P6.5；P6→P6.5→P7、P6.5(needs-revision)→P6 弹回）。
- §7 文件改动清单（12 项：judge.md / check-judge-verdict.py / check-events.py / agate_common.py / check-gate.py / WORKFLOW.md / state-machine.md / dispatch-protocol.md / phase-cards/P6 / dispatch-prompt.md / SELF-GATE.md 自动触发 / tests）。
- §8 对标取舍（oh-my-agent）；§9 落地节奏。

### 待读输入
- review-roles/ 现状（judge 挂靠参考）
- check-gate.py（P6.5 分支挂载点）
- check-p6-provenance.py / check-p6-evidence.py（六道审计参考——事件账本交集）
- state-machine.md / dispatch-protocol.md / phase-cards/P6-acceptance.md（P6.5 挂载点）

### 代码实证（grep/read 命中，作为影响面客观证据）
- **review-roles 现状**：10 个角色文件；frontmatter 统一模式（role_id/type: review/phases 自由值/agent）。`phases:` 是自由 token（P4-after/pre-commit/any/P1/P2/P5）→ judge.md `phases: [P6.5]` **无需枚举变更**。
- **check-gate.py**：main() `handlers` dict = P0-P8（L1082-1092）→ 加 `"P6.5": gate_p65` 即可独立跑；gate_p6（L791-840）return 2=通过；rollback 检测 `phase_num` 数字提取（L1073-1075，"P6.5"→6，不影响 P0-P8 常规）。
- **pre-commit-gate.py**：2h.1 gate（L324-331）+ write_gate_result（L331，gate_run 事件写入点）+ 2i provenance 注入（L334，P6.5 注入并列参照）+ 2n evidence（L410）+ 2n.2 非证据拦截（L439-454：**P6.5-*.md 是 .md → _NON_MD_YAML_RE L77 排除 → verdict commit 在 phase=P6 不被拦**）+ 2p dispatch-context hash（L350-398：glob `phase+"-dispatch-context-*.md"` → **不匹配 P6.5-* → 卡片 hash 不强制**）；`_P_OUTPUT_RE = P[0-8]-.*\.md$`（L78）与 step3 正则（L487 `^(.*)/P[0-8]-[^/]+\.md$`）**均不匹配 P6.5-judge-verdict.md → 无"产出与 phase 不一致"假警告**。
- **agate-state-yaml-check.py**：valid_phases L17（P0-P8/PAUSED/READY/DONE，无 P6.5）；**retries key 正则 `^P\d+$`（L49-50）→ retries.P6.5 会被拦**（两模型都需注意：Model A 改用 judge.rounds 规避）；未知顶层键（judge:）**不校验**（只查 task_id/phase/status/retries L29-53）→ .state.yaml 增 judge: 块安全。
- **check-state-transition.py**：MAX_RETRY_MAP 从 agate_common 导入（L25-34）；phase_num（L93-96）；diff 检查 L137-175。
- **agate_common.py**：MAX_RETRY_MAP L43（"P1:3,...P8:2"，无 P6.5）；write_gate_result L244；append_event/read_judge_verdict 为新增点。
- **check-p6-provenance.py**：审计 2（L318-355：AGATE_CARD + frontmatter 双排除 + `^\s*- (PASS|FAIL)\b` 预判扫描——**BDD-4 白名单扫描直接先例**）；审计 3（L357-399：`^#### BDD-[0-9]` 计 P1 BDD 数 L371 + frontmatter pass/fail 优先——**criteria_total 对照口径**）；审计 1 证据引用存在性/对称（L263-316）；协作规范 glob `P[0-8]-*.md`（L504，不匹配 P6.5-* → verdict agent 字段检查跳过，不改）；_SKIP_AGENT_CHECK L53-59。
- **check-p6-evidence.py**：_md5_entries（L96-106）+ md5 去重阻断（L314-327）→ **BDD-6 证据去重复用思路**。
- **ci-gate-backstop.py**：run_gate L23 + provenance 兜底（L234-244）→ judge/events 兜底扩展点（P1 §3 多端隐含需求）。
- **state-machine.md**：状态集合 L72（P0-P8 无 P6.5）；P6→P7 规则 L134；P6--FAIL-->P4 L143；P6 不可裁 L193。
- **dispatch-protocol.md**：L314 所有阶段强制 dispatch-context；L335 上游关联节；L358 AGATE_CARD 注入；L379-380 禁 PASS/FAIL 预判 + 派发后冻结；L745 P6→P7 gate 表。
- **role-system.md**：评审名册表 L37-51；status 三值映射 L108-116（passed→approved/needs-revision→needs-revision/rejected→rejected 复用）；C8 机械映射 L52-66（judge 强制所有任务 → 不进 C8）。
- **WORKFLOW.md 阶段总览表 L288-296**（`| P0 | 任务简报 | ... | 门槛 |` 形态）→ P6.5 行落点；L63-68 角色树登记 judge。
- **check-protocol-consistency.py**：CHECK 2（引用路径存在性，PROTOCOL_DIRS = agate/assets+phase-cards+rules，**tasks/ 产出不在扫描面 → P2/P3 引用新文件不触发假阳性**）；CHECK 12 `_RETRY_TABLE_ROW_RE = |\s*(P\d+)\s*|\s*(\d+)\s*|`（**P6.5 不匹配 → Model A 不加 `| P6.5 | N |` 表行 + 不动 MAX_RETRY_MAP → 零漂移**）。
- **测试现状**：unit/ 下 test_check_p6_provenance.py（test_pv_N 命名 + task_dir/agate_scripts/python_exe/run_cli fixtures）→ 新 test_check_judge_verdict.py / test_check_events.py 同模式。

### 关键设计决策点（已定，写入 P2-design.md）
1. **挂载方式**：候选 A（P6.5 = P6→P7 转移上的强门槛子阶段，不新增 phase 值，采纳 P1 SUGGEST）vs 候选 B（真实 phase 值，枚举全面扩展）→ 推荐 A（B 的连锁风险 = P1 §3 四项枚举同步压力 + retries regex/MAX_RETRY/CHECK 12 额外改动面）。
2. **事件写入主体**：候选 C1（append_event 单点，门禁脚本自动写：pre-commit-gate 写 gate_run/state_transition，check-judge-verdict 写 judge_verdict）vs C2（主 Agent 手工）→ 推荐 C1。
3. **轮次预算机械兜底**：账本 judge_verdict 事件计数 ≤2（check-events）+ verdict partial:true ⇒ status≠passed（check-judge-verdict），不依赖 retries.P6.5（规避 state-yaml retries regex）。
4. **enforcement**：check-gate.py gate_p65 独立分支（推进判定）+ pre-commit-gate 注入（judge.enabled && verdict 存在 → 两脚本）→ commit-time 硬边界；gate_p6 不改（P6 行为不回归）。

### 产出自检清单（写 P2-design.md 时逐项核）
- [ ] Header：phase/task_id/type/parent/trace_id/status: draft/created/agent
- [ ] frontmatter 机器字段：candidate_count / packages / domains / ui_affected
- [ ] 影响面梳理三部分（写在候选方案前）+ 客观证据
- [ ] 候选方案 ≥2 + 权衡 + 选择理由 + candidate_count 一致
- [ ] gate_commands / files_to_read / env_constraints / minimal_validation
- [ ] 实现完成的标志（供 P3/P5）
### 产出完成（2026-08-22）
- P2-design.md 已产出（358 行）：Header + frontmatter（candidate_count: 3 / packages: [agate] / domains: [backend] / ui_affected: false / dispatch_plan: serial）+ 影响面梳理（改什么 15 文件映射 BDD / 不改什么 10 项 / 风险 11 条配缓解，均附客观证据）+ 候选方案 3 个（P6.5 强门槛子阶段 vs 真实 phase / append 收敛自动写 vs 主 Agent 手工）+ 选定方案细化（事件 schema / 两脚本校验链 / gate_p65 + pre-commit 注入 / .state.yaml judge 块 / status 映射 / 测试要点）+ 批次设计 + 四字段 + files_to_read(13 项) + env_constraints + minimal_validation（纯代码逻辑声明 + 静态验证 confirmed）+ 实现完成标志。
- 自检：frontmatter YAML 解析通过，必填字段齐全；candidate_count=3 与正文 3 个候选一致；影响面梳理在候选方案之前；status: draft。
- [PROD_NOT_TOUCHED]：全程未改协议本体/生产文件，只写任务目录产出。


## plan-eng-review 评审进度（2026-08-22）

### 步骤 1-2：dispatch-context + 角色定义已读
- dispatch-context（P2-dispatch-context-plan-eng-review.md）：强制指令 = 评审 6 项 TAG0020 特性专审 + plan-eng-review 通用要点；产出 P2-review.md（status: approved/rejected，与 Header 一致）
- 角色定义 plan-eng-review.md：数据流/状态机/接口契约/错误边界/测试策略/技术债(DEBT 格式)/多方案探索/实现就绪度/P2 最小验证

### 步骤 3：输入文件逐一读取
- P0-brief.md：env_constraints（/tmp 只读、test_cmd）、known_risks（账本×provenance 交集、历史兼容、预算校准）、同类扫描强制项
- P1-requirements.md：10 BDD approved 基线；BDD-4 黑名单/白名单权威定义（P1 固化）；[SUGGEST: P6.5 不写 phase 值]；P1 §4.3 交集分析（同源不同层/双写）
- P2-design.md（评审对象，359 行）：candidate_count: 3 + 影响面梳理(改 15 / 不改 10 / 风险 11) + 候选 1(P6.5 强门槛子阶段)/候选 2(真实 phase)/候选 3a(append 收敛自动写) + 事件 schema + 双脚本校验链 + gate_p65/pre-commit 注入 + .state.yaml judge 块 + minimal_validation(纯代码逻辑 + 静态 grep 实证 5 项)
- design-independent-judge.md：§4 三层防造假 / §5 三档预算 / §6 状态机（.state.yaml judge 字段 + retries.P6.5——P2 已改为不用 retries.P6.5 规避 regex）/ §7 文件改动清单（12 项）
- check-p6-provenance.py（审计交集核验）：审计 1（L263-316 证据引用对称）✓、审计 2（L318-355 AGATE_CARD+frontmatter 双排除 + L352 `^\s*- (PASS|FAIL)\b` 预判）✓、审计 3（L357-399，L371 `^#### BDD-[0-9]` 计 P1 BDD 数）✓、审计 5（L471-488 EXIT_CODE 尾行）✓、L504 协作规范 glob `P[0-8]-*.md` 不匹配 P6.5-* ✓

### 步骤 3 续：锚点独立核实（grep/read 对照 P2-design 行号引用）
- check-gate.py：gate_p6（L791-840，return 2=通过）✓；handlers dict（L1082-1092 P0-P8）✓ 加 "P6.5" 可行；main() phase=sys.argv[1]（L1067）显式参数优先 ✓
- pre-commit-gate.py：write_gate_result（L331）✓ 2i provenance 注入（L334）✓ 2p glob `phase+"-dispatch-context-*.md"`（L353，P6 时不匹配 P6.5-*）✓ _NON_MD_YAML_RE（L77）✓ _P_OUTPUT_RE（L78 P[0-8]）✓ 2n.2 非证据拦截（L439-454）✓ step3 正则（L487）✓
- agate-state-yaml-check.py：valid_phases L17 无 P6.5 ✓；retries key 正则 L52 `^P\d+$`（P2 引 L49-50 偏移 ±2，结论成立）✓；未知顶层键 judge: 不校验（L29-53）✓
- agate_common.py：MAX_RETRY_MAP L43（P1:3..P8:2，无 P6.5）✓
- check-protocol-consistency.py：PROTOCOL_DIRS L68（assets+phase-cards+rules，tasks/ 不在面）✓；_RETRY_TABLE_ROW_RE L925 `\|\s*(P\d+)\s*\|` 不匹配 P6.5（P2 引 L924 偏移 1）✓
- ci-gate-backstop.py：provenance 兜底（L234-244）✓ 扩展点成立
- check-p6-evidence.py：_md5_entries（L96-106）✓ + md5 去重阻断（L314-327）✓
- check-tdd-red.py：P3 gate_commands 消费链（TEST_RUNNER→P3*→pytest）✓；judge_result 对非 0/1/124 exit 落入 red-light/unexpected ✓
- state-transitions.md：P3→P4 条件（check-tdd-red exit 0 + assertion_failures>0）✓；回退归档机制（agate-archive-stale-outputs）确认 P6.5 不新增 phase 值 → 无独立归档诉求 ✓
- qa.md frontmatter（role_id/type/phases/agent 模式）✓ judge.md 沿用成立

### 步骤 4：评审判定（详见 P2-review.md）
- 六项特性专审：BDD-9 哲学红线 ✓（gate_p65 双脚本 exit code 即门槛 + pre-commit 注入 + check-judge-verdict 明示"LLM 结论不单独放行"）；BDD-4 信息隔离 ✓（两节黑名单串扫描 + 白名单外路径 + 行首预判，机械可校验）；账本×provenance 交集 ✓（同源不同层设计 + 回归测试保审计 1-7 不变）；BDD-2 历史兼容 ✓（gate_p65 早退 + 注入双守卫 + 专项回归）；BDD-8 三档预算 ✓（轮次机械兜底 = 账本事件计数 ≤2 + partial 交叉校验；token/时间靠 partial 诚实声明 + dogfood 校准）；BDD-3/10 挂靠零新架构 ✓（status 三值复用 L108-116、C8 不进、专家组/double-judge 文档级）
- 结论：status: approved（无阻塞级问题；4 项非阻塞观察 + 3 项测试缺口建议，详见 P2-review.md）
- [PROD_NOT_TOUCHED]：全程只读协议本体 + 写任务目录产出，未改任何生产文件

### 评审完成（2026-08-22）
- P2-review.md 已产出（73 行）：结论 status: approved（0 阻塞级）+ 非阻塞 4 项 + 测试缺口 6 项 + 锁定决策 5 项，全部引用具体锚点（小节/文件行号）
- 自检：Header 完整（phase: P2 / task_id / type: review / parent: P2-design.md / trace_id / status: approved / created / agent: plan-eng-review）；文件非空；status 字段与返回 Status 一致
- [PROD_NOT_TOUCHED]：全程未改协议本体/生产文件，仅写任务目录产出
