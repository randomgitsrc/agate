# TAG0016 交接单 — agate 协议卫生与测试效率

> 本交接单供 worktree session 的 agent 按此启动 TAG0016 任务。
> 任务已 P0 立项（.state.yaml phase=P0，P0-brief.md 已就绪）。
> worktree 已完成构建安装与基线验证，可直接开始 P1。

---

## 1. 你要做什么

**TAG0016**：agate 协议卫生与测试效率（RM-AG0025 + RM-AG0026）。

**一句话**：确立协议文档唯一职责与去重（WORKFLOW/dispatch-protocol/state-machine/platform-notes 已知 6 处交叉重复 + 系统排查防复发）+ 测试重跑审计与跨阶段证据引用（P5 全绿且 P6 前无改动 → P6 regression 引用 P5 产物 + P8 放宽 + xdist 试点）。同属'协议成熟化'簇。

## 2. 工作区布局（双工作区纪律，违反必出事故）

| 路径 | 角色 | 纪律 |
|------|------|------|
| `/home/kity/oclab/agate/.worktrees/agate-TAG0016` | **本任务 worktree（改造对象）** | 在这里改代码、写阶段产出、跑测试、git commit |
| `/home/kity/oclab/agate`（主 checkout） | 协议本体 + 任务数据 + `~/.agate` 指向 | **禁止改动**。它是稳定版来源，也是 hook 的 AGATE_ROOT |
| `~/.agate`（软链 → 主 checkout/agate） | **稳定版（开发工具）** | **禁止改动**。跑 gate / 读卡片用它 |

**核心原则（AGENTS.md T001 约定沿用）**：
- **跑 gate 用 `~/.agate`**（稳定版），**改代码/跑测试在 worktree**。
- commit 时 pre-commit hook 用 `~/.agate/scripts/pre-commit-gate.sh` 判定——gate 判定对象是 worktree 里的产出文件，但 gate 工具本身是 `~/.agate`。这是有意的：改造期间工具稳定，改造对象变化。
- **⚠️ gate 工具 ≠ 检查对象（最容易搞混的点）**：
  - commit hook 的 gate **判定工具**用 `~/.agate`（稳定版）——它读 `~/.agate` 自己的脚本逻辑
  - 但 `check-protocol-consistency.py` **必须用 worktree 自己的**（`python3 agate/scripts/check-protocol-consistency.py`），因为检查对象是 **worktree 里的协议文件**。若误用 `~/.agate` 的 consistency 脚本，会扫到主 checkout 的文件而非 worktree 的改动
  - 同理：`python3 ~/.agate/scripts/agate-summary.py` 在 worktree 里跑会显示**主 checkout 的上下文**（版本/分支/HEAD 是稳定版的），不代表 worktree 状态——worktree 自己的状态用 `git log`/`git status` 看
- **hook 在共享 git 目录**：worktree 的 `.git` 是文件（指向主 checkout `.git`），hook 实际在主 checkout 的 `.git/hooks/`（pre-commit/commit-msg/pre-push 已软链安装）。worktree commit 时 hook 自动触发。

**已完成的 setup（worktree 已可独立使用）**：
- 依赖齐全：bash 5.2 / python 3.12 / pyyaml / pytest 9.0.3 / shellcheck
- 基线验证：全量 pytest 916 全绿（808 unit + 108 regression/integration/sanity）+ consistency 0 ERROR（--strict）
- commit hook：指向 `~/.agate`（稳定版），worktree commit 自动触发
- orchestrator 注册：`.opencode/agents/orchestrator.md` + `.claude/agents/orchestrator.md`（均软链到 `~/.agate/orchestrator-template.md`，双平台）
- 工作区解析：`agate_common.py` 输出 worktree 自己的 `agate-workspace/`
- 任务数据：TAG0016 P0-brief + .state.yaml phase=P0 在 worktree 的 `agate-workspace/tasks/`

## 3. 任务范围（P0-brief 已锁定，P1 细化 BDD）

### 已核实并确认的缺陷/需求（全部有代码证据，见 P0-brief known_risks）

**RM-AG0025 协议文档职责边界与去重（核心，改动面大）**：

已知 6 处交叉重复：
- **①平台适配 ×3**：WORKFLOW L461 / dispatch-protocol L1207 / platform-notes
- **②阶段门槛 ×2**：WORKFLOW 阶段总览表 / dispatch-protocol 可判定门槛规范
- **③派发 prompt 双源**：dispatch-protocol L429-628 / assets/templates/dispatch-prompt.md（N6 修过的双源仍在）
- **④Pre-commit 清单 ×2**：WORKFLOW L303 / state-machine L215
- **⑤重试上限 ×2**：state-machine / dispatch-protocol
- **⑥职责定位混乱**：WORKFLOW 塞 gate 命令/Pre-commit/平台适配；dispatch-protocol 塞派发编排机制

**系统排查要求（用户强调，不只修已知 6 处）**：
- P1 做关键词交叉扫描（每条规则 grep 全仓，出现次数 >1 即潜在双源）
- 职责声明表（每文档一句话职责）
- 内容归属审计
- 生成性扫描（新内容塞错文件）
- 防复发（consistency 加同一关键词多处出现检测）

**RM-AG0026 测试重跑审计与跨阶段证据引用（机制改进）**：

同一任务全量测试最坏 4-5 遍：
- P5 首跑 + P5 重试全量（T027 教训）+ P6 refactor 独立 regression.log（regression_pass 硬校验，P6-acceptance.md L108）+ P8 重跑 P5（P8-release.md L82/118）
- 823 用例单次 106-115s，4-5 遍 = 500+s 重复确认

