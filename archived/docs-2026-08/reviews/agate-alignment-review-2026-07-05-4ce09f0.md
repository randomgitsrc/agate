---
review_date: 2026-07-05
reviewer: protocol-alignment-review
change_summary: 上一轮 (5832b26) 评审发现 5 处反向传播漏改 + CHANGELOG 漏记，本次 4ce09f0 修复版
files_changed:
  - agate/loop-orchestration.md:238 (档位 C 启动前"必读"→"查阅")
  - agate/dispatch-protocol.md:247 (8 文件启动读取 → mapping 必读路径)
  - agate/scripts/agate-changes.sh:144,146 (删 8 个必读文件措辞)
  - CHANGELOG.md (Unreleased 加破坏性变更节)
  - agate/scripts/README.md (6 类检查 → 8 类检查 + 删 CHECK 5 行)
---

# 协议-脚本对齐审查（4ce09f0 修复版）

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | **MISALIGNED**（新发现 1 处漏改）|
| A4 | 测试覆盖 | ALIGNED |
| A5 | 下游影响 + 文档传播 | ALIGNED |
| A6 | 锚点表覆盖 | ALIGNED |

**总判定**：**NEEDS_FIX**

上一轮 (5832b26) 评审指出的 5 处漏改（loop-orchestration.md:238 / dispatch-protocol.md:247 / agate-changes.sh:144,146 / CHANGELOG / scripts/README.md）**全部修复干净**。本次审查在更高一阶的 reverse-propagation 搜索中发现 1 处 **新的** active 反向传播遗漏：

**`agate/scripts/agate-summary.sh:81` 仍写"按 orchestrator-template.md 列的 8 文件必读顺序读规则"**——这正是上一轮被删除的"8 文件必读"框架，在面向 agent 启动的输出脚本里复活了。`agate-summary.sh` 是 agent 启动时第一个跑的脚本（orchestrator-template.md:128 引用），这一行直接矛盾于 orchestrator 新模型（"按 phase 读一张卡片 + Fallback reference"）。需要改。

---

## 逐项审查

### A1: 文档→脚本对齐 — ALIGNED

**文档声明**（orchestrator-template.md:131-142 Fallback 节）：
> 这些是 reference，不要求每轮必读

**脚本实现**（check-protocol-consistency.py:601-610 CHECKS 列表）：
```python
CHECKS = [
    ("CHECK 1  YAML 代码块可解析", check_yaml_parseable),
    ...
    ("CHECK 9  协议-脚本结构对齐", check_script_alignment),
]
```
（无 CHECK 5，共 8 项）

**实测**：
- `python3 agate/scripts/check-protocol-consistency.py` 0 ERROR、1 WARNING（已知 analyst.md 示例 YAML 不严格可解析，非本次引入）
- CHECK 5 真删的对抗验证（详见末尾附 A）：monkey-patch 注入 `FILE_COUNT_ANCHORS = [{'expected': 999, ...}]` 后，模块 CHECKS 仍只有 8 项，无任何函数读这个外部注入的常量——确认 FILE_COUNT_ANCHORS 是真正的 dead code（无空壳 theater check 风险）

**结论**：文档不再声明 8 文件必读，脚本不再守此计数——双向删的是同一件事，方向一致。

### A2: 脚本→文档对齐 — ALIGNED

**脚本侧**：
- ✅ `check-protocol-consistency.py:601-610`：CHECKS 列表 8 项，无 CHECK 5
- ✅ `check-protocol-consistency.py:78-82`：保留历史注释（说明为何删）+ 删 `FILE_COUNT_ANCHORS` 数据 + 删 `check_file_count_anchors` 函数
- ✅ `consistency.bats`：CON.5 删除，CON.6→CHECK 7 / CON.8→CHECK 9（CON.7 编号空缺为历史遗留，非本次引入）

**文档侧**：
- ✅ `orchestrator-template.md:108-119`：启动段落改为"按当前任务阶段，只读一张阶段卡片"+ mapping 表
- ✅ `orchestrator-template.md:131-142`：新增「Fallback：完整协议文件列表」节，明标 reference 非必读
- ✅ `state-machine.md:506-507`：中断恢复指向 mapping + Fallback 节，删 8 文件枚举清单

**结论**：脚本删 CHECK 5 ↔ 文档删"8 文件必读"措辞——双向一致。

### A3: 一致性连锁 + 反向传播 — **MISALIGNED**

**A3a 连锁（已知衍生改动）**：
- ✅ `check-protocol-consistency.py:11-18` docstring 同步跳过 CHECK 5
- ✅ `consistency.bats` CON.5 删除 + CON.6/8 重排到 CHECK 7/9
- ✅ count-tests.sh 输出 192 用例 + bats run 198 (含 sanity.bats 6 用例) 双向一致

