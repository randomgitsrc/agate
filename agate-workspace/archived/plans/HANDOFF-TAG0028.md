# TAG0028 交接单 — subagent 存活可观测性与受控自主再派发（RM-AG0055）

> 本交接单供 worktree session 的 agent 按此启动 TAG0028 任务。
> 任务已 P0 立项（.state.yaml phase=P0，P0-brief.md 已就绪）。
> worktree 已完成构建安装与基线验证，可直接开始 P1。

---

## 1. 你要做什么

**TAG0028**：subagent 存活可观测性与受控自主再派发（RM-AG0055）。

**一句话**：命令流日志机制（从平台会话记录外部获取活动信号）机械检测 subagent 卡死/空转 + 心跳文件生命周期 + 执行角色受控自主再派发（judge 例外）。

**设计文档**：`docs/design-notes/260903-design-subagent-liveness-and-self-dispatch/design-subagent-liveness-and-self-dispatch-v5-with-cmdstream-validation.md`（v5，4 轮独立评审 + 三平台数据源实机验证闭环，已在 main）。数据源实机验证：同目录 `verification-cmdstream-datasource-20260903.md`。检测引擎验证脚本：同目录 `verify-heartbeat-cmdstream/verify_cmdstream_detection.py`（9 场景全 PASS，已入库）。

## 2. 工作区布局（双工作区纪律，违反必出事故）

| 路径 | 角色 | 纪律 |
|------|------|------|
| `/home/kity/oclab/agateon/.worktrees/agate-TAG0028` | **本任务 worktree（改造对象）** | 在这里改代码、写阶段产出、跑测试、git commit |
| `/home/kity/oclab/agateon`（主 checkout） | 协议本体 + 任务数据 + `~/.agate` 指向 | **禁止改动**。它是稳定版来源，也是 hook 的 AGATE_ROOT |
| `~/.agate`（软链 → 主 checkout/agate） | **稳定版（开发工具）** | **禁止改动**。跑 gate / 读卡片用它 |

**核心原则（AGENTS.md T001 约定沿用）**：
- **跑 gate 用 `~/.agate`**（稳定版），**改代码/跑测试在 worktree**。
- commit 时 pre-commit hook 用 `~/.agate/scripts/pre-commit-gate.sh` 判定——gate 判定对象是 worktree 里的产出文件，但 gate 工具本身是 `~/.agate`。
- **⚠️ gate 工具 ≠ 检查对象**：
  - commit hook 的 gate **判定工具**用 `~/.agate`（稳定版）
  - 但 `check-protocol-consistency.py` **必须用 worktree 自己的**（`python3 agate/scripts/check-protocol-consistency.py`），检查对象是 **worktree 里的协议文件**
  - **所有编排/派发类工具脚本**（`agate-inject-card.py`、`agate-render-dispatch-prompt.py`、`agate-next-card.py` 等）都用 `~/.agate/scripts/` 稳定版调用（TAG0016 教训）
- **hook 在共享 git 目录**：worktree 的 `.git` 是文件（指向主 checkout `.git`），hook 实际在主 checkout 的 `.git/hooks/`（pre-commit/commit-msg/pre-push 已软链安装）。

**已完成的 setup（worktree 已可独立使用）**：
- 依赖齐全：bash / python 3.12 / pyyaml / pytest 9.0.3 / shellcheck / ruff（`~/.venvs/agate-dev/bin/ruff`）
- 基线验证：全量 pytest 全绿 + consistency 0 ERROR（--strict-errors-only）——见 §9
- commit hook：指向 `~/.agate`（稳定版），worktree commit 自动触发
- orchestrator 注册：`.opencode/agents/orchestrator.md` + `.claude/agents/orchestrator.md` → `~/.agate/orchestrator-template.md`（符号链接，双平台）
- 工作区解析：`agate_common.py` 输出 worktree 自己的 `agate-workspace/`
- 任务数据：TAG0028 P0-brief + .state.yaml phase=P0 在 worktree 的 `agate-workspace/tasks/TAG0028-subagent-liveness-self-dispatch/`

## 3. 任务范围（P0-brief 已锁定，P1 细化 BDD）

### 已核实并确认的缺陷/需求（全部有代码/实测证据，见设计文档 §1-§3.4）

**触发源（用户实测观察）**：
- 长尾 subagent（P4 implementer backend 27M tok / 运行超 1 小时）导致主 Agent 无法判断"卡死 vs 仍在正常工作"，曾因等待超时误判并中止仍在运转的 subagent → 命令流日志机制（§3.4.2）
- subagent 内部执行遇到多方向排查/多子任务并行场景时缺乏受控自主再派发能力 → §4

