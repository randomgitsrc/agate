---
phase: P3
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0030
role: test-designer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

产出 `P3-test-cases.md` + 断言审计测试代码（TDD 红灯）：把 P1 的 BDD-1~21 全部转成
**grep 断言审计用例**（读协议文件文本 + 关键词 `in` 判断——TAG0012/0013 既有模式），
锁定 P2-design §2 各落点的锚词。此时协议文件尚未被本任务改动，全部用例**当前必须失败（红灯）**，
P4 逐条落地后转绿——这是本任务的 TDD 证据。

测试文件路径**已由 P2-design §5 gate_commands.P3 固化**：
`agate/tests/unit/test_tag0030_assertions.py`——**不得另起文件名**（gate 已指向该路径）。

### 约束

1. **锚词逐字复用**（TAG0012 教训）：关键词锚点必须从 P2-design.md §2 改动详述/§0.1 落点表
   「改动一句话」列**逐字复用**（不意译/不改写）——P4 implementer 落地时也用同一批词，
   意译会导致 P4 落地词与 P3 断言词不一致、测试永不转绿。
2. **真红灯语义**（TAG0012 BDD-5 教训）：写每条用例前核实目标关键词当前在目标文件的命中数。
   若某关键词**已存在**于目标文件（如既有条文巧合含词），单关键词断言当前即为真（假绿）——
   必须把该 BDD 改为 AND 语义多关键词（至少一个当前 0 命中）或换唯一锚词，确保**整体断言现在为假**。
   每个「当前已命中」的关键词都要在 P3-test-cases.md 里注明，供 P4 判定。
3. **BDD-1~21 全覆盖 1:1**：每条 BDD 至少一个用例，测试名引用 BDD 编号（`test_bdd_N_...`）；
   BDD 编号连续不跳。允许一条 BDD 拆多条子用例（id 加锚点后缀），仍追溯同一 BDD。
4. **平台无关**（测试约定硬约束）：不裸 `python3`（用 `sys.executable`/`Path`）、不用 `/tmp`
   （用 pytest `tmp_path`）、不假设 POSIX symlink、不用 shell grep（纯 `read_text` + `in`）。
   参照 `agate/tests/unit/test_protocol_mechanism_anchors.py`（ANCHOR_CASES 表驱动）与
   `test_review_role_docs.py`（`_read(agate_root, *parts)` + 逐条 assert）——选其一模式即可，
   一致性优先。windows_smoke 标记按既有约定。
5. **路径基座**（P2-review G2）：目标文件路径相对 worktree 根（agate_root 的父目录）。
   `agate_root` fixture 已由 conftest 提供（上溯解析）；worktree 根 AGENTS.md 用
   `agate_root.parent / "AGENTS.md"`（仓库根，不在 agate/ 内）。
6. **AGENTS.md 根路径**（BDD-20 载体）：`AGENTS.md` 在 worktree 根（`agate_root.parent`），
   断言其「改脚本的工作流」节含「新增 CHECK 上线前先全量扫描」表述时路径基座写对。
7. **不回改协议文件**：P3 只写测试代码与 P3-test-cases.md，**不碰** agate/phase-cards、
   assets/、templates/、tests/README.md、AGENTS.md——那些是 P4 的事。协议文件改动的"预期
   状态"只体现在断言里。
8. **P3-test-cases.md 声明 test_code_dir**：指向测试文件所在目录
   （`agate/tests/unit/`，即 `agate/tests/unit/test_tag0030_assertions.py`）。
9. **不写实现**：P3 产出不含任何对协议文件的修改（那是 P4）；测试当前红灯是预期，不是失败。
10. **无行首预判格式**：P3-test-cases.md 正文禁止行首 `- PASS` / `- FAIL`（provenance 审计拦截）。
11. **命令超时**：跑测试验证红灯时用 `timeout 180s python3 -m pytest agate/tests/unit/test_tag0030_assertions.py -q --tb=short`（P2 固化 P3 命令），预期全部失败（assertion 类，B 类红灯）。

### 上游关联

- P1-requirements.md（BDD-1~21 + §7 同类扫描 + §8 反模式自检）
- P2-design.md（§2 四 phase 改动详述 = 锚词清单来源；§0.1 Modify 表；§5 gate_commands 固化
  P3 命令与文件名；§6 files_to_read）
