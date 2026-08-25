---
phase: P1
task_id: TAG0024
type: problems
parent: P0-brief.md
trace_id: TAG0024-P1-20260825
status: draft
created: 2026-08-25
agent: analyst
# ── v2.0 机器字段 ──
risk_level: medium
ceremony: standard
phases: [P1, P2, P3, P4, P5, P6, P6.5, P7, P8]
packages: [agate-scripts, agate-rules, agate-docs, agate-tests]
domains: [backend]
# 跳过风险: 无跳过——本任务未裁剪任何阶段（见下方「裁剪说明」）
# ── v2.0 标记"已解决/已确认"状态（首次产出，留空）──
need_confirm_resolved: []
suggest_resolved: []
scope_resolved: []
---

P0-brief 时效性已核对：立项日期（2026-08-25）与本次启动同为 2026-08-25，无跨会话间隔，判定"已核对，无漂移"（沿用 dispatch-context 已给结论，本 agent 复核一致）。

[NO_NEED_CONFIRM]

## 1. 需求复述

本任务是一次"工具链/协议卫生"合并批（5 项 issue 同批推进），共同点是消除 agate 协议本体的写入摩擦与文档自洽缺陷，均不改变现有 gate 判定语义：

1. **RM-AG0048（一期）**：新增 `agate-md-field-set.py`（结构化字段写入 CLI）+ `agate-md-field-set-gate-commands.py`（gate_commands 正文 YAML 块专用写入子命令），把"手写 frontmatter"升级为"CLI 写入即校验"，key 白名单化、value 与 check-gate 同源校验、格式由工具生成；证据字段（pass/fail/blocker_count 等）一期拒绝写入；不改变 `check-gate.py`/`check-events.py` 的判定逻辑。
2. **DEBT0019**：`check-gate.py._check_roadmap_done()` 用固定索引 `split("|")` 解析 roadmap.md 表格，未校验列数是否精确匹配表头列数——描述列含字面 `|` 时列可能整体错位但仍满足 `len(cols)>=8`，导致误读 rm_id/status/related_task。修复为列数完整性校验，不改变既有合法表格的判定结果。
3. **DEBT0020**：同函数调用点 `gate_p8()` 用相对当前工作目录的硬编码路径拼接 roadmap.md，非仓库根锚定；CWD 不在仓库根时该路径不存在，检查被静默跳过（不报错）。修复为仓库根锚定定位（或给出区分性提示）。
4. **RM-AG0049**：`phases.yaml` 的 P4 `outputs` 未列出 `P4-review.md`，但 `check-gate.py.gate_p4()` 实际要求其存在且 `status: approved` 且 `agent≠main`——YAML 声明与脚本实际要求不对称。修复为补全 `outputs` 声明并核对 `check-structure-consistency.py` S-1/S-2 双向一致性。
5. **RM-AG0050**：`phases.yaml` 把 P6.5 列为与 P4/P5/P6/P7/P8 平级的独立阶段条目；`state-machine.md` 明确其为"挂载于 P6→P7 转移的强门槛子阶段，非独立 phase 值"——两处对 P6.5 性质的定位表述不一致。修复为统一表述口径（以 state-machine.md 为准），且不改变 `check-gate.py`/`check-judge-verdict.py` 现有判定行为。

## 2. 隐含需求识别

按维度快速过一遍：

