---
phase: P2
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0027
role: architect
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

产出 `P2-design.md`：把 P1 需求基线（25 条 BDD，四 phase + 护栏 1 机械化）转化为**可实现的技术
方案**——候选方案权衡、影响面梳理（改什么/不改什么/风险在哪）、gate_commands 固化、
files_to_read 上下文地图、minimal_validation。设计对象 = worktree 的 `agate/` 协议本体。

四 phase 设计域（对应 P1 BDD 分组）：
- **Phase 1（BDD-1~5）**：`rules/phases.yaml` 增 next/retreat 字段（含 schema 形态 + P6.5
  非独立表达 + P8 无 next 例外）+ S-1/S-2 纳入（WORKFLOW.md 总览表 md 侧锚点扩展）
- **Phase 2（BDD-6~13）**：推进侧 CLI `agate next` / `agate advance`（exit 三态分支 +
  exit2-resolution 落盘 + retreat-to 对接 + 档位 C 对接）
- **Phase 3（BDD-14~17）**：dispatch-protocol 五模式唯一锚点 + 平台名污染三分类清理/挂注记
- **Phase 4（BDD-18~25）**：渲染时注入（`agate dispatch` 单命令）+ 审计 2 A1 联动 + 手工兜底
  两路并存 + 护栏 1 机械化（check-protocol-consistency.py 结构性判据扫描）

### 约束

1. **范围锁定**（P0-brief out-of-scope 硬边界）：P6.5 judge 机制本身不动 / dispatch-protocol
   五模式本体不重构 / 平台食谱不产品化 / **不新开独立一致性检查**（S-1/S-2 复用）。
   `check-gate.py`（exit 0/1/2）与 `check-state-transition.py`（exit 0/1）返回约定**不改**——
   新增 CLI 只做消费方。发现设计需越界 → 停下报告主 Agent，不擅自扩。
2. **P6.5 非独立 phase 口径**（state-machine.md:74-78）：phases.yaml 已有 P6.5 条目，next/retreat
   字段不得把它写成独立转移边（挂载于 P6→P7 转移的强门槛子阶段；.state.yaml phase 保持 P6
   直至 P7）。schema 值域须表达"子阶段门槛"限制。
3. **转移表值域唯一权威 = state-machine.md**（BDD-3）：P5/P6 gate 失败 → P4（retry+1）；
   P6.5 needs-revision → P6 重验（judge 轮次 ≤2）；回退 diff≥2 → 强制 PAUSED（check-state-transition.py
   机械拦截，表内不写跨 ≥2 阶直退）；P6 exit 2 → P6.5 前进特例（唯一 exit 2 直通，不泛化）。
4. **exit 2 三态建模**（BDD-8/9/12）：exit 2 通用语义 = 暂停转主 Agent + 落盘机器可读
   `exit2-resolution` 产物（记录何时/依据什么客观证据/由谁解决），纳入 P6.5 judge / provenance
   复核范围（挂载 check-judge-verdict.py 或 check-events.py 消费面，**不新增独立机制**）；
   P6 的 exit 2 = 前进 P6.5 特例（FAIL=0/证据非空 + provenance exit 0），**不落盘
   exit2-resolution 也不停等**。设计诚实边界：不假装消灭模型自判。
5. **方案 A 两路并存**（BDD-18/19/25）：渲染时注入（`agate dispatch` 单命令 Lazy Injection）是
   新主路径；纯手工写上下文 + `agate-inject-card.py` 注入的存量用法**必须保留**。渲染产物须
   保持 dispatch-context 既有文件结构与 frontmatter（phase/generated_by/task_id/role），不破坏
   pre-commit-gate.py 2p hash 校验、审计 2/3 读取。**存量任务 dispatch-context（591 处物理
   占位符）本次不迁移**。
6. **审计 2 A1 联动**（BDD-20/21）：check-p6-provenance.py 审计 2 扫描对象从"静态文件物理卡片
   块"改为"渲染产物"，卡片块在渲染层标记来源，**排除逻辑不变**；手工文件版兜底保留。
7. **护栏 1 结构性判据**（BDD-15/16/22/24）：`rules/*.yaml` + schema 禁平台名；markdown 叙述
   文档平台名仅限带「实现注记」标记（`> 实现注记：` 标记行）段落；豁免 = platform-notes.md /
   SETUP.md 整文件 + WORKFLOW.md「已知适用环境」表（141-148 行）整表。机械化检查 = 结构性
   判据扫描（不维护文件名单），**上线前须先清存量或豁免**（否则即全红）。
