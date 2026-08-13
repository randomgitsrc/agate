> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。

---
phase: P3
generated_by: agate-inject-card.sh + 主 Agent
task_id: TAG0005
role: test-designer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

产出 `P3-test-cases.md` + 为 6 处修复写**先红后绿**的 bats 测试（写进既有 `agate/tests/unit/` 测试文件），每条 BDD-NN 对应一个测试用例（1:1 映射，测试名引用 BDD 编号）。当前实现未修 → 测试必须红灯。

### 约束

- **测试范围**（P2-design.md 已锁定，6 处修复 + 对应测试文件）：
  1. **RM-AG0011**（BDD-3/4/5）：`agate/tests/unit/agate-gate-p5-count.bats` 改断言 `3`→`1 2`（GPC.1）、`0`→`0 0`（GPC.2），**新增 GPC.3**（块含 P5+P5_formatter → `1 0`，锁定 aux 排除 `_formatter`——P2-review NB 测试缺口）；`agate/tests/unit/check-gate.bats` G5_CMD.1/G5_CMD.5 断言改「1 个主命令 + 1 个辅助命令（共 2 条…）」；G5_CMD.2（仅 P5 不 WARNING）保持
  2. **RM-AG0012①**（BDD-7/8）：`agate/tests/unit/agate-render-dispatch-prompt.bats` 新增 RP.18（execution 角色渲染不含「Review 角色特别指令」）+ RP.19（review 角色渲染含该节 + approved/rejected/needs-revision 完整语义）
  3. **RM-AG0012②**（BDD-10/11）：同文件新增 RP.17（角色不存在 → exit 2 + stderr 含「角色文件不存在」）
  4. **BDD-16**：`agate/tests/unit/agate-debt-check.bats` 新增用例（临时脚本目录仅放 check-debt.sh 无 agate-workspace-resolve.sh → exit 2 + stderr 含「缺少 agate-workspace-resolve.sh」）
  5. **RM-AG0010（BDD-1/2）/ RM-AG0003（BDD-12/13/14）/ BDD-9/BDD-15**：纯文档改动——测试形式为**文本断言**（如 `grep -q 'plan-eng-review' 三处 C8 表文件` / `grep -q '自动重试一次' dispatch-protocol.md` / `rg -l 'Review 角色特别指令' agate/` 仅命中模板单文件 / `rg -n '>&2;\s*exit 0' agate/scripts/*.sh` 仅剩「跳过」语义）。这些断言当前**失败**（修复前文本不存在），满足红灯。写入 `agate/tests/unit/` 对应测试文件或新增。**注意：BDD-1/2/12/13/14/9/15 的断言是文档文本 grep，属自写断言——须在 P3-test-cases.md 标注「文档断言」区分脚本断言。**
- **TDD 纪律**：所有断言针对「修复后」状态——修复前必须红。不要写「现在就能过」的用例。
- **test_code_dir**：本任务测试直接写进既有 `agate/tests/unit/`（P3-test-cases.md 声明 `test_code_dir: agate/tests/unit/`），不另建 P3-test-code/ 目录（遵循既有测试布局，不产生新目录）。
- **测试命名**：测试名引用 BDD 编号（如 `bdd-3 p5-count 主/辅双值`）。
- **P2-review NB 已吸收**：GPC.3（formatter 排除）必须写；BDD-9 P6 判定用 `rg -l`（单文件）——测试断言按此写。
- **格式约束**：约束节避免行首 `- PASS`/`- FAIL`（provenance 预检检测）。
- **不修改被测脚本**（那是 P4 的事）——只写测试 + P3-test-cases.md。

### 上游关联

- `P2-design.md`（方案，§2.1-2.6 测试落实点 + §3 gate_commands + §7 完成标准）
- `P1-requirements.md`（16 BDD 验收条件）
- `P2-review.md`（approved + NB 测试缺口）

### 输入文件

- `agate-workspace/tasks/TAG0005-mechanism-fixes/P2-design.md`（方案 + 测试落实点）
- `agate-workspace/tasks/TAG0005-mechanism-fixes/P1-requirements.md`（BDD）
- `agate-workspace/tasks/TAG0005-mechanism-fixes/P2-review.md`（NB 测试缺口）
- 测试文件（改断言/新增用例）：
  - `agate/tests/unit/agate-gate-p5-count.bats`
  - `agate/tests/unit/check-gate.bats`（G5_CMD.1/.5，约 L606-704）
  - `agate/tests/unit/agate-render-dispatch-prompt.bats`
  - `agate/tests/unit/agate-debt-check.bats`（约 L428-534）
- 被测脚本（读现状，不修改）：
  - `agate/scripts/agate-gate-p5-count.py`、`agate/scripts/check-gate.sh`（L249-258）、`agate/scripts/agate-render-dispatch-prompt.sh`（L63-69）、`agate/scripts/check-debt.sh`（L21-30）
- `{agate_root}/assets/execution-roles/test-designer.md`（角色定义）
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
- 环境状态：worktree `/home/kity/oclab/agate/.worktrees/agate-TAG0005-0009`；协议 v0.44.0 基线；714 bats 全绿；P1/P2 已 commit
- 测试运行：bats 1.10；单脚本跑法 `bats agate/tests/unit/<file>.bats`
- 现有测试计数：agate-render-dispatch-prompt.bats 17 @test（README 记 16，有 1 既有漂移）；新增 RP.17/18/19 后实际 20
- RM-AG0012② 已修复（exit 2）——RP.17 用「现有实现断言」即红→绿反转不明显，但仍是必要回归锁；其余断言修复前均红
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
