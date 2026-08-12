---
phase: P7
task_id: T001
type: consistency
parent: P2-design.md
trace_id: T001-P7-20260810
status: approved
created: 2026-08-10
agent: consistency-reviewer
blocker_count: 0
deviation_count: 0
deviation_critical_count: 0
design_gap_count: 7
design_gap_reviewed_count: 7
---

# T001 — P7 一致性交叉检查

> 独立审查，非机械转抄。P4-implementation.md 声明的 7 条 `[DESIGN_GAP:]` 逐条读取实际代码
> 核实（不只信自述），交叉比对 P2-design.md 对应节。全部 7 条独立核实为"描述与代码一致、
> 理由站得住"，判定 REVIEWED-ACCEPTED。未发现需要打回 P4 的问题。

## 1. DESIGN_GAP 逐条裁决（P4-implementation.md § 全文，7 条）

### 流 A（2 条）

[DESIGN_GAP: check-gate.sh 的 P2 分支未按 P2-design.md §3.1.2 迁移到双读工具——现有 grep 对顶格 frontmatter 字段巧合兼容，已用 git stash 验证行为一致，但设计明确要求"为统一解析可靠性仍需迁移"]（P4-implementation.md 行 78）

[DESIGN_GAP_REVIEWED: 接受。独立读取 `agate/scripts/check-gate.sh` P2 分支源码（约行 138-173）确认：`CANDIDATE_COUNT=$(grep -E '^candidate_count:' "$P2_FILE" ...)`、`FIELD_COUNT=$(grep -cE '^(packages|domains|ui_affected|gate_commands):' "$P2_FILE" ...)`，确实仍是裸 grep，未走 `agate-md-field-get.py` 双读工具（对照 P2-design.md §3.1.2 "5 个调用点不改，check-gate.sh 分支需改走双读工具"）。因 frontmatter 恒在文件最前且顶格书写，`^candidate_count:` 只会命中 frontmatter 内的行，功能上等价于双读的"frontmatter 优先"语义（BDD-10）；且 `agate-frontmatter-check.py` 的 P2 schema（`agate/scripts/agate-frontmatter-check.py` 行 55-65，required=candidate_count/packages/domains/ui_affected）已在 pre-commit 层拦截全角冒号/缩进/枚举错误（BDD-2/4/5），check-gate.sh 未走双读工具不会漏掉这些坏格式——校验責任已由独立的 schema 校验器承担，不依赖 check-gate.sh 本身。这是"统一实现路径"层面的设计偏离（P2 §3.1.2 字面要求全部迁移），但不是"解析可靠性"层面的功能缺口。裁决：可接受，不构成 BLOCKER。引用锚点：P2§3.1.2、P4§流A改动文件清单。]

[DESIGN_GAP: check-pruning.sh 的 8 个 P1 字段读取点同理未迁移，理由同上]（P4-implementation.md 行 86）

[DESIGN_GAP_REVIEWED: 接受。独立读取 `agate/scripts/check-pruning.sh` 确认：`risk_level`/`phases` 两个字段（行 16、18）已走 `agate-md-field-get.py`（双读工具，未变动接口）；`override`（行 23）、`coupling_checklist`（行 82）、`internal_only`/`internal_only_reason`（行 90、92）、`跳过风险`（行 100）等 8 个字段仍是 `grep -qE '^field:' "$P1_FILE"` 裸正则。与流 A 第一条同理，schema 校验器（P1 required 集合 `risk_level`/`phases`/`packages`/`domains`，可选字段的类型/presence 规则同样已覆盖）已在 commit 前挡住坏格式，check-pruning.sh 未迁移不产生实际解析可靠性缺口。裁决：可接受。引用锚点：P2§3.1.2、P4§流A"未改动文件清单"。]

### 流 B（2 条）

[DESIGN_GAP: check-gate.sh P6 分支旧格式回退的正文 grep 计数正则，未采用 P2-design.md §3.2.1 给出的严格锚定形式 `^\s*- (PASS|FAIL) BDD-[0-9]`，而是用更宽松的 `^\s*- (PASS|FAIL)\b.*BDD-[0-9]`。check-p6-provenance.sh 审计 3 的 `P6_BODY_STRICT` 计数已严格照抄设计原文正则，两处口径故意不同]（P4-implementation.md 行 196）

