---
phase: P1
generated_by: agate-inject-card.sh + 主 Agent
task_id: TAG0010-python-migration
role: analyst
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
产出 {AGATE_WORKSPACE}/tasks/TAG0010-python-migration/P1-requirements.md：agate 产品逻辑 Python 化的需求基线。核心工作不是翻译需求，而是**先做全量影响面梳理（同类扫描）**——把 30 个 sh 的调用关系、文档引用、consistency 锚点关键字完整映射表画出来，作为 BDD 与 P2 设计的输入。用户明确：不愿意一轮一轮来回改，P1 必须一次把影响面摸全。

### 约束
- **范围锁定**（P0-brief 已确认，不可扩张）：30 个 sh → py（hook 入口保留 sh 薄壳）；gate-result.sh + agate-workspace-resolve.sh → agate_common.py；阶段一**不做协议文档全量重写**（文档/CI 同步归 TAG0011），但**必要的引用同步**（dispatch/hook/git-integration/platform-notes Windows 章节/UPGRADING）计入范围。
- **hook 保留 sh 薄壳是硬约束**：git 在 Windows 通过 Git Bash 的 sh.exe 执行 hook；`#!/usr/bin/env bash` 总能解析而 `#!/usr/bin/env python3` 不可靠（Windows 命令名是 python 非 python3）；复制模式 `.agate-root` 恢复必须留在薄壳。约 15 行/个（shebang + AGATE_ROOT 自定位 + 复制模式恢复 + exec python）。
- **consistency 锚点约束**：check-protocol-consistency.py CHECK 8/9 锚点表硬编码 `.sh` 路径与关键字（如 `check-gate.sh` 含 `P2 不可裁剪`/`NEED_CONFIRM`、`check-pruning.sh` 含 `coupling_checklist`）——py 版脚本必须保留这些关键字或同步更新锚点表，否则 consistency 报 ERROR。**P1 必须产出锚点关键字完整映射表**（sh 路径 → py 路径 → 保留关键字），供 P2/P4 执行。
- **编码规范**：所有 py 显式 `encoding="utf-8"`（Windows Python 文本默认 ANSI 代码页 cp1252/cp936，否则 88d0deb 根因复发）——列为 gate 规则。
- **Python 版本下限 3.8+**：新代码避免 3.9+/3.10+ 语法（match、str.removeprefix 等）。
- **pyyaml 从可选变强制依赖**：所有 gate 逻辑依赖——SETUP.md 明确 pip install pyyaml，纳入 CI。
- **hook 入口 exec 失败回退**：hook 薄壳加"python 探测 + 失败回退"；保留 sh 逻辑作为 fallback。
- **验收标准 5 条**（分析报告 §9）：①全量 bats（bats 调 py）全绿 ②consistency 0 ERROR（--strict）③ruff 静态检查 py 代码 ④Windows CI 冒烟通过 ⑤平台假设扫描器**扩展覆盖 .py**（现只扫 .bats/.bash/.sh，对 py 失明——必须先扩展规则集）。
- **测试回归**：阶段一逐脚本迁移 + 每步全量 bats 验证；不批量重写。约 30-40 个 bats 用例需随脚本迁移同步改断言（check-platform-assumptions.bats 17、env-adapt-docs.bats 9、agate-scripts-encoding.bats 2、helpers-python.bats 3、agate-workspace-resolve.bats 若干——这些专门断言 sh/python 接口与 bash 行为），P1 需识别这些受影响测试。
- 不掺入解决方案设计（P1 只定义"要解决什么"和"做完什么样算对"）；BDD 可二值判定。

### 上游关联
- P0-brief.md 已锁定（交接单 + 分析报告已定稿）：任务 = 30 个 sh → py，hook 保留 sh 薄壳；分析报告 docs/reviews/agate-python-migration-analysis-20260814.md §9 立项建议 + 5 条验收标准是需求输入的权威来源。
- 现状事实（分析报告 §2）：agate 已是"sh 薄壳 + py 逻辑"混合架构，19/30 个 sh 退出路径落在 python；无 bash-only 不可移植特性（0 个关联数组）；`[[ ]]` 7 个、数组 5 个、readarray 1 个、local 12 个。
- 函数库依赖（分析报告 §2.3）：gate-result.sh（105 行）被 pre-commit-gate/check-tdd-red/agate-capture-env-baseline 3 个脚本 source；agate-workspace-resolve.sh（57 行）被 pre-commit-gate/check-debt/agate-migrate-workspace 3 个脚本 source——Python 化等价物 = agate_common.py。

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0010-python-migration/P0-brief.md（主 Agent 任务简报和风险声明——P1 主要输入）
- {project_root}/docs/reviews/agate-python-migration-analysis-20260814.md（定稿分析报告，§9 验收标准、§10 数据表）
- {project_root}/AGENTS.md（项目开发约定：测试约定、改脚本工作流、dogfooding 工作流）
- {project_root}/agate/scripts/（30 个 sh + 18 个 py 全量清单——按需读取具体脚本核实调用关系）
- {project_root}/agate/scripts/check-protocol-consistency.py（CHECK 8/9 锚点表——P1 必须读取核实锚点关键字）
- {project_root}/agate/tests/（按需读取受影响测试文件，识别需同步改断言的用例）
- {agate_root}/WORKFLOW.md（需求与验收机制）

