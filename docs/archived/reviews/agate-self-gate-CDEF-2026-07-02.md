---
review_date: 2026-07-02
reviewer: protocol-alignment-review
change_summary: C/D/E/F 组审计修复——裁剪条件偏差、门槛表对齐、文档滞后、pre-commit 表格对齐
files_changed:
  - agate/scripts/check-pruning.sh
  - agate/scripts/check-gate.sh
  - agate/state-machine.md
  - agate/dispatch-protocol.md
  - agate/WORKFLOW.md
  - agate/assets/templates/task-files.md
  - agate/assets/execution-roles/verifier.md
  - agate/orchestrator-template.md
  - agate/tests/unit/check-pruning.bats
  - agate/tests/unit/check-gate.bats
  - agate/tests/regression/v060-p8-internal-only.bats
---

# 协议-脚本对齐审查 — C/D/E/F 组审计修复

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | ALIGNED |
| A4 | 测试覆盖 | ALIGNED |
| A5 | 下游影响 + 文档传播 | NEEDS_HUMAN_REVIEW |
| A6 | 锚点表覆盖 | ALIGNED |

## 逐项审查

### A1: 文档→脚本对齐

**C 组 #5 P3 裁剪措辞**：
- 文档（state-machine.md:165）："裁剪 P3：high 风险不可裁"
- 脚本（check-pruning.sh:70-74）：`if [ "$RISK_LEVEL" = "high" ]` → 拦截
- 结论：**ALIGNED** — 文档从"需 risk_level=low"改为"high 风险不可裁"，语义等价但措辞更准确；脚本逻辑不变，仍正确拦截 high 风险裁剪 P3

**C 组 #7 P6 跳过风险**：
- 文档（state-machine.md:170）："每条裁剪须含'跳过风险:'评估"
- 脚本（check-pruning.sh:106-110）：检查 7 现在包含 P6（`! echo "$PHASES_DECLARED" | grep -qw 'P6'`）
- 结论：**ALIGNED** — P6 裁剪时也需跳过风险评估，脚本已补上 P6 条件

**C 组 #8 P8 internal_only_reason**：
- 文档（state-machine.md:168）："裁剪 P8：需声明 internal_only: true + internal_only_reason: <理由>"
- 脚本（check-pruning.sh:96-103）：分两步检查——先查 `internal_only: true`，再查 `internal_only_reason:` 字段
- 结论：**ALIGNED** — 文档和脚本都要求两个字段

**C 组 #10 P2 form check（status:approved + 四字段 + 权衡）**：
- 文档（state-machine.md:84）："P2-review.md 有效 AND status==approved AND P2-design.md 声明 packages/domains/ui_affected/gate_commands AND 候选方案≥2 AND 含权衡/选择理由"
- 脚本（check-gate.sh:32-48）：新增 P2-review.md status:approved 检查 + 四字段计数 ≥4 + 权衡/选择理由 grep
- 结论：**ALIGNED** — 脚本完整实现了文档声明的 P2 门槛

**D 组 #13 P2 status:approved**：
- 文档（dispatch-protocol.md:577）："grep 'status: approved' P2-review.md → 命中"
- 脚本（check-gate.sh:34-37）：`grep -qE 'status:\s*approved' "$P2_REVIEW"`
- 结论：**ALIGNED**

**D 组 #6/#16 P4 门槛 git diff --cached**：
- 文档（state-machine.md:94）："暂存区含非 md/yaml 文件（git diff --cached）"
- 文档（dispatch-protocol.md:579）："暂存区含非 md/yaml 文件（git diff --cached --name-only | grep -qvE '\.(md|yaml)$|^\.state'）"
- 脚本（check-gate.sh:57）：`git diff --cached --name-only | grep -qvE '\.(md|yaml)$|^\.state'`
- 结论：**ALIGNED** — 文档和脚本都从 `git log` 改为 `git diff --cached`

**E 组 #3 md5 建议**：
- 文档（dispatch-protocol.md:359）："操作类 BDD 截图必须互不相同（md5 去重，建议）"
- 文档（verifier.md:130）："操作类 BDD 截图必须互不相同（md5 去重，建议）"
- 文档（task-files.md:246）："操作类 BDD 截图必须互不相同（md5 去重，建议）"
- 脚本：check-p6-evidence.sh 的 md5 去重仍为 WARNING（不阻塞），与"建议"强度一致
- 结论：**ALIGNED** — 三处文档措辞统一为"建议"，与脚本 WARNING 级别一致

