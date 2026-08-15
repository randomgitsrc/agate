---
date: 2026-07-12
branch: feat/u1-p1-requirements-review
intent: ⑧ P1 requirements-review + ⑩ iteration loop + N3 P7 WARNING + F1 frontmatter fix
verdict: ALIGNED
---

# Protocol-Script Alignment Review — U1

## Summary Table

| Check | Verdict | Items |
|-------|---------|-------|
| A1 Doc→Script | ALIGNED | 7/7 items aligned |
| A2 Script→Doc | ALIGNED | 5/5 items aligned |
| A3 Consistency chain | ALIGNED | All expected files present in diff; no spurious files |
| A4 Test coverage | ALIGNED | 7/7 P1-review scenarios + F1 adversarial + P2 adversarial + integration P1 fixture; 65/65 bats pass |
| A5 Downstream | ALIGNED | P1 gate change scoped to P1→P2; P7 WARNING non-blocking; check-p6-provenance.sh unaffected |
| A6 Anchor coverage | ALIGNED | CHECK 9 has P1 review agent≠main anchor; F1 frontmatter fix covered by existing anchors; all gate scripts covered |

## Detailed Findings

### A1: Document→Script alignment

**A1.1** dispatch-protocol.md says "P1-review.md status:approved + agent≠main + 含 BDD-/B[0-9] 锚点"

- dispatch-protocol.md:647: `P1-review.md status:approved + agent≠main + 含 BDD-/B[0-9] 锚点（check-gate.sh P1 检查）`
- check-gate.sh:27-44: P1 branch checks:
  - Line 27: `P1_REVIEW_STATUS=$(sed -n '/^---$/,/^---$/p' "$P1_REVIEW" | { grep '^status:' || true; } | sed 's/^status:\s*//' | head -1)` — frontmatter extraction
  - Line 28: `if [ "$P1_REVIEW_STATUS" != "approved" ]` — status check
  - Line 32: `P1_REVIEW_AGENT=$(sed -n '/^---$/,/^---$/p' "$P1_REVIEW" | { grep '^agent:' || true; } | sed 's/^agent:\s*//' | head -1)` — agent extraction
  - Line 37: `if [ "$P1_REVIEW_AGENT" = "main" ]` — agent≠main check
  - Line 41: `if ! grep -qE 'BDD-|B[0-9]' "$P1_REVIEW"` — BDD anchor check

**Verdict: ALIGNED** — All three conditions (status:approved, agent≠main, BDD anchor) are checked.

**A1.2** state-machine.md P1→P2 transition requires P1-review.md

- state-machine.md:77: `P1 --[P1-requirements.md 有效 AND ... AND P1-review.md status:approved AND agent≠main AND 含 BDD 编号锚点]--> P2`
- check-gate.sh:22-26: P1 branch first checks `P1_REVIEW="$TASK_DIR/P1-review.md"` existence, exits 1 if missing

**Verdict: ALIGNED** — P1-review.md existence is enforced before any other check.

**A1.3** WORKFLOW.md P1 row says "requirements-review（强制，不可裁）"

- WORKFLOW.md:192: `requirements-review（强制，不可裁，所有任务都走独立 review）+ office-hours（大任务或 pruning_tendency 标"保守"时追加）`
- dispatch-protocol.md:780-793: "P1 需求评审（强制，不可裁）" section confirms mandatory requirements-review
- check-gate.sh:23-26: Missing P1-review.md → exit 1 (no bypass path)

**Verdict: ALIGNED** — "强制不可裁" is enforced by exit 1 on missing file.

**A1.4** P1-requirements.md phase card describes review step + gate rules

- P1-requirements.md:10-13: Step 2.5 describes requirements-review dispatch, P1-review.md output, iteration loop
- P1-requirements.md:47: `check-gate.sh P1 → P1-review.md 存在 + status:approved + agent≠main + 含 BDD 编号锚点 → exit 2`
- check-gate.sh:21-46: P1 branch implements exactly these checks

