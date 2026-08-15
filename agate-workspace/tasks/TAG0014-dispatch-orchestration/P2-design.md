---
phase: P2
task_id: TAG0014-dispatch-orchestration
type: design
parent: P1-requirements.md
trace_id: TAG0014-P2-20260816
status: draft
created: 2026-08-16
agent: architect
# ── v2.0 机器字段 ──
candidate_count: 3
packages: [agate-protocol, agate-scripts, agate-tests]
domains: [docs, scripts, tests]
ui_affected: false
---

[PROD_NOT_TOUCHED]

# P2 方案设计 — agate 派发编排机制（全阶段，TAG0014-dispatch-orchestration）

> 本文件把 P1 的 22 条 BDD 转化为可实现的技术方案。approved plan（agate-dispatch-orchestration-20260815.md）是参考输入——字段契约、6 Task 划分、验收标准已定死，本设计引用并落地，不重新发明。所有设计决策与 plan 对齐；未对齐处显式标注理由。

## 1. 候选方案与权衡

候选方案分三个设计维度展开（读取路径 / 权威节落点 / 卡片统一策略），每维度 ≥2 个候选并给出权衡与选择理由。各维度独立正交，选择理由均基于读实际代码后的验证。

### 候选方案 A：dispatch_plan 读取路径（字段契约实现）

**方案 A1（采纳）：新增 op `dispatch_plan`，check-gate 走 `_md_field_get` 子进程读取**
- 实现：`agate-md-field-get.py` 新增 `JSON_FIELDS = frozenset({"dispatch_plan"})`，`_format_value` 增 dict→`json.dumps` 分支（置顶于其它分支之前，dict/list 走 `json.dumps`，其余类型回退 `str`）；`dispatch_plan` 纳入 `KNOWN_OPS` 注册表；纳入 `_get` 的无正文回退分支（frontmatter-only，与流 B 字段同语义——正文散文里的 `dispatch_plan:` 不读取，防伪造）。check-gate.py P2 分支通过既有 `_md_field_get("dispatch_plan", p2_file)`（L115，env FILE + 子进程）读取，返回非空则 `json.loads` 后校验。
- 优点：与 pass/blocker_count/ui_affected 的既有子进程模式完全同路径，`_format_value` 有 yaml 解析 + 格式化的现成管线（L129-142），只需加一个 JSON 分支；op 层契约独立可测（`agate-md-field-get.py dispatch_plan` 直接可验证 BDD-1）；校验逻辑集中在 check-gate，语义与 P2 gate 对齐。
- 缺点：多一次子进程调用（P2 gate 已有多次 `_md_field_get`，成本可忽略）；`json.dumps` 需 `import json`（标准库，无新依赖）。
- 工作量：agate-md-field-get.py +30 行左右，check-gate.py +30 行左右。

**方案 A2：check-gate 直接正则/sed 解析 dispatch_plan（不新增 op）**
- 实现：check-gate P2 分支用 `_frontmatter_field`（L106）提取单行再正则解析；或直接内联 yaml 解析 frontmatter。
- 优点：不经 op，少一层间接。
- 缺点：`_frontmatter_field` 是单行 sed 提取（L107-112），对嵌套 flow YAML 不可用（plan Task 1 已明确"不复用"）；重复实现 yaml 解析破坏 op 工具契约单一来源；无法被 `agate-md-field-get.py` 独立测试（BDD-1 的 op 层断言失去落点）。
- 选择理由：A2 的"优点"仅是少一层调用，但其破坏 op 统一契约、失去 op 层可测性，得不偿失。A1 完全复用既有管线且被 plan 字段契约定死（"读取机制：新增 op dispatch_plan"），**采纳 A1**。

### 候选方案 B：权威节落点

