---
phase: P4
task_id: TAG0012-protocol-mechanism-fixes
type: review
parent: P4-implementation.md
trace_id: TAG0012-P4-review-20260818
status: approved
created: 2026-08-18
agent: review
---

[PROD_NOT_TOUCHED]

# P4 实现评审 — 偏执 Staff Engineer 视角（review）

> 评审对象：agate 仓库工作区当前**未提交**改动（`git diff` / `git diff --stat`），12 个协议文件，共
> 290 insertions / 3 deletions。对照基线：P2-design.md（approved）§1/§2.1/§3.x + P1-requirements.md
> （23 条 BDD）。方法：逐文件读取完整 diff（非仅 grep 关键词），核对规则语义是否忠实传达，独立复跑
> 锚点测试与一致性脚本，不采信 implementer 自述。

## 角色适用性说明（按 dispatch-context 约束 1）

本任务无 SQL/数据库/并发/前端改动，角色文件 Pass 1（SQL 注入、Read-Check-Write 竞态、TOCTOU）与
Pass 2 多数项（async/sync 混用、N+1、资源泄漏）及前端专项均不适用，不作为"无事可审"的依据。评审
精力集中在 dispatch-context 第 2-6 点列出的本任务真实风险面：字段命名一致性、权威源/副本双写一致性、
CHECK3 硬编码行号反模式、回归复核、"意外发现"绕过测试约束的合法性。

## 架构问题（阻塞级）

无。

## 架构问题（非阻塞）

无新增发现。已确认 P2-review.md 记录的 2 条非阻塞发现（批次表 L521 文件覆盖描述不精确 / verification_env
现状"节"定性夸大）均属 P2-design.md 自身文档描述层面的瑕疵，不要求、也未在 P4 实现中被"修正"——
P4 是按 files_to_read 精确定位（L952-1001 实际内容）落地，独立核实 BDD-10/11/13（含 L521 条件性子句）
在 dispatch-protocol.md 中均已正确落地（见下方逐项核查），未因 P2 文档描述层面的瑕疵产生实现缺失。
两点本身非阻塞，本评审同样不作为打回理由。

## 逐项核查（对照 dispatch-context 约束 2-6）

### 约束 2：`timeout_seconds` 三处字段名/语义一致性

`grep -n "timeout_seconds" agate/phase-cards/P2-design.md agate/assets/execution-roles/architect.md
agate/assets/templates/task-files.md` 核实：三处字段名逐字统一为 `{key}_timeout_seconds`（`P5_timeout_seconds`
/ `P5_e2e_timeout_seconds` / `P6_timeout_seconds` 等实例）。语义层面：

- P2-design.md 卡片是**权威定义**，四点规则全部展开（排除 P3 / per-key 声明 / 三档基准表 120/300/600s /
  向后兼容）
- architect.md 是**引用式**落地（"字段规则四点...的权威定义在 P2 卡片...本节只做声明位提醒，不重复展开
  基准表细节"），未重复展开却也未遗漏"存在四点规则"这一事实，读者能顺着引用找到权威定义
- task-files.md 是**样例块 + 完整注释**，三档基准表数值（120/300/600）与 P2 卡片逐字一致，"排除 P3"
  的关系说明与 P2 卡片一致（"P3 走 AGATE_TDD_TIMEOUT，不写 P3_timeout_seconds"）

三处不是"用不同写法表达同一个意思"，而是"权威定义 + 两处引用/样例"的一致结构，符合协议惯例，未发现
语义漂移。

### 约束 3：权威源 vs 引用副本双写检查

**dispatch-protocol.md（权威源）vs dispatch-prompt.md（同步副本）**：逐句对照两份"命令超时兜底"新增段
落——公式结构一致（取值 = 预期耗时 ×1.5；已声明 `{key}_timeout_seconds` 时"预期耗时"直接取该值，仍需
×1.5；未声明则估算后 ×1.5）、固定三动作一致（停止执行/写留痕记录卡在哪条命令/返回主 Agent，不换命令
不深挖）。无矛盾表述。dispatch-prompt.md 侧文字更精简（措辞"精简但语义/关键词与协议侧一致"的自述属实）。

**verifier.md / P5-verification.md / P6-acceptance.md 引用式落地检查**：三处均只提及规则名称（"可重试/
不可重试分类""批处理要求""止损轮次""环境准备职责边界"）作为话题标签，未重复展开 dispatch-protocol.md
中的完整规则文本（如 4 条不可重试判据全文、止损轮次数值"2"的独立计数说明、READY 后三条归属判据全文均
未在这三处重复出现）。verifier.md 保留的"两条操作约束"（默认不自启环境 / 失败先分类批量验证）是 P2-design.md
§3.3 明确要求"落到 verifier 身上的操作约束"这一层，不是对权威定义的重复展开，符合设计意图，不构成
"改一处漏一处"的双写风险。

### 约束 4：CHECK3 硬编码行号引用反模式复核

对 12 个改动文件的完整 diff 内容跑 `grep -nE '[A-Za-z0-9_-]+\.md[[:space:]]+L[0-9]+(-[0-9]+)?'`，**零命中**。
独立确认 implementer 自查结论属实：所有跨文件引用均用「节标题」措辞（如"见 dispatch-protocol.md「verification_env
失败处理协议」"），P2-design.md §2.1 表 / files_to_read 里的 `L691-695` 等行号未被誊抄进协议正文。

### 约束 5：回归确认

