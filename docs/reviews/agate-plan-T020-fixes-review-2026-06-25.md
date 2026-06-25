---
type: review
source: docs/plans/T020-postmortem-fixes.md
trace_id: agate-plan-T020-fixes-review-2026-06-25
created: 2026-06-25
status: draft
---

# 评审：T020 复盘落地实施计划

> 评审者：独立评审
> 评审对象：`docs/plans/T020-postmortem-fixes.md`
> 依据：复盘 `docs/reviews/agate-postmortem-T020-p6-recovery-2026-06-25.md` §7.4、协议原文 grep 实证、T019 plan 格式对比

## 总体评价

plan 方向正确、落地清单与 review §7.4 一致、文件映射准确。但作为可执行计划有 5 个缺陷，其中 1 个事实错误（漏改）、2 个缺失（执行时卡住）、2 个格式退步（可执行性下降）。

---

## 逐项评估

### ✅ 做对的

1. **落地清单与 review §7.4 对齐**：6 项落地 + 2 项不落地，与经三轮迭代后确定的清单一致，没有自作主张增减
2. **文件映射精确**：dispatch-protocol.md（5 项）/ state-machine.md（1 项）/ LIMITATIONS.md（1 项），每项改动对应到具体文件
3. **问题 5 界限判定标准明确**："改常量=最小修复，改控制流=重写"——这是 review §跨复盘模式里专家评审补的，plan 准确继承了
4. **不落地项有理由**：问题 3（等数据）、问题 8（方案无效），不是简单删除

### ❌ 问题 1：事实错误——问题 6 说"两处"实际三处

plan 问题 6 说：
> state-machine.md 两处用 `grep -qF '[BLOCKER]'`

实证 grep 结果：

| 文件 | 行号 | 内容 |
|------|------|------|
| state-machine.md | 120 | `P7 --[! grep -qF '[BLOCKER]' P7-consistency.md]--> P8`（转移规则）|
| state-machine.md | 294 | `- P7: ! grep -qF '[BLOCKER]' P7-consistency.md`（单步函数）|
| dispatch-protocol.md | 402 | `\| P7→P8 \| 一致性通过 \| ! grep -qF '[BLOCKER]' P7-consistency.md ... \|`（gate 表）|

**共 3 处，plan 漏了 dispatch-protocol.md:402**。如果只改 state-machine.md 两处，gate 表里的 grep 命令仍是旧版，主 Agent 跑 P7 gate 时仍会 false positive。

**修正**：plan 问题 6 改为"三处"，补充行号：

```
state-machine.md:120（转移规则）
state-machine.md:294（单步函数）
dispatch-protocol.md:402（gate 表 P7 行）
```

### ❌ 问题 2：缺「已落地清单」，执行时找不到修改位置

T019 plan 开头有「已落地清单」表，列出 7 项前序已 commit 的修复及精确位置（如"降级禁止 554c5aa（dispatch-protocol.md:125-138）"）。这让执行者知道：本次修改是在哪些已存在的节上追加，不是新建。

T020 plan 缺这个表。问题在于本次 6 项落地中，有 4 项是修改**已存在的节**：

| 本次落地项 | 修改的节 | 该节来源 |
|-----------|---------|---------|
| 问题 2 | dispatch-protocol.md「空返回的恢复策略」节 | T016 落地（554c5aa）|
| 问题 4 | dispatch-protocol.md「输入导航原则」节后 | T016 落地（554c5aa）|
| 问题 5 | dispatch-protocol.md「长时操作 subagent 派发策略」节 | T019 落地（fda391c）|
| 问题 1 | dispatch-protocol.md:453 硬超时保护节 | T019 落地（fda391c）|

没有这个表，执行者要自己 grep 确认节是否存在、是追加还是新建。T019 plan 已有此格式，T020 plan 应继承。

**修正**：开头加：

