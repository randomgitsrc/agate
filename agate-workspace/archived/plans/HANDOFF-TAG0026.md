# TAG0026 交接单 — 维护性反模式 gate（RM-AG0046）

> 本交接单供 worktree session 的 agent 按此启动 TAG0026 任务。
> 任务已 P0 立项（.state.yaml phase=P0，P0-brief.md 已就绪）。
> worktree 已完成构建安装与基线验证，可直接开始 P1。

---

## 1. 你要做什么

**TAG0026**：维护性反模式 gate（RM-AG0046，G0 优先，diff 驱动）。

**一句话**：在 agate 协议层落地维护性反模式 gate——新增 `agate/scripts/check-maintainability.py`
（god-file 跨越 + fuzzy-boundary 检测，复用 `agate-risk-score.py` 模式）+ `check-gate.py`
**P4 三重门槛挂载**（violation 登记 + 数量对齐 + P4 评审 approve）+ `known-violations-template.md`
模板 + P4/P6 phase card 自查提醒 + pytest 覆盖 13 条 BDD；只在 P4 挂载，不挂 P6。

## 2. 工作区布局（双工作区纪律，违反必出事故）

| 路径 | 角色 | 纪律 |
|------|------|------|
| `/home/kity/oclab/agateon/.worktrees/agate-TAG0026` | **本任务 worktree（改造对象）** | 在这里改代码、写阶段产出、跑测试、git commit |
| `/home/kity/oclab/agateon`（主 checkout） | 协议本体 + 任务数据 + `~/.agate` 指向 | **禁止改动**。它是稳定版来源，也是 hook 的 AGATE_ROOT |
| `~/.agate`（软链 → 主 checkout/agate） | **稳定版（开发工具）** | **禁止改动**。跑 gate / 读卡片用它 |

**核心原则（AGENTS.md T001 约定沿用）**：
- **跑 gate 用 `~/.agate`**（稳定版），**改代码/跑测试在 worktree**。
- commit 时 pre-commit hook 用 `~/.agate/scripts/pre-commit-gate.sh` 判定——gate 判定对象是
  worktree 里的产出文件，但 gate 工具本身是 `~/.agate`。这是有意的：改造期间工具稳定，改造对象变化。
- **⚠️ gate 工具 ≠ 检查对象（最容易搞混的点）**：
  - commit hook 的 gate **判定工具**用 `~/.agate`（稳定版）
  - 但 `check-protocol-consistency.py` **必须用 worktree 自己的**
    （`python3 agate/scripts/check-protocol-consistency.py`），因为检查对象是 **worktree 里的协议文件**
  - `python3 ~/.agate/scripts/agate-summary.py` 在 worktree 里跑会显示**主 checkout 的上下文**
    （版本/分支/HEAD 是稳定版的），不代表 worktree 状态——worktree 自己的状态用 `git log`/`git status` 看
  - **所有编排/派发类工具脚本**（`agate-inject-card.py` / `agate-render-dispatch-prompt.py` /
    `agate-next-card.py` 等）都用 `~/.agate/scripts/` 稳定版调用（TAG0016 教训）
- **hook 在共享 git 目录**：worktree 的 `.git` 是文件（指向主 checkout `.git`），hook 实际在
  主 checkout 的 `.git/hooks/`（pre-commit/commit-msg/pre-push 已软链安装）。worktree commit 时 hook 自动触发。

**已完成的 setup（worktree 已可独立使用）**：
- 依赖齐全：bash 5.2.21 / python 3.12.3（系统 `/usr/bin/python3`）/ pytest 9.0.3 / pyyaml /
  shellcheck / ruff（`~/.venvs/agate-dev/bin/ruff`）
- 基线验证：全量 pytest 全绿 + consistency 0 ERROR（--strict-errors-only；DEBT0012 教训：
  存量 300+ WARNING 下 --strict 会误导判 exit 2）
