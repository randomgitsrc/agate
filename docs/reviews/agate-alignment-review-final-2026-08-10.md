---
review_date: 2026-08-10
reviewer: protocol-alignment-review（终审，独立重审，不转述历史报告）
change_summary: T001（agate v0.40.0 结构化数据改造）全量版本变更 main..feat/v2.0——机器字段并入 frontmatter + 双读工具 + schema 校验器（流A）、P6/P7 结果结构化（流B）、标记"已解决"状态结构化（流C）、任务编号规则硬切（流D）
files_changed: [49 文件（47 M / 2 A），3588 行 diff，含 agate/ 全部协议文档/角色卡/模板/脚本/测试，SELF-GATE.md 本身零改动]
---

# 协议-脚本对齐审查（T001 v0.40.0 合并前终审）

> 本报告为**全新独立审查**：未转述 `docs/reviews/agate-alignment-review-2026-08-10.md`（此前两次增量审查），所有结论均基于本次重新读取 diff 全文（3588 行）、重新实跑测试基线、独立交叉核对文档与代码得出。旧报告仅作为交叉核对辅助材料使用。

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | MISALIGNED（轻微，非阻断） |
| A3 | 一致性连锁 + 反向传播 | MISALIGNED（轻微 ×2，非阻断） |
| A4 | 测试覆盖 | ALIGNED |
| A5 | 下游影响 + 文档传播 | ALIGNED |
| A6 | 锚点表覆盖 | ALIGNED |
| A7 | 设计原则一致性 | ALIGNED |

**实测基线（本次独立重跑，非引用历史数字）**：
```
bash agate/tests/scripts/count-tests.sh        → 597（与 BASELINE_CHANGE 594→597 一致）
bats sanity.bats + unit/ + regression/ + integration/  → 603/603，0 failed
shellcheck -S warning agate/scripts/*.sh       → 无输出，exit 0
python3 agate/scripts/check-protocol-consistency.py → CHECK 1-9 全部 PASS，0 ERROR（含 CHECK 7 badge=v0.40.0 与 git tag v0.40.0 一致）
```

**合并建议**：本次发现的 3 处 MISALIGNED 均为**文档/示例层面的轻微不一致**，不涉及 gate 逻辑、脚本行为或测试正确性，不影响 v0.40.0 的功能正确性与可靠性。**不构成阻断合并的理由**，建议作为一次小的 follow-up 提交处理（也可在合并前顺手修）。

---

## 逐项审查

### A1: 文档→脚本对齐

**审查方法**：以 `docs/tasks/T001-v2.0-structured/P2-design.md` §3.1-3.4（权威设计落点声明）为对照基准，逐条核对对应脚本 diff 实现。

**流 A（frontmatter 迁移 + 双读 + schema 校验）**：

- **文档声明**（P2-design.md:211-217, §3.1.2）：`agate-md-field-get.py` 采用"字段级 presence 检测"——op 对应字段在 frontmatter 中存在（key 存在且值非 null）优先取 frontmatter，否则正则回退。
- **脚本实现**（`agate/scripts/agate-md-field-get.py` `_get()` 函数，diff 行 1072-1079）：
  ```python
  def _get(text, op):
      fm = _read_frontmatter(text)
      if isinstance(fm, dict) and op in fm and fm[op] is not None:
          return _format_value(fm[op], op)
      if op in NO_FALLBACK_INT_FIELDS or op in NO_FALLBACK_LIST_FIELDS:
          return ""
      return _regex_fallback(text, op)
  ```
  逐字对应文档伪代码（P2-design.md:244-249），字段级 presence 判定语义一致。**ALIGNED**。

- **文档声明**（P2-design.md:213-214，FIND-1 修订）：判别契约不能用"文件级 MIGRATED_KEYS 全集"（会导致 P7 文件只含流 B 字段时被误判旧格式）。
- **脚本实现**（`agate-frontmatter-check.py` 步骤 5，diff 行 885）：`if not (schema["migrated_keys"] & set(data.keys())): return`——按**文件名对应 schema 的迁移字段子集**判定，不是全集。测试 `check-frontmatter.bats` CF.6 专门覆盖"P7 文件只含 blocker_count（无任何流 A 字段）仍触发 P7 schema 校验"场景，已通过。**ALIGNED**。

- **文档声明**（P2-design.md:270，FIND-5）：frontmatter 块存在但 `safe_load` 结果非 dict（如单行全角冒号纯量）→ 一律硬拦截。
- **脚本实现**（`agate-frontmatter-check.py` diff 行 876-883）：`if not isinstance(data, dict): print(...); return`。对应测试 CF.9 覆盖该场景。**ALIGNED**。

- **文档声明**（P2-design.md:256，FIND-4）：`ui_affected` 归一化契约——`_format_value` 对 bool 字段统一 `str(v).lower()`，输出恰好 `"true"`/`"false"`。
- **脚本实现**（`agate-md-field-get.py` diff 行 1019-1020）：`if field in BOOL_FIELDS: return str(value).lower()`。**ALIGNED**。

