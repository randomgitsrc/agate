---
phase: P3
generated_by: agate-inject-card.sh + 主 Agent
task_id: TAG0010-python-migration
role: test-designer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
产出 {AGATE_WORKSPACE}/tasks/TAG0010-python-migration/P3-test-cases.md（回归测试口径）+ 测试代码设计说明。本任务是 **refactor 任务**（P1 frontmatter change_type: refactor），P3 走**回归测试口径**：复用/保留既有 bats 测试，标注每条回归用例覆盖了重构涉及的哪些文件/路径；**不新增功能行为断言**（无新行为可断言）；**不跑 TDD 红灯**（测试套件本就全绿）。

### 约束
- **回归测试口径**（test-designer.md refactor 节 + P3 卡片）：P3-test-cases.md 是"回归口径声明 + 既有用例覆盖映射"，文件存在即满足 gate；不新增功能行为断言。
- **测试代码 = 既有 bats 测试的调用方式改造**（机械调用面 ~400 处 + 断言级变更 5 文件/38 用例，P1 表 D）——test-designer 的任务是设计"改造后每个 bats 文件/用例覆盖了哪个迁移后脚本"，不实际改测试代码（P4 才改）。
- **BDD 性质**：P1 的 10 条 BDD 是"关键路径行为不变断言"——测试映射这些断言，不新增功能性质 BDD。
- **受影响测试清单**（P1 表 D）：5 个断言级文件（check-platform-assumptions.bats 16 / env-adapt-docs.bats 9 / agate-scripts-encoding.bats 2 / helpers-python.bats 3 / agate-workspace-resolve.bats 10）+ 机械调用面（30 文件/379 处直接 run）+ 联动文件 40 个。
- **count-tests 口径**：`count-tests.sh`（`^@test`）用例数不减少（表 D 附录 A 对照）。
- **gate_commands.P3**（P2 固化）：`bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/`；P3_formatter: generic-tap.sh。
- 不写行首 `- PASS`/`- FAIL` 格式。

### 上游关联
- P2-design.md 已 approved：方案 A（模块化公共库 agate_common.py + 批次迁移）；gate_commands 固化；§3.6 bats 断言改动方案（5 文件断言级变更细节）；§3.2 批次 0-4 迁移方案。
- P1-requirements.md 已 approved：10 BDD + 表 D（受影响 bats 清单）。

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0010-python-migration/P1-requirements.md（BDD 验收条件 + 表 D）
- {AGATE_WORKSPACE}/tasks/TAG0010-python-migration/P2-design.md（方案 + §3.6 bats 断言改动方案 + gate_commands）
- {AGATE_WORKSPACE}/tasks/TAG0010-python-migration/P0-brief.md（任务简报）
- {project_root}/agate/tests/（按需读取受影响 bats 文件核实覆盖映射）
- {project_root}/agate/tests/helpers/fixtures.bash（detect_python/$PYTHON 约定——bats 调 py 的统一入口）

### 产出要求
P3-test-cases.md 必须含：
- Header（phase: P3 / task_id: TAG0010-python-migration / type: test-cases / parent: P2-design.md / trace_id: TAG0010-P3-20260814 / status: draft / agent: test-designer）
- `test_code_dir: P3-test-code/` 声明（或注明测试代码为既有 bats 改造，实际改动在 P4）
- 回归口径声明（refactor 任务说明）
- 既有用例覆盖映射表：每个受影响 bats 文件 → 覆盖的迁移后脚本 → 用例数（含 5 个断言级文件的逐条映射）
- BDD 映射表：P1 的 10 条 BDD → 对应既有 bats 用例（哪些用例验证哪条 BDD）
- 批次对应：表 E 批次 0-4 → 每批验证的 bats 文件清单
- 用例数增减对照（count-tests 不减少的保证方式）
</dispatch_guide>

<!-- AGATE_CARD_START -->
## 当前阶段卡片：P3

路径：phase-cards/P3-tdd.md
---
# P3 — TDD 测试设计

