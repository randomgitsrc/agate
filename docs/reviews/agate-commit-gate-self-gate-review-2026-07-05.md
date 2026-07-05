---
review_date: 2026-07-05
reviewer: protocol-alignment-review
change_summary: commit gate + 拦截处理策略 — check-state-transition.sh 新增检查 3，逐阶段 commit 强制
files_changed:
  - agate/scripts/check-state-transition.sh (+55 行，新增检查 3)
  - agate/tests/unit/check-state-transition.bats (ST.16-ST.20 五新测试 + ST.3/ST.11 修复)
  - agate/orchestrator-template.md (commit 时机强制 + 拦截类型表重写)
  - agate/git-integration.md (标记强制执行)
---

# 协议-脚本对齐审查

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | NEEDS_HUMAN_REVIEW (4 项遗漏，均非阻塞) |
| A4 | 测试覆盖 | ALIGNED |
| A5 | 下游影响 + 文档传播 | NEEDS_HUMAN_REVIEW (CHANGELOG 为空) |
| A6 | 锚点表覆盖 | ALIGNED |

**总体**: PASS — 核心实现 (A1/A2/A4/A6) 全部对齐。A3/A5 各有文档遗漏项，均不影响脚本行为正确性，可提交后补。

## 逐项审查

### A1: 文档→脚本对齐

**意图**：在 `.state.yaml` phase 从 Pn 推进到 Pn+1 时，强制 Pn 的产出文件必须先 commit，防止"产出未持久化就标记下一阶段"导致崩溃丢进度。

**文档声明 1 (git-integration.md:31)**：
> **粒度：每个阶段门槛通过后，主 Agent commit 一次。** 一个 Pn 阶段的产出是一个原子的进度单位。**这个规则由 `check-state-transition.sh` 强制执行**——推进 phase 到 Pn+1 前，Pn 产出必须已 commit，否则拦截。

**脚本实现 (check-state-transition.sh:106-155)**：
```bash
# 检查 3：pre-phase-change commit gate（逐阶段 commit 强制）
# 从 P{n} 推进到 P{n+1} 时，P{n} 产出必须已 commit
# 仅适用于任务级 .state.yaml（docs/tasks/Txxx/.state.yaml），根 .state.yaml 跳过
if [ "$old_num" -gt 0 ] && [ "$new_num" -gt 0 ] && [ "$new_num" -gt "$old_num" ] \
   && [ "$old_phase" != "PAUSED" ]; then
    ...
    # 产出在暂存区但未 commit → 拦截
    if git diff --cached --name-only | grep -q "^${TASK_REL}/${OLD_OUTPUT}"; then
        echo "GATE STATE: 在推进到 ${new_phase} 前，${old_phase} 产出必须已 commit" >&2
        exit 1
    fi
    # 产出从未被 commit
    if [ -z "$(git ls-files "$TASK_REL/$OLD_OUTPUT")" ]; then
        echo "GATE STATE: ${old_phase} 产出 ${OLD_OUTPUT} 尚未 commit" >&2
        exit 1
    fi
    ...
fi
```

**文档声明 2 (orchestrator-template.md:163-165)**：
> ### commit 时机（强制执行）
> **每阶段完成必须 commit**（`git-integration.md`）。一个 Pn 阶段的产出是一个原子的进度单位。推进 `.state.yaml` phase 到 Pn+1 前，Pn 产出必须已 commit——`check-state-transition.sh` 会拦截"产出未 commit 就推进 phase"的行为。

**结论**：ALIGNED。文档声明和脚本实现语义一致：强制 commit → 拦截推进。

**文档声明 3 (orchestrator-template.md:184-191 拦截类型表)**：
> | 拦截类型 | 处理 |
> |----------|------|
> | 未 commit 旧阶段就推进 phase | 先 commit 旧阶段产出，再改 phase |

与脚本 exit 1 行为一致，message 给出"先 git commit ... 产出再改 phase"提示。

---

### A2: 脚本→文档对齐

**脚本新增行为**：

1. **仅任务级 .state.yaml 生效** (`check-state-transition.sh:113`):
   ```bash
   if echo "$STATE_FILE" | grep -qE 'docs/tasks/[^/]+/'; then
   ```

2. **前向推进才触发** (`check-state-transition.sh:109`):
   ```bash
   [ "$new_num" -gt "$old_num" ]
   ```

3. **PAUSED 恢复跳过** (`check-state-transition.sh:110`):
   ```bash
   [ "$old_phase" != "PAUSED" ]
   ```

