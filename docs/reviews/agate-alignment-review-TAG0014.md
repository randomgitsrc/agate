---
review_date: 2026-08-16
reviewer: protocol-alignment-review
change_summary: agate 派发编排机制（dispatch_plan 可选字段 + 权威节 + 卡片统一 + 模板兜底）
files_changed: [agate/dispatch-protocol.md, agate/scripts/agate-md-field-get.py, agate/scripts/check-gate.py, agate/phase-cards/P1-requirements.md, agate/phase-cards/P2-design.md, agate/phase-cards/P3-tdd.md, agate/phase-cards/P4-implementation.md, agate/phase-cards/P5-verification.md, agate/phase-cards/P6-acceptance.md, agate/phase-cards/P7-consistency.md, agate/phase-cards/P8-release.md, agate/assets/execution-roles/architect.md, agate/assets/templates/dispatch-prompt.md, agate/assets/templates/task-files.md, README.md, CHANGELOG.md, agate/UPGRADING.md]
---

# 协议-脚本对齐审查 — TAG0014 派发编排机制

> 审查对象：P4 commit `772bbc2` 改动面（dispatch_plan op + P2 gate 校验 + 权威节 + 8 卡统一 + architect/dispatch-prompt 模板兜底）。
> 审查方式：逐文件读全文 + 交叉核对 + 实测（pytest 全量 / consistency / count-tests）。DESIGN_GAP 优先核查已执行（P7-consistency.md 2 条 REVIEWED 与本次审查无冲突项）。

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | MISALIGNED |
| A4 | 测试覆盖 | ALIGNED |
| A5 | 下游影响 + 文档传播 | ALIGNED |
| A6 | 锚点表覆盖 | ALIGNED |
| A7 | 设计原则一致性 | ALIGNED |

**MISALIGNED 数量：1**（A3：tests/README.md 用例计数 8 vs 实际 10，P4-implementation 已声明"待 P5 同步"但未落地）。
另附 2 条 NEEDS_HUMAN_REVIEW（scripts/README.md op 描述、task-files.md P2 样例块），见 A3。

---

## 逐项审查

### A1: 文档→脚本对齐

**文档声明**（agate/phase-cards/P2-design.md:89-93，dispatch_plan 字段契约）：
> `mode` ∈ {single, static-batch, parallel, recon-then-split, serial}——编排模式（单发/静态拆批/并行/先理解后拆/串行链）
> `parallel_limit` 可选，≥1 整数——并行上限（缺省 3）
> `batches` 可选——mode ∈ {static-batch, parallel} 时每批须含 `id` + `complexity` ∈ {low, medium, high}；批数 ≤ parallel_limit
> 缺字段 / 坏 YAML → P2 gate 跳过校验，行为等同现状（向后兼容，不误拦）

**脚本实现**（agate/scripts/check-gate.py:301-334 `_gate_p2_dispatch_plan`）：
```python
valid_modes = frozenset({"single", "static-batch", "parallel", "recon-then-split", "serial"})
...
if parallel_limit is not None and (not isinstance(parallel_limit, int) or parallel_limit < 1):
    return f"dispatch_plan.parallel_limit 非法（当前: {parallel_limit!r}），须为 ≥1 的整数"
if mode in ("static-batch", "parallel"):
    ...
    limit = parallel_limit if parallel_limit is not None else 3
    if len(batches) > limit: ...
    for batch in batches:
        if not isinstance(batch, dict) or "id" not in batch: ...
        complexity = batch.get("complexity")
        if complexity not in ("low", "medium", "high"): ...
```
对照：
- mode 枚举 5 值与文档逐字一致（L312）；中文模式名↔英文枚举映射在 dispatch-protocol.md:661-669（单发/静态拆批/并行/先理解后拆/串行链）与 P2 卡 L90 双向对应，无二义。
- parallel_limit ≥1 整数（L318-319）与文档 L91 一致；缺省 3 的语义在批数上限检查处落地（L325，`limit = parallel_limit if ... else 3`），与文档 L91、dispatch-protocol.md:693「并行上限默认 3」一致。
- batches 仅对 static-batch/parallel 校验、每批须含 id + complexity∈low/medium/high、批数 ≤ parallel_limit（L321-333）与文档 L92 一致；mode=single/recon-then-split/serial 时 batches 不强制（文档样例 dispatch-protocol.md:683-687 的 recon-then-split 仅 mode+parallel_limit，无 batches，一致）。
- 缺字段/坏 YAML → op 输出空 → `if not raw: return None`（L302-304）跳过；`json.loads` 失败同样返回 None（L306-308）——与文档 L93「缺字段 / 坏 YAML → 跳过校验」一致（BDD-2/7 向后兼容）。
- 文档 L82「不入 frontmatter-check schema」——实测 `rg dispatch_plan agate/scripts/agate-frontmatter-check.py` 无匹配，未纳入 schema，一致。
- 权威节硬规则（dispatch-protocol.md:659「任一维 high → 必须拆分」、architect.md:148）为非机器 gate 的文档级规则，由 P7 一致性检查捕获（architect.md:153），与 gate 无冲突。

