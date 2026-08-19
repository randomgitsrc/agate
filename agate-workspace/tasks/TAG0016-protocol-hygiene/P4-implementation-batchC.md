---
phase: P4
task_id: TAG0016
type: implementation
parent: P2-design.md
trace_id: TAG0016-P4c-20260819
status: draft
created: 2026-08-19
agent: implementer
---

implementation_dir: agate/

## 批次 3（test-evidence-provenance）实现摘要：M16-M23

### M16 — `dispatch-protocol.md` 新增「## 全量重跑点审计」
在「派发编排机制」节之前（L453）插入新小节，内容为 P2-design.md §10 四行表格（P5 首跑
必然 / P5 失败后重跑必然 / P6 refactor 独立 regression.log 条件可替代 / P8 bump-version
后重跑必然但范围可简化）原样誊写，未重新设计表格结构。

### M17 — `check-p6-provenance.py` 新增审计 7
新增：
- `EXCLUDE_PRODUCE_PREFIX = "agate-workspace/tasks/"`（复用 P2 minimal_validation 已验证前缀）
- `_run_git(task_dir, args)`：`git -C task_dir <args>` subprocess 封装（git 自动向上发现仓库根，
  兼容测试用真实 `GitRepo` fixture 构造的仓库，task_dir 为仓库子目录）
- `p6_declares_reuse(task_dir)`：正则匹配 P6-acceptance.md 是否含"引用 P5 证据"表述
- `audit7_p5_evidence_reuse(task_dir, state_yaml)`：三态返回值精确匹配测试断言
  （`no_reuse_claim_possible` / `reuse_blocked` / `reuse_allowed`），用 Python 列表过滤代替
  shell `grep -v`（天然规避 P2 §3.5 附注的"grep 无匹配退出码 1"边界问题，未引入该风险）
- main() 内新增审计 7 调用块（p6_exists 时读取 `.state.yaml`，pyyaml 缺失/文件缺失均静默
  降级为 `state_yaml={}` → `no_reuse_claim_possible` 语义，非阻塞）；仅当
  `reuse_blocked` 且 `p6_declares_reuse` 为真时 `sys.exit(1)`（错误信息已在函数内部写 stderr）
- docstring 头部审计计数 "六道" 改 "七道"，补充第 7 条描述

### M18 — 测试变绿（未改测试代码）
`test_check_p6_provenance.py` 审计 7 相关 4 条用例全部由红转绿；文件其余 41 条既有用例
无回归（该文件共 45 passed）。

### M19 — `.state.yaml` schema 文档
`state-machine.md`「每任务独立状态文件」YAML 样例中新增 `p5_pass_commit` 字段行（带
注释说明可选/回退语义），并在「字段说明」列表补一条对应说明，指回
`P5-verification.md` 写入时机。`agate-state-yaml-check.py` 未改动（P2 已确认无
unknown-field 拒绝逻辑）。

### M20 — `P5-verification.md` 写入点
在原步骤 4（git add）之前插入新步骤：`git rev-parse HEAD` 取父提交哈希写入
`p5_pass_commit`，并附加 R9 操作纪律警示行（"P5 commit 不得混入非产出文件改动……应先回
P4 走正常流程"，引用真实反例 `5bdcd90`）；原步骤 4-6 顺延为 5-7。

### M21 — `P6-acceptance.md` 新分支
在 refactor 回归验收口径小节之后新增「### P6-acceptance.md（引用 P5 证据、不重跑：
BDD-12/13）」，写明三态判定（`reuse_allowed`/`reuse_blocked`/`no_reuse_claim_possible`）
各自对应的证据要求，以及 gate 拦截规则（声明复用但判定 blocked → exit 1）与失败方向
保守性说明。同时在「## gate 规则」的 `check-p6-provenance.py` 命令行注释里追加"P5证据
复用判定（审计7，BDD-12/13）"。

