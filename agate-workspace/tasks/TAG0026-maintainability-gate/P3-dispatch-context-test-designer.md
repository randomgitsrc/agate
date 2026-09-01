---
phase: P3
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0026
role: test-designer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

产出 `P3-test-cases.md` + 两个测试文件（红灯状态）：
- `agate/tests/unit/test_check_maintainability.py`（检测器，M9）
- `agate/tests/unit/test_check_gate_p4_maintainability.py`（P4 挂载，M10）

测试设计严格按 P2-design.md §5 的落点与分组（G1-G10 / G1-G7），每条用例 1:1 对应
P1 的 `#### BDD-NN`。**只写测试，不写实现**——实现是 P4 的事，测试此刻必须红。

### 约束

1. **TDD 红灯是硬门槛**：写完测试必须自跑 `check-tdd-red.py` 确认真红灯（exit 0）。
   红灯原因必须是"被测模块未实现"（`ModuleNotFoundError: check_maintainability` /
   assertion 失败 = B类）；若红灯是 `SyntaxError` / 第三方 import 失败（A类）= 测试代码
   自身错误，必须修好再交付。**禁止**为了让测试绿而写任何实现代码。
   注意：check_maintainability 模块不存在 → import 失败，两个测试文件会整体红——这是
   预期形态。但同一文件里不能有语法错误或第三方依赖缺失，否则 check-tdd-red 判 A类。
2. **测试设计以 P2-design.md §5 为蓝本**：分组、要点、fixture 选择均照 §5.1/§5.2 的表；
   P2-review 提出的 2 条测试建议（见客观查证信息 D）一并纳入。若你发现 §5 分组有遗漏
   BDD 或不可测的分组，先在 P3-test-cases.md 说明并给出修正分组，不要静默偏离。
3. **1:1 映射**：P3-test-cases.md 中每条测试用例必须标注对应的 `BDD-NN`；13 条 BDD
   全覆盖（BDD-1..13），不得挑验。
4. **平台无关硬约束**（AGENTS.md）：
   - 全部用 pytest `tmp_path` fixture，不用 /tmp
   - git 操作走 conftest 的 `git_repo` fixture，不裸 PATH、不假设 git 在固定路径
   - 解释器探测用 `python_exe` fixture（python3|python）
   - `AGATE_ROOT` 用 `agate_root` fixture（env 覆盖，CI 无 ~/.agate）
   - Windows 差异场景按平台分支断言或模拟（P2 §5.1 G7 的模拟路径方式），不假设
     POSIX symlink 语义
   - 不硬编码单平台绝对路径（`~/.venvs/...`、`/home/kity/...` 一律不出现在测试里）
5. **test_code_dir 声明**：P3-test-cases.md frontmatter/正文声明
   `test_code_dir: agate/tests/unit/`（P2 已定落点）。
6. **被测对象契约**（写测试的依据，P2-design §3.1/§3.2）：
   - `check_maintainability(task_dir) -> dict`：`{"git_ok": bool, "violations": [...],
     "god_file_count": N, "fuzzy_boundary_count": M}`
   - violation 条目：god-file → `{"type": "god-file", "file": ..., "detail": ...}`；
     fuzzy-boundary → `{"type": "fuzzy-boundary", "file": ..., "line": ..., "detail": ...}`
   - `check-gate.py P4` 三重门槛：violations 非空时 ① known-violations.md 存在 →
     ② `count_kf_entries` 登记 ≥ violations 数 → ③ P4-review approved + agent≠main
     （③ 由 gate_p4 既有检查承载，测试构造时要让 ①②③ 逐态可控）
   - 模块未实现 → `from check_maintainability import check_maintainability` 失败
   - CLI exit：0=无 violation 或 git 通道不可用；1=有 violation
   - 配置：`agate-workspace/maintainability.yaml`（repo_root 相对），键
     `god_file_threshold` / `fuzzy_patterns.python` / `fuzzy_patterns.typescript`，
     缺失/坏值全默认（N=1000）
7. **不改动任何非测试文件**：不改 conftest.py、不改既有测试、不建 agate/scripts/ 下的
   任何文件、不动 P4/P6 卡片。发现 fixture 不足时在 P3-test-cases.md 记录需求，不要
   自行改 conftest。
8. **范围锁定**：只覆盖 13 条 BDD + P2 §5 分组 + review 建议；不多测不少测。
9. **git 命令超时**：所有 bash 命令 `timeout` 包裹；git 操作仅在 tmp_path 的 fixture
   仓库内进行，禁止在 worktree 仓库本身做任何写操作（stage/commit 均不许）。

### 上游关联

- P1-requirements.md：13 条 BDD（验收对照）
- P2-design.md §3（契约细节）+ §5（测试落点与分组）+ §4（gate_commands.P3 = pytest）
- P2-review.md：实测锚点汇总 + 2 条测试建议
- conftest.py：`git_repo` / `task_dir` / `agate_root` / `python_exe` fixture（见客观查证信息 C）

