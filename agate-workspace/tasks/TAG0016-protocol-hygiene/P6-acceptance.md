---
phase: P6
task_id: TAG0016
type: acceptance
parent: P5-verification.md
trace_id: TAG0016-P6-20260819
status: draft
created: 2026-08-19
agent: verifier
pass: 19
fail: 0
ui_affected: false
---

[NO_NEED_CONFIRM]
[PROD_NOT_TOUCHED]

# P6 验收报告 — TAG0016（agate 协议卫生与测试效率）

worktree HEAD 实跑：`4abf959`（与 P5 通过 commit 一致，工作区除本次 P6 新增产出文件外无其他改动）。
工作目录：`/home/kity/oclab/agate/.worktrees/agate-TAG0016`（worktree 自己的 `agate/`，未碰 `~/.agate`）。

本任务 `ui_affected: false`，不涉及 vision-analyst / Playwright / 截图。`change_type` 未声明
`refactor`，走标准功能验收口径（非三段式回归口径）。

铁律遵循声明：以下 19 条 BDD 全部先实跑命令 / 读取文件看到客观结果，再写 PASS/FAIL，未出现"看代码
推断应该满足"的情况；无法验证的会标 FAIL，不标 PASS（本次全部可验证，无 FAIL 项）。

---

## BDD 逐条验收结果

