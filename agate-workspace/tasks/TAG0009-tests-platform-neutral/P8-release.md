---
phase: P8
task_id: TAG0009-tests-platform-neutral
type: release
parent: P7-consistency.md
trace_id: TAG0009-tests-platform-neutral-P8-20260813
status: draft
created: 2026-08-13
agent: implementer
---

# P8 发布准备记录 — agate 测试套件平台无关化（TAG0009）

> 合并发布模式（HANDOFF §8b）：TAG0005 与 TAG0009 同 worktree，合并为一次发布。
> 本文件是**发布计划文档**——声明 bump 计划 / debt_check / 临时资源清单 / 本任务 CHANGELOG 条目草稿。
> **不执行版本 bump、不 git commit/tag**（releaser 不执行；bump + tag + PR 由主 Agent 在 TAG0005 + TAG0009 都 READY 后统一执行）。

## bump_type

- **bump_type: minor**（v0.44.0 → **v0.45.0**，与 TAG0005 合并发布一次 bump）
- 判定依据（dispatch-context 约束 + AGENTS.md 版本发布节）：
  - TAG0009 为测试基建 + 新增静态扫描器 gate + CI 变更——**行为变化**（CI 新增 windows-latest bats + 平台假设扫描阻断），判 minor。
  - 与 TAG0005（同样 minor）合并后 v0.44.0 → v0.45.0，一次 bump、一个 tag、一个 PR。

## 受影响包（P2-design.md frontmatter `packages`）

| 包 | 涉及改动 | P4 提交 | 验证 |
|----|---------|--------|------|
| agate-tests | 24+1 文件测试侧 python3→`$PYTHON`；install-hook/pre-push-hook/agate-next-card/check-scope-resolved/ci-gate-backstop 平台分支；fixtures.bash 新增 detect_python/create_python_shim_bin/SHELLCHECK 探测；新增 helpers-python.bats + check-platform-assumptions.bats；tests/README.md 计数表同步 | b1ba2c7 | P5 全量 bats 733 ok |
| agate-scripts | 新增 check-platform-assumptions.sh（静态扫描器 gate）；agate-extract-context.sh bc→awk（唯一产品脚本改动）；check-protocol-consistency.py SCRIPT_ALIGNMENT_ANCHORS 补扫描器锚点 | b1ba2c7 | P5 consistency --strict 0 ERROR + 扫描器零命中 |
| ci-workflow | protocol-tests.yml 新增 platform-scan job（matrix ubuntu+windows，Linux 阻断）+ bats job 增 windows-latest（含扫描器行为测试步骤） | b1ba2c7 | P5 shellcheck 0 error；Windows 分支 CI 最终确认（I7） |

> 合并发布时三个包随同一个版本 bump（agate 协议本体单版本号，非逐包独立版本）。

## 版本号变更确认（计划，非已执行）

- 当前版本：**v0.44.0**（README badge L6 + git tag v0.44.0，已核实；`git describe --tags --abbrev=0` = v0.44.0）
- 计划新版本：**v0.45.0**（合并发布时执行）
- 需更新的版本引用（合并发布时由主 Agent 执行，参考 AGENTS.md 版本发布节 + 版本引用文件清单）：
  - README.md version badge（L6 v0.44.0 → v0.45.0；L32 残留 v0.43.0 badge 建议一并核对，TAG0005 P8 已标记）
  - CHANGELOG.md `[Unreleased]` → `[0.45.0]`
  - UPGRADING.md 新增 v0.45.0 章节（含 CI required checks 更新提示——bats job 改 matrix 后 job 名带平台后缀，如 `bats (windows-latest)`，分支保护需同步）
- 本任务不执行，全部留待合并发布。

## debt_check

- **debt_check: none**
- 核对过程：读取 `agate-workspace/debt/tech-debt.md`——worktree 与主 checkout 中该文件均**不存在**（`agate-workspace/` 无 `debt/` 目录）。本任务 P1-P7 无 `source: retreat` 回退提交（git log 复核 TAG0009 8 个提交均为 P0-P7 阶段推进，无 retreat）、无未关闭 DEBT 条目登记（P4-implementation.md 仅 [DESIGN_GAP] readlink 决策——已 P7 REVIEWED 配对，非债务；[SCOPE+] 观察非阻塞）。无关注项，合法选项 `none`。

## 本任务变更摘要（CHANGELOG 草稿，供合并发布写入 CHANGELOG.md）

> 合并发布时主 Agent 将本节内容合并进 CHANGELOG.md 的 `[0.45.0]` 版本条目（与 TAG0005 条目并列）。

