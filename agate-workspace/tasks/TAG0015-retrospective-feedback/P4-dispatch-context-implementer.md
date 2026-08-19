> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心输入源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。

---
phase: P4
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0015
role: implementer
retry: 1
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

## 重试 #1（SELF-GATE 语义对齐审查发现的修复项，本节优先于下方原始派发指引）

上一版实现已通过 P4 review（approved）与全量测试，但按 SELF-GATE 流程派发的
protocol-alignment-review 发现 3 项 MISALIGNED + 1 项 NEEDS_HUMAN_REVIEW（完整报告见
`docs/reviews/agate-alignment-review-2026-08-19.md`）。用户已就 NEEDS_HUMAN_REVIEW 项做出裁决
（见下方 1）。本次修复不重写已有实现，只做下列针对性修改：

### 1. ADR-007 合规（A7，用户裁决：扩展 agate-md-field-get.py，非维持现状）

`agate/scripts/agate-feedback.py` 目前本地重新实现了 frontmatter 字段读取（未复用 ADR-007
规定的"单一双读工具" `agate-md-field-get.py`）。修复方式——**扩展该工具注册新字段，
`agate-feedback.py` 改为调用它**：

a) `agate/scripts/agate-md-field-get.py`：
   - `NO_FALLBACK_LIST_FIELDS` 新增 `"mechanism_issues"`, `"execution_issues"`（list，无正文
     回退——retrospective.md 是全新文档类型，无需兼容旧格式；换行连接格式化，与既有
     `need_confirm_resolved` 等字段同语义）
   - `NO_FALLBACK_BOOL_FIELDS` 新增 `"feedback_ready"`（bool，无正文回退）
   - 按既有代码风格加一行注释说明来源（TAG0015，BDD-6/17）
   - 不改动任何既有字段的行为（`NO_FALLBACK_INT_FIELDS`/`LIST_FIELDS`/其余字段集合原样不动）

b) `agate/scripts/agate-feedback.py`：
   - 新增 `_md_field_get(op, file_path)` 函数，模式参照 `agate/scripts/check-gate.py:_md_field_get`
     （`subprocess.run([sys.executable, MD_FIELD_GET, op], env={"FILE": file_path, ...})`，
     `MD_FIELD_GET = os.path.join(SCRIPT_DIR, "agate-md-field-get.py")`）
   - `main()` 里 `mechanism_issues`/`execution_issues`/`feedback_ready` 三个值改为调用
     `_md_field_get()` 取得（`mechanism_issues`/`execution_issues` 用 `.split("\n")` 还原列表，
     空字符串还原空列表；`feedback_ready` 用 `== "true"` 还原布尔）
   - `task_id` **保持本地 `fm_data.get("task_id", "")` 读取不变**——task_id 不是本次 ADR-007
     违规点，不在修复范围内，不要顺手改动
   - `_extract_frontmatter_block` 函数**保留**（仍需要本地判断"文件是否有 frontmatter 块"以
     给出正确的用户可见错误信息，且仍用于读取 `task_id`），不要删除

### 2. `test_bdd20_source_contains_no_network_submit_calls` 断言过窄，需订正（连带 1 的必然结果）

