---
phase: P1
task_id: TAG0028
trace_id: TAG0028-P1-20260903
agent: requirements-review
status: approved
---
# P1 需求基线评审 — TAG0028（requirements-review · 复审轮 fix1）

> 评审对象：`P1-requirements.md`（analyst fix1 修复后，BDD-1~33，含 §11 修复轮记录）
> 评审角色：requirements-review（独立评审 subagent，agent≠main）
> 评审日期：2026-09-03 · 轮次：复审轮 fix1（上轮结论 needs-revision，subagent de346328）
> 输入：fix1 dispatch-context + 上轮 dispatch-context + 上轮 P1-review.md + P0-brief + 设计文档 v5 + verify_cmdstream_detection.py + 角色文件 + AGENTS.md

## 评审结论

**approved** —— 上轮 3 项红线 + 3 项次要全部确认修复（非仅措辞），编号完整性、机制数值一致性、既有 BDD 语义保持均核验通过，无新增问题。gate 判定依据本文件 Header `status: approved`。

## 上轮结论项 1-6 修复核验（逐条对照）

1. **红线 1（BDD-4 混实现细节）→ 已修复**：BDD-4 标题改「dsh 适配器从 JSONL.zstd 解析命令流（解压隔离在适配器内部）」（line 106），Then 改行为化表述「解压全程隔离在 dsh 适配器内部完成（适配器之外不存在解压逻辑）、逐帧拼接后产出统一 CommandRecord IR，且解析不依赖 python zstandard/zstd 二进制」（line 109）——不再点名任何实现 API（zlib.zstdDecompress 等）。capability_requirements 保留「Node 24 原生 zlib.zstdDecompress」环境事实声明（line 297），属能力声明非 BDD 实现细节，fix1 dispatch 明确允许保留，不违规。
2. **红线 2（I-4 子 agent 会话定位无锚点）→ 已修复**：新增 BDD-5（line 111-114），Given 锚定主会话与子 agent 会话文件并存（Claude Code sidecar `subagents/agent-*.jsonl` / DSH 独立 session 文件 delegationDepth 区分层级），When 经适配器 list_sessions/read_commands 定位，Then 要求按平台规则定位到子 agent 会话文件并解析、仅读主会话会漏记录、定位结果与主会话可区分——可二值判定；list_sessions/read_commands 属设计 §3.4.4 契约接口名（line 257-258），非实现细节。对应设计 §3.4.4 line 268 与验证记录 line 190/201 原文一致。
3. **红线 3（多场景未拆号）→ 已修复**：
   - 原调用冻结兜底（300/900 两级）拆为 BDD-9（alert，When 超 300s 未超 900s）/ BDD-10（suspect，When 超 900s），各一条 Given-When-Then（line 133-141）
   - 原活动冻结（60/300 两级）拆为 BDD-11（alert，When 超 60s 未超 300s）/ BDD-12（suspect，When 超 300s），各一条 Given-When-Then（line 143-151）
   - 原阈值配置三场景拆为 BDD-19（显式覆盖生效）/ BDD-20（配置缺失兜底）/ BDD-21（配置损坏兜底），各一条 Given-When-Then（line 183-196）
4. **次要 4a（签名变化不误报独立编号）→ 已修复**：BDD-15（无效重复·结果签名变化不误报）独立成条（line 163-166），Then 判定 NORMAL 不触发空转信号，单一 GWT。
5. **次要 4b（REPEAT_UNIQUE_MIN=3 入 BDD）→ 已修复**：新增 BDD-16（line 168-171），覆盖验证脚本 line 44/148-151 语义——窗口 10 内唯一命令数 <3 且结果签名在变化 → NORMAL + 信息级提示、不判空转（合法迭代特征）。
6. **次要 5（I-15 平台无关输出补锚）→ 已修复**：新增 BDD-24（line 208-211），检测/派发输出为平台无关指令形态（判定类别+原因+阈值依据+建议动作方向），不含平台工具名/平台命令调用，三平台食谱原样消费——与 BDD-23（证据+核查不判死）互补。

**编号重排核算**：25 → 33，净增 8 = 拆分净增 5（原 BDD-8→2 条 +1、原 BDD-9→2 条 +1、原 BDD-11 对照场景拆出 BDD-15 +1、原 BDD-14→3 条 +2）+ 新增 3（BDD-5 / BDD-16 / BDD-24），核算正确（§11 记录一致）。

## BDD 逐条评审（锚点）

