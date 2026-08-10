> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。

---
phase: post-P8
generated_by: 主 Agent（T001 已 READY，本次是合并 main 前的最后一轮 polish，不重开 P0-P8 状态机）
task_id: T001
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。

### 背景

`docs/reviews/agate-alignment-review-final-2026-08-10.md`（合并前终审）发现 3 处轻微 MISALIGNED（纯文档层面，不影响功能）+ 5 项 self-gate 机制升级分析中 3 项建议升级。用户已确认要修，本次一次性处理全部 6 项。

### 目标

修复终审报告"待闭环事项清单"的 3 项 + 落实"Self-gate 机制升级分析"建议升级的 3 项，均为纯文档编辑，不涉及任何脚本逻辑/测试代码改动。

### 约束

1. **待闭环事项 1**：`agate/tests/README.md:37` 把 `check-frontmatter.bats` 的用例数 `11` 改为 `10`（终审已核实实际为 10）。
2. **待闭环事项 2**：以下 8 处 frontmatter 可复制样例块的 `task_id: T001` 改为 `task_id: TAG0001`（保留原有的 `# 替换为实际任务编号` 注释不动，只改示例值本身，与流 D 改造后的新格式风格统一）：
   - `agate/assets/execution-roles/analyst.md:42`
   - `agate/assets/execution-roles/architect.md:46`
   - `agate/assets/execution-roles/verifier.md:147`
   - `agate/assets/templates/task-files.md:129`
   - `agate/assets/templates/task-files.md:233`
   - `agate/assets/templates/task-files.md:316`
   - `agate/assets/templates/task-files.md:369`
   - `agate/phase-cards/P1-requirements.md:54`
   - `agate/phase-cards/P2-design.md:58`
   - `agate/phase-cards/P6-acceptance.md:56`
   - `agate/phase-cards/P7-consistency.md:59`

   （终审报告列了 8 处但实际逐行定位后 `task-files.md` 一个文件里有 4 处，加上 4 个角色卡/phase-cards 文件各 1 处，共 11 处具体行——**改之前自己先 `grep -n "task_id: T001" agate/assets/ agate/phase-cards/` 精确核实实际出现的每一行，以实际 grep 结果为准，不要死板对照上面这份可能不精确的清单**，逐行确认改的是"可复制样例块"里的 task_id，不要误改到其他上下文里的 `T001` 字符串，比如 CHANGELOG.md 或 docs/tasks/ 下的任务自身产出文件——那些不能改，`T001` 是本任务真实编号，不是示例占位符）。
3. **待闭环事项 3（可选，你可以判断处理方式）**：`docs/archived/plans/agate-test-plan-2026-07-01.md` 已严重过期（附录 A 还是"148 个核心测试用例"的极早期版本）。终审报告给了两个选项：更新数字为当前值，或在文档顶部补注"已归档，数字以 count-tests.sh 为准，不再维护"。**选后者**（补注更省事且更诚实——这个文档已经跟不上迭代速度，与其每次改造都要记得同步一份基本没人看的历史归档文档，不如明确标注它不再维护）。在文档最顶部（标题下方）加一行注：`> ⚠️ 本文档已归档，数字可能与当前代码库不一致。测试用例数以 \`bash agate/tests/scripts/count-tests.sh\` 实测为准，本文档不再同步维护。`
4. **self-gate 升级 #2**：在 `agate/assets/review-roles/protocol-alignment-review.md` 的"反向传播的常见路径"表（约第 30-39 行）新增一行，内容参考终审报告"Self-gate 机制升级分析"第 2 点给出的具体建议文本（终审报告里已经写好了完整的表格行内容，照抄过去，格式对齐表格既有行的 Markdown 表格语法）。
5. **self-gate 升级 #3**：在 `agate/assets/review-roles/protocol-alignment-review.md` 的 A6 审查项描述后追加一句说明，内容见终审报告"Self-gate 机制升级分析"第 3 点给出的具体建议文本（"注：CHECK 9 部分锚点...仍需 A1 逐条人工核对"这一句）。
6. **self-gate 升级 #5**：在 `agate/assets/review-roles/protocol-alignment-review.md` 的"审查原则"节（当前 1-5 条）新增第 6 条"DESIGN_GAP 优先核查"，内容见终审报告"Self-gate 机制升级分析"第 5 点给出的具体建议文本（含"审查原则"新增第 6 条 + "输出格式"结论枚举补充 `[KNOWN_DEVIATION: ...]` 标注约定两部分）。
7. **不实施 self-gate 升级 #4**（Layer 0/Layer 1 边界说明）——终审报告明确判定"不需要强制升级，可选"，本次不做，除非你判断顺手加一句成本极低（如果做，加在 `SELF-GATE.md` 触发条件小节下方，内容见终审报告该点给出的建议文本；不做也完全可以，这条不是必须项）。
8. **不要修改任何脚本文件**（`agate/scripts/**`）、**不要修改测试文件**（`agate/tests/**` 除约束 1 那一行）、**不要修改 T001 自身的任务产出文件**（`docs/tasks/T001-v2.0-structured/**`，那些是历史记录不能动）。
9. **自查**：改完后跑 `python3 agate/scripts/check-protocol-consistency.py` 确认 0 ERROR（CHECK 1 会重新校验你新增/改动的 YAML frontmatter 样例块语法仍然合法）。

### 上游关联

- `docs/reviews/agate-alignment-review-final-2026-08-10.md`（本次修复的完整依据，"待闭环事项清单"表 + "Self-gate 机制升级分析"节都有具体建议文本，照抄即可，不需要你重新构思措辞）

### 输入文件（自己读）

- `docs/reviews/agate-alignment-review-final-2026-08-10.md`（全文，尤其"待闭环事项清单"表和"Self-gate 机制升级分析"节）
- `agate/tests/README.md`
- `agate/assets/review-roles/protocol-alignment-review.md`
- `docs/archived/plans/agate-test-plan-2026-07-01.md`
</dispatch_guide>

<objective_info>
- 环境状态：worktree `feat/v2.0`，HEAD `b22c7b0`（T001 READY 后）。这是合并 main 前的最后一轮 polish，不是重新打开 T001 的 P0-P8 状态机（`.state.yaml` 保持 phase=READY 不动）。
- 先跑 `grep -n "task_id: T001" agate/assets/execution-roles/*.md agate/assets/templates/*.md agate/phase-cards/*.md` 得到本次真正要改的精确行号清单，不要凭约束 2 给的清单猜。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
