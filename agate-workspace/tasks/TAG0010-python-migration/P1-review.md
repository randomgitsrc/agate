---
phase: P1
task_id: TAG0010-python-migration
type: review
parent: P1-requirements.md
trace_id: TAG0010-P1-20260814
status: approved
created: 2026-08-14
agent: requirements-review
---

# P1 需求基线复评（round 2，requirements-review）

> 复评对象：修订后 P1-requirements.md（修复轮，仅 3 项 must-revise 相关处）
> 复评方式：独立重扫 worktree 全部相关文档（rg -o 逐次计数）+ 逐字核对 BDD-3/4/6 与表 C 同步点 3 的修订文本
> 结论：**approved**。3 项 must-revise 全部修订到位，与修复轮 dispatch-context 的主 Agent 决策方向逐项吻合。

---

## 复评范围

按派发指令只核 3 项 must-revise，其余已核查通过项（表 A/C/D/E、隐含需求五维度、裁剪三态、P1 纯净性、BDD 格式）抽查确认未被动过。

---

## 修复项 1：表 B 是否按上轮评审实测数据全面更新 —— 修订到位 ✓

独立重扫结果（`rg -o` 逐次计数，与修订后表 B 逐格对照）：

| 文档 | 表 B 记 | 独立重扫实测 | 判定 |
|------|---------|-------------|------|
| dispatch-protocol.md | 10 脚本/22 次（check-gate 6、p6-provenance 4、inject-card 3、state-transition 2、p6-evidence 2、tdd-red 1、scope-resolved 1、p6-format 1、archive 1、retreat 1） | 完全一致（逐格：6/4/3/2/2/1/1/1/1/1，合计 22） | 一致 |
| WORKFLOW.md | 12 脚本（check-gate 7、p6-provenance 3、p6-evidence 2、pruning 2、tdd-red 1、scope-resolved 1、state-transition 1、changelog 1、state-yaml 1、retrospective 1、workspace-resolve 1、pre-commit-gate 1） | 逐格全对，组件合计 22 | 一致 |
| state-machine.md | 6 脚本（check-gate 5、tdd-red 6、p6-provenance 2、state-transition 2、scope-resolved 1、pruning 1） | 逐格全对，合计 17 | 一致 |
| SETUP.md | 4 脚本（summary 4、install-hook 3、workspace-resolve 3、next-card 1） | 逐格全对，合计 11 | 一致 |
| UPGRADING.md | 8 脚本（install-hook 3、summary 3、check-gate 3、p6-evidence 1、debt 1、pre-commit-gate 1、platform-assumptions 1、migrate-workspace 1） | 逐格全对，合计 14 | 一致 |
| LIMITATIONS.md | p6-provenance 3、check-gate 3、p6-evidence 1、pruning 1 | 逐格全对（p6-provenance 按行口径计 3，第 118 行同行两次已注脚说明，逐次口径 4——口径差异已显式标注，不影响 P4 引用同步） | 一致 |
| orchestrator-template.md | check-gate 1、inject-card 1、workspace-resolve 2、install-hook 1、summary 1、migrate-workspace 1 | 逐格全对，合计 7 | 一致 |
| assets/templates/task-files.md | p6-provenance 1、scope-resolved 1、tdd-red 3、state-yaml 1 | 逐格全对，合计 6 | 一致 |
| assets/templates/handoff-template.md | workspace-resolve 1、pre-commit-gate 1、count-tests 1、summary 1 | 逐格全对，合计 4 | 一致 |
| phase-cards/P6-acceptance.md | p6-format 5 | 一致 | 一致 |
| assets/templates/tech-debt-template.md | check-debt 3 | 一致 | 一致 |

- 迁后目标列与表 C 命名一致：同名换后缀 .py；3 个 hook 保留薄壳；install-hook.sh → install-hook.py（P1-requirements.md:142 注记）。
- 上轮 3 个核心差距（dispatch-protocol 5/7→10/22、WORKFLOW 4/5→12 脚本、UPGRADING 漏列 check-gate 等）全部补齐。
- 注：修复轮 dispatch-context 写「WORKFLOW 12 脚本/21 次」，实测组件合计为 22（上轮评审头条「21 次」系算术笔误，其逐组件数据合计即 22）；analyst 采用实测 22 与上轮评审逐组件数据一致，属正确校正。

**锚点**：P1-requirements.md:146-161（表 B 全行）。

---

## 修复项 2：BDD-3 是否按主 Agent 决策方向改写 —— 修订到位 ✓

主 Agent 决策方向（P1-dispatch-context-analyst-fix.md:31-32）三条，逐条核对修订文本：

