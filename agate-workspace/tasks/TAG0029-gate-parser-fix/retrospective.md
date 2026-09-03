---
task_id: TAG0029
mechanism_issues:
  - P8 看板 commit 触发 pre-commit P5 gate 重跑全量（phase=READY 产出面与 gate 消费面错位）
  - ruff 未纳入 P4 派发约束与主 Agent 自查清单（CI 才暴露实现文件 lint 失败）
  - N5 签名 grep 口径与反引号引用格式证据行不匹配（计数 0 但实质齐全）
execution_issues:
  - SELF-GATE commit message 自审路径格式两次写错位置（WARNING 两次）
  - DEBT 关闭 evidence 初版编造聚合文件名（后修正为真实逐文件路径）
  - BDD-7 豁免前缀 startswith 风险由测试侧 in 语义先行暴露，主 Agent 才后补为 P4 约束（顺序倒置）
feedback_ready: false
---

# 复盘 — TAG0029 gate 命令解析器修复批

## 一、事实基线

- 任务：TAG0029（RM-AG0056 + DEBT0027 high + DEBT0023），worktree `.worktrees/agate-TAG0029`，分支 `feat/TAG0029-gate-parser-fix`，PR #270（普通 merge，非 squash），tag v0.67.1（patch，v0.67.0→v0.67.1），远端到达已验。
- 阶段：P0–P8 全量无裁剪；P1 9 BDD；P2 3 候选选 A；P3 10 用例（A 批 4 + B 批 6）；P4 四处实现 + S1/I1 + SELF-GATE 7 ALIGNED；P5 全量 1444 passed（首次 1 flaky 复跑绿）；P6 9/0 + 三 gate 全过；P6.5 judge passed 9/9；P7 BLOCKER=0；P8 bump + roadmap done + DEBT 关闭。
- 重试：P2 round 1 empty_return（architect 中断）/ round 2 quality（review rejected B1）；P3 round 1 empty_return（test-designer 空返回，拆 AB 批恢复）。P2/P3 均未超限（MAX 3/2）。
- gate：P1/P2/P3/P5/P6/P7 预跑全过；P4 gate exit 0；P6.5 双脚本 exit 0；P8 脚本化通过；consistency 0 ERROR（329 WARNING 历史存量）；CI 全绿后合并（ruff 曾 fail 1 次，本地修复后翻绿）。
- 涉及文件：3 脚本（read-gate-commands/judge-R2豁免）+ P2 卡禁令节 + formatters README + judge docstring + CHANGELOG/UPGRADING/README 双 badge + S1 测试同步 + 10 新用例。

## 二、做得好的 + 可复用模式

- **P2 §2.5 显式取舍声明是 P8 发布说明的免费草稿**：历史多栈形态退役 + 白名单后缀清单在设计期写成面向用户语言，P8 CHANGELOG 转正与 UPGRADING 草案逐字复用，零翻译成本。→ 回馈 agate（architect.md 批次设计节可加一句"取舍写成用户语言"的提示）。
- **中断缺证据由主 Agent 补 grep 后重派**：P2 首轮 architect 中断在"P3 存量用法"证据缺口，主 Agent 亲自补全仓 grep（P3_xxx 从未被真实任务声明）写进上下文后重派，一轮即产出。→ 项目资产沉淀（本任务 dispatch-context 已落盘，可作 P2 重派范例）。
- **fail-closed 验收绑"残渣零产出"原子项**：BDD-2 把"exit 非 0 + stderr + 不产出残渣"绑成一条，避免 fail-half-open 半修复过门。→ 回馈 agate（test-designer.md P3 自检节可收录此句式）。
- **豁免强度 = 逃逸成本**：R2 豁免选目录声明绑定而非宽匹配，评审问"借用它要付出什么"（改一行字 vs 搬家）。→ 回馈 agate（architect.md 豁免设计可收录此判据）。
- **DEBT0024 真实调用约束逐批落实**：judge/解析器/扫描器用例全部调真实函数与子进程，零 mock exit 码。→ 执行纪律保持，无需沉淀。

## 三、发现的问题

- 问题 1：P8 看板 commit（phase=READY）触发 pre-commit P5 gate 重跑全量（41s），phase=READY 产出面与 gate 消费面错位。
  归因层面: 机制缺口
  说明：pre-commit 按 .state.yaml phase 跑 check-gate，READY 无对应 gate 分支却触发 P5 重跑；看板更新本应是零 gate 的纯状态 commit。
- 问题 2：ruff 未纳入 P4 派发约束与主 Agent 自查清单，CI 才暴露实现文件 2 处 lint 失败（冗余 import + UP031）。
  归因层面: 执行错误
  说明：AGENTS.md 收尾自检要求快速反馈类检查（test/lint/type-check），P4 派发约束未写 ruff，主 Agent 自查也未跑；协议有定义但未执行。
- 问题 3：SELF-GATE commit message 自审路径格式两次写错位置（括号行中/正文行），hook 正则要求行首 `self-gate-review:`。
  归因层面: 执行错误
  说明：SELF-GATE.md 派发模板写明路径格式，主 Agent 两次未按行首格式写；WARNING 不拦截但属重复犯错。
