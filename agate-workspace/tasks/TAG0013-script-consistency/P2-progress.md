# P2 进度 — TAG0013-script-consistency

> architect subagent 分阶段落盘。时间：2026-08-16。

## 已读
- [x] P2-dispatch-context-architect.md（派发指引）
- [x] architect.md（角色定义）
- [x] P0-brief.md（env_constraints / known_risks）
- [x] P1-requirements.md（11 BDD + 影响面表 378/595 + 豁免清单 5 类）
- [x] P1-review.md（approved；§4 非阻塞观察注 1/2 待 P2 处理）

## 后续
- [ ] 三个被测脚本
- [ ] 三个测试文件 + conftest.py
- [x] check-protocol-consistency.py（L52-65 PROTOCOL_FILES/PROTOCOL_DIRS、L74 NARRATIVE_DIRS、L238 REF_RE、L766-782 CHECKS）
  - 发现：CHECKS 是 (name, fn) 元组列表，main 输出循环用 title.split()[1] 取 CHECK 编号；CHECK 10 若加进 CHECKS 输出自动覆盖。
  - 发现：check_internal_refs 遍历 iter_md_files(root)——含全仓 md（含 docs/、agate-workspace/），narrative 降级机制在函数内。
  - 发现：CHECK 2/3 作用于全仓 iter_md_files，但 check_line_refs 内 is_protocol_file 才严格。phase-cards/rules 入 PROTOCOL_DIRS 后 CHECK 2/3 会严格检查它们。
  - 发现：NARRATIVE_DIRS 不含 docs/superpowers、docs/guides、docs/agents、docs/notes、docs/hardening-roadmap.md——这些在 is_narrative_file 返回 False，但 CHECK 2 会按协议文件 ERROR 级处理？需查证：它们是否在 PROTOCOL_FILES？不在。是_protocol_file False → 非 narrative 非 protocol → CHECK2 的 else 分支 error。这些 docs 文件若有死链会 ERROR。但那是 CHECK 2 现状，与 CHECK 10 无关。