[DESIGN_GAP_REVIEWED: 接受。独立 grep 核实两处正则确实不同：`agate/scripts/check-gate.sh:285` 为 `grep -ciE '^\s*- (PASS|FAIL)\b.*BDD-[0-9]'`（宽松）；`agate/scripts/check-p6-provenance.sh:142` 为 `grep -cE '^\s*- (PASS|FAIL) BDD-[0-9]'`（严格，大小写敏感）。理由可验证：check-gate.bats 既有用例 G6.7 body 为 `- fail: BDD-2 broken`（FAIL 与 BDD 编号间隔一个冒号），若用严格锚定形式确实无法匹配（`\s*BDD-` 要求 PASS/FAIL 后紧跟空白）。已独立跑 `bats agate/tests/unit/check-gate.bats` 确认 G6.7 现状为绿灯，佐证宽松正则是维持既有绿灯用例的必要选择，而非随意放宽。两处口径职责边界清晰（check-gate.sh 面向全部历史正文写法的兼容性判定，provenance 审计面向 BDD-17 从严格式场景的精确计数），不是同一处判定标准前后不一致。裁决：可接受。引用锚点：P2§3.2.1、P1 BDD-17/18。]

[DESIGN_GAP: check-gate.sh P6/P7 分支判断"是否走新格式"时，采用"该判定所需的全部字段皆非空"（AND 语义）而非"任一字段非空即可"]（P4-implementation.md 行 198）

[DESIGN_GAP_REVIEWED: 接受。独立读取 `check-gate.sh` 确认 P6 分支为 `if [ -n "$PASS_FM" ] && [ -n "$FAIL_FM" ]; then`（行 279），P7 分支为 `if [ -n "$BLOCKER_FM" ] && [ -n "$DEVCRIT_FM" ]; then`（行 313）与 `if [ -n "$DESIGN_GAP_COUNT_FM" ] && [ -n "$DESIGN_GAP_REVIEWED_FM" ]; then`（行 332），均为 AND 语义，与 P4 自述一致。独立读取 `agate/scripts/agate-frontmatter-check.py` 的 `SCHEMAS` 字典确认：P6-acceptance.md 的 `required=("pass","fail","ui_affected")`、P7-consistency.md 的 `required=(五个计数字段)` 均是"文件一旦被判为新格式（含任意迁移字段）→ 这些字段必须全部存在"的组合必填规则（agate-frontmatter-check.py 行 66-91）。即 pre-commit 层已保证提交到仓库的新格式文件不会出现"半填"中间态，check-gate.sh 的 AND 判定与已有前置约束一致，不产生新的误判风险。裁决：可接受，属合理的"信任前置校验"设计。引用锚点：P2§3.2.1/§3.2.2、agate-frontmatter-check.py SCHEMAS。]

### 流 C（1 条）

[DESIGN_GAP: check-scope-resolved.sh 对 P1 frontmatter scope_resolved 字段"存在但为空列表"与"字段完全不存在"两种情况未做区分处理，两者都落入原有正文 [SCOPE_RESOLVED] grep 回退判定]（P4-implementation.md 行 342）

[DESIGN_GAP_REVIEWED: 接受，附风险提示。独立读取 `agate/scripts/check-scope-resolved.sh`（行 38-45）确认：`SCOPE_RESOLVED_FM=$(... scope_resolved ...)`，仅当输出非空字符串才走新格式直通判定，字段不存在与字段存在但为空列表两种情况下 op 输出均为空字符串（`agate-md-field-get.py` 对 `NO_FALLBACK_LIST_FIELDS` 空列表用换行连接，空列表连接结果确实是空字符串，属 Python 语言层面客观限制，非实现疏漏），代码逻辑与 P4 自述完全一致。P4 给出的"功能后果等价"论证成立于"正文无残留散文 `[SCOPE_RESOLVED]` 标记"的前提下，唯一的行为差异场景（显式声明空列表但正文残留旧式标记）概率低且 P4 已明确标注该风险，未隐瞒。P3-test-cases.md 给出的唯一流 C 测试用例（SC_BDD22.1）确未覆盖"存在但空列表"这一中间态，P4 的判断依据（无法凭测试断言反推期望）站得住。裁决：可接受，非 BLOCKER；建议后续任务补一条测试用例明确该边界语义（非本次强制项）。引用锚点：P2§3.3.1、P1 BDD-22。]

### 流 D（2 条）

[DESIGN_GAP: check-changelog.sh 移除了 P2-design.md §3.4.2 明确要求"保留"的 `grep -qF "$TASK_ID"` fallback 分支]（P4-implementation.md 行 446）

