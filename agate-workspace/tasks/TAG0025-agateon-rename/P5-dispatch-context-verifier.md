---
phase: P5
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0025
role: verifier
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
执行 P2-design.md 固化的全部 `gate_commands.P5_*` 系列命令（共 24 条独立 key，覆盖回归底线 +
16 条 BDD 的程序化验证），产出 `P5-test-results/unit.md` + `fail-list.txt`（+ 如有其他产出）。
**GitHub 仓库改名与 remote 迁移已在 P4 阶段完成**（4 条验收锚已由主 Agent 实测通过），所以本次
BDD-12~16 相关的 key 现在应该都能真正跑出有意义的结果（不再是 P3/P4 阶段"当前根本不适用"的
状态）。

### 约束

1. **逐条独立执行，不要用 `&&` 拼接**：P2-design.md 的 gate_commands 已按"每条 key 独立、不用
   `&&` 拼接"原则声明，你逐条跑、逐条记录 exit code 与输出摘要，不要图省事拼接执行。
2. **已知问题——`P5_bdd10_residual_scan` 对 P3 新增测试文件有盲区，你需要按下面的方式处理**：
   该 shell key 的排除正则未覆盖 `agate/tests/regression/test_repo_url_no_stale_rename.py`
   自身（该文件文档字符串里出于说明目的引用了字面 `randomgitsrc/agate`）。跑这条 key 时如果
   失败，**先检查失败输出是否精确等于该测试文件自身的命中**（不多不少）：
   - 若失败输出**只**包含该测试文件的行，判定为"已知盲区，非真实残留"，不算 gate 失败，在
     `unit.md` 里明确记录"P5_bdd10_residual_scan（shell 版）命中已知盲区（P3 测试文件自身文档
     字符串），非真实残留；以 pytest 版本
     `test_bdd_10_repo_wide_residual_scan_zero_after_exemptions` 为 BDD-10 权威判定"，并单独
     执行 `python3 -m pytest agate/tests/regression/test_repo_url_no_stale_rename.py::test_bdd_10_repo_wide_residual_scan_zero_after_exemptions -v`
     确认该权威判定通过（应为 PASSED）
   - 若失败输出**除了**该测试文件还命中其他文件/行，那是真实残留，按正常 gate 失败流程处理
     （不要把真实残留也归为"已知盲区"）
   - 这条处理规则不是让你"跳过检查"，是让你正确区分"已知的、已核实的假阳性"与"新的、真实的
     问题"——两者的处理方式必须不同，混淆二者是本条约束要防止的错误。
3. **全量回归必须真正跑**：`P5_unit`（`agate/tests/unit/`）与 `P5_other`
   （`agate/tests/` 排除 `unit/`）都要跑，不要只跑本任务新增的 `regression/` 子集就当作全量。
   `P5_count_tests` 预期输出为 **1294**（P2-design.md 已声明：1293 基线 + 1 条新增回归测试文件，
   注意是"+1 个文件"不是"+1 条 test function"——`test_repo_url_no_stale_rename.py` 内有 11 个
   测试函数，`count-tests.sh` 的计数口径以你实跑输出为准，若与 1294 不符，如实记录实际数字 +
   差异原因，不要为了凑数字而误报）。
4. **shellcheck 范围**：`P5_shellcheck` 覆盖 `agate/scripts/*.sh` 与 `install.sh`——本任务
   P4 批次 1 改过 `install.sh`，这是需要重点关注 shellcheck 是否新增警告的文件。
5. **BDD-14（GitHub 搜索）已知有索引延迟可能性**：P2-design.md 与 P3-test-cases.md 均已声明
   "若因索引延迟失败，按索引延迟复跑，不直接判定失败"——主 Agent 此前已实测确认命中（改名当天
   即命中，见 env-rename-handoff.md §六），大概率你这次跑也会命中；若意外失败，先复跑 1-2 次
   确认是否为延迟，而非立即判失败。
6. **不要执行任何写操作**：`gh api -X PATCH`（改名）已完成，不要重复执行；`git remote set-url`
   已完成，不要重复执行；本阶段是纯验证，不产生任何仓库状态改动。
7. **测试环境隔离**：本任务不涉及生产数据库/生产 API，`[PROD_NOT_TOUCHED]` 直接适用，不需要
   额外的环境准备（P0-brief `env_constraints` 已声明标准测试命令，无需起 debug server）。

