---
phase: P6
task_id: TAG0021-structured-layer
type: acceptance
parent: P5-verification.md
trace_id: TAG0021-P6-20260822
status: draft
created: 2026-08-22
agent: verifier
# ── v2.0 机器汇总 ──
pass: 16
fail: 0
ui_affected: false
---

# P6 验收报告 — TAG0021 协议结构化层（RM-AG0022）

> 状态标记：[PROD_NOT_TOUCHED]（全程只读 worktree 代码/协议；唯一写操作 = P6-acceptance.md + P6-evidence/ + P6-progress.md；漂移反例在可写 dist/ 副本上制造，验收后已清理删除）
> 验收对象: worktree `/home/kity/oclab/agate/.worktrees/agate-TAG0021`（HEAD `074e315` = P5 commit，代码树干净）
> 口径: P1 的 16 条 BDD 逐条实跑/实查（When 动作真实执行、Then 判据从命令输出/文件内容实读）；domains=[backend]、ui_affected=false，无 UI/视觉验收；M0 环境假象（test_bdd_7 / test_bdd_25）按派发口径「全量 pytest 1198 过 + 2 环境假象（隔离复跑转绿或固有）」记录，不判 FAIL

## M0 — 数据层就位（BDD-1..5）

**实跑记录（M0 组）**：
- BDD-1：实查 `agate/rules/{phases,dispatch,roles}.yaml` + `rules/schema/*.json` 6 文件存在；实跑 `check-yaml-schema.py`（AGATE_ROOT=worktree/agate）→ `SCHEMA-phases/dispatch/roles: OK`，EXIT_CODE 0。
- BDD-2：正向实跑 `check-structure-consistency.py` → S1-phases/S2-workflow OK，exit 0。反例在可写 dist/ 副本上制造：① 副本 phases.yaml 篡改 P2 name → `S1-phases: ERROR phase P2 name 不一致`，EXIT_CODE 1（YAML→md 方向）；② 副本 WORKFLOW.md 总览表插入 P9 行 → `S2-workflow: ERROR 阶段 P9 未在 phases.yaml 定义`，EXIT_CODE 1（md→YAML 方向）。
- BDD-3：反例① 副本 phases.yaml P1 exec_role 改 bogus-role → S5-schema ERROR（枚举非法）+ EXIT_CODE 1；反例② 副本 roles.yaml analyst file 改 nonexistent.md → `S6-references: ERROR 引用不存在` + EXIT_CODE 1；正向（真实树）S5/S6 OK exit 0。
- BDD-4/5：见各 PASS 行证据；全量 pytest 1198 过 + 2 环境假象（复核：清空 dist/ 后 test_bdd_25 隔离转绿、test_bdd_7 隔离仍红为沙箱 basetemp 在 git 仓库内的固有语义，与改动零耦合，CI /tmp 在仓库外均通过）；consistency `仅有 318 个 WARNING，无 ERROR` exit 0；count 1202；S-3/S-4 与 check-gate P2 判定三方一致（RECONCILE SUMMARY 0 mismatches）。

- PASS BDD-1: (M0) rules/ 三 YAML 与 schema 存在且 check-yaml-schema.py 全过 exit 0 (P6-evidence/bdd-1-schema.log, P6-evidence/bdd-targeted-pytest.log)
- PASS BDD-2: (M0) S-1/S-2 双向一致——无漂移 exit 0、S-1 YAML→md 漂移与 S-2 md→YAML 漂移均 exit 1 (P6-evidence/bdd-2-s1s2.log, P6-evidence/bdd-2-s1s2-neg.log)
- PASS BDD-3: (M0) S-5 schema 枚举非法与 S-6 引用缺失均非 0、合法全过 0 (P6-evidence/bdd-3-s5s6.log, P6-evidence/bdd-3-s5s6-neg.log)
- PASS BDD-4: (M0) 存量行为不变——全量 pytest 1198 过 + 2 环境假象（test_bdd_25 清空隔离转绿 / test_bdd_7 沙箱固有），count 1202 ≥ 749，consistency 0 ERROR (P6-evidence/bdd-4-pytest-full.log, P6-evidence/bdd-4-env-artifacts.log, P6-evidence/bdd-4-consistency.log)
- PASS BDD-5: (M0) S-3/S-4 三方一致 exit 0（phases.yaml ↔ P2 卡 ↔ check-gate P2 判定）(P6-evidence/bdd-5-s3s4.log, P6-evidence/bdd-8-reconcile-zero.log)

