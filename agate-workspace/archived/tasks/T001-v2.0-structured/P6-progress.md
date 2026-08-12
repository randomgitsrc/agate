# P6 验收进度（重跑 retry1）

开始时间: 2026-08-10
角色: verifier subagent

已读输入文件：
- verifier.md 角色定义
- P6-dispatch-context-verifier-retry1.md
- P6-dispatch-context-verifier.md（上一轮完整指引）
- P6-gate-diagnosis.md（BDD-17 诊断）
- P1-requirements.md（28 条 BDD 全文）
- P2-design.md §9/§10
- P3-test-cases.md 全文
- P4-implementation.md 全文
- P5-test-results-retry1/unit.md 全文（603/603，597 基线）

开始逐条验收 BDD-1..28。

## 完成

28 条 BDD 全部独立实跑验收（27 PASS / 1 FAIL）。
- FAIL: BDD-11（count-tests.sh 实测 597，BDD-11 原文字面要求 594）
- 重点复核 BDD-17：3 组独立构造 fixture 复现原始 bug 场景，确认 worktree 的
  check-p6-format.sh --fix 修复真实有效，frontmatter 不再被破坏。
- 重要发现：执行派发指引给出的自查命令（bash ~/.agate/scripts/check-p6-format.sh --fix）
  时，~/.agate 里的旧版本脚本（无 P4 修复）真的把本文件自己的 frontmatter 破坏了一次
  （与 BDD-17 bug 现象一致）。已现场修复，并改用 worktree 自身已修复的脚本做最终格式
  自查。已在 P6-acceptance.md 顶部专门记录这个操作风险，供主 Agent 处理真实 commit 时
  注意 AGATE_ROOT 指向。
- 自查 3 件套：check-p6-format.sh --check/--fix（worktree，EXIT 0，idempotent）、
  check-p6-evidence.sh（~/.agate，EXIT 0）、check-p6-provenance.sh（~/.agate 与
  worktree 双跑，EXIT 0）。中途一次 check-p6-provenance.sh 报"1 个证据文件未被 PASS
  行引用"，定位到是 bdd11-test-count.md 只被 FAIL 行引用（provenance 脚本只扫 PASS
  行的引用）——已将该文件内容折叠进 P6-acceptance.md 正文的"BDD-11 补充说明"节，不再
  作为独立证据文件，问题解决。

产出：
- docs/tasks/T001-v2.0-structured/P6-acceptance.md
- docs/tasks/T001-v2.0-structured/P6-evidence/（11 个文件）

## 主 Agent 二次指示处理（2026-08-10）

1. 已去掉 P6-acceptance.md frontmatter 的 pass:/fail:/ui_affected: 三个 dogfood 字段，
   只保留 v0.35 通用 Header 字段。独立复核：用 ~/.agate（未修复版）check-p6-format.sh --fix
   重跑，md5 前后完全一致（EXIT=0，无改动）——确认风险已从根本消除，而非绕过。
2. P1-requirements.md 已见 BDD-11 的 [BASELINE_CHANGE: 594→597] 正式标注（主 Agent
   2026-08-10 批准）。独立重跑 count-tests.sh 确认仍为 597，满足新基线，BDD-11 改判 PASS。
   bdd11-test-count.md 证据文件已重写为 PASS 依据（含判定变更过程说明）。
3. 正文汇总已更新为 28 PASS / 0 FAIL。check-p6-evidence.sh / check-p6-provenance.sh
   （~/.agate 与 worktree 双跑）/ check-p6-format.sh --check 全部 EXIT=0。