1. **范围 = 全部 `agate/scripts/*.py`（既有 18 + 迁移新增）**：BDD-3 When 明确 `ruff check agate/scripts/*.py`（P1-requirements.md:268），标题「覆盖全部 agate/scripts/*.py」（:266）；§2.5 也声明「ruff 检查范围 = 全部 `agate/scripts/*.py`（既有 18 个 + 迁移新增）」（:80）✓
2. **规则集（pyproject.toml）作为 P2 交付物、目标既有 py 零违规**：BDD-3 Given 明确「P2 已交付 pyproject.toml 规则集（select 子集 + target-version=py38），使既有 18 个 py 在选定规则集下可过（边界见 §2.5）」（:267）；§2.5 明确「pyproject.toml（select 子集 + target-version=py38）由 P2 设计交付，须让既有 18 个 py 在选定规则集下零违规」+ 保留实测 70 错误基线（UP032×35/BLE001×9/PLW1510×6）（:81）✓
3. **隐含需求声明「既有 py 允许最小调整但 P1 只声明边界」**：§2.5「既有 py 不改功能，但允许加注释/极小调整（不改变行为）以满足规则集；P1 只声明此边界，不列具体调整」（:81）✓

BDD-3 原「不可满足」缺陷消除：Given 引入 P2 交付规则集这一前置，使 When/Then 变为可二值判定且在本任务范围（P2 交付规则集 + 既有 py 零违规目标）下可达成。

**锚点**：P1-requirements.md:266-269（BDD-3）、:80-81（§2.5）。

---

## 修复项 3：install-hook.sh 去留 + BDD-4/BDD-6 澄清 —— 修订到位 ✓

主 Agent 决策方向（P1-dispatch-context-analyst-fix.md:35-36）四条，逐条核对：

1. **install-hook.sh 一并 py 化（→ install-hook.py）**：表 B 迁后目标约定「install-hook.sh 一并 py 化（→ install-hook.py，安装器非 hook 入口，无 shebang 解析硬约束，见 BDD-4）」（P1-requirements.md:142）；表 B 各行 install-hook 迁后目标同步（orchestrator-template:147、SETUP:153）；表 C 同步点 3「install-hook.sh 条目随 py 化移除（install-hook.sh → install-hook.py，不再有 sh 豁免对象，见 BDD-4）」（:218）✓
2. **保留 sh 薄壳只有 3 个 hook 入口（pre-commit-gate / commit-msg-self-gate / pre-push-gate）**：表 B 迁后目标约定「仅 3 个 hook 入口保留 sh 薄壳（pre-commit-gate.sh / commit-msg-self-gate.sh / pre-push-gate.sh）；install-hook.sh 一并 py 化」（:142）；表 C CHECK 9 中 pre-commit-gate/pre-push-gate 锚点标注「保留薄壳 sh」（:190,:207）✓
3. **BDD-4 Then 明确「受扫 .sh 与 3 个保留薄壳一致」**：BDD-4 Then「exit 0，且受扫 `.sh` 文件集合与 3 个保留 hook 薄壳（pre-commit-gate.sh / commit-msg-self-gate.sh / pre-push-gate.sh）一致——install-hook.sh 不属保留薄壳」（:274）；Given 同步「install-hook.sh 一并 py 化 → install-hook.py，见 §2.5 与表 B」（:272）✓
4. **BDD-6 前置条件（P2 先行对既有 py 跑扩展扫描器确认洁净度）**：BDD-6 Given「且 **P2 已先行对既有 18 个 py 跑扩展后的扫描器确认洁净度（或列出预期违规并规划处理）**（前置验证见 §2.6）」（:283）；§2.6 专项条目「BDD-6 前置验证」（:89）✓

上轮「install-hook 去留表述冲突」「BDD-6 扫描范围洁净度未验证」两处歧义均消除。

**锚点**：P1-requirements.md:142（表 B 约定）、:218（表 C 同步点 3）、:271-274（BDD-4）、:282-285（BDD-6）、:89（§2.6）。

---

## 抽查：其余部分未受修订破坏

- BDD 编号连续 1-10、`#### BDD-NN:` 格式、单 Given-When-Then（P1-requirements.md:256-305）✓
- frontmatter 未变：risk_level: high / phases 全 8 / packages / domains: [backend, cli] / change_type: refactor / capability_requirements 两 available（:11-29）✓
- 无 [NEED_CONFIRM]；[NO_NEED_CONFIRM] 保持（:309）；grep 到的 2 处 NEED_CONFIRM 为表 C 关键字列「NEED_CONFIRM 三值声明」与 NO_NEED_CONFIRM 本身，非阻塞标记 ✓
- 表 C CHECK 9 涉 sh 锚点仍 32 条（33 行含表头），与上轮一致；表 A 仍 30 行 ✓

---

## 总体结论

**status: approved**

3 项 must-revise 逐项复核结果：
- 修复项 1（表 B 系统性低估）：**修订到位**——11 个文档逐格独立重扫全部一致，上轮全部差距补齐，迁后目标列与表 C 命名统一。
- 修复项 2（BDD-3 不可满足）：**修订到位**——主 Agent 决策方向三条（全量 py 范围 / P2 pyproject.toml 交付 / 既有 py 最小调整边界）全部落盘，BDD-3 转为可判定可达成。
- 修复项 3（install-hook 去留 + BDD-4/6 澄清）：**修订到位**——install-hook.sh 一并 py 化、3 个 hook 保留薄壳、BDD-4 Then 与 3 薄壳集合一致、BDD-6 P2 前置验证全部显式声明。

已核查通过项未被动过（抽查确认）。需求基线可推进 P2。
