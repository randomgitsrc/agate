i# 复盘：Qt 简单计算器项目实施过程（qtcalc-basic）

- 复盘日期：2026-08-13
- 项目：`D:\home\oclab\playground\qtcalc-basic`（C++17 / Qt 6.8.3 Widgets / CMake+Ninja+MinGW 13.1）
- 依据：本次 opencode 会话的工具调用与输出记录（构建日志、ctest 结果、windeployqt 输出、PowerShell 验证输出），以及复盘时针对"机理存疑点"做的补充验证实验（见 §3）。
- 范围：P0（设计）→ P1（骨架）→ P2（引擎+单测）→ P3（UI 接线）→ P7（打磨+验收）→ P8（打包）。

---

## 1. 客观记录的基本事实（必须先说明的两点）

> 复盘要求"包含调用 subagent 的会话"与"commit log"，基于本次 session 的客观记录，如实说明如下：

1. **subagent 调用：本次会话为 0 次。** 全部实现由主代理直接完成（工具调用类型为 bash/read/write/edit/grep 等，未触发 `task`/`explore` 等 subagent）。工程探索规模小、上下文可控，未达到需要委派的复杂度，这是可以接受的决策；但项目若扩大（多模块并行、大规模重构），应引入 subagent 并纳入复盘。
2. **commit log：不存在。** 环境启动时即标注 `Is directory a git repo: no`，会话过程中未执行 `git init`，也没有任何提交。因此本复盘无法基于提交历史做时间线对齐。**这是治理层面的缺口**，详见问题 I。

其余事实均来自会话内的可复核输出：P1 构建失败 2 次、P2 测试首跑 10 过 2 挂、P3 ctest 出现过 0xC0000135、P8 部署目录缺文件导致首次独立启动失败等，均可在本文 §2/§4 对应编号中找到。

---

## 2. 客观过程时间线

| 阶段 | 关键事件 | 结果 / 产物 | 暴露的问题（编号） |
|---|---|---|---|
| P0 | 先出整体设计（初稿为"表达式模式+递归下降"）→ 用 question 工具确认 3 个决策 | 用户选择：`%`=÷100、**即时运算模式**、写 DESIGN.md | K（设计前提与产品意图偏差） |
| P0' | 按决策重写 DESIGN.md §4 为"运算符栈+优先冲刷"状态机 | 设计定稿 | 无 |
| P1 | 写 CMakeLists + main.cpp + MainWindow 骨架 + 引擎桩文件 | **构建失败 1**：`qt_add_executable(... WIN32_EXECUTABLE)` → `Cannot find source file: WIN32_EXECUTABLE` | A |
| P1 | 改用 `add_executable` + `WIN32_EXECUTABLE` 属性 | **构建失败 2**：`CalcEngine/CalcEngine.h`、`ui/MainWindow.h` 找不到 | B |
| P1 | 补 `target_include_directories(qtcalc PRIVATE src)` | 构建通过，产出 `build/qtcalc.exe`；"启动验证 RUNNING OK"（事后证明为**假阳性**） | G |
| P2 | 实现 CalcEngine 状态机 + Formatting + QTest | 首次构建出现 g++ `-Woverflow` 多字节字符警告 → **预警后主动修复**（`QChar(0x00D7)` 方案） | D |
| P2 | 首次 ctest：`tst_calcengine` 0xC0000135 | 在 PATH 补 MinGW bin 后运行：**10 过 2 挂** | G、E、F |
| P2 | 修复括号待定符误弹（`inputOpenParen` 丢 `×`）+ 修正测试用例字面量 | 12/12 全绿 | F、E |
| P3 | MainWindow 按钮/键盘接线 + `tst_gui` 冒烟测试 | ctest 2/2 全绿（含 GUI 冒烟） | G |
| P7 | UI 打磨（5×5 布局、QSS、固定尺寸）+ DESIGN.md §6/§8 同步 | 测试保持全绿 | L（轻微） |
| P8 | `windeployqt --no-compiler-runtime --dir deploy` | 首次 0xC0000135（PATH 缺 MinGW bin）→ 补 PATH 后部署成功；但 `deploy/` **缺 exe、缺 3 个 MinGW 运行时 DLL** | H、G |
| P8 | 手工拷贝 exe + 运行时 DLL → 干净 PATH 启动 | "STANDALONE OK"（复盘时用模块检查确认为**真运行**） | G、H |

