---
phase: P2
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0007
role: plan-eng-review
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

## 【第 2 轮：复评，增量模式】

上一轮你（plan-eng-review）判定 rejected，1 个阻塞项 + 2 个非阻塞措辞建议，见
{AGATE_WORKSPACE}/tasks/TAG0007-project-structure/P2-review.md（该文件仍是上一轮产出，本轮
完成后会被覆盖）。architect 已用 Edit 做了针对性修复（未重写全文），本轮**只需复核这 3 处**：

1. **阻塞项**：`gate_p7` pairing 校验是否已补全为两层结构（内部一致性
   `code_map_reviewed_count < code_map_new_files_count` + 转抄核对"P4 实际计数 vs
   `code_map_new_files_count`"），且与源码 `check-gate.py` `gate_p7`（L807-903）现有 DESIGN_GAP
   两层结构（L840-848 内部一致性 / L873-893 转抄核对）真正对齐（字段对应关系不能颠倒）；
   `code_map_new_files_count` 字段是否已被正确引用（不再是声明了但未使用）；§5
   minimal_validation 第 1 条的 `result` 措辞是否已如实反映修复情况。
2. **非阻塞项 1**：§1.3 R5 / §1.2「不改什么」是否已改写措辞，不再暗示 CHANGELOG 追加冲突与
   CODE-MAP 结构化字段冲突形态类似。
3. **非阻塞项 2**：§7 是否已改写"已完整声明五字段标题名与格式要求"为准确表述（只声明了字段
   类别名，markup 形式由各批次自行决定）。

复核方式：直接读当前 P2-design.md 对应位置（§1.1/§2.3/§5 阻塞项，§1.2/§1.3 R5 非阻塞项1，
§7 非阻塞项2），必要时重新核对 `check-gate.py` 源码确认两层结构描述是否真正准确（不要只信
architect 的自述，独立核实字段对应关系：转抄核对比较的应是 `code_map_new_files_count` 而非
`code_map_reviewed_count`，这是上轮发现问题的核心，容易被"换个说法但字段对应关系仍然颠倒"式
的表面修复蒙混过关，需重点盯防）。其余 7 项已判定方向确认/合规的核查点（决策组1/2/4、BDD-4/7
累加设计、BDD-10 落地、多方案探索诚实度、gate_commands、dispatch_plan 拆批不相交性）不必重新
展开，可简述"维持上轮判定，未变更"。三处均确认到位且字段对应关系正确 → status: approved；仍有
缺口或表面修复未解决实质问题 → 具体指出并 status: rejected。

---

## 首轮派发指引（背景，供理解上下文）

### 目标
独立评审 architect 刚产出的 P2-design.md（TAG0007：RM-AG0008 骨架 + RM-AG0009 CODE-MAP，8 个
候选方案分 4 个决策组，static-batch 4 批并行拆批），判定 approved / rejected，产出 P2-review.md。
本任务按 C8 机械映射（domains=backend 命中一次 + risk_level=high 硬规则命中一次，去重只派一次）
只触发 plan-eng-review 单一评审角色，**无需组长汇总**，产出直接写 P2-review.md。

### 约束
1. 关键设计决策核实（逐条给出评审意见，不要泛泛而谈）：
   - **决策组 1（落盘位置）**：骨架落 task 目录 `P2-skeleton.md` companion 文件；CODE-MAP 复用
     `{AGATE_WORKSPACE}/agents/` 子目录（不新增 WORKFLOW.md 第 10 个固定子目录）。核查该选择是否
     真的零协议表面变化、是否有遗漏的边界情形。
   - **决策组 2（骨架触发）**：新增 P1 可选字段 `project_phase: bootstrap`（缺省 established，
     向后兼容）驱动 P2 architect 产出 companion 文件。核查向后兼容性论证（1011 条既有测试不受
     影响）是否站得住脚——重点看 §5 minimal_validation 声称已读 `check-gate.py` 源码确认
     `_frontmatter_field` 对缺失字段返回空字符串这一假设是否可信、测试计划是否覆盖该分支。
   - **决策组 3（CODE-MAP 一致性核对）**：复用现有 `DESIGN_GAP`/`DESIGN_GAP_REVIEWED` 的
     frontmatter 计数 + 正文 regex 双轨判定模式（pairing gate），依赖方向偏离检测走人工判断 +
     "必须留痕"硬校验（不做自动化静态依赖分析）。核查这一取舍是否真的经得起 ADR-003（不绑定
     技术栈）审视，以及"只强制留痕不强制判断正确"这一让步是否被诚实标注为局限（而非包装成
     "已解决"）。
   - **决策组 4（角色复用）**：不新增专属角色，骨架并入 architect.md，CODE-MAP 核对并入
     consistency-reviewer.md。核查两角色文件承担的职责增量是否会导致认知过载（architect.md
     已有 P2 设计 + UI 设计节两块职责，再加骨架设计是否合理）。
2. **BDD-4/BDD-7 累加义务的落地检查**：P1 已声明两条 BDD 需同一次实现动作满足，P2-design.md
   §1.1 提出「新增文件核对表」（P4-implementation.md 新增小节，implementer 为每个新文件同时填
   骨架归属列 + CODE-MAP 处理列）。核查这个"一张表两列"的设计是否真的让 implementer 一次动作
   满足两条独立验收标准，而非表面合并、实际仍是两套判定。