[DESIGN_GAP_REVIEWED: 接受。独立读取 `agate/scripts/check-changelog.sh` 确认无固定字符串 fallback 分支，仅保留带单词边界的正则匹配（`grep -qE "(^|[^0-9])${TASK_ID_SHORT}( |:|$|,|-)"`），代码注释（行 33-36）与 P4 自述一致，明确写出"若保留 fallback 会导致 TAG0001 被 TAG00012 误判为已匹配"。独立核实该论证的数学正确性：`TASK_ID_SHORT` 经流 D 改造后已恒等于完整 `TASK_ID`（行 14 `TASK_ID_SHORT="$TASK_ID"`），若再对同一字符串做无边界子串匹配（`grep -qF`），该匹配集合是带边界匹配集合的超集，只会引入误判、不会补充任何带边界正则漏掉的合法场景——P4"移除是唯一能同时满足 BDD-27 三个用例的实现方式"这一判断在逻辑上成立。测试断言（CL.7）与设计原文字面表述冲突时，implementer 选择"不改测试、标记偏离"符合项目既定决策树。裁决：可接受，是对 P2 设计文字表述的必要修正而非功能倒退。引用锚点：P2§3.4.2、P1 BDD-27。]

[DESIGN_GAP: 硬切 `agate-state-yaml-check.py` 的 task_id 正则后，额外触发了 33 个此前未被列入流 D 红灯清单的既有测试失败（1 个单元测试 SY.8 + 26 个 pre-commit-hook.bats + 6 个 dispatch-context-card.bats），根因是集成测试经真实 pre-commit hook 间接调用新正则，fixture 用旧格式 task_id 被硬切正则拦截]（P4-implementation.md 行 448）

[DESIGN_GAP_REVIEWED: 已解决，非仍开放的偏离。派发指引已预先说明此条在 commit `68e4173` 修复并独立验证过，本次未采信该预先说明，而是独立复核：`git log --oneline main..HEAD` 确认存在 `68e4173 wf(T001-P4-streamD-fixturefix): 修复流D硬切引发的33个既有fixture回归`，commit message 显式记录改动范围为仅替换 3 个 fixture 文件（check-state-yaml.bats/dispatch-context-card.bats/pre-commit-hook.bats）中的 task_id 占位字面值（旧格式 → 新格式），不改测试断言/逻辑。独立重新实跑验证（非引用 commit message 自报）：`bats agate/tests/unit/check-state-yaml.bats agate/tests/integration/dispatch-context-card.bats` 17/17 全绿（含此前失败的 SY.8、DC.2-DC.7）；`bats agate/tests/integration/pre-commit-hook.bats` 42/42 全绿（含此前列出的全部 26 个失败用例编号，逐一核对均已转绿）；`bash agate/tests/scripts/count-tests.sh` 实测 597（与 BDD-11 新基线一致，未因本次修复产生用例数漂移）。裁决：该 DESIGN_GAP 描述的问题在验收时点已确认真实解决，如实转抄"已解决"状态（不当作仍悬而未决处理）。引用锚点：P4§流D自查结果、commit 68e4173、P1 BDD-11 BASELINE_CHANGE。]

**DESIGN_GAP 配对小结**：P4-implementation.md 行 78/86/196/198/342/446/448 共 7 条 `[DESIGN_GAP:]`，本文件逐条转抄 + 配对 `[DESIGN_GAP_REVIEWED:]`，7/7 已配对，0 条打回。

> 附注（非 BLOCKER，供主 Agent 参考）：P6-acceptance.md 第 112-122 行的"DESIGN_GAP 交叉核对"小节称"P4-implementation.md 全部 6 条已标注"，实际 P4 正文含 7 条行首 `[DESIGN_GAP:]` 声明（第 7 条即上方"33 个既有测试回归"一条，P6 将其列为"补充，非 P4 原始 DESIGN_GAP 清单"第 7 项处理，内容本身未遗漏，仅计数措辞与行首标记的字面存在性不完全一致）。不影响本次裁决结论，因本文件按 P4 正文的行首标记逐条转抄，非按 P6 的转述计数。

## 2. SCOPE+ 闭环检查

- **P2-design.md §12**（"12. SCOPE+ 标注"节）：`[SCOPE+] 发现：新校验器 check-frontmatter.sh 触发 CHECK 9 反向覆盖检查，锚点表从 37 增至 38`
- **P1-requirements.md §5"SCOPE+ 登记（P2 阶段发现，2026-08-09）"节**：`[SCOPE_RESOLVED: CHECK 9 锚点表 37→38（新校验器 check-frontmatter.sh 触发反向覆盖检查）]`

