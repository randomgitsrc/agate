# P2-dispatch-context-architect — TAG0022 方案设计

> 派发对象：architect（P2 方案设计）。这是本轮的强制指令，不是参考信息。
> 任务目录：`{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/`

## 目标

产出 `P2-design.md`（方案设计 + 实现导航）：
- **影响面梳理**（强制节，写在候选方案之前）：改什么 / 不改什么 / 风险在哪
- **候选方案 ≥2 + 权衡 + 选择理由**（`candidate_count` 必填；若 `design_trivial`/`follows_existing_pattern` 可 1 个，但须附理由——本任务改动面大，预计需要真候选方案）
- 四字段：`packages` / `domains` / `ui_affected` / `gate_commands`
- `dispatch_plan` 机器字段（high 复杂度**必须拆分**——五子项应拆批，mode ∈ 静态批/并行等；批 id + complexity；0038/0039 必须错开文件/批次）
- `files_to_read`（P4 上下文地图）、`env_constraints`、`minimal_validation`
- 完成标准（"做到什么程度算完成"，供 P3/P5 使用）

## 输入文件（逐一读，每读完追加 progress）

1. `{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/P1-requirements.md`（**主要输入**：BDD-1..10 + §4 四组扫描 + §5 范围/决策 + §7 SUGGEST）
2. `{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/P1-review.md`（评审结论 + 非阻塞观察 N1/N2/N3，**P2 须闭环**）
3. `{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/P0-brief.md`
4. `/home/kity/oclab/dsh-workspace/agate-research/tag0019-21-analysis.md`（证据基准）
5. `{project_root}/HANDOFF-TAG0022.md`（范围/纪律/验收锚/分批纪律）
6. `{agate_root}/phase-cards/P2-design.md`（本阶段卡片）与 `{agate_root}/assets/execution-roles/architect.md`（角色定义）

## 必读的实现现状文件（设计方案前必须读，不凭想象设计）

- `{project_root}/agate/scripts/check-gate.py`（**RM-AG0038 迁移对象**——协议规则类 md 解析点，P1 §4.2 六组 A-F 的分组清单）
- `{project_root}/agate/scripts/agate-md-field-get.py` + `{project_root}/agate/rules/*.yaml` + `{project_root}/agate/rules/schema/*.json` + `{project_root}/agate/scripts/check-structure-consistency.py`（**已迁移模式参照**：gate_commands 族如何经 agate-md-field-get 迁到 YAML、S-1~S-6 如何工作——M2 迁移须对齐此模式）
- `{project_root}/agate/scripts/check-routing.py`（ceremony 校验现状，RM-AG0040 已知边界）
- `{project_root}/.github/workflows/protocol-tests.yml`（ruff job，`protocol-tests.yml:106-116`）
- `{project_root}/agate/scripts/pre-commit-gate.py`（judge 链 2i.1 现状；0039 只加 P1 校验点，不动 P6.5 链）
- `{project_root}/agate/state-machine.md`（L440-448 judge 块模板 + L442-443 软强制源头）
- `{project_root}/agate/phase-cards/P1-requirements.md`（0039 的 P1 卡模板语义更新面）与 `{project_root}/agate/phase-cards/P6-acceptance.md`（judge 相关节）
- 测试现状：`{project_root}/agate/tests/unit/test_check_routing.py`（test_bdd_7）与 `{project_root}/agate/tests/unit/test_env_adapt_docs.py`（test_bdd_25，RM-AG0041 改造对象）；`{project_root}/agate/tests/unit/test_check_gate.py`（judge 三态用例 L2628/2636/2666，0039 新增用例挂靠处）；`{project_root}/agate/tests/conftest.py`（fixture 构造方式，0038 迁移兼容面）

## 约束（硬约束，违反即评审打回）

