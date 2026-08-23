# P2-progress — TAG0023 architect

## 输入文件读取
- [x] P2-dispatch-context-architect.md — 已读全文，明确目标/约束/dispatch_plan建议/gate_commands固化值
- [x] architect.md 角色定义 — 已读，明确frontmatter字段规格、UI设计节（本任务ui_affected:false不适用）、批次设计节
- [x] P1-requirements.md — 已读，13条BDD + §4三组扫描结论 + §5范围/D1-D5决策 + §7 SUGGEST清单
- [x] P1-review.md — 已读，第2轮approved，3个修补点均已解决
- [x] P0-brief.md — 已读，env_constraints/verification_env已确认
- [x] retrospective-tag0019-21.md（dsh-workspace正确路径）— 已读，问题10（retries）+ RM-AG0032记录缺口 + test_bdd_14 flaky 均为一手证据来源
- [x] HANDOFF-TAG0023.md — 已读，双工作区纪律/验证命令/风险止损表

## 必读实现现状文件 — RM-AG0042
- [x] check-state-transition.py 全文 — 检查1(回退跳变>=2)/检查2(重试超限 retries_over→PAUSED)/检查4(self-authored产出残留)；无"门槛失败事件↔retries对应性"检查；只在 .state.yaml 有暂存变更时跑（pre-commit hook 触发，git diff --cached 判定）
- [x] agate-state-get.py — retries_over 实现：dict{phase: attempts_list}，len(attempts)>=phase_max 触发；无对"事件是否发生"的判定，纯计数

## 关键发现（RM-AG0042 事件源，超出dispatch-context预期，需在设计中显式点出）
- agate-retreat-state.py 的 write_retreat 操作**已经会**在回退时追加 retries[NEW_PHASE] 条目（attempts.append {attempt, reason}），且 agate-retreat-to.py 调用它——说明"通过标准工具回退"这条路径本身就会写 retries。
- 复盘中"四任务 retries 全为 {}"意味着实际执行时**未走 agate-retreat-to.py 标准路径**，而是绕过它直接手改 .state.yaml 的 phase 字段（工具存在但未被强制使用/未被检测是否被绕过）。
- check-state-transition.py 现有检查1（回退跳变判定）只在 diff(old_num-new_num) >= 2 时触发（拦截跳级回退强制PAUSED），diff==1（如 P5→P4 单步回退，复盘实证场景）完全不被现有任何检查覆盖——这是 BDD-2 的真正落点：新增校验——old_num>new_num（含diff==1）时，必须能在 retries[new_phase] 找到"看起来像这次回退"的新条目，否则拦截/WARNING。
- 校验点具体机制候选：比较 HEAD 版本 retries[new_phase] 长度 vs 新版本 retries[new_phase] 长度，新版本必须 > HEAD版本（新增了条目）——复用 get_old_phase 已有的 git show HEAD 取旧版本 .state.yaml 内容的模式，新增 get_old_retries_count()/get_new_retries_count() 对称实现即可，改动量小、复用度高。

- [x] state-transitions.md L56-107 — 回退规则表（单步回退✅允许+retry+1；跨阶段回退强制PAUSED）；回退落地后必须建DEBT条目（source:retreat），check-debt.py --retreat-coverage 只读WARNING（不阻断）——这是RM-AG0044改动对象的协议依据
- [x] state-machine.md L420/454-495（.state.yaml retries结构定义+字段说明）/L587-624（"重试记录也要落盘"prose级规程，主Agent每次门槛失败追加retries，但无机械强制）/L668-714（⑩L1阶段内再评审循环prose："评审rejected → retries[Pn].append(...)"是文档规程，未见任何脚本强制校验此步骤是否真的发生——这正是BDD-1的机制缺口本体）

## RM-AG0043 现状确认
- [x] check-gate.py gate_p8()（L1181-1257）全文读——确认全函数内无任何 roadmap.md 读取/grep，纯 P8-release.md 字段检查（bump_type/debt_check）+ version/CHANGELOG/tag 变更检查（暂存区+HEAD~N 回看），全部现有校验与 roadmap done 无关，需求确认为"新增分支"而非"改造现有分支"
- [x] roadmap.md 表结构核实：列 id|标题|状态|来源|关联任务|创建|更新；task_id 落在"关联任务"列，纯文本值（如 TAG0023）；RM-AG0042/43/44/45 四行"关联任务"均=TAG0023（一个task关联多条RM的直接实例，D2场景已现地取证）；RM-AG0032 两行：L30 backlog/关联任务=—（无task）、L31 scheduled/关联任务=TAG0020（非TAG0023！历史task）——匹配规则须支持"关联任务"值为历史task_id（非当前task）的情况