4. **P4/P5 特殊处理** (`check-state-transition.sh:123-124`):
   ```bash
   P4) ;;  # scope out — 代码在项目任意路径，无法 task-scoped 关联
   P5) ;;  # 用文件存在性检查，不走路径
   ```

5. **P5 目录级检查** (`check-state-transition.sh:150-153`):
   ```bash
   if [ "$old_phase" = "P5" ] && [ ! -d "$TASK_DIR/P5-test-results" ]; then
       echo "GATE STATE: ${old_phase} 产出 P5-test-results/ 目录不存在" >&2
       exit 1
   fi
   ```

**对应文档覆盖**：

- 行为 1,2,3: `git-integration.md:31` 无细粒度说明，但 `orchestrator-template.md:163-165` 覆盖了"强制执行"语义
- 行为 4 (P4/P5 scope out): 脚本内注释已充分 → 无需文档覆盖（实现细节）
- 行为 5 (P5 目录检查): 脚本内注释 → 同上

**结论**：ALIGNED。脚本新增行为有文档对应（核心语义在 git-integration.md 和 orchestrator-template.md），实现细节（P4/P5 scope out、P5 目录检查）属于脚本内部设计。

---

### A3: 一致性连锁 + 反向传播

#### A3a 一致性连锁

变更涉及 4 个文件，相互一致：
- `git-integration.md` → 声明强制执行规则
- `check-state-transition.sh` → 实现强制执行
- `orchestrator-template.md` → 引用强制执行 + 拦截处理表
- `check-state-transition.bats` → 测试覆盖

**结论**：ALIGNED。

#### A3b 反向传播

以下文件**应被影响但未在 diff 中**：

**1. `agate/rules/state-transitions.md` — 遗漏 (LOW)**

反向传播路径：改了 `check-state-transition.sh` (脚本行为) → `agate/rules/state-transitions.md`（提取跨阶段共用的转移/重试/恢复规则）
- 当前 `rules/state-transitions.md` 包含"转移条件""回退规则""中断恢复步骤"各节
- 但**无**提到"推进 phase 前 Pn 产出必须先 commit"这个执行约束
- 这是一个 state-transition 层面的规则，应在该文件中引用

**建议**：在 `rules/state-transitions.md` "中断恢复步骤" 或新增 "commit 约束" 小节中加一句：`推进 phase 到 Pn+1 前，Pn 产出必须已 commit（check-state-transition.sh 强制执行）`

**2. 阶段卡片 — 遗漏 (LOW)**

反向传播路径：改了 `check-state-transition.sh` (脚本行为) → 阶段卡片 (主 Agent 直接读的指导文件)
- 当前 P4/P5/P6/P7/P8 卡片均含 "git commit" 步骤
- 但**无**任何卡片提到"不先 commit 旧阶段产出就推进 phase 会被 hook 拦截"
- P4-implementation.md:11 "git add 代码文件 → git commit → 更新 phase=P5" → 正确顺序，但没说如果跳过 commit 直接改 phase 会怎样

**建议**：在 P4/P5/P6/P7/P8 卡片的"常见错误"节各加一条：`commit 旧阶段产出前就推进 phase → hook 拦截（check-state-transition.sh 检查 3）`

**3. `agate/scripts/README.md` L17 — 遗漏 (LOW)**

反向传播路径：改了 `check-state-transition.sh` (脚本行为) → `agate/scripts/README.md`
- 当前 L17: `| check-state-transition.sh (P2.3-P2.5) | 状态转移合法性 + 重试上限 |`
- 未提及新增的 commit gate 功能

**建议**：更新为 `(P2.3-P2.5 + commit gate)`，用途改为"状态转移合法性 + 重试上限 + 逐阶段 commit 强制"

**4. `agate/WORKFLOW.md` Pre-commit 检查总览 — 遗漏 (LOW)**

反向传播路径：改了 `check-state-transition.sh` → `WORKFLOW.md` Pre-commit 检查总览
- 当前表 L222: `| 2.3 | check-state-transition.sh | gate 通过后 | 阶段级 | 状态转移合法性 + 重试上限（P2.3-P2.5）|`
- 未提及 commit gate

**建议**：更新描述为"状态转移合法性 + 重试上限 + commit gate（P2.3-P2.5 + commit gate）"

**不需要变更的文件（已验证）**：
- `state-machine.md`: L493 已有 commit 时机描述，L166 引用 pre-commit 检查。变更在 git-integration.md 锚定即可
- `dispatch-protocol.md`: 无直接相关性，步骤 6 "更新状态" 不变
- `role-system.md`, `LIMITATIONS.md`: 无相关性

