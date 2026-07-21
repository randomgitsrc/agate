---
review_date: 2026-07-21
reviewer: protocol-alignment-review
change_summary: agate 多平台 CI 支持完整实施计划——self-gate 三处修复 + 7 条措施（M3.1/M3.2 截图检测、M4.1/M4.2 CI backstop 多平台 + provenance 审计、M5.1 pre-push hook、M1.3a/M1.3b 日志 EXIT_CODE 约定与一致性检测），M1.1 已判定不实施
files_changed:
  - agate/scripts/ci-gate-backstop.py
  - agate/scripts/check-p6-evidence.sh
  - agate/scripts/check-p6-provenance.sh
  - agate/scripts/commit-msg-self-gate.sh
  - agate/scripts/check-protocol-consistency.py
  - agate/scripts/install-hook.sh
  - agate/assets/templates/dispatch-prompt.md
  - agate/WORKFLOW.md
  - agate/state-machine.md
  - agate/dispatch-protocol.md
  - agate/platform-notes.md
  - agate/orchestrator-template.md
  - agate/git-integration.md
  - agate/LIMITATIONS.md
  - agate/scripts/README.md
  - AGENTS.md
  - SELF-GATE.md
  - agate/assets/review-roles/protocol-alignment-review.md
  - CHANGELOG.md
  - .github/workflows/protocol-tests.yml
---

# 协议-脚本对齐审查

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | MISALIGNED |
| A4 | 测试覆盖 | ALIGNED |
| A5 | 下游影响 + 文档传播 | ALIGNED |
| A6 | 锚点表覆盖 | ALIGNED |
| A7 | 设计原则一致性 | ALIGNED |

**MISALIGNED: 1  |  NEEDS_HUMAN_REVIEW: 0**

## 逐项审查

### A1: 文档→脚本对齐

逐条核对计划中声称的脚本改动与对应脚本现状。

#### 1. M4.1/M4.2: ci-gate-backstop.py 多平台 + provenance 审计

**计划声称**（plan:153-212）：新增 `detect_ci_platform()` 函数（Gitea → GitLab → GitHub 顺序检测）、`get_pr_metadata()` 适配器、在 `main()` 末尾追加 `check-p6-provenance.sh` 重跑逻辑。

**脚本现状**（ci-gate-backstop.py:98-116）：当前含 P6 git blame 单 author WARNING，不含多平台检测、不含 provenance 脚本重跑。

**结论**：ALIGNED。计划描述的改动与现状差异准确，新增功能语义清晰（检测顺序避免 Gitea 的 GitHub 兼容变量误判、provenance 重跑补 `--no-verify` 绕过场景）。

#### 2. M3.1: check-p6-evidence.sh 像素方差检测

**计划声称**（plan:298-351）：方差检测独立于文件大小分支，对 `screenshots/` 下所有文件运行；Pillow 缺失时输出 WARNING 而非静默跳过（决定 1）；`AGATE_SKIP_IMAGE_CHECKS=1` 主动跳过开关。

**脚本现状**（check-p6-evidence.sh:74-103）：当前只有 `SIZE ≤ 1024` 的 PNG header 检查 + md5 去重，无方差检测。

**结论**：ALIGNED。计划的代码位置（第 312-345 行，while 循环内但独立于 `if [ "$SIZE" -le 1024 ]`）确实实现了"方差检测独立于文件大小"的语义。`SKIP_NO_PILLOW` 特殊值和 WARNING 输出满足了决定 1 的"防静默失效"要求。

**注意**：计划用 `img.tobytes()` 替代了 `img.getdata()`（Pillow 14 兼容性），M3.2 代码中同样统一为此写法（plan:416 注明"合并时统一"）——这属于实施细节，不影响协议语义。

#### 3. M3.2: check-p6-evidence.sh average hash + md5 升级

**计划声称**（plan:362-421）：md5 重复从 `exit 2`（WARNING）升级为 `exit 1`（阻断）；新增 pure-Pillow average hash 作为视觉相似度检测（WARNING 不阻断）；不引入 `imagehash` 第三方依赖。

