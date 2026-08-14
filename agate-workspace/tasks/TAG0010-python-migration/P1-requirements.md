---
phase: P1
task_id: TAG0010-python-migration
type: problems
parent: P0-brief.md
trace_id: TAG0010-P1-20260814
status: draft
created: 2026-08-14
agent: analyst
# ── v2.0 机器字段 ──
risk_level: high
phases: [P1, P2, P3, P4, P5, P6, P7, P8]
packages: [agate-scripts, agate-hooks, agate-consistency, agate-tests, agate-protocol-docs, agate-ci]
domains: [backend, cli]
change_type: refactor
# 能力需求声明（analyst.md 三态：available=已具备）
# requires_minimal_validation: Windows 真机行为无法在本地 Linux 验证，P2 architect 须产出 minimal_validation 块
capability_requirements:
  - need: python 静态检查（ruff）
    why: 验收③——py 代码静态检查，替代 shellcheck 承担"外部客观 gate"职责
    available:
      - "~/.venvs/agate-dev/（ruff 0.16.3，本任务开发环境已具备）"
    status: available
  - need: Windows CI 冒烟执行
    why: 验收④——Windows 真机行为（复制模式 hook/CRLF/路径）无法在本地 Linux 完整验证
    available:
      - "GitHub Actions windows-latest matrix（executor_env.network: full）"
    status: available
requires_minimal_validation: true
---

# P1 需求基线 — agate 产品逻辑 Python 化（阶段一）

> 本文件是 TAG0010 的需求基线（"活基线"）。后续阶段发现新隐含需求时由主 Agent 增补并标 `[SCOPE+ from Pn]`。
> 需求权威来源：`docs/reviews/agate-python-migration-analysis-20260814.md`（§9 立项建议 + 5 条验收标准）+ `P0-brief.md`。

## 1. 需求复述

**核心需求**：把 `agate/scripts/` 下 30 个 `.sh` 的 bash 逻辑迁移到 Python（`hook 入口保留 sh 薄壳`），消解 bash 在 Windows MSYS2 模拟层的结构性平台问题（MSYS 路径风格混用 / CRLF / WSL 干扰 / 路径解析差异——TAG0005+0009 复盘确认的 78 个 Windows 失败根因）。

**范围锁定**（P0-brief 已确认，不可扩张）：
- 30 个 sh → py；**pre-commit / commit-msg / pre-push 3 个 hook 入口保留 sh 薄壳**（硬约束，理由见 §2）。
- `gate-result.sh`（105 行）+ `agate-workspace-resolve.sh`（57 行）两个被 source 的函数库 → Python 化等价物（`agate_common.py` 模块）。
- 阶段一**不做协议文档全量重写**（文档/CI 全面同步归 TAG0011），但**必要的引用同步**计入范围：dispatch-protocol / orchestrator-template / git-integration / platform-notes（Windows 章节）/ UPGRADING / SETUP（pyyaml 强制化）/ 受影响模板 / scripts/README.md。
- **明确不做**：测试框架 bats→pytest（TAG0011 另立）；18 个既有 .py 不做功能改写（除 ci-gate-backstop.py 因反向依赖 sh 需联动）。

**目标状态（验收口径）**：产品逻辑全 Python，bats 测试改为直接调 py 脚本；CI 保持 Linux 全量 + Windows 冒烟；5 条验收标准（分析报告 §9）全过。

## 2. 隐含需求识别（逐维度）

> 本任务是纯代码/文档逻辑任务，无 UI。按 analyst.md 隐含需求清单逐维度过，并补 agate 特有二层依赖。

### 2.1 数据维度：既有任务数据必须零迁移兼容
- `.state.yaml` / `P{n}-*.md` / `active-tasks.md` / `tech-debt.md` / 证据目录等**既有数据格式与字段语义不变**——Python 读写同格式，不做任何数据迁移动作。这是迁移的兼容性底线（分析报告 §7 风险表「兼容性」行）。

### 2.2 前端/展示维度：CLI 输出契约必须保持
- 无 GUI，但**CLI 面向 Agent/人的输出契约是协议的一部分**：`GATE ...:` 前缀错误消息、exit code 语义（0=通过 / 1=未通过 / 2=需主 Agent 自判，如 check-gate P1、check-debt 覆盖模式依赖加载失败）、`AGATE_WORKSPACE=`/`AGATE_TASKS_DIR=` 两行解析输出（agate-workspace-resolve 执行模式）、gate-result.json 结构（`write_gate_result` 的 JSON 格式）。**输出格式变化 = 破坏协议**（下游 pre-commit-gate、ci-gate-backstop、dispatch 依赖这些契约）。

### 2.3 多端维度：调用方全面盘点（关键隐含需求）
| 调用方 | 现状 | 迁移后必须 |
|--------|------|-----------|
| bats 测试（29 文件 / 约 400 处 `bash $AGATE_SCRIPTS/*.sh` 运行点） | bash 调 sh | 改调 py（验收①「bats 调 py」）；断言级变更集中在 5 个专门文件（表 D） |
| 3 个 hook 薄壳（pre-commit/commit-msg/pre-push） | 保留 sh | 薄壳 `exec python` 主程序 |
| `ci-gate-backstop.py`（既有 py） | bash subprocess 调 check-gate.sh + agate-workspace-resolve.sh | 改直接 python 调用（消除 `_find_bash`/WSL 规避的依赖面） |
| CI（protocol-tests.yml） | shellcheck `*.sh` + check-platform-assumptions.sh + consistency + backstop | shellcheck 收敛到保留薄壳；新增 ruff；扫描器调用目标更新 |
| 文档引用 | 全局 grep 到 30 个 sh 路径 | 同步（表 B） |
| `check-windows-smoke.sh` | 选代表用例 | 保留（机制不变，代表用例随 bats 文件更新自动生效） |

