---
phase: P6
task_id: TAG0022-confirmed-problems
type: acceptance
parent: P5-test-results/
trace_id: TAG0022-P6-20260822
status: draft
created: 2026-08-22
agent: verifier
# ── v2.0 机器汇总 ──
pass: 10
fail: 0
ui_affected: false
---

# P6 验收报告 — TAG0022 三连任务确认问题修复批（RM-AG0037~RM-AG0041）

> 状态标记：[PROD_NOT_TOUCHED]（仅读协议/代码文件与稳定版 `~/.agate`；写操作全部落在 P6-acceptance.md / P6-evidence/ / P6-progress.md）
> 验收对象：worktree `/home/kity/oclab/agate/.worktrees/agate-TAG0022`，HEAD `712bb0c`（wf(TAG0022-P5)）
> 验收口径：dispatch-context 验收口径表（10 条 BDD 逐条实跑，PASS/FAIL 二值）；domains=[backend]，无 UI/视觉验收面
> 环境：Linux；/tmp 只读 → pytest 一律 `-p no:cacheprovider --basetemp=<可写目录>`；bash 一律 timeout 包裹；双工作区纪律（consistency/structure 用 worktree 自己的脚本，`~/.agate` 稳定版只读）

## 逐条 BDD 验收结果

- PASS BDD-1: CI ruff job 可被 required check 引用且配置步骤文档化——workflow 含稳定 `name: ruff` job（无歧义改名，L106-117）+ `ruff==0.16.4` 锁版本；UPGRADING.md L97-109 含「将 ruff job 设为 PR required check（维护者在仓库设置勾选）」配置步骤，AGENTS.md L157 同步(bdd-01-workflow-docs.log)
- PASS BDD-2: 新任务合并时 ruff 零违规（验收锚，防复发）——`~/.venvs/agate-dev/bin/ruff check agate/` 连续两次均 exit 0（All checks passed!），本地 ruff 0.16.4 与 CI 锁版本 ruff==0.16.4 一致(bdd-02-ruff.log)
- PASS BDD-3: check-gate.py 协议规则类 md 解析清零（验收锚前半）——test_md_parse_scan.py 静态扫描 A/B/C/D 组模式命中数 = 0 断言通过（1 passed, exit 0）(bdd-03-scan.log)
- PASS BDD-4: 迁移后全量测试绿（验收锚后半）——全量 pytest（外部 basetemp ptmp）1213 passed, 2 skipped, 0 failed（exit 0）；count-tests 1215 ≥ 1202（只增不减）；consistency 0 ERROR（321 WARNING 历史类）；structure S0-S6 全 OK 0 漂移(bdd-04-full-pytest.log, bdd-04-gates.log, test-output.log)
- PASS BDD-5: S-1~S-6 收紧为「YAML 权威、md 禁止承载可判定规则」——test_check_structure_consistency.py 13 passed（含 S-3a YAML→md 漂移 exit 1 / S-3b md→YAML 漂移 exit 1 / 双侧一致 exit 0 用例），exit 0(bdd-05-s3.log)
- PASS BDD-6: 机制后新任务 P1 不写 judge 即被拦（验收锚）——test_check_gate.py 172 passed：机制后新任务缺 judge 块 → exit 1、judge 声明未启用（cutoff 后）→ exit 1、含 judge.enabled: true → exit 2 放行(bdd-06-07-judge.log)
- PASS BDD-7: 历史任务（机制前）跳过，存量不挂——机制前任务无 judge 块 / 禁用 / 非 dict 畸形均 exit 2 不被拦（向后兼容，与 gate_p65 历史兼容语义一致）(bdd-06-07-judge.log)
- PASS BDD-8: 实证执行计划 + 触发条件落盘（本 task 验收锚）——P2-design.md §4.4.1（L203-211）含 M3 四要素（评审轮数指标 / 真实发现数指标 / TAG0018 基线值 4 场≈0 净收益 / 不达标回滚 standard 决策规则）+ 触发条件（下一 low 风险任务 / 用户指定薄任务真跑 thin），各自有采集/判定口径可二值判定；已知边界（执行语义无机械校验）L213 已写明(bdd-08-plan-check.md)
- PASS BDD-9: 任意 basetemp 位置下全量 pytest 0 失败（验收锚）——仓库内默认 basetemp（agate/.bt-p6-verify）与仓库外显式 basetemp（ptmp）两位置均 1213 passed, 2 skipped, 0 failed（exit 0）；仓库内 basetemp 测后已清理，git 状态干净(bdd-09-dual-position.log, bdd-09-pytest-inrepo.log)
- PASS BDD-10: 平台无关原则不破坏（回归拦截）——check-platform-assumptions.py exit 0（R1-R5 0 命中）；test_bdd_7（GIT_CEILING_DIRECTORIES env 注入）/ test_bdd_25（Path.relative_to + as_posix 位置感知排除注入）修改点 diff 人工核对无裸 PATH=/裸 python3/POSIX symlink 硬假设//tmp 字面量(bdd-10-platform.log)

**Summary**: 10/10 PASS, 0 FAIL —— BDD-1..10 全部实跑通过；无 UI 证据需求（domains=[backend]，P1 §9 声明）；本任务须走 P6.5 judge 复核（.state.yaml 已写 judge.enabled: true）。