**脚本现状**（check-p6-evidence.sh:96-103）：当前 md5 重复为 `exit 2` 警告。

**结论**：ALIGNED。exit code 从 2→1 的语义变更（WARNING→阻断）准确反映到计划代码中（plan:375-379 `exit 1`）。注：M3.2 Python 代码中 `from PIL import Image` 出现两次（plan:384 和 plan:394），重复导入不影响功能但有冗余。

#### 4. M1.3b: check-p6-provenance.sh 审计 5（EXIT_CODE 一致性）

**计划声称**（plan:445-468）：新增"审计 5"，插入到审计 4（provenance.sh:204）与"协作规范：agent 字段"（provenance.sh:206）之间。逻辑：读取 `P6-evidence/*.log`，匹配末行 `EXIT_CODE: N`，与 P6-acceptance.md 中 PASS 声明对照——EXIT_CODE ≠ 0 配 PASS 声明 → exit 1。

**脚本现状**（check-p6-provenance.sh:204-237）：当前有审计 1-4 + agent 字段协作规范，无审计 5。

**结论**：ALIGNED。插入位置精确（plan:449 指明"第 204 行与第 206 行之间"），三种场景实测验证通过（plan:470）。

#### 5. Fix A: commit-msg-self-gate.sh 正则

**计划声称**（plan:75-93）：正则以 `agate/scripts/.*\.(sh|py)` 替代 `agate/scripts/.*\.sh` + 显式列名 `check-protocol-consistency\.py`；同步更新提示文字。

**脚本现状**（commit-msg-self-gate.sh:13）：旧正则为 `^(agate/scripts/.*\.sh|agate/scripts/check-protocol-consistency\.py|agate/[^/]+\.md|agate/.+/.*\.md|SELF-GATE\.md)$`

**结论**：ALIGNED。计划 diff（plan:80-81）将两处独立匹配合并为 `.*\.(sh|py)`，覆盖范围扩大。实测结果（plan:91）确认 6 样本正确匹配。

#### 6. Fix B: check_anchor_coverage 扫描范围

**计划声称**（plan:95-108）：在 `check-protocol-consistency.py` 的 `check_anchor_coverage` 中追加 `ci-gate-backstop.py`。

**脚本现状**（check-protocol-consistency.py:635-662）：只扫描 `check-*.sh` glob + 显式追加 `pre-commit-gate.sh`。

**结论**：ALIGNED。计划 diff（plan:103-106）追加方式与现有 `pre_commit` 模式一致。

---

### A2: 脚本→文档对齐

逐条核对计划是否将脚本变更同步到对应协议文档。

| 脚本改动 | 应更新的文档 | 计划覆盖 | 结论 |
|----------|-------------|---------|------|
| M4.1/M4.2 ci-gate-backstop.py 多平台 + provenance | dispatch-protocol.md:825, WORKFLOW.md:255, state-machine.md:232, LIMITATIONS.md 局限 8, platform-notes.md:57-63, orchestrator-template.md:91, git-integration.md:181 | B3 + B2 + N-N1 + N-N2 + N-N3 | ALIGNED |
| M3.1/M3.2 check-p6-evidence.sh 新检测 | dispatch-protocol.md:523, WORKFLOW.md:244, state-machine.md:222, LIMITATIONS.md 局限 6 | B1 + B2 | ALIGNED |
| M1.3a/M1.3b EXIT_CODE | dispatch-prompt.md, check-p6-provenance.sh 注释 | M1.3a + N4 | ALIGNED |
| M5.1 pre-push hook | install-hook.sh 注释, orchestrator-template.md:113, dispatch-protocol.md:800, scripts/README.md install-hook.sh | N3 + N-N4 + N-N6 + N-N7 | ALIGNED |
| Fix A 正则 | SELF-GATE.md, protocol-alignment-review.md | "SELF-GATE.md 触发条件同步" + N2 | ALIGNED |

