---
review_date: 2026-08-19
reviewer: protocol-alignment-review
change_summary: TAG0015 P4——复盘机制统一（模板迁入协议本体+归因分层+事实依据分层+check-retrospective.py 新增机制缺口检测分支+state-machine.md 新增 L2 会话 checkpoint 两件套+AGENTS.md 措辞同步）与跨项目反馈新增（agate-feedback.py，opt-in）
files_changed: [agate-workspace/roadmap/roadmap.md, agate-workspace/tasks/TAG0015-retrospective-feedback/P4-dispatch-context-implementer.md, agate-workspace/tasks/TAG0015-retrospective-feedback/P4-implementation.md, agate-workspace/tasks/TAG0015-retrospective-feedback/P4-progress.md, agate-workspace/tasks/TAG0015-retrospective-feedback/orchestrator-log.md, agate/AGENTS.md, agate/assets/templates/retrospective-template.md (git mv from docs/reviews/postmortem-template.md), agate/assets/templates/task-files.md, agate/phase-cards/P8-release.md, agate/scripts/agate-feedback.py (new), agate/scripts/check-retrospective.py, agate/state-machine.md, docs/reviews/retrospective-tag0008-docs-20260817.md, docs/reviews/retrospective-tag0010-0011-docs-20260815-review.md, docs/reviews/retrospective-tag0010-0011-docs-20260815.md, docs/reviews/retrospective-tag0013-docs-20260816.md, docs/reviews/retrospective-tag0014-docs-20260816.md]
---

# 协议-脚本对齐审查

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | ~~MISALIGNED（1 项，见下）~~ → **ALIGNED（复核轮 #1 已修复，见文末「复核轮（重试 #1）」）** |
| A3 | 一致性连锁 + 反向传播 | A3a ALIGNED / A3b ~~MISALIGNED（3 项，见下）~~ → **ALIGNED（复核轮 #1 已修复）** |
| A4 | 测试覆盖 | ALIGNED（附实跑数据，含一条与本次 diff 无关的预置失败说明） |
| A5 | 下游影响 + 文档传播 | ~~MISALIGNED（与 A2/A3b 同源的 2 项文档登记缺口）~~ → **ALIGNED（复核轮 #1 已修复）** |
| A6 | 锚点表覆盖 | ALIGNED |
| A7 | 设计原则一致性 | ~~NEEDS_HUMAN_REVIEW（1 项，ADR-007 适用范围）~~ → **ALIGNED（复核轮 #1，用户裁决：扩展 agate-md-field-get.py 合规）** |

---

## 逐项审查

### A1: 文档→脚本对齐

**文档声明**（`agate/state-machine.md:492-518` diff 新增「L2 会话 checkpoint（两件套）」小节）：
> `P{n}-checkpoint.md`……不是阶段门槛产出（gate 不要求其存在，属「辅助文件」），缺失不阻断阶段推进……`task-session-summary.md`……P8 gate 通过后主 Agent 亲自写盘，写完即完成使命，不需回读校验

该小节明确声明两个 L2 文件**不受任何 gate 脚本强制**。核实：仓库内无任何 `check-*.py` 引用 `P{n}-checkpoint.md`/`task-session-summary.md`（`grep -rn "checkpoint\|task-session-summary" agate/scripts/*.py` 零命中）——脚本侧"无实现"与文档侧"声明为非门槛辅助文件"完全一致。

**脚本实现**（`agate/scripts/check-retrospective.py:66-90` `_scan_debt_roadmap_signal`）：
```python
tid = _task_id(state_file)  # 调 agate-state-get.py task_id
workspace = os.path.dirname(os.path.dirname(os.path.abspath(task_dir.rstrip(os.sep))))
...
if os.path.isfile(debt_file): ... re.search(DEBT_TASK_ID_RE_TEMPLATE...)
if os.path.isfile(roadmap_file): ... re.search(ROADMAP_TASK_ID_RE_TEMPLATE...)
```
对应 `P2-design.md` §1.1 类 4.2 BDD-10 给出的 6 步伪代码逐条落地；`agate-state-get.py:37-39` 实读确认 `task_id` op 已存在（`elif op == "task_id": data = _load(...); print(data.get("task_id", "") ...)`），未新增该脚本代码，与设计声明一致。

