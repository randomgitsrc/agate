---
phase: P2
task_id: TAG0013-script-consistency
type: review
parent: P2-design.md
trace_id: TAG0013-P2-20260816
status: approved
created: 2026-08-16
agent: plan-eng-review
---

# P2 方案评审（复审轮）— agate 脚本一致性批（RM-AG0015 / RM-AG0017 / RM-AG0018 剩余）

> 独立视角复审（plan-eng-review，工程经理视角）。只审不写：不修改 P2-design.md / 任何代码。
> 客观查证均在本 worktree 实测（python 模拟 / rg / 脚本实跑），非转引 architect 声称。
> 结论均引用具体锚点（候选方案编号 / 章节 / BDD 编号）。

---

## 0. 结论摘要

**Status: approved（上轮 BLOCKER-1 + 非阻塞 1-5 + 测试缺口 7/8 全部已落实，本轮无新 BLOCKER）**

- **BLOCKER-1 已落实**：P2-design.md §2 步骤 4（L103-105）改为「main() CHECK 状态循环必须同步修正」，提供 `e["check"].split("-")[0] == key`（或 `startswith(key + "-")`）两种等价修法，明确「不再声明『无需改 main()』」；并同步纳入 §9 决策记录 6（L282）与 §11 完成标志 1（L292）。
- **非阻塞 1-5 全部已落实**（§2 白名单下划线形状 + 库文件声明、豁免② forward-defense + my-runner.sh 天然豁免、CHECK 2 影响面精确表述、count-tests 基线统一 751、docstring CHECK 10 行入完成标志）。
- **测试缺口 7/8 已落实**：§2 新增「测试策略」节（L130-136），夹具选型推荐 (a) 最小假协议树，BLOCKER-1 回归断言场景 A/B + 旧逻辑锁定。
- **本轮新观察 2 项（均非阻塞）**：L70「可复现 378/595」措辞与修订正则的计数口径差异；缺口 8 回归测试「复刻表达式」弱于「驱动 real main()」。见 §2 新观察。

---

## 1. 上轮 BLOCKER-1 逐项核验

| 复审目标（派发指引） | 结论 | 证据锚点 |
|---|---|---|
| BLOCKER-1：§2 步骤 4 改为 main() 状态匹配 `split("-")[0] == key`（或 `startswith(key + "-")`），不再声明「无需改 main()」 | **已落实** | P2-design.md §2 步骤 4（L103-105）：明示「CHECKS 列表追加 + main() 状态匹配修正（BLOCKER-1 修复，必改）」；L105 实测 `"CHECK10-scriptref".startswith("CHECK1")` 为 True 复述了碰撞根因，并给出 `split("-")[0] == key` / `startswith(key + "-")` 双方案与「不改变既有 CHECK 1-9 判定」结论 |
| 是否纳入 §9 决策 | **已落实** | P2-design.md §9 决策记录 6（L282）：完整记录 main() 状态匹配修正（BLOCKER-1），标注「属本次设计范围内的 main() 微调，随本次 commit 一起落」 |
| 是否纳入 §11 完成标志 | **已落实** | P2-design.md §11 完成标志 1（L292）：「main() CHECK 状态循环改用 `e["check"].split("-")[0] == key`（或 `startswith(key + "-")`）判定（BLOCKER-1 修复）」 |

**实测复核（本 worktree）**：
- `check-protocol-consistency.py` L810-816：`key = "CHECK" + title.split()[1]`；L813/L815 `e["check"].startswith(key)`。`"CHECK10-scriptref".startswith("CHECK1")` 实测 **True** → 碰撞成立。
- 修订方案正确性：`"CHECK10-scriptref".split("-")[0]` = `CHECK10`，`"CHECK1-yaml".split("-")[0]` = `CHECK1`，`"CHECK9-align".split("-")[0]` = `CHECK9` —— 对既有 CHECK 1-9 与新增 CHECK 10 均正确，且 `"CHECK10-scriptref".startswith("CHECK1-")` = False（`startswith(key + "-")` 变体同样正确）。
- 无其他 `startswith("CHECK...")` 碰撞点：run_all_checks（L769）只判 `name.startswith("CHECK 9")`，CHECK 10 标题不会误触发 `check_anchor_coverage`。

## 2. 上轮非阻塞 1-5 + 测试缺口 7/8 逐项核验

