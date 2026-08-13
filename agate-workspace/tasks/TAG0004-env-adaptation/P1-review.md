---
phase: P1
task_id: TAG0004-env-adaptation
type: review
parent: P1-requirements.md
trace_id: TAG0004-P1-20260813
status: approved
created: 2026-08-13
agent: requirements-review
---

# P1 需求基线评审（复审轮）— TAG0004-env-adaptation

**判定：approved**（37 条 BDD 全部可二值判定；F1/F2/F3 已正确修订闭合；M4 新增 BDD-35/36/37 合格且与 BDD-30/31 互斥自洽；未发现新引入问题）

评审基准：P0-brief 锁定缺陷清单（S1/S2/S3/M4/M5/M6/M9 + Q1/Q2/Q5 + RM-AG0001/AG0002 + TPV0090-M4）+ 代码抽查（check-p6-format.sh:69/84、check-p6-evidence.sh:37、check-tdd-red.sh:70/87-102/104-107、check-gate.sh:356）。

## 上轮 needs-revision 修订核验（F1/F2/F3）

- **F1（BDD-12 小写 Given）已修订**：BDD-12 Given 改为小写 `- fail：3`（line 119），注释明确"走 line 69 `[[:space:]:：]` bracket 归一化路径，区别于已修的 line 84 大写路径"。代码核验：check-p6-format.sh:69 确为 `[[:space:]:：]` bracket 处理小写 pass/fail 路径、:84 为 `(:|：)` alternation 处理大写路径——小写 Given 正确覆盖 line 69 残留，区别于已修 line 84。✅
- **F2（LC_ALL=C locale 前置）已修订**：BDD-11（line 114）、BDD-12（line 119）、BDD-13（line 124）Given 均显式声明"执行前置 `LC_ALL=C`（POSIX locale，回归测试须强制该 locale，默认 C.UTF-8 下不区分修复前后）"。三条闭合。✅
- **F3（BDD-9 括号歧义 + BDD-10 边界）已修订**：BDD-9 Given 改用 ASCII 括号 `(截图 验证通过.png)`（"ASCII 括号包裹、文件名含中文"），When 显式"字符类加宽以支持中文，括号宽度不变仍为 ASCII"——修复范围已澄清（仅字符类加宽、不纳入全角括号）；BDD-10 Given 补"括号内仅有描述性文字无文件名/扩展名（如 `(见截图)`）"边界用例，Then 防修复过宽。✅

## BDD 评审（逐条，全部可二值判定）