### M22 — `P8-release.md` 精简重跑表述
「主 Agent 必须亲自执行」清单中"重跑 P5 gate"一条改为条件化表述（按 P2 §1.1 M22 确切
措辞：无改动→复用 `P5-test-results/`，不重新执行命令；否则完整重跑
`gate_commands.P5`）。同步微调「推进条件」一行措辞与之呼应（未改变语义，只是让两处
表述一致）。

### M23 — CI xdist 观测步骤
`.github/workflows/protocol-tests.yml` 的 `pytest` job 新增
"xdist Timing Observation (Linux)" 步骤，`continue-on-error: true` + `pip install
pytest-xdist` + `time python3 -m pytest -n auto agate/tests/`，仅 Linux 侧运行，
不设置 exit code 判据，不影响 job 整体结果。

## 测试变绿情况

- `test_check_p6_provenance.py`：4 条审计 7 用例（`test_bdd_12_audit7_no_changes_reuse_allowed`
  / `test_bdd_13_audit7_non_produce_change_reuse_blocked` /
  `test_bdd_12_audit7_missing_field_no_reuse_claim_possible` /
  `test_bdd_13_audit7_only_produce_dirs_excluded_active_tasks_board`）全部由红转绿，
  文件整体 45 passed，测试代码本身未改动。
- `test_protocol_dedup_audit.py`：BDD-11（`test_bdd_11_rerun_audit_table_exists`）/
  BDD-14（`test_bdd_14_p8_release_reuse_wording`）/ BDD-15
  （`test_bdd_15_ci_xdist_observability_step`）3 条由红转绿，文件整体 16 passed（含
  批次 1 已绿的 BDD-1/2/3/4/5/7/16/18 回归防护均未破坏），测试代码本身未改动。

## 全量 pytest 结果

`timeout 180s python3 -m pytest agate/tests/ -q --tb=line`：**958 passed, 1 failed, 2 skipped**。

唯一失败为 `test_env_adapt_docs.py::test_bdd_34_shellcheck_three_hook_shells_and_ruff`——
ruff 报的是 `test_protocol_dedup_audit.py` 自身的既有 lint 问题（`I001` import 排序 +
`E741` 变量名 `l`），属批次 1 就已存在、dispatch-context 明确排除在本批次范围外的
既有问题（测试代码不可改）。本批次新增代码（`check-p6-provenance.py` 的
`_run_git`/`p6_declares_reuse`/`audit7_p5_evidence_reuse`）已过 `ruff check`（自查时
发现 1 处 `RUF005` list 拼接警告并已修复，非"顺手改进"，是本批次自己新代码引入的
问题，修复后 `ruff check agate/scripts/check-p6-provenance.py` 显示 all checks passed）。

失败数从批次开始时的 8 failed 降到 0（本批次范围内），剩余 1 failed 为既有 ruff lint
问题（不在本批次门槛范围）。`check-protocol-consistency.py`（非 strict）自查：0 ERROR，
308 WARNING（与批次 2 完成时基线一致，未引入新 WARNING）。

## 未涉及范围确认

未改动批次 1（doc-dedup）与批次 2（check12-anti-recurrence）已完成的文件/内容：
`agate/WORKFLOW.md`、`dispatch-protocol.md`「平台适配」等既有节、
`check-protocol-consistency.py`、`assets/templates/dispatch-prompt.md`、
`rules/state-transitions.md`、`platform-notes.md` 均未触碰；`dispatch-protocol.md` 本批次
仅新增 M16「全量重跑点审计」一个小节。DEBT0010（`agate-read-gate-commands.py` 的
`P3_timeout_seconds` 误判 bug）与本批次改动无交集，未修复，维持既有登记状态。

无 DESIGN_GAP / SCOPE+ / CLARIFY 需要标注——P2 §1.1/§3/§10 对 M16-M23 的设计描述已足够
明确，实现过程中未发现歧义或范围外必须项。
