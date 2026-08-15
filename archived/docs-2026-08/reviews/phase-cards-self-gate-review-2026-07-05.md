---
review_date: 2026-07-05
reviewer: protocol-alignment-review
change_summary: Phase Card 渐进披露体系完整实施（7 commit，1343 行新增 / 13 行修改），含 check-gate.sh P0 分支修复 + pre-commit-gate.sh 2j/2k 容错
files_changed:
  - agate/phase-cards/{P0..P8}*.md + README.md (10 个新增)
  - agate/rules/{state-transitions,review-mapping}.md (2 个新增)
  - agate/scripts/check-gate.sh (P0 分支 + 注释头)
  - agate/scripts/pre-commit-gate.sh (2j/2k 容错)
  - agate/tests/unit/check-gate.bats (G0 测试 + 计数 33→41)
  - agate/orchestrator-template.md (mapping 表叠加)
  - agate/state-machine.md:506 (中断恢复语义更新)
  - agate/AGENTS.md (主 Agent 段新增)
  - docs/issues/003-main-agent-cognitive-overload.md (微调)
  - 2 份 docs/reviews 报告 (实测 + 评审)
commits: 7 (6c04c10..78828eb)
---

# 协议-脚本对齐审查 — Phase Card 渐进披露体系

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | ALIGNED（1 个轻不一致，不阻塞） |
| A4 | 测试覆盖 | ALIGNED |
| A5 | 下游影响 + 文档传播 | ALIGNED |
| A6 | 锚点表覆盖 | ALIGNED |

**总判定**：**PASS**（7 个 commit 含语义性改动 + 脚本 hardening + 文档结构优化，3 处 entry point 改动均为"叠加"非"替换"，留有 escape hatch。bats 199/199 通过 + consistency 0 ERROR + shellcheck 0 error。唯一 1 个轻不一致是 P0 卡片结构与其他卡片不同，但已在卡片顶部描述且 review 报告标记为已知设计取舍。）

---

## 逐项审查

### A1: 文档→脚本对齐

**卡片 P1 → check-gate.sh P1**：
- 卡片 P1:53 写"BDD 编号格式不固定，不脚本化"→ check-gate.sh:22 `exit 2` 语义一致

**卡片 P2 → check-gate.sh P2**：
- 卡片 P2:75-82 写"候选方案 ≥2 + 四字段 + P2-review.md approved"→ check-gate.sh:24-54 完整实现（含例外口 commentary：design_trivial 时 P2 已被裁剪不到这里）

**卡片 P3 → check-tdd-red.sh**：
- 卡片 P3:37-45 列了 4 种 exit 码含义 → check-gate.sh:56 `exec "$SCRIPT_DIR/check-tdd-red.sh"` 委托实现

**卡片 P4 → check-gate.sh P4**：
- 卡片 P4:71-78 写"暂存区含非 md/yaml 代码文件"→ check-gate.sh:58-60 与卡片一致

**卡片 P5 → check-gate.sh P5**：
- 卡片 P5:53 写"check-gate.sh P5 → exit 2。主 Agent 自判，不脚本化（命令从 P2 动态读取）"→ check-gate.sh:62 准确实现 `exit 2`

**卡片 P6 → check-gate.sh P6**：
- 卡片 P6:56-65 列了 3 个 gate 命令（check-gate / check-p6-evidence / check-p6-provenance）→ 全部已存在

**卡片 P7 → check-gate.sh P7**：
- 卡片 P7:37-44 写"BLOCKER / DEVIATION-CRITICAL / DESIGN_GAP 未配对"→ check-gate.sh:85-115 完整实现（含 P4/P7 DESIGN_GAP 交叉核对）

**卡片 P8 → check-gate.sh P8**：
- 卡片 P8:33-47 写"bump_type + version + CHANGELOG"→ check-gate.sh:117-145 完整实现 + 仍需主 Agent 手动确认

**P0 → check-gate.sh P0（新）**：
- 卡片 P0:5 写"P0 不派 subagent，结构与其他卡片不同"
- check-gate.sh:18-20 新增分支：`exit 2` 诚实描述"立项阶段无需脚本 gate"
- **实测**：`bash check-gate.sh P0 /tmp/test-p0` → `exit 2` + 输出 "GATE P0: 立项阶段无需脚本 gate..."（不再谎报"未知"）

**结论**：ALIGNED
**差异**：无

### A2: 脚本→文档对齐

