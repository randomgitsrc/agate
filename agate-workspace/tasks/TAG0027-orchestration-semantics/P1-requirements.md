---
phase: P1
task_id: TAG0027
type: problems
parent: P0-brief.md
trace_id: TAG0027-P1-20260902
status: draft
created: 2026-09-02
agent: analyst
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
---

# TAG0027 需求基线 — 编排语义统一落地（RM-AG0054）

> 本文件是 P1 阶段需求基线（活基线，后续 [SCOPE+] 会增补）。BDD 全部源自设计文档
> `docs/design-notes/design-orchestration-semantics.md` v3b（2026-09-02 三轮评审闭环）§4/§5/§6
> 与评审链（v2/v3 评审文档）采纳语义。BDD 编号连续、Given/When/Then 二值判定、行为视角
> （CLI exit code / 文件存在性 / 渲染产物内容 / 扫描命中数 / schema 校验结果），不绑定实现函数。

已核对 P0-brief 时效性，无漂移（任务 2026-09-02 立项即启动；P0-brief 目标方案/平台前提/
known_risks 与 worktree 当前现状逐一实核一致：phases.yaml 无 next/retreat 字段、scripts/ 无
`agate next`/`agate advance` 同名脚本、审计 2 仍依赖物理占位符块、全协议 0 处「实现注记」
标记——P0 描述全部成立，无需更新任何字段）。

## 需求复述

在 agate 协议层落地编排语义统一设计（RM-AG0054），全量四 phase、不分后续任务：

- **Phase 1（转移表结构化）**：`agate/rules/phases.yaml` 新增 `next`/`retreat` 字段，对齐
  `agate/state-machine.md` 既有转移语义（主线 P{n}→P{n+1}、P5/P6 gate 失败→P4、P6.5
  needs-revision→P6、回退 diff≥2→强制 PAUSED、P6 exit 2→P6.5 前进特例）；新增字段纳入既有
  S-1/S-2 双向一致性 gate（`check-structure-consistency.py`，md 侧锚点 = WORKFLOW.md 阶段总览
  表）与 JSON Schema（`rules/schema/phases.schema.json`），不新开独立一致性检查；P6.5 不得
  被写成独立转移边（挂载于 P6→P7 转移上的强门槛子阶段）。
- **Phase 2（推进侧 CLI）**：新增 `agate next` / `agate advance`，消费 `check-state-transition.py`
  跳变校验（exit 0/1）+ `check-gate.py` exit 三态（0 直推下一 phase / 1 按转移表回退 retry+1 /
  2 暂停转主 Agent 并落盘机器可读 `exit2-resolution` 产物）；与既有 `agate-retreat-to.py` /
  `agate-retreat-state.py` 回退侧对接；`agate/loop-orchestration.md` 档位 C 自动推进改走
  `agate next`（CLI = 档位 C 的可观测层，复用"硬中断点必停 PAUSED 而非 retry"语义）；不改
  既有脚本返回约定（check-gate.py exit 0/1/2、check-state-transition.py exit 0/1 保持原样）。
- **Phase 3（编排心智统一文档化）**：dispatch-protocol 五模式（dispatch-protocol.md:511-519）
  为唯一语义锚点；平台差异（DSH workflow/ralph/goal 及 OpenCode/Claude Code 平台名）在
  markdown 叙述文档仅限带「实现注记」标记（统一格式 `> 实现注记：` 标记行）的小节/段落出现；
  数据面（`rules/*.yaml`）禁平台名；排查既有协议文档语义小节平台名污染并清理/挂注记
  （豁免：`platform-notes.md` / `SETUP.md` / WORKFLOW.md「已知适用环境」表 = 平台适配权威源
  元信息）。
- **Phase 4（渲染层 + 注入自动化，方案 A 渲染时注入）**：派发 = 单命令自动注入渲染
  （`agate dispatch P{phase} {role}`），主 Agent 不再直接调用 `agate-inject-card.py`；
  dispatch-context 渲染时动态拼装 phase-card（Lazy Injection），消灭"占位符缺失→注入失败→
  手动修"环节；`check-p6-provenance.py` 审计 2 联动走 A1 路线——扫描对象从"静态文件物理卡片
  块"改为"渲染产物"（卡片块在渲染层标记来源，排除逻辑不变）；`agate-card-inject.py` /
  `agate-inject-card.py` 保留纯手工写上下文场景兜底；`agate-render-dispatch-prompt.py` 现有
  消费方确认现状后改。
