---
phase: P2
task_id: TAG0006-ui-ux-quality
type: review
parent: P2-design.md
trace_id: TAG0006-P2-20260817
status: approved
created: 2026-08-17
agent: plan-eng-review
---

# P2 评审（工程/架构维度）— plan-eng-review

> 评审对象：P2-design.md（547 行，candidate_count=4，方案 A 选定）
> 评审范围：多方案探索 / 实现就绪度 / 最小验证 / 数据流与异常路径 / 接口契约 / 测试策略 / 技术债
> 证据：grep 实测 fixtures + 通读 check-gate.py / check-p6-evidence.py / check-p6-provenance.py / agate-md-field-get.py / agate-frontmatter-check.py + 实跑 collect-only（825 tests）

## 总体结论

方案 A（三态硬声明 + 降级链）方向正确，与 P1 的 15 条 BDD 三件套验收方式对齐；数据流（P1 声明→P2 门禁→P6 分档消费）链路完整，GAP 的"像素检测 + 人工复核记录"出口明确不死锁。gate_commands 可达可执行（P3 collect-only / P5/P6 `--tb=no` 实测可达，无 P5_e2e 合理）。minimal_validation 四项假设均有 result（含"纯代码逻辑"声明 + 理由）。

**但存在 2 个阻塞问题**，须 architect 修订后复审：

1. **GAP 分支"P1 无视觉能力声明"的默认行为未定义**（见架构问题 1）——直接威胁 BDD-15 基线不红。
2. **兼容性声明与 fixtures 实况不符**（见架构问题 2）——方案 A 的"既有 P2-design 均 ui_affected:false"前提经 grep 实证不成立。

---

## 架构问题（阻塞级）

### BLOCKER-1：check-p6-evidence / check-p6-provenance 的 GAP 分支缺"无视觉能力声明"默认语义（§2.8 / §2.9 / §11）

P2-design.md §2.8 定义了 available/supplementable 与 GAP 两条证据路径，但**未定义 P1 的 capability_requirements 无 `need` 含 visual/vision 条目时（无视觉能力声明）走哪个分支**。这是本机制的数据流入口，缺口直接影响基线：

- 实测证据：`tests/unit/test_check_p6_evidence.py:_write_ui_p2(td, "true")` 构造 `ui_affected: true` 的 P2-design；`tests/unit/test_check_p6_provenance.py` 多例（test_pv_11/12/13 等）；`tests/integration/test_pre_commit_hook.py:1195` 也写 `ui_affected: true`——这些 fixture 的 P1 均来自 `create_task_dir()`（conftest.py:76，默认 P1 只含 agent/risk_level/phases 三字段，**无 capability_requirements 块**）。
- 现状行为：无视觉能力条目时 P6 走 R1b 强制（截图 PASS 必须引 vision YAML，test_pv_11 断言 exit 1"缺 vision"）。若新逻辑将"无声明"落入 GAP 分支放行（免 vision YAML、改要求复核记录），test_pv_11/12/13 及 integration T086 的 exit code 会变红；若落入 available 分支则行为等同现状（test_pv_11 仍 exit 1，基线保持）。
- §11 断言"available/supplementable 分支语义与既有 R1b 完全一致"只覆盖有声明时；无声明时的兼容默认没有写。**implementer 无法据此确定无声明任务的 P6 行为，BDD-15（基线 825 全绿）无保证。**

**建议（修订方向）**：显式声明"P1 无视觉能力条目 → 视为 available 语义，保留既有 R1b 强制（截图 PASS 须引 vision YAML），GAP 分支仅在 P1 显式声明的 GAP 任务触发"，并在 check-p6-*.py 改动点与单测中固化为兼容回归（构造"ui_affected:true + 无 P1 视觉声明 + 截图无 vision → 断言 exit 1"保持）。

### BLOCKER-2：兼容性声明与 fixtures 实况不符（§0.2 / §2.3 / §6.3 / §10）

P2-design.md 多处声称"既有 P2-design 均 ui_affected:false（除 ui-affected 专用 fixture）"：

- §2.3（line 163）："既有 fixture（full-task/high-risk/paused-task/**vision-blocked** 的 P2-design）均 `ui_affected: false`"
- §6.3（夹具行）："全部 ui_affected:false（除 ui-affected 是 true 但仅用于 P6 测试）"
- §10（line 538）："既有 P2-design 均 ui_affected:false（除 ui-affected 专用 fixture 仅 P6 用）"