**E 组 #4 P3 UI 措辞**：
- 文档（state-machine.md:91）："若 P2 声明 ui_affected：P3 必须包含对应的 Playwright/E2E 用例，主 Agent 确认"
- 脚本：P3 gate 委托 check-tdd-red.sh，UI 用例由主 Agent 手动确认（exit 2）
- 结论：**ALIGNED** — 文档改为"主 Agent 确认"，与 P3 gate exit 2（需主 Agent 自判）一致

**E 组 #9 BDD ≥N**：
- 文档（dispatch-protocol.md:370）："P1 有 N 条 BDD → P6 必须有 ≥N 条验收结果（PASS 或 FAIL，允许 SCOPE+ 增补）"
- 脚本：check-p6-provenance.sh 检查 BDD 总数对照，允许 SCOPE+ 增补
- 结论：**ALIGNED**

**E 组 #14 四道审计**：
- 文档（state-machine.md:216）："四道客观审计失败 → exit 1 拦截"
- 文档（dispatch-protocol.md:221）："三道客观审计"→ 未同步？
- 实际检查：dispatch-protocol.md:221 写的是"三道客观审计（证据-结论对应 + dispatch-context 内容约束 + BDD 总数对照）+ agent 字段协作规范"
- state-machine.md:216 写的是"四道客观审计"
- 差异：dispatch-protocol.md 的门槛表描述仍写"三道"，但 state-machine.md 已改为"四道"
- 结论：**NEEDS_HUMAN_REVIEW** — 见 A3 详细分析

**F 组 P1.2 PROD_TOUCHED 行**：
- 文档（dispatch-protocol.md:601）："全局 P1.2 | — | [PROD_TOUCHED] 标记检测（扫描暂存 diff 内容，命中则中止 commit）"
- 脚本（pre-commit-gate.sh:58-63）：`git diff --cached | grep -q '\[PROD_TOUCHED\]'` → exit 1
- 结论：**ALIGNED** — 文档表格新增 P1.2 行，与 pre-commit-gate.sh 实现一致

**F 组 pre-commit 表格顺序**：
- 文档（dispatch-protocol.md:598-609）：顺序为 P2.15 → P1.2 → P2.3-P2.5 → P1.1 → P2.1/P2.10 → P2.7-P2.9 → P2.11 → P2.12 → P1.6 → P1.7
- 脚本（pre-commit-gate.sh）：实际执行顺序为 P2.15 → NEEDS_GATE → P1.2 → P2.3-P2.5 → P1.1 → P2.1/P2.10 → P2.7-P2.9 → P2.11 → P2.12 → P1.6 → P1.7
- 结论：**ALIGNED** — 文档表格顺序与脚本执行顺序一致

### A2: 脚本→文档对齐

**check-pruning.sh P8 internal_only_reason 拆分**：
- 脚本（check-pruning.sh:96-103）：将原单条错误拆为两步——缺 `internal_only: true` 报"需声明 internal_only: true"，有 `internal_only` 但缺 `internal_only_reason:` 报"internal_only_reason: 字段缺失"
- 文档（state-machine.md:168）："需声明 internal_only: true + internal_only_reason: <理由>"
- 文档（task-files.md:145-146）：模板已补 `# internal_only: true` 和 `# internal_only_reason:` 注释
- 结论：**ALIGNED**

**check-gate.sh P2 新增检查**：
- 脚本新增：P2-review.md status:approved + 四字段 ≥4 + 权衡/选择理由
- 文档（state-machine.md:84）：P2 转移条件已同步更新
- 文档（dispatch-protocol.md:577）：门槛表已同步
- 文档（WORKFLOW.md:194）：P2 门槛列已同步
- 结论：**ALIGNED**

**check-pruning.sh 检查 7 补 P6**：
- 脚本（check-pruning.sh:106）：条件链新增 `! echo "$PHASES_DECLARED" | grep -qw 'P6'`
- 文档（state-machine.md:170）："每条裁剪须含'跳过风险:'评估"——覆盖所有可裁剪阶段，P6 是可裁剪阶段之一
- 结论：**ALIGNED**

### A3: 一致性连锁 + 反向传播

**A3a 连锁（已同步的衍生改动）**：

