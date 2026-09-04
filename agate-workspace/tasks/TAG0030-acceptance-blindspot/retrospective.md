---
task_id: TAG0030
mechanism_issues:
  - P1 frontmatter phases 列表与正文裁剪声明一致性无机械校验——phases 漏 P2 靠 requirements-review 打回才暴露（check-frontmatter/check-gate P1 均未拦）
  - judge 信息隔离白名单规则只在 check-judge-verdict.py 源码（BDD-4②），P6.5 派发上下文误列角色文件路径触发 exit 1，卡未显式提醒
  - agate-next P6→P7 A1 裁决把 provenance WARNING（exit 2，根因 P3 缺 agent 字段）误判为"验收异常"假暂停并落盘模板残留
  - 多任务并行共享版本命名空间（CHANGELOG/README/git tag）：merge 引入兄弟 tag 后 git describe 取最近 tag 非最高版本，CHECK 7 CI 失败——tag 须落在含 merge 修复的最终 commit
  - DEBT 关闭 schema 校验器 check-debt 无任何 gate/CI 挂载 + closed 证据判定为 P[56] 子串启发式：P8 纯 status 翻转关闭后 main 上 check-debt exit 1
execution_issues: []
feedback_ready: true
---

# 复盘 — TAG0030 验收盲区机制批（RM-AG0057 四类 + DEBT0024/25/26）

## 一、事实基线

- 任务：TAG0030（RM-AG0057 验收盲区四类 + DEBT0024/25/26 关闭），worktree `.worktrees/agate-TAG0030`，分支 `feat/TAG0030-acceptance-blindspot`，PR #273 普通 merge（f4fca1f → origin/main），tag v0.68.0 最终落在 commit 3aa6de9（含 merge origin/main 冲突全解 + ruff F401 修复的最终 commit，非 pre-merge commit）。
- 执行窗口：2026-09-03 立项 → 2026-09-04 P8/READY。纯协议文档面改造（同文档面 5 处需求合并单 task，避免 5 轮回归）。
- 阶段：P0–P8 + P6.5 全量无裁剪。P1 BDD-1~21 连续 21 条；P2 候选 2 选 A（架构级 candidate_count 下沉 UI 布局层等 pin 定）；P3 21 个断言审计用例（test_tag0030_assertions.py）全红灯（21 failed，全 B 类）；P4 三批并行 implementer 落笔后 21 全绿；P5/P6/P6.5/P7 依次通过。
- 改动面：14 协议文件（P1/P3/P4/P6 卡、plan-design-review.md、dispatch-context.md 模板、analyst/architect/verifier 角色、role-system.md、tests/README.md、AGENTS.md、UPGRADING.md、CHANGELOG.md）+ 1 审计单测（P3 commit 167a044）；SELF-GATE protocol-alignment-review A1-A7 一次 aligned（commit 3c2d647）。
- P5 验证：unit 1312 passed + 1 预存 flaky / regression 28 / integration 92 / consistency 0 ERROR（329 WARNING 历史存量）/ count 1457（1436+21）/ 断言审计 63/63（21+14+28）。
- P6：21/21 PASS，P6-evidence/ 24 文件（21 锚词快照 + assert-full + consistency + count-tests）；P6.5 judge fresh context 21/21 零挑验 passed；P7 BLOCKER=0 / DESIGN_GAP 0 配对 / CODE_MAP_SYNC。
- 打回与一次修复（非重复）：P1 review 1 轮 needs-revision（frontmatter phases 漏 P2 硬阻断）→ fix1 approved；P6.5 首写 dispatch-context 引用 judge.md 触发 check-judge-verdict exit 1 → 一次修复（现文件行 63 已固化提醒）。
- gate 异常留痕：P6 自查预检 `check-p6-provenance.py` exit 2（唯一 WARNING：P3-test-cases.md 缺 agent 字段，系 P3 commit 167a044 既有产出）→ agate-next 误判"验收异常"假暂停并落盘 `P6-exit2-resolution.md`（模板占位符残留，未填写、工作区 untracked 未随任务提交）。
- 并行共享面实证（TAG0029/30/31 三路）：HEAD 链上 TAG0029 发 v0.67.1（bff1767）、TAG0031 发 v0.67.2（a50ee5b）；TAG0030 P8 先本地 bump v0.68.0（aea45c1）并在收尾 commit 52cb420 建 tag，随后 merge origin/main（3aa6de9"共享面冲突全解"）引入兄弟 tag 后 CHECK 7（badge vs tag）CI 失败 → tag 移到最终 merge commit 3aa6de9 后通过（52cb420 的旧 tag 指向被替换）。roadmap.md 同属共享面：main 现残留 RM-AG0057 双行（done + scheduled 各一）。
- DEBT 关闭现状核查：P8 在 aea45c1 将 DEBT0024/25/26 翻为 closed（git show --stat 实证 tech-debt.md 仅 6 行变动 = 纯 status 翻转），协议文件关闭锚词已落笔（tests/README.md:117「真实 gate 语义」/ AGENTS.md:19「新增 CHECK 上线前先全量扫描」/ dispatch-context.md:33「拆小默认指导」）；但 merged 后的 main 状态 `check-debt.py agate-workspace/debt/tech-debt.md` **exit 1**（DEBT0025/26：closed 条目 evidence 须引用 task_id 与 P5/P6 证据；DEBT0026：category `execution` 非法，合法值 technical/management/protocol；DEBT0024 因 note 引文偶然含 "P5 baseline" 绕过同规则）。

