---
phase: P2
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0026
role: architect
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

产出 `P2-design.md`：把 P1 的 13 条 BDD 转成可实现的方案设计——`check-maintainability.py`
（god-file 跨越 + fuzzy-boundary 检测）、`check-gate.py` gate_p4 三重门槛挂载、
`known-violations-template.md`、P4/P6 phase card 自查、`maintainability.yaml` 配置读取、
pytest 13 条 BDD 覆盖。方案必须给出影响面梳理（候选方案之前）、≥2 个候选方案 + 权衡 +
选择理由（或 design_trivial/follows_existing_pattern 附理由）、files_to_read、gate_commands。

### 约束

1. **范围锁定 P1 基线**：只设计 G0 两条 + P4 三重门槛 + 模板 + P4/P6 卡片自查 + 配置 + 测试。
   G1/G2/G3、RM-AG0022 结构化层联动、第八道 provenance 审计、门户、跨行移动检测一律不设计
   （P1 out-of-scope，发现越界需求停下报告主 Agent）。
2. **挂载阶段 P4，不挂 P6**：检测器数据源 `git diff --cached` 与 P4（代码 staged）对齐；
   P6 卡片只加"可再跑一次检测器"的非阻断自查提醒。
3. **三重门槛结构**：violations 非空时依次校验 ① known-violations.md 存在 ②
   `count_kf_entries` 登记数 ≥ violations 数 ③ P4-review.md status:approved 且 agent≠main
   （第③项 gate_p4 现有检查已覆盖，设计须说明复用而非重复实现；评审角色"approve 前必读登记
   理由"是流程要求，落在 P4 卡片评审 checklist，不新增字段）。
4. **返回约定兼容**：gate_p4 新增一步必须保持既有返回约定（0=通过 / 1=阻断 / 2=WARNING），
   不得改变既有 P4 检查（P4-review 存在/approved/agent≠main/代码 staged）的语义与顺序敏感面。
5. **脚本形态**：`check-maintainability.py` 模块级函数 `check_maintainability(task_dir) -> dict`
   可被 check-gate.py import 复用（不走 subprocess 解析文本），CLI 为薄壳、exit code 唯一判定；
   返回结构对齐 `agate-risk-score.py` 的 `score_task()` 形状（含 violations / 计数 / git_ok）。
   复用 `_load_script`/`_norm_rel` 模式（见客观查证信息 A），不重复实现加载与路径归一化。
6. **配置**：读 `agate-workspace/maintainability.yaml`（不用 `.agate/`），缺失/解析失败用协议
   默认值（N=1000，文档明确"仅供参考可配置"）；配置键至少含 god-file 阈值与 fuzzy-boundary
   正则集（Python/TS 两组）。
7. **consistency 扫描影响必须设计进去**：新脚本 `check-*.py` 会落入
   `check-protocol-consistency.py` 对 `agate/scripts/check-*.py` 的锚点覆盖扫描
   （P1 隐含需求 10）；设计须给出明确方案——锚点登记（在协议文档登记脚本引用锚点）或其它
   经核实的机制路径，并验证不引入 consistency ERROR。这关系到 P7 一致性检查能否通过。
8. **影响面梳理节在候选方案之前**（P2 卡强制）：改什么（逐文件逐函数落点 + 关联 BDD）/
   不改什么（显式列出"看着该改但不改"的 + 理由）/ 风险在哪（每条配缓解）。
   三部分都要有客观证据（grep 命中、已读代码行号），不接受凭印象罗列。
9. **gate_commands 在 P2 固化**（P4-P6 不可改）：声明 P3/P5 及其它 key，每条 key 是完整命令、
   禁止 `&&` 链短路反模式（分 key 声明）；`{key}_timeout_seconds` per-key 按三档基准表声明。
   P5 全量 pytest 是资源密集型 → 编排默认串行（dispatch_plan 若声明写 serial/single）。
