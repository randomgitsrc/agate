# BDD-11 证据：GitHub 仓库改名执行前用户在场放行确认记录

> 本条 BDD 验证的是"改名前是否真的获得了用户在场放行确认"，不是可重新实跑的程序化命令。
> 本文件是人工记录类证据，依据 dispatch-context 约束 3 的指引产出，引用 P4 阶段留存的原始
> 记录 + 本次 P6 验收会话内对该记录的复核确认。

## 1. 原始记录来源

`agate-workspace/tasks/TAG0025-agateon-rename/env-rename-handoff.md`「六、版本记录」表格，
第二行（逐字引用，未改写）：

> | 2026-08-26 | P4 改名执行完成（用户当次会话内明确放行确认后，主 Agent 亲自执行 `gh api -X
> PATCH repos/randomgitsrc/agate -f name=agateon`，响应 `full_name: randomgitsrc/agateon`）+
> §四验收锚 4 条实测全部通过：①`curl -sI https://github.com/randomgitsrc/agate` → HTTP/2 301
> ②`git ls-remote https://github.com/randomgitsrc/agateon.git HEAD` → 正常返回 SHA ③全仓残留
> 扫描（pytest BDD-10 权威判定）PASSED，0 残留 ④`gh api search/repositories -f
> q='agateon in:name'` 首位命中 `randomgitsrc/agateon` | TAG0025 主会话 |

该记录明确写出"用户当次会话内明确放行确认后"才执行 `gh api -X PATCH` 改名调用，与 P1
BDD-11 的 Then 子句要求（"必须先在当前会话内获得用户明确的在场放行确认……若未获得该确认，
不得执行改名调用"）在时序上吻合：确认 → 执行，而非执行 → 事后补记确认。

## 2. 交叉核对：P0-brief 已声明的前置条件拆分

`P0-brief.md` known_risks 一节原文（本次 P6 会话独立重读核对，未采信转述）：

> "不可逆外部操作：GitHub 仓库改名一次、对外可见——执行前须确认：① `gh` 具备 repo 管理权限
> （实测 dry-run 或权限查询）② 用户在场确认放行；改名后立即跑验收锚 4 条（301 / ls-remote /
> 无残留 / in:name）"

P1-requirements.md 第 6 条隐含需求识别原文（本次 P6 会话独立重读核对）：

> "权限核实与放行确认是两件事，必须拆开各自成为前置条件……不能因为①已完成就默认②也完成。"

env-rename-handoff.md 记录的措辞"用户当次会话内明确放行确认后"对应的正是这条②，与①
（`gh` admin 权限，dispatch-context 客观查证信息 A 已核实）是两件分别满足的事，未见"用①
代替②"的记录漏洞。

## 3. 本次 P6 会话内对该记录的复核结论

本次验收（P6 阶段）由 verifier subagent 于工作目录
`/home/kity/oclab/agate/.worktrees/agate-TAG0025` 独立执行，未参与 P4 阶段改名操作本身，
无法对"放行确认当时是否真实发生"做程序化重放（该事件已随会话结束，不可逆重跑）。本条证据
的性质是**对既有记录的复核确认**，而非重新实跑：

- 复核对象：env-rename-handoff.md「六、版本记录」第二行原始记录
- 复核方法：逐字读取原始记录文本 + 交叉核对 P0-brief/P1-requirements 对"权限核实"与
  "放行确认"两个前置条件的独立声明是否被记录满足
- 复核结论：记录文本明确区分"权限已实测具备"（①）与"用户当次会话内明确放行确认后"（②）
  两个独立前置条件，且改名调用（`gh api -X PATCH`）的执行时点记录在②之后，与 BDD-11 的
  Then 子句时序要求一致。未发现"仅凭权限核实即执行改名"的记录漏洞。

**结论：PASS**（基于人工记录核对，非程序化断言；证据形式符合 dispatch-context 约束 3 对
本条 BDD 的证据形式指引）。
