---
phase: P4
task_id: TAG0006-ui-ux-quality
type: implementation
parent: P3-test-cases.md
trace_id: TAG0006-P4-20260817
status: draft
created: 2026-08-17
agent: implementer
---

# P4 实现记录 — agate UI/UX 验收质量机制

implementation_dir: agate/

本任务无 UI 产物（自身 `ui_affected: false`），implementation_dir = `agate/`（协议本体目录）：
gate 脚本在 `agate/scripts/`，协议文档在 `agate/` 各 `.md`。

## 改动清单

### 1. Gate 脚本（agate/scripts/）

| 文件 | 改动 |
|------|------|
| `agate_common.py` | 新增 `read_vision_tri_state(p1_file)`：统一解析 P1-requirements.md `capability_requirements` 围栏块内视觉条目（need/name 含 visual\|vision）的 status 三态；无视觉条目/文件缺失/解析失败 → None（调用方按"无声明默认 available"处理，DEBT0005 复用） |
| `agate-md-field-get.py` | `STRING_FIELDS` 增 `ui_render_shape`、`LIST_FIELDS` 增 `ui_ux_dimensions`（P1 frontmatter 可选字段读取，presence 语义；正文 `_regex_fallback` 增 ui_render_shape 标量回退） |
| `agate-frontmatter-check.py` | P1 schema `migrated_keys`/`types` 增可选键 `ui_render_shape: str` / `ui_ux_dimensions: list`（required 不变，不破坏既有 fixture）；P2 schema `migrated_keys`/`types` 增可选字段 `ui_design_section: bool` |
| `check-gate.py` | gate_p1 新增 `_gate_p1_vision_capability`（domains 含 frontend → 必须声明视觉三态条目，缺失/非法 status → exit 1）+ `_gate_p1_ui_shape`（形态/维度声明合法性：shape 但维度空 / 维度非框架且未声明运用 → exit 1；双字段缺失 → 通过）；gate_p2 新增 `_gate_p2_ui_design_section`（ui_affected:true → UI 设计节标题 + 渲染形态声明 + 按形态 checklist + P1-P2 形态一致性规范化值比对，`_canonical_shape` 同义映射 layout/渲染组件型/时序特效型） |
| `check-p6-evidence.py` | ①P1 vision=GAP 降级链：截图 PASS 须引 `(manual-review: <file>)` 且文件存在，缺 → exit 1；②证据形式按形态：shape=render_component/temporal_effects 须含 `frames/`/`renders/`/`-tN` 时序截图，缺 → exit 1；③avg-hash 雷同从 WARNING 升级为**降级待复核**：按 bdd-id 前缀分组（帧序列 `-NN` 与 `-tN` 时序截图同组、组内相邻样本豁免），跨组雷同须含 `雷同截图复核`/`manual-review` 记录才放行，无 → exit 1；④`renders/` 引用须引 actual + diff.json（含量化度量），缺 diff → exit 1；⑤帧序列帧号缺口 → WARNING |
| `check-p6-provenance.py` | R1b 审计 4 增 GAP 放宽：P1 vision=GAP → 截图 PASS 不再强制 vision YAML，改验 `(manual-review: <file>)` 引用 + 文件存在，通过即 exit 0（放行）；available/无声明（默认 available）保留既有 R1b 强制 + blocker_count=0 |
| `check-protocol-consistency.py` | 新增 CHECK 11 `check_uiux_doc_anchors`：按 (文件→关键词) 白名单断言 analyst/architect/verifier/plan-design-review/requirements-review/role-system/dispatch-prompt/dispatch-protocol/P1/P2/P6 卡片含 UI/UX 机制条文锚点（分类框架/渲染形态/三态分档/证据按形态），防文档-脚本-单测三件套漂移 |

### 2. 协议文档（agate/ 下 .md，按 P2 §6 影响面清单）

