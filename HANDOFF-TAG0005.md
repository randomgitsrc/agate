# TAG0005 交接单 — agate 机制修复批

> 本交接单供 worktree session 的 agent 按此启动 TAG0005 任务。
> 任务已 P0 立项（.state.yaml phase=P0，P0-brief.md 已就绪）。
> worktree 已完成构建安装与基线验证，可直接开始 P1。

---

## 1. 你要做什么

**TAG0005**：agate 机制修复批。

**一句话**：修 4 个已核实的机制/契约缺陷——RM-AG0010（P2 gate vs C8 契约矛盾）、RM-AG0011（P5 gate_commands 计数语义）、RM-AG0012（自定义角色两瑕疵）、RM-AG0003（短命会话自动重试）。均为"现有东西错了/不完整"的修复，无新机制。

## 2. 工作区布局（双工作区纪律，违反必出事故）

| 路径 | 角色 | 纪律 |
|------|------|------|
| `/home/kity/oclab/agate/.worktrees/agate-TAG0005` | **本任务 worktree（改造对象）** | 在这里改代码、写阶段产出、跑测试、git commit |
| `/home/kity/oclab/agate`（主 checkout） | 协议本体 + 任务数据 + `~/.agate` 指向 | **禁止改动**。它是稳定版来源，也是 hook 的 AGATE_ROOT |
| `~/.agate`（软链 → 主 checkout/agate） | **稳定版 v0.44.0（开发工具）** | **禁止改动**。跑 gate / 读卡片用它 |

**核心原则（AGENTS.md dogfooding 工作流约定）**：
- **跑 gate 用 `~/.agate`**（稳定版），**改代码/跑测试在 worktree**。
- commit 时 pre-commit hook 用 `~/.agate/scripts/pre-commit-gate.sh` 判定——gate 判定对象是 worktree 里的产出文件，但 gate 工具本身是 `~/.agate`。这是有意的：改造期间工具稳定，改造对象变化。
- **⚠️ gate 工具 ≠ 检查对象（最容易搞混的点）**：
  - commit hook 的 gate **判定工具**用 `~/.agate`（稳定版）——它读 `~/.agate` 自己的脚本逻辑
  - 但 `check-protocol-consistency.py` **必须用 worktree 自己的**（`python3 agate/scripts/check-protocol-consistency.py`），因为检查对象是 **worktree 里的协议文件**。若误用 `~/.agate` 的 consistency 脚本，会扫到主 checkout 的文件而非 worktree 的改动
  - 同理：`bash ~/.agate/scripts/agate-summary.sh` 在 worktree 里跑会显示**主 checkout 的上下文**（版本/分支/HEAD 是稳定版的），不代表 worktree 状态——worktree 自己的状态用 `git log`/`git status` 看
- **hook 在共享 git 目录**：worktree 的 `.git` 是文件（指向主 checkout `.git`），hook 实际在主 checkout 的 `.git/hooks/`（pre-commit/commit-msg/pre-push 已软链安装）。worktree commit 时 hook 自动触发。

**已完成的 setup（worktree 已可独立使用）**：
- 依赖齐全：bash 5.2 / python 3.12 / pyyaml / bats 1.10 / shellcheck
- 基线验证：714 bats 全绿 + consistency 0 ERROR（--strict）
- commit hook：指向 `~/.agate`（稳定版），worktree commit 自动触发
- orchestrator 注册：`.opencode/agents/orchestrator.md` → `~/.agate/orchestrator-template.md`（符号链接，不拷贝）
- 工作区解析：`agate-workspace-resolve.sh` 输出 worktree 自己的 `agate-workspace/`
- 任务数据：TAG0005 P0-brief + .state.yaml phase=P0 在 worktree 的 `agate-workspace/tasks/`

## 3. 任务范围（P0-brief 已锁定，P1 细化 BDD）

### 已核实并确认的缺陷（全部有代码证据，见 P0-brief issues）

**RM-AG0010（P2 gate vs C8 契约矛盾）**：
- `check-gate.sh` P2 L155-159：无条件要求 `P2-review.md` 存在且 status=approved
- `role-system.md` C8 表 backend 域 = "review（P4 后）"，P2 无触发角色
- `phase-cards/P2-design.md` C8 表同样无
- 后果：backend 域（low/medium）任务 P2 按 C8 不派评审 → 无 P2-review.md → gate exit 1 拦截 → 主 Agent 被迫自造评审（TPV0090 实测）
- 修复 = 三处同步（二选一：C8 补 backend P2 也派 review，或 gate 对无 C8 触发角色豁免）——**P1 需先定方案，涉及"backend P2 是否必须派评审"的产品判断，必要时问用户**

**RM-AG0011（P5 gate_commands 计数语义）**：
- 实际计数逻辑在 `agate-gate-p5-count.py`（check-gate.sh L250 调用），WARNING 由 check-gate.sh L253 输出
- P2 声明 P5/P5_cli_remote/P5_serial 时计数 3，实际是"1 主 + 2 辅助"——误导主 Agent
- 修复 = 区分主/辅命令，WARNING 文案区分

**RM-AG0012（自定义角色两瑕疵）**：
- ① `dispatch-prompt.md` L10-13 无条件注入"Review 角色特别指令"（status draft→approved）到执行角色，语义混乱——修复 = 按角色 type 条件注入
- ② `agate-render-dispatch-prompt.sh` L63-67 角色文件不存在时报错到 stderr 但 exit 0——修复 = 角色不存在 exit 非零（如 exit 2）