| 复审目标 | 结论 | 证据锚点 |
|---|---|---|
| 非阻塞 1：`agate_common\.py` 经下划线形状入白名单 + 声明库文件在检测范围 | **已落实** | P2-design.md §2 步骤 1（L73）：`SCRIPT_REF_RE` 增补 `agate_[a-z0-9-]+\.(?:py|sh)` 下划线形状；L78：「**声明：库文件也在漂移检测范围内**（当前 0 漂移不受影响，agate_common.py 真实存在 → token 合法）」。实测 `agate_common.py` 存在于 `agate/scripts/`；修订正则模拟扫描 **非 CHANGELOG 漂移 = 0 保持**，16 处 `agate_common.py` token 全部可解析到真实文件 |
| 非阻塞 2：豁免②标 forward-defense（当前不可达）+ my-runner.sh 天然豁免措辞 | **已落实** | P2-design.md §2 步骤 3.d（L97）：「**⚠️ forward-defense（防未来白名单放宽），当前不可达**……my-runner.sh 因不匹配白名单**天然豁免**，不显式加入豁免集合。P3 不应为不可达分支写测试」；§10 注 1（L286）措辞同步修订。实测 formatters 目录实际文件（pytest.sh / go-test.sh / vitest.sh / generic-*.sh）均不匹配 SCRIPT_REF_RE 白名单形状 → 天然豁免成立 |
| 非阻塞 3：CHECK 2 影响表述改为「本就严格，激活面为 CHECK 3 + CHECK 10」 | **已落实** | P2-design.md §1 风险 2（L48）：「CHECK 2……对其**本就 ERROR 级**，扩展前后行为不变；本次变更真正激活的是 **CHECK 3**……与 **CHECK 10**」；BDD-4（L127）同步「影响面精确表述（非阻塞 3）」。实测 `check_line_refs`（CHECK 3）L279 用 `is_protocol_file` 判定 → 扩展 PROTOCOL_DIRS 真正激活 CHECK 3 严格面，与修订表述一致 |
| 非阻塞 4：§5 基线统一 751 | **已落实** | P2-design.md §5（L224）：「**基线 = 751（以 count-tests.sh 输出为准，实测「总计：751 个测试用例」）**……不采用 749 交接值（P0 时点值，已过时）」。实测 `count-tests.sh` 输出「总计：751 个测试用例」。全文无 749 残留 |
| 非阻塞 5：docstring CHECK 10 行入完成标志 | **已落实** | P2-design.md §11 完成标志 1（L292）：「**模块 docstring（L11-18）补一行「CHECK 10  协议文档脚本名引用漂移」（非阻塞 5，随 BLOCKER-1 main() 改动一起落）**」；§6 files_to_read（L234）同步标注 L11-18 |
| 测试缺口 7：BDD-1/4 夹具选型 | **已落实** | P2-design.md §2「测试策略（评审 §3 缺口 7/8 纳入，供 P3 执行）」（L130-132）：推荐 (a) 测试内构造最小假协议树（`tmp_path` 下建 `agate/scripts/` 假文件 + 协议 md，直接调 `check_script_name_refs(root, rep)` 断言 `rep.errors`/`rep.ok`），并给出不采用 (b) 真实 worktree 集成断言的明确理由（混入 277 WARNING 基线、断言口径复杂化）。沿用 `_load_cpc` importlib 加载模式（实测 test_check_protocol_consistency.py L14-17 存在该 helper） |
| 测试缺口 8：BLOCKER-1 回归断言 | **已落实** | P2-design.md §2「测试策略」（L133-136）：场景 A（CHECK10 报 ERROR → CHECK 1 仍 ✅ / CHECK 10 ❌）+ 场景 B（CHECK10 报 WARNING → CHECK 1 仍 ✅ / CHECK 10 ⚠️）+ 显式断言旧逻辑 `startswith(key)` 在该场景误标（锁定回归根因） |

**本轮新观察（均非阻塞，供 P3/P4 参考，不改变 approved 结论）**：
1. **L70「可复现 378/595」措辞轻微不精确**：L70 称 `SCRIPT_REF_RE`「取自 P1 §4.4 计数正则，可复现 378/595」，但 P1 §4.4 口径（595/217）对应**不含下划线形状**的原正则；修订正则（含 `agate_` 形状）实测为 **616/219**（非 CHANGELOG 应计 378+16=394 量级）。差异来自非阻塞 1 补入的 `agate_common.py` 16 处 token，非遗漏、不影响 0 漂移结论。建议 P3/P4 在实现注释或测试中标注「基线计数为 P1 §4.4 口径，修订正则含库文件 token」，避免数字核对困惑。
2. **缺口 8 回归测试「复刻表达式」弱于「驱动 real main()」**：设计 L133 建议在测试内复刻状态循环判定逻辑。若 P4 忘记改 `check-protocol-consistency.py` 的 main()（L810-816），该测试因复刻了**修订后**表达式仍会绿——存在「测试通过但 main() 未修」的假绿风险。建议 P3 优先：抽一个小 helper（如 `_check_status(title, rep)`）供 main() 调用且被测试直接断言，或对 main() 用 monkeypatch/stdout 捕获跑一次带 CHECK10 假 rep 的端到端断言。非阻塞，因 §11 完成标志已把 main() 修复列为显式验收点、P5 gate 会实跑覆盖。

