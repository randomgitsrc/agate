# TAG0017 交接单 — agate 协议工具链修复批

> 本交接单供 worktree session 的 agent 按此启动 TAG0017 任务。
> 任务已 P0 立项（.state.yaml phase=P0，P0-brief.md 已就绪）。
> worktree 已完成构建安装与基线验证，可直接开始 P1。

---

## 1. 你要做什么

**TAG0017**：agate 协议工具链修复批（RM-AG0027 + RM-AG0028）。

**一句话**：修复 5 个真实、未修复、影响**每个后续任务**的协议工具链系统缺陷——DEBT0010（gate_commands 键解析脚本未排除 _timeout_seconds，4 脚本同类）+ DEBT0011（SELF-GATE 审查文件纯日期命名跨任务覆盖）+ DEBT0012（--strict 与 && 链路短路）+ DEBT0014（Windows Store python3 占位符命中 hook）+ DEBT0015（env_constraints deploy 类动作无执行/gate 绑定，TQC0001 跨项目反馈）。DEBT0013（P8 时序文档注）已在 PR #166 修复、DEBT0009（决策备忘非债）已单独关闭，不在本任务范围。

## 2. 工作区布局（双工作区纪律，违反必出事故）

| 路径 | 角色 | 纪律 |
|------|------|------|
| `/home/kity/oclab/agate/.worktrees/agate-TAG0017` | **本任务 worktree（改造对象）** | 在这里改代码、写阶段产出、跑测试、git commit |
| `/home/kity/oclab/agate`（主 checkout） | 协议本体 + 任务数据 + `~/.agate` 指向 | **禁止改动**。它是稳定版来源，也是 hook 的 AGATE_ROOT |
| `~/.agate`（软链 → 主 checkout/agate） | **稳定版（开发工具）** | **禁止改动**。跑 gate / 读卡片用它 |

**核心原则（AGENTS.md T001 约定沿用）**：
- **跑 gate 用 `~/.agate`**（稳定版），**改代码/跑测试在 worktree**。
- commit 时 pre-commit hook 用 `~/.agate/scripts/pre-commit-gate.sh` 判定——gate 判定对象是 worktree 里的产出文件，但 gate 工具本身是 `~/.agate`。这是有意的：改造期间工具稳定，改造对象变化。
- **⚠️ gate 工具 ≠ 检查对象（最容易搞混的点）**：
  - commit hook 的 gate **判定工具**用 `~/.agate`（稳定版）——它读 `~/.agate` 自己的脚本逻辑
  - 但 `check-protocol-consistency.py` **必须用 worktree 自己的**（`python3 agate/scripts/check-protocol-consistency.py`），因为检查对象是 **worktree 里的协议文件**。若误用 `~/.agate` 的 consistency 脚本，会扫到主 checkout 的文件而非 worktree 的改动
  - 同理：`python3 ~/.agate/scripts/agate-summary.py` 在 worktree 里跑会显示**主 checkout 的上下文**（版本/分支/HEAD 是稳定版的），不代表 worktree 状态——worktree 自己的状态用 `git log`/`git status` 看
- **hook 在共享 git 目录**：worktree 的 `.git` 是文件（指向主 checkout `.git`），hook 实际在主 checkout 的 `.git/hooks/`（pre-commit/commit-msg/pre-push 已软链安装）。worktree commit 时 hook 自动触发。
- **编排/派发类工具一律用 `~/.agate/scripts/` 稳定版**：`agate-inject-card.py` 等有 AGATE_ROOT 自解析逻辑，worktree 内用相对路径调用会读到 worktree 正在被修改的协议卡片副本（TAG0016 P1-P4 教训）。