- **数据**：roadmap.md / phases.yaml 现有数据本身不需要迁移（DEBT0019/20 只改解析健壮性，不改文件格式；RM-AG0049 只补 YAML 声明字段，不改既有任务的 `.state.yaml`/产出文件）。
- **前端**：无（本任务不涉及 UI/渲染，`domains` 不含 frontend）。
- **多端**：agate 本身无 MCP server 层（协议消费方式是 subagent 直接执行 CLI 脚本），`agate-md-field-get.py` 与新增的 `agate-md-field-set.py` 是同一 CLI 层的读/写两面，不存在需要另外同步的第二端。但存在一个容易漏做的隐含依赖：**dispatch-context 模板与 dispatch-prompt 模板必须同步改为"引导使用 set 工具"**（design note §3.2/§3.3 已声明，P0-brief RM-AG0048 issue 描述也明确列入），否则新工具做出来了但 subagent 不知道用，等于白做——已转为 BDD-19，不是隐含新增范围，只是把 P0-brief 已锁定的这部分显式验收化。
- **边界**：roadmap.md 表格空文件/无 `RM-` 前缀行/`task_id` 为空 的既有豁免行为（`_check_roadmap_done` 现有文档已声明"无匹配返回 None，不误拦"）必须在 DEBT0019/20 修复后保持不变（BDD-21 覆盖）；set 工具侧的边界（文件不存在/无 frontmatter/正文残留旧字段/写入中断）均在 design note §5.5-§5.7 有声明，已转为 BDD-10~13。
- **兼容**：RM-AG0048 不得改变 `check-gate.py`/`check-events.py` 判定逻辑（BDD-29）；DEBT0019/20 不得改变既有合法 roadmap.md 的判定结果（BDD-21/BDD-24，回归覆盖 TAG0023 的 P8 roadmap 回写校验 BDD）；RM-AG0049/50 不得改变 `check-gate.py`/`check-judge-verdict.py` 的既有判定行为（BDD-26/28）。

## 3. 同类扫描（强制节，三条线索逐条做实）

### 线索1：grep `agate-md-field-get.py` 全部 op，核对 RM-AG0048 set 白名单是否对齐 get 读取面

**扫描动作**：完整读取 `agate/scripts/agate-md-field-get.py`（269 行），统计 `KNOWN_OPS` 全部字段集合。

**命中结果**：`KNOWN_OPS` 共 **38 个 op**，分 9 组：
- `BOOL_FIELDS`（3）：`ui_affected` / `internal_only` / `design_trivial`
- `LIST_FIELDS`（6）：`phases` / `packages` / `domains` / `coupling_checklist` / `follows_existing_pattern` / `ui_ux_dimensions`
- `INT_FIELDS`（1）：`candidate_count`
- `STRING_FIELDS`（5）：`override` / `internal_only_reason` / `跳过风险` / `risk_level` / `ui_render_shape`
- `NO_FALLBACK_INT_FIELDS`（9）：`pass` / `fail` / `blocker_count` / `deviation_count` / `deviation_critical_count` / `design_gap_count` / `design_gap_reviewed_count` / `code_map_new_files_count` / `code_map_reviewed_count`
- `NO_FALLBACK_LIST_FIELDS`（5）：`need_confirm_resolved` / `suggest_resolved` / `scope_resolved` / `mechanism_issues` / `execution_issues`
- `NO_FALLBACK_BOOL_FIELDS`（2）：`regression_pass` / `feedback_ready`
- `NO_FALLBACK_STRING_FIELDS`（6）：`change_type` / `ceremony` / `status` / `agent` / `project_phase` / `created`
- `JSON_FIELDS`（1）：`dispatch_plan`

