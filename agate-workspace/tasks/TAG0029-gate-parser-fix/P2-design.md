---
phase: P2
task_id: TAG0029
type: design
parent: P1-requirements.md
trace_id: TAG0029-P2-20260904
status: draft
created: 2026-09-04
agent: architect
candidate_count: 3
packages: [gate-parser, tdd-judge, platform-scanner, protocol-docs]
domains: [backend]
ui_affected: false
dispatch_plan: {mode: single}
---

# P2 设计 — TAG0029 gate 命令解析器修复批

> 阶段：P2（方案设计）· 角色：architect · 日期：2026-09-04
> 验收锚：P1-requirements.md 9 条 BDD（BDD-1~BDD-9）· 输入：P0-brief 范围边界 + 改造对象 3 脚本精读
> [PROD_NOT_TOUCHED] 本阶段只做只读查证与方案设计，未改动任何实现代码。

## 1. 影响面梳理（候选方案之前）

> 客观证据：dispatch-context objective_info 主 Agent 实测清单（直接引用，不重扫）+ 本轮精读 3 脚本全文
> + `agate_common.py` 相关函数 + TAG0028 P2-design §4 gate 范例 + `dispatch.yaml` 语法声明 + S-4 校验逻辑。

### 1.1 改什么（Modify）

| # | 文件 / 函数落点 | 改动内容 | 关联 BDD |
|---|----------------|---------|---------|
| M1 | `agate/scripts/agate-read-gate-commands.py` L57（命令值清洗）+ L66（formatter 值清洗，同模式同污染） | 新增值清洗函数：剥离首个未转义 ` #` 行内注释 + 引号闭合校验；失败 fail-closed（exit 非 0 + stderr，不产出残渣） | BDD-1 / BDD-2 |
| M2 | 同文件 L60–67（收集侧 `key.startswith("P3")`） | 收紧为精确键 `key == "P3"`；formatter 伴随查找（`P3_formatter`）语义不变 | BDD-4 / BDD-5 |
| M3 | `agate/scripts/check-tdd-red.py` `judge_result` L87–157 | 新增 exit 2 显式分支（命令串本身语法错误 → exit 1 A 类），不再落末尾 L156–157 red-light exit 0 | BDD-3 |
| M4 | `agate/scripts/check-platform-assumptions.py` R2 L39 + 豁免函数 L46–53 / 扫描循环 L76–93 | 新增 fixture 目录声明绑定豁免（路径前缀判定）；R2 正则本体不动 | BDD-7 / BDD-8 |
| M5 | `agate/phase-cards/P2-design.md` gate_commands 节（现 L125–180） | 新增 P3_xxx 禁止声明及其原因 + 新增 CHECK / 扫描面上线流程（DEBT0025 先全量扫描存量）落点 | BDD-6 / BDD-9（文档面） |
| M6 | `agate/tests/` 新增 pytest（P3 承接，设计声明红灯形态） | 行内注释解析单测 + judge exit 2 单测（先红后绿，H7）+ P3 收集行为单测 + R2 豁免边界单测 | BDD-1~5 / BDD-7 / BDD-8 |

### 1.2 不改什么（Not Modify）

| # | 看起来该改但决定不改 | 理由 |
|---|---------------------|------|
| N1 | `agate-read-p5-commands.py` L30 / L37（P5 值清洗同模式） | P1 同类扫描 #3 结论：P0-brief scope 锁定三缺口，P5 路径不在假绿灯消费链（check-tdd-red 只消费 gate-parser 输出）；同源不同严重度，候选后续任务 |
| N2 | `agate-gate-missing-cmds.py` L24（首 token 检测） | P1 #4：只取首 token 做缺失检测，不经 `bash -c` 执行，注释尾巴不构成 unterminated quote；回归验证覆盖即可 |
| N3 | `agate_common.is_gate_meta_key` L79–87 公共判据 | 选定方案（§2.4 A）收紧落在解析器本地，不动公共判据 → S-4 对账零触碰、5 个消费方语义零漂移；动它（候选 B）须同步 `rules/dispatch.yaml` + 全消费方回归，爆炸半径大 |
| N4 | `agate_common.parse_gate_commands_block` L784–795 + `is_legal_gate_key` L682–693 | M2 单点语义（块解析）保持；本次动的是值清洗（解析器本地），不是块解析（dispatch 指引强制区分） |
| N5 | R2 本体判定逻辑 + cmdstream 检测引擎 + `check-gate.py` 返回约定（0/1/2/3） | P0 out-of-scope 三条：R2 只加数据面豁免；cmdstream 引擎 RM-AG0055 已交付不动；judge 新分支只改变 exit 2 输入的归属，不改变返回约定含义 |
| N6 | TAG0011 bdd-8 断言意图 | 只恢复 fixture 真实日志形态 + 目录豁免，不改测试语义（P0 out-of-scope 第四条） |
| N7 | `rules/*.yaml`（`dispatch.yaml` gate_commands_syntax 等） | N3 的推论：不动公共判据 → YAML 无需同步；S-4 只做回归验证 |

