---
phase: P3
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0016
role: test-designer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

为 P1-requirements.md 的 19 条 BDD 设计测试，产出 P3-test-cases.md + 测试代码，写入
`agate/tests/unit/`（`test_code_dir: agate/tests/unit`）。本任务不是 `change_type: refactor`
（P1 frontmatter 未声明），走标准 TDD 口径：测试当前必须失败（红灯），因为 CHECK 12/审计 7/
文档去重内容都还未实现。

P2-design.md §6 `gate_commands.P3` 已固化 3 个测试文件：
```
python3 -m pytest agate/tests/unit/test_check_protocol_consistency.py agate/tests/unit/test_check_p6_provenance.py agate/tests/unit/test_protocol_dedup_audit.py -v
```
你的任务是在这 3 个文件里（前两个是新增测试函数追加进现有文件，第三个是全新文件）落地全部 19
条 BDD 的测试设计，不新增额外测试文件（除非确有必要，需说明理由）。

### 约束

1. **`test_check_protocol_consistency.py` 新增 CHECK 12 测试**（对应 P2 §1.1 M15）：
   - 正报：人为制造数值不一致 fixture（如临时 8 张卡片中某张 MAX 值与权威表不符），确认 CHECK 12
     报 ERROR
   - 不误报：对 3.4/3.7 节列出的既有正确"权威源+指针"位置（`dispatch-protocol.md` L972 附近 /
     `state-machine.md` Pre-commit 指针 / `git-integration.md` L162）扫描后应 0 ERROR（对应
     BDD-10、BDD-7）
   - 边界：`rules/state-transitions.md` 迁移为纯指针后不再被误判为"重新声明权威表格"
   - CHECK 12 尚未实现，这些测试当前应该因为"CHECK 12 未注册/AUTHORITATIVE_VALUE_ANCHORS 不存在"
     而红灯（B 类错误：项目内 import/属性不存在，不是测试代码本身语法错误）

2. **`test_check_p6_provenance.py` 新增审计 7 测试**（对应 P2 §1.1 M18/§3.5）：
   - 无改动 → 允许引用 P5 证据（审计 7 返回 `reuse_allowed`）
   - 有改动（模拟 P6→P4 修复后重到 P6 场景）→ 拦截，强制重跑（对应 BDD-13）
   - `p5_pass_commit` 字段缺失（存量任务兼容场景）→ 静默回退强制重跑，不报错
   - 审计 7 函数尚未实现，测试应红灯（B 类：函数不存在）

3. **新建 `test_protocol_dedup_audit.py`**（对应 P2 §6 描述的"批量机械改动断言审计"策略，
   HANDOFF-TAG0016.md 建议的方法论）：
   - 一个参数化测试函数，逐条断言"权威源文件含关键内容 + 非权威源文件只含指针短语，不含完整
     段落/表格"，覆盖 BDD-2（平台适配）/BDD-3（阶段门槛表）/BDD-4（派发 prompt 双源）/
     BDD-5（重试上限表）/BDD-6（8 卡片 MAX 数值，可与 CHECK 12 正报测试共用 fixture 思路，但这
     里是"当前去重前"状态的红灯断言，不是 CHECK 12 本身的单测）
   - **必须同时覆盖 BDD-1/BDD-19**（P2 P2-review.md 第 1 轮评审明确指出的测试缺口）：对 M3/M7/
     M10/M12 四个文件（WORKFLOW.md/dispatch-protocol.md/state-machine.md/platform-notes.md）
     断言"文件头/主标题附近含 `> 职责边界：` 前缀行"，内容与 P2 §0 职责声明表对应条目一致
   - **建议覆盖 BDD-7**：对 3.4/3.7 节已验证的三处正确指针位置断言"保持不变"（这条也可以和
     CHECK 12 的"不误报"测试共用断言逻辑，两处测试目的不同——CHECK 12 测的是"脚本检测不误报"，
     这里测的是"文档内容本身未被去重迁移误伤"，你可以判断是否需要都写或只写一处，写清楚理由）
   - **建议覆盖 BDD-11**：断言 `dispatch-protocol.md` 含「## 全量重跑点审计」小节（M16 落点）且
     含四个重跑点的描述
   - **建议覆盖 BDD-16**：断言 `dispatch-protocol.md`「并行规则」第 4 条判据描述仍包含 xdist
     相关表述（回归防护，防止 M23 CI 改动意外波及这条判据文本）
   - 这个文件覆盖的是"去重后文档内容应该长什么样"的断言，当前（去重前）全部应该红灯

