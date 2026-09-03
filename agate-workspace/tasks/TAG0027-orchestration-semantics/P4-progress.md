
## B1 开工（2026-09-02 23:16:11）
- implementer B1 批次开始：core-rules-cli（phases.yaml + schema + agate-next.py + agate-advance.py + check-judge-verdict.py + loop-orchestration.md）

## B2 开工（2026-09-02）
- implementer B2 批次开始：render-audit（agate-dispatch.py 新建 / dispatch-context.md 模板 CARD-SOURCE / check-p6-provenance.py 审计 2 双锚点剥离）
- 已读：P4-dispatch-context-implementer-B2.md（dispatch 指引）+ implementer.md 角色文件
- B2 已读：9 个 B2 测试用例（test_tag0027_b2_agate_dispatch.py 6 用例 BDD-18/19/25 + test_tag0027_b2_audit2_dual_anchor.py 3 用例 BDD-20/21）——契约要点：agate-dispatch.py CLI 产物 frontmatter(phase/generated_by: agate-dispatch.py + 主 Agent/task_id/role) + CARD-SOURCE 在 START 前（块外）+ START..END 内嵌 = agate-next-card stdout 逐字；inject-card 手工路保留；audit2 双锚点剥离（CARD-SOURCE 行起剥，START 前 PASS 行也要被剥）

### B1 输入阅读（2026-09-02 23:21:21）
- 已读：dispatch-context、implementer.md、P2-design.md（§3.1/3.3/3.4/3.7 定案）、P3-test-cases.md、4 个 B1 测试文件、conftest fixtures、phases.yaml/schema 现状、check-gate.py main/gate_p5/gate_p6/gate_p65、agate-retreat-to.py 全文、check-judge-verdict.py 全文、agate_common 公共函数、loop-orchestration.md 46-74/227-243
- B2 已读：P2 §3.5/§3.6/§8 定案 + §4.2 files_to_read + P3-test-cases B2 行 + 参照脚本（agate-next-card.py 全、agate-inject-card.py 全、agate-card-inject.py、agate-render-dispatch-prompt.py、pre-commit-gate.py _extract_card 171-189、check-p6-provenance.py 审计 2 318-355、dispatch-context.md 模板全、conftest fixtures）+ 既有回归测试面（test_check_p6_provenance pv_8/pv_17、test_agate_inject_card、模板消费测试 test_check_gate drift_4/4b、md_field_set bdd_19）
- B2 现状确认：pytest 跑 B2 批 = 4 红 5 绿（4 红 = BDD-18 x2 + BDD-25 two_paths + BDD-20 dual_anchor 真扩展点；5 绿 = BDD-19 x2 + BDD-25 auto_hash + BDD-20 exit_0 + BDD-21 回归守卫）
- 实现方案确定：agate-dispatch.py（镜像 inject-card 的 _agate_root/_next_card_content；frontmatter 行级替换；guide 骨架替换；START 前插 CARD-SOURCE；START..END 内容换 next-card stdout 行）；audit2 剥离改双锚点（CARD-SOURCE 行起 skip 到 END + 既有物理块兜底，flag 双态与原语义逐行等价）
- B2 实现完成（改动 3 独占文件，未碰 B1/B3 文件）：
  1) agate/scripts/agate-dispatch.py（新建）——渲染时注入单命令 CLI（§3.5 D5-A）：读模板骨架 → 子进程 agate-next-card.py {phase} 取卡片 → frontmatter 占位替换（generated_by: agate-dispatch.py + 主 Agent）+ guide 首行替换（--guide FILE 可选）+ CARD-SOURCE 行插 START 前（块外）+ START..END 内容换 next-card stdout 逐字；写 {phase}-dispatch-context-{role}.md；exit 0/1
  2) agate/assets/templates/dispatch-context.md——顶部加双路径说明（渲染/手工），卡片块前注明 CARD-SOURCE 注入区（块外语义），占位符注释改双路径描述；正文不含字面 CARD-SOURCE 锚点串（防渲染产物误触发审计 2）
  3) agate/scripts/check-p6-provenance.py 审计 2——剥离改双锚点（§3.6 D6-A）：CARD-SOURCE 行起（块外触发）至 AGATE_CARD_END 整段剥优先；无 CARD-SOURCE 走既有 AGATE_CARD_START..END 物理块兜底
- B2 批测试结果：9/9 全绿（test_tag0027_b2_agate_dispatch.py 6 + test_tag0027_b2_audit2_dual_anchor.py 3）
- 回归抽查：test_check_p6_provenance(51) + test_agate_inject_card(11) + test_agate_card_inject + test_check_judge_verdict + test_dispatch_context_warning + test_card_render + test_agate_render_dispatch_prompt + test_agate_next_card + test_dispatch_orchestration + test_agate_md_field_set + test_check_gate drift 子集 = 全绿；consistency --strict-errors-only 0 ERROR；ruff 两脚本 clean

### B1 实现进度 1（2026-09-02 23:46:23）
- phases.yaml: P0-P8 加 next/retreat（P5/P6 retreat: P4，P8 null，P6.5 不写）；P6.5 加 gate_subphase{hosted_on: P6, forward_to: P7, needs_revision_to: P6}
- phases.schema.json: 声明 next/retreat（enum P0-P8+null）与 gate_subphase（required 三键）
- 验证：check-yaml-schema.py 3 OK；check-protocol-consistency --strict-errors-only exit 0（326 WARNING 无 ERROR）；test_bdd_1_phases_transfer_fields 5 passed
- B2 最终验证：9/9 全绿（B2 批两文件）；回归抽查全绿 = test_check_p6_provenance(51，含 pv_8 审计2 预判拦截 + pv_17 上下文节) + test_agate_inject_card(11) + test_agate_card_inject + test_check_judge_verdict + test_dispatch_context_warning + test_card_render + test_agate_render_dispatch_prompt + test_agate_next_card + test_dispatch_orchestration + test_agate_md_field_set + test_check_gate drift/template 子集；全量 unit 串行 = 16 failed 全属 B1/B3a/B3b 未落地批（非本批）+ 1219 passed（base 无回归）+ 2 skipped；consistency --strict-errors-only 0 ERROR；ruff 两脚本 clean
- 改动文件清单（3 独占文件）：agate/scripts/agate-dispatch.py（新建，渲染时注入 CLI §3.5 D5-A）；agate/assets/templates/dispatch-context.md（CARD-SOURCE 块外语义 + 双路径说明，正文不含字面锚点串）；agate/scripts/check-p6-provenance.py（审计 2 双锚点剥离 §3.6 D6-A，CARD-SOURCE 行起优先 + 物理块兜底）

## B1 实现进度 2（agate-next / advance / judge / loop-orchestration）
- agate-next.py 新建：三态分支（exit0→next 推进 add+state_transition / exit1→retreat 表值委托 retreat-to / exit2 非 P6 落盘 exit2-resolution；P6 特例 A1 裁决：provenance exit0 → judge 未启用直推 P7 / 启用跑 check-gate P6.5 exit0 推 P7、exit1 停留 P6 不落盘）；git 操作定位 repo root（-C），只 add 不 commit
- agate-advance.py 新建：--to diff≥2 提示先 PAUSED 不自行回退；diff=1 委托 retreat-to 单步；不传 --to 打印转移表建议
- check-judge-verdict.py：_strip_card 双锚点（CARD-SOURCE 行起物理块优先 + START..END 兜底，A2 同步面）；新增 8.1 exit2-resolution 复核（账本 gate_run exit:2 非 P6 → 需 {phase}-exit2-resolution.md frontmatter+三节完整，BDD-12）
- loop-orchestration.md 档位 C：46-74 定义段 + 229+ gate 处理流程改走 agate next + P6 特例裁决说明（§3.7）

## B1 测试结果（pytest 全 B1 文件 5.7s）
- 18 passed / 3 failed（21 用例）
- phases_transfer_fields 5/5、agate_advance_cli 2/2、judge_exit2_review 2/2、agate_next_cli 9/12
- 回归：unit 全量（除并行批）1191 passed 2 skipped；相邻 314+122 passed；ruff 全过；check-yaml-schema 3 OK；consistency --strict-errors-only 0 ERROR

## [DESIGN_GAP] B1 三用例与真实 check-gate exit 语义矛盾（证据，2026-09-02）
- test_bdd_7_next_exit1_delegates_retreat_to_retreat_target（P5 夹具）：注释假设 gate exit 1（mock）
  → 实测 check-gate P5 对 git_repo+P5-state 夹具恒 exit 2（gate_p5 无 baseline 场景不返回 1，P2-design 空）
  → 实现按 §3.4 exit2 通用分支落盘 resolution，phase 不推 P4 → 断言失败
- test_bdd_8_exit2_resolution_frontmatter_machine_readable（P3 夹具）：注释假设 gate exit 2
  → 实测 check-gate P3 对默认 task_dir（无 P3-test-cases.md）恒 exit 1（文件缺失）
  → 实现按 exit1 分支（P3 无 retreat 表值 → 提示重试）不落盘 → 断言失败
