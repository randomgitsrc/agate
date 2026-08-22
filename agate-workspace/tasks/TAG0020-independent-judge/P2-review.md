---
phase: P2
task_id: TAG0020-independent-judge
type: review
parent: P2-design.md
trace_id: TAG0020-P2-20260822
status: approved
created: 2026-08-22
agent: plan-eng-review
---

# P2 方案评审 — plan-eng-review（独立 Judge 机制 TAG0020）

> 评审对象：`P2-design.md`（architect 产出，候选 1 + 3a 选定方案）。评审方式：对 P2-design 引用的全部脚本/协议锚点做了独立 grep/read 核实（check-gate.py / pre-commit-gate.py / check-p6-provenance.py / check-p6-evidence.py / agate-state-yaml-check.py / agate_common.py / ci-gate-backstop.py / check-protocol-consistency.py / check-tdd-red.py / state-transitions.md / qa.md），逐条对照行号引用。状态标记：`[PROD_NOT_TOUCHED]`。

## 结论摘要

**status: approved**（0 阻塞级问题；4 项非阻塞观察 + 6 项测试缺口建议——均不阻断 P2→P3 推进，供 P3/P4 消化）。

评审总判断：P2-design 在六个 TAG0020 特性专审维度全部**闭环且机械可判定**（BDD-9 哲学红线 / BDD-4 信息隔离 / 账本×provenance 交集 / BDD-2 历史兼容 / BDD-8 三档预算 / BDD-3/10 挂靠零新架构）；引用的代码锚点经逐条核实**无位置性错误**（仅 2 处行号 ±2 偏移：agate-state-yaml-check retries regex 实际 L52 非 L49-50、_RETRY_TABLE_ROW_RE 实际 L925 非 L924，结论均成立）；多方案探索充分（3 候选 + 权衡 + 选择理由）；实现就绪度合格（files_to_read 13 项覆盖脚本/协议/测试三面）；minimal_validation 声明"纯代码逻辑 + 静态 grep 实证"与独立核实一致（`_P_OUTPUT_RE` L78、step3 正则 L487、`_NON_MD_YAML_RE` L77、valid_phases L17、协作规范 glob L504 均不匹配 P6.5-*，结论成立）。

---

## 架构问题（阻塞级）

无。以下设计决策与实现路径经独立核实均成立：

1. **候选 1 + 3a 正交组合成立**（§2 权衡 / §3 选定方案）：① P6.5 作为「P6→P7 转移上的强门槛子阶段」不新增 phase 值——`agate-state-yaml-check.py` valid_phases L17 无 P6.5（误写 phase: P6.5 天然 fail-closed）、`agate_common.MAX_RETRY_MAP` L43 无 P6.5（CHECK 12 零漂移）、`check-protocol-consistency.py` `_RETRY_TABLE_ROW_RE` L925 不匹配 P6.5（不新增表行 → 零漂移）；② 事件写入收敛 `append_event` 自动写（pre-commit-gate 写 gate_run/state_transition、check-judge-verdict 写 judge_verdict）——信任模型正确（防改写机制不依赖被防对象自觉），与 BDD-9"机械核对是门槛"精神一致；③ 轮次预算用 `judge.rounds` + 账本事件计数 ≤2 而非 `retries.P6.5`，规避 `agate-state-yaml-check.py` L52 `^P\d+$` retries key 校验（独立核实该 regex 存在，`retries.P6.5` 确会被拦）——规避策略成立。

2. **哲学红线（BDD-9）落地**（§3.3 校验链 / §3.5 gate_p65）：check-gate.py `handlers` dict（L1082-1092）增 `"P6.5": gate_p65` 即可独立跑（main() L1067 phase=sys.argv[1]，显式参数不被 .state.yaml 干扰）；gate_p65 依次调 check-judge-verdict + check-events，任一 exit 1 → P6→P7 阻断；check-judge-verdict step 5 明确"LLM 结论不单独构成放行依据"。commit-time 由 pre-commit 注入（2i L334 并列）承载——上一阶段 P2-design §3.5 的注入条件 `judge.enabled && verdict 存在` 与 phase 值解耦，P6→P7 硬边界不依赖主 Agent 自觉。

3. **信息隔离白名单（BDD-4）**（§3.3 step 7）：复用 check-p6-provenance 审计 2 的 AGATE_CARD + frontmatter 双排除（L318-355，含 L340-351 frontmatter 剥离循环与 L352 `^\s*- (PASS|FAIL)\b` 预判）——独立核实该审计存在且语义一致；黑名单/白名单路径引用扫描限『输入文件』『上游关联』两节 + 行首预判全文扫描，与 BDD-4 字面约束（"两节做路径引用扫描 + 全文做行首预判扫描"）一致。P1 §4.2 白名单权威定义（黑名单 7 项、白名单 6 项 + git log）原样落入 §3.3 step 7，无漂移。

