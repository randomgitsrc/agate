# qtcalc-basic 与 qtcalc 项目对比分析报告

- 报告日期：2026-08-13
- 分析对象：
  - 项目 A：`D:\home\oclab\playground\qtcalc-basic`（Qt 简单计算器，基础版）
  - 项目 B：`D:\home\oclab\playground\qtcalc`（Qt 简单计算器，成熟版）
- 分析方式：基于两个项目的源码、测试、构建/打包产物、文档与工程治理痕迹逐文件阅读与比对
- 结论概览：两者是**同一功能目标的两次不同实现**。qtcalc-basic 简洁、UI 打磨更细、支持键盘输入；qtcalc 在架构分层、测试严谨度（BDD 驱动、84 用例全绿）、工程治理（git + 分阶段流程 + 复盘）上全面领先，并修复了 basic 中"缺 DLL 无法启动"这类打包问题。**推荐以 qtcalc 的工程化水平为基准，吸收 qtcalc-basic 的键盘输入与表达式次显示等 UX 优点**。

---

## 1. 分析维度

本报告从以下 9 个维度展开：

| 维度 | 关注点 |
|------|--------|
| D1 项目概况 | 目标、版本、技术栈、代码规模 |
| D2 架构设计 | 分层、模块职责、依赖方向、可测性 |
| D3 计算引擎设计 | 求值模型、状态管理、错误处理、语义边界 |
| D4 格式化策略 | double→字符串规则、精度、科学计数、溢出 |
| D5 UI 设计与交互 | 控件、布局、样式、键盘支持、视觉反馈 |
| D6 测试策略 | 覆盖范围、BDD 化程度、测试基础设施、运行平台 |
| D7 构建与打包 | CMake 组织、依赖管理、windeployqt、运行验证 |
| D8 工程治理与文档 | git/版本/CHANGELOG、流程产物、文档质量、遗留问题 |
| D9 总体评估 | 各自优势、不足、可迁移建议 |

---

## 2. 项目 A：qtcalc-basic 详细分析

### 2.1 项目概况（D1）

- 目标：Windows 桌面简单计算器，四则 + 连续运算 + 小数 + 括号 + 百分号 + 正负号，windeployqt 打包独立 exe。
- 版本：CMake `project(qtcalc-basic VERSION 0.1.0)`；目标 exe 名 `qtcalc`。
- 技术栈：C++17 + Qt 6（CMake 要求 6.5+，DESIGN.md 实际用 6.8.3）Widgets，CMake + Ninja + MinGW。
- 代码规模（含头文件）：
  - 源码：`CalcEngine.cpp` 372 行 + `Formatting.cpp` 23 行 + `MainWindow.cpp` 206 行 + `main.cpp` 11 行（+ 头文件 66 行）≈ 678 行。
  - 测试：`tst_calcengine.cpp` 152 行 + `tst_gui.cpp` 69 行 ≈ 221 行。
- 目录：`src/CalcEngine/`、`src/ui/`、`tests/`、`deploy/`、`build/`、`build-release/`、`docs/`、`progress/`、`DESIGN.md`。
- **无 git 仓库**，无 CHANGELOG、无 version.txt。

### 2.2 架构设计（D2）

- 两层架构：`ui/MainWindow → CalcEngine`。CalcEngine 不依赖 UI（仅依赖 QString/QVector/标准库），方向清晰。
- 引擎对外暴露 **12 个输入方法**（`inputDigit/inputDecimalPoint/inputBinaryOp/inputEquals/inputPercent/inputNegate/inputBackspace/inputClearEntry/inputClearAll/inputOpenParen/inputCloseParen`）+ 2 个查询（`display()/expression()`）。每个 input 方法返回更新后的显示串。
- 状态数据散落于引擎成员（`m_entry/m_ready/m_hasReady/m_awaiting/m_error/m_lastExpr` + 三个栈），**无显式状态枚举**，状态迁移隐含在方法分支中。
- 测试通过 `tests/CMakeLists.txt` 把 `src/` 下的 .cpp **直接编入测试可执行文件**（源码复制而非共享库），存在"同一份代码编入 3 个目标"的维护风险。

