# P3-dispatch-context-test-designer — TAG0022 TDD 红灯批

> 派发对象：test-designer（P3 测试设计）。这是本轮的强制指令，不是参考信息。
> 任务目录：`{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/`

## 目标

产出 `P3-test-cases.md` + **失败测试代码**（TDD 红灯批）——为 BDD-3/5/6/7/9/10（0038 迁移 / 0039 judge / 0041 环境测试三个子项的可写测试面）写**先于实现**的测试，P4 才实现使其转绿。BDD-1/2（0037 workflow/ruff）与 BDD-4/8 无 P3 测试面（CI 配置/文档/计划交付，P5/P6 验证）。

## 输入文件（逐一读，每读完追加 progress）

1. `{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/P1-requirements.md`（BDD-1..10）
2. `{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/P2-design.md`（**§3 完成标准 + §4.2.1 逐点映射清单 + §4.3 判据 + §4.5 0041 方案 + §7 files_to_read**）
3. `{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/P2-review.md`（**NB-1~6 + TG-1~3 非阻塞闭环项，P3 必须落实**）
4. `{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/P0-brief.md`（环境约束）
5. `{agate_root}/phase-cards/P3-tdd.md` + `{agate_root}/assets/execution-roles/test-designer.md`（角色定义）

## 必读的测试现状文件（worktree `agate/tests/`）

- `agate/tests/unit/test_check_gate.py`（L2626-2689 gate_p65 judge 三态用例参照 + P1 分支用例区，0039 新增用例挂靠）
- `agate/tests/unit/test_check_routing.py`（**test_bdd_7** L148-156 + `_run_routing` helper L20-26，0041 改造对象）
- `agate/tests/unit/test_env_adapt_docs.py`（**test_bdd_25** L47-60，0041 改造对象）
- `agate/tests/unit/test_check_structure_consistency.py`（S-* 既有用例，S-3a/S-3b 漂移用例挂靠，NB-1：既有 S-3 outputs/orphan/exec_role 用例必须保持绿）
- `agate/tests/conftest.py`（create_task_dir / run_cli / task_dir / tmp_path fixture；run_cli 的 env 参数支持：`_run_cli_impl` L55-71 已支持 env 注入——NB-5）

## 测试设计规格（按子项）

### 0038（BDD-3/5）

1. **新文件 `agate/tests/unit/test_md_parse_scan.py`（BDD-3 静态扫描）**：按 P2 §4.2.1 逐点映射清单的 A/B/C/D 组模式（`_frontmatter_field` 字面调用 / `_NC_RE` 等标记正则使用 / `re.finditer(r"```(?:yaml|yml)"` 内嵌 yaml 块 / 任务产出格式判定正则调用位置），静态扫描 `agate/scripts/check-gate.py` 断言「协议规则类 md 解析点命中数 = 0」。**P3 现状 check-gate.py 未迁移 → 扫描有命中 → 测试失败（红）**（A/B/C/D 组模式仍字面存在；E/F 组 `.state.yaml` 读取与 git/CHANGELOG 解析不计入）。
2. **`agate/tests/unit/test_check_structure_consistency.py` 增补 S-3a/S-3b 双向漂移用例（BDD-5，TG-1）**：
   - 人为单侧漂移（若可实现夹具：改卡片 `## gate 规则` 加机器可判定命令行不入 YAML → S-3b ERROR；或改 phases.yaml gates 命令不动卡片 → S-3a ERROR）→ 非 0 退出
   - 双侧一致 → exit 0
   - **P3 现状 S-3a/S-3b 未实现 → 漂移不报 → 测试失败（红）**
   - 确保既有 S-3 outputs/orphan/exec_role 用例（含「产出规格缺失 P2-review.md → 非 0」）不因新增用例回归（NB-1）

### 0039（BDD-6/7，TG-2 边界全补）

3. **`agate/tests/unit/test_check_gate.py` 增补 judge P1 校验用例**（gate_p1 分支，fixture 构造见 conftest create_task_dir 用法）：
   - 机制后新任务（P1 frontmatter `created: 2026-08-22` ≥ judge_required_since）且 `.state.yaml` 无 judge 块 → `check-gate.py P1` exit 1（**P3 现状无该校验 → 现为 exit 2 → 测试失败（红）**）
   - 机制后新任务含 `judge.enabled: true` → exit 2 放行（P3 现状即绿，回归守卫）
   - 历史任务（created: 2026-08-19 或缺失 created）无 judge 块 → 不拦（P3 现状绿）
   - `judge.enabled: false` 且机制后 → exit 1（NB-4：falsy 与缺失同走 created 判据——falsy + created ≥ cutoff → exit 1；falsy + pre-cutoff → 跳过；按 P2-review 锁定决策 2 与 NB-4 的推荐口径设计断言）
   - created 非 ISO / 缺失 → fail-open 不拦
   - judge 非 dict（如 `judge: true` bool）→ 按缺失处理（fail-open）
   - 既有 gate_p65 judge 三态用例（L2663-2689）保持绿（锁定决策 5）

