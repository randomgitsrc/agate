# 独立实施评审报告：orchestrator-template launcher 重构 + 3 gaps 修复

> 评审日期：2026-07-22
> 评审范围：PR #29-#35（orchestrator-template 从 manual 重构为 launcher，+ 3 gaps 修复）
> 评审人：独立 reviewer（非原作者）
> 基线：v0.16.0（PR #28 merged）→ PR #35 merged

---

## 一、修改目标回顾

### 1.1 原始目标（PR #34 commit message）

将 `orchestrator-template.md` 从 **manual（251 行流程手册）** 重构为 **launcher（~80 行身份+约束+导航）**：

- **移除**：gate 判定细节、commit 拦截表、重试协议、日志规范、PAUSED 协议、do→review 迭代等流程 cheat sheet
- **保留**：角色（4 件事）、约束（dispatch-context 铁律、4 文件只有你能写、你不是 gate）、导航（阶段卡片表）
- **核心原则**：模板只给身份和边界，流程知识由阶段卡片和 dispatch-protocol.md 按需提供

### 1.2 3 gaps 修复目标（PR #35 commit message）

- **G1**: `state-machine.md` 扩展 orchestrator-log.md 完整规范（5 种强制事件 + 生命周期规则）
- **G2**: `state-machine.md` 新增 commit 被拦 3 次 → PAUSED 规则
- **G3**: `task-files.md` 修正 orchestrator-log 引用路径（模板 → state-machine.md）

---

## 二、修改前后对比

### 2.1 orchestrator-template.md 结构变化

| 维度 | 修改前（manual，251 行） | 修改后（launcher，~80 行） |
|------|------------------------|---------------------------|
| **角色定义** | 详细列出 4 件事 + 不做第五件 + 派发不是传话 + 空返回处理 + PAUSED 语义 + do→review 迭代 | 精简为 4 行表格 + "你不是 gate" |
| **合法职责** | 列出 P6 归一化、Header 加 agent、P8 清理、N2 禁令等 4 条 | 改为文件清单表格（4 文件 + 何时写） |
| **关键检查** | 单步函数步骤 1/6 的 3 项检查 | 移除（已在 state-machine.md） |
| **Hardening 机制** | 完整的 pre-commit hook 检查类别表（格式/gate/审计/证据/CI 兜底/self-gate） | 移除（已在 WORKFLOW.md） |
| **关键不变量** | 6 条硬约束（你不是 gate / 不 --no-verify / dispatch-context 不写 PASS/FAIL / P6 不可裁剪 / P2 不可裁剪） | 精简为 4 条（dispatch-context 铁律 / PASS/FAIL 禁令 / 不 --no-verify / 不绕过工具失败） |
| **dispatch-context 铁律** | 存在，但分散在多处 | 集中到「你不能做的事」节，强化措辞 |
| **AGATE_CARD 注入** | 存在 | 存在，措辞从"禁止手写"扩大到"禁止任意方式操作" |
| **开始导航** | 存在（读阶段卡片） | 保留并强化「只读一张阶段卡片」 |
| **Fallback 文件列表** | 存在 | 保留 |
| **项目必读** | 存在 | 保留 |

### 2.2 修改范围统计

```
agate/orchestrator-template.md       | 218 +++++++++------------------------  (251→~80 行)
agate/state-machine.md               |  39 +++++--                    (orchestrator-log 扩展 + commit 被拦 3 次)
agate/assets/templates/task-files.md |   4 +--                        (引用路径修正)
agate/dispatch-protocol.md           | 171 +++++++++++++++++------------  (dispatch-context 铁律强化等)
```

**总变更**：4 个文件，+184/-236 行（净减 52 行，但信息密度提升）

---

## 三、逐项审查

### 3.1 设计原则一致性（A7）

#### 3.1.1 launcher 设计原则的合理性

**修改目标**：模板不再替 Agent 预学流程，Agent 按需读阶段卡片和 dispatch-protocol.md。

