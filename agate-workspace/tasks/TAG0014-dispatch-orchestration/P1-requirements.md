---
phase: P1
task_id: TAG0014-dispatch-orchestration
type: problems
parent: P0-brief.md
trace_id: TAG0014-P1-20260816
status: draft
created: 2026-08-16
agent: analyst
# ── v2.0 机器字段 ──
risk_level: high
phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]
packages: [agate-protocol, agate-scripts, agate-tests]
domains: [docs, scripts, tests]
capability_requirements:
  - need: python-runtime
    why: 跑 gate 脚本（check-gate.py / agate-md-field-get.py）、pytest 全量测试、consistency 检查
    available:
      - "系统 python3（3.12.3）+ pyyaml + pytest 9.0.3"
    status: available
  - need: grep-rg
    why: P1 同类扫描、P6 验收对协议文件内容的二进制判定（grep 锚点）
    available:
      - "rg / grep 工具"
    status: available
  - need: ruff
    why: 新增 py 测试文件的静态检查（Task 6）
    available:
      - "~/.venvs/agate-dev/bin/ruff"
    status: available
  - need: shellcheck
    why: 3 个 hook 薄壳静态分析（本次不改薄壳，仅回归确认）
    available:
      - "系统 shellcheck"
    status: available
---

[PROD_NOT_TOUCHED]

# P1 需求基线 — agate 派发编排机制（全阶段，RM-AG0016 / TAG0014-dispatch-orchestration）

> 本文件是需求基线，后续阶段（P2-P8）不应直接修改。变更需主 Agent 显式批准 + `[BASELINE_CHANGE: 理由]` 标注。

## 1. 需求复述

把 P0-brief 的原始任务（task 字段）翻译为结构化需求：

**目标**：建立统一的 subagent 派发编排机制，覆盖全阶段（P1-P8），解决"工作量高时单 subagent 过载卡死"（TAG0010 批次 0 实证：agate_common 整库 + ci-gate-backstop + 3 bats 一次派发，用户中止）。

**要交付的能力（按 P0-brief issues + approved plan 的 Goal/Architecture 整理）**：

| 能力 | 现状 | 目标 |
|------|------|------|
| 工作量评估 | 无——只有「任务粒度指引」（dispatch-protocol.md L639-663，限输入/产出数量） | dispatch-protocol 权威节含五维评级表（产出规模/输入规模/改动性质/耦合度/认知负荷）→ low/medium/high |
| 五模式编排 | 无编排模式定义 | 单发/静态拆批/并行/先理解后拆/串行链，每模式给"何时用 + 流程" |
| 并行规则 | 分散且缺：P3/P4/P5/P6 各卡片独立定义「按包拆分并行」；无并行上限、无失败处理、无共享文件统一约束 | 权威节统一：并行上限默认 3 / 失败批处理 / 共享文件统一后处理（P6 例外走自身汇总 verifier） |
| 模式 4（先理解后拆） | 无（用户扩展需求） | 侦察 subagent 读全貌产出拆分方案 → 按方案派执行（并行/串行）→ 合并（轻量拼装 / 重量整合 subagent）。全阶段适用 |
| 机器字段 | P2-design.md 无编排声明 | frontmatter 单行 flow YAML `dispatch_plan:`（mode/batches/parallel_limit），gate 可校验，缺字段向后兼容 |
| 各阶段卡片 | 分散定义 | 统一引用权威节，完整保留阶段特定约束（P5 端口隔离 / P6 证据并行 / P7 不拆分 / P8 多包拆批+合并） |
| 派发模板 / architect | 无批次设计节、无粒度兜底 | architect.md 批次设计强制节 + dispatch-prompt.md 内联粒度兜底（与协议权威源同步） |

**问题陈述**：协议对"任务该拆多细、拆完怎么派、并行怎么管"只有零散的经验描述（任务粒度指引 + 各卡片「按包拆分并行」），缺一个统一权威源；P1/P2 完全无编排机制。导致高工作量任务在 P1/P2 只能单 subagent 硬扛（过载卡死），P3-P6 的并行规则各自为政且无上限/失败处理/共享文件约束。

