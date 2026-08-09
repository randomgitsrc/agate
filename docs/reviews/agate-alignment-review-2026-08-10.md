---
review_date: 2026-08-10
reviewer: protocol-alignment-review
change_summary: T001 P4 阶段（流A+B+C+D+fixture修复，293924f..HEAD，25 个文件）把 P1/P2/P6/P7 机器读取字段从"正文内嵌/正则提取"迁移为"frontmatter + pyyaml + schema 校验"，新增 check-frontmatter.sh/agate-frontmatter-check.py 并挂 pre-commit，task_id 规则硬切为 `^T[A-Z]{2}\d+$`
files_changed: [agate/assets/execution-roles/{analyst,architect,verifier}.md, agate/assets/templates/{active-tasks-template,task-files}.md, agate/dispatch-protocol.md, agate/phase-cards/{P1,P2,P6,P7}*.md, agate/role-system.md, agate/scripts/agate-frontmatter-check.py(new), agate/scripts/agate-md-field-get.py, agate/scripts/agate-state-yaml-check.py, agate/scripts/check-changelog.sh, agate/scripts/check-frontmatter.sh(new), agate/scripts/check-gate.sh, agate/scripts/check-p6-format.sh, agate/scripts/check-p6-provenance.sh, agate/scripts/check-protocol-consistency.py, agate/scripts/check-scope-resolved.sh, agate/scripts/pre-commit-gate.sh, agate/state-machine.md, agate/tests/integration/{dispatch-context-card,pre-commit-hook}.bats, agate/tests/unit/check-state-yaml.bats]
---

# 协议-脚本对齐审查（T001 P4 全量，293924f..HEAD）

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED（4 条已声明 DESIGN_GAP 核实无误，未发现新增偏离） |
| A2 | 脚本→文档对齐 | MISALIGNED（1 项：scripts/README.md 未按 P2 FIND-8 承诺同步） |
| A3 | 一致性连锁 + 反向传播 | MISALIGNED（A3a 已知连锁 ALIGNED；A3b 反向传播漏 2 项：WORKFLOW.md 示例、dispatch-protocol.md P6 派发模板） |
| A4 | 测试覆盖 | ALIGNED（600/600 全绿实跑已验证，附输出） |
| A5 | 下游影响 + 文档传播 | MISALIGNED（3 项阻断级低但真实：tests/README.md、scripts/README.md、dispatch-protocol.md；2 项轻微：CONTEXT.md/LIMITATIONS.md 完整性） |
| A6 | 锚点表覆盖 | ALIGNED（37→38 确认，流 B/C/D 复用既有锚点判断正确） |
| A7 | 设计原则一致性 | NEEDS_HUMAN_REVIEW ×1（是否需补 ADR：frontmatter 优于独立 facts 文件的选型） |

---

## 逐项审查

### A1: 文档→脚本对齐

审查方法：对 P2-design.md §3.1-§3.4 声明的每条落点，逐一比对 agate/scripts/ 实际代码。

**流 A（双读工具 + 校验器）**

- P2-design.md §3.1.2 判别契约（FIND-1，字段级 presence 检测）：
  > "字段在 frontmatter 中存在（key 存在且值非 null）→ 取 frontmatter；否则正则回退"（P2-design.md:246-249 伪代码）
  实现（`agate/scripts/agate-md-field-get.py:989-996`）：
  ```python
  def _get(text, op):
      fm = _read_frontmatter(text)
      if isinstance(fm, dict) and op in fm and fm[op] is not None:
          return _format_value(fm[op], op)
      if op in NO_FALLBACK_INT_FIELDS or op in NO_FALLBACK_LIST_FIELDS:
          return ""
      return _regex_fallback(text, op)
  ```
  逐字对应设计伪代码。**结论：ALIGNED**。

- FIND-4 归一化契约（P2-design.md:256）："`ui_affected` 的 ... `_format_value` 对 bool 字段统一 `str(v).lower()` → 输出恰好 `"true"`/`"false"`"。
  实现 `agate-md-field-get.py:936-937`：`if field in BOOL_FIELDS: return str(value).lower() ...`。**ALIGNED**。