语义核对：两处内容一致，均指向同一事实——`check-protocol-consistency.py` 的 `check_anchor_coverage` 反向覆盖检查要求每个 `check-*.sh` 在锚点表有对应条目，新增 `check-frontmatter.sh` 必须补登记。独立验证代码现状：`agate/scripts/check-protocol-consistency.py` 第 635-638 行 `SCRIPT_ALIGNMENT_ANCHORS` 含 `desc="frontmatter schema 校验"` / `script="agate/scripts/check-frontmatter.sh"` 条目；`grep -c '"desc":'` 实测锚点总数为 **38**（37 既有 + 1 新增）；独立重跑 `python3 agate/scripts/check-protocol-consistency.py` 确认 CHECK 1-9 全部 PASS、0 ERROR。

**结论：SCOPE+ 闭环成立**（1 处 SCOPE+ ↔ 1 处 SCOPE_RESOLVED，语义匹配，代码现状与登记内容一致）。

## 3. 跨文件一致性核对

### 3.1 P1 BDD 数量 vs P6 验收结果数量

- P1-requirements.md：`grep -oE '^#### BDD-[0-9]+' | 去重排序` → BDD-1 至 BDD-28，共 28 条，编号连续无跳号。
- P6-acceptance.md：`grep -c '^- PASS BDD-'` = 28，`grep -c '^- FAIL BDD-'` = 0；逐条 BDD 编号 1-28 全部出现且各仅一次（独立 grep 核对，无重复/遗漏）。
- **BDD-11 判定变更过程合规性核实**：P6-acceptance.md "BDD-11 补充说明" 节记录了完整流程——首轮验收独立重跑 `count-tests.sh` 实测 597 ≠ P1 原文断言的 594，验收方按"拿不准 → FAIL"纪律先判 FAIL（未擅自放宽标准）；随后主 Agent 审查判定该差值来自 P4 修复 `check-p6-format.sh` 真实 bug（BDD-17）时新增的 3 条合规回归测试（`F_P6FMFIX.1/2/3`），属真实覆盖新增而非删减式漂移，正式走 `[BASELINE_CHANGE: 594 → 597]` 标注批准新基线（P1-requirements.md 第 190-198 行），P6 verifier 据新基线重新判定为 PASS。本次独立复核 `bash agate/tests/scripts/count-tests.sh` 实测仍为 **597**，与批准后基线一致；独立核实 `agate/tests/unit/check-p6-format.bats` 确实含 `F_P6FMFIX.1/2/3` 三条新增用例且现状全绿。**该变更过程符合"验收方先如实报告字面不符 → 主 Agent 走正式基线变更批准 → 验收方据新基线重判"的正确流程，非验收方自行放宽标准**。
- **结论：28 条 BDD 与 28 条 P6 验收结果一一对应，PASS=28/FAIL=0，数量与内容映射均核实无误**（引用：P1-requirements.md §4 BDD-1..28、P6-acceptance.md 验收结果表、P1-requirements.md 第 190-198 行 BASELINE_CHANGE）。

### 3.2 P2 声明的 packages 与实际改动文件范围

