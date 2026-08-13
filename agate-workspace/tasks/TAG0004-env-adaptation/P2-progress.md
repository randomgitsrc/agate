# P2 progress — TAG0004 方案设计

## 2026-08-13 输入读取
- 已读：dispatch-context（P2，强制指令）、architect.md 角色定义、P0-brief.md（env_constraints + known_risks 9 条）
- 已读：P1-requirements.md（37 BDD 基线、P1 SUGGEST 已采纳项、§6 审计范围 46 处）、HANDOFF-TAG0004.md（双工作区纪律）

## 代码阅读
- 已读 pre-commit-gate.sh（S1: L50/57/339/343/350 空格拼接；M9: L102/133/228 grep -E 拼路径）、check-gate.sh（M4: L356/357 [:：]；RM-AG0001: L69/71/89/109/121/125/129 行首正则）、check-p6-evidence.sh（S2: L37）、check-p6-format.sh（M5: L69 4 处 sed bracket、L84 已修 alternation）、check-tdd-red.sh（RM-AG0002: L43/L128-131；TPV0090-M4: L70/L104-107）、agate-next-card.sh（Q1: L56）、agate-workspace-resolve.sh（L33）、install-hook.sh（L31）、agate-render-dispatch-prompt.sh（L112-126）、gate-result.sh（L64-101）、agate-md-field-get.py（L112/L116-126）、agate-frontmatter-check.py（L122-129 _extract_frontmatter_block）
- 测试盘点：check-p6-format.bats 已有 F13（LC_ALL=POSIX 全角冒号总结行）；check-tdd-red-formatter.bats 12 个 formatter 用例；integration/pre-commit-hook.bats 42 用例；agate-next-card.bats 20 用例
- 基线：count-tests 670（unit+regression+integration）+ sanity 6 = 676 ✓

## 最小验证（LC_ALL=C / 真实命令实测）
- M4 CONFIRMED：grep -E '\[BLOCKER\][:：]?...' 在 LC_ALL=C 下不匹配全角冒号（NOMATCH1），(:|：)? alternation 匹配（MATCH2）。check-gate.sh:356/357 排除正则失效 → 总结行 [BLOCKER]：3 条 被误计为真实 BLOCKER
- M5 部分确认：GNU sed 的 [\:：] bracket 在 LC_ALL=C 下只匹配全角冒号首字节（EF），靠 \3 回写"碰巧"输出正确；BSD/busybox sed 行为不可移植 → 需与 L84 同款 alternation 修法统一
- S2 CONFIRMED：现 ASCII 正则不匹配中文文件名；候选 C \(\([^()]*[^()[:space:]]\.[a-zA-Z0-9]+[^()]*\)\) 匹配中文+保留尾缀、拒绝 (见截图) 无扩展名
- Q1 CONFIRMED：${CARD_FILE#$AGATE_ROOT/} 在盘符大小写不一致（C3）/混合斜杠（C2/C5）下前缀剥离失效 → 需归一化后剥离，Linux 字节输出不变（C4）
- RM-AG0001 CONFIRMED：反引号包裹的 [SUGGEST: 计数 1→应为 2、[NEED_CONFIRM] 计数 0→应为 1
- M9 CONFIRMED：目录名含 [ ] 时 grep -E 前缀匹配失效（grep -F + 正则过滤 / re_escape 均可修）
- M6 CONFIRMED：CRLF 下 sed -n '/^---$/...' 提取 frontmatter 空输出；tr -d '\r' / sed 's/\r$//' 修复

## 产出
- 已写 P2-design.md：frontmatter 四字段齐全（candidate_count: 28 与正文 28 个候选一致）、37 BDD 全覆盖映射、gate_commands（P3/P5，bats 无 formatter → exit-code-only 降级说明）、files_to_read（23 项）、env_constraints、minimal_validation（6 项实测：M4/M5、S2、Q1、RM-AG0001、M9、M6 全部 confirmed）
- 自检：YAML frontmatter 解析通过；gate 字段计数 =4；权衡/选择理由关键词存在
- 选择核心：S1 数组化、S3 grep 断言审计、S2 负类加宽、M4/M5 alternation、M6 frontmatter 容错、M9 grep -F 前缀、Q1 归一化剥离、Q2 P5 参照补注、Q5 SETUP 章节、RM-AG0001 正则加反引号、RM-AG0002+TPV0090 一次设计 A/B 判定

## 2026-08-13 评审（review）输入读取
- 已读：P2-dispatch-context-review.md（强制指令）、review.md 角色定义、P2-design.md（评审对象）、P1-requirements.md（37 BDD 基线）、P0-brief.md、HANDOFF-TAG0004.md、P2-progress.md、P2-dispatch-context-architect.md
- 代码核验：check-gate.sh（P2 gate: candidate_count 字段读取 L141、P2-review status/agent 校验 L156-172、四字段 L174-182；M4: L356/357 [:：] bracket；RM-AG0001: L69/71/89/109/121/125/129 行首正则）、pre-commit-gate.sh（S1: L45/50/57/337/339/343/350；M9: L100/102/104/132/133/228/290 grep -E 拼 TASK_REL；2p hash 校验 L202-220）、check-p6-evidence.sh（S2: L37 ASCII 正则）、check-p6-format.sh（M5: L69 4 处 sed bracket，L84 已 alternation）、check-tdd-red.sh（judge_result L59-129、TEST_RUNNER mock L128-131、exit-code-only L93-94 gate-result.sh）、agate-next-card.sh（Q1: L56 REL_CARD 前缀剥离、CARD_FILE 由 AGATE_ROOT 拼）、gate-result.sh（run_test_with_formatter 无 formatter 分支 L93-94）、pytest.sh formatter（无 name_errors 字段）、install-hook.sh（复制模式 L31-40）、agate-workspace-resolve.sh（L33 grep 取 AGATE_WORKSPACE）、agate-render-dispatch-prompt.sh（L112-126 sed 未转义）、P5-verification.md（已对齐规则 2 语义 L14-19）、P1/P2 卡（仍 mode B L17/L13）、git-integration.md（规则 2 L27-35）
- 实测：S2 候选 3A 正则 LC_ALL=C 下匹配中文/拒绝 (见截图) ✓；13 py open() 缺 encoding（agate-md-field-get.py 等 grep 核验）✓；candidate_count=28 与正文候选块一致 ✓；BDD 37/37 全覆盖 ✓

## 2026-08-13 评审产出
- 已写 P2-review.md：status: approved（agent: review），结论引用候选 1A-16A 锚点 + 各权衡评估
- 覆盖：候选方案充分性（candidate_count=28 属实、M6/S1/Q1 ≥2 候选、稻草人检测通过）/ BDD 映射 37/37 / 方案风险（S1 场景清单、S2 负类、TPV0090 NameError 三道闸、RM-AG0002 关键词）/ gate_commands 可执行 + TEST_RUNNER mock 可行 / minimal_validation 6 项 confirmed / Q2 纯文档无 gate 逻辑改动 / 协议语义未破坏
- 非阻塞观察 4 项（§3 补中间 commit 场景、11A 关键词清单去 error:、7A \L 跨平台、pytest.sh 加 name_errors 的 P3 测试）