### 上游关联

- P2-design.md 的完整 `gate_commands` 块（24 个 P5_* key）是本次执行的权威清单，逐条执行，
  不要漏项也不要自己发明新 key
- P4-implementation.md「批次 2：remote 迁移」节记录了改名与 remote 迁移的完成状态，可作为
  BDD-12~16 相关 key 预期通过的背景依据（但仍要实跑验证，不能因为"应该通过"就假设通过）
- P3-test-cases.md「B 类」节记录了 BDD-11~16 各自对应的 gate_commands key，交叉核对用

### 输入文件（按顺序读）

1. `agate-workspace/tasks/TAG0025-agateon-rename/P2-design.md`（gate_commands 全文）
2. `agate-workspace/tasks/TAG0025-agateon-rename/P4-implementation.md`（批次 1 + 批次 2 全文）
3. `agate-workspace/tasks/TAG0025-agateon-rename/P3-test-cases.md`
4. `agate-workspace/tasks/TAG0025-agateon-rename/P0-brief.md`

### 产出文件字段
产出目录：`agate-workspace/tasks/TAG0025-agateon-rename/P5-test-results/`，含 `unit.md`（标注
failed 数量 + 24 条 gate_commands.P5_* 逐条结果）+ `fail-list.txt`（failed 测试 id 逐行列出，
无失败可为空文件）。用 `FILE={AGATE_WORKSPACE}/tasks/TAG0025-agateon-rename/P5-test-results/unit.md
agate-md-field-set --list` 查看应填字段。
</dispatch_guide>

<!-- AGATE_CARD_START -->
## 当前阶段卡片：P5

路径：phase-cards/P5-verification.md
---
# P5 — 技术验证

