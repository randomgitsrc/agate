---
phase: P4
task_id: TAG0020-independent-judge
type: implementation
parent: P2-design.md
trace_id: TAG0020-P4-20260822
status: draft
created: 2026-08-22
agent: implementer
---

# P4 实现汇总 — 独立 Judge 机制（RM-AG0032）：P6.5 挂载与三层防造假

> 本文件是 TAG0020 P4 全批（scripts 批 + docs 批 + CHECK 9 补丁）的汇总产出。分批进度与逐文件记录见 `P4-progress.md`（同目录，权威明细），本文件按 P4 卡产出规格做聚合声明。

## implementation_dir

- `implementation_dir: agate/scripts`（core 脚本；协议文档改动在 `agate/` 各文件，详见实现摘要）

## 新增文件核对表

> 本项目未采用骨架机制（无 `P2-skeleton.md`）且无 CODE-MAP（无 `{AGATE_WORKSPACE}/agents/CODE-MAP.md`），按 P4 卡规则逐新增文件标注豁免。

| 新增文件路径 | 骨架归属 | CODE-MAP 处理 |
|------------|---------|--------------|
| agate/scripts/check-judge-verdict.py | `[SKELETON_DEVIATION: 无骨架机制]` | `[CODE_MAP_EXEMPT: 无 CODE-MAP 机制]` |
| agate/scripts/check-events.py | `[SKELETON_DEVIATION: 无骨架机制]` | `[CODE_MAP_EXEMPT: 无 CODE-MAP 机制]` |
| agate/assets/review-roles/judge.md | `[SKELETON_DEVIATION: 无骨架机制]` | `[CODE_MAP_EXEMPT: 无 CODE-MAP 机制]` |

## 实现摘要（三批）

### ① scripts 批（P2 dispatch_plan serial 第①层，5 文件）

- **agate_common.py**（修改）：事件账本三件套——模块级 `GENESIS_HASH`（sha256(b"")）+ `append_event(task_dir, event)`（append-only 哈希链写入：自动补 ts UTC 微秒 + prev_hash 续接尾行原始文本 + ts 单调兜底 + IOError 仅 WARNING 不抛）+ `read_judge_verdict(task_dir)`（frontmatter 解析 → dict / 缺失 → None）。MAX_RETRY_MAP 未动。
- **check-judge-verdict.py**（新增）：P6.5 verdict 门槛判定九步链——① verdict 存在且非空 ② dispatch-context 存在且非空 ③ Header 字段（status 三值/整数计数/verdict_evidence）④ BDD 对照（`^#### BDD-[0-9]` 计数 + 结论编号集相等 + 条目数==criteria_total，零挑验）⑤ passed 三数全等 + partial+passed 拦截 ⑥ 证据交叉核对（存在/非空/md5 去重/引用对称，gate 于 P6-evidence/ 目录存在前提）⑦ 信息隔离白名单（两节黑名单串大小写不敏感 + 白名单外路径 + 全文行首预判，AGATE_CARD/frontmatter 双排除）⑧ 预算交叉（账本 budget_exhausted ⇒ verdict 须 needs-revision+partial）⑨ 通过后 append_event 记 judge_verdict。
- **check-events.py**（新增）：事件账本审计——缺失/空合法态；逐行 JSON 可解析；首行 prev_hash==GENESIS_HASH；逐行哈希链（改写检测）；ts 单调不减；judge_verdict 事件计数 ≤2（轮次预算兜底）；未知 event 类型不拦截。
- **check-gate.py**（修改）：`gate_p65`（judge 未启用 → 早退 0 历史兼容；启用缺 verdict → exit 1；否则依次调双脚本任一 exit 1 → exit 1）+ handlers 注册 `"P6.5"` + `_load_state_yaml`/`_run_gate_script` helpers。gate_p6 未改（BDD-10）。
- **pre-commit-gate.py**（修改）：2i.1 P6.5 注入（judge.enabled && verdict 存在 → 双脚本任一 exit 1 → 阻断 commit，commit-time 硬边界与 commit 位置解耦）+ write_gate_result 后记 `gate_run` 事件 + phase 变更时记 `state_transition` 事件 + `_judge_enabled` + `_NON_MD_YAML_RE` 纳入 `gate-events.jsonl`（元数据豁免，修复 retreat 回归）。

### ② docs 批（serial 第②层，judge.md 先行 + 8 处文档 + ci-gate-backstop 兜底 + AGENTS.md 登记）

