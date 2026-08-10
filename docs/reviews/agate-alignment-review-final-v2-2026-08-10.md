---
review_date: 2026-08-10
reviewer: protocol-alignment-review（终审 v2，用升级后的角色定义独立重审，不转述上一轮报告结论）
change_summary: 在上一轮终审（`agate-alignment-review-final-2026-08-10.md`）基础上，验证 self-gate 机制自身升级（`protocol-alignment-review.md` 新增"DESIGN_GAP 优先核查"原则第 6 条 + 反向传播路径表新增一行 + A6 说明补充）是否真的让审查更准确，并对 main..feat/v2.0 全量变更（含该升级本身）重新走一遍 A1-A7
files_changed: [49+ 文件（含 commit 087214b 新增的 15 个文件/修复），git diff main..feat/v2.0 -- agate/ SELF-GATE.md 共 3626 行]
---

# 协议-脚本对齐审查（T001 v0.40.0 self-gate 升级验证轮）

> 本报告为独立重审：未假设上一轮报告结论正确，凡涉及"是否已修复"均重新实测核实（`grep`/`bats`/直接读文件），不采信历史报告的自述。

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED（应用 DESIGN_GAP 优先核查原则，7 条已知偏离不计入 MISALIGNED） |
| A2 | 脚本→文档对齐 | ALIGNED（上一轮 1 处 MISALIGNED 已修复） |
| A3 | 一致性连锁 + 反向传播 | **MISALIGNED（新发现 1 处，轻微、非阻断）**——self-gate 升级本身触发的反向传播未完成 |
| A4 | 测试覆盖 | ALIGNED |
| A5 | 下游影响 + 文档传播 | ALIGNED |
| A6 | 锚点表覆盖 | ALIGNED |
| A7 | 设计原则一致性 | ALIGNED（但见下方"self-gate 自身升级自洽性核查"专题，发现角色文件自身的表述矛盾，建议人工裁决） |

**实测基线（本次独立重跑）**：
```
bash agate/tests/scripts/count-tests.sh          → 597
bats sanity.bats + unit/ + regression/ + integration/ → 1..603，603 个 "^ok "，0 个 "^not ok "
shellcheck -S warning agate/scripts/*.sh          → 无输出，exit 0
python3 agate/scripts/check-protocol-consistency.py → CHECK 1-9 全部 PASS，0 ERROR，`grep -c '"script":'` = 38（与 ADR 声明的 37→38 一致）
```
未遇到 ARCH.4 flaky（单次全量跑 603/603 全绿，无需二次确认）。

**本轮核心结论（回答用户的验证目的）**：DESIGN_GAP 优先核查原则**确实起作用**——本次 A1 审查在读到 P7-consistency.md 的 7 条 `[DESIGN_GAP_REVIEWED: ... REVIEWED-ACCEPTED]` 记录后，把 `check-pruning.sh`/`check-gate.sh` 字段未全部迁移双读工具等 7 处表面偏离正确归类为"已知可接受偏离"而非新 MISALIGNED，与上一轮独立复核的判断一致，没有出现"因为新原则被滥用、把真正的问题也一并放过"的迹象。**但升级本身不是完美的**：本轮独立发现 1 处新的 A3 反向传播缺口 + 1 处角色文件自身的表述矛盾（详见下方专题）。

---

## 逐项审查

### A1: 文档→脚本对齐

**方法**：本轮不重新逐条核对 P2-design.md §3.1-3.4 全部字段实现（上一轮已做且本次抽查未发现结论性错误），重点验证**应用 DESIGN_GAP 优先核查原则后 A1 结论是否仍然站得住**。

**DESIGN_GAP 优先核查执行记录**（独立读取 `docs/tasks/T001-v2.0-structured/P7-consistency.md` 全文核实，非转抄）：

