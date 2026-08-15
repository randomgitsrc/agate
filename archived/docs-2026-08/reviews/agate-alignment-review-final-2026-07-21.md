---
review_date: 2026-07-21
reviewer: protocol-alignment-review
change_summary: T060 retro 3 bugfixes + P5 WARNING + self-gate 3修复 + 多平台CI + 截图检测(M3.1/M3.2) + EXIT_CODE一致性(M1.3a/M1.3b) + pre-push hook(M5.1) + provenance CI兜底(M4.2)
files_changed: [agate/scripts/agate-inject-card.sh, agate/scripts/check-scope-resolved.sh, agate/scripts/check-changelog.sh, agate/scripts/check-gate.sh, agate/scripts/commit-msg-self-gate.sh, agate/scripts/check-protocol-consistency.py, agate/scripts/ci-gate-backstop.py, agate/scripts/install-hook.sh, agate/scripts/check-p6-evidence.sh, agate/scripts/check-p6-provenance.sh, agate/assets/templates/dispatch-prompt.md, agate/LIMITATIONS.md, agate/WORKFLOW.md, agate/state-machine.md, agate/dispatch-protocol.md, agate/orchestrator-template.md, agate/git-integration.md, agate/platform-notes.md, agate/scripts/README.md, agate/assets/review-roles/protocol-alignment-review.md, SELF-GATE.md, AGENTS.md, CHANGELOG.md]
---

# 协议-脚本对齐审查

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | ALIGNED |
| A4 | 测试覆盖 | **MISALIGNED** (3 gaps) |
| A5 | 下游影响 + 文档传播 | ALIGNED |
| A6 | 锚点表覆盖 | ALIGNED |
| A7 | 设计原则一致性 | ALIGNED |

**MISALIGNED: 3 / NEEDS_HUMAN_REVIEW: 0**

**Overall verdict: NEEDS_FIXES** — 3 test suites specified in the plan were not created.

---

## 逐项审查

### A1: 文档→脚本对齐

结论：**ALIGNED**。所有 10 个脚本的 plan 规格均已正确实现。

#### Bug 1: agate-inject-card.sh 占位符缺失检测

**计划要求**（Plan t060 §Bug 1:58-68）：替换后检查 `new_text == text`，若未变化则 exit 1。

**脚本实现**（agate-inject-card.sh:52-54）：
```python
if new_text == text:
    print(f'AGATE_CARD 注入失败: {os.path.basename(dc)} 中未找到 AGATE_CARD_START/END 占位符', file=sys.stderr)
    sys.exit(1)
```
ALIGNED — 精确匹配。

#### Bug 2: check-scope-resolved.sh 跳过 dispatch-context

**计划要求**（Plan t060 §Bug 2:119-126）：跳过 `basename | grep -q 'dispatch-context'` 的文件。

**脚本实现**（check-scope-resolved.sh:19）：
```bash
basename "$f" | grep -q 'dispatch-context' && continue
```
ALIGNED — 精确匹配。

#### Bug 3: check-changelog.sh 短前缀提取 + fallback

**计划要求**（Plan t060 §Bug 3:164-189）：提取 `T\d+` 前缀，两步匹配（短前缀正则 + fallback 全路径 `grep -qF`）。

**脚本实现**（check-changelog.sh:12-38）：
- 行12-13：`TASK_ID_SHORT=$(echo "$TASK_ID" | grep -oE 'T[0-9]+' | head -1)` ✓
- 行32-33：`grep -qE "(^|[^0-9])${TASK_ID_SHORT}( |:|$|,|-)"` ✓
- 行36-37：`grep -qF "$TASK_ID"` fallback ✓
ALIGNED — 精确匹配，包含 `[^0-9]` 前缀防误匹配。

#### Bug 4: check-gate.sh P5 全量测试 WARNING

**计划要求**（Plan t060 §Bug 4:265-273）：grep P2 中 `- ` 行数，> 1 时输出 WARNING。