- BDD-1（统一 CommandRecord IR 字段完整性）：可二值判定 ✓；覆盖维度：数据✓（十字段契约+类型）
- BDD-2（claude-code JSONL 解析）：可二值判定 ✓；覆盖维度：数据✓（tool_use/tool_result 配对、is_error + "Exit code N" 文本前缀→exit_signal）
- BDD-3（opencode SQLite 解析）：可二值判定 ✓；覆盖维度：数据✓（state.metadata.exit 整数、truncated 显式标记）
- BDD-4（dsh JSONL.zstd 解析，行为化）：可二值判定 ✓；**上轮混入实现细节已去除**；覆盖维度：数据✓、边界✓（无 python zstandard 环境约束）
- BDD-5（子 agent 会话定位，新增）：可二值判定 ✓；锚定 sidecar / delegationDepth 层级规则（设计 §3.4.4 line 268）；list_sessions/read_commands 为契约接口名可接受；覆盖维度：多端✓
- BDD-6（新增平台只写适配器、引擎零改动）：可二值判定 ✓；覆盖维度：多端✓（适配器注册机制）
- BDD-7（fixture 取自验证记录且脱敏）：可二值判定 ✓；覆盖维度：数据✓、兼容✓（脱敏/真实会话隔离）
- BDD-8（调用冻结主信号 expected×2）：可二值判定 ✓；数值与脚本 line 246 `max(expected×2,30)` 一致（下限 30s）；覆盖维度：边界✓
- BDD-9（调用冻结兜底 alert 300s，拆出）：可二值判定 ✓；单一 GWT；数值与设计 §3.4.3 line 211 一致；覆盖维度：边界✓
- BDD-10（调用冻结兜底 suspect 900s，拆出）：可二值判定 ✓；单一 GWT；数值一致；覆盖维度：边界✓
- BDD-11（活动冻结 alert 60s，拆出）：可二值判定 ✓；单一 GWT；数值与设计 line 212 一致；覆盖维度：边界✓、多端✓（三类活动事件）
- BDD-12（活动冻结 suspect 300s，拆出）：可二值判定 ✓；单一 GWT；数值一致；覆盖维度：边界✓
- BDD-13（三类活动信号均计入、长时间思考不误杀）：可二值判定 ✓；与 BDD-11/12 判据一致（reasoning 属活动事件）；覆盖维度：边界✓（对应实测 max≈1239s）
- BDD-14（无效重复 SPIN）：可二值判定 ✓；数值与脚本一致（REPEAT_WINDOW=10、SPIN_THRESHOLD=5）；覆盖维度：边界✓
- BDD-15（结果签名变化不误报，拆出）：可二值判定 ✓；单一 GWT；与 BDD-14 判据互补；覆盖维度：边界✓
- BDD-16（REPEAT_UNIQUE_MIN=3 信息级提示，新增）：可二值判定 ✓；锚定脚本 line 44/148-151；覆盖维度：边界✓
- BDD-17（截断输出不参与哈希比对）：可二值判定 ✓；与 BDD-14 排除关系一致、仍参与冻结检测（对应脚本 G 场景）；覆盖维度：边界✓
- BDD-18（轮询循环误报标注）：可二值判定 ✓；信号定位"核查提示"而非自动判定/自动终止，与 known_risks「轮询循环误报类」一致；覆盖维度：边界✓、兼容✓
- BDD-19（阈值显式覆盖生效，拆出）：可二值判定 ✓；单一 GWT；maintainability.yaml 模式与设计 line 288 一致；覆盖维度：边界✓
- BDD-20（阈值配置缺失兜底，拆出）：可二值判定 ✓；单一 GWT；默认值 300/900/60/300/10/5 + REPEAT_UNIQUE_MIN=3 与锚点一致；覆盖维度：边界✓、兼容✓
- BDD-21（阈值配置损坏兜底，拆出）：可二值判定 ✓；单一 GWT；不静默跳过检测；覆盖维度：边界✓、兼容✓
- BDD-22（verify 9 场景全 PASS 保持）：可二值判定 ✓；九场景 A-I 逐一对应脚本 SCENARIOS（line 158-310：调用阻塞/空转/合法迭代/健康长尾/合法长命令/expected 超期/截断排除/长时间思考/活动冻结），结论串与脚本 line 350 一致；覆盖维度：验证✓
- BDD-23（证据+触发核查、不自动判死）：可二值判定 ✓；符合「宁可多提示、绝不误杀」；覆盖维度：边界✓（I-8 锚点）
- BDD-24（检测/派发输出平台无关、由平台食谱消费，新增）：可二值判定 ✓；I-15 补锚完成；覆盖维度：多端✓
- BDD-25（心跳父子分层命名）：可二值判定 ✓；命名 `${TASK_DIR}/.heartbeat` / `.heartbeat.child-{n}` 与设计 §3.5 line 277 一致；覆盖维度：数据✓
- BDD-26（心跳审计豁免确认）：可二值判定 ✓；要求显式登记确认（不靠"默认不扫"假设），与设计 §3.5 line 278 一致；覆盖维度：兼容✓
- BDD-27（任务结束清理+异常遗留兜底）：可二值判定 ✓；复用 agate-archive-stale-outputs 模式（设计 §3.5 line 279）；覆盖维度：兼容✓
- BDD-28（两套信号职责分工改写）：可二值判定 ✓；命令流日志承担存活/卡死判定、progress.md 保留语义进展，与设计 §3.4.2 line 160 一致；覆盖维度：兼容✓
- BDD-29（执行角色子派发不写 .state.yaml）：可二值判定 ✓；两边界之一；覆盖维度：多端✓
- BDD-30（子任务写权限严格子集）：可二值判定 ✓；两边界之二；覆盖维度：多端✓、边界✓
- BDD-31（judge 类角色例外声明）：可二值判定 ✓；不开放 Agent/subagent_fork + 显式声明，与设计 §4.4 一致；覆盖维度：多端✓
- BDD-32（子派发产出收敛、不触发 gate）：可二值判定 ✓；仅父 files_modified 走 D2 校验；覆盖维度：多端✓、兼容✓
- BDD-33（不破坏 gate 返回约定）：可二值判定 ✓；两套独立信号、exit 三态不变，与设计 §3.5 line 287 一致；覆盖维度：兼容✓

