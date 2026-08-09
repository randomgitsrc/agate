---
phase: P1
task_id: T001
type: problems
parent: P0-brief.md
trace_id: T001-P1-20260809
status: draft
created: 2026-08-09
agent: analyst
---

# T001 — agate v2.0 结构化数据改造（A+B+C+D 四流）：P1 需求基线

> 输入：P0-brief.md（任务简报/已知风险/硬约束）+ HANDOFF-V2.0.md（交接文档）+ /tmp/opencode/feasibility.md（可行性评估全文）+ P1-dispatch-context-analyst.md（派发指引）。
> 角色：analyst（需求质疑，见 `~/.agate/assets/execution-roles/analyst.md`）。
> 范围说明：本基线覆盖 **A+B+C+D 四流全做**（非仅流 A），一次性发布 agate v0.40.0（P0-brief 2026-08-09 修订决策）。

## 1. 需求复述

**一句话需求**（来自 P0-brief task 字段）：把 agate 协议中所有机器读取字段从"正文内嵌 YAML/纯散文 + 正则提取"重构为"YAML frontmatter + pyyaml 解析 + schema 校验"，覆盖三层（流 A：P1/P2 候选数/裁剪字段入 frontmatter + 校验器；流 B：P6/P7 结果结构化；流 C：标记状态收尾；流 D：任务编号规则改造），一次性发布 agate v0.40.0，消除 v0.30.2 → v0.35.0 连续 5 版的"正则摩擦补丁税"。

**重构后目标形态**（可行性评估 Option A，HANDOFF §5.2，P0-brief §分阶段路线）：
- **流 A**：P1/P2 候选数/裁剪类字段并入文件**已有 frontmatter 块**（不新增独立 .yaml 文件）。gate 读取改用 pyyaml：核心改造点是 `agate-md-field-get.py`（正则 → 先 pyyaml 读 frontmatter、无 key 回退正则），其 6 个 `.sh` 薄壳调用点基本不动。新增 frontmatter schema 校验器（仿 `.state.yaml` 的 `agate-state-yaml-check.py` 范式），pre-commit 拦截写坏格式——**subagent 写坏格式 → gate 直接拦，不靠主 Agent 判断**（HANDOFF §5.2"防造假"机制）。
- **流 B**：P6 汇总（pass/fail/ui_affected）入 frontmatter，逐条 PASS/FAIL 保留正文但格式从严（行首 `- PASS|FAIL BDD-NN:` 带 BDD 编号，消除"总结行误判"）；P7 的 BLOCKER/DEVIATION/DESIGN_GAP_REVIEWED 状态入 frontmatter。
- **流 C**：NEED_CONFIRM/SUGGEST/SCOPE_RESOLVED 的"已解决/已确认"状态结构化；**SCOPE+/PROD_TOUCHED/DESIGN_GAP 发现性标记本体保持散文**（评估 §5.5）。
- **流 D**：任务编号规则改为 `T{项目代号}{编号}`（如 `TAG0001`），校验器 `^T\d+$` → `^T[A-Z]{2}\d+$`，**硬切**不兼容旧格式；`check-changelog.sh` 去掉短前缀提取摩擦（`grep -oE 'T[0-9]+'` → 直接匹配完整 task_id）。

**范围边界（已定，不可收窄）**：
- **流 A 迁移字段**：P1 的 `risk_level` / `phases` / `override` / `implicit_coupling` / `coupling_checklist` / `internal_only` / `internal_only_reason` / `跳过风险` / `design_trivial` / `follows_existing_pattern` / `domains` / `packages`（12 项）；P2 的 `candidate_count` / `packages` / `domains` / `ui_affected`（4 项）。
- **流 A 不迁移**：`gate_commands`（scope 决策已定，4 个读取工具 `agate-read-gate-commands.py` / `agate-gate-missing-cmds.py` / `agate-read-p5-commands.py` / `agate-gate-p5-count.py` 仍从正文正则读）；`files_to_read` / `env_constraints` / `minimal_validation` / `implementation_dir` / `capability_requirements` 等非候选数/裁剪字段。
- **流 D 硬切**：v2.0 校验器只认 `^T[A-Z]{2}\d+$`，不兼容旧 `T\d+`。发布时存量旧格式任务已归档（含本 task T001），不再过 gate。不做双格式兼容。
- **自举原则**：本 task 自身编号 `T001`，全程按 v0.35 格式产出、用 `~/.agate`（v0.35.0 稳定版）跑 gate。新编号规则是流 D 的产物，不是本 task 的运行时约束。

## 2. 摩擦清单（v2.0 要消除的摩擦，系统性全列）

> 证据来源：可行性评估 §1（字段现状）、§2.2/§2.3（半结构化 vs 纯散文）、§5（风险）；v0.30.2 → v0.35.0 变更记录；现状代码（worktree 只读查证）。
> 分类：流 A（F1-F10，承接 archived P1 摩擦表）+ 流 B（F11-F14，新增）+ 流 C（F15-F16，新增）+ 流 D（F17-F19，新增）。

### 流 A：正文内嵌 YAML 字段正则提取摩擦（F1-F10）

