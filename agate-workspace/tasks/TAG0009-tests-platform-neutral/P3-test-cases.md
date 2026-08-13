---
phase: P3
task_id: TAG0009-tests-platform-neutral
type: test-cases
parent: P2-design.md
trace_id: TAG0009-tests-platform-neutral-P3-20260813
status: draft
created: 2026-08-13
agent: test-designer
---

# P3 测试用例清单 — TAG0009 测试套件平台无关化

**test_code_dir**: `agate/tests/`

> 声明：测试代码目录为 `agate/tests/`（含新增 `scripts/check-platform-assumptions.bats` 与任务 B 修改的既有测试文件）。
> 本文档将 29 条 BDD 全部映射到测试用例（1:1）。扫描器相关（BDD-1~9）由**本拆分任务 A** 新建
> `agate/tests/scripts/check-platform-assumptions.bats` 落实；其余（BDD-10~29）属拆分任务 B（改既有测试文件），
> 映射表中标注「改动断言」的用例**本轮不实际修改**，由任务 B 执行。

## 0. 本拆分任务（A）已交付的扫描器测试

**文件**：`agate/tests/scripts/check-platform-assumptions.bats`（14 个 @test，新建，任务 A 完成）
**红灯确认**：bats 14/14 全红（扫描器 `agate/scripts/check-platform-assumptions.sh` 尚未创建，exit 127 = 命令不存在），属预期真红灯。
**自净保证**：测试文件自身已按 R1-R5 模式集 grep 验证 0 命中（fixture 内容全部运行时 fragment 拼接，源码无字面假设），
确保扫描器对全树扫描（BDD-8）时本文件不误报。