**评审结论**：✅ **合理且必要**

理由：
1. **认知负荷分离**：启动模板（launcher）只给"我是谁、我不能做什么、从哪里开始"——这是启动时必须知道的。流程细节（怎么做 gate、怎么重试、PAUSED 怎么处理）是执行时才需要的，不应在启动时预灌。
2. **渐进披露验证**：阶段卡片（phase-cards/P{N}-*.md）确实覆盖了被移除的内容——
   - "gate 判定细节" → P4/P5/P6/P7/P8 卡片各有 gate 规则节
   - "commit 拦截表" → state-machine.md 有 pre-commit 检查全景
   - "重试协议" → state-machine.md 有重试上限表 + 回退规则
   - "PAUSED 协议" → state-machine.md 有 PAUSED 恢复完整流程
   - "do→review 迭代" → dispatch-protocol.md 有迭代循环完整描述
3. **单点真理源**：同一知识不再在 template 和 protocol 文件里重复，避免 drift。

#### 3.1.2 移除内容的去向验证

| 被移除内容 | 去向 | 验证状态 |
|-----------|------|---------|
| 单步函数步骤 1/6（状态标记绑定、阶段跳变检测） | state-machine.md「单步执行」节 | ✅ 存在 |
| pre-commit 检查类别表 | WORKFLOW.md「Pre-commit 检查总览」 | ✅ 存在 |
| retry 上限表 | state-machine.md「重试上限」节 | ✅ 存在 |
| PAUSED 恢复协议 | state-machine.md「PAUSED 恢复」节 | ✅ 存在 |
| do→review 迭代循环 | dispatch-protocol.md「do→review 迭代循环」节 | ✅ 存在 |
| 空返回恢复策略 | dispatch-protocol.md「空返回的恢复策略」节 | ✅ 存在 |
| gate 诊断落盘 | dispatch-protocol.md「gate 诊断落盘」节 | ✅ 存在 |
| SCOPE+ 处理 | state-machine.md「特殊转移」节 | ✅ 存在 |
| 关键不变量（P6/P2 不可裁剪） | WORKFLOW.md「可裁剪的阶段」节 | ✅ 存在 |
| Agent 字段协作规范 | dispatch-protocol.md / task-files.md | ✅ 存在 |

**未发现知识丢失**。

### 3.2 文档→脚本对齐（A1）

#### 3.2.1 orchestrator-template.md 与下游文件的引用一致性

| 引用点 | 修改前 | 修改后 | 状态 |
|--------|--------|--------|------|
| `dispatch-protocol.md` | 多次引用（输入导航、空返回、派发模板） | Fallback 列表引用 | ✅ 一致 |
| `state-machine.md` | 多次引用（retry、PAUSED、单步函数） | Fallback 列表引用 | ✅ 一致 |
| `phase-cards/` | 阶段卡片表 | 阶段卡片表（强化） | ✅ 一致 |
| `WORKFLOW.md` | 引用（pre-commit 检查） | Fallback 列表引用 | ✅ 一致 |
| `task-files.md` | 引用（orchestrator-log） | 移除直接引用 | ✅ 一致（G3 修复） |

#### 3.2.2 G1/G2/G3 修复验证

**G1: orchestrator-log.md 完整规范**

修改内容（state-machine.md）：
```markdown
**`orchestrator-log.md` 防无响应**：

文件：`docs/tasks/{Txxx}/orchestrator-log.md`，主 Agent 专用...

规则：
- 仅追加不编辑不整理
- 不写思考过程、不写文件内容摘要、不写 subagent 返回原文——只写决策和下一步
- 任务从 DONE 重新激活 → 清空后重建；active/PAUSED 恢复 → 追加

必须记录的事件：
- 派发 subagent 前：`NEXT: ...`
- gate 失败后：`GATE FAIL: ...`
- gate 诊断完成：`DIAGNOSIS: ...`
- subagent 失败/空返回：`SUBAGENT FAIL: ...`
- 流程决策：`DECISION: ...`
```