**流 B（P6/P7 结构化计数）**：

- **文档声明**（P2-design.md:331, 358-360）：check-gate.sh P6 分支读 frontmatter `pass`/`fail` 判定；P7 分支读 `blocker_count`/`deviation_critical_count`/`design_gap_count`/`design_gap_reviewed_count`，DESIGN_GAP 判定改为 `reviewed >= count`（不再用数量相减）。
- **脚本实现**（`check-gate.sh` diff 行 1283-1295 / 1315-1360）：均实现为 `if [ -n "$PASS_FM" ] && [ -n "$FAIL_FM" ]; then ... else 回退正文 grep`；DESIGN_GAP 分支为 `if [ "$DESIGN_GAP_REVIEWED" -lt "$DESIGN_GAP_COUNT" ]; then exit 1`。与文档一致。**ALIGNED**。

- **文档声明**（P2-design.md:333，FIND-6）：新格式下 frontmatter `pass+fail` 与正文从严行数不一致 → WARNING（非阻断）。
- **脚本实现**（`check-p6-provenance.sh` diff 行 1519-1523）：`if [ "$P6_TOTAL" -ne "$P6_BODY_STRICT" ]; then echo "...WARNING..." >&2; fi`（无 exit 1）。**ALIGNED**。

**流 C（标记状态结构化）**：

- **文档声明**（P2-design.md:383）：NEED_CONFIRM 阻塞判定改"逐条匹配"（正文每条 NEED_CONFIRM 描述须在 `need_confirm_resolved` 列表中找到对应项），而非数量相减。
- **脚本实现**（`check-gate.sh` diff 行 1232-1241）：`while IFS= read -r nc_desc; do ... if ! printf '%s\n' "$NC_RESOLVED_FM" | grep -qFx -- "$nc_desc"; then NC_UNRESOLVED=$((NC_UNRESOLVED + 1)); fi; done`——逐条 `grep -qFx` 精确匹配，非数量相减。**ALIGNED**。

**流 D（任务编号硬切）**：

- **文档声明**（P2-design.md:405）：`^T\d+$` → `^T[A-Z]{2}\d+$`，硬切不兼容旧格式。
- **脚本实现**（`agate-state-yaml-check.py` diff 行 1128）：`re.match(r"^T[A-Z]{2}\d+$", str(task_id))`。**ALIGNED**。

**唯一需要说明的偏离（非隐藏性，已走过正式流程，不计入 A1 的 MISALIGNED）**：P2-design.md §2"改什么"表声明 `check-pruning.sh` 的 10 个字段、`check-gate.sh` 的 P2 分支应"迁移到双读工具"，但实际实现中 `check-pruning.sh` 仅 `risk_level`/`phases` 走了 `agate-md-field-get.py`（diff 行 1616-1618 未改动，仍为裸 grep：`grep -qE '^override:'`、`grep -qE '^internal_only:'` 等，独立读取 `agate/scripts/check-pruning.sh:23,82,90,92,100` 确认）。**这不是本次审查新发现的隐藏偏离**——`docs/tasks/T001-v2.0-structured/P7-consistency.md` 第 27-33 行已将其记录为 `[DESIGN_GAP: check-pruning.sh 的 8 个 P1 字段读取点同理未迁移...]`，并经 P7 consistency-reviewer 独立核实代码现状后判定 `REVIEWED-ACCEPTED`（理由：frontmatter 字段顶格书写，裸 grep `^field:` 对 frontmatter 内容天然兼容；且 `agate-frontmatter-check.py` 的 schema 校验器已在 pre-commit 层拦截全部坏格式，check-pruning.sh 未走双读工具不产生实际解析可靠性缺口）。本次独立复核该 DESIGN_GAP 记录与代码现状一致，裁决理由站得住，不重新判定为 MISALIGNED。

**A1 结论：ALIGNED**。

---

### A2: 脚本→文档对齐

逐项核对新增/改动脚本的行为是否在对应文档中有对应声明。多数一致（`check-frontmatter.sh` 新增行为已写入 `scripts/README.md`:68、`agate/tests/README.md`、`CHANGELOG.md`），但发现一处真实的数字漂移：

**发现（MISALIGNED，轻微）**：

- **文档声明**（`agate/tests/README.md:37`，本次 diff 新增行）：
  > `| check-frontmatter.sh | unit/check-frontmatter.bats | 11 |`
- **脚本/测试实际**（独立执行 `grep -c '^@test' agate/tests/unit/check-frontmatter.bats`）：
  ```
  10
  ```
  与本次独立执行 `bash agate/tests/scripts/count-tests.sh` 的输出（`unit/check-frontmatter.bats  10 个 @test`）一致，均为 10，非文档所写的 11。

**差异**：`agate/tests/README.md` 的工具→测试文件映射表声称 `check-frontmatter.bats` 含 11 个 `@test`，实际只有 10 个（`CF.1`..`CF.10`）。

