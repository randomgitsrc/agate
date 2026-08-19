> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心输入源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。

---
phase: P3
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0015
role: test-designer
retry: 0
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

按 P2-design.md §5 `gate_commands.P3` 已固化的三个测试文件，为 P1-requirements.md 的 20 条
BDD 各写一个 1:1 对应的测试用例，产出真红灯（实现未写，测试因断言失败/项目内 import 失败而红，
不是语法错误/第三方依赖缺失的假红灯）。

### 约束

1. **三个测试文件严格对应 P2-design.md 的规划，不要另起炉灶**：
   a. `agate/tests/unit/test_check_retrospective.py`（**扩展既有文件**，不要新建/覆盖）——新增
      ≥2 个 `test_` 函数覆盖 BDD-9（路径提示文案改为 `tasks/{Txxx}/retrospective.md`，不再含
      `docs/releases`）+ BDD-10（DEBT/roadmap 关联信号触发"发现机制缺口"提醒，exit code 仍 0）+
      BDD-11 本身就是"新增这些断言"这件事——不需要单独测 BDD-11，BDD-9/10 的新增用例即是 BDD-11
      的实现。
   b. `agate/tests/unit/test_agate_feedback.py`（**新建**，脚本 `agate/scripts/agate-feedback.py`
      本身也不存在，需先写测试文件本身会因 `ImportError`/`ModuleNotFoundError`/`FileNotFoundError`
      产生真红灯）——覆盖 BDD-17（结构化提取，依赖一份含 BDD-6/BDD-7 字段的样例复盘文档 fixture）/
      BDD-18（匿名化：项目名占位符化 + 绝对路径截断，P2-design.md 候选方案 B1 轻量正则脱敏）/
      BDD-19（`AGATE_FEEDBACK` 未设置或 off 时不产生输出，exit code 提示"未启用"）/ BDD-20
      （不调用 `gh`/`git push` 等网络提交命令——可用 `unittest.mock` 打桩确认未调用，或静态
      grep 脚本源码确认不含这些调用）。
   c. `agate/tests/unit/test_retrospective_protocol_docs.py`（**新建**，风格参照
      `agate/tests/unit/test_review_role_docs.py`——`agate_root` fixture（见
      `agate/tests/conftest.py:306`）+ 逐 BDD 一个 `test_bdd_N_xxx` 函数 + 文件内容子串断言，
      不 import 被测协议文档为 Python 模块，纯文本读取校验）——覆盖 BDD-1/2/3/4/5/6/7/8/12/13/
      14/15/16 共 13 条纯文档类 BDD（含 P2-design.md 修订后新增的 `test_bdd_13` 验收锚点，具体
      断言内容见 P2-design.md §6「实现完成的标志」中 BDD-13 对应行——验收对象含"每阶段 gate 通过
      后 `P{n}-checkpoint.md` 存在"这类运行时产物，本 BDD 的测试断言范围按 P2-design.md 已经
      收窄到"协议文档（state-machine.md/task-files.md）是否定义了这个规则"，不是断言某次任务的
      checkpoint 文件真的存在——后者是 P6 verifier 的职责，不是 P3 单测的职责，写测试时不要混淆
      这两个层次）。
2. **20 条 BDD 与三个文件的映射必须是满射（每条 BDD 至少 1 个测试函数，可用
   `grep -c "BDD-" test_*.py` 类命令自查）**，不允许遗漏或用一个笼统的测试函数覆盖多条 BDD
   而不做区分。
3. **红灯真实性是本阶段的核心门槛**——写完测试后必须自跑（`timeout 60s python3 -m pytest
   agate/tests/unit/test_check_retrospective.py agate/tests/unit/test_agate_feedback.py
   agate/tests/unit/test_retrospective_protocol_docs.py -v`），确认每个新增/新建测试函数的失败
   原因都是"断言失败"或"项目内 import 失败"（B 类），不是测试代码自身的语法错误/import 第三方库
   失败（A 类）。**不要为了让红灯"看起来对"而故意写一个会 SyntaxError 的占位文件**——那是假红灯，
   check-tdd-red.py 会判 exit 1 打回。
4. **不要提前实现被测对象**——`docs/reviews/postmortem-template.md` 还没有迁移到
   `agate/assets/templates/retrospective-template.md`（这是 P4 implementer 的工作），
   `agate/scripts/agate-feedback.py` 还不存在，`agate/scripts/check-retrospective.py` 第 93
   行还是旧文案——测试针对的是"改完之后应该是什么样"，不是当前状态，红灯是正常且预期的。
5. **既有测试不能破坏**——`test_check_retrospective.py` 现有 12 个 `test_` 用例（覆盖
   `retries_over`/`SCOPE+`/`override` 三个既有触发点）必须继续通过，只做新增，不删改既有用例的
   断言语义。
