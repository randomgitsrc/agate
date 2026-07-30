- [check-gate.sh] P2 review 文件不存在时 exit 1（bug fix），P0 五字段→四字段，P5 新增机械 diff 检查，P3 exec 传 $TASK_DIR
- [check-tdd-red.sh] 新增 gate_commands.P3 自动读取，探测链 TEST_RUNNER→P3→pytest→exit3，接收位置参数 $1
- [P0-orchestrator.md] 五字段→四字段，推进条件改 AND checklist，环境自检强制
- [P1-requirements.md] 五字段→四字段引用，推进条件加 P1-review.md approved
- [P2-design.md] minimal_validation 强制声明，design_trivial 须附理由，gate_commands.P3 可选，P2-review 不存在→exit1，推进条件 AND checklist
- [P3-tdd.md] 步骤0跑基线，测试运行器探测链文档化，"可选"→"条件触发"
- [P4-implementation.md] P5 改为 verifier subagent 执行，评审 C8 映射强制，"可选"→"条件触发"，基础设施隔离"必须"
- [P5-verification.md] 非 pytest 技术栈改引用 gate_commands.P3，全量测试 WARNING→必须标注，签名校验"必须"
- [P6-acceptance.md] "先验证功能再满足格式"→"两者都必须满足"，P6 gate 明确跑哪些脚本
- [P7-consistency.md] 裁剪跳阶 coupling_checklist 须≥2个耦合点，推进条件 AND checklist
- [P8-release.md] "手动确认"→"必须亲自执行"，推进条件 AND checklist
- [state-machine.md] P0 四字段，check-tdd-red.sh 设计块更新探测链，步骤2 四字段
- [dispatch-protocol.md] P0 四字段，P2 最小验证改措辞，P4 评审 C8 映射，P6 自查节改，office-hours 触发条件改
- [task-files.md] P0 删除 pruning_tendency，gate_commands.P3 新增，minimal_validation 强制声明
- [dispatch-prompt.md] P2 最小验证改措辞（与 P2-design.md/ dispatch-protocol.md 一致）
- [architect.md] 输入删 pruning_tendency，gate_commands P3/P5/P6，minimal_validation 强制声明
- [verifier.md] 非 pytest 技术栈改引用 gate_commands.P3
- [plan-eng-review.md] P2 最小验证检查项更新
- [role-system.md] office-hours 触发条件改
- [review-mapping.md] office-hours 触发条件改
- [hardening-roadmap.md] v0.25.0 记录 P2.49+P2.50

A1/文档→脚本: P2-design.md 说 P2-review.md 不存在→exit 1 / check-gate.sh:101-103 实现 exit 1 / 结论: ALIGNED
A1/文档→脚本: P2-design.md 说 gate_commands.P3 可选 / check-tdd-red.sh:66-78 实现自动读取 / 结论: ALIGNED
A1/文档→脚本: state-machine.md:76 说 P0 四字段 / check-gate.sh:39 P0 提示也改四字段 / 结论: ALIGNED
A1/文档→脚本: P0-orchestrator.md 删除 pruning_tendency / task-files.md:25 删除 / dispatch-protocol.md:200 删除 / state-machine.md:76 删除 / 结论: ALIGNED
A1/文档→脚本: dispatch-protocol.md:200 phase_hint 缩进从 4 空格改为 2 空格 / 但实际 YAML 缩进不一致（见 A3b 反向传播）
A2/脚本→文档: check-gate.sh P3 exec 传 $TASK_DIR / P3-tdd.md:42 写 check-tdd-red.sh $TASK_DIR / 结论: ALIGNED
A2/脚本→文档: check-tdd-red.sh 探测链 TEST_RUNNER→P3→pytest→exit3 / P3-tdd.md:50 文档化探测链 / state-machine.md:290 文档化 / 结论: ALIGNED

A3a/连锁: P0 删除 pruning_tendency → 已传播到 P0-orchestrator/state-machine/dispatch-protocol/task-files/architect / 结论: ALIGNED
A3a/连锁: gate_commands.P3 新增 → 已传播到 P2-design/architect/task-files/P3-tdd/check-tdd-red/state-machine/verifier / 结论: ALIGNED
A3a/连锁: minimal_validation 强制声明 → 已传播到 P2-design/architect/task-files/dispatch-prompt/dispatch-protocol/plan-eng-review / 结论: ALIGNED
A3a/连锁: office-hours 触发条件改 → 已传播到 P2-design/role-system/review-mapping/dispatch-protocol / 结论: ALIGNED

A3b/反向传播: dispatch-protocol.md:200 phase_hint 缩进改为 2 空格但周围 YAML 块用 3 空格缩进 / 结论: NEEDS_HUMAN_REVIEW（YAML 缩进不一致，可能是 diff 引入的格式 bug）
A3b/反向传播: WORKFLOW.md 阶段总览表 P0 门槛仍写"含 debug_env + known_risks" / 未提及四字段 / 结论: 已检查，WORKFLOW.md:216 写的是 debug_env+known_risks 不是字段计数，语义可接受但未同步四字段术语
A3b/反向传播: orchestrator-template.md 未在 diff 列表中 / 检查是否有五字段/pruning_tendency 引用
A3b/反向传播: LIMITATIONS.md 未在 diff 列表中 / 检查是否有 pruning_tendency 引用
A3b/反向传播: analyst.md 未在 diff 列表中 / 检查是否有 pruning_tendency 引用
A3b/反向传播: implementer.md 未在 diff 列表中 / 检查是否有 pruning_tendency 引用
A3b/反向传播: test-designer.md 未在 diff 列表中 / 检查是否有 pruning_tendency 引用
A3b/反向传播: rules/state-transitions.md 未在 diff 列表中 / 检查是否有 P2 不可裁剪+review 引用
A3b/反向传播: CONTEXT.md 未在 diff 列表中 / 检查是否有四字段/pruning_tendency 引用