`agate/tests/unit/test_agate_feedback.py` 现有断言 `assert "subprocess" not in source` 把
"任何 subprocess 用法"都当作"网络提交调用"禁止，但 BDD-20 的真实 Given/When/Then（P1-requirements.md）
只要求"不调用 `gh`/`git push` 等网络提交命令"，从未要求"禁止一切 subprocess 使用"——本次为满足
ADR-007 新增的 `_md_field_get` 调用（本地脚本间通信，非网络操作）与 BDD-20 的真实意图不冲突，
但会撞上这条过窄的断言字面值。**修订断言为忠实反映 BDD-20 真实意图**：
```python
def test_bdd20_source_contains_no_network_submit_calls(agate_scripts):
    script = agate_scripts / "agate-feedback.py"
    assert script.is_file(), "agate-feedback.py 尚未实现（P4 职责，P3 预期红灯）"
    source = script.read_text(encoding="utf-8")

    assert "git push" not in source
    assert re.search(r"\bgh\s", source) is None
    # subprocess 允许用于本地脚本间调用（如 agate-md-field-get.py，ADR-007 单一双读工具），
    # 但不得出现任何 git/gh 网络提交子命令字符串
    assert not re.search(r"subprocess\.\w+\(\s*\[[^\]]*\b(git|gh)\b", source)
```
这是**测试断言订正**，不是"改测试迁就实现"——断言过窄本身就是 P3 阶段的一个小疏漏（BDD-20 的
验收标准应该是"语义上不做网络提交"，不是"语法上不出现 subprocess 字面词"），在
`P4-implementation.md` 里用一句话说明这处订正的理由（引用本节）。

### 3. 三处文档同步缺口（A2/A3b/A5，同一组修复）

a) `agate/WORKFLOW.md:318`（Pre-commit 检查总览表，`check-retrospective.py` 行）：现文案只描述
   "异常模式提醒（重试超限/SCOPE+/override）→ 写复盘；不阻塞 commit"，未提及 BDD-10 新增的
   第 4 类"机制缺口信号"触发条件。追加一句区分，如：
   `异常模式提醒（重试超限/SCOPE+/override）→ 写复盘；另检测到 DEBT/roadmap 已登记本任务
   （机制缺口信号，TAG0015）→ 追加提醒；均不阻塞 commit（P2.12）`
b) `agate/scripts/README.md:37`：`check-retrospective.py` 行同样补一句提及机制缺口信号分支；
   新增一行登记 `agate-feedback.py`（如
   `agate-feedback.py | 跨项目反馈提取（AG0021，opt-in，AGATE_FEEDBACK=on）| 手动触发，非
   gate/非 pre-commit`）
c) `agate/tests/README.md:46`：`check-retrospective.py` 行的用例数从 `10` 更正为实际值（先跑
   `grep -c "^def test" agate/tests/unit/test_check_retrospective.py` 取得准确数字，不要照抄
   审查报告里的旧数字，因为本次改动 2 里对该文件又有新增，需要重新数）；新增两行登记
   `agate-feedback.py | unit/test_agate_feedback.py | {实际数字}`、`复盘协议文档条文 |
   unit/test_retrospective_protocol_docs.py | {实际数字}`（同样重新数，不要照抄审查报告数字）

### 修复后自检（强制）

1. `timeout 60s python3 -m pytest agate/tests/unit/test_check_retrospective.py
   agate/tests/unit/test_agate_feedback.py agate/tests/unit/test_retrospective_protocol_docs.py -v`
   全部通过（含订正后的 `test_bdd20_...` 断言）
2. `timeout 180s python3 -m pytest agate/tests/ -q --tb=short` 全量通过（注意：审查报告记录了
   3 个与本任务无关的**预置失败**——`test_check_pruning.py` 的 3 个用例，已用 `git stash` A/B
   核实改动前后均失败，不是本任务引入。你的自检若也看到这 3 个失败，属预期，不需要修，不要
   因为这 3 个失败而怀疑自己的改动——但若失败数≠3 或失败的不是这 3 个具体用例，需要停下来
   诊断，不要假设"反正有失败都是预置的"）
3. `timeout 60s python3 agate/scripts/check-protocol-consistency.py --strict` 仍 0 ERROR
4. `grep -n "mechanism_issues\|execution_issues\|feedback_ready" agate/scripts/agate-md-field-get.py`
   确认三字段已注册
5. `grep -n "_md_field_get\|subprocess" agate/scripts/agate-feedback.py` 确认已改为调用
   `agate-md-field-get.py`

---

### 目标（原始派发指引，重试时仍适用于未涉及修订的部分）