### 2.4 边界维度：失败路径与平台边界
- **hook exec 失败回退**：薄壳需"python 探测 + 失败回退"，保留 sh 逻辑作为 fallback（P0 known_risks）。
- **Windows 命令名差异**：`python` vs `python3`——py 脚本调用/探测需兼容两者（现有 `detect_python` helper 语义）。
- **编码边界**：Windows Python 文本默认 ANSI 代码页（cp1252/cp936）→ 所有 py 文本读写**必须显式 `encoding="utf-8"`**（列 gate 规则，防 88d0deb 根因复发）。
- **Python 版本边界**：下限 3.8+，新代码不得用 3.9+/3.10+ 语法（`match`、`str.removeprefix` 等）。
- **pyyaml 缺失**：pyyaml 从可选变强制依赖——环境缺 pyyaml 时 py gate 的失败方式须明确（fail-closed 报错而非静默放行，同现有 check-frontmatter/state-yaml 薄壳的 fail-closed 模式）。
- **路径边界**：含空格路径、CRLF 行尾（git diff --cached 输出）、`.agate-root` 复制模式恢复——这些现有 bash 处理点迁移到 py 后语义不丢。

### 2.5 兼容维度：协议一致性机制必须零破坏
- **consistency 锚点约束**（硬约束，P0 known_risks）：CHECK 8/9 锚点表硬编码 `.sh` 路径与关键字。py 版脚本**必须保留这些关键字**或**同步更新锚点表**，否则 consistency 报 ERROR。锚点关键字完整映射表见**表 C**。
- **check_anchor_coverage 反向检查空转风险**：`check_anchor_coverage` 的 glob 是 `check-*.sh` + pre-commit-gate.sh + ci-gate-backstop.py——脚本迁 py 后若 glob 不更新，反向覆盖检查会**静默空转（找不到任何 check-*.sh）**，锚点漏配不再被发现。该 glob 与 `GATE_SCRIPT_EXEMPT` 白名单（gate-result.sh / install-hook.sh / agate-changes.sh / agate-summary.sh / agate-init.sh）须随迁移同步调整。
- **shellcheck 纪律替代**：现有「shellcheck -S warning 全 .sh」是外部客观 gate——py 化后由 **ruff** 承接（验收③），否则丢失"外部客观 gate"纪律（分析报告 §9）。ruff 检查范围 = **全部 `agate/scripts/*.py`（既有 18 个 + 迁移新增）**，与 shellcheck 扫全部 *.sh 的"外部客观 gate 覆盖全代码"纪律一致。
- **ruff 规则集是 P2 交付物**：`pyproject.toml`（select 子集 + target-version=py38）由 P2 设计交付，**须让既有 18 个 py 在选定规则集下零违规**（现默认规则集实测 70 错误：UP032×35 / BLE001×9 / PLW1510×6 为主，ci-gate-backstop.py 14、agate-debt-check.py 14、agate-frontmatter-check.py 11、agate-state-yaml-check.py 7）。既有 py **不改功能**，但允许加注释/极小调整（不改变行为）以满足规则集；**P1 只声明此边界，不列具体调整**。
- **既有 18 个 py 的行为兼容**：不被本任务破坏（它们的调用方 sh 迁移后行为必须与现状等价）。
- **升级兼容**：30 个脚本改名/删档对直接调用脚本的用户是**破坏性变更**，必须列 UPGRADING 章节（分析报告 §7「文档影响面」）。

### 2.6 测试维度（agate 特有隐含依赖）
- **count-tests 用例数不漂移**：受影响 bats 文件被修改时，`count-tests.sh` 口径（`^@test`）用例数不得减少（测试计划附录 A 对照）。
- **受影响专门断言文件**：5 个文件约 38 用例断言 sh/python 接口与 bash 行为（check-platform-assumptions / env-adapt-docs / agate-scripts-encoding / helpers-python / agate-workspace-resolve），需随迁移改断言（表 D）。
- **平台假设扫描器扩展 .py**（验收⑤前置）：现扫描器只扫 `.bats/.bash/.sh`，对 py 失明——**必须先扩展规则集覆盖 .py**，否则验收⑤是空洞验收。
- **BDD-6 前置验证**：`When` 的 `agate/scripts/*.py` 含 18 个既有 py，其扫描洁净度未验证——**P2 须先行对既有 18 个 py 跑扩展后的扫描器**确认洁净度（或列出预期违规并规划处理），再谈迁移后零命中；否则迁移后首扫既有 py 违规会把"迁移引入的违规"与"历史存量"混淆（评审观察项 2）。

## 3. 影响面映射表（核心交付）

### 表 A：30 个 sh 全量清单

> 分类口径：**纯 bash** = 不调用 py（分析报告 §2.1 的 11 个）；**混合** = 已调 py（19 个）。行数按当前 worktree 实测。

