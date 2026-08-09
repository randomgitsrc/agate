---
phase: P2
task_id: T001
type: design
parent: P1-requirements.md
trace_id: T001-P2-20260809
status: draft
created: 2026-08-09
agent: architect
---

# T001 — agate v2.0 结构化数据改造（A+B+C+D 四流）：P2 方案设计

> 输入：P1-requirements.md（28 条 BDD / F1-F19 摩擦 / 语义真实性边界）+ P0-brief.md（范围 / 9 硬约束 / 流 D 硬切）+ P1-review.md（approved）+ HANDOFF-V2.0.md（scope 决策）+ /tmp/opencode/feasibility.md（Option A/B 对比）+ P2-dispatch-context-architect.md（派发指引，优先级最高）。
> 角色：architect（方案设计 + 实现导航，见 `~/.agate/assets/execution-roles/architect.md`）。
> 范围：**A+B+C+D 四流全做**（非仅流 A），一次性发布 agate v0.40.0。
> 自举：本 task 自身编号 T001，本文档按 v0.35 格式产出（`candidate_count`/`packages`/`domains`/`ui_affected`/`gate_commands` 在正文声明），能过 v0.35 gate（BDD-28）。

**客观数字（主 Agent 核证 + 本 architect 复核一致）**：
- count-tests.sh 基线 = **594**（sanity.bats 6 另计）——本设计全部 fixture 改造保持该数字不漂移（BDD-11）
- CHECK 9 锚点表 = **37 条**（`SCRIPT_ALIGNMENT_ANCHORS` AST 解析确认）——脚本改写后全量重新校准（BDD-13）
- gate_commands 读取工具 = **4 个**（agate-read-gate-commands.py / agate-gate-missing-cmds.py / agate-read-p5-commands.py / agate-gate-p5-count.py）——流 A 不改动，仍从正文正则读（BDD-15）
- 受影响测试 = **15 文件、354 个 @test**（占 594 的 60%；2026-08 实测逐文件汇总：check-gate 101 / check-pruning 29 / check-p6-provenance 38 / check-p6-evidence 28 / check-tdd-red 38 / check-gate-p1-review 9 / check-scope-resolved 11 / check-retrospective 11 / check-p6-format 12 / agate-extract-context 15 / v060-design-gap 4 / v060-p8-internal-only 3 / v060-r4-cached 2 / pre-commit-hook 42 / consistency 11；feasibility 附录写 355 因 pre-commit-hook.bats 计 43 已过时，实为 42）——fixture 重写而非删减（BDD-11）

---

## 0. 需求基线回顾与设计目标

P1 将 v2.0 重构定义为**解析可靠性**改造：把机器读取字段从"正文内嵌 YAML + 正则提取"重构为"YAML frontmatter + pyyaml 解析 + schema 校验"，消除 v0.30.2 → v0.35.0 连续 5 版的"正则摩擦补丁税"。摩擦本质是**格式解析层**问题，不是**内容真实性**问题（P1 §2 末）。

**设计目标**（被 P1 BDD 引用为验收条件，即核心设计目标）：
1. **流 A**：P1 的 12 个 + P2 的 4 个迁移字段并入文件**已有 frontmatter 块**；`agate-md-field-get.py` 双读（pyyaml frontmatter 优先 + 正则回退）；新增 frontmatter schema 校验器挂 pre-commit（BDD-1..15）
2. **流 B**：P6 汇总（pass/fail/ui_affected）+ P7 状态（BLOCKER/DEVIATION/DESIGN_GAP）入 frontmatter，逐条结果留正文但格式从严（BDD-16..20）
3. **流 C**：NEED_CONFIRM/SUGGEST/SCOPE_RESOLVED 的"已解决/已确认"状态结构化；**SCOPE+/PROD_TOUCHED/DESIGN_GAP 发现性标记本体保持散文**（BDD-21..24）
4. **流 D**：任务编号 `^T\d+$` → `^T[A-Z]{2}\d+$` 硬切；check-changelog 去短前缀提取（BDD-25..27）
5. **自举**：本 task 自身 T001 全程按 v0.35 产出、用 `~/.agate`（v0.35.0）跑 gate（BDD-28）

candidate_count: 2

---

## 1. 候选方案（≥2，含权衡 + 选择理由）

### 候选方案 A：单工具双读扩展（选定）

**一句话**：机器字段并入已有 frontmatter 块；改造 `agate-md-field-get.py` 为"pyyaml 读 frontmatter 优先 + 无 key 正则回退"；新增 `agate-frontmatter-check.py` / `check-frontmatter.sh` 校验器挂 pre-commit；流 B/C/D 的读取点复用同一双读工具。

**影响域**：
- `agate-md-field-get.py`：新增 frontmatter 解析（`---` 块提取 + `yaml.safe_load`）+ 字段级 presence 检测 + 每 op 先 frontmatter 后正则回退；新增 op（candidate_count、blocker_count、design_gap_count 等流 B/C/D 读取点）
- 5 个 `.sh` 调用点（check-pruning.sh:16,18 / check-p6-provenance.sh:25,152 / check-p6-evidence.sh:61）保持 `FILE` env 传参不变，内部自动双读
- 新增 `agate-frontmatter-check.py`（schema 校验）+ `check-frontmatter.sh`（薄壳）+ pre-commit-gate.sh 挂载
- 流 B/C/D 读取点改走双读工具或直接 frontmatter 读取

**优点**：
- **爆炸半径最小**：核心改 1 个 py 工具（v0.34.0 py 抽离的净帮助，可行性 §4.4），5 个调用点接口不变
- **向后兼容天然**：双读即 BDD-9/10 的实现，旧格式在途任务无需迁移即继续可读
- **单文件原子性**：机器事实与散文同处一个文件，subagent 返回路径不变（评估 §3 Option A 核心优势）
- **测试改造量最小**：fixture 只改 frontmatter 内容，不新增第二文件断言

**风险**：
- 字段级 presence 检测写错（frontmatter 字段判定）→ 新/旧格式误判。缓解：presence 逻辑在双读工具内单一实现 + P3 专测（BDD-9/10 互斥场景 + 流 B/C 文件判定）
- `agate-frontmatter-check.py` 是 gate 脚本 → CHECK 9 反向覆盖检查要求锚点表新增条目（37→38）。缓解：本设计明确新增锚点（见 §3.1.4）

**工作量**：约 14 脚本改读点 + 1 新校验器 + 1 新薄壳 + 15 测试文件 fixture 重写 + 文档/模板/角色卡同步。

### 候选方案 B：拆分事实工具 + 独立机器数据文件（Option B 变体）

**一句话**：放弃并入 frontmatter，为 P1/P2/P6/P7 各建一个 `agate-p{n}-facts.py` 事实工具，机器事实写入**独立** `.yaml` 文件（`P1-facts.yaml` / `P6-facts.yaml`）或集中 `metadata.yaml`；gate 从独立文件读。

**影响域**：新增 4 个 facts 工具 + N 个 `.yaml` 文件类型；`agate-md-field-get.py` 现有 3 op 废弃；5 个调用点全改；subagent 产出路径从 1 变 2；fixture 全部加第二文件。

**优点**（在**某些维度**上确实优于 A）：
- **schema 校验最简单**：独立 `.yaml` 是纯 YAML 无散文干扰，错误信息最干净（评估 §3）
- **gate 读点最少**：从 N 个文件读变 1 个文件读，长期字段扩展只需加 facts 工具输出
- **最接近"机器读事实/人读散文"终极分层**（评估 §3 Option B）

**缺点**：
- **双文件同步漂移**：subagent 改 `.md` 忘改 `.yaml` → 新的"假一致"（评估 §3 B 核心否决点）
- **写入成本翻倍**：LLM 写两个文件并保持同步的失败率远高于写一个文件头（评估 §3 结论）
- **fixture 改造量最大**：每个 fixture 调用点加第二文件 + 双文件断言，354 个测试改造量远超 A
- **并发写冲突**：集中 metadata.yaml 时多阶段并发写同一文件（评估 §3）
- **违反硬约束 4 的双读精神**：独立文件方案对旧格式在途任务需额外迁移工具

### 权衡对比矩阵

| 维度 | A（frontmatter + 双读工具） | B（独立 facts 工具 + .yaml） |
|------|---------------------------|------------------------------|
| subagent 写入成本 | 中（单文件，注意缩进） | 高（双文件 + 同步） |
| 双文件漂移风险 | 无 | **有** |
| fixture 改造量（354 测试） | 低-中（改 frontmatter） | **高**（加第二文件） |
| 向后兼容（在途任务） | 好（双读回退） | 差（需迁移工具） |
| schema 校验难度 | 中（frontmatter 块提取） | 低（纯 YAML） |
| 与硬约束 4 双读一致性 | **一致**（P0-brief 已定） | 冲突 |
| 与评估 §3 结论一致性 | **一致**（Option A 明显优于 B） | 不一致 |
| 未来扩展（新增字段） | 加 op + schema 条目 | 加 facts 输出 |

