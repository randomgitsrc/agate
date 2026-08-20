---
phase: P7
task_id: TAG0017-toolchain-fixes
type: consistency
parent: P2-design.md
trace_id: TAG0017-P7-20260820
status: draft
created: 2026-08-20
agent: consistency-reviewer
blocker_count: 0
deviation_count: 0
deviation_critical_count: 0
design_gap_count: 0
design_gap_reviewed_count: 0
---

# P7 一致性交叉检查 — TAG0017-toolchain-fixes

对 P1-P6 全部产出 + self-gate（protocol-alignment-review）审查报告做跨文件一致性交叉检查。逐项检查结果如下，全部附实质锚点（源文件节名 + 独立命令核验）。

## 1. DESIGN_GAP 配对核查

对 P1-requirements.md / P2-design.md / P3-test-cases.md / P4-implementation.md / P5-test-results/unit.md / P6-acceptance.md 六个产出文件做行首标记扫描：

```
$ /usr/bin/grep -n "^\s*\[DESIGN_GAP" <六个文件>
(全部 0 命中)
```

`P4-implementation.md§无 DESIGN_GAP / SCOPE+ / CLARIFY` 节正文明确写"5 个批次的进度记录均未出现 `[DESIGN_GAP]`/`[SCOPE+]`/`[CLARIFY]` 标记……本次实现无 DESIGN_GAP/SCOPE+/CLARIFY"。self-gate 审查报告（`agate-alignment-review-2026-08-20-TAG0017.md§已知偏离核对`）独立核实"本次审查发现的 A2/A3b MISALIGNED……未见于该任务的任何 P4/P4-review 记录，不属于已被 P7/P4-review 核实接受的已知偏离"，同样确认 P4 无 DESIGN_GAP 声明。

**判定**：`design_gap_count: 0`，`design_gap_reviewed_count: 0`（无 DESIGN_GAP 可配对，无需转抄 REVIEWED 标记）。dispatch-context 约束 2 预期属实，核实通过。

## 2. SCOPE+ 闭环核查

```
$ /usr/bin/grep -n "^\s*\[SCOPE+\]" <P1/P2/P4 三文件>
(全部 0 命中)
```

`P1-requirements.md§1 需求复述` 明确锁定 5 条 issue（DEBT0010/11/12/14/15）范围，并声明"若 P2 设计阶段发现需改动超出以上 5 条锁定范围，须先停下与用户确认，不擅自扩大"。`P2-design.md` 全篇（含 §1.2「不改什么」、§2 候选方案取舍）未出现任何范围外新增声明；`P4-implementation.md` 的改动清单（19 个文件，17 个对应 `P2-design.md§1.1 改什么` 表逐条覆盖、2 个为主 Agent bookkeeping）与 P2 声明范围完全对应，无范围外扩张。

**判定**：本任务全程无 `[SCOPE+]` 声明，无需 `[SCOPE_RESOLVED]` 配对，闭环状态天然成立（起点即闭环）。dispatch-context 约束 3 预期属实，核实通过。

## 3. P1 BDD 数量与 P6 验收结果数量匹配

`P1-requirements.md§4 BDD 验收条件` 列出 BDD-1 至 BDD-12（4 功能分组：分组1 BDD-1~6、分组2 BDD-7~8、分组3 BDD-9、分组4 BDD-10~12），共 12 条。

`P6-acceptance.md` frontmatter `pass: 12, fail: 0`，正文逐条列出 `PASS BDD-1` 至 `PASS BDD-12`（`P6§功能分组1`~`P6§功能分组4`），编号与分组归属与 `P1§4 BDD验收条件` 逐条对应，无跳号无遗漏：
- `P6§功能分组1` PASS BDD-1~6 ↔ `P1§功能分组1`
- `P6§功能分组2` PASS BDD-7~8 ↔ `P1§功能分组2`
- `P6§功能分组3` PASS BDD-9 ↔ `P1§功能分组3`
- `P6§功能分组4` PASS BDD-10~12 ↔ `P1§功能分组4`

