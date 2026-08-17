---
phase: P8
task_id: TAG0006-ui-ux-quality
type: release
parent: P7-consistency.md
trace_id: TAG0006-P8-20260817
status: draft
created: 2026-08-17
agent: implementer
---

# P8 发布准备 — agate UI/UX 验收质量机制（TAG0006-ui-ux-quality）

> 本文件为 releaser（implementer P8 模式）产出的发布准备记录。**不执行 git commit / git tag / bump-version**——这些由主 Agent 在 gate 验证通过后亲自执行。

## 1. 版本与 bump_type

- **当前版本**：v0.50.0（最新 tag `v0.50.0`，`git describe --tags --abbrev=0` 实测）
- **建议新版本**：**v0.51.0**
- **bump_type: minor**

### bump_type 判定理由

按 AGENTS.md「版本发布」清单 + dispatch-prompt P8 节口径（公共 API 行为变化/破坏性变更 → major；加功能/向后兼容 → minor；修 bug → patch）：

1. **主导变更 = 机制增强（新增能力，向后兼容）**：TAG0006 为 UI/UX 验收质量机制新增
   - P1 vision 能力三态硬校验（`_gate_p1_vision_capability`，仅 `domains` 含 `frontend` 触发）
   - P2 UI 设计节检查（`_gate_p2_ui_design_section`，仅 `ui_affected: true` 触发）+ P1-P2 形态一致性规范化值比对
   - P6 证据形式按形态适配（`frames/`/`renders/`/`-tN` 时序截图识别）+ GAP 降级链人工复核
   - P7 一致性 CHECK 11（`check_uiux_doc_anchors`）+ 角色/卡片/派发文档联动
   - 全部新增检查**仅对新声明生效**（presence 语义）——既有 task 无 frontend domains / ui_affected: true / 新形态字段时走默认路径，825→881 基线全绿（BDD-15 回归实证 `881 passed, 2 skipped`），向后兼容成立。

2. **avg-hash 行为变化评估（本任务唯一候选破坏性变更）**：`check-p6-evidence.py` avg-hash 雷同从非阻断 WARNING（exit 2）升级为「降级待复核」（无复核记录 → exit 1 阻断）。这是**既有 P6 证据路径上的真实行为变化**。
   - **不判 major 的理由**：属于新增机制配套的判定收紧，且对既有任务**实际不破坏**——基线 fixture 无"无复核记录的视觉雷同截图"场景（881 passed 实证无基线用例新变红）；边界窄（仅视觉高度相似截图且无复核记录才拦截）。
   - **需在 UPGRADING 记录**：该行为变化仍是"api 行为变化"，须在 UPGRADING 新增破坏性变更条目明示（见 §5），**不得静默发布**。P2 §6.4 已明确要求 UPGRADING 新增"P1 frontend vision 三态 + P2 ui_affected UI 设计节 + P6 avg-hash 降级"条目，并附"渲染形态可选声明（缺失走布局型默认，不破坏性）"说明。
   - 结论：avg-hash 行为变化 + 新声明门槛均为**向后兼容的机制增强**，净判定 **minor**。

3. **非 UI 任务 / 既有项目升级（UPGRADING 已声明）**：新检查是"零动作则无感"门槛式——不新声明 frontend/ui 形态的任务不触发新增硬校验；avg-hash 触发的既有任务需在复核后放行（可操作出口，不 dead-lock）。

## 2. 需要 bump 的包（P2 packages 声明逐包处理）

P2-design.md frontmatter `packages: [agate-docs, agate-scripts-py, agate-tests]`（同仓库 agate 协议本体，**单仓库单版本**，三包共享同一版本号 v0.51.0，非独立多包分发）：

| 包 | 旧版本 | 新版本 | 主要变更 |
|----|--------|--------|---------|
| agate-docs | v0.50.0 | v0.51.0 | 14 个协议文档联动：analyst/architect/verifier/vision-analyst/requirements-review/plan-design-review/role-system/dispatch-protocol/dispatch-prompt/task-files/state-machine/P1-P2-P6 卡片/WORKFLOW/LIMITATIONS/scripts-README —— P1-P6 三态/形态/降级链条文 |
| agate-scripts-py | v0.50.0 | v0.51.0 | agate_common（`read_vision_tri_state`）、check-gate（gate_p1 vision+ui_shape、gate_p2 ui_design_section）、check-p6-evidence（三态/证据按形态/avg-hash 降级）、check-p6-provenance（R1b GAP 放宽）、check-protocol-consistency（CHECK 11）、agate-frontmatter-check、agate-md-field-get |
| agate-tests | v0.50.0 | v0.51.0 | test_check_gate / test_check_p6_evidence / test_check_p6_provenance / test_review_role_docs 共 53 新用例（P3）；全量 883 用例（≥749 单调不减） |