### 1.3 风险在哪（Risk）

| # | 风险 | 缓解 |
|---|------|------|
| R1 | S-4 YAML 对账漂移：若误动 `is_gate_meta_key` 判据而不同步 `rules/dispatch.yaml`，consistency 红 | 选定方案不动公共判据（N3）；P5_consistency 独立 key 回归（§4） |
| R2 | 消费链回归：解析器是 P2 / P3 / P5 gate 共享件，值清洗 fail-closed 可能让存量带注释命令块变红 | P5 全量 pytest 三片合跑 + consistency + count-tests 独立 key 全回归（§4）；存量 gate_commands 块现状无行内注释（TAG0028 fix2 已改独立行，证据见 §2.1） |
| R3 | fixture 豁免被真代码借用 | 豁免绑定目录声明（路径前缀匹配），禁"含 fixture 字样就跳过"宽匹配；单测锁边界：目录内数据面豁免 + 目录外同类文本仍命中（BDD-8） |
| R4 | 常驻面存量命中：扫描器进 P3 / P4 常驻后存量命中阻断开发 | DEBT0025 流程：P4 落地前先全量扫描存量，有命中先登记清单再启（H6）；本任务 Phase 3 同步执行 |
| R5 | 收紧语义变更：`P3_js` / `P3_html` 历史多栈形态失效 | §2.3 专项论证 + 白名单后缀清单 + 未来扩展路径（显式声明取舍，非静默破坏） |
| R6 | 自身 P3 bootstrap：旧解析器会把本任务 P2-design 的 `P3_scanner` 当测试命令收集，污染 TDD 判定 | P3 gate 用 `TEST_RUNNER` 环境变量覆盖跑裸 P3 命令（最高优先级，绕过文件收集）；修后文件收集即安全（仅裸 P3 被收集），见 §4 注记 |

## 2. 候选方案

### 2.1 各改动面备选方向（先发散，再组合）

| 改动面 | 方向 a | 方向 b | 方向 c |
|-------|-------|-------|-------|
| 值清洗（BDD-1/2） | a1 解析器内剥离 + 引号闭合校验，fail-closed | b1 上游文档约束（禁行内注释）+ 解析器只做拒绝（不剥离） | c1 只剥注释、不做闭合校验（fail-open，WARNING） |
| P3 收集（BDD-4/5） | a2 解析器本地收紧为精确键（不动公共库） | b2 扩展 `is_gate_meta_key` 协议级辅助键 + 同步 YAML（S-4） | c2 保留 `startswith`，仅加对账 WARNING（不拦截） |
| judge（BDD-3） | a3 `judge_result` 新增 exit 2 显式分支 | b3 `run_test_with_formatter` 层拦截（新 JSON 标记位 + 管道改动） | —（b3 需改公共库签名，累赘） |
| R2 豁免（BDD-7/8） | a4 路径声明豁免（目录前缀绑定） | b4 内容标记豁免（`# scan-exempt:` 行标记，R4 先例） | c4 豁免清单文件（新增配置文件 + 同步负担） |

- 稻草人自检：b 系在"全链口径统一 / 未来扩展"维度更好；c 系在"工作量最小 / 历史兼容"维度最好——均非纯陪衬，见 §2.3。

### 2.2 候选方案 A：本地化精确修复（推荐）

