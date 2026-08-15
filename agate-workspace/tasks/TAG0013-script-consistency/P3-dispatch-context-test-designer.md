---
phase: P3
generated_by: 主 Agent
task_id: TAG0013-script-consistency
role: test-designer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令。执行优先级：派发指引 > 客观查证信息 > 阶段卡片。
> 你是 TAG0013（agate 脚本一致性批）的 P3 测试设计师。**只产出 P3-test-cases.md + 测试代码，不修改被测脚本/实现。**

### 目标

产出 P3-test-cases.md（测试用例清单）+ 测试代码（追加到现有测试文件），覆盖 P1 全部 11 条 BDD（1:1 映射）。本任务是**功能任务**（非 refactor）→ 走标准 TDD 口径：测试当前必须红灯（实现未写）。

### 约束

- 只写测试；**不修改被测脚本**（check-protocol-consistency.py / commit-msg-self-gate.py / check-retrospective.py）；不 commit
- **测试代码追加到现有测试文件**（不改既有用例，只新增）：
  - CHECK 10 相关 → `agate/tests/unit/test_check_protocol_consistency.py`
  - self-gate 相关 → `agate/tests/unit/test_commit_msg_self_gate.py`（新增 ≥3 用例：README 触发 / AGENTS 触发 / CHANGELOG 豁免）
  - 复盘提醒 → `agate/tests/unit/test_check_retrospective.py`（新增 2 用例：有异常 → DEBT+roadmap 提醒 / 无异常 → 空输出）
- **夹具选型（P2 已推荐）**：CHECK 10 用例走**最小假协议树夹具**——构造临时目录（pytest tmp_path）含 `agate/scripts/*.py` 假文件 + 协议 md 文件，importlib 加载 check-protocol-consistency.py 模块（复用现有 `_load_cpc` 模式）后调用 `check_script_name_refs`。**不要**对真实 worktree 全仓扫描（会被 CHANGELOG 聚合 WARNING 干扰，且测试平台无关原则要求临时目录）
- **BLOCKER-1 回归断言（P2-review §3 缺口 8）**：补一条「CHECK 10 报 ERROR/WARNING 时 CHECK 1 状态行独立」断言——对 main() 状态匹配逻辑做单元断言（`e["check"].split("-")[0] == key` 场景：CHECK10-scriptref 不被 CHECK1 前缀匹配；以及旧逻辑 `startswith("CHECK1")` 误标的锁定）
- 测试名引用 BDD 编号（如 `test_bdd_1_*` / `test_bdd_3_*`），可追溯
- 平台无关：不用裸 python3（用 conftest py_path fixture）、不用 /tmp（用 pytest tmp_path）、不假设 POSIX symlink（测试不创建软链）
- 测试当前必须红灯：`check_script_name_refs` / `_SELF_GATE_RE` 扩展 / 提醒行均未实现 → 新增用例应失败（断言目标行为不存在）
- 自查≠gate：不声称"P3 已过 / 红灯正确"

### 上游关联

- P1-requirements.md approved：11 条 BDD（BDD-1..11），豁免清单 5 类，扫描范围=协议文档面
- P2-design.md approved：候选方案 A（CHECK 10 内联 `check_script_name_refs` + `SCRIPT_REF_RE` + `SCRIPT_REF_SCAN_FILES/DIRS` + PROTOCOL_DIRS 3 目录 + main() 状态匹配 `split("-")[0]`）；self-gate 精确名锚定 `|README\.md|AGENTS\.md`；复盘提醒行在 `if warnings:` 块内
- P2-review.md approved：BLOCKER-1 修复已纳入；豁免② forward-defense；agate_common.py 入白名单（下划线形状）；基线 751

### 输入文件

1. `{AGATE_WORKSPACE}/tasks/TAG0013-script-consistency/P1-requirements.md`（BDD 验收条件）
2. `{AGATE_WORKSPACE}/tasks/TAG0013-script-consistency/P2-design.md`（方案 + §2 测试策略节 + files_to_read §6 + gate_commands §5）
3. `{AGATE_WORKSPACE}/tasks/TAG0013-script-consistency/P2-review.md`（§3 测试缺口 + §4 锁定决策）
4. 角色定义：`agate/assets/execution-roles/test-designer.md`
5. 现有测试（追加对象，参照其用例模式）：
   - `agate/tests/unit/test_check_protocol_consistency.py`（_load_cpc importlib 模式）
   - `agate/tests/unit/test_commit_msg_self_gate.py`（git_repo fixture + _run_csg helper，4 个既有用例）
   - `agate/tests/unit/test_check_retrospective.py`（task_dir fixture + _run_retro helper，RT.1 空输出）
6. 被测脚本（了解当前行为，不修改）：`agate/scripts/check-protocol-consistency.py`、`agate/scripts/commit-msg-self-gate.py`、`agate/scripts/check-retrospective.py`
7. `agate/tests/conftest.py`（fixture：git_repo / task_dir / run_cli / py_path / bash）

### 客观查证信息（已核实）

- `test_check_protocol_consistency.py`：`_load_cpc` 通过 importlib 加载 worktree 的 check-protocol-consistency.py；现有用例断言常量/函数
- `test_commit_msg_self_gate.py`：恰好 4 用例（test_cmsg_1..4），git_repo fixture 造暂存区
- `test_check_retrospective.py`：RT.1 断言 `result.output == ""`（无异常空输出）
- 当前 count-tests.sh 基线 = 751
- P2 gate_commands：P3 = `python3 -m pytest agate/tests/ -q --tb=short`

### 产出要求

**P3-test-cases.md** 必须包含：
1. `test_code_dir: agate/tests/unit/` 声明（测试代码追加到现有文件，路径为仓库内相对路径）
2. 用例清单：编号 + 对应 BDD-NN + 文件 + 测试名 + 预期（当前红灯原因）
3. BDD 1:1 映射表（11 条 BDD → 测试用例）
4. 夹具选型说明（最小假协议树方案）

**测试代码**：直接修改三个现有测试文件（追加用例，不改既有用例）。

### 返回给我

- P3-test-cases.md 路径
- 测试文件路径清单（修改了哪些文件）
- 用例数（多少条 BDD 已映射）
- 当前红灯确认（跑了哪些测试、失败原因）
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