### 选择理由

**选 A 不选 B**。核心判断（与可行性评估 §3 结论一致、P0-brief 已定为双读）：agate 的产出者是 **LLM subagent**，对人类程序员"独立 .yaml 更整洁"，对 LLM"写两个文件并保持同步"是比"在一个文件头写 YAML"高得多的失败率来源（评估 §3 原文）。A 满足硬约束 4（双读：frontmatter 优先 + 旧正则回退）且 fixture 改造量最小——354 个测试换血已是本任务最大成本，B 会把该成本再放大一档。B 的"纯 YAML 校验最简"优势在 A 的 frontmatter 块提取（`---` 分隔符 + pyyaml）下同样获得，不构成选 B 理由。

**子决策（双读工具扩展 vs 拆分事实工具）**：在选定 A 的前提下，读取层采用**单工具双读扩展**而非"每阶段一个 facts 工具"——理由：① 5 个调用点零改动，接口稳定性最高；② 本任务迁移字段仅 16 个（P1 12 + P2 4，去重后 14 键），单工具加 op 成本低；③ 拆分 facts 工具是面向"未来字段爆炸"的架构，对当前 16 字段是过度设计（YAGNI，architect.md §原则）。流 B 的 P6/P7 读取同样复用双读工具新增 op，不新建 `agate-p6-facts.py`。

---

## 2. 影响域分析（改 / 不改 / 风险）

### 改什么（worktree 的 `agate/`）

| 类别 | 文件 | 改动 |
|------|------|------|
| 读取核心 | `agate-md-field-get.py` | 双读（字段级 presence 检测 + 正则回退）+ 新 op |
| 校验器（新） | `agate-frontmatter-check.py` | frontmatter schema 校验（仿 agate-state-yaml-check.py 范式） |
| 校验器薄壳（新） | `check-frontmatter.sh` | 调 py + 报错 + exit 语义 |
| 挂载点 | `pre-commit-gate.sh` | 新增 frontmatter 校验步骤（与 check-state-yaml.sh 同机制） |
| gate 读取点 | `check-gate.sh` | P1 NEED_CONFIRM 分支 / P2 candidate_count+四字段 / P6 / P7 改读 frontmatter（含回退） |
| 裁剪读取点 | `check-pruning.sh` | 10 个字段 grep → 双读工具 op |
| 上下文摘要 | `agate-extract-context.sh`（:69,80,88） | **保持 grep，不改路由（FIND-2 决策）**：该脚本是上下文摘要工具（非 gate 判定点），frontmatter 顶层 key 仍顶格匹配 `^risk_level:` / `^domains:` 等 grep；保持 grep 可同时兼容新旧格式，避免为摘要工具引入双读依赖。注：不满足 BDD-1"统一读取"字面语义，但 BDD-1 的验收对象是 gate 判定读取点（check-gate/check-pruning/check-p6-*），摘要工具不属于判定路径 |
| P6 审计 | `check-p6-provenance.sh` / `check-p6-evidence.sh` | risk_level/ui_affected 读取走双读（薄壳接口不变）；审计 3 计数改从严格式 + frontmatter 交叉 WARNING |
| P6 格式校验 | `check-p6-format.sh` | 从"大小写归一化 sed"升级为"行格式校验" |
| SCOPE 闭环 | `check-scope-resolved.sh` | 已解决状态读 frontmatter（散文扫描保留） |
| 流 D | `agate-state-yaml-check.py` / `check-changelog.sh` | task_id 正则硬切 / 去短前缀提取 |
| 一致性锚点 | `check-protocol-consistency.py` | CHECK 9 锚点表全量重新校准（37 条）+ 新增 check-frontmatter.sh 锚点 |
| 模板/角色卡 | `task-files.md` / `active-tasks-template.md` / analyst / architect / verifier / phase-cards P1/P2/P6/P7 | 可复制 frontmatter 模板（BDD-24） |
| 工具文档 | `scripts/README.md`（:68 工具清单表） | `agate-md-field-get.py` 条目描述同步：新增 op 清单 + 双读语义（FIND-8） |
| 测试计划 | `docs/archived/plans/agate-test-plan-2026-07-01.md` 附录 A | 受影响用例数/脚本清单数字同步（354 而非 355，防 count-tests 文档漂移检查误报，FIND-8） |
| 测试 | `fixtures.bash` + 15 个 `.bats` 文件 | fixture 写 frontmatter 版本，用例数不漂移 |

### 不改什么（明确边界）

- `~/.agate`（主 checkout /home/kity/oclab/agate = v0.35.0 稳定版）**一字不动**——双工作区铁律（HANDOFF §3）
- **gate_commands 暂留正文**：4 个读取工具（agate-read-gate-commands.py / agate-gate-missing-cmds.py / agate-read-p5-commands.py / agate-gate-p5-count.py）仍从正文正则读，**不迁移**（dispatch 约束 2 + P1 §1"流 A 不迁移"）
- `files_to_read` / `env_constraints` / `minimal_validation` / `implementation_dir` / `capability_requirements` 等非候选数/裁剪字段不迁移（P1 §1）
- **发现性标记本体**（`[SCOPE+]` / `[PROD_TOUCHED]` / `[DESIGN_GAP]`）保持散文，pre-commit PROD_TOUCHED 检测 / check-scope-resolved 跨文件扫描行为与 v0.35 一致（BDD-23）
- `.state.yaml` 校验体系（agate-state-yaml-check.py 除 task_id 正则外的 schema）不动；check-state-transition / agate-state-get 等状态机工具不动
- P0-brief.md 字段（task/known_risks/executor_env/env_constraints）不迁移（P1 §1 范围外）
- **主 checkout 的 hooks 不重装**：worktree 无独立 hooks，commits 仍走 main 的 `.git/hooks`（v0.35，自举 BDD-28 的自然保障）

### 风险在哪

| 风险 | 缓解 |
|------|------|
| 字段级 presence 检测写错 → 新/旧格式误判（BDD-9/10 互斥） | presence 逻辑单一实现 + P3 专测互斥场景 + P1 §3 判别契约原文落地 |
| 354 测试 fixture 重写导致 @test 数漂移（BDD-11） | 改写/重命名但保持计数一致；count-tests.sh 在 P5 全量核验 |
| CHECK 9 锚点表 37 条因脚本改写红（BDD-13） | P4 每改一个脚本即跑 consistency 增量校准；锚点表全量过一遍 |
| frontmatter 嵌套超 3 层（LLM 缩进错误率，BDD-12） | schema 单层/一层列表；校验器断言深度 ≤3 |
| P6 行格式从严后 verifier 旧产出被拦 | check-p6-format.sh 保留 --fix 归一化兼容 + pre-commit 自动修正（v0.35 已有机制） |
| 流 D 硬切后存量旧任务过不了 v2.0 gate | 发布时存量已归档；本 task 用 v0.35 工具规避（BDD-26/28） |
| gate_commands 留正文但 check-gate.sh 改写误碰 4 工具 | 4 工具不改；check-gate.sh P2/P5 分支对 gate_commands 块的调用保持原样 |
| P5_DATA 缓存键（CACHE_KEY）因 gate_commands 相关改动失效 | 本设计不改 gate_commands 位置，预期不失效；P4/P5 验证 + CHANGELOG 记录（P1 隐含需求 #9） |

---

## 3. 方案细化：四流落点（选定方案 A）

### 3.1 流 A：P1/P2 格式迁移 + 双读 + schema 校验器

#### 3.1.1 迁移字段与 frontmatter schema

迁移字段并入文件**已有 frontmatter 块**（`---` 分隔，与 phase/task_id/type/agent 等通用 Header 同块）。全部单层 `key: value` 或一层列表，**嵌套深度 ≤3**（BDD-12，P1 隐含需求 #6）。

