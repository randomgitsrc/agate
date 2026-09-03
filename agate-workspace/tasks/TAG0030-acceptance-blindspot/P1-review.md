---
phase: P1
task_id: TAG0030
trace_id: TAG0030-P1-20260904
agent: requirements-review
status: approved
---

# P1-review — TAG0030 需求基线评审（requirements-review）

[PROD_NOT_TOUCHED]——纯协议文档面评审，未触生产环境。

评审对象：`P1-requirements.md`（259 行，BDD-1~21，analyst 产出）。
评审结论：needs-revision。打回要点仅一处硬阻断：frontmatter `phases` 漏 P2，
与 §3"全覆盖、无裁剪 / P2 不可裁"文字自相矛盾，且触 check-pruning "P2 不可裁剪"硬闸。

## BDD 评审

锚点（`#### BDD-1:` 至 `#### BDD-21:` 共 21 条连续，grep `^#### BDD-` 计数 21，无跳号，
每条单 Given-When-Then；载体=条文 grep 命中/未命中 + pytest 红/绿，无中间态）：

- BDD-1: 成立，可二值判定（P3 卡有无清理钩子锚词）｜数据✓ 前端✗ 多端✗ 边界✓ 兼容✓
- BDD-2: 成立，可二值判定（P4 卡同源锚词，与 BDD-1 无矛盾，同类补齐）｜数据✓ 前端✗ 多端✗ 边界✓ 兼容✓
- BDD-3: 成立，可二值判定（"无条件删除"+"200/204/404"锚词）｜数据✓ 前端✗ 多端✗ 边界✓ 兼容✓
- BDD-4: 成立，可二值判定（P6 卡残留检查步骤锚词）｜数据✓ 前端✗ 多端✗ 边界✓ 兼容✓
- BDD-5: 成立，可二值判定（dispatch-context 模板约束条目位锚词）｜数据✓ 前端✗ 多端✗ 边界✗ 兼容✓
- BDD-6: 成立，可二值判定（断言审计单测存在 + pytest 红绿；次要缺口见打回项 2）｜数据✓ 前端✗ 多端✗ 边界✗ 兼容✓
- BDD-7: 成立，可二值判定（P1 卡"人工体验"+seed 锚词同现）｜数据✓ 前端✓（约束下游） 多端✗ 边界✓ 兼容✓
- BDD-8: 成立，可二值判定（analyst.md 同源锚词，与 BDD-7 无矛盾）｜数据✓ 前端✓（约束下游） 多端✗ 边界✓ 兼容✓
- BDD-9: 成立，可二值判定（BDD 清单含/不含 seed 型 BDD，评审打回口径明确）｜数据✓ 前端✓（约束下游） 多端✗ 边界✓ 兼容✓
- BDD-10: 成立，可二值判定（plan-design-review 含"ui_render_shape"+"形态"锚词；本体现 0 命中，缺口真实）｜数据✓ 前端✓ 多端✗ 边界✓ 兼容✓
- BDD-11: 成立，可二值判定（布局型三组维度名锚词）｜数据✓ 前端✓ 多端✗ 边界✓ 兼容✓
- BDD-12: 成立，可二值判定（渲染正确性/动效时序 + 对接 architect checklist 引用锚点）｜数据✓ 前端✓ 多端✗ 边界✓ 兼容✓
- BDD-13: 成立，可二值判定（"候选"+"权衡"锚词；现 0 命中，缺口真实）｜数据✓ 前端✓ 多端✗ 边界✓ 兼容✓
- BDD-14: 成立，可二值判定（"0-10"+"status"既有锚词保留；本体已确认存在）｜数据✗ 前端✗ 多端✗ 边界✓ 兼容✓
- BDD-15: 成立，可二值判定（缺省回落布局型语义锚词）｜数据✗ 前端✗ 多端✗ 边界✓ 兼容✓
- BDD-16: 成立，可二值判定（"可表达子集"+五类 DOM 度量锚词，明确不收主观视觉；现 0 命中）｜数据✓ 前端✓ 多端✗ 边界✓ 兼容✓
- BDD-17: 成立，可二值判定（architect.md 或 P2 卡"DOM 度量"锚词）｜数据✓ 前端✓ 多端✗ 边界✗ 兼容✓
- BDD-18: 成立，可二值判定（verifier.md 或 P6 卡 DOM 度量证据表述锚词）｜数据✓ 前端✓ 多端✗ 边界✗ 兼容✓
- BDD-19: 成立，可二值判定（tests/README"真实 gate 语义"锚词；"何时更新"节现无该表述，缺口真实）｜数据✓ 前端✗ 多端✗ 边界✗ 兼容✓
- BDD-20: 成立，可二值判定（AGENTS.md"全量扫描"+"新增 CHECK"锚词；"改脚本的工作流"现无该表述，缺口真实）｜数据✓ 前端✗ 多端✗ 边界✗ 兼容✓
- BDD-21: 成立，可二值判定（dispatch-context 模板"拆小"/">5 文件"/"体量"锚词；现 0 命中缺默认指导，dispatch-prompt 行 49 既有硬规则不重复）｜数据✓ 前端✗ 多端✗ 边界✗ 兼容✓

跨条一致性：BDD-1/BDD-2 同源无矛盾；BDD-7/BDD-8 同源无矛盾；BDD-10~15 形态组与 BDD-14
格式保持无矛盾；BDD-9 援引 BDD-7/8 条文无循环。主观词仅见 §8 自检行提及，无 BDD 绑定主观判据。

## 隐含需求覆盖

