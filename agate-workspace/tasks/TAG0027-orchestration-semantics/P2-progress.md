# P2-progress.md — architect 工作日志（TAG0027）

## 设计计划（候选方案探索 + 影响面梳理顺序）
1. 读派发上下文与角色定义（已完成：dispatch-context + architect.md）
2. 需求基线全读：P1-requirements.md（25 BDD + I-1~I-17 + D-1~D-7）→ P0-brief.md → design v3b（全读）
3. Phase 1 对象：agate/rules/phases.yaml + phases.schema.json + state-machine.md（74-78/95-99/132-133/139/148/151-157）+ check-structure-consistency.py（S-1/S-2 锚点）+ WORKFLOW.md（287-304 总览表 + 141-148 已知适用环境表）
4. Phase 2 对象：check-gate.py（exit 三态/gate_p* 结构/OLD_PHASE 回退检测）+ check-state-transition.py（P2.3-P2.5/MAX_RETRY_MAP）+ agate-retreat-to.py/agate-retreat-state.py + loop-orchestration.md（档位 A/B/C + 227-243 gate 处理流程）
5. Phase 3 对象：dispatch-protocol.md（五模式 511-519 + dispatch-context 规范）+ grep 平台名污染三分类
6. Phase 4 对象：agate-inject-card.py/agate-card-inject.py/agate-render-dispatch-prompt.py/agate-next-card.py + check-p6-provenance.py（审计 2 ~318-355）+ assets/templates/dispatch-context.md + agate_common.py（按需）
7. 护栏 1 对象：check-protocol-consistency.py（CHECK 1-13 + 分区）+ P1 评审 4 条边界观察核实（grep 实证）
8. 综合：影响面梳理（Modify/Not Modify/Risk）→ 候选方案 ≥2/设计域 → gate_commands 固化 → files_to_read → env_constraints → minimal_validation → dispatch_plan → 落盘 P2-design.md（frontmatter 用 agate-md-field-set）→ 自检


## 读文件发现（1/3：P1 + P0）
- P1-requirements.md 全读：25 BDD（Phase1=1-5 / Phase2=6-13 / Phase3=14-17 / Phase4=18-25），
  隐含 I-1~I-17，同类扫描 D-1~D-7 判定，domains=[backend,cli,api]，risk=high，
  packages=[agate-protocol]。需求要点：
  - BDD-1：P0-P8 主线 9 条目均含 next/retreat；P8 next 值域例外由 P2 定
  - BDD-2：P6.5 非独立转移边（state-machine.md:74-78 口径）
  - BDD-4：S-1/S-2 复用（不新开检查），md 侧 = WORKFLOW.md 总览表
  - BDD-8/9：exit 2 通用暂停+落盘 exit2-resolution；P6 exit 2 例外直通 P6.5（不落盘不停等）
  - BDD-12：exit2-resolution 纳入 P6.5 judge/provenance 复核（check-judge-verdict.py 或 check-events.py 挂载，不新增机制）
  - BDD-14/15/16/17：五模式唯一锚点；数据面禁平台名；md 叙述文档仅限实现注记段落；豁免 = platform-notes.md/SETUP.md 整文件 + WORKFLOW.md「已知适用环境」表
  - BDD-18/19/25：方案 A 渲染时注入（Lazy Injection）+ 手工路径兜底两路并存；pre-commit 2p hash 校验兼容
  - BDD-20/21：审计 2 渲染产物联动 + 文件版兜底
  - BDD-22/24：护栏 1 机械化结构性判据进 check-protocol-consistency.py
  - I-1~I-17 隐含需求（schema/S-1/S-2/exit 三态消费/retry 同步/档位 C/pre-commit 2p/审计剥离/judge 挂载点/SELF-GATE/稳定版工具）
- P0-brief 全读：scope 四 phase + out-of-scope（judge 机制不动/五模式不重构/平台食谱不产品化/不新开独立一致性检查/门户不做）
  + known_risks 7 条 + env_constraints（SELF-GATE / 系统 python / --strict-errors-only / 稳定版派发工具）

## 读文件发现（2/3：design v3b + Phase 1 对象）
- design v3b 全读（213 行）：核心洞察三层拆解；4.1 五模式为唯一锚点；4.2 自动化在协议内（推进决策→转移表/gate exit code→状态落盘）；exit 三态表（0 直推/1 回退/2 暂停转主 Agent，P6 exit 2→P6.5 例外唯一）；4.3 三条护栏（结构性判据：数据面禁平台名、md 叙述面挂实现注记 `> 实现注记：`、豁免=platform-notes.md/SETUP.md/WORKFLOW.md 已知适用环境表）；4.4 渲染层；5. 资产衔接表；6. 落地路径四 phase；7. 风险对策表（回退照抄 state-machine.md、P6.5 子阶段、exit 2 落盘 exit2-resolution 纳入 judge/provenance 复核、CLI=档位 C 可观测层）
- phases.yaml（123 行）实读：主线 P0-P8 9 条目 + P6.5 独立条目（89-101 行注释声明"非独立 phase 值，挂载 P6→P7 转移"）；现有键 = id/name/exec_role/outputs/gates/retry_cap/task_fields；P8 无 next 例外需值域定义；agate-next-card.py M3 读 outputs/gates/retry_cap
- phases.schema.json（68 行）实读：items.additionalProperties=false（新增键必先改 schema 否则 S-5 ERROR）；id enum 含 P6.5；retry_cap enum [2,3]
- state-machine.md（737 行）实读关键锚点：74-78 P6.5 非独立 phase（.state.yaml 保持 P6 至 P7）；95-99 PAUSED 汇合；121 P5 gate→P6；132 P5 失败→P4 retry+1；139 P6 exit 2→P6.5（FAIL=0/证据非空 + provenance exit 0）；148 P6 BDD FAIL→P4；151-157 P6.5→P7 / needs-revision→P6（judge 轮次 ≤2）；重试上限表 403-412（MAX_RETRY：P1-4=3/P3,P5-P8=2）；.state.yaml 结构（judge 块/retries 块/retry_count）；回退规则 615-658（diff=1 直接退/diff≥2 PAUSED）；单步函数 6 回退跳变检测（diff≥2→PAUSED 基于 phase 编号差值）

