# P1-progress — TAG0020 独立 Judge 机制（RM-AG0032）

> 分阶段落盘记录（analyst，2026-08-22）。started_by: analyst / agent: analyst / phase: P1

## 步骤日志

- [x] 读取 dispatch-context（P1-dispatch-context-analyst.md）——派发指引 + P1 卡片全文注入已读
- [x] 读取角色定义 analyst.md（{agate_root}/assets/execution-roles/analyst.md）
- [x] 读取 P0-brief.md（四字段齐全：task/issues/known_risks/executor_env+env_constraints）
  - 时效性质疑前置验证：TAG0019 v0.58.0（风险分路由）已在 worktree 合并（git log 4604836 "merge: 同步 main（TAG0019 v0.58.0）进 TAG0020"），与 P0-brief issue 7 / dispatch-context 上游关联描述一致 → 方案前提未漂移（详细判定写入 P1-requirements.md）
- [x] 读取 design-independent-judge.md —— 设计提案要点：judge review-role（P6.5 强制）/三层防造假（信息隔离白名单+证据交叉核对+append-only gate-events.jsonl 哈希链）/三档预算（轮次≤2/token 100k/时间 30min + partial 诚实降级判 needs-revision）/状态机 P6→P6.5→P7 + 弹回 / 文件改动清单 §7（13 项）/ 设计红线：不引入 LLM 当 gate 主判据
- [x] 读取 HANDOFF-TAG0020.md —— 交接单要点：双工作区纪律/交付物 7 项/核心约束 5 条（历史兼容、不引入 LLM 主判据、平台无关、SELF-GATE 全触发）/阶段推进纪律含【强制】P1 同类扫描三组
- [x] 同类扫描组1：review-roles 现状 + status 门槛映射
  - worktree `agate/assets/review-roles/` 共 10 文件（cso/design-review/investigate/plan-ceo/plan-design/plan-eng/protocol-alignment/qa/review/requirements-review）
  - frontmatter 统一：role_id/type: review/phases/agent；status 门槛表权威在两处：role-system.md:110-116 + rules/review-mapping.md:38-42（approved/rejected/needs-revision，needs-revision 计入重试）
  - 各评审角色文件尾统一"File + Status 报告"句；评审迭代入口表 dispatch-protocol.md:575-577（P1/P2/P4）
  - judge 挂靠结论：新 review-role（role_id: judge / type: review / phases: [P6.5] / agent: judge），status 沿用三值映射（passed→approved / needs-revision→needs-revision / rejected→rejected），需补 P6.5 行到 dispatch-protocol 迭代表 + state-machine 重试表
- [ ] 同类扫描组2：dispatch-context 注入内容 → 白名单反推（check-gate.py / pre-commit-gate.py + 注入脚本）
- [x] 同类扫描组2：dispatch-context 注入内容 → 白名单反推
  - dispatch-context 模板（assets/templates/dispatch-context.md）：frontmatter + dispatch_guide（目标/约束/上游关联/输入文件）+ AGATE_CARD（agate-inject-card.py 注入）+ objective_info（环境状态/关键标识/查证结果）
  - pre-commit-gate.py 2p：各阶段强制 dispatch-context 存在 + 卡片 hash 校验；agate-extract-context.py 从上游产出提取字段注入上游关联节
  - **先例**：check-p6-provenance 审计 2 已扫描 P6-dispatch-context 禁含行首 `- PASS|FAIL` 预判（排除 AGATE_CARD 块 + frontmatter）→ judge 白名单校验的直接祖先，P6.5 扩展该机制
  - 白名单反推：judge 禁传 = P6-acceptance.md（自述）+ 上游关联注入的 verifier 产出摘要 + 验收结论预判；白名单 = P1-requirements.md + P2-design.md 验收节 + P6-evidence/ + .state.yaml + gate-events.jsonl + git log 权
