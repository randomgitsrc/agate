---
review_date: 2026-07-05
reviewer: main
review_target: >-
  commit ac0e10e..476224d + tag v0.9.0 — 强制化 dispatch-context + self-gate ^ 锚修复 + 发版
type: 发布评审（对抗性，全量实跑）
method: 全量 bats + 复现失败 commit + 核对 CI 是否跑该套 + 确认失败前置绿
severity: HIGH — 已 tag 的发布带 6 个失败测试
---

# v0.9.0 发布评审

## 总判定：STOP — v0.9.0 带 6 个失败测试发布，CI 配置能抓到（红着发版）

强制化（f53e4cc）打破了 6 个集成测试，而 v0.9.0 在这个红状态下被 tag 发布。这是 memory 里「commit 声称 152/152 全过、实际 17 失败」的**同型事故重演**——发布这个最高风险的门，没有 gate 在绿套件上。self-gate ^ 锚修复和 F1 相对路径都是对的（已验证），但发版本身必须回退/补发。

---

## 一、发布事故：6 个失败，CI 红

**全量 bats（发版 HEAD 476224d）**：

```
215 ok / 6 not ok
not ok IT.2  pre-commit-hook phase 变更 + gate 通过
not ok IT.6  多任务：任务级 .state.yaml + P1 产出 → 正常 commit
not ok IT.7  多任务：P4 产出但 phase 仍 P3 → WARNING 不拦截
not ok IT.8  多任务：phase 变更无产出 → 不拦截不 WARNING
not ok IT.9  多任务：裁剪跳阶 P2→P5 无 P3/P4 产出 → 不拦截
not ok IT.10 向后兼容：根 .state.yaml 仍工作
```

**CI 配置会抓到**：`.github/workflows/protocol-tests.yml:22` = `bats agate/tests/integration/`。所以 CI 在 v0.9.0 上是**红的**——这不是"CI 漏跑"，是"红着 tag"。

**前置确认是绿的**：上一个 commit ac0e10e（F1 修复）我实测 219/219 全绿。所以是本次范围内的 f53e4cc 打破的，非既存问题。

---

## 二、根因：强制化 gate 了"派发阶段的每一个 commit"，范围过宽，且测试未同步

强制化（f53e4cc，pre-commit-gate.sh:146）：**P1/P2/P3/P4/P6 阶段的 commit 必须有 `{PHASE}-dispatch-context.md`，否则 exit 1。**

**实跑复现**：

```
$ git commit -m "test: P1 无 dispatch-context"   # P1 产出，无 dispatch-context
GATE: subagent 派发阶段需提供 P1-dispatch-context.md（当前阶段卡片嵌入）
→ exit 1
```

6 个失败测试全是在这些阶段 commit 且没有 dispatch-context 的场景。它们分两类：

1. **本该更新的测试**（IT.2/IT.6）：测"P1 产出 → 正常 commit"。强制化后确实需要 dispatch-context，测试 fixture 需补一个。
2. **被误伤的无关测试**（IT.7/IT.8/IT.9/IT.10）：它们测的是 **WARNING-不拦截 / 裁剪跳阶 / 根 .state.yaml 向后兼容**——**与 dispatch-context 无关**，只是恰好在这些阶段 commit，就被强制化在前面拦住了，根本走不到它们要测的行为。

第 2 类暴露一个**设计问题**：强制化 gate 的是"派发阶段的**任何** commit"，而非"派发阶段的**产出/完成** commit"。这意味着在 P1-P4/P6 期间你**任何**中间 commit 都必须先有一个 dispatch-context——包括：

- **legacy 根 .state.yaml 任务**（IT.10）：老布局的任务在派发阶段也被强制，向后兼容被破坏（讽刺的是这个测试的名字就叫"向后兼容"）。
- **测别的行为的 commit**（IT.7-9）：只是路过这些阶段就被拦。

强制"完成派发时必须经过卡片"是合理的 barrier；但强制"这些阶段的每一次 commit 都要有 dispatch-context"范围过宽。这也是 IT.7-9 被误伤的根源。

---

## 三、正面（已验证，别在返工里丢）

| 项 | 验证 |
|----|------|
| self-gate `^` 锚假阴性修复（memory 里的老问题，终于修） | ✅ body 提及不再绕过；行首正常识别 |
| F1 相对路径在强制化实现中未回退 | ✅ CLI 仍输出 `路径：agate/phase-cards/P2-design.md` |
| consistency | ✅ 0 ERROR |
| 强制化方向 | ✅ nudge→barrier 是对的（enforceability 评审建议的 forcing function） |
| 防漂移 hash 校验（同环境） | ✅ 仍工作 |

强制化**方向对**——问题不在"要不要 barrier"，在"barrier 的触发范围过宽 + 发版没跑测试"。

---

## 四、必须做的

1. **回退 / 补发**：v0.9.0 不应停在红状态。要么 re-tag，要么尽快 v0.9.1，且**发版前全量 bats 必须绿**。
2. **收窄强制化范围**：把触发从"派发阶段的任何 commit"改为"派发阶段的**产出 commit**"（例如：仅当该阶段的产出文件被 staged 时才要求 dispatch-context），或显式排除 legacy 根 .state.yaml 布局。这能修掉 IT.7/8/9/10 的误伤。
3. **同步更新真正相关的测试**（IT.2/IT.6）：补 dispatch-context fixture，让它们覆盖新 barrier。
4. **发版 gate**：release commit 的 `self-gate-skip: 版本 badge + CHANGELOG 整理` 把发版描述成纯 cosmetic，但 v0.9.0 的范围含 f53e4cc 这个 breaking feat。**发版 skip 不能免测**——发版恰恰是最该跑全绿套件的时刻。建议：release 前置一步"全量 bats 绿 + consistency 0 ERROR"作为硬 gate。

---

## 五、一句话结论

**强制化方向对、`^` 锚和 F1 修复都对，但 v0.9.0 红着发版了**——f53e4cc 把 barrier 的范围铺到"派发阶段的每个 commit"，打破 6 个集成测试（含 4 个无关误伤 + 讽刺的"向后兼容"测试），而发版没跑套件。这正是项目最该守住、也曾栽过的那条线："systematic quality gates over feature velocity"。**收窄触发范围 + 补测试 + 发版前跑绿，再出 v0.9.1。**
