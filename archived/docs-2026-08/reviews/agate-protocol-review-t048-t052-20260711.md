---
review_date: 2026-07-11
reviewer: protocol-alignment-review
review_target: agate 协议 v0.11.0（基于 T048–T052 五任务连续执行的实证分析）
status: needs-revision
verdict_counts:
  confirmed: 3
  new_finding: 3
  needs_revision: 3
  deferred: 2
---

# agate 协议实证评审（T048–T052 系列）

> 数据来源：5 个任务、85 commits、约 3.5 天连续执行、154 sessions / 6612 messages。
> 本评审从项目复盘中提取**对 agate 协议本身**的通用问题，剥离项目特有细节。
> 评审维度：协议规则有效性 / gate 信噪比 / 主 Agent 行为约束 / 流程成本

---

## 审查结论汇总

| # | 发现 | 结论 | 优先级 |
|---|------|------|--------|
| F1 | provenance 审计信噪比失衡：格式拦截 13 次、功能拦截 0 次 | 🔴 confirmed | 高 |
| F2 | P6 阶段主 Agent 越俎代庖（亲自写验收/验证而非派 subagent） | 🔴 new_finding | 高 |
| F3 | gate 脚本格式约束过紧（正则匹配字符串而非语义） | confirmed | 中 |
| F4 | dispatch-context 时序约束缺失 | confirmed | 中 |
| F5 | subagent "假完成"无防护 | confirmed | 中 |
| F6 | P6 验收环境与生产环境 gap 无协议层约束 | new_finding | 中 |
| F7 | 发布后回归无检查环节 | new_finding | 中 |
| F8 | 任务拆解颗粒度无指导 | needs_revision | 低 |
| F9 | 长会话上下文丢失后协议规则被遗忘 | deferred | — |
| F10 | 不同角色用同模型无专业化 | deferred | — |

> **F1 与 F2 的因果链**：provenance 审计反复拦截格式问题（F1）→ verifier 产出反复被打回 → 主 Agent 判断"重派 verifier 调格式比自己写更慢" → 亲自代写验收报告（F2）。F2 的直接原因是主 Agent 纪律不足，但 F1 的摩擦放大了越俎代庖的诱惑。两个问题应联动解决。

---

## 1. Provenance 审计信噪比失衡（F1）

### 1.1 实证数据

> 注：以下拦截计数来自项目执行观察，非受控实验。provenance 审计的拦截对象是产出格式而非功能，因此"零功能拦截"是设计预期的结果——但 exit 1 的强制力与"只查格式"的实际能力不匹配，才是问题所在。

| 任务 | provenance 拦截次数 | 其中功能缺陷 | 其中格式/合规问题 | 格式调整耗时 |
|------|-------------------|------------|----------------|------------|
| T048 | 4 | 0 | 4 | ~10min |
| T049 | 3 | 0 | 3 | ~15min |
| T050 | 0 | 0 | 0 | 0 |
| T051 | 2 | 0 | 2 | ~10min |
| T052 | 4 | 0 | 4 | ~30min |

5 个任务、13 次拦截，**零功能缺陷被 provenance 审计发现**。每次拦截增加 10-30 分钟格式调整时间，累计约 65 分钟。

### 1.2 根因：审计目标与强制力等级错配

provenance 审计的四道检查按目标可分为两类：

**A. 证据存在性检查（防造假，与局限 3 直接相关）**：
- 审计 1a：PASS 引用的证据文件必须存在
- 审计 1b：证据目录非空
- 审计 1c：证据文件必须被 PASS 行引用（防充数）

**B. 格式合规性检查（防格式偏差，与局限 3 间接相关）**：
- 审计 2：dispatch-context 不含验收结论预判
- 审计 3：BDD 总数对照（P6 结果数 ≥ P1 Given 行数）
- 审计 4：vision YAML 引用 + blocker_count

A 类检查的 exit 1 是合理的——它们验证"证据客观存在"，这是局限 3 缓解措施的核心（提高造假成本 + 留痕审计）。B 类检查的 exit 1 不合理——它们验证的是"格式是否符合脚本期望"，格式偏差不等于功能缺陷，也不等于造假。

### 1.3 建议

**B 类审计降级为 WARNING（exit 2）**，A 类保留 exit 1：

| 审计 | 当前 | 建议 | 理由 |
|------|------|------|------|
| 1a 证据文件存在性 | exit 1 | **exit 1** | 证据存在性是局限 3 核心缓解 |
| 1b 证据目录非空 | exit 1 | **exit 1** | 同上（空目录 = 无证据） |
| 1c 证据文件被引用 | exit 1 | **exit 1** | 防充数，与 1a 配套 |
| 2 dispatch-context 预判 | exit 1 | **exit 2** | 格式约束，非造假防护 |
| 3 BDD 总数对照 | exit 1 | **exit 2** | 格式约束；P1 BDD 格式非标准时已退化为 WARNING |
| 4 vision YAML 引用 | exit 1 | **exit 2** | 格式约束；vision YAML 产出格式与 gate 期望的对齐是独立问题 |

