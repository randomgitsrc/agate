---
phase: P1
task_id: T091
type: problems
parent: P0-brief.md
trace_id: T091-P1-20260809
status: draft
created: 2026-08-09
agent: analyst
---

# T091 — agate v2.0 结构化数据改造：P1 需求基线

> 输入：P0-brief.md（任务简报/已知风险）+ HANDOFF-V2.0.md（交接文档）+ 可行性评估全文（mpifxr）。
> 角色：analyst（需求质疑，见 `~/.agate/assets/execution-roles/analyst.md`）。

## 1. 需求复述

**一句话需求**（来自 P0-brief task 字段）：把 agate 协议中 P1/P2 产出物的机器读取字段从"正文内嵌 YAML + 正则提取"重构为"YAML frontmatter + pyyaml 解析"，新增 frontmatter schema 校验器，消除持续性的正则摩擦补丁税（v0.30.2 → v0.35.0 连续 5 版同类补丁），发布 agate v2.0.0。

**重构后目标形态**（可行性评估 Option A，HANDOFF §5.2）：
- P1-requirements.md / P2-design.md 的候选数/裁剪类字段并入文件**已有的 frontmatter 块**（不新增独立 .yaml 文件）
- gate 读取改用 pyyaml：核心改造点是 `agate-md-field-get.py`（正则 → 先 pyyaml 读 frontmatter、无 key 回退正则），其 6 个 `.sh` 薄壳调用点基本不动
- 新增 **frontmatter schema 校验器**（仿 `.state.yaml` 的 `agate-state-yaml-check.py` 范式），pre-commit 时用 pyyaml 校验字段类型/必填——**subagent 写坏格式 → gate 直接拦截，不靠主 Agent 判断**（HANDOFF §5.2"防造假"机制）

**范围边界（已定，不可扩大，dispatch 约束 2）**：
- **只迁移**候选数/裁剪类字段（正文内嵌 YAML → frontmatter）：
  - P1：`risk_level` / `phases` / `override` / `implicit_coupling` / `coupling_checklist` / `internal_only` / `internal_only_reason` / `跳过风险` / `design_trivial` / `follows_existing_pattern` / `domains` / `packages`
  - P2：`candidate_count` / `packages` / `domains` / `ui_affected`
- **不迁移**：`gate_commands`（scope 决策已定，4 个读取工具 `agate-read-gate-commands.py` / `agate-gate-missing-cmds.py` / `agate-read-p5-commands.py` / `agate-gate-p5-count.py` 仍从正文正则读）；`files_to_read` / `env_constraints` / `minimal_validation` / `implementation_dir` / `capability_requirements` 等非候选数/裁剪字段
- **不在本任务范围**：流 B（P6/P7 结果结构化）、流 C（标记状态收尾）——依赖流 A 的校验器，后续单独处理
- **产出物本身按 v0.35 当前格式写**（能过当前 gate），新格式读取正确性由 P3/P5 的 fixture 覆盖（dispatch 约束 8）

## 2. 正则摩擦清单（v2.0 要消除的摩擦）

> 证据来源：可行性评估 §1（字段现状）、§2.2/§2.3（半结构化 vs 纯散文）、§5（风险）、v0.30.2 → v0.35.0 变更记录。
> 现状代码证据：`agate-md-field-get.py`（3 个正则 op）、`check-gate.sh:106,111,138`（grep 字段存在性）、`check-pruning.sh:16-100`（10 处 grep）。

