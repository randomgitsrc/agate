---
phase: P4
task_id: TAG0006-ui-ux-quality
type: review
parent: P4-implementation.md
trace_id: TAG0006-P4-20260817
status: approved
created: 2026-08-17
agent: design-review
---

# P4 设计评审 — UI/UX 验收质量机制（设计·前端 维度）

> 评审范围：P4 implementer 对 P2 方案（§2.1-§2.16, SCOPE+ 2026-08-17 范围扩展）的机制条文落地。
> 本任务自身 `ui_affected: false`（协议机制增强，无真实 UI 产物），故评审聚焦**机制设计/条文质量**
> （是否完整、可执行、可判定、不写死工具），不做真实 UI 视觉评审。
> 评审对象为 **worktree 版本**（`/home/kity/oclab/agate/.worktrees/agate-TAG0006/agate/`），非主 checkout。

## 结论

**status: needs-revision**——机制条文与文档一致落地、验证通过（§1-§3），但评审中发现 **2 条新增 gate 脚本的正确性缺陷**（§4，1 条为 gate 完整性 BLOCKER 级，1 条为 MEDIUM），需回派 implementer 修复后复审。不推翻整体设计，属局部实现缺陷。

## 1. 逐项核对（对照 P2-design 检查点，锚点 = 文件 + 节 + BDD 编号）

### 1.1 UI 设计节机制（BDD-4/5）——完成 ✓
- **architect.md**：「UI 设计节」结构规格齐备（`## UI 设计` + 渲染形态声明 + 布局/交互/视觉 + 渲染正确性/动效时序 checklist，判据可量化：渲染结果对比/diff 阈值、帧/时间戳对齐、动效起止状态），由 architect 兼任产出、不新增 designer 角色（architect.md:62-112；role-system.md:35）。
- **P2 卡片**（P2-design.md card:71-82）+ **task-files.md**（:245, 310-320）同步 UI 设计节样例。
- **gate_p2 校验**（check-gate.py:314-394 `_gate_p2_ui_design_section`）：节标题 + 渲染形态声明 + 按形态分支 checklist（布局型=布局/交互/视觉三锚点；渲染组件/时序型=渲染正确性或动效时序锚点）+ P1-P2 形态一致性（`_canonical_shape` :210-226 规范化值比对，含中文标签同义映射 §2.15.1）。
- **单测**：test_check_gate.py 20 用例覆盖（test_ui_design_1..9 / test_shape_1..5 / test_vision_1..4），含规范值正例、中文标签同义映射正例。

### 1.2 plan-design-review 维度扩容（BDD-6）——完成 ✓
- **plan-design-review.md**：维度表扩容为视觉设计（:19）/交互设计细节（:20）/渲染正确性与时序（:21），各配 0-10 评分项；**七维边界注**（:23）明确「交互状态覆盖率=状态存在性」vs「交互设计细节=状态内实现质量」，防 double count。
- **role-system.md:47** plan-design-review 行职责同步（渲染形态适配）。
- 渲染正确性与时序维度按形态启用（渲染组件/时序特效类形态；常规布局不启用），避免打分噪音（§2.5）。

### 1.3 verifier.md / P6 卡片双证据分档 + 视觉质量 checklist + 输入态复核（BDD-9/10/13）——完成 ✓
- **verifier.md**：UI 追加约束改写为三态分档双证据（:107-134：available/supplementable→vision YAML + blocker_count=0；GAP→截图/帧序列 + manual-review 人工复核记录，不要求 vision YAML；无声明默认 available 兼容回归锚点）；证据形式按形态选（帧序列/时序截图/渲染输出对比，:121-134）；输入态/交互形态变化类人工复核判定标准（:136-146，含动作/特效/时序交互词）；视觉质量 checklist 核对（:148-153，量化锚点 + 禁主观词）；P6 处理流程补读形态+三态步骤（:224-228）。
- **P6 卡片**：三态分档 + 证据按形态（:52-62）+ 雷同降级待复核（:66-67）+ 真实视觉分析 BDD-10（:148-153，禁 naturalWidth/像素方差糊弄）。
- **check-p6-evidence.py**：GAP 降级链要求截图 PASS 附存在的人工复核记录文件（:232-258）；证据形式按形态匹配（渲染组件/时序型须含 frames/ 或 renders/ 或 -tN 时序截图，:210-226）；帧序列/渲染输出对比完整性（diff.json 含量化度量，:366-408）。
- **check-p6-provenance.py**：R1b 审计 4 GAP 放宽（vision=GAP → 改验 manual-review 引用+文件存在，exit 0 放行；available/无声明保留既有强制 + blocker_count=0，:282-322）。
- **单测**：test_check_p6_evidence.py 15 用例 + test_check_p6_provenance.py（GAP 分支）。

