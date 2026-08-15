# plan-eng-review：subagent 派发编排机制（全阶段）Implementation Plan

- **评审对象**：`agate-workspace/plans/agate-dispatch-orchestration-20260815.md`（RM-AG0016）
- **评审角色**：plan-eng-review（工程经理）
- **评审日期**：2026-08-15
- **结论**：**rejected**（2 个阻塞级问题）

---

## 架构问题（阻塞级）

### B1. Task 1 测试契约与 Task 2 实现范围不闭合，TDD 无法收尾

计划 Task 1 定义 5 个测试，其中 3 个的断言在 Task 2 的实现范围外，Task 2 完成后仍为红：

| Task 1 测试 | 断言 | Task 2 是否实现 |
|---|---|---|
| `test_dispatch_plan_required_fields` | 含 `dispatch_plan:` 时必须有 mode/batches/parallel_limit | ❌ 未实现（Task 2 只校验 mode 枚举 + parallel_limit≥1）|
| `test_dispatch_plan_mode_valid` | mode 枚举合法 | ✅ |
| `test_dispatch_plan_batch_granularity` | static-batch/parallel 下 batch 数 >1 且各 batch 复杂度 ≤ medium | ❌ 未实现 |
| `test_dispatch_plan_parallel_limit` | parallel 模式 batch 数 ≤ parallel_limit | ❌ 未实现 |
| `test_dispatch_plan_optional` | 无 `dispatch_plan:` 不报错 | ✅ |

计划 Task 2 自述"跑 pytest 确认绿"、Task 6 要求"全绿"——按当前范围 `test_dispatch_plan_required_fields` / `batch_granularity` / `parallel_limit` 三个用例无法转绿。

**建议**：二选一（需计划明确）——(a) 扩展 Task 2 实现完整五条校验（required_fields + batch 粒度 + batch 数 ≤ parallel_limit）；或 (b) 将 Task 1 测试裁剪为与 Task 2 范围一致（仅 mode 枚举 + parallel_limit≥1 + optional），把批粒度/上限校验推迟到后续任务并显式说明。**验收标准 #1/#5 与 Task 1/Task 2 的对应关系必须在计划中自洽。**

### B2. `dispatch_plan:` 字段的序列化格式与解析机制未定义，实现就绪度不足

计划 Task 2 声称"复用 `_frontmatter_field`（现有 P2 字段读取通道，check-gate.py 已有）"，但该函数（`agate/scripts/check-gate.py:106-112`）是 sed 式**单行**提取（`grep '^field:' | sed 's/^field:\s*//'`），对结构化字段（`dispatch_plan:` 下挂 mode/batches/parallel_limit 子键）只返回空串。且 `check-gate.py` 无 `import yaml`（imports 仅 os/re/shutil/subprocess/sys），无法解析嵌套 YAML。计划也没有定义 `dispatch_plan:` 的序列化形态（单行 flow YAML？多行块？frontmatter 还是正文？），只写了"frontmatter + 正文样例"。

**建议**：在计划中显式定义字段契约：
- 序列化格式（如 frontmatter 单行 flow：`dispatch_plan: {mode: static-batch, parallel_limit: 3, batches: [...]}`，或正文块 + 新 op）
- 读取机制：`_frontmatter_field` 不可用 → 需新增 `agate-md-field-get.py` op（该工具已支持 yaml）或 check-gate.py 引入 yaml 解析
- 与 `agate-frontmatter-check.py` P2 schema（`scripts/agate-frontmatter-check.py:55-66`）的关系：若字段入 frontmatter，是否同步 schema 的 migrated_keys/types

---

## 架构问题（非阻塞）

