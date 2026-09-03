---
phase: P3
task_id: TAG0028
parent: P2-design.md
trace_id: TAG0028-P3-20260903
status: draft
created: '2026-09-03'
test_code_dir: agate/tests/unit/
agent: test-designer
---
# P3 测试设计 — TAG0028 subagent 存活可观测性与受控自主再派发（RM-AG0055）

> 阶段：P3（TDD 测试设计）· 角色：test-designer · 日期：2026-09-03
> 上游输入：P1-requirements.md（33 条 BDD）· P2-design.md（方案 A + M9 测试面 + gate_commands）·
> verification-cmdstream-datasource-20260903.md（fixture 样例来源）· verify_cmdstream_detection.py
> （9 场景判据参考）· conftest.py（fixture 体系）· AGENTS.md（测试平台无关约束）
> 验收锚：P1 33 条 BDD 逐条对应 pytest 用例（1:1），测试名引用 BDD 编号；当前全部红灯
> （被测模块未实现），P4 实现后转绿。

## 1. test_code_dir 声明

- **test_code_dir: `agate/tests/unit/`**
- 测试文件（5 个，前缀 `test_agate_cmdstream_` 与既有 `test_agate_*` 惯例一致）：
  - `test_agate_cmdstream_ir.py` — BDD-1（CommandRecord IR 契约 + 序列化）
  - `test_agate_cmdstream_adapters.py` — BDD-2~7（三平台 fixture 解析 + 子 agent 会话定位 +
    注册表 + fixture 脱敏）
  - `test_agate_cmdstream_detect.py` — BDD-8~24（检测引擎：9 场景复刻 + 阈值兜底 + verify 锚 +
    不判死 + 平台无关输出）
  - `test_agate_cmdstream_heartbeat.py` — BDD-25~28（心跳命名/审计豁免/清理 + 两套信号文档断言）
  - `test_agate_cmdstream_dispatch.py` — BDD-29~33（再派发边界 + gate 返回约定）
- fixture 落点：`agate/tests/fixtures/cmdstream/`（三平台脱敏样例）

## 2. 测试面总览（P2 M9 映射）

| 测试面 | 文件 | BDD 覆盖 |
|--------|------|----------|
| IR 契约 | test_agate_cmdstream_ir.py | BDD-1 |
| 适配器解析 | test_agate_cmdstream_adapters.py | BDD-2/3/4/5/6/7 |
| 检测引擎判定 | test_agate_cmdstream_detect.py | BDD-8~24 |
| 心跳文件生命周期 | test_agate_cmdstream_heartbeat.py | BDD-25/26/27/28 |
| 自主再派发边界 | test_agate_cmdstream_dispatch.py | BDD-29~33 |

## 3. BDD → 测试用例映射（1:1，33 条全映射）

> 每条 `#### BDD-NN` 至少一个测试用例，测试名引用 BDD 编号。全文件 42 个用例。

### Phase 1 — 命令流数据源解析层（BDD-1~7）

| BDD | 测试用例 | 断言要点 |
|-----|---------|---------|
| BDD-1 | test_bdd_1_ir_field_contract / test_bdd_1_ir_exit_none_truncated_true / test_bdd_1_ir_json_roundtrip | CommandRecord 十字段字段完整 + 类型契约（ts_start/ts_end epoch 毫秒 int、exit int\|None、truncated bool）+ to_json/from_json 往返 |
| BDD-2 | test_bdd_2_claude_adapter_parses_jsonl | claude fixture JSONL → command=input.command、ts_start/ts_end 来自配对 timestamp、"Exit code N" 前缀解析 exit 并写 exit_signal |
| BDD-3 | test_bdd_3_opencode_adapter_parses_sqlite | 运行时构造 SQLite（part.data.state）→ exit 取 metadata.exit 整数、truncated 取 metadata.truncated 显式标记 |
| BDD-4 | test_bdd_4_dsh_adapter_parses_zstd / test_bdd_4_dsh_adapter_no_python_zstandard_dependency | node 运行时构造真实 zstd 帧 → 适配器内部解压、不依赖 python zstandard、callId 配对 ts_start/ts_end、isError+"Error:" 前缀解析；node 不可用 skip 标注 |
| BDD-5 | test_bdd_5_claude_subagent_sidecar_locates / test_bdd_5_dsh_delegation_depth_locates | Claude sidecar subagents/agent-*.jsonl 定位；DSH delegationDepth>0 独立 session 定位 |
| BDD-6 | test_bdd_6_adapter_registry_contract / test_bdd_6_detect_consumes_registry_zero_change | ADAPTERS 注册表三平台键 + probe/list_sessions/read_commands 契约；detect 模块 import ADAPTERS 零改动消费 |
| BDD-7 | test_bdd_7_fixture_sanitized | 三平台 fixture 字段结构取自验证记录 + 内容脱敏（无真实路径/密钥/26 位 hex 会话标识，demo 占位） |

