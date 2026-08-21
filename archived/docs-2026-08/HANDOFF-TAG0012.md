# TAG0012 交接单 — agate 协议机制增强批

> 本交接单供 worktree session 的 agent 按此启动 TAG0012 任务。
> 任务已 P0 立项（.state.yaml phase=P0，P0-brief.md 已就绪）。
> worktree 已完成构建安装与基线验证，可直接开始 P1。

---

## 1. 你要做什么

**TAG0012**：agate 协议机制增强批（RM-AG0013 + RM-AG0014 + RM-AG0019 + RM-AG0023）。

**一句话**：把"同类扫描/影响面梳理"固化进阶段卡（RM-AG0013）、补 verification_env 机制边界与失败处理协议（RM-AG0014）、加 P0-brief 时效性验证（RM-AG0019）、加 subagent 运行时管控（RM-AG0023）——四条都是协议机制缺口，改动域重叠（phase-cards/dispatch-protocol/state-machine/角色文件），合并一个 task 避免四轮改同批文件。

## 2. 工作区布局（双工作区纪律，违反必出事故）

| 路径 | 角色 | 纪律 |
|------|------|------|
| `/home/kity/oclab/agate/.worktrees/agate-TAG0012` | **本任务 worktree（改造对象）** | 在这里改代码、写阶段产出、跑测试、git commit |
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

**已完成的 setup（worktree 已可独立使用）**：
- 依赖齐全：bash 5.2 / python 3.12 / pyyaml / pytest 9.0.3 / shellcheck
- 基线验证：全量 pytest 865 全绿（757 unit + 108 regression/integration/sanity）+ consistency 0 ERROR（--strict）
- commit hook：指向 `~/.agate`（稳定版），worktree commit 自动触发
- orchestrator 注册：`.opencode/agents/orchestrator.md` → `~/.agate/orchestrator-template.md`（符号链接，不拷贝）
- 工作区解析：`agate_common.py` 输出 worktree 自己的 `agate-workspace/`
- 任务数据：TAG0012 P0-brief + .state.yaml phase=P0 在 worktree 的 `agate-workspace/tasks/`

## 3. 任务范围（P0-brief 已锁定，P1 细化 BDD）

### 已核实并确认的缺陷/需求（全部有代码证据，见 P0-brief known_risks）

**协议机制缺口（4+1 条，全部见 roadmap 详情）**：
- **RM-AG0013（机制缺口）**：P0-P8 阶段卡均无"同类扫描/全仓 grep/影响面梳理/联动"要求。agate 历史多次栽在"修一处漏同类"（M4/M5 的 `[:：]` 只修一处、Q2 只修 P5 卡、TPV0090 backend 域反复踩 P2 契约）。"同类扫描"只存在于部分 task 的临时 P0-brief，机制层缺失。修复：P0 卡加"同类/影响面预判"、P1 卡加"同类扫描"、P2 卡加"影响面梳理"。
- **RM-AG0014（机制误用 + 协议空白）**：TAG0009 Windows CI 排障拉 11.7 小时。①机制误用——协议已有 verification_env（dispatch-protocol.md 专用于"环境依赖"），TAG0009 实际标成 supplementable（能力缺失三态，用错机制）；②真协议空白——verification_env 只定义"如何声明环境"，无"验证失败后怎么办"（无 CI 轮次预算/止损轮次/批处理要求/READY 后问题归属）。修复：P1 卡 + analyst 角色加 supplementable vs verification_env 边界注；补失败处理协议；CI 轮次预算进 P1。
- **RM-AG0019（检测+更新缺失）**：P0-brief 是立项时点快照，状态机当恒真前提——任务搁置再启动时前提漂移（TAG0008 实证：立项写 .sh 路线，启动时已全量 Python 化）。现有检测只查运行时工具可用，不查内容过时。修复：P0→P1 前提校验 + 漂移更新/重立项判断 + P1 analyst 发现过时标 `[P0_STALE]`。
- **RM-AG0023（运行时管控，TPV0093 回流）**：3 次 subagent 卡死（`cat` 挂 3.1h、`make test-quick` 挂 188min）。缺命令超时兜底、遇 flaky 偏离约束自由诊断、并行资源竞争、progress 心跳命令执行中失效。修复：①gate_commands/dispatch_plan 加 `timeout_seconds` 字段（阈值须合理——pytest 全量 ~70s/CDP E2E 需更大，不能低到误杀长命令 + 执行留痕）②dispatch-prompt 加"命令超时兜底"标准节（每个 bash 命令必须设 timeout ≤预期时长×1.5；超时→停止+写 progress 返回；遇非预期失败→记录后返回，禁止自行深入诊断）③P5 卡加"资源密集型默认串行"④progress 心跳扩展（命令**前**写 progress）。
- **RM-AG0014 环境准备职责边界（补充）**：verification_env 定义"如何声明环境"，还要补"谁负责准备"——主 Agent（P0-brief debug_env 声明，负责启动/维护/关停）vs subagent（自启无防护→卡死）；多 subagent 各启各的→冲突。建议：环境归主 Agent 统一管理，subagent 只消费不启动。落点：dispatch-protocol verification_env 节 + P5/P6 卡片。