**逐条判定**：
- `design-md-field-set.md` §8 一期范围明确列举的字段（`risk_level`/`ui_affected`/`candidate_count`/`status`/`packages`/`domains`/`gate_commands` 正文块）**本次处理**——设计已覆盖，转入 BDD-1~8。
- `NO_FALLBACK_INT_FIELDS`（9 个）+ `NO_FALLBACK_BOOL_FIELDS` 的 `regression_pass`（1 个，`feedback_ready` 属 retrospective.md 非任务阶段文件不在本工具适用范围）——**本次处理，明确拒绝写入**：这些是"由验证脚本产出的证据字段"，design note §5.10 已声明一期拒绝端，转入 BDD-9。
- `LIST_FIELDS`/`STRING_FIELDS`/`NO_FALLBACK_STRING_FIELDS` 中除 §8 已列举以外的其余声明字段（`phases`/`coupling_checklist`/`follows_existing_pattern`/`ui_ux_dimensions`/`override`/`internal_only_reason`/`跳过风险`/`ui_render_shape`/`internal_only`/`design_trivial`/`change_type`/`ceremony`/`project_phase`/`created`）——**本次处理**：这些都是"任务作者在 frontmatter 中主动声明的协议字段"，性质与已列举字段相同（属 `phases.yaml task_fields` ∪ `task-files.md` 通用 Header 并集），design note §6.1 的白名单定义本身写的是开放式"...`（risk_level/candidate_count/packages/domains/ui_affected/...`），未穷举不代表排除。**[SUGGEST: 建议 P2 把 set 白名单定义为"task-files.md 通用 Header ∪ phases.yaml 各阶段 task_fields 的完整并集"这一机械规则，而非照抄 design note 插图式的字段子集列表，避免因为设计文档举例不全导致实现时遗漏部分声明字段——同源铁律本身要求全集覆盖，理由明确、不涉及破坏性变更、不涉及业务方向，故用 SUGGEST 不阻塞]**，转入 BDD-17。
- `NO_FALLBACK_LIST_FIELDS` 的 `need_confirm_resolved`/`suggest_resolved`/`scope_resolved`（追加语义，换行连接，由主 Agent/后续 subagent 追加已解决项描述）与 `mechanism_issues`/`execution_issues`（retrospective.md 归因分类字段，同样换行连接）、以及 `JSON_FIELDS` 的 `dispatch_plan`（P1 复杂编排场景的结构化 JSON，P2-design.md §3.1 声明）——**本次不处理，理由**：这三组字段的写入语义（追加而非覆盖 / 自由散文换行元素 / 嵌套 JSON 结构）都不适配 design note §5.1.1 定义的"简单 list 空格覆盖"或"gate_commands 专用块整体替换"两种既有形态，design note §8 一期范围列表也未提及它们，说明这是设计遗留边界而非本次锁定范围内的实现细节，若强行塞进一期会引入"覆盖语义与实际追加/JSON 语义不匹配"的新一类写入 bug，风险不对称。**转为一期明确拒绝端（与证据字段拒绝同模式，只是拒绝理由不同：证据字段"不该由 agent 写"，这三组是"一期写入形态不支持，非禁止语义"），BDD-18 覆盖，不构成范围外改动。**
- 追加 grep 定位（辅助验证判定）：`need_confirm_resolved`/`suggest_resolved`/`scope_resolved` 仅出现在 `agate/phase-cards/P1-requirements.md` 注释与 get 工具本身，无独立消费脚本；`mechanism_issues`/`execution_issues` 消费于 `agate/scripts/agate-feedback.py`（retrospective 模板专用字段）。均确认为非本次 RM-AG0048 一期核心目标（P1/P2 声明字段）。

**回归拦截**：白名单来源改为"机械并集规则"（BDD-17）本身就是拦截手段——未来 `phases.yaml` 新增 `task_fields` 时，set 白名单自动覆盖，不需要每次手工加列表项，防止同类不对称复发。

### 线索2：grep roadmap.md 表格解析的全部消费点，核对 DEBT0019 修复是否需要同步到其他消费点

**扫描动作**：
```
grep -rln 'split("|")' agate/scripts/*.py   → 1 个文件命中：agate/scripts/check-gate.py
grep -rln 'roadmap' agate/scripts/*.py      → 3 个文件命中：check-gate.py / check-protocol-consistency.py / check-retrospective.py
```

**命中清单与逐条判定**：
- `agate/scripts/check-gate.py`（第 1181-1202 行 `_check_roadmap_done()`）：`cols = [c.strip() for c in line.split("|")]` 后仅校验 `len(cols) < 8` 跳过——**本次处理**，这正是 DEBT0019 的目标函数。
- `agate/scripts/check-retrospective.py`（第 76、84-88 行）：也读取 `roadmap.md`，但用 `re.search(ROADMAP_TASK_ID_RE_TEMPLATE...)` 做整段正则存在性匹配，**不做按列索引的表格解析**，不受"列错位"缺陷影响——**本次不处理，理由**：解析方式与 DEBT0019 描述的缺陷机制无关，不构成同类实例。
- `agate/scripts/check-protocol-consistency.py`（第 575、577 行）：仅以字符串 `"_check_roadmap_done"` 作为一致性检查的关键词引用（校验文档是否提及该函数名），不含任何表格解析逻辑——**本次不处理，理由**：非消费点，只是文档-代码一致性检查的锚点。

