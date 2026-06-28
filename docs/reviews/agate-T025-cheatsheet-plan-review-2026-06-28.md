---
type: review
source: docs/plans/agate-T025-cheatsheet-2026-06-28.md
trace_id: agate-T025-cheatsheet-plan-review-2026-06-28
created: 2026-06-28
status: done
---

# T025 Cheatsheet 计划专家评审

> 评审对象：`docs/plans/agate-T025-cheatsheet-2026-06-28.md`（3 项动作：新增 gate-cheatsheet.md + 两处引用）
> 评审焦点：新机制引入的一致性风险、与现有协议的冲突、实际使用场景验证

---

## 问题 1：gate 命令三处重复，cheatsheet 是第四处

当前 agate 已有三处包含 gate 判定命令：

1. `dispatch-protocol.md` L501-514「可判定门槛规范」表——完整定义
2. `state-machine.md` L286-295 单步函数步骤 5——按阶段列举
3. `state-machine.md` L76-127 状态转移规则——形式化条件

cheatsheet 将是**第四处**。每次 gate 规则变更（T022 有 7 项），四处都要同步。当前一致性检查脚本 `check-protocol-consistency.py` 不覆盖 cheatsheet——需要扩展，否则 cheatsheet 会成为漂移源。

**判定**：如果做 cheatsheet，必须同步扩展一致性检查脚本覆盖它。但这增加了落地成本，且引入新机制（cheatsheet）的维护负担可能抵消它节省的"找判定规则"时间。

## 问题 2：cheatsheet 命令与实际协议不一致

计划中 cheatsheet 的 P3/P4/P5 命令与协议实际规则有偏差：

| Gate | 计划 cheatsheet | 协议实际规则 | 偏差 |
|------|----------------|------------|------|
| P3 | `{project_test_runner} {test_dir} -q 2>&1 \| tail -1` | `scripts/check-tdd-red.sh exit 0` | cheatsheet 绕过了专用脚本，直接跑 test runner |
| P4 | `{project_test_runner} -q 2>&1 \| tail -1` | `git log --oneline -1 确认 P4 commit` | P4 gate 不跑测试，只看 commit |
| P5 | `{project_test_runner} -q 2>&1 \| tail -1` | 从 P2 `gate_commands` 读取（B7 规则） | P5 gate 命令由 P2 动态声明，不是固定 pytest |
| P6 | `grep -cE '^\s*- (PASS\|FAIL)'` | P1 每条 BDD 标记 PASS/FAIL + vision-analyst blocker_count==0 | cheatsheet 漏了 vision-analyst 条件 |

**根因**：cheatsheet 试图把动态的、上下文相关的 gate 规则压缩成一行静态命令，但 agate 的 gate 规则本身不是静态的——P5/P6 的命令来自 P2 的 `gate_commands` 字段，P3 有专用脚本，P4 看 commit 不看测试。

**判定**：cheatsheet 的"每阶段一行命令"假设与 agate 的 gate 规则设计冲突。agate 的 gate 规则是分层的（静态定义 + 动态注入），不能压成一行。

## 问题 3：P3 check-tdd-red.sh 的 bug 应修脚本，不应绕过

T025 暴露的 `check-tdd-red.sh` 用裸 `pytest` 导致假绿灯，是**脚本 bug**，不是协议设计问题。正确做法是修脚本（用 P0-brief 的 `executor_env` 里的 test runner 路径），不是在 cheatsheet 里绕过脚本直接跑 test runner。

cheatsheet 绕过 `check-tdd-red.sh` 意味着：P3 gate 的"只允许 assertion failure，拒绝 collection error"判定逻辑丢失了——直接跑 test runner 只能看到 failed>0，无法区分 assertion failure 和 collection error。

**判定**：修脚本，不绕过。

## 问题 4："导航索引"定位的实际收益存疑

计划声称 cheatsheet 解决"主 Agent 每次从三个协议文件中提取判定规则的重复劳动"。但：

- 主 Agent 在步骤 0 已读 8 个协议文件（含 dispatch-protocol.md 和 state-machine.md），gate 规则已在上下文中
- 单步函数步骤 5 的按阶段列举已经是一份紧凑参考（8 行，L286-295）
- "找判定规则"的 30-90s 静默时间，真正花在"找"上的可能不多——T025 复盘的思考墙 #1（P3 脚本 bug 调试 3-4 分钟）和 #2（P2 评审双循环读全文）都不是"找规则"的问题

**判定**：cheatsheet 解决的可能不是真正的瓶颈。真正的瓶颈是（a）gate 失败时的诊断成本和（b）产出文件全文阅读成本——cheatsheet 不解决这两个。

## 问题 5："异常时必须读产出全文"的警告不可强制执行

计划在 cheatsheet 头部加警告"异常时必须读产出全文，不可仅凭 exit code 跳过分析"。但这是文本约束，不是可判定约束。Agent 倾向于走阻力最小路径——如果 cheatsheet 给了"exit 0 = 通过"的快速通道，Agent 就会用它，不管警告怎么写。

agate 的核心设计是"可判定的下限"。如果 cheatsheet 的正常路径是"跑命令 → exit 0 → next"，那这个路径本身应该就是完整的 gate 判定——不需要"异常时再读全文"的补充。如果需要补充，说明 cheatsheet 的命令不完整，不应该作为独立参考。

**判定**：要么 cheatsheet 的命令完整覆盖 gate 判定（那就不需要"异常时读全文"），要么 cheatsheet 不完整（那就不应该作为独立参考）。两者矛盾。

---

## 评审结论

cheatsheet 的动机（降低 gate 判定的信息获取成本）是合理的，但实现方式（新增第四份 gate 命令文档）引入的问题比它解决的问题多：

1. 四处重复 → 一致性维护负担
2. 静态一行命令 vs 动态 gate 规则 → 信息丢失
3. 绕过专用脚本 → 判定逻辑降级
4. "导航索引"定位 vs "异常时读全文" → 自相矛盾
5. 不可强制的警告 → Agent 会走捷径

**建议：不做 cheatsheet，改用内联优化。**

具体方向：在 `state-machine.md` 单步函数步骤 5 的按阶段列举中，把每阶段的 gate 命令从自然语言描述改为可直接复制执行的 shell 命令。这是一处修改（不是新增文件），不增加重复，且主 Agent 步骤 0 已读此文件——不需要额外导航。