**方案 B1（采纳）：dispatch-protocol.md L639「任务粒度指引」原位升级为「派发编排机制」权威节**
- 实现：保留 L639 节的既有有效规则（输入/产出数量上限 L642-643、拆分判据 L645、拆分原则 L649-654、T016/T026 教训、P7 例外 L663），在其基础上扩展：①工作量评估五维表 ②五模式定义 ③模式 4 流程 ④并行规则 ⑤全阶段适用表。外部引用（L118/L132/L211 的「任务粒度指引」字样 + task-files.md L80）跟随节改名同步。
- 优点：改动面最小（单文件单节扩展）；consistency CHECK 3 硬编码行号引用零漂移（实测 0 ERROR，见 minimal_validation）；引用点只需改措辞不需要改锚点位置。
- 缺点：权威节所在文件变大（dispatch-protocol.md 已 1253 行）；节内需要组织好层次避免阅读负担。
- 工作量：dispatch-protocol.md 单节改写 + 3 处引用措辞 + task-files.md 1 处。

**方案 B2：新建独立文件 `agate/dispatch-orchestration.md` 承载权威节**
- 实现：新文件定义全部机制，dispatch-protocol.md L639 节改为指向新文件。
- 优点：模块化，主文件不变大。
- 缺点：引入新协议文件 → `check-protocol-consistency.py` 的 PROTOCOL_FILES/PROTOCOL_DIRS 需更新（CHECK 2/3/9 扫描面变化，本任务改动面本已最大，再增一致性维护成本）；卡片/引用点全部改指新文件，锚点迁移风险高；与 plan Task 3 明确定义"把「任务粒度指引」节改写为「派发编排机制」节"冲突。
- 选择理由：plan Task 3 已定死原位改写；B2 的模块化收益被"新增协议文件 + 一致性扫描面变更"的扩散成本抵消，且属 plan 未授权变更。**采纳 B1**。

### 候选方案 C：各阶段卡片「按包拆分并行」统一策略

**方案 C1（采纳）：卡片保留阶段特定约束 + 引用权威节并行规则（plan Task 4 逐卡片核对）**
- 实现：P3/P4/P5/P6 四张卡片的「按包拆分并行」节改写为"→ 见 dispatch-protocol「派发编排机制」并行规则"+ 显式保留本阶段特定约束（P3 拆分判据 L85-88；P4 共享文件后处理 L101/104 + 基础设施隔离全组 L111-117 + 串行安全默认值 L109；P5 只读验证 + 端口/数据库/临时文件/E2E 浏览器隔离 L119-127；P6 证据并行 + 汇总 verifier 整合唯一 P6-acceptance.md L151-157）。
- 优点：阶段特定约束完整保留（plan N7 硬要求）；统一部分（上限/失败处理/共享文件）收敛到单一权威源，消灭四卡各写各的分散定义；改动是"改引用"而非"删内容"，回归风险低。
- 缺点：卡片节标题不变（避免 P6 验收锚点漂移），依赖 grep「派发编排机制」关键词定位——BDD-13 验收口径需要锚点清单（见 files_to_read 中为 P6 准备的卡片锚点清单）。
- 工作量：4 张卡片各改一节。

**方案 C2：删除卡片内并行内容，全部收敛到权威节**
- 实现：P3/P4/P5/P6 卡片删除「按包拆分并行」节，仅留一行"见权威节"。
- 优点：卡片最简。
- 缺点：阶段特定约束（P4 隔离全组、P6 证据并行、P5 端口隔离）属"每阶段不同"的信息，删除后主 Agent 在看卡片时不可见，必须翻权威节才能看到——违反"阶段卡片自包含"原则（agate/AGENTS.md）；plan N7 明确要求"完整保留阶段特定约束（N7 修复——逐卡片核对）"，C2 直接违反。
- 选择理由：C2 的"卡片最简"以丢失阶段特定约束可见性为代价，违反 plan N7 与卡片自包含原则。**采纳 C1**。

> candidate_count: 3（A/B/C 三维度各选 1，每维度均 ≥2 候选 + 权衡 + 理由）。

## 2. 影响域分析（改 / 不改 / 风险）

### 2.1 改什么（Modify）

按 P1 §3 影响面表 + approved plan File Structure 逐文件核对：

