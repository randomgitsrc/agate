---
phase: P2
task_id: TAG0026
type: review
parent: P2-design.md
trace_id: TAG0026-P2-review-20260830
status: approved
created: 2026-08-30
agent: plan-eng-review
---

# P2-review — TAG0026 维护性反模式 gate（RM-AG0046）方案设计评审

> 评审对象：`agate-workspace/tasks/TAG0026-maintainability-gate/P2-design.md`（architect 产出，候选 A 选定）
> 评审角色：plan-eng-review（工程经理视角，单评审角色，直接产出本文件，无组长汇总）
> 评审方式：只审不改。设计文档所有声称的行号/机制均经 worktree 实际读取代码核实（含 git plumbing 行为与
> `count_kf_entries` 正则的沙箱实测），不采信 architect 自述。
> 环境隔离声明：全程未接触生产环境，仅读取 worktree 仓库文件与沙箱内临时目录实测。[PROD_NOT_TOUCHED]

<!-- AGATE_FIELD_HINT: status 见文件头 frontmatter（评审完成后由 agate-md-field-set 写入 approved/rejected） -->

## 逐项核查结论（dispatch-context 约束 2 的 11 项）

### 1. gate_p4 挂载点与返回约定 — 成立

实测 `agate/scripts/check-gate.py:870-927`：gate_p4 结构为 ①review 存在→1（:872-877）②status 非
approved→1（:879-883）③agent 缺失→2 / agent=main→1（:885-891）④staged 代码检查→1（:893-905，其中
`git diff --cached --name-only` 在 :895、无代码文件 return 1 在 :905）⑤骨架/CODE-MAP WARNING 不阻断
（:907-925）⑥return 0（:927）。设计声称的挂载点（④之后、⑤之前）真实存在且为唯一切入位。

"门槛 c 复用既有 ①②③"的顺序声称**成立**：新步骤伪代码（P2-design.md §3.2，:139-165）位于既有 ①②③
之后，若 ①②③ 已 return，新步骤不会执行——BDD-9（数量对齐但评审未 approve 仍阻断）由顺序天然保证：
P4-review.md 缺失/非 approved/agent=main 三态均在 :877/:883/:891 提前 return 1，能走到新步骤即 ①②③
已通过。不新增 return 2 的声称同样成立：伪代码所有失败路径均为 `return 1`（门槛 a/b），其余场景继续
向下落至 :927 return 0，与现状等价。

**非阻塞提醒**：门槛 c 无代码实体（复用既有检查），按伪代码实现时门槛 b 与 `else` 分支之间不得意外
加 `return 0`——若误加，violations 非空场景会跳过骨架 WARNING 与 return 0 主路。此提醒已可由
M10-G5「无 violations 回归面」测试覆盖面延伸确认（见测试缺口 2）。

### 2. consistency 扫描面方案（R6）— 成立

实测 `agate/scripts/check-protocol-consistency.py`：`SCRIPT_ALIGNMENT_ANCHORS` 表尾在 :749-751
（"check-structure-consistency.py" 条目，列表闭合 `]` 于 :751）；`check_script_alignment` 的 callers
校验在 :771-787，核心机制 :773 `script_basename = Path(anchor["script"]).name` + :777
`script_basename in full.read_text(...)`——确为**字面 basename 子串匹配**；import 语句
`from check_maintainability import check_maintainability` 不含 `.py` 字样，不会被命中。设计
（M3/R6/§3.6）要求 gate_p4 挂载处注释含字面 `check-maintainability.py`，对策正确且必要。
`GATE_SCRIPT_EXEMPT`（:791-794）现有 2 项，设计选"登记而非豁免"与该表"无 gate 逻辑才豁免"的注释
语义一致。`check_anchor_coverage` 的 `check-*.py` glob 在 :807-811，`SCRIPT_ALIGNMENT_ANCHORS` 与
`GATE_SCRIPT_EXEMPT` 定义处均含字面 `check-protocol-consistency.py`（:792），`agate-summary.py` 的
`_DRIFT_SCRIPTS` :42-50 实测 7 项与 M4 声称一致——M3+M4+R6 方案能防 CHECK9-coverage / CHECK9-callers
WARNING。