1. **五个子项验收锚**（P1 BDD-1..10 为验收口径，方案设计不得改 BDD 语义）：
   - RM-AG0037（BDD-1/2）：实现侧 = CI workflow 稳定 ruff job name + 文档化 required check 配置步骤（UPGRADING/AGENTS）；**禁止**把"设 required check"当实现侧动作（D1）
   - RM-AG0038（BDD-3/4/5）：check-gate.py 协议规则类 md 解析清零（P1 §4.2 A/B/C/D 组→结构化/YAML；E/F 组不计入，D2）+ S-1~S-6 收紧为"YAML 权威、md 禁止承载可判定规则"。**给出逐点映射清单**（哪个 md 解析点 → YAML 哪个字段/读取器）+ 既有测试兼容策略（fixture 对账桥接，H10）
   - RM-AG0039（BDD-6/7）：check-gate.py P1 分支新增 judge 校验（机制后新任务缺 `judge.enabled: true` → 拦截），历史任务（无 judge 块）跳过；state-machine.md:442-443 模板语义更新为"机制后新任务必须含 judge.enabled: true"；P1 卡同步。**校验强度 P2 冻结**（评审 N1：推荐 fail-closed exit≥1，对齐 gate_p65/缺失必填字段惯例——你须给结论与理由）
   - RM-AG0040（BDD-8）：交付"实证执行计划 + 触发条件"（M3 四要素：评审轮数指标/真实发现数指标/TAG0018 基线值/不达标决策规则 + 触发条件），落 P2-design.md 或独立附件；不改 ceremony 机制本身（D4）
   - RM-AG0041（BDD-9/10）：test_bdd_7/25 改探测 git 上下文 / 强制仓库外 basetemp（或按平台分支断言），不引入 Unix 假设（H5）
2. **分批纪律（D3）**：0038（check-gate.py 规则读取迁移）与 0039（check-gate.py P1 judge 校验）同触 check-gate.py——`dispatch_plan` 批表必须错开文件/改动块，P3/P4 每批独立可验证；其余子项（0037 workflow、0040 计划、0041 测试）按影响面归批
3. **N2 闭环**：对 `dsh-workspace/ptmp` 作为仓库外 basetemp 的**写可性做实证**（若本沙箱写面仅 worktree，须另选/冻结权威仓库外 basetemp 路径或调整 BDD-9 的执行口径——在 P2 给出结论并落盘，P5 据此实跑）
4. **N3 闭环**：count-tests 基线冻结为 **1202**（P1 §H7，避免 P6 判据漂移）
5. **环境**：Linux；/tmp 只读（pytest `--basetemp=<可写目录> -p no:cacheprovider`）；ruff `~/.venvs/agate-dev/bin/ruff`（0.16.4）；双工作区纪律（改造=worktree `agate/`，稳定版 `~/.agate` 只读，consistency 用 worktree 自己的）
6. **SELF-GATE**：本任务改动面（CI/check-gate/state-machine/P6 卡/P1 卡/测试）触发 self-gate——P2 设计须在"完成标准"或隐含节声明后续 commit 的 self-gate 处理纪律（含一次 protocol-alignment-review 的可行性安排）
7. **P1 基线保护**：设计中发现新隐含需求 → 标 `[SCOPE+]`，不擅改 BDD

## gate_commands 声明（P2 固化，后续不可改）

在 P2-design.md 输出 `gate_commands:`，至少声明：
- `P3`: pytest 运行器（verbose 模式供 check-tdd-red 读取）
- `P5`: `python3 -m pytest agate/tests/ -q -p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp`（若 N2 实证改路径，以实证结论为准）
- `P5_consistency`: `python3 agate/scripts/check-protocol-consistency.py --strict-errors-only`（用 worktree 自己的）
- `P5_structure`: `python3 agate/scripts/check-structure-consistency.py`（0038 涉及 S-1~S-6 收紧时）
- `P5_ruff`: `~/.venvs/agate-dev/bin/ruff check agate/`
- `P5_count`: `bash agate/tests/scripts/count-tests.sh`
- 长命令声明 `{key}_timeout_seconds`（全量 pytest 建议 300+）

> 各 key 独立声明，禁止 `&&` 拼接（短路反模式）。

## 影响面梳理（强制，写在候选方案之前）