| # | 脚本 | 行数 | 分类 | source 的函数库 | 调用的 py | git 调用 | 被谁调用/source | 批次 |
|---|------|------|------|----------------|-----------|---------|----------------|------|
| 1 | agate-archive-stale-outputs.sh | 62 | 纯 bash | — | — | — | 被 check-state-transition.sh 引用输出清单（文本耦合）；agate-retreat-to.sh 调 | 1 |
| 2 | agate-capture-env-baseline.sh | 112 | 混合 | gate-result.sh | agate-read-p5-commands.py、agate-json-get.py(×6) | rev-parse | — | 2 |
| 3 | agate-changes.sh | 150 | 纯 bash | — | —（grep 模式含 `.py` 路径） | describe/fetch/tag/log/diff | agate-summary.sh 文档引用 | 1 |
| 4 | agate-extract-context.sh | 187 | 纯 bash | — | — | — | — | 1 |
| 5 | agate-inject-card.sh | 45 | 混合 | — | agate-card-inject.py | — | → 调 agate-next-card.sh | 2 |
| 6 | agate-migrate-workspace.sh | 166 | 纯 bash | agate-workspace-resolve.sh | — | mv/commit/diff | orchestrator-template.md 引用 | 1 |
| 7 | agate-next-card.sh | 83 | 纯 bash | — | — | — | agate-inject-card.sh / pre-commit-gate.sh 调 | 1 |
| 8 | agate-render-dispatch-prompt.sh | 162 | 纯 bash | — | — | — | — | 1 |
| 9 | agate-retreat-to.sh | 73 | 混合 | — | agate-state-get.py、agate-retreat-state.py | diff/commit | — | 2 |
| 10 | agate-summary.sh | 97 | 纯 bash | — | —（存在性检查 ci-gate-backstop.py） | describe/branch/rev-parse/log | — | 1 |
| 11 | agate-workspace-resolve.sh | 57 | 混合（函数库） | — | — | — | 被 pre-commit-gate/check-debt/agate-migrate-workspace source + ci-gate-backstop.py subprocess | 0 |
| 12 | check-changelog.sh | 40 | 混合 | — | agate-changelog-unreleased.py | — | pre-commit-gate.sh 调 | 1 |
| 13 | check-debt.sh | 82 | 混合 | agate-workspace-resolve.sh | agate-debt-check.py | log | — | 2 |
| 14 | check-frontmatter.sh | 42 | 混合 | — | agate-frontmatter-check.py | — | pre-commit-gate.sh 调 | 1 |
| 15 | check-gate.sh | 488 | 混合 | — | agate-md-field-get.py(×7)、agate-gate-missing-cmds.py、agate-gate-p5-count.py | diff/rev-parse/tag | pre-commit-gate.sh 调；ci-gate-backstop.py subprocess | 2 |
| 16 | check-p6-evidence.sh | 177 | 混合 | — | agate-md-field-get.py、agate-image-check.py | — | pre-commit-gate.sh 调 | 2 |
| 17 | check-p6-format.sh | 106 | 纯 bash | — | —（注释引用 frontmatter-check 语义） | — | pre-commit-gate.sh 调（`--fix`/`--check`） | 1 |
| 18 | check-p6-provenance.sh | 274 | 混合 | — | agate-md-field-get.py、agate-vision-blocker.py、agate-evidence-consistency.py | — | pre-commit-gate.sh 调 | 2 |
| 19 | check-platform-assumptions.sh | 113 | 混合 | — | —（自身是扫描器，扫 `.py` 目标模式 R2） | — | CI 调（2 处） | 1 |
| 20 | check-pruning.sh | 152 | 混合 | — | agate-md-field-get.py | diff | pre-commit-gate.sh 调 | 2 |
| 21 | check-retrospective.sh | 50 | 混合 | — | agate-state-get.py | — | pre-commit-gate.sh 调 | 2 |
| 22 | check-scope-resolved.sh | 63 | 混合 | — | agate-md-field-get.py | — | pre-commit-gate.sh 调 | 2 |
| 23 | check-state-transition.sh | 123 | 混合 | — | agate-state-get.py | show/diff | pre-commit-gate.sh 调；agate-retreat-to.sh grep MAX_RETRY_MAP（文本耦合） | 1 |
| 24 | check-state-yaml.sh | 26 | 混合 | — | agate-state-yaml-check.py | — | pre-commit-gate.sh 调 | 1 |
| 25 | check-tdd-red.sh | 216 | 混合 | gate-result.sh | agate-read-gate-commands.py、agate-json-get.py(×12) | — | — | 2 |
| 26 | commit-msg-self-gate.sh | 37 | 纯 bash（hook） | — | —（grep 模式含 `*.py` 触发面） | diff | install-hook.sh 安装 | 3 |
| 27 | gate-result.sh | 105 | 混合（函数库） | — | agate-json-get.py、agate-state-get.py | rev-parse/diff | 被 3 个脚本 source（表：capture-env-baseline / check-tdd-red / pre-commit-gate） | 0 |
| 28 | install-hook.sh | 93 | 纯 bash | — | — | rev-parse | 安装 3 hook + 写 `.agate-root` 标记 | 3 |
| 29 | pre-commit-gate.sh | 404 | 混合（hook 入口） | gate-result.sh、agate-workspace-resolve.sh | agate-state-get.py | 密集 | hook 入口；bash 调 12 个子脚本（见 §3.2） | 3 |
| 30 | pre-push-gate.sh | 28 | 纯 bash（hook） | — | — | diff | hook | 3 |