**根因推测**：`P2-design.md §3.1.5` FIND-7 的"594 配平"表述过程中，`check-frontmatter.bats` 的用例数在设计/实现迭代中出现过 N=10/N=11 的版本差异（`P2-design.md` 正文未直接给出 `tests/README.md` 该行的数字来源），最终代码定稿为 10 条，但 `tests/README.md` 的表格行未同步更新。

**影响面**：该表不被任何 gate 脚本消费（`count-tests.sh` 与 `check-protocol-consistency.py` 均不读取 `agate/tests/README.md` 的表格内容），纯文档性质，不影响 pre-commit/CI 行为，不影响 594→597 基线判定（该判定看的是 `count-tests.sh` 总计数，不是分文件数）。

**建议**：把 `agate/tests/README.md:37` 的 `11` 改为 `10`。工作量 1 行，无需重新验证。

**A2 结论：MISALIGNED（轻微，不阻断合并，建议 follow-up 修正）**。

---

### A3: 一致性连锁 + 反向传播

#### A3a：一致性连锁（衍生改动应同步但未同步）

**发现（MISALIGNED，轻微）**：本次 diff 中，flow D（任务编号规则硬切）触发的"示例值同步"在**协议叙述性文档**（`WORKFLOW.md`、`dispatch-protocol.md`、`state-machine.md`、`role-system.md`、`active-tasks-template.md`）中全部完成——所有 `task_id: T001` 类示例值统一改为 `TAG0001`/`TXX0001`（已逐一核对 diff，如 `state-machine.md:1611`、`dispatch-protocol.md:427`）。

但本次 diff **同时新增**的一批"可直接复制的 frontmatter 完整样例"（flow A 的 BDD-24 交付物，分布在 6 个文件）却仍使用旧格式 `T001` 作为 `task_id` 占位值：

```
agate/assets/execution-roles/analyst.md:42     task_id: T001   # 替换为实际任务编号
agate/assets/execution-roles/architect.md:46   task_id: T001   # 替换为实际任务编号
agate/assets/execution-roles/verifier.md:147   task_id: T001   # 替换为实际任务编号
agate/assets/templates/task-files.md:129/233/316/369  task_id: T001
agate/phase-cards/P1-requirements.md:54        task_id: T001
agate/phase-cards/P2-design.md:58              task_id: T001
agate/phase-cards/P6-acceptance.md:56          task_id: T001
agate/phase-cards/P7-consistency.md:59         task_id: T001
```

**差异**：同一次版本变更（main..feat/v2.0）内，"task_id 示例应使用什么格式"这件事出现了两种前后不一致的处理方式——flow D 改造覆盖到的文档全部切到新格式示例，flow A 新增的 frontmatter 样例块却仍沿用旧格式。这类 "可直接复制样例" 恰恰是最容易被字面照抄的内容（`analyst.md` 原文明确写"可直接复制的完整 frontmatter 样例"），若 subagent 未注意到旁边的 `# 替换为实际任务编号` 注释直接复制粘贴，写出的 `task_id: T001` 会被本次改造新加入的 `agate-state-yaml-check.py` 硬切正则 `^T[A-Z]{2}\d+$` 拒绝（因为 `T001` 不含 2 个大写字母）——即用户按文档指引"直接复制"反而会踩中同一版本刚引入的新校验拦截。

**严重程度评估**：轻微。有明确的替换注释兜底，不会造成静默错误（校验器会报错拦截，不会放行坏数据）；且 `.state.yaml`（非 frontmatter 校验对象）才是 task_id 硬切生效的地方，P1/P2/P6/P7 frontmatter 本身的 `task_id` 字段不在 `agate-frontmatter-check.py` 的必填/枚举校验范围内（只校验 `risk_level`/`phases`/`packages`/`domains` 等迁移字段），所以样例里 `task_id: T001` 本身不会触发 frontmatter 校验器报错——只有当这个 `task_id` 被抄进 `.state.yaml` 才会被拦。属于"示例风格不统一"而非"功能性错误"。

**建议**：把上述 8 处样例块的 `task_id: T001` 统一改为 `task_id: TAG0001`，与 flow D 改造后的示例风格保持一致（保留 `# 替换为实际任务编号` 注释）。

#### A3b：反向传播（应被影响但 diff 未列出的文件）

主动推断本次改动应传播到的文件，逐一核实：