**结论**：**已确认只此一处**——`check-gate.py._check_roadmap_done()` 是仓库内唯一按固定列索引解析 roadmap.md 表格的消费点，DEBT0019 的列数校验修复不需要同步到其他文件。

### 线索3：grep P6.5 定位的全部消费点，供 P2 设计影响面梳理承接

**扫描动作**：`grep -rln 'P6\.5\|P6_5' agate/scripts/*.py agate/*.md agate/rules/*.yaml agate/phase-cards/*.md`

**命中结果**：共 **18 个文件**：
- 脚本（8）：`agate_common.py` / `check-events.py` / `check-gate.py` / `check-judge-verdict.py` / `check-protocol-consistency.py` / `check-structure-consistency.py` / `ci-gate-backstop.py` / `pre-commit-gate.py`
- 文档/规则（10）：`AGENTS.md` / `dispatch-protocol.md` / `LIMITATIONS.md` / `role-system.md` / `state-machine.md` / `UPGRADING.md` / `WORKFLOW.md` / `rules/dispatch.yaml` / `rules/phases.yaml` / `phase-cards/P6-acceptance.md`

**关键定位发现（供 P2 承接，不在 P1 处理）**：
- `agate/scripts/agate_common.py:666` `_DEFAULT_PHASE_IDS = frozenset({"P0"..."P8", "P6.5"})` 与 `agate/rules/phases.yaml:88`（`id: P6.5`）都把 P6.5 结构化为与 P0-P8 平级的 phase-id 集合成员；`agate/scripts/check-gate.py:1322` 的 `handlers` 字典同样把 `"P6.5"` 当 CLI 阶段参数分发（`check-gate.py P6.5 $TASK_DIR`）。
- `agate/state-machine.md`（第 74/152 行）明确区分了两个不同语义维度：`.state.yaml` 持久化的 `phase` 字段值（不含 P6.5，卡在 P6 直至 P7）与 CLI/脚本内部使用的"阶段式调用标签"（含 P6.5，用于 gate 分发和文件命名前缀）。RM-AG0050 要统一的表述冲突，本质是 **`phases.yaml` 结构声明层没有区分这两个维度**，导致读者以为 P6.5 是与其他阶段完全等价的独立阶段。
- `check-judge-verdict.py`（第 2-32 行）、`check-structure-consistency.py`（第 11/117/196/305 行，S-2 检查显式把 `P6.5` 作为特例前缀纳入表格行解析正则）、`ci-gate-backstop.py`、`pre-commit-gate.py` 均以"P6.5 是有专属产物/专属 gate 函数但非独立 `.state.yaml phase`"的口径一致工作，说明**脚本层实现本身语义是自洽的**，不一致仅存在于 `phases.yaml` 的结构声明措辞层面。

**结论**：清单已列出（18 个文件，含 8 个脚本消费点的具体行号定位），供 P2 architect 在设计"统一 phases.yaml 表述口径"方案时逐一核对是否需要同步调整；P1 不修改代码，按 dispatch-context 要求到此为止。

## 4. BDD 验收条件

### RM-AG0048（一期）：agate-md-field-set 结构化写入工具

#### BDD-1: 合法 key 与合法 value 写入成功且可被读回
- Given 一个已存在的任务产出文件（如 P2-design.md）
- When 用 `agate-md-field-set` 写入一个合法 key（如 `packages`）与合法 value
- Then 写入返回成功，`agate-md-field-get` 对同一 key 能读回同一值，且 `check-gate.py` 对应阶段该字段相关检查通过

#### BDD-2: 非法 key 被拒绝
- Given 一个已存在的任务产出文件
- When 用 `agate-md-field-set` 传入一个不在白名单内的 key（如 `risks_level`）
- Then 命令 exit 非 0，且输出中包含合法 key 清单