- test_bdd_11_state_transition_event_observable（P5 夹具）：单次 agate-next 期望 state_transition
  → 与同夹具的 test_bdd_8_non_p6（现绿，期望 exit2 落盘 resolution 不推进）**互斥**：同一 P5 exit2
  夹具既要求"落盘不推进"又要求"推进出事件"，且 gate_p5 无 exit0 路径 → 单次运行不可同时满足
- 判定：P1/BDD-6/7/8/11 与 §3.4 语义权威（exit1=retreat / exit2=非P6 resolution，P6 才特例）无歧义；
  实现忠实 §3.4；三用例夹具无法产出其断言所需真实 gate exit（夹具缺 mock 钩子，且 bdd_11 与
  bdd_8 同夹具互斥）→ 按 implementer 决策树不改测试，标 [DESIGN_GAP] 交由主 Agent 判定
  （建议：修 P3 测试夹具——bdd_7 P5 需能产出 exit1 的场景（如补 pre-task-baseline+fail-list），
  或改用真 exit0/exit1 阶段（P4/P7 可 exit0、P6 无证据可 exit1）构造；bdd_8 P3 需补
  P3-test-cases.md 使 gate exit2；bdd_11 需两次推进链或改用 P7→P8 exit0 场景）
- [PROD_NOT_TOUCHED]：本批只改 worktree agate/ 协议本体文件（phases.yaml/schema/两新 CLI/
  check-judge-verdict.py/loop-orchestration.md）+ 任务目录 progress；未触碰生产环境/主 checkout/~/.agate

## 夹具修复轮开工（test-designer，2026-09-03）
- 已读：dispatch-context、test-designer.md、3 红例 + 18 绿例全代码、conftest fixtures、
  agate-next.py 全文、agate_common.py（append_event/resolve_rules_root/read_rules_yaml）、
  check-gate.py gate_p3/p4/p5/p6/p65/p7/p8 + main 分发
- 关键机制确认：
  * agate-next.py 调 check-gate 走绝对路径 SCRIPT_DIR/check-gate.py（SCRIPT_DIR = agate-next.py 自身
    所在目录，env 无法重定向）→ stub check-gate 需复制脚本目录不可取（违背"不 mock 被测"）
  * 各 phase 真实 gate exit：P3 无 P3-test-cases.md→1 / 有→恒 2；P5 无 baseline→恒 2、
    有 baseline+captured_at_commit + fail-list 新增失败→1；P7 干净产物→0（唯一常见 exit 0）；
    P6 恒 2（合规 pass 也 2）；P6.5 judge 未启用→0；P8 恒 2
  * 修复方向改为**构造真实前置产出**（dispatch-context 允许的两路之一）：
    例1/例3 走真实 gate 判定，不 stub

### 修复方案设计（test-designer，2026-09-03）— 走真实 gate 判定路，不 stub check-gate
> 判据：dispatch-context 允许「构造真实可产 exit 的场景」；stub check-gate 需复制 scripts 目录
> （agate-next.py 用 SCRIPT_DIR/check-gate.py 绝对路径，env 无法重定向），违背"不 mock 被测"
> 且 diff 巨大。真实 gate 判定更贴近集成测试精神（agate-next 消费真实 gate 三态分支）。

