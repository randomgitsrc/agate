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
修复 PR #148 的 Windows 冒烟 2 失败（pytest windows-latest 2 failed），使 merge 解锁。交接单：`FIX-WINDOWS-TAG0008.md`（worktree 根，已 commit a3e0e31）。

### 约束
1. **两个失败（都必须修）**：
   - **失败 1** `test_csg_1_readme_triggers_warning`（integration/test_commit_msg_self_gate_integration.py:46）——TAG0013 引入的 README/AGENTS self-gate 触发面，Windows 上 commit 后无 "self-gate-review" WARNING。
   - **失败 2** `test_bdd_1_latest_pointer_after_noarg_install`（unit/test_agate_version_install.py:82）——agate-install 无参后 `latest` 指针 `exists()` False（Windows 复制模式）。
2. **根因分析（已确认，直接采信，聚焦落地修复）**：
   - **失败 2 根因（已实证）**：`_run_install` helper（test_agate_version_install.py:21-27）只设 `env={"HOME": str(home)}`，未设 `USERPROFILE`。Windows 上 `os.path.expanduser("~")` 优先用 USERPROFILE（ntpath 不认 HOME）→ `_agate_home()`（agate-install.py:66-68）解析到**真实用户目录**（CI 实证：路径 `C:\Users\runneradmin\.agate`）→ `latest`/`current` 写到真实 `~/.agate` → 测试断言 `home/.agate/latest` 不存在。对照：同批 `test_agate_version_resolve.py:17-19` 的 `_resolve_env` **正确设置了 HOME+USERPROFILE**——install 测试 helper 是遗漏。
   - **失败 1 根因（已收敛，待你落地验证）**：
     - CI 实证：returncode==0（commit 成功）+ output 无 WARNING 无 GATE ERROR（仅 `[master d5620ee] update readme`）。薄壳 fail-closed 分支（GATE ERROR + exit 1）会阻断 commit（returncode!=0）→ **与 CI 矛盾，排除薄壳 fail-closed 触发**。
     - 决定性对照：unit 测试 `test_cmsg_1`（windows_smoke，**Windows 冒烟通过**）直接用 `bash commit-msg-self-gate.sh <msgfile>` + AGATE_ROOT env 跑同一薄壳链 → **薄壳+resolve-entry+commit-msg-self-gate.py 全链在 Windows 可用**。`test_csg_1` 唯一区别是 **git 调用 hook**（copy 到 .git/hooks/commit-msg）→ 失败点必然在 git→hook 边界。
     - git-for-windows 机制（mingw.c）：`find_hook` 用 access(X_OK)，mingw_access 剥掉 X_OK 仅判文件存在 → copy 模式 hook 也会被 git 执行；`parse_interpreter` 读 shebang `#!/usr/bin/env bash` → interpreter 取 basename `env`（**丢掉 `bash` 参数！**）→ path_lookup("env") 在 PATH 找 env.exe → 用 interpreter 重新构造 argv 执行。
     - **候选修复方向（供你验证选择）**：
       a. git→hook 边界：Windows 上 git 用 `env` 解释器执行 hook（shebang `#!/usr/bin/env bash` 的 `bash` 参数被 mingw 剥掉）→ hook 实际以 `env <hook> args` 方式运行 → 若 PATH 无 bash 或 env 不传 bash 参数，hook 不执行/执行失败但 git 吞掉 → 无 WARNING + returncode 0。**验证**：CI 日志 hook 是否执行；或 Linux 模拟 `env <hook>` 无 bash 的调用。
       b. 若确认是 shebang 解析问题：改 hook 薄壳首行 shebang（如 `#!/bin/bash` 或显式 `#!/usr/bin/env -S bash`）或在测试侧改用 `bash hook` 直接调用（但测试必须走 git 调用才有意义）——**先确认根因再选方向**。
     - **注意**：如果最终修复落在"测试对 Windows 的适配"（如 `_setup_hook` 在 win32 用软链而非复制、或 git hook 调用方式适配），须确保不破坏测试验证 self-gate 的意图。