| 文件 | 改动内容 | 关联 BDD |
|------|---------|---------|
| `agate/dispatch-protocol.md` | L639 节升级为「派发编排机制」（五维评级 + 五模式 + 模式 4 流程 + 并行规则 + 全阶段适用表）；L118/L132/L211「任务粒度指引」引用措辞跟随改名；「派发 prompt 模板」内联节（L429-497）加粒度兜底约束（与 dispatch-prompt.md 同步，N6） | BDD-8~12, BDD-18 |
| `agate/phase-cards/P2-design.md` | 新增 `dispatch_plan:` 机器字段说明（frontmatter 单行 flow 样例 + 字段契约 + 与 candidate_count 同级） | BDD-17（字段来源侧） |
| `agate/phase-cards/P1-requirements.md` | 加"编排模式"引用：复杂需求（多来源/多模块）可先派侦察 subagent 再拆；合并语义（BDD 全局编号、包归属去重）在侦察产出中定义 | BDD-15 |
| `agate/phase-cards/P3-tdd.md` | L74-90 节改为引用权威节 + 保留拆分判据（L85-88） | BDD-13 |
| `agate/phase-cards/P4-implementation.md` | L94-117 节改为引用权威节 + 完整保留共享文件后处理/隔离全组/串行安全默认值 | BDD-13 |
| `agate/phase-cards/P5-verification.md` | L113-127 节改为引用权威节 + 保留端口/数据库/临时输出/E2E 隔离 | BDD-13 |
| `agate/phase-cards/P6-acceptance.md` | L147-157 节改为引用权威节 + 保留证据并行 + 汇总 verifier 整合唯一文件 | BDD-13 |
| `agate/phase-cards/P7-consistency.md` | L97-102「P7 输入文件数量」表述更新为"模式 1 单发 + 输入数量豁免特例"，保留原有理由 3 条 | BDD-14 |
| `agate/phase-cards/P8-release.md` | 加"多包发布可拆批（模式 2/3）"+ 合并机制（P8-release-{pkg}.md → 合并 subagent 整合唯一 P8-release.md） | BDD-16 |
| `agate/assets/execution-roles/architect.md` | 新增"批次设计"强制节（P2 方案含多个独立子任务时须输出 `dispatch_plan:`；high 复杂度必须拆分） | BDD-17 |
| `agate/assets/templates/dispatch-prompt.md` | 内联粒度兜底（产出文件 >3 或输入文件 >5 个时须分批派发或说明为何不分批）；头部保留"与协议文件保持同步、协议为权威来源"声明 | BDD-18 |
| `agate/scripts/agate-md-field-get.py` | 新增 `dispatch_plan` op（KNOWN_OPS 注册 + dict→json.dumps 分支 + frontmatter-only 无正文回退） | BDD-1, BDD-7 |
| `agate/scripts/check-gate.py` | gate_p2 分支新增 dispatch_plan 校验（mode 枚举 / parallel_limit≥1 / batch 字段 / 批数≤上限；缺字段跳过等同现状） | BDD-2~7 |
| `agate/tests/unit/test_dispatch_orchestration.py`（新建） | dispatch_plan 字段契约测试 8 条（5 正向 + 3 负向） | BDD-19 |
| `agate/tests/unit/test_agate_md_field_get.py` | 新增 dispatch_plan op 层测试 2 条（frontmatter dict→JSON；无字段→空输出）——S2 落地 | BDD-1, BDD-7 |
| `agate/tests/README.md` | 用例计数表新增 test_dispatch_orchestration.py 行 + agate-md-field-get.py 计数 14→16 | BDD-20 |
| `README.md` | version badge v0.48.0 → v0.49.0 | BDD-21（版本发布） |
| `CHANGELOG.md` | 新增 [0.49.0] 版本记录 | BDD-21 |
| `agate/UPGRADING.md` | 新增 0.49.0 章节（dispatch_plan 可选字段 + 权威节改名对既有任务的兼容性说明） | BDD-21 |

### 2.2 不改什么（Not Modify）