10. **测试设计落点**：`agate/tests/unit/` 新增测试文件（参考先例 test_check_gate.py /
    test_check_gate_p5_diff.py / test_agate_risk_score.py），覆盖 13 条 BDD；平台无关硬约束
    （AGENTS.md）：用 pytest tmp_path 不用 /tmp、不裸 PATH、不假设 POSIX symlink、平台差异
    场景按平台分支断言；conftest 支持 AGATE_ROOT env 覆盖。P3 test-designer 会按你的设计
    细化，你给出测试文件落点 + 用例分组即可，不写用例代码。
11. **files_to_read 精准**：只列 P4 implementer 确实要参考的文件（check-gate.py 相关行段、
    risk-score 参照、模板参照、卡片落点），不整目录全读。
12. **minimal_validation**：本任务纯代码逻辑（git diff 解析 + 行数计算 + 正则匹配）→
    在 minimal_validation 字段声明"纯代码逻辑，无外部系统依赖"，并写明依赖的内部函数/
    数据转换（`git diff --cached` 输出解析、count_kf_entries、_norm_rel 归一化）。
13. **UI**：`ui_affected: false`（纯后端脚本/文档/测试），无 UI 设计节、无 UX BDD。
14. **卡片改动设计要具体**：P4 卡（评审 checklist 加"approve 前必读 known-violations 登记
    理由"）与 P6 卡（自查节加检测器复跑提醒，非阻断）的改动落点要落到具体小节标题。

### 上游关联

- P1-requirements.md：13 条 BDD（BDD-1..13）+ 隐含需求 12 条 + 同类扫描 6 类命中 + 全阶段
  不裁声明——设计的验收对照物
- P0-brief.md：known_risks 七条 + out-of-scope + env_constraints
- 落地计划 `docs/design-notes/rm-ag0046-maintainability-gate-plan.md`（v3 定稿）：第 2 节
  落点设计、第 2.1 节脚本形态、第 2.2 节三重门槛伪代码、第 2.3 节 P6 卡自查、第 4.1 节
  模板——设计的直接输入，但不等于照抄：须核实伪代码与当前 gate_p4 实际结构的一致性
- 设计地基 `docs/design-notes/design-maintainability-gate.md`：决策 1（diff 驱动）/2（跨越
  ≠超过）/3（判定权在 gate）

### 输入文件（按顺序读）

1. `agate-workspace/tasks/TAG0026-maintainability-gate/P1-requirements.md`
2. `agate-workspace/tasks/TAG0026-maintainability-gate/P0-brief.md`
3. `docs/design-notes/rm-ag0046-maintainability-gate-plan.md`
4. `agate/scripts/check-gate.py`（gate_p4 ~870-927 / gate_p5 known-failures ~930-985 /
   _STAGED_EXCLUDE_RE ~174 / 分发映射 ~1335-1346）
5. `agate/scripts/agate-risk-score.py`（_load_script :46 / _norm_rel :86 / score_task :202）
6. `agate/scripts/agate_common.py`（count_kf_entries :1015-1017）
7. `agate/assets/templates/known-failures-template.md`（模板格式参照）
8. `agate/phase-cards/P4-implementation.md` 与 `agate/phase-cards/P6-acceptance.md`（卡片改动落点）
9. `agate/tests/README.md` + `agate/tests/conftest.py`（测试约定）
10. `AGENTS.md`（项目约定）

### 产出文件字段

用 `FILE={AGATE_WORKSPACE}/tasks/TAG0026-maintainability-gate/P2-design.md agate-md-field-set --list`
查看本阶段应填字段；`FILE=... agate-md-field-set <key> <value>` 逐个写入；写入失败照错误提示
修正，不要手写 frontmatter；仍失败则报告主 Agent，不要绕开 set。
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
### A. 代码锚点（worktree 实测，2026-08-30）
- `agate/scripts/check-gate.py`（全 1355 行）：
  - `_STAGED_EXCLUDE_RE` :174（`(^|/)P[0-8]-.*\.md$|(^|/)\.state\.yaml$`——P4/P6 判"暂存区
    是否含代码文件"的排除模式）
  - `gate_p4(task_dir)` :870-927：① P4-review.md 存在（无→1）② status==approved（非→1）
    ③ agent 字段缺失→2 / ==main→1 ④ `git diff --cached --name-only` 无代码文件→1
    ⑤ 骨架/CODE-MAP WARNING（不阻断）⑥ return 0
  - gate_p5 known-failures 判定 :930-985（known-violations 数量对齐算法的参照形态：
    客观快照算数 + count_kf_entries 比对 → 不足则 1）
  - 分发映射 :1335-1346（`"P4": gate_p4`）