**脚本实现**（check-gate.sh:120-127）：
```bash
P5_CMD_COUNT=$(grep -cE '^\s+- ' "$TASK_DIR/P2-design.md" 2>/dev/null || echo 0)
P5_CMD_COUNT=$(echo "$P5_CMD_COUNT" | tail -1)
if [ "$P5_CMD_COUNT" -gt 1 ]; then
    echo "GATE P5 WARNING: P2 声明了 ${P5_CMD_COUNT} 个 gate_commands.P5 命令..."
```
ALIGNED — 精确匹配。

#### M3.1 方差检测

**计划要求**（Plan multi §M3.1:307-347）：独立于文件大小，包含 Pillow import 失败 WARNING + `AGATE_SKIP_IMAGE_CHECKS` 开关。

**脚本实现**（check-p6-evidence.sh:77-118）：
- 行77：`AGATE_SKIP_IMAGE_CHECKS=1` 主动跳过 ✓
- 行92-106：Pillow import 失败输出 `SKIP_NO_PILLOW` + WARNING ✓
- 行110-113：方差 < 50 → WARNING ✓
ALIGNED — 精确匹配。`AGATE_SKIP_IMAGE_CHECKS` 同时应用于 M3.1（行77）和 M3.2（行138）。

#### M3.2 Average hash

**计划要求**（Plan multi §M3.2:370-414）：纯 Pillow 实现，无 imagehash 依赖，md5 相同提前 exit 1（阻断）。

**脚本实现**（check-p6-evidence.sh:128-170）：
- 行128-137：md5 完全重复 → exit 1 ✓
- 行138-169：average hash → WARNING 不阻断 ✓
- 行138：`AGATE_SKIP_IMAGE_CHECKS!=1` 时才运行 ✓
ALIGNED — 精确匹配。

#### M4.1 CI 平台探测

**计划要求**（Plan multi §M4.1:153-193）：`detect_ci_platform()` Gitea→GitLab→GitHub 顺序，显式打印平台名。

**脚本实现**（ci-gate-backstop.py:28-60）：
- 行28-35：检测顺序 Gitea → GitLab → GitHub ✓
- 行57-60：显式 `print(f"CI platform: {platform}")`，None → SKIP ✓
ALIGNED — 精确匹配。

#### M4.2 provenance 审计 CI 兜底

**计划要求**（Plan multi §M4.2:200-212）：重跑 check-p6-provenance.sh，exit 1 时 FAIL。

**脚本实现**（ci-gate-backstop.py:150-160）：
```python
prov_result = subprocess.run(["bash", str(provenance_script), task_dir], ...)
if prov_result.returncode == 1:
    print(f"FAIL: check-p6-provenance.sh 重跑未通过...")
    return 1
```
ALIGNED — 精确匹配。

#### M1.3b EXIT_CODE 一致性检测

**计划要求**（Plan multi §M1.3b:451-468）：插入位置在"审计 4"之后"协作规范"之前，命名"审计 5"。

**脚本实现**（check-p6-provenance.sh:206-221）：
- 位置：审计 4（行204结束）之后，协作规范（行223开始）之前 ✓
- 注释行206：`# --- 审计 5：日志 EXIT_CODE 与 PASS/FAIL 声明一致性 ---` ✓
- 行210-216：PASS + EXIT_CODE≠0 → exit 1；缺少 EXIT_CODE → WARNING ✓
ALIGNED — 精确匹配。

#### M5.1 pre-push hook

**计划要求**（Plan multi §M5.1:258-284）：heredoc 用 `'HOOK_EOF'`（单引号防变量展开），`AGATE_ALIGNMENT_REVIEW_THRESHOLD:-20`，恒 exit 0。

**脚本实现**（install-hook.sh:54-73）：
- 行54：`<< 'HOOK_EOF'` 单引号 ✓
- 行56：`THRESHOLD="${AGATE_ALIGNMENT_REVIEW_THRESHOLD:-20}"` ✓
- 行72：`exit 0` 恒不阻断 ✓
ALIGNED — 精确匹配。

#### 修复 A: commit-msg-self-gate.sh 正则

**计划要求**（Plan multi §修复A:79-91）：`^(agate/scripts/.*\.(sh|py)|...)$`，提示文字同步更新。