| 应被影响的文件 | 理由 | 核实结果 |
|---|---|---|
| `agate/scripts/agate-extract-context.sh` | 读取 P1/P2 的 `risk_level`/`domains` 等字段，字段迁移后是否需要改路由 | **已核实，无需改**（FIND-2 决策：该脚本非 gate 判定点，frontmatter 顶层 key 顶格书写，现有 `grep -E '^domains:'` 天然兼容新旧格式；diff 中该文件确实未改动，与设计声明一致，`agate-extract-context.bats` EC.5/EC.6/EC.10 用 frontmatter 声明验证了该边界决策）——**ALIGNED，非遗漏** |
| `agate/orchestrator-template.md` | 常见反向传播路径表列出的高频受影响文件 | 核实无 `T001` 风格示例需要更新，diff 外，**不受影响，非遗漏** |
| `agate/LIMITATIONS.md` | v0.30.2→v0.35.0 连续 5 版"正则摩擦补丁"曾是已知限制，v2.0 解决后是否需要更新已知限制清单 | 核实该文件从未记录过"正文正则提取字段的摩擦"为已知限制条目（grep 无匹配），**不存在需要删除/更新的旧记录，非遗漏** |
| `docs/archived/plans/agate-test-plan-2026-07-01.md` 附录 A | **P2-design.md 自身在 §2 影响域表（行 125）与 §13 FIND-8 回应（行 636-640）明确声明**"受影响用例数/脚本清单数字同步（354）"、且 FIND-8 回应写"✅ 已补入" | **发现真实遗漏**：`git log --oneline main..feat/v2.0 -- docs/archived/plans/agate-test-plan-2026-07-01.md` 输出为空——该文件在本次版本变更的任何 commit 中均未被触碰。P2-design.md §13 FIND-8"已补入"的自述与实际代码库状态不符。该文档内容本身已严重过期（附录 A 表格仍是"148 个核心测试用例"的极早期版本，与当前 597 相去甚远，此陈旧问题早于 T001 已存在），文档自身也声明"所有数字以 `count-tests.sh` 为准，人工数表会漂移"，因此该遗漏**不产生任何机器判定层面的风险**（无脚本读取此文件），但作为"设计文档对自己是否完成某项同步的自述"，这一自述与代码库实际情况不符，值得记录 |
| `agate/scripts/README.md` | FIND-8 同时声明的另一处同步点 | **已核实完成**（diff 行 644：工具清单表 `agate-md-field-get.py` 条目已更新为完整的双读语义 + 17 个新 op 描述）——非遗漏 |
| `agate-summary.sh` / `active-tasks.md` 等下游消费点（P2-design.md §3.4.2 提到"P4 grep 全库核对"） | flow D 硬切后，其他脚本里若有 `T[0-9]+` 类提取式正则会失配 | **已核实完成**：`grep -rn "T\[0-9\]\+" agate/scripts/*.sh agate/scripts/*.py` 只剩 `check-changelog.sh` 注释里提及已移除的旧正则（非活跃代码），无其他脚本残留该风险模式——非遗漏 |

**A3 结论：MISALIGNED（A3a + A3b 各发现 1 处轻微、非阻断的遗漏，均为文档一致性/自述准确性问题，无功能性风险）**。

---

### A4: 测试覆盖

**要求**：必须附最近一次 bats 全量实跑输出（含 passed/failed 计数），无实跑输出的 ✓ 视为无效。

**本次独立实跑**（非引用 P5/P6 历史记录，本次工作目录内重新执行）：

```
$ bash agate/tests/scripts/count-tests.sh
...
总计：597 个测试用例

$ bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
1..603
ok 1 load.bash: AGATE_ROOT 解析正确
...
ok 603 SG.8 SELF-GATE.md 含递归终止条件
（grep -c "^ok " = 603；grep -c "^not ok " = 0）

$ shellcheck -S warning agate/scripts/*.sh
（无输出，exit 0）

$ python3 agate/scripts/check-protocol-consistency.py
✅ PASS  CHECK 1  YAML 代码块可解析
✅ PASS  CHECK 2  仓库内文件引用存在
✅ PASS  CHECK 3  协议文件无硬编码行号
✅ PASS  CHECK 4  gate_commands 键集合一致
✅ PASS  CHECK 6  LICENSE 与 gstack 归属
✅ PASS  CHECK 7  version badge 与 git tag
✅ PASS  CHECK 8  v0.6 关键词存在性
✅ PASS  CHECK 9  协议-脚本结构对齐
🎉 全部检查通过，协议结构一致性无问题。
```

**边界覆盖核实**：新增 `check-frontmatter.bats`（10 个 `@test`）覆盖 BDD-2（全角冒号报错）、BDD-4（缩进错误拦截）、BDD-5（枚举非法值）、BDD-6（缺必填字段，P1/P2/P7 各一例）、BDD-7（类型错误可定位）、BDD-8（与 `check-state-yaml.sh` 同机制挂载）、BDD-12（嵌套 >3 层拦截）、FIND-1（P7 文件只含流 B 字段仍触发 P7 schema 校验）、FIND-5（单行全角冒号非 dict 硬拦截）——已独立通读该文件全部 10 个用例，用例设计与文档声明的判别契约、schema 规则逐一对应，非空泛断言。`check-p6-format.bats` 新增 `F_P6FMFIX.1/2/3` 三个用例覆盖"P6 回退修复"（`--fix` 归一化 sed 曾误伤 frontmatter 内合法 `pass:`/`fail:` 字段的真实 bug），断言里包含独立 `python3 -c "import yaml; ..."` 验证 frontmatter 修复后仍是合法 YAML，属于真实回归覆盖而非表面断言。

