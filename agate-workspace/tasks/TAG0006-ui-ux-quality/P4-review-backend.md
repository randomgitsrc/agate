---
phase: P4
task_id: TAG0006-ui-ux-quality
type: review
parent: P4-implementation.md
trace_id: TAG0006-P4-20260817
status: approved
created: 2026-08-17
agent: review
---

# P4 实现评审（backend 域）— agate UI/UX 验收质量机制

> 角色：review（偏执 Staff Engineer，Pass 1 CRITICAL + Pass 2 INFORMATIONAL）
> 评审对象：P4-implementation.md 声明的 gate 脚本改动（check-gate.py / check-p6-evidence.py / check-p6-provenance.py / agate_common.py / agate-frontmatter-check.py / agate-md-field-get.py / check-protocol-consistency.py）+ 测试。

## 评审方法（客观查证，非仅读 diff）

- 逐一比对 P2-design.md §2.1-§2.16 设计与实际脚本改动。
- 实跑验证：
  - `python3 -m pytest agate/tests/unit/test_check_gate.py -k "vision or shape or ui_design"` → 20 passed
  - `python3 -m pytest agate/tests/unit/test_check_p6_evidence.py` → 45 passed
  - `python3 -m pytest .../test_check_p6_provenance.py .../test_review_role_docs.py .../test_check_frontmatter.py .../test_agate_md_field_get.py` → 84 passed
  - 兼容回归 `test_pv_11/12/13 + test_vision_none_1` → 4 passed（R1b 无声明默认 available 语义保持，BDD-15 基线不红）
  - `check-protocol-consistency.py` → 0 ERROR（CHECK 11 通过；279 既有 WARNING 非缺陷）
  - `count-tests.sh` → 878（≥749 单调不减）
- 静态扫描全部改动脚本的解析/正则/退出码叠加顺序。

## 结论总览

**Status: rejected（1 个 CRITICAL + 1 个 MEDIUM + 2 个 INFORMATIONAL）**

实现与 P2 设计意图高度一致，绝大多数检查逻辑（P1 vision 三态、P1 形态/维度合法性、P2 UI 设计节、规范化值比对、md5 硬阻断保持不变、退出码叠加顺序）正确且测试充分。但 **check-p6-evidence.py 的 avg-hash 雷同分组（BDD-14 新逻辑）存在文件名/hash 对齐缺陷**，会导致分组错误——既可能误拦合法任务（新声明渲染形态/时序任务被误判雷同找不到复核记录而 exit 1），也可能漏放真实充数（跨 BDD/md5 层面的雷同被错误豁免）。该逻辑是本次 BDD-14 验收核心，不允许带缺陷进入 P5。

---

## Pass 1 — CRITICAL

### CRITICAL-1（check-p6-evidence.py:340-343）：avg-hash 文件名/hash 对齐依赖 `zip(ordered, ahash_lines)`，非图片文件导致错位

**位置**：`agate/scripts/check-p6-evidence.py`，ahash 分组块（`main()` 内 `has_screenshot_ref` 分支）：

```python
ordered = sorted(glob.glob(screenshots_dir + "/*"))      # 340
groups = {}
for f, h in zip(ordered, ahash_lines):                    # 342
    groups.setdefault(h, []).append(os.path.basename(f))  # 343
```

**根因**：`agate-image-check.py ahash`（脚本 `agate-image-check.py:50-52`）对目录内每个文件执行 `_ahash(f)`，且用 `contextlib.suppress(Exception)` **吞掉所有解码失败的异常**（非图片文件 / 损坏图片）。因此当 `screenshots/` 存在**非图片文件（>1KB）**或**PIL 无法解码的图像**时，`ahash_lines` 的元素数 < `ordered` 元素数。`zip()` 静默截断到较短列表，导致**哈希与文件名错位**——真实的重复对（同视觉内容不同字节）被拆散、而无关文件名被错误归入同一哈希组。

**为什么会出现非图片文件**：脚本自身的 `empty_count` 只拦截 ≤1KB 的非图片文件（check-p6-evidence.py:305-308，`if size <= 1024`），**>1KB 的非图片文件不会被拦截**，会一路存活到 ahash 阶段。verifier 在 `screenshots/` 旁放置的行为日志/描述文本（>1KB）即可触发。