## 二、做得好的 + 可复用模式

- **断言审计 TDD 21 锚词全覆盖（TAG0012 模式复用成功）**：P3 用 grep 锚词锁定协议条文 + 断言审计单测 1:1 锁 BDD，删条文即转红；假绿点处理是本模式的关键增量——plan-design-review.md 既有词（布局型/渲染正确性/0-10/status）全部改 AND 语义、兜一个当前 0 命中锚词保整体红；architect.md「对齐」行 111/221 语义不同故弃用该锚词。→ 回馈 agate：test-designer.md 假绿点自检节可补"同行异义词（如既有条文内通用词）须 AND 语义规避，避免误以为已红"一句。
- **批量文档改动 grep 断言审计一次锁定（TAG0027 批量 TDD 策略复用）**：14 文件同批改动只做 1 个 21 用例审计单测 + 双保险（test_review_role_docs 14 + test_protocol_mechanism_anchors 28），避免每处单独 TDD；P4 三批各自自查后终跑 21 passed 全绿。→ 回馈 agate：P0-brief 已把该策略写为默认测试验收；审计单测本体为项目资产（agate/tests/unit/test_tag0030_assertions.py 已入常驻回归面）。
- **三批 implementer 并行 + 共享产出文件章节式合并**：P2 dispatch_plan static-batch 三批（phase-cards / assets-roles / templates-tests-meta），文件域不重叠 → 并行安全；共享产出 P4-implementation.md 章节式追加、三批 frontmatter 合并无覆盖（P4-review 复核通过）。→ 回馈 agate：implementer.md 可收录"并行批共享产出文件的协作约定：文件域不重叠校验 + 章节式追加 + frontmatter 由最后落笔批合并"，作为 P4 并行派发范式。
- **P5 verifier 6 组对照实验判定预存 flaky**：unit 片 1 失败（test_nc_byte_stability...）经单例/文件级/配对/排除新测试/串行全量/全量并行 6 组对照，判定为 TAG0011 遗留并行竞争（inject-card IC_IDEMPOTENT.2 改写真实卡文件与 next-card 双读哈希竞争），串行全量 1313 全绿，无功能性回归；结论写进 known-failures.md 而非当成本任务失败。→ 回馈 agate：verifier.md known-failures 登记节可收录该 6 组对照口径（判定"预存失败"的最小实验集），使预存登记从"口头判断"升级为"实验支撑"。
- 执行纪律保持（无需沉淀）：SELF-GATE protocol-alignment-review 一次通过；P3 假绿核实表 + P4 平台词护栏（叙述段无裸平台词）执行到位；P7 只审不写全程 [PROD_NOT_TOUCHED]。

## 三、发现的问题