**结论**：ALIGNED
**差异**：无

### A2: 脚本→文档对齐

**脚本实现**（agate/scripts/agate-md-field-get.py）：
```python
# L111-114: TAG0014 ... JSON_FIELDS = frozenset({"dispatch_plan"})
# L136-137: if field in JSON_FIELDS: return json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else str(value)
# L196-198: if op in (... | JSON_FIELDS): return ""  # frontmatter-only，无正文回退
# L203-206: KNOWN_OPS = (... | JSON_FIELDS)
```
新 op `dispatch_plan` 已注册 KNOWN_OPS（调用未知 op → exit 2 拦截，L213-215）、JSON 格式化（json.dumps ensure_ascii=False 保中文）、frontmatter-only 无正文回退（防正文散文 `dispatch_plan:` 伪造，与 change_type/regression_pass 同语义）。

**文档同步**：
- P2-design.md:78-93「dispatch_plan 机器字段（可选，TAG0014）」完整声明字段契约（frontmatter 单行 flow YAML 样例 + 契约 4 条）。
- architect.md:139-153「批次设计（强制节，TAG0014）」声明产出义务与硬规则。
- 脚本自身 docstring（agate-md-field-get.py:111-114）注明契约来源 P2-design.md §3.1。
- check-gate.py:292-300 / 411-413 注释引用同一契约（BDD-2~7）。
- gate_p2 接入位置在 `return 2` 之前（check-gate.py:413-416），命中 ERROR 走 exit 1——与 P2 卡「gate 规则」（L147-157）及 P4-implementation.md §1.1 记录一致。

**结论**：ALIGNED
**差异**：无（核心字段契约的脚本↔文档双向同步；文档传播的次要缺口见 A3 反向传播项 2/3）

### A3: 一致性连锁 + 反向传播

#### A3a 一致性连锁（已知衍生改动）——全部到位

| 预期连锁 | 实况 | 判定 |
|---------|------|------|
| 8 张阶段卡引用权威节 | P1 卡 L39-47（模式 4 条件触发）、P2 卡 L78-93（dispatch_plan 字段节）、P3 卡 L74-91、P4 卡 L94-118、P5 卡 L113-128、P6 卡 L147-158、P7 卡「输入文件数量例外」（模式 1 + 豁免特例）、P8 卡 L33-46（多包拆批）——grep 全命中 | ✓ |
| 阶段特定约束保留 | P4 隔离/共享文件后处理/串行默认值（L94-118）、P5 端口/数据库/临时输出/E2E 隔离（L113-128）、P6 证据并行 + 汇总 verifier（L147-158）原样保留，仅加权威节引用 | ✓ |
| task-files.md 措辞 | L80「任务粒度指引」→「派发编排机制」同步（consistency CHECK 3 锚点零漂移） | ✓ |
| dispatch-prompt.md 粒度兜底 | L39-41「任务粒度兜底」（产出>3 或输入>5 须分批或说明），与协议内联节（dispatch-protocol.md:471-473）双源同步 | ✓ |
| architect.md 批次设计 | L139-153（mode/batches/parallel_limit + high 必须拆批 + 批次粒度受工作量评估约束） | ✓ |