- PASS BDD-1: 职责声明表已建立且覆盖 WORKFLOW.md/dispatch-protocol.md/state-machine.md/platform-notes.md 4 个显式声明行落地文件（rules/state-transitions.md、dispatch-prompt.md、phase-cards/*.md 三者以指针/文件头修正/保留原样等不同形式受同一职责表约束，形式差异已在 P2-design.md §0 中显式声明）；4 文件头部第 3 行（20 行内）均含 `> 职责边界：{描述}（详见职责声明表，P2-design.md §0）`，内容与 P2-design.md §0 表逐条比对完全一致 (bdd-1-19.log)
- PASS BDD-2: `grep -n "## 平台适配" -A5 agate/WORKFLOW.md agate/dispatch-protocol.md` 确认两处均已收窄为一句话摘要 + 指向 platform-notes.md 的指针，不再独立展开平台能力表格/坑位描述；`grep -c "." agate/platform-notes.md` = 112（非空行），章节标题核对（OpenCode/Claude Code/Codex/Windows 原生/已知限制等 9 个二级标题）确认权威源内容完整，未被误删 (bdd-2.log)
- PASS BDD-3: WORKFLOW.md L284「本表为角色/评审映射颗粒度；逐条可执行判定命令见 dispatch-protocol.md」+ dispatch-protocol.md L734「本表为逐条可执行 grep/命令颗粒度；角色/评审映射颗粒度见 WORKFLOW.md」两条互相指向的分工声明句均存在，颗粒度分工显式声明在文档中 (bdd-3.log)
- PASS BDD-4: dispatch-protocol.md「## 派发 prompt 模板」节（L431-452，约 21 行含空行）已收窄为权威源指针 + 极简 4 行结构骨架，不再维护完整正文；`head -5 agate/assets/templates/dispatch-prompt.md` 确认文件头已改为「本文件是派发 prompt 的权威来源；dispatch-protocol.md 仅保留极简结构提示 + 指针」，两文件头都显式声明各自角色，不再是"声明同步但实际分叉"的矛盾状态 (bdd-4.log)
- PASS BDD-5: `grep -n "重试上限" -A3 agate/rules/state-transitions.md` 确认该节已是纯指针句「详见 state-machine.md《重试上限》——权威唯一来源，本文件不重复维护」，不含数值表，与文件头已有的"权威源：state-machine.md"声明行为一致 (bdd-5.log)
- PASS BDD-6: 实跑 `pytest agate/tests/unit/test_check_protocol_consistency.py -k mismatched_inline_max -v`，`test_bdd_9_check12_mismatched_inline_max_reports_error` 1 passed（该测试构造真实的阶段卡片内联 MAX 与权威表不一致场景并断言 CHECK 12 报 ERROR，是这条 BDD 行为的真实执行证明，非推断） (bdd-6.log)
- PASS BDD-7: `grep -n "Pre-commit 检查" agate/dispatch-protocol.md agate/state-machine.md agate/git-integration.md` 确认 3 处指针句原样未变（均为"详见 WORKFLOW.md《Pre-commit 检查总览》——权威唯一来源，本文件不重复维护"式表述，未被误判误改）；实跑 `python3 agate/scripts/check-protocol-consistency.py --strict`，结果 **0 ERROR，311 个 WARNING**（脚本按既定语义 exit=2，非"命令执行失败"；308+ 条 WARNING 为存量债务，与本任务改动无关，已在 P5 阶段核实并登记 DEBT0012，不影响本条判定） (bdd-7.log)
- PASS BDD-8: P6 阶段人工抽查完成，抽查了 WORKFLOW.md「## 平台适配」小节（L465-469）与 dispatch-protocol.md「## 派发编排机制」小节（L466 起）各 1 处曾被认定"职责定位混乱"的内容段落，逐段对照 P2-design.md §0 职责声明表对应条目：前者已完成迁移收窄（原展开的平台能力表格已移出，仅留一句话摘要+双指针，与"不承载：平台能力矩阵全文"一致）；后者被职责声明表显式认定为"派发编排机制（工作量评估/并行规则/回退处理）"本就是 dispatch-protocol.md 唯一职责范围内容，合理保留在此。抽查过程、对照条目、结论详见证据文件 (bdd-8-manual-review.md)
- PASS BDD-9: 实跑 `pytest agate/tests/unit/test_check_protocol_consistency.py -k bdd_9 -v`，4 项全部 passed（含 CHECK 12 注册断言、锚点表注册断言、正报断言、一致值 0 ERROR 断言）；`grep -n "CHECK 12" agate/scripts/check-protocol-consistency.py` 确认已在 CHECKS 列表第 1072 行注册为 `("CHECK 12 权威数值/规则跨文件一致性", check_authoritative_values)` (bdd-9.log)
- PASS BDD-10: 实跑 `pytest agate/tests/unit/test_check_protocol_consistency.py -k bdd_10 -v`，`test_bdd_10_check12_no_false_positive_on_existing_precommit_pointers` 1 passed，确认 CHECK 12 对存量正确"权威源+指针"模式（Pre-commit 三处指针等）实测 0 误报 (bdd-10.log)
- PASS BDD-11: `grep -n "## 全量重跑点审计" -A40 agate/dispatch-protocol.md` 确认该小节存在（L453 起），含 4 个重跑点（P5 首跑/P5 失败后重跑/P6 refactor 独立 regression.log/P8 bump-version 后重跑）逐点标注"必然/条件"性质、触发条件、是否可被本任务机制替代引用 (bdd-11.log)
- PASS BDD-12: 实跑 `pytest agate/tests/unit/test_check_p6_provenance.py -k "bdd_12 or critical1" -v`，4 项全部 passed（含无改动允许引用、字段缺失回退强制重跑、CRITICAL-1 修复后 git diff 命令失败 fail-closed 场景、fake commit git 失败场景），check-p6-provenance.py 新增审计 7 的可判定"无改动"校验标准已实测通过 (bdd-12.log)
- PASS BDD-13: 实跑 `pytest agate/tests/unit/test_check_p6_provenance.py -k bdd_13 -v`，2 项全部 passed（含非产出文件改动触发拦截、仅产出目录改动被正确排除），P6 退回 P4 修复后重新到达 P6 的不可复用边界由 git diff 结果自动判定，不依赖人工声明 (bdd-13.log)
- PASS BDD-14: `agate/phase-cards/P8-release.md` L82-88（「P5 验证（TAG0016 BDD-14 精简为条件化表述，底线不变——至少一次客观验证动作不可省）」段落）确认条件化表述已落地（读 AUDIT7_RESULT 判定 reuse_allowed/reuse_blocked/no_reuse_claim_possible），且显式保留"至少一次客观验证动作不可省"底线声明（dispatch-context 建议的字面 grep 关键词因反引号未精确命中，已在证据文件中注明并改用相邻关键词 AUDIT7_RESULT 定位同一段落核实内容） (bdd-14.log)
- PASS BDD-15: `grep -n "xdist" -A5 .github/workflows/protocol-tests.yml` 确认观测步骤「xdist Timing Observation (Linux, 仅观测耗时，不影响门禁，BDD-15/M23)」存在、`continue-on-error: true`，步骤失败不影响 job exit code。明确声明：本条判据是"步骤存在且不影响门禁"，不是"已验证加速效果"——本次验收未在真实 CI 环境运行该步骤，不产出"已验证加速"的结论 (bdd-15.log)
- PASS BDD-16: `grep -n "资源密集型默认串行" -A8 agate/dispatch-protocol.md` 确认「并行规则」第 4 条判据描述仍包含"全量测试套件跑 xdist / 多进程并发（如 pytest -n auto）——并行批次各自再起多进程会争抢 CPU 与文件锁"表述，未被 M23（新增 CI 观测步骤）改动削弱，多个并行 subagent 各自跑 xdist 的情形仍默认串行 (bdd-16.log)
- PASS BDD-17: 引用 P5-test-results/unit.md 的实跑结果（966 passed / 0 failed / 2 skipped，consistency --strict 0 ERROR/308 WARNING，count-tests.sh 968 ≥ 961 基线）；P6 验收发起时点 worktree HEAD 仍为 P5 通过 commit `4abf959`，`git status --short` 确认工作区除本次 P6 新增的 3 个未跟踪产出文件外无任何改动，P5→P6 之间本任务自身无代码/协议改动；本次 P6 阶段额外独立复核一遍 `check-protocol-consistency.py --strict`（BDD-7 步骤）同样得到 0 ERROR，与 P5 结论一致，回归基线未被破坏 (bdd-17-p5-regression-evidence.md)
- PASS BDD-18: `grep -n "Windows" agate/platform-notes.md` 确认「## Windows 原生（Git for Windows，不用 WSL）」章节（L85 起，含前置条件/安装步骤/已知限制/latest 指针形态等完整小节）未被去重误删/误改，安装指南步骤完整；人工核对本次 P6-acceptance.md 全文（含本文件自身撰写时逐句自查）未使用"已在 Windows 实测验证"类措辞，全部 Windows 相关表述均限定为"静态检查通过 + CI Windows matrix 冒烟通过"口径 (bdd-18-manual-review.md)
- PASS BDD-19: 与 BDD-1 共用同一处证据（4 文件头部"职责边界"声明行），P2-design.md §0 表已明确 BDD-1/BDD-19 共同落地点为 WORKFLOW.md/dispatch-protocol.md/state-machine.md/platform-notes.md 4 处声明行；后续任何 agate 自身改造任务派发 protocol-alignment-review 时，审查角色可读到这行职责声明判断"本次改动是否加入了不属于本文件职责的内容"，声明本身已先于机制存在 (bdd-1-19.log)

---

## 汇总

**Summary**: 19/19 PASS, 0 FAIL

全部 19 条 BDD（RM-AG0025 9 条：BDD-1~10 含 BDD-8 人工抽查；RM-AG0026 8 条：BDD-11~18；防复发落地入口 1 条：BDD-19）均实跑验证通过，无 FAIL 项，无中间态。回归底线（BDD-17）经独立复核确认未被破坏。P6-evidence/ 目录内 15 个证据文件全部非空且含实质命令输出/人工核对记录，每条 PASS 均已引用对应证据路径。
