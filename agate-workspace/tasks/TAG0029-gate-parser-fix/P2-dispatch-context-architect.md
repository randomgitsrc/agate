---
phase: P2
generated_by: 主 Agent
task_id: TAG0029
role: architect
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
产出 `agate-workspace/tasks/TAG0029-gate-parser-fix/P2-design.md`——把 P1-requirements.md 的 9 条 BDD 转化为可实现的技术方案：候选方案（≥2 + 权衡 + 选择理由）+ 影响面梳理（改什么/不改什么/风险在哪，三部分写在候选方案之前）+ 四字段（packages/domains/ui_affected/gate_commands，正文+frontmatter）+ files_to_read（P4 上下文地图）+ env_constraints 确认 + minimal_validation（纯代码逻辑声明须写明依赖的内部函数/数据转换）+ 实现完成标志。

### 约束
- **范围锁定**：P1 三缺口 + out-of-scope 三条（DEBT0016/17/18→TAG0031；R2 本体判定逻辑不扩；cmdstream 引擎不动；TAG0011 bdd-8 不改断言意图）。设计中发现新隐含需求标 `[SCOPE+]`，不擅自扩大。
- **四处改动面**（packages 对应：gate-parser / tdd-judge / platform-scanner / protocol-docs）：
  1. **gate-parser**：`agate-read-gate-commands.py` L57/L66 值清洗——剥离行内注释（首个未转义 ` #`）+ 引号闭合校验；输出"纯命令"或"解析错误（exit 非 0 + stderr）"。注意 `parse_gate_commands_block` 在 `agate_common.py` L784（公共库单点，M2 防漂移先例）——本次动的是**值清洗**（解析器本地 L57/L66），不是块解析；若候选方案动公共库函数须论证不破坏 M2 单点语义 + 同文件 `agate-read-p5-commands.py` L30/L37（P1 判定本次不处理）是否受牵连。
  2. **tdd-judge**：`check-tdd-red.py` `judge_result` L87-157——exit 2（命令串本身语法错误：bash exit 2 + 语法错误文案 + 无运行器失败断言统计）新增显式分支判 exit 1（A 类），不再落末尾 red-light exit 0。须与既有 A 类分支（L110-116 Traceback/SyntaxError / L152-154 exit>=120）分区论述优先级；不改 check-gate 返回约定；语义修正类修复的 TDD 义务（先补失败测试）在 P3 承接，设计须声明红灯测试形态。
  3. **platform-scanner**：`check-platform-assumptions.py` R2（L39）——fixture 目录/文件声明豁免（绑定目录声明，禁宽匹配）+ 纳入 P3/P4 gate_commands 常驻面。注意扫描器测试文件 `agate/tests/scripts/test_check_platform_assumptions.py` 自身"必须保持干净"契约（头注释：fixture 全用 fragment 拼接，源码任何一行不出现 R1-R5 字面命中，全树扫描本文件 0 命中即 BDD-8）——豁免设计不得破坏该契约；另 cmdstream fixture `command="env python3 -m pytest"`（env 形式本就豁免）与 17 处裸 python3 的关系须在设计中说清（豁免的是哪一类、恢复的是哪一类）。
  4. **protocol-docs**：P2 卡 gate_commands 节——P3_xxx 禁止声明及其原因（BDD-6）+ 新增 CHECK/扫描面上线流程（DEBT0025：先全量扫描存量）落点。