**A3b 反向传播修复验证（针对上一轮 3 处漏改）**：
1. ✅ `agate/loop-orchestration.md:238`：
   > **档位 C 启动前查阅**：orchestrator-template.md「Fallback：完整协议文件列表」节——按需查阅 state-machine.md、platform-notes.md、git-integration.md 等的 hardening 集成段（reference，非必读）。
   - "必读"→"查阅"，"工作流规则"节名（已删）→「Fallback：完整协议文件列表」
2. ✅ `agate/dispatch-protocol.md:247`：
   > 角色定义文件不在主 Agent 的 mapping 必读路径里……
   - "8 文件启动读取列表"→"mapping 必读路径"
3. ✅ `agate/scripts/agate-changes.sh:144,146`：
   ```
   echo "  中等变更（$HIGH_IMPACT 个核心文件）——查阅变更涉及的协议文件"
   echo "  重大变更（$HIGH_IMPACT 个核心文件）——完整重读所有协议文件"
   ```
   - 删"8 个必读文件"硬编码措辞

**A3b 反向传播新发现（本次审查补漏）**：

**`agate/scripts/agate-summary.sh:81` 仍含 active "8 文件必读"措辞**：

```bash
# agate-summary.sh — 输出当前 agate 版本 + 启动必读 + 防护状态
# ...
echo "=== 启动时建议 ==="
1. 第一行：上面这一段（确认协议版本 + 防护机制就位）
2. 读 ~/.agate/AGENTS.md（协议本体入口指引）
3. 读 ~/.agate/CHANGELOG.md（$CURRENT_TAG 段，了解自上次会话以来发生了什么）
4. 按 orchestrator-template.md 列的 8 文件必读顺序读规则  ← MISALIGNED
```

问题分析：
- `agate-summary.sh` 是 agent 启动时第一个跑的脚本（被 orchestrator-template.md:128 引用）
- 这是面向 agent 的**主动建议**输出，不是注释/历史文档
- "8 文件必读顺序"与新模型（按 phase 读一张卡片 + Fallback reference）**直接矛盾**
- 上一轮评审（5832b26）漏掉了这个文件——只在 loop-orchestration / dispatch-protocol / agate-changes 三个文件查了"8 文件必读"，没查 agate-summary.sh
- 应改为："按 mapping 表加载当前阶段卡片（orchestrator-template.md「按阶段加载」小节）——卡片查不到的信息回退到 Fallback reference 节" 或类似措辞

**修复建议**：将第 4 行改为：
```bash
4. 按 orchestrator-template.md「按阶段加载」表读当前阶段的阶段卡片（`~/.agate/phase-cards/P{N}-*.md`）；卡片查不到的信息回退到「Fallback：完整协议文件列表」节（reference，非必读）
```

**结论**：核心 5 处修复完整，但反向传播到 agate-summary.sh 漏了——这是一个**显式的行为冲突**（agent 启动脚本输出的建议直接违反新协议模型）。需要补 1 处。

### A4: 测试覆盖 — ALIGNED

**测试运行**：
```
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
→ 198/198 OK（含 sanity.bats 6 用例）
```

**consistency.bats 实际 9 用例**：
- CON.1 → CHECK 1
- CON.2 → CHECK 2
- CON.3 → CHECK 3
- CON.4 → CHECK 4
- CON.5 → CHECK 6 (LICENSE)
- CON.6 → CHECK 7 (version badge)
- CON.7 编号空缺（历史遗留，跳过）
- CON.8 → CHECK 9
- CON.9 → md5 去重锚点（lock 实现存在）
- CON.10 → CHECK 8

**删除覆盖**：
- ✅ CON.5 (CHECK 5 计数) 删除
- ✅ CHECKS 列表无 CHECK 5
- ✅ 无残留 FILE_COUNT_ANCHORS 引用

**结论**：测试完整覆盖新行为（删 CHECK 5 + 跳过该检查）。

### A5: 下游影响 + 文档传播 — ALIGNED