- 组合：a1 + a2 + a3 + a4。
- 值清洗：新增 `_clean_value(raw)`——扫描首个未转义 ` #`（`\#` 转义保留；引号内 ` #` 保留，防 URL / echo 文本误伤）截断 → 双侧引号闭合校验（残留单侧引号即非法）→ 非法时 `stderr` 报解析错误 + exit 非 0，不输出残渣。M1 两处（L57 / L66）共用。
- 收集：`elif key == "P3":` 精确键；`suffix = ""`，formatter 伴随查找 `P3_formatter` 不变。
- judge：新分支插在 `exit == 0` 判定之后、既有 A 类分支之前——策略选（a）`exit 2` + 零运行器统计为主、文案为辅（评审推荐；主判与 locale 无关，文案只做辅证）。条件：`exit_code == 2` 且运行器统计全零（`failed == errors == syntax_count == import_count == name_errors_count == 0`）为主判 + 输出含辅证文案（英文 `syntax error` / `unexpected` / `matching`——LC_ALL=C 实测，bash 5.2.21；中文 `寻找匹配` / `未预期`——zh_CN.UTF-8 实测，bash 5.2.21）→ 打印 A 类说明 → exit 1。删除无实测推测项 `unmatched` / `找不到匹配`（后者与实测 `寻找匹配` 相反）/ `unterminated`。
- 豁免：豁免目录声明常量（如 `agate/tests/fixtures/` 前缀集合）+ `_scan_target` 内路径前缀判定；正文 R2 循环 `continue` 豁免。
- 优点：公共库零改（S-4 零触碰）；改动面全部本地化、可单测锁定；9 条 BDD 全覆盖。
- 缺点：白名单知识散在解析器本地，跨脚本口径（如 missing-cmds 对 `P3_e2e`）仍不一致——靠回归验证覆盖，不做语义统一。

### 2.3 候选方案 B：协议级统一（备选，最优扩展性）

- 组合：b1 + b2 + a3 + b4。
- `is_gate_meta_key` 扩展 `_e2e`（及未来 `_js` / `_html`）→ 同步 `rules/dispatch.yaml` `meta_suffixes`（S-4 抽样校验要求一致）→ 5 个消费方 + S-4 全回归；豁免走行级内容标记（复用 R4 `# scan-exempt:` 机制，fixture 数据行逐行打标）。
- 优点：在"全链口径统一"维度最好：一次改动，全消费方对辅助键语义一致；未来多栈扩展只需改一处判据。
- 缺点：触碰 DEBT0010 精确匹配意图（防放宽）；爆炸半径 = 公共库 + YAML + 5 脚本 + S-4，不适合 high 风险任务的最小修复原则；内容标记需改 17 处 fixture 行，totouch 面大且标记可被真代码复制（R3 缓解弱于目录绑定）。
- 不选理由：BDD 全覆盖但实现风险显著高于 A；收益（统一口径）可用"P2 卡禁令 + 回归"低成本替代。

### 2.4 候选方案 C：最小兼容（备选，最优成本）

- 组合：c1 + c2 + a3 + c4。
- 解析器只剥注释（不管残留引号）；收集侧保留 `startswith("P3")`，仅对账 WARNING；豁免用独立清单文件。
- 优点：在"工作量最小 / 历史兼容"维度最好：`P3_js` / `P3_html` 历史形态继续工作，零语义变更。
- 缺点：BDD-2（引号未闭合 fail-closed）与 BDD-4（P3_xxx 不收集）不满足——DEBT0027 只修一半、DEBT0023 原地踏步。
- 不选理由：不满足验收基线；仅记录其成本论证，排除。

### 2.5 收紧方案专项：历史多栈形态取舍 + 白名单后缀清单

- 存量证据（引用 dispatch-context，2026-09-04 主 Agent grep）：全仓 `P3_\w+` 仅三类——`P3_formatter`（元键豁免）/ `P3_timeout_seconds`（元键豁免）/ `P3_e2e`（样例 + TAG0012 验收样例，非元键但 ui 任务 E2E 形态）；真实任务 P2-design 从未声明过 `P3_xxx` 检测键（TAG0026 / 27 / 28 全靠约定规避）；`P3_js → both run`（TAG0009 TDD.F10）证明收集侧曾有意支持多 P3* 命令键。
- 取舍结论：收紧为精确键是**语义变更**（不是纯收紧），本设计显式声明——`P3_js` / `P3_html` 历史多栈形态退役：当前 pytest 单栈任务无此用法；若未来多栈回归，走协议修订在收集白名单登记收集后缀（+ 单测 + consistency 回归），不走静默收集。
- 白名单后缀清单（写入 P2 卡禁令，BDD-6）：`_formatter` / `_timeout_seconds`（元键，`is_gate_meta_key` 豁免）+ `_e2e`（E2E 形态，P5_e2e 消费，P3 永不收集）+ 历史 `_js` / `_html`（已退役，不得复用为检测键）。

### 2.6 权衡与选择理由

