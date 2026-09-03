---
phase: P6
task_id: TAG0028
type: acceptance
parent: P5-verification.md
trace_id: TAG0028-P6-20260903
status: draft
created: 2026-09-03
agent: verifier
# ── v2.0 机器汇总 ──
pass: 33
fail: 0
ui_affected: false
---

# P6 验收 — TAG0028 subagent 存活可观测性与受控自主再派发（RM-AG0055）

> 阶段：P6（验收）· 角色：verifier · 日期：2026-09-03
> 验收锚：P1-requirements.md 33 条 BDD（`#### BDD-NN:`，fix1 后全局连续）
> 验收对象：命令流三脚本（IR / 三平台适配器 / 检测引擎）+ 心跳生命周期 + 再派发边界 + 协议改写（P4 实现，P5 已验证 1434 passed）
> 执行环境：worktree `.worktrees/agate-TAG0028`（HEAD=700f074；p5_pass_commit=34366ab 之后无非产出文件改动，审计 7 判 reuse_allowed）
> 全量回归证据：复用 P5-test-results/unit.md（1434 passed / 0 failed / 2 skipped；consistency 0 ERROR；verify 9 场景全 PASS），未重跑全量回归
> 验收方式：每条 BDD 用 pytest 单测（`python3 -m pytest -k "bdd_NN"`）+ 脚本 CLI 实跑（verify 锚 / check-p6-provenance）/ 文档断言（git 检查、脱敏 grep）实跑落盘 P6-evidence/
> 环境隔离：[PROD_NOT_TOUCHED] 只读验收，未写生产环境、未读取其他用户 DSH 会话（fixture 为 P3 已入库脱敏样例）

## Phase 1 — 命令流数据源解析层（BDD-1~7）

- PASS BDD-1: 统一 CommandRecord IR 字段完整性——test_agate_cmdstream_ir.py 4 用例全绿（字段集合十字段 + ts_start/ts_end 毫秒 int + exit int|null + truncated bool + from_dict 坏类型拒绝），证据 (bdd-01.log)
- PASS BDD-2: claude-code 适配器从 JSONL 解析命令流——test_bdd_2_* 3 用例全绿（tool_use/tool_result 配对、command=input.command、ts 来自配对行、"Exit code N" 前缀解析 exit 并写 exit_signal；含未结束 call 产出 exit=None、畸形行不崩溃），证据 (bdd-02.log)
- PASS BDD-3: opencode 适配器从 SQLite 解析命令流——test_bdd_3_* 2 用例全绿（part.data.state 结构、exit 取 state.metadata.exit 整数、truncated 取显式标记；损坏库返回空列表不崩溃），证据 (bdd-03.log)
- PASS BDD-4: dsh 适配器从 JSONL.zstd 解析命令流——test_bdd_4_* 6 用例全绿（解压隔离适配器内、不依赖 python zstandard、多帧容器逐帧解压全量返回、callId 配对 ts_start/ts_end、"Error:" 前缀 exit、截断标记 → truncated=True + output_hash=None），证据 (bdd-04.log)
- PASS BDD-5: 子 agent 会话定位（sidecar / delegationDepth）——test_bdd_5_* 2 用例全绿（Claude Code 读 subagents/agent-*.jsonl sidecar、DSH 读 delegationDepth>0 独立 session 文件，与主会话可区分），证据 (bdd-05.log)
- PASS BDD-6: 新增平台只写适配器、检测引擎零改动——test_bdd_6_* 2 用例全绿（ADAPTERS 显式注册表契约 + detect 消费注册表零改动断言），证据 (bdd-06.log)
- PASS BDD-7: 解析单测 fixture 取自验证记录且脱敏——test_bdd_7_fixture_sanitized 通过 + 脱敏 grep 扫描 0 命中（fixture 仅含 /example/repo、demo 等脱敏样例，无真实用户路径/密钥/会话标识），证据 (bdd-07.log, bdd-07-sanitize.log)

## Phase 2 — 检测引擎（BDD-8~24）

