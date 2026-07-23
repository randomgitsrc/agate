# Plan：回退-续作通用化制度设计 + P6 self-authored gate 代码直改硬拦截 + 多步回退自动化

> 日期：2026-07-23
> 版本影响：minor bump（v0.19.0 目录改名 PR 待落地，本 plan 暂定 v0.20.0，与目录改名 PR 相互独立、不冲突，均只涉及 `agate/scripts/`、`agate/rules/`、`agate/phase-cards/` 下的具体文件，不涉及目录结构本身）
> 破坏性变更：**有**——新增一条会 `exit 1` 硬拦截 commit 的检查（P6 阶段暂存项目源码文件），已有的、依赖"P6 阶段可以随便改代码"这个（未声明的）隐含假设的下游工作流会被拦下来，这是有意为之。另新增 `agate-retreat-to.sh` 会在执行过程中自动产生真实 `git commit`——这是本仓库现有脚本里第一个会主动提交的脚本（`check-p6-format.sh --fix` 只改文件不提交），需要在实施评审时重点核对提交时机和失败回滚行为
> 来源：用户观察到的三个真实场景 (1) P6 打回退到 P4 修复后，P5/P6 旧产出文件是否需要处理，目前协议对此完全没有规定 (2) P6 验收失败（如 20 pass/2 failed）后，主 Agent 没有走"退回重新派发"流程，而是自己直接在 P6 阶段动手改代码——这正是 `LIMITATIONS.md` 里已经点名的"主 Agent 遇到困难时倾向于自行解决而非触发安全网"根因模式（T005/T006/T016/T019 同源）(3) 多步单向回退需要手动敲多次 commit，担心这个机械负担本身会成为主 Agent 绕开正确流程、转而在原地自行修复的诱因

---

## 诚实标注

本 plan 的核心论点建立在对现有脚本的实际核实之上，不是推测：

1. `check-state-transition.sh` 的回退合法性判断（diff≥2 强制 PAUSED）已核实存在且生效，**但完全没有处理"回退之后，被跨过的那个阶段遗留的自撰产出文件该怎么办"**——我搜索了 P4/P5/P6 三张 phase-card，确认协议文档里没有任何一句话讲这件事。
2. `pre-commit-gate.sh` 的 E3 检查（`case "$PHASE" in P4|P5|P6) ;; ...`）**已实测确认**：P6 阶段暂存任意非 `.md`/`.yaml` 文件（包括真实项目源码）与 P4/P5 一样被完全放行、连 WARNING 都没有。这是本 plan 认为需要修的核心问题——P6 按 `LIMITATIONS.md` 自己的分类属于 **self-authored gate**（判定对象是主 Agent/verifier 自己写的文件），P4/P5 属于**外部产出 gate**（判定对象是测试运行器 exit code），两者风险等级不同，却共享同一条"代码文件无脑放行"规则。
3. P4、P5 均**没有**跨重试持久化的、可能过期的自撰结果文件（P4 的产出是代码本身，分散在项目任意路径，无法 task-scoped 追踪；P5 phase-card 明确不要求写 `P5-verification.md` 这类结果声明文件，只要求主 Agent 判定后直接 commit + 推进 phase）。真正有"跨阶段回退后可能过期"风险的自撰文件，只有 P1/P2/P6/P7 各自的产出文件——这与 `LIMITATIONS.md` 的 self-authored 分类完全对应，不是巧合，是同一个根因的两个表现。
4. **`agate-retreat-to.sh` 迭代过程中发现并修复了一个真实 bug**：脚本内部的 `git commit` 最初没有用 pathspec 限定范围，会把调用时暂存区里所有已暂存的内容（包括和这次 retreat 完全无关的文件）一起提交进去——已用真实 git 仓库复现（构造一个无关的 `other-project/wip.txt` 已被 `git add`，跑一遍脚本，确认它被卷进了 `retreat: P6 -> P5` 这条 commit）。已修复为 pathspec 限定的 `git commit ... -- "$TASK_DIR"`，并加了一条前置检查拒绝执行（而非默默只提交一部分）。这条问题不是这次plan 起草时就想到的，是复核阶段主动构造边界场景才发现的，记录在此，具体见问题二小节。
5. **归档机制本身有一处会"藏起关键信息"的副作用，已修复**：P6-acceptance.md 一旦被归档进 `.archived/`，里面记录的具体 FAIL 详情（哪条 BDD、失败原因）就跟着一起被移走了——如果重新派发 implementer 时没人记得去 `.archived/` 翻，"代码保留下来了"这件事本身没有意义，因为不知道具体要修哪里。已给归档脚本加了一份**留在当前任务目录、不被归档**的 `.retreat-history.md` 摘要文件，归档 P6 时自动摘录 FAIL 行写进去。已用实际场景验证，包括连续两次退回时摘要正确追加（不覆盖），且发现这个副产品还有额外价值——同一条 BDD 反复出现在摘要里，是"问题可能不止在 P4、要不要退得更远"的客观信号。

---

## 完整流程走查（用户原始场景：P6 验收 20 pass/2 failed）

用一个具体例子把本 plan 两个问题的方案串起来，避免读者把"归档"理解成"删除"，也避免误以为所有阶段都要走归档：

