=== Review session start 2026年 08月 10日 星期一 01:14:48 CST ===
read P2-design.md full (649 lines)

=== FINDING: scripts/README.md NOT updated ===
P2-design.md FIND-8 (line 636-640) explicitly requires: scripts/README.md:68 工具清单表 agate-md-field-get.py 条目同步新增 op 清单 + 双读语义.
Actual diff: agate/scripts/README.md NOT in changed file list (git diff 293924f..HEAD --name-status -- agate/scripts/README.md returns empty).
File content check: agate/scripts/README.md:68 still reads "| `agate-md-field-get.py` | P1/P2 提取 risk_level/ui_affected/phases | 无 |" -- no mention of frontmatter/双读/new ops (candidate_count, packages, domains, override, blocker_count etc).
This is a design-declared doc-sync commitment (FIND-8) that was NOT implemented. Candidate for A2/A5 MISALIGNED or gap.

=== FINDING: test-plan doc (docs/archived/plans/agate-test-plan-2026-07-01.md) also not updated per FIND-8 but out of agate/ diff scope (docs/) - note for A5 only, not A1/A2 (out of review scope per dispatch constraint 1, but design explicitly committed to this)
read P4-implementation.md full (491 lines, 4 DESIGN_GAP declared + 1 undeclared regression note in flow D, later fixed by fixture commit per dispatch objective_info 600/600)

=== starting fresh bats run for A4 ===