---

## 3. 复盘补充的机理验证实验（保证"机理分析准确"）

针对会话中几处"原因未定/存疑"的点，复盘时做了可复现实验，结论如下：

### 实验 1：`qt_add_executable` 关键字解析（问题 A 机理）
- 最小工程复现：`qt_add_executable(repro WIN32_EXECUTABLE main.cpp)` → 同样的 `Cannot find source file: WIN32_EXECUTABLE`。
- 读宏源码 `D:/Qt/6.8.3/mingw_64/lib/cmake/Qt6Core/Qt6CoreMacros.cmake`：
  - L641-656：`qt6_add_executable(target)` 仅 `cmake_parse_arguments(... "MANUAL_FINALIZATION" ...)`，其余参数（`arg_UNPARSED_ARGUMENTS`）原样传给 `add_executable`。
  - L675：`list(REMOVE_ITEM ARGN "WIN32" "MACOSX_BUNDLE")` **只存在于 `if(ANDROID)` 分支**。
- **结论（确定）**：Qt 6.8.3 桌面端 `qt_add_executable` **不接受 `WIN32_EXECUTABLE`/`WIN32` 关键字**，传入即被当作源文件。正确做法是 `add_executable` + `set_target_properties(WIN32_EXECUTABLE TRUE)`（本项目采用）。该属性还控制 `Qt6::EntryPointPrivate`（`Qt6CoreTargets.cmake` L65）是否链接，即是否提供无控制台窗口的 `wWinMain`。

### 实验 2：运行期 PATH 与"假 RUNNING"（问题 G 机理）
- 事实：`libgcc_s_seh-1.dll / libstdc++-6.dll / libwinpthread-1.dll` 仅在 `D:/Qt/Tools/mingw1310_64/bin`，**不在** `D:/Qt/6.8.3/mingw_64/bin`；本机机器/用户级 PATH 均无 Qt/MinGW 项。
- 实验（`Get-Process -Module`）：
  - `qtcalc.exe`（GUI 子系统）仅 System32 PATH 启动：**12 个模块，无任何 Qt/libgcc/libstdc++**，但进程 2 秒后仍未退出 —— 卡在系统"缺少 DLL"错误弹窗上。
  - 同一 exe 加 Qt+MinGW bin 后：71 个模块，含 `Qt6Widgets.dll / libgcc_s_seh-1.dll` 等，真运行。
  - `tst_calcengine.exe`（控制台子系统）仅 System32 PATH：5 个模块，进程存活但无目标 DLL —— 同样停在装载阶段；ctest 下则直接返回 `0xC0000135 (STATUS_DLL_NOT_FOUND)`。
- **结论（确定）**：GUI 子系统进程缺 DLL 时，系统弹错误对话框、进程**短暂存活**，`Start-Process + HasExited` 判定会给出**假 "RUNNING OK"**。会话早期 P1/P3 的两次"RUNNING OK"即属此类（当时未验证模块加载）。正确的启动验证是**检查已加载模块**或依赖退出码。

### 实验 3：windeployqt 是否自动带运行时 DLL（问题 H 机理）
- 对 `build-release/qtcalc.exe` 用**默认参数**（不传 `--no-compiler-runtime`）重新部署到临时目录，`lib*` 检查结果：**仍为空**。
- **结论（确定）**：在本环境下，无论是否传 `--no-compiler-runtime`，windeployqt 都不会把 `libgcc/libstdc++/libwinpthread` 拷入部署目录（它无法定位编译器运行时）。本项目"手工拷贝 3 个 DLL"是**必需步骤**，不是可选项。同时验证 `deploy/` 最终产物在干净 PATH 下模块加载正常（`Qt6Core/Gui/Widgets` + 运行时齐全），**P8 的独立运行结论成立**（此前 "STANDALONE OK" 为真，尽管判定方法当时不可靠）。

---

## 4. 问题清单与根因分析