- **候选方案诚实探索**：每处改动至少想 2 个方向再选（如值清洗：解析器内剥离 vs 上游文档规范约束 + 解析器 fail-closed；P3 收集：精确键白名单 vs 扩展 is_gate_meta_key 协议级辅助键；豁免：路径声明豁免 vs 内容标记豁免 vs 豁免清单文件）。稻草人检测：第二方案须在某些维度更好，不只是"不如方案一"。
- **影响面梳理三部分**（写在候选方案之前，有客观证据）：改什么（逐文件/函数落点 + 关联 BDD）；不改什么（P5 脚本同模式 2 处 + missing-cmds 首 token + is_gate_meta_key 其余消费方 + R2 本体 + cmdstream 引擎 + check-gate 返回约定，逐条理由）；风险在哪（S-4 YAML 对账：动 is_gate_meta_key 判据须同步 rules/ YAML，否则 consistency 红；消费链 P2/P3/P5 全量回归；fixture 豁免被真代码借用；常驻面存量命中；每条配缓解）。
- **gate_commands 固化**（P2 唯一窗口，后续不得改）：P3（TDD 红灯读取，建议 `python3 -m pytest agate/tests/ -q --tb=short` 参照 TAG0028；formatter 按需）；P5（全量三片合跑 + `-n auto`，参照 TAG0028 P5 写法，逐 key 独立不拼 `&&`；consistency 用 `--strict-errors-only`；shellcheck 与 CI 同口径；count-tests；扫描器常驻条目 BDD-9；timeout_seconds per-key 三档基准）；P5_e2e 不适用（ui_affected=false，P1 已定 backend 无前端面）。
- **frontmatter 机器字段**：phase=P2, task_id=TAG0029, type=design, parent=P1-requirements.md, trace_id=TAG0029-P2-20260904（以你执行日为准）, agent=architect, status=draft；candidate_count（与正文候选数一致）；packages=[gate-parser, tdd-judge, platform-scanner, protocol-docs]（核实后定）；domains=[backend]；ui_affected=false。
- **files_to_read**：只列实现确实需要参考的文件（改造对象 3 脚本 + agate_common 相关函数行号范围 + S-4 校验脚本 + rules YAML + P2 卡 gate_commands 节 + 扫描器测试契约文件 + DEBT0023/0027 条目），大文件标行号，不列大杂烩。
- **minimal_validation**：预期"纯代码逻辑，无外部系统依赖"（写明依赖的内部函数：parse_gate_commands_block / is_gate_meta_key / run_test_with_formatter / judge_result / R2 正则 + 数据转换：gate_commands 块→JSON / 测试输出→JSON→exit 码 / 扫描命中行）。若设计中出现外部行为依赖（如 bash exit 2 语义），须做最小验证（一条 `bash -c` 实测）并记录 result。
- **dispatch_plan**：本任务四处改动同源耦合（同一解析器消费链），建议 mode=single（单发串行实现）；若主张拆批须按 architect.md 批次设计硬规则论证。你定，我只要求理由自洽。
- 返回前跑 `python3 agate/scripts/check-frontmatter.py` 自检（worktree 根），非 0 先修正再返回。
</dispatch_guide>

### 上游关联
- P1-requirements.md 已 approved（9 条 BDD：BDD-1~2 值清洗 / BDD-3 judge / BDD-4~6 P3 收集 / BDD-7~9 扫描器；risk_level=high；phases 全量；domains=[backend]；同类扫描 8 项判定；时效性无漂移；[NO_NEED_CONFIRM]）。
- P1-review.md status=approved（agent=requirements-review；三易错点坐实；2 条非阻塞建议：BDD-3 文案可枚举典型串；H3/H6 动公共判据须回写 [BASELINE_CHANGE]）。
- `.state.yaml` phase=P1（P2 推进随 P2 产出 commit 一起，不单独推进）。