把 P2-design.md §1.1「改什么」的 6 大类改动逐条落地为真实文件改动，让 P3 阶段写的 3 个测试文件
（23 个新测试函数，20 条 BDD 全覆盖）从红转绿，同时不破坏既有 909+2 的测试基线。

### 约束（P2-design.md 已经把每一处改动写到"可直接照做"的颗粒度，本次实现严格照抄，不重新设计）

**§1.1 六大类改动落点（权威依据，逐条对照执行，不要跳过任何一条）**：

1. **类 4.1 模板迁移**（BDD-1~8）：`git mv docs/reviews/postmortem-template.md
   agate/assets/templates/retrospective-template.md`，然后按 P2-design.md §1.1 类 4.1 逐条
   （BDD-1 四节标题 / BDD-2 内容价值标准 / BDD-3 归因分层字段 / BDD-4 技术债登记行强制说明 /
   BDD-5 两类去向标注 + 追问句 / BDD-6 frontmatter 三字段 / BDD-7「## agate 反馈」节 / BDD-8
   挂钩点在 `phase-cards/P8-release.md:86` 附近新增核对项）改写新文件正文。`roadmap.md:313/316/322`
   三处 `docs/reviews/postmortem-template.md` 路径字符串按 P2 指引追加行内脚注式更正（不重写
   整段历史叙述）。
2. **类 4.2 check-retrospective.py**（BDD-9~11）：第 93 行路径文案改为 `tasks/{Txxx}/
   retrospective.md`；按 P2-design.md §3.1 伪代码新增 `_scan_debt_roadmap_signal(task_dir,
   state_file)` 分支，`main()` 新增独立的第二段 stderr 输出块，exit code 不变。
3. **类 4.3 state-machine.md**（BDD-12~13）：第 481 行按 P2 §1.1 给出的确切新文案替换；在
   orchestrator-log.md 防无响应小节之后新增「L2 会话 checkpoint（两件套）」小节，正文覆盖 P2
   §3.2 四点（与 orchestrator-log 关系 / P{n}-checkpoint.md 子机制 / task-session-summary.md
   子机制 / 两者共同覆盖范围），须同时含 `P{n}-checkpoint.md` 与 `task-session-summary.md`
   两个字面字符串（`test_bdd_13_l2_checkpoint_docs` 断言这个）。
4. **类 4.4 跨文件核实**（BDD-14）：`loop-orchestration.md:168,173` 与
   `agate/assets/templates/task-files.md:45` **不改文本**（P2 §1.1 类 4.4 已核实三处不与新
   规则矛盾）——但 `task-files.md`「辅助文件」表（不是"各阶段文件清单"表，P2 §1.2 已明确区分）
   需要新增 2 行说明 `P{n}-checkpoint.md` + `task-session-summary.md`（这是候选方案 A1 落盘
   文件的必要联动，属于类 4.3 的延伸，不是 BDD-14 本身要求）。
5. **类 4.5 AGENTS.md**（BDD-15）：第 11 行按 P2 §1.1 给出的确切新文案替换（只改这一行所在
   段落）。
6. **类 4.6 docs/reviews/ 5 份存量文件标注**（BDD-16）：按 P2 §1.1 给出的确切标注文案，逐一
   插入到 5 个文件（tag0008/tag0010-0011 正文+review/tag0013/tag0014）第 1 行前。
7. **类 4.7 agate-feedback.py 新增**（BDD-17~20）：新建 `agate/scripts/agate-feedback.py`，
   按 P2-design.md §2 候选方案 B1（轻量正则脱敏，具体规则见 B1 四点）+ §1.1 类 4.7 四条 BDD
   逐项实现：frontmatter/agate 反馈节解析（本地实现，不 import agate-frontmatter-check.py，
   参照其 `_extract_frontmatter_block` 正则模式）、`_anonymize(text, project_root)` 函数、
   `AGATE_FEEDBACK` 开关（`os.environ.get("AGATE_FEEDBACK", "off")`，非 "on" → stderr 提示 +
   `sys.exit(2)`）、stdout 输出 JSON + Markdown 片段（`--format` 参数，默认 both）、**不得**
   `import subprocess` 调用任何 `git push`/`gh` 命令（P3 测试 `test_bdd20_source_contains_no_
   network_submit_calls` 会 grep 源码断言这一点）。

