---
phase: P4
task_id: TAG0007
type: review
parent: P4-implementation.md
trace_id: TAG0007-P4-review-20260820
status: approved
created: 2026-08-20
agent: review
---

# P4 评审：TAG0007 项目结构管理机制（骨架 + code-map）

评审对象：`P4-implementation.md` 记录的 4 个并行批次（skeleton-docs / code-map-docs /
gate-script-both / dogfood-bootstrap）。按 dispatch-context 5 条约束逐一核查（协议脚本/文档
改动场景，不套用 Web 应用 checklist）。

## 约束 1 核查：check-gate.py 三处新增分支正确性

**gate_p2（`agate/scripts/check-gate.py:637-646`）— project_phase: bootstrap 判定**

- `project_phase == "bootstrap"` 分支：缺 `P2-skeleton.md` 或缺 `## 骨架声明` 标题 → `return 1`，
  stderr 含 `"P2-skeleton.md"`。存在且含标题 → 不拦截，落到原有 `return 2`。核实无误。
- 字段缺失/`established`（含显式声明）：完全不进入该 if 分支，不产生任何 `"P2-skeleton.md"`
  相关输出。用 `_frontmatter_field` 读取，字段不存在返回 `""`，`"" == "bootstrap"` 为
  `False`，与既有 `design_trivial`/`follows_existing_pattern` 可选字段回退模式同款写法。
  回归安全确认：`timeout 60s python3 -m pytest agate/tests/unit/test_check_gate.py -k
  "bdd_1_ or bdd_3_"` 全部通过（`test_bdd_1_bootstrap_missing_skeleton_exit_1` /
  `test_bdd_1_bootstrap_with_skeleton_title_exit_2` /
  `test_bdd_3_field_missing_no_regression_exit_2` /
  `test_bdd_3_established_explicit_no_regression_exit_2` 均 PASSED）。

**gate_p7（`agate/scripts/check-gate.py:937-980`）— CODE_MAP 两层 pairing 校验**

逐行核对字段对应关系（P2-design.md §2.3/§5 权威规格 + dispatch-context 明确点名的 P2 review
第一轮曾打回的错误点）：

- 内部一致性层（L958）：`cm_reviewed < cm_count`，即
  `code_map_reviewed_count < code_map_new_files_count` → `return 1`。**与规格一致**。
- 转抄核对层（L974）：`p4_code_map_actual_count > cm_count`，`cm_count` 绑定的是
  `code_map_new_files_count`（**不是** `code_map_reviewed_count`，见 L952-953 变量赋值）→
  `return 1`。**与规格一致，未写反**。
- 判定：两层字段对应关系正确，未重复 P2 review 第一轮的错误。测试
  `test_bdd_8_9_gate_p7_transcription_mismatch_exit_1`（P7 声明
  `code_map_new_files_count: 2` / `code_map_reviewed_count: 2` 刻意相等以隔离内部一致性层，
  P4 实际标记 3 条 > 2 触发转抄层）专门覆盖"字段写反"这一失败模式，隔离设计正确，PASSED。

**gate_p4（`agate/scripts/check-gate.py:698-717`）— WARNING 分支**

- 不阻断确认：WARNING 分支（L711-716）执行后无 `return`，直接落到函数末尾 `return 0`（L718），
  exit code 恒为 0，不阻断。
- `change_type: refactor` 不影响判定（BDD-10）确认：`gate_p4` 函数体全文未出现
  `change_type`/`_md_field_get(... "change_type" ...)` 任何引用，逻辑上不可能读取该字段。
  `test_bdd_10_gate_p4_refactor_not_exempt_warning` PASSED（refactor 任务同样触发 WARNING）。
- `gate_p7` 同理，CODE_MAP 两层校验代码段（L937-980）全文未引用 `change_type`。
  `test_bdd_10_gate_p7_refactor_not_exempt_pairing_check` PASSED。

