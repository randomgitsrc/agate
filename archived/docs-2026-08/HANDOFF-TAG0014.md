# TAG0014 交接单 — agate 派发编排机制（全阶段，RM-AG0016）

> 本交接单供 worktree session 的 agent 按此启动 TAG0014 任务。
> 任务已 P0 立项（.state.yaml phase=P0，P0-brief.md 已就绪）。
> worktree 已完成构建安装与基线验证，可直接开始 P1。
> **有 approved plan（agate-workspace/plans/agate-dispatch-orchestration-20260815.md，plan-eng-review 三轮评审通过）——作为参考输入，不替代任务流程。**

---

## 1. 你要做什么

**TAG0014**：agate 派发编排机制（全阶段）。

**一句话**：subagent 派发工作量评估 + 五模式编排（单发/静态拆批/并行/先理解后拆/串行链）+ 并行规则统一，解决"工作量高时单 subagent 过载卡死"（TAG0010 批次 0 实证）。

## 2. 工作区布局（双工作区纪律，违反必出事故）

| 路径 | 角色 | 纪律 |
|------|------|------|
| `/home/kity/oclab/agate/.worktrees/agate-TAG0014` | **本任务 worktree（改造对象）** | 在这里改代码、写阶段产出、跑测试、git commit |
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
- 依赖齐全：bash / python3 / pyyaml / pytest（python3 -m pytest）/ shellcheck
- 基线验证：全量 pytest **768 passed** + consistency **0 ERROR**（含 TAG0013 新增的 CHECK 10）
- commit hook：指向 `~/.agate`（稳定版），worktree commit 自动触发
- orchestrator 注册：`.opencode/agents/orchestrator.md` → `~/.agate/orchestrator-template.md`（符号链接，不拷贝）
- 工作区解析：`agate_common.py` 输出 worktree 自己的 `agate-workspace/`
- 任务数据：TAG0014 P0-brief + .state.yaml phase=P0 在 worktree 的 `agate-workspace/tasks/`
- **参考 plan**：`agate-workspace/plans/agate-dispatch-orchestration-20260815.md`（已批准，含字段契约 + 6 Task + 验收标准）

## 3. 任务范围（P0-brief 已锁定，P1 细化 BDD）

### ⚠️ 阶段完整性声明（必须遵守）

**有 approved plan ≠ 裁剪阶段。** 本任务仍走完整 P0-P8。P1/P2 须产出本任务自己的需求基线与设计（可引用 plan 内容，不可跳过 gate）。plan 是参考输入：
- plan 的字段契约（`dispatch_plan:` frontmatter 单行 flow YAML + op `dispatch_plan` 子进程读取 + JSON 输出 + **不入 frontmatter-check schema**）是 P2 设计必须遵循的（B3 修复结论）
- plan 的 6 个 Task 是实施参考，P2 设计时按阶段组织
- **plan 评审 ≠ 本任务 gate**：plan 审的是"方案"，task gate 验的是"本次任务的实际产出与验收"，两者不互换

### 已核实并确认的缺陷/需求（全部有代码证据，见 P0-brief known_risks）

**RM-AG0016（派发编排机制）**：
- TAG0010 批次 0 卡死（用户中止）：协议只有"任务粒度指引"（dispatch-protocol.md L639-663，限输入/产出数量），无工作量评估方法、无编排模式定义、无并行规则；P1/P2 无任何编排机制
- 并行规则分散且缺：P3/P4/P5/P6 各卡片有独立"按包拆分并行"（P3-tdd.md:74 / P4-implementation.md:94 / P5-verification.md:113 / P6-acceptance.md:147），无统一机制；无并行上限、无并行失败处理、无共享文件统一约束（仅 P4 有）
- 模式 4 先理解后拆（用户扩展需求）：侦察 subagent 读全貌产出拆分方案 → 按方案派执行（并行/串行）→ 合并（轻量拼装主 Agent/单 subagent；重量整合派整合 subagent）。不局限于 P4，全阶段适用
- 落地：dispatch-protocol 新增「派发编排机制」权威节 + P2-design.md 新增 `dispatch_plan:` 机器字段 + 各阶段卡片统一引用 + architect.md 批次设计节 + dispatch-prompt.md 粒度兜底

### 核心约束（不可违反）
1. **Linux 现状是基线**——现有 768 pytest 测试全绿是回归底线，每个修复都必须保持全绿
2. **Windows 兼容是增量**——本环境（Linux）无法实测 Windows，靠静态修复 + Linux 回归 + CI matrix（pytest -m windows_smoke）兜底。**不要宣称"已实测 Windows"**
3. **不破坏已有协议语义**——`dispatch_plan:` 是可选字段（缺字段向后兼容，行为等同现状）；CHECK 10（TAG0013 新增）不能被本任务改动破坏
4. **范围锁定**——若 P1 分析发现需改动超出 P0-brief 锁定范围（RM-AG0016 五模式 + 并行规则 + dispatch_plan 字段），须先停下跟用户确认

