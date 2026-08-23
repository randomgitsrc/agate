# HANDOFF-DOGFOODING-3TASKS — 三连任务程序级交接单

> 本交接单供**以 agate 编排者模式启动的新会话**按此执行 TAG0019 → TAG0020 → TAG0021 三个任务。
> 三个任务均已完成 P0 立项（.state.yaml phase=P0，P0-brief 就绪），worktree 已建、orchestrator 已注册、基线已验证。
> **串行执行，禁止并行**（理由见 §3——文件足迹高度重叠 + 工具稳定优先纪律）。

---

## 1. 程序概述

| 任务 | 对应 RM | 主题 | 一句话 | 设计文档 |
|------|---------|------|--------|----------|
| **TAG0019** | RM-AG0031 | 风险分路由 | 客观信号算分决定仪式深度，压成本不降质量 | `dsh-workspace/agate-research/design-risk-routing.md` |
| **TAG0020** | RM-AG0032 | 独立 Judge | P6.5 独立裁判，fresh context 重验全部 BDD | `dsh-workspace/agate-research/design-independent-judge.md` |
| **TAG0021** | RM-AG0022 | 结构化层 | 协议规则 YAML 权威源 + 双向一致性 gate | `dsh-workspace/agate-research/design-structured-layer.md` |

来源：2026-08-21 用户反馈（成本/速度）+ TAG0018 实证（LLM 评审≈0 净收益、机械 gate 全胜）+ TAG0014 复盘。

## 2. ⚠️ 启动入口（HANDOFF 读取盲点——必读）

**orchestrator 默认启动流程读的是 `{AGATE_WORKSPACE}/tasks/active-tasks.md` + `.state.yaml`，不会自动读 HANDOFF。**

每个任务的新会话**首条指令必须显式写**：

```
读 {worktree 根}/HANDOFF-{Txxx}.md 并严格按其执行（任务范围/纪律/风险全在里面）
```

认准当前任务号——仓库根有历史 HANDOFF-TAG0xxx.md（已归档在 archived/），别读错；未合并前本任务 HANDOFF 只存在于 worktree，不在 main。

## 3. 执行顺序与纪律（硬约束）

1. **串行**：TAG0019 → 合并 → TAG0020 → 合并 → TAG0021 → 合并。禁止并行（三个任务重叠 `phase-cards/check-gate.py/state-machine.md/dispatch-protocol.md/agate_common.py`，并行必然大规模 merge 冲突 + 稳定版 gate 无法验证引入新规则的分支）
2. **每任务独立版本**：0019→v0.58.0、0020→v0.59.0、0021→v0.60.0（按 P8 卡 bump）
3. **release PR 普通 merge（--no-ff）**，禁止 squash（agate-summary.py 依赖 tag 祖先关系）
4. 每任务完成后逐步重跑 `bash agate/tests/scripts/count-tests.sh`（只增不减）

## 4. 每任务速查表

### TAG0019 风险分路由
| 项 | 值 |
|----|----|
| worktree | `/home/kity/oclab/agate/.worktrees/agate-TAG0019` |
| 分支 | `feat/TAG0019-risk-routing`（已推送远端）|
| HANDOFF | worktree 根 `HANDOFF-TAG0019.md` |
| 主要改动 | `agate-risk-score.py`(新) + P1/P2 卡 ceremony 字段 + check-pruning→check-routing + requirements-review 增责 |
| 验收锚 | M3 实证：thin 档评审轮数 vs 真实发现数对比（TAG0018 基线：4 评审≈0 净收益）|

### TAG0020 独立 Judge
| 项 | 值 |
|----|----|
| worktree | `/home/kity/oclab/agate/.worktrees/agate-TAG0020` |
| 分支 | `feat/TAG0020-independent-judge`（已推送远端）|
| HANDOFF | worktree 根 `HANDOFF-TAG0020.md` |
| 主要改动 | `review-roles/judge.md`(新) + `check-judge-verdict.py`/`check-events.py`(新) + state-machine P6.5 + agate_common append_event |
| 依赖 | TAG0019（thin 档生效后为验收基线；非硬阻塞，可先做设计）|

