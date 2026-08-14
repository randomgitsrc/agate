---
phase: P2
task_id: TAG0010-python-migration
type: design
parent: P1-requirements.md
trace_id: TAG0010-P2-20260814
status: draft
created: 2026-08-14
agent: architect
# ── v2.0 机器字段 ──
candidate_count: 3
packages: [agate-scripts, agate-hooks, agate-consistency, agate-tests, agate-protocol-docs, agate-ci]
domains: [backend, cli]
ui_affected: false
---

# P2 方案设计 — agate 产品逻辑 Python 化（阶段一）

> 输入基线：P1-requirements.md（10 BDD + 表 A-E，approved）+ P0-brief.md + 分析报告
> docs/reviews/agate-python-migration-analysis-20260814.md。
> 本设计把 P1 的影响面映射表转化为可分批执行、可验证、可判定的实现导航。

## 1. 候选方案

> 场景类型：系统架构型迁移（30 个脚本跨语言重写 + hook 链 + consistency + CI 全链联动）。
> 三个候选方案均真实可行，从不同维度权衡；P1 已锁定的 SUGGEST（同名换后缀 / 非 hook 不保留薄壳 / ruff CI 独立 job / 扫描器扩展 .py）对所有候选都是硬约束，候选差异在**迁移组织方式**与**公共库边界**上。

### 方案 A（推荐）：模块化公共库 + 按依赖分批迁移

agate_common.py 承载全部被 source 的函数库（gate-result.sh + agate-workspace-resolve.sh），
30 个脚本按 P1 表 E 的依赖批次（0 公共库 → 1 自足叶 13 → 2 复合 11 → 3 hook 链 4 → 4 收尾）
逐脚本迁移，每批全量 bats 验证后推进。

- 优点：
  - 与 P1 表 E 批次划分一致，P0「逐脚本迁移 + 每步全量 bats、不批量重写」约束天然满足
  - agate_common.py 提供 `write_gate_result` / `read_state_phase` / 工作区解析 / `.agate-root` 恢复等公共函数，杜绝函数在 3+ 个脚本间复制漂移
  - ci-gate-backstop.py 批次 0 同步改为 import 直接调用（消除 `_find_bash`/WSL 规避依赖面）
- 风险：公共库边界若划错，批次 1/2 会返工。缓解：公共库只收"被 ≥2 处使用"的函数，单点工具函数留在各自脚本内。
- 工作量：批次 0（agate_common.py ~200 行）+ 批次 1-2（30 脚本各 60-120 行 py）+ 批次 3（3 薄壳 + install-hook.py）+ 批次 4（consistency/文档/CI）。

### 方案 B：零公共库 — 每个 py 脚本自带工具函数

不建 agate_common.py，`write_gate_result`/`resolve_formatter` 等函数在每个需要的脚本内各自实现一份，脚本完全自足、无模块间依赖。

- 优点：
  - 脚本自足，无 import 路径问题；bats 调用点只改命令名（`bash x.sh` → `python3 x.py`），无 sys.path 处理
  - 单脚本迁移独立性强，可完全并行
- 缺点：
  - `write_gate_result` 的 JSON 结构、`.gate-result.json` 格式、`resolve_formatter` 路径优先级在 3 个脚本中复制 → 与表 C 锚点关键字同理，**结构性漂移高发区**（P0 known_risks「协议文档与脚本引用大面积失效」会向"函数级"复发）
  - 违反 DRY，后续修 bug 需改多处
- 结论：仅当 agate_common.py 的 import 机制在 CI/Windows 下不可靠时才备选。实际上 Python 同目录 `import agate_common` 无需 sys.path 配置（脚本所在目录在 sys.path[0]），不构成障碍。

### 方案 C：保留 sh 兼容薄壳的渐进迁移

每个非 hook 脚本迁移后**保留一个同名 sh 薄壳**（`check-gate.sh` → 薄壳 exec `check-gate.py`），供直接调用脚本的用户（docs 引用、bats）无感过渡；全部迁移完成后一次性删薄壳。

- 优点：过渡期破坏性变更后置，文档引用可逐步改
- 缺点：与主 Agent 已采纳 SUGGEST「非 hook 脚本迁移后不保留 .sh 兼容薄壳（删档）」**直接冲突**；30 个 sh 薄壳 = 30 份双份维护，且 bats「改调 py」（验收①）要求测试直调 py，薄壳只服务存量用户却持续产生 shellcheck 面
- 结论：作为对照候选列出，明确否决。

### 权衡与选择理由

| 维度 | A | B | C |
|------|---|---|---|
| 与 P1/P0 约束一致性 | 完全一致 | 一致 | 违背 SUGGEST-1 |
| 公共逻辑防漂移 | 优（单点） | 劣（复制×3） | 中 |
| bats 调用点改动 | 中（~400 处改命令名） | 中 | 大（多一轮） |
| import 机制风险 | 低（同目录 import） | 无 | 低 |
| 并行度 | 中（批次内部可并行） | 高 | 中 |

