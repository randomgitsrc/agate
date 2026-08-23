# P4-dispatch-context-implementer-batchC-migration — TAG0022 C 批（RM-AG0038 M2 迁移闭环）

> 派发对象：implementer（P4 实现，batch C-migration，**最大体量批**）。这是本轮的强制指令，不是参考信息。
> 任务目录：`{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/`

## 目标

实现 **RM-AG0038（BDD-3/4/5）**：把 `check-gate.py` 的协议规则类 md 解析（P1 §4.2 A/B/C/D 组）迁移到结构化读取（agate_common 共享读取器 + agate-md-field-get op）+ S-1~S-6 收紧（S-3 双向 gate 命令一致性）。**验收：P3 红测试转绿（test_md_parse_scan.py / S-3a/S-3b 漂移用例）+ 全量既有用例不回归。**

## C 批文件集（本批独占，不跨批写入）

1. `agate/scripts/check-gate.py` — 解析层重构（A/B/C/D 组迁出；**gate_p1 的 judge 校验块留给 B 批，本批不碰 judge 逻辑**）
2. `agate/scripts/agate_common.py` — 新增共享读取器（B/C/D 组单点，对齐 `parse_gate_commands_block` 模式）
3. `agate/scripts/agate-md-field-get.py` — KNOWN_OPS 注册新 op（status/agent/project_phase/code_map_new_files_count/code_map_reviewed_count/**created**）
4. `agate/scripts/check-structure-consistency.py` — S-3 收紧（S-3a/S-3b）+ S-4 已知字段表补新 op
5. `agate/rules/phases.yaml` — 各阶段 `gates[].check` 增补实际 gate 命令串
6. `agate/tests/unit/test_md_parse_scan.py` — 按迁移后实际状态校准（若共享读取器落点使模式清单需微调，与测试契约一致时允许）

## 逐点映射清单（P2 §4.2.1，实证行号；按此执行）

| 组 | 现解析点（check-gate.py） | 迁移目标 | 要点 |
|----|--------------------------|---------|------|
| A | `_frontmatter_field` L164-170 定义 + **9 处调用（NB-6：L500/506/716/722/768/799/805/1108/1109）** | 全部改走 `_md_field_get`（新注册 op status/agent/project_phase/code_map_new_files_count/code_map_reviewed_count） | 删除 `_frontmatter_field`；L799/805 是 gate_p4 的 P4-review status/agent 读点，**勿漏**；code_map_* 走 NO_FALLBACK_INT_FIELDS（解 DESIGN_GAP 遗留 L1098-1107） |
| B | `_NC_RE/_SUGGEST_RE/_NO_NEED_RE/_NC_DESC_RE/_SUGGEST_DESC_RE/_SUGGEST_TAIL_BT_RE/_SUGGEST_TAIL_BRACKET_RE` L101-110 + 计数 L523-584 | agate_common 共享 `count_markers(text, kind)` + 描述提取 | 逐字节同正则；SELF-GATE 检查清单不破 |
| C | BDD 标题 L390 / UI 区块 L417-462 / candidate_count L693-694 / design_trivial L703 / 权衡 L736 / P6 行首 L946-954 / P7 L1015-1023 / DESIGN_GAP L1048-1088 / CODE_MAP L1127-1135 / fail-list L875-887 / known-failures 表 L909 / P4 关键词 L1060 | agate_common 共享读取器（extract_bdd_titles / parse_ui_design_section / scan_fm_line / count_p6_pass_fail / count_p7_markers / count_design_gap / count_code_map_lines / parse_fail_list_block / count_kf_entries / has_keyword） | 新格式路径保持 `_md_field_get`；判定口径不变（N5：退出码语义/CLI 契约/OLD_PHASE 回退检测不改） |
| D | 内嵌 yaml 块 `re.finditer(r"```(?:yaml\|yml)...")` L336-338 | agate_common `extract_embedded_yaml_blocks(text)` | 同正则单点；`_gate_p1_vision_capability` 走共享 |

**E/F 组（.state.yaml 读取 L230-241/gate_p65 L982-983、git/CHANGELOG 解析 L1162-1230）不动**（D2 口径不计入零 md 解析面）。

## S-3 收紧（P2 §4.2.2 + NB-1/NB-2 + TG-1）

- **既有 S-3 outputs/orphan/exec_role 检查全部保留**（含「产出规格缺失 P2-review.md → 非 0」用例——test_check_structure_consistency.py 既有用例须保持绿）；S-3a/S-3b 是**叠加**子检查，不是重定义（NB-1）
- S-3a（YAML→md）：phases.yaml `gates[].check` 命令串须在对应卡片 `## gate 规则`（或推进条件）节出现；P6.5 无独立卡片 → 沿用既有「无卡片阶段跳过」（NB-2，`_phase_card_path` 对 P6.5 返回 None）
- S-3b（md→YAML）：卡片 `## gate 规则` 节机器可判定命令行（匹配 `check-gate.py P\d+` / `gate_commands.P\d+` / `check-[\w-]+\.py` 模式）须在该阶段 gates[].check 声明
- phases.yaml 命令串增补：P1→`check-gate.py P1 $TASK_DIR`、P5→`gate_commands.P5` 等（P2 §4.2.2 数据面）；**M6 数据增补 + R4 基线核对**（10 张卡逐一核对，卡片确实缺命令串时补卡片——md 侧对齐 YAML 正是收紧语义）
- BDD-5 单侧漂移：卡片加红线行不入 YAML → S-3b ERROR；改 YAML gate 命令不动卡片 → S-3a ERROR；双侧一致 → exit 0（P3 测试已固化为用例）
- S-4 已知字段表（`_TASK_FRONTMATTER_FIELDS`）同步补 status/agent/project_phase/code_map_*（防 S-4 误报）

## 约束（硬约束）

1. **行为逐字节等价（NB-3 口径）**：对 well-formed frontmatter + 既有 1202 用例全绿承诺等价；畸形/带引号 frontmatter 边界允许差异（方向 = fail-closed 或更正确，不产生假 PASS）。迁移是机械但面广——每改一组跑一次目标测试确认不回归
2. **不改判定口径**：check-gate.py 的退出码语义（0/1/2 + OLD_PHASE 回退）、CLI 契约、P0/P3/P4/P5/P8 分支判定逻辑不变（N5）；只换读取方式
3. **不碰 judge 逻辑**：gate_p1 的 judge 校验块是 B 批范围；本批重构 gate_p1 解析层时保持现有 judge 相关代码（gate_p65 等）逐字节不动
4. **双轨向后兼容（H10/R3）**：共享读取器保留旧格式正文回退 → conftest create_task_dir 旧夹具语义不变（预计 conftest 零改动）
5. **禁改范围外文件**：dispatch.yaml/state-machine.md/P1 卡/test_check_gate.py 等 = B 批范围，一律不碰
6. **SELF-GATE**：本批全为 `agate/scripts/*.py`（触发面）——commit message 由主 Agent 处理 self-gate 声明；你在 P4-implementation.md 记录触发面清单
7. 环境：Linux；/tmp 只读（pytest `--basetemp=/home/kity/oclab/dsh-workspace/ptmp -p no:cacheprovider`）；bash 一律 timeout；双工作区纪律；count-tests 只增不减

## 验证（自查≠gate）

- 每次改完一组：`python3 -m pytest agate/tests/unit/test_md_parse_scan.py agate/tests/unit/test_check_gate.py agate/tests/unit/test_check_structure_consistency.py -q -p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp`（bash 加 timeout）——红转绿 + 既有不回归
- 全量自查（P5 才做正式 gate）：`python3 -m pytest agate/tests/ -q -p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp`（timeout 600）
- `python3 agate/scripts/check-structure-consistency.py`（S-* 全绿）
- `python3 agate/scripts/check-protocol-consistency.py --strict-errors-only`（worktree 自己的）
- count-tests 不漂移

## 输入文件（读 P2-design.md 相关节 + 现状代码，勿全仓扫描）

- `{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/P2-design.md`（§4.2 逐点映射 + §4.2.2 S-3 + §1.1 M2-M6 + §7 files_to_read）
- `{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/P2-review.md`（NB-1/2/3/6 + TG-1）
- `{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/P3-test-cases.md`（契约注解 §5）
- 现状代码（files_to_read 清单：check-gate.py 全文 / agate_common.py L769-805 样板 / agate-md-field-get.py / check-structure-consistency.py / phases.yaml / 相关测试）

## 产出

1. 上述 6 文件实际改动
2. `{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/P4-implementation.md`：Header + `implementation_dir:` + 新增文件核对表（新增 test_md_parse_scan.py → CODE-MAP 处理；无其他新增）+ 迁移摘要（逐组 A/B/C/D 结果）+ 自查结果（各 gate 命令输出）

## 分阶段落盘

每完成一组迁移/每次自跑，追加写 `{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/P4-progress.md`。

## 返回给我

只返回两行：① P4-implementation.md 路径 + 改动文件清单；② 一句话摘要（迁移结果 + 红转绿数）。绝不返回文件全文。
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
UI/前端等需构建任务：单元测试全绿不代表可用，implementer 在 P4 完成后应构建并确认 dist 等构建产物存在，不能只跑单元测试就认为完成。

## 生产环境隔离
任何写入生产环境/生产数据库/生产 API 的操作都必须先 PAUSED 报告人工。
```

## 产出规格

- P4-implementation.md 必须声明 `implementation_dir: {实际路径}`
- 代码文件在声明的目录下
- 遵守 P2-design.md 的方案设计 + 现有项目代码规范

## 新增文件核对表

> 仅当项目已采用骨架（`P2-skeleton.md` 存在）或 CODE-MAP（`{AGATE_WORKSPACE}/agents/CODE-MAP.md`
> 存在）机制时填写；未采用则本节可省略。

implementer 为本阶段**每个新增文件**填一行：

| 新增文件路径 | 骨架归属 | CODE-MAP 处理 |
|------------|---------|--------------|
| {path} | `within <dir>` / `[SKELETON_DEVIATION: 理由]` | `[CODE_MAP_UPDATED]` / `[CODE_MAP_EXEMPT: 理由]` |

- **骨架归属列**：新增文件落在骨架声明的目录内 → `within <dir>`；落在骨架外 → 标
  `[SKELETON_DEVIATION: 理由]`（不阻断，供 P7 核对）
- **CODE-MAP 处理列**：新增文件已同步更新 `agents/CODE-MAP.md` → `[CODE_MAP_UPDATED]`；判断
  该文件不需要更新 CODE-MAP（如临时/测试脚手架）→ `[CODE_MAP_EXEMPT: 理由]`

`change_type: refactor` 同样适用本表（不因换用回归口径而豁免）。

## 评审派发（C8 机械映射）

**在 P4 实现完成后、gate 前**，按 P1 声明的 domains 和 risk_level 派评审。C8 映射表是机械规则，不靠判断"需不需要"：

| domain | 派哪些评审 | 产出 |
|--------|----------|------|
| backend | review | P4-review.md |
| frontend | design-review | P4-review.md |
| mcp | review（关注 MCP 接口契约）| P4-review.md |
| security | cso | P4-review.md |
| risk=high | P4 实现评审（按 domains 派 review/design-review/cso；P2 plan-eng-review 已审方案，P4 实现评审不可省）| P4-review.md |
| full（tier=full 或声明 ceremony: full）| P4 实现评审（按 domains 派 review/design-review/cso，同 risk=high 不可省；P2 plan-eng-review 已审方案）+ cso（security 域）+ P7 不可裁（full 档任务 P7 为强制阶段）| P4-review.md |

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
- WARNING（不改变 exit code）：骨架/CODE-MAP 机制已采用（P2-skeleton.md 或 agents/CODE-MAP.md 存在）但缺「新增文件核对表」标题

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
