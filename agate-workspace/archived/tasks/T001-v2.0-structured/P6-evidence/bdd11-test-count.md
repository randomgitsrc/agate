# BDD-11 — 测试用例数不漂移：本次验收判定 PASS（新基线 597，主 Agent 已批准）

## 客观事实（独立重跑，非引用旧记录）
```
  integration/pre-push-hook.bats                       3 个 @test
  integration/protocol-alignment-review.bats           8 个 @test
===
总计：597 个测试用例

如果此数字与 docs/plans/agate-test-plan-2026-07-01.md 附录 A 不一致
→ 文档漂移，需要更新。
如果文档改了但 .bats 文件没动 → 测试计划空头支票。
```

独立复核确认：`count-tests.sh` 实测输出 **597**（不含 sanity.bats 6）。

## P1-requirements.md 基线变更记录（独立重新读取核实存在）
```
#### BDD-11: [流 A] 测试用例数不漂移
- Given v2.0 改造完成后的 worktree
- When 运行 count-tests.sh
- Then 输出 594 个测试用例（sanity.bats 6 另计），与改造前基线一致

[BASELINE_CHANGE: 594 → 597。P6 第一轮验收（27 PASS/1 FAIL）发现 check-p6-format.sh --fix 破坏
frontmatter 的真实 bug（BDD-17），已退回 P4 定向修复并新增 3 条回归测试
（F_P6FMFIX.1/2/3，agate/tests/unit/check-p6-format.bats），修复后 count-tests.sh 实测 597。
这是"发现新 bug 后新增测试覆盖"，不是删减式漂移或范围膨胀——3 条新增用例均已被 P6 verifier
独立核实真实覆盖该 bug 场景（非摆设），且 P4 修复本身已过独立 self-gate 语义审查（ALIGNED，
docs/reviews/agate-alignment-review-2026-08-10.md 增量审查节）。本条 BDD 原文"594"是 P1 基线
制定时的现状快照，未预见到验收过程本身会暴露并修复一个此前从未被测试覆盖的真实缺陷；
"不漂移"的精神实质（测试数不应无理由减少/膨胀）在 597 下依然成立。
主 Agent 批准：2026-08-10，判定依据见上。后续 BDD-11 验收按新基线 597 判定。]
```

## 判定：PASS

本次 P6 验收（第 2 次派发）首轮独立核实时，BDD-11 原文字面要求 594、实测 597，按字面判定过 FAIL。
主 Agent 复核该发现后，认定差值 +3（F_P6FMFIX.1/2/3）是 P4 修复 BDD-17 真实 bug 时新增的合法回归测试，
非删减式漂移，已批准在 P1-requirements.md 给 BDD-11 追加 [BASELINE_CHANGE: 594 → 597] 正式标注（2026-08-10）。
本次复核 count-tests.sh 实测值仍为 597，与新基线一致，判定改为 PASS。

本条 PASS 判定的变更过程（FAIL → PASS）本身即是验收纪律的体现：先如实报告字面不符，
由主 Agent 走正式的基线变更流程批准后，再据新基线重新判定，而非验收方自行放宽标准。