## M1 — 双跑对账（BDD-6/7）

**实跑记录（M1 组）**：
- BDD-6：dist/ 副本任务注入已知差异（P2-design.md gate_commands 块加未声明键 `P9_custom`），实跑 `check-gate.py P2 副本` → stderr `RECONCILE WARNING: check-gate-P2 gate_commands.P9_custom: grep=P9_custom structured=(未声明)` + `RECONCILE SUMMARY: 1 mismatches across 2 fields`；EXIT_CODE 2 与真实任务同命令一致（= P2 原 grep 判定语义，对账不新增阻断）。
- BDD-7：静态实扫：agate-read-gate-commands.py（6 处对账调用）/ check-pruning.py（10 处）/ check-gate.py（10 处）= 3 脚本 ≥ 3；解析点覆盖 ① gate_commands 块 ② P1 裁剪字段 risk_level/phases ③ P2 四字段+candidate_count 三类；agate_common 提供 reconcile_field/reconcile_summary/read_rules_yaml/known_phase_ids/is_legal_gate_key 工具函数。pytest test_check_reconcile（BDD-6/7/8）7/7 passed。

- PASS BDD-6: (M1) 对账模式告警不阻断——差异夹具 stderr RECONCILE WARNING + SUMMARY 计数（1 mismatches），退出码 2 原语义不变 (P6-evidence/bdd-6-reconcile-warning.log)
- PASS BDD-7: (M1) 对账覆盖面 3 脚本（read-gate-commands/pruning/check-gate）× 3 类解析点（gate_commands 块/P1 裁剪字段/P2 四字段）(P6-evidence/bdd-7-coverage.log)

## M2 — 切换权威源（BDD-8..11）

**实跑记录（M2 组）**：
- BDD-8：真实任务实跑 `check-gate.py P2` → `RECONCILE SUMMARY: 0 mismatches across 1 fields`（对账清零），EXIT_CODE 2 = 原判定；test_check_reconcile 一致夹具 7/7 绿。
- BDD-9：静态实扫 4 个已迁移脚本（read-gate-commands/pruning/check-gate/md-field-get）：禁令字面量 A `^(packages|domains|ui_affected|gate_commands):` 与 B `^gate_commands:` 均 0 命中；解析逻辑已单点化至 agate_common `parse_gate_commands_block`（行 784）/ `count_p2_declared_fields`（行 798）。
- BDD-10：三处阻断齐证——① 脚本级：S-1/S-2 漂移副本均 EXIT_CODE 1（bdd-2-s1s2-neg.log）；② pre-commit-gate.py 2j.2 行 410-416 独立调用结构一致性 step（exit 1 阻断 commit，脚本缺失 fail-open）；③ CI `.github/workflows/protocol-tests.yml` 行 131-132 `Run structure consistency check (TAG0021 M2, Linux)` 步骤；pytest test_structure_migration（bdd_10 脚本漂移阻断/pre-commit 接入/CI 接入）4/4 绿。
- BDD-11：见全量回归证据（与 BDD-4 同批命令，BEFORE/AFTER 口径一致：pytest 2 环境假象 + consistency 0 ERROR + count 1202）。