**§1.2 不改什么（严格遵守，不要顺手"优化"或"顺便改动"这些范围外的文件）**：
`docs/hardening-roadmap.md` / `agate-workspace/archived/` / `TAG0013-script-consistency`
历史任务产物 / `agate/WORKFLOW.md:91,318` / `agate/state-machine.md:361` / `dispatch-protocol.md`
/ `task-files.md`"各阶段文件清单"表（只改"辅助文件"表）/ `docs/reviews/agate-alignment-review-*.md`
与 `opencode-session-extraction-guide.md` / `check-retrospective.py` 的 exit code 契约（恒为0）。

**风险缓解（P2 §1.3 R5，实现完成后必须做）**：跑一次全仓兜底 grep
`grep -rn "docs/reviews/postmortem-template" . --include="*.yml" --include="*.yaml"
--include="*.json"`，确认无遗漏引用（若有命中，追加更新，不留旧路径死链）。

### 让 P3 测试转绿的关键提示

- `test_check_retrospective.py` 的 BDD-9/10 新增用例 + `test_agate_feedback.py` 全部用例 +
  `test_retrospective_protocol_docs.py` 全部用例，实现完成后应全部转绿——写完代码后自跑
  `timeout 60s python3 -m pytest agate/tests/unit/test_check_retrospective.py
  agate/tests/unit/test_agate_feedback.py agate/tests/unit/test_retrospective_protocol_docs.py -v`
  确认（这是自查，不是 P5 gate，不要在返回里声称"P5 已过"）。
- 若某条测试断言与 P2 设计的字面文案/路径字符串不完全一致（如测试断言的具体子串），**以测试
  为准微调实现的措辞**，不要反过来修改测试断言迁就实现的随手写法——除非测试本身有明显 bug
  （断言与 P1/P2 的 Given/When/Then 矛盾），此时标 `[SCOPE+]` 或在 P4-implementation.md 里
  说明原因，不要静默改测试。

### 输入文件

严格按 P2-design.md `files_to_read` 声明的清单读取（14 条，含精确行号范围），不要在项目里盲目
搜索或整目录全读：
`{AGATE_WORKSPACE}/tasks/TAG0015-retrospective-feedback/P2-design.md` 的「files_to_read」节
（约第 432-460 行附近）。额外必读：
- `{AGATE_WORKSPACE}/tasks/TAG0015-retrospective-feedback/P1-requirements.md`（20 条 BDD 原文，
  实现细节有疑问时对照 Given/When/Then）
- `{AGATE_WORKSPACE}/tasks/TAG0015-retrospective-feedback/P3-test-cases.md` + 三个测试文件
  本身（`agate/tests/unit/test_check_retrospective.py` 的新增部分 / `test_agate_feedback.py` /
  `test_retrospective_protocol_docs.py`，测试代码是"要让什么变绿"的最直接规格）

### 门槛（什么算完成）

P4-implementation.md 声明 `implementation_dir`；三个测试文件全部转绿；既有 909+2 测试基线不变；
`check-protocol-consistency.py --strict` 仍 0 ERROR；全仓兜底 grep（R5）已跑并处理命中项。
</dispatch_guide>

<!-- AGATE_CARD_START -->
## 当前阶段卡片：P4

路径：phase-cards/P4-implementation.md
---
# P4 — 代码实现

