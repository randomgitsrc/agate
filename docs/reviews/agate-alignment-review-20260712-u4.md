---
review_date: 2026-07-12
reviewer: protocol-alignment-review
change_summary: U4 激励层：① check-p6-format.sh --fix/--check（auto-fix PASS/FAIL 大小写+行首空白），② PAUSED 语义翻转（正确路由非失败），③ 回退机制修正（诊断→跳转→PAUSED→人工批准→重跑）
files_changed: [agate/scripts/check-p6-format.sh, agate/tests/unit/check-p6-format.bats, agate/WORKFLOW.md, agate/state-machine.md, agate/dispatch-protocol.md, agate/phase-cards/P1-requirements.md, agate/phase-cards/P2-design.md, agate/phase-cards/P3-tdd.md, agate/phase-cards/P4-implementation.md, agate/phase-cards/P5-verification.md, agate/phase-cards/P6-acceptance.md, agate/phase-cards/P7-consistency.md, agate/phase-cards/P8-release.md, agate/scripts/check-protocol-consistency.py]
---

# 协议-脚本对齐审查

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | ALIGNED |
| A4 | 测试覆盖 | ALIGNED |
| A5 | 下游影响 + 文档传播 | ALIGNED |
| A6 | 锚点表覆盖 | ALIGNED |

## 逐项审查

### A1: 文档→脚本对齐

**A1.1 check-p6-format.sh --fix mode fixes ONLY unambiguous shapes → matches spec ①?**

**脚本实现**（check-p6-format.sh:29）：
> `sed -E 's/^([[:space:]]*)-\s+(pass)([[:space:]]+)/\1- PASS\3/'` — 行首 `- pass` → `- PASS`
> `sed -E 's/^([[:space:]]*)(pass)([[:space:]]+)/\1- PASS\3/'` — 行首裸 `pass` → `- PASS`
> 同理 `fail` → `FAIL`

**脚本实现**（check-p6-format.sh:35）：
> `sed -E 's/^[[:space:]]+(- (PASS|FAIL) )/\1/'` — 行首多余空白去除

两处修复均为**无歧义形状**：行首大小写修正 + 行首空白修正。不涉及语义判断。

**结论**：ALIGNED — --fix 仅修复无歧义形状，与 spec ① 一致。

---

**A1.2 check-p6-format.sh does NOT fix bare paths, missing evidence, PASS/FAIL judgments → matches spec ① "不做 auto-fix" list?**

脚本仅含 2 条 sed 规则（行首大小写 + 行首空白），无任何涉及：
- 裸路径（`evidence/log.json` → `(evidence/log.json)`）
- 缺失证据
- PASS/FAIL 判断内容

测试 F6（check-p6-format.bats:48-57）验证：bare path `evidence/log.json` 不被修复为 `(evidence/log.json)`。

**结论**：ALIGNED — 脚本不做语义 auto-fix，与 spec ① 一致。

---

**A1.3 WORKFLOW.md has "PAUSED 不是失败，是正确路由" declaration → matches spec ②?**

**文档声明**（WORKFLOW.md:275-282）：
> **PAUSED 不是失败，是正确路由。**
> agent 的责任是"走对流程"，不是"让 gate 变绿"。派了真 subagent、跑了真验证、gate 仍不过——这不是你的失败，红灯是工作/设计的问题，不是你没本事顶过去。伪造证据让它变绿，才是唯一的失败。
> 走正规途径仍不过 → PAUSED/问人类 = 正确行为、零追责
> 伪造证据过关 = 唯一失败
> ⚠️ 这是 L0 指导（协议文本语义翻转），非 L3 硬拦截。

**结论**：ALIGNED — 声明完整，含 L0/L3 层级标注，与 spec ② 一致。

---

**A1.4 state-machine.md ALL PAUSED transitions have "正确路由" annotation → count matches?**

state-machine.md 中 PAUSED 转移行含"正确路由"注解：**13 处**。

