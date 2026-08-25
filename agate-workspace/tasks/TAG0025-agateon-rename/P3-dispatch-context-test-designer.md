---
phase: P3
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0025
role: test-designer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
把 P1-requirements.md 的 16 条 BDD 逐条转成测试用例（1:1 映射），产出 `P3-test-cases.md` +
测试代码目录。**本任务不是传统应用逻辑开发，大部分"实现"是文本文件的字符串替换 + 一次不可逆的
外部操作（GitHub 仓库改名）**，因此 16 条 BDD 分成两类，测试设计方式不同，必须分别处理：

**A 类（可 TDD 红灯，BDD-1~10，10 条）**：改动落在本地文件（README/CHANGELOG/install.sh/
agate-*.py），改前即可写出会失败的断言（文件当前不含目标字符串/不含目标段落结构）。这类必须
写成真实可运行的 pytest 测试代码，落在 P2-design.md 已声明的 `agate/tests/regression/` 目录
（P2 已在 gate_commands.P3 里声明 `python3 -m pytest agate/tests/regression/ -v`，formatter
为 `pytest.sh`——你写的测试文件就是这条命令实际会跑的东西，命令本身不需要你改）。

**B 类（不可 TDD 红灯，BDD-11~16，6 条）**：依赖一次尚未发生、且要等主 Agent 获得用户在场确认
后才会执行的不可逆外部操作（GitHub 改名）。这类 BDD 的"测试"在改名发生之前既无法写出有意义的
失败断言（旧仓库当前返回 200，不是"应该失败但当前失败"的红灯，而是"当前根本不适用"的状态），
也不应该被塞进 pytest 里假装是单元测试。**P2-design.md 已经为这 6 条各自声明了对应的
gate_commands key（P5_bdd11 起到 P5_bdd16，具体见 P2-design.md 正文 gate_commands 块）**——
你的任务是在 P3-test-cases.md 里把这 6 条显式登记为"程序化验证用例"（不是 pytest 用例），
一一引用对应的 gate_commands key 名，并说明为什么它们不适用红灯语义（不是偷懒不测，是这类
用例的执行时机本质上晚于 P3/P4，要等不可逆操作真正发生之后才能跑）。这仍然满足"1:1 映射"要求
——映射的目标是"每条 BDD 都有明确对应的验证手段"，不是"每条 BDD 都必须是 pytest 函数"。

### 约束

1. **A 类测试文件命名**：沿用 P2-design.md 候选方案已确定的文件名
   `agate/tests/regression/test_repo_url_no_stale_rename.py`（若你认为需要拆成多个文件，需在
   P3-test-cases.md 里说明理由；默认沿用 P2 已定的单文件，避免和 P2 固化的 gate_commands 产生
   路径不一致）。
2. **A 类断言设计要覆盖 P2-review.md 指出的测试缺口（重要，不是可选项）**：P2-review.md 的
   「测试缺口」节指出 `gate_commands.P5_bdd4to8_new_url_present` 只验证"新 URL 存在"，不验证
   "旧 URL 已清除"——单靠这条 gate key 拦不住"README.md 两处 URL 只改一处"（BDD-7/8 明确禁止）。
   P2-review 已确认这个缺口由你即将写的这个回归测试兜底。**因此你的测试断言必须同时覆盖两个
   方向**：① 5 个核心文件（install.sh / agate-install.py / agate-changes.py / README.md /
   README.zh-CN.md）各自不含字面 `randomgitsrc/agate\b`（旧 URL 已清除，word-boundary 排除
   `agateon` 误判）② 同时含 `randomgitsrc/agateon`（新 URL 已存在）——两个方向都要断言，不能
   只写其中一个方向就以为覆盖了 BDD-7/8。测试文件顶部注释需要写明"本测试同时承担
   gate_commands.P5_bdd4to8_new_url_present 未覆盖的旧 URL 完全清除校验"（P2-review 非阻塞
   建议，请落地）。
3. **A 类还需覆盖 BDD-1/2/3（品牌声明 + CHANGELOG）**：可以在同一个测试文件里追加独立的测试
   函数（`test_bdd_1_...`/`test_bdd_2_...`/`test_bdd_3_...`），分别断言 README.md/README.zh-CN.md
   首屏含品牌声明句、CHANGELOG.md 含 `## [Unreleased]` 段且段下含 TAG0025 条目。当前这些内容
   都不存在，所以这些测试函数当前必须失败（红灯）——这是判断你是否真的做到"测试先于实现"的
   关键验证点。