**结论**：ALIGNED。所有脚本变更均有对应的协议文档更新计划。注：scripts/README.md 的 install-hook.sh 条目由 N-N7 覆盖，但 check-p6-evidence.sh / check-p6-provenance.sh / ci-gate-backstop.py 的三个条目未覆盖——该问题归入 A3。

---

### A3: 一致性连锁 + 反向传播

#### A3a（连锁：已知衍生改动）— 缺失项

**MISALIGNED-1: 内联 Python 脚本计数错误（AGENTS.md + LIMITATIONS.md）**

**计划声称**（plan:889-897 + plan:621-623）:
> AGENTS.md 依赖节中"8 个 gate 脚本内联 python3 调用"需更新为 9 个
> LIMITATIONS.md 局限 6 中 "8 个 gate 脚本内联 python3 调用" 需更新为 "9 个"

**实际事实**（AGENTS.md:22）:
> Python 3.8+ + `pyyaml`（`pip install pyyaml`）— 8 个 sh 脚本内联 python3：check-changelog.sh、check-p6-evidence.sh、check-p6-provenance.sh、check-pruning.sh、check-retrospective.sh、check-state-transition.sh、check-state-yaml.sh、gate-result.sh

`check-p6-evidence.sh` 和 `check-p6-provenance.sh` **均已在此列表中**。M3.1/M3.2 给 `check-p6-evidence.sh` 添加 Pillow 调用、M1.3b 给 `check-p6-provenance.sh` 添加 EXIT_CODE 审计的 python3 调用，只是在已有 Python 内联的同一脚本中增加新的 Python 代码块，**不是新增脚本**。总数仍为 8。

**结论**：MISALIGNED。计划声称从 8 变为 9 是错误的。正确的改法是：不改变计数 8，但可在注释中说明"其中 check-p6-evidence.sh 新增 Pillow 依赖"。

**建议**：撤消 AGENTS.md 和 LIMITATIONS.md 中 8→9 的 diff，改为在依赖描述中单独注明 Pillow 可选依赖（已在 LIMITATIONS.md 局限 6 B2 diff 中体现为新增 Pillow 条目，但不应改动 8→9 计数）。

---

**MISALIGNED-2: scripts/README.md 三处描述未更新（反向传播遗漏）**

scripts/README.md 是脚本的 canonical description，三处条目在计划改动后已过时但未出现在任何文档传播节（N1-N7, N-N1~N-N7）中：

| scripts/README.md 行 | 当前描述 | 应更新为 |
|----------------------|---------|---------|
| 15: `check-p6-evidence.sh` | `0=通过, 1=缺证据, 2=无 P6 文件` | md5 重复 → exit 1（阻断）已改变 exit code 语义；新增大方差/相似度检测。 |
| 16: `check-p6-provenance.sh` | `客观行为审计（三道）` | 审计 5 新增后共**五道** |
| 27: `ci-gate-backstop.py` | `push 后重跑 gate + P6 git blame 单 author WARNING` | 新增多平台检测（Gitea/GitLab/GitHub）+ `check-p6-provenance.sh` 重跑 |

**结论**：MISALIGNED。计划仅有 N-N7 更新了 scripts/README.md 的 install-hook.sh 条目（plan:950-955），但对上述三处条目的更新完全缺失。

**建议**：在三处 script/README.md 条目中同步更新描述。举例：
```diff
- | `check-p6-provenance.sh` (P2.1/P2.10) | P6 客观行为审计（三道）| 0=通过, 1=审计失败, 2=WARNING |
+ | `check-p6-provenance.sh` (P2.1/P2.10) | P6 客观行为审计（五道 + EXIT_CODE 一致性 + 协作规范）| 0=通过, 1=审计失败, 2=WARNING |
```

---

#### A3b（反向传播：应受影响但未列出的文件）— 已覆盖

以下文件经主动推断确认为已列在计划的 diff 中（无遗漏）：