6. **fixture 隔离（P2-design.md env_constraints 已预警）**：BDD-10 的 DEBT/roadmap 关联检测依赖
   两层嵌套的工作区目录结构（`tmp_path/agate-workspace/tasks/T001/` 作 task_dir，
   `tmp_path/agate-workspace/debt/`、`tmp_path/agate-workspace/roadmap/` 作兄弟目录），不能复用
   共享 `task_dir` fixture 的默认单层布局（会导致两级向上推导指向 `tmp_path` 本身而非虚构的
   debt/roadmap 目录）——自行搭建嵌套结构或用 `monkeypatch`，不要读真实仓库的
   `agate-workspace/debt/tech-debt.md`/`roadmap.md`（会导致测试结果依赖仓库实际数据，不可复现）。
7. **P3-test-cases.md 必须声明 `test_code_dir`**（三个测试文件所在目录 `agate/tests/unit/`），
   每条测试用例需列出"对应哪条 BDD-NN + 测试函数名 + 覆盖点"的映射表，供 P4/P5/P6 追溯。

### 上游关联

- P2-design.md §5 `gate_commands.P3` 已固化的测试命令：
  `python3 -m pytest agate/tests/unit/test_check_retrospective.py
  agate/tests/unit/test_agate_feedback.py agate/tests/unit/test_retrospective_protocol_docs.py -v`
  ——本次产出的三个测试文件路径必须与这条命令逐字匹配，否则 P5 阶段固化的验证命令找不到测试。
- BDD-6/BDD-7（frontmatter 机器字段 + `## agate 反馈` 节）是 BDD-17 的输入依赖——写
  `test_agate_feedback.py` 的 BDD-17 测试用例时，需要在测试代码里构造一份符合 BDD-6/BDD-7
  格式的样例复盘文档 fixture（内联字符串或 `tmp_path` 写临时文件均可），不要依赖真实存在的
  `retrospective-template.md`（P4 才会产出）。
- P2-design.md §3.1（check-retrospective.py 新增分支实现要点）已给出 BDD-9/10 的具体设计要点
  （新增 `_scan_debt_roadmap_signal` 等函数名），测试用例的断言可以先按这个设计要点来写（P4
  implementer 会照此实现），但函数名细节若 P4 实际实现时有调整，测试只断言"公开行为"（stderr
  输出内容 + exit code），不要断言内部私有函数名是否存在。

### 输入文件（按顺序读）

1. `{AGATE_WORKSPACE}/tasks/TAG0015-retrospective-feedback/P2-design.md`（521+ 行，§5
   gate_commands + §6 实现完成的标志 是本次测试设计的直接依据）
2. `{AGATE_WORKSPACE}/tasks/TAG0015-retrospective-feedback/P1-requirements.md`（20 条 BDD 原文）
3. `agate/tests/unit/test_check_retrospective.py`（242 行全文，扩展对象）
4. `agate/tests/unit/test_review_role_docs.py`（104 行全文，`test_retrospective_protocol_docs.py`
   的风格参照）
5. `agate/tests/conftest.py` 第 300-320 行附近（`agate_root`/`task_dir` fixture 定义）
6. `agate/scripts/check-retrospective.py`（100 行全文，BDD-9/10 断言对象）

### 门槛（什么算完成）

P3-test-cases.md 声明 `test_code_dir: agate/tests/unit/`；三个测试文件均已创建/扩展；20 条 BDD
均有对应测试函数（1:1 或更细，不遗漏）；`check-tdd-red.py` 确认为真红灯（exit 0）。
</dispatch_guide>

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
- `agate/tests/unit/test_check_retrospective.py` 现状：242 行，12 个 `test_` 函数，均围绕
  `retries_over`/`SCOPE+`/`override` 三个既有触发点，对路径文案（BDD-9）与新触发条件（BDD-10）
  均无断言（P1 阶段已 grep 确认零命中）。
- `agate/tests/unit/test_review_role_docs.py` 是 P2-design.md 指定的风格参照，104 行，模式：
  `_read(agate_root, *parts)` 辅助函数 + 逐 BDD 一个 `test_bdd_N_xxx(agate_root)` 函数 + 纯文本
  子串断言，不 import 协议文档为模块。
- `agate/tests/conftest.py:306` 定义 `agate_root` fixture。
- 环境基线（P2 阶段验证过，未再变化）：`pytest` 909 passed + 2 skipped；
  `check-protocol-consistency.py --strict` 0 ERROR / 279 WARNING。
- P2-design.md 已声明 `gate_commands.P3` 的完整命令（见上方"上游关联"第一条），执行完直接产出
  verbose 输出，供 `check-tdd-red.py` 自动读取判红灯。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
