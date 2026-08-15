---
review_date: 2026-07-05
reviewer: main
review_target: >-
  commit 6c04c10 — Phase Card 计划追加 P0 hook 误拦截前置修复（issue #001）
  含 agate/docs/issues/issue-001-pre-commit-p0-block.md
  + docs/plans/agate-phase-cards-implementation-2026-07-05.md 的前置修复段
type: 专家评审（前置 bug 修复，实证驱动）
method: 逐条跑脚本核对根因 + 实测 P0 走 check-gate/check-pruning + 追 CI backstop 判定逻辑
---

# 对 issue #001 及其前置修复的专家评审

## 总判定

**根因分析准确，修复对报告的症状正确且 CI 安全（已实测）。但修复治标不治本——真正的根在 `check-gate.sh` 把 P0 当「未知阶段」，修复只让下游容忍了这个错误状态，没纠正它。** 外加一个 self-gate 纪律的过程疏漏。

---

## 一、根因声称：逐条实测，全部属实

| issue 声称 | 实测结果 |
|---|---|
| `check-pruning.sh:11` = `[ ! -f "$P1_FILE" ] && exit 2` | ✅ 第 11 行确认 |
| `pre-commit-gate.sh` 2j 节 = `check-pruning.sh \|\| exit 1` | ✅ 第 129 行确认 |
| 2i 节 `check-p6-provenance` 用正确的 `\|\| PROV_EXIT=$?` 模式 | ✅ 第 120-124 行确认 |
| 2k 节 `check-scope-resolved` 也有同样 `\|\| exit 1` 病 | ✅ 第 134 行确认 |
| P0 无 P1 → check-pruning exit 2 → 被 `\|\| exit 1` 当硬拦 | ✅ 实测 check-pruning P0 = exit 2 |

修复用 `$GATE_EXIT` 作外层守卫——**该变量在 2j 之前（第 112-113 行）确已赋值**，不是悬空引用。修复把 2j/2k 从 `|| exit 1` 改为「捕获退出码，仅 `-eq 1` 时 exit 1」，与 2i 完全对齐。**这个改动本身是对的。**

---

## 二、修复是 CI 安全的（这一点我替 issue 验证了，它没验）

issue 没检查一个关键下游：修复后 P0 commit 会写 `.gate-result.json {exit_code: 2, output: "未知阶段: P0"}`，CI 的 `ci-gate-backstop.py` 会不会把这条 exit 2 当失败？

**实测追了 backstop 逻辑**：它是**一致性检查**（防 `--no-verify` 绕过），不是「exit 必须为 0」检查。判定核心是 `recorded_exit != ci_exit → FAIL`。P0 走 check-gate 是**确定性 exit 2**（永远命中默认分支），本地记录 2、CI 重跑也 2 → 一致 → **PASS**。

所以修复不会在 CI 侧翻车。**结论：报告的症状被完整修复。** 这部分可以放心推进。

---

## 三、真正的根：check-gate 把标准阶段 P0 当「未知阶段」

issue 第 51 行自己记了这条线索（`.gate-result.json → exit_code: 2, output: "未知阶段: P0"`），但修复没往下追。

**实测确认**：`check-gate.sh` 的 `case "$PHASE"` 从 `P1)` 开始，**P0 根本不是一个 case**，直接落到 `*) echo "未知阶段: $PHASE"; exit 2`。

```
$ bash agate/scripts/check-gate.sh P0 <p0-task>
未知阶段: P0
→ exit 2
```

问题在于：**P0 是协议明确定义的标准阶段**（issue 自己引 WORKFLOW.md 阶段总览表第 1 行）。让 check-gate 对一个「已知的标准阶段」输出「未知阶段」，是语义谎报。而且这条谎报会被持久化——`gate-result.sh` 不仅写 `.gate-result.json`，还 append 到 `.gate-history.jsonl`（第 33 行）。**每次任务立项都会在审计轨迹里留一条「未知阶段: P0」**，误导任何读历史的人。

