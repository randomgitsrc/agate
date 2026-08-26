# 复盘：TAG0019/20/21 三连任务程序 + TAG0022 修复批

> 复盘对象：2026-08-21~23 的「合并后立项 → 编排者会话执行 → 外部独立验证合并」完整程序
> （TAG0019 风险分路由 v0.58.0 / TAG0020 独立 Judge v0.59.0 / TAG0021 结构化层 v0.60.0 /
> TAG0022 确认问题修复批 v0.61.0）。
> 复盘角色：外部观察者（DSH 主会话，承担四轮的独立验证与合并；非执行者）。
> 本文按 agate 复盘模板（RM-AG0020）：正文四节 + 归因分层 + 技术债核对 + agate 反馈节。

---

## frontmatter

```yaml
phase: retrospective
task_id: TAG0019-21
created: 2026-08-23
agent: external-observer
review_status: approved
review_log:
  - { round: 1, verdict: needs-revision, blockers: 2, date: 2026-08-23 }
  - { round: 2, verdict: needs-revision, blockers: 2, date: 2026-08-23 }
  - { round: 3, verdict: needs-revision, blockers: 1, date: 2026-08-23 }
  - { round: 4, verdict: approved, date: 2026-08-23 }
mechanism_issues:
  - "ruff 违规在合并阶段无强制（TAG0019/20 共 35 处带病合并），CI ruff job 非 required check"
  - "judge.enabled 由任务自选，'P6.5 强制所有任务'是软强制（P6 卡纸面 vs 机制实现差距）"
  - "结构化层 M2 迁移边界未在协议文档写清：协议级规则可切 YAML、任务级 P2-design.md 必须留 md——边界不清导致验收锚设定失准"
  - "环境假象测试（basetemp 位置依赖）跨任务反复复现，每任务单独登记 known-failures，无集中治理"
  - "编排者子代理模型路由默认解析落到无配额 provider（opencode-go），需显式 provider/model 覆盖才可用——spawn 不继承主会话路由"
execution_issues:
  - "TAG0019/20 的 P4 实现轮未在合并前自跑 ruff 全量（或 CI ruff 未生效），lint 违规漏到 main"
  - "外部验证者早期将 RM-0038 验收锚定为'check-gate 零 md 解析'过严，未区分协议级 vs 任务级规则"
  - "外部验证者监控'等信号'=失明：GUI 会话完成不推送事件，低频等待变成无探测通道，靠用户转告才收到完成信号"
  - "四轮合并全部手动 gh pr merge + G-5 检查，AGENTS.md 文档化的 git-to-main（~/bin）自动化工具未启用"
  - "四任务 .state.yaml retries 全为 {}：评审拒-修-批（requirements-review 3 轮/plan-eng-review rejected）与 P5→P4 回退（TAG0019/21/22 共 3 次）均未记录进 retries——重试无集中留痕（机制清单暴露）"
feedback_ready: true
```

---

## 一、事实基线

- **程序**：TAG0019（RM-0031 风险分路由）→ TAG0020（RM-0032 独立 Judge）→ TAG0021（RM-0022 结构化层）串行；合并后经全面分析确认 5 个问题，TAG0022 合并处理（RM-0037~0041）
- **规模**：BDD 15/10/16/10；测试 1038 → 1213（count-tests.sh 口径，新增 ≈175 用例）；4 个版本 v0.58.0~v0.61.0，tag 祖先全部验证
- **程序记录缺口**：roadmap 中 RM-AG0032 至今仅 backlog+scheduled 两行、无 done 行（v0.59.0 已发布、PR #184 已合并）——本次复盘与分析均未捕获，列为待补记录
- **执行模式**：编排者会话（GUI 真会话，agate preset）自主执行 P0-P8；外部观察者只做：放行（同步 main 进下一 worktree）、验证（独立全量 pytest/consistency/ruff/structure）、合并（--no-ff + G-5）
- **关键事件**：
  - 编排者 P1/P2 评审真实发生拒-修-批循环（requirements-review 3 轮、plan-eng-review 1 轮 rejected）
  - TAG0021 实战启用了 TAG0020 的 P6.5 judge（16/16 零挑验重验 + 账本哈希链审计）——跨任务 dogfooding 闭环
  - ruff 违规三连：TAG0019 23 处 + TAG0020 12 处带病合并（事后 PR #183 补修）；TAG0021 70 处内部 P5 自抓回修；TAG0022 后 workflow 锁版
  - 编排者子代理模型路由事故：subagent 落到 opencode-go（无配额）三连败，换 workflow + 显式 provider/model 恢复
  - 外部验证者早期监控"等信号=失明"：GUI 会话完成不推送事件，靠用户转告/自查；后改低频磁盘信号

## 二、做得好的 + 可复用模式