**grep 实测（`tests/fixtures/` 全部 5 个 P2-design.md）**：

| fixture | P2-design.md `ui_affected` |
|---------|---------------------------|
| full-task | false |
| high-risk | false |
| paused-task | false |
| ui-affected | **true** |
| vision-blocked | **true** |

即 `vision-blocked/P2-design.md` 也是 `ui_affected: true`，且无 UI 设计节。设计只在 §0.3 风险 2 / §2.3 提到 ui-affected 一个 true 夹具，漏了 vision-blocked。虽然实测 `load_fixture()` 目前仅被 test_check_state_transition 消费（且只取 full-task/.state.yaml），pytest 用例均用自建 `task_dir()` 而非静态 fixtures 目录，因此**基线 825 用例本次不红**——但方案 A 的"基线不误伤"核心论证基于错误的前提描述，且影响面核对清单（BDD-8 交付物 §6.3）对该夹具行的处置标注错误，P7 一致性按此清单核对会漏检 vision-blocked。

**建议（修订方向）**：修正 §0.2/§2.3/§6.3/§10 中的 fixture 描述，显式列入 vision-blocked（同 ui-affected：ui_affected:true、不用于 P2 gate 测试、P6 专用）；明确"新 P2 检查对静态 fixtures 目录不触发"的边界，或在 §6.3 夹具行补 vision-blocked 的免责说明。

---

## 架构问题（非阻塞）

### NOTE-1：P6 双证据三态解析逻辑重复（建议登记 DEBT）

check-p6-evidence.py（§2.8 要新增三态读取）与 check-p6-provenance.py（§2.8 改 R1b）将各自读取 P1 的 capability_requirements 视觉条目解析三态，另有 check-gate.py 的 `_gate_p1_vision_capability`（§2.1）第三处解析。同一"解析 capability 视觉条目 + 三态归一"逻辑三处复制。建议抽公共 helper（agate_common.py 或独立模块）。详见文末 DEBT 建议。

### NOTE-2：BDD-14 单测与 check-p6-evidence 前置检查的顺序交互未声明（§2.13）

check-p6-evidence 的实际执行序是：evidence 非文本 → ≤1KB（exit 1） → md5 去重（exit 1） → 像素方差<50（WARNING exit 2，variance_warning>0 时 exit 2）→ ahash。test_ahash_1 断言 exit 0（有复核记录放行），但构造的两张"同 visual 内容不同像素编码"PNG 若像素方差<50 会先触发方差 WARNING→exit 2，测试会红；若文件≤1KB 先 exit 1。设计未说明生成的测试 PNG 须满足">1KB + 方差≥50（用 PIL 生成非纯色图）"两个前置条件。P3 测试设计需在 test_ahash_* 构造时显式满足，否则单测与脚本行为错位。此项已部分被 §2.13 的"Pillow 生成同像素不同编码 PNG"覆盖，但缺对 1KB/方差两道前置门禁的显式声明。

### NOTE-3：P1 与 P2 对基线用例数表述不一致（823 vs 825）

P1-requirements.md §3 BDD-15 写"既有 823 基线用例"，P2-design.md §2.14/§10 写"825 基线"。实测 `count-tests.sh` 与 `pytest --collect-only` 均为 **825**。P2 数值正确，P1 的 823 为过时值（TAG0011 迁移后已累计）。非阻塞但属同任务文档一致性，建议 P1 后续修订或 P7 一致性检查时对齐为 825。

---

## 测试缺口

- **无声明默认的兼容回归用例缺失**：BLOCKER-1 的默认语义一旦确定，需补一条"ui_affected:true + P1 无视觉能力声明 + 截图 PASS 无 vision → 保持现状 exit 1（check-p6-provenance）"的回填用例，守护基线。
- **vision-blocked fixture 的处置回归**：BLOCKER-2 修正后，建议补/更新一条对静态 fixture 目录的核对用例（或断言 test_check_gate 不消费 fixtures/vision-blocked），防止未来某用例开始直接消费静态 fixtures 触发新 P2 检查而变红。
- **BDD-14 ahash 的 Pillow 缺失分支**：design §2.13 已用 `pytest.importorskip("PIL")` 包裹（平台无关），确认与 test_check_p6_evidence.py 现有"Pillow 无关 30 用例"的平台无关原则一致，无新缺口。✓

## 锁定决策（本评审后确定）