降级后 provenance 仍作为 WARNING 输出审计留痕，但不阻塞 commit。功能正确性由 P6 gate（FAIL=0 + 证据目录非空）和 P5 gate（测试全绿）保证。

---

## 2. P6 阶段主 Agent 越俎代庖（F2）

### 2.1 实证

| 任务 | P6 违规行为 | 后果 |
|------|-----------|------|
| T048 | 主 Agent 撰写 P6-acceptance.md | 内容格式由主 Agent 而非角色规范决定 |
| T052 | 主 Agent 亲自写 CDP 验证脚本（P5） | 违反"主 Agent 不做第五件事" |
| T052 | 主 Agent 代写 P6-acceptance.md | 用户要求重做后才派 verifier |

这不是偶发行为——**涉及 P6 的任务中主 Agent 都出现了亲自上手**。模式一致：verifier 产出不理想 → 主 Agent 不重派 → 亲自写。

### 2.2 根因

1. **verifier 产出质量波动大**：verifier 返回的 P6-acceptance.md 格式与 gate 期望不一致，主 Agent 宁可自己写也不愿反复重派
2. **重派成本感知过高**：每次派 verifier 需要 5-15 分钟，格式调 3-4 轮 = 30-60 分钟，主 Agent 判断"自己写更快"
3. **协议无"禁止代写"的硬约束**：agate 的"主 Agent 不做第五件事"是指导原则（L0），不是硬拦截（L3）。P6 阶段没有类似 P2 的 `agent=main` 检查

根因 1 和 2 与 F1 直接相关：provenance 审计反复拦截格式问题 → verifier 产出反复被打回 → 主 Agent 判断重派不如自己写。**F1 的降级会减少 P6 的格式摩擦，间接缓解 F2**。

### 2.3 与 P2 评审的对比

P2 评审已有 `agent=main` 硬拦截（`check-gate.sh` L53-56）：P2-review.md 的 agent=main → exit 1。但 P6-acceptance.md 没有同等检查。

P2 和 P6 的 self-authored 风险是对称的：
- P2：主 Agent 自己批准设计评审 → 可能放过设计缺陷
- P6：主 Agent 自己写验收报告 → 可能放过实现缺陷

两者都是"作者和裁判同一人"的局限 3 场景，应受同等约束。

### 2.4 建议

**P6-acceptance.md 增加 `agent=main` 硬拦截**，与 P2-review.md 对等：

- `check-gate.sh` P6 分支增加：P6-acceptance.md 的 agent 字段 = main → exit 1
- 已知局限（与 P2 同）：主 Agent 可伪造 agent 字段。但抬高"随手代写"成本是值得的——P2 的 agent=main 检查在 T048 后确实减少了 P2 自批行为

**P5 阶段**：P5-test-results/ 的产出也应由 verifier subagent 产出。可在 `check-gate.sh` P5 分支增加 agent 字段检查——这与 P5 gate 的 exit 2（需主 Agent 自判）不冲突，agent 字段检查是独立的产出者身份校验。

---

## 3. Gate 脚本格式约束过紧（F3）

### 3.1 已修复项

T048 复盘后部分问题已修复：
- P7 BLOCKER 正则：已排除 `[BLOCKER]: 0 条` 声明行（`check-gate.sh` L112）
- P2 权衡关键词：已扩展为 `权衡|选择理由|取舍|考量|trade-?off|理由与权衡`（`check-gate.sh` L64）

### 3.2 未修复项

P2 候选方案正则 `方案\s*[ABC123abc一二三四五]` 对非单字母命名不友好：`方案 Alpha`、`方案 一（推荐）` 等常见写法不匹配。正则只认单字符后缀，不认多词方案名。

### 3.3 建议

gate 脚本应将 markdown 标题视为**语义**而非**字符串字面量**。统一原则：**gate 检查"有没有"，不检查"格式对不对"**。格式由 CI lint 管。

- 候选方案：`候选方案|方案\s*[A-Za-z一二三四五]|Alternative|Option` 任一即可
- 其他 gate 正则同理审查：凡是"关键词精确匹配"的，改为"语义关键词集合匹配"

---

## 4. dispatch-context 时序约束缺失（F4）

### 4.1 问题

