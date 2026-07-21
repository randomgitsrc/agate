---
review_date: 2026-07-21
review_round: 2 (re-review)
reviewer: protocol-alignment-review
base_review: docs/reviews/agate-alignment-review-2026-07-21-v2.md
plan_version: docs/plans/agate-multi-platform-ci-support-20260721.md（含第八部分）
---

# 协议-脚本对齐审查（Re-review Round 2）

## 逐项验证：Round 1 Finding → 第八部分是否解决 → 残留 Gap

### BLOCKER 项

| # | Round 1 发现 | 第八部分是否给出具体修改文本 | 残留 Gap | 结论 |
|---|-------------|--------------------------|----------|------|
| B1 | md5 重复从 WARNING 升级为阻断——破坏性变更未标注 | **是**。第八部分 B1 给出：(1) CHANGELOG.md BREAKING 条目；(2) dispatch-protocol.md:523 diff（含 md5 阻断 + average hash WARNING + 方差检测）；(3) WORKFLOW.md:244 diff；(4) state-machine.md:222 diff | 无 | RESOLVED |
| B2 | LIMITATIONS.md 局限 3/6/8 需更新但无具体修改文本 | **是**。第八部分 B2 给出：(1) 局限 3（:44）diff：provenance CI 层覆盖从"仅为 git blame WARNING"改为"git blame WARNING + provenance 重跑"；(2) 局限 6（:82-91）diff：标题加 Pillow（可选）、python3 计数 8→9、新增 Pillow 条目（含 WARNING + AGATE_SKIP_IMAGE_CHECKS=1 说明）；(3) 局限 8（:104-113）diff：标题改为三平台、描述改为 detect_ci_platform()、Gitea 未实测标注、M4.2 provenance 重跑说明 | 无 | RESOLVED |
| B3 | WORKFLOW.md/state-machine.md/dispatch-protocol.md CI backstop 描述需多平台+provenance 更新 | **是**。第八部分 B3 给出：(1) WORKFLOW.md:255 diff；(2) state-machine.md:232 diff；(3) dispatch-protocol.md:825 diff。三处均从"GitHub Actions"改为"CI 平台（GitHub Actions / GitLab CI / Gitea Actions）"，并加入 check-p6-provenance.sh 重跑 | 无 | RESOLVED |
| B4 | 修复 A/B/C 缺少 bats 测试覆盖 | **是**。第八部分 B4 给出：(1) commit-msg-self-gate.bats（4 个用例：.sh 触发、.py 触发、非 agate .py 不触发、self-gate-review 路径消除 WARNING）；(2) check-protocol-consistency.bats 新增 CHECK 9 扫描范围用例；(3) check-protocol-consistency.bats 新增 EXIT_CODE 锚点 + AGATE_ALIGNMENT_REVIEW_THRESHOLD 锚点用例；(4) pre-push-hook.bats（3 个用例）；(5) check-p6-provenance.bats 审计 5 用例（3 个场景） | M5.1 pre-push-hook.bats 和 M1.3b 用例只有骨架注释，无完整 bats 代码（对照修复 A/B/C 有完整代码）。但计划已在 M5.1 正文提供完整 hook 代码和实测结果，bats 骨架够实施时填充。 | RESOLVED（M5.1/M1.3b bats 为骨架但可实施） |

### 非阻断项

