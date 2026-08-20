---
phase: P3
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0007
role: test-designer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
为 P1-requirements.md 的 11 条 BDD 设计测试用例（1:1 映射），产出 P3-test-cases.md +
测试代码，且**当前必须全部红灯**（真红灯：import 失败/assertion 失败，不是语法错误假红灯）。
本任务不是 refactor 任务（P1 frontmatter 未声明 `change_type: refactor`），走标准 TDD 口径。

### 约束
1. **不要重新调研设计**：P2-design.md 已完整规定了每处改动的精确逻辑（字段名、判定分支、
   两层 pairing 校验的对应关系），你的任务是把这些已确定的判定逻辑转成测试断言，不是重新设计
   判定逻辑。P2-design.md §1.1（改什么表）已给出 BDD→测试文件的精确映射，直接按此表执行。
2. **BDD→测试映射**（P2-design.md §1.1 已给出，此处摘录供直接使用）：
   - BDD-1（骨架存在性）+ BDD-3（不重复触发）→ `agate/tests/unit/test_check_gate.py` 新增
     `gate_p2` 用例：`project_phase: bootstrap` + 缺 P2-skeleton.md → gate 失败；含正确标题 →
     通过；字段缺失 → 行为与改动前逐字节一致（回归，用现有测试断言对照）
   - BDD-2（骨架模板参数化）→ 新文件 `agate/tests/unit/test_skeleton_template_stack_neutral.py`：
     读 `assets/templates/skeleton-template.md`，断言不含硬编码技术栈目录名黑名单（如
     `src/components`、`src/include`、`src/hooks`、`src/pages`）+ 含参数化标记关键词
   - BDD-4（P4 落点+偏离说明）+ BDD-7（CODE-MAP 更新义务）→ `test_check_gate.py` 新增 `gate_p4`
     用例：覆盖 WARNING 分支（骨架/CODE-MAP 机制已采用且「新增文件核对表」标题缺失时输出
     WARNING，不阻断）
   - BDD-5（骨架回归基线）+ BDD-11（CODE-MAP 回归基线）→ 不新增测试用例，由 P5 gate 的全量
     `python3 -m pytest agate/tests/` 验证 1011 条既有用例 0 新增失败（P3-test-cases.md 中
     须显式声明这两条 BDD 的验证方式是"全量回归套件"，不是遗漏）
   - BDD-6（CODE-MAP 存在与初始化）→ 新文件 `agate/tests/unit/test_code_map_template.py`：
     读 `assets/templates/code-map-template.md`，断言含五个必填标题（模块/层/依赖方向/关键
     文件/约定）
   - BDD-8（P7 同步核对）+ BDD-9（依赖偏离可见信号）→ `test_check_gate.py` 新增 `gate_p7` 用例：
     覆盖两层 pairing 校验的三态（未配对→exit 1 / 已配对→通过 / 机制未采用→不检查），务必按
     P2-design.md §1.1/§2.3/§5 已修正的字段对应关系编写断言（内部一致性比较
     `code_map_reviewed_count` vs `code_map_new_files_count`；转抄核对比较 P4 表实际计数 vs
     `code_map_new_files_count`，**不是** `code_map_reviewed_count`——这是 P2 review 曾打回的
     错误点，测试用例本身若写反会掩盖同样的错误）
   - BDD-10（refactor 不豁免）→ `test_check_gate.py` 新增用例：验证 `gate_p4`/`gate_p7` 判定
     逻辑不读取/不分支 `change_type` 字段（对 `change_type: refactor` 声明的任务同样生效）
3. **产出文件数量控制**：由于 `gate_p2`/`gate_p4`/`gate_p7` 三处新增用例都落在同一个既有文件
   `agate/tests/unit/test_check_gate.py`（该文件已存在，约 2395 行），这些用例作为该文件的
   新增测试函数一次性写入（不是新建 3 个文件），加上 2 个全新文件（skeleton/code-map 模板
   测试），总产出为：P3-test-cases.md + test_skeleton_template_stack_neutral.py（新）+
   test_code_map_template.py（新）+ test_check_gate.py（编辑追加）= 4 处文件touch，在任务粒度
   基准内（新建文件 2 个 + 1 个既有大文件的定向追加，不是无节制大改）。
