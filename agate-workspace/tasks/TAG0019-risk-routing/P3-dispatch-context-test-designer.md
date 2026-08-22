---
phase: P3
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0019
role: test-designer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

产出 `P3-test-cases.md` + 测试代码（`agate/tests/` 下）：TAG0019「风险分路由」测试设计。P1 15 条 BDD（BDD-1..15）每条 1:1 映射一个测试用例；测试代码先于实现（TDD 红灯批，P4 implementer 按测试反推实现）。

覆盖范围（P2-design 方案 B 的测试资产）：
1. **agate-risk-score.py**（新脚本）：BDD-1（输出三要素 risk_score/tier/证据行）、BDD-2（文件类型信号分级）、BDD-3（敏感路径+security 域）、BDD-4（规模信号>5 对齐 pruning 口径）、BDD-5（域映射与影响面）
2. **check-routing.py**（新脚本）：BDD-6（ceremony 合法值）、BDD-7（thin 四要素缺一/薄化验证回退 standard，含 P5/P6 保留 + check-pruning 检查 3/5 双闸）、BDD-8（不声明=standard）、BDD-9（声明 vs 算分单向 fail-closed）、BDD-10（与 check-pruning 同源：import 复用 + 对拍一致）
3. **协议文档/角色**（BDD-11 requirements-review 审声明职责、BDD-14 full 档强制评审与 P7 不可裁、BDD-15 消费点文档同步）→ 文档/静态断言类测试
4. **BDD-12**（M3 验收锚度量协议四要素）、BDD-13（平台假设零命中：新增脚本过 check-platform-assumptions R1-R5）

### 约束

- **复用不重造**：check-routing 判定测试应 import 复用 check-pruning 判定逻辑（对拍用例：同一 fixture 下 check-routing 与 check-pruning 同源函数输出一致）；断言"独立重写/分叉 = FAIL"（BDD-10）
- **fail-closed 三 BDD**：BDD-7 缺任一要素 exit 1 / BDD-8 不声明 exit 0 / BDD-9 声明薄于算分 exit 1（单向）
- **P1 缺失分支**：check-routing P1 缺失 → exit 2（对齐 check-pruning 语义，P2 §2.3）
- **算分异常分支**：run_git 失败/agate_common 不可导入 → score_task 输出 git_ok:false 不静默降级；thin 声明 → exit 1 fail-closed（P2 §2.3）
- **错误边界测试**（评审测试缺口 3 项）：算分失败分支 + importlib 上下文 agate_common 可导入性断言（防双层模块 sys.path 依赖静默退化）；check-routing 逐分支清单（thin 全过 exit 0 / 缺要素 exit 1 / P1 缺失 exit 2 / 算分异常 fail-closed）
- **full-P7 文档断言**（评审测试缺口）：声明 ceremony: full 但 phases 缺 P7 → 文档断言可 grep（BDD-11/14 联动）
- **平台无关**（BDD-13 + agate 核心约束）：测试不得硬编码单平台假设（无裸 PATH/裸 python3/无 /tmp/无 POSIX symlink 假设）；临时文件用 pytest tmp_path fixture；不写 /tmp
- **测试在哪写**：`agate/tests/unit/` 下新文件（参考既有命名 test_check_pruning.py / test_agate_md_field_get.py 风格）。测试运行需 `-p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp`（/tmp 只读）
- P2-design.md files_to_read 与 §3 测试分支清单（:266-271）为本轮测试范围权威

### 上游关联

P1-requirements.md（15 BDD approved）为用例来源；P2-design.md（方案 B + gate_commands + files_to_read + §3 分支清单）为测试设计导航；P2-review.md approved 锁定设计。

### 输入文件

- {AGATE_WORKSPACE}/tasks/TAG0019-risk-routing/P1-requirements.md（BDD 15 条，权威）
- {AGATE_WORKSPACE}/tasks/TAG0019-risk-routing/P2-design.md（方案 B + files_to_read + §3 测试分支清单）
- /home/kity/oclab/agate/agate/assets/execution-roles/test-designer.md（角色定义，稳定版）
- /home/kity/oclab/agate/agate/scripts/check-pruning.py（复用对象：对拍用例的参考实现）
- /home/kity/oclab/agate/agate/scripts/check-tdd-red.py（红灯判定工具，理解其 exit 语义）
- /home/kity/oclab/agate/agate/tests/ 既有测试风格参考（如 unit/test_check_pruning.py）

路径说明：{AGATE_WORKSPACE} = `/home/kity/oclab/agate/.worktrees/agate-TAG0019/agate-workspace`；{agate_root}（稳定版）= `/home/kity/oclab/agate/agate`；改造对象 worktree = `/home/kity/oclab/agate/.worktrees/agate-TAG0019`。

### 客观查证信息（本机实测，硬约束）

- /tmp 只读：pytest 必须 `-p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp`；解释器 /usr/bin/python3
- 读卡片/角色用 ~/.agate 稳定版；bash 一律外层 timeout（30-90s）；读文件优先 read/grep 工具；单步串行
- [PROD_NOT_TOUCHED]；产出路径硬约束：`{AGATE_WORKSPACE}/tasks/TAG0019-risk-routing/P3-test-cases.md` + 测试代码写入 worktree `agate/tests/`
- 分阶段落盘：关键步骤追加 `{AGATE_WORKSPACE}/tasks/TAG0019-risk-routing/P3-progress.md`

### P3 产出规格（P3 卡片为准）——**紧凑表格格式（强制）**

- P3-test-cases.md 声明 `test_code_dir: {测试代码实际路径}`
- 每条 BDD-NN 1:1 对应测试用例（15 条全覆盖，不能挑）
- **格式约束（重要，防写作卡壳）**：P3-test-cases.md 用**紧凑表格**呈现——三列：`BDD 编号 | 测试文件 | 用例意图（≤2 行）`。每 BDD 一行，不要逐条长篇写 Given/When/Then 步骤（具体断言在测试代码里体现）。全文目标 ≤250 行。**不要试图在文档里完整写出每个测试的代码级细节**——那是测试代码文件的事。
- Header：phase: P3 / task_id: TAG0019-risk-routing / type: test-cases / parent: P2-design.md / trace_id: TAG0019-P3-20260821 / status: draft / created: 2026-08-21 / agent: test-designer
- 测试代码写好即自跑确认红灯（import 失败/模块不存在 = 正确红灯；断言与数据矛盾 = 测试 bug 先修）

### 执行节奏（两次派发教训——分期强制落盘，防止长时间无产出）

**先产测试用例文档，再产测试代码。每完成一个文件立即落盘 progress，不要攒批。**
1. **第一步（优先）**：写完 `P3-test-cases.md` → 立即追加 progress
2. **第二步**：逐个写测试文件（agate/tests/unit/ 下）→ 每写完 1 个文件立即追加 progress（文件名 + 用例数）
3. **第三步**：全部测试文件写完后，跑红灯验证（pytest 一律 `timeout 60s` + `-p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp`）→ 记录红灯结果

> 若任一步超过 10 分钟无法产出，立即停止并返回当前产物路径 + 卡点说明，不要无限继续。

### 返回

只返回两行：① P3-test-cases.md 路径；② 一句话摘要（含已产出测试文件清单；若未全量完成请如实说明完成/未完成数）。
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