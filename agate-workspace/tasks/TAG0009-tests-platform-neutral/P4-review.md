---
phase: P4
task_id: TAG0009-tests-platform-neutral
type: review
parent: P4-implementation.md
trace_id: TAG0009-tests-platform-neutral-P4-20260813
status: approved
created: 2026-08-13
agent: review
---

# P4 实现评审 — TAG0009 测试套件平台无关化

> 评审方式：读 dispatch-context / P4-implementation / P2-design / P1-requirements / P3-test-cases + 直接读改动文件 + 实测复核（扫描器树扫描、14 例行为测试、helpers-python、consistency --strict、bc→awk 空/多文件求和）。

## 结论

**status: approved**

- 2 项必修（NEEDS-REV-1/2）已由主 Agent 修复：扫描器行为测试已接入 CI bats job（Run Scanner Behavior Tests step）+ README 计数 10→11 修正。
- 无 CRITICAL 数据安全/正确性问题；[DESIGN_GAP]（readlink 替代 `[[ -L ]]`）判为合理，批准。
- bc→awk 经实测复核**正确**（空目录→`0`、多文件→`3`，均 exit 0）。

---

## 一、必须修订项（已修复）

### [NEEDS-REV-1] BDD-9 扫描器行为测试未接入 CI / P5 gate → 已修复
- **修复**：`protocol-tests.yml` bats job 增加 `Run Scanner Behavior Tests` step（`bats agate/tests/scripts/check-platform-assumptions.bats`，配 PYTHONIOENCODING=utf-8）。
- gate_commands.P5 已 P2 固化不可改，落地在 CI——与 P2-design §2.1「platform-scan job + 职责分离」一致。

### [NEEDS-REV-2] README 计数漂移（I10）→ 已修复
- **修复**：`agate/tests/README.md:45` ci-gate-backstop 10→11；P4-implementation.md §1.6 同步修正。

---

## 二、已批准项

### [DESIGN_GAP] install-hook.bats Linux 分支 readlink 替代 `[[ -L ]]` — 批准

- 依据充分：P2 §2.5 设计文本本就写明 Linux 分支「`readlink` 指向 pre-push-gate.sh」（P2-design.md:174）；BDD-4（R3 检出 `[[ -L ]]` 字面）+ BDD-8（全树零命中）与字面 `[[ -L ]]` 冲突，readlink 是唯一同时满足两者的表达。
- 语义等价：readlink 对非软链返回空/失败，`[[ "$(readlink ...)" == ... ]]`（`agate/tests/unit/install-hook.bats:31,47`）仍能检出「非软链」失败态，BDD-18「Linux 断言软链语义」意图保留；Windows 复制模式由 mock ln 用例覆盖（`:52-75,77-101`）。
- 实测：install-hook.bats 现无任何 R3 命中（全树扫描 exit 0 佐证）；integration/pre-push-hook.bats:13-17 同构处理正确。

---

## 三、核验通过项（锚点 + 实测）

### 3.1 扫描器正确性（评审重点 1）— 通过

- R1-R5 模式与豁免：`agate/scripts/check-platform-assumptions.sh:28-32`（POSIX ERE，无 GNU `-P`）；R2 豁免集 `command -v python3/python`、`env python3`、行首 `#`/`@test`（`:43-55`）与设计 §2.1 一致。
- `# scan-exempt:` 只豁免 R4：豁免逻辑仅在 R4 分支生效（`:70`，`scan_rule R4 ... r4` 于 `:82`），负向 3 用例（R1/R2/R3 带标记仍被检出）实测绿（`check-platform-assumptions.bats:198-227`）。
- BDD-8 零命中：实测 `bash agate/scripts/check-platform-assumptions.sh` 全树 exit 0 无输出（闭环成立，含 helpers-python.bats、fixtures.bash 自净）。
- 不存在 target：`exit 2`（`:96-98`），与命中 exit 1 区分，符合契约（`check-platform-assumptions.bats:6-17`）。
- 自身 POSIX 兼容：`grep -nE/-vF/sed/find/paste/printf` 均 POSIX 工具；bash 特性（`set -uo pipefail`、`<<<`）为 MSYS2 自带，BDD-1 满足。
- consistency 锚点：`check-protocol-consistency.py:670-675`（关键词「平台假设/R1/R2」与扫描器内容匹配），实测 `--strict` 0 ERROR 0 WARNING。

### 3.2 harness shim（评审重点 2）— 通过

- 自解析循环规避：`create_python_shim_bin` 探测时剔除 `$BATS_TEST_TMPDIR` 段 PATH（`agate/tests/helpers/fixtures.bash:23-25`）+ 包装器内嵌绝对路径（`:29`），成立。
- 注入完整性：10 个 .bats 文件含 `create_python_shim_bin`（check-state-transition / check-frontmatter / check-state-yaml / check-changelog / agate-debt-check / check-p6-provenance / check-retrospective / check-scope-resolved / check-tdd-red + agate-inject-card 合并进既有 setup），与 P4-implementation §1.2 声明一致。
- BDD-17 真验证：`agate/tests/unit/helpers-python.bats:34-70` 构造 exit-127 stub——无 shim 时非法 P4→P2 回退静默 exit 0（41 例根因复现），有 shim 时正确 exit 1（不静默放行），断言为真行为非注释。实测 3/3 绿。
- 自身零 R2 命中：fixtures.bash 内 `"$bin/python3"`（`/python3"` 前字符 `/` 不在 R2 前导类）不触发，探测行走豁免集。