- 问题 1：P1 frontmatter `phases` 列表与正文「裁剪说明」一致性无机械校验——首轮 phases 为 [P1,P3..P8]（漏 P2）而 §3 写「P2 不可裁/全覆盖」，check-frontmatter / check-gate P1 均未拦，靠 requirements-review 逐字核对才 needs-revision 打回。
  归因层面: 机制缺口
  说明：check-pruning「P2 不可裁剪」硬闸只在 P2 门触发（届时 exit 1），P1 门没有"phases 集合 vs 正文全覆盖声明 vs 不可裁阶段清单"的交叉校验；字段格式合法不等于字段语义与正文一致，语义一致性目前只靠 review 人工读。
- 问题 2：check-judge-verdict.py 信息隔离白名单（BDD-4②）扫描 dispatch-context 含白名单外 `.md` 路径（角色定义路径也触发）——规则只在脚本源码，P6.5 卡/派发模板未显式提醒「输入清单勿列角色文件路径」，主 Agent 首写 P6.5-dispatch-context 引用 judge.md 触发 exit 1。
  归因层面: 机制缺口
  说明：白名单约束（含"角色定义走派发 prompt 注入、不在输入清单引用其路径"这一条）未在 P6.5 卡或 judge 派发模板成文，执行者只能从脚本报错反推规则；一次拦截修复后未重复（现 dispatch-context 行 63 已补该句，可作模板先例）。
- 问题 3：agate-next P6→P7 A1 裁决要求 check-p6-provenance exit 0——P3-test-cases.md 缺 agent 字段（agent 键被 agate-md-field-set 防伪造拒绝、按惯例手工写，P3 漏写）导致 provenance exit 2（WARNING）→ agate-next 误判「验收异常」假暂停并落盘 P6-exit2-resolution.md 模板残留（实际是 P3 字段问题非 P6 异常，模板文件留空未填、未随任务提交）。
  归因层面: 机制缺口
  说明：两层缺口叠加——① P3 阶段无 gate 校验产出文件 frontmatter agent 字段存在性（手工写惯例可漏，债潜伏到 P6 门前才暴露）；② agate-next 把 provenance exit 2（WARNING 级）与 exit 1（ERROR）同等当"验收异常"处理，未区分"告警提示"与"阻断异常"，且落盘的是未填写的模板占位符文件（污染任务目录）。
- 问题 4：多任务并行共享 CHANGELOG/README/git tag 序列（TAG0029/30/31 三路）——merge origin/main 引入兄弟 tag（v0.67.1/2）后，`git describe --tags` 取"最近 tag"（提交图距离）而非最高版本号，CHECK 7（badge vs tag）CI 失败；本地 P8 tag 打在 pre-merge 收尾 commit（52cb420）上不够，须移到含 merge 修复的最终 commit（3aa6de9）才通过。
  归因层面: 机制缺口
  说明：DEBT0013 已记录 bump→tag 的单任务时序注意，但未覆盖并行发布层：共享版本命名空间下，兄弟任务的 merge 会改变 describe 的解析目标，bump、merge、tag 三步的先后顺序错误即触发 CHECK 7 假失败；roadmap.md 同属共享面，3aa6de9 冲突全解后残留 RM-AG0057 双行（done + scheduled），显示共享表文件的 merge 结果需要事后人工核对行级去重。
- 问题 5：DEBT 条目关闭的 schema 合规零机械复核——P8「DEBT0024/25/26 关闭」只翻转 status: closed（tech-debt.md 仅 6 行变动），未按 tech-debt-template 关闭约定补引用关闭任务 P5/P6 证据的 evidence、未修正 DEBT0026 登记期遗留的非法 category: execution；merged 后的 main 状态 `check-debt.py` exit 1（DEBT0025/26 报错）。
  归因层面: 机制缺口
  说明：check-debt.py 是 DEBT schema 唯一校验器，但**不挂任何 gate/CI**（phase 卡、3 hook、protocol-tests.yml 均无引用；`agate-workspace/debt/` 还被 detect-docs-only 视为 docs-only 走快路径跳过全量校验；consistency CHECK9-align 只静态查脚本存在与关键词，不实跑校验）——关闭动作合规与否全凭执行者自觉先跑校验器；且 agate-debt-check.py 的 closed 证据规则是 `P[56]` 子串启发式（DEBT0024 仅因 note 引文偶然含 "P5 baseline" 绕过同规则），弱于"引用关闭任务 P5/P6 证据文件"的语义本意。同机制也解释了 DEBT0026 登记期非法 category 从未被拦。执行侧动作（只翻 status 未读模板关闭节）是触发点，但让它溜过并留在 main 的是"校验器无触发点"这一机制缺口。