- [x] commit-msg-self-gate.py（L38-40 _SELF_GATE_RE；L53 run_git diff --cached；L57 match）
  - 发现：正则 `^(...)$` 锚定整行 = 根级精确名天然可行；加 `README\.md|AGENTS\.md` 分支即覆盖，CHANGELOG 天然豁免。
  - 发现：stderr 提示文案 L77 硬编码触发面描述（agate/scripts/*.sh 等）——扩展正则后该文案也应同步更新（否则提示与实际触发面不符，属 [SCOPE+] 级小问题，但只在触发时显示）。
- [x] check-retrospective.py（main() L63-95；warnings 收集；L89-93 输出块；L95 exit 0）
  - 发现：提醒行要含 DEBT + roadmap 两词，且只能在 if warnings: 块内加（L89），避免违反 RT.1 空输出。
- [x] test_commit_msg_self_gate.py（4 用例 test_cmsg_1..4；用 git_repo fixture 造暂存区场景 + _run_csg helper）
  - 发现：新用例可复用同模式（写文件→stage→run sh→断言 output）。
- [x] test_check_retrospective.py（RT.1..RT.7 + retro_* 等；RT.1 空输出断言 result.output == ""）
  - 发现：新增提醒行测试需在异常场景（rt_2/rt_4 等）断言 DEBT+roadmap 字样；RT.1 空输出不回归由既有用例锁定。
- [x] test_check_protocol_consistency.py（_load_cpc importlib 加载模块测锚点）
- [x] conftest.py（git_repo / task_dir / run_cli / bash / python_exe fixture）
- [x] 最小验证（模拟 CHECK 10）：
  - 协议文档面（含 phase-cards/rules/assets）用 P1 §4.4 count 正则提取：**非 CHANGELOG 漂移 = 0**
  - CHANGELOG 155 处历史 .sh 名漂移（叙事降级 WARNING 或聚合）
  - phase-cards/rules 无 .md L 引用（0）、scripts/ 前缀引用 3 处均存在 → PROTOCOL_DIRS 扩展安全
  - CI 一致性跑无 --strict（protocol-tests.yml L122），--strict 仅本地（已有 277 WARNING 基线）
- [x] _SELF_GATE_RE 候选验证：精确名锚定 A 仅命中 README/AGENTS；宽松 glob B 会误命中 NOTICES.md
- [x] 全部输入读完，最小验证完成
- 关键结论：
  1. CHECK 10 扫描面（PROTOCOL_FILES+EXTRA+PROTOCOL_DIRS 扩展）用 P1 §4.4 whitelist 正则 → 非 CHANGELOG 漂移 = 0（增量性成立）
  2. CHANGELOG 155 处历史 .sh 名 → 叙事降级（聚合 WARNING，避免 155 条噪音）
  3. PROTOCOL_DIRS 扩展 phase-cards/rules：无 .md L 引用（0）+ scripts/ 前缀 3 处均存在 → CHECK 2/3 无新 ERROR
  4. _SELF_GATE_RE：精确名锚定 A 仅命中 README/AGENTS；宽松 glob B 会误命中 NOTICES.md → 选 A
  5. CI 一致性非 --strict（protocol-tests.yml L122）；当前 --strict exit 2（277 WARNING 基线）
  6. count-tests.sh 实测 751（P1 基线 749）

## plan-eng-review 追加（2026-08-16）
- [x] 读 P2-dispatch-context-plan-eng-review.md
- [x] 读 plan-eng-review.md（角色定义）
- [x] 读 P0-brief.md / AGENTS.md
- [x] 读 P2-design.md（6 候选方案，四字段齐全）
- [x] 读 P1-requirements.md（11 BDD + 影响面）
- [x] 读 P1-review.md（approved，§4 注 1/2/3）
- [x] 读三个被测脚本
- [x] 读三个测试文件 + conftest.py
- [x] 客观验证：
  - SCRIPT_REF_RE 模拟扫描：协议文档面 token=595（含 CHANGELOG 217），非 CHANGELOG 漂移=0 → BDD-1 增量性成立
  - formatters 目录无 my-runner.sh 实体（仅 README L108 示例名）；count-tests.sh 在 tests/scripts/ 存在
  - consistency 现跑 0 ERROR / 277 WARNING；count-tests.sh=751（目标≥749）；CI 非 --strict
  - phase-cards/rules：.md L 引用 0 处，scripts/ 前缀 3 处均存在 → PROTOCOL_DIRS 扩展安全
  - self-gate 候选 A 零误报（NOTICES/README.zh-CN/CLAUDE/HANDOFF/docs/agate-workspace 全 False）；候选 B 误命中 NOTICES.md+CLAUDE.md+HANDOFF-TAG0013.md
  - CHANGELOG .sh 计数：178 总 - 23 现行 hook = 155（设计口径闭合）
  - 【BLOCKER】main() CHECK 状态循环 `startswith(key)`：'CHECK10-scriptref'.startswith('CHECK1')=True → CHECK 10 报错/警时 CHECK 1 状态行被污染（设计「无需改 main()」不成立）
  - agate_common.py（下划线名）不在白名单形状内，但 ≥10 个扫描面文件引用它 → 漏检盲区（非阻塞）
  - 豁免②（formatters/my-runner.sh）是死代码：正则白名单从不匹配 formatter 名 → 不会误报（非阻塞）

## [2026-08-16 修复轮] architect revise round start
- 读取 dispatch-context（P2-dispatch-context-architect-revise.md）
- 读取 P2-review.md（rejected，BLOCKER-1 + 非阻塞 1-5 + 测试缺口 7/8）
- 实测量证：main() L810-816 startswith(key) 前缀碰撞成立；agate_common.py 10 文件引用；formatters 名不匹配白名单；count-tests=751；docstring 缺 CHECK 10
## [2026-08-16 修复轮] revisions applied
- BLOCKER-1: §2 step 4 改「无需改 main()」为「main() 状态匹配修正（split('-')[0] == key 或 startswith(key + '-'))」
- 非阻塞1: SCRIPT_REF_RE 增 agate_[a-z0-9-]+\.(?:py|sh) 覆盖 agate_common.py + 声明库文件在检测范围
- 非阻塞2: §2 step 3.d + §10 注1 标 forward-defense（当前不可达），my-runner.sh 天然豁免不显式加入
- 非阻塞3: §1 风险2 + BDD-4 改「CHECK 2 本就严格；激活的是 CHECK 3 + CHECK 10」
- 非阻塞4: §5 基线统一 751（以 count-tests.sh 输出为准）
- 非阻塞5: §11 完成标志 + §6 files_to_read 补 docstring CHECK 10 行
- 缺口7: 新增 §2 测试策略节，推荐 (a) 最小假协议树
- 缺口8: BLOCKER-1 回归断言（场景 A/B + 旧逻辑锁定）
- §9 决策记录 6 增补 main() 修正

## [2026-08-16 复审轮] plan-eng-review revise round
- 读 P2-dispatch-context-plan-eng-review-revise.md / plan-eng-review.md / P0-brief.md / AGENTS.md
- 读修订后 P2-design.md / 上轮 P2-review.md / P1-requirements.md
- 读三个被测脚本（check-protocol-consistency.py L810-816 / L769、commit-msg-self-gate.py L38-40/L76-77、check-retrospective.py L89-93）+ 两个测试文件
- 实测：
  - main() L811 key="CHECK"+title.split()[1]；report ids 形如 CHECK1-yaml/CHECK9-align；'CHECK10-scriptref'.startswith('CHECK1')=True 碰撞成立；split('-')[0] 方案对 CHECK1/9/10 均正确
  - 修订正则（含下划线形状）模拟：非 CHANGELOG 漂移=0 保持；agate_common.py 16 处 token 均合法（文件存在）
  - count-tests.sh=751；phase-cards/rules .md L 引用 0 处 + scripts/ 前缀 3 处均存在；CHECK 3 用 is_protocol_file（L279）
  - P1 正则复现 595/217；修订正则 616/219（下划线形状 +21）——L70「可复现 378/595」措辞轻微不精确（P1 口径，非遗漏）
- BLOCKER-1 / 非阻塞 1-5 / 缺口 7-8 逐项核验：全部已落实
- 新观察（非阻塞）：缺口 8 回归测试「复刻」状态循环表达式而非驱动 real main()——建议 P3 抽 helper 或跑 main()，否则 main() 若忘改测试也绿
- 终判：approved（无 BLOCKER）
