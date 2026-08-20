# TAG0007 交接单 — agate 项目结构管理（骨架 + code-map）新增机制

> 本交接单供 worktree session 的 agent 按此启动 TAG0007 任务。
> 任务已 P0 立项（.state.yaml phase=P0，P0-brief.md 已就绪）。
> worktree 已完成构建安装与基线验证，可直接开始 P1。

---

## 1. 你要做什么

**TAG0007**：agate 项目结构管理机制。

**一句话**：给 agate 协议新增"项目结构管理"能力——**0→1 项目骨架脚手架**（RM-AG0008）+ **CODE-MAP 架构演进纪律**（RM-AG0009）。骨架是"初始结构"、code-map 是"演进维护"，同一主题"项目结构管理"。

## 2. 工作区布局（双工作区纪律，违反必出事故）

| 路径 | 角色 | 纪律 |
|------|------|------|
| `/home/kity/oclab/agate/.worktrees/agate-TAG0007` | **本任务 worktree（改造对象）** | 在这里改代码、写阶段产出、跑测试、git commit |
| `/home/kity/oclab/agate`（主 checkout） | 协议本体 + 任务数据 + `~/.agate` 指向 | **禁止改动**。它是稳定版来源，也是 hook 的 AGATE_ROOT |
| `~/.agate`（软链 → 主 checkout/agate） | **稳定版（开发工具）** | **禁止改动**。跑 gate / 读卡片用它 |

**核心原则（AGENTS.md T001 约定沿用）**：
- **跑 gate 用 `~/.agate`**（稳定版），**改代码/跑测试在 worktree**。
- commit 时 pre-commit hook 用 `~/.agate/scripts/pre-commit-gate.sh` 判定——gate 判定对象是 worktree 里的产出文件，但 gate 工具本身是 `~/.agate`。
- **⚠️ gate 工具 ≠ 检查对象（最容易搞混的点）**：
  - commit hook 的 gate **判定工具**用 `~/.agate`（稳定版）
  - 但 `check-protocol-consistency.py` **必须用 worktree 自己的**（`python3 agate/scripts/check-protocol-consistency.py`），检查对象是 worktree 里的协议文件
  - `python3 ~/.agate/scripts/agate-summary.py` 在 worktree 跑显示主 checkout 上下文，不代表 worktree 状态
  - **所有编排/派发类工具（`agate-inject-card.py` / `agate-render-dispatch-prompt.py` / `agate-next-card.py` 等）一律用 `~/.agate/scripts/` 稳定版调用**（TAG0016 教训：worktree 相对路径调用会读到 worktree 正在被修改的协议卡片副本）
- **hook 在共享 git 目录**：worktree 的 `.git` 是文件（指向主 checkout `.git`），hook 实际在主 checkout `.git/hooks/`（pre-commit/commit-msg/pre-push 已软链安装）。

**已完成的 setup（worktree 已可独立使用）**：
- 依赖齐全：bash 5.2 / python 3.12 / pyyaml / pytest 9.0.3 / shellcheck（跑 pytest/pyyaml 用**系统 `/usr/bin/python3`**；ruff 用 `~/.venvs/agate-dev/bin/ruff`）
- 基线验证：全量 pytest **1011 passed, 2 skipped** + consistency 0 ERROR（默认模式 exit 0；314 WARNING 全为历史叙事死链，非回归）
- commit hook：指向 `~/.agate`（稳定版），worktree commit 自动触发
- orchestrator 注册：`.opencode/agents/orchestrator.md` + `.claude/agents/orchestrator.md`（均软链到 `~/.agate/orchestrator-template.md`，双平台）
- 工作区解析：`agate_common.py` 输出 worktree 自己的 `agate-workspace/`
- 任务数据：TAG0007 P0-brief + .state.yaml phase=P0 在 worktree 的 `agate-workspace/tasks/`

## 3. 任务范围（P0-brief 已锁定，P1 细化 BDD）

### 已核实并确认的缺陷/需求（见 P0-brief issues + known_risks，均有机制证据）