**P1-requirements.md 目标 frontmatter**：
```yaml
---
phase: P1
task_id: T001
type: problems
parent: P0-brief.md
trace_id: T001-P1-20260809
status: draft
created: 2026-08-09
agent: analyst
# ── v2.0 机器字段 ──
risk_level: high                  # enum: low/medium/high，必填
phases: [P1, P2, P3, P4, P5, P6, P7, P8]   # list of P\d+，必填
packages: [agate]                 # list，必填
domains: [backend, cli]           # list，必填
# 可选字段：仅在适用时写（不适用即省略，不写 null——presence 语义）
# override: "P2 retained"         # 裁剪声明与执行不一致时
# implicit_coupling: false        # bool；P7 裁剪时声明
# coupling_checklist: [api-schema: checked]  # list；P7 裁剪时必填
# internal_only: true             # bool；P8 裁剪时
# internal_only_reason: "内部工具" # string；P8 裁剪时必填
# 跳过风险: "..."                 # string；裁剪时必填
# design_trivial: true            # bool；P2 候选方案可减为 1 时
# follows_existing_pattern: [agate/scripts/check-state-yaml.sh]  # list
---
```

**P2-design.md 目标 frontmatter**：
```yaml
---
phase: P2
task_id: T001
type: design
parent: P1-requirements.md
trace_id: T001-P2-20260809
status: draft
created: 2026-08-09
agent: architect
# ── v2.0 机器字段 ──
candidate_count: 2                # int ≥1，必填
packages: [agate]                 # list，必填
domains: [backend, cli]           # list，必填
ui_affected: false                # bool，必填
---
```
`gate_commands` / `files_to_read` / `env_constraints` / `minimal_validation` **留正文**（不迁移）。

> **可选字段省略 vs 写 null 的决策**：presence 语义（如 `implicit_coupling:` 存在即阻断 P7 裁剪、`override:` 存在即豁免）要求"字段不适用即省略"。写 `implicit_coupling: null` 会让 pyyaml 解析为 key 存在但值为 None——校验器须将 `null` 视同未声明（§3.1.2 schema 规则 4）。角色卡/模板明确写"可选字段省略，勿填 null"（BDD-24）。

#### 3.1.2 双读工具设计（agate-md-field-get.py）

**判别契约**（P1 §3 隐含需求 #1，BDD-9 vs BDD-10 互斥；**FIND-1 修订：采用方案② 字段级 presence 检测**）：
- **方案①（否决）**：`MIGRATED_KEYS` 扩展为全部迁移字段全集做文件级判别。否决理由：流 B/C 字段（`pass`/`fail`/`blocker_count`/`design_gap_count` 等）与流 A 字段语义不同——P7-consistency.md 的 frontmatter 只含流 B/C 字段（`blocker_count` 等）而不含任何流 A 字段（`risk_level` 等）时，文件级判别会误判"旧格式"→ 回退正则 → 恰好复现 F13/F14 设计要消灭的歧义 grep。全集方案要么把流 B/C 字段塞进同一集合导致"文件级新格式"判定过宽（一个 P6 文件含 `pass` 就触发全部 P1 必填校验），要么仍需按 op 分流，复杂度不降。
- **方案②（采用）**：双读 op 改为**字段级 presence 检测**——op 自身字段在 frontmatter 中存在（key 存在且值非 null）即优先取 frontmatter；不存在则正则回退。判别粒度从"文件"降到"字段"，流 A/B/C 的 frontmatter 字段**天然统一**：P7 文件的 `blocker_count` 在 frontmatter 中 → 双读取 frontmatter；该文件无 `risk_level`（非 P7 字段）→ 该 op 正则回退为空，不影响 P7 判定。旧格式文件（frontmatter 无任何机器字段）→ 所有 op 正则回退，行为与 v0.35 完全一致。**缺点**：无法做"文件级新格式/旧格式"的整文件判定（该校验由校验器 §3.1.3 负责，见下），读取层不需要该判定。
- **schema 校验器的文件级判定保留全集语义**（§3.1.3 判别契约）：校验器按文件名选 schema，frontmatter 解析为 dict 后，**该文件 schema 对应的迁移字段集**（P1 集 / P2 集 / P6 集 / P7 集，即下表的全集按文件名取子集）在 frontmatter 中含任意一个 → 新格式 → 走必填/枚举校验；零个 → 旧格式 exit 0。这样"P7 文件只有 blocker_count"仍走 P7 schema 校验，不漏（FIND-1 核心诉求），而 P1 文件不会被 P6 字段误触发。

**实现伪代码**：
```python
MIGRATED_KEYS_BY_SCHEMA = {
  "P1-requirements.md": {"risk_level","phases","packages","domains","override",
                          "implicit_coupling","coupling_checklist","internal_only",
                          "internal_only_reason","跳过风险","design_trivial",
                          "follows_existing_pattern","need_confirm_resolved",
                          "suggest_resolved","scope_resolved"},
  "P2-design.md":       {"candidate_count","packages","domains","ui_affected"},
  "P6-acceptance.md":   {"pass","fail","ui_affected"},
  "P7-consistency.md":  {"blocker_count","deviation_count",
                          "deviation_critical_count","design_gap_count",
                          "design_gap_reviewed_count"},
}
ALL_MIGRATED_KEYS = frozenset().union(*MIGRATED_KEYS_BY_SCHEMA.values())

def _read_frontmatter(text):
    # 只认文件头 --- 块；无块或解析失败返回 None（由校验器在 pre-commit 拦截坏格式）
    if not text.startswith("---\n"): return None
    end = text.find("\n---", 4)
    if end < 0: return None
    try:
        return yaml.safe_load(text[4:end])
    except yaml.YAMLError:
        return None

def _get(field, regex_fallback, op="FIELD"):
    fm = _read_frontmatter(text)
    # 字段级 presence 检测：frontmatter 是 dict 且 key 存在且值非 null → 取 frontmatter
    if isinstance(fm, dict) and field in fm and fm[field] is not None:
        return _format_value(fm[field], field, op)
    return _regex_fallback(regex_fallback)                # 字段不在 frontmatter → 正则回退
```

> **FIND-1 修订说明**：判别契约从"文件级 MIGRATED_KEYS 全集"改为"**op 字段级 presence 检测**"。核心收益：流 B/C 文件（只有自身字段）不再被误判旧格式回退正则；`ALL_MIGRATED_KEYS` 仅作常量供校验器文件级判定与文档核对用，不参与读取路由。P3 需专测："frontmatter 含 `blocker_count` 但无流 A 字段"的 P7 文件 → `blocker_count` op 走 frontmatter（BDD-19/20 成立）；同时含 `risk_level` 的 P1 文件 → 必填校验触发。

**op 与格式化规则**：
- 现有 op：`risk_level` / `ui_affected` / `phases`（输出格式保持 v0.35 兼容：risk_level→字符串、ui_affected→**归一化小写**、phases→空格连接列表）
- **归一化契约（FIND-4 落地）**：`ui_affected` 的 frontmatter 值经 pyyaml 得 Python `bool`（`true`/`false`）或字符串，`_format_value` 对 bool 字段统一 `str(v).lower()` → 输出**恰好** `"true"` / `"false"`（小写）。消费端 check-p6-evidence.sh:64 / check-p6-provenance.sh:155 均为 `[ "$UI_AFFECTED" = "true" ]` 小写精确匹配，`str(False)` 产出 `"False"` 会失配——故 `.lower()` 必须在 `_format_value` 内完成，不依赖调用方。正则回退路径输出保持 v0.35 原样（已为小写）。P3 专测：frontmatter `ui_affected: true/false` → op 输出 `"true"`/`"false"`（bool 转换各一用例）。
- 新增 op：`candidate_count`（int→str）、`packages` / `domains`（列表空格连接）、`override` / `internal_only` / `internal_only_reason` / `跳过风险` / `design_trivial` / `follows_existing_pattern`（presence 语义：key 存在且值非 null → 输出值，否则空）
- 5 个调用点（check-pruning.sh:16,18 / check-p6-provenance.sh:25,152 / check-p6-evidence.sh:61）**不改**，仍传 `FILE` env + op 名

> **验证（已跑，见 §7）**：frontmatter 含 `risk_level: high` + 正文含 `risk_level: low` → 双读返回 frontmatter 的 "high"（BDD-10）。全角冒号 `risk_level：high` 在 frontmatter 中触发 YAMLError（不静默，BDD-2）。`phases:` 块式列表（`- Pn` 每行）解析为 list（BDD-3）。

#### 3.1.3 frontmatter schema 校验器（agate-frontmatter-check.py + check-frontmatter.sh）

**范式**：完全仿照 `agate-state-yaml-check.py`（pyyaml + schema + 错误行输出，无错误输出空）+ `check-state-yaml.sh`（薄壳：非空输出 → exit 1）。

