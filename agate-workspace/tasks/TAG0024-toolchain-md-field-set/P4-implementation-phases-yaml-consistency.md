---
phase: P4
task_id: TAG0024
type: implementation
parent: P2-design.md
trace_id: TAG0024-P4-phases-yaml-consistency-20260825
status: draft
created: 2026-08-25
agent: implementer
---

```yaml
implementation_dir: agate/rules/
```

## 改了什么

只改 `agate/rules/phases.yaml` 一个文件，两处纯追加：

1. **RM-AG0049**：`id: P4` 的 `outputs` 追加一行
   `{file: P4-review.md, required: true, status_field: status}`，补全 P4 阶段实际要求
   P4-review.md 产出的声明缺口。
2. **RM-AG0050**：`id: P6.5` 条目前追加 3 行纯 YAML 注释块，说明 P6.5 是挂载于 P6→P7
   转移的强门槛子阶段、不是与 P0-P8 平级的独立 phase 值，措辞取自
   `agate/state-machine.md` 第 74/152 行既有权威表述精神，未发明新说法；未改动
   `id`/`name`/`exec_role`/`outputs`/`gates`/`retry_cap`/`task_fields` 任何字段结构。

## 自跑：test_check_structure_consistency.py 全量结果

命令：
```
python3 -m pytest agate/tests/unit/test_check_structure_consistency.py --basetemp=.pytest-tmp -p no:cacheprovider -q
```
结果：
```
.................                                                        [100%]
17 passed in 1.56s
```
17 项全部 PASSED，0 failed（含本批次的 BDD-25/26/27/28 四项全部转绿，既有 13 项 S-1/S-2/S-3 系列用例保持绿）。

## 真实一致性检查脚本结果

命令（worktree 自己的脚本，检查对象为本 worktree 刚改的 phases.yaml）：
```
python3 agate/scripts/check-structure-consistency.py
```
输出：
```
S1-phases: OK
S2-workflow: OK
S3-cards: OK
S4-scripts: OK
S5-schema: OK
S6-references: OK
S0-numbers: OK
```
exit code 0，S-1~S-6（含 S0）全部 OK，0 mismatch。

## git diff 摘要（证明只是追加）

```diff
--- a/agate/rules/phases.yaml
+++ b/agate/rules/phases.yaml
@@ -59,6 +59,7 @@ phases:
     exec_role: implementer
     outputs:
       - {file: P4-implementation.md, required: true}
+      - {file: P4-review.md, required: true, status_field: status}
     gates:
       - {check: "暂存区含非 md/yaml 代码文件（git diff --cached --name-only）"}
       - {check: "check-gate.py P4 $TASK_DIR"}
@@ -85,6 +86,9 @@ phases:
       - {check: "check-gate.py P6.5 $TASK_DIR（= check-judge-verdict.py + check-events.py 双 exit 0；历史任务自动跳过）"}
     retry_cap: 2
     task_fields: [pass, fail, ui_affected]
+  # 注：P6.5 是挂载于 P6→P7 转移的强门槛子阶段，不是与 P0-P8 平级的独立 phase 值
+  # （.state.yaml 的 phase 字段保持 P6 直至 P7）；本条目结构化声明其产出/门槛/重试上限，
+  # 供 check-gate.py P6.5 分发与 CLI 调用，口径详见 state-machine.md「状态机定义」节。
   - id: P6.5
     name: 独立 Judge 复核
     exec_role: judge
```

仅两处新增（P4 outputs 一行 + P6.5 前 3 行注释），未删除/未修改任何既有 `id`/`gates`/`retry_cap`/`task_fields` 字段。

## 范围声明

未修改 `agate/scripts/check-gate.py`、`agate/scripts/agate-md-field-set.py`（不存在，非本批次任务）、
`agate/state-machine.md`、`agate/tests/unit/test_agate_md_field_set.py`、
`agate/tests/unit/test_check_gate.py`，符合本批次范围约束。
