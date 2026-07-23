# 任务看板 (Task Board) — active-tasks-template.md

> 复制此文件到 `{project_root}/docs/tasks/active-tasks.md`，清空示例数据后使用。
> `.state.yaml` 是单任务的权威状态，`active-tasks.md` 是全局汇总视图（主 Agent 维护，subagent 不直接改）。

---

## 任务列表

### 进行中的任务

| 编号 | 任务名称 | 状态 | 阶段 | 优先级 | 依赖 | 创建日期 | 更新日期 |
|------|----------|------|------|--------|------|----------|----------|

### 待开始

| 编号 | 任务名称 | 状态 | 阶段 | 优先级 | 依赖 | 创建日期 | 更新日期 |
|------|----------|------|------|--------|------|----------|----------|

### 已完成

| 编号 | 任务名称 | 状态 | 最终阶段 | 优先级 | 完成日期 |
|------|----------|------|----------|--------|----------|

---

## 状态符号

| 状态 | 符号 | 说明 |
|------|------|------|
| 待开始 | ⬜ | 任务已创建，P1 尚未开始 |
| 进行中 | 🔄 | 正在执行某个阶段 |
| 暂停 | ⏸️ | gate 失败超限 / 等待人工决策 |
| 已完成 | ✅✅ | P8 gate 通过 + READY |
| 已取消 | ❌ | 需求变更或不再需要 |
| 已合并 | 🔀 | 合入另一个任务 |

---

## 阶段产出

| 阶段 | 产出文件 | 门槛（见 state-machine.md） |
|------|----------|------|
| P0 | P0-brief.md | 主 Agent 亲自写，五字段非空 |
| P1 | P1-requirements.md | ≥1 条 BDD + 无行首 [NEED_CONFIRM] + 无 CAPABILITY_GAP |
| P2 | P2-design.md + P2-review.md | review.status=approved |
| P3 | P3-test-design.md | TDD 红灯正确（`check-tdd-red.sh` exit 0） |
| P4 | P4-implementation.md | 文件非空 + gate 通过 |
| P5 | P5-verification.md | 所有测试通过 |
| P6 | P6-acceptance.md + P6-evidence/ | provenance 三道审计通过 |
| P7 | P7-consistency.md | BLOCKER=0 + DESIGN_GAP 全配对 |
| P8 | P8-release.md | version bump + CHANGELOG |

> 项目可调整阶段名称（如 P1→"问题定义"），但编号 P0-P8 和门槛规则不可改。

---

## 目录结构

```
docs/tasks/
├── active-tasks.md          ← 本文件
├── T001-xxx/
│   ├── .state.yaml          ← 单任务权威状态
│   ├── P0-brief.md
│   ├── P1-requirements.md
│   ├── P2-design.md
│   ├── P7-consistency.md    ← 含 DESIGN_GAP + REVIEWED 配对
│   └── ...                  ← 其余阶段产出
└── T002-yyy/
    └── ...
```

---

## 维护规则

1. 只有主 Agent 改这个文件，subagent 不直接写
2. 每次阶段推进后，同步更新对应任务行（状态/阶段/更新日期）
3. `.state.yaml` 是权威来源——怀疑不一致时从 `.state.yaml` 全表重建
4. 新任务编号 = 当前最大编号 + 1，不复用已取消任务的编号