### 3. R7 P3* 键收集行为 — 成立（实测确认，规避必要且正确）

实测 `agate/scripts/agate-read-gate-commands.py:60`：
`elif key.startswith("P3") and not is_gate_meta_key(key):` 后收集 `{"cmd": val, ...}`——所有 `P3*`
非元键（含 `P3_consistency`、`P3_count` 等任意后缀）确实被收集为测试命令，经 `check-tdd-red.py:61`
（READ_GATE_COMMANDS）消费执行。`is_gate_meta_key`（agate_common.py:79-87）只精确匹配 `_formatter` /
`_timeout_seconds` 两个后缀，救不了 `P3_xxx`。`is_legal_gate_key`（agate_common.py:679-693）对
`P3_xxx`（P3 为合法阶段 + 合法后缀形态）返回 True——对账只发 WARNING 不拦截。因此设计 §4 "无
`P3_xxx` 检测命令键"是必要规避（非可选项），检测器红灯由 `P3: "python3 -m pytest"` 统一承载的
方案正确（检测器模块函数 + CLI exit code 均可被 pytest 覆盖，§5 G10/§5.2 G1-G4 已覆盖）。

### 4. R8 count_kf_entries 样例行防虚高 — 成立

实测 `agate_common.py:1015-1017`：`count_kf_entries` 正则为 `^\|\s*[0-9]+\s*\|`。沙箱 python3 实测：
`| # | ...` 与 `| # | | god-file 跨越 / fuzzy-boundary | ...` 均不命中（False），`| 1 | a.py | ...`
命中（True），分隔行 `|---|` 不命中。设计 M5/§3.3 样例行首用 `| # |` 防照抄模板未改导致计数虚高的
机制**成立**。另实测 `known-failures-template.md:14` 样例行确为 `| 1 |`（本设计 M5 对 known-violations
模板改用 `| # |` 是对既有模板样例行为的有意改进，语义反转场景下合理）。

### 5. R4 _norm_rel 单源复用链 — 可行

实测 `agate/scripts/agate-risk-score.py`：`_load_script` :46-54（importlib spec_from_file_location，
模块名连字符转下划线）、`_norm_rel` :86-88（`path.replace("\\", "/")`，模块级 def、无封装/下划线
导入限制）。候选 A 复用链（P2-design.md §2.1/§3.1）可行：`_load_script("agate-risk-score")` 返回
模块对象，`mod._norm_rel` 可直接引用。`run_git`（agate_common.py:50，`def run_git(args, cwd=None)`）
与 `count_kf_entries`（agate_common.py:1015）均可经 `from agate_common import ...` 复用，与
check-gate.py:32-41 既有 ImportError 兜底先例同型。**非阻塞**：建议 P4 实现时注明
`_load_script("agate-risk-score")` 会传递加载 check-pruning 模块（risk-score 模块级 :58-59
`_load_script("check-pruning")`），import 副作用面因此比表面多一层（详见非阻塞问题 3）。

### 6. R3 god-file 行数计算 git plumbing 语义 — 成立（沙箱实测）

实测（沙箱临时 git 仓库）：新增文件 staged 后 `git show :new.txt` 与 `git show :0:new.txt` 均成功
返回 staged 内容——设计 §3.1 "after = `git show :{path}`（staged 版本）"可行；`git show HEAD:new.txt`
对无 HEAD 仓库失败（`fatal: 无效的对象名 'HEAD'`，exit ≠ 0）→ 新增文件/首次提交 before=0 的兜底
必要且可行（`git rev-parse --verify -q HEAD` exit 1 可作首次提交探测）；修改已提交文件后
`git show :mod.txt` 取 staged 4 行、`git show HEAD:mod.txt` 取 HEAD 3 行——与"判定本次 commit"的
语义自洽。设计 §3.1 风险兜底（新增文件/HEAD 缺失 → before=0）在 plumbing 语义上无缺口。

