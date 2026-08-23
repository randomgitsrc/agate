# P3-dispatch-context-test-designer — TAG0023 测试设计（TDD 红灯）

> 派发对象：test-designer（P3 TDD 测试设计）。这是本轮的强制指令，不是参考信息。
> 任务目录：`{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/`
> 单包任务（`packages: [agate]`），不做「按包拆分并行」，串行单次派发；测试文件组织按 P2 `dispatch_plan` 的 5 批分组，便于 P4 各批实现独立跑各自测试。

## 目标

产出 `P3-test-cases.md` + `P3-test-code/` 测试代码，覆盖 P1 全部 BDD-1..13（1:1 映射），当前**必须全部红灯**（真红灯：assertion 失败/项目内 import 失败，不是语法错误）。

## 约束（硬约束）

1. **每条 `#### BDD-NN` 对应一个测试用例**，测试函数名引用 BDD 编号（如 `test_bdd_1_...`），按 P2-design.md §4「完成标准」表的具体判据设计断言（不是重复 BDD 原文，是断言到函数/命令级）
2. **按批次组织测试文件**（对应 P2 `dispatch_plan` 5 批，便于 P4 各批独立验证）：
   - batch A（BDD-1~4，RM-AG0042）：`test_check_state_transition_retries.py`（新文件，或追加到现有 `test_check_state_transition.py`，由你决定但需在 P3-test-cases.md 说明理由）
   - batch B（BDD-5~7，RM-AG0043）：追加到 `test_check_gate.py`（现有文件已有 P8 相关用例，参照其风格）
   - batch C（BDD-8~10，RM-AG0044）：追加到 `test_agate_debt_check.py`（`test_bdd_14` 所在文件）+ 新建 `agate/tests/unit/test_env_sensitive_tests_registry.py`（BDD-10 清单文件存在性）
   - batch D（BDD-11~13，RM-AG0045）：新建或追加到合适的测试文件，覆盖 `agate-frontmatter-check.py` 错误消息增强 + `dispatch-prompt.md` 新增小节文本存在性
3. **BDD-1 是 WARNING 级（非阻断）**：测试断言应为"命中场景时 stderr 含 WARNING 文本，exit code 不为非0拦截值"（不是断言 exit 1），且必须包含 P2-design.md 中 review 要求的负面测试锚点——用真实历史样本 `agate-workspace/archived/tasks/T001-v2.0-structured/P4-dispatch-context-implementer-review-fix-retry1.md` 的文件名模式构造"不得误命中"的回归用例
4. **BDD-8 是"文档四要素齐全"判据**（不是代码断言）：P2-design.md 本身 + 待新建的 `agate/tests/ENV-SENSITIVE-TESTS.md` 共同构成判据，测试用例可以是一条轻量断言（检查 `ENV-SENSITIVE-TESTS.md` 存在 + 含指定字段），不需要复杂逻辑
5. **BDD-9（连续5次CI稳定）不是 P3 单元测试能覆盖的**——P3 阶段该 BDD 对应的"测试用例"可以是一条占位声明（在 P3-test-cases.md 里说明"此 BDD 由 P6 阶段的 CI 触发验证覆盖，P3 不提供单元测试，理由：环境级验收锚"），不要为了凑数造一个假测试
6. **BDD-7（RM-AG0032 历史补记）不是代码逻辑**——测试用例可以是一条轻量断言（`grep "RM-AG0032" roadmap.md | grep done` 非空），但当前尚未补记（P8 阶段才做），所以**当前这条测试也应该是红灯**（断言失败，因为 roadmap.md 还没有这行）
7. **环境**：Linux；`/tmp` 只读——pytest 必须 `--basetemp=/home/kity/oclab/dsh-workspace/ptmp -p no:cacheprovider`；双工作区纪律（只改 worktree `agate/`）
8. **不要实现任何生产代码**——本阶段只写测试，测试针对的函数/文件此时大概率不存在或行为未变（这正是红灯的来源）

## 上游关联

- `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P1-requirements.md`（BDD-1..13 原文）
- `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P2-design.md`（**主要输入**：§4 完成标准表逐条判据 + §5 files_to_read + dispatch_plan 5 批）
- `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P2-review.md`（评审确认的 D1-D6 决策，尤其 BDD-1 WARNING 降级 + 负面测试锚点要求）

## 输入文件（逐一读，每读完追加 progress）

1. `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P1-requirements.md`
2. `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P2-design.md`（重点 §4 完成标准表 + §5 files_to_read）
3. `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P2-review.md`
4. `{agate_root}/assets/execution-roles/test-designer.md`（角色定义）
5. `{agate_root}/phase-cards/P3-tdd.md`（本阶段卡片）
6. 现有测试文件参照风格：`agate/tests/unit/test_check_state_transition.py`、`agate/tests/unit/test_check_gate.py`、`agate/tests/unit/test_agate_debt_check.py`（含 `test_bdd_14`）
7. 现状代码（理解当前行为，判断红灯从哪来）：`agate/scripts/check-state-transition.py`、`agate/scripts/check-gate.py`（`gate_p8`）、`agate/scripts/check-debt.py`（`_retreat_coverage`）、`agate/scripts/agate-frontmatter-check.py`
8. `agate-workspace/archived/tasks/T001-v2.0-structured/P4-dispatch-context-implementer-review-fix-retry1.md`（BDD-1 负面测试锚点样本）

## 验证命令

```bash
python3 -m pytest agate/tests/ -q -p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp
```

## 产出

- `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P3-test-cases.md`（含 `test_code_dir:` 声明，指向 `agate/tests/unit/`，因为本任务测试追加到既有目录而非新建独立目录——请在文件中说明这个映射关系：13 条 BDD → 具体测试函数名 → 所在文件）
- 测试代码直接写入 `agate/tests/unit/` 对应文件（追加或新建，见约束 2）

## 门槛（什么算完成）

- 13 条 BDD 全部有对应测试用例（BDD-9 除外，允许占位声明说明由 P6 覆盖）
- `check-tdd-red.py` 对新增测试确认真红灯（B类错误：assertion失败/项目内import失败），不是语法错误（A类）
- P3-test-cases.md 含 `test_code_dir:` 声明 + BDD↔测试函数映射表

## 返回给我

只返回两行：① 产出文件路径；② 一句话摘要（N 条测试用例，当前红灯，≤30字）。绝不返回文件全文。

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
