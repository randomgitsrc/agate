---
phase: P3
task_id: TAG0010-python-migration
type: test-cases
parent: P2-design.md
trace_id: TAG0010-P3-20260814
status: draft
created: 2026-08-14
agent: test-designer
---

# P3 测试设计 — agate 产品逻辑 Python 化（阶段一）

> refactor 任务（P1 frontmatter `change_type: refactor`）——P3 走**回归测试口径**。
> 本文件是「回归口径声明 + 既有用例覆盖映射」：复用/保留既有 bats 测试，标注每条回归用例覆盖的迁移后脚本与路径；**不新增功能行为断言**（重构无新行为可断言）；**不跑 TDD 红灯**（测试套件本就全绿，回归质量由 P5 全量回归 + P6 regression.log 兜底）。
> 测试代码 = 既有 bats 的调用方式改造（机械调用面改 `bash x.sh` → `"$PYTHON" x.py` + 5 文件断言级变更），实际改动在 P4，P3 只做设计与映射。

## 0. test_code_dir 声明

```
test_code_dir: P3-test-code/
```

- 本任务**不新建测试代码**——测试代码是既有 bats 文件的调用方式改造（P1 表 D 两层影响），改造实际发生在 P4（implementer 逐脚本迁移时同步改调用点）。
- P3-test-code/ 目录保留，用于放置 P4 改造的**设计占位/说明**（若 P4 需要）；P3 阶段测试代码 = 既有 bats 全量（当前 733 用例全绿基线，见 §2 基线）。

## 1. 回归口径声明（refactor 任务）

- **不新增功能行为断言**：重构的目标是"30 个 sh 的 bash 逻辑迁移到 py，行为与重构前一致"——没有新功能行为可以断言。所有既有 bats 用例即为回归断言：改造后脚本（py 版）必须通过**同一套用例**。
- **不跑 TDD 红灯**：测试套件当前全绿（733 用例），check-tdd-red 红灯语义不适用（refactor 任务由 P5 全量回归 + P6 regression.log 兜底）。
- **回归验证主体**：
  - 行为契约断言（必须保持）：CLI 输出契约（`GATE ...:` 前缀 / exit 0/1/2 语义 / `AGATE_WORKSPACE=`/`AGATE_TASKS_DIR=` 两行输出 / gate-result.json 结构）、既有数据格式零迁移、CRLF 剥离、.agate-root 复制模式恢复、python 探测失败 fail-closed 阻断。
  - 调用方式改造（P4 机械面）：`bash "$AGATE_SCRIPTS/x.sh"` → `"$PYTHON" "$AGATE_SCRIPTS/x.py"`（复用 fixtures.bash `$PYTHON` detect_python，Windows 自动解析 python 而非 python3）。
- **断言级变更（5 文件，P2 §3.6）**：这些文件是既有断言中**显式断言 sh/python 接口或 bash 行为**的部分，随迁移改断言（语义仍是回归——断言重构后的 py 版行为与契约一致），变更细则见 §3.2。
- **count-tests 不减少**：改造后 `count-tests.sh`（`^@test` 口径，数 unit/regression/integration）用例数 ≥ 727，不减少（§6 对照）。

## 2. 测试基线（客观实测）

| 项目 | 值 | 依据 |
|------|-----|------|
| count-tests 口径 | **727 个 @test / 58 文件**（unit 46 + regression 6 + integration 6） | `count-tests.sh` 实测（只数 unit/regression/integration） |
| 全量 bats 含 sanity/scripts | 733 用例 / 61 文件（58 + sanity 6 + scripts 2 文件 21 用例） | `rg -c '^@test'` 实测 |
| gate_commands.P3/P5 | `bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/` | P2 §4 固化 |
| 机械调用面 | 30 bats 文件直接 run（AGATE_SCRIPTS 272 处 + AGATE_ROOT/scripts 55 处；含全部 bash 调用形态 409+74） | rg 实测 |
| 断言级文件 | 5 文件 / 38 用例（P4 改造后 40——check-platform-assumptions 14→16） | P1 表 D + P2 §3.6 |