- 方案 A（三态硬声明 + P2 UI 设计节门禁 + P6 分档消费 + GAP 降级链）方向成立，可继续推进——以修订两个 BLOCKER 为前提。
- gate_commands 固化：P3 `--collect-only` / P5/P6 `-q --tb=no` 实测可达（formatter 路径 `agate/assets/formatters/pytest.sh` 存在）；本任务 ui_affected:false 不声明 P5_e2e 合理。✓
- dispatch_plan: {mode: single}：三包强耦合不拆批，理由自洽。✓
- files_to_read：19 项覆盖 P4 实现导航（协议文档脚本双线 + 测试模式参考），量级合理，不构成上下文爆炸。✓

## 技术债建议（若采纳须以标准 DEBT 条目登记，`{AGATE_WORKSPACE}/debt/tech-debt.md`）

```yaml
id: DEBT0005   # 建议编号（登记时以登记簿实际为准）
category: technical
title: P6 双证据三态解析逻辑三处重复（check-gate / check-p6-evidence / check-p6-provenance）
status: open
priority: medium
evidence:
  - path: agate-workspace/tasks/TAG0006-ui-ux-quality/P2-design.md
    note: §2.1 _gate_p1_vision_capability / §2.8 check-p6-evidence 与 check-p6-provenance 各自读取 P1 视觉条目三态
impact: 三处解析口径若漂移（如 GAP 判据扩展）会各自不一致，P6/P1 gate 判定分叉
recommendation: 抽取公共 helper（agate_common.py 新增 read_vision_tri_state(p1_file)），三处复用
closure_criteria:
  - 公共 helper 就位且三处脚本调用同一函数
  - 全量 pytest 825+ 全绿 + consistency 0 ERROR
source: review
created_at: 2026-08-17
task_id: TAG0006-ui-ux-quality
```

---

## 结论

- **结论引用**：P2-design.md §0.2（不改什么）/ §2.1（BDD-3 gate）/ §2.3（BDD-4 gate）/ §2.8（BDD-9 GAP 分档）/ §2.13（BDD-14 ahash 降级）/ §6.3（夹具核对）/ §10（兼容策略）/ §11（断言与缓解）；BDD 编号：BDD-3/4/9/14/15。
- **Status: needs-revision** — 阻塞问题 2 个（BLOCKER-1 GAP 默认语义未定义、BLOCKER-2 兼容声明与 fixtures 实况不符），均可在设计文档层面修订，方案骨架无需推翻。

---

# 复审记录（2026-08-17，二轮）

> 复审对象：architect 对 BLOCKER-1/2 + NOTE-2/3 的修订稿（P2-design.md 当前 555 行）。
> 事件：grep fixtures 实证 + 通读修订节 + 核电基线计数（pytest collect-only = 825）+ 核对 DEBT 登记薄。

## 各修复项核对结论

### B2（BLOCKER-1）— 已彻底解决 ✓

- §2.8 line 234 显式新增「无视觉能力声明的默认语义（兼容回归锚点）」：P1 无 `need` 含 visual/vision 条目 → 视为 **available 语义**（R1b 强制 + blocker_count 保留）；**GAP 分支仅在 P1 显式声明 status: GAP 时触发**，不因"无声明"落入 GAP 放行。
- 兼容回归用例已固化：`test_vision_none_1_no_decl_evidence_no_vision_yaml_exit_1`（§2.8 line 250 单测清单）——构造"ui_affected:true + 无 P1 视觉声明 + 截图 PASS 无 vision YAML → **exit 1**"，明确"对应 test_pv_11 现有断言"（test_check_p6_provenance.py:220-227 实测 `assert returncode == 1` + `"缺 vision"`，语义锚定）。
- §11 line 553 断言已同步：默认 available 语义 + test_vision_none_1 固化 + BDD-15 基线 825 不受影响。
- 实证一致性：test_pv_11/12/13（test_check_p6_provenance.py:220-248）与 integration T086 的 P1 均来自 `create_task_dir()`（默认 P1 无 capability_requirements 块）——正是新默认语义覆盖的"无声明"形态，其现行 exit 1 行为与 available 默认完全吻合。

### B3（BLOCKER-2）— 已彻底解决 ✓