=== Verification results ===
bats full suite (fresh run): 600 ok, 0 not ok (agate/tests/unit + regression + integration + sanity.bats)
count-tests.sh: 594 (matches P2 baseline claim)
check-protocol-consistency.py: CHECK 1-9 all PASS, 0 ERROR
shellcheck -S warning agate/scripts/*.sh: empty output, 0 warnings
CHECK 9 SCRIPT_ALIGNMENT_ANCHORS AST count: 38 (confirmed via python ast parse)
agate/scripts/check-*.sh count on disk: 12 (was 11 pre-diff, now includes check-frontmatter.sh)
SG.6 test title still says "全部 11 个" but test body is dynamic (find-based), so still passes - cosmetic staleness only, pre-existing test file not touched by this diff, out of formal review scope but noted.

=== DESIGN_GAP verification (4 declared in P4-implementation.md) ===
1. check-gate.sh:173 FIELD_COUNT grep unchanged (P2 branch not migrated to double-read) - CONFIRMED matches DESIGN_GAP declaration, coincidental grep compat via frontmatter top-of-file positioning
2. check-pruning.sh unchanged entirely (git diff empty) - CONFIRMED, HAS_OVERRIDE grep '^override:' at line ~24 works coincidentally
3. check-gate.sh P6 branch fallback regex uses '^\s*- (PASS|FAIL)\b.*BDD-[0-9]' (permissive, not the strict '^\s*- (PASS|FAIL) BDD-[0-9]' from design) - CONFIRMED at check-gate.sh, differs intentionally from check-p6-provenance.sh:142 P6_BODY_STRICT which DOES use the strict form matching design verbatim. Both AND-semantics (P6: pass&&fail both non-empty; P7: blocker_count&&deviation_critical_count both non-empty, design_gap_count&&reviewed both non-empty) confirmed at check-gate.sh:277-278,313-314,332-333 (approx).
4. check-changelog.sh removed grep -qF "$TASK_ID" fallback (design said "保留") - CONFIRMED removed, replaced with comment explaining CL.7 conflict. check-changelog.sh:36 comment present.

=== New findings beyond declared DESIGN_GAPs ===
FINDING 1: agate/scripts/README.md:68 NOT updated despite P2-design.md FIND-8 (lines 636-640) explicitly committing to update it ("agate-md-field-get.py 条目描述同步：新增 op 清单 + 双读语义"). Actual content still: "| `agate-md-field-get.py` | P1/P2 提取 risk_level/ui_affected/phases | 无 |" - stale, doesn't mention frontmatter/双读/new ops (17 new ops added).

FINDING 2: agate/dispatch-protocol.md has ZERO mentions of "frontmatter" (grep confirmed empty) despite dispatch-protocol.md being in the changed-files list (only task_id T00X->TAGX example updates were made, flow D). The "P5/P6 派发时追加" dispatch prompt template block (lines ~537-553) that gets copy-pasted into actual P6 dispatch-context still only mentions "- PASS/FAIL BDD-N" line format, doesn't instruct verifier to also write pass:/fail:/ui_affected: into frontmatter (BDD-16 requirement). Role file verifier.md DOES have this (execution-roles/verifier.md updated per BDD-24), so not a hard blocker, but the machine-copyable dispatch template itself is incomplete - a real content propagation gap per the role's own reverse-propagation table entry "dispatch-protocol.md（P6 结果格式 + gate 表）".

FINDING 3: agate/WORKFLOW.md:78-79 "任务目录命名约定" section examples "docs/tasks/T001-mcp-namespace-map/" and "docs/tasks/T002-fix-db-migration/" use OLD task_id format (T + 3 digits, no 2-letter project code), which now FAILS the flow-D hard-cut regex ^T[A-Z]{2}\d+$ enforced by agate-state-yaml-check.py:39. P4-implementation.md's flow D file list (state-machine.md/dispatch-protocol.md/role-system.md/active-tasks-template.md) explicitly did NOT include WORKFLOW.md. This is a genuine reverse-propagation miss flagged by dispatch instruction point 6.

FINDING 4 (A7-relevant): agate/adr.md has no ADR for the frontmatter-vs-independent-yaml-file architectural choice (P2-design.md §1 candidate A vs B, a real architecture decision with documented trade-off matrix). No new ADR added. adr.md diff confirmed empty.

FINDING 5 (A5-relevant, minor): agate/CONTEXT.md term glossary not updated with new terms (frontmatter block, presence语义, 双读 dual-read). Diff confirmed empty for CONTEXT.md. Not blocking (glossary is a "补充入口" not authoritative), but a completeness gap.

FINDING 6 (A5-relevant, minor): agate/LIMITATIONS.md not updated with an explicit boundary note that "structuring improves parseability, not truthfulness" (P2-design.md §10 declares this boundary at the task level but doesn't propagate to the protocol-level LIMITATIONS.md, where 局限3 already discusses self-authored gate risk - natural fit but not done). Diff confirmed empty for LIMITATIONS.md.

=== A6 anchor table check ===
38 anchors confirmed via AST count. New entry at check-protocol-consistency.py:631-637 for check-frontmatter.sh with desc/script/keywords/callers. check_anchor_coverage (dynamic, SG.6 test) confirms coverage of all 12 check-*.sh + pre-commit-gate.sh. Flow B/C/D correctly reused existing anchors for check-gate.sh/check-p6-*.sh/check-changelog.sh/agate-state-yaml-check.py per P2 §3.1.4 claim - verified no new anchors needed for those (their keywords like "BDD-[0-9]"/"CHANGELOG"/"task_id" still present and functioning, confirmed via CHECK 9 PASS).

FINDING 7: agate/tests/README.md coverage table (lines 28-64) missing row for check-frontmatter.sh / unit/check-frontmatter.bats (11 @test). Table has rows for all other check-*.sh scripts including similar-size ones (check-scope-resolved.sh: 11 tests). Diff confirmed empty for tests/README.md. README.md:79 explicitly states rule "协议文档声明新规则 → 必须新增对应 .bats 用例" (implying this table should track it), and this maintenance doc's own stated purpose is violated by the omission.

=== CHANGELOG.md check (non-issue) ===
CHANGELOG.md unreleased/latest entry is [0.35.0], no T001 entry yet. Confirmed via state-machine.md:221/dispatch-protocol.md:836/WORKFLOW.md:242 that check-changelog.sh only runs at P8 phase (not P4). T001 currently at P4, so absence of CHANGELOG entry is EXPECTED, not a gap. Not counted as finding.

=== Review complete, proceeding to write final report ===