### 产出要求
P1-requirements.md 必须含：
1. 需求复述（结构化重写原始需求）
2. 隐含需求识别（每维度过：数据/前端/多端/边界/兼容）
3. **影响面映射表（核心交付）**：
   - 表 A：30 个 sh 全量清单（文件名/行数/角色分类：纯 bash 11 个 vs 混合 19 个/被谁 source/调哪些 py/调哪些 git）
   - 表 B：文档引用映射（哪个文档引用哪个 .sh 路径 → 迁移后的 py 路径或薄壳）
   - 表 C：consistency CHECK 8/9 锚点关键字映射（sh 路径 → py 路径 → 保留关键字）
   - 表 D：受影响 bats 测试清单（文件/用例数/需改什么断言）
   - 表 E：迁移批次划分建议（按依赖关系分批，每批 bats 绿）
4. BDD 验收条件（≥1 条，Given/When/Then，可二值判定——建议覆盖：迁移后 bats 仍绿、consistency 0 ERROR、ruff 通过、Windows 冒烟、扫描器覆盖 .py）
5. 待确认清单（拿不准标 [NEED_CONFIRM] 或 [SUGGEST: 推荐 X，理由 Y]；无则写 [NO_NEED_CONFIRM]）
6. 裁剪说明 + frontmatter 机器字段（risk_level/phases/packages/domains/capability_requirements）
</dispatch_guide>

<!-- AGATE_CARD_START -->
## 当前阶段卡片：P1

路径：phase-cards/P1-requirements.md
---
# P1 — 需求基线

