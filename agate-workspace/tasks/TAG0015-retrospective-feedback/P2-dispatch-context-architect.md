> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。

---
phase: P2
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0015
role: architect
retry: 1
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

## 重试 #1（AP-1 阻塞问题修订，本节优先于下方原始派发指引）

plan-eng-review 对你上一版 P2-design.md 的判定是 `needs-revision`（8 条约束 7 条通过，1 条阻塞），
完整评审见 `{AGATE_WORKSPACE}/tasks/TAG0015-retrospective-feedback/P2-review.md`。**只需处理
AP-1（阻塞）+ 顺手处理 AP-2（非阻塞，可选）**，不要重写全文，不要动已确认成立的其余部分（候选
方案 B / 20 BDD 覆盖 / "不改什么"节 / gate_commands / minimal_validation / dispatch_plan，
review「锁定决策」节已逐条核实这些成立，无需重新论证）：

**AP-1（阻塞）**：你上一版候选方案 A1 把 L2 checkpoint 的落盘时机设计为"任务完成时一次性落盘"，
排除了 `agate-workspace/roadmap/roadmap.md` RM-AG0020 详情第 5 点原始设计里明确并列的**两件套**
机制之一——"每个阶段 gate 通过时落盘 `P{n}-checkpoint.md`（本阶段异常/关键判断/subagent 表现）"。
review 指出：①你排除这一件套时引用的"已被 P{n}-progress.md + orchestrator-log.md 覆盖"这个
等价性断言，没有做内容层面的逐项比对（progress.md 是 subagent 中间产物，不是主 Agent 的阶段级
评估；orchestrator-log 扩展后是"决策+简要依据"，颗粒度也不等于阶段级总结）；②roadmap.md 的
"验证口径"明确要求"长任务复盘能在 session compact 后仍写出完整因果链（L2 落盘生效）"——若 L2
唯一落点在 P8 完成后，任务中途（如 P4/P5）发生 compact 时 L2 尚未产生任何一次落盘，恰恰是
P0-brief 问题⑦要解决的失效场景本身没有被 L2 保护到。

**处理方式（二选一，任一均可解除阻塞，你来判断哪个更合适）**：
a) 恢复 `P{n}-checkpoint.md` 每阶段落盘机制作为 A1 设计的一部分（哪怕内容极简，只要能在中途
   compact 时提供非空的 L2 落点），相应更新 §3.2（state-machine.md 新增小节草案）/§3.3
   （task-files.md 辅助文件表新增行）/§6（实现完成的标志）三处联动；或
b) 保留"只在 P8 落盘一次"的设计，但改用 `[DESIGN_GAP: ...]` 标注形式显式承认这是对 roadmap.md
   原始两件套设计的收窄，写清楚"中途 compact 覆盖不到"这一已知局限 + 为什么可接受（不能再用
   "属于 L1，已被覆盖"这个未经验证的断言掩盖），交后续 P7/主 Agent 判断是否可接受。

**AP-2（非阻塞，可选顺手处理）**：`files_to_read` 里 `agate/scripts/agate_common.py:455-482` 的
行号范围只覆盖 `resolve_workspace()` 函数体，实际 `AGATE_TDD_TIMEOUT` 定义在第 408 行附近，不在
该范围内——若你选择修订 AP-1，可顺手把这条行号范围改为 `400-482`（不修订也不影响本次 P2 approve，
但既然要改文件了顺手带上成本很低）。

修订完成后自检：AP-1 选择的方案（a 或 b）与 §3.2/§3.3/§6 的联动是否一致；若选 a，检查
`agate/tests/unit/test_retrospective_protocol_docs.py`（§5 gate_commands.P3 已声明的测试文件）
是否需要补一条对应的验收锚点声明（review「测试缺口」节已提示这一点）。修订后写回同一路径
`{AGATE_WORKSPACE}/tasks/TAG0015-retrospective-feedback/P2-design.md`（覆盖原文件）。

---

### 目标（原始派发指引，重试时仍适用于未涉及修订的部分）

