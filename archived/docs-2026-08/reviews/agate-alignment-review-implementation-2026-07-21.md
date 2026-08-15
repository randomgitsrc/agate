---
review_date: 2026-07-21
reviewer: protocol-alignment-review
change_summary: T060 retro bugfixes (3 bugs + P5 WARNING) + multi-platform CI support (self-gate fixes A/B/C + M3.1/M3.2/M4.1/M4.2/M5.1/M1.3a/M1.3b) — combined batch implementation review
files_changed:
  - agate/scripts/agate-inject-card.sh
  - agate/scripts/check-scope-resolved.sh
  - agate/scripts/check-changelog.sh
  - agate/scripts/check-gate.sh
  - agate/scripts/commit-msg-self-gate.sh
  - agate/scripts/check-protocol-consistency.py
  - agate/scripts/ci-gate-backstop.py
  - agate/scripts/install-hook.sh
  - agate/scripts/check-p6-evidence.sh
  - agate/scripts/check-p6-provenance.sh
  - agate/assets/templates/dispatch-prompt.md
  - agate/LIMITATIONS.md
  - agate/WORKFLOW.md
  - agate/state-machine.md
  - agate/dispatch-protocol.md
  - agate/platform-notes.md
  - agate/git-integration.md
  - agate/orchestrator-template.md
  - agate/scripts/README.md
  - SELF-GATE.md
  - AGENTS.md
  - CHANGELOG.md
---

# 协议-脚本对齐审查 — 实施后审查

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | MISALIGNED |
| A3 | 一致性连锁 + 反向传播 | MISALIGNED |
| A4 | 测试覆盖 | MISALIGNED |
| A5 | 下游影响 + 文档传播 | MISALIGNED |
| A6 | 锚点表覆盖 | MISALIGNED |
| A7 | 设计原则一致性 | ALIGNED |

**MISALIGNED 计数：5**  
**NEEDS_HUMAN_REVIEW 计数：0**  
**整体判决：NEEDS_FIXES**

---

## 逐项审查

### A1: 文档→脚本对齐

逐项核对计划声明 vs 实际实现：

**Bug 1 — agate-inject-card.sh 占位符检测（plan:42-97）**

计划要求：`re.sub()` 后检查 `new_text == text`，未变化则 `sys.exit(1)` + 输出"未找到...占位符"错误。
实现（`agate-inject-card.sh:52-54`）：完全一致。加入 `import sys`（line 43），`new_text == text` 检测（line 52），`sys.exit(1)`（line 54）。
**结论：ALIGNED**

**Bug 2 — SCOPE+ 排除 dispatch-context（plan:101-151）**

计划要求：在 `check-scope-resolved.sh` 循环中跳过文件名含 `dispatch-context` 的文件。
实现（`check-scope-resolved.sh:18-19`）：`basename "$f" | grep -q 'dispatch-context' && continue`，与计划 diff 完全一致。
**结论：ALIGNED**

**Bug 3 — check-changelog.sh 短前缀搜索（plan:155-248）**

计划要求：(1) 提取 `T\d+` 短前缀，(2) `grep -qE "(^|[^0-9])${TASK_ID_SHORT}( |:|$|,|-)"` 主匹配，(3) fallback `grep -qF "$TASK_ID"`。
实现（`check-changelog.sh:9-39`）：提取行（12-13）+ 主匹配行（32）+ fallback（36-37）与计划 diff 完全一致。
**结论：ALIGNED**

**Bug 4 — P5 全量测试 WARNING（plan:252-303）**

计划要求：在 `check-gate.sh` P5 分支 exit 2 之前，检查 `P2-design.md` 中 `^\s+- ` 命令数 > 1 时输出 WARNING 提示。
实现（`check-gate.sh:120-127`）：位置（exit 2 之前）、grep 模式、消息文本与计划一致。`grep -cE '^\s+- '` 匹配的粗糙度与计划声明一致。
**结论：ALIGNED**

**修复 A — commit-msg-self-gate.sh 正则（plan:76-89）**

