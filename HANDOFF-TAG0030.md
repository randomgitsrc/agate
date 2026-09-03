# TAG0030 交接单 — 验收盲区机制批（RM-AG0057 + DEBT0024/0025/0026）

> 本交接单供 worktree session 的 agent 按此启动 TAG0030 任务。
> 任务已 P0 立项（.state.yaml phase=P0，P0-brief.md 已就绪）。
> worktree 已完成构建安装与基线验证，可直接开始 P1。

---

## 1. 你要做什么

**TAG0030**：验收盲区机制批。

**一句话**：补强 agate 协议验收盲区——测试副作用/环境还原 gate + P1 人工体验路径验收节 + plan-design-review 形态驱动化 + 视觉契约断言 + TAG0027 复盘三连（真实 gate 夹具/新 CHECK 先全量扫描/大任务拆小）。

## 2. 工作区布局（双工作区纪律，违反必出事故）

| 路径 | 角色 | 纪律 |
|------|------|------|
| `/home/kity/oclab/agateon/.worktrees/agate-TAG0030` | **本任务 worktree（改造对象）** | 在这里改代码、写阶段产出、跑测试、git commit |
| `/home/kity/oclab/agateon`（主 checkout） | 协议本体 + 任务数据 + `~/.agate` 指向 | **禁止改动**。它是稳定版来源，也是 hook 的 AGATE_ROOT |
| `~/.agate`（软链 → 主 checkout/agate） | **稳定版（开发工具）** | **禁止改动**。跑 gate / 读卡片用它 |

**核心原则（AGENTS.md T001 约定沿用）**：
- **跑 gate 用 `~/.agate`**（稳定版），**改代码/跑测试在 worktree**。
- commit 时 pre-commit hook 用 `~/.agate/scripts/pre-commit-gate.sh` 判定。
- **⚠️ gate 工具 ≠ 检查对象**：`check-protocol-consistency.py` **必须用 worktree 自己的**；编排/派发类工具用 `~/.agate/scripts/` 稳定版（TAG0016 教训）。
- **hook 在共享 git 目录**：worktree commit 时 hook 自动触发。

**已完成的 setup**：
- 依赖齐全（bash/python3.12/pyyaml/pytest/shellcheck/ruff）
- 基线验证：consistency 0 ERROR（--strict-errors-only）
- orchestrator 注册：`.opencode/` + `.claude/` 软链 → `~/.agate/orchestrator-template.md`
- 工作区解析：`agate_common.py` 输出 worktree 自己的 agate-workspace（须在 worktree 目录内执行）
- 任务数据：TAG0030 P0-brief + .state.yaml phase=P0

## 3. 任务范围（P0-brief 已锁定，P1 细化 BDD）

### 已核实并确认的缺陷/需求（全部有代码/实测证据，见 P0-brief + RM-AG0057 + DEBT 条目）

**RM-AG0057-①（测试副作用/环境还原 gate）**：协议 P3 卡只有测试前失败基线 `agate-capture-env-baseline.py`（capture-env-baseline 是测试前失败列表，供 P5 机械 diff——不是测试后残留检查），P6 只讲环境准备职责边界；无"创建型测试清理钩子/afterEach 清理队列"协议要求。peekview DEBT0008 实证：18 个残留团队污染 debug DB。

**RM-AG0057-②（P1 人工体验路径验收节）**：P1 卡无"验收数据 vs 用户数据（seed）分离"或"Given seed → 页面有内容"类 BDD 要求。peekview DEBT0009 实证：make debug-seed 后 Teams tab 空。

**RM-AG0057-③（plan-design-review 形态驱动化）**：形态机制已在 P1 analyst（`ui_render_shape`：layout/render_component/temporal_effects + `ui_ux_dimensions`）/ P2 architect（UI 设计节：渲染形态声明 + 维度选择 + 按形态 checklist）/ gate（`_gate_p1_ui_shape`）全链落地——但 `plan-design-review.md` 是固定 7 维评分（布局一致性/颜色/字体/组件）+ 一行条件启用，无"按受评形态加载维度组"机制。布局方案 ≥2 候选不下沉 UI 层（P2 candidate_count 只约束架构级）。

**RM-AG0057-④（视觉契约断言）**：vision-analyst 是被动截图翻译（有文字溢出/dropdown 状态描述），协议无"视觉契约断言"（可量化 DOM 度量）概念。

**DEBT0024/0025/0026（TAG0027 复盘三连）**：P3 测试夹具走 mock 假 gate exit（应走真实 gate 语义）；新 CHECK 上线前未先全量扫描存量（CHECK 14/15 首跑 3 ERROR）；单 agent 大任务（>5 文件）上下文耗尽（拆小后稳定）。