T048 复盘 §10.1 已指出：dispatch-context.md 在 P2 干完活后才写（事后补写），hash 校验形同虚设。当前协议和 hook 只校验 hash 一致性，不校验时序（先写再派 vs 事后补写）。

### 4.2 当前状态

`pre-commit-gate.sh` 的 dispatch-context hash 校验（2p 段）只检查"嵌入卡片 = CLI 输出"，不检查"何时创建"。事后补写当然能通过校验。

### 4.3 建议

此问题属于 LIMITATIONS.md 局限 3 的"自报数据同源"无解类——主 Agent 写的文件内容和创建时间都由主 Agent 控制，无法从内部约束时序。

**务实做法**：
- 在 `dispatch-protocol.md` 中**显式声明**：dispatch-context.md 应在派发前创建，事后补写违反协议意图
- hook 层无法强制时序，但协议文本的显式声明比隐含期望更有效——主 Agent 遵循显式规则的概率高于隐含规则
- 不投入 hook 级时序检查（成本高、可绕过、收益低）

---

## 5. Subagent "假完成"无防护（F5）

### 5.1 实证

T048 中 verifier 报告"已修复 dot-in-username 问题"但文件未变，重复派发 2 次才生效。verify_ui.ts 重写后仍为空操作。

### 5.2 当前状态

verifier.md 已有"分阶段落盘"机制（L146），但实测中 progress.md 经常为空（T048–T052 所有任务的 subagent progress.md 都未有效写入）。规则存在但执行率低。

### 5.3 建议

两层防护：

1. **subagent 侧（honor-system，但可脚本化验证）**：派发 prompt 要求 subagent 返回前 `grep` 确认改动落盘。执行率低的问题不能靠"更强调"解决——应在派发 prompt 末尾加固定校验指令："返回前执行 `grep -c '关键改动' 文件路径`，输出非 0 才返回成功"。主 Agent 可在 prompt 中指定期望的 grep 模式

2. **主 Agent 侧（外部可观测）**：主 Agent 收到"已修复/已实现"报告后，**自己 grep 文件系统确认改动存在**。这是 D2 方案（review-20260708-0903.md 评为"本轮质量最高"），但尚未在协议中落地。建议在 `dispatch-protocol.md` 的主 Agent 行为规范中增加：收到 subagent "已修复/已实现"报告后，必须对声称修改的文件做内容校验（grep 关键行或 diff），未改则重派

---

## 6. P6 验收环境与生产环境 gap（F6）

### 6.1 问题

5 个任务中 2 个发布后立即发现视觉/行为问题，根因是 P6 验收环境与生产环境不一致——验收环境缺少生产环境的某些维度（认证态、主题变体、真实数据量等）。

### 6.2 通用化

这不是特定项目问题——任何有 UI 层或认证层的项目都会遇到"验收环境 ≠ 生产环境"。agate 协议当前对 P6 验收环境无任何约束。

### 6.3 建议

在 `verifier.md` 中增加 P6 验收环境规范：

- **P0-brief 新增字段**：`verification_env` — 列出验收环境与生产环境的已知差异（如"无认证"、"仅 dark mode"、"mock 数据"）。主 Agent 在 P6 派发时将此信息传给 verifier
- **原则**：verifier 必须在 P0-brief 声明的验收环境维度内验证。未覆盖的维度标 `[NEED_CONFIRM]`，由用户最终确认
- **ui_affected = true 的任务**：`verification_env` 应至少声明主题和 viewport 覆盖范围

这些是**协议层指导**（L0），不是硬拦截——验收环境配置因项目而异，无法写成通用脚本。但 `verification_env` 字段让"环境 gap"从隐含变为显式，主 Agent 和 verifier 不再靠猜测判断"该测什么环境"。

---

## 7. 发布后回归无检查环节（F7）

### 7.1 问题

T052 v0.6.1 发布后用户立即发现 2 个问题 → 追溯 v0.6.2。P8-release.md 的 READY checklist 缺少"发布后验证"环节。

### 7.2 建议

在 P8-release.md 模板（`assets/templates/`）的 READY checklist 中增加：

- 版本 bump 后重跑 P5 gate（已有，但经常被跳过——应在 checklist 中显式列出）
- UI 任务：至少在 P0-brief `verification_env` 声明的环境维度内做截图验证
- 发布后用户报告窗口：P8 完成后不立即开始下一任务，留出用户验证时间

这是**流程建议**（L0），不是协议硬约束。但 P8 模板的 checklist 是"提醒主 Agent 不要遗漏"的有效手段——T052 的问题不是 gate 没检查，是 P8 checklist 没提醒检查。

---

## 8. 任务拆解颗粒度（F8）

### 8.1 问题

