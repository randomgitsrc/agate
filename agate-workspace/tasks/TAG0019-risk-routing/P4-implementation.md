---
phase: P4
task_id: TAG0019-risk-routing
type: implementation
parent: P2-design.md
trace_id: TAG0019-P4-20260821
status: draft
created: 2026-08-21
agent: implementer
---

# P4 实现记录 — TAG0019 风险分路由（ceremony routing，RM-AG0031）

> 状态标记：`[PROD_NOT_TOUCHED]`（本任务仅改动 agate 协议本体脚本/测试/文档，无任何生产环境接触）。

implementation_dir: agate/scripts

## 新增文件核对表

> 本项目未采用骨架（无 P2-skeleton.md）与 CODE-MAP（无 agents/CODE-MAP.md）机制，按 P4 卡模板标注。

| 新增文件路径 | 骨架归属 | CODE-MAP 处理 |
|------------|---------|--------------|
| agate/scripts/agate-risk-score.py | [SKELETON_DEVIATION: 无骨架机制] | [CODE_MAP_EXEMPT: 无 CODE-MAP 机制] |
| agate/scripts/check-routing.py | [SKELETON_DEVIATION: 无骨架机制] | [CODE_MAP_EXEMPT: 无 CODE-MAP 机制] |

> 测试文件（test_agate_risk_score.py / test_check_routing.py 等）为 P3 阶段新增、本阶段定向修改补充用例，非本阶段新增交付物，不纳入上表；测试属测试资产（P2 D 表），CODE-MAP 豁免同理由。

## 实现摘要

### core 批（本 implementer）

1. **`agate/scripts/agate-risk-score.py`（新）** — 客观信号算分：`score_task(task_dir) -> dict`（file-type / sensitive-path / change-size / impact 四信号 + domain-markers + risk_score 加权和 + tier 合成 thin|standard|full + 逐信号证据行 + `git_ok` 标记）+ CLI 薄壳。git 全经 `agate_common.run_git`；路径 `relpath().replace("\\","/")`；行数 `.rstrip("\r")`；importlib 复用 check-pruning `_staged_source_count`。异常（run_git 失败 / agate_common 不可导入）→ `git_ok: false` 不静默降级（P2 §2.3 NB-2②）。敏感关键词经三轮评审收敛：左锚 `(?<![A-Za-z0-9_])` + 词干 + `\w*` 尾随（覆盖复数/下划线拼接/词干形态，F2），`auth(?!or)`/`api(?!ary)` 区分 author/apiary 误标（F3 不回退）。
2. **`agate/scripts/check-routing.py`（新）** — ceremony 声明校验（P2 §2.3 判定流）：P1 缺失 → exit 2；不声明 → exit 0（=standard，BDD-8）；非法值 → exit 1（BDD-6 兜底）；thin → 四要素（coupling_checklist 流式 + 跳过风险: + phases 含 P5/P6）任一缺 → exit 1（BDD-7）；thin 且算分 tier∈{standard,full} → exit 1（单向 fail-closed，BDD-9）；thin 且 `git_ok: false` → exit 1（NB-2②）；standard/full → exit 0。importlib 复用 check-pruning `_md_field`/`_read_p1`/`_staged_source_count`（模块级暴露，BDD-10）+ importlib 调 `score_task`（不 subprocess）。
3. **注册点（core 部分）**：`agate-frontmatter-check.py` P1 schema 加 ceremony（migrated_keys + enums thin/standard/full + types str）；`agate-md-field-get.py` ceremony 注册于 **NO_FALLBACK_STRING_FIELDS**（frontmatter-only，C1 修复，正文散文不误读，BDD-8）；`pre-commit-gate.py` 2j.1 挂载 `_run_script_rc("check-routing.py", [task_dir])`（gate_exit != 1 时执行，与 2j 并列）。

### docs-sync 批（另一 implementer，12 处文档）

agate-summary.py `_DRIFT_SCRIPTS`、check-protocol-consistency.py 关键词注册表、README 工具清单、tests/README 用例映射、P1 卡/角色/模板/评审映射/WORKFLOW/CONTEXT 等文档同步 ceremony 机制（主 Agent 汇总，本记录仅登记）。

### 测试修复（本 implementer）

- P4 复审二轮 F2：test_agate_risk_score.py 补 28 条 parametrized 用例（21 条复数/拼接/词干形态必 high + 7 条 author/apiary 等误标防护必 low）。
- P3 测试代码缺陷（bdd_2 双仓库 / bdd_5 src 父目录）由 P3 侧修复，本记录确认覆盖。

## 测试状态（自查 ≠ P5 gate）

- 单元：60/61（唯一 failed = test_bdd_7_thin_score_anomaly_git_ok_false_exit_1，环境前提 I1——本 DSH 沙箱所有可写 pytest basetemp 均在 git 仓库内，"非 git 上下文"不可构造；fail-closed 分支已用 GIT_DIR=/nonexistent 探针两轮验证 exit 1 正确，移交 P5 落实 git 仓库外可写 basetemp 后转绿）
- 集成：55 passed（agate/tests/integration/test_pre_commit_hook.py 全量，含 2j.1 挂载链用例）
- 回归：68 passed（check_pruning + frontmatter + md-field-get + 两回归文件）
- platform：check-platform-assumptions.py 变更文件集 0 命中 exit 0（含测试文件头 /tmp 字面清理，C2）

## 评审

P4-review.md status: **approved**（2 轮迭代：① eng 3 CRITICAL（C1-C3）+ cso 2 MEDIUM（F1/F2）全部修复；② 二轮仅剩 F2 词界方案净回退，按 cso 左锚+词干+`\w*` 方案修复；eng + cso 均无 BLOCKER 后 approved）。

## 交付清单

- 代码：agate/scripts/agate-risk-score.py（新）、agate/scripts/check-routing.py（新）、agate/scripts/agate-frontmatter-check.py（改）、agate/scripts/agate-md-field-get.py（改）、agate/scripts/pre-commit-gate.py（改）
- 测试：agate/tests/unit/test_agate_risk_score.py（改）、test_check_routing.py（改）、test_check_frontmatter.py（改）、test_agate_md_field_get.py（改）、agate/tests/integration/test_pre_commit_hook.py（改）
- 状态：`[PROD_NOT_TOUCHED]`，无生产环境改动