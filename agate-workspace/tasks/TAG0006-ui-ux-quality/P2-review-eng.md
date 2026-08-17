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

---

# SCOPE+ 复审记录（2026-08-17，增补复审轮）

> 复审对象：architect 的 SCOPE+ 增补稿（P2-design.md 增至 740 行）——§2.15 形态声明载体与跨阶段一致性（§2.15.1/§2.15.2/§2.15.3/§2.15.4）+ §2.16 P6 证据形式按形态选择，及 §0.3/§2.1-2.5/§2.8-2.13/§5/§6/§7/§9-§11 的 [BASELINE_CHANGE] 标注补丁；gate_commands（§3）与 dispatch_plan（§8，single）宣称不变。
> 事件：grep fixtures 实证（5/5 全查 P1/P2 字段）+ 通读 check-gate.py / agate-frontmatter-check.py / agate-md-field-get.py / check-p6-evidence.py / check-p6-provenance.py / check-protocol-consistency.py 相关段 + 复核测试对静态 fixtures 的引用面 + 核电基线（count-tests.sh = 825）。
> 环境隔离：本复审仅审不写，未触碰任何产品文件——[PROD_NOT_TOUCHED]

## 一、复审焦点逐项核对

### 1.1 形态声明载体方案（§2.15.1：A frontmatter 可选字段 vs B capability 内嵌）— 选择合理 ✓

- A/B 对比表给出 4 组差异（机器可读性/跨阶段可校验性/presence 语义直观性/YAML 耦合），选 A 的理由自洽且有实证支撑：
  - `agate-md-field-get.py` 已有 frontmatter 优先 + 正则回退的 op 模式（ui_affected op 位于 175-176 行，`_get()` 194-200 行字段级 presence 检测），新增两个 op 成本最低（行级改动 + KNOWN_OPS 注册）。
  - `agate-frontmatter-check.py` P1 schema（31-54 行）`types`/`required` 分离，可选键只进 types + migrated_keys、required 不动在 fixtures 层面不破坏（实证：5 个 fixture P1 frontmatter 均不含形态字段，见 1.2）。
  - presence 语义（缺失=布局型默认）与 P1 BDD-16/17（"需求不绑定技术栈/证据形式必可按形态选"）对齐，无语义冲突。
- B 方案批评（能力与形态语义混杂、P6/P2 从 YAML 提取成本高）成立，选 A 无争议。**nudge 强度满足（候选≥2 + 权衡 + 选择理由）。**

### 1.2 gateway 兼容性实证（新增检查不误伤基线）— 成立 ✓

实测（`tests/fixtures/` 5 个目录全查）：

| fixture | P1 frontmatter | P2-design `ui_affected` | 新检查触发 |
|---------|---------------|------------------------|-----------|
| full-task / high-risk / paused-task | 无 domains、无形态字段 | false（body） | 不触发 |
| ui-affected | 无 domains、无形态字段 | true（body） | P2 检查理论命中但**不被消费** |
| vision-blocked | 无 domains、无形态字段 | true（body） | 同上 |

- `_gate_p1_ui_shape` / `_gate_p1_vision_capability` 触发条件为 P1 domains 含 frontend——全部 fixture P1 无 domains → 不触发。
- `_gate_p2_ui_design_section` 触发条件为 P2 自身 ui_affected=true——ui-affected/vision-blocked 两个 fixtures 会命中，但 grep 实证：`load_fixture` 全仓仅被 test_check_state_transition.py:47,50 消费（且仅取 full-task/.state.yaml）；test_check_gate.py 对 `fixtures/` 引用数 = 0（自建 fixture 模式）→ 新 P2 检查不命中静态夹具，兼容成立，与 §2.3/§6.3 免责段表述一致。
- P6 侧：test_check_p6_evidence.py / test_check_p6_provenance.py 全部自建 task_dir（conftest.py `create_task_dir`，默认 P1 无形态字段）；新读取 P1 形态时缺失→空串→布局型默认→行为与现状完全一致（与 §2.8 默认 available 语义、test_vision_none_1 兼容回归锚点对齐）。
- **BP 基线实跑：`bash agate/tests/scripts/count-tests.sh` = 825**，与设计 §2.14/§9/§10/§11 引用一致。

