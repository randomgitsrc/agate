> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。

---
phase: post-P8
generated_by: 主 Agent（T001 已 READY，用户要求用刚升级的 self-gate 机制再审一轮）
task_id: T001
role: protocol-alignment-review
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。

### 背景

上一轮终审（`docs/reviews/agate-alignment-review-final-2026-08-10.md`）用**旧版** `protocol-alignment-review.md`（升级前）审出 3 处轻微 MISALIGNED，均已修复（commit `087214b`）。该 commit 同时**升级了 `protocol-alignment-review.md` 自身**（新增"DESIGN_GAP 优先核查"审查原则第 6 条 + 反向传播路径表新增一行 + A6 说明补充）。

用户现在要求：**用升级后的这版角色定义，对整个改造版重新审查一遍**——目的是验证升级本身是否真的起作用（比如"DESIGN_GAP 优先核查"这条新原则，能不能让审查过程更准确地区分"已知可接受偏离"和"真正需要修的问题"），并且如果这次审查发现任何问题，要**迭代修复到干净为止**，不是只报告。

### 任务

1. **完整读你自己的角色定义**（这次是刚升级过的版本，注意新增的第 6 条审查原则、反向传播表新增行、A6 补充说明——这些你自己就是审查执行者，要用上）：`agate/assets/review-roles/protocol-alignment-review.md`
2. **审查范围**：`git diff main..feat/v2.0 -- agate/ SELF-GATE.md`（完整版本变更，此时 HEAD 已包含 commit `087214b` 的 polish + self-gate 升级本身）。
3. **走完 A1-A7 全部七项**，这次明确应用新增的"DESIGN_GAP 优先核查"原则——遇到看起来像 MISALIGNED 的地方，先查 `docs/tasks/T001-v2.0-structured/P4-implementation.md`/`P7-consistency.md` 是否已有 `[DESIGN_GAP_REVIEWED:]` 记录，按新原则处理（已被 P7 接受的不判 MISALIGNED，用 `[KNOWN_DEVIATION:]` 标注）。
4. **重点检查 self-gate 自身升级的那部分改动**（`agate/assets/review-roles/protocol-alignment-review.md` 本身的 diff）：这是"self-gate 机制审查 self-gate 机制自身改动"的递归场景（`protocol-alignment-review.md` 里"反向传播的常见路径"表本就有一行"`SELF-GATE.md` 或 `protocol-alignment-review.md` → self-gate 机制自身的递归适用"），确认这次升级本身的措辞、格式、逻辑是否清晰自洽，有没有引入新的歧义或矛盾。
5. **测试基线独立重跑**：`bash agate/tests/scripts/count-tests.sh`（应为597）、`bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/`（应为603/603——如果这次遇到 `ARCH.4` 那条单独失败，先重跑一次确认是否为已知的秒级时间戳碰撞 flaky，不要直接判定为回归）、`shellcheck -S warning agate/scripts/*.sh`、`python3 agate/scripts/check-protocol-consistency.py`。
6. **如果发现任何 MISALIGNED（非 DESIGN_GAP 豁免的）**：不要自己改代码/文档，**在报告里清楚列出**，返回时明确告诉主 Agent 发现了什么、建议怎么改——主 Agent 会再派一轮 implementer 修复，然后可能需要你再审一次，直到干净。
7. **产出**：新建 `docs/reviews/agate-alignment-review-final-v2-2026-08-10.md`（区别于上一轮的 `-final-` 文件，这次用 `-final-v2-` 后缀，独立留档）。
8. 分阶段落盘：留痕文件 `docs/reviews/agate-alignment-final-v2-2026-08-10-01.progress.md`，开始前 `rm -f` 清空。
9. 不要修改任何代码/文档，不要执行任何 git 命令。

### 输入文件（自己读）

- `agate/assets/review-roles/protocol-alignment-review.md`（升级后的角色定义，本次审查依据）
- `docs/reviews/agate-alignment-review-final-2026-08-10.md`（上一轮终审，交叉参考）
- `docs/tasks/T001-v2.0-structured/P4-implementation.md` + `P7-consistency.md`（DESIGN_GAP 优先核查要用到）
- `git diff main..feat/v2.0 -- agate/ SELF-GATE.md`（完整版本变更，自己跑读）
</dispatch_guide>

<objective_info>
- 环境状态：worktree `feat/v2.0`，HEAD `087214b`（终审 polish + self-gate 升级 commit 之后）。
- 上一轮终审（旧版角色定义跑的）：A1/A4/A5/A6/A7 ALIGNED，A2/A3 MISALIGNED×3（已修复）。这次用升级后的角色定义重新审查，预期能验证升级是否让判断更准确。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
