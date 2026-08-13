---
phase: P2
task_id: TAG0009-tests-platform-neutral
type: design
parent: P1-requirements.md
trace_id: TAG0009-tests-platform-neutral-P2-20260813
status: draft
created: 2026-08-13
agent: architect
# ── v2.0 机器字段 ──
candidate_count: 2
packages: [agate-tests, agate-scripts, ci-workflow]
domains: [backend]
ui_affected: false
---

# P2 方案设计 — agate 测试套件平台无关化（TAG0009）

## 0. 影响域分析

### 改什么
- **新增产品脚本**：`agate/scripts/check-platform-assumptions.sh`（静态扫描器，bash+grep，自身平台无关）
- **产品脚本改动（仅 1 个，P1 BDD-24 在范围内）**：`agate/scripts/agate-extract-context.sh` L128 `bc` → `awk` 求和
- **测试 helper**：`agate/tests/helpers/fixtures.bash` 新增 `detect_python` / `create_python_shim_bin`
- **19 个测试文件批量修**（78 例失败所在）+ 1 个同类新增（见 [SCOPE+]）：
  - PATH 硬编码 15 处（check-tdd-red.bats）
  - 测试侧裸 python3 → `$PYTHON`（25 文件）
  - symlink 断言按平台分支（install-hook.bats 2 处 + integration/pre-push-hook.bats 1 处新增）
  - /tmp 逻辑路径 → `$BATS_TEST_TMPDIR`（agate-next-card.bats / check-scope-resolved.bats）
  - bdd-21 setup 平台无关化（agate-next-card.bats）
  - 输出归一化 + 编码（ci-gate-backstop.bats 等）
  - shellcheck 探测（env-adapt-docs.bats bdd-34）
  - 受影响 .bats 文件 setup 注入 harness shim（覆盖 41 例 script-side 失败）
- **CI**：`.github/workflows/protocol-tests.yml`（platform-scan job + bats job 增 windows-latest）

### 不改什么
- 其余 16 个产品脚本（harness shim 兜底，P1 scope_resolved 已声明）
- 协议语义、gate 逻辑判定规则（P1 §1 红线）
- 扫描器不接入本地 pre-commit（P1 SUGGEST-2）
- `count-tests.sh` / `check-protocol-consistency.py` 逻辑（扫描器独立成 job，不并入）

### 风险在哪
- Linux 基线是红线（P0 known_risks[0]）：每处修改必须 TDD 先红后绿（BDD-29）
- 扫描器模式集误报/漏报：已用真实代码树验证（见 minimal_validation），R2 命中 25 文件与 P1 §8 完全一致
- `/tmp` 样例文本 vs 逻辑路径无法纯 grep 区分：依赖 `# scan-exempt:` 行内标记机制
- Windows CI 是 supplementable：本地无法验证，bats job 增 windows 后的未知失败由 P5/后续处理（I7）

---

## 1. 候选方案（整体架构层）

### 候选 A：harness PATH shim + 静态扫描器 gate + 批量修测试（**选定**）
**做法**：
1. 测试侧裸 python3 全部改 `$PYTHON`（BDD-14）；
2. 产品脚本内裸 python3（41 例失败真因）由 fixtures 临时 bin 的 `python3` 包装器 shim 兜底（前置 PATH），**不改 17 个产品脚本**；
3. 新增 `check-platform-assumptions.sh` 扫 `agate/tests/` 全树，CI 阻断新假设；
4. 其余平台假设（PATH/symlink//tmp/bc/shellcheck/编码）逐个按平台无关构造修复。

**优点**：
- 一次覆盖 41 例 script-side 失败，零产品回归风险（产品脚本行为在 Linux 上完全不变，shim 只是让 `python3` 解析到真解释器）
- 扫描器 gate 让"同类扫描闭环"（BDD-8）真正成立，用户明确要求"不愿意一轮一轮来回改"
- 范围锁测试套件（P0-brief），产品层根治另立任务（P1 [SCOPE+] 观察 → TAG0010+）

**风险/工作量**：
- shim 依赖"产品脚本 `python3 ... 2>/dev/null || echo` 在 shim 下解析到真解释器"的关键假设 → **已最小验证 CONFIRMED**（见 §8）
- 需给 9 个受影响 .bats 文件加 setup 注入（每个文件 3 行）
- 纯 grep 无法 100% 区分样例文本与逻辑路径 → 需 `# scan-exempt:` 标记机制维护

### 候选 B：直接改 17 个产品脚本（python3 → 探测解释器）+ 不建 shim
**做法**：把 17 个产品脚本 68 处裸 `python3` 改为 `$({ command -v python3 || command -v python; })` 或统一探测变量。

