# tech-debt 登记簿

> 协议/项目技术债登记。每条 DEBT = 一个 ` ```yaml ` fenced block（机器校验）+ 可选正文。
> 机器校验：`python3 {agate_root}/scripts/check-debt.py {AGATE_WORKSPACE}/debt/tech-debt.md`
> 登记判据（三分法）：① 不修它验收声明变假 → 登记；② 不修但未来变更更贵/更危险 → 登记；③ 都不影响 → 不登记（合法出口）。

## DEBT0001

```yaml
id: DEBT0001
category: technical
title: 文档脚本名引用漂移无 gate 兜底（裸脚本名不被 CHECK 2 捕获）
status: closed
priority: high
evidence:
  - ref: agate-workspace/roadmap/roadmap.md
    note: RM-AG0015（backlog，2026-08-15 立案）
  - ref: docs/reviews/retrospective-tag0010-0011-docs-20260815.md
    note: TAG0010/0011 复盘 §3.1——phase-cards 26 处过时 .sh 引用无 gate 兜住
  - ref: agate/scripts/check-protocol-consistency.py
    note: CHECK 2 REF_RE（L238）只匹配 docs/assets/scripts 前缀引用，裸脚本名（phase-cards/rules 全是）完全漏检（实测验证）
  - ref: agate-workspace/tasks/TAG0013-script-consistency/P6-evidence/bdd-1.log
    note: CHECK 10 落地后 0 ERROR（closure_criteria 1 满足）
  - ref: agate-workspace/tasks/TAG0013-script-consistency/P6-evidence/bdd-2.log
    note: 假协议树 check-nonexistent-script.py → ERROR + exit 1（closure_criteria 2 满足）
  - ref: agate-workspace/tasks/TAG0013-script-consistency/P6-evidence/bdd-4.log
    note: PROTOCOL_DIRS 含 phase-cards/rules，CHECK 2/3 0 ERROR（closure_criteria 3 满足）
impact: 脚本删/改名后协议文档漂移，consistency 0 ERROR 照过（v0.46.0 的 26 处过时引用是实锤）；修复后无 gate 防复发，未来破坏性变更再次漂移无拦截
recommendation: 新增 CHECK 10——扫描协议文件脚本名引用（裸名+相对路径）对照 agate/scripts/ 实际文件，漂移报 ERROR；豁免 UPGRADING 对照表/formatters/3 hook 薄壳/count-tests.sh；phase-cards/rules 入 PROTOCOL_DIRS
closure_criteria:
  - check-protocol-consistency.py 新增 CHECK 10 且通过率 0 ERROR
  - 协议文档引用已删脚本名 → 报 ERROR（测试锁定）
  - phase-cards/rules 入 PROTOCOL_DIRS（引用检查升级为严格）
source: retrospective
created_at: 2026-08-15
task_id: TAG0013-script-consistency
closed_at: 2026-08-16
```