**结论**：ALIGNED

---

### A2: 脚本→文档对齐

**脚本实现**（`agate/scripts/check-retrospective.py:144-150`，`main()` 新增分支）：
```python
if os.path.isdir(task_dir):
    debt_roadmap_tid = _scan_debt_roadmap_signal(task_dir, state_file)
    if debt_roadmap_tid:
        sys.stderr.write("GATE RETRO: 建议复盘 — 发现机制缺口信号：\n")
        sys.stderr.write(f"  - {debt_roadmap_tid} 关联的 DEBT/roadmap 条目已登记（可能存在机制缺口，建议复盘归因）\n")
```
这是一条**独立于**既有"异常模式"（重试超限/SCOPE+/override）的新触发类别——标题文案（"发现机制缺口信号"）与既有"检测到异常模式"刻意区分（`test_tag0015_bdd10_debt_signal_triggers_mechanism_gap_reminder` 断言 `"检测到异常模式" not in result.output`），语义上是新增了第 4 类触发条件。

**文档声明**（`agate/WORKFLOW.md:318`，Pre-commit 检查总览表，唯一权威锚点）：
> `2.12 | check-retrospective.py | gate 任何结果 | 阶段级 | 异常模式提醒（重试超限/SCOPE+/override）→ 写复盘；不阻塞 commit（P2.12）`

该行仍只描述旧 3 类"异常模式"，未提及新增的第 4 类"机制缺口信号（DEBT/roadmap 已登记）"触发条件——这是一个语义不同的新类别（不是异常，而是"正常流程里机制缺口已被登记"的信号）。

**结论**：MISALIGNED
**差异**：`agate/WORKFLOW.md:318` 是本仓库对 check-retrospective.py 触发行为的唯一权威描述锚点（协议-脚本对齐审查角色文件"反向传播常见路径"表明确要求"新增/修改某个 check-*.py 的 pre-commit 触发行为 → 只需同步 WORKFLOW.md「Pre-commit 检查总览」一处"）。`P2-design.md:174-180` 对"不改 WORKFLOW.md:318"的免改理由只针对 BDD-9（脚本内 stderr 路径文案变更），未讨论 BDD-10（新增触发分支）是否也落在该行的描述范围内——即设计阶段未识别到 BDD-10 应传播到此处。
**建议**：在 `agate/WORKFLOW.md:318` 表格行的行为列追加一句，如"…（不阻塞 commit）；另检测到 DEBT/roadmap 已登记本任务 → 追加'机制缺口信号'提醒（P2.12/TAG0015）"，或拆成两行/加脚注区分两类提醒的性质差异（异常 vs 正常但值得复盘）。

---

### A3: 一致性连锁 + 反向传播

#### A3a：连锁（已知的衍生改动）

核实以下衍生改动均已正确同步，与设计意图一致：

| 源改动 | 衍生文件 | 核实结果 |
|---|---|---|
| 模板迁移（BDD-1~8） | `agate-workspace/roadmap/roadmap.md:313,316,322` | 三处路径字符串已追加脚注式更正，未删减原叙述文字，符合 `P2-design.md:60-66` 的"不重写历史"要求 |
| L2 checkpoint 新增（BDD-13） | `agate/assets/templates/task-files.md:46-47` | 「辅助文件」表新增两行，未动"各阶段文件清单"门槛表，符合 `P2-design.md:186-189` "不改门槛表"声明 |
| 模板挂钩点（BDD-8） | `agate/phase-cards/P8-release.md:95-97` | READY 收尾检查节新增核对项，含 `agate/assets/templates/retrospective-template.md` 字面路径字符串 |
| 复盘位置措辞（BDD-15） | `agate/AGENTS.md:11` | 按 P2 给定原文逐字替换 |
| 存量文件标注（BDD-16） | `docs/reviews/retrospective-tag00{08,10-0011×2,13,14}-*.md` | 5 个文件逐字命中同一标注模板文案，无遗漏无走样 |

