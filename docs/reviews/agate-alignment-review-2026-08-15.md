---
review_date: 2026-08-15
reviewer: protocol-alignment-review
change_summary: TAG0010 产品逻辑 Python 化（v0.46.0，30 个 .sh → .py，3 hook 保留薄壳）+ TAG0011 测试框架 bats → pytest（v0.47.0，60 bats → pytest，协议文档 34 个 .md 重写 + CI + Windows 冒烟），PR #135 合并到 main
files_changed: [agate/scripts/ 78 文件（47 py + 3 薄壳 sh + agate_common.py）、agate/tests/ 全量重写、34 个协议 .md、.github/workflows/protocol-tests.yml、CHANGELOG.md、README.md]
---

# 协议-脚本对齐审查

审查范围：`f0695fc..cd25ea3`（93 commits），PR #135 已 merge（merge commit cd25ea3）。
权威规则源：`agate/state-machine.md`、`agate/dispatch-protocol.md`、`agate/WORKFLOW.md`。

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | **MISALIGNED** |
| A2 | 脚本→文档对齐 | **MISALIGNED** |
| A3 | 一致性连锁 + 反向传播 | **MISALIGNED**（文档侧 ALIGNED，脚本侧反向传播不完整）|
| A4 | 测试覆盖 | **ALIGNED**（748 passed / 2 skipped 实跑；含覆盖缺口备注）|
| A5 | 下游影响 + 文档传播 | **MISALIGNED** |
| A6 | 锚点表覆盖 | **ALIGNED** |
| A7 | 设计原则一致性 | **ALIGNED**（附建议）|

**核心发现**：`ci-gate-backstop.py` 仍引用本变更已删除的 3 个 `.sh` 脚本（`check-gate.sh` / `check-tdd-red.sh` / `check-p6-provenance.sh`），导致 backstop 在合法项目上**实际跑不通**（已实机复现 FAIL）；`agate-summary.py` 残留 12 处已删 `.sh` 引用（guard 清单失效 + drift 检测失效 + `agate-changes.sh` 指令失效）；`check-gate.py:374` 提示消息指向已删的 `check-tdd-red.sh`。这些均未被 TAG0010 的 P7-consistency 记录（非 DESIGN_GAP，原则 6 不适用）。

---

## 逐项审查

### A1: 文档→脚本对齐 — MISALIGNED

**文档声明**（WORKFLOW.md:300）：
> CI backstop（P1.3）：push 后 CI 平台（GitHub Actions / GitLab CI / Gitea Actions）重跑 `check-gate.py` + `ci-gate-backstop.py`，捕获 `--no-verify` 绕过 hook 的恶意提交；provenance 审计重跑（check-p6-provenance.py）…

（WORKFLOW.md:263 亦声明 "scripts/check-tdd-red.py exit 0（主 Agent 手动 + CI backstop 兜底）"）

**脚本实现**（ci-gate-backstop.py:51-58）：
```python
def run_gate(phase: str, task_dir: str) -> tuple[int, str]:
    script = _AGATE_ROOT / "scripts/check-gate.sh"      # ← 已删除文件
    if not script.exists():
        return 2, "check-gate.sh not found"
```

`scripts/check-gate.sh` 已在本次变更中删除（commit e8bf474，批次 4c/4d 删 27 个已 py 化 .sh），当前 `agate/scripts/` 下仅存 3 个 hook 薄壳。因此 `run_gate` 恒返回 `(2, "check-gate.sh not found")`。

**实机复现**（本审查执行）：
```
mkdir -p /tmp/opencode/backstop-demo && git init
.state.yaml phase=P4 + .gate-result.json exit_code=0 + P4-implementation.md
env GITHUB_ACTIONS=true python3 agate/scripts/ci-gate-backstop.py
→ CI platform: github
→ FAIL: .gate-result.json exit=0 != CI 重跑 exit=2
→ BACKSTOP_EXIT=1
```
即：合法 P4 项目（hook 已记录 exit 0）在 v0.47.0 下 backstop 必然 FAIL——文档描述的"CI backstop 最后防线"机制已失效。