**补充事实**（供 P2 估算）：bash 特性依赖极浅——`[[ ]]` 7 个脚本、数组 5 个、`readarray` 1 个、`local` 12 个、**关联数组 0 个**；14 个脚本调 git；既有 py 18 个（2293 行）。

### 3.1 pre-commit-gate.sh（404 行）调度的子脚本链（迁移后调度对象从 sh → py）

`pre-commit-gate.sh` 经 `bash "$AGATE_ROOT/scripts/xxx.sh"` 调 12 个子脚本：check-state-yaml.sh、check-state-transition.sh、check-frontmatter.sh、check-p6-format.sh、check-gate.sh、check-p6-provenance.sh、check-pruning.sh、check-scope-resolved.sh、agate-next-card.sh、check-retrospective.sh、check-changelog.sh、check-p6-evidence.sh。

→ **隐含需求**：薄壳化后这些子脚本的调用路径必须全部改写为 py 调用（同一调度逻辑、同一 exit code 传递语义）。

### 表 B：文档引用映射（阶段一必要的引用同步）

> 范围 = dispatch-context 指定的 in-scope 文档；docs/plans、docs/reviews 等历史文档**不做全量重写**（归 TAG0011）。

> 迁后目标约定（与表 C 命名一致）：非 hook 脚本**同名换后缀**（`check-gate.sh` → `check-gate.py`，最终命名 P2 定）；仅 3 个 hook 入口保留 sh 薄壳（pre-commit-gate.sh / commit-msg-self-gate.sh / pre-push-gate.sh）；install-hook.sh **一并 py 化**（→ install-hook.py，安装器非 hook 入口，无 shebang 解析硬约束，见 BDD-4）；`count-tests.sh`/`check-windows-smoke.sh` 属 `tests/scripts/`，不在迁移范围（保持 sh）。

| 文档 | 引用的 `.sh`（次数，2026-08-14 逐次实测） | 迁移后目标 |
|------|------------------------------------------|-----------|
| agate/dispatch-protocol.md | check-gate.sh(6)、check-p6-provenance.sh(4)、agate-inject-card.sh(3)、check-state-transition.sh(2)、check-p6-evidence.sh(2)、check-tdd-red.sh(1)、check-scope-resolved.sh(1)、check-p6-format.sh(1)、agate-archive-stale-outputs.sh(1)、agate-retreat-to.sh(1) | 同名换后缀 |
| agate/orchestrator-template.md | agate-workspace-resolve.sh(2)、install-hook.sh(1)、agate-summary.sh(1)、agate-migrate-workspace.sh(1)、check-gate.sh(1)、agate-inject-card.sh(1) | 同名换后缀（install-hook.sh → install-hook.py） |
| agate/git-integration.md | check-gate.sh、check-p6-provenance.sh（文字提及，无 `scripts/` 前缀） | 同名字符串同步 |
| agate/platform-notes.md | install-hook.sh、check-p6-provenance.sh、check-gate.sh、agate-summary.sh（Windows 章节 5 处 `.sh` 引用 + `bash install-hook.sh` + 复制模式前提）+「25 个 .sh 无法运行」限制 | Windows 章节需重写（py 化后"无 bash 环境"成为可行选项）；限制表述更新 |
| agate/UPGRADING.md | install-hook.sh(3)、agate-summary.sh(3)、check-gate.sh(3)、check-p6-evidence.sh(1)、check-debt.sh(1)、pre-commit-gate.sh(1)、check-platform-assumptions.sh(1)、agate-migrate-workspace.sh(1) | **新增本版本迁移章节**：30 个脚本改名/删档破坏性变更逐条列（分析报告 §7 强制项）；脚本引用同步 |
| agate/WORKFLOW.md | check-gate.sh(7)、check-p6-provenance.sh(3)、check-p6-evidence.sh(2)、check-pruning.sh(2)、check-tdd-red.sh(1)、check-scope-resolved.sh(1)、check-state-transition.sh(1)、check-changelog.sh(1)、check-state-yaml.sh(1)、check-retrospective.sh(1)、agate-workspace-resolve.sh(1)、pre-commit-gate.sh(1) | 同名换后缀；pre-commit-gate.sh 保留薄壳 sh |
| agate/state-machine.md | check-tdd-red.sh(6)、check-gate.sh(5)、check-p6-provenance.sh(2)、check-state-transition.sh(2)、check-scope-resolved.sh(1)、check-pruning.sh(1) | 同名换后缀 |
| agate/SETUP.md | agate-summary.sh(4)、install-hook.sh(3)、agate-workspace-resolve.sh(3)、agate-next-card.sh(1) | 同名换后缀 + **pyyaml 强制安装说明**（当前 SETUP.md 无 pyyaml 安装步骤） |
| agate/phase-cards/P6-acceptance.md | check-p6-format.sh(5) | 同名换后缀 |
| agate/assets/templates/handoff-template.md | pre-commit-gate.sh(1)、count-tests.sh(1)、agate-summary.sh(1)、agate-workspace-resolve.sh(1) | pre-commit-gate.sh 保留薄壳 sh；count-tests.sh 不在迁移范围；其余同名换后缀 |
| agate/assets/templates/task-files.md | check-tdd-red.sh(3)、check-state-yaml.sh(1)、check-p6-provenance.sh(1)、check-scope-resolved.sh(1) | 同名换后缀 |
| agate/assets/templates/tech-debt-template.md | check-debt.sh(3) | 同名换后缀 |
| agate/LIMITATIONS.md | check-p6-provenance.sh(3)、check-gate.sh(3)、check-p6-evidence.sh(1)、check-pruning.sh(1) + 局限 6「pyyaml 可选」表述 | 同名换后缀；局限 6 更新为 pyyaml 强制依赖 |
| agate/scripts/README.md | 全部脚本清单表（.sh/.py 分类） | 重写清单 |
| .github/workflows/protocol-tests.yml | shellcheck `*.sh`（Linux+Win）、check-platform-assumptions.sh(2)、ci-gate-backstop.py、check-windows-smoke.sh | shellcheck 收敛到保留薄壳（3 个 hook）+ 新增 ruff job + 扫描器调用目标同步（CI 详细同步归 TAG0011，但**本阶段能跑的 gate 目标**须在此改） |

