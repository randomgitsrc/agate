---
task_id: TAG0031
mechanism_issues:
  - "P6.5 judge dispatch-context 白名单比通用 dispatch-protocol 约定更严格（仅 5 个固定文件名，不含 gate-diagnosis.md），且分散在 check-judge-verdict.py 源码里，P6-acceptance.md/P6.5 相关卡片未显式复述——主 Agent 按通用惯例（引用 gate-diagnosis.md）写 dispatch-context 两次触发白名单/预判扫描拦截"
  - "P8 卡片未覆盖『多个并行任务共享 CHANGELOG/README 版本徽章/git tag 序列』场景下各任务应如何协调版本号——三路并行（TAG0029/30/31）场景下产生了错误的初始假设（延后到合并后统一处理），与实际先完成的兄弟任务 TAG0029 已独立走完标准 P8 流程的事实不符，需要中途改变策略（merge origin/main + 重新规划版本号）"
execution_issues:
  - "P6.5 dispatch-context 首次撰写时直接引用了 gate-diagnosis.md 路径（不在白名单内）、且示例代码块使用了字面 `- PASS BDD-1:` 触发预判扫描——两处均属于对已有规则（dispatch-protocol.md 白名单定义）执行不到位，非规则缺失"
feedback_ready: true
---

# TAG0031 复盘 — DEBT 存量修复批

## 一、事实基线

- 任务规模：7 条历史遗留 DEBT（DEBT0002/3/4/7/16/17/18），P1 拆为 15 条 BDD，三簇并行拆批
  （version-mgmt / test-isolation / gate-robustness）
- 改动文件：5 个生产脚本（`agate_common.py`/`agate-pack-offline.py`/`install-offline.py`/
  `agate-install.py`/`check-gate.py`）+ 2 个文档（`UPGRADING.md`/`scripts/README.md`）+
  7 个测试文件（新增 3 + 扩展 4）+ `debt/tech-debt.md`（7 closed + 2 open 新登记）
- gate 重试记录：`retries[P1]` 1 轮（requirements-review needs-revision：同类扫描口径失真 +
  DEBT 登记闭合覆盖缺失）；`retries[P2]` 1 轮（plan-eng-review rejected：R1 pyyaml checksum
  顺序缺口 + `[SCOPE+]` 格式未闭环）；P3/P4 各出现 1 处非 retry 计数的意外回归（encoding 守卫
  单引号误触发 / ruff import 排序），均在 commit 前发现修复，未进入 retry 账本
- P6.5 judge：账本记账 `judge_verdict` 事件 1 次（`judge 轮次×1`），但产出文件因主 Agent
  dispatch-context 撰写问题实际派发 3 轮（1 次判定 + 2 次纯格式修正，判定内容全程未变）
- 全量 pytest：本任务改动前 1412 passed（P1 阶段基线）→ 完成时 1445 passed（含合并
  TAG0029 v0.67.1 带入的 10 项），0 failed 全程保持
- P8 版本号处理经历一次策略变更：初始决定"三路并行延后版本处理"→ 发现兄弟任务 TAG0029 已
  独立完成标准 P8（v0.67.1，已合并 main）→ 改为跟进（merge origin/main + bump v0.67.2）

## 二、做得好的 + 可复用模式

- **三簇并行 + 独立复核链**（P3/P4 各三个 subagent 并行 + 主 Agent 每轮独立跑测试验证，不采信
  subagent 自述）在全程保持了"发现问题即时修复"的节奏，两处意外回归（encoding/ruff）均在
  commit 前被主 Agent 独立全量测试发现并定向修复，未带着已知缺陷推进下一阶段——去向：①回馈
  agate（该模式已是既定协议要求，本次是执行验证，无需新增协议内容）
- **P8 版本 bump 前先 `git merge origin/main` 同步兄弟并行任务的已发布状态**：本次是临场发现
  问题后补救，但验证有效（1 处可预期的文本重复冲突，其余全部自动合并，合并后重跑全量测试/
  consistency 确认无回归）——去向：**回馈 agate**，建议 P8 卡片补充"多路并行任务发布前建议
  先同步主分支最新状态"的检查项，见下方「改进措施」
- **judge dispatch-context 格式问题的诊断-修复循环**：三轮迭代（错误类型定位准确、每轮只改
  必要内容、判定内容全程未被污染）验证了"gate 失败先诊断根因、只修复不重判"的分层处理是可行
  且高效的（3 轮修复合计耗时远小于重新走一次完整 judge 独立复核）——去向：回馈 agate（已是
  既定协议模式，本次是执行验证）

