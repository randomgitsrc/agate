---
phase: P2
task_id: TAG0016
type: design
parent: P1-requirements.md
trace_id: TAG0016-P2-20260819
status: draft
created: 2026-08-19
agent: architect
# ── v2.0 机器字段 ──
candidate_count: 2
packages: [workflow, dispatch-protocol, state-machine, platform-notes, state-transitions, phase-cards, dispatch-prompt-template, gate-scripts]
domains: [protocol-docs, gate-scripts, test-infra]
ui_affected: false
# ── v2.0 派发编排字段 ──
dispatch_plan: {mode: serial, parallel_limit: 1, batches: [{id: doc-dedup, complexity: high}, {id: check12-anti-recurrence, complexity: medium}, {id: test-evidence-provenance, complexity: medium}]}
---

[PROD_NOT_TOUCHED]

# P2 方案设计 — agate 协议卫生与测试效率（TAG0016）

## 0. 职责声明表（BDD-1，去重前提）

去重方案落地前，先为每份涉及去重的协议文档确立一句话唯一职责，作为"改什么/不改什么"的判据来源。下表全部 7 类文档的职责边界均受本表约束，但**显式新增一行** `> 职责边界：{下表描述}（详见职责声明表，P2-design.md §0）` 的具体落地范围只有 4 份（BDD-1/BDD-19 落地点，对应 §1.1 M3/M7/M10/M12）：`WORKFLOW.md` / `dispatch-protocol.md` / `state-machine.md` / `platform-notes.md`。`rules/state-transitions.md`（M11）改为指向 `state-machine.md` 的指针句而非声明行；`assets/templates/dispatch-prompt.md`（M8）改为修正文件头矛盾声明；`phase-cards/*.md`（M13）保留原样、不新增声明行——三者的"职责"仍受本表约束，只是落地形式不同，不是同一格式的"职责边界"声明行，口径与 §11 完成标志一致（修复轮订正）。

| 文档 | 唯一职责 | 不承载 |
|------|---------|--------|
| `WORKFLOW.md` | 主流程入口——P0-P8 阶段总览、裁剪规则、核心原则、需求/验收机制骨架 | 具体派发操作细节、平台能力矩阵全文、门槛可执行判定命令 |
| `dispatch-protocol.md` | 派发操作层——可执行门槛判定命令、派发编排机制（工作量评估/并行规则/回退处理）、特殊事件恢复 | 平台能力矩阵本身（引用 platform-notes.md）、派发 prompt 模板全文（引用 dispatch-prompt.md） |
| `state-machine.md` | 状态机权威源——阶段转移规则、**重试上限唯一权威数值表**、PAUSED 恢复机制 | 派发操作细节 |
| `platform-notes.md` | 平台适配权威源——各 Agent 平台（OpenCode/Claude Code/Codex 等）能力矩阵、Windows 原生安装指南 | 派发调用方式细节（引用 dispatch-protocol.md） |
| `rules/state-transitions.md` | 阶段卡片速查——从 state-machine.md 提取的转移条件摘要，明确自身非权威 | 重试上限数值本身（改为指针，不复制表格） |
| `phase-cards/*.md` | 渐进披露操作卡——本阶段具体执行步骤/派发指引/gate 规则；允许内联关键数字（如 `MAX=N`）以保阅读体验，但须与权威源一致（由 CHECK 12 守护，不再靠人工同步） | 跨阶段规则的完整定义 |
| `assets/templates/dispatch-prompt.md` | 派发 prompt **权威模板**——完整可复制结构（含全部阶段特定追加节） | 无（本次去重后成为权威源） |

## 1. 影响面梳理（强制节，先于候选方案）

> 建立在 P1-requirements.md 第 3 节「同类扫描」6 类判定结论 + 3.8 结论汇总表之上，本节做候选方案级细化：具体改哪个文件的哪个小节、迁移后指针句长什么样、CHECK 12 检测算法伪代码级细化。

### 1.1 改什么（Modify）