计划要求：`agate/scripts/.*\.sh` → `agate/scripts/.*\.(sh|py)`，同步更新提示文字。
实现（`commit-msg-self-gate.sh:13`）：正则为 `agate/scripts/.*\.(sh|py)`；提示文字（line 30）含 `agate/scripts/*.py`。
**结论：ALIGNED**

**修复 B — check_anchor_coverage 扫描范围（plan:95-108）**

计划要求：在 `pre-commit-gate.sh` 显式追加后，再追加 `ci-gate-backstop.py`。
实现（`check-protocol-consistency.py:674-676`）：三行追加与计划 diff 完全一致。
**结论：ALIGNED**

**修复 C — CHECK 9 新增锚点（plan:110-141）**

计划要求：新增 4 条锚点（EXIT_CODE 文档侧、EXIT_CODE 脚本侧、CI 平台探测、AGATE_ALIGNMENT_REVIEW_THRESHOLD）。
实现（`check-protocol-consistency.py:586-606`）：4 条锚点全部存在，keywords 与 plan 一致。
**结论：ALIGNED**

**M3.1 — 像素方差检测（plan:295-359）**

计划要求：方差检测独立于文件大小分支，Pillow 缺失 WARNING + `AGATE_SKIP_IMAGE_CHECKS=1` 开关。用 `img.tobytes()`。
实现（`check-p6-evidence.sh:77-119`）：`AGATE_SKIP_IMAGE_CHECKS` 开关（77）、方差检测独立于文件大小分支（92-113）、`SKIP_NO_PILLOW` 处理（107-109）、`img.tobytes()` 替代 `img.getdata()`（line 100）。全部一致。
**结论：ALIGNED**

**M3.2 — average hash（plan:362-425）**

计划要求：md5 重复 exit 1（阻断），average hash 纯 Pillow 实现（WARNING 不阻断），不引入 imagehash。
实现（`check-p6-evidence.sh:128-170`）：md5 exit 1（136）、average hash 纯 Pillow 实现（139-157）、AHASH_DUPES WARNING（167）。与计划一致。
**结论：ALIGNED**

**M4.1/M4.2 — CI 平台探测 + provenance 纳入 backstop（plan:147-212）**

计划要求：`detect_ci_platform()` 检测顺序 Gitea→GitLab→GitHub，`get_pr_metadata()` 分平台适配，provenance 审计兜底在 main() return 0 之前。
实现（`ci-gate-backstop.py:28-53, 150-161`）：platform 探测函数（28-35）、get_pr_metadata（38-52）、provenance 重跑（150-161）与计划完全一致。
**结论：ALIGNED**

**M5.1 — pre-push hook（plan:253-286）**

计划要求：heredoc 生成 pre-push hook，`AGATE_ALIGNMENT_REVIEW_THRESHOLD:-20`，`exit 0`（不阻断），零 SHA 新分支跳过。
实现（`install-hook.sh:52-75`）：heredoc 内容与计划 diff 完全一致，阈值默认 20（line 56），零 SHA 检测（line 61），exit 0（line 72）。
**结论：ALIGNED**

**M1.3a — 日志格式约定（plan:428-443）**

计划要求：在 `dispatch-prompt.md` 的"自查≠gate"之后追加 EXIT_CODE 格式约定节。
实现（`dispatch-prompt.md:133-138`）：位置（P5/P6 派发追加内）、格式 `EXIT_CODE: <n>`、降级说明与计划一致。
**结论：ALIGNED**

**M1.3b — 日志一致性检测（plan:432-471）**

计划要求：在 check-p6-provenance.sh 审计 4 与"协作规范"之间插入"审计 5"，`EXIT_CODE=1 + PASS` → exit 1，缺尾行 → WARNING。
实现（`check-p6-provenance.sh:206-221`）：位置正确（审计 4 结束后、协作规范节前），`EXIT_CODE: [0-9]+` 正则（210）、矛盾检测（213-215）、缺尾行 WARNING（218）。全部一致。
**结论：ALIGNED**

