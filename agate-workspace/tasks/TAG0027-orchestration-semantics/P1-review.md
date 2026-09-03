---
phase: P1
task_id: TAG0027
type: review
parent: P1-requirements.md
trace_id: TAG0027-P1-review-20260902
created: '2026-09-02'
agent: requirements-review
risk_level: high
phases:
- P1
- P2
- P3
- P4
- P5
- P6
- P6.5
- P7
- P8
packages:
- agate-protocol
domains:
- backend
- cli
- api
status: approved
---
# TAG0027 P1 需求基线评审（requirements-review）

> 评审对象：`P1-requirements.md`（307 行，25 BDD / I-1~I-17 / D-1~D-7 / [NO_NEED_CONFIRM]）
> 评审依据：design-orchestration-semantics.md v3b（三轮评审闭环 PASS）+ state-machine.md
> + state-transitions.md + check-gate.py 头注释 + check-p6-provenance.py 审计 2（318-355）
> + check-protocol-consistency.py 分区 + pre-commit-gate.py 2p + phases.yaml/schema + WORKFLOW.md
> + loop-orchestration.md + rules/dispatch.yaml + P0-brief scope/out-of-scope
> 评审日期：2026-09-02

## 评审范围与方法

25 条 BDD 分 5 组逐条核对权威源（phases.yaml/schema/S-1-S-2 → check-gate exit 语义/
state-machine 转移/retreat-to → dispatch-protocol 五模式/WORKFLOW 豁免表 →
check-p6-provenance 审计 2 现状 → check-protocol-consistency 结构性判据）。每条给出
二值判定 + 覆盖维度（数据/前端/多端/边界/兼容）。本任务 domains=[backend,cli,api]，
无 frontend/UI/UX/vision 维度（评审要点不适用，已核对 capability_requirements: []）。

## BDD 评审（25/25）

### Phase 1（BDD-1~5）— 对照 phases.yaml / schema / S-1-S-2 / state-machine

- BDD-1: **PASS**（数据✓ 边界✓）。Given（phases.yaml 主线 9 个 P0-P8 条目 + schema
  additionalProperties:false 现状会拦新键）实证成立（schema 实读：item additionalProperties:
  false；phases.yaml 10 条目 = 9 主线 + P6.5 子阶段条目）；行为视角（schema 校验 exit 0 +
  键存在性），不绑函数。
- BDD-2: **PASS**（数据✓ 兼容✓）。与 state-machine.md:74-78 口径一致（P6.5 挂载 P6→P7、
  .state.yaml phase 保持 P6 至 P7、judge 轮次 ≤2 由账本承载）；"不出现 next: P7 主线转移"
  二值可判。
- BDD-3: **PASS**（数据✓ 边界✓）。retreat 值域对照 state-machine.md:132-133（P5→P4）/
  :148（P6→P4）/:156-157（P6.5 needs-revision→P6）+ state-transitions.md 回退表（单步
  retry+1 / |n-m|≥2 强制 PAUSED）一致；"diff≥2 表达为强制 PAUSED"二值可判。
- BDD-4: **PASS**（数据✓ 兼容✓ 多端✓）。S-1/S-2 md 侧锚点 = WORKFLOW.md 阶段总览表
  （S1S2-ANCHOR 注释实证）——纳入不新开一致性检查，守住 out-of-scope。
- BDD-5: **PASS**（兼容✓ 数据✓）。behavior：consistency exit 0 + 全量 pytest exit 0，
  不破坏 S-3/S-4/M3 既有读取；合理（P2 定 schema 形态，BDD 只要求不破坏）。

### Phase 2（BDD-6~13）— 对照 check-gate exit 语义 / state-machine 转移 / retreat-to

- BDD-6: **PASS**（边界✓ 多端✓）。exit 0 直推 = check-gate.py 头注释契约；推进过
  check-state-transition 跳变校验（state-transitions.md RM-AG0042 语境）；行为视角不绑函数。
- BDD-7: **PASS**（边界✓）。exit 1 → retreat 目标 P4 + retries[P4] 记录 = state-transitions.md
  单步回退语义；"或等效走 agate-retreat-to.py 单步路径（P2 实现定）"——语义交付，可二值判。
