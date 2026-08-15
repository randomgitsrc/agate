# 增量审查留痕 02 — check-p6-format.sh frontmatter 修复（commit afe758a）

读 protocol-alignment-review.md：角色定义，A1-A7 清单 + 输出格式 + 闭环规则确认。
读 P4-dispatch-context-protocol-alignment-review-p6formatfix.md：确认审查范围仅 git diff f476834..afe758a -- check-p6-format.sh check-p6-format.bats，count-tests.sh 新基线 597。
读 P6-gate-diagnosis.md：bug 是 --fix 整文件 sed 未排除 frontmatter，误伤 pass:/fail: 字段；建议修复方向=参照 agate-frontmatter-check.py::_extract_frontmatter_block 切分 frontmatter/正文，只对正文跑 5 条归一化 sed。
跑 git diff f476834..afe758a -- 两文件：确认改动仅限 check-p6-format.sh 的 --fix 分支（新增 FM_PART/BODY_PART 切分 + 拼回逻辑）+ bats 新增 3 条 F_P6FMFIX.1/.2/.3。--check 分支、参数解析、文件筛选逻辑零改动。
读 agate-frontmatter-check.py:120-127 _extract_frontmatter_block：text.startswith('---\n') + text.find('\n---',4)。
对照 check-p6-format.sh:57-64：FIRST_LINE=="---" (head -n1) + awk index($0,"---")==1 找闭合行。语义对齐：都要求首行恰好是 --- 独立行，闭合边界都是'以---为前缀的行'而非'整行恰好---'。
手动构造 fixture（frontmatter pass:28/fail:0 + 正文小写 - pass BDD-2）跑新版 --fix：frontmatter 原样保留（pass: 28 / fail: 0 未被改写），yaml.safe_load 成功解析出 {phase, task_id, pass:28, fail:0, ui_affected:False}；正文 - pass BDD-2 被正确归一化为 - PASS BDD-2。复现与 P6-gate-diagnosis.md 独立复现步骤完全对应，确认修复解决了原始 bug。
对比新旧版本对无 frontmatter 文件的处理（拉 f476834 版本另存 old-check-p6-format.sh 跑同一 fixture）：新旧版本输出逐字节相同，确认无 frontmatter 场景（旧格式 BDD-9 兼容）行为未被这次修复改变。
跑 bats agate/tests/unit/check-p6-format.bats：13/13 全绿，含新增 F_P6FMFIX.1/.2/.3。
跑 bats 全量套件（unit+regression+integration+sanity）：ok=603 not ok=0，独立复现派发指引声明的 603/603。
跑 count-tests.sh：总计 597，与派发指引点 3 的新基线（594+3）一致，非漂移。
跑 check-protocol-consistency.py：全部 CHECK 通过，含 CHECK 9，0 ERROR。
跑 shellcheck -S warning check-p6-format.sh：无输出，exit 0。
grep check-p6-format.sh 全项目引用：phase-cards/P6-acceptance.md、dispatch-protocol.md、verifier.md、pre-commit-gate.sh、check-protocol-consistency.py 锚点条目——全部仍引用同一 CLI 签名（--fix/--check + 位置参数文件路径），本次修复未改动参数解析逻辑（diff 中 arg-parse 段落零改动），调用方接口未受影响。
核对 check-protocol-consistency.py:592-597 check-p6-format.sh 锚点条目：keywords=[--fix,--check] 在改动后代码中依然存在（未被移除或改名），callers 列表三处仍准确。CHECK 9 独立重跑 PASS，无需新增/修改锚点条目，符合派发指引点 2 第三条预判。
A3 反向传播核对：本次改动不引入新协议规则/新字段语义（只是让既有 BDD-16 承诺的 frontmatter pass/fail 字段在 --fix 后依然合法，属于修 bug 而非改契约），phase-cards/P6-acceptance.md、dispatch-protocol.md、verifier.md 对 check-p6-format.sh --fix 的既有描述（'归一化 PASS/FAIL 大小写和行首空白'）本就未对 frontmatter 处理做任何承诺或反向承诺，故无需同步改动，非遗漏。
A7：修复不涉及新架构决策，遵循 P4-implementation.md:645-648 声明的'未重新发明逻辑，对齐既有 Python 判定语义'，与 ADR-002（可判定性）方向一致，无新增 ADR 需要。
全部检查完成，开始写成果文件追加内容。
成果文件已追加写入 docs/reviews/agate-alignment-review-2026-08-10.md 末尾。七项结论：A1-A7 全 ALIGNED，无 MISALIGNED/NEEDS_HUMAN_REVIEW。