1. **三连依赖设计兑现**（回馈 agate）：TAG0020 judge 是 TAG0019 薄化的质量兜底、TAG0021 是 0019/0020 的地基——tag 0021 实战启用 judge 证明依赖链设计有效。去向：agate 反馈节 A1
2. **外部独立验证+合并模式**：执行者（编排者）与验证者（外部观察者）分离，四轮零"gate 判自己"污染；合并前必跑独立全量验证，发现过 1 次执行者未察觉的问题（ruff 35 处带病合并）。去向：agate 反馈节 A2
3. **问题→RM→合并→闭环回路**：TAG0019-21 分析产出 5 个确认问题 → RM-0037~41 → TAG0022 单 task 处理 → 独立验证闭环 → 分析文档追加闭环记录。去向：项目资产沉淀，位置：`dsh-workspace/agate-research/tag0019-21-analysis.md`
4. **编排者会话自主性**：单回合持续 ~90 分钟（903+ 步）自主推进 P0-P4，多次对僵死子代理自行重派（空返回恢复机制实战）
5. **引导式干预纪律**：外部观察者对编排者只发会话内消息引导（如"终止僵死子代理 + 采纳你提出的变通方案"），从不越界改文件——验证了"验证者不代执行"的边界

## 三、发现的问题

1. **ruff 违规带病合并**（TAG0019 23 + TAG0020 12 处，合并后才在 main 实测发现）
   归因层面: 执行错误
   （修复：TAG0022 RM-0037 workflow 锁 ruff==0.16.4 + required check 文档化）
2. **CI ruff job 非 required check**——有 job 但合并阶段不拦（与问题 1 同源）
   归因层面: 机制缺口
3. **judge.enabled 自选软强制**——P6 卡宣称"强制所有任务"，实际 P1 主 Agent 自写 enabled，不写则全链跳过
   归因层面: 机制缺口
4. **M2 迁移边界未文档化**——协议级规则可切 YAML、任务级 P2-design.md 必须留 md；边界未写清导致验收锚设定失准
   归因层面: 机制缺口
   （修复：TAG0022 RM-0038 共享读取器 + S-3 双向收紧；边界记录于 RM-0038/分析文档六）
5. **验证者锚定过严**——外部验证者早期将 RM-0038 验收锚定为"check-gate 零 md 解析"不现实（未区分协议级 vs 任务级规则），后经任务实现修正
   归因层面: 执行错误
6. **环境假象测试反复复现**（test_bdd_7/25 依赖 basetemp 位置），跨任务各 2 次，仅登记 known-failures 无集中治理
   归因层面: 机制缺口
7. **编排者子代理模型路由默认解析失控**——spawn 不继承主会话 agent-default-model，落到无配额 provider
   归因层面: 机制缺口（DSH 侧，非 agate）
8. **监控"等信号"= 失明**——GUI 会话完成不推送事件给观察者，低频等待变成无探测通道
   归因层面: 执行错误（外部验证者的流程设计缺陷）
9. **git-to-main 未启用**——四轮手动合并，AGENTS.md 文档化的 git-to-main（~/bin）自动化流水线脚本闲置
   归因层面: 执行错误
10. **评审重试与回退未记录进 retries**——四任务 .state.yaml retries 全为 `{}`：requirements-review 3 轮、plan-eng-review 1 轮 rejected、P5→P4 回退 3 次（TAG0019 CHECK 9 锚点 / TAG0021 ruff 70 处 / TAG0022 BDD-9）、子代理空返回重派均未集中留痕
   归因层面: 执行错误（机制侧无强制校验，见措施 9）

## 四、改进措施

| # | 措施 | 归因 | 状态 |
|---|------|------|------|
| 1 | ruff 设为 PR required check + workflow 锁版 | 机制缺口 | ✅ workflow 锁版；required check 配置步骤已文档化，**待维护者在 GitHub 设置启用** |
| 2 | judge 新任务强制（fail-closed + 日期截止）| 机制缺口 | ✅ RM-0039（TAG0022）|
| 3 | M2 边界协议文档化（协议级→YAML、任务级→md、S-3 双向）| 机制缺口 | ✅ RM-0038（TAG0022）|
| 4 | 环境假象测试根治（GIT_CEILING + 位置感知）| 机制缺口 | ✅ RM-0041（TAG0022）|
| 5 | M3 实证计划+触发条件（报告留待薄任务）| 机制缺口 | ✅ RM-0040（TAG0022，计划交付）|
| 6 | 子代理模型路由：spawn 默认继承父路由（DSH 侧）| 机制缺口 | ⏳ DSH 侧待评估（记录：dsh-subagent-model-routing.md）|
| 7 | 监控事件通道：GUI 会话完成信号接入观察者 / 低频磁盘探测 | 执行错误 | ⏳ 流程改进 |
| 8 | 合并改用 git-to-main（等 CI→合并→清理 自动化）| 执行错误 | ⏳ 流程改进 |
| 9 | retry 记录纳入 gate 校验（.state.yaml retries 与门槛失败事件——评审 rejected/P5→P4 回退/子代理空返回——对应性校验）| 机制缺口 | ⏳ 建议（问题 10）|

## 机制触发核对清单（模板强制，23 行）