## 读文件发现（3/3：Phase 2/4 脚本 + Phase 3 文档）
- check-gate.py（1418 行）实读结构：main() 1379-1414 解析 PHASE/TASK_DIR/OLD_PHASE → 回退抵达检测（old_num>new_num → stderr + exit 2）→ handlers dict（P0-P8 + P6.5）→ exit func(task_dir)。**关键**：exit 0=通过/1=未通过/2=需自判；既有 OLD_PHASE 参数已是"回退抵达→exit 2"约定。gate_p* 各阶段函数（gate_p2 784/gate_p65 1096 等）。不改返回约定，新 CLI 消费其 exit code
- check-state-transition.py（339 行）实读：CLI [STATE_FILE]；exit 0/1；检查 1 回退 diff≥2→PAUSED(exit 1)；检查 2 retries_over MAX → phase 须 PAUSED；检查 3 BDD-1/3 WARNING + BDD-2 回退须 retries[new_phase] 增长（阻断）；检查 4 单步回退 self-authored 产出须先归档。**关键语义**：.state.yaml 暂存变更才检查（git diff --cached）；PAUSED/READY/DONE 早退
- agate-retreat-to.py（196 行）实读：CLI TASK_DIR TARGET_PHASE REASON；逐阶归档+write_retreat+commit（每步独立 commit）；预检查 A 暂存区外文件、B 路径上 retry 超限；结束后提示建 DEBT 条目。**retreat 语义 = 逐阶 Pn→Pn-1，每阶 retry+1**
- check-p6-provenance.py（547 行）实读：审计 2 在 318-355 行——glob P6-dispatch-context-*.md → 剥 AGATE_CARD_START/END 物理块 → 剥 frontmatter → 数 `^\s*- (PASS|FAIL)` 预判。**审计 2 的物理锚点是改进对象（A1）**；审计 3 用 agate-md-field-get.py pass/fail；审计 1/4/5/6/7 各司其职。_SKIP_AGENT_CHECK 模式含 -dispatch-context-*.md
- loop-orchestration.md（256 行）实读：档位 A/B/C 定义（46-74）；硬中断点 50-63；执行逻辑 92-122（步骤 7 = 执行单步）；gate 处理流程 229-239（pre-commit exit 0→自动进入下一 phase）；档位 C 启动前提 202（OpenCode 自定义角色）；220-221 嵌套深度约定

## 实证命中（平台名污染 + 数据面禁词）——P1 评审观察②核实
- rules/dispatch.yaml law-1（19 行）："用 task 工具派发，动词是派发不是执行" —— **实证命中**：
  数据面含平台工具名 task（平台工具指代，非字段名组成部分）。BDD-15 禁词若含裸 task，此处是首个要清理点。
  改写方向：law 语义是协议语义词（派发动词纪律），可去掉 "task 工具" → "用 subagent 派发" 之类
  （subagent 也是 DSH 词？subagent 是协议通用角色概念——dispatch-protocol 全篇用 subagent，非平台特化，
  设计 v3b §4.2 亦用 subagent 作通用词）。P2 禁词扫描实现须区分：
  ①独立平台工具指代（OpenCode/Claude Code/DSH/workflow/ralph/goal/task 作动词宾语）
  ②字段名组成部分（task_fields/task_id/retries 无 task 键/tasks 目录名）——词边界判定 vs 子串判定。