## 2. 隐含需求识别

> 用户没说但技术上必须做（逐条过 analyst 隐含需求清单维度：数据/前端/多端/边界/兼容）。

| # | 隐含需求 | 为什么必须 | 性质 |
|---|---------|-----------|------|
| I1 | SELF-GATE 触发路径 | 本任务改 `agate/*.md` + `agate/scripts/*.py` + phase-cards，全部命中 self-gate 触发块；commit message 须含 `self-gate-review:` 路径并派发 protocol-alignment-review（plan 验收标准 6）。验收落点：BDD-22（§4.6） | 兼容（gate 机制） |
| I2 | `dispatch_plan:` 不入 `agate-frontmatter-check.py` 的 P2 schema（plan B3 方案 c） | frontmatter-check 对 `types: str` 做 `isinstance` 校验，flow YAML dict 会被误拦（pre-commit-gate.py L313-316 拦截 commit）——不入 schema 才能保证"缺字段等同现状"向后兼容 | 兼容（避免误拦） |
| I3 | 新 op `dispatch_plan` 必须注册入 `agate-md-field-get.py` 的 `KNOWN_OPS`（plan N9） | 不注册则 `_md_field_get` 视为缺失 exit 2 → check-gate P2 静默跳过 → `test_mode_valid` 静默不报 ERROR 而红（假绿） | 边界（工具契约） |
| I4 | `agate-md-field-get.py` 须新增 dict → `json.dumps` 输出分支（plan N9） | 当前 `_format_value` 对 dict 走 `str()` Python repr（单引号），非 JSON，无法被 check-gate 的 `json.loads` 消费 | 边界（序列化） |
| I5 | dispatch-prompt.md 与 dispatch-protocol「派发 prompt 模板」节双源同步（plan N6） | dispatch-prompt.md L4 已声明"协议文件为权威来源"；若只在模板加粒度兜底、不同步协议内联节，会出现双源漂移 | 兼容（一致性） |
| I6 | 并行批 retry 预算与 state-machine.md `retries[Pn]` 对齐（plan N3） | 并行批失败后 retry 按"整组计 1 次"默认——若按每批独立计入，重试会快速耗尽 retries[Pn] MAX 上限，破坏状态机语义 | 兼容（状态机契约） |
| I7 | P6 例外：共享文件后处理走自身汇总 verifier（plan N4） | 原 P4 约束"共享文件由主 Agent 统一处理"推广到全阶段时，P6 是 self-authored gate——验收阶段主 Agent 不应介入文件处理，必须走自身汇总 verifier | 边界（self-authored gate） |
| I8 | CHECK 3（check-protocol-consistency.py 硬编码行号引用） | 权威节改名后，consistency 检查对硬编码行号/锚点的引用须同步，否则 0 ERROR 目标失败 | 兼容（CI gate） |
| I9 | 既有任务粒度指引有效规则保留 | T016/T026 教训、输入/产出数量上限、拆分原则、P7 例外是既有有效规则，改写权威节时不得丢失 | 兼容（回归保护） |
| I10 | 新增测试遵守平台无关原则 | AGENTS.md「测试约定」核心约束：不允许裸 python3（探测 `python3|python`）、用 conftest fixtures（task_dir/git_repo/run_cli/py_path），`TEST_RUNNER` mock 等 | 测试约束 |

## 3. 同类扫描影响面表（P0-brief known_risks 强制要求）

> 扫描方法：worktree `agate/` 全仓 grep。以下行号为扫描时点（v0.48.0 / main 1e57a03）。

### 3.1 「按包拆分并行」匹配点