| # | 摩擦 | 现状（正则行为） | 历史补丁 | v2.0 消除方式 | 对应 BDD |
|---|------|-----------------|---------|--------------|---------|
| F1 | **全角冒号** | `risk_level：high`（全角）不匹配 `risk_level:\s*(low\|medium\|high)`，字段被静默当缺失 | v0.30.2/v0.31.0 系列反复修格式 | pyyaml 解析失败 → 校验器明确报错，不再静默 | BDD-2 |
| F2 | **缩进错误** | `executor_env` 子项错 3 空格 → CI 红；产出文件从不校验 YAML 合法性 | v0.6 yaml-indent 回归（`regression/v060-yaml-indent.bats`） | pyyaml + schema 校验拦截并定位（字段名/行号） | BDD-4/7 |
| F3 | **phases 双格式** | 内联 `[P1,P2]` 与块式 `- Pn` 两套正则分支（`agate-md-field-get.py` phases op） | 隐性分叉，无显式补丁 | frontmatter 统一为单一 YAML 结构 | BDD-3 |
| F4 | **grep 计数摩擦** | `grep -c ... \|\| echo 0` 无匹配时产生 `0\n0` 双行，必须 `\| tail -1`；`grep -c` exit 1 语义纠缠 | AGENTS.md 脚本约定（反复踩） | pyyaml 读取返回确定值，无空行/exit code 问题 | BDD-1 |
| F5 | **字段无类型/枚举校验** | `ui_affected:\s*(true\|false)` 正则只做存在性；`candidate_count` 只 `grep -oE '[0-9]+'`（check-gate.sh:106） | v0.31.0 candidate_count 显式化（自声明 nudge） | schema 校验器按类型/枚举校验（如 risk_level ∈ low/medium/high） | BDD-5 |
| F6 | **产出物 YAML 无机器校验** | `check-protocol-consistency.py` CHECK 1 只校验协议文档的 ```yaml 块，**从不校验实际产出文件的 `key: value` 行** → v0.6 回归能漏进 CI | CHECK 1 现状局限 | 新增 frontmatter schema 校验器，pre-commit 拦截 | BDD-6/8 |
| F7 | **正则补丁税（持续性）** | v0.30.2 SUGGEST 重命名 → v0.31.0 candidate_count 显式化 → v0.35.0 PROD_TOUCHED 行尾锚定 + DESIGN_GAP 自检 + P7 启发式——连续 5 版同类补丁 | T090 计划明言"会被结构化取代，故不做过度设计" | 迁移后字段校验一次到位，补丁税终止 | BDD-1..15 |
| F8 | **在途任务格式漂移** | 项目侧在途任务 P1/P2 文件无 frontmatter；硬切换会破坏存量 | 无 | 双读：frontmatter 优先 + 旧正则回退（`agate-md-field-get.py` 内部） | BDD-9/10 |
| F9 | **测试数字漂移** | `count-tests.sh` 基线 594 + sanity 6；355 个测试直接触及待迁移字段（占 594 的 60%，约 15 个测试文件） | 发布检查依赖数字 | 改造后计数不漂移（fixture 重写而非删减） | BDD-11 |
| F10 | **一致性检查红** | `check-protocol-consistency.py` CHECK 9 锚点表（**37 条**）引用旧关键词（candidate_count/ui_affected/NEED_CONFIRM/DESIGN_GAP） | 硬约束：锚点表全量过一遍 | 脚本改写后锚点表重新校准 | BDD-13 |

### 流 B：P6/P7 结果纯散文正则摩擦（F11-F14，新增）

| # | 摩擦 | 现状（正则行为） | 历史补丁 | v2.0 消除方式 | 对应 BDD |
|---|------|-----------------|---------|--------------|---------|
| F11 | **P6 总结行误判** | `- PASS: 16` / `- FAIL: 1` 之类的"总结行"被 `grep -ciE '^\s*- (PASS|FAIL)'`（check-gate.sh:239）误计为逐条 PASS/FAIL → TOTAL 膨胀、与 P1 BDD 数对不上 | check-p6-format.sh 用 sed 把 `- PASS: N` 总结行改写为 `**Summary**:`（补丁式规避） | P6 汇总入 frontmatter，逐条 PASS/FAIL 行首强制 `- PASS|FAIL BDD-NN:`，总结行不再参与逐条计数 | BDD-16/17 |
| F12 | **P6 大小写/全角归一化补丁** | `- pass`/`- fail`/`- FAIL：` 需 sed 归一化（check-p6-format.sh:29-42），归一化失败 → 计数漏 | v0.35 多次补丁 | 行格式校验器强制 `- PASS|FAIL`（大写）+ BDD-NN 前缀，格式错直接报错而非静默改写 | BDD-17 |
| F13 | **P7 BLOCKER 计数行 vs 非计数行歧义** | `grep -cvE '\[BLOCKER\][:：]?\s*[0-9]+\s*条?\s*$'` 需区分"BLOCKER: 3 条"总结行与具体 BLOCKER 条目，语义依赖正则排除 | T090 收紧 + v0.35 DESIGN_GAP 自检 | BLOCKER/DEVIATION 状态入 frontmatter（结构化计数），不再用"非计数行排除"正则 | BDD-18 |
| F14 | **P7 DESIGN_GAP 0-vs-0 配对歧义** | `DESIGN_GAP_COUNT - DESIGN_GAP_REVIEWED` 用数字相减判断未配对（check-gate.sh:268-272），数量语义非配对语义——0-vs-0 时 WARNING 误报/漏报 | v0.35 P7 启发式 WARNING | DESIGN_GAP_REVIEWED 状态入 frontmatter（配对关系结构化），消除数量相减歧义 | BDD-19 |

### 流 C：标记状态纯散文摩擦（F15-F16，新增）

| # | 摩擦 | 现状（正则行为） | 历史补丁 | v2.0 消除方式 | 对应 BDD |
|---|------|-----------------|---------|--------------|---------|
| F15 | **P1 标记三值分级依赖行首正则** | 阻塞标记（行首 NEED_CONFIRM 样式）/建议标记（行首 SUGGEST 样式）/负向声明（行首 NO_NEED_CONFIRM 样式）靠 grep 计数（check-gate.sh:69-94），typo 兜底靠检测旧式"NEED_CONFIRM 倾向"标记残留（check-gate.sh:81，v0.30.2 重命名前格式）；全角/缩进敏感 | v0.30.2 SUGGEST 重命名 | 标记"已解决/已确认"状态结构化入 frontmatter，gate 读结构化状态，散文标记保留为人类痕迹 | BDD-21 |
| F16 | **发现性标记与状态耦合** | `[SCOPE_RESOLVED]` 靠行首正则 `[SCOPE_RESOLVED($\|[^a-z])`（check-scope-resolved.sh:37）；`[PROD_TOUCHED]` 行尾锚定（pre-commit-gate.sh:130-134）；SCOPE+/DESIGN_GAP 跨文件扫描——发现性标记本体必须保持散文（评估 §5.5），强行结构化反而漏报 | v0.35 PROD_TOUCHED 行尾锚定 | 只结构化"已解决/已确认"状态，发现性标记（SCOPE+/PROD_TOUCHED/DESIGN_GAP）本体保持散文，相关检测行为与 v0.35 一致 | BDD-22/23 |

### 流 D：任务编号规则摩擦（F17-F19，新增）

| # | 摩擦 | 现状（正则行为） | 历史补丁 | v2.0 消除方式 | 对应 BDD |
|---|------|-----------------|---------|--------------|---------|
| F17 | **check-changelog 短前缀提取摩擦** | `check-changelog.sh:14` 用 `grep -oE 'T[0-9]+'` 从 task_id 提取短前缀——只认旧格式 `T\d+`，新格式 `TAG0001` 提取为空 → CHANGELOG 无法记录 task_id | 无（旧格式下一直能用） | 直接匹配完整 task_id（去 `grep -oE 'T[0-9]+'` 截断），新格式完整识别 | BDD-26/27 |
| F18 | **编号空间无项目维度（撞号风险）** | 校验器 `^T\d+$`（agate-state-yaml-check.py:39）不表达项目命名空间，多项目局部编号（T001）无全局唯一约束 | 无 | 新格式 `T{项目代号}{编号}`（项目代号 2 个大写字母，对齐 Jira `[A-Z][A-Z]+`；编号动态 `\d+`，3 位起步可扩到 6 位），校验器硬切 `^T[A-Z]{2}\d+$`；active-tasks-template 第 4 条规则明确"项目局部命名空间 + 项目代号 + 动态编号" | BDD-25/26 |
| F19 | **硬切迁移摩擦** | v2.0 校验器只认新格式，存量旧格式任务（含本 task T001）在 v2.0 下无法过 gate | 硬切决策（已定，P0-brief §扩展） | 发布时存量旧格式任务已归档，不再过 gate；本 task 自身用 v0.35 开发工具（`~/.agate`）规避，不受影响 | BDD-26 |

**摩擦本质**：上述摩擦全部是"格式解析层"问题（解析可靠性），**不是**"内容真实性"问题。v2.0 只解决前者（见 §9）。

## 3. 隐含需求识别

> 用户没说但技术上必须做的依赖。逐条给出"为什么必须"。

1. **在途任务双读兼容（frontmatter 优先 + 旧正则回退）**
   为什么必须：项目侧在途任务的 P1/P2 文件无 frontmatter（`agate-md-field-get.py` 现状纯正则）。硬切换会破坏存量；dispatch 硬约束 4 已定"双读"。这是临时双路径代码，须写对（参考 `check-state-transition.sh` 的 HEAD/staged 双读模式）。
   判别契约（BDD-9 与 BDD-10 的 Given 据此互斥，同一文件不会同时命中）：frontmatter 含任意迁移字段 → 视为新格式，严格校验必填项（BDD-6 场景）；frontmatter 不含任何迁移字段 → 视为旧格式，回退正则且不触发必填校验（BDD-9 场景）。
2. **frontmatter schema 校验器是新交付物**
   为什么必须：只"搬位置"不"加校验"，等于只解决 F1/F2 表象、不解决 F6 根因——LLM 写坏缩进仍漏过（v0.6 yaml-indent 教训）。校验器让"subagent 写坏格式 → gate 拦截"成为机器机制而非主 Agent 判断（dispatch 约束 7）。
3. **check-protocol-consistency.py CHECK 9 锚点表（37 条）重新校准**
   为什么必须：锚点表白名单式盯死旧关键词（`ui_affected`/`NEED_CONFIRM`/`DESIGN_GAP` 等），脚本改写后关键词位置/存在性变化 → 正向或反向检查红。CI 红即任务失败（硬约束 5）。
4. **测试 fixture 大规模重写且用例数不漂移**
   为什么必须：`create_task_dir` 按旧格式写 P1/P2（正文内嵌），355 个测试（占 594 的 60%，约 15 个测试文件）直接触及迁移字段；fixture 必须改为写 frontmatter 版本。重写必须保持 `count-tests.sh` 数字不漂移（硬约束 1）——改写/重命名测试但保持 @test 数一致。
5. **角色卡/模板贴可复制的最小 frontmatter 模板**
   为什么必须：LLM subagent 是产出者，没有可复制模板就写不出正确缩进的 YAML。v0.31.0 给 P1 加模板验证有效（可行性 §5.1 ③）。涉及 analyst/architect/verifier 角色卡 + `task-files.md` 模板 + phase-cards（硬约束 3）。
6. **frontmatter 禁止 >3 层嵌套**
   为什么必须：嵌套越深 LLM 缩进错误率越高（v0.6 yaml-indent 教训）。迁移字段多为单层 `key: value` 或一层列表，天然满足；schema 定义必须守住此限（硬约束 2）。
7. **语义真实性边界写入设计文档**
   为什么必须：硬约束 6。结构化只提高解析可靠性，不改变 gate 对内容真实性的判断能力（BDD-8 单侧/双侧歧义、candidate_count 虚报依旧）。不声明此边界会产生"做了结构化就以为 gate 变强"的错觉（可行性 §5.2）。
8. **`agate-md-field-get.py` 是核心改造点（py 内部换实现，薄壳不动）**
   为什么必须：v0.34.0 把 46 处内联 python 抽离为 14 个 `.py`，解析逻辑集中。结构化只需改这一个工具的正则 → pyyaml+回退，6 个 `.sh` 薄壳（check-pruning/check-p6-provenance/check-p6-evidence/extract-context 等）只需保持 `FILE` env 传参不变。
9. **`agate-read-p5-commands.py` 的 P5_DATA 缓存键（CACHE_KEY）验证不失效**
   为什么必须：可行性 §4.4/§6.3 提醒——`agate-capture-env-baseline.sh` 的 `CACHE_KEY` 与 gate_commands 相关。因 gate_commands 暂留正文，预期不失效，但需在 P4/P5 验证并写进 changelog（一次性可接受成本）。
   验证载体：P4/P5 实现验证 + CHANGELOG 记录（无对应 BDD——属实现回归检查项，非可验收行为）。
10. **流 B：P6"结构放 frontmatter、枚举留正文但格式从严"折中需要行格式校验器**
    为什么必须：评估 §3 折中增强 + §6.2——逐条 BDD 结果（P6 常见 15-40 条）全塞 frontmatter 会让文件头膨胀、LLM 缩进错误率高；因此汇总入 frontmatter、枚举留正文但强制 `- PASS|FAIL BDD-NN:` 行格式。`check-p6-format.sh` 需从"大小写归一化"升级为"行格式校验"。
11. **流 B：P6 dispatch-context 预判检查白名单同步**
    为什么必须：评估 §5.6——`check-p6-provenance.sh:115` 检查 dispatch-context 无 `- PASS/FAIL` 预判，依赖"行首锚定"。P6 结果入 frontmatter 后，dispatch-context 模板示例（如"期望 BDD 全过"）不得误伤 frontmatter 样例；需同步白名单（AGATE_CARD 块已排除模式）。
12. **流 C：发现性标记保持散文的边界明确**
    为什么必须：评估 §5.5——`[SCOPE+]`/`[PROD_TOUCHED]`/`[DESIGN_GAP]` 是"运行时意外发现"，发生在产出文件任意位置，强行要求写进 frontmatter 会让"意外发现"变成"必须提前知道要声明"，反而漏报。只结构化其"已解决/已确认"状态（SCOPE_RESOLVED、DESIGN_GAP_REVIEWED）。
13. **流 D：本 task 自举——T001 用 v0.35 开发工具，新校验器只约束 v2.0 之后**
    为什么必须：本 task 在 worktree 改造期间用 `~/.agate`（v0.35.0 稳定版）跑 gate，编号保持 `T001` 旧格式；流 D 交付的新校验器（worktree 本体）只对 v2.0 之后新建任务生效。二者通过双工作区隔离保证互不干扰（HANDOFF §3 铁律）。
14. **流 D：check-changelog 去短前缀后 TASK_ID_SHORT 派生逻辑变更的连锁影响**
    为什么必须：`check-changelog.sh:14` 的 `TASK_ID_SHORT` 派生被下游引用，改直接匹配完整 task_id 后需确认下游引用点全部更新，避免"只改提取、漏改消费"的半迁移。
15. **版本发布流程（v0.40.0）**
    为什么必须：P8 需 badge 更新 + CHANGELOG + tag + **普通 merge（--no-ff）禁 squash**（HANDOFF 铁律，v0.31.0 tag 分叉事故）。P1 基线需声明完整 P1-P8 流程（本项目自身 dogfooding，不可裁阶段）。
    验证载体：P8 发布流程（badge/tag/merge 检查）——无对应 BDD，由 P8 阶段执行验证。
16. **主 checkout 与 worktree 双工作区隔离**
    为什么必须：改的是 gate 本身（自我改造）。`~/.agate` 指向主 checkout（v0.35.0 稳定版，本机项目在用），任何改动必须在 worktree（HANDOFF §3 铁律）。这是环境约束不是功能需求，但在需求基线登记以防 scope 越界。
    验证载体：P0 env_constraints（debug_env 指向 worktree，禁止触碰主 checkout）——环境约束，P6 验收不要求额外覆盖。

## 4. BDD 验收条件

> BDD 反模式自检（analyst.md）：Then 不绑定类名/属性名、无主观形容词、可二值判定（PASS/FAIL）、每条单一 Given-When-Then、编号连续。
> **本任务 BDD 全部断言"解析可靠性/格式校验"，不断言 gate 变强**（dispatch 约束 5 + 硬约束 6）。P6 逐条验收，PASS/FAIL 总数必须 ≥ 本基线 BDD 总数。
> 编号说明：连续编号 BDD-1..27，每条标注所属流（[流 A]/[流 B]/[流 C]/[流 D]）。

### 流 A：字段读取可靠性（F1-F8 消除）

#### BDD-1: [流 A] 机器字段从 frontmatter 统一读取
- Given 一份按 v2.0 格式书写的 P1-requirements.md，其候选数/裁剪类字段（risk_level/phases/packages/domains 等）全部声明在 frontmatter 块中
- When 运行协议门禁读取这些字段（裁剪检查/候选数检查）
- Then 门禁基于 frontmatter 声明值完成判定，判定结果与声明一致

#### BDD-2: [流 A] 全角冒号不再导致字段静默缺失
- Given P1-requirements.md 的 frontmatter 中某字段误用全角冒号（如 `risk_level：high`）
- When 运行 frontmatter schema 校验
- Then 校验失败并报错，且报错信息可指出该字段位置（不再被静默当作缺失处理）

#### BDD-3: [流 A] phases 内联与块式两种格式统一解析
- Given P1-requirements.md 的 frontmatter 中 phases 以块式列表（每阶段一行 `- Pn`）声明
- When 读取 phases 字段
- Then 解析结果与声明一致（不要求内联方括号格式）

#### BDD-4: [流 A] 缩进错误被校验器拦截（v0.6 yaml-indent 类回归不再漏进 CI）
- Given frontmatter 中某嵌套字段的子项缩进错误（如少 3 空格）
- When 运行 schema 校验
- Then 校验失败，且错误信息包含字段名或行号

#### BDD-5: [流 A] 枚举字段非法值被类型校验拦截
- Given P1-requirements.md 的 frontmatter 中 risk_level 声明为枚举外的值（如 "HIGH"）
- When 运行 schema 校验
- Then 校验失败并提示合法值（low/medium/high）

### 流 A：frontmatter schema 校验器（新交付物机制，F6 根因消除）

#### BDD-6: [流 A] 缺必填字段时 gate 拦截
- Given 一份新格式文件（frontmatter 含迁移字段集）的 P1-requirements.md 缺少必填字段（如缺 risk_level）
- When pre-commit 门禁运行 frontmatter schema 校验
- Then 门禁退出非零（拦截），不依赖主 Agent 人工判断

#### BDD-7: [流 A] 校验错误信息可定位修复
- Given frontmatter 含 YAML 语法错误（缩进/引号/换行错误）
- When 运行校验器
- Then 错误信息包含字段名或行号，subagent 可据此直接修复

#### BDD-8: [流 A] 校验器与 .state.yaml 校验同机制接入 pre-commit
- Given v2.0 改造完成后的协议仓库，且存在一个 frontmatter 不合规的 P1/P2 产出文件
- When 提交该文件
- Then pre-commit hook 在 commit 前拦截（与 `check-state-yaml.sh` 对 `.state.yaml` 的校验同机制）

### 流 A：在途任务双读兼容（F8 消除）

#### BDD-9: [流 A] 旧格式文件（正文内嵌、无 frontmatter）仍被正确读取
- Given 一份 v0.35 格式的 P1-requirements.md（候选数/裁剪字段在正文，frontmatter 无这些字段）
- When 运行协议门禁读取字段
- Then 通过回退路径读到字段，行为与 v0.35 一致

#### BDD-10: [流 A] frontmatter 优先于正文正则
- Given 一份同时声明 frontmatter 字段与正文同名字段的 P1 文件（两处值不同）
- When 读取该字段
- Then 返回 frontmatter 中的值（frontmatter 优先，不再走正则回退）

### 流 A：硬约束（F9/F10）

#### BDD-11: [流 A] 测试用例数不漂移
- Given v2.0 改造完成后的 worktree
- When 运行 count-tests.sh
- Then 输出 594 个测试用例（sanity.bats 6 另计），与改造前基线一致

#### BDD-12: [流 A] frontmatter 无超过 3 层的嵌套结构
- Given v2.0 的模板与角色卡定义的 frontmatter schema
- When 检查 schema 定义
- Then 任何字段的嵌套深度不超过 3 层

#### BDD-13: [流 A] 一致性检查 0 ERROR
- Given v2.0 改造完成后的协议仓库
- When 运行 check-protocol-consistency.py
- Then 输出 0 ERROR（含 CHECK 9 锚点表 37 条全量通过）

#### BDD-14: [流 A] v2.0 设计文档声明"结构化不解决语义真实性"
- Given v2.0 的 P2-design.md
- When 检索"语义真实性"或"内容真实性"相关表述
- Then 存在明确声明：结构化提高解析可靠性，不改变 gate 对内容真实性的判断（BDD-8 单侧/双侧歧义、candidate_count 虚报在结构化后依旧）

#### BDD-15: [流 A] gate_commands 保持正文读取，四个工具无回归
- Given v2.0 改造完成的 P2-design.md（gate_commands 仍在正文，未移入 frontmatter）
- When 运行 agate-gate-missing-cmds.py / agate-read-gate-commands.py / agate-read-p5-commands.py / agate-gate-p5-count.py 读取 gate_commands
- Then 四个工具仍能按旧正则正确读取，相关 P3/P5 门禁行为与 v0.35 一致

### 流 B：P6/P7 结果结构化（F11-F14 消除）

#### BDD-16: [流 B] P6 汇总（pass/fail/ui_affected）声明于 frontmatter
- Given 一份按 v2.0 格式书写的 P6-acceptance.md，其 frontmatter 含 pass/fail/ui_affected 汇总声明
- When 运行 P6 门禁读取汇总
- Then 门禁基于 frontmatter 汇总值判定（FAIL=0 且 total>0），而非从正文全文 grep 计数

#### BDD-17: [流 B] P6 逐条结果行格式从严（行首 `- PASS|FAIL BDD-NN:`）
- Given P6-acceptance.md 正文的逐条结果行为 `- PASS BDD-1: ...`（行首 `- PASS|FAIL` + BDD 编号）格式
- When 运行 P6 行格式校验器（check-p6-format.sh 升级版）
- Then 该行被识别为有效逐条结果；行首不带 BDD 编号（如 `- PASS: 16` 总结行）不被计为逐条结果

#### BDD-18: [流 A→B 边界] P6 总结行不再导致逐条计数膨胀（F11 消除）
- Given P6-acceptance.md 含 `- PASS: 16` 形式的总结行，且 frontmatter 已声明汇总
- When 运行 P6 门禁统计逐条结果数
- Then 总结行不计入逐条 PASS/FAIL 总数，总数仅统计行首 `- PASS|FAIL BDD-NN:` 的逐条结果

#### BDD-19: [流 B] P7 BLOCKER/DEVIATION 状态入 frontmatter（计数结构化）
- Given 一份按 v2.0 格式书写的 P7-consistency.md，其 frontmatter 声明 blocker_count / deviation_count（含"BLOCKER: 3 条"等汇总行）
- When 运行 P7 门禁读取 BLOCKER/DEVIATION 计数
- Then 门禁基于 frontmatter 结构化计数判定（=0 通过），不再用"非计数行排除"正则（`grep -cvE '\[BLOCKER\][:：]?[0-9]+条?$'`）从全文推断

#### BDD-20: [流 B] P7 DESIGN_GAP_REVIEWED 配对状态入 frontmatter
- Given 按 v2.0 格式书写的 P7-consistency.md，frontmatter 声明 design_gap 总数与 design_gap_reviewed 数（配对关系结构化）
- When 运行 P7 门禁检查未配对 DESIGN_GAP
- Then 未配对判断基于 frontmatter 结构化计数（REVIEWED < 总数 → 拦截），不再用正文数量相减的 0-vs-0 歧义判定

### 流 C：标记状态收尾（F15-F16 消除）

#### BDD-21: [流 C] P1 标记"已解决/已确认"状态结构化
- Given 按 v2.0 格式书写的 P1-requirements.md，frontmatter 声明 need_confirm/已解决状态（对应 NEED_CONFIRM/SUGGEST/SCOPE_RESOLVED 的"已解决/已确认"集合）
- When 运行 P1 门禁检查未解决 NEED_CONFIRM
- Then 门禁只把"未解决"的 NEED_CONFIRM（未在 frontmatter 声明 resolved）计为阻塞，已结构化解决的项不阻塞；散文标记保留为人类痕迹且不影响机器判定

#### BDD-22: [流 C] SCOPE_RESOLVED 状态结构化后闭环门禁仍工作
- Given 按 v2.0 格式书写的任务文件，`[SCOPE+]` 发现性标记保持散文、其"已解决"状态声明于 frontmatter（SCOPE_RESOLVED 结构化）
- When 运行 check-scope-resolved.sh 检查 SCOPE+ 闭环
- Then 有 SCOPE+ 且有对应已解决状态 → 通过；有 SCOPE+ 无对应已解决状态 → 拦截（闭环判定基于结构化状态，散文标记只作发现性痕迹）

#### BDD-23: [流 C] 发现性标记（SCOPE+/PROD_TOUCHED/DESIGN_GAP）本体保持散文
- Given v2.0 改造完成后，任务文件正文含 `[SCOPE+]`/`[PROD_TOUCHED]`/`[DESIGN_GAP:` 散文标记（未强制移入 frontmatter）
- When 运行 pre-commit PROD_TOUCHED 检测与 check-scope-resolved.sh 跨文件扫描
- Then 检测行为与 v0.35 一致（PROD_TOUCHED 行首锚定仍触发中止、SCOPE+ 仍被扫描识别），发现性标记未被强制结构化

#### BDD-24: [流 C] 角色卡/模板贴可复制 frontmatter 模板
- Given v2.0 改造完成后，analyst/architect/verifier 角色卡与 `task-files.md` 模板
- When 检查 frontmatter 模板段落
- Then 存在可直接复制的完整 frontmatter 样例（含迁移字段占位），可复制模板的 YAML 块通过 pyyaml 解析

### 流 D：任务编号规则改造（F17-F19 消除）

#### BDD-25: [流 D] 新编号格式 TAG0001 被 v2.0 校验器接受
- Given 一个按 v2.0 新编号格式创建的 `.state.yaml`，task_id 为 `TAG0001`（项目代号 AG + 动态编号 0001）
- When 运行 v2.0 版 agate-state-yaml-check.py 校验
- Then 校验通过（匹配 `^T[A-Z]{2}\d+$`），不再报"task_id 格式错误"

#### BDD-26: [流 D] 旧编号格式 T001 被 v2.0 校验器拒绝（硬切）
- Given 一个 task_id 为 `T001` 的 `.state.yaml`（旧格式）
- When 运行 v2.0 版 agate-state-yaml-check.py 校验
- Then 校验失败并提示合法格式（`^T[A-Z]{2}\d+$`），不兼容旧格式（硬切，无双格式过渡）

#### BDD-27: [流 D] check-changelog 直接匹配完整 task_id（F17 消除）
- Given CHANGELOG 的 task_id 记录为 `TAG0001`（新格式），check-changelog.sh 已改为直接匹配完整 task_id（去掉 `grep -oE 'T[0-9]+'` 短前缀提取）
- When 运行 check-changelog.sh 检查 task_id 记录
- Then `TAG0001` 被完整识别（不再被 `T[0-9]+` 截断为空/错截），该 task_id 的记录检查通过

### 自举约束（本 task 运行时不变式）

#### BDD-28: [流 D 边界] 本 task 自身 T001 全程按 v0.35 gate 通过
- Given 本 task（T001）执行期间的所有产出文件按 v0.35 旧格式书写（编号 `T001`，字段在正文/旧 frontmatter）
- When 运行 `~/.agate/scripts/check-gate.sh`（v0.35.0 稳定版）校验各阶段产出
- Then 各阶段 gate 通过（exit 0/1/2 按 gate 语义判定），本 task 不被流 D 新校验器约束

## 5. 待确认清单

[NO_NEED_CONFIRM]

> 方向判断已在 scope 决策中定死，无真无方向项：
> - 迁移集（候选数/裁剪类字段）与 `gate_commands` 暂留正文 → dispatch 约束 2 + P0-brief 已定
> - 双读 vs 硬切换（流 A）→ dispatch 硬约束 4 已定双读
> - 流 D 硬切（不兼容旧格式）→ P0-brief §扩展 已定硬切（F19）
> - A+B+C+D 四流全做 → P0-brief 2026-08-09 修订决策已定
>
> 以下为倾向项（审计痕迹，主 Agent 可自行采纳，不阻塞）：
- [SUGGEST: 校验器命名采用 `agate-frontmatter-check.py`，理由：对齐既有 `agate-state-yaml-check.py` 的 `agate-*-check.py` 命名族，check-protocol-consistency.py 工具白名单无需特例] → **已采纳（archived P1 主 Agent 2026-08-09）**：命名与既有 `agate-state-yaml-check.py` 命名族对齐，P2/P4 按此实现
- [SUGGEST: 角色卡 frontmatter 模板采用"可复制最小集 + 注释占位"格式，理由：v0.31.0 给 P1 加模板已验证有效（可行性 §5.1 ③），可复制模板是 LLM 写对格式的最可靠输入] → **已采纳（archived P1 主 Agent 2026-08-09）**：P2 角色卡/模板设计按此实现
- [SUGGEST: 流 B 的 P6 逐条结果按评估 §3 折中增强处理（汇总入 frontmatter、枚举留正文但格式从严），理由：P6 常见 15-40 条逐条结果全塞 frontmatter 会让文件头膨胀、LLM 缩进错误率上升；折中增强兼顾结构校验与可读性] → **已采纳（P0-brief 分阶段路线已定此折中）**：P2 设计按此实现

### SCOPE+ 登记（P2 阶段发现，2026-08-09）

- [SCOPE_RESOLVED: CHECK 9 锚点表 37→38（新校验器 check-frontmatter.sh 触发反向覆盖检查）]
  [BASELINE_CHANGE: P2 设计阶段发现——新增 check-frontmatter.sh 是 gate 脚本，check-protocol-consistency.py 的 check_anchor_coverage 反向检查会把新增脚本标记为未覆盖，锚点表须从 37 增至 38（BDD-13"37 条全量通过"表述加注"新增 1 条后 38 条"）。属新增脚本的必然结果，不改变任何 BDD Given/When/Then 语义]

## 6. 裁剪说明

```yaml
risk_level: high            # high=数据格式变更（P1/P2/P6/P7 产出物 frontmatter schema）+ gate 自我改造 + 355 测试换血（占 594 的 60%）+ 流 D 编号硬切
phases: [P1, P2, P3, P4, P5, P6, P7, P8]
跳过风险: 本次不裁剪任何阶段（全流程 P1-P8，HANDOFF §6.3）。协议级重构（约 25-30 文档/角色卡/模板 + 14 脚本 + 15 测试文件受影响 + 流 D 编号硬切），P3 测试设计先行、P7 双向一致性、P8 发布均不可省。
```

- **不裁剪理由**：
  - P2 不可裁剪——frontmatter 方案细化（字段 schema、校验器设计、双读回退、P6 折中增强、流 D 编号校验器）是核心设计，必须 architect 产出
  - P3 不可裁剪——风险 high，TDD 阶段必须保留；新格式 fixture + 校验器测试先行（HANDOFF §6.3 第 4 步），四流按流分组写测试
  - P4 不可裁剪——实现是交付底线（改 `agate-md-field-get.py` + 新增校验器 + 改模板/角色卡/fixtures + 流 B/C/D 脚本改造）
  - P5 不可裁剪——验证是交付底线（全量 bats + shellcheck + consistency）
  - P6 不可裁剪——验收是质量最后防线（逐条对照本基线 28 条 BDD）
  - P7 不可裁剪——设计 vs 实现双向一致性检查，本项目同时跑 self-gate 流程
  - P8 不可裁剪——发布 v0.40.0（badge + CHANGELOG + tag + 普通 merge，含流 D 编号规则生效）
- 本声明与执行一致，无 `override` 需求。

## 7. 范围声明

packages: [agate]          # 协议本体单一包（v0.40.0 版本 bump 对象 = worktree 的 agate/）
domains: [backend, cli]    # backend=gate 脚本/校验器逻辑；cli=agate-*.py 工具读取层。无 frontend（无 UI）、无 security（不涉及权限/安全模型）

> 备注：本项目无多包结构，`packages` 即 agate 协议自身。P8 多包发布逻辑不适用，但仍需版本 bump + CHANGELOG。流 D 涉及 `state-machine.md`/`dispatch-protocol.md`/`active-tasks-template.md` 文档示例同步，仍属 backend（协议文档/脚本层），不新增域。

## 8. 能力需求声明

```yaml
capability_requirements:
  - need: pyyaml 解析
    why: 新格式 frontmatter 读取与 schema 校验依赖（agate-state-yaml-check.py 已证明可用）
    available:
      - "Python 3.12 + pyyaml（可行性评估已核实可用，agate-state-yaml-check.py 在用）"
    status: available

  - need: bats 测试框架
    why: P3/P5/P6 验证 355 个测试的改造与 frontmatter fixture（四流全做，fixture 重写量更大）
    available:
      - "bats 1.10.0（worktree 环境已核实）"
    status: available

  - need: shellcheck
    why: P5 对改动的 14 个 .sh 脚本做静态检查
    available:
      - "shellcheck（worktree 环境已核实）"
    status: available
```

无 `status: GAP` 项。本任务非 UI 任务，不需要浏览器/视觉能力（`ui_affected: false` 由 P2 声明）。

## 9. 语义真实性边界（诚实声明）

> 硬约束 6 + dispatch 约束 5 要求写进需求基线。本基线所有 BDD 已据此设计。

- **结构化解决**（解析可靠性）：全角冒号（F1）、缩进错误（F2）、phases 双格式（F3）、grep 计数摩擦（F4）、字段类型/枚举校验（F5）、产出物 YAML 无机器校验（F6）、正则补丁税（F7）、P6 总结行误判（F11）、P7 BLOCKER 计数行歧义（F13）、P7 DESIGN_GAP 0-vs-0 配对歧义（F14）、check-changelog 短前缀提取（F17）、编号空间撞号（F18）。
- **结构化不解决**（内容真实性）：BDD-8 单侧/双侧歧义（P7 卡片 L83 记录的"数量对但 BDD-8 内容映射错"）、candidate_count 虚报（v0.31.0 已是自声明 nudge）、权衡/选择理由关键词（仍是语义匹配）。
- **真实性保障机制不变**：继续依赖 subagent 独立上下文 + requirements-review / plan-design-review 独立评审角色（ADR-002/006）。
- **BDD 不得声称"gate 变强"**：本基线 28 条 BDD 只断言"字段被可靠读取/坏格式被拦截/编号规则被正确校验"，不断言"gate 能发现内容造假"。

## 参考

- 可行性评估全文：/tmp/opencode/feasibility.md（§1 字段清单、§3 方案对比、§4 迁移成本、§5 风险、§6 路线/硬约束）
- 交接文档：HANDOFF-V2.0.md（§5 scope 决策、§6 流程、§8 已踩坑）
- 任务简报：P0-brief.md（A+B+C+D 范围、12 条风险、9 条硬约束、流 D 硬切决策）
- 现状代码：`~/.agate/scripts/agate-md-field-get.py`、`agate-state-yaml-check.py`、`check-gate.sh`、`check-pruning.sh`、`check-changelog.sh:14`、`assets/templates/task-files.md`
- 测试基线：`bash agate/tests/scripts/count-tests.sh` = 594（sanity.bats 6 另计）