| # | 文件 · 小节 | 改动 | 关联 BDD |
|---|------------|------|---------|
| M1 | `WORKFLOW.md`「## 平台适配」(L461-469) | 收窄为一句话摘要 + 指向 `platform-notes.md` 的指针（沿用 3.4 节已验证的"详见 X.md《标题》——权威唯一来源，本文件不重复维护"句式） | BDD-2 |
| M2 | `WORKFLOW.md`「## P1-P8 阶段总览」(L280) 表头附近 | 新增一句分工声明："本表为角色/评审映射颗粒度；逐条可执行判定命令见 `dispatch-protocol.md`《可判定门槛规范》" | BDD-3 |
| M3 | `WORKFLOW.md` 文件头（H1 下方） | 新增 §0 职责边界声明行 | BDD-1, BDD-19 |
| M4 | `dispatch-protocol.md`「## 平台适配」(L1291-1310) | 收窄为一句话摘要 + 指针（同 M1 句式），OpenCode issue #29616 等独家操作细节保留（不属于平台能力矩阵，属"调用方式"，符合本文件职责） | BDD-2 |
| M5 | `dispatch-protocol.md`「## 可判定门槛规范」(L948) 表头附近 | 新增分工声明（与 M2 对偶）："本表为逐条可执行 grep/命令颗粒度；角色/评审映射颗粒度见 `WORKFLOW.md`《P1-P8 阶段总览》" | BDD-3 |
| M6 | `dispatch-protocol.md`「## 派发 prompt 模板」(L429-661 内联版) | 内联 ` ``` ` 代码块收窄为极简结构提示（阶段名/角色/dispatch-context/输出路径 4 行骨架）+ 显式指针"完整模板（含全部阶段特定追加节）唯一权威源：`assets/templates/dispatch-prompt.md`，本文件不维护完整版" | BDD-4 |
| M7 | `dispatch-protocol.md` 文件头 | 新增 §0 职责边界声明行 + M2/M5 分工声明落点 | BDD-1, BDD-3, BDD-19 |
| M8 | `assets/templates/dispatch-prompt.md` 文件头 (L1-4) | 修正矛盾声明：删除"本模板与 dispatch-protocol.md 保持同步，协议文件为权威来源"，改为"本文件是派发 prompt 的**权威来源**；dispatch-protocol.md 仅保留极简结构提示 + 指针" | BDD-4, BDD-19 |
| M9 | `state-machine.md`「## 重试上限」表头附近 | 追加"本表是重试上限的唯一权威源；`rules/state-transitions.md` 与 8 张阶段卡片均须与本表一致（CHECK 12 自动校验）" | BDD-5, BDD-6 |
| M10 | `state-machine.md` 文件头 | 新增 §0 职责边界声明行 | BDD-1, BDD-19 |
| M11 | `rules/state-transitions.md`「## 重试上限」(L56-67) | 删除完整数值表，改为指针句："详见 `state-machine.md`《重试上限》——权威唯一来源，本文件不重复维护"（与文件头已有的"权威源：state-machine.md"声明保持行为一致） | BDD-5 |
| M12 | `platform-notes.md` 文件头 | 新增 §0 职责边界声明行（确立为平台适配权威源） | BDD-1, BDD-2, BDD-19 |
| M13 | 8 张 `phase-cards/P{N}-*.md` 的 `MAX=` 内联行 | **保留原样不改**（P1 3.6 节已判定"阅读体验需要就近可见"），仅纳入 M15 CHECK 12 锚点表检测范围 | BDD-6 |
| M14 | `agate/scripts/check-protocol-consistency.py` | 新增 CHECK 12（`AUTHORITATIVE_VALUE_ANCHORS` 锚点表 + `check_authoritative_values()` 函数 + 注册进 `CHECKS` 列表 + docstring 编号表追加一行），详细设计见 §2 | BDD-9, BDD-10 |
| M15 | `agate/tests/unit/test_check_protocol_consistency.py` | 新增 CHECK 12 测试：① 正报（值不一致触发 ERROR）② 不误报既有正确模式（3.4/3.7 节位置扫描后 0 ERROR）③ 边界（M11 迁移后 `rules/state-transitions.md` 不再被误判为重复源） | BDD-9, BDD-10 |
| M16 | `dispatch-protocol.md` 新增小节「## 全量重跑点审计」（建议插入「派发编排机制」节之前） | 落地 BDD-11 审计表（四个重跑点 + 必然/条件标注 + 是否可被 BDD-12/14 机制替代引用） | BDD-11 |
| M17 | `agate/scripts/check-p6-provenance.py` | 新增审计 7「引用 P5 证据的无改动校验」，详细设计见 §3 | BDD-12, BDD-13 |
| M18 | `agate/tests/unit/test_check_p6_provenance.py` | 新增审计 7 测试：① 无改动 → 允许引用 ② 有改动（P4 修复后重到 P6）→ 拦截，强制重跑 ③ 字段缺失（存量任务兼容）→ 回退强制重跑 | BDD-12, BDD-13 |
| M19 | `.state.yaml` schema 文档落点：`agate/state-machine.md`「每任务独立状态文件」小节 | 新增可选字段 `p5_pass_commit` 的文档声明（可选、缺失回退语义） | BDD-12（补充说明段） |
| M20 | `agate/phase-cards/P5-verification.md`「如果是首次进入本阶段」步骤 4-5 之间 | 插入一行：主 Agent 在 `git add` 前先 `git rev-parse HEAD` 写入 `.state.yaml` 的 `p5_pass_commit` 字段（值 = 本次 P5 commit 的**父提交**哈希，理由见 §3.2） | BDD-12 |
| M21 | `agate/phase-cards/P6-acceptance.md` | 新增"引用 P5 证据、不重跑"分支的产出规格 + gate 规则更新（含审计 7 的门槛描述） | BDD-12, BDD-13 |
| M22 | `agate/phase-cards/P8-release.md`「主 Agent 必须亲自执行」重跑 P5 一条 | 精简为："若 BDD-12 无改动校验判定 P8 发起时点距 P5 通过点无代码改动 → 复用同一份 `P5-test-results/`（不重新执行命令）；否则完整重跑 `gate_commands.P5`" | BDD-14 |
| M23 | `.github/workflows/protocol-tests.yml` `pytest` job（L10-33） | 新增一个**观测性**步骤（不影响门禁结果）：`pytest -n auto agate/tests/` 并记录耗时到 job 日志，仅用于人工事后对比，不作为 pass/fail 判据 | BDD-15 |

### 1.2 不改什么（Not Modify）

| 文件/范围 | 为什么看起来该改但不改 |
|-----------|----------------------|
| `dispatch-protocol.md` L972 / `state-machine.md` L231-233 / `git-integration.md` L162（Pre-commit 清单三处指针）| P1 3.4 节已验证是"权威源+指针"正确模式，非重复源；本任务防误伤（BDD-7），CHECK 12 锚点表不纳入这三处（物理上不可能触发误报，见 §2.3） |
| `AGENTS.md` / `loop-orchestration.md` / `phase-cards/README.md` 中"平台适配"/"阶段门槛"引用行 | P1 3.1/3.2 节判定为合法索引/交叉引用，不构成重复 |
| `dispatch-protocol.md`「并行规则」第 4 条判据描述（L730-750） | BDD-16 要求保持不变——本任务只加 CI 观测步骤（M23），不修改并行隔离判据本身；若测试涉及需断言其原文不变，而非新增豁免 |
| `role-system.md` / `git-integration.md` / `loop-orchestration.md` | P1 §8 SCOPE+ 预留声明未纳入本次去重对象；本次影响面梳理未发现波及这些文件的必须改动，不擅自扩大范围 |
| CHECK 5（已废弃） | 历史锚点，不恢复，不受本任务影响 |
| `agate/scripts/check-gate.py` P6 主逻辑 | BDD-12/13 的"无改动"判定是新增审计（check-p6-provenance.py 审计 7），不改变 check-gate.py 既有的 FAIL=0/证据非空判定，两者是并列关卡而非替换关系 |
| `agate/scripts/check-state-yaml.py` / `agate-state-yaml-check.py` | 已读代码确认（见 minimal_validation）：schema 校验只对 `task_id`/`phase`/`status`/`retries` 做存在性与格式校验，**不做 unknown-field 拒绝**——新增可选字段 `p5_pass_commit` 无需改这两个文件 |
| `agate/scripts/check-p6-evidence.py` | BDD-12/13 不改变证据文件本身的格式/去重规则，只新增"是否需要重新产出 regression.log"的判定，证据校验逻辑不变 |

### 1.3 风险在哪（Risk）

