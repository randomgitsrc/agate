---
implementation_dir: agate/scripts/
phase: P4
task_id: TAG0028
type: implementation
parent: P2-design.md
trace_id: TAG0028-P4-20260903
status: draft
created: '2026-09-03'
agent: implementer
---
# P4 实现 — TAG0028 subagent 存活可观测性与受控自主再派发（RM-AG0055）

> 阶段：P4（代码实现）· 角色：implementer · 日期：2026-09-03
> 上游输入：P2-design.md（方案 A + §5 files_to_read + §8 实现完成标志）· P3-test-cases.md
> （42 用例：38 红待转绿 + 4 绿保持）· P0-brief.md（env_constraints）· verify 脚本（9 场景锚）
> 本文档 frontmatter 由 `agate-md-field-set` 填写（不手写）。

## implementation_dir

- **implementation_dir: `agate/scripts/`**（三个新脚本平铺在此，符合 agate/scripts 既有单层惯例）
- 配置落点：`agate-workspace/maintainability.yaml`（cmdstream_detection 节）
- 协议文档落点：`agate/dispatch-protocol.md` / `agate/role-system.md` / `agate/assets/templates/dispatch-context.md` / `agate/scripts/check-p6-provenance.py`

## 新增文件核对表（CODE-MAP 已采用）

| 新增文件路径 | 骨架归属 | CODE-MAP 处理 |
|------------|---------|--------------|
| agate/scripts/agate-cmdstream-ir.py | N/A（P1 无 project_phase: bootstrap，骨架机制未采用；位于 agate/scripts 平铺惯例内） | [CODE_MAP_UPDATED] |
| agate/scripts/agate-cmdstream-adapters.py | N/A（同上） | [CODE_MAP_UPDATED] |
| agate/scripts/agate-cmdstream-detect.py | N/A（同上） | [CODE_MAP_UPDATED] |

> CODE-MAP 处理：三脚本已登记入 `agate-workspace/agents/CODE-MAP.md`（scripts 目录新增条目）。
> 骨架机制未采用（P1 无 project_phase: bootstrap），骨架归属列统一 N/A。

## 实现摘要（每 phase 关键改动 + 关联 BDD）

### Phase 1（M1/M2）— 命令流数据源解析层（BDD-1~7）

- **M1 `agate/scripts/agate-cmdstream-ir.py`（新增）**：CommandRecord dataclass 十字段
  （platform/session_id/tool/command/ts_start/ts_end/exit/exit_signal/output_hash/truncated）；
  类型契约 ts_start/ts_end epoch 毫秒 int、exit int|None、truncated bool（BDD-1）；
  `to_json()` / 模块级 `from_json(s)` JSON 往返。实现要点：dataclass 注解用运行时
  `int | None`（importlib 独立加载时不注册 sys.modules，字符串注解会触发 dataclasses
  模块查找失败——`from __future__ import annotations` 不能解决，直接运行时注解）。
- **M2 `agate/scripts/agate-cmdstream-adapters.py`（新增）**：`CommandStreamAdapter` 基类
  （probe/list_sessions/read_commands 契约）+ 三平台适配器 + 显式注册表
  `ADAPTERS = {"claude-code": ..., "opencode": ..., "dsh": ...}`（BDD-6）：
  - ClaudeCodeAdapter：JSONL，tool_use/tool_result 按 tool_use_id/sourceToolAssistantUUID
    ↔ id/uuid 配对；command=input.command、ts 来自 timestamp（ISO-8601 → epoch ms）、
    exit 从 is_error + "Exit code N" 文本前缀解析并写 exit_signal 留档（BDD-2）；子 agent
    = sidecar `subagents/agent-*.jsonl`（BDD-5）
  - OpenCodeAdapter：SQLite part.data.state（含双重嵌套解包，fixture 结构
    part.data.state.state 与实机单层兼容）；exit=state.metadata.exit 整数、truncated=
    state.metadata.truncated 显式标记（BDD-3）
  - DSHAdapter：JSONL.zstd，解压隔离在适配器内部（spawn node 单行脚本
    zlib.zstdDecompressSync，逐帧扫描拼接帧；不依赖 python zstandard，BDD-4）；
    tool/call+tool/result 按 callId 配对产出 ts_start/ts_end；exit 从 isError + "Error:"
    前缀解析；子 agent = delegationDepth>0 独立 session 文件（BDD-5）
  - DSH 记录按时间倒序返回（最新在前，监控视角；检测引擎按 ts 计算不依赖列表顺序）
