# TAG0006 交接单 — agate UI/UX 验收质量机制

> 本交接单供 worktree session 的 agent 按此启动 TAG0006 任务。
> 任务已 P0 立项（.state.yaml phase=P0，P0-brief.md 已就绪）。
> worktree 已完成构建安装与基线验证，可直接开始 P1。

---

## 1. 你要做什么

**TAG0006**：agate UI/UX 验收质量机制。

**一句话**：解决"agate 保证工程质量但不保证 UX 质量"（qtcalc 实证）——给 `ui_affected` 任务补 UX 需求基线（P1）+ UI 设计产物（P2）+ 视觉评审维度（P2）+ 视觉验收（P6，vision 能力三态）。

## 2. 工作区布局（双工作区纪律，违反必出事故）

| 路径 | 角色 | 纪律 |
|------|------|------|
| `/home/kity/oclab/agate/.worktrees/agate-TAG0006` | **本任务 worktree（改造对象）** | 在这里改代码、写阶段产出、跑测试、git commit |
| `/home/kity/oclab/agate`（主 checkout） | 协议本体 + 任务数据 + `~/.agate` 指向 | **禁止改动**。稳定版来源 + hook 的 AGATE_ROOT |
| `~/.agate`（软链 → 主 checkout/agate） | **稳定版（开发工具）** | **禁止改动**。跑 gate / 读卡片用它 |

**核心原则（AGENTS.md T001 约定沿用）**：
- **跑 gate 用 `~/.agate`**（稳定版），**改代码/跑测试在 worktree**。
- commit hook 用 `~/.agate/scripts/pre-commit-gate.sh` 判定（gate 工具稳定，改造对象变化）。
- **⚠️ gate 工具 ≠ 检查对象**：`check-protocol-consistency.py` **必须用 worktree 自己的**（检查 worktree 里的协议文件）；`~/.agate` 的脚本在 worktree 跑显示主 checkout 上下文。
- **hook 在共享 git 目录**：worktree 的 `.git` 是文件，hook 在主 checkout 的 `.git/hooks/`。

**已完成的 setup**：
- 依赖齐全：python3 / pyyaml / pytest（python3 -m pytest）
- 基线验证：全量 pytest **823 passed** + consistency **0 ERROR**
- hook 就位 + orchestrator 注册（软链）+ 工作区解析指向 worktree 自己

## 3. 任务范围（P0-brief 已锁定，P1 细化 BDD）

### 已确认的缺陷/需求（有代码证据，见 P0-brief）

**RM-AG0007（核心：UX 质量机制缺失）**：
- qtcalc 实证：走 agate 的 qtcalc 架构/测试/治理领先，但表达式次显示/键盘输入/UI 样式三项 UX 反而不如没走的 qtcalc-basic
- 根因：`ui_affected` 只触发 E2E 功能测试（state-machine.md:89-94），不要求视觉/交互质量；P2 plan-design-review 审架构不审视觉稿；P6 视觉验收看"渲染成功"无美观/易用维度；全部 gate 是 exit code 无用户主观体验验收
- 修复方向：①P1/P2 加 UX 需求基线（键盘/显示/样式写成 BDD 可测项 + 视觉验收项）②frontend 任务 plan-design-review 增视觉/交互维度 ③P6 对 UI 任务强制双证据 + 视觉质量 checklist

**RM-AG0004（视觉验收能力边界，2026-08-17 已修正：能力识别不写死）**：
- 视觉验收能力**运行时探测，不写死具体工具**——项目可能有 vision-engine/多模态模型/其他视觉能力，也可能没有
- 修复：①`ui_affected` 任务 P1 **capability_requirements 必须声明 vision 能力三态**：available（真实视觉验收）/ supplementable（可注入 skill→派发指引注入）/ GAP（降级：双证据 + 像素 + 人工复核）②available 时 P6 真实视觉分析（本机 vision-engine 可用，别的项目可换）③**subagent 能力自查**（派发时要求 subagent 先自查能否调 vision，不能就报告不静默假设）④输入态变化类用例人工复核 ⑤雷同截图降级待复核
- 能力传递机制见 RM-0014（supplementable 扩展，TAG0012 实施）——本任务引用

**RM-AG0006（GUI 自动化框架评估）**：
- Windows 环境无 Playwright 等 GUI 框架，UI e2e 用 QTest offscreen 信号级模拟 + 截图
- P2 设计时评估 WinAppDriver/AutoIt 是否补真实 GUI 交互路径，**可能产出"保持现状"结论**（技术选型调研，非纯实现）

### 已定的关键设计决策（2026-08-17 讨论）