### 3.3 bc→awk（评审重点 3）— 通过（含回归疑点排除）

- `agate/scripts/agate-extract-context.sh:128` 新行 `... | awk '{s+=$1} END{print s+0}'`：
  - 空目录 / 目录内无 `failed:` 行 → 实测输出 `P5 failed 参考: 0`，exit 0。
  - 多文件 `failed: 2` + `failed: 1` → 实测输出 `P5 failed 参考: 3`，exit 0。
  - 已消除原 `bc 2>/dev/null || echo 0 | tail -1` 的管道优先级隐患（P2-design.md:215）；`2>/dev/null` 保留在 grep 层（提取上下文为 `P6` 段、`if [ -d P5-test-results ]` 保护）。

### 3.4 测试断言修改（评审重点 5）— 通过（P3 契约未篡改）

- `agate/tests/scripts/check-platform-assumptions.bats` 为 P3 commit `a3fd64f` 交付后 P4 未改动（git log 单 commit），14 用例为 P3 原样；P4 仅新建扫描器使其转绿——纯 TDD。
- 其余改动均为 P4 声明范围内的「新增 setup/shim + `python3`→`$PYTHON` + 平台分支」，既有断言（exit 码/输出匹配）未被弱化（抽查 check-tdd-red.bats:493-565、ci-gate-backstop.bats:60-230）。
- cp1252 用例真实性：`ci-gate-backstop.bats:207-230` ① `PYTHONIOENCODING=cp1252` 下断言 `UnicodeEncodeError` 崩溃（编码风险源实证）② 文件级 `export PYTHONIOENCODING=utf-8`（`:10`）下不崩溃且中文关键词命中——真实可执行。
- CRLF 归一化：`tr -d '\r'` 覆盖 5 处既有断言 + 新用例（`:72,88,105,139,201,227`）。
- PATH 构造：check-tdd-red.bats 现无 `PATH="/usr/bin:/bin"` 字面（实测 0），TD.1b/TDD.F8 用 `env -u PATH`（`:56,388`）；4 处样例文本带 `# scan-exempt:` 且内容原样（`check-tdd-red.bats:146,155`、`check-tdd-red-formatter.bats:97,105`）。

### 3.5 CI（评审重点 6）— 通过（标注诚实）

- `platform-scan` job matrix 双平台、Linux 阻断 / Windows 等价证明（`.github/workflows/protocol-tests.yml:54-71`）满足 BDD-7/BDD-1。
- `bats` job windows matrix + `defaults.run.shell: bash` + 各步 `PYTHONIOENCODING=utf-8`（`:6-52`）；Windows bats 精确安装命令标注「P5 验证时定稿，I7 supplementable」（P4-implementation.md §6），诚实无虚报。

### 3.6 脚本健壮性（评审重点 7）— 通过

- 扫描器 `grep -nE ... || true` 防 set -e 空匹配中断（`check-platform-assumptions.sh:61`）；`find`/target 存在性先判（`:88-98`）。
- 全量自查基线（P4-implementation §2）：733 bats / consistency --strict 0 ERROR / shellcheck 0 error，其中扫描器行为测试与 helpers-python 已由本评审实测复绿；`count-tests.sh` 总计 727 与 P4 声明一致。

---

## 四、非阻塞观察（供主 Agent / 后续任务参考）

- **O1**：R1 正则 `PATH=[^[:space:]]*(/usr|/bin)` 会误伤 `PATH="$PREFIX/bin"` 这类平台无关写法（`[^[:space:]]*` 回溯到 `/bin` 即命中）。当前树零命中，属低概率；后续模式集演进可考虑收紧（如 `=/usr`、`=/bin` 字面锚定）。
- **O2**：Windows bats job 将全量执行未加 shim 的测试文件（check-gate.bats→check-gate.sh、pre-commit-hook.bats→pre-commit-gate.sh、check-pruning/agate-retreat-to/gate-result 等产品脚本内部裸 `python3` 多带 `2>/dev/null || echo ""` 兜底）——Windows 上这些调用将静默空值化，断言是否仍成立未知。属 P2 [SCOPE+] #2 已声明、I7 supplementable 的已知风险；BDD-27（Windows 0 失败）不由 Linux 侧可证，最终以 CI 结果裁定。
- **O3**：`run $PYTHON ...` / `bash -c "... $PYTHON ..."` 多处未加引号（如 `helpers-python.bats:12`、`check-tdd-red.bats:496`）——解释器路径含空格时会被拆分。CI runner 路径无空格，低风险；与全仓既有风格一致，不强制改。

---

## 五、门槛对照

- 无行首 `- PASS` / `- FAIL` 格式。
- 结论均引用 `文件:行号` 锚点。
- Header `status: needs-revision`（2 项必修：NEEDS-REV-1 CI 接线 / NEEDS-REV-2 README 计数）。
