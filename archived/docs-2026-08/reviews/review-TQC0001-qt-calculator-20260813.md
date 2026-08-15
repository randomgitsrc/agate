# TQC0001（Qt 简单计算器）P0-P8 全流程复盘

- 复盘日期：2026-08-13
- 任务：TQC0001-qt-calculator（Qt 6.8.3 Widgets + C++17 + CMake/Ninja/MinGW，Windows 桌面简单计算器）
- 状态：DONE（tag v0.1.0）
- 依据：opencode session 客观记录（主会话 + 15 个 subagent 会话，`C:\Users\Administrator\.local\share\opencode\opencode.db`）、git commit log（10 个提交）、`.gate-history.jsonl`（10 条 gate 运行记录）、各阶段产出文件
- 结论：流程闭环、交付质量达标；过程中暴露 5 类机制/管理/技术问题，其中 2 类（state.phase 与 commit gate 联动、Windows 路径适配）具系统性，需在协议与文档层面固化处置。

---

## 1. 完成情况总览

### 1.1 交付物

| 项 | 结果 |
|---|---|
| 需求 | 31 条 BDD 全部验收 PASS（22 张互不相同截图 + 22 份 vision 报告 blocker=0） |
| 测试 | 84/84 全绿（引擎 18 / 控制器 34 / UI e2e 32） |
| 代码 | `src/core`（CalcEngine/CalcFormat）+ `src/ui`（CalcController/MainWindow）+ `src/main.cpp` |
| 发布 | `dist/qt_calculator.exe` 独立可运行（18 文件：8 顶层 DLL + 8 插件），offscreen 冒烟通过 |
| 版本 | version.txt=0.1.0，CHANGELOG.md 已建，tag `v0.1.0` |

### 1.2 commit log（客观记录）

| commit | 阶段 | 内容 | 文件数 |
|---|---|---|---|
| 2db238d | P1 | 需求基线 31 BDD approved | 9 |
| 3b0da0d | P2 | 方案设计 approved（3 轮评审闭环） | 5 |
| 9c2dbae | P3 | 测试设计 31/31 BDD 红灯（QTest 三件套） | 6 |
| 431a789 | P4 | 实现完成 84/84 + 修复 P3 测试缺陷 | 18 |
| d83901a | P5 | 技术验证 84/84 全通过（fail-list 空） | 4 |
| 3618e75 | P6 | 验收 31/31 PASS（22 截图 + vision） | 50 |
| 0daf62e | P7 | 一致性检查通过（SCOPE+ 2/2 闭环） | 2 |
| 81f8c3f | P8 | 发布 0.1.0（windeployqt + CHANGELOG + version） | 6 |
| 064a78b | READY | 收尾（任务看板 + phase=READY） | 2 |
| 1e125c2 | DONE | 任务完成 | 1 |

### 1.3 session 记录（opencode.db，客观记录）

主会话 `ses_007588afaffeXN0p5BvBhprvWk`（orchestrator，01:05–03:29，约 2h24m）。15 个 subagent 会话全部挂载其下：