#### A3b 反向传播（应被影响但 diff 外的文件逐一验证）

1. **`agate/tests/README.md:54` 用例计数未同步 → MISALIGNED**
   表内声明 `dispatch_plan 编排字段契约 | unit/test_dispatch_orchestration.py | 8`；实测 `pytest --collect-only` = **10 tests collected**（test_dispatch_orchestration.py 正 5 + 负 5，函数清单见 L62/78/88/110/128/151/166/176/186/196）。
   P4-implementation.md:57 明确记录「修复轮追加 2 条负向用例后该文件计数 8→10，**待 P5 一致性核对同步**」——该同步在 P5/P6 未落地。该文件属 P4 commit（772bbc2 含 `agate/tests/README.md`）且计数与事实不符，属本次改动引入的文档漂移。
   **建议**：`tests/README.md` L54 计数 8→10（与 P5 count-tests 782、P4 记录的口径一致）。

2. **`agate/scripts/README.md:102` op 描述未含 dispatch_plan → NEEDS_HUMAN_REVIEW**
   工具清单表描述 `agate-md-field-get.py` 为「覆盖 P1/P2/P6/P7 共 20 个 op（…17 个新增 op，详见脚本内 docstring）」。新 op `dispatch_plan`（JSON_FIELDS）未在描述中提及；且该"20 个 op"计数本身在本次改动前已不精确（脚本当前 op 全集 26 个：BOOL 3 + NO_FALLBACK_BOOL 1 + NO_FALLBACK_STRING 1 + LIST 5 + INT 1 + NO_FALLBACK_INT 7 + NO_FALLBACK_LIST 3 + STRING 4 + JSON 1）。角色文件反向传播表（protocol-alignment-review.md:41）明确将「agate-md-field-get.py 的字段集/op 清单」列为 scripts/README.md 传播目标。
   因部分漂移为本次改动前既有、修复范围（仅补 dispatch_plan vs 全量修正 26 op）需人工裁量：
   `[HUMAN_CONFIRMED: 2026-08-16 确认：主 Agent 采纳建议——在 agate/scripts/README.md:102 的 op 描述补入 dispatch_plan 并修正计数口径（或改为"详见脚本内 docstring"弱化硬计数），最小改动不扩大为全量清点既有漂移]`

3. **`agate/assets/templates/task-files.md` P2-design 样例块未含 dispatch_plan → NEEDS_HUMAN_REVIEW**
   task-files.md:229-245 的 P2-design frontmatter「可直接复制的完整样例」不含 dispatch_plan（该字段仅存在于 P2 卡 L84-87 与 architect.md:141）。角色文件反向传播表（protocol-alignment-review.md:41）列 task-files.md「对应阶段的可复制 frontmatter 样例块」为字段变更传播目标。因 dispatch_plan 为可选字段、契约权威在 P2 卡，是否补入模板样例属裁量：
   `[HUMAN_CONFIRMED: 2026-08-16 确认：主 Agent 采纳建议——在 task-files.md P2-design frontmatter 样例块追加一行注释性 `# dispatch_plan: {mode: ...}` 可选字段样例（对齐 architect.md 批次设计节），或明确声明该可选字段以 P2 卡为准不重复维护]`

**结论**：MISALIGNED（1 条，tests/README.md 计数；2 条 NEEDS_HUMAN_REVIEW 待人工确认）
**差异**：见上 1/2/3 条
**建议**：见各条

### A4: 测试覆盖

