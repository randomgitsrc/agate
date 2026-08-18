> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心输入源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。

---
phase: P3
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0012
role: test-designer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

产出 P3-test-cases.md + 测试代码，把 P1 的 23 条 BDD（BDD-1~22 + BDD-15b）转成一个新建的
grep 断言审计测试文件 `agate/tests/unit/test_protocol_mechanism_anchors.py`
（P2-design.md `gate_commands.P3` 已固化命令：
`python3 -m pytest agate/tests/unit/test_protocol_mechanism_anchors.py -v`）。
**此时协议文件尚未被本任务改动**，全部断言当前必须失败（红灯）——这是本任务的 TDD 证据。

### 约束

1. **本任务的 BDD 性质特殊**：不是常规业务功能断言，而是"协议文档/角色文件是否含特定新增小节/
   关键词"的存在性断言。P2-design.md §2.1 改动落点表最后一列「关键词锚点」已经给出了绝大多数
   BDD 对应的确切关键词字符串，**必须逐字复用这些关键词**（不得意译/改写），因为这些是 P4
   implementer 落地协议文档改动时也必须逐字使用的同一批词（P2-design.md §3.5 已明确"不得意译
   替换"）。
2. **测试结构**：参照 `agate/tests/unit/test_check_protocol_consistency.py` 的组织范式（P2-design.md
   §3.6 已指定），但本测试更简单——不需要 importlib 加载脚本模块，只需要**直接读文件文本 + 关键词
   `in` 判断**。建议结构：
   ```python
   ANCHOR_TABLE = [
       ("agate/phase-cards/P0-orchestrator.md", "同类/影响面预判"),
       ("agate/phase-cards/P0-orchestrator.md", "[P0_STALE]"),
       # ... 逐条 BDD 对应的 (文件路径, 关键词) 二元组，见 P2-design.md §2.1 表
   ]

   @pytest.mark.parametrize("file_path,keyword", ANCHOR_TABLE, ids=[...])
   def test_anchor_present(file_path, keyword):
       text = (REPO_ROOT / file_path).read_text(encoding="utf-8")
       assert keyword in text, f"{file_path} 缺少关键词锚点：{keyword}"
   ```
   仓库根路径用相对 worktree 根定位（不要硬编码绝对路径），保持平台无关（纯文本 `in` 判断，
   不依赖 shell/grep 二进制，覆盖 Windows CI matrix）。
3. **1:1 映射到 BDD 编号**：每个 parametrize 用例的 test id 或注释需能追溯到对应 BDD 编号
   （如 `id="BDD-1"`），P1/P2 已把 BDD 与关键词一一对应，测试设计不需要重新发明映射，只需要
   把 P2-design.md §2.1 表转成可执行断言。BDD-15b/19/20 是"引用式"落地（不重复展开完整规则，
   只引用权威定义），断言其"引用词"而非完整规则文本，具体引用词见 P2-design.md §2.1 表对应行。
4. **BDD-22 自身**：以"本测试文件存在 + 全部用例可运行（此刻全红）"为验收标准，不需要额外的
   关键词断言（P2-design.md §3.6 已明确）。
5. **不要求 UI/Playwright 用例**：`ui_affected: false`（P2 已声明），本任务无 UI。
6. **红灯验证**：写完后自行跑一次
   `cd /home/kity/oclab/agate/.worktrees/agate-TAG0012 && python3 -m pytest agate/tests/unit/test_protocol_mechanism_anchors.py -v`
   确认全部用例目前失败（AssertionError，不是 ImportError/SyntaxError——后者是"假红灯"，
   需要先修好测试代码本身）。这是 P3 gate 的核心判据（check-tdd-red.py 会独立复核）。
7. **`test_code_dir` 声明**：P3-test-cases.md frontmatter 或正文需声明
   `test_code_dir: agate/tests/unit/`（沿用既有测试目录，不新建独立子目录——本任务只新增
   1 个测试文件，不需要专属目录）。

### 上游关联

- P1-requirements.md（approved，23 条 BDD）+ P2-design.md（approved，`gate_commands.P3` 已固化，
  §2.1 改动落点表含全部关键词锚点，§3.6 已给出测试设计范式）。
- P2-review.md 非阻塞发现 2 点（verification_env 现状范围描述/批次表遗漏 L521 子句）均不影响本
  阶段测试设计，无需处理。

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0012-protocol-mechanism-fixes/P1-requirements.md（23 条 BDD，测试的主要来源）
- {AGATE_WORKSPACE}/tasks/TAG0012-protocol-mechanism-fixes/P2-design.md（§2.1 改动落点表 = 关键词锚点权威来源；§3.6 测试设计范式；§6 gate_commands.P3 固化命令）
- {AGATE_WORKSPACE}/tasks/TAG0012-protocol-mechanism-fixes/P0-brief.md
- agate/tests/unit/test_check_protocol_consistency.py（组织范式参照，不是断言内容参照）
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
- 环境状态：worktree 基线已验证（881 pytest 全绿），协议文件尚未被本任务改动（P4 才会改），所以
  本测试当前全红是预期且正确的状态。
- `gate_commands.P3` 固化为：`python3 -m pytest agate/tests/unit/test_protocol_mechanism_anchors.py -v`
  （P2-design.md §6，verbose 输出，check-tdd-red.py 会读取该命令）。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
