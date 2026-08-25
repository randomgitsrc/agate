# P4-progress-review

## batch A / batch B 已读完（详见汇总，问题 1-7）

## batch C（check-debt.py + protocol-tests.yml + ENV-SENSITIVE-TESTS.md）已读完

未发现 CRITICAL 问题。`_short_hash()` 逻辑清晰：git 调用失败/输出为空回退固定 `full[:7]`，不引入新崩溃路径；`full` 来源于 `git log --format=%H%x09%s` 的 `%H`（干净 40 位 hex，无需额外清洗）。保留 `full` 全量兜底比对符合设计。性能：每条 retreat 提交一次 git 子进程调用，retreat 数量通常个位数，非阻塞项（P2-design.md 已预判并接受）。`--reruns 1` 只加在 Linux 全量测试步骤，未影响其他步骤，权衡已在 P2-design.md 记录。ENV-SENSITIVE-TESTS.md 三条目齐全，格式清晰。

## batch D（dispatch-prompt.md + agate-frontmatter-check.py）已读完

未发现 CRITICAL 问题。错误消息增强只是追加后缀文本，已 grep 全仓确认无调用方对旧文案做精确
等值比较（均是 `in` 子串断言或只判 exit code），不会破坏依赖旧文案的调用方。dispatch-prompt.md
新增自检节与 P2-design.md §2.4 D5 结论一致。

## 全部 4 批读完，关键决策核实 4 项已核实，已写产出 P4-review.md（status: rejected）

核心结论：4 条 CRITICAL 集中在 batch A（_scan_bdd1_review_retry_phase 首命中即返回丢失多阶段、
_scan_bdd3_keyword_phases 的 progress.md 精确匹配漏扫描本任务自己的 P4-progress-batchX.md、
BDD-2 的 old_retries_len>0 守卫使其无法拦截"从未写过 retries"的首次违规——即 RM-AG0042 立项
动机本身、_load_current_state_yaml 缺 errors="replace" 导致非法编码可致整个脚本崩溃）；
batch B 有 3 条 INFORMATIONAL（roadmap 表格解析脆弱/路径硬编码/RM-AG0032 新增行与既有 scheduled
行的交互副作用）；batch C/D 干净。均已用真实项目数据验证，非假设场景。