8. **P1 评审 4 条非阻断边界观察必须显式处理**（写入 P2-design.md，不留到 P3/P4 踩坑）：
   ① BDD-10 示例"从 P7 按转移表回退到 P4"用边不当——P7 gate 失败的回退目标不是 P4，示例应
   用 P6→P4（BDD-3 语义）；② BDD-15 禁词含 `task`，但 `rules/dispatch.yaml` 数据面既有
   `task_fields` 等含 task 的键——须核实禁词清单是否误伤既有数据面（机械检查若上线即对存量
   数据面报红）；③ BDD-17 排查面（9 文件）窄于机械化扫描面（未来扫全部协议 md）——P2 须定义
   存量清理/豁免的完整面；④ 同类扫描 D-2 称 adr.md 豁免因"docs/reviews 属 NARRATIVE 区"，
   但 adr.md 本体在 `agate/` 协议区——豁免理由须核实修正（ADR-008 决策记录的平台名属叙事，
   按实现注记或白名单豁免处理）。
9. **gate_commands 固化**（P3/P5/P6 后续阶段按此执行，P2 后不得改）：本任务改动 = 协议
   rules/*.yaml + schema + scripts/* + 协议 md + tests。P5 全量 pytest（串行或 --reruns 1 -n
   auto，注意存量并行偶发）+ consistency 0 ERROR（--strict-errors-only，worktree 脚本）+
   shellcheck。参考既有任务（TAG0026）gate_commands 结构，拆独立 key 不塞 && 链。
10. **P2 四字段必填**：candidate_count / packages / domains / ui_affected（本任务 ui_affected:
    false——协议层改造无 UI，但 P1 domains=[backend,cli,api] 须延续）。
11. **影响面梳理在候选方案之前**（强制节）：Modify / Not Modify / Risk 三部分齐全，落点须到
    "哪个文件的哪个小节/函数"，Not Modify 显式列出看起来该改但不改的（如 agate-next-card.py
    不改名、存量 dispatch-context 不迁移、check-gate/check-state-transition 返回约定不改、
    P6.5 judge 机制本身不动）。
12. **dispatch_plan**：本任务跨 4 个设计域 + 多脚本改动 = high 复杂度，必须设计后续阶段拆批
    方案（P3/P4 的编排模式），按 architect.md「批次设计」节产出。
13. **minimal_validation 必声明**：本任务纯 Python/YAML/md 代码逻辑（无浏览器/外部系统依赖），
    声明"纯代码逻辑，无外部系统依赖"时须写明依赖哪些内部函数/数据转换（如 check-gate exit
    语义、check-state-transition P2.3-P2.5、agate_common MAX_RETRY_MAP、check-p6-provenance
    审计 2 剥离逻辑、agate-next-card M3 渲染）。

### 上游关联

- P1-requirements.md（25 BDD + 17 隐含需求 I-1~I-17 + 同类扫描 D-1~D-7 判定，BDD 语义权威）
- P0-brief.md（范围锁定 + out-of-scope + known_risks + env_constraints）
- 设计 v3b `docs/design-notes/design-orchestration-semantics.md`（§4 采纳设计 / §5 资产衔接 /
  §6 落地路径——方案形态的来源；§4.2 平台语义等价表是「实现注记」示范）
- 评审链：P1-review.md approved + 4 条非阻断边界观察（约束 8 已转述）
- 设计评审链 v2/v3/meta（P6.5 非独立 / S-1/S-2 纳入 / 结构性判据 / WORKFLOW 豁免 / 可追溯
  版本标注——BDD 语义背后的采纳理由）

### 输入文件（按顺序读）

1. `agate-workspace/tasks/TAG0027-orchestration-semantics/P1-requirements.md`（需求基线，全读）
2. `agate-workspace/tasks/TAG0027-orchestration-semantics/P0-brief.md`
3. `docs/design-notes/design-orchestration-semantics.md`（设计 v3b，全读）
4. `agate/rules/phases.yaml` + `agate/rules/schema/phases.schema.json`（Phase 1 扩展对象）
5. `agate/state-machine.md`（转移规则权威源：74-78 / 95-99 / 132-133 / 139 / 148 / 151-157）
6. `agate/loop-orchestration.md`（档位 A/B/C + gate 处理流程 227-243）
7. `agate/dispatch-protocol.md`（五模式 511-519 + 派发机制 + dispatch-context 规范）
8. `agate/scripts/check-gate.py`（exit 三态 + OLD_PHASE 回退检测 + gate_p* 结构）
9. `agate/scripts/check-state-transition.py`（P2.3-P2.5 + MAX_RETRY_MAP 导入）
10. `agate/scripts/agate-retreat-to.py` / `agate-retreat-state.py`（回退侧对接对象）
11. `agate/scripts/check-p6-provenance.py`（审计 2 ~318-355 行，A1 联动对象）
12. `agate/scripts/check-structure-consistency.py`（S-1/S-2，行 7-11 + S1S2-ANCHOR）
13. `agate/scripts/check-protocol-consistency.py`（护栏 1 挂载点：CHECK 1-13 + 分区）
14. `agate/scripts/agate-inject-card.py` / `agate-card-inject.py` / `agate-render-dispatch-prompt.py`
    / `agate-next-card.py`（渲染/注入链现状）
15. `agate/scripts/agate_common.py`（公共函数：write_gate_result / read_state_phase /
    resolve_workspace / MAX_RETRY_MAP / run_git 等，按需）
16. `agate/WORKFLOW.md`（S-1/S-2 md 侧锚点 = 阶段总览表 287-304 行附近 + 已知适用环境表
    141-148 行）
17. `agate/assets/templates/dispatch-context.md`（渲染时注入要兼容的文件模板）
18. `AGENTS.md` + `docs/guides/worktree-dogfooding-guide.md`（双工作区纪律，按需）

> ⚠️ 协议文件（4-17 项）读 **worktree 自己的 `agate/`**（改造对象现状），不是 `~/.agate`。
> 全量 pytest / count-tests 等基线命令在 worktree 根跑；编排/派发工具用 ~/.agate 稳定版。

### 产出文件字段

用 `FILE=agate-workspace/tasks/TAG0027-orchestration-semantics/P2-design.md agate-md-field-set --list`
看字段清单再逐个 set（candidate_count/packages/domains/ui_affected 进 frontmatter；
gate_commands/files_to_read/env_constraints/minimal_validation 留正文）。不要手写 frontmatter。
</dispatch_guide>

<!-- AGATE_CARD_START -->
## 当前阶段卡片：P2

路径：phase-cards/P2-design.md
---
# P2 — 方案设计

> 当前状态：[首次 / 重试 #N / 裁剪跳阶]
> 裁剪跳阶 → P2 不可裁剪。design_trivial / follows_existing_pattern 可简化（1 个候选方案），不可省略。

## 如果是首次进入本阶段

1. 派发 architect subagent → 产出 P2-design.md
   1.1 写 P2-dispatch-context-architect.md（派发指引：目标/约束/上游关联/输入文件 + 客观查证信息）
2. 按 C8 映射表派评审（见下方）
3. 评审通过 → P2-review.md status: approved
4. 预跑 check-gate.py P2（脚本化检查）
5. git add {AGATE_WORKSPACE}/tasks/{Txxx}/（含 .state.yaml + 产出文件，若 .gitignore 忽略需 git add -f）
   ⚠️ 此时 .state.yaml 的 phase 保持 P2，不要提前写 P3——phase = 本 commit 的产出阶段
6. git commit -m "wf({Txxx}-P2): {摘要}"（phase=P2，P2 产出含 P2-design.md + P2-review.md）
7. P2 commit 完成后进入 P3：**phase 推进 P3 随 P3 产出 commit 一起**（P3-test-cases.md 就绪后），不是单独 phase commit

## 如果是重试

确认上一轮失败原因（方案选择有误 / 候选方案不足 / 评审 rejected）
→ 读 agate/rules/state-transitions.md 确认 retry 上限（P2 MAX=3）

## 前置条件

- [ ] P1-requirements.md 含 domains / risk_level / phases 声明
- [ ] P0-brief.md env_constraints 可查阅

## 派发

- **角色**：architect（`{agate_root}/assets/execution-roles/architect.md`）
- **输入**：P1-requirements.md + P0-brief.md
- **输出**：P2-design.md
- **派发 prompt 追加**：

```
## P2 最小验证
方案设计前，先用最小验证确认关键假设（10 行 HTML 测试页 / curl 请求 / 20 行脚本）。
验证结果写入 P2-design.md 的 minimal_validation 字段。
- 方案依赖浏览器行为/安全模型/外部系统行为 → 必须做最小验证
- 纯代码逻辑 → 须在 minimal_validation 字段声明 `纯代码逻辑，无外部系统依赖`（须写明依赖了哪些内部函数/数据转换）
```

## 产出规格

P2-design.md 必须包含：
- **候选方案 ≥2** + 权衡 + 选择理由（design_trivial / follows_existing_pattern 时可只写 1 个，见下方）
- **`candidate_count: N` 必填**：本方案候选方案数（≥2，design_trivial/follows_existing_pattern 时可 1），gate 按此字段校验，不再解析标题。你写几个候选就填几个，与正文一致。
- **四字段**：`packages:` `domains:` `ui_affected:` `gate_commands:`
- **files_to_read**：实现时需要参考的文件清单（控制 P4 implementer 上下文）
- **env_constraints**：确认/细化 P0-brief 的环境约束
- **minimal_validation**：验证结果 或 声明"纯代码逻辑，无外部系统依赖"（声明时须附理由）

`candidate_count`/`packages`/`domains`/`ui_affected` 写在文件头 **frontmatter**（`---` 分隔块），
不写正文；`gate_commands:`/`files_to_read:`/`env_constraints:`/`minimal_validation:` 留正文。
**可直接复制的完整样例**：
```yaml
---
phase: P2
task_id: TAG0001           # 替换为实际任务编号
type: design
parent: P1-requirements.md
trace_id: T001-P2-20260101 # {task_id}-P2-{YYYYMMDD}
status: draft
created: 2026-01-01
agent: architect
# ── v2.0 机器字段 ──
candidate_count: 2                # int ≥1，必填
packages: [pkg-a]                 # list，必填
domains: [backend, cli]           # list，必填
ui_affected: false                # bool，必填
ui_design_section: true           # bool，可选（presence 语义：ui_affected: true 时声明已含 UI 设计节）
---
```

**UI 设计节（`ui_affected: true` 时必含，P2 gate 校验）：** `ui_affected: true` 的 P2-design.md
正文必须包含 `## UI 设计` 节，节内含**渲染形态声明**（`渲染形态:` 声明行，复用 P1 frontmatter
`ui_render_shape` 的规范形态值 + 中文注释，gate 按规范化值比对校验 P1-P2 一致；无 P1 声明时按
布局型默认）+ **维度选择**（`适用维度:` 声明行）+ **按形态适配的 checklist**（常规布局型 =
布局/交互/视觉三类；渲染组件/时序特效型 = 渲染正确性/动效时序等适用维度 checklist；不适用的维度
显式声明"维度不适用"）。缺 UI 设计节 / 缺形态声明 / 缺按形态 checklist / P1-P2 形态声明不一致 →
P2 gate exit 1。结构规格见 `assets/execution-roles/architect.md`「UI 设计节」节（由 architect
兼任产出，不新增 designer 角色）。

**骨架产出（`project_phase: bootstrap` 时必含，P2 gate 校验）：** P1-requirements.md frontmatter
声明 `project_phase: bootstrap`（0→1 新项目；缺省 `established` 不触发）的任务，P2 architect 除
P2-design.md 外，还须在 task 目录下产出 `P2-skeleton.md`（须含 `## 骨架声明` 标题）。骨架内容以
「候选目录集合 + 项目侧声明」的参数化形式表达（不写死具体语言/框架目录名），模板见
`assets/templates/skeleton-template.md`，结构规格见 `assets/execution-roles/architect.md`
「骨架设计职责」节（由 architect 兼任产出，不新增专属角色）。`project_phase` 字段缺失或非
`bootstrap` 时不检查（向后兼容，行为与改动前一致）。

候选方案简化（须附理由，无理由视为无效声明，要求 ≥2 候选方案）：
- `design_trivial: true` + 理由（为什么 trivial）→ 可只写 1 个候选方案（P2 仍不可省略）
- `follows_existing_pattern: [src/foo.py]`（列出参照文件路径）→ 可只写 1 个候选方案，参照已有模式（P2 仍不可省略）

## dispatch_plan 机器字段（可选，TAG0014）

> 本字段是 P2 对**后续阶段编排方案**的机器声明（评估 + 编排模式，见 dispatch-protocol「派发编排机制」），由 architect 在"批次设计"节（execution-roles/architect.md）产出，P2 gate 校验其合法性。

方案含多个独立子任务（多包/多模块/high 复杂度）时，P2-design.md frontmatter 应声明 `dispatch_plan:`（单行 flow YAML，与 candidate_count 同级，**不入 frontmatter-check schema**，缺省不校验）：

```yaml
# ── v2.0 派发编排字段（可选）──
dispatch_plan: {mode: static-batch, parallel_limit: 3, batches: [{id: pkg-a, complexity: medium}, {id: pkg-b, complexity: low}]}
```

字段契约（gate 校验口径）：
- `mode` ∈ {single, static-batch, parallel, recon-then-split, serial}——编排模式（单发/静态拆批/并行/先理解后拆/串行链）
- `parallel_limit` 可选，≥1 整数——并行上限（缺省 3）
- `batches` 可选——mode ∈ {static-batch, parallel} 时每批须含 `id` + `complexity` ∈ {low, medium, high}；批数 ≤ parallel_limit
- 缺字段 / 坏 YAML → P2 gate 跳过校验，行为等同现状（向后兼容，不误拦）

## 影响面梳理（强制节）

**写候选方案之前**先做影响面梳理——方案的取舍取决于它牵动多大面，先设计再补影响面等于反过来给方案找理由。P0 卡片的「同类/影响面预判」给量级、P1 卡片的「同类扫描」给清单，P2 在这两者基础上做**候选方案级**的影响域分析，三处同源、逐级细化，不重复劳动。

P2-design.md 正文必须含影响面梳理节，覆盖三部分：

1. **改什么（Modify）**：逐文件/逐模块列出改动点 + 关联 BDD 编号；改动落点必须落到"哪个文件的哪个小节/函数"，不写"相关代码"这种模糊表述
2. **不改什么（Not Modify）**：显式列出**看起来该改但决定不改**的文件/范围 + 理由。这一栏比"改什么"更容易漏，也是 P4 implementer 判断范围边界的依据（避免"顺手改进"）
3. **风险在哪（Risk）**：每条风险配一条缓解措施；跨模块引用、双源同步（权威源 + 副本）、schema 变更、并发/资源竞争是高频风险项

梳理动作要有客观证据：grep/rg 命中清单、读过的消费方代码、既有 gate 脚本的校验口径——不是凭印象列。P1 已声明 `follows_existing_pattern` 的任务同样要做（沿用既有模式不等于影响面为零）。

## gate_commands 声明

gate_commands 在 P2 固化，后续阶段按此执行：

```yaml
gate_commands:
  P3: "pytest"                  # 可选：测试运行器（verbose 输出，供 check-tdd-red.py 自动读取）
  P5: "pytest -q --tb=no"       # 紧凑输出模式
  P5_e2e: "playwright test --reporter=line tests/e2e/"  # ui_affected: true 时必填
  P5_timeout_seconds: 120       # 可选：该 key 命令的预期耗时上限（秒），见下方字段规则
  P5_e2e_timeout_seconds: 300   # 可选：per-key 声明，不同命令类型各自取档
```

### `{key}_timeout_seconds` 字段规则

`timeout_seconds` 是 `gate_commands` 块内的**可选声明性字段**，用来给每条 gate 命令声明"预期耗时上限"，供跑命令的一方（主 Agent / subagent）据此设置 shell 层超时。四点规则：

1. **排除 P3**：`gate_commands.P3` 继续走既有 `AGATE_TDD_TIMEOUT` 环境变量机制（默认 120s，由 `agate_common.py` 的 `run_test_with_formatter()` 消费、`check-tdd-red.py` 读取，exit 124 → 超时 JSON，区分 A/B 类错误）。`timeout_seconds` **只服务 P5 / P6 / 其他非 P3 key**，不覆盖 P3。两层不合并：P3 层是运行时代码真实消费的超时，`timeout_seconds` 是给人和 subagent 读的静态声明
2. **per-key 声明**：写成 `{key}_timeout_seconds`（如 `P5_timeout_seconds` / `P5_e2e_timeout_seconds`），每条 key 各自声明，**不设整体共享默认**——单元测试与 E2E 的耗时差 2.5 倍以上，共享一个值起不到分类阈值的作用。命名与既有 `{key}_formatter` / `{key}_e2e` 的 per-key 惯例一致
3. **三档默认基准表**（**建议档位，需按命令类型手动声明，不是自动推断**——没有任何代码去"猜"命令属于哪一类）：

   | 命令类型 | 建议档位 | 依据 |
   |---------|---------|------|
   | 单元测试类（pytest / vitest 等） | 120s | 与 `AGATE_TDD_TIMEOUT` 默认值对齐，同类命令的既有锚点 |
   | E2E 类（Playwright / CDP） | 300s | 覆盖页面加载 + 多步操作；比脚本内部硬超时（HARD 90s/180s）更大——外层命令级预期时长必须留够内层完整走完的余量 |
   | 构建类（编译 / 安装依赖 / 打包） | 600s | 覆盖 `npm install` / 编译等长操作。宁可档位定高，也不要让长命令被误判失败（TPV0093 教训：`make test-quick` 挂 188 分钟） |

4. **向后兼容**：缺字段 → 行为等同现状（沿用 `dispatch_plan` 的"缺字段 / 坏 YAML → gate 跳过校验"先例），不新增强制阻断，老任务无需回填

与运行时超时纪律的关系：本字段是**静态声明**（层级 1），subagent 执行命令时真正去设 shell timeout 的是**层级 4** 的「命令超时兜底」（取值 = 预期耗时 ×1.5；本字段已声明时"预期耗时"直接取该值）。四层超时机制的完整分层见 dispatch-protocol.md「命令超时兜底与既有超时机制的分层关系」。

### env_constraints 与 gate_commands 的边界（不等价）

`env_constraints` 是**声明性字段**——它只做信息确认/注入（写清楚环境约束是什么，供 P4/P8 读取参考），本身不会被自动执行，也没有任何 gate 脚本会去校验 `env_constraints` 里写的条件是否真的成立。真正被执行的机制是 `gate_commands`：P5/P6 只会去跑 `gate_commands` 里声明的命令，不会去"执行" `env_constraints` 的内容。二者不等价，不能互相替代。

**因此**：任何需要被强制执行的约束，必须落到 `gate_commands`（有命令可跑、有 exit code 可判定），或者落到 P4/P8 阶段卡片里的明确 checklist 条目（有人工自查动作可执行）。只写进 `env_constraints` 而不落 `gate_commands`/checklist 的约束，等于没有强制力——architect 设计时若发现某条环境约束必须被强制执行，不要止步于写进 `env_constraints`。

### `--strict` 反模式：不要放进 `&&` 链路中间

`gate_commands` 的每个 key 声明的是**一条完整命令**，若把多个校验命令用 `&&` 拼接成一条命令串塞进同一个 key，会有短路问题——只要前一个命令非零退出，后面的命令（包括 `--strict` 校验）根本不会跑，看似"全部声明了"，实际后半段从未被执行过，问题被掩盖。

**反例（不要这样写）**：
```yaml
gate_commands:
  P5: "pytest -q --tb=no && check-protocol-consistency.py --strict && shellcheck scripts/*.sh"
```
上面这条命令一旦 `pytest` 失败就短路退出，`--strict` 校验和 `shellcheck` 都不会执行，历史上 TAG0004 等任务已经在这类写法上吃过亏。

**正确做法**：把每个校验拆成独立的 key 分别声明，各自独立跑、独立记录 pass/fail，不共享短路关系：
```yaml
gate_commands:
  P5: "pytest -q --tb=no"
  P5_consistency: "check-protocol-consistency.py --strict-errors-only"
  P5_shellcheck: "shellcheck scripts/*.sh"
```
`--strict-errors-only`（仅 ERROR 判失败）适合日常任务默认使用；`--strict`（WARNING-only 也判失败）保留给专门做 WARNING 债务清理的任务主动选用。

## 评审派发（C8 机械映射）

按 P1 声明的 domains + risk_level 机械映射评审：

| domain | risk_level | 必须派的评审 |
|--------|------------|------------|
| backend | 任意 | plan-eng-review（P2 方案评审） |
| frontend | 任意 | plan-design-review |
| 任意 | high | plan-eng-review（硬规则，必须派独立 subagent） |
| 任意 | full（tier=full 或声明 ceremony: full）| plan-eng-review（硬规则，必须派独立 subagent）+ cso（security 域）+ P7 不可裁 |
| P1-requirements.md 含 [NEED_CONFIRM] 且涉及业务方向 | 任意 | plan-ceo-review |

> **去重说明**：同一任务命中多行且触发同一评审角色时，去重只派发一次（如 backend + high 均命中 plan-eng-review，只派 1 个 plan-eng-review，不重复派发）。

多个评审角色 `专家组并行` → 组长汇总 → P2-review.md（status: approved / rejected）。
详见 `agate/rules/review-mapping.md`。

**并行派发**（多个评审角色时）：
1. 同时派发所有触发的评审 subagent（每个一个 task 调用）
   > **操作方式**：在一个 assistant 消息中连续发起多个 task 工具调用（每个评审角色一个）。
   > 不要等前一个 task 返回再发下一个——那是串行，不是并行。
   > 平台会并行执行多个 task，全部返回后再进入下一步（派发组长汇总）。
2. 每个评审 subagent 各写一个 dispatch-context + 各自产出文件（示例非穷举，按 C8 映射表触发）：
   - plan-eng-review → P2-review-eng.md
   - plan-design-review → P2-review-design.md
   - plan-ceo-review → P2-review-ceo.md
   - cso → P2-review-cso.md
3. 所有评审返回后，派发组长汇总 subagent（角色：review + 指定为「专家组组长」）
4. 组长输入：所有评审文件路径
5. 组长产出：P2-review.md（统一 status: approved / rejected）。**组长 subagent 产出的 P2-review.md 的 Header agent 字段必须是组长角色名（非 main）——check-gate.py P2 硬拦截 agent=main 的 approved**
6. 组长规则：
   - 不发表新意见，只汇总
   - 任何专家标 BLOCKER → status: rejected
   - 多位专家分歧 → 标「专家组分歧」交人工
   - 全票无 BLOCKER → status: approved

**单评审角色时**：直接派发，无需组长汇总，产出直接写 P2-review.md。

review 不通过 → architect 修改方案 → 再 review → … → approved（⑩迭代循环，review 和 gate 重试共享 retry 预算）

**UI 测试选择器**：涉及前端时，P2 design 建议声明 UI 组件的稳定测试标识清单（如 `data-testid`，而非 class 命名）。P3 test-designer 用稳定标识定位元素，P4 implementer 按清单实现--class 命名可重构，稳定标识不变。具体方案由 P2 architect 决定。

## gate 规则

```bash
check-gate.py P2 $TASK_DIR
```

- 候选方案数 ≥2（design_trivial / follows_existing_pattern 时可只写 1 个）
- P2-review.md 存在且 status: approved（agent≠main）— 不存在 → gate exit 1
- 四字段齐全（packages/domains/ui_affected/gate_commands）
- gate_commands.P3 可选（非 pytest 项目建议声明，供 check-tdd-red.py 自动读取测试运行器）
- 候选方案 ≥2 时含权衡/选择理由

## 推进条件（全部满足才写 phase: P3）

- [ ] P2-design.md 候选方案 ≥2（或 design_trivial/follows_existing_pattern 须附理由时可只写 1 个）+ 四字段齐全
- [ ] 含「影响面梳理」节（改什么 / 不改什么 / 风险在哪 三部分齐全，且写在候选方案之前）
- [ ] P2-review.md 存在且 status: approved（agent≠main）
- [ ] gate_commands.P5_e2e 已声明（ui_affected: true 时）

## 常见错误

1. **忘了最小验证**：方案依赖外部系统行为（API MIME 类型、浏览器 CSP 等）但直接假设前提成立 → 到 P6 才发现不可行。跑一个 curl / 10 行 HTML 就能 5 分钟发现
2. **gate_commands.P5 只列单元测试**：UI 任务时缺少 P5_e2e → P5 不会跑端到端验证
3. **files_to_read 列太多文件**：把所有相关文件都列上 → P4 implementer 上下文爆炸。只列确实需要参考的
4. **忘了派评审**：按 C8 映射机械执行，不靠"觉得不需要"
5. **gate 不过 ≠ 你失败了**：红灯指向工作/设计的问题，不指向你。正确动作是诊断→退回/重试/PAUSED，不是修改产出让它变绿。

## 下游影响

- P4 依赖 files_to_read 导航代码阅读范围
- P5 依赖 gate_commands 执行验证命令
- P6 依赖 ui_affected 判断是否需要 vision-helper
- gate_commands 在 P2 固化后 P4-P6 不能改——设计阶段是声明验证契约的唯一窗口

> 完成 → 读 phase-cards/P3-tdd.md
<!-- AGATE_CARD_END -->

<objective_info>
### A. 路径拓扑
- worktree 根 = `/home/kity/oclab/agateon/.worktrees/agate-TAG0027`（分支
  feat/TAG0027-orchestration-semantics）
- 任务目录 = `agate-workspace/tasks/TAG0027-orchestration-semantics/`
- 协议本体（改造对象）= worktree 的 `agate/`；`~/.agate` = 稳定版主 checkout（勿改）
- 测试基线：pytest 1311（unit 1191 + regression 28 + integration 92）串行全绿；count-tests
  collect 口径 1335；consistency 0 ERROR（--strict-errors-only）；存量并行偶发 1 例
  （test_agate_next_card.py sha256 漂移，CI --reruns 1 兜底）
- 环境：python 3.12.3 / pyyaml 6.0.1 / pytest 9.0.3 / ruff ~/.venvs/agate-dev/bin/ruff

### B. 设计决策面（P2 必须定，P1 留白给 P2）
1. next/retreat 字段 schema 形态：主线 P0-P8 每条目加 next/retreat 键；P8 next 值域（无后继 →
   READY？）；P6.5 条目如何表达"子阶段门槛"（挂 P6→P7 转移，非独立边）；值域枚举 vs 自由串
2. S-1/S-2 md 侧扩展：WORKFLOW.md 阶段总览表加列（next/retreat 列）或等效锚点，与
   check-structure-consistency.py S-1 YAML→md 双向逻辑兼容
3. exit2-resolution 落盘格式与位置（任务目录内？.state.yaml 字段？）+ judge/provenance 复核
   挂载点（check-judge-verdict.py verdict 校验 vs check-events.py 事件类型扩展）
4. agate next / agate advance CLI 契约：参数、输出、exit code、与 check-gate.py 三态消费分支、
   retreat 目标解析、retry 记录写入、与 agate-retreat-to.py 对接边界（advance 调 retreat-to vs
   内联实现）
5. agate dispatch CLI 契约：单命令 = 读上下文模板 + 渲染时拼装 phase-card（Lazy Injection）+
   写 dispatch-context；与 agate-render-dispatch-prompt.py / agate-inject-card.py /
   agate-next-card.py 的关系（复用 vs 替代）；渲染产物卡片来源标记格式（审计 2 A1 依赖）
6. 审计 2 A1：扫描对象切换的兼容策略（渲染产物标记 + 手工物理块并存识别）
7. 档位 C 对接：loop-orchestration.md 文字更新 + agate next 调用点（文档约定层 vs 脚本层？
   档位 C 是主 Agent 执行模式，agate next 由主 Agent 调用——BDD-11 的可观测证据如何产生）
8. 护栏 1 机械化：check-protocol-consistency.py 新增 CHECK 的扫描规则（段落级判据 + 豁免
   清单实现 + 存量清理批次面）

### C. P1 评审 4 条非阻断边界观察（约束 8 已转述，此处为原始记录）
① BDD-10 Given 写"从 P7 按转移表回退到 P4"——示例用边不当（P7 失败不回 P4），正文核心判据
   （advance 回退走 retreat-to 单步 + diff≥2 拦截）正确，示例修正即可
② BDD-15 禁词含 task，rules/dispatch.yaml 既有 task_fields/gates 等键含 task——禁词清单与
   既有数据面兼容性须核实（可能需区分"独立平台工具指代" vs "字段名组成部分"）
③ BDD-17 排查面 = 9 文件窄于机械化扫描面——存量清理/豁免的完整面由 P2 定义
④ D-2 称 adr.md 豁免因 docs/reviews 属 NARRATIVE 区，但 adr.md 在 agate/ 协议区——豁免理由
   核实修正（ADR-008 平台名属决策叙事，按实现注记挂载或协议区白名单豁免）
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
