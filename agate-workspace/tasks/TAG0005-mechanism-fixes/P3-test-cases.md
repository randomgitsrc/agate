---
phase: P3
task_id: TAG0005-mechanism-fixes
type: test-cases
parent: P2-design.md
trace_id: TAG0005-mechanism-fixes-P3-20260813
status: draft
created: 2026-08-13
agent: test-designer
---

# P3 测试设计 — agate 机制修复批（TAG0005）

> test_code_dir: `agate/tests/unit/`（不另建 P3-test-code/，遵循既有测试布局）
> BDD 全覆盖（P1 16 条 BDD → 16 个测试用例，1:1 映射）。本任务测试直接写进既有 4 个测试文件，不新增测试文件。

## 测试映射总表

| BDD | 测试名 | 文件 | 断言类型 | 预期现状（修复前） |
|-----|--------|------|---------|-------------------|
| BDD-1 | GPC.1（改断言 `3`→`1 2`） | agate-gate-p5-count.bats | 脚本断言 | 红（现状输出 `3`） |
| BDD-2 | GPC.2（改断言 `0`→`0 0`） | agate-gate-p5-count.bats | 脚本断言 | 红（现状输出 `0`） |
| BDD-3 | GPC.3（新增：块含 P5+P5_formatter → `1 0`） | agate-gate-p5-count.bats | 脚本断言 | 红（现状输出 `2`） |
| BDD-4 | G5_CMD.1（改断言主/辅文案） | check-gate.bats | 脚本断言 | 红（现状输出「2 个 gate_commands.P5」） |
| BDD-5 | G5_CMD.2（保持，仅 P5 不 WARNING） | check-gate.bats | 脚本断言 | 绿（保持） |
| BDD-6 | P5C.*（既有，回归守卫，不改） | agate-read-p5-commands.bats | 脚本断言 | 绿（保持） |
| BDD-7 | RP.18（新增：execution 角色不含 Review 指令） | agate-render-dispatch-prompt.bats | 脚本断言 | 红（现状无条件注入） |
| BDD-8 | RP.19（新增：review 角色含完整语义） | agate-render-dispatch-prompt.bats | 脚本断言 | 绿（现状已含，回归锁） |
| BDD-9 | BDD-9 文档断言（新增：`Review 角色特别指令` 仅模板单文件） | check-gate.bats | 文档断言 | 绿（现状仅模板一处，回归锁——P4 后必须仍单文件） |
| BDD-10 | RP.17（新增：角色不存在 → exit 2 + stderr 报错） | agate-render-dispatch-prompt.bats | 脚本断言 | 绿（v0.23.0 已修复，回归锁） |
| BDD-11 | RP.17（同用例，回归锁定） | agate-render-dispatch-prompt.bats | 脚本断言 | 绿（回归锁） |
| BDD-12 | BDD-12 文档断言（新增：dispatch-protocol.md 含「自动重试一次」） | check-gate.bats | 文档断言 | 红（修复前无此措辞） |
| BDD-13 | BDD-13 文档断言（新增：dispatch-protocol.md 含「会话时长异常短」+「<1min」） | check-gate.bats | 文档断言 | 红（修复前无此措辞） |
| BDD-14 | BDD-14 文档断言（新增：MAX_RETRY / PAUSED 段未改） | check-gate.bats | 文档断言 | 绿（现状保持，回归锁） |
| BDD-15 | BDD-15 文档断言（新增：`>&2;\s*exit 0` 全部命中含「跳过」语义） | check-gate.bats | 文档断言 | 红（修复前 check-debt.sh:26 命中但非跳过语义） |
| BDD-16 | BDD-16 新增用例（check-debt.sh 依赖缺失 → exit 2 + stderr 报错） | agate-debt-check.bats | 脚本断言 | 红（现状 exit 0） |

> **断言类型区分**：BDD-9/12/13/14/15 为**文档断言**（自写断言，grep 文档文本，修复前失败原因 = 文档文本不存在/不匹配）；其余为**脚本断言**（跑被测脚本，失败原因 = 被测脚本行为未修）。
> **回归锁说明**：BDD-8/9/10/11/14 与 RP.17 现状已绿（所断言行为已存在且不得回退），如实记录为绿——它们是防回退锁定用例，不算假红（P3 自检口径）。真正红灯（修复前失败）为 GPC.1/2/3、G5_CMD.1/5、RP.18、BDD-1/12/13/15/16。

## RM-AG0011 — P5 主/辅计数（BDD-1/2/3/4/5/6）

### 测试 1：GPC.1 统计 P5 命令数（改断言，BDD-1）

- **BDD-1**: P5 计数区分主命令与辅助命令
- 前置：P2-design.md 声明 `P5: pytest` + `P5_unit: pytest unit` + `P5_e2e: npx vitest`
- 断言：`GATE_FILE` 指向该文件运行 `agate-gate-p5-count.py` → 输出 `1 2`（1 主 + 2 辅）
- **文档断言**：否（脚本断言）。预期红灯：现状输出 `3`（合并计数），断言 `1 2` 失败
- 既有用例 GPC.1 改断言（`3` → `1 2`）

