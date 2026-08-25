# P4-progress-review-retry1（复评第2轮，review subagent 自记）

1. 读 P4-dispatch-context-review-retry1.md 全文 — done。明确 4 条 CRITICAL 修复摘要 + 本轮任务5点。
2. 读 P4-review.md（第1轮全文）— done。逐条记下原 CRITICAL 1~4 的位置、根因、Fix 选项（含 A/B/C 三选项供 CRITICAL 1）。
3. `git diff HEAD -- check-state-transition.py test_check_state_transition.py` 全量读取 — done。
   - CRITICAL 2 fix: `open(..., errors="replace")`，未额外扩 except（因 errors=replace 后 read() 不再抛 UnicodeDecodeError，无需扩 except）。
   - CRITICAL 3 fix: `_scan_bdd1_review_retry_phase` 返回 set，main() 用 `for bdd1_phase in sorted(...)` 逐个检查。
   - CRITICAL 4 fix: `rest.startswith("progress")`（原 "progress.md"）。
   - CRITICAL 1 fix: 采用方案A，去掉 `old_retries_len>0` 守卫；`test_st_archive_1/2/3/6` 四个既有回归用例补了非空 retries fixture。
4. 读 review.md 角色定义 — done。Pass1 CRITICAL 关注点：竞态/校验/状态消费完整性；输出格式；修复只提方案不动代码（本轮是核实，非修复）。
5. 逐条核实：
   - CRITICAL 2：`errors="replace"` 是正确且完备的修复（避免了 UnicodeDecodeError 而非只是catch它），比 review 建议的"扩 except"更彻底。新增单测 `test_load_current_state_yaml_invalid_utf8_no_crash` 绕开子进程屏蔽问题、直接测内部函数，用真实非法字节验证 dict 仍可用——判定：真实、非浅层。
   - CRITICAL 3：核对 `_scan_bdd1_review_retry_phase` 现在完整收集 set，写法对齐已有 `_scan_bdd3_keyword_phases` 模式。新增用例 `test_bdd_1_multiple_phase_hits_all_warned` 直接复刻 review 原始复现场景（本任务自身 task_dir 结构：P1+P2 两份 review-retry 文件同时命中），断言两个 WARNING 都触发——判定：真实复现，非浅层。
   - CRITICAL 4：`rest.startswith("progress")` 替代精确匹配。新增用例用 `P4-progress-batchA.md` 命名（与本任务自己产出的 P4-progress-batchA/B/C/D.md 完全同构），断言 WARNING 命中——判定：真实复现，非浅层。
   - CRITICAL 1：去掉守卫后与 P2-design.md L92-93 原文（"old_num>new_num（含 diff==1）且暂存版本长度未大于 HEAD 版本长度→拦截"，无 old_retries_len>0 前提）逐字比对，确认此前的守卫本身就是对 P2-design 的未声明偏离，本次修复是回归设计原文而非新增行为。新增用例 `test_bdd_2_first_time_retreat_both_sides_empty_retries_exit_1` 精确复现 RM-AG0042 立项证据本身（两侧 retries 皆空的首次单步回退），断言 exit 1——判定：真实复现，非浅层，且直接命中任务最初动机。
6. 连带修复范围核实（CRITICAL 1 的隐含假设是否还有遗漏）：
   - grep `test_check_state_transition.py` 全部 diff==1 回退用例：test_st_archive_1/2/3/6（已修复，补了 fixture）；test_st_archive_5（P1→P0，new_num=0 被 `new_num>0` 守卫排除，不受影响）；其余 test_st_4/5/13/14/ws_1~4 均 diff>=2，被检查1提前 exit，不会走到检查3。
   - grep 全仓 `check-state-transition` 调用点：仅 `test_check_state_transition.py`、`test_dispatch_context_warning.py`（新建 task 无 HEAD，old_num=0 不受影响）直接调用；`pre-commit-gate.py:248` 在 phase_changed 时调用（`test_pre_commit_hook.py` 走真实 hook 链路）。
   - 读 `test_pre_commit_hook.py::test_retreat_1_real_hook_each_step`：用真实 `agate-retreat-to.py`（生产回退工具，非手改 phase）跑 P6→P5→P4 两步回退，初始 retries 均为空（`_write_state_yaml` 默认 `retries: {}`），断言 returncode==0 且两步 commit 均落地——**这是"首次回退+标准工具路径"的真实集成场景，验证了标准路径下 write_retreat 会自动 append retries，不会被新逻辑误伤**。
   - 独立跑全量：`python3 -m pytest agate/tests/unit/test_check_state_transition.py agate/tests/ -q` → 1238 passed, 2 skipped，与主 Agent 声称一致，无回归。
   - `ruff check` 两个改动文件均 All checks passed。
   - 结论：连带修复范围完整，未发现遗漏。
7. 方案A新副作用核实（dispatch-context 第4点）：
   - 状态机规则 `agate/rules/state-transitions.md:66/69` 明文规定"单步回退（Pn→Pn-1）✅允许，retry+1"且"必须同步写 retries"——协议上不存在"合法单步回退可以不写 retries"的场景，即"该阶段第一次经历单步回退但不算重试"这一假设本身不成立：协议要求任何单步回退（无论是否第一次）都必须写 retries。
   - `agate-retreat-state.py`/`agate-retreat-to.py`（标准回退工具）已经会自动 append retries（P2-design.md L86 已读代码确认），配合上一步的真实集成测试（test_retreat_1）实证：只要走标准工具，首次回退也不会被新逻辑误伤。会被拦截的只有"绕过标准工具手改 phase 字段"的场景——这正是 RM-AG0042 要修的问题本身，不是误伤。
   - 结论：方案A的"更严格"是符合协议本意的加严，未发现对合法工作流的误伤。
8. 写产出文件 P4-review.md（status: approved）。
