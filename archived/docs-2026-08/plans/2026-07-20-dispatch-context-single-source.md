# dispatch-context 单一信息源重构 实施计划 (v8 — 评审修正版)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 dispatch-context 从"过门条"变成 subagent 的核心信息源，消除派发 prompt 与 dispatch-context 的信息重复，使主 Agent 必须在派发前写好 dispatch-context（否则 subagent 拿不到信息）。

**Architecture:** 
1. 文件名从 `P{N}-dispatch-context.md` 改为 `P{N}-dispatch-context-{role}.md`——每个 subagent 一个 dispatch-context，只含该角色相关的导航信息，无噪音
2. dispatch-context 新增"派发指引"节（目标/约束/上游关联/输入文件），从 dispatch-prompt 迁移任务特定内容
3. dispatch-prompt 精简但不萎缩：移除任务特定内容（目标/关注点/约束/输入文件列表），保留执行框架（环境隔离/分阶段落盘/输出约束/返回格式/项目约定）
4. 所有 P1-P8 阶段统一强制 dispatch-context 存在
5. hook/provenance 校验从固定文件名改为 glob 匹配 `P{N}-dispatch-context-*.md`
6. dispatch-context 格式从纯 Markdown 改为 Markdown + XML 标记——Anthropic+OpenAI 双重官方推荐，提升 LLM 节定位准确度

**Tech Stack:** bash, markdown+XML 模板, bats 测试

**Task 依赖顺序**：Task 1→2→3→4→5→6/7→8→9→10→11→12→13→14。Task 6/7 可并行但须在 Task 1/2 后。Task 3 Step 7 全文替换须在 Step 1-6 完成后执行。

---

## 关键设计决策

### 为什么一个 subagent 一个 dispatch-context？

同一阶段可能派发多个 subagent，导航信息完全不同：
- P1：analyst（关注 BDD 完整性）+ requirements-review（关注 P1 纯净性）
- P4：implementer（关注代码实现）+ review（关注安全/质量）+ cso（关注安全）
- P6：verifier（关注功能验证）+ vision-analyst（关注 UI 视觉）

一个 dispatch-context 给所有 subagent 看，subagent 要自己分辨"哪些是给我的"——增加认知负担。每个 subagent 只看自己的 dispatch-context，信息零噪音。

### 命名格式

`P{N}-dispatch-context-{role}.md`

评审 subagent 也需要 dispatch-context，但评审角色文件本身不新增"输入"节——dispatch-context 引用由 dispatch-prompt 模板统一注入。

### dispatch-prompt 精简但不萎缩（提示词工程 v7 修正）

**原则**：dispatch-prompt 移除的是任务特定内容（每次派发都不同的），保留的是跨阶段通用执行纪律。

| 保留在 dispatch-prompt | 移入 dispatch-context |
|----------------------|---------------------|
| 环境隔离（硬约束） | 目标 |
| 分阶段落盘（执行纪律） | 约束（原"关注点"+"已知约束"合并） |
| 输出路径约束（硬约束） | 上游关联 |
| Header 规范（格式约束） | 输入文件 |
| 返回格式（格式约束） | |
| 返回前自检（质量约束） | |
| 项目约定（必读）（跨任务） | |
| dispatch-context 权威性声明 | |
| 执行顺序 | |

**dispatch-context 权威性声明**：dispatch-prompt 中加一句"dispatch-context 中的派发指引是本次任务的强制指令，不是参考信息"——利用 user prompt 的优先级提升 dispatch-context 指令的 LLM 遵从度。

**执行顺序**：dispatch-prompt 提供 7 步执行框架，subagent 不需要自行推断执行顺序。具体步骤：
```
1. 读取 dispatch-context 派发指引（目标/约束/上游关联/输入文件）
2. 读取角色定义文件和项目约定
3. 按输入文件列表逐一读取，每读完一个追加 progress
4. 按 dispatch-context 约束执行任务
5. 写产出文件到约定路径
6. 自检产出文件（Header/内容/证据）
7. 返回路径 + 一句话摘要
```

