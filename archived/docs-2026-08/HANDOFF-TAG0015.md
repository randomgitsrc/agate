# TAG0015 交接单 — agate 复盘与反馈机制统一

> 本交接单供 worktree session 的 agent 按此启动 TAG0015 任务。
> 任务已 P0 立项（.state.yaml phase=P0，P0-brief.md 已就绪）。
> worktree 已完成构建安装与基线验证，可直接开始 P1。

---

## 1. 你要做什么

**TAG0015**：agate 复盘与反馈机制统一（RM-AG0020 + RM-AG0021）。

**一句话**：把"复盘"和"跨项目反馈"从临场发挥变成协议机制——复盘模板进协议本体（正文结构 + 归因分层 + 事实依据 + 项目资产沉淀）、复盘产出归 task 产物、check-retrospective 路径同步、orchestrator-log 扩展决策依据 + 会话 checkpoint、复盘→agate 项目组反馈（结构化 agate 反馈节 + 匿名化 + 开关 + 触发方式修正）。AG0020 是核心（复盘机制），AG0021 建立在 AG0020 的结构化产出上（反馈机制）。

## 2. 工作区布局（双工作区纪律，违反必出事故）

| 路径 | 角色 | 纪律 |
|------|------|------|
| `/home/kity/oclab/agate/.worktrees/agate-TAG0015` | **本任务 worktree（改造对象）** | 在这里改代码、写阶段产出、跑测试、git commit |
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
- 基线验证：全量 pytest 893 全绿（785 unit + 108 regression/integration/sanity）+ consistency 0 ERROR（--strict）
- commit hook：指向 `~/.agate`（稳定版），worktree commit 自动触发
- orchestrator 注册：`.opencode/agents/orchestrator.md` → `~/.agate/orchestrator-template.md`（符号链接，不拷贝）
- 工作区解析：`agate_common.py` 输出 worktree 自己的 `agate-workspace/`
- 任务数据：TAG0015 P0-brief + .state.yaml phase=P0 在 worktree 的 `agate-workspace/tasks/`

## 3. 任务范围（P0-brief 已锁定，P1 细化 BDD）

### 已核实并确认的缺陷/需求（全部有代码证据，见 P0-brief known_risks）

**RM-AG0020 复盘机制统一（八项残缺，核心）**：
- ①**模板缺正文结构**——postmortem-template.md（docs/reviews/）只有机制触发核对清单，无复盘正文（做得好的/发现的问题/改进措施）→ 模板定义正文结构：事实基线/做得好的/发现的问题/改进措施
- ②**内容无价值标准**——易沦为流水账/自我表扬 → 模板定义"什么值得写"：机制缺口 + 可复用模式 + 可行动问题
- ③**标的矛盾**——check-retrospective.py（P2.12）只在异常模式（retry 超限/SCOPE+/override）提醒 → 统一触发：异常强制/发现机制缺口强制/高价值建议
- ④**路径矛盾**——复盘是 task 产物应放 `tasks/{Txxx}/retrospective.md`；实际先例在 docs/reviews/；check-retrospective 提示 docs/releases/——三处不一致 → 统一到 tasks/{Txxx}/，存量迁移/标记
- ⑤**归因纪律缺失**——不区分执行错误 vs 机制缺口 → 每条问题标归因层面
- ⑥**产出流向缺失**——机制缺口应流向 roadmap（RM）/DEBT → 强制约定
- ⑦**事实依据缺失**——因果链在 session，compact 就丢 → 三层事实源 L1/L2/L3，orchestrator-log 扩展"决策+依据"
- ⑧**时机前置**——L2 过程摘要在任务完成时立即落盘，正式复盘在 merge main 后基于摘要写

**RM-AG0020 项目资产沉淀（用户 2026-08-17 补充）**：
- 复盘"做得好的/可复用模式"节区分两类资产并明确流向——①agate 机制可复用 → RM-AG0021 ②项目可复用资产（临时命令/脚本如 make/run-e2e、经验教训 xdist flaky/timeout）→ 项目基础设施（Makefile/scripts）+ 项目记忆（agents.md/project.md）。模板强制问"本次产生的临时命令/脚本/经验，哪些该沉淀为项目固定资产？沉淀到哪？"

**RM-AG0021 跨项目反馈机制（增量，建立在 AG0020 结构化产出上）**：
- 其他项目用 agate 复盘归因到 agate 层的问题对 agate 项目组有价值但无回馈通道 → ①复盘文档加 frontmatter 机器字段（mechanism_issues/execution_issues/feedback_ready）+ `## agate 反馈` 结构化节 ②agate-feedback.py 提取+匿名化+JSON+提示提交（手动触发）③AGATE_FEEDBACK 开关默认 off（opt-in 隐私优先）④回传通道（issue/PR）
- **触发方式修正（TPV0093 实证）**：回馈是用户/agate 项目组推动（要求外部项目复盘时提醒登记反馈节），非项目自发回馈。不要假设"项目自动回馈"