| 文件 | 理由 |
|------|------|
| `agate/scripts/agate-frontmatter-check.py` | **明确不改**（I2 / plan B3 方案 c）：`dispatch_plan` 不入 P2 schema。实测含 dispatch_plan 的 P2 文件 frontmatter-check exit 0（minimal_validation），不改即可保证"缺字段等同现状"。若入 schema 的 `types` 用 `str` 会因 isinstance 拦截 dict |
| `agate/scripts/check-pruning.py` / `check-p6-evidence.py` / `check-p6-provenance.py` / `check-scope-resolved.py` | 只读既有 op，新增 op 不影响其行为（P1 §3.3） |
| `agate/scripts/ci-gate-backstop.py` / `agate-summary.py` / `pre-commit-gate.py` | 调 check-gate.py 的既有分支，不改逻辑；P2 commit 时 hook 跑新增校验由 BDD-2 向后兼容断言保护 |
| `agate/scripts/*.sh`（3 个 hook 薄壳） | self-gate 触发面含 .sh 但本次不改薄壳 |
| `agate/state-machine.md` / `agate/WORKFLOW.md` | 不改。retries[Pn] 表（state-machine L369-378）已存在，并行批 retry 对齐只引用不改动 |
| `agate/tests/unit/test_check_gate.py`（既有 P2 用例） | 复用既有 fixture（`_write_p2_design` / `add_p2_candidate_count` / `add_p2_review` / `_run_gate`），不新增用例——校验逻辑的断言落在新建 test_dispatch_orchestration.py（S2 主张 op 层补 2 条，见 2.1） |
| `agate/tests/scripts/count-tests.sh` | 只运行确认不漂移 |
| `agate/loop-orchestration.md` | **待主 Agent 定夺（SUGGEST: S1）**：L215 历史记录"见 P3/P4/P5/P6 阶段卡片"建议改为"见 dispatch-protocol「派发编排机制」"。不阻塞，主 Agent 决定是否纳入 Task 4 |
| 既有测试文件（P1 §3.3 列出的一批 test_check_gate_*.py / regression/） | 全量回归确认（BDD-20），不改 |

### 2.3 风险在哪（Risk）

