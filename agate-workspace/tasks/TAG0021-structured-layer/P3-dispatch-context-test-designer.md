---
phase: P3
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0021
role: test-designer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

产出 `P3-test-cases.md` + 测试代码（TDD 红灯批）：TAG0021「协议结构化层（RM-AG0022）」——为 16 条 BDD（M0-M3）写失败测试，测试先于实现（P4 才实现）。

### 上游输入（按序读取，每读完一个追加 progress）

1. {AGATE_WORKSPACE}/tasks/TAG0021-structured-layer/P1-requirements.md（16 条 BDD 按 M0/M1/M2/M3 分组——测试 1:1 映射基准）
2. {AGATE_WORKSPACE}/tasks/TAG0021-structured-layer/P2-design.md（C1 方案：YAML 边界 §3.1 / schema §3.2 / S-1~S-6 判定口径与触发点 §3.3 / M1 对账 §3.4 / M0-M3 里程碑清单 §3.5 / 完成标志 §3.7 / files_to_read / gate_commands——测试设计的实现导航）
3. {AGATE_WORKSPACE}/tasks/TAG0021-structured-layer/P2-review.md（plan-eng-review approved；非阻塞发现 1-3 要求在**首批失败测试**中固化 S-1/S-2 READY 行排除、gate_commands 合法 key 判据（含 project_module）、五模式词表对齐；#4 825 基线出处改为"既有 fixture 集合"表述；#5 53/57 口径统一）
4. {AGATE_WORKSPACE}/tasks/TAG0021-structured-layer/P0-brief.md（约束）
5. {agate_root}/phase-cards/P3-tdd.md（随本上下文已注入卡片全文）

路径说明：{AGATE_WORKSPACE} = `/home/kity/oclab/agate/.worktrees/agate-TAG0021/agate-workspace`；{agate_root} = `/home/kity/oclab/agate/agate`（~/.agate 稳定版）；改造对象（要写测试的仓库本体）= worktree `/home/kity/oclab/agate/.worktrees/agate-TAG0021`。

### 测试设计要点（对照 BDD 分组）

**M0（BDD-1..5，测试对象 = 新脚本 check-yaml-schema.py / check-structure-consistency.py，P4 才实现）**：
- BDD-1: test_check_yaml_schema.py——合法/非法 YAML 通过 JSON Schema 校验的退出码判定（非法字段/错误枚举/错误类型 → 非 0）
- BDD-2/3/5: test_check_structure_consistency.py——S-1（YAML→md 阶段总览）/ S-2（md→YAML）/ S-3（YAML→卡片）/ S-4（YAML→脚本字段）/ S-5（schema 枚举）/ S-6（引用完整性）双向判定；人为制造漂移 → 非 0；两侧一致 → 0
- BDD-4: 存量行为不变——不新写测试，P5 全量回归覆盖（测试设计里声明）
**M1（BDD-6/7，对账模式）**：test_check_reconcile.py（或按脚本拆分 test_reconcile_*.py 若干）——已知差异夹具 → stderr WARNING + 差异计数 + 退出码保持原语义；覆盖面 ≥3 脚本（agate-read-gate-commands / check-pruning / check-gate）+ 3 类解析点（gate_commands 块 / P1 裁剪字段 / P2 四字段）
**M2（BDD-8/9/10/11）**：对账清零判据 / 静态扫描零命中（agate/scripts 中已迁移解析模式命中数=0）/ 一致性 gate 提升阻断（pre-commit+CI 语义）/ 迁移后回归声明（P5 覆盖）
**M3（BDD-12/13/14）**：test_card_render.py 类——卡片渲染一致 + 篡改 YAML → 非 0；agate-inject-card 渲染化兼容 + 稳定版隔离；回归声明
**跨里程碑（BDD-15/16）**：count-tests 只增不减（用现有 count-tests 机制）/ 平台无关（新测试自身不引入裸 python3、/tmp、硬编码 PATH、-L 软链假设、POSIX 假设；平台差异按分支断言或模拟覆盖）

### 硬约束

- **TDD 红灯**：测试代码写完这些测试必须红（被测模块 check-structure-consistency.py / check-yaml-schema.py 在 P3 尚不存在；对账模式钩子未实现）——真红灯（B 类：assertion 失败 / 项目内 import 失败），禁止假红灯（A 类：SyntaxError / 第三方 import 失败）
- **count-tests 只增不减**：新增测试文件纳入 count-tests 计数（用例数 > 基线，不允许删/改既有用例条数）
- **平台无关（BDD-16）**：不引入裸 `python3`（用探测 `python3|python`）、不写死 `/tmp`（用 pytest tmp_path / --basetemp）、不假设 POSIX 软链语义、不硬编码 PATH。测试临时目录用 pytest fixture。
- **/tmp 只读**：自跑确认红灯用 `python3 -m pytest <新测试文件> -q -p no:cacheprovider --basetemp=/home/kity/oclab/agate/.worktrees/agate-TAG0021/dist/`（dist/ 已实证可写）；不得用 /tmp、ptmp
- **既有测试零回归**：不改既有测试（除非 P2 评审 #4 要求的口径微调，需在 progress 说明）
- 新测试文件放 `agate/tests/unit/`（或对账/集成类放相应子目录），命名 `test_*.py`
- bash 一律外层 timeout（30-90s）；读文件优先 read/grep/glob 工具；单步串行

### 产出规格

- `{AGATE_WORKSPACE}/tasks/TAG0021-structured-layer/P3-test-cases.md`：必须声明 `test_code_dir:`（如 `agate/tests/unit/`），每条测试用例对应一条 BDD-NN（1:1 映射表：BDD 编号 → 测试文件 → 用例描述 → 预期红灯类型），P2 评审非阻塞发现 1-3 的固化为独立用例
- 测试代码文件（写到 worktree `agate/tests/` 下约定目录）
- 状态标记：`[PROD_NOT_TOUCHED]`
- 分阶段落盘：`{AGATE_WORKSPACE}/tasks/TAG0021-structured-layer/P3-progress.md`

### 返回

只返回两行：① P3-test-cases.md 路径；② 一句话摘要（≤30 字，含红灯测试文件数）。
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