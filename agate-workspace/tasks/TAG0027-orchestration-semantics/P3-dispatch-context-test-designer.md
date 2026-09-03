---
phase: P3
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0027
role: test-designer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

产出 `P3-test-cases.md` + `P3-test-code/`（测试代码，**当前全部红灯**）：把 P1 的 25 条 BDD
（BDD-1~25）1:1 转为 pytest 用例，为 P4 实现提供 TDD 红灯。测试覆盖 P2 设计 §5 的 BDD 覆盖
映射表全部验证手段。

### 约束

1. **BDD→测试 1:1 映射**：每条 `#### BDD-NN` 至少一个 pytest 用例（可参数化），测试名引用
   BDD 编号（如 `test_bdd_1_next_retreat_schema`）。P6 验收对照 P1 的 25 BDD，测试覆盖不全 =
   P6 无自动化验证 → 打回。P2 §5 映射表的"验证手段"列是测试设计的直接来源。
2. **测试代码落点**：写 `agate/tests/unit/` 下新测试文件（与既有测试同目录，P5 全量 pytest
   会自动收集；参照既有测试命名：`test_agate_*.py` / `test_check_*.py`）。P3-test-cases.md
   声明 `test_code_dir:`。**测试文件命名与内容须与既有测试风格一致**（读 1-2 个既有测试文件
   参照 fixture/conftest 用法）。
3. **红灯正确性**：当前实现未写 → 被测模块/函数不存在 → 测试应因 import 失败/模块缺失红
   （B 类红灯，check-tdd-red 可放行）。**不要**为让红灯更"优雅"去 mock 掉被测对象——TDD
   红灯语义 = 测真实目标。已有既有机制（check-structure-consistency S-1/S-2 等）的扩展点测试
   可对既有函数写断言（现状绿 + 新扩展点红要能区分）。
4. **测试设计先行、实现未写**：P3 只写测试不写实现。测试引用目标 CLI/函数用"预期路径"——
   P2 设计已定名：`agate/scripts/agate-next.py`、`agate/scripts/agate-advance.py`、
   `agate/scripts/agate-dispatch.py`（agate-next.py 与既有 agate-next-card.py 区分——新 CLI
   名确认见 P2 §3.4/§3.5）。
5. **不越 P2 设计范围**：测试断言以 P2 §5 映射表 + §3.1-3.8 定案语义为准（next/retreat 值域、
   P6.5 gate_subphase 三键、exit2-resolution 文件、CARD-SOURCE 块外、CHECK 14/15 结构豁免、
   S-1/S-2 加列等）。测试用临时任务目录（tmp_path）模拟 .state.yaml 推进场景，不碰真实任务
   数据。临时目录不落协议本体。
6. **回归拦截测试**：P2 §1.1 影响面 15 行中的既有机制改动（check-p6-provenance 审计 2 双锚点、
   check-judge-verdict _strip_card、check-structure-consistency S-1/S-2、check-protocol-consistency
   CHECK 14/15、pre-commit 2p hash）——既有行为测试须保持绿（回归），新扩展点测试红。
7. **平台无关硬约束**（AGENTS.md 测试约定）：不硬编码单平台假设、不裸 python3（探测
   python3|python）、不用 /tmp（pytest tmp_path fixture）、路径用相对 worktree 根。
8. **测试用例数**：P1 无 ceremony 声明 → standard。BDD 25 条 → 预计 ~30-40 用例（部分 BDD
   多场景拆多用例）。记录最终用例数。
9. **分阶段落盘强制**：P3 是空返回高发阶段——每读完一个输入文件、每写一批测试追加
   P3-progress.md。

### 上游关联

- P1-requirements.md（25 BDD Given/When/Then 语义权威）——BDD-10 已回改（P6→P4 示例，
  [BASELINE_CHANGE] 已批准，测试按回改后语义写）
- P2-design.md（§5 BDD 覆盖映射表 = 测试设计直接来源；§3.1-3.8 定案语义 = 断言依据；
  §4.1 gate_commands = P5 验证命令）
- P2-review.md（approved，A1/A2/A3 修复后定案含 P6 judge 后推进裁决、CARD-SOURCE 块外 +
  审计 2 双锚点、assets/templates/dsh/ 结构豁免）
- P2-progress.md（architect 脚本实读记录：check-gate gate_p6/gate_p65 行号、审计 2 剥离逻辑、
  _extract_card 等——测试写这些扩展点时对照真实现状）

### 输入文件（按顺序读）

1. `agate-workspace/tasks/TAG0027-orchestration-semantics/P1-requirements.md`（25 BDD 全读）
2. `agate-workspace/tasks/TAG0027-orchestration-semantics/P2-design.md`（§5 BDD 映射表 + §3.x
   定案 + §4.1 gate_commands 全读，其余按需）
3. `agate-workspace/tasks/TAG0027-orchestration-semantics/P2-review.md`（approved 定案含 A1/A2/A3，
   按需）
