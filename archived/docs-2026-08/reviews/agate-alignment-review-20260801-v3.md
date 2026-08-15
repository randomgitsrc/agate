---
review_date: 2026-08-02
reviewer: protocol-alignment-review
change_summary: T075 复盘的 3 个效率问题（P2.61 gate 命令可执行性检查 / P2.62 P3 自检注入 + 经典红灯提示 / P2.63 修复轮 dispatch-context 模板）从"角色文件规则"升级为"机制/脚本"
files_changed: [agate/scripts/check-gate.sh, agate/scripts/check-tdd-red.sh, agate/scripts/agate-render-dispatch-prompt.sh, agate/assets/templates/dispatch-prompt.md, agate/tests/unit/check-gate.bats, agate/tests/unit/check-tdd-red.bats, agate/tests/unit/agate-render-dispatch-prompt.bats, agate/tests/README.md, docs/hardening-roadmap.md, docs/plans/agate-t075-mechanism-fixes-20260801.md]
---

# 协议-脚本对齐审查（T075 机制化修复 P2.61-P2.63）

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | MISALIGNED |
| A3 | 一致性连锁 + 反向传播 | MISALIGNED |
| A4 | 测试覆盖 | ALIGNED |
| A5 | 下游影响 + 文档传播 | MISALIGNED |
| A6 | 锚点表覆盖 | ALIGNED |
| A7 | 设计原则一致性 | ALIGNED |

## 逐项审查

### A1: 文档→脚本对齐

**文档声明**（dispatch-prompt.md:100-106，P3 派发追加块）：
> ## P3 自检（强制）
> 产出测试代码后，必须自跑测试，确认每个红灯的失败原因都是"被测模块未实现"……
> 如果某个红灯的失败原因是"断言与测试数据矛盾"……这是测试代码 bug，先修正断言再交付……

**roadmap 声明**（docs/hardening-roadmap.md P2.61/P2.62/P2.63 标题块，状态=已实施）：
- P2.61：check-gate.sh P2 分支增加命令可执行性检查（机制层，**WARNING 不阻断**）
- P2.62：dispatch-prompt.md 新增 P3 派发追加块（强制自检，机械注入每次 P3 派发）+ check-tdd-red.sh 经典红灯分支输出断言矛盾提示（WARNING）
- P2.63：dispatch-prompt.md 新增修复轮派发追加块（主 Agent 模板：引用上轮 + 只写增量）

**脚本实现**：
- check-gate.sh:137-173：解析 `gate_commands` 第一个 token → `command -v` 验证存在性 → 缺失时 stderr WARNING（exit 2 不变，P2 仍"需主 Agent 自判"）。含 `_formatter`/`project_module` 跳过、`/` 路径跳过、`=` 环境变量前缀跳过。
- check-tdd-red.sh:134-138：经典红灯分支 echo 断言矛盾提示到 stderr，return 0 不变。
- agate-render-dispatch-prompt.sh:85-87：case 新增 P3 分支，sed 区间 `/^### P3 派发追加$/` 到 `/^### /` 正确截取 P3 块（RP.16 实测通过）。

**结论**：ALIGNED
**差异**：无。三处机制与文档声明语义一致，全部为 WARNING/新增块，未改变 gate exit code 语义（与 roadmap「WARNING 不阻断」一致）。

### A2: 脚本→文档对齐

**脚本/模板行为**（dispatch-prompt.md 新增 P3 派发追加块 L100-106 + 修复轮派发追加块 L177-183；agate-render-dispatch-prompt.sh P3 接线 L85-87）

**对应协议文档**（dispatch-protocol.md「阶段特定提示（按需追加到 prompt 末尾）」L498-567）：只有 P2 / P4 / P5/P6 / P8 块，**无 P3 派发追加块，也无修复轮派发追加块**。

**同步声明**（dispatch-prompt.md:4）：
> 本模板与 dispatch-protocol.md「派发 prompt 模板」节保持同步，**协议文件为权威来源**

**结论**：MISALIGNED
**差异**：dispatch-prompt.md 新增的 P3 自检（强制行为）和修复轮模板（P2.63）只存在于模板文件，未同步到权威来源 dispatch-protocol.md 的「阶段特定提示」节。读协议文件的人无法得知 P3 派发现在强制自检、修复轮派发要用增量 dispatch-context。声明"模板与协议文件保持同步、协议文件为权威来源"，实际模板已成为 P3 行为的唯一事实源——层级倒置。
**建议**：在 dispatch-protocol.md「阶段特定提示」节补齐 P3 派发追加块和修复轮派发追加块（与 dispatch-prompt.md 对应块同文案），或修正 dispatch-prompt.md:4 的同步声明。

### A3: 一致性连锁 + 反向传播

