---
phase: P3
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0017-toolchain-fixes
role: test-designer
batch: fg1-doc-boundary
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令。本次是**批次化并行派发**之一（P2 dispatch_plan 5 批之一），你只负责 `fg1-doc-boundary` 批次范围，不要碰其他批次的文件。

### 目标
为 P1 的 BDD-5/6（DEBT0015：`env_constraints` 声明性 vs `gate_commands` 执行性边界文档化 + P4 卡片 deploy 类提醒）**以及 BDD-9 的文档半**（DEBT0012：`--strict` 不放 `&&` 链路中间的协议指引，代码半 `--strict-errors-only` 由 fg3 批次负责）写测试。这三条 BDD 在本批次都是**文档断言型**（判据="能否在文档中找到明确结论"），测试形式是对协议 Markdown 文件做内容/结构断言，当前必须失败（因为对应文字段落尚未写入）。

> ⚠️ 关键：`agate/phase-cards/P2-design.md`「gate_commands 声明」节（约 L117-146）会新增**两段**——BDD-5 的边界说明 + BDD-9 的 `&&` 反模式指引，两段都属于本批次（fg1-doc-boundary），这是 P2 设计文档 §1.3 R1 明确的"两个功能分组共享同一落点文件、合并为一批"处理（避免被拆到两个批次导致同一文件被改两次）。**不要**把 BDD-9 文档半误认为 fg3 批次的工作——fg3 只负责 `check-protocol-consistency.py` 代码本身和它的测试文件，不碰 `phase-cards/P2-design.md`。

### 约束
1. **双工作区纪律**：只读写 worktree，不碰主 checkout 或 `~/.agate`。
2. **只写本批次范围的测试文件**——新增一个或两个 pytest 文件（如 `agate/tests/unit/test_p2p4_boundary_docs.py`），用 Python 读取以下文档文件的文本内容，做字符串/正则断言：
   - `agate/phase-cards/P2-design.md`「gate_commands 声明」节 —— 断言含**两段**新内容：① `env_constraints` 是声明性字段、`gate_commands` 是执行机制的边界说明文字（BDD-5）；② `--strict` 不放 `&&` 链路中间的指引 + 反例（BDD-9 文档半）。两段各自独立断言，具体关键词由你根据 BDD-5/BDD-9 原文设计，不要求逐字匹配未来文案，但要能验证"结论存在"这一行为
   - `agate/assets/execution-roles/architect.md` —— 同步的边界说明段落（BDD-5）
   - `agate/phase-cards/P4-implementation.md`「自查≠gate」节（约 L44-52）—— 断言含"UI/需构建任务 P4 后应构建并确认 dist 类产物存在"的提醒条目（BDD-6）
3. **不要修改这三个协议文档本身**（那是 P4 implementer 的工作，P3 只写测试）。**不要**碰 `agate/scripts/check-protocol-consistency.py` 或其测试文件（那是 fg3 批次的范围）。
4. **红灯诚实性**：当前这些文字都不存在，测试应该真实失败（断言的关键词/段落找不到），不是语法错误或 import 失败导致的假红灯。
5. test_code_dir 声明为 `agate/tests`。

### 上游关联
P2 architect 摘要：8 候选方案（4 功能分组各 2 个），已声明 dispatch_plan（5 批 static-batch）。plan-eng-review 复评摘要：approved，本批次候选方案（仅文档新增说明，不新增 gate 脚本执行绑定）已确认无需重新设计——**注意**：BDD-5/6/9(文档半) 的验收标准是"文档能找到结论"，不是"新增自动化校验脚本"，测试设计不要越权设计成需要新脚本才能通过的形式。

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0017-toolchain-fixes/P1-requirements.md（BDD-5/6/9 原文）
- {AGATE_WORKSPACE}/tasks/TAG0017-toolchain-fixes/P2-design.md（§1.1 改什么表格中 `phase-cards/P2-design.md`/`architect.md`/`P4-implementation.md` 三行、§2.1 功能分组1候选方案、§2.3 功能分组3候选方案的文档指引部分、§6 dispatch_plan 说明「fg1-doc-boundary」行、§7 files_to_read「fg1-doc-boundary」节）
- agate/phase-cards/P2-design.md:110-146（gate_commands 声明节尾，BDD-5 与 BDD-9 两段增补落点，均属本批次）
- agate/assets/execution-roles/architect.md（grep `env_constraints` 定位现有相关段落）
- agate/phase-cards/P4-implementation.md:44-54（「自查≠gate」节现状）
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
- 环境：worktree 基线已验证（950 pytest 全绿）
- 其他 4 个批次由并行的其他 test-designer subagent 负责：fg1-parser-scripts（BDD-1/2/3/4）/ fg2-self-gate-naming（BDD-7/8）/ fg3-strict-mode-code（BDD-9 代码半：`check-protocol-consistency.py` + 其测试文件，不碰 `phase-cards/P2-design.md`）/ fg4-windows-python-probe（BDD-10/11/12）
</objective_info>