## 3. 既有用例覆盖映射表

> 每个受影响 bats 文件 → 覆盖的迁移后脚本 → 用例数（`^@test` 口径实测）。
> 迁移后脚本命名：同名换后缀（check-gate.sh → check-gate.py，P1 SUGGEST-2）；hook 3 个保留 sh 薄壳；install-hook.sh → install-hook.py。

### 3.1 断言级变更文件（5 文件 / 38 → 40 用例）

| 受影响 bats 文件 | 用例数 | 覆盖的迁移后脚本 | 断言变更（P2 §3.6） |
|------------------|--------|------------------|----------------------|
| tests/scripts/check-platform-assumptions.bats | 14 → 16 | check-platform-assumptions.py | ①13 处调用改 py；②目录扫描扩展名过滤 `.bats/.bash/.sh` 扩展 `.py`；③"本体无 GNU 特性"断言改 py 语义（正则引擎约束）；④干净树契约重述；⑤新增 `.py` fixture 含 R1-R5 假设能被检出；⑥**新增 2 条 docstring 豁免用例**（docstring 内 python3 引用不命中 R2 + docstring 外裸 python3 仍被检出）——对应 BDD-6 |
| unit/env-adapt-docs.bats | 9 | 无（协议文档 + CI + ruff/shellcheck 层） | bdd-34（shellcheck `*.sh` 0 error）→ shellcheck 覆盖面收敛到 3 保留薄壳 + 新增 ruff 断言（`ruff check agate/scripts/` 0 error）；其余 8 个（bdd-23/24/25/16/26/27/33/32）断言不变——对应 BDD-2/3/4/8 |
| unit/agate-scripts-encoding.bats | 2 | 无（扫描 `agate/scripts/*.py`） | bdd-5（扫描 `*.py` encoding 守卫）覆盖面扩大为强守卫（含迁移新增 py）；bdd-8（agate-state-get.py Linux ASCII 回归）不变——对应 BDD-7/8 |
| unit/helpers-python.bats | 3 | check-state-transition.py（bdd-17）、agate_common.py probe_python（bdd-13/15） | bdd-17 重构为"py 自举后的 python 探测 + 失败回退"语义（不再依赖 bash shim）；bdd-13/15 的 detect_python helper 语义保留（bats 仍需 `$PYTHON`）——对应 BDD-9/10 |
| unit/agate-workspace-resolve.bats | 10 | agate_common.py（resolve_workspace 执行模式） | 10 处调用改 py；两行输出契约（`AGATE_WORKSPACE=`/`AGATE_TASKS_DIR=`）与 CRLF 剥离（bdd-18）断言保留（py 版必须满足的行为契约）——对应 BDD-10 |

### 3.2 断言级 5 文件逐条映射（38 条，含 P4 将新增 2 条）

**tests/scripts/check-platform-assumptions.bats（14 条，P4 后 16）**

