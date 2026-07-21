---
review_date: 2026-07-21
reviewer: protocol-alignment-review
change_summary: agate 多平台 CI 支持完整实施计划——含 self-gate 三处修复（A/B/C）、7 项措施（M4.1/M4.2/M5.1/M3.1/M3.2/M1.3a/M1.3b）、M1.1 判定不实施、7 条决定落地
files_changed:
  - agate/scripts/commit-msg-self-gate.sh（修复 A：正则通用化）
  - agate/scripts/check-protocol-consistency.py（修复 B：anchor coverage 扫描范围 + 修复 C：新增锚点）
  - agate/scripts/ci-gate-backstop.py（M4.1/M4.2：平台探测 + provenance 审计纳入）
  - agate/scripts/install-hook.sh（M5.1：pre-push hook）
  - agate/scripts/check-p6-evidence.sh（M3.1/M3.2：方差检测 + average hash）
  - agate/scripts/check-p6-provenance.sh（M1.3b：审计 5 EXIT_CODE 一致性）
  - agate/assets/templates/dispatch-prompt.md（M1.3a：日志格式约定）
  - agate/LIMITATIONS.md（局限 6/8 更新）
  - agate/WORKFLOW.md（CI backstop 描述更新）
  - agate/dispatch-protocol.md（P6 gate 表 + CI backstop 描述更新）
  - .github/workflows/protocol-tests.yml（pip install Pillow）
---

# 协议-脚本对齐审查

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | MISALIGNED |
| A2 | 脚本→文档对齐 | MISALIGNED |
| A3 | 一致性连锁 + 反向传播 | NEEDS_HUMAN_REVIEW |
| A4 | 测试覆盖 | NEEDS_HUMAN_REVIEW |
| A5 | 下游影响 + 文档传播 | MISALIGNED |
| A6 | 锚点表覆盖 | ALIGNED |
| A7 | 设计原则一致性 | ALIGNED |

## 逐项审查

### A1: 文档→脚本对齐

**1. LIMITATIONS.md 局限 6 依赖清单未含 Pillow**

**文档声明**（LIMITATIONS.md:82-91）：
> 局限 6：运行时依赖 bash+git+python3+pyyaml，但不限制被管理项目语言
> 具体影响：
> - python3 + pyyaml：check-protocol-consistency.py 和 ci-gate-backstop.py 需要 python3 + pyyaml。此外 8 个 gate 脚本内联 python3 调用（见 AGENTS.md 依赖节完整列表），缺 python3 时这些脚本的 YAML 解析逻辑不可用

**计划声明**（plan:352）：
> 需要 Pillow（`pip install Pillow --break-system-packages`），新增运行时依赖，需写进 `LIMITATIONS.md` 局限6依赖清单

**结论**：MISALIGNED
**差异**：计划明确要求将 Pillow 写入 LIMITATIONS.md 局限 6 依赖清单，但当前局限 6 的依赖列表仅列 bash + git + python3 + pyyaml，未含 Pillow。计划虽声明"需写进"，但作为审查对象，此差异在计划落地前即为 MISALIGNED——计划未提供具体的 LIMITATIONS.md 修改文本，仅说"需写进"。
**建议**：计划应补充 LIMITATIONS.md 局限 6 的具体修改内容，至少包括：(1) Pillow 加入依赖列表；(2) Pillow 未安装时的降级行为说明（WARNING + AGATE_SKIP_IMAGE_CHECKS=1）；(3) 更新 AGENTS.md 依赖节中"8 个 gate 脚本内联 python3 调用"的计数（check-p6-evidence.sh 新增 Pillow 调用）。

**2. LIMITATIONS.md 局限 8 CI backstop 仅支持 GitHub Actions**

**文档声明**（LIMITATIONS.md:104-113）：
> 局限 8：CI backstop 当前仅支持 GitHub Actions
> 具体影响：
> - GitLab CI、Jenkins、CircleCI 等平台的用户需自行适配 ci-gate-backstop.py 的环境检测逻辑

