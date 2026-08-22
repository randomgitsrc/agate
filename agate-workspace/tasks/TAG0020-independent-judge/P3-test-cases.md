---
phase: P3
task_id: TAG0020-independent-judge
type: test-cases
parent: P2-design.md
trace_id: TAG0020-P3-20260822
status: draft
created: 2026-08-22
agent: test-designer
---

# P3 测试用例映射 — 独立 Judge 机制（TAG0020）

> 分工：本文件只产出 BDD → 测试文件映射（10 条 1:1 全覆盖）；测试代码由后续 subagent 依据本映射写入，本文件不含代码级细节。
> `test_code_dir: agate/tests/unit/`（worktree 相对路径；绝对路径 = `.worktrees/agate-TAG0020/agate/tests/unit/`；P3 红灯命令参照 P2-design §5 gate_commands.P3，运行两个新文件）。

## 1. 测试资产分组概览（P2-design §3.8 为准）

| 测试文件 | 性质 | 覆盖 BDD |
|---|---|---|
| `test_check_judge_verdict.py` | 新增 | BDD-3/4/5/6/8/9 |
| `test_check_events.py` | 新增 | BDD-7/8 |
| `test_check_gate.py` | 增补 | BDD-1/2/9/10 |
| `test_agate_common.py` | 增补 | BDD-5（读取侧）/ BD-7（写侧，append_event） |
| `test_docs_assertions.py` | 新增（文档断言，亦可并入上述各文件） | BDD-4/8/10 |

## 2. BDD → 测试文件映射（10 条 1:1，全覆盖）

| BDD 编号 | 测试文件 | 用例意图（≤2 行） |
|---|---|---|
| BDD-1 | `test_check_gate.py` + `test_check_judge_verdict.py` | gate_p65：judge 启用（`judge.enabled: true`）后 verdict 缺失 → exit 1（P6→P7 阻断）；verdict + 双脚本通过 → exit 0 放行。verdict 存在且非空的 fail-closed 由 check-judge-verdict 承载 |
| BDD-2 | `test_check_gate.py` | gate_p65：无 judge 字段（历史任务）→ 早退 exit 0，全程不要求 `P6.5-judge-verdict.md` / `gate-events.jsonl`，check-gate 不拦截 |
| BDD-3 | `test_check_judge_verdict.py` | criteria_total == P1 `#### BDD-NN:` 标题数（审计 3 计数口径）；结论编号集与 P1 全集相等（含 P6 已 PASS 项零挑验），条目数 == criteria_total；任一不符 → exit 1 |
| BDD-4 | `test_check_judge_verdict.py` + `test_docs_assertions.py` | 白名单机械扫描：两节黑名单串 / 白名单外路径 / 行首 `- PASS|FAIL` 预判 → exit 1；AGATE_CARD + frontmatter 双排除不误报；`dispatch-prompt.md` Judge 信息隔离节条文可 grep 断言 |
| BDD-5 | `test_check_judge_verdict.py` + `test_agate_common.py` | Header 字段完备与取值合法（status 三值 / 整数计数 / `verdict_evidence` 存在）；passed ⇒ `criteria_total == criteria_passed == P1 BDD 数`；`read_judge_verdict` 解析正确、文件缺失返回 None |
| BDD-6 | `test_check_judge_verdict.py` | 证据交叉核对：引用存在非空 / md5 互异去重 / 引用 ⊆ `verdict_evidence` 且对称；缺失引用、空文件、md5 重复充数 → exit 1 |
| BDD-7 | `test_check_events.py` + `test_agate_common.py` | 账本审计：首行 `prev_hash == GENESIS_HASH`、逐行哈希链完整（改写历史行 → 断裂 exit 1）、ts 单调不减、仅行尾追加；空/缺失账本合法；坏 JSON exit 1。写侧：`append_event` 首行 GENESIS、ts 单调兜底、失败仅 WARNING |
| BDD-8 | `test_check_judge_verdict.py` + `test_check_events.py` + `test_docs_assertions.py` | partial+passed → exit 1；账本 `reason: budget_exhausted` 但 verdict 非 needs-revision+partial → exit 1；`judge_verdict` 事件计数 > 2 → exit 1（轮次兜底）；三档预算字段文档条文断言 |
| BDD-9 | `test_check_judge_verdict.py` + `test_check_gate.py` | status=passed 但机械核对（计数/证据/白名单）exit 1 → 不放行（LLM 结论不单独构成放行依据）；双脚本任一 exit 1 → gate_p65 exit 1、P6→P7 阻断 |
| BDD-10 | `test_check_gate.py` + 既有回归 + `test_docs_assertions.py` | gate_p6 与审计 1-7 行为不回归（既有 P6 回归全绿）；role-system status 三值映射 / WORKFLOW P6.5 行 / state-machine 挂载条文断言；count-tests 用例数不漂移、consistency 0 ERROR |

## 3. TDD 红灯与 gate 说明

- P3 红灯以两个新文件承载（`test_check_judge_verdict.py` / `test_check_events.py`，P2-design §5 gate_commands.P3）：目标脚本未实现 → 真红灯（B 类，import 失败归 A 类需排除）。
- 增补文件（`test_check_gate.py` / `test_agate_common.py`）随 P4 实现批同批落地；`test_docs_assertions.py` 随协议文档改动变绿（文档先行断言，P4 同批）。
- 用例命名引用 BDD 编号（如 `test_bdd_4_whitelist_blacklist_path`），全部可二值判定；沿用 AGENTS.md 测试约定（tmp_path、平台无关、windows_smoke marker）。

## 4. BDD 覆盖对照

- P1 10 条 BDD → 本文档 10 行映射，每条 BDD 至少 1 个测试文件承载、无遗漏；多重承载行（BDD-4/7/8/9/10）为跨层校验（机械核对 + 文档断言 + 回归），非重复计数。
- [PROD_NOT_TOUCHED]：本文件只写任务目录产出，未改协议本体。