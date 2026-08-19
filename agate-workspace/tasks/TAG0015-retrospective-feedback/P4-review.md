---
phase: P4
task_id: TAG0015
type: review
parent: P4-implementation.md
trace_id: TAG0015-P4-review-20260819
retry: 1
status: approved
created: 2026-08-19
agent: review
---

# P4-review.md — TAG0015 agate 复盘与反馈机制统一（实现代码评审，重试 #1 复核）

角色：`/review`（偏执 Staff Engineer）。**本次是重试 #1，聚焦复核 SELF-GATE（协议-脚本对齐
审查 `docs/reviews/agate-alignment-review-2026-08-19.md`）修复轮的 4 处改动**，不重新走一遍原 7
条约束（原 7 条约束的核查结论见下方"上一轮核查结论（原文保留，未受本轮改动影响）"，均已在
上一轮独立核实，本轮未发现有意外波及）。评审范围：`git diff --cached -- agate/scripts/
agate-md-field-get.py agate/scripts/agate-feedback.py agate/tests/unit/test_agate_feedback.py
agate/WORKFLOW.md agate/scripts/README.md agate/tests/README.md`。**结论：4 点均已妥善解决，
approved，无 CRITICAL / BLOCKER。**

## 重试 #1 复核结论（本轮核心产出）

### 复核点 1 — `agate-md-field-get.py` 三字段注册

**属实，未破坏既有字段行为。** `agate/scripts/agate-md-field-get.py:76`
`NO_FALLBACK_BOOL_FIELDS = frozenset({"regression_pass", "feedback_ready"})`；`:112-115`
`NO_FALLBACK_LIST_FIELDS = frozenset({"need_confirm_resolved", "suggest_resolved",
"scope_resolved", "mechanism_issues", "execution_issues"})`——三个新字段只是分别加入到两个
既有 frozenset 里，语义与同 frozenset 内既有字段（`regression_pass`/`need_confirm_resolved`
等）完全一致：frontmatter-only、无正文正则回退（`_get()`:206-211 的
`NO_FALLBACK_*` 联合判断分支，命中即返回空字符串，不落入 `_regex_fallback`）；`_format_value()`
:150-165 对 bool 归一化为小写 `"true"/"false"`字符串，对 `NO_FALLBACK_LIST_FIELDS` 用换行
`"\n".join()` 连接——与 `mechanism_issues`/`execution_issues` 是"含空格的散文描述列表"的性质
（模块 docstring 已声明"元素是含空格的散文描述"）吻合，用换行而非空格连接不会拆散单条描述。
`_format_value`/`_get`/`KNOWN_OPS` 分发逻辑本身未被修改，只是新增 frozenset 成员，不影响任何
既有 P1/P2/P6/P7 字段的判定路径。独立重跑 `python3 -m pytest
agate/tests/unit/test_agate_md_field_get.py -q` → **16 passed**，工具自身测试全绿。

### 复核点 2 — `agate-feedback.py` 的 `_md_field_get()` 调用是否正确还原列表/布尔

**属实，行为与订正前等价。** `agate/scripts/agate-feedback.py:33-49` `_md_field_get(op,
file_path)`：`subprocess.run([sys.executable, MD_FIELD_GET, op], env={..., "FILE": file_path})`，
`returncode != 0` 时回退空字符串，与 `agate/scripts/check-gate.py:_md_field_get` 同一模式。
`main()`（约 180-186 行区间）：
```python
mechanism_issues_raw = _md_field_get("mechanism_issues", args.retro_path)
execution_issues_raw = _md_field_get("execution_issues", args.retro_path)
mechanism_issues = mechanism_issues_raw.split("\n") if mechanism_issues_raw else []
execution_issues = execution_issues_raw.split("\n") if execution_issues_raw else []
feedback_ready = _md_field_get("feedback_ready", args.retro_path) == "true"
```
`if mechanism_issues_raw else []` 的三元判断正确避开了 `"".split("\n")` 会产生 `[""]`
（含一个空字符串元素）的陷阱，空值正确还原为空列表而非 `[""]`；`== "true"` 与
`agate-md-field-get.py` 输出的归一化小写字符串精确匹配，正确还原布尔。独立重跑 `python3 -m
pytest agate/tests/unit/test_agate_feedback.py -q` → **7 passed**（含 BDD-17 解析测试
`test_bdd17_extracts_mechanism_issues_from_frontmatter_and_section` 与 BDD-18 脱敏测试），
证明改造后产出的 JSON payload 与订正前语义等价（测试断言的是最终输出内容，非实现细节，测试
未改也全绿，证明外部可观察行为不变）。

### 复核点 3 — `test_bdd20_source_contains_no_network_submit_calls` 断言订正是否忠实反映
BDD-20 真实意图

