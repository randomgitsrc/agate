---
phase: P4
task_id: TAG0016
type: implementation
parent: P2-design.md
trace_id: TAG0016-P4-selfgate-fix-20260819
status: draft
created: 2026-08-19
agent: implementer
---

implementation_dir: agate/

# P4 实现（SELF-GATE 语义审查修复轮）

本轮修复 `docs/reviews/agate-alignment-review-2026-08-19.md` 发现的 2 项 MISALIGNED（A1-c、A3/A5）
+ 1 项已裁决 NEEDS_HUMAN_REVIEW（A7），不改动批次 1/2/3 已经改对的其余内容，不改动测试代码的
既有断言逻辑（仅新增用例）。

## 修复目标 1（A1-c）：审计 7 在 P8 场景不可操作

**问题**：`P8-release.md`/`dispatch-protocol.md` 描述"读取 `check-p6-provenance.py` 审计 7
判定结果决定 P8 是否可复用证据"，但 `audit7_p5_evidence_reuse()` 的返回值从未输出到 stdout，
也没有独立 CLI 模式，主 Agent 实际拿不到判定结果。

**改动**：

- `agate/scripts/check-p6-provenance.py`：
  - 新增 `--audit7-only TASK_DIR` 显式模式（`main()` 顶部分支判断 `sys.argv[1] == "--audit7-only"`）。
  - 只跑审计 7（`audit7_p5_evidence_reuse`），不跑其余六道审计。
  - 三态结果打印到 stdout，一行：`AUDIT7_RESULT: <reuse_allowed|reuse_blocked|no_reuse_claim_possible>`。
  - exit code：`reuse_allowed` → 0；`reuse_blocked` → 1；`no_reuse_claim_possible` → 0（字段缺失
    是"无法声明复用"而非"错误"，与主流程审计 7 的静默回退语义一致）。
  - 新增 `_load_state_yaml(task_dir)` 辅助函数，从 `main()` 原有的 `.state.yaml` 读取逻辑中
    提取出来，`--audit7-only` 分支与原有审计 7 调用点共用，避免重复代码。
  - 不带 `--audit7-only` 参数时的既有行为完全不变（六道/七道审计全套逻辑不动，仅新增可选独立入口）。
  - 文档头部（docstring）新增该模式的用法说明。

- `agate/phase-cards/P8-release.md`（L82-86）：把"若 check-p6-provenance.py 审计 7 判定……"
  这句抽象表述改为可执行操作步骤：跑 `python3 agate/scripts/check-p6-provenance.py --audit7-only
  $TASK_DIR`，读 stdout 的 `AUDIT7_RESULT:` 行，`reuse_allowed` → 复用 `P5-test-results/`；
  `reuse_blocked` / `no_reuse_claim_possible` → 完整重跑 `gate_commands.P5`。

- `agate/dispatch-protocol.md`「全量重跑点审计」表 P8 行（L462）：同步改为具体命令 +
  `AUDIT7_RESULT:` 判定步骤，措辞与 P8-release.md 一致（不再是"复用/简化"的抽象描述）。
  未改动该表中 P6 行（该行原有措辞已可操作，不属于本次修复范围）。

**验证**：手工构造真实 git 仓库（`git init` + 两次 commit）验证三态：

```
case1 reuse_allowed expected: 0 AUDIT7_RESULT: reuse_allowed
case2 reuse_blocked expected: 1 AUDIT7_RESULT: reuse_blocked
case3 no_reuse_claim_possible expected: 0 AUDIT7_RESULT: no_reuse_claim_possible
```

exit code 与 stdout 行格式均符合规格。

## 修复目标 2（A3/A5）：verifier.md / dispatch-prompt.md 未同步新机制

**问题**："P5→P6 无代码改动时可引用 P5 证据、不必重跑"这个新选项只落到了
`phase-cards/P6-acceptance.md`（操作卡）和 `check-p6-provenance.py`（脚本），verifier 角色卡和
派发 prompt 权威源都未提及，verifier subagent 若不靠 dispatch-context 每次手写提醒，不知道该
选项存在。

**改动**：

- `agate/assets/execution-roles/verifier.md`：在「refactor 任务验收口径」小节之后新增
  「引用 P5 证据、不重跑（P6 模式，TAG0016 BDD-12/13）」小节（5 行）：说明判定条件
  （`.state.yaml` 有 `p5_pass_commit` 字段 + 主 Agent 跑审计 7 判定 `reuse_allowed`）、可引用
  `P5-test-results/` 而非独立产出 `regression.log`，明确判定权在主 Agent、verifier 不自行
  判断，并指向 `P6-acceptance.md` 权威节获取完整格式规则（不复制第二份完整描述，避免和
  `phase-cards/P6-acceptance.md` 产生第二处可能漂移的完整规则拷贝——这正是本任务本身要防的
  反模式）。

