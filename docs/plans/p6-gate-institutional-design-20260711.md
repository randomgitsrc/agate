---
task_id: p6-gate-institutional-design
agent: main
date: 2026-07-11
status: 方案 v3（v2+CSO评审：①效果段区分排版/安全两维度；④短期安全收益标零；"不做的事"补1a内容校验）
来源: docs/reviews/agate-protocol-review-t048-t052-20260711.md + docs/reviews/review-20260711-1921.md
---

# P6 Gate 制度设计：从军备竞赛到激励对齐

> 总原则（R8）：**先疏后堵**。造假不是因为"没有出口"，而是正规出口（重试/回退/PAUSED）被误用或贴了负标签，造假在性价比上插了队。解法是修出口的语义和排序（让正路更快、失败免责、红灯指向溯源），最后才拿走作弊工具。

## 诚实标注

本方案是**结构性修复**，不是增量加固。它修正了此前所有"加检查/降门禁"方案的同一盲区：producer=judge=editor 同体时，纯检测是输家的军备竞赛——agent 能满足的任何 bar 都不可信，加更多检查只告诉造假者该造什么。

但本方案也有边界：
- ①②③（激励层）依赖主 Agent 遵循协议文本——是 L0 指导，非 L3 硬拦截。效果取决于"语义翻转"对 LLM 行为的实际影响，这需要实证验证
- ④（结构层）对测试类证据是强解，对 UI 类证据受限于项目是否有 CI e2e 流水线——agate 栈无关，不能假设
- R8.4·补 的设计张力（大跳回退=立即 PAUSED vs 强制逐步退+触底才停）留为开放问题，需作者定夺

---

## 方案总览

| 部件 | 改什么 | 层次 | 对象 | 优先级 |
|------|--------|------|------|--------|
| ① | 疏通 honest path：自动格式化断掉"自己写更快"的算计 | 激励 | 让绝大多数 agent 不想造假 | 🔴 |
| ② | 给 PAUSED 出口贴对标签：责任绑流程不绑绿灯 | 激励 | 同上 | 🔴 |
| ③ | 红 gate 默认逐步溯源退回，而非原地重试 | 激励 | 同上 | 🟠 |
| ④ | P6 证据由 CI 执行生成、agent 只引用 | 结构 | 给极少数铁头兜底 | 🟡 |
| ⑤ | F5 subagent 假完成：主 Agent 文件校验 | 结构 | 兜底 | 🟡 |
| ⑥ | F3 gate 正则语义化放宽 | 卫生 | 减少格式摩擦 | 🟡 |
| ⑦ | F6/F7 验收环境/发布 checklist（仅 ui_affected 时） | 卫生 | 减少漏测 | 🟢 |

**顺序不可反**：①②③ 先疏、④⑤ 后堵。光有 ④⑤ 没 ①②③ = 继续军备竞赛；光有 ①②③ 没 ④⑤ = 挡不住铁头。

---

## ① 疏通 honest path：P6 自动格式化

### 问题

P6 格式摩擦的根因不是"格式没规定"（verifier.md L87-128 已有详尽规范），而是"规定了但生成时不被机器强制、gate 事后才拦"——verifier 产出后、gate 拦截前，中间的往返就是 65 分钟摩擦的来源。

### 方案

新增 `scripts/check-p6-format.sh --fix`（pre-gate 规范化器）：

**自动归一化的范围（只碰无歧义形状，绝不触语义）**：

| 归一化项 | 示例 | 性质 | 歧义性 |
|---------|------|------|--------|
| PASS/FAIL 行首大小写 | `pass B01` → `- PASS B01` | 形状 | 无歧义 |
| 行首空白标准化 | `  - PASS` → `- PASS` | 形状 | 无歧义 |

**不做 auto-fix 的范围（有歧义或触语义，留给 gate）**：

| 不碰项 | 理由 |
|--------|------|
| 裸路径补括号（`b01.png` → `(b01.png)`） | 需判断"这个 token 是证据路径"——描述文本里也可能出现文件名，"哪个 token 是路径"是语义判断 |
| 裸 vision 引用补括号 | 同上 |
| 凭空补出缺失的证据引用 | 需判断"该引用哪个文件"，是语义判断 |
| 补上缺失的 PASS/FAIL 行 | 需判断"该跑哪个 BDD"，是语义判断 |
| 修改 PASS/FAIL 判定 | 需判断"结果对不对"，是语义判断 |
| 补上缺失的 vision YAML 引用 | 需判断"该引用哪个 YAML"，是语义判断 |

