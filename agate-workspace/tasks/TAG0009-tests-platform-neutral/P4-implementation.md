---
phase: P4
task_id: TAG0009-tests-platform-neutral
type: implementation
parent: P2-design.md
trace_id: TAG0009-tests-platform-neutral-P4-20260813
status: draft
created: 2026-08-13
agent: implementer
---

# P4 实现说明 — TAG0009 测试套件平台无关化

> implementation_dir: `agate/tests/` + `agate/scripts/` + `.github/workflows/`

## 1. 改动清单（按 P2 §2 分组）

### 1.1 静态扫描器（§2.1，BDD-1~9）
- **新建 `agate/scripts/check-platform-assumptions.sh`**：bash + POSIX ERE grep（无 GNU `-P`/`--perl-regexp`），双平台可跑。
  - R1 硬编码 PATH：`PATH=[^[:space:]]*(/usr|/bin)`
  - R2 命令位置裸 python3：`(^|[[:space:]]|[=("'])python3([[:space:]]|$)`，豁免 `command -v python3/python` 探测、`env python3`、shebang、行首 `@test` 标题、行首注释行
  - R3 `[[ -L ]]`/`[ -L ]` 单平台断言：`(^|[[:space:]])[[]+[[:space:]]+-L[[:space:]]`
  - R4 `/tmp` 逻辑路径：`/tmp([[:space:]]|/|"|'|$)`，豁免 `$BATS_TEST_TMPDIR`（变量名天然不命中）+ 含 `# scan-exempt:` 标记的行（标记只豁免 R4，R1/R2/R3 不做行豁免）
  - R5 Unix-only 外部工具：`bc` 已登记
  - 用法：文件/目录 target；目录递归扫 `*.bats *.bash *.sh`；无参数默认 `agate/tests/`
  - 输出 `R{n} <file>:<line> <摘要>` 到 stderr；任一命中 exit 1，零命中 exit 0
- **新建 `agate/tests/scripts/check-platform-assumptions.bats`**（P3 已交付，P4 实现后转绿）：14 例全部通过（BDD-1~9，含负向：`# scan-exempt:` 不豁免 R1/R2/R3）
- **`agate/scripts/check-protocol-consistency.py`**：`SCRIPT_ALIGNMENT_ANCHORS` 补 `check-platform-assumptions.sh` 锚点（CHECK 9 反向覆盖要求，否则 consistency 报 WARNING）；运行后 `--strict` 0 ERROR

### 1.2 PYTHON 探测 helper + harness shim（§2.2/2.3，BDD-13~17）
- **`agate/tests/helpers/fixtures.bash`** 新增：
  - `detect_python()`（`command -v python3 || command -v python`，探测形态命中扫描器 R2 豁免集）+ 顶层 `export PYTHON`
  - `create_python_shim_bin()`：临时 bin + `python3` 包装器（内嵌真解释器绝对路径，探测时排除 `$BATS_TEST_TMPDIR` 避免自解析循环），返回 bin 路径
  - `export SHELLCHECK`（`command -v shellcheck || command -v shellcheck.exe`，BDD-25 配合 bdd-34 `${SHELLCHECK:-shellcheck}` 兜底）
- **10 个受影响 .bats 文件 setup() 注入 shim**（BDD-16/17，41 例 script-side 兜底）：check-state-transition / check-frontmatter / check-state-yaml / check-changelog / agate-debt-check / check-p6-provenance / check-retrospective / check-scope-resolved / check-tdd-red（9 个新增 setup），agate-inject-card（合并进既有 setup）

### 1.3 产品脚本 bc→awk（§2.8，BDD-24）
- **`agate/scripts/agate-extract-context.sh`** L128：`... | bc 2>/dev/null || echo 0 | tail -1` → `... | awk '{s+=$1} END{print s+0}'`（POSIX 工具，Windows Git Bash 自带；同时消除原管道优先级隐患）。EC.16（无 bc stub 下 `2+1=3` 求和）转绿

