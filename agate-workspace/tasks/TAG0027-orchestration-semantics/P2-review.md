---
phase: P2
task_id: TAG0027
type: review
parent: P2-design.md
trace_id: TAG0027-P2-review-20260902
created: '2026-09-02'
agent: plan-eng-review
status: approved
---
# TAG0027 P2 方案设计评审（plan-eng-review 复审轮）

> 评审对象：`P2-design.md`（修复后 498 行，retry1 定点修订版）
> 评审性质：**复审轮**——首轮 rejected（P2-review.md 2026-09-02，211 行）后 architect 已按
> A1/A2/A3/B1/B2/B3 修复；本轮核对 6 问题闭合度 + 抽查修复波及节的连贯性，产出终局判定。
> 评审依据（协议文件全部实读 worktree `agate/` 现状，非 ~/.agate）：check-gate.py /
> pre-commit-gate.py / check-p6-provenance.py / check-judge-verdict.py /
> check-protocol-consistency.py / state-machine.md / P1-requirements.md（25 BDD）+ P0-brief.md +
> 首轮 P2-review.md + P2-progress.md（修复轮记录）。
> 评审日期：2026-09-02

## 评审范围与方法

复审范围 = 首轮 6 问题闭合核对（增量），标准不变：每条结论引用设计节号（修复落点）+ 外部
实证（脚本/state-machine 行号）。dispatch-context 约束 4（测试缺口 3 条须确认已在 §5 映射表补
锚点）逐条核对。首轮 approved 部分（候选 A + 8 面形态锁定）不重新全量评审，只抽查修复波及节
连贯性。

## 闭合核对表（A1/A2/A3 阻塞 + B1/B2/B3 非阻塞）

| # | 首轮问题（摘要） | 修复落点（P2-design.md） | 实证核对结论 | 状态 |
|---|----------------|------------------------|------------|------|
| **A1** | P6/P6.5 共用 phase=P6，judge 通过后 P6→P7 推进裁决缺失 | §3.1 148-165（P6 条目 `next: P7` + 条件式裁决三步）、§3.4 253-264（exit 2 P6 特例分支完整裁决）、§5 BDD-6/9 447/450（P6 通过路径锚点） | `gate_p6`（check-gate.py 1051-1093）恒 return 1/2、无 exit 0（1093 return 2）——「P6 恒 exit 2、推进为条件式」前提成立；`gate_p65`（1096-1120）judge 未启用 return 0 / 缺 verdict return 1 / 双脚本过 return 0，与设计裁决链逐条对应；state-machine.md:139 + 74-78 佐证。裁决闭环完整：谁推进（agate-next P6 分支）、什么条件（provenance exit 0 → judge.enabled 分支 → gate_p65 exit 0）、不成立怎么办（exit 1 停留 P6 有指引）——P4 implementer 有实现依据，BDD-6/9 场景闭环 | ✅ 闭合 |
| **A2** | CARD-SOURCE 块内/替代 START 撞 pre-commit 2p hash；与 §3.5 来源标记不一致 | §3.5 282-290（CARD-SOURCE 置 START **之前**块外，不进 `_extract_card` 区间）、§3.6 300-320（D6-A 双锚点剥离 + 三处消费方同步面 311-318）、§5 BDD-18/20/25 459/461/466 | `_extract_card`（pre-commit-gate.py 171-189）只抽 START..END 之间行（183 起 / 186 止）→ 块外 CARD-SOURCE 不影响嵌入 hash；2p（425-448）期望 = next-card stdout、嵌入 = _extract_card，机制自洽。定案 (a) 明确：check-p6-provenance 审计 2（318-355）+ check-judge-verdict `_strip_card`（98-111/396-397）改剥离起点，pre-commit `_extract_card` 天然兼容无需改——三处消费方语义统一（BDD-25 转绿机制完整） | ✅ 闭合 |
| **A3** | CHECK 14 扫描面含 assets/，SKILL.md 等命中不在清理批也不在豁免清单 → 上线即红 | §3.8 336-337（豁免结构补 `assets/templates/dsh/` 平台食谱目录 + 语义叙述面 = `agate/*.md` 顶层）、346（存量清理批次面：9 顶层 md + architect.md:229 / custom-role.md:49-56 挂注记 + dsh/ 不进批）、§6③ 474（排查/扫描/豁免三面并陈）、§8 B3a 494、§7 484、R8 79 | `PROTOCOL_DIRS`（check-protocol-consistency.py:69）含 `agate/assets/` 实证；assets/ 平台名命中实测仅 3 文件 = `templates/dsh/SKILL.md`（目录实存 agent.cordis.yml/preset.yml/SKILL.md，17 处命中）+ execution-roles/architect.md:229 + templates/custom-role.md:49-56——设计处置面**全覆盖实测命中面，无遗漏**；dsh/ 结构豁免 + 两命中段挂注记 → 上线首跑 0 命中基线可达，与 §7 完成标志一致 | ✅ 闭合 |
| **B1** | §3.4 diff=1 前置与 P6 retreat:P4 矛盾；P5 误标 diff=2；§3.1/§6① 口径互斥 | §3.1 172（P5→P4 diff=1 / P6→P4 diff=2 均 retreat: P4；diff=2 由 retreat-to 逐阶落地，647-654 PAUSED 是人工直跳路径；CLI 不预判 diff）、§3.4 247-252（删 diff=1 前置 → retreat 表值存在即委托）、§6① 472、R11 82 | state-machine.md:132（P5→P4）/148（P6→P4）/647-654（diff≥2 PAUSED 表，652 行 P6→P4 diff=2）实读一致；agate-retreat-to.py 136-137 `while n>target_n: nxt=n-1` 逐阶语义与设计委托描述吻合；全篇 grep 无残留 "diff=1 前置"/"P5 diff=2" 旧表述 | ✅ 闭合 |
| **B2** | 加列位置正文/示例/解析器/S1S2-ANCHOR 三处不一致 | §3.2 180-198（统一 4/5 列：示例表头 184 next/retreat 在第 4/5 列、解析器取 4/5 列 196、S1S2-ANCHOR 注释 191-193 注明列位语义） | 首轮 163 行旧示例表头（next/retreat 第 6/7 列）已消除，正文/示例/解析器/注释四处一致；`_TABLE_ROW_RE` 取前 3 列兼容实证（§3.2 178）保持成立 | ✅ 闭合 |
| **B3** | minimal_validation 表述过强 | §4.4 433（method 补 ⑧ P6 judge 后推进裁决链、⑨ CARD-SOURCE 过 2p hash）、435（note 弱化"均已实读确认"→ 不豁免失败测试首写，4 条首写主线 ②⑥⑧⑨） | 表述与 A1/A2 定案一致，⑧⑨ 即两条新主线；"已实读定位 4 条首写失败测试"比首轮"均已实读确认"更准确——A1/A2 正是"实读可发现却未定案"的教训 | ✅ 闭合 |