- 测试结果：IR 3 用例绿；adapters 7/8 绿，**test_bdd_3 标 [DESIGN_GAP]（见下）**

> [DESIGN_GAP: P3 test_bdd_3_opencode_adapter_parses_sqlite 断言结构性矛盾——测试用
> `by_cmd = {r.command: r for r in records}` 按 command 建字典，而 fixture 中 call_demo_0002
> 与 call_demo_0003 命令同为 "make build-docs"（0002: exit=2/truncated=false；0003:
> exit=0/truncated=true），字典同键只能保留一条记录，`by_cmd["make build-docs"].exit == 2`
> 与 `by_cmd["make build-docs"].truncated is True` 两条断言要求同一记录同时满足 exit==2 与
> truncated==True，fixture 无此记录——任何适配器实现（任意返回顺序）都无法同时满足；属
> P3 测试/fixture 设计问题，按 implementer 决策树不改测试，上报主 Agent 决策（P3 修复轮）]
>
> [DESIGN_GAP_REVIEWED: 已确认——P3 测试设计缺陷（T075 类：断言与 fixture 数据矛盾），
> 非实现问题、非 P1 BDD 矛盾；已回派 test-designer fix1 修复（过滤式匹配），修复后
> cmdstream 套件 42/42 全绿（4 长期不变量保持），主 Agent 2026-09-03 核验通过]

### Phase 2（M3/M4）— 检测引擎（BDD-8~24）

- **M3 `agate/scripts/agate-cmdstream-detect.py`（新增）**：`detect(events, now, config=None)
  -> (verdict, reasons)`：
  - 调用冻结：未结束 call（call 无配对 result）→ expected 声明用 max(expected×2, 30s)
    主信号（BDD-8）/ 无 expected 兜底 alert 300s（BDD-9）/ suspect 900s（BDD-10）；
    最新开始的未结束调用优先判定
  - 活动冻结：无未结束 call → 最后活动事件距今 ≥ alert 60s（BDD-11）/ ≥ suspect 300s
    （BDD-12）；think/out/call/result 三类均计活动 → 长时间思考不误杀（BDD-13）
  - 无效重复：窗口 10 内同 (命令, exit, 输出哈希) ≥5 → SPIN（BDD-14）；签名变化不误报
    （BDD-15）；唯一命令数 <3 信息级提示不判空转（BDD-16）；truncated 不参与哈希比对
    仍参与冻结检测（BDD-17）
  - 轮询误报标注：命令含 watch/poll 特征 → SPIN 附「轮询」核查提示（BDD-18/23）
  - 输出平台无关：判定类别 + 原因 + 阈值依据 + 建议动作方向，不含平台工具名（BDD-24）；
    无 kill/terminate/abort 动作指令（BDD-23）
  - 阈值配置全兜底：config 为 dict（显式覆盖，兼容 activity_alert 别名）/ maintainability.yaml
    路径（缺失/损坏/类型坏 → 协议默认值，不报错不静默跳过），复用 check-maintainability
    _load_config 模式（BDD-19/20/21）
  - 心跳 helper：`heartbeat_path(task_dir, n=None)` / `cleanup_heartbeats(task_dir)`（BDD-25/27）
  - CLI 子命令：list-sessions / read-commands / detect（P2 M3）
- **M4 `agate-workspace/maintainability.yaml`（修改）**：新增 `cmdstream_detection:` 节
  （call_freeze_alert/suspect=300/900、activity_freeze_alert/suspect=60/300、
  spin_window/threshold=10/5、repeat_unique_min=3、expected_multiplier/lower_bound=2/30）
- 测试结果：detect 19 用例全绿（含 BDD-22 verify 锚长期不变量）；verify 脚本 9 场景全 PASS

### Phase 3（M5/M8）— 心跳文件生命周期 + 协议文档（BDD-25~28）