**实证复现**（独立构造，非测试夹具）：
```
screenshots/ 含：00_notes.log (3600B 文本) / a_log.png / z_shot.png（a 与 z 为同视觉内容不同压缩 → 真重复对）
agate-image-check ahash 输出仅 2 行（00_notes.log 被 suppress），3 个文件排序为 [00_notes.log, a_log.png, z_shot.png]
zip 后：hash1→[00_notes.log, a_log.png]，hash2→[a_log.png]（z_shot.png 因 zip 截断被丢弃）
真重复对 (a_log.png, z_shot.png) 未被识别成一组；00_notes.log 被错误归入重复组。
```
实测输出：`groups: hash->['00_notes.log','a_log.png'] prefixes={'00_notes.log','a_log.png'}`，`z_shot.png` 完全未进入分组。

**影响**（BDD-14 判定可靠性被破坏）：
- 据文件名排序不同，可能把**真重复**漏判为"组内豁免/非重复"（`ahash_dupes` 计算错误）→ 充数漏放；或把**非重复**误判为雷同且找不到复核记录 → 对合法渲染/时序任务误 exit 1（误拦）。
- `_ahash_group`/`_is_temporal_shot` 的分组豁免逻辑建立在"文件名正确对到哈希"的前提上，前提被破坏则豁免判断全错。

**Fix 建议（交 implementer 落地）**：不要在 check-p6-evidence 侧用 `sorted(glob)` 与子进程输出 `zip` 对齐。应改为「单进程内直接计算 ahash 并同时持有文件名」——将 ahash 计算逻辑内联到 check-p6-evidence.py（或改 agate-image-check.py ahash 输出为 `文件名\t哈希` 成对行，check-p6-evidence 按行解析拿到 (name, hash) 对）。这样天然消除对齐错位，且不新增依赖。现有测试未覆盖此场景——**需新增回归测试**：screenshots/ 混入 >1KB 非图片文件，断言重复对仍被正确分组。

---

## Pass 1 — MEDIUM

### MEDIUM-1（check-p6-provenance.py:322）：GAP 分支 `sys.exit(0)` 短路**全部**后续审计，超出设计声明的"仅放松 vision YAML R1b"

**位置**：`agate/scripts/check-p6-provenance.py:322`（GAP 分支内部 `sys.stderr.write(...R1b 放行...); sys.exit(0)`）。

**问题**：P2 §2.8/§2.9 声明的 GAP 放宽语义是"截图 PASS 不再强制 vision YAML，改验人工复核记录"，即只应放松本条 vision 相关强制。但实现用 `sys.exit(0)` **立即整脚本退出**，跳过：
- **审计 5**（check-p6-provenance.py:351-368）：日志 EXIT_CODE 与 PASS/FAIL 声明一致性——硬检查（exit 1），与 vision 能力无关；
- **审计 6**（397-409）：evidence JSON 与 P6 PASS/FAIL 声明一致性——硬检查（exit 1，agate-evidence-consistency.py）；
- agent 字段 WARNING 收集（374-395）。

对 **任何** vision=GAP 的 ui_affected 任务，上述非 vision 硬检查被静默跳过，可能掩盖真实的日志/证据不一致缺陷。注释的辩护（"后续审计只会误报 WARNING"）不成立——审计 5/6 是 exit 1 硬检查，不是 WARNING。

**Fix 建议**：GAP 分支应只跳过「vision YAML 存在性 + blocker_count」这一子块（即 `else:` 分支的那段），**不要 `sys.exit(0)`**，而是把 `is_gap` 作为该子块的开关，随后正常落入审计 5/审计 6/agent WARNING 流程。

---

## Pass 2 — INFORMATIONAL

### INFO-1（check-gate.py `_gate_p2_ui_design_section`）：layout 分支 `unknown_waived` 一刀切豁免三类关键词

当 `ui_block` 中**任意位置**出现 `"不适用"` 时，`unknown_waived=True`，则 布局/交互/视觉 **三个** checklist 关键词全部豁免（check-gate.py 约第 430 行区域）。设计语义（§2.3）是"维度不适用时显式声明即可豁免**该维度**"。当前实现是：只要声明了任一维度不适用，另两个本应必填的维度也一起被豁免——偏宽松，可能让只写了"布局不适用"的任务跳过交互/视觉校验。建议改为按维度粒度豁免（如分别匹配"布局不适用/交互不适用/视觉不适用"）。低危（self-authored gate，document 层）。