### 2.3 计算引擎设计（D3）

- 求值模型：**即时运算模式（流式 shunting-yard）**。维护数值栈 `m_values`、运算符栈 `m_ops`、括号索引栈 `m_parenIndex`，每按一次二元运算符就按优先级 `precedence()` 冲刷栈（`flushWhile`）。这是 DESIGN.md 明确选择的"即时版 shunting-yard"，非整串表达式解析。
- 内部字符：运算符统一用 Unicode `×`(0x00D7)、`÷`(0x00F7)，`(` 作为括号标记。
- 优先级：`+ -` = 1，`× ÷` = 2，`(` = 0（冲刷时遇到 `(` 停止）。
- 除零：`apply()` 中 `right == 0.0` → 置 `m_error = "除数为零"`，所有 input 方法入口检查 `m_error` 后直接短路。
- 语法容错：`(` 后无操作数等畸形输入 **忽略该次按键、不破坏现有状态**（如 `2+(` → 显示 "2"）。
- 连续运算：结果 `m_ready` 作为后续左操作数（`10+5= ×2=` → 30）。
- 百分号语义：`÷100`。支持作用于输入中 entry、就绪值 `m_ready`、等待操作数（`50+10%=` → 50.1；`200×10%=` → 20；`50+%=` → 50.5）。
- 正负号：输入中翻转 entry 符号；否则翻转 ready/栈顶值。
- 输入限制：**MaxDigits = 15**，超出忽略按键。
- 评估：单文件 372 行把所有交互逻辑集中，紧凑但耦合高；错误处理统一为"除零 → 中文文案 + 其他非法输入静默忽略"，缺少对溢出（inf/NaN）的显式防线。

### 2.4 格式化策略（D4）

- `Formatting::format(double)`：
  - 0 → "0"。
  - `|v| ≤ 1e15` 且为整数 → `'f' 0`（去掉 ".0"）。
  - 否则 `QString::number(v, 'g', 12)`（**12 位有效数字**），含 `e` 则原样保留科学计数；否则去尾零、去尾点。
- 验证用例：`0.1+0.2` → "0.3"；`1÷3` → "0.333333333333"；`999999999999+1` → "1000000000000"；`0.0000001` → "1e-07"。
- 无非有限值（±inf/NaN）拦截——除零已在引擎拦截，但纯数值溢出（如超大数相乘）无显式处理，依赖 15 位输入上限兜底。

### 2.5 UI 设计与交互（D5）

- 主窗口 `QMainWindow`：
  - 主显示：只读 `QLineEdit`（右对齐、28px 大字号）。
  - **表达式次显示：`QLabel`（右对齐、灰字），实时显示构建中表达式**（如 "2 + 3 × 4"），这是 basic 版亮点。
  - `QGridLayout` 5 列按键，`=` 跨 3 列并高亮（accent 蓝色），清除键红色系；按钮通过 `property("role")` 分区着色（op/clear/accent），纯 QSS 扁平化样式。
  - 固定窗口 360×420，禁止缩放。
- **完整键盘支持**：`keyPressEvent` 处理 Enter/Backspace/Esc，`handleKey` 映射数字、`.`、`+-*/`（`*`→×、`/`→÷）、`×÷` 原字符、`%`、`(`、`)`。
- 双清空键：`AC`=全清、`C`=清当前输入（Clear Entry）、`⌫`=退格。
- 评估：视觉打磨与键盘体验是两版中更好的；但所有 UI 代码（含样式字符串）都堆在 `MainWindow.cpp` 206 行中，与引擎直接耦合，UI 变更会影响测试稳定性（测试靠 `findChild` 按按钮文本查找，无稳定 objectName）。

### 2.6 测试策略（D6）

