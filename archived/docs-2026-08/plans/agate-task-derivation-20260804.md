# Task 派生机制论证 + 设计

> 2026-08-04 | 状态：论证中

## 一、问题

当前 agate 的 task 创建是完全手动的：
1. 主 Agent 判断"任务太大要拆"
2. 主 Agent 手动在 active-tasks.md 写新 task 行
3. 主 Agent 手动创建 docs/tasks/T00X-xxx/ 目录
4. 主 Agent 手动写 P0-brief.md

**缺失的场景**：
- P1 analyst 发现"这个任务其实包含 3 个独立模块"→ 只能在 P1-requirements.md 里建议拆分，主 Agent 要手动跟进
- P2 architect 设计完发现需要"先做一个基础设施任务"→ 没有机制声明"这依赖一个还不存在的 task"
- 从 0 创建项目 → 用户说"建一个新项目"，主 Agent 需要自己拆成 T001 脚手架 + T002 认证 + T003 业务逻辑...但没有机制辅助拆分决策

## 二、现有机制的接近点

### 2.1 packages 声明

P2-design.md 声明 `packages: [core, auth, api]`。这不是 task 派生——是**一个 task 内的多包声明**。packages 决定 P5 测试命令和 P8 发布粒度，但不生成新 task。

### 2.2 active-tasks.md 依赖列

看板模板有"依赖"列，但**从未被脚本读取**——纯展示性，没有"依赖未完成则阻塞"的机制。

### 2.3 parent 字段

产出文件的 Header 有 `parent: P1-requirements.md`——这是**阶段间**的 parent（P2 的 parent 是 P1），不是**任务间**的 parent（T002 的 parent 是 T001）。

### 2.4 WORKFLOW.md L122

> 大任务（跨模块重构）| P1 拆成多个子任务，各自走 P1-P8

一句话描述，无机制支撑。P1 analyst 怎么拆？拆完怎么创建？创建完怎么管理依赖？全是手动。

## 三、核心设计决策

### 决策 1：派生声明在哪个阶段？

| 阶段 | 候选 | 判断 |
|------|------|------|
| P0 | P0-brief 写 subtasks | ❌ P0 信息不够，连需求都没分析 |
| P1 | P1-requirements.md 声明 subtasks | ✅ P1 analyst 分析完需求，最清楚是否该拆 |
| P2 | P2-design.md 声明 subtasks | ✅ P2 architect 设计完，知道是否需要前置任务 |

**选择 P1 + P2 都可声明**。P1 从需求维度拆（功能模块），P2 从技术维度拆（基础设施/依赖顺序）。

### 决策 2：声明格式

在 P1-requirements.md 或 P2-design.md 的 frontmatter 加可选字段：

```yaml
subtasks:
  - id: T002
    name: 用户认证模块
    reason: 认证独立于核心业务，可并行开发
    depends_on: []           # 空 = 可立即开始
  - id: T003
    name: 核心业务逻辑
    reason: 依赖 T001 的数据模型
    depends_on: [T001]       # T001 DONE 后才能开始
```

**id 是预分配**（不是最终编号——最终编号由 active-tasks.md 的 max+1 决定）。主 Agent 读到 subtasks 声明后，在 active-tasks.md 创建对应 task 行，分配实际编号。

**为什么不是自动**：subagent 不能写 active-tasks.md（规则：只有主 Agent 改这文件）。subtask 声明是 subagent 的建议，创建是主 Agent 的动作。

### 决策 3：依赖如何执行

active-tasks.md 的"依赖"列已有，但从未被脚本读取。**不改脚本**——依赖执行靠主 Agent 读 active-tasks.md 判断。

原因：
- 依赖关系可能很复杂（T003 依赖 T001 的 P2 产出，不是 T001 DONE）
- 机械化"依赖未完成则阻塞"可能过于死板（T003 的 P0-brief 可以在 T001 还在 P4 时就写）
- 主 Agent 的判断力比脚本更适合处理复杂依赖

**但 active-tasks.md 的依赖列需要被填充**——主 Agent 创建 subtask 时把 depends_on 值写入依赖列。

### 决策 4：subtask 的 P0-brief 怎么来

两种方案：

**方案 A：主 Agent 亲自写 subtask 的 P0-brief**
- 主 Agent 读 P1/P2 的 subtasks 声明 → 为每个 subtask 写 P0-brief（引用父 task 的产出）
- 优点：P0 不派 subagent，与现有机制一致
- 缺点：主 Agent 可能写肤浅的 P0-brief（T078 教训）

**方案 B：subtask 的 P0-brief 引用父 task 产出自动生成骨架**
- agate 提供 `agate-create-subtask.sh PARENT_TASK_DIR SUBTASK_ID`
- 脚本从父 task 的 P1-requirements.md 提取相关 BDD，从 P2-design.md 提取相关 packages/domains/gate_commands
- 生成 P0-brief 骨架（四字段 + 关联的 BDD 列表）
- 主 Agent 审阅修改后 commit