> 注意：3 个 hook 薄壳（.sh）与 install-hook 不受本任务影响（本任务未改 hook）。

## 3. 版本引用文件清单（本任务特有，通用 P8 卡不覆盖）

按 AGENTS.md「版本引用文件清单（agate 仓库自身特有）」逐项核对需更新文件：

| 文件 | 当前 | P8 动作 | 破坏性变更章节 |
|------|------|---------|----------------|
| `README.md` badge（`version-v0.50.0`）| v0.50.0 | bump → v0.51.0 | — |
| `README.zh-CN.md` badge（镜像）| v0.50.0 | bump → v0.51.0（与 README 同步）| — |
| `CHANGELOG.md` | 最新 [0.50.0]，**无 [Unreleased]** | 主 Agent 新增 [Unreleased] 或直接建 v0.51.0 节（建议建 v0.51.0 节），见 §4 | — |
| `agate/UPGRADING.md` | 最新 v0.50.0 章节 | **新增 v0.51.0 章节**（破坏性变更条目，见 §5）| ✅ 新增 |
| 稳定版引用 | AGENTS.md/文档优先写"稳定版"不写死版本号 | 核对无硬编码 v0.50.0 需改的稳定版引用（README 安装示例 `v0.49.0` 为示例可保留）| — |
| `docs/roadmap*`（hardening-roadmap.md）| RM-AG0004/0006/0007 待回写 | **P8 主 Agent 确认回写 done**（P2 §6.4 外部联动）| — |

> 无独立 `version` 文件（仓库根无 version 文件，版本唯一载体为 README badge——`ls` 已核实）。bump-version 命令对象 = README.md + README.zh-CN.md badge 两处。

## 4. CHANGELOG 更新建议（v0.51.0 节内容）

> 实际写入由主 Agent 执行（P8 gate：暂存区 CHANGELOG 必有变更）。

建议 `CHANGELOG.md` 在 `## [0.50.0]` 前新增：

```markdown
## [0.51.0] - 2026-08-18

### 新增（TAG0006：agate UI/UX 验收质量机制）

- **P1 vision 能力三态硬声明（check-gate.py gate_p1）**：`domains` 含 `frontend` 的任务 P1 必须在 `capability_requirements` 声明视觉能力条目（`need`/`name` 含 visual/vision）且 `status ∈ {available, supplementable, GAP}`；缺失/非法 → exit 1。既有任务无 frontend domains 不触发（向后兼容）。
- **P1 渲染形态/维度声明（可选字段）**：frontmatter 新增可选 `ui_render_shape`（规范值 layout / render_component / temporal_effects）+ `ui_ux_dimensions`（presence 语义，缺失 = 布局型默认，不破坏性）；跨阶段一致（I14）由 P2 gate + P7 CHECK 11 校验。
- **P2 UI 设计节检查（check-gate.py gate_p2）**：`ui_affected: true` 的 P2-design.md 必须含「UI 设计」节（渲染形态声明 + 按形态 checklist：常规布局型布局/交互/视觉；渲染组件型渲染正确性/动效时序）+ P1-P2 形态一致性规范化值比对（`_canonical_shape` 同义映射）；缺节/缺声明/不一致 → exit 1。由 architect 兼任产出，**不新增 designer 角色**。
- **P6 三态分档双证据 + 证据形式按形态（check-p6-evidence / check-p6-provenance）**：P1 vision=GAP → 降级为像素检测 + 人工复核记录（`(manual-review: <file>)`，缺 → exit 1）；available/无声明（默认 available）保留既有 R1b vision YAML + blocker_count 强制。渲染组件型形态可用帧序列 `frames/` / 渲染输出对比 `renders/`（须含 actual + diff.json 量化度量）/ 时序截图 `-tN`，纯文本证据拦截。
- **input-state/review 人工复核（BDD-13）**：输入态/交互形态变化类 BDD 结论必须附人工复核记录（复核人/时间/结论）。
- **P7 一致性 CHECK 11（check_uiux_doc_anchors）**：断言各协议文档含 UI/UX 机制条文锚点，防文档-脚本-单测三件套漂移。
- **plan-design-review 维度五维→七维**：新增视觉设计/交互设计细节/渲染正确性与时序 0-10 可判定评分项 + 七维边界注。
- **dispatch-prompt 新增「能力自查（强制）」节 + A3 视觉 supplementable 注入**：subagent 无法调用视觉能力时须报告 [CAPABILITY_GAP] 走降级，不静默假设（BDD-11/12）。

### 变更（行为变化，需读者注意）

- **avg-hash 雷同截图判定升级（check-p6-evidence.py avg-hash）**：视觉高度相似截图从非阻断 WARNING（exit 2）升级为「降级待复核」——含人工复核记录（`雷同截图复核`/`manual-review` 引用）→ 放行；无记录 → exit 1 阻断。md5 硬阻断语义不变。帧序列/时序截图按同 BDD 组（bdd-id 前缀）豁免相邻样本。**本行为变化对所有任务的 P6 截图证据路径生效，见 `agate/UPGRADING.md` v0.51.0 章节。**

### 测试
- P3 53 新增用例（test_check_gate 20 / test_check_p6_evidence 15 / test_check_p6_provenance 4 / test_review_role_docs 14）；全量 pytest 881 passed + 2 skipped 无回归（BDD-15）；consistency 0 ERROR；count-tests 883（≥749 单调不减）；ruff 通过。
```