**结论**：ALIGNED

#### A3b：反向传播（主动推断的应被影响文档）

按角色文件"反向传播常见路径"表逐条核查：

1. **`agate/dispatch-protocol.md`**：`grep -n "postmortem\|retrospective\|复盘\|checkpoint\|agate-feedback\|AGATE_FEEDBACK" agate/dispatch-protocol.md` 零命中。P1 已判定该文件不是 BDD-8 挂钩点选定对象（挂钩点在 `phase-cards/P8-release.md`），且实读确认改动前后该文件确无任何相关字符串——**ALIGNED**，P1 的"不改"判断与实际情况一致。

2. **`agate/WORKFLOW.md:318`**：见 A2，**MISALIGNED**（同一发现，A2/A3b 共享同一差异点，不重复计数为两个独立问题）。

3. **`agate/scripts/README.md`**（工具清单表）：
   - `agate/scripts/README.md:37`：`check-retrospective.py (P2.12) | 异常模式提醒（不阻塞）| 0=总是通过` ——同 A2 的问题，未提机制缺口信号分支。
   - 全文 `grep -n "agate-feedback" agate/scripts/README.md` 零命中——**新增脚本 `agate-feedback.py` 完全未登记进工具清单表**，该表是仓库对所有 `agate/scripts/*.py` 的唯一权威索引（角色文件"常见路径"表明确要求 `check-*.py（脚本行为）→ agate/scripts/README.md`，新增脚本理应比照登记）。
   - **结论：MISALIGNED**。
   - **建议**：`agate/scripts/README.md` 新增一行 `agate-feedback.py | 跨项目反馈提取（AG0021，opt-in，AGATE_FEEDBACK=on）| 手动触发，非 gate/非 pre-commit`；`check-retrospective.py` 行补充机制缺口信号分支的一句话描述。

4. **`agate/tests/README.md`**（覆盖度表）：
   - `check-retrospective.py | unit/test_check_retrospective.py | 10`——实读 `grep -c "^def test" agate/tests/unit/test_check_retrospective.py` = **15**。此项测试增量（BDD-9/10 相关 5 个新用例）是在 P3 阶段提交 `fbd9c31` 时引入的，**不属于本次 P4 diff 范围**（`git diff --cached --stat -- agate/tests/` 为空——本次 P4 未改任何测试文件），故不计入 P4 本次的 MISALIGNED，但作为沿袭旧债在此记录，建议一并处理。
   - `agate-feedback.py`/`test_agate_feedback.py`（8 个测试函数）与 `test_retrospective_protocol_docs.py`（13 个测试函数，覆盖 BDD-1~8/12~16）**完全未在覆盖度表中登记**——这两个测试文件是本次 P4 实现落地时新增的，理应同步登记进该表（`agate/tests/README.md` 明确是"给协议 maintainer"的自检索引，覆盖度表用途就是"新脚本/新测试文件不漏登")。
   - **结论：MISALIGNED**（P4 新增部分应登记而未登记；check-retrospective.py 计数误差是 P3 遗留旧债，一并列出供修复参考）。
   - **建议**：新增两行 `agate-feedback.py | unit/test_agate_feedback.py | 8`、`复盘协议文档条文 | unit/test_retrospective_protocol_docs.py | 13`；顺带把 `check-retrospective.py` 行的用例数从 10 更正为 15。

5. **`agate/loop-orchestration.md:168,173`**：已实读，`"只写决策和下一步"` 不在文中出现（`test_bdd_14_cross_file_orchestrator_log_consistency` 同款断言），核实 P1/BDD-14"三处均不与新规则矛盾，不改"的结论准确——**ALIGNED**。