### dispatch-context 格式：Markdown + XML 标记（提示词工程 v7 修正）

**为什么不用纯 Markdown？** 纯 Markdown 缺乏明确节边界标记，LLM 可能混淆指令性内容与参考性内容。Anthropic 官方文档明确推荐"Structure prompts with XML tags"。

**为什么不用 JSON/YAML？** 阶段卡片是 CLI 输出的 markdown 长文本，JSON/YAML 嵌入需转义，破坏 sha256 校验链。LLM 生成 JSON/YAML 的错误率也高于 Markdown+XML。

**XML 标记方案**：在现有 markdown 节标题外，用 XML 标签包裹各节提供无歧义边界。hook 脚本已有 `<!-- AGATE_CARD_START/END -->` 先例，新增标签无需改变解析方式。

| 评分维度 | 纯 Markdown | Markdown+XML | JSON | YAML |
|----------|-----------|-------------|------|------|
| LLM 生成 | 9 | 8 | 5 | 4 |
| LLM 解析 | 6 | 9 | 8 | 7 |
| hook 解析 | 8 | 8 | 4 | 5 |
| 人类可读 | 9 | 8 | 4 | 7 |
| token 效率 | 9 | 8 | 6 | 7 |
| 容错 | 7 | 8 | 3 | 4 |
| **总分** | **48** | **49** | **30** | **34** |

### 合并"关注点"+"已知约束"为"约束"（提示词工程 v7 修正）

LLM 对"约束"的遵从度显著高于"关注点"——"关注"暗示可选，"约束"暗示必遵。原 5 子节（目标/关注点/已知约束/上游关联/输入文件）合并为 4 子节：

| 原子节 | 新子节 | 理由 |
|--------|--------|------|
| 目标 | 目标 | 不变 |
| 关注点 | 约束 | 与"已知约束"合并，消除"关注 vs 行动"歧义 |
| 已知约束 | （并入约束） | 同上 |
| 上游关联 | 上游关联 | 不变 |
| 输入文件 | 输入文件 | 不变 |

### 角色文件不列 dispatch-context 路径

角色定义是通用的（"你是什么角色"），dispatch-context 路径是任务特定的（含 task_id/phase/role）。两者层次不同。dispatch-prompt 是 dispatch-context 路径的唯一注入点。

角色文件删除"输入"节中 `P{N}-dispatch-context.md` 占位符路径引用（不是更新为新格式，是删除），加通用规则："dispatch-prompt 中指定的输入文件是必读的，按 prompt 给出的路径读取"——补偿安全网。

### hook / provenance 校验

当前检查固定文件名 `${PHASE}-dispatch-context.md`。改为 glob 匹配 `P{N}-dispatch-context-*.md`（至少一个存在）。sha256 校验逐个文件校验。使用 bash 数组 + for 循环。

**glob 实现骨架**（v8 新增，解决 BLOCKER）：
```bash
shopt -s nullglob
DC_FILES=("$TASK_DIR/${PHASE}-dispatch-context-"*.md)
shopt -u nullglob
if [ ${#DC_FILES[@]} -eq 0 ]; then
    # 走强制检查逻辑（暂存区含阶段产出 → 必须有 dispatch-context）
else
    for DC_FILE in "${DC_FILES[@]}"; do
        # 逐个校验 hash
    done
fi
```

### P5 强制 dispatch-context 的判定逻辑（v8 新增，解决 BLOCKER）

P5 产出是 `P5-test-results/` 目录而非 `.md` 文件，PHASE_OUTPUT 匹配模式需特殊处理：
- P5 的 PHASE_OUTPUT 判定改为检查目录存在性：`[ -d "$TASK_DIR/P5-test-results" ]`
- 暂存区检查：`git diff --cached --name-only | grep -qE "P5-test-results/"`
- case 语句新增：`P5) PHASE_OUTPUT_DIR="P5-test-results" ;;` + 目录存在性判定

### 向后兼容

