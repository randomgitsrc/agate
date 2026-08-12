---
phase: P4
task_id: TAG0002-refactor-first-class
type: implementation
parent: P4-review.md
trace_id: TAG0002-P4-20260812
status: draft
created: 2026-08-12
agent: implementer
---

# TAG0002 — P4 评审修复轮（implementer-review-fix）：change_type 正文回退误判 BLOCKER

> 修复依据：P4-review.md §2.1 BLOCKER + 修复方案 A + §5 回归用例建议。
> 环境隔离：本改动仅落 worktree `agate/` 与任务 docs，未触碰 `~/.agate`（v0.40.2 稳定版开发工具）与主 checkout。`[PROD_NOT_TOUCHED]`

## 1. BLOCKER 修复：change_type 改为 frontmatter-only 读取

修复对象：`agate/scripts/agate-md-field-get.py`

问题链（P4-review §2.1 实证）：`change_type` 在 `_regex_fallback`（L172-173）用 `change_type:\s*(\S+)` 全文扫描对任意值匹配 → 功能任务（frontmatter 无 change_type）P1 正文出现 `change_type: refactor` 字样即被误判 refactor → check-gate.sh P6 分流误拦（exit 1）+ ci-gate-backstop P3 误跳 check-tdd-red（SKIP）→ 违反 BDD-2"未声明 change_type 的任务验收行为与改造前完全一致"。

修复方案（P4-review 方案 A，主 Agent 采纳）：复用 NO_FALLBACK 语义（同 `regression_pass` 的 NO_FALLBACK_BOOL_FIELDS 先例）。

| 落点 | 改动 |
|---|---|
| `NO_FALLBACK_STRING_FIELDS`（新增，L78） | `frozenset({"change_type"})`——frontmatter 无该字段输出空串，不做正文正则回退 |
| `STRING_FIELDS`（L107） | 移除 `change_type`（仅保留 override / internal_only_reason / 跳过风险 / risk_level） |
| `_regex_fallback` | 删除 change_type 分支（不再全文扫描 `change_type:\s*(\S+)`） |
| `_get` no-fallback 判定 | 并入 `NO_FALLBACK_STRING_FIELDS`（frontmatter 无该字段直接 return ""） |
| `KNOWN_OPS` | 并入 `NO_FALLBACK_STRING_FIELDS`（op 合法，供调用方使用） |
| 模块 docstring（L15-17） | change_type 描述改为"frontmatter-only，无正文回退；正文散文提及不读取" |

设计理由（与 risk_level 的区别）：change_type 是 TAG0002 新增 P1 机器字段，v0.35 正文旧格式从未有该字段，**无向后兼容需求**；risk_level 有旧正文格式（`--legacy-fields` BDD-9 回退），保留正文回退。修复后语义稳定：未声明即功能口径，不受正文是否恰好出现字符串影响。

## 2. 回归用例（补 4 条 + 改 1 条契约）

| 文件 | 用例 | 断言 |
|---|---|---|
| `agate/tests/unit/agate-md-field-get.bats` | `MDF.8`（改契约） | frontmatter 无 change_type、正文行 `change_type: refactor` → 输出空 |
| 同上 | `MDF.11`（新增） | 正文散文 `change_type: refactor 是可选字段` → 输出空（BDD-2） |
| 同上 | `MDF.12`（新增） | 正文否定式 `本任务不涉及 change_type: refactor 机制` → 输出空（BDD-2） |
| `agate/tests/unit/check-gate.bats` | `test_bdd_2b_p6_gate_default_body_mentions_change_type_still_functional`（新增） | 功能任务 P1 正文提及关键字 → P6 gate exit 2（不误拦） |
| `agate/tests/unit/ci-gate-backstop.bats` | `backstop P3: 功能任务正文提及 change_type 关键字仍走 TDD 兜底（不 SKIP，BDD-2）`（新增） | mock tdd-red exit 2 → 输出 FAIL + 绿灯，不含 `SKIP: refactor`（不误跳） |

MDF.8 原契约（正文回退输出 refactor）随 BLOCKER 修复改为 frontmatter-only 断言，P3-test-cases.md §3.2/§3.4 及 BDD 映射表已同步。

## 3. 低危顺手项（P4-review §3 观察点）

`agate/scripts/ci-gate-backstop.py`：`_read_p1_change_type()` 内 `import os as _os`（L89）与模块顶部 `import os`（L11）重复 → 删除函数内重复 import，改用模块级 `os.environ`。行为不变，成本低，顺手修复。

## 4. 自查结果（P4 自查 ≠ P5 gate）

| 检查 | 命令 | 结果 |
|---|---|---|
| P3 目标 4 文件 | `bats agate/tests/unit/check-gate.bats agate/tests/unit/agate-md-field-get.bats agate/tests/unit/check-frontmatter.bats agate/tests/unit/ci-gate-backstop.bats` | 147/147 通过，0 not ok（111+12+14+10） |
| 全量回归 | `bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/` | 654/654 通过（650 基线 + 4 新增），0 not ok |
| shellcheck | `shellcheck -S warning agate/scripts/*.sh` | 0 error |
| 协议一致性 | `python3 agate/scripts/check-protocol-consistency.py` | 0 ERROR（全部检查 PASS） |
| 用例计数 | `bash agate/tests/scripts/count-tests.sh` | 总计 648（644 基线 + 4 新增，MDF.8 改契约不计数） |

手动实证（修复后）：frontmatter `change_type: refactor` → 输出 `refactor`；正文散文提及/否定式提及/正文行 → 均输出空；`risk_level` 正文回退不受影响（对照）。`grep` 确认 `agate-md-field-get.py` 无 `change_type:\s*(\S+)` 残留。

## 5. 备注

- **self-gate 触发**：本次改动含 `agate/scripts/agate-md-field-get.py` + `agate/scripts/ci-gate-backstop.py`（commit-msg-self-gate.sh 的触发文件，L30 覆盖 `agate/scripts/*.py`）。主 Agent commit 时须在 message 含 `self-gate-review: <路径>` 或 `self-gate-skip: <理由>`，否则 WARNING。
- 无 DESIGN_GAP / SCOPE+ / SCOPE_GAP 新增——修复严格按 P4-review 方案 A 落地，测试契约变更已同步 P3-test-cases.md。
- 未改动修复清单之外的无关文件。