### 1.3 gate_commands / dispatch_plan 保持不变 — 确认 ✓

- §3 gate_commands 与上轮 approved 稿逐字一致（P3 collect-only / P5/P6 `-q --tb=no` / 无 P5_e2e——本任务 ui_affected:false 不声明合理）。
- §8 dispatch_plan 仍 `{mode: single}`，理由（三包 BDD 三件套强耦合、batch 无独立可验收子目标）自洽；P2-design.md 头部 line 23 显式声明"gate_commands（§3）与 dispatch_plan（§8，single）**不变**"，与正文一致（grep 复核无漂移）。

### 1.4 帧序列/渲染输出对比证据形式在 check-p6-evidence.py 的实现路径 — 清晰可测 ✓

- 代码实证：check-p6-evidence.py 现用 `_find_files`（os.walk 递归）+ 扩展名排除（156-171 行，仅 .md/.txt 排除，.png/.json 天然计入非文本）+ PASS 引用计数 `has_screenshot_ref`（173-175 行，仅匹配 `(screenshots/`）。§2.16 的适配注入点确切：
  - 证据类型识别（§2.16 条目 1）→ 在 156-171 行判定块之上/旁新增"P1 shape 为渲染组件/时序特效 → 须含 frames/ 或 renders/ 或 -tN 截图"的目录规范化检查（形态不匹配 exit 1）。帧/renders 的 .png 已被非文本计数计入，无重复逻辑。
  - 帧序列完整性（条目 2）→ 新增 frames/ 引用解析（`{bdd-id}-{NN}.png` 命名正则）+ 文件 >1KB + 帧号连续性（缺口→WARNING，exit 2 不阻断）。
  - 渲染输出对比（条目 3）→ 新增 diff.json 存在性 + 含量化度量字段检查（缺→exit 1）。
  - 雷同分组豁免（条目 4）→ `_md5_entries`/ahash 判定域扩展至 frames/，按"同 BDD 帧序列组"分组（组内相邻帧豁免、跨组命中降级判定）。
  - 交互自洽性：渲染组件型 PASS 引 `(frames/...` 或 `(renders/...` 时 `has_screenshot_ref`=0 → 既有 screenshots/ 相关门禁不误触发（§2.16 目录约定与 148-263 行既有分支正交，无执行序冲突）。
- 单测可构造性：§2.8 test_render_evid_1~3 / §2.16 test_frame_seq_1 / test_render_diff_1/2 / test_render_evid_4 全部可用 tmp_path + task_dir helper 构造（P1 frontmatter 注入形态字段 + P6-evidence/frames|renders 目录 + 帧/diff 文件），Pillow 缺省时结构性检查无需 PIL（§2.16 条目 5 平台无关声明合理，与现有 `SKIP_NO_PILLOW` 分支同模式）。✓

### 1.5 判据可量化表可落地（§2.15.3）— 可执行 ✓

- 四行判据档（渲染正确性/时序/动效/手势交互）均给出二进制可判定锚点（渲染结果对比+diffs 度量、帧号/时间戳断言、关键帧状态/结束态、旋转角/缩放/位移量化）与禁用主观词表（可读/美观/流畅/平滑/跟手等），与 §2.16 判定锚点列一一映射；requirements-review 打回条款（§2.15.3 末行）为**可机检的文档条文**（打回靠审阅人执行，属 self-authored gate 缓解层次，与本任务既有管理模式一致）。
- P6 判定锚点（§2.16 表第 3 列"判定锚点"）＝帧号连续性 + diff 度量值 vs BDD 阈值 + 时刻序列完整——全部可被证据文件/文件内字段机检，无主观词依赖。**P6 判定锚点可执行、可测。**

### 1.6 原 approved 部分一致性抽查 — 无回归 ✓

- §0.2 保留（含 vision-blocked 修正）；§1 四候选 + nudge 探索保留；§3/§8 未动（见 1.3）。
- BDD-3/4/6/9/13/14 上轮 approved 内容保留，SCOPE+ 均以 `[BASELINE_CHANGE]` 显式标注叠加，未发现原语义被覆盖改写。
- §2.8 默认 available 语义 + test_vision_none_1 兼容回归锚点保留（§11 断言同步，line 737）。
- 上轮锁定决策项（files_to_read 19 项 / P5_e2e 合理 / GAP 降级链 / dispatch single）均未被 SCOPE+ 改动破坏。

