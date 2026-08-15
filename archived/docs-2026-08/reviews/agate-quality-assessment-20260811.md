# agate 质量评估报告（2026-08-11）

> 评估人：主 Agent（orchestrator）
> 评估范围：agate v0.40.2 协议本体（43 脚本 / 5159 行 / 27 文档 / 602 bats / 33 版本）
> 评估方法：客观数据采集（测试/一致性/shellcheck/规模）+ 源码审计（残留正则提取点）+ 架构分析

---

## 0. 一句话结论

**agate 是"流程正确性"做得非常扎实、"内容真实性"只能靠流程间接保证的成熟协议。**
当前处于**质量平台期**：该做的门禁都做了，继续加 gate 边际收益递减；真正的短板是"agent 执行过程可观测性"（P2.34 审计重设计）和"正文正则提取残留"的一致性债。

---

## 1. 质量强项（数据支撑）

| 维度 | 数据 | 判断 |
|------|------|------|
| 一致性 | consistency **0 ERROR**（13 WARNING 均为叙事文件旧引用，无害） | ✅ 协议-脚本结构高度对齐 |
| 静态检查 | shellcheck **0 警告** | ✅ 所有 26 个 sh 脚本无 shell 规范问题 |
| 测试覆盖 | 602 用例 / 52 文件 / **每个 gate 脚本都有对应 bats** | ✅ 覆盖完整 |
| 架构分层 | 17/26 sh 调用 py 工具（v0.34.0 抽离成果，5159 行中 py 占主体逻辑） | ✅ bash 薄壳 + py 逻辑 |
| 门禁体系 | P0-P8 每阶段 gate + pre-commit 三 hook + CI backstop + self-gate | ✅ 多层防护 |
| 版本纪律 | 33 tag，release 一律普通 merge（v0.31.0 事故后固化，`agate-summary` 用 describe 验证） | ✅ 发布流程规范 |
| 结构化演进 | v0.40.0 把 ~40 机器字段迁入 frontmatter + pyyaml 双读 + schema 校验器 | ✅ 方向正确 |

## 2. 质量短板（诚实指出）

### 2.1 语义真实性无硬保证（结构性局限，非 bug）
- gate 只验证"留痕动作做了"（机器可判定），不验证"内容对不对"
- candidate_count 虚报、BDD 答非所问、主 Agent 自批——结构上无法根治（需平台支持独立 git author，Phase 3 已取消，见 LIMITATIONS 局限 3）
- **这是设计边界，不是缺陷**——评估 §5.2 已明确"结构化不解决语义真实性"

### 2.2 测试偏向"格式/存在性"而非"语义"
- 602 用例大多测"脚本行为是否符合协议"，很少测"agent 产出物的质量"
- 这是 gate 脚本测试的正常特征，但意味着协议核心质量（subagent 做得好不好）依赖独立评审，无法自动验证

### 2.3 文档漂移风险仍在
- 13 个 consistency WARNING 全是过时引用（count-tests.sh 附录 A 引用已改名 plan）
- 不阻塞但持续存在

### 2.4 正文正则提取残留（详细见 §3）
- **64 处**正文正则提取点，其中部分"该结构化但漏了"，部分"本就是散文语义不该结构化"

### 2.5 依赖 Python 生态
- pyyaml/Pillow 半必需依赖（本机已装，新环境需 pip install）

---

## 3. 重点：正文正则提取残留审计（64 处分类）

> 用户的关切："我以为 v0.40.0 已把所有正文正则提取改掉，现在发现还有。"——**实测：确实还有 64 处，但需分类看**。

### 3.1 按脚本分布

| 脚本 | 提取点 | 主要字段 |
|------|-------|---------|
| check-gate.sh | 23 | NEED_CONFIRM/SUGGEST/DESIGN_GAP/BLOCKER/DEVIATION/candidate_count/packages/domains/ui_affected/gate_commands/PASS/FAIL |
| agate-extract-context.sh | 19 | P0 task/risks/env + P1 domains/risk/BDD + P2 packages/gate_commands + P6 PASS/FAIL/DESIGN_GAP + P7 BLOCKER/DEVIATION |
| check-p6-provenance.sh | 8 | PASS/FAIL/vision/BDD 等 |
| check-pruning.sh | 7 | override/implicit_coupling/coupling_checklist/internal_only/跳过风险（+risk_level/phases 已走 md-field-get） |
| check-p6-evidence.sh | 3 | PASS/FAIL/截图引用 |
| check-scope-resolved.sh | 1 | SCOPE_RESOLVED |
| check-retrospective.sh | 1 | SCOPE+/override |
| check-changelog.sh | 1 | 版本段落 |
| agate-archive-stale-outputs.sh | 1 | FAIL 行 |

### 3.2 分类：不该结构化（散文语义标记）——合理保留

这些是**语义判断标记**，结构化方案（评估 §5.5）明确保持散文：