---

### A4: 测试覆盖

**变更前**：15 测试 (ST.1-ST.15)
**变更后**：20 测试 (ST.1-ST.20)

**新增测试**：
| 测试 | 场景 | 覆盖边界 |
|------|------|---------|
| ST.16 | P1→P2 推进，P1 产出已 commit | Happy path |
| ST.17 | P1 产出在暂存区未 commit + phase 改 P2 | 拦截：暂存未 commit |
| ST.18 | P1 产出从未 commit + phase 改 P2 | 拦截：从未 commit |
| ST.19 | PAUSED→P3 恢复 | 跳过 commit gate |
| ST.20 | P3→P1 回退 | 回退不触发 commit gate |

**边界覆盖**：正向推进 / 暂存未 commit / 从未 commit / PAUSED 恢复 / 回退方向 → 5/5 ✅

**修复测试**：
- ST.3: 从根 `.state.yaml` 迁移到 `docs/tasks/T001/.state.yaml` + 加入 P1 产出（commit gate 要求）
- ST.11: 加入 P2 产出（commit gate 要求）

**全量回归**：226/226 全绿 ✅

**结论**：ALIGNED。

---

### A5: 下游影响 + 文档传播

**破坏性变更**：无。根 `.state.yaml` 不触发 commit gate（`check-state-transition.sh:113` 的 `grep -qE 'docs/tasks/[^/]+/'` 守卫）。向下兼容。

**现有项目影响**：仅 task-level `.state.yaml` (多任务架构)触发。已有 behavior 不受影响，commit gate 是新增约束不是修改变约束。

**CHANGELOG 标注**：❌ `[Unreleased]` 节为空（L33-35）。本次变更（commit gate + 拦截处理策略）应记录。

建议添加：
```markdown
## [Unreleased]

### 新增
- **commit gate（逐阶段 commit 强制）**：check-state-transition.sh 新增检查 3，推进 phase 前 Pn 产出必须先 commit。适用于任务级 .state.yaml（docs/tasks/Txxx/），根 .state.yaml 不受影响。PAUSED 恢复和回退不触发。
- **拦截处理策略表**：orchestrator-template.md 新增按拦截类型的处理流程 + 3 次累计限流 → PAUSED

### 变更
- check-state-transition.sh 增加 P5 产出目录存在性检查
- git-integration.md 规则 2 标注 check-state-transition.sh 强制执行
```

[HUMAN_CONFIRMED: 2026-07-05 确认：CHANGELOG 遗漏是文档整洁度问题，不影响代码正确性。提交后补即可。]

---

### A6: 锚点表覆盖

**CHECK 9** 扫描协议文档声明的规则 vs 脚本关键词。本次变更：
- `check-state-transition.sh` 已在锚点表中（现有条目覆盖 P2.3-P2.5 状态转移 + 重试上限）
- 新增检查 3 是同一脚本的附加功能，关键词（`commit`/`产出`/`暂存`/`git ls-files`）不一定在锚点表中

**验证**：`check-protocol-consistency.py` CHECK 9 → PASS ✅（无新增 ERROR）

**结论**：ALIGNED。CHECK 9 是关键词存在性检查（非语义检查），其局限已在 SELF-GATE.md:40-44 声明。新增检查 3 不影响现有 CHECK 9 结果。

---

## 实跑验证

| 验证项 | 命令 | 结果 |
|--------|------|------|
| 全量 bats | `bats agate/tests/` | 226/226 全绿 ✅ |
| 协议一致性 | `check-protocol-consistency.py` | 0 ERROR, 1 WARNING (预存) ✅ |
| shellcheck | `shellcheck check-state-transition.sh` | 0 错误 ✅ |
| Live: happy path | P1→P2, P1 committed | exit 0 ✅ |
| Live: 暂存未 commit | P1 产出 + phase change 同暂存区 | exit 1, "产出必须已 commit" ✅ |
| Live: 从未 commit | P1 产出未创建 | exit 1, "尚未 commit" ✅ |
| Live: 根 .state.yaml | 非 task-level 路径 | exit 0, 跳过 commit gate ✅ |

---

## 结论

核心实现（A1/A2/A4/A6）全部 ALIGNED。A3 有 4 项文档遗漏（rules/state-transitions.md、阶段卡片 ×5、scripts/README.md、WORKFLOW.md Pre-commit 表），均为次要文档更新，不影响脚本行为正确性或现有项目运行。A5 的 CHANGELOG 遗漏是整洁度问题。总体判定 **PASS** — 可提交，遗漏项可后补。