1. verifier 在 P6 跑完 22 条 BDD，20 PASS、2 FAIL，写入 `P6-acceptance.md`，`check-gate.sh` P6 分支判定 FAIL≠0，gate 不通过
2. 主 Agent **不能**在 phase=P6 的状态下直接改 `src/` 下的实现代码去让这 2 条变绿——**问题三的硬拦截**会在这一步拦下来（暂存了 P6-evidence/ 之外的文件），报错指引退回
3. 主 Agent 诊断：问题出在 P4 实现，不是本步抖动，决定退回。因为 `check-state-transition.sh` 只允许单步回退（diff=1），先把 `.state.yaml` phase 改成 P5
4. **这一步会被问题一的检查 4 拦住**：P6 的自撰产出（`P6-acceptance.md`、`P6-evidence/`）还在原位，必须先跑 `agate-archive-stale-outputs.sh P6 docs/tasks/Txxx`——**这是归档，不是删除**：两者被完整挪到 `docs/tasks/Txxx/.archived/{时间戳}-P6/`，历史证据保留、可追溯，只是清空了当前生效目录。归档脚本同时会把那 2 条 FAIL 的详情摘要写进 `docs/tasks/Txxx/.retreat-history.md`——**这份摘要文件不会被归档，一直留在当前任务目录**，重新派发时不需要翻 `.archived/` 就能看到"当初具体是哪里失败的"
5. 归档完成后，phase=P5 的这次 commit 才能通过；P5 本身没有需要清的自撰文件（不在 P1/P2/P6/P7 名单里），所以 P6→P5 这一步只处理 P6 的归档，不额外做别的
6. 若诊断后发现问题真的在 P4：再退一步，P5→P4（diff=1，合法）。P5 不在 self-authored 名单里，这一步不触发任何归档检查
7. 到达 P4，主 Agent 重新派发 implementer——**这里代码变更是完全合法的（P4 本来就是实现阶段），但代码本身没有被撤销或重置**：归档机制只处理 P1/P2/P6/P7 的自撰 markdown 产出，不碰代码，implementer 面对的是"已有代码 + `.retreat-history.md` 里明确记录的 2 条 FAIL 详情"，是在已有实现基础上定向修复，不是从零重新实现
8. 修完往前走：P4→P5→P6，重新派发 verifier。此时 `docs/tasks/Txxx/` 下**没有旧的 P6-acceptance.md 和 P6-evidence/**（已被移到 `.archived/`），verifier 只能老老实实重新截图、重新写 22 条 PASS/FAIL——不存在"挑几条改改、其余沿用旧结论"的空间
9. 新的 P6-acceptance.md 全绿，gate 通过，继续往 P7 走

这个流程里唯一需要人工记住并主动执行的动作是"退回前先跑归档脚本"——但这个动作**不是靠自觉**，是被检查 4 强制要求的：不跑，退回的 commit 就过不了 gate。

**若诊断已经明确指向 2 阶之外（如本例 P6→P4）**，步骤 3-7 可以合并成一次调用：`agate-retreat-to.sh docs/tasks/Txxx P4 "诊断原因"`（问题二），脚本内部会自动依次产生 P6→P5、P5→P4 两个独立 commit，每一步依然各自归档、各自过 gate 校验，主 Agent 不需要手动分两次操作。

## 问题一：回退后，被跨过阶段的自撰产出文件没有失效机制（用户原始问题的通用化版本）

### 现状

`check-state-transition.sh` 的检查 1 只做"这次回退跨度是不是 1"的合法性判断，`diff=1` 就放行，**不做任何文件层面的操作**。协议假设"退回到 Pn 之后，主 Agent 自然会重新做 Pn 的事，一路往前走到原来失败的阶段"，但"重新做"这件事对 P1/P2/P6/P7 这类 self-authored gate 阶段来说，具体是指"重新写一份产出文件"还是"看一眼旧文件、觉得没大问题就继续用"，协议没有做出规定，脚本层面也没有任何东西强制前者、排除后者。

**已核实的具体风险**：以 P6→P4→P5→P6 这条最典型的路径为例，如果主 Agent 退到 P4 修完代码后，没有让 verifier 重新写一份 P6-acceptance.md（比如误以为"这条 BDD 跟这次修改无关，原来的 PASS 应该还成立"），旧的 P6-acceptance.md 原封不动地留在 `docs/tasks/Txxx/` 下。`check-gate.sh` 的 P6 分支**只读当前文件内容**计数 PASS/FAIL/NC，完全不知道这份文件是修复前写的还是修复后写的——gate 会用修复前的验收结果，判定"通过"。这不是假设性担忧，是直接读 `check-gate.sh` P6 分支源码得出的结论：里面没有任何时间戳/commit hash 比对逻辑。

### 方案：新增"回退时归档 self-authored 产出"的强制前置检查

**不做自动静默归档**（不在 pre-commit hook 里悄悄 `mv` 文件——git hook 运行时对工作区做隐式文件搬移，容易和"这次 commit 到底提交了什么"产生混淆，且这个仓库目前没有"脚本自动改工作区文件"的先例，除了 `check-p6-format.sh --fix` 这种**主 Agent 主动调用**的显式修复，不存在隐式自动挪文件的模式）。改为：**新增一个显式脚本 + 一条前置门槛检查**，让归档这件事变成"不做就过不了 gate"的强制动作，而不是"希望主 Agent 记得做"的软约定。

**新脚本 `agate/scripts/agate-archive-stale-outputs.sh`**：

```bash
#!/usr/bin/env bash
# agate-archive-stale-outputs.sh — 回退时归档被跨过阶段的自撰产出
# 用法：agate-archive-stale-outputs.sh PHASE_BEING_LEFT TASK_DIR
# 只处理 self-authored gate 阶段（P1/P2/P6/P7），P4/P5 无跨重试持久化产出，不适用

set -euo pipefail
PHASE="${1:?用法: agate-archive-stale-outputs.sh PHASE TASK_DIR}"
TASK_DIR="${2:?用法: agate-archive-stale-outputs.sh PHASE TASK_DIR}"

_outputs_for() {
    case "$1" in
        P1) echo "P1-requirements.md P1-review.md" ;;
        P2) echo "P2-design.md P2-review.md" ;;
        P6) echo "P6-acceptance.md" ;;
        P7) echo "P7-consistency.md" ;;
        *) echo "" ;;
    esac
}

OUTPUTS=$(_outputs_for "$PHASE")
[ -z "$OUTPUTS" ] && { echo "GATE ARCHIVE: $PHASE 无需归档（非 self-authored 产出阶段）"; exit 0; }

TS=$(date +%Y%m%d-%H%M%S)
ARCHIVE_DIR="$TASK_DIR/.archived/${TS}-${PHASE}"
mkdir -p "$ARCHIVE_DIR"

# 归档前先把关键失败信息摘要写入一份不会被归档的 breadcrumb 文件
# （P6-acceptance.md 一旦挪进 .archived/，"当初具体是哪条 BDD 失败"这个信息
#  如果没有留痕在当前目录，重新派发 implementer 时容易被忽略——代码保留下来了，
#  但"为什么要退回来"这个最关键的上下文却跟着一起被"藏"进了归档目录）
BREADCRUMB="$TASK_DIR/.retreat-history.md"
{
    echo ""
    echo "## ${TS} 归档 ${PHASE}"
    echo ""
    echo "归档位置：\`${ARCHIVE_DIR}\`"
    if [ "$PHASE" = "P6" ] && [ -f "$TASK_DIR/P6-acceptance.md" ]; then
        FAIL_LINES=$(grep -iE '^\s*- FAIL' "$TASK_DIR/P6-acceptance.md" 2>/dev/null || true)
        if [ -n "$FAIL_LINES" ]; then
            echo ""
            echo "失败详情（供重新派发时引用，避免翻 .archived/）："
            echo '```'
            echo "$FAIL_LINES"
            echo '```'
        fi
    fi
} >> "$BREADCRUMB"

MOVED=0
for f in $OUTPUTS; do
    if [ -f "$TASK_DIR/$f" ]; then
        mv "$TASK_DIR/$f" "$ARCHIVE_DIR/"
        MOVED=$((MOVED + 1))
    fi
done
# P6 专属：连带归档证据目录
if [ "$PHASE" = "P6" ] && [ -d "$TASK_DIR/P6-evidence" ]; then
    mv "$TASK_DIR/P6-evidence" "$ARCHIVE_DIR/"
    MOVED=$((MOVED + 1))
fi

echo "GATE ARCHIVE: $PHASE 产出已归档至 ${ARCHIVE_DIR}（${MOVED} 项），失败摘要已写入 ${BREADCRUMB}"
```

**已用实际场景验证 breadcrumb 设计**：构造 P6-acceptance.md 含 2 条 FAIL，归档后确认 `.retreat-history.md` 正确摘要了失败详情且**留在当前任务目录**（`ls -la` 确认，未被移入 `.archived/`），P6-acceptance.md 本身正确移走。进一步验证了"连续两次退回"的场景：第二次修复后又失败（同一条 BDD-7 再次 FAIL），breadcrumb 正确**追加**（不覆盖）第二条记录——这个副产品还有额外价值：如果同一条 BDD 反复出现在 breadcrumb 里，是"这个问题可能不止是 P4 实现问题、要不要退得更远（P3/P2）"的一个客观信号。

**`check-state-transition.sh` 新增检查 4（独立于检查 2/3，插入位置不敏感——判断条件用 `diff == 1` 且方向为回退，与检查 2 的重试限额判断、检查 3 的"仅前进方向"判断互不重叠，放在检查 3 之后即可，不需要紧贴检查 1）**：

```bash
# 检查 4：回退时若被跨过阶段是 self-authored 产出阶段（P1/P2/P6/P7），
# 且该阶段的产出文件仍在原位（未归档）→ 拦截，要求先跑 agate-archive-stale-outputs.sh
if [ "$old_num" -gt 0 ] && [ "$new_num" -gt 0 ] && [ "$diff" -eq 1 ]; then
    case "$old_phase" in
        P1|P2|P6|P7)
            TASK_DIR=$(dirname "$STATE_FILE")
            STALE_FOUND=""
            case "$old_phase" in
                P1) [ -f "$TASK_DIR/P1-requirements.md" ] && STALE_FOUND="P1-requirements.md" ;;
                P2) [ -f "$TASK_DIR/P2-design.md" ] && STALE_FOUND="P2-design.md" ;;
                P6) [ -f "$TASK_DIR/P6-acceptance.md" ] && STALE_FOUND="P6-acceptance.md" ;;
                P7) [ -f "$TASK_DIR/P7-consistency.md" ] && STALE_FOUND="P7-consistency.md" ;;
            esac
            if [ -n "$STALE_FOUND" ]; then
                echo "GATE STATE: 回退 P${old_num}→P${new_num}，但 ${old_phase} 的自撰产出（${STALE_FOUND}）仍在原位" >&2
                echo "  退回前须先跑：bash agate/scripts/agate-archive-stale-outputs.sh ${old_phase} ${TASK_DIR}" >&2
                echo "  （self-authored gate 产出不能跨重试静默复用，见 LIMITATIONS.md self-authored 分类）" >&2
                exit 1
            fi
            ;;
    esac
fi
```

**为什么这样设计能通用支持"回退和继续"**：diff=1 的单步回退约束（R8③ 已确立）保证任何一次回退最多只跨过一个阶段，所以"归档 old_phase 的产出"这个动作在每一步回退里都是**恰好一件事**，不需要判断"这次回退到底跨过了几个阶段的产出"。P6→P5→P4 这条路径会依次触发两次检查（先 P6→P5 时归档 P6 产出，再 P5→P4 时——P5 不在 self-authored 名单里，跳过），完全自动适配任意深度的连续回退，不需要为"回退到底退了几步"写特判逻辑。往前走（Pn→Pn+1）完全不受影响，检查 4 的判断条件里 `diff` 是负数或 0 时不会触发。

---

## 问题二：多步回退需要手动敲 N 次 commit——用自动化消除这个"疏通 honest path"的反例

### 现状与风险

R8③ 已经确立"diff≥2 强制 PAUSED"这条安全网不放宽——直接跳 2 阶被拦下是有意为之（大跳是"问题严重"的强信号，`check-state-transition.sh` 一个字都不改）。但这带来一个 R8③ 讨论时没有覆盖的副作用：如果主 Agent 已经确诊问题在 2 阶之外（比如 P6 的失败明显是 P4 实现问题），要合法地退到 P4，必须手动做两次完整的"归档 → 改 phase → commit"流程。**如果这个手动流程比直接在 P6 原地改代码更麻烦，主 Agent 就有理由绕开正确路径去走近道**——这正好和问题三想拦住的行为形成对冲：越是让"退回"这条路难走，"原地修"的诱惑就越大。这是本仓库一直坚持的"疏通 honest path，再谈拦截"这条设计哲学在这里的一个真实反例，需要补上。

### 方案：自动化多步回退的执行，不动 diff≥2 的安全网本身

**关键澄清：这不是在重提 R8③ 已经否决过的"放宽 diff≥2 拦截"**。R8③ 拒绝的是"改 `check-state-transition.sh`，让一次 commit 里的大跳直接放行"——这条路径本 plan **完全不碰**，`check-state-transition.sh` 的 diff≥2 判断逻辑不做任何修改。本 plan 提议的是：把"主 Agent 需要手动执行 N 次单步回退"这个纯**执行层面**的机械劳动自动化掉，执行层面自动化之后，依然是 N 次独立的、diff=1 的、各自触发 `pre-commit-gate.sh`/`check-state-transition.sh` 完整校验的真实 commit——**校验的严格程度一分都没降低，降低的只是主 Agent 需要手动操作的次数**。

**新脚本 `agate/scripts/agate-retreat-to.sh`**：

```bash
#!/usr/bin/env bash
# agate-retreat-to.sh — 自动化多步单向回退（每一步仍是独立、真实、受 gate 校验的 commit）
# 用法：agate-retreat-to.sh TASK_DIR TARGET_PHASE "诊断原因"
set -euo pipefail

TASK_DIR="${1:?用法: agate-retreat-to.sh TASK_DIR TARGET_PHASE REASON}"
TARGET_PHASE="${2:?用法: agate-retreat-to.sh TASK_DIR TARGET_PHASE REASON}"
REASON="${3:?必须提供诊断原因（用于每一步回退的 commit message）}"
STATE_FILE="$TASK_DIR/.state.yaml"
MAX_RETRY_MAP="${MAX_RETRY_MAP:-P1:3,P2:3,P3:2,P4:3,P5:2,P6:2,P7:2,P8:2}"
ARCHIVE_SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/agate-archive-stale-outputs.sh"

[ -f "$STATE_FILE" ] || { echo "GATE RETREAT: $STATE_FILE 不存在" >&2; exit 1; }
phase_num() { echo "$1" | grep -oE '[0-9]+' || echo ""; }

CURRENT_PHASE=$(STATE_FILE="$STATE_FILE" python3 -c "
import yaml, os
with open(os.environ['STATE_FILE']) as f:
    print((yaml.safe_load(f) or {}).get('phase', ''))
")
cur_num=$(phase_num "$CURRENT_PHASE")
tgt_num=$(phase_num "$TARGET_PHASE")

if [ -z "$cur_num" ] || [ -z "$tgt_num" ]; then
    echo "GATE RETREAT: 当前 phase（$CURRENT_PHASE）或目标 phase（$TARGET_PHASE）不是合法的 P0-P8" >&2
    exit 1
fi
if [ "$tgt_num" -ge "$cur_num" ]; then
    echo "GATE RETREAT: 目标 phase（$TARGET_PHASE）不低于当前 phase（$CURRENT_PHASE），这不是回退" >&2
    exit 1
fi

# 预检查 A：暂存区不能有 TASK_DIR 之外的内容——下面的 commit 会用 pathspec 限定到 TASK_DIR，
# 但如果暂存区本来就有无关文件，容易让人误以为它们也被这次 retreat 处理了（其实只是继续留在暂存区，
# 状态含糊）。提前报错比事后困惑更清楚。
OUTSIDE_STAGED=$(git diff --cached --name-only 2>/dev/null | grep -vE "^${TASK_DIR#./}/" || true)
if [ -n "$OUTSIDE_STAGED" ]; then
    echo "GATE RETREAT: 暂存区含 TASK_DIR 之外的文件，请先处理（commit 或 unstage）再重试：" >&2
    echo "$OUTSIDE_STAGED" | sed 's/^/  /' >&2
    exit 1
fi

# 预检查 B：一次性查完路径上每一阶退回后的 retry 是否超限，避免半退到一半卡在中间
CHECK_RESULT=$(STATE_FILE="$STATE_FILE" MAX_RETRY_MAP="$MAX_RETRY_MAP" CUR="$cur_num" TGT="$tgt_num" python3 -c "
import yaml, os
with open(os.environ['STATE_FILE']) as f:
    data = yaml.safe_load(f) or {}
retries = data.get('retries', {}) or {}
max_map = dict(p.split(':') for p in os.environ['MAX_RETRY_MAP'].split(','))
cur, tgt = int(os.environ['CUR']), int(os.environ['TGT'])
for n in range(cur - 1, tgt - 1, -1):
    phase = f'P{n}'
    attempts = retries.get(phase, [])
    count = len(attempts) if isinstance(attempts, list) else 0
    limit = int(max_map.get(phase, 3))
    if count + 1 > limit:
        print(f'{phase}:{count+1}:{limit}')
        break
")
if [ -n "$CHECK_RESULT" ]; then
    IFS=':' read -r bad_phase would_be limit <<< "$CHECK_RESULT"
    echo "GATE RETREAT: 路径上 ${bad_phase} 退回后 retry 将达到 ${would_be}（MAX=${limit}），超限——不执行任何一步，直接转 PAUSED 问人类" >&2
    exit 1
fi

# 逐步执行：每一步都是独立的归档 + phase 更新 + retry+1 + 真实 git commit
n="$cur_num"
STEPS=0
while [ "$n" -gt "$tgt_num" ]; do
    next=$((n - 1))
    old_p="P${n}"; new_p="P${next}"
    bash "$ARCHIVE_SCRIPT" "$old_p" "$TASK_DIR"
    STATE_FILE="$STATE_FILE" NEW_PHASE="$new_p" python3 -c "
import yaml, os
with open(os.environ['STATE_FILE']) as f:
    data = yaml.safe_load(f) or {}
retries = data.setdefault('retries', {})
new_phase = os.environ['NEW_PHASE']
attempts = retries.setdefault(new_phase, [])
attempts.append({'attempt': len(attempts) + 1})
data['phase'] = new_phase
with open(os.environ['STATE_FILE'], 'w') as f:
    yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
"
    git add "$TASK_DIR" 2>/dev/null || true
    git commit -qm "retreat: ${old_p} -> ${new_p}（诊断：${REASON}）" -- "$TASK_DIR" 2>&1 || {
        echo "GATE RETREAT: ${old_p} -> ${new_p} 的 commit 未通过 pre-commit hook 校验，已停在 ${old_p}" >&2
        exit 1
    }
    echo "GATE RETREAT: ${old_p} -> ${new_p} 已提交（诊断：${REASON}）"
    n="$next"; STEPS=$((STEPS + 1))
done
echo "GATE RETREAT: 已退到 ${TARGET_PHASE}，共 ${STEPS} 步，均已独立 commit + 归档"
```

**已用真实 git 仓库端到端验证**（非仅推理）：

| 场景 | 验证方式 | 结果 |
|------|---------|------|
| P6→P4 两步回退（.state.yaml phase=P6，目标 P4） | 实跑脚本 | ✅ 产生 2 个独立 commit（`retreat: P6 -> P5` / `retreat: P5 -> P4`），各自带诊断原因；`retries` 正确记为 `P5: [attempt 1]`、`P4: [attempt 1]`；P6 的自撰产出正确归档，P5 因不在 self-authored 名单被跳过归档，日志明确打印"无需归档" |
| retry 预算沿途会超限（P5 已有 2 次 attempt，MAX=2，再退一次会到 3） | 实跑脚本 | ✅ 预检查阶段就报错拦截，**不做任何一步操作**——`.state.yaml` 内容和 git log 均确认未发生任何变化，不会出现"退了一半卡住"的中间状态 |
| **暂存区在调用脚本前已有 TASK_DIR 之外的无关文件**（如主 Agent 手头还有别的未提交改动） | 实跑脚本 | ⚠️ **这里发现并修复了一个真实 bug**：脚本最初的 `git commit -qm "..."`（不带 pathspec）会把暂存区里**所有**已暂存内容一起提交进去，不管是不是这次 retreat 该处理的——实测复现：`other-project/wip.txt` 这种无关文件被一起卷进了 `retreat: P6 -> P5` 这条 commit 里，污染了审计轨迹。已修复为 `git commit ... -- "$TASK_DIR"`（pathspec 限定），并追加了一条预检查：暂存区有 TASK_DIR 之外的文件就直接拒绝执行，而不是默默地只提交一部分、让人不清楚剩下的东西是不是也被处理了。**额外验证了一点容易被忽略的细节**：pathspec 限定的 `git commit` 触发的 pre-commit hook，`git diff --cached` 只会看到 pathspec 范围内的文件（实测确认，hook 完全看不到 `other-project/` 下的无关文件），不会因为暂存区里有别的东西而干扰 gate 判断 |

**为什么这不违背 R8③ 的决定**：R8③ 否决的是"改脚本让一次 commit 里的大跳直接放行"；本方案里每一次 `git commit` 依然会触发 `.git/hooks/pre-commit`，依然会被现有的 `pre-commit-gate.sh` 和 `check-state-transition.sh` 完整校验一遍（`diff` 判断的输入是相邻两次 commit 的 phase 差，脚本内部产生的 N 次 commit 每一次的 diff 依然是 1，不会被误判为大跳）——**唯一变化是"敲键盘的手"从人变成了脚本，安全网的判断逻辑没有被这个脚本绕过或削弱**。这正好回应了 R8.4 决定里"没有论证放宽的安全性"这个顾虑：因为压根不需要放宽，安全逻辑原样保留，只是执行自动化了。

**诊断纪律没有被自动化掉**：脚本强制要求传入"诊断原因"参数，且这个原因会写进每一步的 commit message——主 Agent 依然必须先想清楚"问题出在哪一层"才能调用这个脚本，自动化拿走的是"手动敲 N 次 git 命令"这个机械负担，不是"先诊断再行动"这个纪律本身。

## 问题三：P6 验收失败后，主 Agent 直接在 P6 改代码——是 `pre-commit-gate.sh` 的 E3 检查把 P6 和 P4/P5 混为一谈

### 现状（已实测确认的根因）

```bash
# pre-commit-gate.sh 现状（:259-267）
CODE_FILES=$(git diff --cached --name-only 2>/dev/null | grep -vE '\.(md|yaml)$|^\.state' || true)
if [ -n "$CODE_FILES" ]; then
    case "$PHASE" in
        P4|P5|P6) ;;   # ← P6 和 P4/P5 一起被放行，没有 WARNING 也没有 BLOCK
        *)
            echo "GATE WARNING: phase=$PHASE 但暂存了代码文件——主 Agent 是否在非实现阶段直接改代码？" >&2
            ;;
    esac
fi
```

P4 是实现阶段，改代码是它的全部意义所在；P5 是外部产出 gate（判定对象是测试运行器返回值，主 Agent 无法伪造），验证过程中做点脚本/配置层面的小修补是合理的。**P6 不一样**——它是 `LIMITATIONS.md` 明确点名的 self-authored gate，判定对象是 verifier 自己写的 P6-acceptance.md。P6 阶段本来就不应该有"改项目源码"这个动作：如果验收发现了问题，说明源头在 P4（实现）或更早，正确路径是走问题一的回退协议退回去重新派发 implementer，而不是主 Agent 在还挂着"phase=P6"这个状态标记的情况下直接手动改代码让 2 条 FAIL 变成 PASS——这样做的结果和 T026 事故（主 Agent 直接编造 PASS 结论）性质上是一回事：**判定证据和判定对象由同一个人在同一个时间点生产**，只是这次造的不是假 markdown，是真代码——反而更难被"证据存在性检查"这类现有缓解措施发现，因为代码变了、测试真的跑过了、证据是真的，只是这个"真"绕开了本该走的重新派发流程。

用户观察到的"P0-P5 都正常，P6 开始 agent 自己发挥"，精确定位到的就是这一条代码：P6 是唯一一个"该拦、但目前被和外部产出 gate 混在一起放行"的阶段。

### 方案：把 P6 从"放行清单"里摘出来，区分证据文件与源码文件

不能简单把 P6 移到 `case` 的 `*)` 分支只给 WARNING——因为 P6 阶段本来就会合法地暂存 `P6-evidence/` 下的截图、日志等非 `.md`/`.yaml` 文件，这些不该被拦。需要先把"证据目录文件"排除掉，剩下的才是真正的"项目源码"：

```bash
# pre-commit-gate.sh 改动（:259-267）
ALL_NONMD=$(git diff --cached --name-only 2>/dev/null | grep -vE '\.(md|yaml)$|^\.state' || true)
# 证据文件例外：TASK_REL/P{n}-evidence/ 下的文件不算"代码"
NON_EVIDENCE_FILES=$(echo "$ALL_NONMD" | grep -vE "^${TASK_REL}/P[0-9]-evidence/" || true)
if [ -n "$NON_EVIDENCE_FILES" ]; then
    case "$PHASE" in
        P4|P5) ;;  # 外部产出 gate：代码变更是预期行为
        P6)
            echo "GATE: phase=P6 暂存了项目源码/非证据文件（不在 P6-evidence/ 下）——" >&2
            echo "  P6 是 self-authored gate 的验收阶段，不应直接改代码。" >&2
            echo "  若验收发现问题，应退回至实现阶段重新派发 implementer，而非在 P6 自行修复。" >&2
            echo "  （见 LIMITATIONS.md「主 Agent 遇到困难时倾向于自行解决」已知风险模式，" >&2
            echo "   退回步骤见 agate/rules/state-transitions.md 回退规则 + 问题一的归档前置检查）" >&2
            exit 1
            ;;
        *)
            echo "GATE WARNING: phase=$PHASE 但暂存了代码文件——主 Agent 是否在非实现阶段直接改代码？" >&2
            ;;
    esac
fi
```

**已知代价（明确写出，不回避）**：这条改成硬拦截后，即便只是"验收时发现一处无关紧要的测试脚本手误，改一个字符就行"这种极小改动，也会被拦、必须走完整的退回-重派发流程，不能在 P6 原地小修。这是有意的权衡——参照本仓库对 `PROD_TOUCHED` 的一贯态度（无论触发原因多微小，一律 PAUSED 报告人类，不设"这次情况特殊所以放过"的例外），P6 self-authored gate 的代码直改风险和 PROD_TOUCHED 是同一量级的问题：一旦开了"这次是小改动所以放行"的口子，就无法区分"真的是小改动"和"主 Agent 说服自己这是小改动"——而这恰恰是 self-authored gate 无法自证的地方。

---

## 与已有 plan/文档的关系

| 已有内容 | 关系 |
|---------|------|
| `p6-gate-institutional-design-20260711.md` 方案③（逐步溯源退回，含 R8.4 补充的"大跳回退 vs 强制逐步退"设计张力讨论） | 本 plan 是它的直接延伸——③解决了"回退不能跳阶段"（diff≥2 强制 PAUSED，本 plan **完全不改**这条规则），本 plan 补上③遗留的三个缺口：退回之后跨过的阶段产出怎么处理（问题一）、多步回退的机械负担会不会诱使 agent 绕开正确流程（问题二，且明确论证了这不是重开③已否决的"放宽 diff≥2"讨论）、主 Agent 会不会绕开退回直接在原地改代码（问题三） |
| `LIMITATIONS.md` self-authored/外部产出 gate 分类 | 本 plan 三个问题的方案设计都直接建立在这个既有分类之上，不是新发明一套风险模型 |
| `agate-p6-gate-friction-fixes-20260723.md`（v0.18.0，已落地） | 独立、不冲突——那份改的是 P6 证据格式解析的正确性，本 plan 改的是"什么时候允许改代码""退回后旧证据怎么处理""多步回退怎么自动化"这三个更上游的流程问题 |

---

## 测试

### 新增 `agate/tests/unit/agate-archive-stale-outputs.bats`

| 用例 | 描述 | 期望 |
|------|------|------|
| ARCH.1 | P6 阶段有 P6-acceptance.md + P6-evidence/，归档 P6 | 两者都被移动到 `.archived/{ts}-P6/`，原位置不存在 |
| ARCH.2 | P4 阶段调用归档脚本 | exit 0，提示"无需归档"，不做任何文件操作 |
| ARCH.3 | P6-evidence/ 不存在，只有 P6-acceptance.md | 只归档存在的那个，不报错 |
| ARCH.4 | 同一任务对 P6 归档两次（模拟第一次失败归档后修复、第二次又失败）| **已实测验证**：两次归档的时间戳目录名不同（`{ts1}-P6`、`{ts2}-P6`），两份历史证据都完整保留、互不覆盖，用户明确要求过"客观证据要留足，支持多次存档" |
| ARCH.5 | P6-acceptance.md 含 2 条 FAIL，归档 P6 | **已实测验证**：`.retreat-history.md` 正确摘要 2 条 FAIL 详情，且该文件本身**留在当前任务目录、未被归档**（用 `ls -la` 确认） |
| ARCH.6 | 同一任务连续两次归档 P6（同一条 BDD 两次都失败）| **已实测验证**：`.retreat-history.md` 正确追加（不覆盖）两条记录，可用于识别"同一条 BDD 反复失败，问题可能不止在 P4"这类信号 |

### 新增 `agate/tests/unit/agate-retreat-to.bats`

| 用例 | 描述 | 期望 |
|------|------|------|
| RETREAT.1 | phase=P6，目标 P4，retry 预算充足 | **已实测**：产生 2 个独立 commit，`retries` 正确记为 P5/P4 各 1 次，P6 产出正确归档，P5 正确跳过归档 |
| RETREAT.2 | 目标 phase 不低于当前 phase | exit 1，报错"不是回退" |
| RETREAT.3 | 路径上某阶 retry 预算不足 | **已实测**：exit 1，预检查阶段即报错，`.state.yaml` 和 git log 均未发生任何变化（不产生"退一半卡住"的中间态） |
| RETREAT.4 | 中途某一步的 commit 被 pre-commit hook 拒绝（如暂存了不该有的文件） | exit 1，明确报告停在哪一步，不继续后续步骤 |
| RETREAT.5 | 目标 phase 不是 P0-P8 合法值 | exit 1 |
| RETREAT.6 | 调用前暂存区已有 TASK_DIR 之外的文件 | **已实测验证**：exit 1，明确列出哪些文件需要先处理，不执行任何一步（不做归档、不改 `.state.yaml`、不 commit），避免无关内容被静默卷入 retreat commit |

### 一致性检查（可选，锦上添花）

`check-protocol-consistency.py` 的 CHECK 9 反向覆盖检查只扫描 `check-*.sh` + `pre-commit-gate.sh` + `ci-gate-backstop.py`，`agate-archive-stale-outputs.sh` 和 `agate-retreat-to.sh` 均不匹配这个模式，**不需要**加锚点（与 `agate-inject-card.sh`/`agate-next-card.sh` 等非 gate 脚本待遇一致，已核实）。`check-state-transition.sh` 已有的两条锚点（`MAX_RETRY`、`diff`+`phase_num`）关键词在新增检查 4 里依然存在，不会失效，无需改动；可选：新增一条锚点专门覆盖检查 4（如 keywords: `STALE_FOUND`），非必须。

### `check-state-transition.sh` 新增测试

| 用例 | 描述 | 期望 |
|------|------|------|
| ST_ARCHIVE.1 | 回退 P6→P5，P6-acceptance.md 仍在原位（未归档） | exit 1，提示先跑归档脚本 |
| ST_ARCHIVE.2 | 回退 P6→P5，P6-acceptance.md 已被归档（原位不存在） | exit 0，放行 |
| ST_ARCHIVE.3 | 回退 P5→P4（P5 不在 self-authored 名单） | exit 0，不检查归档，不受影响（回归：确认 P4/P5 无关分支未被误伤） |
| ST_ARCHIVE.4 | 前进 P4→P5（非回退方向） | exit 0，不触发归档检查（回归：正常前进流程不受影响） |

### `pre-commit-gate.sh` 新增测试

| 用例 | 描述 | 期望 |
|------|------|------|
| IT_P6_CODE.1 | phase=P6，暂存 `P6-evidence/screenshots/a.png` | exit 0（证据文件例外，不拦） |
| IT_P6_CODE.2 | phase=P6，暂存项目源码文件（如 `src/app.py`） | exit 1，报"不应直接改代码"+ 退回指引 |
| IT_P6_CODE.3 | phase=P4，暂存源码文件 | exit 0（回归：P4 不受影响） |
| IT_P6_CODE.4 | phase=P5，暂存源码文件 | exit 0（回归：P5 不受影响，外部产出 gate 允许过程中的脚本修补） |
| IT_P6_CODE.5 | phase=P2（现有 `*)` 分支场景），暂存源码文件 | WARNING 而非 exit 1（回归：现有行为不受影响，本 plan 只改 P6 这一个分支） |

---

## 实施顺序

1. 新增 `agate-archive-stale-outputs.sh` + 单元测试
2. `check-state-transition.sh` 新增检查 4 + 测试
3. 新增 `agate-retreat-to.sh` + 单元测试（依赖步骤 1 的归档脚本）
4. `pre-commit-gate.sh` E3 检查改造（证据文件例外 + P6 硬拦截）+ 测试
5. `agate/rules/state-transitions.md`「回退规则」小节补充归档前置要求说明 + `agate-retreat-to.sh` 用法
6. `phase-cards/P6-acceptance.md` 补充"验收失败时不能直接改代码，须走回退协议"的显式指引；`phase-cards/P4-implementation.md` 补充"重新派发时，dispatch-context 须引用 `.retreat-history.md` 里的失败详情"的要求（防止归档把关键上下文一并"藏"起来）
7. `dispatch-protocol.md` 的逐步溯源决策表旁补充"退回前先跑归档脚本（或直接调用 `agate-retreat-to.sh`）"的操作步骤
8. 跑全量测试 + `check-protocol-consistency.py` + `shellcheck`
9. CHANGELOG 标注破坏性变更（P6 阶段暂存源码文件从"放行"变为"硬拦截"）
10. self-gate：派发 protocol-alignment-review

---

## 与用户原始问题的对应关系（便于验收）

| 用户提出的问题 | 本 plan 的回应 |
|--------------|---------------|
| "P6-P4-P5 重复流程，P5/P6 有旧内容会不会有影响" | 问题一：新增归档前置检查，回退时强制清空 self-authored 产出，不能带着旧内容"续作" |
| "agate 应该更通用，支持回退和继续" | 归档机制基于 diff=1 单步回退 + self-authored 阶段名单，天然适配任意深度、任意阶段的回退-继续循环，不是只修 P6→P4 这一个特例 |
| "P6 验收失败后 agent 自己发挥，是哪里的问题" | 问题三：定位到 `pre-commit-gate.sh` E3 检查把 P6（self-authored）和 P4/P5（外部产出）混为一谈，导致 P6 阶段改代码不受任何约束 |
| "分两次 commit 会不会让 agent 觉得麻烦，干脆自己改了" | 问题二：`agate-retreat-to.sh` 自动化多步回退的执行，机械负担降到一次调用，安全校验（diff=1 逐步验证、retry 限额、R8③ 的 PAUSED 安全网）一分不少 |
| "R8③ 当时怎么讨论的，合理么" | 已在问题二开头引用原文并解释：R8③ 否决的是"放宽 diff≥2 拦截"，本 plan 完全不碰这条规则，只自动化多步单步回退的执行过程，两者不冲突 |
| "archive 机制要支持多次存档" | 已实测验证：时间戳目录名保证多次归档互不覆盖，历史证据完整保留（见 ARCH.4 测试用例） |
| "P4 退回后，代码会不会被撤销，是重新实现还是接着改" | **不会撤销**：归档机制只处理 P1/P2/P6/P7 的自撰 markdown，不碰代码；P4 是在已有代码基础上定向修复，不是重来。另外发现并修复了一处关联缺口：归档 P6-acceptance.md 会把具体 FAIL 详情一起"藏"进 `.archived/`，已加 `.retreat-history.md` 摘要文件（不被归档，留在当前目录）解决 |