| 位置 | 行号 | 内容 | 处置（plan Task 4） |
|------|------|------|---------------------|
| agate/phase-cards/P3-tdd.md | L74（节标题）| 按包拆分并行（条件触发，非强制）；L78-90 拆分判据 | 改为引用权威节 + 保留拆分判据（阶段特定约束） |
| agate/phase-cards/P4-implementation.md | L94（节标题）| 按包拆分并行（条件触发，需额外约束）；L101-109 共享文件约束 + 串行安全默认值；L111-117 基础设施隔离全组 | 改为引用权威节 + **完整保留**共享文件后处理/隔离全组（plan N7 逐卡片核对） |
| agate/phase-cards/P5-verification.md | L113（节标题）+ L117（正文）| P5 只读验证无代码写冲突；L121-127 端口/数据库/临时输出/E2E 浏览器隔离 | 改为引用权威节 + 保留基础设施隔离 |
| agate/phase-cards/P6-acceptance.md | L147（节标题）| 证据并行、验收文件不并行（受限模式）；L151-157 各包写 P6-evidence/{pkg}/ + 汇总 verifier 整合唯一 P6-acceptance.md + BDD 编号合集核对 | 改为引用权威节 + **完整保留**证据并行 + 汇总 verifier（plan N4/N7） |
| agate/dispatch-protocol.md | L656/L658 | 任务粒度指引内「按包拆分并行（与按产出拆分正交）」小节 + "phase card 是包级并行的权威来源" | L639 节改写后并入权威节；"权威来源"表述随权威节迁移而翻转 |
| agate/loop-orchestration.md | L215 | 历史记录（v0.22.0"执行阶段按包拆分并行已落地"，指向 P3/P4/P5/P6 卡片） | 非定义点；plan 未列。见 [SUGGEST: S1] |

### 3.2 「任务粒度指引」引用点

| 位置 | 行号 | 内容 | 处置 |
|------|------|------|------|
| agate/dispatch-protocol.md | L118 | 空返回恢复策略 d：拆分任务（见「任务粒度指引」）| 引用跟随权威节改名 |
| agate/dispatch-protocol.md | L132 | 空返回诊断：产出文件数是否超过 3——见「任务粒度指引」 | 同上 |
| agate/dispatch-protocol.md | L211 | P0-brief task 字段：写不出一句话 → 拆分——见「任务粒度指引」 | 同上 |
| agate/dispatch-protocol.md | L639 | 「任务粒度指引」节本体（权威节改写对象）| plan Task 3：升级为「派发编排机制」权威节 |
| agate/assets/templates/task-files.md | L80 | P0-brief 模板 task 字段指引（见 dispatch-protocol「任务粒度指引」）| 引用跟随改名 |

### 3.3 ~/.agate 脚本引用路径（本任务要改的 check-gate.py / agate-md-field-get.py 消费方）