覆盖 P1 §5 范围表 + §4 扫描清零：
1. 改什么（Modify）：逐文件逐小节——`.github/workflows/protocol-tests.yml`（ruff job 稳定化）、`agate/scripts/check-gate.py`（A/B/C/D 组解析点逐一映射）、`agate/rules/*.yaml`/schema（新增字段）、`agate/state-machine.md`（judge 模板语义）、`agate/phase-cards/P1-requirements.md`（0039 校验条文）、`agate/UPGRADING.md`（配置步骤+破坏性变更）、测试文件（test_check_routing/test_env_adapt_docs/test_check_gate/conftest 等）
2. 不改什么（Not Modify）：P6.5 judge 链（pre-commit 2i.1/ci-backstop/gate_p65）、ceremony 机制本体（check-routing 语义）、`.state.yaml` 读取（E 组）、git/CHANGELOG 解析（F 组）、ruff 规则集配置
3. 风险在哪（Risk）：0038/0039 同文件互扰（分批缓解）、工具链自举（用未发布 gate 判自己）、fixture 兼容回归（H10）、S-1~S-6 收紧误伤既有条文

## dispatch_plan（high 复杂度强制拆批）

五子项静态拆批建议（你可调整，但必须符合 D3 错开文件 + 单批产出 ≤3/输入 ≤3）：
- batch A（RM-AG0037）：protocol-tests.yml ruff job 稳定化 + 配置步骤文档（agate/UPGRADING.md / AGENTS.md）
- batch B（RM-AG0039）：check-gate.py P1 judge 校验 + state-machine.md + P1 卡模板语义（**与 batch C 错开：本批的 check-gate.py 改动 = P1 分支新增校验逻辑**）
- batch C（RM-AG0038）：check-gate.py A/B/C/D 解析点迁移（**本批的 check-gate.py 改动 = 规则读取层换源**）+ rules/*.yaml/schema + S-1~S-6 收紧 + 相关测试
- batch D（RM-AG0041）：test_bdd_7/25 改造
- batch E（RM-AG0040）：实证执行计划落盘（文档产出，可与任一文件批并行）
> 0039 与 0038 的 check-gate.py 改动分属不同 commit 批，批次边界写明各自文件集，批内不得交叉。

## minimal_validation（必须声明）

- N2 的 basetemp 写可性实证（写最小验证：实际在 dsh-workspace/ptmp 建临时文件测写可性 → 结论落盘）
- check-gate.py 迁移的"YAML 读取路径可打通"验证（最小脚本验证 agate-md-field-get 或等价读取器能读 rules/*.yaml 目标字段）
- 其余为纯代码/文档逻辑 → 声明"纯代码逻辑，无外部系统依赖"（写明依赖的内部函数/数据转换）

## 产出规格

`{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/P2-design.md`，Header：

---
phase: P2
task_id: TAG0022-confirmed-problems
type: design
parent: P1-requirements.md
trace_id: TAG0022-P1-20260822
status: draft
created: 2026-08-22
agent: architect
# ── v2.0 机器字段 ──
candidate_count: N
packages: [agate]
domains: [backend]
ui_affected: false
# ── 可选 ──
dispatch_plan: {mode: static-batch, parallel_limit: N, batches: [...]}
---

正文含：影响面梳理节 → 候选方案节（权衡+选择理由）→ 五子项设计节（含逐点映射清单/校验强度结论/实证计划）→ 批次设计节 → gate_commands → files_to_read → env_constraints → minimal_validation → 完成标准。

## 门槛（什么算完成）

- P2-design.md 存在且非空；candidate_count ≥2（或附理由 1）
- 影响面梳理三部分齐全（改什么/不改什么/风险在哪）
- dispatch_plan 批表满足 D3（0038/0039 错开）+ high 拆批
- gate_commands 各 key 独立声明、含 P3/P5/consistency/ruff/count + timeout_seconds
- N1（校验强度结论）/N2（basetemp 写可性实证）/N3（count-tests 基线 1202）闭环落盘
- RM-AG0038 逐点映射清单、RM-AG0040 四要素+触发条件落盘

## 分阶段落盘

每读完输入/完成关键步骤，追加写 `{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/P2-progress.md`；bash 命令一律 `timeout` 包裹。

## 返回给我

只返回两行：① 产出文件路径；② 一句话摘要（方案要点，≤40 字）。绝不返回文件全文。

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