### 新增（TAG0009 测试套件平台无关化：测试平台无关原则落地 + 静态扫描器 gate）

- **静态扫描器 gate `check-platform-assumptions.sh`**：bash + POSIX ERE（无 GNU `-P` 特性，MSYS2 可跑），扫描 `agate/tests/` 全树 5 类 Unix 假设——R1 硬编码 PATH / R2 命令位置裸 python3（豁免 `command -v` 探测/env/shebang/@test/注释）/ R3 `[[ -L ]]` symlink 单平台断言 / R4 `/tmp` 逻辑路径（`$BATS_TEST_TMPDIR` 与行内 `# scan-exempt:` 标记豁免，标记仅豁免 R4）/ R5 bc 等 Unix-only 工具；任一命中 exit 1，零命中 exit 0。接入 CI 新增 `platform-scan` job（matrix ubuntu+windows，Linux 步骤阻断合并 / Windows 步骤证明扫描器双平台等价）
- **PYTHON 探测 helper**：fixtures.bash 新增 `detect_python`（`command -v python3 || command -v python`）+ 顶层导出 `PYTHON`，24+1 文件测试侧裸 python3 全部改为 `$PYTHON`（BDD-14，全树 R2 零命中）
- **harness PATH shim `create_python_shim_bin`**：10 个受影响 .bats 文件 setup 注入临时 bin 的 python3 包装器（内嵌真解释器绝对路径），兜底产品脚本内部裸 python3——41 例 script-side Windows 失败一次覆盖，17 个产品脚本零改动（候选 A 方案）
- **bc→awk**：`agate-extract-context.sh` P5 failed 求和 `bc 2>/dev/null || echo 0 | tail -1` → `awk '{s+=$1} END{print s+0}'`（POSIX 工具，消除管道优先级隐患，Windows Git Bash 自带）
- **bats job 增 windows-latest**：`.github/workflows/protocol-tests.yml` bats job 改 matrix `[ubuntu-latest, windows-latest]`（Windows 分支 bash shell + bats-core v1.11.0 + `PYTHONIOENCODING=utf-8`）——真 Windows CI 作最终确认（I7 supplementable，本地 Linux 全量覆盖各 Windows 分支模拟）

### 变更（TAG0009 批量修正存量平台假设，Linux 基线零回归）

- **PATH 硬编码移除**：check-tdd-red.bats 15 处 `PATH="/usr/bin:/bin"` 移除，改 `env -u PATH` 等平台无关构造（TD.1b exit `3 or 1`、TDD.F8 exit `3` 语义不变）
- **symlink 断言按平台分支**：install-hook.bats 2 处 + integration/pre-push-hook.bats 1 处 `[[ -L ]]`/`[ -L ]` 拆为 Linux 真软链（readlink 目标断言）+ Windows 复制模式（mock ln 用例，断言「复制/需重跑」升级提醒）两套，Linux 模拟覆盖 Windows 分支
- **`/tmp` 逻辑路径 → `$BATS_TEST_TMPDIR`**：agate-next-card.bats / check-scope-resolved.bats 2 处；4 处 vitest mock 输出样例文本保留原内容并加 `# scan-exempt:` 标记
- **bdd-21 setup 平台分支**：agate-next-card.bats 构造 MINGW/MSYS 用正斜杠 `C:/proj/agate`、其余字面反斜杠，双平台断言同一输出串
- **输出/编码健壮化**：ci-gate-backstop.bats 等行尾敏感断言匹配前 `tr -d '\r'` 归一化（CRLF 模拟命中）；含中文输出 python 工具文件级 `export PYTHONIOENCODING=utf-8` + 新增 cp1252 模拟用例（不 UnicodeEncodeError 崩溃）
- **shellcheck 名探测**：fixtures.bash 导出 `SHELLCHECK`（`command -v shellcheck || command -v shellcheck.exe`），bdd-34 调用 `${SHELLCHECK:-shellcheck} -S warning "$AGATE_ROOT"/scripts/*.sh`

### 测试（TAG0009 配套）

- 新增扫描器行为测试 `check-platform-assumptions.bats`（14 例：含假设/干净 fixture、目录扩展名过滤、`# scan-exempt:` 仅豁免 R4 不豁免 R1/R2/R3 负向用例）+ `helpers-python.bats`（detect_python 优先/回退/shim 不静默放行）+ cp1252 用例；count-tests.sh 总计 727，全量 bats 733 ok / 0 not ok
- 变更流程先红后绿（P3 commit 先行交付测试红灯，P4 commit 才首次创建扫描器实现，符合 AGENTS.md「先加失败测试再改」工作流）

### 文档