**选择方案 A**：公共库边界按"≥2 处使用"收敛，批次依赖与 P1 表 E 完全对齐，
P4 implementer 按批次推进、每批可独立验收。表 C 锚点关键字、CLI 输出契约、
gate-result.json 结构由 agate_common.py 单点承载，是防漂移的关键决策。

---

## 2. 影响域分析

### 改什么
- `agate/scripts/`：30 个 sh → py（3 hook 保留 sh 薄壳）；`gate-result.sh`+`agate-workspace-resolve.sh` → `agate_common.py`；`install-hook.sh` → `install-hook.py`；新增 `pyproject.toml`
- `agate/scripts/check-protocol-consistency.py`：CHECK 8/9 锚点表路径 + `check_anchor_coverage` glob + `GATE_SCRIPT_EXEMPT`（4 项结构性同步点，§5）
- `agate/scripts/ci-gate-backstop.py`：bash subprocess 调用 → import/direct python 调用（消 `_find_bash`）
- `agate/tests/`：51 个 bats 文件约 400 处调用点改命令名；5 个专门断言文件改断言（表 D）
- `.github/workflows/protocol-tests.yml`：shellcheck 收敛到 3 薄壳 + 新增 ruff job + 扫描器调用目标
- 文档（表 B）：dispatch-protocol / orchestrator-template / git-integration / platform-notes（Windows 章节）/ UPGRADING（新章节）/ WORKFLOW / state-machine / SETUP（pyyaml 强制化）/ P6-acceptance 卡 / 受影响模板 / LIMITATIONS（局限 6）/ scripts/README.md

### 不改什么（边界）
- 18 个既有 py 不做功能改写（允许加注释/极小行为保持调整以满足 ruff 规则集）
- `count-tests.sh` / `check-windows-smoke.sh`（tests/scripts/，保持 sh）
- 既有任务数据格式（`.state.yaml` / `P{n}-*.md` / `active-tasks.md` / gate-result.json）零迁移
- CLI 输出契约：`GATE ...:` 前缀、exit 0/1/2 语义、`AGATE_WORKSPACE=`/`AGATE_TASKS_DIR=` 两行输出、gate-result.json 结构
- 协议文档全量重写（归 TAG0011）
- 测试框架 bats→pytest（TAG0011 另立）

### 风险点
- consistency 锚点表同步遗漏 → CHECK 8/9 ERROR（每批次后跑 consistency 兜底）
- ruff 规则集与既有 py 冲突 → 规则集在 P2 定死（§4），P4 只允许行为保持调整
- hook 薄壳 exec 失败静默放行 → 薄壳 fail-closed 阻断（不运行 sh 兜底逻辑，§3.3；BDD-9 已 BASELINE_CHANGE 为阻断语义）
- bats 机械调用点改动量大（~400 处）→ 按脚本批次同步改，每步全量 bats

---

## 3. 设计方案主体

### 3.1 agate_common.py 模块设计（批次 0）

> 职责：替代 `gate-result.sh` + `agate-workspace-resolve.sh` 的函数库；承载 3 个 hook 薄壳共用的定位/探测工具。所有函数显式 `encoding="utf-8"`，pyyaml 缺失时 fail-closed（同 agate-state-get.py L18-21 模式）。

**数据流函数（从 gate-result.sh 迁移）：**
- `write_gate_result(phase, task_id, exit_code, output)` → 写 `.gate-result.json`（6 字段结构不变）+ 追加 `.gate-history.jsonl`。`output` 的 JSON 转义改用 `json.dumps`（替代 agate-json-get.py escape），`prev_commit_sha` 用 `git rev-parse HEAD`（失败回退 "pre-commit"）
- `read_state_phase(state_file)` / `read_state_task_id(state_file)` → 读 frontmatter 字段；文件不存在返回 `""`；用 `yaml.safe_load`（替代 agate-state-get.py subprocess 调用，pyyaml 已是强制依赖）
- `has_staged_phase_change(state_file)` → `git diff --cached --name-only` + CRLF 剥离（`line.rstrip("\r")`）+ 检查 `^\+.*phase:`（替代 `tr -d '\r'` + grep）
- `has_staged_phase_output()` → staged 文件名匹配 `P[0-9]+-.*\.(md|yaml)$`
- `resolve_formatter(fmt, task_dir, agate_root)` → 路径优先级：绝对路径 → `$task_dir/.agate/formatters/` → `$agate_root/assets/formatters/`
- `run_test_with_formatter(cmd, fmt_path, timeout_secs)` → subprocess + `AGATE_TDD_TIMEOUT` 超时 + JSON 结构（含 `raw_output` 转义），保留 exit 124 超时语义

