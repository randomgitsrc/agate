# P0-brief — TAG0031 DEBT 存量修复批（DEBT0002/0003/0004/0007/0016/0017/0018）

> 本文件由主 Agent 亲自填写（P0 阶段产出）。来源：历史遗留 open DEBT（TAG0008 版本管理域 3 条 + 测试隔离 1 条 + check-gate.py 健壮性 3 条）。
> 全部低风险脚本健壮性修复，按文件域分三簇，但都无新机制设计、无协议文档面改动——**单 task 打包**（仿 TAG0024「工具链批」先例）。

## task

"批量关闭 7 条历史遗留 open DEBT（全部低风险脚本健壮性，无新机制设计）：**版本管理域 3 条（DEBT0002/0003/0004）**——离线包 compute_sha256 双实现漂移（pack/install 两侧各自实现未共享，补 agate_common 目录 hash 工具 import 共享）；离线 manifest 未签名（checksum 防损坏不防整包替换，文档明示信任边界，如需签名引入 minisign/GPG 校验 manifest）；卸载引用保护扫描限流漏扫旧引用且无提示（限流边界命中时 stderr WARNING 提示可能漏扫）；**测试隔离 1 条（DEBT0007）**——test_check_pruning.py 部分用例依赖真实 git 暂存区而非隔离 fixture，改在隔离临时 git 仓库内运行（git init）；**check-gate.py 健壮性 3 条（DEBT0016/0017/0018）**——gate_p4 的 CODE-MAP.md 路径用本地 task_dir 向上两级推导未调 resolve_workspace 权威函数（改 import agate_common 共享）；「## 新增文件核对表」子串判定自指场景假阴性（改整行/标题级判定）；agate_common import 降级 stub 返回 0/空呈 false-PASS（降级 stub 改显式失败 fail-closed）。"

### scope

- **Phase 1（版本管理域，DEBT0002/3/4）**：`agate_common.py` 补 compute_sha256 目录 hash 工具；pack/install 两侧改 import 共享（closure：单实现 + 两侧引用）；manifest 信任边界文档化（bundle 提供者可信声明；评估签名成本后决定 minisign/GPG 或文档明示）；卸载引用保护扫描限流边界命中 → stderr WARNING
- **Phase 2（测试隔离，DEBT0007）**：`test_check_pruning.py` 的 `_staged_source_count` 用例改隔离临时 git 仓库（tmp_path + git init），不再依赖真实暂存区
- **Phase 3（check-gate.py 健壮性，DEBT0016/17/18）**：gate_p4 CODE-MAP 路径改 resolve_workspace 权威解析；「新增文件核对表」改整行/标题级判定消除自指假阴性；import 降级 stub 改显式失败（fail-closed：关键读取器不可导入时报错而非返回 0/空）
- **测试**：每条 DEBT 对应回归测试（hash 共享单测 / 隔离 git 仓库用例 / CODE-MAP 路径边界 / 核对表整行判定 / 降级失败显式化）——TDD 先红后绿

### out-of-scope

- 离线包签名体系完整实现（DEBT0003 的 minisign/GPG 若评估成本过高，文档明示信任边界即关闭——签名体系作为 backlog 后续条目）
- gate 命令解析器（DEBT0023/0027/RM-AG0056——归 TAG0029）
- 验收盲区机制（RM-AG0057/DEBT0024-26——归 TAG0030）
- 平台假设扫描器规则语义（RM-AG0056 本体，归 TAG0029）

## known_risks

- "同类/影响面预判（DEBT0002 hash 合并）：pack/install 两侧调用点 grep 全量确认，合并后跑离线包安装全流程回归（pack → install → 卸载）确认无行为变化"
- "DEBT0017 子串→整行判定是 gate_p4 逻辑变更：先补'自指场景'失败测试确认红（TDD），再改判定；全量 pytest + consistency 0 ERROR 是硬门槛（check-gate 是核心 gate 消费方）"
- "DEBT0018 fail-closed 改造是行为变更：降级 stub 改显式失败后，安装破损环境（agate_common 不可导入）下消费脚本从 false-PASS 变报错——确认无合法场景依赖降级静默（grep 消费方）"
- "DEBT0007 测试隔离改造：改后用例必须在任意 basetemp 位置全绿（RM-AG0041 教训），跑全量 pytest 确认无环境敏感回归"

## env_constraints

- 本任务改 `agate/scripts/*`（agate_common.py / check-gate.py / pack / install 相关）→ **触发 SELF-GATE**，commit message 须含 `self-gate-review:` 或 `self-gate-skip:`
- 用系统 python（`/usr/bin/python3`）跑 pytest/pyyaml；ruff 用 `~/.venvs/agate-dev/bin/ruff`
- 基线验证用 `--strict-errors-only`（DEBT0012）；编排/派发类工具用 `~/.agate` 稳定版
- 跑离线包相关回归需准备离线 bundle 样例（pack 产物），确认无网络依赖

## executor_env

- worktree：`.worktrees/agate-TAG0031`（分支 `feat/TAG0031-debt-cleanup`），构建流程见 `docs/guides/worktree-dogfooding-guide.md`，交接单 `HANDOFF-TAG0031.md` 按模板全 9 节填写
- 任务目录：`agate-workspace/tasks/TAG0031-debt-cleanup/`
- **merge 模式**：完成 PR 后由主 Agent 综合 merge（三路并行 TAG0029/30/31 之一，文件域与另两路不重叠）
