# T075 复盘效率修复 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复 T075 复盘暴露的 1 个 agate 角色文件效率问题（P2.61），预期节省 ~0.5h/任务。

**Architecture:** architect 角色文件增加 gate_commands 校验清单，帮助 architect 在 P2 阶段自检声明的命令是否可执行。

P2.62（test-designer 量化断言规则）和 P2.63（dispatch-prompt 修复轮增量模式）经分析不修——前者是 LLM 推理错误非协议规则可解决，后者简化 dispatch-context 会削弱 subagent 上下文。

**Tech Stack:** Markdown（角色文件修改）

---

## 文件结构

### 修改文件

| 文件 | 改动 |
|------|------|
| `agate/assets/execution-roles/architect.md` | gate_commands 校验清单 |
| `docs/hardening-roadmap.md` | P2.61 状态更新 |

---

## Task 1: architect 角色文件增加 gate_commands 校验清单 (P2.61)

**Files:**
- Modify: `agate/assets/execution-roles/architect.md`

- [ ] **Step 1: 在质量门槛节追加校验清单**

在 architect.md 的"质量门槛"节末尾（`### DEVIATION 分类` 之前），追加一个新的 bullet：

```markdown
- **gate_commands 校验清单**（architect 声明后必须自检）：命令中的可执行文件是否存在于当前环境？（如 `python` vs `.venv/bin/python`，`pytest` vs `npx vitest`）。若使用 venv/容器，命令须包含完整路径（如 `.venv/bin/pytest`）。建议引用 Makefile target（`make test`），让 Makefile 封装环境细节。T075 教训：architect 写 `python -m pytest`，系统无 `python` 命令，P3 gate exit 127 浪费 0.5h 诊断。
```

- [ ] **Step 2: Commit**

```bash
git add agate/assets/execution-roles/architect.md
git commit -m "docs: add gate_commands validation checklist to architect role (P2.61)"
```

---

## Task 2: 更新 roadmap 状态

**Files:**
- Modify: `docs/hardening-roadmap.md`

- [ ] **Step 1: 将 P2.61 表格行改为标题块格式 + 标记已实施**

将 T075 复盘表格中的 P2.61 行：

```markdown
| P2.61 | architect 声明的 gate_commands 命令本身不可执行（如 `python` 不存在） | architect 角色文件增加 gate_commands 校验清单："命令中的可执行文件是否存在于当前环境？" | T075 AGATE-M1 | 0.5h | P1 |
```

替换为：

```markdown
**P2.61: architect gate_commands 校验清单**

**状态**：已实施
**来源**：T075 复盘 AGATE-M1（gate_commands 声明不可执行命令）
**改动**：
- architect 角色文件增加 gate_commands 校验清单（可执行文件是否存在于当前环境）
```

- [ ] **Step 2: 全量验证**

Run: `bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/`
Expected: ALL PASS

Run: `python3 agate/scripts/check-protocol-consistency.py`
Expected: 0 ERROR

- [ ] **Step 3: Commit**

```bash
git add docs/hardening-roadmap.md
git commit -m "docs: mark P2.61 as implemented"
```

---

## Self-Review

### 1. Spec coverage

| 需求 | Task |
|------|------|
| P2.61 architect gate_commands 校验清单 | Task 1 |
| roadmap 更新 | Task 2 |

### 2. Placeholder scan

无 TBD/TODO。

### 3. 不修理由

| ID | 不修理由 |
|----|---------|
| P2.62 | LLM 推理错误不是协议规则能解决的，加规则增加角色文件噪音 |
| P2.63 | 简化 dispatch-context 削弱 subagent 上下文，增加主 Agent 判断负担 |