## 5. UPGRADING.md 更新建议（v0.51.0 章节——主 Agent 新增，破例变更逐条列）

> 主 Agent P8 必须新增 `agate/UPGRADING.md` 的 v0.51.0 章节（AGENTS.md 版本发布清单步骤 3，v0.44.0 漏更新教训）。建议内容：

```markdown
### v0.51.0 — agate UI/UX 验收质量机制（影响：frontend / UI 任务；存量非 UI 项目无感）

> 本版本为**机制增强**，破坏性变更限定于新声明门槛；不新声明前端的存量项目零动作无感。本版本章节必须包含以下破坏性/行为变更条目：

| 变更 | 影响 | 升级动作 |
|------|------|---------|
| P1 `frontend` 任务必须声明 vision 三态（capability_requirements 视觉条目）| 仅 `domains` 含 `frontend` 的新/进行中任务。缺失 → P1 gate exit 1 | 进行中的 frontend 任务在 P1 补声明 vision 条目（status ∈ available/supplementable/GAP）|
| P2 `ui_affected: true` 任务必须含「UI 设计」节 + 渲染形态声明 | 仅 `ui_affected: true` 的 P2 任务。缺节/缺声明/与 P1 形态不一致 → P2 gate exit 1 | 进行中的 UI 任务补 UI 设计节 + 形态声明（复用 P1 形态）|
| **P6 avg-hash 雷同截图判定升级（WARNING → 降级待复核）** | **对所有任务的 P6 截图证据路径生效**（不限于 UI 任务）。视觉高度相似截图无复核记录 → exit 1 | 升级前已存在雷同截图证据的任务：补 `雷同截图复核`/`manual-review` 复核记录，或改用非截图证据；md5 硬阻断不变 |
| P1/P2 渲染形态/维度可选声明 | 缺失 = 布局型默认，**不破坏性** | 无需动作；渲染组件/时序特效类任务建议声明以启用形态适配 |

**迁移最小动作**：`git pull` + 重跑 `install-hook.py`（hook 指向 fixed resolve-entry，自动跟随新版本）。仅"要继续推进的进行中任务"需补声明/复核；已完成任务零触发。
```

## 6. debt_check 字段

`debt_check: reviewed`

已核对 `agate-workspace/debt/tech-debt.md`（150 行，DEBT0001-0006）。本任务关联条目：

- **DEBT0005**（三态解析重复）：本任务已落地修复——`agate_common.py` 新增 `read_vision_tri_state(p1_file)`，check-gate / check-p6-evidence / check-p6-provenance 三处复用（P4-implementation §1）。**registry 仍 `status: open`** ⚠️ P8 主 Agent 应推动由主人在 P4/P5 完成后将该条目标 `closed`（closure_criteria"公共 helper 就位 + 三处复用 + 全量 pytest 825+ 全绿"已满足）。
- **DEBT0006**（check-p6-evidence ahash zip 错位）：本任务已落地修复——`ordered` 仅收集图片文件（`_is_image`）与 ahash 子进程输出一一对应，消除 zip 错位（P4-implementation B2）；新增 `test_ahash_4_nonimage_file_misalign_temporal_exempt_exit_0` 判别式回归。**registry 仍 `status: open`** ⚠️ 同 DEBT0005，P8 主 Agent 应推动标 `closed`（closure_criteria 已满足）。