**评审**：✅ 完整覆盖了被移除的"主 Agent 分阶段落盘"内容，且增加了生命周期规则（清空/追加）。

**G2: commit 被拦 3 次 → PAUSED**

修改内容（state-machine.md）：
```markdown
**commit 被 hook 拦截**：同一阶段累计被拦 3 次 → PAUSED（不要无限重试，Agent 明显走进了错误路径）。
```

**评审**：✅ 填补了 launcher 移除"commit 拦截表"后的信息缺口。但注意：此规则在 hook 脚本中是否有对应实现？

→ **待验证**：`check-state-transition.sh` 或 `check-gate.sh` 是否实际追踪"同一阶段被拦次数"？还是仅作为指导原则？

**G3: task-files.md 引用路径修正**

修改内容：
```diff
- orchestrator-log.md | 主 Agent | ...详见 orchestrator-template.md「主 Agent 分阶段落盘」节
+ orchestrator-log.md | 主 Agent | ...详见 state-machine.md「orchestrator-log.md 防无响应」节
```

**评审**：✅ 精确修正。旧引用指向已移除的 template 章节，新引用指向 state-machine.md 的规范位置。

### 3.3 一致性连锁 + 反向传播（A3）

#### 3.3.1 跨文件引用一致性

| 文件 | 修改前引用 template 的章节 | 修改后状态 |
|------|------------------------|-----------|
| task-files.md | "详见 orchestrator-template.md「主 Agent 分阶段落盘」节" | 改为 "state-machine.md「orchestrator-log.md 防无响应」" ✅ |
| dispatch-protocol.md | 无直接引用 template 具体章节 | N/A |
| state-machine.md | 无直接引用 template 具体章节 | N/A |
| WORKFLOW.md | 无直接引用 template 具体章节 | N/A |

**未发现其他悬空引用**。

#### 3.3.2 术语一致性

| 术语 | 修改前 | 修改后 | 状态 |
|------|--------|--------|------|
| "dispatch-context 铁律" | 存在，分散 | 集中到「你不能做的事」节 | ✅ 一致 |
| "你不是 gate" | 在"关键不变量"节 | 提升到角色定义后独立段落 | ✅ 强化 |
| "只有你能写" | "可以写" | "只有你能写"（PR #33） | ✅ 措辞强化 |
| "AGATE_CARD 注入" | "禁止手写" | "禁止任意方式操作"（PR #31） | ✅ 范围扩大 |

### 3.4 测试覆盖（A4）

#### 3.4.1 现有测试验证

```bash
$ bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
# 317 bats tests, 0 failures
```

**评审**：✅ 全部通过。

#### 3.4.2 测试覆盖缺口

launcher 重构是**文档结构重构**，不涉及脚本逻辑变更，因此：

- **无需新增 bats 测试**（无脚本变更）
- **但需验证**：阶段卡片是否完整覆盖被移除内容 → 已在 3.1.2 验证，全部覆盖 ✅

**G1/G2/G3 修复**：
- G1（orchestrator-log 规范）：state-machine.md 是纯文档，无脚本变更 → 无需测试
- G2（commit 被拦 3 次）：**待确认**——这是指导原则还是硬规则？如果是硬规则，需要 hook 脚本实现 + 测试
- G3（引用路径修正）：纯文档修正 → 无需测试

**⚠️ 发现潜在缺口**：G2 "同一阶段累计被拦 3 次 → PAUSED" 在 hook 脚本中是否有实现？

检查：
```bash
$ grep -r "3 次\|三次\|被拦" agate/scripts/
# 无匹配

$ grep -r "PAUSED\|paused" agate/scripts/check-state-transition.sh
# 有 PAUSED 检测逻辑，但无"3 次"计数
```