| # | Round 1 发现 | 第八部分是否解决 | 残留 Gap | 结论 |
|---|-------------|----------------|----------|------|
| N1 | M3.1/M3.2 文档声明需补充具体修改文本 | **是**。B1 的 dispatch-protocol.md:523 diff 已涵盖：md5 逐字节去重（阻断）+ average hash 视觉相似度检测（WARNING）+ 像素方差检测（WARNING）+ Pillow/AGATE_SKIP_IMAGE_CHECKS 说明 | 无 | RESOLVED |
| N2 | protocol-alignment-review.md 触发条件需同步更新 | **是**。第八部分 N2 给出 diff：`check-protocol-consistency.py` → `*.py` | 无 | RESOLVED |
| N3 | install-hook.sh 注释需更新 | **是**。第八部分 N3 给出 diff：注释从"安装 pre-commit hook"改为"安装 pre-commit hook + commit-msg hook + pre-push hook"，增加 pre-push 说明行 | 无 | RESOLVED |
| N4 | check-p6-evidence.sh / check-p6-provenance.sh 脚本注释需更新 | **是**。第八部分 N4 给出：(1) check-p6-evidence.sh 注释增加"md5 去重（阻断）+ 像素方差/average hash 检测（WARNING，需 Pillow）"；(2) check-p6-provenance.sh 注释"四道"→"五道" | 无 | RESOLVED |
| N5 | M5.1/M1.3b 缺少具体 bats 文件路径 | **是**。B4 明确：M5.1 → `agate/tests/integration/pre-push-hook.bats`；M1.3b → `agate/tests/unit/check-p6-provenance.bats`（追加用例） | 无 | RESOLVED |
| N6 | ADR-003 Pillow 依赖扩大需人工确认 | **是**。第八部分 N6 给出确认方向 + `[HUMAN_CONFIRMED]` 标记文本。确认理由：Pillow 是 agate 自身工具依赖，未安装时不阻断 gate，与 ADR-003 核心精神一致 | 需人工实际签署确认 | RESOLVED（待人工签署） |
| N7 | 步骤 2 文档声明落地后需为 M3.1/M3.2 补充锚点 | **是**。第八部分 N7 给出具体锚点代码：M3.1 方差检测锚点（VARIANCE_WARNING + AGATE_SKIP_IMAGE_CHECKS）+ M3.2 average hash 锚点（AHASH_LIST + AHASH_DUPES） | 无 | RESOLVED |

### Round 1 A3 衍生文件清单验证

| 应被影响的文件 | 第八部分是否覆盖 | 备注 |
|---|---|---|
| LIMITATIONS.md 局限 6 | **是**（B2） | |
| LIMITATIONS.md 局限 8 | **是**（B2） | |
| LIMITATIONS.md 局限 3 | **是**（B2） | |
| dispatch-protocol.md P6 gate 表 | **是**（B1 :523 diff） | |
| dispatch-protocol.md CI backstop 描述 | **是**（B3 :825 diff） | |
| WORKFLOW.md CI backstop 描述 | **是**（B3 :255 diff） | |
| WORKFLOW.md Pre-commit 检查总览 | **是**（B1 :244 diff） | P1.7 行增加 md5+方差+ahash 描述 |
| state-machine.md Pre-commit 检查全景 | **是**（B1 :222 diff + B3 :232 diff） | P1.7 行 + CI 兜底行 |
| protocol-alignment-review.md 触发条件 | **是**（N2） | |
| SELF-GATE.md 触发文件列表 | **是**（第八部分末尾单独节） | `check-protocol-consistency.py` → `*.py` |
| .github/workflows/protocol-tests.yml | 部分（第六部分 + 第七部分提及加 `pip install Pillow`） | 无具体 diff，但计划正文 352 行明确声明 |
| install-hook.sh 自身注释 | **是**（N3） | |
| agate/scripts/README.md | **否** | 见新发现 N-N1 |
| agate/tests/README.md | **否** | 见新发现 N-N2 |
| check-p6-evidence.sh 脚本注释 | **是**（N4） | |
| check-p6-provenance.sh 脚本注释 | **是**（N4） | |
| AGENTS.md 依赖节计数 | **是**（第八部分末尾单独节） | 8→9 |

---

## 新发现

### N-N1：platform-notes.md CI backstop 描述未更新

**位置**：platform-notes.md:57-63

