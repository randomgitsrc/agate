---
review_date: 2026-07-05
reviewer: main
review_target: >-
  commit 717c4d7 — Phase Card 可执行性方案修订（评审 F1-F5 回应）
  docs/plans/agate-phase-card-enforceability-2026-07-05.md
prior_review: docs/reviews/agate-phase-card-enforceability-review-2026-07-05.md
type: 修订复审（实证驱动）
method: 逐条核对 5 个发现是否真修 + 静态求值 step2↔step3↔CLI 字节一致性
---

# 「可执行性方案修订」复审

## 总判定

**4/5 真修好了，诚实降级尤其到位。但 F3b 只修了一半——hook 侧 marker 改了名，产出它输入的 step 2 模板没跟上，两者仍会 100% mismatch。** 这正是项目 v0.8 引入「反向传播」原则要抓的漏：改了 A，A 的上游 B 没同步改。

---

## 已完全修复（4 项）

| 发现 | 修订 | 核实 |
|------|------|------|
| **F1** 决策表言过其实 | C 行为层「✓」→「条件式 nudge，非 barrier」；决策层 A/C「✓」→「✗（agent 仍需自决 phase→cat）」；补「真实价值在信息层和防漂移，不是 barrier，这是诚实降级」 | ✅ 诚实到位 |
| **F3a** `P${PHASE}`=PP3 | 改为 `${PHASE}`，加实测注释（check-p6-provenance.sh:105），提示行同步；无残留 | ✅ |
| **F4** CLI「机械化决策层」高估 | 改为「权威卡片源 + 防漂移锚点」 | ✅ |
| **F5** 卡片行数凭记忆 | 换成真实 `wc -l`（P0=51…P2=104…P8=90），与实测一致 | ✅ |

这轮修订的诚实性值得肯定——F1 选择了「诚实降级表格」而非「加 forcing function」，这是有权做的架构选择，且做得干净：不再假装 C 是 barrier。

---

## F3b 只修了一半：hook marker 变更未反向传播到模板（会 100% 误拦）

原 F3b 是「hash 两侧规范化不对称」。修订把 **hook 侧**改对了——两侧都 hash CLI 原始输出、hook 用 `sed` 区间提取。但引入了**新的 marker 名**，而**没有同步 step 2 模板**：

```
step 2 模板（169/175 行）：  <!-- AGATE_CARD_HASH: … -->  …  <!-- END_AGATE_CARD -->
step 3 hook（197 行）：       sed -n '/<!-- AGATE_CARD_START -->/,/<!-- AGATE_CARD_END -->/p'
```

hook 拿 `AGATE_CARD_START/END` 去 `sed` 一个只含 `AGATE_CARD_HASH / END_AGATE_CARD` 的文件 → **区间匹配为空 → EMBEDDED 空 → hash 必然 mismatch → 100% 误拦照旧**。原 F3b 的病没根治，只是从「规范化不对称」变成了「marker 名不一致」。

**第二层，即使 marker 对上也不够**：step 2 模板把 CLI 输出包在 ` ``` ` fence 里：

```
<!-- AGATE_CARD_START -->      ← 假设改成新 marker
```
{CLI 输出原文}
```
<!-- AGATE_CARD_END -->
```

hook 的 `sed '1d;$d'` 只删区间首尾两行（两个 marker 行），**留下了 ` ``` ` fence**。而 EXPECTED 是 CLI 原始输出（无 fence）。两侧再次不等。

### 根治

step 2 模板必须与 step 3 hook + CLI 输出做到**三方字节一致**：
1. marker 统一为 `AGATE_CARD_START` / `AGATE_CARD_END`
2. 去掉 ` ``` ` fence（CLI 原文直接嵌在两个 marker 之间），或 hook 侧同时 strip fence——推荐前者，更少出错
3. 确认 CLI 输出末尾换行、`sed '1d;$d'` 的边界与模板里 marker 紧贴 CLI 首末行的方式完全对齐

### 为什么这条必须实跑才能收敛

这是字节级 marker/fence 问题——和 `printf '%s'` 回归、P4 鸡生蛋悖论同类，**读伪代码永远看不出**。step 5 的测试计划要显式包含：**用 step 2 模板真生成一份 dispatch-context.md → 塞入 `agate-next-card.sh P3` 的真实输出 → 跑 hook → 断言 hash 相等、commit 成功**。只测「文件生成了」不够，必须测到「hash 相等」这一步。否则实现时这个漏会原样带进代码，且首次真派 subagent 时才炸。

---

## 软观察：诚实降级后，标题相对内容略微超售

F1 诚实降级后，方案 C 明说是「nudge + 防漂移」。那它其实**没回答催生本计划的那个问题**——用户问的是「用 map 又不知道 agent 真读了没」，而降级后的 C 承认它不强制 agent 读、只防止嵌入过期卡片。**C 解决的是「防漂移」，不是「可执行性/强制阅读」，这是两个不同的问题。**

标题「可执行性强化」相对降级后的内容偏乐观。这不是要求回退诚实降级（降级是对的），而是建议：**要么标题据实改为「Phase Card 防漂移 + 信息层完整性」，要么在计划开头一句话点明「本方案在诚实评估后定位为防漂移，真正的强制阅读需 forcing function（未采纳）或 issue #003 后续」**，避免读者（或未来的自己）误以为可执行性已经解决。低优先级，但值得一句。

---

## 建议清单

| # | 建议 | severity |
|---|------|----------|
| 1 | step 2 模板 marker 改为 `AGATE_CARD_START/END`，与 hook 一致（反向传播修复） | 高（会 100% 误拦） |
| 2 | step 2 模板去掉 ` ``` ` fence，CLI 原文直嵌 marker 之间；确保三方字节一致 | 高（会 100% 误拦） |
| 3 | step 5 测试显式断言「模板生成 → 嵌真实 CLI 输出 → hook → hash 相等 + commit 成功」 | 中（验证纪律） |
| 4 | 标题或开头据实标注 C 的真实定位（防漂移，非强制阅读） | 低 |

## 一句话结论

**诚实降级做得漂亮，4/5 真修好。唯一残留是 F3b 的反向传播漏——hook 换了 marker 名，模板没跟上，加上 fence 没去，实现出来仍会 100% 误拦。** 修 step 2 模板让 template↔hook↔CLI 三方字节一致，并让 step 5 的测试真跑到 hash 相等，这个方案就 implementation-ready 了。