### 7. gate_commands 契约完整性 — 通过

实测 P2-design.md §4（:234-247）：11 键 = P3 / P5 / P5_timeout_seconds / P5_consistency /
P5_consistency_timeout_seconds / P5_count_tests / P5_count_tests_timeout_seconds / P5_ruff /
P5_ruff_timeout_seconds / P5_shellcheck / P5_shellcheck_timeout_seconds，每键各占一行、无 `&&` 链
（TAG0004 短路反模式规避到位）。timeout 档位：P5=600s（构建档，TPV0093 教训对齐）、consistency=120s
（单测档）、count_tests/ruff/shellcheck=60s，与 P2 卡三档基准表一致；P3 不声明 timeout（走
`AGATE_TDD_TIMEOUT`，P2 卡字段规则第 1 条）。**无 `P3_xxx` 键**（第 3 项已证必要）。P5_ruff 用
`~/.venvs/agate-dev/bin/ruff`（CI 锁 ruff==0.16.4 对齐）；P5_consistency 用 worktree 相对路径
`agate/scripts/check-protocol-consistency.py`（dogfooding 约定，AGENTS.md；§7 workspace_note 再次
强调）。与 dispatch-context objective_info 的 11 键清单逐一对上，P5 命令与 AGENTS.md worktree 验证
命令口径一致。P5 分片不声明的取舍（§4 说明）合理——全量 P5 为权威口径，分片是执行技术。

### 8. 多方案探索 — 自洽

实测 §2：候选 A（选定）/ B（subprocess，否决）/ C（下沉 agate_common，否决），candidate_count: 3。
权衡表 §2.4 五维对照 + 选择理由自洽：候选 B 与 architect dispatch-context 约束 5（实测
P2-dispatch-context-architect.md:33 "不走 subprocess 解析文本"）直接冲突，且 Windows 解释器探测
（DEBT0014 同源）论据成立；候选 C 的分层代价论证成立（检测独立脚本先例：agate-risk-score.py /
check-pruning.py / check-tdd-red.py 均独立，实测 agate_common.py 无业务检测函数）。约束 5 只禁
subprocess 文本解析、未禁"逻辑下沉公共库"，C 属于设计层自主权衡而非约束排除——架构上 C 否决合理
（公共库回归面放大论据与 agate_common 定位一致），无稻草人嫌疑。

### 9. 实现就绪度 — 通过（1 处小缺口，非阻塞）

files_to_read（§6，16 条）覆盖实现所需全部主上下文：gate_p4 挂载点与 import 区（check-gate.py
:870-927 / :25-58 / :930-985）、复用链三点（agate-risk-score.py :41-59 / :86-88 / :202-229）、
count_kf_entries（agate_common.py:1015-1017）、consistency 扫描面（check-protocol-consistency.py
:697-830）、_DRIFT_SCRIPTS（agate-summary.py:42-50）、模板参照、P4/P6 卡落点（:84-148 / :226-229）、
conftest fixtures、先例测试、P1 BDD、落地计划。§5 测试落点与 13 条 BDD 一一对齐：M9
（test_check_maintainability.py G1..G10 ↔ BDD-1..6/11/12/13 + 契约组）、M10
（test_check_gate_p4_maintainability.py G1..G7 ↔ BDD-7/8/9/10 + 回归面）；先例文件
test_check_gate_p5_diff.py / test_md_parse_scan.py / test_check_gate.py / test_agate_risk_score.py
均实测存在；conftest fixtures 实测（git_repo :264-302 / agate_root :305-312 / python_exe :358-365 /
task_dir :374-394）与设计声称行号一致。缺口见非阻塞问题 2（conftest 引用行段不覆盖 task_dir
:374-394）。

### 10. minimal_validation — 通过