- §0.2 line 45 / §0.3 line 53 / §2.3 line 163 / §6.3 line 471 / §10 line 545 均已将 `vision-blocked` 与 `ui-affected` 并列：均 `ui_affected: true` + 无 UI 设计节 + **不用于 P2 gate 测试（test_check_gate 自建 fixture，不引用静态夹具目录）+ P6 专用**，并声明"新 P2 检查（触发条件仅为 P2 自身 ui_affected:true）不会命中它们"。
- **grep fixtures 实证（5/5 全查）**：

  | fixture | P2-design.md `ui_affected` | P1 domains | 与设计表述 |
  |---------|---------------------------|------------|-----------|
  | full-task | false | 无 | 一致 |
  | high-risk | false | 无 | 一致 |
  | paused-task | false | 无 | 一致 |
  | ui-affected | **true** | 无 | 一致（P6 专用） |
  | vision-blocked | **true** | 无 | 一致（P6 专用） |

- 实证边界：`load_fixture` 全仓仅被 test_check_state_transition.py:47,50 消费（且只取 `full-task/.state.yaml`）；test_check_gate.py 对 `fixtures/` 引用数 = **0**（grep 实证）——"新 P2 检查不命中静态夹具"断言有据。
- 残缺的"u-affected 仅一个 true 夹具"的旧表述已全部清除（grep 复核无残留）。

### N1（NOTE-2：BDD-14 构造前置门禁）— 已解决 ✓

- §2.13 line 322 新增「⚠️ 构造前置门禁（test_ahash_* 共用）」：测试 PNG 须满足 `>1KB`（<1KB 先 exit 1）+ `像素方差 ≥50`（方差<50 先触发方差 WARNING→exit 2）+ **非纯色图**（PIL 生成含内容/噪声/渐变，不能纯色填充），并显式断言生成文件尺寸与方差满足门禁后再进 ahash 断言。test_ahash_1（line 323）同步附"均满足 >1KB + 方差≥50"构造约束。P3 测试设计不再有歧义。

### N2（NOTE-3：基线用例数 823 vs 825）— 已解决 ✓

- P2-design.md 全文档无 "823"（grep 实证），"825" 出现 7 处（§0.2/§2.14/§9/§10/§11）统一。
- 实证：`bash agate/tests/scripts/count-tests.sh`（pytest collect-only 口径）= **825**，与设计一致。P2 侧已统一为实测值 825。

### DEBT0005 — 已登记 ✓

- `agate-workspace/debt/tech-debt.md:110-129` DEBT0005 标准化条目（category/status/priority/evidence/impact/recommendation/closure_criteria/source/created_at/task_id 齐全），与上轮建议条目逐字段一致。

## 上轮通过项复核（未被意外改动）

- §1 候选方案仍为 4（A/B/C/D），保留 nudge 探索 + 选择理由（§1.5 排除式论证）。✓
- §3 gate_commands 未动：P3 collect-only / P5/P6 `--tb=no` / 无 P5_e2e（本任务 ui_affected:false 合理）。✓
- §5.2 minimal_validation 四项已证假设（fixtures P1 均无 frontend domains / ahash 可构造 / capability yaml 可解析 / UI 节标题可 grep）无漂移。✓
- §7 files_to_read 19 项未缩减/扩张，覆盖实现导航。✓
- §8 dispatch_plan: {mode: single} 未动，理由自洽。✓
- §2.13 Pillow 缺失 `pytest.importorskip("PIL")` 平台无关包裹保留。✓
- BDD-3/4/E 单测设计（test_vision_1~4 / test_ui_design_1~4）仍在 §2.1/§2.3。✓

## 残留观察（非阻塞，交后续阶段）

- P1-requirements.md 仍含过时值 "823"（line 63/166/200/299；实测 825）。上轮 NOTE-3 已界定为"P1 后续修订或 P7 一致性检查时对齐"，P2 侧已统一，此处仅留痕提醒 P7 一致性检查覆盖该点。
- test_vision_none_1 的归属文件（evidence vs provenance）未显式指定，但设计已注明"对应 test_pv_11 现有断言"（P6 双证据中 vision YAML 缺失的 exit 1 由 provenance R1b 执行）——P3 测试设计按此归属即可，无歧义。

## 复审结论

- **结论引用**：修订节 §0.2 / §0.3 / §2.3 / §2.8 / §2.13 / §6.3 / §10 / §11；BDD 编号 BDD-3/4/9/14/15；单测锚点 test_vision_none_1 / test_ahash_*；DEBT0005。
- **Status: approved** — 阻塞问题 0 个。BLOCKER-1/2 已在设计文档层面彻底修订并经 fixtures 实证核验，NOTE-2/3 已落实，DEBT0005 已登记，上轮通过项无回归。方案骨架可进入 P3。