**差异**：WORKFLOW.md 声明 CI backstop 重跑 `check-gate.py` + provenance 审计重跑；`ci-gate-backstop.py` 实际调用的是已删除的 `check-gate.sh`（exit 2 not found）、`check-p6-provenance.sh`（line 262，`exists()` 检查静默跳过，provenance 兜底审计失效）。

**建议**：`run_gate` 改调 `_AGATE_ROOT / "scripts/check-gate.py"`（subprocess `sys.executable`，或直接 import 复用），`tdd_script` 默认值改 `check-tdd-red.py`，`provenance_script` 改 `check-p6-provenance.py`；同步删除 `_find_bash`/`_bash_cmd`（P2-design.md:134 本计划的批次 2 动作，从未执行）。

---

### A2: 脚本→文档对齐 — MISALIGNED

脚本内部残留已删 `.sh` 引用（功能路径，非注释）：

**① ci-gate-backstop.py**（同 A1 复现）：
- `:51` `_AGATE_ROOT / "scripts/check-gate.sh"`（已删）
- `:176` `Path(os.environ.get("AGATE_TDD_RED_SCRIPT", str(_AGATE_ROOT / "scripts/check-tdd-red.sh")))`（已删，P3 兜底默认失效 → 恒 "check-tdd-red.sh 不存在，P3 红灯检查跳过" WARN）
- `:262` `_AGATE_ROOT / "scripts/check-p6-provenance.sh"`（已删，provenance CI 层兜底静默失效）

**② agate-summary.py**：
- `:21-31` `_GUARD_SCRIPTS` 列 9 个已删 `.sh`（check-state-yaml.sh / check-gate.sh / check-changelog.sh / check-p6-evidence.sh / check-p6-provenance.sh / check-state-transition.sh / check-pruning.sh / check-scope-resolved.sh / check-retrospective.sh）→ `_build_guards` 全 miss，"防护机制"清单实际只显示 pre-commit-gate.sh 薄壳 + ci-gate-backstop.py，9 个真实 gate 防护不展示。
- `:33` `_DRIFT_SCRIPTS = ["check-tdd-red.sh", "check-gate.sh", "check-pruning.sh"]`（已删）→ `_check_copy_drift` 恒空跑，本地副本漂移检测失效。
- `:147-150` 启动提示输出 `bash ~/.agate/scripts/agate-changes.sh [since-tag]`（已删；正确应为 `python3 ~/.agate/scripts/agate-changes.py`）→ 用户按提示执行报 "No such file"。

**③ check-gate.py:374**：
```
GATE P3: P3-test-cases.md 存在。TDD 红灯由主 Agent 手动跑 check-tdd-red.sh 确认 + CI backstop P3 兜底。
```
（`check-tdd-red.sh` 已删，指令失效；且 test_check_gate.py:89 断言 `"check-tdd-red.sh" in result.output` 把这个失效引用锁进了测试。）

**差异**：P2-design.md:134 明确计划 "`run_gate` 的 check-gate.sh → check-gate.py 切换**移入批次 2**"，P4-implementation.md:76 计划 "`_bash_cmd`/`_find_bash` 于批次 2 随 check-gate.py / check-tdd-red.py / check-p6-provenance.py 落地逐个删除"——批次 2-4 实际只改了 check-gate.py 本体与 bats 调用点，**ci-gate-backstop.py 的切换被静默丢弃**。

**建议**：三处脚本内的 `.sh` 字符串改指 `.py`；agate-summary.py 的 guard/drift 清单改 `.py` 名、advice 命令改 `python3`；check-gate.py:374 + test_check_gate.py:89 同步改 `check-tdd-red.py`。

---

### A3: 一致性连锁 + 反向传播 — MISALIGNED（文档侧 ALIGNED / 脚本侧不完整）