- 问题 4：N5 签名 grep 口径（行首 `^(PASSED|FAILED|...)`）与反引号引用格式证据行不匹配，计数 0 但实质签名齐全。
  归因层面: 机制缺口
  说明：P5 卡 N5 缓解的 grep 口径假设签名行顶格，而 verifier 按可读性写反引号引用；口径与实际写法脱节，靠主 Agent 人工豁免而非机械通过。
- 问题 5：DEBT 关闭 evidence 初版编造聚合文件名（`bdd-4-5-6.log`），与真实逐文件证据路径不符，后修正。
  归因层面: 执行错误
  说明：真实路径就在 P6-evidence/ 下可查，主 Agent 为省事编造聚合名；属可查证事实的编造，不可接受。
- 问题 6：BDD-7 豁免前缀 startswith 风险由 B 批测试侧 `in` 语义先行暴露，主 Agent 才后补为 P4 实现约束（顺序倒置）。
  归因层面: 机制缺口
  说明：P2 §3.4 写"路径前缀判定"未明确禁止 startswith，测试先用 `in` 写对、实现约束后补；设计应对实现语义做禁止性声明（同 B1 匹配表的"推测项不得加回"写法）。

## 四、改进措施

1. 针对问题 1：看板更新类纯状态 commit 是否应跳过 P5 gate 重跑，由后续任务评估（`pre-commit-gate.py` phase=READY 分支：仅状态文件变更时跳重跑或降 WARNING）。落点文件：`agate/scripts/pre-commit-gate.py` + P8 卡 READY 节。候选 roadmap RM，不在本任务登记（DEBT0026 式执行域，可归 TAG0030/31 评估）。
2. 针对问题 2：P4 派发约束模板补 `ruff` 自查行（`~/.venvs/agate-dev/bin/ruff check agate/scripts/` + 改动文件），与全量 pytest 抽查并列。落点：本任务 P4 上下文已口头要求，协议层落 `agate/assets/execution-roles/implementer.md` 自查节。候选 roadmap RM，同上。
3. 针对问题 4：N5 grep 口径扩展反引号引用格式（或 verifier 单元模板固定签名行顶格输出）。落点：`agate/phase-cards/P5-verification.md` N5 节。候选 roadmap RM，同上。
4. 针对问题 6：architect.md 豁免/判据设计节加"禁止性语义声明"要求（实现不能用的形态要写出来，不只写能用的）。落点：`agate/assets/execution-roles/architect.md`。候选 roadmap RM，同上。
5. 问题 3/5 为执行纪律：self-gate 行首格式 + evidence 真实路径， convoluted 无需修协议；本复盘记录即闭环。

## 技术债登记核对清单

| 机制 | 应该触发？ | 实际触发？ | 未触发后果 | 原因 |
|------|-----------|-----------|-----------|------|
| retry 记录 | 是（P2 中断/P2 打回/P3 空返回） | ✅（P2×2 + P3×1 全记录） | | |
| PAUSED | —（未超限） | — | | |
| PROD_TOUCHED | —（纯本地） | —（全程 PROD_NOT_TOUCHED） | | |
| SCOPE+ | —（0 条） | — | | |
| SCOPE_RESOLVED | — | — | | |
| DESIGN_GAP | —（0 条） | — | | |
| DESIGN_GAP_REVIEWED | — | — | | |
| NEED_CONFIRM | —（[NO_NEED_CONFIRM]） | — | | |
| CAPABILITY_GAP | —（空表） | — | | |
| gate 验证（每阶段） | 是 | ✅（P1–P8 预跑全过） | | |
| 阶段产出文件（每阶段） | 是 | ✅（P1–P8 + P6.5 全齐） | | |
| .state.yaml phase 同步 | 是 | ✅（P0→READY 全程同步） | | |
| 裁剪条件 + override | —（全量无裁剪） | — | | |
| capability_requirements | 是 | ✅（空表 + 判断树说明） | | |
| 分阶段落盘 | 是 | ✅（A/B/progress 全落盘；首派空返回即靠此恢复） | | |
| phase-产出一致性 | 是 | ✅（commit 时 phase=产出阶段） | | |
| P6 evidence | 是 | ✅（9 日志 + EXIT_CODE + 引用） | | |
| P2 候选方案 + 权衡 | 是 | ✅（3 候选 + 稻草人自检） | | |
| P8 internal_only_reason | —（未裁 P8） | — | | |
| dispatch-context.md | 是 | ✅（每派发先写后派 + inject-card） | | |
| pre-commit hook | 是 | ✅（P4/P8 SELF-GATE WARNING 按规则处理） | | |
| CI backstop | 是 | ✅（ruff fail 捕获 + 全绿后合并） | | |
| 技术债登记 | 是 | ✅（DEBT0023/0027 关闭 + RM-AG0056 done；新缺口 4 项候选 RM 见 §四） | | |

## agate 反馈

（feedback_ready: false，本节暂空。§四 4 项候选 RM 待用户确认是否立项后再反馈。）