破坏性变更。过渡期：check-p6-provenance.sh 的 skip 模式同时匹配新旧格式。过渡期结束条件：下一个 major 版本（v2.0）发布时移除旧格式兼容，在代码中加 `# TODO: remove old format compatibility in v2.0` 注释。

### 全文替换策略

两种格式需替换：
1. `P{N}-dispatch-context.md` / `${PHASE}-dispatch-context.md` → `P{N}-dispatch-context-{role}.md`
2. 裸引用 `dispatch-context.md`（无 `P{N}-` 前缀）→ 按上下文改为新格式

机制描述（"dispatch-context 审计"等，不含 `.md` 后缀）不需要改文件名格式。

---

## v7→v8 变更摘要

| 变更 | v7 | v8 | 理由 |
|------|----|----|------|
| Task 2 执行顺序 | "5-7 步框架"无具体内容 | 给出 7 步具体内容 | 评审 MAJOR：执行者无法凭空编写 |
| Task 2 "输入"节 | "简化为 dispatch-context + 角色定义" | 明确：删除 4 行，新增"dispatch-context（核心输入）"节 | 评审 MAJOR：WORKFLOW.md 去向不明 |
| Task 3 Step 2 行号 | "第 391-460+ 行" | "第 391-453 行" | 评审 BLOCKER：行号偏移 |
| Task 3 Step 6 910 行 | "文件名替换+回退诊断节改引用" | 整句重写 | 评审 MAJOR：回退诊断节已不存在 |
| Task 3 Step 7 | "排除已重写的第 282-340 行" | 删除排除说明 | 评审 MINOR：排除无必要 |
| Task 4 Step 1 | "第 56/194 行裸引用" | "第 56 行"（删除不存在的 194 行） | 评审 MAJOR：行号错误 |
| Task 5 | 3 步笼统描述 | 逐卡片列出具体改动位置 | 评审 MAJOR |
| Task 6 Step 1 | "PHASE_OUTPUT case 加 P5/P7/P8" | P5 用目录存在性判定 | 评审 BLOCKER：P5 产出是目录 |
| Task 6 Step 2 | "bash 数组 glob"无实现细节 | 给出 glob 实现骨架 | 评审 BLOCKER |
| Task 6 Step 3 | "git ls-tree 替代 git show" | 给出具体实现 | 评审 BLOCKER |
| Task 7 Step 4 | sed 排除 XML 标记块 | 改用 awk 模式匹配 | 评审 BLOCKER：sed 对不完整标签脆弱 |
| Task 8 | "删除输入节中 dispatch-context 路径引用" | 明确：删除该行（非更新），加通用规则行 | 评审 MAJOR |
| Task 9 | "全文搜索替换"无文件清单 | 列出 Task 1-8 未覆盖的文件清单 | 评审 MAJOR |
| Task 10 | 锚点表更新不完整 | 为每个新增锚点指定目标文件和关键词 | 评审 MAJOR |
| Task 11 Step 1 | DC 测试改动缺逐用例断言 | 列出 DC.1-DC.8 每个用例的断言变更 | 评审 MAJOR |
| Task 11 Step 3 | D-drift-4 更新方向 | 明确新断言 | 评审 MAJOR |
| Task 1 模板 | objective_info 无内容指引 | 加内容指引 | 评审 MAJOR |
| Task 12 | 无具体内容 | 给出更新后的 CONTEXT.md 条目 | 评审 MINOR |
| 过渡期 | 无结束条件 | v2.0 移除旧格式兼容 | 评审 MINOR |
| custom-role.md | 未提及 | Task 9 文件清单中包含 | 评审 MINOR |
| task-files.md | 未提及 | Task 9 文件清单中包含 | 评审 MINOR |

---

## 文件结构

### 受影响文件清单（按 Task 分配）

