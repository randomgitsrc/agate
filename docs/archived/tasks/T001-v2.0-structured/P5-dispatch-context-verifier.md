> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。

---
phase: P5
generated_by: agate-inject-card.sh + 主 Agent
task_id: T001
role: verifier
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

执行 P2-design.md §5 声明的全部 `gate_commands.P5*` 命令（4 个：主命令 + consistency + shellcheck + count），产出 `docs/tasks/T001-v2.0-structured/P5-test-results/unit.md` + `fail-list.txt`。

### 约束

1. **执行全部 4 个命令**，一个都不能漏跑（P2-design.md §5 原文）：
   ```
   P5:             bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/ 2>&1 | tail -40
   P5_consistency:  python3 agate/scripts/check-protocol-consistency.py 2>&1 | tail -30
   P5_shellcheck:   shellcheck -S warning agate/scripts/*.sh 2>&1 | tail -30
   P5_count:        bash agate/tests/scripts/count-tests.sh 2>&1 | tail -5
   ```
   工作目录：`/home/kity/oclab/agate/.worktrees/v2.0`（worktree 本体，不是 `~/.agate`）。
2. **这是全量测试**（含本任务未直接触及的既有测试），不要只跑受影响的子集——T060 教训：只跑子集可能掩盖预存失败。
3. **产出 `P5-test-results/unit.md`**：必须包含可被 N5 签名校验识别的格式——文件里要能匹配到 `grep -cE '^(PASSED|FAILED|passed|failed|ok|not ok)'` 且计数 >0（bats 的 `ok N ...`/`not ok N ...` 输出格式天然满足这个要求，把 bats 主命令的完整输出原样保留在这个文件里即可，不要只写"通过"两个字這种摘要）。同时写清楚 4 个命令各自的结果（pass/fail 数、exit code）。
4. **产出 `P5-test-results/fail-list.txt`**：failed 测试 id 逐行列出，无失败时可为空文件。
5. **预期结果**（不是让你直接抄这个当结论——自己实跑，如果实跑结果和这个不一致，如实报告不一致）：
   - bats 全量应为 600/600（594 + sanity 6），0 个 `not ok`
   - `check-protocol-consistency.py` 应为 0 ERROR（CHECK 1-9 全 PASS）
   - `shellcheck -S warning` 应无输出（0 警告）
   - `count-tests.sh` 应输出 594
6. **PROD_TOUCHED 检查**：本任务全程只改 agate 协议本体的脚本/文档/测试，不涉及任何生产环境/生产数据库/生产 API，本次验证也不会触达生产环境——正文如实声明 `[PROD_NOT_TOUCHED]`。
7. **非 UI 任务**：P2 声明 `ui_affected: false`，不需要产出 `e2e.md`。
8. **不要修改任何代码/测试文件**——你是纯只读验证角色，只跑命令、记录结果、写报告。发现真失败（非环境问题）不要自己去修，如实记录，由主 Agent 判断退回 P4 还是记录已知失败。
9. **发现预存失败时**：本任务从 P3 起测试基线一直是 594（sanity 另计 6），本任务的历次独立验证（P4 各流commit记录）显示全程无预存失败。如果你这次全量实跑发现有失败，无论是否"看起来与本任务无关"，都如实完整记录在 `unit.md`，不要自行判断为"预存失败"而略过不报——是否预存/是否需要 known-failures.md 登记由主 Agent 判断。

### 上游关联

- `docs/tasks/T001-v2.0-structured/P2-design.md` §5（gate_commands 声明，本次执行依据）。
- `docs/tasks/T001-v2.0-structured/P4-implementation.md`（P4 完整实现记录，含所有流的自查数据——本次是独立验证，不是抄那些数字，是自己重新跑一遍）。

### 输入文件（自己读）

- `agate/assets/execution-roles/verifier.md`（你的角色定义，先读这个）
- `docs/tasks/T001-v2.0-structured/P2-design.md` §5（gate_commands 精确命令）
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
4. 更新 .state.yaml phase=P5 → P6
5. git add docs/tasks/{Txxx}/（含 .state.yaml + 产出文件，若 .gitignore 忽略需 git add -f）
6. git commit -m "wf({Txxx}-P5): {摘要}"

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

1. 在 `docs/tasks/{Txxx}/known-failures.md`（从 `{agate_root}/assets/templates/known-failures-template.md` 拷贝模板）登记：
   - 测试文件、失败数、根因、是否与当前任务相关
2. 在 P5-test-results/unit.md 标注"预存失败：X（与本次改动无关）"
3. 主 Agent 按修复成本判断：修复成本 < 推迟成本 → 立即修复；否则记录推迟
4. 即使不立即修复，债务也可见、可追踪——不会因为"与本任务无关"而默默累积

## gate 规则

check-gate.sh P5 → exit 2。主 Agent 验 gate（检查 P5-test-results/ 存在 + failed 计数），CI backstop 兜底。

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

当 P2 声明多个 packages 时，P5 可按包拆分并行——各 verifier subagent 跑各包的 gate_commands，各写 P5-test-results/{pkg}/。

拆分判据同 P3。P5 是只读验证，无代码写冲突风险。

**基础设施隔离（并行时强制）**：
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
- 环境状态：worktree `feat/v2.0`，`.state.yaml` phase=P5 status=active。P4 已 commit（9 个 commit，最后一个 098cb06）。
- P4 阶段主 Agent 多次独立验证均为 600/600、594 基线、0 一致性错误、shellcheck 干净——本次 P5 是协议要求的正式验证阶段产出（P5-test-results/ 此前不存在），不是重复劳动，是走完整流程的必要步骤。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
