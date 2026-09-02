# TAG0027 交接单 — 编排语义统一落地（推进侧状态机 CLI）

> 本交接单供 worktree session 的 agent 按此启动 TAG0027 任务。
> 任务已 P0 立项（.state.yaml phase=P0，P0-brief.md 已就绪）。
> worktree 已完成构建安装与基线验证，可直接开始 P1。

---

## 1. 你要做什么

**TAG0027**：编排语义统一落地（RM-AG0054）。

**一句话**：推进决策从 orchestrator 临场判断改为查表推进——新增推进侧状态机 CLI（`agate next`/`agate advance`），复用既有资产（`check-state-transition.py` + `check-gate.py` exit 三态 + `rules/phases.yaml` 扩展 next/retreat 字段 + `agate-retreat-to.py` 回退侧对接），CLI 为 `/loop` 档位 C 的可观测层；并完成编排心智统一文档化（dispatch 五模式唯一锚点 + 平台差异挂实现注记标记）+ **方案 A 渲染时注入（派发=单命令自动注入渲染，主 Agent 不直接调注入工具，审计 2 联动走渲染产物）+ 护栏 1 机械化**。**全量四 phase 已纳入本任务，不分后续任务。**

**完成后达到的目标（验收愿景，P6.5 judge 对照基准）**：
- **推进侧**：主 Agent 不再"自己判断进入下一 phase"——`agate next` 查转移表给出结论（exit 0 直推 / 1 回退 / 2 暂停转主 Agent）；/loop 档位 C 自动推进强制走 `agate next`；转移表经 S-1/S-2 双向 gate 与 state-machine.md 防漂移
- **派发侧**：`agate dispatch P1 {role}` 单命令 = 读上下文 + 动态拼装卡片 + 输出成品 prompt，复制即派发；"占位符缺失→注入失败→手动修"环节（TPV0095 事故类）**无失败路径**；手工写上下文 + `agate-inject-card.py` 存量用法兼容保留
- **心智/护栏**：dispatch 五模式为唯一语义锚点，平台差异全部挂「实现注记」标记；`check-protocol-consistency.py` 扫描"含平台名无实现注记段落"进 **CI 硬校验**（护栏从评审时人工检查升级为机械校验）
- **可量化**：3 个新 CLI（`agate next`/`agate advance`/`agate dispatch`）、BDD ≥16 条、消灭 3 个环节（注入失败-手动修 / 模型自判推进 / 评审人工查平台名）
- **不变式**：既有 1311 pytest 全绿 + consistency 0 ERROR；check-gate.py exit 1/2 返回约定不变

## 2. 工作区布局（双工作区纪律，违反必出事故）

| 路径 | 角色 | 纪律 |
|------|------|------|
| `/home/kity/oclab/agateon/.worktrees/agate-TAG0027` | **本任务 worktree（改造对象）** | 在这里改代码、写阶段产出、跑测试、git commit |
| `/home/kity/oclab/agateon`（主 checkout） | 协议本体 + 任务数据 + `~/.agate` 指向 | **禁止改动**。它是稳定版来源，也是 hook 的 AGATE_ROOT |
| `~/.agate`（软链 → 主 checkout/agate） | **稳定版（开发工具）** | **禁止改动**。跑 gate / 读卡片用它 |

**核心原则（AGENTS.md T001 约定沿用）**：
- **跑 gate 用 `~/.agate`**（稳定版），**改代码/跑测试在 worktree**。
- commit 时 pre-commit hook 用 `~/.agate/scripts/pre-commit-gate.sh` 判定——gate 判定对象是 worktree 里的产出文件，但 gate 工具本身是 `~/.agate`。这是有意的：改造期间工具稳定，改造对象变化。
- **⚠️ gate 工具 ≠ 检查对象（最容易搞混的点）**：
  - commit hook 的 gate **判定工具**用 `~/.agate`（稳定版）
  - 但 `check-protocol-consistency.py` **必须用 worktree 自己的**（`python3 agate/scripts/check-protocol-consistency.py`），因为检查对象是 **worktree 里的协议文件**
  - 同理：`python3 ~/.agate/scripts/agate-summary.py` 在 worktree 里跑会显示**主 checkout 的上下文**，不代表 worktree 状态——worktree 自己的状态用 `git log`/`git status` 看
  - 同理：**所有编排/派发类工具脚本**（`agate-inject-card.py`、`agate-render-dispatch-prompt.py`、`agate-next-card.py` 等）都用 `~/.agate/scripts/` 稳定版调用（TAG0016 教训：worktree 相对路径调用会读到 worktree 正在被修改的协议卡片副本，注入未发布的新机制）