3. **修复纪律**：
   - 已有测试锁（两个 windows_smoke 测试）——**先分析根因再改**；若改测试 helper（如补 USERPROFILE）须确认是测试缺陷（对照同批 resolve 测试的正确实现），不是"改测试迁就实现"
   - 改实现脚本（agate-install.py / 3 hook 薄壳 / resolve-entry.py / commit-msg-self-gate.py）时按 TDD：先加/改测试确认红（Linux 模拟 Windows 分支），再改实现确认绿
   - **Linux 全量必须保持全绿**（基线 823 passed）——Windows 修复不能破坏 Linux
   - 平台无关原则：禁止裸 python3 / 裸 /tmp / POSIX symlink 假设；Windows 分支用 `sys.platform == "win32"` 或 `AGATE_HOOK_COPY_MODE=1` 模拟
4. **验证（worktree 内）**：
   - `python3 -m pytest agate/tests/ -q`（全量必须全绿）
   - `python3 -m pytest agate/tests/unit/test_agate_version_install.py agate/tests/integration/test_commit_msg_self_gate_integration.py -q`（两测试文件）
   - `python3 agate/scripts/check-protocol-consistency.py --strict`（0 ERROR）
   - `shellcheck -S warning agate/scripts/*.sh`（0 error）
   - `bash agate/tests/scripts/count-tests.sh`（用例数未漂移）
5. **修复边界**：只修两个 Windows 失败，不扩大范围。若发现修复需超出"两个失败"（如薄壳机制深层问题），停下在 progress 标注，主 Agent 与主 checkout 确认。
6. **self-gate**：修复涉及 agate/scripts/*.py 或协议文档 → commit message 须含 `self-gate-review:` 或 `self-gate-skip:` 理由。
7. **只 add 修复文件**：不用 `git add -A`。commit message 前缀 `wf(TAG0008-P5fix):`。
8. **双工作区纪律**：worktree 内改代码；`~/.agate` / 主 checkout 禁止改动。

### 上游关联
- FIX-WINDOWS-TAG0008.md（交接单：两失败完整代码 + 排查方向 + 修复纪律）
- 失败 2 相关：test_agate_version_install.py:21-27 `_run_install` + agate-install.py:66-68 `_agate_home` + :74-88 `_write_pointer`（Windows 分支写文本指针）+ 对照 test_agate_version_resolve.py:17-19 `_resolve_env`（正确实现）
- 失败 1 相关：test_commit_msg_self_gate_integration.py:14-43 `_setup_hook`/`_commit` + commit-msg-self-gate.sh:6-16 薄壳 + commit-msg-self-gate.py:38-57 `_SELF_GATE_RE` + resolve-entry.py

### 输入文件
- /home/kity/oclab/agate/.worktrees/agate-TAG0008/FIX-WINDOWS-TAG0008.md（交接单，必读）
- /home/kity/oclab/agate/.worktrees/agate-TAG0008/agate/tests/unit/test_agate_version_install.py（失败 2 测试）
- /home/kity/oclab/agate/.worktrees/agate-TAG0008/agate/tests/unit/test_agate_version_resolve.py（对照正确实现）
- /home/kity/oclab/agate/.worktrees/agate-TAG0008/agate/tests/integration/test_commit_msg_self_gate_integration.py（失败 1 测试）
- /home/kity/oclab/agate/.worktrees/agate-TAG0008/agate/scripts/agate-install.py / commit-msg-self-gate.sh / commit-msg-self-gate.py / resolve-entry.py / agate_common.py / pre-commit-gate.sh（实现代码）
- /home/kity/oclab/agate/.worktrees/agate-TAG0008/agate/tests/conftest.py（fixtures：run_cli / git_repo / py_path）
- /home/kity/oclab/agate/.worktrees/agate-TAG0008/AGENTS.md（项目约定 + 测试平台无关原则）
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
- 环境状态：worktree 分支 feat/TAG0008-version-management；PR #148 CI Windows 冒烟 2 failed；Linux 全量 823 passed（修复前基线）
- 关键路径：worktree=/home/kity/oclab/agate/.worktrees/agate-TAG0008；测试 agate/tests/unit/ + agate/tests/integration/；实现 agate/scripts/
- 查证结果：Linux 本机两测试文件 15 passed（windows_smoke 用例走非 win32 分支）；resolve 测试 helper 已设 USERPROFILE，install 测试 helper 未设；薄壳 ENTRY_ROOT 依赖 env AGATE_ROOT（复制模式）
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
