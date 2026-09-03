# TAG0031 交接单 — DEBT 存量修复批（DEBT0002/0003/0004/0007/0016/0017/0018）

> 本交接单供 worktree session 的 agent 按此启动 TAG0031 任务。
> 任务已 P0 立项（.state.yaml phase=P0，P0-brief.md 已就绪）。
> worktree 已完成构建安装与基线验证，可直接开始 P1。

---

## 1. 你要做什么

**TAG0031**：DEBT 存量修复批。

**一句话**：批量关闭 7 条历史遗留 open DEBT——版本管理域 3 条（hash 双实现合并/信任边界/扫描限流提示）+ 测试隔离 1 条 + check-gate.py 健壮性 3 条。全部低风险脚本健壮性修复，无新机制设计。

## 2. 工作区布局（双工作区纪律，违反必出事故）

| 路径 | 角色 | 纪律 |
|------|------|------|
| `/home/kity/oclab/agateon/.worktrees/agate-TAG0031` | **本任务 worktree（改造对象）** | 在这里改代码、写阶段产出、跑测试、git commit |
| `/home/kity/oclab/agateon`（主 checkout） | 协议本体 + 任务数据 + `~/.agate` 指向 | **禁止改动**。它是稳定版来源，也是 hook 的 AGATE_ROOT |
| `~/.agate`（软链 → 主 checkout/agate） | **稳定版（开发工具）** | **禁止改动**。跑 gate / 读卡片用它 |

**核心原则（AGENTS.md T001 约定沿用）**：
- **跑 gate 用 `~/.agate`**（稳定版），**改代码/跑测试在 worktree**。
- commit 时 pre-commit hook 用 `~/.agate/scripts/pre-commit-gate.sh` 判定。
- **⚠️ gate 工具 ≠ 检查对象**：`check-protocol-consistency.py` **必须用 worktree 自己的**；编排/派发类工具用 `~/.agate/scripts/` 稳定版（TAG0016 教训）。
- **hook 在共享 git 目录**：worktree commit 时 hook 自动触发。

**已完成的 setup**：
- 依赖齐全（bash/python3.12/pyyaml/pytest/shellcheck/ruff）
- 基线验证：consistency 0 ERROR（--strict-errors-only）
- orchestrator 注册：`.opencode/` + `.claude/` 软链 → `~/.agate/orchestrator-template.md`
- 工作区解析：`agate_common.py` 输出 worktree 自己的 agate-workspace（须在 worktree 目录内执行）
- 任务数据：TAG0031 P0-brief + .state.yaml phase=P0

## 3. 任务范围（P0-brief 已锁定，P1 细化 BDD）

### 已核实并确认的缺陷/需求（全部有代码证据，见 P0-brief + DEBT 条目）

**DEBT0002（版本管理域，medium）**：离线包 compute_sha256 双实现漂移——pack/install 两侧各自实现，未共享 agate_common。修复 = `agate_common.py` 补目录 hash 工具（compute_sha256），pack/install 两侧改 import 共享。

**DEBT0003（medium）**：离线 manifest 未签名——checksum 防损坏不防整包替换。修复 = 文档明示信任边界（bundle 提供者可信）；如需防整包替换引入签名（minisign/GPG）校验 manifest。若签名评估成本过高，文档明示信任边界即关闭（签名作为 backlog）。

**DEBT0004（medium）**：卸载引用保护扫描限流（mtime 365 天/深度 ≤4/跳隐藏目录）漏扫旧引用且无提示。修复 = 限流边界命中时 stderr WARNING 提示可能漏扫。

**DEBT0007（测试隔离，medium）**：test_check_pruning.py 部分用例依赖真实 git 暂存区而非隔离 fixture，大体量协议自身任务会误报。修复 = `_staged_source_count` 用例改隔离临时 git 仓库（tmp_path + git init），不依赖真实暂存区。

**DEBT0016（check-gate.py 健壮性，low）**：gate_p4 的 CODE-MAP.md 路径用本地"task_dir 向上两级"推导，未调 resolve_workspace 权威函数。修复 = import agate_common 调 resolve_workspace，与其余脚本同一权威解析源 + 补边界场景回归测试。

**DEBT0017（low）**：gate_p4「## 新增文件核对表」子串判定在自指/dogfooding 场景假阴性。修复 = 改整行/标题级判定。

**DEBT0018（low）**：agate_common import 降级 stub 返回 0/空——安装破损边缘呈 false-PASS。修复 = 降级 stub 改显式失败（fail-closed）：关键读取器不可导入时报错而非返回 0/空。