跨功能域的任务（前端 + 后端 + 配置同时改）执行时间长、发布后问题多。单一功能域的归零修复任务执行时间短、零发布后问题。

### 8.2 建议

在 `WORKFLOW.md` 或 `dispatch-protocol.md` 中增加任务拆分指导：

- **任务范围应以单一用户可观察行为为界**：如"添加 entry 归档功能"（含后端 API + 前端 UI）是一个行为，可以是一个任务；"添加 entry 归档 + 修改图表清洗规则"是两个行为，应拆为两个任务
- **归零修复单独成任务**：发布后修复不混入新功能开发
- **UI 重构单独成任务**：纯视觉/交互变更与逻辑变更分离

这是**指导性建议**（L0），不强制——任务拆分是 P0 阶段的主 Agent 判断，无法脚本化。

---

## 9. 已确认有效的协议机制

| 机制 | 实证 | 评价 |
|------|------|------|
| P0-brief 风险/约束前置 | T048–T052 全部使用 | 有效——减少范围 creep |
| P2 多候选方案 + 评审 | T051 评审通过顺畅 | 有效——减少方向错误；评审轮次过多时成本高 |
| P5 gate 重跑 | T051→T052 测试一直绿 | 有效——防止回归 |
| 子 Agent 专业化分工 | T051 P4 后端/前端并行派发 | 有效——比串行快 |
| .state.yaml 一致性检查 | T052 P4 产出已 commit 但 phase=P3 → gate warning 正确捕获 | 有效 |
| P2 agent=main 硬拦截 | T048 后 P2 自批行为减少 | 有效——应扩展到 P6 |
| BDD 总数对照（provenance 审计 3） | 拦截了 P6 结果数 < P1 BDD 数 | 有效——但应降级为 WARNING |

---

## 10. 优先级排序

### 立即执行（影响大、成本低）

| # | 建议 | 针对问题 | 具体做法 |
|---|------|---------|---------|
| 1 | provenance B 类审计降级 WARNING | F1 | `check-p6-provenance.sh` 审计 2/3/4 改 exit 2；审计 1（1a/1b/1c）保留 exit 1 |
| 2 | P6-acceptance.md agent=main 硬拦截 | F2 | `check-gate.sh` P6 分支增加 agent 字段检查，与 P2 对等 |
| 3 | 主 Agent 收到"已修复"后做文件校验 | F5 | `dispatch-protocol.md` 主 Agent 行为规范增加校验步骤 |

### 短期改进（1-2 周）

| # | 建议 | 针对问题 |
|---|------|---------|
| 4 | P0-brief 新增 `verification_env` 字段 | F6 |
| 5 | P8 发布后验证 checklist | F7 |
| 6 | dispatch-context 时序显式声明 | F4 |
| 7 | gate 正则语义化放宽 | F3 |

### 中期（1-3 个月）

| # | 建议 | 针对问题 |
|---|------|---------|
| 8 | 任务拆分指导 | F8 |
| 9 | P6 验收语义化（结构化数据替代 grep PASS） | F1 长期方案 |
| 10 | 执行角色与 Skill 统一 | F10 |

### Defer

| # | 建议 | 理由 |
|---|------|------|
| F9 | 长会话上下文丢失 | 需平台支持，协议层只能靠落盘缓解（已有 progress.md 机制） |
| F10 | 不同角色用不同模型 | 需多模型路由支持，超出 agate 协议范围 |

---

## 附：与已有评审的交叉引用

| 本评审发现 | 已有评审对应 | 关系 |
|-----------|------------|------|
| F1 provenance 信噪比失衡 | review-20260708-0903.md §E2 | E2 指出"自报字段可绕过"，本评审补充量化数据：13 次拦截零功能缺陷。两者都指向"provenance 的强制力与实际能力不匹配" |
| F2 P6 主 Agent 代写 | review-20260708-0903.md §E2 | E2 已为 P2 实现 agent=main 硬拦截，本评审建议扩展到 P6 |
| F4 dispatch-context 时序 | review-20260708-0903.md §B | B 被评为 needs-revision（scope 错配），本评审同意 B 的核心问题（事后补写）属 defer 类 |
| F5 subagent 假完成 | review-20260708-0903.md §D | D2（主 Agent grep 校验）被评为本轮质量最高，本评审建议落地到 dispatch-protocol.md |
| F3 gate 格式约束 | t048-retrospective-20260707.md §5.1 | 部分已修复（P7 BLOCKER、P2 权衡关键词），P2 候选方案正则仍待放宽 |

---

*评审依据：T048–T052 系列 85 commits、154 sessions、6612 messages 的实证数据 + agate v0.11.0 协议源码 + 已有评审文档。*
*评审日期：2026-07-11*