- **N1 P1/P2 的编排形态需澄清**：P2 的产物是单一 `P2-design.md`（frontmatter 四字段 + gate_commands 固化 + 设计评审针对整体），"先理解后拆"实际是 **architect 单发（模式 1，architect 兼任侦察）+ 输出 dispatch_plan 供下游**，并非把 P2 本身并行拆分。计划"P1/P2 补空白"的表述容易误导为"P2 也要拆"——P2 阶段的编排 = 单发 + dispatch_plan 产出，应显式写明。P1 复杂需求拆批的合并语义（BDD 全局编号、包归属去重）也未定义。
- **N2 P7 例外归类错误**：计划 Task 4 要求给 P7 卡片加"属于串行链特例"说明。P7 不拆分的本质是**模式 1 单发 + 输入数量豁免**（P7-consistency.md L99 跨文件对照），不是串行链（模式 5 是多批依赖串行）。应改为"模式 1 单发 + 输入豁免特例"。
- **N3 失败批 retry 与 `retries[Pn]` 计数交互未定义**：dispatch-protocol.md L683-690 规定 review/gate 重试共享 `retries[Pn]`。并行批失败后"失败批单独 retry"，一次 retry 事件如何计入阶段预算（`retries[Pn] += 1`?）计划未说明，需与 state-machine 对齐。
- **N4 共享文件后处理与 P6 汇总 verifier 的边界**：权威节"共享文件由主 Agent 统一后处理"推广到 P6 时，与 P6 卡片 L154"汇总 verifier 整合唯一 P6-acceptance.md"存在职责重叠。需写明 P6 走自身汇总 verifier（例外），不适用主 Agent 后处理。
- **N5 P8 多包拆批缺合并机制**：P8-release.md 是单一文件（bump_type/CHANGELOG/debt_check），多 releaser 并行各写一份会冲突。P8 拆批需定义合并（谁汇总、如何汇总），计划只加了"提示"。
- **N6 dispatch-prompt.md 修改未同步权威源**：`dispatch-prompt.md` 头部声明"本模板与 dispatch-protocol.md「派发 prompt 模板」节保持同步，协议文件为权威来源"（L429 附近）。计划只在模板加内联兜底，未同步 dispatch-protocol.md 内联节 → 权威源漂移风险，需在 Task 5 一并同步。
- **N7 阶段卡片保留清单不完整**：Task 4 只列了"P5 端口隔离 / P6 证据并行 / P4 共享文件"，但 P4/P5 卡片还有基础设施隔离全组（端口/数据库/环境变量/临时文件，P4-implementation.md L111-117、P5-verification.md L121-127）、P4 冲突预防的"无法确定共享改动 → 串行安全默认值"（L109）。迁移删除分散节时需逐卡片核对完整保留，避免误删。

---

## 测试缺口

- **模式 4 三阶段流程无任何测试**：roadmap RM-AG0016 验证口径明确要求"模式 4 流程有测试覆盖（侦察→执行→合并 三阶段）"，但计划 Task 1 的 5 个测试全部是 `dispatch_plan:` 字段校验，没有任何模式 4 流程用例。模式 4 是编排行为（文档/编排规则），需明确其验证方式（如一致性检查 + 文档样例自测）或补用例。
- **`dispatch_plan:` 解析的负向用例缺失**：格式错误、mode 枚举非法值、parallel_limit=0/负数、batches 结构缺复杂度字段——计划只列了 5 个正向用例，无负向路径。
- **无测试验证 P2 无 `dispatch_plan:` 时 gate 行为完全等同现状**（向后兼容回归，不只"不报错"）。

---

## 锁定决策

- **五模式枚举与用户需求对齐**：`single / static-batch / parallel / recon-then-split / serial` 完整覆盖"单发/拆批/并行/先理解后拆+合并/串行"，无遗漏形态。✓
- **`dispatch_plan:` 可选 + 缺字段不拦截（向后兼容）必要**：存量在途任务（如 TAG0001 系列）P2-design.md 均无此字段，硬校验会误拦。✓
- **并行规则组（上限默认 3、失败批单独 retry、共享文件后处理）方向正确**，与既有 P4 约束兼容。✓
- **不改状态机**：拆分不改变 phase 语义、P3-P6 gate 仍为阶段门槛命令，与 dispatch-protocol.md L654 现有规则一致。✓
- **权威节单一来源 + 阶段卡片引用 + 模板兜底**的落地结构合理。✓

---