- **hook 在共享 git 目录**：worktree 的 `.git` 是文件（指向主 checkout `.git`），hook 实际在主 checkout 的 `.git/hooks/`（pre-commit/commit-msg/pre-push 已软链安装）。worktree commit 时 hook 自动触发。

**已完成的 setup（worktree 已可独立使用）**：
- 依赖齐全：bash / python 3.12 / pyyaml / pytest 9.0.3 / shellcheck / ruff（`~/.venvs/agate-dev/bin/ruff`）
- 基线验证：unit 1191 + regression 28 + integration 92 = **1311 passed**（串行全绿）+ consistency **0 ERROR**（--strict-errors-only，324 存量 WARNING 为历史叙事死链，DEBT0012 语义）
- ⚠️ **基线注记（存量并行偶发，非本任务引入）**：`-n auto` 全量并行下 `test_agate_next_card.py::test_nc_p3_cli_body_sha256_matches_card` 偶发 FAIL（CLI 输出 sha256 与卡片字节漂移，xdist 调度干扰；单文件并行/串行均绿，主 checkout 同现象）。CI 用 `--reruns 1` 兜底（protocol-tests.yml:137），本地复现 CI 口径建议 `--reruns 1 -n auto`，或串行跑确认
- commit hook：指向 `~/.agate`（稳定版），worktree commit 自动触发
- orchestrator 注册：`.opencode/agents/orchestrator.md` + `.claude/agents/orchestrator.md` → `~/.agate/orchestrator-template.md`（符号链接，不拷贝，双平台）
- 工作区解析：`agate_common.py` 输出 worktree 自己的 `agate-workspace/`
- 任务数据：TAG0027 P0-brief + .state.yaml phase=P0 在 worktree 的 `agate-workspace/tasks/`

## 3. 任务范围（P0-brief 已锁定，P1 细化 BDD）

### 已核实并确认的需求（全部有设计文档/权威源证据，见 P0-brief + design-orchestration-semantics.md v3b）

**设计文档 v3b（2026-09-02 三轮独立评审闭环）**：
- **Phase 1（转移表结构化）**：`rules/phases.yaml` 增 `next`/`retreat` 字段（或扩展 `rules/state-transitions.md` 数据面），对齐 `state-machine.md` 既有转移语义（P5/P6→P4、P6.5→P6、diff≥2→PAUSED）；新增字段纳入既有 S-1/S-2 双向一致性 gate（`check-structure-consistency.py`，md 侧锚点 WORKFLOW.md 阶段总览表）——不新开独立一致性检查
- **Phase 2（推进侧 CLI）**：新增 `agate next`/`agate advance`，消费 `check-state-transition.py` 跳变校验 + `check-gate.py` exit 三态（0 直推 / 1 回退 / 2 暂停转主 Agent + exit 2 落盘 `exit2-resolution` 机器可读产物）；与 `agate-retreat-to.py` 回退侧对接；`loop-orchestration.md` 档位 C 自动推进改走 `agate next`；补 BDD"档位 C 全程用 agate next 推进，主 Agent 未自行判断进入下一 phase"
- **Phase 3（编排心智统一文档化）**：dispatch-protocol 五模式为唯一语义锚点，平台差异（workflow/ralph/goal）全部挂「实现注记」标记（4.3 结构性判据格式约定）；排查协议文档语义小节平台名污染
- **Phase 4（渲染层 + 注入自动化，方案 A：渲染时注入）**：派发=单命令自动注入渲染，**主 Agent 不直接调用 `agate-inject-card.py`**——dispatch 上下文渲染时动态拼装 phase-card（Lazy Injection），消灭"占位符缺失→注入失败→手动修"环节；审计 2 联动走 **A1 路线**：`check-p6-provenance.py` 审计 2 的扫描对象从"静态文件"改为"渲染产物"（卡片块在渲染层标记来源，排除逻辑不变）；`agate-card-inject.py`/`agate-inject-card.py` 保留兼容路径（纯手工写上下文场景兜底）
- **护栏 1 机械化**：`check-protocol-consistency.py` 增加"含平台名无实现注记标记段落"扫描（结构性判据，非文件名单）——把护栏从"评审时检查"升级为"CI 硬校验"