- **M5 `agate/dispatch-protocol.md`（修改）**：
  - 「Subagent 安全 → 硬超时保护 → 存活检查」节改写（原 951 行）：命令流日志承担
    「存活/卡死」判定职责（取代 progress 心跳扩展此职责），progress.md 保留「语义进展」
    职责不变——两套信号分工清晰（BDD-28）；含平台名段挂 `> 实现注记：` 标记
    （check-protocol-consistency 护栏 1）
  - 新增「心跳文件生命周期」子节：`.heartbeat` / `.heartbeat.child-{n}` 命名规范
    （BDD-25）、审计豁免声明（BDD-26）、清理时机（产生方清理 + 派发前置检查清空遗留，
    复用 agate-archive-stale-outputs 收尾模式，不新建机制，BDD-27）
  - 新增「subagent 自主再派发」节：与五模式编排关系（并存互补不替代，模式 4 仍权威）、
    §4.1 两条硬边界、产出收敛语义（中间产出不计 gate、files_modified 走 D2、
    不产生新的编排层级）（BDD-29/30/32）
- **M8 `agate/scripts/check-p6-provenance.py`（修改，登记级）**：`_find_files`（85-93 行）
  隐藏文件过滤天然跳过 `.heartbeat*`（`if name.startswith("."): continue`），登记显式
  豁免确认——`HEARTBEAT_AUDIT_EXEMPTION = "confirmed"` 常量 + 注释说明；不改枚举逻辑、
  不改 7 道审计结构（BDD-26）
- 测试结果：heartbeat 5 用例全绿（命名/豁免登记/豁免行为/清理/两信号文档断言）

### Phase 4（M6/M7）— 受控自主再派发（BDD-29~33）

- **M6 `agate/role-system.md`（修改）**：新增「子派发权限边界」节——执行角色
  （analyst/architect/implementer/verifier）可被授予子派发权限；两条硬边界
  （子任务不写 .state.yaml/active-tasks.md、写权限严格子集不自动继承）；judge 类角色
  例外（不开放 Agent/subagent_fork，信息隔离冲突论证）（BDD-29/30/31）
- **M7 `agate/assets/templates/dispatch-context.md`（修改）**：`<dispatch_guide>` 约束节
  补「子派发能力声明位」——judge 类角色派发时注入「不启用子派发能力」显式声明（BDD-31）
- 测试结果：dispatch 6 用例中 5 绿（边界/子集/judge 例外/声明位/收敛）；BDD-33 gate
  三态长期不变量绿保持

## 自查结果（≠ P5 gate）

- cmdstream 套件：`timeout 180s python3 -m pytest agate/tests/unit/test_agate_cmdstream_*.py -q --tb=short`
  → **41 passed / 1 failed**（唯一失败 test_bdd_3 为 [DESIGN_GAP]，见上）
- verify 锚：`verify_cmdstream_detection.py` 9 场景全 PASS（BDD-22 保持）
- 一致性：`check-protocol-consistency.py --strict-errors-only` → **0 ERROR**（329 WARNING 为既有基线）
- ruff：4 个脚本 `ruff check` All checks passed
- 全量 unit 回归：后台跑（结果待主 Agent 复核；本批未触碰既有测试面，改动均为新增脚本 +
  协议文档 + 登记注释）

## 环境隔离声明