**工作区解析函数（从 agate-workspace-resolve.sh 迁移）：**
- `resolve_workspace(project_root) -> (AGATE_WORKSPACE, AGATE_TASKS_DIR)`：优先级 `.agate.env(AGATE_WORKSPACE=)` → env `AGATE_TASKS_DIR` → 默认 `{project_root}/agate-workspace`；相对路径对 project_root 归一；`Path.resolve()`（替代 realpath -m）；`.agate.env` 读取 `encoding="utf-8"` + CRLF 剥离（bdd-18 契约）
- 执行模式 main：`AGATE_WORKSPACE=`/`AGATE_TASKS_DIR=` 两行输出（CLI 契约，bats 直调）

**hook 公共工具（薄壳共用）：**
- `resolve_agate_root(script_path)`：readlink 软链解析 → 复制模式 `.agate-root` 恢复（读标记文件 + CRLF 剥离）
- `probe_python()` → `python3` → `python`（shutil.which 顺序探测，替代 detect_python helper 语义）
- `run_git(args, cwd=None)` → subprocess 封装，`encoding="utf-8"` + `errors="replace"` + 返回 `(returncode, stdout)`，统一 CRLF 处理

**模块入口约定**：`if __name__ == "__main__"` 仅实现工作区解析执行模式（供 bats 直调），函数被 `import agate_common` 复用。同目录 import 无需 sys.path 配置。

### 3.2 30 个脚本分批迁移方案（按表 E 批次）

> 迁移规则（每批通用）：同名换后缀（`check-gate.sh` → `check-gate.py`）；`#!/usr/bin/env python3` shebang；`encoding="utf-8"` 强制；3.8+ 语法；CLI 契约不变；grep/sed/awk 管道 → re/pathlib/subprocess 等价实现；**依赖表 A 调用的既有 py 保持 subprocess 调用**（既有 py 不做功能改写）。

**批次 0 — 公共库（前置，无依赖）**
- `agate_common.py`（§3.1）+ 同步改 `ci-gate-backstop.py`：`resolve_tasks_dir` 改调 `agate_common.resolve_workspace`（消除对 `agate-workspace-resolve.sh` 的 bash subprocess；`sys.executable` 自举）
- **批次 0 收窄（BLOCKER-2 修订）**：`_find_bash`/`_bash_cmd` **保留**（`run_gate` 仍调 check-gate.sh，check-tdd-red.sh / check-p6-provenance.sh 亦仍为 sh）；`run_gate` 的 check-gate.sh → check-gate.py 切换**移入批次 2**（与 check-gate.py 产出同批）；`_bash_cmd` 随批次 2 各被调脚本 py 化逐个删除（check-gate.py / check-tdd-red.py / check-p6-provenance.py 落地后调用点同步换 py、删除对应 `_bash_cmd` 使用）
- 验证：`agate-workspace-resolve.bats`(10) 改调 py 后绿 + `helpers-python.bats`(3) 重构后绿 + `ci-gate-backstop.bats`（断言**仅 workspace 解析相关**）改后绿 + 全量 bats

**批次 1 — 自足叶节点（13）**：check-changelog / check-frontmatter / check-state-yaml / check-p6-format / check-scope-resolved / agate-archive-stale-outputs / agate-extract-context / agate-next-card / agate-render-dispatch-prompt / agate-summary / agate-changes / agate-migrate-workspace / **check-platform-assumptions**（含扩展 .py 规则集，§4.2）
- 逐脚本迁移，每迁一个同步改对应 bats 调用点 + 跑全量
- check-platform-assumptions：sh → py 时保留 R1-R5 规则 + 扩展名过滤新增 `.py`；"本体无 GNU 特性"断言改 py 语义（正则引擎约束）；fixture 检测契约不变
- **BDD-6 前置验证执行方案（BLOCKER-1 修订）**：对既有 18 个 py 跑扩展后的扫描器确认洁净度，预期违规清单 + 处理方式如下：
  - **预期违规（实测 4 行 R2，全部位于 docstring 内，非 `#` 注释行）**：`agate-json-get.py:5`（docstring 示例 `echo "$x" | python3 -c '...'`）、`check-protocol-consistency.py:23-25`（docstring 用法示例 `python3 scripts/check-protocol-consistency.py [--strict|--json]`）——当前 `r2_exempt` 只豁免 `#`/`@test`/`command -v`/`env` 形态（check-platform-assumptions.sh:43-55），对 docstring 不豁免
  - **处理方式（主 Agent 决策，写死）**：扫描器 py 版 `r2_exempt` 语义**扩展到 `"""` docstring 块**——docstring 内示例命令不命中 R2（docstring 是文档非可执行代码，与 `#` 注释行同类豁免）；**不改写既有 py 的 docstring 内容**（18 个既有 py 不做功能/文档改写，§2 边界）
  - **零命中目标**：docstring 豁免生效后，对既有 18 py 扩展扫描器扫描 = 0 命中（exit 0），BDD-6 前置验证通过；迁移新增 py 同样受 docstring 豁免约束