> 计数口径：`rg -o` 逐次实测（同行出现多次计多次），与评审 §4 表 B 逐文档数据逐组件核对一致。LIMITATIONS.md 的 check-p6-provenance.sh 在第 118 行同行出现两次——按行口径计 3 次（与评审一致）、逐次口径计 4 次，两口径差异不影响 P4 引用同步。

### 表 C：consistency CHECK 8/9 锚点关键字映射（sh 路径 → py 路径 → 保留关键字）

> 迁移命名按**同名换后缀**计（check-gate.sh → check-gate.py，最终命名 P2 定）；hook 3 个（pre-commit-gate / commit-msg-self-gate / pre-push-gate）保留 sh 薄壳，锚点可继续命中 sh 路径。
> 两方案（保关键字 or 改锚点表）可混合：关键字必须存活在 py 中；锚点表的 script 路径随最终命名同步改。

**CHECK 8（V06_KEYWORD_ASSERTIONS）**

| 关键字 | 原 sh 路径 | 迁后路径 | 保留关键字 |
|--------|-----------|---------|-----------|
| DESIGN_GAP | agate/scripts/check-gate.sh | check-gate.py | DESIGN_GAP |
| P2 不可裁剪 | agate/scripts/check-pruning.sh | check-pruning.py | P2 不可裁剪 |
| --cached | agate/scripts/check-gate.sh | check-gate.py | --cached |
| --cached | agate/scripts/check-pruning.sh | check-pruning.py | --cached |

**CHECK 9（SCRIPT_ALIGNMENT_ANCHORS，涉 sh 条目全量）**

| 锚点 desc | 原 sh 路径 | 迁后路径 | 保留关键字 |
|-----------|-----------|---------|-----------|
| P2 不可裁剪（design_trivial 可简化） | check-pruning.sh | check-pruning.py | P2 不可裁剪 |
| 裁剪 P3 条件（risk_level） | check-pruning.sh | check-pruning.py | risk_level |
| P6 不可裁剪 | check-pruning.sh | check-pruning.py | P6 不可裁剪 |
| 裁剪 P7 coupling_checklist | check-pruning.sh | check-pruning.py | coupling_checklist |
| 裁剪 P7 条件（源码文件数） | check-pruning.sh | check-pruning.py | SOURCE_FILE_COUNT |
| 裁剪 P8 条件（internal_only） | check-pruning.sh | check-pruning.py | internal_only |
| 重试上限检查（MAX_RETRY） | check-state-transition.sh | check-state-transition.py | MAX_RETRY |
| 回退跳变检测 | check-state-transition.sh | check-state-transition.py | diff、phase_num |
| PROD_TOUCHED 检测 | pre-commit-gate.sh | **保留薄壳 sh** | PROD_TOUCHED、PROD_NOT_TOUCHED |
| NEED_CONFIRM 三值声明 | check-gate.sh | check-gate.py | NEED_CONFIRM、NO_NEED_CONFIRM、SUGGEST |
| SCOPE+ 追踪 | check-scope-resolved.sh | check-scope-resolved.py | SCOPE_RESOLVED |
| DESIGN_GAP 配对 | check-gate.sh | check-gate.py | DESIGN_GAP |
| P6 evidence UI 检查 | check-p6-evidence.sh | check-p6-evidence.py | ui_affected |
| P6 截图去重（md5） | check-p6-evidence.sh | check-p6-evidence.py | md5、去重 |
| P6 provenance 审计 | check-p6-provenance.sh | check-p6-provenance.py | EVIDENCE_DIR |
| 复盘提醒 | check-retrospective.sh | check-retrospective.py | retries |
| P8 CHANGELOG 检查 | check-changelog.sh | check-changelog.py | CHANGELOG |
| state.yaml 格式校验（.sh 入口） | check-state-yaml.sh | check-state-yaml.py | state.yaml |
| TDD 红灯检查 | check-tdd-red.sh | check-tdd-red.py | formatter、pytest |
| P2 agent=main 硬拦截 | check-gate.sh | check-gate.py | agent=main |
| P1 review agent≠main 检查 | check-gate.sh | check-gate.py | P1、agent=main |
| P7 DESIGN_GAP_REVIEWED | check-gate.sh | check-gate.py | DESIGN_GAP_REVIEWED |
| dispatch-context provenance 引用 | check-p6-provenance.sh | check-p6-provenance.py | dispatch-context |
| P6 格式自动修复 | check-p6-format.sh | check-p6-format.py | --fix、--check |
| EXIT_CODE 一致性检测 | check-p6-provenance.sh | check-p6-provenance.py | EXIT_CODE |
| pre-push alignment-review 阈值 | pre-push-gate.sh | **保留薄壳 sh** | AGATE_ALIGNMENT_REVIEW_THRESHOLD |
| 截图像素方差（M3.1） | check-p6-evidence.sh | check-p6-evidence.py | VARIANCE_WARNING、AGATE_SKIP_IMAGE_CHECKS |
| 截图 ahash（M3.2） | check-p6-evidence.sh | check-p6-evidence.py | AHASH_LIST、AHASH_DUPES |
| P1 BDD 编号格式 | check-gate.sh | check-gate.py | BDD-[0-9] |
| frontmatter schema 校验 | check-frontmatter.sh | check-frontmatter.py | frontmatter |
| tech-debt schema + 回退覆盖 | check-debt.sh | check-debt.py | debt、retreat |
| 平台假设静态扫描器 | check-platform-assumptions.sh | check-platform-assumptions.py | 平台假设、R1、R2 |