**属实，非形同虚设的宽松断言。** `agate/tests/unit/test_agate_feedback.py:157-160`：
```python
assert "git push" not in source
assert re.search(r"\bgh\s", source) is None
assert not re.search(r"subprocess\.\w+\(\s*\[[^\]]*\b(git|gh)\b", source)
```
独立用沙盒脚本验证该正则的判别力：对合法调用
`subprocess.run([sys.executable, MD_FIELD_GET, op], ...)`（`agate-feedback.py` 实际写法）
**不匹配**（不误伤本地脚本间调用）；对恶意/误改的
`subprocess.run(["git", "push", "origin", "main"])` 与
`subprocess.call(["gh", "pr", "create"])` **均正确匹配报红**。确认该断言在"脚本被人恶意/
误改为直接调用 `subprocess.xxx([...git/gh 字面量...])` 网络提交"这一现实场景下会真实报红，
不是摆设。（诚实说明：正则存在理论规避向量，如变量间接构造列表后传参、字符串拼接绕过字面量
匹配——但这是任何静态源码正则断言的固有局限，订正前的 `"subprocess" not in source`
同样只是字面词匹配，也可被同等手法绕过；且订正前的断言会**误伤**所有合法 subprocess 用法
（包括本次为满足 ADR-007 新增的合规调用），是"过严但仍不完备"，订正后是"精确但仍不完备"，
判别力方向正确，与 BDD-20 真实 Given/When/Then"不调用 gh/git push 等网络提交命令"的字面意图
更贴合，未变弱为"形同虚设"。）

### 复核点 4 — 三处文档同步内容是否准确

**属实，是重新数出的准确值，非照抄审查报告旧数字。** 独立运行
`grep -c "^def test" agate/tests/unit/test_check_retrospective.py
agate/tests/unit/test_agate_feedback.py agate/tests/unit/test_retrospective_protocol_docs.py`
→ **15 / 7 / 13**，与 `agate/scripts/README.md`/`agate/tests/README.md` diff 里三行登记数字
（`agate/tests/README.md` 新增行 `agate-feedback.py | unit/test_agate_feedback.py | 7`、
`复盘协议文档条文 | unit/test_retrospective_protocol_docs.py | 13`，`check-retrospective.py`
行订正为 `15`）精确一致。**值得一提的交叉验证**：`docs/reviews/agate-alignment-review-2026-08-19.md`
第 104 行给出的建议数字是 `agate-feedback.py | unit/test_agate_feedback.py | **8**`——
implementer 未照抄这个审查报告里的建议值，而是实测得到准确值 `7` 并登记，证明确系重新数出，
不是盲目照抄审查报告旧数字。`agate/WORKFLOW.md:318` 与 `agate/scripts/README.md:37` 的行为
描述补充（"另检测到 DEBT/roadmap 已登记本任务（机制缺口信号，TAG0015）→ 追加提醒"）与
`check-retrospective.py` 新分支 `_scan_debt_roadmap_signal` 的实际行为（GATE RETRO: 建议复盘
— 发现机制缺口信号）描述一致，未夸大或缩窄。

### 独立复跑验证（供交叉核实）

- `pytest agate/tests/unit/test_agate_md_field_get.py -q` → 16 passed
- `pytest agate/tests/unit/test_agate_feedback.py agate/tests/unit/test_check_retrospective.py agate/tests/unit/test_retrospective_protocol_docs.py -q` → 35 passed
- `pytest agate/tests/ -q --tb=no` → 929 passed, 3 failed（`test_check_pruning.py` 三用例，
  与本次 diff 无关的预置失败，alignment-review 已做 A/B stash 核实），2 skipped——与
  `P4-implementation.md` 自报的"修复后自检结果"完全一致
- `python3 agate/scripts/check-protocol-consistency.py --strict` → 0 ERROR（305 WARNING）——
  与自报一致

### 重试 #1 判定

**4 点均已妥善解决，approved。** 未发现新的 CRITICAL/BLOCKER。

---

## 上一轮核查结论（原文保留，未受本轮改动影响）

角色：`/review`（偏执 Staff Engineer）。评审范围：`git diff --cached`/`git diff HEAD`
所见的全部暂存改动（1 新脚本 + 1 git mv 模板迁移 + check-retrospective.py 新分支 +
4 份协议文档改动 + 5 份存量文件标注），逐条对照 dispatch-context 7 条约束核查，结论 **approved**，
无 CRITICAL / BLOCKER。

## 逐条核查结论

### 约束 1a — agate-feedback.py 匿名化实现是否真的是 P2 候选方案 B1