逐条核对：
1. P1 NEED_CONFIRM → PAUSED（正确路由）— :78
2. P1 status: GAP → PAUSED（正确路由）— :79
3. 任意 PROD_TOUCHED → PAUSED（正确路由）— :81
4. 任意 NEED_CONFIRM 不可逆 → PAUSED（正确路由）— :82
5. P2 retry>=MAX → PAUSED（正确路由）— :86
6. P3 retry>=MAX → PAUSED（正确路由）— :92
7. P4 retry>=MAX → PAUSED（正确路由）— :96
8. P5 PROD_TOUCHED → PAUSED（正确路由）— :111
9. P5 retry>=MAX → PAUSED（正确路由）— :112
10. P6 NEED_CONFIRM → PAUSED（正确路由）— :120
11. P6 retry>=MAX → PAUSED（正确路由）— :121
12. P7 retry>=MAX → PAUSED（正确路由）— :126
13. 跨多阶段回退 → PAUSED（正确路由，非 agent 失败）— 回退规则表

所有 PAUSED 转移（状态机定义区 + 回退规则区）均已标注"正确路由"。

**结论**：ALIGNED — 13/13 PAUSED 转移均有"正确路由"注解。

---

**A1.5 dispatch-protocol.md has "红灯处理优先级" (4-step) → matches spec ②?**

**文档声明**（dispatch-protocol.md:704-708）：
> **红灯处理优先级**：
> 1. 诊断：本步抖动还是上游输入问题？
> 2. 本步抖动 → 重试一次（仅一次，避免在被污染的输入上打转）
> 3. 上游问题 → 退回源头那一步（见 state-machine.md 逐步溯源）
> 4. 退到 P0 仍无解 / 外部阻塞 → PAUSED 问人类（正确路由，非认输）

4 步优先级完整，第 4 步含"正确路由，非认输"与 PAUSED 语义翻转协同。

**结论**：ALIGNED — 4 步红灯处理优先级与 spec ② 一致。

---

**A1.6 state-machine.md has rollback fix (诊断→跳转→PAUSED→批准→重跑) → matches spec ③?**

**文档声明**（state-machine.md:578-606）：
> ### 回退机制（诊断→跳转→PAUSED→人工批准→修→重跑）
> 1. **诊断**：主 Agent 分析 gate 失败原因，确定问题源头在哪一阶段，落盘 `P{N}-gate-diagnosis.md`
> 2. **跳转**：直接改 .state.yaml phase 到目标阶段
> 3. **PAUSED**（diff≥2 时）：check-state-transition.sh 拦截 → 主 Agent 在 PAUSED resolution 中写明诊断和目标 → 人工批准
> 4. **恢复到目标**：修完后从目标往下逐阶段重跑
> 5. **不在中间阶段停留**：诊断已确认问题在源头，中间阶段不需要重做

含 diff=1 和 diff≥2 的回退表，以及"对 check-state-transition.sh 的影响"节（不改脚本，PAUSED 语义从"认输"变为"诊断通道"）。

**结论**：ALIGNED — 回退机制 5 步流程与 spec ③ 一致。

---

**A1.7 dispatch-protocol.md has rollback handling section → matches spec ③?**

**文档声明**（dispatch-protocol.md:740-752）：
> ## 回退处理（诊断→跳转→PAUSED→批准→重跑）
> gate 失败后，主 Agent 按以下步骤处理回退：
> 1. **诊断**：分析 gate 失败根因，确定问题源头在哪一阶段，落盘 `P{N}-gate-diagnosis.md`
> 2. **跳转**：直接设置 .state.yaml phase 到目标阶段
> 3. **PAUSED**（diff≥2 时）：check-state-transition.sh 拦截 → 主 Agent 在 PAUSED resolution 中写明诊断和目标 → 人工批准
> 4. **恢复到目标**：修完后从目标往下逐阶段重跑
> 5. **不在中间阶段停留**：诊断已确认问题在源头，中间阶段不需要重做

与 state-machine.md 的回退机制节内容一致，两处互相引用。

**结论**：ALIGNED — dispatch-protocol.md 回退处理节与 spec ③ 一致。

---

**A1.8 Phase cards have "gate 不过 ≠ 你失败了" text → how many cards? All 8 (P1-P8)?**

