---
phase: P3
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0031
role: test-designer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）
> 本次是并行拆批之一（batch id: test-isolation，P2 dispatch_plan 声明的三簇之一）。只负责本簇的测试用例，不要写其他簇（版本管理域/check-gate.py 健壮性）的测试。

### 目标
为「测试隔离」簇（DEBT0007）写测试用例，产出 `P3-test-cases-test-isolation.md` + 对应测试代码/断言。覆盖 BDD-6/7。**本簇特殊性**：`_staged_source_count` 的隔离修复已由 TAG0024（commit `e2357fc`）落地，本簇**不改生产代码**，只需（a）确认既有 4 个用例仍稳定 PASS（BDD-6，验证性质，非新写红灯测试）（b）为 debt 登记闭合动作准备一个可判定的验证点（BDD-7，检查 `debt/tech-debt.md` DEBT0007 状态字段）。

### 约束
- **BDD-6 不是传统 TDD 红灯**：`test_p2_6e_prune_p7_coupling_checklist_exit_0` / `test_p2_52_yaml_list_phases_exit_0` / `test_p2_52b_yaml_list_phases_p3_pruned_low_exit_0` / `test_p2_6f_staged_source_count_uses_task_repo_not_outer_cwd_repo_exit_0` 四个用例已存在且已绿（TAG0024 已修复）。你的任务是**确认它们仍绿**并在 `P3-test-cases-test-isolation.md` 里明确记录"此四例现状已绿，本次不新增红灯测试，验证动作见 P5/P6 证据"——不要为了凑"红灯"人为改坏这些已有测试。
- **BDD-7 的验证点**：`debt/tech-debt.md` 当前 DEBT0007 `status: open`（红），P4 实现阶段改为 `status: closed`（绿）后才算完成——这是**真正可做红灯的部分**。设计一个简单断言（可以是 pytest 用例读 `debt/tech-debt.md` grep `DEBT0007` 后续的 `status:` 字段，或者是一条明确写在 `P3-test-cases-test-isolation.md` 里的人工核对步骤 + grep 命令），当前状态断言应为 FAIL（因为 status 仍是 open），P4 改完后应为 PASS。
- **不要重复 TAG0024 已做的工作**：不新增 `_staged_source_count` 相关的生产代码修复，也不要重写已有的 4 个测试用例本体（除非发现它们其实不稳定，若发现异常立即在 progress 里记录并停下报告主 Agent，不要自行"修复"）。
- **test_code_dir 声明**：`agate/tests/unit/test_check_pruning.py`（既有文件，仅新增一条可选的确认性断言/或不改代码只在 P3-test-cases 里记录验证步骤）+ 若需要写 debt 登记状态检测的独立小测试，放在 `agate/tests/unit/` 下新文件（如 `test_debt_registry_closure.py`，若判断没必要写成 pytest 用例，可用文档化的 grep 命令代替，在文件里说明理由）。

### 上游关联
- P2 architect 方案（approved，2 轮）：影响面梳理明确"簇 B 不改产出代码，仅验证 + 登记"
- P1 requirements-review 已核实 DEBT0007 的 P0_STALE 判定（TAG0024 e2357fc 已修复生产代码，本任务范围收窄为验证 + 登记闭合）

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0031-debt-cleanup/P2-design.md（§1.1 簇 B 改动点表 + §4 files_to_read 簇 B 部分）
- {AGATE_WORKSPACE}/tasks/TAG0031-debt-cleanup/P1-requirements.md（BDD-6/7 原文 + P0_STALE 节）
- /home/kity/oclab/agateon/.worktrees/agate-TAG0031/agate/scripts/check-pruning.py（L60-100，`_staged_source_count` 现状实现）
- /home/kity/oclab/agateon/.worktrees/agate-TAG0031/agate/tests/unit/test_check_pruning.py（L214-420，四个既有回归用例）
- /home/kity/oclab/agateon/.worktrees/agate-TAG0031/agate-workspace/debt/tech-debt.md（DEBT0007 条目 + DEBT0005/DEBT0006 已 closed 条目的登记格式先例）
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
- 环境状态：worktree 分支 feat/TAG0031-debt-cleanup，Python 3.12.3 + pytest 9.0.3
- 关键标识：四个既有用例的精确名称见「约束」节第一条；`AGATE_WORKSPACE`/debt 路径为 `{AGATE_WORKSPACE}/debt/tech-debt.md`（非项目根 `debt/`）
- 查证结果：主 Agent 曾实测 `pytest -k "test_p2_6e_... or test_p2_52_... or test_p2_52b_... or test_p2_6f_..."` 4 项全部 PASS（P1 阶段核实），本轮请你自行复跑一次确认现状未变
</objective_info>