**已完成的 setup（worktree 已可独立使用）**：
- 依赖齐全：bash 5.2 / python 3.12 / pyyaml / pytest 9.0.3 / shellcheck
- 基线验证：全量 pytest 950 全绿（842 unit + 108 其余）+ consistency 0 ERROR（--strict）
- commit hook：指向 `~/.agate`（稳定版），worktree commit 自动触发
- orchestrator 注册：`.opencode/agents/orchestrator.md` + `.claude/agents/orchestrator.md`（均软链到 `~/.agate/orchestrator-template.md`，双平台）
- 工作区解析：`agate_common.py` 输出 worktree 自己的 `agate-workspace/`
- 任务数据：TAG0017 P0-brief + .state.yaml phase=P0 在 worktree 的 `agate-workspace/tasks/`

## 3. 任务范围（P0-brief 已锁定，P1 细化 BDD）

### 已核实并确认的缺陷/需求（全部有代码证据，见 P0-brief known_risks + roadmap RM-AG0027/0028 详情）

**DEBT0010 gate_commands 键解析脚本未排除 _timeout_seconds 后缀（4 处同类，medium）**：
- 4 脚本只排除 `_formatter`、未排除 `_timeout_seconds`：`agate-read-gate-commands.py` L31 / `agate-gate-missing-cmds.py` L20 / `agate-gate-p5-count.py` L23 / `agate-read-p5-commands.py` L29
- TAG0016 三阶段实测复现：P2 报假"命令不存在" WARNING / P3 `check-tdd-red.py` 对真红灯误报 exit 1（A 类）/ P5 报假"1 主+1 辅助"
- 修复：4 脚本判据统一补 `key.endswith("_timeout_seconds")`（与 `_formatter` 并列，可抽 `agate_common.py` 共享判据函数）+ 回归用例覆盖 P2/P3/P5

**DEBT0011 SELF-GATE 审查文件纯日期命名跨任务覆盖（medium）**：
- `SELF-GATE.md` 派发模板规定 `agate-alignment-review-{date}.md` / `agate-alignment-{date}-{NN}.progress.md`（只含日期）
- TAG0016 实测：TAG0015/TAG0016 同日各自触发审查，TAG0016 覆盖 TAG0015 已提交历史（git diff 实证）
- 修复：命名模板补任务标识 + `protocol-alignment-review` 角色文件提示 subagent Write 前先确认目标路径

**DEBT0012 check-protocol-consistency.py --strict 与 && 链路永久短路（medium）**：
- main() 末尾 `--strict` 模式"WARNING-only 也 exit 2" 与 `gate_commands.P5` 的 `&&` 串联组合，在存量 314 条 WARNING 未清零时**永远短路**链路末步
- TAG0016 P5 实跑 count-tests 未执行到；历史 `command | tail` 验证方法盲区掩盖了它
- 修复（二选一或都做）：(a) P2 卡片 gate_commands 声明示例不再推荐 `--strict` 放 `&&` 链路中间；(b) `check-protocol-consistency.py` 新增 `--strict-errors-only` 模式

**DEBT0014 Windows Store python3 占位符命中 hook 探测循环（medium，跨项目反馈）**：
- 3 薄壳（`pre-commit-gate.sh` / `commit-msg-self-gate.sh` / `pre-push-gate.sh`）第 11-13 行探测循环命中 WindowsApps 下 Store 占位符 `python3.exe`（`command -v` 能找到、exec exit 49）→ commit 阻断
- 修复：3 薄壳探测后做可执行性小测试（exit 49 / stderr 含 "Microsoft Store" → skip）+ 或 `AGATE_PYTHON` 环境变量优先 + platform-notes 已知限制表新增 + AGENTS.md 同步

**DEBT0015 env_constraints 声明性字段无执行/gate 绑定（medium，TQC0001 跨项目反馈）**：
- `env_constraints` 是声明性字段——协议所有引用只"确认/细化 + 注入"（`agate-extract-context.py` L107-109）；`check-gate.py` grep `deploy` 零命中
- TQC0001 实证：P2 声明 `env_constraints.deploy`（windeployqt 构建 dist），全流程从未主动执行，用户提醒才补做
- 修复：env_constraints 语义边界文档化（声明性 vs 执行性）+ UI 任务 P4 后构建 dist（P4 卡「自查≠gate」节补）+ 可选 P8 gate 加 dist 产物检查

