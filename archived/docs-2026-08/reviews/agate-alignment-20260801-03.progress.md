read: protocol-alignment-review.md (role def)
read: git diff v0.27.0..HEAD --stat (20 files, 656+/25-)
read: git diff 8fe75c2..HEAD (T075 mechanism range): check-gate.sh, check-tdd-red.sh, agate-render-dispatch-prompt.sh, dispatch-prompt.md, tests/README.md, hardening-roadmap.md, tests diffs
read: dispatch-prompt.md full (232 lines) — P3 自检 block at 100-106, 修复轮 block at 177-183 NOT in code fence, P8 at 185
read: agate-render-dispatch-prompt.sh full — P3 case added line 85-87
read: check-gate.sh full (373 lines) — P2.61 at 137-173 WARNING-only
read: check-tdd-red.sh full (214 lines) — hint added line 136 stderr
next: state-machine.md, dispatch-protocol.md, WORKFLOW.md, architect.md, test-designer.md, task-files.md, adr.md, CHANGELOG
read: state-machine.md full (653 lines) — P2 transition line 85 no P2.61 mention, P3 红灯 line 267-290, gate design line 276-290
note: P2.61 is WARNING-only exit 2, so state-machine.md P2 transition (line 85) unaffected — ok
read: dispatch-protocol.md full (1219 lines) — 阶段特定提示 section lines 498-567 has P2/P4/P5P6/P8 only, NO P3 block, NO 修复轮 block
note: dispatch-prompt.md line 4 claims sync with dispatch-protocol.md「派发 prompt 模板」; P3/修复轮 blocks NOT propagated → potential A3b/A5 gap
read: architect.md full (165) — gate_commands section L39-58, NO P2.61 checklist (intentional mechanism-over-rule)
read: test-designer.md full (49) — NO P3 自检/断言矛盾 mention (intentional, injected via dispatch-prompt)
read: P3-tdd.md card — NO P3 自检 mention; 派发 prompt 指向 dispatch-prompt.md
read: check-protocol-consistency.py CHECK 9 anchors — agate-render-dispatch-prompt.sh not a gate script (exempt); no anchor needed
read: adr.md — 6 ADRs; changes align ADR-002/003/001/006
read: plan agate-t075-mechanism-fixes-20260801.md — implementation matches plan closely; P2.62/63 were re-scoped from not-fix to mechanism
read: CHANGELOG.md — [Unreleased] has P2.51-57 but NO P2.61/62/63 entries → A5 gap
VERIFY: check-protocol-consistency.py = 0 ERROR, 12 pre-existing WARNING
VERIFY: count-tests.sh = 513 total; check-gate=95, render=16, tdd-red=31 match README
VERIFY: full bats = 519 ok / 0 not ok / exit 0 (sanity+unit+regression+integration)
VERIFY: shellcheck -S warning on 3 changed scripts = clean
VERIFY: manual P2.61 test — python/pytest missing → WARNING; python3/bash present → no WARNING; ENV=x skip works; $(...)/path skip works
FINDING A2/A3b: dispatch-protocol.md 阶段特定提示 (L498-567) 无 P3 派发追加 + 修复轮块，dispatch-prompt.md:4 声称与协议文件同步且协议文件为权威 → 未反向传播
FINDING A5: CHANGELOG [Unreleased] 缺 P2.61-63 条目
FINDING A4 minor: env-prefix/$()/path-skip 分支无专属测试（G_CMD_EXEC 只覆盖 happy path）
FINDING minor: tests/README.md integration 行仍漂移（pre-commit-hook 5 vs 37, consistency 10 vs 11, self-gate 6 vs 8）——既有漂移，本次仅修 unit 行
DONE — writing report