---

## 3. 测试缺口复核（其余 BDD 覆盖）

| BDD | 结论 | 锚点 |
|---|---|---|
| BDD-1（0 漂移 PASS） | ✓ | 修订正则模拟非 CHANGELOG 漂移=0；§2 测试策略夹具 (a) 覆盖 |
| BDD-2（引用不存在脚本 → ERROR） | ✓ | §2 BDD 覆盖 L125 + 测试策略（`check-nonexistent-script.py` → `rep.error`） |
| BDD-3（5 类豁免） | ✓ | §2 BDD 覆盖 L126；豁免①-⑤ 逐条映射（含修订后 forward-defense 表述） |
| BDD-4（PROTOCOL_DIRS 扩展） | ✓ | §1 风险 2 + BDD-4 L127；实测无新增 CHECK 2/3 ERROR |
| BDD-5（叙事至多 WARNING / docs 不扫） | ✓ | §2 BDD 覆盖 L128；CHANGELOG 聚合单条 WARNING 决策（§9 决策 2） |
| BDD-6/7/8（README/AGENTS 触发 / CHANGELOG 豁免） | ✓ | §3 BDD 覆盖 L169-171；新 3 用例复用 git_repo + `_run_csg` 模式（实测该 helper 存在） |
| BDD-9（既有 4 用例不回归） | ✓ | §3 BDD 覆盖 L172；精确名锚定追加分支，既有分支未动（实测 test_cmsg_1..4 场景） |
| BDD-10/11（DEBT+roadmap 提醒 / 空输出） | ✓ | §4 BDD 覆盖 L208-209；提醒行在 `if warnings:` 块内（L183-188），RT.1 不回归 |

---

## 4. 锁定决策（复审确认，与上轮一致）

- **CHECK 10 内联（候选方案 A）成立，否决候选 B（拆独立脚本）**：复用 Report/iter/rel/is_narrative_file；无 CHECK 9 锚点循环引用。修订后 §2 步骤 4 补入 main() 状态匹配修正，规避了上轮唯一阻塞点。
- **self-gate 精确名锚定（候选方案 A）成立，否决候选 B（宽松 glob）**：上轮实测候选 B 会误命中 NOTICES.md / CLAUDE.md / HANDOFF-TAG0013.md；候选 A 零误报。修订保持。
- **check-retrospective 独立提醒行（候选方案 A）成立**：`if warnings:` 内追加含 DEBT+roadmap 独立行，exit 0 不变，RT.1 不回归。
- **PROTOCOL_DIRS 扩展为 3 目录（assets + phase-cards + rules）成立**：实测 0 处 `.md L\d+`、3 处 `scripts/` 前缀引用均真实存在；真实激活面 = CHECK 3 + CHECK 10（非阻塞 3 修订确认）。
- **P5_consistency 非 `--strict` 判据（0 ERROR）成立**：当前 0 ERROR / 277 WARNING 基线，CI 非 strict；count-tests 基线统一 751。
- **CHANGELOG 聚合单条 WARNING（§9 决策 2）合理**：155 处历史 `.sh` 名逐条报无拦截价值，协议面 ERROR 兜底已覆盖；NARRATIVE_DIRS 不重组、不读 .state.yaml——决策合理，不扩范围。

---

## 5. 返回给主 Agent

- 状态：**approved**
- 阻塞问题数：0
- 上轮 BLOCKER-1 + 非阻塞 1-5 + 测试缺口 7/8 全部已落实（逐项证据见 §1/§2）。
- 建议转告 architect/P3（非阻塞）：① L70 计数口径措辞在 P3 注释标注 P1 §4.4 基线口径；② 缺口 8 回归测试优先抽 `_check_status` helper 或端到端跑 main()，避免「复刻表达式」的假绿风险。