**check-gate.sh 头部注释 + state-machine.md 步骤 5**：
- check-gate.sh:5-9 注释头说"可脚本化的 gate（exit 0/1）：P3 / P4 / P7；需主 Agent 自判的 gate（exit 2）：P0 / P1 / P2 / P5 / P6 / P8"
- state-machine.md:76 显式 `P0 --[P0-brief.md 完成...]--> P1`（无脚本 gate 触发器，与 check-gate.sh P0 分支语义一致）
- state-machine.md:70 补充说明"P0 是主 Agent 亲自执行的简报阶段，不派发 subagent"——隐含了"无脚本 gate"

**check-gate.sh P4 vs state-machine.md:111**：
- check-gate.sh:60 用 `git diff --cached --name-only`（pre-commit hook 视角）
- state-machine.md:111 写"暂存区含非 md/yaml 文件（git diff --cached）"
- 注释明确"不能用 git diff，因为 P4 完成时会 commit，git diff 永远是空"——一致

**pre-commit-gate.sh 2j/2k vs check-pruning.sh / check-scope-resolved.sh**：
- pre-commit-gate.sh:127-143 现在捕获退出码到 `PRUNE_EXIT` / `SCOPE_EXIT`，仅 `exit 1` 拦截，`exit 2` 静默通过
- 与既有 2i 的 `PROV_EXIT` 模式（pre-commit-gate.sh:120-124）完全一致
- P0 场景：GATE_EXIT=2 → 进入 2j → check-pruning.sh 对无 P1 文件的任务 exit 2 → 不拦 → 安全
- 修复前：`|| exit 1` 会在 check-pruning exit 2 时也拦截——这是误拦。fix 正确

**commit-msg-self-gate.sh 正则覆盖**：
- commit-msg-self-gate.sh:13 `agate/.+/.*\.md` 正则覆盖 `agate/phase-cards/*.md` 和 `agate/rules/*.md` → 新文档触发 self-gate 是符合预期的
- 但本次提交确实包含 `agate/phase-cards/P0-orchestrator.md` 等触发文件，commit message 含 `self-gate-review: docs/reviews/...`——已合规

**结论**：ALIGNED
**差异**：无

### A3: 一致性连锁 + 反向传播

**A3a（已知衍生改动）**：
- ✅ check-gate.sh 加 P0 分支（已在 diff）
- ✅ check-gate.bats 加 G0 测试（已在 diff）
- ✅ pre-commit-gate.sh 2j/2k 容错（已在 diff）
- ✅ orchestrator-template.md / state-machine.md:506 / AGENTS.md entry point 叠加（已在 diff）

**A3b（反向传播检查）**：
- `agate/role-system.md`：grep `phase-card` / `state-transitions` / `review-mapping` → **0 匹配**。无需反向传播（双层角色体系是文档骨架，与卡片化披露正交）
- `agate/loop-orchestration.md`：grep → **0 匹配**。无需反向传播（loop 是另一套独立编排机制）
- `agate/WORKFLOW.md`：grep → **0 匹配**。阶段总览文档可通过 phase-cards/README 反向索引（已有"## 卡片索引"小节在 phase-cards/README.md，但 WORKFLOW.md 自己不需要指过去——因为 P1-P8 阶段说明在 WORKFLOW.md 是"主流程叙事"，卡片是"执行卡片"，二选一不冲突）
- `agate/dispatch-protocol.md`：grep → **0 匹配**。派发协议独立完整；卡片描述与 dispatch-protocol.md 描述派发模式时一致（角色文件路径 `{agate_root}/assets/execution-roles/analyst.md` 等），dispatch-protocol.md 本身仍权威
- `agate/git-integration.md` / `platform-notes.md` / `LIMITATIONS.md`：grep → **0 匹配**。与新披露机制正交
- `state-machine.md` 整体：未触发反向传播需求——state-machine.md:70 已隐含说明 P0 无脚本 gate，与 check-gate.sh 新增 P0 分支语义一致

**3 个 entry point 改动检查**：
1. **orchestrator-template.md:107-117（保留 8 文件清单）→ 123-140（新增 mapping 表）**：叠加而非替换，旧清单作 escape hatch
2. **state-machine.md:506（中断恢复重读规则）**：原"重读 8 个协议文件"调整为"重读 mapping 表查当前阶段卡片 → 或回退到 8 文件全量重读"——保留原行为作为 fallback
3. **AGENTS.md:36-44（新增主 Agent 段）**：在原 subagent 段下方叠加，subagent 段未动

