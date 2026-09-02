---
review_date: 2026-09-02
reviewer: independent-design-review
change_summary: subagent 存活可观测性与自主再派发设计 v3 独立评审——评审链核验（v1 FAIL/v2 PASS 真实性）+ 新发现（心跳载体与 task 工具派发模型不兼容）
files_reviewed: [design-subagent-liveness-and-self-dispatch.md (当前 213 行), review-subagent-liveness-and-self-dispatch-v1-20260902.md, review-subagent-liveness-and-self-dispatch-v2-20260902.md]
status: FAIL
---

# subagent 存活可观测性与自主再派发设计 v3 独立评审

审查对象：`docs/design-notes/design-subagent-liveness-and-self-dispatch.md`（213 行，v2 声称已复审 PASS，候选 RM 编号待定）。
权威规则源：`agate/dispatch-protocol.md`（铁律 1 工具派发 / 五模式 / 并行规则 / subagent 超时判定）、`agate/state-machine.md`、`SELF-GATE.md`、`agate/platform-notes.md`。

## 结论汇总

| # | 问题 | 级别 | 归属 |
|---|------|------|------|
| B1 | **心跳包装脚本载体与既有 task 工具派发模型不兼容**——§3.2 的 `agate-heartbeat-wrap.sh` 以 `"$@"` 包装"subagent 派发命令"，隐含假设派发是 shell 命令；但 dispatch-protocol.md 铁律 1（17-19 行）规定主 Agent 用 **task 工具**派发，工具调用无法被 shell 脚本包装。机制在主流派发模型下的落地路径未定义 | **BLOCKER** | 设计内容 |
| B2 | **主 Agent 阻塞等待时无心跳检查执行时机**——dispatch-protocol.md:648 明确"Task 工具本身无超时参数，subagent 挂起会无限阻塞主 Agent"；阻塞等待期间主 Agent 无法"周期检查心跳文件"（§3.2 三支判定的前提）。心跳机制只对异步派发平台（DSH background subagent）成立，对阻塞派发平台（Claude Code/OpenCode task 工具）需改为"中止前二次确认"用法，文档未区分 | **BLOCKER** | 设计内容 |
| R1 | **v2 复审声称的 N1 闭合不实**——v2 复审第 23 行"N1 ✅ 闭合：README.md 已新增本文档条目"，实测 `docs/design-notes/README.md` 中 `design-subagent-liveness-and-self-dispatch` 匹配数为 **0**，未登记。评审链证据与事实不符 | **WARNING** | 评审链 |
| R2 | **v2 审查对象版本与当前存档不一致**——v2 声称审查"214 行"版本，当前文件 `wc -l` 与 `grep -c ''` 均为 **213 行**，差 1 行。审查版本与存档版本未对齐，PASS 结论对应的文件版本不明确（时间线：design-note mtime 23:42:09 < v1 23:44:19 < v2 23:44:25，文件 mtime 早于两份评审，行数却与 v2 声称不符）| WARNING | 评审链 |
| W1 | 阻塞模型下 §3.2 三支判定的触发时点未定义（与 B2 同源，独立记录：即使引入 watcher 进程，也需要平台支持在等待期间并行执行/中断，文档未说明）| WARNING | 设计内容 |
| N1 | 未提及与 `agate-archive-stale-outputs.py` 之外的既有产物清理清单（`.retreat-history.md` 等）的交互 | NIT | 设计内容 |

## 评审链核验（v1/v2 真实性 + 证据一致性）

| 声称 | 核验结果 |
|------|---------|
| v1 评审存在（185 行版，2 BLOCKER+3 WARNING+3 NIT，FAIL）| ✅ 属实，`review-...-v1-20260902.md` 存在，结论 FAIL，B1/B2 论证有据（五维评级 high 判据引用 dispatch-protocol.md:509 一致）|
| v2 复审存在（214 行版，逐条闭环，PASS）| ⚠️ 文档存在且逐条闭环表完整，但见 R1（N1 闭合不实）与 R2（行数不符）|
| v2 声称"章节编号乱序已修复" | ✅ 属实，当前 §3.4 生命周期定义（126 行）在 §3.5 影响面（134 行）之前 |
| v2 声称"全角字符残留已修复" | ✅ 属实，§4.4 无全角"選擇"残留 |
| v2 声称 "N1 ✅ 闭合：README 已登记" | ❌ **不实**——README 匹配 0（R1）|
| 时间线合理性（文档先、评审后）| ⚠️ mtime 顺序合理，但文档 213 行 vs v2 声称 214 行无法用时间线解释（R2）|

## B1（BLOCKER）：心跳包装脚本载体与 task 工具派发模型不兼容

§3.2 机制设计给出 `agate-heartbeat-wrap.sh`：

```bash
TASK_DIR=$1; shift
...
"$@"                      # 真正执行 subagent 派发命令
EXIT_CODE=$?
```

其语义是"把派发命令包进 shell 脚本，脚本后台跑心跳 touch + 前台执行派发"。但 Agateon 的派发协议（dispatch-protocol.md:17-19 铁律 1）：

> 用 task 工具派发，动词是"派发"不是"执行"。主 Agent 到了某个阶段，不自己产出文件，而是调用 task 工具启动一个 subagent。