- 两个测试可执行文件：
  - `tst_calcengine`：10 个测试槽（基本四则 / 优先级 / 连续运算 / 小数 / 括号 / 百分号 / 正负号 / 错误处理 / 格式化 / 表达式文本），用紧凑 `run("2+3×4=")` 字符串编码驱动。
  - `tst_gui`：3 个测试槽（键盘输入 / 按钮点击 / 清空按钮），`QTEST_MAIN` + `qWaitForWindowExposed` 需真实窗口平台，非 offscreen。
- 覆盖定位：**引擎逻辑层为主，GUI 仅冒烟**（3 个用例）；无控制器中间层测试、无 BDD 编号溯源、无 offscreen 平台化运行。
- 风险：`tst_gui` 依赖真实桌面，CI/无头环境不可跑。

### 2.7 构建与打包（D7）

- 根 `CMakeLists.txt`：单 `add_executable(qtcalc)`，`WIN32_EXECUTABLE TRUE`，链接 `Qt6::Widgets`；`tests/CMakeLists.txt` 重复 `find_package` 并内联源文件。
- 打包：`deploy/` 目录含 windeployqt 全套 DLL（Qt6Core/Gui/Widgets/Network、platforms、styles、translations 等），`qtcalc.exe` 已生成。
- **遗留问题**：`progress/progress.txt` 记录了一次运行时报错——`由于找不到 libgcc_s_seh-1.dll, 无法继续执行代码`（当时 deploy 目录缺 MinGW 运行库）。当前 deploy 目录已含该 DLL，说明问题已修复；但无冒烟验证记录，无证据证明"无 Qt 环境下可运行"。

### 2.8 工程治理与文档（D8）

- 文档：`DESIGN.md`（195 行）质量不错——含架构分层、输入模型、内部状态、核心算法、错误处理、行为示例表、P1–P8 分阶段计划与手动验收清单。**有设计文档但无流程落地痕迹**（无阶段产出、无验收记录、无复盘）。
- 版本治理：无 git、无 CHANGELOG、无版本文件，仅 CMake 里的 0.1.0。
- 遗留：`build-release/qtcalc.exe` 仅 148KB（release 精简）与 `build/qtcalc.exe` 2.8MB（debug）并存，无明确交付说明。

### 2.9 项目 A 小结

**优点**：代码量小、直观；表达式次显示 + 键盘输入体验好；除零有具体中文文案；15 位输入上限避免展示失控；DESIGN.md 有完整设计文档。

**不足**：无显式状态机（逻辑散落）；无溢出防护；测试只有 13 个用例且 GUI 测试不可无头运行；无共享库（测试内联源码）；无 git/版本/CHANGELOG；打包曾出现缺 DLL 运行错误且无冒烟证据。

---

## 3. 项目 B：qtcalc 详细分析

### 3.1 项目概况（D1）

- 目标：同款 Windows 桌面简单计算器（四则 + 连续 + 小数 + 括号 + 百分号 + 正负号；**明确不含键盘输入**），windeployqt 打包独立 exe。
- 版本：CMake `project(qt_calculator VERSION 1.0.0)`；`version.txt` = 0.1.0；git tag `v0.1.0`。**CMake 版本 1.0.0 与发布版本 0.1.0 不一致**（小瑕疵）。
- 技术栈：C++17 + Qt 6.8.3 Widgets + QtTest，CMake + Ninja + MinGW（CMAKE_PREFIX_PATH 硬编码默认 `D:/Qt/6.8.3/mingw_64`）。
- 代码规模（含头文件）：
  - 源码：`calceval.cpp` 226 + `calcformat.cpp` 35 + `calccontroller.cpp` 459 + `mainwindow.cpp` 64 + `main.cpp` 9（+ 头文件 84）≈ 877 行。
  - 测试：`tst_engine.cpp` 133 + `tst_controller.cpp` 292 + `tst_ui_e2e.cpp` 363 ≈ 788 行。
- 目录：`src/core/`、`src/ui/`、`tests/`、`dist/`、`agate-workspace/`、`docs/`、`.opencode/`、`CHANGELOG.md`、`version.txt`、`.git/`。

### 3.2 架构设计（D2）