### 输入文件（按顺序读）

1. `agate-workspace/tasks/TAG0026-maintainability-gate/P2-design.md`（重点 §3 契约 + §5 分组）
2. `agate-workspace/tasks/TAG0026-maintainability-gate/P1-requirements.md`（13 BDD 原文）
3. `agate-workspace/tasks/TAG0026-maintainability-gate/P2-review.md`（实测锚点 + 测试建议）
4. `agate/tests/conftest.py`（fixture 清单与用法）
5. `agate/tests/unit/test_check_gate_p5_diff.py`（gate 挂载测试结构先例）
6. `agate/tests/unit/test_agate_risk_score.py`（返回结构断言先例）
7. `agate/tests/README.md`（测试套件约定）
8. `AGENTS.md`（测试约定节）

### 产出文件字段

P3-test-cases.md 的 frontmatter 用 agate-md-field-set 填写（先 `--list`；报错照提示改；
不要手写 frontmatter；仍失败报告主 Agent）。关键字段：`phase: P3` / `task_id: TAG0026` /
`parent: P2-design.md` / `trace_id: TAG0026-P3-20260830` / `status: draft` /
`created: 2026-08-30` / `agent: test-designer`；正文声明 `test_code_dir: agate/tests/unit/`。
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
### A. 被测契约速查（来自 P2-design §3，主 Agent 已核）
- 模块：`agate/scripts/check-maintainability.py`（**尚未实现**——P4 才写）
- 函数：`check_maintainability(task_dir) -> dict`（`git_ok` / `violations` /
  `god_file_count` / `fuzzy_boundary_count`）
- violation 条目：god-file → `{type, file, detail}`；fuzzy-boundary → `{type, file, line, detail}`
- gate_p4 挂载（check-gate.py :870-927，新步骤将落在 :905 之后）：violations 非空 →
  ① known-violations.md 存在（无→exit 1）② count_kf_entries(登记) ≥ len(violations)
  （不足→exit 1）③ 评审检查（既有①②③：P4-review.md 存在/status=approved/agent≠main，
  缺失→1 或 2）④ git diff --cached 无代码文件→1
- 配置：`{repo_root}/agate-workspace/maintainability.yaml`；键 `god_file_threshold`（int，
  默认 1000）、`fuzzy_patterns.python`（list，默认 `^\s*except\s*:` + `#\s*type:\s*ignore`）、
  `fuzzy_patterns.typescript`（list，默认 `:\s*any\b` + `\bas\s+any\b`）
- CLI：`python3 check-maintainability.py {TASK_DIR}` → exit 0（无 violation/git 不可用）/
  exit 1（有 violation）

### B. check-tdd-red 语义（P3 卡 gate 规则）
- exit 0 = 真红灯（断言失败 / 项目内 import 失败）✅ 预期
- exit 1 = 假红灯（SyntaxError / 第三方 import 失败）❌ 测试自身错误
- exit 2 = 绿了（实现先于测试）❌ 违反 TDD
- exit 3 = 无测试运行器
- 探测链：gate_commands.P3（P2-design.md 已声明 `python3 -m pytest`）→ pytest

### C. conftest fixture（P2-design §5 引用的行段，architect 已核，用时以实际为准）
- `git_repo`（:264-302）：tmp git 仓库封装（init/stage/commit）
- `task_dir`（:374-394）：任务目录 fixture
- `agate_root`（:305-312）：AGATE_ROOT env 覆盖
- `python_exe`（:358-365）：python3|python 探测
- 先例文件：`test_check_gate_p5_diff.py`（gate 挂载结构）、`test_agate_risk_score.py`
  （dict 返回断言）

### D. P2-review 评审提出的 2 条测试建议（纳入设计）
1. **G5（回归面）建议补"既有失败路径逐项等价"断言**——不只断言"无 violations 时 exit 0"，
   还要断言 gate_p4 既有 ①②③④ 失败路径（P4-review 缺失/status 非 approved/agent=main/
   无 staged 代码）的返回值在改动前后一致（P2-review §"测试缺口"）
2. **G6（ImportError 降级）建议用 monkeypatch 模拟**——直接 patch
   `check-gate` 模块的 `check_maintainability` 属性为 None 验证 WARNING 路径，比模拟
   import 失败更稳定（同节建议）

### E. 环境事实
- worktree dogfooding：测试在 worktree 跑（`python3 -m pytest agate/tests/unit/...`）；
  禁止对 worktree 仓库本身做 git 写操作，git fixture 全部在 tmp_path
- 基线全量 pytest 全绿（2026-08-30 实测）；新增测试文件暂时全红是预期
- 平台无关硬约束见约束 4；测试内不得出现 `/home/kity` 等绝对路径
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