- `agate/assets/templates/dispatch-prompt.md`「P5/P6 派发追加」节：在「P6 BDD 覆盖完整性」
  后加一句提示（2 行）：`## P6 引用 P5 证据、不重跑（refactor 任务，若适用）`，指向 verifier.md
  的新增小节，不展开完整规则。

## 修复目标 3（A7，已裁决）：新增 ADR-010

**背景**：审查在 A7 提出"P5→P6/P8 间无代码改动时可复用证据"是在 ADR-004"完整重跑是安全网"
哲学基础上开的受控例外口子，属新架构原则，建议记录为正式 ADR。主 Agent 已裁决：需要（工程判断，
非业务方向问题）。

**改动**：`agate/adr.md` 末尾新增 **ADR-010: 受控例外——满足客观可判定条件时允许复用既有验证
证据**（格式参照现有 ADR-002/ADR-004 的 状态/语境/决策/理由/后果 五节结构）：

- **语境**：概括 RM-AG0026 的问题（P5→P6→P8 重复全量测试成本）+ ADR-004 既有哲学与本次缺口的关系
- **决策**：满足客观可判定条件时允许复用证据，不重新执行验证；判定标准必须机器可判定
  （呼应 ADR-002），不依赖主观声明（呼应 C7 规则"subagent 自我报告不可信"精神）
- **理由**：引用 P2-design.md §3.2 的失败方向保守性论证（不会产生"应重跑却被跳过"的安全漏洞，
  只会产生"该被判定可复用却被误判为需要重跑"这种保守方向的误判）+ R9 残余风险（真实反例
  `5bdcd90` P5 commit 混入非产出文件改动会破坏等价性前提，已有 `P5-verification.md` 操作纪律缓解）
- **后果**：本次落地为 `check-p6-provenance.py` 审计 7（BDD-12/13）+ P6/P8 两处应用；未来任何
  类似"复用而非重跑"设计都应参照本 ADR 判定标准（机器可判定 + 失败方向保守 + 显式声明何时不可
  复用），判定权始终归主 Agent

## 新增测试（--audit7-only CLI 模式，此前无测试覆盖）

`agate/tests/unit/test_check_p6_provenance.py` 新增 4 条 CLI 模式测试用例（不改动任何已有断言
逻辑，纯新增）：

- `test_audit7_only_reuse_allowed_stdout_and_exit0`：无改动场景，exit 0 + stdout 含
  `AUDIT7_RESULT: reuse_allowed`
- `test_audit7_only_reuse_blocked_stdout_and_exit1`：非产出文件改动场景，exit 1 + stdout 含
  `AUDIT7_RESULT: reuse_blocked`
- `test_audit7_only_missing_field_no_reuse_claim_possible_exit0`：`.state.yaml` 无
  `p5_pass_commit` 字段，exit 0 + stdout 含 `AUDIT7_RESULT: no_reuse_claim_possible`
- `test_audit7_only_missing_task_dir_arg_exit1`：缺 TASK_DIR 参数，exit 1

均复用既有 `_init_repo_with_p5_commit` / `GitRepo` fixture 思路，用真实 git 仓库而非 mock，
与既有审计 7 单元测试（`test_bdd_12_*`/`test_bdd_13_*`）保持同一验证路径风格。

## 验证结果

- 新增 4 条 --audit7-only 测试：单独跑 `-k audit7` → 8 passed（4 条既有函数级测试 + 4 条新增
  CLI 测试）。
- 全量 pytest：`timeout 180s python3 -m pytest agate/tests/ -q --tb=no` → **963 passed, 2
  skipped, 0 failed**（基线 959 passed + 新增 4 条，无回归、无新失败）。

## 改动文件清单

- `agate/scripts/check-p6-provenance.py`（新增 `--audit7-only` CLI 模式）
- `agate/phase-cards/P8-release.md`（P5 验证步骤措辞改为可执行命令）
- `agate/dispatch-protocol.md`（「全量重跑点审计」表 P8 行措辞同步）
- `agate/assets/execution-roles/verifier.md`（新增「引用 P5 证据、不重跑」小节）
- `agate/assets/templates/dispatch-prompt.md`（「P5/P6 派发追加」节新增指针句）
- `agate/adr.md`（新增 ADR-010）
- `agate/tests/unit/test_check_p6_provenance.py`（新增 4 条 --audit7-only CLI 测试用例）
