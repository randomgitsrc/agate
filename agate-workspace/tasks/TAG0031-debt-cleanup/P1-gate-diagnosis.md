---
phase: P1
date: 2026-09-04
trigger: review_needs_revision
---
# P1 Gate 诊断（第 1 轮 review 后）

- review 结果：status needs-revision（requirements-review，agent≠main，P1-review.md）
- 失败项：BDD-14（同类扫描第 3 小节口径）, DEBT 登记闭合覆盖（DEBT0002/3/4/16/17/18 六条）

## 诊断

主 Agent 已亲自复核 review 提出的两处，均确认成立（非 review 误判）：

1. **同类扫描第 3 小节口径失真**：正文给出的原始 grep 命令 `grep -n "dirname(dirname\|dirname(os.path.dirname" agate/scripts/*.py` 主 Agent 实测命中 14 行，但正文只讨论了其中 3 行（`check-gate.py:986` 本体 + `check-retrospective.py:74`/`agate-render-dispatch-prompt.py:191` 两处同类），未说明其余约 9 处（以 `__file__`/`script_path` 为推导起点）为何不纳入同类判定。review 给出两条修复路径：① 换更精确的 grep（追加 `task_dir` 关键词过滤）让命中数与展示命令逐字节对应；② 保留宽口径命令但显式写出筛选依据（按推导起点 `task_dir` vs `__file__` 分两类，说明为何仅前者构成同类）。
2. **DEBT 登记闭合覆盖缺口**：14 条 BDD 中仅 BDD-7 一条要求把 debt 条目 status 改为 closed（且仅针对 DEBT0007），DEBT0002/0003/0004/0016/0017/0018 六条只验收"代码修复本身"，没有任何 BDD 要求这六条登记条目的 status 字段被改写。任务标题是"批量关闭 7 条历史遗留 open 技术债"，当前需求基线实际只保证 1 条会被登记关闭。

## 路由

两处均是 P1 需求基线本身的缺口，不涉及 P0-brief 范围问题（P0-brief scope 本身没错，是 P1 analyst 转 BDD 时遗漏），退回 analyst 修改 P1-requirements.md：

- BDD-14 / 同类扫描第 3 小节：按 review 给出的两条路径之一修正（任选，需保证复现同一 grep 命令能得到与正文一致的结论）
- 新增/扩展 BDD：为 DEBT0002/0003/0004/0016/0017/0018 六条补齐登记闭合验收条件（可仿 BDD-7 单条覆盖多个 debt id，也可扩展 BDD-7 本身），比照 DEBT0005/DEBT0006 先例的登记格式

## 不需要修改的部分（避免 analyst 无谓返工）

review 已确认通过、无需改动：BDD-1~5、BDD-6（仅措辞建议，非阻塞）、BDD-7~13、P0_STALE 判定（DEBT0007 轻微漂移分类维持）、frontmatter 声明（domains/packages/risk_level/phases）、裁剪说明、同类扫描小节 1/2/4/5/6/7。
