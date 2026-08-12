> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。

---
phase: post-P8
generated_by: 主 Agent（无 agate-inject-card.sh 可用阶段卡片，本次是 T001 READY 之后、合并 main 之前的终审，不属于 P0-P8 任一具体阶段，手写指引不注入卡片）
task_id: T001
role: protocol-alignment-review
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。

### 背景

T001（agate v0.40.0 结构化数据改造）已完成 P0-P8 全流程，`.state.yaml` phase=READY，`feat/v2.0` 分支已 tag `v0.40.0`。此前分两次做过 self-gate 语义审查：一次覆盖流A+B+C+D+fixture修复（`293924f..f476834`），一次覆盖 P6回退修复（`f476834..afe758a`）——这之后的 commit（P5重跑/P6验收/P7一致性/P8发布）均未触碰 `agate/` 协议本体或 `agate/**/*.md`，不在 self-gate 触发范围内。

**用户在决定是否合并 `feat/v2.0` 到 `main`（会让 `~/.agate` 切到 v0.40.0，本机所有项目生效）之前，要求做两件事**：

### 任务一：对整个改造版做一次全新的、不依赖旧报告的完整 self-gate 审查

不是"确认之前两次报告的结论还成立"，是**从头重新审查一遍 `main..feat/v2.0` 里所有 self-gate 范围内的改动**，当作一个完整的版本变更来看待（而不是分段看）。

1. **审查范围**：`git diff main..feat/v2.0 -- agate/ SELF-GATE.md`（这是完整版本变更，不是某个 commit 的 diff）。工作目录：`/home/kity/oclab/agate/.worktrees/v2.0`，当前分支已经是 `feat/v2.0`（HEAD 即 tag `v0.40.0`）。
2. **走完角色定义里的 A1-A7 全部七项**，每项独立给出结论 + 原文行号引用，不要因为"之前审过"就简化。
3. **可以参考**（不是照抄）之前两份报告作为交叉核对的辅助材料：
   - `docs/reviews/agate-alignment-review-2026-08-10.md`（含两次增量审查内容）
   但结论必须是你自己独立核实后得出的，不是转述旧报告。
4. **测试基线**：`bash agate/tests/scripts/count-tests.sh` 现在应输出 **597**；`bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/` 应为 **603/603**；`shellcheck -S warning agate/scripts/*.sh` 应无输出；`python3 agate/scripts/check-protocol-consistency.py` 应 0 ERROR（含 CHECK 7，此时 tag v0.40.0 已存在，badge 应与其一致）。全部自己重新跑，不要引用历史数字。
5. **产出**：新建 `docs/reviews/agate-alignment-review-final-2026-08-10.md`（独立文件，不追加进旧文件——这是终审，值得单独留档），格式同角色定义给的模板（A1-A7 结论汇总表 + 逐项审查 + 待闭环事项清单）。

### 任务二：分析 self-gate 机制本身是否需要因这次改造而升级

这是一个元层面的问题：`SELF-GATE.md`（self-gate 流程定义）和 `agate/assets/review-roles/protocol-alignment-review.md`（你正在扮演的这个角色的定义）本身，是否因为 v0.40.0 引入的新机制（frontmatter schema 校验器、字段级 presence 双读、P6/P7 结构化计数、任务编号规则硬切）而需要更新？请具体分析以下几点，每点给出"需要升级"或"不需要，理由是"的明确结论：

1. **`SELF-GATE.md` 的触发文件清单**（当前：`agate/scripts/*.sh`、`agate/scripts/*.py`、`agate/*.md`、`agate/**/*.md`、`SELF-GATE.md`）——v0.40.0 新增了 `agate-frontmatter-check.py` 这类校验器，触发清单的通配符 `agate/scripts/*.py` 是否已经覆盖？有没有新的文件类别（比如新的 fixture 生成规范）本该触发但没有被覆盖？
2. **`protocol-alignment-review.md` 的"反向传播常见路径"表**——现在协议里有了新的核心机制（frontmatter 双读 + schema 校验），这张表要不要新增一行，比如"改了 `agate/assets/*/SCHEMAS 定义或迁移字段集`→ 应传播到 XXX"这种？参照现有表里"BDD 编号格式"那一行的详细程度。
3. **A6"锚点表覆盖"审查项**——CHECK 9 锚点表机制本身现在有 38 条，且新增了 `check-frontmatter.sh` 这类"校验产出物格式而非协议规则关键词"的新型锚点。protocol-alignment-review 角色定义里 A6 项的描述是否还准确覆盖这种新型锚点，还是需要补充说明？
4. **self-gate 的两层设计**（Layer 0 CHECK 9 脚本结构兜底 + Layer 1 LLM 语义审查）在"产出物本身现在也有机器校验"（frontmatter schema 校验器）的新格局下，边界是否清晰——self-gate 审的是"协议文档与脚本的一致性"，frontmatter schema 校验器审的是"subagent 产出物格式是否合规"，这两者会不会有重叠或者遗漏地带？值得在 `SELF-GATE.md` 里补充说明这个边界吗？
5. **DESIGN_GAP 机制**（本次 T001 自己就用了 7 次）——`SELF-GATE.md`/`protocol-alignment-review.md` 要不要显式提及"self-gate 审查中如果发现代码里有 `[DESIGN_GAP:]` 标记，应该怎么处理"（目前这个机制主要在 P4/P7 阶段内部使用，self-gate 审查跨阶段做整体审查时，是否也该核对 DESIGN_GAP 的处理状态）？

**产出**：在同一份 `docs/reviews/agate-alignment-review-final-2026-08-10.md` 文件末尾追加"## Self-gate 机制升级分析"一节，逐条给出上述 5 点的结论。如果结论是"需要升级"，请给出具体的修改建议（不需要你自己去改 `SELF-GATE.md`/`protocol-alignment-review.md`，只需要写清楚建议改什么、改成什么样，供主 Agent 后续决定是否派发实施）。

### 约束

- **不要修改任何代码/协议文档**——纯审查+分析角色，只写报告。
- **不要执行任何 git 命令**（不 commit，不 merge，不 tag）。
- 分阶段落盘：留痕文件 `docs/reviews/agate-alignment-final-2026-08-10-01.progress.md`，开始前先 `rm -f` 清空。

### 输入文件（自己读）

- `agate/assets/review-roles/protocol-alignment-review.md`（你的角色定义）
- `SELF-GATE.md`
- `git diff main..feat/v2.0 -- agate/ SELF-GATE.md`（完整版本变更，自己跑读）
- `docs/reviews/agate-alignment-review-2026-08-10.md`（之前两次审查，交叉核对辅助材料）
- `docs/tasks/T001-v2.0-structured/P2-design.md`（设计依据）
- `docs/tasks/T001-v2.0-structured/P4-implementation.md`（实现记录，含全部 7 条 DESIGN_GAP）
- `docs/tasks/T001-v2.0-structured/P7-consistency.md`（一致性检查最终结论）
- `agate/adr.md`（ADR-007，架构决策参考）
</dispatch_guide>

<objective_info>
- 环境状态：worktree `feat/v2.0`，HEAD = tag `v0.40.0`（commit b22c7b0）。`main` 分支仍是 e5540fc（v0.35.0），尚未合并。
- T001 全流程状态：P0-P8 全部通过，`.state.yaml` phase=READY。
- 已知历史：本任务途中出过 1 次真实 P6→P4 回退（check-p6-format.sh bug）+ 1 次 C8 review CRITICAL 修复迭代，均已闭环。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