**结论**：G2 当前是**指导原则**（写在 state-machine.md 里给主 Agent 看），不是 hook 脚本的硬拦截。这是合理的——hook 只能检测单次 commit，无法追踪"同一阶段累计被拦次数"（这需要跨 commit 的状态持久化）。

但这也意味着：**主 Agent 需要自觉遵守此规则**，无外部强制。

### 3.5 下游影响 + 文档传播（A5）

#### 3.5.1 下游项目影响

| 下游项目 | 影响 | 状态 |
|---------|------|------|
| peekview | orchestrator.md 已同步（PR #29-#33） | ✅ 已同步 |
| 其他使用 agate 的项目 | 需要重新拷贝 orchestrator-template.md | ⚠️ 需手动更新 |

#### 3.5.2 版本兼容性

- 修改是**结构性的**（manual → launcher），但**无破坏性变更**（不修改 gate 规则、不修改脚本行为）
- 版本 bump：无需（已在 v0.16.0 中）

### 3.6 锚点表覆盖（A6）

`check-protocol-consistency.py` 的 `SCRIPT_ALIGNMENT_ANCHORS` 无需更新——orchestrator-template.md 重构未新增/删除锚点。

### 3.7 已知局限评估

#### 3.7.1 局限 5（协议文档内部一致性）

launcher 重构**缓解**了此局限：
- 修改前：orchestrator-template.md 和 state-machine.md / dispatch-protocol.md 有大量重复内容
- 修改后：知识单点存放，降低 drift 风险

#### 3.7.2 局限 3（主 Agent 判断力是单点故障）

launcher 重构**对此局限无影响**——主 Agent 仍是最终裁判，launcher 只是改变了信息呈现方式。

但 G2（commit 被拦 3 次 → PAUSED）是**缓解措施**：当主 Agent 反复犯错时强制停下来，避免无限循环。

---

## 四、发现与修复

### 4.1 悬空节名引用（已修复）

**发现**：global grep `orchestrator-template.md` → 13 处引用。其中 2 处引用了旧的节名：

| 文件 | 行号 | 旧引用 | 修复 |
|------|------|--------|------|
| state-machine.md | 515 | `「Fallback：完整协议文件列表」节` | → `「Fallback（按需查阅，不要求每轮必读）」节` |
| loop-orchestration.md | 238 | `「Fallback：完整协议文件列表」节` | → `「Fallback（按需查阅，不要求每轮必读）」节` |

其余 11 处引用均为概念性引用（"orchestrator-template.md 的 mapping 表"、"从 orchestrator-template.md 进入"等），不指向特定节名，无漂移。

### 4.2 G2 hook 硬拦截（确认无实现）

- `grep -r "被拦\|拦截次数\|hook.*fail\|cumulative\|累计" agate/scripts/` → 无匹配
- 结论：G2 是指导原则（依赖主 Agent 自觉遵守），无 hook 脚本实现
- 原因：hook 无跨 commit 持久化状态，无法追踪"同一阶段累计被拦次数"
- 判定：**接受现状**。作为指导原则是合理的，future work 考虑 `.state.yaml` 增加 `commit_hook_failures` 字段

## 五、最终判定

**Overall verdict: ALIGNED（2 个悬空节名引用已修复）**

| 审查项 | 结论 |
|--------|------|
| A7 设计原则 | ✅ launcher 设计合理，知识去向验证完整 |
| A1 文档对齐 | ✅ 2 个悬空节名引用已修复，其余一致 |
| A3 一致性连锁 | ✅ G1/G2/G3 修复正确 |
| A4 测试覆盖 | ✅ 317 bats 全绿 |
| A5 下游影响 | ✅ peekview 已同步 |
| A6 锚点覆盖 | ✅ 无需更新 |
| G2 硬拦截 | ⚠️ 指导原则，无 hook 实现（可接受） |

## 六、附录：修改前后完整 diff

（见 git diff 8648b06~1 8648b06 -- agate/orchestrator-template.md）