### 1.4 dispatch-prompt 能力自查（BDD-12）+ supplementable 注入（BDD-11）——完成 ✓
- **dispatch-prompt.md**：新增**能力自查强制段**（:74-78）；能力补充说明节补视觉 supplementable 获取指引注入（:67-72）。
- **dispatch-protocol.md** A3 视觉语境扩展（:1196-1200）：vision supplementable + ui_affected:true → P6 派发注入视觉获取指引 + 能力自查要求。
- 单测：test_dispatch_orchestration.py 覆盖。

### 1.5 vision-analyst 能力自查 + 不写死工具（BDD-10/12/17）——完成 ✓
- **vision-analyst.md**：能力自查强制（:244-251，能→按所选证据形式分析；不能→[CAPABILITY_GAP] 降级，不静默假设/不编造观察）；分析对象按渲染形态适配（:253-257 常规布局=截图，渲染组件=帧序列/渲染输出对比，时序特效=时序截图）；"不写死视觉工具，仅作机制描述"。

### 1.6 不写死视觉工具/技术栈（约束 4）——满足 ✓
- WebGL/Canvas/OpenGL 仅以"仅举例/不构成技术栈要求"语境出现（analyst.md:216,221；architect.md:73；vision-analyst.md:253），无任何强制绑定；gate 启发关键词（check-gate.py:205-207）明确标注"启发非绑定注"，形态判定以 P1 规范值为准。一致性检查 CHECK 11 覆盖锚点（check-protocol-consistency.py:825-847）。

### 1.7 跨文档一致（check-protocol-consistency CHECK 11, I14）——完成 ✓
- **CHECK 11**（check-protocol-consistency.py:819-867）：白名单式断言 10 文件 UI/UX 机制条文锚点存在性（分类框架/渲染形态/三态/证据按形态等），防文档-脚本-单测三件套漂移。**验证通过：`✅ PASS CHECK 11`**。

## 2. 验证结果（客观查证，非自报）

- 目标单测 7 模块：**283 passed**（test_check_gate / test_check_p6_evidence / test_check_p6_provenance / test_review_role_docs / test_agate_md_field_get / test_check_frontmatter / test_dispatch_orchestration）。
- `check-protocol-consistency.py`（worktree 自身版）：**0 ERROR**（含 CHECK 11 PASS；279 既有 WARNING 非缺陷）。
- `count-tests.sh`：**878**（≥749 单调不减，与 P4-implementation 声明一致）。
- P4-implementation 声称的 28 文件改动，git status 核实其覆盖范围（7 gate 脚本 + 文档 + 测试），新机制 tests（test_check_gate 20 / test_check_p6_evidence 15）均实际存在。

## 3. P4-implementation 声明核验（§2 改动清单）

- analyst.md（前端视觉三态硬要求/渲染形态/UX 分类框架/反模式清单扩展）✓
- architect.md（UI 设计节结构规格）✓
- verifier.md（三态分档/证据按形态/输入态复核/视觉质量清单）✓
- vision-analyst.md（能力自查/形态适配/不写死工具）✓
- plan-design-review.md（七维）✓
- requirements-review.md（UI/UX 评审要点）✓
- dispatch-prompt.md（能力自查/supplementable 注入）✓
- task-files.md（P2 UI 设计节样例/P6 三态分档样例）✓
- P1/P2/P6 卡片、dispatch-protocol.md、role-system.md、LIMITATIONS.md、state-machine.md、rules/state-transitions.md、WORKFLOW.md、scripts/README.md ✓
- agate_common.py `read_vision_tri_state`（统一三态解析）、agate-frontmatter-check.py、agate-md-field-get.py、check-gate.py、check-p6-evidence.py、check-p6-provenance.py、check-protocol-consistency.py ✓
- 测试格式修复：`test_check_p6_evidence.py` read_text 跨行→单行，**确认仅为格式调整**（git diff 核实：保留 `encoding="utf-8"`，断言与测试逻辑不变），符合"3 测试格式修复"声明。

## 4. BLOCKER / MEDIUM 缺陷（需修复，本次审出）

### 4.1 [BLOCKER] check-p6-provenance GAP 分支 `sys.exit(0)` 短路后续审计（审计 5/6）
- **位置**：`agate/scripts/check-p6-provenance.py:322`（GAP 分支末尾 `sys.exit(0)`）。
- **问题**：P1 vision=GAP 时，R1b 审计 4 的 GAP 分支在校验 manual-review 引用后直接 `sys.exit(0)`，
  使 `check-p6-provenance.py` **在审计 4 之后立即返回 0，跳过全部后续审计**——
  审计 5（日志 EXIT_CODE 与 PASS/FAIL 一致性，:351-368）、协作规范 agent 字段（:376-395）、
  审计 6（evidence JSON 与 P6 声明一致性，:397-409）。