**计划声明**（plan:148-195，M4.1）：
> 新增 detect_ci_platform() 函数，检测顺序 Gitea → GitLab → GitHub

**结论**：MISALIGNED
**差异**：M4.1 实施后，ci-gate-backstop.py 将支持 Gitea/GitLab/GitHub 三平台，局限 8 的"仅支持 GitHub Actions"描述将过时。计划未同步更新。计划未列出对 LIMITATIONS.md 局限 8 的修改。
**建议**：计划应补充局限 8 的更新内容——至少改为"当前支持 GitHub Actions / GitLab CI / Gitea Actions，其他平台需自行适配"，并保留 Gitea 环境变量未实测的诚实标注。

**3. dispatch-protocol.md CI backstop 描述未更新**

**文档声明**（dispatch-protocol.md:825）：
> CI backstop（P1.3）：push 后 GitHub Actions `.github/workflows/protocol-tests.yml` 重跑 `check-gate.sh` + `ci-gate-backstop.py`，捕获 `--no-verify` 绕过 hook 的 commit；并对 `P6-acceptance.md` 单 author 情况发 WARNING 作为兜底审计。

**计划声明**（plan:196-212，M4.2）：
> provenance 审计纳入 backstop——在 main() 末尾追加 check-p6-provenance.sh 重跑

**结论**：MISALIGNED
**差异**：M4.2 将 provenance 审计纳入 CI backstop，但 dispatch-protocol.md:825 的 CI backstop 描述仅提及"单 author WARNING"，未提及 provenance 重跑。当前 LIMITATIONS.md:44 也明确说"CI backstop 当前不重跑 check-p6-provenance.sh（只重跑 check-gate.sh），provenance 的 CI 层覆盖仅为 git blame WARNING"——M4.2 实施后此描述需同步更新。
**建议**：计划应补充 dispatch-protocol.md:825 和 LIMITATIONS.md:44 的更新内容。

**4. M3.1/M3.2 截图检测规则未在协议文档声明**

**计划声明**（plan:494）：
> M3.1/M3.2 需要补一条声明，建议加在 `agate/dispatch-protocol.md` 的 P6 gate 表附近，一句话说明"截图证据须通过低方差/相似度检测，检测未过为 WARNING 不阻断"即可

**当前文档**（dispatch-protocol.md:787，P6 gate 表）：
> 截图质量标准：操作类 BDD 截图必须互不相同（md5 去重，hook 强制），查询类 BDD 可不截图但须有断言记录文件

**结论**：MISALIGNED
**差异**：计划正确识别了需要补声明，但当前文档的 P6 gate 表仅提及 md5 去重，未提及方差检测和 average hash。计划将此列为步骤 2（文档层声明），但未给出具体修改文本。此差异在计划落地前即为 MISALIGNED。
**建议**：计划应补充 dispatch-protocol.md P6 gate 表的具体修改文本，至少包括：(1) 方差检测（WARNING 不阻断）+ AGATE_SKIP_IMAGE_CHECKS=1 开关；(2) average hash 相似度检测（WARNING 不阻断）；(3) md5 完全重复升级为阻断级（exit 1）。

**5. check-p6-evidence.sh md5 重复行为语义变更**

**当前脚本**（check-p6-evidence.sh:96-103）：
> MD5 重复时输出 `GATE P6-EVIDENCE WARNING` 并 `exit 2`（WARNING，不阻断）

**计划声明**（plan:371-379）：
> md5 完全重复升级为阻断级（同一物理文件被引用两次，属证据造假）→ `exit 1`

