---
phase: P6
task_id: TAG0009-tests-platform-neutral
type: acceptance
parent: P5-verification.md
trace_id: TAG0009-tests-platform-neutral-P6-20260813
status: approved
created: 2026-08-13
agent: verifier
# ── v2.0 机器汇总 ──
pass: 29
fail: 0
ui_affected: false
---

# P6 验收报告 — agate 测试套件平台无关化（TAG0009）

> 验收环境：worktree `/home/kity/oclab/agate/.worktrees/agate-TAG0005-0009`（Linux，UTF-8）。
> Windows 分支由测试内模拟环境覆盖（PYTHONIOENCODING=cp1252 / fakebin ln→cp / PATH 无 python3 / 无 bc / shellcheck 名探测），
> 真 Windows CI 由 bats job windows-latest 作最终确认（I7 supplementable）。
> 验收口径：功能任务标准口径，P1 的 29 条 BDD 逐条实跑（非文本声称），每条 PASS 引用实际命令输出证据文件。
> 验收记录的是验收时的事实：全部证据为本次实跑/实时 grep 输出落盘，未复用历史结论。

## 1. BDD 逐条验收结果

### 3.1 静态扫描器 gate（BDD-1~9）

- PASS BDD-1: 扫描器自身平台无关——脚本存在、无 GNU 专用特性（grep -P / --perl-regexp / -P 均未出现，POSIX ERE），行为测试通过(bdd-1-9-scanner-bats.log)
- PASS BDD-2: 硬编码 PATH 检出——fixture `PATH="/usr/bin:/bin"` 扫描 exit 1 并报告 R1 与文件路径(bdd-2-6-8-manual-rules.log)
- PASS BDD-3: 命令位置裸 python3 检出——fixture `python3 -c ...` 扫描 exit 1 并报告 R2 与文件路径(bdd-2-6-8-manual-rules.log)
- PASS BDD-4: symlink 单平台断言检出——fixture `[[ -L ... ]]` 扫描 exit 1 并报告 R3 与文件路径(bdd-2-6-8-manual-rules.log)
- PASS BDD-5: /tmp 逻辑路径检出——fixture `cd /tmp` 扫描 exit 1 并报告 R4 与文件路径；`$BATS_TEST_TMPDIR` 与 `# scan-exempt:` 行豁免(bdd-2-6-8-manual-rules.log, bdd-1-9-scanner-bats.log)
- PASS BDD-6: Unix-only 外部工具检出——fixture `echo 1 | bc` 扫描 exit 1 并报告 R5 与文件路径(bdd-2-6-8-manual-rules.log)
- PASS BDD-7: 扫描器接入 CI 检出即阻断——protocol-tests.yml 新增 platform-scan job，Linux 步骤跑扫描器且无 continue-on-error，命中即 job 失败阻断合并(bdd-7-27-ci-workflow.log)
- PASS BDD-8: 干净测试套件零检出——修复后对 `agate/tests/` 全树扫描 exit 0 无输出，同类扫描闭环成立(bdd-2-6-8-manual-rules.log, bdd-1-9-scanner-bats.log)
- PASS BDD-9: 扫描器自身有行为测试——14 个 @test 全绿（含含假设/干净 fixture、目录扩展名过滤、scan-exempt 标记仅豁免 R4 不豁免 R1/R2/R3 负向用例）(bdd-1-9-scanner-bats.log)

### 3.2 PATH 硬编码修复（BDD-10~12）

- PASS BDD-10: check-tdd-red.bats 移除 PATH 硬编码——全文件 grep 字面 `PATH="/usr/bin:/bin"` 0 处（grep exit 1）(bdd-10-11-tdd-red-grep.log)
- PASS BDD-11: 「PATH 无 python」场景改平台无关构造——TD.1b / TDD.F8 改用 `env -u PATH`，原 exit 语义保留（TD.1b 期望 `3 or 1`、TDD.F8 期望 `3`）(bdd-10-11-tdd-red-grep.log, bdd-12-tdd-red-bats.log)
- PASS BDD-12: 原 PATH 失败用例红绿灯语义不变——check-tdd-red.bats 全量 43 ok / 0 not ok(bdd-12-tdd-red-bats.log)