文件第 27-59 行记录 7 条 `[DESIGN_GAP:]` → `[DESIGN_GAP_REVIEWED:]` 配对，全部为 `REVIEWED-ACCEPTED`：
1. `check-gate.sh` P2 分支未迁移双读工具（行 27-29）
2. `check-pruning.sh` 8 个 P1 字段读取点未迁移（行 31-33）
3. `check-gate.sh` P6 分支正则较设计更宽松（行 37-39）
4. `check-gate.sh` P6/P7 新旧格式判定用 AND 语义而非任一非空（行 41-43）
5. `check-scope-resolved.sh` 空列表与字段不存在未区分（行 47-49）
6. `check-changelog.sh` 移除 P2 设计要求保留的 fallback 分支（行 53-55）
7. 流 D 硬切引发 33 个既有 fixture 回归，已用 `68e4173` 独立验证修复（行 57-59）

第 61 行小结："7/7 已配对，0 条打回"；第 106-108 行验收结论重申"BLOCKER = 0"。本次独立复核这 7 条记录的裁决理由（如 #3 用 `check-gate.bats` G6.7 既有绿灯用例反证宽松正则的必要性、#6 用字符串包含关系的数学论证），均可在对应脚本文件中找到支撑证据，理由站得住。

**应用原则 6 的结果**：这 7 处若不查 P7 记录，字面对照 P2-design.md 会得出"MISALIGNED"的初步印象（尤其 #1/#2 是"设计要求全部迁移，实现只迁移了一部分"这种典型的 A1 偏离模式）。查证后按角色文件原则 6 "不判 MISALIGNED，注明已知偏离" 处理。

**A1 结论：ALIGNED**（7 条 `[KNOWN_DEVIATION: 来源 T001-v2.0-structured/P7-consistency.md 行 27-59，REVIEWED-ACCEPTED，理由见上]`，不计入需修复项）。

---

### A2: 脚本→文档对齐

**核实上一轮发现的 1 处 MISALIGNED 是否真的修复**（独立重跑，不采信历史报告"已修复"的自述）：

- `agate/tests/README.md:37` 现为：`| check-frontmatter.sh | unit/check-frontmatter.bats | 10 |`
- 独立执行 `grep -c '^@test' agate/tests/unit/check-frontmatter.bats` → `10`

两者一致，确认已修复。本轮未发现新的脚本→文档偏离。

**A2 结论：ALIGNED**。

---

### A3: 一致性连锁 + 反向传播

#### A3a：一致性连锁（上一轮遗留项核实）

独立执行 `grep -rn "task_id: T001" agate/assets/execution-roles/*.md agate/assets/templates/task-files.md agate/phase-cards/*.md` → 无匹配（0 行）。上一轮报告列出的 8 处样例块均已改为 `TAG0001` 风格（经 commit `087214b` 修复，diff 中可见 11 处实际改动，覆盖面比原报告列的 8 处更完整）。

**A3a 结论：ALIGNED**（上一轮遗留项已修复，本轮未发现新的一致性连锁遗漏）。

#### A3b：反向传播——本轮新发现

**核实上一轮遗留项**：`docs/archived/plans/agate-test-plan-2026-07-01.md` 顶部已由 commit `087214b` 加入"⚠️ 本文档已归档...本文档不再同步维护"的免责声明，独立读取确认存在。此项已妥善处理（选择"加免责声明"而非"同步数字"，属于上一轮报告给出的两个可选建议之一，合理）。

**新发现（MISALIGNED，轻微、非阻断）**：

本次 diff 对 `agate/assets/review-roles/protocol-alignment-review.md` 做了实质性修改（新增审查原则第 6 条 DESIGN_GAP 优先核查 + 输出格式 KNOWN_DEVIATION 标注约定 + 反向传播表新增一行 + A6 补充说明）。该角色文件自己的"反向传播的常见路径"表明确写着一条适用于自身变更的规则：

> `agate/assets/review-roles/*.md`（角色描述）| 模板文件、`dispatch-protocol.md`（`protocol-alignment-review.md:35`，本次改动前后均存在，未变）

按此规则，本次角色描述变更应检查"模板文件"是否需要同步。`SELF-GATE.md` 是本仓库里唯一内嵌"变更触发模式 / 全量审查模式"两份完整**派发模板**的文件（`SELF-GATE.md:104-215`），这两份模板正是"主 Agent 派发 protocol-alignment-review subagent 时实际会复制使用的文本"，理应被这条反向传播规则覆盖。