### 测试 2：GPC.2 无 gate_commands 块 → `0 0`（改断言，BDD-2）

- **BDD-2**: check-gate P5 多命令 WARNING 文案区分主/辅
- 前置：P2-design.md 无 gate_commands 块
- 断言：输出 `0 0`
- **文档断言**：否（脚本断言）。预期红灯：现状输出 `0`，断言 `0 0` 失败
- 既有用例 GPC.2 改断言（`0` → `0 0`）

### 测试 3：GPC.3 块含 P5+P5_formatter → `1 0`（新增，BDD-3）

- **BDD-3**: aux 排除 `_formatter`（P2-review NB 测试缺口）
- 前置：gate_commands 块含 `P5: pytest` + `P5_formatter: pytest.sh`（无 P5_e2e 等辅助命令）
- 断言：输出 `1 0`（主=1，辅=0——`_formatter` 不计入辅助命令）
- **文档断言**：否（脚本断言）。预期红灯：现状正则 `^  (P5\w*):` 会把 formatter 计入 → 输出 `2`

### 测试 4/5：G5_CMD.1 / G5_CMD.5 改主/辅文案断言（BDD-4/5）

- **BDD-4**: check-gate P5 WARNING 区分主/辅文案
- 前置：P2-design.md 声明 `P5: pytest` + `P5_e2e: playwright test`
- 断言：check-gate.sh P5 输出含 `1 个主命令 + 1 个辅助命令` 且含 `共 2 条`
- **文档断言**：否（脚本断言）。预期红灯：现状文案「2 个 gate_commands.P5」不匹配新断言
- G5_CMD.1（L626）与 G5_CMD.5（L697，无尾随换行回归）两处同步改断言

### 测试 6：G5_CMD.2 仅 P5 不 WARNING（保持，BDD-5）

- **BDD-5**: 仅主命令（无 P5_*）时不输出多命令 WARNING
- 断言：check-gate.sh P5 输出不含 `gate_commands.P5 命令`
- **文档断言**：否（脚本断言）。现状绿，保持不动（P2-design 明确「G5_CMD.2 保持」）

### 测试 7：P5C.* 执行枚举回归守卫（既有，不改，BDD-6）

- **BDD-6**: read-p5-commands 执行枚举行为不变（主+辅全枚举）
- 断言：agate-read-p5-commands.bats P5C.1-P5C.4 保持全绿
- **文档断言**：否（脚本断言）。不改该文件，P5 全量回归时作守卫（I5 回归守卫）

## RM-AG0012① — Review 指令按角色类型条件注入（BDD-7/8/9）

### 测试 8：RP.18 execution 角色渲染不含「Review 角色特别指令」（新增，BDD-7）

- **BDD-7**: 执行角色派发 prompt 不含「Review 角色特别指令」
- 前置：执行 `agate-render-dispatch-prompt.sh P2 architect TASK_DIR`
- 断言：输出不含 `Review 角色特别指令`
- **文档断言**：否（脚本断言）。预期红灯：现状 render 脚本从模板主代码块无条件注入 → architect 输出含该节

### 测试 9：RP.19 review 角色渲染含「Review 角色特别指令」完整语义（新增，BDD-8）

- **BDD-8**: 评审角色派发 prompt 含该节 + status 初始 draft 后改 approved/rejected/needs-revision 完整语义
- 前置：执行 `agate-render-dispatch-prompt.sh P2 design-review TASK_DIR`
- 断言：输出含 `Review 角色特别指令` + `approved` + `rejected` + `needs-revision`
- **文档断言**：否（脚本断言）。现状绿（无条件注入 → review 角色本就含该节），回归锁——P4 条件注入改动后仍须保持 review 角色含完整语义

### 测试 10：BDD-9 文档断言 — 全仓该指令仅模板一处（新增，BDD-9）

- **BDD-9**: 协议内「Review 角色特别指令」仅 dispatch-prompt.md 模板一处
- 断言：`grep -rl 'Review 角色特别指令' "$AGATE_ROOT" --include='*.md'` 输出仅 1 个文件且为 `assets/templates/dispatch-prompt.md`
- **文档断言**：是。现状绿（仅模板一处），回归锁——P4 后必须仍单文件
- **作用域说明**：断言限 `--include='*.md'`（协议文档文件）。原因：P2-design §2.3 的 render 脚本实现含 `sed -n '/^### Review 角色特别指令$/...'`——节标题字面量会出现在 render 脚本中（机制引用，非「无条件注入副本」），故全类型 `rg -l` 会命中 2 文件导致误判。BDD-9 语义是「协议文档无第二份无条件注入副本」，故只对 `.md` 协议文档断言单文件

## RM-AG0012② — render 角色不存在 exit 2（BDD-10/11）

### 测试 11：RP.17 角色文件不存在 → exit 2 + stderr 报错（新增，BDD-10/11）