- FIND-5 非 dict 硬拦截（P2-design.md §3.1.3 步骤 4）："`safe_load` 结果不是 dict ... 一律报错'frontmatter 必须为 key: value 映射'"。
  实现 `agate-frontmatter-check.py:795-802`：`if not isinstance(data, dict): print("{}: frontmatter 必须为 key: value 映射...")`。**ALIGNED**。

- CHECK 9 锚点新增（P2-design.md §3.1.4）：见 A6。

**流 B（P6/P7 结构化）**

- BDD-16/18 P6 判定（P2-design.md §3.2.1）："frontmatter 声明 pass/fail 汇总（新格式）→ 门禁基于该汇总判定 ... frontmatter 无该汇总（旧格式）→ 回退正文 grep 计数"。
  实现 `check-gate.sh:277-292`（`PASS_FM`/`FAIL_FM` 双非空判新格式，否则回退 `grep -ciE '^\s*- (PASS|FAIL)\b.*BDD-[0-9]'`）。**ALIGNED，但回退正则的严格度是本节唯一偏离**——见下方"已声明 DESIGN_GAP 核实"。

- BDD-19/20 P7 判定（P2-design.md §3.2.2）同构核实，`check-gate.sh:313-345` 一致，AND 语义见 DESIGN_GAP 核实。

- FIND-6 交叉校验 WARNING（P2-design.md:333 "非阻断，属防呆"）。
  实现 `check-p6-provenance.sh:145-153`：新格式下 `P6_TOTAL != P6_BODY_STRICT` 时仅 `echo ... WARNING`，未见任何 `exit 1`。**ALIGNED**。

**流 C（标记状态结构化）**

- BDD-21 逐条匹配（P2-design.md:383 "采用逐条匹配"）：`check-gate.sh:77-93` 用 `NC_UNRESOLVED` 逐条 `grep -qF` 匹配，未见数量相减实现。**ALIGNED**。
- BDD-22 SCOPE 闭环（P2-design.md:388）：`check-scope-resolved.sh:42-45` 非空即通过，空/不存在回退正文 grep。**ALIGNED**（presence 合并处理见下方 DESIGN_GAP 核实）。
- BDD-23 发现性标记保持散文：确认 `[SCOPE+]`/`[PROD_TOUCHED]`/`[DESIGN_GAP]` 均未出现在任何 frontmatter schema 定义中（`agate-frontmatter-check.py` SCHEMAS 字典逐一核对），`check-scope-resolved.sh` 跨文件散文扫描代码未改动。**ALIGNED**。

**流 D（编号硬切）**

- BDD-25/26（P2-design.md §3.4.1）：`agate-state-yaml-check.py:39` `re.match(r"^T[A-Z]{2}\d+$", ...)`，硬切无双格式兼容。**ALIGNED**。
- BDD-27（P2-design.md §3.4.2）：`check-changelog.sh:14` `TASK_ID_SHORT="$TASK_ID"`。**ALIGNED**（fallback 移除见 DESIGN_GAP 核实）。

**已声明 DESIGN_GAP 核实（4 条，P4-implementation.md 主动声明，非本次新发现，逐条核实与实际代码一致）**：

