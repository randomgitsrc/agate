---
phase: P7
task_id: TAG0009-tests-platform-neutral
type: consistency
parent: P2-design.md
trace_id: TAG0009-tests-platform-neutral-P7-20260813
status: approved
created: 2026-08-13
agent: consistency-reviewer
# ── v2.0 机器计数 ──
blocker_count: 0
deviation_count: 0
deviation_critical_count: 0
design_gap_count: 1
design_gap_reviewed_count: 1
---

# P7 一致性审查结论 — TAG0009 测试套件平台无关化

> 审查方式：逐文件读 P1/P2/P4/P4-review/P6/P5-test-results + 实际改动文件
> （`agate/scripts/check-platform-assumptions.sh`、`agate/tests/helpers/fixtures.bash`、
> `agate/scripts/agate-extract-context.sh`、`.github/workflows/protocol-tests.yml`、
> `install-hook.bats`、`pre-push-hook.bats`、`check-protocol-consistency.py`）交叉核对。
> 审查环境：worktree `/home/kity/oclab/agate/.worktrees/agate-TAG0005-0009`（Linux），未接触生产环境。

## 结论

一致性审查通过：无 BLOCKER / DEVIATION-CRITICAL；DESIGN_GAP 已配对 REVIEWED；SCOPE+ 已闭环；
跨文件检查项均引用具体锚点。

## 1. DESIGN_GAP 配对（P4-implementation.md §4 → 本文件 REVIEWED）

转抄 P4 声明（P4-implementation.md:77 行首原文）：

```
[DESIGN_GAP: P2 §2.5 设计文本「Linux 真软链语义保留：现有 [[ -L "$repo/.git/hooks/pre-push" ]]」与 BDD-8（扫描器对修复后全树零命中，含 R3）+ P3 test_bdd_4（[[:space:]]\[+[[:space:]]+-L[[:space:]] 字面必须检出）冲突——`[[ -L ]]` 字面存在即被 R3 检出。实现改为：Linux 分支用 `readlink` 目标断言（真软链存在且指向 pre-push-gate.sh 的语义等价，readlink 对非软链返回空/失败），保留 BDD-18「Linux 断言软链语义」意图，同时满足 R3 零命中。]
```

[DESIGN_GAP_REVIEWED: P4 的 readlink 替代 `[[ -L ]]` 决策经 P4-review 批准（P4-review.md「二、已批准项 [DESIGN_GAP] … — 批准」，依据 = P2-design.md:174 本就写明 Linux 分支 readlink 指向、BDD-4/BDD-8 与字面 `[[ -L ]]` 冲突）。P7 复核实际代码：`agate/tests/unit/install-hook.bats:31,47` 用 `[[ "$(readlink ...)" == ... ]]` 断言真软链指向 pre-push-gate.sh，无 `-L` 字面；`agate/tests/integration/pre-push-hook.bats:16` 同构；复制模式由 mock ln 用例覆盖（install-hook.bats:52-75,77-101、pre-push-hook.bats:29）。BDD-18「Linux 断言软链语义」意图保留、R3 零命中，结论成立。]

- 配对状态：1 条 DESIGN_GAP（readlink）→ 1 条 REVIEWED（本文件），全部配对。

## 2. SCOPE+ 闭环

- **P1 scope_resolved**（P1-requirements.md:16 frontmatter）：产品脚本裸 python3 真实 Windows 环境失效（17 文件 68 处）→ 判定另立任务（TAG0010+）根治，本任务 harness shim 只覆盖测试场景。
  - P2-design.md:37 / :79 确认「其余 16 个产品脚本 harness shim 兜底，P1 scope_resolved 已声明」「P1 scope_resolved 字段已声明本任务采用候选 A」→ **已闭环**。