### 输入文件
- `agate-workspace/tasks/TAG0029-gate-parser-fix/P1-requirements.md`（需求基线 + 9 条 BDD + 同类扫描结论——**P2 主要输入**）
- `agate-workspace/tasks/TAG0029-gate-parser-fix/P0-brief.md`（scope/out-of-scope/约束——范围边界）
- `agate/scripts/agate-read-gate-commands.py`（改造对象 ①，70 行——精读）
- `agate/scripts/check-tdd-red.py`（改造对象 ②，judge_result L87-157——精读）
- `agate/scripts/check-platform-assumptions.py`（改造对象 ③，R2 L39 + 豁免函数 L46-93——精读）
- `agate/scripts/agate_common.py`（is_gate_meta_key L79-87；parse_gate_commands_block L784-795；is_legal_gate_key L682-693——按需读相关函数）
- `agate-workspace/debt/tech-debt.md`（DEBT0023 L814-841 / DEBT0027 L910-932 closure_criteria 原文——必读）
- `agate/phase-cards/P2-design.md`（worktree 本体：gate_commands 节为 BDD-6 落点——核对改动面表述）
- `agate/tests/scripts/test_check_platform_assumptions.py`（头注释"保持干净"契约——必读前 60 行）
- `agate-workspace/tasks/TAG0028-subagent-liveness-self-dispatch/P2-design.md`（§4 gate_commands 固化范例：P3/P5 写法 + timeout 三档 + 逐 key 独立——参照，不复制）

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
- worktree 根：`/home/kity/oclab/agateon/.worktrees/agate-TAG0029`；分支 `feat/TAG0029-gate-parser-fix`；hook 指向 `~/.agate` 稳定版。
- 已核实查证（主 Agent 实测，供交叉核对）：
  - 值清洗 `strip(chr(34))` 5 处：read-gate-commands L57/L66（本次处理）/ read-p5-commands L30/L37（P1 判定不处理）/ gate-missing-cmds L24（不处理，首 token 检测不经 bash -c）。
  - `startswith("P3")` 仅 read-gate-commands L60 一处；`is_gate_meta_key` 消费方 5 脚本 + S-4 校验 + rules YAML。
  - R2 正则全仓唯一（check-platform-assumptions.py L39）；cmdstream IR fixture 含 `command="env python3 -m pytest"`（env 形式已豁免）；扫描器测试文件用 fragment 拼接避字面命中（_PY="python"+_VER="3" 等）。
  - judge_result：exit 2 无显式分支→末尾 exit 0（L156-157）；既有 A 类分支 L110-116/L152-154（运行器正常退出路径）。
  - P2 卡 gate_commands 节：worktree `agate/phase-cards/P2-design.md` L125-180（含 timeout 三档 + 反 `&&` + env_constraints 边界）。
- C8 评审映射（P1 domains=[backend] + risk=high）：plan-eng-review 1 个（去重后单评审，无需组长汇总，直接产出 P2-review.md）。
- **P3 辅助键存量证据（主 Agent 已补 grep，2026-09-04，你直接引用，无需重扫）**：
  - 全仓 `P3_\w+` 声明键仅三类：`P3_formatter`（多任务通用，元键豁免）/ `P3_timeout_seconds`（TAG0016/24，元键豁免，DEBT0010 已修）/ `P3_e2e`（仅 task-files.md 样例 + TAG0012 BDD-21 验收样例，`_e2e` 后缀非元键但 ui 任务 E2E 形态）。
  - 真实任务 P2-design.md 从未声明过 `P3_xxx` 检测键——TAG0026（"无 P3_xxx 检测命令键"R7 + P7 逐键核对）/ TAG0027（P8 确认无关）/ TAG0028（§4 无 P3_xxx）全部靠约定规避；DEBT0023 登记的"未来任务声明 P3_xxx 辅助检测键被当测试命令执行"迄今是**潜在风险**，无真实命中实例。
  - 收紧方案的关键推论：精确键（裸 `P3`）+ 白名单（`_formatter`/`_timeout_seconds`/`_e2e` 三后缀）已覆盖全仓存量合法用法——`P3_js`/`P3_html`（TAG0009/TAG0011 多栈形态）是历史形态，当前 pytest 单栈任务无此用法；若候选方案选白名单，须论证历史多栈形态是否保留（P1 同类扫描 #5 要求）。
  - 另：`P3_js → both run`（TAG0009 TDD.F10）证明收集侧曾有意支持多 P3* 命令键——收紧为精确键是**语义变更**，不是纯收紧，设计须显式声明此取舍。
- SELF-GATE 预告：本任务改 `agate/scripts/*` + `agate/phase-cards/P2-design.md` 触发 SELF-GATE——P2 commit message 须含 `self-gate-review:` 或 `self-gate-skip:`（commit 时处理，设计阶段先知晓）。
- 注：该文件禁止包含 verdict 预判（provenance 审计要求）。
</objective_info>
