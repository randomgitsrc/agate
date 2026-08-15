---
review_date: 2026-07-05
reviewer: main
review_target: docs/plans/agate-commit-strategy-2026-07-05.md
type: 专家评审（设计方案，实证驱动）
method: 核实 check-state-transition.sh 现有基础设施 + 静态求值 _phase_output_for 各分支 + 核对 P4/P5 产出形态
---

# 「逐阶段 commit 强制 + 拦截后处理」方案评审

## 总判定

**方向正确、踩在已有文档教训（T019）上、基础设施现成——但把伪代码真跑一遍后发现：方案宣称的核心能力「忘记 commit → 拦截」是坏的，`git ls-files` 退出码 bug 让那个检查永不触发。** 加上 P4 无 gate、跨任务误匹配、覆盖声称 > 实际交付。

**关键结论（实测五场景）**：方案「如写」唯一真正拦住的只有「产出和推进塞进同一 commit」——比「防止忘记」弱得多。它宣称要防的「忘记 commit」恰恰防不住。以下 F0 是最高优先级，排在原 P4 gap 之前。

---

## 〇、F0（命门 bug，实测暴露）：line 47 的「从未 commit」检查永不触发

方案的**核心承诺**是"推进 phase 时，前阶段产出没 commit 就拦"。这个承诺全靠 line 47：

```bash
if [ -n "$OLD_OUTPUT" ] && ! git ls-files "$TASK_REL/$OLD_OUTPUT" >/dev/null 2>&1; then
    echo "GATE: ${OLD_PHASE} 产出 ${OLD_OUTPUT} 尚未 commit"; exit 1;
fi
```

**实测 `git ls-files <未跟踪文件>` 的退出码是 0**（只是输出为空）：

```
$ git ls-files "docs/tasks/T1/P1-requirements.md" >/dev/null 2>&1; echo $?
0    ← 文件根本没跟踪，退出码仍是 0
```

所以 `! git ls-files ... >/dev/null` = `!(退出 0)` = `!true` = **false → 永不触发**。

**把伪代码原样实现跑五场景**：

| 场景 | 应然 | 实测 |
|------|------|------|
| 正常：P1 产出已 commit → 推进 P1→P2 | 放行 | ✅ 放行 |
| **忘记：P1 产出从未 commit → 推进 P1→P2** | **拦** | ❌ **放行（F0）** |
| 产出+推进同一 commit | 拦 | ✅ 拦（line 41，唯一真拦的） |
| **P4 忘记 commit 代码 → 推进 P4→P5** | 拦 | ❌ 放行（F1，见下） |
| 批量·不推进 phase（phase 停 P1） | （范围外） | 放行（F3） |

**后果**：方案本是照 T019 教训（状态标记先于现实）建的，却因这个 bug **在最该防的地方复现 T019**——`.state.yaml` 标 P2，而 P1 产出根本不存在，一路放行。宣称的核心能力被打穿。

**修法**：判断输出是否为空，而非退出码：

```bash
if [ -n "$OLD_OUTPUT" ] && [ -z "$(git ls-files "$TASK_REL/$OLD_OUTPUT")" ]; then
    echo "GATE: ${OLD_PHASE} 产出 ${OLD_OUTPUT} 尚未 commit"; exit 1;
fi
```

**这个 bug 静态读代码看不出**——伪代码"看起来"在查跟踪状态，实际 `git ls-files` 的退出码语义让取反永不成立。只有把伪代码真跑一遍才暴露。正是项目一贯的"跑一次才知道"。

---

## 补记（2026-07-05 修订复审）：F0 真修好，但 F1 是「伪装的修复」

计划据本评审出了修订版（commit 848e8a0）。**把修订版伪代码原样再跑一遍**：

| 发现 | 纸面 | 实测（跑修订版伪代码） |
|------|------|----------------------|
| **F0** git ls-files 判空 | 改了 | ✅ **真修好**——场景2「P1 从未 commit → 推进 P1→P2」现 GATE 拦截 |
| **F1** P4 代码检查 | "改了" | ❌ **假修**——见下 |
| **F2** 限定 `^TASK_REL/` | 改了 | ✅ |
| **F3** 覆盖列诚实标注 | 加了 | ✅ |
| **F4** 抽共享映射 | 加备注 | ✅ 方向对 |

### F1 假修：P4 分支引用未定义函数，fail-open 到 PASS

修订把 `P4) return 0` 改成 `P4) ;;` + 新增一个 P4 block：

```bash
if [ "$OLD_PHASE" = "P4" ]; then
    if _phase_code_staged && ! _phase_code_committed; then
        echo "GATE: P4 代码产出尚未 commit" >&2; exit 1; fi
fi
```

**实测**：`_phase_code_staged` / `_phase_code_committed` **全库无定义**（grep agate/scripts/ 无结果）。跑起来 → `command not found` → `if` 条件为假 → **P4→P5 仍放行（退出码 0）**。

