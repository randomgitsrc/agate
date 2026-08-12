---
phase: P2
task_id: TAG0002-refactor-first-class
type: review
parent: P2-design.md
trace_id: TAG0002-P2-20260812
status: approved
created: 2026-08-12
agent: plan-eng-review
---

# TAG0002 — P2 工程评审（plan-eng-review）

> 评审对象：P2-design.md（candidate_count=2，方案 A「结构化字段 + 分支 gate」选定）
> 评审维度：方案可行性 / 候选方案质量 / 影响域完整性 / BDD 可验收性 / gate_commands 合理性 / 回填验证 / 止损条件
> 查证方式：逐文件对照 worktree `agate/` 现状代码（check-gate.sh / agate-md-field-get.py / agate-frontmatter-check.py / ci-gate-backstop.py / check-p6-format.sh / check-p6-provenance.sh / 阶段卡片 / fixtures.bash / 历史 commit c182dc3）+ 测试基线计数。

## 1. 检查清单逐项结论（dispatch-context 七项）

### 1.1 方案可行性（change_type → P6 分流 → P3 跳红灯三环自洽）

结论：可行且自洽。已逐条核实现状代码：

- **change_type 入 P1 frontmatter**：`agate-frontmatter-check.py` P1 schema 现有 `migrated_keys`/`enums`/`types` 机制可直接扩展（P2-design §3.1）；`agate-md-field-get.py` STRING_FIELDS + `_regex_fallback` 同 risk_level 模式（L90/L147-148）可读。**BDD-1 成立的关键前提已实证**：frontmatter-check 只校验 known keys + 枚举/类型/嵌套深度（L130-190），未知键不报错 → P1 声明 change_type 不会误杀；P1 gate（check-gate.sh L43-133）不解析该字段，`2>/dev/null || echo ""` 短路语义与现有 L298-299 同构。
- **P6 gate 分流**：插入点（L292 `P6)` 之后、L297 `P6_FILE=` 之后、L298 PASS_FM 读取之前）确认与设计 §3.3 一致；既有 L300-321 判定逻辑逐字节保留的约束可落地。`regression_pass + regression.log 双证`判定是**二值**的（`REGRESSION_PASS != "true" || 文件缺失 → exit 1`）。
- **P3 跳 TDD 红灯**：`ci-gate-backstop.py` P3 分支 L109-139 无条件重跑 check-tdd-red.sh，对 refactor 任务（全量即绿 → exit 2 绿灯）会误报 FAIL —— [SCOPE+] 判定属实且必要；`check-tdd-red.sh` L77-80 exit 0 → judge 2 的行为印证了该误杀路径。P3 卡片 + ci-gate-backstop 双点声明覆盖完整。
- **与既有 v2.0 frontmatter 体系兼容**：复用同一读取/校验通道，无新机制引入。

### 1.2 候选方案质量（candidate_count=2）

结论：两个候选均为真实替代，非稻草人；权衡诚实；选择理由自洽。

- 方案 B（纯文档口径 + 人工分流）是真实存在的低成本选项（只动卡片文档 + P1 样例），其缺点论证落到具体 BDD：**BDD-3/4/6 的 Then 绑定 gate 级机械判定，文档口径下"回归失败拦截"完全依赖 verifier 自觉，BDD-4 的 Then 无法成立**——这是实质性反驳而非凑数。
- 方案 A 的成本被诚实列出（"动协议而非写文档"工作量 + `regression_pass` self-authored 局限），未隐藏。
- 选择理由三重（BDD 可验收性 / 与机器字段体系同构 / 风险可控）均与 P1 决策 1（frontmatter）对齐，且"文档只当油门不当刹车"（§2.3 末段）正确处理了方案 B 的价值残留。

### 1.3 影响域完整性（改 / 不改 / 风险）

结论：覆盖完整，边界清晰，P0 known_risks 四项全部有落点。