- **护栏 1 机械化**：`check-protocol-consistency.py` 增加"markdown 段落含平台名但无「实现
  注记」标记"扫描（结构性判据，非文件名单）进 CI 硬校验。
- **测试**：`agate/tests/` 新增 pytest 覆盖（转移表 schema 校验、CLI 推进/回退/exit 2 分支、
  S-1/S-2 扩展、档位 C 对接、渲染时注入、审计 2 渲染产物联动），BDD 以本文件为准。

### 设计诚实边界（本任务不自欺部分）

exit 2 分支的"暂停转主 Agent"**不假装消灭模型自判**——CLI 在 exit 2 分支暂停转主 Agent 是
设计意图而非缺陷（文档明确标注）；转移表为 exit 2 定义"下一动作"字段并落盘机器可读
`exit2-resolution` 产物（记录"何时 / 依据什么客观证据 / 由谁解决"），纳入 P6.5 judge 或
provenance 审计复核范围，让"必须信任模型的区间"事后可核查。

## 隐含需求识别

| # | 隐含需求 | 为什么必须 | 关联阶段 |
|---|---------|-----------|---------|
| I-1 | phases.yaml 的 next/retreat 字段必须过 JSON Schema（`additionalProperties: false` 现状会拦新键）与 S-5 schema 校验 | 不加 schema 声明 = S-5 直接 ERROR，全量 pytest 红 | Phase 1 |
| I-2 | next/retreat 字段须与既有 task_fields/gates 数据结构兼容（不破坏 `check-structure-consistency.py` S-3/S-4 与 `agate-next-card.py` M3 渲染的现有读取） | 复用既有资产的前提是不破坏其解析 | Phase 1 |
| I-3 | P6.5 在 phases.yaml 已是独立条目但语义非独立 phase 值——next/retreat 字段值域不能把它写成转移边，schema 值域需表达"子阶段门槛"限制 | P0 out-of-scope + 设计 v3b §4.1 口径（state-machine.md:74-78） | Phase 1 |
| I-4 | S-1/S-2 的 md 侧锚点是 WORKFLOW.md 阶段总览表（不是 state-machine.md）——next/retreat 纳入 S-1/S-2 须明确 md 侧对照面如何表达新字段（总览表加列或等效锚点），否则 gate 无物可比 | 设计 v3b N-New3 闭环：防"数据面 ↔ 人类可读权威源"漂移而不新开检查 | Phase 1 |
| I-5 | `agate next` 推进决策查表时，表内"目标 phase"与"当前 gate exit code"可能冲突（如 exit 1 回退目标 = 表 retreat，exit 0 直推 = 表 next）——CLI 必须消费 exit 三态做分支，不是无脑查 next | exit 2 分支不能按 next 直推（多数阶段暂停转主 Agent；P6 例外直通 P6.5） | Phase 2 |
| I-6 | 回退时 retry 计数必须与既有机械校验一致（单步回退须同步写 retries，diff≥2 强制 PAUSED 由 check-state-transition.py 拦截）——CLI 不能绕过 | state-transitions.md 回退规则 + check-state-transition.py P2.3-P2.5 现状 | Phase 2 |
| I-7 | `agate advance` 与 `agate-retreat-to.py` 对接：exit 1 回退分支的"目标 phase"须与 retreat-to 的 TARGET_PHASE 一致且逐阶 = diff 1 | retreat-to 是既有单步回退自动化（每步独立 commit + gate），advance 须复用而非重造 | Phase 2 |
| I-8 | 档位 C 对接是行为变更：`loop-orchestration.md` 档位 C 现状推进点 = pre-commit hook exit 0 后"自动进入下一 phase"（227-243 行），改走 agate next 不能破坏档位 A（手动）/档位 B（半自动）与硬中断点必停语义 | 设计 v3b 缺口 3 + P0 known_risks 档位 C 对接风险 | Phase 2 |
| I-9 | 平台名结构性判据落地前须先清存量或豁免，否则机械化检查一上线即全红（worktree 现状 9 文件含平台名、0 处实现注记） | 护栏 1 机械化的前置条件（存量清零 → 新检查才有意义） | Phase 3+4 |
| I-10 | dispatch-context 是 subagent 核心信息源且 commit 前强制存在、provenance 需初始版本冻结——方案 A 渲染时注入生成的 dispatch-context 须保持既有文件结构与 frontmatter（phase/generated_by/task_id/role），不能破坏下游读取 | dispatch-context 规范（dispatch-protocol.md:306-374）+ 审计 2/审计 3 依赖其结构 | Phase 4 |
| I-11 | 审计 2 改扫渲染产物后，手工写上下文 + `agate-inject-card.py` 注入的存量用法（占位符物理块仍存在于手工文件）必须继续被排除逻辑覆盖 | 方案 A 两路并存 + P0 known_risks 审计 2 联动（排除逻辑不变） | Phase 4 |
| I-12 | pre-commit-gate.py 2p 对 dispatch-context 卡片做 sha256 hash 校验（抽取 AGATE_CARD_START/END 物理块）——渲染时注入后 2p 校验对象与排除锚点同步演进 | pre-commit-gate.py 2p/2g.1 现状（物理锚点消费方之一，同类扫描 D-4 命中） | Phase 4 |
| I-13 | check-judge-verdict.py 审计 2 同款物理块剥离（_strip_card 99-103 行）与 check-events.py 事件账本（gate_run/judge_verdict/state_transition 已知类型）——exit2-resolution 纳入 P6.5 复核范围需在其消费面扩展 | 设计 v3b 采纳想法 1（exit 2 可复核子状态）+ 约束 15（judge 复核范围含 exit2-resolution） | Phase 2 |
| I-14 | `agate next`/`advance` 新命令与既有 `agate-next-card.py`（输出当前阶段卡片）命名相邻——文档/测试须防混淆但不改名既有脚本 | 同类扫描 D-6：scripts/ 无同名命令但 agate-next-card.py 语义相邻 | Phase 2 |
| I-15 | SELF-GATE：改 `agate/scripts/*` + `agate/rules/*.yaml` + 协议 md 触发，commit message 须含 self-gate-review/self-gate-skip 标注 | env_constraints 硬约束（P0-brief） | 全程 |
| I-16 | 编排/派发类工具运行时用 `~/.agate/scripts/` 稳定版（worktree 相对路径会读到未发布协议副本）；但 check-protocol-consistency.py 必须用 worktree 自己的（否则扫到主 checkout） | 双工作区纪律（TAG0016 教训，AGENTS.md / handoff-template.md） | 全程 |
| I-17 | Phase 3 平台名排查须把命中按"语义定义（须清理/挂注记）vs 实现注记（豁免）vs 元信息（豁免）"三分类逐条判定写进 P1 正文 | 约束 11：编排心智锚点唯一性 + 机械化基线需要分类清单 | Phase 3 |