**594→597 基线变更核实**：`P1-requirements.md` 第 190-198 行 `[BASELINE_CHANGE: 594 → 597]` 标注（P4 修复 `check-p6-format.sh` 真实 bug 时新增 3 条合规回归测试导致），本次独立重跑确认当前 `count-tests.sh` = 597，与该正式批准的基线一致，非未经批准的数字漂移。

**A4 结论：ALIGNED**。

---

### A5: 下游影响 + 文档传播

**CHANGELOG.md 核对**（`CHANGELOG.md:9-33`，`[0.40.0] - 2026-08-10` 节）：分"新增"（5 条）、"变更"（3 条）、"修复"（2 条）、"已知偏离"（3 条）四段结构化记录。已知偏离段明确列出与 P7-consistency.md 记录的 DESIGN_GAP 相对应的代表性条目（check-pruning.sh/check-gate.sh 部分字段未迁移双读工具、check-gate.sh P6 正则较设计文字宽松、check-scope-resolved.sh 空列表/不存在未区分），如实标注"均经 P7 独立核实，7/7 REVIEWED-ACCEPTED，非 BLOCKER"。**这是本次审查见过的最完整的 CHANGELOG 记录之一**——既写了"做了什么"，也写了"哪里没完全按设计做、为什么可接受"，符合 A5 对"下游影响 + 已知偏离"的最高标准。

**破坏性变更评估**：
- 对**其他已在用 agate 的项目**（本机通过 `~/.agate` 软链接指向主 checkout）：v0.40.0 采用双读设计（frontmatter 优先 + 正则回退），旧格式在途任务（frontmatter 无迁移字段）行为与 v0.35 完全一致，是**加法而非破坏性变更**——本次审查确认 `check-gate.bats` 中专门有 `G_BDD9.1`（BDD-9）用例验证"P2-design.md 四字段仅在正文、frontmatter 无这些字段"时行为与 v0.35 一致。
- **唯一真正的硬性破坏性变更**：`task_id` 正则硬切（`^T\d+$` → `^T[A-Z]{2}\d+$`），旧格式 `T001` 类任务 id 在新版校验器下会被拒绝。P0-brief 已明确此为"硬切不兼容"的既定决策（非本次审查新发现的风险），且 `CHANGELOG.md:21` 已标注。发布时机上，`P7-consistency.md` 记录"存量已归档"，本 T001 任务自身用 v0.35 工具规避（BDD-28 自举），风险可控。

**文档传播**：`orchestrator-template.md`、`WORKFLOW.md`、`dispatch-protocol.md`、`role-system.md`、`LIMITATIONS.md` 逐一核对（见 A3b 表），除 A3b 已列出的 `test-plan-2026-07-01.md` 附录 A 一处遗漏外，均已同步或确认无需同步。

**A5 结论：ALIGNED**（唯一瑕疵已计入 A3b，不重复扣分）。

---

### A6: 锚点表覆盖

**文档声明**（`SELF-GATE.md:31`）：`check-protocol-consistency.py` 的 CHECK 9 扫描协议文档声明的规则，核对对应脚本是否含相关关键词。

**新增锚点核实**（`check-protocol-consistency.py` diff 行 1538-1543）：
```python
{
    "desc": "frontmatter schema 校验",
    "script": "agate/scripts/check-frontmatter.sh",
    "keywords": ["frontmatter"],
    "callers": ["agate/scripts/pre-commit-gate.sh"],
},
```
- 独立执行 `grep -c '"script":' agate/scripts/check-protocol-consistency.py` = **38**（37 既有 + 1 新增），与 P2-design.md §3.1.4"37→38"声明一致。
- `callers` 字段声明的调用方 `pre-commit-gate.sh` 核实为真：`pre-commit-gate.sh` diff 行 1588-1598 新增"2g.2 frontmatter schema 校验"步骤，确有 `bash "$AGATE_ROOT/scripts/check-frontmatter.sh" "$TASK_DIR/$FM_NAME"` 调用。
- `check-frontmatter.sh` 脚本文件内确实含 `"frontmatter"` 关键词（多处），锚点关键词匹配不会假阴性。

**已核实的其余 37 条既有锚点全量重新校准**（P2-design.md §3.1.4 声明的"脚本改写后逐条核对关键词仍存在"）：本次独立跑 `check-protocol-consistency.py` 输出 `CHECK 9 协议-脚本结构对齐` 为 PASS（无 ERROR），已覆盖全部 38 条锚点的关键词存在性核对，不存在遗漏锚点导致误报的情况。

**A6 结论：ALIGNED**。

---

### A7: 设计原则一致性

**新增 ADR-007**（`agate/adr.md` 新增 33 行，diff 行 24-53）核对：

