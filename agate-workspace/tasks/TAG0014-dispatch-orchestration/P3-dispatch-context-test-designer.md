---
phase: P3
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0014
role: test-designer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

产出 P3-test-cases.md + 测试代码：为 TAG0014「agate 派发编排机制」写 TDD 红灯测试。测试当前必须失败（实现未写），证明真的在测目标功能。

### 约束

- **TDD 顺序**：只写测试，不写实现。测试当前必须红灯（check-tdd-red.py 判定）。
- **测试范围（P2-design §2.1 与 §3.1 已定死）**：
  1. 新建 `agate/tests/unit/test_dispatch_orchestration.py` — **8 条用例**（5 正向 + 3 负向）：
     - `test_dispatch_plan_required_fields`：含 `dispatch_plan:` 时 op 返回 JSON 含 mode 且 mode ∈ 枚举；parallel_limit 存在时 ≥ 1
     - `test_dispatch_plan_mode_valid`：mode 非法值（如 `xyz`）→ P2 gate 报 ERROR exit 1
     - `test_dispatch_plan_batch_granularity`：static-batch/parallel 模式，batches 存在时各 batch 含 id + complexity 且 complexity ∈ {low, medium, high}；模式 1/5 可无 batches
     - `test_dispatch_plan_parallel_limit`：static-batch/parallel 模式 batch 数 ≤ parallel_limit（默认 3）
     - `test_dispatch_plan_optional`：无 `dispatch_plan:` 时 P2 gate 行为等同现状（exit 2 通过，无额外输出）——含"等同现状"断言（比较有无该字段时的输出）
     - `test_dispatch_plan_malformed_yaml`：frontmatter 含 `dispatch_plan:` 但 YAML 解析失败 → 不误拦（按缺字段处理），且不崩溃
     - `test_dispatch_plan_parallel_limit_zero`：parallel_limit=0 → 报 ERROR（非法，至少 1）
     - `test_dispatch_plan_batch_missing_complexity`：batch 缺 complexity → 报 ERROR
  2. 修改 `agate/tests/unit/test_agate_md_field_get.py` — **+2 条 op 层用例**（S2 主张，P2-design §2.1 已纳入）：
     - op `dispatch_plan` 注册入 KNOWN_OPS：`agate-md-field-get.py dispatch_plan` 对含 flow YAML 的 P2 文件输出合法 JSON（含 mode）
     - dict → json.dumps 输出路径：输出是合法 JSON（非 Python repr 单引号）
- **测试实现方式**：
  - 参照 `agate/tests/conftest.py` 的 fixture 模式（`add_p2_candidate_count` / `add_p2_review`，L213-227）
  - 参照 `agate/tests/unit/test_check_gate.py` 的 `_write_p2_design` + `_run_gate` P2 测试 fixture 模式（L220-272）
  - 参照 `agate/tests/unit/test_agate_md_field_get.py` 的 `_run_mdf` 封装模式（L10-16）
  - **测试平台无关原则（agate 测试核心约束）**：不得裸 `PATH="/usr/bin:/bin"`、不得裸 `python3`（应探测 `python3|python`）、不得假设 /tmp 等 Unix-only 路径、不得假设 POSIX symlink 语义。临时文件用 pytest `tmp_path` fixture。
- **BDD 追溯**：8 条用例对应 P1 BDD-19（+ BDD-1~7 覆盖）；op 层 2 条对应 BDD-1。测试名引用 BDD 编号或语义。
- **红灯预期**：字段契约未实现——`agate-md-field-get.py` 无 dispatch_plan op（KNOWN_OPS 未注册 → exit 2 "unknown op"）、check-gate P2 不读此字段。test_dispatch_orchestration.py 会红灯（断言失败/import 失败 = B 类）。**注意：test_agate_md_field_get.py 新增 2 条也会红灯**（op 未注册）。
- **P3-test-cases.md 必须声明 `test_code_dir: agate/tests/unit/`**（测试代码写到项目测试目录，不是 task 目录下）。
- **不写实现代码**：不得修改 agate/scripts/agate-md-field-get.py / check-gate.py。
- **输出路径硬约束**：
  - P3-test-cases.md → {AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/P3-test-cases.md
  - 测试代码 → {project_root}/agate/tests/unit/test_dispatch_orchestration.py（新建）+ {project_root}/agate/tests/unit/test_agate_md_field_get.py（追加）

### 上游关联

- P1-requirements.md：22 条 BDD；BDD-19（8 条 = 5 正向 + 3 负向，与 plan Task 1 完全一致）
- P2-design.md：§2.1 测试设计、§3.1 测试层映射、minimal_validation 已验证 op 路径可行、files_to_read 含测试参照文件
- approved plan：Task 1 测试清单（8 条 + 负向 3 条定义逐字）

### 输入文件

- {AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/P1-requirements.md（BDD 验收条件）
- {AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/P2-design.md（方案：§2.1 测试设计 + §3.1 映射 + gate_commands）
- {AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/P0-brief.md（任务简报与风险声明）
- {AGATE_WORKSPACE}/plans/agate-dispatch-orchestration-20260815.md（Task 1 字段契约 + 测试清单）
- {project_root}/AGENTS.md（测试约定：平台无关原则、fixture、tmp_path、TEST_RUNNER mock）
- {project_root}/agate/assets/execution-roles/test-designer.md（角色定义）
- 测试参照文件：agate/tests/conftest.py、agate/tests/unit/test_check_gate.py、agate/tests/unit/test_agate_md_field_get.py
- 被测对象（只读理解接口）：agate/scripts/agate-md-field-get.py、agate/scripts/check-gate.py
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
- 环境：pytest 9.0.3；系统 python3 可用；test runner 无 formatter（env baseline 已跑，放弃捕获不阻塞）
- 基线：count-tests.sh 实测 770（P2 minimal_validation ⑦）
- 现状代码：agate-md-field-get.py 的 KNOWN_OPS 未含 dispatch_plan（实测 exit 2 "unknown op"）；_format_value 对 dict 走 str() repr（非 JSON）——两条现状都是本任务要改的红灯基础
- gate_commands.P3 = "python3 -m pytest agate/tests/unit/test_dispatch_orchestration.py agate/tests/unit/test_agate_md_field_get.py -q --tb=no"
- 测试平台无关：Linux 全量覆盖，Windows 冒烟由 CI 兜底；本任务新增测试不得引入 Unix 假设
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
