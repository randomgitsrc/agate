---
phase: P2
task_id: T001
type: review
parent: P2-design.md
trace_id: T001-P2-review-eng-20260809
status: approved
created: 2026-08-09
agent: plan-eng-review
---

# T001 — P2 方案设计独立工程评审（plan-eng-review）

> 被评审对象：`P2-design.md`（architect 产出）
> 评审依据（优先级）：`P2-dispatch-context-plan-eng-review.md`（派发指引）> P1-requirements.md（28 BDD / 判别契约 / 语义真实性边界）> P0-brief.md（A+B+C+D / 9 硬约束 / 流 D 硬切）> P1-review.md（approved）> /tmp/opencode/feasibility.md > HANDOFF-V2.0.md > 角色定义 plan-eng-review.md。
> 评审方式：全部关键数字与代码引用在 worktree 实测/AST 核实，不依赖 architect 自述。
> 结论：**approved**（8 条非阻塞 FIND，交 architect 在 P3 前酌改；无阻塞级问题）

---

## 0. 客观查证结果（独立核实，不轻信 architect 自述）

| 待查证事实 | P2-design 声明 | 独立核实 | 结论 |
|-----------|--------------|---------|------|
| count-tests.sh 基线 | 594（sanity 6 另计，§正文"客观数字"）| worktree 实跑 `bash agate/tests/scripts/count-tests.sh` = **594** | ✅ 一致 |
| CHECK 9 锚点表条数 | 37 条（BDD-13，§3.1.4）| python3 AST 解析 `SCRIPT_ALIGNMENT_ANCHORS` = **37 items**；锚点 schema 含 desc/script/keywords/callers（`"callers"` 字段存在）| ✅ 一致 |
| 反向覆盖检查位置与语义 | `check_anchor_coverage`（check-protocol-consistency.py:683-713），新增 `check-*.sh` 不列锚点 → WARNING | 逐行核实：遍历 gate 脚本，未覆盖 → `rep.warn("CHECK9-coverage", ...)`；有 `GATE_SCRIPT_EXEMPT` 白名单（gate-result/install-hook/agate-changes/agate-summary/agate-init）| ✅ 一致（WARNING 级，非 ERROR；仅 --strict 阻断——设计表述"不新增则 WARNING"准确）|
| gate_commands 读取工具 = 4 个 | §正文"客观数字" + §2 不改（BDD-15）| 4 个工具均存在：agate-read-gate-commands.py / agate-gate-missing-cmds.py / agate-read-p5-commands.py / agate-gate-p5-count.py；调用点 check-gate.sh / check-tdd-red.sh:57 / agate-capture-env-baseline.sh:25 核实 | ✅ 一致 |
| agate-md-field-get.py 现状 | 3 op 正则（risk_level/ui_affected/phases），薄壳传 FILE env（§3.1.2）| 读源码核实：47 行，3 op 正则；调用点 check-pruning.sh:16,18 / check-p6-provenance.sh:25,152 / check-p6-evidence.sh:61（**共 5 个直接调用点**）| ⚠️ "6 个 .sh 薄壳"表述不精确（见 FIND-2）|
| agate-state-yaml-check.py task_id 正则 | `^T\d+$` 在 L39（流 D 硬切点）| 逐行核实 L39 `re.match(r"^T\d+$", ...)` | ✅ 一致 |
| check-changelog.sh:14 短前缀提取 | `grep -oE 'T[0-9]+'`，下游消费点 `(^|[^0-9])${TASK_ID_SHORT}( \|:\|$\|,\|-)`（§3.4.2）| 逐行核实 L14 与 L41 消费者正则；设计"直接匹配完整 task_id"方案在流 D 硬切（`^T[A-Z]{2}\d+$` 无目录后缀）下自洽 | ✅ 一致 |
| pre-commit 挂载点 | check-state-yaml.sh 调用旁（pre-commit-gate.sh:52）；P6 --fix 在 2h 步骤（:140-144）| 逐行核实 L52 `check-state-yaml.sh`、L140-144 `check-p6-format.sh --fix`（注释"2h. P6 格式自动归一化"）| ✅ 一致 |
| check-p6-format.sh 现状 | 大小写/全角归一化 sed（--fix/--check 双模式已存在，§3.2.1）| 读源码核实：--fix/--check 双模式 + sed 归一化链 | ✅ 一致 |
| P2 分支 grep 对 frontmatter 形式的兼容性 | `^candidate_count:` / `^(packages\|domains\|ui_affected\|gate_commands):` 对顶格 frontmatter 字段仍匹配（§7 assumption 2）| 逻辑推演 + 现文件结构核实：frontmatter 顶层 key 顶格，正文 gate_commands 顶格 → 匹配成立；check-gate.sh:106/138 引用位置逐行核实 | ✅ 一致 |
| 受影响测试规模 | 15 文件 / 355 @test（§正文 + §3.1.5）| worktree 逐文件汇总 = **354**（pre-commit-hook.bats 现为 42，feasibility 附录写 43）| ⚠️ 数字陈旧（见 FIND-3）|
| regression 摩擦锚点 | "5 个 regression 文件"（§3.1.5）| regression/ 确有 5 个 .bats；但 v060-p8-cached（P8 --cached，不涉迁移字段）与 v060-yaml-indent（task-files.md 模板 executor_env，P0 字段不迁移）非"改写为测 frontmatter 版行为"目标；真正摩擦锚点 = design-gap/p8-internal-only/r4-cached 3 个（feasibility 附录亦只列这 3 个）| ⚠️ 表述过度（见 FIND-3）|
| BDD 映射表 | §9 覆盖 BDD-1..28 | 逐行数 = **28 行**，每条指向 §3.x 具体设计落点（非只列编号）| ✅ 一致 |
| candidate_count | 2（正文 L38），§1 两个候选方案含权衡矩阵 + 选择理由 | 核实：方案 A/B 完整 + 对比矩阵 8 维 + 选择理由 + 子决策 | ✅ 一致 |
| 四字段 | §4 packages/domains/ui_affected + §5 gate_commands（正文留）| 全部存在且值合理（domains 含 cli 的 FIND-3 已在 P1-review 注明）| ✅ 一致 |
| 语义真实性边界 | §10 显式声明（BDD-14）| 读 §10 全文：结构化解决 11 项 / 不解决 3 项 / 保障机制不变 / gate 强度不升不降 | ✅ 一致 |
| pyyaml 行为（§7 声称已验证 5 点）| ② 全角冒号 YAMLError、③ 无空格 YAMLError、④ phases 块式 list、① 中文 key、⑤ frontmatter 优先 | 本评审实测复现：多行 frontmatter 块内含全角冒号行/无空格行 → **均 YAMLError**；块式列表 → list；中文 key → 正常；但**单行纯 scalar 块（如仅一行全角冒号、无其它 key:value）→ safe_load 返回 str 而非 dict、不报 YAMLError**（边界，见 FIND-5）| ⚠️ 主路径证实，单行块边界未覆盖 |
| ui_affected 值归一化风险 | §7 声明 bool→"true"/"false" 转换 | 消费端实测：check-p6-evidence.sh:64 / check-p6-provenance.sh:155 均为 `[ "$UI_AFFECTED" = "true" ]`（**小写精确匹配**）→ 转换必须输出小写，设计未写明 `.lower()` 细节（见 FIND-4）| ⚠️ 风险真实存在，已有声明，缺 P3 测试锚点 |