§8 声明"纯代码逻辑，无外部系统依赖" + 理由（五点内部依赖逐条列出，均经实测核实：①②为 diff 解析
与 plumbing 行为——本次评审沙箱实测证实；③count_kf_entries :1015-1017 实测；④_norm_rel :86-88
复用链实测；⑤_md_field_get 存在 check-gate.py:230，gate_p4 ①②③ 现用 :879/:885）。`result:
"not_needed"` 符合 P2 卡"纯代码逻辑须声明 + 理由"要求。§8 note 中"唯一假设——挂载点顺序"已实读
gate_p4 全函数体核实，与本次评审独立读码结论一致。

### 11. 影响面梳理（§1）三部分齐全 + 证据客观 — 通过

- **改什么（§1.1）**：M1-M10 逐文件落点到"哪个文件哪个小节/函数/行段"并关联 BDD 编号；抽查全部属实
  （check-gate.py :32-41 import 兜底 / :870-927 gate_p4；check-protocol-consistency.py 锚点表尾
  :751 / callers :771-787 / 豁免表 :791-794 / coverage glob :807-811；agate-summary.py :42-50；
  known-failures-template.md :1-14；P4 卡 :84-110 + :140-148；P6 卡 :226-229）。
- **不改什么（§1.2）**：8 项显式列出且逐项给客观理由（消费方清单、provenance 审计、gate_p5 判定、
  _STAGED_EXCLUDE_RE :174 实测存在、ruff pyproject.toml select 实测含 E7、既有模板本体、协议主流程
  文件）。
- **风险（§1.3）**：R1-R10 每条配缓解；R6/R7/R8 的技术声称经本次实测证实（见第 2/3/4 项），R3 的
  git plumbing 语义经沙箱实测证实（见第 6 项）。

---

## 评审结论

### 架构问题（阻塞级）：

无。11 项核查（dispatch-context 约束 2）全部通过：设计的关键机制声称（gate_p4 结构与挂载点、callers
字面 basename 校验、P3* 键收集、count_kf_entries 正则、_norm_rel 复用链、git plumbing 语义）均经
worktree 读码 + 沙箱实测证实，与落地计划 v3（docs/design-notes/rm-ag0046-maintainability-gate-plan.md
§2/§4.1）的三处偏离（after 取 staged 版而非工作区文件、模板样例 `| # |`、模板加「违规详情」列）均有
实测依据（判定本次 commit 自洽性 / R8 防虚高 / 对应检测器 detail 字段），属有据修正而非漂移。

### 架构问题（非阻塞）：

1. **§1.3 R3 行（P2-design.md:60）表述笔误**："`git show :{path}` 失败（新增文件）→ before=0" 与
   实测不符——新增文件 staged 后 `git show :path` 是**成功**的（staged blob 存在），失败的是
   `git show HEAD:{path}`（无 HEAD 提交/文件不在 HEAD）。§3.1（P2-design.md:121-123）表述正确。
   建议 P4 实现前由 architect 改一行（仅文案勘误，不影响实现方向）；若不改，implementer 以 §3.1
   为准亦可，但 R3 行保留错误表述会误导后来读 R 表的人。
2. **files_to_read 的 conftest 行段缺口**：§6 引用 `agate/tests/conftest.py:264-312`（GitRepo +
   agate_root），但 M10 G5 回归面与 §5.2 平台无关硬约束声明的 `task_dir` fixture 在 :374-394、
   `python_exe` 在 :358-365——引用行段未覆盖，implementer 需自行展开该文件。建议把行段改为
   :264-394（或 :264-312 / :358-394 两段）。影响面：一次额外的文件打开，不阻塞实现。
3. **_load_script 传递加载链未注明**：候选 A 复用链 `_load_script("agate-risk-score")` 会经
   agate-risk-score.py:58-59 模块级语句传递加载 check-pruning 模块（`_check_pruning =
   _load_script("check-pruning")`）——import 副作用面比设计描述多一层（多一次文件读 + 多一个模块
   初始化）。失败模式一致（均 ImportError/文件缺失类，R2 降级先例可兜），非风险新增，但 P4 实现
   check-maintainability.py 的模块头注释宜注明该传递链，避免后来者误判加载面。