6. **CHANGELOG.md**：`git diff --cached -- CHANGELOG.md` 为空；当前 `[Unreleased]` 区块不存在，最新已发布版本为 0.52.0。任务当前阶段为 P4（未到 P8），按 `WORKFLOW.md` 表格第 1.6 行 `check-changelog.py` 触发条件"P8 phase 且 gate 通过后"，P4 阶段本就不要求登记——**ALIGNED（符合预期，非遗漏，P8 阶段会处理）**。

7. **是否有其他脚本消费 `check-retrospective.py` 的输出格式**：`grep -rn "GATE RETRO" agate/` 只命中脚本自身与其测试文件，无其他消费方——新增分支不破坏任何下游解析器，**ALIGNED**。

8. **CHECK 9 锚点表新增需求**：见 A6，`agate-feedback.py` 不匹配 `check-*.py` glob，不需要锚点——**ALIGNED**。

**A3b 汇总结论**：MISALIGNED（3 项：WORKFLOW.md:318 与 A2 共享同一差异 / agate/scripts/README.md 缺 agate-feedback.py 登记 + 触发行为描述未更新 / agate/tests/README.md 缺两个新测试文件登记）

---

### A4: 测试覆盖

**新增/改动逻辑对应测试**：

| BDD | 覆盖测试 | 边界情况 |
|---|---|---|
| BDD-9（stderr 路径文案）| `test_tag0015_bdd9_stderr_hint_points_to_task_dir` | — |
| BDD-10（DEBT/roadmap 信号，两条正则）| `test_tag0015_bdd10_debt_signal_triggers_mechanism_gap_reminder`、`test_tag0015_bdd10_roadmap_signal_triggers_mechanism_gap_reminder` | 两条独立正则路径分别覆盖；断言 `"检测到异常模式" not in output` 确认与旧提醒文案互相独立可区分；用手搭两级嵌套目录 fixture 隔离验证工作区路径推导逻辑 |
| BDD-17（解析）| `test_bdd17_extracts_mechanism_issues_from_frontmatter_and_section` | — |
| BDD-18（脱敏）| `test_bdd18_anonymize_project_name_replaced_with_placeholder`、`test_bdd18_anonymize_absolute_path_removed_or_relativized` | 项目名 + 绝对路径两类规则分别覆盖 |
| BDD-19（开关）| `test_bdd19_env_unset_produces_no_output_and_disabled_message`、`test_bdd19_env_explicit_off_produces_no_output_and_disabled_message` | 未设置环境变量 + 显式设为非 on 两种情形 |
| BDD-20（输出格式 + 无网络提交）| `test_bdd20_source_contains_no_network_submit_calls`、`test_bdd20_stdout_contains_markdown_issue_body_snippet` | 源码 grep 断言无 subprocess/gh/git push |
| BDD-1~8/12~16（协议文档条文）| `test_retrospective_protocol_docs.py` 13 个函数 | 逐 BDD 一个函数，风格与仓库既有 `test_review_role_docs.py`/`test_protocol_mechanism_anchors.py` 一致（关键词锚点断言，非语义解析） |

**实跑输出**（本次审查独立实跑，非转述 subagent 自报）：

```
$ timeout 120s python3 -m pytest agate/tests/unit/test_check_retrospective.py agate/tests/unit/test_agate_feedback.py agate/tests/unit/test_retrospective_protocol_docs.py -q
35 passed in 1.47s

$ timeout 180s python3 -m pytest agate/tests/ -q --tb=no
929 passed, 3 failed, 2 skipped in 92.83s
FAILED agate/tests/unit/test_check_pruning.py::test_p2_6e_prune_p7_coupling_checklist_exit_0
FAILED agate/tests/unit/test_check_pruning.py::test_p2_52_yaml_list_phases_exit_0
FAILED agate/tests/unit/test_check_pruning.py::test_p2_52b_yaml_list_phases_p3_pruned_low_exit_0
```

对这 3 个失败做了 A/B 核实：`git stash`（完整暂存区，含索引）后重跑 `test_check_pruning.py`，改动前同样 3 failed/26 passed——与本次 diff 无关（`check-pruning.py` 未出现在本次改动文件列表中），确认是预置于当前工作区/环境的既有失败，不因本次 TAG0015 P4 改动引入或加剧。