**结论**：MISALIGNED
**差异**：计划将 md5 重复从 WARNING（exit 2）升级为阻断（exit 1），语义从"不阻断"变为"阻断"。这是一个破坏性变更——现有项目如果存在合法的 md5 重复截图（如行为差异类 BDD 截图视觉相同），gate 行为将从"通过但警告"变为"不通过"。当前文档 dispatch-protocol.md:787 和 WORKFLOW.md:222 均描述 md5 重复为 WARNING 不阻断。
**建议**：(1) 计划应明确标注此为破坏性变更；(2) 更新 dispatch-protocol.md:523 "截图质量标准"和 WORKFLOW.md:222 P6 gate 表中 md5 重复的描述；(3) 考虑在 CHANGELOG 标注此行为变更。

### A2: 脚本→文档对齐

**1. commit-msg-self-gate.sh 正则修改后提示文字未同步到协议文档**

**当前脚本**（commit-msg-self-gate.sh:13）：
> 正则：`^(agate/scripts/.*\.sh|agate/scripts/check-protocol-consistency\.py|agate/[^/]+\.md|agate/.+/.*\.md|SELF-GATE\.md)$`

**计划修改**（plan:80-88）：
> 正则改为 `^(agate/scripts/.*\.(sh|py)|agate/[^/]+\.md|agate/.+/.*\.md|SELF-GATE\.md)$`
> 提示文字改为含 `agate/scripts/*.py`

**协议文档**（protocol-alignment-review.md:12，触发条件）：
> 触发条件：`agate/scripts/*.sh`、`agate/scripts/check-protocol-consistency.py`、`agate/*.md`、`agate/**/*.md`、`SELF-GATE.md` 有改动时

**结论**：MISALIGNED
**差异**：修复 A 实施后，protocol-alignment-review.md:12 的触发条件描述需同步更新为 `agate/scripts/*.sh` + `agate/scripts/*.py`（而非单独列出 check-protocol-consistency.py）。SELF-GATE.md 也应检查是否需要同步更新触发文件列表。
**建议**：计划应补充 protocol-alignment-review.md 触发条件节的更新。同时检查 SELF-GATE.md 是否有类似的触发文件列表需同步。

**2. ci-gate-backstop.py 新增 detect_ci_platform 输出未在文档反映**

**当前脚本**（ci-gate-backstop.py:28-117）：
> main() 直接读 .state.yaml → run_gate → 对比 .gate-result.json → timestamp 验证 → git blame WARNING

**计划修改**（plan:186-194）：
> main() 改为先调用 detect_ci_platform() 并打印 "CI platform: {platform}"，无平台时 SKIP

**结论**：MISALIGNED
**差异**：ci-gate-backstop.py 新增了平台探测输出行（`CI platform: gitea/gitlab/github/None`），但 WORKFLOW.md:255 和 dispatch-protocol.md:825 对 CI backstop 的描述未提及平台探测逻辑。文档仍描述为"GitHub Actions 重跑"，未反映多平台支持。
**建议**：同 A1-2，更新 WORKFLOW.md 和 dispatch-protocol.md 的 CI backstop 描述。

**3. install-hook.sh 新增 pre-push hook 未在文档反映**

**当前脚本**（install-hook.sh:1-50）：
> 仅安装 pre-commit hook + commit-msg hook

**计划修改**（plan:258-282）：
> 新增 pre-push hook 安装（heredoc 生成，含 AGATE_ALIGNMENT_REVIEW_THRESHOLD 阈值检测）

**结论**：MISALIGNED
**差异**：install-hook.sh 将新增第三种 hook（pre-push），但 WORKFLOW.md 的 Pre-commit 检查总览（WORKFLOW.md:235-256）和 state-machine.md 的 Pre-commit 检查全景（state-machine.md:214-232）均未提及 pre-push hook。dispatch-protocol.md:802 的 hook 安装描述也仅提及 pre-commit 和 commit-msg。
**建议**：计划应补充以下文档更新：(1) WORKFLOW.md 新增 pre-push 检查节（或在现有 Pre-commit 节扩展）；(2) state-machine.md 检查全景表新增 pre-push 行；(3) dispatch-protocol.md hook 安装描述更新；(4) install-hook.sh 自身注释更新（第 2 行仍说"安装 pre-commit hook"，应改为含 pre-push）。