编号连续性：BDD-1~33 连续无跳号 ✓（grep 全文件 33 条全命中，无缺号/重号）；每条恰一条 Given-When-Then、可 PASS/FAIL 二值判定 ✓。

## 既有 BDD 语义保持核验（fix1 dispatch 约束）

按语义点核验（fix1 dispatch 约束段引用编号为旧编号映射，与修复后新编号存在位移——按语义核验，不构成 analyst 缺陷）：

- expected×2 下限 30s → BDD-8（脚本 line 246 `max(200×2,30)=400s` 实测口径一致）✓
- 轮询误报标注 → BDD-18（核查提示不自动终止）✓
- 心跳父子命名 → BDD-25（§3.5 line 277）✓
- 心跳审计豁免 → BDD-26（§3.5 line 278）✓
- 子派发两边界 → BDD-29/30（§4.1）✓
- judge 例外 → BDD-31（§4.4）✓
- gate 返回约定 → BDD-33（两套独立信号）✓

## 隐含需求覆盖（I-1~I-15 对照）

| 条目 | BDD 锚点 | 判定 |
|---|---|---|
| I-1 适配器模式 | BDD-6（+BDD-1） | 覆盖 ✓ |
| I-2 文本前缀 exit 解析 | BDD-2 / BDD-4 | 覆盖 ✓ |
| I-3 zstd 解压隔离不硬依赖 | BDD-4（行为化） | 覆盖 ✓（上轮 ⚠ 已消解） |
| I-4 子 agent 会话定位（sidecar / delegationDepth） | **BDD-5（新增）** | 覆盖 ✓（上轮 ✗ 缺口已补） |
| I-5 truncated 不参与哈希 | BDD-17 | 覆盖 ✓ |
| I-6 冻结判据覆盖三类活动 | BDD-11/12/13 | 覆盖 ✓ |
| I-7 阈值可配置 | BDD-19/20/21 | 覆盖 ✓（拆分后单场景） |
| I-8 证据+核查不自动判死 | BDD-23 | 覆盖 ✓ |
| I-9 心跳命名空间管理 | BDD-25/26/27 | 覆盖 ✓ |
| I-10 两套信号职责分工 | BDD-28 | 覆盖 ✓ |
| I-11 子派发两硬边界 | BDD-29/30 | 覆盖 ✓ |
| I-12 judge 例外显式声明 | BDD-31 | 覆盖 ✓ |
| I-13 不破坏 gate 返回约定 | BDD-33 | 覆盖 ✓ |
| I-14 fixture 脱敏 | BDD-7 | 覆盖 ✓ |
| I-15 检测输出平台无关 | **BDD-24（新增）** | 覆盖 ✓（上轮 ⚠ 弱覆盖已补） |