**结论**：ALIGNED（新逻辑测试覆盖充分，含正/负两类边界；全量回归除已排除的 3 个不相关预置失败外全部通过）
**附注**：3 个 `test_check_pruning.py` 失败与本次审查对象无关，但按 A4 硬性要求如实附上完整实跑计数，不做静默过滤；建议主 Agent 另行登记 DEBT 或在其他任务中跟进，不阻塞本次 commit。

---

### A5: 下游影响 + 文档传播

**exit code 契约**：`check-retrospective.py` 新分支不改变 `sys.exit(0)` 恒定契约（`P2-design.md §1.2` 显式声明"不改变这个契约"，代码实读确认 `main()` 末尾仍为无条件 `sys.exit(0)`）——**无破坏性变更**。

**CHANGELOG.md**：见 A3b 第 6 点，P4 阶段不要求登记，符合既有触发条件（P8 phase-only）——ALIGNED，非遗漏。

**文档传播（除 A3b 已列出的 WORKFLOW.md / scripts/README.md / tests/README.md 三处）**：
- `orchestrator-template.md`：`grep -n "postmortem\|retrospective\|checkpoint" agate/orchestrator-template.md` 零命中，该文件不描述具体 pre-commit 检查表或复盘细节，不需要同步。
- `role-system.md`：同样零命中，不涉及。
- `LIMITATIONS.md`：零命中，本次改动不涉及已知局限性描述范围。

**结论**：MISALIGNED（与 A3b 同源的 2 项文档登记缺口：`agate/scripts/README.md` 未登记新脚本、`agate/tests/README.md` 未登记两个新测试文件——不重复计数为独立差异，指向同一组修复动作）

---

### A6: 锚点表覆盖

**CHECK 9 正向锚点**（`check-protocol-consistency.py:557-560`）：
```python
{"desc": "复盘提醒", "script": "agate/scripts/check-retrospective.py", "keywords": ["retries"]},
```
关键词 `retries` 对应既有 `_retries_over` 函数与 `retries` 相关文案，未被本次改动移除，锚点仍有效，无需更新。

**CHECK 9 反向覆盖**（`check-protocol-consistency.py:722-761` `check_anchor_coverage`）：只扫描 `agate/scripts/check-*.py` glob + `pre-commit-gate.{sh,py}` + `ci-gate-backstop.py`。`agate-feedback.py` 文件名不匹配 `check-*.py` 模式，且未被 pre-commit hook 调用（`grep -rn "agate-feedback" agate/scripts/pre-commit-gate.sh agate/scripts/pre-commit-gate.py` 零命中，符合 BDD-19/20"手动触发，不存在任何自动触发钩子"的设计），因此**不需要**在 CHECK 9 锚点表登记。

**实跑验证**：
```
$ timeout 60s python3 agate/scripts/check-protocol-consistency.py --strict
✅ PASS  CHECK 9  协议-脚本结构对齐
⚠️  WARN  CHECK 2  仓库内文件引用存在（303 WARNING，0 ERROR）
```
CHECK 9 通过；CHECK 2 的 WARNING（含 `roadmap.md` 里连续出现的 `docs/reviews/postmortem-template.md` 历史叙述引用）对应 `P4-implementation.md` 已记录的已知 DESIGN_GAP（见下方"已知偏离核实"），非本次新引入 ERROR。

**结论**：ALIGNED

---

### A7: 设计原则一致性

**相关 ADR 逐条核查**：