### 3.3 python3 探测 helper（BDD-13~17）

- PASS BDD-13: PYTHON 探测 helper 提供且平台无关——fixtures.bash `detect_python`（command -v 探测形态豁免扫描器 R2），`$PYTHON` 顶层导出可执行(bdd-13-15-17-helpers-python.log)
- PASS BDD-14: 测试侧裸 python3 全量清除——扫描器 R2 对 `agate/tests/` 全树零命中（exit 0），原始正则命中行全部落在注释/@test/command -v 探测豁免形态(bdd-14-bare-python3-zero.log)
- PASS BDD-15: helper 回退分支有 Linux 模拟测试——PATH 仅含 python（无 python3）环境下 detect_python 回退到 `python`(bdd-13-15-17-helpers-python.log)
- PASS BDD-16: script-side 41 例由 harness shim 兜底转绿——9 个受影响 .bats 文件 + check-tdd-red.bats 注入 `create_python_shim_bin` setup，实测 149 ok / 0 not ok(bdd-16-script-side-shim.log)
- PASS BDD-17: 无 python3 模拟下产品脚本行为不劣化——fakebin 放 exit 127 的 python3 stub 复现 41 例根因（静默 exit 0），注入 shim 后非法回退 P4→P2 正确 exit 1 拦截(bdd-13-15-17-helpers-python.log)

### 3.4 symlink 按平台分支（BDD-18~19）

- PASS BDD-18: install-hook.bats [[ -L ]] 断言按平台分支——Linux 分支用 readlink 断言真软链指向 pre-push-gate.sh（无 -L 字面满足 R3 零命中）；复制模式分支断言输出升级提醒而非软链(bdd-18-19-install-hook.log, bdd-18-19-pre-push-hook.log)
- PASS BDD-19: Windows 分支（ln 复制模式）有 Linux 模拟覆盖——fakebin ln→cp 复制模式下安装输出含「复制/需重跑」且不误报软链语义，install-hook.bats 与 integration/pre-push-hook.bats 均通过(bdd-18-19-install-hook.log, bdd-18-19-pre-push-hook.log)

### 3.5 /tmp 与 Windows 路径（BDD-20~21）

- PASS BDD-20: 测试逻辑路径不再使用裸 /tmp——agate-next-card.bats L104 改为 `cd "$BATS_TEST_TMPDIR"`，check-scope-resolved.bats 改为 `$BATS_TEST_TMPDIR/nonexistent-...`；4 处样例文本行保留原内容并加 `# scan-exempt:` 标记(bdd-20-tmp-replacement.log)
- PASS BDD-21: bdd-21 setup 平台无关——MINGW/MSYS 用正斜杠 `C:/proj/agate`、其余字面反斜杠 `C:\proj\agate` 平台分支构造，双平台断言同一输出串「路径：phase-cards/P3-tdd.md」，32 ok / 0 not ok(bdd-20-21-next-card-scope-resolved.log)

### 3.6 输出匹配 / 编码 / 外部工具（BDD-22~25）

- PASS BDD-22: 输出匹配断言对行尾差异健壮——ci-gate-backstop.bats 等行尾敏感断言匹配前 `tr -d '\r'` 归一化，模拟 CRLF 混入仍命中，11 ok / 0 not ok(bdd-22-23-ci-gate-backstop.log)
- PASS BDD-23: 中文关键词对编码差异健壮——文件级 `export PYTHONIOENCODING=utf-8` 兜底中文输出；cp1252 模拟用例验证：未导出时中文 print 崩溃（证明风险源）、文件级导出后无崩溃且中文关键词可断言(bdd-22-23-ci-gate-backstop.log)
- PASS BDD-24: agate-extract-context.sh 移除 bc 依赖——L128 改为 `awk '{s+=$1} END{print s+0}'` 求和；无 bc 模拟环境（失败 stub 前置）下单值 `1` 与多文件 `2+1=3` 求和正确，16 ok / 0 not ok(bdd-24-extract-context.log, bdd-24-awk-sum-manual.log)
- PASS BDD-25: env-adapt-docs.bats bdd-34 shellcheck 调用平台无关——fixtures.bash 探测 `SHELLCHECK`（shellcheck|shellcheck.exe），调用 `${SHELLCHECK:-shellcheck} -S warning "$AGATE_ROOT"/scripts/*.sh`，9 ok / 0 not ok(bdd-25-env-adapt-docs.log)

