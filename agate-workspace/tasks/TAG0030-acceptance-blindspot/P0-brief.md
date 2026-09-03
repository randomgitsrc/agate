# P0-brief — TAG0030 验收盲区机制批（RM-AG0057 + DEBT0024/0025/0026）

> 本文件由主 Agent 亲自填写（P0 阶段产出）。来源：TPV0095 复盘（RM-AG0057，验收盲区 4 类）+ TAG0027 复盘（DEBT0024-26，协议测试约定）。
> 五处都落在"协议卡/评审角色/派发模板/测试约定"文档面（P1/P3/P6 卡 + plan-design-review.md + dispatch-context 模板）——**同文档面合并单 task**（避免 5 处分别改同一批卡文件触发 5 轮回归）。

## task

"补强 agate 协议验收盲区机制（RM-AG0057 + DEBT0024-26）：① **测试副作用/环境还原 gate（RM-AG0057-①）**——BDD 只有正向路径，创建型 E2E（建团队/条目）跑完不清理累积污染共享环境，P6 验收全 PASS 时环境尚干净、残留验收后才暴露（协议 P3 只有测试前失败基线 capture-env-baseline，无测试后残留检查/清理钩子要求）；② **P1 人工体验路径验收节（RM-AG0057-②）**——排除 seed/数据改动时 BDD 全用 fixture 验收，'用户按文档 seed 后页面应有内容'成隐性无人验路径；③ **plan-design-review 形态驱动化 + 布局方案 ≥2 候选必审（RM-AG0057-③）**——形态机制（ui_render_shape：layout/render_component/temporal_effects → 维度选择 → 按形态 checklist → 可量化判据）已在 P1 analyst/P2 architect/gate 全链落地，但评审角色文件 plan-design-review.md 未接形态体系（固定 7 维评分 + 一行条件启用，无'按受评形态加载维度组'），布局方案 ≥2 候选不下沉 UI 层（'行 vs 卡'无必审）；④ **视觉契约断言收录（RM-AG0057-④）**——'dropdown ≥ trigger'类可量化协调性无 BDD 表达机制，收录为可表达子集（E2E DOM 度量断言）；⑤ **TAG0027 复盘三连（DEBT0024/25/26）**——P3 测试夹具走真实 gate 语义（不 mock 假 exit）；新 CHECK 上线前先全量扫描存量；单 agent 大任务派发前评估体量拆小。"

### scope

- **Phase 1（测试副作用/环境还原 gate，RM-AG0057-①）**：P3 卡补"创建型测试清理钩子"要求（创建即注册、无条件删除、接受 200/204/404——afterEach 清理队列模式）；P6 补 post-test 环境残留检查步骤（快照比对或清理钩子验证）；dispatch-context 模板补对应要求
- **Phase 2（P1 人工体验路径验收节，RM-AG0057-②）**：P1 卡/analyst 角色补"人工体验验收"节——凡涉及用户可见页面且数据源（seed）影响其内容，强制补"Given seed 数据 → 页面有内容"BDD
- **Phase 3（plan-design-review 形态驱动化，RM-AG0057-③）**：`plan-design-review.md` 改形态驱动评分——先读受评任务 `ui_render_shape` 再加载对应维度组评分细则（布局型 → 布局/交互/视觉三组；渲染组件型 → 渲染正确性/动效时序）；每个启用维度要求布局方案 ≥2 候选 + 权衡（架构级 candidate_count 下沉 UI 布局层）；渲染组件型评审 checklist 对接 architect 渲染正确性 checklist
- **Phase 4（视觉契约断言收录 + TAG0027 三连，RM-AG0057-④ + DEBT0024/25/26）**：视觉契约断言（DOM 度量：宽度/高度/对齐/重叠/溢出）收录为可表达子集，P2 视觉 checklist/P6 指南提及；P3 测试夹具真实 gate 语义要求（DEBT0024）；新 CHECK 上线前全量扫描流程（DEBT0025）；大任务拆小派发指引（DEBT0026，核对 TAG0028 自主再派发落地后的剩余缺口）
- **测试**：协议文档改造类以 consistency 0 ERROR + 全量 pytest 回归为验收；涉及模板/卡的 checklist 新增以 grep 断言审计锁定（TAG0027 批量改动 TDD 策略）

### out-of-scope

- 实现级 E2E 清理逻辑本身（peekview teams-page.spec.ts 已自行落地——本任务只把模式收进协议卡/模板，不写具体项目 spec）
- plan-design-review 评分权重/数值调整（只加形态驱动结构，不改 0-10 权重语义）
- gate 命令解析器（DEBT0027/RM-AG0056/DEBT0023——归 TAG0029）
- check-gate.py 健壮性（DEBT0016/17/18——归 TAG0031）

## known_risks

- "卡文件批量改动回归面：P1/P3/P6 卡 + plan-design-review.md + dispatch-context 模板同批改，触发多轮 consistency/pytest——用 grep 断言审计单测锁定新增要求（TAG0027 批量 TDD 策略），避免每处单独 TDD"
- "形态驱动化改动 plan-design-review.md 是评审角色行为变更：须保持既有 0-10 评分输出格式（门槛读 status 字段），只加形态分组的内部逻辑；评审角色文件与 P1/P2 形态声明的对接靠读受评文件，无声明时回落布局型默认"
- "视觉契约断言是概念新增：须明确'可表达子集'边界（只收可量化 DOM 度量，不收主观视觉），避免 P2/P6 指南产生'所有视觉都必须断言'的误解"
- "DEBT0026 与 TAG0028 自主再派发（§4 子任务拆批）的边界：外部拆小（派发前）是现状兜底，内部自主拆（subagent 运行时）是 TAG0028 交付方向——本任务只补派发模板的默认指导，不重复实现"

## env_constraints

- 本任务改 `agate/phase-cards/*.md`（P1/P3/P6）+ `agate/assets/review-roles/plan-design-review.md` + `agate/assets/templates/dispatch-context.md` + `agate/assets/execution-roles/analyst.md` → **触发 SELF-GATE**，commit message 须含 `self-gate-review:` 或 `self-gate-skip:`
- 用系统 python（`/usr/bin/python3`）跑 pytest/pyyaml；ruff 用 `~/.venvs/agate-dev/bin/ruff`
- 基线验证用 `--strict-errors-only`（DEBT0012）；编排/派发类工具用 `~/.agate` 稳定版
- 协议文档变更（卡/角色/模板）须跑 `check-protocol-consistency.py` 确认无 ERROR

## executor_env

- worktree：`.worktrees/agate-TAG0030`（分支 `feat/TAG0030-acceptance-blindspot`），构建流程见 `docs/guides/worktree-dogfooding-guide.md`，交接单 `HANDOFF-TAG0030.md` 按模板全 9 节填写
- 任务目录：`agate-workspace/tasks/TAG0030-acceptance-blindspot/`
- **merge 模式**：完成 PR 后由主 Agent 综合 merge（三路并行 TAG0029/30/31 之一，文件域与另两路不重叠）