4. **对 BDD-8/14/15/17/18，请判断是否可自动化测试，做不到的要显式声明并说明验证方式**（不是
   偷懒跳过，是像 P1/P2 阶段一样做显式判断并写进 P3-test-cases.md，空白不算做过）：
   - BDD-8（P6 人工抽查"职责定位混乱"段落）：这条 P1 定义为 P6 阶段的人工抽查动作，大概率不适合
     写自动化测试；若你认为可以写一个"抽查范围清单存在性"的轻量断言也可以，但不强制
   - BDD-14（P8 重跑范围精简的表述变化）：可考虑写一个对 `phase-cards/P8-release.md` 内容的
     grep 断言（确认"复用同一份 P5-test-results/"这类精简表述存在），或判断为文档变更不需要
     独立测试，只需 P6 人工核对
   - BDD-15（xdist CI 观测步骤）：建议写一个解析 `.github/workflows/protocol-tests.yml` 的测试，
     断言新增的 xdist 步骤存在、且不影响 job 整体 exit code（可以本地验证 YAML 结构，不需要真的
     在 CI 跑）
   - BDD-17（回归基线不破坏）：这是贯穿全任务的元要求（P5 gate_commands.P5 本身就是校验点），
     不需要为它单独写一条新测试，在 P3-test-cases.md 里注明"由 gate_commands.P5 整体校验，非
     独立 P3 红灯项"即可
   - BDD-18（Windows 兼容仅增量声明）：纯文档表述要求（不得声称已实测 Windows），大概率不适合
     写自动化测试，判断为"P6/P8 人工核对表述"即可，不强制写测试

5. **测试当前必须真红灯（B 类错误）**：跑一遍你写的测试，确认失败原因是"CHECK 12/审计 7 函数
   不存在"或"文档内容尚未包含预期的职责边界声明/指针句"这类"实现未写"导致的失败，不是测试代码
   自身的 SyntaxError 或第三方 import 失败（A 类，假红灯）。

6. **不要在 P3 阶段改动任何 `agate/*.md` 协议文档或 `agate/scripts/*.py` 脚本本体**——那是 P4
   implementer 的工作，P3 只写测试代码（`agate/tests/unit/*.py`）和 P3-test-cases.md。

### 上游关联

P2-design.md 已 approved（第 2 轮）。§6 gate_commands.P3 已固化上述 3 个测试文件的命令行。
§1.1 改动清单（M1-M23）与 §1.3 风险表（含 R9 残余风险）、§3 BDD-12/13 provenance 机制设计、
§2 CHECK 12 设计（含伪代码级的 `AUTHORITATIVE_VALUE_ANCHORS` 结构）是测试设计的直接依据。
P2-review.md 第 1 轮曾指出"测试缺口：BDD-1/BDD-19 未被 test_protocol_dedup_audit.py 覆盖"，
本次 P3 派发已把这个缺口的弥补写入约束 3，不需要你重新发现这个问题。

### 输入文件

- {AGATE_WORKSPACE}/tasks/TAG0016-protocol-hygiene/P1-requirements.md（19 条 BDD 全文）
- {AGATE_WORKSPACE}/tasks/TAG0016-protocol-hygiene/P2-design.md（§0/§1/§2/§3/§6，测试设计的
  技术依据；§2 的 CHECK 12 伪代码、§3.5 的审计 7 伪代码可直接作为测试断言对象的接口参考）
- {AGATE_WORKSPACE}/tasks/TAG0016-protocol-hygiene/P2-review.md（第 1 轮"测试缺口"发现）
- agate/scripts/check-protocol-consistency.py（现有 CHECK 1-11 实现 + 现有测试写法风格，
  新测试要跟现有 CHECK 的测试风格一致）
- agate/tests/unit/test_check_protocol_consistency.py（现有测试文件，追加进这个文件）
- agate/scripts/check-p6-provenance.py（现有六道审计实现）
- agate/tests/unit/test_check_p6_provenance.py（现有测试文件，追加进这个文件）
- .github/workflows/protocol-tests.yml（若写 BDD-15 测试，需要读现有结构）

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
- worktree HEAD：28d088d（P2 commit + phase 补记），工作区干净。
- `agate/tests/unit/test_check_protocol_consistency.py` 和 `agate/tests/unit/test_check_p6_provenance.py`
  均已存在（现有 CHECK 1-11 / 六道审计的测试），本次是追加新测试函数，不是新建文件。
- `agate/tests/unit/test_protocol_dedup_audit.py` 当前不存在，需新建。
</objective_info>