**CHANGELOG Unreleased 破坏性变更节**（line 24-29）：
```markdown
### 破坏性变更（Breaking Changes）
- **删"8 个协议文件必读"框架**：orchestrator 启动从"读完 8 文件"改为"按 phase 读一张阶段卡片 + Fallback reference"。阶段卡片（`agate/phase-cards/P{N}-*.md`）成为默认入口，8 文件降为按需查阅的 reference。映射见 `agate/orchestrator-template.md` 的「按阶段加载」小节
- **删 CHECK 5（协议文件计数校验）**：`check-protocol-consistency.py` 不再校验"8 文件必读清单计数"——该计数已无协议意义。检查项从 9 减到 8（CHECK 1-4, 6-9）。`agate/tests/integration/consistency.bats` 删 CON.5，重排后续编号
- **state-machine.md:506 中断恢复语义更新**：从"重读 8 文件"改为"读 mapping 表查当前阶段卡片 + 按卡片指引"。删 :507-508 旧 8 文件枚举清单
- **反向传播同步**：loop-orchestration.md:238 / dispatch-protocol.md:247 / agate-changes.sh:144,146 同步删"8 文件必读"措辞
- **scripts/README.md 改"8 类检查"**（从 6 类修正）
```

5 项破坏性变更条目齐全：含框架删除 / CHECK 5 删除 / state-machine 语义更新 / 反向传播同步 / README 修订。

**scripts/README.md**：
- ✅ `## 6 类检查` → `## 8 类检查`（line 60）
- ✅ 表格中 CHECK 5 行删除（line 67-68）
- ✅ 新增 CHECK 7/8/9 行（line 69-71）
- ✅ 加注 "CHECK 5 已删除" 解释（line 73）

**结论**：CHANGELOG 破坏性变更节完整 + scripts/README.md 同步——A5 ALIGNED。

### A6: 锚点表覆盖 — ALIGNED

**CHECK 9 锚点表**（check-protocol-consistency.py:414-527）：
- 已删"白名单式（和 CHECK 5 同模式）"引用（line 439）
- 其他白名单锚点（README badge / v0.6 关键词 / gate scripts）未受影响
- `check_anchor_coverage` 函数（line 562-589）反向兜底：扫描所有 gate 脚本，确认每个都在锚点表里
- SG.6 测试通过（line 196 of bats 输出）

**结论**：CHECK 5 整体消失后，锚点表不需要再包含它；FILE_COUNT_ANCHORS 完全删除，无 dead-data 风险。

---

## 附 A：对 CHECK 5 真删的对抗验证

执行 monkey-patch 注入 `FILE_COUNT_ANCHORS = [{'expected': 999, ...}]` 后加载模块 + 检查所有函数的 `__code__.co_names`：

```
CHECKS list: ['CHECK 1', 'CHECK 2', 'CHECK 3', 'CHECK 4', 'CHECK 6', 'CHECK 7', 'CHECK 8', 'CHECK 9']
Functions that reference FILE_COUNT_ANCHORS in co_names:
  NONE — FILE_COUNT_ANCHORS is dead code, even when externally injected.
mod.FILE_COUNT_ANCHORS after injection: [{'expected': 999, ...}]
  (visible at module level, but no function reads it)
```

**结论**：CHECK 5 函数体 + FILE_COUNT_ANCHORS 数据结构 + CON.5 测试三件全删，无空壳 theater check 风险。

## 附 B：Shellcheck 状态

仅 2 处 info/warning（SC2015/SC2001），均为历史代码模式（`A && B || C`、`sed s///`），**非本次引入**。

---

## 总结

| 项 | 结论 | 证据 |
|----|------|------|
| A1 | ALIGNED | orchestrator 措辞 / 脚本 CHECKS 列表双向同步，对抗测试证实 CHECK 5 真删 |
| A2 | ALIGNED | 脚本删 CHECK 5 ↔ 文档删"8 文件必读"措辞 |
| A3 | **MISALIGNED** | 上一轮 3 处漏改已修复，但新发现 `agate-summary.sh:81` 仍含 "8 文件必读顺序" 主动建议——active 行为冲突 |
| A4 | ALIGNED | 198/198 bats 全过，CON.5 删除 + CHECK 5 真删 |
| A5 | ALIGNED | CHANGELOG 破坏性变更节 5 项齐全 + scripts/README.md 同步 |
| A6 | ALIGNED | 锚点表 SG.6 通过，FILE_COUNT_ANCHORS 完全 dead |

**总判定**：**NEEDS_FIX**

需要补 1 处：`agate/scripts/agate-summary.sh:81` 的"按 orchestrator-template.md 列的 8 文件必读顺序读规则"改为新模型（按 mapping 表加载当前阶段卡片 + Fallback reference）。这是上一轮 (5832b26) 评审漏掉的反向传播目标——修复后本组改动达到完整 PASS。

不是 PASS 因为有一处 active 行为冲突未消除（agent 启动脚本直接输出违反新模型的建议）。不是 FAIL 因为上一轮发现的 5 处全部修复正确，对抗测试证实 CHECK 5 真删是干净落地，不是空壳 theater。

**主 Agent 动作建议**：派 implementer 改 `agate-summary.sh:81` 一行，然后重审确认无新遗漏。