## BDD 验收条件

BDD 分组对应设计 v3b §6 落地路径 Phase 1-4 + 护栏 1 机械化。行为视角、可二值判定。

### Phase 1：转移表结构化（next/retreat 字段 + S-1/S-2 纳入）

#### BDD-1: phases.yaml 主线阶段新增 next/retreat 字段且 schema 校验通过
- Given `agate/rules/phases.yaml` 主线阶段（P0-P8，不含 P6.5 独立条目）已新增 `next` 与 `retreat` 字段，且 `agate/rules/schema/phases.schema.json` 已声明这两个字段
- When 对 `rules/phases.yaml` 运行既有 schema 校验（check-yaml-schema.py，S-5 链路）
- Then 校验 exit 0，且全部 9 个主线阶段条目均含 `next`、`retreat` 两键（P8 无 next 的例外须在 P2 设计明确值域）

#### BDD-2: P6.5 条目不被写成独立转移边
- Given `rules/phases.yaml` 的 P6.5 条目按 state-machine.md:74-78 口径建模（挂载于 P6→P7 转移的强门槛子阶段，.state.yaml phase 保持 P6 直至 P7）
- When 检查 phases.yaml 中 P6.5 条目的 next/retreat 字段建模方式
- Then P6.5 不出现指向独立后继 phase（如 `next: P7`）的主线转移语义，其表达方式与"非独立 phase 值"口径一致（P2 设计定具体 schema 形态，P6 按 BDD-2 原文验证）

#### BDD-3: 转移表 next/retreat 值域与 state-machine.md 语义一致（P5/P6→P4 回退、P6.5→P6、diff≥2→PAUSED）
- Given phases.yaml 各阶段条目按 state-machine.md 转移规则填写 next/retreat（P5、P6 的 retreat 指向 P4；P6.5 needs-revision 回退指向 P6；回退 diff≥2 语义 = 强制 PAUSED 而非表内直退）
- When 用 P2 设计的校验手段（schema 值域校验 + 既有 check-state-transition.py P2.3-P2.5）核对表中每个 retreat 目标
- Then 每个 retreat 目标与 state-machine.md 转移规则一致，且任何"跨 ≥2 阶回退"均表达为强制 PAUSED（不写成表内多步直退）