| # | 风险 | 缓解措施 |
|---|------|---------|
| R1 | **锚点漂移**：CHECK 2（内部引用存在性）/CHECK 3（硬编码行号）/CHECK 9（协议-脚本结构对齐锚点表）依赖协议文档当前标题/路径/关键词位置，去重迁移会移动这些位置 | 批次内每完成一个文件的迁移，立刻跑 `python3 agate/scripts/check-protocol-consistency.py`（非 strict）；批次收尾再跑 `--strict`；批次划分本身（§4 批次设计）就是为控制单次锚点变动范围 |
| R2 | **双源同步遗漏复发**：本任务修的就是双源问题，若 CHECK 12 设计有覆盖漏洞，未来又会产生新双源且无人发现 | CHECK 12 用白名单锚点扫描（非通用相似度），把本次修复的具体锚点（重试表 + 8 卡片 MAX + gate_commands 键集合已有 CHECK 4）纳入检测范围，形成结构防护网；§2 附测试设计方向 |
| R3 | **schema 变更向后兼容**：`.state.yaml` 新增 `p5_pass_commit` 字段，存量任务（TAG0001~TAG0015）无此字段 | 字段声明可选；`check-p6-provenance.py` 审计 7 读取时用"字段不存在 → 回退强制重跑"语义，不新增必填校验；已读代码确认 `agate-state-yaml-check.py` 当前实现不做 unknown-field 拒绝，无需改动该文件（见 §1.2） |
| R4 | **"无改动"判定被意外滥用**：exclusion 正则写得过宽，意外把真实源码改动排除在 diff 之外，导致该重跑却被跳过 | exclusion 正则严格限定为 `^agate-workspace/tasks/` 前缀（已用真实 git 命令验证，见 minimal_validation：该前缀不会匹配 `agate/scripts/`、`agate/*.md` 等协议本体路径）；M18 测试用例显式覆盖"改了源码后声称无改动"的拦截场景 |
| R5 | **CHECK 12 误报既有正确模式**（BDD-10 核心担忧） | 锚点式设计只对已注册的"权威数值锚点"做比对，不扫描非锚点段落——3.4/3.7 节列出的 Pre-commit 三处指针物理上不在锚点表内，不会被扫描到；M15 测试显式跑一遍这些位置确认 0 误报 |
| R6 | **批次间隐性依赖**：CHECK 12 锚点表（batch 2）的白名单条目依赖 doc-dedup（batch 1）迁移后的最终文档结构（如 `rules/state-transitions.md` 迁移后应变为纯指针，CHECK 12 的 pointer_files 规则要按迁移后的最终形态设计） | 批次采用 **serial**（§4），batch 1 完成并跑通 consistency 后才开始 batch 2，避免"设计防护网时目标结构还没定型"的错序风险 |
| R7 | **8 张卡片 MAX 内联行"保留不去重"的决策可能被质疑与"系统排查、不只修已知 6 处"的要求矛盾** | 不矛盾：P1 3.6 节已系统排查发现该重复并给出处理判定（"处理" = 纳入 CHECK 12 检测范围，不是要求物理去重），P2 继承该判定，不重新讨论，见 M13 |
| R8 | **xdist CI 观测步骤影响门禁稳定性**：若把 `pytest -n auto` 结果也作为 job 判据，单核/多核并行的 flaky 测试可能拖垮 CI | M23 明确该步骤只做耗时记录，不设 exit code 判据、不影响 job 整体 pass/fail（BDD-15 要求"仅用于耗时对比"，不是新增门禁） |
| R9 | **P5 commit 混入非产出文件改动会破坏 §3.2 等价性论证前提**：真实反例见 `5bdcd90`（`wf(TAG0001-P5):`），该 commit 混入了 `agate/scripts/agate-debt-check.py` 的真实修复（非产出文件）；若复发，父提交哈希与 P5 commit 自身哈希在审计 7 的 diff exclusion 判定上不再等价 | 失败方向保守——只会导致"本可复用却被误判需重跑"，不会产生"应重跑却被跳过"的安全漏洞（详见 §3.2）；M20 落点在 `P5-verification.md` 明确要求"P5 commit 不得混入非产出文件改动，若发现顺手修复的必要性，应先回 P4 走正常流程"，作为操作纪律层面的轻量缓解 |

---

## 2. CHECK 12 设计（BDD-9/10，真实候选权衡，非稻草人）

> 场景类型：设计模式（`follows_existing_pattern` 部分适用——延续 CHECK 4/9/11 的既有跨文件比对/白名单锚点模式），但**检测算法本身**（如何区分"内容真复制"与"合法引用"）是本任务的核心设计决策，需要真实候选探索（dispatch-context 约束 1 明确要求）。

### 2.1 三个候选算法

| 候选 | 思路 | 3 行伪代码适配 |
|------|------|---------------|
| **候选 1：整段文本相似度** | 对协议文件两两做段落级 diff（如 `difflib.SequenceMatcher`），相似度超阈值（如 0.85）→ 报重复 | `for f1, f2 in combinations(protocol_files, 2): for para in extract_headed_blocks(f1): match = best_match(para, extract_headed_blocks(f2)); if match.ratio > 0.85: warn(...)` |
| **候选 2：结构化"权威锚点"扫描** | 沿用 CHECK 4 的"从声明的权威文件里提取具名值 → 与其余文件里同名锚点的值/存在性比对"模式，白名单式只盯死已注册锚点 | `authoritative = extract(anchor.authoritative_file); for f in anchor.pointer_files: assert not redeclares_full_table(f); for f in anchor.inline_value_files: assert extract_inline(f) == authoritative[phase(f)]` |
| **候选 3：关键词+行数阈值** | 同一标题关键词出现在 ≥2 文件且标题下内容 > N 行 → 疑似重复，除非紧邻处出现"详见/见/权威源"字样 | `for kw in tracked_headers: hits = grep_heading(kw); if len(hits) >= 2: for f in hits: if block_len(f, kw) > N and not has_pointer_phrase(f, kw, within=3): warn(...)` |

### 2.2 权衡

| 维度 | 候选 1（相似度）| 候选 2（结构化锚点）| 候选 3（关键词+阈值）|
|------|-----------------|---------------------|----------------------|
| 与既有设计哲学一致性 | ❌ 冲突——`check-protocol-consistency.py` 文件头明文声明"只做结构一致性，不碰语义一致性"，模糊阈值判断（0.85 是语义判断）直接违反该原则 | ✅ 一致——延续 CHECK 4/9/11 已验证的白名单模式 | ⚠️ 部分冲突——"行数>N"仍是启发式而非精确结构判定 |
| 误报既有正确模式风险（BDD-10）| 高——WORKFLOW.md 的"一句话摘要"版本与 dispatch-protocol.md 的"操作细节"版本本身按 BDD-2/3 设计就该有实质差异，但都描述同一主题，相似度算法可能因主题重叠而误判；也可能因为改写彻底而漏判真复制 | 低——只提取具名数值/存在性，不比较自然语言相似度，3.4/3.7 节的纯指针句物理上没有可提取的"值"，天然不参与比对 | 中——同标题不同内容的文件（如两份都叫"环境隔离"但内容独立）会被误判；反之复制后改了标题的重复会漏判 |
| 覆盖面（能否抓住未注册的新重复） | 高——通用扫描，未来任意新增重复内容都有概率被抓到 | 低——只覆盖已注册锚点，新类型重复需要人工新增锚点条目才能被检测到 | 中——按标题关键词覆盖，比候选 2 广，比候选 1 窄 |
| 实现/维护成本 | 高——需要调阈值、处理误报噪音、性能（全文件两两比对）| 低——复用 CHECK 4 已验证的提取-比对代码骨架，新增锚点即扩展 | 中——阈值和"紧邻"距离都要调，仍有噪音需要处理 |
| 可测试性（M15 单测覆盖既有正确模式 0 误报）| 差——阈值型逻辑难以用少量单测穷尽边界 | 好——白名单是显式列表，单测直接构造每个锚点的正报/不误报用例 | 中 |