**选择方案 B**——自动化减少主 Agent 负担，且骨架从父 task 产出提取保证不肤浅。

### 决策 5：agate-create-subtask.sh 设计

```bash
#!/usr/bin/env bash
# agate-create-subtask.sh PARENT_TASK_DIR SUBTASK_NAME [SUBTASK_ID]
# 从父 task 的 P1/P2 产出提取相关内容，生成 subtask 的 P0-brief 骨架

PARENT_DIR="$1"
SUBTASK_NAME="$2"
SUBTASK_ID="${3:-}"  # 可选，不传则自动分配

# 1. 分配编号（active-tasks.md max+1）
# 2. 创建 docs/tasks/T00X-{name}/ 目录
# 3. 从 PARENT_DIR/P1-requirements.md 提取与 subtask 相关的 BDD
# 4. 从 PARENT_DIR/P2-design.md 提取 packages/domains/gate_commands
# 5. 生成 P0-brief.md 骨架：
#    task: "{subtask_name}"
#    known_risks: [引用父 task 的 risks]
#    executor_env: [从父 task 继承]
#    env_constraints: [从父 task 继承]
#    parent_task: T001  # 新字段：标记父 task
#    related_bdds: [BDD-3, BDD-5, BDD-7]  # 相关的 BDD 编号
# 6. 在 active-tasks.md 添加新行
# 7. echo "Created: docs/tasks/T00X-{name}/"
```

**BDD 提取**：subtasks 声明里可以指定 related_bdds，脚本只提取这些 BDD。如果没指定，提取全部（subtask 是父 task 的子集）。

### 决策 6：不增加 gate 层负担

- subtasks 声明是**可选**字段，不进 gate（P1/P2 gate 不检查 subtasks）
- agate-create-subtask.sh 是**辅助工具**，不是 gate 的一部分
- 主 Agent 可以不用脚本手动创建 subtask（脚本只是减少工作量）

## 四、改动清单

### 脚本
- **新增** `agate/scripts/agate-create-subtask.sh`——从父 task 产出生成 subtask P0-brief 骨架

### 文档
- **修改** `agate/state-machine.md`——追加"Task 派生"节，描述 subtasks 声明 + agate-create-subtask.sh
- **修改** `agate/WORKFLOW.md` L122——从"P1 拆成多个子任务"改为"P1 声明 subtasks + agate-create-subtask.sh 创建"
- **修改** `agate/orchestrator-template.md`——mapping 表后追加"发现 subtasks 声明时的处理流程"
- **修改** `agate/assets/templates/active-tasks-template.md`——维护规则追加"subtask 创建规则"

### 测试
- `agate/tests/unit/agate-create-subtask.bats`——脚本功能测试
- `agate/tests/integration/subtask-flow.bats`——端到端：父 task P1 声明 subtasks → 主 Agent 调 agate-create-subtask.sh → subtask 目录创建 + P0-brief 骨架生成

### P0-brief 模板扩展
- P0-brief.md 新增可选字段 `parent_task` 和 `related_bdds`
- P0 卡片说明：subtask 的 P0-brief 由 agate-create-subtask.sh 生成骨架，主 Agent 审阅修改

## 五、Self-Review

### 不增加 agent 负担

- subtasks 声明是可选的——P1 analyst 如果觉得不需要拆，不声明就行
- agate-create-subtask.sh 自动提取 BDD + 继承环境——主 Agent 不需要手动复制
- 主 Agent 仍需审阅 P0-brief 骨架——但比从零写轻得多

### 向后兼容

- subtasks 字段可选，不声明不影响现有流程
- parent_task/related_bdds 字段可选，不影响 P0 gate（四字段检查不变）
- active-tasks.md 依赖列已有，只是开始真正使用

### 风险

- **BDD 提取准确性**：如果 subtasks 声明没指定 related_bdds，脚本提取全部 BDD——可能导致 subtask 的 P0-brief 包含不相关的 BDD。但这只是骨架，主 Agent 审阅时删掉就行
- **编号冲突**：subtasks 声明里的 id 是预分配，实际编号由 active-tasks.md max+1 决定——如果两个 subtask 同时声明同一 id，后创建的会重新分配
- **依赖死锁**：如果 T002 depends_on T003 且 T003 depends_on T002——主 Agent 需要人工检测。但这不是 agate 的问题（主 Agent 不会创建循环依赖）

### 不做的

- 不做"依赖未完成则自动阻塞"的 gate 机制——主 Agent 判断力更合适
- 不做 subtask 自动派 P1 subagent——subtask 创建后主 Agent 按正常流程推进
- 不做 subtask 状态聚合到父 task——active-tasks.md 看板已经够用