## 二、发现的问题（非阻塞 NOTE）

> 全部为非阻塞——不威胁 825 基线（实证见 1.2）、不推翻方案骨架；均为"实现就绪度/契约措辞"精修，P3/P4 落地时须按下列建议执行。

### NOTE-S1（建议 architect 修订 §2.15.1 措辞）：形态字段 op 不应参照 ui_affected 的"正文回退"，应走 NO_FALLBACK frontmatter-only

- §2.15.1 line 390 写"参照 ui_affected op 的 frontmatter 优先 + **正文回退**模式（175-176 行附近）"。ui_affected 的正文回退是为兼容 v0.35 老 fixture（`ui_affected: true` 写在正文，**既有 fixtures 实证如此**）；但 `ui_render_shape`/`ui_ux_dimensions` 是全新字段、**不存在历史正文格式**，本设计自定"presence 语义（缺失=布局型默认）"。
- 若 implementer 按字面加 `_regex_fallback` 分支（`ui_render_shape:\s*(.+)`），正文散文提及"ui_render_shape: 渲染组件型"（如影响面清单/说明段落举例）会被误判为声明，把本应走布局默认的任务翻转成渲染组件型 → 违反 §0.2 line 52 的 presence 保证。仓库内已有反例先例：`change_type`（agate-md-field-get.py 74-79 行注释明确"正文散文提及不得被误判"）+ `dispatch_plan` 同走 NO_FALLBACK。
- **建议**：§2.15.1 措辞改为"参照 `change_type`/`dispatch_plan` 的 frontmatter-only（NO_FALLBACK）模式注册（进 NO_FALLBACK_STRING_FIELDS/NO_FALLBACK_LIST_FIELDS + KNOWN_OPS），不做正文回退"；并配套负向单测（正文写"ui_render_shape:"不触发，见三、测试缺口）。

### NOTE-S2（建议 architect 修订 §2.15.4 P7 行）：`check-protocol-consistency.py` 不读任务产出，I14 "三处一致"以实现载体不匹配

- §2.15.4 P7 行 / §6.2 / §9 写"check-protocol-consistency.py 新增规则（I14 三处形态一致）→ consistency ERROR"。实证：该工具是**仓库级协议结构检查器**（`--root` 指向仓库根，扫描 `agate/` 协议文件，无 task-dir/workspace 输入参数，见 main() 887-898 行），CI 也无任务数据——"某任务 P1/P2/P6 三处形态一致"是**任务级**校验，两者职责不匹配。
- 缓解事实：P1↔P2 已由 gate_p2 形态一致性交叉校验（§2.3，exit 1）、P1↔P6 已由 check-p6-evidence 形态-证据匹配检查（§2.16，exit 1）**机械覆盖**；I14 缺口仅在 P2↔P6 残留对（低风险，转递成立）。
- **建议**：把"三处形态一致"的 P7 落点改为 `gate_p7(task_dir)` 任务级新检查（读 task_dir 内 P1/P2/P6 三处形态比对）或写入 consistency-review subagent 派发指令；check-protocol-consistency.py 只保留**协议文档族**的分类框架/可量化判据条文一致锚点（§6.2 原有 3 条规则，本就属该工具职责）。若不愿改设计，亦可接受由 P7 gate + P2/P6 gate 的组合覆盖（缺口低风险），但须在 §2.15.4 显式声明"P7 行弱化为人工/派发检查"，避免给 P4 implementer 留下"改 repo 工具支持任务扫描"的错误指引。

### NOTE-S3（建议 architect 补一句判定算法）：gate_p2 形态分支的分类优先级未定义，"渲染"字样可误分类布局型

