---
phase: P6
task_id: TAG0020
type: acceptance
parent: P5-verification.md
trace_id: TAG0020-P6-20260822
status: draft
created: 2026-08-22
agent: verifier
# ── v2.0 机器汇总 ──
pass: 10
fail: 0
ui_affected: false
---

# P6 验收报告 — 独立 Judge 机制（RM-AG0032，TAG0020）

[PROD_NOT_TOUCHED]
[NO_NEED_CONFIRM]

## 验收范围与方法

- **验收对象**：TAG0020 P6.5 独立 Judge 机制实施产出（worktree `agate/`）：`scripts/check-judge-verdict.py` / `scripts/check-events.py` / `scripts/agate_common.py`（append_event/read_judge_verdict/GENESIS_HASH）/ `scripts/check-gate.py`（gate_p65 分支）+ 协议文档（judge.md / state-machine.md / WORKFLOW.md / dispatch-protocol.md 信息隔离节 / phase-cards/P6 / dispatch-prompt.md Judge 追加节 / role-system.md 登记）。
- **验收口径**：P1-requirements.md 共 **10 条 BDD**（`#### BDD-1` ~ `#### BDD-10`，grep 实测计数 = 10）；`ui_affected: false`（P1 domains: backend，capability_requirements: []，无 UI）。非 refactor 任务，走标准功能验收口径。
- **方法**：每条 BDD 实跑获得客观结果——① 分组单元测试实跑（pytest，`--basetemp=agate-workspace/.pytest-tmp`，解释器 /usr/bin/python3）② `check-gate.py P6.5` / `check-judge-verdict.py` / `check-events.py` 功能演示（scratch 任务目录）③ 文档断言（grep 协议文档 P6.5/judge 条文）④ BDD-10 引用 P5 全量回归复用（`.state.yaml` `p5_pass_commit: ae8fe1774d44e2c50740ecad99dc62c109658637`，P5→P6 间无非产出文件改动，审计 7 判定 reuse_allowed）。
- **全套验证输出汇总**：`P6-evidence/test-output.log`（尾行 `EXIT_CODE: 0`）。

## 逐条验收结果

- PASS BDD-1: 新任务 P6 验收后必须经 P6.5 judge 门槛才能进入 P7 —— `check-gate.py` 新增 `gate_p65` 子阶段并注册（`"P6.5": gate_p65`，L1155）；功能演示：`.state.yaml` 含 `judge.enabled: true` + 缺 `P6.5-judge-verdict.md` → `GATE P6.5: 缺 P6.5-judge-verdict.md（judge 未产出），P6→P7 阻断` exit 1；完整合规 verdict + dispatch-context + 证据 → `check-judge-verdict` exit 0 + `check-events` exit 0 → `gate_p65` exit 0 放行；单元 15 用例全过（verdict 缺失/空 → exit 1 等，check-judge-verdict 与 check-gate 双层 fail-closed）(bdd-1-unit.log, bdd-1-blocked.result, bdd-1-allowed.log)

- PASS BDD-2: 历史任务（无 judge 字段）跳过 P6.5，存量不挂 —— `gate_p65` 对 `.state.yaml` 无 `judge.enabled: true` 早退 0（不需 verdict / gate-events）；功能演示：无 judge 字段任务 → `GATE P6.5: judge 机制未启用（历史任务），跳过` exit 0；单元 5 用例全过（无 judge 字段 / `judge.enabled: false` → exit 0，不要求任何 judge 产物）(bdd-2-unit.log, bdd-2-legacy.log)

- PASS BDD-3: judge 以 fresh context 逐条重验所有 BDD（含已 PASS 项，零挑验）—— `check-judge-verdict.py` 用 P1 `^#### BDD-([0-9]+)` 标题数（审计 3 同款口径）比对 `criteria_total`，且结论编号集 == P1 BDD 全集、条目数 == criteria_total（零挑验强制）；单元 4 用例全过（criteria_total 不符 / 跳过 BDD-2 / 多余 BDD-9 编号 → exit 1；3 条全覆盖 → exit 0）；本任务 P1 实测 10 条标题（见上文验收口径）(bdd-3-unit.log, bdd-1-allowed.log)

- PASS BDD-4: 信息隔离白名单——黑名单路径引用集禁注入、白名单外路径禁引、行首验收预判禁 —— `check-judge-verdict.py` 对 `P6.5-dispatch-context-judge.md` 的『输入文件』『上游关联』两节做黑名单串扫描（P6-acceptance.md / P4·P5·P6-dispatch-context-*.md / P4-implementation.md / P4-review.md / P5-test-results/，大小写不敏感）+ 白名单外任务路径扫描（白名单 = P1-requirements.md / P2-design.md / P6-evidence/ / .state.yaml / gate-events.jsonl / P6.5-judge-verdict.md）+ 全文行首 `- PASS|FAIL` 预判扫描（排除 AGATE_CARD 注入块与 frontmatter）；单元 9 用例全过（输入/上游节黑名单命中、大小写变体、白名单外 P3-test-cases.md、行首预判 → exit 1；AGATE_CARD 块 / frontmatter 内 PASS 行不误报、绝对路径白名单归一 → exit 0）(bdd-4-unit.log)