## 测试缺口核对（dispatch-context 约束 3：首轮「测试缺口」3 条须在 §5 补锚点）

| 首轮缺口 | §5 映射表锚点 | 核对 |
|---------|-------------|------|
| P6 judge 后推进路径无测试锚点 | BDD-6 447（judge 未启用直推 P7）+ BDD-9 450（judge 启用 + verdict 存在 + gate_p65 exit 0 → P6→P7 + state_transition 事件；exit 1 → 停留） | ✅ 已补 |
| CARD-SOURCE 产物过 pre-commit 2p 无测试 | BDD-25 466（渲染产物嵌入抽取 hash == next-card 期望 hash，CARD-SOURCE 不入抽取区间）+ BDD-18 459 / BDD-20 461（CARD-SOURCE 在 START 前断言） | ✅ 已补 |
| assets/ 平台名命中无清理/豁免测试 | BDD-17 458（pytest 断言 SKILL.md 属结构豁免：插平台名 → pass；architect.md/custom-role.md 命中段带注记 → CHECK 14 pass） | ✅ 已补 |

## 修复波及节连贯性抽查（首轮 approved 部分未被推翻）

- **架构方向**：候选 A（数据面权威 + 薄 CLI 消费方）维持（§2），未因修复改写 ✓。
- **8 决策面**：除 A1（①/④）、A2（⑤/⑥）、A3（⑧）、B1（①/④/⑧ R11）、B2（②）修正处外，形态锁定保持；§3.3/§3.7（exit2-resolution、档位 C）未受波及失真 ✓。
- **§1.1 Modify 表**：已含 check-judge-verdict.py `_strip_card` 双锚点同步行（45 行）——A2 三处消费方同步面在 Modify/消费方两处成对声明，P4 implementer 不易漏 ✓。
- **§1.2 Not Modify**：check-gate/check-state-transition 返回约定不变声明保持（首轮锁定的 BDD-13 边界未被破坏；A1 裁决全部落在新 CLI 消费侧）✓。
- **机器字段**：gate_commands（§4.1）9 key、files_to_read（§4.2）、env_constraints（§4.3）未受修复波及；§4.4 minimal_validation 与 A1/A2 定案对齐 ✓。
- **§5 BDD 映射**：25 条全映射保持，A1/A2/A3/B1 涉及行（BDD-6/7/9/10/17/18/20/25）已同步修复语义 ✓。
- **§7 完成标志**：482-484 分别含 A1（P6 推进裁决闭环）/A2（CARD-SOURCE 过 2p）/A3（dsh 豁免 + 命中段注记）三闭环表述，完成标志与修复一致、可达 ✓。
- **§8 批边界**：B1/B2 可并行、B3a→B3b 串行的批编排与 A3 处置面（B3a 含 assets 两命中段、dsh/ 不进批）一致，文件不跨批声明保持 ✓。

