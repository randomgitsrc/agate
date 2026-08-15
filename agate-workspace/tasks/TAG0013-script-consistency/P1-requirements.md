---
phase: P1
task_id: TAG0013-script-consistency
type: problems
parent: P0-brief.md
trace_id: TAG0013-P1-20260815
status: draft
created: 2026-08-15
agent: analyst
# ── v2.0 机器字段 ──
risk_level: medium
phases: [P1, P2, P3, P4, P5, P6, P7, P8]
packages: [agate-scripts, agate-tests, agate-protocol-docs, agate-consistency]
domains: [backend, cli]
capability_requirements:
  - need: python3 + pyyaml 运行环境
    why: 三个被测脚本（check-protocol-consistency.py / commit-msg-self-gate.py / check-retrospective.py）均为 Python，gate 与测试直接依赖
    available:
      - "系统 /usr/bin/python3（3.12.3，系统自带 pyyaml）"
      - "开发 venv ~/.venvs/agate-dev/（pyyaml + ruff）"
    status: available
  - need: pytest 测试运行器
    why: 现有测试套件为 pytest（749 用例全绿是回归底线），新增测试用例沿用同框架
    available:
      - "系统 python3 -m pytest 可跑（当前测试套件基线已验证）"
      - "开发 venv ~/.venvs/agate-dev/"
    status: available
  - need: ruff 静态检查
    why: py 代码变更后的静态检查（AGENTS.md 开发约定）
    available:
      - "~/.venvs/agate-dev/bin/ruff"
    status: available
---

# P1 需求基线 — agate 脚本一致性批（RM-AG0015 / RM-AG0017 / RM-AG0018 剩余）

> 本文件是 TAG0013 的需求基线（"活基线"）。后续阶段发现新隐含需求时由主 Agent 增补并标 `[SCOPE+ from Pn]`。
> 范围锁定：P0-brief 三条 issue（RM-AG0015 / RM-AG0017 / RM-AG0018 剩余）是全部范围，不扩。

---

## 1. 需求复述

### 1.1 RM-AG0015：新增 CHECK 10（协议文档脚本名引用漂移 gate）

**现状**：`check-protocol-consistency.py` 的 `REF_RE`（L238）只匹配 `docs/`、`assets/`、`scripts/` 前缀引用；
`agate/phase-cards/` 与 `agate/rules/` 下的脚本名引用**全部是裸名**（如 `check-gate.py`、`check-tdd-red.py`），
且这两个目录不在 `PROTOCOL_FILES`（L52-64）也不在 `PROTOCOL_DIRS`（L65）——现行正则完全匹配不上，
裸名脚本引用漂移**无 gate 兜底**。v0.46.0 的 phase-cards 26 处过时 `.sh` 引用已修但防复发手段缺失
（已登记 DEBT0001，source: retrospective）。

**缺陷**：脚本改名/退役后，协议文档里的裸名引用无人拦截，直到人工发现。

**期望行为**：
- 新增 **CHECK 10**：扫描**协议文档面**（扫描范围定义见 §4 开头，二选一定死为协议文档面）中
  的脚本名引用（裸名 + `scripts/` 相对路径 + `agate/scripts/`/`~/.agate/scripts/` 全路径），
  对照 `agate/scripts/` 下实际存在的脚本文件，报"引用了不存在的脚本"漂移。
- **增量检查**：只报新漂移，不误伤现有合法引用（实测当前协议文档面全部脚本名都能解析到真实文件，0 漂移）。
- `agate/phase-cards/` 与 `agate/rules/` 纳入 PROTOCOL 严格检查（`PROTOCOL_DIRS`），使必读卡的引用检查升级为 ERROR 级。
- **CHANGELOG.md 豁免 ERROR**：按叙事文件处理（NARRATIVE_DIRS 已含），至多 WARNING。

### 1.2 RM-AG0017：self-gate 触发面补 README.md / AGENTS.md

**现状**：`commit-msg-self-gate.py` 的 `_SELF_GATE_RE`（L38-40）匹配 `agate/scripts/*.sh|py`、
`agate/*.md`、`agate/*/*.md`、`SELF-GATE.md`——**不含仓库根级 `README.md` / `AGENTS.md`**。
（复盘原文称"SELF-GATE.md 不在触发面"是错误，实测正则包含它——只补 README/AGENTS。）