## 结论

**rejected** —— 2 个阻塞级问题：
1. Task 1 测试契约与 Task 2 实现范围不闭合（3/5 用例无法转绿，TDD 断裂）；
2. `dispatch_plan:` 字段序列化格式与解析机制未定义（`_frontmatter_field` 对结构化字段不可用、check-gate.py 无 yaml），实现就绪度不足。

修复方向：计划中显式定义字段契约（格式 + 读取 op + frontmatter schema 同步），并统一 Task 1/Task 2/验收标准的范围对应；同时处理 N2（P7 归类）、N3（retry 预算）、N6（模板同步权威源）。修复后重新评审。

---

## 复审结论（2026-08-15）

**复审对象**：修复后计划（`agate-workspace/plans/agate-dispatch-orchestration-20260815.md`，169 行）。
**验证方式**：逐项对照上次 B1/B2/N1-N7 + 实地核对 `agate-md-field-get.py` / `check-gate.py` / `agate-frontmatter-check.py` / `check-protocol-consistency.py` / 各阶段卡片 / dispatch-protocol.md L639-663 与 L683-690 / pre-commit-gate.py L313-316 / count-tests.sh（751）。
**结论**：**rejected** —— B1/B2 主体与 N1-N7 均已修复，但 B2 修复方案自身引入 1 个新的阻塞级矛盾（见 B3）。

### 逐项核对表

| 项 | 状态 | 修复质量 |
|----|------|---------|
| **B1**（Task1↔Task2 不闭合）| ✅ 已修复 | Task 1 现为 5 正向 + 3 负向 = 8 用例，Task 2 逐条对账实现：mode 枚举（`test_mode_valid`）、parallel_limit<1 ERROR（`test_parallel_limit_zero`）、batch 含 id+complexity∈三值（`test_batch_granularity` + `test_batch_missing_complexity`）、batch 数≤parallel_limit 默认 3（`test_parallel_limit`）、模式 1/5 batches 可选（`required_fields` 弱化断言）、无字段跳过等同现状含输出对比断言（`test_optional`）、malformed YAML 不崩溃不误拦（`test_malformed_yaml`）。测试范围 ↔ 实现范围闭合，与 gate_p2 尾部 return 2 一致。 |
| **B2**（序列化格式/解析机制未定义）| ⚠️ 主体已修复，schema 同步部分引入新矛盾 | 序列化格式（frontmatter 单行 flow YAML，L51-55）、mode 枚举（L56）、读取机制（新增 op `dispatch_plan` + subprocess，明确**不复用** `_frontmatter_field`，L57——与 check-gate.py L106-112 单行 sed 判定一致，正确）、`agate-md-field-get.py` yaml 解析路径 L56/L124 属实。**但** L58 的 frontmatter schema 同步"migrated_keys/types 增加 dispatch_plan（类型 str）"与 L52 的 flow YAML dict 序列化自相矛盾 → **新阻塞 B3**。 |
| **N1**（P1/P2 编排形态误导）| ✅ 已修复 | L104 显式写明"P2 = 单发 + dispatch_plan 产出，非 P2 自身拆分"；L117 P1 拆批合并语义（BDD 全局编号、包归属去重）在 P1 侦察产出中定义。 |
| **N2**（P7 归类错误）| ✅ 已修复 | L104 + L119 改为"模式 1 单发 + 输入数量豁免特例"，非串行链；P7-consistency.md L99 实际内容与此一致。 |
| **N3**（失败批 retry 与 retries[Pn] 计数）| ✅ 已修复 | L103 定义对齐：每批独立计入 vs 整组计 1 次"二选一，默认整组计 1 次"，与 dispatch-protocol.md L683-690 retry 预算表语义衔接。默认值已定，可执行。 |
| **N4**（共享文件后处理 vs P6 汇总 verifier）| ✅ 已修复 | L103 显式"P6 例外：走自身汇总 verifier"，L118 保留"汇总 verifier 整合唯一 P6-acceptance.md"（对应 P6-acceptance.md L154 实文）。 |
| **N5**（P8 多包拆批缺合并机制）| ✅ 已修复 | L120 定义合并：多 releaser 并行各写 `P8-release-{pkg}.md` → 合并 subagent 整合唯一 `P8-release.md`。 |
| **N6**（dispatch-prompt.md 未同步权威源）| ✅ 已修复 | L106 + L132 双向：权威节与模板内联节同步写兜底约束 + dispatch-prompt.md L4 头部同步声明（实际存在）。 |
| **N7**（阶段卡片保留清单不完整）| ✅ 已修复 | L118 逐卡片核对清单含 P4 L109 串行安全默认值 + L111-117 隔离全组 + 共享文件后处理、P5 L121-127、P6 证据并行 + 汇总 verifier——已逐一实地核对存在。 |
| 上次测试缺口（模式 4 无测试/负向缺失/等同现状回归）| ✅ 已修复 | 3 条负向用例补齐；`test_dispatch_plan_optional` 含"等同现状"断言；模式 4 以文档样例 + consistency CHECK 2 引用存在性兜底（CHECK 2 = 仓库内文件引用存在，脚本中 `check_internal_refs` 属实）。 |