| 会话 ID | 阶段/角色 | 起止（UTC） | 时长 |
|---|---|---|---|
| ses_0074b9ba6ffehHE1gHrQHxlZZN | P1 analyst | 01:19:59–01:25:56 | 6m |
| ses_00747be01ffeNj4E7cTZe1168c | P1 requirements-review | 01:24:12–01:25:17 | 1m |
| ses_0073c128fffeDsMU7yEcNs0F4P | P2 architect | 01:36:57–01:52:16 | 16m |
| ses_007384084ffe5g1E54p0zZq0cr | P2（短会话，异常后重发） | 01:41:08–01:41:57 | **49s** |
| ses_007374b68ffegkAz3L1hj8hYWB | P2 plan-design-review | 01:42:10–01:52:59 | 11m |
| ses_0072bdc6affeLds6iLiHkpzMKt | P3 test-designer（首派） | 01:54:40–01:57:31 | **3m** |
| ses_00728fbe7ffetzQyx777vE367y | P3 test-designer（恢复） | 01:57:48–02:25:47 | 28m |
| ses_0071fcca5ffe1TCLhWQxDzd1F7 | P4 implementer | 02:07:50–02:26:58 | 19m |
| ses_0070da301ffejpLY75H5Os0ziL | P4 design-review | 02:27:40–02:30:22 | 3m |
| ses_0070977cbffe00jD0pILMNGpUg | P5 verifier | 02:32:14–02:35:58 | 4m |
| ses_00704f2f4ffeZpP0BtQQQyf1k9 | P6 verifier | 02:37:10–02:59:21 | 22m |
| ses_006f047e0ffepvqgYm6emWnYiy | P6 vision-analyst | 02:59:44–03:12:54 | 13m |
| ses_006e2674affeYwPLG9nOlbkcFz | P7 consistency-reviewer | 03:14:54–03:17:02 | 3m |
| ses_006de96dfffebZnGkpwng1c3H9 | P8 releaser | 03:19:04–03:19:59 | 1m |

注：P3/P4 有并行时段（P4 implementer 02:07:50 启动，与 P3 test-designer 恢复会话 02:07–02:25 重叠），属测试修复与实现并行的合理编排。

### 1.4 gate 运行历史（`.gate-history.jsonl` 客观记录，10 条）

| 时间 | phase | exit | 上下文 | 判定 |
|---|---|---|---|---|
| 01:27:08 | P2 | 1 | P1 首次 commit 尝试（state 超前至 P2） | 失败 |
| 01:28:00 | P1 | 2 | P1 commit 重试（hash mismatch） | 需手动判断 |
| 01:29:40 | P1 | 2 | P1 commit 重试（hash mismatch） | 需手动判断 |
| 01:36:02 | P1 | 2 | P1 commit 重试（hash mismatch） | 需手动判断 |
| 01:53:14 | P3 | 1 | P2 首次 commit 尝试（state 超前至 P3） | 失败 |
| 01:53:33 | P2 | 2 | P2 改回后 | 需手动判断 |
| 02:07:12 | P3 | 2 | P3 commit | 需手动判断 |
| 02:31:10 | P4 | 0 | P4 gate | 通过 |
| 02:36:11 | P5 | 2 | P5 gate | 需手动判断 |
| 03:13:54 | P7 | 0 | P6 产出 commit（state 超前至 P7，产出缺失仍 0） | 通过（侥幸） |
| 03:17:26 | P8 | 1 | P7 首次 commit 尝试（state 超前至 P8） | 失败 |
| 03:20:47 | P8 | 2 | P8 commit | 需手动判断 |

---

## 2. 问题清单（按阶段）

### Q1（P1）commit gate 失败 ×4：卡片 hash mismatch（AGATE_ROOT 路径格式）

- **现象**：P1 首次 commit 失败（GATE P2 exit 1），随后 P1 gate 连续 3 次 exit 2 后 commit 成功。根因是 hook 校验 `agate-next-card.sh` 相对路径卡片哈希不一致（EMBEDDED ≠ EXPECTED）。
- **机理（技术/平台）**：pre-commit hook 用 `AGATE_ROOT` 前缀做相对路径计算 `${CARD_FILE#$AGATE_ROOT/}`。在 Windows 下，若 `AGATE_ROOT=C:\Users\Administrator\.agate`（Windows 风格），与卡片文件绝对路径 `D:\...\agate\...`（或其他盘符/正斜杠风格）前缀不匹配，相对化失败 → 卡片头残留绝对路径行 → 哈希漂移。改用 Unix 风格 `/c/Users/Administrator/.agate` 后前缀匹配成功，哈希稳定。这是 **agate 脚本对 Windows 路径假设不足** 的典型例子（默认 Unix 环境，未对盘符/正斜杠做归一化）。
- **处置（已做）**：固化 commit 配方——`AGATE_ROOT=/c/Users/Administrator/.agate` + `PYTHONUTF8=1` + Git Bash 执行。
- **建议**：
  1. agate 脚本层做路径归一化（统一正斜杠、盘符 `C:` ↔ `/c/` 互转），消除环境敏感性；
  2. SETUP.md 增加 Windows 章节，明示"AGATE_ROOT 必须使用 Unix 路径格式"，并给出完整 commit 配方。