- 数据维度：覆盖（§2"数据"条：条文锚词 + 断言审计单测为数据载体；BDD-6 回归防线）
- 前端维度：覆盖（§2"前端"条：本任务不产出业务 UI + §3 `domains: [backend]` 排除理由；Phase 2/3 约束下游 frontend 任务）
- 多端维度：覆盖（§2"多端"条：role-system 行 47 + CHECK11 锚点列为连带同步点，P7 捕获）
- 边界维度：覆盖（§2"边界"条：无形态回落默认 / 0-10 语义保持 / 五类 DOM 度量边界；BDD-3 三码语义 + BDD-15 回落）
- 兼容维度：覆盖（§2"兼容"条：SELF-GATE + CHECK14/15 护栏；BDD-14 门槛格式契约保持）
- 遗漏：无（五维逐项有条目编号对应）。

## 裁剪评审

- 跳过阶段：声明"全覆盖、无裁剪"，但 frontmatter `phases: [P1, P3, P4, P5, P6, P7, P8]`
  漏 P2——声明与列表自相矛盾（§3 正文又写"P2 不可裁"），理由不成立，见打回项 1。
- `risk_level: high` 理由充分（≥7 协议文件批量改动 + 评审角色行为变更 + SELF-GATE 触发 + 与 TAG0029/TAG0031 并行 merge；引 TAG0026 high + standard 先例）。
- `ceremony: standard`：未声 thin，无四要素核对义务；fail-closed 缺省亦为 standard，一致。
- `capability_requirements: []` 与"无浏览器/外部系统/视觉能力依赖"一致；`verification_env` 缺省成立（纯 md + pytest/grep，无服务/端口/库依赖）。

## 审声明（风险分级/裁剪声明 vs diff 证据）

- frontmatter 声明 vs §3 正文：risk / ceremony / packages / domains 一致；`phases` 不一致
  （列表漏 P2，§3 写"P2 不可裁"+"全覆盖、无裁剪"）→ 不一致。
- 改动面证据：暂存区仅 `.state.yaml`（1 文件）；工作区新增 `P1-requirements.md`（259 行）+
  两 dispatch-context + progress（未 add，属 P1 产出集）；协议本体改动落在 P4
 （P1/P3/P6 卡 + plan-design-review.md + dispatch-context 模板 + analyst.md +
  tests/README + UPGRADING，SELF-GATE 触发面）→ high / standard 与改动意图匹配。
- `ceremony: standard` → 无 full-P7 核对义务；P7 仍在列（跨包一致性核对，加分项）。
- 按规则"声明与实际不一致时结论必须为 needs-revision 或 rejected（不得 approved）"→ 本结论 needs-revision。

## 二值判定与强制节核对

- §0 含"已核对 P0-brief 时效性，无漂移"三点复核行；§7 同类扫描 10 行判定（#1~#10 含 8a/8b，
  命中数量 + 文件清单 + 逐条处理判定）+ 回归拦截声明（BDD-6 + P7 三包面核对）具备。
- `[NO_NEED_CONFIRM]` 行首具备（§6 区）；无 `[NEED_CONFIRM]`；无 `[CAPABILITY_GAP]`。
- 范围锁定复核具备（§2 末段：不重构形态声明 / 不改 gate 判据 / 不实现清理钩子运行器；
  TAG0029/TAG0031 out-of-scope 保持）。

## P1 纯净性

- Then 均绑定条文存在性/锚词/测试覆盖，未绑定实现函数；§9 标注"非 BDD，供 P2/P4 参考"，
  所列为落笔注意（CHECK11 锚点保持 / v0.68 章节 / self-gate-review / role-system 行 47 同步），
  未写"用哪个函数实现" → 未越界成方案设计。

## 复核结论（fix1 增量复核，2026-09-04）

首轮 BDD-1~21 逐条成立结论保留。本轮只核对打回项闭环：

- 打回项 1（硬阻断）已闭环：frontmatter `phases` 现为 P1~P8 全 8 项（含 P2），
  与 §3"全覆盖、无裁剪 / P2 不可裁"一致，check-pruning P2 硬闸解除。
- 打回项 2（次要）已闭环：BDD-6 Then 含"dispatch-context 模板含 BDD-5 载体锚词
  （模板锚词同锁）"，载体系补模板路径 + 清理/残留/环境还原锚词 grep 断言（行 120）。
- 打回项 3（信息项）确认未动：BDD-16 落点"或"表述保留（P2 视觉 checklist
  或 verifier/P6 指南），由 P2 影响面梳理 pin 定。
- 不变项抽查：`^#### BDD-` 计数 21 连续；正文无行首 `- PASS` / `- FAIL`；
  无裸 `[NEED_CONFIRM]` / `[CAPABILITY_GAP]`（仅 `[NO_NEED_CONFIRM]` 声明行）。
- 本文件 check-frontmatter.py exit 0。

复核结论：approved。锚点：BDD-1~21（首轮逐条成立）+ 五维覆盖（数据/前端/多端/
边界/兼容逐项有条目编号对应）+ phases 全 8 项与 §3 对齐。

## 打回项（analyst 修改清单）

1. （硬阻断）frontmatter `phases` 补 P2 → `[P1, P2, P3, P4, P5, P6, P7, P8]`，
   与 §3"P2 不可裁 / 全覆盖"对齐；否则 check-pruning "P2 不可裁剪"硬闸 P2 门直接 exit 1。
2. （次要）BDD-6 载体补 dispatch-context 模板锚词锁定（否则 BDD-5 条目被删不断言转红），
   或在 BDD-6 Then 加"模板锚词同锁"一句。
3. （次要）BDD-16 落点"或"表述 P1 可保留，由 P2 影响面梳理 pin 定落点文件（P7 核对）。