内容层面亦逐条核对（非仅数量对齐）：如 `P1§BDD-2`（"真实失败仍判 A 类，不因新增排除逻辑被放宽"）对应 `P6§PASS BDD-2`（"`test_bdd_2_timeout_seconds_declared_real_a_class_failure_stays_a_class` 实跑通过"），语义与测试用例名一致，非张冠李戴。

**判定**：12/12 精确匹配，内容映射正确，不存在"数量对但内容错位"问题。

## 4. P2 候选方案（4组）与 P4 五批实现的关系——非不一致，是有意设计

`P2-design.md§2 候选方案` 确认 4 个功能分组各自独立探索 2 候选，A 组（推荐）均获选（`P2§2.1候选A`/`§2.2候选A`/`§2.3候选A`/`§2.4候选A` 逐一"选择理由：候选 A"）。

`P2-design.md§6 dispatch_plan 说明` 与 frontmatter `dispatch_plan.batches` 拆为 5 批：`fg1-parser-scripts`/`fg1-doc-boundary`/`fg2-self-gate-naming`/`fg3-strict-mode-code`/`fg4-windows-python-probe`。

**核实**：这不是"4 组 vs 5 批"数量不一致，而是有意拆批设计——功能分组 1（DEBT0010+DEBT0015）因涉及 `phase-cards/P2-design.md`「gate_commands 声明」节这一与功能分组 3（DEBT0012）共享的文档落点（`P2§1.3 风险R1`："`phase-cards/P2-design.md`「gate_commands 声明」节被 DEBT0010/DEBT0015（BDD-5）与 DEBT0012（BDD-9）两个……功能分组同时需要增补"），被拆为 `fg1-parser-scripts`（代码半）+ `fg1-doc-boundary`（文档半，同时吸收 DEBT0012 的文档半以避免同一文件被两批各改一次）。功能分组 3（DEBT0012）相应地也拆为文档半（并入 `fg1-doc-boundary`）+ 代码半（`fg3-strict-mode-code`）。

`P4-implementation.md` 5 批标题与 `P2-design.md§6` 批次表逐一对应（`P4§批次1 fg1-parser-scripts`~`P4§批次5 fg4-windows-python-probe`），`P4§批次2` 正文明确复述"与 `fg3-strict-mode-code` 同属 DEBT0012，但落点文件不同……本批次因 P2-design.md §1.3 R1 与 DEBT0015 合并为一批"，与 P2 的设计意图完全吻合。

**判定**：4 组→5 批的差异是文件级批次拆分策略（跨批共享文件冲突规避），非方案数量与实现数量的不一致，二者吻合。

## 5. P2 packages/domains 与 P4 实际改动文件范围一致性

`P1-requirements.md`/`P2-design.md` frontmatter 均声明：
```
packages: [gate-scripts, hooks-shell, phase-cards, self-gate-template, platform-notes, agent-roles]
domains: [protocol-docs, gate-scripts]
```

对照 self-gate 审查报告（`agate-alignment-review-2026-08-20-TAG0017.md` frontmatter `files_changed`，16 个文件）+ P4-review-fix 轮新增的 `agate/scripts/README.md`（共 17 个 implementer 产出文件，与 `P4-implementation.md` 正文"17 个是 P2-design.md §1.1「改什么」表列明的代码/文档文件（全部覆盖，无遗漏）"一致），逐一映射到 package：

| package | 对应改动文件 |
|---|---|
| `gate-scripts` | `agate/scripts/agate_common.py`、`agate-gate-missing-cmds.py`、`agate-gate-p5-count.py`、`agate-read-gate-commands.py`、`agate-read-p5-commands.py`、`check-protocol-consistency.py`、`README.md` |
| `hooks-shell` | `agate/scripts/pre-commit-gate.sh`、`commit-msg-self-gate.sh`、`pre-push-gate.sh` |
| `phase-cards` | `agate/phase-cards/P2-design.md`、`P4-implementation.md` |
| `self-gate-template` | `SELF-GATE.md`、`agate/assets/review-roles/protocol-alignment-review.md` |
| `platform-notes` | `agate/platform-notes.md`、`AGENTS.md` |
| `agent-roles` | `agate/assets/execution-roles/architect.md` |