### A3: 一致性连锁 + 反向传播

**A3a: 已知的衍生改动（计划已列出但未给出具体修改文本）**

| 应被影响的文件 | 计划是否提及 | 具体修改文本 | 状态 |
|---|---|---|---|
| LIMITATIONS.md 局限 6 | 是（plan:352） | 无 | 需补充 |
| LIMITATIONS.md 局限 8 | 否 | 无 | 需补充 |
| LIMITATIONS.md 局限 3（provenance CI 覆盖） | 否 | 无 | 需补充 |
| dispatch-protocol.md P6 gate 表 | 是（plan:494） | 无 | 需补充 |
| dispatch-protocol.md CI backstop 描述 | 否 | 无 | 需补充 |
| WORKFLOW.md CI backstop 描述 | 否 | 无 | 需补充 |
| WORKFLOW.md Pre-commit 检查总览 | 否 | 无 | 需补充 |
| state-machine.md Pre-commit 检查全景 | 否 | 无 | 需补充 |
| protocol-alignment-review.md 触发条件 | 否 | 无 | 需补充 |
| SELF-GATE.md 触发文件列表 | 未确认 | 无 | 需检查 |
| .github/workflows/protocol-tests.yml | 是（plan:352） | 无 | 需补充 |
| install-hook.sh 自身注释 | 否 | 无 | 需补充 |
| agate/scripts/README.md | 否 | 无 | 需检查 |
| agate/tests/README.md | 否 | 无 | 需检查 |

**A3b: 反向传播——应被影响但计划未列出的文件**

1. **LIMITATIONS.md 局限 3**（LIMITATIONS.md:44）：
   > 已知局限：`git commit --no-verify` 绕过 pre-commit hook 时 provenance 审计也被绕过，CI backstop 当前不重跑 check-p6-provenance.sh（只重跑 check-gate.sh），provenance 的 CI 层覆盖仅为 git blame WARNING

   M4.2 将 provenance 审计纳入 CI backstop，此局限描述需更新。计划未提及。

2. **WORKFLOW.md:255 CI backstop 描述**：
   > CI backstop（P1.3）：push 后 GitHub Actions 重跑 `check-gate.sh` + `ci-gate-backstop.py`

   M4.1/M4.2 实施后需更新为多平台 + provenance 重跑。计划未提及。

3. **state-machine.md:232 CI 兜底描述**：
   > CI 兜底（P1.3）：push 后 GitHub Actions 重跑 `check-gate.sh` + `ci-gate-backstop.py`，捕获 `--no-verify` 绕过 hook 的 commit。

   同上，需更新。计划未提及。

4. **dispatch-protocol.md:523 截图质量标准**：
   > 操作类 BDD 截图必须互不相同（md5 去重，hook 强制）

   M3.1/M3.2 实施后需补充方差检测和 average hash 描述。计划提及需补声明但未给出具体文本。

5. **check-p6-evidence.sh 脚本注释**（check-p6-evidence.sh:2-5）：
   > check-p6-evidence.sh — P6 证据格式检查（P1.7）
   > 检查 P6-evidence/ 目录非空 + UI 截图实质检查（R1a）

   M3.1/M3.2 实施后脚本注释需更新以反映新增的方差检测和 average hash 功能。

6. **check-p6-provenance.sh 脚本注释**（check-p6-provenance.sh:2-3）：
   > check-p6-provenance.sh — P6 验收客观行为审计（P2.1/P2.10 降级方案 v2）
   > 四道客观审计 + agent 字段协作规范

   M1.3b 新增"审计 5"后，注释应从"四道"改为"五道"。