A3b/反向传播: dispatch-protocol.md:200 phase_hint 缩进从 3 空格→4 空格（删除 pruning_tendency 时引入），与 env_constraints 的 3 空格不一致 / 但这是 Markdown 代码块内的示例，不被脚本解析 / 结论: NEEDS_HUMAN_REVIEW（cosmetic）
A3b/反向传播: WORKFLOW.md:216 P0 门槛写"含 debug_env + known_risks"未改四字段 / 但语义仍正确（debug_env 是 env_constraints 的子字段，known_risks 是四字段之一）/ 结论: ALIGNED（语义可接受，术语未同步但无误导）
A3b/反向传播: analyst.md/implementer.md/test-designer.md/orchestrator-template.md/LIMITATIONS.md/CONTEXT.md/rules/state-transitions.md 均无 pruning_tendency/五字段引用 / 结论: ALIGNED
A3b/反向传播: rules/state-transitions.md P2 不可裁剪引用 / 检查是否有"P2 未被裁剪时"措辞
A3b/反向传播: CHANGELOG.md 未在 diff 中 / 检查是否有 v0.25.0 条目

A6/锚点表: CHECK 9 锚点表无 gate_commands.P3 专门锚点 / 现有锚点"TDD 红灯检查"只检查 check-tdd-red.sh 含"pytest"关键词 / gate_commands.P3 是新增功能，非协议规则硬约束 / 结论: ALIGNED（P3 键是可选功能，不需要专门锚点；check-tdd-red.sh 仍含"pytest"关键词，现有锚点仍通过）
A6/锚点表: check-gate.sh P2 review 不存在→exit 1 / 无专门锚点 / 但"P2 agent=main 硬拦截"锚点仍覆盖 check-gate.sh P2 分支 / 结论: ALIGNED
A6/锚点表: P0 四字段 / 无专门锚点（P0 gate 是 exit 2，不检查字段）/ 结论: ALIGNED

A4/测试覆盖: check-gate.bats G2.13 改为 exit 1 + 新增 PG.P2REVIEW 测试 P2-review 不存在→exit 1 / 结论: ALIGNED
A4/测试覆盖: check-tdd-red.bats 新增 TDD.G1-G5 覆盖 gate_commands.P3 自动读取 / 结论: ALIGNED
A4/测试覆盖: fixtures.bash 新增 add_p2_review helper / 结论: ALIGNED
A4/测试覆盖: pre-commit-hook.bats 新增 P2-review.md fixture / 结论: ALIGNED
A4/测试覆盖: bats 全量实跑 476 tests passed 0 failed / 结论: ALIGNED

A5/下游影响: P2 review 不存在→exit 1 是破坏性变更（原来 exit 2 跳过检查）/ 但 P2 评审本就不可裁剪，语义上 review 文件必须存在 / 结论: ALIGNED（行为变更但不违反协议语义）
A5/下游影响: gate_commands.P3 可选键 / 新增功能，向后兼容 / 结论: ALIGNED
A5/文档传播: CHANGELOG [Unreleased] 有 pruning_tendency 移除条目 / 但无 P2.49(gate_commands.P3) 和 P2.50(措辞加固) 条目 / 结论: NEEDS_HUMAN_REVIEW（CHANGELOG 遗漏新变更条目）

A7/ADR-001(隔离性): P4 自查节改"P5 由主 Agent 派发 verifier subagent 执行"更符合隔离性 / 结论: ALIGNED
A7/ADR-002(可判定性): P2 review 不存在→exit 1 是可判定门槛 / 结论: ALIGNED
A7/ADR-003(最小约定/技术栈无关): gate_commands.P3 增强技术栈无关性 / 结论: ALIGNED
A7/ADR-005(改动性质判断): pruning_tendency 移除消除与 risk_level 重复 / 结论: ALIGNED

A1/最终: P4-implementation.md:50 "派发 verifier subagent 执行" vs dispatch-protocol.md:516 "派发 verifier subagent 从 P2-design.md 读取" vs dispatch-prompt.md:99-100 简化版无 verifier subagent 引用 / 三处语义一致但措辞不同 / 结论: ALIGNED（模板简化版是设计选择，完整版在阶段卡片和 dispatch-protocol）
A2/最终: check-gate.sh:39 P0 提示"四字段" vs state-machine.md:76 "四字段" vs P0-orchestrator.md:11 "四字段" / 结论: ALIGNED
A3a/最终: "亲自执行"定义统一: P4 自查节改 "派发 verifier subagent 执行" / P6 自查节改 "主 Agent 亲自跑 gate 脚本" / 两处区分了"派 subagent"和"主 Agent 跑 gate" / 结论: ALIGNED