**agate-frontmatter-check.py 逻辑**：
1. `FILE` env 读文件；按文件名判定 schema（`P1-requirements.md`→P1 schema，`P2-design.md`→P2 schema，`P6-acceptance.md`→P6 schema，`P7-consistency.md`→P7 schema；其他文件不校验 exit 0）
2. 提取文件头 `---` 块；无块 → 旧格式 exit 0（BDD-9 兼容：旧格式文件不触发必填校验）
3. `yaml.safe_load`；YAMLError → 输出错误行（含字段名/行号，BDD-2/4/7），exit 0（薄壳判非空拦截）
4. **非 dict 硬拦截（FIND-5 落地）**：有 frontmatter 块但 `safe_load` 结果**不是 dict**（如单行全角冒号 `risk_level：high` 无 `key: value` 行 → pyyaml 返回 str 而非 dict 且**无 YAMLError**）→ 一律报错"frontmatter 必须为 key: value 映射"（P1/P2 文件；P6/P7 同规则）。此步堵死 BDD-2"不再静默"在"单行全角冒号块"边界的失效（FIND-5）
5. **判别契约**：解析结果 dict 含**该文件 schema 的迁移字段集**（§3.1.2 `MIGRATED_KEYS_BY_SCHEMA`，非全集）任意一个 → 新格式 → 走 schema 校验；否则 exit 0
6. schema 校验规则：
   - 必填（P1：risk_level/phases/packages/domains；P2：candidate_count/packages/domains/ui_affected；P6：pass/fail/ui_affected；P7：blocker_count/deviation_count/deviation_critical_count/design_gap_count/design_gap_reviewed_count）——缺 → 报错（BDD-6）
   - 枚举：risk_level ∈ {low, medium, high}——非法 → 提示合法值（BDD-5）
   - 类型：candidate_count int≥1；ui_affected bool；pass/fail/各 count int≥0；phases/packages/domains list；internal_only/design_trivial bool
   - presence 语义：可选字段 `null` 视同未声明（不参与后续规则）
   - **嵌套深度 ≤3**：任意值深度 >3 → 报错（BDD-12）
7. 错误一行一条，含 `文件名:字段名` 定位；无错误输出空

**check-frontmatter.sh**：`FILE=... python3 agate-frontmatter-check.py`，非空输出 → 打印 + exit 1（与 check-state-yaml.sh:14-26 同构）。

**pre-commit 挂载**（BDD-8，与 check-state-yaml.sh 同机制）：在 `pre-commit-gate.sh` 现有 `check-state-yaml.sh` 调用旁（2a 步骤区）新增——扫描暂存的 `P1-requirements.md` / `P2-design.md` / `P6-acceptance.md` / `P7-consistency.md`，逐个跑 `check-frontmatter.sh`，失败 → exit 1 拦截。**subagent 写坏格式 → gate 直接拦，不靠主 Agent 判断**（HANDOFF §5.2 防造假机制）。

#### 3.1.4 CHECK 9 锚点表重新校准（37 → 38）

- **既有 37 条全量过一遍**（BDD-13）：脚本改写后逐条核对关键词仍存在。涉及锚点的脚本：check-pruning.sh（P2 不可裁剪/risk_level/coupling_checklist/internal_only/SOURCE_FILE_COUNT）、check-gate.sh（NEED_CONFIRM/DESIGN_GAP/agent=main/DESIGN_GAP_REVIEWED/BDD-[0-9]）、check-p6-evidence.sh（ui_affected/md5/去重/VARIANCE_WARNING/AHASH）、check-p6-provenance.sh（EVIDENCE_DIR/EXIT_CODE/dispatch-context）、check-scope-resolved.sh（SCOPE_RESOLVED）、check-changelog.sh（CHANGELOG）、check-state-yaml.sh（state.yaml）、agate-state-yaml-check.py（task_id）、check-tdd-red.sh（formatter/pytest）、pre-commit-gate.sh（PROD_TOUCHED/PROD_NOT_TOUCHED）
- **新增 1 条**：`check-frontmatter.sh` 锚点（desc: frontmatter schema 校验；keywords: frontmatter；callers: pre-commit-gate.sh）——`check_anchor_coverage` 反向覆盖检查要求每个 `check-*.sh` 在锚点表有对应条目（check-protocol-consistency.py:683-713），不新增则 WARNING

> **[SCOPE+] 发现**：新校验器 check-frontmatter.sh 触发 CHECK 9 反向覆盖检查，锚点表必须从 37 增至 38。
> 必须做的理由：`check_anchor_coverage` 对未列入锚点表的 `check-*.sh` 输出 WARNING，且锚点表新增是"脚本改写后重新校准"的题中之义（P1 F10/BDD-13）。
> 影响：BDD-13"锚点表 37 条全量通过"在验收时表述为"既有 37 条全量通过 + 新增 1 条 = 38 条全过，0 ERROR"；P1 基线无需新增 BDD（BDD-13 的 Then 是 0 ERROR，不锁死条数上限）。

#### 3.1.5 测试 fixture 重写（BDD-11，354 个 @test）

- `tests/helpers/fixtures.bash` 的 `create_task_dir`：P1/P2 改为写 frontmatter 版本（risk_level/phases/packages/domains/candidate_count 等入 frontmatter 块，正文保留 BDD 部分）。新增 `--legacy-fields` 选项保留旧格式（正文字段）供 BDD-9 旧格式测试使用
- `add_p1_field` / `add_p2_candidate_count` / `add_p2_review` 等 helper：改为写/改 frontmatter 对应字段
- 15 个受影响 `.bats` 文件（354 个 @test，见正文"客观数字"逐文件汇总）：改写 fixture + 断言，**@test 数逐文件保持**（改写/重命名但不删减）；**3 个 regression 摩擦锚点**（v060-design-gap / v060-p8-internal-only / v060-r4-cached）是"摩擦修复"锚点 → 改写为测 frontmatter 版行为（可行性 §5.3）；**v060-p8-cached（P8 --cached）与 v060-yaml-indent（模板 executor_env，P0 字段不迁移）不是改写对象**，保持不动（FIND-3）
- 新增校验器测试：`unit/check-frontmatter.bats`（新文件，含 BDD-2/4/5/6/7/12 用例）——**594 配平机制（FIND-7）**：
  - **核算口径**：594 = 354（15 受影响文件）+ 240（其余文件）。新增 `check-frontmatter.bats` 用例数记 N；为保证 BDD-11（594 不漂移），**N 必须显式配平**，且配平来源**只允许改造既有断言**（把新校验器覆盖的断言场景并入既有 @test 的断言集，删掉失效断言），**不允许净新增**
  - **具体配平动作（改造而非新增）**：新校验器校验的 6 个行为（BDD-2/4/5/6/7/12）目前分布在 check-gate.bats（101 条中部分）、check-p6-format.bats、agate-md-field-get.bats、check-state-yaml.bats。实施策略：① `check-frontmatter.bats` 的每条用例**对应在受影响文件中删除/合并一条重复覆盖的既有断言**——例如 check-gate.bats 里"P2 四字段缺失"断言与校验器 BDD-6 重复、check-p6-format.bats 里"大小写归一化"断言与新行格式校验重复；② P3 test-designer 在 count-tests.sh 对齐时输出配平表：`新增 N（check-frontmatter.bats）= 移减 M（受影响文件重复断言）`，`N = M` 则 594 不变
  - **兜底**：若 P3 发现 N ≠ M，允许在受影响文件内"合并两条断言为一条"压缩差额（改写而非删减，语义不丢失）——总量必须回落到 594，P5 count gate 核验

### 3.2 流 B：P6/P7 结果结构化（BDD-16..20）

#### 3.2.1 P6 汇总入 frontmatter + 逐条行格式从严

**P6-acceptance.md 目标 frontmatter**：
```yaml
---
phase: P6
task_id: T001
type: acceptance
parent: P5-verification.md
trace_id: T001-P6-20260809
status: draft
created: 2026-08-09
agent: verifier
# ── v2.0 机器汇总 ──
pass: 28                          # int ≥0
fail: 0                           # int ≥0
ui_affected: false                # bool（与 P2 声明一致）
---
```
**逐条结果留正文但格式从严**（评估 §3 折中增强，P1 隐含需求 #10）：行首必须 `- PASS BDD-NN: ...` 或 `- FAIL BDD-NN: ...`（带 BDD 编号），消除"总结行误判"（F11）。

**check-p6-format.sh 升级**：从"大小写归一化 sed"升级为"行格式校验"——
- `--check` 模式：校验每行 `^\s*-\s+(PASS|FAIL)\s+BDD-\d+`；`- PASS: 16` 总结行、`- pass` 小写、全角 `- FAIL：` → 报错（BDD-17）；旧文件小写/全角 → 报"格式偏差，用 --fix 归一化"（保留 v0.35 的归一化能力，但从"自动改写"变为"校验+可修复"）
- `--fix` 模式：保留 v0.35 归一化 sed（小写→大写、全角→半角、总结行→`**Summary**:`）
- pre-commit 在 gate 前自动 `--fix`（pre-commit-gate.sh 2h 步骤，v0.35 已有）

