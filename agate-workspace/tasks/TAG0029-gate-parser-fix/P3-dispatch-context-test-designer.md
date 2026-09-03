---
phase: P3
generated_by: 主 Agent
task_id: TAG0029
role: test-designer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
产出 `agate-workspace/tasks/TAG0029-gate-parser-fix/P3-test-cases.md`（声明 `test_code_dir` + BDD-1~9 的 1:1 用例映射）+ `agate/tests/` 下新增 pytest 测试代码——9 条 BDD 每条至少 1 个红灯测试（当前实现未改，跑即失败，失败原因须是"被测模块未实现/旧语义"，不是测试代码 bug）。

### 约束
- **BDD→测试 1:1 映射**（测试名含 BDD 编号，如 `test_tag0029_bdd_1_...`）：
  - BDD-1（行内注释→纯命令）：构造含行内注释的 gate_commands 块 fixture → 调解析器 → 断言输出 cmd 恰等于纯命令（无注释尾巴、无残留引号）+ `bash -c` 执行该 cmd 退出码 ≠ 2 且 stderr 无 unterminated 类文案。红灯形态：旧解析器输出带残渣 → 断言失败。
  - BDD-2（未闭合引号→解析错误）：构造引号未闭合块 → 断言解析器 exit 非 0 + stderr 有解析错误 + 无残渣命令串输出。红灯形态：旧解析器 exit 0 产出残渣 → 断言失败。
  - BDD-3（exit 2 语法错误→exit 1）：直接调 `judge_result`（或走 check-tdd-red 对含语法错误命令串的块）：输入 `exit_code=2` + 语法文案 + 零运行器统计（failed=errors=syntax=import=name=0）→ 断言返回 1。**双 locale 用例**（P2-review T1 强制）：中文串（`寻找匹配`/`未预期`，zh_CN.UTF-8 实测）→ 1 + 英文串（`unexpected`/`matching`/`syntax error`，LC_ALL=C 实测）→ 1。已删推测项 `unmatched`/`找不到匹配`/`unterminated` 不得出现在用例里。红灯形态：旧 judge 落末尾 exit 0 → 断言失败。
  - BDD-4（P3_xxx 不收集）：构造含 P3_xxx 辅助键的块 → 断言 commands 不含该键条目（含 `_e2e` 形态一例）。红灯形态：旧 `startswith("P3")` 收集 → 断言失败。
  - BDD-5（裸 P3 收集 + 元键豁免）：构造裸 P3 + `_formatter`/`_timeout_seconds` 元键三键共存块 → 断言含裸 P3 条目且不含元键条目。注意：这是**锁定既有正确行为**的用例，新旧实现都应绿——若红了说明测试 fixture 写法有误，先自查（P3 自检强制）。
  - BDD-6（P2 卡禁令存在性）：文档存在性断言——读 worktree `agate/phase-cards/P2-design.md` gate_commands 节，断言含 P3_xxx 禁止声明文本 + 原因说明。注意这是**前瞻断言**：P4 才改卡，P3 跑即红（文件尚无禁令）——红灯原因是"被测产物未实现"，符合 TDD。
  - BDD-7（R2 fixture 豁免）：fixture 目录内数据文件 command 字段含裸 `python3 -m pytest` → 扫该目录 → 断言 R2 无命中 + exit 0。fixture 路径须落在设计 §3.4 豁免常量前缀下（`agate/tests/fixtures/`）。
  - BDD-8（R2 代码面仍拦截）：豁免目录外的测试代码行含命令位置裸 python3（非注释/非 docstring/非探测形态）→ 断言 R2 命中 + exit 1。
  - BDD-6/9 的 P2-design.md 存在性断言（本任务自己的 P2-design，非协议卡）：BDD-9 断言本任务 P2-design.md 的 P3/P4 块含 scanner 条目——已存在即绿（锁定用例）；BDD-6 的协议卡禁令尚不存在即红。