**check-protocol-consistency.py 自身的结构性同步点**：
1. `SCRIPT_ALIGNMENT_ANCHORS` 每条的 `script:` 路径 `.sh` → 新 py 路径（或保留薄壳）。
2. `V06_KEYWORD_ASSERTIONS` 的 rel_path 同步。
3. `GATE_SCRIPT_EXEMPT`：gate-result.sh 条目移除（函数库并入 agate_common.py）；**install-hook.sh 条目随 py 化移除**（install-hook.sh → install-hook.py，不再有 sh 豁免对象，见 BDD-4）；agate-changes.sh / agate-summary.sh 条目删除（脚本已 py 化）。
4. **`check_anchor_coverage` 的 glob 必须改为扫新的 py gate 脚本**（如 `check-*.py` + pre-commit-gate.py + ci-gate-backstop.py），否则反向覆盖检查空转（见 §2.5）。

### 表 D：受影响 bats 测试清单

> **两层影响**：
> - **机械调用面**（断言不变，改调用方式）：29 个 bats 文件 / 约 400 处 `bash $AGATE_SCRIPTS/*.sh` 运行点 → 随各脚本迁移改调 py。
> - **断言级变更**（专门断言 sh/python 接口与 bash 行为）：集中在以下 5 个文件 / 38 用例。

| 文件 | 用例数 | 需改什么断言 |
|------|--------|-------------|
| tests/scripts/check-platform-assumptions.bats | 14 | ①调用方式 `bash …check-platform-assumptions.sh` → 调 py（13 处 run）；②目录扫描扩展名过滤契约（`.bats/.bash/.sh`）须扩展 `.py`；③扫描器"本体无 GNU 专用特性（POSIX ERE / 无 grep -P）"断言需改为 py 语义（py 无 grep，改为正则引擎约束断言）；④自身"干净树"契约随 py 化重述 |
| unit/env-adapt-docs.bats | 9 | bdd-34（shellcheck `*.sh` 0 error）→ shellcheck 覆盖面收敛到保留薄壳 + 新增 ruff 断言；其余 8 个（bdd-23/24/25/16/26/27/33/32）断言不变 |
| unit/agate-scripts-encoding.bats | 2 | bdd-5（扫描 `*.py` encoding 守卫）覆盖面扩大为强守卫，断言逻辑可复用、覆盖率目标扩到迁移后全部 py；bdd-8（agate-state-get.py Linux ASCII 回归）不变 |
| unit/helpers-python.bats | 3 | bdd-17 断言 `python3 stub exit 127 + shim` 下 check-state-transition.sh 的失败回退行为——py 自举后不再依赖 bash shim，断言需重构（新语义：py 探测 + 失败回退）；bdd-13/15（detect_python helper）需评估是否随 py 化退役/保留 |
| unit/agate-workspace-resolve.bats | 10 | 全部 `run bash $AGATE_SCRIPTS/agate-workspace-resolve.sh`（10 处）→ 调 py；两行输出契约（`AGATE_WORKSPACE=`/`AGATE_TASKS_DIR=`）与 CRLF 剥离（bdd-18）断言保留（这是 py 版必须满足的行为契约） |

**其他联动测试文件**（调用面改、断言不变，随对应脚本批次同步）：check-gate.bats / check-gate-p1-review.bats / check-gate-p5-diff.bats / check-pruning.bats / check-state-transition.bats / check-state-yaml.bats / check-frontmatter.bats / check-changelog.bats / check-retrospective.bats / check-scope-resolved.bats / check-p6-evidence.bats / check-p6-format.bats / check-p6-provenance.bats / check-tdd-red.bats / check-tdd-red-formatter.bats / check-debt.bats（间接）/ agate-capture-env-baseline.bats / agate-archive-stale-outputs.bats / agate-extract-context.bats / agate-next-card.bats / agate-inject-card.bats / agate-card-inject.bats / agate-retreat-to.bats / agate-migrate-workspace.bats / agate-render-dispatch-prompt.bats / agate-summary（无专属测试）/ commit-msg-self-gate.bats（unit+integration）/ install-hook.bats / pre-commit-hook.bats / pre-push-hook.bats / protocol-alignment-review.bats / dispatch-context-card.bats / dispatch-context-warning.bats / consistency.bats（integration）/ ci-gate-backstop.bats / v060-*.bats（regression，直接调 check-gate/check-pruning 的用例）。

**约束**：改这些 bats 文件时 `count-tests.sh`（`^@test` 口径）用例数不得减少（测试计划附录 A 对照）；`tests/scripts/check-windows-smoke.bats` 代表用例随更新自动生效，机制不动。