**TOCTOU/竞态角度**：新增三处分支读取的 `P2-skeleton.md`/`P4-implementation.md`/
`P7-consistency.md` 均通过 `_read_text`/`_frontmatter_field` 直接读工作区文件（非
`git show :file` 读暂存区快照），与既有 `p1_file`/`p2_review`/`p6_file`/`p7_file` 等所有既有
判定分支的读取方式完全一致——本次改动沿用既有假设，未引入新的、比现状更严重的不一致。暂存区
状态只在 `gate_p4` 的 `has_code_file` 判定处用到（`git diff --cached --name-only`，既有逻辑，
未改动）。不构成本次改动引入的新风险。

**状态枚举完整性（防御性检查）**：`gate_p2` 的判定是 `if project_phase == "bootstrap":`——
严格等值比较，非 `if/elif` 穷举分支。任何未来新增的第三个枚举值（非 `"bootstrap"`）都会自然
落入"不检查"分支，与当前 `established` 走向完全一致，不会被静默误判为 `bootstrap`。这是安全
的默认写法（未知值 → 保守跳过，不会误拦或误判），无需修改。

## 约束 2 核查：DESIGN_GAP 逐条判定

见下方「DESIGN_GAP 逐条判定」独立小节（dispatch-context 硬性要求给出明确判定，不能只是"已阅读"）。

## 约束 3 核查：回归验证

已复核主 Agent 提供的结果为可信证据，未发现造假迹象；额外自行抽查以下命令（均可复现）：

```
timeout 60s python3 -m pytest agate/tests/unit/test_check_gate.py -k "bdd_1_ or bdd_3_ or bdd_4_7 or bdd_8_9 or bdd_10_" -q
→ 15 passed, 144 deselected
```

12 个新增测试 + 3 个既有同前缀测试（`test_bdd_3_p6_refactor_with_regression_evidence_exit_2`
等）全部通过，无回归。主 Agent 提供的全量结果（1028 passed, 2 skipped, 0 failed；
consistency 0 ERROR；shellcheck 0 error）予以采信，不重跑全量（objective_info 已声明的证据
链完整，抽查结果与之一致）。

## 约束 4 核查：跨批次一致性

grep 核对以下字段名/标题在文档批次与代码批次间的逐字匹配：

| 字符串 | phase-cards/execution-roles 文档 | check-gate.py 代码 | 一致 |
|---|---|---|---|
| `## 新增文件核对表` | `P4-implementation.md:66` | `check-gate.py:713`（`if "## 新增文件核对表" not in ...`） | 是 |
| `[CODE_MAP_UPDATED]` | `P4-implementation.md:75/79` | `check-gate.py:971` | 是 |
| `[CODE_MAP_EXEMPT` | `P4-implementation.md:75/80` | `check-gate.py:972` | 是 |
| `code_map_new_files_count` | `P7-consistency.md:55/75` | `check-gate.py:952/960/977` | 是 |
| `code_map_reviewed_count` | `P7-consistency.md:55/76` | `check-gate.py:953/960` | 是 |
| `[CODE_MAP_SYNC:]`/`[CODE_MAP_DRIFT:]` | `P7-consistency.md:35`、`consistency-reviewer.md:52` | （P7 人工核对标记，非 gate 判定字符串，正确地不在 check-gate.py 中出现） | 是（各归属正确层） |

未发现"大致相似但字面不同"的漂移。

## ADR-003 合规复核（约束 5）

`assets/templates/skeleton-template.md` 全文已读：无 `src/components`/`src/include`/
`src/hooks`/`src/pages` 等硬编码技术栈目录名，五类候选目录以抽象类别标签
（源码类/测试类/文档类/构建类/部署类候选目录）表达，具体目录名留空白由项目侧按技术栈填写，
含参数化关键词「候选目录」「技术栈」。合规。

`assets/templates/code-map-template.md` 五个必填标题（模块/层/依赖方向/关键文件/约定）齐全，
占位声明形式，不预设任何语言/框架。合规。

---

## 架构/正确性问题（阻塞级）

无。

## 架构/正确性问题（非阻塞）

- DEBT0016（已登记，见下）：`gate_p4` 的 `{AGATE_WORKSPACE}/agents/CODE-MAP.md` 路径解析用
  本地"task_dir 向上两级"算术，未复用 `agate_common.resolve_workspace` 权威函数（详见下方
  DESIGN_GAP 第 2 条判定）。

