---
phase: P3
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0024
role: test-designer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
产出批次 `phases-yaml-consistency`（P2-design.md dispatch_plan 第 3 批，complexity: low）的测试设计：为 P1-requirements.md 的 BDD-25~29（RM-AG0049 phases.yaml P4 outputs 补全 + RM-AG0050 P6.5 口径统一 + 跨 issue 约束）追加测试用例，TDD 红灯。

### 约束
- **只写本批次范围**：在 `agate/tests/unit/test_check_structure_consistency.py`（若不存在则于既有 S-3 相关测试文件新建/追加，见 files_to_read 确认实际文件名）追加测试。不要碰 `test_agate_md_field_set.py` 或 `test_check_gate.py`（另两批次负责）——P2 review 已确认 RM-AG0049 相关用例全部落在本文件，与其余两批次零交叉
- **红灯性质**：`phases.yaml` 当前 P4 `outputs` 未列 `P4-review.md`——新增测试断言"P4 outputs 声明包含 P4-review.md"，在当前 phases.yaml 下必须真实断言失败（B 类真红灯）
- **BDD-25（P4 outputs 补全）测试**：读取 `agate/rules/phases.yaml`，断言 `id: P4` 的 `outputs` 列表含 `{file: P4-review.md, required: true, status_field: status}`（或等价字段存在性判断）
- **BDD-26（S-1/S-2 一致性不变）测试**：断言 `check-structure-consistency.py` 全量跑 S-1~S-6 在补全 outputs 后仍 0 mismatch（可用子进程调用实际脚本或直接调用其内部校验函数，参照该脚本既有测试写法）
- **BDD-27（phases.yaml 与 state-machine.md 表述口径一致）测试**：这是文档措辞一致性断言，可设计为读取两份文件中 P6.5 相关的关键表述片段，断言不再存在"独立阶段"与"强门槛子阶段，非独立 phase 值"两种矛盾说法共存（用关键字符串存在性/不存在性断言，不强求语义解析）
- **BDD-28（既有判定行为不变）测试**：断言 `check-gate.py P6.5` 调用与 `check-judge-verdict.py` 的既有判定行为（可复用/参照已有 P6.5 相关测试用例）在 phases.yaml 措辞修改后不变
- **BDD-29（跨 issue 约束：check-gate.py/check-events.py 判定逻辑不变）**：这条更适合作为 P6/P7 阶段的 diff 审查断言而非单元测试，若你判断确实无法写成有意义的自动化测试，可在 P3-test-cases.md 中明确标注"本条以 P7 一致性检查阶段的 diff 逐行核对方式验收，非自动化单元测试覆盖"，不算测试缺口
- 测试运行器：`python3 -m pytest agate/tests/ --basetemp=.pytest-tmp -p no:cacheprovider`

### 上游关联
- P2-design.md §1.1：`phases.yaml` 的 `id: P4`（现第 57-66 行）与 `id: P6.5`（现第 88-97 行）两处改动落点
- P2-design.md minimal_validation 已实测确认：`grep -n "P4-review" agate/phase-cards/P4-implementation.md` 现命中 10 次（第 90-153 行区域），`check-structure-consistency.py` 的 S-3 逻辑只做字符串存在性判断，追加 outputs 声明不会触发新增不一致

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0024-toolchain-md-field-set/P1-requirements.md（BDD-25~29）
- {AGATE_WORKSPACE}/tasks/TAG0024-toolchain-md-field-set/P2-design.md（§1.1 该批改动落点 / §3.8 详细设计）
- agate/scripts/check-structure-consistency.py:153-266（S-1/S-2/S-3 校验逻辑，供测试直接调用或子进程验证）
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
- 查证结果：`agate/rules/phases.yaml` 的 `id: P4` 现位于第 57-66 行（`outputs` 仅含 `P4-implementation.md`），`id: P6.5` 现位于第 88-97 行（与 P4-P8 平级声明）
- 查证结果：`agate/state-machine.md` 第 74/152 行明确表述"P6.5 是挂载于 P6→P7 转移的强门槛子阶段，不是独立 phase 值"
</objective_info>
