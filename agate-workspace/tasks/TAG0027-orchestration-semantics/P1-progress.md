# P1 progress — TAG0027（analyst）

## 输入读取与发现（逐条追加）

### 1. P0-brief.md ✅
- task = 四 phase 全量纳入（Phase 1 转移表结构化 / Phase 2 推进侧 CLI / Phase 3 编排心智文档化 / Phase 4 渲染层+注入自动化）；范围锁定（S-1/S-2 复用、不新开独立一致性检查、P6.5 非独立口径、exit2-resolution、方案 A 两路并存、审计 2 A1 联动、护栏 1 机械化进 CI）。
- known_risks 7 条 = 核心 gate 消费方（不改返回约定）/ 档位 C 对接行为变更 / 转移表防漂移 / P6.5 口径 / exit 2 模型残留 / 审计 2 静态锚点失效 / 渲染时注入两路并存。
- env_constraints：改 agate/scripts/* + agate/rules/*.yaml + loop-orchestration.md + dispatch-protocol.md → 触发 SELF-GATE。

### 2. design-orchestration-semantics.md v3b ✅（213 行全读）
- §4.1 五模式锚点（模式 1 单发/2 静态拆批/3 并行/4 先理解后拆/5 串行链）语义表；§4.2 exit 三态表（0 直推/1 回退/2 暂停转主 Agent，P6 例外 exit 2 → P6.5）+「实现注记」示范表 + 三平台实现映射（DSH workflow/ralph/goal）。
- §4.3 护栏三条：①数据面（rules/*.yaml）禁平台名 + markdown 仅带「实现注记」标记可含（`> 实现注记：` 标记行）；②platform-notes/SETUP/WORKFLOW「已知适用环境」表整文件/整表豁免；③通用食谱先于平台食谱。
- §5 资产表：回退侧 CLI 已存在非缺口；真实缺口 = ①phases.yaml 无 next/retreat ②无推进 CLI ③档位 C 推进靠主 Agent 自律。
- §6 落地路径 Phase 1-4（v3b：P6.5→P6 回退、next/retreat 纳入 S-1/S-2、exit2-resolution、CLI=档位 C 可观测层）。
- v3b 修复闭环（4 NIT）：裁剪跳变示例 = P2→P4/P5→P7/P6→P8/P7→DONE；4.4 补「实现注记」；S-1/S-2 md 侧锚点 = WORKFLOW 总览表；exit 三态补 P6 例外。

### 3. review-orchestration-semantics-v3-20260902.md ✅（复审 PASS + 4 NIT 闭环确认）
- v3a → v3b 修复闭环 4 NIT 逐条确认（N-New1 跳变示例、N-New2 4.4 实现注记、N-New3 S-1/S-2 md 锚点、N-New4 exit 2 P6 例外）；15 项评审发现全闭合；PASS。

### 4. review-orchestration-semantics-v2-independent-20260902.md ✅（按需通读）
- 补充想法 4 条（exit2-resolution 子状态 / CLI 档位 C 可观测层 / S-1-S-2 纳入 / 结构性判据）采纳到 v3 的源头。

### 5. agate/state-machine.md ✅（重点节全读）
- 74-78：P6.5 挂载于 P6→P7 强门槛子阶段非独立 phase 值（.state.yaml phase 保持 P6 至 P7；推进判定 = check-gate.py P6.5 = check-judge-verdict + check-events 双 exit 0；judge 轮次 ≤2 由账本承载）。
- 95-99 PAUSED 汇合；132-133 P5→P4、148 P6→P4（retry+1）；139 P6 exit 2（FAIL=0/证据非空 + provenance exit 0）→ P6.5；151 P6.5 verdict exit 0 → P7；156-157 needs-revision → P6 重验（judge 轮次 ≤2）。
- 218-224 裁剪跳变；233-241 SCOPE+；254-263 PAUSED 恢复；720-730 用户介入边界（硬中断点 PAUSED 表）。
- 步骤 5 同步注：check-gate.py 判定与 state-machine 同步——新增 CLI 不能改该契约。

### 6. agate/loop-orchestration.md ✅（全读 256 行）
- 档位 A（17 行手动）/档位 B（30 行半自动）/档位 C（46 行全自动，硬中断点必停列表 50-61 行）。
- 执行逻辑 94-121：每轮重读 active-tasks.md → 硬中断点检查 → 执行单步（派发→判定门槛→更新状态）。
- 227-243 档位 C gate 处理流程：每次阶段 commit 过 pre-commit hook，exit 0 自动进下一 phase / exit 1 PAUSED / exit 2 WARNING 通过；硬中断点（PAUSED 而非 retry）244-247。
- 结论：档位 C 推进点即 pre-commit hook exit 0 后"自动进入下一 phase"的判定——agate next 的可观测层落点。

### 7. agate/dispatch-protocol.md ✅（五模式 511-519 + dispatch-context 规范 + 执行模式）
- 五模式表 511-519（语义权威）；模式 4 流程 521-539（合并语义 BDD 全局编号/包归属去重）；并行规则 541-551。
- dispatch-context 规范 306-374：模板含 `<!-- AGATE_CARD_START/END -->` 占位符 + "禁止手写 AGATE_CARD"；358 行 AGATE_CARD 注入 = agate-inject-card.py 唯一合法。
- 166-169 单 Agent 顺序模式（has_task_tool: false）——编排降级场景与"叙述面豁免"边界相关。
- 1108 OpenCode 坑位（issue #29616）——平台适配/实现注记面。

### 8. agate/rules/phases.yaml ✅（全读 122 行）
- 10 条 P0-P8 + P6.5（92-101 行，注释"挂载于 P6→P7 强门槛子阶段非独立 phase 值"）；每条 id/name/exec_role/outputs/gates/retry_cap/task_fields；**无 next/retreat 字段**。
- schema_version: 1；S-1/S-2 锚点 + S-5 schema 校验。

### 9. agate/rules/schema/phases.schema.json ✅（全读 68 行）
- 顶层 properties 仅 schema_version/phases；phase item required=[id,name,exec_role]；id enum 含 P6.5；additionalProperties:false → **新增 next/retreat 须在 schema 层声明字段**，否则 S-5 拦截。
- retry_cap enum [2,3]；task_fields string 数组——next/retreat 需扩展（retreat 可能需表达跨阶段的 "diff≥2→PAUSED" 语义，设计 v3b 用"下一动作"字段建模 exit 2）。

### 10. check-state-transition.py ✅（全读 339 行）
- exit 0/1；P2.3 跳变合法性（回退 diff≥2 → exit 1 强制 PAUSED）；P2.4 retry 超限；P2.5 回退 diff==1 单步（retries 同步校验 BDD-2 阻断 + 归档要求）；RM-AG0042 评审重试/空返回 WARNING。
- 契约：只读 .state.yaml + git HEAD 对比，不读 phases.yaml next/retreat——agate next 消费方（复用 P2.3-P2.5）。

### 11. check-gate.py ✅（docstring + P6.5 分发 + 关键分支）
- exit 0/1/2 契约 + OLD_PHASE 第 3 参回退抵达 → exit 2。P0-P8 全分支已实现。
- judge/P6.5 机制在 .state.yaml + pre-commit 层；check-gate 不直接落 exit2-resolution。

### 12. agate-retreat-to.py / agate-retreat-state.py ✅（回退侧 CLI 现状）
- retreat-to: TASK_DIR TARGET_PHASE REASON，多步单向回退（每步独立归档+commit+gate），exit 0/1。
- retreat-state: 读改写状态（write_retreat/check_retreat）env 契约。
- 结论：回退侧已存在非缺口；agate next/advance 与 agate-retreat-to 对接（advance 的 exit 1 分支可调 retreat-to）。

### 13. check-p6-provenance.py 审计 2 ✅（318-355 行）
- 现状 = 逐 dispatch-context 文件剥离 AGATE_CARD 物理块（in_card 状态机）+ 剥离首对 frontmatter → 数 PASS/FAIL 预判。
- A1 联动：改渲染时注入后文件里无物理卡片块 → 审计 2 改为扫渲染产物；排除逻辑（卡片内容不判预判）须在渲染层标记来源延续。

### 14. check-structure-consistency.py ✅（S-1~S-6 现状 + 行 7-11）
- S-1 YAML→md（phases.yaml id/name/exec_role ↔ WORKFLOW 总览表行，287-299 行锚点 S1S2-ANCHOR）；S-2 md→YAML；S-3/S-4/S-5/S-6。
- next/retreat 纳入 S-1/S-2 的扩展面：字段须在 WORKFLOW 总览表（或另加列）有 md 侧对应。

### 15. agate-inject-card.py / agate-card-inject.py / agate-render-dispatch-prompt.py ✅
- inject-card: PHASE TASK_DIR（两参）；经 agate-next-card.py 取卡片 → agate-card-inject.py 注入 AGATE_CARD 占位符；exit 1 = 占位符缺失（"注入失败→手动修"环节的源头）。
- card-inject: env DC_FILE/CARD_FILE，正则替换 AGATE_CARD_START/END 之间。
- render-dispatch-prompt: PHASE ROLE TASK_DIR [--rollback]，渲染模板到 P{N}-dispatch-prompt-{role}.md + stdout——主 Agent 手拼 prompt 场景（消费方：无 repo 内其他脚本调用，仅模板/文档/测试引用）。

### 16. check-protocol-consistency.py ✅（护栏 1 挂载点）
- CHECK 1-13 结构一致性；退出码 0/1/2；PROTOCOL_FILES/PROTOCOL_DIRS/NARRATIVE_DIRS 分区——护栏 1 机械化挂载为新 CHECK 14（markdown 含平台名无实现注记段落）。

### 17. AGENTS.md + worktree-dogfooding-guide ✅（双工作区纪律按需）
- 编排/派发工具用 ~/.agate 稳定版；check-protocol-consistency 用 worktree 自己的；SELF-GATE commit 需 self-gate-review 标注。

## 同类/影响面扫描（D 清单）

### D-1 next/retreat 字段：全仓 rules/*.yaml|schema/*.json 无任何 next/retreat 键（0 命中）→ 首增；既有检查面 = phases.schema.json（S-5）+ S-1/S-2（WORKFLOW 总览表锚点）+ agate-next-card.py M3 渲染（_render_sections 读 outputs/gates/retry_cap，若 next/retreat 进渲染面需同步）。
### D-2 平台名污染：worktree agate/*.md 命中 9 文件（adr/AGENTS/dispatch-protocol/loop-orchestration/platform-notes/role-system/SETUP/UPGRADING/WORKFLOW）→ 逐文件判定（见 P1-requirements 正文三分类）；全协议 0 处「实现注记」标记。
### D-3 inject/render 消费方：agate-inject-card.py 唯一运行时消费方 = orchestrator-template.md:60 + dispatch-protocol.md:358（主 Agent 派发）；agate-card-inject.py 仅被 inject-card 调；render-dispatch-prompt.py 无 repo 内脚本调用（模板/文档/测试引用）——手工场景 = 主 Agent 逐文件写 dispatch-context + 注入；存量任务 dispatch-context 591 处 AGATE_CARD_START（大量历史文件，A1 改渲染产物后仍保留文件版兜底，存量不动）。
### D-4 AGATE_CARD_START 锚点消费方：agate-card-inject.py（注入）、pre-commit-gate.py 2p/2g.1（hash 校验 + PROD_TOUCHED 剥离）、check-p6-provenance.py 审计 2、check-judge-verdict.py 审计 2 同款、check-retrospective.py、check-scope-resolved.py、assets/templates/dispatch-context.md、dispatch-protocol.md。
### D-5 exit2-resolution：全仓仅设计文档/HANDOFF/P0-brief/dispatch-context 引用 → 无既有机制（首增）。
### D-6 agate next / agate advance 命名：scripts/ 无同名；agate-next-card.py 是"输出当前阶段卡片"的既有脚本（命名相邻需防混淆，但功能不同不冲突）；active-tasks.md 已引用"agate next/advance"作任务描述。
### D-7 judge/P6.5 复核范围：check-judge-verdict.py 审计 2 同款物理块剥离（99-103 行 _strip_card）；check-events.py 哈希链账本（gate_run/judge_verdict/state_transition 已知事件类型）——exit2-resolution 若纳入复核范围 = 挂 judge verdict 校验或 check-events 事件类型扩展（P2 决策实现方式，P1 只定验收行为）。

---

# requirements-review 评审记录（TAG0027-P1，追加）

## 评审计划（BDD 分组 × 权威源核对矩阵）
- BDD-1~5（Phase 1 转移表结构化 + S-1/S-2 纳入）→ 对 phases.yaml / schema（rules/*.yaml + schema/*.json）/ design v3b §6 Phase 1 / state-machine.md 回退表 / check-structure-consistency.py 现状
- BDD-6~13（Phase 2 推进侧 CLI）→ 对 check-gate.py 头注释 exit 语义 / state-machine.md 转移（74-78/132-133/139/148）/ retreat-to / loop-orchestration.md 档位定义
- BDD-14~17（Phase 3 编排心智文档化）→ 对 dispatch-protocol.md 五模式（511-519）/ WORKFLOW.md 豁免表（141-148）/ P0-brief out-of-scope
- BDD-18~21/25（Phase 4 渲染层+注入自动化）→ 对 check-p6-provenance.py 审计 2 现状（~318-355）/ A1 联动 / 两路并存
- BDD-22/24（护栏 1 结构性判据 + 豁免清单）→ 对 check-protocol-consistency.py 分区现状 / 豁免清单自洽性（BDD-16/17）
- 隐含需求 I-1~I-17 五维度覆盖 / 审声明（risk_level/phases/packages/domains vs 改动面）/ P1 纯净性 / 裁剪合理性（不裁 P2-P8）/ 同类扫描 D-1~D-7 完整性

### requirements-review: P1-requirements.md 全读 ✅（307 行）
- frontmatter: risk_level=high / phases=[P1,P2,P3,P4,P5,P6,P6.5,P7,P8] / packages=[agate-protocol] / domains=[backend,cli,api] / agent=analyst / status=draft / trace_id=TAG0027-P1-20260902
- 25 条 BDD 编号连续 `#### BDD-NN:`（BDD-1~25）；Phase 1: 1-5 / Phase 2: 6-13 / Phase 3: 14-17 / Phase 4: 18-23 / 回归拦截: 24-25
- 隐含需求 I-1~I-17（表格式，含"为什么必须"）；同类扫描 D-1~D-7 逐条判定 + 回归拦截结论；[NO_NEED_CONFIRM]；裁剪说明（不裁 P2-P8）；capability_requirements: []；下游影响注记
- 待核对疑点初记：BDD-1 说"9 个主线阶段条目"（P0-P8 是否 9 个？）；BDD-15 禁词含 "workflow/ralph/goal/task" 是否与平台语义冲突；D-2 中 adr.md 判"docs/reviews 属 NARRATIVE 区豁免"但 BDD-17 说排查覆盖 9 文件含 adr.md——需对 WORKFLOW.md:141-148 豁免表与 check-protocol-consistency 分区现状核对；BDD-2/3/9 与 state-machine.md 74-78/132-133/139/148 语义核对；BDD-19/21/25 手工兜底路径与 pre-commit 2p 现状核对

### requirements-review: P0-brief.md ✅（92 行全读）
- scope 四 phase + 护栏 1 + 测试；out-of-scope 4 条：P6.5 judge 机制本身不动 / 五模式本体不重构 / 平台食谱不产品化（渲染层只输出平台无关派发指令）/ 不新开独立一致性检查
- known_risks 7 条与 dispatch-context 复核线索一致：核心 gate 消费方不改返回约定 / 档位 C 对接 / 转移表防漂移（state-machine 唯一权威）/ P6.5 非独立 / exit 2 模型残留（诚实边界）/ 审计 2 静态锚点失效（A1 + 文件版兜底两路）/ render-dispatch-prompt 消费方先确认现状
- env_constraints：SELF-GATE 触发面（scripts/* + rules/*.yaml + loop-orchestration.md + dispatch-protocol.md）

### requirements-review: state-machine.md 关键节核对 ✅（60-169 行）
- :74-78 P6.5 挂载 P6→P7 强门槛子阶段、非独立 phase 值（.state.yaml phase 保持 P6 直至 P7）；推进判定 = check-gate P6.5 = judge-verdict + check-events 双 exit 0；judge 轮次 ≤2 由账本承载 → BDD-2 口径一致
- :132-133 P5 failed>0&&retry<MAX → P4 (retry+1) → BDD-3/7 P5 retreat→P4 一致
- :139 P6 check-gate exit 2（FAIL=0/证据非空）AND check-p6-provenance exit 0 → P6.5 → BDD-9 一致
- :148 P6 BDD FAIL && retry<MAX → P4 (retry+1) → BDD-3/7 P6 retreat→P4 一致
- :151-157 P6.5 verdict exit 0 → P7；needs-revision/rejected → P6 重验（judge 轮次 +1）→ BDD-3 P6.5→P6 一致

### requirements-review: 权威源逐组核对（组 1-5）
**组 1（BDD-1~5）**: phases.yaml 实读 = 10 条目（主线 9：P0-P8 + P6.5 子阶段条目），schema additionalProperties:false 会拦新键（BDD-1 Given 成立）；S-1/S-2 md 侧锚点 = WORKFLOW.md 总览表 S1S2-ANCHOR（287-304 行附近）确认（BDD-4/5）；state-machine:74-78 P6.5 非独立口径 ↔ BDD-2 一致；:132-133/:148 P5/P6→P4、:156-157 P6.5→P6 ↔ BDD-3 一致
**组 2（BDD-6~13）**: check-gate.py 头注释 exit 0/1/2 + OLD_PHASE 回退抵达语义确认（BDD-6/7/8/13）；check-state-transition 由 state-transitions.md RM-AG0042（单步 retry+1 + diff≥2 强制 PAUSED + retreat-to 逐阶）支撑；P6 exit 2 → P6.5 = state-machine:139 + check-p6-provenance exit 0 ↔ BDD-9 一致；BDD-11 档位 C 语义 = loop-orchestration.md 46-61（硬中断 PAUSED 非 retry）确认
**组 3（BDD-14~17）**: 五模式唯一锚点 = dispatch-protocol 511-519（design v3b 4.1 确认）；WORKFLOW.md「已知适用环境」表 = 141-148 行确认
**组 4（BDD-18~21/25）**: 审计 2 = check-p6-provenance.py 318-355（AGATE_CARD_START/END 物理块剥离 + frontmatter 首块排除 + PASS/FAIL 预判计数）；pre-commit-gate.py 2p（425-447 sha256 卡片 hash + 462-472 dispatch-context 强制）确认两路并存约束（BDD-19/21/25）
**组 5（BDD-22/24）**: check-protocol-consistency.py 分区 = PROTOCOL_FILES（11 文件）/PROTOCOL_DIRS（assets/ phase-cards/ rules/）/NARRATIVE_DIRS（docs/design-notes 等）——护栏 1 新 CHECK 若扫协议面，覆盖 assets/ 子树

### requirements-review: 评审发现（实质问题候选，需写入 P1-review）
- F1: BDD-15 禁词含 "task"，但 rules/dispatch.yaml:19 iron_law-1 现有 "用 task 工具派发"（数据面既有命中，语义核心）未在 D-2/BDD 处置；task 是协议通用派发语义词，BDD-15 只给 workflow 留协议语义词口子
- F2: 存量清零面（BDD-17 = 顶层 9 个 agate/*.md）< 机械扫描面（PROTOCOL_DIRS 含 agate/assets/）——architect.md:229 / assets/templates/custom-role.md:49,54 / assets/templates/dsh/SKILL.md 含平台名无实现注记且未列 BDD-16 豁免 → 新 CHECK 上线即红；I-9 存量面不全
- F3: BDD-16 豁免清单（platform-notes/SETUP/WORKFLOW 141-148 表）与 D-2 判定不同步——D-2 将 WORKFLOW:5/:150-153/:166-168、AGENTS.md:30、adr.md、dispatch-protocol:1108、loop-orchestration:202 判豁免/元信息/叙事，但结构判据豁免面仅 3 整类；adr.md 理由误述（agate/adr.md 不在 PROTOCOL_FILES 也不在 NARRATIVE_DIRS，非"docs/reviews NARRATIVE 豁免"）
- F4: BDD-10 Given "从 P7 按转移表回退到 P4" 无 state-machine 失败边支撑（P7 无失败回退边）；真实跨阶边 = P6→P4（state-machine:148）
- F5: BDD-1 Then "全部 9 个主线阶段均含 next/retreat" 与括号"P8 无 next 例外"内部判据歧义（P6 验收无法二值判定）

### requirements-review: 产出 P1-review.md ✅ + 自检通过
- 25 条 BDD 逐条 PASS（含覆盖维度标注）；隐含需求 I-1~I-17 五维度覆盖表；裁剪评审（不裁 P2-P8 理由充分）；审声明（git status 实证：改动 = .state.yaml/active-tasks.md/4 P1 文件，域 backend/cli/api，risk_level=high 匹配）；范围锁定守（P6.5 机制不动/五模式本体不重构/平台食谱不产品化/不新开一致性检查/不改 check-gate/check-state-transition 返回约定）
- 4 条边界观察（非阻断，P2/P3 设计面消化）：①BDD-10 示例 P7→P4 无边、真实为 P6→P4；②BDD-15 禁词 task vs dispatch.yaml:19 iron_law-1 既有命中；③BDD-17 排查面(9 顶层 md) < 机械扫描面(PROTOCOL_DIRS 含 assets/，custom-role/architect/SKILL 含平台名无标记)；④D-2 adr.md 豁免理由误述（adr.md 不在 PROTOCOL_FILES/NARRATIVE_DIRS）
- frontmatter 自检：check-frontmatter.py exit 0；status=approved / agent=requirements-review / phases 全量 / risk_level=high；文件 195 行