> 每个问题按 现象 → 机制原因 → 管理/流程原因 → 技术原因 → 处置与建议 展开。严重度：🔴高 / 🟠中 / 🟡低。

### A. `qt_add_executable` 关键字不被识别（🟡 技术）
- 现象：`qt_add_executable(qtcalc WIN32_EXECUTABLE ...)` 报 `Cannot find source file: WIN32_EXECUTABLE`。
- 机制原因：见 §3 实验 1 —— 6.8.3 宏仅解析 `MANUAL_FINALIZATION`，`WIN32_EXECUTABLE` 被当作源文件；对 `WIN32` 的剔除仅存在于 Android 分支。**已用宏源码+最小复现双证**。
- 管理/流程原因：把 Qt 文档/经验中的关键字直接套用，未在目标版本（6.8.3）上验证 API 行为。
- 技术原因：Qt 6 宏在不同小版本对关键字支持不一致，属于"文档与实现漂移"类问题；其错误信息（把关键字当源文件）极具误导性。
- 处置与建议：改用 `add_executable` + `set_target_properties(WIN32_EXECUTABLE TRUE)`（已验证稳定）；后续升级 Qt 小版本时，用最小工程先行验证 `qt_add_executable` 关键字集合；如条件允许，将此类验证沉淀为 CI 冒烟。

### B. 头文件 include 路径缺失（🟡 技术/流程）
- 现象：`CalcEngine/CalcEngine.h`、`ui/MainWindow.h` 均 `No such file or directory`。
- 机制原因：引号 include 先搜"当前文件所在目录"再搜 `-I` 路径；`src/CalcEngine/CalcEngine.cpp` 引用 `"CalcEngine/CalcEngine.h"` 时相对本文件目录解析为 `src/CalcEngine/CalcEngine/CalcEngine.h`，且未提供 `-Isrc`。
- 管理/流程原因：CMakeLists 先于 include 目录接线完成，属"配 CMake 时漏一步"的常见顺序问题；被首轮编译低成本捕获（编译错误，最便宜的反馈路径）。
- 技术原因：无（属于工程配置遗漏）。
- 处置与建议：CMake 目标创建后立即补 `target_include_directories(... PRIVATE src)`；把"include 目录"加入 P1 构建门禁自检清单。

### C. P1 阶段 CMake 引用了尚未存在的引擎文件（🟡 流程）
- 现象：P1 目标是"空窗口可构建"，但 CMakeLists 已列出 `CalcEngine/Formatting` 等源文件，不得不先写桩文件、P2 再替换。
- 管理/流程原因：阶段边界（P1/P2）与工程文件清单不同步——设计把引擎归 P2，但 CMake 骨架按"最终形态"一次性写全。
- 处置与建议：每阶段的 CMakeLists 只引用该阶段已实现的文件；或明确接受"桩文件"策略并在阶段计划中注明（本次实际采用后者，代价可忽略，但应在计划里写清楚）。

### D. 多字节字符字面量 `'×' / '÷'`（🟠 技术，隐患大、检出早）
- 现象：g++ 对 `QLatin1Char('×')`、`case '×':` 报 `-Woverflow: overflow in conversion from 'int' to 'char'`（如 `50103 → -73`）。
- 机制原因：源码为 UTF-8，`'×'`(U+00D7) 是两个字节（`C3 97`），C++ 将其作为**多字符常量**（implementation-defined int），窄化到 `char` 后值完全错误；`QChar(0x00D7).toLatin1()==0xD7` 永远匹配不上被破坏的 case 值。若未修复，`×/÷` 会落入默认分支或按 0 优先级处理，产生**静默错误结果**。
- 管理/流程原因：无（属代码写法问题），但暴露了"警告纪律"的重要性——本问题**在运行测试前由编译警告捕获并主动修复**，未进入测试面。
- 技术原因：非 ASCII 字符以 `char` 字面量写入代码，未显式使用 Unicode 码点。
- 处置与建议：非 ASCII 一律用 `QChar(0x00D7)` 显式码点（本项目已落实：引擎统一 `QChar(0x00D7)/0x00F7`、`switch(op.unicode())`，测试用 `ch.unicode()==0x00D7`）；建议构建门禁加入"零警告"或对 `-Woverflow` 置 `-Werror`，杜绝此类静默隐患。