### 2.3 选择：候选 2（结构化权威锚点扫描）

**理由**：
1. **不违背既有设计哲学**——`check-protocol-consistency.py` 明确只做结构一致性；候选 1/3 都引入了或多或少的"语义相似度"判断，候选 2 是纯粹的值提取+比对，与 CHECK 4/9/11 一脉相承。
2. **BDD-10 天然满足**——候选 2 只从"已注册锚点"里提取具体值（数字/存在性），3.4/3.7 节的纯指针句里没有可提取的值，物理上不会进入比对逻辑，不需要额外的"排除规则"去豁免它们（候选 1/3 都需要额外维护一份"豁免列表"，本身就是误报-打补丁的循环）。
3. **BDD-9 的 Given 子句本身就是锚点式描述**："扫描协议文档中被标记为权威表格/权威数值的内容块（至少覆盖重试上限表、8 张阶段卡片内联 MAX 数字）"——这已经是白名单语言，候选 2 是对该描述最直接的技术翻译。
4. 覆盖面局限（候选 2 最大缺点：无法自动发现未注册的新重复类型）是可接受的权衡——防复发的目标是"本次修复的具体问题不再复发"+"结构化模式让未来新增锚点的成本很低"，不是"通用重复检测器"（YAGNI：P1 没有要求做通用检测器）。

**CHECK 12 具体设计（供 P3/P4 承接的实现导航，非完整实现）**：

```python
# ── CHECK 12: 权威数值/规则跨文件一致性（防复发，BDD-9/10）──
AUTHORITATIVE_VALUE_ANCHORS = [
    {
        "id": "retry-max",
        "desc": "阶段重试上限（MAX_RETRY）",
        "authoritative_file": "agate/state-machine.md",
        # 解析 "| P1 | 3 | ..." 表格行 -> {"P1": 3, "P2": 3, ...}
        "extract_authoritative": extract_md_table_int_column,
        "pointer_files": [
            # 断言：不再重新声明完整表格（不含 ≥3 组 "P\d \| \d" 行），且含指针短语
            {"file": "agate/rules/state-transitions.md",
             "must_not_redeclare_table": True,
             "must_contain_any": ["权威源", "详见", "见 agate/state-machine.md"]},
        ],
        "inline_value_files": [
            # 8 张卡片各自的 MAX= 内联行；phase 从文件名 P(\d)-*.md 推断
            {"glob": "agate/phase-cards/P*-*.md",
             "extract": r"MAX=(\d+)", "phase_from": "filename"},
        ],
    },
]

def check_authoritative_values(root, rep):
    for anchor in AUTHORITATIVE_VALUE_ANCHORS:
        authoritative = anchor["extract_authoritative"](root / anchor["authoritative_file"])
        for pf in anchor.get("pointer_files", []):
            text = (root / pf["file"]).read_text(encoding="utf-8")
            if redeclares_table(text, authoritative):     # 复用值集合比对，非文本相似度
                rep.error("CHECK12-authval", f"{pf['file']} 重新声明了权威表格（应改指针）")
            elif not any(p in text for p in pf["must_contain_any"]):
                rep.error("CHECK12-authval", f"{pf['file']} 缺少指向权威源的指针短语")
        for ivf in anchor.get("inline_value_files", []):
            for f in sorted((root).glob(ivf["glob"])):
                phase = re.match(r"(P\d+)-", f.name).group(1)
                m = re.search(ivf["extract"], f.read_text(encoding="utf-8"))
                if m and int(m.group(1)) != authoritative.get(phase):
                    rep.error("CHECK12-authval",
                              f"{f.name} 内联 MAX={m.group(1)} 与权威表 {phase}={authoritative.get(phase)} 不一致")
    rep.ok("CHECK12-authval")  # 无 error 时
```

`redeclares_table()` 的判定：统计文本里能匹配"权威表格的 (phase, value) 组合"的行数，≥3 组同时命中即判定"重新声明了完整表格"（阈值 3 而非"任意 1 组"是为了容忍正文偶尔提及某一阶段的具体数字，如 dispatch-protocol.md L1065-1103 节的伪代码注释提及"MAX_RETRY"但没有逐条列出 8 阶段数值——已用真实读码确认该处不会误触发，见 minimal_validation）。

---

## 3. BDD-12/13 跨阶段证据引用机制设计（真实候选权衡，非稻草人）

> 场景类型：设计模式（follows_existing_pattern 部分适用——`check-p6-provenance.py` 已有 6 道审计的加审计模式可复用），但 **"P5 通过 commit hash 记录在哪"是本任务的核心设计决策**（dispatch-context 约束 1 明确点名），需要真实候选探索。

### 3.1 三个候选方案

| 候选 | 存储位置 | 写入者 | 写入时机 |
|------|---------|--------|---------|
| **候选 A：`.state.yaml` 新增可选字段** `p5_pass_commit` | 任务状态文件（主 Agent 已有的写入权限区） | **主 Agent**（不是 subagent）| P5 gate 通过、`git add` 之前 |
| **候选 B：`P5-test-results/` 新增结构化 provenance 头** | 新文件如 `P5-test-results/provenance.yaml`，含 `commit: <hash>` | verifier subagent | verifier 产出 P5-test-results/ 时 |
| **候选 C：从 commit message 派生（不新增 schema）** | 不存储，P6 时刻现查：`git log --grep '^wf({task_id}-P5):' --format=%H -1` | 无需写入，读取既有 commit 历史 | P6 dispatch-context 准备阶段现查现用 |

### 3.2 一个共同的技术约束（先厘清，避免候选 A/B 设计出错）

**自指悖论**：无论候选 A 还是 B，都不可能把"本次 P5 commit 自身的哈希"写进这次 commit 携带的文件里——commit hash 是对树内容（含该文件的最终字节）做哈希计算的结果，写入前无法预知写入后的哈希值。

**等价解法**：候选 A/B 实际能做到的，是在 `git add`/写文件**之前**，用 `git rev-parse HEAD` 取**当前（父）提交**的哈希写入。这在语义上仍然成立——因为 BDD-12 的 diff exclusion 规则本身就排除了 `agate-workspace/tasks/**` 下的产出文件改动（P5 commit 本身只改这些文件），所以"父提交哈希"和"P5 commit 自身哈希"在 `git diff <hash>..HEAD --name-only` 的非产出文件判定上是**等价的**——父提交到 P5 commit 之间的 diff 全部是被排除的产出文件，不影响判定结果。候选 C 不受此约束（它是 commit 存在之后再查询，天然拿到的就是 P5 commit 自身的真实哈希）。