### 新增问题

**B3（阻塞）**：`dispatch_plan:` 字段的 frontmatter schema 类型声明与序列化格式自相矛盾，按计划实现会导致功能在 pre-commit 被自己拦截。

- 计划 L52 规定序列化格式为 frontmatter **flow YAML dict**：`dispatch_plan: {mode: static-batch, ...}`；L58 / Task 2 同时要求 `agate-frontmatter-check.py` P2 schema 的 **migrated_keys/types 增加 `dispatch_plan`（类型 `str`）**。
- 但 `agate-frontmatter-check.py` L172-175 的 `_check()` 对 `types` 中声明为 `str` 的字段做 `isinstance(value, str)` 校验——flow YAML 解析结果是 dict → 输出 `"P2-design.md:dispatch_plan: 类型错误（应为 str，实际 dict）"`。
- `pre-commit-gate.py` L313-316 对暂存的 P2 产出逐个跑 `check-frontmatter.py`，非空错误即拦截。因此**任何按计划 L52 格式写 `dispatch_plan:` 的 P2-design.md 都会在 commit 时被 pre-commit 拒绝**——计划自己的字段契约无法落地，且连带破坏 L59 的"向后兼容"承诺（凡新格式 P2-design.md 含该字段即被拦，非"缺字段等同现状"）。
- **修复方向（三选一，需在计划中定死）**：(a) schema 类型改 `dict` 并给 `_check()` 补 dict 分支（或显式声明"仅入 migrated_keys、不入 types"，避免触发类型校验）；(b) 序列化改为 frontmatter 单行**字符串**（引号包裹 JSON），此时 Task 2 的 op 读取与 `json.loads` 成立，但 L52 样例与 malformed 用例语义（YAML 解析失败）需同步改写；(c) `dispatch_plan` 完全不入 frontmatter-check schema，全部校验由 check-gate 经 op 完成（与 L57"结构校验由 op 返回 JSON 后 check-gate 做"最自洽）。三种方案均需同步更新验收标准 #1 的表述。

**N8（非阻塞）**：Task 2 L84 称读取路径"与 candidate_count 同路径"——不实。`check-gate.py` 的 candidate_count 在 gate_p2 L301-307 用**正则逐行**读取，非 subprocess；subprocess 模式（`_md_field_get`，L115-129）实际用于 P1/P6/P7 字段。机制可行，仅引用对象错误，建议改为"与 pass/blocker_count 同路径"。

**N9（非阻塞）**：op 输出 JSON 需新增序列化路径，计划未写明。`agate-md-field-get.py` 当前 `_format_value` 对 dict 走默认 `str(value)`（Python repr，单引号，非 JSON），且 `main()` L204-206 对未注册 op exit 2（`_md_field_get` 视为缺失 → gate 跳过，会导致 `test_dispatch_plan_mode_valid` 静默不报 ERROR 而红）。Task 2 需明确：`dispatch_plan` 须注册入 `KNOWN_OPS` 并新增 dict→`json.dumps` 输出路径。

