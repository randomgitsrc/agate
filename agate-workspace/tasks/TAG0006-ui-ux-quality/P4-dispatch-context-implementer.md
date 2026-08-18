---
phase: P4
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0006
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
实现 agate UI/UX 验收质量机制（含 SCOPE+ 增补：UI/UX 覆盖任意渲染形态），让 P3 的 53 个新增测试从红灯变绿灯（不修改测试本身），并产出 P4-implementation/。

### 约束
1. **本任务是 agate 协议本体增强**（dogfooding 双工作区）：改代码在 worktree（/home/kity/oclab/agate/.worktrees/agate-TAG0006/），**禁止动主 checkout（/home/kity/oclab/agate）与 ~/.agate**。改动对象 = worktree 内 `agate/` 下的协议文档 + gate 脚本。
2. **实现范围（按 P2-design.md 方案 A + SCOPE+ 增补）**：
   - **Gate 脚本**（agate/scripts/）：
     - `check-gate.py`：gate_p1 新增 `_gate_p1_vision_capability`（domains 含 frontend → 校验 capability_requirements 视觉条目 + status 三态）+ `_gate_p1_ui_shape`（形态声明合法性：shape 存在维度空 → exit 1；维度非框架且未声明使用 → exit 1；双字段缺失 → 通过）；gate_p2 新增 `_gate_p2_ui_design_section`（ui_affected:true → 校验 UI 设计节标题 + 渲染形态声明 + 布局/交互/视觉关键词或渲染正确性/时序锚点 + P1-P2 形态一致性规范化值比对）
     - `check-p6-evidence.py`：avg-hash 雷同从 WARNING 改为"降级待复核"判定（有复核记录放行 exit 0/2、无记录 exit 1；md5 硬阻断不变）+ 雷同判定按"同 BDD 证据组（bdd-id 前缀）"分组豁免相邻帧/时序截图（-tN 与 frames/ 同权）+ GAP 分支证据检查（人工复核记录文件存在性）
     - `check-p6-provenance.py`：R1b 增加 GAP 放宽（P1 视觉 status=GAP → 截图 PASS 不强制 vision YAML，改为要求人工复核记录被引用；无声明默认 available 语义不变）
     - `agate-frontmatter-check.py`：P1 schema 增可选键 `ui_render_shape`（str）/`ui_ux_dimensions`（list）；P2 schema 增可选字段 `ui_design_section`（bool）
     - `agate-md-field-get.py`：新增 op `ui_render_shape` / `ui_ux_dimensions`（参照 ui_affected op 模式）
     - `check-protocol-consistency.py`：新增一致性规则（analyst.md/P1 卡片含分类框架+UX 类别 BDD 要求；plan-design-review.md 含视觉设计/交互设计/渲染正确性维度；verifier.md/P6 卡片含三态分档/输入态复核/证据按形态选择条文）
     - 抽取公共 helper（agate_common.py 新增 `read_vision_tri_state(p1_file)`，三处复用——DEBT0005 建议）
   - **协议文档**（agate/ 下 .md，按 P2 §6 影响面核对清单逐文件落实）：analyst.md（分类框架 + 形态声明 + UX BDD 要求 + 反模式清单）、architect.md（UI 设计节产出职责 + 结构规格）、verifier.md（三态分档双证据 + 输入态复核 + 证据按形态选择 + 视觉质量 checklist）、vision-analyst.md（能力自查）、requirements-review.md（UX/vision 评审要点）、plan-design-review.md（七维 + 渲染正确性与时序维度）、P1/P2/P6 阶段卡片（对应条文）、dispatch-protocol.md（A3 扩展 + gate 表 + 证据段）、dispatch-prompt.md（能力自查节 + supplementable 注入位）、task-files.md（P2/P6 模板）、role-system.md（不新增 designer）、LIMITATIONS.md（局限 7 缓解）、scripts/README.md（脚本说明）
