# Changelog

All notable changes to the agate protocol will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

### Added
- P3 gate red-light A/B classification: B-class (import from missing implementation) now exits 0, A-class (test code bugs) exits 1. `PROJECT_MODULE` env var for precision, heuristic fallback when unset
- P5 fix flow: main Agent must rerun full P5 gate (all tests) after fix subagent returns, not just check fixed items. Fix history must be included in re-dispatch prompt
- P8 gate CHANGELOG coverage check: `git log v{prev_version}..HEAD --oneline` vs CHANGELOG entries. `CHANGELOG_FILE` env var for non-CHANGELOG.md projects
- P6 BDD result format: must use line-start `- PASS`/`- FAIL`, no tables/emoji, for reliable grep matching
- P6 evidence directory (`P6-evidence/`): non-empty check as anti-forgery measure for self-authored gate
- Gate classification: external-output gates (P3/P4/P5) vs self-authored gates (P1/P2/P6/P7) with ⚠️ markers
- `check-gate.sh`: scripted gate checks for P3/P4/P6/P7/P8 (exit 0/1/2)
- `check-protocol-consistency.py`: 6-category structural consistency check + CI workflow
- Task granularity guide: split criterion changed from "output heterogeneity" to "output file count > 3" (T026 experiment proved dispatch prompt handles heterogeneous output reliably)
- `LIMITATIONS.md` limitation 3: self-authored gate classification + T026 incident record

### Changed
- P6 gate exit code changed from 0 to 2: scripted checks (FAIL=0/NC=0/evidence non-empty) pass, but BDD count match requires main Agent manual verification
- `check-tdd-red.sh`: added `PROJECT_MODULE` env var, multi-language import error detection, TEST_RUNNER output contract documented, pytest as reference implementation
- `check-gate.sh` P8: added `CHANGELOG_FILE` env var, expanded version file patterns (go.mod/pom.xml/etc.), documented single-commit assumption
- P6-evidence/ subdirectories: `screenshots/` and `traces/` now marked as UI-task-only, `test-output.log` is universal
- Gate classification examples: changed from pytest/vue-tsc to generic terms (test runner/type checker)

### Fixed
- `check-tdd-red.sh`: fixed `IndententationError` → `IndentationError` typo; removed duplicate `SyntaxError` in regex

---

## [0.3.0] - 2026-06-28

### Added
- `check-gate.sh`: scripted gate checks for P3/P4/P6/P7 (exit 0/1/2 for scriptable, exit 2 for dynamic/semantic gates)
- `check-tdd-red.sh`: `TEST_RUNNER` env var with fallback chain ($TEST_RUNNER → which pytest → exit 3)
- P8 gate: bump_type field check, version file change check, CHANGELOG change check
- T022 debt paydown: P6 BDD coverage completeness, P8 bump re-run P5, bump_type judgment, DEVIATION-CRITICAL classification, write-run separation clarification, verifier evidence priority (DOM > interaction > vision), compact environment recovery (env_state in .state.yaml)

### Changed
- State machine step 5: gate commands in two tiers — shell-commandable (P3/P4/P7) write shell commands, dynamic (P1/P2/P5/P6/P8) keep natural language
- P5/P8 gate: bump after P8 must rerun P5 gate + bump_type field
- P7 gate: DEVIATION-CRITICAL marker format added
- P8 gate: `git diff HEAD~1` for version/CHANGELOG verification

---

## [0.2.0] - 2026-06-27

### Added
- Phased landing (分阶段落盘) as default: every dispatch prompt includes landing instructions, not just as fallback after empty returns
- P0-brief executor_env completion, P0/P1 responsibility boundary three-layer guide
- LIMITATIONS.md limitation 5: protocol document internal consistency verification not in scope
- WORKFLOW.md: main Agent legal responsibilities list and downgrade hard boundary

### Changed
- T020 review fixes: P6 single-step function old wording corrected (PASS/FAIL binary), duplicate write-run separation paragraph removed
- assets/ synced with T016-T020 protocol fixes (6 execution roles + 4 templates + all protocol files)

### Fixed
- T019 retrospective fixes: 6 items (review checklist template, LIMITATIONS T019/T016 data points, etc.)
- T020 retrospective fixes: 6 items (2 bug fixes + 3 capability supplements + 1 known limitation)
- Empty return root cause: verified `steps` limit is ineffective, phased landing is effective (5-group controlled experiment)

---

## [0.1.0] - 2026-06-26

### Added
- Core protocol: state machine (P0-P8 phases), dispatch protocol, workflow guide
- Role system: 6 execution roles (analyst, architect, test-designer, implementer, verifier, vision-analyst) + 3 review roles
- Orchestrator template: startup read list, platform-specific config blocks
- Git integration, loop orchestration, platform notes
- LIMITATIONS.md: 5 known limitations documented
- T016 retrospective: 5 protocol fixes (input navigation, downgrade prohibition, empty return recovery, etc.)
- Expert review: 10 BLOCKER fixes + 8 suggestions addressed

### Changed
- Generalization cleanup: removed PeekView-specific content (6 locations)
- Standard install location: `~/.agate/`
- Context engineering optimization: orchestrator reads all 7 top-level files at startup

### Fixed
- Ambiguous trigger conditions: git-integration boundaries + review role judgment standards clarified
- Startup read gap: orchestrator-template changed to mandatory startup read, added interrupt recovery gap fill
