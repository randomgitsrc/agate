---
phase: P4
task_id: TAG0027
type: implementation
parent: P2-design.md
trace_id: TAG0027-P4-20260902
status: draft
created: 2026-09-02
agent: orchestrator（主 Agent 汇总，implementer 分批执行）
implementation_dir: agate/
---

# TAG0027 P4 实现汇总 — 编排语义统一落地（RM-AG0054）

> 实现按 P2-design.md §8 dispatch_plan 拆 4 批执行（B1 core-rules-cli / B2 render-audit /
> B3a docs-clean / B3b guardrail-scripts），各批 implementer 完成 + 分批 commit。
> 本文件为主 Agent 综合各批 P4-progress.md 的实现汇总，供 P4 review（C8: backend + high →
> review 角色）评审。

## implementation_dir

`agate/`（协议本体 worktree：`/home/kity/oclab/agateon/.worktrees/agate-TAG0027/agate/`）

## 批次实现摘要

### B1 core-rules-cli（commit 57e5f1c）
- `agate/rules/phases.yaml`：主线 P0-P8 每条目加 `next`/`retreat` 键；P8 `next: null`（无自动
  后继）；P6 `next: P7`（条件式，A1 裁决）；P5/P6 `retreat: P4`；P6.5 条目加 `gate_subphase`
  （hosted_on: P6 / forward_to: P7 / needs_revision_to: P6），**不写 next/retreat**（非独立
  phase 口径）
- `agate/rules/schema/phases.schema.json`：声明 next/retreat/gate_subphase 键 + 值域（phaseId
  不含 P6.5 + null；additionalProperties:false 兼容）
- `agate/scripts/agate-next.py`（新建）：推进 CLI——消费 check-gate exit 三态：exit 0 → 按
  phases.yaml next 更新 .state.yaml phase（只 add 不 commit）；exit 1 → 委托 agate-retreat-to.py
  （retreat 表值存在即委托，不预判 diff）；exit 2 非 P6 → 落盘 {phase}-exit2-resolution.md
  （不推进）；P6 特例（A1）→ gate_p65 exit 0 后直推 P7（judge.enabled 分支）
- `agate/scripts/agate-advance.py`（新建）：--to 委托 retreat-to 逐阶；人工直跳 diff≥2 → 提示
  PAUSED
- `agate/scripts/check-judge-verdict.py`：verdict 复核加 exit2-resolution 检查（有 exit:2 事件
  无 resolution 文件 → 校验失败）；_strip_card 加 CARD-SOURCE 双锚点
- `agate/loop-orchestration.md`：档位 C 自动推进改走 agate next（文档约定 + CLI 调用点双层）
- B1 批测试 21 用例全绿（含 3 例夹具修复：真实 gate exit 场景构造——P5 baseline+fail-list
  造 exit 1、P3-test-cases.md 造 exit 2、P7 干净场景造 exit 0）

### B2 render-audit（commit 57e5f1c）
- `agate/scripts/agate-dispatch.py`（新建）：单命令渲染时注入——读 dispatch-context.md 模板 +
  子进程调 agate-next-card.py 取卡片 + 写 {phase}-dispatch-context-{role}.md；CARD-SOURCE 标记
  放 AGATE_CARD_START **之前（块外）**（A2 定案 (a)，不进 _extract_card 区间 → 2p hash 兼容）
- `agate/assets/templates/dispatch-context.md`：加 CARD-SOURCE 渲染来源说明 + 占位符注释
- `agate/scripts/check-p6-provenance.py`：审计 2 剥离锚点改**双锚点**（CARD-SOURCE 行起物理块
  优先 + AGATE_CARD_START..END 物理块兜底），扫描对象面不变
- B2 批测试 9 用例全绿

### B3a docs-clean（commit 15505bf）
- 8 文件平台名三分类处理：role-system.md（3 注记 + 语义去平台化）/ adr.md（ADR-008 决策叙事
  3 注记）/ dispatch-protocol.md（铁律 1 去平台化 + 4 段注记 + 7 处 task 改派发工具，五模式
  锚点未动）/ UPGRADING.md（4 版本节注记）/ WORKFLOW.md（4 段注记 + 已知适用环境表整表豁免 +
  S1S2 锚点未动）/ assets architect.md + custom-role.md（平台适配注记）
- AGENTS.md:30 判定元信息豁免（指向 platform-notes.md 豁免源，不在 CHECK 14 扫描面）零改动
- 全协议平台名存量清零（0 处未覆盖命中）

### B3b guardrail-scripts（待 commit，当前被 P4 gate 拦截——先评审后 commit）
- `agate/WORKFLOW.md`：S1S2-ANCHOR 总览表加 next/retreat 4/5 列（7 列结构，评审角色/门槛顺延；
  P0-P8+P6.5 按 phases.yaml 填值，READY 留空）
- `agate/scripts/check-structure-consistency.py`：_parse_workflow_rows 5 元组 +
  _check_s1 增 next/retreat 比对 + P6.5 gate_subphase 形态检查（_norm_transfer_cell 归一）
- `agate/scripts/check-protocol-consistency.py`：新增 CHECK 14（md 段落平台名扫描：切段/围栏
  跳过/注记行豁免/整文件+表行豁免结构）+ CHECK 15（数据面词边界 + 豁免词典机械生成）
- B3 补漏（CHECK 14/15 首跑 0 ERROR）：dispatch.yaml law-1 去 task / loop-orchestration.md:205
  平台前提改写 + 注记 / dispatch-protocol.md:234 task 字段名语境挂注记
- 3 测试注释 /tmp 字面量 R4 命中修复（test_check_platform_assumptions 回归）
- B3b 批测试 9 用例全绿；CHECK 14/15 首跑 0 ERROR

## 验证状态（P4 自查）

- 全量 pytest：1376 passed + 2 skipped（本批后），无回归
- check-protocol-consistency.py --strict-errors-only：0 ERROR（worktree 脚本）
- check-structure-consistency.py：S1-S6+S0 全 OK exit 0
- CHECK 14/15 首跑：0 ERROR（B3a 存量清零 + B3 补漏后）
- check-platform-assumptions.py：0 命中（R4 注释修复后）
- ruff：新改动 clean

## DESIGN_GAP / SCOPE+ 处理记录

- [DESIGN_GAP] B1 三用例与真实 check-gate exit 语义矛盾（2026-09-02）：P5 夹具恒 exit 2、
  P3 夹具恒 exit 1——非实现缺陷，P3 测试夹具无法构造真实 gate exit 场景 → 已由 test-designer
  夹具修复轮闭环（补 P5 baseline+fail-list 造 exit 1、P3-test-cases.md 造 exit 2、P7 干净场景
  造 exit 0），BDD-7/8/11 语义不变
- [SCOPE+] B3b CHECK 14/15 首跑 3 ERROR 补清（2026-09-03）：dispatch.yaml law-1 task /
  loop-orchestration.md:205 OpenCode 前提 / dispatch-protocol.md:234 task 字段引用——B3a/B1
  清理漏网 → 已由 B3 补漏 agent 闭环（law-1 去 task / 平台前提注记 / 字段名语境注记），
  CHECK 14/15 首跑 0 ERROR
- [DESIGN_GAP 候选] P3 测试注释 "/tmp 字面量" 触发 check-platform-assumptions R4（3 文件）——
  注释措辞误触扫描规则 → 已修复（措辞改为"临时目录字面量（用 tmp_path）"）

无遗留未决 DESIGN_GAP / SCOPE_GAP / CLARIFY。