- 四层架构，依赖方向 `core ← controller ← ui ← main`：
  - `core/calceval`：纯函数 `calc::eval(QString) → EvalResult`（解析 + 求值）。
  - `core/calcformat`：纯函数 `calc::format(double) → QString`。
  - `ui/calccontroller`：**仅依赖 QtCore** 的交互状态机（`QObject` + `press(token)` + `displayChanged` 信号）。
  - `ui/mainwindow`：QWidget 界面，只做按钮→token 绑定与显示。
- **共享静态库 `calc_core`**：`add_library(calc_core STATIC ...)`，app 与三个测试统一链接，无源码复制。
- **字符集契约（P2-design 固化）**：引擎/控制器内部统一 ASCII `0-9 . + - * / ( ) %`；UI 层负责渲染 `− × ÷`，按钮→token 由一张映射表对齐，消除二义。
- 评估：职责边界清晰，每一层都可独立单测（P2 设计文档明确把"逻辑可脱离界面验证"作为架构决策依据）。

### 3.3 计算引擎设计（D3）

- 求值模型：**表达式字符串累积 + "=" 时全量求值**。控制器把按键拼成规范中缀表达式，`=` 时交给 `calc::eval` 一次解析求值。
- `eval` 实现：tokenizer（只认 ASCII，数字含单一小数点、后缀 `%`、一元负号）+ **递归下降（优先级爬升）**：`expression → term {(+|-) term}`、`term → factor {(*|/) factor}`、`factor → ( expression ) | unary | number [%]`。无状态纯函数，同输入必同输出。
- 错误模型：`enum EvalError { None, DivideByZero, EmptyParens, Malformed, Overflow }`，UI 层统一显示"错误"。**含溢出防护**（`std::isfinite` 检查，超大数相乘 → Overflow）。
- 控制器状态机：显式 6 态 `START / NUMBER / OP / PCT / RESULT / ERROR`，每种状态一个 handler（`handleStart/handleNumber/...`），状态迁移表写进设计文档。
- 语义细节（比 basic 更完备）：
  - **重复等号**：`2+3=` 后按 `=` → 8（`lastOp`/`lastOperand` 重放，BDD-16）。
  - **操作符覆盖**：`2+*3=` → 6（后者覆盖前者，BDD-14）。
  - **未闭合括号自动补全**（`2+3=` → 5，BDD-22）；**空括号报错**（`()` → "错误"）。
  - **PCT 态**：`200*10%` 时实时显示 `0.1`，`=` 得 20；CE 可删除尾部 `%` 回到原操作数。
  - ERROR 态**仅 C 可恢复**，其余按键忽略。
- 百分号：后缀 `%` token 作用于紧邻单个操作数 ×0.01（引擎唯一机制）；**OP 态按 `%` 被忽略**（`50+%` 无效果，与 basic 的 `50+%=50.5` 语义不同）。
- 无输入位数上限（有 400 位超长串不崩溃的契约测试）。

### 3.4 格式化策略（D4）

- `calc::format(double)`：
  - 非有限值 → `'g' 15` 直接输出（引擎侧已拦截，防御性兜底）。
  - 0 → "0"；`|v| < 1e-12` → "0"（极小值归零）。
  - 主格式 `QString::number(v, 'g', 15)`（**15 位有效数字**，精度高于 basic 的 12）。
  - 科学计数规范化：`1e+22` → `1e22`（去 `+`）；去尾零、去尾点；`-0` → "0"。
- 取舍明确写入设计文档：`0.000000000001×0.1=1e-13` 会被归零显示，属可接受启发式，且被单测固化（`contract_format_boundaries`）。

### 3.5 UI 设计与交互（D5）

- 主窗口 `QWidget`（非 QMainWindow）：
  - 显示区：`QLabel`（objectName=`displayLabel`，右对齐，24pt）——**只有主显示，无表达式次显示**。
  - `QGridLayout` 4 列按钮，按钮统一 `objectName = btn_<key>` 约定（`btn_5/btn_plus/btn_mul/btn_equals/btn_clear/btn_backspace/btn_lparen/...`），这是 e2e 定位的稳定锚点。
  - 按钮文字渲染 Unicode（`− × ÷`），token 传 ASCII（`- * /`）。
  - 无 QSS（系统默认样式）；无固定窗口尺寸。
