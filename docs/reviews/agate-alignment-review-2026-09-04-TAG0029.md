---
review_date: 2026-09-04
reviewer: protocol-alignment-review
change_summary: TAG0029 P4修复gate命令解析器与TDD红灯判定的三个关联缺口——值清洗剥离行内注释加引号闭合校验堵DEBT0027假绿灯、judge补exit2显式分支、P3精确键收紧退役P3_js/P3_html（DEBT0023）加P2卡禁令、R2加fixture目录豁免（RM-AG0056）
files_changed: [agate-workspace/tasks/TAG0029-gate-parser-fix/.state.yaml, agate-workspace/tasks/TAG0029-gate-parser-fix/P4-dispatch-context-implementer-fix1.md, agate-workspace/tasks/TAG0029-gate-parser-fix/P4-dispatch-context-implementer.md, agate-workspace/tasks/TAG0029-gate-parser-fix/P4-dispatch-context-review.md, agate-workspace/tasks/TAG0029-gate-parser-fix/P4-implementation.md, agate-workspace/tasks/TAG0029-gate-parser-fix/P4-review.md, agate/phase-cards/P2-design.md, agate/scripts/agate-read-gate-commands.py, agate/scripts/check-platform-assumptions.py, agate/scripts/check-tdd-red.py, agate/tests/unit/test_check_tdd_red.py]
---

# 协议-脚本对齐审查

## 意图分析

为什么改（1句话）：`agate-read-gate-commands.py` 的值清洗不剥行内注释且残留引号，导致消费方 `bash -c` 报 unterminated quote（exit 2）却被 `check-tdd-red.py` 误判为红灯可推进（DEBT0027 假绿灯，验收真实性风险 high），顺带收紧 `startswith("P3")` 静默收集（DEBT0023）与 R2 fixture 数据面误伤（RM-AG0056）——三处同源指向同一解析器消费链，故强合并单任务。

## 反向传播——应被影响文件（优先级排序）

| # | 文件 | 被影响理由 | 验证结果 |
|---|------|-----------|---------|
| 1 | `agate/assets/formatters/README.md` L89-102 | 多技术栈节仍教 `P3_js` 声明 + "P3 → P3_js 依次执行"，与本次 `P3_js/_html` 显式退役直接矛盾 | 未同步 → A3 MISALIGNED |
| 2 | `agate/scripts/check-tdd-red.py` L32 docstring | 探测链仍写 `gate_commands.P3*`，与精确键语义矛盾（同文件内文档） | 未同步 → A2 MISALIGNED（1行） |
| 3 | `CHANGELOG.md` | `P3_js/_html` 退役是显式声明的语义变更（任务P2 §2.5），需 Unreleased 条目标注 | 无条目 → A5 MISALIGNED |
| 4 | `agate/state-machine.md` L295/303 | 探测链/formatter 键表述 | 已是精确 `P3` 表述，无需同步 |
| 5 | `agate/phase-cards/P3-tdd.md` L68-72 | 探测链/formatter 表述 | 已是精确 `P3` 表述，无需同步 |
| 6 | `agate/scripts/README.md` L44-45/122 | 两脚本工具表行 exit 码/职责描述 | 仍准确（返回约定未变），无需同步 |
| 7 | `check-protocol-consistency.py` 锚点 L617-621/721-724 | TDD/扫描器关键词锚点 | 仍命中，无需同步 → A6 |
| 8 | `orchestrator-template.md` / `dispatch-protocol.md` / `WORKFLOW.md` / 角色文件 / 模板 / `LIMITATIONS.md` | 反向传播常见路径 | 均无 P3* 收集语义副本，无需同步 |
| 9 | `agate-read-p5-commands.py` L30/37、`agate-gate-missing-cmds.py` L24 | 同源 strip 模式（任务P2 N1/N2 显式 out-of-scope） | 文档化不改，有据 → A3a 通过 |
| 10 | `rules/*.yaml`、`agate_common.py` 判据 | N3/N7 零触碰 | sed 实测 intact → A3a 通过 |