**check-gate.sh P6 分支**：读 frontmatter `pass`/`fail`（经双读工具新 op）判定 `fail=0 && total>0`（BDD-16/18）；frontmatter 无汇总（旧格式）→ 回退现有正文 grep 计数。

**check-p6-provenance.sh 审计 3**（P1 BDD 数 vs P6 结果数）：计数改从严格式 `grep -cE '^\s*- (PASS|FAIL) BDD-[0-9]'`（BDD-17/18——总结行不带 BDD 编号不再计入）；或读 frontmatter `pass+fail` 为总数（新格式），回退从严 grep（旧格式）。**FIND-6 决策（加）**：新格式下增加交叉校验 WARNING——frontmatter `pass+fail` 总数与正文从严行数（`grep -cE '^\s*- (PASS|FAIL) BDD-[0-9]'`）**不一致 → 输出 WARNING**（提示"frontmatter 汇总与正文逐条不符，请复核"，如声明 pass:28 但正文只有 20 条 PASS 行）。WARNING 非阻断（exit 仍 0），属防呆（verifier 自声明 nudge 的提示），**不提升 gate 强度**——语义真实性边界不变（BDD-14/§10）：机器只提示"计数对不上"，不判定"内容造假"。**审计 4/5（vision/EXIT_CODE）**：逐条 PASS 行的证据/vision 引用检查保留正文 grep（行格式从严后仍以 `- PASS BDD-NN:` 行首识别）。

#### 3.2.2 P7 状态入 frontmatter

**P7-consistency.md 目标 frontmatter**：
```yaml
---
phase: P7
task_id: T001
type: consistency
parent: P2-design.md
trace_id: T001-P7-20260809
status: draft
created: 2026-08-09
agent: consistency-reviewer
# ── v2.0 机器计数 ──
blocker_count: 0                  # int ≥0（BDD-19）
deviation_count: 0                # int ≥0（BDD-19）
deviation_critical_count: 0       # int ≥0（DEVIATION-CRITICAL）
design_gap_count: 0               # int ≥0（BDD-20）
design_gap_reviewed_count: 0      # int ≥0（BDD-20）
---
```
正文 `[BLOCKER]` / `[DEVIATION-CRITICAL]` / `[DESIGN_GAP]` / `[DESIGN_GAP_REVIEWED]` **散文标记保留为人类痕迹**，但 gate 判定改读 frontmatter 结构化计数（F13 消除）。

**check-gate.sh P7 分支**：
- BLOCKER/DEVIATION-CRITICAL：读 frontmatter `blocker_count`/`deviation_critical_count` → 皆 0 通过（BDD-19），不再用 `grep -cvE '\[BLOCKER\][:：]?[0-9]+条?$'` 排除总结行
- DESIGN_GAP 配对：读 frontmatter `design_gap_count` / `design_gap_reviewed_count` → reviewed ≥ count 通过，否则拦截（BDD-20），不再用数量相减的 0-vs-0 歧义判定（F14）
- P4 DESIGN_GAP 转抄核对（R2.3）：P4 的 `[DESIGN_GAP:]` 仍从正文 grep（P4-implementation.md 不迁移，发现性标记保持散文 BDD-23）；P7 侧改读 frontmatter `design_gap_count`，`P4_count > frontmatter_gap_count` → 拦截（转抄遗漏）
- 启发式 WARNING（P4 含"设计偏差/gap"关键词但 gap 计数 0）保留正文 grep
- frontmatter 无这些字段（旧格式）→ 回退现有正文 grep 逻辑

#### 3.2.3 P6 dispatch-context 预判检查白名单同步（P1 隐含需求 #11）

`check-p6-provenance.sh:115` 检查 dispatch-context 无 `- PASS/FAIL` 预判，依赖"行首锚定"。P6 结果入 frontmatter 后，dispatch-context 模板示例（如"期望 BDD 全过"）不得误伤 frontmatter 样例。**同步动作**：审计 2 的扫描在排除 AGATE_CARD 块之外，同时排除 `---` frontmatter 块（新增 sed 范围），dispatch-context 模板示例若有 frontmatter 样例则放入 AGATE_CARD 排除区或避免 `- PASS/FAIL` 行首。

### 3.3 流 C：标记状态收尾（BDD-21..24）

#### 3.3.1 P1 标记"已解决/已确认"状态结构化

**P1-requirements.md frontmatter 追加**（可选字段，仅标记存在时写）：
```yaml
# ── v2.0 标记状态 ──
need_confirm_resolved: []         # list[str]：已解决的 NEED_CONFIRM 项（BDD-21）
suggest_resolved: []              # list[str]：已采纳的 SUGGEST 项
scope_resolved: []                # list[str]：已解决的 SCOPE+ 项（BDD-22）
```
正文散文标记（`- [NEED_CONFIRM] ...` / `- [SUGGEST: ...]` / `- [SCOPE_RESOLVED] ...`）**保留为人类痕迹**（F15：三值分级散文痕迹不删，只让机器判定走结构化状态）。

**check-gate.sh P1 分支**：
- 阻塞判定改：正文 `- [NEED_CONFIRM]` 计数 − frontmatter `need_confirm_resolved` 覆盖数 = 未解决数（>0 → exit 1）；或更严格——逐条匹配：正文每条 NEED_CONFIRM 的描述须在 `need_confirm_resolved` 列表中找到对应项，未匹配即阻塞（BDD-21）。**采用逐条匹配**（F14 教训：避免数量相减的歧义）
- SUGGEST WARNING：`suggest_resolved` 已采纳项不重复 WARNING
- typo 兜底（NEED_CONFIRM倾向 / SUGGEST 漏冒号）保留
- frontmatter 无标记字段（旧格式）→ 回退现有 grep 三值分级逻辑

**check-scope-resolved.sh（BDD-22）**：SCOPE+ 跨文件散文扫描**保留**（发现性标记本体保持散文，BDD-23）；闭环判定改读 frontmatter `scope_resolved`（非空即已解决 → 通过；有 SCOPE+ 无 resolved → 拦截）；旧格式回退正文 `[SCOPE_RESOLVED]` grep。

#### 3.3.2 发现性标记保持散文（BDD-23）

`[SCOPE+]` / `[PROD_TOUCHED]` / `[DESIGN_GAP]` **不迁移 frontmatter**（P1 隐含需求 #12，评估 §5.5）：
- pre-commit PROD_TOUCHED 行首锚定检测（pre-commit-gate.sh:130-137）不改
- check-scope-resolved.sh 跨文件扫描（排除 dispatch-context/progress + AGATE_CARD）不改
- 强行结构化会让"运行时意外发现"变成"必须提前知道要声明"，反而漏报

#### 3.3.3 角色卡/模板可复制 frontmatter 模板（BDD-24）

`analyst.md` / `architect.md` / `verifier.md` 角色卡 + `task-files.md` 模板的 P1/P2/P6/P7 产出规格节，贴**可直接复制的完整 frontmatter 样例**（含迁移字段占位 + 注释），样例 YAML 块须通过 pyyaml 解析（v0.31.0 给 P1 加模板验证有效，可行性 §5.1 ③）。phase-cards P1/P2/P6/P7 同步产出规格节。

### 3.4 流 D：任务编号规则改造（BDD-25..27）

#### 3.4.1 校验器硬切（agate-state-yaml-check.py:39）

`^T\d+$` → `^T[A-Z]{2}\d+$`，报错信息同步更新为"（应为 T + 2 个大写字母项目代号 + 数字，如 TAG0001）"。**硬切，不做双格式兼容**（F19，P0-brief 已定）：v2.0 校验器只认新格式。

#### 3.4.2 check-changelog.sh 去短前缀提取（F17，BDD-27）

`check-changelog.sh:14`：
```bash
# 旧：TASK_ID_SHORT=$(echo "$TASK_ID" | grep -oE 'T[0-9]+' | head -1)
TASK_ID_SHORT="$TASK_ID"   # 直接匹配完整 task_id（新格式 TAG0001 完整识别）
```
下游消费点核对（P1 隐含需求 #14）：
- `grep -qE "(^|[^0-9])${TASK_ID_SHORT}( |:|$|,|-)"` —— `TAG0001` 完整 id 含数字，`[^0-9]` 前置边界仍正确
- fallback `grep -qF "$TASK_ID"` 保留
- **连锁影响**：`agate-summary.sh` / `active-tasks.md` / `check-changelog` 其他调用方若用 `T[0-9]+` 提取任务短号 → 同步改直接匹配（P4 grep 全库核对）