#### BDD-3: 非法 value 被拒绝
- Given 一个已存在的任务产出文件
- When 用 `agate-md-field-set` 给合法 key 传入非法值（如 `status Approve`）
- Then 命令 exit 非 0，输出中包含合法值枚举、字段归属角色、下一步建议

#### BDD-4: 角色越权写入被拒绝
- Given 一个 frontmatter `agent` 字段声明为非 review 角色的文件
- When 用 `agate-md-field-set` 尝试写入仅限 review/judge 角色的字段（如 `status: approved`）
- Then 命令 exit 非 0，输出提示该字段归属角色

#### BDD-5: --list 输出与阶段 schema 一致
- Given 一个已进入某阶段（如 P2）的任务产出文件
- When 执行 `agate-md-field-set --list`
- Then 输出包含该阶段（依据 `phases.yaml` task_fields）应填字段清单、当前值、缺失项，且清单与 `phases.yaml` 声明一致

#### BDD-6: 写入后报告剩余缺失
- Given 一个尚缺部分必填字段的任务产出文件
- When 用 `agate-md-field-set` 成功写入其中一个字段
- Then 命令输出中包含"剩余缺失"字段清单（而非仅报告"写入成功"）

#### BDD-7: gate_commands 正文块写入与解析
- Given 一个已声明 gate 阶段的 P2-design.md
- When 用 `agate-md-field-set-gate-commands` 写入一个合法 YAML 块
- Then `parse_gate_commands_block` 能正确解析该块，且 `check-gate.py` 对应阶段该字段相关检查通过

#### BDD-8: gate_commands 非法块被拒绝
- Given 一个已声明 gate 阶段的 P2-design.md
- When 用 `agate-md-field-set-gate-commands` 写入一个含未声明 key 或非法 `_timeout_seconds` 的块
- Then 命令 exit 非 0，输出可操作的错误提示（说明哪个 key/值非法）

#### BDD-9: 证据字段一期拒绝写入
- Given 任意任务产出文件
- When 用 `agate-md-field-set` 尝试写入证据字段（`pass`/`fail`/`blocker_count`/`deviation_count`/`deviation_critical_count`/`design_gap_count`/`design_gap_reviewed_count`/`code_map_new_files_count`/`code_map_reviewed_count`/`regression_pass` 任一）
- Then 命令 exit 非 0，输出提示"该字段由验证脚本产出，不可手动填写"

#### BDD-10: 原子写，中断不落盘
- Given 一次模拟写入中断（进程被杀/序列化失败）的 set 调用
- When 中断发生在写入过程中
- Then 目标文件保持写入前的完整状态，不出现半成品 frontmatter

#### BDD-11: 文件不存在时拒绝
- Given 目标路径不存在任何文件
- When 执行 `agate-md-field-set` 对该路径写入字段
- Then 命令 exit 非 0，输出提示"请先 Write 产出文件，再 set 字段"

#### BDD-12: 无 frontmatter 时插入且不破坏正文
- Given 一个存在但不含 `---` frontmatter 块的文件
- When 执行 `agate-md-field-set` 写入字段
- Then 文件头被插入合法 `---` 块，原有正文内容逐字节保留不变

#### BDD-13: 正文残留旧字段时提示不删除
- Given 一个正文中含有与目标 key 同名旧格式声明的文件
- When 执行 `agate-md-field-set` 写入该 key 到 frontmatter
- Then 写入成功，且命令输出提示"检测到正文残留同名字段，frontmatter 优先，建议清理"，正文原残留内容不被自动删除

#### BDD-14: 生成的 frontmatter 通过 check-frontmatter.py
- Given 任意合法 set 写入操作后的文件
- When 执行 `check-frontmatter.py` 对该文件校验
- Then 校验 exit 0

#### BDD-15: set 校验与 check-gate.py 同源
- Given set 工具对某字段的 value 校验逻辑
- When 与 `check-gate.py`/`agate_common` 对同一字段的判定逻辑对照
- Then 二者读取同一份 `phases.yaml`/`task-files.md` schema 源，不存在 set 自建的独立校验规则（无"set 通过、gate 不通过"的新分叉）

