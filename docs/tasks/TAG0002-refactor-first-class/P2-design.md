---
phase: P2
task_id: TAG0002-refactor-first-class
type: design
parent: P1-requirements.md
trace_id: TAG0002-P2-20260812
status: draft
created: 2026-08-12
agent: architect
# ── v2.0 机器字段 ──
candidate_count: 2
packages: [agate]
domains: [backend, cli]
ui_affected: false
---

# TAG0002 — 重构一等任务（Phase A）：P2 方案设计

> 输入：P1-requirements.md（8 条 BDD，risk_level=medium，全 8 阶段）+ P1-review.md（approved）+ P0-brief.md（env_constraints/test_cmd）+ review-design-20260812-1428.md 方案己 §5.3 + worktree `agate/` 现有代码逐文件查证（P6 卡片/check-gate.sh/check-p6-*.sh/frontmatter schema/field-get/CI backstop）。
> 角色：architect。本任务为**功能型任务**（为协议新增"重构一等任务"机制），自身不声明 `change_type: refactor`——TDD 红灯、P5 全量回归照常适用于本任务自身。
> 结论摘要：选定"**结构化字段 + 分支 gate**"架构。`change_type: refactor` 入 P1 frontmatter 机器字段体系；P6 refactor 口径 = **行为不变声明 + 全量回归全绿（frontmatter `regression_pass: true` + `P6-evidence/regression.log` 双证）+ 关键路径 BDD 逐条 PASS/FAIL**；`check-gate.sh` P6 按 change_type 分流（refactor 走回归口径，缺省走既有功能口径）；P3 refactor 任务走回归测试设计口径且跳过 TDD 红灯。

---

## 1. 影响域分析（改 / 不改 / 风险）

### 1.1 改什么

| 文件 | 改动 |
|---|---|
| `agate/scripts/check-gate.sh` | P6 分支（L292-322）新增 change_type 分流前置分支（refactor → 校验 regression_pass + regression.log）；P1/P2/P3/P4/P5/P7/P8 分支不动 |
| `agate/scripts/agate-md-field-get.py` | 新增 `change_type`（字符串字段）、`regression_pass`（bool，无正文回退）两个 op |
| `agate/scripts/agate-frontmatter-check.py` | P1 schema：migrated_keys+types+enums 增 `change_type`（枚举 `refactor`，非必填）；P6 schema：migrated_keys+types 增 `regression_pass`（bool，非必填） |
| `agate/phase-cards/P6-acceptance.md` | L4 后新增 refactor 口径分支（行为不变 + 全量回归全绿 + 关键路径验收，禁止伪造功能 BDD）；产出规格节注明 refactor 验收记录三段式结构 |
| `agate/phase-cards/P1-requirements.md` | frontmatter 样例节注明可选 `change_type` 字段及取值（可发现性，P1 §2.6） |
| `agate/phase-cards/P3-tdd.md` | 新增 refactor 回归测试口径说明（测试用例映射 BDD 的说明 + refactor 跳过 TDD 红灯步骤） |
| `agate/scripts/ci-gate-backstop.py` | P3 分支 refactor 感知：change_type=refactor 时跳过 check-tdd-red（exit 2 绿灯会被误判 FAIL） |
| `agate/WORKFLOW.md`（L201）/ `agate/state-machine.md`（L174）/ `agate/dispatch-protocol.md`（P6 派发追加节 + P3 派发追加节） | P6 不可裁剪表述处补充"refactor 换口径非裁 P6"；P3/P6 派发追加 refactor 口径说明（P1 §2.5/§2.6） |
| `agate/assets/execution-roles/verifier.md` | P6 模式补 refactor 口径（行为不变声明 + regression.log 产出 + 禁止伪造功能 BDD） |
| `agate/assets/execution-roles/test-designer.md` | P3 模式补 refactor 回归测试设计说明 |
| `agate/tests/unit/check-gate.bats` 等 | 新增 P6 分流 bats 用例（refactor 正反例 + 缺省向后兼容反证）；`check-frontmatter.bats`/`agate-md-field-get.bats` 补新字段 schema/读取用例 |
| `agate/tests/helpers/fixtures.bash` | 可选：补 `add_p6_regression` helper（写 regression_pass frontmatter + regression.log） |
| `docs/plans/agate-test-plan-2026-07-01.md` 附录 A | 测试用例数漂移同步（新增 @test 后重跑 count-tests.sh 更新） |
| `agate/scripts/check-protocol-consistency.py` | 核对 CHECK9 锚点表、CHECK1（新增 YAML 样例可解析）、CHECK2/3 引用不破坏；如需在 P6 卡片措辞中引用"行为不变"等新关键词则校准锚点（当前锚点 keywords=["P6 不可裁剪"] 不随措辞变化破坏，见 §3.6） |

