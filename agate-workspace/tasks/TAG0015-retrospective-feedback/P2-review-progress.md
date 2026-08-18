[2026-08-19] 约束1a 候选方案A(L2落点)：核对 roadmap.md RM-AG0020 详情/P0-brief.md:11 原文，发现 A1"落盘时机"排除每阶段checkpoint的理由与roadmap原设计（P{n}-checkpoint.md + task-session-summary.md 两件套）不符，判定为需修订项
[2026-08-19] 约束1b 候选方案B(匿名化深度)：B1/B2权衡对应BDD-18 Given场景具体，理由充分，通过
[2026-08-19] 约束2 BDD覆盖：grep -o "BDD-[0-9]+" | sort -u 得20个唯一编号(BDD-1~20全部命中)，通过
[2026-08-19] 约束3 不改什么覆盖P1第7节三项：hardening-roadmap.md P2.68 / archived/ / TAG0013历史产物 均逐条列出，通过
[2026-08-19] 约束4 gate_commands可执行性：P3/P5均为具体pytest命令，含test_retrospective_protocol_docs.py覆盖纯文档BDD，非"待定"，通过
[2026-08-19] 约束5 P3/P5惯例：P3不声明timeout_seconds(遵循AGATE_TDD_TIMEOUT)，P5_timeout_seconds:180附RM-AG0026实测数据(823用例106-115s)佐证，通过
[2026-08-19] 约束6 minimal_validation读代码验证：核实agate-state-get.py:37-39 task_id op存在、pre-commit-gate.py:397调用签名[task_dir,state_file]、tech-debt-template.md:70/roadmap.md表格task_id格式，均属实；发现files_to_read次要瑕疵：agate_common.py:455-482引用范围不含AGATE_TDD_TIMEOUT(实际在408行)
[2026-08-19] 约束7 dispatch_plan single：批次设计理由具体(implicit_coupling风险/低复杂度/脚本-文档语义耦合)，通过
[2026-08-19] 约束8 判定：needs-revision，理由见P2-review.md，非裸approved
[r1-1] 核查 §2/§3.2/§3.3/§6 四处联动：均一致描述 P{n}-checkpoint.md（每阶段 gate 通过后落盘）+ task-session-summary.md（P8 完成后一次性落盘）两件套机制，无半吊子状态。通过。
[r1-2] 核查核心问题（中途 compact 时 L2 非空落点）：§2 A1 第1点已恢复"每阶段 gate 通过时落盘"，非仅 P8 后落盘一次，明确解决 AP-1。通过。
[r1-3] 核查 test_bdd_13_l2_checkpoint_docs 锚点合理性：断言 state-machine.md 小节正文含两个文件名字符串，对应 BDD-13 Then 子句（P2-design.md 须显式回答四问 + 落字到协议文档），非摆样子；BDD-13 本身不要求验证运行时跨阶段文件存在性（无法用 P3 单测验证真实 P1-P8 执行），静态锚点是恰当颗粒度。通过。
[r1-4] 核查 AP-2 files_to_read 行号订正：agate_common.py 行号范围已改为 400-482，覆盖 AGATE_TDD_TIMEOUT 实际所在的第 408 行（grep 验证）；why 文字写"第 407 行"（与实际 408 行差 1，属文字描述层面的轻微笔误，范围本身已覆盖，不影响 P4 落地）。基本通过，遗留极小笔误不阻塞。