裸路径缺括号的情况由 gate 的 provenance 审计 1a 检查（引用格式不对 → exit 1 或 WARNING），不由 auto-fix 猜着包。

### 执行位置

verifier subagent 返回后、主 Agent 运行 gate 前，主 Agent 调：

```bash
bash $AGATE_ROOT/scripts/check-p6-format.sh --fix "$TASK_DIR/P6-acceptance.md"
```

### 效果

- 排版摩擦大幅下降（行首大小写/空白等无歧义形状偏差在 verifier 产出后自动修复，无往返）
- 伪造防御：零增量（provenance 审计能力不变，1a 仍只验存在性不验内容——这是已知局限，非本方案引入）
- 四道 provenance 审计**全部保留 exit 1**（门牙不动）
- 只有真问题（证据文件真不存在、真漏跑场景、真有 blocker、引用真缺失）才 exit 1——这些本就该阻塞
- ① 的价值在排版维度：排版摩擦降 + 防御零削弱。在安全维度：防御零增量。两个维度独立，不可混称

### 边界

`--fix` 覆盖不到的边角格式摩擦仍可能存在。对**那一小部分**单独评估降级——但先自动化、后降级，而非一刀切降级。

### bats 测试

- `unit/check-p6-format.bats`：
  - `--fix` 模式：行首大小写和空白偏差自动修正，exit 0
  - `--check` 模式（默认）：上述偏差 exit 1 + 输出差异描述
  - 裸路径缺括号：**不修复**（语义判断），由 gate provenance 审计 1a 处理
  - 语义内容（PASS/FAIL 判定、证据引用指向）不被 `--fix` 改动
  - 无 P6-acceptance.md 时 exit 0（不阻塞非 P6 阶段）

---

## ② 给 PAUSED 出口贴对标签

### 问题

PAUSED 出口本就存在（state-machine.md），但被当成"认输"而非"正确"。agent 倾向于凿墙（造假过关）而不愿走一扇挂着"失败者走这里"牌子的门。

### 方案

**纯协议文本改动**，零脚本成本。在以下文件中翻转 PAUSED 的语义定义：

### 修改清单

**1. `WORKFLOW.md`** — 在 PAUSED 定义处增加语义声明段落：

> **PAUSED 不是失败，是正确路由。**
>
> agent 的责任是"走对流程"，不是"让 gate 变绿"。派了真 subagent、跑了真验证、gate 仍不过——这不是你的失败，红灯是工作/设计的问题，不是你没本事顶过去。伪造证据让它变绿，才是唯一的失败。
>
> 走正规途径仍不过 → PAUSED/问人类 = 正确行为、零追责
> 伪造证据过关 = 唯一失败
>
> ⚠️ 这是 L0 指导（协议文本语义翻转），非 L3 硬拦截。效果取决于语义翻转对 LLM 行为的实际影响，需实证验证。但它零脚本成本，且与 ①③ 协同——当 honest path 被疏通（①）且红灯正确路由（③）时，PAUSED 的语义翻转才有物质基础。

**2. `state-machine.md`** — 在每个 `→ PAUSED` 转移规则旁加注释：

现有格式如：
```
P6 --[retry>=MAX]--> PAUSED
```

改为：
```
P6 --[retry>=MAX]--> PAUSED（正确路由：上游问题需人工介入，非 agent 失败）
```

对全部 PAUSED 转移统一加注（P1/P2/P3/P4/P5/P6/P7 的 retry 超限 + NEED_CONFIRM + PROD_TOUCHED）。

**3. `dispatch-protocol.md`** — 在主 Agent 行为规范中增加：

> **红灯处理优先级**：
> 1. 诊断：本步抖动还是上游输入问题？
> 2. 本步抖动 → 重试一次（仅一次，避免在被污染的输入上打转）
> 3. 上游问题 → 退回源头那一步（见 ③ 逐步溯源）
> 4. 退到 P0 仍无解 / 外部阻塞 → PAUSED 问人类（正确路由，非认输）

**4. `phase-cards/` 各阶段卡片** — 在"gate 不通过"处理段增加：

> gate 不过 ≠ 你失败了。红灯指向工作/设计的问题，不指向你。正确动作是诊断→退回/重试/PAUSED，不是修改产出让它变绿。

### bats 测试

无新增脚本态，无需新增 bats。但 `check-protocol-consistency.py` 的 CHECK 9 锚点表需更新：新增关键词 `PAUSED 不是失败` / `正确路由` / `责任绑流程不绑绿灯` 在 WORKFLOW.md / dispatch-protocol.md 中存在。

---

## ③ 红 gate 默认逐步溯源退回

### 问题