| 文件 | 改动 |
|------|------|
| `analyst.md` | frontend 任务视觉三态声明硬要求 + 渲染形态 frontmatter 字段；UX 分类框架 + 形态/维度声明步骤 + 可量化判据挡（BDD 反模式自检清单扩展）；技术栈中立注 |
| `architect.md` | `ui_design_section` 字段说明 + **UI 设计节结构规格**（渲染形态声明 + 布局/交互/视觉 + 渲染正确性/动效时序 checklist，判据可量化；architect 兼任，不新增 designer）|
| `verifier.md` | UI 追加约束改写为三态分档双证据 + 证据形式按形态（帧序列/时序截图/渲染输出对比）+ 输入态/交互形态变化类人工复核判定标准 + 视觉质量 checklist + 真实视觉分析条文 + 证据输出节输出形式清单 |
| `vision-analyst.md` | 能力自查强制 + 分析对象按渲染形态适配（帧序列逐帧/渲染输出对比/时序截图）+ 不写死工具 |
| `requirements-review.md` | frontend 任务 UX BDD / 形态声明 / vision 能力声明评审要点 + 主观词打回 |
| `plan-design-review.md` | 维度表五维→七维（视觉设计/交互设计细节/渲染正确性与时序）+ 0-10 评分项 + 七维边界注 |
| `role-system.md` | 不新增 designer 注明 + plan-design-review 行职责同步 + architect 兼任注 |
| `phase-cards/P1-requirements.md` | frontmatter 样例补 ui_render_shape/ui_ux_dimensions 可选键 + UX 分类框架条文 + common-error 漏 vision 声明 exit 1 |
| `phase-cards/P2-design.md` | UI 设计节必含条文（形态声明 + 按形态 checklist + P1-P2 一致性 gate）|
| `phase-cards/P6-acceptance.md` | 三态分档双证据 + 证据形式按形态 + 输入态复核 + 真实视觉分析（BDD-10）+ GAP 降级改人工复核 |
| `dispatch-protocol.md` | A3 视觉语境扩展（supplementable 注入 + 能力自查）+ P6 证据段三态/雷同降级/证据形式条文 |
| `dispatch-prompt.md` | 能力补充说明节视觉注入 + 新增**能力自查**强制段 |
| `task-files.md` | P2 frontmatter 补 ui_design_section + P2 模板补 UI 设计节样例 + P6 模板补三态分档/人工复核/雷同复核样例 |
| `state-machine.md` | P2 转移补 vision 三态声明/ui_affected UI 设计节 + P6 转移补双证据三态分档 + 证据形式按形态 |
| `rules/state-transitions.md` | P1→P2 frontend vision+形态、P2→P3 UI 设计节、P6→P7 三态分档 |
| `WORKFLOW.md` | P2 评审映射补 plan-design-review 视觉/交互维度 + UI 设计节门槛；P6 行补双证据三态分档 + 雷同降级 + 形态证据 |
| `LIMITATIONS.md` | 局限 7 缓解更新（三态分档 + 降级链 + 帧/输出对比证据 + 雷同降级待复核 + 残余边界）|
| `scripts/README.md` | check-p6-evidence / check-p6-provenance / check-gate / agate_common 说明更新 |

### 3. 测试代码（P3 落点调整）

`agate/tests/unit/test_check_p6_evidence.py`：`read_text(encoding=...)` 从跨行改为单行——修复 `test_agate_scripts_encoding.py` 的 text-I/O-explicit-encoding 守卫（断言语义与测试本身未变，仅格式对齐既有守卫）。其余 53 个 P3 用例未改。

## 兼容策略确认（P2 §10）

- 新检查只对**新声明**生效：domains=frontend / ui_affected=true / P1 声明 ui_render_shape → 既有 825 基线 fixtures 均不命中（既有 fixture P1 无 frontend domains 且无形态字段；既有 P2-design 无 ui_affected:true 用于 P2 gate 测试）→ 基线全绿
- P6 无视觉能力声明 → 默认 **available 语义**（既有 R1b + blocker_count 强制保留，不落入 GAP 放行），test_vision_none_1 回归守卫固化
- avg-hash 雷同从 WARNING 升级为降级待复核（md5 硬阻断不变）；帧序列/`-tN` 时序截图按同 BDD 组（bdd-id 前缀）豁免相邻样本
- count-tests 计数 878 ≥ 749 单调不减；consistency 0 ERROR

## test_result

- P3 53 新增用例：**全部转绿**（test_check_gate 20 / test_check_p6_evidence 15 / test_check_p6_provenance 4 / test_review_role_docs 14；含 1 个 P3 格式规整修复）
- 全量 pytest：`878 collected → 876 passed, 2 skipped`（2 skip = Pillow-independent 平台分支，既有行为；无失败无回归）
- `check-protocol-consistency.py`：0 ERROR（279 既有 WARNING 非缺陷）
- `count-tests.sh`：**878** 个测试用例（≥749 单调不减）
- ruff check（改动的 7 个脚本）：All checks passed

## 自查≠gate

本文件为 P4 自查记录。P5 由主 Agent 派发 verifier 执行 gate_commands.P5 全量 pytest，主 Agent 验 gate。不声称"P5 已过"。

## DESIGN_GAP / SCOPE+ 记录

[DESIGN_GAP: 无]——P2 方案（§2.1-2.16）各检查点均已按计划落地，未发现需自主决策的歧义。

[SCOPE_GAP: 无]——prompt 覆盖 P2 §6 全部影响面清单。


SCOPE+ 扫描：无（2026-08-17 用户范围扩展已在 P1/P2 作为 [BASELINE_CHANGE] 处理为 BDD-16/17，非 implementer 在本阶段新发现的需求）。