### Q2（P2、P7）state.phase 与 commit gate 联动错位（系统性，两次踩坑 + 一次侥幸）

- **现象**（gate-history 客观记录）：
  - P2：01:53:14 尝试 commit，state 已被卡片指引推进到 P3 → hook 跑 GATE P3 exit 1（P3 产出缺失）→ 改回 P2 → 01:53:33 GATE P2 exit 2 → commit 成功。
  - P7：03:17:26 尝试 commit，state 被推进到 P8 → hook 跑 GATE P8 exit 1（P8-release.md 缺 bump_type）→ 改回 P7 → commit 成功。
  - P6（侥幸）：03:13:54 时 state 一次推进到 P7，GATE P7 exit 0——因 P7 gate 对"产出缺失"宽容返回 0，未被拦截。
- **机理（agate 机制）**：pre-commit hook 以 `.state.yaml` 的 `phase` 为 gate 目标阶段。而各阶段卡片（P2 卡"更新 phase=P2→P3"、P7 卡"更新 phase=P7→P8"）都把"推进 state 到下一阶段"放在 commit **之前**——当下一阶段产出未就绪时，commit 必然触发下一阶段 gate。不同阶段 gate 脚本对"目标阶段产出缺失"的处理不一致（P7 exit 0 宽容、P3/P8 exit 1 严格），进一步放大了不确定性。**卡片模板的步骤顺序与 hook 机制存在结构性冲突**。
- **处置（已做）**：经验规则——commit 时 state 必须等于该 commit 产出的阶段；跨阶段推进放到产出 commit 之后（或与下一阶段产出同 commit）。
- **建议**：
  1. 修订各阶段卡片：把"更新 .state.yaml 到下一阶段"移到"git commit"之后，并加注"commit 时 phase 必须等于本 commit 产出的阶段"；
  2. hook/gate 脚本统一"目标阶段产出缺失"的可辨识退出码（如 exit 3 = 产出未就绪），与真实 gate 失败（exit 1）区分，避免主 Agent 混淆；
  3. gate 脚本对缺失产出的宽容行为（P7 exit 0）应改为显式提示而非静默通过。

### Q3（P3）测试代码缺陷 ×2（编译错误 + 必然失败断言），P4 才发现

- **现象**：`tst_ui_e2e.cpp` displayText() 为 `QString` 返回函数却使用 `QVERIFY2`（编译错误）；`tst_controller.cpp` bdd_01 依赖从未发出的信号日志（断言必然失败）。两处缺陷由 P4 implementer 构建时发现并修复（P4-implementation.md §4 记 2 个 [SCOPE+]，均"已解决"）。
- **机理**：
  - **技术**：QTest 宏误用（`QVERIFY2` 需 bool 表达式，在非 void 返回函数中编译失败）；信号断言未正确初始化/等待（QSignalSpy 时序问题）。
  - **agate 机制**：P3 阶段测试代码在 CMakeLists 与实现代码未就绪时无法进入真实构建验证；`check-tdd-red` 若将"编译失败"也计为红灯（exit 0），则编译缺陷被误判为"预期红灯"而放行。P3 缺"测试代码可编译"独立检查，也无测试代码评审环节。
  - **管理**：test-designer 产出未经编译冒烟即交付 P4，质量责任后移。