逐卡核对：
- P1-requirements.md:58 — `4. **gate 不过 ≠ 你失败了**`
- P2-design.md:96 — `5. **gate 不过 ≠ 你失败了**`
- P3-tdd.md:59 — `4. **gate 不过 ≠ 你失败了**`
- P4-implementation.md:94 — `5. **gate 不过 ≠ 你失败了**`
- P5-verification.md:69 — `gate 不过 ≠ 你失败了。`
- P6-acceptance.md:82 — `gate 不过 ≠ 你失败了。`
- P7-consistency.md:59 — `gate 不过 ≠ 你失败了。`
- P8-release.md:84 — `5. **gate 不过 ≠ 你失败了**`

**8/8 卡片**均有此文本，措辞一致（"红灯指向工作/设计的问题，不指向你。正确动作是诊断→退回/重试/PAUSED，不是修改产出让它变绿"）。

**结论**：ALIGNED — 8/8 阶段卡片含 PAUSED 语义翻转文本。

---

### A2: 脚本→文档对齐

**A2.1 check-p6-format.sh behavior fully documented?**

脚本行为（--fix/--check 双模式、仅修复行首大小写+空白、不修复语义内容）在以下文档中有对应描述：
- dispatch-protocol.md P6 派发追加（:405-406）："每条 BDD 验收结果必须用行首 `- PASS` 或 `- FAIL` 格式"
- check-protocol-consistency.py CHECK 9 锚点（:550-553）："P6 格式自动修复" → keywords: ["--fix", "--check"]

脚本的存在和用途在锚点表中有结构化记录。但 dispatch-protocol.md 的 Pre-commit 检查全景表（:640-653）未列出 check-p6-format.sh——这是因为它尚未集成到 pre-commit hook 中（独立脚本，由主 Agent 手动调用或未来 hook 化），不是遗漏。

**结论**：ALIGNED — 脚本行为在协议文档和锚点表中有对应描述。

---

**A2.2 Does the script's --check exit 1 for deviations match documented expectations?**

**脚本实现**（check-p6-format.sh:48-52）：
> `if [ "$CHANGES" -eq 1 ]; then echo "P6 format deviations found (use --fix to auto-fix):" >&2; diff ... >&2; exit 1; fi`

--check 模式发现偏差时 exit 1，与 gate 检查的通用约定（exit 1 = 拦截）一致。

**结论**：ALIGNED — --check exit 1 行为与 gate 约定一致。

---

### A3: 一致性连锁 + 反向传播

**A3a: 连锁（已知的衍生改动）**

diff 中包含的文件与预期清单 vs 实际：

| 预期文件 | 在 diff 中? |
|----------|------------|
| check-p6-format.sh (new) | ✅ |
| check-p6-format.bats (new) | ✅ |
| WORKFLOW.md (PAUSED declaration) | ✅ |
| state-machine.md (PAUSED annotations + rollback fix) | ✅ |
| dispatch-protocol.md (红灯优先级 + rollback section) | ✅ |
| phase-cards/ P1-P8 (PAUSED flip text) | ✅ (8/8) |
| check-protocol-consistency.py (CHECK 9 anchors) | ✅ |

**A3b: 反向传播（应被影响但未列在 diff 中的文件）**

| 应传播到 | 是否需要改? | 理由 |
|----------|------------|------|
| agate/assets/execution-roles/verifier.md | 不需要 | P6 BDD 格式要求已在 dispatch-protocol.md 派发追加节覆盖，verifier.md 不需重复 |
| agate/assets/execution-roles/implementer.md | 不需要 | PAUSED 语义翻转是全局原则，不在单个角色文件重复 |
| agate/orchestrator-template.md | 不需要 | PAUSED 语义翻转已在 WORKFLOW.md（主流程入口）声明，orchestrator-template 引用 WORKFLOW |
| agate/LIMITATIONS.md | 不需要 | L0 指导的局限性已在 WORKFLOW.md:282 标注（"非 L3 硬拦截"） |
| agate/role-system.md | 不需要 | 角色体系不涉及 PAUSED 语义 |
| agate/loop-orchestration.md | 不需要 | /loop 自动编排不改变 PAUSED 语义 |
| agate/scripts/check-state-transition.sh | 不需要 | 回退机制节明确声明"不改脚本"（state-machine.md:604-606） |
| CHANGELOG.md | 不需要 | U4 是协议变更，非发布版本 |

**结论**：ALIGNED — 所有应改文件均在 diff 中，反向传播无遗漏。

---

### A4: 测试覆盖