## RM-AG0044 最小验证（P2 强制要求，已实跑，非猜测）
1. 本地 git 2.43.0：全量仓库(1250 commits)/浅克隆(depth 1)/全新init仓库(1 commit) 三种场景下 `git rev-parse --short HEAD` 均返回固定 7 位（floor=7），与 check-debt.py `full[:7]` 恒等，本地**无法复现** mismatch——与 P1 §4.3 预判一致。
2. 用 gh api 拉取 PR #188 实际失败 CI job 日志（run 32645685798 attempt 1，job 97209482443，pytest ubuntu-latest）：确认 CI runner git 版本为 **2.55.0**（本地 2.43.0），远高于本地版本。失败断言实证：`GATE DEBT WARNING: retreat 提交 0674061（...）未登记为 source: retreat DEBT 条目` —— 0674061 即 check-debt.py 固定输出的 `full[:7]`（7位）；该值未命中 `covered`（覆盖内容含测试 fixture 用同一 runner git 2.55.0 `git rev-parse --short HEAD` 生成的 short hash，长度未必为 7）。
3. 结论（已确认，非候选）：**根因确认为 git 版本差异导致的 auto-abbrev 长度计算不一致**——check-debt.py `_retreat_coverage()` L75 `short = full[:7]` 硬编码固定 7 位前缀，而测试 fixture 与实际"是否已登记"的比对逻辑理论上应使用与运行环境一致的 short 长度（`git rev-parse --short HEAD`的实际动态长度），二者在 git ≥ 某新版本（CI 用 2.55.0）时可能不一致，在旧版本（本地 2.43.0）时因 floor=7 而恰好一致，故本地必然无法复现，只能在新版 git 环境复现。
4. 进一步复现尝试（docker 拉取更高版本 git 镜像验证 git 2.55 下 --short 实际长度，任务后台执行中，若成功会补充精确数值；即使不成功，上述 CI 实证日志已构成充分证据链，不依赖此步骤定案）。

## RM-AG0044 补充：CI workflow 关键细节
- [x] .github/workflows/protocol-tests.yml — pytest job 用 `actions/checkout@v4` with `fetch-depth: 0, fetch-tags: true`（**全量克隆，非浅克隆**）——排除"CI 用浅克隆导致 short 变短"这一假设；结合已确认的 CI 实际 git 版本 2.55.0 vs 本地 2.43.0，锁定根因维度为"git 版本演进导致 auto-abbrev 算法/floor 变化"而非克隆深度
- 环境敏感测试集中清单设计方向确认：可挂靠 test 文件的 pytest marker（如 `@pytest.mark.env_sensitive` 或复用现有 `windows_smoke` marker 模式）+ 独立清单 md 文件登记 根因分类字段，风格参照 LIMITATIONS.md 已有 known-failures.md 登记格式（但登记维度不同，见 P1 §4.3 判定）
- CI flaky 自动重跑机制候选：pytest-rerunfailures 插件（`--reruns N --reruns-delay`）或 workflow 级 retry action（`nick-invision/retry`），二选一，落 P2 候选方案设计

## RM-AG0045 现状确认（关键设计约束发现）
- [x] agate-frontmatter-check.py 全文 —— 错误输出格式：`{basename}:{field}: {原因}`（无绝对行号，但有字段名定位，满足BDD-12"行号或字段名"二选一锚点）；yaml.YAMLError 场景（真正语法错误如全角冒号导致解析失败）PyYAML 原生异常消息**已含 line/column 信息**；现状**完全缺"修复建议"文本**——这是唯一真正的 gap，增强量很小（每条 errors.append 追加一句修复提示）
- [x] check-frontmatter.py —— pre-commit 调用入口，FILE 参数化，把 agate-frontmatter-check.py 的 stdout 逐行转 stderr 输出并 exit 1；写时校验若复用同一校验器，输出格式可保持一致
- **关键约束发现**：TAG0019 三类历史错误中，"coupling_checklist流式声明"+"半角冒号"两类由 agate-frontmatter-check.py 覆盖（可在 Write 后立即校验，不依赖 git 状态）；但"源码数 6>5"由 check-routing.py 的 `_staged_source_count()` 计算，**该函数读取 `git diff --cached --name-only`（已暂存区），本质是 commit-time 计算，不是纯文件内容校验**——纯"写文件"时刻（未 git add）无法得到真实源码数。设计需要在 D5 明确处理：写时自检需扩展为"subagent 返回前 git add 本阶段产出 + 跑 check-routing.py"（在 subagent 自己的回合内完成，早于主 Agent 决定是否要求重写，等价消灭"commit 折返"，但技术上仍依赖已暂存），而非真正独立于 git 状态之外的纯写时校验——此结论须在 P2-design.md 明确写清，不能含糊带过