- PASS BDD-8: (M2) 对账清零——真实任务 RECONCILE SUMMARY 0 mismatches，test_check_reconcile 7/7 (P6-evidence/bdd-8-reconcile-zero.log, P6-evidence/bdd-targeted-pytest.log)
- PASS BDD-9: (M2) 已迁移解析点静态零命中——4 脚本两禁令字面量均 0 命中，解析逻辑单点化 agate_common (P6-evidence/bdd-9-static-zero.log)
- PASS BDD-10: (M2) 一致性 gate 三处阻断——脚本漂移 exit 1 + pre-commit 独立 step + CI job step (P6-evidence/bdd-10-blocking.log, P6-evidence/bdd-2-s1s2-neg.log)
- PASS BDD-11: (M2) 迁移后回归全绿——全量 pytest（2 环境假象口径）+ consistency 0 ERROR + count 1202 (P6-evidence/bdd-4-pytest-full.log, P6-evidence/bdd-4-consistency.log, P6-evidence/bdd-15-count.log)

## M3 — 卡片渲染化（BDD-12..14）

**实跑记录（M3 组）**：
- BDD-12：真实树 S-3 OK exit 0；dist/ 副本 phases.yaml P2 outputs 注入伪造产出 `P2-fake-output.md` → `S3-cards: ERROR phase P2 产出 P2-fake-output.md 未出现在 P2-design.md`，EXIT_CODE 1；pytest test_card_render BDD-12 两例（默认假树 exit 0 / 篡改假树 exit 非 0）绿。
- BDD-13：pytest test_card_render BDD-13 两例用真实 agate-inject-card.py/next-card.py + AGATE_ROOT 假树构造：① worktree 注入的卡片块含 AGATE_ROOT YAML 声明的输出名（渲染化兼容）② 稳定版树与 worktree 树标记差异化时互不污染（稳定版注入不含 worktree 未发布 marker）——4/4 绿。
- BDD-14：全量回归四闸全绿（pytest 2 环境假象口径 + consistency 0 ERROR + count 1202 + structure S1-S6 全 OK + schema 全 OK）。

- PASS BDD-12: (M3) 渲染一致——真实树 S-3 OK exit 0；篡改 phases.yaml P2 产出 → S-3 ERROR exit 1 (P6-evidence/bdd-12-s3-tamper.log)
- PASS BDD-13: (M3) inject-card 渲染化 + 稳定版隔离——BDD-13 两例（YAML 渲染注入 + AGATE_ROOT 双树互不污染）4/4 (P6-evidence/bdd-targeted-pytest.log)
- PASS BDD-14: (M3) 渲染化回归全绿——全量 pytest（2 环境假象口径）+ consistency 0 ERROR + count 1202 + structure S1-S6 全 OK + schema 全 OK (P6-evidence/bdd-4-pytest-full.log, P6-evidence/bdd-2-s1s2.log, P6-evidence/bdd-1-schema.log)

## 跨里程碑回归（BDD-15/16）

**实跑记录（跨里程碑组）**：
- BDD-15：实跑 `bash agate/tests/scripts/count-tests.sh` → `总计：1202 个测试用例` ≥ 749 立项基线，EXIT_CODE 0（只增不减）。
- BDD-16：实跑 `check-platform-assumptions.py` 逐文件扫 TAG0021 新增/修改 9 脚本（check-yaml-schema/check-structure-consistency/agate_common/read-gate-commands/check-pruning/check-gate/md-field-get/next-card/inject-card）→ 全部 0 命中 exit 0；tests 默认扫描面 exit 0。全 scripts 扫描中的既有 R1/R2/R3 命中（agate-install、hook 薄壳、错误提示字符串等）为历史基线（本次 diff 前已存在，pre-commit-gate.py:62 命中位于既有 import 守卫文本，非本任务新增行）。

- PASS BDD-15: (M0-M3 全程) count-tests 只增不减——1202 ≥ 749 立项基线 (P6-evidence/bdd-15-count.log)
- PASS BDD-16: (M0-M3 全程) 测试平台无关——9 个新/改脚本逐文件 0 命中 + tests 默认面 exit 0；既有脚本命中均为历史基线（非本任务引入）(P6-evidence/bdd-16-platform.log)

## Summary

**Summary**: 16/16 PASS, 0 FAIL（逐条实跑/实查；M0 环境假象 2 项按派发口径记录放行）