**结论**：NEEDS_HUMAN_REVIEW
**差异**：计划识别了部分需要同步更新的文件（LIMITATIONS.md 局限 6、dispatch-protocol.md P6 gate 表、CI workflow），但遗漏了至少 6 个应被影响的文件/位置。特别是 LIMITATIONS.md 局限 3 和局限 8、WORKFLOW.md CI backstop 描述、state-machine.md CI 兜底描述、以及两个脚本的自身注释。这些遗漏可能导致实施后文档与代码不一致。
**建议**：计划应补充完整的文档传播清单，逐一给出修改文本。建议在第四部分实施顺序的步骤 2（文档层声明）中，将所有需更新的文档位置列出并给出具体修改。

### A4: 测试覆盖

**计划声明的测试**：

| 措施 | 计划声明的测试 | bats 文件 |
|---|---|---|
| 修复 A | 端到端 commit 测试（6 样本文件 + 真实 git 仓库） | 未列 |
| 修复 B | 未提及 | 未列 |
| 修复 C | `python3 -c` 解析确认语法有效 | 未列 |
| M4.1/M4.2 | `agate/tests/unit/ci-gate-backstop.bats`（3 个用例） | 已列 |
| M5.1 | 集成测试（mock 超阈值改动 + git push） | 未列具体文件 |
| M3.1 | `agate/tests/unit/check-p6-evidence.bats` | 已列 |
| M3.2 | 同上 | 同上 |
| M1.3a | 纯文档，无测试 | N/A |
| M1.3b | 三场景实测 | 未列 bats 文件 |
| M1.1 | 不实施 | N/A |

**结论**：NEEDS_HUMAN_REVIEW
**差异**：
1. 修复 A（commit-msg-self-gate.sh 正则修改）无 bats 测试——计划声称"端到端 commit 测试"但未列出对应的 bats 文件。正则修改是行为逻辑改动，应有 bats 测试覆盖。
2. 修复 B（check_anchor_coverage 扫描范围）无 bats 测试——新增 ci-gate-backstop.py 到扫描范围，应测试"ci-gate-backstop.py 无锚点时 CHECK 9 报 WARN"。
3. 修复 C（新增锚点）仅用 `python3 -c` 验证语法，未验证运行时行为（锚点是否正确报 WARN/PASS）。
4. M5.1 pre-push hook 无 bats 文件名——计划说"集成测试"但未给出具体 bats 文件路径和用例。
5. M1.3b 审计 5 无 bats 文件——计划声称"三场景实测"但未列出 bats 文件。

**必须附最近一次 bats 全量实跑输出**：本审查为计划审查（代码尚未实施），无法提供实跑输出。但按审查角色要求，A4 必须附实跑输出——此处标注 NEEDS_HUMAN_REVIEW，要求实施完成后补跑全量 bats 并将输出附于审查报告更新版。

**建议**：
1. 为修复 A 新增 `agate/tests/unit/commit-msg-self-gate.bats`（或归入现有 sanity.bats）
2. 为修复 B 新增测试用例验证 ci-gate-backstop.py 被纳入 anchor coverage
3. 为 M5.1 明确 bats 文件路径（建议 `agate/tests/integration/pre-push-hook.bats`）
4. 为 M1.3b 明确 bats 文件路径（建议归入 `agate/tests/unit/check-p6-provenance.bats`）
5. 实施完成后跑全量 bats 并附输出

### A5: 下游影响 + 文档传播

**1. 破坏性变更：md5 重复从 WARNING 升级为阻断**

**当前行为**（check-p6-evidence.sh:99-103）：
> md5 重复 → `exit 2`（WARNING，不阻断 commit）

**计划行为**（plan:371-379）：
> md5 完全重复升级为阻断级 → `exit 1`