## 四、改进措施

1. 针对问题 1：P1 门加 frontmatter phases ↔ 正文裁剪声明的交叉校验。落点：`agate/scripts/check-frontmatter.py`（或 check-gate.py P1 分支）——当 phases 缺某阶段时，与正文「全覆盖/无裁剪」声明及 check-pruning 不可裁阶段清单比对，不一致报 ERROR；或将 check-pruning 的"声明裁剪即校验 phases 完整性"提前到 P1 门。候选 roadmap RM。
2. 针对问题 2：judge 信息隔离白名单约束显式化。落点：P6.5 卡（P6-acceptance.md 内 P6.5 节）或 judge 派发模板补固定句「输入清单只列白名单内文件；角色定义经派发 prompt 注入，不得在输入清单引用其文件路径」+ `check-judge-verdict.py` 报错文案附规则出处与修复指引（当前只报"含白名单外路径"不说怎么改）。候选 roadmap RM。
3. 针对问题 3：provenance 退出码分级 + P3 字段债前置拦截。落点：`agate/scripts/agate-next-card.py` P6→P7 A1 裁决——exit 2（WARNING）与 exit 1（ERROR）分级，WARNING 提示人工核对、不判「验收异常」暂停、不落盘 exit2-resolution 模板；`check-p6-provenance.py` WARNING 说明标注缺失字段归属阶段（P3 字段债 ≠ P6 异常）；另评估 P3 gate 是否补"产出文件 frontmatter agent 字段存在性"检查（agate-md-field-set 拒写 agent 的防伪设计 + 手工写惯例是漏写温床，见 P4-progress 行 83-85 同一问题在 P4/P7 均被正确处理）。候选 roadmap RM。
4. 针对问题 4：并行发布共享版本命名空间的时序规则 + 共享面 merge 后行级核对。落点：`agate/UPGRADING.md`/AGENTS.md 版本发布清单（DEBT0013 时序注意扩展为"多任务并行时：release 前先 merge origin/main 解共享面冲突，bump + tag 必须落在含全部 merge 修复的最终 commit，push 后以 `git describe --tags` 复核 origin/main"）；CHECK 7 排查手册补"兄弟 tag 并行插入 → describe 取最近 tag 非最高版本"第一排查项；本任务遗留清理：删除 roadmap.md RM-AG0057 残留的 scheduled 行（保留 done 行）。候选 roadmap RM + 直接清理。
5. 针对问题 5：DEBT 关闭机械校验 gate 化 + 证据判定收紧。落点：`agate/phase-cards/P8-release.md` DEBT 关闭节绑定「关闭后必跑 `check-debt.py <tech-debt.md>` 确认 exit 0」；tech-debt.md 头部机器校验注记重申；`agate/scripts/agate-debt-check.py` closed 证据判定由 `P[56]` 子串启发式收紧为"evidence 引用关闭任务 task_id 或其 P5/P6 证据路径"（消除正文引文偶然满足）；本任务遗留修正：DEBT0025/26 补引用 TAG0030 P5/P6 证据 + closed_at、DEBT0026 改合法 category。候选 roadmap RM。
6. 无执行纪律类新增措施（问题 1-5 中执行动作均为触发点而非根因；P1 打回与 P6.5 白名单拦截均一次修复未重复）。

## 技术债登记核对清单