**优点**：测试侧不需要 shim，产品脚本在真实 Windows 用户环境也一次性根治（顺便解决 P1 [SCOPE+] 观察）。

**缺点/风险**：
- 68 处改产品脚本 + 每处 `|| echo` 兜底语义要重验 → 改动面远超 78 例测试失败，Linux 回归风险高（红线）
- 超出 P0-brief 锁定的任务范围（范围 = 测试套件平台无关化）
- 产品脚本在 hooks 场景（pre-commit 等）的真实 Windows 部署属独立产品问题，与测试基建混做会让评审/验收边界模糊

**选择理由**：P1 SUGGEST-1 已定方向（候选 A），且关键假设已最小验证成立；候选 B 的真实 Windows 产品根治价值应作为独立任务（TAG0010+）推进，避免范围蔓延与 Linux 回归风险。**P1 scope_resolved 字段已声明本任务采用候选 A。**

> 各设计选型点内部的替代方案见 §2 逐点权衡。

---

## 2. 九个设计选型点

### 2.1 静态扫描器（BDD-1~9）

**位置/命名**：`agate/scripts/check-platform-assumptions.sh`（bash + POSIX ERE grep 实现；GNU 专用特性如 `-P` 禁用——MSYS2 的 grep 亦支持 ERE，保证 BDD-1 双平台行为一致）。

**扫描范围**：`agate/tests/` 全树——`unit/*.bats` `regression/*.bats` `integration/*.bats` `sanity.bats` `helpers/*.bash` `scripts/*.sh` `fixtures/**`。不含 `agate/scripts/`（产品脚本，本任务范围外；P1 SUGGEST-2）。

**模式集（5 组，正则已用真实代码树验证）**：

| 规则 | 模式（POSIX ERE） | 豁免 | 实测量 |
|------|-------------------|------|--------|
| R1 硬编码 PATH | `PATH=[^[:space:]]*(/usr\|/bin)` | 无 | 15 行（check-tdd-red.bats，与 P1 一致）|
| R2 命令位置裸 python3 | `(^\|[[:space:]]\|[=(\"'])python3([[:space:]]\|$)` | `command -v python3/python` 探测形态、`env python3`、shebang、行首 `@test` 标题、行首注释行 | 110 行 25 文件（行数与 P1 §8 的 25 文件一致；含引号前字符类，实测含 ci-gate-backstop 等）|
| R3 symlink 单平台断言 | `[[:space:]]\[+[[:space:]]+-L[[:space:]]` | 无（`[[ -f ]]` 等非 `-L` 不匹配）| 3 处（install-hook.bats 2 + **integration/pre-push-hook.bats 1 新增**，见 [SCOPE+]）|
| R4 `/tmp` 逻辑路径 | `/tmp([[:space:]]\|/\|"\|'\|$)` | `$BATS_TEST_TMPDIR`（变量名不含 `/tmp`，天然不命中）；**行含 `# scan-exempt:` 标记整行跳过** | 6 处（2 逻辑路径 + 4 样例文本）|
| R5 Unix-only 工具（bc 等） | `(^\|[[:space:]]\|[=\|(])bc([[:space:]]\|$\|\|)` | 无 | 0 处（tests/ 内无 bc；产品脚本 bc 属范围外）|

**规则语义要点**：
- **命令位置 vs 探测形态**（P1 I2）：R2 的豁免集显式列探测形态（`command -v python3` / `command -v python`），helper 自身不触发误报（已验证 fixtures 里探测行豁免生效）
- **逻辑路径 vs 样例文本**（P1 I9）：纯 grep 无法区分（`cd /tmp` 与 `imported from /tmp/test/...` 都是空格+`/tmp`），设计采用 **行内 `# scan-exempt:` 标记**作为样例文本的显式豁免通道（见 §2.6）；BDD-9 的干净 fixture 用 `$BATS_TEST_TMPDIR` 或样例文本不含 `/tmp` 构造，标记豁免行为单独用例覆盖
- **标记豁免边界**（P2-review 非阻塞建议，P3 落实）：`# scan-exempt:` 标记**只豁免 R4（/tmp）样例文本**，不豁免 R1/R2/R3 命中行——BDD-9 需补一条负向用例：对 R1/R2/R3 命中行追加 `# scan-exempt:` 标记，断言仍被检出（防标记通道被误用为"任意假设的白名单"）。实现侧扫描器逻辑：标记仅在 R4 判定分支生效，R1/R2/R3 不做行豁免

**阻断方式**（P1 SUGGEST-2）：新增 `platform-scan` job，matrix `[ubuntu-latest, windows-latest]`，Linux 步骤为阻断 gate（exit 1 即失败阻断合并，BDD-7）；Windows 步骤同时跑证明扫描器双平台等价（BDD-1）。

