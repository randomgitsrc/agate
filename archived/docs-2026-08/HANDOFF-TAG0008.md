# TAG0008 交接单 — agate 版本管理机制（v1）

> 本交接单供 worktree session 的 agent 按此启动 TAG0008 任务。
> 任务已 P0 立项（.state.yaml phase=P0，P0-brief.md 已就绪）。
> worktree 已完成构建安装与基线验证，可直接开始 P1。

---

## 1. 你要做什么

**TAG0008**：agate 版本管理机制（v1）。

**一句话**：让不同项目可以用不同版本的 agate（多版本共存 + 项目锁定 + 程序化安装/升级 + 内网离线部署包），解决"~/.agate 唯一、pull 被动升级打断实施"。

## 2. 工作区布局（双工作区纪律，违反必出事故）

| 路径 | 角色 | 纪律 |
|------|------|------|
| `/home/kity/oclab/agate/.worktrees/agate-TAG0008` | **本任务 worktree（改造对象）** | 在这里改代码、写阶段产出、跑测试、git commit |
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
- 依赖齐全：bash / python3 / pyyaml / pytest（python3 -m pytest）/ shellcheck / git
- 基线验证：全量 pytest **780 passed** + consistency **0 ERROR**（--strict）
- commit hook：指向 `~/.agate`（稳定版），worktree commit 自动触发
- orchestrator 注册：`.opencode/agents/orchestrator.md` → `~/.agate/orchestrator-template.md`（符号链接，不拷贝）
- 工作区解析：`agate_common.py` 输出 worktree 自己的 `agate-workspace/`
- 任务数据：TAG0008 P0-brief + .state.yaml phase=P0 在 worktree 的 `agate-workspace/tasks/`

## 3. 任务范围（P0-brief 已锁定，P1 细化 BDD）

### 已核实并确认的缺陷/需求（全部有代码证据，见 P0-brief known_risks）

**核心问题**：`~/.agate` 是单一软链 → git pull 后所有项目被动升级，进行中项目被打断。hook 通过软链自动跟随，无法按项目隔离。

**设计稿**：`archived/docs-2026-08/plans/agate-version-management-20260813.md`（§8 决策定稿 + v1/v2 范围）。⚠️ **注意**：设计稿 §3.2 L61-62 写"版本工具用 .sh（复用 TAG0004 bash 适配）"——**已过时**（TAG0010/0011 已全量 Python 化）。本任务按 **Python 路线** 实现（install/resolve/summary 用 .py，hook 入口保留 sh 薄壳）。

**v1 完整范围（2026-08-16 用户确认 + P0-brief 更新）**：

**6 组件**：
1. **agate-install**：`agate-install`（无参数）= 装最新（latest 指针）；`agate-install v0.48.0` = 装指定版本（repo clone + worktree add tag）；`agate-install --uninstall v0.43.0` = 删版本目录 + 清理指针；`agate-install --check` = 环境探测（python3/pyyaml/git/bash）
2. **agate-resolve**：读项目 `.agate-version`（asdf 模式，cwd 向上找）→ 映射版本 → 得 AGATE_ROOT；无声明回退 ~/.agate/current（默认→latest）；AGATE_ROOT env 显式覆盖优先级最高
3. **hook 解析入口**：install-hook 装固定入口 resolve-entry → 运行时读 .agate-version → exec 对应版本 gate 逻辑。项目 A 锁旧版、项目 B 用新版互不干扰，切版本不用重装 hook
4. **summary 集成**：显示当前项目解析到的版本 + 原因（.agate-version 或 global current）
5. **agate-pack-offline.py**（外网打包器）：`agate-pack-offline.py v0.48.0 [--platform linux-x86_64|windows-x86_64] [--include-python] [--include-pillow]` → 平台标签 bundle（agate tag + wheels（pyyaml 必装/Pillow 可选，`pip download --platform <目标>` 按目标平台拉）+ 嵌入式 Python 可选 + manifest.json（含 checksum sha256））
6. **install-offline.py**（内网一键安装器）：读 manifest.json 核对平台（不匹配警告防错装）+ 校验 checksum → 装 wheels（`--no-index --find-links wheels/`）→ 建 ~/.agate/vX.Y.Z/ → hook/orchestrator 指向（Windows 复制模式/Linux 软链）→ 验证（agate-summary）

**其他需求**：
- 形态 2（用户确认）：安装即建版本目录 `~/.agate/vX.Y.Z/`（git worktree 检出 tag），latest 是纯指针→最新发布版
- 项目锁定（asdf 模式）：`agate: v0.43.0` 精确锁定；v1 只支持精确版本，`>=` 折中留 v2
- 环境探测 + agent 向 setup 指引：`agate-install --check` + SETUP.md「环境准备（agent 执行）」节（写给 agent：探测命令 exit code 可判 → 分平台修复 → 验证闭环）。**不自动装系统级依赖**（Windows 自动配置不可行）

**v2 边界（本任务不做）**：`>=` 版本折中、版本列表扩展、离线包自动更新/镜像分发、离线首次安装