- §2.3 步骤 4 形态分支给关键词集（布局/交互/视觉 vs 渲染组件/画布/图表/... vs 时序/动效/...），但未定义"解析 `渲染形态: <值>` 单值决定分支"还是"任意关键词命中即分支"。若按关键词任意命中，"渲染"是高频词（布局型任务的设计节也可能写"渲染成功"），布局型任务可能被误判进渲染组件分支 → 只查渲染/时序锚点、跳过布局/交互/视觉三组必查（门禁降级）。
- **建议**：补一句"形态分支判定以 `渲染形态:` 声明行的**值**为主判据（值含`布局`/`layout`→布局分支；值含`渲染组件`/`render`/`画布`/`图表`等→渲染组件分支；值含`时序`/`特效`/`动效`→时序分支），关键词集仅用于值缺失时的兜底"。

### NOTE-S4（建议 architect 复核）：P2 schema `ui_design_section` 可选字段冗余 + migrated_keys 翻转语义提示

- §2.3 line 162 / §6.2 拟为 P2 schema 加 `ui_design_section` 可选字段；但 gate_p2 的检查实际是 **body 检测**（`## UI 设计` 节标题 + 形态声明行 + 关键词），无需 frontmatter 标记（同一节自相矛盾："供 P2 gate 读取"而 gate 逻辑未用该字段）。保留该字段会在"frontmatter 标记 + body 节"间制造双源。
- 另：`agate-frontmatter-check.py` 的 migrated_keys 兼具"新格式触发器"语义（223-224 行：frontmatter 含任一 migrated key → 走必填校验）。把新可选键加入 P1 的 migrated_keys 意味着"仅含 ui_render_shape 一个键的 frontmatter"也会被翻转成新格式 → 缺 required 字段报错。**对既有 fixtures 无影响（实证：5 个 fixture P1 frontmatter 均不含形态字段），且真实 frontend 任务因 `domains`（已是 migrated key）必已处于新格式**，故不误伤——但"可选键不破坏既有校验"的表述在此语义下偏乐观。
- **建议**：①若 gate 用 body 检测，删除 `ui_design_section` 字段（消除双源）或显式定义"frontmatter 字段=声明标记、body 节=内容"的双检契约；②P1 形态键明确选择"仅进 types（类型校验）+ 依赖已有 migrated 键翻转"（推荐，presence 更安全）或"进 migrated_keys + 显式声明翻转行为"。

### NOTE-S5（实现提示，非问题）：帧序列完整性"帧号缺口 WARNING 不阻断"与既有 WARNING 语义一致（exit 2），不破坏 BDD-17 验收（PASS 引用存在即不阻）；测试须显式满足 >1KB + 方差≥50 的构造门禁（沿用 §2.13 的 test_ahash_* 前置约束，§2.8/§2.16 未重复声明该门禁，P3 test-designer 须按其继承）。

## 三、SCOPE+ 测试缺口（P3 补）

- **形态字段负向用例**（若采纳 N-S1）：test_agate_md_field_get.py 增"正文散文含 `ui_render_shape: 渲染组件型` 不触发（输出空）"用例，防伪造陷阱。
- **前端任务 schema 兼容用例**（若采纳 N-S4 的 types-only）：test_check_frontmatter.py 增"P1 frontmatter 含形态字段 + 无其他 migrated key → 不翻转块式"用例；现有 test_shape_5（`既有 P1 schema 无形态字段的 fixture → frontmatter-check 通过 → exit 2`）已覆盖无字段场景 ✓。
- **I14 三处一致用例**（若采纳 N-S2 落 gate_p7）：新增"P1/P2 形态一致但 P6 证据形式不匹配"类用例（P1↔P6 反向），guard 三处全链路；若维持"P2/P6 gate 组合覆盖"则需在 test_check_gate.py 补 test_ui_design_7 的 P1 注入形态字段 helper（§7 files_to_read 已预判 conftest 需新增该 helper ✓）。
- 既有缺口继承：§2.13 的 test_ahash_* 构造门禁、§2.8 test_vision_none_1 兼容回归，均未被 SCOPE+ 改变，P3 按原设计落实。

## 四、SCOPE+ 锁定决策