- BDD-8: **PASS**（边界✓ 数据✓）。exit 2 暂停转主 Agent + exit2-resolution 落盘（位置格式
  P2 定）→ 行为可判（"CLI 不自行推进 phase + 产物落盘"）。
- BDD-9: **PASS**（边界✓ 兼容✓）。P6 exit 2 → P6.5 = state-machine.md:139 特例（FAIL=0/
  证据非空 + provenance exit 0 前置已含 in Given）；"不落盘 exit2-resolution 也不停等"唯一
  例外不泛化，与设计 v3b N-New4 一致。
- BDD-10: **PASS**（边界✓ 兼容✓）。已识别示例用边问题（见"边界观察"①），核心判据（advance
  回退分支走既有 retreat-to 单步逐阶、diff≥2 被 check-state-transition 拦截强制 PAUSED）
  与 state-transitions.md 多步回退自动化一致，不构成语义缺陷。
- BDD-11: **PASS**（边界✓）。档位 C 全程 agate next + 硬中断 PAUSED 非 retry =
  loop-orchestration.md 档位 C 硬中断点表 + 设计 v3b 想法 2（可观测层）；档位 A/B 不受影响
  显式声明。
- BDD-12: **PASS**（边界✓ 兼容✓）。exit2-resolution 纳入 P6.5 judge/provenance 复核，
  产物缺失或格式不合法 → judge 不通过；挂载点（judge-verdict/check-events）P2 定、不新增
  独立机制——守范围。
- BDD-13: **PASS**（兼容✓）。不改 check-gate/check-state-transition 返回约定 = P0 known_risks
  核心约束（核心 gate 消费方）；BDD 用"核对 exit 语义文档"二值判——行为视角成立。

### Phase 3（BDD-14~17）— 对照 dispatch-protocol 五模式 / WORKFLOW 豁免表

- BDD-14: **PASS**（兼容✓）。五模式唯一锚点 = dispatch-protocol.md:511-519（grep 定位），
  协议层不发明 workflow/ralph/goal 模式概念——与 design v3b 4.1 及 out-of-scope（五模式本体
  不重构，只引用）一致。
- BDD-15: **PASS**（数据✓）。数据面禁平台名（OpenCode/Claude Code/DSH/workflow/ralph/goal/
  task）二值可判；规则级既有"task 工具"实例属 P3 排查处置面（见"边界观察"②）。
- BDD-16: **PASS**（兼容✓ 数据✓）。豁免 = platform-notes.md/SETUP.md 整文件 + WORKFLOW.md
  已知适用环境表（141-148 实证）= design v3b 4.3 护栏 2 同类豁免口径。
- BDD-17: **PASS**（数据✓）。排查覆盖 9 文件 + 判定可追溯（三分类写入 P1 正文同类扫描）；
  存量清零为机械化前置（I-9）——见"边界观察"③④ 影响 BDD-22 存量就绪度。

### Phase 4（BDD-18~23）— 对照 check-p6-provenance 审计 2 / pre-commit 2p

- BDD-18: **PASS**（多端✓ 兼容✓）。单命令渲染时注入（Lazy Injection）+ 内容与
  agate-next-card.py 输出一致 → 二值可判（命令成功路径卡片完整）；消灭占位符缺失环节。
- BDD-19: **PASS**（兼容✓）。手工兜底 + 注入 exit 0 + 2p sha256 hash 校验通过——
  pre-commit-gate.py 2p（425-447）实证存在；两路并存守住 out-of-scope/P0 known_risks。
- BDD-20: **PASS**（兼容✓ 边界✓）。审计 2 排除逻辑渲染产物上生效 = check-p6-provenance.py
  318-355 剥离逻辑对象换为渲染产物 + 渲染层标记来源（排除逻辑不变 = A1 路线）。
- BDD-21: **PASS**（兼容✓）。文件版兜底（物理 AGATE_CARD_START/END 块被既有剥离逻辑排除）
  —check-p6-provenance.py 330-339 实证。
- BDD-22: **PASS**（兼容✓ 边界✓ 数据✓）。结构性判据（非文件名单）+ 豁免整文件/整表 =
  check-protocol-consistency 分区 + design v3b 4.3 想法 4；插入平台名 → ERROR exit 1 →
  补标记 exit 0，二值可判。（存量就绪前置见"边界观察"③④）