4. **事件账本 × provenance 交集**（§3.2 字段交集 / R1）：`ts/event/phase/cmd/exit/runner` 与审计 5 EXIT_CODE 尾行约定（check-p6-provenance L471-488）"同源不同层"；`state_transition` 与 .state.yaml 双写（.state.yaml 权威）；哈希链 + 时间戳单调为账本独有能力（审计 1-7 无此机制，无冲突）。回归测试保审计 1-7 行为不变（BDD-10）——既有单元回归（test_check_p6_provenance / test_check_p6_evidence / test_check_gate）不改作为锚点，正确。

5. **历史兼容（BDD-2）**（§3.5 / §3.6）：双守卫 = gate_p65 早退（`judge.enabled` falsy → exit 0）+ pre-commit 注入条件（marker && verdict 存在）——历史任务无 judge 字段 → 全链跳过；AGENTS.md 测试约定下 `.state.yaml` 未知顶层键 `judge:` 不拦截（agate-state-yaml-check L34-55 只校验 task_id/phase/status/retries，独立核实成立）。

6. **三档预算（BDD-8）**（§3.3 step 5/8 + §3.4 step 7）：轮次 ≤2 机械兜底 = 账本 `judge_verdict` 事件计数 ≤2（check-events step 7）+ `partial:true ⇒ status≠passed`（check-judge-verdict step 5）+ 账本 budget_exhausted ⇒ needs-revision+partial（step 8）——"超限不静默放行"机械可判定。token/时间预算经 judge.md 声明 + dispatch-prompt 注入（judge 侧自控 + 诚实降级声明），P5 dogfood 校准，符合 BDD-8 字面语义。

7. **挂靠零新架构（BDD-3/10）**（§3.7）：status 三值映射复用 role-system.md L108-116（passed→approved / needs-revision→needs-revision / rejected→rejected）；dispatch-prompt 模板方法 B + 专家组/double-judge 仅文档级（不新增机器校验）；judge 不进 C8 表（"强制所有任务"与 domain/risk 触发语义不同，P1 §4.1 判定正确）；judge.md frontmatter `phases: [P6.5]` 为自由 token（qa.md frontmatter `phases: [P5]` 同模式，独立核实）——零新架构成立。

---

## 架构问题（非阻塞）

1. **token/时间预算无客观测量，仅 judge 自报 + 格式校验**（§3.3 step 8）：机械核对只能校验"已声明 `budget_exhausted` 的 verdict 是否符合 `needs-revision + partial:true` 降级格式"，无法测量 judge 实际 token 消耗/墙钟时间是否超限（LLM 侧自控）。轮次有账本计数机械兜底，token/时间没有。**建议**：judge.md + dispatch-prompt 追加节强制 judge 在 verdict 中自报预算达成情况（如 `budget_used: token|time|rounds` 字段），供 P5 dogfood 校准阈值（P0 known_risks"预算阈值合理性需 dogfood 校准"已点名）——不阻塞，设计符合 BDD-8 字面（诚实降级语义）。

2. **`append_event` IOError 仅告警的审计降级面**（§3.2 L169）：judge_verdict 事件写入失败时账本无该事件 → check-events 轮次计数 ≤2 机械兜底失效（该轮次绕过记账）。设计理由（"gate 主判定不依赖写账本成功，账本审计是辅助防线"）可接受，但应在 judge.md 或 dispatch-protocol 明示"账本审计降级 ≠ 校验降级"，并依赖 `.state.yaml judge.rounds`（主 Agent 维护）作为轮次计数兜底的第二源。**建议**：P3 测试覆盖"账本缺失 judge_verdict 事件但 judge.rounds=3"的判定语义（明确主 Agent rounds 不构成机械放行依据）。

3. **信息隔离路径引用扫描限两节，注入面若扩散则盲区**（§3.3 step 7）：BDD-4 字面限定『输入文件』『上游关联』两节扫描——若未来 dispatch-context 模板新增其他含路径引用的节（如 objective_info 环境状态节），黑名单漏扫。当前设计符合 P1 固化约束（路径引用扫描两节 + 全文行首预判），第一道防线仍是主 Agent 派发约定（dispatch-protocol 信息隔离节声明）。**建议**：dispatch-protocol 新增节时注明"含路径引用的节须纳入白名单扫描语义"。

4. **files_to_read 未列 `agate/rules/review-mapping.md`**（§5 L38-42 为评审产出统一 status 字段表，P1 §4.1 已引用）：judge verdict Header `status` 遵守该表，P4 implementer 需知晓。role-system.md L108-116 已覆盖三值映射，review-mapping 主要补充"评审产出统一 status 字段"规范。**建议**：P4 实现 judge.md 产出格式时补读该文件；可在 P3 测试设计时对照（不阻塞，files_to_read 13 项整体覆盖充分）。

---