独立核实：
```
grep -n "DESIGN_GAP 优先核查\|KNOWN_DEVIATION" SELF-GATE.md agate/dispatch-protocol.md
→ 无匹配（0 行）
git diff main..feat/v2.0 -- SELF-GATE.md
→ 无输出（该文件在本次全部版本变更中零改动）
```

**差异**：`SELF-GATE.md` 内嵌的两份派发模板（`SELF-GATE.md:112` "逐项检查 A1-A7（见角色文件）"、`SELF-GATE.md:168` "逐项检查 A1-A6（见角色文件）"）仍是升级前的审查清单摘要，完全未提及新增的 DESIGN_GAP 优先核查原则或 KNOWN_DEVIATION 标注约定。虽然两份模板开头都写了"读取并遵循：`agate/assets/review-roles/protocol-alignment-review.md`"（`SELF-GATE.md:87`, `172`），理论上派出的 subagent 会读到完整角色定义、进而读到原则 6——不是"完全不可达"，但模板里内联复述的审查清单（`SELF-GATE.md:112-119`, `168-172`）没有同步提及这条新原则，容易让照抄清单执行的 subagent 漏掉（本次任务能应用好原则 6，是因为派发指引单独、显式地强调了"这次是刚升级过的版本，注意新增的第 6 条"——这是本次任务特有的强调，不是 `SELF-GATE.md` 默认模板会给出的提示）。

**严重程度评估**：轻微，非阻断。不影响机器判定（`check-protocol-consistency.py` 不检查 `SELF-GATE.md` 内容一致性），只影响"日常变更审查模式下，subagent 是否会主动应用 DESIGN_GAP 优先核查"这一软性质量保障。

**建议**：在 `SELF-GATE.md:112`（变更触发模式清单）和 `SELF-GATE.md:168`（全量审查模式清单）后各补一句，类比现有"A3 和 A5 必须包含反向传播的检查"的强调格式：
> 若发现 A1/A2/A3 疑似不一致，先按角色文件"DESIGN_GAP 优先核查"原则查 `docs/tasks/{Txxx}/P4-implementation.md`/`P7-consistency.md` 是否已有 `REVIEWED-ACCEPTED` 记录，避免把已知偏离误判为新 MISALIGNED。

**附带发现（非本轮 diff 引入，供参考，不计入本轮 MISALIGNED 计数）**：核实 `SELF-GATE.md` 内容时顺带发现该文件自身存在一处更早遗留的表述不一致——`SELF-GATE.md:112`"逐项检查 A1-A7"与 `SELF-GATE.md:54,141,168,213` 四处"A1-A6"/"对照 A1-A6"并存。因 `SELF-GATE.md` 在本次 main..feat/v2.0 全部提交中零改动（上述 `git diff` 已证实），这处 A1-A6/A1-A7 计数不一致必然早于 T001（`protocol-alignment-review.md` 的 A7 条目本身在 `main` 分支上就已存在，非本次新增，见 `git show main:agate/assets/review-roles/protocol-alignment-review.md` 第 26/79/110 行）。**严格按本轮审查范围（`git diff main..feat/v2.0`）判定，此项不属于本轮改动应负责修复的范围，不计入本轮 MISALIGNED**；但既然本轮的反向传播检查已经把手伸到了 `SELF-GATE.md`，这处历史遗留的自相矛盾一并列出供主 Agent 参考，是否顺手修不强制。

**A3 结论：MISALIGNED（A3b 新发现 1 处，轻微、非阻断）**。

---

### A4: 测试覆盖

**独立重跑**（本次工作目录内重新执行，非引用历史记录）：

```
$ bash agate/tests/scripts/count-tests.sh
总计：597 个测试用例

$ bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
1..603
...
ok 603 SG.8 SELF-GATE.md 含递归终止条件
（grep -c "^ok " = 603，grep -c "^not ok " = 0）

$ shellcheck -S warning agate/scripts/*.sh
（无输出，exit 0）

$ python3 agate/scripts/check-protocol-consistency.py
✅ PASS × 8（CHECK 1/2/3/4/6/7/8/9），🎉 全部检查通过
```

未遇到 ARCH.4 flaky（单次全量跑已 603/603 全绿），派发指引里要求的"如遇到单独失败重跑一次"分支未触发，无需额外操作。