4. **红灯的真实性核实**：`gate_p2`/`gate_p4`/`gate_p7` 目前均未实现 `project_phase`/
   CODE-MAP pairing 相关判定分支（P4 尚未开始），新增测试断言这些尚不存在的行为必然失败——
   写完后自跑一次 `python3 -m pytest agate/tests/unit/test_check_gate.py
   agate/tests/unit/test_skeleton_template_stack_neutral.py
   agate/tests/unit/test_code_map_template.py -v` 确认新增用例是真红灯（AssertionError /
   属性不存在等），不是 SyntaxError 类假红灯。
5. **不要动 P4/P7/P1/P2 阶段卡片、architect.md、consistency-reviewer.md、模板文件本身**——那些是
   P4 实现阶段的产出物，P3 只写测试代码本身，不要提前实现被测对象。
6. **test_code_dir 声明**：按本仓库既有约定（TAG0017 先例）填 `agate/tests/unit`。
7. **本任务不涉及 UI**（`ui_affected: false`），不需要 Playwright/E2E 用例。

### 上游关联
P2-design.md（approved）已完整规定：
- §1.1 改什么表：11 条 BDD 到文件/函数的精确映射（本 dispatch-context 约束 2 已摘录关键部分）
- §2.3 决策组3：CODE-MAP pairing 两层校验的精确字段对应关系（内部一致性 + 转抄核对，字段名
  `code_map_new_files_count`/`code_map_reviewed_count`）——这部分是 P2 review 第一轮打回、
  第二轮才修复对齐的部分，测试用例必须按修复后的正确对应关系编写，不要按直觉重新推导
- §3 实现完成的标志：给出了每条判定的可判定标准（gate exit code、字段存在性）
- §6 gate_commands：`P3: "python3 -m pytest agate/tests/"`（本阶段的测试运行器）

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0007-project-structure/P1-requirements.md（BDD 验收条件，主要来源）
- {AGATE_WORKSPACE}/tasks/TAG0007-project-structure/P2-design.md（核心输入，已完整规定判定逻辑，
  重点读 §1.1/§2.3/§3/§5/§6）
- {AGATE_WORKSPACE}/tasks/TAG0007-project-structure/P0-brief.md（环境约束）
- /home/kity/oclab/agate/.worktrees/agate-TAG0007/agate/scripts/check-gate.py（`gate_p2`
  L552-641、`gate_p4` L650-680、`gate_p7` L807-903 三处函数现状，供理解当前未实现状态和既有
  DESIGN_GAP 测试用例的编写风格）
- /home/kity/oclab/agate/.worktrees/agate-TAG0007/agate/tests/unit/test_check_gate.py（grep
  `def test_gate_p2\|def test_gate_p4\|def test_gate_p7` 定位既有用例风格，比照编写新用例；
  文件较大 2395 行，不通读，按 grep 结果定位相关测试类/函数附近读取）
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
- P2-design.md frontmatter：dispatch_plan 声明 4 批（skeleton-docs/code-map-docs/
  gate-script-both/dogfood-bootstrap），但该 dispatch_plan 是**给 P4 实现阶段**的编排方案；
  P3 测试设计阶段由于 gate_p2/gate_p4/gate_p7 三处判定都落在同一个既有文件
  `test_check_gate.py`，按「同一文件不跨批次被改两轮」原则，P3 本身采用单发模式（不拆批），
  与 P4 的 4 批拆分是两个独立的编排决策（P3 阶段的产出规模在单发范围内可靠交付）
- 环境基线捕获（`agate-capture-env-baseline.py`）返回："命令无 formatter，无法提取 fail-list，
  放弃捕获，不写入任何文件"（exit 0，非阻塞，按 P3 卡片步骤 0 说明可忽略继续）
- 本仓库回归基线：改动前 1011 pytest passed + consistency 0 ERROR
- gate_commands.P3 = "python3 -m pytest agate/tests/"（无 formatter 声明，check-tdd-red.py
  退化为 exit-code-only 模式，所有红灯 = 可推进）
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