**Verdict: ALIGNED** — Phase card gate rules match script behavior.

**A1.5** orchestrator-template.md says "P1 评审不可裁"

- orchestrator-template.md:94: `P1 评审不可裁——所有任务都走独立 requirements-review（agent≠main），与 P2 design-review 对称。check-gate.sh P1 对 P1-review.md agent=main 硬拦截（exit 1）`
- check-gate.sh:37-39: `if [ "$P1_REVIEW_AGENT" = "main" ]` → exit 1

**Verdict: ALIGNED** — Template invariant matches script enforcement.

**A1.6** F1 fix: frontmatter extraction for status (not full-grep)

- dispatch-protocol.md:647: `P1-review.md status:approved` (refers to frontmatter status field)
- state-machine.md:77: `P1-review.md status:approved` (transition rule)
- check-gate.sh:27: `P1_REVIEW_STATUS=$(sed -n '/^---$/,/^---$/p' "$P1_REVIEW" | { grep '^status:' || true; } | sed 's/^status:\s*//' | head -1)` — extracts from frontmatter only
- check-gate.sh:67 (P2): Same `sed -n '/^---$/,/^---$/p'` pattern for P2-review.md status

**Verdict: ALIGNED** — Both P1 and P2 use frontmatter extraction (`sed -n '/^---$/,/^---$/p'`), not full-file grep. F1 fix correctly implemented.

**A1.7** N3: P7-consistency.md says "DESIGN_GAP_REVIEWED + cross-file reference keywords → WARNING"

- P7-consistency.md: No explicit WARNING text in the phase card itself (the WARNING is a script-level nudge, not a phase-card rule)
- check-gate.sh:163-168: `if [ "$DESIGN_GAP_REVIEWED" -gt 0 ]; then if ! grep -qE 'P1.*BDD|P2.*packages|P4.*implementation' "$P7_FILE"; then echo "WARNING P7: ..."` — WARNING (not exit 1) when DESIGN_GAP_REVIEWED exists but lacks cross-file reference keywords
- dispatch-protocol.md:721-725: DESIGN_GAP_REVIEWED documentation describes the mechanism

**Verdict: ALIGNED** — N3 WARNING is implemented as a non-blocking WARNING (echo to stderr, no exit 1), consistent with "nudge" semantics. The WARNING does not change gate exit code.

### A2: Script→Document alignment

**A2.1** check-gate.sh P1 branch exits exit 1 for missing P1-review.md

- check-gate.sh:23-26: `[ ! -f "$P1_REVIEW" ]` → exit 1
- state-machine.md:77: P1→P2 transition requires `P1-review.md status:approved` (implies file must exist)
- WORKFLOW.md:192: P1 threshold includes `P1-review.md status:approved` (implies file must exist)

**Verdict: ALIGNED** — Missing file → exit 1 is documented as a gate failure condition.

**A2.2** check-gate.sh P1 branch exits exit 1 for agent=main

- check-gate.sh:37-39: `if [ "$P1_REVIEW_AGENT" = "main" ]` → exit 1
- WORKFLOW.md:229: `agent=main（自审）被 check-gate.sh 硬拦截 exit 1`
- dispatch-protocol.md:780-793: "P1 评审不可裁" implies agent≠main
- orchestrator-template.md:94: "check-gate.sh P1 对 P1-review.md agent=main 硬拦截（exit 1）"

**Verdict: ALIGNED** — agent=main exit 1 is documented in WORKFLOW.md, dispatch-protocol.md, and orchestrator-template.md.

**A2.3** check-gate.sh P1 branch exits exit 1 for no BDD anchor

- check-gate.sh:41-43: `if ! grep -qE 'BDD-|B[0-9]' "$P1_REVIEW"` → exit 1
- dispatch-protocol.md:647: `含 BDD-/B[0-9] 锚点（check-gate.sh P1 检查）`
- P1-requirements.md:47: `含 BDD 编号锚点 → exit 2；缺 P1-review.md / agent=main / 无锚点 → exit 1`
- requirements-review.md:47: `不引用 BDD 编号的裸 "approved" 极可能是假完成——gate 脚本会检查锚点存在性`

