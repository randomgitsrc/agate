# TAG0020 交接单 — 独立 Judge 机制（P6.5）

> 本交接单供 worktree session 的 agent 按此启动 TAG0020 任务。
> 任务已 P0 立项（.state.yaml phase=P0，P0-brief.md 已就绪）。
> worktree 已完成构建安装与基线验证，可直接开始 P1。

---

## 1. 你要做什么

**TAG0020**：独立 Judge 机制（RM-AG0032）。

**一句话**：P6.5 新增验收独立裁判——judge 角色用 fresh context 只凭标准（P1 BDD + P2 验收设计）逐条重验所有 BDD，信息隔离白名单禁传实现者自述，配合三层防造假与三档预算，解决 LIMITATIONS-3（自写 gate 作者与评判者同为一人）。

**设计文档（必读，P1 分析的基础）**：`/home/kity/oclab/dsh-workspace/agate-research/design-independent-judge.md`
（角色设计 / 三层防造假 / 预算 / 状态机集成 / 文件改动清单 / 与 oh-my-agent 对标取舍 / 落地节奏）。

## 2. 工作区布局（双工作区纪律，违反必出事故）

| 路径 | 角色 | 纪律 |
|------|------|------|
| `/home/kity/oclab/agate/.worktrees/agate-TAG0020` | **本任务 worktree（改造对象）** | 在这里改代码、写阶段产出、跑测试、git commit |
| `/home/kity/oclab/agate`（主 checkout） | 协议本体 + 任务数据 + `~/.agate` 指向 | **禁止改动**。稳定版来源 + hook 的 AGATE_ROOT |
| `~/.agate`（软链 → 主 checkout/agate） | **稳定版（开发工具）** | **禁止改动**。跑 gate / 读卡片用它 |

核心原则：跑 gate 用 `~/.agate`；`check-protocol-consistency.py` 用 worktree 自己的；编排/派发类工具用 `~/.agate/scripts/` 稳定版；hook 在共享 git 目录。

## 3. 任务范围（P0-brief 已锁定，P1 细化 BDD）

**交付物（设计文档 §7 文件改动清单）**：
1. `agate/assets/review-roles/judge.md`（新）——judge 角色定义（fresh context / 信息隔离 / 重验所有 BDD / 预算）
2. `agate/scripts/check-judge-verdict.py`（新）——verdict 门槛判定（BDD 计数对照 / 证据引用 / 白名单校验）
3. `agate/scripts/check-events.py`（新）——gate-events.jsonl 事件账本审计（append-only + 行间哈希链）
4. `agate/scripts/agate_common.py`——新增 `append_event()` / `read_judge_verdict()`
5. `agate/scripts/check-gate.py`——增加 P6.5 阶段分支
6. `WORKFLOW.md` / `state-machine.md`（P6.5 转移 + 重试表）/ `dispatch-protocol.md`（信息隔离节）/ `phase-cards/P6-acceptance.md` / `assets/templates/dispatch-prompt.md`（Judge 追加节）
7. 测试：`test_check_judge_verdict.py` / `test_check_events.py` + 回归（BDD 计数对照、哈希链、信息隔离白名单）

**核心约束（不可违反）**：
1. Linux 现状是基线——全量 pytest 全绿 + consistency 0 ERROR
2. 历史任务兼容：旧任务无 judge 字段 → P6.5 只对新任务生效（存量不挂）
3. 不引入"LLM 当 gate 主判据"——judge verdict 叠加机械核对，exit code 才是门槛（保持 agate 哲学）
4. 测试平台无关 + /tmp 只读（--basetemp）
5. SELF-GATE 触发：`agate/**/*.md` 与 `agate/scripts/*.py` 全触发

## 4. 关键验证命令

```bash
python3 -m pytest agate/tests/unit/ -q -p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp
python3 agate/scripts/check-protocol-consistency.py --strict-errors-only
bash agate/tests/scripts/count-tests.sh   # 只增不减
```

## 5. 阶段推进纪律（硬约束）

- commit 时 phase = 本 commit 产出所在阶段；TDD 先红后绿；commit message 前缀 `wf(TAG0020-P{N})`
- 触发 self-gate 文件入暂存区时，commit message 须含 `self-gate-review:` 路径或 `self-gate-skip:` 理由
- 【强制要求】P1 同类扫描：grep review-roles 现状与 status 门槛映射；grep dispatch-context 注入内容（白名单禁入项推导）；grep check-p6-provenance 六道审计（事件账本交集）
- bash 一律 timeout；读文件用 read/grep/glob 工具；单步串行

## 6. 任务编号与状态

- task_id: `TAG0020`（RM-AG0032，roadmap 已回写 scheduled；依赖 TAG0019）
- 分支：`feat/TAG0020-independent-judge`（worktree `.worktrees/agate-TAG0020`）
- 当前阶段：P0（.state.yaml phase=P0）

## 7. 已知风险与止损

| 风险 | 止损 |
|------|------|
| 改动面大（12+ 文件）全触发 SELF-GATE | P8 派发 protocol-alignment-review；改动按批次 commit |
| 事件账本与 provenance 审计交集 | P2 设计字段交集；P6 兼容验证 |
| 预算阈值初值不合理 | P5 dogfood 实测校准 |
| 历史任务误触发 P6.5 | 无 judge 字段 → 跳过（设计文档 §6）|

## 8. 完成后

1. pytest 全绿 + 0 consistency ERROR + count-tests 不漂移
2. SELF-GATE review；3. release PR 普通 merge（--no-ff）；4. 版本引用文件清单；5. roadmap 回写 RM-AG0032 → done

## 9. 交接确认

- P0-brief 四字段齐全 ✅；worktree 基线（pytest 全绿 + 0 ERROR）✅；设计文档就绪（design-independent-judge.md）✅