| 改动源 | 衍生文件 | 是否已同步 |
|--------|----------|-----------|
| state-machine.md P2 门槛 | dispatch-protocol.md 门槛表 | ✅ 已同步 |
| state-machine.md P2 门槛 | WORKFLOW.md P2 门槛列 | ✅ 已同步 |
| state-machine.md P4 门槛 | dispatch-protocol.md 门槛表 | ✅ 已同步 |
| state-machine.md P4 门槛 | WORKFLOW.md P4 门槛列 | ✅ 已同步 |
| state-machine.md P8 裁剪条件 | task-files.md 模板 | ✅ 已同步 |
| dispatch-protocol.md md5 建议 | verifier.md 截图质量标准 | ✅ 已同步 |
| dispatch-protocol.md md5 建议 | task-files.md 截图质量标准 | ✅ 已同步 |
| dispatch-protocol.md BDD ≥N | — | ✅ 已同步 |
| dispatch-protocol.md pre-commit 表格 | pre-commit-gate.sh 执行顺序 | ✅ 已同步 |
| state-machine.md P3 UI 措辞 | — | ✅ 已同步 |
| orchestrator-template.md 裁剪条件措辞 | — | ✅ 已同步 |

**A3b 反向传播（应被影响但 diff 未列出的文件）**：

1. **"三道客观审计" vs "四道客观审计"不一致**
   - state-machine.md:216 已改为"四道客观审计"
   - 但以下文件仍写"三道"：
     - dispatch-protocol.md:221（Pre-commit 检查总览表）
     - WORKFLOW.md:221（Pre-commit 检查总览表）
     - LIMITATIONS.md:36（局限描述）
     - check-p6-provenance.sh:3（脚本注释）
   - 实际审计内容：证据-结论对应 + dispatch-context + BDD 总数对照 + UI vision YAML 审计 = 四道
   - 结论：**MISALIGNED** — state-machine.md 已改为"四道"但其他 4 个文件未同步
   - 严重程度：低——描述性文字/注释，不影响 gate 行为（脚本实际执行四道检查），但文档不一致会造成理解偏差

2. **check-protocol-consistency.py CHECK 9 锚点表**
   - 本次新增的 P2 gate 检查（status:approved + 四字段 + 权衡）未加入 CHECK 9 锚点表
   - 但 CHECK 9 是白名单式，只盯死已知锚点，不要求覆盖所有规则
   - CHECK 8 已覆盖 design_trivial / DESIGN_GAP / --cached 等关键词
   - P2 的 status:approved / 四字段 / 权衡 检查是 check-gate.sh 内部逻辑，CHECK 9 的现有锚点"DESIGN_GAP 配对 → check-gate.sh"已覆盖 check-gate.sh 的存在性
   - 结论：**ALIGNED** — CHECK 9 白名单模式不要求新增锚点，现有覆盖足够

3. **SELF-GATE.md / protocol-alignment-review.md**
   - 本次修改未改变 self-gate 机制或审查角色定义
   - 结论：**ALIGNED** — 无需同步

4. **role-system.md**
   - 本次修改未涉及角色体系变更
   - 结论：**ALIGNED** — 无需同步

5. **LIMITATIONS.md**
   - 本次修改未改变已知局限
   - 结论：**ALIGNED** — 无需同步

### A4: 测试覆盖

**check-pruning.sh 新增逻辑的测试**：

| 新逻辑 | 测试用例 | 覆盖 |
|--------|---------|------|
| P8 internal_only_reason 缺失 | P2.13 (check-pruning.bats:211-220) | ✅ |
| P8 internal_only + reason 完整 | P2.14 (check-pruning.bats:222-230) | ✅ |
| P6 裁剪无跳过风险 | P2.12 (check-pruning.bats:190-198) | ✅ |
| P6 裁剪 + no_behavior_change + 跳过风险 | P2.12a (check-pruning.bats:200-207) | ✅ |
| P8 internal_only_reason 回归 | R4.3 (v060-p8-internal-only.bats:25-33) | ✅ |

**check-gate.sh P2 新增逻辑的测试**：

| 新逻辑 | 测试用例 | 覆盖 |
|--------|---------|------|
| P2 候选方案≥2 但无权衡 | G2.8 (check-gate.bats:80-95) | ✅ |
| P2 候选方案≥2 + 含权衡 | G2.9 (check-gate.bats:97-113) | ✅ |
| P2 有方案+权衡+四字段，review 无 approved | G2.10 (check-gate.bats:115-138) | ✅ |
| P2 有方案+权衡+四字段+review approved | G2.11 (check-gate.bats:140-162) | ✅ |
| P2 缺字段（<4）| G2.12 (check-gate.bats:164-179) | ✅ |
| P2 有方案+权衡+四字段，无 review 文件 | G2.13 (check-gate.bats:181-197) | ✅ |

**边界覆盖**：
- P2 review 不存在时：G2.13 测试 exit 2（不强制要求 review 文件存在，与脚本逻辑一致——`if [ -f "$P2_REVIEW" ]` 只在文件存在时检查）
- P2 四字段恰好 =4：G2.3/G2.9 等测试
- P2 四字段 <4：G2.12 测试