全部 17 个文件均落位在声明的 6 个 package 内，无越界改动（如未触碰 `state-machine.md`/`dispatch-protocol.md`/`WORKFLOW.md`，`P2§1.2不改什么`与 self-gate 审查`A3a`均已核实这些文件本不该被本次改动触及）；`domains: [protocol-docs, gate-scripts]` 与改动性质（协议 Markdown 文档 + gate 脚本）完全对应，无 frontend/UI 相关 domain（`ui_affected: false` 与实际无 UI 改动一致）。

**判定**：packages/domains 声明与 P4 实际改动范围精确对应，无遗漏无越界。

## 6. CRITICAL 修复生效核实——`--strict` → `--strict-errors-only`

`P4-review.md§CRITICAL复核` 记录该 CRITICAL 涉及两处文件：`agate/phase-cards/P2-design.md`（协议范例文档）与本任务自身 `agate-workspace/tasks/TAG0017-toolchain-fixes/P2-design.md§5 gate_commands`。独立命令核验（本次 P7 复核，非转述）：

```
$ /usr/bin/grep -n "strict-errors-only\|strict_errors_only" agate/phase-cards/P2-design.md agate-workspace/tasks/TAG0017-toolchain-fixes/P2-design.md
agate/phase-cards/P2-design.md:169:  P5_consistency: "check-protocol-consistency.py --strict-errors-only"
agate/phase-cards/P2-design.md:172:（推荐用法说明……）
agate-workspace/tasks/TAG0017-toolchain-fixes/P2-design.md:168-169:
  # P4 review 修正：原 --strict 在当前 WARNING 基线下阻塞本任务自身 P5，改用 --strict-errors-only
  P5_consistency: "python3 agate/scripts/check-protocol-consistency.py --strict-errors-only"
```

两处均已确认是 `--strict-errors-only`，与 `P4-review.md§CRITICAL复核` 记录的修复内容一致，未回退。

另核实脚本本身实现（`agate/scripts/check-protocol-consistency.py:78-86`）：`is_gate_meta_key` 与互斥组、`main()` 尾部分支逻辑均已按 self-gate 审查报告`A1`节引用的代码片段落地，`P5-test-results/unit.md§命令2` 的独立执行记录（`--strict-errors-only` → exit 0, 0 ERROR + 314 WARNING）与 `P4-review.md§独立全量核验` 的复核结果（同为 exit 0）互相印证。

**判定**：CRITICAL 修复已在最终代码状态中生效，`agate/phase-cards/P2-design.md` 与本任务自身 `P2-design.md` 均已同步，无回退迹象。

## 7. self-gate MISALIGNED（`agate/scripts/README.md`）修复生效核实

`agate-alignment-review-2026-08-20-TAG0017.md§A2/A3b` 记录初次发现 `agate/scripts/README.md` 未同步 `--strict-errors-only`（MISALIGNED），`§复评（retry round 1）` 记录修复后转为 ALIGNED。独立命令核验（本次 P7 复核）：

```
$ /usr/bin/grep -n "strict-errors-only" agate/scripts/README.md
173:python3 agate/scripts/check-protocol-consistency.py --strict-errors-only
181:日常任务默认用 `--strict-errors-only`；`--strict` 留给专门做 WARNING 债务清理的任务主动选用。两者互斥，不可同时传入。
184-186:（三态退出码说明，含 --strict-errors-only 分支）
```

确认三处修复内容（用法示例行 173、选用指引行 181、退出码三态说明 184-186）均已在最终文件状态中存在，与 self-gate 审查报告记录一致。`self-gate 审查报告§闭环状态` 最终结论"A1-A7 现全部 ALIGNED……闭环完成，可 commit"，本次 P7 独立复核未发现推翻该结论的证据。

**判定**：self-gate MISALIGNED 修复已生效，A1-A7 全 ALIGNED 状态在最终代码/文档状态中成立。

## 8. P4 实现路径与 P2 方案设计吻合性（补充抽查）