## 测试缺口

1. **BDD-10 双位编号边界**：P1 BDD 计数口径 `^#### BDD-[0-9]` 与 verdict 结论 `- (PASS|FAIL|NEEDS-REVISION) BDD-NN:` 的编号提取——本任务 P1 有 BDD-1..BDD-10，须确认双位编号（BDD-10）在计数与编号集相等校验中不丢失（`BDD-([0-9]+)` 分组提取，非 `[0-9]` 单字符）。§3.8 测试要点未列该边界用例。
2. **verdict commit 与 pre-commit 2p/2n.2 互动的回归**：`P6.5-judge-verdict.md` / `P6.5-dispatch-context-judge.md` 在 phase=P6 commit 暂存时——2p 强制 dispatch-context（glob `P6-dispatch-context-*.md` 不匹配 P6.5-*，L353）、2n.2 非证据拦截（`_NON_MD_YAML_RE` L77 排除 .md）、step3 产出-阶段 WARNING（L487 `P[0-8]-` 不匹配 P6.5-*）三条路径都应"零误拦零假警告"；minimal_validation 已静态论证，缺自动化回归固化。
3. **账本尾部删除语义**：check-events "仅允许行尾追加"对**删除尾部行**无法哈希检测（§3.4 step 6 自承认），靠 ts 单调 + judge_verdict 事件计数部分兜底——测试须覆盖"删掉最后一条 judge_verdict 事件后剩余链完整但计数变化"的判定语义（明确该场景的期望 exit code 与审计局限声明）。
4. **append_event 单测边界**：GENESIS_HASH（sha256(b"")）正确性、首行写、ts 单调兜底（`max(now, 尾行 ts)` 微秒递增）、IOError 降级（WARNING 不抛）、并发同秒写——§3.8 只列了 check-events 侧链审计用例与"GENESIS_HASH 常量正确性"，append_event 的写入侧单测（尤其 ts 兜底并发语义，R7）宜补管。
5. **信息隔离归一化/大小写绕过用例**：R3 声称"黑名单串用大小写不敏感正则 + 归一化匹配"防路径改写绕过（相对路径/大小写）——§3.8 BDD-4 组只列了黑名单命中/白名单外路径/行首预判/AGATE_CARD 排除四类，缺"相对路径改写（`./P6-acceptance.md` / `evidences/` 前缀剥离, 仿审计 1 L283 的 `^(P6-evidence|p6-evidence|evidences)/`）与大小写变体"的定向用例。
6. **read_judge_verdict 返回 None 的交互**：`.state.yaml judge.enabled: true` 但 verdict 缺失/解析失败（frontmatter 坏 YAML）→ gate_p65 缺 verdict exit 1 + pre-commit 注入条件不成立——两条路径的 exit code 与 stderr 语义应有测试固化（§3.8 test_check_gate 增补覆盖了 skip/缺 verdict/通过三态，可补"verdict 存在但 frontmatter 解析失败"态）。

---

## 锁定决策

1. **P6.5 挂载方式**：候选 1——P6.5 是「P6→P7 转移上的强门槛子阶段」，非 `.state.yaml` phase 值（phase 保持 P6 至 P7）；`check-gate.py` 增 `"P6.5": gate_p65` 分支（显式参数调用），pre-commit 注入兜底 commit-time 强制；`.state.yaml` 不加 P6.5、`retries` 不使用 P6.5 key。
2. **事件写入主体**：候选 3a——`append_event()` 单点收敛，门禁脚本自动写（pre-commit-gate 写 gate_run + state_transition；check-judge-verdict 校验通过后写 judge_verdict），主 Agent 不手工记账。
3. **事件账本 schema**：`gate-events.jsonl` 任务级路径 + 行间哈希链（`prev_hash` = sha256(上一行原始行)，首行 = GENESIS_HASH）+ ts UTC ISO8601 微秒单调（append 侧 `max(now, 尾行)` 兜底）；`.state.yaml` 权威状态源、`state_transition` 事件只记录不改写；与审计 5 "同源不同层"、与审计 7 双写不冲突。
4. **机械核对职责边界**：check-judge-verdict（verdict 字段/BDD 对照/证据交叉/信息隔离/预算交叉）+ check-events（账本完整性/轮次计数）exit code 即 P6.5 门槛；judge 的 LLM 结论只作行为描述输入，不单独放行（BDD-9）；verdict 正文行格式细节由 judge.md 产出规范约束、脚本不做语义判定。
5. **历史兼容与回归锚点**：`judge.enabled` marker 缺失 → 全链跳过（gate_p65 早退 + pre-commit 注入条件双守卫）；既有 P6 审计 1-7 / check-p6-evidence / check-gate P0-P8 全部不改，作为 BDD-10 回归锚点；`check-protocol-consistency.py --strict-errors-only` 0 ERROR + count-tests 不漂移为质量门槛。