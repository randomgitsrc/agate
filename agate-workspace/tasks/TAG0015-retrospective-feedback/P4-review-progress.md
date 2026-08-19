- 约束1a：agate-feedback.py `_anonymize` 已核实为 B1 轻量正则脱敏（先绝对路径截断/`<PATH>` 替换，后项目名 `<PROJECT>` 替换），非简化版。
- 约束5：`grep -n "subprocess\|gh \|git push" agate/scripts/agate-feedback.py` 独立复核为零命中（exit 1），实现自报属实。
- 约束1b：check-retrospective.py `_scan_debt_roadmap_signal` 分支已核实，main() 末尾仍为无条件 `sys.exit(0)`，exit code 契约未破坏。
- 约束1c：state-machine.md 新增「L2 会话 checkpoint（两件套）」小节，同时含 `P{n}-checkpoint.md` 与 `task-session-summary.md` 字面字符串，正文①②③④四段完整回答四问；第 481 行三项既有排除原样保留，仅追加"和触发决策的简要依据"分句。
- 约束2：`git diff -- agate-workspace/roadmap/roadmap.md` 核查：仅第一处（原 313 行附近）出现连续字符串 `docs/reviews/postmortem-template.md`（被拆为"`docs/reviews/` 下的 `postmortem-template.md`"两段），另两处（316/322 对应内容）原文本身是倒序表述（"postmortem-template.md 在/保留在 docs/reviews/"），非连续字符串，故只追加脚注未拆分，语义均未删减，只追加行内脚注。读 check-protocol-consistency.py 源码确认 `NARRATIVE_DIRS = ("docs/plans/", "docs/reviews/", "docs/design-notes/", "docs/tasks/", "archived/", "agate-workspace/tasks/", "CHANGELOG.md")`——`agate-workspace/roadmap/` 与 `agate/assets/` 确实均不在名单内，CHECK 2 的 REF_RE 会匹配连续路径字符串为 ERROR 候选，DESIGN_GAP declaration 属实非借口。独立重跑 `check-protocol-consistency.py --strict` → 0 ERROR（299 WARNING）。
- 约束3：`git show fbd9c31 -- agate/tests/unit/test_check_retrospective.py` 确认该文件已在 P3 commit 纯新增 3 个函数（+83/-0），P4 暂存区对三份测试文件（含 test_check_retrospective.py）无任何改动（`git diff --cached` 空），既有 12 用例完整保留（现共 15 个 test_ 函数）。独立重跑三测试文件 → 35 passed。
- 约束4：`git status --porcelain`/`git diff --cached --stat` 核对改动文件清单，恰好落在 P2-design.md §1.1 七类改动范围 + 正常工作区产出文件（P4-implementation.md/P4-progress.md/orchestrator-log.md/dispatch-context），未触碰 docs/hardening-roadmap.md / agate-workspace/archived/ / dispatch-protocol.md / agate/WORKFLOW.md / state-machine.md:361（gate 失败追加 orchestrator-log 用法示例行原样未动，已读 355-365 行确认）。
- 约束6：`git diff --cached` 核对 5 份 docs/reviews/ 存量文件首行标注，逐字完全一致："> 历史复盘（迁移前旧布局），新复盘请见 \`tasks/{Txxx}/retrospective.md\`（模板：\`agate/assets/templates/retrospective-template.md\`）"，与 P2-design.md §1.1 类 4.6 给出的文案逐字相符。
- 约束7：产出判定 approved，理由见 P4-review.md 正文。

## 重试 #1 复核（对照 dispatch-context「重试 #1」节 4 点清单）

- 复核点1：`agate-md-field-get.py:74-76`（`NO_FALLBACK_BOOL_FIELDS` 新增 `feedback_ready`）、
  `:110-115`（`NO_FALLBACK_LIST_FIELDS` 新增 `mechanism_issues`/`execution_issues`）语义与
  `regression_pass`/`need_confirm_resolved` 等既有同类字段一致（frontmatter-only 无正文回退，
  bool 归一化小写字符串，list 换行连接）；`_format_value`/`_get` 分发逻辑未改动，只是新增
  frozenset 成员，未触碰既有字段行为。独立重跑 `pytest agate/tests/unit/test_agate_md_field_get.py -q`
  → 16 passed，工具自身测试全绿，无回归。
- 复核点2：`agate-feedback.py:33-49` `_md_field_get()` 调用 `agate-md-field-get.py`（子进程，
  `env["FILE"]=file_path`），`main()` 内 `mechanism_issues_raw.split("\n") if ... else []`、
  `execution_issues_raw.split("\n") if ... else []` 正确还原列表（空字符串走 else 分支得空列表，
  非 `"".split("\n")` 产生的 `[""]`）；`feedback_ready = _md_field_get(...) == "true"` 正确还原
  布尔。独立重跑 `pytest agate/tests/unit/test_agate_feedback.py -q` → 7 passed（含
  BDD-17/18 解析与脱敏用例），行为与订正前等价。
- 复核点3：静态验证订正后的正则 `subprocess\.\w+\(\s*\[[^\]]*\b(git|gh)\b`——用沙盒脚本验证：
  对合法调用 `subprocess.run([sys.executable, MD_FIELD_GET, op], ...)` 不匹配（不误伤）；对
  恶意/误改 `subprocess.run(["git", "push", ...])` 与 `subprocess.call(["gh", "pr", "create"])`
  均正确匹配报红。存在理论规避向量（变量间接赋值、字符串拼接）但这是静态正则断言的固有局限，
  与仓库同类"关键词锚点断言"风格一致（A4 审查已定性 test_retrospective_protocol_docs.py 为
  同一风格），非本次订正引入的新弱点，且比订正前的 `"subprocess" not in source`（会误伤任何
  合法 subprocess 用法）更贴合 BDD-20 真实验收意图，不是形同虚设的宽松断言。
- 复核点4：`grep -c "^def test" agate/tests/unit/test_check_retrospective.py
  agate/tests/unit/test_agate_feedback.py agate/tests/unit/test_retrospective_protocol_docs.py`
  → 15 / 7 / 13，与 `agate/tests/README.md` 新版三行数字（15/7/13）精确一致，非照抄审查报告
  旧数字（审查报告 A3b 建议行曾写"8"，implementer 实测订正为 7，与本次独立复核一致）。
- 独立重跑全量：`pytest agate/tests/ -q --tb=no` → 929 passed, 3 failed（`test_check_pruning.py`
  三个用例，与本次 diff 涉及文件无关，alignment-review 已做 A/B stash 核实为预置失败）, 2 skipped，
  与 P4-implementation.md 自报一致。`check-protocol-consistency.py --strict` → 0 ERROR
  （305 WARNING），与自报一致。
- 4 点复核结论：均已妥善解决，判定 approved（见 P4-review.md 更新版正文）。
