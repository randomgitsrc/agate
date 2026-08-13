---
phase: P4
task_id: TAG0004-env-adaptation
type: implementation
parent: P2-design.md
trace_id: TAG0004-P4-20260813
status: draft
created: 2026-08-13
agent: implementer
---

implementation_dir: `agate/`

# P4 实现记录 — 组 3b（Q1/Q2/Q5/其他-a/其他-c/CI）

> 组 3b 并行实现，只改本组文件。13 py（组 3a）、sh gate 脚本（组 1/2）不动。
> 自查已跑：相关 .bats 全绿 + consistency --strict 0 ERROR + shellcheck 0 error。自查 ≠ P5 gate。

## 改动清单（组 3b 全部落盘）

| BDD | 文件 | 改动 |
|-----|------|------|
| BDD-21/22 | `agate/scripts/agate-next-card.sh` | Q1：新增 `lower_drive()` + `rel_card()`，前缀剥离先试直接剥离（Linux 字节不变），失败再归一化双方（`tr '\\' '/'` 统一斜杠 + 盘符小写）后剥离 |
| BDD-18 | `agate/scripts/agate-workspace-resolve.sh` | 其他-a：L33 `.agate.env` 值取值后追加 `tr -d '\r'` |
| BDD-20 | `agate/scripts/agate-render-dispatch-prompt.sh` | 其他-c：新增 `esc_repl()` 转义 `&`/`\|`/`/`/`\`，全部 13 个 sed 替换串改用转义值 |
| BDD-23/24/25 | `agate/phase-cards/P{1,2,3,4,6,7,8}-*.md` | Q2：7 张卡"更新 .state.yaml phase="旧写法改为规则 2 语义（git add 时 phase 保持本阶段 + 下一阶段推进随产出 commit），参照 P5 卡 |
| BDD-26 | `agate/SETUP.md` | Q5：新增「Windows 环境适配要点」章节，覆盖 AGATE_ROOT Unix 路径 / PATH 注入 / Git Bash 执行 hook / PYTHONUTF8=1 / CRLF-core.autocrlf 5 项 |
| BDD-27 | 仓库根 `.gitignore` | Q5：增 `dist/` 忽略 + `!version.txt` 白名单 |
| BDD-33 | `.github/workflows/protocol-tests.yml` | CI：bats/shellcheck/consistency/gate-backstop 四 job 全部加 `strategy.matrix.os: [ubuntu-latest, windows-latest]` + Windows 分支安装步骤（bats-core clone / shellcheck zip 下载 / `python` 命令适配） |

## 实现要点

### Q1 — agate-next-card.sh 路径归一化（候选 7A）

- 顺序：`rel_card` 先试 `rel="${file#$root/}"`；若 `rel == file`（剥离失败，Windows 盘符/反斜杠/大小写场景），归一化双方后剥离。
- 归一化用 `tr '\\' '/'` + `lower_drive`（`${p:0:1}` 取盘符 + `tr 'A-Z' 'a-z'` 小写），**未用 `sed '\L'`**（GNU 专有，P2 观察项 3 / BDD-21 断言只查输出相对路径，不锁实现）。
- Linux 字节不变：直接剥离优先，`CARD_FILE` 恒在 `AGATE_ROOT` 下 → Linux 永不进归一化分支（bdd-22 全量 hash 回归验证）。

### Q2 — 7 张 phase-cards 规则 2 对齐（候选 8A，纯文档）

- 每张卡的推进步骤改为：`git add`（含 .state.yaml）→ ⚠️ 注"phase 保持本阶段，不提前写下一阶段——phase = 本 commit 的产出阶段"→ commit（标注产出含哪些文件）→ 追加"下一阶段推进随下一阶段产出 commit 一起"。
- 与 `git-integration.md` 规则 2（L31-35）及 P5 卡（L14-20）措辞同构；不改 commit 顺序、不改任何 gate 逻辑（bdd-24 回归守卫绿）。
- 触发 SELF-GATE（phase-cards/*.md 变更）→ commit message 需 `self-gate-review:`。

### Q5 — SETUP.md Windows 章节 + .gitignore 预设（候选 9A）

- SETUP.md 在现有「Windows（无 WSL，用 Git for Windows）」小节后新增独立「Windows 环境适配要点」，5 项覆盖对齐 BDD-26；与 `platform-notes.md`「Windows 原生」章节交叉引用、不矛盾。
- .gitignore 追加 `dist/`（发布产物忽略）+ `!version.txt`（版本文件白名单，防误忽略），满足 BDD-27。

### 其他-a — .agate.env CR 剥离（候选 13A）

- 在 sed 取值管道后加 `| tr -d '\r'`，剥离 Windows CRLF 编辑残留；`|| true` 语义保持（无匹配时不报错）。

### 其他-c — render-dispatch-prompt sed 转义（候选 15A）

- 新增 `esc_repl()`：`sed 's/[&|/\\]/\\&/g'` 把替换串里的 `&`（整体匹配引用）、`|`（分隔符）、`/`、`\` 全部前置转义；13 个替换值先转义再用进 sed。
- 测试 `AGATE_ROOT=…/x&y/agate` 下 `{agate_root}` 无残留、字面路径正确插入（bdd-20 绿）。

### CI — windows-latest matrix（候选 12A）

- 四 job 统一 `strategy: fail-fast: false + matrix.os: [ubuntu-latest, windows-latest]`；
- Windows 分支：bats 用 `git clone --branch v1.10.0 bats-core` 后加 PATH；shellcheck 下载 v0.10.0 zip 解压加 PATH；consistency/gate-backstop 用 `python`（Windows 无 `python3`）；`defaults.run.shell: bash`（Git Bash 语义，保证 `$GITHUB_PATH` 写法跨平台一致）。

## 自查结果（2026-08-13）

| 检查 | 结果 |
|------|------|
| `bats agate/tests/unit/agate-next-card.bats` | 全绿（含 bdd-21/22） |
| `bats agate/tests/unit/agate-workspace-resolve.bats` | 全绿（含 bdd-18） |
| `bats agate/tests/unit/agate-render-dispatch-prompt.bats` | 全绿（含 bdd-20） |
| `bats agate/tests/unit/env-adapt-docs.bats` | 全绿（含 bdd-23/24/25/26/27/33） |
| 全量 unit | 607 通过 / 1 失败（bdd-14 M6 CRLF，属组 1/3a check-gate.sh 范围，非本组） |
| integration / regression / sanity | 84 / 全绿 / 6 全绿 |
| `python3 agate/scripts/check-protocol-consistency.py --strict` | 0 ERROR |
| `shellcheck -S warning`（本组 3 个 sh） | 0 error |
| `bash agate/tests/scripts/count-tests.sh` | 708 用例，无漂移警告 |

## 门槛对照

- ✅ P4-implementation-group3b.md 存在且含 Header + implementation_dir（`agate/`）
- ✅ Q1/Q2/Q5/其他-a/其他-c/CI 修复已落盘（实际 diff，见 git status）
- ✅ BDD-18/20/21/23/26/27/33 红灯已变绿；BDD-22/24/25 回归守卫保持绿
- ✅ consistency --strict 0 ERROR（worktree 自己的脚本）
- ✅ 无 SCOPE_GAP 缺口声明（本组 7 文件全部在 dispatch-context 声明的范围内，无遗漏）

## 状态标记

`[PROD_NOT_TOUCHED]` 本阶段仅改 worktree 内代码/文档并跑测试，未接触任何生产环境。

> 注：仓库根的 `.state.yaml` 已由主 Agent 并行任务更新；本组不负责 check-gate.sh（组 1）、13 py（组 3a）、check-tdd-red（组 2）等文件的改动。