- DESIGN_GAP 1 揭示的边界差异（非阻塞，供后续参考，不要求本轮修复）：`_frontmatter_field` 与
  `_md_field_get`（针对 `NO_FALLBACK_INT_FIELDS` 类字段，如已有的
  `design_gap_count`/`design_gap_reviewed_count`，本次新增的
  `code_map_new_files_count`/`code_map_reviewed_count` 若未来注册进该 allowlist 也适用同一
  差异）在"frontmatter 块内其它字段存在 YAML 语法错误"场景下行为不等价：`_md_field_get` 要求
  整个 frontmatter 块可被 `yaml.safe_load` 完整解析为 dict 才生效，块内任意位置的 YAML 语法
  错误会导致该函数静默返回空字符串（等同"字段不存在"，pairing 检查被跳过而不自知）；
  `_frontmatter_field` 是逐行前缀字符串匹配，不要求整块可解析，能在块内他处存在 YAML 语法
  错误时仍正确取到目标字段值。本任务 P2-design.md 自身在 TDD 阶段就真实撞过这类 YAML 转义
  bug（第 276 行 `note:` 字段内嵌未转义 ASCII 双引号导致 `check-protocol-consistency.py`
  一度失败），说明这不是纸面假设风险。**分歧方向本身是 `_frontmatter_field` 更稳健**（不会
  因无关字段的 YAML 错误而漏检 CODE_MAP pairing），不构成需要立即修复的缺陷，但 DESIGN_GAP 1
  原文声称"行为等价"这一表述不够精确，建议后续若真的切回 `_md_field_get`（DESIGN_GAP 1 末尾
  提议的路径）时，需在切换前补充这一边界场景的回归测试，否则会静默丢失当前 `_frontmatter_field`
  实现具备的健壮性。"字段存在但值为空字符串"这一具体边界情形，两者行为一致（均判定同缺失，
  不构成实质差异）。

## DESIGN_GAP 逐条判定

**第 1 条**（`_md_field_get` 因 `KNOWN_OPS`/`NO_FALLBACK_INT_FIELDS` 未注册新字段会静默失败，
改用本地 `_frontmatter_field` 替代）：

判定：**接受该实现选择，行为在本任务测试覆盖的场景下等价，但补充一个未被 implementer 声明的
边界差异点**（见上方「架构/正确性问题（非阻塞）」小节的详细分析）——`_md_field_get` 依赖整个
frontmatter 块可被 `yaml.safe_load` 完整解析，`_frontmatter_field` 是逐行前缀匹配不要求整块
可解析；在"块内其它字段 YAML 语法错误"场景下两者不等价，且分歧方向对当前实现有利（更稳健，
不会因无关字段错误而漏检）。"字段存在但值为空串"场景下两者行为确实一致（均视为缺失），
DESIGN_GAP 1 原文对这一具体边界的等价性判断没错，只是"行为等价"的整体表述范围过宽，未覆盖
块级解析失败这一更极端的边界。非阻塞，不要求本轮修复，已在本评审文件留痕供后续参考。

**第 2 条**（`{AGATE_WORKSPACE}/agents/CODE-MAP.md` 路径用"task_dir 向上两级"简化推导，
未用 `resolve_workspace`）：

判定：**非阻塞，登记为技术债（DEBT0016），approve 通过**。理由：

1. 已读 `agate_common.py:464-493` `resolve_workspace` 源码 + `pre-commit-gate.py:251-252`
   `task_dir` 实际构造逻辑（`task_dir = os.path.join(tasks_dir, task_id) if state_dir ==
   repo_root else state_dir`），确认在项目当前所有实际调用路径下，`task_dir` 恒等于
   `{workspace}/tasks/{task_id}` 两级嵌套结构——这一不变式由 `resolve_workspace` 自身两个分支
   的构造方式保证（`.agate.env` 分支：`tasks_dir = workspace/tasks`；`AGATE_TASKS_DIR` 分支：
   `workspace = dirname(tasks_dir)`，两者都使 `workspace` 恰好是 `task_dir` 的祖父目录）。因此
   即使项目通过 `.agate.env` 自定义了工作区位置，implementer 的"向上两级"推导在数学上与
   `resolve_workspace` 的输出**代数等价**，dispatch-context 原文"会得出错误路径"这一结论在
   标准场景下不成立。