**三平台数据源实机验证结论（verification-cmdstream-datasource-20260903.md）**：
- Claude Code：`~/.claude/projects/<dir>/<session>.jsonl`，`assistant` 消息带 `isError` + `"Exit code N"` 前缀（无数字 exit 字段）
- OpenCode：`~/.local/share/opencode/storage/session/<id>/info.json + messages.json`，tool 调用 `calls`/`results` 数组，整数 `exit` 字段
- **DSH：`~/.dsh/sessions/<sanitized-cwd>/<session-id>/session.jsonl.zstd`**——JSONL + zstd 拼接帧容器（Node 24 原生 `node:zlib.zstdDecompress` 可解，无 python zstandard/zstd 二进制时勿硬依赖）；`tool/call`+`tool/result` 毫秒时间戳、`arguments.command`、`isError` + `"Error:"` 前缀（无数字 exit）；实时写入 0.96ms；配对 634/635
- 三类活动信号：model 思考（reasoning-chunks）/ model 输出（assistant, text-chunks）/ 执行 tool（tool/call + tool/result）
- 实测节奏（DSH 会话 30432 事件）：思考间隙 p50=9.8s/p95=94s/p99=742s/max≈1239s（40 次>60s、12 次>300s）；执行阶段 p95=12s/p99=189s/max≈925s；reasoning chunk 内部间隔 p95=3.8s；活动静默 p99=7.4s/p99.9=154s；bash 命令 p50=57ms/p95≈7s/max≈196s

**§6 待确认事项现状**：事项 1/2/3/5/7 待 P1 处理（均不阻塞立项）；事项 4（RM 排期交叉）与事项 6（三平台验证）已解决。

### 核心约束（不可违反）

1. **Linux 现状是基线**——现有全量 pytest 全绿是回归底线，每个改动必须保持全绿
2. **不破坏已有协议语义**——本任务不改 `check-gate.py` / `check-state-transition.py` 返回约定（心跳判定与 gate 判定是两套独立信号）；`agate/rules/*.yaml` 若增字段须过 JSON Schema + S-1~S-6 双向一致性 gate
3. **阈值宁可偏保守（用户明确要求）**——"不要因为 timeout 设置太短，造成本身耗时的任务被强制终止"：默认值宁可多提示、绝不误杀；检测定位"证据 + 触发核查，不自动判死"（§3.4.3 定位原则）
4. **冻结判据不能只看"最后一条命令"（用户明确指正）**——需覆盖三类活动（model 思考/输出/执行 tool）；两级冻结：调用冻结（未结束 call vs expected×2 / 兜底 alert=300/suspect=900）+ 活动冻结（无未结束 call 时最后活动事件距今 alert=60/suspect=300）
5. **三平台解析器不一致是既定现实**——架构按适配器模式（§3.4.4）：统一 CommandRecord IR + 每平台一个适配器 + 检测引擎平台无关；**新增平台只写适配器，检测引擎零改动**（用户强调"后续扩展性要良好"）
6. **judge 类角色不适用本设计**（§4.4）——fresh context 信息隔离与自主再派发决策路径存在性质冲突，judge 不得开放 Agent/subagent_fork 工具权限
7. **范围锁定**——若 P1 分析发现需改动超出 P0-brief 锁定范围，须先停下跟用户确认

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