- **judge.md**（新增，先行）：角色定义——fresh context 逐条重验所有 BDD（零挑验）/ 信息隔离白名单与黑名单（与 check-judge-verdict 实现同源）/ 三档预算（轮次 ≤2 / token 100k / 30min）与诚实降级 partial / 机械核对红线（exit code 才是门槛，BDD-9）/ status 三值映射 / double-judge 可选。
- **state-machine.md**：P6→P6.5→P7 转移 + needs-revision/rejected 弹回 P6 重验（judge.rounds + 账本事件计数 ≤2 兜底）；状态集合注记"P6.5 非独立 phase 值"；重试上限 prose ≤2 轮（**未加表行/未用 retries.P6.5**，CHECK 12 零漂移）；.state.yaml judge 字段块说明。
- **WORKFLOW.md**：阶段总览 P6.5 行 + 角色清单树登记 judge + P6.5 judge 复核（强制）说明段（P6 行 self-authored 缓解标注同步增补）。
- **dispatch-protocol.md**：新增「Judge 信息隔离（P6.5）」节——白名单/黑名单路径引用集、AGATE_CARD + frontmatter 双排除、agate-extract-context.py 在 P6.5 禁用或净化（上游关联注入面防泄漏）、P6.5 派发流程 6 步、预算/账本 budget_exhausted 交叉文档化。
- **phase-cards/P6-acceptance.md**：派发步骤 10（P6.5 judge 复核强制）+ gate 规则追加 `check-gate.py P6.5` + 推进条件 checkbox。
- **assets/templates/dispatch-prompt.md**：Judge 派发追加节（信息隔离清单/三档预算/只信证据与 git log 认知约束/verdict 产出格式）。
- **role-system.md**：评审名册 judge 行 + status 三值映射复用说明 + 明示 judge 不进 C8 表。
- **LIMITATIONS.md**：局限 3 补「P6.5 独立 Judge 缓解链」（明示"缓解而非根治"）。
- **ci-gate-backstop.py**（修改，SCOPE_GAP 补齐）：provenance 兜底后新增 judge/events 兜底（条件与 pre-commit 2i.1 一致；--no-verify 绕过时 CI 层补跑）。
- **AGENTS.md**（修改）：协议本体入口角色清单登记 judge.md（P2 §1.1 声明面 + P3 测试驱动）。

### ③ 补丁（主 Agent 追加任务）

- **check-protocol-consistency.py**：SCRIPT_ALIGNMENT_ANCHORS 增补 2 条锚点（check-judge-verdict：keywords criteria_total/judge；check-events：keywords prev_hash/GENESIS；均含 callers 声明）——消除 CHECK9-coverage 警告。
- **agate-summary.py**：_DRIFT_SCRIPTS 增补两新脚本（copy-drift 检测覆盖）。

## 测试状态（自查 ≠ P5 gate；仅实现批自跑，P5 由主 Agent 派 verifier 执行）

| 项 | 结果 |
|----|------|
| test_check_judge_verdict (29) + test_check_events (12) | **41 passed** |
| test_agate_common（增补 5）+ test_check_gate（增补 6，含既有回归）| **182 passed** |
| test_pre_commit_hook（integration 真实 hook）| **55 passed**（含 1 处回归修复：gate-events.jsonl 纳入元数据豁免）|
| test_ci_gate_backstop | passed |
| 邻近回归切片（P6 审计/state/2p/sanity）| **143 passed** |
| test_docs_assertions（TAG0020 增补）+ test_ci_gate_backstop + test_review_role_docs | **39 passed** |
| 协议文档回归切片（mechanism_anchors/self_gate_naming/p2p4_boundary/dedup/consistency/retrospective/dispatch_orchestration）| **107 passed** |
| 核心汇总（41+182+39+review_role_docs）| **262 passed** |
| test_protocol_alignment_review（check9）+ test_check_protocol_consistency + test_consistency | **46 passed** |
| check-protocol-consistency.py --strict-errors-only（worktree 自身）| **0 ERROR / 318 WARNING**（不阻断；原 2 条 CHECK9-coverage 已消除）|
| py_compile（8 个改动/新增 .py）| 全净（-W error::SyntaxWarning 零警告）|

> 备注：docs 断言 test_docs_assertions.py 中 P6.5 相关 9 条断言全绿；脚本批回归修复 1 处（pre-commit retreat）；测试代码零改动（测试是验收口径，未迁就实现）。

## SCOPE_GAP 记录

- **已闭环**：`[SCOPE_GAP: P2-design §1.1/§4 声明 ci-gate-backstop.py judge/events 兜底，scripts 批 prompt 未列 → docs 批主 Agent 确认后补齐（本轮已实现，见实现摘要 ②）]`
- 实现中未发现新的 P2 未预见必须项（无新增 SCOPE+）。

## 产物文件总清单（17 文件）

- scripts 批（5）：修改 agate/scripts/agate_common.py、check-gate.py、pre-commit-gate.py；新增 agate/scripts/check-judge-verdict.py、check-events.py
- docs 批（10）：新增 agate/assets/review-roles/judge.md；修改 agate/state-machine.md、WORKFLOW.md、dispatch-protocol.md、phase-cards/P6-acceptance.md、assets/templates/dispatch-prompt.md、role-system.md、LIMITATIONS.md、AGENTS.md、agate/scripts/ci-gate-backstop.py
- 补丁（2）：修改 agate/scripts/check-protocol-consistency.py、agate-summary.py
- 明细：agate-workspace/tasks/TAG0020-independent-judge/P4-progress.md（逐文件分批复盘）