- **BDD-10**: 角色文件不存在 → exit 2 + stderr 含「角色文件不存在」
- **BDD-11**: 该行为有 bats 回归测试锁定（RP 系列新增编号）
- 前置：`agate-render-dispatch-prompt.sh P2 nonexistent-role TASK_DIR`
- 断言：`status` = 2 且输出含 `角色文件不存在`
- **文档断言**：否（脚本断言）。现状绿（v0.23.0 已修复 exit 2），回归锁——防退回 v0.23.0 前 exit 0（P2-design §2.4 锁定）

## RM-AG0003 — 短命会话自动重试（BDD-12/13/14）

### 测试 12：BDD-12 文档断言 — dispatch-protocol.md 含「自动重试一次」（新增）

- **BDD-12**: 空返回恢复策略含「自动重试一次」
- 断言：`grep -q '自动重试一次' dispatch-protocol.md`
- **文档断言**：是。预期红灯：修复前 L111-118「第 1 次空返回」无该措辞

### 测试 13：BDD-13 文档断言 — 含「会话时长异常短」+「<1min」（新增）

- **BDD-13**: 短会话（<1min）空返回触发异常告警
- 断言：`grep -q '会话时长异常短' dispatch-protocol.md` 且 `grep -q '<1min' dispatch-protocol.md`
- **文档断言**：是。预期红灯：修复前无此告警措辞与阈值

### 测试 14：BDD-14 文档断言 — MAX_RETRY / PAUSED 段未改（新增，回归锁）

- **BDD-14**: 自动重试不改变现有 retry 上限/PAUSED 规则
- 断言：`grep -q 'MAX_RETRY' dispatch-protocol.md` 且 `grep -q 'PAUSED 报告人工' dispatch-protocol.md`（L122 现有措辞保持）
- **文档断言**：是。现状绿（两处均存在），回归锁——P4 改写恢复策略后这些段必须原样保留

## 同类扫描守卫（静默 exit 0，BDD-15/16）

### 测试 15：BDD-15 文档断言 — 全仓 `>&2;\s*exit 0` 仅剩「跳过」语义（新增）

- **BDD-15**: 全仓 scripts 的「stderr 报错后 exit 0」仅剩显式跳过语义
- 断言：`rg -n '>&2;\s*exit 0' "$AGATE_ROOT"/scripts/*.sh` 全部命中行的消息文本含「跳过」语义（`rg` 不可用时退化为 `grep -E`）；命中行数 0 或全含「跳过」即过
- **文档断言**：是。预期红灯：修复前 check-debt.sh:26「无法加载 agate-workspace-resolve.sh」非跳过语义 → 断言失败

### 测试 16：BDD-16 check-debt.sh 依赖缺失 → exit 2 + stderr 报错（新增）

- **BDD-16**: check-debt.sh --retreat-coverage 依赖加载失败不再静默 exit 0
- 前置：临时脚本目录仅放 check-debt.sh（无 agate-workspace-resolve.sh），运行 `check-debt.sh --retreat-coverage`
- 断言：`status` = 2 且输出含 `缺少 agate-workspace-resolve.sh`
- **文档断言**：否（脚本断言）。预期红灯：现状缺依赖时 stderr 报「缺少…跳过回退覆盖比对」但 exit 0

## 测试计数变更

| 文件 | 现状 @test | 变更 | 变更后 |
|------|-----------|------|--------|
| agate-gate-p5-count.bats | 2 | GPC.1/GPC.2 改断言 + 新增 GPC.3 | 3 |
| check-gate.bats | 117 | G5_CMD.1/G5_CMD.5 改断言 + 新增 BDD-1/2/9/12/13/14/15 文档断言 7 条 | 124 |
| agate-render-dispatch-prompt.bats | 17 | 新增 RP.17/18/19 | 20 |
| agate-debt-check.bats | 20 | 新增 BDD-16 | 21 |

> 注：`agate/tests/README.md` 逐脚本计数表（render 记 16，现状 17 已有 1 漂移）在 P4 按实际数同步为 20（P1 I8 + P2-design §2.4 锁定）。check-gate.bats README 记 100（现状 117 存在既有漂移），P4 同步 README 时一并按实际数更新（非本任务引入）。

## 自跑结果（P3）

- 改动断言/新增用例后自跑 4 个测试文件确认红灯性质：
  - 脚本断言（GPC.1/2/3、G5_CMD.1/5、RP.18、BDD-16）：失败原因为「被测脚本行为未修」（断言值 vs 现状输出不符）——红灯正确
  - 文档断言（BDD-12/13/15）：失败原因为「修复前文档文本不存在/不匹配」——红灯正确
  - BDD-1 文档断言：失败原因为「三处 C8 表 backend 行现无 plan-eng-review」——红灯正确
  - 回归锁（RP.17/19、BDD-2/9/14、G5_CMD.2）：现状已绿，如实记录（防回退锁定，不算假红）
  - 未发现「断言与测试数据矛盾」类测试 bug（全部红灯均为被测对象未修所致）
- `[PROD_NOT_TOUCHED]`——全程仅读写 worktree 测试文件与被测脚本副本，未接触生产环境。