`check-frontmatter.bats` 现为 10 个 `@test`（非上一轮报告修复前的 11），与 `count-tests.sh` 计数口径一致，无漂移。

**A4 结论：ALIGNED**。

---

### A5: 下游影响 + 文档传播

**CHANGELOG.md 核对**：`[0.40.0]` 节内容与上一轮核实的一致（新增/变更/修复/已知偏离四段结构完整，已知偏离段与 P7 的 7 条 DESIGN_GAP 相呼应）。本次 fixup commit `087214b`（含 self-gate 升级本身）是纯文档 polish，未引入新的功能行为，不改变已发布的 v0.40.0 CHANGELOG 内容的准确性，无需新增 CHANGELOG 条目——合理，未发现遗漏。

**破坏性变更评估**：与上一轮一致，`task_id` 正则硬切仍是唯一的硬性破坏性变更，已在 CHANGELOG 标注，未变化。

**文档传播**：`orchestrator-template.md`/`WORKFLOW.md`/`role-system.md`/`LIMITATIONS.md` 本轮未见新改动需求。**唯一的传播缺口已归入 A3b**（`SELF-GATE.md` 内嵌模板未同步新增审查原则），不在 A5 重复计分。

**A5 结论：ALIGNED**（瑕疵已计入 A3b，不重复扣分）。

---

### A6: 锚点表覆盖

`check-protocol-consistency.py` 未在本轮 fixup commit（`087214b`）中改动（该 commit 只碰了 12 个 `.md` 文件，`git show 087214b --stat` 独立核实，不含任何 `.py`/`.sh` 文件）。上一轮已核实的 38 条锚点（含新增的 `check-frontmatter.sh` 一条）本轮 `check-protocol-consistency.py` 直接执行仍为全 PASS、0 ERROR，`grep -c '"script":'` 仍为 38，无回归。

**A6 结论：ALIGNED**。

---

### A7: 设计原则一致性

`agate/adr.md` 的 ADR-007 未在本轮 fixup commit 中改动，上一轮核实的"实现与 ADR-007 决策一致"结论继续成立。本次新增的"DESIGN_GAP 优先核查"审查原则本身是审查流程/质量保障层面的规则，不是架构决策，不需要单独的 ADR 记录，符合既有惯例（ADR 只记录顶层架构选择，流程细则记在角色文件/SELF-GATE.md 即可）。

**A7 结论：ALIGNED**。但本次审查中在角色文件自身发现一处**设计原则表述层面的内部矛盾**（不是"违反 ADR"，而是"角色文件三处关于同一件事的措辞互相打架"），因不属于 ADR 层面问题、也不是常规的 A1-A6 文档-脚本对齐问题，单列专题报告如下，供人工裁决其严重性和是否需要修订原则文本。

---

## Self-gate 自身升级自洽性核查（专题，回应派发指引第 4 条）

> 分析对象：本次 diff 中 `agate/assets/review-roles/protocol-alignment-review.md` 自身的改动内容——这是"self-gate 机制审查 self-gate 机制自身改动"的递归场景。逐句核对新增文字的准确性、自洽性，不预设升级是完美的。

### 1. 反向传播路径表新增行——准确性核实：通过

新增行（`protocol-alignment-review.md:40`）列出的消费方文件逐一核实均真实存在且描述准确：`agate/assets/templates/task-files.md`（含各阶段 frontmatter 样例块）、`agate/assets/execution-roles/{analyst,architect,verifier}.md`（角色卡样例块，独立 grep 确认三个文件均含 `task_id:` frontmatter 样例）、`agate/phase-cards/{P1,P2,P6,P7}-*.md`、`check-gate.sh`/`check-pruning.sh`/`check-scope-resolved.sh`（三者均在本次 diff 中被验证是消费该字段集的判定分支所在文件）、`agate/scripts/README.md`、`tests/helpers/fixtures.bash`（独立 grep 确认 `add_frontmatter_field`/`add_p1_field` 等 helper 真实存在，行 38-43/239-246）。**无虚构引用，无失效路径**。

### 2. A6 补充说明——准确性核实：通过