3. **BDD-10（refactor 不豁免）落地检查**：P2-design.md §1.1 声明在「新增文件核对表」末尾追加
   一句"change_type: refactor 同样适用本表"。核查这一行是否足以承载 P1 BDD-10 的验收含义，还是
   需要更明确的机制绑定（如 P6-acceptance.md 的 refactor 口径小节也要提及）。
4. **并发更新边界（P1 隐含需求第 8 条）处理方式检查**：P2 §1.3 R5 declares"本轮不解决，比照
   `CHANGELOG.md [Unreleased]` 现有处理方式"。核查这一类比是否恰当（CHANGELOG 冲突通常是纯文本
   追加冲突，CODE-MAP.md 可能涉及结构化字段更新，冲突形态是否真的类似）。
5. **多方案探索的诚实度检查**（角色定义已要求）：4 个决策组各自的"候选 B（不采纳）"是否是真实
   的替代方案（在某些维度上确实更好），还是稻草人陪衬（缺点只是"不如候选 A"）。重点看决策组 3
   候选 B（自动化静态依赖分析）——这条排除理由充分（违反 ADR-003），但决策组 1/2/4 的候选 B 也
   要同样核实是否只是形式满足。
6. **测试缺口检查**：`test_skeleton_template_stack_neutral.py` 用黑名单字符串匹配检测硬编码技术栈
   目录名（P2 §1.3 R7 已自陈是"启发式黑名单，非语义验证"）——核查这个自我认知是否准确，是否需要
   在测试文档中进一步强调局限性避免被误当作完备性保证。
7. **gate_commands 声明格式检查**：§6 是否真的用独立 key（非 `&&` 链路），是否覆盖了回归基线
   验证（P1 BDD-5/BDD-11 要求的"1011 个现有测试仍全部通过 + 一致性检查仍 0 ERROR"）。
8. **dispatch_plan 拆批检查**：4 批文件集合是否真的两两不相交（§7 已自称核查过，独立复核一次）；
   `dogfood-bootstrap` 批次依赖 `code-map-docs` 批次确定的模板结构但仍声称可同轮并行——核查这一
   并行判断的依据是否可信（P2-design.md 是否真的已完整声明了足够的信息让 dogfood 批次不依赖
   code-map-docs 批次的实际产出）。

### 上游关联
P1-requirements.md（approved）→ P2-design.md（本次评审对象）：候选方案 8 个（4 决策组 × 2），
影响面梳理（改什么/不改什么/风险在哪，7 条风险）已完成，dispatch_plan 声明 static-batch 4 批
（skeleton-docs / code-map-docs / gate-script-both / dogfood-bootstrap），并行度 4，无跨批文件
重叠（check-gate.py 的 gate_p2/gate_p4/gate_p7 三处判定合并进单一批次 gate-script-both，规避
TAG0017 §1.3 R1 同类"单文件多函数跨批冲突"教训）。

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0007-project-structure/P2-design.md（评审对象）
- {AGATE_WORKSPACE}/tasks/TAG0007-project-structure/P1-requirements.md（需求基线，核对方案是否
  覆盖全部 11 条 BDD）
- {AGATE_WORKSPACE}/tasks/TAG0007-project-structure/P1-review.md（P1 评审关注点，核查 P2 是否
  延续了正确的处理方式）
- /home/kity/oclab/agate/.worktrees/agate-TAG0007/agate/adr.md（ADR-003 不绑定技术栈、ADR-005
  机制交叉判据，决策组 3 候选 B 排除理由 + 决策组 1/2 落点判据的评审依据）
- /home/kity/oclab/agate/.worktrees/agate-TAG0007/agate/role-system.md（角色清单最小化既定原则，
  决策组 4 评审依据）
- /home/kity/oclab/agate/.worktrees/agate-TAG0007/agate/scripts/check-gate.py（DESIGN_GAP pairing
  判定逻辑源码，L807-903 附近，核实 minimal_validation 声称的"结构完全对称可原样套用"是否属实）
- /home/kity/oclab/agate/.worktrees/agate-TAG0007/agate/phase-cards/P2-design.md（P2 卡片本身，
  核对 gate_commands 声明格式/影响面梳理规格是否合规）
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
- architect 返回摘要：「8候选方案（4决策组×2），static-batch 4批并行：骨架落task目录companion
  文件，CODE-MAP复用agents/子目录，复用architect/consistency-reviewer角色」
- P2-design.md frontmatter：candidate_count=8, packages=[phase-cards, execution-roles, templates,
  scripts], domains=[backend], ui_affected=false,
  dispatch_plan={mode: static-batch, parallel_limit: 4, batches: 4 个（skeleton-docs/
  code-map-docs/gate-script-both/dogfood-bootstrap，均 complexity: medium 除 dogfood-bootstrap
  为 low）}
- C8 机械映射命中：domains=backend → plan-eng-review；risk_level=high（P1 frontmatter）→
  plan-eng-review 硬规则；两者去重只派一次，本次派发即该次；无 frontend/NEED_CONFIRM 业务方向，
  不触发 plan-design-review / plan-ceo-review
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