| 用例（@test 标题） | 覆盖的迁移后脚本/契约 |
|-------------------|----------------------|
| test_bdd_1_scanner_script_exists_platform_neutral | check-platform-assumptions.py 存在 + 无 GNU 专用特性（POSIX ERE 无 grep -P）——③py 语义重述 |
| test_bdd_2_scanner_detects_hardcoded_path | R1 规则（硬编码 PATH）在 py 版存活 |
| test_bdd_3_scanner_detects_bare_python3 | R2 规则（命令位置裸 python3）在 py 版存活 |
| test_bdd_4_scanner_detects_symlink_assertion | R3 规则（方括号 -L）在 py 版存活 |
| test_bdd_5_scanner_detects_tmp_path | R4 规则（临时目录字面量）在 py 版存活 |
| test_bdd_6_scanner_detects_bare_bc | R5 规则（裸 bc）在 py 版存活 |
| test_bdd_8_clean_tree_zero_detection | py 版扫描器对 `$AGATE_ROOT/tests` 全树 0 命中（干净树契约） |
| test_bdd_9_dirty_fixture_all_rules_reported | R1-R5 全部报告（py 版行为） |
| test_bdd_9_clean_fixture_zero_report | R2 豁免形态 + R4 天然豁免（py 版行为） |
| test_bdd_9_directory_scan_respects_shell_extension_filter | ②扩展名过滤契约扩展 `.py`（新增 dirty.py 检出、ignored 忽略） |
| test_bdd_9_scan_exempt_exempts_r4_sample_text | 标记豁免仅限 R4 |
| test_bdd_9_scan_exempt_does_not_exempt_r1_path | 标记不豁免 R1 |
| test_bdd_9_scan_exempt_does_not_exempt_r2_python | 标记不豁免 R2 |
| test_bdd_9_scan_exempt_does_not_exempt_r3_symlink | 标记不豁免 R3 |
| **[新增] docstring 内 python3 引用不命中 R2（BLOCKER-1）** | docstring 豁免生效——docstring 是文档非可执行代码，与 `#` 注释行同类豁免（P2 §3.2 批次 1） |
| **[新增] docstring 外裸 python3 仍被检出（豁免不越界）** | 豁免不越界——真 R2 命中仍被检出 |

**unit/env-adapt-docs.bats（9 条）**

| 用例（@test 标题） | 覆盖的契约 |
|-------------------|-----------|
| bdd-23（7 张阶段卡片与 git-integration.md 规则 2 对齐） | 不变——协议文档引用 |
| bdd-24（git-integration.md 规则 2 语义不变） | 不变——协议文档引用 |
| bdd-25（修复后协议一致性检查 0 ERROR） | `check-protocol-consistency.py`（worktree 自身）——对应 BDD-2 |
| bdd-16（.gitattributes 不含强制 *.md eol 规则） | 不变 |
| bdd-26（SETUP.md 含 Windows 章节覆盖 PYTHONUTF8） | 不变（SETUP 引用同步后仍含 PYTHONUTF8） |
| bdd-27（.gitignore 预设 version.txt/dist 白名单） | 不变 |
| bdd-33（protocol-tests.yml 含 windows-latest matrix） | 不变——CI 引用 |
| bdd-34（shellcheck -S warning 0 error） | **改断言**：shellcheck 覆盖面收敛到 3 个保留 hook 薄壳 + 新增 ruff 断言——对应 BDD-3/4 |
| bdd-32（全量 bats 可被解析） | 不变——P5 全量回归前提 |

**unit/agate-scripts-encoding.bats（2 条）**