- P2-review.md（非阻塞 N1/N3/N5 + 测试缺口 G1/G2——G2 见约束 5/6；N1 见输入文件 4/5）
- 既有模式源：test_protocol_mechanism_anchors.py（TAG0012）/ test_review_role_docs.py（TAG0006）

### 输入文件（按顺序读）

1. `agate-workspace/tasks/TAG0030-acceptance-blindspot/P1-requirements.md`（BDD-1~21）
2. `agate-workspace/tasks/TAG0030-acceptance-blindspot/P2-design.md`（锚词清单 + gate_commands + files_to_read）
3. `agate-workspace/tasks/TAG0030-acceptance-blindspot/P0-brief.md`
4. `agate/tests/unit/test_protocol_mechanism_anchors.py`（ANCHOR_CASES 表驱动模式源，P2-review N1 点名）
5. `agate/tests/unit/test_review_role_docs.py`（逐条 assert 模式源，含 CHECK11 三锚词双保险测试）
6. `agate/assets/execution-roles/test-designer.md`（角色定义）
7. `AGENTS.md`（worktree 根：测试约定 + DEBT0025 载体「改脚本的工作流」节——BDD-20 断言对象）

### 产出文件字段

用 `FILE={AGATE_WORKSPACE}/tasks/TAG0030-acceptance-blindspot/P3-test-cases.md agate-md-field-set --list`
查看本阶段应填字段；逐个写入；失败照提示修正，不要手写 frontmatter。

frontmatter 必填：phase=P3, task_id=TAG0030, type=test-design, parent=P2-design.md,
trace_id=TAG0030-P3-20260904, status=draft, created=2026-09-04, agent=test-designer,
test_code_dir（声明测试代码目录）。
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
### A. 路径拓扑
- worktree 根 = `/home/kity/oclab/agateon/.worktrees/agate-TAG0030`
- 任务目录 = `agate-workspace/tasks/TAG0030-acceptance-blindspot/`
- 测试文件 = `agate/tests/unit/test_tag0030_assertions.py`（P2 §5 固化，不得另起名）
- 改造对象 = worktree 的 `agate/`（P4 才动）；P3 只写测试 + test-cases 文档

### B. BDD 分组与落点速查（锚词详单见 P2-design §2，逐字复用）
- Phase1 BDD-1~6：P3 卡 step0 补「创建型测试清理钩子」（创建即注册/无条件删除/200/204/404）；
  P4 卡 step0 镜像；P6 卡 post-test 残留检查；dispatch-context 模板条目位；
  BDD-6 断言审计单测本身（本测试文件）
- Phase2 BDD-7~9：P1 卡「人工体验路径验收」节（Given seed → 页面有内容）；
  analyst.md 同源一句
- Phase3 BDD-10~15：plan-design-review.md 形态分派头（ui_render_shape → 维度组）；
  布局型三组/渲染组件型渲染正确性+动效时序；≥2 布局候选+权衡；CHECK11 三锚词保持；
  0-10/status 保持；缺省回落布局型
- Phase4 BDD-16~21：architect.md 视觉契约「可表达子集」（五类 DOM 度量，不收主观视觉）；
  verifier.md DOM 度量证据表述；tests/README「真实 gate 语义」；AGENTS.md「新增 CHECK 上线前
  全量扫描」；dispatch-context 模板「拆小/体量」默认指导

### C. 既有模式源要点（约束 4 参照）
- ANCHOR_CASES 表驱动：(test_id, file_path, keywords) 元组列表 + 循环参数化
- 逐条 assert：`_read(agate_root, *parts)` + `assert "关键词" in content`
- 平台无关：Path.read_text + `in`，无 shell grep；windows_smoke 标记
- agate_root fixture 来自 conftest（上溯解析），仓库根 = agate_root.parent

### D. P3 gate / check-tdd-red
- check-gate P3：P3-test-cases.md 存在（含 test_code_dir）+ 测试代码目录存在
- check-tdd-red exit 0 = 真红灯（assertion 失败 / 项目内 import 失败 = B 类）——本任务测试
  import pytest 失败属第三方（A 类）风险，确保不 import 未装依赖；目标文件读取用 Path 直读，
  不依赖被测模块 import（P2-review G1 边界：grep 锁词存在，不锁逻辑——预期）
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
