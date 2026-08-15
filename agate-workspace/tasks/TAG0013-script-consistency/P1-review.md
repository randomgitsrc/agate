---
phase: P1
task_id: TAG0013-script-consistency
type: review
parent: P1-requirements.md
trace_id: TAG0013-P1-20260815
status: approved
created: 2026-08-15
agent: requirements-review
---

# P1 评审 — agate 脚本一致性批（RM-AG0015 / RM-AG0017 / RM-AG0018 剩余）（复审轮）

> 独立视角审查（requirements-review），**复审轮**。上轮判定 needs-revision（§7 列 4 个必须修订项），
> analyst 已修订。本文件对照上轮 §7 四项逐项核验（已落实 / 未落实），并对 BDD-1..11 逐条终判。
> 只审不写：不修改 P1-requirements.md / 任何代码。
> 客观查证均在本 worktree 实测（rg / grep / ls），非转引 analyst 声称。

---

## 0. 结论摘要

**Status: approved**（复审轮，4 个修订项全部落实，无残留阻塞项）。

- 上轮 §7 的 4 个修订项全部核验为**已落实**（见 §1，逐项附物证）；
- BDD-1..11 逐条终判：11 条全部可二值判定且目标合理（见 §2）；
- 影响面表 4.1/4.3/4.4 计数已可复现（4.4 规则实测：协议文档面 378 / 含 CHANGELOG 595，与 analyst 声称逐项吻合）；
- 发现 1 个**非阻塞**小瑕疵（BDD-3 ② my-runner.sh 事实性描述，见 §4 注），不影响 gate 语义与实现方向。

**不构成 rejected / needs-revision**：4 项必须修订全部落实，无新缺口；瑕疵为描述性、不影响二值判定。

---

## 1. 上轮 §7 修订项逐项核验

### 修订项 1：BDD-3 豁免清单补「scripts/README.md 退役名」第 5 类 → **已落实**

- BDD-3（L139）Given 现列 **5 类**豁免，⑤ = `scripts/README.md` 退役名（gate-result.sh /
  agate-workspace-resolve.sh / check-windows-smoke.sh）。
- 物证：`agate/scripts/README.md` L45 实测含 `gate-result.sh` + `agate-workspace-resolve.sh`（并入
  `agate_common.py` 说明）；L3 实测含 `check-windows-smoke.sh` 已退役说明 → 三名单确实存在，豁免对象成立。
- 联动：§2 隐含需求补「scripts/README.md 退役名豁免」段（L105-107）；§4.4 豁免清单 ⑤ 同步（L280-281）。
- 粒度为**单名豁免**（仅 3 个退役名），非整文件豁免——scripts/README.md 的现行脚本名引用（如
  check-gate.py）仍需解析，合理。

### 修订项 2：扫描范围钉死协议文档面 + UPGRADING 整文件豁免 + BDD-1 措辞收窄 → **已落实**

- §4 开头新增「CHECK 10 扫描范围（决策：协议文档面）」决策框（L193-199）：PROTOCOL_FILES +
  PROTOCOL_DIRS + phase-cards/rules + README/AGENTS + UPGRADING + scripts/README + CHANGELOG（叙事降级），
  **显式不含** `docs/` 与 `agate-workspace/`，理由（docs/ 含退役 .sh 名、不扫=无 ERROR）写明。
- UPGRADING 豁免粒度为**整文件级**：BDD-3 ①（L134）「UPGRADING.md 整文件」；§2（L101-104）
  「表级豁免会让散文行 ERROR → 整文件豁免」；§4.4 ①（L275）「整文件」。物证：`agate/UPGRADING.md`
  L105 / L151 / L152 / L153 / L158 实测散文行含退役名（check-windows-smoke.sh / xxx.sh /
  gate-result.sh / agate-workspace-resolve.sh / install-hook.sh）→ 散文行确实存在退役名，整文件豁免必要且成立。
- BDD-1（L123）Given 措辞由「全仓」收窄为「协议文档面（扫描范围见 §4 开头）」→ 与影响面表范围一致。

### 修订项 3：影响面表修订（P3-tdd 补 ci-gate-backstop.py / assets/** 入表 / 4.4 计数可复现） → **已落实**

- **P3-tdd.md 补 `ci-gate-backstop.py` ×1**：表 4.1（L207）现列 `ci-gate-backstop.py ×1`。物证：
  `agate/phase-cards/P3-tdd.md` L25 实测含 `ci-gate-backstop.py`。✓