4. **门槛 c 无代码实体的回归面确认**：门槛 c 复用既有 ①②③（无新代码），M10 G5 的"逐项等价"断言
   建议在 P3 细化为：violations 非空且门槛 a/b 满足时，确认函数继续走到骨架 WARNING 与 return 0 主路
   （即新步骤不在中途引入提前 return 0/2）——见测试缺口 2。

### 测试缺口：

1. **known-violations.md 真实文件放行的 e2e 型用例**：§5.2 M10 用 task_dir 构造场景，G4（三重满足
   放行）需实际写 known-violations.md 文件并验证 `count_kf_entries` 对其计数 ≥ violations 数——
   建议 P3 明确该用例须含"登记文件存在但正文无 `| N |` 行（0 条）→ exit 1"的反向分支（BDD-8 的
   "文件存在但登记为空"变体），防"有文件就过"回归。BDD-8 判定锚已隐含（登记条目数 < violations 数
   → 1），但 §5.2 G2 场景描述只写"登记 2 条"，未显式含 0 条变体。
2. **新步骤中途 return 的回归断言**：见非阻塞 4——建议 M10 G5 在"无 violations"之外补一组
   "violations 非空 + 三重满足"场景下对 return 路径的断言（落到 return 0，且骨架 WARNING 消息在
   stderr 出现），锁定新步骤与既有步骤的衔接面（对应 check-gate.py:905→:907 的执行流穿过新代码段）。

### 锁定决策：

1. **候选 A 锁定**：check-maintainability.py 为独立检测脚本（模块级 `check_maintainability(task_dir)
   -> dict` 可 import），复用链 = agate_common（run_git/count_kf_entries）+ `_load_script` 复用
   agate-risk-score 的 `_norm_rel`；否决 subprocess CLI 互调（约束 5 + 解析面）与逻辑下沉
   agate_common（分层先例 + 回归面）。
2. **挂载点锁定**：gate_p4 既有第④步（check-gate.py:905）之后、骨架 WARNING（:907）之前追加一步；
   只产生 return 1（门槛 a/b），不新增 return 2；BDD-9/10 由 ①②③ 先于新步骤的顺序天然保证，
   门槛 c 不重复实现。
3. **gate_commands 契约锁定**（P2 固化，P4-P6 不可改）：§4 的 11 键，无 `&&` 链，无 `P3_xxx` 键，
   P5=600s / consistency=120s / 其余 60s，P3 走 `AGATE_TDD_TIMEOUT`；consistency 必须跑 worktree
   自己的 `check-protocol-consistency.py --strict-errors-only`。
4. **consistency 扫描面方案锁定**：登记锚点（SCRIPT_ALIGNMENT_ANCHORS 表尾，keywords 含
   god_file_count / fuzzy_boundary_count，callers=[check-gate.py]）而非豁免；gate_p4 挂载处注释必须
   含字面 `check-maintainability.py`（callers 校验按字面 basename 子串匹配，check-protocol-consistency.py:773/:777）。
5. **模板样例行首锁定 `| # |`**：known-violations-template.md 样例行不命中
   `count_kf_entries` 正则（`^\|\s*[0-9]+\s*\|`），防照抄虚高（对既有 known-failures-template.md
   `| 1 |` 样例的有意改进）。
6. **R3 风险行文案勘误**（非阻塞 1）交主 Agent 回派 architect 一行修改，或由 P4 implementer 按
   §3.1 正确表述实现（二选一，不阻塞 P2 通过）。

### 架构债（DEBT 条目内容，登记由主 Agent 执行）：

依据 dispatch-context 约束 4（DEBT 格式强制），R7 实测揭示的协议缺口属"未来变更更危险"类（三分法
第 2 类），登记内容如下（登记簿 `{AGATE_WORKSPACE}/debt/tech-debt.md`）：