## 设计决策已定案（写入P2-design.md前的内部结论）
- RM-AG0042 落点：check-state-transition.py 新增函数（不新建脚本），复用 get_old_phase 模式；D1结论：分层强度（BDD-1/2 用阻断exit1，BDD-3因信号来源是文本关键词扫描置信度低改用高优WARNING，理由需写清）
- RM-AG0043 落点：check-gate.py gate_p8() 新增分支（不新建脚本），与0042所在文件完全不重叠——H3预判的"同触碰check-gate.py"风险在本设计下不成立（0042实际落点是check-state-transition.py），两批次生产代码文件零重叠，可并行执行
- RM-AG0044 根因：已通过 gh api 拉取 PR#188 真实失败 CI 日志确认（非候选，已confirmed）——CI runner git 2.55.0 vs 本地 2.43.0，workflow用fetch-depth:0排除浅克隆假设；修复方案：full[:7]固定切片改为动态 `git rev-parse --short {full}` 调用
- RM-AG0045 落点：dispatch-prompt.md「返回前自检」标准节新增子项（不新建formatter脚本）+ agate-frontmatter-check.py 各 errors.append 增加修复提示文本；已确认check-routing.py的_staged_source_count()依赖git staged diff，"源码数"类检查无法脱离git add语义，设计中需明确"写时自检"对此类检查等价于"subagent返回前自行git add后跑检查"，非绝对独立于git状态

## 下一步
- 撰写 P2-design.md（8候选方案：4子项×2）+ 影响面梳理 + 完成标准 + dispatch_plan（5批，parallel_limit=5）

## 完成
- [x] P2-design.md 已写出并自检：candidate_count=8 与正文8个"候选A/候选B"标题精确匹配；frontmatter四字段齐全（packages/domains/ui_affected/dispatch_plan）；dispatch_plan 5批 ≤ parallel_limit=5；gate_commands 各key独立无&&拼接（已核实）；影响面梳理三部分（改/不改/风险）齐全且写在候选方案之前（§1在§2前）
- 状态标记：[PROD_NOT_TOUCHED]（本阶段所有写操作均落在 worktree 内 task 目录，读操作含 gh api 只读拉取公开CI日志与本地临时git实验目录，未触碰生产环境/主checkout/~/.agate）

---

# P2-progress — plan-eng-review（独立评审）

## 输入文件读取
- [x] P2-dispatch-context-plan-eng-review.md — 已读全文，9 条硬约束 + 按需核实清单
- [x] plan-eng-review.md 角色定义 — 已读，评审重点/输出结构
- [x] P2-design.md — 已读全文（8候选方案/4子项影响面/完成标准/files_to_read/minimal_validation）
- [x] P1-requirements.md — 已读全文（13条BDD + D1-D5 + 三组同类扫描）
- [x] P2-dispatch-context-architect.md — 已读全文（硬约束对照）
- [x] phase-cards/P2-design.md — 已随 dispatch-context 附带内容读过

