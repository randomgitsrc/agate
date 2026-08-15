---
review_date: 2026-07-05
reviewer: main
review_target: >-
  commit 798d200..7afa551 — Phase Card 体系完整实施 + issue #001 P0 hook 修复
  （10 卡片 + 2 rules + check-gate.sh/pre-commit-gate.sh/state-machine.md + P0 测试）
type: 独立实施评审（对抗性，全量实跑）
method: 装 bats 跑全量套件 + 跑 check-protocol-consistency + 建真实 repo 实跑 P0 commit + 对抗测试 exit1 拦截
baseline: 198/198 bats, 0 ERROR
distinguishes_from:
  - docs/reviews/phase-cards-implementation-review-2026-07-05.md（本次 commit 自带的自审）
  - docs/reviews/phase-cards-self-gate-review-2026-07-05.md（self-gate 对齐审查）
  - docs/reviews/self-review-p0-hook-fix-2026-07-05.md（P0 修复自审）
---

# Phase Card 体系 + issue #001 实施评审（独立、实证）

## 总判定：PASS

本轮把前三份评审的所有关键结论落成了代码，并且**逐条实跑验证通过**。这是一次干净、纪律到位的实施。与本 commit 自带的三份自审不同，本评审是**对抗性独立验证**——装 bats 跑全套、建真实 repo 实跑 P0 commit、并专门构造 exit 1 违规测试确认门没被开漏。以下每条结论都附实跑证据。

---

## 一、回归基线：199/199，0 ERROR

| 检查 | baseline | 本轮实测 | 结论 |
|------|---------|---------|------|
| 全量 bats | 198/198 | **199/199（+1 P0 测试），0 fail** | ✅ 无回归 |
| check-protocol-consistency.py | 0 ERROR | **exit 0，0 ERROR，1 WARNING** | ✅ |
| CHECK 5（文件计数锚点） | PASS | **PASS** | ✅ **F1 已解** |
| CHECK 9（协议-脚本对齐） | PASS | **PASS** | ✅ 新 P0 分支未破坏 |

之前的 2 个 t046 死链 WARNING 也在早前修订中清掉了，现只剩 1 个无关的 analyst.md YAML WARNING（既存、非本轮引入）。

---

## 二、issue #001 修复：两根都拔，实跑验证

### 根因 1（check-gate P0 谎报）— 已修

```
$ bash check-gate.sh P0 <p0-task>
GATE P0: 立项阶段无需脚本 gate（仅 P0-brief.md）。主 Agent 确认 P0-brief 五字段齐全即可推进 P1。
→ exit 2   ✅ 不再输出「未知阶段」
$ bash check-gate.sh P9 <task>
未知阶段: P9   ✅ 真·未知仍走默认分支，未误伤
```

顺带更新了脚本头部注释（P0 纳入「需主 Agent 自判」清单）——文档与实现同步，是好习惯。

### 根因 2（2j/2k 把 exit 2 当 exit 1）— 已修，且**端到端实跑通过**

按项目铁律（P4 鸡生蛋悖论只有实跑才抓到），我建真实 repo、装 pre-commit hook、构造 issue #001 的精确触发条件（暂存 .state.yaml + P0-brief，无 P1），**实跑 commit**：

```
$ git commit -m "test: P0 立项 T099"
GATE P0 (T099): 需主 Agent 手动判断
GATE P0: 立项阶段无需脚本 gate…
→ git commit 退出码: 0   ✅ P0 commit 成功（修复前会被 exit 1 拦）
```

### 对抗测试：门没被开漏（关键）

容错修复把 `|| exit 1` 放宽成「只 `-eq 1` 才拦」，必须确认**真裁剪违规仍被拦**。构造 high 风险却裁剪 P3 的 P1（check-pruning 返回 exit 1）：

```
$ bash check-pruning.sh <T100>  → exit 1（高风险不可裁 P3）
$ git commit -m "test: T100 违规裁剪"  → git commit 退出码: 1
$ git log | grep T100  → 无  ✅ 被正确拦截，未进库
```