**比原来的 `return 0` 更糟**：原来诚实地空着（一眼看出没做），现在挂了个引用空函数的 block，fail-open 到 PASS，**看起来解决了**。

### 而 `_phase_code_committed` 恰是真难点，且 v0.9.1 无可复用

计划说"复用 v0.9.1 dispatch-context 的代码文件判断"。但实测 v0.9.1（pre-commit-gate.sh:181）的 P4 判断**只查 staged**：

```bash
[ "$PHASE" = "P4" ] && echo "$STAGED_IN_TASK" | grep -qvE '\.(md|yaml)$|^\.state'
```

**v0.9.1 没有"已 commit"这个 helper**——`_phase_code_committed` 得**新写**，而它是真难点：

- v0.9.1 的 `STAGED_IN_TASK` 限定 `^${TASK_REL}/`（task dir 内）
- 但 P4 是 implementer 产出**实现代码**，代码通常在项目 `src/`——**在 task dir 之外、任意路径**
- 若代码在 task dir 内 → 可查 `git ls-files "$TASK_REL/" | grep -v 文档`
- 若在 `src/` → **根本无法和这个 task 关联**，"P4 代码是否已 commit"无从判起

计划把这个前置难题（P4 代码在哪、怎么和 task 关联）**藏进一个未定义函数 + 一句"复用 v0.9.1"**，但 v0.9.1 没这东西可复用。

### 必须做

- **要么老实定义 `_phase_code_committed`**，但先回答"P4 实现代码的位置约定"——如果 agate 不强制 P4 代码落在 task dir，这个检查在架构上就做不出可靠版本
- **要么诚实承认 P4 代码-commit 检测是难点、显式 scope 出去**（像"范围外"那节那样），别用假函数糊成"已解决"

**F1 又是"看着修了、跑才知道没修"，与 F0 同类。** 修订复审的教训：修复也要跑验证，尤其"复用现有函数"这类声称——先确认那个函数真存在、真能复用，别假设。

---

## 一、基础设施核实：假设大多成立

| 伪代码假设 | 实测 |
|-----------|------|
| `$OLD_PHASE`/`$NEW_PHASE` 可得 | ✅ check-state-transition.sh:25 已 `git show HEAD:.state.yaml` 读旧 phase；新 phase 在 staged 版本 |
| 脚本只在 phase 变更时跑 | ✅ :50 `git diff --cached \| grep .state.yaml \|\| exit 0` |
| 在 pre-commit 生效 | ✅ pre-commit-gate.sh:67 调用 |

所以"旧/新 phase 从哪来"的鸡生蛋不成立——现成。方案是在现有脚本上加逻辑，合理。

**且方案有据**：state-machine.md:535 记的 T019 教训——".state.yaml 标 P5 但 P5-test-results/ 不存在，状态标记先于验证"。本方案本质是把 T019 的"标记绑定验证"从单点推广到所有转移（推进 phase 绑定前阶段产出已 commit）。有出处，不是拍脑袋。

---

## 二、F1（确凿 gap）：P4→P5 推进完全没有 commit gate

伪代码 line 70：

```bash
P4) return 0 ;;  # P4 产出是代码文件，不在单一 .md 产物，用暂存区代码检查
```

**静态求值**：`OLD_OUTPUT=$(_phase_output_for P4)` → `return 0` 不 echo 任何东西 → `OLD_OUTPUT=""`。而后面两个检查都以 `[ -n "$OLD_OUTPUT" ]` 为前提：

```bash
if [ -n "$OLD_OUTPUT" ] && ...   # 空串 → 整条跳过
```

→ **P4→P5 推进不触发任何 commit gate。** 注释说"用暂存区代码检查"，但伪代码**根本没实现这个检查**——只是 `return 0` 空手而归。

**为什么这是最重要的 gap**：P4 是实现阶段，是全流程最高价值、最该保证"产出已 commit 再推进"的一环。恰恰是它被漏掉了。而且现成的参照就在隔壁——v0.9.1 的 dispatch-context 强制化里，P4 用的是"暂存区含非 .md/.yaml/.state 文件（代码）"判断：

```bash
# pre-commit-gate.sh 里已有的 P4 判断
[ "$PHASE" = "P4" ] && echo "$STAGED_IN_TASK" | grep -qvE '\.(md|yaml)$|^\.state'
```

本方案的 P4 分支应复用同一套代码文件判断，而不是 `return 0`。

---

## 三、F2（跨任务误匹配）：line 41 与 line 47 作用域不一致

```bash
# line 41：全局 grep，不限任务
git diff --cached --name-only | grep -q "$OLD_OUTPUT"
# line 47：限定到本任务
git ls-files "$TASK_REL/$OLD_OUTPUT"
```