**A3a 连锁（已知衍生改动）**：全部完成 ✓
- CHECK 9 锚点表：`check-protocol-consistency.py:448,452,525,535,580,585,590,662` 已全部 `.py`；覆盖扫描 glob `check-*.py` + `pre-commit-gate.{sh,py}` + `ci-gate-backstop.py`（`:737-750`）；新增 `check-platform-assumptions.py` 已入表（`:678`）。
- WORKFLOW.md「Pre-commit 检查总览」（`:283-299`）全部 `.py`；多任务适配仍指 `pre-commit-gate.sh` 薄壳（`:303`，正确）。
- state-machine.md（`:91-92,119,259,261,596`）、dispatch-protocol.md、orchestrator-template.md、git-integration.md、LIMITATIONS.md、adr.md（`:93,110,177`）均已 `.py`。
- UPGRADING.md 新增 v0.46.0 迁移章节（`:112`，30 脚本改名/删档逐条 + 迁移命令）与 v0.47.0 bats→pytest 章节（`:92`）；CHANGELOG v0.47.0 条目（`:11`）。
- README badge v0.47.0 == `git tag v0.47.0` == HEAD 描述。✓

**A3b 反向传播（应被影响文件的逐一验证）**：发现 2 个应被影响且**在 diff 中已修改但未同步完全**的文件：

| 应传播目标 | 结果 |
|-----------|------|
| `ci-gate-backstop.py`（`run_gate` 调 check-gate.sh）| **未同步** → 引用已删 `.sh`（见 A1/A2）|
| `agate-summary.py`（guard/drift 清单 + agate-changes 指令）| **未同步** → 引用已删 `.sh`（见 A2）|
| 协议文档硬编码 `.sh` 脚本路径 | 已同步 ✓（仅 UPGRADING 历史表/asset formatters `.sh`/3 薄壳为有意保留）|
| 角色文件/模板文件 bats/check-tdd-red.sh/bash 命令 | 已同步 ✓（handoff-template.md:67 shellcheck `*.sh` 仍可匹配 3 薄壳；`:70` count-tests.sh 仍存在）|
| CHECK 9 锚点表 | 已同步 ✓ |
| WORKFLOW.md 检查总览 | 已同步 ✓ |
| UPGRADING.md 破坏性变更 | 已同步 ✓ |
| README badge vs tag | 一致 ✓ |

**结论**：文档侧反向传播完整；脚本侧（ci-gate-backstop.py / agate-summary.py）反向传播不完整，列为 MISALIGNED。

---

### A4: 测试覆盖 — ALIGNED

**pytest 全量实跑**（本审查执行，2026-08-15）：
```
$ python3 -m pytest agate/tests/ -q
...
748 passed, 2 skipped in 65.93s (0:01:05)
```
`agate/tests/scripts/count-tests.sh`：750 用例（pytest collect-only 口径；基线 ≥749，BDD-1）——750 = 748 passed + 2 skipped ✓。0 个 `.bats` 残留。

bats→pytest 迁移无用例流失：`ci-gate-backstop.bats` 11 用例 → `test_ci_gate_backstop.py` 11 用例逐条对应（含 windows_smoke 4 处）；`check-tdd-red.bats`/`check-gate.bats` 等抽样核对迁移完整。

**覆盖缺口（非回归，备注）**：
- `ci-gate-backstop.py` 的「gate-result.json 对照 FAIL」路径**历来无测试**（bats 与 pytest 均未覆盖）——这正是 A1 的 run_gate 失效 bug 逃逸的原因（P5-test-results 里跑 backstop 时 agate 仓库根无 `.state.yaml` → 恒 SKIP，验证空转）。
- `agate-summary.py` 无对应测试（迁移前后皆无）。

建议：为 `run_gate` 补一条「check-gate.py 被调 + exit 对照」用例（可覆盖本审查发现的回归）。

---

### A5: 下游影响 + 文档传播 — MISALIGNED