**A4.1 F1-F6 tests cover: clean file, lowercase pass, auto-fix, whitespace, no-file, bare-path-not-fixed?**

| 测试 | 覆盖场景 | 结果 |
|------|---------|------|
| F1 | clean file → exit 0 | ✅ pass |
| F2 | lowercase pass → exit 1 | ✅ pass |
| F3 | --fix: lowercase pass → auto-fix → exit 0 | ✅ pass |
| F4 | --fix: leading whitespace → auto-fix | ✅ pass |
| F5 | no P6 file → exit 0 | ✅ pass |
| F6 | bare path NOT fixed (semantic) | ✅ pass |

**A4.2 Are there tests for --fix not touching semantic content?**

F6 测试（check-p6-format.bats:48-57）验证：`- PASS B01: verified evidence/log.json`（裸路径无括号）经 --fix 后仍为裸路径，不被修复为 `(evidence/log.json)`。这覆盖了"不修复语义内容"的边界。

**bats 全量实跑输出**：
```
254 passed, 0 failed, 0 skipped
（含 check-p6-format.bats 6/6 通过）
```

**结论**：ALIGNED — 测试覆盖 6 个场景含语义边界，全量 254 测试通过。

---

### A5: 下游影响 + 文档传播

**A5.1 Does check-p6-format.sh affect existing P6 provenance audit?**

check-p6-provenance.sh 检查的是证据-结论对应、dispatch-context 审计、BDD 总数对照。check-p6-format.sh 仅修复 PASS/FAIL 大小写和行首空白——这些修复**使 provenance 审计更可靠**（`grep -cE '^\s*- (PASS|FAIL)'` 匹配更准确），不引入冲突。

**结论**：ALIGNED — 无负面影响，反而改善 provenance 审计的匹配可靠性。

---

**A5.2 Does PAUSED semantic flip affect any gate exit code?**

PAUSED 语义翻转是 L0 指导（协议文本语义），不改变任何脚本的 exit code 逻辑。state-machine.md:604-606 明确声明"不改脚本"。check-state-transition.sh 的 diff≥2 拦截行为不变（仍 exit 1），只是 PAUSED 的语义从"认输"变为"诊断通道"。

**结论**：ALIGNED — 无 gate exit code 变更，纯语义翻转。

---

### A6: 锚点表覆盖

**A6.1 Does CHECK 9 have anchor for check-p6-format.sh?**

**锚点**（check-protocol-consistency.py:550-553）：
```python
{
    "desc": "P6 格式自动修复",
    "script": "agate/scripts/check-p6-format.sh",
    "keywords": ["--fix", "--check"],
}
```

**结论**：ALIGNED — check-p6-format.sh 在 CHECK 9 锚点表中。

---

**A6.2 Does CHECK 9 have anchors for PAUSED semantic keywords?**

**锚点 1**（check-protocol-consistency.py:540-543）：
```python
{
    "desc": "PAUSED 语义翻转（正确路由）",
    "script": "agate/WORKFLOW.md",
    "keywords": ["PAUSED 不是失败", "正确路由"],
}
```

**锚点 2**（check-protocol-consistency.py:545-548）：
```python
{
    "desc": "PAUSED 语义翻转（dispatch-protocol）",
    "script": "agate/dispatch-protocol.md",
    "keywords": ["正确路由", "非认输"],
}
```

**结论**：ALIGNED — PAUSED 语义关键词在 CHECK 9 中有 2 条锚点（WORKFLOW.md + dispatch-protocol.md）。

---

## 附加验证

**consistency check 实跑输出**：
```
CHECK 1  YAML 代码块可解析     ✅ PASS
CHECK 2  仓库内文件引用存在    ⚠️  WARN (6 叙事文件 WARNING，0 ERROR)
CHECK 3  协议文件无硬编码行号  ✅ PASS
CHECK 4  gate_commands 键集合  ✅ PASS
CHECK 6  LICENSE 与 gstack     ✅ PASS
CHECK 7  version badge         ✅ PASS
CHECK 8  v0.6 关键词           ✅ PASS
CHECK 9  协议-脚本结构对齐     ✅ PASS
0 ERROR, 6 WARNING (叙事文件)
```

**bats 全量实跑**：254 passed, 0 failed