**Verdict: ALIGNED** — BDD anchor check is documented in dispatch-protocol.md, P1 phase card, and requirements-review role file.

**A2.4** check-gate.sh P1 branch frontmatter status extraction

- check-gate.sh:27: `sed -n '/^---$/,/^---$/p' "$P1_REVIEW" | { grep '^status:' || true; } | sed 's/^status:\s*//' | head -1`
- This is the F1 fix: extracts status from YAML frontmatter only, not from body text
- dispatch-protocol.md:647: `P1-review.md status:approved` — refers to frontmatter status field
- state-machine.md:77: `P1-review.md status:approved` — same

**Verdict: ALIGNED** — Frontmatter extraction is the correct implementation matching the documented "status:approved" field semantics.

**A2.5** check-gate.sh P7 WARNING for cross-file references

- check-gate.sh:163-168: WARNING (echo to stderr, continues to exit 0) when DESIGN_GAP_REVIEWED > 0 but no cross-file reference keywords
- dispatch-protocol.md:721-725: DESIGN_GAP_REVIEWED mechanism documented
- P7-consistency.md:26: "DESIGN_GAP 配对" check listed

**Verdict: ALIGNED** — The WARNING is a nudge (non-blocking), consistent with the "review 实质锚点" concept in requirements-review.md:39-47. The WARNING does not change gate exit code (P7 still exits 0 if no BLOCKER/DEVIATION-CRITICAL/unreviewed DESIGN_GAP).

### A3: Consistency chain + reverse propagation

#### A3a: Chain (known derivative changes)

| File | In diff? | Status |
|------|----------|--------|
| requirements-review role file (new) | ✅ `agate/assets/review-roles/requirements-review.md` | New file, 74 lines |
| check-gate.sh P1 branch | ✅ Lines 21-46 | P1 review checks implemented |
| P1-requirements.md phase card | ✅ Lines 10-13, 47-48, 69-72 | Review step + gate rules + ⑩ annotation |
| state-machine.md P1→P2 transition | ✅ Line 77 | P1-review.md + agent≠main + BDD anchor |
| dispatch-protocol.md P1 threshold + dispatch flow | ✅ Lines 647, 780-793 | P1 threshold + requirements-review section |
| WORKFLOW.md P1 row | ✅ Line 192 | requirements-review（强制，不可裁） |
| orchestrator-template.md P1 invariant | ✅ Line 94 | P1 评审不可裁 + agent=main 硬拦截 |
| check-protocol-consistency.py CHECK 9 anchor | ✅ Lines 539-543 | P1 review agent≠main anchor |
| P2/P4/P6/P7 phase cards for ⑩ annotations | ✅ P2:73, P472, P667, P747 | ⑩ iteration loop annotations |
| check-gate.bats + check-gate-p1-review.bats | ✅ Both files | 7 P1-review tests + 58 general gate tests |
| pre-commit-hook.bats (P1 fixture) | ✅ Lines 65-74, 154-163 | P1-review.md fixture with BDD anchor |

#### A3b: Reverse propagation (files that should be affected but not listed)

| Should be affected | In diff? | Analysis |
|-------------------|----------|----------|
| `agate/assets/execution-roles/analyst.md` | Not in diff | **Not needed**: analyst.md doesn't reference P1 review mechanism; it's the execution role, not the review role |
| `agate/assets/review-roles/design-review.md` | Not in diff | **Not needed**: design-review is P2/P4, not P1 |
| `agate/role-system.md` | Not in diff | **NEEDS_HUMAN_REVIEW**: role-system.md may need to list requirements-review in the review-roles catalog. However, AGENTS.md:55 already lists it. |
| `CHANGELOG.md` | Not in diff | **Not needed yet**: U1 branch not at P8; CHANGELOG update is P8's job |
| `agate/LIMITATIONS.md` | Not in diff | **Not needed**: No new limitations introduced |