**N10（非阻塞）**：Task 1 `test_dispatch_plan_parallel_limit` 描述为"parallel 模式 batch 数 ≤ parallel_limit"，Task 2 实现为"static-batch/parallel 模式"均校验——实现范围宽于测试描述，测试仍可通过，但术语不一致应统一（limit 语义本就应覆盖 static-batch，建议改测试描述为"static-batch/parallel"）。

### 复审结论

**rejected** —— B1 与 N1-N7 均已正确修复，B2 主体（格式/op/不复用 `_frontmatter_field`）修复到位；但 B2 修复的 schema 同步子项引入 **1 个新的阻塞问题（B3）**：`dispatch_plan` 的 frontmatter schema 类型 `str` 与 flow YAML dict 序列化自相矛盾，会导致含该字段的 P2-design.md 在 pre-commit 被 frontmatter-check 拦截，字段契约无法落地。

修复方向：在计划中按 B3 三选一方案定死 schema 处理方式（建议方案 (c)：不入 frontmatter-check schema，全部校验走 check-gate + op，与现有 P1/P6/P7 子进程读取模式一致），并顺带修正 N8/N9/N10。修复后可执行。

---

## 三审结论（2026-08-15）

**三审对象**：修复后计划（`agate-workspace/plans/agate-dispatch-orchestration-20260815.md`，169 行）。
**验证方式**：逐项核对 B3/N8/N9/N10 修复内容与任务描述是否一致，并实地读 `agate-md-field-get.py` / `check-gate.py` / `agate-frontmatter-check.py` / `pre-commit-gate.py` 核实机制匹配度；跑 `check-protocol-consistency.py`（0 ERROR）与 `count-tests.sh`（751，与计划"既有 751+"一致）。
**结论**：**approved** —— 4 项修复全部正确落地，无阻塞问题。新发现 4 项非阻塞备注（N11-N14），不阻断执行。

### B3/N8/N9/N10 核对表

| 项 | 修复内容 | 核实结果 |
|----|---------|---------|
| **B3**（`dispatch_plan` 入 schema 自相矛盾 → pre-commit 拦截）| 方案 c：完全不入 `agate-frontmatter-check.py` P2 schema，全部校验走 check-gate + op | ✅ 修复正确。计划 L58 显式"完全不入 schema"；Task 2 Files（L80）删去 `agate-frontmatter-check.py` 并注明"不改"；验收标准 #1（L152）同步更新为"不入 frontmatter-check schema"。核实 `agate-frontmatter-check.py` P2 schema（L55-66）migrated_keys/types 确无 `dispatch_plan`，且 `pre-commit-gate.py` L313-316 是 frontmatter 校验拦截点（跑 `check-frontmatter.py`，非空错误即 exit 1）——与 B3 前提一致。 |
| **N8**（读取路径引用错误）| 改"与 pass/blocker_count 的 `_md_field_get` 子进程模式同路径"（L57/L84），不再引用 candidate_count | ✅ 修复正确。`check-gate.py` L115-129 `_md_field_get` 确为 subprocess（env FILE + `sys.executable agate-md-field-get.py`），实际用于 P6 pass/fail（L502-503）、P7 blocker_count（L541-542）；candidate_count 走正则逐行（L301-307），非子进程——计划表述与代码事实一致。 |
| **N9**（op 未注册 KNOWN_OPS + dict 无 JSON 输出）| 注册入 `KNOWN_OPS` + `_format_value` 增 dict→`json.dumps` 分支（L59/L83）| ✅ 修复正确。`agate-md-field-get.py` 现状：`KNOWN_OPS`（L194-198）为各 field set 并集，无 `dispatch_plan`（`main()` L204-206 未注册则 exit 2）；`_format_value`（L129-142）对 dict 走 `return str(value)`（Python repr 单引号，非 JSON）——计划诊断与代码一致。 |
| **N10**（parallel_limit 测试术语不一致）| `test_dispatch_plan_parallel_limit` 描述改"static-batch/parallel"（L68）| ✅ 修复正确。Task 1 L68 与 Task 2 L87 均写"static-batch/parallel 模式"，术语统一。 |