| 维度 | A 本地化精确修复 | B 协议级统一 | C 最小兼容 |
|------|----------------|-------------|-----------|
| BDD 覆盖（9 条） | 全覆盖 | 全覆盖 | BDD-2 / BDD-4 不满足 |
| 公共库 / YAML 触碰 | 零触碰 | 公共判据 + YAML + 5 消费方 | 零触碰 |
| 历史多栈兼容 | 显式退役（声明取舍） | 保留扩展点 | 完全保留 |
| 豁免防借用（R3） | 目录绑定（强） | 内容标记（弱） | 清单文件（中，需同步） |
| 实现工作量 | 中 | 大 | 小 |

**选择理由（选 A）**：唯一同时满足"9 条 BDD 全覆盖 + 公共库零触碰 + high 风险最小爆炸半径"的方案；B 的统一收益可用文档禁令替代，C 的成本收益以牺牲验收为代价——A 为最优折中。

## 3. 选定方案设计（候选方案 A）

### 3.1 Phase 1 — gate-parser 值清洗（M1，BDD-1 / BDD-2）

- 新增 `_clean_value(raw) -> str`（解析器本地函数，L56 前定义；`parse_gate_commands_block` 公共单点不动）：
  1. `raw.strip()` → 扫描首个未转义 ` #`：逐字符推进，引号状态机（`"` / `'` 开闭，`\` 转义跳过）——仅引号外的 ` #` 截断；
  2. 截断后 strip → 若首尾被一对匹配引号包裹则剥一层；剥后仍含未闭合引号（计数为奇）→ `sys.stderr` 写解析错误（含 key 名 + 行摘要）→ `sys.exit(2)`；
  3. 返回纯命令串。
- M1 两处调用：L57 命令值 + L66 formatter 值（注释尾巴同样污染 formatter 伴随查找）。
- P3 红灯形态（H7）：先补"带行内注释块 → 纯命令 + `bash -c` exit ≠ 2"失败测试确认红，再改实现；"未闭合引号 → exit 非 0 + stderr 有解析错误"同理。

### 3.2 Phase 2 — P3 收集收紧（M2，BDD-4 / BDD-5 / BDD-6）

- L60 改为 `elif key == "P3":`；`suffix = ""`；`fmt_key = "P3_formatter"` 伴随查找逻辑不变。
- BDD-5 锁定：裸 P3 收集、两元键豁免——单测覆盖"三键共存块"的输出断言。
- BDD-6 落点：P2 卡 gate_commands 节新增"P3_xxx 禁止声明"子节（含 §2.5 白名单清单 + 原因：静默收集致 TDD 误执行）。

### 3.3 Phase 1b — judge 显式分支（M3，BDD-3）

- 分区论述：既有 A 类分支 L110–116（`exit == 1` + raw 含 Traceback / SyntaxError 等——运行器正常退出但报告编译错）与 L152–154（`exit >= 120`——运行器自身故障）输入域分别为 exit 1 / exit ≥ 120；新分支输入域为 exit 2（命令串本身语法错误，`bash -c` 未起运行器），三域不交、无优先级冲突；新分支置于 exit 0 判定后、L110 之前。
- 匹配策略（选评审推荐 a）：主判 `exit 2` + 零运行器统计（locale 无关，中文环境亦成立）→ 文案只做辅证。辅证表每项有实测出处（bash 5.2.21）：英文 `syntax error` / `unexpected` / `matching`（LC_ALL=C 实测 `unexpected EOF while looking for matching`"'"`）；中文 `寻找匹配` / `未预期`（zh_CN.UTF-8 实测 `寻找匹配的 `"' 时遇到了未预期的 EOF`）。已删推测项 `unmatched` / `找不到匹配`（与实测 `寻找匹配` 相反）/ `unterminated`。
- 不改 `check-gate.py` 返回约定：0 红灯可推进 / 1 A 类 / 2 全绿 / 3 无运行器含义不变，只是 exit 2 输入从末尾 exit 0 改判 exit 1。
- P3 红灯形态：先补"exit 2 + 语法文案 + 零运行器统计 → exit 1"失败测试确认红（H7）。

### 3.4 Phase 3 — R2 目录声明豁免（M4，BDD-7 / BDD-8）