**UI 设计产物**（你问的"DESIGN.md"）：
- **并入 P2-design.md 的独立节**（`ui_affected: true` 时 P2 必须含"UI 设计"节）——不新增文件
- **architect 兼任**（复用现有角色，不新造 designer）
- 节内容规格（布局/交互/视觉 checklist）由 P2 architect 设计——这是 P2 的活，P1 不空想
- 视觉验收时 P6 verifier 以 UI 设计节为依据

### 核心约束（不可违反）
1. **Linux 现状是基线**——现有 823 pytest 全绿是回归底线
2. **Windows 兼容是增量**——本环境无真实 Windows GUI，RM-0006 基于调研非实测，**不要宣称"已实测 Windows"**
3. **不写死视觉能力工具**——vision-engine 只是本机例子，靠 capability_requirements 三态识别
4. **范围锁定**——若 P1 分析发现需改动超出 P0-brief 锁定范围，先停下跟用户确认

## 4. 关键验证命令

```bash
# 在 worktree 根执行：

# 全量测试（必须全绿才算过）
python3 -m pytest agate/tests/

# 一致性（0 ERROR 才行；--strict 让 WARNING 也阻断）
# ⚠️ 必须用 worktree 自己的脚本
python3 agate/scripts/check-protocol-consistency.py --strict

# shellcheck（3 hook 薄壳）
shellcheck -S warning agate/scripts/*.sh

# 测试计数（验证文档没漂移）
bash agate/tests/scripts/count-tests.sh

# 单脚本测试（改哪个跑哪个，TDD 先红后绿）
python3 -m pytest agate/tests/unit/test_check_gate.py
python3 -m pytest agate/tests/unit/test_check_p6_evidence.py
```

## 5. 阶段推进纪律（T001 血泪教训）

- **commit 时 phase = 本 commit 产出阶段**：P1 产出 → phase=P1 再 commit；推进 P2 随 P2 产出同 commit。不要先写 phase=P2 再 commit P1 产出
- **改脚本走 TDD**：先写失败测试确认红 → 改脚本确认绿
- **git 命令加 timeout**、单步串行
- **commit message 含 `wf({Txxx}-P{阶段}):`** 前缀
- **改 `agate/*.md`、`agate/scripts/*.py/.sh`、`agate/phase-cards/*` 触发 SELF-GATE**：commit message 需含 `self-gate-review:` 或 `self-gate-skip:`
- **只 add 本 task 文件**：不用 `git add -A`
- **切分支前确认干净**：`git status` 空才切

## 6. 任务编号与状态

- 任务目录：`agate-workspace/tasks/TAG0006-ui-ux-quality/`（在 worktree 里）
- `.state.yaml`：phase=P0（P1 开始后推进）
- active-tasks.md「待开始」已有 TAG0006 行
- roadmap：RM-AG0004 / RM-AG0006 / RM-AG0007 关联本任务（scheduled）
- **编号体系**：任务用 `{Txxx}`（项目代号 + 动态数字，v2.0 起的 Jira 式编号）。校验器 `^T[A-Z]{2}\d+$`

## 7. 已知风险与止损

- **UX 质量机制跨 P1/P2/P6 三阶段**——改动面大（analyst/architect/verifier 角色 + phase-cards + state-machine），P1 拆 BDD 时按阶段组织。止损：按 RM-0007 的三层（基线/评审/验收）分节
- **视觉验收依赖项目声明的视觉能力**——本机 vision-engine available（P1 能力识别确认），但 subagent 能否调用需自查。止损：dispatch-context 要求 subagent 先自查能力，不能就报告降级
- **RM-0006 是技术选型调研**——可能产出"建议保持现状"结论，非纯实现。止损：P2 先出评估结论再定方向
- **同类扫描强制**——P1/P2 必须梳理"UX 机制影响面"：ui_affected/plan-design-review/vision-analyst 在 64 处文件被消费，改一处须同步所有联动点（state-machine 转移条件、verifier 角色、vision-analyst 角色、P2 卡片 C8 表）。用户明确：不愿意一轮一轮来回改
- **改动触发 SELF-GATE**——涉及 phase-cards/*.md + assets/execution-roles/*.md + state-machine.md，commit 带 self-gate-review

## 8. 完成后

- P8 gate + READY → 提 PR 合并 main（PR 普通 merge 非 squash，tag 要求）
- 合并前看 PR CI 结果（matrix 双平台）——pytest/shellcheck/consistency/gate-backstop 全绿
- roadmap 回写 RM-AG0004/0006/0007 → done
- 复盘按 agate 自身变更流程归档（合并后在主 checkout 写复盘 + 更新 roadmap/版本）

## 9. 交接确认

- worktree 基线全绿：823 pytest + consistency 0 ERROR（--strict）
- hooks 就位、orchestrator 已注册、依赖齐全
- 任务数据就绪：TAG0006 P0-brief（vision 能力修正版）+ .state.yaml phase=P0
- 交接单位置：`HANDOFF-TAG0006.md`（worktree 根，已 commit）