> 当前状态：[首次 / 重试 #N]
> P1 不可裁剪（核心阶段）

## 如果是首次进入本阶段

1. 派发 analyst subagent → 产出 P1-requirements.md
   1.1 写 P1-dispatch-context-analyst.md（派发指引：目标/约束/上游关联/输入文件 + 客观查证信息）
2. 主 Agent 确认：BDD 验收条件 ≥1 条 + 无未决 NEED_CONFIRM
2.5 派发 requirements-review subagent（角色文件：{agate_root}/assets/review-roles/requirements-review.md）
     2.5.1 写 P1-dispatch-context-requirements-review.md（派发指引：目标/约束/上游关联/输入文件 + 客观查证信息）
    输入：P1-requirements.md
    产出：P1-review.md（agent≠main，含 BDD 编号引用 + 覆盖维度标注）
    review 不通过 → analyst 修改 → 再 review → … → approved（⑩迭代循环）
3. 预跑 check-gate.sh P1（exit 2，主 Agent 自判）
4. git add {AGATE_WORKSPACE}/tasks/{Txxx}/（含 .state.yaml + 产出文件，若 .gitignore 忽略需 git add -f）
   ⚠️ 此时 .state.yaml 的 phase 保持 P1，不要提前写 P2——phase = 本 commit 的产出阶段
5. git commit -m "wf({Txxx}-P1): {摘要}"（phase=P1，P1 产出含 P1-requirements.md + P1-review.md）
6. P1 commit 完成后进入 P2：**phase 推进 P2 随 P2 产出 commit 一起**（P2-design.md + P2-review.md 就绪后），不是单独 phase commit

## 如果是重试

确认上一轮失败原因（BDD 不完整 / domains 声明错 / NEED_CONFIRM 未处理）
→ review 不通过时：analyst 修改需求 → 重派 requirements-review → 共享 retry 预算
→ 读 agate/rules/state-transitions.md 确认 retry 上限（P1 MAX=3）

## 前置条件

- [ ] P0-brief.md 完成（四字段齐全）

## 派发

- **角色**：analyst（`{agate_root}/assets/execution-roles/analyst.md`）
- **输入**：P0-brief.md（env_constraints / known_risks / executor_env）
- **输出**：P1-requirements.md
- **派发 prompt 模板**：`{agate_root}/assets/templates/dispatch-prompt.md`

## 产出规格

P1-requirements.md 必须包含：
- BDD 验收条件（至少 1 条，Given/When/Then 格式）
- `domains:` 声明（backend / frontend / mcp / security）
- `packages:` 声明（受影响的包/模块）
- `risk_level:` 声明（low / medium / high）→ 决定 P2 评审强度
- `phases:` 裁剪声明（跳过哪些阶段 + 理由）
- `capability_requirements:` 能力需求声明（available / supplementable / GAP 三态）
- 无未决 `[NEED_CONFIRM]`（有则 PAUSED）；无待确认项时写 `[NO_NEED_CONFIRM]`

`risk_level`/`phases`/`packages`/`domains` 写在文件头 **frontmatter**（`---` 分隔块），不写正文。
**可直接复制的完整样例**：
```yaml
---
phase: P1
task_id: TAG0001           # 替换为实际任务编号
type: problems
parent: P0-brief.md
trace_id: T001-P1-20260101 # {task_id}-P1-{YYYYMMDD}
status: draft
created: 2026-01-01
agent: analyst
# ── v2.0 机器字段 ──
risk_level: low             # low / medium / high，必填
phases: [P1, P4, P5, P6, P8]   # list of P\d+，必填
packages: [pkg-a]           # list，必填
domains: [backend, frontend]  # list，必填
# 可选字段：override / implicit_coupling / coupling_checklist / internal_only /
# internal_only_reason / 跳过风险 / design_trivial / follows_existing_pattern
# ── v2.0 refactor 任务类型声明（可选，缺省 = 功能任务）──
# change_type: refactor   # 当前仅支持 refactor；枚举非法值由 frontmatter schema 拦截
# ── v2.0 标记"已解决/已确认"状态（可选，仅标记存在时写）──
# need_confirm_resolved: []   # list[str]：已解决的 NEED_CONFIRM 项描述（逐条匹配正文）
# suggest_resolved: []        # list[str]：已采纳的 SUGGEST 项描述
# scope_resolved: []          # list[str]：已解决的 SCOPE+ 项描述
---
```

**NEED_CONFIRM 分级**：
- `[SUGGEST: 推荐 X，理由 Y]` - 有倾向但求确认。主 Agent 可自行采纳倾向（除非涉及破坏性变更/业务方向），不必问用户
- `[NEED_CONFIRM]` - 真无方向需人定夺。阻塞推进，主 Agent 问用户

## gate 规则

check-gate.sh P1 → P1-review.md 存在 + status:approved + agent≠main + 含 BDD 编号锚点 → exit 2（BDD 编号格式为 `#### BDD-NN:`）；缺 P1-review.md / agent=main / 无锚点 → exit 1
P1 评审不可裁——所有任务都走独立 requirements-review，无例外

## 推进条件（全部满足才写 phase: P2）

- [ ] P1-requirements.md 含 BDD ≥1 条
- [ ] domains / packages / risk_level / phases 已声明
- [ ] 无 [NEED_CONFIRM] 标记
- [ ] 无 status: GAP（supplementable 不阻，GAP 阻）
- [ ] P1-review.md status: approved（agent≠main，含 BDD 编号锚点）

## 常见错误

1. **BDD 写成技术实现而非用户行为**：BDD 应该描述"用户能看到什么/系统应该做什么"，不是"调用哪个 API"
2. **domains 声明不全**：漏了某个受影响域 → P2 不派该域的评审 → 实现方向错误
3. **capability_requirements 漏声明**：P6 验收时才发现需要但不可用的能力 → 返工
4. **gate 不过 ≠ 你失败了**：红灯指向工作/设计的问题，不指向你。正确动作是诊断→退回/重试/PAUSED，不是修改产出让它变绿。

## 下游影响

- P2 设计依赖 domains + risk_level 决定评审角色
- P6 验收逐条对照 P1 的 BDD（PASS/FAIL 总数必须 ≥ P1 BDD 总数）
- P7 一致性检查依赖 packages 声明做跨文件交叉核对

## 评审

P1 评审通用必有（所有任务都走 requirements-review），P2/P4 评审是 C8 域触发（见 review-mapping.md）——二者在"是否通用"上不对称，仅在"独立 subagent、agent≠main"上类比。P1 评审不可裁剪。
review 不通过 → analyst 修改需求 → 再 review（⑩迭代循环），直至 approved。

> 完成 → 读 phase-cards/P2-design.md


## P1 基线保护

P1-requirements.md 是需求基线，后续阶段（P2-P8）不应直接修改。如需变更（如 P4 发现 BDD 矛盾需补充注释），必须：
1. 主 Agent 显式批准
2. 在变更处标注 `[BASELINE_CHANGE: 理由]`
3. 不改 BDD 的 Given/When/Then 语义（只补充注释/优先级说明）
<!-- AGATE_CARD_END -->

<objective_info>
- 环境：Linux；python3 3.12.3 + pyyaml 6.0.3 + ruff 0.16.3（~/.venvs/agate-dev/）；bats 1.10.0
- 开发工具：~/.agate = 稳定版 v0.45.0（软链 → /home/kity/oclab/agate/agate），禁止改动；worktree agate/ = 改造对象
- worktree 根：/home/kity/oclab/agate/.worktrees/agate-TAG0010；任务目录：{AGATE_WORKSPACE}/tasks/TAG0010-python-migration/
- 脚本清单已核实：agate/scripts/ 下 30 个 .sh + 18 个 .py（check-protocol-consistency.py 841 行是最大 py 单文件；check-gate.sh 488 行 + pre-commit-gate.sh 404 行是最重两个 sh）
- 测试基线：733 bats 全绿 + consistency 0 ERROR（--strict）
- 任务数据：TAG0010（phase=P0，P0-brief 已锁定）；TAG0011 依赖本任务完成后启动
</objective_info>