### 表 E：迁移批次划分建议（按依赖，每批全量 bats 绿）

| 批次 | 内容 | 依赖前置 | 每批验证 |
|------|------|---------|---------|
| **批次 0 — 公共库** | `gate-result.sh` + `agate-workspace-resolve.sh` → `agate_common.py`（write_gate_result / read_state_phase / 工作区解析 / .agate-root 恢复工具）；**同步** ci-gate-backstop.py 改 python 调用（消除对这两个 sh 的 bash subprocess） | 无（一切依赖它） | agate-workspace-resolve.bats(10) + helpers-python.bats(3) + ci-gate-backstop.bats 改断言后绿 |
| **批次 1 — 自足叶节点（13）** | check-changelog、check-frontmatter、check-state-yaml、check-p6-format、check-scope-resolved、agate-archive-stale-outputs、agate-extract-context、agate-next-card、agate-render-dispatch-prompt、agate-summary、agate-changes、agate-migrate-workspace、**check-platform-assumptions**（含扩展规则集覆盖 `.py`） | 仅需批次 0（migrate-workspace 用 workspace 解析；archive 被 retreat 依赖但自身无依赖） | 逐脚本迁移 + 对应 bats 改调用后全量绿 |
| **批次 2 — 依赖 py 工具/库的复合（11）** | check-state-transition、check-retrospective、check-pruning、check-debt、check-tdd-red、check-gate、check-p6-evidence、check-p6-provenance、agate-capture-env-baseline、agate-retreat-to、agate-inject-card | 批次 0（函数库）+ 批次 1（retreat-to 依赖 archive + state-transition 的 MAX_RETRY_MAP 提取；inject-card 依赖 next-card） | 每迁一个跑全量 bats；check-gate 是最大单文件（488 行）宜拆子任务逐步验证 |
| **批次 3 — hook 链（4）** | pre-commit-gate 薄壳化（shebang + AGATE_ROOT 自定位 + 复制模式 `.agate-root` 恢复 + python 探测回退 + exec py）+ commit-msg-self-gate + pre-push-gate + install-hook | 批次 2 全部完成（pre-commit 调度的 12 个子脚本已 py 化） | pre-commit-hook.bats / pre-push-hook.bats / commit-msg-self-gate.bats / install-hook.bats / protocol-alignment-review.bats 全绿 |
| **批次 4 — 收尾（0 ERROR 门槛）** | consistency.py 锚点表路径同步（表 C 结构性同步点）+ 文档引用同步（表 B）+ SETUP.md pyyaml 强制化 + UPGRADING 新章节 + scripts/README.md 重写 + CI（shellcheck→ruff、扫描器调用） | 批次 0-3 | consistency `--strict` 0 ERROR；ruff 0 error；全量 bats 绿；Windows 冒烟绿 |

**批次依赖图**：批次 0 → {批次 1, 批次 2}；批次 1 → 批次 2（部分）；批次 2 → 批次 3；批次 0-3 → 批次 4。批次内部逐脚本迁移、每步全量 bats（不做批量重写——P0「测试回归」约束）。

## 4. BDD 验收条件

> 每条独立可二值判定（PASS/FAIL）。覆盖分析报告 §9 的 5 条验收标准 + 硬约束。

### 迁移完整性
#### BDD-1: 全量 bats 测试全绿（验收①）
- Given 阶段一完成（30 个 sh 的 bash 逻辑已迁移，bats 测试改为调 py）
- When 运行 `bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/`
- Then 全部用例 PASS（0 FAIL、0 error），且 `count-tests.sh` 口径用例数不减少

#### BDD-2: consistency 0 ERROR（--strict）（验收②）
- Given py 版脚本保留表 C 锚点关键字（或锚点表已同步）
- When 运行 `python3 agate/scripts/check-protocol-consistency.py --strict`
- Then exit 0，无 ERROR 无 WARNING

#### BDD-3: ruff 静态检查覆盖全部 agate/scripts/*.py（验收③）
- Given 全部产品逻辑已为 .py，且 P2 已交付 `pyproject.toml` 规则集（select 子集 + target-version=py38），使既有 18 个 py 在选定规则集下可过（边界见 §2.5）
- When 运行 `ruff check agate/scripts/*.py`（按 P2 交付的 pyproject.toml 规则集）
- Then exit 0，无 error 级违规

#### BDD-4: shellcheck 覆盖面收敛到保留 sh 薄壳
- Given 非 hook 脚本已 py 化（install-hook.sh 一并 py 化 → install-hook.py，见 §2.5 与表 B）
- When 运行 `shellcheck -S warning` 扫描 `agate/scripts/*.sh`
- Then exit 0，且受扫 `.sh` 文件集合与 3 个保留 hook 薄壳（pre-commit-gate.sh / commit-msg-self-gate.sh / pre-push-gate.sh）一致——install-hook.sh 不属保留薄壳

### 平台与硬约束
#### BDD-5: Windows CI 冒烟通过（验收④）
- Given CI Windows matrix 执行冒烟子集
- When 运行 `check-windows-smoke.sh` 选取的代表用例（每文件第 1 个 + 平台敏感关键词用例）
- Then 全部代表用例 PASS，无平台机制（复制模式/CRLF/编码/py 探测）失败

