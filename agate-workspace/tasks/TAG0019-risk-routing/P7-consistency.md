---
phase: P7
task_id: TAG0019-risk-routing
type: consistency
parent: P2-design.md
trace_id: TAG0019-P7-20260821
status: draft
created: 2026-08-21
agent: consistency-reviewer
# ── v2.0 机器计数 ──
blocker_count: 0
deviation_count: 1
deviation_critical_count: 0
design_gap_count: 0
design_gap_reviewed_count: 0
code_map_new_files_count: 0
code_map_reviewed_count: 0
---

# TAG0019 风险分路由（ceremony routing，RM-AG0031）— P7 一致性检查

> 状态标记：`[PROD_NOT_TOUCHED]`（仅审查协议本体文件与任务产出，无任何生产环境接触）。
> 审查对象：P1-requirements.md / P2-design.md / P3-test-cases.md / P4-implementation.md（+P4-progress.md / P4-review.md）/ P5-test-results/ / P6-acceptance.md（+P6-evidence/）+ worktree 实现（`agate/scripts/agate-risk-score.py`、`check-routing.py`、`check-gate.py` gate_p7）+ `{AGATE_WORKSPACE}/agents/CODE-MAP.md`。
> 结论摘要：**BLOCKER 0 / DEVIATION-CRITICAL 0 / DESIGN_GAP 未配对 0（无残留声明）/ SCOPE+ 增补 0（空真闭环）/ CODE-MAP DRIFT 1（WARNING 级不阻断）/ DEVIATION 1 簇（I9 文档同步三处未落地，非 CRITICAL，P8 收尾）**。

## 1. DESIGN_GAP 配对（检查清单 1）

核查方法：对 P1-P4 全部产出（P3-test-cases.md / P3-progress.md / P4-progress.md / P4-implementation.md / P4-review.md）grep 行首 `[DESIGN_GAP:` 声明，并与 P4-implementation.md 全文比对（与 gate_p7 交叉核对层同口径：`^\s*-?\s*\[DESIGN_GAP:`）。

**结论：design_gap_count = 0 / design_gap_reviewed_count = 0，无残留 [DESIGN_GAP] 声明，无待配对项（配对空闭环）。**

- P4-implementation.md 全文无行首 `[DESIGN_GAP:`，亦无 [BASELINE_CHANGE]（P1 §BDD 基线 15 条未被 P4 修改）；gate_p7 交叉核对：P4 声明数 0 ≤ P7 转抄数 0 ✓。
- 派发线索追踪（dispatch-context 提示两项）：
  - 「P3 test-designer 曾标 [DESIGN_GAP(测试缺陷)] 于 test_bdd_2 / test_bdd_5」→ 最终落盘核对：**P4-progress.md:22-23** 记录 P3 test-designer 以「测试代码缺陷修复」闭环——test_bdd_2（双仓库 FileExistsError → 改用两个独立 git_repo）、test_bdd_5（src 父目录缺失 → `_stage` helper 自建父目录），仅改测试代码、未动被测模块，修复后 `test_agate_risk_score.py` 11 passed；两处均**未以 [DESIGN_GAP:] 格式残留**于任何最终产出。
  - 「core 批曾报 [DESIGN_GAP] 于 P3 测试」→ **P3-progress.md:23** 红灯确认记录（30 failed 全部因被测模块未实现：CLI No such file / importlib FileNotFoundError / 文档断言未写入；明确「无 A 类测试 bug」），属 TDD 红灯先行证据，非实现偏差声明。
- gate T090 WARNING 评估（dg_count=0 时扫 P4 关键词「设计偏差|design gap|未列入|gap:」）：P4-implementation.md 均不命中（仅含 [SKELETON_DEVIATION]/[CODE_MAP_EXEMPT] 登记性标记，非设计偏差字面）→ 不触发 WARNING。

## 2. SCOPE+ 闭环（检查清单 2）

核查：P1-requirements.md 全文件 grep `[SCOPE+]` / `[SCOPE_RESOLVED]`；P4 产出 grep `[SCOPE+]`；frontmatter `scope_resolved` 字段。

- P1-requirements.md：**无 `[SCOPE+]` 条目**（§7 与正文均无增补声明；frontmatter 注释 `scope_resolved: []`）。
- P4-implementation.md / P4-progress.md：**无 `[SCOPE+]` 增补**（实现报告无 scope 外改动，dispatch-context 亦确认"P4 无 [SCOPE+] 新增"）。
- 全 tasks 目录 grep：`[SCOPE_RESOLVED]` 仅出现在派发模板（dispatch-context 引用文本）中，无实际任务内声明。

**结论：SCOPE+ 增补集合 = ∅ → 闭环空真成立**（无增补项即无"未纳入基线"项；无 [SCOPE_RESOLVED] 声明是当前形态的正确表达，不存在"有增补未闭环"的情形）。

## 3. 跨文件一致性（检查清单 3，逐条附源文件锚点）