## 按需核实（源码/git 实测，非只信文字描述）
- [x] check-state-transition.py L137-143：确认现有"检查1"用 `diff = old_num - new_num; if diff >= 2` —— 与设计 §2.1 描述精确一致
- [x] check-gate.py L1181 `def gate_p8(task_dir):` —— 行号精确匹配；全函数体(1181-1257)内 grep 确认无任何 roadmap 相关代码；全文件 grep "roadmap" 仅 L871 一处（P4 门禁注释，与 P8 无关）—— 与设计 §2.2「现状确认」精确一致
- [x] gate_p8() 实际 return 路径：只有 `return 1`（两处）与末尾 `return 2`，**从无 `return 0`**——main() 用 `sys.exit(func(task_dir))` 直接透传；pre-commit-gate.py L541 确认 exit=2 语义为"需主Agent手动判断"且不阻断 commit。设计 BDD-6 完成判据写"最终 return 2"是准确的（比 P1 BDD-6 原文"Then exit 0"更贴近真实代码行为），非阻塞问题，但建议 P3 测试断言用"非1"而非字面"等于0"
- [x] agate-retreat-state.py L47 `attempts.append({"attempt": len(attempts) + 1, "reason": ...})` —— 精确匹配；agate-retreat-to.py L155 确认调用 write_retreat —— 设计 §2.1「关键发现」属实，非猜测
- [x] check-pruning.py L84-108 `_staged_source_count()`（check-routing.py 只是 alias 引用）：确认用 `git diff --cached --name-only`（L98），commit-time 依赖属实 —— 设计 D5 的"仍依赖 git add"诚实标注成立
- [x] dispatch-prompt.md L92「返回前自检」/ L288「返回前自检（强制）」—— 行号精确匹配
- [x] check-debt.py L48 `_retreat_coverage` / L75 `short = full[:7]` —— 精确匹配
- [x] 本地实测 `git --version` = 2.43.0，`git rev-parse --short HEAD` = 7 位（含换行 8 字节）—— 与设计 minimal_validation 本地实测结论一致
- [x] `gh api repos/randomgitsrc/agate/actions/runs/32645685798/attempts/1/jobs` 实拉取：确认 job id 97209482443 = "pytest (ubuntu-latest)"，conclusion=failure —— 与设计引用精确一致
- [x] `gh api .../jobs/97209482443/logs` 实拉取完整日志：确认 `git version 2.55.0`（L55/L455）、`actions/checkout@v4` 用 `fetch-depth: 0` + `fetch-tags: true`（L36-37）、真实断言失败 `AssertionError: assert 'GATE DEBT WARNING' not in ...` 含 `0674061` 短哈希（L436-448）—— 设计 minimal_validation 的 RM-AG0044 证据链**逐字核实为真实存在**，非自我宣称
- [x] roadmap.md 逐行核实：RM-AG0032 两行（L30 backlog 关联=—；L31 scheduled 关联=TAG0020）；RM-AG0042/43/44/45 四行关联任务均=TAG0023 —— 与设计 §2.2 现地取证精确一致

## 关键发现（核实中新发现，超出 dispatch-context 核实清单范围，构成阻塞级问题）
- RM-AG0042 BDD-1 的事件源判定机制（§2.1：扫描 `*-review.md` Header `status: rejected`）在当前 agate review 协议下**结构性不可能被触发**：
  - review 驳回→修订→通过的迭代循环，根据 phase-cards/P2-design.md 步骤 3→5→6（先 approved 才 git add + commit），全部发生在**单次 commit 之前**，被驳回的中间版本从未单独提交
  - 实测 3 个真实案例，`git log --oneline -- <path>/P{n}-review.md` 均只有 **1 次 commit**，文件当前内容均为 `status: approved`：
    ① 本任务自己的 `P1-review.md`（commit 5ba0a75，尽管 `.state.yaml` 的 `retries.P1` 确实记录了一次真实驳回）
    ② RM-AG0042 的原始动机案例 TAG0019 `P1-review.md`（commit 0398e5f，commit message 明确"3轮迭代 approved"）
    ③ TAG0016 `P4-review.md`（commit 880269d，文件正文甚至写"见本文件历史版本，status: rejected"，但 git log 证明该"历史版本"从未真正提交，只是会话内草稿被覆盖）
  - 结论：check-state-transition.py 作为 pre-commit hook，其检查范围内的 review.md 文件必然已经是"approved 之后才发生的那次 commit"版本——BDD-1 设计的信号源永远读不到 `status: rejected`，该检查会永远静默通过，无法捕获它本应捕获的场景，等价于复现了 RM-AG0042 本身要修复的"静默绕过"问题（只是绕过原因从"手改 phase"变成"检查从不会真正触发"）
  - 对比：BDD-2（HEAD vs 暂存版本的 retries 长度比较）与 BDD-3（扫描按轮次持久化、不被覆盖的 dispatch-context 文件如 `*-retry1.md`）之所以技术可行，正是因为二者选择的信号源具备跨-commit持久性；BDD-1 唯独选错了信号源（选中的是"必然被覆盖成 approved"的文件本身）

## 结论
status: rejected（阻塞级问题：RM-AG0042 BDD-1 事件源机制不可行，需 architect 重新设计后再评审）

## P2 重试 #1（architect，BDD-1 事件源重新设计）

- 读 dispatch-context-retry1（本次强制指令）+ P2-review.md 全文：确认唯一阻塞问题——BDD-1 判定
  规则（扫描已提交 review.md 的 status:rejected 字段）在"驳回→修订→再评审→approved 全部发生在
  同一次 commit 之前"的协议下结构性永不触发，review 已用 3 个真实 git log 案例证实。
