> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。

---
phase: P3
generated_by: agate-inject-card.sh + 主 Agent
task_id: T001
role: test-designer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

为 T001（agate v0.40.0 结构化改造，A+B+C+D 四流全做）产出 `docs/tasks/T001-v2.0-structured/P3-test-cases.md` + `docs/tasks/T001-v2.0-structured/P3-test-code/`（bats 测试文件，写入/改写到 `agate/tests/` 对应目录），覆盖 P1-requirements.md 全部 28 条 `#### BDD-NN`（1:1 映射），当前全部红灯（TDD：实现尚未开始）。

### 约束

1. **测试用例总数硬约束（BDD-11）**：`count-tests.sh` 输出必须严格回落到 **594**（sanity 6 另算），不允许净漂移。计算口径见下方"594 配平机制"，产出物**必须包含配平表**（新增 N = 移减 M）。
2. **不允许净新增测试**：新校验器测试（`unit/check-frontmatter.bats`）覆盖的行为，必须在受影响文件中**删除或合并**等量的重复断言配平，不是简单加测试。
3. **15 个受影响文件（354 个 @test）改写而非删减**：@test 数逐文件保持不变（可改写断言内容、可重命名，不可删减用例）。
4. **3 个 regression 摩擦锚点需改写**：`v060-design-gap`（4 test）/ `v060-p8-internal-only`（3 test）/ `v060-r4-cached`（2 test）改写为测 frontmatter 版行为。
5. **2 个 regression fixture 明确不动**：`v060-p8-cached`（P8 --cached）与 `v060-yaml-indent`（模板 executor_env，P0 字段不迁移）——不要误改。
6. **P3 范围只跑 unit + regression**（`gate_commands.P3` 已在 P2 固化为 `bats agate/tests/unit/ agate/tests/regression/`，formatter=`generic-tap.sh`）；integration/sanity 属于 P5/P6 范围，不在本阶段红灯判定内。
7. **UI 任务判断**：P2 declares `ui_affected: false`（非 UI 任务），不需要 Playwright/E2E 用例。
8. **内部按流 A→B→C→D 组织**：P3-test-cases.md 与测试代码需按流分组标注（P4 实现会严格按 A→B→C→D 串行推进，P3 产出需支持这个顺序——流 A 的测试红灯不依赖流 B/C/D 未实现的东西，反之亦然，互不阻塞）。
9. **frontmatter 嵌套 ≤3 层（硬约束 2）**：设计的测试 fixture 里任何 frontmatter 样例本身也要遵守这条，不要在测试数据里写出 >3 层嵌套的反例之外的"合法期望值"。
10. **语义真实性边界（BDD-14）**：测试只断言"字段被可靠读取/坏格式被拦截/编号规则被正确校验"这类解析层行为，不要设计"判断 BDD 内容语义真实性"的测试（那不是本次改造的范围，P2 §10 已声明结构化不解决语义真实性）。
11. **分阶段落盘**：每完成一个流（A/B/C/D）的测试设计，立即追加写入 `docs/tasks/T001-v2.0-structured/P3-progress.md`（bash 追加模式，不要等全部完成再一次性写）——P3 是空返回问题高发阶段，分阶段落盘是缓解措施。
12. **不要修改 `agate/scripts/*.py` / `agate/scripts/*.sh` 的实现代码**——本阶段只写测试，实现在 P4。红灯的来源应该是"实现未写"（B 类错误：assertion 失败/项目内 import 失败），不是"测试代码本身有语法错误"（A 类错误）。

### 上游关联

- P1-requirements.md：28 条 BDD 验收条件（BDD-1~15 流A / BDD-16~20 流B / BDD-21~24 流C / BDD-25~28 流D），每条都是测试的直接来源。
- P2-design.md：已 approved 的方案设计（候选方案A：单工具双读扩展），关键落点见下方"输入文件"。
- P2-review.md：8 条 FIND 已全部修订，其中 FIND-3（354 测试口径）、FIND-7（594 配平机制）、FIND-5（单行全角冒号块返回 str 非 dict 需硬拦截）与本阶段测试设计直接相关。