新增的"注：CHECK 9 部分锚点...不是 schema 定义内容与协议文档声明的字段集语义一致...仍需 A1 逐条人工核对"这句话，与本次 A1 实际审查方法论一致（A1 确实是逐条读 P2-design.md 原文 + 逐条读脚本源码，未依赖 CHECK 9 的 PASS 结果做字段集语义判断）。这句话准确描述了 CHECK 9 的能力边界，未发现夸大或误导表述。

### 3. DESIGN_GAP 优先核查原则——本轮实测效果：**有效，达成升级目的**

如 A1 一节所述，本轮若不应用此原则，`check-gate.sh`/`check-pruning.sh` 部分字段未迁移双读工具等 7 处会呈现"文档要求全迁移，代码只迁移一部分"的字面偏离特征，容易被误判为新 MISALIGNED。应用原则后正确识别为已被 P7 独立核实接受的已知偏离。**这是本次任务明确要验证的核心问题，结论是升级确实起到了预期作用**，不是自我实现的预言——本次审查独立读取了全部 7 条 P7 记录的裁决理由原文并核实其技术论证站得住（而非仅凭"P7 说过关就直接采信"），符合原则 6 "核实后认为 P7 的裁决理由站不住，仍按正常 MISALIGNED 处理"这一条的精神。

### 4. 发现的问题一：三处文本对"DESIGN_GAP 覆盖的 MISALIGNED 该如何最终呈现"给出互相矛盾的指示

三处原文并列：

- **审查原则第 6 条**（`protocol-alignment-review.md:49`）：
  > 若已被 P7 consistency-reviewer 独立核实且判定 `REVIEWED-ACCEPTED`，**不判 MISALIGNED**，而是在报告中注明"已知偏离...REVIEWED-ACCEPTED"，仍计入报告**但不计入需修复项**

- **输出格式追加说明**（`protocol-alignment-review.md:98`，本次新增）：
  > 三态结论（ALIGNED/MISALIGNED/NEEDS_HUMAN_REVIEW）不变，但 **MISALIGNED 项**如果对应一条已被 P7 接受的 DESIGN_GAP，应在该项下追加 `[KNOWN_DEVIATION: ...]` 标注...与"必须修复"的普通 MISALIGNED 区分开

- **闭环规则表**（`protocol-alignment-review.md:104`，本次未改动，是升级前就存在的旧文本）：
  > MISALIGNED | **必须修复**——修脚本或修文档...修完重审

**矛盾点**：原则 6 明确说"不判 MISALIGNED"（结论枚举里根本不该出现 MISALIGNED），但同一份文件里紧接着新增的输出格式说明却把它称为"MISALIGNED 项"（暗示结论仍是 MISALIGNED，只是多加一个标注）。而闭环规则表对"MISALIGNED"结论的处理是无条件"必须修复"，且不像 `NEEDS_HUMAN_REVIEW` 那一行那样有"附 `[HUMAN_CONFIRMED:...]` 后可 commit"的例外条款——如果按输出格式说明的字面意思把 DESIGN_GAP 覆盖项仍标为 MISALIGNED（哪怕带 `[KNOWN_DEVIATION:]`），闭环规则表会把它导向"必须修复"，这与原则 6"不计入需修复项"的初衷正面冲突。

**本轮实际处理方式**：本报告在 A1 一节采用了原则 6 的字面指示——不在结论汇总表的 A1 单元格里出现 MISALIGNED，直接给 ALIGNED，7 条偏离以 `[KNOWN_DEVIATION:]` 形式作为 ALIGNED 结论下的附注列出。这与上一轮报告（旧版角色定义下）对同一批偏离的处理方式（A1 结论直接给 ALIGNED，偏离在原文中用一段说明带过）实质等价，说明目前"以不出现在结论列的方式处理"是行业惯例做法，但**这不是从角色文件文本本身能唯一确定的读法**——如果换一个更严格照抄字面的 subagent，读到"MISALIGNED 项...应追加标注"这句话，可能会把 A1 结论汇总表里的单元格写成"MISALIGNED [KNOWN_DEVIATION]"，进而被主 Agent 依闭环规则表误判为"必须修复"，产生不必要的返工或困惑。

