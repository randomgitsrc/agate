---
phase: P4
task_id: TAG0020-independent-judge
type: review
parent: P4-implementation.md
trace_id: TAG0020-P4-20260822
status: approved
created: 2026-08-22
agent: review
---

# P4 实现评审（复审轮）— 独立 Judge 机制（RM-AG0032）：P6.5 挂载与三层防造假

> 评审角色：/review（偏执 Staff Engineer，backend 域单角色）。本文件为 P4 复审轮产出（覆盖首轮 rejected 版）：implementer 已修复 CRITICAL-1 + 次要项①②，③④⑤ 记录取舍。**只写评审意见不改代码**。

## 结论

**status: approved**（CRITICAL-1 已按内容寻址去重方案修复并经独立复现实验验证；次要项①②修复验证通过；③④⑤ 取舍记录合理；全量复评未发现修复引入的新 CRITICAL/BLOCKER，仅 3 条 INFORMATIONAL 残留项，见 PASS 2）。

- CRITICAL-1 写侧：`check-judge-verdict.py` step 9（L423-431）记账事件增 `verdict_hash = _verdict_hash(verdict_text)`（L291-298，verdict 全文 sha256，内容寻址）。
- CRITICAL-1 计侧：`check-events.py` L61-66/L104-112 改为按 `verdict_hash` set 去重计轮 + 无 hash 旧事件各计 1（legacy 向后兼容）；`MAX_JUDGE_VERDICT_EVENTS=2` 语义保留（L37-38、L112-116）。
- 独立复现（真实脚本）：① 同一合规 verdict 连跑 3 次 check-judge-verdict（等价 manual check-gate P6.5 + verdict commit + P7 commit）→ 账本 3 条同 hash 事件 → check-events「judge 轮次×1」**exit 0**（修复前该实验 exit 1 阻断 P7 commit）② 3 个不同 verdict 内容 → 3 hash → check-events 轮次 3 > 2 **exit 1**（预算兜底仍有效）③ 2 个不同 verdict → 轮次 2 **exit 0**（边界）④ 账本哈希链/ts 单调仍通过（同一次审计内验证）。

---

## CRITICAL-1 复审（写侧 × 计侧 × 语义保持）

| 复审点 | 结果 | 锚点 |
|--------|------|------|
| step 9 写 verdict_hash | ✅ | check-judge-verdict.py L423-431（`"verdict_hash": _verdict_hash(verdict_text)`）；`_verdict_hash` L291-298（全文 sha256，同文件多次重跑 hash 稳定） |
| check-events 按 hash 去重计轮 | ✅ | check-events.py L104-110（hash 入 set / 无 hash 计 legacy）+ L112（`count = len(hashes) + legacy`） |
| ≤2 语义保持（真实复核才 +1） | ✅ | L37-38 常量未动；L112-116 判定；边界实验 2 轮 exit 0 / 3 轮 exit 1 |
| 既有无 hash 用例/旧账本兼容 | ✅ | legacy 各计 1（L109-110）；test_check_events 既有 12 用例（构造事件均无 hash）全部仍绿 |
| 复现实验转绿（修复前 exit 1） | ✅ | 3 次同 verdict 连跑 → judge 轮次×1 exit 0（本评审实操） |

**方案评注**：内容寻址去重落在「写侧事件字段 + 计侧去重」，是首轮评审建议方案 A 的等价实现；`append_event` 保持通用（`row = dict(event)` 透传 verdict_hash，agate_common 零改动），verdict_hash 计算归属拥有 verdict 文件内容的 check-judge-verdict —— 分层合理。

## 次要项复审

- **I-1 白名单绝对路径归一化** ✅：`_is_whitelisted`（check-judge-verdict.py L157-166）basename 归一（`tok.split("/")[-1]`）+ `p6-evidence/` 前缀保留在完整 token（L163-164）；`_check_whitelist_outside` 同步（L169-184）。独立复现：绝对路径白名单引用（仓库既有书写惯例）→ **exit 0**；**绝对路径黑名单引用（`/abs/…/P6-acceptance.md`）仍 exit 1**——黑名单子串匹配不受归一化影响，非对称误报消除且无放水回归。
- **I-2 结论引用全形态匹配** ✅：`_REF_GROUP_RE` 取全部括号组 + `_REF_PATH_FULL_RE.fullmatch` 只取"路径形态"内容（可逗号分隔多文件，L376-389）。独立复现：描述含括号 `verified as discussed (in context) (e1.json)` → 正确提取 e1.json → **exit 0**；旧实现首个括号 token 会误取 "in"。
- **I-3/I-4/I-5 取舍记录** ✅ 合理：I-3（budget_exhausted 粘性）注明属 P2 语义副作用、改为轮次区分配对属 P2 变更，交主 Agent 决策——如实记录不静默；I-4（同 BDD 重复行）为可选增强进决策池；I-5（append 非原子 + fail-open）引用 P2 R7 缓解与 P2 明确"账本=辅助防线"设计，且 CRITICAL-1 修复后"清空账本逃生门"动机消除。

## 测试印证（复审轮实测）