**批次 2 — 复合（11）**：check-state-transition / check-retrospective / check-pruning / check-debt / check-tdd-red / check-gate / check-p6-evidence / check-p6-provenance / agate-capture-env-baseline / agate-retreat-to / agate-inject-card
- 依赖批次 0（函数库）+ 批次 1（retreat-to 依赖 archive + state-transition 的 MAX_RETRY_MAP 提取；inject-card 依赖 next-card）
- **check-gate.py（488 行）拆子任务**：P0/P1 分支 → P2/P3 → P4/P5 → P6 → P7/P8，每个子任务跑 check-gate.bats 相关用例
- MAX_RETRY_MAP：单一数据源保持——`agate-retreat-to.sh` 的 grep 提取改为 import 常量或模块级常量（避免文本耦合漂移）

**批次 3 — hook 链（4）**：pre-commit-gate / commit-msg-self-gate / pre-push-gate 薄壳化 + install-hook.sh → install-hook.py
- pre-commit-gate.py 承载调度逻辑（12 个子脚本从 `bash xxx.sh` 改为 `sys.executable xxx.py`）+ PROD_TOUCHED 三步检测 + dispatch-context hash 校验 + write_gate_result
- commit-msg-self-gate.py / pre-push-gate.py 承载各自逻辑；薄壳 §6
- install-hook.py：`ln -sf` 软链（Windows 复制模式 + 写 `.agate-root` 标记）+ chmod + 备份既有 hook + `.gitignore` 检测
- 验证：pre-commit-hook.bats / pre-push-hook.bats / commit-msg-self-gate.bats / install-hook.bats / protocol-alignment-review.bats

**批次 4 — 收尾（0 ERROR 门槛）**：consistency 锚点表同步（§5）+ 文档引用同步（表 B，§7）+ SETUP pyyaml 强制化 + UPGRADING 新章节 + scripts/README.md 重写 + CI 同步（§8）

### 3.3 hook 薄壳设计（3 个，~15 行/个）

> 设计依据：分析报告 §3.1（git 通过 Git Bash sh.exe 执行 hook；`#!/usr/bin/env python3` 在 Windows 不可靠；复制模式 `.agate-root` 恢复必须留薄壳）。约束：`PROD_TOUCHED`/`PROD_NOT_TOUCHED`、`AGATE_ALIGNMENT_REVIEW_THRESHOLD` 两个锚点关键字必须存活在薄壳中（表 C 观察项）。

通用结构（以 pre-commit-gate.sh 为例）：
```bash
#!/usr/bin/env bash
set -u
# 1. AGATE_ROOT 自定位（软链→本体；复制模式 .agate-root 恢复）
AGATE_ROOT="${AGATE_ROOT:-$(dirname "$(dirname "$(readlink -f "${BASH_SOURCE[0]:-$0}")")")}"
if [ ! -d "$AGATE_ROOT/scripts" ] \
    && [ -f "$(dirname "$(readlink -f "${BASH_SOURCE[0]:-$0}")")/.agate-root" ]; then
    AGATE_ROOT=$(tr -d '\r' < "$(dirname "$(readlink -f "${BASH_SOURCE[0]:-$0}")")/.agate-root")
fi
# 2. python 探测：python3 → python
PY=""
for c in python3 python; do command -v "$c" >/dev/null 2>&1 && { PY="$c"; break; }; done
# 3. exec python 主程序
if [ -n "$PY" ] && [ -f "$AGATE_ROOT/scripts/pre-commit-gate.py" ]; then
    exec "$PY" "$AGATE_ROOT/scripts/pre-commit-gate.py" "$@"
fi
# 4. exec 失败 → fail-closed 阻断（不运行 sh 兜底逻辑，非静默放行）
echo "GATE ERROR: 无法启动 python gate（python3/python 均不可用或脚本缺失）" >&2
echo "  PROD_TOUCHED / PROD_NOT_TOUCHED 检测无法执行，commit 中止——请安装 python3 + pyyaml" >&2
exit 1
```
> **fallback 语义（BLOCKER-3 修订，fail-closed）**：薄壳 exec 失败时**阻断 commit（输出 GATE ERROR + exit 非 0）**，**不运行保留的 sh gate 逻辑**——sh 薄壳只承担「python 探测 + exec 主程序 + 失败阻断」三件事，gate 判定逻辑全部在 py 侧单份维护（保 sh 逻辑需双份维护 gate 判定，违背本任务宗旨）。此语义为主 Agent 已批准的 [BASELINE_CHANGE]（P1 BDD-9，P1-requirements.md §4 BDD-9 标注），影响面 = Windows 无 python 环境 commit 被阻断，UPGRADING 明示 python3+pyyaml 为强制安装项。
- pre-push-gate.sh：同样的薄壳 + `AGATE_ALIGNMENT_REVIEW_THRESHOLD` 关键字保留（薄壳注释或阈值默认值）
- commit-msg-self-gate.sh：薄壳 + self-gate 触发面 grep 逻辑由 py 主程序承载（薄壳只 exec commit-msg-self-gate.py）
- 3 个薄壳是仅存的 sh，BDD-4 的 shellcheck 扫描面收敛到它们