- 读任务目录实际文件列表：确认存在 `P1-dispatch-context-analyst-retry1.md` /
  `P1-dispatch-context-requirements-review-retry1.md` / `P2-dispatch-context-architect-retry1.md`
  （本文件即是）——candidate 1（dispatch-context 重试文件命名）现状真实存在，非猜测。
- 读 gate-events.jsonl（本任务实况：仅 2 类事件 gate_run/state_transition，均由
  pre-commit-gate.py 在 **commit 时**才 append_event——与 review.md 同样的"仅 commit 时可观测"
  局限，若要用于 BDD-1 必须新增一个"非 commit 触发"的写入点，等同发明新写入义务）。
- 读 check-events.py：确认未知 event 类型不拦截（向后兼容），账本哈希链+ts单调审计不针对
  特定字段，扩展新 event 类型技术上安全，但"谁在什么时机 append"仍是空白，candidate 2
  需要新协议写入义务，成本高于 candidate 1。
- 读 check-judge-verdict.py 佐证：judge_verdict 事件是本仓库唯一"非 commit 触发、由校验脚本
  主动 append_event"的先例（P6.5 阶段专属机制），说明"扩展账本"技术可行但从未有通用先例覆盖
  "评审阶段（P1/P2/...）通用的 rejected 事件"，candidate 2 若选中需要新建一整套写入协议，
  风险与 dispatch-context「不发明新写入拦截机制」教训冲突。
- 全仓 `find` 扫描 `agate-workspace/tasks/*/*-dispatch-context-*.md`，实测 7 个历史任务
  （TAG0008/16/17/19/20/23）共 36 个 retryN/revN 文件；用正则
  `^P(\d+)-dispatch-context-.*review.*-(retry|rev)\d+\.md$` 跑实测脚本：13 个评审角色重试文件
  全部命中，17 个非评审角色重试文件（analyst/architect/test-designer/implementer/fix1-hook）
  全部正确排除，0 假阳性 0 假阴性——candidate 1 的判定规则在真实历史数据上验证通过。
- 结论：选 candidate 1（dispatch-context 评审角色重试文件命名存在性），理由：①零新增写入
  义务（复用主 Agent 已有派发行为，非发明新协议动作）②正则已用真实历史文件验证 100% 准确
  ③持久性来源于"从不覆盖旧文件"这一现有惯例，天然不会被后续 approved 状态覆盖——直接对应
  review 指出的缺陷根因。唯一风险：该命名惯例目前只是历史实践，非协议明文，故同步在
  dispatch-protocol.md「评审打回后的意见回流」节新增强制措辞，把惯例固化为规则。
- 已用 Edit 原地修改 P2-design.md：§2.1 BDD-1 判定规则 + 新增「BDD-1 事件源重新设计」说明块
  + D6 决策标签 + 校验强度段落措辞同步 + §1.1 改动表第 4 行 + §4 完成标准表 BDD-1 行
  + files_to_read 新增 dispatch-protocol.md 条目。未改动 BDD-2/3/4、D2-D5、§2.2/2.3/2.4、
  candidate_count（仍 8，D6 是既有 RM-AG0042 候选 A 内部子决策，不新增顶层候选对）。
- 自检通过：新方案（评审角色 retryN/revN dispatch-context 文件存在性）具备跨-commit 持久
  可观测性（早于 commit 落盘、写入后从不被覆盖），选择理由基于本仓库 36 个真实历史文件的
  正则实测结果，非猜测。§4 完成标准表 BDD-1 行已同步新判据。files_to_read 已追加
  dispatch-protocol.md:1139-1156 一条（未删除任何已有条目）。BDD-2/3/4、D2-D5、
  §2.2/2.3/2.4、candidate_count（8）、gate_commands 均未改动。[PROD_NOT_TOUCHED]

---

# P2-progress — plan-eng-review 复评（第 2 轮，retry1）

## 步骤 1-3：读 dispatch-context / P2-design.md / P2-review.md（第1轮）
- [x] 已读 P2-dispatch-context-plan-eng-review-retry1.md 全文，明确本轮聚焦 BDD-1 新方案（D6）+ 候选2未选理由 + 协议固化措辞边界，其余项不重新评审
- [x] 已读 P2-design.md 全文（367行），重点 §2.1 D6 专节（L96-121）+ §4 BDD-1 行（L219）
- [x] 已读 P2-review.md 第1轮全文（rejected），确认第1轮阻塞理由：review.md status:rejected 在现行协议下永远不会先于 approved 版本被 commit 捕获