**缺陷**：改仓库根级协议文档（README/AGENTS 是协议文档体系的一部分）不触发 self-gate WARNING。

**期望行为**：`_SELF_GATE_RE` 扩展匹配 `README.md` / `AGENTS.md`；`CHANGELOG.md` **豁免**
（频繁变动，不应触发 self-gate 噪音）。

### 1.3 RM-AG0018 剩余：check-retrospective.py 登记提醒行

**现状**：`check-retrospective.py` main() 收集 retries_over / SCOPE+ / override 三类 warnings，
stderr 输出 `GATE RETRO: 建议复盘...`（L89-93），exit 0 不拦截。主体（DEBT0001 登记 + postmortem-template
核对行）已在 2026-08-15 完成。

**缺陷（剩余）**：复盘输出缺"新缺口登记 DEBT/roadmap"提醒——复盘发现了新问题但无引导去向。

**期望行为**：输出加一行"复盘发现的新缺口请登记 DEBT/roadmap"提醒（**纯提醒不拦截**，exit 0 不变）。

---

## 2. 隐含需求识别（每次过全维度）

- **数据/兼容（回归底线）**：Linux 749 pytest 全绿 + consistency 0 ERROR 是回归底线。CHECK 10 必须**增量**——
  当前协议文档面全脚本引用可解析，落地后不能产生新的 ERROR（否则 CI 直接红）。→ BDD-1
- **CHECK 2 / CHECK 3 相互作用**：phase-cards/rules 入 PROTOCOL_DIRS 后，`check_internal_refs`（CHECK 2）与
  `check_line_refs`（CHECK 3）会对它们按协议文件严格检查。实测 phase-cards/rules **无 `.md L\d+` 行号引用**
  （grep 0 命中），且其 `scripts/` 前缀引用（如有）均真实存在 → 入 PROTOCOL_DIRS 不会新增 CHECK 2/3 漂移。→ BDD-4
- **CHECK 9 锚点交互**：CHECK 10 是新增检查，不含脚本实现逻辑 → 不进 `SCRIPT_ALIGNMENT_ANCHORS`。
  但若 P4 把 CHECK 10 拆成独立脚本，则需走 CHECK 9 反向锚点覆盖（`check_anchor_coverage`）。→ 隐含项
- **REF_RE 与 CHECK 10 的关系**：REF_RE 是死链检查（引用路径不存在），CHECK 10 是脚本名漂移检查
  （裸名/路径引用对照 scripts/ 实际文件）。两者互补不重叠；CHECK 10 需处理"同名不同目录"场景
  （如 `count-tests.sh` 在 `agate/tests/scripts/`，若按 `agate/scripts/` 解析会误报）。
- **扫描范围与 docs/ 的处置**：CHECK 10 扫描范围定为**协议文档面**（不含 docs/ 与 agate-workspace/）——
  `docs/superpowers/`、`docs/guides/`、`docs/agents/`、`docs/notes/`、`docs/hardening-roadmap.md` 含
  退役 `.sh` 名引用（如 check-gate.sh），但它们是项目开发资料/叙事，非协议文件；不扫 = 无 ERROR。
  （若扫全仓 md，这些文件会 ERROR 破坏 BDD-1 的 0 漂移——这是选择协议文档面的决定性理由。）→ BDD-1/5
- **UPGRADING.md 整文件豁免**：UPGRADING 是对照表**之外**的散文行也含退役名
  （L105 check-windows-smoke.sh / L151 xxx.sh / L152 gate-result.sh + agate-workspace-resolve.sh /
  L153 check-windows-smoke.sh / L158 install-hook.sh）。表级豁免会让散文行 ERROR →
  **整文件豁免**（历史迁移文档，语义本就是"旧名对照新名"，名漂移检查无意义）。→ BDD-3
- **scripts/README.md 退役名豁免**：该文件是 `agate/scripts/` 自身索引文档，含 3 个已退役名
  （gate-result.sh / agate-workspace-resolve.sh / check-windows-smoke.sh），不属于 NARRATIVE_DIRS；
  若不豁免，CHECK 10 扫到会 ERROR 破坏 BDD-1 → 作为第 5 类豁免显式编码。→ BDD-3