- **ADR-002（可判定性——gate 门槛机器可判定）**：`check-retrospective.py` 新分支保持"只提醒不阻断"（exit 恒 0），与其"软提醒"定位一致，不违反该 ADR 对"gate 门槛"的机器可判定要求（该分支本就不是判定 PASS/FAIL 的硬门槛）——ALIGNED。
- **ADR-007（机器字段并入 frontmatter——单工具双读，不拆分独立事实文件）**：
  `agate/adr.md:205-207` 决策原文：
  > 机器字段并入产出物已有的 frontmatter 块……由**单一双读工具** `agate-md-field-get.py` **统一提供**"frontmatter 优先 + 正则回退"的读取语义；不引入独立的 `.yaml`/facts 元数据文件

  BDD-6（`retrospective-template.md` frontmatter 新增 `mechanism_issues`/`execution_issues`/`feedback_ready` 三字段）遵循了"字段进 frontmatter、不建独立文件"的核心原则——ALIGNED 部分。

  但 BDD-17（`agate-feedback.py:48-59` `_extract_frontmatter_block` + 直接 `yaml.safe_load`）**未复用** `agate-md-field-get.py`，而是本地重新实现了一份等价的 frontmatter 提取逻辑，绕开了 ADR-007 指定的"单一双读工具"。核实 `agate-md-field-get.py:69-108`（`BOOL_FIELDS`/`LIST_FIELDS`/`NO_FALLBACK_*_FIELDS` 等注册表）确认该工具当前的字段登记范围严格限定在 P1/P2/P6/P7 **gate 消费**的约 40+ 字段，且其核心价值（"frontmatter 优先 + 正则回退"双读兼容旧格式）对 `retrospective.md` 这个全新文档类型不适用——`retrospective.md` 没有需要向后兼容的"正则回退"旧格式，`agate-feedback.py` 也明确不是 gate 脚本（opt-in、手动触发）。

  **结论**：NEEDS_HUMAN_REVIEW
  **理由**：ADR-007 决策文本字面上要求"单一双读工具统一提供读取语义"，本次改动新增了第二个 frontmatter 读取实现路径，字面上是对该条款的偏离；但该 ADR 的语境（`agate/adr.md:201-203`）明确是针对"P1/P2/P6/P7 共约 40+ 个"**gate 消费**字段的历史技术债，`agate-feedback.py` 服务的是一个性质不同的场景（非 gate、opt-in 工具、消费一个全新文档类型、且不需要正则回退语义）。是否应该扩展 `agate-md-field-get.py` 的字段登记范围以覆盖这类非 gate 场景，还是维持"gate 字段专用工具 + 独立轻量工具各自实现"的分层，是一个需要人工裁决的架构取舍，不属于可机械判定的违反。
  **[HUMAN_CONFIRMED: 待补——需人工确认是否要求 agate-feedback.py 改造为复用 agate-md-field-get.py，或明确 ADR-007 的适用边界仅限 gate 消费场景并在 ADR 中补充说明]**

**结论**：NEEDS_HUMAN_REVIEW（1 项，如上）

---

## 已知偏离核实（DESIGN_GAP 交叉核实，非本次新发现）

`P4-implementation.md:59-69` 记录了 1 条 `[DESIGN_GAP]`：`roadmap.md:313` 与新模板迁移说明里的连续路径字符串 `docs/reviews/postmortem-template.md`，因 `check-protocol-consistency.py` CHECK 2（`NARRATIVE_DIRS` 白名单不含 `agate-workspace/roadmap/` 与 `agate/assets/`）会误判为死链 ERROR，实现时将其拆成两段非连续字符串规避。

**独立核实**：读取 `check-protocol-consistency.py:76`：
```python
NARRATIVE_DIRS = ("docs/plans/", "docs/reviews/", "docs/design-notes/", "docs/tasks/", "archived/", "agate-workspace/tasks/", "CHANGELOG.md")
```
确认不含 `agate-workspace/roadmap/`，DESIGN_GAP 的技术前提成立。实跑 `check-protocol-consistency.py --strict`：CHECK 2 结果为 **WARN**（非 ERROR），"仅有 303 个 WARNING，无 ERROR"——与 DESIGN_GAP 声称的"满足 check-protocol-consistency.py --strict 仍 0 ERROR"完全一致。