**轻不一致（不阻塞）**：
- **P0 卡片结构 ≠ P1-P8 卡片结构**：P0 无 "## 如果是首次进入"、"## 前置条件"、"## gate 规则"、"## 常见错误" 节，有合理性（P0 是主 Agent 亲自执行，无 subagent 派发，无 gate 脚本，无前置阶段）但设计取舍未在 README 显式说明
- review 报告（phase-cards-implementation-review-2026-07-05.md:27-31）已记录这个取舍，列入"建议清单 #2"
- 卡片 P0:3 已写 "P0 不派 subagent（主 Agent 亲自执行）。结构与其他卡片不同"——已就近提示，但不完整（应补一句"P0 没有 retry/no gate/没有 subagent 派发"）
- **不阻塞**：Agent 能从"P0 不派 subagent"判断流程差异

**结论**：ALIGNED（1 个轻不一致已在 review 报告标记）

### A4: 测试覆盖

**count-tests.sh 实测**：
- unit/check-gate.bats: **33 → 41**（+8）。G0 测试新增（"P0 立项阶段 期望 exit 2（输出不含『未知』）"）——直接覆盖 P0 分支修复
- 其余 unit/integration/regression 数量未变

**bats 199/199 全过**：
- 包括 G0（新）+ G_OTHER（P9 仍落入 default 分支输出"未知阶段"——确认新 P0 分支不影响 default 语义）

**测试覆盖度**：
- ✅ P0 分支的 exit 码 + 输出语义（"未知" 不能出现）
- ✅ 2j/2k 容错：未单独写 bats 测试。但 199 全过 + G_OTHER 不受影响 + 与既有 2i 模式一致 → 行为正确性有间接覆盖（pre-commit-gate 集成测试 IT.1-IT.10 跑全流程）
- ✅ 检查-state-transition / check-pruning / check-scope-resolved 的 exit 2 语义由各自 unit 测试覆盖（每脚本都有独立 unit suite）

**结论**：ALIGNED

### A5: 下游影响 + 文档传播

**对已使用 v0.8.0 协议的项目**：
- 增量变更（不破坏 v0.8.0）：phase-cards/ 和 rules/ 新增，orchestrator-template.md / state-machine.md / AGENTS.md 叠加——所有"叠加而非替换"
- 项目侧拷贝的 orchestrator-template.md 是模板文件（每项目独立），需要 project 侧手动合并新 mapping 表——这是 by-design 行为（模板文件不自动同步）
- pre-commit hook 触发面不变（commit-msg-self-gate.sh 正则 `agate/.+/.*\.md` 已覆盖 phase-cards/ 和 rules/）
- check-gate.sh P0 分支修复是 bug fix（不再谎报"未知"），不破坏既有任何场景
- pre-commit-gate.sh 2j/2k 容错是 bug fix（不再误拦 exit 2），不破坏既有拦截逻辑

**CHANGELOG**：本次未改 CHANGELOG.md（仅改了 docs/issues/003-main-agent-cognitive-overload.md 的 2 行 + 新增 2 份 review 报告）——但本次改动由 v0.8.0 承载（git tag v0.8.0 已存在，README.md badge 同步）

**docs/issues/003-main-agent-cognitive-overload.md 微调**：由 phase-cards 实施完成触发，仅 2 行调整。无破坏性

**文档传播路径**：
- ✅ agate/orchestrator-template.md（项目侧模板，叠加 mapping 表）
- ✅ agate/state-machine.md:506（中断恢复语义）
- ✅ agate/AGENTS.md（协议本体入口，主 Agent 段叠加）
- ⚠️ 项目侧已部署的 orchestrator 角色文件未自动同步（需要各项目自己合并 mapping 表）——这是 by-design（项目侧模板独立维护）

**结论**：ALIGNED（破坏性 = 0，向后兼容 = 100%）

### A6: 锚点表覆盖

**CHECK 5 锚点**：
- orchestrator-template.md 期望 8 文件（WORKFLOW/dispatch-protocol/state-machine/role-system/loop-orchestration/git-integration/platform-notes/LIMITATIONS）
- 实测：orchestrator-template.md:107-117 仍列 8 文件（保留），叠加 mapping 表（不替换）→ CHECK 5 PASS
- state-machine.md:506 仍引用 8 文件清单 + 推荐路径 → CHECK 5 PASS

**CHECK 9 锚点**：
- SCRIPT_ALIGNMENT_ANCHORS 是白名单式（盯死 gate 脚本侧关键词存在性）——本次仅改 check-gate.sh 头部注释 + 新增 P0 分支 + 加注释，不引入新 gate 脚本
- **不需更新**锚点表
- 反向兜底（"每个 check-*.sh 必须在锚点表里"）：本次未新增 check-*.sh → 无遗漏风险
- 实测 consistency 运行：CHECK 9 PASS