#### 3.4.3 文档/模板示例同步

- `active-tasks-template.md` 第 4 条规则改为"新任务编号 = `T{项目代号}{编号}`（项目代号 2 个大写字母对齐 Jira `[A-Z][A-Z]+`，编号动态 `\d+` 3 位起步可扩 6 位）；项目局部命名空间 + 项目代号 + 动态编号"（P0-brief §扩展，BDD-25/26）
- `state-machine.md` / `dispatch-protocol.md` / `role-system.md` 的 task_id 示例（T001）→ 新格式示例（如 TAG0001）
- 本 task 自身 T001 不受影响（自举，BDD-28）

---

## 4. 范围声明（四字段，P2 必填）

packages: [agate]          # 协议本体单一包（v0.40.0 版本 bump 对象 = worktree 的 agate/）
domains: [backend, cli]    # backend=gate 脚本/校验器逻辑；cli=agate-*.py 工具读取层。无 frontend（无 UI）、无 security。
                           # cli 是 backend 域内子语义（P1-review FIND-3 已注明），不触发额外评审映射。
ui_affected: false         # 本任务无显示/交互变化（P0-brief 环境自检已定），无需 E2E/vision 覆盖

## 5. gate 命令（P2 固化，P4-P6 不得修改）

gate_commands:
  P3: "bats agate/tests/unit/ agate/tests/regression/"
  P3_formatter: "generic-tap.sh"
  P5: "bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/ 2>&1 | tail -40"
  P5_consistency: "python3 agate/scripts/check-protocol-consistency.py 2>&1 | tail -30"
  P5_shellcheck: "shellcheck -S warning agate/scripts/*.sh 2>&1 | tail -30"
  P5_count: "bash agate/tests/scripts/count-tests.sh 2>&1 | tail -5"
  P6: "bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/ 2>&1 | tail -40"

> 说明：
> - P3/P5/P6 测试运行器 = bats（TAP 输出），formatter 用 `generic-tap.sh`（bats TAP 协议，assets/formatters/README.md 速查表）；P3 用 formatter 供 check-tdd-red.sh 自动读取 + A/B 类错误分类
> - P5 主命令紧凑输出（tail 兜底，T060 教训：只跑子集可能掩盖预存失败）；consistency/shellcheck/count 作为独立 P5 子命令（P5_* 后缀），主 Agent 需全部执行
> - P3 范围 unit+regression：新校验器测试 + 受影响 fixture 主要落在 unit/ 与 regression/（regression 是"摩擦修复"锚点，改 frontmatter 版行为）
> - project_module 不填：bats 非 python 项目，无 B 类 import 检测需求

## 6. 实现导航（files_to_read，P4 implementer 按需读取）

files_to_read:
  - path: agate/scripts/agate-md-field-get.py
    why: 双读改造核心。frontmatter 提取 + 字段级 presence 检测 + 每 op frontmatter 优先/正则回退 + 新 op
  - path: agate/scripts/agate-state-yaml-check.py
    why: 校验器范式（pyyaml + schema + 错误行输出）；流 D task_id 正则 `^T\d+$` 改 `^T[A-Z]{2}\d+$`（L39）
  - path: agate/scripts/check-state-yaml.sh
    why: check-frontmatter.sh 薄壳同构参照（env 传参 + 非空输出 exit 1）
  - path: agate/scripts/check-gate.sh:67-98, 100-173, 236-254, 255-298
    why: P1 NEED_CONFIRM 分支 / P2 candidate_count+四字段 / P6 / P7 分支的读取点改造（frontmatter + 回退）
  - path: agate/scripts/check-pruning.sh:16-103
    why: 10 个 P1 字段 grep → 双读工具 op 的读取点
  - path: agate/scripts/check-p6-provenance.sh:115, 127-141, 148-186
    why: 审计 2 dispatch-context 预判白名单同步（隐含需求 #11）；审计 3 计数改从严格式；审计 4 ui_affected 走双读
  - path: agate/scripts/check-p6-evidence.sh:58-62
    why: ui_affected 读取点（薄壳不改，双读内部生效）
  - path: agate/scripts/check-p6-format.sh
    why: 从归一化 sed 升级为行格式校验（--check/--fix 双模式）
  - path: agate/scripts/check-scope-resolved.sh:20-45
    why: 闭环判定改读 frontmatter scope_resolved，散文扫描保留
  - path: agate/scripts/check-changelog.sh:14-41
    why: 流 D 去短前缀提取 + 下游消费点核对（隐含需求 #14）
  - path: agate/scripts/pre-commit-gate.sh:52, 140-144, 181-238
    why: 挂载 check-frontmatter.sh（与 check-state-yaml 同机制）；P6 --fix 自动归一化已有逻辑确认
  - path: agate/scripts/check-protocol-consistency.py:439-713
    why: CHECK 9 锚点表（37 条）重新校准 + 新增 check-frontmatter.sh 锚点
  - path: agate/assets/templates/task-files.md:1-19, 123-260
    why: P1/P2/P6 模板贴可复制 frontmatter 样例（BDD-24）
  - path: agate/assets/templates/active-tasks-template.md:76-81
    why: 流 D 编号规则第 4 条更新
  - path: agate/assets/execution-roles/analyst.md, architect.md, verifier.md
    why: 角色卡贴可复制 frontmatter 模板（BDD-24）
  - path: agate/phase-cards/P1-requirements.md, P2-design.md, P6-acceptance.md, P7-consistency.md
    why: 产出规格节同步新 frontmatter 要求
  - path: agate/tests/helpers/fixtures.bash:38-157, 179-301
    why: create_task_dir 写 frontmatter 版本 + add_p1_field/add_p2_candidate_count 改 frontmatter；--legacy-fields 保留旧格式
  - path: agate/tests/scripts/count-tests.sh
    why: 594 基线核验（BDD-11，P5 gate 用）

## 7. 最小验证（minimal_validation）

本方案为**纯代码逻辑**（pyyaml frontmatter 解析 + schema 校验 + 脚本读取点改造），无浏览器/外部系统行为依赖。依赖的内部函数/数据转换：
- `yaml.safe_load`（pyyaml 6.0.1，agate-state-yaml-check.py 已在用，P0-brief §环境自检已核实）
- `agate-md-field-get.py` 现有 3 个 op 的正则（回退路径复用）
- 数据转换：frontmatter dict → 与 v0.35 op 输出一致的字符串（risk_level→str、phases→空格连接 list、ui_affected→`str(v).lower()` 恰好输出 "true"/"false"——FIND-4 归一化契约，见 §3.1.2）

已做的**关键假设最小验证**（本节是 pyyaml 行为的实证，非推测）：

minimal_validation:
  assumption: "frontmatter 块能被 pyyaml 正确解析，且 frontmatter 优先于正文同名"
  method: "10 行 python 脚本验证：① 含中文 key（跳过风险）的 frontmatter 解析 ② 全角冒号 risk_level：high → YAMLError（不静默）③ risk_level:high 无空格 → YAMLError ④ phases 块式列表解析 ⑤ frontmatter 与正文同名（risk_level high vs low）→ 取 frontmatter"
  result: "confirmed"
  note: "②③ 验证了 BDD-2（全角冒号不再静默缺失）与 BDD-4（格式错误报错）的机制；⑤ 验证了 BDD-10（frontmatter 优先）；④ 验证了 BDD-3（phases 块式统一解析）。可选字段 null 视同未声明的 presence 语义已确认需在 schema 规则中显式处理。**FIND-5 补充验证**：单行纯 scalar 块（如仅一行全角冒号、无其它 key:value 行）→ `yaml.safe_load` 返回 str 非 dict、**不报 YAMLError**——已由 plan-eng-review 实测复现；校验器据此新增"frontmatter 块存在但解析结果非 dict → 一律报错"硬拦截（§3.1.3 步骤 4）"

  assumption: "P2-design.md 四字段/候选数从正文移到 frontmatter 后，v0.35 的 grep 读取点会失配——需确认新读取方式"
  method: "读代码验证：check-gate.sh:106（candidate_count grep）、check-gate.sh:138（四字段 grep）在 frontmatter 场景下匹配失败；因此 P2 分支必须改走双读工具新 op 或直接读 frontmatter"
  result: "confirmed"
  note: "这是'移动路由'类最小验证（T086 B1 教训）：frontmatter 字段行首无缩进，`^candidate_count:` 在 frontmatter 内能匹配到（`candidate_count: 2` 顶格）；但四字段 grep `^(packages|domains|ui_affected|gate_commands):` 中 gate_commands 留正文、packages/domains/ui_affected 移 frontmatter → 均能匹配（顶格）。即 v0.35 的 check-gate.sh P2 分支对 frontmatter 形式**可继续工作**；但为统一解析可靠性，仍按 §3.1.2 改走双读工具。P3 需专测此兼容性"

  assumption: "frontmatter 中字段移入后，pre-commit 校验器能在 commit 前拦截坏格式"
  method: "读代码验证 pre-commit-gate.sh 挂载点（2a 步骤区）与 check-state-yaml.sh 同构可复用；新校验器行为由 P3 新增测试覆盖（BDD-6/8）"
  result: "not_needed"
  note: "挂载机制是既有模式（check-state-yaml.sh 同款），无需额外运行时验证；校验器本身的拦截行为由 P3/P5 测试覆盖"