---

## 1. 架构问题（阻塞级）

**无。** 方案 A（单工具双读扩展 + frontmatter schema 校验器挂 pre-commit）在工程上成立，全部关键机制（pyyaml 解析、判别契约、薄壳不动、反向覆盖、挂载点、流 D 硬切）经实测/代码核实无致命缺陷。候选方案 B 的排除理由（双文件漂移 / 写入成本翻倍 / fixture 改造量最大 / 并发写冲突 / 违反硬约束 4）与可行性 §3 矩阵一致且工程论证充分，"355 测试换血已是最⼤成本、B 再放大一档"的判断成立。

---

## 2. 架构问题（非阻塞）

- **FIND-1（重要，建议 P3 前澄清）**：`MIGRATED_KEYS` 判别契约集（§3.1.2 伪代码）只覆盖**流 A 的 16 个字段**，未含流 B/C 的新 frontmatter 字段（`pass`/`fail`/`blocker_count`/`deviation_count`/`deviation_critical_count`/`design_gap_count`/`design_gap_reviewed_count`/`need_confirm_resolved`/`suggest_resolved`/`scope_resolved`）。若流 B/C 读取经双读工具的判别契约路由（§3.2.1 P6 明确"经双读工具新 op"），则一份**只有流 B 字段**的 v2.0 P7-consistency.md（其 frontmatter 无任何流 A 迁移字段）会被判别契约判为"旧格式"→ 回退正则 → 恰好复现 F13/F14 设计要消灭的歧义 grep。建议二选一明确：① `MIGRATED_KEYS` 扩展为全部迁移字段全集；② 双读 op 改为"**op 自身字段在 frontmatter 中存在即优先取 frontmatter**"的字段级 presence 检测（与 §3.1.1 presence 语义一致），判别契约仅用于"frontmatter 无任何机器字段时回退正则"的旧格式判定。此点不推翻架构，但影响流 B/C 核心收益，须在 P3 测试设计前定死。
- **FIND-2（表述精度）**："6 个 .sh 薄壳接口不变"（§1 方案 A 优点①）不精确——`agate-md-field-get.py` 实际直接调用点 **5 处**（check-pruning×2 / check-p6-provenance×2 / check-p6-evidence×1）；`agate-extract-context.sh:69,80,88` 读 risk_level 与四字段走**原生 grep**，不经双读工具，不会"内部自动双读"（frontmatter 顶格 key 仍能匹配，功能不受损，但不满足 BDD-1"统一读取"的字面语义）。建议在影响域表补一行 `agate-extract-context.sh`（保持 grep 或改路由二选一），否则 P4 实现可能漏掉它。
- **FIND-3（数字陈旧）**：受影响测试 = **354** 而非 355（pre-commit-hook.bats 现为 42，feasibility 附录写的 43 已过时）；regression 摩擦锚点实为 **3 个**（v060-design-gap / v060-p8-internal-only / v060-r4-cached），v060-p8-cached（P8 --cached）与 v060-yaml-indent（模板 executor_env，P0 字段不迁移）不是"改写为测 frontmatter 版行为"对象。不影响 gate（只有 594 总数被 gate），但 P3/P5 对齐 count-tests 时应以实数为准。
- **FIND-4（归一化落地）**：`ui_affected: false` 经 pyyaml 得 Python `bool False`，消费端 `[ "$UI_AFFECTED" = "true" ]` 要求**小写**。§7 已声明转换方向但未写 `str(v).lower()` 细节。建议 P3 专测：frontmatter `ui_affected: true/false` → op 输出恰好 `"true"`/`"false"`（大小写、bool 转换各一用例），防 P4 用 `str(False)` 产出 `"False"`。
- **FIND-5（边界）**：frontmatter 块若**只有一行全角冒号行**（无任何 `key: value` 行）→ `yaml.safe_load` 返回 str 非 dict、**无 YAMLError** → 校验器步骤 3"YAMLError → 报错"与步骤 4"非 dict → exit 0"都放行 → BDD-2"不再静默"在该边界失效。实际 P1/P2 文件 frontmatter 必有 phase/task_id 等通用 Header（保证 ≥1 个合法 key 行），故实操不触发；建议校验器对"有 frontmatter 块但解析结果非 dict"（P1/P2 文件）一律报错，彻底堵死。
- **FIND-6（可选硬化）**：流 B 审计 3（check-p6-provenance）设计给出"从严正文 grep **或** frontmatter pass+fail"两选一，无两者交叉校验。P1 BDD-16 明确要求"基于 frontmatter 判定"，故 verifier 在 frontmatter 声明 pass:28 而正文只有 20 条 PASS 行的"假一致"不会被拦（属语义真实性边界内的自声明 nudge，不违反硬约束 6）。低成本建议：审计 3 增加 frontmatter 总数 vs 正文从严行数不一致的 **WARNING**，作为防呆而非 gate 强度提升。
- **FIND-7（数量预算）**：§3.1.5 同时声明"15 文件 @test 数逐文件保持"与"新增 unit/check-frontmatter.bats 测试（只要总数 594）"——两者若不配平则总数必然上浮。需明确补偿机制（把既有断言改造为校验器断言、或从某文件显式移减 N 条），P3 test-designer 对齐 count-tests.sh 时须有具体核算表，否则 P5 会因 594 漂移返工。非阻塞（P1 隐含需求 #4 已把"改造而非新增"列为职责），但设计应给出核算口径。
- **FIND-8（跨文件同步遗漏风险）**：§3.4.2 已列出 agate-summary.sh / active-tasks.md / check-changelog 其他调用方"P4 grep 全库核对"，但 `scripts/README.md:68`（`agate-md-field-get.py` 工具清单表）与 `agate-test-plan-2026-07-01.md` 附录 A 未列入影响域。前者新增 op 后工具描述需同步，后者 count-tests 文档漂移检查会因 354/355 数字不一致报漂移。建议补入 §2 影响域表（文档类低风险）。