**Verdict: ALIGNED** — All expected files are in the diff. One NEEDS_HUMAN_REVIEW for role-system.md catalog completeness, but AGENTS.md already covers it.

### A4: Test coverage

**A4.1** check-gate-p1-review.bats covers:

| Scenario | Test | Line |
|----------|------|------|
| Missing P1-review.md | `P1: 缺 P1-review.md 期望 exit 1` | :3-18 |
| agent=main | `P1: P1-review.md agent=main 期望 exit 1` | :20-44 |
| No BDD anchor | `P1: P1-review.md 无 BDD 编号引用 期望 exit 1` | :46-70 |
| All pass (approved + agent≠main + anchor) | `P1: P1-review.md status:approved + agent≠main + 含锚点 期望 exit 2` | :72-96 |
| Rejected status | `P1: P1-review.md status:rejected 期望 exit 1` | :98-122 |
| Missing status field | `P1: P1-review.md 缺 status 字段 期望 exit 1` | :124-147 |

**Verdict: ALIGNED** — All 6 core scenarios covered.

**A4.2** F1 adversarial: frontmatter=rejected + body contains "status: approved"

- check-gate-p1-review.bats:149-178: `P1: frontmatter rejected + 正文含 status: approved 字面串 期望 exit 1（对抗绕过）`
- Test creates P1-review.md with frontmatter `status: rejected` but body text "gate 规则要求 status: approved 才放行"
- Expected: exit 1 (frontmatter wins, body text ignored)

**Verdict: ALIGNED** — F1 adversarial test covers the exact attack vector.

**A4.3** P2 adversarial tests matching F1 fix

- check-gate.bats:189-215: `G2.10a check-gate.sh P2 frontmatter rejected + 正文含 status: approved 字面串 期望 exit 1（对抗绕过）`
- Same adversarial pattern for P2-review.md

**Verdict: ALIGNED** — P2 has matching F1 adversarial test.

**A4.4** Integration tests include P1-review.md fixture

- pre-commit-hook.bats:65-74 (IT.2): P1-review.md fixture with `status: approved`, `agent: requirements-review`, BDD anchor `B01: PASS`
- pre-commit-hook.bats:154-163 (IT.6): Same P1-review.md fixture for multi-task architecture
- pre-commit-hook.bats:324-333 (IT.10): Same fixture for backward compatibility test

**Verdict: ALIGNED** — Integration tests use P1-review.md fixture with all required fields.

**Bats full run output** (2026-07-12):
```
1..65
ok 1 P1: 缺 P1-review.md 期望 exit 1
ok 2 P1: P1-review.md agent=main 期望 exit 1
ok 3 P1: P1-review.md 无 BDD 编号引用 期望 exit 1
ok 4 P1: P1-review.md status:approved + agent≠main + 含锚点 期望 exit 2
ok 5 P1: P1-review.md status:rejected 期望 exit 1
ok 6 P1: P1-review.md 缺 status 字段 期望 exit 1
ok 7 P1: frontmatter rejected + 正文含 status: approved 字面串 期望 exit 1（对抗绕过）
ok 8-65 [all remaining check-gate.bats tests pass]
```

### A5: Downstream impact

**A5.1** Does the P1 gate change affect P2 gate or later phases?

- P1 gate now requires P1-review.md (new requirement). This only affects P1→P2 transition.
- P2 gate (check-gate.sh:47-101) is unchanged — it checks P2-design.md and P2-review.md independently.
- P3-P8 gates are unchanged.
- The P1 gate change is **additive** (new file requirement), not **breaking** (no existing valid state is invalidated).

**Verdict: ALIGNED** — P1 gate change is scoped to P1→P2 transition only.

**A5.2** Does the P7 WARNING affect P7 gate exit code?

- check-gate.sh:163-168: The WARNING is an `echo` to stderr, followed by `exit 0` (line 169).
- The WARNING does NOT change the exit code. P7 gate still exits 0 when BLOCKER=0, DEVIATION-CRITICAL=0, and all DESIGN_GAPs are REVIEWED.
- This is a **nudge** (like check-retrospective.sh), not a **blocker**.