- BDD-1: 通过。数据✓ 前端✗ 多端✓ 边界✓ 兼容✓（fail-open 反转判定）
- BDD-2: 通过。数据✓ 前端✗ 多端✓ 边界✓ 兼容✓（逐文件处理断言）
- BDD-3: 通过。数据✓ 前端✗ 多端✓ 边界✓ 兼容✓（切词拆分断言）
- BDD-4: 通过。数据✗ 前端✗ 多端✗ 边界✗ 兼容✓（Linux 回归锚点）
- BDD-5: 通过。数据✓ 前端✗ 多端✗ 边界✓ 兼容✓（grep 断言审计 0/非0 机判）
- BDD-6: 通过。数据✓ 前端✗ 多端✓ 边界✓ 兼容✓（中文读取）
- BDD-7: 通过。数据✓ 前端✗ 多端✓ 边界✓ 兼容✓（中文写回）
- BDD-8: 通过。数据✓ 前端✗ 多端✗ 边界✗ 兼容✓（ASCII 回归锚点）
- BDD-9: 通过。数据✓ 前端✗ 多端✗ 边界✓ 兼容✗（修复范围已澄清：字符类加宽、括号宽度不变，见 F3）✅
- BDD-10: 通过。数据✓ 前端✗ 多端✗ 边界✓ 兼容✗（`(见截图)` 边界已补，防过宽）✅
- BDD-11: 通过。数据✓ 前端✗ 多端✗ 边界✓ 兼容✓（LC_ALL=C 前置已加，P7 总结行排除）✅
- BDD-12: 通过。数据✓ 前端✗ 多端✗ 边界✓ 兼容✓（小写 Given 覆盖 line 69，LC_ALL=C 前置）✅
- BDD-13: 通过。数据✓ 前端✗ 多端✗ 边界✓ 兼容✓（LC_ALL=C 前置 + v0.40.3 对照）✅
- BDD-14: 通过。数据✓ 前端✗ 多端✓ 边界✓ 兼容✓（CRLF 行尾 frontmatter）
- BDD-15: 通过。数据✓ 前端✗ 多端✗ 边界✗ 兼容✓（LF 回归锚点）
- BDD-16: 通过。数据✓ 前端✗ 多端✗ 边界✓ 兼容✓（历史 CRLF 文件不强制改写）
- BDD-17: 通过。数据✓ 前端✗ 多端✓ 边界✓ 兼容✓（正则元字符）
- BDD-18: 通过。数据✓ 前端✗ 多端✓ 边界✓ 兼容✓（\r 尾字符）
- BDD-19: 通过。数据✓ 前端✗ 多端✓ 边界✓ 兼容✓（复制模式 AGATE_ROOT）
- BDD-20: 通过。数据✓ 前端✗ 多端✓ 边界✓ 兼容✓（sed 特殊字符）
- BDD-21: 通过。数据✓ 前端✗ 多端✓ 边界✓ 兼容✓（盘符/反斜杠）
- BDD-22: 通过。数据✓ 前端✗ 多端✗ 边界✗ 兼容✓（Linux 字节输出回归锚点）
- BDD-23: 通过。数据✓ 前端✗ 多端✗ 边界✗ 兼容✓（7 卡逐张核对）
- BDD-24: 通过。数据✓ 前端✗ 多端✗ 边界✓ 兼容✓（commit 顺序/gate 逻辑不变）
- BDD-25: 通过。数据✓ 前端✗ 多端✗ 边界✗ 兼容✓（consistency 0 ERROR）
- BDD-26: 通过。数据✓ 前端✗ 多端✓ 边界✗ 兼容✓（SETUP Windows 章节）
- BDD-27: 通过。数据✓ 前端✗ 多端✗ 边界✗ 兼容✓（.gitignore 预设条目）
- BDD-28: 通过。数据✓ 前端✗ 多端✗ 边界✓ 兼容✓（反引号包裹 SUGGEST 识别）
- BDD-29: 通过。数据✓ 前端✗ 多端✗ 边界✓ 兼容✓（反引号包裹 NEED_CONFIRM 阻塞）
- BDD-30: 通过。数据✓ 前端✗ 多端✗ 边界✓ 兼容✓（无 formatter A 类：compile/error 关键词）
- BDD-31: 通过。数据✓ 前端✗ 多端✗ 边界✓ 兼容✓（无 formatter B 类：普通断言失败，与 BDD-30 互斥）
- BDD-32: 通过。数据✓ 前端✗ 多端✗ 边界✗ 兼容✓（全量 bats 回归锚点）
- BDD-33: 通过。数据✓ 前端✗ 多端✓ 边界✗ 兼容✓（CI windows-latest matrix，判定依赖 CI 报告可接受）
- BDD-34: 通过。数据✓ 前端✗ 多端✗ 边界✗ 兼容✓（shellcheck 0 error）
- BDD-35: 通过。数据✓ 前端✗ 多端✗ 边界✓ 兼容✓（M4 新增：NameError → B 类 exit 0；与 BDD-30/31 无 formatter 路径边界互斥——本组走 formatter 路径 syntax_errors/import_errors/errors 字段）✅
- BDD-36: 通过。数据✓ 前端✗ 多端✗ 边界✓ 兼容✓（M4 新增：globals().get() 规避模式向后兼容 exit 0）✅
- BDD-37: 通过。数据✓ 前端✗ 多端✗ 边界✓ 兼容✓（M4 新增：真实 bug TypeError 仍 A 类 exit 1，防过宽；与 BDD-35 互斥自洽）✅

