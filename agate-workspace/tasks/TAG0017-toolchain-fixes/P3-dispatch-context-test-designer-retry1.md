---
phase: P3
generated_by: 主 Agent（修复轮，增量模式，跨批次汇总修复）
task_id: TAG0017-toolchain-fixes
role: test-designer
retry_round: 1
---

<dispatch_guide>
> ⚠️ 修复轮——主 Agent 亲自执行了 `gate_commands.P3`（`python3 -m pytest agate/tests/`，与 P2-design.md §5 完全一致的命令）与相关静态检查后，发现 3 处由 5 个并行批次产生的**测试代码卫生问题**（不是 BDD 覆盖或方案设计问题），需一次性修复。三处分属不同批次原本负责的文件，但修复内容都是局部、机械的，故合并为一轮统一派发，不需要按批次分别处理。

### 修复目标（共 3 项，逐项精确定位，不要额外改动其他内容）

**1. `agate/tests/unit/test_check_tdd_red.py` 第 723-742 行（`test_bdd_2_timeout_seconds_declared_real_a_class_failure_stays_a_class`，fg1-parser-scripts 批次产出）**

第 726 行的字符串字面量 `"Traceback (most recent call last):\nSyntaxError: invalid syntax"` 是问题根源：主 Agent 亲自执行 `python3 -m pytest agate/tests/`（无 `-q`/`--tb=short`，与 P2-design.md 声明的 `gate_commands.P3` 完全一致）后发现，由于该测试当前处于红灯（`is_gate_meta_key` 尚未实现），pytest 默认详细模式会把这个测试函数的完整源码（含这行字符串字面量）回显到失败报告里。这导致**外层** `python3 -m pytest agate/tests/` 整体运行的原始输出里出现了 `Traceback`/`SyntaxError` 子串，而 `check-tdd-red.py` 在无 formatter 声明时的兜底逻辑（第 110 行 `re.search(r"Traceback|SyntaxError|ImportError|ModuleNotFoundError", raw_output)`）会把**整个外层 gate 判定**误判为 A 类错误（假红灯），即使这个字符串只是测试内部构造的模拟数据、不是真实的编译/导入错误。

**修复方式**：把这个字符串字面量改写成不含连续可匹配子串 `Traceback` 或 `SyntaxError` 的等价构造（运行时值必须完全不变，因为它是喂给内部 `_make_fake_pytest` 的模拟输出，测试语义不能变）。推荐用字符串拼接拆开触发词，例如：
```python
"Trace" + "back (most recent call last):\n" + "Syntax" + "Error: invalid syntax"
```
或改用 `"".join([...])` 等价写法。**只改这一处（第 726 行）**，不要动第 750 行 `test_bdd_30_no_formatter_compile_error_a_class` 里同样的字符串——那是既有测试（非本任务产出），当前处于绿灯状态，不受本问题影响，不要碰它。

**2. `agate/tests/unit/test_self_gate_naming_docs.py` 第 24 行（fg2-self-gate-naming 批次产出）**

`import pytest` 未被使用，触发 `ruff check agate/` 报 F401（`agate_root` 全量 lint 回归，主 Agent 亲自跑 `ruff check agate/` 复现）。**修复方式**：删除这行未使用的 import（若文件其余部分确实不需要 pytest 提供的 fixture/装饰器/mark；若你核实后发现其实某处间接需要，改为实际使用而非删除，但当前 ruff 报告显式指出未使用，大概率可直接删除）。

**3. `agate/tests/integration/test_pre_commit_hook.py` 第 1462 行附近（fg4-windows-python-probe 批次产出）**

断言消息字符串 `f"探测循环未跳过不可执行的 python3 候选（{hook_filename}）："` 中的裸词 `python3` 触发 `check-platform-assumptions.py` 的 R2 规则（`agate/scripts/check-platform-assumptions.py agate/tests` 主 Agent 亲自跑复现，报告 `R2 agate/tests/integration/test_pre_commit_hook.py:1462`）。R2 规则设计用于捕获"裸 `python3` 命令引用"（DEBT0014 本身要修的那类缺陷），但此处是中文断言消息里的自然语言描述，被误判为命令引用。

**修复方式**：改写这条消息，避免 `python3` 作为独立单词出现在正则可匹配的位置（正则形如 `(^|[\s=(\'\"])python3([\s]|$)`，匹配"前面是行首/空白/等号/括号/引号，后面是空白/行尾"的裸 `python3`）。可选做法：把 `python3` 改成不触发正则边界匹配的写法（如 `Python3` 大写开头——需确认 regex 是否区分大小写，或更稳妥地整句改写为不含 `python3` 独立词的表达，如"探测循环未跳过不可执行的 Python 解释器候选"）。**同样检查同一批次的其他断言消息**（如 BDD-11 用例、其他 hook 文件的对应位置）是否有相同模式，一并订正，不要只改这一处然后漏掉同结构的其他地方。

### 约束
1. **双工作区纪律**：只读写 worktree，不碰主 checkout 或 `~/.agate`。
2. **只做上述 3 项机械修复**，不要改动测试的其他断言逻辑、不要改动其他批次未提及的文件、不要碰任何非测试代码（脚本本身、协议文档均不在本轮范围）。
3. **验证修复有效**（强制自检步骤）：
   - 修复 1 后：跑 `python3 -m pytest agate/tests/ 2>&1 | /usr/bin/grep -c "Traceback\|SyntaxError\|ImportError\|ModuleNotFoundError"` 应为 0（或若仍有命中需确认命中处不是本次引入的假阳性）
   - 修复 2 后：跑 `ruff check agate/` 应无 F401
   - 修复 3 后：跑 `python3 agate/scripts/check-platform-assumptions.py agate/tests` 应无 R2 命中
4. **不要引入新的红灯变化**：修复后重新跑一次 `python3 agate/scripts/check-tdd-red.py {task_dir}`（task_dir 见下方 objective_info），确认返回 exit 0（真红灯，非 A 类）。

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0017-toolchain-fixes/P2-design.md（§5 gate_commands 声明，确认 P3 命令原文）
- agate/tests/unit/test_check_tdd_red.py:715-742（问题 1 上下文）
- agate/tests/unit/test_self_gate_naming_docs.py:1-30（问题 2 上下文）
- agate/tests/integration/test_pre_commit_hook.py:1400-1500（问题 3 上下文）
- agate/scripts/check-platform-assumptions.py:30-60（R2 规则定义，理解匹配边界）
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
- 主 Agent 独立执行结果：`python3 -m pytest agate/tests/`（P2 声明的 gate_commands.P3 原文命令）→ 43 failed, 968 passed, 2 skipped（均为合理 AssertionError，无真实 SyntaxError/ImportError）；`python3 agate/scripts/check-tdd-red.py {task_dir}` → exit 1（A-class 误判，根因见修复目标 1）
- task_dir: /home/kity/oclab/agate/.worktrees/agate-TAG0017/agate-workspace/tasks/TAG0017-toolchain-fixes
- 本轮是 retries[P3] 第 1 轮（P3 MAX=2）
</objective_info>