**主 Agent 派发 subagent 是平台工具调用（task/Agent/subagent 工具），不是 shell 命令**。工具调用无法放进 `"$@"` 被 shell 脚本包装——主 Agent 不能"经由心跳包装脚本调用 task 工具"。因此：

- 若设计意图是"主 Agent 启动心跳守护进程 + 照常调 task 工具"，则脚本形态应改为 heartbeat-daemon（只 touch，不包装派发），§3.2 示例与命名（wrap）均误导
- 若设计意图是"派发走 CLI"（如 §4.3 OpenCode 的 `opencode run`），则与铁律 1 的 task 工具主路径冲突，需要说明 CLI 派发仅限哪些场景，且文档未定义两条路径的取舍

**修复建议**：明确心跳产生机制与派发载体的关系，二者选一并修正示例代码：① 心跳守护进程独立于派发（主 Agent 用 bash 起守护，再调 task 工具）；② 或显式限定心跳仅用于 CLI 派发路径，工具派发路径另行定义心跳来源。

## B2（BLOCKER）：阻塞等待模型下无心跳检查执行时机

dispatch-protocol.md:648（subagent 超时判定节）：

> Task 工具本身无超时参数。subagent 内部脚本挂起会无限阻塞主 Agent。

主 Agent 调用 task 工具派发后处于**阻塞等待**状态——它没有"等待期间周期检查 `.heartbeat` mtime"的执行机会（三支判定的前提是主 Agent 能主动读文件）。心跳检查若要成立，需要：

- 平台支持异步派发 + 主 Agent 并行（DSH background subagent 成立；Claude Code/OpenCode task 工具不成立），或
- 平台支持超时回调/中断钩子（§3.2 提到的 `kill -0` 二次确认需在主 Agent 决定中止时执行，但阻塞中主 Agent 无法自主触发"决定中止"之外的动作）

**修复建议**：按派发模型拆分心跳用法——异步派发平台：主 Agent 周期轮询心跳（三支判定成立）；阻塞派发平台：心跳降级为"中止前二次确认"信号（主 Agent 已主观决定中止 → 查心跳 → 新鲜则继续等），并修改 §1.2 目标表述（阻塞平台下心跳解决的是"避免误杀"，不是"主动发现卡死"）。§3.2 当前对两种模型使用同一套三支判定，落地必然冲突。

## R1（WARNING）：v2 复审 N1 闭合不实（评审链证据缺陷）

v2 复审闭环表 N1 行："✅ 闭合。README.md 已新增本文档条目"。实测 `grep -c "design-subagent-liveness-and-self-dispatch" docs/design-notes/README.md` = **0**。README 现有 subagent 相关条目仅 `subagent-empty-return-root-cause.md` 与 `subagent-context-mechanism.md`，无本篇。

按本仓库评审纪律（PASS 需落盘证据、评审链时间线须在快照内可见），v2 的 PASS 标签存在**一处证据核验失实**。这不影响 v1 的真实性，但要求：补登 README 后由评审者确认，或在本评审中记录为待修复项。

## R2（WARNING）：v2 审查版本与存档版本行数不一致

v2 复审声明"审查对象 214 行"，当前存档文件实测 **213 行**（`wc -l` 与 `grep -c ''` 均为 213）。有两种可能：① v2 数错了；② v2 审查后文件又改过 1 行（但 mtime 23:42:09 早于 v2 落盘 23:44:25，不支持"复审后修改"）。无论哪种，**PASS 结论对应的文件版本与当前存档未对齐**，需确认 v2 审的确切版本。

## 事实核验（设计内容 vs 仓库现状，补充 v1/v2 已核验项之外的）

| 声称 | 核验结果 |
|------|---------|
| "Task 工具本身无超时参数…无限阻塞主 Agent"（隐含前提，§3.2 未引用）| ✅ 属实（dispatch-protocol.md:648）——但文档未处理该事实对心跳检查时机的冲击（B2）|
| "用 task 工具派发"（§1.1 现状描述隐含）| ✅ 属实（铁律 1）——与 §3.2 shell 包装示例冲突（B1）|
| "opencode run CLI 路线未经实测"（§4.3 注）| ✅ 已诚实标注，风险表有对应行（W2 闭合属实）|
| "judge 类角色不适用子派发"论证（§4.4）| ✅ 论证链完整（决策路径主观性 vs fresh context），W3 闭合属实 |
| "与 RM-AG0054 在 exit 三态/实现注记概念交叉"（§6 事项 4）| ✅ 属实，且本评审的 B1/B2 进一步显示两设计在"派发载体"上也有交叉面（TAG0027 的渲染时注入同样涉及派发路径改造）|

## 是否通过

**FAIL**——v1 的两条 BLOCKER 修复（B1→§1.5 核验节、B2→§3.4 生命周期定义）经核验**属实**，v1 的 W1-W3 修复也**属实**；但 v3 独立评审发现两条**新的 BLOCKER**（B1 心跳载体与 task 工具派发模型不兼容、B2 阻塞等待下无心跳检查时机），且评审链自身存在两处证据缺陷（R1 README 未登记、R2 审查版本行数不符）。设计文档需修复 B1/B2 后重新提交复审；R1/R2 需补登 README 并确认审查版本对齐。

> 说明：本评审对 v1/v2 评审文档的"内容判断"予以认可（B1/B2/W1-W3 的修复核验均属实），FAIL 结论源于**新发现的设计缺陷**与**评审链证据问题**，不是对既有评审工作的否定。