---

## 3. 测试缺口（当前设计下 P3 必须补、设计已列但需落地）

| 场景 | 设计落点 | 缺口/建议 |
|------|---------|----------|
| 判别契约互斥（BDD-9 vs BDD-10）| §1 风险行 + §3.1.2 | P3 需覆盖"frontmatter 含流 B/C 字段但无流 A 字段"的 P7 文件（对应 FIND-1）——现设计只提到 BDD-9/10 互斥 |
| ui_affected bool 归一化 | §7 | 补 `true`/`false` 与大小写锚点测试（FIND-4） |
| frontmatter 单行 scalar 块 | §3.1.3 | 补"非 dict 但有 frontmatter 块"用例（FIND-5） |
| 流 B frontmatter 汇总 vs 正文行数 | §3.2.1 | 可选 WARNING 一致性用例（FIND-6） |
| 值归一化 / 类型校验对旧格式回退的隔离 | §3.1.2/§3.1.3 | 旧格式文件不得触发必填/枚举校验（判别契约反向用例）|
| 流 D 硬切（BDD-25/26）| §3.4.1 | 既有 agate-state-yaml-check.bats 需补 TAG0001/T001 双向用例（现文件仅测 `^T\d+$`）|

---

## 4. 锁定决策（本次评审后确定的技术方向）