**结论**：MISALIGNED
**差异**：此变更对已有项目是破坏性的——如果现有项目的 P6-evidence/screenshots/ 中存在 md5 相同的截图（行为差异类 BDD 截图可能视觉相同），gate 行为将从"通过但警告"变为"不通过"。计划未在 CHANGELOG 标注此行为变更，也未在文档传播中提及。
**建议**：(1) 在 CHANGELOG 标注此破坏性变更；(2) 在 dispatch-prompt.md P5/P6 派发追加的"截图质量标准"节更新描述；(3) 考虑是否需要过渡期（如先 WARNING 一版再升级为阻断）。

**2. 新增运行时依赖 Pillow**

**结论**：MISALIGNED（同 A1-1）
**差异**：Pillow 是新增运行时依赖，影响所有使用 check-p6-evidence.sh 的环境。计划提及需更新 LIMITATIONS.md 和 CI workflow，但未给出具体修改文本，也未提及对 AGENTS.md 依赖节的影响。
**建议**：补充 LIMITATIONS.md、AGENTS.md 依赖节、CI workflow 的具体修改。

**3. 文档传播遗漏**

以下文档应被本次改动影响但计划未列出具体修改：

| 文档 | 需更新的原因 | 当前状态 |
|---|---|---|
| WORKFLOW.md:255 | CI backstop 多平台 + provenance 重跑 | 未更新 |
| state-machine.md:232 | CI 兜底多平台描述 | 未更新 |
| dispatch-protocol.md:825 | CI backstop 多平台 + provenance 重跑 | 未更新 |
| LIMITATIONS.md:44 | provenance CI 层覆盖升级 | 未更新 |
| LIMITATIONS.md:104-113 | CI backstop 多平台支持 | 未更新 |
| dispatch-prompt.md:523 | 截图质量标准补充方差/ahash | 未更新 |
| protocol-alignment-review.md:12 | 触发条件加 *.py | 未更新 |

**结论**：MISALIGNED
**建议**：计划应补充完整的文档传播清单。

### A6: 锚点表覆盖

**计划新增锚点**（plan:114-137，修复 C）：

| 锚点 | script | keywords | callers |
|---|---|---|---|
| EXIT_CODE 格式约定（文档侧） | dispatch-prompt.md | EXIT_CODE | — |
| EXIT_CODE 一致性检测（脚本侧） | check-p6-provenance.sh | EXIT_CODE | — |
| CI 平台探测 | ci-gate-backstop.py | detect_ci_platform, GITEA_ACTIONS, GITLAB_CI | .github/workflows/protocol-tests.yml |
| pre-push alignment-review 阈值 | install-hook.sh | AGATE_ALIGNMENT_REVIEW_THRESHOLD | — |

**对照现有锚点表**（check-protocol-consistency.py:444-586）：

现有锚点已覆盖 check-p6-evidence.sh 的 `ui_affected` 和 `md5/去重` 关键词。M3.1/M3.2 新增的方差检测和 average hash 逻辑在 check-p6-evidence.sh 中，但计划明确说明"M3.1/M3.2 暂不加对应锚点"，理由是"这两条规则目前只在脚本里实现，没有在任何协议文档里'声明'，按锚点设计模式，必须先在文档层声明（第三部分步骤1），才轮到加锚点"。

**结论**：ALIGNED
**差异**：计划的锚点新增逻辑与锚点设计模式一致（先文档声明再加锚点）。M3.1/M3.2 暂不加锚点的决定合理——待步骤 2 文档声明落地后再补。修复 B 将 ci-gate-backstop.py 纳入 anchor coverage 扫描范围，修复 C 新增 4 条锚点，覆盖了本次新增的规则。
**建议**：步骤 2 文档声明落地后，应为 M3.1/M3.2 补充对应锚点（方差检测关键词如 `VARIANCE` / `AGATE_SKIP_IMAGE_CHECKS`，average hash 关键词如 `AHASH` / `ahash`）。

### A7: 设计原则一致性

**ADR-001（隔离性）**：ALIGNED
计划不涉及主 Agent 写产出。M5.1 pre-push hook 是工具安装，不是阶段产出。