**集成点**：`protocol-tests.yml` 新增独立 job（**不并入** count-tests.sh / check-protocol-consistency.py——职责分离：count-tests 管用例数漂移、consistency 管协议文档一致性、扫描器管平台假设，三者互不依赖避免耦合）。

**范围扫描内自测**：`agate/tests/scripts/` 下的 `count-tests.sh` 无平台假设（已验证 0 命中）。

### 2.2 PYTHON 探测 helper（BDD-13/14/15）

**放置**：`fixtures.bash`（P1 SUGGEST-3，已确认 fixtures.bash 被 load.bash source，所有 .bats 首行 load 后即可用）。

**设计**：
```bash
# detect_python — 探测可用的 python 解释器（优先 python3，回退 python）
detect_python() {
    command -v python3 2>/dev/null || command -v python 2>/dev/null \
        || { echo "FATAL: 找不到 python3/python 解释器" >&2; return 1; }
}
export PYTHON="$(detect_python 2>/dev/null || true)"   # 顶层导出一次，全局默认
```
- `detect_python` 是函数：BDD-15 回退分支测试可 `(export PATH="仅含 python 的 bin:$PATH"; detect_python)` 重新探测并断言回退到 `python`
- 导出 `PYTHON`：测试引用 `$PYTHON` 无需重复探测；`run bash -c "... '$PYTHON' ..."` 中外层展开路径
- **自身不触发扫描器**：探测形态 `command -v python3` 命中 R2 豁免集（已验证）

**边界**：`PYTHON` 只替换测试侧命令位置调用；产品脚本内部 python3 由 shim 覆盖（§2.3），不混用。

### 2.3 script-side 裸 python3 41 例 → harness PATH shim（BDD-16/17）

**关键假设已最小验证 CONFIRMED**（见 §8）：无 python3 时 check-state-transition.sh 对非法 P4→P2 回退静默 exit 0（41 例根因复现）；注入 shim 后恢复 exit 1。

**shim 具体设计**（fixtures.bash 新增 `create_python_shim_bin`）：
```bash
# create_python_shim_bin — 建临时 bin 目录 + python3 包装器指向真解释器（BDD-16/17）
# 返回 bin 路径；调用方前置到 PATH
create_python_shim_bin() {
    # 探测时排除自身 shim bin，避免自解析循环（包装器内嵌绝对路径）
    local clean_path
    clean_path=$(printf '%s' "$PATH" | tr ':' '\n' | grep -vF "$BATS_TEST_TMPDIR" | paste -sd:)
    local real_py
    real_py=$(PATH="$clean_path" command -v python3 2>/dev/null || PATH="$clean_path" command -v python 2>/dev/null)
    [ -n "$real_py" ] || { echo "FATAL: 找不到 python3/python" >&2; return 1; }
    local bin
    bin=$(mktemp -d "$BATS_TEST_TMPDIR/shim-bin-XXXXXX")
    printf '#!/usr/bin/env bash\nexec "%s" "$@"\n' "$real_py" > "$bin/python3"
    chmod +x "$bin/python3"
    echo "$bin"
}
```
- **注入点**：9 个受影响 .bats 文件（check-state-transition / check-frontmatter / check-state-yaml / check-changelog / agate-debt-check / check-p6-provenance / check-retrospective / check-scope-resolved / agate-inject-card，外加 check-tdd-red.bats——其被测脚本 check-tdd-red.sh 内部 L62-194 有 12 处 python3）的文件级 `setup()` 注入：
  ```bash
  setup() {
      local shim; shim=$(create_python_shim_bin) || return 1
      export PATH="$shim:$PATH"
  }
  ```
- **为什么包装器内嵌绝对路径**：避免 `command -v python3` 在 shim 前置 PATH 后解析到自己（自解析循环）；`real_py` 在排除 `$BATS_TEST_TMPDIR` 的 PATH 下探测
- **为什么 Linux 行为不劣化（BDD-17）**：Linux 上 `python3` 原本即解析到真解释器，shim 只是多一次 exec 转发，行为等价；shim 命中 R2 豁免？——不，shim 内容 `exec "/usr/bin/python3" "$@"` 在 tests/ 下（fixtures.bash 内嵌 heredoc），R2 扫的是 .bats/.bash/.sh 文件中的字面 `python3`——fixtures.bash 里 `create_python_shim_bin` 的 `printf '...exec "%s" "$@"...'` 用 `%s` 占位不出现字面 `python3`，且 R2 豁免 `command -v python3` 探测行；需 P4 确认 fixtures.bash 中无命令位置字面 `python3`（探测形态除外）

### 2.4 PATH 硬编码 15 处（BDD-10/11/12）