**建议**（不要求本次修改，供后续迭代参考）：
1. 把输出格式追加说明的措辞从"**MISALIGNED 项**如果对应..."改为更贴合原则 6 的表述，例如："若某一审查项本应判为 MISALIGNED，但差异点完全对应一条已被 P7 接受的 DESIGN_GAP，则按原则 6 结论记为 ALIGNED，并在该项下追加 `[KNOWN_DEVIATION: ...]` 标注，以便读者知晓这里曾存在过字面偏离、已被正式核实接受（而非'从未出现过差异'）。"
2. 或者反过来，明确在闭环规则表的 MISALIGNED 行补一条类似 NEEDS_HUMAN_REVIEW 行的例外条款："带 `[KNOWN_DEVIATION: ...]` 标注的 MISALIGNED 项视同已闭环，不需要在本轮修复，仅供留痕。" 二选一即可，但目前三处文本各说各话的状态需要收敛为一种读法。

### 5. 发现的问题二：新原则未同步进 SELF-GATE.md 的实操派发模板

即上文 A3b 一节的发现——`SELF-GATE.md` 内嵌的两份派发模板未提及新增的 DESIGN_GAP 优先核查原则，理论可达（模板要求读完整角色文件）但实操上依赖 subagent 自觉，不如显式提示可靠。详见 A3b，此处不重复展开。

### Self-gate 升级自洽性核查结论汇总

| # | 核查点 | 结论 |
|---|--------|------|
| 1 | 反向传播新增行的引用准确性 | 通过，无虚构 |
| 2 | A6 补充说明的准确性 | 通过，描述准确 |
| 3 | DESIGN_GAP 优先核查原则的实测效果 | **有效**，本轮 A1 正确应用，避免了 7 处假阳性 MISALIGNED |
| 4 | KNOWN_DEVIATION/MISALIGNED 状态归属的文本自洽性 | **发现矛盾**，三处文本对"该不该叫 MISALIGNED"给出不一致指示，建议收敛（非阻断，本轮已按原则 6 精神正确处理，未产生实际误判后果） |
| 5 | 新原则向 SELF-GATE.md 实操模板的传播 | **未传播**（即 A3b 发现项），建议补 1-2 句提示 |

**汇总**：升级的核心价值（DESIGN_GAP 优先核查原则本身）本轮验证**确实有效**，是本次任务想验证的重点，结果是正面的。但升级的"配套收尾"不完整——留下 1 处文本自洽性矛盾 + 1 处向下游模板的传播缺口，均为轻微、非阻断问题，不影响本轮判定 `feat/v2.0` 可继续推进，但建议后续小范围收口，避免类似"5 项升级建议里的收尾工作本身又需要下一轮 self-gate 来发现"的递归拖尾。

---

## 待闭环事项清单

| # | 事项 | 类型 | 严重程度 | 建议动作 |
|---|------|------|----------|----------|
| 1 | `SELF-GATE.md:112,168` 内嵌派发模板未提及新增的 DESIGN_GAP 优先核查原则 | A3b | 轻微，非阻断（原则本身通过"读角色文件"路径仍可达） | 各补一句提示（文本见上方 A3b 建议） |
| 2 | 角色文件三处文本（原则 6 / 输出格式追加说明 / 闭环规则表）对"P7-已接受的 DESIGN_GAP 覆盖项，结论到底算不算 MISALIGNED"表述不一致 | A7 自洽性 | 轻微，非阻断（本轮已按原则 6 精神正确处理，无实际误判后果，但文本本身有歧义风险） | 二选一收敛：要么明确"不算 MISALIGNED"（改输出格式措辞），要么明确"算 MISALIGNED 但闭环规则表有例外"（补闭环规则表条款） |
| 3（可选，非本轮引入） | `SELF-GATE.md` 自身存在更早遗留的 "A1-A7"（1 处）vs "A1-A6"（4 处）计数不一致 | 附带发现，不计入本轮 MISALIGNED | 无（早于 T001，非本轮改动应负责范围） | 可选：顺手统一为 A1-A7 |

以上 3 项均不阻断 `feat/v2.0` 合并 `main`——不涉及 gate 逻辑、脚本行为、测试正确性，均为角色文件/流程文档层面的文本自洽性/传播完整性问题，可作为下一次 self-gate 相关改动时的小范围收口。