### 3.4 pyproject.toml 规则集建议（P2 交付物，BDD-3）

> 实测基线（ruff 0.16.3，本任务 dev venv `~/.venvs/agate-dev/`）：默认规则集对既有 18 py 报 68 错误（P1 记 70 系版本差异），UP032×35 / BLE001×9 / PLW1510×6 为主，F541×2、UP031×1、SIM905/103/102×1、S112/S110×1、RUF059×1、I001×1、F401×1。

建议 pyproject.toml（select 子集 + target py38 + ignore 列表，让既有 18 py 在 `ruff check --fix` 后零违规）：

```toml
[tool.ruff]
target-version = "py38"
line-length = 120
src = ["agate/scripts"]

[tool.ruff.lint]
select = ["E4", "E7", "E9", "F", "W", "I", "UP", "B", "SIM", "C4", "RUF", "PLW"]
ignore = [
  "BLE001",   # gate 脚本 fail-closed 兜底有意捕获宽异常（语义有意）
  "PLW1510",  # subprocess.run 显式捕获 returncode，不需要 check=（调用方语义）
  "SIM115",   # 一次性读文件 open().read() 简洁形态（语义等价）
  "RUF001", "RUF002", "RUF003",  # Unicode 混淆字符检查（中文注释误报）
]
```
> 说明（非阻塞-1 修订）：已清理死 ignore 条目——`E501`（select 只含 E4/E7/E9，E501 未被选中）、`PLR0911/0912/0915/2004` 与 `PLC0415`（select 只含 PLW，PLR/PLC 未选中）均不生效，属误导性死条目，不再列出。

设计依据（实测验证）：
- 该 select 集对既有 18 py 报 60 错误，其中 54 个为 `--fix` 可自动修复（UP032/F401/I001/F541/UP031 等，行为保持），剩 6 个（SIM102/SIM103/SIM105/RUF005/RUF059 + PLW 类）需 `--unsafe-fixes` 或极小手工调整——均在 P1 §2.5「既有 py 不改功能，允许极小调整（不改变行为）」边界内
- 实测：`ruff check --fix --unsafe-fixes` 后既有 18 py 全绿（零违规），且改动全部为 f-string 化/import 排序/折叠 if 等行为保持重构
- `target-version = "py38"` 满足 BDD-8（ruff 会拒绝 `match` 等 3.10+ 语法，实测验证）；`str.removeprefix` 属运行期方法非语法，靠 code review + 单测覆盖（无静态保证，标注局限）
- 排除 S（bandit）与 PLR 复杂度规则：gate 脚本的 try/except-pass（S110/S112）与 subprocess 模式（S603/S607）是协议固有模式，纳入会大量误报

**ruff CI 接入**：独立 job（`pip install ruff && ruff check agate/scripts/`，项目根 pyproject.toml 自动生效），不做 pre-commit hook 子步骤（SUGGEST-4）。

### 3.5 consistency 锚点表同步方案（表 C 结构性同步点 4 项）

> 设计原则：**关键字必须存活在 py 中**（迁移时原样保留字符串字面量），锚点表的 `script:` 路径随命名同步改 `.sh` → `.py`。两方案混合使用——保关键字为主、改锚点表路径为辅。

1. **`V06_KEYWORD_ASSERTIONS` 路径同步**（CHECK 8，4 条涉 sh）：
   - `check-gate.sh` → `check-gate.py`（DESIGN_GAP / --cached 两条）
   - `check-pruning.sh` → `check-pruning.py`（P2 不可裁剪 / --cached 两条）
   - 关键字（DESIGN_GAP / P2 不可裁剪 / --cached）在 py 中以字符串字面量存活
2. **`SCRIPT_ALIGNMENT_ANCHORS` 路径同步**（CHECK 9，16 条涉 sh）：所有 `agate/scripts/check-*.sh` → `check-*.py`（check-gate×6 / check-pruning×6 / check-state-transition×2 / check-p6-evidence×4 / check-p6-provenance×3 / check-p6-format / check-frontmatter / check-debt / check-platform-assumptions / check-retrospective / check-changelog / check-state-yaml / check-tdd-red / check-scope-resolved）；**pre-commit-gate.sh / pre-push-gate.sh 两条保留 sh 路径**（薄壳含关键字）
3. **`GATE_SCRIPT_EXEMPT` 调整**：移除 gate-result.sh（并入 agate_common.py）、install-hook.sh（→ install-hook.py）、agate-changes.sh / agate-summary.sh（已 py 化）；新增 `agate/scripts/check-protocol-consistency.py`（自身无锚点但必须被 glob 豁免，见下）+ `agate/scripts/pre-commit-gate.py`；清理 stale 的 agate-init.sh
4. **`check_anchor_coverage` glob 更新**：`check-*.sh` → `check-*.py`（+ pre-commit-gate.sh + pre-commit-gate.py + ci-gate-backstop.py 显式追加）。**关键边界（本设计新增发现）**：glob 改成 `check-*.py` 后 `check-protocol-consistency.py` 自身会命中 glob 但无锚点 → 必须加入 GATE_SCRIPT_EXEMPT，否则 CHECK9-coverage WARNING → `--strict` 挂（破坏 BDD-2）