**当前文本**：
> | CI backstop（gate 重跑 + git blame WARNING）| ⚠️ 自实现 | ⚠️ 自实现 | ⚠️ 自实现 | 仅 GitHub Actions 提供开箱实现 |
> **CI backstop 说明**：`.github/workflows/protocol-tests.yml` 的 `gate-backstop` job 用 GitHub Actions 实现。在自建 CI（Gitea/GitLab/本地）跑 agate 时：
> - 需要等价实现：`git push` 后重跑 `scripts/check-gate.sh` + 调用 `ci-gate-backstop.py`

**差异**：M4.1/M4.2 实施后，ci-gate-backstop.py 原生支持 Gitea/GitLab，不再是"仅 GitHub Actions 提供开箱实现"。此处的"⚠️ 自实现"和说明文字需更新。此文件不在第八部分的修改清单中。

**严重度**：非阻断（platform-notes.md 是平台适配参考，非 gate 逻辑或流程定义）

**建议**：第八部分追加 platform-notes.md:57-63 的 diff，至少：
- 表格行改为"GitHub Actions / GitLab CI / Gitea Actions 提供开箱实现（⚠️ Gitea 未实测）"
- 说明文字更新为反映 detect_ci_platform() 多平台支持

### N-N2：orchestrator-template.md CI 兜底描述未更新

**位置**：orchestrator-template.md:91

**当前文本**：
> - **CI 兜底**：push 后 GitHub Actions 重跑 gate + git blame 单 author WARNING，捕获 `--no-verify` 绕过

**差异**：与 WORKFLOW.md:255、state-machine.md:232 同类描述，已纳入 B3 修改范围，但 orchestrator-template.md 被遗漏。M4.1/M4.2 实施后需同步更新。

**严重度**：非阻断（orchestrator-template.md 是用户接入入口，描述过时会导致新用户误以为只支持 GitHub）

**建议**：第八部分 B3 追加 orchestrator-template.md:91 的 diff

### N-N3：git-integration.md CI backstop 描述未更新

**位置**：git-integration.md:181

**当前文本**：
> **禁止 `--no-verify` 绕过 hook**：CI backstop 会重跑 `check-gate.sh` + git blame 单 author WARNING，绕过 hook 的"恶意 commit"会被抓到并在日志暴露。

**差异**：M4.2 实施后 CI backstop 也重跑 check-p6-provenance.sh，此处描述需同步。

**严重度**：非阻断

**建议**：第八部分追加 git-integration.md:181 的 diff

### N-N4：dispatch-protocol.md:800 Pre-commit 检查全景表 install-hook.sh 描述未更新

**位置**：dispatch-protocol.md:802

**当前文本**：
> 每次 `git commit` 触发 `.git/hooks/pre-commit`（由 `~/.agate/scripts/install-hook.sh` 安装），按顺序执行：

**差异**：M5.1 实施后 install-hook.sh 还安装 pre-push hook，此描述仅提及 pre-commit。同时表后未提及 pre-push hook 的存在。

**严重度**：非阻断

**建议**：更新为"安装 pre-commit + commit-msg + pre-push hook"，并在全景表后补充 pre-push hook 说明

### N-N5：AGENTS.md 依赖节 "8 个 gate 脚本" 计数——第八部分仅提及更新但无具体 diff

**位置**：AGENTS.md 依赖节

**差异**：第八部分末尾说"AGENTS.md 依赖节中'8 个 gate 脚本内联 python3 调用'需更新为 9 个"，但未给出具体 diff 文本。与 B2 中 LIMITATIONS.md 的 8→9 更新一致，但 AGENTS.md 本身是独立的文件。

**严重度**：非阻断（文字明确，实施时无歧义）

### N-N6：orchestrator-template.md:113 install-hook.sh 描述仅提 pre-commit

**位置**：orchestrator-template.md:113

**当前文本**：
> 1. `bash ~/.agate/scripts/install-hook.sh` — 安装 pre-commit hook（重复执行安全，会覆盖旧链接）

**差异**：M5.1 实施后 install-hook.sh 安装三种 hook，此描述仅提 pre-commit。

**严重度**：非阻断

**建议**：改为"安装 pre-commit + commit-msg + pre-push hook"

