---
review_date: 2026-07-25
reviewer: protocol-alignment-review
change_summary: v0.23.0 release — version badge + CI fetch-tags fix
files_changed: [README.md, .github/workflows/protocol-tests.yml]
---

# 协议-脚本对齐审查

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | ALIGNED |
| A4 | 测试覆盖 | ALIGNED |
| A5 | 下游影响 + 文档传播 | ALIGNED |
| A6 | 锚点表覆盖 | ALIGNED |
| A7 | 设计原则一致性 | ALIGNED |

## 逐项审查

### A1: 文档→脚本对齐

README.md version badge 从 v0.16.0 更新到 v0.23.0，与最新 git tag 一致。CI workflow 新增 `fetch-tags: true` 确保 bats job 能获取 tag 用于 CON.6 检查。无 gate 行为变化。

**结论**：ALIGNED

### A2: 脚本→文档对齐

不涉及脚本逻辑改动。

**结论**：ALIGNED

### A3: 一致性连锁 + 反向传播

CON.6（version badge 同步）此前因 CI 不 fetch tags 而误报 ERROR。修复后 CI 能正确获取 tag，CON.6 检查结果与本地一致。

**结论**：ALIGNED

### A4: 测试覆盖

445 bats / 0 fail。CON.1 和 CON.6 在本地和 CI 均通过。

**结论**：ALIGNED

### A5: 下游影响 + 文档传播

无下游影响。badge 更新是纯展示层。

**结论**：ALIGNED

### A6: 锚点表覆盖

不涉及新 gate 脚本。

**结论**：ALIGNED

### A7: 设计原则一致性

ADR-003（最小约定）：CI fetch-tags 修复是最小必要改动 ✅

**结论**：ALIGNED
