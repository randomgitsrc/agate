---
phase: P4
task_id: TAG0023-mechanism-checks
type: review
parent: P4-implementation.md
trace_id: TAG0023-P4-review-20260825-r2
status: approved
created: 2026-08-25
agent: review
---

> [PROD_NOT_TOUCHED] 只读评审（复评第2轮）：读了 P4-dispatch-context-review-retry1.md、
> P4-review.md（第1轮全文）、`git diff HEAD -- check-state-transition.py test_check_state_transition.py`
> 全量、P1-requirements.md BDD-2 原文、P2-design.md BDD-2 设计定案原文、review.md 角色定义、
> agate/rules/state-transitions.md 回退规则、test_pre_commit_hook.py 真实集成回退用例；独立
> 跑了 `pytest agate/tests/unit/test_check_state_transition.py agate/tests/ -q` 与
> `ruff check` 两个改动文件，未做任何写操作。

# P4 实现复评（第2轮）— TAG0023 机制校验补强批，聚焦第1轮4条CRITICAL修复核实

结论：**approved**。4 条 CRITICAL 均已正确、完整修复，未发现遗漏的连带影响，也未发现方案A
引入的新副作用（真实集成测试实证：标准回退工具路径下首次回退不会被误伤）。

## 逐条核实结论

**CRITICAL 1（BDD-2 old_retries_len>0 守卫漏判首次违规）— 已修复，方案A，核实通过**
- 去掉守卫后的实现（`old_num>new_num` 且 `new_retries_len<=old_retries_len` → exit 1）与
  `P2-design.md` L92-93 BDD-2 设计定案原文逐字比对一致（"old_num>new_num（含 diff==1）且
  暂存版本长度未大于 HEAD 版本长度→拦截"，原文从未提过"该阶段此前必须已有记录"这一前提）。
  即第1轮的守卫本身是对 P2-design 的未声明偏离，本次修复是回归设计原文，不是新增行为，字面
  满足 P1-requirements.md BDD-2 Given 子句。
- 新增回归用例 `test_bdd_2_first_time_retreat_both_sides_empty_retries_exit_1`：HEAD/暂存
  两侧 `retries: {}`，P5→P4 单步回退，断言 exit 1 + `retries[P4]` 出现在输出——精确复现
  RM-AG0042 立项证据本身（复盘四任务 retries 全为 {} 的首次单步回退），非浅层合成用例。
- **连带修复范围**：逐一核对 `test_check_state_transition.py` 内全部 diff==1 回退用例，
  `test_st_archive_1/2/3/6` 已补非空 retries fixture；`test_st_archive_5`（P1→P0）因
  `new_num>0` 守卫天然排除不受影响；其余回退用例均 diff>=2，被检查1提前 exit，不会走到检查3。
  全仓搜索 `check-state-transition.py` 调用点：单测直调（已核）+
  `pre-commit-gate.py:248`（`phase_changed` 时调用真实 hook 链路，被
  `test_pre_commit_hook.py` 覆盖）。独立全量重跑 `pytest ... -q` → 1238 passed/2 skipped，
  与主 Agent 声称一致，无回归，未发现遗漏的既有测试。
- **方案A新副作用核实**（dispatch-context 重点关切）：读 `agate/rules/state-transitions.md`
  L66/L69 确认协议本身规定"任何单步回退（Pn→Pn-1）都必须同步写 retries"，不存在"合法首次
  回退可以不写 retries"的场景——review 提出的"P8→P7 合法首次回退被误伤"假设在协议层面不成立，
  这本来就该被要求写 retries，不写就该被拦截。更进一步用真实集成测试实证而非纯推理：
  `test_pre_commit_hook.py::test_retreat_1_real_hook_each_step` 用生产回退工具
  `agate-retreat-to.py`（非手改 phase）对初始 `retries: {}` 的任务做 P6→P5→P4 两步真实回退
  （两步都是"该阶段此前从未记录过"的首次回退），断言两次 commit 均成功落地——证明标准工具
  路径下 `write_retreat` 会自动 append retries，首次回退不会被新逻辑误伤。会被拦截的只有
  "绕过标准工具手改 `.state.yaml` phase 字段"这一种场景，这正是 RM-AG0042 要修的问题本身，
  不是对合法工作流的误伤。结论：方案A的"更严格"符合协议本意，未发现新副作用。

