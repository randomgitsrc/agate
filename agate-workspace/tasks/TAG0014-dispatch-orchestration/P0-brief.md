task: "agate 派发编排机制（全阶段，RM-AG0016）：subagent 派发工作量评估 + 五模式编排（单发/静态拆批/并行/先理解后拆/串行链）+ 并行规则统一，解决'工作量高时单 subagent 过载卡死'（TAG0010 批次 0 实证）。P1/P2 补编排空白、P3-P6 统一分散的'按包并行'、P7 不拆分例外、P8 多包拆批。实施参考：agate-workspace/plans/agate-dispatch-orchestration-20260815.md（已通过 plan-eng-review 三轮评审 approved）"

issues:
  - "TAG0010 批次 0 卡死（agate_common 整库 + ci-gate-backstop + 3 bats 一次派发，用户中止）：协议只有'任务粒度指引'（dispatch-protocol.md L639-663，限输入/产出数量），无工作量评估方法、无编排模式定义、无并行规则；P1/P2 无任何编排机制"
  - "并行规则分散且缺：P3/P4/P5/P6 各卡片有独立'按包拆分并行'，无统一机制；无并行上限（平台并发 + 主 Agent 上下文）、无并行失败处理（失败批单独 retry vs 全批重跑）、无共享文件统一约束（仅 P4 有）"
  - "模式 4 先理解后拆（用户扩展需求）：工作量高/结构不明时——侦察 subagent 读全貌产出拆分方案 → 按方案派执行（并行/串行）→ 合并（轻量拼装主 Agent/单 subagent；重量整合派整合 subagent）。不局限于 P4，全阶段适用"
  - "落地：dispatch-protocol 新增「派发编排机制」权威节 + P2-design.md 新增 dispatch_plan: 机器字段（frontmatter flow YAML，mode/batches/parallel_limit，gate 校验）+ 各阶段卡片统一引用 + architect.md 批次设计节 + dispatch-prompt.md 粒度兜底"

known_risks:
  - "改动面最大（dispatch-protocol + P1-P8 全阶段卡 + architect + 派发模板 + check-gate.py + agate-md-field-get.py + 测试）→ 触发 SELF-GATE，P2 需按 approved plan 的 6 个 Task 组织"
  - "【阶段完整性】有 approved plan ≠ 裁剪阶段——本任务仍走完整 P0-P8，P1/P2 须产出本任务自己的需求基线与设计（可引用 plan 内容，不可跳过 gate）。plan 是参考输入（roadmap RM-AG0016 详情已声明）"
  - "dispatch_plan: 字段契约细节已由 plan 定死（frontmatter 单行 flow + op 子进程读取 + JSON 输出 + 不入 frontmatter-check schema，B3 修复）——P2 设计须遵循，不重新发明"
  - "【强制要求】同类扫描 + 影响面梳理：P1 必须全仓 grep '按包拆分并行'（P3-P6 卡片 4 处）、'任务粒度指引'引用点（dispatch-protocol 内部 3 处）、~/.agate 脚本引用路径，建影响面表。用户明确：不愿意一轮一轮来回改"

executor_env:
  platform: "opencode"
  has_task_tool: true
  has_local_runtime: true
  network: "full"
  git: true

env_constraints:
  debug_env: "本环境为 Linux；Windows 靠 CI matrix（pytest -m windows_smoke）"
  test_cmd: "python3 -m pytest agate/tests/；python3 agate/scripts/check-protocol-consistency.py --strict；bash agate/tests/scripts/count-tests.sh"
  workspace_path: "{AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/"
  # 参考计划：agate-workspace/plans/agate-dispatch-orchestration-20260815.md（三轮评审 approved，字段契约 + 6 Task + 验收标准）
