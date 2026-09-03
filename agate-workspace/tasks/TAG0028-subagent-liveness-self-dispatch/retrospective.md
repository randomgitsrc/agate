---
task_id: TAG0028
mechanism_issues:
- "gate_commands 行内注释污染命令解析（agate-read-gate-commands.py 值清洗不剥离行内注释/残留引号 → bash -c 语法错误 exit 2 → check-tdd-red judge 分支假绿灯），P2 fix2 仅规避未修解析器"
- "平台假设扫描器 R2 静态误伤 fixture 数据面（模拟平台日志的 command 数据串含裸 python3 → 破坏 TAG0011 bdd-8 tests 树 0 命中），P5 round 1 红灯回 P4 fix3 才闭环"
execution_issues:
- "P4 review rejected 后主 Agent 误派重复 implementer（fix1 完成后又派 0d1c7f28 随即 interrupt）——执行纪律问题"
feedback_ready: true
---

# TAG0028 复盘 — subagent 存活可观测性与受控自主再派发（RM-AG0055）

## 一、事实基线

- 任务跨度：2026-09-03 单日集中执行（P0 commit 999c672 13:43 → P8 commit 837fc52 19:00，
  约 5.5 小时）；P0-P8 全流程 + P6.5 judge 独立复核，发布 v0.67.0（PR #262 merged）
- 任务 commit 链 12 个：P0 999c672 → P1 b6581e3 → P2 d120453 / 2f1d887（fix2）→ P3 50d48c6 →
  P4 6964dbf / 34366ab（fix3）→ P5 700f074 → P6 58569fa → P6.5 6fd4e2b → P7 6aba3e4 → P8 837fc52
- retries（.state.yaml 记录）：P1 round 1（quality，独立评审 needs-revision → fix1 修复
  3 红线 + 3 次要）；P4 round 1（quality，review rejected 7 CRITICAL → fix1）；P4 round 2
  （quality，fix1 复审 rejected 残留 CRITICAL-4 → fix2）
- gate/review 失败：P1 review needs-revision 1 次（fix1 后 approved）；P4 review rejected 2 次
  （fix1 7 CRITICAL、fix2 复审 2 残留崩溃链 → approved）；**P5 round 1 全量 pytest 1 failed**
  （bdd-8 R2 回归，本任务引入）→ fix3 → P5 round 2 全 5 key PASS
- 测试量级：P3 42 用例（38 红 + 4 长期不变量绿）→ P4 fix1 后 cmdstream 53 passed；
  P5 全量 **1434 passed / 0 failed / 2 skipped**（count-tests 1436 ≥ 749 基线）
- BDD：P1 初稿 25 条 → fix1 拆号/新增后 **33 条**（BDD-1~33 全局连续）；P6 验收 33/33 PASS；
  P6.5 judge 33/33 passed；P7 blocker=0（DESIGN_GAP 4/4 REVIEWED、CODE-MAP 3/3 SYNC）
- P4 修复链：fix1（7 CRITICAL：CLI 毫秒/秒单位错配、DSH zstd 多帧只解第一帧、未结束 call
  通路不可达、Claude 畸形输入崩溃链、OpenCode SQLite 损坏崩溃、from_dict 无类型校验、
  DSH truncated 恒 False，+11 新测试）→ fix2（CRITICAL-4 残留 2 崩溃链 + 4 类畸形输入测试）→
  fix3（R2 回归 17 处裸 python3 → env python3）
- 涉及文件：agate/scripts 3 新脚本（ir/adapters/detect）+ check-p6-provenance.py 登记 +
  dispatch-protocol.md / role-system.md / dispatch-context.md 模板改写 + maintainability.yaml +
  agate/tests 5 新测试文件 + 2 fixture + 任务目录产出

## 二、做得好的 + 可复用模式

**填写引导语（强制追问）**：本次产生的临时命令/脚本/经验，哪些该沉淀为项目固定资产？
沉淀到哪？——架构模式与流程经验已由 P8 releaser 沉淀进 `docs/notes/lessons.md`（§11 三条），
复盘不重复沉淀；以下标注去向。