4. **BDD-9（批次原子性）不适合塞进 pytest**：这条的判定逻辑是"检查 git commit 历史"，在测试
   设计阶段（改动尚未发生）没有真实断言对象可写（跑了也没有意义——git log 里还没有对应的 commit）。
   把它归入 A 类还是 B 类由你判断并在 P3-test-cases.md 里说明理由，两种处理都可以：要么写一个
   pytest 测试但明确注明"本用例在 P3/P4 阶段跑不出有意义的结果，仅在 P6 验收时通过
   gate_commands.P5_bdd9_atomic_commit 生效"，要么直接归入 B 类程序化验证用例。不要为了凑"A
   类必须是 pytest"而写一个此刻恒定失败但和真正的判定逻辑（git log SHA 比对）没有关系的假断言。
5. **不要修改 P2 已固化的 gate_commands**：P2-design.md 的 gate_commands 已经过 plan-eng-review
   评审通过、"P2 固化后 P4-P6 不能改"是协议纪律。你只能在 P3-test-cases.md 里**引用**这些 key
   名，不能改写它们的内容。
6. **不涉及 UI/Playwright**：`ui_affected: false`（P2 已声明），不需要 E2E 用例。
7. **不是 refactor 任务**：P1 未声明 `change_type: refactor`，走常规 TDD 口径（不是回归测试口径），
   check-tdd-red.py 红灯步骤正常适用于 A 类测试。

### 上游关联

- P1-requirements.md（approved，16 条 BDD，已含 P2 阶段追加的 BDD-10 第 5 类豁免
  `[BASELINE_CHANGE]` 标注）
- P2-design.md（approved by plan-eng-review）：候选 B 已选定（改名从 P4 抽离，主 Agent 亲自
  执行）；`gate_commands.P3 = "python3 -m pytest agate/tests/regression/ -v"`（formatter:
  `pytest.sh`）——这条命令就是 check-tdd-red.py 会跑的红灯探测命令
- P2-review.md「测试缺口」节（约束 2 已引用其核心内容）

### 输入文件（按顺序读）

1. `agate-workspace/tasks/TAG0025-agateon-rename/P1-requirements.md`
2. `agate-workspace/tasks/TAG0025-agateon-rename/P2-design.md`（重点：§0.1 影响面表、候选方案
   §1 的"其余分歧点"节、gate_commands 块全文）
3. `agate-workspace/tasks/TAG0025-agateon-rename/P2-review.md`（重点：核查项 3「测试缺口」）
4. `agate-workspace/tasks/TAG0025-agateon-rename/P0-brief.md`

### 产出文件字段
用 `FILE={AGATE_WORKSPACE}/tasks/TAG0025-agateon-rename/P3-test-cases.md agate-md-field-set --list`
查看本阶段应填字段；`FILE=... agate-md-field-set <key> <value>` 逐个写入；写入失败照错误提示
修正，不要手写 frontmatter；仍失败则报告主 Agent，不要绕开 set。`test_code_dir:` 字段填
`agate/tests/regression/`。
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
- 环境基线已捕获（`agate-capture-env-baseline.py` 已跑，2026-08-26）：
  `python3 -m pytest agate/tests/unit/ -q --tb=no` 无失败、
  `python3 -m pytest agate/tests/ --ignore=agate/tests/unit -q --tb=no` 无失败——当前全仓测试
  套件本就是绿的，你新写的测试文件里的断言失败必须是"因为改动尚未发生"（B 类真红灯），不能是
  环境/依赖问题（A 类假红灯）
- `agate/tests/regression/` 目录当前是否已存在、目录下现有哪些测试文件，请自己 `ls` 确认——
  按现有目录的文件组织风格新增文件，不要另起结构
- P2-design.md 的 gate_commands 已声明（供你在 P3-test-cases.md 引用，不要重新发明 key 名）：
  `P5_bdd1_readme_en` / `P5_bdd2_readme_zh` / `P5_bdd3_unreleased_section` /
  `P5_bdd3_tag0025_entry` / `P5_bdd4to8_new_url_present` / `P5_bdd9_atomic_commit` /
  `P5_bdd10_residual_scan` / `P5_bdd12_301_status` / `P5_bdd12_301_location` /
  `P5_bdd13_ls_remote` / `P5_bdd14_search` / `P5_bdd15_remote_main` /
  `P5_bdd15_remote_worktree` / `P5_bdd16_fetch_main` / `P5_bdd16_fetch_worktree`
  （BDD-11 无对应 key，见 P2-design.md 说明：会话时序人工确认，不是可复跑的文件/系统状态判定）
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