- **role-system.md**：本次改动未触及角色体系（执行角色/评审角色定义不变）
- **phase-cards/**：阶段卡片是 WORKFLOW.md 的状态机表 derivative，表本身已在 B1 更新
- **CHANGELOG.md**：计划 B1 已明确指定 BREAKING 条目内容（plan:571-577）

---

### A4: 测试覆盖

计划提出的测试覆盖：

| 新增测试文件 | 内容程度 | 评估 |
|-------------|---------|------|
| `agate/tests/unit/ci-gate-backstop.bats` | 3 个完整用例（plan:227-245） | 完备 |
| `agate/tests/unit/commit-msg-self-gate.bats` | 4 个完整用例（plan:675-713） | 完备 |
| `agate/tests/unit/check-protocol-consistency.bats`（追加）| Fix B + Fix C 各 1 个完整用例（plan:720-757）| 完备 |
| `agate/tests/unit/check-p6-evidence.bats` | 已实测两种场景，计划未给出完整测试代码（plan:356-358） | 细节待补 |
| `agate/tests/unit/check-p6-provenance.bats`（追加）| 3 个骨架用例（plan:786-803），注释表明需 bdd helper fixtures | 骨架可验证 |
| `agate/tests/integration/pre-push-hook.bats` | 3 个骨架用例（plan:764-779），依赖 git-helper.bash | 骨架可验证 |

**结论**：ALIGNED。每条 script 改动都有对应测试文件或测试用例追加。`check-p6-evidence.bats` 的描述（plan:358）说"已实测"但未提供完整测试代码，建议实施时补全。骨架用例（pre-push-hook, check-p6-provenance）是合理的——integration 测试需 git 环境，可在 CI 中完整实现。

**注**：审查角色要求"必须附最近一次 bats 全量实跑输出"。目前为计划阶段，测试尚未实现，此要求适用于实施后的最终审查，非计划阶段。

---

### A5: 下游影响 + 文档传播

#### 破坏性变更

**md5 重复从 exit 2 → exit 1**：在此前版本中，包含 md5 重复截图的 commit **通过** gate（exit 2 = WARNING 不阻断）。v0.16.0 起相同 commit 将**失败**。这是个正确标注的破坏性变更（ADR-005 → minor bump）。

#### CHANGELOG

计划 B1（plan:571-577）指定了 `CHANGELOG.md` 的 `### BREAKING` 条目，内容精确描述了变更边界（md5 重复阻断 vs average hash WARNING 不阻断）。

#### 文档传播

本次文档传播覆盖**19 处**（B1-B3 + N1-N7 + N-N1~N-N7），包括全部 7 个协议文件 + platform-notes + orchestrator-template + git-integration + 角色文件 + SELF-GATE + AGENTS.md。传播路径依据 `protocol-alignment-review.md`「反向传播的常见路径」表：

| 改了 X | 应传播到 Y | 覆盖 |
|--------|-----------|------|
| `agate/state-machine.md` 表描述 | `WORKFLOW.md`、`dispatch-protocol.md`、`orchestrator-template.md`、`LIMITATIONS.md` | B1-B3, B2, N2, N-N2 |
| `agate/scripts/check-*.sh` 行为 | `scripts/README.md`、角色文件 | **部分——漏 3 处（见 A3）** |
| `agate/dispatch-protocol.md` gate 表 | 角色文件、模板文件 | M1.3a, N-N4 |
| `SELF-GATE.md` / `protocol-alignment-review.md` | self-gate 递归适用 | N2, "SELF-GATE.md 触发条件同步" |
| `CHANGELOG.md` 未更新 | A5 下游影响不完整 | B1 已覆盖 |

**结论**：ALIGNED（注：A3 中 scripts/README.md 的 3 处缺失已在 A3 报告，不重复计入 A5）。

---

### A6: 锚点表覆盖

计划新增 7 条锚点（Fix C: 4 条 + N7: 2 条 + 合计），逐条核对关键词匹配：

| 锚点 | 目标文件 | 关键词 | 关键词匹配源 |
|------|---------|--------|------------|
| EXIT_CODE 格式约定（文档侧）| `dispatch-prompt.md` | `EXIT_CODE` | plan:432-439 M1.3a 文本 |
| EXIT_CODE 一致性检测（脚本侧）| `check-p6-provenance.sh` | `EXIT_CODE` | plan:456 `EXIT_CODE: [0-9]+$` |
| CI 平台探测 | `ci-gate-backstop.py` | `detect_ci_platform, GITEA_ACTIONS, GITLAB_CI` | plan:154-163 |
| AGATE_ALIGNMENT_REVIEW_THRESHOLD | `install-hook.sh` | `AGATE_ALIGNMENT_REVIEW_THRESHOLD` | plan:263 |
| 像素方差检测 | `check-p6-evidence.sh` | `VARIANCE_WARNING, AGATE_SKIP_IMAGE_CHECKS` | plan:308,343 |
| average hash 相似度 | `check-p6-evidence.sh` | `AHASH_LIST, AHASH_DUPES` | plan:383,406-409 |

Fix B 修复了 `check_anchor_coverage` 的反向扫描，使 `ci-gate-backstop.py` 被纳入 CHECK 9 覆盖范围。

**结论**：ALIGNED。所有新增锚点关键词均与计划代码中的实际字符串匹配。N7 的 M3.1/M3.2 锚点标注了"步骤 2 文档声明落地后追加"的前置条件，这是合理的——按锚点设计模式，必须先有文档声明才有锚点。

---

### A7: 设计原则一致性

逐 ADR 检查：

| ADR | 相关变更 | 结论 |
|-----|---------|------|
| ADR-001（隔离性） | 变更均在工具/脚本层，不涉及主 Agent 执行阶段产出 | ALIGNED |
| ADR-002（可判定性） | 新增检测（方差/相似度/EXIT_CODE）均产出确定的 exit code；Pillow 缺失时降级为 WARNING（显式可判定） | ALIGNED |
| ADR-003（最小约定） | 引入 Pillow 作为 agate 工具依赖（非被管理项目依赖），且未安装时 WARNING 不阻断 + `AGATE_SKIP_IMAGE_CHECKS=1` 主动跳过 | ALIGNED（人工已确认：plan:858 `[HUMAN_CONFIRMED: 2026-07-21]`） |
| ADR-004（安全网分层） | M4.2 provenance 审计纳入 CI backstop → 强化第三层（CI 层） | ALIGNED |
| ADR-005（改动性质） | md5 升级正确判定为破坏性变更（minor bump v0.15.0→v0.16.0） | ALIGNED |
| ADR-006（双层角色） | 本次不涉及执行/评审角色变更 | ALIGNED |

**结论**：ALIGNED。ADR-003 的 Pillow 依赖已获人工确认，符合 ADR-003 "不绑定被管理项目技术栈"的核心精神。

---

## MISALIGNED 项汇总

### MISALIGNED-1: 内联 Python 脚本计数错误

- **影响文件**: AGENTS.md, LIMITATIONS.md
- **错误**: 声称从 8 增至 9，实际应保持 8
- **根因**: `check-p6-evidence.sh` 和 `check-p6-provenance.sh` 已在内联 Python 脚本列表中，新增 Python 代码不增加脚本计数
- **修复**: 撤消 8→9 diff，改为在依赖描述中注明 Pillow 是 check-p6-evidence.sh 的新增依赖

### MISALIGNED-2: scripts/README.md 三处描述遗漏

- **影响文件**: scripts/README.md
- **错误**: check-p6-evidence.sh（退出码变更 + 新检测）、check-p6-provenance.sh（三道→五道）、ci-gate-backstop.py（多平台 + provenance 重跑）三个条目的描述未更新
- **修复**: 在 scripts/README.md 对应行更新描述

---

## 总体评估

计划文档质量高——19 处文档传播覆盖、7 条锚点、每项措施有验证状态说明（区分"已实测"vs"仍是推断"）。2 个 MISALIGNED 均为具体且可修复的问题（一个计数错误、一个描述遗漏），无结构性缺陷。

**修复后可直接进入实施。**