- **P3 自检（强制）**：产出后自跑每个测试，确认失败原因都是"被测模块未实现/旧语义"（残渣输出 / exit 0 误判 / 收集多余条目 / 禁令缺失），不是"断言与 fixture 矛盾"（魔数/路径写错）。BDD-5/BDD-9-本任务面是锁定用例，预期绿——红了先修测试。
- **测试隔离铁律**：fixture 用 `tmp_path`，不用 `/tmp`；不裸 `python3`（用 conftest 的 `python_exe` fixture 探测）；平台无关断言（本机中文 locale 文案只出现在 BDD-3 中文用例的输入构造，不做全量输出匹配）。
- **扫描器测试干净契约**：新增测试文件自身不得含 R1–R5 字面命中（参照 `test_check_platform_assumptions.py` 头注释 fragment 拼接法）——否则全树扫描自伤。`python3` 字面只出现在经豁免的形态（注释行/`env `形/docstring）或拆写（`"python"+"3"`）。
- **DEBT0024（假 gate exit 教训）**：judge 相关用例调真实 `judge_result` 函数，不 mock exit 码；解析器用例调真实解析器（子进程或 import），不 stub 输出。
- 测试文件落点：`agate/tests/unit/` 下新建（命名如 `test_tag0029_gate_parser_fix.py`，BDD-1~5 judge/解析器/收集）+ `agate/tests/scripts/` 下 R2 豁免用例是否新建由你定（若复用既有扫描器测试文件则声明位置；新建则遵守干净契约）。`test_code_dir` 在 P3-test-cases.md 声明实际路径。
- 返回前跑 `python3 agate/scripts/check-frontmatter.py` 自检 P3-test-cases.md（worktree 根），非 0 先修正再返回。
</dispatch_guide>

### 上游关联
- P2-design.md 已 approved（选定方案 A；B1 复审关闭：匹配策略主判 locale 无关 + 双 locale 实测串；D1–D10 锁定；dispatch_plan mode=single）。
- P1-requirements.md 9 条 BDD 为测试映射源；P2 §8 实现完成标志为用例验收清单。
- `.state.yaml` phase=P2（P3 推进随 P3 产出 commit 一起）。

### 输入文件
- `agate-workspace/tasks/TAG0029-gate-parser-fix/P2-design.md`（选定方案 §3.1–3.4 实现形态 + §8 完成标志——**P3 主要输入**）
- `agate-workspace/tasks/TAG0029-gate-parser-fix/P1-requirements.md`（BDD-1~9 Given/When/Then 原文）
- `agate-workspace/tasks/TAG0029-gate-parser-fix/P2-review.md`（T1–T5 测试缺口清单——逐条落实）
- `agate/scripts/agate-read-gate-commands.py`（被测对象 ①，70 行）
- `agate/scripts/check-tdd-red.py`（被测对象 ②，judge_result L87-157 + main 收集循环 L160-219）
- `agate/scripts/check-platform-assumptions.py`（被测对象 ③，R2 L39 + 豁免 L46-93）
- `agate/tests/conftest.py`（fixture 体系：create_task_dir / run_cli / python_exe / agate_scripts——复用，不自造）
- `agate/tests/scripts/test_check_platform_assumptions.py`（头 60 行干净契约 + fragment 拼接法——R2 用例参照）
- `agate/tests/unit/test_check_tdd_red.py`（既有 judge 用例形态——BDD-3 用例参照，不重复造轮子）

<!-- AGATE_CARD_START -->
## 当前阶段卡片：P3

路径：phase-cards/P3-tdd.md
---
# P3 — TDD 测试设计