- 豁免常量：`_FIXTURE_EXEMPT_DIRS`（声明式路径前缀集合，初始含 `agate/tests/fixtures/`；cmdstream fixture 路径在列）——绑定目录声明，禁宽匹配。
- 豁免点：`_scan_file` 入口处判定 `path` 是否位于豁免前缀内 → 是则 R2 跳过（其余 R1 / R3–R5 照常，豁免仅针对 R2 数据面）。
- 与 17 处裸 python3 的关系：fixture 恢复真实日志形态用裸 `python3 -m pytest`（无 `env` 前缀，模拟真实日志）→ 靠目录豁免放行；`command="env python3 -m pytest"` 的 `env` 形式行在任何位置本就豁免（`_r2_comment_exempt`）——两类正交，单测各锁一条。
- 扫描器测试文件干净契约：豁免走路径判定，源码不新增 R1–R5 字面命中，不碰头注释 fragment 机制；P4 自查"全树扫描本文件 0 命中"。
- BDD-9 常驻面：本文件 §4 固化 `P3_scanner` / `P4_scanner` / `P5_scanner` 三 key。

## 4. gate_commands（P2 固化，后续阶段不得修改）

```yaml
gate_commands:
  # P3 TDD 红灯读取（bootstrap 注记：本任务 P3 gate 用 TEST_RUNNER 环境变量覆盖跑裸 P3 命令，
  # 因修前旧解析器会把 P3_scanner 一并收集污染 TDD 判定；修后文件收集即安全，仅裸 P3 被收集）
  P3: "python3 -m pytest agate/tests/ -q --tb=short"
  P3_scanner: "python3 agate/scripts/check-platform-assumptions.py agate/tests/"
  P4_scanner: "python3 agate/scripts/check-platform-assumptions.py agate/tests/"
  # P5 全量三片合跑 + -n auto 并行（参照 TAG0028 P5 写法）
  P5: "python3 -m pytest agate/tests/ -q --tb=no -n auto"
  P5_consistency: "python3 agate/scripts/check-protocol-consistency.py --strict-errors-only"
  P5_shellcheck: "shellcheck -S warning agate/scripts/pre-commit-gate.sh agate/scripts/commit-msg-self-gate.sh agate/scripts/pre-push-gate.sh"
  P5_count_tests: "bash agate/tests/scripts/count-tests.sh"
  P5_scanner: "python3 agate/scripts/check-platform-assumptions.py agate/tests/"
  P5_timeout_seconds: 600
  P3_scanner_timeout_seconds: 120
  P4_scanner_timeout_seconds: 120
  P5_consistency_timeout_seconds: 120
  P5_shellcheck_timeout_seconds: 120
  P5_count_tests_timeout_seconds: 120
  P5_scanner_timeout_seconds: 120
```

- 逐 key 独立（不拼接 `&&`，防短路掩盖）；consistency 用 `--strict-errors-only`；shellcheck 与 CI 同口径 `-S warning` 3 个 hook 薄壳。
- timeout 三档：P5 全量 600s（宁高勿低，TPV0093 教训）；其余单命令 120s；P3 走 `AGATE_TDD_TIMEOUT` 运行时机制（`run_test_with_formatter` 默认 120s），不声明静态值。
- P5_e2e 不适用：`ui_affected: false`（P1 已定 backend 无前端面），故不声明。
- BDD-9 对应：`P3_scanner` / `P4_scanner`（P4 为声明式，implementer 按 checklist 直接跑，exit code 判定）/ `P5_scanner` 常驻。

## 5. files_to_read（P4 implementer 上下文地图）

```yaml
files_to_read:
  - path: agate/scripts/agate-read-gate-commands.py
    why: 改造对象 ① 全文 70 行——L57 / L66 值清洗落点 + L60–67 收集落点
  - path: agate/scripts/check-tdd-red.py:87-157
    why: 改造对象 ② judge_result——新 exit 2 分支插入位置与既有 A 类分区
  - path: agate/scripts/check-platform-assumptions.py:39-93
    why: 改造对象 ③ R2 正则 + 豁免函数 + 扫描循环豁免点
  - path: agate/scripts/agate_common.py:79-87
    why: is_gate_meta_key 判据原文——确认不动它（N3 依据）
  - path: agate/scripts/agate_common.py:679-693
    why: is_legal_gate_key——P3_scanner 等新 key 合法性确认（无对账 WARNING）
  - path: agate/scripts/agate_common.py:784-795
    why: parse_gate_commands_block 公共单点——确认不动（M2 防漂移先例）
  - path: agate/scripts/agate_common.py:499-538
    why: run_test_with_formatter——P3 超时机制与 fallback JSON 形态（judge 输入域依据）
  - path: agate/scripts/check-structure-consistency.py:414-460
    why: S-4 校验口径——不动判据的回归锚
  - path: agate/rules/dispatch.yaml:25-28
    why: gate_commands_syntax 声明——与判据一致性确认（N7 依据）
  - path: agate/phase-cards/P2-design.md:125-180
    why: BDD-6 落点——gate_commands 节禁令子节新增位置
  - path: agate/tests/scripts/test_check_platform_assumptions.py:1-60
    why: 扫描器测试"保持干净"契约——豁免设计不得破坏的边界
  - path: agate-workspace/debt/tech-debt.md:814-841
    why: DEBT0023 closure_criteria 原文（单测锁定 + P2 卡禁令）
  - path: agate-workspace/debt/tech-debt.md:910-932
    why: DEBT0027 closure_criteria 原文（纯命令 / exit 1 / 单测三条）
  - path: agate-workspace/tasks/TAG0028-subagent-liveness-self-dispatch/P2-design.md:173-197
    why: gate_commands 固化范例（P3 / P5 写法 + timeout 三档 + 逐 key 独立）
```