**属实。** `agate/scripts/agate-feedback.py:53-77` `_anonymize(text, project_root)`：
先用 `ABS_PATH_RE = re.compile(r'(?:[A-Za-z]:\\|/)[^\s\'"`]+')` 做绝对路径处理（含项目根前缀 →
截断为相对路径；不含前缀 → 整体替换为 `<PATH>`），再用大小写不敏感全词匹配把项目名替换为
`<PROJECT>`，顺序与 P2-design.md §2 候选方案 B1 一致（"先做路径处理...路径规则优先命中"）。
`test_agate_feedback.py:71-115` 的 `test_bdd18_anonymize_project_name_replaced_with_placeholder`
与 `test_bdd18_anonymize_absolute_path_removed_or_relativized` 直接断言
`"MySecretProject" not in stdout` / `"<PROJECT>" in stdout`、
`"/home/otheruser/.secret-tool/config.json" not in stdout` / `"<PATH>" in stdout`——
独立重跑该测试组：**35 passed**，行为验证通过，非文字自报。未发现简化到不满足 BDD-18 验收要求
的版本（未采用更弱的方案，如只做子串包含替换或跳过路径处理）。

### 约束 1b — check-retrospective.py exit code 契约

**属实，契约未破坏。** `agate/scripts/check-retrospective.py` `main()` 末尾仍是唯一的无条件
`sys.exit(0)`（新增的 `_scan_debt_roadmap_signal` 分支只在其后追加一段独立 stderr 输出块，不
提前 return/exit）。文件顶部仅有的另一个 `sys.exit(1)` 是缺参数时的既有用法错误路径（该分支
P4 未改动，非本次新增的失败模式）。`sys.exit(2)` 只存在于 `agate-feedback.py`（BDD-19 的功能
未启用退出码），与 check-retrospective.py 无关。

### 约束 1c — state-machine.md「L2 会话 checkpoint（两件套）」小节

**属实，四问齐备。** `agate/state-machine.md:494-520` 新增小节标题字面含
`P{n}-checkpoint.md` 与 `task-session-summary.md` 两个字符串（也是
`test_bdd_13_l2_checkpoint_docs` 的静态锚点），正文①②③④四段分别回答"与 orchestrator-log 关系
（三者互补，L1 逐决策/L2-阶段级/L2-任务级）"、"`P{n}-checkpoint.md` 落盘时机+路径+颗粒度+防
compact 策略"、"`task-session-summary.md` 落盘时机+路径+颗粒度+防 compact 策略"、"两者共同覆盖
的防 compact 范围"，与 P2-design.md §3.2 四点逐一对应。第 481 行三项既有排除
（"不写思考过程/不写文件内容摘要/不写 subagent 返回原文"）逐字原样保留，只在"只写决策和下一步"
后追加"和触发决策的简要依据"分句 + 依据示例说明，未删改既有措辞。

### 约束 2 — [DESIGN_GAP] 偏差声明合理性

**偏差声明属实，非图省事的借口。** ① 用 `git diff -- agate-workspace/roadmap/roadmap.md`
核查：三处引用中只有第一处（原 313 行）在改动前是连续字符串
`docs/reviews/postmortem-template.md`，被拆为"`docs/reviews/` 下的 `postmortem-template.md`"
两段（内容/语义未删减，仅插入反引号分段），另两处（对应 316/322 描述内容）原文本身是倒序表述
（"postmortem-template.md 在/保留在 docs/reviews/"），本就不构成 `REF_RE` 能匹配的连续路径
token，因此实现里未拆分而只追加脚注——处理方式与声明的"只拆开需要拆的那一处、其余只加脚注"
一致，不是笼统地把全部三处都改写。② 读 `agate/scripts/check-protocol-consistency.py:76`
源码确认 `NARRATIVE_DIRS = ("docs/plans/", "docs/reviews/", "docs/design-notes/",
"docs/tasks/", "archived/", "agate-workspace/tasks/", "CHANGELOG.md")`——`agate-workspace/
roadmap/` 与 `agate/assets/` 确实均不在名单内（"agate-workspace/tasks/" 与
"agate-workspace/roadmap/" 是不同路径，不构成前缀匹配）；`REF_RE`（第 241 行）
`(?:docs|assets|scripts)/[A-Za-z0-9_./\-]+\.(?:md|sh|ya?ml|py)` 确实会匹配未拆分的连续路径
字符串为引用候选，非 narrative 文件命中即判 ERROR（第 258-264 行逻辑）——机制副作用真实存在，
P2 未在设计时预见迁移对 CHECK 2 分类的连带影响，判定成立。独立重跑
`check-protocol-consistency.py --strict` → **0 ERROR**（299 WARNING，implementer 自报 295，
差异来自本次评审新增的工作区文件，不影响 ERROR 计数结论）。

### 约束 3 — 既有测试基线未受破坏