- **改**：P1/P6/P3 三张卡片 + check-gate.sh P6 + md-field-get + frontmatter-check + ci-gate-backstop（[SCOPE+]）+ WORKFLOW/state-machine/dispatch-protocol + verifier/test-designer 角色 + bats + count-tests + check-protocol-consistency——清单 §1.1 完整，且每项标注了现状锚点（L 号可查证）。
- **不改**：no_behavior_change 语义与全部既有触点保留（known_risks[2] 的等价性结论 §2.1 正确：两者语义方向相反，独立分支而非替换）；check-p6-*.sh 六道审计不加不改；其余 7 张阶段卡片不动；`~/.agate` 禁止改动。边界具体到"逐字节保留"，可执行。
- **风险表 5 项**：已知风险 3（P3 回归测试）→ BDD-8 + §3.4；已知风险 0（P6 口径冲突）→ §3.7 止损；已知风险 1（形式化后不重构/流程负担）→ §2.7 + BDD-7 Then。覆盖完整，等级/缓解务实。

### 1.4 BDD 可验收性（8 条全覆盖）

结论：8 条 BDD 全部有实质锚点，二值可判定：

| BDD | 锚点 | 可验收证据 |
|---|---|---|
| BDD-1 | §3.1 | P1 gate 不解析 + frontmatter-check 枚举校验（minimal_validation 已验）+ bats |
| BDD-2 | §3.3 短路 | 既有 P6 基线 + 缺省反证 bats 用例 |
| BDD-3 | §3.2/§3.3 | refactor fixture P6 gate exit 2（bats） |
| BDD-4 | §3.3 硬校验 | fixture 缺 regression_pass/regression.log → exit 1（bats），关键路径 PASS 不豁免 |
| BDD-5 | §3.2.1 约束 5 + §3.5 三处声明 | 文档含明确禁止表述（P6 验收引用具体文案） |
| BDD-6 | §3.3 只看 change_type | refactor+no_behavior_change 混用仍强制双证（bats） |
| BDD-7 | §3.7 fixture 建模 c182dc3 | 回填 fixture P1/P3/P6 三处 gate（bats） |
| BDD-8 | §3.4 卡片/派发/test-designer | 文档含回归口径说明（P6 验收引用 P3 卡片措辞） |

**"regression_pass + regression.log 双证二值判定"**：确认成立——判定就是 `!= "true" || 缺失 → exit 1`，无中间态；回归失败的反例路径（BDD-4）与缺省兼容路径（BDD-2）都能被 bats 机械断言。

### 1.5 gate_commands 合理性

结论：合理。P3 用 P0-brief test_cmd（check-gate.bats，新分流用例主落点）+ generic-exit-only formatter（新失败用例 → exit 非零 → 真红灯，符合 TDD）；P5 全量套件覆盖 631 基线 + 新增用例；ui_affected=false → 无 P5_e2e 正确；**不新增 gate_commands 键**（P6 回归重跑复用 P5 全量命令）→ CHECK 4 锚点安全。631 = unit 530 + regression 17 + integration 78 + sanity 6，计数口径已核实与 count-tests.sh（625，不含 sanity）自洽。

### 1.6 回填验证路径（BDD-7）

结论：可行。c182dc3（`refactor: trim orchestrator-template.md`，12+/14-）已核实为真实重构 commit，review-design §5.3 点名一致。§3.7 的 fixture 建模方案（`create_task_dir` + `add_p1_field change_type refactor`，fixtures.bash L242-247 已确认 helper 存在）忠实反映"产物形状"；"不重执行历史重构 + 不重跑 631"的取舍诚实且避免无谓成本。**重要边界已自洽**：fixture P6 的 regression_pass/regression.log 是构造产物，验证对象是"refactor 形状能否走通 gate 机制"而非"真实回归能否产出 EXIT_CODE: 0 日志"——后者由 P5 全量回归真实执行覆盖。

### 1.7 止损条件

结论：覆盖。P0 known_risks[0]（refactor 口径与既有 P6 gate 冲突难以调和 → 停，重设计而非硬塞）在 §3.7 末段落为显式边界，并声明在 P6 验收报告记录、不作为可强行通过的 BDD。"连续 3 次重构仍走协议外 → 设计失败"（review-design L265）属**跨任务观测指标**，单任务内不可机械判定，本设计通过 BDD-7 Then（"全程未被强制新增功能 BDD 或额外功能测试，重构流程不比直接改更麻烦"）在 Phase A 范围内守住"不比直接改麻烦"的下界，处理合理。

## 2. 架构问题（阻塞级）