当前红灯的默认响应是原地重试。但"这步反复不过"的根子常在上游——原地重试在被污染的输入上打转，必然失败。重试上限被感知成"倒计时"，催生"赶紧想办法过"= 凿墙。

### 方案

**L0 指导 + 纯协议文本改动**，不改变 state-machine.md 的转移规则和 check-state-transition.sh 的脚本逻辑。改变的是主 Agent 面对红灯时的决策偏好——从"原地重试"改为"先诊断再路由"。

⚠️ **关键约束**：`check-state-transition.sh` 对回退 diff≥2 强制 PAUSED。因此"逐步溯源"是**字面意义的一次退一阶**（P6→P5→P4→…），不是直接跳到诊断出的源头。直接跳 ≥2 阶段（如 P6→P2）在当前脚本下会触发 PAUSED——这正是 T019 教训的设计：大跳是"问题严重"的强信号。若 agent 确信源头在 2+ 阶之外，PAUSED 问人类是正确路由。

| 诊断结果 | 正确动作 | 错误动作 |
|---------|---------|---------|
| 本步抖动（方向对、只是没做好） | 重试一次（仅一次） | 反复重试直到 MAX |
| 上游输入问题（P4 实现没对齐 P2 设计） | 逐步退回：P6→P5→P4，修好后从 P4 往下走 | 在 P6 原地重试；直接跳到 P4（diff≥2 被拦→PAUSED，不是错误而是安全网） |
| 上游设计问题（P2 方案本身有洞） | 逐步退回：P6→P5→P4→P3→P2，修好后从 P2 往下走 | 直接跳到 P2（diff≥4 被拦→PAUSED）；在 P6 原地重试 |
| 外部阻塞（缺凭据/服务挂/需求歧义） | 立即 PAUSED 问人类 | 退回 P0 再重走 |

### 实证核查：agate 已内置单步回退

`check-state-transition.sh` 检查 1：`diff = old_num - new_num`，diff≥2 → 强制 PAUSED。

| 回退路径 | 真实 diff | 真实结果 |
|---------|----------|---------|
| P5→P4、P4→P3、P3→P2、P2→P1 | 1 | ✅ 放行 |
| **P6→P5** | 1 | ✅ 放行 |
| **P6→P4** | **2** | **❌ 强制 PAUSED** |
| **P6→P2** | **4** | **❌ 强制 PAUSED** |
| P6→P1 | 5 | ❌ 强制 PAUSED |

即"逐步溯源"的可行路径是**一次退一阶**（P6→P5→P4→…），每步 diff=1 均放行。直接跳到源头（≥2 阶差）会被脚本拦为 PAUSED——这不是 bug，是 T019 教训的设计意图。回退时 retry 计数不清零（T016 教训），使溯源自然消耗预算、逐步逼近 PAUSED——机制自带收敛。

### 问人类的两类触发

| 类型 | 判据 | 动作 | 门槛 |
|------|------|------|------|
| 内部缺陷类 | "缺的东西，是我回去重做上游能产出的" | 逐步溯源退回，P0 是"地板"非"必到站" | 高——退到 P0 仍无解才问 |
| 外部/不可逆类 | "缺的东西，只有人类/外部才握着" | 立即 PAUSED 问人类 | 低——识别出即问 |

外部类的三种具体场景：
1. 需求本身歧义/矛盾（源头是人类意图）
2. 不可逆/高风险操作（NEED_CONFIRM——state-machine.md:82 已实现"任意阶段 NEED_CONFIRM → PAUSED"）
3. 外部阻塞（缺凭据、服务挂）

### 修改清单

**1. `dispatch-protocol.md`** — 增加逐步溯源决策表 + 问人类两类触发

**2. `state-machine.md`** — 在回退转移规则旁增加溯源注释：

```
P6 --[任何 BDD 标 FAIL && retry<MAX]--> P4 (retry+1)
  （溯源优先：先诊断"本步抖动还是上游输入问题"
   本步抖动 → 重试一次；上游问题 → 退回源头那步修好再往下走
   退回时 retry 计数不清零，溯源自然消耗预算）
```

**3. `phase-cards/` 各阶段卡片** — 在"gate 不通过"段增加溯源指引

### R8.4·补 设计张力（已决定）

| 现状 | 上一轮评审倾向 |
|------|--------------|
| 大跳回退（≥2 阶段）→ 立即 PAUSED | 大跳回退 → 强制逐步退（P6→P4→P2→…）+ 触底才 PAUSED |

**决定：选方案 A（顺代码，不改脚本）**。理由：