BDD 编号连续性核验：BDD-1..37 全部存在、无跳号（grep 核验 57/62/.../265 行，37 条全列）。

## 隐含需求覆盖

- 数据维度：**覆盖**。I1（encoding 断言审计）→ BDD-5；I3（中文文件名回归）→ BDD-9/10；I4（历史 CRLF）→ BDD-16；S1/S2/S3/M4/M5/M6/M9 数据边界均落 BDD。
- 前端维度：**不适用**（domains 未声明 frontend，正确）。
- 多端维度：**覆盖**。I2（CI windows matrix）→ BDD-33；Q1 双平台 → BDD-21/22；Windows 降级验证策略在 capability_requirements 声明。
- 边界维度：**覆盖**。空格路径（S1）、全角冒号（M4/M5，LC_ALL=C 前置补齐）、CRLF/\r（M6）、正则元字符（M9）、反引号包裹（RM-0001）、`(见截图)` 无文件名边界（BDD-10）、NameError 与真实 bug 边界（BDD-35/37）。
- 兼容维度：**覆盖**。Linux 基线回归锚点贯穿（BDD-4/8/15/22/32/34）；v0.40.3 对照（BDD-13）；globals().get() 规避模式不回退（BDD-36）；"不破坏协议语义"由 BDD-24/25 约束。

## 裁剪评审

- **P1 保留**：核心阶段不可裁，合理。
- **P2 保留**：46 脚本 + 多方案评估（M6 修法、S1 数组化、Q1 归一化），medium 风险需设计评审，理由充分。
- **P3 保留**：改脚本 TDD 先行是 AGENTS.md 硬性约定；I1/I3/M4 需新增失败测试，理由充分。
- **P4 保留**：46 脚本实际改动，不可裁，合理。
- **P5 保留**：全量 bats + shellcheck + consistency 客观证据，理由充分。
- **P6 保留**：逐条 BDD-1..37 验收（计数 ≥37），不可裁，合理。
- **P7 保留**：46 脚本跨文件交叉核对 + phase-cards 一致性（I7 SELF-GATE），理由充分。
- **P8 保留**：协议本体变更需发布，`internal_only: false`，合理。

**risk_level: medium**：与"46 脚本改动 + SEVERE fail-open + 跨 Linux/Windows 双平台"匹配，合理。

**capability_requirements 三态**：windows-runtime=supplementable（CI 兜底，不宣称已实测 Windows，符合约束）；grep-assert-audit / bats-test-framework / shellcheck / protocol-consistency=available 均属实；无 GAP 漏标。

## 新增问题检查

- **无新引入问题**：F1/F2/F3 修订仅改动 Given 表述与前置声明，未改变 BDD 语义结构；M4 三条 BDD（35/36/37）走 formatter 字段路径，与 RM-AG0002（30/31）无 formatter 路径在 Given 条件上互斥（formatter 存在性）、判定方向自洽（NameError→B、真实 bug→A、规避模式→B），无矛盾。
- M4 代码锚点核验属实：check-tdd-red.sh:70（import_count）、:87-102（import_errors B 类检测）、:104-107（`errors>0` 一律 A 类）——BDD-35 Given 的"NameError 落入 errors 被误判 A 类"与代码一致。

## 结论

**approved**。37 条 BDD 连续且全部可二值判定；F1（BDD-12 小写 line 69）、F2（BDD-11/12/13 LC_ALL=C）、F3（BDD-9 ASCII 括号 + BDD-10 `(见截图)` 边界）已正确修订；M4 新增 BDD-35/36/37 合格、与 BDD-30/31 边界互斥自洽；五维覆盖完整、裁剪与能力声明合理、无新引入问题。

## 环境约束记录

- `[PROD_NOT_TOUCHED]` 本评审仅读 worktree 内文件（P1-requirements.md / P0-brief.md / 脚本代码抽查），未接触任何生产环境。