修复：
- ①审计全量重跑点（逐任务统计）
- ②跨阶段证据引用协议（核心）：P5 全绿 + P6 验收前无代码改动（git log 校验）→ P6 regression 引用 P5 产物；provenance 审计支持引用前序证据 + 无改动声明
- ③P8 放宽（bump 后跑一次而非完整重跑）
- ④xdist 试点（P5 单发场景 -n auto，真实 CI 4 核验证，不与并行派发叠加）

### 核心约束（不可违反）
1. **Linux 现状是基线**——现有 916 pytest 测试全绿是回归底线，每个修复都必须保持全绿
2. **Windows 兼容是增量**——本环境（Linux）无法实测 Windows，靠静态修复 + Linux 回归 + CI matrix 兜底。**不要宣称"已实测 Windows"**
3. **AG0025 去重必须先定义每文档唯一职责，再迁移内容**——避免边改边乱（known_risks 第 2 条）
4. **AG0026 跨阶段证据引用需定义"无改动校验"可判定标准**——P2 设计 git log 对比范围 + "何时不可复用"边界（P6 验收前有代码改动则不能复用）
5. **xdist 需真实 CI（4 核）验证**——本环境 1 核测不出加速，P5 在 CI 上验证，不在本地空测
6. **范围锁定**——若 P1 分析发现需改动超出 P0-brief 锁定范围，须先停下跟用户确认
7. **【强制要求】同类扫描 + 影响面梳理（AG0025 自身是示范）**——P1 必须 grep 全仓每条协议规则的出现次数建影响面表；AG0026 统计各任务实际全量重跑次数。用户明确：不愿意一轮一轮来回改

## 4. 关键验证命令

```bash
# 在 worktree 根执行：

# 全量测试（必须全绿才算过）
python3 -m pytest agate/tests/

# 一致性（0 ERROR 才行；--strict 让 WARNING 也阻断）
# ⚠️ 必须用 worktree 自己的脚本（检查对象是 worktree 里的协议文件），不要用 ~/.agate 的
python3 agate/scripts/check-protocol-consistency.py --strict

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
- **批量机械改动的 TDD 策略**：这类改动每个都写单独测试边际成本高。建议——①先写一个"grep 断言审计"测试作为回归拦截；②批量改动后跑该断言 + 全量 pytest 确认绿。不要为每个小改动单独写测试，也不要跳过测试直接改
- **git 命令加 timeout**、单步串行（AGENTS.md 工具纪律）
- **commit message 含 `wf(TAG0016-P{阶段}):` 前缀**
- **改 `agate/*.md`、`agate/scripts/*.py/.sh`、`agate/phase-cards/*` 触发 SELF-GATE**：commit message 需含 `self-gate-review:` 或 `self-gate-skip:`（否则 commit-msg hook WARNING）。协议文档变更需跑 `check-protocol-consistency.py` 确认无 ERROR。本任务改核心协议文档 + gate 脚本 → 大概率需要 self-gate-review 语义审查

## 6. 任务编号与状态

- 任务目录：`agate-workspace/tasks/TAG0016-protocol-hygiene/`（在 worktree 里）
- `.state.yaml`：phase=P0（P1 开始后推进）
- active-tasks.md「待开始」已有 TAG0016 行
- roadmap：RM-AG0025/RM-AG0026 关联本任务（scheduled）
- **编号体系**：任务用 `TAG0016`（项目代号 + 动态数字）。校验器 `^T[A-Z]{2}\d+$`

## 7. 已知风险与止损

- AG0025 改动面大（WORKFLOW/dispatch-protocol/state-machine/platform-notes/role-system 等）→ 触发 SELF-GATE + consistency 锚点可能失效（CHECK 3/9 引用）→ 每批改动后跑 consistency，锚点失效即修
- AG0025 去重是"改文档结构"→ 先定义每文档唯一职责，再迁移内容，避免边改边乱
- AG0026 跨阶段证据引用是协议机制改进（check-p6-provenance.py 支持引用前序证据）→ P2 需设计"无改动校验"的可判定标准（git log 对比范围）
- AG0026 P6 regression 复用边界：P6 验收前有代码改动（回 P4 修 bug）则不能复用 → P2 需定义"何时不可复用"
- xdist 试点需真实 CI（4 核）验证——P5 阶段在 CI 上验证，不在本地空测
- 防复发机制（consistency 检测同一关键词多处出现）可能产生误报 → 设计需考虑合法多源（如模板引原文）

## 8. 完成后

- P8 gate + READY → 提 PR 合并 main（PR 普通 merge 非 squash，tag 要求）
- **合并前在 PR 里看 CI 结果**（跨平台任务看 matrix 双平台）——pytest/shellcheck/consistency/gate-backstop 全绿才算过
- roadmap 回写关联条目 → done
- 复盘按 agate 自身变更流程归档（合并后在主 checkout 写复盘 + 更新 roadmap/版本）——按 TAG0015 落地的新机制执行（tasks/{Txxx}/retrospective.md + frontmatter 三字段）

## 9. 交接确认

- worktree 基线全绿：916 pytest + consistency 0 ERROR（--strict）
- hooks 就位（指向 `~/.agate` 稳定版）、orchestrator 双平台已注册、依赖齐全
- 任务数据就绪：TAG0016 P0-brief + .state.yaml phase=P0
- 交接单位置：`HANDOFF-TAG0016.md`（worktree 根，已 commit）

---

> 模板字段：任务编号、任务标题/一句话、worktree/主 checkout 路径、缺陷清单（文件:行号:问题）、核心约束、验证命令、阶段纪律、风险、完成后动作。复制到 worktree 根目录 `HANDOFF-TAG0016.md` 填写。