- **形态声明载体锁定 A**（P1 frontmatter 可选字段 `ui_render_shape`/`ui_ux_dimensions`，presence 语义，缺失=布局型默认；P2 UI 设计节复用声明；P6 从 P1 读形态选证据形式）——载体合理、gate 可读、跨阶段一致（P1↔P2 由 gate_p2 机检、P1↔P6 由 check-p6-evidence 机检）。
- **判据可量化档位锁定**（§2.15.3 四档：渲染正确性/时序/动效/手势，均有可量化锚点 + 禁用主观词表），P6 锚点（§2.16 表第 3 列）可机检。
- **证据形式按形态分档锁定**（常规布局型：截图/行为日志；渲染组件型：帧序列 `frames/{bdd-id}-{NN}.png` / 渲染输出对比 `renders/{bdd-id}-{variant}-{actual,reference}.png + diff.{json,png}` / 时序截图 `-tN` 后缀），命名约定写入 verifier.md 输出节 + P6 卡片（共享同一契约）。
- **雷同判定域分组豁免**（同 BDD 帧序列组内相邻帧豁免、跨组雷同触发降级待复核）成立——防动画时序证据误伤，与 BDD-14 不冲突。
- **gate_commands 与 dispatch_plan 保持上轮锁定**（§3/§8），SCOPE+ 不动。

## 五、技术债候选（若采纳 N-S1/N-S2，登记于 `{AGATE_WORKSPACE}/debt/tech-debt.md`）

```yaml
id: DEBT0006   # 建议编号（登记时以登记簿实际为准）
category: technical
title: 形态声明字段的实现载体的 P2 契约措辞需收敛（md-field-get 正文回退 + I14 检查载体）
status: open
priority: medium
evidence:
  - path: agate-workspace/tasks/TAG0006-ui-ux-quality/P2-design.md
    note: §2.15.1 line 390 参照 ui_affected 正文回退（与 presence 语义冲突）；§2.15.4 P7 行 I14 落 check-protocol-consistency.py（工具不读任务产出）；§2.3 line 162 ui_design_section 字段与 body 检测双源
impact: 若按字面实现，正文散文提及形态字段名会误判声明、翻转布局型任务至渲染组件型；I14 P7 行实现指引与工具职责不匹配，P4 implementer 易走弯路
recommendation: ①形态字段 op 走 NO_FALLBACK frontmatter-only（参照 change_type/dispatch_plan）；②I14 三处一致落 gate_p7 任务级检查或 consistency-review 派发指令；③删除/明确定义 ui_design_section 双源契约
closure_criteria:
  - §2.15.1/§2.15.4/§2.3 三处措辞按建议修订
  - 配套负向单测（正文散文不触发 / I14 三处机械比对）落地
  - 全量 pytest 825+ 全绿 + consistency 0 ERROR
source: review
created_at: 2026-08-17
task_id: TAG0006-ui-ux-quality
```

## 六、复审结论

- **结论引用**：SCOPE+ 增补节 §2.15.1（载体 A/+line 390 措辞）/ §2.15.2（维度合法性+扩展维）/ §2.15.3（判据可量化表）/ §2.15.4（gate 收口表，P7 行载体存疑见 NOTE-S2）/ §2.16（证据形式清单+check-p6-evidence 适配+分组豁免）；兼容证据：§0.2/§2.3/§6.3/§10（vision-blocked 已列入）+ fixtures 实证（5 fixture P1 无形态字段/无 domains）+ count-tests=825；BDD 编号：BDD-16/17（新增）+ BDD-1/4/9/6/13（扩展）；实现载体代码实证：agate-md-field-get.py（NO_FALLBACK 模式可用）、agate-frontmatter-check.py（types/migrated_keys 分离）、check-gate.py（gate_p1/p2 挂载点）、check-p6-evidence.py（156-171 行证据类型判定/173-175 行引用计数）、check-protocol-consistency.py（--root 仓库级契约）。
- **Status: approved** — 阻塞问题 0 个。SCOPE+ 增补方向成立：载体选择合理、gate 兼容性经 fixtures 实证成立（825 基线不误伤）、证据形式实现路径清晰可测、判据可量化表可落地、gate_commands/dispatch_plan 保持锁定、原 approved 部分无回归。4 条非阻塞 NOTE（N-S1 正文回退措辞、N-S2 I14 载体、N-S3 形态分支判定算法、N-S4 双源字段/migrated_keys 语义）与 DEBT0006 候选已留痕，P3/P4 按建议落地即可，无需回退 architect 大改。