### 输入文件

- `docs/tasks/T001-v2.0-structured/P0-brief.md`（任务简报，9 条硬约束）
- `docs/tasks/T001-v2.0-structured/P1-requirements.md`（28 条 BDD，§0 附近有验收标准正文）
- `docs/tasks/T001-v2.0-structured/P2-design.md`——重点段落：
  - §3.1 流 A 全节（§3.1.1 schema / §3.1.2 双读工具 op / §3.1.3 校验器 / §3.1.4 pre-commit 挂载 / §3.1.5 fixture 重写与 594 配平机制）
  - §3.2 流 B 全节（P6/P7 frontmatter 落点）
  - §3.3 流 C 全节（P1 标记状态结构化）
  - §3.4 流 D 全节（编号规则硬切）
  - §5 gate 命令（P3 固化：`bats agate/tests/unit/ agate/tests/regression/`，formatter `generic-tap.sh`）
  - §6 files_to_read（P4 实现导航，列出了每个待改脚本的具体行号，测试设计时可参考定位断言对象）
  - §7 minimal_validation（pyyaml 行为已验证的 5 条假设，测试可直接复用这些验证方法）
  - §9 BDD 覆盖映射表（28 条 BDD → 设计落点，直接查表定位每条 BDD 该测什么）
  - §13 FIND-3/FIND-5/FIND-7 修订详情（354 测试口径、str-not-dict 硬拦截、594 配平机制）
- `agate/assets/execution-roles/test-designer.md`（你的角色定义，先读这个）
- `agate/assets/templates/dispatch-prompt.md`（如需核对派发格式）
- `agate/tests/README.md`（bats helper 加载顺序、fixture 约定）
- `agate/scripts/agate-state-yaml-check.py`（P2 §3.1.3 提到的校验器范式参照——新 `agate-frontmatter-check.py` 的测试设计可参照这个的现有 `.bats`：`agate/tests/unit/agate-state-yaml-check.bats`）
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
- 环境状态：worktree `feat/v2.0`，`.state.yaml` phase=P3 status=active retries={}；P0/P1/P2 已 commit 且 review approved；`count-tests.sh` 当前基线 594（sanity 6 另算），改造前干净。
- P3 gate 命令（P2 §5 固化，不得修改）：`gate_commands.P3 = "bats agate/tests/unit/ agate/tests/regression/"`，`P3_formatter = "generic-tap.sh"`。
- 15 个受影响文件的当前 @test 数（2026-08 实测，逐文件保持不变）：
  check-gate.bats=101 / check-pruning.bats=29 / check-p6-provenance.bats=38 / check-p6-evidence.bats=28 / check-tdd-red.bats=38 / check-gate-p1-review（含在 check-gate 内或独立文件，按实际目录核实）=9 / check-scope-resolved.bats=11 / check-retrospective.bats=11 / check-p6-format.bats=12 / agate-extract-context.bats=15 / regression/v060-design-gap=4 / regression/v060-p8-internal-only=3 / regression/v060-r4-cached=2 / integration/pre-commit-hook.bats=42 / integration/consistency.bats=11。合计 354。
- 594 配平口径：594 = 354（上述 15 文件）+ 240（其余未受影响文件，保持不动）。新增 `unit/check-frontmatter.bats` 的用例数 N，必须通过在上述 15 文件中删除/合并 M 条与新校验器重复覆盖的既有断言配平，N=M。P2 §3.1.5 举例：check-gate.bats"P2 四字段缺失"断言 vs BDD-6 重复、check-p6-format.bats"大小写归一化"断言 vs 新行格式校验重复，可作为配平候选。
- FIND-5 硬拦截点：`yaml.safe_load` 对"单行纯 scalar 块"（仅一行、无 key:value 结构，如整块只有一行全角冒号文本）返回 `str` 而非 `dict`，且**不报 YAMLError**——这是 pyyaml 的真实行为（P2-review 已实测复现），校验器需要"frontmatter 块存在但解析结果非 dict → 一律报错"的显式判断，测试必须覆盖这个具体场景（非 YAMLError 类型的坏格式）。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