**脚本实现**（commit-msg-self-gate.sh:13,30）：
- 行13：`^(agate/scripts/.*\.(sh|py)|agate/[^/]+\.md|agate/.+/.*\.md|SELF-GATE\.md)$` ✓
- 行30：提示文字含 `agate/scripts/*.py` ✓
ALIGNED — 精确匹配。

#### 修复 B: check_anchor_coverage 扫描范围

**计划要求**（Plan multi §修复B:97-106）：显式追加 `ci-gate-backstop.py`。

**脚本实现**（check-protocol-consistency.py:684-686）：
```python
ci_backstop = root / "agate" / "scripts" / "ci-gate-backstop.py"
if ci_backstop.exists():
    gate_scripts.append("agate/scripts/ci-gate-backstop.py")
```
ALIGNED — 精确匹配。

#### 修复 C: 新增锚点

**计划要求**（Plan multi §修复C:113-141 + N7:863-875）：6 条新锚点。

**脚本实现**（check-protocol-consistency.py:586-616）：
| 锚点 | 关键词 | 状态 |
|------|--------|------|
| EXIT_CODE (文档侧) | EXIT_CODE | ✓ 行586-589 |
| EXIT_CODE (脚本侧) | EXIT_CODE | ✓ 行591-594 |
| CI 平台探测 | detect_ci_platform, GITEA_ACTIONS, GITLAB_CI | ✓ 行596-600 |
| AGATE_ALIGNMENT_REVIEW_THRESHOLD | AGATE_ALIGNMENT_REVIEW_THRESHOLD | ✓ 行602-605 |
| M3.1 方差检测 | VARIANCE_WARNING, AGATE_SKIP_IMAGE_CHECKS | ✓ 行607-610 |
| M3.2 average hash | AHASH_LIST, AHASH_DUPES | ✓ 行612-615 |
ALIGNED — 全部 6 条存在且关键词正确。

---

### A2: 脚本→文档对齐

结论：**ALIGNED**。所有 11 个文档传播项均在实施中正确落地。

#### "四道" → "五道" 迁移

Plan N4 要求所有 `check-p6-provenance.sh` 相关文档从"四道"更新为"五道"：

| 文件:行号 | 内容 | 状态 |
|-----------|------|------|
| check-p6-provenance.sh:3 | `# 五道客观审计 + agent 字段协作规范` | ✓ |
| WORKFLOW.md:245 | `五道客观审计（证据-结论对应 + ... + EXIT_CODE 一致性 [审计5]）` | ✓ |
| state-machine.md:223 | `五道客观审计失败 → exit 1 拦截` | ✓ |
| scripts/README.md:16 | `五道 + EXIT_CODE 一致性 + 协作规范` | ✓ |
| LIMITATIONS.md:38 | `五道客观审计` | ✓ |

所有引用已验证 — 无残留"四道"。

#### BREAKING 变更标注

**CHANGELOG.md:28**：
```
- **BREAKING**：`check-p6-evidence.sh` md5 完全重复截图从 exit 2 (WARNING) 升级为 exit 1（阻断）
```
Plan B1 要求此条目 — ✓ 已落盘。简短但完整（含 exit 码语义变更）。

#### CI backstop 多平台更新

| 文件:行号 | Plan 要求 | 实际内容 | 状态 |
|-----------|-----------|----------|------|
| WORKFLOW.md:255 | "CI 平台（GitHub Actions / GitLab CI / Gitea Actions）" | 匹配 | ✓ |
| state-machine.md:232 | "CI 平台（GitHub Actions / GitLab CI / Gitea Actions）" | 匹配 | ✓ |
| dispatch-protocol.md:828 | "CI 平台（GitHub Actions / GitLab CI / Gitea Actions）" | 匹配 | ✓ |
| platform-notes.md:57,61-63 | "ci-gate-backstop.py 原生支持 / Gitea 未实测" | 匹配 | ✓ |
| orchestrator-template.md:91 | "CI 平台（GitHub Actions / GitLab CI / Gitea Actions）" | 匹配 | ✓ |
| git-integration.md:181 | "check-gate.sh + check-p6-provenance.sh" | 匹配 | ✓ |

#### N2: protocol-alignment-review.md 触发条件

