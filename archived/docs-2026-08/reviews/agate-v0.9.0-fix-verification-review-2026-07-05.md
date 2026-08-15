---
review_date: 2026-07-05
reviewer: main
review_target: >-
  commit 0276200..780b6c6 — 收窄 dispatch-context 强制化范围（仅产出 commit）+ 测试修复
  回应 v0.9.0 发布评审的 6 失败
type: 修复验证评审（对抗性，双向实跑）
method: 全量 bats + 对抗双向（产出 commit 拦 / 非产出放行）+ 核对 v0.9.0 tag 现状
prior_review: docs/reviews/agate-v0.9.0-release-review-2026-07-05.md
---

# v0.9.0 修复验证评审

## 总判定：代码修复干净且正确（已双向实证），但 release 未闭合——v0.9.0 tag 仍指向红 commit

强制化范围收窄成"仅产出 commit"，6 个失败全修、无回归、对抗双向通过。这是正确的修复。但我上一份评审建议 #1（回退/补发 v0.9.1）**只做了一半**：main 绿了，**v0.9.0 这个已发布 tag 仍指向 476224d（6 失败）**。发布事故在补 tag 之前技术上没关闭。

---

## 一、修复正确性：双向对抗实证

**收窄逻辑**（pre-commit-gate.sh）：仅当该阶段的**产出文件**被 staged 时才要求 dispatch-context：

```bash
STAGED_IN_TASK=$(git diff --cached --name-only | grep "^${TASK_REL}/")
case "$PHASE" in
    P1) PHASE_OUTPUT="P1-requirements\.md" ;;
    P2) PHASE_OUTPUT="P2-design\.md" ;;
    P3) PHASE_OUTPUT="P3-test-cases\.md" ;;
    P6) PHASE_OUTPUT="P6-acceptance\.md" ;;
esac
# staged 含产出文件 → 要求 dispatch-context；否则放行
# P4: 用代码文件（非 .md/.yaml/.state）判断
```

注释明确"中间 commit / legacy 任务 / 裁剪跳阶 → 不强制"。这正是发布评审建议的"产出 commit"语义。

**对抗双向实跑**（建真实 repo）：

| 场景 | 期望 | 实测 |
|------|------|------|
| P2 产出（staged P2-design.md）无 dispatch-context | 拦 | ✅ exit 1「派发阶段产出 commit 需提供 P2-dispatch-context.md」 |
| P2 非产出（仅 staged note.txt + .state.yaml） | 放行 | ✅ exit 0 |
| 中间/legacy commit（无产出文件 staged） | 放行 | ✅ |

**barrier 没被收没**——它精确地在"产出文件被 staged"时触发，其余放行。这是正确的语义：完成派发阶段的产出时必须经过卡片，中间步骤不干预。

**回归**：全量 bats **221/221，0 fail**（v0.9.0 时是 215/6-fail）；consistency 0 ERROR。IT.2/6/7/8/9/10 全绿。

---

## 二、未闭合：v0.9.0 tag 仍是红发布

```
v0.9.0 → 476224d
实测该 commit 集成套失败数：6（仍是那个红发布）
修复在 main：780b6c6（全绿）
```

代码修好了，但**发布的 v0.9.0 还是坏的**——任何人 `git checkout v0.9.0` 拿到的是 6 失败的版本。发布评审建议 #1 是"回退/补发 v0.9.1，发版前 bats 必须绿"，目前只做了"让 main 绿"，没做"补一个绿的发布"。

**必须做**：cut **v0.9.1** 指向当前绿 HEAD（干净），或移动 v0.9.0 tag（已发布 tag 强移一般不推荐，且 CHANGELOG 已记 v0.9.0，移动会造成 tag 与 changelog 历史错位——不建议）。**推荐 v0.9.1。**

顺带：v0.9.1 的 CHANGELOG 应记这次 scope narrowing 是对 v0.9.0 的 hotfix，让"v0.9.0 曾短暂红过"这件事在历史里可追溯——这本身也是诚实文档的一部分，别把红发布悄悄抹掉。

---

## 三、结论

**代码层面：干净的正确修复**，收窄语义合理、对抗双向验证、全绿无回归。强制化从"派发阶段任何 commit"收窄到"产出 commit"，既保住 barrier 又消除误伤——这是对发布评审的到位回应。

**发布层面：还差最后一步**。main 绿 ≠ 发布好。v0.9.0 tag 仍指向红 commit，事故要到 **v0.9.1 补发（前置全绿 gate）** 才算真正关闭。这也正是发布评审的核心教训：发布是最高风险的门，绿的判据是 tag 指向的 commit 全绿，不是 main 全绿。

**一句话**：修得对，但"发布"这件事没做完——补 v0.9.1，且把发版前"全量 bats 绿"固化成硬 gate，别再让 tag 指向红 commit。