- PASS BDD-8: 调用冻结·主信号（未结束 call + expected → expected×2）——test_bdd_8_* 2 用例全绿（含 CLI --expected 注入 350s 未结束 call：--expected 200 → 阈值 400s → NORMAL），证据 (bdd-08.log)
- PASS BDD-9: 调用冻结·兜底 alert（无 expected → 300s）——test_bdd_9_* 2 用例全绿（400s 未结束 call → FROZEN alert；CLI 通路未结束 call 距今 400s → FROZEN），证据 (bdd-09.log)
- PASS BDD-10: 调用冻结·兜底 suspect（无 expected → 900s）——test_bdd_10_call_freeze_fallback_suspect_900 通过（FROZEN suspect），证据 (bdd-10.log)
- PASS BDD-11: 活动冻结·alert（最后活动 >60s）——test_bdd_11_* 2 用例全绿（含 CLI 毫秒/秒单位归一不误报回归），证据 (bdd-11.log)
- PASS BDD-12: 活动冻结·suspect（最后活动 >300s）——test_bdd_12_activity_freeze_suspect_300 通过（ACTIVITY_FROZEN suspect），证据 (bdd-12.log)
- PASS BDD-13: 三类活动信号均计入活动、长时间思考不误杀——test_bdd_13_* 2 用例全绿（think 事件持续流动 20 分钟级 → NORMAL；out 输出事件计入活动），证据 (bdd-13.log)
- PASS BDD-14: 无效重复检测（窗口 10 同签名 ≥5 → SPIN）——test_bdd_14_spin_repeat_signature 通过（SPIN + 重复组合与次数），证据 (bdd-14.log)
- PASS BDD-15: 无效重复·结果签名变化不误报——test_bdd_15_signature_change_no_spin 通过（NORMAL，不触发空转），证据 (bdd-15.log)
- PASS BDD-16: 无效重复·唯一命令数 <3 信息级提示——test_bdd_16_unique_cmd_lt3_info 通过（NORMAL + 信息级提示，不判 SPIN），证据 (bdd-16.log)
- PASS BDD-17: 截断输出不参与无效重复哈希比对——test_bdd_17_* 2 用例全绿（truncated 不参与 (命令,exit,哈希) 比对 → NORMAL；truncated 记录仍参与冻结检测），证据 (bdd-17.log)
- PASS BDD-18: 轮询循环误报标注（合法轮询不判死）——test_bdd_18_polling_loop_annotated 通过（信号附「轮询」核查提示，非自动终止），证据 (bdd-18.log)
- PASS BDD-19: 阈值显式覆盖生效——test_bdd_19_threshold_override_config 通过（config 覆盖 activity_alert=120 生效，不用默认值），证据 (bdd-19.log)
- PASS BDD-20: 阈值配置缺失兜底默认值——test_bdd_20_config_missing_fallback 通过（config 缺失 → 协议默认值 300/900/60/300/10/5 + REPEAT_UNIQUE_MIN=3，正常运行），证据 (bdd-20.log)
- PASS BDD-21: 阈值配置损坏兜底默认值——test_bdd_21_config_corrupt_fallback 通过（损坏 config → 兜底默认值，不报错不静默跳过），证据 (bdd-21.log)
- PASS BDD-22: verify_cmdstream_detection.py 9 场景全 PASS 保持——verify 锚直跑 9 场景（A 调用阻塞/B 空转/C 合法迭代/D 健康长尾/E 合法长命令/F expected 超期/G 截断排除/H 长时间思考/I 活动冻结）全部 PASS + 结论行「全部断言通过——命令流日志可机械区分九种状态」+ pytest 承载 test_bdd_22 通过，证据 (bdd-22.log)
- PASS BDD-23: 检测定位「证据 + 触发核查，不自动判死」——test_bdd_23_evidence_no_auto_kill 通过（输出仅客观证据，无 kill/terminate/abort 动作指令），证据 (bdd-23.log)
- PASS BDD-24: 检测/派发输出平台无关——test_bdd_24_output_platform_agnostic 通过（判定类别 + 原因 + 阈值依据 + 建议动作方向，不含平台工具名），证据 (bdd-24.log)