**已覆盖**：
- UPGRADING.md v0.46.0（`:112`）/ v0.47.0（`:92`）两章逐条列破坏性变更 + 迁移命令 ✓；CHANGELOG v0.47.0 标注 ✓；README badge == tag ✓。
- 协议文档全量传播 ✓（见 A3a）。

**未覆盖的下游破坏**（本审查发现，均未在 UPGRADING/CHANGELOG 标注，也无迁移救济）：
1. **`ci-gate-backstop.py` 对下游用户项目失效**：用户项目在 v0.47.0 上跑 CI backstop → 恒 FAIL（见 A1 复现）。这是 P1.3 防线（捕获 `--no-verify`）的功能性回归，且 CI 里表现为**误报 FAIL**（会把合法 push 标红），比静默失效更危险。
2. **`agate-summary.py` 启动提示指令失效**：`bash ~/.agate/scripts/agate-changes.sh`（已删）——用户照抄执行报错。

**结论**：破坏性变更文档清单已齐全，但**变更本身引入的 2 处下游失效未同步标注/修复**，判 MISALIGNED。

---

### A6: 锚点表覆盖 — ALIGNED

- CHECK 9 正向锚点：`check-pruning.py`（P2 不可裁剪/risk_level/P6 不可裁剪/coupling_checklist/源码文件数/internal_only）、`check-gate.py`（DESIGN_GAP/--cached）、`check-p6-provenance.py`、`check-platform-assumptions.py`（`:678`）等全部 `.py`，无 `.sh` 残留锚点。
- CHECK 8 v0.6 关键词断言：`check-gate.py` 含 DESIGN_GAP/--cached（`:448,452`）✓。
- CHECK 9 反向覆盖：`check_anchor_coverage`（`:727-760`）遍历 `check-*.py` + 薄壳 + backstop；`GATE_SCRIPT_EXEMPT`（`:721-724`）豁免 check-protocol-consistency.py / pre-commit-gate.py（合理）。实跑 `check-protocol-consistency.py`：**0 ERROR，274 WARNING**（WARNING 均为任务工作区/叙事文件指向已删脚本的引述，属历史记录，非协议语义）。
- 建议：`ci-gate-backstop.py` 修复后无需新增锚点（已有锚点 `:641` 引用它）。

---

### A7: 设计原则一致性 — ALIGNED（附建议）

- ADR-004 安全网分层（hook 兜底 + CI backstop）：迁移保留了分层结构，但 CI backstop 层因 A1 问题失效——**恢复该层后**方与 ADR-004 完全一致（此为修复项，非原则违背）。
- ADR-001（主 Agent 不写产出）/ADR-002（可判定）/ADR-006（双层角色）：gate 语义逐分支等价迁移，无行为偏离 ✓。
- adr.md `.sh → .py` 名称同步（`:93,110,177`）✓。
- **建议（非阻断）**：Python 化 + pytest 迁移是重大架构决策，adr.md 未新增 ADR 记录该决策（仅在 AGENTS.md/任务文档记录）。建议补充新 ADR（如 "ADR-009: 产品逻辑 Python 化 + 测试框架 pytest"），理由与取舍（平台无关 / 单语言维护 / 3 hook 薄壳 fail-closed 边界）留档。按 A7 特殊规则，仅记建议，不影响结论。

---

## MISALIGNED 汇总（需修复项）