| 脚本/测试文件 | 引用关系 | 影响 |
|---------------|---------|------|
| agate/scripts/check-gate.py | 调用 `agate-md-field-get.py`（L37 MD_FIELD_GET + L115 `_md_field_get` 子进程模式）| P2 分支新增 `dispatch_plan` 校验（plan Task 2） |
| agate/scripts/check-pruning.py | 调 `agate-md-field-get.py` 读 risk_level/phases（L27/31）| 不改（只读既有 op）；新增 op 不破坏 |
| agate/scripts/check-p6-evidence.py | 调 `agate-md-field-get.py ui_affected`（L152）| 不改 |
| agate/scripts/check-p6-provenance.py | 调 `agate-md-field-get.py pass/fail/ui_affected`（L251/255/284）| 不改 |
| agate/scripts/check-scope-resolved.py | 调 `agate-md-field-get.py scope_resolved`（L51）| 不改 |
| agate/scripts/ci-gate-backstop.py | 调 `check-gate.py`（L24）+ `agate-md-field-get.py`（L85 读 change_type）| 不改逻辑；新增 op 后 CI backstop 回归跑通即可 |
| agate/scripts/pre-commit-gate.py | 调 `check-gate.py P2`（L326 merge 模式）| 本任务 P2 提交时 hook 会跑新增校验——backward compatible 断言（BDD-2）保护 |
| agate/scripts/agate-summary.py | 引用 check-gate.py 路径（L23/33 drift 脚本表）| 不改 |
| agate/scripts/check-protocol-consistency.py | 多处锚点引用 check-gate.py（L449/453/526/536/581/586/591/663）| 改 check-gate.py 须保持锚点关键词（--cached/DESIGN_GAP/P7 等）不漂移 |
| agate/tests/unit/test_check_gate.py | check-gate.py P2 gate 测试（1907 行，`_write_p2_design`/`add_p2_candidate_count`/`add_p2_review`/`_run_gate` fixture 模式）| 新增 dispatch_plan 校验用例或复用 fixture（plan Task 1 改此文件？plan 列为 Modify） |
| agate/tests/unit/test_agate_md_field_get.py | agate-md-field-get.py op 测试（14 例）| 新增 dispatch_plan op 测试（plan 未显式列，但 op 契约变更须有测试，见 BDD-19） |
| agate/tests/unit/test_check_gate_p1_review.py / test_check_gate_p5_diff.py / test_check_p6_provenance.py / test_check_p6_format.py / test_ci_gate_backstop.py / test_check_retrospective.py / test_check_protocol_consistency.py / test_dispatch_context_warning.py | check-gate.py 的 P1/P5/P7/backstop/consistency 锚点测试 | 不改；全量回归确认（BDD-20） |
| agate/tests/regression/test_v060_*.py | check-gate.py P7/P8 回归 | 不改；全量回归确认 |
| agate/tests/unit/test_dispatch_orchestration.py | **新建**（plan File Structure）| dispatch_plan 字段契约测试（5 正向 + 3 负向，plan Task 1） |
| agate/tests/README.md | 用例计数表（agate-md-field-get.py 14 例 / check-gate.py 124 例行）| Task 6 更新计数 |
| agate/tests/scripts/count-tests.sh | 全树 pytest 计数 | 不修改，仅运行确认不漂移（BDD-20） |

## 4. BDD 验收条件

> 每条 BDD 独立可验证、二值判定（PASS/FAIL，无中间态）。判定方：P6 verifier 对照文件内容/命令输出。

### 4.1 dispatch_plan: 字段契约（P2 机器字段，plan Task 1/2）

#### BDD-1: dispatch_plan 支持单行 flow YAML 且 mode 为五值枚举
- Given P2-design.md frontmatter 含 `dispatch_plan:` 单行 flow YAML（如 `{mode: static-batch, parallel_limit: 3, batches: [{id: B1, complexity: medium}]}`）
- When 运行 `agate-md-field-get.py dispatch_plan`（env FILE 指向该文件）
- Then 输出为合法 JSON 字符串，且 JSON 含 `mode` 字段，`mode` ∈ {single, static-batch, parallel, recon-then-split, serial}

#### BDD-2: 无 dispatch_plan 字段时行为完全等同现状
- Given P2-design.md 不含 `dispatch_plan:` 字段
- When 运行 `check-gate.py P2 <task_dir>`
- Then 输出与"改造前 gate 输出"逐行一致（无新增 ERROR / WARNING，exit code 相同）

#### BDD-3: P2 gate 拦截非法 mode 值
- Given P2-design.md 含 `dispatch_plan: {mode: xyz}`
- When 运行 `check-gate.py P2 <task_dir>`
- Then stderr 含 GATE P2 ERROR 且 exit code 为 1

#### BDD-4: P2 gate 拦截 parallel_limit < 1
- Given P2-design.md 含 `dispatch_plan: {mode: parallel, parallel_limit: 0}`
- When 运行 `check-gate.py P2 <task_dir>`
- Then stderr 含 GATE P2 ERROR 且 exit code 为 1