| 文件 | 负责 Task | 改动类型 |
|------|----------|---------|
| `agate/assets/templates/dispatch-context.md` | Task 1 | 整文件重写 |
| `agate/assets/templates/dispatch-prompt.md` | Task 2 | 大幅修改 |
| `agate/dispatch-protocol.md` | Task 3 | 大幅修改 |
| `agate/orchestrator-template.md` | Task 4 | 局部修改（3 处引用） |
| `agate/state-machine.md` | Task 4 | 局部修改（2 处引用） |
| `agate/phase-cards/P1-P8` | Task 5 | 局部修改（每张卡片 1-3 处） |
| `agate/scripts/pre-commit-gate.sh` | Task 6 | 大幅修改 |
| `agate/scripts/check-p6-provenance.sh` | Task 7 | 中等修改 |
| `agate/assets/execution-roles/*.md`（7 个） | Task 8 | 局部修改 |
| `agate/assets/review-roles/*.md`（9 个） | Task 8 | 检查+局部修改 |
| `agate/assets/templates/custom-role.md` | Task 9 | 局部修改（行 24） |
| `agate/assets/templates/task-files.md` | Task 9 | 局部修改（行 43） |
| `agate/WORKFLOW.md` | Task 9 | 局部修改（行 274） |
| `agate/LIMITATIONS.md` | Task 9 | 局部修改（行 40） |
| `agate/role-system.md` | Task 9 | 局部修改（行 77/124） |
| `agate/scripts/README.md` | Task 9 | 局部修改（行 50） |
| `agate/scripts/check-protocol-consistency.py` | Task 10 | 局部修改（CHECK 9） |
| `agate/tests/integration/dispatch-context-card.bats` | Task 11 | 大幅修改 |
| `agate/tests/integration/dispatch-context-warning.bats` | Task 11 | 中等修改 |
| `agate/tests/unit/check-gate.bats` | Task 11 | 局部修改（D-drift-4） |
| `agate/tests/unit/check-p6-provenance.bats` | Task 11 | 中等修改 |
| `agate/tests/integration/pre-commit-hook.bats` | Task 11 | 中等修改 |
| `agate/CONTEXT.md` | Task 12 | 局部修改 |

---

### Task 1: 更新 dispatch-context 模板

**Files:** `agate/assets/templates/dispatch-context.md`

- [ ] **Step 1: 修改模板** — 改为 Markdown + XML 标记格式（见上方"dispatch-context 格式"节）。`<objective_info>` 节增加内容指引：环境状态/关键标识/查证结果，主 Agent 知道该填什么格式。

---

### Task 2: 精简 dispatch-prompt 模板

**Files:** `agate/assets/templates/dispatch-prompt.md`

- [ ] **Step 1: 修改模板** — 精简但不萎缩：

**删除的节**（任务特定，已迁移到 dispatch-context）：
- "任务"节（目标/关注点/已知约束/与上阶段关联）→ 改为"dispatch-context（核心输入）"节
- "输入"节（行 22-27）→ 删除 P0-brief/上一阶段产出/WORKFLOW.md/dispatch-context 4 行。dispatch-context 的"输入文件"子节已包含 P0-brief 和上一阶段产出；WORKFLOW.md 不再由 dispatch-prompt 列出（subagent 按需从 dispatch-context 约束节获取流程信息）

**保留的节**（跨阶段通用执行纪律）：项目约定/环境隔离/分阶段落盘/输出路径约束/Header 规范/能力补充/门槛/返回前自检/返回格式/阶段特定提示

**新增的节**：
- "dispatch-context（核心输入）"节：`读取并严格遵循：docs/tasks/{Txxx}/P{N}-dispatch-context-{role}.md` + 权威性声明
- "执行顺序"节（7 步框架，见上方"执行顺序"节）

- [ ] **Step 2: 更新"关键提醒"节** — 移除"dispatch-context.md 按需引用"，改为 `- **dispatch-context 是 subagent 的核心输入**：主 Agent 派发前必须写好 dispatch-context（含目标/约束/上游关联/输入文件），subagent 从中获取任务特定信息，prompt 只提供跨阶段通用执行纪律`

---

### Task 3: 更新 dispatch-protocol.md

**Files:** `agate/dispatch-protocol.md`