**M1.1 — 正确未实现**

计划（plan:473-488）判定 M1.1 不值得实现（决定 3），实际代码中无 M1.1 痕迹——符合计划。
**结论：ALIGNED**

---

### A2: 脚本→文档对齐

检查脚本侧变更是否已同步到文档侧。

**check-p6-provenance.sh:3 写"五道客观审计" vs 文档仍写"四道"**

脚本注释已更新为"五道"（`check-p6-provenance.sh:3`）。但以下文档仍写"四道"：
- `LIMITATIONS.md:38` — `scripts/check-p6-provenance.sh` 四道客观审计
- `state-machine.md:223` — 四道客观审计失败 → exit 1 拦截
- `WORKFLOW.md:245` — 四道客观审计（证据-结论对应 + ...）

**差异**：审计 5（EXIT_CODE 一致性）新增后，审计从"四道"变为"五道"。脚本注释已更新，三处文档仍用旧计数。

**结论：MISALIGNED**  
**建议**：将上述三处"四道"改为"五道"。注意：LIMITATIONS.md 局限 3（line 38-43）的审计描述列表也需补上审计 5 条目。

**check-p6-evidence.sh 注释 vs scripts/README.md**

脚本注释（`check-p6-evidence.sh:5`）写"含像素方差检测（...）+ md5 去重（阻断）+ average hash 相似度（WARNING）"，scripts/README.md:15 已同步为"md5 逐字节去重（阻断）+ 像素方差/average hash 检测（WARNING）"。
**结论：ALIGNED**

**install-hook.sh 注释 vs scripts/README.md**

脚本注释（`install-hook.sh:2`）写"安装 pre-commit hook + commit-msg hook + pre-push hook"，scripts/README.md:33 已同步。
**结论：ALIGNED**

---

### A3: 一致性连锁 + 反向传播

**A3a — 连锁（已知衍生改动）：**

| 改动 | 应传播到 | 实际状态 |
|------|---------|----------|
| check-p6-provenance.sh 审计 4→5 | LIMITATIONS.md 局限 3（line 38）| **未更新（仍写"四道"）** |
| check-p6-provenance.sh 审计 4→5 | state-machine.md:223 | **未更新** |
| check-p6-provenance.sh 审计 4→5 | WORKFLOW.md:245 | **未更新** |
| ci-gate-backstop.py 新增 platform detection | platform-notes.md | ✅ 已更新 |
| ci-gate-backstop.py 新增 provenance 重跑 | LIMITATIONS.md 局限 8 | ✅ 已更新 |
| ci-gate-backstop.py 多平台 | WORKFLOW.md:255 | ✅ 已更新 |
| ci-gate-backstop.py 多平台 | state-machine.md:232 | ✅ 已更新 |
| ci-gate-backstop.py 多平台 | dispatch-protocol.md:828 | ✅ 已更新 |
| ci-gate-backstop.py 多平台 | git-integration.md:181 | ✅ 已更新 |
| ci-gate-backstop.py 多平台 | orchestrator-template.md:91 | ✅ 已更新 |
| ci-gate-backstop.py 多平台 | SELF-GATE.md | ✅ 已更新 |
| install-hook.sh pre-push 新增 | dispatch-protocol.md:826 | ✅ 已更新（含 Pre-push hook 节） |
| install-hook.sh pre-push 新增 | orchestrator-template.md:113 | ✅ 已更新 |
| install-hook.sh + pre-commit + commit-msg | dispatch-protocol.md:803 | ✅ 已更新 |
| dispatch-prompt.md EXIT_CODE 约定 | dispatch-protocol.md | 未找到专门的 EXIT_CODE 节，但 prompt 模板由 dispatch-prompt.md 直接提供 |
| M3.1/M3.2 截图检测 | dispatch-protocol.md:523-524 | ✅ 已更新 |
| M3.1/M3.2 截图检测 | state-machine.md:222 | ✅ 已更新 |
| M3.1/M3.2 截图检测 | WORKFLOW.md:244 | ✅ 已更新 |
| M3.1/M3.2 截图检测 | scripts/README.md:15 | ✅ 已更新 |
| Pillow 依赖 | LIMITATIONS.md 局限 6 | ✅ 已更新 |
| Pillow 依赖 | AGENTS.md | ✅ 已更新 |
| commit-msg-self-gate 正则 → \*.py | SELF-GATE.md (触发条件) | ✅ 已更新 |
| commit-msg-self-gate 正则 → \*.py | protocol-alignment-review.md (触发条件) | ✅ 已更新 |
| commit-msg-self-gate 正则 → \*.py | SELF-GATE.md 触发条件 | ✅ 已更新 |