1. **流 A**：`check-gate.sh:173` `FIELD_COUNT=$(grep -cE '^(packages|domains|ui_affected|gate_commands):' ...)` 与 `check-pruning.sh`（全文件未改动，`git diff` 为空）均未迁移到双读工具，靠 frontmatter 字段顶格书写与 grep 巧合兼容。**核实：与 P4-implementation.md:78-90 声明一致**。
2. **流 B**：`check-gate.sh:283`（旧格式回退）用 `grep -ciE '^\s*- (PASS|FAIL)\b.*BDD-[0-9]'`（宽松），而 `check-p6-provenance.sh:142` 用 `grep -cE '^\s*- (PASS|FAIL) BDD-[0-9]'`（严格，与设计原文 P2-design.md:331 逐字一致）——两处口径故意不同。P6/P7 新旧格式判定均为 AND 语义（`check-gate.sh:281 [ -n "$PASS_FM" ] && [ -n "$FAIL_FM" ]`；`:317`；`:336`）。**核实：与 P4-implementation.md:196,198 声明一致**。
3. **流 C**：`check-scope-resolved.sh:42-45` 对"字段存在但空列表"与"字段完全不存在"未做区分（`SCOPE_RESOLVED_FM` 为空字符串时两种情况都落入下方 grep 回退）。**核实：与 P4-implementation.md:342 声明一致**。
4. **流 D**：`check-changelog.sh:36`（注释处）确认移除了设计要求"保留"的 `grep -qF "$TASK_ID"` fallback，理由是该 fallback 会与已恒等的 `TASK_ID_SHORT` 重复裸匹配、误判 `TAG00012` 为 `TAG0001` 已匹配。**核实：与 P4-implementation.md:446 声明一致，且逻辑推理站得住（同一字符串对自身做无边界子串匹配不可能比前一句已用边界正则更严格）**。

**A1 结论：ALIGNED**。4 条已知 DESIGN_GAP 均核实为对已声明内容的准确复述，未发现文档要求但脚本未落实的新增遗漏。

---

### A2: 脚本→文档对齐

- 新工具 `agate/scripts/agate-frontmatter-check.py` / `check-frontmatter.sh`：对应文档在 `task-files.md`、`phase-cards/{P1,P2,P6,P7}*.md`、`analyst.md`/`architect.md`/`verifier.md` 均已同步可复制 frontmatter 样例（BDD-24 落地，`P4-implementation.md:293-338` 逐项核对与实际 diff 一致）。**ALIGNED**。

- **MISALIGNED**：`agate/scripts/README.md:68` 未同步。P2-design.md §13 FIND-8（`P2-design.md:636-640`）明确写："`scripts/README.md`（:68 工具清单表，`agate-md-field-get.py` 条目同步新增 op + 双读语义）"，标注"✅ 已补入（文档类低风险，不改变协议逻辑）"。但实际 `git diff 293924f..HEAD --name-status -- agate/scripts/README.md` 为空，文件内容仍是：
  ```
  | `agate-md-field-get.py` | P1/P2 提取 risk_level/ui_affected/phases | 无 |
  ```
  （`agate/scripts/README.md:68`）——未反映新增的 17 个 op（`candidate_count`/`packages`/`domains`/`override`/`pass`/`fail`/`blocker_count`/`design_gap_count`/`need_confirm_resolved` 等）及双读语义。
  **差异**：设计文档明确声明"已补入"，实现未做。
  **建议**：把 `scripts/README.md:68` 该行更新为反映双读语义 + 完整 op 清单（或至少标注"详见脚本内 docstring"）。

**A2 结论：MISALIGNED**（1 项，低严重度——不影响 gate 行为，属工具清单表文档失实）。

---

### A3: 一致性连锁 + 反向传播

**A3a（已知连锁）**：BDD-24 要求的角色卡/模板/phase-cards 同步样例，8 处改动文件（`task-files.md`、`analyst.md`/`architect.md`/`verifier.md`、`P1/P2/P6/P7-*.md` phase-cards）逐一核对，字段集与 P2-design.md §3.1.1/§3.2.1/§3.2.2 一致，YAML 均可被 pyyaml 解析（P4-implementation.md:384-386 自查记录 + 本次抽查 `task-files.md`/`analyst.md` 样例语法正确）。流 D 的 `active-tasks-template.md`/`state-machine.md`/`dispatch-protocol.md`/`role-system.md` 示例值 T001→TAG0001/TAG0002 逐一核对（diff 中共约 15 处）。**A3a：ALIGNED**。

**A3b（反向传播，主动推断）**：

