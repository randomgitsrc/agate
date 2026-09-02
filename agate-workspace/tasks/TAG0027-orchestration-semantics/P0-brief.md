# P0-brief — TAG0027 编排语义统一落地（RM-AG0054）

> 本文件由主 Agent 亲自填写（P0 阶段产出）。设计文档：`docs/design-notes/design-orchestration-semantics.md`
> （v3b，2026-09-02 三轮独立评审闭环：v1 FAIL→v2 Claude FAIL→v3 落盘复审 PASS→第三轮 Claude 元评审
> 时间线核验不成立；评审链文档见 `docs/reviews/review-orchestration-semantics-*-20260902.md`）。

## task

"在 agate 协议层落地编排语义统一设计（RM-AG0054）：**推进侧状态机 CLI**（`agate next` /
`agate advance`）——推进决策从 orchestrator 临场判断改为查表推进，复用既有资产
（`check-state-transition.py` 校验 + `check-gate.py` exit 三态 + `rules/phases.yaml` 扩展 +
`agate-retreat-to.py` 回退侧对接），CLI 定位为 `/loop` 档位 C 的**可观测层**（档位 C 自动推进
强制走 `agate next`，消除模型自律环节）。"

### scope

- **Phase 1（转移表结构化）**：`rules/phases.yaml` 增 `next`/`retreat` 字段（或扩展
  `rules/state-transitions.md` 数据面），对齐 `state-machine.md` 既有转移语义
  （P5/P6→P4、P6.5→P6、diff≥2→PAUSED）；新增字段纳入既有 S-1/S-2 双向一致性 gate
  （`check-structure-consistency.py`，md 侧锚点为 WORKFLOW.md 阶段总览表）
- **Phase 2（推进侧 CLI）**：新增 `agate next` / `agate advance`，消费 `check-state-transition.py`
  跳变校验 + `check-gate.py` exit 三态（0 直推 / 1 回退 / 2 暂停转主 Agent + exit 2 落盘
  `exit2-resolution` 机器可读产物）；与 `agate-retreat-to.py` 回退侧对接；`loop-orchestration.md`
  档位 C 自动推进改走 `agate next`；补 BDD"档位 C 全程用 agate next 推进，主 Agent 未自行
  判断进入下一 phase"
- **Phase 3（编排心智统一文档化）**：dispatch-protocol 五模式为唯一语义锚点，平台差异
  （workflow/ralph/goal）全部挂「实现注记」标记（4.3 结构性判据格式约定）；排查协议文档
  语义小节平台名污染
- **测试**：`agate/tests/` 新增 pytest 覆盖（转移表字段 schema 校验、CLI 推进/回退/exit 2
  分支、S-1/S-2 扩展、档位 C 对接），BDD 以 P1 定稿为准（计划 ≥10 条）

### out-of-scope

- **Phase 4（可选）**：渲染层（批次清单 → 各平台派发指令）+ 护栏 1 机械化
  （`check-protocol-consistency.py` 扫描"含平台名无实现注记标记段落"）——本次不做，随后续任务
- P6.5 judge 机制本身（已有，不动）；dispatch-protocol 五模式本身（只引用不重构）
- 平台食谱产品化（DSH workflow 脚本等，Phase 4 范畴）
- 新建独立一致性检查（按设计笔记想法 3，纳入既有 S-1/S-2，不新开）

## known_risks

- "同类/影响面预判（check-gate.py / check-state-transition.py 是核心 gate 消费方）：新增
  CLI 不改既有脚本返回约定（1/2），只新增消费方；`rules/phases.yaml` 增字段须过
  JSON Schema + S-1~S-6 一致性 gate，字段命名与既有 task_fields/gates 结构兼容，全量
  pytest + consistency 0 ERROR 是硬门槛"
- "同类/影响面预判（档位 C 对接 loop-orchestration.md）：'档位 C 自动推进改走 agate next'
  是行为变更，须先确认档位 C 现状执行逻辑（主 Agent 逐轮读状态→执行单步），BDD 验证
  不破坏既有 /loop 手动/半自动档位"
- "转移表语义与 state-machine.md 漂移风险：next/retreat 字段值域以 state-machine.md 转移
  规则为唯一权威（P5/P6→P4、P6.5→P6、diff≥2→PAUSED、P6.5 非独立 phase 值），schema
  校验 + S-1/S-2 双向 gate 防漂移；P6 exit 2 → P6.5 前进特例须在转移表显式建模"
- "P6.5 非独立 phase 的口径（state-machine.md:74-78）：phases.yaml 已有 P6.5 条目
  （结构化声明产出/门槛、注释说明非独立 phase），新增 next/retreat 字段不得把它写成
  独立转移边，保持'挂载于 P6→P7 转移上的强门槛子阶段'"
- "exit 2 的模型残留点（设计笔记诚实边界）：转移表为 exit 2 定义'下一动作'字段并落盘
  exit2-resolution，但不假装消灭模型自判——CLI 在 exit 2 分支暂停转主 Agent 是设计意图
  而非缺陷"

## env_constraints

- 本任务改 `agate/scripts/*` + `agate/rules/*.yaml` + `agate/loop-orchestration.md` →
  **触发 SELF-GATE**，commit message 须含 `self-gate-review:` 或 `self-gate-skip:`
- 用系统 python（`/usr/bin/python3`）跑 pytest/pyyaml；ruff 用 `~/.venvs/agate-dev/bin/ruff`
- 基线验证用 `--strict-errors-only`（DEBT0012）；`agate-next-card.py` 等派发类工具用
  `~/.agate` 稳定版，不用 worktree 相对路径（TAG0016 教训）

## executor_env

- worktree：`.worktrees/agate-TAG0027`（分支 `feat/TAG0027-orchestration-semantics`），
  构建流程见 `docs/guides/worktree-dogfooding-guide.md`，交接单
  `HANDOFF-TAG0027.md` 按模板全 9 节填写