**A3b — 反向传播（主动推断）：**

检查"改了 check-p6-provenance.sh 的审计计数（4→5）→ 哪些文件引用这个数字需要同步更新"：
- `agate/assets/execution-roles/verifier.md:91` — 写"check-p6-provenance.sh 客观行为审计"，不引用"四道"计数，**无需更新**。
- `agate/phase-cards/P6-acceptance.md:14,79` — 引用路径和用途但不引用审计道数，**无需更新**。
- `agate/scripts/README.md:16` — 写"五道 + EXIT_CODE 一致性 + 协作规范"，**已更新**。

**结论：MISALIGNED**（3 处"四道"未更新为"五道"）

---

### A4: 测试覆盖

**已有测试：**

| 测试文件 | 测试数 | 计划要求 | 状态 |
|---------|--------|---------|------|
| `unit/agate-inject-card.bats` | 8 测试 | Bug 1: 1 条新增 | ✅ 含"无占位符时 exit 1"测试（line 183） |
| `unit/check-scope-resolved.bats` | 7 测试 | Bug 2: 1 条新增 | ✅ 含"dispatch-context SCOPE+ 不触发"测试（line 77） |
| `unit/check-changelog.bats` | 8 测试 | Bug 3: 3 条新增 | ✅ 含 CL.6/CL.7/CL.8（lines 71/85/100） |
| `unit/check-gate.bats` | 70 测试 | Bug 4: 1 条新增 | ✅ 含"P5 WARNING"测试（line 363） |
| `unit/check-p6-provenance.bats` | 22 测试 | M1.3b: 3 条新增 | ✅ 从 19 → 22（含 PV.21/PV.22 等 EXIT_CODE 测试） |
| `unit/check-p6-evidence.bats` | 14 测试 | M3.1/M3.2: 4+ 条 | ✅ 含方差/average hash/md5 测试 |
| `integration/commit-msg-self-gate.bats` | 6 测试 | 修复 A: 4 条 | ✅ 含 .sh/.py 触发 + skip 测试 |

**缺失测试：**

| 测试文件 | 计划要求 | 状态 |
|---------|---------|------|
| `unit/ci-gate-backstop.bats` | B4: 3 条（detect_ci_platform 三场景） | **不存在** |
| `integration/pre-push-hook.bats` | B4: 3 条（大改动触发、新分支跳过、THRESHOLD 覆盖） | **不存在** |

**测试计数验证**：
- `count-tests.sh` 输出：**296 个测试用例**
- 预期（已知测试结果）：302 tests
- 缺失：6 tests（`ci-gate-backstop.bats` 3 条 + `pre-push-hook.bats` 3 条 = 6 matches the delta）

**结论：MISALIGNED**（2 个测试文件缺失：`ci-gate-backstop.bats` + `pre-push-hook.bats`，共 6 个测试用例）

---

### A5: 下游影响 + 文档传播

**破坏性变更标注：**

md5 重复从 WARNING（exit 2）升级为阻断（exit 1）— 这是破坏性变更，改变 gate 通过条件。
- 计划 B1 明确要求：CHANGELOG `[Unreleased]` 下加 `### BREAKING` 条目。
- 当前 CHANGELOG.md **无 `[Unreleased]` 节**，直接以 `## [0.15.0]` 开头。
- **结论：MISALIGNED**