- tests/README.md 计数表按 count-tests.sh 实输出同步（含既有漂移修正 + helpers-python 新增行）；protocol-tests.yml 增加扫描器行为测试步骤

## 临时资源清单（releaser → 主 Agent READY 收尾交接）

本任务为测试基建 + 扫描器 + CI 变更，P4/P5/P6 阶段未启动任何临时服务/进程，未创建持久临时数据，未做开发安装。逐项核对：

- **临时服务/进程**：无（P4/P5/P6 自查均为 bats / shellcheck / consistency / 扫描器本地命令，无 debug server / daemon / 网络监听启动）
- **临时数据**：无持久临时数据。运行时 ephemeral 临时文件全部在 `$BATS_TEST_TMPDIR` 内（bats 每用例自建自清，含 `create_python_shim_bin` 的 `mktemp -d` shim bin），不落盘；P6-evidence/ 与 P5-test-results/ 为阶段产出物，属任务目录内正常产物，随任务归档，不需单独清理
- **开发安装**：无（未做 editable install / 全局包安装；bats 1.10 / python3 3.12+pyyaml / shellcheck 均为既有环境）
- **端口占用**：无（无网络监听服务）
- **工作区残留**：worktree `agate-TAG0005-0009` 本身为隔离开发环境，合并发布完成后由主 Agent 按常规流程处理（merge + 清理）

## 合并发布注意事项（主 Agent）

- bump 版本引用三处：README badge（L6 + L32 残留 v0.43.0）/ CHANGELOG / UPGRADING.md 新增 v0.45.0 章节（AGENTS.md 版本发布节固化清单）
- **CI required checks**：bats job 改 matrix 后 job 名带平台后缀（`bats (ubuntu-latest)` / `bats (windows-latest)`）、新增 `platform-scan` job——分支保护 required checks 需更新（UPGRADING.md v0.45.0 章节要写明，TAG0004 v0.44.0 有同类教训：4e597e9 补 job 固定 name）
- **P8 收尾检查项（协议一致性）**：本任务为 dogfooding（改造 agate 自身测试基建），需在干净 checkout 跑 `check-protocol-consistency.py`（或确认 CI consistency job 对本次 PR 通过）——扫描器/helper 改动可能被 `.worktrees` 路径过滤掩盖，本地 0 ERROR ≠ CI 0 ERROR（TAG0001 批 D4 教训）
- release PR 用普通 merge（`--no-ff`），禁 squash merge（`agate-summary.sh` 依赖 `git describe --tags`）
- 合并发布时重跑 P5 gate（bats 733 全绿 / consistency 0 ERROR / shellcheck 0 error / 扫描器零命中）确认 bump 后仍绿
- CHANGELOG 对照 `git log v0.44.0..HEAD --oneline` 无遗漏（TAG0005 提交 + TAG0009 8 个提交 341b679~5605e7c）
- `debt_check: none` 为合法选项，不阻断发布

## Lessons Learned

| 类别 | 教训 | 来源任务 | 日期 |
|------|------|---------|------|
| 测试 | **平台无关测试基建的价值与边界**：Linux 恰好满足多数 Unix 假设，导致 78 例 Windows 失败长期不可见。静态扫描器 gate（扫描测试树）使"测试平台无关"从文档原则变为可执行检查——但扫描器只覆盖测试树，产品脚本的真实 Windows 根治（17 文件 68 处裸 python3）仍须另立任务（TAG0010+），本轮仅用 harness shim 覆盖测试场景 | TAG0009 | 2026-08-13 |
| 测试 | **Linux 模拟可覆盖 Windows 分支**：cp1252 编码（PYTHONIOENCODING）、symlink 复制模式（fakebin ln→cp）、PATH 无 python3/无 bc（纯净 PATH stub）、shellcheck.exe 名探测均可在 Linux 显式模拟用例覆盖，真 Windows CI 降级为"最终确认"而非"必要兜底"——模拟用例是关键资产，Windows CI 只作兜底 | TAG0009 | 2026-08-13 |
| 架构 | **harness 思路（PATH shim）控制产品回归面**：候选 A 用"测试侧 PATH shim 包装器"而非改 17 个产品脚本，一次覆盖 41 例 script-side 失败且零产品回归风险——包装器必须内嵌真解释器绝对路径（避免 `command -v python3` 自解析循环）；把高风险改动隔离在测试 harness 而非扩散到产品层，是测试基建改造的可行模式 | TAG0009 | 2026-08-13 |

## 环境隔离

`[PROD_NOT_TOUCHED]`——本阶段仅读取 worktree 内产出文件与 git log/status 核验，未接触生产环境。