| 机制 | 应该触发？ | 实际触发？ | 未触发后果 | 原因 |
|------|-----------|-----------|-----------|------|
| retry 记录 | 是 | ❌（部分）| 评审拒-修-批/回退/子代理空返回均无集中留痕 | 执行错误：四任务 .state.yaml retries 全为 {}（详见问题 10）|
| PAUSED | 否 | — | — | 无 gate 超限需人工介入 |
| PROD_TOUCHED | 否 | — | — | 未发生意外接触生产环境（P8 写 [PROD_NOT_TOUCHED] 是常规声明，非触发事件）|
| SCOPE+ | 是 | ✅ | — | TAG0022 M15（Windows pytest 修复）经 SCOPE+ 采纳并 [SCOPE_RESOLVED] |
| SCOPE_RESOLVED | 是 | ✅ | — | 同上 |
| DESIGN_GAP | 是 | ✅ | — | TAG0021 3 条 DESIGN_GAP（check-protocol-consistency 锚点等）均已采纳回写 |
| DESIGN_GAP_REVIEWED | 是 | ✅ | — | TAG0021 P7 DESIGN_GAP 配对 9/9 REVIEWED；TAG0022 2/2 |
| NEED_CONFIRM | 否 | — | — | P1 均以 [NO_NEED_CONFIRM] 常规声明关闭，非触发事件 |
| CAPABILITY_GAP | 是 | ✅ | — | TAG0021/22 test_bdd_7 沙箱 basetemp CAPABILITY_GAP 登记 |
| gate 验证（每阶段） | 是 | ✅ | — | 四任务全部阶段 gate 通过（含 P6.5 judge 双脚本）|
| 阶段产出文件（每阶段） | 是 | ✅ | — | P0-P8 产出文件齐全（P3-test-cases/P6-evidence/P8-release 等）|
| .state.yaml phase 同步 | 是 | ✅ | — | phase 随 commit 推进，READY 均落盘 |
| 裁剪条件 + override | 否 | — | — | 四任务 P1 均声明 phases 全保留不裁剪（TAG0019 L12/TAG0020 L11/TAG0021 L13/TAG0022 L13）|
| capability_requirements | 是 | ✅ | — | TAG0021/22 P1 声明 [text-analysis-scanning, protocol-editing] 等并评估 available；TAG0019/20 显式空列表 [] |
| 分阶段落盘（防 subagent 空返回）| 是 | ✅ | — | 各任务 P{N}-progress.md；编排者对空返回子代理重派（TAG0021 test-designer 3 次）|
| phase-产出一致性 | 是 | ✅ | — | pre-commit WARNING 机制生效，无跨 phase 提交 |
| P6 evidence（含截图 + 引用 + vision YAML）| 是 | ✅ | — | P6-evidence 13/19/18 证据文件；非 UI 任务无截图 |
| P2 候选方案 + 权衡（≥2）| 是 | ✅ | — | TAG0019/20/21 各 3 候选；TAG0022 candidate_count=2 |
| P8 internal_only_reason | 否 | — | — | P8 均正常发布，未裁剪 |
| dispatch-context.md | 是 | ✅ | — | 每阶段派发前后置齐全（含 rev 轮）|
| pre-commit hook（gate / 状态转移 / 裁剪）| 是 | ✅ | — | 多次拦截（裁剪格式/self-gate 标记/源码数）|
| CI backstop | 是 | ✅（部分）| **ruff job 未拦截 TAG0019/20 违规合并（非 required/版本未锁，见问题 1-2）**；其余 checks 全绿 | 机制缺口 |
| **技术债登记** | 是 | ✅ | — | RM-AG0037~41 + DEBT0018（见下表）|

## 技术债登记核对清单

| 技术债登记 | 是否 | 去向 |
|-----------|------|------|
| ruff 合并强制 | 是 | RM-AG0037（TAG0022 闭环）|
| M2 迁移边界 | 是 | RM-AG0038（TAG0022 闭环）|
| judge 软强制 | 是 | RM-AG0039（TAG0022 闭环）|
| M3 实证 | 是 | RM-AG0040（TAG0022，计划交付）|
| 环境假象测试 | 是 | RM-AG0041（TAG0022 闭环）|
| check-gate 降级 stub false-PASS | 是 | **DEBT0018**（TAG0022 登记，open）|
| RM-AG0032 记录缺口（无 done 行）| 是 | 待补 roadmap 记录（程序级）|
| 子代理模型路由 | 是（DSH 侧）| 记录于 dsh-subagent-model-routing.md，未入 agate DEBT（非仓库域）|
| 监控事件通道 / git-to-main | 否 | 流程改进，非仓库债；如要入账 → DEBT0019 候选 |

## agate 反馈

- A1：跨任务依赖设计（质量兜底链）有效——建议协议文档显式支持"任务间机制依赖"编排模式
- A2：外部独立验证+合并模式（执行者与验证者分离）显著降低带病合并概率——建议沉淀为 P8 的"外部验证"可选步骤文档
- A3：复盘中的验收锚要区分"协议级可判定规则"（可切 YAML）与"任务级数据"（必须留 md）——边界修正记录于 RM-AG0038 与结构化层协议文档（RM-AG0022 已完成）
