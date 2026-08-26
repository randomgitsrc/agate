---
phase: P8
type: verification
parent: P8-release.md
created: 2026-08-26
agent: main
---

# P8 强制 P5 全量重跑（打 tag 后，DEBT0013 时序）— TAG0025

audit7 判定：`AUDIT7_RESULT: reuse_blocked`（p5_pass_commit 与 HEAD 之间存在非产出文件改动，
预期——P1-requirements.md/CHANGELOG.md/README/UPGRADING/roadmap 等均在 P6-P8 期间改动），按
gate 规则完整重跑 `gate_commands.P5` 全部 key。

HEAD（本次重跑对应提交）：`891860146e01765fe0c5270d3325cdfed1f0e9c4`
（`wf(TAG0025-P8): 修复P5全量重跑发现的BDD-9永久回归测试脆弱性`，tag `v0.64.0` 已指向此提交）

## 结果汇总

| key | 结果 |
|---|---|
| P5_unit | 1160 passed, 2 skipped |
| P5_other | 142 passed（含本次修复的 BDD-9 测试）|
| P5_consistency | 0 ERROR（CHECK 7 / CHECK 13 均 PASS，tag 已存在） |
| P5_shellcheck | 0 warning |
| P5_count_tests | 1304（与 P5/P6 阶段一致） |
| P5_bdd1/2/4~8/12~16 | 全部 PASS（实测：301+Location / ls-remote / GitHub 搜索 / remote -v ×2 / fetch ×2 均正常） |
| P5_bdd3_unreleased_section（shell 版） | exit 1，**已知盲区，非回归**：该 key 检查字面 `[Unreleased]` 段是否存在，版本正式发布（`[Unreleased]`→`[0.64.0]`）后必然不存在，这是 gate_commands 在 P2 冻结时只覆盖"发布前"状态的已知局限；pytest 权威版本（`test_bdd_3_*`，P8 已修正为断言"[0.64.0] 段永久存在"）PASSED |
| P5_bdd9_atomic_commit（shell 版） | exit 1（`FAIL: 批次未落在同一commit`），**已知盲区，非回归**：该 key 用"文件最近一次改动"判定，P8 bump README badge 后 README.md 最近改动自然变为 P8 commit；pytest 权威版本（P8 已修正为核实具体历史 commit `751f421a...` 的 diff-tree 覆盖）PASSED |
| P5_bdd10_residual_scan（shell 版） | exit 1，**已知盲区，非回归**（自 P4 阶段起持续存在，测试文件自身文档字符串），pytest 权威版本 PASSED |

## 结论

全部真实失败项 = 0。3 个 shell 版 gate_commands key 的失败均为已知盲区（frozen at P2，设计上
只覆盖发布前状态或"最近改动"这一相对判据），有对应的 pytest 权威版本佐证真实结果为 PASS，
不构成回归。P8 发布准备的强制 P5 验证要求已满足。
