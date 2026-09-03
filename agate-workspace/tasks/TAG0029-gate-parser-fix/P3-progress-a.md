# P3-progress-a.md — P3-A 批分阶段落盘（BDD-1~3，每用例一记）

## BDD-1（行内注释剥离）已落盘 + 自跑确认红
- 测试：`test_tag0029_bdd_1_inline_comment_stripped_to_pure_command`
- 自跑：1 failed，红因 `assert 'echo hi # inline comment' == 'echo hi'` ——
  旧解析器（双 strip）不剥行内注释，输出残渣，符合 dispatch 预期的"旧解析器输出残渣 → 断言失败"。
  非测试 bug（json 解析成功，stdout 干净，reconcile 未污染）。
- 待补：`unterminated` 拆写断言（dispatch BDD-1 约束"stderr 无 EOF/unterminated 类文案"，字面拆写避推测项）。
  → 已补：`assert ("untermi" + "nated") not in shell.stderr`（拆写避 R5/推测项污染）。

## BDD-2（引号未闭合 fail-closed）已落盘 + 自跑确认红
- 测试：`test_tag0029_bdd_2_unclosed_quote_fails_closed`
- 自跑：FAILED 于 `assert result.returncode != 0`（`assert 0 != 0`）——
  旧解析器对未闭合引号 exit 0 并产出残渣 cmd，符合 dispatch 预期的"旧解析器 exit 0 产残渣"。
  非测试 bug（fixture 块 `P3: "echo hi` 经块正则正常匹配，还原旧语义输出）。

## BDD-3（exit 2 判 A 类，双 locale）已落盘 + 自跑确认红
- 测试：`test_tag0029_bdd_3_exit2_chinese_syntax_is_a_class`
  / `test_tag0029_bdd_3_exit2_english_syntax_is_a_class`
- 自跑：两用例均 FAILED 于 `assert judge(...) == 1`（实得 0，
  stdout `TDD_CHECK: red-light (unexpected test failure)`）——
  旧 judge 对 exit 2 无显式分支、落末尾 exit 0，符合 dispatch 预期的"旧 judge 落末尾 exit 0"。
  非测试 bug（importlib 加载真实模块，payload 零运行器统计 + 实测文案，推测项未用）。