- **TD.1b（L48-51）/ TDD.F8（L380-383）**「PATH 无 python」场景：改平台无关构造——**`env -u PATH`**（清除 PATH，不硬编码 Unix 路径；与 `env -i PATH="/usr/bin:/bin"` 等价，实测 exit 3），不再覆盖 PATH。exit 语义保持：TD.1b 期望 `3 or 1`、TDD.F8 期望 `3`（BDD-11/12）。`TEST_RUNNER` 指向不存在路径（→ exit 1，A-class）的既有语义由 TD.1 单独覆盖，勿重复造
- **TDD.G/F 系列（L164/227/245/260/279/296/315/333/351/367/404/435/451，13 处）**：这些用例已用 `-u TEST_RUNNER` + fake runner + TASK_DIR 构造，`PATH="/usr/bin:/bin"` 仅作"环境净化"（防止系统 pytest 被 PATH 命中）——**全部移除 PATH 覆盖**（fake runner 通过 TEST_RUNNER/TASK_DIR 绝对路径指定，不依赖 PATH；不覆盖 PATH 不会命中系统 pytest，因为 TEST_RUNNER 优先）
- BDD-10 验收：全文件 grep 字面 `PATH="/usr/bin:/bin"` 为 0

### 2.5 symlink 平台分支（BDD-18/19 + [SCOPE+]）

- **install-hook.bats L22-28 / L30-41** 两处 `[[ -L ]]` 断言拆分为两层用例：
  1. Linux 真软链语义保留：现有 `[[ -L "$repo/.git/hooks/pre-push" ]]` + `readlink` 指向 `pre-push-gate.sh`（BDD-18 前半）
  2. Windows 复制模式分支：复用 L43 mock 先例（fakebin `ln` → `cp -f`）跑 install-hook.sh，断言输出含 `复制`/`需重跑` 且**不**断言 `-L`（BDD-18 后半 + BDD-19）
- 分支语义：两套用例都在 Linux 上跑（真实软链 + mock ln），即"Linux 全量覆盖 Windows 分支"（BDD-26）
- **[SCOPE+] 同类新增**：`integration/pre-push-hook.bats` L11 `[ -L ... ] || fail "pre-push 应为软链"`（R3 实测命中但 P1 未列）——同样按平台分支处理（Linux 断言软链 / 复制模式断言输出 WARNING 语义），归 BDD-8 同类扫描闭环，不改 P1 范围（tests 包内）

### 2.6 /tmp 与 Windows 路径（BDD-20/21）

- **逻辑路径替换**（R4 实测 2 处）：
  - `agate-next-card.bats` L104 `cd /tmp` → `cd "$BATS_TEST_TMPDIR"`（该用例仅需一个可 cd 目录验证 AGATE_ROOT 解析，`$BATS_TEST_TMPDIR` 满足）
  - `check-scope-resolved.bats` L8 `dir="/tmp/nonexistent-..."` → `dir="$BATS_TEST_TMPDIR/nonexistent-..."`（不创建即构造不存在路径，语义不变）
- **样例文本豁免**（R4 实测 4 处）：`check-tdd-red.bats` L139/148、`check-tdd-red-formatter.bats` L97/105 的 vitest mock 输出字符串——**内容不动**（断言依赖原样），行尾追加 `# scan-exempt: mock 输出样例文本（非路径假设）` 标记，扫描器整行豁免（机制已验证，见 §8）
- **BDD-21 setup 精确方式**（agate-next-card.bats L186-195）：当前 `mkdir -p "$dir/C:\\proj\\agate/phase-cards"` 在 Windows 上反斜杠即分隔符、setup 失效。改造为平台分支构造：
  ```bash
  # Linux：字面反斜杠目录名模拟 Windows 风格 AGATE_ROOT
  # Windows：反斜杠即分隔符，直接用正斜杠路径
  local root_agate
  if [[ "$(uname -s)" == *MINGW* || "$(uname -s)" == *MSYS* ]]; then
      root_agate='C:/proj/agate'
  else
      root_agate='C:\proj\agate'
  fi
  mkdir -p "$BATS_TEST_TMPDIR/$root_agate/phase-cards"
  cp "$AGATE_ROOT/phase-cards/P3-tdd.md" "$BATS_TEST_TMPDIR/$root_agate/phase-cards/"
  run bash -c "cd '$BATS_TEST_TMPDIR' && AGATE_ROOT='$root_agate' bash '$AGATE_SCRIPTS/agate-next-card.sh' P3"
  [[ "$output" == *"路径：phase-cards/P3-tdd.md"* ]]
  ```
  双平台断言同一输出串，Linux 行为不变（BDD-21 后半）。

### 2.7 输出/编码（BDD-22/23）