## 锁定决策（终版）

1. **整体架构方向锁定**：候选 A（数据面权威 + 薄 CLI 消费方）成立——新增消费方不复制语义、
   S-1/S-2 复用扩展、exit2-resolution 独立文件 + judge 复核挂载、审计 2 双锚点方向、CHECK 14/15
   进既有脚本、B1→B2 可并行 / B3a→B3b 串行的批编排，全部批准（§2、§3.1-3.8、§8）。
2. **8 决策面形态锁定（终版）**：
   - ① next/retreat schema：值域 = 枚举 phaseId（P0-P8，不含 P6.5）+ null；P8 next/retreat: null；
     P6.5 用 `gate_subphase`（hosted_on/forward_to/needs_revision_to）不写 next/retreat；
     **P6 条目 next: P7 合法但推进为条件式**——schema 只管值域，裁决在 CLI（§3.1）。
   - ② S-1/S-2 md 侧：WORKFLOW 总览表在「执行角色」后加 **4/5 列**（next/retreat），评审角色/门槛
     顺延 6/7 列；S1S2-ANCHOR 注释同步列位语义；`_parse_workflow_rows` 扩展取 4/5 列（§3.2）。
   - ③ exit2-resolution：任务目录 `{phase}-exit2-resolution.md`（frontmatter + 正文留痕）；不塞
     .state.yaml、不加 events 类型；复核挂载 = check-judge-verdict.py P6.5 校验扩展；
     P6 自身 exit 2 前进特例不落盘（§3.3）。
   - ④ agate next/advance：CLI 只 add 不 commit；exit 0 按 next 直推 / exit 1 按 retreat 表值存在
     即委托 retreat-to（CLI 不预判 diff）/ exit 2 非 P6 落盘 exit2-resolution、**P6 特例按 A1
     裁决消费 next:P7**（§3.4）。
   - ⑤ agate dispatch：模板骨架 + Lazy Injection（子进程 next-card）；**CARD-SOURCE 置于
     AGATE_CARD_START 之前（块外）**；手工兜底保留（§3.5）。
   - ⑥ 审计 2：双锚点剥离 = CARD-SOURCE 行起物理块优先 + START..END 兜底；三处消费方同步面
     （check-p6-provenance 审计 2 / check-judge-verdict `_strip_card` 需改，pre-commit `_extract_card`
     天然兼容无需改）（§3.6）。
   - ⑦ 档位 C：文档约定层 + CLI 调用点双层；append_event + commit 为可观测证据（§3.7）。
   - ⑧ 护栏 1：CHECK 14 段落级判据（`> 实现注记：` 段级豁免）+ 豁免结构三类（整文件
     platform-notes/SETUP、**assets/templates/dsh/ 平台食谱目录**、WORKFLOW 适用环境表行）；
     CHECK 15 词边界 + 豁免词典机械生成（§3.8）。
3. **测试缺口 3 条已闭环**：P6 judge 后推进 / CARD-SOURCE 过 2p / assets/ 处置，均在 §5 映射表
   有 pytest 锚点（BDD-6/9、BDD-25/18/20、BDD-17）。

## 结论

首轮 3 阻塞（A1/A2/A3）+ 3 非阻塞（B1/B2/B3）**全部闭合**：每项修复落点可定位（§节号 + 行号）、
与 worktree 脚本/state-machine 实证逐条对应、未引入新矛盾；架构方向与首轮 approved 部分未被
修复推翻；§5 测试缺口 3 条均已补锚点。按 dispatch-context 判定：**approved**（无遗留阻塞/非阻塞
问题，无新发现问题）。遗留事项 0——仅 P1 BDD-10 Given 正文回改（P6→P4）为 [SCOPE+] 文档修正，
由主 Agent 在 P2 通过后跟进（§6① 已声明，非 P2 缺陷）。