#### BDD-5: P2 gate 校验 batch 必填字段与 complexity 枚举
- Given P2-design.md 含 `dispatch_plan: {mode: static-batch, batches: [{id: B1}]}`（batch 缺 complexity 或 complexity ∉ {low, medium, high}）
- When 运行 `check-gate.py P2 <task_dir>`
- Then stderr 含 GATE P2 ERROR 且 exit code 为 1
> 注：本 BDD 合并两个子场景——① batch 缺 complexity（对应 plan 负向用例 `test_dispatch_plan_batch_missing_complexity`）② complexity 非法值（对应 plan 正向粒度用例 `test_dispatch_plan_batch_granularity` 的枚举校验）。P6 验收须分别构造两子场景的 Given 各验一次，两子场景均须 PASS。

#### BDD-6: P2 gate 拦截 batch 数超过 parallel_limit
- Given P2-design.md 含 `dispatch_plan: {mode: static-batch, parallel_limit: 3, batches: [{id: B1, complexity: low}, {id: B2, complexity: low}, {id: B3, complexity: low}, {id: B4, complexity: low}]}`（4 批 > 上限 3，各批字段完整，不会先命中 BDD-5 缺字段错误路径）
- When 运行 `check-gate.py P2 <task_dir>`
- Then stderr 含 GATE P2 ERROR 且 exit code 为 1

#### BDD-7: dispatch_plan YAML 解析失败时不误拦、不崩溃
- Given P2-design.md frontmatter 含 `dispatch_plan:` 但值为不可解析 YAML
- When 运行 `check-gate.py P2 <task_dir>`
- Then 不崩溃、按缺字段处理（无新增 ERROR，行为等同现状）

### 4.2 dispatch-protocol「派发编排机制」权威节（plan Task 3）

#### BDD-8: 权威节含工作量评估方法
- Given 读取 agate/dispatch-protocol.md
- When 查找「派发编排机制」节
- Then 该节含工作量评估小节，覆盖五维评级：产出规模 / 输入规模 / 改动性质 / 耦合度 / 认知负荷，且输出 low/medium/high 分级

#### BDD-9: 权威节含五模式编排定义
- Given 读取 agate/dispatch-protocol.md 权威节
- When 查找模式定义
- Then 该节含 5 个模式（单发 / 静态拆批 / 并行 / 先理解后拆 / 串行链），每个模式含"何时用"与"流程"两部分

#### BDD-10: 模式 4（先理解后拆）流程完整
- Given 读取 agate/dispatch-protocol.md 权威节模式 4 小节
- When 检查流程结构
- Then 含三步：① 侦察 subagent 读全貌产出拆分方案 → ② 按方案派执行 subagent（并行或串行）→ ③ 合并（轻量拼装由主 Agent/单 subagent，重量整合派整合 subagent），且含可运行的文档样例

#### BDD-11: 并行规则含三要素（上限 / 失败处理 / 共享文件）
- Given 读取 agate/dispatch-protocol.md 权威节并行规则小节
- When 检查内容
- Then 含：① 并行上限（默认 3）② 失败批 retry 处理（retry 事件与 state-machine retries[Pn] 对齐，默认整组计 1 次）③ 共享文件统一后处理（P6 例外：走自身汇总 verifier）

#### BDD-12: 全阶段适用表覆盖 P1-P8
- Given 读取 agate/dispatch-protocol.md 权威节全阶段适用表
- When 检查 P1-P8 每阶段
- Then 每阶段有编排模式参考，且 P2 = 单发 + dispatch_plan 产出（非 P2 自身拆分）、P7 = 模式 1 单发 + 输入豁免特例（非串行链）、P8 = 多包可拆批且含合并机制

### 4.3 各阶段卡片统一引用（plan Task 4）

#### BDD-13: P3/P4/P5/P6 卡片「按包拆分并行」改为引用权威节且保留阶段特定约束
- Given 读取 P3-tdd.md / P4-implementation.md / P5-verification.md / P6-acceptance.md 的「按包拆分并行」节
- When 逐卡片检查
- Then 每卡片该节含对 dispatch-protocol「派发编排机制」并行规则的引用，且完整保留本阶段特定约束（P3 拆分判据 / P4 共享文件后处理 + 基础设施隔离全组 + 串行安全默认值 / P5 端口数据库临时文件隔离 / P6 证据并行 + 汇总 verifier 整合唯一 P6-acceptance.md）

