---
phase: P3
generated_by: 主 Agent
task_id: TAG0029
role: test-designer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）
> 本次为 P3-A 批（重派第 2 轮拆批之一）：只做 BDD-1~3（解析器值清洗 + judge 双 locale），BDD-4~9 由 B 批另派。不要碰 BDD-4~9。

### 目标
产出 `agate/tests/unit/test_tag0029_gate_parser_fix_a.py`（BDD-1~3 用例）+ 在 P3-test-cases.md 写 A 批节（B 批随后增补，不是一次写完）。BDD-1~3 每条 ≥1 用例，当前跑即红，红因须是"被测未实现/旧语义"。

### 约束
- BDD-1：构造含行内注释的 gate_commands 块 fixture（tmp_path 写块文件，GATE_FILE env 调真实 `agate-read-gate-commands.py` 子进程）→ 断言输出 cmd 恰等于纯命令 + `bash -c` 执行 exit ≠ 2 且 stderr 无 EOF/unterminated 类文案。红因：旧解析器输出残渣 → 断言失败。
- BDD-2：构造引号未闭合块 → 断言 exit 非 0 + stderr 有解析错误 + 无残渣命令串。红因：旧解析器 exit 0 产残渣。
- BDD-3：直接调真实 `judge_result`（import check-tdd-red）：输入 exit_code=2 + 语法文案 + 零运行器统计 → 断言返回 1。双用例：中文（`寻找匹配`/`未预期`）+ 英文（`unexpected`/`matching`/`syntax error`）。推测项 `unmatched`/`找不到匹配`/`unterminated` 不得出现。红因：旧 judge 落末尾 exit 0。
- 真实调用（DEBT0024）：调真实解析器子进程 + 真实 judge_result，不 mock exit 码。
- 测试隔离：tmp_path；不裸 `python3` 字面（conftest python_exe fixture 或 `"python"+"3"` 拆写）；平台无关断言。
- 干净契约：本文件自身全树扫描 0 自伤（R1–R5 字面只出现在豁免形态或拆写）。
- 每写完一个 BDD 用例立即追加 `P3-progress-a.md`（分阶段落盘，空返回恢复依据）。
- 自跑全部用例确认红因正确后返回。返回前跑 check-frontmatter 自检 P3-test-cases.md（若你创建了它；B 批增补时复用）。
</dispatch_guide>

### 上游关联
- P2-design.md §3.1（值清洗算法）+ §3.3（judge 分支）+ §8 BDD-1~3 行；P2-review T1/T2 缺口。
- P3 首派空返回（无产出无 progress），本轮拆批 A 先行；B 批（BDD-4~9）随后另派。

### 输入文件
- `agate-workspace/tasks/TAG0029-gate-parser-fix/P2-design.md`（§3.1/§3.3/§8）
- `agate-workspace/tasks/TAG0029-gate-parser-fix/P1-requirements.md`（BDD-1~3 原文）
- `agate/scripts/agate-read-gate-commands.py`（被测 ①）
- `agate/scripts/check-tdd-red.py`（被测 ②，judge_result L87-157）
- `agate/tests/conftest.py`（python_exe / run_cli / agate_scripts fixture）
- `agate/tests/unit/test_check_tdd_red.py`（既有用例形态参照）

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
- worktree 根：`/home/kity/oclab/agateon/.worktrees/agate-TAG0029`。
- 产出文件：`agate/tests/unit/test_tag0029_gate_parser_fix_a.py` + `agate-workspace/tasks/TAG0029-gate-parser-fix/P3-test-cases.md`（A 批节；B 批增补）。
- progress 文件：`agate-workspace/tasks/TAG0029-gate-parser-fix/P3-progress-a.md`（每用例一落盘）。
- 红灯确认由主 Agent 用 TEST_RUNNER 覆盖执行；你只需自跑确认红因正确。
- 注：该文件禁止包含 verdict 预判。
</objective_info>