### 核心约束（不可违反）
1. **Linux 现状是基线**——全量 pytest 全绿是回归底线
2. **不破坏已有协议语义**——plan-design-review 保持 0-10 评分输出格式（门槛读 status 字段），只加形态分组内部逻辑；P1/P2 形态声明机制（已有）不重构
3. **卡文件批量改动用 grep 断言审计 TDD 策略**（TAG0027 批量 TDD 教训）——不为每处小改动单独 TDD，先写断言审计再批量改
4. **视觉契约是"可表达子集"**——只收可量化 DOM 度量（宽度/高度/对齐/重叠/溢出），不收主观视觉，避免误解
5. **DEBT0026 与 TAG0028 自主再派发边界**——本任务只补派发模板默认指导，不重复实现内部自主拆
6. **范围锁定**——若 P1 分析发现需改动超出 P0-brief 锁定范围，须先停下跟用户确认

## 4. 关键验证命令

```bash
# 在 worktree 根执行：

# 全量测试（必须全绿才算过；分片 + -n auto 并行提速）
python3 -m pytest agate/tests/unit/ -n auto
python3 -m pytest agate/tests/regression/ -n auto
python3 -m pytest agate/tests/integration/ -n auto

# 一致性（0 ERROR 才行；必须用 worktree 自己的脚本）
python3 agate/scripts/check-protocol-consistency.py --strict-errors-only

# shellcheck
shellcheck -S warning agate/scripts/*.sh

# 测试计数（验证文档没漂移）
bash agate/tests/scripts/count-tests.sh

# 单脚本测试（改哪个跑哪个，TDD 先红后绿）
python3 -m pytest agate/tests/unit/test_{具体测试文件}.py
```

## 5. 阶段推进纪律（T001 血泪教训）

- **commit 时 phase = 本 commit 产出阶段**：P1 产出 → phase=P1 再 commit；推进 P2 随 P2 产出同 commit。**不要**先写 phase=P2 再 commit P1 产出
- **改脚本走 TDD**：先写失败测试确认红 → 改脚本确认绿
- **批量机械改动（卡/模板）的 TDD 策略**：先写"grep 断言审计"测试作为回归拦截；批量改动后跑该断言 + 全量 pytest 确认绿
- **git 命令加 timeout**、单步串行（AGENTS.md 工具纪律）
- **commit message 含 `wf(TAG0030-P{阶段}):`** 前缀
- **改 `agate/phase-cards/*.md` + `agate/assets/review-roles/plan-design-review.md` + `agate/assets/templates/dispatch-context.md` + `agate/assets/execution-roles/analyst.md` 触发 SELF-GATE**：commit message 需含 `self-gate-review:` 或 `self-gate-skip:`。协议文档变更需跑 `check-protocol-consistency.py` 确认无 ERROR

## 6. 任务编号与状态

- 任务目录：`agate-workspace/tasks/TAG0030-acceptance-blindspot/`（在 worktree 里）
- `.state.yaml`：phase=P0（P1 开始后推进）
- active-tasks.md「待开始」已有 TAG0030 行（⬜ P0）
- roadmap：RM-AG0057 关联本任务（scheduled，2026-09-03 立项）
- **编号体系**：任务用 `TAG0030`。校验器 `^T[A-Z]{2}\d+$`
- **并行提示**：TAG0029（gate 解析器）/ TAG0031（DEBT 存量）与本路并行，三路文件域不重叠——roadmap/active-tasks/debt 登记行是共享面，只改自己关联的行，不整表重排

## 7. 已知风险与止损

- **卡文件批量改动回归面广**（P1/P3/P6 卡 + 评审角色 + 模板同批改）：触发多轮 consistency/pytest → 止损：grep 断言审计单测锁定新增要求（TAG0027 批量 TDD 策略）
- **形态驱动化是评审角色行为变更**：保持 0-10 评分输出 + status 字段格式（门槛读取），只加形态分组内部逻辑；无形态声明时回落布局型默认 → 止损：跑一致性 + 相关单测确认既有评审产出格式不破
- **视觉契约概念新增易误解**："可表达子集"边界要写清 → 止损：文档明确只收可量化 DOM 度量，P2/P6 指南避免"所有视觉都必须断言"误解
- **DEBT0026 与 TAG0028 §4 边界**：只补派发模板默认指导，不重复实现 → 止损：先读 TAG0028 交付的 dispatch-protocol 改动，确认剩余缺口再写

## 8. 完成后

- P8 gate + READY → 提 PR 合并 main（PR 普通 merge 非 squash，tag 要求）
- **合并前在 PR 里看 CI 结果**——pytest/shellcheck/consistency/gate-backstop 全绿才算过
- **merge 模式：本任务 PR 完成后由主 Agent 综合 merge**（三路并行 TAG0029/30/31，不自行 git-to-main）
- roadmap 回写 RM-AG0057 → done；DEBT0024/25/26 登记关闭（closure_criteria 逐条核验）
- 复盘按 agate 自身变更流程归档（合并后在主 checkout 写复盘 + 更新 roadmap/版本）

## 9. 交接确认

- worktree 基线：consistency 0 ERROR（--strict-errors-only）已验
- hooks 就位（指向 `~/.agate` 稳定版）、orchestrator 已注册（双平台）、依赖齐全
- 任务数据就绪：TAG0030 P0-brief + .state.yaml phase=P0
- 交接单位置：`HANDOFF-TAG0030.md`（worktree 根，已 commit）