**边界条件与残余风险（修复轮补充，回应 plan-eng-review 阻塞项）**：上述等价性依赖一个前提——"P5 commit 本身只改产出文件"。该前提**并非无条件成立**：本仓库真实历史中，`5bdcd90`（`wf(TAG0001-P5):` commit）除产出文件外，还混入了对 `agate/scripts/agate-debt-check.py`（`serialize_evidence()` 函数 YAML int 边界修复）的真实改动（`git show --name-only 5bdcd90` 可验证，属真实反例，非假设场景）。若某次 P5 commit 重演此模式，父提交哈希与该 P5 commit 自身哈希在 diff exclusion 判定上**不再等价**——用父提交哈希做 exclusion 基准会把"P5 commit 里顺手带的非产出文件改动"误算作"P5 之后才发生的改动"。

失败方向是**保守/安全**的：这不会产生"应重跑却被误判为可复用、从而跳过应有验证"的安全漏洞——多出来的那份"改动"只会让审计 7（§3.5）判定 `changed` 非空，进而拦截"引用 P5 证据、不重跑"的声明，强制走完整重跑。唯一代价是该本可复用的场景被误判为需要重跑，即多跑一次，不会少跑该跑的验证，不威胁 BDD-17 回归底线。

轻量缓解：见下方 §1.3 风险表 R9；并要求 §1.1 M20 落点（`P5-verification.md`「如果是首次进入本阶段」步骤 4-5 之间）在写入 `p5_pass_commit` 的同时明确一句操作纪律——"P5 commit 不得混入非产出文件改动，若发现顺手修复的必要性，应先回 P4 走正常流程，不要混入 P5 commit"。

### 3.3 权衡

| 维度 | 候选 A（.state.yaml 字段） | 候选 B（P5-test-results 头） | 候选 C（commit message 派生） |
|------|---------------------------|------------------------------|-------------------------------|
| 是否需要新 schema | 需要（新增 1 个可选字段） | 需要（新文件 + 新解析规则） | **不需要**——零 schema 改动 |
| 写入者可信度 | 高——主 Agent 是 gate 判定方本人，在"确认 P5 通过"这一时刻写入，写入行为与判定行为同源 | 中——verifier subagent 是"自写文件 gate"里可信度较低的一方（P1/P2/P6/P7 同类），把关键 provenance 数据交给它写，增加了一层不必要的信任依赖 | 高——commit 存在本身就是主 Agent 亲自执行 `git commit` 的客观事实（外部产出，git 对象不可伪造），无需额外信任声明 |
| 对既有基础设施的复用 | 高——`.state.yaml` 已有 schema 校验脚本（`agate-state-yaml-check.py`），已验证支持可选字段无痛扩展 | 中——需要新增文件格式的解析代码（新 YAML 头或类似 M1.3a 的 EXIT_CODE 尾行约定） | 高——直接复用现有 `wf({Txxx}-P{n}): {摘要}` commit message 强约定（AGENTS.md/dispatch-protocol.md 已要求），且 P1 frontmatter 已声明 `git-log-diff` 能力可用 |
| 健壮性（约定漂移风险） | 高——字段读写都在受控代码路径里（P5 卡片指令 + provenance 脚本），不依赖自然语言文本格式 | 中——同 A，但多一层新文件格式解析，出错面更大 | **中低**——依赖 commit message 前缀严格匹配 `wf({task_id}-P5):`；这个前缀虽有约定但**当前没有任何 gate 脚本强制校验 commit message 格式**（commit-msg hook 只检查 self-gate 标记，不检查 `wf()` 前缀），人工/subagent 偶发写错前缀会导致查询失败 |
| 处理"BDD-13 不可复用边界"的自然度 | 高——每次真正走到 P5 gate 通过都会覆写字段值，天然反映"最近一次真实通过点"，无需额外逻辑 | 高——同 A | 高——`-1`（最近一条）天然取最新一次 P5 commit |
| 存量任务兼容 | 好——字段缺失时天然是"未声明"语义，回退强制重跑 | 好——文件不存在同样回退 | 好——查不到匹配 commit 同样回退；但存量任务的历史 commit message 格式可能不满足现行 `wf()` 约定（agate 早期任务可能未遵循），漏判概率略高于 A |

### 3.4 选择：候选 A（`.state.yaml` 新增可选字段 `p5_pass_commit`）

**理由**：
1. **信任模型更干净**——候选 A 由主 Agent（gate 判定方本人）在确认通过的那一刻写入，不依赖 subagent 自报（呼应 dispatch-protocol.md 的 C7 规则："subagent 自我报告不可信"，虽然 provenance 字段不是"结果声明"而是"事实记录"，但让判定方而非被判定方来记录，风险模型更简单）。
2. **候选 C 虽然零 schema 改动、技术上更优雅，但依赖一个当前无 gate 强制校验的自然语言约定**（commit message 前缀）——这恰好是本任务本身要修的"协议里存在事实上的重复/漂移风险点未被机制兜底"这类问题的同构风险，选它会把一个新的隐性依赖引入这个刚刚要收紧协议纪律的任务里，不划算。若未来 commit message 格式本身也上了 gate 强校验，候选 C 值得重新评估——已按标准格式登记为 `DEBT0009`（`{AGATE_WORKSPACE}/debt/tech-debt.md`，category: protocol，priority: low，source: review），不在本任务展开。
3. 候选 B 的"新文件格式解析"成本没有换来任何候选 A 没有的好处（写入时机、自指悖论、存量兼容三个维度 A/B 打平），选复用度更高的 A。

**字段设计**：

```yaml
# .state.yaml 新增可选字段（BDD-12 补充说明段已预先约束此设计）
p5_pass_commit: <40 位 git 提交哈希，可选字段>
```

- 缺失 → 审计 7（见 3.5）直接判定"无法复用，强制重跑"，不报错（向后兼容存量任务）。
- 写入时机：`P5-verification.md`「如果是首次进入本阶段」步骤 4（`git add` 之前）新增一步：`git rev-parse HEAD` 取父提交哈希，写入 `.state.yaml` 的 `p5_pass_commit` 字段，随后按原步骤 4-5 一并 `git add` + `commit`（不新增独立 commit）。
- `agate-state-yaml-check.py` 无需改动（已验证不做 unknown-field 拒绝，见 minimal_validation）。

### 3.5 审计 7 设计（`check-p6-provenance.py`，M17）

```python
# --- 审计 7：P6 引用 P5 证据的无改动校验（BDD-12/13）---
EXCLUDE_PRODUCE_PREFIX = "agate-workspace/tasks/"   # 已用真实 git 命令验证不匹配任何源码路径

def audit7_p5_evidence_reuse(task_dir, state_yaml):
    p5_commit = state_yaml.get("p5_pass_commit")
    if not p5_commit:
        return "no_reuse_claim_possible"   # 字段缺失 → 不允许声明复用，静默回退强制重跑，不报错
    out = run(["git", "diff", f"{p5_commit}..HEAD", "--name-only"])
    changed = [l for l in out.splitlines() if not l.startswith(EXCLUDE_PRODUCE_PREFIX)]
    if changed:
        # P6-acceptance.md 若仍声明"引用 P5 证据、不重跑" → 拦截
        if p6_declares_reuse(task_dir):
            error("GATE PROVENANCE: 声明引用 P5 证据但检测到非产出文件改动，须重跑 P5：" + ", ".join(changed))
        return "reuse_blocked"
    return "reuse_allowed"
```

