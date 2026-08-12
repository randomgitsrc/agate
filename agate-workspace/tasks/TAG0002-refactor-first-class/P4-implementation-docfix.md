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

# TAG0002 — P4 文档同步修复轮（复审 needs-revision 残留项）

> 本轮为 P4 review 复审轮（needs-revision）的最小文档修复：代码层 BLOCKER 已闭环（change_type frontmatter-only 实测三层验证 + 654/654 全绿），仅残留 2 处文档描述与落地代码矛盾（P4-review.md §6）。只改 2 处文档，未改动代码/测试。

## 1. 修复对象与依据

- 修复依据：P4-review.md §6「文档一致性 —— 1 个残留项」+ dispatch-context 派发指引（强制指令）。
- 代码对照：`agate/scripts/agate-md-field-get.py` 实际行为——
  - L78 `NO_FALLBACK_STRING_FIELDS = frozenset({"change_type"})`
  - L107-108 change_type 不在 `STRING_FIELDS`（注释明确"走 NO_FALLBACK_STRING_FIELDS"）
  - L164-180 `_regex_fallback` 无 change_type 分支
  - L188-190 `_get` no-fallback 集合并入判定，frontmatter 无该字段直接 `return ""`
  - L72-77 模块注释明确"frontmatter-only，无正文回退"及 BDD-2 理由

## 2. 改动（2 处文档）

1. **`P2-design.md` §3.1 机器通道 L122**：
   - 旧：`新增 change_type op（STRING_FIELDS，读 frontmatter；可选正文正则回退 change_type:\s*(\S+)，与 risk_level 同模式）`
   - 新：`新增 change_type op（NO_FALLBACK_STRING_FIELDS，frontmatter-only，无正文回退——change_type 是新增 P1 机器字段，正文旧格式从未有该字段，无向后兼容需求；正文散文提及 change_type 不得误判为 refactor（BDD-2））`

2. **`P4-implementation.md` §1.1 改动清单 L24**：
   - 旧：`新增 change_type（STRING_FIELDS + 正文正则回退，与 risk_level 同模式）`
   - 新：`新增 change_type（NO_FALLBACK_STRING_FIELDS，frontmatter-only，无正文回退——P4-review §2.1 BLOCKER 修复）`

## 3. 自检

- grep 确认 P2-design.md / P4-implementation.md 已无"change_type + 正文正则回退 / STRING_FIELDS"描述残留；其余匹配项均在 review / dispatch-context / fix-record / progress 等引用性文档中（引述旧文案作上下文，非残留描述）。
- 未改动代码、测试、其他文件。

## 4. 环境隔离

[PROD_NOT_TOUCHED] 仅改动 worktree `docs/tasks/TAG0002-refactor-first-class/` 下 2 个文档 + 1 个实现记录；未触碰 `~/.agate`（稳定版 v0.40.2）与生产环境。