### INFO-2（check-gate.py `_gate_p2_ui_design_section`）：节标题正则要求精确等于 `## UI 设计`

`re.search(r"^#{2,3}\s+UI 设计\s*$", ...)` 要求标题行以"UI 设计"精确结尾（`\s*$`）。若 protocol 文档在标题后附加括号说明（如 `## UI 设计（ui_affected: true 时必含）`），会不匹配导致误拦。当前 P2 规格写明精确标题，故低危；建议放宽为标题**前缀**匹配以防漂移误拦。

---

## 已核验的正确项（供主 Agent 确认不需返工）

- **check-gate.py `_gate_p1_vision_capability`**（BDD-3）：frontmatter domains 含 frontend 才触发；`read_vision_tri_state` 与本地兜底解析一致；缺失→exit 1、非法 status→exit 1、合法 GAP→exit 2。测试 `test_vision_1~4` 全过。
- **check-gate.py `_gate_p1_ui_shape`**（BDD-16）：domains 含 frontend 触发；双字段缺失→通过（presence 语义，不红基线）；shape 有而 dims 空→exit 1；扩展维度须在 BDD 标题出现。测试 `test_shape_1~5` 全过。
- **check-gate.py `_gate_p2_ui_design_section`**（BDD-4）：ui_affected:true 触发；缺节/缺形态声明/按形态缺 checklist→exit 1；`_canonical_shape` 规范化值/同义映射比对（§2.15.1）正确；`test_ui_design_1~9`（含规范值正例、同义映射正例）全过。**兼容**：既有 ui-affected/vision-blocked fixtures 均 P2 专用、不用于 P2 gate 测试，未误伤。
- **check-p6-evidence.py 退出码叠加顺序**（§2.13）：① 雷同无复核记录→exit 1（优先于方差）；② 雷同有记录+方差 WARNING→exit 2；③ 雷同有记录无方差→exit 0；④ 无雷同仅方差→exit 2。与设计完全一致。**md5 硬阻断语义不变**（315-327）。
- **check-p6-evidence.py GAP 降级证据路径**（BDD-9）：vision=GAP 时截图 PASS 须引 `manual-review:` 且文件存在，缺→exit 1。测试 `test_vision_gap_1/2` 过。
- **check-p6-evidence.py 证据形式按形态**（BDD-17）：render_component/temporal_effects 形态要求 frames//renders/-tN，`renders/` 须引 actual+diff.json 且 diff 含量化度量。测试 `test_render_evid_1~4 / test_render_diff_1~2 / test_time_seq_1` 全过。
- **agate_common.py `read_vision_tri_state`**（DEBT0005）：三处复用（check-gate 兜底 / check-p6-evidence / check-p6-provenance）解析口径一致；无视觉条目/文件缺失/解析失败→None（调用方按无声明默认 available 语义），`test_vision_none_1` 固化基线不红。
- **agate-frontmatter-check.py**：P1 可选键 `ui_render_shape:str`/`ui_ux_dimensions:list`、P2 可选字段 `ui_design_section:bool` 均进 `migrated_keys`+`types`，`required` 未动 → 既有 fixtures 不破坏。
- **agate-md-field-get.py**：新 op `ui_render_shape`（STRING_FIELDS+fallback）、`ui_ux_dimensions`（LIST_FIELDS）presence 语义正确。
- **check-protocol-consistency.py CHECK 11**：白名单锚点断言 10 文件 27 关键词，全部通过，无历史 WARNING→ERROR 误判（0 ERROR）。
- **测试健康**：新增测试使用 `task_dir`（pytest tmp_path，非 /tmp）、`pytest.importorskip("PIL")` 平台无关、非空 assert（returncode+output）、ahash 前置门禁 `_png_ok`（>1KB + 方差≥50）显式断言。均合规。

## DEBT

- **DEBT-0006**（`source: TAG0006-P4-review`，`type: refactor`）
  - 标题：check-p6-evidence.py 内联 ahash 计算 / agate-image-check ahash 改输出 (name, hash) 成对行，消除 `zip(sorted(glob), subprocess_output)` 对齐脆性。
  - 现状：CRITICAL-1 的修复路径即建立此重构；当前 `agate-image-check.py` 的 `sorted(glob)` + `contextlib.suppress` 输出与 check-p6-evidence 侧 `sorted(glob)` 的 zip 对齐是隐式耦合，任何一侧改排序/加 suppression 都会破坏。
  - 建议：将 ahash 计算收敛到单一拥有方（内联或成对输出），单元测试直接对"文件名↔哈希"配对断言。