- **处置（已做）**：implementer 修复测试（SCOPE+ 记录留痕）；P4 全量构建 84/84 回归。
- **建议**：
  1. P3 卡增加前置检查：测试代码最小可编译（独立于被测代码的小构建或静态检查 QTest 宏用法）；
  2. `check-tdd-red` 区分"编译失败"（error，exit 非 0）与"断言失败"（红灯，exit 0），杜绝编译错误冒充红灯；
  3. 测试代码引入评审角色或由 test-design-review 复核宏使用/信号断言。

### Q4（P2、P3）subagent 短命会话：空返回/失败后恢复重发

- **现象**（session 客观记录）：P2 有 49 秒会话 `ses_00738408...`、P3 有 3 分钟首派会话 `ses_0072bdc6...`，随后均通过恢复会话（architect `ses_0073c128...`、test-designer `ses_00728fbe...`）完成任务。
- **机理（平台）**：opencode general subagent 偶发返回空且无产出（瞬态故障/上下文构建失败），与任务复杂度无强相关（短会话后重发即成功）。
- **处置（已做）**：带 `task_id` 恢复会话重发。
- **建议**：派发协议增加"空返回自动重试一次"；会话时长 <1min 自动判定异常并告警。

### Q5（P4/P5/P8）Windows 环境适配问题簇（PATH / 乱码 / LF-CRLF / .gitignore）

- **现象**：
  - `cmake`/`ctest` 不在默认 PATH，gate 命令（P5）首次运行失败；
  - gate 脚本中文输出在 PowerShell 控制台乱码（GBK vs UTF-8）；
  - `git add` 持续 LF→CRLF 警告；
  - `.gitignore` 的 `*.txt` 误伤 P8 的 `version.txt`（git add 被忽略），需 `!version.txt` 白名单；
  - P8 的 `dist/` 打包产物需追加忽略。
- **机理（平台/管理）**：agate 脚本与文档假设 Unix 环境；Windows 控制台默认 GBK；`core.autocrlf=true`；.gitignore 规则设计未前瞻 P8 产物。
- **处置（已做）**：PATH 注入配方（`D:\Qt\Tools\CMake_64\bin;D:\Qt\Tools\Ninja;D:\Qt\Tools\mingw1310_64\bin;D:\Qt\6.8.3\mingw_64\bin`）；`PYTHONUTF8=1`；.gitignore 白名单 `!version.txt` + `dist/`。
- **建议**：
  1. SETUP.md 增 Windows 章节（PATH 注入、Git Bash 执行、AGATE_ROOT Unix 路径、PYTHONUTF8）；
  2. hook/gate 输出统一英文或显式 UTF-8，消除乱码干扰；
  3. agate 模板 .gitignore 预设 `!version.txt` 与 `dist/`，避免后续任务重复踩坑。

### Q6（P8）CHANGELOG gate 警告：[Unreleased] 段被替换未保留

- **现象**：P8 commit 输出 `GATE CHANGELOG: 警告 — [Unreleased] 未记录 TQC0001`（WARNING 不阻断）。
- **机理（agate 机制）**：CHANGELOG gate 要求 `[Unreleased]` 段存在并记录任务；releaser 直接将 `[Unreleased]` 段整体替换为 `0.1.0`，未保留 `[Unreleased]` 占位头。
- **处置（已做）**：接受 WARNING；CHANGELOG 已含 `0.1.0 - 2026-08-13` 记录。
- **建议**：P8 卡/releaser 指引明确"新版本段与 `[Unreleased]` 空占位段并存"；CHANGELOG 模板固化该结构。

### Q7（P6）视觉验收能力受限：无多模态模型，b17 前置态截图仍判 PASS