**CRITICAL 2（`_load_current_state_yaml` 非法 UTF-8 崩溃）— 已修复，核实通过**
- `open(state_file, encoding="utf-8", errors="replace")`：`errors="replace"` 使
  `f.read()` 遇到非法字节直接替换为 U+FFFD 而不抛 `UnicodeDecodeError`，比 review 建议的
  "扩 except 捕获"更彻底（从源头避免异常，不是事后兜底），未额外扩 except 是合理的，因为
  异常已经不会发生。
- 新增单测 `test_load_current_state_yaml_invalid_utf8_no_crash` 绕开子进程屏蔽问题
  （docstring 已解释：端到端 CLI 路径下 `agate-state-get.py` 子进程会先于本函数在同一非法
  字节上崩溃并被吞掉，掩盖本函数自身仍会崩溃的事实），改为用 `importlib` 直接加载模块调用
  内部函数，写入含 `\xff\xfe` 非法字节的真实文件，断言返回 dict 且 `task_id` 字段仍可读——
  真实复现且规避了测试盲区，非浅层用例。

**CRITICAL 3（`_scan_bdd1_review_retry_phase` 只返回首个命中阶段）— 已修复，核实通过**
- 改为收集全部命中到 `set` 返回，`main()` 用 `for bdd1_phase in sorted(...)` 逐个检查，
  写法对齐同批已有的 `_scan_bdd3_keyword_phases` 的 set 收集模式，一致性良好。
- 新增回归用例 `test_bdd_1_multiple_phase_hits_all_warned` 精确复刻第1轮的复现场景（本任务
  自身 task_dir 结构：`P1-dispatch-context-requirements-review-retry1.md` +
  `P2-dispatch-context-plan-eng-review-retry1.md` 同时存在），断言两个阶段的 WARNING 都
  各自触发——非浅层用例。

**CRITICAL 4（`_scan_bdd3_keyword_phases` 精确匹配漏扫分批进度文件）— 已修复，核实通过**
- `rest.startswith("progress.md")` → `rest.startswith("progress")`，机械性放宽匹配。
- 新增回归用例 `test_bdd_3_progress_batch_named_file_detected` 用
  `P4-progress-batchA.md`（与本任务自己产出的 P4-progress-batchA/B/C/D.md 完全同构命名）
  验证含关键词时能被扫到——非浅层用例。注：放宽后理论上会连带匹配 `progress` 开头的其他
  非分批文件名（如 `progressive-notes.md`），但该分支只影响 BDD-3 的 WARNING（非阻断）且
  仍需关键词命中才触发，不构成新的 CRITICAL 风险，仅记录不阻塞本轮。

## 测试与静态检查复核

- 独立重跑 `python3 -m pytest agate/tests/unit/test_check_state_transition.py agate/tests/ -q`
  → **1238 passed, 2 skipped**，较修复前 1234 净增 4 条新回归用例全部通过，无回归，与主 Agent
  声称一致（独立复核，非转述信任）。
- `ruff check agate/scripts/check-state-transition.py agate/tests/unit/test_check_state_transition.py`
  → All checks passed。

## batch B/C/D 无需重新评审的依据

- `git diff HEAD` 确认本轮改动仅限 `agate/scripts/check-state-transition.py` +
  `agate/tests/unit/test_check_state_transition.py`（batch A），与 dispatch-context 声明
  一致；未见 `check-gate.py`（batch B）、`check-debt.py`/`.github/workflows/protocol-tests.yml`
  （batch C）、`dispatch-prompt.md`/`agate-frontmatter-check.py`（batch D）在本次 diff 中
  出现任何改动。
- 第1轮 review 已对 batch B/C/D 做过 Pass 1/Pass 2 评审，无 CRITICAL（仅 batch B 有两条
  INFORMATIONAL，非阻断项，本轮未改动，不需重评）。batch A 与 batch B/C/D 文件集合两两不
  相交（第1轮已核实），本轮 batch A 的修改不会波及其余三批。

## 结论

status: **approved**。4 条 CRITICAL 修复方法正确、连带修复范围完整、新增回归用例真实复现
原始场景非走过场，方案A的加严行为经真实集成测试证实不会误伤合法工作流（标准回退工具路径下
首次回退自动写 retries）。batch B/C/D 未受影响，无需重新评审。
