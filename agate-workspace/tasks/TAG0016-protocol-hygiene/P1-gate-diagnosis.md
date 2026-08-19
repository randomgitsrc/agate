---
phase: P1
date: 2026-08-19
trigger: gate_fail
---
# P1 Gate 诊断

- gate 结果：`python3 agate/scripts/check-gate.py P1 agate-workspace/tasks/TAG0016-protocol-hygiene` exit 1
- gate 输出：`GATE P1: 不合规的 NEED_CONFIRM 标记格式（须用行首 [NEED_CONFIRM]、[SUGGEST: ...] 或 [NO_NEED_CONFIRM] 声明）`
- 诊断：P1-requirements.md 第 282 行「5. 待确认清单」说明段落里出现了字面文本 `` `[NEED_CONFIRM]` ``
  （"...故不标 `[NEED_CONFIRM]`"）。这是在正文里引用标记文本做否定描述，命中
  dispatch-protocol.md 明文禁止的反模式（禁止在产出文件中引用标记文本做否定描述，例如写"无
  {生产环境接触标记}"或"所有需确认项已解决"这类句式；要表达"未触发"应写负向格式声明本身，
  而不是在句子里提一遍原标记）。check-gate.py 第 491 行的检测逻辑是字面子串匹配
  `"[NEED_CONFIRM]" in p1_text and nc_blocking == 0`——只要正文任何位置出现这个字面串（哪怕是在
  反引号里、哪怕是否定语气），且没有合规的行首阻塞声明，就判定"不合规的 NEED_CONFIRM 标记格式"。
  文件第 280 行已正确声明 `[NO_NEED_CONFIRM]`（行首、无反引号包裹），这条声明本身合规；问题仅在
  第 282 行说明文字里又提了一遍 `[NEED_CONFIRM]` 字面串。
- 影响范围：只影响 P1-requirements.md 第 282 行这一处文本，不影响其余 18+1 条 BDD、不影响
  frontmatter、不影响已 approved 的 P1-review.md 结论（review 内容未引用这个禁用格式，review 本身
  不受影响）。
- 路由：回派 analyst 做定点文本修复（不重新走 requirements-review，因为这不是内容/判定问题，是
  纯格式违规，且改动范围是一句解释性文字，不影响任何 BDD 判定内容）——按 dispatch-protocol.md
  「gate 无法执行时的处理路径」外的常规 diff=0 同阶段修复处理：主 Agent 修正后重新预跑
  check-gate.py 确认 exit 2，不需要走完整 review 迭代循环（review 循环针对的是 BDD/需求内容质量，
  不是这种字面格式违规）。
- 修复方向：把第 282 行"故不标 `[NEED_CONFIRM]`"改写为不包含字面 `[NEED_CONFIRM]` 子串的表述，
  如"故不使用该阻塞标记"或"不判定为需人工确认的阻塞项"，保留原意（说明为何这条不构成
  NEED_CONFIRM）但不重复引用禁用的标记字面文本。