- **决策内容与实现是否一致**：ADR-007 声明"机器字段并入产出物已有的 frontmatter 块……由单一双读工具 `agate-md-field-get.py` 统一提供……不引入独立的 `.yaml`/facts 元数据文件，读取层也不按阶段拆分成多个 facts 工具"。核实实现现状：确认全程只有一个 `agate-md-field-get.py`（改造）+ 一个新校验器 `agate-frontmatter-check.py`（对应 ADR 提及的"新增独立校验器不违反单读取工具原则"，因为校验器职责是格式校验，不是读取路由，`agate-md-field-get.py` 依旧是唯一的读取入口），**与 ADR 决策一致**。
- **与既有 ADR 的一致性**：
  - **ADR-001（多阶段独立评审，防自我批准）**：本次 T001 P1/P2/P4/P7 均有独立 review/consistency-review 角色产出（P1-review approved、P2-review approved + 8 条 FIND 已回应、P4-review approved 复审通过、P7-consistency approved），符合 ADR-001 的"评审角色独立上下文"原则，无冲突。
  - **ADR-002/006（真实性保障机制不因结构化改造而减弱）**：P2-design.md §10"语义真实性边界"一节明确声明"结构化解决解析层问题，不解决内容真实性问题……真实性保障机制不变，继续依赖 subagent 独立上下文 + 独立评审角色"，与 ADR-002/006 的既定原则直接呼应，未见冲突或弱化。
- **是否存在未记录的架构决策**：核实"字段级 presence 检测 vs 文件级 MIGRATED_KEYS 全集判定"（FIND-1 修订，P2-design.md §3.1.2）这一判别契约选择本质上是一个独立的设计决策，但其决策记录已经完整保留在 P2-design.md §13 FIND-1 回应中（任务级设计文档），且其重要性/影响面小于 ADR-007（frontmatter vs 独立文件）这一顶层架构选择——不认为需要单独提炼为新 ADR，任务设计文档的记录粒度已足够。

**A7 结论：ALIGNED**。

---

## 待闭环事项清单

| # | 事项 | 类型 | 严重程度 | 建议动作 |
|---|------|------|----------|----------|
| 1 | `agate/tests/README.md:37` `check-frontmatter.bats` 测试数写 11，实际 10 | A2 | 轻微，无功能影响 | 改为 10（1 行修改） |
| 2 | 8 处新增 frontmatter 可复制样例块的 `task_id: T001` 未同步 flow D 新格式 | A3a | 轻微，有替换注释兜底 | 统一改为 `task_id: TAG0001` |
| 3 | `docs/archived/plans/agate-test-plan-2026-07-01.md` 附录 A 未按 P2-design.md FIND-8 承诺同步 354 数字（该文档已严重过期，非本次新增问题） | A3b | 轻微，无机器读取依赖 | 可选：更新该行数字，或在文档顶部补注"已归档，数字以 count-tests.sh 为准，不再维护" |

以上 3 项均不阻断 `feat/v2.0` 合并 `main`——不涉及 gate 逻辑、脚本行为、测试正确性，纯文档一致性/示例风格问题，可作为合并后的一次小 follow-up 处理。

---

## Self-gate 机制升级分析

> 分析对象：`SELF-GATE.md`（self-gate 流程定义）与 `agate/assets/review-roles/protocol-alignment-review.md`（本审查角色定义）本身，是否因 v0.40.0 引入的新机制（frontmatter schema 校验器、字段级 presence 双读、P6/P7 结构化计数、任务编号规则硬切）而需要升级。

### 1. `SELF-GATE.md` 的触发文件清单是否已覆盖新校验器

**当前清单**（`SELF-GATE.md:14-19`）：`agate/scripts/*.sh`、`agate/scripts/*.py`、`agate/*.md`、`agate/**/*.md`、`SELF-GATE.md`。

**结论：不需要升级**。

理由：新增的 `agate-frontmatter-check.py`（`agate/scripts/` 下的 `.py` 文件）与 `check-frontmatter.sh`（`agate/scripts/` 下的 `.sh` 文件）都天然落在现有通配符 `agate/scripts/*.py` / `agate/scripts/*.sh` 覆盖范围内，不需要新增条目。新增的 4 类 frontmatter schema 定义（`SCHEMAS` 字典）也内嵌在 `agate-frontmatter-check.py` 文件本体里，未产生"schema 定义在脚本之外的独立配置文件"这种新文件类别——若未来真的把 schema 拆成独立 `.yaml`/`.json` 配置文件（本次 P2-design.md 已明确否决此路线，见 ADR-007），才需要为该新文件类别扩展触发清单。当前架构下现有 5 类通配符已是完全覆盖。

### 2. `protocol-alignment-review.md` 的"反向传播的常见路径"表是否需要新增一行

**结论：需要升级**。