- 例1 `test_bdd_7_next_exit1_delegates_retreat_to_retreat_target`（P5 夹具）：
  原失败根因 = check-gate P5 对无 baseline 的 git_repo 夹具恒 exit 2 → agate-next 走 exit2 分支落
  resolution 不推 P4。
  修复 = 构造 P5 gate exit 1 的真实前置：task 目录补 pre-task-baseline.md（含
  `captured_at_commit:` 标记 + ```fail-list 空块）+ P5-test-results/fail-list.txt（放一条
  fail-list 中不存在的测试名 = 新增失败）→ gate_p5 机械 diff 判新增失败 → exit 1
  （check-gate.py gate_p5 L1028-1032 return 1）→ agate-next exit1 分支查 phases.yaml
  P5.retreat=P4 → 委托 agate-retreat-to（单步 P5→P4 + retries[P4] 记录 + 独立 commit）。
  预期：phase=P4 + retries[P4] + rc=0，BDD-7 语义（exit 1 → 委托 retreat-to + retries 同步）不变。
  环境隔离：[PROD_NOT_TOUCHED]
- 例2 `test_bdd_8_exit2_resolution_frontmatter_machine_readable`（P3 夹具）：
  原失败根因 = task_dir 默认产物缺 P3-test-cases.md → gate_p3 恒 exit 1（文件缺失）→ 不走 exit2 分支。
  修复 = 夹具补写 `td/P3-test-cases.md`（占位内容）→ gate_p3 exit 2（存在即 2，L891-892）
  → agate-next 非 P6 exit2 分支落盘 P3-exit2-resolution.md（frontmatter 机器可读 + 触发/客观证据/解决
  三节）→ 断言的 frontmatter/三节全由实现产出（§3.3 模板），与 BDD-8 语义不变。
  预期：rc=0 + P3-exit2-resolution.md 存在且含 type: exit2-resolution / phase: P3 / task_id /
  parent / 三节标题。[PROD_NOT_TOUCHED]
- 例3 `test_bdd_11_state_transition_event_observable`（P5 夹具）：
  原失败根因 = P5 无 baseline 恒 exit 2 → 落盘不推进 → 无 state_transition 事件；且与
  test_bdd_8_non_p6_exit2（同 P5 exit2 夹具）互斥——同一场景不可能既"落盘不推进"又"推进出事件"。
  修复 = 把本用例推进场景迁移到**真实可 exit 0 的 P7**：task_dir 默认产物含干净 P7-consistency.md
  （conftest 创建）→ gate_p7 检查 blocker/devcrit/design_gap/code_map 全干净 → exit 0
  （check-gate.py L1241 return 0）→ agate-next exit0 分支消费 phases.yaml P7.next=P8 推进
  P7→P8 + append state_transition(from=P7/to=P8/ts)。
  预期：rc=0 + gate-events.jsonl 含 from/to/ts 齐全的 state_transition，BDD-11 证据面
  （推进经 agate next 产生可观测事件）不变，且与 exit2 落盘用例互斥消除。
  测试名与 docstring 同步更新（P7 锚点），用例意图（BDD-11 推进产生 state_transition）不删。

### 三例修复完成 + 验证（test-designer，2026-09-03）
- 例1 test_bdd_7_next_exit1_delegates_retreat_to_retreat_target：夹具补 pre-task-baseline.md
  （captured_at_commit: + 空 fail-list 块）+ P5-test-results/fail-list.txt（一条新增失败）
  → 真实 gate_p5 exit 1 → agate-next 委托 retreat-to P5→P4 + retries[P4]。
  验证：通过（rc=0 + phase: P4 + retries 记录）。
- 例2 test_bdd_8_exit2_resolution_frontmatter_machine_readable：夹具补 P3-test-cases.md
  → 真实 gate_p3 exit 2 → agate-next 落盘 P3-exit2-resolution.md。
  验证：通过（frontmatter type: exit2-resolution / phase: P3 / task_id / parent + 触发/客观证据/解决三节）。
- 例3 test_bdd_11_state_transition_event_observable：P5 exit2 夹具（与 bdd_8 exit2 落盘用例互斥）
  → 迁移到真实 exit 0 的 P7 场景（干净 P7-consistency.md → gate_p7 exit 0 → 消费 P7.next=P8）。
  验证：通过（rc=0 + gate-events.jsonl state_transition from=P7/to=P8 + from/to/ts 齐全）。
- 跑批 `timeout 300s python3 -m pytest agate/tests/unit/test_tag0027_b1_*.py -q --tb=short`：
  **21 passed**（3 红例全转绿，18 已绿零改动）
- 改动范围核对：git diff 仅 test_tag0027_b1_agate_next_cli.py（+31/-3，只动 3 个函数体与 docstring，
  断言未改）；agate-next.py / phases.yaml / check-gate.py 等实现零改动；BDD-7/8/11 验收语义未变
  （例1 仍测 exit1→retreat-to 委托 + retries；例2 仍测 exit2 resolution 机器可读 frontmatter + 三节；
  例3 仍测推进产生 state_transition from/to/ts 事件）
- 回归说明：改动纯测试文件、不被其他测试导入 → 无跨文件回归面；B1 批内 21 例全绿覆盖
  [PROD_NOT_TOUCHED]

## B3a 开工（implementer，docs-clean 批）
- 读 dispatch-context 完成：B3a 批 = 顶层 agate/*.md（除 loop-orchestration.md）语义叙述文档清理平台名污染
  + assets/ 两文件命中段挂注记；TDD 目标 = test_tag0027_b3a_platform_name_docs.py（5 用例）

## B3a 续做开工（implementer，2026-09-03，剩余 7 文件）
- dispatch-context（B3a-retry）已读：续做清单 = adr.md / AGENTS.md / dispatch-protocol.md /
  UPGRADING.md / WORKFLOW.md / assets/execution-roles/architect.md / assets/templates/custom-role.md
  （role-system.md 已完成不动）；约束三分类 + 注记统一格式 `> 实现注记：`；每完成 1 文件即追加本文件
- 回归锚点测试已读：test_tag0027_b3a_platform_name_docs.py（5 用例）——BDD-14 五模式锚点不变量 +
  banned 平台命名概念词；BDD-16 已知适用环境表存在 + 清理面文档含 `> 实现注记：` 标记行（≥1 即过，
  已由 role-system.md 满足）；BDD-17 dsh/ 结构豁免；BDD-23 render-dispatch-prompt CLI 回归
- 样板 git diff 已看：role-system.md（语义句去平台名 → "平台"泛指 + 平台细节入 `> 实现注记：` 段）
- git status：仅 role-system.md 已改 + P4-progress.md 本文件待续；7 目标文件当前未动

## B3a AGENTS.md 处理（implementer，2026-09-03）
- agate/AGENTS.md 命中 2 处，均判元信息豁免、正文零改动：30 行入口表指针行（OpenCode/Claude Code/Windows → platform-notes.md，导航指针指向整文件豁免权威源，P1 D-2 已判 AGENTS:30 豁免，指针不构成语义定义）；89 行升级 how-to 段（Windows 复制模式说明 → 指针 platform-notes.md「Windows 原生」章节，平台细节全委托豁免源）。判定证据：b3a 5 测试 cleaned_docs 不含 AGENTS.md（未锁定）、CHECK 14 扫描面 = is_protocol_file（agate/AGENTS.md 不在 PROTOCOL_FILES/PROTOCOL_DIRS，不在扫描面）→ 无需挂 `> 实现注记：`，不越批改结构
- [PROD_NOT_TOUCHED]

- adr.md 处理完成（B3a 续做）：命中段 = ADR-008 语境(原233行，OpenCode/Claude Code 接入方式缺失)、决策(原237行，`.claude/agents`/`.opencode/agents` 符号链接注册路径，大小写不敏感扫描命中)、权衡(原248行，frontmatter 字段兼容实测) 三段落各挂 `> 实现注记：` 标记行（P2 §6④ 决策叙事，不做整文件豁免）；理由节 CLAUDE.md 文件名指针判定非命中（banned 词为 Claude Code 短语，D-2 记 adr.md(2) 同口径）未挂注记；ADR 编号/日期/结论正文零改动；自检 grep -c '实现注记' agate/adr.md = 3

## UPGRADING.md 处理完成（implementer，2026-09-03，B3a 续做轮）
- 判定：整文件按「升级说明元信息」处理——UPGRADING.md 全文为面向存量项目的版本升级记录（文件头
  明示），平台名（DSH/workflow/task/Windows 等）全部描述"某版本加了什么"，是记录对象本身（历史
  事实，不删改）；按命中版本节挂 `> 实现注记：` 标记行（CHECK 14 豁免粒度 = 标题节内任一注记行
  即豁免整节，B3b 用例 test_bdd_22_check14_add_note_marker_pass 实证）
- 命中 4 节 → 各挂 1 条注记（节标题下首段；版本号/日期/变更内容一字未改）：
  1) v0.57.0（DSH ×8 行命中 303/307-312）——注记：平台支持变更史（RM-AG0030）历史叙事元信息
  2) v0.47.0（workflow @363 CI matrix）——注记：测试框架/CI matrix 变更史，workflow/CI 平台 job
     名是记录对象
  3) v0.49.0（task @483 task-files.md 文件名引用）——注记：派发编排机制变更史，task 词是文件/
     机制引用非平台工具指代
  4) v0.44.0（workflow @517 CI matrix）——注记：Windows 环境适配/CI matrix 变更史
- 自检：word-boundary 词表（OpenCode/Claude Code/DSH/workflow/ralph/goal/task）全文件扫描，
  UNCOVERED: none（无注记覆盖的命中段 = 0）；无豁免判定遗留未记录
- 测试：test_tag0027_b3a_platform_name_docs.py 5/5 绿；git diff = +16 行纯注记（4 段），0 删改
- [PROD_NOT_TOUCHED]：只改 worktree agate/UPGRADING.md + 追加本 progress；未碰主 checkout/
  ~/.agate/生产环境/其他文档文件

## B3a 续做收尾 2（implementer，2026-09-03，architect.md / custom-role.md）
- 词表扫描（OpenCode/Claude Code/DSH/workflow/ralph/goal/task 词边界）两文件各命中段确认：
  architect.md 仅 L229（"无 prompt 派发场景（如 OpenCode agent markdown）"举例；L117 "task 目录" 为
  通用协议词非平台工具指代，不命中）；custom-role.md L49（方法 A "OpenCode/Claude Code agent 目录"）
  + L54-56（"注意（OpenCode issue #29616）"节）——正文即平台注册方法说明，属适配说明段非语义定义
- architect.md（角色文件，语义定义零改动）：「分阶段落盘」节首挂 1 条 `> 实现注记：`——平台名仅作
  举例（agent markdown 直接派发无 prompt 场景），非协议语义定义；正文未改写（保留 OpenCode 举例于注记内）
- custom-role.md（平台注册方法模板）：「使用步骤」节首挂 1 条注记——方法 A/B 为平台注册适配说明
  （OpenCode/Claude Code 自定义 agent 机制），语义指 role-system.md「自定义角色」；「注意」节首挂
  1 条注记——OpenCode issue #29616 坑位实测属平台适配记录。两节平台正文（方法 A/B + 注意内容）不删
- 自检：git diff 两文件 = +9 行纯注记（3 段，架构语义正文 0 删改）；注记格式 `> 实现注记：` 与
  role-system.md 样板/B3b 段落级豁免判据一致；词表重扫 UNCOVERED: none
- [PROD_NOT_TOUCHED]：只改 worktree 两 assets 文件 + 追加本 progress；未碰主 checkout/~/.agate/
  生产环境/其他文档文件

## B3a dispatch-protocol.md 处理完成（implementer，2026-09-03）
- 命中段处理（挂注记/去平台化，五模式锚点一字未动）：
  1) 铁律 1 标题 + 正文去平台化（"task 工具"→"派发 subagent/派发工具"），句首挂 `> 实现注记：`
     注明 task/Claude Code Task 是平台实现命名（语义句"主 Agent 不自己产出、派发 subagent"保留）
  2) 执行模式节（166/168/179 行）：标题去平台化 →"支持 subagent 派发 vs 单 Agent"；intro 段下挂
     注记（task 工具/has_task_tool/Claude Project = 平台适配说明）；179 行改"切换到支持 subagent
     派发的平台"
  3) 执行模式表（164 行下方，P1 待复核）：判定 = 无直接平台名但语义依赖 has_task_tool 平台字段 →
     表头上方 intro 段挂注记说明"平台适配、与具体工具名无关"（免独立表格注记）
  4) OpenCode 坑位（1108 行）：整节段首挂 `> 实现注记：`（平台细节 OpenCode/issue #29616/opencode
     .jsonc/subagent_type 全部归入注记段），正文去平台化为"自定义 agent 调用坑位"
  5) 其他 task 工具引用：261 行 fence 内"派发 subagent（task 工具）"→"派发工具"；580 行"多次 task
     调用"→"多次派发调用"；574 行"在一个 task 里"→"在同一次派发中"；653/706/940 行 "Task 工具"
     →"派发工具"（653 段挂注记说明平台无超时参数属平台能力事实）；1120 行 fence 内"调用 task 工具"
     →"调用派发工具"
  6) task-files.md 引用等字段名语境（212/229 行 P0-brief yaml task 字段示例、223 行 platform 枚举
     值 opencode/claude-code/codex/claude-project）不动——代码围栏内 + 字段名语境（数据面豁免）
- 验证：词表重扫 = 剩余命中全在注记段/注记紧邻段/代码围栏；B3a 5 用例全绿；consistency
  --strict-errors-only 0 ERROR
- [PROD_NOT_TOUCHED]：只改 worktree agate/dispatch-protocol.md + 追加本 progress；未碰主 checkout/
  ~/.agate/生产环境/其他协议文件

## B3a WORKFLOW.md 处理完成（implementer，2026-09-03）
- 命中分类与处理（word-boundary 词表全扫描后逐段判定）：
  1) L5 文档头部「适用：OpenCode / Claude Code / Codex…」——适用平台声明（文件头元信息）→ 头部
     块quote 内挂 1 条 `> 实现注记：`（声明为元信息 + 版本行/版本策略同为元信息；正文语义与平台
     无关）——注记行与命中行同段双粒度豁免（段落级 + 整文件头块quote 段覆盖）
  2) L138 能力对比表「task 工具」行 + L153/155 Claude Project 会话定位/建议工作方式 + executor_env
     声明——`## 运行环境前提` 整节为平台运行前提适配说明 → 节首挂 1 条注记（任务书判定①③④归并，
     标题节豁免粒度覆盖 L138/L147/L153-157/L162/L164 全部命中）
  3) L141-148「已知适用环境」表（L152-157 现文件）——**整表结构豁免区（CHECK 14 行级豁免）**：
     表行一字未改，记录豁免判定（行 154-157 平台名 = 元信息，CHECK 14 按表行跳过）
  4) L168「中任务（Claude Project 会话）」建议工作方式表行——`## 适用边界` 节首挂 1 条注记
     （平台间交接工作流建议，任务书判定④）；任务类型分层语义与平台无关
  5) L191「roadmap / plan / task 如何挂接」规划概念节（task = {Txxx} 工作单元，非平台工具）→
     节首挂 1 条注记说明词义（同 architect.md:117 通用协议词口径，挂注记双保险）
  6) L21/L360「task 工具」作派发动词宾语 → 去平台化改写"平台的派发工具/派发工具"（dispatch-
     protocol.md 铁律 1 同口径，该处已有权威注记）；语义句（用派发工具派发 subagent）未变
  7) L75 task-files.md / L222-225 代码围栏内 task → 文件名字段语境 + 代码围栏跳过（数据面/围栏
     豁免，同 dispatch-protocol 212/229 行处理口径）