- **与设计偏差**：P2 §2.8/§2.9 只要求"R1b 审计在 GAP 分支放宽 vision YAML 强制，改验人工复核记录"，
  即只放宽**审计 4 内的 vision 检查**，并未要求跳过审计 5/6。available 分支（无声明/available/supplementable）
  会继续跑完审计 5+6（:351-409），而 GAP 任务被短路——**同一 gate 对 GAP 任务比 available 任务更弱**，
  可能放行"声明 PASS 但日志 exit≠0"、"evidence JSON 与 P6 声明矛盾"的验收结果。
- **修复建议**（回派 implementer）：GAP 分支不要整体 `sys.exit(0)`，改为仅跳过"vision YAML 强制 + 
  blocker_count"这一子检查（使 GAP 走 R1b 的"人工复核记录"分支后**继续**执行审计 5/6 与协作规范检查）。
  逻辑应镜像 available 分支的结构（available 分支在 :349 校验完直接落入后续审计，无提前 exit）。

### 4.2 [MEDIUM] check-p6-evidence avg-hash 文件名/哈希 zip 对齐错位（非图片文件被静默跳过）
- **位置**：`agate/scripts/check-p6-evidence.py:338-343` 与 `agate/scripts/agate-image-check.py:50-52`。
- **问题**：`agate-image-check.py ahash` 遍历 `SCREENSHOTS_DIR/*` **全部文件**（含非图片），对每个文件执行
  `_ahash(f)`；非图片文件 `Image.open` 抛异常被 `contextlib.suppress` 捕获，**不打印任何行**（:50-52）。
  而 `check-p6-evidence.py` 用 `ordered = sorted(glob(screenshots_dir/"*"))`（**含**非图片文件）与
  `ahash_lines`（**只含**打印出的图片哈希行）做 `zip` 按位置配对。screenshots/ 中一旦混入非图片文件
  （.json/.log 等，verifier 可能随手放入），`ahash_lines` 行数 < `ordered` 文件数 →
  zip 位置错位/尾部文件被丢弃，导致 **avg-hash 雷同分组归错文件或漏掉文件**，
  雷同降级判定（BDD-14）与同 BDD 时序豁免（BDD-16）结果失真。
- **影响**：avg-hash 是 P6 非文本证据实质检查（R1a objective evidence barrier）的一环，
  错位会静默破坏充数/雷同防伪。测试用例（test_ahash_*/test_frame_seq_*）均用纯 PNG 目录，
  未覆盖含非图片文件的歧义场景。
- **修复建议**：`agate-image-check.py` 对非图片文件也应输出占位/hash（或跳过但仍输出一行），
  或 `check-p6-evidence.py` 只对图片文件（`_is_image`）做 `ordered` 收集并对齐；两者须用**同一过滤口径**
  保证行数一一对应。补一条含非图片文件的中等复现单测。

## 5. SUGGEST 级观察（非阻塞，主 Agent 可采纳可不采纳）

1. **P2 布局 checklist 豁免过宽**（check-gate.py:354）：单个"不适用"字符串豁免全部布局/交互/视觉三锚点（`unknown_waived = "不适用" in ui_block`）。与 P2 §2.3 设计明示"维度不适用显式声明即可豁免该维度 checklist 关键词"一致，且渲染组件分支 + P1 gate 仍保留结构约束——属设计内松紧，非缺陷。
2. **ahash 时序组豁免为整组而非"相邻样本"**（check-p6-evidence.py:347-349）：同 BDD 前缀 + 全时序样本时整组豁免，比 §2.16 "相邻样本豁免"措辞略宽，但对同动画/时序证据更正确，跨 BDD 组雷同仍严格拦截——不阻塞。

## 6. 环境标记

[PROD_NOT_TOUCHED]——本任务为协议文档 + gate 脚本增强，评审全程只读（读文件 + 跑只读验证命令：pytest/consistency/count-tests），未触碰任何生产环境/数据库/外部服务。

## 门槛自检

- 产出文件存在 + Header 完整（phase/task_id/type/parent/trace_id/status/created/agent）✓
- status 已改为 **needs-revision** ✓
- 结论引用具体文件 + 节 + BDD 编号 ✓
- agent = design-review ≠ main ✓

---

## 修复复审记录（2026-08-17）

> 上轮判定 needs-revision（§4.1 BLOCKER check-p6-provenance GAP 短路审计 5/6 + §4.2 MEDIUM avg-hash zip 错位）。
> implementer 已修复 B1/B2 并补充回归测试。本节约本轮对修复的核对结论。