- **适配器模式收敛外部数据源脆弱性**：三平台命令流格式（JSONL / SQLite / JSONL.zstd）与
  exit 信号三形态（数字 / "Exit code N" / "Error:"）完全不同且脆弱（平台改格式解析需跟随），
  用统一 CommandRecord IR + 每平台一个适配器 + 显式注册表 ADAPTERS 收敛平台细节，检测引擎
  平台无关（BDD-6 新增平台只写适配器）→ 去向：① 回馈 agate（架构模式，已落
  docs/notes/lessons.md 第 1 条；未来新增平台只写适配器的注册契约可复用）
- **两套信号职责显式分工**：存活/卡死判定（命令流日志）与语义进展（progress.md）是两套独立
  信号，改写协议节时明确边界表述防职责漂移；心跳文件审计豁免靠隐藏文件过滤天然覆盖但**显式
  登记确认**（check-p6-provenance.py 注释级 HEARTBEAT_AUDIT_EXEMPTION）而非默认假设 →
  去向：① 回馈 agate（已落 lessons 第 2 条；"豁免须显式登记不可假设"值得推广到其他审计面）
- **P4 review 独立运行时实证纪律**：review 不只读代码，独立跑 cmdstream 套件 + 4 类畸形输入
  崩溃实验 + node zstd 多帧实验，复现 CRITICAL-1/2/3 后再写 rejected 结论（非转述 implementer
  自报）→ 去向：① 回馈 agate——review 角色把"消费方实现 vs 真实运行时语义核对"列为 Pass 1
  必查项（TAG0027 复盘同款建议，本任务再次实证有效，机制未固化）
- **DESIGN_GAP 决策树正确执行**：P3 test_bdd_3 断言与 fixture 数据结构性矛盾（同 command
  键无法同时满足 exit==2 与 truncated==True），implementer 标 [DESIGN_GAP] **不改测试**，
  主 Agent 归因"测试设计缺陷"回派 test-designer fix1（过滤式匹配），P7 4/4 配对 REVIEWED →
  去向：① 回馈 agate（已落 lessons 第 3 条；断言与 fixture 矛盾先归因再动的处置路径验证有效）
- **review 修复轮 Fix 方向选项化 + 先补测试后改实现**：fix1 dispatch-context 对每个 CRITICAL
  给 Fix A/B/C 选项由 implementer 照做；修复先扩展测试确认红（int/null timestamp、非 dict
  toolUseResult 崩溃链）再落地守卫转绿 → 去向：② 项目资产沉淀（TAG0027 复盘同款做法保持，
  评审给选项 + 先红后绿记录于 P4-implementation.md 各 fix 节）

## 三、发现的问题

- 问题：gate_commands 行内注释污染命令解析 → check-tdd-red 假绿灯路径（P2 fix2，commit 2f1d887）
  归因层面: 机制缺口
  说明：`agate-read-gate-commands.py` 值清洗 `val = raw.strip().strip(chr(34)).strip(chr(39))`
  不剥离值内 `# 注释` 与残留引号——值不以 `"` 结尾时 `strip(chr(34))` 只剥开头引号，残留结尾
  `"` + 注释尾巴；check-tdd-red 的 `run_test_with_formatter` 用 `bash -c` 执行该命令时
  unterminated quote 语法错误（exit 2），judge 分支可能把该输出**误判为红灯可推进（假绿灯）**。
  触发：主 Agent 跑 P3 env baseline 时发现命令带注释尾巴，经最小 shell 验证确认语法错误。
  P2 fix2 只改注释形态（行内 → 独立行）**规避**了本任务，未修解析器缺口本身。教训：解析器
  应把"值内注释 + 引号闭合"当输入形态处理；check-tdd-red 把"命令语法错误"与"测试红灯"
  区分开，否则测试运行器故障会被吞成绿灯证据。

