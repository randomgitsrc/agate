---
phase: P2
task_id: TAG0028
type: review
parent: P2-design.md
trace_id: TAG0028-P2-20260903
status: approved
created: '2026-09-03'
agent: plan-eng-review
---

# P2 工程评审 — TAG0028 subagent 存活可观测性与受控自主再派发（RM-AG0055）

> 阶段：P2（方案设计评审）· 角色：plan-eng-review（工程经理独立评审）· 日期：2026-09-03
> 评审对象：P2-design.md（260 行，candidate_count=3，trace_id=TAG0028-P2-20260903）
> 核对输入：P1-requirements.md（33 条 BDD + I-1~15 + S-1~8）/ P0-brief.md（scope/out-of-scope/known_risks）/
> 设计文档 v5（§3/§4）/ 验证记录 verification-cmdstream-datasource-20260903.md /
> verify_cmdstream_detection.py（9 场景锚）/ dispatch-context（11 条派发约束）

## 评审范围与方法

本评审对 P2-design.md 做独立工程评审，覆盖：数据流清晰度、状态机完整性、接口契约明确性、
错误边界、测试策略、技术债、多方案探索（候选数/权衡客观性/选择理由自洽性）、实现就绪度
（files_to_read 覆盖）、P2 最小验证（minimal_validation），并逐条核对 dispatch-context 的
11 条派发约束。评审过程实读核对设计引用的客观证据锚点：check-p6-provenance.py:85-93（`_find_files`
隐藏文件过滤，实读确认 `if name.startswith("."): continue`）、check-maintainability.py:88-148
（`_load_config` 全兜底：文件缺失/yaml 损坏/键缺失/类型坏均回默认值）、check-protocol-consistency.py:947-949
（CHECK 10 `iterdir()` 顶层文件枚举，实读确认 scripts 顶层检测面）、maintainability.yaml（9 行，
god_file_threshold=1000）、dispatch-protocol.md:944-951（Subagent 安全节 951 行存活检查现状）、
dispatch-context.md 模板（56 行，dispatch_guide 骨架）、protocol-tests.yml:179-215（shellcheck
`-S warning` 3 薄壳，与 P5_shellcheck 同口径）、verify_cmdstream_detection.py EXPECTED 字典
（9 场景 NORMAL/FROZEN/SPIN 期望值）。

## 架构问题（阻塞级）

无。

以下候选阻塞疑点经核查后**不成立**，结论记录备查：

- 疑点：B 方案 god-file 风险是否被夸大（A 宣称 3 脚本每文件 <500 行、B 宣称 800-1200 行）。
  核查：maintainability.yaml `god_file_threshold: 1000`（实读确认），三平台适配器（Claude JSONL +
  OpenCode SQLite + DSH zstd 解压）+ IR + 检测引擎 + CLI 聚合单文件预估 800-1200 行会触发 P4 gate
  红灯，B 的缺点描述客观成立；A 的 <500 行/文件预估与三脚本职责切分（IR/适配器/检测+CLI）匹配，
  两案行数口径无矛盾，不构成夸大。