### R1. B1（4.1）check-p6-provenance GAP 分支不再整脚本 `sys.exit(0)` —— **已修复 ✓**

- **代码实证**（`agate/scripts/check-p6-provenance.py:301-323`）：`is_gap = vision_state == "GAP"` 分支内仅做
  ①截图 PASS 须附 `manual-review` 引用校验（:304-311）②`manual-review` 引用文件存在性校验（:313-317），
  校验通过后只打印放行说明（:323），**删除原 `sys.exit(0)`**，随后自然落入审计 5（:352 日志 EXIT_CODE 一致性）、
  协作规范 agent 字段（:371-396）与审计 6（:398 evidence JSON 一致性）。逻辑已镜像 available 分支结构
  （available 分支 :324-350 校验完同样无提前 exit，直接落入 :352）。
- **回归测试**（`agate/tests/unit/test_check_p6_provenance.py:594-606`）
  `test_vision_gap_prov_3_gap_audit5_log_mismatch_exit_1`：构造"manual-review 齐全但日志 EXIT_CODE=1"的合规 GAP 任务，
  断言 gate 返回 **exit 1**——证明审计 5 硬检查对 GAP 任务生效、不再被 vision 降级静默跳过。修复前此测试会误给 exit 0。
- **结论**：§4.1 BLOCKER 已彻底解决。GAP 任务与 available 任务接受同等强度的非 vision 硬检查（审计 5/6 + 协作规范）。

### R2. B2（4.2）check-p6-evidence avg-hash 统一 `_is_image` 过滤口径 —— **已修复 ✓**

- **代码实证**（`agate/scripts/check-p6-evidence.py:343`）：`ordered = [f for f in sorted(glob.glob(screenshots_dir + "/*")) if _is_image(f)]`——
  ordered 现仅收集图片文件，与 `agate-image-check.py ahash`（:50-52 仅对被成功解码的图片逐行打印哈希，非图片被 suppress 不打印行）的
  输出逐行一一对应，`zip(ordered, ahash_lines)`（:345）不再因混入非图片文件而错位。
  `_is_image`（:71-93）用 MIME/magic bytes 判定 image 类型，与 PIL 可解码口径一致。
- **回归测试**（`agate/tests/unit/test_check_p6_evidence.py:712-733`）
  `test_ahash_4_nonimage_file_misalign_temporal_exempt_exit_0`：在 `bdd7-t1.png` 与 `bdd7-t2.png` 之间混入
  **>1KB 的 .log 非图片文件**（`bdd7-t1a.log`，排序落在两时序样本间），断言修复后真时序重复对被正确豁免（**exit 0** 且
  不误报 "average hash 相同"）。修复前 zip 错位会误判跨组雷同 → exit 1（误拦合法时序任务）。
- **结论**：§4.2 MEDIUM 已彻底解决，且补了含非图片文件的回归测试，防止复发。

### R3. 全量验证复查（非自报，客观跑证）

- 全量 pytest（worktree 自身）：**881 passed + 2 skipped**（PIL skip），较上轮 876 增至 881——新增 4 个 B1/B2 回归用例。
- `check-protocol-consistency.py`（worktree 自身版）：**0 ERROR**，其中 **`✅ PASS CHECK 11`（UI/UX 机制条文跨文档一致）**；
  279 个 WARNING 均为既有叙事文件引述旧路径等历史项，非本轮缺陷。
- `count-tests.sh` 单调不减，与 881 passed 对应。

### R4. 已 approved 机制条文未被意外改动 ✓

- spot-check 5 个核心机制文档仍含上轮核准的条文锚点：
  `verifier.md` 三态（available/supplementable/GAP 共 6 处引用）、`architect.md` UI 设计节、`plan-design-review.md` 渲染正确性/时序维度、
  `vision-analyst.md` CAPABILITY_GAP/能力自查、`dispatch-prompt.md` supplementable/能力自查。
- CHECK 11 对 10 文件 UI/UX 机制条文做白名单断言通过，确认无漂移/回退。

### R5. 复审判定

**status: approved**——上轮 2 条缺陷（1 BLOCKER + 1 MEDIUM）均已彻底修复，修复方式与修复建议一致，
回归测试针对性覆盖，全量测试 881 passed + 2 skipped、0 consistency ERROR、CHECK 11 PASS，
已核准的机制条文部分未被意外改动。整体设计（三态双门禁方案 A + 15 BDD + 形态适配层）批准放行。

**门槛自检（复审）**
- 保留上轮全部内容（§1-§6 未抹掉）+ 追加本复审节 ✓
- status 已由 needs-revision 改为 **approved** ✓
- 结论引用具体文件 + 节 + BDD 编号 ✓
- agent = design-review ≠ main ✓
