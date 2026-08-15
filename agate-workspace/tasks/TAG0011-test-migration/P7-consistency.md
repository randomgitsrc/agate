---
phase: P7
task_id: TAG0011-test-migration
type: consistency
parent: P2-design.md
trace_id: TAG0011-P7-20260815
status: draft
created: 2026-08-15
agent: consistency-reviewer
# ── v2.0 机器计数 ──
blocker_count: 0
deviation_count: 1
deviation_critical_count: 0
design_gap_count: 0
design_gap_reviewed_count: 0
---

# P7 一致性检查报告 — TAG0011 测试框架迁移（bats → pytest）

> 角色：consistency-reviewer（只读交叉检查，未修改任何代码/测试/文档文件）
> 输入：P0-brief / P1-requirements / P2-design / P3-test-cases / P4-implementation /
> P5-test-results（unit.md + fail-list.txt）/ P6-acceptance + P6-evidence/
> 时间：2026-08-15（检查在 worktree `/home/kity/oclab/agate/.worktrees/agate-TAG0010` 实测核对）

## 1. DESIGN_GAP 配对

- grep `^\[DESIGN_GAP:` 确认 **P4-implementation.md 全文件 0 条** [DESIGN_GAP: 行首声明；
  各批次「偏离点」小节均为「无 `[DESIGN_GAP]` / `[SCOPE+]`」+ 实现细节记录，未按 DESIGN_GAP
  标准格式声明（非偏差条目）。
- 故 `design_gap_count: 0`、`design_gap_reviewed_count: 0`——无未配对项，无需
  `[DESIGN_GAP_REVIEWED]` 转抄行（P4 有则 P7 必须逐条转抄，此处 P4 无声明，配对义务为空）。
- 附带核对（gate 问题 4 / R2.3）：P4 无行首 `[DESIGN_GAP:` 声明，P4 声明数（0）与 P7
  `design_gap_count`（0）一致。**gate 会触发 1 条 T090 WARNING**（`check-gate.py P7` 实测
  exit 0 + WARNING）——P4 批次 8e 的 G_DG_ANCHOR 测试设计描述 L763/764 含散文
  「`[DESIGN_GAP: xxx]`」（gate_p7 行首锚点用例说明），被 T090 的 `gap:` 大小写不敏感启发式
  误命中；非行首声明、非偏差条目，属误报，不影响 gate exit code（WARNING 不阻断）。

## 2. SCOPE+ 闭环

- grep 确认 P4-implementation.md 无行首 `[SCOPE+` 声明（0 命中）；P1 §10 SCOPE+ 预留节无登记条目。
- 本任务无 SCOPE+ 增补 → 无未闭环项。（P4 批次 9c 的「TAG0002 [SCOPE+]」是历史回归测试名引用，
  非本任务 SCOPE+ 声明。）
- 附带核对：P1 §8 [SUGGEST] 4 项全部在 P4 落地——count-tests 改写（P4 批次 17）、test_*.py
  同目录替换（P4 批次 0-18）、windows_smoke marker 打标（各批 + 批次 17）、ruff src 扩展
  （pyproject `[tool.ruff] src = ["agate/scripts", "agate/tests"]`，实测）。

## 3. 跨文件一致性

### 3.1 P2§packages ↔ P4 实现范围

| package（P2-design.md 12 行声明） | 实现落点（P4-implementation.md） | 实测核对 | 结论 |
|---|---|---|---|
| agate-tests | 60 .bats → 60 个 test_*.py + conftest.py | `find agate/tests -name 'test_*.py'` = 60；`*.bats` = 0；conftest.py 存在（P4 批次 0） | 吻合 |
| agate-test-helpers | helpers/ 三文件 → conftest fixture 体系 | `agate/tests/helpers/` 目录不存在（P4 批次 18 删除 3 文件）；conftest 承接 | 吻合 |
| agate-test-scripts | count-tests.sh 改写 + check-windows-smoke.sh/.bats 退役 | count-tests.sh 为 pytest collect-only 实现（实测输出「总计：750 个测试用例（pytest collect-only 口径）」）；`check-windows-smoke.*` 0 残留 | 吻合 |
| agate-protocol-docs | P1 §5 表 E 文档重写 | 多数文件 0 bats 引用（见 §3.4）；**dispatch-protocol.md L878 遗留 1 处** | 基本吻合（1 处遗留） |
| agate-ci | protocol-tests.yml bats job → pytest job | pytest job（ubuntu 全量 + windows `-m windows_smoke`）+ ruff `agate/`（含 tests）+ bats 安装步骤已删 | 吻合 |

### 3.2 P1 BDD ↔ P6 验收结果

- P1 §7 共 12 条 BDD（BDD-1..12）；P6-acceptance.md frontmatter `pass: 12` / `fail: 0`，
  正文 12 条 PASS。**数量匹配（12 = 12）**。
- P6 对 P1 的 BDD 编号作了重排/合并，逐条映射核对：

| P1 §7 BDD | P6 验收条目 | 判定 |
|---|---|---|
| BDD-1 全量 pytest 全绿 ≥ 749 | P6 BDD-1（748 passed / 2 skipped，收集 750 ≥ 749） | 吻合 |
| BDD-2 consistency 0 ERROR | P6 BDD-2（--strict exit 0） | 吻合 |
| BDD-3 ruff 覆盖全部 py | P6 BDD-3（ruff check agate/ exit 0） | 吻合 |
| BDD-4 Windows CI 冒烟通过 | P6 BDD-5（78/750 marker 收集 + CI 配置；真机实跑待 CI，按 minimal_validation 兜底） | 吻合 |
| BDD-5 扫描器覆盖 .py 且树干净 | 并入 P6 BDD-8（platform-scan 0 命中 + 自身行为测试 16 passed 非空转） | 吻合（合并） |
| BDD-6 迁移期双跑对照 | P6 未单列——bats 已整体退役，过渡标准随之闭环；终态由 P6 BDD-1（全量绿）+ BDD-12（0 残留）覆盖 | 收敛（注 1） |
| BDD-7 encoding=utf-8 | P6 BDD-7（encoding 守卫 2 passed） | 吻合 |
| BDD-8 py38 + 平台无关 | P6 BDD-8（ast.parse py38 0 违规 + scan 0 命中） | 吻合 |
| BDD-9 CLI 输出契约 | P6 BDD-9（179 代表契约用例：workspace-resolve 10 / check-gate 124 / next-card 22 / json-get 8 / capture-env 15） | 吻合 |
| BDD-10 helpers fixture 等价 | P6 BDD-6（sanity 6 + helpers_python 3 + 全量 0 失败） | 吻合 |
| BDD-11 hook 链测试等价 | P6 未单列——hook 用例（批次 12 的 20 + 批次 13 的 56）已迁移并纳入 P6 BDD-1 全量回归 | 收敛（注 2） |
| BDD-12 冒烟机制决策落地 | P6 BDD-12（check-windows-smoke.sh/.bats 0 残留 + CI 引用 `-m windows_smoke`） | 吻合 |

- P6 另列 3 条 P1 非 BDD 项升格为验收 BDD：P6 BDD-4 = count-tests 改写（P1 §6.3）、
  P6 BDD-10 = pytest 全平台可跑（P1 §6.2 评估结论）、P6 BDD-11 = 文档/CI 同步
  （P1 §2.6 env-adapt-docs + §5 表 E）——对应实现均实测有证据（count-tests.log / windows-smoke-collect.log / env-adapt-docs.log）。
- 注 1：P1 BDD-6 的判定条件是「迁移期双跑对照，直至 bats 整体退役」；P4 批次 18 已退役全部 bats，
  P6 以迁移终态判定（全量 pytest 全绿 + 0 .bats 残留）替代过渡态双跑，标准自然闭环，非遗漏。
- 注 2：P1 BDD-11 的 hook 链行为由批次 12（commit-msg / pre-push / install-hook 20 用例）+
  批次 13（pre-commit-hook 48 + dispatch-context-card 8）迁移并纳入全量回归，行为等价由 P6 BDD-1
  的 748 passed 覆盖，非遗漏。

### 3.3 P4§impl-path ↔ P2 方案

| P2 方案决策（P2-design.md §1.5） | P4 落实路径（P4-implementation.md） | 实测 | 结论 |
|---|---|---|---|
| A1 同目录 test_*.py 替换，目录树不变 | 批次 0-18 逐批同目录新建 test_*.py，`.bats` 迁移期共存、批次 18 删除 | 60 个 test_*.py / 0 个 .bats，目录结构保留 | 吻合 |
| B1 单根 conftest.py fixture 体系 | 批次 0 交付 conftest.py（会话级 agate_root/python_exe + 函数级 task_dir/git_repo/run_cli + 纯函数 add_*） | conftest.py 存在，helpers/ 已退役 | 吻合 |
| C1 windows_smoke 显式 marker | 各批按 P3 §5.2 表 W + 每文件第 1 用例打标；pyproject 注册 markers | `-m windows_smoke` 收集 78/750 | 吻合 |
| D1 count-tests.sh 改写收集计数 | 批次 17 改写（`pytest --collect-only` 提取） | 输出 750 ≥ 749 | 吻合 |
| 批次规划 0-16 = 60 文件 / 749 @test | P4 批次 0-17 + 8 补遗/8i + 18，合计 **750 collected**（749 @test + 1 流语义回归锁） | P6-evidence/collect-only.log 750 | 吻合 |
| 批次 17 = Windows 冒烟退役批（0 文件） | P4 批次 17 = 退役 + count-tests 改写 + CI 同步；新增批次 18 = bats 删档 | 实现完成标志（P2 §6）全部达成 | 细化（非偏离） |

- 批次间执行细化（记录，非偏离）：helpers-python.bats 从 P2/P3 的批次 0 移到 P4 批次 1
  （P4 批次 0 派发范围仅 3 文件，批次 1 补齐 3 用例），总和不减；批次 17 从 P2 的「退役批」
  扩展为「退役 + count-tests 改写 + CI 同步」，并新增批次 18（bats 删档）落实 P2 §6
  「tests/ 下无 .bats 残留」标志——均为设计内执行细化。
- P3 §2 test_code_dir（agate/tests/）与 P4 implementation_dir（agate/tests/）一致；
  P3 §4 覆盖映射（60 bats → 60 test_*.py）与 P4 实际文件数（60）一致。

### 3.4 文档重写（P1 §5 表 E）核对

- 0 bats 引用（实测 `grep -c '\.bats\|bats '` = 0）：AGENTS.md（仓库根）、agate/platform-notes.md、
  agate/SETUP.md、agate/git-integration.md、agate/tests/README.md、agate/assets/templates/handoff-template.md、
  agate/assets/review-roles/protocol-alignment-review.md——表 E 对应项已落地。
- UPGRADING.md 9 处 bats 引用全部位于 v0.47.0 迁移章节（旧→新命令对照表，P1 表 E「新增本版本
  迁移章节」要求）与历史版本记录（L192/203/205，按「历史记录保留不重写」口径），属预期保留。
- scripts/README.md L38 扫描器扩展名枚举 `.bats/.bash/.sh/.py`（P4 批次 18 判定保留，扫描器
  通用性，bats 删除后自然零命中）+ L3「退役」注记——预期保留。
- formatters/README.md L53 `bats | generic-tap.sh` 行按 P2 §3.7「保留」决策保留——预期。
- **[DEVIATION: agate/dispatch-protocol.md L878 仍含「测试类证据（pytest/bats 结果）：CI 天然可行」
  ——P1 §5 表 E 明确要求「第 875/878 行「pytest/bats 结果」表述 → 统一 pytest」；L875 已统一为
  「如 pytest 结果路径」，L878 未同步。非功能性、不影响任何 BDD/gate 判定（consistency --strict
  仍 0 ERROR，env-adapt-docs 9 passed），属文档重写残留，建议 P8 发布前顺手统一为「pytest」。]**
- CI 同步：protocol-tests.yml 实测 pytest job（ubuntu 全量 + windows `-m windows_smoke`）、
  ruff 目标 `agate/`、bats 安装步骤已删、check-windows-smoke 引用清除（P4 批次 17）——吻合。

### 3.5 未决项清零

- P1-requirements.md：grep 确认无行首 [NEED_CONFIRM] / [BLOCKER] / [DEVIATION-CRITICAL]；
  §8 有 `[NO_NEED_CONFIRM]` 声明；[SUGGEST] 4 项全部在 P4 落地（见 §2）。
- P5-test-results/unit.md 有 `[NO_NEED_CONFIRM]`，fail-list.txt 为空（0 失败）。
- P6-acceptance.md：pass 12 / fail 0，无「调整/跳过/覆盖」中间态；BDD-5 的「待 Windows CI 确认」
  为 P1 `requires_minimal_validation: true` + P2 §4.4 minimal_validation 的既定边界，非未决缺陷
  （P6-evidence/bdd5-windows-ci-note.md 已声明回退路径）。

## 4. 结论

- **BLOCKER = 0**，**DEVIATION-CRITICAL = 0**，DESIGN_GAP 未配对 = 0，SCOPE+ 未闭环 = 0。
- 非关键 DEVIATION = 1（§3.4：dispatch-protocol.md L878「pytest/bats 结果」文档重写残留，无功能/gate 影响）。
- 跨文件引用锚点齐备（`P2§packages` / `P4§impl-path` / `P1 BDD` 均在本报告 §3 引用），非裸「一致」。
- **P7 gate 实测判定**：`python3 agate/scripts/check-gate.py P7 $TASK_DIR` exit 0——
  blocker_count=0、deviation_critical_count=0、design_gap_count(0) ≥ design_gap_reviewed_count(0)、
  P4 声明 0 条 DESIGN_GAP 无未配对、无 [BLOCKER] / [DEVIATION-CRITICAL] 散文标记。
  输出含 1 条 T090 WARNING（§1 已述，P4 G_DG_ANCHOR 散文「DESIGN_GAP:」启发式误报，
  WARNING 不改变 exit code，gate 通过）。