**protocol-alignment-review.md:12**：
```
**触发条件**：`agate/scripts/*.sh`、`agate/scripts/*.py`、`agate/*.md`...
```
✓ `check-protocol-consistency.py` 改为 `*.py`。

#### N3: install-hook.sh 注释

**install-hook.sh:2**：
```
# install-hook.sh — 安装 pre-commit hook + commit-msg hook + pre-push hook
```
✓ 含全部三个 hook。

#### N4: 脚本注释更新

- **check-p6-evidence.sh:3-5**: `像素方差/average hash 检测（WARNING，需 Pillow）` ✓
- **check-p6-provenance.sh:2-3**: `五道客观审计` ✓

#### N-N4: dispatch-protocol.md install-hook 描述

**dispatch-protocol.md:803**：
```
每次 `git commit` 触发 `.git/hooks/pre-commit`（由 `~/.agate/scripts/install-hook.sh` 安装 pre-commit + commit-msg + pre-push hook）
```
✓ 含全部三个 hook。

**dispatch-protocol.md:826**：Pre-push hook 描述完整存在 ✓。

#### N-N6: orchestrator-template.md:113

**orchestrator-template.md:113**：
```
1. `bash ~/.agate/scripts/install-hook.sh` — 安装 pre-commit + commit-msg + pre-push hook
```
✓ 含全部三个 hook。

#### AGENTS.md 依赖

**AGENTS.md:22**：含 `Pillow` + `（可选）` + `check-p6-evidence.sh 新增 Pillow 依赖` ✓。

#### SELF-GATE.md 触发条件

**SELF-GATE.md:16**：`agate/scripts/*.py` ✓。

#### scripts/README.md 更新

| 条目 | Plan 要求 | 行号 | 状态 |
|------|-----------|------|------|
| check-p6-evidence.sh | md5 逐字节去重（阻断）+ 像素方差/average hash（WARNING）| 15 | ✓ |
| check-p6-provenance.sh | 五道 + EXIT_CODE 一致性 + 协作规范 | 16 | ✓ |
| ci-gate-backstop.py | provenance 审计重跑 + 多平台自动检测 | 27 | ✓ |
| install-hook.sh | pre-commit + commit-msg + pre-push hook | 33 | ✓ |

#### M1.3a: dispatch-prompt.md EXIT_CODE 格式约定

**dispatch-prompt.md:133-138**：
```
## 证据日志格式约定（M1.3a）
日志文件末行必须是可解析的退出码声明，格式固定为：
`EXIT_CODE: <n>`（n 为整数，0 表示成功）
```
✓ 完全匹配 plan。

#### B2: LIMITATIONS.md 修改

| 局限 | Plan 要求 | 行号 | 状态 |
|------|-----------|------|------|
| 局限3 | "provenance 的 CI 层覆盖为 git blame WARNING + provenance 重跑" | 44 | ✓ |
| 局限6 | "bash+git+python3+pyyaml+Pillow（可选）" + Pillow 单独条目 | 84,90 | ✓ |
| 局限8 | "支持 GitHub Actions / GitLab CI / Gitea Actions" + Gitea 未实测说明 | 107,113 | ✓ |

#### B1: dispatch-protocol.md:523 截图质量标准

**dispatch-protocol.md:523-524**：
```
操作类 BDD 截图必须互不相同（md5 逐字节去重，hook 阻断；average hash 视觉相似度检测，WARNING 不阻断）
截图须通过像素方差检测（低方差/疑似占位图 WARNING 不阻断）；Pillow 未安装时检测跳过并输出 WARNING，可设 `AGATE_SKIP_IMAGE_CHECKS=1` 主动跳过。
```
✓ 完全匹配 plan。

#### B3: WORKFLOW.md / state-machine.md CI backstop 更新

已验证（同上 CI backstop 表格）— 完全匹配。

---

### A3: 一致性连锁 + 反向传播

结论：**ALIGNED**。全部计划文档传播路径已验证 — 无遗漏。

**A3a（连锁）**：Plan 第八部分列出的全部文档传播项（N1-N7, N-N1 至 N-N7, B1-B4, SELF-GATE.md, AGENTS.md, scripts/README.md）均已在实施中落地。逐一验证如下：

| Plan 章节 | 应传播文件 | 实际路径 | 状态 |
|-----------|-----------|----------|------|
| B1 | dispatch-protocol.md:523 | 行523-524 | ✓ |
| B1 | WORKFLOW.md:244 | 行244 | ✓ |
| B1 | state-machine.md:222 | 行222 | ✓ |
| B2 | LIMITATIONS.md 局限3/6/8 | 行44,84,90,107,113 | ✓ |
| B3 | WORKFLOW.md:255, state-machine.md:232, dispatch-protocol.md:828 | 全部 | ✓ |
| N2 | protocol-alignment-review.md:12 | 行12 | ✓ |
| N3 | install-hook.sh:2 | 行2 | ✓ |
| N4 | check-p6-evidence.sh:3-5, check-p6-provenance.sh:2-3 | 行3-5, 2-3 | ✓ |
| N-N1 | platform-notes.md:57,61-63 | 全部 | ✓ |
| N-N2 | orchestrator-template.md:91 | 行91 | ✓ |
| N-N3 | git-integration.md:181 | 行181 | ✓ |
| N-N4 | dispatch-protocol.md:803,826 | 行803,826 | ✓ |
| N-N6 | orchestrator-template.md:113 | 行113 | ✓ |
| N-N7 | scripts/README.md:15-16,27,33 | 全部 | ✓ |
| SELF-GATE | SELF-GATE.md:16 | 行16 | ✓ |
| AGENTS | AGENTS.md:22 | 行22 | ✓ |

**A3b（反向传播）**：基于 plan 的"反向传播常见路径"表，跨检以下路径确认无遗漏：
- `check-p6-evidence.sh` 脚本行为变更 → `agate/scripts/README.md` 已更新 ✓
- `check-p6-provenance.sh` 脚本行为变更 → `agate/scripts/README.md` 已更新 ✓
- `check-changelog.sh` 脚本行为变更 → `agate/scripts/README.md` 已更新 ✓
- `ci-gate-backstop.py` 变更 → `agate/scripts/README.md` + `WORKFLOW.md` + `state-machine.md` 已更新 ✓
- `SELF-GATE.md` 触发条件变更 → `protocol-alignment-review.md` 触发条件同步 ✓
- `CHANGELOG.md` BREAKING → `dispatch-protocol.md` P5/P6 派发节 + `CHANGELOG.md` 均标注 ✓

---

### A4: 测试覆盖

结论：**MISALIGNED** — 3 个 plan 规格的测试文件/用例未创建。

#### MISALIGNED-1: `agate/tests/unit/commit-msg-self-gate.bats` 未创建

**Plan 要求**（Plan multi §B4 修复A测试:671-714）：创建 4 个单元测试：
1. `.sh` 文件触发 self-gate
2. `.py` 文件触发 self-gate
3. 非 agate `.py` 文件不触发
4. `self-gate-review:` 路径消除 WARNING

**现状**：文件 `agate/tests/unit/commit-msg-self-gate.bats` **不存在**。

替代方案：`agate/tests/integration/commit-msg-self-gate.bats`（6 个测试）覆盖了部分场景，但**未覆盖 `.py` 文件触发**（CSG.5 测试 `.sh`，CSG.6 测试 `.md`，无 `.py` 测试）。修复 A 的 `.py` 正则变更未经测试验证。

**建议**：补充 `agate/tests/unit/commit-msg-self-gate.bats` 或扩展集成测试加入 `.py` 触发用例。

#### MISALIGNED-2: `agate/tests/unit/check-protocol-consistency.bats` 未创建

**Plan 要求**（Plan multi §B4 修复B/C测试:718-757）：创建 3 个 CHECK 9 测试：
1. `ci-gate-backstop.py` 被纳入 anchor coverage 扫描范围
2. EXIT_CODE 锚点存在且关键词匹配（≥2 条）
3. AGATE_ALIGNMENT_REVIEW_THRESHOLD 锚点存在（≥1 条）

**现状**：文件 `agate/tests/unit/check-protocol-consistency.bats` **不存在**。

替代方案：`agate/tests/integration/consistency.bats` 有 CHECK 9 集成测试（CON.8, CON.9），但仅验证 CHECK 9 整体通过/失败，**未做锚点级别的单元断言**（未验证具体锚点条目是否在 SCRIPT_ALIGNMENT_ANCHORS 中）。

**建议**：创建该文件或扩展现有集成测试加入锚点级断言。

#### MISALIGNED-3: EXIT_CODE 审计 5 测试未实现

**Plan 要求**（Plan multi §B4 M1.3b测试:786-803）：在 `check-p6-provenance.bats` 追加 3 个测试：
1. 日志 `EXIT_CODE=1` 但声明 PASS → exit 1
2. 日志 `EXIT_CODE=0` 配 PASS → exit 0
3. 日志缺少 EXIT_CODE 尾行 → WARNING 不阻断

**现状**：`check-p6-provenance.bats` 共 22 个测试（PV.1-PV.20 + PV.4b, PV.5b），**无 EXIT_CODE 相关测试**。审计 5 的三种运行时路径未经测试验证。

**建议**：追加 3 个 EXIT_CODE 测试用例。

#### 已有测试覆盖验证（正常）

以下 plan 规格的测试已正确实现：

| Plan 用例 | 测试位置 | 行号 | 状态 |
|-----------|----------|------|------|
| Bug 1: 无占位符 → exit 1 | agate-inject-card.bats | 183-203 | ✓ |
| Bug 2: dispatch-context排除 | check-scope-resolved.bats | 77-94 | ✓ |
| Bug 3: CL.6 短前缀匹配 | check-changelog.bats | 71-83 | ✓ |
| Bug 3: CL.7 不误匹配 | check-changelog.bats | 85-98 | ✓ |
| Bug 3: CL.8 后缀-匹配 | check-changelog.bats | 100-112 | ✓ |
| Bug 4: P5多命令 WARNING | check-gate.bats | 363-384 | ✓ |
| E.12 md5重复 → exit 1 | check-p6-evidence.bats | 164-184 | ✓ |
| CI 平台探测 Gitea | ci-gate-backstop.bats | 6-14 | ✓ |
| CI 平台探测 GitLab | ci-gate-backstop.bats | 16-24 | ✓ |
| CI 平台探测 SKIP | ci-gate-backstop.bats | 26-32 | ✓ |
| pre-push hook 新分支 | pre-push-hook.bats | 6-40 | ✓ |
| pre-push hook 大改动 | pre-push-hook.bats | 42-95 | ✓ |

**关键验证项**：
- E.12 md5 重复期望 **exit 1**（非 exit 2）— ✓ 行183 正确断言 `[ "$status" -eq 1 ]`
- `HOOK_EOF` 使用**单引号**（无变量展开）— ✓ install-hook.sh:54 使用 `'HOOK_EOF'`
- `AGATE_SKIP_IMAGE_CHECKS` 在 M3.1（行77）和 M3.2（行138）**均生效** — ✓
- check-changelog.sh **fallback 到全 TASK_ID grep** — ✓ check-changelog.sh:36-37

---

### A5: 下游影响 + 文档传播

结论：**ALIGNED**。

**破坏性变更**：
- md5 重复从 exit 2 (WARNING) → exit 1 (阻断)：CHANGELOG.md:28 标注 `**BREAKING**` ✓
- Plan 判定为 minor bump (v0.15.0→v0.16.0)，遵循 ADR-005 ✓

**CHANGELOG** 覆盖完整：
- 修复节：3 个 bugfix ✓
- 新增节：M3.1, M3.2, M4.1, M4.2, M5.1, M1.3a, M1.3b, P5 WARNING, AGATE_SKIP_IMAGE_CHECKS ✓
- 变更节：BREAKING, commit-msg 正则, CHECK9 扫描范围, CHANGELOG 搜索方式 ✓
- 已评估节：M1.1（不实施）✓

**文档传播**（A2/A3 中已验证全部 11 个文件）：
- LIMITATIONS.md 局限3/6/8 ✓
- WORKFLOW.md ✓
- state-machine.md ✓
- dispatch-protocol.md ✓
- platform-notes.md ✓
- orchestrator-template.md ✓
- git-integration.md ✓
- SELF-GATE.md ✓
- AGENTS.md ✓
- protocol-alignment-review.md ✓
- scripts/README.md ✓

---

### A6: 锚点表覆盖

结论：**ALIGNED**。

`check-protocol-consistency.py` 的 `SCRIPT_ALIGNMENT_ANCHORS` 已添加全部 6 条新锚点：

| 锚点 | 文件 | 关键词 | 行号 |
|------|------|--------|------|
| EXIT_CODE (文档侧) | dispatch-prompt.md | EXIT_CODE | 587-589 |
| EXIT_CODE (脚本侧) | check-p6-provenance.sh | EXIT_CODE | 592-594 |
| CI 平台探测 | ci-gate-backstop.py | detect_ci_platform, GITEA_ACTIONS, GITLAB_CI | 597-600 |
| alignment-review 阈值 | install-hook.sh | AGATE_ALIGNMENT_REVIEW_THRESHOLD | 603-605 |
| M3.1 方差 | check-p6-evidence.sh | VARIANCE_WARNING, AGATE_SKIP_IMAGE_CHECKS | 608-610 |
| M3.2 average hash | check-p6-evidence.sh | AHASH_LIST, AHASH_DUPES | 613-615 |

`check_anchor_coverage` 已将 `ci-gate-backstop.py` 加入扫描范围（行684-686）✓。

`GATE_SCRIPT_EXEMPT` 中 `install-hook.sh` 保留豁免但通过独立锚点覆盖（行602-605）✓ — 符合决定 7。

---

### A7: 设计原则一致性

结论：**ALIGNED**。

相关 ADR 检查：

**ADR-003（最小依赖）**：新增 Pillow 依赖为可选。未安装时输出 WARNING（不阻断）+ `AGATE_SKIP_IMAGE_CHECKS=1` 可主动跳过。Plan N6 已人工确认：`[HUMAN_CONFIRMED: 2026-07-21 确认：Pillow 依赖可接受]` ✓

**ADR-005（改动性质分类）**：md5 重复升级为破坏性变更（改变 gate 通过条件），按 minor bump 处理 ✓。

**ADR-002（可判定性）**：所有 gate 检查保持机器可判定：
- md5 重复 → 逐字节比较 → 机器可判定 ✓
- 像素方差 → 数学计算 → 机器可判定 ✓
- average hash → 位图比较 → 机器可判定 ✓
- EXIT_CODE → 正则解析 → 机器可判定 ✓

**hook 鲁棒性优先**：pre-push hook 恒 exit 0（不阻断 push）✓，commit-msg self-gate hook WARNING 不拦截 ✓。

---

## MISALIGNED 汇总

| # | 类别 | 文件 | 问题 | 修复方向 |
|---|------|------|------|---------|
| 1 | A4 | `agate/tests/unit/commit-msg-self-gate.bats` | 文件未创建（plan B4 指定 4 测试），`.py` 文件触发 self-gate 未经测试 | 创建文件 + 加入 .py 触发/非触发用例 |
| 2 | A4 | `agate/tests/unit/check-protocol-consistency.bats` | 文件未创建（plan B4 指定 3 CHECK 9 单元断言） | 创建文件 + 加入 ci-gate-backstop.py coverage/EXIT_CODE anchors/THRESHOLD anchor 断言 |
| 3 | A4 | `agate/tests/unit/check-p6-provenance.bats` | EXIT_CODE 审计 5 的 3 个测试未追加（plan B4 指定） | 追加 PV.21/22/23：EXIT_CODE=1+PASS、EXIT_CODE=0+PASS、缺失EXIT_CODE |

**MISALIGNED: 3 / NEEDS_HUMAN_REVIEW: 0**

---

## 总体判定

**NEEDS_FIXES** — 3 个 plan 规格的测试文件/用例缺失。代码实现和文档传播均为 ALIGNED，但缺少测试覆盖意味着以下功能路径未经 bats 验证：

1. `.py` 文件触发 commit-msg-self-gate hook（修复 A 的核心变更）
2. CHECK 9 锚点 coverage 扫描范围正确性（修复 B 的核心变更）
3. EXIT_CODE 审计 5 的三种运行时行为（M1.3b 的核心逻辑）

这些 gap 不会导致现有功能退化，但会降低这些新增功能回归测试的可靠性。