- **无键盘输入**（P2 明确排除，功能范围已确认不可变更）。
- 双清空键：`C`=全清、`CE`=退格（Backspace）。
- 评估：UI 朴素但稳定可测（objectName 契约），是"为可测试性让渡视觉打磨"的设计取向。

### 3.6 测试策略（D6）

- 三个测试可执行文件，统一链接 `calc_core`：
  - `tst_engine`：BDD-6..12/20/23-25/28-30 + 契约测试（溢出不崩溃、格式化边界），用 `expectEval/expectError` 断言容差。
  - `tst_controller`：BDD-1..28 + 契约测试，用 `displayChanged` 信号日志（`m_displayLog`）断言——**信号级行为验证**。
  - `tst_ui_e2e`：BDD-1..30，**offscreen 平台**构造 MainWindow，按 objectName 用 `QTest::mouseClick` 模拟点击 → 断言 displayLabel。
- **全部 BDD 编号溯源**（BDD-1..31 映射到模块/机制，写进 P2-design §3.6）。
- 数量口径：复盘报告记录 **84/84 全绿（引擎 18 / 控制器 34 / UI e2e 32）**，含 P6 验收 22 张截图 + vision 报告。
- 运行平台：e2e 固定 `QT_QPA_PLATFORM=offscreen`，无头可跑（CI 友好）。

### 3.7 构建与打包（D7）

- 根 CMake：`calc_core` 静态库 + `qt_calculator` 主程序 + 3 个测试目标；测试注册名含固定 `ui_e2e`（与 gate 命令 `-R ui_e2e` 契约）。
- 打包：`dist/` 完整（18 个文件：8 顶层 DLL + 8 插件），offscreen 冒烟通过，`qt_calculator.exe` 可独立启动。
- 无 basic 的缺 DLL 问题——打包验证流程在 P8 复盘报告中明确为"独立目录 + PATH 不含 Qt bin 冒烟"。

### 3.8 工程治理与文档（D8）

- **git + 10 次按阶段提交**（P1→P8/READY/DONE），tag `v0.1.0`；`.gitignore` 精细（`build/ dist/ .opencode/`，并白名单 `!version.txt`）。
- `CHANGELOG.md` 遵循 Keep a Changelog；`version.txt` 独立维护。
- `agate-workspace/` 完整流程产物：P0-brief、P1-requirements（31 BDD）、P2-design（349 行，接口契约 + 状态迁移表 + 字符集契约 + BDD 覆盖映射 + gate_commands）、P3 测试设计、P4 实现、P5 验证、P6 验收（22 截图 + vision 报告）、P7 一致性、P8 发布、以及 238 行全流程复盘报告。
- 复盘报告暴露并处置 9 类问题（Q1..Q9）：Windows 路径/GATE/编码适配、state.phase 与 commit gate 联动冲突、P3 测试缺陷后移、短命 subagent 会话重试、视觉验收无多模态能力等，并提出 R1..R12 改进措施。**流程可复现性、证据留存（git log / gate 历史 / session 记录）是其最大工程优势**。
- 已知小瑕疵：CMake 版本 1.0.0 与 version.txt 0.1.0 不一致；`docs/` 目录基本为空（文档主体在 agate-workspace）。

### 3.9 项目 B 小结

**优点**：四层架构 + 共享库，分层可测；显式状态机 + 递归下降解析，语义完备（重复等号、操作符覆盖、溢出防护、自动补括号）；BDD 驱动 84 用例三层覆盖、offscreen 可无头运行；完整 git/CHANGELOG/版本治理与全流程复盘；打包验证有冒烟证据。

**不足**：无键盘输入、无表达式次显示（UX 弱于 basic）；CMake 版本号与发布版本不一致；UI 无 QSS 样式打磨；源码（尤其 calccontroller 459 行）状态分支较多，对新手可读性一般。

