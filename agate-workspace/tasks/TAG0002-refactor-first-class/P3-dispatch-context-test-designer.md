---
phase: P3
generated_by: agate-inject-card.sh + 主 Agent
task_id: TAG0002
role: test-designer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
产出 docs/tasks/TAG0002-refactor-first-class/P3-test-cases.md + 测试代码（原位写在 worktree `agate/tests/` 下）。本任务是 **refactor 一等任务**：测试设计为**回归测试口径**（复用既有用例、不新增功能行为断言）——见 P1 BDD-8 与 P2 方案。

### 约束
- 本任务是 **agate 协议自身改造**（dogfooding）：改造对象是 worktree `agate/` 目录（已含 TAG0003 工作区架构改动），`~/.agate` 是稳定版 v0.40.2 开发工具（禁止改动）。测试代码写进 worktree 的 `agate/tests/`（原位）。
- **refactor 任务 TDD 语义（P2 方案确认）**：refactor 无新功能行为断言，**不适用 TDD 红灯**——P3 产出回归测试用例（复用/扩展既有用例覆盖新机制），P3 gate 跳过 check-tdd-red（CI backstop 也 refactor 感知跳过）。
- **test_code_dir 声明**：P3-test-cases.md 必须声明 `test_code_dir: agate/tests/`——P2 gate_commands.P3 固化指向 `bats agate/tests/unit/check-gate.bats`（+ 相关新增测试文件），测试代码必须落在既有 tests 树内。
- **P3 范围（P2-design.md §1.1/§5 明确）**：
  1. **新增/扩展** `agate/tests/unit/check-gate.bats` 相关用例：check-gate.sh P6 分支按 change_type 分流（refactor → 回归口径判定；功能 → 现 BDD 计数判定）
  2. **新增** 覆盖 P1-requirements frontmatter `change_type` 字段解析/校验的用例（若 P2 设计了校验逻辑）
  3. **新增/扩展** P6 refactor 口径验收记录格式用例（regression_pass + regression.log 双证）
  4. 其他 P2 §5 gate_commands.P3 指向的测试文件
- **不做**（P4 实现期做）：check-gate.sh / phase-cards 的实际改动；既有用例大范围重写。
- BDD→测试 1:1 映射：每条 `#### BDD-NN`（8 条）对应一个测试（回归口径下测试验证"新机制存在且行为正确"）；测试名引用 BDD 编号（如 `test_bdd_6_p6_gate_refactor_split`）。
- P6 BDD 二值规则：设计的测试必须产出明确 PASS/FAIL，不支持中间态。
- 测试输出须可被 `bats --formatter tap` 解析。
- 禁止行首 `- PASS` / `- FAIL` 格式（provenance 审计拦截）。

### 上游关联
- P2 已通过（plan-eng-review approved）：方案 change_type 入 P1 frontmatter + P6 gate 分流回归口径（regression_pass+regression.log 双证）+ P3 refactor 跳过 TDD 红灯 + ci-gate-backstop refactor 感知（SCOPE+）。
- P2 gate_commands.P3（固化）：`bats agate/tests/unit/check-gate.bats`（+ 设计新增测试文件）。
- P1 基线：8 条 BDD（BDD-1..8），risk_level=medium。
- 1 项 SCOPE+ 已在 P1 scope_resolved 回补（ci-gate-backstop refactor 感知）。

### 输入文件
- docs/tasks/TAG0002-refactor-first-class/P2-design.md（方案设计 + gate_commands + files_to_read——**必读**）
- docs/tasks/TAG0002-refactor-first-class/P1-requirements.md（8 条 BDD——**必读**，测试主要来源）
- docs/tasks/TAG0002-refactor-first-class/P0-brief.md（任务简报与风险声明——必读）
- AGENTS.md（项目约定：测试约定、helpers、CI——必读）
- agate/tests/ 现有测试结构（参照 fixtures.bash / load.bash / 既有 .bats 风格——按需读取）
- agate/scripts/check-gate.sh P6 分支现状（待测逻辑——按需读取）
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
3. 更新 .state.yaml phase=P3 → P4
4. git add docs/tasks/{Txxx}/（含 .state.yaml + 产出文件，若 .gitignore 忽略需 git add -f）
5. git commit -m "wf({Txxx}-P3): {摘要}"

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
- 环境状态：worktree 是改造对象（分支 dev/workspace，HEAD=TAG0002-P2 commit）；`~/.agate` → 主 checkout 是稳定版 v0.40.2 开发工具（禁止改动）。
- 测试基线：worktree 全量 bats 631 用例全绿（TAG0003 后）；count-tests.sh 基线 625 + sanity 6。
- 测试框架：bats 1.10.0；helpers：load.bash / fixtures.bash / git-helper.bash；CI 里 ~/.agate 软链不存在，load.bash 通过 BATS_TEST_DIRNAME 反推 AGATE_ROOT。
- 已核实查证：check-gate.sh P6 分支（L292 附近）现为 BDD 计数 + 证据目录检查；P1-requirements frontmatter 已加 change_type 字段体系（P2 设计）；ci-gate-backstop.py P3 分支（L109-139）无条件重跑 check-tdd-red（SCOPE+ 要改）。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