- 问题：平台假设扫描器 R2 静态误伤 fixture 数据面（P5 round 1 红灯 → fix3，commit 34366ab）
  归因层面: 机制缺口
  说明：R2 规则 `(^|[\s=(\'\"])python3([\s]|$)` 静态扫描无法区分"测试代码里的命令调用"
  （应禁止裸 python3）与"fixture 模拟平台日志的数据面内容"（command 字段模拟真实日志本应含
  `python3 -m pytest`）——cmdstream fixture 与断言串 17 处裸 python3 被命中，破坏 TAG0011
  bdd-8「agate/tests 树 0 命中」长期不变量，P5 全量 pytest 1 failed（本任务引入的回归）。
  修复利用 R2 显式豁免形态 `env python3`（命令语义不变）。已闭环但**扫描器缺 fixture 数据面
  的语义区分/豁免机制**，未来任何以"模拟平台日志"为 fixture 的测试仍会踩同一误伤；
  且平台假设扫描器不在 P3/P4 gate_commands 常驻面，回归要到 P5 全量才暴露。

- 问题：P4 review rejected 后主 Agent 误派重复 implementer（fix1 完成后又派一次 0d1c7f28，
  随即 interrupt）
  归因层面: 执行错误
  说明：P4 fix1 完成（7 CRITICAL 修复 + 11 新测试，09:37 返回）后，主 Agent 未等 fix1 复审
  （dispatch-context-review-fix1）结论即重复派发 implementer，发现后立即 interrupt。
  协议/卡片已定义"review rejected → implementer 修复 → 再 review"同轮次迭代（P4 卡片「重试」
  节 + C8 映射），无协议缺口——属派发时序核对缺失的执行纪律问题，浪费派发资源与子上下文。

## 四、改进措施

- **修 gate 命令解析器 + check-tdd-red 判定分层**（针对问题 1）：
  - 落点：`agate/scripts/agate-read-gate-commands.py`——值清洗剥离行内注释（首个未转义 ` #`）
    与引号闭合校验，输出纯命令或报解析错误（exit 非 0 + stderr），不再产出带残渣的命令串；
  - 落点：`agate/scripts/check-tdd-red.py`——`run_test_with_formatter` 执行失败（exit 127 /
    语法错误 exit 2 / 命令不可解析）不得计入"红灯证据"，judge 分支仅在测试运行器正常退出时
    才判定红灯可推进（关联 RM-AG0002 A/B 类盲区既有语义，扩展覆盖语法错误类）；
  - 建议登记 DEBT0027（source: retrospective，本任务 P2 fix2 仅规避未修根因）。

- **平台假设扫描器区分代码面与 fixture 数据面**（针对问题 2）：
  - 落点：`agate/scripts/check-platform-assumptions.py` R2——对显式 fixture 数据面（如
    `agate/tests/fixtures/` 目录或数据串标记）豁免或按上下文判定，区分"测试代码调用"与
    "模拟外部日志的数据内容"；
  - 落点：P3/P4 阶段自查命令补平台假设扫描器预跑（当前不在 gate_commands 常驻面，回归到
    P5 全量才暴露——建议把扫描器纳入 P3 test-designer 自查或 P4 自查清单）；
  - 建议登记 roadmap backlog（RM-AG0056 候选，待登记）。

- **派发前查重核对时序**（针对问题 3）：
  - 落点：主 Agent 执行纪律——review rejected 后派 fix 轮前先查任务目录既有
    `P4-dispatch-context-implementer-fix{N}.md` 与 progress 时间线，确认上一 fix 轮已返回且
    fix 内容未被重复派发；不新建协议机制（P4 卡片重试节已覆盖），只补派发动作前的查重自检。

## 技术债登记核对清单