3. **改脚本走 TDD**：先跑 P3 测试确认红灯 → 改脚本 → 确认绿灯；不修改测试本身（测试是契约）。
4. **验收标准**：全量 878 tests（825 基线 + 53 新增）目标全绿；check-protocol-consistency 0 ERROR；count-tests 计数无漂移（新增用例只增不减，≥749 单调不减）。
5. **平台无关原则**：脚本改动不引入 Unix 假设；测试已用 tmp_path/importorskip("PIL") 包裹。
6. **不写死视觉工具**：文档条文与脚本不得绑定 vision-engine/WebGL/Canvas 等具体工具/技术栈（仅可作"举例"出现）；形态分类是开放集合（layout/render_component/temporal_effects 为规范值）。
7. **兼容策略（P2 §10）**：新检查只对新声明生效（domains=frontend / ui_affected=true / 形态字段存在）；既有 fixtures 无新字段 → 布局型默认，825 基线不红。
8. **SELF-GATE**：本次改动触发 SELF-GATE（agate/*.md + scripts/*.py），commit message 需含 self-gate-review: 或 self-gate-skip:。
9. **DESIGN_GAP/SCOPE+/CLARIFY 协议**：实现中发现 P2 设计歧义 → [DESIGN_GAP: ...]；发现新隐含需求 → [SCOPE+]；对方案疑问 → [CLARIFY: ...]；prompt 漏了 P2 已声明的事 → [SCOPE_GAP]。均报告主 Agent，不擅自处理。
10. **自查≠gate**：写完自跑测试（自查），但自查通过 ≠ P5 gate 通过；不要声称"P5 已过"。

### 上游关联
- P1-requirements.md：17 BDD（含 SCOPE+ BDD-16/17）。
- P2-design.md（759 行，含 SCOPE+ 增补 + 修复轮闭合）：§2.1-2.16 逐 BDD 三件套 + §6 影响面核对清单（46 文件）+ §7 files_to_read（19 项）+ §10 兼容策略 + §11 断言。
- P3-test-cases.md + 测试代码（53 新增用例：test_vision_1~4、test_shape_1~5、test_ui_design_1~9、test_vision_gap_1~2、test_vision_avail_1、test_vision_none_1、test_vision_docs_1~3、test_ahash_1~3、test_time_seq_1、test_review_role_docs.py 14 用例等）。
- P2 gate_commands：P3/P5/P6 = `python3 -m pytest -q --tb=no agate/tests/`（P3 已从 collect-only 修复）。
- DEBT0005（三态解析重复）：建议抽公共 helper read_vision_tri_state。

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0006-ui-ux-quality/P2-design.md（方案设计——主输入：§2 三件套 + §6 影响面 + §7 files_to_read）
- {AGATE_WORKSPACE}/tasks/TAG0006-ui-ux-quality/P1-requirements.md（17 BDD 需求基线）
- {AGATE_WORKSPACE}/tasks/TAG0006-ui-ux-quality/P3-test-cases.md（测试用例清单）
- {AGATE_WORKSPACE}/tasks/TAG0006-ui-ux-quality/P0-brief.md（任务简报）
- {project_root}/agate/assets/execution-roles/implementer.md（角色定义）
- {project_root}/agate/assets/execution-roles/architect.md、verifier.md、analyst.md（改这些文档时参考）
- {project_root}/agate/scripts/check-gate.py、check-p6-evidence.py、check-p6-provenance.py、agate-frontmatter-check.py、agate-md-field-get.py、check-protocol-consistency.py、agate_common.py（改动对象）
- {project_root}/agate/phase-cards/P1-requirements.md、P2-design.md、P6-acceptance.md（改动对象）
- {project_root}/agate/assets/templates/dispatch-prompt.md、task-files.md（改动对象）
- {project_root}/agate/dispatch-protocol.md、state-machine.md、rules/state-transitions.md、role-system.md、WORKFLOW.md、LIMITATIONS.md（改动对象）
- {project_root}/agate/tests/conftest.py（fixture helpers）

> 输入多但均为方案 §6/§7 已明确的改动点——按 files_to_read 导航改，不全文通读。产出 P4-implementation/ + 代码改动。
</dispatch_guide>

<!-- AGATE_CARD_START -->
## 当前阶段卡片：P4

路径：phase-cards/P4-implementation.md
---
# P4 — 代码实现

> 当前状态：[首次 / 重试 #N / 裁剪跳阶]
> 裁剪跳阶 → 确认 P1 phases 不含 P4 且有合规理由（check-pruning.py 已检查）→ 跳过，读 P5 卡片

## 如果是首次进入本阶段

0. 跑 `agate-capture-env-baseline.py $TASK_DIR`（自动捕获环境基线）。
   该步骤不会阻塞流程——任何 stderr 输出（含 WARNING）均可忽略，直接继续步骤 1，
   无需查看结果、无需判断、无需因为看到 WARNING 而停下来处理。
1. 派发 implementer subagent → 产出代码文件
   1.1 写 P4-dispatch-context-implementer.md（派发指引：目标/约束/上游关联/输入文件 + 客观查证信息）
2. 按 P2 的 gate_commands 跑单元测试（非 gate，只是自查）
3. 按 C8 映射表派发评审（见下方）
4. 预跑 check-gate.py P4（确认暂存区有代码文件）
5. git add {AGATE_WORKSPACE}/tasks/{Txxx}/ + 代码文件（含 .state.yaml，若 .gitignore 忽略需 git add -f）
   ⚠️ 此时 .state.yaml 的 phase 保持 P4，不要提前写 P5——phase = 本 commit 的产出阶段
6. git commit -m "wf({Txxx}-P4): {摘要}"（phase=P4，P4 产出含 P4-implementation.md + 代码文件）
7. P4 commit 完成后进入 P5：**phase 推进 P5 随 P5 产出 commit 一起**（P5-test-results/ 就绪后），不是单独 phase commit

## 如果是重试

确认上一轮失败原因（来自 gate 输出 / review rejected 理由）
→ 只修复失败项，不重做已通过的部分
→ 修复后重跑全量测试（T027 教训：修复可能引入回归）
→ 读 agate/rules/state-transitions.md 确认 retry 上限（P4 MAX=3）

**若这次是从 P6（或其他更后的阶段）退回来的**：`{AGATE_WORKSPACE}/tasks/{Txxx}/` 下不会再有旧的 P6-acceptance.md（已被归档），但当初具体是哪条 BDD 失败、失败原因是什么，会摘要在 `{AGATE_WORKSPACE}/tasks/{Txxx}/.retreat-history.md` 里——**重新派发 implementer 时，dispatch-context 必须引用这份摘要**，不能让 implementer 只看到"现有代码"却不知道具体要修哪里。已有代码不会被撤销、也不需要重新实现，是在已有实现基础上定向修复。**回退落地后必须建 DEBT 条目**（`source: retreat`，`evidence` 引用 retreat 提交哈希，模板 `assets/templates/tech-debt-template.md`——TAG0001 强制，见 `agate/rules/state-transitions.md` 回退规则节）。

## 前置条件

- [ ] P2-design.md 存在且 files_to_read 字段完整（导航清单）
- [ ] P2-review.md status: approved（P2 不可裁剪）
- [ ] P3-test-cases.md 存在（测试已设计）
- [ ] check-tdd-red.py 确认红灯（测试先于实现）
- [ ] 未跳过 P4（如有裁剪理由，见上方裁剪跳阶）

## 派发

- **角色**：implementer（`{agate_root}/assets/execution-roles/implementer.md`）
- **输入**：P2-design.md（files_to_read 导航 + gate_commands）+ P3-test-cases.md + P0-brief.md（env_constraints）
- **输出**：代码文件（在 P4-implementation.md 声明的 implementation_dir 下）
- **派发 prompt 模板**：`{agate_root}/assets/templates/dispatch-prompt.md` + 以下阶段特定追加：

```
## 上下文控制
读取代码文件以 P2-design.md 的 files_to_read 清单为准，按需读取（标了行号范围的只读片段）。
不要在项目里盲目搜索或整目录全读。

## 自查≠gate
写完代码后应自跑测试确认基本功能（自查），但自查通过 ≠ P5 gate 通过。
P5 由主 Agent 派发 verifier subagent 执行 gate_commands.P5，主 Agent 验 gate（检查产出 + failed 计数 + N5 最小校验）。
不要在返回中声称"P5 已过"或"全部测试通过"——只返回路径 + 摘要。

## 生产环境隔离
任何写入生产环境/生产数据库/生产 API 的操作都必须先 PAUSED 报告人工。
```

## 产出规格

- P4-implementation.md 必须声明 `implementation_dir: {实际路径}`
- 代码文件在声明的目录下
- 遵守 P2-design.md 的方案设计 + 现有项目代码规范

## 评审派发（C8 机械映射）

**在 P4 实现完成后、gate 前**，按 P1 声明的 domains 和 risk_level 派评审。C8 映射表是机械规则，不靠判断"需不需要"：

| domain | 派哪些评审 | 产出 |
|--------|----------|------|
| backend | review | P4-review.md |
| frontend | design-review | P4-review.md |
| mcp | review（关注 MCP 接口契约）| P4-review.md |
| security | cso | P4-review.md |
| risk=high | P4 实现评审（按 domains 派 review/design-review/cso；P2 plan-eng-review 已审方案，P4 实现评审不可省）| P4-review.md |

多个评审角色 `专家组并行` → 所有返回后派组长汇总 → 统一 P4-review.md（status: approved / rejected）。
详见 `agate/rules/review-mapping.md`。

**并行派发**（多个评审角色时）：
1. 同时派发所有触发的评审 subagent（每个一个 task 调用）
   > **操作方式**：在一个 assistant 消息中连续发起多个 task 工具调用（每个评审角色一个）。
   > 不要等前一个 task 返回再发下一个——那是串行，不是并行。
   > 平台会并行执行多个 task，全部返回后再进入下一步（派发组长汇总）。
2. 每个评审 subagent 各写一个 dispatch-context + 各自产出文件
3. 所有评审返回后，派发组长汇总 subagent（角色：review + 指定为「专家组组长」）
4. 组长产出：P4-review.md。**agent 字段必须非 main**（与 P2 评审同规则，check-gate.py 在 P2 分支硬拦截 agent=main 的 approved）
5. 组长规则：不发表新意见，只汇总；任何 BLOCKER → rejected；分歧 → 交人工；全票无 BLOCKER → approved

**单评审角色时**：直接派发，无需组长汇总，产出直接写 P4-review.md。

review 不通过 → implementer 修改代码 → 再 review → … → approved（⑩迭代循环，review 和 gate 重试共享 retry 预算）

## 按包拆分并行（条件触发，需额外约束）

> 仅当 P2 packages > 1 且包间无依赖时适用。单包任务跳过本节。
> 并行上限 / 失败批 retry / 共享文件统一后处理见 dispatch-protocol「派发编排机制」并行规则。

当 P2 声明多个 packages 且包间无数据依赖时，P4 可拆分并行，但**有额外约束**：

1. 每个 package 派一个 implementer subagent
2. **各 implementer 只改自己 package 目录下的文件**——跨包的共享文件（类型定义、接口、配置）由主 Agent 在所有并行 implementer 返回后统一处理
3. 各自返回路径 + 摘要
4. 主 Agent 汇总后统一 commit
5. 主 Agent 在所有 implementer 返回后，统一处理共享文件改动（如果有）

**冲突预防**：
- dispatch-context 约束节必须写明：`只改动 {pkg}/ 目录下的文件。共享文件（{列出}）不在本次改动范围内`
- 如果某个 implementer 必须改共享文件 → 该包不能并行，改为串行（主 Agent 先派其他包并行，再串行处理含共享改动的包）
- 无法确定是否有共享改动 → 串行（安全默认值）

**基础设施隔离（并行时强制）**：
- debug server 端口：每个 implementer 的 dispatch-context 约束节分配不同端口（如 pkg-a: 3001, pkg-b: 3002）
- 测试数据库：每个 implementer 用独立数据库路径（如 `test-{pkg}.db`），不共享同一 test.db
- 环境变量：dispatch-context 写明各 subagent 独立的环境变量值（如 `PORT=3001` vs `PORT=3002`）
- 临时文件：各 subagent 写入 `P4-implementation/{pkg}/` 独立目录

主 Agent 在并行派发前**必须**为每个 subagent 的 dispatch-context 分配上述隔离参数。当前无 gate 脚本检查（已知缺口），但未分配导致运行时冲突（端口占用/数据库锁）时计为重试，不算环境问题。

## gate 规则（check-gate.py 会跑）

```bash
check-gate.py P4 $TASK_DIR
```

- **exit 0**：暂存区含非 md/yaml 代码文件（git diff --cached --name-only）
- **exit 1**：暂存区仅 .md/.yaml 文件（无实际代码变更）→ 不能推进

## 推进条件（全部满足才写 phase: P5）

- [ ] 暂存区含代码文件（非 .md/.yaml）
- [ ] 按 C8 映射表触发的评审全部完成：P4-review.md status: approved（所有任务都要求——risk=high 的 P2 plan-eng-review 审方案，P4 实现评审按 domains 另行派发，不可省）
- [ ] SCOPE+ 已处理（若本阶段产生）：P1-requirements.md 有 [SCOPE_RESOLVED]（行首声明格式）
- [ ] git commit 完成

## 常见错误

1. **不读 files_to_read，在项目里乱翻**：implementer 拿到 P2 的 files_to_read 清单后应按清单阅读，不要在项目里全文搜索或整目录全读——上下文会爆炸
2. **自行加范围外改动**：发现需要做但不在 P1 范围内的改动 → 标 [SCOPE+]（行首声明格式）而非直接做
3. **只跑单元测试不验证集成**：单元测试全绿 ≠ 功能可用。P5 会跑 gate_commands 做技术验证，但要确保实现时路径依赖的端点行为已验证
4. **先更新 .state.yaml 再 commit**：state 和产出在同一 commit 里——不要先 commit 产出再单独 commit state
5. **gate 不过 ≠ 你失败了**：红灯指向工作/设计的问题，不指向你。正确动作是诊断→退回/重试/PAUSED，不是修改产出让它变绿。

## 下游影响

- P5 验证依赖：P5 跑 gate_commands.P5 的命令（在 P2 声明），确保你的实现能通过
- P6 验收依赖：实现路径的端点行为必须可验证（确认 API 返回正确的 Content-Type、状态码等）
- 代码改动文件路径：P8 发布时确认版本文件变更需要知道你改动了哪些 package

> 完成 → 读 phase-cards/P5-verification.md

6. **修改 P1 文档**：P4 发现 BDD 矛盾时标 DESIGN_GAP，不直接改 P1-requirements.md。需变更 P1 时标 `[BASELINE_CHANGE: 理由]` 并经主 Agent 批准。
<!-- AGATE_CARD_END -->

<objective_info>
- 测试现状：53 新增用例全部红灯（B 类断言失败：gate 检查函数/文档条文未实现），全量 878 收集。
- check-gate.py 现状：gate_p1（196 行起）/gate_p2（337 行起）结构；`_md_field_get`/`_frontmatter_field` 模式可复用。
- check-p6-evidence.py 现状：avg-hash WARNING（250-262 行附近）、md5 去重、像素方差检测；证据类型 R1a 判定（156-171 行 os.walk）。
- check-p6-provenance.py 现状：R1b vision YAML 审计（277-313 行）。
- 基线：825 pytest 全绿 + consistency 0 ERROR；PIL 已装（测试用 importorskip 保持平台无关）。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。