- [ ] **Step 1: 完整重写"dispatch-context.md 规范"节（第 282-340 行）** — 文件名改为 `P{N}-dispatch-context-{role}.md`，内容结构内联 Task 1 新模板（Markdown+XML 格式），4 子节（目标/约束/上游关联/输入文件），信息来源表更新，生命周期改为"每个 subagent 一个"，所有阶段统一强制，"派发指引"必填，回退不再写"回退诊断节"
- [ ] **Step 2: 更新内联版 prompt 模板（第 391-453 行）** — 与 dispatch-prompt.md 变更范围一致：删除"任务"节和"输入"节，新增"dispatch-context（核心输入）"节+执行顺序节+权威性声明，保留项目约定/环境隔离/落盘/输出/Header/门槛/返回
- [ ] **Step 3: 更新"标准派发流程"步骤** — 步骤 3 增加 dispatch-context 路径为必须传入项
- [ ] **Step 4: 更新 N2 禁令描述（第 362-375 行）+ 第 382 行落盘时机表** — "dispatch-context.md 回退诊断节"改为"dispatch-context 上游关联节引用 gate-diagnosis.md 路径"
- [ ] **Step 5: 更新缺失 WARNING 描述（第 789 行）** — 逻辑从固定文件名检查改为 glob 匹配检查："暂存了阶段产出但无 `P{N}-dispatch-context-*.md` 时发 WARNING"
- [ ] **Step 6: 更新其他旧格式引用** — 第 694/716/910 行 + 第 575 行裸引用。第 910 行整句重写为：`diff=1 回退（如 P5→P4）：直接退，诊断信息写入 P{N}-gate-diagnosis.md，新阶段 dispatch-context 的上游关联节引用诊断路径，无需 PAUSED。`
- [ ] **Step 7: 全文搜索替换** — 须在 Step 1-6 完成后执行。Step 1 重写后 282-340 行已是新格式，全文替换不会匹配到新格式中的 `dispatch-context-{role}.md`，无需排除行范围。

---

### Task 4: 更新 orchestrator-template.md + state-machine.md

- [ ] **Step 1: orchestrator-template.md** — 第 64 行 `P{N}-dispatch-context.md` → `P{N}-dispatch-context-{role}.md`；第 56 行裸引用 `dispatch-context` → 按上下文更新；第 99 行 `dispatch-context.md` → `dispatch-context`（通用约束描述，不含 `.md` 后缀）；全文旧格式替换
- [ ] **Step 2: state-machine.md** — 第 584 行 `dispatch-context.md` → `dispatch-context`（机制描述不改文件名格式）；第 602 行 `P4-dispatch-context.md 的回退诊断节` → `P4-dispatch-context-{role}.md 的上游关联节引用 gate-diagnosis.md 路径`；全文旧格式替换

---

### Task 5: 更新阶段卡片 P1-P8

- [ ] **Step 1: 逐一检查每张卡片"首次进入"节格式** — 确认卡片中 dispatch-context 引用的位置
- [ ] **Step 2: 在"派发 subagent"步骤中更新 dispatch-context 引用** — 每张卡片具体改动：
  - P0: 无 dispatch-context 引用，不改
  - P1: "派发 analyst"步骤中加"写 P1-dispatch-context-analyst.md"子步骤；"派发 requirements-review"步骤中加"写 P1-dispatch-context-requirements-review.md"子步骤
  - P2: "派发 architect"步骤中加"写 P2-dispatch-context-architect.md"子步骤
  - P3: "派发 test-designer"步骤中加"写 P3-dispatch-context-test-designer.md"子步骤
  - P4: "派发 implementer"步骤中加"写 P4-dispatch-context-implementer.md"子步骤
  - P5: "派发 verifier"步骤中加"写 P5-dispatch-context-verifier.md"子步骤
  - P6: 第 63 行旧格式引用更新 + "派发 verifier"步骤中加"写 P6-dispatch-context-verifier.md"子步骤
  - P7: 第 75 行旧格式引用更新 + "派发 consistency-reviewer"步骤中加"写 P7-dispatch-context-consistency-reviewer.md"子步骤
  - P8: "派发 releaser"步骤中加"写 P8-dispatch-context-implementer.md"子步骤（P8 复用 implementer.md 角色文件 P8 模式，文件名含 implementer）