- phases.yaml 亦含 task_fields 键（数据面）——同②，字段名不是指代，须豁免。
- rules/*.yaml 其它平台名 = 0 命中（roles.yaml 无平台名，dispatch.yaml 仅 law-1）。
- md 侧命中数与 P1 D-2 基本一致：adr.md(2)/AGENTS.md(1)/dispatch-protocol.md(2)/loop-orchestration.md(1)/
  platform-notes.md(16)/role-system.md(3)/SETUP.md(21)/UPGRADING.md(8)/WORKFLOW.md(7)。WORKFLOW 比 P1 记录的 5 多
  （可能是 5 行命中多词）。全协议 0 处「实现注记」标记（证实 P1：0 处）。
- P1 D-2 判定回顾：role-system.md 138/141/146（OpenCode 自定义角色语义段）、UPGRADING.md（DSH 平台支持版本条目）、
  adr.md ADR-008（决策叙事）、dispatch-protocol.md:1108（OpenCode 坑位=实现注记）、loop-orchestration.md:202
  （档位 C 前提=实现注记）、WORKFLOW.md 各命中=元信息；@P1 评审观察④：adr.md 本体在 agate/ 协议区不是 docs/reviews——
  豁免理由须改为"ADR-008 平台名属决策叙事（记录当时决策语境），按实现注记标记或协议区白名单豁免"，P2 定。

## 读文件发现（4/3 补：渲染/注入链 4 脚本 + check-structure-consistency + check-protocol-consistency 骨架）
- agate-inject-card.py（120 行）：CLI PHASE TASK_DIR → 调 agate-next-card.py PHASE 取卡片 → glob {phase}-dispatch-context-*.md
  （无匹配回退 {phase}-dispatch-context.md）→ 逐文件 env DC_FILE/CARD_FILE 调 agate-card-inject.py 注入。exit 0 全部完成/1 失败。
- agate-card-inject.py（29 行）：正则 `(<!-- AGATE_CARD_START -->\n)(.*?)(<!-- AGATE_CARD_END -->)` 替换。
- agate-render-dispatch-prompt.py（229 行）：CLI PHASE ROLE TASK_DIR [--rollback] → 渲染 dispatch-prompt.md 模板
  → 写 P{N}-dispatch-prompt-{role}.md + stdout。exit 0/1/2。PHASE 白名单仅 P1-P8（无 P0/P6.5）。
- agate-next-card.py（193 行）：CLI PHASE（P0-P8）→ 输出卡片全文。正式卡片（含 ## 节）原样透传；裸模板卡片从
  rules/phases.yaml 渲染 4 节（产出规格/派发/gate 规则/retry 上限）。_PHASE_CARDS 映射 P0-orchestrator…P8-release。
  P6.5 无独立卡片（不在 _PHASE_CARDS）。
- check-structure-consistency.py（534 行）实读 S-1~S-6 全实现：S-1/S-2 用 _parse_workflow_rows 解析 WORKFLOW 总览表
  行（id/name/role_cell 3 字段正则），_TABLE_ROW_RE = ^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|——
  **加列需同步此正则与行结构**（S-1/S-2 只取前 3 列，后续列不干扰？_TABLE_ROW_RE 匹配前 3 列，后面列会被忽略——
  需实证：加第 4/5 列后 m.group(1..3) 不变则 S-1/S-2 天然兼容加列）。S-3a/S-3b 双向 gate 命令、S-4 field_readers、
  S-5 schema（独立进程 check-yaml-schema.py）、S-6 引用完整性、S-0 编号自校验。
- check-protocol-consistency.py（1248 行）：CHECK 1-13 + PROTOCOL_FILES/PROTOCOL_DIRS/NARRATIVE_DIRS 分区；
  iter_md_files 遍历全部 md（rglob）；is_protocol_file/is_narrative_file；CHECK 10 脚本名引用漂移
  （_iter_script_ref_scan_files 显式文件集 + 协议目录 rglob）。护栏 1 新 CHECK 挂载点 = 此脚本（结构性判据扫描 md
  段落，复用 iter_md_files + is_narrative_file 豁免区；NARRATIVE_DIRS 已豁免 agate-workspace/tasks 等）。

## 重试轮（architect retry）
- 重试轮开工：采信上轮全部调查落盘（读文件发现 1-4 + 实证命中），不重复调查；按需补读 P1 BDD 全文 / phases.yaml / WORKFLOW 锚点后直接进入设计综合。


## 重试轮补读（按需，控制上下文）
- P1-requirements.md 全读（307 行）：25 BDD 原文 + I-1~I-17 + D-1~D-7 判定表逐条核实（与上轮摘要一致）。
  补读确认的细节：BDD-6/7/8/9 用 .state.yaml/check-gate exit 三态表述；BDD-10 Given 用 P7→P4 示例（评审观察①确认）；BDD-15 禁词清单原文含 task；
  D-2 判定表把 role-system/UPGRADING/adr/dispatch-protocol/loop 命中判"语义定义须清理或实现注记/元信息豁免"，platform-notes/SETUP/WORKFLOW 表/AGENTS:30 判豁免。
- phases.yaml（123 行）补读确认：主线 P0-P8 9 条目既有键 = id/name/exec_role/outputs/gates/retry_cap/task_fields；
  P6.5 条目（92-101）注释已声明"非独立 phase 值、挂载 P6→P7、供 check-gate.py P6.5 分发与 CLI 调用"——P6.5 已存在是既定事实，设计只加 gate_subphase 结构。
- phases.schema.json 补读确认：items.additionalProperties=false（68 行顶层 also false）；id enum 含 P6.5；retry_cap enum [2,3]；draft-07 subset。
- check-structure-consistency.py S-1/S-2 实证（60-181 行）：_TABLE_ROW_RE 不锚行尾、group(1..3) 只取前 3 列 → 总览表**加列不破坏既有 id/name/role 匹配**（实证结论：天然兼容加列）；S-1 比对 YAML id/name/exec_role ↔ 表行，S-2 反查。
- check-state-transition.py 全读（339 行）：暂存变更才检查（git diff --cached）；回退 diff≥2→PAUSED exit1；retries 对应性 BDD-2 阻断；_STALE_OUTPUTS={P1,P2,P6,P7}；
  MAX_RETRY_MAP 从 agate_common 导入（注意：**map 无 P6.5 键**——P6.5 retry 上限按 phases.yaml retry_cap:2 消费）。
- dispatch-context.md 模板（45 行）确认 frontmatter = phase/generated_by/task_id/role + AGATE_CARD_START/END 占位 + dispatch_guide/objective_info 结构（I-10 兼容对象）。
- gate-events.jsonl 实测格式：{"event":"gate_run"|"state_transition","cmd":...,"exit":...,"phase":...,"prev_hash":...,"ts":...}——append_event 落盘点确认。
- agate_common 函数面确认：read_rules_yaml(637)/known_phase_ids(669)/append_event(309)/write_gate_result(245)/split_frontmatter(696)/parse_gate_commands_block(784)。
- agate-md-field-set.py 全读：key 白名单 = GENERIC_HEADER_KEYS ∪ phases.yaml task_fields（agent 永久拒绝 set）→ P2 四机器字段 candidate_count/packages/domains/ui_affected 可 set；gate_commands 属正文块（_remaining_missing 查正文 parse_gate_commands_block）；需文件先存在。

## 设计决策定案（8 决策面）
D1 next/retreat schema 形态：主线 next ∈ {P0..P8, null}（P8 next: null 无自动后继）+ retreat ∈ {P0..P8, null}（null=无跨阶回退，exit1 重试本阶段）；P6.5 条目**不写 next/retreat**，
   增 gate_subphase: {hosted_on: P6, forward_to: P7, needs_revision_to: P6}（BDD-2 非独立表达，schema 声明该 object 键）；S-1 扩展做形态语义检查。
D2 S-1/S-2 md 侧：WORKFLOW 总览表（S1S2-ANCHOR 内 287-304）加 next/retreat 两列；_TABLE_ROW_RE 兼容性实证 = 加列不破坏前 3 列解析；S-1 扩展按行 split 取列 4/5；P6.5 行列标 "—（gate_subphase）" 跳过比对。
D3 exit2-resolution：任务目录文件 {phase}-exit2-resolution.md（frontmatter 机器字段 + 正文留痕），不塞 .state.yaml（嵌套字段一期拒绝）不加 events 类型；
   复核挂载 = check-judge-verdict.py（P6.5 时对比 events 中 exit:2 gate_run ↔ exit2-resolution 文件存在性/字段完整，缺→不通过），不新增机制。
D4 agate next/advance：agate-next.py TASK_DIR → 子进程 check-gate.py {phase} → exit0 查表 next 更新 .state + commit（check-state-transition 由 commit hook 消费暂存 diff）；
   exit1 调 agate-retreat-to.py {retreat}（复用逐阶归档+retry+commit）；exit2 通用（非 P6）落盘 exit2-resolution + 提示；P6 exit2 特例引导 P6.5（不落盘不停等）；
   agate-advance.py = 手动/多阶回退引导（逐阶 retreat-to，diff≥2 提示 PAUSED）。
D5 agate dispatch：新 agate-dispatch.py PHASE ROLE [TASK_DIR] [--guide FILE] → 模板骨架 + Lazy Injection（调 agate-next-card.py 取卡片渲染完整进 AGATE_CARD_START/END）+ 来源标记；
   手工路径（inject-card 占位符注入）保留；render-dispatch-prompt.py 既有 CLI 不动（BDD-23）。
D6 审计 2 A1：渲染产物标记 = generated_by: agate-dispatch.py + 卡片块首行 HTML 注释 `<!-- CARD-SOURCE: ... -->`；剥离 = 有 CARD-SOURCE 剥注释标记块 / 无则剥 AGATE_CARD_START..END 物理块，两路并存。
D7 档位 C：loop-orchestration.md 档位 C 推进点改"运行 agate next"；可观测证据 = agate next 每次推进 append_event(state_transition)+ commit；硬中断 exit2 → exit2-resolution + 转主 Agent（非 retry）。
D8 护栏 1：check-protocol-consistency.py 新 CHECK：md 段落级判据（块 = 标题/空行分隔 + 跳过代码围栏 + 词边界词表）+ 豁免（platform-notes.md/SETUP.md 整文件 + WORKFLOW.md「已知适用环境」节表行结构豁免）+
   数据面第二判据（rules/*.yaml+schema 词边界 + 既有键名豁免词典机械生成）；存量清理 = P1 D-2 9 文件三分类清单全处理（adr.md 按实现注记，不做整文件豁免——评审观察④修正）。
P1 评审 4 条：① BDD-10 示例修正 P6→P4；② task 禁词词边界+字段名豁免；③ 排查面（9 文件全处理）vs 扫描面（全协议 md）两表并陈；④ adr.md 豁免理由修正。


## 落盘完成（重试轮）
- P2-design.md 已产出（430 行，非空）：影响面梳理（Modify 15 行 / Not Modify 12 项 / Risk 13 条）→ 候选方案 2（A 薄 CLI 消费方采纳 / B 中心控制器否决）→ 8 决策面逐一定案（含各节备选形态否决理由）→ gate_commands 9 独立 key → files_to_read 14 项 → env_constraints → minimal_validation（纯代码逻辑声明 + 依赖清单）→ BDD 25 全覆盖映射表 → P1 评审 4 观察处理 → 完成标志 → dispatch_plan（frontmatter flow YAML + 正文批边界叙述）。
- frontmatter 经 agate-md-field-set 写入：candidate_count=2 / packages=[agate-protocol] / domains=[backend,cli,api] / ui_affected=false；dispatch_plan 单行 flow YAML 与 candidate_count 同级（check-frontmatter exit 0 验证通过，不入 schema 缺省不校验）。
- 自检：文件存在非空（430 行）+ check-frontmatter.py exit 0 + yaml frontmatter 可解析。
- [PROD_NOT_TOUCHED]：本重试轮未改动任何 worktree agate/ 协议文件（只读调查 + 任务目录产出/日志写入）。

---

## P2 评审计划（plan-eng-review 追加）
评审角色：plan-eng-review（唯一 P2 评审，C8: backend+high → 直接产出 P2-review.md 无组长环节）
评审顺序：
1. 读 dispatch-context（完成）→ 读角色定义 plan-eng-review.md（完成）
2. 全读 P2-design.md（评审对象）→ P1-requirements.md（BDD 对照）→ P0-brief.md（范围）→ P2-progress.md（architect 实证核实）→ design v3b（按需）
3. 按需核实：state-machine.md 锚点 / phases.yaml / check-gate.py / check-state-transition.py / check-structure-consistency.py S-1/S-2
4. 逐项评审 13 维度：数据流 / 状态机 / 接口契约 / 错误边界 / 测试策略 / 多方案 / 实现就绪度 / minimal_validation / 范围锁定 / 8 决策面 / BDD 语义 / P1 评审 4 观察处理 / 审声明一致性
5. 产出 P2-review.md（Header status 用 agate-md-field-set 写）
6. 自检：文件非空 + check-frontmatter.py exit 0

## P2 评审发现（1/3：P2-design.md 全读）
- 结构：影响面梳理（§1 Modify 15 行 / Not Modify 12 项 / Risk 13 条）→ 候选 A/B（§2）→ 8 决策面（§3.1-3.8）→ 机器字段（§4 gate_commands 9 key / files_to_read 14 / env_constraints / minimal_validation）→ BDD 映射表（§5 25 条全映射）→ §6 评审 4 观察 → §7 完成标志 → §8 dispatch_plan 批边界。
- frontmatter：candidate_count=2 / packages=[agate-protocol] / domains=[backend,cli,api] / ui_affected=false / dispatch_plan static-batch 4 批（B1/B2 high / B3a medium / B3b high）。与审声明一致。
- gate_commands 9 独立 key 无 && 短路（P3 / P5 / P5_consistency / P5_structure / P5_schema / P5_shellcheck / P5_counttests / P5_selfgate + 各自 timeout_seconds）。注意 gate_commands 正文在 §4.1 用 ```yaml 围栏包裹——需确认 parse_gate_commands_block 是否按 yaml 块解析（gate 校验点，P2 gate 已由 architect 预跑？）。

## P2 评审发现（2/3：P1-requirements.md 全读）
- 25 BDD 语义权威已对照：BDD-1（9 主线含两键 + P8 例外值域 P2 定）；BDD-2（P6.5 非独立）；BDD-3（P5/P6→P4、P6.5→P6、diff≥2→PAUSED 不入表）；BDD-4（WORKFLOW 总览表 md 侧锚点，不新开检查）；BDD-5（兼容 S-3/S-4/M3）；BDD-6~13（Phase 2 CLI）；BDD-14~17（Phase 3 文档）；BDD-18~25（Phase 4 渲染 + 护栏）。I-1~I-17 隐含需求。
- BDD-10 原文 Given 仍是 "从 P7 按转移表回退到 P4（跨 ≥1 阶）"（158 行）——评审观察①说的 P7→P4 用边不当。P2 §6① 说 "P1 BDD-10 Given 修正为 P6→P4……由主 Agent 在 P2 通过后回改"。注意：设计只提出回改，P1 文件本身尚未改。需核实这是否构成设计缺陷（评审视角：P2-design §5 BDD-10 行验证手段 "pytest: diff≥2 --to 提示 PAUSED 拦截" 与其自身 §3.4 一致；BDD-10 Given 文本的 P7→P4 跨 3 阶示例与 P2 §3.4 advance 语义——P2 已把"示例语义 = P6→P4（diff=1 单步）"声明。这是 P1 待回改项而非 P2 缺陷，但要确认 P2 是否给 P4 implementer 足够防误指引）。
- BDD-15 禁词清单 = OpenCode / Claude Code / DSH / workflow / ralph / goal / task（186 行含 task）。P1 D-2 判定表把 role-system/UPGRADING/adr/dispatch-protocol/loop 判"语义定义须清理或实现注记/元信息豁免"，platform-notes/SETUP/WORKFLOW 表/AGENTS:30 判豁免——与 P2-progress 实证命中一致。
- BDD-16 豁免 = platform-notes.md/SETUP.md 整文件 + WORKFLOW.md「已知适用环境」表 141-148 行。
- BDD-17 排查面 = 9 文件。
- BDD-20 Given 明示"卡片块来源在渲染层可标记"→ P2 §3.6 CARD-SOURCE 注释回应。

## P2 评审发现（3/3：P0-brief.md 全读）
- out-of-scope 核对（评审项 4）：judge 机制不动 / 五模式本体不重构 / 平台食谱不产品化 / 不新开独立一致性检查。P2-design Not Modify（§1.2）12 项逐条覆盖这些 out-of-scope + BDD-13（返回约定）。
- P0 scope 原文 Phase 1 说 "rules/phases.yaml 增 next/retreat 字段（或扩展 rules/state-transitions.md 数据面）"——P2 选 phases.yaml 增字段，与 P1 BDD-1 一致，合法。
- env_constraints（P0）：SELF-GATE / 系统 python / --strict-errors-only / ~/.agate 稳定版派发工具。P2 §4.3 env_constraints 覆盖全部 + 不弱化；且 §4.1 gate_commands P5_selfgate 用 ~/.agate 稳定版、P5_consistency 用 worktree 版——双面正确。
- known_risks 7 条与 P2 §1.3 Risk 13 条映射关系：P2 R3/R4 缓解 check-gate/check-state-transition；R5 缓解 P6 exit 2 特例泛化；R6 P6.5 retry 上限。覆盖。

## P2 评审核实（state-machine + phases.yaml）
- state-machine.md 74-78 确认：P6.5 非独立 phase 值（.state.yaml phase 保持 P6 至 P7）；132 行 P5 --[failed>0 && retry<MAX]--> P4；148 行 P6 --[任何 BDD 标 FAIL && retry<MAX]--> P4 (retry+1)；139 行 P6 exit 2（FAIL=0/证据非空）+ check-p6-provenance exit 0 → P6.5；151-157 行 P6.5 → P7 / needs-revision/rejected → P6 重验（judge.rounds + 账本 ≤2）。
- phases.yaml 实读：9 主线条目（P0-P8）+ P6.5 独立条目（92-101 行，注释声明非独立 phase 值）。既有键 = id/name/exec_role/outputs/gates/retry_cap/task_fields（无 next/retreat）。设计 §3.1 示例 P5/P6.5 与现状结构一致。
- 关注点：设计称 P5/P6→P4 为"表内唯一 diff=2 特例"——实际 P5→P4 是 diff=1（state-machine 132 单步回退），仅 P6→P4 是 diff=2（state-machine 148）。措辞小瑕（P5 被误标 diff=2），不构成架构问题但 P4 实现时 retreat 表值要按 state-machine 核对。
- 待核实：check-state-transition.py 的 diff≥2→PAUSED 拦截与 state-machine 148（P6→P4 合法 diff=2 回退）如何并存；state-machine.md 600-680 回退规则。

## P2 评审核实（脚本层，关键矛盾点）
1. **check-state-transition.py 检查 1（256-262 行）**：`old_num>0 and new_num>0 → diff = old_num-new_num; diff>=2 → exit 1 强制 PAUSED`——**无条件，无 P6→P4 例外**。但 pre-commit 只在 .state.yaml 有暂存变更时跑；check-gate.py main 有 OLD_PHASE 回退抵达→exit 2 的既有约定（1379-1418 行 handlers dict 含 P6.5）。
2. **agate-retreat-to.py（136-137 行）**：`while n > target_n: nxt = n-1` 逐阶 P6→P5→P4（每步独立 commit + 归档 + retry+1 + pre-commit 校验）。→ 任何 diff≥2 的多步回退由 retreat-to 拆成 N 个 diff=1 commit，check-state-transition 检查 1 天然放行（每步 old_num-new_num=1）→ 设计"表内 P6→P4 直退会撞 diff≥2 拦截"的担忧与 retreat-to 逐阶语义矛盾——设计 §3.4 exit 1 分支"调用 retreat-to"实际**不触发** diff≥2 拦截，表内写 P6 retreat:P4 是安全的（retreat-to 逐阶落 P5 再 P4）。R11 缓解叙述部分失准（state-machine 652 行 P6→P4 走 PAUSED 是"人工跳转"路径，与 retreat-to 自动化逐阶不同轨）。
3. **check-gate.py gate_p6（1051-1093 行）**：恒 exit 2（证据非空且 FAIL=0）或 exit 1（FAIL>0/证据空），**无 exit 0 分支**。→ 设计 §3.4 查表 next 前进路径对 P6 形同虚设（P6 的"通过"就是 exit 2 → 特例转 P6.5，须 judge 复核通过后门禁 P6.5 exit 0 才推进 P7）；next 表 P6→P7 非 agate next exit 0 直推可达。§5 BDD-6 行对 P6 无覆盖（P6 恒 exit 2，BDD-6 Given exit 0 场景不含 P6，故"隐含缺口"多数场景成立）。更显著：P6.5 通过后 judge verdict status passed → 谁把 phase P6 改 P7？gate_p65 exit 0 后 agate next 读 .state.yaml phase=P6 → 查表 next 直推 P7 → 但 next 表对 P6 该填 P6.5 还是 P7？若填 P7，agate next 在 P6.5 复核前（.state.yaml 仍 P6）就把 phase 推到 P7，绕过 judge；若填 P6.5，gate_p65 exit 0 时 .state.yaml 已是 P7——agate next 无法表达"P6 停留直到 judge 通过"。→ **P6/P6.5 双 phase 共用一个 .state.yaml phase 值（P6）是状态机核心矛盾，next 表单值建模缺失**——设计 D1-A gate_subphase 只建模 P6.5 条目，未定义主线 P6 的 next 在该状态下的取值 → P4 implementer 遇到 BDD-6/9 场景无裁决规则。这是**实现就绪度缺口**（架构问题级）。
4. **gate_commands 解析（agate_common:779）**：`_GATE_COMMANDS_BLOCK_RE = ^gate_commands:[ \t]*\n((?:  .*\n|\s*\n)*)` → 正文 YAML 围栏块模式实际被支持（frontmatter 内 gate_commands 值 + 正文块双读取，M2 语义）。P2 §4.1 用 ```yaml 围栏包块不破坏解析（_GATE_KEY_LINE_RE `^  (\w+):\s*(.+)$` 匹配 2 空格缩进键）。**但**：field-set _remaining_missing 的 gate_commands 查正文块 parse_gate_commands_block(body)——P2 的 gate_commands 在正文 §4.1 围栏内，_GATE_COMMANDS_BLOCK_RE 会命中（块行以 `  ` 缩进），兼容✓。
5. **pre-commit 2p 卡片 hash（425-448 行）**：期望 = agate-next-card.py {phase} stdout 逐字节（CR 剥离 + rstip）；嵌入 = _extract_card（AGATE_CARD_START..END 之间，不含标记行）。**CARD-SOURCE 若放 AGATE_CARD_START 之后、卡片正文之前 → 改变嵌入内容 → 2p hash mismatch exit 1**。设计 §3.6 说"卡片块首行含 `<!-- CARD-SOURCE: ... -->`"（247 行）→ 与 2p hash 校验**直接冲突**（除非 CARD-SOURCE 行在 AGATE_CARD_START 之前、或 2p 同步改、或 audit2 与 2p 剥取范围不对称）。设计 §3.5 第 3 点又说"frontmatter generated_by 差异是来源标记，pre-commit 2p 只看卡片块 hash 不看 generated_by，兼容"——把来源标记放在 generated_by（frontmatter）则 2p 兼容，但 §3.6 双锚点剥离用的 CARD-SOURCE 在块首行又与 2p 冲突。两处来源标记设计不一致 → **P4 实现会撞 2p hash 校验**（BDD-20/25 的矛盾面，未显式解决）。
6. **assets/ 扫描面（check-protocol-consistency PROTOCOL_DIRS:69）**：含 `agate/assets/`（全部角色/模板）+ phase-cards + rules。实测 `agate/assets/templates/dsh/SKILL.md` 大量 DSH/workflow/ralph/goal 命中（且是平台食谱——P0 out-of-scope 说"平台食谱不产品化"，SKILL.md 就是平台食谱资产）。P2 §3.8 CHECK 14 扫描对象"iter_md_files + is_protocol_file"→ **assets/ 全扫**。P1 评审边界观察③ 点名 custom-role.md:49,54 + architect.md:229 命中；实测另有 dsh/SKILL.md（全篇平台名）。P2 §6③ 把排查面写成"9 文件全处理"但**未把 assets/ 平台名命中（含平台食谱 SKILL.md）纳入清理或豁免设计** → 设计声称"上线首跑 = 0 命中基线"与 CHECK 14 的 assets/ 扫描面矛盾。CHECK 14 豁免 = platform-notes/SETUP 整文件 + WORKFLOW 表 + 实现注记段——不豁免 assets/templates/dsh/SKILL.md（平台食谱整文件）→ **上线即红**（除非把 SKILL.md 判为"平台食谱豁免"但 P0 out-of-scope 说食谱不产品化——SKILL.md 存在本身即食谱资产，其平台名密集，属需显式判定的新类）。设计未处理 P1 评审观察③ 的扩展面建议 → 架构问题。

## P2 评审核实补充（结论支撑）
- gate_p65 exit 0 = P6→P7 唯一机械门槛（judge verdict + 双脚本）；.state.yaml phase 全程 P6。agate-next 若 phase=P6 时跑 check-gate.py P6 → 恒 exit 2 → 每次打印"前进 P6.5 指引"→ judge verdict 就绪后再次 agate next 仍 exit 2 → **无裁决规则把 phase P6 推 P7**（BDD-6/9/11 在 P6 场景不闭环）。
- P6 retreat: P4（表内 diff=2）与 §3.4 exit1 分支条件"retreat 且 diff=1 才调 retreat-to"自相矛盾（retreat-to 实际逐阶 P6→P5→P4 天然合规，无需 PAUSED）；§3.1 注释与 §6① 对 P6→P4 的 diff 表述（2 vs 1）互斥，P5 被误标 diff=2（实际 diff=1）。
- 2p hash 期望 = agate-next-card.py stdout；嵌入 = _extract_card（AGATE_CARD_START..END 之间）。CARD-SOURCE 若在块内首行 → hash 变 → 2p exit 1；若替代 START → _extract_card 抽空 → 2p exit 1。设计 §3.6 与 §3.5（generated_by 兼容 2p）两处来源标记设计不一致且均未同步 pre-commit-gate.py 抽取逻辑。
- PROTOCOL_DIRS 含 agate/assets/ → CHECK 14 扫到 assets/templates/dsh/SKILL.md（全篇 DSH/workflow/ralph/goal 平台名，平台食谱资产）；B3a 批只列 9 顶层 md，assets/ 不在清理批、SKILL.md 不在豁免清单 → CHECK 14 上线即红（P1 观察③ 未落实）。

## P2 评审收尾（plan-eng-review）
- P2-review.md 已产出（211 行非空，status=rejected 经 agate-md-field-set 写入，agent=plan-eng-review）；check-frontmatter.py exit 0。
- 结论：rejected（3 阻塞 + 3 非阻塞）：A1 P6/P6.5 共用 phase=P6 时 judge 通过后 P6→P7 推进裁决缺失（gate_p6 恒 exit 2、gate_p65 exit 0 后无 CLI 消费）；A2 CARD-SOURCE 放卡片块内/替代 START 与 pre-commit 2p hash 校验冲突且与 §3.5 generated_by 标记不一致；A3 CHECK 14 扫描面含 agate/assets/（PROTOCOL_DIRS:69），SKILL.md 等 assets/ 命中不在 B3a 清理批也不在豁免清单 → 上线即红。非阻塞 B1（P6→P4 diff 口径互斥，P5 误标 diff=2）、B2（加列位置正文/示例/解析器三处不一致）、B3（minimal_validation 表述过强）。锁定决策 = 候选 A 架构方向 + 8 决策面形态（除 A1/A2/A3 修正处）批准。
- [PROD_NOT_TOUCHED]：评审全程只读 worktree agate/ 协议文件（核实现状），仅写任务目录 P2-progress.md / P2-review.md，未改动任何协议本体文件。

## 修复轮开工（retry1）
- 时间：读 dispatch-context 完成
- 修复指令：P2-review.md rejected，A1/A2/A3 阻塞 + B1/B2/B3 非阻塞
- 范围：定点修订 P2-design.md（不整文件重写），架构方向不推翻
## 修复轮实证复核（retry1，A1/A2/A3 落点）
- A1：check-gate.py gate_p6（1051-1093）恒 return 2（无 exit 0 分支）；gate_p65（1096-1120）exit 0 后 .state.yaml phase 仍 P6。state-machine.md 74-78 确认 P6.5 非独立 phase。P6 推进裁决 = 条件式（P6.5 门槛过 → 按 P6.next=P7 推）方案成立。
- A2：pre-commit-gate.py _extract_card（171-189）只取 AGATE_CARD_START..END 间行 → CARD-SOURCE 放 START **之前**（块外）不影响 2p hash；check-p6-provenance 审计 2（318-355）与 check-judge-verdict _strip_card（98-111，消费点 396-397）剥离 START..END 整块 → 剥离起点扩展为"CARD-SOURCE 行起"即可，三处消费方语义统一。dispatch-context.md 模板 START/END 单独成行（块内可注入 next-card stdout 全文）。
- A3：check-protocol-consistency.py PROTOCOL_DIRS:69 含 agate/assets/；实测平台名（OpenCode/Claude Code/DSH/deepseek-harness/ralph）命中 = assets/templates/dsh/SKILL.md（DSH 平台食谱，17 处）+ assets/templates/custom-role.md:49-56（平台适配说明）+ assets/execution-roles/architect.md:229（无 prompt 派发场景举例）；phase-cards/ 0 命中。处置 = 平台食谱目录结构豁免（assets/templates/dsh/）+ 平台适配说明段挂注记（另 2 文件入 B3a）。
- B1：state-machine.md 132（P5→P4 diff=1）/148（P6→P4，diff=2 语义）/647-654（diff≥2 表）；agate-retreat-to.py 136-137 `while n>target_n: nxt=n-1` 逐阶 → CLI 不预判 diff。
- B2：WORKFLOW 总览表（290-302 行）5 列（阶段|名称|执行角色|评审角色|门槛）；_TABLE_ROW_RE 只取前 3 列 → next/retreat 加在 4/5 列，评审角色/门槛顺延 6/7 列。
- [PROD_NOT_TOUCHED]：本轮实证只读 worktree agate/，未改任何协议本体文件。
## 修复记录 A1（§3.1）
- §3.1 新增「P6 主线 next 条件式裁决（A1 定案）」段：P6 条目 next: P7（值域合法）；推进 = 条件式（gate_p65 exit 0 前置），CLI P6 分支消费 forward_to；schema 只管值域不管裁决。
- §3.1 retreat 口径修正（B1）：P5→P4 diff=1 / P6→P4 diff=2；P6→P4 的 diff=2 不触发 PAUSED（retreat-to 逐阶落地，state-machine:647-654 的 diff≥2→PAUSED 是人工直跳路径）；CLI 不预判 diff。
## 修复记录 A1（§3.4）+ B1（§3.4）
- §3.4 exit 1 分支：删 diff=1 前置 → "retreat 表值存在 → 委托 retreat-to（内部逐阶），CLI 不预判 diff"（B1）。
- §3.4 exit 2 P6 特例分支（A1 裁决）：gate_p6 exit 2 + provenance exit 0 → 查 judge.enabled → 未启用直推 P7（gate_p65 早退 0）；启用 → gate_p65 exit 0 前置成立 → 推进裁决成立，phase P6→P7 + add；exit 1 → 停留 P6 不推进不落盘。
## 修复记录 A2（§3.5/§3.6）
- A2 定案选 (a)：CARD-SOURCE 注释放 AGATE_CARD_START **之前**（块外）——不进 _extract_card 抽取区间、不影响 2p hash；§3.5 注入结构图 + §3.6 剥离锚点统一为"CARD-SOURCE 行起的物理块优先 + START..END 兜底"；三处消费方同步面写明（audit2 318-355 / check-judge-verdict _strip_card 98-111+396-397 / pre-commit _extract_card 171-189 无需改）；备选 (c)(d)（放块内/替代 START）实证否决。
## 修复记录 A3（§3.8 部分）
- A3 定案选①（含结构豁免）：CHECK 14 豁免结构补 assets/templates/dsh/ 平台食谱目录（SKILL.md 等，P0 out-of-scope「平台食谱不产品化」资产落地）；段落判据明确语义叙述面 = agate/*.md 顶层；存量清理批次面 = 9 顶层 md + assets/ 适配说明命中段（architect.md:229 / custom-role.md:49-56 挂实现注记）+ dsh/ 目录结构豁免。
## 修复记录 A3（§6③）+ B1（§6①）
- §6① diff 口径修正：P6→P4 diff=2（retreat-to 逐阶落地，CLI 不预判）；P5→P4 diff=1（state-machine:132）；diff≥2→PAUSED 是人工直跳路径。
- §6③ 三面并陈（A3 定案①）：排查面（9 顶层 md + assets 适配说明命中段）/ 扫描面（agate/*.md 语义面 + assets 非豁免适配段）/ 结构豁免面（platform-notes/SETUP + assets/templates/dsh/ 平台食谱目录 + WORKFLOW 表行）。
## 修复记录 B2（§3.2）
- §3.2 加列位置统一为 4/5 列（执行角色后，评审角色/门槛顺延 6/7 列）：示例表头/数据行/解析器取列/S1S2-ANCHOR 注释四处一致。
## 修复记录 B3（§4.4）
- §4.4 minimal_validation：method 补 ⑧ P6 judge 后推进裁决链、⑨ CARD-SOURCE 过 2p hash（A1/A2 定案主线）；note 弱化"均已用实读代码确认"→ 代码逻辑假设不豁免失败测试首写，4 条 P4 首写失败测试主线（②⑥⑧⑨）。
## 修复记录 A1/A2/A3（§5 BDD 映射表测试锚点）
- BDD-6 补 P6 通过路径（judge 未启用直推 P7）锚点；BDD-9 补 P6 judge 后推进（gate_p65 exit 0 → P6→P7；exit 1 → 停留）锚点；BDD-7/10 补"不预判 diff / retreat-to 逐阶"措辞。
- BDD-17 补 assets/ 处置测试锚点（dsh/ 豁免 + 适配段注记）；BDD-18 补 CARD-SOURCE 块外断言；BDD-20 补剥离起点锚点；BDD-25 补含 CARD-SOURCE 过 2p 测试锚点。
## 修复轮收尾（retry1）
- §7 完成标志强化：P6 推进裁决闭环（A1）/ 审计 2 CARD-SOURCE 过 2p（A2）/ 护栏 1 assets dsh 豁免 + 命中段注记（A3）。
- 一致性自检通过：R6/R7/R8/R11、BDD-3、§6① diff 口径全修正；§3.6 标题去"A1"歧义（原为审计机制旧标签，与阻塞项 A1 撞名）；check-judge-verdict.py Modify 行补 _strip_card 双锚点同步（A2 消费方）。
- check-frontmatter.py exit 0；P2-design.md 498 行完整。
- [PROD_NOT_TOUCHED]：仅定点修订任务目录 P2-design.md / P2-progress.md，未改任何协议本体文件。

---

## 复审轮开工（plan-eng-review retry1）
- 时间：复审轮开始
- 输入：dispatch-context-plan-eng-review-retry1.md + 首轮 P2-review.md（rejected，A1/A2/A3/B1/B2/B3 建议原文）+ P2-progress.md 修复轮记录
- 任务：逐条核对 6 问题闭合度，产出 P2-review.md 终局判定
## 复审逐项核对（plan-eng-review retry1，6 项闭合度）
- **A1 闭合**：修复落点 §3.1 148-165（P6 条目 next: P7 + 条件式裁决三步：gate_p6 exit 2 + provenance exit 0 → 查 judge.enabled 未启用直推 / 启用跑 gate_p65 exit 0 → 消费 next:P7 + state_transition + add，exit 1 停留 P6）+ §3.4 253-264（exit 2 P6 特例分支，删"只引导复核"缺裁决）+ §5 BDD-6 447 / BDD-9 450（P6 通过路径锚点）。实证核对：check-gate.py gate_p6 1051-1093 恒 return 1/2 无 exit 0（1093 return 2）；gate_p65 1096-1120 judge 未启用 return 0 早退 / verdict 缺 return 1 / 双脚本过 return 0——设计与脚本行为逐条对应；state-machine.md:139 P6 exit 2→P6.5 + 74-78 phase 保持 P6。裁决闭环完整（谁推进、什么条件、不成立怎么办）。
- **A2 闭合**：修复落点 §3.5 282-290（CARD-SOURCE 放 AGATE_CARD_START 之前块外 + 不进 _extract_card 区间）+ §3.6 300-320（D6-A 双锚点剥离：CARD-SOURCE 行起物理块优先 + START..END 兜底 + 三处消费方同步面 311-318：check-p6-provenance 318-355 需改 / check-judge-verdict _strip_card 98-111+396-397 需改 / pre-commit _extract_card 171-189 天然兼容无需改）+ §5 BDD-18 459 / BDD-20 461 / BDD-25 466。实证核对：pre-commit-gate.py _extract_card 171-189 只抽 START..END 之间行（183 行 in_block 起 / 186 行 END 止）→ 块外 CARD-SOURCE 不影响 hash；2p 425-448 期望=next-card stdout 嵌入=_extract_card。机制成立。
- **A3 闭合**：修复落点 §3.8 336-337（豁免结构补 assets/templates/dsh/ 平台食谱目录 + 语义叙述面=agate/*.md 顶层 + assets 非豁免 md 命中段按注记处理）+ 346（存量清理批次面：9 顶层 md + architect.md:229 / custom-role.md:49-56 挂注记 + dsh/ 不进批）+ §6③ 474（三面并陈含 assets）+ §8 B3a 494 + §7 484（完成标志可达）+ R8 79。实证核对：check-protocol-consistency.py PROTOCOL_DIRS:69 含 agate/assets/（实测）；assets/ 平台名命中实测仅 3 文件 = dsh/SKILL.md（17 处，目录实存 agent.cordis.yml/preset.yml/SKILL.md）+ architect.md:229 + custom-role.md:49-56——设计处置面全覆盖实测命中，无遗漏面。
- **B1 闭合**：修复落点 §3.1 172（P5→P4 diff=1 / P6→P4 diff=2 均 retreat: P4，diff=2 不触发 PAUSED = retreat-to 逐阶落地，647-654 PAUSED 是人工直跳路径；CLI 不预判 diff）+ §3.4 247-252（删 diff=1 前置，retreat 表值存在即委托）+ §6① 472 + R11 82。实证核对：state-machine.md:132（P5→P4）/148（P6→P4）/647-654（diff≥2 PAUSED 表，652 行 P6→P4 diff=2）实测一致；全篇无残留 "diff=1 前置" 表述。
- **B2 闭合**：修复落点 §3.2 180-198（统一 4/5 列：示例表头 184 next/retreat 在 4/5 列、解析器取 4/5 列 196、S1S2-ANCHOR 注释 191-193 注明 1-3 既有列/4-5 next-retreat/6 起评审门槛）。四处一致，首轮 163 行旧表头（6/7 列）已消除。
- **B3 闭合**：修复落点 §4.4 433（method 补 ⑧ P6 judge 后推进裁决链、⑨ CARD-SOURCE 过 2p hash）+ 435（note 弱化"均已实读确认"→ 不豁免失败测试首写，4 条首写主线 ②⑥⑧⑨）。表述与 A1/A2 定案一致。
- **测试缺口 3 条确认闭合**（dispatch-context 约束 3）：P6 judge 后推进 → §5 BDD-9/BDD-6 锚点；CARD-SOURCE 过 2p → §5 BDD-25/18/20 锚点；assets/ 处置 → §5 BDD-17 锚点（SKILL.md 豁免断言 + architect/custom-role 注记 pass）。
- **一致性抽查**：架构方向（候选 A）未推翻；8 决策面形态除 A1/A2/A3/B1/B2 修正处保持；§1.1 Modify 表已含 check-judge-verdict _strip_card 双锚点同步行（45）；gate_commands/files_to_read/env_constraints 未被修复波及失真；§7 完成标志 482-484 含 A1/A2/A3 三闭环表述。
## 复审轮收尾（plan-eng-review retry1）
- P2-review.md 已产出（94 行非空，覆盖首轮文件）；status=approved 经 agate-md-field-set 写入（agent=plan-eng-review）；check-frontmatter.py exit 0。
- 结论：approved（A1/A2/A3/B1/B2/B3 六项全部闭合 + §5 测试缺口 3 条补锚点确认 + 修复波及节连贯性抽查通过 + 无新矛盾）；遗留事项 0（仅 P1 BDD-10 Given 回改为主 Agent 跟进项，非 P2 缺陷）。
- [PROD_NOT_TOUCHED]：复审轮仅只读 worktree agate/ 协议文件（核实修复真实性），写任务目录 P2-progress.md / P2-review.md，未改动任何协议本体文件。