- PASS BDD-5: verdict 落盘机器可读且字段完备（passed 三数全等）—— `read_judge_verdict`（agate_common.py）解析 frontmatter；`check-judge-verdict.py` 校验 status ∈ {passed, rejected, needs-revision}、criteria_total / criteria_passed 为整数、verdict_evidence 非空清单、status=passed 时 criteria_passed == criteria_total == P1 BDD 数；单元 6 用例全过（status 非法 / 字段缺失 / 非整数 / 三数不等 → exit 1）(bdd-5-unit.log)

- PASS BDD-6: 证据交叉核对——每条结论的证据引用真实存在且不重复充数 —— `check-judge-verdict.py` `_check_evidence`：verdict_evidence 每条引用须存在于 P6-evidence/ 且非空、相互 md5 互异、结论引用 ⊆ 清单且每条被引用（对称）；缺失引用 / 空文件 / md5 重复 / 引用不对称 → exit 1；单元 6 用例全过（ghost 引用、空文件、md5 重复充数、结论引用不在清单、清单未被引用 → exit 1；描述中任意括号不误取引用 → exit 0）(bdd-6-unit.log)

- PASS BDD-7: 事件账本 append-only + 行间哈希链 —— `append_event`（agate_common.py）为账本唯一写路径（自动补 ts + prev_hash，首行 = GENESIS_HASH = sha256(b"")）；`check-events.py` 六步审计：缺失/空账本合法态、逐行 JSON 可解析、首行 prev_hash==GENESIS、逐行 prev_hash==sha256(上一行原文)、ts 单调不减、judge_verdict 轮次计数；功能演示：3 行合法链 → `账本审计通过（3 行，哈希链完整，ts 单调）` exit 0；改写中间行 exit:2→99 → `第 3 行 prev_hash 与上一行原始文本不匹配（历史行被改写检测）` exit 1；单元 10 用例全过（缺失/空账本 exit 0、篡改链 / 首行非 GENESIS / ts 逆序 / 坏 JSON → exit 1、未知事件类型向后兼容 exit 0）(bdd-7-unit.log, bdd-7-valid-chain.log, bdd-7-tampered-chain.result)

- PASS BDD-8: 三档预算与诚实降级——超限不静默放行 —— 预算交叉：账本存在 `reason: budget_exhausted` 的 judge_verdict 事件 ⇒ verdict 必须 `partial: true` 且 `status: needs-revision`（否则 exit 1）；`partial: true + status: passed` → exit 1；judge 轮次机械兜底：`check-events.py` 按 verdict_hash 去重后 judge_verdict 事件计数 ≤ 2（同 verdict 多 gate 执行点重跑不增轮，真实复核才 +1，超 2 轮 → exit 1 人工接管）；单元 8 用例全过（partial+passed exit 1、budget_exhausted 非 needs-revision exit 1、合规 needs-revision+partial exit 0、2 轮边界 exit 0 / 3 轮 exit 1、同 hash 去重 exit 0、3 个不同 hash → exit 1）(bdd-8-unit.log)

- PASS BDD-9: 不引入"LLM 当 gate 主判据"—— exit code 才是门槛 —— `gate_p65` 依次调 `check-judge-verdict.py` + `check-events.py`，任一 exit 1 → P6.5 gate exit 1、P6→P7 转移阻断；LLM verdict（status: passed）不单独构成放行依据；功能演示：status=passed 但证据引用 ghost.json → `GATE JUDGE-VERDICT: verdict_evidence 引用不存在` exit 1；单元 1 用例（passed 但证据缺失 → 机械核对 exit 1）(bdd-9-unit.log, bdd-9-llm-not-gate.result)

- PASS BDD-10: 协议一致性与回归——P6.5 挂载不破坏现有体系 —— worktree 自身 `check-protocol-consistency.py --strict-errors-only` = **0 ERROR / 318 WARNING / exit 0**（WARNING 非阻断，与 P5 基线一致）；`count-tests.sh` = 1168 用例 ≥ 749 基线、无漂移 / exit 0；重点回归（新增 test_check_judge_verdict + test_check_events + test_check_gate 全量 + test_agate_common + test_check_p6_provenance + test_docs_assertions）= **292 passed / exit 0**；全量 pytest 复用 P5 通过证据（`P5-test-results/unit.md`：1164 passed / 2 预存环境失败 / 0 本次引入，known-failures.md 条目 1/2 登记）(bdd-10-consistency.log, bdd-10-count-tests.log, bdd-10-pytest-focus.log, test-output.log)

**Summary**: 10/10 PASS, 0 FAIL

## 说明与边界

- **本任务不派发 judge**：TAG0020 自身 `.state.yaml` 无 judge 字段（属"存量开放"），P6.5 对无 judge 字段任务跳过（BDD-2 语义），故本 P6 验收走标准 verifier 自评流程；judge 机制本身的正确性由本报告 BDD-1~BDD-9 的机械校验实跑 + 全量单元测试覆盖。
- **负向证据文件命名**：三份负向功能演示（缺 verdict 阻断 / 账本篡改检测 / LLM 自述不放行）exit 1 属预期行为，以 `.result` 后缀命名避免与审计 5 的"日志 EXIT_CODE"约定冲突（该审计只扫描 `*.log`）。
- **P5 全量 2 项 failed 均为预存环境失败**（basetemp 位于 worktree git 仓库内导致：non-git 上下文前提失效 / 一致性扫描面误收 pytest 临时 fixture），非本次改动引入（P5 unit.md + known-failures.md 已登记）。