1. 改 `check-state-transition.sh` 放宽 diff≥2 拦截需谨慎论证为何 T019 的教训可以放宽——当前无此论证
2. 逐步一阶退回（P6→P5→P4→…）虽略笨但安全：每步都重新验证，不会跳过中间阶段的问题
3. 若 agent 在逐步退回过程中发现中间阶段无问题（P5 过→P4 问题），自然在 P4 停住——无需直接跳
4. diff≥2 → PAUSED 的安全网保留：若 agent 尝试大跳，PAUSED 问人类仍是正确路由

---

## ④ P6 证据由 CI 执行生成、agent 只引用

### 问题

当前 P6 证据由 agent 自己提交（写 P6-evidence/ 文件）。producer=judge=editor 同体时，agent 可以伪造证据。provenance 审计只查"在不在/被没被引用"，不查真伪。

### 方案

**长期目标**：P6 证据由 CI 从真实代码跑出，agent 只能引用 CI 产出物，不能自带。它没法"改证据"，因为证据不是它写的。

### 可行性分层

| 证据类型 | CI 生成可行性 | 方案 |
|---------|-------------|------|
| 测试类（pytest/bats 结果） | ✅ 天然可行 | CI 跑测试 → 产出结果文件 → agent 在 P6-acceptance.md 引用 CI 产出路径 |
| UI 类（截图 + vision YAML） | ⚠️ 依赖项目有 e2e/截图流水线 | 有流水线 → 同上；无流水线 → 退化为"尽量锚 + 明标残余风险" |

**agate 栈无关，不能假设 CI 有 e2e 流水线**。所以 ④ 对测试类证据是强解，对 UI 类证据是条件解。

### 落地路径

1. **短期（本方案）**：在 `verifier.md` 和 `dispatch-protocol.md` 中增加可操作指令——P6 派发 verifier 时，若项目有 CI 流水线，优先要求 verifier 引用 CI 产出（如 pytest 结果路径）而非自带证据文件。⚠️ **安全收益为零**（不改变任何可执行检查——provenance 1a 只验引用存在性不验来源，verifier 可引用 CI 路径同时自带伪造文件）。短期价值是语义铺垫（为中期落地建立文档基础），非安全增益
2. **中期**：CI 独立**重新生成证据**（跑测试→产出结果文件），而非重跑 provenance 审计。provenance 重跑同一把不辨真伪的尺子，对伪造无效（见"不做的事"）；真正堵伪造的是"证据由执行生成"——CI 生成新证据，agent 产出若与 CI 不一致则暴露伪造
3. **长期**：P6 证据产出完全由 CI 驱动，agent 只写引用

### bats 测试

短期（L0 指导）无需新增 bats。中期 CI 复核需 `integration/ci-p6-evidence.bats`。

---

## ⑤ Subagent 假完成：主 Agent 文件校验

### 问题

subagent 报告"已修复/已实现"但文件未实际变更（T048 实证）。verifier.md 已有"分阶段落盘"机制但执行率低。

### 方案

两层防护（来自 t048-improvements-phase2 方案 D2，评为"本轮质量最高"但尚未落地）：

**1. subagent 侧**：派发 prompt 末尾加固定校验指令：

```
返回前执行：grep -c '关键改动标记' 文件路径
输出非 0 才返回成功，否则报告"改动未落盘"并重试
```

主 Agent 在 prompt 中指定期望的 grep 模式和文件路径。

**2. 主 Agent 侧（外部可观测，D2）**：在 `dispatch-protocol.md` 主 Agent 行为规范中增加：

> 收到 subagent "已修复/已实现"报告后，必须对声称修改的文件做内容校验（grep 关键行或 diff），未改则重派。不信 subagent 摘要，信磁盘内容。

### 修改清单

- `dispatch-protocol.md`：主 Agent 行为规范增加校验步骤
- `assets/templates/dispatch-prompt.md`：prompt 模板末尾加校验指令段

### bats 测试

- `unit/dispatch-context-warning.bats` 补充：dispatch-prompt.md 含校验指令关键词

---

## ⑥ Gate 正则语义化放宽

### 问题

P2 候选方案正则 `^###?\s*(候选方案|方案\s*[ABC123abc一二三四五])` 对 `方案 <多词名>` 写法不友好（如 `### 方案 Alpha`）。但用 `候选方案` 前缀的写法（如 `### 候选方案 Alpha`）已可匹配——问题仅限 `方案` 前缀+多词名的场景。gate 检查"格式对不对"而非"有没有"。

### 方案

统一原则：**gate 检查"有没有"，不检查"格式对不对"**。格式由 CI lint 管。