**执行顺序**：批次 4 一次性同步；但批次 0-3 每迁一个脚本后跑 consistency，若锚点未同步会 ERROR——因此**锚点表路径随各批次脚本迁移同步改**（非集中在批次 4），批次 4 只做最终 `--strict` 全绿确认。

### 3.6 bats 断言改动方案（表 D）

**两层改动：**

1. **机械调用面（~400 处 / 51 文件）**：`bash "$AGATE_SCRIPTS/x.sh"` → `"$PYTHON" "$AGATE_SCRIPTS/x.py"`（复用 fixtures.bash 的 `$PYTHON` detect_python，Windows 上自动解析 python 而非 python3）。随各脚本批次同步改。
2. **断言级变更（5 文件 / 40 用例）：**
   - `check-platform-assumptions.bats`(16)：①调用方式 13 处改 py；②目录扫描扩展名过滤契约（`.bats/.bash/.sh`）扩展 `.py`；③"本体无 GNU 特性（POSIX ERE/无 grep -P）"断言改 py 语义（无 grep，改为"py 源码无 subprocess 调 grep -P / 正则引擎约束"）；④干净树契约重述；⑤新增 `.py` fixture 含 R1-R5 假设能被检出的用例；⑥**docstring 豁免两类用例（BLOCKER-1）**：docstring 内 python3 引用不命中 R2（豁免生效）+ 真 R2 命中（docstring 外裸 python3）仍被检出（豁免不越界）
   - `env-adapt-docs.bats`(9)：bdd-34（shellcheck `*.sh` 0 error）→ shellcheck 覆盖面收敛到 3 薄壳 + 新增 ruff 断言（`ruff check agate/scripts/` 0 error）；其余 8 个不变
   - `agate-scripts-encoding.bats`(2)：bdd-5 扫描 `*.py` 强守卫扩大（含新增 py）；bdd-8 不变
   - `helpers-python.bats`(3)：bdd-17 重构为"py 自举后的 python 探测 + 失败回退"语义（不再依赖 bash shim）；bdd-13/15 的 detect_python 评估——product 侧 py 化后 helper 语义保留（bats 仍需 `$PYTHON`），断言保留
   - `agate-workspace-resolve.bats`(10)：10 处调用改 py；两行输出契约与 CRLF 剥离（bdd-18）断言保留（py 版必须满足的行为契约）
3. **约束**：`count-tests.sh`（`^@test` 口径）用例数不减少（表 D 附录 A 对照）；`check-windows-smoke.bats` 机制不动

### 3.7 文档引用同步方案（表 B）

> 范围 = P1 表 B 的 in-scope 文档。迁后命名约定：同名换后缀；3 hook 保留 sh；install-hook.sh → install-hook.py；count-tests.sh 不在范围。

- **agate/scripts/README.md**：脚本清单表重写（sh/py 分类）
- **platform-notes.md**：Windows 章节重写——"25 个 .sh 无法运行"限制更新为"py 化后无 bash 环境成为可行选项"；`bash install-hook.sh` → `python3 install-hook.py`；复制模式前提保留
- **UPGRADING.md**：新增本版本迁移章节（破坏性变更逐条列：30 脚本改名/删档、install-hook 变 py、shellcheck→ruff）
- **SETUP.md**：新增 pyyaml 强制安装说明 + 调用命令改 py
- **LIMITATIONS.md**：局限 6「pyyaml 可选」→ 强制依赖表述
- **dispatch-protocol / orchestrator-template / git-integration / WORKFLOW / state-machine / P6-acceptance 卡 / task-files / handoff-template / tech-debt-template**：脚本引用同名换后缀
- 计数口径按 P1 表 B（`rg -o` 逐次实测）逐文档核对，防遗漏

### 3.8 UPGRADING / SETUP 更新要点

- **UPGRADING 新章节（必做，P8 强制项）**：30 个脚本改名/删档的破坏性变更逐条列；install-hook.sh → install-hook.py 的迁移命令；hook 无需重装（软链自动跟随）；复制模式用户需重跑 install-hook
- **SETUP.md**：`pip install pyyaml` 强制步骤；脚本调用示例改 py（`python3 ~/.agate/scripts/agate-summary.py` 等）

---

## 4. gate_commands（P2 固化，P4-P6 不得修改）

```yaml
gate_commands:
  P3: "bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/"
  P3_formatter: "generic-tap.sh"
  P5: "bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/ 2>&1 | tail -40"
  P5_consistency: "python3 agate/scripts/check-protocol-consistency.py --strict 2>&1 | tail -20"
  P5_ruff: "ruff check agate/scripts/ 2>&1 | tail -20"
  P5_scan: "python3 agate/scripts/check-platform-assumptions.py 2>&1 | tail -20"
  P5_ci: "python3 agate/scripts/ci-gate-backstop.py 2>&1 | tail -20"
```