- `grep -v` 语义边界（已用真实命令验证，见 minimal_validation）：当排除后无剩余文件时，管道命令退出码为 1（非 0），需在实现里按"空列表"处理，不能把 `grep` 的非 0 退出码误判为脚本异常。
- BDD-13 的"不可复用边界"由该逻辑自然满足：P6→P4 修复后重新到达 P6，若未重新走 P5（`p5_pass_commit` 未更新）→ `changed` 非空（P4 改动的源码文件不在排除前缀内）→ 强制重跑，不依赖任何额外的"回退检测"代码，diff 结果本身就是判据。

---

## 4. 候选方案（整体路线级，candidate_count: 2）

> 按 dispatch-context 约束 3：本节的候选方案数是"整体路线"级别（不是每条 BDD 各自数一遍）。§2/§3 已经是方案 A 内部对 BDD-9/10、BDD-12 两个核心子决策的真实探索，本节把"结构化锚点 + serial 分批 + .state.yaml 字段 + CI-only xdist"打包为方案 A，并给出一个真实存在优点、但综合权衡更差的方案 B 作对照。

### 方案 A（推荐）：结构化锚点扫描 + serial 分批迁移 + `.state.yaml` provenance 字段 + CI-only xdist 观测

- CHECK 12 用 §2.3 选定的结构化锚点扫描算法
- 迁移执行分 3 批 **serial**（doc-dedup → check12-anti-recurrence → test-evidence-provenance，见 §5）
- BDD-12 用 §3.4 选定的 `.state.yaml` 字段方案
- BDD-15 xdist 试点仅在 CI 新增一个观测性步骤（不影响门禁）

### 方案 B（真实存在优点的替代路线，非稻草人）：整段相似度扫描 + 单次全量迁移 + P5-test-results provenance 头 + 本地预跑 xdist

- CHECK 12 用候选 1（整段文本相似度）——**真实优点**：通用性更强，未来任意新增的、未被人工注册进锚点表的重复内容都有概率被自动发现，不需要每次新增重复类型都手工扩展白名单
- 迁移执行**一次性全量派发**（不分批）——**真实优点**：没有 serial 分批带来的批次协调开销（3 次 dispatch-context 撰写、3 次 consistency 中间检查），若一次性改对，总耗时更短
- BDD-12 用 P5-test-results provenance 头——**真实优点**：provenance 数据和测试证据物理上放在同一目录，查阅时不用跳到 `.state.yaml`，对人类阅读更直观
- xdist 直接本地预跑一次留痕耗时数字——**真实优点**：至少留了一个数字作参考，即使单核环境不能证明"加速"，也能证明"命令本身可执行不报错"

### 权衡与选择

| 维度 | 方案 A | 方案 B |
|------|--------|--------|
| 与既有代码设计哲学一致性 | 高（延续 CHECK 4/9/11 白名单模式，见 §2.2） | 低（相似度检测与"只做结构不做语义"原则冲突） |
| 误报既有正确模式风险（BDD-10 硬约束） | 低 | 高 |
| 单次改动风险（risk_level=high 任务，改动面 ≥8 文档+2 脚本+CI） | 低——serial 分批，每批独立跑 consistency，出错易定位回退到具体批次 | 高——一次性全量派发，若某处出错，8+ 文件的改动混在一次 diff 里难以定位回退单元 |
| provenance 写入者信任模型 | 高（主 Agent 写，见 §3.4） | 中（subagent 写） |
| BDD-15 硬约束遵守（"本地环境跑出的任何耗时数字不得作为已验证加速效果的证据"）| 天然满足——不在本地跑判据性质的 xdist | **有违反风险**——本地预跑数字即使声明"仅供参考"，也容易在后续复盘/PR 描述中被误引用为"已验证"，需要额外纪律约束 |
| 总执行耗时（乐观情况） | 中（分批协调有固定开销） | 低（无分批开销，若一次成功） |

**选方案 A**：risk_level=high + 改动面覆盖 ≥5 个协议文档的任务，"一次性改对"的乐观假设不成立的代价（大范围回退、错位改动难定位）远高于分批协调的固定开销；CHECK 12 的算法选择已在 §2 单独论证，不因整体路线打包而改变结论；BDD-15 的硬约束（禁止本地伪造已验证结论）决定了方案 B 的 xdist 处理方式存在合规风险。方案 B 每一条"真实优点"都成立，但在本任务的风险画像（协议自身机制变更、8+ 文件、CI 门禁牵涉）下，方案 A 的风险控制优势更重要。

---

## 5. 批次设计（dispatch_plan，mode: serial）

risk_level=high（P1 已声明），改动面覆盖 ≥8 个协议文档 + 2 个 gate 脚本 + 1 处 CI 配置，按 architect.md 硬规则必须拆批，不允许单发。

| 批次 id | 覆盖范围 | complexity | 依赖 |
|---------|---------|-----------|------|
| `doc-dedup` | RM-AG0025 文档去重：§0 职责声明表落地（M3/M7/M10/M12）+ M1/M2/M4/M5/M6/M8/M9/M11（BDD-1~8） | high（≥8 个文件，需逐个跑 consistency 确认锚点未失效） | 无 |
| `check12-anti-recurrence` | RM-AG0025 防复发机制：M14/M15（BDD-9/10）| medium（单脚本+单测试文件，但锚点表设计需要 `doc-dedup` 批次的最终文档结构定型后才能正确声明 pointer_files 断言） | `doc-dedup` |
| `test-evidence-provenance` | RM-AG0026：M16/M17/M18/M19/M20/M21/M22/M23（BDD-11~19）| medium（2 个脚本改动 + 3 张卡片 + 1 处 CI 配置，文件面不小但彼此无跨文件锚点依赖） | 无独立声明的批次前置依赖，但见下方理由——与 `doc-dedup` 存在真实文件重叠，选择 serial |

