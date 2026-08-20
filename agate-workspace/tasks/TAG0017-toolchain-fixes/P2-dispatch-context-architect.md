---
phase: P2
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0017-toolchain-fixes
role: architect
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
把 P1-requirements.md 的 12 条 BDD（4 个功能分组，覆盖 DEBT0010/11/12/14/15）转化为可实现的技术方案，产出 P2-design.md：候选方案 + 影响面梳理 + gate_commands 固化 + files_to_read 导航 + minimal_validation。

### 约束
1. **双工作区纪律**：本次会话在 worktree（`/home/kity/oclab/agate/.worktrees/agate-TAG0017`）执行，只读写 worktree 内文件；不得改动主 checkout（`/home/kity/oclab/agate`）或 `~/.agate`。
2. **回归基线不可破**：950 pytest 全绿 + `check-protocol-consistency.py --strict` 0 ERROR 是回归底线。
3. **功能分组 1（DEBT0010 + RM-AG0028/DEBT0015）必须整体设计**：P1 已把这两条 issue 归并为同一功能分组，核心边界是"`gate_commands` 是真正被执行的机制，`env_constraints` 是声明性字段（仅信息注入）"。方案设计时不能分开两次设计导致口径冲突——4 个解析脚本的修复方式（是否抽共享判据函数到 `agate_common.py`，还是各自内联修复 + grep 断言审计测试防第五处，P1 已声明两种方式都可，由你判断）与 `env_constraints` 语义边界文档化（P2-design.md「gate_commands 声明」节 + `architect.md` 角色文件 + P4 卡片「自查≠gate」节）要在同一节里统一表述。
4. **DEBT0011（功能分组 2）**：命名模板改动（`agate-alignment-review-{date}.md` → 补任务标识）+ `protocol-alignment-review.md` 角色文件的"写入前检查目标路径"逻辑，两处改动点要在方案里明确写清楚新命名规则的具体格式（如 `agate-alignment-review-{date}-{task_id}.md`）。
5. **DEBT0012（功能分组 3）**：P1 待确认清单已把"具体修复路径"留给你决定——(a) 只调整 P2 卡片 `gate_commands` 声明指引（不推荐 `--strict` 放 `&&` 链路中间）/ (b) `check-protocol-consistency.py` 新增独立 CLI 模式（如 `--strict-errors-only`，仅 ERROR 非零、WARNING-only 打印提示但 exit 0）/ (c) 两者都做。选定后写清理由，并在你自己产出的本任务 `gate_commands` 声明里**以身作则**——不要把 `--strict` 放进 `&&` 链路中间（这正是本任务要修复的反模式，若你自己的 gate_commands 声明踩了同一个坑，会被 P4/P5 直接复现问题）。
6. **DEBT0014（功能分组 4）**：P1 待确认清单已把"Store 占位符识别阈值"留给你决定——具体判据（exit code 49 / stderr 内容特征字符串 / 两者结合）需要写清楚，并说明为何选这个判据（可读 platform-notes.md 现有 Windows 已知限制条目、DEBT0014 相关 issue 描述里"exec 时 Store 占位符非交互模式直接 exit 49"这条线索）。**验证方式必须诚实**：本环境是 Linux，无法真实触发 Windows Store 占位符的 exit 49，`minimal_validation` 字段要么做"读代码验证 + 构造模拟 stub 脚本验证判据逻辑"，要么明确声明该假设无法在本环境验证、依赖 CI matrix 兜底，不能声称已实测。
7. **domains 沿用 P1 声明**（`[protocol-docs, gate-scripts]`），若你判断需要调整（如细分为不同粒度），需说明与 P1 声明的差异理由。`ui_affected: false`（无用户可见 UI/交互面，P1 已确认）。
8. **风险与工作量**：改动跨越 4 个 Python 解析脚本 + 3 个 shell 薄壳 + 至少 4 处协议 Markdown 文档（`SELF-GATE.md`/`phase-cards/P2-design.md`/`assets/execution-roles/architect.md`/`phase-cards/P4-implementation.md`/`platform-notes.md`/`AGENTS.md`）+ 可能的共享判据函数（`agate_common.py`）——产出文件数明显 >6，按「派发编排机制」工作量五维评估大概率落在 high 档，**必须在 frontmatter 声明 `dispatch_plan:`**（拆批方案，覆盖后续 P4 实现阶段怎么按"文件→改动"批次拆分，呼应 P1 已确认的"五条 issue 域重叠，按文件→改动归并"原则，批次边界应与 P1 的 4 个功能分组对齐，避免同一文件被两个批次各改一次）。
9. **`gate_commands` 声明**：本任务 P3/P5 验证命令固定为 `python3 -m pytest agate/tests/`（P3 走既有 `AGATE_TDD_TIMEOUT` 机制，不声明 `_timeout_seconds`）+ `python3 agate/scripts/check-protocol-consistency.py --strict`（P2-design.md 声明层面单条命令，不与其他命令用 `&&` 拼接在同一 key 里，避免自我复现 DEBT0012）+ `bash agate/tests/scripts/count-tests.sh` + `shellcheck -S warning agate/scripts/*.sh`，均需要独立 key 声明（如 `P5`/`P5_consistency`/`P5_count_tests`/`P5_shellcheck`），供主 Agent 分别执行分别判断，不整体拼一条链路。