## 阻塞项清单

| # | 级别 | 位置 | 摘要 | BDD |
|---|------|------|------|-----|
| 1 | CRITICAL | check-p6-evidence.py:340-343 | ahash 分组依赖 zip(ordered, ahash_lines)，非图片/损坏图导致错位 → 分组错误（误拦/漏放） | BDD-14 |

## 返回

- Status: **rejected**
- 阻塞问题数：1（CRITICAL-1）；另有 1 MEDIUM + 2 INFORMATIONAL 建议一并修复。

---

# 修复复审记录（2026-08-17）

> 复审轮：主 Agent 依据上轮 rejected 意见回派 implementer 落地 B1/B2/I1/I2 四项修复。本复审逐项核对修复后代码实证 + 跑新增回归测试，并复跑全量测试 / consistency / count-tests。

## 复审结论总览

**Status: approved（0 阻塞问题）**

上轮 1 CRITICAL + 1 MEDIUM + 2 INFORMATIONAL 全部彻底解决，且有**非空断言**的回归测试固化行为。全量 881 passed + 2 skipped；consistency 0 ERROR；count-tests 883（≥749 基线）。未发现新增缺陷。

## B1（MEDIUM-1）核对 — 已解决 ✔

**位置**：`agate/scripts/check-p6-provenance.py:299-350`

修复后 GAP 分支不再 `sys.exit(0)` 整脚本退出，改为 `is_gap` 开关（line 299）只控制审计 4 的 vision 强制子块：
- `is_gap` 分支（301-323）：只校验截图 PASS 是否附 `manual-review:` 引用 + 复核文件存在，随后**正常落入**审计 5（日志 EXIT_CODE 一致性，line 352）、协作规范 agent 字段（line 371）、审计 6（evidence JSON 一致性，line 398）。
- `else` 分支（324-350）：available/supplementable 的既有 vision YAML 强制保持不变。

**实证**：构造 GAP 任务 + 日志 `EXIT_CODE: 1`（与 PASS 声明矛盾）→ 修复后 `test_vision_gap_prov_3_gap_audit5_log_mismatch_exit_1`（test_check_p6_provenance.py:594-606）断言 `returncode==1` 且输出含 `EXIT_CODE`/`矛盾`——审计 5 对 GAP 任务生效，不再被静默跳过。运行 5 passed（含此用例）。基线 `test_vision_gap_prov_1/2` 仍绿（GAP 放行/缺失复核引用 exit 1 语义保持）。

## B2（CRITICAL-1）核对 — 已解决 ✔

**位置**：`agate/scripts/check-p6-evidence.py:343-346`

修复后 `ordered` 用统一过滤口径：
```python
ordered = [f for f in sorted(glob.glob(screenshots_dir + "/*")) if _is_image(f)]
```
只收集 `_is_image(f)==True` 的文件，与 `agate-image-check.py ahash`（agate-image-check.py:50-52，`contextlib.suppress` 只对 PIL 可解码图片输出行）对齐。>1KB 非图片文件（.log/.json）现被排除，不再触发 zip 错位。

**实证（独立构造复现）**：`screenshots/` 含 `00_notes.log`(3000B 文本) / `bad.png`(PNG magic+garbage, 2008B) / `a_log.png` / `z_shot.png`（同视觉不同字节，真重复对）。
- `agate-image-check.py ahash` 仅输出 2 行（bad.png 解码失败 + .log 被 suppress）。
- `_is_image` 过滤后 `ordered = ['a_log.png','z_shot.png']` 与 2 行 ahash **一一对应**，真重复对被正确归组（`groups: hash->[a_log.png, z_shot.png]`），`.log`/损坏图不再混入或顶掉真样本。

**回归测试**：`test_ahash_4_nonimage_file_misalign_temporal_exempt_exit_0`（test_check_p6_evidence.py:717-733）——>1KB .log 文件（3600B）名字排序落在两个同 BDD 时序样本之间，断言真时序对仍被豁免（exit 0）。运行 4 passed。ahash 全组 4 用例通过。