> 备注：dispatch-context 描述 DEBT0005/0006 "已登记"，实现层面的 P4 已闭合两处缺陷，但 registry 字段未翻转为 closed——P8 主 Agent 在 READY 收尾时核对并更新 registry 状态（非发布阻断项，gate 只查 `debt_check` 字段存在）。

## 7. 临时资源清单（releaser → 主 Agent 交接）

```yaml
temporary_resources:
  services_processes: []
  temp_data: []
  dev_installs: []
  notes: >
    本任务为纯脚本 + 文档 + 单测改造（dogfooding 双工作区），无任何临时服务/进程启动、
    无临时数据库/文件目录、无开发安装（未改 pip/pipx/venv，未装新包——Pillow 用既有开发环境）。
    READY 收尾检查的"测试环境已清理 / 开发环境已还原"项仅需确认 worktree 无残留调试进程即可。
```

## 8. 主 Agent 亲自执行项（releaser 不执行）

- [ ] bump-version：README.md + README.zh-CN.md badge `v0.50.0` → `v0.51.0`（无独立 version 文件）
- [ ] CHANGELOG.md 写入 v0.51.0 节（§4 建议内容）
- [ ] agate/UPGRADING.md 新增 v0.51.0 章节（§5 建议内容）
- [ ] 重跑 P5 gate：`python3 -m pytest -q --tb=no agate/tests/` exit 0 + failed==0
- [ ] `git log v0.50.0..HEAD --oneline` 对照 CHANGELOG 无遗漏
- [ ] consistency：`python3 agate/scripts/check-protocol-consistency.py` 0 ERROR（用 worktree 自己的）
- [ ] count-tests：`bash agate/tests/scripts/count-tests.sh`（883 ≥ 749 无漂移）
- [ ] 干净 checkout 跑一次 consistency（dogfooding 任务，worktree .worktrees 路径过滤可能掩盖扫描问题）
- [ ] git commit + git tag v0.51.0（`--no-ff` 普通 merge，禁止 squash）
- [ ] docs/hardening-roadmap.md 的 RM-AG0004/0006/0007 回写 done（P2 §6.4）
- [ ] .state.yaml phase → READY、active-tasks.md 更新、DEBT0005/0006 registry 状态核对

## 9. PROD_TOUCHED 标记

`[PROD_NOT_TOUCHED]` 本任务全部在 worktree（/home/kity/oclab/agate/.worktrees/agate-TAG0006/）执行，未触碰主 checkout（/home/kity/oclab/agate）与 ~/.agate 稳定版。

## 10. Lessons Learned

- **流程**：dogfooding 任务多包（agate-docs/scripts-py/tests）实为同仓库单版本，P8 需识别"多包声明 ≠ 多版本分发"，版本 bump 收拢到 README badge + CHANGELOG + UPGRADING 三件套，避免给同一仓库打多个 tag（来源 TAG0006，2026-08-17）。
- **流程**：avg-hash WARNING→硬拦是"主 Agent 口中向后兼容"与"脚本行为变化"的交界——发布时把行为变化如实写进 UPGRADING 破坏性变更条目，即便判 minor 也不静默（来源 TAG0006，2026-08-17）。
- **架构**：`debt_check: reviewed` 需区分"实现已修复"（P4 闭合）与"registry status 未翻转"（open）两个事实——releaser 应如实记录 gap 并交主 Agent READY 收尾核对，不得谎报 closed（来源 TAG0006，2026-08-17）。

## 11. 门槛自检

- [x] P8-release.md 存在 + Header 完整（phase P8 / task_id / parent / trace_id / status / agent）
- [x] 含 `bump_type: minor` + 理由
- [x] 含 `debt_check: reviewed` + 条目 id 清单（DEBT0005/0006）
- [x] 含版本引用文件清单（README badge / CHANGELOG / UPGRADING / 稳定版引用）
- [x] 含 CHANGELOG 更新建议（v0.51.0 节内容）
- [x] 含临时资源清单
- [x] 主 Agent 亲自执行项已列出（releaser 不含 git 操作）
- [ ] 主 Agent 执行 gate：`check-gate.py P8 $TASK_DIR`（bump_type/debt_check 字段存在性；本文件为 draft，暂存区变更待主 Agent bump 后提交）