- **CRLF 归一化**（P1 SUGGEST-5）：ci-gate-backstop.bats 等行尾敏感断言，匹配前 `output=$(printf '%s' "$output" | tr -d '\r')`；`tr` 为 POSIX 工具双平台可用。涉及文件：ci-gate-backstop.bats（7 例相关）
- **编码显式化**（复用 CI 既有 `PYTHONIOENCODING=utf-8` 模式）：调用含中文输出 python 工具的测试文件级 `export PYTHONIOENCODING=utf-8`（setup 层），保证中文关键词（真红灯/绿灯/SKIP）断言命中（BDD-23 前半）
- **cp1252 模拟用例**（BDD-23 后半 + BDD-26）：新增/改造一个用例，`PYTHONIOENCODING=cp1252` 下运行受影响工具，断言"脚本正常结束、不 UnicodeEncodeError 崩溃"且（若 cp1252 无法表示中文）输出经归一化后断言语义等价——模拟 Windows 默认代码页

### 2.8 外部工具（BDD-24/25）

- **BDD-24 agate-extract-context.sh L128 `bc` → `awk`**（唯一产品脚本改动，P1 在范围内）：
  ```bash
  # 原：failed="$(grep -rh '^\s*failed:' ... | grep -oE '[0-9]+' | paste -sd+ 2>/dev/null | bc 2>/dev/null || echo 0 | tail -1)"
  # 改：failed="$(grep -rh '^\s*failed:' "$task_dir/P5-test-results/" 2>/dev/null | grep -oE '[0-9]+' | awk '{s+=$1} END{print s+0}')"
  ```
  `awk` 是 POSIX 标准工具，Windows Git Bash / MSYS2 自带；同时消除原 `bc 2>/dev/null || echo 0 | tail -1` 的管道优先级隐患（`||` 绑定 `bc`、`| tail -1` 绑 `echo 0`）。验证用例：agate-extract-context.bats L78-86（单值 `1`）、L198-205（多文件求和 `2+1=3`）在无 bc 模拟环境（PATH 剔除 bc）下仍求和正确（BDD-24 + BDD-26）
- **BDD-25 env-adapt-docs.bats bdd-34（L53-56）**：`shellcheck -S warning` → 探测 `SHELLCHECK="$(command -v shellcheck || command -v shellcheck.exe)"`，调用 `${SHELLCHECK:-shellcheck} -S warning "$AGATE_ROOT"/scripts/*.sh`；glob 引号统一用 `"$AGATE_ROOT"/scripts/*.sh`（bash 展开 glob，Git Bash 双平台一致）

### 2.9 Windows bats CI（BDD-27）

- **复用既有 windows matrix 模式**（shellcheck/consistency/gate-backstop 三个 job 已用：`runs-on: ${{ matrix.os }}` + `if: runner.os == 'Windows'` + `python` + `PYTHONIOENCODING=utf-8`）
- **bats job 改 matrix**：`os: [ubuntu-latest, windows-latest]`；Windows 分支：
  - `defaults.run.shell: bash`
  - 装 bats：下载 bats-core 发布包（`curl` tarball + `install.sh` 安装到 PATH）或 choco；**精确安装命令 P5 验证时定稿**（本地 Linux 无法验证安装步骤，属 I7 supplementable）
  - 跑测试：`bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/`，`env: PYTHONIOENCODING: utf-8`，setup-python 用 `python` 命令
- 验收：push/PR 触发，Windows 分支 0 失败（BDD-27）；P5 本地只能确认 Linux 全绿，Windows 结果由 CI 最终确认（I7）

---

## 3. BDD 覆盖映射（29 条全覆盖）