2. 已识别的唯一真实分歧点：`resolve_workspace` 内部 `_resolve_abs` 用 `Path(...).resolve()`
   （解析符号链接、归一化），而 `check-gate.py` 本地推导用 `os.path.abspath`（不解析符号
   链接）。若 workspace/task_dir 路径链中存在符号链接，两者产出的字符串可能不同（尽管多数
   情况下 `os.path.isfile` 在打开时仍会正确follow符号链接，字符串层面的差异通常不影响文件
   存在性判定的最终正确性，除非符号链接结构导致"向上两级"在字符串层面走出了错误的相对关系）。
   本 worktree 场景中 `~/.agate` 软链接命中的是 `AGATE_ROOT`（协议本体路径），不是
   `AGATE_WORKSPACE`（工作区路径），未直接命中这条风险路径。
3. 影响范围严格限于 `gate_p4` 一处 **WARNING** 分支（骨架/CODE-MAP 机制已采用但缺「新增文件
   核对表」标题时的提醒），不阻断任何 commit，不影响任何 exit code 判定，最坏后果是"该提醒
   一次没有触发"——不是 BLOCKER 级数据安全问题，也不会导致"骨架/CODE-MAP 机制被错误判定为
   已采用从而误拦截"（误判方向只会是"少提醒"，不会"多阻断"）。
4. 依 review.md 门槛（区分"逻辑变更/架构决策"应列选项供用户决定 vs 可直接处理的技术债）：
   本问题属于"实现选了一条局部有效但未复用权威函数"的技术债性质，不是需要人工在多个架构选项
   间抉择的问题——已给出唯一推荐方向（改为调用 `resolve_workspace`），符合登记 DEBT 而非
   rejected 的处理路径。

已登记 `DEBT0016` 至 `{AGATE_WORKSPACE}/debt/tech-debt.md`（`category: technical`，
`priority: low`，`evidence` 引用 `check-gate.py:702-710` + `agate_common.py:464-493` +
`pre-commit-gate.py:251-252`，`source: review`，`task_id: TAG0007`），
`python3 agate/scripts/check-debt.py {AGATE_WORKSPACE}/debt/tech-debt.md` exit 0（schema
校验通过）。

## 回归验证确认

主 Agent 提供结果（全量 pytest 1028 passed/2 skipped/0 failed；consistency 0 ERROR；
shellcheck 0 error）予以采信。本评审额外抽查 12 个新增 + 3 个同前缀既有测试
（`test_check_gate.py -k "bdd_1_ or bdd_3_ or bdd_4_7 or bdd_8_9 or bdd_10_"`）：15 passed，
结果与 P4-implementation.md 自查记录一致，无造假迹象。

## 跨批次一致性确认

见上方「约束 4 核查」表格：`## 新增文件核对表`、`[CODE_MAP_UPDATED]`、`[CODE_MAP_EXEMPT`、
`code_map_new_files_count`、`code_map_reviewed_count` 五组字符串在文档批次
（`P4-implementation.md`/`P7-consistency.md`/`consistency-reviewer.md`）与代码批次
（`check-gate.py`）间逐字匹配，无漂移。

## 结论

**approved**

理由：check-gate.py 三处新增分支（gate_p2/gate_p4/gate_p7）逻辑正确，字段对应关系与
P2-design.md §2.3/§5 权威规格及 P3-test-cases.md 12 个测试断言完全一致，未重复 P2 review
第一轮曾打回的 pairing 字段写反错误；WARNING 分支确认不阻断、`change_type: refactor` 确认不
影响判定；跨批次字段名/标题字符串逐字一致；ADR-003 合规（骨架模板无硬编码技术栈目录名）；
2 条 DESIGN_GAP 均已给出明确判定——第 1 条接受实现选择并补充一处此前未声明的边界差异说明
（非阻塞，已留痕）；第 2 条判定为非阻塞技术债，已登记 DEBT0016。无 CRITICAL/BLOCKER 级问题。
