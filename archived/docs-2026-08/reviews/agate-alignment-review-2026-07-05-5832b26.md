---
review_date: 2026-07-05
reviewer: protocol-alignment-review
change_summary: 删 8文件必读框架 + CHECK 5 — orchestrator 改 mapping 入口，8 文件降为 reference；删 CHECK 5 函数 + FILE_COUNT_ANCHORS + CON.5 测试
files_changed:
  - agate/orchestrator-template.md (mapping 入口化，8 文件降为 reference)
  - agate/state-machine.md:506 (中断恢复改读 mapping + 卡片指引)
  - agate/scripts/check-protocol-consistency.py (删 CHECK 5 + FILE_COUNT_ANCHORS + check_file_count_anchors 函数)
  - agate/tests/integration/consistency.bats (删 CON.5 + 重排编号)
---

# 协议-脚本对齐审查

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | **MISALIGNED** |
| A4 | 测试覆盖 | ALIGNED |
| A5 | 下游影响 + 文档传播 | **MISALIGNED** |
| A6 | 锚点表覆盖 | ALIGNED |

测试与脚本本身：全绿、CHECK 5 真删（对抗测试证实 FILE_COUNT_ANCHORS 已是 dead code）。但 3 个文件未做反向传播（仍引用"8 文件必读" / 旧节名"工作流规则"），CHANGELOG 也未记录这次破坏性变更。

## 逐项审查

### A1: 文档→脚本对齐 — ALIGNED

**文档声明**（orchestrator-template.md:108）：
> 按当前任务阶段，**只读一张阶段卡片**……卡片查不到的信息再回退到本文件末尾的 Fallback reference 节

**文档声明**（orchestrator-template.md:131-142 Fallback 节）：
> 如果 phase-cards 查不到需要的细节，按需查阅下列文件——**这些是 reference，不要求每轮必读**

**脚本实现**（check-protocol-consistency.py:601-610 CHECKS 列表）：
> 8 项检查（CHECK 1-4, 6-9），无 CHECK 5；FILE_COUNT_ANCHORS 已注释为历史（line 78-82）

**实测输出**（python3 check-protocol-consistency.py）：
```
✅ PASS  CHECK 1  YAML 代码块可解析
✅ PASS  CHECK 2  仓库内文件引用存在
✅ PASS  CHECK 3  协议文件无硬编码行号
✅ PASS  CHECK 4  gate_commands 键集合一致
✅ PASS  CHECK 6  LICENSE 与 gstack 归属
✅ PASS  CHECK 7  version badge 与 git tag
✅ PASS  CHECK 8  v0.6 关键词存在性
✅ PASS  CHECK 9  协议-脚本结构对齐
```
0 ERROR、1 WARNING（已知，非本次引入）。

**结论**：文档不再声明 8 文件必读，脚本不再有 CHECK 5 守此计数——二者删的是同一件事，方向一致。

### A2: 脚本→文档对齐 — ALIGNED

**脚本变更**（check-protocol-consistency.py:601-610）：
- CHECK 5 从 CHECKS 列表移除
- check_file_count_anchors 函数体删除
- FILE_COUNT_ANCHORS 数据结构删除
- 脚本头部 docstring（line 11-18）同步跳过 CHECK 5

**文档变更**：
- orchestrator-template.md 头部（line 108）：启动段落从"协议文件（8 个协议文件，依次读完，不可跳过）"改为"只读一张阶段卡片"
- orchestrator-template.md（line 131-142）：新增 Fallback reference 节，8 文件清单移至此处，明确标"非必读"
- state-machine.md:506-507：中断恢复指引指向 mapping 表 + Fallback 节，不再要求重读 8 文件
- consistency.bats: CON.5 删除，CON.6 改为 LICENSE，CON.8 改为 CHECK 9

**结论**：脚本删 CHECK 5 后，文档侧声明"8 文件必读"的措辞也同步删除——双向对齐。

### A3: 一致性连锁 + 反向传播 — **MISALIGNED**

**A3a 连锁（已识别）**：
- ✅ check-protocol-consistency.py docstring 更新（跳 CHECK 5）
- ✅ consistency.bats CON.5 删除
- ⚠️ count-tests.sh 输出 9 用例，bats 文件注释也写"9 用例"——两者自洽，**但 CON.7 编号缺失**（CON.6 → CON.8），不是本次引入，不阻断

**A3b 反向传播（应被影响但未列在 diff 中）—— 3 个文件未同步**：

1. **`agate/loop-orchestration.md:238`**
   > **档位 C 启动前必读**：orchestrator-template.md「工作流规则」8 个协议文件——包括 state-machine.md、platform-notes.md、git-integration.md 的 hardening 集成段。
   - 节名"工作流规则"已不存在（已改为"Fallback：完整协议文件列表"）
   - "8 个协议文件 + 必读"语义已被新模型取代（"按需查阅 reference，非必读"）
   - **应改为**："档位 C 启动前查阅 orchestrator-template.md「Fallback：完整协议文件列表」节按需读取"或类似措辞

2. **`agate/dispatch-protocol.md:247`**
   > 角色定义文件不在主 Agent 的 8 文件启动读取列表里——主 Agent 不需要读它们……
   - "8 文件启动读取列表"框架已废弃——主 Agent 现在用 mapping 表按阶段读一张卡片
   - **应改为**："角色定义文件不在主 Agent 的 mapping 必读路径里"或类似措辞

3. **`agate/scripts/agate-changes.sh:144, 146`**
   > 中等变更（$HIGH_IMPACT 个核心文件）——重读变更的 8 个必读文件中受影响的那几份
   > 重大变更（$HIGH_IMPACT 个核心文件）——完整重读 8 个必读文件
   - "8 个必读文件"措辞与新模型矛盾——没有"必读清单"了
   - **应改为**："重读变更中受影响的核心协议文件"或类似措辞（不限定 8 个，也不限定"必读"）

