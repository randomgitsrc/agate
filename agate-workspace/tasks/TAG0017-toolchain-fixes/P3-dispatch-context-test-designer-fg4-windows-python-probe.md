---
phase: P3
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0017-toolchain-fixes
role: test-designer
batch: fg4-windows-python-probe
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令。本次是**批次化并行派发**之一（P2 dispatch_plan 5 批之一），你只负责 `fg4-windows-python-probe` 批次范围，不要碰其他批次的文件。

### 目标
为 P1 的 BDD-10/11/12（DEBT0014：3 个 hook 薄壳探测循环增强 + Windows 已知限制文档化）写测试。核心行为：① 探测循环命中不可执行候选时能跳过并继续探测下一候选（BDD-10）；② `AGATE_PYTHON` 显式指定可跳过整个探测循环（BDD-11）；③ 文档含 Store 占位符说明且不夸大"已实测通过"（BDD-12，文档断言型）。

### 约束
1. **双工作区纪律**：只读写 worktree，不碰主 checkout 或 `~/.agate`。**诚实边界（P0-brief 约束 3）**：本环境是 Linux，无法真实触发 Windows Store 占位符，测试必须用**模拟 stub**（构造一个 exit 非零的假 python3 可执行文件）复现"候选不可执行"场景，不得声称测试"验证了真实 Windows 行为"。
2. **只写本批次范围的测试文件**：
   - 新增/扩展 `agate/tests/integration/test_pre_commit_hook.py`（及同构的 pre-push/commit-msg 集成测试，参照该文件已有的 PATH 操作用例风格）：
     - BDD-10 用例：在临时 PATH 中放置一个"不可执行的 python3 stub"（脚本体非零 exit，模拟 Store 占位符）+ 一个"可用的 python stub"（脚本体正常退出），验证探测循环最终解析到可用的 python，而不是在不可执行候选处直接失败
     - BDD-11 用例：设置 `AGATE_PYTHON` 环境变量指向一个显式路径，验证薄壳直接使用该路径、不执行探测循环（不受 PATH 上其他 stub 干扰）
     - 3 个 hook 薄壳（`pre-commit-gate.sh`/`commit-msg-self-gate.sh`/`pre-push-gate.sh`）结构完全一致，用例应能验证三者行为一致（可以是同一组用例参数化跑三个脚本，或至少各自跑一遍，不要只测 1 个当代表）
   - 新增一个 pytest 文件（如 `agate/tests/unit/test_windows_python_probe_docs.py`）读取 `agate/platform-notes.md`（「已知限制（Windows 原生）」表 + 「Windows 原生」章节，约 L140-170）与 `AGENTS.md`（「Gate 脚本分层」节，约 L40-43）的文本内容，断言：① 含 Store 占位符现象说明；② 含 `AGATE_PYTHON` 机制说明；③ **不含**"已在 Windows 实测通过"一类断言字符串（BDD-12 的诚实性要求本身就是可测试的负面断言）
3. **不要修改** 3 个 hook 薄壳、`platform-notes.md`、`AGENTS.md` 本身（那是 P4 implementer 的工作，P3 只写测试）。
4. **红灯诚实性**：当前薄壳探测循环无可执行性小测试、无 `AGATE_PYTHON` 支持，测试应该真实失败；文档断言测试当前也应真实失败（对应文字尚不存在）。
5. test_code_dir 声明为 `agate/tests`。

### 上游关联
P2 architect 摘要：8 候选方案（4 功能分组各 2 个），已声明 dispatch_plan（5 批 static-batch）。plan-eng-review 复评摘要：approved，本批次候选方案（`AGATE_PYTHON` 显式覆盖 + 探测循环候选可执行性小测试，通用 exit code 判据而非精确 49）已确认无需重新设计。minimal_validation 已用模拟 stub 验证该判据逻辑可行（见 P2-design.md §8），P3 测试设计可参照该验证脚本的结构。

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0017-toolchain-fixes/P1-requirements.md（BDD-10/11/12 原文）
- {AGATE_WORKSPACE}/tasks/TAG0017-toolchain-fixes/P2-design.md（§1.1 改什么表格「3 个 hook 薄壳」「platform-notes.md」「AGENTS.md」相关行、§2.4 功能分组4候选方案、§7 files_to_read「fg4-windows-python-probe」节、§8 minimal_validation 中 DEBT0014 那条的模拟 stub 验证方法，可直接参照复用测试结构）
- agate/scripts/pre-commit-gate.sh（全文，约 25 行，探测循环现状）
- agate/scripts/commit-msg-self-gate.sh、agate/scripts/pre-push-gate.sh（全文，同结构确认）
- agate/tests/integration/test_pre_commit_hook.py（现有 PATH 操作/探测相关用例风格，grep `PATH` 定位）
- agate/platform-notes.md:140-170（已知限制表 + Windows 原生章节现状）
- AGENTS.md:38-43（Gate 脚本分层节现状）
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
- 其他 4 个批次由并行的其他 test-designer subagent 负责：fg1-parser-scripts（BDD-1/2/3/4）/ fg1-doc-boundary（BDD-5/6/9文档半）/ fg2-self-gate-naming（BDD-7/8）/ fg3-strict-mode-code（BDD-9代码半）
</objective_info>