### 3.7 Linux 模拟覆盖 Windows 分支（BDD-26）

- PASS BDD-26: 每个 Windows 分支有对应 Linux 显式模拟测试——cp1252（bdd-23/26）、ln 退化为复制（bdd-18/19）、PATH 无 python3 仅 python（bdd-15/26）、无 bc（EC.16）、shellcheck 名探测（bdd-34/25）五分支各有真实断言用例(bdd-26-windows-branch-simulation-coverage.log)

### 3.8 真 Windows CI 最终确认（BDD-27~29）

- PASS BDD-27: bats job 增加 windows-latest 作最终确认——protocol-tests.yml bats job 改 matrix `[ubuntu-latest, windows-latest]`，Windows 分支用 bash shell + 下载 bats-core v1.11.0 + `PYTHONIOENCODING: utf-8`，且新增扫描器行为测试步骤(bdd-7-27-ci-workflow.log)
  - **验收偏差（v0.45.0 合并阶段设计变更，主 Agent 确认）**：Windows bats 从"全量最终确认"调整为"**技术路线冒烟**"——全量 747 用例在 Windows 上 ~11.5 分钟且随测试增长线性上升，阻塞 CI。变更后 `bats` job Windows 分支只跑 `agate/tests/scripts/check-windows-smoke.sh`（每文件第 1 个用例 + 名称含平台敏感关键词的用例，约 60 文件代表子集，`xargs -P 4` 并行约 2 分钟）。**功能正确性由 Linux 全量保证（不降级）**，Windows 只验证每条平台敏感机制（py_path / shim / cp1252 / CRLF / symlink / 盘符路径等）代表用例跑通——技术路线成立则共享同机制（helper/shim/setup）的同类用例在 Windows 应同样通过。代表选取规则机械（规则即定义，无人工维护清单），新增 WSMOKE.1-7 测试锁定脚本行为 + 脚本自身平台无关（扫描器 0 命中）。
- PASS BDD-28: Linux 全量基线全程全绿——P5 复核：sanity+unit+regression+integration 全量 733 ok / 0 not ok，consistency --strict 0 ERROR、shellcheck 0 error、扫描器零命中，全部 EXIT_CODE: 0(bdd-28-linux-baseline.log, test-output.log)
- PASS BDD-29: 修改流程先红后绿——git 历史证实 P3 commit 先行交付测试（扫描器 14 用例红灯 exit 127、check-tdd-red 改造断言），P4 commit 才首次创建 `check-platform-assumptions.sh` 实现，符合 AGENTS.md「先加失败测试再改」工作流(bdd-29-tdd-red-green.log)

## 2. 验收执行说明

- 29/29 BDD 全部实跑（bats 运行 / 扫描器实跑 / grep 静态断言 / git log 复核），无「应该能过」类推断结论。
- 证据文件均为本次验收实时产出，命令输出落盘 + 末行 `EXIT_CODE: <n>`（test-output.log 汇总全部 15 组执行）。
- 无 UI 影响：本任务为测试基建 + 扫描器 + CI，`ui_affected: false`（与 P2-design frontmatter 一致）。
- 自查≠gate：本报告为 verifier 自查产出，最终判定以主 Agent 运行的 gate 脚本为准。

**Summary**: 29/29 PASS, 0 FAIL