**该任务当前处于 P4 阶段，尚无 P7 记录**（`agate-workspace/tasks/TAG0015-retrospective-feedback/` 目录下无 `P7-consistency.md`），故按角色文件原则 6，此 DESIGN_GAP **不能**直接判 ALIGNED/免检——但本审查独立核实其技术依据（CHECK 2 白名单范围、实际 WARN 而非 ERROR 结果）后确认理由站得住，不属于本次审查范围内的新增 MISALIGNED，留待 P7 阶段按常规流程走 `DESIGN_GAP_REVIEWED` 确认闭环。

---

## 审查过程中的意外与处理

审查中途执行 `git stash`（用于 A/B 对比 `test_check_pruning.py` 失败是否由本次 diff 引入）时，与并发运行的主 Agent 对 `orchestrator-log.md` 的写入产生了 merge 冲突标记。已第一时间发现并用 `Edit` 工具去除冲突标记、保留双方全部内容（未丢失任何一方的日志记录），`git add` 恢复暂存状态，并清理了因此产生的冗余 stash 条目。当前 `git status --short` 已与审查开始前的暂存文件列表完全一致（17 个文件，无新增/无丢失）。

## 人工验收清单

- [x] 审查报告含 A1-A7 七项，每项有结论
- [x] MISALIGNED 项（A2/A3b/A5，共享同一组差异：WORKFLOW.md:318 + scripts/README.md + tests/README.md）有差异描述 + 建议方向
- [ ] NEEDS_HUMAN_REVIEW（A7，ADR-007 适用范围）下面的 `[HUMAN_CONFIRMED: ...]` 待人工补充确认——**当前状态等同 MISALIGNED，不允许在此项未确认前 commit**
- [x] 审查报告落盘到 `docs/reviews/agate-alignment-review-2026-08-19.md`

---

## 复核轮（重试 #1）

**背景**：首轮发现 A2/A3b/A5（共享同一组差异）MISALIGNED，A7（ADR-007）NEEDS_HUMAN_REVIEW。用户已就 A7 裁决：**扩展 `agate-md-field-get.py` 注册新字段，`agate-feedback.py` 改为调用它，完全合规**（不修改 ADR-007 边界文本）。implementer 已完成全部 4 项修复，P4 review（实现评审）复核已判 approved。本轮独立复核这 4 个具体差异点是否已解决，不重走 A1-A7 全套（A1/A4/A6/A3a 上轮已 ALIGNED 且本轮未涉及改动，不复查）。

### 复核点 1（对应首轮 A2/A3b）：`agate/WORKFLOW.md:318`

**实读现状**（`agate/WORKFLOW.md:318`）：
> `| 2.12 | check-retrospective.py | gate 任何结果 | 阶段级 | 异常模式提醒（重试超限/SCOPE+/override）→ 写复盘；另检测到 DEBT/roadmap 已登记本任务（机制缺口信号，TAG0015）→ 追加提醒；均不阻塞 commit（P2.12）|`

该行已在原有"异常模式提醒（重试超限/SCOPE+/override）"描述之后，追加了"另检测到 DEBT/roadmap 已登记本任务（机制缺口信号，TAG0015）→ 追加提醒"一句，与 BDD-10 新增的第 4 类触发条件（机制缺口信号，区别于旧的 3 类异常模式）语义一致，且保留了原有 3 类描述未被覆盖删除。

**结论**：ALIGNED

### 复核点 2（对应首轮 A3b）：`agate/scripts/README.md`

**实读**：
- 第 37 行：`| check-retrospective.py (P2.12) | 异常模式提醒（不阻塞）；另检测到 DEBT/roadmap 已登记本任务（机制缺口信号，TAG0015）→ 追加提醒 | 0=总是通过 |`——已补充机制缺口信号分支描述。
- 第 38 行：`| agate-feedback.py | 跨项目反馈提取（AG0021，opt-in，AGATE_FEEDBACK=on）| 手动触发，非 gate/非 pre-commit |`——`agate-feedback.py` 已登记进工具清单表。

**结论**：ALIGNED

### 复核点 3（对应首轮 A3b/A5）：`agate/tests/README.md`