**RM-AG0008 0→1 项目无骨架设计（新增机制）**：
- P0-brief 只写任务描述/风险/环境，无"项目骨架设计"环节；P1 analyst 分析需求、P2 architect 设计本次任务方案，都不要求设计整个项目目录布局
- 后果：CMakeLists/源码/测试/文档/构建产物散落、阶段文件与工程文件不同步（qtcalc-basic 复盘问题 C：CMake 引用尚未存在文件）
- 修复=①P1（或 P0）增"项目骨架"产出：按技术栈最佳实践输出目录树（C++/CMake：src/include/tests/docs/build/deploy；Web：src/components/hooks/pages/api）②骨架作为首个可验收产物，后续阶段产出落在骨架布局内 ③配 skeleton 模板

**RM-AG0009 code-map + 架构演进纪律缺失（新增机制）**：
- agate 每阶段（P2/P4）只对本次任务设计/实现，无全局架构视角；P7 一致性只查本次任务范围
- 缺"当前架构全貌"维护物（模块/层/依赖方向/关键文件）——subagent 每次独立上下文启动不知道项目有什么
- 缺"新增代码必须符合架构"约束——新增文件放哪层/依赖方向/是否复用抽象 vs 胶水堆叠；架构随版本漂移无防漂移机制
- 修复=①工作区维护 CODE-MAP.md（模块/层/依赖/关键文件/约定），P4 新增文件时更新，P7 核对漂移 ②P2 架构演进检查（新文件属哪层/依赖合规/复用抽象）③gate 或 WARNING 检测依赖方向偏离 ④P2 评审增设计模式合理性维度

### 核心约束（不可违反）
1. **Linux 现状是基线**——现有 1011 pytest 测试全绿是回归底线，每个修复都必须保持全绿
2. **两个都是"建"（新增机制），不是"修"**——需完整 P0-P8，不能 plan 硬做（2026-08-13 用户确认：不为了 hotfix 故意不做 task）
3. **不破坏已有协议语义**——骨架/code-map 是全新机制，但落地会触碰既有机制（P7 一致性检查、P2 架构评审、TAG0002 的 change_type 分流），避免新机制与旧机制并存时的口径冲突
4. **范围锁定**——若 P1 分析发现需改动超出 P0-brief 锁定范围，须先停下跟用户确认
5. **【强制要求】同类扫描 + 机制一致性**——P2 设计必须梳理"新增机制如何接入既有 gate/角色/卡片"。用户明确：**不愿意一轮一轮来回改**

## 4. 关键验证命令

```bash
# 在 worktree 根执行（用系统 python，非 venv——pytest 装在系统 python）：
PY=/usr/bin/python3

# 全量测试（必须全绿才算过）
$PY -m pytest agate/tests/

# 一致性（0 ERROR 才行）
# ⚠️ 必须用 worktree 自己的脚本（检查 worktree 里的协议文件），不要用 ~/.agate 的
$PY agate/scripts/check-protocol-consistency.py        # 默认（ERROR 才非 0，基线 exit 0）
$PY agate/scripts/check-protocol-consistency.py --strict   # 全量 WARNING 也阻断（当前 314 存量 WARNING 时 exit 2）

# shellcheck
shellcheck -S warning agate/scripts/*.sh

# 测试计数（验证文档没漂移）
bash agate/tests/scripts/count-tests.sh

# 单脚本测试（改哪个跑哪个，TDD 先红后绿）
$PY -m pytest agate/tests/unit/test_{具体测试文件}.py
```

## 5. 阶段推进纪律（T001 血泪教训）