| 机制 | 应该触发？ | 实际触发？ | 未触发后果 | 原因 |
|------|-----------|-----------|-----------|------|
| retry 记录 | 是（P1 review 打回 1 轮 + P6 provenance exit 2 处理） | ✅（P1-fix1 留痕 + P6-exit2-resolution 留痕） | | |
| PAUSED | 否（未超限/未跨阶段回退；agate-next 假暂停系误判非真暂停） | —（误判性落盘 exit2-resolution 模板后人工解除，见问题 3） | 无（误判由主 Agent 识别解除） | 机制缺口（问题 3） |
| PROD_TOUCHED | 否（纯本地协议文档面） | —（全程 PROD_NOT_TOUCHED） | | |
| SCOPE+ | 否（0 条） | — | | |
| SCOPE_RESOLVED | — | — | | |
| DESIGN_GAP | 否（P4 三批偏差声明均否定式） | — | | |
| DESIGN_GAP_REVIEWED | 否（P7 显式配对 count=0） | ✅ | | |
| NEED_CONFIRM | 否（[NO_NEED_CONFIRM]） | — | | |
| CAPABILITY_GAP | 否（空表 + 判断树说明） | — | | |
| gate 验证（每阶段） | 是 | ✅（P1–P8 + P6.5 预跑全过；P6 自查预检 provenance exit 2 见问题 3） | | |
| 阶段产出文件（每阶段） | 是 | ✅（P1–P8 + P6.5 + P6-exit2-resolution 模板残留） | | |
| .state.yaml phase 同步 | 是 | ✅（P0→READY 全程同步） | | |
| 裁剪条件 + override | 否（全量无裁剪） | — | | |
| capability_requirements | 是 | ✅（空表 + 无浏览器/视觉依赖判定） | | |
| 分阶段落盘 | 是 | ✅（三批 implementer 各自落盘 + 共享 P4-implementation.md 章节式合并） | | |
| phase-产出一致性 | 是 | ✅（commit 时 phase=产出阶段） | | |
| P6 evidence | 是 | ✅（24 文件 + 引用 + EXIT_CODE） | | |
| P2 候选方案 + 权衡 | 是 | ✅（2 候选 + 权衡 + 选择理由） | | |
| P8 internal_only_reason | —（未裁 P8） | — | | |
| dispatch-context.md | 是 | ✅（每派发先写后派；P6.5 首写违规一次修复，见问题 2） | | |
| pre-commit hook | 是 | ✅（P4/P8 SELF-GATE WARNING 按规则处理） | | |
| CI backstop | 是 | ✅（CHECK 7 并行 tag 失败由 CI 捕获 → tag 移最终 commit，见问题 4） | | |
| 技术债登记 | 是 | ✅（DEBT0024/25/26 关闭 + RM-AG0057 done；本复盘新缺口 5 项候选 RM 见 §四 1-5，待主 Agent 立项登记编号） | | |

## agate 反馈

- P1 gate 缺 frontmatter phases ↔ 正文裁剪声明的交叉机械校验（问题 1）：字段格式合法 ≠ 字段语义与正文一致，语义一致性全靠 review 人工读；建议 check-frontmatter/P1 gate 对"phases 缺项 vs 全覆盖声明 vs 不可裁阶段"做交叉校验。
- P6.5 judge 信息隔离白名单约束未从脚本源码显式化进卡/派发模板（问题 2）：执行者只能从脚本报错反推规则；建议 P6.5 卡与 judge 派发模板补固定句 + 校验器报错附修复指引。
- agate-next P6→P7 裁决未区分 provenance WARNING（exit 2）与 ERROR（exit 1）（问题 3）：WARNING 级字段债被误判"验收异常"假暂停并落盘未填模板；建议退出码分级 + P3 侧补 agent 字段存在性检查（手工写惯例易漏）。
- 并行发布共享版本命名空间的时序无规则（问题 4）：merge 引入兄弟 tag 后 `git describe` 取最近 tag 非最高版本，CHECK 7 假失败；建议发布清单扩展 DEBT0013 时序注意至并行场景（先同步 main → 冲突全解 → bump+tag 于最终 commit → 复核 describe），共享表文件（roadmap/tech-debt/CHANGELOG）merge 后须行级去重核对。
- DEBT schema 校验器 check-debt 无 gate/CI 挂载 + closed 证据 `P[56]` 子串启发式过弱（问题 5）：关闭动作合规零机械复核、正文引文可偶然满足证据规则；建议 P8 卡 DEBT 关闭节绑定 check-debt exit 0、证据判定收紧为引用关闭任务证据，并将 debt/roadmap 从 docs-only 快路径的"全量校验豁免"中区分出来。