> 当前状态：[首次 / 重试 #N / 裁剪跳阶]
> 裁剪跳阶 → 确认 P1 phases 不含 P3 + 有合规理由（risk=low + 跳过风险已声明）→ 跳过，读 P4 卡片

## 如果是首次进入本阶段

0. 跑 `agate-capture-env-baseline.sh $TASK_DIR`（自动捕获环境基线）。**必须执行**。
   该步骤不阻塞流程——脚本的 stderr 输出（含 WARNING）均可忽略，执行完直接继续步骤 1。
1. 派发 test-designer subagent → 产出 P3-test-cases.md + 测试代码目录
   1.1 写 P3-dispatch-context-test-designer.md（派发指引：目标/约束/上游关联/输入文件 + 客观查证信息）
2. 主 Agent 跑 check-tdd-red.sh 确认红灯
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

**check-gate.sh P3**（hook + 主 Agent 预跑，秒级文件检查）：
- exit 1：P3-test-cases.md 不存在
- exit 2：P3-test-cases.md 存在（TDD 红灯由 check-tdd-red.sh 独立确认）

**check-tdd-red.sh**（主 Agent 手动确认红灯 + CI backstop P3 兜底）：

```bash
check-tdd-red.sh $TASK_DIR
```

- **exit 0**：真红灯（assertion 失败 / 项目内 import 失败 = B类错误）— 测试正确但因实现未写而失败
- **exit 1**：假红灯（SyntaxError / 第三方 import 失败 = A类错误）— 测试代码自身错误
- **exit 2**：绿了 — 实现先于测试，违反 TDD
- **exit 3**：无可用测试运行器

**技术栈无关**：check-tdd-red.sh 通过 formatter 将测试输出标准化为 JSON，不直接解析任何框架的输出格式。formatter 在 gate_commands.P3_formatter 中声明（可选）。不提供 formatter 时退化为 exit-code-only（所有红灯 = 可推进）。

**探测链**：`$TEST_RUNNER` 环境变量 → `gate_commands.P3`（P2-design.md 声明）→ `which pytest` → exit 3。`$TEST_RUNNER` 始终优先（退化为 exit-code-only，无 formatter）。

**formatter 选择**：见 `assets/formatters/README.md` 速查表。常用：pytest → `pytest.sh`，vitest → `vitest.sh`，go test → `go-test.sh`，其他 → `generic-exit-only.sh`。

## 按包拆分并行（条件触发，非强制）

> 仅当 P2 packages > 1 且包间无依赖时适用。单包任务跳过本节。

当 P2 声明多个 packages 且包间无数据依赖时，P3 可拆分并行：

1. 每个 package 派一个 test-designer subagent
2. 各自写各自的测试文件（不同目录）
3. 各自返回路径 + 摘要
4. 主 Agent 汇总后统一 commit

拆分判据：
- P2 packages > 1 且包间无数据依赖 → 可并行
- 单包或包间有依赖 → 串行（不拆分）
- P2 未声明 packages → 串行

每个 subagent 的 dispatch-context 必须明确其负责的 package 范围（约束节写"只写 {pkg} 目录下的测试"）。

## 推进条件（全部满足才写 phase: P4）

- [ ] check-tdd-red.sh exit 0（真红灯确认）
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
- 测试基线：733 bats 全绿（58 文件/727 @test）+ consistency 0 ERROR（--strict）
- 机械调用面：30 个 bats 文件 / 379 处直接 run（AGATE_SCRIPTS 314 + AGATE_ROOT/scripts 65）
- 断言级文件：check-platform-assumptions.bats 16 / env-adapt-docs.bats 9 / agate-scripts-encoding.bats 2 / helpers-python.bats 3 / agate-workspace-resolve.bats 10（合计 40 用例——P1 表 D 记 38 系版本差异，以实测为准）
- 环境：Linux；python3 3.12.3 + pyyaml 6.0.3 + ruff 0.16.3；bats 1.10.0
- worktree 根：/home/kity/oclab/agate/.worktrees/agate-TAG0010（改造对象）；~/.agate = 稳定版 v0.45.0（禁止改动）
</objective_info>