line 41 在**所有** staged 文件里 grep `P1-requirements.md`——多任务场景下会匹配到**另一个任务**的同名产出，误判"本任务旧产出已 staged"。line 47 却正确限定了 `$TASK_REL/`。两者应统一：line 41 也 anchor 到 `^${TASK_REL}/`。

```bash
git diff --cached --name-only | grep -q "^${TASK_REL}/${OLD_OUTPUT}"
```

---

## 四、F3（覆盖 < 问题表声称）：又一个 nudge-vs-barrier 诚实问题

顶部"问题"表把"中间 gate 绕过"和"dispatch-context 跳过"标为**高**，暗示本方案解决它们。但本机制**只在 agent 诚实推进 .state.yaml phase 时**触发——它 gate 的是"推进 phase → 前阶段产出必须已 commit"。

方案自己在"不解决问题"（line 112-113）诚实承认了逃逸路径：**agent 一直把 .state.yaml 停在 P1，实际做 P4 的工作，最后一次性 commit**。这种批量 agent **从不推进 phase**，所以 commit gate 从不触发，dispatch-context 强制化（也 key 在 phase 字段上）同样不触发——**问题表里那两个"高"对这种 agent 完全没被解决。**

这是贯穿整条 Phase Card 线的老命题：**机制只对"诚实按阶段前进"的 agent 是 barrier，对"主 Agent 撒谎 phase 字段"的是空气**——归根到底是 issue #003 主 Agent 单点故障。方案把它 scope out 是对的，但**问题表的措辞应与机制实际覆盖对齐**：本机制是"诚实推进时的 commit 纪律"，不是"批量 commit 防护"。建议把问题表的"高"项标注为"仅当 agent 诚实推进 phase 时缓解"，别让读者以为高危项已解决。

---

## 五、F4（结构）：phase→产出映射出现第二份，会漂移

本方案的 `_phase_output_for`（P1→P1-requirements.md…）与 v0.9.1 pre-commit-gate.sh 里的 `PHASE_OUTPUT` case（P1→P1-requirements\.md…）是**同一个映射的第二份拷贝**。两处独立维护 → 迟早漂移，正是项目反复警惕的"规则文档化但两处不同步"。

**建议**：把 phase→产出映射抽成**一个** shared 函数（如 `agate/scripts/lib/phase-outputs.sh`），两个 gate 都 source 它。否则将来改一处忘另一处，两个 gate 对"什么是 P3 产出"会各执一词。

---

## 六、正面

1. **有据**：T019 教训的合理推广（标记绑定验证）。
2. **基础设施现成**：复用 check-state-transition.sh 的 HEAD/staged diff 机制，不新造轮子。
3. **"不解决问题"诚实**：明说批量-不推进-phase 的逃逸路径，归给 issue #003。
4. **拦截后处理表 + retry-3→PAUSED** 是有用的运维补强，尤其"绝对不能"三条（--no-verify / 凑条件 / 伪造证据）直接对齐项目的诚实底线。
5. **范围外**（批量检测/squash）划得清楚——批量检测误检风险大，避开是对的。

---

## 建议清单

| # | 建议 | severity |
|---|------|----------|
| 0 | **修 line 47：`[ -z "$(git ls-files …)" ]` 判空，别用 `! git ls-files … >/dev/null`（退出码恒 0，检查永不触发）** | **最高（核心能力失效）** |
| 1 | 实现 P4 分支的代码文件检查（复用 pre-commit-gate.sh 的 `grep -qvE '\.(md\|yaml)$\|^\.state'`），别 `return 0` 留空 gate | 高（最高价值阶段漏 gate） |
| 2 | line 41 anchor 到 `^${TASK_REL}/`，与 line 47 作用域一致，防跨任务误匹配 | 中 |
| 3 | 问题表"高"项标注"仅诚实推进 phase 时缓解"，与机制实际覆盖对齐 | 中（诚实） |
| 4 | phase→产出映射抽成 shared 函数，两个 gate 共用，防漂移 | 中（结构） |
| 5 | P5 目录级检查：`git ls-files "$TASK_REL/P5-test-results"` 对目录可用，但显式确认 grep/ls-files 对目录路径的行为，加一条目录场景测试 | 低 |

## 一句话结论

**方向对、有据（T019）、基础设施现成，但把伪代码真跑一遍后，方案宣称的核心能力「忘记 commit → 拦截」是坏的**——line 47 的 `git ls-files` 退出码 bug 让它永不触发，方案「如写」只拦得住「产出+推进同一 commit」这一种弱得多的情况。**先修 F0（判空而非判退出码）恢复核心能力，再补 F1（P4 代码检查）**，然后修跨任务误匹配、合并 phase→产出映射防漂移、问题表覆盖对齐。F0+F1 不修，这个方案挂着"强制 commit"的名，实际几乎什么都拦不住。