- **self-gate 触发面测试缺口**：现有 4 个测试（test_commit_msg_self_gate.py）只覆盖 agate/scripts/*.sh|py
  与非 agate 文件，**无 README.md / AGENTS.md / CHANGELOG.md 覆盖** → 扩展后必须补测试。→ BDD-6/7/8
- **CHANGELOG 豁免的确认方式**：`_SELF_GATE_RE` 扩展时若用 `^(README\.md|AGENTS\.md|...)` 锚定根级
  精确名，则 CHANGELOG 天然不在其列（无需额外逻辑）；若用宽松 glob 则需显式排除。P2 设计决策。
- **check-retrospective 空输出约束**：RT.1 断言无异常时输出为空——提醒行只能在 warnings 存在时输出，
  不能无条件打印。→ BDD-10/11
- **平台无关**：三处改动均为纯 Python + 文件系统，不引入 Unix 假设（Windows CI 冒烟只跑 marker 用例）。

---

## 3. BDD 验收条件

### RM-AG0015 — CHECK 10 漂移 gate

#### BDD-1: 协议文档面脚本引用无漂移时 CHECK 10 通过
- Given 协议文档面（扫描范围见 §4 开头）脚本名引用全部可解析到 `agate/scripts/`（或豁免清单）真实文件
- When 运行 `python3 agate/scripts/check-protocol-consistency.py`
- Then CHECK 10 报告 PASS，且整体 0 ERROR

#### BDD-2: 协议文件引用不存在的脚本名 → CHECK 10 ERROR
- Given 某协议文件（如 phase-cards）含 `check-nonexistent-script.py` 的脚本名引用
- When 运行 check-protocol-consistency.py
- Then CHECK 10 输出 ERROR（exit 1），消息含文件名与引用位置

#### BDD-3: 豁免清单内的引用不报漂移
- Given 协议文档面中出现以下任一类引用（**豁免清单 5 类**）：
  ① UPGRADING.md **整文件**（含对照表 `.sh→.py` 迁移行如 `check-gate.sh`，及散文行的退役名）
  ② formatters 名（`agate/assets/formatters/` 下的 `pytest.sh` / `go-test.sh` / `generic-exit-only.sh` /
     `generic-tap.sh` / `generic-junit-xml.sh` / `vitest.sh` / `my-runner.sh`，真实存在于 assets/ 不在 scripts/）
  ③ 3 个 hook 薄壳（`pre-commit-gate.sh` / `commit-msg-self-gate.sh` / `pre-push-gate.sh`）
  ④ `count-tests.sh`（真实位置 `agate/tests/scripts/`）
  ⑤ scripts/README.md 的退役名（`gate-result.sh` / `agate-workspace-resolve.sh` / `check-windows-smoke.sh`）
- When 运行 check-protocol-consistency.py
- Then CHECK 10 不报 ERROR/WARNING（豁免生效）

#### BDD-4: phase-cards/rules 纳入 PROTOCOL 严格检查
- Given `agate/phase-cards/` 与 `agate/rules/` 下的 md 文件
- When 检查脚本的 PROTOCOL_DIRS 声明
- Then 两者均被列为协议目录，且此改动未给 CHECK 2/3 引入新的 ERROR（回归验证）

#### BDD-5: 叙事文件中的脚本名引用不升 ERROR
- Given 叙事文件（= `NARRATIVE_DIRS` 覆盖集，含 `CHANGELOG.md` / `archived/` / `docs/plans|reviews|design-notes|tasks` /
  `agate-workspace/tasks/`）含历史脚本名（如 `check-gate.sh`），且 `docs/superpowers`、`docs/guides`、`docs/agents`、
  `docs/notes`、`docs/hardening-roadmap.md` 不在扫描范围（协议文档面）内、不被 CHECK 10 扫描
- When 运行 check-protocol-consistency.py
- Then CHECK 10 对叙事文件至多 WARNING，不产生 ERROR；对不在扫描面的 docs/ 文件无输出（无 ERROR）

### RM-AG0017 — self-gate 触发面

#### BDD-6: 暂存 README.md 变更触发 self-gate WARNING
- Given git 暂存区含仓库根 `README.md` 变更，commit message 无 self-gate-review/self-gate-skip
- When 运行 commit-msg-self-gate.sh
- Then stderr 输出含 "self-gate" 的 WARNING（exit 0 不阻断）

#### BDD-7: 暂存 AGENTS.md 变更触发 self-gate WARNING
- Given git 暂存区含仓库根 `AGENTS.md` 变更，commit message 无标记
- When 运行 commit-msg-self-gate.sh
- Then stderr 输出含 "self-gate" 的 WARNING（exit 0 不阻断）

#### BDD-8: 暂存 CHANGELOG.md 变更不触发 self-gate
- Given git 暂存区含 `CHANGELOG.md` 变更
- When 运行 commit-msg-self-gate.sh
- Then 无输出（CHANGELOG 豁免）

#### BDD-9: 既有 self-gate 触发面不回归
- Given git 暂存区含 `agate/scripts/*.sh|py` 或 `agate/*.md` 变更
- When 运行 commit-msg-self-gate.sh
- Then 原有 4 个测试（test_commit_msg_self_gate.py）全部通过

### RM-AG0018 剩余 — 复盘登记提醒

#### BDD-10: 有异常模式时输出 DEBT/roadmap 登记提醒
- Given 任务目录存在异常模式（gate 重试超限 / SCOPE+ / override 任一）
- When 运行 check-retrospective.py
- Then stderr 含 "DEBT" 与 "roadmap" 的登记提醒行（exit 0 不拦截）

#### BDD-11: 无异常模式时输出为空（RT.1 不回归）
- Given 任务目录无任何异常模式
- When 运行 check-retrospective.py
- Then 输出为空字符串，exit 0

---

## 4. 影响面表（P0-brief 强制：全仓 grep 脚本名引用）

> **CHECK 10 扫描范围（决策：协议文档面）**：`PROTOCOL_FILES`（L52-64 的 11 文件 + `agate/CONTEXT.md`）+
> `PROTOCOL_DIRS`（`agate/assets/`）+ `agate/phase-cards/` + `agate/rules/` + 根级 `README.md` / `AGENTS.md` +
> `agate/AGENTS.md` + `agate/UPGRADING.md` + `agate/scripts/README.md` + `CHANGELOG.md`（叙事降级）。
> **不含**：`docs/`（含 docs/superpowers、docs/guides、docs/agents、docs/notes、docs/hardening-roadmap.md 等
> 项目开发资料）与 `agate-workspace/`（任务产出）——非协议文件不扫，无 ERROR。
> 引用形式三类：**裸名**（REF_RE 漏检，CHECK 10 目标）、**`scripts/` 相对前缀**（REF_RE 已检）、
> **`agate/scripts/`/`~/.agate/scripts/` 全路径**（REF_RE 漏检，因 lookbehind `(?<![\w/])` 在 `agate/` 后不匹配）。

### 4.1 phase-cards / rules（全部裸名引用，REF_RE 现行漏检，共 58 处，当前 0 漂移）

| 文件 | 引用的脚本名（计数） | 裸名? | 豁免? |
|------|---------------------|-------|-------|
| P1-requirements.md | check-gate.py ×2 | ✅ | 否 |
| P2-design.md | check-gate.py ×3, check-tdd-red.py ×2 | ✅ | 否 |
| P3-tdd.md | agate-capture-env-baseline.py ×1, check-gate.py ×1, check-tdd-red.py ×6, **ci-gate-backstop.py ×1** | ✅ | 否 |
| P4-implementation.md | agate-capture-env-baseline.py ×1, check-gate.py ×4, check-pruning.py ×1, check-tdd-red.py ×1 | ✅ | 否 |
| P5-verification.md | check-gate.py ×1 | ✅ | 否 |
| P6-acceptance.md | agate-archive-stale-outputs.py ×1, agate-retreat-to.py ×1, check-gate.py ×4, check-p6-evidence.py ×3, check-p6-format.py ×5, check-p6-provenance.py ×6, pre-commit-gate.sh ×1 | ✅ | pre-commit-gate.sh 豁免（hook 薄壳） |
| P7-consistency.md | check-gate.py ×2 | ✅ | 否 |
| P8-release.md | check-gate.py ×1, check-protocol-consistency.py ×1 | ✅ | 否 |
| rules/state-transitions.md | agate-archive-stale-outputs.py ×1, agate-retreat-to.py ×1, check-debt.py ×1, check-gate.py ×2, check-p6-provenance.py ×1, check-state-transition.py ×2, check-tdd-red.py ×1 | ✅ | 否 |
| rules/review-mapping.md | （无脚本名引用） | — | — |

> 全部引用（含 pre-commit-gate.sh）实测能解析到 `agate/scripts/` 真实文件 → CHECK 10 当前 0 漂移（增量性成立）。
> 合计 58 处（P0-orchestrator.md 与 phase-cards/README.md 0 处，不计）。

### 4.2 协议文件（裸名 + 前缀 + 全路径混合）

| 文件 | 脚本名引用 | 引用形式 | 豁免? |
|------|-----------|---------|-------|
| agate/WORKFLOW.md | check-gate.py, check-tdd-red.py, check-p6-evidence.py, check-p6-provenance.py, check-state-transition.py, check-pruning.py, check-scope-resolved.py, check-retrospective.py, check-changelog.py, check-state-yaml.py, ci-gate-backstop.py | 裸名 + `scripts/` 前缀 | 否 |
| agate/dispatch-protocol.md | check-gate.py, check-p6-provenance.py, check-p6-format.py, check-tdd-red.py, check-scope-resolved.py, agate-inject-card.py, agate-archive-stale-outputs.py, agate-retreat-to.py | 裸名 + `scripts/` 前缀 | 否 |
| agate/state-machine.md | check-gate.py, check-tdd-red.py, check-p6-provenance.py, check-pruning.py, check-scope-resolved.py, check-state-transition.py | 裸名 + `scripts/` 前缀 | 否 |
| agate/git-integration.md | check-gate.py, check-p6-provenance.py | 裸名 | 否 |
| agate/role-system.md | check-gate.py | 裸名 | 否 |
| agate/loop-orchestration.md | check-gate.py | 裸名 | 否 |
| agate/platform-notes.md | check-gate.py, check-p6-provenance.py, ci-gate-backstop.py, agate-summary.py | 裸名 + `scripts/` 前缀 | 否 |
| agate/LIMITATIONS.md | check-gate.py, check-p6-provenance.py, ci-gate-backstop.py, check-p6-evidence.py, check-pruning.py | 裸名 + `scripts/` 前缀 | 否 |
| agate/SETUP.md | agate-summary.py, agate-next-card.py, check-protocol-consistency.py, install-hook.py | `~/.agate/scripts/` 全路径 | 否（install-hook.py 存在） |
| agate/orchestrator-template.md | check-gate.py, agate-inject-card.py, agate-summary.py, agate-migrate-workspace.py | 裸名 + `{agate_root}/scripts/` | 否 |
| agate/CONTEXT.md | check-gate.py ×2 | 裸名 | 否 |
| agate/UPGRADING.md | 27 个历史 `.sh` 名（check-gate.sh / check-tdd-red.sh / agate-summary.sh 等）+ 现行 `.py` 名 | 全路径 + `~/.agate/` | **✅ 整文件豁免**（对照表行 + 散文行退役名） |
| README.md | install-hook.py ×1 | 裸名 | 否 |
| AGENTS.md | pre-commit-gate.sh / commit-msg-self-gate.sh / pre-push-gate.sh / install-hook.py / pre-commit-gate.py / check-gate.py / check-protocol-consistency.py / agate-summary.py / count-tests.sh | `agate/scripts/` 全路径 + 裸名 | 3 hook 薄壳 + count-tests.sh 豁免 |
| agate/AGENTS.md | install-hook.py | `~/.agate/scripts/` 全路径 | 否 |
| CHANGELOG.md | 历史 `.sh`/`.py` 名大量（38×check-gate.sh 等） | 裸名 | **✅ 叙事豁免**（NARRATIVE_DIRS 已含） |
| agate/scripts/README.md | 全部现行脚本 + 退役名 gate-result.sh / agate-workspace-resolve.sh / check-windows-smoke.sh（退役说明） | 裸名 | **✅ 退役名 3 个豁免**（第 ⑤ 类） |

### 4.3 agate/assets/** 协议文件（PROTOCOL_DIRS，L65 已含，全部裸名引用，共 47 处，当前 0 漂移）

| 文件 | 引用的脚本名（计数） | 豁免? |
|------|---------------------|-------|
| execution-roles/architect.md | agate-capture-env-baseline.py ×1, check-gate.py ×1, check-tdd-red.py ×1 | 否 |
| execution-roles/consistency-reviewer.md | check-gate.py ×1 | 否 |
| execution-roles/verifier.md | check-gate.py ×1, check-p6-evidence.py ×1, check-p6-format.py ×2, check-p6-provenance.py ×3 | 否 |
| formatters/README.md | check-tdd-red.py ×1（formatter 名 pytest.sh 等归第 ② 类豁免） | check-tdd-red.py 否；formatter 名豁免 |
| review-roles/protocol-alignment-review.md | check-gate.py ×3, check-pruning.py ×2, check-p6-provenance.py ×1, check-protocol-consistency.py ×1, check-state-yaml.py ×1, check-scope-resolved.py ×1, check-frontmatter.py ×1, agate-frontmatter-check.py ×1, agate-md-field-get.py ×1 | 否 |
| templates/active-tasks-template.md | check-tdd-red.py ×1 | 否 |
| templates/dispatch-context.md | agate-inject-card.py ×2, check-p6-provenance.py ×2 | 否 |
| templates/dispatch-prompt.md | check-p6-provenance.py ×1 | 否 |
| templates/handoff-template.md | check-protocol-consistency.py ×4, agate-summary.py ×1, pre-commit-gate.sh ×1, count-tests.sh ×1 | pre-commit-gate.sh + count-tests.sh 豁免 |
| templates/task-files.md | check-tdd-red.py ×3, check-p6-provenance.py ×1, check-scope-resolved.py ×1, check-state-yaml.py ×1 | 否 |
| templates/tech-debt-template.md | check-debt.py ×3, agate-retreat-to.py ×1 | 否 |

> 合计 47 处（review 实测 ~30 处，本表逐文件核实后为 47 处——差异来自形式化正则计入 install-hook.py /
> 全文件名 token，属计数口径问题非遗漏）。全部引用（含 formatter 名）实测能解析到 `agate/scripts/` 或
> `agate/assets/formatters/` 真实文件 → 0 漂移仍成立（增量性不受影响）。

### 4.4 影响面摘要

- **引用类别**：3 类（裸名 ≈ 协议面主体；`scripts/` 前缀；`agate/scripts/`/`~/.agate/` 全路径）。
- **计数规则（可复现）**：对扫描面内每类文件运行
  `rg -o '\b(check-[a-z0-9-]+\.(py|sh)|agate-[a-z0-9-]+\.(py|sh)|install-hook\.(py|sh)|pre-commit-gate\.(py|sh)|commit-msg-self-gate\.(py|sh)|pre-push-gate\.(py|sh)|count-tests\.sh|ci-gate-backstop\.py)\b' 文件集 | wc -l`
  按脚本名 token 出现次数计数（含同文件内重复引用）。
- **分项实测**：phase-cards/rules **58** / 协议 md（PROTOCOL_FILES 11 + CONTEXT）**104** /
  README/AGENTS（根级 + agate/AGENTS）**22** / UPGRADING **86** / scripts/README **61** / assets/** **47** =
  **协议文档面 378**（不含 CHANGELOG）；含 CHANGELOG **217** → 总计 **595**。
- **独立复核**：与 requirements-review 独立实测对照——四类核心（58 + 104 + 22 + 86 = **270**）与
  含 CHANGELOG（**487**）逐项吻合；scripts/README 与 assets/** 两块为评审要求补入的新增行
  （原 270/487 未含），计数口径可复现。
- **当前漂移**：0（v0.46.0 已修，无 gate 防复发）。
- **豁免清单（CHECK 10 设计输入，P0-brief 已锁定 + review 修订补足，最终 5 类）**：
  ① UPGRADING.md **整文件**（对照表迁移行 + 散文行退役名，历史迁移文档）
  ② formatters（`agate/assets/formatters/` 下的 pytest.sh / vitest.sh / go-test.sh / generic-exit-only.sh /
     generic-tap.sh / generic-junit-xml.sh / my-runner.sh——不在 agate/scripts/，若按 scripts/ 解析会误报）
  ③ 3 个 hook 薄壳（pre-commit-gate.sh / commit-msg-self-gate.sh / pre-push-gate.sh）
  ④ `count-tests.sh`（真实位置 `agate/tests/scripts/count-tests.sh`，不在 agate/scripts/）
  ⑤ **scripts/README.md 退役名**（gate-result.sh / agate-workspace-resolve.sh / check-windows-smoke.sh，
    该文件是 scripts/ 自身索引，退役名属历史说明）
  另加叙事文件（CHANGELOG/archived/docs/plans|reviews|design-notes|tasks/agate-workspace/tasks）至多 WARNING。

---

## 5. self-gate 触发面现状表

`_SELF_GATE_RE` 现行（L38-40）：`^(agate/scripts/.*\.(sh|py)|agate/[^/]+\.md|agate/.+/.*\.md|SELF-GATE\.md)$`

| 触发文件类别 | 现行是否触发 | 扩展后 | 备注 |
|-------------|-------------|--------|------|
| `agate/scripts/*.sh` | ✅ | ✅ | test_cmsg_1 覆盖 |
| `agate/scripts/*.py` | ✅ | ✅ | test_cmsg_2 覆盖 |
| `agate/*.md`（如 WORKFLOW.md） | ✅ | ✅ | — |
| `agate/*/*.md`（如 phase-cards） | ✅ | ✅ | — |
| `SELF-GATE.md` | ✅ | ✅ | 实测正则包含（复盘原文误判） |
| `README.md`（根级） | ❌ | ✅ | **需补测试（test_cmsg_new_1）** |
| `AGENTS.md`（根级） | ❌ | ✅ | **需补测试（test_cmsg_new_2）** |
| `CHANGELOG.md`（根级） | ❌ | ❌（豁免） | **需补测试（test_cmsg_new_3）** |
| `docs/` / `agate-workspace/` | ❌ | ❌ | 非协议面，保持不触发 |

> **测试缺口**：现有 test_commit_msg_self_gate.py 4 用例无 README/AGENTS/CHANGELOG 覆盖。
> 扩展后需新增 ≥3 用例（README 触发 / AGENTS 触发 / CHANGELOG 豁免），并保证既有 4 用例不回归（BDD-9）。

---

## 6. 裁剪说明

`phases: [P1, P2, P3, P4, P5, P6, P7, P8]` — 全流程，无裁剪。

- **P2（设计）**：不可裁。CHECK 10 豁免设计（5 类豁免 + 叙事降级 + 扫描范围实现方式）与 `_SELF_GATE_RE`
  扩展模式需 architect 定方案。
- **P3（TDD）**：medium risk 不可裁。三处改动都有明确二值验收（BDD 11 条）。
- **P4 / P5 / P6**：不可裁，标准实现/验证/验收。
- **P7（一致性）**：不裁。跨文件一致性是本次主题（脚本名引用 + self-gate 触发面），packages 声明交叉核对必要。
- **P8（发布）**：不裁。本次修改协议本体（gate 脚本 + 测试 + 协议文档），按版本发布流程走
  （CHANGELOG / UPGRADING / version badge / tag）。

---

## 7. NEED_CONFIRM 处理

- [NO_NEED_CONFIRM]
- 无待确认项。三条 issue 范围已锁定（P0-brief），豁免清单已锁定（5 类），扫描范围已定（协议文档面），
  隐含需求均可在 P2 设计内消化。
- [SUGGEST: 若 P4 将 CHECK 10 逻辑拆为独立脚本 `check-script-refs.py`，需同步加进
  `SCRIPT_ALIGNMENT_ANCHORS` 锚点表（否则 CHECK 9 反向锚点覆盖会 WARNING）。倾向：留在
  check-protocol-consistency.py 内作为第 10 个 CHECK 函数（与现有 CHECK 1-9 同构，改动最小）。]

## 8. SCOPE+ 预留

> 活基线预留节。后续阶段发现新隐含需求时由主 Agent 增补并标 `[SCOPE+ from Pn]`；P7 一致性审查后登记 `[SCOPE_RESOLVED: ...]`。

- [SCOPE+ from P4] 既有集成测试 `test_csg_1_non_trigger_no_warning`（`agate/tests/integration/test_commit_msg_self_gate_integration.py`）断言 README.md 变更不触发 self-gate WARNING——这是 RM-AG0017 要修复的旧行为（BDD-6 要求 README.md 触发）。实现后该用例转红，属测试断言过时而非新需求；需更新断言为「README.md 变更触发 self-gate WARNING」。
- [SCOPE_RESOLVED: 本任务 SCOPE+（integration test_csg_1 断言过时）已闭环——test_commit_msg_self_gate_integration.py L47 已更新为 test_csg_1_readme_triggers_warning（README 触发），P6 BDD-9 14 passed 实测通过，P7 一致性审查确认。]