---

## 4. 逐维度对比总表

| 维度 | qtcalc-basic (A) | qtcalc (B) | 评价 |
|------|------------------|-----------|------|
| 架构分层 | 2 层（Engine → MainWindow） | 4 层（core → controller → ui → main） | **B 优**：B 中间控制器层可独立单测；A 的引擎与 UI 直接耦合 |
| 求值模型 | 流式 shunting-yard 即时求值 | 表达式累积 + "=" 递归下降全量求值 | 各有取舍：A 响应即时；B 语义完备、纯函数易测 |
| 状态管理 | 隐式标志（entry/ready/awaiting） | 显式 6 态状态机（START…ERROR） | **B 优**：A 状态散落，易漏边界 |
| 内部字符集 | Unicode × ÷ 贯穿引擎 | ASCII * / - + 契约 + UI 渲染映射 | **B 优**：契约化，消除二义 |
| 除零处理 | 中文文案"除数为零" | EvalError::DivideByZero → "错误" | A 文案更友好；B 错误模型更统一 |
| 溢出防护 | 无显式防护（靠 15 位上限） | `std::isfinite` → Overflow | **B 优** |
| 输入上限 | MaxDigits=15 | 无上限（契约测 400 位不崩） | A 防展示失控；B 防溢出更强 |
| 重复等号 | 不支持 | 支持（lastOp 重放） | **B 优** |
| 操作符覆盖 | 覆盖型（m_awaiting 替换） | 覆盖型（BDD-14） | 两者一致 |
| 百分号语义 | `50+%` 可用 → 50.5；作用于 ready 值 | OP 态 % 忽略；后缀 % 仅作用操作数 | 语义不同，B 更严格自洽 |
| 空括号/未闭合 | 静默忽略按键 | 空括号报错、未闭合自动补全 | **B 优**（行为明确且有测试） |
| 格式化精度 | 'g' 12 + 整数 'f' 0 | 'g' 15 + 极小值归零 + 科学计数规范化 | **B 优**（15 位精度 + 边界更全） |
| 表达式次显示 | 有（QLabel 实时表达式） | 无（仅主显示） | **A 优** |
| 键盘输入 | 完整支持 | 不支持（设计排除） | **A 优** |
| UI 样式 | QSS 扁平化 + role 分区着色 | 系统默认样式 | **A 优** |
| UI 稳定标识 | 按按钮文本 findChild | objectName 契约（btn_*） | **B 优**（测试更稳） |
| 测试规模 | 13 用例（引擎 10 + GUI 3） | 84 用例（引擎/控制器/UI e2e） | **B 优**（数量 + 分层 + BDD 溯源） |
| GUI 测试平台 | 真实窗口（不可无头） | offscreen（可无头/CI） | **B 优** |
| 共享库 | 无（测试内联源码） | calc_core 静态库 | **B 优** |
| 打包验证 | 曾缺 libgcc DLL，现目录含齐，无冒烟记录 | dist/ 完整 + offscreen 冒烟通过 | **B 优** |
| git/版本治理 | 无 git、无 CHANGELOG | git 10 提交 + tag v0.1.0 + CHANGELOG + version.txt | **B 优** |
| 流程/复盘 | 仅 DESIGN.md（无落地痕迹） | agate P0-P8 全流程 + 238 行复盘 + R1-R12 | **B 优** |
| 代码规模 | 源码 ≈678 行 / 测试 ≈221 行 | 源码 ≈877 行 / 测试 ≈788 行 | B 测试代码量更大，源码更完备 |
| 已知瑕疵 | 缺 DLL 历史错误、无 git | CMake 1.0.0 ≠ 发布 0.1.0、docs/ 空 | 均为小瑕疵 |

**对比结论**：D2/D3/D4/D6/D7/D8 六个维度 B 占优；D5 上 A 在"表达式次显示、键盘输入、视觉样式"三点占优；D1 两者功能范围基本等价。

---

## 5. 关键行为差异明细