注：实现中修正了 P3 测试代码的 1 处文本 I/O 格式（`test_check_p6_evidence.py` 的 read_text 跨行写法触发既有 encoding 守卫回归），属测试格式调整非测试语义改动，已在"测试代码"节标注。

## 修复轮记录（2026-08-18，TAG0006 双评审缺陷修复）

> 修复 P4-review-backend.md（CRITICAL-1/MEDIUM-1/INFO-1/2）+ P4-review-design.md（4.1 BLOCKER/4.2 MEDIUM）。
> 本轮仅做增量修复，不重写既有实现；双评审其余全通过项不动。

### B1 / M1（check-p6-provenance.py GAP 分支短路）
- **缺陷**：:322 GAP 分支 `sys.exit(0)` 在审计 4 后整脚本退出，静默跳过审计 5（日志 EXIT_CODE 一致性）、审计 6（evidence JSON 一致性）与协作规范 agent 字段检查——这些是 exit 1 硬检查（审计 5/6）与 WARNING 收集，被 GAP 无条件跳过。
- **修复**：删掉 `sys.exit(0)`；GAP 分支只跳过「vision YAML 强制 + blocker_count」子块（`is_gap` 分支本体），随后正常落入审计 5/审计 6/agent 字段检查，镜像 available 分支结构（available 分支本就不提前 exit）。
- **测试**：`test_vision_gap_prov_1` 夹具补 `agent` 字段（P2/P6）使"完全合规 GAP 任务"仍以 exit 0 通过（断言语义不变）；新增 `test_vision_gap_prov_3`（GAP 任务日志 EXIT_CODE 矛盾 → 审计 5 生效 exit 1），证明非 vision 硬检查不再被跳过。

### B2（check-p6-evidence.py avg-hash zip 错位）+ DEBT0006
- **缺陷**：`agate-image-check.py ahash` 只对"图片文件"逐行输出 hash（非图片/解码失败 `contextlib.suppress` 吞掉不打印行），而 check-p6-evidence 用 `sorted(glob(dir/*))`（含全部文件）与之 `zip` 按位配对——screenshots/ 混入 >1KB 非图片文件（.log/.json）时行数 < 文件数 → 哈希错位/尾部文件被丢弃，雷同分组失真（误拦/漏放）。
- **修复**：统一过滤口径——`ordered` 只收集图片文件（`_is_image` 过滤），与 ahash 子进程输出一一对应，消除 zip 错位。不新增依赖。
- **测试**：新增 `test_ahash_4_nonimage_file_misalign_temporal_exempt_exit_0`（判别式回归，含 >1KB 非图片 .log）：`.log` 文件名排序落在两个同 BDD 时序样本之间时，修复前把真会被误判为跨组雷同误拦（exit 1），修复后真时序重复对被正确豁免（exit 0）——红/绿判别均验证。

### I1（check-gate.py 维度不适用豁免按粒度）
- **缺陷**：`unknown_waived = "不适用" in ui_block` 任一维度声明不适用即一刀切豁免 布局/交互/视觉 三维，偏宽松（只写"布局不适用"也能跳过另两维必填校验）。
- **修复**：改为按维度粒度豁免——`布局\s*不适用` 只豁免布局锚点，`交互\s*不适用`/`视觉\s*不适用` 各自豁免，与 P2 §2.3"维度不适用显式声明即可豁免该维度"一致。
- **测试**：`test_ui_design_10`（仅"布局不适用"、缺 交互/视觉 → 修复后 exit 1，修复前 exit 2 判别）+ `test_ui_design_11`（三维全豁免 → exit 2）。

### I2（check-gate.py UI 设计 节标题前缀匹配）
- **缺陷**：节标题正则 `^#{2,3}\s+UI 设计\s*$` 要求精确结尾，标题后附括号说明（如"（ui_affected: true 时必含）"）会被误拦。
- **修复**：放宽为前缀匹配 `^#{2,3}\s+UI 设计`（两处：存在性判定 + 节区块起点），防漂移误拦。
- **测试**：`test_ui_design_12_heading_prefix_with_suffix_exit_2`（标题带后缀 → 修复后 exit 2，修复前 exit 1 判别）。

### 修复轮验证
- 全量 pytest：`881 collected → 881 passed, 2 skipped`（876 基线 + 5 新用例，无回归）
- `check-protocol-consistency.py`：0 ERROR（279 既有 WARNING 非缺陷）
- `count-tests.sh`：**883**（878 + 5 新用例，≥749 单调不减）
- ruff check（改动的 check-p6-provenance.py / check-p6-evidence.py / check-gate.py）：All checks passed（见 P4-progress.md 自查）