1. **方案 A 锁定**：单工具双读扩展（`agate-md-field-get.py` frontmatter 优先 + 正则回退）+ `agate-frontmatter-check.py` / `check-frontmatter.sh` 挂 pre-commit。方案 B（独立 .yaml）排除理由成立。
2. **流 B 折中增强确认**：P6 汇总入 frontmatter、逐条留正文但行首强制 `- PASS|FAIL BDD-NN:`；`check-p6-format.sh` 升级为 --check/--fix 双模式，pre-commit 自动 --fix（既有 2h 机制复用）。
3. **流 C 边界确认**：只结构化"已解决/已确认"状态（need_confirm_resolved / scope_resolved / design_gap_count），SCOPE+/PROD_TOUCHED/DESIGN_GAP 发现性标记保持散文（BDD-23）。
4. **流 D 硬切确认**：`^T[A-Z]{2}\d+$`，无双格式兼容；check-changelog 直接匹配完整 task_id（新格式无目录后缀，方案自洽）。
5. **gate_commands 暂留正文确认**：4 工具不改、check-gate.sh P2/P5 分支对 gate_commands 块调用保持原样（BDD-15）。
6. **自举路径确认**：worktree 与主 checkout 共享 `.git/hooks`（git worktree 特性），T001 提交自动走 v0.35 主 checkout hook——设计 §2"不改主 checkout hooks"表述与 git 语义一致。

---

## 5. 四流覆盖 / 硬约束遵守（逐项判定）

| 项 | 判定 | 依据 |
|----|------|------|
| 流 A（P1/P2 迁移+双读+校验器+pre-commit+锚点+fixture）| ✅ 完整 | §3.1 五小节齐备，无遗漏文件 |
| 流 B（P6/P7 结构化）| ✅ 完整（FIND-1 澄清项除外）| §3.2.1/3.2.2/3.2.3，含审计 2 白名单同步 |
| 流 C（标记收尾）| ✅ 完整 | §3.3.1/3.3.2/3.3.3 |
| 流 D（编号硬切）| ✅ 完整 | §3.4.1/3.4.2/3.4.3，连锁影响已列 |
| 硬约束 1（594 不漂移）| ⚠️ 预算未配平 | FIND-7，P3 需核算表 |
| 硬约束 2（≤3 层嵌套）| ✅ | §3.1.1 单层/一层列表 + §3.1.3 深度断言 |
| 硬约束 3（可复制模板）| ✅ | §3.3.3 + v0.31.0 先例 |
| 硬约束 4（双读）| ✅ | §3.1.2 判别契约（FIND-1 澄清后更稳）|
| 硬约束 5（CHECK 9 全过）| ✅ | §3.1.4 既有 37 全量校准 + 新增 1 条 = 38，反向覆盖已核实 |
| 硬约束 6（语义真实性）| ✅ | §10 显式声明，BDD-14 对应 |
| 硬约束 7（gate_commands 留正文）| ✅ | §2 边界 + 风险行 |
| 硬约束 8（先写 regression）| ✅ | §3.1.5 regression 改写 + P3 gate 含 regression 目录 |
| 硬约束 9（流 D 硬切）| ✅ | §3.4.1，无双格式 |
| 自举（BDD-28）| ✅ | §2 不改主 checkout + worktree 共享 hooks |