### N-N7：scripts/README.md install-hook.sh 描述未更新

**位置**：scripts/README.md:33

**当前文本**：
> | `install-hook.sh` | 在项目仓库内安装 pre-commit hook（接受 `AGATE_ROOT` 参数）|

**差异**：M5.1 实施后需补充 pre-push hook 安装说明。

**严重度**：非阻断

---

## 更新后的 A1-A7 结论表

| # | 审查项 | Round 1 结论 | Round 2 结论 | 变化说明 |
|---|--------|-------------|-------------|---------|
| A1 | 文档→脚本对齐 | MISALIGNED | **ALIGNED** | B1-B4 全部在第八部分给出具体修改文本。残留 N-N1~N-N7 为新发现的非阻断文档传播遗漏 |
| A2 | 脚本→文档对齐 | MISALIGNED | **ALIGNED** | N2/N3 已解决。N-N4/N-N6 为新发现非阻断项 |
| A3 | 一致性连锁 + 反向传播 | NEEDS_HUMAN_REVIEW | **NEEDS_HUMAN_REVIEW** | Round 1 的 14 项衍生文件中 13 项已覆盖，1 项（scripts/README.md）在 N-N7 中补出。但新发现 7 处文档传播遗漏（platform-notes.md、orchestrator-template.md、git-integration.md、dispatch-protocol.md:800、AGENTS.md diff 缺失），说明"完整传播清单"仍不完整 |
| A4 | 测试覆盖 | NEEDS_HUMAN_REVIEW | **NEEDS_HUMAN_REVIEW** | 修复 A/B/C 已有完整 bats 代码。M5.1/M1.3b 仅有骨架注释。仍需实施完成后跑全量 bats 并附输出 |
| A5 | 下游影响 + 文档传播 | MISALIGNED | **NEEDS_HUMAN_REVIEW** | B1 破坏性变更已标注 CHANGELOG + 版本 bump。B2/B3 依赖/CI 描述已更新。但 N-N1~N-N7 7 处文档传播遗漏表明传播扫描仍不完整 |
| A6 | 锚点表覆盖 | ALIGNED | **ALIGNED** | N7 已给出 M3.1/M3.2 补充锚点的具体代码 |
| A7 | 设计原则一致性 | ALIGNED | **ALIGNED** | N6 给出 HUMAN_CONFIRMED 标记文本 |

---

## 总体结论

**Round 1 的 4 个 BLOCKER（B1-B4）全部 RESOLVED**——第八部分逐一给出了具体的修改文本、diff、bats 测试代码。

**Round 1 的 7 个非阻断项（N1-N7）全部 RESOLVED**。

**新发现 7 个非阻断项（N-N1~N-N7）**，均为文档传播遗漏——platform-notes.md、orchestrator-template.md（2 处）、git-integration.md、dispatch-protocol.md:800、AGENTS.md、scripts/README.md。这些文件在 Round 1 审查中未被识别为需同步更新，但实际包含 CI backstop / install-hook.sh 的描述，M4.1/M4.2/M5.1 实施后均需更新。

**统计**：
- MISALIGNED: 0（从 Round 1 的 3 降为 0）
- NEEDS_HUMAN_REVIEW: 3（A3/A4/A5——A3/A5 因新发现文档传播遗漏，A4 因 bats 骨架+待实跑）
- ALIGNED: 4（A1/A2/A6/A7）
- 新发现非阻断项: 7

**Verdict: ALIGNED（附条件）**

所有 MISALIGNED 已解决。3 项 NEEDS_HUMAN_REVIEW 的残留问题均为非阻断性质：
1. A3/A5 的文档传播遗漏（7 处）可在实施步骤 2 中一并修补，不影响代码实施
2. A4 的 bats 骨架需在实施时填充，但计划正文已提供足够的实测证据支撑骨架填充
3. N6 的 Pillow 人工确认需签署

**建议**：实施前在第八部分追加 N-N1~N-N7 的具体 diff，将传播遗漏清零。