> 当前状态：[首次 / 重试 #N / 裁剪跳阶]
> 裁剪跳阶 → 确认 P1 phases 不含 P4 且有合规理由（check-pruning.py 已检查）→ 跳过，读 P5 卡片

## 如果是首次进入本阶段

0. 跑 `agate-capture-env-baseline.py $TASK_DIR`（自动捕获环境基线）。
   该步骤不会阻塞流程——任何 stderr 输出（含 WARNING）均可忽略，直接继续步骤 1，
   无需查看结果、无需判断、无需因为看到 WARNING 而停下来处理。
1. 派发 implementer subagent → 产出代码文件
   1.1 写 P4-dispatch-context-implementer.md（派发指引：目标/约束/上游关联/输入文件 + 客观查证信息）
2. 按 P2 的 gate_commands 跑单元测试（非 gate，只是自查）
3. 按 C8 映射表派发评审（见下方）
4. 预跑 check-gate.py P4（确认暂存区有代码文件）
5. git add {AGATE_WORKSPACE}/tasks/{Txxx}/ + 代码文件（含 .state.yaml，若 .gitignore 忽略需 git add -f）
   ⚠️ 此时 .state.yaml 的 phase 保持 P4，不要提前写 P5——phase = 本 commit 的产出阶段
6. git commit -m "wf({Txxx}-P4): {摘要}"（phase=P4，P4 产出含 P4-implementation.md + 代码文件）
7. P4 commit 完成后进入 P5：**phase 推进 P5 随 P5 产出 commit 一起**（P5-test-results/ 就绪后），不是单独 phase commit

## 如果是重试

确认上一轮失败原因（来自 gate 输出 / review rejected 理由）
→ 只修复失败项，不重做已通过的部分
→ 修复后重跑全量测试（T027 教训：修复可能引入回归）
→ 读 agate/rules/state-transitions.md 确认 retry 上限（P4 MAX=3）

**若这次是从 P6（或其他更后的阶段）退回来的**：`{AGATE_WORKSPACE}/tasks/{Txxx}/` 下不会再有旧的 P6-acceptance.md（已被归档），但当初具体是哪条 BDD 失败、失败原因是什么，会摘要在 `{AGATE_WORKSPACE}/tasks/{Txxx}/.retreat-history.md` 里——**重新派发 implementer 时，dispatch-context 必须引用这份摘要**，不能让 implementer 只看到"现有代码"却不知道具体要修哪里。已有代码不会被撤销、也不需要重新实现，是在已有实现基础上定向修复。**回退落地后必须建 DEBT 条目**（`source: retreat`，`evidence` 引用 retreat 提交哈希，模板 `assets/templates/tech-debt-template.md`——TAG0001 强制，见 `agate/rules/state-transitions.md` 回退规则节）。

## 前置条件

- [ ] P2-design.md 存在且 files_to_read 字段完整（导航清单）
- [ ] P2-review.md status: approved（P2 不可裁剪）
- [ ] P3-test-cases.md 存在（测试已设计）
- [ ] check-tdd-red.py 确认红灯（测试先于实现）
- [ ] 未跳过 P4（如有裁剪理由，见上方裁剪跳阶）

## 派发

- **角色**：implementer（`{agate_root}/assets/execution-roles/implementer.md`）
- **输入**：P2-design.md（files_to_read 导航 + gate_commands）+ P3-test-cases.md + P0-brief.md（env_constraints）
- **输出**：代码文件（在 P4-implementation.md 声明的 implementation_dir 下）
- **派发 prompt 模板**：`{agate_root}/assets/templates/dispatch-prompt.md` + 以下阶段特定追加：

```
## 上下文控制
读取代码文件以 P2-design.md 的 files_to_read 清单为准，按需读取（标了行号范围的只读片段）。
不要在项目里盲目搜索或整目录全读。

## 自查≠gate
写完代码后应自跑测试确认基本功能（自查），但自查通过 ≠ P5 gate 通过。
P5 由主 Agent 派发 verifier subagent 执行 gate_commands.P5，主 Agent 验 gate（检查产出 + failed 计数 + N5 最小校验）。
不要在返回中声称"P5 已过"或"全部测试通过"——只返回路径 + 摘要。

## 生产环境隔离
任何写入生产环境/生产数据库/生产 API 的操作都必须先 PAUSED 报告人工。
```

## 产出规格

- P4-implementation.md 必须声明 `implementation_dir: {实际路径}`
- 代码文件在声明的目录下
- 遵守 P2-design.md 的方案设计 + 现有项目代码规范

## 评审派发（C8 机械映射）

**在 P4 实现完成后、gate 前**，按 P1 声明的 domains 和 risk_level 派评审。C8 映射表是机械规则，不靠判断"需不需要"：

| domain | 派哪些评审 | 产出 |
|--------|----------|------|
| backend | review | P4-review.md |
| frontend | design-review | P4-review.md |
| mcp | review（关注 MCP 接口契约）| P4-review.md |
| security | cso | P4-review.md |
| risk=high | P4 实现评审（按 domains 派 review/design-review/cso；P2 plan-eng-review 已审方案，P4 实现评审不可省）| P4-review.md |

多个评审角色 `专家组并行` → 所有返回后派组长汇总 → 统一 P4-review.md（status: approved / rejected）。
详见 `agate/rules/review-mapping.md`。

**并行派发**（多个评审角色时）：
1. 同时派发所有触发的评审 subagent（每个一个 task 调用）
   > **操作方式**：在一个 assistant 消息中连续发起多个 task 工具调用（每个评审角色一个）。
   > 不要等前一个 task 返回再发下一个——那是串行，不是并行。
   > 平台会并行执行多个 task，全部返回后再进入下一步（派发组长汇总）。
2. 每个评审 subagent 各写一个 dispatch-context + 各自产出文件
3. 所有评审返回后，派发组长汇总 subagent（角色：review + 指定为「专家组组长」）
4. 组长产出：P4-review.md。**agent 字段必须非 main**（与 P2 评审同规则，check-gate.py 在 P2 分支硬拦截 agent=main 的 approved）
5. 组长规则：不发表新意见，只汇总；任何 BLOCKER → rejected；分歧 → 交人工；全票无 BLOCKER → approved

**单评审角色时**：直接派发，无需组长汇总，产出直接写 P4-review.md。

review 不通过 → implementer 修改代码 → 再 review → … → approved（⑩迭代循环，review 和 gate 重试共享 retry 预算）

## 按包拆分并行（条件触发，需额外约束）

> 仅当 P2 packages > 1 且包间无依赖时适用。单包任务跳过本节。
> 并行上限 / 失败批 retry / 共享文件统一后处理见 dispatch-protocol「派发编排机制」并行规则。

当 P2 声明多个 packages 且包间无数据依赖时，P4 可拆分并行，但**有额外约束**：

1. 每个 package 派一个 implementer subagent
2. **各 implementer 只改自己 package 目录下的文件**——跨包的共享文件（类型定义、接口、配置）由主 Agent 在所有并行 implementer 返回后统一处理
3. 各自返回路径 + 摘要
4. 主 Agent 汇总后统一 commit
5. 主 Agent 在所有 implementer 返回后，统一处理共享文件改动（如果有）

**冲突预防**：
- dispatch-context 约束节必须写明：`只改动 {pkg}/ 目录下的文件。共享文件（{列出}）不在本次改动范围内`
- 如果某个 implementer 必须改共享文件 → 该包不能并行，改为串行（主 Agent 先派其他包并行，再串行处理含共享改动的包）
- 无法确定是否有共享改动 → 串行（安全默认值）

**基础设施隔离（并行时强制）**：
- debug server 端口：每个 implementer 的 dispatch-context 约束节分配不同端口（如 pkg-a: 3001, pkg-b: 3002）
- 测试数据库：每个 implementer 用独立数据库路径（如 `test-{pkg}.db`），不共享同一 test.db
- 环境变量：dispatch-context 写明各 subagent 独立的环境变量值（如 `PORT=3001` vs `PORT=3002`）
- 临时文件：各 subagent 写入 `P4-implementation/{pkg}/` 独立目录

主 Agent 在并行派发前**必须**为每个 subagent 的 dispatch-context 分配上述隔离参数。当前无 gate 脚本检查（已知缺口），但未分配导致运行时冲突（端口占用/数据库锁）时计为重试，不算环境问题。

## gate 规则（check-gate.py 会跑）

```bash
check-gate.py P4 $TASK_DIR
```

- **exit 0**：暂存区含非 md/yaml 代码文件（git diff --cached --name-only）
- **exit 1**：暂存区仅 .md/.yaml 文件（无实际代码变更）→ 不能推进

## 推进条件（全部满足才写 phase: P5）

- [ ] 暂存区含代码文件（非 .md/.yaml）
- [ ] 按 C8 映射表触发的评审全部完成：P4-review.md status: approved（所有任务都要求——risk=high 的 P2 plan-eng-review 审方案，P4 实现评审按 domains 另行派发，不可省）
- [ ] SCOPE+ 已处理（若本阶段产生）：P1-requirements.md 有 [SCOPE_RESOLVED]（行首声明格式）
- [ ] git commit 完成

## 常见错误

1. **不读 files_to_read，在项目里乱翻**：implementer 拿到 P2 的 files_to_read 清单后应按清单阅读，不要在项目里全文搜索或整目录全读——上下文会爆炸
2. **自行加范围外改动**：发现需要做但不在 P1 范围内的改动 → 标 [SCOPE+]（行首声明格式）而非直接做
3. **只跑单元测试不验证集成**：单元测试全绿 ≠ 功能可用。P5 会跑 gate_commands 做技术验证，但要确保实现时路径依赖的端点行为已验证
4. **先更新 .state.yaml 再 commit**：state 和产出在同一 commit 里——不要先 commit 产出再单独 commit state
5. **gate 不过 ≠ 你失败了**：红灯指向工作/设计的问题，不指向你。正确动作是诊断→退回/重试/PAUSED，不是修改产出让它变绿。

## 下游影响

- P5 验证依赖：P5 跑 gate_commands.P5 的命令（在 P2 声明），确保你的实现能通过
- P6 验收依赖：实现路径的端点行为必须可验证（确认 API 返回正确的 Content-Type、状态码等）
- 代码改动文件路径：P8 发布时确认版本文件变更需要知道你改动了哪些 package

> 完成 → 读 phase-cards/P5-verification.md

6. **修改 P1 文档**：P4 发现 BDD 矛盾时标 DESIGN_GAP，不直接改 P1-requirements.md。需变更 P1 时标 `[BASELINE_CHANGE: 理由]` 并经主 Agent 批准。
<!-- AGATE_CARD_END -->

<objective_info>
- P2-design.md 是本次实现的权威规格来源，§1.1/§1.2/§1.3/§2/§3.1/§3.2/§5(files_to_read) 已经
  把每一处改动写到接近可直接执行的颗粒度，implementer 的核心工作是"照着写"而不是"重新设计"。
- 环境基线（P3 阶段验证过）：`pytest` 909 passed + 2 skipped（改动前）；本次改动后预期新增约
  23 个测试函数从红转绿，既有用例数不变。
- P0-brief known_risks 已预警本任务改动触发 SELF-GATE（改 `agate/*.md` + `agate/scripts/*.py`
  + `phase-cards/*`）——commit message 需含 `self-gate-review:` 或 `self-gate-skip:`（主 Agent
  在 commit 时处理，implementer 不需要关心 commit message，只需产出代码）。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