### E. 测试 DSL 作者失误：字面 `'±'` 与映射 `'n'` 不一致（🟠 测试工程）
- 现象：`negate()` 用例 `"5±×3="` 期望 `-15`，实测 `15`（预期之外的失败）。
- 机制原因：测试驱动函数 `run()` 把 `n` 映射为取负，对**未知字符静默忽略**；用例里写的字面 `'±'` 不被识别而被跳过 → 实际执行 `5×3`。
- 管理/流程原因：DSL 未文档化、`run()` 未对非法 token 快速失败，作者笔误只有靠 QCOMPARE 失败才暴露；且与真实引擎缺陷（问题 F）混在同一轮 2 个失败中，需人工甄别。
- 技术原因：`run()` 的容错设计（静默忽略）掩盖了输入错误。
- 处置与建议：`run()` 对未知字符**断言失败**（fail-fast）；在测试文件顶部注释 DSL 表；把"DSL 映射"本身拆一个最小单测。这样作者错误会在第一时间暴露为明确的"测试数据非法"，而非疑似引擎 bug。

### F. 括号待定运算符误弹：`2×(3+4)` 得 7（🔴 引擎逻辑）
- 现象：`QCOMPARE(run("2×(3+4)="), "14")` 实测 `7`。
- 机制原因：`inputOpenParen()` 中 `if (m_awaiting) m_ops.pop_back();` 把待定的 `×` 弹掉了；而按状态机语义，`(` 前若有待定二元运算符，其**右操作数应正是该括号组的结果**，必须保留。修复：`(` 只压标记、`m_awaiting=false`，不弹运算符（已在代码落实）。
- 管理/流程原因（主因之一）：DESIGN.md §4.3 对"待定运算符 + `(` 的交互"描述不明确（"重置当前输入状态"易被实现为"丢弃待定运算符"），编码前**未按状态机示例逐条走查**。
- 技术原因（主因之二）：状态机规格不完整——`(` 需要"挂起"而非"重置"；同类边界（如空括号、`(` 后紧跟运算符需忽略）都是在实现中临时补充的规则。
- 处置与建议：①DESIGN.md 增补"`(` 保留待定运算符，其右操作数为括号组结果"的明确规则；②扩充括号×运算符交互用例（`2×(3+4)`、`2÷(3)`、`(2+3)÷(4-1)`、`(2+3)×(4+1)` 等），本次测试集已含 `2×(3+4)` 并成功拦截该 bug——**测试先行策略有效**；③后续可用表驱动/随机生成测试补充覆盖。

### G. 0xC0000135 DLL 缺失连锁 + 启动验证假阳性（🔴 环境/方法，影响多个阶段）
- 现象：ctest 下 `tst_calcengine` 返回 `0xC0000135`（STATUS_DLL_NOT_FOUND）；windeployqt 同样失败；而 P1/P3 的"RUNNING OK"事后证明为假阳性。
- 机制原因：见 §3 实验 2。Qt 运行库在 `D:/Qt/6.8.3/mingw_64/bin`，MinGW 运行库（`libgcc_s_seh-1.dll` 等 3 个）在 `D:/Qt/Tools/mingw1310_64/bin`，二者缺一即无法加载；GUI 子系统进程缺 DLL 时弹窗滞留 → "进程存活"判定不可靠。
- 管理/流程原因（主因）：环境约束说明（`env_constraints`）只给了构建命令，**未给出运行/测试/部署所需的完整 PATH 要求**；且会话内未做环境预检（PATH 内容、运行库位置），导致同一问题在 P2/P3/P8 反复触发。
- 技术原因：无（环境事实），但**验证方法有缺陷**——用 `Start-Process + HasExited` 判活，未校验模块加载。
- 处置与建议：①文档化运行 PATH：`D:/Qt/6.8.3/mingw_64/bin` + `D:/Qt/Tools/mingw1310_64/bin`（构建/测试/运行/部署统一）；②提供 `build.ps1 / test.ps1 / run.ps1 / deploy.ps1` 把环境与命令固化；③启动验证改用**模块检查**（`Get-Process -Module` 含 `Qt6*` 与 `lib*`）或控制台退出码；④环境预检脚本（PATH 完整性 + DLL 存在性）作为每个阶段开始的门禁。