```yaml
id: DEBT0000X
category: protocol
title: gate_commands 的 P3* 前缀键被静默收集为 TDD 测试命令执行（无任何 gate 拦截）
status: open
priority: low
evidence:
  - path: agate/scripts/agate-read-gate-commands.py:60
    note: "key.startswith('P3') and not is_gate_meta_key(key) 收集所有 P3* 非元键为测试命令"
  - path: agate/scripts/agate_common.py:79-87
    note: "is_gate_meta_key 只精确匹配 _formatter/_timeout_seconds 后缀，P3_xxx 不被豁免"
  - path: agate/scripts/agate_common.py:679-693
    note: "is_legal_gate_key 对 P3_xxx 形态返回 True（P3 为合法阶段 + 合法后缀），仅对账 WARNING 不拦截"
  - path: agate-workspace/tasks/TAG0026-maintainability-gate/P2-review.md
    note: "TAG0026 P2 评审实测：P2-design 靠'禁用 P3_xxx 键'约定规避，协议层无机械防护"
impact: 未来任务在 gate_commands 声明 P3_xxx 辅助检测键时，该命令会被 check-tdd-red 在 P3 阶段当作
  测试命令执行（可能误报红灯或产生副作用），且无任何 gate/对账机制拦截（对账 WARNING 亦不触发）
recommendation: 后续协议任务评估：agate-read-gate-commands.py 收集侧收紧（如 P3 仅精确键 + 白名单
  后缀）或 is_gate_meta_key 扩展协议级辅助键约定；并补 read-gate-commands 单测锁定收集行为
closure_criteria:
  - read-gate-commands 对 P3* 键的收集行为有单测锁定，协议文档（P2 卡 gate_commands 节）写明
    P3_xxx 键禁止声明及其原因
source: review
created_at: 2026-08-30
task_id: TAG0026
```

> 说明：`id: DEBT0000X` 为占位——登记时由主 Agent 按登记簿现有最大编号顺延（evidence 必填项已
> 齐备）。本条不影响 TAG0026 本次验收（设计已用"无 P3_xxx 键"契约规避，锁定决策 3）。

---

## 评审依据（关键实测锚点汇总）

- check-gate.py：import 兜底区 :32-41；`_STAGED_EXCLUDE_RE` :174；`_md_field_get` :230；
  gate_p4 :870-927（①:872-877 ②:879-883 ③:885-891 ④:893-905 ⑤:907-925 ⑥:927）；
  gate_p5 count_kf_entries 用法 :977-984；分发映射 :1335-1346
- agate-risk-score.py：`_load_script` :46-54（传递加载 check-pruning :58-59）；`_norm_rel` :86-88
- agate_common.py：`is_gate_meta_key` :79-87；`is_legal_gate_key` :679-693；`run_git` :50；
  `count_kf_entries` :1015-1017（正则 `^\|\s*[0-9]+\s*\|`，沙箱实测 `| # |` 不命中 / `| 1 |` 命中）
- check-protocol-consistency.py：锚点表尾 :749-751；callers 字面 basename 校验 :771-787（:773/:777）；
  GATE_SCRIPT_EXEMPT :791-794；CHECK9-coverage glob :807-811；CHECK 10 扫描面 SCRIPT_REF_SCAN_DIRS
  :857（含 phase-cards，R10 成立）
- agate-read-gate-commands.py：P3* 收集 :60（is_gate_meta_key :79-87 语义实测）
- agate-summary.py：`_DRIFT_SCRIPTS` :42-50（现 7 项）
- conftest.py：git_repo :264-302 / agate_root :305-312 / python_exe :358-365 / task_dir :374-394
- git plumbing 沙箱实测：`git show :path` = staged 版本（成功）；`git show HEAD:path` 对新增文件/
  无 HEAD 仓库失败（exit ≠ 0）；`git rev-parse --verify -q HEAD` 首提 exit 1
- 模板/卡片落点：known-failures-template.md :1-14（样例行 `| 1 |` :14）；P4-implementation.md
  评审节 :84-110 + gate 规则节 :140-148；P6-acceptance.md 自查节 :226-229
- BDD 对照：P1-requirements.md BDD-1..13（:126-219）↔ §5 M9/M10 全覆盖；消费方行号抽查
  （pre-commit-gate.py:349,362 / ci-gate-backstop.py:24,26,154）属实