### 核心约束（不可违反）
1. **Linux 现状是基线**——现有 865 pytest 测试全绿是回归底线，每个修复都必须保持全绿
2. **Windows 兼容是增量**——本环境（Linux）无法实测 Windows，靠静态修复 + Linux 回归 + CI matrix 兜底。**不要宣称"已实测 Windows"**
3. **不破坏已有协议语义**——本任务改的是协议文档/卡片/gate 脚本的行为增强，既有任务数据（.state.yaml/产出文件）兼容性不能破坏；P1 阶段必须按"哪些卡/哪些节"组织 BDD，避免重复改同文件
4. **范围锁定**——若 P1 分析发现需改动超出 P0-brief 锁定范围，须先停下跟用户确认
5. **【强制要求】同类扫描 + 影响面梳理是本任务自身的示范**——P1 必须 grep 全仓 phase-cards 确认"哪些卡片缺同类扫描要求"、grep verification_env 确认"哪些文件消费该字段"、grep P0-brief 确认"消费点"、grep timeout/os.execv 确认"运行时管控同类风险"。用户明确：不愿意一轮一轮来回改

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
- **commit message 含 `wf(TAG0012-P{阶段}):` 前缀**
- **改 `agate/*.md`、`agate/scripts/*.py/.sh`、`agate/phase-cards/*` 触发 SELF-GATE**：commit message 需含 `self-gate-review:` 或 `self-gate-skip:`（否则 commit-msg hook WARNING）。协议文档变更需跑 `check-protocol-consistency.py` 确认无 ERROR

## 6. 任务编号与状态

- 任务目录：`agate-workspace/tasks/TAG0012-protocol-mechanism-fixes/`（在 worktree 里）
- `.state.yaml`：phase=P0（P1 开始后推进）
- active-tasks.md「待开始」已有 TAG0012 行
- roadmap：RM-AG0013/0014/0019/0023 关联本任务（scheduled）
- **编号体系**：任务用 `TAG0012`（项目代号 + 动态数字，v2.0 起的 Jira 式编号）。校验器 `^T[A-Z]{2}\d+$`

## 7. 已知风险与止损

- 五条都改 phase-cards/dispatch-protocol/state-machine/角色文件 → 触发 SELF-GATE → 每个协议文档 commit 都需 self-gate-review/skip 标注 + consistency 0 ERROR
- 改动面高度重叠（RM-0013 改 P0-P2 卡、RM-0014 改 dispatch-protocol+P1 卡+analyst、RM-0019 改 P0/P1 卡+state-machine、RM-0023 改 dispatch-prompt+P5 卡+gate_commands）→ 同文件两轮改是本批要治的反模式，自己不能犯 → P1 必须合并规划 BDD，按"文件→改动"归并设计
- RM-AG0014 的"失败处理协议"是新增机制设计（止损轮次/批处理要求）→ P2 需定义具体规则，不是简单补文档
- RM-AG0019 的"重新立项判断"边界需可判定标准（漂移严重到什么程度算重立项 vs 更新 P0-brief）→ P2 设计
- RM-AG0023 的 timeout_seconds 阈值过低会误杀长命令（pytest 全量 ~70s/CDP E2E 需大阈值）→ P2 需定义"命令类型→默认时长"基准
- 本任务是"同类扫描"的活示范——若 P1 不 grep 全仓就产出 BDD，等于自己没有贯彻本任务要修的机制 → P1 gate 审查关注点

## 8. 完成后

- P8 gate + READY → 提 PR 合并 main（PR 普通 merge 非 squash，tag 要求）
- **合并前在 PR 里看 CI 结果**（跨平台任务看 matrix 双平台）——pytest/shellcheck/consistency/gate-backstop 全绿才算过
- roadmap 回写关联条目 → done
- 复盘按 agate 自身变更流程归档（合并后在主 checkout 写复盘 + 更新 roadmap/版本）

## 9. 交接确认

- worktree 基线全绿：865 pytest + consistency 0 ERROR（--strict）
- hooks 就位（指向 `~/.agate` 稳定版）、orchestrator 已注册、依赖齐全
- 任务数据就绪：TAG0012 P0-brief + .state.yaml phase=P0
- 交接单位置：`HANDOFF-TAG0012.md`（worktree 根，已 commit）

---

> 模板字段：任务编号、任务标题/一句话、worktree/主 checkout 路径、缺陷清单（文件:行号:问题）、核心约束、验证命令、阶段纪律、风险、完成后动作。复制到 worktree 根目录 `HANDOFF-TAG0012.md` 填写。