- [ ] **Step 3: 确认卡片内无旧格式引用** - P6:63 是 `dispatch-context审计`（机制描述，无 `.md`），P7:75 是 `dispatch-context`（无 `.md`）。两者都不是 `dispatch-context.md` 旧格式引用，无需替换，确认即可。

---

### Task 6: 更新 pre-commit-gate.sh

- [ ] **Step 1: P5/P7/P8 也强制 dispatch-context** — PHASE_OUTPUT case 改为：
  - P1/P2/P3/P6/P7/P8 用 `.md` 匹配
  - P5 用 `PHASE_OUTPUT_DIR="P5-test-results"` + 目录存在性判定
  - P4 用代码文件判定（见 pre-commit-gate.sh 第 190-194 行现有逻辑，不变）
- [ ] **Step 2: 2p 节改为 bash 数组 glob** — 实现骨架：`shopt -s nullglob; DC_FILES=("$TASK_DIR/${PHASE}-dispatch-context-"*.md); shopt -u nullglob`；0 匹配走强制检查逻辑；for 循环逐个校验 hash，错误消息含 `$(basename "$DC_FILE")`
- [ ] **Step 3: B3 WARNING 节改为 glob** — `git ls-tree HEAD "${TASK_REL}/" 2>/dev/null | grep -qE "${PHASE}-dispatch-context-.*\.md$"` 替代 `git show`（加 `2>/dev/null || true` 容错处理首次 commit 无 HEAD 场景）
- [ ] **Step 4: 更新所有错误消息** — 全部从 `dispatch-context.md` → `dispatch-context-{role}.md（至少一个）`
- [ ] **Step 5: hook 脚本适配 XML 标记** — 改用 awk 模式匹配排除三个块（AGATE_CARD + dispatch_guide + objective_info），比 sed 范围删除更健壮

---

### Task 7: 更新 check-p6-provenance.sh

- [ ] **Step 1: 审计 2 改为 glob 遍历** — `shopt -s nullglob; DISPATCH_CTXS=("$TASK_DIR/P6-dispatch-context-"*.md); shopt -u nullglob` + for 循环
- [ ] **Step 2: skip 模式新旧兼容** — `*-dispatch-context.md|*-dispatch-context-*.md`。加注释 `# TODO: remove old format compatibility in v2.0`
- [ ] **Step 3: 更新注释和错误消息** — 错误消息含具体文件名：`GATE PROVENANCE: $(basename "$DISPATCH_CTX") 含 N 处验收结论预判`
- [ ] **Step 4: 适配 XML 标记** — 审计 2 的排除逻辑改用 awk（与 Task 6 Step 5 一致）

---

### Task 8: 更新角色文件

- [ ] **Step 1: 执行角色（6 个文件，vision-analyst.md 无引用只需确认）** — 每个文件：1. 删除"输入"节中 `docs/tasks/{Txxx}/P{N}-dispatch-context.md（若存在：...）` 行（不是更新为新格式，是删除——dispatch-prompt 是 dispatch-context 路径的唯一注入点）。verifier.md 需删除两处（P5 模式行 35 和 P6 模式行 112）；2. 加通用规则行：`- dispatch-prompt 中指定的输入文件是必读的，按 prompt 给出的路径读取`；3. verifier.md 第 96 行 `P{N}-dispatch-context.md 禁止预判` → `dispatch-context 禁止预判`
- [ ] **Step 2: 评审角色（11 个文件）** — 只检查是否有旧格式路径引用需删除。当前评审角色文件无 dispatch-context 路径引用，确认即可

---

### Task 9: 更新其他协议文件

**Task 1-8 未覆盖的文件清单**：