1. **MISALIGNED**：`agate/WORKFLOW.md:78-79`「任务目录命名约定」：
   ```
   docs/tasks/T001-mcp-namespace-map/
   docs/tasks/T002-fix-db-migration/
   ```
   两个示例任务目录名用的是旧格式 `T\d{3}`（无 2 字母项目代号），在流 D 硬切正则 `^T[A-Z]{2}\d+$`（`agate-state-yaml-check.py:39`）下会被拒绝。P4-implementation.md:429-442 明确列出流 D 改了哪些文档的示例（`state-machine.md`/`dispatch-protocol.md`/`role-system.md`/`active-tasks-template.md`），**未包含 WORKFLOW.md**——该文件本次 diff 中确认零改动（`git diff 293924f..HEAD --name-status -- agate/WORKFLOW.md` 为空）。
   **建议**：`WORKFLOW.md:78-79` 示例改为 `TAG0001-mcp-namespace-map` / `TAG0002-fix-db-migration` 或等价新格式。

2. **MISALIGNED**：`agate/dispatch-protocol.md` 的"P5/P6 派发时追加"派发 prompt 模板（`dispatch-protocol.md:537-553`）——这是主 Agent 实际复制给 verifier subagent 的派发文本，只提到：
   ```
   ## P6 BDD 结果格式
   每条 BDD 验收结果必须用行首 `- PASS` 或 `- FAIL` 格式 ...
   ```
   未提及 BDD-16 要求的 `pass:`/`fail:`/`ui_affected:` frontmatter 汇总字段。经全文 `grep -n "frontmatter" agate/dispatch-protocol.md` 确认**全文件零处提及 "frontmatter"**，尽管本次 diff 确实改动了该文件（仅限流 D 的 task_id 示例值替换，`role-system.md`/`dispatch-protocol.md` 均属此类）。`execution-roles/verifier.md` 本身已含完整样例（`P4-implementation.md:327-330`），故非硬阻断（subagent 读角色文件仍可得知），但该 dispatch 派发模板作为"直接可复制粘贴进 dispatch-context"的机器化载体，遗漏了本次改造的核心内容，属于角色定义的"反向传播常见路径"表明确列出的检查项（`agate/dispatch-protocol.md（P6 结果格式 + gate 表）`）。
   **建议**：在"P5/P6 派发时追加"模板块补一句 frontmatter `pass:`/`fail:`/`ui_affected:` 要求。

**A3 结论：MISALIGNED**（A3a 部分完全 ALIGNED；A3b 反向传播确认 2 项真实遗漏）。

---

### A4: 测试覆盖

**要求的实跑（本次独立重跑，非仅采信派发指引数字）**：

```
$ bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/ agate/tests/sanity.bats
...
ok 600 git-helper.bash: git_commit + git_stage 工作
```
统计：`grep -c "^ok "` = **600**，`grep -c "^not ok "` = **0**。与派发指引 objective_info 声明的"600/600 全绿，0 个 not ok"一致，本次独立重跑复现。

```
$ bash agate/tests/scripts/count-tests.sh
总计：594 个测试用例
```
与 P2-design.md 基线（594）一致，无漂移（BDD-11）。

```
$ python3 agate/scripts/check-protocol-consistency.py
✅ PASS  CHECK 1 ... CHECK 9
🎉 全部检查通过，协议结构一致性无问题。
```
0 ERROR，含 CHECK 9（见 A6）。

```
$ shellcheck -S warning agate/scripts/*.sh
(空输出)
```
0 警告。

**BDD 覆盖抽查**：`grep -oE "BDD-[0-9]+" agate/tests/{unit,regression,integration}/*.bats` 覆盖 BDD-1 至 BDD-23、BDD-25 至 BDD-27（26 条有对应 bats 用例标注）。**BDD-24（角色卡可复制样例）与 BDD-28（本 task 自举 v0.35）未见对应 bats 用例标题**——BDD-24 靠 P4 implementer 手动 `yaml.safe_load` 自查验证（`P4-implementation.md:311-312,384-386`），BDD-28 是任务自身运行时不变式（约束"本 task 用 ~/.agate v0.35 走完全程"，性质上是流程约束而非协议脚本行为，机器可判定性低）。这是覆盖面上的次要缺口，不影响门槛判定的可靠性（新校验器 `check-frontmatter.bats` 已用 `yaml.safe_load` 间接验证同类样例可解析性），故不计入 MISALIGNED。