## 4. 关键验证命令

```bash
# 在 worktree 根执行：

# 全量测试（必须全绿才算过）
python3 -m pytest agate/tests/

# 一致性（0 ERROR 才行；--strict 让 WARNING 也阻断）
# ⚠️ 必须用 worktree 自己的脚本（检查对象是 worktree 里的协议文件），不要用 ~/.agate 的
python3 agate/scripts/check-protocol-consistency.py --strict

# shellcheck（3 hook 薄壳）
shellcheck -S warning agate/scripts/*.sh

# 测试计数（验证文档没漂移）
bash agate/tests/scripts/count-tests.sh

# 单脚本测试（改哪个跑哪个，TDD 先红后绿）
python3 -m pytest agate/tests/unit/test_dispatch_orchestration.py
python3 -m pytest agate/tests/unit/test_check_gate.py
python3 -m pytest agate/tests/unit/test_check_protocol_consistency.py
```

## 5. 阶段推进纪律（T001 血泪教训）

- **commit 时 phase = 本 commit 产出阶段**：P1 产出 → phase=P1 再 commit；推进 P2 随 P2 产出同 commit。**不要**先写 phase=P2 再 commit P1 产出（pre-commit 会用 P2 gate 检查，P2-design.md 不存在 → 拦截）
- **改脚本走 TDD**：先写失败测试确认红 → 改脚本确认绿（AGENTS.md「改脚本的工作流」）
- **git 命令加 timeout**、单步串行（AGENTS.md 工具纪律）
- **commit message 含 `wf({Txxx}-P{阶段}):`** 前缀
- **改 `agate/*.md`、`agate/scripts/*.py/.sh`、`agate/phase-cards/*` 触发 SELF-GATE**：commit message 需含 `self-gate-review:` 或 `self-gate-skip:`（否则 commit-msg hook WARNING）。协议文档变更需跑 `check-protocol-consistency.py` 确认无 ERROR
- **只 add 本 task 文件**：不用 `git add -A`（agate-workspace/tasks/ 下有全部 task 目录，只 add TAG0014 相关 + 本 task 改的协议文件）
- **切分支前确认干净**：本 worktree 串行做 TAG0014→TAG0012，切分支前 `git status` 空才切

## 6. 任务编号与状态

- 任务目录：`agate-workspace/tasks/TAG0014-dispatch-orchestration/`（在 worktree 里）
- `.state.yaml`：phase=P0（P1 开始后推进）
- active-tasks.md「待开始」已有 TAG0014 行
- roadmap：RM-AG0016 关联本任务（scheduled）
- **编号体系**：任务用 `{Txxx}`（项目代号 + 动态数字，v2.0 起的 Jira 式编号）。校验器 `^T[A-Z]{2}\d+$`

## 7. 已知风险与止损

- **dispatch_plan 字段契约复杂度**：frontmatter 单行 flow YAML + op 子进程读取 + JSON 输出 + 不入 schema（plan B3 已定）——实现细节多，P2 严格按 plan 字段契约，不要重新发明。止损：测试锁定 8 用例（5 正 + 3 负）
- **P1-P8 全阶段卡改动面大**：dispatch-protocol + P1-P8 卡 + architect + 派发模板 + check-gate.py + agate-md-field-get.py——改动分散，每步跑 consistency 确认 0 ERROR。止损：按 plan 6 Task 组织，每 Task 独立 commit
- **模式 4（先理解后拆）是新机制**：侦察→执行→合并三阶段无既有实现——P2 设计需明确合并语义（轻量/重量划分）。止损：plan 已定义，P2 细化
- **与 TAG0013 的 CHECK 10 交互**：本任务改协议文档（phase-cards/dispatch-protocol），CHECK 10（TAG0013 新增）会扫描这些文档的脚本名引用——改文档时注意脚本名引用合规。止损：每步跑 consistency
- **改动触发 self-gate（改 agate/*.md + scripts/*.py）**：按 SELF-GATE.md 流程：派发 protocol-alignment-review + commit message 带 `self-gate-review:`

## 8. 完成后

- P8 gate + READY → 提 PR 合并 main（PR 普通 merge 非 squash，tag 要求）
- **合并前在 PR 里看 CI 结果**（跨平台任务看 matrix 双平台）——pytest/shellcheck/consistency/gate-backstop 全绿才算过
- roadmap 回写关联条目（RM-AG0016）→ done
- 复盘按 agate 自身变更流程归档（合并后在主 checkout 写复盘 + 更新 roadmap/版本）

## 9. 交接确认

- worktree 基线全绿：768 pytest + consistency 0 ERROR（--strict）
- hooks 就位（指向 `~/.agate` 稳定版）、orchestrator 已注册、依赖齐全
- 任务数据就绪：TAG0014 P0-brief + .state.yaml phase=P0
- 参考 plan 就绪：agate-workspace/plans/agate-dispatch-orchestration-20260815.md（approved）
- 交接单位置：`HANDOFF-TAG0014.md`（worktree 根，已 commit）