无。方案 A 三环机制（P1 字段声明 → P6 gate 分流 → P3 跳红灯）经逐行对照现状代码全部落地可行，无发现会导致 P4 实现卡死或 P6 验收不可判定的阻塞问题。

## 3. 架构问题（非阻塞，记录待 P3/P4 留意）

- **N1**：`regression.log` 内容完整性有客观边界——gate 只硬校验文件存在 + frontmatter `regression_pass: true`，provenance 审计 5 仅拦截"被引用且 EXIT_CODE 非 0"的日志；**EXIT_CODE 尾行缺失时审计 5 输出非阻塞提示跳过（check-p6-provenance.sh L222-224）**，即"内容为失败但尾行伪造 EXIT_CODE: 0"的日志无法被机器拦截。此为 LIMITATIONS 局限 3 的固有形态，设计 §7 已诚实标注，未假装封死——评审认为可接受，但建议 verifier.md 口径明确"regression.log 保存全量命令原始输出 + EXIT_CODE 尾行"结构，保留人工核验锚点。
- **N2**：设计示例中"全量回归全绿"被呈现为 **BDD-1** 的 PASS 行（§3.2.1 约束 2）——这把"回归全绿"与具体 BDD 编号耦合。refactor 任务 P1 必须把 BDD-1 定义为"关键路径行为不变（含全量回归全绿）"断言，P6 才能对号入座。建议 P3 回归测试口径说明中明确该编号对齐规则，避免 test-designer 自行定义 BDD-1 语义造成 P6 行文错位。
- **N3**：`regression_pass` 走"bool 无正文回退"语义需要 md-field-get 新增一个 NO_FALLBACK_BOOL 类别（现有 NO_FALLBACK_INT_FIELDS L75-79 是同类先例）——纯实现细节，P2 层面无歧义。
- **N4**：P5 gate_commands 复用 P0-brief test_cmd 指向 `agate/tests/unit/check-gate.bats`——本任务 P3 新增的 refactor 用例会先红后绿，注意 P3 阶段 check-tdd-red 判红时不应受同文件既有 500+ 绿用例干扰（bats 逐 @test 独立判定，exit 非零即红，无干扰）——已确认安全，仅提示不必为此拆分文件。

## 4. 测试缺口

无阻塞性缺口。P3 用例组应覆盖的 4 条路径（refactor 正例 / 回归证据缺失反例 / no_behavior_change 混用反例 / 缺省兼容反证）已在设计 §6 完成标志 6 中列明，与 BDD-3/4/6/2 一一对应。建议 P3 额外补一条"P1 声明非法枚举值（如 `change_type: feature`）被 frontmatter-check 拦截"的正向用例，锁定 BDD-1 的枚举校验侧。

## 5. 锁定决策

- **change_type 入 P1 frontmatter 机器字段体系**（枚举 `{refactor}`，缺省 = 功能口径，与 risk_level 同类为 gate 读取者）。
- **P6 refactor 口径 = 行为不变声明 + regression_pass/regression.log 双证硬校验 + 关键路径 BDD 逐条 PASS/FAIL**，缺省路径逐字节保留。
- **refactor 不豁免 BDD 编号机制、不豁免 provenance 审计、不改 check-p6-*.sh**；no_behavior_change 保留原语义，与 refactor 互补不混用。
- **P3 refactor 任务走回归测试口径并跳过 check-tdd-red 红灯**，由 ci-gate-backstop P3 分支 refactor 感知兜底（[SCOPE+] 已声明）。
- **P2 固化 gate_commands 不新增键**；P6 回归重跑复用 P5 全量命令。
- **回填验证以 fixture 建模 c182dc3**，不重执行历史重构；口径冲突止损边界在 P6 验收报告记录。

## 6. 评审结论

**approved**。

方案 A（结构化字段 + 分支 gate）满足 P1 全部 8 条 BDD 的可验收性（BDD-1..8 锚点见 §1.4），三环机制（change_type 声明 → P6 gate 分流 → P3 跳红灯）经现状代码逐行核实可行，影响域/风险/止损边界完整覆盖 P0 known_risks 四项，候选方案 B 被实质反驳而非稻草人，回填路径（c182dc3 + fixture）诚实可行。非阻塞项 N1-N4 记录待 P3/P4 留意，不影响推进。
