# TAG0013 交接单 — agate 脚本一致性批（CHECK 10 + self-gate 触发面 + tech-debt 提醒）

> 本交接单供 worktree session 的 agent 按此启动 TAG0013 任务。
> 任务已 P0 立项（.state.yaml phase=P0，P0-brief.md 已就绪）。
> worktree 已完成构建安装与基线验证，可直接开始 P1。

---

## 1. 你要做什么

**TAG0013**：agate 脚本一致性批。

**一句话**：补上文档脚本名引用漂移 gate（CHECK 10）+ self-gate 触发面补 README/AGENTS + tech-debt 登记提醒——三个都是脚本 + 测试层的一致性补漏。

## 2. 工作区布局（双工作区纪律，违反必出事故）

| 路径 | 角色 | 纪律 |
|------|------|------|
| `/home/kity/oclab/agate/.worktrees/agate-batch` | **本任务 worktree（改造对象）** | 在这里改代码、写阶段产出、跑测试、git commit |
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
- 基线验证：全量 pytest 749 passed + consistency 0 ERROR（--strict）
- commit hook：指向 `~/.agate`（稳定版），worktree commit 自动触发
- orchestrator 注册：`.opencode/agents/orchestrator.md` → `~/.agate/orchestrator-template.md`（符号链接，不拷贝）
- 工作区解析：`agate_common.py` 输出 worktree 自己的 `agate-workspace/`
- 任务数据：TAG0013 P0-brief + .state.yaml phase=P0 在 worktree 的 `agate-workspace/tasks/`

## 3. 任务范围（P0-brief 已锁定，P1 细化 BDD）

### 已核实并确认的缺陷/需求（全部有代码证据，见 P0-brief known_risks）

**RM-AG0015（CHECK 10 文档脚本名引用漂移）**：
- `check-protocol-consistency.py`:238 的 `REF_RE` 只匹配 `docs/assets/scripts` 前缀引用——裸脚本名（phase-cards/rules 全是）完全漏检 → 脚本删/改名后文档漂移，consistency 0 ERROR 照过（v0.46.0 的 phase-cards 26 处过时 .sh 引用是实锤）
- `check-protocol-consistency.py`:52-64 `PROTOCOL_FILES` 不含 `agate/phase-cards/`、`agate/rules/` → 必读卡引用检查降级 WARNING
- `check-protocol-consistency.py`:74 `NARRATIVE_DIRS` 按目录粗分未按文件性质分（2026-08-15 数据核查：archived 62.7% 漂移/已完成 task 42.7% 是历史常态，严格=误报海啸；debt/进行中 task 应严格）
- 已登记 DEBT0001（source: retrospective，关联 RM-AG0015）

**RM-AG0017（self-gate 触发面缺仓库根级文档）**：
- `commit-msg-self-gate.py`:38-40 `_SELF_GATE_RE` 覆盖 `agate/scripts/*`、`agate/*.md`、`agate/*/*.md`、`SELF-GATE.md`——不含 `README.md`/`AGENTS.md` → 改仓库根级协议文档不触发 self-gate WARNING
- 注意：复盘原文称"SELF-GATE.md 不在触发面"是**错误**（实测正则包含它），只补 README/AGENTS，CHANGELOG 豁免

**RM-AG0018 剩余（tech-debt 登记提醒）**：
- DEBT0001 已登记、postmortem-template 已加核对行（主 checkout 2026-08-15 完成）——本任务只做剩余：`check-retrospective.py`（P2.12）输出加一行"复盘发现的新缺口请登记 DEBT/roadmap"提醒（纯提醒不拦截）