- 自检：词表重扫剩余命中 = 注记段内（5-8/137-141/206-209）+ 注记紧邻表格区（147/152/154-156/162/
  164/181 命中行位于所挂节注记之后，标题节豁免粒度覆盖）+ 豁免表行（154-157）+ 代码围栏（222-225）
  + 字段名语境（78/164 task-files）；UNCOVERED: none；已知适用环境表行零改动；S1S2-ANCHOR
  阶段总览表（283-304 区）未动
- 测试：test_tag0027_b3a_platform_name_docs.py 5/5 绿；consistency --strict-errors-only 0 ERROR
- [PROD_NOT_TOUCHED]：只改 worktree agate/WORKFLOW.md + 追加本 progress；未碰主 checkout/
  ~/.agate/生产环境/其他协议文件

## B3b 开工（implementer B3b 轮）
- 已读 dispatch-context P4-dispatch-context-implementer-B3b.md + 角色 implementer.md
- 任务：WORKFLOW.md 总览表加 next/retreat 列（S1S2-ANCHOR 区域）+ check-structure-consistency.py S-1/S-2 加列扩展 + check-protocol-consistency.py 新增 CHECK 14/15；9 用例 TDD 目标
- 下一步：读 B3b 测试 2 文件 9 用例 → 再读 P2 §3.2/§3.8 定案原文 → 逐个改动点落盘

## B3b-1 开工（implementer，S-1/S-2 加列扩展子批）
- 任务：WORKFLOW 总览表加 next/retreat 4/5 列（P0-P8+P6.5 填值，READY 不加）+ check-structure-consistency.py
  _parse_workflow_rows 5 元组 + _check_s1 next/retreat 比对 + P6.5 gate_subphase 特判
- 已读：implementer.md 角色 + P4-dispatch-context-implementer-B3b.md + test_tag0027_b3b_structure_s1s2_next_retreat.py（3 用例）+
  test_check_structure_consistency.py（既有 17 用例）+ _rules_test_utils.make_fake_root + conftest fixtures +
  check-structure-consistency.py 现状 + WORKFLOW.md S1S2-ANCHOR 区域（309-319 行表体）+ phases.yaml 实际
  next/retreat 值（B1 已加）+ phases.schema.json（B1 已声明）+ P2-design §3.2 定案
- 实际值核对（phases.yaml 主线）：P0 next:P1/retreat:null；P1→P2/null；P2→P3/null；P3→P4/null；P4→P5/null；
  P5→P6/retreat:P4；P6→P7/retreat:P4；P6.5 无 next/retreat 但 gate_subphase{hosted_on:P6,forward_to:P7,
  needs_revision_to:P6}；P7→P8/null；P8 next:null/retreat:null
- 测试语义确认：3 用例仅 S-1 比对（假树 P1/P2/P3 主线带 next/retreat + READY 行 7 列）；retreat/next 不一致 →
  exit 1；一致 → exit 0。P6.5 不在假树（S-1 只比 phases.yaml 出现的 phase）
- 红灯实测：test_tag0027_b3b_structure_s1s2_next_retreat.py = 2 failed（B 类红：next/retreat 不一致未检出 exit 0）
  + 1 passed（一致场景回归守卫）；test_check_structure_consistency.py = 17 passed 基线绿

## B3b-2 开工（implementer，CHECK 14/15 子批）
- 已读：B3b dispatch-context + implementer 角色 + 被测 6 用例全文 + P2 §3.8 定案 + P1 BDD-15/16/22/24 原文
  + 参照 test_check_protocol_consistency.py（Report 形态/importlib）+ conftest fixture（未直接读到文件，
  用例里 fixture 名 = agate_scripts / tmp_path）→ 函数签名定：check_md_platform_paragraphs(root, rep) /
  check_rules_platform_tokens(root, rep)，e["check"] = "CHECK14-platform"/"CHECK15-rules"（.startswith 判定）。
- 词表：契约明列 OpenCode/Claude Code/DSH/workflow/ralph/goal/task——按**大小写敏感 + 词边界**实现
  （bdg 词表本身即原文大小写；"workflow" 若大小写不敏感会与文件名 WORKFLOW.md 大写产生海量误报，
  且 B3a 实证自检均用 word-boundary 大小写敏感口径——UNCOVERED: none 基线同口径）。