抽查 `P2-design.md§1.1改什么` 表中关键落点与 `P4-implementation.md` 对应批次描述、及实际代码文件的三方一致性：
- `is_gate_meta_key` 判据设计（`P2§1.1`："`key.endswith(("_formatter","_timeout_seconds"))`"）↔ `P4§批次1`（同一描述）↔ 实测 `agate/scripts/agate_common.py:78` 定义存在，4 个解析脚本（`agate-read-gate-commands.py:33`/`agate-gate-missing-cmds.py:22`/`agate-gate-p5-count.py:25`/`agate-read-p5-commands.py:31`）均已改用 `is_gate_meta_key`，三方吻合。
- R7 风险（`project_module` 精确匹配不强行并入共享函数）↔ `P4§批次1`："保留 `project_module` 精确匹配独立分支，不强行合并进 `is_gate_meta_key`，见 P2-design.md §1.3 R7" ↔ 实测 `agate-gate-missing-cmds.py:22`：`if is_gate_meta_key(k) or k == "project_module":`，三方吻合，设计约束未被实现阶段遗漏或简化。

**判定**：抽查的关键设计约束在实现中均未走样。

## 9. 未决项清零核查

对 P1-P6 六个产出文件行首标记做统一扫描（含本次 P7 独立执行的命令核验）：

```
$ /usr/bin/grep -n "^\s*\[NEED_CONFIRM\|^\s*\[BLOCKER\]\|^\s*\[DEVIATION-CRITICAL\]" <六个文件>
(全部 0 命中)
```

`P1-requirements.md§5 待确认清单` 显式声明 `[NO_NEED_CONFIRM]`，正文注明"本次未发现需要人工拍板业务方向的开放问题"，两处技术实现选择（DEBT0012 修复路径、DEBT0014 判据阈值）均已明确"留给 P2 architect 按方案空间自行设计，不构成 P1 层面的方向性分歧"，且已在 `P2§2.3`/`§2.4` 落地为候选方案取舍，非遗留未决项。`P5-test-results/unit.md`/`P6-acceptance.md` 均显式声明 `[NO_NEED_CONFIRM]`。

**判定**：无残留 `[NEED_CONFIRM]`/`[BLOCKER]`/`[DEVIATION-CRITICAL]`，未决项清零确认通过。

## 10. 诚实性边界核查（Windows 验证声明，补充）

`P1-requirements.md§verification_env` 与 `P2-design.md§1.3 R6` 均要求 Windows 相关验证不得夸大声称"已在真实 Windows 环境实测通过"。核对：
- `P3-test-cases.md§批次fg4-windows-python-probe` 开头"诚实边界（P0-brief 约束 3，强制）"声明明确、`§BDD-12` 含"负面断言（诚实性护栏）"用例。
- `P6-acceptance.md§PASS BDD-10`："Windows 真实场景由 CI matrix `pytest -m windows_smoke` 冒烟兜底（本地无法真实复现，未夸大声称已在真实 Windows 环境实测通过）"。
- self-gate 审查报告`§A1`最后一段引用 `platform-notes.md` 新增段落"明确声明'未在真实 Windows 环境下触发过 Store 占位符场景本身……不代表已在 Windows 环境中复现并验证通过'"。

三处独立文件的措辞均遵守同一诚实性约束，无夸大声称，跨文件一致。

## 总结

| 检查项 | 结果 |
|---|---|
| DESIGN_GAP 配对 | design_gap_count=0，design_gap_reviewed_count=0（核实确无声明） |
| SCOPE+ 闭环 | 全程无 SCOPE+ 声明，闭环天然成立 |
| P1 BDD 数量 ↔ P6 验收数量 | 12/12 精确匹配，内容映射正确 |
| P2 4组候选 ↔ P4 5批实现 | 差异为有意拆批设计（共享文档落点合并），非不一致 |
| packages/domains ↔ P4 改动范围 | 17 文件全部落位声明的 6 个 package，无越界 |
| CRITICAL 修复（--strict-errors-only） | 已在 `agate/phase-cards/P2-design.md` 与任务自身 `P2-design.md` 生效 |
| self-gate MISALIGNED（README.md）修复 | 已生效，A1-A7 全 ALIGNED |
| 未决项清零 | 无残留 [NEED_CONFIRM]/[BLOCKER]/[DEVIATION-CRITICAL] |

**结论：无 BLOCKER，无 DEVIATION-CRITICAL，无未配对 DESIGN_GAP，无未闭环 SCOPE+。P1-P6 全部产出跨文件一致，可进入 P8。**