把 P1-requirements.md 的 20 条 BDD（approved，按"文件→改动"归并组织）转成一份 P2-design.md：
候选方案 ≥2 + 权衡 + 选择理由、影响面梳理（改什么/不改什么/风险在哪）、gate_commands 声明、
files_to_read 导航、minimal_validation。本任务无 UI（`ui_affected: false`），跳过 UI 设计节。

### 约束

1. **domains: [process]（agate 自身协议改动）按本仓库既有惯例映射评审角色**——参照 TAG0012（同为
   `domains: [process]`、`risk_level: medium` 的协议机制改动任务）的先例，P2 阶段派 **plan-eng-review**
   （主 Agent 稍后按此惯例派发，architect 不需要在 P2-design.md 里自己声明评审角色，只需产出方案，
   评审派发是主 Agent 的职责）。
2. **候选方案必须真的是两条不同路线，不是同一方案的措辞变体**——尤其以下两处需要认真权衡（不要
   随手写"方案A/方案B"应付候选数量要求）：
   a. **L2 会话 checkpoint 落点**（BDD-13 四问）：新开一类文件（如 `checkpoint.md`）vs 扩展
      `orchestrator-log.md` 语义覆盖 L2 checkpoint 内容——这是本任务唯一"从零设计新机制"的点，
      两个方向对下游（P4 落地方式、P7 一致性检查、未来任务的心智负担）影响不同，值得认真展开权衡。
   b. **`agate-feedback.py` 的匿名化实现深度**（BDD-18）：轻量正则脱敏（替换项目名字符串/截断
      绝对路径前缀）vs 结构化字段白名单提取（只拷贝 frontmatter 声明的字段值，不触碰原始文本）——
      前者实现简单但可能有脱敏遗漏风险，后者更安全但要求 frontmatter 字段本身已经是"可安全外泄"
      的颗粒度。两种方案的失败模式不同，需要写清楚。
3. **【强制】影响面梳理必须逐条覆盖 20 条 BDD**，不能只挑几条展开、其余带过——P1 已经按文件分组
   （6 大类：postmortem-template 迁移/check-retrospective.py/state-machine.md/跨文件同步/
   AGENTS.md/docs-reviews 存量决策/agate-feedback.py 新增），"改什么"节至少按这 6 类分组列出，
   每类下逐条关联 BDD 编号（不是写"BDD-1~8 见上"这种笼统带过）。
   "不改什么"节至少要显式回应 P1 第 7 节「范围外观察」的 3 项（`hardening-roadmap.md` P2.68 /
   `agate-workspace/archived/` 历史归档 / TAG0013 历史任务产物引用）——确认设计阶段同样不碰这些。
4. **gate_commands 声明必须区分脚本改动 BDD 与纯文档 BDD**——BDD-9/10/11（check-retrospective.py）
   与 BDD-17~20（agate-feedback.py）需要 `gate_commands.P3`（pytest，TDD 红灯）；纯文档类
   BDD（1-8/12-16）没有配套自动化测试，architect 需要在 gate_commands 里说清楚"P5 如何验证纯文档
   BDD"（大概率是 grep 断言脚本，可以是新增的一次性验证脚本，或者复用 pytest 里新增的文档结构
   断言测试——由 architect 决定，但必须给出可执行命令，不能留空）。
5. **minimal_validation**：本任务是纯协议文档 + Python 脚本改动，无浏览器/外部系统依赖，正常声明
   "纯代码逻辑，无外部系统依赖"，并写明依赖了哪些内部函数/数据转换（如 check-retrospective.py 的
   `_scan_scope_plus`/`_retries_over`、agate-feedback.py 待设计的 YAML frontmatter 解析 + JSON
   序列化 + 脱敏规则）。
6. **dispatch_plan（可选）**：本任务涉及 6 个 packages、20 条 BDD，改动面不小，architect 可自行
   判断 P4 实现是否需要声明 `dispatch_plan`（如按 6 个 packages 拆批）。若判断单次 implementer
   派发即可完成（改动虽多但都是加性文本改动，逻辑不复杂），也可以不声明，两种选择都可接受，但需
   要在「批次设计」节说明判断依据。
