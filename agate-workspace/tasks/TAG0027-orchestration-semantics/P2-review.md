---
phase: P2
task_id: TAG0027
type: review
parent: P2-design.md
trace_id: TAG0027-P2-review-20260903
created: '2026-09-03'
agent: plan-eng-review
status: approved
---
# TAG0027 P2 方案设计评审（plan-eng-review exit2 复审轮 · 终局）

> 评审对象：`P2-design.md`（修正版 641 行，architect dd858932 exit2fix 轮）+ `P1-requirements.md`
> （[BASELINE_CHANGE] 回改后 26 BDD）
> 评审基准：`P4-review.md`（rejected：CRITICAL-1/2 实证 + Fix A/B/C + DEVIATION-1/2）
> 评审性质：**复审轮（exit2 语义修正闭合核对）**——P4 review 曾 rejected（2 CRITICAL 触及设计）后
> architect 已修 P2-design（exit2fix 轮）+ 主 Agent 已按 [BASELINE_CHANGE] 回改 P1（R1-R8 + BDD-26）。
> 本轮核对修正闭合度并给终局判定。首轮/retry1 approved 的架构方向（候选 A + 8 面形态）不重新
> 全量评审，只核修正波及节。
> 评审依据（全部实读 worktree `agate/` 现状，非 ~/.agate）：check-gate.py / check-judge-verdict.py /
> phases.yaml / phases.schema.json / pre-commit-gate.py / check-protocol-consistency.py +
> P4-review.md + P2-design.md 修正版 + P1-requirements.md 回改版 + P2-progress.md（exit2fix 轮记录）。
> 评审日期：2026-09-03

## 评审范围与方法

复审范围 = P4 review 2 CRITICAL Fix 方向闭合核对 + DEVIATION-1/2 决策记录核对 + P1 回改
（R1-R8/BDD-26）一致性核对 + 已 approved 部分未被推翻抽查。每条结论引用 P2-design 节号 +
外部实证（check-gate.py 行号实读）。

## 闭合核对表（CRITICAL-1 / CRITICAL-2 / DEVIATION-1 / DEVIATION-2 / P1 回改一致性）