| 文件 | 行号 | 改动 |
|------|------|------|
| `agate/assets/templates/custom-role.md` | 24 | 删除 dispatch-context 路径行，加通用规则行 |
| `agate/assets/templates/task-files.md` | 43 | 更新文件名为 `P{N}-dispatch-context-{role}.md`，描述增加"每个 subagent 一个" |
| `agate/WORKFLOW.md` | 274 | 更新为新格式（保留 WORKFLOW.md 在 dispatch-prompt "项目约定"节中，或在 dispatch-context 模板"输入文件"子节中加 WORKFLOW.md 路径作为默认项） |
| `agate/LIMITATIONS.md` | 40 | 更新为新格式 |
| `agate/role-system.md` | 77, 124 | 按上下文更新裸引用 |
| `agate/scripts/README.md` | 50 | 更新为新格式 |

- [ ] **Step 1: 逐一更新上述文件** — 注意机制描述不改

---

### Task 10: 更新 check-protocol-consistency.py 锚点表

- [ ] **Step 1: CHECK 9 锚点表更新** — "dispatch-context 任务上下文节" → "dispatch-context 派发指引节"（keywords: `["dispatch-context", "dispatch_guide"]`）；新增 "dispatch-context role frontmatter"（target: dispatch-context.md, keywords: `["role:"]`）；新增 "dispatch-context XML 标记"（target: dispatch-context.md, keywords: `["<dispatch_guide>", "<objective_info>"]`）；D-drift-4 从检查 dispatch-prompt 含"目标："改为检查 dispatch-context 含 `<dispatch_guide>` + `### 目标` + `### 约束`

---

### Task 11: 更新测试

**Files:** 5 个 bats 文件

- [ ] **Step 1: dispatch-context-card.bats** — `_create_dispatch_context` 新增 role 参数+新文件名+新模板+XML 标记+4 子节；DC.1/DC.2/DC.3 更新文件名和模板格式断言；DC.4 错误消息改为 glob 提示；DC.5 改为 P5 强制测试（语义反转：当前 DC.5 测"P5 产出 commit 缺 dispatch-context.md -> 不拦截"，改为"P5 产出 commit 缺 dispatch-context -> 拦截"，断言从 `[[ "$output" != *"需提供"* ]]` 改为 `[ "$status" -ne 0 ]` + `[[ "$output" == *"dispatch-context"* ]]`）；新增 DC.6/7/8 P7/P8 强制；新增 DC.multi 多文件 hash 校验
- [ ] **Step 2: pre-commit-hook.bats** — 同步更新（含 P5/P7/P8 强制测试 + XML 标记适配）
- [ ] **Step 3: check-gate.bats D-drift-4** — 删除对 dispatch-prompt.md 含"目标："和"关注点："的旧断言；新增检查 dispatch-context.md 含 `<dispatch_guide>` + `### 目标` + `### 约束`；D-drift-4b 从检查"任务上下文"改为检查 `<dispatch_guide>`
- [ ] **Step 4: check-p6-provenance.bats** — PV fixture 新文件名+新模板+XML 标记；新增 PV.18 旧格式共存 skip 测试
- [ ] **Step 5: dispatch-context-warning.bats** — B3 WARNING 测试从固定文件名检查改为 glob 匹配

---

### Task 12: 更新 CONTEXT.md

- [ ] **Step 1: dispatch-context 术语** — 更新为：`dispatch-context | 派发前主 Agent 写的核心信息源，含派发指引（目标/约束/上游关联/输入文件）+ 阶段卡片 + 客观查证信息。文件名 P{N}-dispatch-context-{role}.md，每个 subagent 一个。禁止含 PASS/FAIL 预判 | dispatch-protocol.md`

---

### Task 13: 全文搜索替换兜底检查

- [ ] **Step 1:** `grep -rn 'dispatch-context\.md' agate/ --include='*.md' --include='*.sh' | grep -v 'dispatch-context-.*\.md'` → 0 结果

---

### Task 14: 验证

- [ ] **Step 1:** `shellcheck -S warning agate/scripts/*.sh`
- [ ] **Step 2:** `python3 agate/scripts/check-protocol-consistency.py` → 0 ERROR
- [ ] **Step 3:** `bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/` → 全绿
- [ ] **Step 4:** `bash agate/tests/scripts/count-tests.sh` → 用例数未漂移