| 用例（@test 标题） | 覆盖的契约 |
|-------------------|-----------|
| bdd-5（全部 agate/scripts/*.py 文本 open()/read_text() 带 encoding=utf-8） | 覆盖迁移新增 py（BDD-7 强守卫扩大） |
| bdd-8（agate-state-get.py Linux 纯 ASCII .state.yaml 读取行为不变） | 回归——既有 py 行为不破坏（BDD-8） |

**unit/helpers-python.bats（3 条）**

| 用例（@test 标题） | 覆盖的迁移后脚本/契约 |
|-------------------|----------------------|
| bdd-13（detect_python 优先 python3，PYTHON 已导出且可执行） | fixtures.bash detect_python（bats 侧保留；product 侧 py 化后语义不变）——对应 BDD-5 |
| bdd-15（PATH 仅含 python 无 python3 时 detect_python 回退 python） | fixtures.bash detect_python 回退语义——对应 BDD-5 |
| bdd-17（无 python3 环境 + shim：非法回退 P4→P2 仍 exit 1 不静默放行） | **重构断言**：py 自举后不再依赖 bash shim，改为"py 探测 + 失败回退"（check-state-transition.py + agate_common.py probe_python；fail-closed 阻断）——对应 BDD-9 |

**unit/agate-workspace-resolve.bats（10 条）**

| 用例（@test 标题） | 覆盖的迁移后脚本/契约 |
|-------------------|----------------------|
| WR.1（默认工作区位置为项目内 agate-workspace/） | agate_common.py resolve_workspace（两行输出契约） |
| WR.2（无 .agate.env 时不报错、走默认位置） | 同上 |
| WR.3（.agate.env 指向项目外绝对路径） | 同上 |
| WR.4（.agate.env 相对路径相对项目根解析） | 同上 |
| WR.5（工作区路径含空格仍正常解析） | 同上（Path.resolve() 归一） |
| WR.6（环境变量 AGATE_TASKS_DIR 二级解析源） | 同上 |
| WR.7（.agate.env 显式配置优先于 AGATE_TASKS_DIR） | 同上 |
| WR.8（orchestrator 从工作区内路径读取 project.md） | 同上（解析输出锚定） |
| WR.9（orchestrator 从工作区 tasks/ 读取任务看板） | 同上（解析输出锚定） |
| bdd-18（.agate.env 尾部 \r 不污染 AGATE_WORKSPACE 解析） | 同上（CRLF 剥离契约，py 版必须满足） |

### 3.3 机械调用面文件（断言不变，改调用方式）

> 30 bats 文件 / 379 处直接 run（AGATE_SCRIPTS 314 + AGATE_ROOT/scripts 65，P1 表 D 口径；本 P3 实测 272+55 直接 run 形态、含全部 bash 调用形态 409+74，差异为统计形态，改造范围一致）。

| 受影响 bats 文件 | 用例数 | 覆盖的迁移后脚本（调用点改 py） |
|------------------|--------|--------------------------------|
| unit/check-gate.bats | 124 | check-gate.py（+ G8.9/G8.10 覆盖 check-debt.py 联动） |
| unit/check-gate-p1-review.bats | 9 | check-gate.py（P1 分支） |
| unit/check-gate-p5-diff.bats | 13 | check-gate.py（P5 分支） |
| unit/check-tdd-red.bats | 43 | check-tdd-red.py |
| unit/check-tdd-red-formatter.bats | 13 | check-tdd-red.py（formatter 解析） |
| unit/check-pruning.bats | 29 | check-pruning.py |
| unit/check-state-transition.bats | 30 | check-state-transition.py |
| unit/check-state-yaml.bats | 9 | check-state-yaml.py |
| unit/check-frontmatter.bats | 14 | check-frontmatter.py |
| unit/check-changelog.bats | 8 | check-changelog.py |
| unit/check-retrospective.bats | 10 | check-retrospective.py |
| unit/check-scope-resolved.bats | 10 | check-scope-resolved.py |
| unit/check-p6-evidence.bats | 30 | check-p6-evidence.py |
| unit/check-p6-format.bats | 16 | check-p6-format.py |
| unit/check-p6-provenance.bats | 36 | check-p6-provenance.py |
| unit/agate-debt-check.bats | 21 | check-debt.py（间接：check-debt.sh 薄壳 → check-debt.py，经 agate-debt-check.py） |
| unit/agate-capture-env-baseline.bats | 15 | agate-capture-env-baseline.py |
| unit/agate-archive-stale-outputs.bats | 7 | agate-archive-stale-outputs.py |
| unit/agate-extract-context.bats | 16 | agate-extract-context.py |
| unit/agate-next-card.bats | 22 | agate-next-card.py |
| unit/agate-inject-card.bats | 11 | agate-inject-card.py |
| unit/agate-migrate-workspace.bats | 9 | agate-migrate-workspace.py |
| unit/agate-render-dispatch-prompt.bats | 20 | agate-render-dispatch-prompt.py |
| unit/agate-retreat-to.bats | 5 | agate-retreat-to.py |
| unit/install-hook.bats | 6 | install-hook.py（软链/复制模式/.agate-root 标记） |
| unit/commit-msg-self-gate.bats | 4 | commit-msg-self-gate.py（薄壳 exec） |
| unit/dispatch-context-warning.bats | 1 | pre-commit-gate.py（dispatch-context hash 校验 + 子脚本调度） |
| unit/ci-gate-backstop.bats | 11 | ci-gate-backstop.py（批次 0 改 python 调用，消 _find_bash） |
| integration/pre-commit-hook.bats | 48 | pre-commit-gate.py（薄壳 exec + 12 子脚本调度 + PROD_TOUCHED + bdd-19 复制模式恢复） |
| integration/pre-push-hook.bats | 4 | pre-push-gate.py（薄壳 exec + AGATE_ALIGNMENT_REVIEW_THRESHOLD） |
| integration/commit-msg-self-gate.bats | 6 | commit-msg-self-gate.py（薄壳 exec + self-gate 触发面） |
| integration/protocol-alignment-review.bats | 8 | commit-msg-self-gate.py（SG.7 断言薄壳可执行）+ 锚点表 |
| integration/dispatch-context-card.bats | 8 | pre-commit-gate.py（dispatch-context 校验）+ agate-inject-card.py/agate-next-card.py |
| integration/consistency.bats | 11 | check-protocol-consistency.py（锚点表同步后；CON.8 锁已实现脚本含关键字） |
| regression/v060-design-gap.bats | 4 | check-gate.py（DESIGN_GAP 交叉核对） |
| regression/v060-p8-cached.bats | 3 | check-gate.py（P8 分支） |
| regression/v060-p8-internal-only.bats | 3 | check-pruning.py（P8 裁剪） |
| regression/v060-r4-cached.bats | 2 | check-pruning.py（P7 裁剪） |
| regression/v060-yaml-indent.bats | 3 | task-files.md 模板（一致性，无脚本调用） |
| regression/v040-dotarchived-exclusion.bats | 2 | agate-common.py iter_md_files 等价（无脚本调用） |
| scripts/check-windows-smoke.bats | 7 | check-windows-smoke.sh（tests/scripts/ 保持 sh，不迁移）+ WSMOKE.7 调 check-platform-assumptions.py |
| sanity.bats | 6 | helpers 加载（load.bash/fixtures.bash/git-helper.bash） |

## 4. BDD 映射表（P1 的 10 条 BDD → 对应既有 bats 用例）

> 回归口径下 BDD 是"关键路径行为不变断言"，下表列出验证每条 BDD 的既有用例（改造后仍须通过）。

| BDD | 验收标准（P1 §4） | 验证的既有 bats 用例 |
|-----|-------------------|----------------------|
| BDD-1 | 全量 bats 全绿 + count-tests 不减少 | **全量回归**：gate_commands.P3/P5 = sanity+unit+regression+integration（733 用例全绿）；env-adapt-docs bdd-32（全量可解析）；count-tests.sh = 727 不减少（§6） |
| BDD-2 | consistency 0 ERROR（--strict） | integration/consistency.bats（11 条，含 CON.8 锚点表锁关键字）；unit/env-adapt-docs bats bdd-25 |
| BDD-3 | ruff 覆盖全部 agate/scripts/*.py | env-adapt-docs bdd-34（P4 新增 ruff 断言：`ruff check agate/scripts/` 0 error） |
| BDD-4 | shellcheck 覆盖面收敛到 3 保留薄壳 | env-adapt-docs bdd-34（P4 改断言：shellcheck `*.sh` 受扫集合 == 3 hook 薄壳） |
| BDD-5 | Windows CI 冒烟通过 | scripts/check-windows-smoke.bats（WSMOKE.1-7，机制保留）；CI windows-latest matrix（bdd-33 断言 matrix 存在） |
| BDD-6 | 扫描器扩展覆盖 .py | check-platform-assumptions.bats（14→16 条，含扩展名过滤扩展 .py、.py fixture 检出、docstring 豁免两类用例） |
| BDD-7 | 新增 py 全部显式 encoding=utf-8 | agate-scripts-encoding.bats bdd-5（覆盖面扩到迁移后全部 py） |
| BDD-8 | py 代码兼容 Python 3.8+ | env-adapt-docs bdd-34（P4 新增 ruff 断言，target-version=py38 拒 match）；agate-scripts-encoding bdd-8（回归） |
| BDD-9 | hook 薄壳保留复制模式恢复且 exec 失败 fail-closed | integration/pre-commit-hook.bats bdd-19（.agate-root 复制模式恢复）；unit/install-hook.bats（ln 复制模式提示 + BDD-18/19）；integration/pre-push-hook.bats（复制模式安装）；helpers-python bdd-17（P4 重构为 py 探测失败回退） |
| BDD-10 | CLI 输出契约与既有数据兼容 | agate-workspace-resolve.bats WR.1-9 + bdd-18（两行输出契约 + CRLF 剥离）；check-gate.bats / check-state-transition.bats（exit 0/1/2 语义 + GATE 前缀）；ci-gate-backstop.bats（对照 .gate-result.json 结构） |

## 5. 批次对应（表 E 批次 0-4 → 每批验证的 bats 文件清单）

> 批次划分与验证口径按 P2 §3.2 + P1 表 E。每批验证 = 全量 bats（gate_commands.P3）+ 该批专项清单，全绿才推进下一批。

| 批次 | 内容 | 该批验证的 bats 文件清单（专项） |
|------|------|--------------------------------|
| **批次 0 — 公共库** | gate-result.sh + agate-workspace-resolve.sh → agate_common.py；ci-gate-backstop.py 改 python 调用 | unit/agate-workspace-resolve.bats（10，改调 py 后绿）+ unit/helpers-python.bats（3，重构后绿）+ unit/ci-gate-backstop.bats（11，workspace 解析相关断言改后绿）+ 全量 bats |
| **批次 1 — 自足叶节点（13）** | check-changelog / check-frontmatter / check-state-yaml / check-p6-format / check-scope-resolved / agate-archive-stale-outputs / agate-extract-context / agate-next-card / agate-render-dispatch-prompt / agate-summary / agate-changes / agate-migrate-workspace / check-platform-assumptions（含扩展 .py 规则集） | 逐脚本迁移同步改对应 bats：unit/check-changelog.bats(8)、check-frontmatter.bats(14)、check-state-yaml.bats(9)、check-p6-format.bats(16)、check-scope-resolved.bats(10)、agate-archive-stale-outputs.bats(7)、agate-extract-context.bats(16)、agate-next-card.bats(22)、agate-render-dispatch-prompt.bats(20)、agate-migrate-workspace.bats(9)、scripts/check-platform-assumptions.bats(14→16)；agate-summary/agate-changes 无专属测试（文档引用 + 手动 verify）+ 全量 bats |
| **批次 2 — 复合（11）** | check-state-transition / check-retrospective / check-pruning / check-debt / check-tdd-red / check-gate / check-p6-evidence / check-p6-provenance / agate-capture-env-baseline / agate-retreat-to / agate-inject-card | check-state-transition.bats(30)、check-retrospective.bats(10)、check-pruning.bats(29)+v060-p8-internal-only(3)+v060-r4-cached(2)、agate-debt-check.bats(21)（check-debt 联动）、check-tdd-red.bats(43)+check-tdd-red-formatter.bats(13)、check-gate.bats(124)+check-gate-p1-review.bats(9)+check-gate-p5-diff.bats(13)+v060-design-gap(4)+v060-p8-cached(3)、check-p6-evidence.bats(30)、check-p6-provenance.bats(36)、agate-capture-env-baseline.bats(15)、agate-retreat-to.bats(5)、agate-inject-card.bats(11) + 全量 bats |
| **批次 3 — hook 链（4）** | pre-commit-gate 薄壳化 + commit-msg-self-gate + pre-push-gate + install-hook | integration/pre-commit-hook.bats(48，含 bdd-19)、integration/pre-push-hook.bats(4)、integration/commit-msg-self-gate.bats(6)+unit/commit-msg-self-gate.bats(4)、unit/install-hook.bats(6)、integration/protocol-alignment-review.bats(8)、unit/dispatch-context-warning.bats(1)、integration/dispatch-context-card.bats(8) + 全量 bats |
| **批次 4 — 收尾（0 ERROR 门槛）** | consistency 锚点表同步 + 文档引用同步 + SETUP pyyaml 强制化 + UPGRADING 新章节 + scripts/README.md 重写 + CI（shellcheck→ruff、扫描器调用） | integration/consistency.bats(11)（锚点表同步后 --strict 0 ERROR）、env-adapt-docs.bats(9)（bdd-34 shellcheck 收敛 + ruff 断言）、agate-scripts-encoding.bats(2)（bdd-5 覆盖面扩大）、check-windows-smoke.bats(7)、consistency `--strict` 0 ERROR + ruff 0 error + 全量 bats 绿 + Windows 冒烟绿 |

## 6. 用例数增减对照（count-tests 不减少的保证方式）

| 范围 | 当前（基线） | P4 改造后 | 净变化 |
|------|-------------|-----------|--------|
| count-tests 口径（unit+regression+integration `^@test`） | **727** | ≥ 727（不减少） | 0 或 +2 |
| 断言级 5 文件 | 38（14+9+2+3+10） | **40**（16+9+2+3+10） | +2（check-platform-assumptions 新增 2 条 docstring 豁免用例） |
| 全量 bats（含 sanity 6 + scripts 21） | 733 | ≥ 735 | +2 |

**保证方式**：
1. **`^@test` 行不删除**：机械调用面 30 文件只改 `bash x.sh` → `"$PYTHON" x.py`（调用命令名），不增删 `@test` 行；断言级 5 文件只改断言体、不删用例，check-platform-assumptions 另新增 2 条（14→16）。
2. **每批跑 count-tests.sh**：批次 0-4 每批完成即跑 `bash tests/scripts/count-tests.sh`，对比基线 727，只增不减。
3. **全量 bats 每批绿**：gate_commands.P3 = sanity+unit+regression+integration 每批全绿后推进（P0「逐脚本迁移 + 每步全量 bats」约束）。
4. **P5/P6 兜底**：P5 全量回归（gate_commands.P5）+ P6 regression.log（全量回归重跑记录）验证用例数未漂移。
5. **check-windows-smoke 机制不动**：代表用例选取规则（每文件第 1 个 + 平台敏感关键词）机械生效，随 bats 文件更新自动跟随。

## 7. 平台无关原则对照（回归口径下新增/改造用例的约束）

- 测试代码改造（P4）遵循 AGENTS.md 测试约定：无裸 `PATH="/usr/bin:/bin"`、无裸 `python3`（用 fixtures.bash `$PYTHON`/`detect_python`）、POSIX symlink 语义按平台分支断言、临时文件用 `$BATS_TEST_TMPDIR`。
- **扫描器洁净度**：本测试文件自身不含 R1-R5 字面命中（回归用例文本经 fragment 拼接），确保 py 版扫描器对全树扫描 0 命中。
- 新增 docstring 豁免用例（check-platform-assumptions.bats 第 15/16 条）用运行时 fragment 拼接，避免新引入 R2 字面命中。

## 8. P4 实施指引（供 implementer）

1. **机械调用面**：`bash "$AGATE_SCRIPTS/x.sh"` → `"$PYTHON" "$AGATE_SCRIPTS/x.py"`；`bash "$AGATE_ROOT/scripts/x.sh"` 同理。改动随脚本批次同步，每批全量 bats。
2. **断言级 5 文件**按 §3.2 逐条改造（细节在 P2 §3.6），改动后用例数 ≥ 基线。
3. **不新增功能行为断言**：除 check-platform-assumptions 新增 2 条 docstring 豁免用例（P2 BLOCKER-1 要求）外，不添加任何新断言。
4. **每批验证顺序**：改调用 → 跑该批专项 bats → 跑全量 bats → 跑 count-tests.sh → 跑 consistency（锚点表路径随批次同步改，非集中批次 4）。