- commit hook：指向 `~/.agate`（稳定版），worktree commit 自动触发
- orchestrator 注册：`.opencode/agents/orchestrator.md` + `.claude/agents/orchestrator.md` →
  `~/.agate/orchestrator-template.md`（符号链接，不拷贝，双平台）
- 工作区解析：`agate_common.py` 输出 worktree 自己的 `agate-workspace/`
- 任务数据：TAG0026 P0-brief + .state.yaml phase=P0 在 worktree 的 `agate-workspace/tasks/`

## 3. 任务范围（P0-brief 已锁定，P1 细化 BDD）

### 已核实的任务需求（见 P0-brief known_risks + v3 计划）

**设计来源**：`docs/design-notes/rm-ag0046-maintainability-gate-plan.md`（v3，2026-08-30 独立评审
修复 5 项后定稿）；`docs/design-notes/design-maintainability-gate.md`（G0-G3 分级 + 决策 1/2/3）。

- **G0 两条**：god-file 跨越（`before < N and after >= N`，N 默认 1000 可配置）+ fuzzy-boundary
  （diff 新增行匹配 Python/TS 类型逃逸正则：`# type: ignore`/裸 `except:`/`any`/`as any`）
- **P4 gate 硬挂钩**（check-gate.py gate_p4 新增一步）：v3 三重门槛——
  ① `agate-workspace/tasks/{Txxx}/known-violations.md` 存在 ② 登记条目数 ≥ violations 数
  （`count_kf_entries`，`| N |` 行首格式）③ `P4-review.md` status:approved 且 agent ≠ main
- **P4/P6 phase card**：P4 自查清单项（不 gate 强制，真正的强制在 check-gate）+ P6 自查提醒（非阻断）
- **known-violations-template.md**：登记模板，含"P4 评审确认"列（不参与机械计数）
- **配置**：`agate-workspace/maintainability.yaml`（阈值/正则集，缺失用默认值；不用 `.agate/`）
- **测试**：`agate/tests/` 新增 pytest 覆盖 13 条 BDD（含移动代码假阳性 BDD-12、挂载阶段对齐 BDD-13）

### out-of-scope（不可越界）

- G1（DRY）/ G2（条件纠缠/薄抽象/顺序耦合）/ G3（纯品味）
- RM-AG0022 结构化层联动（语义进 `rules/*.yaml`）
- 新增第 8 道 provenance 审计
- 门户/可视化面板、跨行移动代码识别

### 核心约束（不可违反）

1. **Linux 现状是基线**——现有全量 pytest 全绿是回归底线，每个修复都必须保持全绿
2. **不破坏已有协议语义**——check-gate.py 是核心 gate，P4 判定新增一步须保证返回约定（1/2）
   与既有调用链兼容
3. **挂载阶段必须 P4，不挂 P6**——`git diff --cached` 在 P6 已不含代码 diff（v2 教训，BDD-13 防复发）
4. **范围锁定**——若 P1 分析发现需改动超出 P0-brief 锁定范围，须先停下跟用户确认

## 4. 关键验证命令

```bash
# 在 worktree 根执行：

# 全量测试（必须全绿才算过）
python3 -m pytest agate/tests/ -n auto

# 一致性（0 ERROR 才行；--strict-errors-only 仅在 ERROR 时 exit 非 0，对齐 DEBT0012/TAG0017 语义）
# ⚠️ 必须用 worktree 自己的脚本（检查对象是 worktree 里的协议文件），不要用 ~/.agate 的
python3 agate/scripts/check-protocol-consistency.py --strict-errors-only

# shellcheck
shellcheck -S warning agate/scripts/*.sh

# ruff（改 py 脚本后）
~/.venvs/agate-dev/bin/ruff check agate/scripts/

# 测试计数（验证文档没漂移）
bash agate/tests/scripts/count-tests.sh

# 单脚本测试（改哪个跑哪个，TDD 先红后绿）
python3 -m pytest agate/tests/unit/test_{具体测试文件}.py
```

## 5. 阶段推进纪律（T001 血泪教训）