`unit/check-frontmatter.bats` 新增 **11 个 `@test`**（CF.1-CF.10 对应 P2-design.md 声明的 10 项 + 1 项補充），594 配平口径（P4-implementation.md:92-96）在 P3 阶段已由 test-designer 完成配平，本流 P4 未再变动测试文件（除 T001/T999→TXX 格式修复外）。

**A4 结论：ALIGNED**（数字全部独立复现，无假绿灯迹象）。

---

### A5: 下游影响 + 文档传播

**下游影响（gate 行为破坏性变更检查）**：
- task_id 硬切（BDD-26）是刻意的破坏性变更，P0-brief 已定为"硬切不兼容"，且本次 fixture 修复 commit（68e4173）已把受影响的 33 处旧格式 fixture（`T001`/`T999` 等）改为 `TXX0001`/`TXX0999` 等新格式，`check-state-yaml.bats`/`pre-commit-hook.bats`/`dispatch-context-card.bats` 三个文件的 diff 逐一核对确认为纯 fixture 数据修复，未见测试逻辑被弱化来"制造绿灯"（如放宽断言、删除用例）。**此前 P4-implementation.md 记录的"33 个未清零红灯"（流 D 段落末尾）已通过独立重跑的 600/600 确认清零**。
- CHANGELOG.md 检查：确认 `check-changelog.sh` 仅在 P8 阶段触发（`state-machine.md:221`/`dispatch-protocol.md:836`/`WORKFLOW.md:242` 三处一致："P2.54：仅 P8 检查，P1-P7 不触发"），T001 当前在 P4，CHANGELOG.md 未含 T001 条目**符合预期，非遗漏**。

**文档传播（按派发指引点 6 逐一核对是否遗漏）**：

| 文件 | 本次是否改动 | 判断 |
|------|------------|------|
| `agate/WORKFLOW.md` | 否 | **遗漏**（见 A3b 第 1 项，task_id 示例过期） |
| `agate/orchestrator-template.md` | 否 | 核对无 frontmatter/task_id 格式相关内容（`grep` 全文件 0 命中），无需同步，**不算遗漏** |
| `agate/LIMITATIONS.md` | 否 | 轻微遗漏——见下 |
| `agate/CONTEXT.md` | 否 | 轻微遗漏——见下 |
| `agate/adr.md` | 否 | 见 A7 |
| `agate/scripts/README.md` | 否 | **遗漏**（见 A2，且与设计文档"已补入"的声明矛盾） |
| `agate/tests/README.md` | 否 | **遗漏**——见下 |

**新增细节 1（MISALIGNED）**：`agate/tests/README.md:28-64` 的"覆盖度"表逐脚本列出测试文件+用例数（如 `check-scope-resolved.sh | unit/check-scope-resolved.bats | 11`），但**没有 `check-frontmatter.sh` 这一行**（新增 `unit/check-frontmatter.bats`，11 个 `@test`）。该文档第 79 行自陈维护规则："协议文档声明新规则 → 必须新增对应 .bats 用例"，本次已新增用例但未同步进这张表，表内容与实际测试套件不一致。
**建议**：补一行 `| check-frontmatter.sh | unit/check-frontmatter.bats | 11 |`。

**新增细节 2（轻微，不构成 MISALIGNED，供参考）**：
- `agate/CONTEXT.md` 术语表（`CONTEXT.md:6-30`）未新增 "frontmatter 块"/"presence 语义"/"双读" 等本次改造引入的核心概念术语。该文件自我定位是"补充入口"（非权威来源），且这些概念已在 P2-design.md/scripts docstring 中有权威定义，缺失不影响 gate 判定，但对新读者理解协议有一定成本。
- `agate/LIMITATIONS.md` 未新增"结构化只提高解析可靠性，不改变语义真实性判断"的边界声明。P2-design.md §10（`P2-design.md:556-563`）已在**任务级**文档声明此边界（对应 BDD-14），但 `LIMITATIONS.md` 是**协议级**局限文档，其"局限 3"已经讨论 self-authored gate 的同类问题（`LIMITATIONS.md:21-48`），本次改造是该局限的一个新实例（frontmatter 字段可靠但仍可被主 Agent/subagent 编造），若不在协议级文档留痕，未来其他 subagent 审查协议局限时可能遗漏这一点。

