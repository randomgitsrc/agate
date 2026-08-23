# TAG0021 交接单 — 协议结构化层（RM-AG0022）

> 本交接单供 worktree session 的 agent 按此启动 TAG0021 任务。
> 任务已 P0 立项（.state.yaml phase=P0，P0-brief.md 已就绪）。
> worktree 已完成构建安装与基线验证，可直接开始 P1。

---

## 1. 你要做什么

**TAG0021**：协议结构化层（RM-AG0022）。

**一句话**：把 agent 消费的协议规则从 8000+ 行自由文本 markdown 抽成机器可读的 YAML 权威源（phases/dispatch/roles + JSON Schema），双向一致性 gate 防漂移，gate 脚本从"grep markdown"迁移到"读 YAML"——压"agent 读 8000+ 行 md 理解规则"的摩擦与 grep 解析脆弱性。

**设计文档（必读，P1 分析的基础）**：`/home/kity/oclab/dsh-workspace/agate-research/design-structured-layer.md`
（总体架构：YAML 权威源 + markdown 叙事层 / Schema 草案 / S-1~S-6 双向 gate / M0-M3 迁移路径 / 风险对策）。

## 2. 工作区布局（双工作区纪律，违反必出事故）

| 路径 | 角色 | 纪律 |
|------|------|------|
| `/home/kity/oclab/agate/.worktrees/agate-TAG0021` | **本任务 worktree（改造对象）** | 在这里改代码、写阶段产出、跑测试、git commit |
| `/home/kity/oclab/agate`（主 checkout） | 协议本体 + 任务数据 + `~/.agate` 指向 | **禁止改动**。稳定版来源 + hook 的 AGATE_ROOT |
| `~/.agate`（软链 → 主 checkout/agate） | **稳定版（开发工具）** | **禁止改动**。跑 gate / 读卡片用它 |

核心原则：跑 gate 用 `~/.agate`；`check-protocol-consistency.py` 用 worktree 自己的；编排/派发类工具用 `~/.agate/scripts/` 稳定版；hook 在共享 git 目录。

## 3. 任务范围（P0-brief 已锁定，P1 细化 BDD）

**交付物（M0-M3 阶段化）**：
1. **M0**：`agate/rules/{phases,dispatch,roles}.yaml` + `agate/rules/schema/*.json` + `check-structure-consistency.py`（S-1~S-6）+ `check-yaml-schema.py`——**只加不改**，现有 53 脚本继续 grep md
2. **M1**：选 3-5 个高频脚本（agate-read-gate-commands / check-pruning / check-gate）双跑对账（读 YAML vs grep 结果，不一致告警不阻断）
3. **M2**：对账稳定后切换权威源，grep 逻辑删除，一致性 gate 提升为阻断
4. **M3**：phase-cards 渲染化（模板 + YAML 数据），agate-inject-card.py 改造
5. 测试：schema 校验 / S-1~S-6 双向一致性 / 对账模式回归；count-tests 只增不减

**核心约束（不可违反）**：
1. Linux 现状是基线——全量 pytest 全绿 + consistency 0 ERROR
2. M0-M3 每阶段独立可回退（纯增量起步）
3. YAML 只承载可判定规则；叙事留 markdown
4. 工具链自举纪律：~/.agate 稳定版跑 gate，worktree 改（TAG0016 教训）
5. 测试平台无关 + /tmp 只读（--basetemp）；SELF-GATE 触发面全中

## 4. 关键验证命令

```bash
python3 -m pytest agate/tests/unit/ -q -p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp
python3 agate/scripts/check-protocol-consistency.py --strict-errors-only
bash agate/tests/scripts/count-tests.sh   # 只增不减
```

## 5. 阶段推进纪律（硬约束）

- commit 时 phase = 本 commit 产出所在阶段；TDD 先红后绿；commit message 前缀 `wf(TAG0021-P{N})`
- 触发 self-gate 文件入暂存区时，commit message 须含 `self-gate-review:` 路径或 `self-gate-skip:` 理由
- 【强制要求】P1 同类扫描：grep 53 个脚本对 markdown 的解析点（grep -cE 模式清单，按脚本归类）；grep phase-cards 门槛/产出/派发字段清单；grep check-protocol-consistency CHECK 编号空间（新 CHECK 防冲突）
- BDD 按迁移阶段（M0/M1/M2/M3）组织，便于分批 commit
- bash 一律 timeout；读文件用 read/grep/glob 工具；单步串行

## 6. 任务编号与状态

- task_id: `TAG0021`（RM-AG0022，roadmap 已回写 scheduled）
- 分支：`feat/TAG0021-structured-layer`（worktree `.worktrees/agate-TAG0021`）
- 当前阶段：P0（.state.yaml phase=P0）

## 7. 已知风险与止损

| 风险 | 止损 |
|------|------|
| 双份维护（md+YAML）漂移 | S-1~S-4 双向 gate 阻断 + CI 强制 |
| 一次性迁移爆炸 | M0-M3 渐进 + 每阶段可回退 + BDD 按阶段分组 |
| YAML 过深失去可读性 | schema 枚举约束 + 叙事留 md |
| 工具链自举（新 gate 判自己）| 双工作区纪律（稳定版判、worktree 改）|

## 8. 完成后

1. pytest 全绿 + 0 consistency ERROR + count-tests 不漂移
2. SELF-GATE review；3. release PR 普通 merge（--no-ff）；4. 版本引用文件清单；5. roadmap 回写 RM-AG0022 → done

## 9. 交接确认

- P0-brief 四字段齐全 ✅；worktree 基线（pytest 全绿 + 0 ERROR）✅；设计文档就绪（design-structured-layer.md）✅