- 扫描面定案：CHECK 14 扫描对象 = **iter_md_files + is_protocol_file**（P2 §3.8 字面 + dispatch-context
  约束 3；B3b 4 用例的 agate/WORKFLOW.md 属 PROTOCOL_FILES、新增 agate/*.md 顶层文件将被 is_protocol_file
  命中仅当在 PROTOCOL_FILES/PROTOCOL_DIRS——BDD-24 用 agate/new-future-protocol.md 顶层（不在清单）会
  ERROR 或豁免取决于实现）——按"语义叙述面 = agate/ 顶层协议 md + assets/ 非豁免 md 适配说明段"实现，
  见下一步实测树验证（目标：对现 worktree 0 ERROR + 4 用例语义过）。
- CHECK 15 对象 = agate/rules/*.yaml + agate/rules/schema/*.json（含注释、词边界大小写敏感）；
  豁免词典 = schema property 名 ∪ phases.yaml task_fields 值 ∪ dispatch.yaml 顶层键/模式枚举等既有键名
  （机械生成：只豁免"含 task 子串的既有键"，裸平台词仍 ERROR）。task_fields 值如 risk_level 不含平台词，
  真实豁免价值 = 键名 task_fields/task_id 自身；B3b 用例夹具键值全为 task_fields/task_id → 键名豁免足够。
- 风险：dispatch-context 声称 law-1 已去平台化，但实测 dispatch.yaml L19 law-1 仍含 "task 工具" → CHECK 15
  真实树会命中（如 law-1 的 task 未豁免）——需在实现后实测校准；若 0 ERROR 不可达，标 [DESIGN_GAP]。

### B3b-1 改动点 1：WORKFLOW.md 总览表加列完成
- 表头/分隔行：`| 阶段 | 名称 | 执行角色 | next | retreat | 评审角色 | 门槛（…）|`（7 列，next/retreat 落 4/5 列）
- S1S2-ANCHOR 锚点注释同步：说明第 1-3 列 = 既有比对列、第 4/5 列 = next/retreat 扩展比对列
  （YAML null ↔ 表 `—`/空归一）
- 行值（对齐 phases.yaml B1 实际值）：P0 next=P1/retreat=—；P1 P2/—；P2 P3/—；P3 P4/—；P4 P5/—；
  P5 P6/P4；P6 P7/P4；P6.5 next=—（gate_subphase: 通过→P7）/retreat=—（needs-revision→P6）注释形态
  （非 plain P7）；P7 P8/—；P8 next=—（无自动后继）/retreat=—（失败重试本阶段）；
  READY 行 = 7 列结构但 next/retreat 单元格留空（§3.2「READY 行不加 next/retreat 列内容」）
- 验证：sed 列数核对 P0-P8/P6.5/READY 行均 7 列（P2/P4/P7 因门槛单元格内 grep 模式历史性内嵌 `|` 计数偏高，
  行结构不受影响——S-1 正则只消费前 3 列）

### B3b-1 改动点 2：check-structure-consistency.py S-1/S-2 加列扩展完成
- `_TABLE_ROW_RE` 不动（P2 §3.2 实证：不锚行尾只消费前 3 列 → 加列向后兼容）；新增
  `_TABLE_CELL5_RE`（取第 4/5 列 next/retreat 单元格，缺失 → None）
- `_parse_workflow_rows` → 5 元组 (id, name, role_cell, next_cell, retreat_cell)；旧 3 列表行
  4/5 列取 None（向后兼容）
- 新增 `_norm_transfer_cell`：表单元格 `—`（含 `—（…）` 注释形态）/`-`/`–`/空 → None（YAML
  null 归一）；plain phase id 原样返回
- `_check_s1` 增比对：phase 声明了 next/retreat 才比对表 4/5 列（YAML null ↔ 表 —/空 归一；
  未声明跳过——schema 仅 required id/name/exec_role）；P6.5 走 gate_subphase 分支 → 形态级
  负面检查：md 4/5 列不出现 plain 独立后继 phase 值（`_PHASE_ID_RE` 整格匹配）
- `_check_s2` 解包同步 5 元组（行为不变：只反查 phase id 存在性）
- 验证：B3b-1 3 用例 + 既有 structure 17 用例 = 20/20 全绿；真实 worktree 根
  check-structure-consistency.py = S1-S6/S0 全 OK exit 0；ruff clean；P6.5 负面分支实测
  （真实树副本把 P6.5 next 列改 plain P7 → S-1 ERROR exit 1 命中）

### B3b-1 收尾验证（implementer，2026-09-03）
- `_TABLE_CELL5_RE` 方案改为行 split 取 4/5 列 + 内容列数 ≥6 判定（旧 3/5 列表无 next/retreat
  列 → None 向后兼容；避免把旧 5 列表的评审角色/门槛误当 next/retreat——新 7 列表才是加列形态）
- 真实表解析核对：P0-P8+P6.5 十行 next/retreat 单元格全部正确（P5/P6 retreat=P4、P6.5 注释
  形态、P8 null 注释形态、主线 next=P{n+1}）
- B3b-1 3 用例 + 既有 structure 17 用例 = 20/20 全绿；真实 worktree 根 structure 检查
  S1-S6+S0 全 OK exit 0；ruff clean；P6.5 负面分支复验（真实树副本改 plain P7 → S-1 ERROR
  exit 1 命中）；相邻回归（b3a 5 + docs_assertions + protocol_dedup_audit + debt_check 共 56）
  全绿；unit 全量 sweep = 1229 passed 2 skipped 6 failed——6 failed 全属 B3b 另一子批
  test_tag0027_b3b_protocol_check14_check15.py（CHECK 14/15 未实现，stash 验证在我改动前即红）
- 改动范围：仅 agate/WORKFLOW.md（S1S2-ANCHOR 总览表区域 30 行）+ agate/scripts/
  check-structure-consistency.py（82 行）；未 commit；未碰主 checkout/~/.agate/生产环境
- [PROD_NOT_TOUCHED]

## B3b-2 语义定案（实测校准后，2026-09-03）
- 段落粒度定案 = **标题节内注记豁免整节**（B3a UPGRADING 条目实证 + test_bdd_22_add_note 用例：
  注记行与命中行同属一个 `## 某节`，空行分段会拆开二者致红 → 标题节粒度是唯一使该用例过的读法）。
- 词边界大小写敏感 + 排除 `[A-Za-z0-9_-]` 邻接：task-files.md/task_id/task_fields/pre-task-baseline.md
  等文件名/字段名/路径复合词不命中（下划线是 \w，连字符复合词用邻接排除）；WORKFLOW.md 大写
  不命中 workflow（CONTEXT/state-machine 大量大写引用因此 0 命中，与 P1 D-2 grep 口径一致）。
- 扫描面 = iter_md_files 协议面：is_protocol_file 成员 + **agate/ 顶层 *.md 结构覆盖**（BDD-24 的
  new-future-protocol.md 不在任何名单却须命中 → 名单机制不可用，顶层 agate/*.md 结构入面）；
  整文件豁免 platform-notes.md/SETUP.md + assets/templates/dsh/ + 已知适用环境表行（标题行锚点 +
  后续连续 `|` 行）+ 注记节。
- CHECK 15 数据面文件双基路径（root/rules 测试夹具 + root/agate/rules 真实布局）；豁免词典 = 解析
  键名 identifier 集合（_/- 邻接已天然排除 task_id/task_fields；词典兜底未来裸键名）。
- **[DESIGN_GAP 候选]** 实测数据面 dispatch.yaml L19 law-1 仍含 "task 工具"（B3a 未处理 rules/，
  dispatch-context 声称已去平台化不实）→ CHECK 15 真实树首跑必 1 ERROR；loop-orchestration.md L205 /
  AGENTS.md L30 / dispatch-protocol L217 等标题节无注记 → CHECK 14 真实树首跑可能 >0。实现后实测
  取证，若 >0 无法在本批独占文件内消除 → 如实上报主 Agent（不弱化检查语义掩盖）。

## B3b-2 语义终定（实测收敛，2026-09-03）
- 扫描面终定 = **agate/ 顶层 *.md**（BDD-16 Given `agate/*.md` + BDD-24 新顶层文档自动覆盖，
  assets/phase-cards/rules md 属非叙述面不扫——B3a P2-review A3 实证 assets 命中仅 3 处、SKILL 目录
  豁免 + architect/custom-role 命中段注记，若机械扫 assets 的 analyst/phase-cards 裸 task 引用会
  大量误报 → 叙述面 = 顶层）。整文件豁免 = platform-notes.md/SETUP.md（平台适配权威源）+
  AGENTS.md/CONTEXT.md（入口导航/术语元信息，B3a AGENTS 判定记录：元信息不挂注记）。
- 段落粒度 = 标题节（`^#{1,6} ` 起新节）；节内任一行 `^> 实现注记：` → 整节豁免（B3a 各文件
  注记均挂节首、测试用例注记行与命中行同节，标题节粒度是唯一自洽读法）；代码围栏 CommonMark
  闭合（`^```{3,}\s*$`，info string 行不闭）整段跳过；「已知适用环境」节内 `|` 表行豁免。
- 词边界 = (?<![\w-])tok(?![\w-]) 大小写敏感：task_id/task_fields/task-session-summary.md/
  pre-task-baseline.md/WORKFLOW.md 大写文件名全天然不命中（与 P1 D-2 grep 口径一致）。
- CHECK 15 双基路径 root/rules + root/agate/rules（测试夹具 = root/rules 布局）；豁免词典 = 数据面
  键名/字段值机械收集（schema properties ∪ yaml 键 ∪ task_fields/fields 值），裸平台词仍 ERROR。
- 实测残余取证（将实现的精确语义）：CHECK14 叙述面残余 = AGENTS(L30, 已豁免) + loop-orchestration
  L205「落地建议」OpenCode/task 前提无注记（B1 独占文件未清，B3a 除名未处理）→ 首跑 1 ERROR；
  CHECK15 残余 = rules/dispatch.yaml L19 law-1 "用 task 工具派发"（B3b context 声称已去平台化不实，
  B3a commit 未动 rules/）→ 首跑 1 ERROR。两处残余均在**本批独占文件之外**（loop= B1 文件、
  dispatch.yaml=数据面）→ 如实上报，不弱化检查语义掩盖。

## B3b-2 CHECK 14/15 实现完成（2026-09-03）
- 改动 = 仅 agate/scripts/check-protocol-consistency.py：
  1) 模块 docstring CHECK 清单 + 2 行（CHECK 14/15 说明）
  2) CHECK 14：PLATFORM_TOKEN_RE（(?<![\w-])tok(?![\w-]) 大小写敏感词边界）+
     _MD14_WHOLE_FILE_EXEMPT（platform-notes/SETUP/AGENTS/CONTEXT）+ _split_md_sections
     （标题切节 + CommonMark 列0围栏跳过 + 空行不切节）+ check_md_platform_paragraphs
     （节内 > 实现注记： 整节豁免 + 已知适用环境节表行豁免 + 顶层 agate/*.md 扫描面）
  3) CHECK 15：_iter_rules_files（双基路径 root/rules + root/agate/rules，yaml+schema json）+
     _collect_rule_exempt_tokens（JSON property 名 ∪ YAML 键机械生成豁免词典）+
     check_rules_platform_tokens（键定义行键名在豁免词典 → 整行豁免；其余行词边界平台词 ERROR）
  4) CHECKS 注册 CHECK 14/15（追加编号，不动既有 1-13）
- 验证：
  * B3b-2 6 用例 + 既有 test_check_protocol_consistency 33 用例 = 39 passed（0 failed）
  * ruff（~/.venvs/agate-dev）clean；无 SyntaxWarning
  * 真实 worktree 首跑：CHECK 14/15 报 3 ERROR = agate/dispatch-protocol.md:234
    （「标准派发流程」P0-brief task 字段自查段，B3a 判字段名语境豁免但未挂注记）+
    agate/loop-orchestration.md:205（「落地建议」OpenCode/task 工具前提，B1 独占文件未清）
    + agate/rules/dispatch.yaml:19（law-1 "用 task 工具派发"，B3b context 声称已去平台化不实）
  → 3 残余均在**本批独占文件之外**（loop-orchestration.md=B1 文件、dispatch.yaml=数据面、
    dispatch-protocol.md=B3a 文件但漏挂该节注记）；按 implementer 决策树不改测试不弱化检查
    语义 → [SCOPE+] 上报主 Agent 路由补清（loop 注记 / dispatch.yaml law-1 去平台化 /
    dispatch-protocol 标准派发流程节挂注记），CHECK 14/15 语义本身与 P2 §3.8 定案一致。
- [PROD_NOT_TOUCHED]：只改 worktree agate/scripts/check-protocol-consistency.py + 追加本 progress；
  未碰主 checkout/~/.agate/生产环境/测试文件。

## B3b-2 CHECK 15 简化 + 最终验证（2026-09-03）
- CHECK 15 内层豁免循环简化（原 any(tok in e ...) 对复合键永不匹配，属死代码且语义可疑）→
  改为：豁免词典 = JSON property 名 ∪ YAML 既有键（机械生成）；键定义行（^key: / ^"key":）键名在
  词典 → 整行豁免；其余行词边界平台词扫描。task_fields/task_id 因下划线词字符邻接天然不命中。
- 复验：B3b-2 6 用例 + 既有 test_check_protocol_consistency 33 + B3a 5 = 44 passed；
  ruff clean；py_compile OK；无 SyntaxWarning。
- 真实树首跑残余 3 ERROR 逐条定性（均在**本批独占文件之外**，不改测试不弱化语义）：
  1) agate/dispatch-protocol.md:234「标准派发流程」P0-brief 自查节 "- task：是否工程视角一句话描述"
     ——task 指 P0-brief **字段名**（数据模型语境），B3a 分类 = 字段名语境豁免（未挂注记）；
     纯词边界机械扫描会把字段名叙述当平台工具引用命中 → **md 叙述面 task 字段语境 vs 平台工具
     指代需 P2/评审定夺**（[DESIGN_GAP 候选]：机械判据无法区分，B3a 靠人工分类）
  2) agate/loop-orchestration.md:205「落地建议」"OpenCode 自定义角色能被 task 工具调起来"
     ——真平台名/工具引用无注记；loop-orchestration.md 归 B1 独占文件，B1/B3a 均未挂该节注记
     → 存量清理遗漏（真缺口，CHECK 14 正确捕获）
  3) agate/rules/dispatch.yaml:19 law-1 "用 task 工具派发" ——B3b dispatch-context 声称
     "law-1 已由 B3a 去平台化"不实（B3a commit 未动 rules/）；P2 §6② 明确 law-1 属清理对象
     → 数据面存量未清（真缺口，CHECK 15 正确捕获）
- [SCOPE+] 上报主 Agent：补清 3 处（loop-orchestration L205 节挂注记 / dispatch.yaml law-1 改写
  "subagent 派发" / dispatch-protocol L234 挂注记或裁定字段语境豁免规则）后 CHECK 14/15 真实树
  首跑 0 ERROR 可达；本批独占文件内无法消除（不在 check-protocol-consistency.py）。

## B3b-3 B3 补漏：3 处残余平台名定点修复（2026-09-03）
- 背景：CHECK 14/15 首跑 3 ERROR（CHECK14×2 + CHECK15×1）为 B3a/B1 清理漏网，本批定点补清；
  只改 3 个文件，不 commit（[PROD_NOT_TOUCHED]：worktree 内改，未碰主 checkout/~/.agate/测试/生产）。
- 1) agate/rules/dispatch.yaml:19（CHECK 15 数据面）law-1 rule 值去掉平台工具名 task →
  "派发 subagent 而非亲自执行，动词是派发不是执行"——保留 law-1 纪律语义（主 Agent 不自己产出、
  派发 subagent），不改 YAML 结构/id/其他 law。已 grep 确认无测试/夹具/顶层协议叙述引用旧串。
- 2) agate/loop-orchestration.md:205（CHECK 14）「落地建议」前提第 4 条：平台适配前提 → 整条改写为
  平台无关语义（"先验证当前平台能调起自定义角色"）+ 段后挂 `> 实现注记：`（列 0）承载平台细节
  （OpenCode / task 工具 / issue #29616 / dispatch-protocol.md 平台适配指针），通用语义保留。
- 3) agate/dispatch-protocol.md:234（CHECK 14）P0-brief 四字段自查节 "- task：…"：task 为 P0-brief
  frontmatter 字段名语境（非平台工具），文档侧定点 → 自查块后挂 `> 实现注记：`（列 0）说明 task 为
  机器字段名（YAML 键），非平台派发工具指代；该行在代码围栏外属叙述面，挂注记豁免，不动脚本
  （选任务 b 优先）。
- 踩坑记录（注记必须列 0）：首版注记沿用外层列表 3 空格缩进 → checker 的 `_NOTE_MARKER_RE`
  （^>\s*实现注记：，列 0 锚定）不识别该注记 → 节未豁免 + 注记自身 task 词成为新命中（临时
  2 ERROR @234/@240）；去缩进到列 0 后注记被识别、整节豁免。参照样板 role-system.md:141/145 注记
  均为列 0。
- 验证：CHECK 14/15 首跑 0 ERROR 达成（exit 0，仅存量 324 WARNING = 历史死链 DEBT0012 语义）；
  dispatch.yaml yaml.safe_load 通过；pytest 44 passed（test_check_protocol_consistency 33 +
  test_tag0027_b3a_platform_name_docs 5 + test_tag0027_b3b_protocol_check14_check15 6）；
  未跑 ruff（未改 .py）。git diff 确认仅 3 文件各 1 处 + 无其他改动混入。

## P4 review 开工（2026-09-03）
- 独立 review subagent 开工：读 dispatch-context + review 角色文件完成；评审对象 = B1+B2（57e5f1c）+ B3a（15505bf）已 commit + B3b 工作区未 commit

## P4 review 开工 2（读项目约定）
- 已读 review.md 角色 + P0-brief + P1-requirements（25 BDD 语义）+ P4-implementation 汇总 + P4-progress 全量

## P4 review 核查项 1-3（代码阅读）
- 全读 agate-next.py / agate-advance.py / agate-dispatch.py + check-judge-verdict.py 双锚点剥离 + exit2-resolution 复核 diff + phases.yaml/schema diff + loop-orchestration diff + check-p6-provenance 双锚点 diff
- 核查发现（待实验确认）：① schema 缺 if/then 条件约束（P2 §3.1/§7 要求 P6.5 有 gate_subphase 且无 next/retreat 的 schema 强制 + 主线 next/retreat 必填——实现只有 optional enum 声明）② BDD-12 judge 复核谓词过宽疑点：gate_run exit:2 是 P0/P1/P2/P3/P5 等阶段的正常通过码（pre-commit 每次 commit 都记），非仅 exit-2 暂停事件

## P4 review 核查项 4-7（实验验证 + 评审推进）
- B1/B2 23 用例 + B3a/B3b/phases 19 用例全绿（实测）
- 真实树 CHECK 14/15 PASS、structure S1-S6 exit 0、yaml-schema 3 OK
- 【实验确认 CRITICAL-1】agate next 对"gate exit 2 = 正常通过码"的 phase（P1/P2/P3/P5/P8 等）
  误判为"需自判"→ 落盘 exit2-resolution + 暂停不推进（实测：完整 P1 产物 → check-gate exit 2 →
  agate-next 落盘 P1-exit2-resolution.md 且 phase 停在 P1）——与 档位 C 自动推进（BDD-11）
  直接冲突：除 P4/P6/P7 外几乎所有正常 phase 推进都会被 CLI 卡死
- 【实验确认 CRITICAL-2】BDD-12 judge 复核谓词把"正常通过的 gate exit 2 事件"（P0-P3/P5/P8 的
  正常通过码，pre-commit 每次 commit 都写账本）当"exit2-resolution 缺失"→ 实测健康任务全历史
  ledger（P0-P5 exit 2 正常推进）judge verdict 复核 exit 1 误拦

## P4 review 核查项 8-9（推进 CLI 语义碰撞量化）
- 各 phase 正常成功码（check-gate.py 实证）：P0/P1/P2/P3/P5/P8 恒 exit 2（成功也 2）；
  P4/P7 成功 exit 0；P6 恒 exit 2（成功也 2）；P6.5 judge 跳过 exit 0
- agate-next.py 对 exit 2（非 P6）= 落盘 exit2-resolution + 暂停 → 除 P4/P7 外几乎全部正常
  阶段推进都会卡死（BDD-6/11 语义被架空）——CLI 只在 P6 特例(P6 恒 exit 2)与 P4/P7 exit 0
  上自洽，正常 P0/P1/P2/P3/P5/P8 主线推进无法经 agate next 走通
- BDD-12 judge 谓词把正常 exit 2 成功事件当"exit 2 暂停事件"——健康任务全历史 ledger 必被
  误拦（实测：完整 P0-P5 正常 ledger → judge 复核 exit 1 缺 P0/P1/P2/P3/P5-exit2-resolution）

## P4 review 实验结论固化（CRITICAL-1/-2 实证）
- CRITICAL-1 再确认：agate-next.py 对非 P6 exit 2 分支——落盘 resolution 后无论文件是否已存在
  都 exit 0 不推进（_write_exit2_resolution 返回后 main 只打日志退出，无"resolve 后推进"路径）
  → exit-2 正常通过 phase 在 CLI 内是死路，主 Agent 只能手改 .state.yaml（违反 BDD-11）
- CRITICAL-2 再确认：check-gate P6.5（真实 judge gate）对健康全历史 ledger（P0-P5 正常 exit:2）
  exit 1 误拦——所有 judge 启用任务（2026-08-22 后全量）到 P6.5 必失败；TAG0027 自身
  ledger 含 P0-P3 exit:2 + judge.enabled → 自我证明会触发
- 全量 tag0027 44 用例 + 相邻 371 用例全绿（回归面无破坏）；CHECK14/15/structure/schema 真实树全过

## P4 review 核查项 10-11（schema 条件约束 + BDD-2 语义）
- 【DEVIATION 确认】phases.schema.json 无 if/then/not 条件约束（validator 只支持 type/required/
  enum/properties/items/additionalProperties/minItems 子集，check-yaml-schema.py 无参数固定校验
  AGATE_ROOT 下 rules）——P2 §3.1/§7「schema if/then 拦截 next: P6.5 独立边 + 主线 next/retreat
  必填」未落地；反例 P6.5 写 next: P7 当前 schema 校验通过（数据面真值靠 test_bdd_2 断言 phases
  .yaml 实际无 next/retreat 键保证，非 schema 强制）
- BDD-2 语义（"不出现指向独立后继的主线转移语义"）由数据面实值 + S-1 P6.5 负面形态检查兜底，
  但 schema 级强制缺失 → 若未来有人给 P6.5 加 next: P7，schema 不拦、S-1 会拦（md 表不写）——
  部分缓解但偏离 P2 定案（DEV/中）
- B3b WORKFLOW 表 + S-1 next/retreat 比对 + P6.5 形态负面检查（实测 20/20 绿 + 负面分支实测命中）

## P4 review 核查项 12（CRITICAL-2 谓词细读）
- _check_exit2_resolution 只按 event/exit==2/phase!=P6 判，无 runner/cmd/时间/后随推进判别——
  无法区分"正常通过的 exit 2"（pre-commit 对 P0-P3/P5/P8 成功 commit 恒记）与"真 exit 2 暂停"

## P4 review 核查收尾（CRITICAL-1 全谱系 + DEVIATION）
- CRITICAL-1 全谱系：check-gate exit 0 仅 P4（需暂存代码，commit 后 index 清空 → 独立跑 gate_p4
  反而 exit 1）/P7 可达；P0/P1/P2/P3/P5/P8 成功恒 exit 2；P6 恒 exit 2。→ agate next 对"post-commit
  推进"在绝大多数 phase 上不可用（P0-P3/P5/P8 → 落盘假 resolution 停住；P4 commit 后 index 空 →
  gate_p4 exit 1 → 无 retreat → 提示重试不推进；唯一可用 = P7→P8）。BDD-11"档位 C 全程经 agate
  next 推进"在实际协议语义上不可达成 = 核心交付失效
- DEVIATION-2：CHECK 14 实现只扫 agate/ 顶层 *.md；P2 §6③ 扫描面含"assets/ 非豁免 md 适配说明段"
  ——实现比设计窄（assets 平台名污染后续无机械拦截）
- 正面确认：44 新用例 + 371 相邻回归全绿、真实树 CHECK14/15/structure/schema 全过、A2 双锚点
  2p hash 实测匹配、B3a 清理 0 残余、S-1 next/retreat + P6.5 负面形态实测命中
- 判：rejected（2 CRITICAL + 2 DEVIATION）

## P4 review 产出完成
- P4-review.md 已写（status: rejected，2 CRITICAL + 2 DEVIATION）；frontmatter-check exit 0；
  自检：文件存在非空（170 行/8.5KB）+ status/agent/phase 解析正确 + [PROD_NOT_TOUCHED]

## exit2fix 实现开工（implementer，2026-09-04）
- 已读：dispatch-context（exit2fix）+ implementer.md 角色 + P4-progress 全量
- 任务：修复 P4 review 2 CRITICAL——gate_pass_exit pass_set 判定（exit 2 双义）+ judge Fix C 谓词

### exit2fix 输入阅读 + 现状分析（2026-09-04）
- 已读：P4-review.md（CRITICAL-1/2 实证 + Fix A/C）+ P2-design 修正版 §3.1/§3.3/§3.4（gate_pass_exit 表 +
  Fix C 谓词 + pass_set 三态）+ P1 BDD-6/8/12/13/26（回改后新语义）+ 现实现全文件
- 现实现问题确认：
  * agate-next.py main()：rc==0 → 一律直推、rc==2 → 非 P6 无条件落盘 resolution —— 未按 gate_pass_exit
    pass_set 判定（P0-P3/P5/P8 成功码恒 2 → 误落盘假 resolution 卡死主线 = CRITICAL-1）
  * check-judge-verdict.py _check_exit2_resolution：账本凡 gate_run exit:2（非 P6）强制要求 resolution
    文件 —— 健康任务 P0-P5 正常通过 exit:2 事件被误拦 = CRITICAL-2
  * phases.yaml/schema：10 条目均无 gate_pass_exit 键（schema items.required 无该键）
  * check-gate.py 头注释：exit 2 = 需主 Agent 自判（旧语义，与 BDD-13 R8 新口径冲突）
- 测试受影响面盘点（须按新语义改/补）：
  * test_bdd_6_next_exit0_advances_to_next_phase（P5）→ 新语义下 P5 exit 2 ∈ pass_set 直推 P6，
    正好补"健康任务 exit:2 直推"锚点
  * test_bdd_8 两用例（P5/P3 exit 2 落盘）→ 新语义 P5/P3 的 exit 2 ∈ pass_set 不落盘 → 换 P4
    真暂停锚点（P4 pass=0，P4-review approved 无 agent → gate_p4 L913 return 2 ∉ {0} = 真暂停）
  * test_bdd_12_judge_review_gate_run_exit2_without_resolution_fails → Fix C 反向（无 resolution 文件
    + 健康 exit:2 账本 → 通过不误拦）
  * test_bdd_13 头注释断言 "exit 2 = 需主 Agent 自判" → 改新口径断言
  * test_bdd_6_p6_judge_disabled_direct_p7_anchor / bdd_9 / bdd_11（P7 exit 0 / P6 exit 2 条件式）在新
    语义下行为不变（P6 pass=2 仍条件式；P7 pass=0 直推）→ 只校准 docstring，不改断言
- [PROD_NOT_TOUCHED]：只读 worktree agate/ + 任务目录；未触碰生产环境/主 checkout/~/.agate

### exit2fix 测试改造 1：test_tag0027_b1_agate_next_cli.py（2026-09-04）
- 文件 → 改动（纯测试，未动实现）：
  1) 头注释契约改 D4-A pass_set 语义（exit ∈ pass_set 直推 / P6 条件式 / 真暂停才落盘）
  2) test_bdd_6_next_exit0_advances_to_next_phase → test_bdd_6_next_exit2_pass_advances_to_next_phase：
     P5 真 exit 2（无 baseline → gate_p5 L1048 return 2 ∈ pass_set{2}）→ 直推 P6 + 不落盘 resolution
     （旧实现 exit 2 一律落盘 = 红灯，CRITICAL-1 盲区补测）
  3) BDD-8 两用例 P5/P3 exit2 落盘锚点 → P4 真暂停锚点（P4-review approved 缺 agent → gate_p4 L913
     return 2 ∉ pass_set{0} 且 ≠ 1 = 真暂停；旧实现对 P4 exit2 落盘恰好正确 → 该对现即绿 = 回归守卫）
  4) test_bdd_13 头注释断言 "exit 2 = 需主 Agent 自判" → R8 新口径（exit 2 + gate_pass_exit 说明）
  5) 新增 test_bdd_11_healthy_exit2_full_advance_no_resolution：P5 exit2 直推 P6 + state_transition
     事件 + 无任何 resolution 落盘（BDD-11 健康任务全程经 CLI 推进证据）
  6) 共享夹具 _write_p5_full_pass_fixture（P2-design.md 无 gate_commands.P5、无 baseline → gate_p5
     恒 exit 2）
- 验证（红灯确认）：3 failed = bdd_13 头注释（缺 gate_pass_exit 说明）+ bdd_6 P5 exit2 直推
  （旧实现停 P5）+ bdd_11 健康推进（停 P5）；10 passed（含 P6/P7/P4 锚点与回归守卫）
- [PROD_NOT_TOUCHED]

### exit2fix 测试改造 2：judge_exit2_review + phases_transfer_fields（2026-09-04）
- test_tag0027_b1_judge_exit2_review.py → Fix C 语义：
  1) 头注释契约改 Fix C（只校验已存在 resolution 文件；账本正常通过 exit:2 无文件不要求）
  2) test_bdd_12_judge_review_gate_run_exit2_without_resolution_fails →
     test_bdd_12_healthy_ledger_no_resolution_file_passes（CRITICAL-2 反向）：账本含 P0/P1/P2/P3/P5
     正常通过 exit:2 + 无 resolution 文件 → 复核 exit 0（不误拦）——旧实现 exit 1 = 红灯
  3) 新增 test_bdd_12_existing_resolution_format_invalid_fails：已存在 resolution 文件格式非法
     （frontmatter 缺 type/必填字段）→ 复核 exit 1——旧实现（账本无 exit:2 → 不查文件）exit 0 = 红灯
  4) test_bdd_12_judge_review_exit2_resolution_present_passes 校准为 Fix C（文件存在性驱动，账本
     可不含 exit:2；P5 → P4 文件）
- test_tag0027_b1_phases_transfer_fields.py → 新增 BDD-26 断言（纯追加，未动既有 5 用例）：
  1) test_bdd_26_all_entries_declare_gate_pass_exit：10 条目全含 gate_pass_exit ∈ {0,2}
  2) test_bdd_26_gate_pass_exit_matches_check_gate_return：数据面真值对 P2 §3.1 实证表（P0-P3/P5/P6/
     P8=2、P4/P7/P6.5=0）+ 真实 gate 抽跑对照（P5 无 baseline exit 2 / P6.5 judge 未启用 exit 0 /
     P7 干净 exit 0）
- 验证（红灯确认）：judge 文件 2 failed（healthy 反向 + format invalid，Fix C 未实现）+ 1 passed
  （正向回归守卫）；phases 文件 2 failed（gate_pass_exit 键缺失）
- [PROD_NOT_TOUCHED]

### exit2fix 实现 1：phases.yaml + schema（2026-09-04）
- agate/rules/phases.yaml：
  * 10 条目（P0-P8 + P6.5）全加 gate_pass_exit：P0-P3/P5/P6/P8=2、P4/P7/P6.5=0（P2 §3.1 实证表）
  * 文件头 schema_version 后补注释块（gate_pass_exit 语义 + exit 2 = 多数 phase 正常通过码 +
    pass_set 三态消费 + P6 条件式说明）
- agate/rules/schema/phases.schema.json：
  * items.properties 声明 gate_pass_exit（type integer，enum [0,2]）
  * items.required 加 gate_pass_exit（全局 required——所有条目必含；规避子集不支持条件 required）
- 验证：check-yaml-schema.py 3 OK（phases ERROR 消除）；JSON 解析 OK
- [PROD_NOT_TOUCHED]

### exit2fix 实现 2：agate-next.py pass_set 判定（2026-09-04）
- 文件 → 改动（main() exit 分发重写 + 头注释/docstring 同步）：
  * main() 读 phases.yaml 当前 phase 的 gate_pass_exit → pass_set = {值}；数据面守卫（缺键/非法
    值 → 暂停转主 Agent 不推进，fail-safe）
  * rc ∈ pass_set → 通过直推：P6 特例（exit 2 ∈ pass_set，provenance exit 0 → A1 裁决 judge
    推进；provenance exit 1 → 验收异常落盘 resolution）；普通 phase 查 next（Pn+1 推进 /
    null 转 READY）——exit 2 正常通过码（P0-P3/P5/P8）直推不落盘（CRITICAL-1 修复）
  * rc == 1 → retreat 委托（不变）
  * rc ∉ pass_set 且 ≠ 1（真暂停/异常）→ 落盘 resolution（BDD-8 触发面收窄；删除旧
    "无条件 rc==2 落盘"逻辑）
  * _write_exit2_resolution / _p6_judge_advance 日志与 docstring 同步（真暂停措辞）
- check-gate.py：仅头注释 exit 2 语义补充（R8：多数 phase 正常通过码 + pass 判定以
  gate_pass_exit 为准；含逐 phase 实证行号）；git diff 确认返回逻辑零改动（+7/-2 纯注释）
- check-judge-verdict.py _check_exit2_resolution → Fix C（CRITICAL-2 修复）：
  * 谓词从"账本凡 exit:2 强制要求 resolution 文件"改为"扫描任务目录**已存在**的
    *-exit2-resolution.md 文件 → 校验 frontmatter(type/phase/task_id/parent/created/agent)
    + 三节完整性"
  * 文件不存在 → 不报错（健康任务账本 exit:2 正常通过 + 无 resolution 文件 → 复核通过）
  * 保留 P6 特例豁免注释 + §3.3 账本可追溯性（文件 phase ∉ 账本 gate_run phase → WARNING
    提示不阻断）
  * 头 docstring + main() 挂载注释同步 Fix C 语义
- 验证：B1 批 4 文件 25 passed（含新语义 6 个 BDD-26 断言 + Fix C 反向 + 健康推进 + 真暂停锚点）
- [PROD_NOT_TOUCHED]

### exit2fix 实现 3 + 全批验证（2026-09-04）
- 改动范围核对：check-gate.py git diff = +7/-2 纯头注释（返回逻辑零改动，BDD-13）；
  check-state-transition.py diff 空
- ruff（~/.venvs/agate-dev）clean（顺带清 3 个既有 unused import：next_cli 的 os/pytest、
  judge_exit2_review 的 pytest——stash 实证 HEAD 即存在，非本批引入）
- 全批验证：
  * B1 批 4 文件 25 passed（新语义全绿）
  * 全 tag0027 批 48 passed（b1+b2+b3a+b3b）
  * 基础回归 295 passed（test_check_gate 180 / test_check_state_transition 44 /
    test_check_judge_verdict 32 / test_check_structure_consistency 17 /
    test_check_yaml_schema 8 / test_ci_gate_backstop 14）
  * check-structure-consistency S0-S6 OK exit 0；check-yaml-schema 3 OK；
    check-protocol-consistency --strict-errors-only 0 ERROR（324 存量 WARNING）
- 未碰 B3a/B3b/B2 approved 文件（WORKFLOW/CHECK 14-15/structure/dispatch 等）；本批改动仅
  phases.yaml + phases.schema.json + agate-next.py + check-judge-verdict.py + check-gate.py（头
  注释）+ 3 个 B1 测试文件 + P4-progress.md
- [PROD_NOT_TOUCHED]

## P4 review 复审开工（review retry1，2026-09-04）
- 独立 review subagent（复审轮）开工：读 dispatch-context（review-retry1）+ review.md 角色 + 首轮 P4-review.md（Fix 基准）+ exit2fix implementer dispatch-context + P4-progress exit2fix 轮记录完成
- 复审范围：CRITICAL-1/2 闭合核对 + 首轮 approved 面保持 + BDD-13 零改动 + 新问题排查

### exit2fix 复审 retry1 信息级修复：REV-2/REV-3（2026-09-04，只改 agate-next.py）
- REV-2（main() 数据面守卫日志 ~349）：缺 gate_pass_exit 分支日志补"数据面异常，非真暂停——
  exit 0 且不落盘 resolution"区分（该分支与真暂停分支行为不同：真暂停落盘 resolution）+
  指引主 Agent 修 phases.yaml 后重跑。只改日志文案与注释。
- REV-3（_write_exit2_resolution）：签名加 gate_rc 参数（实际 check-gate exit code）——正文
  "触发命令: check-gate.py {phase}（exit {gate_rc}）"与"客观证据"节 exit 描述不再写死 exit 2
  （真暂停码实际 ∉ pass_set 且 ≠ 1，如 P4 gate return 2 但 2 ∉ {0}）；已存在提示/落盘日志同步
  带实际 rc。两个调用点（P6 provenance 异常 ~366、真暂停 ~390）传各自 rc。
- 验证：py_compile OK + ruff（~/.venvs/agate-dev）clean + B1 两测试文件 16 passed（全绿）
- [PROD_NOT_TOUCHED]

## P4 终审开工（review-final，2026-09-04）
- 独立 review subagent（终审轮）开工：读 dispatch-context（review-final）+ review.md 角色 + retry1 P4-review.md（REV-1/2/3 描述）完成
- 终审范围：三项修复闭合核对（REV-1 loop-orchestration.md 代码块 pass_set 语义 / REV-2 agate-next.py 数据面守卫日志 / REV-3 _write_exit2_resolution gate_rc）
- [PROD_NOT_TOUCHED]