| # | 摩擦 | 现状（正则行为） | 历史补丁 | v2.0 消除方式 | 对应 BDD |
|---|------|-----------------|---------|--------------|---------|
| F1 | **全角冒号** | `risk_level：high`（全角）不匹配 `risk_level:\s*(low\|medium\|high)`，字段被静默当缺失 | v0.30.2/v0.31.0 系列反复修格式 | pyyaml 解析失败 → 校验器明确报错，不再静默 | BDD-2 |
| F2 | **缩进错误** | `executor_env` 子项错 3 空格 → CI 红；产出文件从不校验 YAML 合法性 | v0.6 yaml-indent 回归（`regression/v060-yaml-indent.bats`） | pyyaml + schema 校验拦截并定位（字段名/行号） | BDD-4/7 |
| F3 | **phases 双格式** | 内联 `[P1,P2]` 与块式 `- Pn` 两套正则分支（`agate-md-field-get.py` phases op） | 隐性分叉，无显式补丁 | frontmatter 统一为单一 YAML 结构 | BDD-3 |
| F4 | **grep 计数摩擦** | `grep -c ... \|\| echo 0` 无匹配时产生 `0\n0` 双行，必须 `\| tail -1`；`grep -c` exit 1 语义纠缠 | AGENTS.md 脚本约定（反复踩） | pyyaml 读取返回确定值，无空行/exit code 问题 | BDD-1 |
| F5 | **字段无类型/枚举校验** | `ui_affected:\s*(true\|false)` 正则只做存在性；`candidate_count` 只 `grep -oE '[0-9]+'`（check-gate.sh:106） | v0.31.0 candidate_count 显式化（自声明 nudge） | schema 校验器按类型/枚举校验（如 risk_level ∈ low/medium/high） | BDD-5 |
| F6 | **产出物 YAML 无机器校验** | `check-protocol-consistency.py` CHECK 1 只校验协议文档的 ```yaml 块，**从不校验实际产出文件的 `key: value` 行** → v0.6 回归能漏进 CI | CHECK 1 现状局限 | 新增 frontmatter schema 校验器，pre-commit 拦截 | BDD-6/8 |
| F7 | **正则补丁税（持续性）** | v0.30.2 SUGGEST 重命名 → v0.31.0 candidate_count 显式化 → v0.35.0 PROD_TOUCHED 行尾锚定 + DESIGN_GAP 自检 + P7 启发式——连续 5 版同类补丁 | T090 计划明言"会被结构化取代，故不做过度设计" | 迁移后字段校验一次到位，补丁税终止 | BDD-1..5 |
| F8 | **在途任务格式漂移** | 项目侧在途任务 P1/P2 文件无 frontmatter；硬切换会破坏存量 | 无 | 双读：frontmatter 优先 + 旧正则回退（`agate-md-field-get.py` 内部） | BDD-9/10 |
| F9 | **测试数字漂移** | `count-tests.sh` 基线 594 + sanity 6；355 个测试直接触及待迁移字段 | 发布检查依赖数字 | 改造后计数不漂移（fixture 重写而非删减） | BDD-11 |
| F10 | **一致性检查红** | `check-protocol-consistency.py` CHECK 9 锚点表（37 条）引用旧关键词（candidate_count/ui_affected/NEED_CONFIRM/DESIGN_GAP） | 硬约束：锚点表全量过一遍 | 脚本改写后锚点表重新校准 | BDD-13 |

**摩擦本质**：上述摩擦全部是"格式解析层"问题（解析可靠性），**不是**"内容真实性"问题。v2.0 只解决前者（见 §9）。

## 3. 隐含需求识别

> 用户没说但技术上必须做的依赖。逐条给出"为什么必须"。

1. **在途任务双读兼容（frontmatter 优先 + 旧正则回退）**
   为什么必须：项目侧在途任务的 P1/P2 文件无 frontmatter（`agate-md-field-get.py` 现状纯正则）。硬切换（v0.20.0 BDD 标准化方式）会破坏存量；dispatch 硬约束 4 已定"双读"。这是临时双路径代码，须写对（参考 `check-state-transition.sh` 的 HEAD/staged 双读模式）。
   判别契约（BDD-6 与 BDD-9 的 Given 据此互斥，同一文件不会同时命中）：frontmatter 含任意迁移字段 → 视为新格式，严格校验必填项（BDD-6 场景）；frontmatter 不含任何迁移字段 → 视为旧格式，回退正则且不触发必填校验（BDD-9 场景）。
2. **frontmatter schema 校验器是新交付物**
   为什么必须：只"搬位置"不"加校验"，等于只解决 F1/F2 表象、不解决 F6 根因——LLM 写坏缩进仍漏过（v0.6 yaml-indent 教训）。校验器让"subagent 写坏格式 → gate 拦截"成为机器机制而非主 Agent 判断（dispatch 约束 7）。
3. **check-protocol-consistency.py CHECK 9 锚点表（37 条）重新校准**
   为什么必须：锚点表白名单式盯死旧关键词（`ui_affected`/`NEED_CONFIRM`/`DESIGN_GAP` 等），脚本改写后关键词位置/存在性变化 → 正向或反向检查红。CI 红即任务失败（硬约束 5）。
4. **测试 fixture 大规模重写且用例数不漂移**
   为什么必须：`create_task_dir` 按旧格式写 P1/P2（正文内嵌），355 个测试（占 594 的 60%）直接触及迁移字段；fixture 必须改为写 frontmatter 版本。重写必须保持 `count-tests.sh` 数字不漂移（硬约束 1）——改写/重命名测试但保持 @test 数一致。
5. **角色卡/模板贴可复制的最小 frontmatter 模板**
   为什么必须：LLM subagent 是产出者，没有可复制模板就写不出正确缩进的 YAML。v0.31.0 给 P1 加模板验证有效（可行性 §5.1 ③）。涉及 analyst/architect 角色卡 + `task-files.md` 模板 + phase-cards（硬约束 3）。
6. **frontmatter 禁止 >3 层嵌套**
   为什么必须：嵌套越深 LLM 缩进错误率越高（v0.6 yaml-indent 教训）。迁移字段多为单层 `key: value` 或一层列表，天然满足；schema 定义必须守住此限（硬约束 2）。
7. **语义真实性边界写入设计文档**
   为什么必须：硬约束 6。结构化只提高解析可靠性，不改变 gate 对内容真实性的判断能力（BDD-8 单侧/双侧歧义、candidate_count 虚报依旧）。不声明此边界会产生"做了结构化就以为 gate 变强"的错觉（可行性 §5.2）。
8. **`agate-md-field-get.py` 是核心改造点（py 内部换实现，薄壳不动）**
   为什么必须：v0.34.0 把 46 处内联 python 抽离为 14 个 `.py`，解析逻辑集中。结构化只需改这一个工具的正则 → pyyaml+回退，6 个 `.sh` 薄壳（check-pruning/check-p6-provenance/check-p6-evidence/extract-context 等）只需保持 `FILE` env 传参不变。
9. **`agate-read-p5-commands.py` 的 P5_DATA 缓存键（CACHE_KEY）验证不失效**
   为什么必须：可行性 §4.4/§6.3 提醒——`agate-capture-env-baseline.sh` 的 `CACHE_KEY` 与 gate_commands 相关。因 gate_commands 暂留正文，预期不失效，但需在 P4/P5 验证并写进 changelog（一次性可接受成本）。
   验证载体：P4/P5 实现验证 + CHANGELOG 记录（无对应 BDD——属实现回归检查项，非可验收行为）。
10. **版本发布流程（v2.0.0）**
    为什么必须：P8 需 badge 更新 + CHANGELOG + tag + **普通 merge（--no-ff）禁 squash**（HANDOFF 铁律，v0.31.0 tag 分叉事故）。P1 基线需声明完整 P1-P8 流程（本项目自身 dogfooding，不可裁阶段）。
    验证载体：P8 发布流程（badge/tag/merge 检查）——无对应 BDD，由 P8 阶段执行验证。
11. **主 checkout 与 worktree 双工作区隔离**
    为什么必须：改的是 gate 本身（自我改造）。`~/.agate` 指向主 checkout（v0.35.0 稳定版，本机项目在用），任何改动必须在 worktree（HANDOFF §3 铁律）。这是环境约束不是功能需求，但在需求基线登记以防 scope 越界。
    验证载体：P0 env_constraints（debug_env 指向 worktree，禁止触碰主 checkout）——环境约束，P6 验收不要求额外覆盖。

**不在范围的隐含项（记录不处理）**：流 B 的 P6 dispatch-context 预判检查白名单（可行性 §5.6）——P6 结果入 frontmatter 时模板示例可能误伤 `check-p6-provenance.sh` 预判检查；本任务只做流 A，此风险由后续流 B 任务承接。

## 4. BDD 验收条件

> BDD 反模式自检（analyst.md）：Then 不绑定类名/属性名、无主观形容词、可二值判定（PASS/FAIL）、每条单一 Given-When-Then、编号连续。
> 本任务 BDD 全部断言"解析可靠性/格式校验"，**不断言 gate 变强**（dispatch 约束 5 + 硬约束 6）。

### 摩擦消除：字段读取可靠性

#### BDD-1: 机器字段从 frontmatter 统一读取
- Given 一份按 v2.0 格式书写的 P1-requirements.md，其候选数/裁剪类字段（risk_level/phases/packages/domains 等）全部声明在 frontmatter 块中
- When 运行协议门禁读取这些字段（裁剪检查/候选数检查）
- Then 门禁基于 frontmatter 声明值完成判定，判定结果与声明一致

#### BDD-2: 全角冒号不再导致字段静默缺失
- Given P1-requirements.md 的 frontmatter 中某字段误用全角冒号（如 `risk_level：high`）
- When 运行 frontmatter schema 校验
- Then 校验失败并报错，且报错信息可指出该字段位置（不再被静默当作缺失处理）

#### BDD-3: phases 内联与块式两种格式统一解析
- Given P1-requirements.md 的 frontmatter 中 phases 以块式列表（每阶段一行 `- Pn`）声明
- When 读取 phases 字段
- Then 解析结果与声明一致（不要求内联方括号格式）

#### BDD-4: 缩进错误被校验器拦截（v0.6 yaml-indent 类回归不再漏进 CI）
- Given frontmatter 中某嵌套字段的子项缩进错误（如少 3 空格）
- When 运行 schema 校验
- Then 校验失败，且错误信息包含字段名或行号

#### BDD-5: 枚举字段非法值被类型校验拦截
- Given P1-requirements.md 的 frontmatter 中 risk_level 声明为枚举外的值（如 "HIGH"）
- When 运行 schema 校验
- Then 校验失败并提示合法值（low/medium/high）

### frontmatter schema 校验器（新交付物机制）

#### BDD-6: 缺必填字段时 gate 拦截
- Given 一份新格式文件（frontmatter 含迁移字段集）的 P1-requirements.md 缺少必填字段（如缺 risk_level）
- When pre-commit 门禁运行 frontmatter schema 校验
- Then 门禁退出非零（拦截），不依赖主 Agent 人工判断

#### BDD-7: 校验错误信息可定位修复
- Given frontmatter 含 YAML 语法错误（缩进/引号/换行错误）
- When 运行校验器
- Then 错误信息包含字段名或行号，subagent 可据此直接修复

#### BDD-8: 校验器与 .state.yaml 校验同机制接入 pre-commit
- Given v2.0 改造完成后的协议仓库，且存在一个 frontmatter 不合规的 P1/P2 产出文件
- When 提交该文件
- Then pre-commit hook 在 commit 前拦截（与 `check-state-yaml.sh` 对 `.state.yaml` 的校验同机制）

### 兼容：在途任务双读

#### BDD-9: 旧格式文件（正文内嵌、无 frontmatter）仍被正确读取
- Given 一份 v0.35 格式的 P1-requirements.md（候选数/裁剪字段在正文，frontmatter 无这些字段）
- When 运行协议门禁读取字段
- Then 通过回退路径读到字段，行为与 v0.35 一致

#### BDD-10: frontmatter 优先于正文正则
- Given 一份同时声明 frontmatter 字段与正文同名字段的 P1 文件（两处值不同）
- When 读取该字段
- Then 返回 frontmatter 中的值（frontmatter 优先，不再走正则回退）

### 硬约束

#### BDD-11: 测试用例数不漂移
- Given v2.0 改造完成后的 worktree
- When 运行 count-tests.sh
- Then 输出 594 个测试用例（sanity.bats 6 另计），与改造前基线一致

#### BDD-12: frontmatter 无超过 3 层的嵌套结构
- Given v2.0 的模板与角色卡定义的 frontmatter schema
- When 检查 schema 定义
- Then 任何字段的嵌套深度不超过 3 层

#### BDD-13: 一致性检查 0 ERROR
- Given v2.0 改造完成后的协议仓库
- When 运行 check-protocol-consistency.py
- Then 输出 0 ERROR（含 CHECK 9 锚点表 37 条全量通过）

#### BDD-14: v2.0 设计文档声明"结构化不解决语义真实性"
- Given v2.0 的 P2-design.md
- When 检索"语义真实性"或"内容真实性"相关表述
- Then 存在明确声明：结构化提高解析可靠性，不改变 gate 对内容真实性的判断（BDD-8 单侧/双侧歧义、candidate_count 虚报在结构化后依旧）

### 范围边界（防回归）

#### BDD-15: gate_commands 保持正文读取，四个工具无回归
- Given v2.0 改造完成的 P2-design.md（gate_commands 仍在正文，未移入 frontmatter）
- When 运行 agate-gate-missing-cmds.py / agate-read-gate-commands.py / agate-read-p5-commands.py / agate-gate-p5-count.py 读取 gate_commands
- Then 四个工具仍能按旧正则正确读取，相关 P3/P5 门禁行为与 v0.35 一致

## 5. 待确认清单

[NO_NEED_CONFIRM]

> 方向判断已在 scope 决策中定死，无真无方向项：
> - 迁移集（候选数/裁剪类字段）与 `gate_commands` 暂留正文 → dispatch 约束 2 + P0-brief 已定
> - 双读 vs 硬切换 → dispatch 硬约束 4 已定双读
> - 流 B/C 边界 → P0-brief 扩展已定（流 B/C 不在本任务）
>
> 以下为倾向项（审计痕迹，主 Agent 可自行采纳，不阻塞）：
- [SUGGEST: 校验器命名采用 `agate-frontmatter-check.py`，理由：对齐既有 `agate-state-yaml-check.py` 的 `agate-*-check.py` 命名族，check-protocol-consistency.py 工具白名单无需特例] → **已采纳（主 Agent 2026-08-09）**：命名与既有 `agate-state-yaml-check.py` 命名族对齐，P2/P4 按此实现
- [SUGGEST: 角色卡 frontmatter 模板采用"可复制最小集 + 注释占位"格式，理由：v0.31.0 给 P1 加模板已验证有效（可行性 §5.1 ③），可复制模板是 LLM 写对格式的最可靠输入] → **已采纳（主 Agent 2026-08-09）**：P2 角色卡/模板设计按此实现

## 6. 裁剪说明

```yaml
risk_level: high            # high=数据格式变更（P1/P2 产出物 schema）+ gate 自我改造 + 355 测试换血（dispatch 约束 6）
phases: [P1, P2, P3, P4, P5, P6, P7, P8]
跳过风险: 本次不裁剪任何阶段（全流程 P1-P8，HANDOFF §6.3）。协议级重构（约 25-30 文档/角色卡/模板 + 14 脚本 + 15 测试文件受影响），P3 测试设计先行、P7 双向一致性、P8 发布均不可省。
```

- **不裁剪理由**：
  - P2 不可裁剪——frontmatter 方案细化（字段 schema、校验器设计、双读回退）是核心设计，必须 architect 产出
  - P3 不可裁剪——风险 high，TDD 阶段必须保留；新格式 fixture + 校验器测试先行（HANDOFF §6.3 第 4 步）
  - P4 不可裁剪——实现是交付底线（改 `agate-md-field-get.py` + 新增校验器 + 改模板/角色卡/fixtures）
  - P5 不可裁剪——验证是交付底线（全量 bats + shellcheck + consistency）
  - P6 不可裁剪——验收是质量最后防线（逐条对照本基线 15 条 BDD）
  - P7 不可裁剪——设计 vs 实现双向一致性检查，本项目同时跑 self-gate 流程
  - P8 不可裁剪——发布 v2.0.0（badge + CHANGELOG + tag + 普通 merge）
- 本声明与执行一致，无 `override` 需求。

## 7. 范围声明

packages: [agate]          # 协议本体单一包（v2.0.0 版本 bump 对象 = worktree 的 agate/）
domains: [backend, cli]    # backend=gate 脚本/校验器逻辑；cli=agate-*.py 工具读取层。无 frontend（无 UI）、无 security

> 备注：本项目无多包结构，`packages` 即 agate 协议自身。P8 多包发布逻辑不适用，但仍需版本 bump + CHANGELOG。

## 8. 能力需求声明

```yaml
capability_requirements:
  - need: pyyaml 解析
    why: 新格式 frontmatter 读取与 schema 校验依赖（agate-state-yaml-check.py 已证明可用）
    available:
      - "Python 3.12 + pyyaml（可行性评估已核实可用，agate-state-yaml-check.py 在用）"
    status: available

  - need: bats 测试框架
    why: P3/P5/P6 验证 355 个测试的改造与 frontmatter fixture
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