DESIGN_GAP 优先核查：任务目录无 P7 文件（任务仍在 P4，`ls` 确认无 `P7*`/`*consistency*`），无 `REVIEWED-ACCEPTED` 裁决记录 → 疑似不一致按正常 MISALIGNED 处理，不适用"已知偏离"标注。

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | ALIGNED（复审 2026-09-04：已修复） |
| A3 | 一致性连锁 + 反向传播 | ALIGNED（复审 2026-09-04：已修复） |
| A4 | 测试覆盖 | ALIGNED（含三份实跑输出） |
| A5 | 下游影响 + 文档传播 | ALIGNED（复审 2026-09-04：已修复） |
| A6 | 锚点表覆盖 | ALIGNED |
| A7 | 设计原则一致性 | ALIGNED |

## 逐项审查

### A1: 文档→脚本对齐

**文档声明1**（任务 `P2-design.md` §3.1，L121-128）：新增 `_clean_value(raw)`——扫描首个未转义 ` #`（`\#` 保留、引号内保留）截断 → 首尾匹配引号剥一层 → 残留未闭合引号（计数为奇）→ stderr 解析错误 + `sys.exit(2)`；L57 命令值 + L66 formatter 值两处共用。

**脚本实现**（`agate-read-gate-commands.py` L49-92，调用点 L103/L112）：`_clean_value` 外层先剥一层（L62）+ 转义跳过（L68-72）+ 引号开闭跟踪（L73-80）+ 仅引号外且前导空白的 ` #` 截断（L81）+ 截断后复剥（L85）+ 奇计数 fail-closed 含 key 名 + `sys.exit(2)`（L86-91）；L103 命令值 / L112 formatter 值两处共用。语义逐字一致。

**文档声明2**（任务 `P2-design.md` §3.2，L130-134）：`elif key == "P3":` 精确键；`suffix = ""`；`fmt_key = "P3_formatter"` 伴随查找不变。

**脚本实现**（同文件 L106-113）：`elif key == "P3":`（L106，fix1 已落实 P4-review I1 简化建议，无冗余条件）+ `suffix = ""`（L107）+ `P3_formatter` 伴随查找（L108-112）。一致；全仓 `startswith("P3")` 零残留（grep 实测 scripts/ 仅剩 L106 精确键）。

**文档声明3**（任务 `P2-design.md` §3.3，L136-141）：新分支置于 exit 0 判定后、既有 A 类分支前；主判 `exit 2` + 运行器统计全零（locale 无关）+ 辅证 5 项（`syntax error`/`unexpected`/`matching`/`寻找匹配`/`未预期`），推测项（`unmatched`/`找不到匹配`/`unterminated`）已删。

**脚本实现**（`check-tdd-red.py` L110-121）：位置在 exit 0 判定（L106-108）之后、既有 A 类分支（L123，要求 exit 1）之前，与 `exit >= 120` 分支（L165）三域不交；主判 exit 2 + 五零统计 + 辅证正则恰为关闭版 5 项。一致。

**文档声明4**（任务 `P2-design.md` §3.4，L143-149）：`_FIXTURE_EXEMPT_DIRS` 声明式前缀集合 + 路径判定；`_scan_file` 内 R2 跳过，其余规则照常；R2 正则本体不动。

**脚本实现**（`check-platform-assumptions.py` L46-65 + L101/L108-109）：豁免集（L46）+ 连续路径段包含判定（L62-64，posix 归一化 + 反斜杠兼容，禁 startswith）+ `if exempt == "r2" and fixture_exempt: continue`（L108）仅跳 R2；R2 正则（L39）不动。一致。注：设计写" `_scan_target` 内判定"，实现落在 `_scan_file` 入口（L101）——`_scan_file` 即 `_scan_target` 的逐文件下钻点，粒度等价，无语义差。

**文档声明5**（协议卡 `P2-design.md` L182-194）：`P3_xxx` 禁止声明子节（白名单 `_formatter`/`_timeout_seconds` + `_e2e` + 退役 `_js`/`_html`）+ DEBT0025 上线流程段；只加节既有不动。

**脚本/实现对应**：M2 精确键 + S1 测试同步（见 A4）与禁令互为表里；任务 P2 §2.5（L101-105）退役声明与卡片禁令清单一致。