# 检测引擎验证脚本（9 场景，全部断言通过才算过——本任务 Phase 2 的验收锚）
python3 docs/design-notes/260903-design-subagent-liveness-and-self-dispatch/verify-heartbeat-cmdstream/verify_cmdstream_detection.py
```

## 5. 阶段推进纪律（T001 血泪教训）

- **commit 时 phase = 本 commit 产出阶段**：P1 产出 → phase=P1 再 commit；推进 P2 随 P2 产出同 commit。**不要**先写 phase=P2 再 commit P1 产出（pre-commit 会用 P2 gate 检查，P2-design.md 不存在 → 拦截）
- **改脚本走 TDD**：先写失败测试确认红 → 改脚本确认绿（AGENTS.md「改脚本的工作流」）
- **批量机械改动的 TDD 策略**：先写一个"grep 断言审计"测试作为回归拦截；批量改动后跑该断言 + 全量 pytest 确认绿
- **git 命令加 timeout**、单步串行（AGENTS.md 工具纪律）
- **commit message 含 `wf(TAG0028-P{阶段}):`** 前缀
- **改 `agate/*.md`、`agate/scripts/*.py/.sh`、`agate/phase-cards/*` 触发 SELF-GATE**：commit message 需含 `self-gate-review:` 或 `self-gate-skip:`（否则 commit-msg hook WARNING）。本任务改 `agate/scripts/*` + `agate/dispatch-protocol.md`（RM-AG0023 心跳扩展节改写）+ `agate/state-machine.md`（如有）→ **必触发 SELF-GATE**，协议文档变更需跑 `check-protocol-consistency.py` 确认无 ERROR

## 6. 任务编号与状态

- 任务目录：`agate-workspace/tasks/TAG0028-subagent-liveness-self-dispatch/`（在 worktree 里）
- `.state.yaml`：phase=P0（P1 开始后推进）
- active-tasks.md「待开始」已有 TAG0028 行（⬜ P0）
- roadmap：RM-AG0055 关联本任务（scheduled，2026-09-03 立项）
- **编号体系**：任务用 `TAG0028`（项目代号 + 动态数字的 Jira 式编号）。校验器 `^T[A-Z]{2}\d+$`

## 7. 已知风险与止损

- **外部数据源脆弱性**（验证记录差异点）：三平台存储格式/字段命名完全不同（Claude Code 无数字 exit 靠 "Exit code N" 前缀、DSH 靠 "Error:" 前缀、OpenCode 整数 exit 字段），平台改失败输出格式则解析规则需跟随更新 → 止损：适配器把差异点沉淀在验证记录文档；fixture 样例取自验证记录（脱敏）
- **DSH zstd 解压依赖**：`session.jsonl.zstd` 是拼接帧容器，本机无 python zstandard/zstd 二进制 → 止损：Node 24 原生 `node:zlib.zstdDecompress` 可行（已验证），或把解压隔离在适配器内部（如 spawn node 单行脚本），不许硬依赖未验证的 python 包
- **阻塞派发平台（Claude Code/OpenCode）依赖 subagent 配合**（§3.4 诚实边界）：心跳降级为"中止前二次确认"，不产生新风险敞口也不产生新收益 → 止损：设计上诚实妥协而非缺陷，文档明确标注
- **轮询循环误报类**（§3.4.3）：`gh pr checks --watch`、`sleep N; check` 合法轮询重复相同签名 → 止损：阈值保守（SPIN_THRESHOLD=5/REPEAT_WINDOW=10/REPEAT_UNIQUE_MIN=3），触发核查后主 Agent 识别循环体消解
- **judge 类角色信息隔离冲突**（§4.4）：子派发决策路径是 judge 主观认知过程，可能被诱导或产生确认偏误 → 止损：judge 不得开放子派发权限，派发时显式声明"不启用子派发能力"
- **与 RM-AG0023 职责边界**（§3.4.2 关系说明）：命令流日志取代 progress 心跳扩展的存活判定职责，progress.md 保留语义进展职责 → 止损：落地时同步改写 dispatch-protocol.md 对应节，避免两套信号定义漂移
- **关联 DEBT**（本任务可顺带解决或引用）：DEBT0024（P3 测试夹具走真实 gate 语义——本任务检测引擎测试若测 gate 消费方须引真实 gate）、DEBT0025（新 CHECK 上线前先全量扫描）、DEBT0026（单 agent 大任务拆小——本任务 §4 自主再派发与之互为补充，外部拆小是现状兜底、内部自主拆是根治方向）

## 8. 完成后

- P8 gate + READY → 提 PR 合并 main（PR 普通 merge 非 squash，tag 要求）
- **合并前在 PR 里看 CI 结果**——pytest/shellcheck/consistency/gate-backstop 全绿才算过
- roadmap 回写 RM-AG0055 → done
- 复盘按 agate 自身变更流程归档（合并后在主 checkout 写复盘 + 更新 roadmap/版本）；复盘模板 `agate/assets/templates/retrospective-template.md`，含"agate 反馈"去向登记（关联 DEBT0024-26 现状核验）

## 9. 交接确认

- worktree 基线全绿：全量 pytest + consistency 0 ERROR（--strict-errors-only）
- hooks 就位（指向 `~/.agate` 稳定版）、orchestrator 已注册（双平台）、依赖齐全
- 任务数据就绪：TAG0028 P0-brief + .state.yaml phase=P0
- 交接单位置：`HANDOFF-TAG0028.md`（worktree 根，已 commit）
- 验证脚本就绪：`verify_cmdstream_detection.py` 9 场景全 PASS（Phase 2 验收锚）