### Phase 2 — 检测引擎（BDD-8~24）

| BDD | 测试用例 | 断言要点 |
|-----|---------|---------|
| BDD-8 | test_bdd_8_call_freeze_expected_x2 | 未结束 call + expected 声明 → 距今 >max(expected×2,30s) → FROZEN，原因注明 expected×2 主信号 |
| BDD-9 | test_bdd_9_call_freeze_fallback_alert_300 | 未结束 call 无 expected → 距今 >300s → FROZEN（alert 级 + 阈值依据） |
| BDD-10 | test_bdd_10_call_freeze_fallback_suspect_900 | 未结束 call 无 expected → 距今 >900s → FROZEN（suspect 级 + 阈值依据） |
| BDD-11 | test_bdd_11_activity_freeze_alert_60 | 无未结束 call → 最后活动距今 >60s → FROZEN（alert 级活动冻结） |
| BDD-12 | test_bdd_12_activity_freeze_suspect_300 | 无未结束 call → 最后活动距今 >300s → FROZEN（suspect 级） |
| BDD-13 | test_bdd_13_long_thinking_no_false_freeze / test_bdd_13_output_activity_counts | think 事件持续流动（20 分钟不调工具）→ NORMAL；output/think/工具三类均计活动 |
| BDD-14 | test_bdd_14_spin_repeat_signature | 窗口 10 内同 (命令,exit,输出哈希) 重复 ≥5 → SPIN + 重复组合与次数 |
| BDD-15 | test_bdd_15_signature_change_no_spin | 命令名重复但 exit/输出哈希变化（合法迭代）→ NORMAL |
| BDD-16 | test_bdd_16_unique_cmd_lt3_info | 唯一命令数 <3 且签名变化 → NORMAL + 信息级提示（REPEAT_UNIQUE_MIN=3） |
| BDD-17 | test_bdd_17_truncated_not_in_hash_compare / test_bdd_17_truncated_still_in_freeze_detect | truncated 不参与哈希比对（不误判 SPIN）；仍参与冻结检测 |
| BDD-18 | test_bdd_18_polling_loop_annotated | 轮询重复（gh pr checks --watch）→ 附轮询误报类标注（核查提示非自动终止） |
| BDD-19 | test_bdd_19_threshold_override_config | config 显式覆盖（activity_alert=120）→ 按覆盖值判定 |
| BDD-20 | test_bdd_20_config_missing_fallback | 配置缺失（不存在路径）→ 兜底协议默认值不报错 |
| BDD-21 | test_bdd_21_config_corrupt_fallback | 配置损坏（YAML 解析失败）→ 兜底默认值不报错不静默跳过 |
| BDD-22 | test_bdd_22_verify_script_all_pass | verify_cmdstream_detection.py 存在 + 运行 exit 0 + 结论串（长期不变量） |
| BDD-23 | test_bdd_23_evidence_no_auto_kill | FROZEN/SPIN 输出仅为客观证据（类别+原因+阈值依据），无 kill/terminate/abort 动作指令 |
| BDD-24 | test_bdd_24_output_platform_agnostic | 检测输出不含 claude/opencode/dsh 平台工具名（平台无关指令形态） |

### Phase 3 — 心跳文件生命周期 + 协议文档（BDD-25~28）