#### BDD-14: P7 不拆分例外表述更新
- Given 读取 P7-consistency.md「P7 输入文件数量」节
- When 检查表述
- Then 含"模式 1 单发 + 输入数量豁免特例"表述，且"跨文件一致性需要全部源文件同时可见"的原有理由保留

#### BDD-15: P1 卡片含编排模式引用
- Given 读取 agate/phase-cards/P1-requirements.md 阶段卡片（即阶段卡片目录下的 P1-requirements.md，非任务自身同名需求基线文件）
- When 查找编排模式表述
- Then 含"复杂需求（多来源/多模块）可先派侦察 subagent 再拆"引用，且合并语义（BDD 全局编号、包归属去重）在该侦察产出中定义

#### BDD-16: P8 卡片含多包拆批与合并机制
- Given 读取 P8-release.md
- When 查找多包发布表述
- Then 含"多包发布可拆批（模式 2/3）"且定义合并机制：多 releaser 并行各写 P8-release-{pkg}.md → 主 Agent 派合并 subagent 整合唯一 P8-release.md

### 4.4 architect.md 批次设计 + 派发模板兜底（plan Task 5）

#### BDD-17: architect.md 含批次设计强制节
- Given 读取 agate/assets/execution-roles/architect.md
- When 查找批次设计相关内容
- Then 含强制节：P2 方案含多个独立子任务时，P2-design.md 必须输出 `dispatch_plan:`（模式 + 批次表 + 并行上限）；high 复杂度必须拆分

#### BDD-18: dispatch-prompt.md 粒度兜底与协议权威源同步
- Given 读取 agate/assets/templates/dispatch-prompt.md 与 agate/dispatch-protocol.md「派发 prompt 模板」节
- When 检查粒度兜底约束
- Then 两处均含"产出文件 >3 或输入文件 >5 个时，必须分批派发或明确说明为何不分批"约束，且 dispatch-prompt.md 头部保留"与协议文件保持同步、协议为权威来源"声明

### 4.5 测试与回归（plan Task 1/6）

#### BDD-19: 新增 dispatch_plan 契约测试 8 条全绿
- Given 新建 agate/tests/unit/test_dispatch_orchestration.py
- When 运行 `python3 -m pytest agate/tests/unit/test_dispatch_orchestration.py`
- Then 8 条用例全部 PASS（5 正向：必填字段/mode 枚举/batch 粒度/并行上限/可选向后兼容；3 负向：malformed YAML/parallel_limit=0/batch 缺 complexity）

#### BDD-20: 全量 pytest 全绿且用例数不漂移
- Given 完成所有协议与脚本改动
- When 运行 `python3 -m pytest agate/tests/` 与 `bash agate/tests/scripts/count-tests.sh`
- Then 全部测试通过，且 count-tests.sh 统计的用例总数 ≥ 改造前实测基线 + 8 条新增（基线 = P4 实现前 `bash agate/tests/scripts/count-tests.sh` 的实际输出值；不硬编码 plan 估算值 751+ 或 tests/README.md 的 TAG0011 基线 749）

#### BDD-21: consistency 检查 0 ERROR（CHECK 3 行号引用不误报）
- Given 完成权威节改写与卡片迁移
- When 运行 `python3 agate/scripts/check-protocol-consistency.py`
- Then 输出 0 ERROR（含 CHECK 3 硬编码行号/锚点引用同步校验通过，不因「任务粒度指引」改名误报）

### 4.6 SELF-GATE 触发（plan 验收标准 6，隐含需求 I1 落点）

#### BDD-22: 协议/脚本改动 commit 均走 self-gate-review 流程
- Given 本任务完成涉及 `agate/*.md` + `agate/scripts/*.py` + phase-cards 的改动，且该批文件已提交
- When 用 `git log` 检查该批 commit message 与派发记录
- Then 该批 commit message 均含 `self-gate-review:` 路径，且存在 protocol-alignment-review 派发记录（对应 plan 验收标准 6）

