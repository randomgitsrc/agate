---
review_date: 2026-07-05
reviewer: main
review_target: >-
  commit b0fb461..bbcf5d8 — step 1 (agate-next-card.sh) + step 2-3 (dispatch-context 模板 + hook hash 校验)
  + dispatch-context 强制化 plan
type: 独立实施评审（对抗性，跨环境实跑）
method: 装 bats 全套 + 端到端造 dispatch-context 跑 hook（同环境）+ 跨 checkout 路径实测 + 篡改对抗
baseline: 198/198 bats, 0 ERROR
prior_reviews:
  - docs/reviews/agate-phase-card-enforceability-revision-review-2026-07-05.md（F3b marker/fence）
  - docs/reviews/agate-step2-3-self-gate-review-2026-07-05.md（本 commit 自审：A1-A6 全 ALIGNED PASS）
---

# step 1 + step 2-3 实施评审（独立、跨环境实证）

## 总判定：PASS，但有一个 blocking 可移植性缺陷——必须在「强制化 plan」落地前修

marker/fence 陷阱（前评审 F3b）**确实解决了**，防漂移核心**同环境实跑通过**、篡改能拦。但 CLI 把**绝对路径**写进了被 hash 的内容，导致 hash 依赖环境——**同一份卡片在不同 checkout 路径下 hash 不同**。今天危害有限（dispatch-context 还是可选 nudge），但排队中的强制化 plan 会让它对每个 P2/P4 commit 生效，那时这个缺陷会在 fresh clone / CI / 队友机器上**逐个误拦**。

自审报告标了「A1-A6 全 ALIGNED PASS」——它没抓到这个，因为测试是**同环境** generate + verify。这正是独立跨环境评审的价值。

---

## 一、验证通过的部分

| 检查 | 结果 |
|------|------|
| 全量 bats | **218/218**（+20：agate-next-card + dispatch-context-card 两套），0 fail |
| consistency | 0 ERROR |
| marker/fence（前 F3b） | ✅ 模板用 `AGATE_CARD_START/END`、禁 fence；hook `sed '1d;$d'` 对称去 marker |
| 同环境端到端 | ✅ CLI 原文嵌模板 → hook 校验 → **hash 相等**（9b8c83e…=9b8c83e…）→ commit 通过 |
| 篡改对抗 | ✅ 改嵌入卡片一个字 → hash mismatch → 拦截（防漂移生效） |
| self-gate 纪律 | ✅ 每 feat 后跟 alignment/hardening review |

**同一 checkout 内，这套机制是工作的。** F3b 的字节级尾巴收干净了：EMBEDDED（`sed` 区间 + 去首尾 marker）与 EXPECTED（CLI 原文）在同环境下逐字节相等。测试也确实端到端跑到了 hash 相等这一步——比"文件生成"扎实。

---

## 二、F1（blocking）：CLI 绝对路径进 hash → 跨 checkout 必然误拦

CLI 第 68 行：

```bash
printf '## 当前阶段卡片：%s\n\n路径：%s\n---\n' "$PHASE" "$CARD_FILE"
```

`$CARD_FILE` = `$AGATE_REPO/agate/phase-cards/P3-tdd.md`——**绝对路径**。这行进了被 hash 的内容。

**跨 checkout 实测**（把 repo 复制到两个路径，各调 CLI）：

```
/tmp/dctest/agate/phase-cards/P3-tdd.md   → hash 6f1c1b5e…
/tmp/dctest2/agate/phase-cards/P3-tdd.md  → hash 55ad927b…
```

**同一份卡片、两个 checkout 路径 → 两个不同 hash。**

### 触发场景

dispatch-context.md 是**提交进 git 的 artifact**，里面 baked 了生成时那台机器的绝对路径。之后：

- **队友 / fresh clone**：Alice 在 `/home/alice/agate` 生成并提交（本地 hook 过）。Bob 在 `/home/bob/agate` clone 后，只要 P3 任务还在、他 commit 任何东西，hook 的 2p 段（`[ -f "$DC_FILE" ]` 命中）重跑 CLI 得到 `/home/bob/…` → 与嵌入的 Alice 路径 mismatch → **Bob 被误拦**。
- **CI**：checkout 到 `/github/workspace` 或 `/home/runner/work/…`，与提交者本地路径不同 → 若 CI 重跑该 gate 段 → mismatch。

### 为什么测试没抓到

218 个测试全在**同一环境** generate + verify，绝对路径两侧一致，hash 自然相等。**跨环境才暴露**——正是前几轮反复强调的字节级跨环境脆弱性：同环境看着好，换机器炸。

### 修法（trivial）

CLI 的 `路径：` 改为**仓库相对路径**：

```bash
REL="${CARD_FILE#$AGATE_REPO/}"   # → agate/phase-cards/P3-tdd.md
printf '## 当前阶段卡片：%s\n\n路径：%s\n---\n' "$PHASE" "$REL"
```

相对路径既保留可读信息、又让 hash 跨 checkout 稳定。或者：把 header（标题 + 路径）排除在 hash 之外，只 hash 卡片正文——但相对路径是最小改动。

### 必须配一个跨环境测试

修完加一条：**在路径 A 生成 dispatch-context，从路径 B 跑 CLI，断言两者 hash 相等**。否则这个缺陷会无声回归——现有同环境测试永远绿。

---

## 三、F2（序列 blocking）：强制化 plan 不能先于 F1 落地

新计划 `dispatch-context-mandatory` 把 dispatch-context 对 **P1/P2/P3/P4/P6 变成强制**（缺则 exit 1）——这是把 nudge 变 barrier，方向完全正确，正是 enforceability 评审建议的 forcing function，序列也对（先诚实降级、再单独强制化）。

**但它放大 F1 的爆炸半径**：强制化后，每个派发阶段 commit 都**必须**有一个 hash 匹配的 dispatch-context。叠加 F1 的绝对路径问题 → **每个 fresh clone / CI / 队友机器上的 P2/P4 commit 都会误拦**。今天 F1 只是"可选功能偶发失效"，强制化后变成"协作/CI 全面阻塞"。

**建议顺序**：① 修 F1（相对路径）② 加跨环境测试 ③ 再落强制化 plan。别把顺序颠倒。

---

## 四、结论

**同一 checkout 内实现是对的、扎实的**：marker/fence 解决、端到端 hash 校验通、篡改能拦、测试跑到 hash 相等。**但 hash 因绝对路径而不可移植，这是 blocking**——尤其考虑到强制化 plan 已在门口，它会把这个缺陷从"偶发"放大成"协作/CI 阻塞"。

修 F1 是 3 行改动（绝对→相对路径）+ 1 条跨环境测试。修完，这套防漂移机制才真正 production-ready、才能安全地被强制化 plan 依赖。

**过程注记**：本 commit 自审（step2-3-self-gate-review）标 A1-A6 全 ALIGNED，是诚实的——在它的测试范围（同环境）内确实对齐。缺的是"跨环境"这个维度。建议把"跨 checkout / CI 路径一致性"加进 A5（下游影响）的检查清单——hash 校验类机制天然有环境依赖风险，值得成为固定审查项。