> 当前状态：[首次 / 重试 #N / 裁剪跳阶]
> 裁剪跳阶 → 确认 P1 phases 不含 P3 + 有合规理由（risk=low + 跳过风险已声明）→ 跳过，读 P4 卡片

## 如果是首次进入本阶段

0. 跑 `agate-capture-env-baseline.py $TASK_DIR`（自动捕获环境基线）。**必须执行**。
   该步骤不阻塞流程——脚本的 stderr 输出（含 WARNING）均可忽略，执行完直接继续步骤 1。
1. 派发 test-designer subagent → 产出 P3-test-cases.md + 测试代码目录
   1.1 写 P3-dispatch-context-test-designer.md（派发指引：目标/约束/上游关联/输入文件 + 客观查证信息）
2. 主 Agent 跑 check-tdd-red.py 确认红灯
3. git add {AGATE_WORKSPACE}/tasks/{Txxx}/（含 .state.yaml + 产出文件，若 .gitignore 忽略需 git add -f）
   ⚠️ 此时 .state.yaml 的 phase 保持 P3，不要提前写 P4——phase = 本 commit 的产出阶段
4. git commit -m "wf({Txxx}-P3): {摘要}"（phase=P3，P3 产出含 P3-test-cases.md + 测试代码）
5. P3 commit 完成后进入 P4：**phase 推进 P4 随 P4 产出 commit 一起**（P4-implementation.md 就绪后），不是单独 phase commit

## refactor 任务：回归测试口径

> 适用：P1 frontmatter 声明 `change_type: refactor` 的任务（P2-design.md §3.4）。功能任务（缺省）走上方既有 TDD 口径，不受本节影响。

refactor 任务无新增功能行为可断言，P3 测试设计改用**回归测试口径**：

- **测试设计 = 回归测试口径**：复用/保留既有测试用例，标注每条回归用例覆盖了重构涉及的哪些文件/路径；**不新增功能行为断言**（无新行为可断言）。
- **跳过 check-tdd-red 红灯步骤**：重构无新功能断言，测试套件本就全绿，红灯语义不适用（check-tdd-red 对 refactor 任务会误报 exit 2 绿灯）。回归质量由 P5 全量回归（gate_commands.P5）+ P6 的 `regression.log`（全量回归重跑）兜底。CI backstop 对 refactor 任务同样跳过 check-tdd-red（ci-gate-backstop.py P3 分支 refactor 感知）。
- **P3 gate 不变**：仍为文件存在性检查——refactor 的 P3 产出是 P3-test-cases.md（回归口径声明 + 既有用例覆盖映射），文件存在即满足 gate。

## 如果是重试

确认上一轮失败原因（测试设计不合理 / 未覆盖关键 BDD / 非真红灯）
→ 读 agate/rules/state-transitions.md 确认 retry 上限（P3 MAX=2）

## 前置条件

- [ ] P2-design.md files_to_read 完整（测试设计需要知道实现导航）
- [ ] P2-review.md status: approved（P2 不可裁剪）

## 派发

- **角色**：test-designer（`{agate_root}/assets/execution-roles/test-designer.md`）
- **输入**：P2-design.md + P1-requirements.md（BDD 验收条件，每条 `#### BDD-NN` 对应一个测试用例）
- **输出**：P3-test-cases.md + test_code_dir/
- **派发 prompt**：`{agate_root}/assets/templates/dispatch-prompt.md`

## 产出规格

- P3-test-cases.md 必须声明 `test_code_dir: {路径}`
- 每条测试用例对应一条 P1 的 `#### BDD-NN` 验收条件（1:1 映射）
- UI 任务（P2 ui_affected: true）：必须含 Playwright/E2E 用例

## gate 规则

**check-gate.py P3**（hook + 主 Agent 预跑，秒级文件检查）：
- exit 1：P3-test-cases.md 不存在
- exit 2：P3-test-cases.md 存在（TDD 红灯由 check-tdd-red.py 独立确认）

**check-tdd-red.py**（主 Agent 手动确认红灯 + CI backstop P3 兜底）：

```bash
check-tdd-red.py $TASK_DIR
```

- **exit 0**：真红灯（assertion 失败 / 项目内 import 失败 = B类错误）— 测试正确但因实现未写而失败
- **exit 1**：假红灯（SyntaxError / 第三方 import 失败 = A类错误）— 测试代码自身错误
- **exit 2**：绿了 — 实现先于测试，违反 TDD
- **exit 3**：无可用测试运行器

**技术栈无关**：check-tdd-red.py 通过 formatter 将测试输出标准化为 JSON，不直接解析任何框架的输出格式。formatter 在 gate_commands.P3_formatter 中声明（可选）。不提供 formatter 时退化为 exit-code-only（所有红灯 = 可推进）。

**探测链**：`$TEST_RUNNER` 环境变量 → `gate_commands.P3`（P2-design.md 声明）→ `which pytest` → exit 3。`$TEST_RUNNER` 始终优先（退化为 exit-code-only，无 formatter）。

**formatter 选择**：见 `assets/formatters/README.md` 速查表。常用：pytest → `pytest.sh`，vitest → `vitest.sh`，go test → `go-test.sh`，其他 → `generic-exit-only.sh`。

## 按包拆分并行（条件触发，非强制）

> 仅当 P2 packages > 1 且包间无依赖时适用。单包任务跳过本节。
> 并行上限 / 失败批 retry / 共享文件统一后处理见 dispatch-protocol「派发编排机制」并行规则。

当 P2 声明多个 packages 且包间无数据依赖时，P3 可拆分并行：

1. 每个 package 派一个 test-designer subagent
2. 各自写各自的测试文件（不同目录）
3. 各自返回路径 + 摘要
4. 主 Agent 汇总后统一 commit

拆分判据（本阶段特定）：
- P2 packages > 1 且包间无数据依赖 → 可并行
- 单包或包间有依赖 → 串行（不拆分）
- P2 未声明 packages → 串行

每个 subagent 的 dispatch-context 必须明确其负责的 package 范围（约束节写"只写 {pkg} 目录下的测试"）。

## 推进条件（全部满足才写 phase: P4）

- [ ] check-tdd-red.py exit 0（真红灯确认）
- [ ] P3-test-cases.md 存在且含 test_code_dir
- [ ] 测试代码目录存在
- [ ] UI 任务：Playwright/E2E 用例存在

## 常见错误

1. **测试绿了才 commit**：测试已在 P4 之前通过 → 违反 TDD"测试先于实现"原则。P3 的 gate 要求红灯
2. **忘记声明 test_code_dir**：后续阶段找不到测试代码 → P5 跑 gate_commands 时找不到测试路径
3. **测试覆盖不全**：只为部分 BDD 写了测试 → P6 验收时那些 BDD 没有自动化验证
4. **gate 不过 ≠ 你失败了**：红灯指向工作/设计的问题，不指向你。正确动作是诊断→退回/重试/PAUSED，不是修改产出让它变绿。
5. **只覆盖交互路径，忽略前置状态**：测试设计应覆盖 BDD Given 隐含的前置状态，不只覆盖 When/Then 路径（详见 WORKFLOW.md §P3 测试设计指导）

## 下游影响

- P4 用测试驱动实现（implementer 看测试理解预期行为）
- P5 跑同一套测试验证实现正确性（gate_commands.P5）

> 完成 → 读 phase-cards/P4-implementation.md
<!-- AGATE_CARD_END -->

<objective_info>
- worktree 根：`/home/kity/oclab/agateon/.worktrees/agate-TAG0029`；分支 `feat/TAG0029-gate-parser-fix`；hook 指向 `~/.agate` 稳定版。
- P3 环境基线已捕获（无 formatter 故未写文件，符合预期——P2 未声明 formatter，pytest 输出走 exit-code-only + exit 码判定）。
- 红灯确认方式（主 Agent 执行，你只需保证测试本身红得正确）：`TEST_RUNNER="python3 -m pytest <新测试文件> -q --tb=no" python3 agate/scripts/check-tdd-red.py agate-workspace/tasks/TAG0029-gate-parser-fix`（TEST_RUNNER 最高优先级，绕过文件收集，避免旧解析器把 P3_scanner 当命令污染判定——设计 R6）。
- 本任务 P2-design.md gate_commands 的 P3/P3_scanner 在 P3 阶段的语义：P3=全量 pytest（红灯确认在 P4 实现后才绿，P3 时全量仍绿故不用它确认红灯）；新测试红灯由 TEST_RUNNER 覆盖确认。test-designer 只需写好测试并自跑确认红因正确。
- 单发串行（dispatch_plan mode=single，四改动同源耦合，不拆批）。
- 注：该文件禁止包含 verdict 预判（provenance 审计要求）。
</objective_info>