- `agate/scripts/agate-risk-score.py`：`_load_script` :46（importlib 加载模式）、`_norm_rel`
  :86（路径归一化）、`score_task(task_dir)` :202（返回 dict 形状参照）、`_impact_high` :139
- `agate/scripts/agate_common.py`：`count_kf_entries(text)` :1015-1017
  （`^\|\s*[0-9]+\s*\|` 行首计数）
- `agate/assets/templates/known-failures-template.md`：现存模板（`| # | 测试文件 | 失败数 |
  根因 | 与本任务相关 | 处理计划 |`，语义=预存失败）——known-violations 模板对齐其格式但
  语义反转

### B. consistency 扫描面（P1 隐含需求 10，设计必答）
- `check-protocol-consistency.py` 对 `agate/scripts/check-*.py` 有锚点覆盖扫描（check_anchor_
  coverage）；新增 `check-maintainability.py` 会进入该 glob
- `agate-summary.py` 的 `_DRIFT_SCRIPTS` 清单是另一处可能需同步的脚本清单
- 设计必须给出：新脚本是否需要协议文档锚点登记（哪个文档哪一节）或经核实的豁免路径，
  并在方案里注明"P7 前用 worktree 自己的 check-protocol-consistency.py --strict-errors-only
  实测验证"

### C. 测试布局与约定
- `agate/tests/`：conftest.py + unit/（82 文件）+ regression/ + integration/ + fixtures/
- 直接先例：`test_check_gate.py`（gate 判定主套件）、`test_check_gate_p5_diff.py`（P5
  diff 判定）、`test_check_gate_p1_review.py`（P1 评审 gate）、`test_agate_risk_score.py`
  （risk-score 返回结构）、`test_md_parse_scan.py`（count_kf_entries）
- conftest 支持 `AGATE_ROOT` env 覆盖（CI 无 ~/.agate）；测试用 tmp_path 构造任务目录
- 平台无关硬约束（AGENTS.md）：不硬编码单平台假设、Windows 场景按平台分支断言或模拟
- 基线：全量 pytest 全绿；count-tests 1308（2026-08-30 实测，P0-brief）——文档不写死，
  P5 用 `bash agate/tests/scripts/count-tests.sh` 实测验证

### D. 卡片改动落点（P1 已定，设计细化）
- `agate/phase-cards/P4-implementation.md`：评审 checklist 增加"approve 前必读
  known-violations.md 登记理由"（流程要求，非新字段）
- `agate/phase-cards/P6-acceptance.md`：自查≠gate 节增加"可再跑一次 check-maintainability.py
  确认 P4 后无新增反模式"（非阻断自查提醒）

### E. gate_commands 建议（architect 定夺，P2 后固化）
- P3: pytest（check-tdd-red.py 自动读取测试运行器）
- P5: 全量 pytest（分片 unit/regression/integration 按项目惯例，注意资源密集型串行）
- P5_consistency: worktree 自己的 `check-protocol-consistency.py --strict-errors-only`
- P5_shellcheck: `shellcheck -S warning agate/scripts/*.sh`（本次无新 .sh，防回归）
- P5_ruff: `~/.venvs/agate-dev/bin/ruff check agate/scripts/`
- P5_count_tests: `bash agate/tests/scripts/count-tests.sh`
- 每个 key 独立声明（禁 `&&` 链），`{key}_timeout_seconds` 按三档基准表（单元 120s /
  构建 600s；全量 pytest 分片按项目实测耗时声明）

### F. 评审与编排（主 Agent 执行，architect 无需动作）
- C8 映射：domains=[backend] + risk_level=high → plan-eng-review（去重后单角色，
  直接产出 P2-review.md）
- 你的 dispatch_plan 如声明，mode 应为 single 或 serial（单脚本 + 资源密集型 P5 串行）
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