| 机制 | 应该触发？ | 实际触发？ | 未触发后果 | 原因 |
|------|-----------|-----------|-----------|------|
| retry 记录 | 是（P1 round 1、P4 round 1+2）| ✅（.state.yaml retries 记录）| — | — |
| PAUSED | 否（无 retry 超限/跨阶回退/不可逆操作）| — | — | — |
| PROD_TOUCHED | 否 | ✅（全任务各阶段 [PROD_NOT_TOUCHED]，fixture 脱敏未读他人会话）| — | — |
| SCOPE+ | 否（P7 核对 P1-P4 无 SCOPE+ 增补）| — | — | — |
| SCOPE_RESOLVED | 否 | — | — | — |
| DESIGN_GAP | 是（P4 4 条：test_bdd_3 断言矛盾 / ts_end 放宽 / DSH 截断双信号 / CLI --expected）| ✅（P4-implementation 4 条）| — | — |
| DESIGN_GAP_REVIEWED | 是 | ✅（P7 4/4 配对 REVIEWED）| — | — |
| NEED_CONFIRM | 否（P1 [NO_NEED_CONFIRM]，无实跑偏差待决）| — | — | — |
| CAPABILITY_GAP | 否（capability_requirements 3 项全 available 无 GAP）| — | — | — |
| gate 验证（每阶段）| 是 | ✅（P5 round 1 红灯 → 归因 fix3 → round 2 全 PASS；P8 AUDIT7 reuse_allowed）| — | — |
| 阶段产出文件（每阶段）| 是 | ✅（P0-P8 + P6.5 全产出）| — | — |
| .state.yaml phase 同步 | 是 | ✅（gate-events.jsonl state_transition 链完整）| — | — |
| 裁剪条件 + override | 否（全量 P1-P8）| — | — | — |
| capability_requirements | 是（dsh-zstd-decompression / platform-session-parsing / detection-logic-verification）| ✅（P1 §7 三态全 available）| — | — |
| 分阶段落盘（防 subagent 空返回）| 是 | ✅（各阶段 progress + P4-progress 记录到分钟级）| — | — |
| phase-产出一致性 | 是 | ✅（pre-commit 多次拦截/放行，commit 与 phase 对齐）| — | — |
| P6 evidence（含截图 + 引用 + vision YAML）| 是 | ✅（P6-evidence 36 文件全引用 + P6.5 judge 33/33）| — | — |
| P2 候选方案 + 权衡（≥2）| 是 | ✅（候选 A 平铺脚本族+显式注册表 / B 单脚本聚合 / C 子目录包，选 A）| — | — |
| P8 internal_only_reason | 否（走完整 P8，protocol-alignment-review）| — | — | — |
| dispatch-context.md | 是 | ✅（各阶段 + fix1/fix2/fix3 轮 dispatch-context 齐备）| — | — |
| pre-commit hook（gate / 状态转移 / 裁剪）| 是 | ✅（gate-events.jsonl 16 条 gate_run/state_transition 留痕）| — | — |
| CI backstop | 是 | ✅（release PR #262 merged 后 CI 全绿）| — | — |
| **技术债登记** | 是（复盘发现 2 个机制缺口）| ✅（本复盘登记建议：**DEBT0027**（gate_commands 解析器 + check-tdd-red 假绿灯）+ **roadmap backlog RM-AG0056 候选**（R2 fixture 数据面），落账动作由主 Agent 复盘后执行）| 若零登记则重蹈 DEBT0001（复盘发现缺口不落账）| 机制缺口（登记触发 = 本复盘产出）|

## agate 反馈

1. **gate 命令解析器不处理行内注释与引号闭合，且测试运行器故障可被吞成"假绿灯"**：值清洗
   （`strip().strip(chr(34)).strip(chr(39))`）对"值内 `# 注释` + 残留引号"的输入产出带残渣命令
   串，消费方 `bash -c` 执行触发 unterminated quote（exit 2）；check-tdd-red 的 judge 分支把
   该输出当"红灯可推进"，测试运行器本身的故障被误读为测试失败证据。建议：① 解析器剥离值内
   注释并校验引号闭合，产出纯命令或报解析错误；② check-tdd-red 仅在测试运行器正常退出时
   判定红灯，语法错误/命令不可解析（exit 127 / 2）不计入红灯证据。
2. **平台假设扫描器 R2 无法区分测试代码调用面与 fixture 数据面**：静态规则命中"模拟平台日志
   的 fixture 数据串"（command 字段模拟真实日志内容含裸 `python3`），破坏 tests 树 0 命中
   长期不变量，且该扫描不在 P3/P4 自查常驻面、回归到 P5 全量才暴露。建议：R2 对显式 fixture
   数据面豁免或按上下文判定，并将平台假设扫描纳入 P3/P4 阶段自查命令。