**RM-AG0003（短命会话重试）**：
- `dispatch-protocol.md` L105 已有"空返回的恢复策略" + 重试机制（L51-57）但全手动
- TQC0001 实测 P2 49 秒 / P3 3 分钟各一次空返回
- 修复 = 恢复策略加"自动重试一次" + "会话时长 <1min 判定异常告警"（增量增强，不改现有重试语义）

### 核心约束（不可违反）
1. **Linux 现状是基线**——现有 714 bats 测试全绿是回归底线，每个修复都必须保持全绿
2. **不破坏已有协议语义**——改动是"契约对齐 / 计数语义 / 条件注入 / 增量重试"，不是重构协议流程
3. **范围锁定**——若 P1 分析发现需改动超出 P0-brief 锁定范围，须先停下跟用户确认
4. **【强制要求】同类扫描**——P1 阶段对每个修复做全仓同类模式 grep（"静默 exit 0" / "无条件注入评审指令" / "P5 前缀计数"），发现的同类实例一并纳入 BDD，不能只修 roadmap 列的位置（agate 历史多次栽在"修一处漏同类"）。用户明确：不愿意一轮一轮来回改

## 4. 关键验证命令

```bash
# 在 worktree 根执行：

# 全量测试（必须全绿才算过）
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/

# 一致性（0 ERROR 才行；--strict 让 WARNING 也阻断）
# ⚠️ 必须用 worktree 自己的脚本（检查对象是 worktree 里的协议文件），不要用 ~/.agate 的
python3 agate/scripts/check-protocol-consistency.py --strict

# shellcheck
shellcheck -S warning agate/scripts/*.sh

# 测试计数（验证文档没漂移）
bash agate/tests/scripts/count-tests.sh

# 单脚本测试（改哪个跑哪个，TDD 先红后绿）
bats agate/tests/unit/check-gate.bats
bats agate/tests/unit/check-gate-p1-review.bats
bats agate/tests/unit/agate-render-dispatch-prompt.bats  # 若有
bats agate/tests/unit/check-state-transition.bats
```

## 5. 阶段推进纪律（T001 血泪教训）

- **commit 时 phase = 本 commit 产出阶段**：P1 产出 → phase=P1 再 commit；推进 P2 随 P2 产出同 commit。**不要**先写 phase=P2 再 commit P1 产出（pre-commit 会用 P2 gate 检查，P2-design.md 不存在 → 拦截）
- **改脚本走 TDD**：先写失败测试确认红 → 改脚本确认绿（AGENTS.md「改脚本的工作流」）
- **批量机械改动的 TDD 策略**：这类改动每个都写单独测试边际成本高。建议——①先写一个"grep 断言审计"测试作为回归拦截；②批量改动后跑该断言 + 全量 bats 确认绿。不要为每个小改动单独写测试，也不要跳过测试直接改
- **git 命令加 timeout**、单步串行（AGENTS.md 工具纪律）
- **commit message 含 `wf(TAG0005-P{阶段}):`** 前缀
- **改 `agate/*.md`、`agate/scripts/*.py/.sh`、`agate/phase-cards/*` 触发 SELF-GATE**：commit message 需含 `self-gate-review:` 或 `self-gate-skip:`（否则 commit-msg hook WARNING）。协议文档变更需跑 `check-protocol-consistency.py` 确认无 ERROR

## 6. 任务编号与状态

- 任务目录：`agate-workspace/tasks/TAG0005-mechanism-fixes/`（在 worktree 里）
- `.state.yaml`：phase=P0（P1 开始后推进）
- active-tasks.md「待开始」已有 TAG0005 行
- roadmap：RM-AG0010/0011/0012/0003 关联本任务（scheduled）
- **编号体系**：任务用 `TAG0005`（项目代号 `AG` + 动态数字，Jira 式编号）。校验器 `^T[A-Z]{2}\d+$`

## 7. 已知风险与止损

- **RM-AG0010 有方案决策**（二选一）→ P1 先定方案再改；若涉及"backend P2 是否必须派评审"的产品判断，须停下问用户（超出机械修复范围）
- **四处改动互不耦合但都触发 SELF-GATE** → 每处 commit 带 self-gate 标记；protocol-alignment-review 审查（SELF-GATE 流程）
- **RM-AG0012 渲染脚本 exit code 改动可能影响调用方** → P1 先 grep 确认 agate-render-dispatch-prompt.sh 的调用处
- **RM-AG0003 增量重试不能破坏现有语义** → 保持现有重试逻辑，只加自动重试 + 告警
- **同类扫描可能发现超出 4 处的同类实例** → 全部纳入 BDD（用户明确：不一轮一轮来回改）

## 8. 完成后

- P8 gate + READY → 提 PR 合并 main（PR 普通 merge 非 squash，tag 要求）
- **合并前在 PR 里看 CI 结果**——bats/shellcheck/consistency/gate-backstop 全绿才算过
- roadmap 回写 RM-AG0010/0011/0012/0003 → done
- 复盘按 agate 自身变更流程归档（合并后在主 checkout 写复盘 + 更新 roadmap/版本）
- **交接顺序**：TAG0005 完成后 → TAG0009（测试套件平台无关化）在下一个 worktree 实施（主 checkout 侧会安排）

## 9. 交接确认

- worktree 基线全绿：714 bats + consistency 0 ERROR（--strict）
- hooks 就位（指向 `~/.agate` 稳定版）、orchestrator 已注册、依赖齐全
- 任务数据就绪：TAG0005 P0-brief + .state.yaml phase=P0
- 交接单位置：`HANDOFF-TAG0005.md`（worktree 根，已 commit）

---

> 模板字段已填充。任务范围/风险从 P0-brief issues + known_risks 提取，行号在 v0.44.0 下已核对（check-gate L159 / render L67 / dispatch L105）。