### 1.4 测试文件断言落实（§2.4-2.7，BDD-10~23/25/26）
- **24 文件测试侧裸 python3 → `$PYTHON`**（100 处，BDD-14；ci-gate-backstop 由 P3 已改）+ 全树 R2 零命中
- **check-tdd-red.bats**：PATH 硬编码 15 处移除（P3 已改 `env -u PATH` 等）+ 4 处样例文本 `# scan-exempt:`（P3 已改）+ 6 处 python3→`$PYTHON`（P4）
- **install-hook.bats**：2 处 `[[ -L ]]` 拆为 Linux 真软链（readlink 断言）+ Windows 复制模式（mock ln 用例，P3 已加）——见 [DESIGN_GAP]
- **integration/pre-push-hook.bats**：[SCOPE+] L11 `[ -L ]` 按平台分支（Linux readlink / Windows `[ -f ]`）
- **agate-next-card.bats / check-scope-resolved.bats**：`/tmp` 逻辑路径→`$BATS_TEST_TMPDIR`（P3 已改）；bdd-21 平台分支 setup（P3 已改）
- **ci-gate-backstop.bats**：文件级 `export PYTHONIOENCODING=utf-8`（setup）+ 新增 cp1252 模拟用例（BDD-23/26：①无 utf-8 导出时 UnicodeEncodeError 崩溃 ②文件级导出兜底不崩溃、中文关键词命中）+ CRLF 归一化（P3 已改）
- **新建 `agate/tests/unit/helpers-python.bats`**（BDD-13/15/17 新用例，任务 B）：detect_python 优先 python3 / PATH 仅 python 回退 / shim 下无 python3 环境非法回退仍 exit 1（不静默放行，对照 stub 失败时静默 exit 0）

### 1.5 CI（§2.9，BDD-7/27）
- **`.github/workflows/protocol-tests.yml`**：
  - 新增 `platform-scan` job：matrix `[ubuntu-latest, windows-latest]`，Linux 步骤 `bash agate/scripts/check-platform-assumptions.sh`（exit 1 阻断合并，BDD-7），Windows 步骤同命令（双平台等价证明，BDD-1）
  - `bats` job 改 matrix `[ubuntu-latest, windows-latest]`：Windows 分支 `defaults.run.shell: bash`、bats 用 curl tarball 安装（v1.11.0，**精确安装命令 P5 验证时定稿**，I7 supplementable）、各步 `PYTHONIOENCODING=utf-8`

### 1.6 测试计数同步（I10）
- **`agate/tests/README.md`**：计数表按 `count-tests.sh` 实际输出重排（含既有漂移修正：check-tdd-red 43 / ci-gate-backstop 11 / install-hook 6 / pre-push-hook 4 / agate-extract-context 16 / helpers-python 3 等），新增 helpers-python 行；`count-tests.sh` 总计 727（P3 起 723 + helpers-python 3 + cp1252 1），无漂移告警
- **`protocol-tests.yml`**：bats job 增加 `Run Scanner Behavior Tests` step（执行 check-platform-assumptions.bats，P4-review NEEDS-REV-1 修复）

## 2. 自查结果（自查≠P5 gate）

- `bash agate/scripts/check-platform-assumptions.sh`：exit 0，零命中（BDD-8 闭环）
- `bats agate/tests/scripts/check-platform-assumptions.bats`：14/14 绿
- 全量 `bats sanity+unit+regression+integration`：733/733 绿（727 count-tests + 6 sanity），not ok 0
- `python3 agate/scripts/check-protocol-consistency.py --strict`：0 ERROR 0 WARNING
- `shellcheck -S warning agate/scripts/*.sh`：0 error

## 3. 约束