这直接抵触项目核心价值「honest capability documentation」。当前的 3 行修复让 P0 能过，但代价是「用下游容错掩盖上游谎报」——和当年 self-report 的 `agent` 字段被否是同一类问题：真相被一层容错糊住了。

**建议（3 行，比现修复更根治）**：在 `check-gate.sh` 加显式 `P0)` 分支：

```bash
P0)
  echo "GATE P0: 立项阶段无需脚本 gate（仅 P0-brief.md）。主 Agent 确认 P0-brief 五字段齐全即可推进 P1。" >&2
  exit 2 ;;
```

这样：
- 审计轨迹诚实（「P0 无需 gate」而非「未知阶段」）
- 2j/2k 的容错修复退化为**纵深防御**而非唯一机制
- exit 2 语义清晰（第 150 行 case 已把 exit 2 处理为「需主 Agent 手动判断」，非阻塞，天然契合）

**注意**：这个 P0 分支和 2j/2k 容错修复**都要做**——前者纠正谎报，后者防 check-pruning/check-scope 对无 P1 状态的误拦（那是独立于 check-gate 的两条路径）。只做 P0 分支不够（check-pruning 仍会 exit 2 被 `|| exit 1` 拦）；只做 2j/2k 不够（审计轨迹仍谎报）。

---

## 四、过程疏漏：本次 commit 触发 self-gate 但无 skip 理由

commit 6c04c10 新增了 `agate/docs/issues/issue-001-pre-commit-p0-block.md`。

**实测**：该路径命中 self-gate 触发正则（`agate/.+/.*\.md`）→ commit-msg-self-gate.sh 应吐 WARNING。但本次 commit message **不含** `self-gate-review:` 或 `self-gate-skip:`。

这是一份 bug 报告文档、非协议规则变更，本应带一句 `self-gate-skip: bug 报告，无协议规则变更` 来正当地跳过。WARNING 不阻塞所以 commit 过了，但这正是 self-gate「强制力边界」文档里担心的场景——**主 Agent 忽略 WARNING 直接 commit**。一次两次是疏忽，成习惯就是机制形同虚设。

（顺带印证了已知的 `self-gate-review:` 缺 `^` 锚假阴性：即便当时写了 review 路径，body 里随便一提也会被误判为已审。计划 step 5 已把「顺手修 `^` 锚」纳入，方向对。）

---

## 五、计划文档侧的修订：干净

前置修复以「独立 bug，不影响卡片架构」正确定位，节奏表插入 `0a`（前置修复）→ `0b`（基准验证），顺序合理。这个 bug 确实必须先修——否则卡片模式下每个新任务立项（P0）都会被拦，验证都没法起步。

唯一建议：把三节里「修复」的描述从「2j/2k 容错」扩到「check-gate 加 P0 分支 + 2j/2k 容错」，对齐第三节的根治方案。

---

## 建议清单

| # | 动作 | severity |
|---|------|----------|
| 1 | `check-gate.sh` 加显式 `P0)` 分支，停止把标准阶段谎报为「未知阶段」（污染 .gate-history 审计轨迹） | 中（诚实性） |
| 2 | 保留 2j/2k 的容错修复作为纵深防御（与 #1 都做，不是二选一） | 已在计划，正确 |
| 3 | 补一条测试：P0 任务（仅 P0-brief，无 P1）走 pre-commit 应通过 + check-gate P0 输出不含「未知」 | 中 |
| 4 | 本类触发 `agate/**.md` 的 commit 养成带 `self-gate-skip: <理由>` 的习惯 | 低（纪律） |
| 5 | 计划第三节描述扩为「P0 分支 + 2j/2k 容错」 | 低 |

## 一句话结论

**修复对症、CI 安全、可以推进**；但它靠「下游容忍上游的错误状态」达成，没纠正 check-gate 把 P0 谎报为「未知阶段」这个根——那条谎报正落进审计轨迹，撞项目的诚实底线。加 3 行 P0 分支即可根治，与现容错修复并存。