数据✓ 前端 N/A（domains 无 frontend）多端✓ 边界✓ 兼容✓——I-1~I-15 全部锚定，无整维空缺。

## 跨条一致性核对

- BDD-8（有 expected → expected×2）与 BDD-9/10（无 expected → 300/900 分段）互斥互补，Given 条件（有无 expected 声明）无重叠歧义 ✓
- BDD-11/12（60/300 分段）与 BDD-13（长时间思考不误杀）判据一致（最后活动事件，reasoning 算活动）✓
- BDD-14（同签名重复≥5 → SPIN）与 BDD-15（签名变化 → NORMAL）/ BDD-16（唯一命令数<3 → NORMAL+提示）判据互斥互补，无矛盾 ✓
- BDD-17 截断排除关系一致（哈希比对排除、冻结检测保留）✓
- BDD-18 与 BDD-23 轮询不判死一致 ✓
- 阈值数值（300/900/60/300/10/5、expected×2 下限 30s、REPEAT_UNIQUE_MIN=3）与设计 §3.4.3 + 验证脚本常量（REPEAT_WINDOW=10 / SPIN_THRESHOLD=5 / REPEAT_UNIQUE_MIN=3）全一致 ✓
- 子派发四 BDD（29/30/32/33）与 judge 例外（31）边界互不冲突 ✓

## 同类扫描核对（S-1~S-8）

与上轮一致：S-1~S-8 命中清单 + 逐条判定齐全（§3 表），回归拦截声明引用已更新为新编号 BDD-6（新增平台只写适配器）+ BDD-23（检测定位原则）；fix1 未改动本节省内容，结论延续 ✓

## P0-brief 时效性质疑核对

正文 §8 含「已核对 P0-brief 时效性，无漂移」+ 4 条核对依据（目标方案/executor_env/known_risks/轻微项），非空白 ✓；fix1 未改动，结论延续 ✓

## 裁剪合理性核对

- phases 全量 [P1..P8]，无跳过阶段 → 裁剪评审 N/A ✓
- risk_level=medium：协议机制升级（新增脚本 + 协议文档改写，跨 4 phase，SELF-GATE 触发）——与实际风险匹配 ✓
- ceremony=standard：fail-closed 缺省，多文件机制改动不做薄化 ✓（非 full，P7 不可裁条款不触发）
- capability_requirements：dsh-zstd / platform-session-parsing / detection-logic-verification 三项均 available，无 GAP，status 值合法 ✓；无 frontend 域 → 无视觉能力声明 ✓

## 审声明 vs diff 证据

- 声明：risk_level=medium / ceremony=standard / phases=[P1..P8]（全量）/ packages=[agate] / domains=[backend, cli]
- 修复轮改动面：仅 `P1-requirements.md`（任务目录内，BDD 25→33 + §11 修复轮记录），未触碰协议本体；任务本质仍是协议机制升级（P0 commit 999c672 + 0029c75 + 工作区 P1 产出），触发 SELF-GATE、跨 4 phase
- 判定：medium + standard + 全量 phases 与实际改动面匹配，属合理保守档位；**声明与实际一致，不构成打回理由** ✓
- 附注：当前暂存区为空（P1 commit 未发生，符合阶段卡片时序），审声明以分支已提交内容 + 工作区改动为证据面

## P1 纯净性核对

- 上轮唯一违规点（BDD-4 点名 zlib.zstdDecompress）已去除，修复后 P1 纯净性红线通过 ✓
- 可接受引用：BDD-5 list_sessions/read_commands（设计 §3.4.4 契约接口名）；BDD-16 REPEAT_UNIQUE_MIN（阈值常量锚点，fix1 dispatch 明确要求）；BDD-22 verify 脚本文件名与结论串（验收锚）；BDD-2/3/4 数据源字段（is_error / state.metadata / callId 等为数据契约事实，源自验证记录）
- 其余 BDD 均为系统行为视角（解析器输出 / 检测器判定 / 心跳生命周期 / 权限边界），未绑定实现函数 ✓

## 修复轮记录核对（§11）

§11 存在且逐条对应评审结论项 1-6（含编号重排说明、25→33 净增核算、正文旧编号引用同步更新声明）；对照正文核实：回归拦截声明（§3）引用 BDD-6/23、待确认清单（§5）引用 BDD-8~21、§10 下游提示引用 BDD-1~33，均为新编号，无遗留旧编号引用 ✓

[PROD_NOT_TOUCHED] 本评审仅读取任务目录、协议文档、设计文档与验证脚本，全程未接触生产环境，未读取其他用户 DSH 会话。