| BDD | 测试用例 | 断言要点 |
|-----|---------|---------|
| BDD-25 | test_bdd_25_heartbeat_naming_doc | dispatch-protocol.md 含 .heartbeat / .heartbeat.child-{n} 命名规范（文档断言） |
| BDD-26 | test_bdd_26_audit_exemption_registered / test_bdd_26_audit_behavior_hidden_files_skipped | check-p6-provenance.py 登记显式豁免（红）；行为：_find_files 跳过隐藏文件（绿，长期不变量） |
| BDD-27 | test_bdd_27_cleanup_doc | dispatch-protocol.md 含清理时机（产生方清理 + 派发前置检查清空遗留）文档断言 |
| BDD-28 | test_bdd_28_two_signals_doc | dispatch-protocol.md 存活检查节改写：命令流=存活判定、progress.md=语义进展（文档断言） |

### Phase 4 — 受控自主再派发（BDD-29~33）

| BDD | 测试用例 | 断言要点 |
|-----|---------|---------|
| BDD-29 | test_bdd_29_no_state_yaml_boundary | role-system.md 含子派发不写 .state.yaml/active-tasks.md 边界（文档断言） |
| BDD-30 | test_bdd_30_write_subset_boundary | role-system.md 含写权限严格子集边界（文档断言） |
| BDD-31 | test_bdd_31_judge_exception_role_system / test_bdd_31_judge_no_subdispatch_declaration | role-system.md judge 例外 + dispatch-context.md 模板「不启用子派发能力」声明位（文档断言） |
| BDD-32 | test_bdd_32_output_convergence_no_gate | dispatch-protocol.md 含自主再派发节 + 不产生新编排层级（文档断言） |
| BDD-33 | test_bdd_33_gate_return_contract_preserved | check-gate.py/check-state-transition.py 对既有任务仍返回三态 0/1/2（绿，长期不变量） |

## 4. 被测接口契约（P4 implementer 导航）

> 测试是 P4 实现的契约：以下接口假设均有 P2-design.md 或 verify 脚本明文依据，非测试杜撰。
> 检测引擎判据以 verify_cmdstream_detection.py 9 场景（A-I）为参考实现，阈值常量同源。

### 4.1 agate-cmdstream-ir.py（M1，BDD-1）

- `CommandRecord` dataclass 十字段：platform / session_id / tool / command / ts_start / ts_end /
  exit / exit_signal / output_hash / truncated
- 类型契约：ts_start/ts_end epoch 毫秒 int、exit int|None、truncated bool
- `to_json()` / 模块级 `from_json(s)`（JSON 往返）

### 4.2 agate-cmdstream-adapters.py（M2，BDD-2~7）

- 基类 `CommandStreamAdapter`：`probe(path)->bool` / `list_sessions(cwd)->list[str]` /
  `read_commands(session_path)->list[CommandRecord]`
- `ClaudeCodeAdapter`：JSONL，tool_use/tool_result 配对（sourceToolAssistantUUID↔uuid）、
  command=input.command、ts 来自 timestamp、"Exit code N" 文本前缀解析 exit + exit_signal 留档
- `OpenCodeAdapter`：SQLite part.data.state，exit=state.metadata.exit 整数、
  truncated=state.metadata.truncated、ts=state.time.start/end
- `DSHAdapter`：JSONL.zstd（node zlib.zstdDecompressSync 解压，隔离在适配器内部），
  tool/call+tool/result 按 callId 配对、isError+"Error:" 前缀解析 exit + exit_signal、
  子 agent=delegationDepth>0 独立 session
- 注册表 `ADAPTERS = {"claude-code": ..., "opencode": ..., "dsh": ...}`（显式注册，P2 §2.1 候选 A）
- 子 agent 定位：Claude list_sessions 返回 sidecar `subagents/agent-*.jsonl`；DSH 返回
  delegationDepth>0 独立 session 文件

### 4.3 agate-cmdstream-detect.py（M3，BDD-8~24）

- `detect(events, now, config=None) -> (verdict, reasons)`；verdict ∈ {FROZEN, SPIN, NORMAL}，
  reasons 为字符串列表（阈值依据 + alert/suspect 级别标注）