### 核心约束（不可违反）
1. **Linux 现状是基线**——现有 950 pytest 测试全绿是回归底线，每个修复都必须保持全绿
2. **Windows 兼容是增量**——本环境（环境（Linux）无法实测 Windows，靠静态修复 + Linux 回归 + CI matrix 兜底。**不要宣称"已实测 Windows"**（DEBT0014 涉及 Windows 时由 CI matrix 验证）
3. **5 条 issue 域重叠严重**——同改 `gate_commands` 解析 / `env_constraints` 语义边界（DEBT0010 + DEBT0015 都涉及 P2 卡片 gate_commands 声明）；同改薄壳（DEBT0014 一人改三薄壳）；同改 SELF-GATE/SELF-GATE.md（DEBT0011）→ **P1 必须按"文件→改动"归并 BDD，避免重复改同文件两轮**——这正是 RM-AG0025 倡导的"系统排查防重复"在协议工具链改造上的应用
4. **P1 隐藏整合点**——DEBT0010（gate_commands 解析 _timeout_seconds）与 DEBT0015（env_constraints deploy 无执行）的修复方向都触及"`gate_commands` 是真正执行机制、env_constraints 是声明"这条语义边界；P1 派发 architect 设计时要把这两条**作为整体**设计（不能分开两次设计导致口径冲突）
5. **范围锁定**——若 P1 分析发现需改动超出 P0-brief 锁定范围，须先停下跟用户确认
6. **【强制要求】同类扫描 + 影响面梳理**——P1 必须 grep 全仓以下关键词建影响面表：
   - `_timeout_seconds`（找第五处遗漏消费点）
   - `agate-alignment-review-{date}`（找同类命名引用）
   - `--strict` 在 gate_commands/协议文档的所有使用点
   - `env_constraints` 全协议引用点 + 对应 gate_commands 消费
   - `command -v` / 薄壳探测相关 grep（防 Windows Store 类类似陷阱）
   - `python3` / `WindowsApps` / `Store`（防同类跨平台兼容性陷阱）
   
   用户明确：不愿意一轮一轮来回改

## 4. 关键验证命令

```bash
# 在 worktree 根执行：

# 全量测试（必须全绿才算过）
python3 -m pytest agate/tests/

# 一致性（0 ERROR 才行；--strict 让 WARNING 也阻断）
# ⚠️ 必须用 worktree 自己的脚本（检查对象是 worktree 里的协议文件），不要用 ~/.agate 的
python3 agate/scripts/check-protocol-consistency.py --strict

# shellcheck
shellcheck -S warning agate/scripts/*.sh

# 测试计数（验证文档没漂移）
bash agate/tests/scripts/count-tests.sh

# 单脚本测试（改哪个跑哪个，TDD 先红后绿）
python3 -m pytest agate/tests/unit/test_{具体测试文件}.py
```

## 5. 阶段推进纪律（T001 血泪教训）

- **commit 时 phase = 本 commit 产出阶段**：P1 产出 → phase=P1 再 commit；推进 P2 随 P2 产出同 commit。**不要**先写 phase=P2 再 commit P1 产出（pre-commit 会用 P2 gate 检查，P2-design.md 不存在 → 拦截）
- **改脚本走 TDD**：先写失败测试确认红 → 改脚本确认绿（AGENTS.md「改脚本的工作流」）
- **批量机械改动的 TDD 策略**：这类改动每个都写单独测试边际成本高。建议——①先写一个"grep 断言审计"测试作为回归拦截；②批量改动后跑该断言 + 全量 pytest 确认绿。不要为每个小改动单独写测试，也不要跳过测试直接改
- **git 命令加 timeout**、单步串行（AGENTS.md 工具纪律）
- **commit message 含 `wf(TAG0017-P{阶段}):` 前缀**
- **改 `agate/*.md`、`agate/scripts/*.py/.sh`、`agate/phase-cards/*` 触发 SELF-GATE**：commit message 需含 `self-gate-review:` 或 `self-gate-skip:`（否则 commit-msg hook WARNING）。本任务改 5 个 gate 脚本 + 3 薄壳 sh + 4 份协议文档 + 角色文件 → **几乎所有 commit 都需要 self-gate-review 语义审查**（派发 `protocol-alignment-review` subagent，角色文件 `agate/assets/review-roles/protocol-alignment-review.md`）

