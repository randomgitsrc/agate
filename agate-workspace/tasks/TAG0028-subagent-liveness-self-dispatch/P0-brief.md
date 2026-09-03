# P0-brief — TAG0028 subagent 存活可观测性与自主再派发（RM-AG0055）

> 本文件由主 Agent 亲自填写（P0 阶段产出）。设计文档：
> `docs/design-notes/260903-design-subagent-liveness-and-self-dispatch/design-subagent-liveness-and-self-dispatch-v5-with-cmdstream-validation.md`
> （v5，2026-09-02 起 4 轮独立评审 + 命令流日志数据源三平台实机验证闭环；评审存档见同目录
> `review-subagent-liveness-and-self-dispatch-v1~v4-20260902.md`；数据源实机验证见同目录
> `verification-cmdstream-datasource-20260903.md`）。

## task

"在 agate 协议层落地 subagent 存活可观测性与受控自主再派发（RM-AG0055）：**命令流日志机制**——
从平台会话记录（Claude Code JSONL / OpenCode SQLite / DSH JSONL.zstd）外部获取活动信号
（model 思考/输出/执行 tool 三类事件），机械检测两类卡死（调用冻结 = 未结束 call 超期；
活动冻结 = 无未结束 call 且无任何活动超期）与逻辑空转（同命令+同结果签名重复），阈值按
§3.4.3 两级设计（expected×2 主信号复用 RM-AG0023 timeout_seconds + 兜底 alert/suspect），
检测结果定位'证据 + 触发核查、不自动判死'；解析架构按**适配器模式**（统一 CommandRecord IR +
每平台一个适配器 + 检测引擎平台无关，新增平台只写适配器）；**心跳文件生命周期**定义
（命名/审计豁免/清理）；**受控自主再派发**——执行角色子派发权限下放（子任务不写
.state.yaml、写权限严格子集），judge 类角色例外（信息隔离冲突，不得开放）。"

### scope

- **Phase 1（命令流数据源解析层）**：三平台适配器（claude-code / opencode / dsh）+ 统一
  CommandRecord IR（platform/session_id/tool/command/ts_start/ts_end/exit/exit_signal/
  output_hash/truncated）+ 适配器注册机制（配置声明或目录扫描 `adapters/*.py`）+ 解析
  单测（fixture 样例取自验证记录）
- **Phase 2（检测引擎）**：命令流检测器消费 IR——调用冻结（未结束 call vs expected×2 /
  兜底 300s alert + 900s suspect）+ 活动冻结（60s alert + 300s suspect）+ 无效重复
  （窗口 10 重复 ≥5）+ 截断排除 + 轮询误报标注；阈值全部可配置（maintainability.yaml
  模式），验证脚本 `verify_cmdstream_detection.py` 9 场景全 PASS 保持
- **Phase 3（心跳文件生命周期 + 协议文档）**：`.heartbeat` / `.heartbeat.child-{n}` 命名、
  `check-p6-provenance.py` 审计豁免确认、任务结束清理 + 异常遗留兜底（复用
  agate-archive-stale-outputs 模式）；dispatch-protocol.md 改写 RM-AG0023 progress 心跳
  扩展节（命令流日志取代存活判定职责，progress.md 保留语义进展职责）
- **Phase 4（受控自主再派发）**：执行角色（analyst/architect/implementer/verifier）子派发
  权限下放（§4.1 两条边界：不写 .state.yaml / 写权限严格子集）；judge 类角色例外声明；
  dispatch-context 模板补"不启用子派发能力"显式声明（judge）；BDD 覆盖边界行为
- **测试**：`agate/tests/` 新增 pytest 覆盖（适配器解析 / 检测引擎判定 / 心跳文件生命周期
  / 自主再派发边界），BDD 以 P1 定稿为准（计划 ≥16 条）

### out-of-scope

- DSH 心跳钩子机制本身（§3.3 异步路径的钩子附加方式，本任务命令流路径已验证，钩子方案
  仅需实机验证注记，不实现）；OpenCode `opencode run` CLI 子进程路线（§4.3 仅文档指导，
  不封装脚本）
- 平台食谱产品化（DSH workflow 脚本等——检测/派发输出平台无关指令，平台适配由各平台食谱消费）
- 修改 `check-gate.py` / `check-state-transition.py` 返回约定（心跳判定与 gate 判定是两套
  独立信号）；独立 judge 机制本身（已有，不动）
- RM-AG0023 全部机制重构（只改写 progress 心跳扩展的存活判定职责边界，其余不动）

## known_risks

- "外部数据源脆弱性（验证记录差异点）：三平台存储格式/字段命名完全不同（解析器各写一套），
  Claude Code 与 DSH 无数字 exit code 靠文本前缀（'Exit code N' / 'Error:'）解析——平台改
  失败输出格式则解析规则需跟随更新；适配器须把差异点沉淀在验证记录文档，防重复踩坑"
- "阻塞派发平台（Claude Code/OpenCode）依赖 subagent 配合（§3.4 诚实边界）：心跳降级为
  '中止前二次确认'，subagent 不配合则心跳缺失，退回既有'拆分+预期耗时'机制——不产生新
  风险敞口也不产生新收益，设计上诚实妥协而非缺陷"
- "轮询循环误报类（§3.4.3）：`gh pr checks --watch`、`sleep N; check` 合法轮询重复相同
  签名 → 触发核查后主 Agent 识别循环体消解；阈值保守（宁可多提示、绝不误杀），默认值
  偏保守"
- "judge 类角色信息隔离冲突（§4.4）：子派发决策路径本身是 judge 主观认知过程，可能被诱导
  或产生确认偏误，与 fresh context 信息隔离设计直接冲突——judge 不得开放子派发权限，
  派发时显式声明不启用"
- "TPV0095 案例立论（§1.4，可能性 B）：P2 正确评级批拆但批内顺序依赖粒度未被静态评级
  捕捉——立论素材成立；若 P1 细化 BDD 时发现需要更细粒度证据，须停下与用户确认"
- "与 RM-AG0023 职责边界（§3.4.2 关系说明）：命令流日志取代 progress 心跳扩展的存活判定
  职责，落地时须同步改写 dispatch-protocol.md 对应节，避免两套信号定义漂移"

## env_constraints

- 本任务改 `agate/scripts/*`（新增检测/解析脚本）+ `agate/dispatch-protocol.md`（RM-AG0023
  心跳扩展节改写）+ `agate/state-machine.md`（如有）→ **触发 SELF-GATE**，commit message
  须含 `self-gate-review:` 或 `self-gate-skip:`
- 用系统 python（`/usr/bin/python3`）跑 pytest/pyyaml；ruff 用 `~/.venvs/agate-dev/bin/ruff`
- 基线验证用 `--strict-errors-only`（DEBT0012）；编排/派发类工具用 `~/.agate` 稳定版，
  不用 worktree 相对路径（TAG0016 教训）
- DSH 会话文件（`~/.dsh/sessions/*.jsonl.zstd`）为拼接帧容器，解析需 Node zstd 或系统
  zstd；三平台真实会话片段仅作 fixture 样例（脱敏），不得读取其他用户会话

## executor_env

- worktree：`.worktrees/agate-TAG0028`（分支 `feat/TAG0028-subagent-liveness`），构建流程见
  `docs/guides/worktree-dogfooding-guide.md`，交接单 `HANDOFF-TAG0028.md` 按模板全 9 节填写
- 任务目录：`agate-workspace/tasks/TAG0028-subagent-liveness-self-dispatch/`