- 未改协议语义与 gate 逻辑判定规则（P1 红线）；Linux 基线全程全绿（BDD-28）
- 测试侧裸 python3 全部改 `$PYTHON`（BDD-14）；产品脚本仅改 agate-extract-context.sh bc→awk + 新增扫描器（P1 §6 声明）
- 扫描器不接入本地 pre-commit（P1 SUGGEST-2）；count-tests.sh / consistency 逻辑未并入扫描器
- 本文件约束节无行首 `- PASS`/`- FAIL` 格式（provenance 预检合规）
- [PROD_NOT_TOUCHED]（开发全程在 worktree + `$BATS_TEST_TMPDIR`，未接触生产环境）

## 4. DESIGN_GAP / SCOPE+ 标注

```
[DESIGN_GAP: P2 §2.5 设计文本「Linux 真软链语义保留：现有 [[ -L "$repo/.git/hooks/pre-push" ]]」与 BDD-8（扫描器对修复后全树零命中，含 R3）+ P3 test_bdd_4（[[:space:]]\[+[[:space:]]+-L[[:space:]] 字面必须检出）冲突——`[[ -L ]]` 字面存在即被 R3 检出。实现改为：Linux 分支用 `readlink` 目标断言（真软链存在且指向 pre-push-gate.sh 的语义等价，readlink 对非软链返回空/失败），保留 BDD-18「Linux 断言软链语义」意图，同时满足 R3 零命中。]
```

```
[SCOPE+ 观察（非阻塞，供主 Agent 知悉）：P3 test_bdd_8 要求全树零命中，但 P2 §2.5 仅列 install-hook.bats 2 处 [[ -L ]]；P3 实测又发现 integration/pre-push-hook.bats L11 `[ -L ... ] || fail` 命中 R3（P2 [SCOPE+] 已声明）。P4 已按 §2.5 同类平台分支处理（Linux readlink / Windows [ -f ]），不属 P1 范围外新改动。]
```

## 5. 完成标准对照（P2 §4）

- [x] `check-platform-assumptions.sh` 存在，Linux 可跑，仅 POSIX 特性（BDD-1）
- [x] 扫描器行为测试 14 例通过（BDD-9，含 R1/R2/R3 不被 scan-exempt 豁免的负向用例）
- [x] 扫描器对修复后 `agate/tests/` 全树 0 命中（BDD-8）
- [x] 24 文件测试侧裸 python3 → `$PYTHON`（含 P3 已改 ci-gate-backstop = 25 文件，R2 零命中）
- [x] 10 个受影响 .bats 文件 setup 注入 shim（BDD-16），BDD-17 新用例验证不静默放行
- [x] check-tdd-red.bats 无 `PATH="/usr/bin:/bin"` 字面（BDD-10），TD.1b/TDD.F8 exit 语义不变（BDD-11/12）
- [x] install-hook.bats 软链（readlink）+ 复制模式两套用例通过（BDD-18/19）
- [x] 2 处逻辑 /tmp → `$BATS_TEST_TMPDIR`；4 处样例文本带标记且内容原样（BDD-20）
- [x] bdd-21 平台分支 setup（BDD-21）
- [x] CRLF 归一化 + PYTHONIOENCODING + cp1252 模拟用例（BDD-22/23）
- [x] agate-extract-context.sh L128 无 bc，无 bc 模拟求和正确（BDD-24，EC.16 绿）
- [x] env-adapt-docs.bats bdd-34 shellcheck 探测（BDD-25，fixtures 导出 SHELLCHECK）
- [x] protocol-tests.yml platform-scan job + bats job windows matrix（BDD-7/27；Windows 安装命令 P5 定稿，I7）
- [x] 全量 bats + consistency --strict + shellcheck 全绿（BDD-28）；tests/README 计数同步（I10）

## 6. 遗留（P5 验证关注）

- bats job Windows 分支的 bats 精确安装命令（curl tarball v1.11.0）未在本地验证（Linux 无法验证 Windows 安装步骤，属 I7 supplementable）；push 到 CI 后由 Windows 分支最终确认
- Windows CI 可能暴露的日志外不兼容用例（[SCOPE+] 观察）由 P5/后续处理