**CHANGELOG 状态：**
- v0.15.0 已包含 T060 Bug 1-3 和 P5 WARNING（行 27）— 这些是已发布变更
- 多平台 CI（self-gate 修复 + M3/M4/M5/M1.3）— 这些变更在代码中但 CHANGELOG 无记录

**文档传播检查（应被影响的文档 vs 实际状态）：**

| 文档 | 应更新 | 实际 |
|------|--------|------|
| `LIMITATIONS.md` 局限 3:44 | provenance CI backstop 已重跑 | ✅ 已更新 |
| `LIMITATIONS.md` 局限 6:82-91 | Pillow 依赖 | ✅ 已更新 |
| `LIMITATIONS.md` 局限 8:104-113 | 三平台支持 | ✅ 已更新 |
| `LIMITATIONS.md` 局限 3:38 | 审计 4→5 | **未更新（仍写"四道"）** |
| `WORKFLOW.md:244-245` | P6 evidence + provenance 描述 | ✅ 已更新（evidence），**未更新（provenance 仍写"四道"）** |
| `state-machine.md:222-223` | P6 evidence + provenance 描述 | ✅ 已更新（evidence），**未更新（provenance 仍写"四道"）** |
| `dispatch-protocol.md:523-524` | 截图质量标准 | ✅ 已更新 |
| `dispatch-protocol.md:803` | install-hook.sh 描述 | ✅ 已更新 |
| `dispatch-protocol.md:826` | pre-push hook 描述 | ✅ 已更新 |
| `dispatch-protocol.md:828` | CI backstop 多平台 | ✅ 已更新 |
| `platform-notes.md` | CI backstop 多平台 | ✅ 已更新 |
| `git-integration.md:181` | CI backstop | ✅ 已更新 |
| `orchestrator-template.md:91,113` | CI backstop + install-hook | ✅ 已更新 |
| `SELF-GATE.md` 触发条件 | `*.py` | ✅ 已更新 |
| `protocol-alignment-review.md` 触发条件 | `*.py` | ✅ 已更新 |
| `scripts/README.md` | install-hook + ci-backstop + evidence + provenance | ✅ 全部已更新 |
| `AGENTS.md` 依赖节 | Pillow | ✅ 已更新 |
| `CHANGELOG.md` | BREAKING md5 + 多平台 CI 新增 | **未更新** |
| `phase-cards/P5-verification.md:48-51` | 全量测试 WARNING 描述 | ✅ 已有（与 check-gate.sh 新增脚本层 WARNING 对应，计划第三部分声明"文档已有描述，脚本补上检测逻辑，不冲突"） |

**结论：MISALIGNED**（3 处"四道"未更新 + CHANGELOG 无 Unreleased 节 + 无 BREAKING 标注）

---

### A6: 锚点表覆盖

**已添加的锚点（计划修复 C + N7）：**

| 锚点 | 计划要求 | 实际 |
|------|---------|------|
| EXIT_CODE 文档侧 | 修复 C | ✅ 存在（line 586-589） |
| EXIT_CODE 脚本侧 | 修复 C | ✅ 存在（line 591-594） |
| CI 平台探测 | 修复 C | ✅ 存在（line 596-600） |
| AGATE_ALIGNMENT_REVIEW_THRESHOLD | 修复 C | ✅ 存在（line 602-606） |
| 截图像素方差检测（M3.1）| N7（line 862-868） | **不存在** |
| 截图 average hash（M3.2）| N7（line 869-874） | **不存在** |

N7（plan:862-875）要求：步骤 2 文档声明落地后，追加 2 条锚点（`VARIANCE_WARNING` + `AGATE_SKIP_IMAGE_CHECKS` 锚点 + `AHASH_LIST` + `AHASH_DUPES` 锚点）。