### 修复闭环确认（B1 复核）

Task 1 8 条用例（5 正 + 3 负）↔ Task 2 实现范围逐条闭合：mode 枚举（`test_mode_valid`）、parallel_limit≥1（`test_parallel_limit_zero`）、batch id+complexity∈三值（`test_batch_granularity`+`test_batch_missing_complexity`）、batch 数≤parallel_limit 默认 3（`test_parallel_limit`）、模式 1/5 batches 可选（`required_fields`/`batch_granularity`）、无字段跳过等同现状含输出对比断言（`test_optional`）、malformed YAML 不崩溃不误拦（`test_malformed_yaml`）。Task 2 L90"八条全过"与验收 #5"8 条用例：5 正向 + 3 负向"自洽。✓

### 新增问题（非阻塞，不阻断执行）

- **N11（备注）**：`agate-frontmatter-check.py` `_check()` L177-181 的 **MAX_DEPTH=3 深度检查对所有 frontmatter 字段生效**（`for field, value in data.items()`），非仅 schema 字段——B3 方案 c"不入 schema"**不豁免深度检查**。实测计划样例 `{mode, parallel_limit, batches:[{id, complexity}]}` 深度恰好 = 3（通过），但若未来 batches 元素再嵌套（如加 `tasks` 数组）深度会超 3，pre-commit 被 frontmatter-check 拦。建议在字段契约中显式声明"dispatch_plan 嵌套深度 ≤ 3（受 frontmatter-check MAX_DEPTH 约束）"。
- **N12（备注）**：计划 File Structure L37 声称 **Modify `test_check_gate.py`**，但 Task 1/2/6 全部只使用新建的 `test_dispatch_orchestration.py`（8 条用例全部在其中），无任何 task step 触及 `test_check_gate.py`；且 L38 描述新文件覆盖"工作量评估/模式决策/并行规则逻辑测试"，实际 8 条全是 dispatch_plan 字段校验。File Structure 与任务主体描述不一致，建议统一（删除 L37 或改注"字段校验测试在 test_dispatch_orchestration.py"；L38 描述改为与 Task 1 一致），避免 implementer 困惑/文档漂移。
- **N13（备注）**：check-gate 校验规格（Task 2 L84-89）只定义了 mode 枚举 / parallel_limit≥1 / static-batch+parallel 的 batch 校验 / 模式 1·5 batches 可选，**未定义 mode 4 `recon-then-split` 的 batches 语义**。语义上合理（先侦察后拆批，P2 时可能无 batches，属"宽松无误报"），但建议显式声明"recon-then-split 的 batches 不校验"，封死规格空隙。
- **N14（备注）**：`dispatch_plan` 键存在但**值为标量**（如 `dispatch_plan: single`，YAML 解析成功）时，op 输出非 dict 值（`_format_value` 走 str() 返回 `"single"`），check-gate `json.loads("single")` 会抛 JSONDecodeError。`test_dispatch_plan_malformed_yaml` 只覆盖"整体 frontmatter YAML 解析失败 → op 输出空"，未覆盖"值类型错误（标量）"。建议 check-gate 对 json.loads 用 try/except（解析失败 → 报 ERROR 或按缺字段处理，不崩溃），并在负向用例补一条"dispatch_plan 值非 dict"。

### 三审结论

**approved** —— 第 2 次评审的阻塞问题 B3 及非阻塞 N8/N9/N10 均已正确修复，与任务描述一致；计划 TDD 流程闭合（8 用例 ↔ Task 2 实现 1:1）、验收标准可判定、无自相矛盾。字段契约（frontmatter 单行 flow YAML + op `dispatch_plan` 子进程读取 + JSON 输出 + 不入 frontmatter-check schema）与 `check-gate.py` / `agate-md-field-get.py` 实际能力完全匹配。N11-N14 为可执行性备注，不阻断。可执行。