> 残余低危观察（非阻塞）：`_is_image` 用 `file -b --mime-type`（或 magic bytes），ahash 用 PIL 可解码性，理论上有"`file` 报 image/* 但 PIL 解码失败"的文件会导致单侧错位。已实证 `file` 对损坏 PNG（magic+garbage）报 `application/octet-stream`（两侧一致排除），此残余面远窄于原系统性缺陷，且无现成夹具触发，不构成登录门槛。可后续用 DEBT 追踪（见下）。

## I1（INFO-1）核对 — 已解决 ✔

**位置**：`agate/scripts/check-gate.py:354-378`

维度不适用豁免改为**按维度粒度**：
```python
layout_ok = "布局" in ui_block or bool(re.search(r"布局\s*不适用", ui_block))
interaction_ok = "交互" in ui_block or bool(re.search(r"交互\s*不适用", ui_block))
visual_ok = "视觉" in ui_block or bool(re.search(r"视觉\s*不适用", ui_block))
```
三个维度独立判定；仅声明"布局不适用"不再豁免交互/视觉。

**回归测试**：`test_ui_design_10_layout_waived_but_interaction_visual_required_exit_1`（仅布局豁免→ exit 1，line 2333）、`test_ui_design_11_all_three_dimensions_waived_exit_2`（三维全豁免→ exit 2）。均通过。

## I2（INFO-2）核对 — 已解决 ✔

**位置**：`agate/scripts/check-gate.py:328`（节标题正则）

`re.search(r"^#{2,3}\s+UI 设计", p2_text, re.MULTILINE)` 改为**前缀匹配**（去除原 `\s*$`），标题后附括号说明不再误拦。

**回归测试**：`test_ui_design_12_heading_prefix_with_suffix_exit_2`（标题 `## UI 设计（ui_affected: true 时必含本节）` → exit 2，line 2375）。通过。

## 全量验证

| 检查 | 结果 |
|------|------|
| 全量 pytest `agate/tests/` | **881 passed, 2 skipped** |
| `check-protocol-consistency.py` | 0 ERROR（279 既有 WARNING 非缺陷） |
| `count-tests.sh` | 883（≥749 基线，BDD-1） |
| 5 项修复回归测试（B1/B2/I1/I2）| 5 passed |
| check-gate UI（vision/shape/ui_design）| 23 passed |
| check-p6-evidence + provenance | 87 passed |

## DEBT（审批后跟踪）

- **DEBT-0006（维持）**（`source: TAG0006-P4-review`，`type: refactor`）
  - 标题：check-p6-evidence.py 内联 ahash 计算 / agate-image-check ahash 改输出 (name, hash) 成对行，消除 `zip(_is_image 过滤后有序列表, subprocess_output)` 对齐脆性。
  - 现状：B2 已用 `_is_image` 统一过滤口径大幅收窄对齐风险，但两侧过滤口径（`file`/PIL）理论上仍非同一函数实现，属隐式耦合；`file` 与 PIL 解码结果一致性的残余边界未完全消除。
  - 建议：将 ahash 计算收敛到单一拥有方（内联或输出 `文件名\t哈希` 成对行），单元测试直接对"文件名↔哈希"配对断言。

## 阻塞项清单（复审后）

| # | 级别 | 位置 | 摘要 | BDD | 复审判定 |
|---|------|------|------|-----|---------|
| 1 | CRITICAL | check-p6-evidence.py:343 | ahash 对齐错位 | BDD-14 | ✅ 已修复（_is_image 统一口径 + 回归测试） |
| 2 | MEDIUM | check-p6-provenance.py:301-323 | GAP 分支整脚本退出 | — | ✅ 已修复（is_gap 开关仅控 vision 子块） |
| 3 | INFO | check-gate.py:354-378 | 维度豁免一刀切 | §2.3 | ✅ 已修复（按维度粒度） |
| 4 | INFO | check-gate.py:328 | 节标题精确匹配 | §2.3 | ✅ 已修复（前缀匹配） |

## 返回

- Status: **approved**
- 阻塞问题数：0
- 摘要：B1/B2/I1/I2 全部彻底解决，回归测试非空断言固化；全量 881 passed + 2 skipped，consistency 0 ERROR。