## 三、发现的问题

- 问题：P6.5 judge 的 dispatch-context 白名单（`p1-requirements.md`/`p2-design.md`/
  `.state.yaml`/`gate-events.jsonl`/`p6.5-judge-verdict.md` 五个固定文件名）比其余阶段的通用
  dispatch-context 惯例（"上游关联"节引用 gate-diagnosis.md 路径）严格得多，且该白名单定义
  只存在于 `check-judge-verdict.py` 源码常量里，P6-acceptance.md 卡片正文和
  dispatch-protocol.md「Judge 信息隔离」节虽有提及白名单存在，但未把完整清单和"连
  gate-diagnosis.md 都不在内"这一反直觉细节显式列出。
  归因层面: 机制缺口
  说明：这是为防锚定刻意设计的严格白名单（合理），但文档呈现方式使得主 Agent 按其余阶段的
  惯例惯性去写会两次踩坑（第一次踩白名单外文件名，第二次踩全文 PASS/FAIL 预判扫描——示例
  代码块本身也被扫描，这一点同样不直观）。

- 问题：主 Agent 撰写 P6.5-dispatch-context-judge.md 首版时未意识到"输入文件/上游关联"两节
  的白名单扫描如此严格，直接引用了 gate-diagnosis.md；第二版修复时又在"约束"节的示例代码块里
  用了字面 `- PASS BDD-1:`，触发了作用于全文（非仅两节）的预判扫描。
  归因层面: 执行错误
  说明：dispatch-protocol.md 已经定义了"dispatch-context 禁止包含 PASS/FAIL 预判"这条通用
  规则（不限于两节），主 Agent 撰写示例时没有意识到这条规则同样约束"举例说明格式用的示例文本"，
  属于对既有规则理解不到位，不是规则缺失。

- 问题：P8 阶段初始按"三路并行任务应统一延后版本处理"的假设执行，与实际情况（兄弟任务
  TAG0029 已独立走完标准流程并合并 main）不符，导致需要中途改变策略。
  归因层面: 机制缺口
  说明：P8 卡片和 HANDOFF 文档均未对"多个并行任务如何协调共享的 CHANGELOG/版本号/git tag
  资源"给出明确指引——三路并行的具体分工由项目侧交接单口头约定（"文件域不重叠"），但版本号/
  CHANGELOG 这类**全仓单点资源**天然会被三路都触及，协议对此没有覆盖规则，主 Agent 只能临场
  推测，推测结果与实际不符。

## 四、改进措施

1. **P6.5 卡片补充白名单速查**：`phase-cards/P6-acceptance.md`（或专门的 P6.5 小节）里显式
   列出 dispatch-context「输入文件」「上游关联」两节的完整白名单清单（5 个固定文件名），并
   明确标注"gate-diagnosis.md 不在白名单内，修复指引必须内联写在'约束'节，不能放在这两节里
   引用"，避免下一次 P6.5 撰写者重复踩坑。落点：`agate/phase-cards/P6-acceptance.md`。
2. **dispatch-context 撰写补一条自检**：`dispatch-protocol.md`「dispatch-context 规范」节
   补充"含示例代码块时同样要避免行首 `- PASS/FAIL BDD-N:` 字面文本，可用占位符替代"这一具体
   注意事项（当前只有抽象规则"禁止包含预判"，没有点出"举例文本也算"这一常见误踩点）。落点：
   `agate/dispatch-protocol.md`「dispatch-context 规范」节。
3. **P8 卡片补"多路并行发布协调"节**：说明当同一批次存在多个并行任务且各自独立走 P8 时，
   建议在 bump-version 前先 `git merge`/`rebase` 主分支最新状态，确认版本号/CHANGELOG 位置
   未被其他已完成任务占用，避免临场推测。落点：`agate/phase-cards/P8-release.md`。
4. **技术债登记**：为改进措施 1-3 登记一条 DEBT（`source: retrospective`，本次任务
   `task_id: TAG0031`），归类"低优先级协议文档完善"，避免这三条改进意见随复盘归档后被遗忘。

## 技术债登记核对清单