**A5 结论：MISALIGNED**（3 项确认遗漏：WORKFLOW.md、scripts/README.md、tests/README.md；2 项轻微完整性缺口：CONTEXT.md、LIMITATIONS.md，不影响 gate 强度，建议性质）。

---

### A6: 锚点表覆盖

P2-design.md §3.1.4（`P2-design.md:284-291`）声明："既有 37 条全量过一遍 + 新增 1 条 `check-frontmatter.sh` = 38 条；流 B/C/D 不新增锚点，复用既有 `check-gate.sh`/`check-p6-*.sh`/`check-changelog.sh`/`agate-state-yaml-check.py` 锚点"。

**核实 1**：`agate/scripts/check-protocol-consistency.py` 的 `SCRIPT_ALIGNMENT_ANCHORS` 列表用 AST 解析实际元素数：
```
count: 38
```
确认从 37 增至 38，新增条目在 `check-protocol-consistency.py:631-637`：
```python
{
    "desc": "frontmatter schema 校验",
    "script": "agate/scripts/check-frontmatter.sh",
    "keywords": ["frontmatter"],
    "callers": ["agate/scripts/pre-commit-gate.sh"],
},
```

**核实 2**：流 B/C/D 改动的 `check-gate.sh`/`check-p6-format.sh`/`check-p6-provenance.sh`/`check-scope-resolved.sh`/`check-changelog.sh`/`agate-state-yaml-check.py` 均**未**新增独立锚点条目——核对这些脚本原有锚点的 `keywords`（如 `check-gate.sh` 锚点的 `["BDD-[0-9]"]`、`check-changelog.sh` 锚点的 `["CHANGELOG"]`、`agate-state-yaml-check.py` 锚点的 `task_id` 相关关键词）在改造后的代码中依然存在且被匹配（`check-protocol-consistency.py` CHECK 9 独立重跑结果为 PASS，0 ERROR，无锚点关键词丢失警告）。

**核实 3**：反向覆盖检查（`SG.6` 用例，动态 `find agate/scripts -name 'check-*.sh' -o -name 'pre-commit-gate.sh'` 后逐个核对是否在锚点表中）本次独立重跑为 `ok`，确认全部 12 个 `check-*.sh` + `pre-commit-gate.sh` 均有锚点条目覆盖。

**A6 结论：ALIGNED**。37→38 数字、新增条目内容、流 B/C/D 不新增锚点的判断均核实无误。

（附带发现，不计入本项结论）：`SG.6` 用例标题文本仍写"覆盖全部 **11** 个 gate 脚本"（`agate/tests/integration/protocol-alignment-review.bats:46`），但脚本目录下 `check-*.sh` 实际已有 12 个（新增 `check-frontmatter.sh`）。该用例断言逻辑是动态 `find` 而非硬编码数字，功能不受影响，测试本身仍绿；该文件本次未被改动（不在 diff 范围内），标题数字过期属于此前遗留的命名巧合，非本次改造引入的新问题，建议顺手更新但不阻断。

---

### A7: 设计原则一致性

逐条对照 `agate/adr.md` 六条 ADR：