- **P2 §9 [SCOPE+] #1**（P2-design.md:394）：integration/pre-push-hook.bats L11 `[ -L ... ] || fail` 命中 R3——P4-implementation.md:44 已按平台分支处理（Linux readlink / Windows `[ -f ]`），实测 pre-push-hook.bats:16 确已改 readlink → **已闭环**（归 BDD-8 同类扫描闭环，不改 P1 范围）。
- P2 §9 [SCOPE+] #2（Windows CI 可能暴露日志外用例）与 #3（产品脚本根治 TAG0010+）为**非阻塞观察**，P1 scope_resolved / P6「I7 supplementable」已覆盖 → 不构成未决项。

## 3. 跨文件一致性检查（引用具体锚点）

### 3.1 P1 29 BDD ↔ P6 29 验收结果（数量匹配 + 编号对齐）

- P1-requirements.md「## 3. BDD 验收条件」共 29 条 `#### BDD-1:` ~ `#### BDD-29:`（grep -c = 29）。
- P6-acceptance.md 恰有 29 条 `- PASS BDD-N:`（grep -c = 29），且 BDD-1..BDD-29 **每个编号恰好 1 条 PASS**、无 FAIL、无行首 NEED_CONFIRM；frontmatter `pass: 29 / fail: 0` 与正文一致。
- 抽样核对编号内容映射无错位：P6 BDD-8 = 全树零检出（P1 BDD-8「扫描器对'干净'测试套件零检出」✓）、P6 BDD-24 = awk 求和（P1 BDD-24「agate-extract-context.sh 移除 bc 依赖」✓）、P6 BDD-27 = windows-latest（P1 BDD-27 ✓）。

### 3.2 P2 packages ↔ P4 实际改动归属

- P2-design.md frontmatter `packages: [agate-tests, agate-scripts, ci-workflow]` ↔ P4-implementation.md §1 改动清单：
  - `agate-tests`：24+1 文件测试侧 `python3`→`$PYTHON`（P4 §1.4）、install-hook/pre-push-hook/agate-next-card/check-scope-resolved/ci-gate-backstop 平台分支、新增 helpers-python.bats（P4 §1.4）→ 归属 ✓
  - `agate-scripts`：仅 `check-platform-assumptions.sh`（新增）+ `agate-extract-context.sh`（bc→awk）+ `check-protocol-consistency.py`（锚点补录）→ 与 P1 §6「其余 17 个产品脚本不改」一致 ✓
  - `ci-workflow`：protocol-tests.yml platform-scan job + bats job windows matrix → 归属 ✓

### 3.3 P4 实现 ↔ P2 §2.1-2.9 方案吻合