独立重跑：
```
python3 -m pytest agate/tests/unit/test_protocol_mechanism_anchors.py -v
→ 28 passed in 0.04s（结果与 implementer 自查一致）

python3 agate/scripts/check-protocol-consistency.py --strict
→ 0 ERROR，279 WARNING（结果与 implementer 自查一致）
```
抽查关联既有测试：
```
python3 -m pytest agate/tests/unit/test_agate_render_dispatch_prompt.py agate/tests/unit/test_check_protocol_consistency.py -q
→ 36 passed（无关联回归）
```

### 约束 6：dispatch-prompt.md 意外发现（花括号占位符改写）核查

`test_rp_13_no_residual_placeholders_except_whitelisted` 的正则 `\{[a-zA-Z0-9_|： -]+\}` 只匹配 ASCII
字母数字/下划线/竖线/冒号/连字符/空格组成的花括号内容，中文字符（如 `{命令}`）本不会被该正则命中——
implementer 的改写严格来说不是绕开一个真实会拦截的残留，而是主动规避了潜在的 `{N}` / `{key}` 类 ASCII
占位符残留。改写后的文本（`timeout 180s <你的命令>`）保留了完整的 ×1.5 公式与"已声明则取该值"的分支
逻辑，语义未损失，不是"掩盖问题"式改写。

**唯一值得记录的可读性瑕疵（INFORMATIONAL，非阻塞）**：

```
[INFORMATIONAL] agate/assets/templates/dispatch-prompt.md:38
  示例命令 `timeout 180s <你的命令>` 中的 "180s" 是纯占位数字，与下方 "P5_e2e_timeout_seconds: 300"
  的示例数值无对应关系（300×1.5=450，不是 180），若读者未细看"秒数按下面算"这句提示，容易误以为
  180 是某种计算结果或推荐默认值。
  Fix（可选）：把示例改成同一处引用的数值以消歧，如 `timeout <预期耗时×1.5 秒>s <你的命令>` 或直接
  用 "timeout 450s <你的命令>  # 对应 P5_e2e_timeout_seconds: 300 的例子"，让占位符与下方公式讲解
  的数字对得上。不影响测试通过、不影响规则语义传达，是否修复留给主 Agent 判断是否值得为此再走一轮
  implementer 迭代。
```

## BDD 覆盖抽查（P2-design.md §2.1 逐条语义核对，非仅关键词命中）

以下每条均实读 diff 原文确认"规则语义是否准确传达"，不只是确认 grep 命中：

- BDD-10（verification_env 失败处理协议）：dispatch-protocol.md 新增段落完整覆盖 P2 候选 A1 采纳文本
  的 4 条规则（可重试/不可重试二列判据表、批处理要求、止损轮次=2 独立计数不入 `.state.yaml`、READY
  后三条归属判据），文字与 P2-design.md §1 候选 A 原文逐条对应，未遗漏"机制误用型问题"这一不可重试
  判据（TAG0009 案例专门提及）。
- BDD-11（环境准备职责边界）：三条条款齐全，且显式声明"本节是权威定义，P5/P6 卡片与 verifier.md 引用
  本节，不重复展开"，与 env_state 字段建立引用关系而非重新定义字段语法，符合 P2 §3.3 设计。
- BDD-12/17（资源密集型默认串行）：并行规则新增第 4 条，四项判据（xdist/E2E/构建/独占资源）与"全阶段
  适用表"P5 行同步更新，P5-verification.md 侧新增引用句，双向一致。
- BDD-1~9（P0/P1/analyst 三处同类扫描+P0_STALE+能力/环境判断树）：三问式预判、判断树 ASCII 图、`[P0_STALE:
  漂移点]` 标记格式（含裸标记不算数的显式声明）均逐字落地，严重 3 条/轻微 2 条判据在 P0 卡/P1 卡/analyst.md
  三处表述一致（均引用同一套判据文本，未出现三种不同表达）。
- BDD-21（task-files.md 样例块）：新增 `P5_timeout_seconds`/`P5_e2e_timeout_seconds`/`P6_timeout_seconds`
  三行示例 + P3 key 处补充"P3 的超时不写 P3_timeout_seconds"一行，联动 BDD-16 第 4 点要求满足。

未发现"关键词命中但语义空洞/规则表达有歧义"的情况。

## 决策标注复核

- `[DESIGN_GAP]` / `[SCOPE+]` / `[SCOPE_GAP]` / `[CLARIFY]`：对 `git diff` 全文 grep 以上标记，**零命中**，
  与 implementer 自报的"0 条"一致。
- 未改动文件核查：`check-gate.py` / `agate_common.py` / `agate-frontmatter-check.py` / `.state.yaml` schema /
  既有测试文件 / `scripts/*.sh` 确认零改动（`git diff --stat` 12 个文件清单与 P2-design.md §2.2「明确不改」
  清单互斥，无越界）。

## 结论

12 个协议文件的改动忠实落地 P2-design.md §1/§2.1/§3.x 的三类新增机制设计，未发现规则语义传达失真、
权威源/副本矛盾、CHECK3 反模式、或范围外改动。独立复跑锚点测试（28/28）与一致性检查（0 ERROR）结果
与 implementer 自查一致。发现 1 条 INFORMATIONAL 级可读性瑕疵（dispatch-prompt.md 示例数字与下方公式
数值不对应），不构成阻塞，是否修复留给主 Agent 判断。

**PASS，0 个 CRITICAL / 0 个阻塞架构问题。**