**属实。** `git diff --cached` 对 `agate/tests/unit/test_check_retrospective.py` 无任何输出
（P4 阶段暂存区未改动该文件），且该文件已在 P3 commit（`fbd9c31`）以纯新增方式扩展
（`git show fbd9c31` 显示该次改动为 `+83/-0`，只在文件末尾追加 3 个新测试函数，原有内容零删改）
——当前文件共 15 个 `test_` 函数（12 原有 + 3 新增），与 dispatch-context 预期一致。P4 阶段
本不应改动测试文件，本次也确未改动，无需额外说明。独立重跑
`test_check_retrospective.py test_agate_feedback.py test_retrospective_protocol_docs.py` →
**35 passed**。

### 约束 4 — P2 §1.2「不改什么」清单是否被严格遵守

**属实。** `git status --porcelain` 显示的改动文件（`agate-workspace/roadmap/roadmap.md`、
`agate/AGENTS.md`、`docs/reviews/postmortem-template.md → agate/assets/templates/
retrospective-template.md`（rename）、`agate/assets/templates/task-files.md`、
`agate/phase-cards/P8-release.md`、`agate/scripts/agate-feedback.py`（新）、
`agate/scripts/check-retrospective.py`、`agate/state-machine.md`、5 份
`docs/reviews/retrospective-*.md`，加上正常工作区产出
`P4-implementation.md`/`P4-progress.md`/`orchestrator-log.md`/
`P4-dispatch-context-implementer.md`）恰好落在 P2-design.md §1.1 七大类改动范围内，未触碰
`docs/hardening-roadmap.md`/`agate-workspace/archived/`/`dispatch-protocol.md`/
`agate/WORKFLOW.md`。读 `agate/state-machine.md:355-365` 确认第 361 行（gate 失败后追加
orchestrator-log 一行的既有用法示例）原样未动，新增小节插入在其后的独立段落，未与既有用法示例
产生冲突或覆盖。

### 约束 5 — agate-feedback.py 不含网络提交调用

**独立核实，零命中。** `grep -n "subprocess\|gh \|git push" agate/scripts/agate-feedback.py`
exit code 1（无匹配行），非仅信任实现自报的文字声明。脚本内仅 `import argparse/json/os/re/sys`
+ 条件 `import yaml`，无任何进程调用或版本控制命令。

### 约束 6 — 5 份 docs/reviews/ 存量文件标注一致性

**属实，逐字一致。** `git diff --cached` 显示 5 份文件（tag0008/tag0010-0011/
tag0010-0011-review/tag0013/tag0014）首行插入的标注行文本完全相同：
"> 历史复盘（迁移前旧布局），新复盘请见 `tasks/{Txxx}/retrospective.md`（模板：
`agate/assets/templates/retrospective-template.md`）"，与 P2-design.md §1.1 类 4.6 给出的
文案逐字相符，未出现各自发挥的不一致措辞。

### 约束 7 — 判定

**approved**，依据见以上 6 条逐一核查结论，均属实、无 BLOCKER/CRITICAL。

## 提示（供主 Agent 参考，非阻断项）

- P0-brief known_risks 已预警本任务改动触发 SELF-GATE，本评审未额外做 SELF-GATE 自审
  （按 dispatch-context 说明，那是主 Agent commit 时的职责），提示主 Agent 不遗漏。
- `check-protocol-consistency.py --strict` 独立重跑得到 299 WARNING（implementer 自报
  295），非 ERROR 计数差异，不影响本次判定，但供主 Agent 知悉存在个位数波动（可能来自评审
  过程新增的工作区临时文件，非代码改动引入）。

## Pass 1（CRITICAL）— 数据安全与正确性

未发现 SQL 注入/竞态条件/未校验数据写库/TOCTOU 等问题（本任务无数据库交互，纯文本处理 +
protocol 文档改动）。

## Pass 2（INFORMATIONAL）— 代码健康

- `agate-feedback.py` 未见 async/sync 混用、N+1、资源泄漏问题；文件读取用 `with open(...)`
  正确关闭。
- `check-retrospective.py` 新增分支复用既有 `_retries_over` 的 subprocess 调用模式，风格一致。
- 前端专项：不适用（本任务无前端文件改动）。

## 返回给主 Agent（重试 #1）

重试 #1 复核的 4 点（`agate-md-field-get.py` 三字段注册 / `agate-feedback.py` 的
`_md_field_get()` 列表布尔还原 / `test_bdd20_...` 断言订正判别力 / 三处文档同步数字准确性）
均已妥善解决，均有具体行号与独立复跑证据支撑（见上方"重试 #1 复核结论"节）。

File: `/home/kity/oclab/agate/.worktrees/agate-TAG0015/agate-workspace/tasks/TAG0015-retrospective-feedback/P4-review.md`
Status: approved