### 核心约束（不可违反）
1. **Linux 现状是基线**——现有 893 pytest 测试全绿是回归底线，每个修复都必须保持全绿
2. **Windows 兼容是增量**——本环境（Linux）无法实测 Windows，靠静态修复 + Linux 回归 + CI matrix 兜底。**不要宣称"已实测 Windows"**
3. **AG0020 核心 + AG0021 增量两阶段**——避免一次过大；AG0021 依赖 AG0020 结构化产出
4. **本任务是"机制设计"不是"替项目写复盘"**——定义模板/路径/触发/脚本；实际提炼是项目侧行为，不由本任务做
5. **范围锁定**——若 P1 分析发现需改动超出 P0-brief 锁定范围，须先停下跟用户确认
6. **【强制要求】同类扫描 + 影响面梳理**——P1 必须 grep 全仓 '复盘/retrospective/postmortem/orchestrator-log' 引用点（check-retrospective.py 提示、交接单、AGENTS.md、state-machine.md、复盘模板、docs/reviews/ 存量复盘），建影响面表。用户明确：不愿意一轮一轮来回改

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
- **commit message 含 `wf(TAG0015-P{阶段}):` 前缀**
- **改 `agate/*.md`、`agate/scripts/*.py/.sh`、`agate/phase-cards/*` 触发 SELF-GATE**：commit message 需含 `self-gate-review:` 或 `self-gate-skip:`（否则 commit-msg hook WARNING）。协议文档变更需跑 `check-protocol-consistency.py` 确认无 ERROR。本任务改复盘模板/check-retrospective/state-machine → 大概率需要 self-gate-review

## 6. 任务编号与状态

- 任务目录：`agate-workspace/tasks/TAG0015-retrospective-feedback/`（在 worktree 里）
- `.state.yaml`：phase=P0（P1 开始后推进）
- active-tasks.md「待开始」已有 TAG0015 行
- roadmap：RM-AG0020/RM-AG0021 关联本任务（scheduled）
- **编号体系**：任务用 `TAG0015`（项目代号 + 动态数字）。校验器 `^T[A-Z]{2}\d+$`

## 7. 已知风险与止损

- postmortem-template.md 现在 docs/reviews/（项目资料），应进协议本体 agate/assets/templates/（retrospective-template.md）→ 存量复盘文档引用旧位置，迁移需处理存量 → P1 影响面梳理必须覆盖
- 复盘产出位置从 docs/reviews/ 迁到 tasks/{Txxx}/retrospective.md → 存量复盘（TAG0008/0010-11/0013/0014 等）需迁移或标记旧布局 → P1/P2 设计迁移策略
- orchestrator-log 扩展（决策+依据）+ 会话 checkpoint 是新机制 → 需定义落盘时机/内容/防 compact 策略 → P2 设计关键决策
- 反馈机制（AG0021）依赖 AG0020 的复盘结构化产出 → 按 AG0020 核心 + AG0021 增量两阶段做
- 项目资产沉淀是"复盘模板设计"而非"沉淀本身" → 本任务定义模板要求，实际提炼是项目侧行为
- 反馈触发方式：TPV0093 实证回流是用户推动非项目自发 → 按"用户推动 + 反馈节引导"设计，不假设自动回馈
- 改动触发 SELF-GATE（改 agate/assets/templates/ + state-machine.md + check-retrospective.py）→ commit message 需 self-gate-review

## 8. 完成后

- P8 gate + READY → 提 PR 合并 main（PR 普通 merge 非 squash，tag 要求）
- **合并前在 PR 里看 CI 结果**（跨平台任务看 matrix 双平台）——pytest/shellcheck/consistency/gate-backstop 全绿才算过
- roadmap 回写关联条目 → done
- 复盘按 agate 自身变更流程归档（合并后在主 checkout 写复盘 + 更新 roadmap/版本）——注意：本任务做完后，复盘本身要按新机制执行（自举）

## 9. 交接确认

- worktree 基线全绿：893 pytest + consistency 0 ERROR（--strict）
- hooks 就位（指向 `~/.agate` 稳定版）、orchestrator 已注册、依赖齐全
- 任务数据就绪：TAG0015 P0-brief + .state.yaml phase=P0
- 交接单位置：`HANDOFF-TAG0015.md`（worktree 根，已 commit）

---

> 模板字段：任务编号、任务标题/一句话、worktree/主 checkout 路径、缺陷清单（文件:行号:问题）、核心约束、验证命令、阶段纪律、风险、完成后动作。复制到 worktree 根目录 `HANDOFF-TAG0015.md` 填写。