#### BDD-4: 新增 next/retreat 字段纳入既有 S-1/S-2 双向一致性 gate
- Given phases.yaml 新增 next/retreat 字段后，WORKFLOW.md 阶段总览表区域（S-1/S-2 md 侧锚点）存在对应表达（P2 设计定列/锚点形态）
- When 在 phases.yaml 与 WORKFLOW.md 总览表之间制造不一致（如改一处 retreat 值不同步）
- Then `agate/scripts/check-structure-consistency.py`（S-1 与 S-2）对不一致输出 ERROR 并 exit 1，且不引入任何新的一致性检查脚本（复用 S-1/S-2）

#### BDD-5: 转移表字段与 schema 结构兼容既有消费方
- Given phases.yaml 新增 next/retreat 字段且 schema 通过
- When 运行 `agate/scripts/check-protocol-consistency.py`（worktree 版本）与全量 pytest
- Then 两者均 exit 0（0 ERROR；既有 WARNING 口径不变），即新增字段未破坏 S-3/S-4、agate-next-card.py M3 渲染、check-structure-consistency.py 现有读取

### Phase 2：推进侧 CLI（agate next / agate advance）

#### BDD-6: agate next 在 gate exit 0 时按转移表推进到下一 phase
- Given 任务 T 当前 phase=Pn，.state.yaml 正常，`check-gate.py Pn` 跑出 exit 0
- When 运行 `agate next`（或等效 CLI）
- Then .state.yaml 的 phase 变为 Pn+1（按 phases.yaml next 字段），且本次推进经过既有 check-state-transition.py 跳变合法性校验（exit 0 通过）

#### BDD-7: agate next 在 gate exit 1 时按转移表 retreat 目标回退（retry+1）
- Given 任务 T 当前 phase=P5（或 P6），`check-gate.py P5` 跑出 exit 1（未通过）
- When 运行 `agate next`
- Then 不回退到 P4 之前的阶段：phase 按转移表 retreat 目标变为 P4 且 retries[P4] 追加一条记录（与既有单步回退机械校验一致），或等效走既有 agate-retreat-to.py 单步回退路径（P2 实现定，P6 按语义验证）

#### BDD-8: agate next 在 gate exit 2 时暂停并落盘机器可读 exit2-resolution 产物
- Given 任务 T 当前 phase=Pn（非 P6），`check-gate.py Pn` 跑出 exit 2（需主 Agent 自判）
- When 运行 `agate next`
- Then CLI 不自行推进 phase，输出暂停转主 Agent 提示，并落盘一个机器可读 `exit2-resolution` 产物（记录何时 / 依据什么客观证据 / 由谁解决，位置与格式 P2 定）

#### BDD-9: P6 的 exit 2 保持前进特例，不落盘 exit2-resolution 也不停等
- Given 任务 T 当前 phase=P6，check-p6-provenance.py exit 0，`check-gate.py P6` 跑出 exit 2（FAIL=0/证据非空）
- When 运行 `agate next`
- Then 按 state-machine.md:139 前进到 P6.5 judge 复核（phase 仍保持 P6 直至 P7 通过），不按通用 exit 2 暂停语义处理（唯一例外，不泛化到其他 phase）

#### BDD-10: agate advance 与既有回退侧 CLI 对接（exit 1 分支多阶回退走既有路径）
- Given 任务 T 需从 P6 按转移表回退到 P4（state-machine.md:148，P6 BDD FAIL → P4 retry+1；表内 retreat 值 P4，跨 2 阶的机械落地由 agate-retreat-to.py 逐阶 P6→P5→P4 处理）[BASELINE_CHANGE: P2 plan-eng-review 确认 BDD-10 原 Given "P7→P4" 示例用边不当（P7 gate 失败不回退 P4，非既有转移边），修正为 P6→P4（state-machine.md:148 的真实多阶回退例）；Given/When/Then 语义不变（多阶回退走既有 retreat-to 路径），仅修正示例 phase 用值，2026-09-02 主 Agent 显式批准]
- When 触发 agate advance 的回退分支（或等效既有 agate-retreat-to.py 调用序列）
- Then 回退按既有 agate-retreat-to.py 单步路径逐阶执行（每步独立 commit + 归档 + gate 校验，retry 记录同步），且任何 diff≥2 的人工直接回退被 check-state-transition.py 拦截为强制 PAUSED（retreat-to 逐阶自动化与人工直退不同轨）