理由：现有表格（`protocol-alignment-review.md:30-39`）列出的 8 行路径全部是"改了协议叙述性文档/脚本行为 → 传播到哪些相邻文档"这类模式，唯独没有覆盖 v0.40.0 新引入的**"frontmatter 迁移字段集/schema 定义"这一新的核心耦合面**——本次审查实际执行反向传播推理时（A3b），能命中 `test-plan-2026-07-01.md`、`scripts/README.md` 这类关联点，正是因为独立读了 P2-design.md §2 影响域表；如果没有这份任务级设计文档兜底（比如未来对 frontmatter schema 做增量小改动、不会重新产出一份完整 P2-design.md 的场景下），审查员缺少一个"改了 schema 该查哪些文件"的结构化起点。

**具体建议新增行**（比照现有表"BDD 编号格式"行的详细程度）：

```markdown
| `agate-frontmatter-check.py` 的 `SCHEMAS`（migrated_keys/required/enums/types）或
  `agate-md-field-get.py` 的 `BOOL_FIELDS`/`LIST_FIELDS`/`NO_FALLBACK_*_FIELDS`（frontmatter
  迁移字段集/op 清单）| `agate/assets/templates/task-files.md`（对应阶段的可复制 frontmatter
  样例块）、`agate/assets/execution-roles/{analyst,architect,verifier}.md`（角色卡样例块）、
  `agate/phase-cards/{P1,P2,P6,P7}-*.md`（产出规格节样例块）、消费该字段的
  `check-gate.sh`/`check-pruning.sh`/`check-scope-resolved.sh` 判定分支、
  `agate/scripts/README.md`（工具清单表的 op 描述）、`tests/helpers/fixtures.bash`
  （`add_frontmatter_field` 系列 helper）、对应的 `.bats` fixture |
```

### 3. A6"锚点表覆盖"审查项描述是否需要补充新型锚点说明

**结论：需要升级（补充说明，非重新设计）**。

理由：`protocol-alignment-review.md` 当前对 A6 的描述是"CHECK 9 的锚点表是否需要更新？新增的协议规则是否需要加入锚点表？"——这句话隐含的锚点模型是**"协议文档提到某规则关键词 → 对应脚本代码也应出现该关键词"**（如"NEED_CONFIRM 三值"这类语义关键词匹配）。但本次新增的 `check-frontmatter.sh` 锚点性质不同：它的 `keywords: ["frontmatter"]` 本质是**"确认这个新校验脚本存在、且被声明的调用方（`callers`）真的调用了它"**的存在性/挂载点核实，而不是"协议文档某句话的关键词是否出现在脚本里"这种语义关键词匹配——`check-frontmatter.sh` 本身就是一段新协议规则（frontmatter schema）的机器实现载体，它的"对齐对象"不是某句协议文档原文，而是 `agate-frontmatter-check.py` 内部的 `SCHEMAS` 定义是否与 `task-files.md`/角色卡声明的字段集一致，这件事 CHECK 9 的关键词匹配机制根本验证不了，**仍然要靠 A1 人工核对**。这个"新型锚点只验证'脚本存在且被调用'，不验证'schema 内容与文档描述的字段集是否一致'"的边界，如果不在角色定义里说清楚，容易让审查员误以为"CHECK 9 PASS 就说明 frontmatter 字段集文档-脚本对齐"，而实际上那件事仍然依赖 A1 的逐条人工核对（本报告 A1 一节正是这么做的）。

**具体建议**：在 A6 条目后追加一句：
> 注：CHECK 9 部分锚点（如 `check-frontmatter.sh`）验证的是"校验脚本存在且被正确挂载调用"，不是"schema 定义内容与协议文档声明的字段集语义一致"——后者不属于关键词匹配可判定范围，仍需 A1 逐条人工核对。

### 4. Layer 0（CHECK 9）/ Layer 1（LLM 语义审查）与新增的 frontmatter schema 校验器三者边界是否清晰

**结论：不需要强制升级，但建议补充一句可选澄清**。

理由：`agate-frontmatter-check.py` 审的是**"某个使用 agate 协议的项目里，subagent 产出的 P1/P2/P6/P7 文件格式是否合规"**（面向 agate 协议的下游消费者/使用者），这与 self-gate 审的**"agate 协议仓库自身改动时，协议文档描述与脚本实现是否语义一致"**（面向 agate 协议的开发者/维护者）是两个完全不同维度的问题，作用对象、触发时机都不同——这个边界并非本次新引入的模糊地带，`agate-state-yaml-check.py`（.state.yaml 格式校验器）在 v0.40.0 之前就已经是同类"产出物格式校验器"，同样不属于 self-gate 机制的一部分，`SELF-GATE.md` 至今也没有为它专门写边界说明，说明这个边界一直是隐式清晰、无需显式声明的（"格式校验器校验产出物，self-gate 审协议仓库自身"）。因此不认为存在因为新增 frontmatter 校验器而产生的新重叠或空白地带。