- **§2.1 扫描器**：P2 模式集（R1 PATH / R2 命令位置 python3 + 豁免 / R3 -L / R4 /tmp + scan-exempt 仅 R4 / R5 bc）↔ check-platform-assumptions.sh:28-32（R1-R5 正则一致）、:43-55（R2 豁免集 command -v/env/shebang/@test/注释）、:70（scan-exempt 仅在 R4 分支生效）、:92（find 递归扫 *.bats/*.bash/*.sh）、:96-98（不存在 target exit 2）。P2-review「标记不豁免 R1/R2/R3 负向用例」已落实（check-platform-assumptions.bats:198-227）。
- **§2.2 helper**：P2 detect_python + `export PYTHON` ↔ fixtures.bash:7-11；P2 §2.3 create_python_shim_bin（排除 `$BATS_TEST_TMPDIR` + 内嵌绝对路径）↔ fixtures.bash:21-32 完全一致。
- **§2.8 bc→awk**：P2 设计（awk '{s+=$1} END{print s+0}'）↔ agate-extract-context.sh:128 逐字一致；P4-review 实测空目录→0、多文件→3。
- **§2.9 CI**：P2 复用 windows matrix 模式 ↔ protocol-tests.yml:8-56（bats job matrix `[ubuntu-latest, windows-latest]` + `defaults.run.shell: bash` + 每步 `PYTHONIOENCODING: utf-8`）+ :58-75（platform-scan 双平台，Linux 阻断 / Windows 等价性证明）。
- **§2.4 PATH**：P2 `env -u PATH` 构造 ↔ 实测 check-tdd-red.bats 无 `PATH="/usr/bin:/bin"` 字面（grep = 0）、TD.1b/TDD.F8 语义保留（P6 BDD-10/11）。
- **§2.6 /tmp**：P2 逻辑路径→`$BATS_TEST_TMPDIR` + 样例文本 `# scan-exempt:` ↔ 实测 check-tdd-red.bats:146,155、check-tdd-red-formatter.bats:97,105 均带标记且内容原样 ✓。
- **§2.7 编码**：P2 PYTHONIOENCODING + cp1252 模拟 ↔ ci-gate-backstop.bats 文件级导出 + cp1252 用例（P4-review §3.4 实测）。

### 3.4 P2 gate_commands ↔ P5 执行结果

- P2-design.md §5 gate_commands.P5 四命令 ↔ P5-test-results/unit.md 判定汇总表（4/4 exit 0）：
  - `bats sanity+unit+regression+integration` → ok 733 / not ok 0（unit.md:23）
  - `python3 agate/scripts/check-protocol-consistency.py --strict` → 0 ERROR 0 WARNING（unit.md:24）
  - `shellcheck -S warning agate/scripts/*.sh` → 0 error（unit.md:25）
  - `bash agate/scripts/check-platform-assumptions.sh` → 零命中 exit 0（unit.md:26，BDD-8 闭环）

### 3.5 扫描器模式集 ↔ 实际扫描器 ↔ P6 ↔ BDD-8 零命中

- P2 §2.1 实测量（R1=15、R2=110/25 文件、R3=3、R4=6、R5=0）↔ P2 §8 minimal_validation 修订记录（R2 前字符类含引号修正后 110/25）↔ P6 BDD-2~6 fixture 检出（各规则独立验证）↔ P6 BDD-8 全树零命中（exit 0 无输出）↔ P5 命令 4 零命中。四者闭环，模式集未漂移。

### 3.6 SELF-GATE 一致性（协议本体相关改动）

- 新增扫描器 `check-platform-assumptions.sh` 与 P2 §2.1 设计一致（见 3.3 §2.1）。
- helper `detect_python`/`create_python_shim_bin` 与 P2 §2.2/2.3 设计逐字吻合（fixtures.bash:7-11,21-32）。
- `check-protocol-consistency.py:672` SCRIPT_ALIGNMENT_ANCHORS 已补 `check-platform-assumptions.sh` 锚点（P4 §1.1 声明，CHECK 9 反向覆盖），P5 consistency 0 ERROR 0 WARNING 佐证。
- 产品脚本改动面符合 P1 §6：除 bc→awk + 新增扫描器外无其他产品脚本改动（P4 §3 声明 + P6 BDD-28 全量回归佐证）。

## 4. 未决项清零

- P1-requirements.md：无行首 `[NEED_CONFIRM]`（仅 :217 `[NO_NEED_CONFIRM]` 标记 + SUGGEST 项，均已采纳落实）→ 清零 ✓
- P6-acceptance.md：无 `[BLOCKER]` / `[DEVIATION-CRITICAL]`；P2/P4 亦无 → 清零 ✓
- P4-implementation.md §6 遗留（Windows bats 安装命令 I7 supplementable / CI 可能暴露日志外用例）：均标注 supplementable，不构成一致性缺口。

## 5. 审查结论

- [BLOCKER] 数量：0
- [DEVIATION-CRITICAL] 数量：0
- DESIGN_GAP 配对：1/1（readlink 决策，REVIEWED 见 §1）
- SCOPE+ 闭环：已闭环（P1 scope_resolved + P2 §9 #1 已处理）
- 跨文件检查项：全部引用具体锚点（P1-requirements.md BDD-N / P2-design.md §2.x / P4-implementation.md §1.x / P6-acceptance.md / P5-test-results/unit.md / 实际文件:行号）

**Summary**: consistency PASS — BLOCKER=0, DEVIATION-CRITICAL=0, DESIGN_GAP 未配对=0