- `[NEED_CONFIRM]`/`[SUGGEST:]`/`[NO_NEED_CONFIRM]`（P1 待确认）
- `[DESIGN_GAP]`/`[DESIGN_GAP_REVIEWED]`（P4/P7 偏差声明）
- `[BLOCKER]`/`[DEVIATION]`/`[DEVIATION-CRITICAL]`（P7 严重度）
- `[SCOPE+]`/`[SCOPE_RESOLVED]`/`[PROD_TOUCHED]`（运行时意外发现）
- 权衡/选择理由关键词（语义关键词匹配）
- `- PASS/FAIL` 行（验收证据，格式从严但保留正文）

**这些不该进 frontmatter**——它们是"subagent 运行时发现、写在任意位置的意外"，强行结构化会漏报。

### 3.3 分类：该结构化但"碰巧能用"（一致性债，非 bug）

以下字段**已在 v0.40.0 迁入 frontmatter**，但部分脚本仍用 `grep '^field:'` 读：

| 字段 | 读取方式 | 为什么"碰巧能用" |
|------|---------|-----------------|
| candidate_count | check-gate.sh:141 `grep '^candidate_count:'` | frontmatter 内行首，grep 能匹配 |
| packages/domains/ui_affected | check-gate.sh:173 `grep -c '^(...):'` | 同上 |
| design_trivial/follows_existing_pattern | check-gate.sh:146 | 同上 |
| override/implicit_coupling/coupling_checklist/internal_only/跳过风险 | check-pruning.sh:23-100 | 同上（P7 已 REVIEWED-ACCEPTED） |
| gate_commands | check-gate.sh + extract-context | 同上 |

**实测验证**：`candidate_count: 2` 写在 frontmatter 里是行首，`grep -E '^candidate_count:'` 能匹配到——所以**当前功能正确，没有解析 bug**。

**为什么是"债"而不是"bug"**：
1. 功能正确（frontmatter 行首兼容正则）
2. schema 校验器兜底（类型/枚举/格式错误在 pre-commit 被拦）
3. 只是"同类字段两种读法"的不一致——部分走 md-field-get.py（risk_level/phases），部分走裸 grep

**潜在风险**：若未来 frontmatter 允许嵌套结构（字段非行首），裸 grep 会失效。当前无此风险。

### 3.4 该结构化但**确实漏了**的（真正缺口）

审计发现 **P6/P7 的计数提取仍走正文**（`check-gate.sh:306-308`）：

```bash
TOTAL=$(grep -ciE '^\s*- (PASS|FAIL)\b.*BDD-[0-9]' "$P6_FILE" ...)
FAIL=$(grep -ciE '^\s*- FAIL\b.*BDD-[0-9]' "$P6_FILE" ...)
```

但 v0.40.0 已把 P6 的 `pass`/`fail` **结构化到 frontmatter**（md-field-get.py 有 `pass/fail` frontmatter-only 字段，check-gate.sh:332 附近读 `design_gap_count` 也是 frontmatter）。所以 check-gate.sh:306-308 是**双轨**——frontmatter 有则用之，无则回退正文正则。这与"双读"设计一致，不算 bug。

### 3.5 结论（回答用户关切）

**"是否还有正文正则提取"——有，64 处，但分三类**：
1. **散文语义标记（~30 处）**：合理保留，不该结构化
2. **"碰巧能用"的机器字段（~20 处）**：功能正确，一致性债（check-pruning 6 字段 + check-gate candidate_count 等）
3. **双读回退（~14 处）**：frontmatter 优先 + 正则回退，符合双读设计

**真正值得做的一致性收尾**：把第 2 类（机器字段裸 grep）统一走 `agate-md-field-get.py`——这是"一个入口"的一致性优化，不是 bug 修复。优先级低于 P2.34（审计可观测性）。

---

## 4. 改进杠杆排序（我的判断）

| 优先级 | 项 | 类型 | 理由 |
|--------|----|------|------|
| **高** | P2.34 审计/可观测性重设计 | 设计 | orchestrator-log 8% 合规率、subagent 中断恢复靠主观——当前最弱的一环 |
| **中** | 第 2 类正则残留统一走 md-field-get | 一致性 | 消除"同类字段两种读法"，成本低（~20 处），但非 bug |
| 低 | P2.66 并行环境隔离 | 设计 | 已有按包并行，只缺 debug server 生命周期规范 |
| 低 | P2.35 重试预算分离 | 设计 | 格式 vs 功能 retry 分离 |

## 5. 附录：质量信号汇总

| 指标 | 值 |
|------|-----|
| 脚本数 | 43（26 sh + 17 py） |
| 脚本总行数 | 5159 |
| 协议文档 | 27 |
| 测试用例 | 602（52 文件） |
| 版本数 | 33 tag / 658 commit |
| consistency | 0 ERROR（13 WARNING） |
| shellcheck | 0 警告 |
| 近 10 版本 fix commit | 占比约 3/主要改动 |
| pyyaml/Pillow | 已装（半必需） |