**实读**（第 46-48 行）：
```
| check-retrospective.py | unit/test_check_retrospective.py | 15 |
| agate-feedback.py | unit/test_agate_feedback.py | 7 |
| 复盘协议文档条文 | unit/test_retrospective_protocol_docs.py | 13 |
```

**独立核对实际函数数**（`grep -c "^def test" <file>`，不采信任何既有报告数字）：
- `test_check_retrospective.py` → **15**，与登记值一致。
- `test_agate_feedback.py` → **7**（非派发任务描述中提及的"8 个函数"——该数字来自任务描述转述，本审查以自行 grep 结果为准），与登记值一致。
- `test_retrospective_protocol_docs.py` → **13**，与登记值一致。

三行均已登记且用例数准确，`check-retrospective.py` 行的用例数已从首轮报告记录的旧值 10 更正为准确值 15。

**结论**：ALIGNED

### 复核点 4（对应首轮 A7，ADR-007 合规）

**`agate/scripts/agate-md-field-get.py` 字段注册核实**：
- `NO_FALLBACK_BOOL_FIELDS`（:76）：`frozenset({"regression_pass", "feedback_ready"})`——`feedback_ready` 已注册，行内注释明确标注"TAG0015（BDD-6/17，重试#1 A7 修复）"。
- `NO_FALLBACK_LIST_FIELDS`（:112-115）：`frozenset({"need_confirm_resolved", "suggest_resolved", "scope_resolved", "mechanism_issues", "execution_issues"})`——`mechanism_issues`/`execution_issues` 已注册，同样标注"重试#1 A7 修复"。

**`agate/scripts/agate-feedback.py` 调用方式核实**：
- 新增 `_md_field_get(op, file_path)`（:46-65）：通过 `subprocess.run([sys.executable, MD_FIELD_GET, op], ...)` 调用 `agate-md-field-get.py`，docstring 显式引用 ADR-007（"ADR-007 单一双读工具（重试#1 A7 修复）"）。
- `main()`（:191-195）：`mechanism_issues`/`execution_issues`/`feedback_ready` 三字段均已改为经由 `_md_field_get()` 取值，不再本地重新实现 frontmatter 字段解析。
- `task_id` 字段（:200）：仍为 `fm_data.get("task_id", "")` 本地读取——按派发任务说明，此字段例外保留本地读取，不属于本次修复范围，符合预期。

**`agate/adr.md` ADR-007 条目核实**：`git diff main -- agate/adr.md` 输出为空——ADR-007 条目本身未被改动，与用户裁决"扩展工具使其合规"而非"修改 ADR 边界"一致。

**回归测试**（本次独立实跑）：
```
$ timeout 60s python3 -m pytest agate/tests/unit/test_agate_md_field_get.py -q
16 passed in 0.50s

$ timeout 60s python3 -m pytest agate/tests/unit/test_agate_feedback.py agate/tests/unit/test_check_retrospective.py agate/tests/unit/test_retrospective_protocol_docs.py -q
35 passed in 1.81s
```
共享工具自身测试（覆盖 P1/P2/P6/P7 既有字段消费方）未被破坏，`agate-feedback.py` 改造后相关测试全绿。

**结论**：ALIGNED

### 复核轮汇总

| # | 首轮结论 | 复核轮结论 |
|---|---|---|
| A2 | MISALIGNED | **ALIGNED** |
| A3b | MISALIGNED（3 项） | **ALIGNED** |
| A5 | MISALIGNED（同源） | **ALIGNED** |
| A7 | NEEDS_HUMAN_REVIEW | **ALIGNED**（`[HUMAN_CONFIRMED: 2026-08-19 用户裁决：扩展 agate-md-field-get.py 注册 mechanism_issues/execution_issues/feedback_ready 三字段，agate-feedback.py 改为 subprocess 调用该工具，完全合规，不修改 ADR-007 边界文本]`） |

首轮 A1/A4/A6/A3a（均 ALIGNED）本轮未涉及改动，复核过程中未发现任何意外破坏迹象（相关测试全绿，adr.md 无 diff）。**4 个复核点全部转 ALIGNED，可 commit。**