## 步骤 4：独立验证 13/17 分类声称
- [x] 用 `find . -iname "*dispatch-context*.md" | grep -E '\-(retry|rev)[0-9]+\.md$'` 在 worktree 全仓跑出 34 个唯一文件（不是 architect 声称的 36，也不是 dispatch-context 里"主 Agent 独立复核"声称的 30）
- [x] 用 architect 给出的正则 `^P(\d+)-dispatch-context-.*review.*-(retry|rev)\d+\.md$` 逐一匹配 34 个文件：**15 个匹配 / 19 个不匹配**（不是双方声称的 13/17）
- [x] 逐一读匹配到的 15 个文件的 frontmatter `role:` 字段核实真实角色，发现 **2 个确认的假阳性**：
  - `agate-workspace/archived/tasks/T001-v2.0-structured/P4-dispatch-context-implementer-review-fix-retry1.md` — frontmatter `role: implementer`（非评审角色），正文写明该次重试原因是"主 Agent 账号触发月度 API 花费上限"（平台配额中断），与"评审 rejected"毫无关系
  - `agate-workspace/tasks/TAG0016-protocol-hygiene/P7-dispatch-context-consistency-reviewer-retry1.md` — frontmatter `role: architect`（非评审角色），正文同样写明是配额中断后的干净重启
- [x] 用 `grep role:` 扫描全部含"review"子串的 dispatch-context 文件，确认 `implementer-review-fix` 是**跨 5 个历史任务（T001/TAG0002/TAG0003/TAG0016/TAG0017）反复出现的命名惯例**，不是孤例——假阳性有结构性复发风险，不是一次性巧合
- 结论：architect 声称的"零假阳性/假阴性"**不成立**，且双方自报的统计数字（36/30 vs 13/17）本身互相之间、与我方实测（34/15/19）均对不上——这本身就是"未认真独立核实、只是数字凑巧一致就采信"的证据

## 步骤 4b：验证"先于 commit 独立存在于工作目录"这一核心前提
- [x] 用 `git log --oneline`（不用 --follow，避免重命名探测误导）核实 TAG0016 的 `P2-dispatch-context-plan-eng-review-retry1.md` 首次且唯一出现在 commit `cfdf3cb`，与该轮最终 `P2-review.md`（approved）、`P2-design.md`（最终版）同一次 commit 一起入库
- [x] 核实 phase-cards P2 卡片步骤 5 "`git add {AGATE_WORKSPACE}/tasks/{Txxx}/`"（整目录添加）——retry 文件与最终 approved 产出确实会被同一次 `git add` 扫入同一个 commit
- 结论：与原方案的关键区别成立——retry 文件是**从不被覆盖的独立物理文件**，即使和 approved 版本同落一个 commit，pre-commit hook 仍能在该 commit 的暂存快照里同时看到"retry 文件存在"与"retries[] 字段值"两个独立信号；原方案的 `status: rejected` 内容在被 commit 捕获前就已被覆盖为 approved，二者不是同一类问题。这部分设计改进**方向正确**，问题出在具体正则实现上（见上）

## 步骤：候选2（gate-events.jsonl）未选理由核查
- [x] 读 `pre-commit-gate.py` L356-380 确认 `gate_run`/`state_transition` 事件确实只在该 hook `main()` 内 append
- [x] 读 `check-judge-verdict.py` 确认 `judge_verdict` 事件在其 `main()` 步骤 9 append；结合 `phase-cards/P6-acceptance.md`/`dispatch-protocol.md` 确认该脚本是**主 Agent 在 commit 前手动跑 `check-gate.py P6.5`** 触发，非 git hook 触发——architect "唯一非 commit 触发先例" 的表述准确，未发现矛盾
- 结论：候选2 未选理由基本站得住（候选1 零新增手动步骤 vs 候选2 需要评审角色新增一个易被遗忘的手动 append_event 步骤，恰是 RM-AG0042 本身要修复的失败模式）

## 步骤：协议固化措辞边界核查
- [x] `git status --short` + `git diff HEAD --stat` 确认 `agate/dispatch-protocol.md` 当前无任何改动（干净）
- [x] 读 `dispatch-protocol.md:1139-1156`「评审打回后的意见回流」节现状，确认确实**尚未**包含 retryN/revN 命名强制措辞
- 结论：P2 阶段未提前动协议文档本体，符合"P2 只设计不实现"的边界；但 D6 候选1"缓解"段落与 §1.1 改动表用词（"本设计同步把...固化进"）时态较含糊，容易让人误读成"已经改完"，建议 architect 后续措辞更明确标注"P4 交付物"，非阻塞