#### BDD-16: 零协议知识 subagent 模拟场景
- Given 一个只被告知"用 `agate-md-field-set --list` 看要填什么，照提示填"的模拟调用序列（不预先注入协议知识）
- When 该序列按 `--list` 输出逐项调用 set 直至无缺失
- Then 最终 `--list` 输出无剩余缺失，且 `check-gate.py` 对该阶段的字段相关检查通过

#### BDD-17: set 白名单声明为 task_fields 与通用 Header 的完整并集
- Given `phases.yaml` 定义的某阶段 `task_fields` 列表与 `task-files.md` 定义的通用 Header 字段列表
- When 计算 set 工具实际支持写入的 key 白名单
- Then 该白名单等于两者并集（不是 design note 举例段落列出的子集），`--list` 的缺失项判定与该并集比对结果一致

#### BDD-18: 追加/自由格式字段一期明确拒绝
- Given `need_confirm_resolved`/`suggest_resolved`/`scope_resolved`/`mechanism_issues`/`execution_issues`/`dispatch_plan` 任一字段
- When 用 `agate-md-field-set` 尝试写入
- Then 命令 exit 非 0，输出提示"该字段一期写入形态暂不支持（追加/嵌套语义），见后续版本评估"

#### BDD-19: dispatch-context / dispatch-prompt 模板同步改为引导 set
- Given `agate/assets/templates/dispatch-context*.md` 与 `agate/assets/templates/dispatch-prompt.md`
- When 检视其中关于"如何声明产出文件字段"的指引文字
- Then 指引改为"用 agate-md-field-set 填写"一行式指令，且不再展示可被字面复制的 frontmatter 代码围栏示例

### DEBT0019：roadmap.md 表格列数完整性校验

#### BDD-20: 描述列含字面 `|` 时不误判
- Given 一份 roadmap.md，其中某数据行的描述列内容含字面 `|` 字符，导致 `split("|")` 后列数不等于表头精确列数（但仍 `>= 8`）
- When `_check_roadmap_done()` 解析该行
- Then 该行因列数不精确匹配被跳过（不进入 rm_id/status/related_task 取值逻辑），不产生误判的 status 结果

#### BDD-21: 既有合法表格判定结果不变
- Given 一份列数精确匹配表头的既有合法 roadmap.md（含 TAG0023 P8 roadmap 回写校验 BDD 覆盖的既有用例）
- When 修复后的 `_check_roadmap_done()` 解析该文件
- Then 判定结果（返回值/阻断行为）与修复前完全一致

### DEBT0020：roadmap.md 路径仓库根锚定

#### BDD-22: 非仓库根 CWD 下仍能正确定位
- Given 当前工作目录不是仓库根
- When `gate_p8()` 调用 `_check_roadmap_done()` 定位 roadmap.md
- Then 该函数按仓库根（而非相对 CWD 的硬编码拼接）定位到实际存在的 roadmap.md 并执行状态检查

#### BDD-23: 仓库根不可得时给出区分性提示
- Given 仓库根路径无法确定（如非 git 仓库环境）
- When `gate_p8()` 尝试定位 roadmap.md
- Then 输出区分性 stderr 提示（说明"仓库根不可得"），而非静默返回 None 跳过检查

#### BDD-24: 既有合法场景（仓库根 CWD）判定结果不变
- Given 当前工作目录是仓库根（既有正常调用路径，含 TAG0023 P8 roadmap 回写校验覆盖的既有用例）
- When 修复后的 `gate_p8()` 调用 `_check_roadmap_done()` 定位并解析 roadmap.md
- Then 判定结果（阻断行为/rm_id/status）与修复前完全一致

### RM-AG0049：phases.yaml P4 outputs 声明对齐

#### BDD-25: P4 outputs 声明补全
- Given `agate/rules/phases.yaml` 中 `id: P4` 的条目
- When 检视其 `outputs` 列表
- Then 列表包含 `{file: P4-review.md, required: true, status_field: status}`