**结论**：ALIGNED

### A2: 脚本→文档对齐

**脚本逻辑**（`check-tdd-red.py` L32）：模块 docstring 探测链仍写"`gate_commands.P3*（P2-design.md 声明）`"。

**文档侧**：精确键语义下解析器只收集裸 `P3`（L106），`P3*` 通配表述已失真——读者按此 docstring 会误以为 `P3_xxx` 仍被探测。权威规则源（`state-machine.md` L303、P3 卡 L70）均已是精确 `gate_commands.P3` 表述，同文件 docstring 反而滞后，属脚本内文档未同步。

**结论**：ALIGNED（复审 2026-09-04：L32 已为精确 `gate_commands.P3` 表述，`P3*` 通配零残留）
**复审证据**：grep `P3\*|gate_commands\.P3` → L19/L32/L197/L198 均为精确 `P3` 表述，无 `P3*`。
**差异**（上轮）：同文件 docstring 通配符 `P3*` 与实现精确键矛盾。
**建议**：L32 改为 `gate_commands.P3`（1行，与 state-machine L303 口径对齐）；与 A3 的 formatters README 系同一退役传播根因的两处落点，各修各的。

### A3: 一致性连锁 + 反向传播

A3a 连锁（已知的衍生改动）：

- N3/N7 零触碰——`is_gate_meta_key`（sed 实测：仅精确匹配 `_formatter`/`_timeout_seconds`）与 `is_legal_gate_key`（`P{阶段}` + 合法后缀 → `P3_xxx` 仍合法 True，仅对账 WARNING）均 intact，无 `rules/*.yaml` 同步义务。ALIGNED。
- N1/N2 out-of-scope——`agate-read-p5-commands.py` L30/37、`agate-gate-missing-cmds.py` L24 同源 strip 模式本次不改，任务 P1 §4（#3/#4）+ P2 §1.2（N1/N2）已书面论证（P5 不在假绿灯消费链；missing-cmds 只取首 token 不经 `bash -c`），有据保留。ALIGNED。
- S2/S3 存量——P4-review §3 定论保留（S2 仅断言 exit 0 + classic red-light，修后仍成立；S3 测公共判据非收集侧），S1 已同步（见 A4）。ALIGNED。

A3b 反向传播（主动推断，见上表 #1/#4-#8）：

**应被影响但未同步**（`agate/assets/formatters/README.md` L89-102）：
> 原文 L91-102："项目包含多种语言时，声明多个 gate 阶段对" + `P3_js: "npx vitest run"` / `P3_js_formatter: "vitest.sh"` 示例 + "主 Agent 按阶段前缀依次执行 `P3` → `P3_js`，所有阶段通过后才进入 P4。"
修后 `P3_js` 声明即被解析器丢弃（L106 精确键）且协议卡 L188-189 明令"历史 `_js`/`_html`已退役，不得复用为检测键"——README 仍把退役形态当推荐写法教，属可执行的错误指引（读者照做则命令静默丢失）。

其余反向传播点逐一验证干净：state-machine 探测链（L303 精确 `P3`）、P3 卡（L70 精确 `P3`）、scripts README 工具表（返回约定未变仍准确）、WORKFLOW Pre-commit 总览（无触发行为变更）、LIMITATIONS（无相关副本）、dispatch-protocol（无 P3 收集语义副本）。

**结论**：ALIGNED（复审 2026-09-04：多技术栈节 L89-100 已改写为单栈精确 `P3` + 退役说明 + 登记注记，无 `P3_js` 推荐示例）
**复审证据**：L91 "历史 `P3_js` / `P3_html` 形态已退役"；L100 "未来多栈并行需先经协议修订登记收集后缀"；示例块仅 `P3`/`P3_formatter`。
**差异**（上轮）：formatters README 多技术栈节与 `P3_js/_html` 退役矛盾。
**建议**：二选一（看哪个是对的——退役是对的，已由任务P2 §2.5 显式裁决）：(a) README 该节改写为"单栈精确 `P3` + 未来多栈走协议修订登记收集后缀"并删 `P3_js` 示例；(b) 若多栈示例必须保留，须显注"需协议修订先登记收集后缀，否则解析器丢弃"。推荐 (a)。