**为何整体选 `serial` 而非"`doc-dedup`/`test-evidence-provenance` 并行 + `check12-anti-recurrence` 串行其后"**（修复轮订正：原文曾称 `test-evidence-provenance` 与 `doc-dedup` "文件不重叠"，经核对 §1.1 M-表为事实错误，已订正如下）：`test-evidence-provenance` 批次与 `doc-dedup` 批次**实际存在文件重叠**——`doc-dedup` 批次的 M7（`dispatch-protocol.md` 文件头新增职责边界声明行）与 `test-evidence-provenance` 批次的 M16（同一文件 `dispatch-protocol.md` 新增小节「## 全量重跑点审计」）都改动 `dispatch-protocol.md`。若这两批并行派发，两个 subagent 会同时编辑同一份文件，产生合并冲突/相互覆盖的真实风险——这本身就是选择 serial 而非"两批并行+一批串行"方案的**更硬理由**，不只是协调开销权衡下的保守选择。除此之外，三批全部改动协议自身机制（本任务是 agate 自我改造），均会触发 SELF-GATE（改 `agate/*.md`/`agate/scripts/*.py`）并需要独立跑一次 consistency + 全量 pytest 确认，一次性并行三个 subagent 会让"发现某批出问题需要回退"时的归因复杂度上升（P7 一致性检查要交叉核对三批结果），而三批各自改动量都不小（尤其 `doc-dedup` 是 high），协调开销相对总工作量占比不高。选保守的 serial，用执行时间换取回退可定位性——符合本任务"用户明确不愿意一轮一轮来回改"（P0-brief known_risks）的诉求：一次做对比事后返工更重要。

---

## 6. gate_commands 声明

```yaml
gate_commands:
  P3: "python3 -m pytest agate/tests/unit/test_check_protocol_consistency.py agate/tests/unit/test_check_p6_provenance.py agate/tests/unit/test_protocol_dedup_audit.py -v"
  P3_timeout_seconds: 120
  P5: "python3 -m pytest agate/tests/ -q --tb=no && python3 agate/scripts/check-protocol-consistency.py --strict && bash agate/tests/scripts/count-tests.sh"
  P5_timeout_seconds: 180
```

- P3 命令覆盖本任务新增的 3 个测试落点（CHECK 12 单测 + provenance 审计 7 单测 + BDD-2~8 的"grep 断言审计"回归测试，后者建议新建 `agate/tests/unit/test_protocol_dedup_audit.py` 落地 HANDOFF-TAG0016.md 建议的"批量机械改动用一个断言审计测试覆盖"策略——一个参数化测试函数，逐条断言"权威源含关键内容 + 非权威源只含指针短语，不含完整段落/表格"，覆盖 BDD-2/3/4/5/6 全部去重项，不为每处改动单独写测试）。
- P5 命令是本任务自身的回归底线（BDD-17）：pytest 全绿 + consistency `--strict` 0 ERROR + 用例计数不漂移，三者用 `&&` 串联，任一失败即整体失败。
- `P5_timeout_seconds: 180`：三条命令串联，pytest 单跑基线 106-115s（HANDOFF 声明），加上 consistency + count-tests 预估合计 <180s，按三档基准表"单元测试类 120s"上浮到 180s（非默认值，显式声明理由：多命令串联）。

---

## 7. files_to_read

```yaml
files_to_read:
  - path: agate/WORKFLOW.md
    why: 「## 平台适配」(L461-469)「## P1-P8 阶段总览」(L280)「## Pre-commit 检查总览」(L303，不改仅核对) 的迁移落点（M1/M2/M3）
  - path: agate/dispatch-protocol.md
    why: 「## 平台适配」(L1291-1310)「## 可判定门槛规范」(L948)「## 派发 prompt 模板」(L429-661) 三处迁移落点（M4/M5/M6/M7），及「派发编排机制」节前插入 M16 全量重跑点审计表的位置
  - path: agate/assets/templates/dispatch-prompt.md
    why: 全文 259 行——本次去重后成为派发 prompt 权威源，文件头矛盾声明需修正（M8）
  - path: agate/state-machine.md
    why: 「## 重试上限」表(权威源，M9/M10)、「每任务独立状态文件」小节（.state.yaml schema 落点，M19）
  - path: agate/rules/state-transitions.md
    why: 全文 116 行——「## 重试上限」(L56-67) 改指针（M11）
  - path: agate/platform-notes.md
    why: 全文 156 行——确立为平台适配权威源，文件头新增职责声明（M12）
  - path: agate/phase-cards/P1-requirements.md
    why: MAX= 内联行位置示例（其余 7 张卡片同构，见下）
  - path: agate/phase-cards/P2-design.md
  - path: agate/phase-cards/P3-tdd.md
  - path: agate/phase-cards/P4-implementation.md
  - path: agate/phase-cards/P5-verification.md
    why: 「如果是首次进入本阶段」步骤 4-5（M20 p5_pass_commit 写入点）
  - path: agate/phase-cards/P6-acceptance.md
    why: 「产出规格」节（M21：新增"引用 P5 证据"分支）+「gate 规则」节
  - path: agate/phase-cards/P7-consistency.md
  - path: agate/phase-cards/P8-release.md
    why: 「主 Agent 必须亲自执行」重跑 P5 一条（M22 精简点）
  - path: agate/scripts/check-protocol-consistency.py:295-367
    why: CHECK 4 `_extract_gate_keys`/`check_gate_commands_keys` 实现模式——CHECK 12 复用的既有跨文件值比对骨架
  - path: agate/scripts/check-protocol-consistency.py:472-570
    why: CHECK 9 `SCRIPT_ALIGNMENT_ANCHORS` 白名单锚点表写法参考
  - path: agate/scripts/check-protocol-consistency.py:819-918
    why: CHECK 11 `UIUX_DOC_ANCHORS` 白名单锚点表写法参考 + CHECKS 列表注册位置（M14 落点）
  - path: agate/scripts/check-p6-provenance.py
    why: 全文 419 行——六道既有审计实现模式，M17 新增审计 7 需遵循同一风格（sys.stderr.write + sys.exit 语义）
  - path: agate/scripts/agate-state-yaml-check.py
    why: 已确认无 unknown-field 拒绝，新增 p5_pass_commit 字段无需改此文件，仅供 P4 复核结论
  - path: agate/tests/unit/test_check_protocol_consistency.py
  - path: agate/tests/unit/test_check_p6_provenance.py
  - path: .github/workflows/protocol-tests.yml:10-33
    why: pytest job 现有结构，M23 xdist 观测步骤插入点
  - path: HANDOFF-TAG0016.md
    why: 「批量机械改动的 TDD 策略」段——test_protocol_dedup_audit.py 设计依据
```

---

## 8. env_constraints（确认/细化 P0-brief）

```yaml
env_constraints:
  debug_env: "本环境为 Linux worktree（/home/kity/oclab/agate/.worktrees/agate-TAG0016）；xdist 加速验证需真实 CI（ubuntu-latest 4 核），本地单核环境不产出可采信的加速证据（BDD-15 硬约束，见 §4 方案 A/B 权衡）"
  test_cmd: "python3 -m pytest agate/tests/；python3 agate/scripts/check-protocol-consistency.py --strict；bash agate/tests/scripts/count-tests.sh（P0-brief 已给出，P2 确认无变化）"
  isolation_check: "本任务不涉及运行时服务/数据库/用户数据，无需额外测试环境隔离；[PROD_NOT_TOUCHED] 声明贯穿全阶段"
  双工作区纪律: "跑 gate 工具用 ~/.agate（稳定版）；改代码/跑测试/跑 check-protocol-consistency.py 必须用 worktree 自己的（HANDOFF-TAG0016.md §2 已详述，P4/P5 阶段 subagent 须遵循，不得混用）"
```