| 机制 | 应该触发？ | 实际触发？ | 未触发后果 | 原因 |
|------|-----------|-----------|-----------|------|
| retry 记录 | 是 | ✅ | — | P1/P2 各 1 轮，已记入 `.state.yaml` retries |
| PAUSED | 否 | — | — | 全程无 retry 超限/不可逆操作需确认场景 |
| PROD_TOUCHED | 否 | — | — | 全程 `[PROD_NOT_TOUCHED]`，未接触 `~/.agate`/生产环境 |
| SCOPE+ | 是 | ✅ | — | P2 阶段发现 R1 pyyaml checksum 顺序问题，已标 `[SCOPE+]` |
| SCOPE_RESOLVED | 是 | ✅ | — | P1-requirements.md 已补 `[BASELINE_CHANGE]`+`[SCOPE_RESOLVED]` |
| DESIGN_GAP | 是 | ✅ | — | P4 implementer 标注 identity 断言与零依赖约束的折中方案 |
| DESIGN_GAP_REVIEWED | 是 | ✅ | — | P7 consistency-reviewer 逐字转抄 + 接受判定 |
| NEED_CONFIRM | 否 | — | — | 全程 `[NO_NEED_CONFIRM]` |
| CAPABILITY_GAP | 否 | — | — | 无特殊能力需求（backend 脚本任务） |
| gate 验证（每阶段） | 是 | ✅ | — | P1-P8 每阶段主 Agent 均亲自跑 gate 脚本 |
| 阶段产出文件（每阶段） | 是 | ✅ | — | P0-P8 全部产出齐全 |
| .state.yaml phase 同步 | 是 | ✅ | — | 每次 commit 前同步更新 |
| 裁剪条件 + override | 否 | — | — | 未裁剪任何阶段（risk_level=medium 不满足裁剪前提） |
| capability_requirements | 是 | ✅ | — | P1 声明 available（backend 脚本开发环境） |
| 分阶段落盘（防 subagent 空返回） | 是 | ✅ | — | 全部 dispatch-context 遵循默认落盘指令，无空返回 |
| phase-产出一致性 | 是 | ✅ | — | pre-commit hook WARNING 均为预期内（P3 阶段测试文件属于产出） |
| P6 evidence | 是 | ✅ | — | 15 条 BDD 各自独立证据文件（pytest -v 输出/grep 日志） |
| P2 候选方案 + 权衡（≥2） | 是 | ✅ | — | 候选方案 1（三簇并行）vs 候选方案 2（单批顺序），已选定并说明理由 |
| P8 internal_only_reason | 否 | — | — | 未裁剪 P8 |
| dispatch-context.md | 是 | ✅ | — | 每次派发前均先写 dispatch-context |
| pre-commit hook | 是 | ✅ | — | 全程通过 hook 校验（含 WARNING 提醒均已核实非阻断） |
| CI backstop | 是 | — | 待 PR 后 CI 验证 | 本地已跑全量 gate，CI 兜底待 PR 触发 |
| **技术债登记** | 是 | ✅ | — | DEBT0002/3/4/7/16/17/18 七条 closed + DEBT0028/0029 两条新登记 open；本复盘另建议登记一条协议文档完善类 DEBT（见「改进措施」4） |

## agate 反馈

- **P6.5 judge 白名单文档化不足**：`check-judge-verdict.py` 定义的 dispatch-context 白名单
  （仅 5 个固定文件名，不含 gate-diagnosis.md）比通用 dispatch-context 惯例严格得多，但完整
  清单只存在于脚本源码常量里，未在面向人类撰写者的卡片/协议文档中显式列出，容易导致按通用惯例
  撰写时踩坑（本次踩了两次：白名单外文件引用 + 全文 PASS/FAIL 预判扫描误伤示例代码块）。建议
  在 P6-acceptance.md 或 dispatch-protocol.md「Judge 信息隔离」节补充完整白名单清单 +
  "示例文本也受预判扫描约束"的显式提示。
- **P8 缺少多路并行任务的版本协调指引**：当同一批次存在多个并行 worktree 任务且各自独立走
  P8 发布准备时，协议未定义应如何协调共享的 CHANGELOG.md/README 版本徽章/git tag 序列这类
  全仓单点资源。本次任务因此在 P8 阶段基于不完整信息做出了错误的初始假设（延后到合并后统一
  处理），发现兄弟任务已独立完成标准流程后才改变策略。建议 P8 卡片补充"多路并行发布前建议先
  同步主分支最新状态，确认版本号资源未被占用"的检查项与操作指引。