## 8. env_constraints（确认/细化 P0-brief）

env_constraints:
  debug_env: "worktree 里跑测试：cd /home/kity/oclab/agate/.worktrees/v2.0 && bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/（load.bash 自动反推 AGATE_ROOT 到 worktree 本体）。跑 gate/读卡片用 ~/.agate（v0.35.0），改代码/跑测试在 worktree。主 checkout（/home/kity/oclab/agate）禁止改动"
  python_toolchain: "py3.12 + pyyaml 6.0.1 + shellcheck 0.9.0（agate-state-yaml-check.py 在用，新校验器同依赖，无需新装）"
  isolation_check: "verify ~/.agate 指向主 checkout（v0.35.0）且未被本任务改动：readlink ~/.agate = /home/kity/oclab/agate/agate 或等价路径；git -C /home/kity/oclab/agate status 干净；worktree 的 bat 运行经 load.bash 反推 AGATE_ROOT 到 worktree 本体。P5 gate 用此检查确认双工作区隔离未破坏（P0-brief env_constraints 细化，不弱化）"

## 9. BDD 覆盖映射（P1 基线 28 条 → 设计落点）

| BDD | 流 | 设计落点 |
|-----|----|---------|
| BDD-1 机器字段从 frontmatter 统一读取 | A | §3.1.2 双读工具（frontmatter 优先 + 正则回退） |
| BDD-2 全角冒号报错定位 | A | §3.1.3 校验器 pyyaml YAMLError + §7 已验证（risk_level：high） |
| BDD-3 phases 内联/块式统一 | A | §3.1.2 双读 phases op（pyyaml list 解析）+ §7 已验证（块式） |
| BDD-4 缩进错误拦截 | A | §3.1.3 校验器 YAMLError 含行号 |
| BDD-5 枚举非法值拦截 | A | §3.1.3 schema 枚举规则（risk_level） |
| BDD-6 缺必填字段拦截 | A | §3.1.3 必填规则 + §3.1.4 pre-commit 挂载 |
| BDD-7 校验错误可定位 | A | §3.1.3 错误行含字段名/行号 |
| BDD-8 与 state-yaml 同机制接 pre-commit | A | §3.1.4 挂载点与 check-state-yaml.sh 同构 |
| BDD-9 旧格式回退 | A | §3.1.2 字段级 presence 检测（字段不在 frontmatter → 正则回退） |
| BDD-10 frontmatter 优先 | A | §3.1.2 字段级 presence 检测（字段在 frontmatter → 取 frontmatter）+ §7 已验证（同名 high vs low） |
| BDD-11 测试数不漂移 594 | A | §3.1.5 fixture 重写不删减 + P5_count gate |
| BDD-12 嵌套 ≤3 层 | A | §3.1.1 schema 单层/一层列表 + §3.1.3 深度断言 |
| BDD-13 一致性 0 ERROR | A | §3.1.4 CHECK 9 锚点表重新校准（37→38） |
| BDD-14 声明不解决语义真实性 | A | §10（本文件） |
| BDD-15 gate_commands 四工具无回归 | A | §2 不改 + §3.1.1 gate_commands 留正文 + P3 回归测试 |
| BDD-16 P6 汇总入 frontmatter | B | §3.2.1 P6 frontmatter（pass/fail/ui_affected）+ check-gate P6 分支 |
| BDD-17 P6 行格式从严 | B | §3.2.1 check-p6-format.sh 升级（--check/--fix） |
| BDD-18 总结行不计入 | B | §3.2.1 计数改 `- PASS|FAIL BDD-NN:` 格式 + check-p6-provenance 审计 3 |
| BDD-19 P7 BLOCKER/DEVIATION 入 frontmatter | B | §3.2.2 P7 frontmatter + check-gate P7 分支 |
| BDD-20 P7 DESIGN_GAP 配对结构化 | B | §3.2.2 design_gap_count/reviewed_count 配对 |
| BDD-21 P1 标记已解决状态结构化 | C | §3.3.1 need_confirm_resolved 逐条匹配 + check-gate P1 分支 |
| BDD-22 SCOPE_RESOLVED 闭环 | C | §3.3.1 scope_resolved + check-scope-resolved.sh |
| BDD-23 发现性标记保持散文 | C | §3.3.2 SCOPE+/PROD_TOUCHED/DESIGN_GAP 不迁移 |
| BDD-24 角色卡可复制模板 | C | §3.3.3 角色卡 + task-files.md 可复制样例 |
| BDD-25 TAG0001 被接受 | D | §3.4.1 校验器 `^T[A-Z]{2}\d+$` |
| BDD-26 T001 被拒绝（硬切） | D | §3.4.1 校验器硬切，无双格式兼容 |
| BDD-27 check-changelog 完整 task_id | D | §3.4.2 去短前缀 + 下游消费点核对 |
| BDD-28 本 task 自举 v0.35 | D 边界 | 本文件按 v0.35 产出 + ~/.agate 跑 gate + §2 不改主 checkout |

## 10. 语义真实性边界（BDD-14 对应，硬约束 6）

**本文档明确声明：v2.0 结构化改造只提高解析可靠性，不改变 gate 对内容真实性的判断能力。**

- **结构化解决**（解析层）：全角冒号（F1）、缩进错误（F2）、phases 双格式（F3）、grep 计数摩擦（F4）、字段类型/枚举校验（F5）、产出物 YAML 无机器校验（F6）、正则补丁税（F7）、P6 总结行误判（F11）、P7 BLOCKER 计数行歧义（F13）、P7 DESIGN_GAP 0-vs-0 配对歧义（F14）、check-changelog 短前缀提取（F17）、编号空间撞号（F18）
- **结构化不解决**（内容真实性）：BDD-8 单侧/双侧歧义（"数量对但内容映射错"）、candidate_count 虚报（v0.31.0 起即自声明 nudge）、权衡/选择理由关键词（仍是语义匹配）
- **真实性保障机制不变**：继续依赖 subagent 独立上下文 + requirements-review / plan-design-review 独立评审角色（ADR-002/006）
- **gate 强度不升不降**：本设计全部 28 条 BDD 只断言"字段被可靠读取 / 坏格式被拦截 / 编号规则被正确校验"，不断言"gate 能发现内容造假"。**防止"做了结构化就以为 gate 变强"的错觉**（可行性 §5.2）

## 11. 实现完成标志（供 P3/P5/P6 判定）

**流 A 完成**：
- `agate-md-field-get.py` 双读 + 新 op 全部实现；`agate-frontmatter-check.py` + `check-frontmatter.sh` 挂 pre-commit
- BDD-1..10 的测试绿（frontmatter 读取 / 全角冒号 / phases 统一 / 缩进拦截 / 枚举 / 必填 / 定位 / 同机制 / 回退 / 优先）
- BDD-11（count-tests.sh = 594）/ BDD-12（无 >3 层嵌套 schema）/ BDD-13（consistency 0 ERROR）/ BDD-15（四工具回归）通过
- 模板/角色卡可复制 frontmatter 样例落地

**流 B 完成**：P6/P7 frontmatter 字段可读可校验；check-gate P6/P7 分支基于 frontmatter 判定（含旧格式回退）；check-p6-format.sh 行格式校验 BDD-17/18 测试绿

**流 C 完成**：check-gate P1 逐条匹配 resolved；check-scope-resolved 读 frontmatter；发现性标记散文未动（BDD-21/22/23/24 测试绿）

**流 D 完成**：state-yaml 校验器硬切（TAG0001 过 / T001 拒）；check-changelog 完整 task_id；文档/模板编号示例同步（BDD-25/26/27）

**总判据**：P5 全量 bats 过 + shellcheck 0 error + consistency 0 ERROR + count-tests.sh = 594；P6 逐条 PASS/FAIL ≥ 28 条（含 BDD-14 语义边界声明的确认）。

## 12. SCOPE+ 标注