- [x] 同类扫描组3：check-p6-provenance 六道审计 + 事件账本交集
  - 审计 1 证据-结论对应（1a 引用存在/1b 空证据/1c 充数拦截）｜审计 2 dispatch-context 内容约束｜审计 3 BDD 总数对照（P6≥P1）｜审计 4 vision YAML｜审计 5 日志 EXIT_CODE 尾行一致性（P6-evidence/*.log）｜审计 6 evidence JSON 一致性｜审计 7 P5 证据复用（.state.yaml p5_pass_commit）
  - 账本交集：①审计5消费 log EXIT_CODE、账本 gate_run 也记 exit——同源不同层（账本=全阶段事件源+哈希链；审计5=P6 证据目录约定），P2 需字段交集 ②审计7消费 .state.yaml 状态 vs 账本 state_transition 事件——双写同步语义 P2 定 ③审计3 计数口径（P1 BDD 数）→ judge criteria_total 复用 ④审计1 证据存在性 → check-judge-verdict 复用 check-p6-evidence 逻辑 ⑤哈希链/时间戳单调为账本独有，审计 1-7 无此机制，无冲突
- [x] 读 state-machine.md / WORKFLOW.md / dispatch-protocol.md（P6.5 挂载点）
  - state-machine: 状态集合 L72 {P0..P8}；转移表 P6→P7 L134（check-gate P6 exit 2 + check-p6-provenance exit 0）；重试上限表 L390-398（P6=2/P7=2，P6.5 需加行）；回退表 L584-616（P6.5 needs-revision→P6 弹回）
  - WORKFLOW: P1-P8 总览表 L282-294（P6 行后补 P6.5 行）；gate 调度表 L311-323（check-p6-evidence L317 / check-p6-provenance L318 → P6.5 加 check-judge-verdict/check-events 行）；转移 gate 表 L745（P6→P7 行需加 P6.5）
  - dispatch-protocol: dispatch-context 定位 L308；do→review 迭代表 L567-578；自写文件 gate 弱点表 L765-769（judge 为 LIMITATIONS-3 根治点）
  - **影响面（组1/组3 交叉命中）**：agate-state-yaml-check.py valid_phases L17 无 "P6.5"；check-state-transition.py _DEFAULT_MAX_RETRY_MAP L28 + _PHASE_OUTPUTS L37-40 无 P6.5；agate-next-card.py / agate-render-dispatch-prompt.py PHASE 枚举 P0-P8——P6.5 挂载方式须与这些校验体系兼容（P2 设计决策：.state.yaml 独立 phase 值 vs P6 内嵌门槛）
  - LIMITATIONS.md 局限 3（L21-46）："self-authored gate 只能缓解无法根治"是 judge 机制的反向锚点；机制落地后该节现状描述需同步（隐含需求）
  - "P6.5"/"gate-events"/"judge verdict" 无现有协议命名占用（check-tdd-red 的 judge_result 是另一语义）；dsh/SKILL.md 食谱 2 + platform-notes L188 已预埋 judge/ralph 映射
- [x] 写 P1-requirements.md（211 行；frontmatter 机器字段齐全：phase/task_id=TAG0020-independent-judge/type/parent/trace_id=TAG0020-P1-20260822/status/created/agent + risk_level: medium/phases 全流程/packages: [agate]/domains: [backend]/capability_requirements: []）
  - BDD 10 条（BDD-1~10，`#### BDD-NN:`，Given/When/Then，可二值判定）
  - 同类扫描三组结论落盘正文第 4 节（命中数量 + 文件清单 + 逐条判定 + 回归拦截声明）＋P0-brief 时效性核对（第 2 节，无漂移）
  - [NO_NEED_CONFIRM]；2 条 [SUGGEST:] 倾向项；无 status: GAP
- [x] 自检：agate-frontmatter-check.py（FILE env）exit 0；grep 确认 BDD-1~10 连续、无 NEED_CONFIRM/GAP/P0_STALE
- [x] 状态标记：[PROD_NOT_TOUCHED]（本任务仅读协议本体 + 写任务工作区文件，未触碰生产代码）## [requirements-review] 步骤记录
- 1/7 已读 P1-dispatch-context-requirements-review.md（派发指引 + P1 卡片注入）
- 2/7 已读 requirements-review.md 角色定义 + AGENTS.md 项目约定（workspace 注入）
- 3/7 已读 P1-requirements.md（评审对象，211 行）+ P0-brief.md（26 行）
- 4/7 已读 design-independent-judge.md（设计提案，170 行）+ HANDOFF-TAG0020.md（83 行）
- 开始独立核实：同类扫描三组命中 + 锚点验证（BDD 格式/frontmatter/既有机制）
- 5/7 独立核实完成（全部锚点验证）：
  - 同类扫描组1：review-roles 10 文件 ✓ / role-system L108-116 status 映射 ✓ / review-mapping L38-42 ✓ / dispatch-protocol L575-577 迭代表 ✓ / C8 表 role-system L52-66 ✓ / 第二层角色清单 L37+ ✓
  - 组2：dispatch-context 模板 ✓ / pre-commit-gate L350-397 ✓ / agate-inject-card + agate-card-inject 均存在 ✓ / agate-extract-context 存在 ✓ / check-p6-provenance 审计2 L318-355（白名单先例）✓
  - 组3：check-p6-provenance 七道审计（1-7）✓ / check-p6-evidence ✓ / agate-evidence-consistency ✓
  - 哲学红线 BDD-9 ✓ / 历史兼容 BDD-2 ✓ / 预算 BDD-8 ✓ / frontmatter 六项合法 ✓ / git 实证 4604836 + check-routing + agate-risk-score ✓ / LIMITATIONS-3 原文 ✓ / valid_phases+MAX_RETRY_MAP 无 P6.5 ✓ / _PHASES P1-P8 ✓ / agate_common 无 append_event ✓
- 发现：BDD-4 "自述摘要"无机械检测锚点（§4.2 识别的 extract 注入禁项未固化进 BDD）+ §4.3 标题"六道审计"vs 内容"七道审计"不一致
- 结论：needs-revision
- 6/7 P1-review.md 已写入（needs-revision）；7/7 自检通过（Header 完整 + status=needs-revision + BDD 锚点）

## 修改轮 1（requirements-review needs-revision → 修订 R1/R2，2026-08-22，analyst）

- [x] 读取 P1-dispatch-context-analyst-rev1.md（增量模式）+ P1-review.md（status: needs-revision，2 条修改项）
- [x] R1：BDD-4 禁项 2 固化为可机械判定的黑名单路径引用集
  - §4.2 白名单反推结论重写为四行表（黑名单自述文件路径 / 黑名单语义禁注入 / 黑名单继承先例 / 白名单准入），并声明"黑名单路径引用集 = BDD-4 机械判定的权威定义，禁入项 P1 固化、不在 P2 再议；P2 只负责扫描实现"
  - BDD-4 重写：检测范围限定『输入文件』与『上游关联』两节路径扫描 + 全文行首预判扫描（排除 AGATE_CARD/frontmatter）；禁项 = 黑名单七模式（P6-acceptance.md / P6·P5·P4-dispatch-context-*.md / P4-implementation.md / P4-review.md / P5-test-results/）+ 白名单外路径引用；『上游关联』节声明 agate-extract-context P6.5 禁用或净化
  - 同步 L28 需求复述防造假①项 + §4.2 审计 2 行措辞（黑名单路径引用集）——均完成（edit 全成功）
- [x] R2：§4.3 标题/结论 + §3 兼容行"六道审计" → "七道审计（审计 1-7）"统一口径（3 处 edit 完成，grep 确认全文无"六道"残留）
- [x] 自检：agate-frontmatter-check.py（FILE env）exit 0；grep 确认 BDD-1~10 连续、黑名单锚点双固化（§4.2 表 + BDD-4）、无 [NEED_CONFIRM]/GAP/"六道"；[PROD_NOT_TOUCHED]

## [requirements-review] 复审轮（修改轮 1 后）
- 已读修订版 P1-requirements.md（215 行）与 progress 修改轮记录
- R1 复核通过：全文无"自述摘要"残留；BDD-4 黑名单七模式/白名单六项/扫描范围（输入文件+上游关联两节路径扫描+全文行首预判）机械可判定；§4.2 四行结论表与 BDD-4 逐项一致；权威定义"禁入项 P1 固化、P2 只负责实现"；L28/L98 同步措辞 ✓
- R2 复核通过：§3 兼容行/§4.3 标题/命中数量/结论四处"七道审计（审计 1-7）"，grep 六道=0 残留 ✓
- 全量复评：BDD-1~10 连续（L135/140/145/152/157/162/169/174/181/186）可二值；同类扫描三组无改动不需重验；哲学红线 BDD-9/历史兼容 BDD-2/三层防造假 BDD-4-7/预算 BDD-8 均达标
- 结论：approved（无新引入问题）
- [requirements-review] 复审轮产出：P1-review.md 已覆盖写入（status: approved）；自检通过（Header 完整 8 字段 / status=approved / BDD 锚点 35+ / 无残留词）