- BDD-23: **PASS**（兼容✓）。render-dispatch-prompt 无 repo 内脚本消费方（D-3 实证）→
  CLI 契约不破坏或改动时写 P2 设计 + 测试——裁剪合理。

### 回归拦截（BDD-24~25）

- BDD-24: **PASS**（兼容✓ 边界✓）。结构性判据不依赖文件名单 → 新增权威文档自动覆盖
  （design v3b 4.3"新增任何权威文档自动被覆盖"）；同类问题机械拦截成立。
- BDD-25: **PASS**（多端✓ 兼容✓）。两路 dispatch-context 均满足 pre-commit 强制存在 +
  hash 校验 + provenance 冻结——pre-commit-gate.py 2p + 2n 实证支撑，两路无 gate 差异。

**BDD 结构检查**：编号连续（BDD-1~25，grep 25 条 `#### BDD-NN:` 无跳号）；每条单一
Given-When-Then；无"部分通过/调整"等中间态；行为视角不绑定实现函数名（P2 实现决策面
明确标注"P2 设计定"）。

## 边界观察（非阻断建议，随 BDD-10/15/22 落 P2/P3 设计面）

① BDD-10 Given"从 P7 按转移表回退到 P4"——state-machine.md 无 P7 失败回退边（P7 无
   failed→ 边），真实多阶示例是 P6→P4（state-machine:148 + state-transitions.md 多步回退
   例）。建议 P2/P6 验证时用 P6→P4 作跨阶样例，BDD-10 判据本身（逐阶 + diff≥2 拦截）不受影响。
② BDD-15 禁词含 "task"，但 rules/dispatch.yaml:19 iron_law-1 明文"用 task 工具派发"（数据面
   既有命中，task 是派发协议通用词）。BDD-15 仅给 workflow 留"协议语义词"口子，未覆盖 task
   在既有数据面的处置——建议 P3 排查把 iron_law-1 的 task 归入处置面（改词/判定不构成平台
   工具指代），否则按字面"命中数=0"含注释与既有内容不可达成。