---

## 6. 技术风险识别情况（评审重点 5）

| 风险 | 设计识别 | 对策充分性 |
|------|---------|-----------|
| 值归一化（ui_affected bool→小写）| ✅ §7 声明转换方向 | 缺 `.lower()` 细节 + P3 锚点（FIND-4）|
| FIELD_COUNT 改动牵动 check-gate.bats 101 测试 | ✅ §3.1.5 覆盖 + §7 assumption 2（grep 兼容性已核实）| 充分 |
| CHECK 9 反向覆盖（37→38）| ✅ §3.1.4 [SCOPE+] 明示 | 充分（锚点 schema callers 字段已核实存在）|
| pre-commit 挂载时机 | ✅ §3.1.4 与 check-state-yaml 同构 | 充分 |
| 判别契约写错（BDD-9/10 互斥）| ✅ §1 风险行 + P3 专测 | FIND-1 使契约覆盖流 B/C 后更完备 |
| P5_DATA CACHE_KEY 失效 | ✅ §2 风险行 + P4/P5 验证 + CHANGELOG | 充分 |
| 流 B 汇总 vs 正文假一致 | ❌ 未识别 | FIND-6（可选 WARNING）|
| 新校验器测试导致 594 漂移 | ⚠️ 声明"允许但需对齐" | FIND-7（预算未配平）|

---

## 7. 语义真实性边界（评审重点 7 / BDD-14）

✅ §10 显式、完整地写明"v2.0 结构化改造只提高解析可靠性，不改变 gate 对内容真实性的判断能力"，列出结构化解决 11 项 / 不解决 3 项（BDD-8 单侧/双侧歧义、candidate_count 虚报、权衡关键词语义匹配）/ 保障机制不变 / gate 强度不升不降。与 P1 §9、P0-brief known_risks 第 9 条、可行性 §5.2 一致。满足 BDD-14 与硬约束 6。

---

## 8. minimal_validation 评审（角色定义要求）

- assumption 1（pyyaml 解析行为）：实际做了 5 点实证，本评审复现 ①②③④ 均成立；⑤（frontmatter 优先）机制正确。**不是只写声明**。✅
- assumption 2（P2 分支 grep 兼容性）：代码读验证 + 本评审独立核实成立。✅
- assumption 3（pre-commit 挂载）：声明 `not_needed` 并附理由（既有 check-state-yaml 同构机制 + P3 测试覆盖）。按 P2 卡片"纯代码逻辑须声明"规则，本方案属纯代码逻辑（依赖 yaml.safe_load / 既有正则 / 字符串转换，均在 §7 列出），声明合规。✅

---

## 9. 评审结论

**status: approved**

- 方案 A 技术可行性成立，关键机制全部经独立实测/代码核实；候选方案 B 排除理由成立且公平（正确承认其纯 YAML 校验优势，无稻草人）。
- 四流（A/B/C/D）设计落点完整可实施，28 条 BDD 映射真实（逐条指向 §3 具体设计，非编号装饰）。
- 9 条硬约束 + 自举原则全部有对应设计；语义真实性边界 §10 显式声明。
- minimal_validation 是实证而非形式声明，符合 P2 卡片要求。
- 8 条 FIND 均非阻塞（FIND-1 判别契约全集、FIND-4 bool 归一化、FIND-7 数量预算在 P3 前需 architect 澄清/配平，其余为表述与文档精度）。建议 architect 在 P3 测试设计派发前回填 FIND-1 的判别契约口径与 FIND-7 的数量核算表。

> 提示主 Agent：gate 规则要求 P2-review.md 的 `agent` 非 main（此处 = plan-eng-review，满足）。预跑 `check-gate.sh P2` 预期通过；P2-progress.md 更新后再 commit（带 self-gate-review）。