- **agate/assets/** 入表（新 4.3 节，L241-259）**：逐文件列出 11 个角色/模板文件的脚本名引用，
  注明「合计 47 处，当前 0 漂移」。实测复核：`rg` 对 `agate/assets/**/*.md` 计数 = **47**，与表一致。✓
- **4.4 计数可复现**：analyst 给出可复现规则（§4.4，L264-266：`rg -o` 精确 token 计数）。实测按该规则：
  phase-cards/rules **58** + 协议 md（10 agate 文件 + CONTEXT）**104** + README/AGENTS **22** + UPGRADING **86** +
  scripts/README **61** + assets/** **47** = **378**；含 CHANGELOG **217** → **595**。与 analyst 声称逐项吻合。
  口径对照：上轮我的 270/487 = 58+104+22+86（四类核心），不含 scripts/README（61）与 assets/**（47）；
  378 = 270+108 即补入两块新增行，口径闭合，无重复计数（README.md 计入 README/AGENTS 桶，协议 md 桶不含根 README）。✓
- 备注：analyst 文中「协议 md（PROTOCOL_FILES 11 + CONTEXT）」实为 10 个 agate 协议文件 + CONTEXT（根 README
  归入 README/AGENTS 桶），括号内「11」系笔误（PROTOCOL_FILES 含 README 共 11，计数时已剔除避免重复）——
  非语义问题，计数本身正确且与 README/AGENTS=22 无重复。见 §4 注 2。

### 修订项 4：BDD-5 叙事边界对齐 + docs/ 非扫描面处置 → **已落实**

- BDD-5（L149-151）Given 显式声明：叙事文件 = `NARRATIVE_DIRS` 覆盖集（CHANGELOG.md / archived/ /
  docs/plans|reviews|design-notes|tasks / agate-workspace/tasks/），且 `docs/superpowers`、`docs/guides`、
  `docs/agents`、`docs/notes`、`docs/hardening-roadmap.md` **不在扫描范围（协议文档面）内、不被 CHECK 10 扫描**。
- 物证：`check-protocol-consistency.py` L74 `NARRATIVE_DIRS` 实测 =（docs/plans/, docs/reviews/,
  docs/design-notes/, docs/tasks/, archived/, agate-workspace/tasks/, CHANGELOG.md）——与 BDD-5 Given 完全对齐。✓
- Then 明确：叙事文件至多 WARNING，非扫描面 docs/ 文件无输出（无 ERROR）→ 0 漂移（BDD-1）不破。✓

---

## 2. BDD 终判（11 条逐条 + 覆盖维度标注）

### 数据维度 ✓ / 前端维度 ✗（无 UI）/ 多端维度 ✓（git 暂存区语义）/ 边界维度 ✓（修订后）/ 兼容维度 ✓

- **BDD-1（数据✓ 边界✓）: approved**。Given 已收窄为「协议文档面」且范围在 §4 开头定义；豁免清单 5 类
  完整（见修订项 1）。实测：协议文档面当前 0 漂移（phase-cards/rules 58 处含 pre-commit-gate.sh 均可解析、
  assets/** 47 处含 formatter 名均可解析、scripts/README 退役名入豁免）→ Given 成立、0 漂移可满足。✓
- **BDD-2（数据✓ 边界✓）: approved**。Given/When/Then 全可二值判定；check-protocol-consistency.py
  exit 1（L837）+ Report.error 含 loc → 「消息含文件名与引用位置」可测。✓
- **BDD-3（数据✓ 边界✓）: approved**。豁免清单 5 类齐全（①UPGRADING 整文件 ②formatters ③3 hook 薄壳
  ④count-tests.sh ⑤scripts/README 退役名），每一类对象实测物证成立：formatters 目录（pytest.sh /
  vitest.sh / go-test.sh / generic-exit-only.sh / generic-tap.sh / generic-junit-xml.sh）真实存在；
  3 hook 薄壳在 `agate/scripts/` 存在；count-tests.sh 在 `agate/tests/scripts/` 存在。②中 my-runner.sh
  系 formatters/README.md 的示例名（`agate/assets/formatters/README.md` L108），豁免该名合理但描述见 §4 注 1。✓
- **BDD-4（数据✓ 兼容✓）: approved**。实测 phase-cards/rules 无 `.md L\d+` 行号引用（grep 0 命中）；
  scripts/ 前缀引用均存在；入 PROTOCOL_DIRS 不新增 CHECK 2/3 漂移。✓
- **BDD-5（数据✓ 边界✓）: approved**。与 NARRATIVE_DIRS 对齐 + docs/ 非扫描面处置显式声明（修订项 4）。✓
- **BDD-6/7/8（多端✓ 边界✓）: approved**。`_SELF_GATE_RE`（commit-msg-self-gate.py L38-40）实测不含
  README.md/AGENTS.md/CHANGELOG.md → 扩展目标明确；git 暂存区语义可由 git_repo fixture 造场景（test_cmsg_1..4 同款）。✓
- **BDD-9（兼容✓）: approved**。`agate/tests/unit/test_commit_msg_self_gate.py` 实测恰好 4 用例
  （grep `def test_` = 4）→ 「既有 4 用例不回归」有明确对象。✓
- **BDD-10/11（数据✓ 边界✓）: approved**。check-retrospective.py 现行为：warnings 存在才输出
  GATE RETRO（L90）、exit 0（L95）；RT.1 空输出已有测试断言 result.output == ""。BDD-10 新增提醒行须含
  「DEBT」与「roadmap」两词且仅在 warnings 时输出（不违反 RT.1）；BDD-11 Given 无异常 → 空输出 + exit 0。✓

**终判汇总：11/11 approved**，无 rejected / needs-revision 项。

---

## 3. 隐含需求覆盖（复审确认）

- **数据维度**: 覆盖（回归底线 749 pytest + 0 ERROR → BDD-1；增量性 → BDD-1/4；CHECK 10 不进
  SCRIPT_ALIGNMENT_ANCHORS，P4 拆独立脚本才需走 CHECK 9——§2 已识别）。✓
- **前端维度**: N/A（无 UI）。遗漏合理。✓
- **多端维度**: 覆盖（git 暂存区语义 → BDD-6/7/8；`_SELF_GATE_RE` 扩展模式 §5 表完整含 CHANGELOG 豁免）。✓
- **边界维度**: **修订后覆盖**。上轮三个缺口（scripts/README 退役名 / UPGRADING 散文行退役名 / docs/ 非扫描面
  退役名）分别由修订项 1、2、4 补齐；同名不同目录 count-tests.sh（§2 已识别）仍覆盖。✓
- **兼容维度**: 覆盖（CHECK 2/3 不新增 ERROR → BDD-4；既有 self-gate 4 用例不回归 → BDD-9；
  consistency 0 ERROR 底线 → BDD-1）。✓

---

## 4. 非阻塞观察（不影响 approved，P2 设计时确认即可）

1. **BDD-3 ② my-runner.sh 描述不精确**：清单将 my-runner.sh 与 pytest.sh 等并列描述为「真实存在于
   assets/ 不在 scripts/」，但 `agate/assets/formatters/` 实测无 my-runner.sh 实体文件——它仅作为示例名
   出现在 `agate/assets/formatters/README.md` L108（`.agate/formatters/my-runner.sh`）。豁免该名本身正确
   （避免示例引用被误报），但「真实存在」表述不实。建议 P2 将该类措辞改为「formatters 名（含 README 示例名）」。
2. **§4.4「PROTOCOL_FILES 11 + CONTEXT」括号笔误**：计数时根 README 已剔出（归 README/AGENTS 桶），
   实际为 10 agate 协议文件 + CONTEXT = 104。计数正确无重复，仅括号内数字「11」易误导。建议 P2 顺手修正。
3. **BDD-3 ① UPGRADING「整文件豁免」已定，无需再细化**：整文件级语义已消除上轮「表级 vs 散文行」歧义，
   P2 只需按整文件实现。

---

## 5. 裁剪 / frontmatter / P1 纯净性（复审确认）

- **裁剪**: `phases: [P1..P8]` 全流程无裁剪。P2 不可裁（CHECK 10 豁免 5 类 + 扫描范围 + `_SELF_GATE_RE`
  扩展模式需 architect 定案）；P3 不可裁（11 条二值 BDD）；P7 不裁（跨文件一致性即本次主题）；P8 不裁
  （改协议本体走版本发布）。理由充分。✓
- **risk_level: medium**: 合理（触及协议本体 + CI 底线 749 pytest + 0 ERROR，高于 low；无数据/安全风险，低于 high）。✓
- **capability_requirements**: python3+pyyaml / pytest / ruff 三态均 available，无 GAP。✓
- **domains: [backend, cli] / packages: 4 项**: 与改动域（脚本 + 测试 + 协议文档）匹配。✓
- **P1 纯净性**: BDD-1..11 均为期望行为（Given 状态 / When 运行脚本 / Then 输出与 exit code），非实现方案；
  唯一实现倾向（CHECK 10 留在 check-protocol-consistency.py 内）以 SUGGEST 标注且可被 P4 覆写，符合分级约定。✓
- **frontmatter**: `agate-frontmatter-check.py` P1 schema 四必填 + risk_level 枚举 + domains list 均合法。✓

---

## 6. 覆盖维度汇总

| 维度 | 判定 | 依据 |
|------|------|------|
| 数据 | 覆盖 | BDD-1/2/3/4/10/11 |
| 前端 | N/A | 无 UI 变更 |
| 多端 | 覆盖 | BDD-6/7/8（git 暂存区语义） |
| 边界 | 覆盖（修订后） | BDD-1/2/3/5（豁免 5 类 + 扫描范围 + docs/ 非扫描面） |
| 兼容 | 覆盖 | BDD-4（CHECK2/3 不回归）、BDD-9（既有 4 用例） |

**结论：approved。** 上轮 §7 四项全部落实，11 条 BDD 全部 approved，无残留阻塞项。