③ BDD-17 存量排查面 = 顶层 9 个 agate/*.md，但护栏 1 机械扫描面（PROTOCOL_DIRS）含
   agate/assets/（execution-roles/、templates/）——assets/templates/custom-role.md:49,54 +
   assets/execution-roles/architect.md:229 含 OpenCode 平台名且无「实现注记」标记，不在
   BDD-17 排查清单、也不在 BDD-16 豁免清单 → 若机械 CHECK 扫 assets/ 则上线即红。
   I-9"存量清零"的存量面定义偏窄。建议：BDD-17 排查范围扩至 assets/ 平台名命中
   （或 BDD-22 Given 明确新 CHECK 扫描面限定为 BDD-17 已清存量面）——P2/P3 定，P6 按行为验证。
④ D-2 将 adr.md 判豁免理由是"docs/reviews 属 NARRATIVE 区本就豁免 CI 扫描"——但 agate/adr.md
   是 PROTOCOL_FILES 未列文件（不在 11 文件集合），且不在 NARRATIVE_DIRS（docs/reviews 指
   仓库 docs/reviews/ 目录，非 agate/adr.md）；adr.md 平台名命中属 ADR-008 决策记录叙事，
   豁免结论可成立但理由误述，且该命中不在 BDD-17 的 9 文件处置结论内（9 文件含 adr.md 但
   处置判"豁免"）。同理 D-2 对 WORKFLOW.md:5/:150-153/:166-168、AGENTS.md:30、
   loop-orchestration.md:202、dispatch-protocol.md:1108 的豁免/元信息判定均属叙述文档处置面
   而非 BDD-16 结构豁免清单——建议同类扫描结论与 BDD-16 豁免口径显式对齐（哪些是"结构豁免
   整类"，哪些是"逐段判定后挂标记"，避免 P6 验证二值性模糊）。

## 隐含需求覆盖（I-1~I-17 五维度）

| 维度 | 覆盖条目 | 判定 |
|------|---------|------|
| 数据维度 | I-1（schema 拦新键）/ I-2（结构兼容）/ I-4（S-1/S-2 md 锚点）/ I-10（dispatch-context 结构）/ I-17（三分类）| 覆盖✓ |
| 边界维度 | I-3（P6.5 非独立值域）/ I-5（exit 三态分支冲突）/ I-6（retry 同步）/ I-8（档位 C 行为变更）/ I-9（存量清零前置）| 覆盖✓（I-9 存量面偏窄见边界观察③）|
| 多端维度 | I-7（advance↔retreat-to 对接）/ I-12（2p hash 同步演进）/ I-13（judge/events 消费面扩展）| 覆盖✓ |
| 兼容维度 | I-11（审计 2 两路并存）/ I-14（命名防混淆）/ I-15（SELF-GATE）/ I-16（双工作区纪律）| 覆盖✓ |
| 前端维度 | 不适用（domains=[backend,cli,api]）| N/A ✓ |

隐含需求跨条一致性：I-3 ↔ BDD-2/3（P6.5 非独立）、I-5 ↔ BDD-8/9（exit 2 分支不直推）、
I-7 ↔ BDD-10、I-8 ↔ BDD-11、I-9 ↔ BDD-16/17/22、I-11 ↔ BDD-19/20/21/25 均无矛盾。

## 裁剪评审

- 不裁剪 P2-P8（frontmatter phases 全量 P1-P8 含 P6.5）。理由充分：改 agate 协议本体
  （rules/*.yaml + scripts/* + 协议 md），每阶段独立评审与验证是"gate 脚本改造后协议仍
  自洽"的客观确认——与 P1 卡片「P1 不可裁剪」一致。无 ceremony 声明 → standard（fail-closed）。
- risk_level=high 匹配：核心 gate 消费方脚本 + 编排路径行为变更（P2/P4 评审强度 high 档）。

## 审声明（risk_level / ceremony / phases / packages / domains vs diff 证据）

- **diff 证据（commit 前，git status 实测）**：改动 = .state.yaml（M，phase=P1 + judge.enabled:
  true）+ active-tasks.md（M，TAG0027 状态行）+ P1-requirements.md / P1-progress.md /
  P1-dispatch-context-analyst.md / P1-dispatch-context-requirements-review.md（未跟踪新增）。
  全部在 agate-workspace/tasks/TAG0027-*/，域 = 协议改造任务数据（backend/cli/api），无
  frontend 文件。
- risk_level=high **匹配**（改协议本体 + gate 消费方，P0 known_risks 7 条高风险面）。
- phases=[P1..P8+P6.5] 全量 **匹配**（无裁剪声明 + 范围四 phase 全量纳入）。
- packages=[agate-protocol] **匹配**（唯一改造对象 = worktree agate/ + agate/tests/）。
- domains=[backend,cli,api] **匹配**（backend=脚本改造、cli=新 CLI、api=phases.yaml 数据面
  schema；无 frontend/mcp/security 面；能力声明空 capability_requirements: [] 与无视觉依赖
  匹配）。ceremony 未声明 → standard，不涉 full→P7 核对。
- P1 纯净性：正文无掺方案/实现细节（exit2-resolution 格式、S-1/S-2 锚点形态、schema 形态均
  标注 P2 设计决策面）；设计诚实边界（exit 2 不假装消灭模型自判）显式声明。
- 同类扫描 D-1~D-7 逐条有判定（本次处理/不处理+理由）+ 回归拦截结论（BDD-22/24/25）——
  完整。P0-brief 时效性已核对无漂移（显式写一行）。[NO_NEED_CONFIRM] 无阻塞待确认。

## 结论

需求基线 25 条 BDD 全部可二值判定、编号连续、行为视角、范围锁定守住（P6.5 judge 机制不
动/五模式本体不重构/平台食谱不产品化/不新开独立一致性检查/不改 check-gate 与
check-state-transition 返回约定）。隐含需求五维度覆盖齐全（前端 N/A）。审声明与实际改动面
匹配。4 条边界观察（BDD-10 示例边、BDD-15 task 既有命中、BDD-17 vs 扫描面缺口、D-2 豁免
理由误述）均属 P2/P3 设计面或 BDD-22 Given 的存量就绪度澄清，不构成 BDD 语义矛盾或不可判
定；建议 analyst 在下游 P2/P3 dispatch-context 显式记录，无需回改 P1 基线语义。