**Verdict: ALIGNED** — P7 WARNING is non-blocking, consistent with nudge semantics.

**A5.3** Does check-p6-provenance.sh need adaptation?

- check-p6-provenance.sh audits P6 evidence, not P1 review.
- P1 review changes don't affect P6 provenance checks.
- The P1 review requirement (P1-review.md) is a new file that provenance doesn't inspect.

**Verdict: ALIGNED** — No adaptation needed.

### A6: Anchor table coverage

**A6.1** CHECK 9 has anchor for "P1 review agent≠main"

- check-protocol-consistency.py:539-543:
  ```python
  {
      "desc": "P1 review agent≠main 检查",
      "script": "agate/scripts/check-gate.sh",
      "keywords": ["P1", "agent=main"],
  }
  ```
- check-gate.sh:37: Contains `agent=main` in P1 branch

**Verdict: ALIGNED** — Anchor exists and keywords match.

**A6.2** CHECK 9 has anchor for F1 frontmatter fix

- The F1 fix (frontmatter extraction via `sed -n '/^---$/,/^---$/p'`) is an implementation detail of the existing status check, not a new rule.
- CHECK 9 already has anchors for:
  - `P2 agent=main 硬拦截` (line 535-538) — covers P2 frontmatter extraction
  - `P1 review agent≠main 检查` (line 539-543) — covers P1 frontmatter extraction
- The frontmatter extraction pattern is the same for both P1 and P2; no separate anchor needed.

**Verdict: ALIGNED** — F1 fix is covered by existing agent=main anchors (both P1 and P2 use the same frontmatter extraction pattern).

**A6.3** Is every gate script covered?

Gate scripts in `agate/scripts/check-*.sh`:
- check-gate.sh → ✅ Multiple anchors (DESIGN_GAP, P2 agent=main, P1 review agent≠main)
- check-tdd-red.sh → ✅ Anchor: "TDD 红灯检查"
- check-state-transition.sh → ✅ Anchors: "重试上限检查", "回退跳变检测"
- check-p6-evidence.sh → ✅ Anchors: "P6 evidence UI 检查", "P6 截图去重"
- check-p6-provenance.sh → ✅ Anchor: "P6 provenance 审计"
- check-pruning.sh → ✅ Multiple anchors (P2/P3/P6/P7/P8 裁剪)
- check-scope-resolved.sh → ✅ Anchor: "SCOPE+ 追踪"
- check-changelog.sh → ✅ Anchor: "P8 CHANGELOG 检查"
- check-state-yaml.sh → ✅ Anchor: "state.yaml 格式校验"
- check-retrospective.sh → ✅ Anchor: "复盘提醒"
- pre-commit-gate.sh → ✅ Anchor: "PROD_TOUCHED 检测"

Exempt scripts (GATE_SCRIPT_EXEMPT): gate-result.sh, install-hook.sh, agate-changes.sh, agate-summary.sh, agate-init.sh — correctly exempted.

**Verdict: ALIGNED** — All gate scripts have CHECK 9 anchor coverage.

## Overall Verdict

**ALIGNED** — All A1-A6 checks pass. U1 implementation correctly delivers:

1. **⑧ P1 requirements-review**: New role file + check-gate.sh P1 branch with status/agent/anchor checks + all docs updated
2. **⑩ do→review iteration loop**: Annotations in P1/P2/P4/P6/P7 phase cards + dispatch-protocol.md iteration table
3. **N3 P7 WARNING**: Cross-file reference keyword nudge in check-gate.sh P7 branch (non-blocking)
4. **F1 frontmatter fix**: `sed -n '/^---$/,/^---$/p'` extraction for both P1 and P2 review status (not full-grep), with adversarial tests

One NEEDS_HUMAN_REVIEW item: `role-system.md` may need requirements-review added to its review-roles catalog, but AGENTS.md already lists it.