**反向覆盖检查**（`check_anchor_coverage`）：
- `ci-gate-backstop.py` 已被纳入扫描范围（修复 B）— 其对应的锚点（CI 平台探测）也存在。✅
- 反向覆盖未报告错误 — 意味着 `check-p6-evidence.sh` 在锚点表中已有条目（"P6 evidence UI 检查"和"P6 截图去重（md5）"），只是缺少 M3.1/M3.2 对应的新关键词锚点。

**结论：MISALIGNED**（2 条 N7 锚点未添加）

---

### A7: 设计原则一致性

逐条检查相关 ADR（`agate/adr.md`）：

**ADR-001（子任务隔离）**：本次改动不改变任何 subagent 隔离行为。新增的 provenance 审计（审计 5）是在 pre-commit hook 侧运行，不影响 subagent 执行边界。
**结论：ALIGNED**

**ADR-002（机器可判定性）**：
- 像素方差检测：`variance < 50` → WARNING — 机器可判定的数值比较 ✅
- average hash：`AHASH_TOTAL > AHASH_UNIQUE` → WARNING — 可判定 ✅
- md5 去重：`MD5_TOTAL > MD5_UNIQUE` → exit 1 — 可判定 ✅
- EXIT_CODE 一致性：`LOG_EXIT != 0` 且 PASS → exit 1 — 可判定 ✅
- Pillow 缺失：降级为 WARNING — 显式可判定（不是静默跳过）✅
**结论：ALIGNED**

**ADR-003（最小约定）**：
- Pillow 是可选依赖（未安装时 WARNING 不阻断 + `AGATE_SKIP_IMAGE_CHECKS=1`）✅
- 不绑定被管理项目的技术栈（Pillow 是 agate 自身工具依赖）✅
- `gat_commands.P5` 多命令 WARNING 是低成本提示，不强制 ✅
**结论：ALIGNED**

**ADR-004（安全网分层）**：
- 变更在多防线生效：pre-commit hook → commit-msg hook → CI backstop → pre-push hook ✅
- CI backstop 现重跑 check-gate.sh + check-p6-provenance.sh（双层兜底）✅
**结论：ALIGNED**

**ADR-005（改动性质分类）**：
- md5 重复升级为阻断 → 破坏性变更 → minor bump（v0.15.0→v0.16.0）。计划已标注此判定。✅
- 其他变更均为非破坏性。✅
**结论：ALIGNED**

---

## 需要修复的项目汇总

| # | 问题 | 严重度 | 涉及文件 | 修复方向 |
|---|------|--------|---------|---------|
| 1 | "四道→五道"计数未同步 | 中 | `LIMITATIONS.md:38`, `state-machine.md:223`, `WORKFLOW.md:245` | 三处"四道"改为"五道"；LIMITATIONS.md 局限 3 审计列表补上审计 5 条目 |
| 2 | CHANGELOG 无 `[Unreleased]` 节 | 高 | `CHANGELOG.md` | 添加 `[Unreleased]` 节，含 BREAKING（md5 升级为阻断）+ Added（multi-platform CI + screenshot detection + provenance 审计 5 + pre-push hook + log format convention） |
| 3 | 缺少 `ci-gate-backstop.bats` | 高 | `agate/tests/unit/ci-gate-backstop.bats`(新建) | 按 plan B4 写 3 条 detect_ci_platform 测试 |
| 4 | 缺少 `pre-push-hook.bats` | 高 | `agate/tests/integration/pre-push-hook.bats`(新建) | 按 plan B4 写 3 条 pre-push hook 测试 |
| 5 | N7 锚点未添加 | 中 | `check-protocol-consistency.py` | 在 `SCRIPT_ALIGNMENT_ANCHORS` 追加 VARIANCE_WARNING + AHASH_LIST 两条锚点 |

---

## 闭环规则

| 结论 | 主 Agent 动作 |
|------|--------------|
| MISALIGNED (5 items) | **必须修复** —— 修复上述 5 项后重跑 consistency + bats，再 commit |

## 修复后的验证命令

```bash
# 修复完成后
python3 agate/scripts/check-protocol-consistency.py
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
bash agate/tests/scripts/count-tests.sh
```
