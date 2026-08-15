# TAG0010 + TAG0011 交接单 — agate 全面 Python 化

> 本交接单供 worktree session 的 agent 按此启动。
> 单 worktree 顺序执行 TAG0010 → TAG0011，各自 bump tag，最后统一一个 PR 合并 main。

---

## 1. 你要做什么

**TAG0010**：agate 产品逻辑 Python 化（阶段一）——30 个 sh → py（hook 保留 sh 薄壳），消解 bash 在 Windows MSYS2 模拟层问题。
**TAG0011**：agate 测试框架迁移（阶段二）——58 个 .bats → pytest + 协议文档全量重写 + CI 同步。
**目标**：agate 全面 Python 化（产品 + 测试），hook 保留 sh 薄壳（理由核实充足）。

## 2. 工作区布局（双工作区纪律，违反必出事故）

| 路径 | 角色 | 纪律 |
|------|------|------|
| `/home/kity/oclab/agate/.worktrees/agate-TAG0010` | **本任务 worktree（改造对象）** | 在这里改代码、写阶段产出、跑测试、git commit |
| `/home/kity/oclab/agate`（主 checkout） | 协议本体 + 任务数据 + `~/.agate` 指向 | **禁止改动**。它是稳定版来源，也是 hook 的 AGATE_ROOT |
| `~/.agate`（软链 → 主 checkout/agate） | **稳定版 v0.45.0（开发工具）** | **禁止改动**。跑 gate / 读卡片用它 |

**核心原则（AGENTS.md dogfooding 工作流约定）**：
- **跑 gate 用 `~/.agate`**（稳定版），**改代码/跑测试在 worktree**。
- **⚠️ gate 工具 ≠ 检查对象**：commit hook 用 `~/.agate` 判定；但 `check-protocol-consistency.py` 必须用 worktree 自己的（`python3 agate/scripts/check-protocol-consistency.py`），因为检查对象是 worktree 里的协议文件。
- `bash ~/.agate/scripts/agate-summary.sh` 在 worktree 跑显示主 checkout 上下文（稳定版），不代表 worktree 状态——用 `git log`/`git status` 看。
- **hook 在共享 git 目录**：worktree 的 `.git` 是文件（指向主 checkout `.git`），hook 在主 checkout 的 `.git/hooks/`，worktree commit 时自动触发。

**已完成的 setup**：
- 依赖：bash / python 3.12 / pyyaml / bats 1.10 / shellcheck。
- **共享开发环境已建立**（2026-08-14，解决"各装各的环境乱"）：
  - `~/.venvs/agate-dev/`：单一共享 venv（python 3.12 + pyyaml 6.0.3 + ruff 0.16.3）
  - 所有 worktree 共享此环境（agate 是同一仓库多 checkout，代码一致环境也该一致）
  - **进入 worktree 直接用**（不激活，绝对路径调用）：`~/.venvs/agate-dev/bin/python` / `~/.venvs/agate-dev/bin/ruff`
  - 或激活：`source ~/.venvs/agate-dev/bin/activate`
  - ruff 是 TAG0010 引入的新开发 gate（替代 shellcheck 对 py 的检查；**运行 agate 不需要**）。正式声明文件（pyproject.toml/requirements-dev.txt）由 TAG0010 P1 设计，本环境先就位
- 基线：733 bats 全绿 + consistency 0 ERROR（--strict）
- hook / orchestrator / 工作区解析：全部就位
- 任务数据：TAG0010 + TAG0011 都在 worktree（phase=P0）

## 3. 任务范围

### TAG0010（产品逻辑 Python 化）——P0-brief 已锁定

**关键决策（已确认）**：
- **hook 保留 sh 薄壳**（~15 行/个：shebang + AGATE_ROOT 自定位 + 复制模式 `.agate-root` 恢复 + exec python）。理由已核实充足：git Windows 用 sh.exe 执行 hook、`#!/usr/bin/env bash` 可靠而 `env python3` 不可靠、复制模式恢复须留薄壳。
- **阶段一不做文档全量重写**——文档/CI 同步归 TAG0011。
- 范围：30 个 sh → py（优先 check-gate.sh 488 行 + pre-commit-gate.sh 404 行两个最重）；gate-result.sh + agate-workspace-resolve.sh → agate_common.py。
- 验收：全量 bats 仍绿（bats 调 py）+ consistency 0 ERROR + **ruff 静态检查** + Windows CI 冒烟。

**关键风险（P1 必读）**：
- consistency CHECK 8/9 锚点表硬编码 `.sh` 路径与关键字——py 版必须保留关键字或同步更新锚点表。
- 编码：所有 py 显式 `encoding="utf-8"`（Windows ANSI 代码页坑）。
- Python 3.8+：避免 3.9+/3.10+ 语法（match、str.removeprefix）。
- pyyaml 从可选变强制依赖。
- **同类扫描 + 影响面梳理**：P1 必须梳理 30 个 sh 的调用关系 + 文档引用 + 锚点关键字完整映射表，先画再动手。