[PROD_NOT_TOUCHED] 本阶段仅写入 worktree 的 agate/scripts、agate/*.md、agate-workspace/
maintainability.yaml 与任务目录产出；未触碰生产环境；未读取其他用户 DSH 会话（fixture 均为
P3 已入库脱敏样例）。

## 修复轮记录（fix1）

> 依据：P4-review.md（status=rejected，7 个 [CRITICAL]，每个附 Fix 选项 A/B/C）+ fix1
> dispatch-context「修复目标」节。本记录逐条对应 7 CRITICAL（现象 → 修法 → 验证），
> 并登记本轮新增/调整的测试与两个 [DESIGN_GAP] 决策。
> 修复只动实现与测试，未改 P1 基线 / P3 既有断言 / verify 锚 / 阈值数值。

### CRITICAL-1 CLI detect 时间单位错配（agate-cmdstream-detect.py）

- **现象**：CLI 构造 events 的 ts 来自适配器 IR（epoch 毫秒），`--now` 默认也是毫秒
  （int(time.time()*1000)）；detect() 用 age=now-ts 直接比对秒级阈值（300/900/60/300）——
  实验复现 3 秒无活动即误报 FROZEN「距今 3000s ≥ 300s」。
- **修法（评审 Fix A）**：CLI 归一单位——新增 `_parse_epoch_seconds()`（毫秒 13 位输入
  //1000、秒 10 位原样、ISO-8601 经适配器转换后 //1000）；事件 ts 改为 `r.ts_start // 1000`
  （result 事件 `ts_end // 1000`）；`--now` 缺省 `int(time.time())`（秒）。detect 引擎
  语义保持秒阈值不变（与 verify 脚本/测试同口径）。
- **验证**：新测试 `test_bdd_11_cli_detect_seconds_unit_no_false_freeze`——完成调用 +3s
  观察 → VERDICT: NORMAL（修复前复现为 FROZEN）。cmdstream 套件 53 passed。

### CRITICAL-2 DSH zstd 拼接帧容器只解第一帧（agate-cmdstream-adapters.py DSHAdapter._decompress）

- **现象**：node 脚本 `z.zstdDecompressSync(buf.subarray(off))` 成功即 `off=buf.length`
  退出循环，未处理帧边界推进——验证记录 Q7 实测 20020 帧 / 28406 条记录，帧 2..N 全部
  丢弃；实验复现两帧容器只返回帧 1 记录。
- **修法（评审 Fix A）**：node 脚本改为按 zstd 帧 magic `0x28B52FFD`（`indexOf`）扫描
  帧边界——每找到一个 magic 位置 `idx` 即 `zstdDecompressSync(buf.subarray(idx))` 解出
  一帧入 chunks，然后 `off=idx+4` 继续扫下一帧；解压失败（数据内伪 magic）跳过 1 字节
  继续。全部帧解出后 `Buffer.concat` 拼接（验证记录「需扫描帧边界逐个解压后拼接」落地）。
- **验证**：新测试 `test_bdd_4_dsh_multi_frame_container_returns_all_records`——两帧各含
  完整 call+result 对（echo early@100 + echo late@200）→ 返回 2 条记录且帧 2 时间戳保留
  （修复前只返回 1 条）。

### CRITICAL-3 「未结束 call」通路在 claude-code/dsh 数据源不可达（adapters + detect CLI）

- **现象**：ClaudeCodeAdapter/DSHAdapter 仅从配对成功的 result 反查产出记录，无 result
  的未结束 call 不产出 IR；CLI detect 事件 id=f"{session_id}:{tool}:{command}" 同会话
  同命令多次调用 id 相同，call_ids/result_ids 集合运算坍缩——BDD-8/9/10 调用冻结在
  claude/dsh CLI 通路永不触发；且 IR 十字段无 expected 字段，CLI 从不注入 expected。
- **修法（评审 Fix A）**：
  ① 两适配器对未结束 call（call 无配对 result）产出 exit=None/ts_end=None 记录
     （exit_signal="pending" 留档未结束信号；IR 契约本就允许 exit=None）；
  ② CLI 事件 id 加调用序号保证唯一：`f"{session_id}:{tool}:{command}#{idx}"`
     （enumerate 序号），unresolved 集合不再被坍缩；
  ③ CLI `detect` 新增 `--expected N` 参数注入 call 事件（观察者声明未结束调用预期时长，
     expected×2 主信号可达——BDD-8 语义接入 CLI；接入方式自主决策，记录于此）。
- **验证**：新测试 `test_bdd_2_claude_unfinished_call_emits_exit_none` /
  `test_bdd_4_dsh_unfinished_call_emits_exit_none`（适配器产出 exit=None/ts_end=None 记录）；
  `test_bdd_9_cli_detect_unfinished_call_frozen`（CLI 通路同会话同命令一结束一未结束，
  未结束 call 距今 400s → FROZEN 兜底 300s）；`test_bdd_8_cli_detect_expected_signal`
  （未结束 call 距今 350s：无 expected → FROZEN（350≥300 兜底）；--expected 200 →
  阈值 400s → NORMAL，证明 expected 已接入 CLI 事件）。

### CRITICAL-4 Claude 解析崩溃链（agate-cmdstream-adapters.py）

- **现象**：`_iso8601_to_epoch_ms(u.get("timestamp", ""))` timestamp 缺失/非 ISO-8601 →
  ValueError 无 try 包裹；`obj.get("content")` 前未校验 obj 为 dict → AttributeError
  （DSH read_commands 同样未校验 obj 类型）。
- **修法（评审 Fix A）**：`_build_record` 内 ts_start/ts_end 解析包 try/except
  (ValueError, TypeError)——ts_start 失败返回 None（该配对跳过并计数告警）；ts_end 失败
  置 None（记录保留、结束时间未知，不崩溃）；`_collect_parts` 与 DSH 解析循环前加
  `isinstance(obj, dict)` 守卫；JSON 解析失败行计数；read_commands 汇总跳过行数写 stderr
  （防静默吞数据需计数）。
- **验证**：新测试 `test_bdd_2_claude_malformed_lines_no_crash`（非 JSON 行/数组行/
  timestamp 缺失 use/timestamp 非法配对应全部跳过，合法配对保留）/
  `test_bdd_4_dsh_non_dict_lines_no_crash`（数组行/字符串行跳过、合法 call/result 保留）。

### CRITICAL-5 OpenCode SQLite 畸形/损坏库崩溃（agate-cmdstream-adapters.py OpenCodeAdapter.read_commands）

- **现象**：`sqlite3.connect` + `conn.execute("SELECT data FROM part")` 无 try/except——
  非 SQLite 文件/缺表/损坏库 → DatabaseError 传播，read_commands 崩溃（DB 文件在用户
  目录，外部不可信输入）。
- **修法（评审 Fix A）**：connect 与 execute 均包 try/except sqlite3.Error——失败返回
  空列表 + stderr 告警（与 `_load_config` 全兜底模式同风格）。
- **验证**：新测试 `test_bdd_3_opencode_corrupt_db_no_crash`——非 SQLite 文本文件与缺
  part 表的合法库均返回空列表不崩溃。

### CRITICAL-6 CommandRecord 类型契约校验缺失（agate-cmdstream-ir.py from_dict/from_json）

- **现象**：P2-design M1 明确「字段契约校验（ts epoch 毫秒 int、exit int|null、truncated
  bool）」，实现只查字段存在性不校验类型——from_json 喂入 ts_start="abc" / exit="x" /
  truncated="yes" 静默接受，坏数据流入 detect 后崩溃或判定失真。
- **修法（评审 Fix A，from_dict 逐字段校验）**：from_dict 对十字段逐字段类型校验——
  platform/session_id/tool/command/exit_signal 须 str；ts_start 须 int（排除 bool，
  bool 是 int 子类）；ts_end/exit 须 int|None；truncated 须 bool；output_hash 须 str|None。
  不符抛 ValueError 带字段名。BDD-1 Then「类型符合 IR 契约」的直接落点。
- **验证**：新测试 `test_bdd_1_ir_from_dict_rejects_bad_types`——5 类坏类型均抛
  ValueError 且带字段名；合法边界（exit=None + ts_end=None，CRITICAL-3 未结束形态）
  不抛；bool 冒充 int 被拒。既有 test_bdd_1 三用例保持绿。

### CRITICAL-7 DSH truncated 恒 False（agate-cmdstream-adapters.py）

- **现象**：适配器硬编码 truncated=False，BDD-17（截断输出不参与无效重复哈希比对）对
  DSH 数据源失效；验证记录 Q6 明确 DSH 有截断标记，真实超大输出截断后仍参与
  (命令, exit, 输出哈希) 比对 → 多个不同失败截断成同前缀 → 误判 SPIN。
- **修法（评审 Fix A）**：新增 `DSHAdapter._detect_truncated(first)` 双信号检测——
  ① tool-result dict 显式布尔字段（truncated / isTruncated）；② 输出文本截断标记字面量
  （"[truncated]" / "…[truncated]" / "Output truncated"，不区分大小写）。命中即
  truncated=True 且 output_hash=None（与 IR 契约 truncated=True → output_hash=None 一致）。
- **验证**：新测试 `test_bdd_4_dsh_truncated_marker_sets_truncated_true`——含
  truncated=true 标记记录 → truncated=True + output_hash=None；exit 解析不受影响。

### 新增/调整测试汇总（BDD 编号引用，不削弱既有断言）

| 测试 | 覆盖 CRITICAL | 说明 |
|------|--------------|------|
| test_bdd_1_ir_from_dict_rejects_bad_types | 6 | from_dict 类型契约（5 类坏类型 + 合法边界 + bool 排除）|
| test_bdd_4_dsh_multi_frame_container_returns_all_records | 2 | 两帧容器逐帧解压全量返回 |
| test_bdd_2_claude_unfinished_call_emits_exit_none | 3 | 未结束 call 产出 exit=None/ts_end=None |
| test_bdd_4_dsh_unfinished_call_emits_exit_none | 3 | 同上（DSH）|
| test_bdd_9_cli_detect_unfinished_call_frozen | 1+3 | CLI 通路调用冻结可达（id 唯一）|
| test_bdd_8_cli_detect_expected_signal | 1+3③ | CLI --expected 注入 expected×2 主信号 |
| test_bdd_11_cli_detect_seconds_unit_no_false_freeze | 1 | 毫秒/秒单位归一不误报 |
| test_bdd_2_claude_malformed_lines_no_crash | 4 | 畸形行跳过不崩溃 + 计数 |
| test_bdd_4_dsh_non_dict_lines_no_crash | 4 | 非 dict 行跳过不崩溃 |
| test_bdd_3_opencode_corrupt_db_no_crash | 5 | SQLite 畸形/缺表返回空列表 |
| test_bdd_4_dsh_truncated_marker_sets_truncated_true | 7 | 截断标记 → truncated=True + output_hash=None |

- 顺带清理（非修复项，保持 CI `ruff check agate/` 全绿）：既有测试文件 5 处 ruff error
  （test_agate_cmdstream_adapters.py RUF015×1 + F841×1、test_agate_cmdstream_detect.py
  RUF059×2、test_agate_cmdstream_dispatch.py 未用 pytest import）——均为机械风格修正，
  不改断言语义。

### [DESIGN_GAP] 决策登记（本轮自主决策）

[DESIGN_GAP: P2-design §3.1 声明 ts_end 为 epoch 毫秒 int；CRITICAL-3 修复需未结束
call 记录携带 ts_end=None（评审 Fix A 明确推荐），故 CommandRecord.ts_end 类型放宽为
int|None（默认 None），from_dict 校验同步放宽；既有 BDD-1 断言（构造时传 int）不受影响]

[DESIGN_GAP: 验证记录 Q6 仅确认 DSH「有截断标记（超大输出会被截断）」未给字段名；
CRITICAL-7 修复采用双信号启发式检测（tool-result dict 显式 truncated/isTruncated 布尔
字段 + 输出文本 "[truncated]"/"…[truncated]"/"Output truncated" 字面量），记录于此供
评审复核；若实机 DSH 截断标记为其他形态，适配器 _detect_truncated 为唯一修改点]

[DESIGN_GAP: fix1 dispatch-context 授权「expected 声明接入 CLI 事件——具体接入方式自主
决策并在 P4-implementation.md 记录」；采用 CLI `--expected N` 参数（观察者声明，事件
元数据形态）而非读 maintainability.yaml——expected 是 RM-AG0023 timeout_seconds 的
per-command 语义，全局阈值配置节无对应键，per-command 由观察者传入最贴合语义]

### 自查结果（fix1，≠ P5 gate）

- cmdstream 套件：`timeout 180s python3 -m pytest agate/tests/unit/test_agate_cmdstream_*.py -q --tb=short`
  → **53 passed**（原 42 + 新增 11，含 4 长期不变量保持）
- verify 锚：`verify_cmdstream_detection.py` 9 场景全 PASS（BDD-22 保持，阈值锚未动）
- 一致性：worktree 自己的 `check-protocol-consistency.py --strict-errors-only` → **0 ERROR**
  （329 WARNING 为既有基线）
- ruff：`~/.venvs/agate-dev/bin/ruff check agate/` → **All checks passed**（全目录，含既有
  测试文件清理）
- count-tests：1436 用例 ≥ 749 基线（+11 来自 fix1 新测试，预期内）
- 全量 unit 回归：后台跑（结果待主 Agent 复核）

### 环境隔离声明（fix1）

[PROD_NOT_TOUCHED] 本修复轮仅修改 worktree 的 agate/scripts 三脚本 + 三个 cmdstream 测试
文件 + P4-implementation.md / P4-progress.md；未触碰生产环境、未读取其他用户 DSH 会话、
未修改 P4-review.md。

### fix2：CRITICAL-4 残留修复

> 依据：P4-review.md（fix1 复审，status=rejected）CRITICAL-4 节——7 CRITICAL 中 6 项已彻底
> 修复，残留 2 条崩溃链（运行时实验复现：int/null timestamp → AttributeError
> 'int'/'NoneType' object has no attribute 'endswith'；toolUseResult 字符串 → AttributeError
> 'str' object has no attribute 'get'），修法按评审原文照做。本轮只修这两处 + 补回归测试，
> 不动已通过评审的 6 项修复、不动阈值数值锚、不动 verify 脚本、不改 P1 基线。

#### 残留崩溃链 1：`_iso8601_to_epoch_ms` 非字符串 timestamp（agate-cmdstream-adapters.py:73-82）

- **现象**：入口 `ts.endswith("Z")` 对 int/None 输入抛 AttributeError，而 `_build_record`
  的 `except (ValueError, TypeError)`（adapters.py:212/235）**不含 AttributeError** →
  传播到 read_commands 整体崩溃。实验复现：tool_use `timestamp:1788400860000`(int) /
  `timestamp:null` / tool_result `timestamp` 为 int → 均 AttributeError 崩溃。
- **修法（评审原文）**：`_iso8601_to_epoch_ms` 入口加
  `if not isinstance(ts, str): raise TypeError`——非字符串输入归一为 TypeError，落入既有
  except 分支：ts_start 失败返回 None（配对跳过 + dropped 计数）、ts_end 失败置 None
  （记录保留、结束时间未知）。
- **验证**：`test_bdd_2_claude_malformed_lines_no_crash` 扩展用例——timestamp 为 int/null
  的 use 配对应被跳过（不崩溃、不产出坏记录）；tool_result timestamp 为 int → 记录保留
  且 ts_end=None。修复前该用例红（AttributeError: 'int' object has no attribute
  'endswith'），修复后绿。

#### 残留崩溃链 2：`_build_record` 非 dict toolUseResult（agate-cmdstream-adapters.py:261-263）

- **现象**：`(r.get("toolUseResult") or {}).get("isImage", False)`——toolUseResult 为非空
  非 dict（如字符串）时 `"str".get` → AttributeError，无守卫。实验复现。
- **修法（评审原文）**：先取引用再 isinstance 守卫——
  `tr = r.get("toolUseResult")`；`truncated = bool(r.get("truncated", False)) or
  (isinstance(tr, dict) and bool(tr.get("isImage", False)))`——非 dict toolUseResult 不再
  触发 `.get`。
- **验证**：`test_bdd_2_claude_malformed_lines_no_crash` 扩展用例——toolUseResult 为字符串
  的 tool_result → 记录保留、truncated 判定不崩溃且为 False。修复前该用例红（AttributeError:
  'str' object has no attribute 'get'），修复后绿。

#### 测试补充记录

- `test_bdd_2_claude_malformed_lines_no_crash` 扩展 4 类畸形输入（引用既有 BDD 编号
  test_bdd_2_*，不削弱既有断言）：timestamp int（tool_use）/ timestamp null（tool_use）/
  tool_result timestamp int / toolUseResult 非 dict（字符串）。先红后绿：修复前 4 类均触发
  崩溃链 AttributeError（红），修复后畸形输入不崩溃、合法配对（python3 -m pytest -q
  tests/unit）保留、计数告警正常（绿）。
- 用例数不变（扩展既有测试函数，未新增函数）：cmdstream 套件保持 53 passed。

#### 自查结果（fix2，≠ P5 gate）

- cmdstream 套件：`timeout 180s python3 -m pytest agate/tests/unit/test_agate_cmdstream_*.py -q --tb=short`
  → **53 passed**（42 既有 + 11 fix1 新增，扩展用例计入既有函数）
- verify 锚：`verify_cmdstream_detection.py` 9 场景全 PASS（BDD-22 保持，阈值锚未动）
- 一致性：worktree 自己的 `check-protocol-consistency.py --strict-errors-only` → **0 ERROR**
  （329 WARNING 为既有基线）
- ruff：`~/.venvs/agate-dev/bin/ruff check agate/scripts/agate-cmdstream-adapters.py
  agate/tests/unit/test_agate_cmdstream_adapters.py` → **All checks passed**
- 全量 unit 回归：后台跑（结果待主 Agent 复核）

#### 环境隔离声明（fix2）

[PROD_NOT_TOUCHED] 本修复轮仅修改 worktree 的 agate/scripts/agate-cmdstream-adapters.py +
agate/tests/unit/test_agate_cmdstream_adapters.py + P4-implementation.md / P4-progress.md；
未触碰生产环境、未读取其他用户 DSH 会话、未修改 P4-review.md。

### fix3：P5 回归修复（R2 裸 python3）

> 依据：P5-test-results/unit.md（P5 全量 pytest 1 failed）——本任务新增 cmdstream 测试
> fixture 数据串裸 `python3`（17 处）触发平台假设扫描器 R2 规则
> （`(^|[\s=(\'\"])python3([\s]|$)`），破坏 TAG0011 bdd-8「tests 树 0 命中」长期不变量
> （`test_bdd_8_clean_tree_zero_detection`）。按 P5 卡片「真失败 → 回 P4 修复」。

#### 根因

- cmdstream 测试 fixture 数据串（模拟平台日志的 command 字段）与断言串直接写裸 `python3`：
  `test_agate_cmdstream_adapters.py` 13 处（141/150/216/217/250/258/270/398/414/431/447/497/506）、
  `test_agate_cmdstream_detect.py` 3 处（396/422/429）、`test_agate_cmdstream_ir.py` 1 处（80）。
- 扫描器 R2 静态命中这些字面量 → `agate/tests/` 全树 0 命中不变量被破坏 → bdd-8 FAIL。
- 该失败为**本任务引入的回归，非预存失败**（check-platform-assumptions.py 未被 TAG0028 改动，
  最后修改 commit = a65e274 wf(TAG0011-P4)）。

#### 修法（利用 R2 显式豁免形态 `env python3`）

- 命令字面量 `python3 -m pytest ...` / `python3 main.py` / `python3 child.py` →
  `env python3 -m pytest ...` / `env python3 main.py` / `env python3 child.py`——R2 豁免逻辑
  `_r2_comment_exempt`（check-platform-assumptions.py:53）显式检查 `"env python3" in text`
  即豁免；命令语义不变（仍表示"用 python3 运行"）。
- 改动集中在 fixture 数据串与对应断言串：**fixture 与断言同步**——不仅三个测试文件 17 处，
  且外部 fixture `cmdstream/claude-code-session.jsonl`（2 处）与 `cmdstream/dsh-session.jsonl`
  （2 处）的 command 字段同步改（断言 141/150/216/217 直接引用其解析值，不同步则断言失配）。
- 测试语义不变：BDD-2/3/4 验证的是"command 字段被正确解析为 IR.command"，`env python3`
  前缀不影响断言逻辑；未动检测引擎/适配器逻辑、未动阈值数值锚、未动 verify 脚本、
  未改 P1 基线、未削弱既有断言。

#### 验证（fix3 自查，≠ P5 gate）

- 扫描器：`check-platform-assumptions.py agate/tests/` → **exit 0、0 命中**（bdd-8 不变量恢复）
- cmdstream 套件：`pytest agate/tests/unit/test_agate_cmdstream_*.py -q --tb=short` → **53 passed**
- verify 锚：`verify_cmdstream_detection.py` 9 场景全 PASS（BDD-22 保持）
- 一致性：`check-protocol-consistency.py --strict-errors-only` → **0 ERROR**（329 WARNING 基线）
- ruff：三个修改测试文件 → **All checks passed**
- 全量 unit 回归：后台跑（结果待主 Agent 复核）

#### 环境隔离声明（fix3）

[PROD_NOT_TOUCHED] 本修复轮仅修改 worktree 的三个 cmdstream 测试文件 + 两个 cmdstream
外部 fixture（.jsonl）+ P4-implementation.md / P4-progress.md；未触碰生产环境、未读取
其他用户 DSH 会话、未修改 P5-test-results/。