- 疑点：C 方案是否稻草人（仅用于衬托 A）。核查：C 对应 P0-brief scope 原文「适配器注册机制
  （配置声明或目录扫描 adapters/*.py）」的第二选项，且有独立客观缺点（CHECK 10 顶层枚举盲区、
  隐式注册容错、pytest 子包 import 处理）——非稻草人，构成真替代。
- 疑点：R10（OpenCode 数据源）是否与 P1 BDD-3 冲突。核查：architect dispatch-context:359 写
  `storage/session/<id>/info.json + messages.json`（grep 实命中），验证记录 line 28 写单一 SQLite
  库 `opencode.db`（实读确认）；P1 BDD-3 已锚定「opencode 会话 SQLite 库（fixture 含 part.data.state
  结构）」。设计 R10 以验证记录为准并标注差异来源，与 P1 一致，无冲突。

## 架构问题（非阻塞）

- [N1] verdict 顶层枚举与 BDD 输出类别名映射未完全钉死。P2-design §3.2 声明 `verdict ∈ {FROZEN,
  SPIN, NORMAL}`，但 P1 BDD-11/12 的输出类别名是 `ACTIVITY_FROZEN`（alert/suspect 两级），
  verify 脚本 EXPECTED 中活动冻结场景（I_活动冻结_进程级卡死）顶层期望为 FROZEN。即：活动冻结在
  顶层 verdict 是 FROZEN 的子类别，还是独立类别 ACTIVITY_FROZEN，设计未显式给出「顶层三值 +
  输出细分类别（调用冻结/活动冻结）」的映射声明。建议：P3 测试设计/P4 实现时明确 detect() 返回
  契约（顶层 verdict 三值 + reasons/细分类别字段承载「调用冻结/活动冻结」标注），并在单测断言
  同时锁定两类冻结的类别名，避免 P6 对照 BDD-11/12 验收时类别名对不上。位置：P2-design.md §3.2、
  P1-requirements.md BDD-11/12、verify_cmdstream_detection.py:313-323。
- [N2] DSH 适配器的 zstd 解压测试依赖未明示。M9 声明「适配器解析（三平台 fixture → CommandRecord
  断言）」，但 DSH 解压实现是 spawn node 单行脚本（M2/R2），单测是 mock node 子进程、还是依赖
  真实 node 环境（验证记录已确认 node v24.15.0 可用）、无 node 时是否 skip——设计未声明。
  建议：P3 测试设计明确 DSH 适配器单测的 node 依赖策略（mock subprocess 为主 + 真实 node 冒烟
  可选），避免 CI 环境无 node 时用例失败或测试形同虚设。位置：P2-design.md §3.1/M9、P1 BDD-4。
- [N3] files_to_read 未显式含 P1-requirements.md。files_to_read 11 项覆盖实现所需上下文
  （_load_config 参照、provenance 过滤、archive 清理、protocol 改写、role-system、模板、验证记录、
  verify 脚本、conftest、maintainability.yaml），但 BDD 验收锚（P1-requirements.md 33 条）未列入。
  实现依赖 BDD 语义（M1-M10 已内联关联 BDD 编号，但全文细节在 P1 文件）。建议：P4 派发时
  dispatch-context 上游关联显式带上 P1-requirements.md（或 files_to_read 补一行），防止
  implementer 上下文缺 BDD 全文。位置：P2-design.md §5。
- [N4] P5_cmdstream_verify 命令的 cwd 依赖未声明。gate_commands 用相对路径
  `python3 docs/design-notes/.../verify_cmdstream_detection.py`，执行方须以 worktree 根为 cwd。
  既有 gate 惯例如此（P5_consistency 同），非缺陷，仅提示主 Agent P5 执行时确认 cwd。位置：
  P2-design.md §4。

## 测试缺口

- BDD-33（不破坏 gate 返回约定）的回归验证方式未落 gate_commands。BDD-33 要求「check-gate.py /
  check-state-transition.py 对既有任务判定 exit 三态与落地前一致」，但 gate_commands 无对应 key，
  也未在 M9 单测列表明示（M9 覆盖再派发边界测试，未提 gate 返回约定回归）。建议：P5 验证阶段对
  至少一个既有任务跑 check-gate.py 三态回归（人工步骤或 P5 命令），或将 BDD-33 的验证方法写进
  P3 测试设计。位置：P2-design.md §4 gate_commands、P1 BDD-33。
- verify 9 场景锚（BDD-22）在 P5_cmdstream_verify 固化，但检测引擎单测「复刻 9 场景断言」的
  判定输入构造方式未明示（直接构造 CommandRecord 列表 vs 复用 verify 的场景文本格式）。建议 P3
  明确复刻方式，防止单测与 verify 脚本判据漂移（R3 缓解已覆盖数值对齐，输入格式对齐补一句即可）。
  位置：P2-design.md §3.2/M9、R3。

## 锁定决策（本次评审确认的技术方向）

1. **候选方案 A（平铺脚本族 + 显式注册表）锁定**：`agate-cmdstream-ir.py`（IR+字段契约）/
   `agate-cmdstream-adapters.py`（基类+三平台适配器+显式注册表 `ADAPTERS`）/
   `agate-cmdstream-detect.py`（检测引擎+CLI 子命令）平铺 `agate/scripts/`，符合既有惯例，
   CHECK 10 检测面内，god-file 可控，BDD-6 由「适配器契约 + 注册表一行」满足。
2. **检测阈值数值锁定**（与 verify 脚本同源）：调用冻结 expected×2（下限 30s）/ 兜底 alert=300 /
   suspect=900；活动冻结 alert=60 / suspect=300；无效重复窗口 10 内同签名 ≥5 → SPIN；
   REPEAT_UNIQUE_MIN=3 信息级；truncated 不参与哈希比对仍参与冻结检测；阈值从 maintainability.yaml
   `cmdstream_detection:` 节读取，缺失/损坏兜底默认值不报错（复用 `_load_config` 全兜底模式）。
3. **检测定位「证据 + 触发核查，不自动判死」锁定**：输出 = 判定类别 + 原因 + 阈值依据 + 建议动作
   方向，平台无关（BDD-23/24）；FROZEN/SPIN 信号不携带自动终止/中止指令。
4. **verify_cmdstream_detection.py 9 场景锚不改（N7）**：P5 gate 直接运行判 9 场景全 PASS（exit 0），
   检测引擎以其判据为参考实现，阈值常量对齐（R3）。
5. **两套信号分工锁定**：命令流日志承担「存活/卡死」判定职责，progress.md 保留「语义进展」职责；
   check-gate.py / check-state-transition.py 返回约定不动（N1/BDD-33）；dispatch-protocol.md:951
   存活检查节为改写对象（实读确认现状措辞）。
6. **心跳文件生命周期锁定**：命名 `${TASK_DIR}/.heartbeat` + `.heartbeat.child-{n}`（父任务内
   不重复）；审计豁免 = check-p6-provenance.py `_find_files` 隐藏文件过滤（实读确认天然跳过）+
   显式登记确认（M8）；清理 = 产生方清理 + 派发前置检查清空遗留（复用 agate-archive-stale-outputs
   收尾模式，不新建机制）。
7. **DSH zstd 解压隔离锁定**：解压隔离在 dsh 适配器内部（spawn node `zlib.zstdDecompress`，
   minimal_validation 引用验证记录实机验证 confirmed，node v24.15.0），检测引擎零平台细节
   （BDD-4）。
8. **受控自主再派发边界锁定**：执行角色（analyst/architect/implementer/verifier）可被授予子派发
   权限；两条硬边界（子任务不写 .state.yaml/active-tasks.md、写权限严格子集 + prompt 显式重申）；
   judge 类角色例外（不开放 Agent/subagent_fork，信息隔离冲突论证成立）；dispatch-context 模板补
   「不启用子派发能力」声明位；子任务中间产出不计 gate 判定、files_modified 走 D2 假完成校验。
9. **OpenCode 数据源以验证记录为准**（单一 SQLite `opencode.db`，part.data.state 结构），差异来源
   已标注（architect dispatch-context:359 旧描述 vs 验证记录 line 28），OpenCodeAdapter 只依赖
   验证记录确认字段（state.time/start+end、state.input.command、state.metadata.exit/truncated）。
10. **gate_commands 11 项逐 key 独立锁定**（无 && 拼接）：P3 pytest / P5 pytest -q --tb=no /
    P5_consistency（worktree 自己的 check-protocol-consistency.py --strict-errors-only）/
    P5_cmdstream_verify（9 场景锚）/ P5_shellcheck（-S warning 3 薄壳，与 CI 同口径）/
    P5_count_tests + 5 个 timeout_seconds（P5=300 混合档、其余 120 单测档）。
11. **SELF-GATE 面覆盖锁定**：改 agate/scripts/* + agate/*.md → commit 须含 `self-gate-review:`；
    P5_consistency 0 ERROR；P8 走 protocol-alignment-review（R9）。
12. **范围锁定确认**：未超出 P0-brief out-of-scope——DSH 心跳钩子机制不实现（N10）、OpenCode CLI
    子进程路线不封装（N10）、check-gate.py/check-state-transition.py 返回约定不改（N1）、五模式
    编排与状态机单层不变（BDD-32）。

## 关键核对结果

- 影响面梳理三部分（改 M1-M10 / 不改 N1-N10 / 风险 R1-R10）齐全且动作有客观证据（本评审实读
  确认 check-p6-provenance.py、check-maintainability.py、check-protocol-consistency.py、
  maintainability.yaml、protocol-tests.yml 等锚点，与设计引用一致）。
- 候选方案 3 个均为真替代，权衡表 6 维度客观（现状一致/检测面/god-file/扩展路径/可测试性/
  工作量），选择理由 4 条自洽（不扩范围/gate 兼容/BDD-6 语义/平台无关）。
- minimal_validation 合格：方案依赖的外部行为（DSH JSONL.zstd 解压）引用验证记录实机验证结论
  （confirmed，无需重验 + P4 复验命令），其余纯代码逻辑显式声明且由 M9 pytest 承载。
- dispatch-context 约束 1-11 逐条核对通过（详见锁定决策与各节）；无行首 PASS/FAIL 预判格式。
- 本评审未提出「后续应重构/架构债」类结论，故不产出 DEBT 条目（角色定义允许不产出）。

## 环境隔离声明

[PROD_NOT_TOUCHED] 本评审仅读取任务目录、协议本体（worktree）、设计文档与验证记录，未触碰任何
生产环境，未读取其他用户 DSH 会话内容。