| BDD | 测试名 | 文件 | 断言类型 | 预期现状 |
|-----|--------|------|---------|---------|
| 1 | test_bdd_1_scanner_script_exists_platform_neutral | scripts/check-platform-assumptions.bats | 文件存在 + 无 grep -P/--perl-regexp（POSIX ERE 约束） | 红（脚本不存在） |
| 2 | test_bdd_2_scanner_detects_hardcoded_path | 同上 | exit 1 + 输出含 R1 与文件路径 | 红 |
| 3 | test_bdd_3_scanner_detects_bare_python3 | 同上 | exit 1 + 输出含 R2 与文件路径 | 红 |
| 4 | test_bdd_4_scanner_detects_symlink_assertion | 同上 | exit 1 + 输出含 R3 与文件路径 | 红 |
| 5 | test_bdd_5_scanner_detects_tmp_path | 同上 | exit 1 + 输出含 R4 与文件路径 | 红 |
| 6 | test_bdd_6_scanner_detects_bare_bc | 同上 | exit 1 + 输出含 R5 与文件路径 | 红 |
| 7 | （CI 文档断言）protocol-tests.yml 新增 platform-scan job，Linux 步骤 exit 1 阻断 | .github/workflows/protocol-tests.yml | 文档断言（CI 配置，P5/P7 验证） | 红（CI 未接入）；阻断机制由 BDD-2~6 exit 1 语义支撑 |
| 8 | test_bdd_8_clean_tree_zero_detection | scripts/check-platform-assumptions.bats | 对 `$AGATE_ROOT/tests` 全树 exit 0 + 无输出 | 红（命令不存在；任务 B 全部修复后转绿） |
| 9 | test_bdd_9_dirty_fixture_all_rules_reported | 同上 | 含 5 类假设 fixture → exit 1 + R1~R5 全报告 | 红 |
| 9 | test_bdd_9_clean_fixture_zero_report | 同上 | 干净 fixture（R2 五类豁免形态 + $BATS_TEST_TMPDIR）→ exit 0 无输出 | 红 |
| 9 | test_bdd_9_directory_scan_respects_shell_extension_filter | 同上 | 目录目标递归扫 *.bats/*.bash/*.sh，忽略其他扩展名 | 红 |
| 9 | test_bdd_9_scan_exempt_exempts_r4_sample_text | 同上 | 负向：`# scan-exempt:` 标记豁免 R4 样例文本 → exit 0 | 红 |
| 9 | test_bdd_9_scan_exempt_does_not_exempt_r1_path | 同上 | 负向：标记不豁免 R1 → exit 1 + R1 | 红 |
| 9 | test_bdd_9_scan_exempt_does_not_exempt_r2_python | 同上 | 负向：标记不豁免 R2 → exit 1 + R2 | 红 |
| 9 | test_bdd_9_scan_exempt_does_not_exempt_r3_symlink | 同上 | 负向：标记不豁免 R3 → exit 1 + R3 | 红 |

> 说明：BDD-7 的「检出即阻断」本质是 CI job 接线（protocol-tests.yml platform-scan job，Linux 步骤 exit 1 阻断合并），
> 属文档断言（任务 B / P5 落实 CI 配置）；其可观测机制（扫描器命中即 exit 1）已由 BDD-2~6 的 exit 1 断言锁定。

## 1. 全量 BDD 1:1 映射（29 条）

| BDD | 测试名 / 断言 | 文件 | 断言类型 | 预期现状 | 执行方 |
|-----|--------------|------|---------|---------|--------|
| 1 | 见 §0 test_bdd_1 | scripts/check-platform-assumptions.bats | 行为断言 | 红 | 任务 A（已交付） |
| 2 | 见 §0 test_bdd_2 | 同上 | 行为断言 | 红 | 任务 A（已交付） |
| 3 | 见 §0 test_bdd_3 | 同上 | 行为断言 | 红 | 任务 A（已交付） |
| 4 | 见 §0 test_bdd_4 | 同上 | 行为断言 | 红 | 任务 A（已交付） |
| 5 | 见 §0 test_bdd_5 | 同上 | 行为断言 | 红 | 任务 A（已交付） |
| 6 | 见 §0 test_bdd_6 | 同上 | 行为断言 | 红 | 任务 A（已交付） |
| 7 | platform-scan job 文档断言（§0 说明） | .github/workflows/protocol-tests.yml | 文档断言 | 红 | 任务 B |
| 8 | 见 §0 test_bdd_8 | scripts/check-platform-assumptions.bats | 行为断言 | 红 | 任务 A（已交付） |
| 9 | 见 §0 7 个用例 | 同上 | 行为断言（含负向） | 红 | 任务 A（已交付） |
| 10 | 文档断言：修复后全文件 grep 字面 `PATH="/usr/bin:/bin"` 为 0 | unit/check-tdd-red.bats | 文档断言（grep） | 红（当前 15 处） | 任务 B |
| 11 | 改动断言：TD.1b（L48-51）/ TDD.F8（L380-383）改 `env -u PATH` 构造，exit 3/1 语义保持（TEST_RUNNER 不存在路径→exit 1 由 TD.1 覆盖，不重复） | unit/check-tdd-red.bats | 改动断言 | 红 | 任务 B |
| 12 | 回归断言：check-tdd-red.bats 全量通过，红绿灯 exit 0/1/2/3 语义不变 | unit/check-tdd-red.bats | 回归断言 | 绿（改后需保持） | 任务 B |
| 13 | 新用例：fixtures.bash `detect_python` 优先 python3 回退 python，导出 PYTHON；helper 自身探测形态豁免扫描器 | tests/helpers/fixtures.bash + 引用用例 | 行为断言 | 红（helper 未实现） | 任务 B |
| 14 | 文档断言：25 文件测试侧裸 python3 → $PYTHON，全树 R2 零命中（BDD-8 test_bdd_8 自动覆盖）+ 对 .bats grep 命令位置 python3 为 0 | 25 个 .bats 文件 | 文档断言（grep） | 红 | 任务 B |
| 15 | 新用例：PATH 仅含 python 无 python3 的模拟环境跑 detect_python → 回退 python（Linux 模拟 Windows） | fixtures.bash 相关用例 | 行为断言 | 红 | 任务 B |
| 16 | 改动断言：9+1 受影响 .bats 文件 setup 注入 create_python_shim_bin，41 例 script-side 相关用例转绿 | 9 个 .bats + check-tdd-red.bats | 行为断言（回归） | 红（41 例当前失败） | 任务 B |
| 17 | 新用例：无 python3 模拟环境对比 shim 前后产品脚本 gate 判定一致（不静默 exit 0） | 相关 .bats | 行为断言 | 红 | 任务 B |
| 18 | 改动断言：install-hook.bats 2 处 [[ -L ]] 拆 Linux 真软链 + Windows 复制模式两套用例 | unit/install-hook.bats | 平台分支断言 | 红 | 任务 B |
| 19 | 新用例：复用 L43 先例 mock ln→cp 复制模式，断言输出升级提醒且不误报软链 | unit/install-hook.bats | 平台分支断言（Linux 模拟） | 红（新增用例；L43 既有用例绿） | 任务 B |
| 20 | 改动断言：agate-next-card.bats L104 `cd /tmp` → `$BATS_TEST_TMPDIR`；check-scope-resolved.bats L8 → `$BATS_TEST_TMPDIR`；4 处样例文本行尾加 `# scan-exempt:` 标记且内容原样 | unit/agate-next-card.bats / unit/check-scope-resolved.bats / check-tdd-red.bats L139,148 / check-tdd-red-formatter.bats L97,105 | 改动断言 | 红 | 任务 B |
| 21 | 改动断言：bdd-21 setup 平台分支构造（MINGW/MSYS 用正斜杠、其余字面反斜杠），双平台断言同一输出串 | unit/agate-next-card.bats | 平台分支断言 | 红 | 任务 B |
| 22 | 改动断言：ci-gate-backstop.bats 等行尾敏感断言匹配前 `tr -d '\r'` 归一化 | unit/ci-gate-backstop.bats 等 | 行为断言（改动） | 红 | 任务 B |
| 23 | 改动/新用例：含中文输出 python 工具的测试文件级 export PYTHONIOENCODING=utf-8；cp1252 模拟用例断言不 UnicodeEncodeError 崩溃 | unit/ci-gate-backstop.bats 等 | 行为断言（编码） | 红 | 任务 B |
| 24 | 改动断言：agate-extract-context.sh L128 bc→awk，无 bc 模拟环境下求和正确（L78-86 单值 1 / L198-205 多文件 2+1=3） | unit/agate-extract-context.bats + agate/scripts/agate-extract-context.sh | 行为断言（改动） | 红 | 任务 B |
| 25 | 改动断言：env-adapt-docs.bats bdd-34 shellcheck/shellcheck.exe 探测 + glob 引号统一 | unit/env-adapt-docs.bats | 行为断言（改动） | 红 | 任务 B |
| 26 | 分散新用例：PYTHONIOENCODING=cp1252（编码）/ fakebin ln→cp（复制模式）/ 纯净 PATH 无 python3（回退与无 bc）/ SHELLCHECK 探测缺失——每个 Windows 分支 Linux 至少一个显式模拟用例 | 各相关 .bats | 平台分支断言（Linux 模拟） | 红（新增用例） | 任务 B |
| 27 | 文档断言：protocol-tests.yml bats job 改 matrix `[ubuntu-latest, windows-latest]`，Windows 分支 0 失败（push/PR 触发） | .github/workflows/protocol-tests.yml | 文档断言 | 红 | 任务 B |
| 28 | P5 gate 全量回归：bats sanity+unit+regression+integration（726）+ consistency --strict 0 ERROR + shellcheck 0 error | 全量 | 回归断言 | 绿（全程保持） | P5 执行 |
| 29 | 流程约束：每处修复先加平台无关失败测试确认红再改（check-tdd-red 红灯 + AGENTS.md 工作流） | 任务 B 全流程 | 流程约束（非可执行用例） | 不适用 | 任务 B |

## 2. 重要说明与 Gap 标注

- **用例数漂移（I10）**：`count-tests.sh` 仅统计 `unit/*.bats regression/*.bats integration/*.bats`，**不含 `tests/scripts/`**，
  故新增 `scripts/check-platform-assumptions.bats`（14 例）**不改变 count-tests 总数（720）**，tests/README 表格无需同步该项。
  任务 B 新增/改动用例若落在 unit/regression/integration 则需按 I10 约定同步 README 与计数。
- **Gap：扫描器测试未被标准 bats 调用覆盖**——P5 gate 命令为 `bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/`，
  不包含 `tests/scripts/*.bats`。P2 未声明扫描器测试的调用位置。**建议**：P4/P5 把 `agate/tests/scripts/check-platform-assumptions.bats`
  并入 bats 调用（CI `protocol-tests.yml` bats job 或新增调用项），否则 BDD-9 行为测试在标准流程中不会被运行。
  此为设计缺口提示（非任务 A 可自行决定范围），请主 Agent 知悉并决定落点。
- **扫描器自身测试的红灯性质**：14/14 全红且为「命令不存在」（exit 127）类——B 类红灯可推进，非测试代码自身错误。
- **负向用例**：`# scan-exempt:` 标记只豁免 R4（/tmp 样例文本），不豁免 R1/R2/R3（P2-review 非阻塞建议已落实为 4 个用例）。
- **BDD-14 文档断言口径**：以扫描器 R2 全树零命中（test_bdd_8）为准绳 + 25 文件逐文件 grep 复核；`agate-debt-check.bats` 实测 0 处 python3，不属测试侧。

## 3. 约束

- 本任务不改协议语义与 gate 逻辑判定规则（P1 红线）；Linux 基线（BDD-28）是全程回归底线。
- 扫描器测试文件自身必须保持"干净"（fragment 拼接构造 fixture），任何新注释/断言不得引入 R1-R5 字面命中。
- 测试代码目录：`agate/tests/`（test_code_dir 声明）；本拆分任务仅新建扫描器测试，不改任何既有测试文件（任务 B 职责）。

[PROD_NOT_TOUCHED]