#### BDD-26: S-1/S-2 双向一致性检查通过
- Given 补全后的 `phases.yaml`
- When 执行 `check-structure-consistency.py`
- Then S-1（YAML→文档/脚本）与 S-2（文档/脚本→YAML）双向检查均不因 P4-review.md 声明产生新的不一致报错

### RM-AG0050：P6.5 定位口径统一

#### BDD-27: phases.yaml 与 state-machine.md 表述口径一致
- Given `agate/rules/phases.yaml` 对 P6.5 的结构声明与 `agate/state-machine.md` 对 P6.5 性质的文字定位
- When 对照两处表述
- Then 两处均明确表达"P6.5 是挂载于 P6→P7 转移的强门槛子阶段，非独立 `.state.yaml` phase 值"这一口径，不再存在互相矛盾的叙述

#### BDD-28: 既有判定行为不变
- Given 统一口径后的 `phases.yaml`
- When 执行 `check-gate.py`（含 `check-gate.py P6.5 $TASK_DIR` 调用）与 `check-judge-verdict.py`
- Then 二者现有判定行为（`.state.yaml phase` 字段语义、事件账本记录、judge 复核轮次预算计数方式）与修复前完全一致

### 跨issue 约束验收

#### BDD-29: RM-AG0048 不改变 check-gate.py / check-events.py 判定逻辑
- Given 本任务提交的全部改动
- When 审查 `check-gate.py`/`check-events.py` 的 diff
- Then 除 `_check_roadmap_done()` 及其调用点 `gate_p8()` 中 `roadmap_path` 定位相关行外，两文件不含其他判定逻辑变更

## 5. 能力需求声明

```yaml
capability_requirements:
  - need: python-cli-execution
    why: 编写/验证 agate-md-field-set.py 及 check-gate.py 修复需要本地 Python 3.8+ 执行 pytest/ruff
    available:
      - "worktree 本地 Python 3.8+ + pytest 9.0.3 + ruff 0.16.4（P0-brief env_constraints 已确认可用）"
    status: available
  - need: git-repo-access
    why: DEBT0020 修复需验证仓库根定位逻辑（如 git rev-parse --show-toplevel），需在真实 git 仓库/worktree 中测试
    available:
      - "本 worktree 本身是 git 仓库（executor_env.git: true），可直接构造非仓库根 CWD 场景测试"
    status: available
```

本任务不涉及视觉/UI 能力，`domains` 不含 frontend，不需要 vision 相关声明。

## 6. 裁剪说明

`phases: [P1, P2, P3, P4, P5, P6, P6.5, P7, P8]` —— **无裁剪**，理由：

- P1/P2/P4/P5/P6 本身不可裁（协议核心阶段）。
- P3（TDD）不裁：`risk_level: medium`，仅 low 风险才可裁 P3，且本任务改动含核心 gate 判定函数（`_check_roadmap_done`），需要先写失败测试锁定缺陷再修复（AGENTS.md「改脚本的工作流」要求）。
- P6.5：本任务 P1 `created` 晚于 `judge_required_since`，`.state.yaml` 已声明 `judge.enabled: true`（dispatch-context 已确认，P1 frontmatter 不重复声明），故 P6.5 门槛按机制正常挂载，不裁剪。
- P7（一致性）不裁：本任务改动 `phases.yaml` + 多处协议文档表述（RM-AG0049/50），且 known_risks 已明确指出 `check-structure-consistency.py` S-1/S-2 双向一致性可能受影响，P7 是核对这类跨文件一致性的强制阶段，不能省略。
- P8（发布）不裁：本任务改动 `agate/scripts/*.py` + `agate/rules/*.yaml` + `agate/*.md`，触发 SELF-GATE（known_risks 已声明），需走正常发布流程更新 CHANGELOG/UPGRADING。

## 7. 待确认清单

[NO_NEED_CONFIRM]（无阻塞项；已发现的边界性问题均以 `[SUGGEST]` 形式落在第 3 节「同类扫描」中，不阻塞推进）