## Phase 3 — 心跳文件生命周期 + 协议文档（BDD-25~28）

- PASS BDD-25: 心跳文件父子分层命名——test_bdd_25_heartbeat_naming_doc 通过（dispatch-protocol.md 命名规范断言：`${TASK_DIR}/.heartbeat` 与 `.heartbeat.child-{n}`，同父任务内不重复不覆盖），证据 (bdd-25.log)
- PASS BDD-26: 心跳文件审计豁免确认——test_bdd_26_* 2 用例全绿（check-p6-provenance.py HEARTBEAT_AUDIT_EXEMPTION 登记 + 隐藏文件天然跳过审计行为）+ CLI 实跑：含 `.heartbeat`/`.heartbeat.child-1` 的任务目录跑 check-p6-provenance.py exit 0，证据 (bdd-26.log, bdd-26-cli.log)
- PASS BDD-27: 任务结束清理 + 异常遗留兜底——test_bdd_27_cleanup_doc 通过（文档断言：产生方清理自己心跳文件 + 派发前置检查清空遗留，复用 agate-archive-stale-outputs 模式），证据 (bdd-27.log)
- PASS BDD-28: dispatch-protocol.md 两套信号职责分工改写——test_bdd_28_two_signals_doc 通过（文档断言：命令流日志承担存活/卡死判定、progress.md 保留语义进展职责、不修改 check-gate.py/check-state-transition.py 返回约定），证据 (bdd-28.log)

## Phase 4 — 受控自主再派发（BDD-29~33）

- PASS BDD-29: 执行角色子派发权限下放（不写 .state.yaml）——test_bdd_29_no_state_yaml_boundary 通过（role-system.md 文档断言：子任务不写 .state.yaml/active-tasks.md，不产生独立 phase 状态，父汇总「路径+摘要」回报），证据 (bdd-29.log)
- PASS BDD-30: 子任务写权限严格子集——test_bdd_30_write_subset_boundary 通过（文档断言：父派子任务 prompt 显式重申写权限子集、不自动继承），证据 (bdd-30.log)
- PASS BDD-31: judge 类角色例外声明——test_bdd_31_* 2 用例全绿（role-system.md judge 不适用子派发 + dispatch-context 模板「不启用子派发能力」声明位），证据 (bdd-31.log)
- PASS BDD-32: 子派发产出收敛、不触发 gate 判定——test_bdd_32_output_convergence_no_gate 通过（文档断言：中间产出不计 gate 判定、files_modified 走 D2、不产生新编排层级），证据 (bdd-32.log)
- PASS BDD-33: 不破坏 gate 返回约定（两套独立信号）——test_bdd_33_gate_return_contract_preserved 通过（长期不变量绿保持）+ git 检查确认 34366ab..HEAD 间 check-gate.py/check-state-transition.py/agate/rules/ 零改动（exit 三态约定天然保持）+ 全量回归复用 P5 证据 1434 passed 无回归，证据 (bdd-33.log, bdd-33-git.log, ../P5-test-results/unit.md)

## 验收汇总

**Summary**: 33/33 PASS, 0 FAIL（pass=33, fail=0, ui_affected=false；pass+fail=33 与 P1 BDD 数一致）

- 全量回归：复用 P5-test-results/unit.md（1434 passed / 0 failed / 2 skipped），未重跑（审计 7 reuse_allowed）
- ui_affected: false（P2 声明一致），无 UI/视觉维度，证据形式 = 断言日志 / 测试输出 / 脚本实跑记录
- 验收记录的是验收时的事实：BDD-1~33 全部按实跑结果判定 PASS，无"调整/跳过/覆盖"中间态
- 自查≠gate：本文件为 verifier 产出，P6 gate（check-gate/check-p6-evidence/check-p6-provenance + P6.5 judge）由主 Agent 亲自跑