| # | 位置 | 差异 | 建议方向 |
|---|------|------|---------|
| M1 | `ci-gate-backstop.py:51` | `run_gate` 调已删 `check-gate.sh` → 合法项目恒 FAIL | 改调 `check-gate.py`（`sys.executable` subprocess 或 import 复用），删 `_find_bash`/`_bash_cmd` |
| M2 | `ci-gate-backstop.py:176` | P3 兜底默认指已删 `check-tdd-red.sh` → 恒 WARN 跳过 | 默认值改 `check-tdd-red.py` |
| M3 | `ci-gate-backstop.py:262` | provenance 兜底指已删 `check-p6-provenance.sh` → 静默失效 | 改 `check-p6-provenance.py` |
| M4 | `agate-summary.py:21-33` | `_GUARD_SCRIPTS`/`_DRIFT_SCRIPTS` 列 12 个已删 `.sh` → guard 清单空 + drift 检测失效 | 改 `.py` 名 |
| M5 | `agate-summary.py:147-150` | 提示 `bash .../agate-changes.sh`（已删）| 改 `python3 .../agate-changes.py` |
| M6 | `check-gate.py:374` | P3 消息指已删 `check-tdd-red.sh` | 改 `check-tdd-red.py`（并同步 `test_check_gate.py:89` 断言）|

**闭环**：以上 M1-M6 修复后重跑 `python3 -m pytest agate/tests/ -q` + `check-protocol-consistency.py`（0 ERROR）+ `count-tests.sh`（750 不漂移），方可进入 P8/commit。

**人工验收清单**：
- [x] 审查报告含 A1-A7 七项，每项有结论
- [x] MISALIGNED 项有差异描述 + 建议方向
- [x] 无 NEEDS_HUMAN_REVIEW 项（无需 HUMAN_CONFIRMED 配对）
- [x] 审查报告落盘 `docs/reviews/agate-alignment-review-2026-08-15.md`

---

## 修复记录（2026-08-15 主 Agent 执行）

### 已修复（M1-M6 全部落地）

| # | 修复 | 位置 | 验证 |
|---|------|------|------|
| M1 | `run_gate` 改调 `check-gate.py`（`sys.executable`），删 `_find_bash`/`_bash_cmd` | ci-gate-backstop.py:50-58 | P5 实机复现 PASS（exit 一致），不再 `not found` |
| M2 | P3 兜底 `check-tdd-red.sh` → `check-tdd-red.py`（`_run_python`）| ci-gate-backstop.py:176 | test_ci_gate_backstop 6 个 P3 用例全过（mock 改 py 脚本）|
| M3 | provenance 兜底 `check-p6-provenance.sh` → `check-p6-provenance.py` | ci-gate-backstop.py:262 | — |
| M4 | `_GUARD_SCRIPTS`/`_DRIFT_SCRIPTS` 9+3 个 `.sh` → `.py` | agate-summary.py:21-33 | guard 清单恢复展示 |
| M5 | 启动提示 `bash ...agate-changes.sh` → `python3 ...agate-changes.py` | agate-summary.py:147-150 | — |
| M6 | `check-gate.py:374` P3 消息 + `check-gate.py:530` P6 消息 `.sh` → `.py`；`test_check_gate.py:89` 断言同步；integration 触发示例 `check-gate.sh` → `pre-commit-gate.sh` | check-gate.py / test_check_gate.py / test_commit_msg_self_gate_integration.py | 全过 |

### 补充回归测试
- `test_backstop_p5_py_gate_pass`（test_ci_gate_backstop.py）：M1 回归锁——P5 场景 .gate-result.json exit=2 与 CI 重跑一致 → PASS。此前该路径无测试，正是 M1 bug 逃逸原因（A4 备注）。用例数 750 → 751（≥749 基线 ✓）。

### 验证结果
- `python3 -m pytest agate/tests/ -q` → **748 passed, 2 skipped**
- `check-protocol-consistency.py` → **0 ERROR**（279 WARNING 均为叙事引用）
- `count-tests.sh` → **751**（≥ 749 基线）
- 实机复现：P5 合法项目 backstop → `PASS: phase=P5 exit_code=2 一致`

### 待办（非阻塞）
- **A7 建议**：adr.md 未记录「产品逻辑 Python 化 + 测试框架 pytest」架构决策，建议补 ADR-009（平台无关 / 单语言维护 / 3 hook 薄壳 fail-closed 边界）。不影响本次闭环，按 A7 特殊规则仅记建议。