| 场景 | qtcalc-basic (A) | qtcalc (B) |
|------|------------------|-----------|
| `10+5= ×2=` | 30（结果作为左操作数） | 30（RESULT 态结果复用 BDD-15） |
| `2+3=` 后按 `=` | 维持 15，无重放 | 8（重复上次运算 BDD-16） |
| `50+10%` / `50+%` | 50.1 / 50.5（% 作用于就绪值） | 50.1；`50+%` 的 `%` 被忽略 |
| `200×10%` | 20 | 20（PCT 态实时显示 0.1） |
| `()` 按 `=` | 忽略按键（显示 0） | "错误"（EmptyParens） |
| `2+(` 按 `=` | 忽略按键（显示 2） | 自动补 `)` → `2+()` → "错误" |
| `5÷0` | "除数为零"，C/AC 可恢复 | "错误"，仅 C 可恢复 |
| 清除键映射 | AC=全清 / C=清输入 / ⌫=退格 | C=全清 / CE=退格（无"清输入"键） |
| 键盘 | 数字/`.`/`+-*/`/`×÷`/Enter/Backspace/Esc/%/() | 不支持 |
| 表达式显示 | 有次显示（"2 + 3 × 4"） | 仅主显示当前值/结果 |

> 说明：以上均来自双方测试用例与源码实际行为，非推测。

---

## 6. 各维度结论与改进建议

### 6.1 若以 qtcalc（B）为主体吸收 A 的优点

1. **加入键盘输入**：B 的 controller 已是 `press(token)` 单入口，键盘只需在 MainWindow 层把 key 事件映射为 token 即可，改动小收益大。
2. **增加表达式次显示**：B 的 controller 内部已持有 `m_expr` 字符串，只需新增 `expressionChanged` 信号或 `expression()` 查询 + 一个 QLabel，即可获得 A 的实时表达式反馈。
3. **统一错误文案**：可保留 B 的 `EvalError` 枚举，但 UI 层按错误类型映射中文文案（如 `DivideByZero` → "除数为零"），兼得 B 的模型与 A 的友好度。

### 6.2 若以 qtcalc-basic（A）为主体吸收 B 的优点

1. **引入显式状态机 + 纯函数求值**：A 的引擎可拆为 `core`（流式求值保留即时性）与 `controller`（状态机）两层，恢复可测性。
2. **补测试**：至少补到"引擎边界（溢出/空括号/未闭合）+ 控制器信号级 + offscreen GUI e2e"三层，并把 GUI 测试改为 offscreen 平台。
3. **共享库化**：把引擎编成静态库，测试不再内联源码。
4. **建立 git + CHANGELOG + 版本文件**，并补打包冒烟验证（无 Qt 环境启动）。

### 6.3 共性建议

- 两版 CMake 都建议显式 `CMAKE_AUTOMOC ON`（B 已设，A 未设，A 靠内联 .moc 编译）。
- 版本号单一来源：CMake `project()` 版本、`version.txt`、CHANGELOG、tag 四者应一致（B 的 CMake 1.0.0 vs 0.1.0 需修正）。
- 键盘映射表与按钮→token 映射表应各自文档化（B 已固化，A 依赖代码内约定）。

---

## 7. 总结

两项目目标与功能高度一致，代表"**快速实现**"与"**工程化交付**"两条路线：

- **qtcalc-basic**：约 900 行、2 层架构、13 个测试，代码直观、UX（键盘 + 表达式次显示 + 样式）更好，但无版本治理、测试单薄、打包曾出过缺 DLL 运行错误。适合作为"学习/原型"参考。
- **qtcalc**：约 1665 行、4 层架构 + 共享库、84 个 BDD 用例三层覆盖、offscreen 可无头运行，git/CHANGELOG/复盘完整，打包有冒烟证据。工程成熟度高，适合作为"可维护交付物"基准。

**最终建议**：以 qtcalc 的架构与工程治理为骨架，回填 qtcalc-basic 的键盘输入、表达式次显示与友好错误文案，即可得到功能与质量兼备的版本。
