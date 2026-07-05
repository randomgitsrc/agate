---
review_date: 2026-07-05
reviewer: main
review_target: >-
  commit 5564cc2..46e0f36 — step 0 实施：删 8 文件必读框架 + CHECK 5 + 反向传播修复
  （check-protocol-consistency.py / orchestrator-template.md / state-machine.md /
   consistency.bats / dispatch-protocol.md / loop-orchestration.md /
   agate-changes.sh / agate-summary.sh / scripts/README.md / CHANGELOG.md）
type: 独立实施评审（对抗性，全量实跑）
method: 装 bats 跑全套 + 跑 consistency + 全库扫悬空"8文件"引用 + 核对 CHECK 数同步 + 审 self-gate-skip 准确性
baseline: 199/199 bats, 0 ERROR, 9 CHECK
prior_reviews:
  - docs/reviews/agate-phase-card-enforceability-step0-review-2026-07-05.md（提出 S1/S2/S3）
---

# step 0 实施评审（独立、实证）

## 总判定：PASS

上一份评审的 S1/S2/S3 **全部正确落实**，反向传播做得彻底，且**这次实施的过程自身就是一个正面样本**——他们自己的 alignment review 把反向传播漏改标成 MISALIGNED 并在后续 commit 修掉。唯一一条值得记的是 5832b26 的 self-gate-skip 理由不准确（但后续 alignment review 兜住了）。以下每条附实跑证据。

---

## 一、回归基线：198/198，0 ERROR，CHECK 5 干净移除

| 检查 | baseline | 本轮实测 | 结论 |
|------|---------|---------|------|
| 全量 bats | 199 | **198，0 fail** | ✅ −1 = CON.5 随 CHECK 5 删除（预期） |
| consistency exit | 0 | **0，0 ERROR** | ✅ |
| CHECK 数 | 9 | **8（1-4,6-9）** | ✅ CHECK 5 **整个消失，非空壳** |

CHECK 5 不是留了个空 `FILE_COUNT_ANCHORS=[]` 的绿色 no-op——是**函数体 + 锚点一起删**（check-protocol-consistency.py −56 行），头部 CHECK 列表跳过 5，line 78 留显式「已删除」注释。这正是 S1 建议的 option (a)：删掉，不留 theater。

---

## 二、S1/S2/S3 逐条落实

### S1（theater check）— 完全解决，含建议 4

- CHECK 5 + CON.5 一起删（option a），不留空壳 ✅
- **检查数 9→8 同步**：`scripts/README.md:73` 显式「检查项从 9 减到 8（CHECK 1-4, 6-9）」——我建议 4 的头部注释 + README 同步都做了 ✅
- 事实错误（把 CHECK 7/8 锚点当 CHECK 5）在实施中自然消解——他们没有去"保留其他 CHECK 5 锚点"，而是直接确认 CHECK 5 只有那两条、全删 ✅

### S2（:506 现状过时 + 悬空回退）— 完全解决

实测当前 :506：

> 依次重读：orchestrator-template.md 的 mapping 表查当前阶段卡片，按卡片指引执行。

`grep "8 个协议文件" state-machine.md` **返回空**——:506 的"8 文件"回退指针彻底清除，:507-508 旧枚举清单也删了（CHANGELOG 记录）。无悬空。

### S3（论证高估 CHECK 5）— 措辞据实修正

CHANGELOG 的表述是「删 CHECK 5……该计数**已无协议意义**」——不再用"CHECK 5 强制阅读"的错误 attribution，改为"计数不再有意义"。正是 S3 建议的据实措辞。

---

## 三、反向传播：彻底，且被自己的 alignment review 抓出来

删 8-文件框架后，最大实施风险是残留的"读 8 文件"引用变悬空。**全库实测扫描**：

```
$ grep -rn "8 个协议文件|依次重读|重读.*协议文件" agate/
AGENTS.md:40   "不必全读 8 个协议文件"   ← 正确的降级提示（别全读、用 mapping），非悬空
state-machine.md:506  "读 mapping 表查卡片"  ← 已清
agate-changes.sh:146  "重大变更→完整重读所有协议文件"  ← 有意保留（重大变更场景 ≠ 例行必读，CHANGELOG 确认已改"8"为"所有"）
```

**无悬空的"必读 8 文件"残留。** 且 CHANGELOG「破坏性变更」节完整登记了每一处反向传播（loop-orchestration.md:238 / dispatch-protocol.md:247 / agate-changes.sh:144,146 / scripts/README.md）。

**过程亮点**：这些漏改不是我这次评审发现的——是**他们自己的 alignment review（5832b26.md）抓的**。该报告把 A3（反向传播）和 A5（下游影响）标成 **MISALIGNED**，明确指出"3 个文件未做反向传播 + CHANGELOG 未记录"，然后在 4ce09f0 / 46e0f36 修掉。self-gate 的语义审查在这里**真起了对抗作用**，不是橡皮章。这是整条链里 self-gate 机制运作最健康的一次。

---

## 四、唯一值得记的：5832b26 的 self-gate-skip 理由不准确

commit 5832b26（删 CHECK 5）用了 `self-gate-skip: 协议结构重组（删约束，非加约束），脚本行为不变`。

**"脚本行为不变"是不准确的。** 实测该 commit 改了 `check-protocol-consistency.py`（删 CHECK 5，−56 行）——脚本行为**变了**（少跑一个检查）。"删约束非加约束"作为风险启发是合理的，但"行为不变"与事实不符。

**为什么不上纲上线**：紧随其后的两个 commit（4ce09f0 / 46e0f36）**跑了完整 self-gate（alignment review）**，把 skip 掩盖掉的反向传播漏改全抓出来修了。**过程净结果是对的**——skip 的不严谨被后续的实审兜住了。

**但记这一笔的价值**：self-gate-skip 的理由本身也是审计轨迹的一部分。删检查项时写"脚本行为不变"，和当年"未知阶段 P0"谎报、"hash 证明读了"是同一类——**用一个方便的措辞掩盖了实际发生的变化**。诚实的 skip 理由应是"删除检查项（降低约束），已跑全量 bats + consistency 确认 0 ERROR"，而非"行为不变"。这条纯属措辞精度，不影响本次实施质量。

---

## 五、结论

**可以合入 / 已合入，质量合格。** step 0 把原 F1 的临时兼容（保留 8 文件保 CHECK 5）正面清算了：Phase Card 从"叠加的可选优化"变成"真正的默认入口"，8 文件降为 reference，CHECK 5 随之干净退场。S1/S2/S3 全部落实，反向传播彻底，CHANGELOG 详尽，bats/consistency 全绿。

这一轮最值得肯定的不是代码，是**过程**：self-gate 的 alignment review 这次真的以对抗姿态运作（主动标 MISALIGNED、抓出自己的漏改），印证了"改了什么 + 应影响什么 + 影响到了没"的反向传播原则在实战中有效。唯一的瑕疵（skip 理由不准）也被这个机制自己兜住了。

下一步该回到主线：CLI（step 1）+ dispatch-context 模板/hook（step 2-3）——那才是"防漂移"机制的本体，且带着上一份评审确认过的字节级 marker/fence 陷阱。到那一步，step 4 测试务必真跑到"hash 相等 + commit 成功"，别止于"文件生成"。