- P2-design.md §4："packages: [agate]"。
- 独立执行 `git diff main..HEAD --stat`（覆盖 T001 全部 27 个 commit）核实文件改动范围：**绝大多数改动均在 `agate/` 目录内**（`agate-md-field-get.py`/`agate-frontmatter-check.py`/`check-frontmatter.sh`/`check-gate.sh`/`check-pruning.sh`/`check-p6-format.sh`/`check-p6-provenance.sh`/`check-scope-resolved.sh`/`check-changelog.sh`/`agate-state-yaml-check.py`/`check-protocol-consistency.py`/`pre-commit-gate.sh`/模板/角色卡/phase-cards/tests/**），与 P4-implementation.md 各流"改动文件清单"逐一对照一致，无遗漏也无越界。
- 分支历史另含少量 `agate/` 目录外文件改动（`.gitignore`、`AGENTS.md`、`docs/converse/agents/orchestrator.md`、`docs/reviews/agate-alignment-review-2026-08-10.md`、`docs/progress/*.progress.md`）。独立溯源这些改动所属 commit：`.gitignore`/`docs/converse/agents/orchestrator.md` 来自 `65a9199`（"chore: 接入 orchestrator agent 配置"，环境接入类 chore commit，先于 T001-P1 立项）；`AGENTS.md` 来自 `75a2b9a`/`0d50cc8`（主 Agent 记录执行纪律/工具约定的元文档，非 P4 implementer 产出）；`docs/reviews/*`/`docs/progress/*` 来自 P4 review-fix 流的自查/审查记录本身（`e566303`/`fade134`），属阶段产出物的证据文档，不是"改代码"意义上的 production touch。**这些改动均不在 P4-implementation.md 各流"改动文件清单"中，P4 本身未触碰 `agate/` 目录外的任何代码/协议文件**——P2 packages 声明与 P4 实际代码改动范围一致；上述元文档/chore 类改动不构成对 packages 声明的违反。
- **结论：P4 实际改动文件范围与 P2-design.md §4 声明的 packages:[agate] 一致**（引用：P2-design.md §4、P4-implementation.md 各流"改动文件清单"/"未改动文件"节、git diff main..HEAD --stat）。P8 尚未执行，此处仅确认 P2/P4 范围声明层面无越界，供 P8 bump 范围参照。

### 3.3 P4 实现路径与 P2 设计方案吻合度

- P2-design.md §6 files_to_read 声明的文件清单（`agate-md-field-get.py`/`agate-state-yaml-check.py`/`check-state-yaml.sh`/`check-gate.sh`/`check-pruning.sh`/`check-p6-provenance.sh`/`check-p6-evidence.sh`/`check-p6-format.sh`/`check-scope-resolved.sh`/`check-changelog.sh`/`pre-commit-gate.sh`/`check-protocol-consistency.py`/`task-files.md`/`active-tasks-template.md`/角色卡/phase-cards/`fixtures.bash`/`count-tests.sh`）与 P4-implementation.md 流 A/B/C/D 四节"改动文件清单"逐一核对：**全部命中**，P4 未新增 P2 未声明的改动文件类别（新建的 `agate-frontmatter-check.py`/`check-frontmatter.sh` 属 P2 §1/§3.1.3 明确规划的新交付物，非越界）。
- **结论：P4 六个小节（流 A/B/C/D + Review 修复 + P6 回退修复）的实现路径与 P2-design.md §6 files_to_read 声明范围吻合，无未声明改动**（引用：P2-design.md §6、P4-implementation.md 各流改动文件清单）。

## 4. 未决项清零检查

- P1-requirements.md：`grep -n '^\[NEED_CONFIRM\]\|^\[BLOCKER\]\|^\[DEVIATION-CRITICAL\]'` 无匹配；§5 待确认清单为 `[NO_NEED_CONFIRM]`，3 条历史 `[SUGGEST:]` 均标注"已采纳（archived P1 主 Agent 2026-08-09）"，无残留未决 SUGGEST。新增的 `[BASELINE_CHANGE: 594 → 597]` 标注（第 190 行）不是 NEED_CONFIRM，按角色定义与派发指引第 4 条不构成冲突。
- P1-review.md：frontmatter `status: approved`。
- P2-review.md：frontmatter `status: approved`。
- P4-review.md：frontmatter `status: approved`（复审通过）。
- P6-acceptance.md：全文无 `[NEED_CONFIRM]`/`[BLOCKER]`/`[DEVIATION-CRITICAL]` 标记，28 条结果均为客观 PASS/FAIL 二值判定，无 NEED_CONFIRM 残留。
- **结论：未决项清零，P1/P2/P4 三份评审均 approved，P1 无残留 NEED_CONFIRM/BLOCKER/DEVIATION-CRITICAL**。

## 5. 总体结论

- BLOCKER = 0（独立核实 7 条 DESIGN_GAP 全部代码层面属实且理由站得住，无一条判定为不可接受）
- DEVIATION-CRITICAL = 0
- DESIGN_GAP：7 条声明，7 条已转抄 + REVIEWED 配对（0 条未配对）
- SCOPE+ 闭环：1 处 SCOPE+ ↔ 1 处 SCOPE_RESOLVED，语义匹配，代码现状（锚点表 38 条、consistency 0 ERROR）与登记内容一致
- 跨文件一致性：BDD 数量/内容映射、packages 范围、files_to_read 吻合度均已附具体锚点核实，无裸"一致"结论
- 未决项：P1 无残留 NEED_CONFIRM/BLOCKER/DEVIATION-CRITICAL，三份评审（P1/P2/P4）均 approved

**判定：approved。P7 通过，可进入 P8 发布流程。**
