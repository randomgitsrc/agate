---
review_date: 2026-07-05
reviewer: main
review_target: >-
  commit 21300ca — Phase Card 方案加 step 0（8文件必读→mapping 入口）+ F3b 修复
  docs/plans/agate-phase-card-enforceability-2026-07-05.md
prior_reviews:
  - docs/reviews/agate-phase-card-enforceability-review-2026-07-05.md
  - docs/reviews/agate-phase-card-enforceability-revision-review-2026-07-05.md
type: 修订复审（实证驱动）
method: 跑脚本核对 FILE_COUNT_ANCHORS 条目 / CHECK 5 空锚点行为 / CON.5 测试 / state-machine.md:506 现状
---

# 「step 0 + F3b 修复」复审

## 总判定

**F3b 彻底修好，标题诚实降级也采纳了——这两块干净。新加的 step 0 方向正确（让 Phase Card 真正取代 8 文件必读），但有三处问题，最重的是：删完两个锚点后 CHECK 5 变成一个"永远绿、什么都不查"的空壳检查，而计划对此的描述是错的。**

---

## 已修好（上一轮残留 + 软观察，全部采纳）

| 上轮发现 | 本次修订 | 核实 |
|---------|---------|------|
| **F3b** marker 名不一致（hook 用 START/END，模板用 HASH/END_AGATE_CARD） | 模板改为 `AGATE_CARD_START/END`，与 hook 一致 | ✅ |
| **F3b** ` ``` ` fence 导致两侧不等 | 模板去 fence，CLI 原文直嵌 marker 之间 + 补「三方字节一致」三点约束 | ✅ |
| **F3b** 测试只测"文件生成" | 测试改为「必须实跑到 hash 相等 + commit 成功」 | ✅ |
| 软观察：标题超售 | 标题改「防漂移 + 信息层完整性」+ 开头加诚实定位声明（不声称解决强制阅读） | ✅ |

F3b 这条尾巴收干净了，且把"实跑到 hash 相等"写进了测试纪律——正是这个字节级问题需要的。诚实定位声明尤其好：明说本方案不解决「不知道 agent 真读了没」，只解决防漂移，把原始用户问题挂回 forcing function / issue #003。

---

## step 0 方向对：这是原 F1 张力的逻辑收尾

回顾：本系列第一份评审的 F1 指出「删 8 文件列表会破 CHECK 5」，当时选择「保留列表 + 叠加 mapping 保 CHECK 5」。那是**临时兼容**——代价是 orchestrator-template.md 同时说「读这 8 个文件」和「用 mapping 表」，一个矛盾的双入口。

step 0 现在决定**彻底删掉「8 文件必读」框架，让 mapping/CLI 成为默认入口，8 文件降为 reference**，并配套移除 CHECK 5 锚点。这个方向是对的——它把当时的临时兼容清算掉，让 Phase Card 从「叠加的可选优化」变成「真正的默认入口」。**问题不在方向，在执行细节。**

---

## S1（事实错误 + theater check）：删完锚点，CHECK 5 变绿色空壳

计划 step 0 写：「去掉这两个锚点…**保留 CHECK 5 其他锚点（如 v0.6 关键词、README badge 等）**」。

**这句话是错的。** 实测：

```python
FILE_COUNT_ANCHORS = [
    { "file": "agate/orchestrator-template.md", "expected": 8, ... },
    { "file": "agate/state-machine.md",         "expected": 8, ... },
]   # ← 只有这两个，没有别的
```

- v0.6 关键词是 **CHECK 8**，README badge 是 **CHECK 7**——都不是 CHECK 5。
- `FILE_COUNT_ANCHORS` 是 CHECK 5 的**唯一**数据源，只有这 2 条，step 0 要全删。

删完 `FILE_COUNT_ANCHORS = []`。看 CHECK 5 函数体：

```python
def check_file_count_anchors(root, rep):
    all_ok = True
    for anchor in FILE_COUNT_ANCHORS:   # ← 空列表，循环体不执行
        ...
    if all_ok:                          # ← 恒 True
        rep.ok("CHECK5-count")          # ← 永远 PASS