### 0041（BDD-9/10）

4. **`agate/tests/unit/test_check_routing.py` 改 test_bdd_7**（P2 §4.5.1）：`_run_routing` 增 env 透传（NB-5），test_bdd_7 注入 `GIT_CEILING_DIRECTORIES=<tmp_path>` 使 git 上下文确定化（git_ok:false 语义），不依赖 basetemp 位置；保持平台无关（无裸 PATH/python3 假设）。断言按设计：thin + 算分异常 + git_ok:false → exit 1。
5. **`agate/tests/unit/test_env_adapt_docs.py` 改 test_bdd_25**（P2 §4.5.2 + M15）：basetemp 位于仓库根下时注入 `AGATE_CONSISTENCY_SKIP_DIRS=<basetemp 相对根 rel 路径>`，使一致性检查免疫 basetemp 污染；两种位置（仓库内/仓库外）断言口径。**P3 现状 M15 未实现 → env 无效果 → 仓库内位置仍失败（红）**。
6. **M15 排除钩子单测（TG-3）**：落点 `agate/tests/unit/test_env_adapt_docs.py`（或 test_check_protocol_consistency.py 若存在）——注入 `AGATE_CONSISTENCY_SKIP_DIRS` 后 `iter_md_files` 不产出被排除路径；默认未设置时行为不变（扫面变化可观测）。

## 约束（硬约束）

1. **TDD 红灯**：新测试写完必须红，且是**真红灯（B 类）**——assertion 失败 / 项目内（agate.scripts / agate.tests）import 失败。**禁止假红灯（A 类）**：SyntaxError / 第三方 import 失败 / 测试代码自身错误。写完自跑（`python3 -m pytest <目标文件> -q -p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp -x`，bash 加 timeout）确认每个红灯失败原因都是「被测模块未实现/行为未变更」，不是断言与数据矛盾。
2. **P3 只写测试，不碰生产代码**：不得修改 `agate/scripts/*.py`（除非 test_bdd_7 的 `_run_routing` 属测试 helper 需改——那是测试文件自身，可改）。
3. **test_bdd_7 改造后若转绿**（git 核心机制使隔离即时生效）属预期，不构成「实现先于测试」——红集是 0038/0039 的新测试与 test_bdd_25（M15 未实现仍红）；在 progress 里如实记录每个测试的红/绿状态。
4. **平台无关**：不引入裸 `PATH=`/裸 `python3`/POSIX symlink 硬假设/`/tmp` 字面；use pytest tmp_path fixture。
5. **不破坏既有测试**：目标文件的既有用例保持绿为主（判死例外：该测试恰是本次改造对象）。
6. 环境：/tmp 只读 → pytest 一律 `--basetemp=/home/kity/oclab/dsh-workspace/ptmp -p no:cacheprovider`；bash 一律 timeout；双工作区纪律（写测试到 worktree `agate/tests/`，稳定版只读）。

## 产出规格

1. `{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/P3-test-cases.md`：Header（phase: P3 / task_id: TAG0022-confirmed-problems / type: test-cases / parent: P2-design.md / trace_id: TAG0022-P3-20260822 / status: draft / agent: test-designer）+ 声明 `test_code_dir: agate/tests/unit/` + BDD-NN ↔ 测试文件 ↔ 用例描述 ↔ 预期红灯类型（B 类）1:1 映射表
2. 测试代码写入 worktree `agate/tests/unit/`（新增 test_md_parse_scan.py + test_check_gate.py 增量 + test_check_structure_consistency.py 增量 + test_check_routing.py 改 + test_env_adapt_docs.py 改）

## 分阶段落盘

每读完输入/写完每个测试文件/每次自跑，追加写 `{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/P3-progress.md`（含每个测试的红/绿状态 + 红灯失败原因一句话）。

## 门槛（什么算完成）

- P3-test-cases.md 存在且非空，含 `test_code_dir`，BDD 映射表 1:1 覆盖本次可写测试面（BDD-3/5/6/7/9/10）
- 测试代码已写入 worktree `agate/tests/unit/` 对应文件，自跑确认：红集测试真的红（B 类），原因是被测模块未实现/行为未变更
- 既有用例无意外破坏（progress 记录）

## 返回给我

只返回两行：① P3-test-cases.md 路径（+ 测试文件清单路径）；② 一句话摘要（N 个测试用例，红集状态）。绝不返回文件全文。

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