---

## 9. minimal_validation

```yaml
minimal_validation:
  - assumption: "git diff <commit>..HEAD --name-only 可用于 BDD-12/13 的无改动判定，且排除产出文件后的管道语义可控"
    method: "在 worktree 里跑真实 git 命令：git diff <上一commit>..HEAD --name-only 对比 PREV=d48b742 与当前 HEAD=546b093，得到 12 个改动文件全部落在 agate-workspace/tasks/ 前缀下；再用 grep -v '^agate-workspace/tasks/' 排除后管道为空，确认 grep 无匹配时退出码为 1（需在 §3.5 审计 7 实现里显式处理，不能把该退出码当异常）"
    result: confirmed
    note: "额外发现：agate-workspace/tasks/active-tasks.md（跨任务共享看板文件）同样落在 agate-workspace/tasks/ 前缀下会被排除，这是期望行为（它是编排产出而非源码，见 §1.1 M17/§3.5 EXCLUDE_PRODUCE_PREFIX 设计）——已在设计里采用广义前缀 agate-workspace/tasks/（不局限于 {Txxx}/ 子目录），与 BDD-12 原文'{AGATE_WORKSPACE}/tasks/** 下的...'表述一致"
  - assumption: "agate-state-yaml-check.py 当前 schema 校验不会因新增可选字段 p5_pass_commit 而报错（BDD-12 补充说明的'可选、缺失回退'前提是否已被现有代码满足）"
    method: "读代码验证：agate/scripts/agate-state-yaml-check.py 全文 58 行，仅对 task_id/phase/status（必填存在性+格式）与 retries（可选，存在时校验 dict 结构）做校验，无 unknown-field 拒绝逻辑（无 for key in data: if key not in ALLOWED_FIELDS 这类白名单校验）"
    result: confirmed
    note: "确认新增字段是纯增量、零风险改动，不需要同步改这个校验脚本"
  - assumption: "CHECK 4 的既有跨文件值比对实现模式（_extract_gate_keys + check_gate_commands_keys）可作为 CHECK 12 的骨架复用"
    method: "读代码验证：agate/scripts/check-protocol-consistency.py L295-367，确认其模式为'从声明的权威文件提取具名集合 → 遍历其余文件比对缺失项 → 报 ERROR 含文件名+具体差异'，与 §2.3 CHECK 12 设计的提取-比对结构一致"
    result: confirmed
    note: "CHECK 9（L472-570 白名单锚点表）与 CHECK 11（L819-918 白名单关键词存在性）进一步确认既有代码已有 3 种可复用的白名单式检测风格，CHECK 12 是这些风格在'数值一致性'场景的自然扩展，非全新范式"
  - note: "本任务其余部分（文档去重迁移、职责声明表落地、指针句改写、CI 观测步骤新增）为纯代码逻辑/纯文本编辑变更，无外部系统依赖：依赖的内部函数/数据转换均已在上方逐条列出（CHECK 4/9/11 提取比对函数、agate-state-yaml-check.py 校验逻辑、check-p6-provenance.py 六道既有审计的 sys.exit 语义约定）；不涉及浏览器行为/安全模型/外部系统交互，故不适用『必须做最小验证』的浏览器/外部系统类判据"
```

---

## 10. 全量重跑点审计表（BDD-11，M16 落点内容预览，供 P4 直接誊写进 dispatch-protocol.md 新增小节）

| 重跑点 | 性质 | 触发条件 | 是否可被本任务机制替代引用 |
|--------|------|---------|--------------------------|
| P5 首跑 | 必然 | 每个任务到达 P5 阶段必然执行一次 `gate_commands.P5` | 不可替代——首次验证无前序证据可引用 |
| P5 失败后重跑 | 条件 | 仅当首跑失败、修复后重新验证时发生（T027 教训：必须全量重跑，不能只测修复项） | 不可替代——重跑本身就是"确认修复且无新回归"的必要动作 |
| P6 refactor 独立 regression.log | 条件 | 仅 `change_type: refactor` 任务，且当前口径要求独立跑一次全量回归 | **本任务后可替代**——BDD-12 无改动校验成立时，P6 可引用 P5-test-results/ 而非独立重跑（§3） |
| P8 bump-version 后重跑 `gate_commands.P5` | 必然（发布前最后一道防线，不可移除，见 P1 BDD-14）| 每个走到 P8 的任务，bump-version 后需确认测试仍全绿 | **范围/方式可被简化**——BDD-12 判定 P8 发起时点距 P5 通过点无代码改动时，复用同一份 `P5-test-results/`（不重新执行命令）；否则仍需完整重跑（M22） |

---

## 11. 完成标志（供 P3 测试设计和 P5 验证使用）

- CHECK 12 已注册进 `check-protocol-consistency.py` 的 `CHECKS` 列表，`python3 agate/scripts/check-protocol-consistency.py --strict` 在**去重完成后**的 worktree 上 0 ERROR
- `test_check_protocol_consistency.py` 新增用例覆盖：CHECK 12 正报（人为制造数值不一致 fixture）+ 3.4/3.7 节既有正确模式 0 误报
- `check-p6-provenance.py` 审计 7 已实现，`test_check_p6_provenance.py` 新增用例覆盖：无改动允许引用 / 有改动拦截（BDD-13）/ 字段缺失回退强制重跑
- 4 份协议文档文件头均含"职责边界"声明行，内容与 §0 职责声明表一致：`WORKFLOW.md`（M3）/ `dispatch-protocol.md`（M7）/ `state-machine.md`（M10）/ `platform-notes.md`（M12）——这是"职责边界"声明行这一具体格式在本任务中落地的完整范围（口径统一，修复轮订正，与 §1.1 M-表一致）。`rules/state-transitions.md`（M11）改为指向 `state-machine.md` 的指针句，不新增"职责边界"声明行；`assets/templates/dispatch-prompt.md`（M8）改为修正文件头矛盾声明，同样不是同一格式的"职责边界"声明行——两者各自的验收点见 M11/M8 对应条目，不纳入本条"4 份文件"计数
- `rules/state-transitions.md`「## 重试上限」不再含完整数值表，仅含指向 state-machine.md 的指针句
- `dispatch-protocol.md`「## 派发 prompt 模板」内联版收窄为极简结构提示 + 指针；`assets/templates/dispatch-prompt.md` 文件头声明改为"本文件是权威来源"
- `python3 -m pytest agate/tests/` 全绿，用例总数只增不减（本任务新增用例，无删除）
- `bash agate/tests/scripts/count-tests.sh` 计数与文档声明一致
- `.github/workflows/protocol-tests.yml` 新增的 xdist 观测步骤存在且不影响 job 整体 exit code