**结论**：核心反转（orchestrator-template / state-machine / 脚本 / 测试）干净，但反向传播到 loop-orchestration / dispatch-protocol / agate-changes 漏了。

**建议修复方向**：
- loop-orchestration.md:238 删"工作流规则"节名引用 + "必读"措辞
- dispatch-protocol.md:247 删"8 文件启动读取列表"
- agate-changes.sh:144,146 删"8 个必读文件"措辞，改中性表达

### A4: 测试覆盖 — ALIGNED

**测试运行**（bats 全套）：**192/192 全过**

**consistency.bats 实际 9 用例**（数 @test）：CON.1, CON.2, CON.3, CON.4, CON.5(→CHECK 6), CON.6(→CHECK 7), CON.8(→CHECK 9), CON.9(md5 锁定), CON.10(→CHECK 8)

**删除覆盖**：
- CON.5 (CHECK 5 计数) 删除 ✅
- CON.6 重命名到 LICENSE（重排编号） ✅
- CON.7 编号空缺（历史遗留，跳过编号），不阻断 ✅

**结论**：测试完整覆盖新行为（删 CHECK 5 + 跳过该检查），无残留 CON.5 测试断言。

### A5: 下游影响 + 文档传播 — **MISALIGNED**

**破坏性变更**：
1. CHECK 5 从一致性脚本中移除（外部 CI 消费方不再看到这一项）
2. orchestrator-template.md 启动行为从"必读 8 文件"变为"按阶段读一张卡片 + Fallback reference"

**CHANGELOG.md Unreleased 节**（line 9-23）**未提及**：
- "删 8 文件必读框架"——破坏性变更的协议语义变化
- "删 CHECK 5 + CON.5"——脚本检查数从 9 减到 8
- "orchestrator 启动行为变更"——影响所有使用 agate 的项目

**scripts/README.md**（line 60-69）仍写"6 类检查"+ 表格中含 CHECK 5 行（line 68）：
> ## 6 类检查
> | CHECK 5 | 「N 个协议文件」计数声明 == 实际列表长度 | P1-1 |
- 实际现在是 8 类（CHECK 1-4, 6-9）
- 应改为"8 类检查" + 删 CHECK 5 行

**结论**：CHANGELOG 漏掉破坏性变更的记录（外部用户不知道升级时启动行为变了），scripts/README.md 还把 CHECK 5 当作活的检查在介绍——双重 MISALIGNED。

**建议修复方向**：
- CHANGELOG Unreleased 加破坏性变更条目（删 CHECK 5 + 启动行为变化）
- scripts/README.md:60-69 改"8 类检查" + 删 CHECK 5 行

### A6: 锚点表覆盖 — ALIGNED

**check-protocol-consistency.py 锚点表**（CHECK 9）：
- 之前提到"白名单式（和 CHECK 5 同模式）"——已改为"白名单式"（line 439）
- FILE_COUNT_ANCHORS 完全删除
- 其他白名单锚点（README badge / v0.6 关键词 / gate scripts）未受影响

**结论**：锚点表在 CHECK 9 内仍完整覆盖 gate 脚本（SG.6 bats 测试通过）。FILE_COUNT_ANCHORS 删除后，CHECK 5 整体消失，锚点表不需要再包含它。

---

## 附：对 CHECK 5 真删的对抗验证

执行 monkey-patch 注入 `FILE_COUNT_ANCHORS = [{'expected': 999, ...}]` 后加载模块 + 跑全部 CHECKS：
- ✅ 模块仍只有 8 项 CHECKS
- ✅ 无任何函数引用 FILE_COUNT_ANCHORS（grep `obj.__code__.co_names` 确认）
- ✅ 即使 FILE_COUNT_ANCHORS 被外部注入，也无函数能读到它——**彻底 dead code，不会复活为 no-op theater check**

这是评审建议"(a) 删 CHECK 5 + CON.5"路径的正确落地：函数体 + 数据结构 + 测试断言三件全删，不留空壳。

---

## 总结

| 项 | 结论 | 证据 |
|----|------|------|
| A1 | ALIGNED | orchestrator 措辞 / 脚本 CHECKS 列表双向同步 |
| A2 | ALIGNED | 脚本删 CHECK 5 ↔ 文档删"8 文件必读"措辞 |
| A3 | **MISALIGNED** | loop-orchestration.md:238 + dispatch-protocol.md:247 + agate-changes.sh:144,146 漏改 |
| A4 | ALIGNED | 192/192 bats 全过，含 CON.5 删除 |
| A5 | **MISALIGNED** | CHANGELOG Unreleased 漏破坏性变更；scripts/README.md:60-69 还写"6 类检查"+ CHECK 5 行 |
| A6 | ALIGNED | 锚点表不受影响，FILE_COUNT_ANCHORS 完全 dead |

**总判定**：**NEEDS_FIX** — 核心反转（删 CHECK 5 + 8 文件改 reference）正确且对抗测试通过，但 4 处反向传播漏改（loop-orchestration / dispatch-protocol / agate-changes / scripts/README.md）+ CHANGELOG 漏记。需要派 implementer 补这 4-5 处同步，然后重审。

不是 PASS 因为 A3 + A5 都是 MISALIGNED——这些是评审角色能客观判定的文档传播遗漏，不是"判断模糊"。不是 FAIL 因为脚本 + 核心文档 + 测试的"删 CHECK 5"动作本身干净，对抗测试证实不是 theater check。