- **结构化解决**（解析可靠性）：全角冒号（F1）、缩进错误（F2）、phases 双格式（F3）、grep 计数摩擦（F4）、字段类型/枚举校验（F5）、产出物 YAML 无机器校验（F6）。
- **结构化不解决**（内容真实性）：BDD-8 单侧/双侧歧义（P7 卡片 L83 记录的"数量对但 BDD-8 内容映射错"）、candidate_count 虚报（v0.31.0 已是自声明 nudge）、权衡/选择理由关键词（仍是语义匹配）。
- **真实性保障机制不变**：继续依赖 subagent 独立上下文 + requirements-review / plan-design-review 独立评审角色（ADR-002/006）。
- **BDD 不得声称"gate 变强"**：本基线 15 条 BDD 只断言"字段被可靠读取/坏格式被拦截"，不断言"gate 能发现内容造假"。

## 参考

- 可行性评估全文：/tmp/opencode/feasibility.md（§1 字段清单、§3 方案对比、§4 迁移成本、§5 风险、§6 路线/硬约束）
- 交接文档：HANDOFF-V2.0.md（§5 scope 决策、§6 流程、§8 已踩坑）
- 现状代码：`~/.agate/scripts/agate-md-field-get.py`、`agate-state-yaml-check.py`、`check-gate.sh`、`check-pruning.sh`、`assets/templates/task-files.md`
- 测试基线：`bash agate/tests/scripts/count-tests.sh` = 594
