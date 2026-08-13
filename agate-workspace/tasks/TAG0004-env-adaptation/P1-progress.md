# TAG0004 P1 progress

## 已读输入
- dispatch-context (P1-analyst)：目标=产出 P1-requirements.md，缺陷清单 S1/S2/S3/M4/M5/M6/M9+Q1/Q2/Q5+RM-AG0001/0002；约束=Linux 基线 + Windows 增量、不可宣称实测 Windows、Q2 纯文档修复
- analyst.md 角色定义：先质疑再定义、隐含需求、BDD 二值判定、NEED_CONFIRM 分级、capability_requirements 三态
- P0-brief.md：env_constraints / known_risks（46 脚本 25sh+21py）/ executor_env
- HANDOFF-TAG0004.md：双工作区纪律、验证命令、阶段推进纪律
- AGENTS.md：脚本关键约定、测试约定、SELF-GATE 触发清单

## 下一步
- 实际核验目标脚本（按行号）
## 已核验脚本（实际读代码）
- pre-commit-gate.sh：S1 确认（L45-54 STAGED_STATE_FILES 空格拼接、L57 未引号切词、L337-344 PROCESSED_DIRS 拼接、L339/350 case 切词）；M9 确认（L102/L133/L228 TASK_REL 拼进 grep -E）；AGATE_ROOT copy-mode readlink 问题（L26）
- check-gate.sh：M4/M5 确认（L356/357 [BLOCKER\][:：]? 全角冒号 bracket 在 POSIX locale 匹配问题）；RM-AG0001 反引号盲区对应 L69/L71/L89/L109 行首正则 ^\s*-?\s* 前缀，反引号包裹时不匹配
## 已核验（续）
- check-p6-evidence.sh:37 S2 确认：证据引用正则只认 ASCII [a-zA-Z0-9_/. -]*，中文文件名（如 截图.png）不匹配 → PASS 缺引用假失败
- check-p6-format.sh:69 M5 确认：三处 sed 仍用 [[:space:]:：] bracket expression（v0.40.3 只修了 :84 Summary 行）
- check-tdd-red.sh:43 RM-AG0002 确认：无 formatter 退化 exit-code-only 分支存在（TEST_RUNNER 直用 / gate_commands 无 formatter）
- agate-next-card.sh:56 Q1 确认：REL_CARD=${CARD_FILE#$AGATE_ROOT/} 前缀匹配，Windows 盘符/反斜杠下失效
- agate-workspace-resolve.sh:33 确认：.agate.env grep 取 AGATE_WORKSPACE= 未 tr -d '\r'，CRLF 文件会带入 \r
- install-hook.sh:31 + pre-commit-gate.sh:26 确认：复制模式（Windows 无软链权限）下 readlink -f 解析到副本位置而非 AGATE_ROOT
- agate-render-dispatch-prompt.sh:112-126 确认：sed 替换串未转义 & / 分隔符 |，AGATE_ROOT/路径含特殊字符会替换错
- .gitattributes 确认 M6：不含 *.md（注释明确排除），Windows checkout md→CRLF，frontmatter sed 提取失效
- SETUP.md 确认 Q5：无 Windows 章节（PATH/编码/CRLF/PYTHONUTF8），.gitignore 模板无 version.txt/dist 预设
- Q2 确认：P1/P2/P3/P4/P6/P7/P8 七张卡仍有'更新 phase=Pn→Pn+1'模式 B 写法（P1卡:17、P2卡:13、P3卡:13、P4卡:16、P6卡:16、P7卡:14、P8卡:14）；P5卡:14 已同步规则2
- git-integration.md 规则2（:27/:33）：phase=本 commit 提交的产出阶段，不得提前写下一阶段
- WORKFLOW.md 裁剪规则：P1/P2/P4/P5/P6 不可裁，P3 可跳(两种情形)，P7 可选（多文件改动时），P8 涉及发布必做；风险矩阵
## 已核验（S3/M6/CI）
- S3 确认：13 个 py 文本 open() 缺 encoding="utf-8"（agate-card-inject.py:13/15/28、agate-changelog-unreleased.py:8、agate-evidence-consistency.py:21/30、agate-gate-missing-cmds.py:12、agate-gate-p5-count.py:11、agate-md-field-get.py:112、agate-read-gate-commands.py:16、agate-read-p5-commands.py:18、agate-retreat-state.py:28/42/49、agate-state-get.py:25、agate-state-yaml-check.py:21、agate-vision-blocker.py:17、ci-gate-backstop.py:51/118/180）；参照已带 encoding 的 agate-debt-check.py/agate-frontmatter-check.py；agate-image-check.py 的 Image.open 是二进制图片不受影响
- CI：protocol-tests.yml 仅 ubuntu-latest 四 job（bats/shellcheck/consistency/gate-backstop），无 windows matrix —— 需新增
- Q2 卡片文本核实：P1 卡步骤 4 '更新 .state.yaml phase=P1 → P2' 先于步骤 6 commit —— 模式 B 残留确认
- git-integration.md 规则 2（:27/:33）：phase=本 commit 提交的产出阶段，不得提前写下一阶段
## 产出完成
- P1-requirements.md 已写入约定路径（355 行）
- 34 条 BDD（BDD-1..34 连续、二值可判定、按 S1/S3/S2/M4/M5/M6/M9/其他/Q1/Q2/Q5/RM/RM/全局回归分组）
- frontmatter：risk_level=medium / phases=P1-P8 全保留 / packages 7 个 / domains=[backend,security,cli]
- [NO_NEED_CONFIRM]；3 条 [SUGGEST]（M6 修法倾向、S3 断言审计、RM-0002 保守判定）
- capability_requirements 无 GAP（windows-runtime=supplementable，CI 兜底）
- 自检通过：check-frontmatter.sh OK；stable gate 相关正则（line-start NEED_CONFIRM=0 / SUGGEST=3 / NO_NEED_CONFIRM=2 / BDD=34 / prose GAP=0）；已规避 [NEED_CONFIRM] 字面量被 stable gate 误判的坑
- [PROD_NOT_TOUCHED]
## requirements-review 评审中
- 已读角色定义、dispatch-context(requirements-review)、P1-requirements.md(34 BDD)、P0-brief、HANDOFF
- 开始抽查 BDD 涉及的脚本行为（check-gate.sh:69/71/89/109、:356；check-p6-evidence.sh:37；check-tdd-red.sh:43；agate-next-card.sh:56）
## 评审核验结果（requirements-review）
- S1 确认：pre-commit-gate.sh L45-54/57/339/343/350 空格拼接+未引号切词（fail-open）
- S3 确认：13 py 文本 open() 缺 encoding（逐文件核验；agate-frontmatter-check.py:202 是注释误报，其 open()@209 已带 encoding）
- S2 确认：check-p6-evidence.sh:37 ASCII 正则 `\([a-zA-Z0-9_/. -]*...\)` 不匹配中文文件名
- M4 确认：check-gate.sh:355-356 `\[BLOCKER\][:：]?` 在 C locale 下 count=1（不排除总结行→误计为 blocker），C.UTF-8 下 count=0；`(:|：)` 修正后 C locale count=0（修法可行）
- M5 关键发现：BDD-12 的 Given（大写 `- FAIL：3`）走的是已修好的 line 84，当前代码在 C 和 C.UTF-8 下都已经是 `**Summary**: FAIL: 3` → BDD-12 对 line 69 的 M5 残留无区分力；真正走 line 69 的是小写 `- fail：3`
- M4/M5 的 bug 是 locale 依赖的：C.UTF-8（默认）下现代码已通过 BDD-11 → BDD-11/12 需在 Given 加 LC_ALL=C 前置条件才有区分力
- BDD-9 歧义：Given 示例用全角括号 `（截图 验证通过.png）`，但正则/实际 PASS 行用 ASCII 括号 `(...)`；S2 修复范围是字符类非括号宽度
- Q1 确认：agate-next-card.sh:56 `${CARD_FILE#$AGATE_ROOT/}` 前缀匹配
- Q2 确认：7 张卡均残留"更新 phase=Pn→Pn+1"模式 B（P1:17/P2:13/P3:13/P4:16/P6:16/P7:14/P8:14）；git-integration.md 规则2 @27/33 明确 phase=本 commit 产出阶段；:113"先更新再 commit"与规则2一致（同 commit 内顺序），Q2 不应改它
- RM-AG0001 确认：check-gate.sh:69/71 行首 `^\s*-?\s*\[` 正则对反引号包裹不匹配（实测 0 vs 1）
- RM-AG0002 确认：check-tdd-red.sh:43 无 formatter 退化 exit-code-only；gate-result.sh:93-94 无 formatter 时不解析 failed/errors
- capability_requirements：windows-runtime=supplementable（CI matrix）合理；无 GAP
- 结论：needs-revision（BDD-12 区分力缺失 + BDD-11/12 缺 locale 前置 + BDD-9 括号宽度歧义）
## 评审结论（已写入 P1-review.md）
- 判定：needs-revision（3 个实质发现）
- F1 BDD-12 Given 用大写 `- FAIL：3`，走的是已修复的 line 84（实测当前代码 C/C.UTF-8 均正确归一化）→ 对 line 69 残留 M5 bug 无区分力；应改用小写 `- fail：3`
- F2 BDD-11/12/13 缺 POSIX locale 前置：实测 C.UTF-8 下 BDD-11 现代码即通过（count=0），仅 LC_ALL=C 下区分（count=1）→ 回归测试必须强制 LC_ALL=C，BDD 应写明
- F3 BDD-9 Given 用全角括号 `（截图 验证通过.png）`，但 S2 正则用 ASCII 括号 `(...)`；若修复只加宽字符类，全角括号仍不匹配 → 修复范围/BDD 示例需澄清；BDD-10 只测"无括号"不测"括号内无文件名"（过宽风险）
- 其余 BDD-1..34 均可二值判定、跨条一致、裁剪合理、capability 三态正确、P1 纯净性 OK
## 修订轮（analyst，2026-08-13）开始
- 已读 dispatch-context（修订轮）、P1-review.md（F1/F2/F3）、P1-requirements.md（修订对象）、P0-brief（含 TPV0090-M4 known_risk）、analyst.md
- 已核验 check-tdd-red.sh：L70 import_count、L87-102 仅认 import_errors，L104-107 errors>0 一律判 A 类 → NameError 落入 errors 被误判 A 类（TPV0090-M4 确认）
- 已核验 check-p6-format.sh:69（三处 [[:space:]:：] bracket，M5 残留）vs :84（已修 alternation）；check-p6-evidence.sh:37（ASCII 括号）
- 修订方案：F1=BDD-12 Given 改小写 `- fail：3`（走 line 69）；F2=BDD-11/12/13 Given 加 LC_ALL=C 前置；F3=BDD-9 Given 改 ASCII 括号 + BDD-10 补 `(见截图)` 边界；M4=新增 BDD-35/36/37（NameError→B 类、globals().get() 兼容、真实 bug 仍 A 类）
## 修订完成（analyst）
- F1：BDD-12 Given 改小写 `- fail：3`（走 line 69 bracket 路径，区别于已修 line 84 大写路径）
- F2：BDD-11/12/13 Given 显式声明 LC_ALL=C（POSIX locale）执行前置 + 注明回归测试须强制
- F3：BDD-9 Given 改 ASCII 括号 `(截图 验证通过.png)`（字符类加宽、括号宽度不变）；BDD-10 补 `(见截图)` 边界（括号内无文件名仍被拦）
- M4：新增 TPV0090-M4 节 BDD-35（NameError→B 类 exit 0）/BDD-36（globals().get() 兼容）/BDD-37（真实 bug 仍 A 类）
- 同步：§6 审计范围补 TPV0090-M4（check-tdd-red.sh:70/87-102/104-107）；§7 P6 计数 BDD-1..37（≥37）
- 自检：BDD 编号 BDD-1..37 连续无跳号；无 [NEED_CONFIRM]；无 status: GAP（仅"无 status: GAP 项"否定句）；frontmatter 完整；[PROD_NOT_TOUCHED]

## P1 复审（requirements-review 复审轮）
- 已核验 F1/F2/F3 + M4 全部通过：F1=BDD-12 小写覆盖 line 69、F2=BDD-11/12/13 LC_ALL=C、F3=BDD-9 ASCII 括号+字符类加宽声明 + BDD-10 (见截图) 边界、M4=BDD-35/36/37 与 BDD-30/31 边界互斥
- 37 BDD 连续编号，全部可二值判定
- 待写 P1-review.md（覆盖重写）
P1 复审 approved 已落盘，37 BDD 锚点齐备