#### BDD-11: 档位 C 全程用 agate next 推进，主 Agent 未自行判断进入下一 phase
- Given 任务 T 在档位 C（/loop 全自动）下运行
- When 检查档位 C 推进记录（loop-orchestration.md 描述的执行路径 / gate-events.jsonl 或等效可观测证据）
- Then 每一处"进入下一 phase"的推进均经 agate next（或等价 CLI）判定而非主 Agent 临场自行判断，且硬中断点仍必停为 PAUSED 而非 retry（档位 A/B 手动/半自动路径不受影响）

#### BDD-12: exit2-resolution 产物纳入 P6.5 judge / provenance 复核范围
- Given 任务 T 在运行中产生过 exit2-resolution 产物（exit 2 分支解决留痕）
- When 任务走到 P6.5 judge 复核（或 provenance 审计）
- Then 复核范围包含该 exit2-resolution 产物（可核查"exit 2 何时/依据什么证据/由谁解决"），产物缺失或格式不合法时 judge 复核不通过（挂载点：check-judge-verdict.py 或 check-events.py 消费面，P2 设计定，不新增独立机制）

#### BDD-13: 既有脚本返回约定未被改造
- Given 任务 T 任意阶段 gate 运行
- When 核对 `agate/scripts/check-gate.py` 与 `agate/scripts/check-state-transition.py` 的 exit code 语义文档/头注释
- Then check-gate.py 仍为 exit 0=通过/1=未通过/2=需主 Agent 自判，check-state-transition.py 仍为 exit 0=合法/1=非法（本任务只新增消费方，不修改这两个脚本的返回约定）

### Phase 3：编排心智统一文档化（五模式锚点 + 实现注记）

#### BDD-14: dispatch-protocol 五模式为唯一语义锚点
- Given 协议文档（dispatch-protocol.md 及引用编排语义的文档）
- When 检查编排语义的定义来源
- Then 单一语义锚点是五模式（模式 1 单发 / 2 静态拆批 / 3 并行 / 4 先理解后拆 / 5 串行链），协议层不发明以平台工具命名的"workflow 模式 / ralph 模式 / goal 模式"概念

#### BDD-15: 数据面（rules/*.yaml）不出现平台名
- Given `agate/rules/*.yaml`（含 phases.yaml 扩展后）与 `agate/rules/schema/*.json`
- When 扫描其中是否出现平台名/平台工具名（OpenCode / Claude Code / DSH / workflow / ralph / goal / task）
- Then 命中数 = 0（含注释与新增字段；workflow 若作协议语义词如"工作流"与平台工具名重名时，P3 排查确认不构成平台工具指代）

#### BDD-16: markdown 叙述文档平台名仅限带「实现注记」标记的小节/段落
- Given `agate/*.md` 协议叙述文档（豁免文件除外：platform-notes.md、SETUP.md 整文件 + WORKFLOW.md「已知适用环境」表 141-148 行）
- When 用护栏 1 扫描规则（含平台名但所在段落无 `> 实现注记：` 标记行）扫描
- Then 除豁免文件/豁免表外，命中数 = 0（Phase 3 清理存量后）