- **现象**：vision-analyst 无法直接"看"截图（模型无视觉输入），退化为像素分析 + OCR + assert-bdd.log 佐证；b17 截图显示前置态"34"仍判 PASS（以行为日志为准，已在报告中注明）。
- **机理（模型能力）**：当前模型（deepseek-v4-flash-free）无视觉通道，视觉验收本质是启发式代理，存在漏检风险；check-p6-evidence 报 16 组视觉相似 WARNING（不阻断）亦源于截图内容高度雷同（表达式变化但 UI 相似）。
- **处置（已做）**：双证据原则（截图 + assert-bdd.log 行为日志）；b17 判据如实记录。
- **建议**：
  1. 接入多模态模型执行真实视觉验收；
  2. 无视觉能力时强制"截图 + 行为日志"双证据，输入态变化类用例（如 b17）加人工复核；
  3. 对"截图与上一状态 md5 相同/雷同"自动降级为待复核，而不是仅 WARNING。

### Q8（P8/READY）冒烟进程残留

- **现象**：READY 收尾 `Get-Process` 发现 `qt_calculator`（PID 21312）仍在运行（releaser 冒烟启动后未完全退出）。
- **机理（管理）**：冒烟验证的启动/关闭未做成原子操作（finally-kill 缺失），或 offscreen 子进程清理时序问题。
- **处置（已做）**：READY 收尾逐项实查（非凭记忆打勾）并强杀进程；确认临时数据（p6pkg/p6shots）已删、无 `[PROD_TOUCHED]`（P5 产出已有 `[PROD_NOT_TOUCHED]`）、工作区干净、tag 存在。
- **建议**：冒烟验证脚本内置 finally-kill；subagent 报告"进程已清理"须经主 Agent 复核（本次已复核，流程有效）。

### Q9（P6）无 GUI 自动化框架（技术决策，非缺陷）

- **现象**：无 Playwright 等 GUI 自动化框架，UI e2e 用 QTest offscreen 信号级模拟 + P6 截图。
- **机理（技术/平台）**：Windows 环境未配置 GUI 自动化框架；agate P6 视觉验收需截图证据。
- **处置（已做）**：P2 固化 `add_test NAME=ui_e2e` + offscreen 运行 + 22 张截图；全部 31 BDD 用信号级断言覆盖。
- **建议**：保持现有模式；如需真实 GUI 交互测试，评估 WinAppDriver/AutoIt 并提前在 P2 决策；当前决策已记录于 P2 gate_commands。

---

## 3. 按维度归因总结

### 3.1 agate 机制原因（Q2、Q3、Q6，含 Q1 脚本适配）

1. **state.phase 推进步骤与 commit gate 的冲突**（最重）——阶段卡片把"推进 state"放在 commit 前，而 hook 以 state.phase 为 gate 目标；跨阶段产出缺失时 gate 失败/侥幸通过并存。触发 2 次真实失败（P2、P7）+ 1 次侥幸（P6）。
2. **gate 对"目标阶段产出缺失"行为不一致**——P7 exit 0（宽容）、P3/P8 exit 1（严格），导致主 Agent 对失败判定不可预期。
3. **check-tdd-red 对"编译失败"与"断言失败"未区分**——测试代码编译错误可冒充红灯放行。
4. **CHANGELOG gate 的 [Unreleased] 要求未在模板/指引中固化**——releaser 替换而非保留，触发 WARNING。
5. **脚本路径假设 Unix**——AGATE_ROOT 前缀相对化在 Windows 盘符/斜杠下失效，引发 hash mismatch。

### 3.2 管理原因（Q3、Q4、Q8）

1. subagent 产出（测试代码）缺乏编译冒烟前置检查，质量责任后移至 P4。
2. 短命会话（空返回）依赖主 Agent 经验性重试，缺制度化重试协议。
3. 冒烟验证启动/关闭未原子化，残留进程由收尾兜底发现。
4. 正面项：READY 收尾逐项实查（非凭记忆打勾）、gate 历史留痕完整，使本次复盘有据可依。

### 3.3 技术原因（Q3、Q7、Q9）