| BDD | 落实点 |
|-----|--------|
| 1 | §2.1 扫描器自身平台无关（POSIX ERE，无 GNU 专用特性）+ platform-scan job matrix 双平台跑 |
| 2 | §2.1 R1 硬编码 PATH 检出→exit 1 |
| 3 | §2.1 R2 命令位置裸 python3（豁免探测形态）→exit 1 |
| 4 | §2.1 R3 `[[ -L ]]`/`[ -L ]` 检出→exit 1 |
| 5 | §2.1 R4 `/tmp` 逻辑路径检出（`$BATS_TEST_TMPDIR` 与 `# scan-exempt:` 行豁免）|
| 6 | §2.1 R5 `bc` 等 Unix-only 工具检出，模式集可扩充（seq/timeout 等）|
| 7 | §2.1 platform-scan job（Linux 步骤 exit 1 阻断）|
| 8 | §2.1 修复后全树扫描 0 命中（§2 各修复点 + [SCOPE+] pre-push-hook L11）|
| 9 | `agate/tests/scripts/check-platform-assumptions.bats` 行为测试：含假设 fixture→非零+报告模式；干净 fixture→零；负向用例：`# scan-exempt:` 标记只豁免 R4（/tmp）样例文本，不豁免 R1/R2/R3（P2-review 建议）|
| 10 | §2.4 移除 15 处 `PATH="/usr/bin:/bin"`，grep 字面为 0 |
| 11 | §2.4 TD.1b/TDD.F8 改 `env -u PATH` 构造，exit 3/1 语义不变（TEST_RUNNER 不存在路径→exit 1 由 TD.1 覆盖）|
| 12 | §2.4 全量通过 + 红绿灯语义不变（P5 回归）|
| 13 | §2.2 detect_python + PYTHON 导出，helper 平台无关、探测形态豁免 |
| 14 | §2.2 25 文件测试侧裸 python3 → `$PYTHON`，全树 R2 零命中 |
| 15 | §2.2 回退分支（PATH 仅 python 无 python3）Linux 模拟用例 |
| 16 | §2.3 harness shim（已最小验证 CONFIRMED），41 例 script-side 转绿 |
| 17 | §2.3 shim 下 Linux 行为不劣化（无 python3 模拟对比，已验证恢复拦截）|
| 18 | §2.5 install-hook.bats Linux 断言软链 + 复制模式断言 WARNING |
| 19 | §2.5 mock ln 复制模式（L43 先例复用）Linux 模拟覆盖 |
| 20 | §2.6 逻辑路径→`$BATS_TEST_TMPDIR`；样例文本标记豁免 |
| 21 | §2.6 bdd-21 setup 平台分支构造，双平台断言同串 |
| 22 | §2.7 `tr -d '\r'` 归一化，CRLF 模拟输出下断言命中 |
| 23 | §2.7 PYTHONIOENCODING 显式设置 + cp1252 模拟用例 |
| 24 | §2.8 agate-extract-context.sh bc→awk，无 bc 模拟下求和正确 |
| 25 | §2.8 shellcheck/shellcheck.exe 探测，双平台调用一致 |
| 26 | §2.5/2.6/2.7/2.8 各 Windows 分支（ln 复制/反斜杠路径/CRLF/cp1252/无 bc/无 python3/无 shellcheck 名）均有 Linux 显式模拟用例 |
| 27 | §2.9 bats job 增 windows-latest（matrix），CI 最终确认 0 失败 |
| 28 | §4 gate_commands.P5 全量 bats + consistency --strict + shellcheck 全程全绿 |
| 29 | 每处修复先加平台无关失败测试确认红再改（AGENTS.md 工作流）|

---

## 4. 完成标准（实现完成的标志）

- [ ] `check-platform-assumptions.sh` 存在，自身在 Linux + MSYS2 可跑且行为一致（BDD-1）
- [ ] `agate/tests/scripts/check-platform-assumptions.bats` 行为测试通过（BDD-9，含 R1/R2/R3 不被 scan-exempt 标记豁免的负向用例）
- [ ] 扫描器对修复后 `agate/tests/` 全树运行 0 命中（BDD-8）
- [ ] 25 文件测试侧裸 python3 全部 `$PYTHON`（R2 零命中）
- [ ] 9 个受影响 .bats 文件 setup 注入 shim，41 例 script-side 相关用例转绿（BDD-16）
- [ ] check-tdd-red.bats 无 `PATH="/usr/bin:/bin"` 字面（BDD-10），TD.1b/TDD.F8 exit 语义不变（BDD-11/12）
- [ ] install-hook.bats 软链 + 复制模式两套用例通过（BDD-18/19）
- [ ] `$BATS_TEST_TMPDIR` 替换 2 处逻辑 /tmp；4 处样例文本带标记且内容原样（BDD-20）
- [ ] bdd-21 平台分支 setup 双平台可构造断言（BDD-21）
- [ ] CRLF 归一化 + PYTHONIOENCODING + cp1252 模拟用例（BDD-22/23）
- [ ] agate-extract-context.sh L128 无 `bc`，无 bc 模拟求和正确（BDD-24）
- [ ] env-adapt-docs.bats bdd-34 shellcheck 探测（BDD-25）
- [ ] protocol-tests.yml platform-scan job + bats job windows matrix（BDD-7/27）
- [ ] 全量 bats + consistency --strict + shellcheck 全绿（BDD-28）；tests/README 用例数同步（I10，count-tests.sh 无漂移告警）

---

## 5. gate_commands（P2 固化，后续阶段不可改）

```yaml
gate_commands:
  P3: "bats"
  P5: "bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/ && python3 agate/scripts/check-protocol-consistency.py --strict && shellcheck -S warning agate/scripts/*.sh && bash agate/scripts/check-platform-assumptions.sh"
```