#### BDD-6: 平台假设扫描器扩展覆盖 .py（验收⑤）
- Given 扫描器规则集已扩展覆盖 `.py`，且 **P2 已先行对既有 18 个 py 跑扩展后的扫描器确认洁净度（或列出预期违规并规划处理）**（前置验证见 §2.6）
- When 对 `agate/tests/` 全树 + 迁移后 `agate/scripts/*.py` 运行 check-platform-assumptions
- Then exit 0（无 Unix 假设命中）；且含 R1-R5 假设的 `.py` fixture 能被检出（非空转）

#### BDD-7: 新增 py 代码全部显式 encoding=utf-8
- Given 迁移产生的 py 代码
- When 运行 encoding 守卫（agate-scripts-encoding.bats bdd-5 逻辑）
- Then 无 `open()`/`read_text()` 缺 `encoding=` 的违规

#### BDD-8: py 代码兼容 Python 3.8+
- Given 迁移产生的 py 代码
- When 以 py38 target 静态检查（ruff `target-version=py38` 或等价扫描）
- Then 无 3.9+/3.10+ 专属语法（`match`、`str.removeprefix` 等）

#### BDD-9: hook 薄壳保留复制模式恢复且 exec 失败回退
- Given hook 经 install-hook.py 以复制模式安装（Windows 无符号链接，写入 `.agate-root`）
- When 运行 `.git/hooks/pre-commit`（sh 薄壳）
- Then 薄壳读取 `.agate-root` 恢复 AGATE_ROOT 并成功 exec py 主程序；且 python 不可探测/exec 失败时 **fail-closed 阻断**（输出明确 GATE ERROR + exit 非 0），绝不静默放行

[BASELINE_CHANGE: 主 Agent 2026-08-14 批准——BDD-9 Then 语义从"回退到保留的 sh 逻辑"改为"fail-closed 阻断（exit 非 0）"。理由：①P0-brief 已确认 pyyaml 从可选变强制依赖——python 是硬前提，Windows 无 python 环境本就无法运行 gate；②"保留 sh 逻辑 fallback"要求双份维护 gate 判定逻辑，违背本任务"逻辑全部 py 化"的宗旨（分析报告 §3.1）；③fail-closed（阻断 commit + 明确错误）是安全默认，静默放行才是被禁止的（原句"而非静默放行"语义保留）。影响面：Windows 无 python 用户的 commit 被阻断——UPGRADING 明示 python3+pyyaml 为强制安装项。]

#### BDD-10: CLI 输出契约与既有数据兼容
- Given 既有任务数据（`.state.yaml`、`P{n}-*.md`、`active-tasks.md`）与既有调用方（pre-commit hook、ci-gate-backstop）
- When 迁移后的 py 脚本按原接口读写/执行
- Then 数据格式与字段语义不变（读回值一致）；exit code 语义（0/1/2）与 `GATE ...:` 输出前缀保持；`AGATE_WORKSPACE=`/`AGATE_TASKS_DIR=` 两行解析输出不变

## 5. 待确认清单

[NO_NEED_CONFIRM]

无阻塞性待确认项。以下为有倾向的审计痕迹项（主 Agent 可直接采纳，不阻塞推进）：

- [SUGGEST: 非 hook 脚本迁移后**不保留** .sh 兼容薄壳（删档），理由：P0 范围锁定「30 个 sh → py + hook 保留薄壳」，且验收①「bats 调 py」确立测试直调 py；保留会留下双份维护负担]
- [SUGGEST: 迁移命名按**同名换后缀**（check-gate.sh → check-gate.py），理由：表 C 锚点路径、文档引用、bats 调用点的改动幅度最小（仅扩展名变化），一致性风险最低]
- [SUGGEST: hook 薄壳的 python 探测顺序 = `python3` → `python`（复用 detect_python helper 语义），理由：Windows 命令名是 python，Linux 是 python3，二者都要覆盖]
- [SUGGEST: ruff 以 CI 独立 job 形式接入（不做成 pre-commit hook 子步骤），理由：避免拖慢项目侧 pre-commit 且与现有「外部客观 gate」纪律一致（shellcheck 同样是独立 CI job）]
- [SUGGEST: check-platform-assumptions 的扩展名过滤新增 `.py` 后保留 `.bats/.bash/.sh` 不删，理由：helpers/ 与薄壳仍是 shell，需要继续受扫]

## 6. 裁剪说明 + 能力声明

- **risk_level: high**——影响面横跨协议文档、hook 链、dispatch、consistency、CI 全链；分析报告 §7 风险表定级「高」；P2 须走完整设计评审（C8 域多角色）。
- **phases: [P1, P2, P3, P4, P5, P6, P7, P8]**——无裁剪。P0-brief 已确认「走完整 task」；P7 一致性不可裁（表 C 锚点跨文件核对 + packages 交叉验证）；P8 发布必须执行（UPGRADING 破坏性变更章节 + version badge + git tag）。
- **domains: [backend, cli]**——产品逻辑（backend）+ CLI 工具链（cli）。无 frontend/mcp/security 影响（agate 无 UI；无外部服务面）。
- **capability_requirements**：见文件头 frontmatter。ruff（available）+ Windows CI（available）均不阻塞；`requires_minimal_validation: true`（Windows 真机行为本地无法验证，P2 architect 须产出 `minimal_validation:` 块）。
- **P1 基线保护**：本文件为需求基线，后续阶段不直接修改；确需变更走 `[BASELINE_CHANGE: 理由]` + 主 Agent 批准流程。