### 上游关联
P1 analyst 首轮摘要：需求基线已建立，12 条 BDD（4 功能分组归并 5 条 issue），0 个待确认项，1 处轻微 P0_STALE 已记录（P0-brief task 字段计数漂移，非阻塞）。
requirements-review 复评轮摘要：approved——首轮 needs-revision（第 3.3/3.4 节同类扫描计数与实际枚举不符），analyst 订正后复核通过，其余内容（BDD 结构、隐含需求覆盖、裁剪合理性、P1 纯净性）全程未提出异议。

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0017-toolchain-fixes/P1-requirements.md（需求基线，12 条 BDD + 4 功能分组 + 同类扫描结论，本阶段的主要输入）
- {AGATE_WORKSPACE}/tasks/TAG0017-toolchain-fixes/P0-brief.md（环境约束、已知风险）
- 需读取的现有代码（供影响面梳理"改什么/不改什么/风险在哪"引用具体行号）：
  - agate/scripts/agate-read-gate-commands.py（DEBT0010，约 L31）
  - agate/scripts/agate-gate-missing-cmds.py（DEBT0010，约 L20）
  - agate/scripts/agate-gate-p5-count.py（DEBT0010，约 L23）
  - agate/scripts/agate-read-p5-commands.py（DEBT0010，约 L29）
  - agate/scripts/agate_common.py（可选抽共享判据函数的落点）
  - agate/SELF-GATE.md（DEBT0011 命名模板定义）
  - agate/assets/review-roles/protocol-alignment-review.md（DEBT0011 消费引导，约 L118）
  - agate/scripts/check-protocol-consistency.py（DEBT0012，main() 尾部，约 L1079 附近 `--strict` flag 定义）
  - agate/scripts/pre-commit-gate.sh / commit-msg-self-gate.sh / pre-push-gate.sh（DEBT0014，约 L11-15 探测循环）
  - agate/scripts/agate-extract-context.py（DEBT0015，约 L107-109）
  - agate/phase-cards/P2-design.md（本文件自身——DEBT0010/DEBT0015 的 gate_commands 声明规则节，需要新增边界说明）
  - agate/phase-cards/P4-implementation.md（DEBT0015 的"自查≠gate"节，需要新增 deploy 类约束提醒）
  - agate/platform-notes.md（DEBT0014 的"已知限制（Windows 原生）"表插入点，约 L152）
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
- 环境：worktree 基线已验证（950 pytest 全绿 + consistency 0 ERROR --strict）
- 任务目录：{AGATE_WORKSPACE}/tasks/TAG0017-toolchain-fixes/
</objective_info>