### 核心约束（不可违反）
1. **Linux 现状是基线**——现有 780 pytest 测试全绿是回归底线，每个修复都必须保持全绿
2. **Windows 兼容是增量**——本环境（Linux）无法实测 Windows，靠静态修复 + Linux 回归 + CI matrix（pytest -m windows_smoke）兜底。**不要宣称"已实测 Windows"**。Windows 相关逻辑（软链退化/复制模式/PYTHONUTF8/盘符路径）复用 platform-notes 已有先例
3. **不破坏已有协议语义**——`~/.agate` 软链保留（向后兼容）；无 .agate-version 的项目 resolve 回退 current；AGATE_ROOT env 覆盖优先级最高；gate 逻辑（check-gate.py 等）本身不改，只改"如何解析到哪个版本"
4. **resolve 失败必须回退稳**——不能因解析失败静默禁用 gate（回退 current）
5. **范围锁定**——若 P1 分析发现需改动超出 P0-brief 锁定范围，须先停下跟用户确认

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
python3 -m pytest agate/tests/unit/test_agate_version_install.py   # 新增
python3 -m pytest agate/tests/unit/test_agate_version_resolve.py   # 新增
python3 -m pytest agate/tests/unit/test_agate_summary.py
python3 -m pytest agate/tests/unit/test_install_hook.py
```

## 5. 阶段推进纪律（T001 血泪教训）

- **commit 时 phase = 本 commit 产出阶段**：P1 产出 → phase=P1 再 commit；推进 P2 随 P2 产出同 commit。**不要**先写 phase=P2 再 commit P1 产出（pre-commit 会用 P2 gate 检查，P2-design.md 不存在 → 拦截）
- **改脚本走 TDD**：先写失败测试确认红 → 改脚本确认绿（AGENTS.md「改脚本的工作流」）
- **git 命令加 timeout**、单步串行（AGENTS.md 工具纪律）
- **commit message 含 `wf({Txxx}-P{阶段}):`** 前缀
- **改 `agate/*.md`、`agate/scripts/*.py/.sh`、`agate/phase-cards/*` 触发 SELF-GATE**：commit message 需含 `self-gate-review:` 或 `self-gate-skip:`（否则 commit-msg hook WARNING）。协议文档变更需跑 `check-protocol-consistency.py` 确认无 ERROR
- **只 add 本 task 文件**：不用 `git add -A`（agate-workspace/tasks/ 下有全部 task 目录，只 add TAG0008 相关 + 本 task 改的协议文件）
- **同类扫描强制**：本任务涉及 install.sh/install-hook.py/pre-commit-gate.py/agate-summary.py/SETUP/README/UPGRADING 多文件联动——P1 必须全仓 grep `~/.agate` 消费点建影响面表，确保改一处同步所有联动点。用户明确：不愿意一轮一轮来回改

## 6. 任务编号与状态

- 任务目录：`agate-workspace/tasks/TAG0008-version-management/`（在 worktree 里）
- `.state.yaml`：phase=P0（P1 开始后推进）
- active-tasks.md「待开始」已有 TAG0008 行
- roadmap：本任务无关联 RM 条目（直接立项任务，非从 RM 拆出）
- **编号体系**：任务用 `{Txxx}`（项目代号 + 动态数字，v2.0 起的 Jira 式编号）。校验器 `^T[A-Z]{2}\d+$`

## 7. 已知风险与止损

- **hook 改造影响所有下游项目**：resolve 失败必须回退稳（回退 current），不能因解析失败静默禁用 gate → 止损：resolve 单元测试锁定失败回退路径
- **~/.agate 从'单软链'到'目录'的迁移影响存量用户**：需迁移脚本/文档，install.sh 保留兼容 → 止损：向后兼容测试（旧用法不破坏）
- **Windows 软链退化**：latest/current 指针在无符号链接权限时用复制/配置文件模式 → 止损：复用 platform-notes 先例 + windows_smoke 测试
- **内网部署包平台/校验复杂度**：manifest.json 平台核对 + checksum + wheels 按目标平台拉 → 止损：P2 严格设计，打包/安装分离测试
- **离线首次安装（无网络装从未装过版本）**：超出 v1（需网络拉 tag），明确边界 → 止损：文档声明，不实现
- **改动触发 self-gate**：涉及 scripts/*.py + SETUP/README/UPGRADING → commit message 带 `self-gate-review:`，派发 protocol-alignment-review

## 8. 完成后

- P8 gate + READY → 提 PR 合并 main（PR 普通 merge 非 squash，tag 要求）
- **合并前在 PR 里看 CI 结果**（跨平台任务看 matrix 双平台）——pytest/shellcheck/consistency/gate-backstop 全绿才算过
- roadmap 回写（本任务无关联 RM，标注任务完成）
- 复盘按 agate 自身变更流程归档（合并后在主 checkout 写复盘 + 更新 roadmap/版本）

## 9. 交接确认

- worktree 基线全绿：780 pytest + consistency 0 ERROR（--strict）
- hooks 就位（指向 `~/.agate` 稳定版）、orchestrator 已注册、依赖齐全
- 任务数据就绪：TAG0008 P0-brief + .state.yaml phase=P0
- 设计稿就绪：archived/docs-2026-08/plans/agate-version-management-20260813.md（注意 §3.2 .sh 路线已过时，按 Python）
- 交接单位置：`HANDOFF-TAG0008.md`（worktree 根，已 commit）