4. `agate/tests/unit/` 下 1-2 个既有测试文件（风格参照，如 test_agate_next_card.py /
   test_check_structure_consistency.py 或同类——确认 fixture/conftest 用法）
5. `agate/tests/conftest.py`（fixture：临时任务目录/state 构造方式，必读）
6. `agate/rules/phases.yaml` + `agate/rules/schema/phases.schema.json`（被测数据面现状）
7. `agate/scripts/agate-next-card.py`（既有相邻脚本，测试命名防混淆参照；按需）
8. `agate/scripts/check-structure-consistency.py` / `check-protocol-consistency.py` /
   `check-p6-provenance.py` / `check-judge-verdict.py` / `pre-commit-gate.py`（被测扩展点现状，
   按需读——大文件只读相关函数区）
9. `AGENTS.md`（项目约定 + 测试约定）

> ⚠️ 协议文件读 worktree 自己的 `agate/`。P3 只写测试到 agate/tests/（worktree），不改协议
> 本体脚本/rules/文档。

### 产出文件字段

- `P3-test-cases.md`：声明 `test_code_dir:`（如 `agate/tests/unit/` 或明确子目录）；Header 用
  agate-md-field-set 填（phase/task_id/agent 等）。
- 测试代码写入 test_code_dir 指向位置（新文件）。
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
### A. 路径拓扑
- worktree 根 = `/home/kity/oclab/agateon/.worktrees/agate-TAG0027`（分支
  feat/TAG0027-orchestration-semantics）
- 任务目录 = `agate-workspace/tasks/TAG0027-orchestration-semantics/`
- 协议本体（按需读，不改）= worktree 的 `agate/`
- 测试代码落点 = worktree 的 `agate/tests/`（P5 全量 pytest 收集路径 = `agate/tests/`）
- 测试基线：pytest 1311（unit 1191 + regression 28 + integration 92）；环境 python 3.12.3 /
  pyyaml 6.0.1 / pytest 9.0.3

### B. P2 §5 BDD 覆盖映射（验证手段速查——测试设计来源）
BDD-1 schema 校验 exit 0 + 9 条目键齐全（P5_schema）；BDD-2 schema 反例（P6.5 写 next: P7 →
失败）；BDD-3 各 retreat 与 state-machine.md 锚点核对；BDD-4 制造 YAML/WORKFLOW 不一致 →
check-structure-consistency exit 1；BDD-6 P5→P6 exit 0 直推 + P6 通过路径（A1：judge 未启用 →
直推 P7）；BDD-7 mock check-gate exit 1 → retreat-to 委托/retries[P4]+1；BDD-8 exit 2（非 P6）
不推进 + 落盘 {phase}-exit2-resolution.md；BDD-9 P6 exit 2 特例（无 exit2-resolution）+ P6 judge
后推进（judge.enabled + verdict 存在 + gate_p65 exit 0 → P6→P7）；BDD-10 diff≥2 人工直跳提示
PAUSED + retreat-to 逐阶调用；BDD-11 两次推进后 gate-events.jsonl 含 state_transition；BDD-12
有 exit:2 gate_run 无 resolution 文件 → verdict 校验失败；BDD-13 两脚本头注释 + exit code 回归；
BDD-15 插裸 task → ERROR + task_fields 键不误报；BDD-16 无注记段含 DSH → ERROR + 补注记 pass；
BDD-17 SKILL.md 结构豁免 + architect.md 注记段 → CHECK 14 pass；BDD-18 产物含卡片块 +
generated_by + CARD-SOURCE 在 START 前（块外）；BDD-19 手工占位符 + inject-card exit 0（回归）；
BDD-20 渲染产物含 PASS/FAIL 模板 → audit2 exit 0（CARD-SOURCE 块外剥离）；BDD-21 手工注入文件
→ audit2 exit 0（回归）；BDD-22 插平台名 ERROR → 补注记 pass；BDD-23 render-dispatch-prompt
CLI 契约回归；BDD-24 新文档自动被 CHECK 14 覆盖；BDD-25 两路 dispatch-context 过 2p hash
（CARD-SOURCE 产物过 2p = A2 机制）。

### C. 新 CLI/脚本命名（P2 定案）
- `agate/scripts/agate-next.py`（推进，exit 0/1/2 消费 check-gate 三态）
- `agate/scripts/agate-advance.py`（多阶回退引导/委托 retreat-to）
- `agate/scripts/agate-dispatch.py`（渲染时注入单命令）
（与既有 `agate-next-card.py` / `agate-inject-card.py` / `agate-card-inject.py` /
`agate-render-dispatch-prompt.py` 区分——P4 新建，P3 测试引用其预期行为）

### D. P5 gate 命令（P3 测试须能被这些命令收集）
- P3/P5 均用 `python3 -m pytest agate/tests/` 收集（worktree 根跑）——测试文件放
  `agate/tests/unit/`（或对应子目录）即可被收集；P3 红灯由 check-tdd-red.py 用
  gate_commands.P3 判定
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