> 当前状态：[首次 / 重试 #N / 裁剪跳阶]
> P5 不可裁剪（核心阶段）
> ⑨ P5 subagent 化

## 如果是首次进入本阶段

1. 主 Agent 派发 verifier subagent（P5 模式）执行 gate_commands.P5
   1.1 写 P5-dispatch-context-verifier.md（派发指引：目标/约束/上游关联/输入文件 + 客观查证信息）
2. 逐条判定通过/失败
3. 若失败：判定是真失败还是环境问题 → 真失败回 P4，环境问题修复环境
4. `git rev-parse HEAD` 取当前（父）提交哈希，写入 `.state.yaml` 的 `p5_pass_commit` 字段（TAG0016 BDD-12：供 P6/P8 判定"引用 P5 证据、不重跑"，字段可选、写入时机见 `state-machine.md`「每任务独立状态文件」）
   ⚠️ **P5 commit 不得混入非产出文件改动**（真实反例：`5bdcd90` 混入了 `agate-debt-check.py` 的真实修复）——若发现顺手修复的必要性，应先回 P4 走正常流程，不要混入 P5 commit（R9 缓解措施，P2-design.md §3.2/§1.3）
5. git add {AGATE_WORKSPACE}/tasks/{Txxx}/（含 .state.yaml + P5 产出，若 .gitignore 忽略需 git add -f）
   ⚠️ 此时 .state.yaml 的 phase 保持 P5，不要提前写 P6——phase = 本 commit 的产出阶段
6. git commit -m "wf({Txxx}-P5): {摘要}"（phase=P5，P5 产出含 P5-test-results/fail-list.txt）
7. P5 commit 完成后进入 P6：**phase 推进 P6 随 P6 产出 commit 一起**（P6-acceptance.md + P6-evidence/ 就绪后），不是单独 phase commit
   ⚠️ P5→P6 是唯一硬拦边界：P6 的 self-authored gate 拦截"非证据文件"，
      P5 的 .txt/.json 等合法产出必须在 phase=P5 的 commit 里提交，不能带进 phase=P6
   ⚠️ 不要"先 commit 产出再单独 commit 改 phase"（state-machine.md:431 明确禁止）——
      phase 与产出同 commit，P6 产出就绪时 phase 一并写 P6

## 如果是重试

→ 修复后重跑 gate_commands.P5 **全量**（T027 教训：修复可能引入回归，不能只检查修复项）
→ 读 agate/rules/state-transitions.md 确认 retry 上限（P5 MAX=2）

## 前置条件

- [ ] P4 代码已 commit（暂存区含代码文件）
- [ ] gate_commands.P5 命令在 P2 已声明（这是 gate 会执行的命令清单）

## 执行方式

verifier subagent 从 P2-design.md 读取 gate_commands.P5 并执行：

```bash
# 示例（实际命令取决于 P2 声明）
pytest -q --tb=no                    # 后端单元测试
vitest run --reporter=verbose        # 前端单元测试
playwright test --reporter=line tests/e2e/  # E2E（ui_affected: true 时）
```

紧凑输出模式：用工具的汇总模式（pytest --tb=no / vitest --reporter=dot / go test | tail -30）。只保留通过/失败汇总+失败清单，不逐项 traceback。

**技术栈无关**：gate_commands.P5_formatter 声明 formatter 脚本（可选），将测试输出标准化。见 `assets/formatters/README.md` 速查表。不提供 formatter 时退化为 exit-code-only。

## 判定规则

- **exit 0 + failed=0**：全通过 → 继续
- **exit ≠0 或 failed>0**：主 Agent 判定
  - 真 bug → 回 P4 修复
  - 环境问题（超时/端口占用/依赖缺失）→ 修复环境重新跑
  - flaky test → 记入 P5-test-results/，三振记录
- **PROD_TOUCHED**：任何生产环境触达 → 立即 PAUSED（触发写 `[PROD_TOUCHED] {描述}`，未触发写 `[PROD_NOT_TOUCHED]`）
- **E2E 未执行**（ui_affected: true 但未跑 P5_e2e）：视为验证不完整
- **全量测试**：P5 阶段应运行全量测试套件（含非本任务测试）。发现预存失败时：
  - 在 P5-test-results/unit.md 标注"预存失败：X（与本次改动无关）"
  - 主 Agent 判断：修复成本 < 推迟成本 → 立即修复；否则记录到 known-failures.md
  全量测试不阻断 P5 推进，但未运行全量测试时须在 P5-test-results/unit.md 标注"未运行全量测试"。

## 产出规格

- P5-test-results/unit.md：标注 failed 数量（verifier subagent 产出）
- P5-test-results/fail-list.txt：verifier subagent 产出，failed 测试 id 逐行列出（`FAILED ` 前缀同上，
  pytest 参考实现），可为空文件（无失败时）。使用 gate_commands.P5_formatter 声明的 formatter 提取（与 baseline 捕获一致）。无 formatter 时可省略此文件——P5 gate 检测到缺失时优雅降级为 WARNING-only 行为，不因此新增拦截。
- UI 任务：P5-test-results/e2e.md（Playwright 实跑结果 + 截图路径，verifier subagent 产出）

## 预存失败的处理

若 verifier subagent 发现改动前就存在的失败（预存失败），按以下流程登记：

> **known-failures.md 只登预存失败**（P5 之前就存在的、与当前任务无关的）。当前任务引入的失败用 P5-test-results/ 记录。

1. 在 `{AGATE_WORKSPACE}/tasks/{Txxx}/known-failures.md`（从 `{agate_root}/assets/templates/known-failures-template.md` 拷贝模板）登记：
   - 测试文件、失败数、根因、是否与当前任务相关
2. 在 P5-test-results/unit.md 标注"预存失败：X（与本次改动无关）"
3. 主 Agent 按修复成本判断：修复成本 < 推迟成本 → 立即修复；否则记录推迟
4. 即使不立即修复，债务也可见、可追踪——不会因为"与本任务无关"而默默累积

## gate 规则

check-gate.py P5 → exit 2。主 Agent 验 gate（检查 P5-test-results/ 存在 + failed 计数），CI backstop 兜底。

**external-output-gate vs self-authored-gate**：P5 的 gate 是 external-output-gate——主 Agent 验证的是 verifier subagent 的产出（P5-test-results/），而非自己跑的命令结果。这与 P4（主 Agent 自己写代码、自己跑 lint）的 self-authored-gate 不同。external-output-gate 的信任链依赖 subagent 隔离 + CI backstop 双重保障。

## 推进条件（全部满足才写 phase: P6）

- [ ] gate_commands.P5 全部命令 exit 0 + failed=0
- [ ] UI 任务：gate_commands.P5_e2e 已执行且通过
- [ ] 无 PROD_TOUCHED 标记
- [ ] 测试环境隔离正常（对比测试前后生产库状态）

## 常见错误

1. **不跑 E2E**：UI 任务只跑单元测试和类型检查 → 端到端行为未验证。T046 教训：38 个单元测试全绿 + vue-tsc OK，但浏览器里图片是破的
2. **把测试绿了当作功能正确**：单元测试通过 ≠ 用户看到的功能正常。P5 是代码正确性验证，P6 才是用户视角验收
3. **修复后不重跑全量**：只跑修复的那一个测试 → 修复引入的回归没被发现

## P5 commit→push 窗口残余风险（N5）

**残余风险**：verifier subagent 产出 P5-test-results/ 后，主 Agent commit 并推进到 P6，但 push→CI 之前存在时间窗口。伪造的 P5-test-results 可在此窗口内流向下游。

**缓解**：主 Agent 在推进前**必须**执行签名校验——grep test runner 输出签名：

```bash
grep -cE '^(PASSED|FAILED|passed|failed|ok|not ok)' P5-test-results/unit.md
```

计数 >0 才视为有效产出，计数=0 视为假完成，计为重试。这不是重跑测试（CI backstop 在 push 后兜底全量验证）。

gate 不过 ≠ 你失败了。红灯指向工作/设计的问题，不指向你。正确动作是诊断→退回/重试/PAUSED，不是修改产出让它变绿。

## 按包拆分并行（条件触发，非强制）

> 仅当 P2 packages > 1 且包间无依赖时适用。单包任务跳过本节。
> 并行上限 / 失败批 retry / 共享文件统一后处理见 dispatch-protocol「派发编排机制」并行规则。

当 P2 声明多个 packages 时，P5 可按包拆分并行——各 verifier subagent 跑各包的 gate_commands，各写 P5-test-results/{pkg}/。

拆分判据同 P3。P5 是只读验证，无代码写冲突风险。

**但"无写冲突"不等于可以随便并行**：`gate_commands.P5` 常是全量测试套件（含 xdist 多进程）或 E2E 浏览器命令，属**资源密集型默认串行**——按 dispatch-protocol.md「派发编排机制」并行规则第 4 条处理，即使包间无依赖也默认改为串行；要并行必须先按下方「基础设施隔离」为每批分配独立端口/数据库/临时目录，无法隔离即串行（安全默认值）。判据细节见该节，本卡片不重复展开。

**环境准备职责边界（本阶段落地）**：verifier subagent **默认不自行启动环境**——debug server、测试数据库、临时端口等由主 Agent（或 P0-brief 声明的单一责任方）统一准备好，通过 dispatch-context 注入访问方式；多个并行 verifier 共享同一环境时更是如此，不允许各自启动。环境验证失败时的可重试/不可重试分类、批处理要求与止损轮次，一律按 dispatch-protocol.md「verification_env 失败处理协议」与「环境准备职责边界」执行，本卡片只做落地引用，不重复展开规则。

**基础设施隔离（本阶段特定，并行时强制）**：
- 测试端口：各 verifier 使用独立端口（与 P4 并行时分配的端口一致，或新分配）
- 测试数据库：各 verifier 用独立数据库（与 P4 隔离方案一致），不共享同一 test.db
- 临时输出：各 verifier 写入 `P5-test-results/{pkg}/` 独立目录，不共享同一 unit.md
- E2E 浏览器：Playwright 默认隔离 browser context，但若 E2E 测试启动了本地 server，各 verifier 需用不同端口

主 Agent 在并行派发前**必须**为每个 verifier 的 dispatch-context 分配独立的基础设施参数（同 P4，未分配导致冲突时计为重试）。

## 下游影响

- P6 验收在 P5 通过的基础上做用户视角验证
- P8 发布时需重跑 P5 gate（确认 bump-version 后测试仍全绿）

> 完成 → 读 phase-cards/P6-acceptance.md
<!-- AGATE_CARD_END -->

<objective_info>
- 改名 + remote 迁移均已在 P4 完成并实测（见 env-rename-handoff.md §六）：`randomgitsrc/agate`
  → `randomgitsrc/agateon`，主 checkout + worktree 的 `origin` 均已指向新仓
- P4 批次 1 自查 + P4 review 独立复核：`agate/tests/regression/test_repo_url_no_stale_rename.py`
  11 个测试函数在批次 1 commit 后全部 PASSED（含 BDD-9 批次原子性）
- 当前 HEAD 是 P4 批次 2 的 commit（`18a6b7b`），暂存区为空
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