| 风险 | 缓解 |
|------|------|
| dispatch_plan 校验误拦既有任务（T016/T026 教训方向） | 缺字段 → op 返回空 → check-gate 完全跳过（BDD-2/7）；负向用例锁定非法值拦截行为；pre-commit hook 在 P2 commit 时跑新增校验，由 BDD-2"逐行一致"断言保护 |
| consistency CHECK 3 硬编码行号引用误报（I8） | 权威节原位改写不移动锚点；改名引用用措辞同步（L118/L132/L211 的「任务粒度指引」字样）；每改一节跑一次 consistency（plan Task 3/4/5 内嵌） |
| 卡片删分散定义后丢阶段约束（N7） | C1 方案"改引用 + 显式保留阶段特定约束"，P6 验收逐卡片 grep 锚点清单（见 files_to_read） |
| dispatch-prompt.md 与 dispatch-protocol 内联节双源漂移（I5） | BDD-18 双处断言（两文件同含粒度兜底 + dispatch-prompt.md 头部权威源声明）；N6 强制同步 |
| 并行批 retry 与 retries[Pn] 对齐破坏状态机语义（I6） | 权威节并行规则明确"默认整组计 1 次"；state-machine 不改，只引用 |
| `json.dumps` 输出中文/特殊字符 | `ensure_ascii=False` 保持可读；check-gate `json.loads` 标准库解析，与既有 `_md_field_get` 子进程返回契约一致 |
| SELF-GATE 触发（I1 / BDD-22） | 本任务改动面大（agate/*.md + scripts/*.py + phase-cards）→ 提交时 commit message 带 `self-gate-review:` 路径 + 派发 protocol-alignment-review（见 §6） |

## 3. 方案设计

### 3.1 dispatch_plan 字段契约实现（plan Task 1/2，BDD-1~7, 19）

**op 层（agate-md-field-get.py）：**
1. 新增 `import json`
2. 新增 `JSON_FIELDS = frozenset({"dispatch_plan"})`
3. `_format_value` 在现有分支之前插入：`if field in JSON_FIELDS: return json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else str(value)`
4. `_get` 的无回退集合并入 `JSON_FIELDS`（frontmatter-only，无正则回退——防止正文散文 `dispatch_plan:` 被误读，与 change_type/regression_pass 同语义）
5. `KNOWN_OPS` 并入 `JSON_FIELDS`

**gate 层（check-gate.py gate_p2）：**
1. 复用 `_md_field_get("dispatch_plan", p2_file)`（L115 子进程模式）
2. 返回空 → 跳过（BDD-2/7 向后兼容）
3. 非空 → `json.loads` 解析（解析失败同样跳过，BDD-7 不误拦）：
   - `mode` ∉ {single, static-batch, parallel, recon-then-split, serial} → stderr `GATE P2 ERROR` + return 1（BDD-3）
   - `parallel_limit` 存在且 < 1 → ERROR + return 1（BDD-4）
   - mode ∈ {static-batch, parallel} 时校验 batches：每 batch 含 `id` 且 `complexity` ∈ {low, medium, high} → 缺 → ERROR + return 1（BDD-5 子场景①）；batch 数 > parallel_limit（缺省 3）→ ERROR + return 1（BDD-6）
   - mode ∈ {single, serial, recon-then-split}：batches 不校验（可选）
4. 校验放在 candidate_count / 四字段 / P2-review 检查之后、`return 2` 之前

> 注意：P2 gate 当前 return 2（需主 Agent 自判）。dispatch_plan 校验命中 ERROR 时须返回 1 覆盖（在 return 2 之前 return 1）。

**测试层（test_dispatch_orchestration.py，新建，8 条）：** 正向 5 条（required_fields / mode_valid / batch_granularity / parallel_limit / optional 向后兼容）+ 负向 3 条（malformed_yaml / parallel_limit_zero / batch_missing_complexity）。复用 conftest fixtures（`agate_scripts` / `python_exe` / `run_cli` / `tmp_path`），平台无关（探测 `python_exe` 不裸 python3）。

### 3.2 dispatch-protocol「派发编排机制」权威节（plan Task 3，BDD-8~12）

L639 节升级为「派发编排机制」，五小节：

1. **工作量评估**：五维评级表（产出规模 / 输入规模 / 改动性质 / 耦合度 / 认知负荷），每维 low/medium/high 描述 + 综合定级规则
2. **五模式编排**：模式 1 单发 / 模式 2 静态拆批 / 模式 3 并行 / 模式 4 先理解后拆 / 模式 5 串行链，每模式"何时用 + 流程"两部分
3. **模式 4 流程**（重点新增）：①侦察 subagent 读全貌产出拆分方案（含合并语义：BDD 全局编号、包归属去重，与 P1 卡片 BDD-15 联动）→ ②按方案派执行 subagent（并行或串行）→ ③合并（轻量拼装由主 Agent/单 subagent；重量整合派整合 subagent）。含可运行的文档样例（consistency CHECK 2 校验样例引用路径存在）
4. **并行规则**：①并行上限默认 3（`dispatch_plan.parallel_limit` 可覆盖）②失败批 retry 与 state-machine retries[Pn] 对齐，默认整组计 1 次 ③共享文件统一后处理（原 P4 约束推广全阶段，**P6 例外：走自身汇总 verifier**）
5. **全阶段适用表**：P1-P8 每阶段编排模式参考——P1 单发/复杂可先理解后拆、P2 = 单发 + dispatch_plan 产出（非 P2 自身拆分）、P3/P4/P5/P6 按包并行（引用本规则）、P7 = 模式 1 单发 + 输入豁免特例（非串行链）、P8 = 多包可拆批 + 合并机制

保留既有有效规则（输入/产出数量上限、拆分判据、T016/T026 教训、P7 例外、状态机不变原则 L654）。

### 3.3 各阶段卡片统一引用（plan Task 4，BDD-13~16）

- P3/P4/P5/P6：C1 方案（见 §1 候选方案 C），节标题保留，正文改"→ 见 dispatch-protocol「派发编排机制」并行规则" + 阶段特定约束原样保留
- P7：L97-102 表述更新为"模式 1 单发 + 输入数量豁免特例"，保留"跨文件一致性需要全部源文件同时可见"理由
- P1（卡片）：加侦察 subagent 引用 + 合并语义定义
- P8：加多包拆批（模式 2/3）+ 合并机制（多 releaser 并行各写 P8-release-{pkg}.md → 主 Agent 派合并 subagent 整合唯一 P8-release.md）

### 3.4 architect.md + 派发模板（plan Task 5，BDD-17~18）

- architect.md：新增"批次设计"强制节——P2 方案含多个独立子任务时，P2-design.md 必须输出 `dispatch_plan:`（模式 + 批次表 + 并行上限）；high 复杂度必须拆分；批次粒度受工作量评估约束
- dispatch-prompt.md：粒度兜底——"产出文件 >3 或输入 >5 个时，必须分批派发或明确说明为何不分批"；同步写入 dispatch-protocol「派发 prompt 模板」内联节（N6，双源一致）

### 3.5 测试与回归（plan Task 6，BDD-19~21）

- P3：先写 test_dispatch_orchestration.py 8 条 + test_agate_md_field_get.py 2 条（S2），确认红灯
- P4：实现 op + gate 校验 + 文档改动
- P5：全量 pytest + consistency --strict + count-tests.sh
- 用例数：改造前实测基线 770（2026-08-16 扫描，见 minimal_validation）→ 新增 8+2 = 10 条 → 目标 ≥ 780（BDD-20 以 P4 实现前实测为准，此值仅记录当前基线供参考）

### 3.6 SELF-GATE（BDD-22）

按 SELF-GATE.md 变更触发模式：commit message 含 `self-gate-review:` 路径（引用协议对齐审查报告），P7 阶段派发 protocol-alignment-review（`agate/assets/review-roles/protocol-alignment-review.md`），产出 `docs/reviews/agate-alignment-review-{date}.md`；MISALIGNED 必须修复，NEEDS_HUMAN_REVIEW 附 `[HUMAN_CONFIRMED: ...]`。

## 4. BDD 覆盖映射（22 条全量）

| BDD | 设计方案落点 |
|-----|------------|
| BDD-1 | §3.1 op 层：JSON_FIELDS + json.dumps + KNOWN_OPS 注册 |
| BDD-2 | §3.1 gate 层：op 返回空跳过；test_dispatch_plan_optional 含"等同现状"断言 |
| BDD-3 | §3.1 gate 层：mode 枚举校验 + ERROR return 1 |
| BDD-4 | §3.1 gate 层：parallel_limit < 1 拦截 |
| BDD-5 | §3.1 gate 层：batch 缺 complexity / complexity 非法 → ERROR（P6 分双子场景各验一次） |
| BDD-6 | §3.1 gate 层：batch 数 > parallel_limit（缺省 3）拦截 |
| BDD-7 | §3.1 op 层 + gate 层：frontmatter-only 无回退 + json.loads 失败跳过，不崩溃不误拦 |
| BDD-8 | §3.2 工作量评估五维表 + low/medium/high |
| BDD-9 | §3.2 五模式定义（何时用 + 流程） |
| BDD-10 | §3.2 模式 4 三步流程 + 文档样例 |
| BDD-11 | §3.2 并行规则三要素（上限 3 / retry 对齐 / 共享文件 P6 例外） |
| BDD-12 | §3.2 全阶段适用表 P1-P8 + P2/P7/P8 特例 |
| BDD-13 | §3.3 四卡引用权威节 + 阶段特定约束保留（§2.1 逐卡片） |
| BDD-14 | §3.3 P7 卡片表述更新 + 原有理由保留 |
| BDD-15 | §3.3 P1 卡片侦察引用 + 合并语义定义 |
| BDD-16 | §3.3 P8 卡片多包拆批 + 合并机制 |
| BDD-17 | §3.4 architect.md 批次设计强制节 |
| BDD-18 | §3.4 dispatch-prompt.md + 协议内联节双源同步 |
| BDD-19 | §3.1 测试层：test_dispatch_orchestration.py 8 条 |
| BDD-20 | §3.5 全量 pytest + count-tests（基线 770 实测） |
| BDD-21 | §3.5 consistency 0 ERROR（CHECK 3 锚点不漂移，minimal_validation 预验证） |
| BDD-22 | §3.6 self-gate 流程（commit message + protocol-alignment-review 派发记录） |

## 5. 四字段声明

### gate_commands

```yaml
gate_commands:
  P3: "python3 -m pytest agate/tests/unit/test_dispatch_orchestration.py agate/tests/unit/test_agate_md_field_get.py -q --tb=no"
  P5: "python3 -m pytest agate/tests/ -q --tb=no"
  P5_consistency: "python3 agate/scripts/check-protocol-consistency.py --strict"
  P5_count: "bash agate/tests/scripts/count-tests.sh"
```

> P0-brief test_cmd 三件套全部纳入 P5（主命令 + 辅助命令，`_gate_p5_count` 识别 P5_* 辅助键）。P5_e2e 不需要（ui_affected: false）。

### env_constraints

```yaml
env_constraints:
  debug_env: "Linux；Windows 靠 CI matrix（pytest -m windows_smoke）。开发用 ~/.venvs/agate-dev/（ruff）；运行 agate 只需系统 python3 + pyyaml。本环境 pytest 9.0.3"
  isolation_check: "新增测试遵守平台无关原则（探测 python_exe 不裸 python3、用 conftest fixtures、无 /tmp 依赖）；Linux 全量覆盖，Windows 只跑 windows_smoke"
  consistency_strict: "P5 用 --strict（WARNING 也阻断），CI 用默认；worktree 跑 check-protocol-consistency.py（0 ERROR 当前已实测）"
```

### files_to_read

```yaml
files_to_read:
  - path: agate/scripts/agate-md-field-get.py
    why: op 新增点：_format_value L129-142 插 JSON 分支、_get L183-191 并入 frontmatter-only、KNOWN_OPS L194-198 注册
  - path: agate/scripts/check-gate.py:291-366
    why: gate_p2 分支，dispatch_plan 校验插入位置（candidate_count L301-307 之后、return 2 之前）；_md_field_get L115 复用
  - path: agate/dispatch-protocol.md:639-663
    why: 权威节改写对象（任务粒度指引现状 + 既有有效规则）
  - path: agate/dispatch-protocol.md:429-497
    why: 「派发 prompt 模板」内联节——粒度兜底同步落点（N6）
  - path: agate/tests/conftest.py:213-227
    why: add_p2_candidate_count / add_p2_review fixture 复用模式（新建测试文件参照）
  - path: agate/tests/unit/test_check_gate.py:220-272
    why: _write_p2_design + _run_gate 的 P2 测试 fixture 模式，新建测试沿用
  - path: agate/tests/unit/test_agate_md_field_get.py:10-16
    why: _run_mdf 封装模式，新增 dispatch_plan op 测试沿用
  - path: agate/phase-cards/P4-implementation.md:94-117
    why: 卡片引用改写样板（共享文件/隔离全组/串行默认值的完整保留清单）
  - path: agate/SELF-GATE.md
    why: self-gate 派发模板（commit message self-gate-review: + protocol-alignment-review）
  # P6 verifier 的 BDD-13 逐卡片 grep 锚点清单（S3）：
  #   P3-tdd.md「按包拆分并行」节 → grep "派发编排机制" + "拆分判据"
  #   P4-implementation.md → grep "派发编排机制" + "共享文件" + "基础设施隔离" + "串行"
  #   P5-verification.md → grep "派发编排机制" + "端口" + "数据库"
  #   P6-acceptance.md → grep "派发编排机制" + "证据并行" + "汇总 verifier"
```

### minimal_validation

```yaml
minimal_validation:
  assumption: "agate-md-field-get.py 既有 yaml 解析路径能支撑新 op dispatch_plan（frontmatter flow YAML → dict → json.dumps），且 dict 值当前无 JSON 分支（plan L124/N9 引用路径成立）"
  method: |
    1. 用临时 P2-design.md（frontmatter 含 `dispatch_plan: {mode: static-batch, parallel_limit: 3, batches: [{id: B1, complexity: medium}]}`）跑 worktree 的 agate-md-field-get.py
    2. 手写 yaml.safe_load + json.dumps 复现 _read_frontmatter/_format_value 管线
    3. 手写坏 YAML（`{mode: [unclosed`）验证解析失败路径
    4. 用含 dispatch_plan 的完整 P2 文件跑 agate-frontmatter-check.py 验证 I2（不入 schema 不误拦）
    5. 跑 check-protocol-consistency.py 验证 CHECK 3 现状 0 ERROR（权威节原位改写前提）
    6. 跑 count-tests.sh 记录 P4 前基线
  result: "confirmed"
  note: |
    ① dispatch_plan 未注册 KNOWN_OPS → exit 2 "unknown op"（实测），确认 N9（注册必要性）+ BDD-1 op 层当前红灯。
    ② yaml.safe_load 对 flow dict 解析成功，json.dumps 输出合法 JSON（mode/parallel_limit/batches 齐全），json.loads round-trip 成功——BDD-1/BDD-6 的 op 输出路径可用。
    ③ 当前 _format_value 对 dict 走 str() 输出 Python repr（单引号），非 JSON——确认 I4（须加 json.dumps 分支）。
    ④ 坏 YAML → yaml.safe_load 抛 YAMLError → _read_frontmatter 返回 None → _get 走 frontmatter-only 分支输出空（不崩溃）——BDD-7 成立的前提已验证。
    ⑤ 含 dispatch_plan 的 P2 文件跑 agate-frontmatter-check.py → exit 0（不入 schema 不被 isinstance 误拦）——I2/B3 方案 c 成立。
    ⑥ check-protocol-consistency.py 当前 0 ERROR（279 WARNING 均为既有叙事文件引用），原位改写权威节的前提成立（I8）。
    ⑦ count-tests.sh 基线实测 770（pytest collect-only 口径）。
    结论：核心假设全部 confirmed，op 路径无需外部系统依赖，方案可直接进入 P3 TDD。
```

## 6. 实现完成标志

> 供 P3 测试设计 / P5 验证 / P6 验收判定"做到什么程度算完成"。

1. **op 契约完成**：`agate-md-field-get.py dispatch_plan` 对含 flow YAML 的 P2 文件输出合法 JSON（含 mode），对无字段/坏 YAML 输出空字符串 exit 0（BDD-1/7）
2. **gate 校验完成**：check-gate P2 对 mode 非法 / parallel_limit<1 / batch 缺 complexity / 批数超限 各报 `GATE P2 ERROR` + exit 1；对无字段/坏 YAML 行为等同现状 exit 2（BDD-2~7）
3. **权威节完成**：dispatch-protocol「派发编排机制」含五维评级表 + 五模式 + 模式 4 三步流程（含文档样例）+ 并行规则三要素 + 全阶段适用表（BDD-8~12）
4. **卡片统一完成**：P3/P4/P5/P6/P7/P1/P8 七卡按 §3.3 改完，阶段特定约束逐卡核对保留（BDD-13~16）
5. **模板完成**：architect.md 批次设计强制节 + dispatch-prompt.md 粒度兜底 + 协议内联节双源同步（BDD-17~18）
6. **测试完成**：test_dispatch_orchestration.py 8 条 + test_agate_md_field_get.py 2 条全绿；全量 pytest 全绿；count-tests ≥ 基线 + 10（BDD-19~20）
7. **一致性完成**：consistency --strict 0 ERROR（BDD-21）
8. **self-gate 完成**：所有协议/脚本改动 commit message 含 `self-gate-review:` 路径 + protocol-alignment-review 派发记录存在（BDD-22）
9. **发布完成**：README badge / CHANGELOG / UPGRADING 更新 + 版本 tag（P8）

## 7. [SCOPE+] 声明

> 无新增隐含需求。I1-I10 已在 P1 §2 声明，本设计全部纳入（见 BDD 映射表）。SUGGEST S1（loop-orchestration.md L215）与 S2（test_agate_md_field_get.py op 测试）主 Agent 可自行决定——S2 已纳入本设计（§2.1），S1 待定。