- **ADR-001（隔离性）**：本次改造未涉及主 Agent 是否代写阶段产出，无冲突。
- **ADR-002（可判定性）**：本次改造的核心动机正是强化此原则——`agate-frontmatter-check.py` 把此前依赖散文/正则的隐式判定（如 P7 DESIGN_GAP 数量相减的 0-vs-0 歧义、P6 总结行误判）替换为结构化的、机器可判定的字段读取，是 ADR-002"gate 通过/不通过由脚本 exit code 决定"精神的强化实现，未见任何新增的"主观判断"或"自然语言判断"路径。**一致**。
- **ADR-003（最小约定）**：新工具依赖 `pyyaml`——但 `LIMITATIONS.md:92`（局限 6）已确认 `python3+pyyaml` 是 agate 既有运行时依赖（`agate-state-yaml-check.py` 已在用，`check-protocol-consistency.py` 已在用），本次未引入新依赖，不违反"不绑定被管理项目技术栈"（这是 agate **自身**工具链依赖，非对项目的约束）。**一致**。
- **ADR-004（安全网分层）**：`check-frontmatter.sh` 挂载到 `pre-commit-gate.sh`（`pre-commit-gate.sh:140-150`）与既有 `check-state-yaml.sh` 挂载点同机制，延续"主动验 + hook 兜底"分层模式，未破坏该分层。**一致**。
- **ADR-005（改动性质决定流程）**：本任务自身完整走了 P0-P8（属于"机制交叉"级改动：影响脚本+文档+测试三层），符合该 ADR 判断标准。**一致**。
- **ADR-006（双层角色）**：本次改造未改变评审角色机制（P2/P4 评审仍按 C8 域触发），无冲突。

**NEEDS_HUMAN_REVIEW ×1**：P2-design.md §1（`P2-design.md:44-102`）对"方案 A（frontmatter + 双读工具）vs 方案 B（独立 facts 工具 + .yaml）"做了完整的权衡矩阵（`P2-design.md:84-95`），这是一次实质性的架构选型决策——但 `agate/adr.md` 中未新增对应 ADR 记录该决策（"frontmatter 优于独立事实文件"这一选型，其推理链——"LLM 写两个文件同步失败率高于写一个文件头"——具备可复用价值，未来若有人提议再引入独立 facts 文件，缺少 ADR 会导致同样的论证被重新做一遍）。角色定义（`protocol-alignment-review.md`）A7 条款明确写"如发现未记录的架构决策，建议补充新 ADR"。这属于设计原则完整性问题，不是任何现有 ADR 被违反，故按角色规则只能标 NEEDS_HUMAN_REVIEW，不能标 MISALIGNED。

**[NEEDS_HUMAN_REVIEW: 是否需要为"frontmatter 优于独立 facts 文件"新增 ADR-007？—— 待人工确认]**

**A7 结论：NEEDS_HUMAN_REVIEW ×1**（其余对既有 6 条 ADR 的一致性检查均 ALIGNED，此项待人工裁决是否值得单独立 ADR，非强制阻断）。

---

## 待闭环事项清单（供主 Agent 处理）

| 结论 | 文件:位置 | 问题 | 建议动作 |
|------|----------|------|---------|
| MISALIGNED | `agate/scripts/README.md:68` | 工具清单表未反映新增 op + 双读语义（P2 FIND-8 承诺未兑现） | 补充该行描述 |
| MISALIGNED | `agate/WORKFLOW.md:78-79` | task_id 示例仍用旧格式，过不了新硬切正则 | 改为 TAG0001/TAG0002 格式 |
| MISALIGNED | `agate/dispatch-protocol.md:537-553` | P6 派发模板未提及 frontmatter pass/fail/ui_affected 要求 | 模板块补一句 |
| MISALIGNED | `agate/tests/README.md:28-64` | 覆盖度表缺 check-frontmatter.sh 行 | 补一行（11 用例） |
| 建议（非阻断） | `agate/CONTEXT.md` | 缺 frontmatter/双读/presence 语义术语 | 视优先级补充 |
| 建议（非阻断） | `agate/LIMITATIONS.md` | 局限 3 可补一句本次改造的语义真实性边界 | 视优先级补充 |
| NEEDS_HUMAN_REVIEW | `agate/adr.md` | 是否需新增 ADR 记录 frontmatter vs 独立 facts 文件选型 | 人工确认，若确认需要则补 ADR-007，并附 `[HUMAN_CONFIRMED: ...]` |

以上 4 项 MISALIGNED 均为**文档滞后性问题**（不改变任何已实测的 gate 行为，600/600 测试全绿不受影响），修复成本低（均为纯文档编辑），可由主 Agent 直接处理或另派 implementer 定向修复，无需回退代码。