- **commit 时 phase = 本 commit 产出阶段**：P1 产出 → phase=P1 再 commit；推进 P2 随 P2 产出同 commit。**不要**先写 phase=P2 再 commit P1 产出（pre-commit 会用 P2 gate 检查，P2-design.md 不存在 → 拦截）
- **改脚本走 TDD**：先写失败测试确认红 → 改脚本确认绿（AGENTS.md「改脚本的工作流」）
- **批量机械改动的 TDD 策略**：先写一个"grep 断言审计"测试作回归拦截；批量改动后跑断言 + 全量 pytest 确认绿。不为每个小改动单独写测试，也不跳过测试直接改
- **git 命令加 timeout**、单步串行（AGENTS.md 工具纪律：bash 加 `timeout N`、不并行 bash、卡住换读工具）
- **commit message 含 `wf(TAG0007-P{阶段}):` 前缀**
- **改 `agate/*.md`、`agate/scripts/*.py/.sh`、`agate/phase-cards/*` 触发 SELF-GATE**：commit message 需含 `self-gate-review:` 或 `self-gate-skip:`（否则 commit-msg hook WARNING）。本任务新增机制改协议文档 + 模板 + 可能新增脚本 → **几乎所有 commit 都需 self-gate-review 语义审查**（派发 `protocol-alignment-review` subagent，角色文件 `agate/assets/review-roles/protocol-alignment-review.md`）

## 6. 任务编号与状态

- 任务目录：`agate-workspace/tasks/TAG0007-project-structure/`（在 worktree 里）
- `.state.yaml`：phase=P0（P1 开始后推进）
- active-tasks.md「待开始」已有 TAG0007 行
- roadmap：RM-AG0008 + RM-AG0009 关联本任务（scheduled）
- **编号体系**：任务用 `TAG0007`（项目代号 + 动态数字）。校验器 `^T[A-Z]{2}\d+$`

## 7. 已知风险与止损

- **两个都是"建"（新增机制），需完整 P0-P8，工作量完整**——不能因"新机制"而裁剪阶段；scope 充分
- **RM-AG0008 新增"项目骨架"产出环节**——需设计放哪个阶段（P0/P1）、怎么验证（目录树可验收）、配模板（按技术栈）——P2 设计关键决策
- **RM-AG0009 新增 CODE-MAP 维护物 + 架构演进纪律**——CODE-MAP 放哪（工作区）、P2 怎么查架构合规、gate 怎么检测依赖偏离——设计决策多，P1/P2 需充分
- **改协议本体触发大量 SELF-GATE**——流程会重；P1 阶段必须按"文件→改动"归并 BDD 避免重复改同文件两轮（RM-AG0025 倡导的系统排查防重复）
- **自举验证机会**：agate 自己就是 0→1 项目的骨架案例，可在本仓库自举验证骨架/CODE-MAP 机制
- **P7 一致性 + P2 架构评审接入**——新机制与既有机制并存口径冲突是最大风险，P2 设计必须整体梳理接入点
- **复盘自举验证**：任务完成后按 TAG0015 落地的新机制在 `tasks/{Txxx}/retrospective.md` 写复盘（含 frontmatter 三字段 + 「## agate 反馈」节）

## 8. 完成后

- P8 gate + READY → 提 PR 合并 main（PR 普通 merge 非 squash，tag 要求）
- **合并前在 PR 里看 CI 结果**（跨平台任务看 matrix 双平台）——pytest/shellcheck/consistency/gate-backstop 全绿才算过
- roadmap 回写关联条目 → done（RM-AG0008 + RM-AG0009）
- 复盘按 agate 自身变更流程归档（合并后写复盘 + 更新 roadmap/版本）

## 9. 交接确认

- worktree 基线全绿：1011 pytest passed + consistency 0 ERROR（默认模式 exit 0）
- hooks 就位（指向 `~/.agate` 稳定版）、orchestrator 已注册（双平台）、依赖齐全（系统 python）
- 任务数据就绪：TAG0007 P0-brief + .state.yaml phase=P0
- 交接单位置：`HANDOFF-TAG0007.md`（worktree 根，已 commit）

---

> 模板字段：任务编号、任务标题/一句话、worktree/主 checkout 路径、缺陷清单（文件:行号:问题）、核心约束、验证命令、阶段纪律、风险、完成后动作。复制到 worktree 根目录 `HANDOFF-{Txxx}.md` 填写。
