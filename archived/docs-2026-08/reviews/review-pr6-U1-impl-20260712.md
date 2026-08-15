---
review_target: PR #6 — feat(U1) P1 需求评审 gate + do→review 迭代循环
reviewer: 独立第三方评审（非本 PR 作者，非 self-review）
date: 2026-07-12
head_sha: 7a607d3
base: 22225f7 (origin/main, PR #4 合并点)
verdict: pass-with-minor（0 blocking，2 次要，1 提醒）
status: approved-for-merge（U1 切片）
blocking: 0
secondary: 2（F1 status 全文 grep 可绕过；F2 B[0-9] 锚点近乎恒真）
info: 1（F3 方案引用未实施组件 → 6 个持久 consistency WARNING）
verification: 源码逐行核对 + 全套件实跑（254/254）+ 3 处变异测试 + 2 处对抗用例 + shellcheck + consistency + protocol-consistency
---

# PR #6 (U1) 实施评审

## 0. 范围认定（先划清 PR 实际做了什么）

本 PR 是「**完整 v7 方案文档（12 部件）+ 6 份评审记录 + U1 实施切片**」的打包，不是 12 部件全量实施。经 `git diff base..pr6 --name-only` 核实，**实际改动的源码/测试**仅覆盖：

- **⑧ P1 需求评审 gate**（核心）：新增 `requirements-review` 角色 + `check-gate.sh` P1 分支 + P1 阶段卡片 + state-machine 转移 + dispatch-protocol 强制评审节 + WORKFLOW 表 + orchestrator 不变量 + consistency.py CHECK 9 锚点
- **⑩ do→review 迭代循环**（纯文档注释）：P1/P2/P4/P6/P7 阶段卡片 + dispatch-protocol 新节 + state-machine 注释
- **N3 P7 实质锚点 WARNING**：`check-gate.sh` P7 分支加一条跨文件引用缺失告警

**未实施（仅存在于方案文档，属 U2–U5）**：①P6 自动格式化、③红 gate 逐步溯源回退、④provenance-CI、⑤subagent 文件校验、⑥⑦gate 正则/verification_env、⑨P5·P7·P8 subagent 化、⑪dispatch-context 扩展、⑫诊断落盘。

→ 本评审只对 **U1 已落地部分**判定实施质量；方案文档本身此前已经 6 轮评审在 `review-20260711-2257` 判 approved，不重复评审方案方向。

## 1. 实施正确性（独立核实，不采信 commit message / 评审记录）

| 项 | 方式 | 结论 |
|----|------|------|
| P1 gate 逻辑 | 逐行读 `check-gate.sh` P1 分支 | ✅ 缺 P1-review.md / 缺 status:approved / 缺 agent / agent=main / 无 BDD 锚点 → 逐条 exit 1；全满足 → exit 2。与 P2 gate 结构对称 |
| requirements-review 角色 | 读全文 | ✅ 结构完整，输出格式产出 `B01/B02` 锚点，与 gate 锚点检查自洽 |
| 文档一致性 | P1 卡片 / state-machine / dispatch-protocol / WORKFLOW 表 / orchestrator 不变量 / consistency.py 交叉读 | ✅ 六处对 "P1-review approved + agent≠main + BDD 锚点" 的表述一致，无悬挂引用 |
| 全测试套件 | 实跑 `bats unit/ regression/ integration/ sanity.bats`（与 CI 同调用） | ✅ **254/254 通过，0 失败**（unit 194 / regression 15 / integration 39 / sanity 6）|
| 既有测试是否被削弱 | diff `check-gate.bats` + `pre-commit-hook.bats` | ✅ 无削弱：G1 更新为新行为并**加了 output 断言**；集成测试**补齐 P1-review.md fixture** 以诚实满足新 gate（而非绕过）|
| shellcheck | `shellcheck check-gate.sh`（CI 用 `-S warning`） | ✅ exit 0，无告警 |
| 协议结构一致性 | `check-protocol-consistency.py` | ✅ exit 0，CHECK 9 PASS（6 WARNING 见 F3）|

### 1.1 变异测试（关键——防 G2.5「假✓」，验证测试真有牙齿）

对 `check-gate.sh` 做 3 处定点破坏，确认新测试**确实抓得到**：

| 变异 | 结果 |
|------|------|
| 缺 P1-review.md 的 `exit 1` → 改 `exit 2` | `not ok 1 P1: 缺 P1-review.md 期望 exit 1` ✅ 抓到 |
| `agent=main` 拦截 → 改 `exit 2` | `not ok 2 P1: agent=main 期望 exit 1` ✅ 抓到 |
| BDD 锚点检查失效（条件短路） | `not ok 3 P1: 无 BDD 编号引用 期望 exit 1` ✅ 抓到 |

恢复后 6/6 复绿。→ **P1 gate 测试非假✓，破坏实现即红。** 这一点独立佐证了评审记录里 "approved" 的自评——但佐证来自我的外部变异，不是采信自评。

## 2. Findings

### F1（次要 · 系统性 · 非本 PR 引入）— `status: approved` 是**全文 grep**，可被正文绕过

`check-gate.sh` 用 `grep -qE 'status:\s*approved' "$P1_REVIEW"` 扫**整个文件**，而 `agent` 字段却是**仅 frontmatter**提取（`sed -n '/^---$/,/^---$/p' | grep '^agent:'`）。同一段代码里两个门槛字段口径不一致。

对抗用例（已实跑验证）：frontmatter `status: rejected`、正文含一句 "gate 规则要求 status: approved 才放行" → **gate 返回 exit 2（放行）**，而正确行为应是 exit 1（拦截）。

**现实触发路径不牵强**：`requirements-review.md` 角色文件的「门槛产出」节写着 "通过 → `status: approved`"。一个**打回**的评审如果在正文里解释这条映射规则（LLM 解释裁决时很常见），正文就落了 "status: approved" 字面串 → 打回被当通过。

**诚实归因**：这**不是本 PR 的回归**——P1 gate 忠实镜像了**已合并的 P2 gate**（`check-gate.sh` 第 21 行 P2 同样全文 grep status、第 25 行 P2 同样仅 frontmatter 取 agent）。PR 达到了它的前置基线标准。但按项目自己的教义（LIMITATIONS §3 "能满足的任何 bar 都不可信"），这是一个**既有系统性弱点被复制到第 2 个 gate**，且恰好削弱本 PR 主打的那一条保证（P1 硬门禁可信）。

**不 block 合并**（内部与 approved 的 P2 基线一致），但这是**最值得在本 PR 顺手修**的一项——一行改动，同时收紧 P1 与 P2：

```bash
# check-gate.sh，P1 与 P2 分支通用改法：status 也只从 frontmatter 取
P1_REVIEW_STATUS=$(sed -n '/^---$/,/^---$/p' "$P1_REVIEW" | { grep '^status:' || true; } | sed 's/^status:\s*//' | head -1)
if [ "$P1_REVIEW_STATUS" != "approved" ]; then
    echo "GATE P1: P1-review.md frontmatter status 非 approved（当前: ${P1_REVIEW_STATUS:-缺失}）" >&2
    exit 1
fi
```

补一条 bats：frontmatter=rejected + 正文含 "status: approved" 字面串 → 期望 exit 1。（现有 test 5 的 rejected 用例正文**不含**该串，故抓不到此洞——测试覆盖也有同一盲区。）

### F2（次要 · 方案已诚实标注，但标注低估了弱度）— `B[0-9]` 锚点近乎恒真

锚点正则 `grep -qE 'BDD-|B[0-9]'`。对抗用例（已实跑）：正文无任何真 BDD、仅含 "面向 **B2B** 场景" → **exit 2 放行**（`B2` 命中 `B[0-9]`）。"B2B/B2C" 是需求文档极高频词。叠加：角色文件自己的示例输出就含 `B01/B02`，**照抄模板即满足锚点**。

方案正文已承认锚点 "只拦最懒的假完成"、真反造假靠 LLM 语义层 + 下游 P6/P7 暴露——所以这是**已知且接受**的边界，不是意外。但 "只拦最懒" 这个说法**低估了**：实际上对任何提及商业语境的真实需求文本，锚点几乎恒真，边际防护≈0。

**可选收紧**（非必须，有取舍）：改 `BDD-|B[0-9]{2,}` 对齐角色文件 `B01` 两位数格式，可排除 `B2B`。代价：会拒绝单位数 `B1`——而方案刻意要 "BDD 编号格式不固定"。故仅作为选项提出，是否收紧取决于是否愿意约束编号格式。

### F3（提醒 · 信息性）— 方案引用未实施组件 → 6 个持久 consistency WARNING

`check-protocol-consistency.py` 报 6 个 WARNING，全部是 v7 方案文档引用 U2–U5 才会建的文件：`consistency-reviewer.md`(⑨)、`check-p6-format.sh`(①)、`p0-brief-template.md`(⑪)。检查器正确地归为 "叙事文件" 只 WARN 不 ERROR，**不阻塞**。但这些 WARNING 会持续到 U2–U5 落地为止；建议给方案里这类前向引用加个 "future component" 标注或建 tracking，避免日后被误读成真实漂移。

## 3. 与历史遗留项的衔接

- 我此前对 `p6-gate-institutional-design` 判的 2 个 blocking（B1 逐步溯源与 `check-state-transition.sh` diff≥2 PAUSED 冲突；B2 ④ CI 重跑自相矛盾）——经 `review-20260711-2207` 记录，v4 已干净修复；方案在 `review-20260711-2257` 达 approved。本 PR 无重新引入。
- ⑩ 的 P1→P1 自评审循环 diff=0，**不**触发 `check-state-transition.sh` 的 diff≥2 强制 PAUSED；retry 累加到 `retries[P1]` MAX=3 后落 PAUSED。与 B1 关注点无冲突（B1 是 ③ 跨阶回退 P6→P4/P2，本 PR 未实施）。

## 4. 判定

**pass-with-minor / U1 可合并。** 0 blocking。实施正确、测试有牙齿（变异证实）、六处协议文档一致、与 approved 方案决策（P1 评审对所有任务不可裁）吻合，CI 三个 required check（bats/shellcheck/consistency）本地全绿。

两个次要项都指向同一族问题——**门槛字符串可以在"非真实裁决"的情况下被满足**，这正是本特性要消灭的模式。F1（status 全文 grep）尤其值得在本 PR 顺手收紧，因为它现在横跨 P1+P2 两个 gate，且修法只有一行。F2 方案已诚实认账，收紧与否是格式约束的取舍。

**一个不可让渡的提醒**：本 PR 附带的 6 份评审记录是 **self-authored**。它们展示了好的纪律（自评抓到过假✓、跑过第三方轮），但按项目自身 LIMITATIONS §3，self-authored 的 "approved" 本身不构成可信证据。上面判定成立的依据是我的**外部变异 + 对抗测试**，不是采信那些记录。
