---
phase: P7
task_id: TAG0008
type: consistency
parent: P2-design.md
trace_id: TAG0008-P7-20260816
status: approved
created: 2026-08-16
agent: consistency-reviewer
# ── v2.0 机器计数 ──
blocker_count: 0
deviation_count: 0
deviation_critical_count: 0
design_gap_count: 8
design_gap_reviewed_count: 8
---

# P7 — 一致性审查：agate 版本管理机制（v1）

> trace：TAG0008-P7-20260816（consistency-reviewer）。交叉核对 P1-P6 全部产出
> （P1-requirements / P2-design + P2-review / P3-test-cases ×3 分批 / P4-implementation ×3 批 +
> P4-review 三件套 / P5-test-results / P6-acceptance + P6-evidence/）。只读审查，
> 未修改任何代码/文档，仅产出本文件 `[PROD_NOT_TOUCHED]`。
> 8 条 DESIGN_GAP 全部转抄 + REVIEWED 配对；无 [BLOCKER] / [DEVIATION-CRITICAL]。
> **结论：status: approved**（BLOCKER=0，DEVIATION-CRITICAL=0，DESIGN_GAP 配对 8/8）。

---

## 1. DESIGN_GAP 配对（8/8，gate 硬校验）

> P4 声明 8 条（3 resolve-chain + 4 install + 1 offline），本文件逐条转抄原标记行 + 配
> `[DESIGN_GAP_REVIEWED: 已确认/已打回 P2]`。3 条 resolve-chain 已由 P2 plan-eng-review
> 评估方向可接受（P2-review.md 决策点 1/4 + 非阻塞 2/7 对应）；4 条 install + 1 条 offline
> 由本审查员独立复核。

### 1.1 resolve-chain 批（3 条，来源 P4-implementation.md §3）

- [DESIGN_GAP: P2 §4.1 层 4「legacy 软链兜底」仅用于 agate-resolve/summary；resolve-entry（hook 链）与 resolve_agate_root 的终态兜底用「脚本路径上溯 + .agate-root 标记」而非 ~/.agate legacy 解析——否则 copy 模式集成测试（.agate-root 指向 worktree）会被真实 ~/.agate 稳定版软链劫持，且真实 legacy 安装下脚本路径上溯与 legacy 目标等价。]
- [DESIGN_GAP_REVIEWED: 已确认——P2-review.md 决策点 4（§4.1 层 4 与 BDD-30 对齐）与非阻塞 2（resolve-entry 用 readlink 自定位，AGATE_ROOT env 只进 resolve_agate_root 第 1 层）已预评此方向；BDD-30 验收（P6 PASS，agate-resolve 路径）与 P6-evidence/bdd30-legacy.log 实测一致，resolve-entry 走脚本路径上溯不违反 BDD-30 语义。P2 §4.1 层 4 文字表述未同步修订，属文档漂移但 P8 文档联动一并处理（见 §3.5）。]

- [DESIGN_GAP: P2 §4.4「3 内联脚本统一归口 agate_common.resolve_agate_root」保留了 agate_common 不可用（脚本被独立复制、agate_common 不在同目录）时的内联兜底（env → 脚本路径上溯）——既有 test_agate_next_card.py 的 standalone-copy 场景（test_nc_root_2 等）只复制脚本本身，无 agate_common 可 import；兜底仅在 import 失败时生效，不改变归口主路径。]
- [DESIGN_GAP_REVIEWED: 已确认——P2-review.md 决策点 1 已评估归口方案成立（pyyaml 依赖 fail-closed 可接受，3 脚本当前零 agate_common import 为纯加法）；本 GAP 是归口主路径之外的独立复制兜底，不违背 §4.4 决策，且不引入静默降级（import 失败才触发，兜底仍走 env→上溯既有语义）。]