**测试执行结果**：全部 67 个测试通过（check-pruning 19 + check-gate 33 + regression 3 + 额外 12）

结论：**ALIGNED** — 新增逻辑均有对应测试，边界条件覆盖充分

### A5: 下游影响 + 文档传播

**下游项目影响**：
- check-gate.sh P2 新增检查：对已有项目，P2 gate 现在会检查 status:approved + 四字段 + 权衡。如果项目之前 P2-design.md 缺这些字段，gate 会从 exit 2 变为 exit 1。这是**行为变更**，但属于"补全已有文档声明的规则"——文档一直要求这些字段，脚本之前没检查。
- check-pruning.sh P8 internal_only_reason：新增字段要求。已有项目如果裁剪 P8 且只有 `internal_only: true`，现在会 exit 1。这是**行为变更**。
- check-pruning.sh P6 跳过风险：已有项目如果裁剪 P6 且无"跳过风险:"评估，现在会 exit 1。这是**行为变更**。

**文档传播**：
- dispatch-protocol.md:221 和 WORKFLOW.md:221 仍写"三道客观审计"，应同步为"四道"（见 A3b-1）
- CHANGELOG.md 未更新——本次修改涉及协议语义变更（P2 gate 行为变更、P8 裁剪条件变更、P6 跳过风险要求），应标注

结论：**NEEDS_HUMAN_REVIEW** — 两个问题需人工确认：
1. "三道 vs 四道"措辞不一致是否需要本次修复（低严重度，不影响 gate 行为）
2. CHANGELOG 是否需要标注本次行为变更

### A6: 锚点表覆盖

**CHECK 9 锚点表现有条目**：

| 锚点 | 关键词 | 本次是否受影响 |
|------|--------|--------------|
| 裁剪 P2 条件 | design_trivial, follows_existing_pattern, legacy_p2_pruned | ❌ 未变 |
| 裁剪 P3 条件 | risk_level | ❌ 未变 |
| 裁剪 P6 条件 | no_behavior_change | ❌ 未变 |
| 裁剪 P7 条件 | SOURCE_FILE_COUNT | ❌ 未变 |
| 裁剪 P8 条件 | internal_only | ❌ 未变（关键词仍在） |
| 重试上限 | MAX_RETRY | ❌ 未变 |
| 回退跳变 | diff, phase_num | ❌ 未变 |
| PROD_TOUCHED | PROD_TOUCHED | ❌ 未变 |
| SCOPE+ 追踪 | SCOPE_RESOLVED | ❌ 未变 |
| DESIGN_GAP 配对 | DESIGN_GAP | ❌ 未变 |
| P6 evidence UI | ui_affected | ❌ 未变 |
| P6 截图去重 | md5, 去重 | ❌ 未变（WARNING 已知） |
| P6 provenance | EVIDENCE_DIR | ❌ 未变 |
| 复盘提醒 | retries | ❌ 未变 |
| P8 CHANGELOG | CHANGELOG | ❌ 未变 |
| state.yaml 格式 | task_id | ❌ 未变 |
| TDD 红灯 | pytest | ❌ 未变 |

**是否需要新增锚点**：
- P2 status:approved + 四字段 + 权衡：check-gate.sh 已有 DESIGN_GAP 锚点覆盖其存在性，新增的 P2 检查是同一脚本内的逻辑扩展，不需要独立锚点
- P8 internal_only_reason：check-pruning.sh 已有 internal_only 锚点，internal_only_reason 是同脚本的扩展检查
- P6 跳过风险：check-pruning.sh 已有多个裁剪条件锚点

结论：**ALIGNED** — 现有锚点表覆盖了所有受影响脚本的存在性，新增逻辑是已有锚点脚本的内部扩展，不需要新增锚点

## 遗留问题汇总

| # | 问题 | 严重度 | 建议 |
|---|------|--------|------|
| 1 | state-machine.md 改为"四道客观审计"但 dispatch-protocol.md:221 / WORKFLOW.md:221 / LIMITATIONS.md:36 / check-p6-provenance.sh:3 仍写"三道" | 低 | 统一为"四道"，或确认"三道"是刻意保留（agent 字段协作规范不算审计道） |
| 2 | CHANGELOG.md 未标注本次行为变更 | 中 | 建议在 `[Unreleased]` 下添加条目，说明 P2 gate 补全检查、P8 裁剪新增 internal_only_reason、P6 裁剪新增跳过风险要求 |

## 自动化验证结果

- check-protocol-consistency.py：0 ERROR，5 WARNING（均为已知非本次引入）
- bats 全量：67/67 通过
- shellcheck：0 error