**A3a（连锁，已知衍生改动）**：
- P3 块插入 P2 与 P4 之间：P2 sed 区间终点从 P4 头变为 P3 头，P2 内容完整保留（RP.5 实测通过）。
- 修复轮块插入 P4 回退与 P8 之间：P4 回退 sed 区间终点从无头变为修复轮头，`sed '/^### /d'` 剔除 heading，extract_first_code_block 取第一个 fence，回退块内容完整（RP.7 实测通过）；P8 sed 区间从其 heading 到 EOF（其后无 `### ` 头），不受影响（RP.9 实测通过）。
- 修复轮块**未用 code fence 包裹**（dispatch-prompt.md:177-183），与其余追加块（P2/P3/P4/P5P6/P8 均有 ``` 包裹）风格不一致；但因无 render case 读取它（仅主 Agent 手工参考），功能无影响。属风格一致性问题。
- 所有改动 WARNING/新增块，无破坏性变更；state-machine.md P2/P3 转移规则无需改（exit 语义未变）。

**A3b（反向传播，主动推断应被影响的文件）**：

| 应被影响文件 | 是否更新 | 验证 |
|---|---|---|
| dispatch-protocol.md「阶段特定提示」节 | ❌ 未更新 | 见 A2（权威来源缺口） |
| CHANGELOG.md | ❌ 未更新 | 见 A5 |
| architect.md（gate_commands 校验清单） | ❌ 未更新 | **刻意设计**——P2.61 原计划加角色清单，实施改为机制层（check-gate.sh 检查），hardening-roadmap 已记录"→ gate 脚本检查"。符合"机制不依赖 agent 自觉"意图。可接受，但建议 architect.md gate_commands 节补一句"P2 gate 会校验命令可执行性"提示，非强制 |
| test-designer.md（P3 自检/断言矛盾） | ❌ 未更新 | 刻意设计——自检经 dispatch-prompt 机械注入，角色文件不加噪音。可接受 |
| P3-tdd.md 阶段卡片 | ❌ 未更新 | 卡片"派发 prompt"指向 dispatch-prompt.md，机制经渲染生效；主 Agent 手写 prompt 时不生效（渲染脚本非强制路径）。可接受但建议卡片补"P3 派发须含自检块"提示 |
| tests/README.md | ✅ 更新 | unit 行已修正（check-gate 95 / render 16 / tdd-red 31 与 count-tests.sh 实测一致）|

**结论**：MISALIGNED
**差异**：A3a 连锁全部验证通过（render 区间无破坏）；A3b 主缺口 = dispatch-protocol.md 权威来源未同步 + CHANGELOG 未标注（见 A5）。角色文件/P3 卡片未更新属"机制不依赖自觉"的刻意取舍，记录为可接受项。
**建议**：补 dispatch-protocol.md 两处块；CHANGELOG 补条目；可选补 P3-tdd.md 提示。

### A4: 测试覆盖

**新增测试**：
- P2.61：check-gate.bats `G_CMD_EXEC.1`（不可执行 → WARNING 不阻断 exit 2）+ `G_CMD_EXEC.2`（均可执行 → 无 WARNING）
- P2.62：check-tdd-red.bats `TD.FAIL_HINT`（经典红灯输出含"断言…数据"）+ agate-render-dispatch-prompt.bats `RP.16`（P3 render 含"P3 自检"）+ check-gate.bats `D-drift-5`
- P2.63：check-gate.bats `D-drift-6`（模板含"修复轮派发追加"）

**边界覆盖缺口（minor）**：P2.61 的跳过分支（env 前缀 `=`、`$(...)`、`/` 路径、`_formatter`、`project_module`）无专属测试——commit 2276e06"skip env-prefixed tokens"的修复行为没有回归测试。核心路径（可执行/不可执行）已覆盖。

**全量实跑输出**（最近一次，本次审查执行）：

```
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
exit=0
ok = 519 个
not ok = 0 个
（末行为 ok 519 SG.8 SELF-GATE.md 含递归终止条件）
```

- 目标文件定向测试：check-gate.bats（95 @test）✓、check-tdd-red.bats（31 @test）✓、agate-render-dispatch-prompt.bats（16 @test，含 RP.16）✓ 全部通过
- shellcheck -S warning：check-gate.sh / check-tdd-red.sh / agate-render-dispatch-prompt.sh 均 0 告警
- count-tests.sh：总计 513，与 README 修正后 unit 行一致

**结论**：ALIGNED（含 minor 边界测试缺口，不阻断）

### A5: 下游影响 + 文档传播

**破坏性**：无。P2.61 WARNING（exit 2 不变，不阻断已有 P2 gate）；P2.62 提示 exit 0 不变；P2.63 为新增模板块；render 脚本 P3 为新增分支。既有项目 gate 行为不回归（519/519 全过）。

**CHANGELOG 标注**：❌ 缺失。CHANGELOG.md [Unreleased]（L9-23）含 P2.51-P2.57 等条目，**无 P2.61/P2.62/P2.63**。本次变更属协议语义变更（P3 派发强制自检 = 新协议行为；P2 gate 新增检查 = 新机制；修复轮模板 = 新流程指引），反向传播表明确"CHANGELOG.md 未更新 + 协议语义变更 + 未标注 = A5 下游影响不完整"。

**文档传播**：hardening-roadmap.md ✅（三个 P2.6x 已标"已实施"）；tests/README.md ✅（unit 行）；dispatch-protocol.md ❌（见 A2/A3b）。

**tests/README.md 残余漂移（minor，既有）**：integration 行仍不准（pre-commit-hook 表列 5 实际 37；consistency 表列 10 实际 11；self-gate 表列 6 实际 8）。为既有漂移，本次 commit 只修正了 unit 行，未全表对齐 count-tests.sh。

**计划文件漂移（minor）**：docs/plans/agate-t075-retro-fixes-20260801.md 仍写 P2.62/P2.63"不修"、P2.61 走 architect.md 清单——与最终实施的机制化方案不一致（docs/plans 属历史规划，非协议，建议标注 superseded 或更新）。

**结论**：MISALIGNED
**差异**：CHANGELOG 未标注 P2.61-P2.63 三项机制化变更。
**建议**：[Unreleased] 增补三条（可合并为一条 T075 机制化：P2.61 gate_commands 可执行性 WARNING / P2.62 P3 自检注入 + 经典红灯提示 / P2.63 修复轮 dispatch-context 模板）。

### A6: 锚点表覆盖

**验证**：CHECK 9 锚点表（check-protocol-consistency.py:444-627）——P2.61 在已有锚点 check-gate.sh 内（已有 P2 agent=main / DESIGN_GAP / BDD-[0-9] 锚点覆盖该脚本）；P2.62 在已有锚点 check-tdd-red.sh 内（"TDD 红灯检查"锚点）+ dispatch-prompt.md（"EXIT_CODE 格式约定"锚点已覆盖）；agate-render-dispatch-prompt.sh 非 check-*.sh gate 脚本，`check_anchor_coverage` 反向扫描只覆盖 check-*.sh + pre-commit-gate.sh + ci-gate-backstop.py，无需加锚点。无新增 gate 脚本，无需新增锚点。

**check-protocol-consistency.py 实跑**：0 ERROR（12 个 WARNING 均为既有叙事文件引用问题，与本次变更无关）；CHECK 9 结构对齐 PASS。

**结论**：ALIGNED

### A7: 设计原则一致性

逐条对照 agate/adr.md：
- **ADR-002（可判定性）**：P2.61 用 WARNING 不阻断、P2 gate 仍 exit 2"主 Agent 自判"——尊重"不可脚本化的部分用 exit 2 标记需人工判断"的边界，不越权硬拦截。✅
- **ADR-003（最小约定/不绑定技术栈）**：P2.61 用 `command -v` 通用检查命令存在性，不绑定任何具体框架/语言。✅
- **ADR-001/006（隔离性/自查≠gate）**：P2.62 的 P3 自检是注入 subagent 的自我检查，最终 gate 仍是主 Agent 亲跑 check-tdd-red.sh（"自查≠gate"原则不变）；提示是 WARNING 不改变 A/B 类判定。✅
- **机制不依赖 agent 自觉**：P2.61-P2.63 全部落为脚本/模板注入（机制层），与 roadmap 及 CHANGELOG 历史中的 hardening 方向（P2.5x 全为机制化）一致。该哲学已在多文档记录，非新架构决策，无需新增 ADR。

**结论**：ALIGNED

## 闭环规则

| 结论 | 主 Agent 动作 |
|------|--------------|
| A2 MISALIGNED | **必须修复**：dispatch-protocol.md「阶段特定提示」节补 P3 派发追加 + 修复轮派发追加两块（对齐 dispatch-prompt.md），或修正同步声明 |
| A3 MISALIGNED | **必须修复**：随 A2/A5 一并处理（dispatch-protocol.md + CHANGELOG） |
| A5 MISALIGNED | **必须修复**：CHANGELOG [Unreleased] 补 P2.61-P2.63 条目 |
| 其余 ALIGNED | 通过 |

## 人工验收清单

- [x] 审查报告含 A1-A7 七项，每项有结论
- [x] MISALIGNED 项有差异描述 + 建议方向
- [ ] 每条 NEEDS_HUMAN_REVIEW 下面有 `[HUMAN_CONFIRMED: ...]` 标记（本次无 NEEDS_HUMAN_REVIEW 项）
- [x] 审查报告落盘到 docs/reviews/agate-alignment-review-20260801-v3.md
