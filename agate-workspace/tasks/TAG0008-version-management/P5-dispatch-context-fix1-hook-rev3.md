> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。

---
phase: P5
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0008
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
失败 1（`test_csg_1_readme_triggers_warning`）第三轮修复。**前两轮修复均被 CI 证伪**：shebang 改 /bin/bash（3500192）无效；bash 包装 git（605a0cc/436bbe6）也无效。**停止静态猜测——本轮做 CI 实证诊断**，拿到 Windows 真机证据后确定根因再修。

### 约束
1. **已证伪的假设（不要再走）**：
   - shebang `/usr/bin/env bash` → `/bin/bash`：CI 证伪（3500192 后仍失败）
   - PATH 假设（bash 包装 git）：CI 证伪（605a0cc/436bbe6 后仍失败，output 仅 `[master f67bede] update readme`）
2. **当前事实链**：
   - unit `test_cmsg_1`（bash 直调薄壳，windows_smoke 通过）→ 薄壳链 Windows 可用
   - test_bdd_19（bash 包装 git + pre-commit hook）Windows 通过，但**只断言 returncode 0，不验证 hook 输出**——它可能也在"hook 静默跳过"下假通过
   - test_csg_1（bash 包装 git + commit-msg hook）Windows 失败，output 无 hook 任何输出
   - **git 源码**：`find_hook` 用 `access(path, X_OK)`（Windows mingw_access 剥 X_OK 仅判存在）；hook 经 `run_hooks` → `start_command` → `mingw_spawnvpe` → `parse_interpreter`（读 shebang）→ `path_lookup(interp)` → spawn。spawn 失败 git 通常 warning 到 stderr 但不中止 commit——**但 CI 连 warning 都没有**，说明 hook 未被 git 尝试执行，或输出被吞。
3. **本轮策略（CI 实证诊断）**：
   - 在 test_csg_1 里加**临时诊断打印**（用 `pytest` 的 `print` + `-s`，或直接 assert 前 print）：
     a. `shutil.which("bash")`、`os.environ.get("PATH")`（确认 bash 是否在 PATH）
     b. hook 文件是否存在 + `os.access(hook, os.X_OK)`（确认 git 的 find_hook 判定）
     c. `git version` + `git -C repo config core.hooksPath`（确认 hook 路径配置）
     d. **手动执行 hook**：`run_cli(bash, str(hook), str(commit_msg_file), env={AGATE_ROOT:...})` 看输出（确认薄壳链在测试 repo 环境可用）
     e. git commit 的完整 stderr（`result.stderr` vs `result.output` 分离）
   - push 分支 → CI 看 Windows 打印 → **基于证据确定根因**
   - 拿到证据后，若根因明确 → 直接修复；若证据指向"git 在 Windows 无法执行 .sh hook"（git-for-windows 限制），修复方向可能是**测试改用 bash 显式调用薄壳验证 self-gate 逻辑**（unit 已有 test_cmsg_1 做这个）——**但 test_csg_1 的本意是验证"git 触发 hook"**，若 git 机制在 Windows 不可行，需与主 Agent 确认测试意图调整（如该用例仅 Linux 跑，Windows 冒烟用 unit 覆盖）
4. **诊断后决策**：
   - 若证据显示 hook 能执行但输出被吞 → 修输出捕获（如 git 的 `stdout_to_stderr` 行为）
   - 若证据显示 hook 未执行（find_hook 失败 / spawn 失败）→ 修 hook 可执行性（Windows chmod 语义 / 用 .exe 包装）
   - 若证据显示 git-for-windows 根本不能跑 .sh hook → 与主 Agent 确认测试意图（Windows 冒烟降级为 unit 覆盖 or 用例仅 Linux）
5. **修复纪律**：Linux 全量必须保持全绿（基线 823 passed）；平台无关原则；测试意图（验证 self-gate 触发）不破坏。
6. **验证**：本地 integration 全绿 + 全量无回归 + shellcheck 0 error；**push → CI 重跑**（最终裁判）。
7. **边界**：只修失败 1；诊断补丁是临时的，确认根因后清理或保留（若保留需注释说明）。
8. **双工作区纪律**：worktree 内改代码；`~/.agate` / 主 checkout 禁止改动。

### 上游关联
- 前两轮修复：3500192（shebang）、605a0cc/436bbe6（bash 包装）——均被 CI 证伪
- 当前 HEAD：436bbe6（bash 包装版 _commit）
- git 源码证据：hook.c find_hook（access X_OK）+ run-command.c start_command + mingw.c parse_interpreter/path_lookup（见 dispatch-context 已确认事实）

### 输入文件
- /home/kity/oclab/agate/.worktrees/agate-TAG0008/agate/tests/integration/test_commit_msg_self_gate_integration.py（诊断改造对象）
- /home/kity/oclab/agate/.worktrees/agate-TAG0008/agate/tests/unit/test_commit_msg_self_gate.py（unit 对照，test_cmsg_1）
- /home/kity/oclab/agate/.worktrees/agate-TAG0008/agate/tests/integration/test_pre_commit_hook.py（test_bdd_19 对照）
- /home/kity/oclab/agate/.worktrees/agate-TAG0008/agate/scripts/commit-msg-self-gate.sh / commit-msg-self-gate.py / resolve-entry.py
- /home/kity/oclab/agate/.worktrees/agate-TAG0008/FIX-WINDOWS-TAG0008.md
- /home/kity/oclab/agate/.worktrees/agate-TAG0008/agate-workspace/tasks/TAG0008-version-management/P5-progress.md（前几轮诊断）
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
4. git add {AGATE_WORKSPACE}/tasks/{Txxx}/（含 .state.yaml + P5 产出，若 .gitignore 忽略需 git add -f）
   ⚠️ 此时 .state.yaml 的 phase 保持 P5，不要提前写 P6——phase = 本 commit 的产出阶段
5. git commit -m "wf({Txxx}-P5): {摘要}"（phase=P5，P5 产出含 P5-test-results/fail-list.txt）
6. P5 commit 完成后进入 P6：**phase 推进 P6 随 P6 产出 commit 一起**（P6-acceptance.md + P6-evidence/ 就绪后），不是单独 phase commit
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
- 环境状态：worktree 分支 feat/TAG0008-version-management；HEAD=436bbe6（bash 包装版）；两轮修复 CI 证伪
- 关键路径：worktree=/home/kity/oclab/agate/.worktrees/agate-TAG0008
- 查证结果：CI 证据——output 仅 `[master f67bede] update readme` 无 hook 输出；test_bdd_19 假通过（只断言 rc）；git 源码 find_hook=access(X_OK)
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