| # | 检查项 | 交叉引用锚点（源文件:节/行） | 判定 |
|---|--------|------------------------------|------|
| 3a | P2§packages ↔ 交付范围 | **P2 §frontmatter `packages`** == P1 §frontmatter = [agate-protocol, agate-scripts, agate-tests]；P4 §交付清单 + P4-progress docs-sync 批 | ✓ 三包全覆盖：agate-scripts（agate-risk-score.py / check-routing.py / frontmatter-check / md-field-get / pre-commit-gate / summary / consistency）、agate-protocol（P1 卡 / requirements-review / role-system / review-mapping / P2 卡 / P4 卡 / WORKFLOW / CONTEXT / UPGRADING / scripts-README）、agate-tests（2 新 unit + 4 既有测试扩展 + integration）。**P8 release bump 范围在 P7 时点未产出**，以本表为 P8 对照基线（P7 卡 3 的「P2 packages 与 P8 bump 一致」移交 P8 复核） |
| 3b | P1§BDD 数量 ↔ P6 验收数量 | **P1 §BDD-1..15**（grep `^#### BDD-` = 15 条连续）vs **P6 §BDD 逐条**（grep `^- PASS BDD-` = 15 行，frontmatter pass: 15 / fail: 0） | ✓ 15 = 15，编号 BDD-1..15 一一对应（P6 每行引用同号 BDD，无 P7 卡常见错误 2 的"数量对但内容映射错"） |
| 3c | P4 实现路径 ↔ P2 方案 B | **P2 §1.4 选方案 B**（独立 check-routing.py + importlib 复用）vs **P4 §实现摘要** + check-routing.py:56-63（`_md_field`/`_read_p1`/`_staged_source_count` importlib 复用 + `score_task` 不 subprocess） | ✓ 实现形态与方案 B 完全吻合（BDD-10 证据 bdd-10-same-source.log 同源） |
| 3d | P2 candidate_count=3 方案 B ↔ P4 实际 | **P2 §frontmatter `candidate_count: 3`** + §1.1-1.3 三候选 vs P4 实际（独立脚本 + import 复用，pre-commit-gate.py:338-343 2j/2j.1 并列挂载） | ✓ 一致 |
| 3e | P2§gate_commands ↔ P5 实际执行 | **P2 §4 gate_commands**（P5 全量 / P5_consistency / P5_platform 7 文件集 / P5_count_tests）vs **P5-test-results/unit.md** 重试轮逐条 | ✓ 全量 1099 passed / 1 env-premise I1（非缺陷，P6 BDD-7 GIT_DIR 探针补测通过）；consistency 0 ERROR（318 WARNING 存量，worktree 自己脚本）；platform 7 文件（2 脚本 + 5 测试）R1-R5 0 命中；count-tests 1102 ≥ 749 基线，只增不减 |
| 3f | P5-test-results / P6-evidence 引用可追溯 | **P6 §Evidence 清单**（14 个 log 文件）vs P6 §BDD 各 PASS 行引用 | ✓ 抽查 bdd-10-same-source.log（exit 0/2 + importlib 复用行号 56-59）与 bdd-15-consistency.log（exit 0 / 0 ERROR / 318 WARNING / 5 个具名消费点）均与对应 PASS 行描述一致 |

## 4. 未决项清零（检查清单 4）

- **P1 无行首 [NEED_CONFIRM]**：P1 §7 行首 `[NO_NEED_CONFIRM]` 负向声明；全文件无行首 [NEED_CONFIRM]（P1-progress.md:40 GATE-FIX 记录已清理字面 [NEED_CONFIRM]）。
- **SUGGEST 两项采纳情况（dispatch-context 要求注明）**：
  - **SUGGEST-1**（check-routing 扩展现有 check-pruning.py vs 独立脚本）→ **已采纳为方案 B**（P2 §1.4 理由 4：核心诉求是"复用不重造"而非物理合并，importlib 复用 _md_field/_read_p1/_staged_source_count 满足意图且避开改名破坏）。
  - **SUGGEST-2**（M1 与 M2 合并为同一实现任务）→ **已自然合并**：P4 core 批 + docs-sync 批同实现阶段落地，D1-D5 同批交付，无"字段已声明但无 gate 保障"中间态。
