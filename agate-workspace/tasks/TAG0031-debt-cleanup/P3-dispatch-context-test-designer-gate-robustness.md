---
phase: P3
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0031
role: test-designer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）
> 本次是并行拆批之一（batch id: gate-robustness，P2 dispatch_plan 声明的三簇之一）。只负责本簇的测试用例，不要写其他簇（版本管理域/测试隔离）的测试。

### 目标
为「check-gate.py 健壮性」簇（DEBT0016/17/18）写测试用例，产出 `P3-test-cases-gate-robustness.md` + 对应测试代码。覆盖 BDD-8/9/10/11/12/13/14/15。

### 约束
- **1:1 映射 BDD**：
  - BDD-8（gate_p4 CODE-MAP 路径改用 resolve_workspace，正常流）/ BDD-9（非标准两级嵌套场景，边界流，DEBT0016）
  - BDD-10（自指场景说明性文字不误判，异常流）/ BDD-11（标题真实存在时判定通过，正常流，DEBT0017）
  - BDD-12（agate_common 不可导入时 4 个关键读取器显式失败，异常流）/ BDD-13（正常可导入时行为逐字节不变，回归，DEBT0018）
  - BDD-14（同类未处理实例登记为新 DEBT——这是 P8 阶段动作，P3 可选择不写自动化测试，改为在 `P3-test-cases-gate-robustness.md` 里记录"此 BDD 为登记动作，非代码断言，验证方式见 P6/P8"）
  - BDD-15（六条 DEBT 登记闭合，跨簇聚合——同样是登记动作，可设计一个简单断言/grep 命令模板，检查 `debt/tech-debt.md` 中 DEBT0002/0003/0004/0016/0017/0018 六个 ID 的 `status:` 字段，当前均为 open（红），P4 全部实现完成后应全部 closed（绿）。这条测试/断言归属本簇产出，因为本簇是三簇中最后完成、适合做"收尾聚合检查"的天然位置）
- **DEBT0012 R2 风险提醒（P2-design.md §1.3 R2）**：`count_p6_pass_fail`（gate_p6）/`count_p7_markers`/`count_code_map_lines`（gate_p7）三个消费点**仅在旧格式回退分支**（frontmatter 计数字段为空时）才会被调用，新格式（字段已声明）时根本不会触达。写 BDD-12 测试时必须显式构造**旧格式**（无 frontmatter 计数字段）的 P6-acceptance.md/P7-consistency.md fixture 才能命中降级哨兵分支——写"新格式下也能测出 fail-closed"的测试是假绿，不要这样写。`read_rules_yaml`（gate_p1）无此限制，是无条件调用点，测试构造更直接，可作为该场景的主力用例。
- **DEBT0016 R3 边界（P2-design.md §1.3 R3）**：BDD-9 只需覆盖"非标准两级嵌套 + agate_common 可用"场景（验证走 resolve_workspace 分支能正确解析），**不要求**覆盖"agate_common 不可用 + 非标准嵌套"的组合场景（P1 未要求，超出本次范围，写了也不算错但不是必须）。
- **红灯类型**：确保是 B 类错误（assertion 失败，非语法错误）。DEBT0016/17/18 均为 check-gate.py 内部判定逻辑改动，测试应能直接调用 check-gate.py 里的相关函数（如 `gate_p4`/`gate_p1`/`gate_p6`/`gate_p7` 或其内部辅助函数），断言当前行为（未实现新逻辑）与预期不符从而失败。
- **test_code_dir 声明**：`agate/tests/unit/test_check_gate.py`（既有文件，新增用例插入位置参照其组织方式）。

### 上游关联
- P2 architect 方案（approved，2 轮）：R2/R3 风险与缓解措施已在 P2-design.md §1.3 明确声明，测试设计需遵循这些边界，不要"好心"扩大覆盖范围导致假绿或超范围
- 本簇 `agate_common.py` 只涉及 import 列表追加（`check-gate.py` 顶部 import `resolve_workspace`），不改 `agate_common.py` 本体（与簇 A 的 `compute_sha256` 新增互不冲突，见 P2-design.md §1.3 R5）

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0031-debt-cleanup/P2-design.md（§1.1 簇 C 改动点表 + §1.3 R2/R3/R5 + §4 files_to_read 簇 C 部分）
- {AGATE_WORKSPACE}/tasks/TAG0031-debt-cleanup/P1-requirements.md（BDD-8~15 原文 + 同类扫描第 3/4 小节）
- /home/kity/oclab/agateon/.worktrees/agate-TAG0031/agate/scripts/check-gate.py（L30-166 + L975-996 + L1074-1098 + L1128-1245）
- /home/kity/oclab/agateon/.worktrees/agate-TAG0031/agate/scripts/agate_common.py（L875-906，re.MULTILINE 标题匹配写法参照）
- /home/kity/oclab/agateon/.worktrees/agate-TAG0031/agate/tests/unit/test_check_gate.py（既有测试组织方式）
- /home/kity/oclab/agateon/.worktrees/agate-TAG0031/agate-workspace/debt/tech-debt.md（BDD-15 六条 DEBT 状态字段现状核对）
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
- 关键标识：test_code_dir 见「约束」节；三簇并行，其余两簇分别由其他 subagent 同时处理
- 查证结果：本节不预查证测试内容——由你自行读取现状代码确认判定逻辑
</objective_info>