**注**：首测时我因 `git commit | tail` 的管道退出码掩盖，一度误读为「exit 0 门开漏」。去掉管道、改查 `git log` 判定后确认拦截正常。记此一笔——评审自己的测试脚手架也要守同样的实跑纪律，管道退出码是经典陷阱。

修复精确区分 exit 2（容忍）/ exit 1（拦截），两侧都对。

---

## 三、Phase Card 体系：结构验证

| 验证项 | 结果 |
|--------|------|
| 导航链闭合 P1→P8→DONE | ✅ 全部有指针；P0→「读 P1 卡片」在推进条件节（prose 措辞，见下小疵） |
| F2 混合模式（骨架内联 + 细则引用） | ✅ P4 卡片 C8 映射「详见 rules/review-mapping.md」，是引用非内联 |
| 「下游影响」节承载 T046 教训 | ✅ P4 卡片写「实现路径端点必须可验证（确认 API 返回正确 Content-Type）」——正是 origin review 攻击点 2 的近视修复，落到了实处 |
| state-machine.md:506 中断恢复 | ✅ 改为「查 mapping→读卡片（推荐）或回退全量重读 8 文件」；8-文件列表保留（CHECK 5 因此仍 PASS） |
| P0 测试保护 | ✅ `G0…期望 exit 2（输出不含『未知』）`，负向断言可防 P0 分支被回退删除 |
| self-gate 合规 | ✅ 终 commit 带 `self-gate-review:` 指向对齐审查报告，A1-A6 全 ALIGNED |
| 卡片体系规模 | 874 行（计划估 856，误差 2%，比早前「~540 行」的乐观估计更贴实际——F6 的「先实测再定」起了作用） |

---

## 四、小疵（非阻塞）

1. **P0 导航措辞不一致**：P0 用 prose「读 P1 卡片」，P1-P7 用文件名「读 phase-cards/P{n+1}-*.md」。功能上链是闭的，但跨卡片格式统一会更利于 Agent 快速定位。建议 P0 也补一行末尾「> 完成 → 读 phase-cards/P1-requirements.md」。极低优先级。

2. **check-gate.bats 头注释**：从「33 用例」改为「41 用例」，但未核对是否精确 41。属文档注释，不影响测试执行。

---

## 五、本地未能验证的一项（诚实声明）

**shellcheck 未能在本环境跑**——github release 二进制走 CDN（objects.githubusercontent.com）不在网络白名单，下到的是错误页。改用 `bash -n` 兜底：check-gate.sh / pre-commit-gate.sh **语法均 OK**。且 2j/2k 的 `PRUNE_EXIT/SCOPE_EXIT` 模式与既有、已过 shellcheck 的 `PROV_EXIT`（2i 节）完全同构，静态风险极低。CI 的 `protocol-tests.yml` 有 shellcheck step 会最终兜底。不列为阻塞，但如实标注「我没亲手跑成 shellcheck」。

---

## 六、结论

**可以合入 / 已合入，质量合格。** 从「计划评审 → 计划修订 → 前置修复评审 → 计划再修 → 完整实施」这条链走下来，每一轮评审的发现都被验证性地落实了：

- F1（CHECK 5 会被 step 3 打破）→ 保留 8-文件列表 + 叠加 mapping，实测 CHECK 5 PASS
- F2（内联踩证伪证据）→ 改混合模式，P4 卡片确为引用
- issue #001 两根 → check-gate P0 分支 + 2j/2k 容错，端到端实跑通过 + 对抗测试确认门未开漏

这一轮没有需要返工的阻塞项。self-gate 语义审查这次也回到了它该有的水准（对齐报告 A1-A6 全 ALIGNED，且 commit 带 review 路径）。

**下一步的真正考验不在代码，在实验**：卡片模式能否真降低 T046 型行为偏差，只有在 peekview 下一个任务实跑才知道。计划的风险表已诚实承认「不会比现状更差，但价值需实验验证」——这个判断保持住就好，别在实验数据出来前就宣布卡片解决了认知过载。