- 本项目测试运行器是 **bats**（阶段一保持），`P3`/`P3_formatter`（bats TAP 输出用 generic-tap.sh）供 check-tdd-red.sh 读取
- P5 主命令 = bats 全量（紧凑输出）；`P5_consistency`/`P5_ruff`/`P5_scan`/`P5_ci` 为 BDD-2/3/6/验收④的辅助 gate
- `ui_affected: false` → 无需 P5_e2e

## 5. files_to_read（实现导航，控制 P4 上下文）

```yaml
files_to_read:
  - path: agate/scripts/gate-result.sh
    why: agate_common.py 数据流函数的迁移源（write_gate_result/read_state_phase/formatter）
  - path: agate/scripts/agate-workspace-resolve.sh
    why: agate_common.py 工作区解析函数迁移源（两行输出契约/bdd-18）
  - path: agate/scripts/check-gate.sh
    why: check-gate.py 迁移源（最大单文件，P0-P8 case 分支/CRLF 容错 sed 模式）
  - path: agate/scripts/pre-commit-gate.sh
    why: 薄壳化源（L1-38 AGATE_ROOT/复制模式恢复）+ pre-commit-gate.py 调度链迁移源（12 子脚本/PROD_TOUCHED/hash 校验）
  - path: agate/scripts/pre-push-gate.sh
    why: 批次 3 薄壳化独立迁移源（AGATE_ALIGNMENT_REVIEW_THRESHOLD 关键字保留——表 C 锚点）
  - path: agate/scripts/commit-msg-self-gate.sh
    why: 批次 3 薄壳化独立迁移源（self-gate 触发面 grep）
  - path: agate/scripts/check-protocol-consistency.py:442-767
    why: 锚点表路径同步（V06_KEYWORD_ASSERTIONS/SCRIPT_ALIGNMENT_ANCHORS/GATE_SCRIPT_EXEMPT/check_anchor_coverage glob）
  - path: agate/scripts/install-hook.sh
    why: install-hook.py 迁移源（软链/复制模式/.agate-root 标记/备份）
  - path: agate/scripts/ci-gate-backstop.py
    why: _find_bash/_bash_cmd 替换为 agate_common 直接调用的改造点
  - path: agate/scripts/check-platform-assumptions.sh
    why: 扫描器 py 化 + 扩展 .py 规则集（R1-R5/扩展名过滤）
  - path: agate/scripts/check-tdd-red.sh
    why: check-tdd-red.py 迁移源（read_gate_commands/judge_result A-B 类/resolve_formatter）
  - path: agate/tests/helpers/fixtures.bash
    why: detect_python/$PYTHON/py_path 约定（bats 调用 py 的统一入口）
  - path: agate/tests/unit/agate-workspace-resolve.bats
    why: 两行输出契约 + CRLF 剥离断言（py 版行为契约）
  - path: agate/tests/scripts/check-platform-assumptions.bats
    why: 扫描器行为断言（扩展名过滤/本体特性/干净树契约）
  - path: .github/workflows/protocol-tests.yml
    why: CI 同步（shellcheck 收敛/ruff job/扫描器目标）
```

## 6. env_constraints（继承 P0-brief，不弱化）

```yaml
env_constraints:
  debug_env: "本环境 Linux（python3 3.12.3 + pyyaml 6.0.1 + ruff 0.16.3 @ ~/.venvs/agate-dev/）；Windows 用 CI matrix 冒烟 + 静态分析验证"
  python_min: "3.8+（ruff target-version=py38；禁 match/str.removeprefix 等 3.9+/3.10+ 语法）"
  encoding: "所有 py 文本读写显式 encoding='utf-8'（gate 规则）"
  pyyaml: "强制依赖（SETUP.md 明确 pip install pyyaml；缺失时 py gate fail-closed）"
  isolation_check: "bats 用 $BATS_TEST_TMPDIR；worktree 隔离；~/.agate 稳定版禁止改动"
  windows: "复制模式 .agate-root 恢复 / CRLF / python 命令名差异 → CI Windows matrix 冒烟"
```

## 7. minimal_validation（P1 已标 requires_minimal_validation: true，必须产出）