- **无 [BLOCKER]**：P4-review.md 终裁 approved（组长规则：eng + cso 均 approved，全票无 BLOCKER）。
- **无 [DEVIATION-CRITICAL]**；**1 簇非阻断 [DEVIATION]（deviation_count: 1，deviation_critical_count: 0）**：
  - **I9 五处文档同步面 3/5 未落地**：P1 §2 I9 明确「ceremony/算分机制说明须同步：P1 卡 / analyst.md / task-files.md / dispatch-protocol.md / requirements-review.md——五处任缺一处即文档漂移」；P2 §0.1 C 表将 `agate/assets/execution-roles/analyst.md:63-66`（样例块加 ceremony 行）、`agate/assets/templates/task-files.md:127-160`（frontmatter 块加 ceremony 行）、`agate/dispatch-protocol.md:931`（评审检查项升级为「声明 vs diff 证据」）列为修改点——实测三文件 case-insensitive grep `ceremony` **均 0 命中**，修改点未实现；已落地 2/5 = P1 卡（ceremony 字段 + fail-closed checklist + M3 锚，P2 §2.2）与 requirements-review.md（审声明核对项，P6 BDD-11 PASS 锚点）。
  - 严重性评估：**非 CRITICAL**——功能链（frontmatter 三节点 / check-routing fail-closed / 审声明职责）均已实现且有测试（BDD-6/7/8/9/11 PASS）；三处缺口属**消费端文档完整性**（analyst 写 P1 时无可复制 ceremony 样例、模板用户无 ceremony 行、派发清单仍为旧单句），fail-closed 缺省 standard（BDD-8）兜底无功能暴露；P6 附注已如实记录 dispatch-protocol.md:931（本 P7 扩展确认 analyst.md / task-files.md 同缺）。**建议主 Agent 在 P8（文档同步收尾）补三处 ceremony 说明**，不构成本任务 gate 阻断。
- **附注观察（非偏差，P8 复核）**：test_docs_assertions.py（P3 新增测试文件）未列入 P2 P5_platform 7 文件清单（P2 §4 注「P3 产出后按实际变更文件集调整」未落实该行）；其 /tmp 字面已在 P4 fix3 清除（P5 重试轮 test_bdd_8 转绿），补扫亦 0 命中；BDD-13 Given 判据对象为 `agate/scripts/*.py`（测试文件伴随扫描），不违反验收口径。P8 复核 P5_platform 清单与实际变更文件集对齐。

## 5. CODE-MAP 核对（检查清单 5）

- `{AGATE_WORKSPACE}/agents/CODE-MAP.md` **存在**（本仓库为 dogfooding 实例，文件头部明确「后续任务新增/挪动协议文件时，P4 implementer 应更新本文件；P7 consistency-reviewer 核对同步/偏离」）。
- P4-implementation.md 新增文件核对表：`[SKELETON_DEVIATION: 无骨架机制]`（骨架确实无，无 P2-skeleton.md ✓）与 `[CODE_MAP_EXEMPT: 无 CODE-MAP 机制]`——**CODE-MAP 豁免声明与文件实际存在不符**。
- CODE-MAP.md「scripts」模块描述（gate 族 / 一致性族 / 状态族）**未登记**本任务新增的 `agate-risk-score.py` / `check-routing.py`。

**结论：偏离。[CODE_MAP_DRIFT: agate-risk-score.py / check-routing.py 未登记进 agents/CODE-MAP.md（P4 新增文件核对表声明"[CODE_MAP_EXEMPT: 无 CODE-MAP 机制]"与文件实际存在不符）]** —— WARNING 级不阻断（角色卡：DRIFT 不阻断；CODE-MAP 依赖方向未违反，新脚本属 scripts→phase-cards/templates 消费方，无反向依赖注入）。建议主 Agent 在 P8 或后续维护任务补登记两脚本至 CODE-MAP.md scripts 模块。
- frontmatter：`code_map_new_files_count: 0` / `code_map_reviewed_count: 0`（机制未采用口径，dispatch-context 指示；gate 两层校验：内部一致性 0<0 false ✓、转抄核对 P4 行首标记数 0 > 0 false ✓）；实际偏离已用 [CODE_MAP_DRIFT] 正文记录。

## 6. 汇总（实质锚点对照）

| gate 断言 | 锚点（本文件 §） | 状态 |
|-----------|------------------|------|
| BLOCKER=0 | §1 DESIGN_GAP 配对（0/0）+ §4 无 [BLOCKER] 残留（P4-review 终裁 approved） | ✓ |
| CRITICAL=0 | §3 跨文件 6 项逐条锚点（P2§packages / P1§BDD-1..15 / P4 §实现摘要 / P2§gate_commands / P6 §Evidence）+ §4 deviation_critical_count: 0 | ✓ |
| SCOPE+ 闭环 | §2 SCOPE+ 增补 = ∅（空真闭环） | ✓ |
| DESIGN_GAP_REVIEWED 配对 | §1 无声明 → 无待配对项（design_gap_count=0 / design_gap_reviewed_count=0） | ✓ |

- **BLOCKER 数 = 0；DEVIATION-CRITICAL 数 = 0；DESIGN_GAP 未配对 = 0；SCOPE+ 增补 = 0（闭环）；CODE-MAP DRIFT = 1（WARNING 级）；DEVIATION = 1 簇（I9 文档同步 3 处未落地，非 CRITICAL，P8 收尾）。**
- 本报告为一致性审查结论（status: draft）；gate 通过与推进判定由主 Agent 执行。