## 6. 任务编号与状态

- 任务目录：`agate-workspace/tasks/TAG0017-toolchain-fixes/`（在 worktree 里）
- `.state.yaml`：phase=P0（P1 开始后推进）
- active-tasks.md「待开始」已有 TAG0017 行
- roadmap：RM-AG0027 + RM-AG0028 关联本任务（scheduled）
- **编号体系**：任务用 `TAG0017`（项目代号 + 动态数字）。校验器 `^T[A-Z]{2}\d+$`

## 7. 已知风险与止损

- 5 条 issue 域重叠严重（4 个改 P2 卡 + 3 个改薄壳 + 4 个改协议文档）→ 触发大量 SELF-GATE 评审 → 流程会重，**P1 阶段必须按"文件→改动"归并 BDD** 避免重复
- DEBT0010 修复会触碰 `check-tdd-red.py` 判定语义核心——回归测试必须覆盖"P3 声明 timeout_seconds 时真红灯仍正确判定"，不能把修复做成放宽判定
- DEBT0010 抽共享判据函数是建议非强制——若 4 处判据上下文差异大，可保持各自内联修复 + grep 断言审计测试防第五处
- DEBT0012 的 (b) 方案加新 CLI 模式影响 `check-protocol-consistency.py` 的 AI4 接口——需要与既有 `--strict`/默认模式测试覆盖区分
- DEBT0011 需一并检查存量已生成的 `docs/reviews/` 文件是否有历史同名覆盖（TAG0016 已手工恢复一次，确认无其他遗留）
- DEBT0014 需在 Windows CI matrix 验证 + 真实 Git Bash 环境实测（本环境为 Linux，薄壳改动只能静态分析 + grep 断言审计）
- DEBT0015 与 DEBT0010 的语义整合风险：两者都触及"`gate_commands` vs `env_constraints` 执行绑定"边界——P1 architect 必须**整体设计**这两条（不能分开两次设计），写 P2-design.md 时明确语义边界
- **复盘自举验证**：本任务完成后按 TAG0015 落地的新机制在 `tasks/TAG0017/retrospective.md` 写复盘（含 frontmatter `mechanism_issues/execution_issues/feedback_ready` + 「## agate 反馈」节）；平台 Store 占位符、env_constraints 边界等发现都属于"对 agate 协议自身的反馈"，可走 `AGATE_FEEDBACK=on` 提取

## 8. 完成后

- P8 gate + READY → 提 PR 合并 main（PR 普通 merge 非 squash，tag 要求）
- **合并前在 PR 里看 CI 结果**（跨平台任务看 matrix 双平台）——pytest/shellcheck/consistency/gate-backstop 全绿才算过
- roadmap 回写关联条目 → done（RM-AG0027 + RM-AG0028）
- 复盘按 TAG0015 落地的新机制执行（`tasks/{Txxx}/retrospective.md` + frontmatter 三字段）

## 9. 交接确认

- worktree 基线全绿：950 pytest + consistency 0 ERROR（--strict）
- hooks 就位（指向 `~/.agate` 稳定版）、orchestrator 双平台已注册、依赖齐全
- 任务数据就绪：TAG0017 P0-brief（5 条 issue）+ .state.yaml phase=P0
- 交接单位置：`HANDOFF-TAG0017.md`（worktree 根，已 commit）

---

> 模板字段：任务编号、任务标题/一句话、worktree/主 checkout 路径、缺陷清单（文件:行号:问题）、核心约束、验证命令、阶段纪律、风险、完成后动作。复制到 worktree 根目录 `HANDOFF-TAG0017.md` 填写。