1. QTest 宏误用（QVERIFY2 在非 void 函数）、信号断言时序错误——测试代码技术质量缺陷。
2. 模型无视觉通道，视觉验收退化为启发式（像素/OCR）——能力边界需双证据/人工复核补偿。
3. UI e2e 信号级模拟覆盖良好（84/84），但真实 GUI 交互路径未覆盖（无 GUI 框架）——已知取舍。

### 3.4 平台/环境原因（Q1、Q5）

Windows 下 Unix 假设（路径格式、PATH、编码、行尾、ignore 规则）集中爆发，消耗若干轮调试；均为一次性适配，固化配方后不再复现。

---

## 4. 处置措施与建议（按优先级）

### 立即固化（下次任务前）

| # | 措施 | 归属 |
|---|---|---|
| R1 | 修订阶段卡片：state 推进移到 commit 之后；卡片顶部加"commit 时 phase = 本 commit 产出阶段"强制注记 | agate 机制 |
| R2 | hook/gate 对"目标阶段产出缺失"返回统一 exit 3（产出未就绪），与 exit 1（真实失败）区分 | agate 机制 |
| R3 | SETUP.md 增 Windows 章节：AGATE_ROOT Unix 路径、PATH 注入配方、Git Bash 执行、PYTHONUTF8=1、标准 commit 配方 | 文档 |
| R4 | agate 模板 .gitignore 预设 `!version.txt` 与 `dist/` | 模板 |
| R5 | P3 卡增加"测试代码最小可编译"前置检查；check-tdd-red 区分编译失败与断言失败 | agate 机制 |

### 中期改进（1-2 个任务内）

| # | 措施 | 归属 |
|---|---|---|
| R6 | 派发协议增加"空返回自动重试一次"；<1min 会话告警 | 管理 |
| R7 | releaser 指引/CHANGELOG 模板固化"[Unreleased] 空占位 + 新版本段"并存 | agate 机制 |
| R8 | P6 视觉验收：无多模态模型时强制双证据 + 输入态变化类用例人工复核；雷同截图自动降级待复核 | 管理/机制 |
| R9 | 冒烟验证脚本内置 finally-kill，进程清理结果由主 Agent 复核 | 管理 |

### 长期建议

| # | 措施 | 归属 |
|---|---|---|
| R10 | agate 脚本层路径归一化（盘符/斜杠统一），消除 Windows 敏感性 | agate 机制 |
| R11 | 接入多模态模型做真实视觉验收；评估 WinAppDriver/AutoIt 覆盖真实 GUI 交互路径 | 技术 |
| R12 | gate 脚本对缺失产出行为统一审查（本次已发现 P7 宽容 / P3/P8 严格的不一致） | agate 机制 |

---

## 5. 结论

TQC0001 全流程（P0–P8）在约 2.5 小时内闭环：10 个提交、15 个 subagent 会话、31 BDD 全验收、84 测试全绿、独立 exe 打包发布（v0.1.0）。流程治理有效（gate 历史完整、dispatch-context 注入哈希 100% 一致、SCOPE+ 留痕、READY 收尾实查），未发生需求漂移或生产污染。

主要代价集中在 5 个问题上：state 推进与 commit gate 的机制冲突（2 次失败 + 1 次侥幸）、Windows 路径适配（4 次 gate 重试）、P3 测试缺陷后移（2 个 SCOPE+）、短命会话重试（2 次）、视觉验收能力受限（b17 启发式判 PASS）。其中前两类具系统性，建议按 R1/R2/R3 在协议与文档层面立即固化，其余按 R5/R6/R8 渐进改进。

> 复盘依据声明：本报告 commit log、session 记录、gate 历史均取自客观存储（git / opencode.db / .gate-history.jsonl），未凭记忆补记未发生事件；个别机制推断（如 check-tdd-red 编译失败判定）基于行为观察，标注为推断待验证。