- 新回归 5 用例 + 既有全绿：test_check_judge_verdict（32）+ test_check_events（14）+ test_agate_common（17）= **63 passed**；test_check_gate 全量 **165 passed**（含 gate_p65 6 用例 + 既有回归）；test_pre_commit_hook integration **55 passed**（真实 hook 全流程，含 retreat 回归修复路径）。
- check-protocol-consistency.py --strict-errors-only：**0 ERROR / 318 WARNING**（CHECK 9 锚点关键词 criteria_total/judge/prev_hash/GENESIS 仍命中）；count-tests.sh：**1168 用例 ≥ 749 基线，无漂移**。
- 生命周期路径覆盖闭环：`test_bdd_8_rerun_same_verdict_round_not_increment`（同 verdict 连跑 2 次 → 轮次=1）+ `test_bdd_8_judge_verdict_same_hash_dedupe_exit_0` + `test_bdd_8_judge_verdict_three_distinct_hashes_exit_1`——首轮指出的测试覆盖缺口（无生命周期用例）已补。

## PASS 2 — INFORMATIONAL 残留（不阻断，供 P7/主 Agent 关注）

- **R-1（新，内容寻址固有取舍）**：两个真实复核轮若产出**字节完全相同**的 verdict 内容，只计 1 轮（内容寻址去重）——≤2 上限在"重复同内容复核"场景可被轻微拉长。语义上字节相同 = 结论相同、未产生新复核工作，预算目的（防 judge 空转）仍成立；如需严格轮次计数，事件需另带 `round` 序号字段（与 I-3 的轮次区分配对可合并设计，属 P2 变更面）。
- **R-2（既有，未在新修复范围）**：黑名单扫描是扩展名锁定子串（`p6-acceptance.md`）；**变形引用**（裸 `P6-acceptance` 无扩展名 / `.html` 改扩展名）可绕过两节黑名单扫描（白名单扫描只匹配 `.md|yaml`）。未变形的标准路径引用全部被拦；行首 `- PASS|FAIL` 全文预判 + 主 Agent 派发约定仍兜底，风险低。建议 P7 一致性评审评估是否补"协议固定文件名裸名"黑名单项。
- **R-3（新，fail-closed 方向）**：I-2 全形态匹配要求引用为「路径形态（含扩展名）」——无扩展名证据引用（如 `(e1)`，即使同名文件真实存在）不再被提取 → 引用对称检查报"条目未被引用" exit 1。按 judge.md 产出规范（证据路径带扩展名）不受影响；方向 fail-closed 安全。

## 全量复评（防修复引入新问题）

| 复评项 | 结果 | 依据 |
|--------|------|------|
| 哲学红线（BDD-9）：exit code 才是门槛 | ✅ 无回归 | gate_p65（check-gate.py L881-905）+ pre-commit 2i.1（L386-396）调用链未动，机械核对 exit 1 仍阻断；verdict 不单独放行语义不变 |
| 信息隔离白名单（BDD-4）机械校验 | ✅ 修复且无放水 | I-1 归一化验证（绝对路径黑名单仍拦 / 白名单不误报）；黑名单/白名单/行首预判/AGATE_CARD+frontmatter 双排除逻辑未弱化 |
| 事件账本哈希链（BDD-7） | ✅ 无回归 | append_event/check-events 链式校验（prev_hash 逐行 + GENESIS_HASH 首行 + ts 单调）未改动；篡改测试仍绿（test_bdd_7_tampered_middle_line_chain_break_exit_1） |
| 历史兼容（BDD-2） | ✅ 无回归 | gate_p65 早退 / pre-commit `_judge_enabled` / ci-backstop `_judge_enabled` 三守卫未动；test_bdd_2_* 仍绿 |
| 三档预算（BDD-8） | ✅ 修复 | 轮次计数语义修正（真实复核才 +1）+ partial/budget_exhausted 交叉未动；边界语义实测（2 轮 exit 0 / 3 轮 exit 1） |
| 挂靠零新架构（BDD-3/10） | ✅ 无回归 | 无新增 phase 值（state-machine 非独立 phase 声明原样）；MAX_RETRY_MAP 未动；CHECK 9 锚点 + _DRIFT_SCRIPTS 仍有效；consistency 0 ERROR |

## 评审范围声明

- 复审对象 = 修复轮改动（check-judge-verdict.py / check-events.py + 5 新测试，P4-progress.md「P4 修复轮」节声明）+ 全量复评面（首轮 15 文件 + 2 补丁）。
- 实跑（全部 timeout 90s 内，真实 worktree 脚本，可写 scratch 目录）：复现实验 ×5（3 次同 verdict → 轮次 1 / 3 异 hash → exit 1 / 2 异 hash 边界 exit 0 / 白名单绝对路径 / 黑名单绝对路径 / I-2 括号描述）；pytest 切片 + test_check_gate 全量 165 + test_pre_commit_hook 55；consistency 0 ERROR；count-tests 1168 无漂移。
- [PROD_NOT_TOUCHED]：未改任何代码/协议文件，未触碰主 checkout。