- [DESIGN_GAP: 3 hook 薄壳改用 `ENTRY_ROOT`（非 `AGATE_ROOT`）承载自定位结果——bash 从环境继承的 AGATE_ROOT 具 exported 属性，薄壳内 `AGATE_ROOT=${AGATE_ROOT:-...}` 赋值会保留该属性并泄漏给 resolve-entry，使其 env 覆盖恒触发而绕过项目版本解析；换名后用户显式 AGATE_ROOT env 仍原样透传（BDD-12 语义保留）。]
- [DESIGN_GAP_REVIEWED: 已确认——P2-review.md 非阻塞 2 正是此问题的设计预判（"resolve-entry 的位置用 readlink 自定位，AGATE_ROOT env 只进 resolve_agate_root 第 1 层"）；实现以 ENTRY_ROOT 换名落地，实测 pre-commit-gate.sh 自定位经 ENTRY_ROOT + exec resolve-entry.py pre-commit，用户显式 AGATE_ROOT env 仍进入 resolve_agate_root 第 1 层（BDD-12 PASS，P6-evidence/bdd12-resolve.log）。]

### 1.2 install 批（4 条，来源 P4-implementation-install.md §DESIGN_GAP）

- [DESIGN_GAP: P2 §4.5 未指明 repo URL 来源（P3 §5 备注确认），AGATE_REPO_URL 未设置时默认采用仓库 canonical URL https://github.com/randomgitsrc/agate]
- [DESIGN_GAP_REVIEWED: 已确认（本审查员独立复核）——P2 §4.5 "repo 单克隆" 未定义 URL 来源，P3-install §5 引入 AGATE_REPO_URL 为测试隔离环境契约；默认 canonical URL 是合理补全，无 BDD 冲突（BDD-1/2 经 AGATE_REPO_URL 注入本地 repo 验证，P6 PASS）。]

- [DESIGN_GAP: P2 §4.5 "mtime 合理限流" 未给具体参数，实现采用深度 ≤4 + 跳过隐藏/.agate/.git 等目录 + mtime 窗口 365 天]
- [DESIGN_GAP_REVIEWED: 已确认（本审查员独立复核）——P2-review 决策点 3 已提示 bounded-scan 漏扫风险并列为非阻塞；实现采用限流参数，BDD-6（正常深度引用）PASS（P6-evidence/bdd6-uninstall.log）。残余风险（限流边界外引用漏扫→卸载误放行）已由 cso P4-review MEDIUM-3 记录为接受项（建议限流命中时 stderr WARNING），非本任务阻塞。]

- [DESIGN_GAP: P2 §4.5 未给 worktree remove 失败策略，实现采用 remove 失败后 --force 兜底 + rmtree + git worktree prune]
- [DESIGN_GAP_REVIEWED: 已确认（本审查员独立复核）——P2 §4.5 未定义 remove 失败路径，--force + rmtree + prune 是合理兜底（MV 已核实 worktree 重复 add exit 128，故先判存在）；BDD-5 PAss 红线验证（P6-evidence/bdd5-uninstall.log, bdd5-after.txt），不悬空指针。]

- [DESIGN_GAP: P2 §4.5 "最新发布 tag" 未给确定方法，实现采用 git tag --sort=-version:refname 过滤 vX.Y.Z 取首项]
- [DESIGN_GAP_REVIEWED: 已确认（本审查员独立复核）——P2 §4.5 "装 latest 指针（最新发布 tag）" 未给取法；`git tag --sort=-version:refname` 过滤 vX.Y.Z 与 P2 §7 MV 验证的 tag 语义一致，BDD-1/4 PASS（P6-evidence/bdd1-install.log, bdd4-pointers.txt）。]

### 1.3 offline 批（1 条，来源 P4-implementation-offline.md §未解决的 DESIGN_GAP）

- [DESIGN_GAP: P3-test-cases-offline.md 声明"pack 与 install 应共享 agate_common 工具函数（依赖 resolve-chain 批）"，但 resolve-chain 批交付的 agate_common.py（438 行）未含 sha256/目录 hash 工具；本批约束"只新建 2 个脚本、不得修改 agate_common.py"，故在 pack/install 两侧各自实现了**相同约定**的 compute_sha256（目录=排序逐文件 hash 拼接再整体 hash），未通过 agate_common 共享。若后续期望共享，需在 agate_common.py 补一个 hash 工具并让两侧 import]
- [DESIGN_GAP_REVIEWED: 已确认（本审查员独立复核）——与 P3 声明的"共享 agate_common 工具"期望不符，但两侧按相同约定实现且端到端验证通过：BDD-22/23（manifest sha256 64 hex）与 BDD-26（篡改后校验失败）均 PAss（P6-evidence/bdd22-pack-reallog.log, bdd23-manifest-real.txt, bdd26-checksum-mismatch.log）。功能正确，无 BDD 冲突；双实现漂移风险已由 P4-review-eng INFORMATIONAL 8 显式跟踪，非本任务阻塞（记录为已知结构性局限，P8 可决定是否归口 agate_common）。]

---

## 2. SCOPE+ 闭环

- **无 [SCOPE+] 声明**：全 P1-P6 产出无行首 `[SCOPE+]` 标记。P4-implementation-install.md §SCOPE 标注（L67-68）明确声明"本批无新隐含需求（无行首 [SCOPE+] 标记）"（L67 的 `- [SCOPE_GAP]：无` 为"无 SCOPE_GAP"声明，非 SCOPE+）；P4-implementation-offline.md L52 "未发现 [SCOPE_GAP] / [SCOPE+]"。
- P1-requirements.md §5 为 `[NO_NEED_CONFIRM]`（L344），无阻塞项/方向分歧待 P2 裁决。
- **结论**：无 SCOPE+ → 无 [SCOPE_RESOLVED] 要求（check-scope-resolved.py 无命中即 exit 0）；若 P8 文档联动引入新需求按 P1 §8 活基线机制回写。

## 3. 跨文件一致性检查

### 3.1 P1 BDD 数 vs P6 验收结果 vs P3 测试用例数

- P1 §4 BDD-1~BDD-31（P1-requirements.md:165-331）编号连续，共 **31 条**。
- P6-acceptance.md frontmatter：`pass: 31, fail: 0`（P6-acceptance.md:11-12），逐条 PASS 含 P6-evidence/ 证据引用，PASS+FAIL=31 **= P1 31 条** ✓。
- P3-test-cases.md §1：6 测试文件 36 用例（resolve 17 + install 8 + offline 11，P3-test-cases.md:26-31）≥ 31 ✓（用例数 ≥ BDD 数为预期，参数化/平台变体所致）。
- **P1§4 BDD / P3 §1 / P6 frontmatter** 三向数量一致。

### 3.2 P2 packages vs P8 bump 范围

- **P2§packages**（P2-design.md:12 `packages: [agate]`，§3.1 L125 明确"agate 协议/脚本/docs 单包发布（P8 单版本 bump，无多包版本分叉）"）。
- P1 frontmatter packages 列的是受影响的文件清单（12 项，含 install.sh/docs），非发布包单元；P2 以 `[agate]` 单包聚合。P8 应做**单包版本 bump**（README badge / CHANGELOG / version 文件 / UPGRADING 章节），与 **P2 packages=[agate]** 一致，无多包分叉。

### 3.3 P2 方案 vs P4 实现路径

| P2 设计 | P4 实现 | 验证 |
|---------|---------|------|
| **P2§4.1** 版本解析四层语义 | agate-resolve.py + agate_common `resolve_version_root`/`resolve_hook_root`（P4-implementation.md §1） | 文件在盘；BDD-9~14 PASS（P6） |
| **P2§4.3** resolve-entry 固定入口 + 3 hook 薄壳 exec 目标改 | resolve-entry.py + 3 薄壳 ENTRY_ROOT 自定位（P4-implementation.md §1 + DESIGN_GAP 3） | pre-commit-gate.sh:16 `exec "$PY" "$ENTRY_ROOT/scripts/resolve-entry.py" pre-commit`；BDD-15~19 PASS（P6） |
| **P2§4.3** install-hook 装固定入口 + 复制模式 | install-hook.py 校验 resolve-entry 存在 + `.agate-root` 标记保留（P4-implementation.md §1） | BDD-15/19 PASS（P6） |
| **P2§4.5** agate-install（install/uninstall/--check） | agate-install.py（install 批，P4-implementation-install.md） | BDD-1~8 PASS（P6） |
| **P2§4.6** summary 显示解析版本 + 原因 | agate-summary.py 语义迁移（P4-implementation.md §1） | BDD-20/21 PASS（P6） |
| **P2§4.4** 3 内联脚本归口 agate_common | agate-inject-card / agate-next-card / agate-render-dispatch-prompt 归口（P4-implementation.md §1 + DESIGN_GAP 2 兜底） | 三脚本在 diff（git diff 640607c..HEAD）；回归 unit 679 passed（P4 自查） |
| **P2§4.7** pack-offline / install-offline | agate-pack-offline.py + install-offline.py（offline 批，P4-implementation-offline.md） | BDD-22~29 PASS（P6） |
| **P2§1.4** gate 判定逻辑不改（BDD-31） | check-gate.py / pre-commit-gate.py / commit-msg-self-gate.py / pre-push-gate.py / ci-gate-backstop.py **零改动** | `git diff 640607c..HEAD` 对 5 个 gate 判定脚本无输出（本审查员实跑确认）；仅 3 个 .sh 薄壳各改 19 行（exec 目标改 resolve-entry，属解析层） |

- 5 个新脚本（agate-resolve.py / resolve-entry.py / agate-install.py / agate-pack-offline.py / install-offline.py）全部落地于 `agate/scripts/`（P4 §1 声明路径，本审查员 ls 实查存在）。
- **P2§4 / P4§1 实现路径**全部吻合，无方案级偏离。

### 3.4 P2 gate_commands vs P5 执行结果

- **P2§gate_commands**（P2-design.md:129-139）固化 4 条 P5 命令：P5 / P5_unit / P5_consistency / P5_count。
- P5-test-results/unit.md §命令明细逐条执行：P5 → 823 passed（L32-38）；P5_unit → 29 passed（L42-50）；P5_consistency → 0 ERROR（L54-62）；P5_count → 825（L66-73）。4 条命令**全部执行且 exit 0**（L80 EXIT_CODE: 0）✓。
- 注：P5_unit 定向列表（4 个文件）不含 test_hook_resolve_entry / pack-offline / install-offline——与 P2-review 测试缺口 4 预判一致（离线/hook 测试依赖全量 P5 覆盖，P6 已用 pytest 佐证补齐：hook 集成 58 用例 + 离线 15 用例）。**P2§gate_commands / P5 执行结果**数量与结果吻合。

### 3.5 影响面表（P1 §2）vs P4 改动清单

- **P1§2.1 脚本层**：P4 实现全部落地——3 hook 薄壳改（改）、install-hook 改、agate_common 集成、agate-summary 语义迁移、3 内联脚本归口、4 新脚本新增。`ci-gate-backstop.py`（复核不改）与 `pre-commit-gate.py` 等（判定不改，BDD-31）按 P2 结论未动 ✓。
- **P1§2.2 文档层**：**P4 未落地（预期状态，非缺陷）**——README / README.zh-CN / SETUP / UPGRADING / platform-notes / AGENTS / WORKFLOW / orchestrator-template / adr / project.md / install.sh / 等文档联动均未改。dispatch-context 明确"文档层改动……这是 P8 发布节的事，需在 P7 明确标注（不阻塞）"。
- **P1§2.3 测试层**：6 新测试文件落地（resolve 3 + install 1 + offline 2，本审查员 ls 实查），test_install_hook.py / integration hook 测试经 P4 修正（P4-implementation.md §2 测试修正 3 处，均对齐 P3 设计文档行为）✓。
- **⚠️ P8 承接项（非阻塞，需 P8 显式处理）**：
  1. **agate/scripts/README.md**（P1 §2.1 L91 + P2 §1.1）：新增 4 脚本入清单 + resolve-entry 解析入口说明——P4 未改（grep 无新脚本名）。
  2. **check-protocol-consistency.py SCRIPT_REF_RE 白名单**（P2 §1.1）：补 install-offline.py / resolve-entry.py 等新脚本名——P4 未改（本审查员读 L771-775 确认白名单正则不含 install-offline / resolve-entry）。当前 P5 consistency 0 ERROR 不受影响（新脚本均存在、协议文档面尚无这些脚本名的悬空引用），但 P8 更新文档引用新脚本名后，正则不覆盖 install-offline.py / resolve-entry.py 会导致 CHECK 10 无法校验这两个脚本名的引用漂移——建议 P8 顺带补入白名单（属命名联动，不改变判定逻辑）。
  3. **P1 §2.2 全部文档联动点**（13 项）：P8 发布步骤处理，含 UPGRADING 破坏性变更章节（.agate-version 语法 / ~/.agate 目录化 / 解析入口迁移）。

### 3.6 未决项清零

- P1-requirements.md §5 为 `[NO_NEED_CONFIRM]`（L344），**无行首 [NEED_CONFIRM]**；P1-P6 全部产出 **无 [BLOCKER] / [DEVIATION-CRITICAL] 行首标记**（grep 实查确认）。
- P4-review 三件套 status 均 approved（P4-review.md / -eng.md / -cso.md），3 CRITICAL 修复闭环 + 回归测试；P4-review 遗留项（MEDIUM-2/3 + INFORMATIONAL + LOW）均不阻塞、作为 backlog 记录。
- P2-review status approved；P2-review 8 项非阻塞契约澄清 + 5 项测试缺口已在 P3/P4 处理（测试缺口 1 → test_resolve_terminal_failure_fail_closed；缺口 4 → P6 pytest 佐证补齐；缺口 5 → BDD-31 由 git diff 判定，本审查员已实跑确认）。

---

## 4. 检查清单完成确认

| # | 检查项 | 结论 | 证据锚点 |
|---|--------|------|----------|
| 1 | DESIGN_GAP 配对 | 8/8 全部转抄 + REVIEWED | P4-implementation.md §3 / P4-implementation-install.md §DESIGN_GAP / P4-implementation-offline.md §未解决 + 本文件 §1 |
| 2 | SCOPE+ 闭环 | 无 SCOPE+，无 SCOPE_RESOLVED 要求 | P1 §5 [NO_NEED_CONFIRM] / P4-implementation-install.md §SCOPE 标注 |
| 3 | 跨文件一致性 | 全部吻合（见 §3.1~3.5） | P1§4 BDD / P2§packages / P2§gate_commands / P1§2 影响面 vs P4 改动清单 |
| 4 | 未决项清零 | 无残留 NEED_CONFIRM / BLOCKER / DEVIATION-CRITICAL | grep 实查 P1-P6 |
| 5 | frontmatter 机器计数 | blocker=0, deviation=0, devcrit=0, dg=8, dg_reviewed=8 | 本文件 Header |

---

## 5. 门槛对照

- [x] P7-consistency.md 存在且非空
- [x] 8 条 [DESIGN_GAP] 全部转抄 + [DESIGN_GAP_REVIEWED] 配对（8/8）
- [x] 无 [BLOCKER] / [DEVIATION-CRITICAL]
- [x] 跨文件检查项含源文件节名引用（P1§4 BDD / P2§packages / P2§gate_commands / P1§2 / P4§1）
- [x] frontmatter 机器计数与正文一致（blocker_count=0, deviation_count=0, deviation_critical_count=0, design_gap_count=8, design_gap_reviewed_count=8）
- [x] P8 承接项已显式标注（§3.5，非阻塞）

**Summary**: BLOCKER=0, DEVIATION-CRITICAL=0, DESIGN_GAP 配对 8/8, SCOPE+ 闭环（无）, 跨文件一致性全通过 → **status: approved**。P8 承接：文档层联动（含 scripts/README.md 清单 + check-protocol-consistency 白名单 + UPGRADING 章节）。
