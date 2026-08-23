# TAG0022 交接单 — 三连任务确认问题修复批

> 本交接单供 worktree session 的 agent 按此启动 TAG0022 任务。
> 任务已 P0 立项（.state.yaml phase=P0，P0-brief.md 已就绪）。
> worktree 已完成构建安装与基线验证，可直接开始 P1。

---

## 1. 你要做什么

**TAG0022**：三连任务确认问题修复批（RM-AG0037 + RM-AG0038 + RM-AG0039 + RM-AG0040 + RM-AG0041）。

**一句话**：修复 TAG0019/20/21 全面分析（2026-08-22，基于 main 落地实测）确认的 5 个真实问题——ruff 合并强制 / 结构化层 M2 迁移闭环 / judge 启用强制化 / TAG0019 M3 实证收尾 / 环境假象测试根治。

**完整分析（必读）**：`/home/kity/oclab/dsh-workspace/agate-research/tag0019-21-analysis.md`

## 2. 工作区布局（双工作区纪律，违反必出事故）

| 路径 | 角色 | 纪律 |
|------|------|------|
| `/home/kity/oclab/agate/.worktrees/agate-TAG0022` | **本任务 worktree（改造对象）** | 在这里改代码、写阶段产出、跑测试、git commit |
| `/home/kity/oclab/agate`（主 checkout） | 协议本体 + 任务数据 + `~/.agate` 指向 | **禁止改动**。稳定版来源 + hook 的 AGATE_ROOT |
| `~/.agate`（软链 → 主 checkout/agate） | **稳定版（开发工具）** | **禁止改动**。跑 gate / 读卡片用它 |

核心原则：跑 gate 用 `~/.agate`；`check-protocol-consistency.py` 用 worktree 自己的；编排/派发类工具用 `~/.agate/scripts/` 稳定版；hook 在共享 git 目录；**共享 .git/hooks 与 ~/.agate 禁止并行跑测试/commit**。

## 3. 任务范围（P0-brief 已锁定，P1 细化 BDD；五子项各自验收锚）

1. **RM-AG0037 ruff 合并强制**：CI ruff job 设为 PR required check（分支保护，需维护者在仓库设置勾选——实现侧改 workflow + 文档标注配置步骤）；验收=新任务合并时 ruff 零违规
2. **RM-AG0038 M2 迁移闭环**：check-gate.py 等核心脚本迁移到 rules/*.yaml（22 处 md 解析清零）；S-1~S-6 收紧；验收=check-gate.py 零 md 解析 + 全量绿
3. **RM-AG0039 judge 强制化**：P1 gate 校验新任务必须 judge.enabled: true（缺失阻断/高优 WARNING）；历史任务跳过；验收=新任务 P1 不写 judge 被拦
4. **RM-AG0040 M3 实证收尾**：ceremony: thin 实战计划 + 实证对比报告（评审轮数 vs 真实发现数）；验收=实证报告（可能需经用户指定薄任务实战）
5. **RM-AG0041 环境测试根治**：test_bdd_7/25 改探测 git 上下文/强制仓库外 basetemp；验收=任意 basetemp 全量 0 失败

**核心约束（不可违反）**：
1. Linux 现状是基线——全量 pytest 全绿 + consistency 0 ERROR + **ruff All checks passed**（~/.venvs/agate-dev/bin/ruff 0.16.4 对齐 CI）
2. 五子项改动面：CI 配置/check-gate.py/state-machine/P6 卡/P1 卡/测试 → 触发 SELF-GATE
3. RM-AG0038 是最大体量——P1 BDD 按子项分组，避免同文件多轮改
4. 测试平台无关 + /tmp 只读（--basetemp=/home/kity/oclab/dsh-workspace/ptmp -p no:cacheprovider）

## 4. 关键验证命令

```bash
python3 -m pytest agate/tests/ -q -p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp
python3 agate/scripts/check-protocol-consistency.py --strict-errors-only
~/.venvs/agate-dev/bin/ruff check agate/
bash agate/tests/scripts/count-tests.sh   # 只增不减
```

## 5. 阶段推进纪律（硬约束）

- commit 时 phase = 本 commit 产出所在阶段；TDD 先红后绿；commit message 前缀 `wf(TAG0022-P{N})`
- 触发 self-gate 文件入暂存区时，commit message 须含 `self-gate-review:` 路径或 `self-gate-skip:` 理由
- 【强制要求】P1 同类扫描：grep 全仓 ruff 消费点；grep check-gate.py 全部 md 解析点清单；grep judge.enabled 消费点；grep ceremony 消费点
- bash 一律 timeout；读文件用 read/grep/glob 工具；单步串行

## 6. 任务编号与状态

- task_id: `TAG0022`（RM-AG0037~0041 五条，roadmap 已回写 scheduled + 关联）
- 分支：`feat/TAG0022-confirmed-problems`（worktree `.worktrees/agate-TAG0022`）
- 当前阶段：P0（.state.yaml phase=P0）

## 7. 已知风险与止损

| 风险 | 止损 |
|------|------|
| RM-AG0037 required check 是 GitHub 配置，实现侧只能改 workflow | P1 明确"实现 vs 配置"边界；配置步骤写入文档/UPGRADING；验收以 workflow 改动为准 |
| RM-AG0038 迁移大（check-gate.py）| BDD 按子项分组 + 渐进迁移（对齐已迁移的 gate_commands 族模式）+ 每步全量测试 |
| RM-AG0040 实证依赖外部薄任务出现 | 交付"实证执行计划 + 触发条件"；或经用户指定一个 low 任务实战 |
| 五子项同簇互扰（check-gate.py 同时被 0038/0039 触碰）| P1 影响面梳理 + 分批 commit（0039 的 P1 gate 校验可与 0038 的迁移错开文件）|

## 8. 完成后

1. pytest 全绿 + 0 consistency ERROR + count-tests 不漂移 + **ruff All checks passed**
2. SELF-GATE review；3. release PR 普通 merge（--no-ff）；4. 版本引用文件清单（README badge/CHANGELOG/UPGRADING）
5. roadmap 回写：RM-AG0037~0041 → done（RM-AG0040 以实证报告为准）

## 9. 交接确认

- P0-brief 四字段齐全 ✅；worktree 基线（pytest 全绿 + 0 ERROR + ruff 绿）✅；分析文档就绪（tag0019-21-analysis.md）✅
