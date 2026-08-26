# BDD-11 人工复核记录：GitHub 仓库改名执行前用户在场放行确认

> BDD-11 性质：会话时序内的人工确认动作，不是可复跑的文件/系统状态判定（P2-design.md gate_commands
> 说明节已明确"BDD-11 不出现在 gate_commands 表中"）。本条按治理类 BDD 的人工复核记录形式提交证据，
> 本轮（P6 第 2 轮）独立重新核对该记录的内部一致性，不直接复用第 1 轮的判定文本。

## 复核对象

`agate-workspace/tasks/TAG0025-agateon-rename/env-rename-handoff.md` 「六、版本记录」表格，
第二行（2026-08-26，事件列）原始记录：

> P4 改名执行完成（**用户当次会话内明确放行确认后**，主 Agent 亲自执行 `gh api -X PATCH
> repos/randomgitsrc/agate -f name=agateon`，响应 `full_name: randomgitsrc/agateon`）+ §四验收锚
> 4 条实测全部通过：①`curl -sI https://github.com/randomgitsrc/agate` → HTTP/2 301
> ②`git ls-remote https://github.com/randomgitsrc/agateon.git HEAD` → 正常返回 SHA ③全仓残留扫描
> （pytest BDD-10 权威判定）PASSED，0 残留 ④`gh api search/repositories -f q='agateon in:name'`
> 首位命中 `randomgitsrc/agateon`

## 交叉核对

1. **P0-brief.md known_risks**："不可逆外部操作：GitHub 仓库改名一次、对外可见——执行前须确认：
   ① `gh` 具备 repo 管理权限 ② 用户在场确认放行"——与本记录的"用户当次会话内明确放行确认后"表述
   方向一致（确认在执行前）。
2. **P2-design.md 候选方案 B**（已选定）："主 Agent 在会话中向用户发起明确的放行请求……拿到用户
   明确同意后，**由主 Agent 本人**运行 `gh api -X PATCH repos/randomgitsrc/agate -f name=agateon`"
   ——记录里的执行主体（主 Agent 亲自执行）与执行前置（放行确认在前）与该方案完全对应，无偏离。
3. **P1-requirements.md BDD-11 Then 子句**："必须先在当前会话内获得用户明确的在场放行确认……
   权限核实（技术上能不能做）不能替代放行确认（现在要不要做），二者是并列的两个前置条件"——
   记录同时体现了①权限核实（P1-dispatch-context-analyst.md 客观查证信息 A，`gh` admin 权限）与
   ②放行确认（本条记录"用户当次会话内明确放行确认后"）两个独立环节，未见把①当作②的替代表述。
4. **时序表述**：记录用"确认后，主 Agent 亲自执行"的先后语序（confirm → execute），不是
   "执行后补记确认"的事后补票语序，与 BDD-11 要求的"确认发生在本次改名操作执行窗口内"一致。
5. **内部无矛盾**：本条记录与同一交接单「四、P4 改名执行窗口」节的操作说明、以及
   P4-implementation.md:97-98（"GitHub 仓库改名……已由主 Agent 在获得用户放行确认后亲自执行完成"）
   互相印证，未发现表述矛盾。

## 复核结论

- **复核人**：verifier subagent（P6 第 2 轮）
- **复核时间**：2026-08-26（本轮验收执行时点）
- **复核结论**：PASS——记录内部一致、时序正确（确认先于执行）、执行主体与 P2 选定方案一致，
  与 P0/P1 对"权限核实"和"放行确认"两个独立前置条件的表述无矛盾。
- **本 judge/verifier 诚实边界声明**：该类治理性 BDD 的证据上限是"会话记录的内部一致性核对"，
  无法对"用户放行确认事件本身是否真实发生于历史会话"做独立可重放的程序化核实——这是此类 BDD
  的固有证据形式，P6.5 第 1 轮 judge 复核已认可这一证据上限（判 PASS，未在第 1 轮被判定为
  needs-revision 项，本轮仅 BDD-10 是 needs-revision 根因）。