#### BDD-17: 既有协议文档平台名污染排查完成且判定可追溯
- Given Phase 3 排查覆盖 worktree agate/*.md 全部 9 个含平台名文件（adr.md / AGENTS.md / dispatch-protocol.md / loop-orchestration.md / platform-notes.md / role-system.md / SETUP.md / UPGRADING.md / WORKFLOW.md）
- When 逐文件核对平台名所在段落分类（语义定义 / 实现注记 / 元信息）
- Then 每个命中均有明确判定与处理（清理或挂实现注记或豁免），判定结论写入 P1 正文同类扫描节（见下），无遗漏未分类命中

### Phase 4：渲染层 + 注入自动化（方案 A）+ 护栏 1 机械化

#### BDD-18: agate dispatch 单命令渲染时注入，主 Agent 不再直接调用 agate-inject-card.py
- Given 主 Agent 要派发 phase=P{phase}、role={role} 的 subagent
- When 主 Agent 运行 `agate dispatch P{phase} {role}`（或等效单命令），生成 dispatch-context
- Then 生成的文件含完整的当前阶段卡片内容（渲染时动态拼装，Lazy Injection），全程无需主 Agent 手动运行 agate-inject-card.py，且无"占位符缺失→注入失败→手动修"环节（命令成功路径下文件内卡片块完整、内容与 agate-next-card.py 输出一致）

#### BDD-19: 纯手工写上下文 + 注入的存量用法保留（两路并存）
- Given 主 Agent 按存量流程手工写 dispatch-context（含 AGATE_CARD_START/END 占位符），再运行 `agate-inject-card.py P{n} TASK_DIR`
- When 执行注入
- Then 注入成功（exit 0，卡片写入占位符块）且该文件继续通过 pre-commit-gate.py 2p 的卡片 sha256 hash 校验——方案 A 落地后手工路径不被破坏

#### BDD-20: 审计 2 排除逻辑在渲染产物上仍生效（P6 dispatch-context 含卡片块不误报预判）
- Given P6 dispatch-context 采用方案 A 渲染时注入生成，文件含完整 P6 阶段卡片块（P6 卡片本身含 PASS/FAIL 模板字样），且卡片块来源在渲染层可标记（渲染产物标记来源）
- When 运行 `check-p6-provenance.py $TASK_DIR`（审计 2）
- Then 卡片块内容被排除（不因卡片模板含 PASS/FAIL 字样而误报"验收结论预判"），审计 2 exit 0（排除逻辑与文件版等效，扫描对象为渲染产物）

#### BDD-21: 手工场景的审计 2 文件版兜底仍有效
- Given P6 dispatch-context 由纯手工写上下文 + agate-inject-card.py 注入生成（文件含物理 AGATE_CARD_START/END 占位符块）
- When 运行 `check-p6-provenance.py $TASK_DIR`（审计 2）
- Then 物理卡片块被既有剥离逻辑排除（不误报预判），审计 2 exit 0——文件版兜底路径在新机制下继续工作

#### BDD-22: 护栏 1 机械化检查进 check-protocol-consistency.py 且可判定
- Given `check-protocol-consistency.py`（worktree 版本）已增加"markdown 段落含平台名但无「实现注记」标记"扫描（结构性判据：豁免整文件/整表清单 = platform-notes.md、SETUP.md、WORKFLOW.md 已知适用环境表，不维护逐段文件名单）
- When 在协议 md 中某段无「实现注记」标记处插入平台名（如 "DSH"）
- Then 扫描命中该段并报 ERROR（exit 1）；该段补 `> 实现注记：` 标记行后扫描通过（exit 0）——检查按结构性判据工作，不依赖维护文件名单

#### BDD-23: agate-render-dispatch-prompt.py 现有消费方不破坏
- Given Phase 4 改动涉及派发渲染路径
- When 核对 `agate-render-dispatch-prompt.py` 的既有用法（模板渲染到 P{N}-dispatch-prompt-{role}.md + stdout 的独立场景，无 repo 内脚本调用方——消费方为文档约定/人工/测试）
- Then 该脚本既有 CLI 契约（PHASE ROLE TASK_DIR [--rollback]，exit 0/1/2）不因方案 A 破坏；若需改动，其消费场景与兼容说明写入 P2 设计并有对应测试

### 回归拦截（同类问题未来不再新增）

#### BDD-24: 新增"语义文档平台名"有机械拦截，未来新增文档自动被覆盖
- Given 护栏 1 机械化已上线（BDD-22）
- When 未来协议新增叙述文档含平台名但无「实现注记」标记
- Then 该文档自动被一致性检查命中（结构性判据不依赖文件名单，新增任何权威文档自动覆盖）——同类问题（协议概念被平台名污染）在机械层被拦截，不需人工维护名单

#### BDD-25: 手工/自动两路派发的 dispatch-context 均满足 pre-commit 强制与 provenance 冻结
- Given 方案 A 落地后存在两种派发路径：自动（agate dispatch 渲染时注入）与手工（手写 + agate-inject-card.py 兜底）
- When 对任一 P1-P8 阶段产出 commit 运行 pre-commit hook
- Then 两条路径生成的 dispatch-context 均满足：commit 前暂存区含当前阶段 dispatch-context、卡片内容 hash 校验通过与 provenance 冻结要求（初始版本不被改写）——两路并存不产生 gate 行为差异

## 同类扫描（强制节）

按 P1 卡片「同类扫描」节对客观查证信息 D 清单逐条判定（grep 实证，2026-09-02 worktree）：

| # | 扫描对象 | 命中事实（grep 实证） | 判定 | 理由 |
|---|---------|---------------------|------|------|
| D-1 | `next` / `retreat` 字段 | `agate/rules/*.yaml` + `rules/schema/*.json` 0 命中（首增）；既有读取面 = phases.schema.json（additionalProperties:false 会拦新键）、S-1/S-2（WORKFLOW 总览表锚点 287-304 行）、agate-next-card.py `_render_sections`（读 outputs/gates/retry_cap） | **本次处理** | 首增字段必须过 schema（S-5）+ 纳入 S-1/S-2（不新开检查）+ 不破坏 agate-next-card.py 渲染读取 → BDD-1/2/3/4/5 |
| D-2 | 平台名污染（Phase 3 清理面 + 机械化扫描基线） | worktree `agate/*.md` 命中 9 文件：adr.md(2) / AGENTS.md(1) / dispatch-protocol.md(1) / loop-orchestration.md(1) / platform-notes.md(16) / role-system.md(3) / SETUP.md(21) / UPGRADING.md(8) / WORKFLOW.md(5)；全协议 0 处「实现注记」标记 | **本次处理（Phase 3 逐文件判定）+ 部分豁免** | 逐文件三分类：①**语义定义面须清理/挂注记**：role-system.md（138/141/146 行 OpenCode 自定义角色语义段）、UPGRADING.md（DSH 平台支持版本条目属升级说明，按实现注记/元信息处理）；②**元信息/适配权威源豁免**：platform-notes.md 整文件、SETUP.md 整文件、WORKFLOW.md「已知适用环境」表 141-148 行 + 150-153 行 Claude Project 会话定位段、WORKFLOW.md:5/168 行（声明适用平台的文档元信息）、agate/AGENTS.md:30（入口表"平台适配→platform-notes.md"指针，元信息）、adr.md（ADR-008 决策记录含平台名属叙事/实现注记豁免——docs/reviews 属 NARRATIVE 区本就豁免 CI 扫描）、dispatch-protocol.md:1108（OpenCode 坑位 = 平台适配实现注记）、loop-orchestration.md:202（档位 C 前提 = 平台适配实现注记）；③**待 P3 复核判定**：dispatch-protocol.md:166 单 Agent 模式表（平台名未直接出现但语义依赖平台，P3 排查确认）→ BDD-16/17 |
| D-3 | `agate-inject-card.py` / `agate-card-inject.py` / `agate-render-dispatch-prompt.py` 消费方 | inject-card 运行时消费方 = orchestrator-template.md:60 + dispatch-protocol.md:358（主 Agent 派发唯一合法注入路径）+ pre-commit 2p hash 校验间接依赖；card-inject 仅被 inject-card 调用；render-dispatch-prompt **无 repo 内脚本调用方**（仅模板/文档/scripts README/测试引用） | **本次处理（Phase 4：方案 A 新主路径 + 保留兜底）** | 方案 A 两路并存（BDD-18/19/25）；render-dispatch-prompt 消费方为空 → 改动风险低但须过既有单测（BDD-23） |
| D-4 | `AGATE_CARD_START` 物理占位符锚点消费方 | 全仓 591 处命中（含存量任务 dispatch-context 数百文件）；运行时消费方 = agate-card-inject.py（注入）、pre-commit-gate.py 2p/2g.1（hash 校验 + PROD_TOUCHED 剥离）、check-p6-provenance.py 审计 2、check-judge-verdict.py 审计 2 同款、check-retrospective.py、check-scope-resolved.py；模板 = dispatch-context.md + dispatch-protocol.md | **本次处理（A1 联动对象）+ 存量不处理** | 存量任务 dispatch-context（含 TAG0002-TAG0025 等历史文件）**本次不迁移**——方案 A 只改新派发路径，手工兜底保留物理锚点，存量文件继续被文件版逻辑覆盖（BDD-19/21）；运行时消费方中审计 2 改扫渲染产物（BDD-20），pre-commit 2p 与手工路径保留 |
| D-5 | `exit2-resolution` | 全仓仅设计文档/HANDOFF/P0-brief/dispatch-context 引用 → **无既有机制（首增）** | **本次处理** | 新机制，纳入 P6.5 judge / provenance 复核范围（BDD-8/12） |
| D-6 | `agate next` / `agate advance` 命名冲突 | `agate/scripts/` 无同名脚本；`agate-next-card.py`（输出当前阶段卡片全文）命名相邻；active-tasks.md 已把 "agate next/advance" 写入任务描述 | **本次处理（防混淆，不改既有脚本名）** | 既有 agate-next-card.py 语义不同（卡片输出 vs 推进），不构成冲突但文档/CLI 帮助须区分（BDD-6-13 隐含） |
| D-7 | judge / P6.5 复核范围扩展挂载点 | check-judge-verdict.py `_strip_card`（99-103 行审计 2 同款物理块剥离）；check-events.py 事件账本（已知类型 gate_run/judge_verdict/state_transition，哈希链 + ts 单调 + judge_verdict 计数 ≤2） | **本次处理（exit2-resolution 纳入复核范围的挂载面）** | 设计 v3b 采纳想法 1 + 约束 15——P2 定挂载实现（judge verdict 校验或 events 类型扩展），P1 只定验收行为（BDD-12） |

**回归拦截结论**：同类问题中"协议概念被平台名污染"与"语义文档新增平台名"未来仍会新增（非一次性存量），
拦截手段 = 护栏 1 机械化结构性判据扫描进 CI（BDD-22/24），不依赖维护文件名单；
"手工/自动派发路径并存"未来持续存在，拦截手段 = pre-commit 强制 + hash 校验两路等价（BDD-25）。
其余同类项（next/retreat 首增、agate next 命名、exit2-resolution 首增）为一次性，无未来新增面。

## 待确认清单

[NO_NEED_CONFIRM]
- 无阻塞性待确认项。设计 v3b 经三轮独立评审闭环 PASS（v3 复审 4 NIT 全部修复为 v3b），本任务范围与
  语义有明确锁定（P0-brief scope/out-of-scope + 设计 §4/§5/§6）；分析中所有需要实现层抉择的点
  （next/retreat schema 形态、exit2-resolution 落盘格式与位置、审计 2 渲染产物标记方式、S-1/S-2 md
  侧扩展表达）均属 P2 设计决策面（Given/When/Then 已按行为视角给出，不阻塞 P1 推进）。

## 裁剪说明

- 本任务走完整 P2-P8，不裁剪任何阶段（frontmatter `phases` 已声明）。理由：TAG0027 改 agate 协议
  本体（rules/*.yaml + scripts/* + 协议 md），每阶段产出均须独立评审（P2/P4 review）与验证
  （P5/P6/P6.5 judge/P7/P8）——协议自身改造是最高自举风险场景，裁剪任一验证阶段即失去对
  "gate 脚本改造后协议仍自洽"的客观确认。
- 无 ceremony 声明 → 按 standard（fail-closed）处理，不薄化仪式。

## 范围声明

- `packages: [agate-protocol]`（本任务唯一改造对象 = worktree 的 `agate/` 协议本体 + 其测试
  `agate/tests/`；docs/design-notes + docs/reviews 为输入不产出）。
- `domains: [backend, cli, api]`：
  - backend = gate/编排脚本改造（check-*-consistency / 新 CLI / inject 渲染层）
  - cli = `agate next`/`agate advance`/`agate dispatch` 新命令行界面
  - api = phases.yaml 数据面 schema（next/retreat 字段机器接口）——本任务不涉及 frontend /
    mcp / security / UI 视觉维度，无 frontmatter 渲染形态/UX 维度声明。
- `risk_level: high`：改协议本体 + 核心 gate 消费方脚本 + 编排路径行为变更，P2/P4 评审强度走
  high 档（P4 需独立 review subagent）。

## 能力需求声明

```yaml
capability_requirements: []
```

- 本任务全部产出为协议 md + Python 脚本 + YAML/JSON schema + pytest，均在当前环境可验证
  （系统 python3 + pyyaml 6.0.1 + pytest 9.0.3，见 P0-brief 测试基线），无浏览器/外部系统/
  视觉/网络依赖；无 `requires_minimal_validation` 场景（不依赖浏览器行为/安全模型/外部系统行为）。
- 能力判断树：无 agent 侧能力缺口（不涉视觉/工具盲区），无运行环境缺口（无需起服务/装依赖）——
  不走 verification_env 声明。

## 下游影响注记（供 P2 使用，非需求正文）

- P2 设计须产出：next/retreat 字段 schema 形态（含 P6.5 非独立表达）、S-1/S-2 md 侧扩展方式、
  exit2-resolution 落盘格式与位置、审计 2 渲染产物标记方式（来源标记）、agate next/advance/dispatch
  CLI 契约、exit 三态分支与档位 C 对接细节。
- P6 验收逐条对照 BDD-1~25（PASS+FAIL 总数 ≥25）。