### H. windeployqt 部署产物不完整（🟠 流程/技术）
- 现象：首次独立启动报"找不到文件"；检查发现 `deploy/` **缺 `qtcalc.exe`、缺 3 个 MinGW 运行时 DLL**。
- 机制原因：①windeployqt 只部署**依赖**，不拷贝目标 exe（exe 需手工拷入 `--dir`）；②本环境下无论是否 `--no-compiler-runtime`，都不拷贝运行库（见 §3 实验 3）；③还顺带拉入了 `Qt6Network` 及 `tls/generic` 插件（由 `qtuiotouchplugin` 引起，属体积浪费）。
- 管理/流程原因（主因）：DESIGN.md 未把打包写成**可执行的步骤清单**，P8 靠试错补齐（拷贝 exe、拷贝 3 个 DLL）；首轮"文件不存在"报错一度被误判为环境问题而非产物缺失。
- 技术原因：对 windeployqt 行为假设错误（误以为会拷贝 exe 与编译器运行库）。
- 处置与建议：①写 `deploy.ps1`：`windeployqt --release --no-translations --dir deploy ...` → `Copy-Item` exe → `Copy-Item` 3 个运行库 → 干净 PATH 模块检查自检；②部署验证两步走：先 `Test-Path` 关键产物，再启动+模块检查；③体积优化（可选）：排除无关插件需验证运行，属锦上添花，不做强制。

### I. 未初始化版本控制（🔴 管理/治理）
- 现象：项目至交付无 git 仓库、无提交历史（复盘的"commit log"项为空）。
- 管理/流程原因（主因）：多阶段（P1–P8）项目实施应在立项即 `git init`，按阶段提交；本次缺失导致：无可追溯的阶段快照、无法回滚/比对、复盘无法引用提交粒度证据。
- 技术原因：无。
- 处置与建议：**立项即建仓、阶段即提交**（如 `P2: engine + tests`、`P3: ui wiring`、`P8: deploy`）；提交信息遵循仓库既定风格；本次如需补建仓可由用户决定（不主动代劳）。

### J. 未使用 subagent（🟡 流程/可扩展性）
- 现象/事实：会话全程 0 次 subagent 调用。
- 评估：单项目、小规模、上下文可控，直接实现是合理选择；但对"大规模/多模块/并行"任务，应评估 subagent 委派（如 explore 先行摸查、general 并行子任务），并在复盘记录调用与产出。

### K. 设计前提与产品意图偏差（🟠 设计/需求）
- 现象：初稿设计按"表达式模式+递归下降"展开，用户经 question 工具确认选择**即时运算模式**，引擎设计整体重写为"运算符栈+优先冲刷"。
- 机制原因：初稿把风险清单中的"中缀求值/递归下降"默认成了输入模型，未先识别这是**产品决策**。
- 管理/流程原因（主因）：好的一面是**在编码前**用提问工具澄清了歧义（避免了最坏结果——按错误模型实现）；可改进的是**提问应在成稿前**：先呈现两种模型的交互/实现代价差异，再锁定设计文档，减少返工。
- 技术原因：无。
- 处置与建议：设计文档中凡涉及"模式选择"（输入模型、语义口径如 `%`）一律列为**前置决策点**，用 `question` 工具先问再写；DESIGN.md 增补"决策记录"小节（选了什么、为什么、代价）。

### L. 阶段计划与文档编号不一致（🟡 文档）
- 现象：P4/P5/P6（小数/括号/百分号·正负号）被合并进 P2，阶段表出现编号跳空（虽有注释说明）。
- 管理/流程原因：引擎逻辑天然聚合，拆阶段是计划粒度过细；合并合理，但文档同步滞后。
- 处置与建议：阶段表在合并时同步改版（如重排为 P1..P5），或明确保留跳号并标注"已并入 P2"；本复盘建议下次直接重排编号。