```yaml
minimal_validation:
  - assumption: "hook 薄壳 python 探测（python3→python）+ exec 失败回退在 Linux 可模拟验证"
    method: "写 mock thin-shell.sh：①真 python 存在→exec py 主程序成功；②python3 stub exit 127 + python 缺失→回退 sh fallback（非静默放行，exit 非 0）"
    result: "confirmed"
    note: "本地实测通过：python 存在时 PY_MAIN_RAN 输出 + exit 0；python3 stub 127 时进入 FALLBACK_SH_BRANCH + exit 3（未静默放行）。Windows 真机行为（sh.exe 解析 shebang/复制模式安装）标 CI Windows matrix 验证"
  - assumption: "复制模式 .agate-root 恢复逻辑（薄壳 L31-38 语义）"
    method: "模拟环境：hook 副本目录含 .agate-root 标记、本体 scripts/ 不存在 → 读标记恢复 AGATE_ROOT"
    result: "confirmed"
    note: "本地实测通过：RECOVERED_AGATE_ROOT=真实本体路径 + SCRIPTS_DIR_OK。Windows 复制安装行为（ln 退化为复制）标 CI 冒烟"
  - assumption: "ruff select 规则集可让既有 18 py 零违规（P2 pyproject.toml 交付物）"
    method: "对现有 18 py 跑候选 select+ignore，先 --fix（行为保持）再核对剩余违规"
    result: "confirmed"
    note: "实测：候选规则集报 60 错误，54 个 --fix 自动修复（f-string/import 排序/折叠 if 等行为保持），剩余 6 个用 --unsafe-fixes（SIM102/SIM103/SIM105/RUF005/RUF059）或极小手工调整归零——均在 P1 §2.5 边界内"
  - assumption: "ruff target-version=py38 能拒绝 3.10+ 语法（BDD-8）"
    method: "对含 match 的样例跑 ruff --target-version py38"
    result: "confirmed"
    note: "实测 match 语句报 invalid-syntax。str.removeprefix 属运行期方法非语法，ruff 不报——靠 code review + 单测覆盖，标注局限"
  - assumption: "纯代码逻辑部分（gate 判定/状态机/CLI 输出）无外部系统依赖"
    method: "依赖清单：subprocess(git/既有 py)、pyyaml、json、pathlib、re、shutil（probe_python）；数据转换：YAML frontmatter 读写、CRLF 剥离、JSON 转义"
    result: "not_needed"
    note: "纯代码逻辑声明：依赖的都是 Python 标准库 + 已锁定的 pyyaml，无浏览器/安全模型/外部系统行为假设。Windows 专属行为（复制模式/CRLF/命令名）在 CI 冒烟覆盖"
```

## 8. 实现完成的标志（可判定标准）

| 标志 | 判定方式 |
|------|---------|
| 全量 bats 全绿 | `bats sanity+unit+regression+integration` exit 0，且 `count-tests.sh` 用例数不减少（BDD-1） |
| consistency 0 ERROR 0 WARNING（--strict） | `python3 agate/scripts/check-protocol-consistency.py --strict` exit 0（BDD-2） |
| ruff 全绿 | `ruff check agate/scripts/` exit 0（按 P2 pyproject.toml 规则集，BDD-3/BDD-8） |
| shellcheck 收敛 | `shellcheck -S warning agate/scripts/*.sh` exit 0，受扫集合 == 3 个 hook 薄壳（BDD-4） |
| 扫描器覆盖 .py | `check-platform-assumptions.py` 对 tests/ + scripts/*.py 扫描 exit 0，且 .py fixture 能被检出（BDD-6） |
| Windows 冒烟 | CI windows-latest matrix 全绿（BDD-5） |
| hook 薄壳 | pre-commit/pre-push/commit-msg 薄壳含 PROD_TOUCHED / AGATE_ALIGNMENT_REVIEW_THRESHOLD 关键字 + python 探测 exec + 失败 fail-closed 阻断（BDD-9） |
| CLI 契约 | .state.yaml 读回一致、exit 0/1/2 语义、GATE 前缀、AGATE_WORKSPACE=/AGATE_TASKS_DIR= 两行、gate-result.json 结构不变（BDD-10） |
| 编码守卫 | encoding 守卫对全部 py 零违规（BDD-7） |
| 文档同步 | 表 B 文档引用逐一核对无 .sh 残留（除 3 薄壳 + tests/scripts） |
| UPGRADING | 新章节列出破坏性变更（P8 强制项） |

## 9. 实现完成后的验证口径（P5）

P5 gate 按 §4 gate_commands 执行：
1. `bats` 全量（主命令）
2. `P5_consistency`（--strict 0 ERROR）
3. `P5_ruff`（规则集 0 error）
4. `P5_scan`（扩展扫描器 0 命中）
5. `P5_ci`（backstop 对照 .gate-result.json）
6. Windows 冒烟由 CI matrix 覆盖（BDD-5）

## 10. 风险与缓解补充

- **公共库边界错划**：agate_common.py 只收 ≥2 处使用的函数；单点函数留脚本内（P4 implementer 判断，标 [DESIGN_GAP] 上报）
- **批次 2 check-gate.py 大文件**：拆 P 分支子任务，每个子任务独立跑 check-gate.bats 相关用例
- **锚点表同步遗漏**：每批次后跑 consistency（非集中批次 4）；批次 4 以 --strict 全绿收口
- **ruff --unsafe-fixes 的 6 处**：标注为行为保持重构，P4 需 diff 审查确认无行为变化
- **Windows 复制模式用户升级**：UPGRADING 明示需重跑 install-hook.py