### 核心约束（不可违反）
1. **Linux 现状是基线**——现有 1311 pytest 测试全绿是回归底线，每个改动必须保持全绿
2. **不破坏已有协议语义**——本任务新增 CLI 不改既有脚本返回约定（check-gate.py exit 1/2、check-state-transition.py 拦截项）；`rules/phases.yaml` 增字段须过 JSON Schema + S-1~S-6 双向一致性 gate，字段命名与既有 task_fields/gates 结构兼容
3. **P6.5 非独立 phase 口径**（state-machine.md:74-78）——phases.yaml 已有 P6.5 条目，新增 next/retreat 字段不得把它写成独立转移边，保持"挂载于 P6→P7 转移上的强门槛子阶段"
4. **方案 A 两路并存**——渲染时注入是新主路径，但纯手工写上下文 + `agate-inject-card.py` 注入的存量用法必须保留（BDD 覆盖两路）；`agate-render-dispatch-prompt.py` 现有消费方须先确认现状再改
5. **范围锁定**——全量四 phase 已纳入本任务（不分后续任务）；若 P1 分析发现需改动超出 P0-brief 锁定范围，须先停下跟用户确认

## 4. 关键验证命令

```bash
# 在 worktree 根执行：

# 全量测试（必须全绿才算过；并行有 1 例存量偶发见 §2 基线注记，串行必绿）
python3 -m pytest agate/tests/ --reruns 1 -n auto
# 或串行（确认基线）：python3 -m pytest agate/tests/

# 一致性（0 ERROR 才行；必须用 worktree 自己的脚本）
python3 agate/scripts/check-protocol-consistency.py --strict-errors-only

# shellcheck
shellcheck -S warning agate/scripts/*.sh

# 测试计数（验证文档没漂移）
bash agate/tests/scripts/count-tests.sh

# 单脚本测试（改哪个跑哪个，TDD 先红后绿）
python3 -m pytest agate/tests/unit/test_{具体测试文件}.py
```

## 5. 阶段推进纪律（T001 血泪教训）

- **commit 时 phase = 本 commit 产出阶段**：P1 产出 → phase=P1 再 commit；推进 P2 随 P2 产出同 commit。**不要**先写 phase=P2 再 commit P1 产出（pre-commit 会用 P2 gate 检查，P2-design.md 不存在 → 拦截）
- **改脚本走 TDD**：先写失败测试确认红 → 改脚本确认绿（AGENTS.md「改脚本的工作流」）
- **批量机械改动的 TDD 策略**：先写一个"grep 断言审计"测试作为回归拦截；批量改动后跑该断言 + 全量 pytest 确认绿。不要为每个小改动单独写测试，也不要跳过测试直接改
- **git 命令加 timeout**、单步串行（AGENTS.md 工具纪律）
- **commit message 含 `wf(TAG0027-P{阶段}):` 前缀**
- **改 `agate/*.md`、`agate/scripts/*.py/.sh`、`agate/phase-cards/*` 触发 SELF-GATE**：commit message 需含 `self-gate-review:` 或 `self-gate-skip:`（否则 commit-msg hook WARNING）。本任务改 `agate/scripts/*` + `agate/rules/*.yaml` + `agate/loop-orchestration.md` → **必触发 SELF-GATE**，协议文档变更需跑 `check-protocol-consistency.py` 确认无 ERROR

## 6. 任务编号与状态