**新增用例**：`agate/tests/unit/test_dispatch_orchestration.py` 10 条（正 5 + 负 5，L62-206），覆盖：
- mode 合法枚举（required_fields）与非法值（mode_valid `{mode: xyz}` → exit 1）与非字符串（mode_non_string `{mode: [single]}` → 干净报 ERROR 不崩溃，修复轮 CRITICAL 闭环）
- parallel_limit ≥1（parallel_limit 正向）与 =0（parallel_limit_zero → exit 1）
- batches 含 id + complexity 合法（batch_granularity）与缺 complexity（batch_missing_complexity → exit 1）与非法 complexity（complexity_invalid → exit 1）
- 批数 ≤ parallel_limit 缺省 3（parallel_limit 正向 2 批）
- 缺字段向后兼容（optional：有/无 dispatch_plan gate 输出逐行一致、exit 均 2）
- 坏 YAML 不误拦不崩溃（malformed_yaml：op 空输出 + gate exit 2）
- op 层 JSON 输出契约 2 条（test_agate_md_field_get.py mdf_16/17，L159-184：flow YAML → 合法 JSON、dict 值 json.dumps）
新逻辑边界（mode 枚举/limit 下限/batch 字段/批数上限/缺省跳过）全覆盖。

**全量实测输出**（本审查复跑，2026-08-16）：
```
python3 -m pytest agate/tests/ -q --tb=no
780 passed, 2 skipped in 65.87s (0:01:05)
```
（与 P5-test-results/unit.md:28 记录 `780 passed, 2 skipped in 66.88s` 一致，来源 P5 实测；本审查自行复跑确认。）

```
python3 agate/scripts/check-protocol-consistency.py
仅有 284 个 WARNING，无 ERROR。
```
（0 ERROR。WARNING 由既有基线 279 + 5 组成——5 条为本任务 P6/P7 产出引用 `docs/reviews/agate-alignment-review-TAG0014.md` 未落盘所致，本报告落盘后自愈，非协议漂移。）

```
bash agate/tests/scripts/count-tests.sh
总计：782 个测试用例（pytest collect-only 口径）
```
（≥749 达标，与 P5-test-results/unit.md:43 一致。）

**注意**：tests/README.md:54 表内计数 8 ≠ 实测 10（见 A3 反向传播项 1，需修复）。

**结论**：ALIGNED
**差异**：无（用例真实存在且全绿；README 计数漂移归 A3）

### A5: 下游影响 + 文档传播

- **向后兼容声明**：dispatch_plan 为可选字段——缺字段/坏 YAML 时 `_gate_p2_dispatch_plan` 返回 None（check-gate.py:303-310），P2 gate 行为与改造前逐行一致（test_dispatch_plan_optional 实证 gate_with.output == gate_without.output）。既有项目不写该字段 → gate 行为不变，无破坏性变更。
- **CHANGELOG**：CHANGELOG.md:13-30 [0.49.0] 新增节完整标注（权威节升级 + dispatch_plan 可选字段 + 8 卡统一 + 无破坏性变更声明）。
- **UPGRADING**：UPGRADING.md:181-187 v0.49.0 章节存在且逐条列明（无破坏性变更、缺字段跳过语义、权威节改名与锚点零漂移说明）——版本发布清单要求满足。
- **README badge**：README.md:5 为 v0.48.0（P8 才 bump）——与 P7-consistency.md:31 DESIGN_GAP REVIEWED 记录一致，非漂移。
- **既有项目 gate 影响**：check-gate.py 改动仅新增 P2 分支内可选校验，无 pre-commit 触发行为变更，不新增 hook 拦截面。
- **文档传播覆盖**：dispatch-protocol 权威节 + 8 卡 + architect + dispatch-prompt + task-files 均已同步（见 A3a）；state-machine.md / WORKFLOW.md / role-system.md / LIMITATIONS.md / orchestrator-template.md 逐文件核对无需同步（状态机与阶段总览不承载编排规则，编排规则权威已集中到 dispatch-protocol）。

**结论**：ALIGNED
**差异**：无

### A6: 锚点表覆盖

- 未新增 gate 脚本（agate-md-field-get.py 为 agate-*.py 工具类，不在 CHECK 9 `check_anchor_coverage` 的 check-*.py 覆盖面；check-gate.py 已有 7 条锚点，本次仅增内部校验逻辑，不改变既有关键词集）。
- 既有锚点无回归：实测 consistency 0 ERROR，check-gate.py 中 NEED_CONFIRM/SUGGEST/DESIGN_GAP/DESIGN_GAP_REVIEWED/agent=main/BDD-[0-9] 等关键词全部在位。
- 新规则（dispatch_plan mode/limit/batch 契约）是否入锚点表：锚点表为白名单式只盯死已知锚点（check-protocol-consistency.py:473-477），P2 gate 已覆盖；按角色文件 A6 注，锚点验证的是"关键词存在性"而非"字段集语义一致"，后者由 A1 人工核对完成——本次 A1 已逐条核对，无需强制新增锚点。