P5 子命令分解（供验证者逐项核对）：
| 子命令 | 验证目标 |
|--------|---------|
| `bats sanity+unit+regression+integration` | 全量回归基线（BDD-28）+ 各修复用例 |
| `python3 agate/scripts/check-protocol-consistency.py --strict` | 协议一致性 0 ERROR（BDD-28）|
| `shellcheck -S warning agate/scripts/*.sh` | 产品脚本 shellcheck 0 error（BDD-28）|
| `bash agate/scripts/check-platform-assumptions.sh` | 扫描器对全树 0 命中（BDD-8 闭环）|

> P3 说明：`P3: "bats"` 配合 `TEST_RUNNER="bats <具体修复文件>"` 由 check-tdd-red.sh 逐文件做 TDD 红灯确认（AGENTS.md「改脚本的工作流」）；BDD-11 的 exit 3 语义由 check-tdd-red.sh 自身测试（TD.1b/TDD.F8 用 `env -u PATH` 构造）覆盖，不依赖本命令。

---

## 6. files_to_read（P4 implementer 上下文地图）

```yaml
files_to_read:
  - path: agate/tests/helpers/fixtures.bash
    why: 新增 detect_python / create_python_shim_bin 的挂载点；复用 add_frontmatter_field 等既有模式
  - path: agate/tests/helpers/load.bash:40-44
    why: 确认 fixtures.bash 被 source 的顺序与位置
  - path: agate/tests/unit/check-tdd-red.bats:43-51,153-459,476-555
    why: TD.1b/TDD.F8 的 PATH 场景 + TDD.G/F 系列 13 处 PATH 覆盖移除 + PYX 测试侧 python3→$PYTHON
  - path: agate/tests/unit/install-hook.bats:22-65
    why: "[[ -L ]] 2 处平台分支 + L43 ln mock 先例（复制模式）"
  - path: agate/tests/integration/pre-push-hook.bats:11
    why: [SCOPE+] 第 3 处 symlink 断言平台分支
  - path: agate/tests/unit/agate-next-card.bats:102-106,184-201
    why: cd /tmp 替换 + bdd-21 setup 平台分支
  - path: agate/tests/unit/check-scope-resolved.bats:7-12
    why: /tmp/nonexistent 逻辑路径替换
  - path: agate/tests/unit/check-tdd-red.bats:139,148 + agate/tests/unit/check-tdd-red-formatter.bats:95-109
    why: 4 处 /tmp 样例文本加 # scan-exempt: 标记（内容原样）
  - path: agate/tests/unit/ci-gate-backstop.bats:54-190
    why: 7 例 python3→$PYTHON + 中文关键词断言 CRLF 归一化 + PYTHONIOENCODING
  - path: agate/tests/unit/env-adapt-docs.bats:48-61
    why: bdd-33/34：windows-latest 断言 + shellcheck 探测
  - path: agate/tests/unit/agate-extract-context.bats:78-86,198-205
    why: P5 failed 求和断言（bc→awk 后求和正确性）
  - path: agate/scripts/agate-extract-context.sh:126-130
    why: 唯一产品脚本改动（bc→awk）
  - path: agate/scripts/check-state-transition.sh:36,41,78
    why: shim 覆盖的 script-side python3 样例（其余 8 个产品脚本同型）
  - path: agate/scripts/check-platform-assumptions.sh
    why: 新增扫描器本体（P4 新建，模式集见 §2.1）
  - path: agate/tests/scripts/check-platform-assumptions.bats
    why: 新增扫描器行为测试（BDD-9，TDD 目标）
  - path: .github/workflows/protocol-tests.yml:5-33,34-61
    why: bats job 改 windows matrix + 复用 shellcheck/consistency 的 windows 模板；新增 platform-scan job
  - path: agate/tests/README.md + agate/tests/scripts/count-tests.sh
    why: 用例数同步约定（I10）与漂移检查
```

---

## 7. env_constraints（确认/细化 P0-brief）

```yaml
env_constraints:
  debug_env: "本环境为 Linux（UTF-8 locale）；Windows 分支用模拟环境覆盖：PYTHONIOENCODING=cp1252（编码）、fakebin ln→cp（symlink 复制模式）、纯净 PATH 无 python3（探测回退/无 bc）、SHELLCHECK 探测缺失（工具名）"
  isolation_check: "P5 gate 全部在本地 Linux 执行（全量 bats + consistency --strict + shellcheck + 扫描器零检出），全程不接触生产环境；Windows 真机仅由 GitHub Actions windows-latest CI 最终确认（supplementable，I7）"
```

---

## 8. minimal_validation（两个关键假设均已实测）