### A4: 测试覆盖

BDD→用例映射（9 条全覆盖，P3-test-cases A/B 批）：BDD-1/2 → `test_tag0029_gate_parser_fix_a.py`（纯命令 + `bash -c` exit≠2 / 非零退出 + stderr + 无残渣）；BDD-3 → 双 locale（中文 `寻找匹配`/`未预期` + 英文 `syntax error`/`unexpected`/`matching`）→ exit 1；BDD-4/5 → P3_xxx 不收集 / 裸 P3 + 元键豁免；BDD-6/9 → 卡片禁令文本 + scanner 三 key 存在性；BDD-7/8 → fixture 内 0 命中 / 目录外仍命中。边界：转义 `\#` 保留、引号内 ` #` 保留、未闭合 fail-closed、exit2+空输出回落（I3 记录为实际不可达）、R2-only 豁免（R1/R3-R5 照常）均有对应断言或评审记录。

S1 存量同步已落地：`test_check_tdd_red.py` L588-611，docstring 加注 `[TAG0029: P3_html 已退役]`（L591），断言由"被收集"改为 `"npx vitest run" not in result.output`（L610），`P3` + `project_module` 断言保留。

最近一次实跑输出（本审查员在 worktree 实跑，非引用自报）：

- 新批：`10 passed in 0.40s`（`test_tag0029_gate_parser_fix_a/b.py`，job bash-44，exit 0）
- 回归单文件：`45 passed in 5.37s`（`test_check_tdd_red.py` 全文件，job bash-45，exit 0）
- 全量：`1444 passed, 2 skipped in 33.99s`（`pytest agate/tests/ -n auto`，job bash-46，exit 0；用例数 1446 与 count-tests 口径一致：1444 + 2 skipped）
- consistency：`--strict-errors-only` exit 0，0 ERROR / 329 WARNING（WARNING 均为历史叙事文件引用类，非本变更引入）

**结论**：ALIGNED

### A5: 下游影响 + 文档传播

破坏性变更判定：`P3_js`/`P3_html` 历史多栈形态退役是任务 P2 §2.5（L101-105）**显式声明的语义变更**（"收紧为精确键是语义变更，不是纯收紧"）。实际 blast 半径小（§2.5 存量证据：真实任务 P2 从未声明 `P3_xxx` 检测键；仅测试与文档示例涉及），但"影响小" ≠ "可不标注"。

- `CHANGELOG.md`：本次 diff 无 CHANGELOG 条目（`git show HEAD --stat` grep 确认缺席；文件头最新节仍为 [0.67.0] 2026-09-03）。协议语义变更 + 未标注 → 下游影响不完整。MISALIGNED。
- 文档传播：除 A3 的 formatters README 外，orchestrator-template / WORKFLOW / dispatch-protocol / role-system / 角色文件 / 模板 / LIMITATIONS 均无 P3* 收集语义副本，无需同步；`UPGRADING.md` 无需动（非版本发布任务，CHANGELOG Unreleased 登记即足）。
- 消费链回归：解析器是 P2/P3/P5 共享件——全量 1444 passed + 存量 gate_commands 块无行内注释现状（任务P2 R2）佐证 fail-closed 不误伤存量。

**结论**：ALIGNED（复审 2026-09-04：`[Unreleased]` L13-18 含 TAG0029 条目——退役 + fail-closed + exit2 分支 + R2 豁免 + 无存量用法注记）
**差异**（上轮）：语义变更缺 CHANGELOG 标注。
**建议**：CHANGELOG `[Unreleased]` 补条目（`P3_js`/`P3_html` 退役 + 精确键 + fail-closed 值清洗 + fixture 豁免，注明真实任务无存量用法、测试已同步 S1）。

### A6: 锚点表覆盖