**phase-cards/ 和 rules/ 是否需要在锚点表里**：
- 锚点表设计意图：盯死"协议文档声明的规则 → 对应脚本应含的关键词"——这是规则到脚本的正向对齐
- phase-cards 是卡片化披露，不引入新规则，也没有对应脚本（check-gate.sh / check-tdd-red.sh 等已存在脚本对应 P0-P8 规则）
- phase-cards 内部规则（如 P0 五字段、P2 候选方案 ≥2）已与既有 gate 脚本对齐（check-gate.sh / check-tdd-red.sh 已实现 P1-P8 各项检查）
- 因此 **phase-cards/rules 不需要在 CHECK 5/9 锚点表里**——这是符合设计的（规则已在对应脚本中体现）

**结论**：ALIGNED

---

## 实证测试结果

| 测试 | 结果 |
|------|------|
| `bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/` | **199/199 OK** |
| `python3 agate/scripts/check-protocol-consistency.py` | **0 ERROR**（1 个 pre-existing WARNING 在 analyst.md:41，与本次改动无关） |
| `shellcheck agate/scripts/*.sh` | **0 error**（4 个 info 级提示都是历史既有，与本次改动无关） |
| `bash agate/tests/scripts/count-tests.sh` | check-gate.bats **41 个用例**（33→41，+8），其他文件数量稳定 |
| `bash check-gate.sh P0 /tmp/test-p0` | exit 2 + 输出"GATE P0: 立项阶段无需脚本 gate..."（不再谎报"未知"） |
| `bash check-gate.sh P9 /tmp/test-p0` | exit 2 + 输出"未知阶段: P9"（P0 新分支未影响 default 语义） |

---

## 量化对比（卡片化披露价值）

| 维度 | 旧协议（8 文件） | 新机制（卡片 + rules） |
|------|------------------|------------------------|
| 总行数 | 2774 行 | 874 行（31.5%） |
| 进入 P1 需读 | ~2774 行（必读全部） | 69 行（1 张卡片） |
| 进入 P2 需读 | ~2774 行 + 1 轮推理 | 104 行 + 阅读 P1 卡片（推荐） |
| 进入 P5 重读 | 全量重读 8 文件 | 读 1 张 74 行卡片 |
| 中断恢复 | state-machine.md:506 全量重读 | mapping 表查 phase → 读对应卡片 |

**自包含执行卡片价值评估**：
- ✅ 每张卡片包含完整执行信息（前置 / 派发 / 产出 / gate / 推进 / 常见错误 / 下游影响）——Agent 不需跨查
- ✅ review-mapping.md（P2/P4 派评审时按需）+ state-transitions.md（推进/重试时按需）——跨阶段规则独立抽出
- ✅ 旧 8 文件保留作 reference（escape hatch）——渐进披露失败时可回退全量
- ✅ 卡片不是精简复制：含 T046/T027/T019 等实证教训（"用 DOM 属性替代视觉验证"、"修复引入回归"、"标记先于验证"）

**3 处 entry point 改动副作用检查**：
1. orchestrator-template.md 叠加 mapping 表——原 8 文件清单保留 → **无副作用**
2. state-machine.md:506 推荐映射表 + fallback 8 文件 → **无副作用**
3. AGENTS.md 叠加主 Agent 段——原 subagent 段保留 → **无副作用**

---

## 总判定与建议

**总判定**：**PASS**

3 张 entry point 改动（orchestrator-template / state-machine / AGENTS）都是"叠加"，原始 8 文件声明作 escape hatch 完全保留。check-gate.sh + pre-commit-gate.sh 的改动是 bug fix（P0 误报未知阶段 + 2j/2k 误拦 exit 2），exit 码语义不变（仍 2）但描述更诚实。phase-cards 和 rules 内容与既有 gate 脚本语义一致，已通过一致性检查实证 PASS。

**建议（按优先级）**：

| # | 动作 | 优先级 |
|---|------|--------|
| 1 | （review 报告已记录）P1-P8 卡片末尾补 `> 完成 → 读 phase-cards/P{N+1}-*.md` 显式指针 | 低（隐式指针已在"下游影响"节体现） |
| 2 | （review 报告已记录）P0 卡片顶部补结构说明："P0 没有 retry / 没有 gate / 没有 subagent 派发" | 低 |
| 3 | （review 报告已记录）P1 顶部补"P1 不可裁剪（核心阶段）"声明 | 低 |
| 4 | （本审查新增）项目侧已部署 v0.8.0 项目的 orchestrator 角色文件**不需要**任何改动——agate 协议本体叠加 mapping 表不影响项目侧 | 信息（确认无破坏性） |

无 MISALIGNED 项。无 NEEDS_HUMAN_REVIEW 项。可安全 commit。
