# P1 progress (analyst)

- [x] 读 dispatch-context（P1-dispatch-context-analyst.md）：范围=候选数/裁剪类字段迁移到 frontmatter，gate_commands 暂留正文；硬约束 5 条；风险 high/medium-high；BDD 须覆盖"写坏格式→gate 拦截"
- [x] 读角色定义（analyst.md）+ P0-brief.md + AGENTS.md：结构 1-7 节 + BDD 反模式自检 + [NO_NEED_CONFIRM] 行首声明
- [x] 读 HANDOFF-V2.0.md：scope 决策（gate_commands 留正文）、双读、CHECK 9 锚点、语义真实性边界、普通 merge 禁 squash
- [x] 读可行性评估 /tmp/opencode/feasibility.md：40+ 字段现状、Option A 优于 B、Phase1 迁移集、10 项风险、6.3 硬约束
- [x] 读现状代码：agate-md-field-get.py（核心改造点：3 个正则 op）、agate-state-yaml-check.py（校验器范式）、check-gate.sh（P1/P2 分支 grep 读取）、check-pruning.sh（10 处 grep）
- [x] 读模板 task-files.md（P1/P2 产出格式权威）+ architect.md 角色卡 + WORKFLOW.md 需求验收机制
- [x] 验证测试基线：worktree count-tests.sh = 594（sanity 6 另计）；CHECK 9 锚点表含 ui_affected/NEED_CONFIRM/DESIGN_GAP 等旧关键词
- [x] 写 P1-requirements.md 完成
- [x] 自检：BDD-1..15 连续无跳号；[NO_NEED_CONFIRM] 行首声明；无阻塞 [NEED_CONFIRM]；无 status: GAP；risk_level=high/phases 全 8 阶段/packages=[agate]/domains=[backend,cli]
- [x] 过当前 gate：check-pruning.sh exit=0（v0.35 可解析）

## 修复轮（analyst，round 2）逐条落盘

- [FIND-1 已应用] §3 隐含需求 1 补判别契约（frontmatter 含迁移字段→新格式严格校验；不含→旧格式回退不触发必填校验，BDD-6/9 Given 互斥）；BDD-6 Given 收紧为"新格式文件（frontmatter 含迁移字段集）缺必填字段"。
- [FIND-2 已应用] "33 条"→"37 条"三处：§2 F10 摩擦表、§3 隐含需求 3、BDD-13 Then。实测 SCRIPT_ALIGNMENT_ANCHORS=37（check-protocol-consistency.py:446-634）。另发现 P0-brief.md:24/57 仍写"33 条"，属 P0 旧数字，本任务只改 P1 不碰 P0，在此报告。
- [FIND-3 已应用] BDD-15 工具清单补 agate-gate-p5-count.py（4 个工具），Then 改"四个工具"；§1 不迁移清单同补 4 个工具名以保持一致。已核实 agate-gate-p5-count.py:14 含 ^gate_commands: 正则。
- [FIND-4 已应用] §3 隐含需求 9/10/11 注明验证载体（9→P4/P5 实现验证+changelog；10→P8 流程；11→P0 env_constraints）。