## 结论
- status: rejected（阻塞理由：BDD-1 新正则规则在真实历史数据上有 2 个确认假阳性，且双方自报的验证数字本身经不起复核，与"零假阳性/假阴性"的核心论证矛盾，该论证正是 D1 把 BDD-1 定为"阻断级"而非 WARNING 的依据）
- 已写产出 P2-review.md（trace_id: TAG0023-P2-review-20260824-r2）
- [PROD_NOT_TOUCHED]

## P2 重试 #2（architect，聚焦 BDD-1/D6 修正）

- 读 architect.md 角色文件 + dispatch-context-architect-retry2.md + P2-review.md（第2轮复评，rejected）+ P2-design.md（上一轮产出）
- 读 C8 映射表 `agate/rules/review-mapping.md`：评审角色为 requirements-review(P1)/plan-eng-review(P2,backend)/plan-design-review(P2,frontend)/plan-ceo-review(P1后/P2,NEED_CONFIRM)/review(P4后,backend/mcp)/design-review(P4后,frontend)/cso(P4后,security)
- 读 `agate/assets/review-roles/*.md` 全部 11 个文件 frontmatter，确认 role_id 清单：cso/design-review/investigate/judge/plan-ceo-review/plan-design-review/plan-eng-review/protocol-alignment-review/qa/review/requirements-review。**关键发现**：`consistency-reviewer` 不在此清单中——它不是注册角色，只是 P7 阶段"architect 兼任一致性检查"的历史文件命名别名（phase-cards P7 模板固定写"P7-dispatch-context-consistency-reviewer.md"，但派发的真实角色是 architect，非评审委员会角色）
- 逐文件核实两个假阳性样本原文：
  1. `.../T001-v2.0-structured/P4-dispatch-context-implementer-review-fix-retry1.md` frontmatter `role: implementer`，正文确认是月度配额中断后干净重启，与评审驳回无关
  2. `.../TAG0016-protocol-hygiene/P7-dispatch-context-consistency-reviewer-retry1.md` frontmatter `role: architect`，正文同样是配额中断重启；且该文件名是 P7 阶段**协议规定的标准文件名**（非偶然），意味着每个任务的 P7 重试都会产生这个 token，是结构性命中源，不是孤例
- 独立重新全仓核验（不采信任何一方历史自述数字）：
  - `find . -iname "*dispatch-context*.md"` → 440 个文件，过滤 `-(retry|rev)\d+\.md$` 后缀 → **35 个**（含本任务本轮新增的 P2-dispatch-context-architect-retry2.md 本身），排除后 **34 个**历史文件（与 review 复评数字一致）
  - 用原宽松正则 `^P(\d+)-dispatch-context-.*review.*-(retry|rev)\d+\.md$` 逐一匹配 34 个文件 → **15 匹配 / 19 不匹配**（与 review 复评数字完全一致）
  - 用新收紧枚举正则（见下）逐一匹配同 34 个文件 → **13 匹配 / 21 不匹配**，两个假阳性样本均被排除，13 个匹配全部逐一核实 role/内容为真实评审委员会重试（含 TAG0023 自身 2 个无 frontmatter 的新格式文件，逐条读正文确认角色属实）
