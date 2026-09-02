
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