- TDD 锚点（`check-protocol-consistency.py` L617-621）："TDD 红灯检查" → `check-tdd-red.py`，关键词 `["formatter", "pytest"]`——脚本 docstring 与 formatter 机制均 intact，仍命中。本次新增 exit 2 分支是**判定分支内部扩展**，无新增协议规则需要新锚点（返回约定 0/1/2/3 未变，state-machine L291/L297-301 口径仍成立）。
- 扫描器锚点（L721-724）：关键词 `["平台假设", "R1", "R2"]`——docstring 与规则号均 intact，仍命中。 fixture 豁免是**数据面豁免点新增**，不改变 R1-R5 规则面，CHECK 9（关键词存在性）覆盖充分；语义一致性已由 A1 人工核对。
- 触发行为：本次未改任何脚本的 pre-commit 触发行为（WORKFLOW「Pre-commit 检查总览」唯一权威表无需动；`dispatch-protocol.md`/`state-machine.md` 无检查清单副本可回归）。

**结论**：ALIGNED

### A7: 设计原则一致性

逐条检查相关 ADR（`agate/adr.md`）：

- ADR-002 可判定性（L41-66）：gate 由脚本 exit code 决定。本变更**加强**该原则——值清洗 fail-closed（`sys.exit(2)` 替代带残渣输出，消灭"测试没跑却放行"的不可判定路径）+ judge exit 2 显式分支（exit 2 输入从末尾 exit 0 改判 exit 1，判定更精确）。ALIGNED。
- ADR-003 最小约定不绑定技术栈（L69-93）：技术栈命令经 `gate_commands` 注入。本变更保持 formatter 机制与技术栈无关性（judge 新分支只看 exit 码 + 零统计 + 通用文案，不绑定 pytest/vitest）；精确键收紧的是**键收集语义**，不是技术栈绑定。ALIGNED。
- ADR-004 安全网分层（hook 兜底）：本次语义修正走 TDD 先红后绿（H7）+ P5 全量回归 + consistency + count-tests，与分层思想一致。ALIGNED。
- 其余 ADR（001/005/006/007/008/009/010/011）与本次改动无实质关联。
- 未记录的新架构决策：无——"退役多栈形态走协议修订登记"已记入任务 P2 §2.5 + 协议卡禁令，无需新 ADR。

**结论**：ALIGNED（A7 无 MISALIGNED 档）

## 闭环要求（主 Agent 动作）

| 项 | 动作 |
|---|------|
| A2 | `check-tdd-red.py` L32：`gate_commands.P3*` → `gate_commands.P3`（1行） |
| A3 | `assets/formatters/README.md` L89-102：按建议 (a)/(b) 改写多技术栈节 |
| A5 | `CHANGELOG.md` `[Unreleased]` 补语义变更条目 |
| A1/A4/A6/A7 | 通过，无动作（沿用上轮 ALIGNED） |
| A2/A3/A5 | 复审 2026-09-04 已修复 → 全 ALIGNED，可 commit |

## 复审节（2026-09-04 SELF-GATE 重审轮）

- A2：`check-tdd-red.py` L32 已为精确 `gate_commands.P3`；grep 全文件 4 命中（L19/L32/L197/L198）均为精确 `P3`，无 `P3*` 通配残留 → ALIGNED。
- A3：formatters README L89-100 多技术栈节已改写——单栈精确 `P3` 示例 + "历史 `P3_js`/`P3_html` 已退役" + "未来多栈需协议修订登记后缀"，无 `P3_js` 推荐示例 → ALIGNED。
- A5：`CHANGELOG.md` `[Unreleased]` L13-18 含 TAG0029 条目（退役 + fail-closed + exit2 分支 + R2 豁免 + 无存量用法注记）→ ALIGNED。
- A1/A4/A6/A7 沿用上轮 ALIGNED，未重审。

## 人工验收清单

- [x] Write 前已检查目标路径：成果文件此前不存在（`ls` 确认 `没有那个文件或目录`），直接写入，无覆盖冲突；留痕文件按规则先 `rm -f` 后追加
- [x] 审查报告含 A1-A7 七项，每项有结论
- [x] MISALIGNED 项（A2/A3/A5）有差异描述 + 建议方向
- [x] NEEDS_HUMAN_REVIEW：0 条，无需 `[HUMAN_CONFIRMED]` 配对
- [x] 成果文件落盘到 `docs/reviews/agate-alignment-review-2026-09-04-TAG0029.md`（worktree 内相对路径；硬约束路径）