```yaml
minimal_validation:
  - assumption: "harness PATH shim 能让产品脚本内部裸 python3 在'仅 python 可解析'环境解析到真解释器（BDD-16/17 关键假设）"
    method: "临时 bin 放 python3 包装器（内嵌真解释器绝对路径 exec），前置 PATH 跑 check-state-transition.sh，并对比无 python3 环境"
    result: "confirmed"
    note: |
      ① shim 命中验证：含暂存变更（P4→P5）的 .state.yaml 下跑 check-state-transition.sh，shim 日志显示 3 次 python3 调用
      （phase_stdin/phase/retries_over）全部经 shim 解析到 /usr/bin/python3，exit 0（合法转移）；
      ② 根因复现：构造"核心工具齐全但无 python3"的纯净 PATH，对非法 P4→P2 回退跑脚本 → 静默 exit 0
      （与 P1 I1 分析的 41 例根因一致：python3 失败 → 读不到 phase → case \"\" 早退）；
      ③ shim 恢复：同一纯净 PATH 前置 shim → 正确 exit 1（回退跳变 ≥2 拦截）。
      结论：shim 方案成立，包装器必须内嵌绝对路径（避免 command -v 自解析循环）。
  - assumption: "扫描器模式集（R1-R5）能检出 Unix 假设且不误伤探测形态/样例文本（BDD-2~6,8,9）"
    method: "构造 dirty/clean fixture + 对真实 agate/tests/ 全树实测规则命中"
    result: "confirmed"
    note: |
      真实树实测：R1=15 行（与 check-tdd-red.bats 15 处 PATH 一致）；R2=110 行 25 文件（与 P1 §8 的 25 文件
      清单逐文件一致，行数 110 为含引号前字符类的实测口径——P2 修订后与 §2.1 表格一致）；R3=3 处（install-hook 2 + pre-push-hook 1 新增）；R4=6 处（2 逻辑路径 + 4 样例文本，
      样例文本需 # scan-exempt: 标记豁免——已验证标记行跳过、无标记行检出）；R5=0（tests/ 无 bc）。
      豁免验证：command -v python3 探测行、@test 标题行、注释行均不误报；[[ -L ]] 与 [ -L ] 双形式均可检。
      经验教训：R2 前字符类必须含引号（bash -c \"python3 ...\" 形式），否则漏检 ci-gate-backstop 等 7 例。
      修订记录：P2 修订轮按 P2-review 修正 R2 正则（全角 `）` 笔误→半角 `)` 且前字符类含引号），实测
      110 行 25 文件，消除与 §2.1 表格/§8 经验教训的计数矛盾。
  - assumption: "其余修复（$PYTHON 替换/PATH 构造/symlink mock//tmp 替换/bc→awk/PYTHONIOENCODING/shellcheck 探测）为纯代码逻辑"
    method: "依赖内部函数与数据转换：fixtures.bash helpers（create_task_dir 等既有）、bats run/assert 机制、POSIX 工具（awk/tr/grep）"
    result: "not_needed"
    note: |
      纯代码逻辑，无外部系统依赖。bc→awk 依赖 awk 在 Windows Git Bash 可用（POSIX 标准工具，MSYS2 自带）；
      awk 求和逻辑（s+=$1; END{print s+0}）在 P5 用无 bc 模拟环境回归验证。
```

---

## 9. [SCOPE+] 观察

```
[SCOPE+] 发现：integration/pre-push-hook.bats L11 存在 `[ -L "$repo/.git/hooks/pre-push" ] || fail "pre-push 应为软链"`
          （R3 扫描实测命中，P1 §8 同类扫描清单仅列 install-hook.bats 2 处）
          必须做的理由：属 BDD-8「同类扫描闭环」范畴——扫描器要求修复后全树零命中，该断言在 Windows
          复制模式下恒假，不修则扫描器 gate 与 Windows CI 双失败
          影响：不改 P1 范围（tests 包内新增 1 个平台分支修复点，同 §2.5 处理）；packages: [agate-tests]
```

```
[SCOPE+] 观察（非阻塞，供主 Agent 知悉）：bats job 增 windows-latest 后可能暴露日志外的其他 Windows
          不兼容用例（/tmp/bats-win-fail.log 仅记录 PR #127 一次运行）。设计已按"扫描器零命中 + 全平台分支
          模拟覆盖"尽最大可能闭环；若 CI 暴露新失败，属 I7 supplementable 范畴，由 P5/后续处理。
```

```
[SCOPE+] 观察（非阻塞）：产品脚本 17 文件 68 处裸 python3 在真实 Windows 用户环境的根治（探测 python3|python）
          建议另立任务（TAG0010+），本任务 harness shim 仅覆盖测试场景（P1 scope_resolved 已声明）。
```

---

*约束节行首无 `- PASS`/`- FAIL` 格式（provenance 预检合规）。*
