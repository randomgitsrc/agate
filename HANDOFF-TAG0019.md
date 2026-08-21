# TAG0019 交接单 — 风险分路由（ceremony routing）

> 本交接单供 worktree session 的 agent 按此启动 TAG0019 任务。
> 任务已 P0 立项（.state.yaml phase=P0，P0-brief.md 已就绪）。
> worktree 已完成构建安装与基线验证，可直接开始 P1。

---

## 1. 你要做什么

**TAG0019**：风险分路由（RM-AG0031）。

**一句话**：把任务仪式深度从"agent 自报复杂度"改为"客观信号脚本算分"——压 agate 成本曲线而不降质量地板。

**设计文档（必读，P1 分析的基础）**：`/home/kity/oclab/dsh-workspace/agate-research/design-risk-routing.md`
（三原则：客观信号算分 / fail-closed 默认 / 声明被审；M1-M4 落地节奏；三档 ceremony 表）。

## 2. 工作区布局（双工作区纪律，违反必出事故）

| 路径 | 角色 | 纪律 |
|------|------|------|
| `/home/kity/oclab/agate/.worktrees/agate-TAG0019` | **本任务 worktree（改造对象）** | 在这里改代码、写阶段产出、跑测试、git commit |
| `/home/kity/oclab/agate`（主 checkout） | 协议本体 + 任务数据 + `~/.agate` 指向 | **禁止改动**。稳定版来源 + hook 的 AGATE_ROOT |
| `~/.agate`（软链 → 主 checkout/agate） | **稳定版（开发工具）** | **禁止改动**。跑 gate / 读卡片用它 |

核心原则：跑 gate 用 `~/.agate`；`check-protocol-consistency.py` 用 worktree 自己的；编排/派发类工具用 `~/.agate/scripts/` 稳定版；hook 在共享 git 目录（主 checkout `.git/hooks/`）。

## 3. 任务范围（P0-brief 已锁定，P1 细化 BDD）

**交付物（M1-M2 主体）**：
1. `agate/scripts/agate-risk-score.py`（新）——客观信号算分：文件类型/敏感路径/改动规模（对齐 pruning 源码数≤5）/域映射/影响面 → risk_score + tier
2. P1 卡加 `ceremony` 字段（thin/standard/full）+ fail-closed 声明 checklist（对齐 coupling_checklist 流式 + 跳过风险评估）
3. `check-pruning.py` 扩展为 check-routing（或新增 CHECK）：校验 ceremony 声明 vs risk_score 与 checklist
4. `requirements-review` 角色增"审声明"职责（风险分级/裁剪声明 vs diff 证据）
5. M3（thin 档跳过 LLM 评审）以实证验收锚（TAG0018：LLM 评审≈0 净收益）

**核心约束（不可违反）**：
1. Linux 现状是基线——全量 pytest 全绿 + consistency 0 ERROR
2. 复用 check-pruning.py 既有判定逻辑（源码数≤5/coupling_checklist/跳过风险），不重复发明
3. 测试平台无关（agate 核心约束）；/tmp 只读需 --basetemp
4. SELF-GATE 触发：改动 `agate/**/*.md` 与 `agate/scripts/*.py` 均触发

## 4. 关键验证命令

```bash
python3 -m pytest agate/tests/unit/ -q -p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp
python3 agate/scripts/check-protocol-consistency.py --strict-errors-only
bash agate/tests/scripts/count-tests.sh   # 只增不减
```

## 5. 阶段推进纪律（硬约束）

- commit 时 phase = 本 commit 产出所在阶段；TDD 先红后绿；commit message 前缀 `wf(TAG0019-P{N})`
- 触发 self-gate 文件入暂存区时，commit message 须含 `self-gate-review:` 路径或 `self-gate-skip:` 理由
- 【强制要求】P1 同类扫描：grep check-pruning.py 源码数≤5/coupling_checklist/跳过风险判定；grep 全仓 risk_level/ceremony 消费点；grep 平台差异对 gate 语义影响
- bash 一律 timeout；读文件用 read/grep/glob 工具；单步串行不并行 bash

## 6. 任务编号与状态

- task_id: `TAG0019`（RM-AG0031，roadmap 已回写 scheduled）
- 分支：`feat/TAG0019-risk-routing`（worktree `.worktrees/agate-TAG0019`）
- 当前阶段：P0（.state.yaml phase=P0）

## 7. 已知风险与止损

| 风险 | 止损 |
|------|------|
| 算分规则被 exploit（agent 凑低分）| 信号来自 diff 客观事实 + 降级 checklist + requirements-review 独立审声明 |
| thin 档漏真实问题 | fail-closed + 机械 gate 保留 + P5/P6 不可裁 + M3 实证验收锚，不达标回滚 |
| 与 pruning 逻辑重复 | 直接复用 check-pruning.py 判定函数，不新写一套 |

## 8. 完成后

1. pytest 全绿 + 0 consistency ERROR + count-tests 不漂移
2. SELF-GATE review（protocol-alignment-review 派发）
3. release PR 普通 merge（--no-ff），禁止 squash
4. 版本引用文件清单（README badge/CHANGELOG/UPGRADING）
5. roadmap 回写 RM-AG0031 → done

## 9. 交接确认

- P0-brief 四字段齐全 ✅；worktree 基线（pytest 全绿 + 0 ERROR）✅；设计文档就绪（design-risk-routing.md）✅