7. **BDD-16 存量文档处理决策已在 P1 定案**（保留 docs/reviews/ 4 份存量复盘原位 + 顶部加标注，
   不物理迁移）——P2 设计不要重新讨论这个决策，只需设计"标注怎么加"的具体实现方式（如统一的标注
   文案模板）。
8. **`agate/AGENTS.md:11` 措辞同步（BDD-15）范围要收窄**——只改这一行的表述让它区分"历史存量复盘
   仍在 docs/reviews/"与"新复盘归 tasks/{Txxx}/"，不要借机重写 AGENTS.md 其他部分。

### 上游关联

- P1-requirements.md 的 BDD-6/BDD-7 是 BDD-17 的输入依赖（frontmatter 字段 + agate 反馈节先定义，
  agate-feedback.py 后解析）——P2 设计 `agate-feedback.py` 时必须先确认 BDD-6/BDD-7 在
  retrospective-template.md 里的具体字段名/节标题，不要自己另起字段名。
- P1 第 8 节裁剪说明：`phases` 全阶段不裁（P3 不可省），architect 设计 gate_commands 时要对应
  声明 P3 的测试运行器命令。
- check-retrospective.py 现有设计哲学是"只提醒不阻断"（exit 0 恒成立）——P2 方案不应该把它改造
  成阻断式 gate（这是 P1 已经定的边界，P2 只是把"怎么改"具体化）。

### 输入文件（按顺序读）

1. `{AGATE_WORKSPACE}/tasks/TAG0015-retrospective-feedback/P1-requirements.md`（226 行 + 修订后
   略有增长，全文——20 条 BDD 是本阶段设计的直接输入）
2. `{AGATE_WORKSPACE}/tasks/TAG0015-retrospective-feedback/P0-brief.md`（环境约束 + known_risks）
3. `agate/scripts/check-retrospective.py`（100 行全文，改动对象）
4. `agate/tests/unit/test_check_retrospective.py`（242 行，改动前的既有测试结构，供设计新增
   断言的落点参考）
5. `docs/reviews/postmortem-template.md`（迁移前的模板全文，理解要迁移的起点内容）
6. `agate/state-machine.md` 第 470-490 行附近（orchestrator-log.md 防无响应节原文）
7. `agate/AGENTS.md` 第 1-15 行附近（第 11 行措辞冲突的上下文）
8. `agate/assets/execution-roles/architect.md`（角色定义，含影响面梳理/最小验证/dispatch_plan
   规格要求）

### 门槛（什么算完成）

P2-design.md 含：candidate_count ≥2（frontmatter）、packages/domains/ui_affected（false）/
gate_commands 四字段齐全、影响面梳理三部分（改什么按 6 大类逐条关联 20 条 BDD / 不改什么含 P1
范围外观察 3 项 / 风险在哪每条配缓解措施）、minimal_validation、files_to_read。
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
- P1-requirements.md 客观事实：20 条 BDD（approved），frontmatter `risk_level: medium`，
  `phases: [P1,P2,P3,P4,P5,P6,P7,P8]`（全阶段不裁），`packages: [assets/templates, scripts,
  state-machine, phase-cards, docs-reviews-migration, core-protocol-docs]`，`domains: [process]`，
  `implicit_coupling: true`。
- 环境基线（P1 阶段验证过，未再变化）：`pytest` 909 passed + 2 skipped；
  `check-protocol-consistency.py --strict` 0 ERROR / 279 WARNING。
- BDD 按文件分组一览（P1 第 4 节结构，供 architect 快速定位，不替代通读全文）：
  4.1 postmortem-template.md 迁移（BDD-1~8）／4.2 check-retrospective.py（BDD-9~11）／
  4.3 state-machine.md orchestrator-log 扩展（BDD-12~13）／4.4 跨文件同步（BDD-14）／
  4.5 AGENTS.md（BDD-15）／4.6 docs/reviews 存量决策（BDD-16）／4.7 agate-feedback.py 新增
  （BDD-17~20）。
- `test_check_retrospective.py` 现状：242 行，12 个 `test_` 用例，均围绕 `retries_over`/
  `SCOPE+`/`override` 三个既有触发点，对路径文案（BDD-9）与新触发条件（BDD-10）均无断言。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