### 核心约束（不可违反）
1. **Linux 现状是基线**——现有 749 pytest 测试全绿是回归底线，每个修复都必须保持全绿
2. **Windows 兼容是增量**——本环境（Linux）无法实测 Windows，靠静态修复 + Linux 回归 + CI matrix（pytest -m windows_smoke）兜底。**不要宣称"已实测 Windows"**
3. **不破坏已有协议语义**——CHECK 10 是新增检查，必须是"增量"（只报新漂移），不能误伤现有合法引用（豁免 UPGRADING 对照表/formatters/3 hook 薄壳/count-tests.sh）
4. **范围锁定**——若 P1 分析发现需改动超出 P0-brief 锁定范围（RM-0015/0017/0018），须先停下跟用户确认

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
python3 -m pytest agate/tests/unit/test_check_protocol_consistency.py
python3 -m pytest agate/tests/unit/test_commit_msg_self_gate.py
python3 -m pytest agate/tests/unit/test_check_retrospective.py
```

## 5. 阶段推进纪律（T001 血泪教训）

- **commit 时 phase = 本 commit 产出阶段**：P1 产出 → phase=P1 再 commit；推进 P2 随 P2 产出同 commit。**不要**先写 phase=P2 再 commit P1 产出（pre-commit 会用 P2 gate 检查，P2-design.md 不存在 → 拦截）
- **改脚本走 TDD**：先写失败测试确认红 → 改脚本确认绿（AGENTS.md「改脚本的工作流」）
- **批量机械改动的 TDD 策略**：这类改动每个都写单独测试边际成本高。建议——①先写一个"grep 断言审计"测试作为回归拦截；②批量改动后跑该断言 + 全量 pytest 确认绿。不要为每个小改动单独写测试，也不要跳过测试直接改
- **git 命令加 timeout**、单步串行（AGENTS.md 工具纪律）
- **commit message 含 `wf({Txxx}-P{阶段}):`** 前缀
- **改 `agate/*.md`、`agate/scripts/*.py/.sh`、`agate/phase-cards/*` 触发 SELF-GATE**：commit message 需含 `self-gate-review:` 或 `self-gate-skip:`（否则 commit-msg hook WARNING）。协议文档变更需跑 `check-protocol-consistency.py` 确认无 ERROR
- **只 add 本 task 文件**：不用 `git add -A`（agate-workspace/tasks/ 下有全部 14 个 task，只 add TAG0013 相关 + 本 task 改的协议文件）
- **切分支前确认干净**：本 worktree 串行做 TAG0013→TAG0014→TAG0012，切分支前 `git status` 空才切

## 6. 任务编号与状态

- 任务目录：`agate-workspace/tasks/TAG0013-script-consistency/`（在 worktree 里）
- `.state.yaml`：phase=P0（P1 开始后推进）
- active-tasks.md「待开始」已有 TAG0013 行
- roadmap：RM-AG0015 / RM-AG0017 / RM-AG0018 关联本任务（scheduled）
- **编号体系**：任务用 `{Txxx}`（项目代号 + 动态数字，v2.0 起的 Jira 式编号）。校验器 `^T[A-Z]{2}\d+$`

## 7. 已知风险与止损

- **CHECK 10 豁免清单误伤**：UPGRADING 对照表/formatters/3 hook 薄壳/count-tests.sh 引用旧名是有意保留 → 豁免设计要精确，P1 先画"哪些文档引用哪些脚本名"影响面表 → 止损：豁免路径逐个测试锁定
- **进行中 task 动态分类（RM-AG0015 修复方向 4）**：读 `.state.yaml` phase 区分进行中/已完成，复用 agate-state-get.py → 若实现复杂度高，P2 评估是否本任务做或拆分
- **self-gate 触发面扩展误报**：CHANGELOG 频繁变动 → 豁免设计 + 测试锁定
- **一致性检查现有 ERROR 误伤**：NARRATIVE_DIRS 重组可能影响现有 WARNING/ERROR 分布 → 每步跑 consistency 确认 0 ERROR，基线已锁定（2026-08-15）

## 8. 完成后

- P8 gate + READY → 提 PR 合并 main（PR 普通 merge 非 squash，tag 要求）
- **合并前在 PR 里看 CI 结果**（跨平台任务看 matrix 双平台）——pytest/shellcheck/consistency/gate-backstop 全绿才算过
- roadmap 回写关联条目 → done
- 复盘按 agate 自身变更流程归档（合并后在主 checkout 写复盘 + 更新 roadmap/版本）

## 9. 交接确认

- worktree 基线全绿：749 pytest + consistency 0 ERROR（--strict）
- hooks 就位（指向 `~/.agate` 稳定版）、orchestrator 已注册、依赖齐全
- 任务数据就绪：TAG0013 P0-brief + .state.yaml phase=P0
- 交接单位置：`HANDOFF-TAG0013.md`（worktree 根，已 commit）