## 6. env_constraints（确认 P0-brief，不得弱化）

```yaml
env_constraints:
  debug_env: "系统 python3 + pyyaml 跑 pytest；ruff 用 ~/.venvs/agate-dev/bin/ruff；基线验证 --strict-errors-only（DEBT0012）"
  isolation_check: "改造对象为 worktree 的 agate/，~/.agate 稳定版勿动；编排/派发类工具一律用 ~/.agate/scripts 稳定版（TAG0016 教训）；consistency 必须用 worktree 自己的脚本"
  self_gate: "改 agate/scripts/* + agate/phase-cards/P2-design.md 触发 SELF-GATE——commit message 须含 self-gate-review: 或 self-gate-skip:（commit 时处理）"
```

- 强制力说明：环境约束本身是声明性的；真正的强制执行落在 §4 gate_commands（P5_consistency / P5_scanner 等有 exit code 判定）与 M6 单测（BDD 逐条锁定）。

## 7. minimal_validation

```yaml
minimal_validation:
  assumption: "值清洗残渣（残留引号 + 注释尾巴）致消费方 bash -c 报 unterminated quote，exit 2"
  method: "一条 bash -c 实测：bash -c 'echo hi\" # comment'"
  result: "confirmed——exit=2，stderr 含“寻找匹配的 `\"' 时遇到了未预期的 EOF”；对照组 bash -c 'echo hi' exit=0"
  note: "其余设计为纯代码逻辑，无外部系统依赖——依赖内部函数：parse_gate_commands_block（块→JSON entries）、is_gate_meta_key / is_legal_gate_key（合法性口径确认）、run_test_with_formatter（命令→JSON，exit 124 超时语义）、judge_result（JSON→exit 码分支）、R2 正则 + _r2_comment_exempt；数据转换：gate_commands 块→commands JSON / 测试输出→formatter JSON→exit 码 / 扫描命中行→exit 1"
```

## 8. 实现完成标志

- [ ] M1：带行内注释块解析出纯命令且 `bash -c` exit ≠ 2（BDD-1）；未闭合引号报解析错误 exit 非 0 + stderr（BDD-2）
- [ ] M3：语法错误命令串判 exit 1（BDD-3），P3 双 locale 用例：中文串（`寻找匹配`/`未预期`）→ exit 1 + 英文串（`unexpected`/`matching`/`syntax error`）→ exit 1；既有 A 类分支行为不变
- [ ] M2：P3_xxx 不收集、裸 P3 + 元键豁免行为单测锁定（BDD-4 / BDD-5）；P2 卡禁令子节存在（BDD-6）
- [ ] M4：fixture 数据面 0 命中且 exit 0（BDD-7）；目录外裸调用仍命中 exit 1（BDD-8）；三 scanner key 可独立跑通（BDD-9）
- [ ] 回归底线：Linux 全量 pytest 全绿 + consistency 0 ERROR + shellcheck 0 error + 用例数不漂移（count-tests）
- [ ] P4 落地前按 DEBT0025 先全量扫描存量（常驻面启用前提，H6）

## 9. 批次设计

- `dispatch_plan: {mode: single}`——四处改动同源耦合（同一解析器消费链：M1 / M2 同文件、M3 消费 M1 输出、M4 / M5 共享 gate 语义），P0 已定强合并单 task；单批产出小（3 脚本局部改 + 1 卡片节 + 单测），无 high 工作量维度；全量 pytest 为资源密集型，串行跑。拆批反而制造同文件跨批冲突，故单发串行。
