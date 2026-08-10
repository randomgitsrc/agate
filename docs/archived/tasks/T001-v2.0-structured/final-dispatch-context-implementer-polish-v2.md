> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。

---
phase: post-P8
generated_by: 主 Agent（第二轮 polish，修复 self-gate 升级验证轮发现的 2 个收尾问题）
task_id: T001
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。

### 背景

`docs/reviews/agate-alignment-review-final-v2-2026-08-10.md`（用升级后角色定义做的验证轮审查）确认"DESIGN_GAP 优先核查"原则本身有效，但发现该次升级自己留了 2 个收尾问题，本次修复。

### 目标

1. **修复问题一（A3b，`SELF-GATE.md` 内嵌派发模板未同步）**：在 `SELF-GATE.md:112` 附近（"变更触发模式"派发模板的审查清单部分）和 `SELF-GATE.md:168` 附近（"全量审查模式"派发模板的审查清单部分）各补一句提示。具体文本（终审报告已给出，照抄）：
   ```
   若发现 A1/A2/A3 疑似不一致，先按角色文件"DESIGN_GAP 优先核查"原则查
   `docs/tasks/{Txxx}/P4-implementation.md`/`P7-consistency.md` 是否已有
   `REVIEWED-ACCEPTED` 记录，避免把已知偏离误判为新 MISALIGNED。
   ```
   放在两处审查清单文本的合适位置（紧跟清单本身，不要打断清单结构）。**先用 `grep -n "逐项检查 A1" SELF-GATE.md` 精确定位这两处的当前行号**（终审报告给的行号是审查时刻的快照，可能因之前的改动有偏移，以实际 grep 结果为准）。

2. **修复问题二（角色文件自身文本矛盾，二选一收敛）**：`agate/assets/review-roles/protocol-alignment-review.md` 里三处文本对"DESIGN_GAP 覆盖的偏离该不该叫 MISALIGNED"表述不一致（审查原则第6条说"不判MISALIGNED"，本次新增的输出格式说明却称其为"MISALIGNED项"，旧有的闭环规则表对MISALIGNED又是无条件"必须修复"）。**采用终审报告建议的方案一**：把"输出格式追加说明"那句话的措辞改掉，使其与原则 6 一致——即"这类偏离最终结论是 ALIGNED，不是 MISALIGNED，只是要在 ALIGNED 结论下追加 KNOWN_DEVIATION 标注说明曾有偏离"。

   具体改法：找到 `protocol-alignment-review.md` 里"三态结论（ALIGNED/MISALIGNED/NEEDS_HUMAN_REVIEW）不变，但 **MISALIGNED 项**如果对应一条已被 P7 接受的 DESIGN_GAP..."这句话（这是上一轮 polish 新加的），改写为终审报告"建议 1"给出的措辞：
   ```
   若某一审查项本应判为 MISALIGNED，但差异点完全对应一条已被 P7 接受的
   DESIGN_GAP，则按原则 6 结论记为 ALIGNED，并在该项下追加
   `[KNOWN_DEVIATION: ...]` 标注，以便读者知晓这里曾存在过字面偏离、
   已被正式核实接受（而非"从未出现过差异"）。
   ```
   **不需要改闭环规则表**（选方案一之后，闭环规则表的 MISALIGNED 行不会再被这类情况触发，因为这类情况现在明确走 ALIGNED 路径，不产生矛盾，不用加例外条款）。

3. **可选：顺手修一处更早遗留的问题**（终审报告"待闭环事项清单"第3项，非本次改动引入，但既然要碰 `SELF-GATE.md`，可以顺手处理）：`SELF-GATE.md` 里 "A1-A7" 和 "A1-A6" 两种计数并存（角色文件确实有 A1-A7 共 7 项，`SELF-GATE.md` 部分地方写成了"A1-A6"，遗漏了 A7）。**先 `grep -n "A1-A[67]" SELF-GATE.md` 精确定位全部出现位置**，统一改为 "A1-A7"（因为角色文件确实是 7 项，不是 6 项）。这一步你可以做，也可以判断成本/收益后跳过——终审报告明确这不是本轮改动引入的问题，不强制。

### 约束

- **只改这 2 个文件**：`SELF-GATE.md`、`agate/assets/review-roles/protocol-alignment-review.md`。
- 不要修改任何脚本/测试文件，不要修改 `docs/tasks/T001-v2.0-structured/` 下的任务产出文件。
- 改完后跑 `python3 agate/scripts/check-protocol-consistency.py` 确认 0 ERROR。

### 输入文件（自己读）

- `docs/reviews/agate-alignment-review-final-v2-2026-08-10.md`（本次修复的完整依据，"A3b"节 + "Self-gate自身升级自洽性核查"专题第4/5点 + "待闭环事项清单"表）
- `SELF-GATE.md`
- `agate/assets/review-roles/protocol-alignment-review.md`
</dispatch_guide>

<objective_info>
- 环境状态：worktree `feat/v2.0`，HEAD `087214b`。这是 T001 READY 后的第二轮 polish。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