### 1.2 不改什么（降低风险的关键边界）

- **`no_behavior_change` 语义与全部既有触点不动**：check-pruning.sh、P6-acceptance.md L4 既有"可简化"表述、WORKFLOW/state-machine 的"no_behavior_change 可简化 P6"保留原样。refactor 口径是**新增独立分支**，不是替换 no_behavior_change（P1 §2.1/BDD-6）。
- **check-gate.sh P6 既有判定逻辑（L300-321：frontmatter pass/fail 汇总 / 旧格式正文 BDD 计数回退 / 证据目录非空）逐字节保留**，refactor 分支为纯增量前置分支，缺省（change_type 空）时行为与改造前一致（BDD-2）。
- **check-p6-evidence.sh / check-p6-format.sh / check-p6-provenance.sh 六道审计**不加新检查、不改既有审计（BDD 编号机制对 refactor 不豁免，P1 §2.4）。refactor 的 P6 证据格式与功能任务完全同构（PASS/FAIL 行 + 证据引用 + frontmatter 汇总），仅证据内容口径不同。
- **agate 协议其余 7 个阶段卡片、角色体系、rules/、templates/** 不因本任务重构（回填验证建模对象是历史 commit，不重写其代码）。
- **`~/.agate`（稳定版 v0.40.2）禁止改动**；所有改动只落 worktree `agate/`。

### 1.3 风险

| 风险 | 等级 | 缓解 |
|---|---|---|
| refactor 任务 P6 缺回归证据被放行（伪造"行为不变"声明蒙混） | 中 | `regression_pass` + `regression.log` 双证是 gate 硬校验（exit 1）；provenance 审计 5 校验 regression.log 尾行 `EXIT_CODE: 0`；审计 1c 强制 regression.log 被 PASS 行引用（压缩"造声明不造证据"空间）。语义边界诚实标注（P1 §2.8）：机器只能判"证据存在"，判不了"重构真的没改行为" |
| 缺省路径被新分流误伤（631 用例基线回归） | 中 | refactor 分支仅 `change_type=refactor` 时进入；P5 全量 bats 复跑 + 新增"缺省任务走既有口径"反证用例（BDD-2） |
| refactor 任务 P3 被 TDD 红灯 / CI backstop 误杀（重构无新行为断言，全量即绿） | 中 | P3 卡片/派发说明 refactor 跳过 check-tdd-red；**ci-gate-backstop.py P3 分支 refactor 感知**（[SCOPE+]） |
| P6 验收格式约束冲突：`check-p6-format.sh` 只认 `BDD-N` 编号 PASS 行，回归结果无法单列一行 | 低 | 设计明确：regression.log 由"全量回归全绿"这条关键路径 BDD 的 PASS 行引用（多文件逗号分隔），不新增非 BDD 编号行（§3.2.2） |
| check-protocol-consistency 因措辞变化报 ERROR/WARNING | 低 | §3.6 逐项核对锚点；P5 重跑 0 ERROR |
| 回填验证太重（重跑 631 用例） | 低 | 回填以"fixture 任务目录 + gate 级跑批"实现（§3.7），不重执行历史重构 |

---

## 2. 候选方案与权衡（candidate_count: 2）

### 2.1 方案 A：结构化字段 + 分支 gate（选定）

- `change_type: refactor` 作为 **P1-requirements.md frontmatter 机器字段**（与 risk_level/phases/packages/domains 同块），枚举 `{refactor}`，缺省 = 功能口径。
- `check-gate.sh` P6 分支读取 P1 `change_type` 分流：refactor → 额外硬校验 `P6-acceptance.md` frontmatter `regression_pass: true` + `P6-evidence/regression.log` 存在；缺省 → 既有逻辑一字不改。
- P6 refactor 验收记录 = 三段式（行为不变声明 + 全量回归全绿 + 关键路径 BDD 逐条）。
- P3 refactor 任务走回归测试设计口径，跳过 TDD 红灯（卡片 + ci-gate-backstop 双点声明）。

权衡：
- 优点：gate 驱动的结构化口径，BDD-3/4/6 的"gate 通过/不通过"可机械判定；与既有 v2.0 机器字段体系同构（复用 agate-md-field-get.py 读取通道）；缺省行为由"分支前置 + 空值短路"天然保证。
- 缺点/成本：触及面广（check-gate.sh + md-field-get + frontmatter-check + P1/P3/P6 卡片 + verifier/test-designer 角色 + ci-gate-backstop + bats + count-tests），是"动协议"而非"写文档"的工作量；`regression_pass` 是 verifier 自报字段（self-authored gate 固有局限，provenance 审计部分缓解）。

### 2.2 方案 B：纯文档口径 + 人工分流

- `change_type: refactor` 只在 P1 正文散文声明（不落 frontmatter、不读入机器字段体系）。
- `check-gate.sh` P6 分支**不改**：refactor 任务照走功能 BDD 计数路径。
- P6 refactor 口径只写在 P6-acceptance.md / P6 卡片文档层面（"refactor 任务按行为不变 + 回归全绿验收"），由 verifier / 主 Agent 人工核对回归证据。

权衡：
- 优点：改动面极小（只动卡片文档 + P1 样例），零脚本风险，P5 无需重跑全量回归。
- 缺点：**无法满足 P1 的 3 条 BDD 的可验收性**——BDD-3（"When 对该任务执行 P6 验收 gate → gate 通过"）、BDD-4（"回归失败 → gate 不通过"）、BDD-6（"no_behavior_change 不改变 refactor 判定"）都要求 gate 级机械判定，文档口径下"回归失败拦截"完全依赖 verifier 自觉，BDD-4 的 Then 无法成立；且 check-p6-provenance 审计 3 仍强制 P6 ≥ P1 BDD 数，refactor 任务若被要求走功能口径，审计语义与"禁止伪造功能 BDD"直接冲突。

### 2.3 选择理由（方案 A）

- **BDD 可验收性压倒改动成本**：P1 的 BDD-3/4/6 把验收判定明确绑定到"P6 验收 gate"，方案 B 无法让 gate 机械判定回归失败 → BDD-4 直接落空。方案 A 是唯一能让"回归是硬性组成"（BDD-4）成为二值可判状态的架构。
- **与 v2.0 机器字段体系同构**：change_type 是"决定 gate 行为"的任务类型声明，与 risk_level 同类（gate 读取者），放 frontmatter 复用既有读取/校验通道，符合 P1 §1.2 决策 1（frontmatter）与 P2 派发指引"需与机器字段体系协调"。
- **风险可控**：缺省路径逐字节保留 + 全量 bats 基线（631）复跑兜底；refactor 分支为纯增量。
- 方案 B 的文档口径价值保留：P6 卡片 refactor 分支措辞、verifier 角色说明属于方案 A 的一部分（§3.5），两者不是互斥而是"文档只当油门不当刹车"。

---

## 3. 选定方案详细设计

### 3.1 change_type 字段设计（P1 层，BDD-1/BDD-2）

**字段定义**（P1-requirements.md frontmatter，可选字段，缺省 = 功能口径）：

```yaml
---
phase: P1
# ── v2.0 机器字段 ──
risk_level: medium
phases: [P1, P2, P3, P4, P5, P6, P7, P8]
packages: [agate]
domains: [backend, cli]
# ── v2.0 refactor 任务类型声明（可选，缺省 = 功能任务）──
change_type: refactor     # 当前仅支持 refactor；枚举非法值由 frontmatter schema 拦截
---
```

- **位置**：frontmatter（与 risk_level 同块）。理由：change_type 是 gate 分流读写的机器字段，走既有 `agate-md-field-get.py` 读取通道；正文散文声明无法被 gate 机械读取。
- **取值枚举**：`refactor`（唯一合法值）。`no_behavior_change` **不是** change_type 的取值（P1 §2.1：两者语义方向相反，互补不替代）——SUGGEST #1 提及的"长期将 no_behavior_change deprecate 归并入 change_type"明确超出 Phase A，不做。
- **缺省语义**：frontmatter 无 change_type（存量任务/模板/fixture）→ 功能口径，与改造前完全一致（BDD-2）。
- **机器通道**：
  - `agate-md-field-get.py`：新增 `change_type` op（STRING_FIELDS，读 frontmatter；可选正文正则回退 `change_type:\s*(\S+)`，与 risk_level 同模式）。
  - `agate-frontmatter-check.py` P1 schema：`migrated_keys` 增 `change_type`，`types` 增 `change_type: str`，`enums` 增 `{"change_type": ("refactor",)}`，**不加入 required**。
  - `check-gate.sh` P1 分支不改：P1 gate 不解析 change_type，未知 frontmatter 键不报错（校验器只校验已知键 + 嵌套深度），故"P1 声明 change_type: refactor 时 gate 通过且不报错"（BDD-1）成立——该断言已在本设计的 minimal_validation 中验证。

### 3.2 P6 refactor 验收口径（BDD-3/4/5/6）

#### 3.2.1 P6-acceptance.md 三段式结构（refactor 任务）

refactor 任务的 P6-acceptance.md 在既有 PASS/FAIL 行 + frontmatter 汇总的基础上，固定为三段式：

```yaml
---
phase: P6
task_id: <refactor 任务 id>
type: acceptance
parent: P5-verification.md
trace_id: <task_id>-P6-<YYYYMMDD>
status: draft
created: <YYYY-MM-DD>
agent: verifier
# ── v2.0 机器汇总 ──
pass: N
fail: 0
ui_affected: false
regression_pass: true      # refactor 口径：全量回归全绿声明（change_type=refactor 时 gate 必校验）
---
```

正文三段式（body 的 PASS/FAIL 行沿用既有行首格式 `- PASS BDD-N: {描述} ({证据})`，与功能任务同构，经 check-p6-format.sh --check 校验）：

1. **行为不变声明节**：verifier 自声明"本次重构仅改变内部实现，不改外部行为；判定依据 = 全量回归全绿 + 关键路径 BDD 逐条 PASS；禁止为凑验收数量新增功能性质 BDD"。
2. **全量回归全绿节**：以"全量回归全绿"为一条关键路径 BDD 的 PASS 行（`- PASS BDD-1: 全量回归全绿（重构后完整测试套件 0 失败）(P6-evidence/regression.log)`），其中 regression.log 实跑输出尾行为 `EXIT_CODE: 0`。
3. **关键路径验收节**：其余关键路径行为不变断言 BDD 逐条 PASS/FAIL（每条带证据引用）。

约束（与既有 P6 产物格式契约兼容，全部经现有 check-p6-*.sh 校验，不改审计脚本）：

1. **frontmatter 汇总**：`pass`/`fail`/`ui_affected` 照常必填（frontmatter schema 既有 required）；refactor 任务额外写 `regression_pass: true`（bool，可选字段）。
2. **全量回归证据**：`P6-evidence/regression.log`——全量回归套件实跑输出 + 尾行 `EXIT_CODE: 0`（复用 provenance 审计 5 的既有 EXIT_CODE 约定，审计 5 自动核对"声明 PASS 但日志 exit≠0"的矛盾）。regression.log **必须被一条 PASS 行引用**（满足 provenance 审计 1c"证据文件须被引用"，也满足审计 5 的扫描触发）。
3. **禁止新增非 BDD 编号 PASS 行**：`check-p6-format.sh --check` 只认 `- PASS|FAIL BDD-N` 行，回归结果**不能**单列 `- PASS REGRESSION: ...`（会被判格式违规）——"全量回归全绿"作为一条**关键路径 BDD 的 PASS 行**呈现，多文件证据用逗号分隔（如 `(P6-evidence/regression.log, P6-evidence/bdd-1.log)`）。
4. **BDD 性质**：refactor 任务 P1 的 BDD 是"关键路径行为不变断言"（Given 重构后状态 / When 跑关键路径 / Then 行为与重构前一致），非新增功能断言；P6 逐条 PASS/FAIL 对照（check-p6-provenance 审计 3 的 PASS+FAIL ≥ P1 BDD 数 对 refactor **不豁免**，P1 §2.4）。
5. **禁止伪造功能 BDD**：口径文档显式声明"禁止为凑验收数量新增功能性质 BDD"，verifier 角色/P6 卡片/派发指引三处写明（BDD-5）。

#### 3.2.2 P6 frontmatter schema 同步

`agate-frontmatter-check.py` P6 schema：`migrated_keys` 增 `regression_pass`；`types` 增 `regression_pass: bool`；**不加入 required**（仅在 change_type=refactor 时由 check-gate.sh 条件校验——条件性必填无法在无状态的文件级 schema 校验器里表达，交由 gate 层强制）。P6-acceptance.md 含 pass/fail/ui_affected 即触发新格式校验，regression_pass 存在则验 bool 类型。

### 3.3 check-gate.sh P6 分流（BDD-2/3/4/6）

在现有 P6 分支开头（L292 `P6)` 之后、现 L297 `P6_FILE=...` 之前）插入前置分流；**既有 L300-321 判定逻辑逐字节保留**：

```bash
P6)
    P6_FILE="$TASK_DIR/P6-acceptance.md"
    # ── v2.0 refactor 口径分流（TAG0002 Phase A）──
    # 缺省（未声明 change_type）→ 走既有功能口径，行为与改造前一致（BDD-2）
    CHANGE_TYPE=""
    if [ -f "$TASK_DIR/P1-requirements.md" ]; then
        CHANGE_TYPE=$(FILE="$TASK_DIR/P1-requirements.md" python3 "$SCRIPT_DIR/agate-md-field-get.py" change_type 2>/dev/null || echo "")
    fi
    if [ "$CHANGE_TYPE" = "refactor" ]; then
        REGRESSION_PASS=$(FILE="$P6_FILE" python3 "$SCRIPT_DIR/agate-md-field-get.py" regression_pass 2>/dev/null || echo "")
        if [ "$REGRESSION_PASS" != "true" ] || [ ! -f "$TASK_DIR/P6-evidence/regression.log" ]; then
            echo "GATE P6: change_type=refactor 但缺全量回归证据（须 P6-acceptance.md frontmatter regression_pass: true 且 P6-evidence/regression.log 存在）" >&2
            exit 1
        fi
    fi
    # ↓↓ 既有判定（pass/fail 汇总 / 证据目录非空）原样保留，不随 change_type 变化 ↓↓
```

判定语义（机械，全部在 gate 层，主 Agent 仍 exit 2 自判）：

- **BDD-3**（refactor 无功能 BDD 不被拦）：refactor 分支**不要求**新增功能性质断言，只要求关键路径 BDD 的 PASS/FAIL 行 + 回归双证；关键路径 BDD 走既有 TOTAL>0/FAIL=0 判定。
- **BDD-4**（回归失败 → 不通过）：`regression_pass != true` 或 `P6-evidence/regression.log` 缺失 → **exit 1**；关键路径 PASS 不能豁免（回归检查独立于关键路径 FAIL 判定）。
- **BDD-6**（独立于 no_behavior_change）：分流只看 change_type，不读 no_behavior_change；即使 refactor 任务声明了 no_behavior_change，回归双证仍强制（`[SCOPE+ 验证]`：既有 gate 从不读 no_behavior_change，故无需"解除豁免"代码，仅文档口径声明"no_behavior_change 不豁免回归证据"）。
- **BDD-2**（缺省向后兼容）：CHANGE_TYPE 为空 → 整个前置分支短路，走既有逻辑，判定输出与改造前一致。

### 3.4 P3 回归测试口径（BDD-8）

**P3 卡片（phase-cards/P3-tdd.md）新增 refactor 分支说明**：

- refactor 任务的 P3 测试设计 = **回归测试口径**：复用/保留既有测试用例，标注每条回归用例覆盖了重构涉及的哪些文件/路径；**不新增功能行为断言**（无新行为可断言）。
- refactor 任务 **跳过 check-tdd-red 红灯步骤**：重构无新功能断言，测试套件本就全绿，红灯语义不适用（check-tdd-red 对 refactor 任务会误报 exit 2 绿灯）。回归质量由 P5 全量回归（gate_commands.P5）+ P6 的 `regression.log`（全量回归重跑）兜底。
- P3 gate（check-gate.sh P3）仍为文件存在性检查，不新增脚本逻辑——refactor 的 P3 产出是 P3-test-cases.md（回归口径声明 + 既有用例覆盖映射），文件存在即满足 gate。

**P3 派发指引（P3-dispatch-context-test-designer 模板）追加**：refactor 任务时注明"按回归测试口径设计，不新增行为断言，不跑 TDD 红灯"。

**ci-gate-backstop.py P3 分支 refactor 感知**（[SCOPE+]，否则 refactor 任务在 P3 commit 后被 CI 重跑 check-tdd-red → exit 2 绿灯 → 误报 FAIL）：`phase == "P3"` 且 P1 `change_type == refactor` 时，跳过 check-tdd-red 并输出 `SKIP: refactor 任务，TDD 红灯不适用（回归口径由 P5/P6 全量回归兜底）`。

**test-designer.md 角色**：P3 模式补一条 refactor 回归设计说明（与 P3 卡片同口径）。

### 3.5 可发现性同步（P1 §2.6）

- **P1 卡片样例**（phase-cards/P1-requirements.md frontmatter 样例）：加可选 `change_type: refactor` 注释行，注明取值与"缺省=功能任务"。让 analyst 知道可声明。
- **P6 卡片**（phase-cards/P6-acceptance.md）：新增 refactor 口径分支节（3.2.1 三段式结构 + 禁止伪造功能 BDD + 全量回归双证 + regression.log 由 PASS 行引用），让 verifier 知道按什么口径验收。
- **verifier.md 角色**：P6 模式补 refactor 口径（产出 regression.log + EXIT_CODE: 0 + 被 PASS 行引用 + 三段式报告 + 禁止伪造功能 BDD）。
- **dispatch-protocol.md**：P5/P6 派发追加节（L558-592）补 refactor 口径说明（三段式 + 回归双证 + 禁止伪造功能 BDD）；P3 派发追加节补回归测试口径。
- **WORKFLOW.md / state-machine.md**：P6 不可裁剪表述处（WORKFLOW L201 / state-machine L174）补一句"change_type: refactor 的任务 P6 换用回归口径（换口径 ≠ 裁 P6，P6 仍不可裁剪）"，消除与 refactor 口径的表述冲突（P1 §2.5）。

### 3.6 check-protocol-consistency.py 与协议文案同步（P1 §2.5）

- **CHECK 9 锚点表 L463**（"P6 不可裁剪（no_behavior_change 可简化不可省略）"→ keywords `["P6 不可裁剪"]`）：check-pruning.sh L41 的"P6 不可裁剪"文案**不改**，锚点不破坏。P6 卡片新增 refactor 分支不删"no_behavior_change 可简化"表述，故锚点表无需动。
- **CHECK 4 gate_commands 键集合**：本设计**不新增 gate_commands 键**（P6 回归重跑复用既有 P5 全量命令，refactor 口径不引入新键）→ CHECK 4 不受影响。
- **CHECK 1 YAML 可解析**：P1/P6 卡片新增的 frontmatter 样例（含 change_type/regression_pass 注释行）必须是合法 YAML（注释行 `# ── ...` 用 `#` 前缀，不破坏解析）。
- **CHECK 2/3 引用**：新增/修改的文档不引入指向不存在文件的引用、不引入 `*.md L<N>` 硬编码行号引用。
- **P5 验收**：改动落地后重跑 `python3 agate/scripts/check-protocol-consistency.py`，目标 0 ERROR（新增 WARNING 逐条判定是否可接受）。

### 3.7 回填验证路径（BDD-7）

- **建模对象**：真实历史重构 commit `c182dc3 refactor: trim orchestrator-template.md — reduce duplication, add SELF-GATE.md to fallback`（review-design §5.3 点名示例；git log 已核实存在）。
- **实现方式**：P3 设计一个 bats 用例组（落 `agate/tests/unit/check-gate.bats` 或新增 `agate/tests/regression/refactor-first-class.bats`），用 `create_task_dir` + `add_p1_field change_type refactor` 构造 fixture 任务目录，fixture 的 P1 BDD 全部为**关键路径行为不变断言**（不声明任何新增功能断言），走通 P1 → P3 → P6 三处 gate：
  - P1 gate：change_type 声明不报错、正常 exit 2（BDD-1）；
  - P3 gate：回归口径文件存在性 exit 2；
  - P6 gate：refactor 分支在"regression_pass + regression.log 齐备"时 exit 2（BDD-3/7 主路径）。
- **不重执行历史重构**：c182dc3 已合并，回填验证的对象是"**该重构的产物形状**（改的文件/commit 轮廓）能否以 refactor 类型通过协议 gate"，fixture 忠实反映这一点；"全程未被强制伪造"由 fixture 无功能 BDD + gate 不要求功能 BDD 验证（BDD-7 Then）。
- **止损**（P0 known_risks[0] / P1 §1.2 决策 5）：若 P6 阶段回填验证发现 refactor 口径与既有 P6 gate 冲突难以调和 → 停止，重设计而非硬塞。此边界在 P6 验收报告中记录，不作为可强行通过的 BDD。

---

## 4. 四字段声明

### 4.1 gate_commands（P2 固化，P3-P6 不得修改）

```yaml
gate_commands:
  P3: "bats agate/tests/unit/check-gate.bats"
  P3_formatter: "generic-exit-only.sh"
  P5: "bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/"
  P5_formatter: "generic-exit-only.sh"
  # 无 P5_e2e：ui_affected=false
  # 说明：P6 refactor 口径的"全量回归重跑"复用 P5 全量命令（bats 全量），不新增 gate_commands 键
```

- P3 用 P0-brief 声明的 test_cmd（check-gate.bats，P6 分流新增用例的主落点），bats 失败即非零退出 → generic-exit-only 判红灯（本任务自身是功能任务，TDD 红灯照常适用）。
- P5 为全量套件（sanity + unit + regression + integration），覆盖既有 631 用例 + 新增用例。
- bats 输出逐用例 `ok/not ok` 行，已含通过/失败汇总，无需 `tail` 截断（AGENTS.md 纪律：输出控制在几十行内，主 Agent 跑 gate 只判断过没过，完整诊断留修复 subagent）。

### 4.2 files_to_read（P4 implementer 上下文导航）

```yaml
files_to_read:
  - path: agate/scripts/check-gate.sh:292-322
    why: P6 分支现状，refactor 分流前置分支的插入点；P1 分支 L43-133 参考（change_type 不解析的既有行为）
  - path: agate/scripts/agate-md-field-get.py
    why: STRING_FIELDS / BOOL_FIELDS / NO_FALLBACK_INT_FIELDS 机制；新增 change_type（字符串）、regression_pass（bool 无回退）op
  - path: agate/scripts/agate-frontmatter-check.py:30-102
    why: P1/P6 schema 定义；change_type 加 P1 migrated_keys/types/enums，regression_pass 加 P6 migrated_keys/types
  - path: agate/scripts/ci-gate-backstop.py:109-139
    why: P3 分支 check-tdd-red 触发点；refactor 感知跳过（[SCOPE+]）
  - path: agate/phase-cards/P6-acceptance.md
    why: refactor 口径分支落点（L4 之后）；产出规格三段式结构
  - path: agate/phase-cards/P1-requirements.md:49-72
    why: frontmatter 样例节，加 change_type 可选字段注释
  - path: agate/phase-cards/P3-tdd.md
    why: 回归测试口径说明 + refactor 跳过 TDD 红灯
  - path: agate/dispatch-protocol.md:558-592
    why: P5/P6 派发追加节，refactor 口径说明落点
  - path: agate/WORKFLOW.md:201 与 agate/state-machine.md:174
    why: P6 不可裁剪表述处补"换口径非裁 P6"
  - path: agate/assets/execution-roles/verifier.md 与 test-designer.md
    why: P6/P3 模式 refactor 口径说明
  - path: agate/tests/helpers/fixtures.bash
    why: create_task_dir / add_p1_field / add_frontmatter_field，bats fixture 复用
  - path: agate/tests/unit/check-gate.bats:706-778
    why: 既有 G6.* P6 用例模式，新增 refactor 分流用例参照
  - path: agate/tests/unit/check-frontmatter.bats 与 agate/tests/unit/agate-md-field-get.bats
    why: P1/P6 schema 与 field-get 的既有用例模式，补新字段用例
  - path: agate/scripts/check-p6-provenance.sh
    why: 确认审计 1c/3/5 对 refactor 证据（regression.log 被 PASS 行引用）兼容，不改审计
```

### 4.3 env_constraints（继承并细化 P0-brief，不弱化）

```yaml
env_constraints:
  debug_env: "bash agate/scripts/check-state-yaml.sh docs/tasks/TAG0002-refactor-first-class/.state.yaml"
  test_cmd: "bats agate/tests/unit/check-gate.bats"
  isolation_check: "本任务无外部系统/服务/网络依赖；全部验证在本仓内完成（bats + python3 脚本），不触生产。P5 全量回归在 worktree 内运行。状态标记：本任务为协议自身改造，无生产环境接触 → [PROD_NOT_TOUCHED] {协议 gate 脚本 + 协议卡片改造}，全程未触发 [PROD_TOUCHED]"
```

### 4.4 minimal_validation（T086 B1：涉及 P6 既有判定路径的修改，必须验证"删除/修改后请求流向"）

```yaml
minimal_validation:
  assumption: "check-gate.sh P6 分支新增 change_type=refactor 前置分流后，缺省（未声明 change_type）任务仍走既有功能口径，判定行为与改造前一致；refactor 任务的回归硬校验不误伤缺省路径"
  method: "读代码验证路由流向 + 复跑既有 P6 基线用例：(1) 读 check-gate.sh L292-322 确认分流为纯前置增量分支，仅 change_type=refactor 时进入，空值短路直落既有 L300-321 判定；(2) 复跑 bats -f 'P6' agate/tests/unit/check-gate.bats 确认缺省路径基线 exit 2 行为不变；(3) 读 check-gate.sh P1 分支 L43-133 确认不解析 change_type、agate-frontmatter-check.py 只校验已知键+嵌套深度 → P1 声明 change_type 不报错"
  result: "confirmed"
  note: "纯代码逻辑（bash + python 字段读取/校验），无外部系统依赖。已复跑 12/12 P6 基线用例全绿。缺省路径的'修改后流向'= 前置分支短路跳过 → 既有 BDD 计数路径不变；refactor 路径的'硬校验失败流向'= exit 1 拦截（BDD-4）。'P1 gate 不因 change_type 报错'（BDD-1）已由读代码确认：P1 gate 无该字段解析，frontmatter 校验器对未知键不报错、对 change_type 只做枚举校验。"
```

---

## 5. BDD 覆盖对照（BDD-1..8）

| BDD | 覆盖设计点 | 可验收证据 |
|---|---|---|
| BDD-1（P1 可声明 change_type: refactor） | §3.1 字段设计 + frontmatter schema 枚举 | P1 gate 不报错（minimal_validation 已验）+ bats 用例 |
| BDD-2（缺省向后兼容） | §3.3 缺省短路 + §2.3 | 既有 P6 用例回归 + "缺省任务走既有口径"反证 bats 用例 |
| BDD-3（refactor 走回归口径，无功能 BDD 不被拦） | §3.2/§3.3 refactor 分支 | refactor fixture 走 P6 gate exit 2（bats） |
| BDD-4（回归失败 → 不通过） | §3.3 regression_pass/regression.log 硬校验 | refactor fixture 缺 regression.log → exit 1（bats） |
| BDD-5（口径文档禁止伪造功能 BDD） | §3.2.1 约束 5 + §3.5 P6 卡片/verifier/dispatch 三处声明 | 文档含明确禁止表述 |
| BDD-6（独立于 no_behavior_change） | §3.3 分流只看 change_type + §3.2.1 约束 | refactor+no_behavior_change 声明仍强制回归双证（bats） |
| BDD-7（真实重构回填走 P1-P6） | §3.7 fixture 建模 c182dc3 + P1/P3/P6 gate | 回填 fixture 三处 gate 通过（bats） |
| BDD-8（P3 回归测试口径） | §3.4 P3 卡片/派发说明 + test-designer 角色 | 文档含回归口径说明，P6 可逐条对照 |

---

## 6. 实现完成标志（供 P3 测试设计 / P5 验证使用）

做到以下程度算完成（非步骤脚本，是判定标准）：

1. `check-gate.sh` P6 分支含 change_type 分流：refactor 缺 regression_pass 或 regression.log → exit 1；齐备 → 继续走既有判定；缺省 → 走既有判定（行为不变）。
2. `agate-md-field-get.py` 可读取 `change_type` 与 `regression_pass` 两个新 op。
3. `agate-frontmatter-check.py`：P1 `change_type` 枚举校验（非法值报错），P6 `regression_pass` bool 校验；既有 P1/P6 schema 必填项不变化。
4. P6/P1/P3 三张卡片 + WORKFLOW/state-machine/dispatch-protocol + verifier/test-designer 角色含 refactor 口径说明（§3.5 清单逐项落实）。
5. `ci-gate-backstop.py` P3 分支对 change_type=refactor 任务跳过 check-tdd-red。
6. bats：新增 P6 分流用例（refactor 正例/回归缺失反例/no_behavior_change 混用/缺省兼容）全绿，既有 631 用例全绿；`bash agate/tests/scripts/count-tests.sh` 计数与 `agate-test-plan-2026-07-01.md` 附录 A 同步。
7. `python3 agate/scripts/check-protocol-consistency.py` 0 ERROR。
8. `shellcheck -S warning agate/scripts/*.sh` 对改动的 .sh 无 error。

---

## 7. [SCOPE+] 与风险声明

```
[SCOPE+] 发现：ci-gate-backstop.py 的 P3 分支（L109-139）无条件重跑 check-tdd-red.sh；
          change_type=refactor 任务在 P3 commit 后会被 CI 兜底重跑 → 全量即绿 → exit 2 绿灯
          被误判 FAIL。
          必须做的理由：refactor 任务无新功能断言，TDD 红灯语义不适用；P1 BDD-7/BDD-8 的
          "全程 gate 通过"若不含 CI backstop 则机制不完整，CI 会误杀合法 refactor 任务。
          影响：P1 改动面表格未列 ci-gate-backstop.py，需在实现中一并改动（P3 分支 refactor
          感知跳过）；packages: [agate] 不变。
```

风险声明（诚实标注，P1 §2.8 一致性）：

- `regression_pass` 与"行为不变声明"是 **self-authored 字段**（verifier 自报），机器只能判"证据存在"，判不了"重构真的没改行为"——这是 LIMITATIONS 局限 3 在 refactor 口径下的固有形态，本设计不假装封死（P1 §2.8 判定边界诚实标注），只把客观锚点（全量回归运行结果 + 关键路径 PASS + EXIT_CODE）做硬。
- refactor 口径**不豁免** BDD 编号机制（P1 §2.4/SUGGEST #2）：refactor P1 仍须 ≥1 条"关键路径行为不变断言" BDD，P6 仍逐条对照——避免击穿 provenance 统一基线。
- 本设计不引入新 gate_commands 键、不改 check-p6-*.sh 审计脚本、不改 no_behavior_change 语义，将协议横切面控制在 §1.1 清单内。