可选的低成本改进：如果担心未来贡献者第一次接触 self-gate 时把两者搞混（尤其现在 self-gate 触发清单里 `agate/scripts/*.py` 恰好也会命中 `agate-frontmatter-check.py`，容易让人以为"改这个文件走 self-gate 审的是它的格式校验逻辑对不对"），可以在 `SELF-GATE.md` 触发条件下方加一句：
> 注：本机制审的是"改 agate 协议文档/脚本时两者是否语义一致"；`agate-frontmatter-check.py`/`agate-state-yaml-check.py` 这类"校验任务产出物格式"的脚本本身改动也要走 self-gate（因为它们也是"agate 脚本"），但 self-gate 审的是这些校验器的实现是否忠实反映了协议文档声明的 schema，而不是校验器本身要不要更严格——后者是产品设计问题，不是一致性问题。

（此项为可选建议，非必须项，不计入"需要升级"计数的强制性理由——因为边界本身没有被破坏，只是缺少一句显式说明。）

### 5. DESIGN_GAP 机制是否应在 self-gate 审查中显式提及

**结论：需要升级**。这是本次实际审查过程中真实遇到的问题，不是假设性推演。

理由：本次 A1 审查中，`check-pruning.sh`/`check-gate.sh` 部分字段读取点未迁移到双读工具，字面对照 P2-design.md §2 的"改什么"表会得出 MISALIGNED 的初步印象——但因为本次审查任务的输入文件清单里包含了 `docs/tasks/T001-v2.0-structured/P7-consistency.md`，读到其中记录的 `[DESIGN_GAP_REVIEWED: ...]` 独立核实结论后，才改判为"非隐藏性偏离，已走过 P7 正式核实流程，ALIGNED"。**如果本次审查没有被显式要求读 P7-consistency.md（比如日常"变更触发模式"，只审 diff，不主动去查任务目录下有没有 P7 记录），审查员大概率会把这类已经被走过 DESIGN_GAP→P7 REVIEWED-ACCEPTED 流程的已知偏离，误判为新发现的 MISALIGNED，制造假阳性。** 这正是本次 T001 任务本身用了 7 次 DESIGN_GAP 机制、且其中至少 2 条与"文档→脚本对齐"直接相关（check-pruning.sh/check-gate.sh 字段迁移不完整）所暴露出的真实缺口——protocol-alignment-review.md 当前的 A1/A3 审查原则完全没有提到"发现不一致时，先检查是否已有 DESIGN_GAP 记录"这一步。

**具体建议**（供主 Agent 后续决定是否派发实施，不要求本次修改）：

1. 在 `protocol-alignment-review.md` 的"审查原则"节（当前 1-5 条）新增第 6 条：
   > 6. **DESIGN_GAP 优先核查**：发现文档-脚本不一致时，若审查对象关联某个具体任务（`docs/tasks/{Txxx}/`），先检查该任务的 `P4-implementation.md`/`P7-consistency.md` 是否已有对应的 `[DESIGN_GAP:]`/`[DESIGN_GAP_REVIEWED:]` 记录——若已被 P7 consistency-reviewer 独立核实且判定 `REVIEWED-ACCEPTED`，不判 MISALIGNED，而是在报告中注明"已知偏离，来源：{task} P7 REVIEWED-ACCEPTED（引用原文）"，仍计入报告但不计入需修复项；若该任务尚无 P7 记录（比如任务仍在 P4/P5 阶段）或核实后认为 P7 的裁决理由站不住，仍按正常 MISALIGNED 处理。
2. 在"输出格式"的结论枚举里补充说明：三态结论（ALIGNED/MISALIGNED/NEEDS_HUMAN_REVIEW）不变，但 MISALIGNED 项如果对应一条已被 P7 接受的 DESIGN_GAP，应在该项下追加 `[KNOWN_DEVIATION: 来源 {task} P7-consistency.md，REVIEWED-ACCEPTED，理由摘要]` 标注（类比现有 `[HUMAN_CONFIRMED: ...]` 标注模式），与"必须修复"的普通 MISALIGNED 区分开。

### Self-gate 升级分析结论汇总

| # | 分析点 | 结论 |
|---|--------|------|
| 1 | 触发文件清单覆盖 | 不需要升级 |
| 2 | 反向传播路径表 | 需要升级（加 1 行） |
| 3 | A6 锚点表描述 | 需要升级（补 1 句说明） |
| 4 | Layer 0/Layer 1 边界 | 不需要强制升级（可选补 1 句，非必须） |
| 5 | DESIGN_GAP 机制提及 | 需要升级（补审查原则第 6 条 + 输出格式标注约定） |

**汇总：5 项分析中，3 项需要升级（#2/#3/#5），2 项不需要（#1/#4，其中 #4 附带一条非强制的可选建议）。** 三项建议升级的内容均为角色定义/流程文档的局部补充说明（合计约 20-30 行新增文字），不改变 self-gate 的两层架构（Layer 0 CHECK 9 + Layer 1 LLM 审查）本身，不属于紧急项——可在下次 self-gate 相关改动时一并处理，也可作为独立的小任务单独排期。