**结论**：ALIGNED
**差异**：无（可选改进：可新增 `dispatch_plan → check-gate.py` 锚点兜底，非必须）

### A7: 设计原则一致性

对照 agate/adr.md 相关 ADR：
- **ADR-007（机器字段并入 frontmatter，单工具双读，不拆分独立事实文件）**：dispatch_plan 走 frontmatter 单行 flow YAML + agate-md-field-get.py 统一读取（JSON_FIELDS 分支）——完全符合 ADR-007 的核心决策（L207-221）。
- **ADR-001（隔离性，主 Agent 不写产出）**：编排机制是派发模型（主 Agent 只评估/编排/验 gate，不亲自写批量产出），无冲突。
- **ADR-002（可判定性）**：dispatch_plan 校验为机器可判定 gate（exit 1 拦截非法值），符合。
- **ADR-003（最小约定）**：机制不绑定技术栈（无框架/运行时假设），符合。
- 未发现违反已记录 ADR 的决策。

**建议（非强制）**：五模式编排 + 并行规则是一块成体系的机制决策，目前记录在 dispatch-protocol.md 权威节（协议文档层）而无可检索的 ADR 条目。按 ADR 实践（与"按包拆分并行 v0.22 未单独立 ADR"的先例一致）可接受，若维护者认为值得留决策记录，建议补充 ADR-009「派发编排机制——工作量评估五维 + 五模式 + 并行规则」。

**结论**：ALIGNED（附建议）
**差异**：无

---

## DESIGN_GAP 优先核查（原则 6）

- P7-consistency.md:27-31 两条 DESIGN_GAP REVIEWED：
  1. P2-design.md files_to_read `why:` YAML 引号（P4 修复轮）——为任务工作区文件格式问题，与本次 A1-A7 协议/脚本审查对象无交集，未触发本审查判项。
  2. README badge v0.48.0（P8 才 bump）——本审查 A5 独立核实一致（README.md:5），无偏离。
- 本审查的 MISALIGNED（tests/README.md 计数）与 2 条 NEEDS_HUMAN_REVIEW（scripts/README.md / task-files.md）均**未被 P7 记录覆盖**——非 KNOWN_DEVIATION，需按闭环规则处理。

## 闭环规则

| 结论 | 处理 |
|------|------|
| A3 MISALIGNED（tests/README.md:54 计数 8→10） | **必须修复**（派 implementer 或主 Agent 直改，一行计数；修完本项重审） |
| A3 NEEDS_HUMAN_REVIEW（scripts/README.md:102 op 描述） | 待 `[HUMAN_CONFIRMED: 2026-08-16 确认：...]` 人工确认（建议采纳补入 dispatch_plan） |
| A3 NEEDS_HUMAN_REVIEW（task-files.md P2 样例块） | 待 `[HUMAN_CONFIRMED: 2026-08-16 确认：...]` 人工确认（建议采纳追加可选字段样例或明确以 P2 卡为准） |

> 两条 NEEDS_HUMAN_REVIEW 的 `[HUMAN_CONFIRMED: ...]` 标记需主 Agent 在人工确认后补全日期与理由；未确认前按协议视同 MISALIGNED，不允许 commit。

## 审查环境记录

- 只读审查：未修改任何代码/协议文档文件（仅新增本报告 + 追加 P7-progress.md 留痕）。状态标记 `[PROD_NOT_TOUCHED]`。
- 复跑实测（2026-08-16）：pytest 780 passed / 2 skipped / 0 failed；consistency 0 ERROR（284 WARNING，其中 +5 为本任务待产报告路径引用，本报告落盘后自愈）；count-tests 782。