**ADR-002（可判定性）**：ALIGNED
M3.1 方差检测阈值 50 是机器可判定的（像素方差 < 50 → WARNING）。M5.1 阈值 20 是机器可判定的（改动行数 > 20 → 提示）。M1.3b EXIT_CODE 一致性是机器可判定的（grep EXIT_CODE + 对比 PASS/FAIL）。

**ADR-003（最小约定/不绑定技术栈）**：NEEDS_HUMAN_REVIEW
M3.1/M3.2 引入 Pillow 依赖。Pillow 是 Python 图像处理库，agate 的 gate 脚本已依赖 python3，Pillow 是 python3 生态内的包，不绑定被管理项目的技术栈。但 Pillow 是 agate 运行时依赖中第一个**非标准库 + 非 pyyaml** 的第三方包，扩大了依赖面。计划通过 AGATE_SKIP_IMAGE_CHECKS=1 和 WARNING 降级缓解了"没装就跑不了"的问题，这与 ADR-003 的"不硬编码技术栈"精神一致（Pillow 未安装时不阻断 gate）。但依赖面扩大本身是否违背"最小约定"原则，需人工裁决。

**ADR-004（安全网分层）**：ALIGNED
M4.2 将 provenance 审计纳入 CI backstop 是第三层防线（CI 层）的增强，与 ADR-004 的多层防线设计一致。M5.1 pre-push hook 是新增的提示层（WARNING 不阻断），不与现有三层冲突。

**ADR-005（改动性质决定流程）**：ALIGNED
不涉及流程入口判断的变更。

**ADR-006（双层角色）**：ALIGNED
不涉及执行/评审角色变更。

**结论**：ALIGNED（ADR-003 标 NEEDS_HUMAN_REVIEW 但 A7 不存在 MISALIGNED）
**差异**：ADR-003 的 Pillow 依赖扩大问题需人工确认是否可接受。计划已通过 AGATE_SKIP_IMAGE_CHECKS=1 和 WARNING 降级做了合理缓解，与 ADR-003 的核心精神（不绑定被管理项目技术栈）不冲突——Pillow 是 agate 自身工具依赖，不是对被管理项目的限制。
**建议**：人工确认 Pillow 依赖是否可接受。如果确认，建议在 LIMITATIONS.md 局限 6 中明确标注"Pillow 为可选依赖，未安装时图像检测降级为 WARNING"。

---

## 阻断级发现汇总

| # | 发现 | 严重度 | 来源 |
|---|------|--------|------|
| B1 | md5 重复从 WARNING(exit 2)升级为阻断(exit 1)是破坏性变更，计划未标注 | BLOCKER | A1-5, A5-1 |
| B2 | LIMITATIONS.md 局限 3/6/8 需更新但计划未给出具体修改文本 | BLOCKER | A1-1, A1-2, A3 |
| B3 | WORKFLOW.md/state-machine.md/dispatch-protocol.md 的 CI backstop 描述需多平台+provenance 更新，计划未列出 | BLOCKER | A1-3, A2-2, A3 |
| B4 | 修复 A/B/C 缺少 bats 测试覆盖 | BLOCKER | A4 |

## 非阻断但需关注

| # | 发现 | 来源 |
|---|------|------|
| N1 | M3.1/M3.2 文档声明（步骤 2）需补充具体修改文本 | A1-4 |
| N2 | protocol-alignment-review.md 触发条件需同步更新 | A2-1 |
| N3 | install-hook.sh 注释需更新（含 pre-push） | A2-3 |
| N4 | check-p6-evidence.sh/check-p6-provenance.sh 脚本注释需更新 | A3b-5, A3b-6 |
| N5 | M5.1/M1.3b 缺少具体 bats 文件路径 | A4 |
| N6 | ADR-003 Pillow 依赖扩大需人工确认 | A7 |
| N7 | 步骤 2 文档声明落地后需为 M3.1/M3.2 补充锚点 | A6 |