## 5. 待确认清单

[NO_NEED_CONFIRM]

> 无阻塞待确认项。方向性判断均来自已 approved plan（三轮 plan-eng-review），字段契约已定死，P1 只引用不重设计。仅下列 [SUGGEST:] 倾向项供主 Agent 采纳（均不阻塞、不涉及破坏性变更/业务方向）。

- [SUGGEST: S1] loop-orchestration.md L215 历史记录仍指向"P3/P4/P5/P6 阶段卡片"作为并行权威来源——权威节迁移后建议把该句的"见 P3/P4/P5/P6 阶段卡片"改为"见 dispatch-protocol「派发编排机制」"或补一句"（卡片现引用权威节）"。plan File Structure 未列此文件，主 Agent 可自行决定是否纳入 Task 4 范围。
- [SUGGEST: S2] plan Task 1 的 Files 仅列 test_dispatch_orchestration.py（新建），未显式列 test_agate_md_field_get.py 的 op 测试——op 契约（KNOWN_OPS 注册 + JSON 输出）变更建议在该文件补 2-3 条用例（BDD-1/BDD-7 的 op 层验证），主 Agent 可决定是否并入 Task 1。
- [SUGGEST: S3] BDD-13 的验收在 P6 需逐卡片 grep「派发编排机制」引用 + 阶段特定约束关键词，建议 P2 在 files_to_read 中为 P6 verifier 列出 4 张卡片的锚点清单，降低逐卡片核对遗漏风险。

## 6. 裁剪说明

- `phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]` — **无裁剪**。P0-brief known_risks 强制"有 approved plan ≠ 裁剪阶段，仍走完整 P0-P8"。风险声明 + 协议一致性 + SELF-GATE 要求 P7/P8 不可跳过。
- risk_level = **high**：改动面最大（dispatch-protocol 权威节 + P1-P8 全阶段卡片 + architect.md + dispatch-prompt.md + check-gate.py + agate-md-field-get.py + 测试）。触发 P2 plan-eng-review 硬规则 + P4 实现评审 + P7 双向一致性检查。
- 各阶段职责对应 plan 6 Task：P1（本文件）→ P2（Task 1/2 字段契约 + 校验设计）→ P3（Task 1 先写失败测试）→ P4（Task 2/3/4/5 实现）→ P5（Task 6 全量验证）→ P6（本 BDD 验收）→ P7（跨文件交叉核对）→ P8（协议变更发布，版本号 + CHANGELOG + UPGRADING）。

## 7. 范围声明

- `packages:`（frontmatter 已声明，正文补充归属明细）：
  - **agate-protocol**（docs）：`agate/dispatch-protocol.md`、`agate/phase-cards/P1-P8-*.md`、`agate/assets/execution-roles/architect.md`、`agate/assets/templates/dispatch-prompt.md`、`README.md`、`CHANGELOG.md`、`agate/UPGRADING.md`（可选：`agate/loop-orchestration.md`，见 S1）
  - **agate-scripts**（gate 脚本）：`agate/scripts/check-gate.py`、`agate/scripts/agate-md-field-get.py`
  - **agate-tests**（测试）：`agate/tests/unit/test_dispatch_orchestration.py`（新建）、`agate/tests/unit/test_check_gate.py`、`agate/tests/unit/test_agate_md_field_get.py`（可选 S2）、`agate/tests/README.md`
- `domains:`（frontmatter 已声明）：docs（协议文档）/ scripts（gate 脚本）/ tests（测试套件）。无 backend/frontend/mcp/security 外部系统域。

## 8. 能力需求声明

frontmatter `capability_requirements` 已声明（三态判定）：python-runtime / grep-rg / ruff / shellcheck 全部 **available**（本环境已具备，见 dispatch-context 客观查证信息：pytest 9.0.3 + 系统 python3）。无 GAP、无 supplementable。任务为文档 + Python 脚本 + 测试改造，不依赖浏览器行为/外部系统行为 → 不声明 `requires_minimal_validation`。