| # | P4 review 问题（Fix 方向） | 修正落点（P2-design.md + P1-requirements.md） | 实证核对结论 | 状态 |
|---|--------------------------|--------------------------------------------|------------|------|
| **CRITICAL-1** | agate next 把"exit 2 = 正常通过码"误当暂停 → 主线推进死锁（Fix A：逐 phase 声明 pass_set） | §3.1 gate_pass_exit 字段定案（151-174）+ 逐 phase 出口码表（159-167）+ §3.4 pass_set 三态判定重写（298-325）+ R5/R12 风险行改写 + §9.1 R1/R2/R3/R5 回改清单 | 实证行号与 worktree check-gate.py **全吻合**：gate_p0 L577 / p1 L698 / p2 L883 / p3 L892 / p5 L1048 / p6 L1093 / p8 L1376 `return 2`；gate_p4 L990 / p65 L1110+L1120 / p7 L1241 `return 0`（实读函数体：gate_p4 的 L913 return 2 为"缺 agent 字段 WARNING"非通过路径——§3.1 P4 pass_set 单值 {0} 成立；gate_p5 的 L1016 return 2 为 baseline 损坏降级 WARNING——通过码确为 L1048 return 2，表值无误）。§3.4 判定：exit ∈ pass_set → 直推（含 P0-P3/P5/P8 exit 2 全程可推进，健康任务闭环成立）/ exit 1 → retreat 委托 / 真暂停（∉ pass_set 且 ≠ 1，协议实际极少）→ 落盘 resolution。Fix B 否决理由（BDD-13 禁止面 + pre-commit 账本历史不可迁移）成立；**P6 条件式推进**（gate_p65 exit 0 前置消费 next:P7，§3.1 176-193 + §3.4 301-307）与 gate_p6（恒 return 2 无 exit 0）/ gate_p65（judge 未启用 return 0 早退 / verdict 缺失 return 1 / 双脚本过 return 0）实读逐条对应。**健康任务 exit 2 直推闭环成立（无假 resolution、不停等）** | ✅ 闭合 |
| **CRITICAL-2** | judge 复核谓词把"正常通过的 exit 2 事件"当暂停 → 健康任务 P6.5 必误拦（Fix C：只校验已存在 resolution 文件） | §3.3 复核挂载 Fix C 定案（272-287：文件存在性驱动——存在才校验格式/完整性 + phase 与账本对应；不存在 → 不要求文件，健康任务不误拦；P6 exit 2 条件式推进不落盘）+ §3.9 + §9.1 R6/R7 | Fix C 语义自洽：触发面 = 真暂停落盘（§3.4 收窄），judge 复核谓词 = resolution 文件存在性（文件不在 → 通过）。Fix C vs Fix B 等价性说明 + 采纳理由（唯一落盘场景驱动、实现面小、与 agate next 落盘契约单一来源）充分。check-judge-verdict.py 现文旧谓词（L32-34 / L326-353 `_check_exit2_resolution`：凡 exit:2 非 P6 事件要求 resolution）恰是 P4 待修对象，与 §1.1 Modify 行、files_to_read（496-497）、§5 BDD-12 反向断言锚点一致——**设计给出明确修法（Fix C），implementer 可执行** | ✅ 闭合 |
| **DEVIATION-1** | schema if/then 条件约束未落地（schema 级强制缺失） | §3.9 DEVIATION-1 范围决策（413-430）：schema if/then **不落地** → `gate_pass_exit` 进 schema 全局 required（纯 required 子集支持）+ 数据面 pytest 断言（P6.5 条目无 next/retreat + 含 gate_subphase 三键；主线 9 条目三键齐全）+ S-1 P6.5 负面形态检查承载 + `[DESIGN_GAP: schema 层不强制 P6.5 无 next/retreat 的条件约束（校验器子集不支持 if/then，2026-09-03 定案…）]` 内联立项 | 决策记录完整：P4 review 实证（schema 无 if/then/not；check-yaml-schema.py 子集 L10-11）采纳"第一分支"（改数据面承载），不扩展校验器子集的理由（子集实现膨胀 + 其它 rules schema 消费面回归）记录；DESIGN_GAP 内联标记走既有 P7 配对机制（P2 文档内记立项，P4/P7 转抄——gate_p7 实读确认 [DESIGN_GAP]/[DESIGN_GAP_REVIEWED] 配对硬校验存在）。schema 属性声明（next/retreat/gate_subphase/gate_pass_exit 值域枚举）保留（不动已 approved 部分）。**§7 完成标志与 §5 BDD-2 已同步改为"反例由数据面断言拒绝"** | ✅ 决策已记录 |
| **DEVIATION-2** | CHECK 14 扫描面窄于 P2 §6③ 排查面，assets/ 无机械拦截 | §3.9 DEVIATION-2 范围决策（432-444）：assets 清理 = **一次性**（B3a 已对 architect.md:229 / custom-role.md:49-56 挂注记），CHECK 14 扫描面维持 `agate/*.md` 顶层**不扩 assets/**（避免误伤 assets/templates/dsh/ 平台食谱豁免 + B3b 已落地实现返工）；后续 assets 新增平台名段由角色文件评审流程覆盖（接受面明确） | 决策记录完整：P4 review 实证（check-protocol-consistency.py 只 glob `root/"agate"/*.md` L1233-1237）采纳"记录一次性决策"分支；§6③（573 排查/扫描/豁免三面并陈）+ §7 完成标志（583）+ R8（79）与 §3.9 对齐——"assets 一次性清理、不进 CHECK 14 扫描面"表述全篇一致，无残留"扫描面含 assets"旧叙述 | ✅ 决策已记录 |
| **P1 回改一致性** | R1-R8 + BDD-26 与 P2 修正语义一致 | P1-requirements.md 回改版：R1 需求复述 L52-60 / R2 诚实边界 L85-91 / R3 BDD-6 Given L149 / R4 BDD-8 Given L159 / R5 BDD-11 Then L176 / R6 BDD-12 Given L179 / R7 BDD-12 Then L181 / R8 BDD-13 Then L186 / BDD-26 新增 L254-257 | R1-R8 逐条与 P2 §3.1/§3.3/§3.4/§9.1 回改清单语义一致，每条带 `[BASELINE_CHANGE: ... 主 Agent 显式批准]` 标注（含原因追溯）；BDD-26 与 P2 §9.2 草案逐字一致（P0-P8 + P6.5 全条目 gate_pass_exit ∈ {0,2} + 出口码实证值 P0-P3/P5/P6/P8=2、P4/P7/P6.5=0 + pytest 断言对照 gate_p* return + agate next pass_set 判定）。**发现 1 处回改遗漏（非 BDD、非验收条件，见下）** | ✅ 一致（1 遗留跟进项） |

## P1 I-5 残留（非 BDD 行，主 Agent 跟进项，不构成 P2 缺陷）

- **位置**：P1-requirements.md L101（隐含需求表 I-5「为什么必须」说明列）：
  "exit 2 分支不能按 next 直推（**多数阶段暂停转主 Agent**；P6 例外直通 P6.5）"。
- **定性**：括号解释为 CRITICAL-1 推翻的旧前提残余——与 BDD-26/BDD-6 修正语义直接冲突
  （exit 2 ∈ pass_set 恰按 next 直推）。隐含需求表是 P1 分析过程的"为什么必须"说明，非 BDD
  验收条件；BDD 正文（26 条）已全部按修正语义回改、为验收权威。不阻塞 P4 实现。
- **修复建议**：主 Agent 走 [BASELINE_CHANGE] 微修该行措辞（如 "exit ∈ pass_set（多数 phase
  正常通过码 = exit 2）→ 按 next 直推；真暂停（∉ pass_set 且 ≠ 1）才转主 Agent；P6 经 gate_p65
  前置裁决"），与 R1/R3 同批。参照 retry1 轮 P1 BDD-10 同例处理（approved + 主 Agent 跟进项）。

## 已 approved 部分未被推翻（抽查）

- 架构方向：候选 A（数据面权威 + 薄 CLI 消费方，§2）保持，未因修正改写 ✓。
- 8 决策面形态：除 exit2 修正波及节（§3.1 gate_pass_exit 新增、§3.3 Fix C、§3.4 pass_set 三态、
  §3.7 档位 C 语义校准）外保持；WORKFLOW 加列（§3.2 4/5 列）与 S-1 比对范围不变；**gate_pass_exit
  不加列**（§3.2 223-226：机器声明字段、S-1 比对面只含 next/retreat——与 §3.9 数据面断言分工自洽）
  ✓。
- B3a/B3b 处置面（9 顶层 md + assets 适配段注记 + dsh/ 结构豁免）与 §3.9 DEVIATION-2 决策一致，
  批边界（§8）未失真 ✓。
- 旧语义残留扫描：P2-design.md 全篇 0 命中"exit 2 一律暂停/通用暂停分支"旧表述（除 §3.4 备选
  形态 c 与 R12 的显式否决叙述）；P1 正文 BDD 区 0 残留（仅 I-5 一处，见上）✓。

## 锁定决策（终版）

1. **exit 2 语义修正锁定**：gate_pass_exit 逐 phase 出口码声明（P0-P3/P5/P6/P8=2、P4/P7/P6.5=0）
   = agate next 推进判定基准；exit ∈ pass_set → 直推（健康任务 P0-P3/P5/P8 exit 2 全程可推进）、
   exit 1 → retreat 委托（retreat-to 逐阶）、真暂停（∉ pass_set 且 ≠ 1）→ 落盘 exit2-resolution；
   P6 条件式推进（gate_p65 exit 0 前置）为唯一特例。check-gate 返回约定不改（BDD-13）。
2. **judge 复核谓词 Fix C 锁定**：check-judge-verdict.py P6.5 只校验**已存在** resolution 文件
   格式/完整性 + 与账本对应；健康任务无 resolution 文件 → 不要求、复核通过（不误拦）。
3. **DEVIATION-1/2 范围决策锁定**：schema if/then 不落地（gate_pass_exit 全局 required + 数据面
   断言 + S-1 负面形态 + DESIGN_GAP 立项）；assets 清理一次性（不进 CHECK 14 扫描面）。
4. **P1 回改面锁定**：R1-R8 + BDD-26 已落地（[BASELINE_CHANGE] 授权），与 P2 修正语义一致。

## 结论

P4 review 2 CRITICAL Fix 方向（Fix A gate_pass_exit pass_set / Fix C judge 谓词存在性驱动）在
P2-design 修正版全部落实、与 worktree 代码实证逐条对应、健康任务 exit 2 直推闭环与 judge 反向
不误拦语义成立；DEVIATION-1/2 均记录为范围决策（含 DESIGN_GAP 立项 / 一次性清理声明）；P1 回改
（R1-R8 + BDD-26）与 P2 修正语义一致；已 approved 部分未被推翻、无新引入矛盾。按 dispatch-context
判定：**approved**。遗留跟进项 1（非 P2 缺陷）：P1 I-5 隐含需求行旧前提措辞残留（L101），由主
Agent [BASELINE_CHANGE] 微修一行，与 R1/R3 同批（同 retry1 轮 P1 BDD-10 处理先例）。

## 环境隔离声明

[PROD_NOT_TOUCHED]：本复审只读 worktree agate/ 协议文件（实证核对）+ 写任务目录
P2-progress.md / P2-review.md，未改动任何协议本体文件 / 主 checkout / ~/.agate。