- events：活动事件 dict 列表（与 verify Event 同构）：`{"ts": int, "kind": "think"|"out"|"call"|"result",
  "id"?, "cmd"?, "exit"?, "out"?, "expected"?, "truncated"?}`
- config：dict（阈值显式覆盖，BDD-19）或路径字符串（maintainability.yaml 路径，缺失/损坏兜底
  协议默认值不报错，BDD-20/21）
- 阈值常量（与 verify 同源）：CALL_EXPECT_MULT=2 / CALL_FLOOR=30 / CALL_ALERT_FALLBACK=300 /
  CALL_SUSPECT_FALLBACK=900 / ACTIVITY_ALERT=60 / ACTIVITY_SUSPECT=300 / SPIN_THRESHOLD=5 /
  REPEAT_WINDOW=10 / REPEAT_UNIQUE_MIN=3
- 输出约束：reasons 含级别关键字（alert/suspect）与阈值依据；SPIN 附重复组合与次数；
  轮询场景附"轮询"标注（BDD-18）；不含 kill/terminate/abort 动作指令（BDD-23）；
  不含 claude/opencode/dsh 平台工具名（BDD-24）

### 4.4 心跳生命周期（Phase 3，文档断言为主）

- BDD-25/27/28：dispatch-protocol.md「心跳文件生命周期」子节改写（命名规范 / 清理时机 /
  两套信号分工）——测试为文档断言，P4 改写后转绿
- BDD-26：check-p6-provenance.py 路径过滤逻辑处登记显式豁免确认（M8）；行为部分
  `_find_files` 隐藏文件过滤为既有长期不变量（已绿）

## 5. 红灯性质与 TDD 语义

- 42 用例当前 **38 failed + 4 passed**；failed 全部为 B 类红灯（被测模块未实现：
  `agate-cmdstream-ir.py` / `agate-cmdstream-adapters.py` / `agate-cmdstream-detect.py` 不存在 →
  `_load_*` helper 检查文件存在性后 `pytest.fail`；协议文档改写未落地 → 文档断言失败），
  无 A 类错误（SyntaxError / 第三方 import 失败 / collection error 均为 0）
- 4 个 passed 为预期绿（长期不变量 / 数据断言）：
  - test_bdd_7_fixture_sanitized（fixture 脱敏数据断言，fixture 为 P3 产出）
  - test_bdd_22_verify_script_all_pass（verify 脚本 9 场景全 PASS 保持——TAG0025 长期不变量）
  - test_bdd_26_audit_behavior_hidden_files_skipped（既有 _find_files 隐藏过滤行为）
  - test_bdd_33_gate_return_contract_preserved（既有 gate 三态约定）
- 红灯归类安全性：所有被测模块缺失路径均转 pytest.fail（failed 计数），不传播裸
  FileNotFoundError/ImportError（error 计数 → check-tdd-red 按 A 类误判）；pytest 输出无
  Traceback/ImportError/ModuleNotFoundError 字样，无 formatter 时 check-tdd-red 走
  exit-code-only 也不会误判 A 类

## 6. 环境事实记录

- node zstd：`node -e "const z=require('node:zlib'); console.log(typeof z.zstdDecompressSync,
  typeof z.zstdCompressSync)"` → 均 function（2026-09-03 本机探测）——DSH zstd 用例运行时
  构造真实 zstd 帧，不硬依赖 python zstandard
- pytest 形态：`python3 -m pytest`（环境无裸 pytest 可执行文件，gate_commands.P3 已固化）
- 测试平台无关约束（AGENTS.md）：全部用 `tmp_path`（不用 /tmp）、`python_exe` fixture 探测
  （不裸 python3）、`run_cli`/`load_fixture`/`git_repo`/`task_dir` 复用 conftest 体系

## 7. 环境隔离声明

[PROD_NOT_TOUCHED] 本阶段仅读取任务目录、协议本体、设计文档与验证记录，未触碰生产环境；
未读取其他用户 DSH 会话（三平台 fixture 均为脱敏虚构样例，字段结构取自验证记录，内容为
demo 占位）。