- 最终枚举正则：`^P(\d+)-dispatch-context-(requirements-review|plan-eng-review|plan-design-review|plan-ceo-review|cso|review|design-review|review-eng|review-cso)-(retry|rev)\d+\.md$`——排除 `consistency-reviewer`（非 C8/registry 角色）、`protocol-alignment-review`/`qa`/`judge`/`investigate`（未在 34 个真实文件中观测到，且非 P1-P4 评审委员会 rejected→retry 语义范畴，judge 另有 judge_verdict 事件机制覆盖）
- D1 校验强度改判：鉴于枚举法仍存在"未来命名漂移导致新 token 碰撞"的结构性残余风险（非本次 2 个已知假阳性可穷尽），且 frontmatter role 字段不总是存在无法做兜底交叉校验，BDD-1 由"阻断"降级为与 BDD-3 同级"高优 WARNING"
- 已用 Edit 原地修改 P2-design.md 的 D6/D1/§4 BDD-1 行/§0 结论速览/files_to_read 相关表述，未触碰 D2-D5/BDD-2-4/其余候选方案
## P2 重试 #2 完成（architect）
自检通过：正则=C8角色token精确枚举（基于review-roles/*.md role_id + 34个真实文件核实）；残余边界已承认（未来命名碰撞风险，consistency-reviewer已证实一例）；D1结论=BDD-1由阻断降为高优WARNING（BDD-2仍阻断）；未依赖frontmatter兜底（已证实2个本任务自身文件无frontmatter）；§4已补T001+TAG0016两个真实假阳性负样本锚点；D6缓解措辞已改为P4交付物式表述。

---

# P2-progress — plan-eng-review 复评（第 3 轮，retry2，MAX=3 最后一轮）

## 步骤 1-5：读 dispatch-context-retry2 / plan-eng-review.md / P2-design.md / P2-review.md(r2) / P1-requirements.md / review-mapping.md
- [x] 全部读毕，明确本轮聚焦 4 点：①新正则假阳性/假阴性 ②枚举完整性 vs review-mapping.md ③WARNING 降级是否符合 P1 BDD-1 双路径 ④残余边界诚实度

## 步骤 6：独立复现新正则统计（不采信 architect 自述数字）
- `find . -iname "*dispatch-context*.md" | grep -E '\-(retry|rev)[0-9]+\.md$'` → 36 个文件；排除本轮自身新产生的 2 个（P2-dispatch-context-architect-retry2.md + P2-dispatch-context-plan-eng-review-retry2.md）→ **34 个历史文件**，与 architect/r2 一致
- 用原宽松正则 → **15 匹配/19 不匹配**；用新枚举正则 → **13 匹配/21 不匹配**，与 architect 声称完全一致（可复现）
- 逐一核实 13 个匹配文件的 frontmatter `role:` 字段（11 个有 frontmatter 的全部核实为 requirements-review/plan-eng-review/review/cso 真实评审角色；TAG0023 自身 2 个无 frontmatter 文件为本任务真实历史评审轮次，非编造）→ **无新假阳性**
- 检查 21 个不匹配文件中含"review"子串者，只有 2 个（T001 implementer-review-fix / TAG0016 consistency-reviewer），恰好是已知的 2 个假阳性，其余 19 个不匹配文件角色名（analyst/architect/test-designer/implementer/verifier/fix1-hook）均非评审角色 → 未发现"review"子串类的漏判

## 步骤 7：枚举完整性核对 review-mapping.md + assets/review-roles/*.md（发现新问题）
- C8 表角色：plan-eng-review/review/plan-design-review/design-review/cso/plan-ceo-review，均在枚举内
- **发现1（非阻塞但需记录）**：`agate/assets/review-roles/qa.md`（role_id: qa, type: review, phases: [P5]）与 `investigate.md`（role_id: investigate, type: review, phases: [any]）均在正文明确声明"本角色的'打回/HOLD/转向/有CRITICAL或BLOCKER' → `status: rejected`"——与 BDD-1 判定的语义（评审 rejected）完全吻合，但均未被收入枚举。design 对二者的排除理由（"非本 BDD 覆盖范围"）与角色文件原文矛盾，不像 judge 那样有可验证的替代机制说明
- **发现2（design 自身推理错误，已用正则实测证伪）**：design 声称 `protocol-alignment-review` 若真实出现"会被 review token 命中"——用 Python 实测新枚举正则对字符串 `P4-dispatch-context-protocol-alignment-review-retry1.md` 匹配结果为 **False**（因枚举要求角色段整体精确等于某个 token，不做子串包含判断）。design 这条排除理由技术上不成立，尽管实际排除该角色本身影响有限（34 个真实文件中从未以此 token 出现）

## 步骤 8：P1 BDD-1 原文核对 WARNING 路径合法性
- P1-requirements.md L161："Then 校验以非 0 退出码（阻断）或高优先级 WARNING 输出提示...（两种拦截强度实现路径均满足本条锚点，具体强度由 P2 定案，见 §5 D1）"——WARNING 明确是 P1 本就允许的选项，非本轮临时松绑

## 结论
- status: approved
- 阻塞问题：0（round 2 的核心问题——正则假阳性——已修正且独立验证无新假阳性/无新遗漏；WARNING 降级有 P1 原文依据）
- 非阻塞发现：①qa/investigate 两个 type:review 角色的 status:rejected 语义与枚举脱节（应准确归类为"YAGNI 未观测到"而非"非本 BDD 覆盖范围"）②protocol-alignment-review 的排除理由（"会被 review 命中"）经正则实测证伪，应改为准确表述（"34 个真实文件从未见此 token，YAGNI"）——均属 WARNING 级机制的覆盖面精度问题，不影响本轮已修正的核心缺陷（真实历史数据假阳性），不构成阻塞
- 已写产出 P2-review.md（trace_id: TAG0023-P2-review-20260824-r3）
- [PROD_NOT_TOUCHED]