- 任务目录：`agate-workspace/tasks/TAG0027-orchestration-semantics/`（在 worktree 里）
- `.state.yaml`：phase=P0（P1 开始后推进）
- active-tasks.md「待开始」已有 TAG0027 行
- roadmap：RM-AG0054 关联本任务（scheduled）
- **编号体系**：任务用 `TAG0027`（项目代号 + 动态数字的 Jira 式编号）。校验器 `^T[A-Z]{2}\d+$`

## 7. 已知风险与止损

- **check-gate.py / check-state-transition.py 是核心 gate 消费方**：新增 CLI 不改既有脚本返回约定（1/2），只新增消费方；`rules/phases.yaml` 增字段须过 JSON Schema + S-1~S-6 gate——全量 pytest + consistency 0 ERROR 是硬门槛 → 止损：先加失败测试确认红，改完跑全量回归
- **档位 C 对接 loop-orchestration.md 是行为变更**："档位 C 自动推进改走 agate next"须先确认档位 C 现状执行逻辑（主 Agent 逐轮读状态→执行单步），BDD 验证不破坏既有 /loop 手动/半自动档位 → 止损：P1 细化 BDD 时先读 loop-orchestration.md 现状，行为变更点与用户确认
- **转移表语义与 state-machine.md 漂移**：next/retreat 字段值域以 state-machine.md 转移规则为唯一权威（P5/P6→P4、P6.5→P6、diff≥2→PAUSED、P6 exit 2→P6.5 前进特例），schema 校验 + S-1/S-2 双向 gate 防漂移 → 止损：转移表实现照抄 state-machine.md，不搞双套判定
- **exit 2 的模型残留点（设计诚实边界）**：转移表为 exit 2 定义"下一动作"字段并落盘 exit2-resolution，但不假装消灭模型自判——CLI 在 exit 2 分支暂停转主 Agent 是设计意图而非缺陷 → 止损：文档明确标注，P6.5 judge 复核范围含 exit2-resolution 产物
- **方案 A 渲染时注入 vs 审计 2 联动（check-p6-provenance.py 审计 2，318-355 行）**：审计 2 现在靠 dispatch-context 物理占位符块排除卡片内容（P6 卡片本身含 PASS/FAIL 模板字样）——改渲染时注入后文件里无物理卡片块，审计 2 失去静态锚点，须改扫渲染产物（A1 路线）→ 止损：P2 设计先定"渲染产物标记来源"契约，BDD 覆盖"渲染输出含卡片块时排除逻辑仍生效 + 手工写上下文场景文件版兜底"
- **渲染时注入是行为变更（agate-inject-card.py / agate-card-inject.py / agate-render-dispatch-prompt.py）**：改派发路径不得破坏手工写上下文 + 注入的存量用法 → 止损：P1 先读三个脚本现状 + grep 消费方，两路并存 BDD 化
- **存量并行偶发测试**（§2 基线注记）：`-n auto` 全量并行偶发 FAIL 为存量问题，非本任务引入 → 止损：CI 口径 `--reruns 1 -n auto`；疑似本任务引入时用串行对照区分

## 8. 完成后

- P8 gate + READY → 提 PR 合并 main（PR 普通 merge 非 squash，tag 要求）
- **合并前在 PR 里看 CI 结果**——pytest/shellcheck/consistency/gate-backstop 全绿才算过
- roadmap 回写 RM-AG0054 → done
- 复盘按 agate 自身变更流程归档（合并后在主 checkout 写复盘 + 更新 roadmap/版本）

## 9. 交接确认

- worktree 基线：unit 1191 + regression 28 + integration 92 = **1311 pytest passed**（串行）+ consistency **0 ERROR**（--strict-errors-only；324 存量 WARNING 为历史叙事死链）
- hooks 就位（指向 `~/.agate` 稳定版）、orchestrator 已注册（双平台符号链接）、依赖齐全
- 任务数据就绪：TAG0027 P0-brief + .state.yaml phase=P0
- 交接单位置：`HANDOFF-TAG0027.md`（worktree 根，已 commit）

---

> 模板字段：任务编号、任务标题/一句话、worktree/主 checkout 路径、缺陷清单（文件:行号:问题）、核心约束、验证命令、阶段纪律、风险、完成后动作。