```

**CHECK 5 变成一个永远 PASS、但什么都不检查的空壳。** 而 CON.5 测试（`断言 "PASS CHECK 5"`）照样绿——测试也一起变成无意义。

这正是本项目自己批评过的**「same-source dashboard = theater」**那一类：一个绿着的检查给出"已验证"的假信号，实际什么都没验。**空壳检查比没有检查更糟**——它让读输出的人以为 CHECK 5 在守某个不变量，其实没有。

**建议二选一（诚实优先）**：
- **(a) 连 CHECK 5 + CON.5 一起删**：明说 agate 不再计数校验任何文件清单。检查数从 9 减到 8，README/文档同步。诚实、干净。
- **(b) 把 CHECK 5 改去守别的真东西**：如果还有值得计数校验的清单（比如 phase-cards 数量 = 9、rules 文件数），把锚点换成它。让 CHECK 5 继续有意义。

不建议保留一个空的 `FILE_COUNT_ANCHORS`——那是 theater。

---

## S2（现状描述过时 + 悬空回退指针）：state-machine.md:506 已经不是计划说的样子

计划 step 0 item 2 说「当前：重读 orchestrator-template 列出的 8 个协议文件」。

**实测当前 :506 已经是**：

> 依次重读：orchestrator-template.md 的 mapping 表查当前阶段卡片，然后按卡片指引加载协议文件（推荐），或回退到…「工作流规则」列出的 8 个协议文件全量重读。

:506 在 phase-cards 实施（commit 7afa551）时**已经改过一次**。计划描述的是**那次修改之前**的状态——作者没有重读 :506 的当前内容。这是"把过时状态当现状"的老模式。

**更重要的连锁**：当前 :506 里仍有「**回退到…8 个协议文件全量重读**」这句。如果 step 0 从 orchestrator-template 删掉 8-文件必读列表（移到 Fallback reference 节），:506 这个「回退到…8 文件」指针会**再次悬空**——它指向的东西换了位置/性质。step 0 item 2 只写「改为 mapping 表」，漏了同步这个回退指针的落点。

**建议**：step 0 先重读 :506 当前内容，基于**真实现状**描述改动；并明确把 :506 的回退指针指向 8 文件的新位置（Fallback reference 节），而非留悬空。

---

## S3（论证高估 CHECK 5）：CHECK 5 从不强制 agent 读

计划的核心论证是「8 文件必读 vs 渐进加载（推荐）是矛盾体：必读是强约束 → **CHECK 5 强制 → agent 必须读**」。

**CHECK 5 是文档计数一致性检查**——它只校验"orchestrator-template 声明的文件数 = 实际列表长度"，**从不强制 agent 读任何文件**。把 CHECK 5 说成"强制 agent 读"，和之前"hash 证明 agent 读了卡片"是同一类误 attribution：把只做 artifact/文档一致性的机制，说成有行为强制力。

真实的"矛盾体"只是 orchestrator-template.md 的**散文措辞自相矛盾**（既说读 8 文件、又说用 mapping），不是"CHECK 5 强制读 vs mapping 说别读"。

**这条改对了反而加强删锚点的理由**：CHECK 5 锚点守的是一个"必读清单的计数"，而这个清单本就不该是"必读"——所以锚点守的是个不再有意义的不变量，删它是对的。但删的理由应该是"这个计数不再有意义"，不是"CHECK 5 在强制阅读、我们要解除强制"。措辞据实，逻辑更顺。

---

## 建议清单

| # | 建议 | severity |
|---|------|----------|
| 1 | 纠正"保留 CHECK 5 其他锚点"的事实错误；决策 CHECK 5 空壳去留——删（含 CON.5）或改守真东西，别留 theater | 高（诚实 + theater） |
| 2 | step 0 基于 :506 **真实现状**重写改动描述；把 :506 回退指针指向 8 文件的新 reference 位置，防悬空 | 中 |
| 3 | 删 8-文件必读的**理由**据实改为"该计数不再有意义"，不用"CHECK 5 强制阅读"的错误 attribution | 低（措辞精度） |
| 4 | 若采纳建议 1(a)，同步改 check-protocol-consistency.py 头部注释的"CHECK 5"行 + README 检查数（9→8）——注意这触发 self-gate 递归 | 中（连锁） |

## 一句话结论

**F3b 和标题诚实降级都干净收尾；step 0 方向正确（清算原 F1 的临时兼容）。但它留了一个绿色空壳 CHECK 5——而计划对此的描述是错的（把 CHECK 7/8 的锚点当成 CHECK 5 的）。** 决策清楚：删空壳还是改它去守真东西，别让一个永远 PASS 的 no-op 冒充在检查什么。顺带据实重写 :506 的现状与回退指针。修完这三处，step 0 就 implementation-ready。
