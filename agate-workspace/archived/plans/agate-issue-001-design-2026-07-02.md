---
task_id: agate-issue-001
agent: main
date: 2026-07-02
status: 设计文档（v2，自行评审修订已纳入）
来源: docs/issues/001-peekview-commit-hook-inactive.md + 用户讨论
---

# Issue #001 设计：多任务 hook 适配 + phase-产出一致性检查

## 问题全貌

### Bug 1：hook 写死根 .state.yaml，多任务架构下完全失效

- `pre-commit-gate.sh:29` 写死 `STATE_FILE="$REPO_ROOT/.state.yaml"`
- 协议文档 `state-machine.md:449` 规定 `.state.yaml` 位置是 `docs/tasks/{Txxx}/.state.yaml`
- PeekView 等项目用多任务架构，根目录无 `.state.yaml`
- 结果：hook 读不到 phase → `exit 0` 静默放行

### Bug 2：phase 和产出文件不一致时 hook 无感知

agent 可能：
- 产出了 P4-implementation.md 但忘了改 phase（仍标 P3）→ hook 跑 P3 gate，放过 P4 产出
- 改了 phase P3→P4 但没产出 P4-implementation.md → hook 放行，下次 agent 接手发现 P4 产出不存在

state-machine.md:523-532 有"状态标记绑定检查"规则，但只靠主 Agent 下次启动时自检——错误的 commit 已经进了历史。

## 设计原则

**该拦的拦，不该拦的放行，宁可 WARNING 不 exit 1。**

hook 是 pre-commit 门槛，不是完整验证器。hook 的职责是拦住**明确违规**，对**模糊场景**只 WARNING。理由：
- 拦截太严 → agent 每个 commit 都被挡 → 绕过 hook（`--no-verify`）→ 比不装 hook 更糟
- WARNING 留痕 → 下次 agent 接手时能看到 → 由主 Agent 的绑定检查兜底

## 设计

### 改动 1：多任务 .state.yaml 扫描

把单 `STATE_FILE` 逻辑改为扫描暂存区中所有变更的任务级 `.state.yaml`。

```
当前逻辑：
  STATE_FILE="$REPO_ROOT/.state.yaml"  # 写死根
  检查这一个文件

改为：
  1. 扫描暂存区，找所有变更的 .state.yaml 文件
     git diff --cached --name-only | grep -E '\.state\.yaml$'
     包括根 .state.yaml（向后兼容）和 docs/tasks/{Txxx}/.state.yaml（多任务）
  2. 对每个变更的 .state.yaml：
     a. 跑 check-state-yaml.sh 格式校验
     b. 检测 phase 是否变更（git diff --cached -- 文件 | grep '+.*phase:'）
     c. 如果 phase 变了 → 跑 check-state-transition.sh
     d. 从 .state.yaml 路径反推 TASK_DIR（dirname）
     e. 读 phase → 如果 phase 是 P0-P8（非 PAUSED/READY/DONE）→ 跑 check-gate.sh
     f. gate 结果按任务路径写 .gate-result.json（不是根目录）
  3. PROD_TOUCHED 检测保持全局（扫暂存 diff 内容，不按任务分）
```

### 改动 2：phase-产出一致性检查（WARNING，不拦截）

在 gate 运行前，检查暂存的产出文件和 phase 是否匹配。

**检查逻辑**：

```
从暂存区提取所有 P{n}-*.md 文件，按任务分组：
  docs/tasks/T001/P4-implementation.md → 任务 T001，产出阶段 P4

对该任务的 .state.yaml：
  读 phase 值

判定（只对"暂存了 P{n}-*.md 产出"的情况检查）：
  情况 A：暂存 P4 产出 + phase=P4 → 正常，放行
  情况 B：暂存 P4 产出 + phase=P3（忘改） → WARNING
  情况 C：暂存 P4 产出 + phase=P5（跳了） → WARNING
  情况 D：无 P{n}-*.md 产出 → 不检查（可能是纯代码 commit / 裁剪跳阶 / PAUSED 恢复 / 状态转移等）
```

**为什么不检查 D（无产出）**：
- 裁剪跳阶 P2→P5 无 P3/P4 产出是合法的，hook 不读 P1 phases 声明无法区分裁剪和跳阶
- PAUSED→P4 恢复也无新产出
- 纯代码 fix commit 无 P{n}-*.md
- 这些都是合法场景，WARNING 会噪音太大

**为什么不拦截 B/C**：
- agent 可能先 commit 产出再改 phase（合法中间状态）
- 拦截太严 → agent 用 `--no-verify` 绕过 → 比不装 hook 更糟
- WARNING 留痕 → 下次 agent 接手时由 state-machine.md:523 绑定检查兜底

**什么情况下拦截**：

hook 只在以下情况 exit 1：
- `check-state-yaml.sh` 格式校验失败（已有）
- `check-state-transition.sh` 状态转移非法（已有）
- `check-gate.sh` gate 未通过（已有）
- `[PROD_TOUCHED]` 标记（已有）

phase-产出不一致**只 WARNING 不拦截**。

### 改动 3：has_staged_phase_output 适配多任务

当前 `has_staged_phase_output` 只检查是否有 `P[0-9]+-.*\.(md|yaml)$` 变更，不关心属于哪个任务。

改为：返回变更的产出文件列表（含任务路径），供改动 2 做一致性检查。

### 不做的事

- **不做 active-tasks.md 校验**：active-tasks.md 是人维护的 markdown 看板，格式不稳定，不适合 hook 解析。state-machine.md:580 明确"以 .state.yaml 为准"。
- **不做 phase-产出强制绑定**：太严格会导致裁剪跳阶、先产出后改 phase 等合法场景被误拦。
- **不改 check-state-transition.sh**：它已接受 .state.yaml 路径参数，只需传对的路径。
- **不改 check-gate.sh**：它已接受 TASK_DIR 参数，只需传对的路径。

## 变更文件清单

| 文件 | 改动 |
|------|------|
| `agate/scripts/pre-commit-gate.sh` | 多任务扫描 + phase-产出 WARNING |
| `agate/scripts/gate-result.sh` | `has_staged_phase_output` 返回文件列表（或新增函数） |
| `agate/tests/integration/pre-commit-hook.bats` | 新增多任务场景测试 |
| `agate/state-machine.md` | 补充"hook 扫描任务级 .state.yaml"的说明 |
| `CHANGELOG.md` | 标注行为变更 |

## 测试计划

### 新增集成测试

| ID | 描述 | 期望 |
|----|------|------|
| IT.6 | 多任务：T01/P1.md + T01/.state.yaml(phase=P1) | exit 0（正常） |
| IT.7 | 多任务：T01/P4.md + T01/.state.yaml(phase=P3，忘改) | exit 0 + WARNING |
| IT.8 | 多任务：phase P3→P4 变更 + 无 P4 产出 | exit 0（无 WARNING，合法中间状态） |
| IT.9 | 多任务：裁剪跳阶 P2→P5 + 无 P3/P4 产出 | exit 0（无 WARNING） |
| IT.10 | 向后兼容：根 .state.yaml 仍工作 | exit 0 |

### 现有测试不回归

IT.1-IT.5 全部保持通过（向后兼容根 .state.yaml）。