### TAG0021 结构化层
| 项 | 值 |
|----|----|
| worktree | `/home/kity/oclab/agate/.worktrees/agate-TAG0021` |
| 分支 | `feat/TAG0021-structured-layer`（已推送远端）|
| HANDOFF | worktree 根 `HANDOFF-TAG0021.md` |
| 主要改动 | `rules/{phases,dispatch,roles}.yaml`(新) + schema + `check-structure-consistency.py`(新) + M0-M3 脚本迁移 |
| 注意 | 体量最大；P1 BDD 按 M0/M1/M2/M3 分组便于分批 commit |

## 5. 环境事实（本机实测，直接照做）

- **权限**：danger-full-access（无审批弹窗，沙箱不拦截文件操作）
- **/tmp 只读**：pytest 必须 `-p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp`
- **解释器**：用系统 python（`/usr/bin/python3`）跑 pytest（模块装在系统 python，裸 pytest 命令 PATH 找不到）
- **bash 纪律**：长命令外层 `timeout`；读文件用 read/grep/glob 工具（不占 bash 通道）；单步串行不并行 bash
- **稳定版纪律**：跑 gate/读卡片用 `~/.agate`；`check-protocol-consistency.py` 必须用 worktree 自己的；编排/派发类工具（agate-inject-card.py 等）用 `~/.agate/scripts/` 稳定版
- **hook**：三个 worktree 的 commit 自动触发共享 git 目录 hook（`/home/kity/oclab/agate/.git/hooks/`），gate 工具为 `~/.agate` 稳定版
- **⚠️ 共享状态禁止并行（2026-08-21 实证事故）**：三个 worktree 共享 `.git/hooks/` 与 `~/.agate`——**并行跑 pytest / commit 会让集成测试互相污染**（实测：三个 worktree 并行全量 pytest 出现 commit-msg-self-gate 集成测试 2-3 个假失败；串行重跑全绿 1036 passed）。基线验证必须串行
- **worktree 解析**：`python3 agate/scripts/agate_common.py` 必须**在 worktree 目录内**跑（CWD 决定 project_root），输出 `AGATE_WORKSPACE=.../.worktrees/agate-TAG00XX/agate-workspace`

## 6. 启动 orchestrator 会话

1. `cd <worktree>`（如 `cd .worktrees/agate-TAG0019`）
2. 用平台（OpenCode/Claude Code/DSH）选 orchestrator agent（worktree 的 `.opencode/agents/orchestrator.md`/`.claude/agents/orchestrator.md` 已软链到 `~/.agate/orchestrator-template.md`）
3. 首条指令：`读 worktree 根 HANDOFF-TAG0019.md 并严格按其执行`
4. orchestrator 会自动：解析 {agate_root}/{AGATE_WORKSPACE} → 读 active-tasks.md → 按 .state.yaml phase=P0 推进 P1

## 7. 程序级验收（三个都合并后）

- [ ] 三分支各自 PR 合并（普通 merge --no-ff），tag v0.58.0/v0.59.0/v0.60.0 创建并推送
- [ ] `git describe --tags origin/main` == v0.60.0；`git merge-base --is-ancestor` 验证 tag 祖先
- [ ] 三个 RM 条目（RM-AG0031/0032/0022）roadmap 回写 done
- [ ] 全量 pytest 全绿 + consistency 0 ERROR + count-tests 单调
- [ ] 三个 HANDOFF-TAG00XX.md 归档到 `archived/docs-2026-08/`（对齐既有惯例）

---

*本交接单由 DSH 会话（2026-08-21）生成。基线验证：TAG0019 串行全量 pytest 1036 passed + 2 skipped + consistency 0 ERROR（V0.57.0 代码态；TAG0020/21 代码与其同源，仅 roadmap/board 文本差异，不涉测试逻辑）。注意：并行跑 pytest 会产生假失败（见 §5 共享状态事故）。*