- **commit 时 phase = 本 commit 产出阶段**：P1 产出 → phase=P1 再 commit；推进 P2 随 P2 产出同
  commit。**不要**先写 phase=P2 再 commit P1 产出（pre-commit 会用 P2 gate 检查，P2-design.md
  不存在 → 拦截）
- **改脚本走 TDD**：先写失败测试确认红 → 改脚本确认绿（AGENTS.md「改脚本的工作流」）
- **git 命令加 timeout**、单步串行（AGENTS.md 工具纪律）
- **commit message 含 `wf({Txxx}-P{阶段}):` 前缀**
- **改 `agate/*.md`、`agate/scripts/*.py/.sh`、`agate/phase-cards/*` 触发 SELF-GATE**：
  commit message 需含 `self-gate-review:` 或 `self-gate-skip:`（否则 commit-msg hook WARNING）。
  协议文档变更需跑 `check-protocol-consistency.py` 确认无 ERROR

## 6. 任务编号与状态

- 任务目录：`agate-workspace/tasks/TAG0026-maintainability-gate/`（在 worktree 里）
- `.state.yaml`：phase=P0（P1 开始后推进）
- active-tasks.md「待开始」已有 TAG0026 行
- roadmap：RM-AG0046 关联本任务（scheduled）
- **编号体系**：任务用 `{Txxx}`（项目代号 + 动态数字的 Jira 式编号）。校验器 `^T[A-Z]{2}\d+$`

## 7. 已知风险与止损

- **check-gate.py 是核心 gate（回归风险最高）**：所有任务 P0-P8 都经它判定，P4 新增一步须保持
  返回约定兼容 → 全量 pytest + consistency 0 ERROR 是硬门槛，失败立即停下排查
- **挂载阶段错位（v2 教训）**：检测器数据源 `git diff --cached` 必须与 P4（代码 staged）对齐，
  挂 P6 是死代码 → BDD-13 专门验证"数据源与挂载阶段对齐"，先写这个测试
- **阈值 N=1000 无实证**：来自 Cursor skill，文档/配置须明确"默认值仅供参考可配置"，
  不造成"协议断言该阈值"的错觉
- **fuzzy-boundary 正则集只覆盖 Python/TS**：其它语言不在本版范围，项目经 gate_commands 自行补充
- **移动代码假阳性**：已知行为（含裸 except 的代码块被移动 → diff 判新增），靠 known-violations
  登记吸收，不引入跨行移动检测（BDD-12 验证登记路径可用）
- **known-violations 与 known-failures 语义相反**：三重门槛必须落实"数量对齐 + P4 评审 approve"，
  不得退回"登记即放行"（v3 已修复，实现须守住）
- **登记模板格式**：须用 `| N |` 行首表格格式（`count_kf_entries` 依赖），P4 评审确认列不参与
  机械计数（防"填了就自动放行"错觉）→ 止损：模板字段与 BDD-8 对照

## 8. 完成后

- P8 gate + READY → 提 PR 合并 main（PR 普通 merge 非 squash，tag 要求）
- **合并前在 PR 里看 CI 结果**——pytest/shellcheck/consistency/gate-backstop 全绿才算过
- roadmap 回写关联条目 RM-AG0046 → done（P8 gate 硬校验，RM-AG0043）
- 复盘按 agate 自身变更流程归档（合并后在主 checkout 写复盘 + 更新 roadmap/版本）

## 9. 交接确认

- worktree 基线全绿：全量 pytest + consistency 0 ERROR（--strict-errors-only）
- hooks 就位（指向 `~/.agate` 稳定版）、orchestrator 已注册、依赖齐全
- 任务数据就绪：TAG0026 P0-brief + .state.yaml phase=P0
- 交接单位置：`HANDOFF-TAG0026.md`（worktree 根，已 commit）

---

> 启动入口（HANDOFF 读取盲点）：orchestrator 默认读 `active-tasks.md` + `.state.yaml`，并不会
> 自动读本交接单。新 session 首条指令必须显式写"**读 worktree 根 `HANDOFF-TAG0026.md`**"。
