---
phase: P3
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0006
role: test-designer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
产出 P3-test-cases.md（测试用例清单 + test_code_dir 声明）+ 测试代码：为 agate UI/UX 验收机制的 gate 脚本行为（BDD-3/4/9/14）与协议文档条文（BDD-1/2/6/11/12/13）写 pytest 单测，实现前先红（TDD 红灯语义，P4 实现脚本后转绿）。

### 约束
1. **本任务是 agate 协议本体增强**（dogfooding）：测试对象是 gate 脚本（check-gate.py / check-p6-evidence.py / check-p6-provenance.py / 等）与协议文档（analyst.md / architect.md / verifier.md / plan-design-review.md / dispatch-prompt.md / P1/P2/P6 卡片）。测试代码写在 worktree 的 `agate/tests/` 下（改造对象），改的就是仓库测试文件。
2. **测试代码落点**（在 worktree 既有测试文件内增量追加，不新建独立测试模块——保持 pytest 集合一致）：
   - BDD-3（P1 gate vision 三态检查）：`agate/tests/unit/test_check_gate.py` 追加 4 用例（fixture 构造缺失/非法 status/GAP 合法/backend 兼容）
   - BDD-4（P2 gate UI 设计节检查）：`agate/tests/unit/test_check_gate.py` 追加 4 用例（缺节/完整/缺关键词/非 UI 不触发）
   - BDD-9/10/13（P6 双证据分档/真实分析/输入态复核）：`agate/tests/unit/test_check_p6_evidence.py` + `test_check_p6_provenance.py` 追加（vision=GAP 走复核记录、available 无 vision YAML exit 1、无声明默认 available 语义 test_vision_none_1、文档条文 test_vision_docs_*）
   - BDD-14（雷同截图降级）：`agate/tests/unit/test_check_p6_evidence.py` 追加 3 用例（有复核记录放行/无复核记录 exit 1/不重复不受影响）——注意构造前置门禁：测试 PNG 须 >1KB + 像素方差≥50（PIL 生成非纯色图），Pillow 缺失 `pytest.importorskip("PIL")` 包裹
   - BDD-1/2/6/11/12/13（协议文档条文）：新增 `agate/tests/unit/test_review_role_docs.py`（或并入既有文档检查测试）—读 analyst.md/plan-design-review.md/verifier.md/P6 卡片/dispatch-prompt.md 断言含要求锚点词
3. **P3 红灯语义**：所有测试用例在 P4 实现前必须**失败**（红灯）——因为 gate 脚本尚未新增对应检查逻辑、文档尚未新增条文。红灯类型应为 B 类（断言失败/引用未实现函数），非 A 类（测试代码自身语法错误）。
4. **平台无关原则（AGENTS.md 测试约定，强制）**：不硬编码 Unix 路径（用 pytest tmp_path fixture）、不假设 /tmp；Pillow 缺失时 ahash 相关测试 skip；不裸 `python3`（探测 `python3|python`）。
5. **BDD→测试 1:1 映射**：每条 `#### BDD-NN` 对应 ≥1 个测试用例，测试名引用 BDD 编号（如 `test_vision_1_...` / `test_ui_design_1_...`）。
6. **测试可运行性**：写完测试后自跑确认"测试文件可收集、红灯原因是被测功能未实现"（import 失败/断言失败），不是测试代码 bug（T075 教训：手写魔数断言与 fixture 数据矛盾）。
7. **不做实现**：只写测试，不改 gate 脚本/协议文档实现（P4 implementer 的活）。
8. **产出结构**：P3-test-cases.md（测试用例清单：编号、对应 BDD、预期、当前状态红灯）+ 测试代码（在 agate/tests/ 内）。`test_code_dir` 声明为 `agate/tests/`（或具体子目录）。
9. **本任务特殊性**：P6 验收以"脚本单测 + 文档内容"为证据，不依赖真实截图/视觉分析——测试设计覆盖的是脚本行为断言与文档条文存在性断言。

### 上游关联
- P2-design.md 已 approved：方案 A（三态硬声明 + P2 UI 设计节门禁 + P6 三态分档消费 + GAP 降级链）。§2.1-2.14 每条 BDD 已定义 gate 逻辑 + 单测规格（函数名/断言/兼容）。
- 关键设计决策：P1 无视觉能力声明 → 默认 available 语义（R1b 强制保留）；GAP 分支仅在显式声明 status: GAP 时触发。
- gate_commands（P2 固化）：P3 = `python3 -m pytest -q --collect-only agate/tests/`。
- 基线：现有 825 pytest 用例全绿（回归底线）；本任务新增用例只增不减。

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0006-ui-ux-quality/P2-design.md（方案设计——主输入，§2.1-2.14 已定义每 BDD 的测试规格）
- {AGATE_WORKSPACE}/tasks/TAG0006-ui-ux-quality/P1-requirements.md（BDD 验收条件——测试来源）
- {AGATE_WORKSPACE}/tasks/TAG0006-ui-ux-quality/P0-brief.md（任务简报）
- {project_root}/agate/assets/execution-roles/test-designer.md（你的角色定义）
- {project_root}/agate/tests/conftest.py（fixture helpers：create_task_dir / add_frontmatter_field / task_dir 等）
- {project_root}/agate/tests/unit/test_check_gate.py、test_check_p6_evidence.py（既有测试模式参考）
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
- 测试对象现状：
  - check-gate.py 现有 gate_p1（BDD 锚点 + NEED_CONFIRM 检查）与 gate_p2（四字段检查）——本任务新增 `_gate_p1_vision_capability` + `_gate_p2_ui_design_section`（P4 实现）
  - check-p6-evidence.py 现有 avg-hash WARNING（P4 改为降级待复核判定）
  - check-p6-provenance.py 现有 R1b vision YAML 审计（P4 加 GAP 放宽）
  - fixtures：full-task/high-risk/paused-task/ui-affected/vision-blocked 5 个静态夹具（P2 gate 测试用自建 fixture，不引用它们）
- 测试环境：worktree 内 pytest 可跑（`python3 -m pytest agate/tests/` 收集 825 用例）；PIL 已装（agate-image-check.py 依赖）但测试仍须 `importorskip("PIL")` 保持平台无关
- 基线：825 pytest 全绿 + consistency 0 ERROR
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。