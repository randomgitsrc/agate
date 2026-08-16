---
phase: P4
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0014
role: architect
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

修复轮（P4 发现）：修复 P2-design.md 的 YAML 语法错误，使 check-protocol-consistency.py CHECK 1 通过。

### 约束

- **修复点（唯一）**：{AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/P2-design.md L256（files_to_read 块内）：
  ```
  - path: agate/SELF-GATE.md
    why: self-gate 派发模板（commit message self-gate-review: + protocol-alignment-review）
  ```
  `why:` 值含未加引号的冒号（`self-gate-review: +`），YAML 解析报 `mapping values are not allowed here`。修复方式：给 `why:` 值加双引号（注意值内含双引号时转义）或改写避免裸冒号。
- **范围**：只改这一处 YAML 语法，不改任何设计内容、不改 P1 基线、不改协议文件。其他 YAML 块（L216/L228/L266）已验证解析 OK，不要动。
- **输出路径硬约束**：直接修改 {AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/P2-design.md。

### 上游关联

- P4 implementer 实现完成后，consistency 检查发现 P2-design.md YAML 块解析失败（CHECK 1 ERROR）。
- P2-design.md 是 architect 在 P2 产出的设计文档，本次是格式修复。

### 输入文件

- {AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/P2-design.md（修复对象）
</dispatch_guide>

<!-- AGATE_CARD_START -->
{由 agate-inject-card.py 注入，禁止手写}
<!-- AGATE_CARD_END -->

<objective_info>
- 错误定位：L256 `why: self-gate 派发模板（commit message self-gate-review: + protocol-alignment-review）`，YAML 报 mapping values are not allowed here
- 验证命令：`python3 agate/scripts/check-protocol-consistency.py --root /home/kity/oclab/agate/.worktrees/agate-TAG0014` 应不再报 P2-design.md CHECK 1 ERROR
- 其他 YAML 块已通过，只修 L256
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