### M. 键盘事件空文本风险（🟡 技术稳健性）
- 现象/原因：初版 `keyPressEvent` 直接取 `event->text().at(0)`，修饰键/功能键下 `text()` 为空会 UB；已在编码时预置 `isEmpty()` 防护。
- 处置与建议：防御性键盘处理（仅当 `text().size()==1` 才取 `at(0)`）；按键路由集中到单一 `dispatch`，避免与按钮回调两套映射重复维护。

---

## 5. 做得好的方面（保留并强化）

1. **设计先行 + 前置决策确认**：P0 用 question 工具澄清 `%` 语义、输入模型、文档落盘，避免了按错误模型开发（K 的好面）。
2. **引擎/UI 解耦**：CalcEngine 不依赖 UI，纯逻辑可由 QTest 直接驱动，GUI 自动化受限的风险被有效对冲（引擎 12 项单测 + GUI 冒烟）。
3. **警告纪律**：D 问题在运行测试前由编译警告捕获并主动修复，未形成线上缺陷。
4. **测试先行拦截真实 bug**：F（括号丢运算符）被 `parentheses()` 用例当场拦截；修复后 12/12 全绿。
5. **逐阶段门禁**：P1 构建门禁、P2 单测门禁、P3 GUI 冒烟门禁、P8 部署验证门禁，每步验证后再推进。
6. **文档与实现同步**：DESIGN.md 随输入模型、UI 布局、验收清单的变更实时更新。
7. **打包产物真独立**：复盘实验确认 `deploy/qtcalc.exe` 在干净 PATH 下模块加载完整（虽然当时的判定方法不可靠，结论经复核成立）。

---

## 6. 改进建议汇总（按优先级）

**P0（立即，影响治理与正确性）**
- I：立项即 `git init`，按阶段提交；提交信息约定统一风格。
- G：环境预检脚本 + 文档化运行/部署完整 PATH（Qt bin + MinGW bin）；`build.ps1 / test.ps1 / run.ps1 / deploy.ps1`。
- G：启动/部署验证统一改用**模块加载检查**或退出码，废弃"进程存活"判定。

**P1（近期，影响工程健壮性）**
- A：固定使用 `add_executable` + `WIN32_EXECUTABLE` 属性；升级 Qt 时用最小工程验证关键字。
- D：构建门禁加"零警告"或对 `-Woverflow` 置 `-Werror`。
- F：DESIGN.md 增补状态机边界规则（`(` 保留待定运算符、空括号、`(` 后运算符忽略），扩充括号×运算符表驱动用例。
- H：将 P8 步骤固化为 `deploy.ps1`（含 `Test-Path` 预检 + 拷贝 exe/运行库 + 干净 PATH 模块自检）。

**P2（持续改进）**
- B/C：每阶段 CMake 只引用本阶段文件；include 目录接线进门禁自检清单。
- E：测试 DSL 对未知 token fail-fast 并文档化；拆 DSL 映射单测。
- J：大规模任务评估 subagent 委派，并在复盘记录。
- K/L/M：设计文档前置"决策记录"；阶段表合并时重排编号；键盘路由集中为单一 dispatch。

---

## 7. 附录：环境事实与证据索引

- 工具链：Qt 6.8.3 (mingw_64) @ `D:/Qt/6.8.3/mingw_64`；CMake 3.30.5 @ `D:/Qt/Tools/CMake_64`；Ninja @ `D:/Qt/Tools/Ninja`；g++ 13.1.0 @ `D:/Qt/Tools/mingw1310_64`。
- 关键 DLL 分布（实测）：Qt 运行库在 Qt bin；`libgcc_s_seh-1.dll / libstdc++-6.dll / libwinpthread-1.dll` 仅在 MinGW bin；机器/用户级 PATH 均无 Qt 项。
- 关键证据：`Qt6CoreMacros.cmake` L641-701（关键字解析与 Android 分支剔除）；`Qt6CoreTargets.cmake` L65（`WIN32_EXECUTABLE`→`Qt6::EntryPointPrivate`）；ctest 0xC0000135 输出；`Get-Process -Module` 12 vs 71 模块对比；windeployqt 默认部署 `lib*` 为空；最终 deploy 目录模块清单完整。
