# TAG0023 交接单 — 机制校验补强批

> 本交接单供 worktree session 的 agent 按此启动 TAG0023 任务。
> 任务已 P0 立项（.state.yaml phase=P0，P0-brief.md 已就绪）。
> worktree 已完成构建安装与基线验证，可直接开始 P1。

---

## 1. 你要做什么

**TAG0023**：机制校验补强批（RM-AG0042 + RM-AG0043 + RM-AG0044 + RM-AG0045）。

**一句话**：修复 TAG0019-21 复盘独立评审（2026-08-23 approved）确认的 4 个 agate 机制缺口——①门槛失败事件强制记录 retries（重试上限防绕过）②P8 roadmap 回写 done 校验（记录闭环）③环境敏感测试集中治理（第三例 test_bdd_14）④声明写时校验（消灭 commit 时格式折返）。

**复盘（必读）**：`/home/kity/oclab/dsw-workspace/agate-research/retrospective-tag0019-21.md`

## 2. 工作区布局（双工作区纪律，违反必出事故）

| 路径 | 角色 | 纪律 |
|------|------|------|
| `/home/kity/oclab/agate/.worktrees/agate-TAG0023` | **本任务 worktree（改造对象）** | 在这里改代码、写阶段产出、跑测试、git commit |
| `/home/kity/oclab/agate`（主 checkout） | 协议本体 + 任务数据 + `~/.agate` 指向 | **禁止改动**。稳定版来源 + hook 的 AGATE_ROOT |
| `~/.agate`（软链 → 主 checkout/agate） | **稳定版（开发工具）** | **禁止改动**。跑 gate / 读卡片用它 |

核心原则：跑 gate 用 `~/.agate`；`check-protocol-consistency.py` 用 worktree 自己的；编排/派发类工具用 `~/.agate/scripts/` 稳定版；hook 在共享 git 目录；**共享 .git/hooks 与 ~/.agate 禁止并行跑测试/commit**。

## 3. 任务范围（P0-brief 已锁定，P1 细化 BDD；三子项各自验收锚）

1. **RM-AG0042 retries 强制记录**：gate 校验 retries 与门槛失败事件（评审 rejected/P5→P4 回退/子代理空返回）对应性——失败事件存在而 retries 为空 → 阻断/高优 WARNING；P1/P2 卡明确评审被拒须写 retries；验收=新任务评审 rejected 后 retries 必有对应条目
2. **RM-AG0043 roadmap 回写校验**：P8 gate 按 task_id 反查关联 RM 条目状态必须 done；**补记 RM-AG0032 → done**（v0.59.0 已发布）；验收=新任务 P8 后 roadmap RM 自动 done
3. **RM-AG0044 环境敏感测试治理**：排查 check-debt.py --retreat-coverage 的 git 环境敏感点（short SHA/runner）；建立环境敏感测试判定+集中清单+CI flaky 重跑机制；验收=test_bdd_14 连续 5 次 CI 稳定 + 集中清单
4. **RM-AG0045 声明写时校验**：ceremony/coupling_checklist/跳过风险/phases 等声明写文件时即 schema 校验（生成器/formatter 层）；验收=格式错误写入即报、commit 折返归零

**核心约束（不可违反）**：
1. Linux 现状是基线——全量 pytest 全绿 + consistency 0 ERROR + ruff All checks passed（0.16.4 对齐 CI）
2. 三子项改动面：check-gate.py/check-state-transition.py/P1/P2 卡/P8 卡/check-debt.py/CI/测试 → 触发 SELF-GATE
3. RM-0042 的"门槛失败事件判定"需可机器判定的事件源定义（P2 设计）；RM-0043 需处理历史 RM 与多 RM 关联
4. 测试平台无关 + /tmp 只读（--basetemp=/home/kity/oclab/dsh-workspace/ptmp -p no:cacheprovider）

## 4. 关键验证命令

```bash
python3 -m pytest agate/tests/ -q -p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp
python3 agate/scripts/check-protocol-consistency.py --strict-errors-only
~/.venvs/agate-dev/bin/ruff check agate/
bash agate/tests/scripts/count-tests.sh   # 只增不减
```

## 5. 阶段推进纪律（硬约束）

- commit 时 phase = 本 commit 产出所在阶段；TDD 先红后绿；commit message 前缀 `wf(TAG0023-P{N})`
- 触发 self-gate 文件入暂存区时，commit message 须含 `self-gate-review:` 路径或 `self-gate-skip:` 理由
- 【强制要求】P1 同类扫描：grep retries 全部消费点（check-state-transition/state-machine/check-gate）；grep roadmap 回写消费点；grep 环境敏感测试已知清单（test_bdd_7/25/14 + known-failures）
- bash 一律 timeout；读文件用 read/grep/glob 工具；单步串行

## 6. 任务编号与状态

- task_id: `TAG0023`（RM-AG0042~0045 四条，roadmap 已回写 scheduled + 关联）
- 分支：`feat/TAG0023-mechanism-checks`（worktree `.worktrees/agate-TAG0023`）
- 当前阶段：P0（.state.yaml phase=P0）

## 7. 已知风险与止损

| 风险 | 止损 |
|------|------|
| RM-0042 事件源判定误报 | P2 定义可机器判定规则（status=rejected/回退 commit 证据/空返回记录），配正反用例 |
| RM-0043 历史 RM 匹配 | P2 定义匹配规则（task_id 反查 + 无关联回写兜底）|
| RM-0044 根因在 git 环境假设 | P1 先复现定位（本地 3/3 过 vs CI flaky 差异），再定 BDD，不盲改 |
| 三子项同簇互扰（check-gate 被 0042/0043 同时触碰）| 分批 commit + 影响面梳理 |

## 8. 完成后

1. pytest 全绿 + 0 consistency ERROR + count-tests 不漂移 + ruff All checks passed
2. SELF-GATE review；3. release PR 普通 merge（--no-ff）；4. 版本引用文件清单（README badge/CHANGELOG/UPGRADING）
5. roadmap 回写：RM-AG0042~0044 → done（含 RM-AG0032 历史补记）

## 9. 交接确认

- P0-brief 四字段齐全 ✅；worktree 基线（pytest 全绿 + 0 ERROR + ruff 绿）✅；复盘文档就绪（retrospective-tag0019-21.md，approved）✅