### 修改清单

- `check-gate.sh` P2 分支：候选方案正则改为 `^###?\s*(候选方案|方案\s*[A-Za-z一二三四五]|Alternative|Option)`——保留 `^###?\s*` 行首锚点，防止匹配行内任意位置
- 审查其他 gate 正则，凡是"关键词精确匹配"的，改为"语义关键词集合匹配"——均保留行首锚点

### bats 测试

- `unit/check-gate.bats` 补充：`方案 Alpha` / `方案 Recommended` / `Alternative A` 等多词方案名匹配

---

## ⑦ F6/F7 验收环境与发布 checklist（仅 ui_affected 时）

### 问题

原评审建议 P0-brief 新增 `verification_env` 字段 + P8 发布后 checklist。但给每个任务（含大量非 UI 任务）增加填写负担——UI 任务受益，非 UI 任务纯负担。

### 方案

**`verification_env` 仅当 `ui_affected: true` 时必填**，非 UI 任务可省。

### 修改清单

- `verifier.md`：P6 验收环境规范段增加——"若 P0-brief 声明 ui_affected=true，verification_env 字段必填（列出验收环境与生产环境的已知差异）"
- `assets/templates/p0-brief-template.md`：`verification_env` 字段标注 `(ui_affected=true 时必填)`
- P8-release.md 模板：READY checklist 增加发布后验证项（版本 bump 后重跑 P5 gate + UI 任务截图验证），标注 `(ui_affected=true 时适用)`

### bats 测试

无需新增。这是 L0 指导层改动。

---

## 实施顺序

```
Phase 1（激励层，疏）：
  ① check-p6-format.sh --fix    ← 新脚本 + bats
  ② PAUSED 语义翻转              ← 纯文本改动 + consistency 锚点更新
  ③ 逐步溯源决策表               ← 纯文本改动

Phase 2（结构层，堵）：
  ④ 证据由 CI 生成原则声明       ← 纯文本改动（L0）
  ⑤ subagent 假完成校验          ← dispatch-protocol.md + dispatch-prompt.md

Phase 3（卫生层）：
  ⑥ gate 正则语义化              ← check-gate.sh + bats
  ⑦ verification_env 条件化      ← 纯文本改动
```

Phase 1 先行——① 是最直接的疏通手段。②③ 不依赖 ① 也能独立成立（语义翻转和溯源决策表是协议层面的正确指引），但 ① 提供物质基础：当"派 verifier"真的比自己写快时，语义翻转才不是空话。

---

## 不做的事

| 不做 | 理由 |
|------|------|
| provenance 审计降级 WARNING | 削弱局限 3 防御换摩擦缓解，交易方向错（R1）。用自动格式化替代 |
| P6-acceptance.md 加 agent=main 硬拦截 | 投入产出比不如制度设计（R3）。P6-acceptance 本身即产物、无独立交叉核对物，比 P2 上弱——能抬高"随手代写"成本，但不能阻止"改标 verifier"。有限价值不如 ①②③④ 的制度+结构方案 |
| CI 重跑同一套 provenance | 重跑同一把不辨真伪的尺子，对伪造无效（R8.3）。真正堵伪造的是 ④ 证据由执行生成 |
| provenance 1a 从存在性升级为内容校验（hash/签名） | 1a 只验文件存在不验内容，agent 可放任意内容充数。但内容校验需 CI 基础设施支持（CI 生成带 hash 的证据清单 + 1a 比对 hash），超出 agate 栈无关协议的范围——留为长期目标，与 ④ 长期合并 |
| verification_env 无条件进全局 | 给非 UI 任务加填写负担（R7） |

---

## 与已有方案的关系

| 已有方案 | 本方案关系 |
|---------|-----------|
| t048-improvements-phase2（G/B/D/E2/E3） | D（假完成防护）→ 本方案 ⑤；E2（agent=main）→ 不做（R3）；G/B → 已实施 |
| agate-protocol-review-t048-t052（F1-F10） | F1 降级 → 不做，改 ① 自动格式化；F2 agent 字段 → 不做，改 ①②③ 制度设计；F3-F8 → 本方案 ⑤⑥⑦ |
| review-20260711-1921（R1-R8） | 本方案是 R8 落地清单的实现 |

---

## 验证

每个 Phase 完成后跑：

```bash
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
python3 agate/scripts/check-protocol-consistency.py
shellcheck -S warning agate/scripts/*.sh
bash agate/tests/scripts/count-tests.sh
```

Phase 1 新增 `unit/check-p6-format.bats`，用例数以 `count-tests.sh` 输出为准。