[SCOPE+] 发现：新校验器 check-frontmatter.sh 触发 CHECK 9 反向覆盖检查，锚点表从 37 增至 38（详见 §3.1.4）。
         必须做的理由：`check_anchor_coverage`（check-protocol-consistency.py:683-713）要求每个 `check-*.sh` 在锚点表有对应条目，否则 WARNING；且这是"脚本改写后锚点表重新校准"的题中之义。
         影响：BDD-13 的"37 条"是改造前基线，验收时 38 条全过 + 0 ERROR 即可；P1 基线无需新增 BDD，但 P6 验收措辞需注明"既有 37 条 + 新增 1 条"。

> 注（非 SCOPE+）：P6 dispatch-context 预判检查（审计 2）的 frontmatter 排除是 P1 隐含需求 #11 的实现载体，非新发现——P6 结果入 frontmatter 后，`grep -cE '^\s*- (PASS|FAIL)\b'` 不匹配 frontmatter 的 `pass: N`（无 `- ` 前缀），实测无碍；模板示例若写 `- PASS BDD-NN:` 则在 AGATE_CARD 排除区内。实现时在 check-p6-provenance.sh 审计 2 确认排除范围即可，无需新增 BDD。

## 13. 评审 FIND 回应（P2-review.md 8 条，逐一修订）

> 本文件已按 plan-eng-review（P2-review.md，approved + 8 条非阻塞 FIND）逐条修订。修订均为设计文档级澄清/修正，**不改变**方案 A 架构、candidate_count: 2、四字段（§4）、gate_commands（§5）、语义真实性边界（§10）。以下为逐条回应记录（FIND-N → 修订方式 → 修订后状态）。

### FIND-1（判别契约未覆盖流 B/C 字段）→ 修订 → **已定死**

- **修订方式**：采用评审给出的**方案② 字段级 presence 检测**，否决方案①（MIGRATED_KEYS 全集文件级判别）。
- **修订落点**：§3.1.2 判别契约整节重写 + 伪代码 `_get` 改为 `isinstance(fm, dict) and field in fm and fm[field] is not None → 取 frontmatter`；新增 `MIGRATED_KEYS_BY_SCHEMA`（按文件名分 P1/P2/P6/P7 四组）供校验器文件级判定用，`ALL_MIGRATED_KEYS` 仅为常量/文档核对。§3.1.3 步骤 5 判别契约改为"含该文件 schema 的迁移字段集任意一个 → 新格式"。§9 BDD-9/10 映射同步更新。
- **修订后状态**：✅ 已定死。流 B/C 文件（P7 只有 `blocker_count` 等字段、无流 A 字段）不再被误判旧格式回退正则；P3 需专测该场景（§3.1.2 FIND-1 修订说明 + §3.2.2）。

### FIND-2（调用点数与 agate-extract-context.sh 遗漏）→ 修订 → **已澄清**

- **修订方式**：① 全文"6 个薄壳"→"5 个调用点"（§1 方案 A 影响域/优点/子决策、方案 B 影响域、§3.1.2）；② §2 影响域表新增 `agate-extract-context.sh`（:69,80,88）行。
- **修订落点**：§2 影响域表"上下文摘要"行 + §1 方案 A 优点①。
- **修订后状态**：✅ 已澄清。`agate-extract-context.sh` **保持 grep、不改路由**（决策理由写入 §2：该脚本是上下文摘要工具非 gate 判定点，frontmatter 顶层 key 顶格 grep 仍匹配，保持 grep 兼容新旧格式；BDD-1"统一读取"验收对象是 gate 判定读取点，摘要工具不在判定路径，故不违反 BDD-1 语义）。

### FIND-3（受影响测试 354、regression 摩擦锚点 3 个）→ 修订 → **已修正**

- **修订方式**：全文 `355` → `354`（正文"客观数字"逐文件汇总、§1 方案 B 缺点/矩阵/选择理由、§2 风险行、§3.1.5 标题、§13 参考）；§3.1.5 regression 改写对象明确为 **3 个摩擦锚点**（v060-design-gap / v060-p8-internal-only / v060-r4-cached），v060-p8-cached（P8 --cached）与 v060-yaml-indent（模板 executor_env，P0 字段不迁移）明确**不是改写对象**。
- **修订落点**：§正文客观数字、§3.1.5。
- **修订后状态**：✅ 已修正。pre-commit-hook.bats 实测 42（feasibility 附录 43 已过时），累计 354。

### FIND-4（ui_affected 归一化契约未落地）→ 修订 → **已落地**

- **修订方式**：§3.1.2 op 格式化规则明确归一化契约：`ui_affected` 经 `_format_value` 统一 `str(v).lower()`，输出**恰好** `"true"` / `"false"`（小写）；消费端 check-p6-evidence.sh:64 / check-p6-provenance.sh:155 `[ "$UI_AFFECTED" = "true" ]` 小写精确匹配的依赖关系写明。§7 数据转换同步。
- **修订落点**：§3.1.2 op 与格式化规则 + §7。
- **修订后状态**：✅ 已落地。P3 需专测：frontmatter `ui_affected: true/false` → op 输出 `"true"`/`"false"`（bool 转换各一用例）。

### FIND-5（单行全角冒号块返回 str 非 dict）→ 修订 → **已堵死**

- **修订方式**：§3.1.3 校验器逻辑新增**步骤 4（非 dict 硬拦截）**——有 frontmatter 块但 `safe_load` 结果非 dict（含单行全角冒号块）→ 一律报错"frontmatter 必须为 key: value 映射"。§7 minimal_validation assumption 1 note 补充 FIND-5 验证结论。
- **修订落点**：§3.1.3 步骤 4 + §7。
- **修订后状态**：✅ 已堵死。BDD-2"不再静默"在单行 scalar 块边界不再失效；校验器对 P1/P2/P6/P7 文件统一拦截非 dict 结果。

### FIND-6（审计 3 frontmatter vs 正文交叉校验）→ 决定**加** → **已写入**

- **决策**：加 WARNING。
- **修订方式**：§3.2.1 审计 3 增加交叉校验——新格式下 frontmatter `pass+fail` 总数与正文从严行数不一致 → WARNING（如声明 pass:28 但正文仅 20 条 PASS）。**明确为防呆而非 gate 强度提升**：WARNING 非阻断（exit 仍 0），只提示不判定造假，语义真实性边界不变（§10）。
- **修订落点**：§3.2.1 check-p6-provenance.sh 审计 3。
- **修订后状态**：✅ 已写入。P3 需补该 WARNING 的触发/不触发用例。

### FIND-7（check-frontmatter.bats 数量预算未配平）→ 修订 → **已配平**

- **修订方式**：§3.1.5 新增"594 配平机制"——核算口径：594 = 354（15 受影响）+ 240（其余）；新增 N（check-frontmatter.bats）必须由受影响文件**移减 M 条重复断言**配平，`N = M` 则总量不变；只允许"改造既有断言"（删/并重复覆盖的断言），不允许净新增。给出重复断言实例（check-gate.bats"P2 四字段缺失" vs BDD-6、check-p6-format.bats"大小写归一化" vs 新行格式校验）；兜底允许合并断言压缩差额。
- **修订落点**：§3.1.5。
- **修订后状态**：✅ 已配平。P3 test-designer 据此输出配平表；P5 count gate 核验 594。

### FIND-8（scripts/README.md:68 与 test-plan 附录 A 遗漏）→ 修订 → **已补入**

- **修订方式**：§2 影响域表新增两行：`scripts/README.md`（:68 工具清单表，`agate-md-field-get.py` 条目同步新增 op + 双读语义）、`docs/archived/plans/agate-test-plan-2026-07-01.md` 附录 A（受影响用例数/脚本清单同步 354，防 count-tests 文档漂移检查误报）。
- **修订落点**：§2 影响域表。
- **修订后状态**：✅ 已补入（文档类低风险，不改变协议逻辑）。

## 14. 参考

- P1-requirements.md（28 条 BDD / F1-F19 / 判别契约 / 语义真实性边界）
- P0-brief.md（A+B+C+D 范围 / 9 硬约束 / 流 D 硬切 / v0.40.0 发布）
- /tmp/opencode/feasibility.md（三层结构 / Option A vs B / 折中增强 / 354 测试分布）
- HANDOFF-V2.0.md（scope 决策 / 双工作区铁律 / 已踩坑）
- 现状代码：`~/.agate/scripts/agate-md-field-get.py`、`agate-state-yaml-check.py`、`check-gate.sh`、`check-pruning.sh`、`check-p6-provenance.sh`、`check-p6-evidence.sh`、`check-changelog.sh`、`check-protocol-consistency.py`、`assets/templates/task-files.md`