### 核心约束（不可违反）
1. **Linux 现状是基线**——全量 pytest 全绿是回归底线
2. **不破坏已有协议语义**——check-gate.py 是核心 gate 消费方，改判定逻辑先补失败测试（TDD）；不改返回约定（1/2 exit 语义）
3. **fail-closed 是行为变更**——降级 stub 改显式失败前 grep 消费方确认无合法场景依赖降级静默
4. **测试隔离改造后任意 basetemp 全绿**（RM-AG0041 教训）
5. **范围锁定**——若 P1 分析发现需改动超出 P0-brief 锁定范围，须先停下跟用户确认

## 4. 关键验证命令

```bash
# 在 worktree 根执行：

# 全量测试（必须全绿才算过；分片 + -n auto 并行提速）
python3 -m pytest agate/tests/unit/ -n auto
python3 -m pytest agate/tests/regression/ -n auto
python3 -m pytest agate/tests/integration/ -n auto

# 一致性（0 ERROR 才行；必须用 worktree 自己的脚本）
python3 agate/scripts/check-protocol-consistency.py --strict-errors-only

# shellcheck
shellcheck -S warning agate/scripts/*.sh

# 测试计数（验证文档没漂移）
bash agate/tests/scripts/count-tests.sh

# 单脚本测试（改哪个跑哪个，TDD 先红后绿）
python3 -m pytest agate/tests/unit/test_{具体测试文件}.py

# 离线包流程回归（DEBT0002/3/4 验收）：pack → install → 卸载全流程
python3 agate/scripts/agate-install.py --help  # 先确认入口；具体流程按 P1 分析
```

## 5. 阶段推进纪律（T001 血泪教训）

- **commit 时 phase = 本 commit 产出阶段**：P1 产出 → phase=P1 再 commit；推进 P2 随 P2 产出同 commit。**不要**先写 phase=P2 再 commit P1 产出
- **改脚本走 TDD**：先写失败测试确认红 → 改脚本确认绿
- **批量机械改动的 TDD 策略**：先写"grep 断言审计"测试作为回归拦截；批量改动后跑该断言 + 全量 pytest 确认绿
- **git 命令加 timeout**、单步串行（AGENTS.md 工具纪律）
- **commit message 含 `wf(TAG0031-P{阶段}):`** 前缀
- **改 `agate/scripts/*` 触发 SELF-GATE**：commit message 需含 `self-gate-review:` 或 `self-gate-skip:`。协议文档变更需跑 `check-protocol-consistency.py` 确认无 ERROR

## 6. 任务编号与状态

- 任务目录：`agate-workspace/tasks/TAG0031-debt-cleanup/`（在 worktree 里）
- `.state.yaml`：phase=P0（P1 开始后推进）
- active-tasks.md「待开始」已有 TAG0031 行（⬜ P0）
- roadmap：无独立 RM（DEBT 修复，不关联 RM 条目——closure 后 debt 文件登记关闭）
- **编号体系**：任务用 `TAG0031`。校验器 `^T[A-Z]{2}\d+$`
- **并行提示**：TAG0029（gate 解析器）/ TAG0030（验收盲区）与本路并行，三路文件域不重叠——roadmap/active-tasks/debt 登记行是共享面，只改自己关联的行，不整表重排

## 7. 已知风险与止损

- **check-gate.py 是核心 gate 消费方**（DEBT0016/17/18）：改判定逻辑先补失败测试确认红（TDD），全量 pytest + consistency 0 ERROR 是硬门槛 → 止损：单改单测，逐步回归
- **fail-closed 行为变更**（DEBT0018）：降级 stub 改显式失败后安装破损环境消费脚本从 false-PASS 变报错 → 止损：grep 消费方确认无合法依赖降级静默
- **hash 合并影响面**（DEBT0002）：pack/install 调用点全 grep → 止损：合并后跑 pack → install → 卸载全流程回归
- **测试隔离改造**（DEBT0007）：改后任意 basetemp 全绿 → 止损：全量 pytest 确认无环境敏感回归（RM-AG0041 教训）

## 8. 完成后

- P8 gate + READY → 提 PR（PR 普通 merge 非 squash，tag 要求——但**不自行 git-to-main**，merge 由主 Agent 执行）
- **合并前在 PR 里看 CI 结果**——pytest/shellcheck/consistency/gate-backstop 全绿才算过
- **merge 模式：本任务 PR 完成后由主 Agent 综合 merge**（三路并行 TAG0029/30/31，不自行 git-to-main）
- 7 条 DEBT 登记关闭（debt/tech-debt.md 逐条 status: closed + closure 核验）
- 复盘按 agate 自身变更流程归档（合并后在主 checkout 写复盘 + 更新 roadmap/版本）

## 9. 交接确认

- worktree 基线：consistency 0 ERROR（--strict-errors-only）已验
- hooks 就位（指向 `~/.agate` 稳定版）、orchestrator 已注册（双平台）、依赖齐全
- 任务数据就绪：TAG0031 P0-brief + .state.yaml phase=P0
- 交接单位置：`HANDOFF-TAG0031.md`（worktree 根，已 commit）