```
## 已落地清单（本次在其基础上修改）

| 节/规则 | 来源 | commit |
|---------|------|--------|
| 降级硬边界 | T016 | 554c5aa |
| 空返回的恢复策略 | T016 | 554c5aa |
| 输入导航原则 | T016 | 554c5aa |
| 长时操作 subagent 派发策略 | T019 | fda391c |
| 硬超时保护 | T019 | fda391c |
| P2 最小验证 | T019 | fda391c |
```

### ❌ 问题 3：LIMITATIONS.md 局限 4 没给内容草稿

plan 问题 2 说"LIMITATIONS.md 新增局限 4：subagent 活动不可观测"，但没给具体文字。review §7.5 里有完整的已知限制文本（约 15 行），plan 应直接引用。

执行者如果没有草稿，要自己组织语言，可能偏离 review 的措辞（特别是"间接缓解"和"根本解决"的区分）。

**修正**：plan 问题 2 项下补充局限 4 的内容草稿，直接从 review §7.5 复制。LIMITATIONS.md 现有 3 条局限，每条格式是"标题 + 正文段落"，局限 4 应保持同样格式。

### ⚠️ 问题 4：缺「验证整改有效」检查点

T020 review §5.2 item 2 自评说"整改建议缺'如何验证整改有效'"。plan 同样缺这个——6 项落地后怎么知道改对了？

这是 T020 review 才提出的缺口，T019 plan 也没有（是新增实践）。T020 plan 作为提出者应率先补上。

**修正**：末尾加「验证检查点」节，每项给验证方式。大部分是"下次任务时观察是否遵守"（非即时验证），但至少给了检查标准。

### ⚠️ 问题 5：格式退步——缺"为什么"段

T019 plan 每个修复项是三段式：**问题 → 为什么 → 修法**。"为什么"段解释了修复的必要性（如"为什么是结构性修复：不靠主 Agent 主动遵守"）。

T020 plan 是两段式：**现状 → 动作**。缺"为什么"。这降低了 plan 的可读性——执行者知道"改什么"但不知道"为什么这么改"，遇到细节决策时缺乏判断依据。

例：问题 4（客观信息落盘）没解释"为什么这是铁律 2 的补全而不是优化"——而这个判断是 review §跨复盘模式的核心论点。执行者如果不理解这个定位，可能把它当成可选优化而不严格执行。

**修正**：每项补"为什么"段，从 review 对应章节提取一句核心判断。

---

## 修正后的落地清单（建议版）

| 优先级 | 问题 | 动作 | 改动位置 | 类型 |
|--------|------|------|---------|------|
| 🔴 | 问题 1 | 删"默认 10 分钟"错误描述 | dispatch-protocol.md:453 | bug fix |
| 🔴 | 问题 6 | 改 `grep -E` 行首匹配 | state-machine.md:120,294 **+ dispatch-protocol.md:402**（共 3 处）| bug fix |
| 🟠 | 问题 2 | 撤回耗时三档；改间接缓解三条 | dispatch-protocol.md「空返回的恢复策略」节（T016 554c5aa 建）| 能力补充→已知限制 |
| 🟠 | 问题 2 | 新增局限 4 | LIMITATIONS.md（现有 3 条后追加）| 已知限制记录 |
| 🟠 | 问题 4 | 加「客观信息落盘」子节 | dispatch-protocol.md「输入导航原则」节后（T016 554c5aa 建）| 能力补充 |
| 🟠 | 问题 5 | 加「写脚本与跑脚本分离」子节 | dispatch-protocol.md「长时操作 subagent 派发策略」节（T019 fda391c 建）| 能力补充 |
| 🟡 | 问题 7 | P6 gate 补截图质量标准 | dispatch-protocol.md gate 表 P6 行（line 401）| gate 完善 |

---

## 总结

plan 的方向、清单、文件映射都对，可以作为执行依据。5 个缺陷中：

- 问题 1（漏改第三处 grep）是**事实错误，必须修**——否则 P7 gate 仍有 false positive
- 问题 2（缺已落地清单）和问题 3（缺局限 4 草稿）是**执行时会卡住的缺失，必须补**
- 问题 4（验证检查点）和问题 5（格式退步）是**应该补的**——提高可执行性和可追踪性

建议修正这 5 点后再执行。