### TAG0011（测试框架迁移）——TAG0010 完成后

- 58 个 .bats（727 @test）+ 526 行 helpers → pytest fixture。
- 协议文档全量重写（platform-notes Windows 章节、SETUP、UPGRADING 破坏性章节、dispatch/git-integration bash 引用、CI workflow bats→pytest）。
- 验收：pytest 全绿替代 bats + consistency 0 ERROR + ruff + Windows CI 冒烟 + 扫描器覆盖 .py。

## 4. 执行顺序与版本策略

```
TAG0010: P0 → P1 → ... → P8（bump v0.46.0，tag 推送）→ READY
  ↓ 不合并，继续
TAG0011: P0 → P1 → ... → P8（bump v0.47.0，tag 推送）→ READY
  ↓
最后：统一一个 PR 合并 main（普通 merge --no-ff，保持两个 tag 祖先）
```

- **TAG0010 P8**：bump v0.46.0（README badge + CHANGELOG + UPGRADING 章节——UPGRADING 记 Python 化破坏性变更）
- **TAG0011 P8**：bump v0.47.0
- **注意**：v0.46.0 和 v0.47.0 都是"未合并 main 的 tag"（在 worktree 分支上打）——**最终 PR 必须普通 merge（--no-ff）**，让两个 tag 成为 main 祖先（AGENTS.md release PR 铁律，v0.31.0 事故）。

## 5. 关键验证命令

```bash
# 在 worktree 根执行：
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/   # 全量（阶段一保持绿）
python3 agate/scripts/check-protocol-consistency.py --strict   # 用 worktree 自己的
shellcheck -S warning agate/scripts/*.sh   # 只扫保留的 sh 薄壳
ruff check agate/scripts/*.py   # TAG0010 验收（需先 pip install ruff）
pytest agate/tests/   # TAG0011 目标
bash agate/tests/scripts/count-tests.sh
```

## 6. 阶段推进纪律（T001 血泪教训）

- **commit 时 phase = 本 commit 产出阶段**：不要先写 phase=N+1 再 commit N 产出（pre-commit 用 N+1 gate 拦截）。
- **改脚本走 TDD**：先写失败测试确认红 → 改绿（AGENTS.md「改脚本的工作流」）。
- **git 命令加 timeout**、单步串行（AGENTS.md 工具纪律）。
- **commit message 含 `wf(TAG0010-P{阶段}):` / `wf(TAG0011-P{阶段}):`** 前缀。
- **改 `agate/*.md`、`agate/scripts/*`、`agate/phase-cards/*` 触发 SELF-GATE**：commit message 需含 `self-gate-review:` 或 `self-gate-skip:`（否则 commit-msg hook WARNING）。

## 7. 已知风险与止损

- **30 个 sh 迁移是大工程（3-4 周）**——P1 拆 BDD 按"每脚本一组"组织，分批迁移，每批 bats 绿。
- **consistency 锚点约束**：每迁一个脚本立刻跑 consistency 确认 CHECK 8/9 不报 ERROR（保留关键字或更新锚点表）。
- **测试回归**：阶段一逐脚本迁移 + 每步全量 bats；不批量重写。
- **同类扫描**：P1 全仓 grep（sh 调用关系 / 文档引用 / 锚点关键字），实例全入 BDD。用户明确：不愿意一轮一轮来回改。
- **TAG0011 727 个 bats 断言重写是高回归风险**——按模块分批，每批 pytest 绿 + 原 bats 对照。

## 8. 完成后

- 两个 task 全部 READY → 统一一个 PR 合并 main（普通 merge --no-ff，保持 v0.46.0 + v0.47.0 tag 祖先）。
- **合并前在 PR 里看 CI 结果**（bats 阶段一 / pytest 阶段二 / consistency / ruff / shellcheck / Windows 冒烟）全绿才算过。
- roadmap 回写关联条目 → done。
- 复盘按 agate 自身变更流程归档。

## 9. 交接确认

- worktree 基线全绿：733 bats + consistency 0 ERROR（--strict）
- hooks 就位、orchestrator 已注册、依赖齐全（ruff 待装）
- 任务数据就绪：TAG0010 + TAG0011 都在 worktree（phase=P0）
- 交接单位置：`HANDOFF-TAG0010-0011.md`（worktree 根，已 commit）

---

> 双任务交接单：TAG0010（产品逻辑 Python 化，bump v0.46.0）→ TAG0011（测试迁移，bump v0.47.0）→ 统一 PR 合并。关键文件：P0-brief（TAG0010/TAG0011）+ 分析报告 docs/reviews/agate-python-migration-analysis-20260814.md。
