# 环境基线快照机制 + P5 机械化回归判定

> 起草日期：2026-07-25
> 触发来源：PeekView T073 事件（ruff `--fix --unsafe-fixes` 引入 43 个测试回归，潜伏 3 天未被发现；
> T068 的 P5 阶段实际看到过 63 个预存失败，但被主 Agent 一句话"非本任务相关"带过，未登记未排查）+
> X2Infinity 提出的整改建议（`agate-T073-整改建议-20260725-1.md`）与讨论中的两点修正：
>   1. 硬拦截不该锚定固定阶段号（P0 是纯设计阶段，不接触环境）
>   2. 能自动化的必须自动化，不新增任何需要主 Agent 判断/自证的检查点——
>      主 Agent 是"总想钻空子的叛逆期小孩"，新机制的设计前提是**不给它可钻的空子**，
>      而不是"多一条规则靠它自觉"
> 编号延续：v0.23.0 用到 P2.46，本计划为 P2.47、P2.48

---

## 零、诊断与设计取舍

### 0.1 为什么"P0 硬拦截"是错的锚点

复核 `phase-cards/P0-orchestrator.md`、`P1-requirements.md`、`P2-design.md` 三张卡片：三者的产出物全部是 markdown（brief/requirements/design），**没有一步会调用测试运行器或接触真实代码/环境**。

第一个真正调用测试运行器的阶段是 **P3**（`check-tdd-red.sh` 会跑项目真实测试命令确认红灯）。但 P3 本身可裁剪（`risk=low` 时可跳过），跳过后**第一个真正接触环境的变成 P4**（前置条件要求 P3-test-cases.md 存在——若 P3 被裁剪则此前置条件按裁剪规则豁免，P4 自己成为首触点）。

结论：不存在一个固定的"第一个环境接触阶段"，它取决于该任务 P1 声明的 `phases:` 裁剪列表。硬把检查点钉死在 P0 上，会导致纯设计任务（不含 P3/P4）被要求做一次它根本用不到的环境自检——这正是 X2Infinity 指出的问题。

### 0.2 为什么"判断预存 vs 新增"不该是主 Agent 的活

原整改建议的建议 2（P5 硬拦截 known-failures.md 必须存在）思路对，但拦截条件依赖 `P5-test-results/unit.md` 里是否**主动写了**"预存失败"这几个字——判定"这次失败该不该算预存"仍然是主 Agent 自己说了算。T068 事故的核心正是主 Agent 自己判断"63 个，非本任务相关，不阻塞"——如果这个判断本身错了（比如把一个真实新回归也归类成预存），文字匹配式的硬拦截对此没有任何防御力，只挡得住"完全没提"的情况，挡不住"提了但分类错"的情况。

**改进方向**：把"预存 or 新增"从主观声明改成两次快照的机械 diff——

- 任务开始时（不指定固定阶段，见 0.3）自动跑一次全量测试，脚本产出失败列表快照
- P5 阶段 verifier 再跑一次，脚本产出失败列表
- gate 脚本对两份列表做 `comm` diff：**只在"任务后"出现的 = 新增，直接拦截；两边都有的 = 预存，才需要 known-failures.md 登记**

分类不再依赖任何人写的文字，纯粹是两个文件的集合运算。主 Agent 剩下唯一要做判断的地方，是"预存失败要不要现在顺手修"——这个权衡本来就该留给人/主 Agent，不是机器能替代的语义判断，**不新增负担，只是把本来就该由它判断的部分留给它，把不该由它判断的部分（哪些算预存）拿走**。

### 0.3 如何在不判断"是不是第一个环境接触阶段"的前提下自动挂载

不需要在协议里推导"这个任务的 phases 列表里第一个碰环境的是哪个"——把捕获脚本设计成**任务级幂等**：脚本第一步检查 `$TASK_DIR/pre-task-baseline.md` 是否已存在，存在就直接退出（no-op）。这样可以**无条件**在 P3 和 P4 两处入口都调用它：

- 若 P3 存在（未裁剪）：P3 入口第一次调用时真正执行，P4 入口调用时发现文件已存在，no-op
- 若 P3 被裁剪：P3 阶段整个跳过，P4 入口第一次调用时真正执行

主 Agent 不需要判断"我该不该跑这个"——两处都无条件跑，脚本自己决定要不要真的做事。这比 0.1 讨论时设想的"判断哪个是首触点"更简单，也更不容易出错（少一个可能被跳过或判断错的决策点）。

### 0.4 成本控制：git commit hash 缓存，不用"隔 N 个任务"

"隔 N 个任务跑一次"需要主 Agent 数数/记着——又是一个可能被遗忘或走样的自报信号。改用仓库级缓存：

- 缓存 key = `sha256(commit_hash + 排序后的 gate_commands.P5 命令列表)`（同一 commit 上若不同任务声明的 P5 命令不同，仍需重新捕获，避免用错误的测试范围复用缓存）
- 每次调用先算 key，命中缓存（`docs/.agate-env-baseline-cache/{key}.txt`，仓库内、随 git 提交，可审计）就直接复制内容到 `$TASK_DIR/pre-task-baseline.md`，不重新跑测试
- 未命中才真的跑一次全量测试并写入缓存

判断条件是"HEAD 和已缓存的 commit 是否一致"，客观可查（`git rev-parse HEAD` 对比），不依赖任何计数或记忆。

### 0.5 明确不在本计划范围内的问题（留作后续观察）

P5 目前整体是 `exit 2`（`check-gate.sh` P5 分支主判断靠主 Agent 自己写"通过"），**不是**机器验证 `gate_commands.P5` 实际 exit code + failed 计数（`推进条件` 清单里写了这个要求，但没有对应脚本强制）。T068 能在 63 个失败的情况下让 P5 "通过"，根子也有这一层原因。这是比本计划范围更大的结构性改动（把 P5 从 self-authored gate 升级为 external-output-gate，涉及改变 verifier 产出格式的强约束），本计划的机械 diff 只解决"预存/新增分类不能靠嘴说"这一层，不改变 P5 整体仍是 `exit 2` 这件事。建议作为独立后续计划观察是否需要做。

---

## P2.47：环境基线快照捕获（自动、幂等、无主 Agent 判断）

### 新增脚本 `agate/scripts/agate-capture-env-baseline.sh`

```bash
#!/usr/bin/env bash
# 用途：捕获任务开始前的全量测试失败列表，供 P5 阶段做机械 diff。
# 幂等：任务级已捕获过则直接退出，不重跑。
# 缓存：仓库级按 (commit hash + gate_commands.P5 命令集合) 缓存，HEAD 未变则复用。
# 不阻塞：本脚本任何情况下都不应导致调用方 P3/P4 流程失败——
#   捕获失败或无法可靠解析（如项目尚未声明 TEST_RUNNER/gate_commands.P5、
#   命令执行异常、fail-list 提取行数与汇总计数对不上）一律只打印 WARNING 到 stderr、
#   不写入任何文件、exit 0（不影响 P3/P4 推进；缺失的后果由 P5 阶段的
#   graceful degradation 承担，见 P2.48——宁可"没有基线"，不可"基线是假的"）。
#
# 重要：不对声明的命令追加任何 flag（不做 v0.23.0 已踩过的"硬编码 -q 假设 pytest"同类错误）。
# 命令必须原样来自 gate_commands.P5（项目自己声明时就该带齐所需参数，本脚本只复用不改写）。
set -uo pipefail

TASK_DIR="$1"
[ -f "$TASK_DIR/pre-task-baseline.md" ] && exit 0   # 任务级幂等

P2_FILE="$TASK_DIR/P2-design.md"
[ -f "$P2_FILE" ] || { echo "ENV_BASELINE: P2-design.md 不存在，跳过基线捕获（P2 未完成前不应到达此步）" >&2; exit 0; }

# 复用 gate_commands.P5 声明的命令（与 P5 实际会跑的命令保持一致，diff 才有意义）
P5_CMDS=$(python3 - "$P2_FILE" <<'PYEOF'
import re, sys
content = open(sys.argv[1]).read()
m = re.search(r'^gate_commands:[ \t]*\n((?:  .*\n|\s*\n)*)', content, re.MULTILINE)
if not m:
    sys.exit(0)
for line in re.findall(r'^  P5\w*:\s*(.+)$', m.group(1), re.MULTILINE):
    print(line.strip().strip('"').strip("'"))
PYEOF
)
[ -z "$P5_CMDS" ] && { echo "ENV_BASELINE: 未在 P2-design.md 找到 gate_commands.P5，跳过基线捕获" >&2; exit 0; }

COMMIT=$(git rev-parse HEAD 2>/dev/null) || { echo "ENV_BASELINE: 非 git 仓库，跳过" >&2; exit 0; }
CACHE_KEY=$(printf '%s\n%s' "$COMMIT" "$(echo "$P5_CMDS" | sort)" | sha256sum | cut -d' ' -f1)
CACHE_DIR="$(git rev-parse --show-toplevel)/docs/.agate-env-baseline-cache"
CACHE_FILE="$CACHE_DIR/$CACHE_KEY.md"
mkdir -p "$CACHE_DIR"
# 缓存清理：缓存文件随 commit 增长单调积累。可在版本发布前手动清理：
#   rm docs/.agate-env-baseline-cache/*.md
# 缓存文件很小（纯文本失败列表），长期膨胀可接受；如需自动清理可在 P8 阶段 prune。

if [ -f "$CACHE_FILE" ]; then
    cp "$CACHE_FILE" "$TASK_DIR/pre-task-baseline.md"
    echo "ENV_BASELINE: 复用缓存（commit $COMMIT 未变）" >&2
    exit 0
fi

# 未命中缓存：真正跑一遍。参考实现为 pytest（同 check-tdd-red.sh 的技术栈无关约定）。
# 复用 check-tdd-red.sh 已验证的 FAIL_PATTERN 提取"N failed"汇总计数（不是新发明），
# 用它做 sanity check：明细行提取数量对不上汇总数量 → 视为解析不可靠，整批放弃。
FAIL_PATTERN="${TEST_FAIL_PATTERN:-[0-9]+ failed}"
FAIL_LIST=""
PARSE_OK=1
while IFS= read -r cmd; do
    OUT=$(eval "$cmd" 2>&1)
    CMD_EXIT=$?
    SUMMARY_COUNT=$(echo "$OUT" | grep -oE "$FAIL_PATTERN" | grep -oE '[0-9]+' | tail -1)
    if [ -z "$SUMMARY_COUNT" ]; then
        echo "ENV_BASELINE: 命令 '$cmd' 输出中未找到可识别的失败汇总行（exit=$CMD_EXIT），放弃捕获，不写入任何文件" >&2
        echo "$OUT" | tail -5 >&2
        PARSE_OK=0
        break
    fi
    CMD_FAIL_LIST=$(echo "$OUT" | grep '^FAILED ' | sed 's/^FAILED //; s/ - .*//')
    CMD_FAIL_COUNT=$(echo "$CMD_FAIL_LIST" | grep -c . | tail -1)
    if [ "$CMD_FAIL_COUNT" -ne "$SUMMARY_COUNT" ]; then
        echo "ENV_BASELINE: 命令 '$cmd' 汇总计数($SUMMARY_COUNT)与明细提取数($CMD_FAIL_COUNT)不一致，" >&2
        echo "  说明当前 runner 的明细行格式未被本脚本识别，放弃捕获" >&2
        PARSE_OK=0
        break
    fi
    FAIL_LIST+="$CMD_FAIL_LIST"$'\n'
done <<< "$P5_CMDS"

[ "$PARSE_OK" -eq 0 ] && exit 0

FAIL_LIST=$(echo "$FAIL_LIST" | grep -v '^$' | sort -u)
FAIL_COUNT=$(echo "$FAIL_LIST" | grep -c . | tail -1)

{
  echo "---"
  echo "captured_at_commit: $COMMIT"
  echo "generated_by: agate-capture-env-baseline.sh"
  echo "---"
  echo "# 任务前环境基线"
  echo ""
  echo "失败数：$FAIL_COUNT"
  echo ""
  echo '```fail-list'
  echo "$FAIL_LIST"
  echo '```'
} > "$CACHE_FILE"

cp "$CACHE_FILE" "$TASK_DIR/pre-task-baseline.md"
echo "ENV_BASELINE: 已捕获，失败数=$FAIL_COUNT" >&2
exit 0
```

**非 pytest 技术栈**：与 `check-tdd-red.sh` 同一约定，`FAILED ` 前缀匹配 + `[0-9]+ failed` 汇总匹配都是 pytest 参考实现；vitest 等其他 runner 需要项目自行提供 `TEST_FAIL_PATTERN` 覆盖或接受"无法捕获、优雅跳过"的降级结果（此处先不做通用适配，避免重蹈 v0.23.0 "先只解决已知报错，未做系统扫描"的覆辙）。**明确不做**的事：不对声明命令追加任何硬编码 flag（BLOCKING 1 的教训）；命令执行异常或明细/汇总数量对不上时，宁可完全不产出基线文件，也不产出一份可能是假的基线（BLOCKING 2/3 的教训——错误的"看似干净"比"没有"更危险，因为后续 P5 diff 会信任这份文件）。

### 挂载点（无判断，无条件调用）

- `phase-cards/P3-tdd.md`「如果是首次进入本阶段」新增步骤 0（在步骤 1 之前）：
  ```
  0. 跑 agate-capture-env-baseline.sh $TASK_DIR（自动捕获环境基线）。
     该步骤不会阻塞流程——任何 stderr 输出（含 WARNING）均可忽略，直接继续步骤 1，
     无需查看结果、无需判断、无需因为看到 WARNING 而停下来处理。
  ```
- `phase-cards/P4-implementation.md`「如果是首次进入本阶段」同样新增步骤 0（保证 P3 被裁剪时 P4 兜底触发），文字一致

两处都是"无条件调用，脚本自己决定要不要做事"，不要求主 Agent 判断"这是不是我的首触点"。

### 需要新增的测试场景（bats）

| 测试 | 场景 | 断言 |
|---|---|---|
| EB.1 | 任务级已有 pre-task-baseline.md | 脚本 no-op，exit 0，不重跑测试命令 |
| EB.2 | P2-design.md 不存在 | exit 0 + WARNING，不阻塞 |
| EB.3 | gate_commands.P5 未声明 | exit 0 + WARNING，不阻塞 |
| EB.4 | 首次捕获，仓库无缓存 | 真实跑测试命令，写入缓存文件 + 任务文件，两者内容一致 |
| EB.5 | 缓存命中（同 commit + 同命令集合） | 不重跑测试命令（用标记文件验证测试命令未被执行），直接复制缓存 |
| EB.6 | 缓存未命中（commit 变了） | 重新真实跑测试命令，覆盖生成新 key 的缓存 |
| EB.7 | 同一 commit 但 gate_commands.P5 命令集合不同 | 视为未命中（不同 key），重新跑 |
| EB.8 | 声明命令本身参数错误/崩溃（如 vitest 项目误用 pytest 专属 flag） | 不写任何文件，stderr 有明确 WARNING，exit 0 不阻塞 |
| EB.9 | 汇总计数与明细提取数不一致（模拟 fixture：伪造一个"3 failed"但只有 1 行 FAILED 明细的输出） | 不写任何文件，stderr 提示"明细行格式未被识别"，exit 0 |
| EB.10 | gate_commands.P5 声明 2 条命令（如单元+集成），各自有失败 | 两条命令的 fail-list 合并去重，逐命令分别校验汇总/明细一致性（含重叠失败场景） |
| EB.11 | 非 git 仓库（git rev-parse HEAD 失败） | exit 0 + WARNING，不阻塞 |
| EB.12 | 缓存文件存在但内容损坏（非合法 frontmatter + fail-list 格式） | P5 diff 优雅降级：PRE_LIST 提取为空，所有 post 失败视为新增 |

---

## P2.48：P5 gate 机械化回归判定

### `P5-verification.md` 产出规格新增

```
- P5-test-results/fail-list.txt：verifier subagent 产出，failed 测试 id 逐行列出（`FAILED ` 前缀同上，
  pytest 参考实现），可为空文件（无失败时）。runner 格式无法提取 id 列表时可省略此文件——
  P5 gate 检测到缺失时优雅降级为原有 WARNING-only 行为，不因此新增拦截。
```

**落地注意**：需同步修改 `phase-cards/P5-verification.md` 的"产出规格"节和"返回前自检"节，
把 fail-list.txt 加入产出物列表和自检清单。

### `check-gate.sh` P5 分支新增（在现有 WARNING 逻辑之后，`exit 2` 之前插入）

```bash
BASELINE="$TASK_DIR/pre-task-baseline.md"
POST_FAILS="$TASK_DIR/P5-test-results/fail-list.txt"
if [ -f "$BASELINE" ] && [ -f "$POST_FAILS" ]; then
    PRE_LIST=$(sed -n '/```fail-list/,/```/p' "$BASELINE" | sed '1d;$d')
    NEW_FAILS=$(comm -13 <(echo "$PRE_LIST" | sort -u) <(sort -u "$POST_FAILS"))
    STILL_FAILING=$(comm -12 <(echo "$PRE_LIST" | sort -u) <(sort -u "$POST_FAILS"))

    if [ -n "$NEW_FAILS" ]; then
        echo "GATE P5: 检测到基线快照中不存在的新增失败，视为本任务引入的回归，拦截：" >&2
        echo "$NEW_FAILS" | sed 's/^/  - /' >&2
        exit 1
    fi
    if [ -n "$STILL_FAILING" ] && [ ! -f "$TASK_DIR/known-failures.md" ]; then
        echo "GATE P5: 检测到 $(echo "$STILL_FAILING" | grep -c .) 个预存失败仍未修复，" >&2
        echo "  基线快照证实这些失败早于本任务存在，但 known-failures.md 不存在——按协议必须登记" >&2
        exit 1
    fi
    # 两份文件都在、且无新增失败、预存失败已登记 → 不再打印 T060 WARNING（已被机械判定取代）
fi
exit 2
```

**向后兼容**：`pre-task-baseline.md` 或 `fail-list.txt` 任一缺失（旧任务、runner 格式不支持、P2 未声明 gate_commands.P5 等情况），整段新逻辑跳过，回退到现状（WARNING-only，`exit 2`）——不影响任何现有任务/测试。

### 需要新增的测试场景（bats）

| 测试 | 场景 | 断言 |
|---|---|---|
| PG.1 | 两份文件均缺失 | 走原有分支，exit 2，行为与改动前一致 |
| PG.2 | 无新增失败、无预存失败 | exit 2（正常推进，无拦截） |
| PG.3 | 有新增失败（post 独有） | exit 1，输出列出具体新增失败 id |
| PG.4 | 有预存失败（pre/post 都有）、已有 known-failures.md | exit 2（预存但已登记，不拦截） |
| PG.5 | 有预存失败、known-failures.md 不存在 | exit 1 |
| PG.6 | 预存失败已在本任务修复（pre 有、post 无） | exit 2（视为正常收益，不要求登记） |
| PG.7 | pre-task-baseline.md 的 fail-list 为空（0 个预存失败），post 有失败 | 全部视为新增失败，exit 1 |
| PG.8 | fail-list.txt 为空文件（0 个 post 失败），pre 有失败 | 全部视为预存已修复，exit 2 |
| PG.9 | known-failures.md 存在但为空（只有 frontmatter 无登记行） | exit 2（文件存在即通过，内容审查超出 gate 边界——与 provenance 审计同局限） |

---

## LIMITATIONS.md 更新

局限 3 案例列表追加一条实证（与 T005/T006/T016/T019 同级）：PeekView T068——P5 阶段实际看到 63 个预存失败，主 Agent 以"非本任务相关"一句话带过，未登记未排查，回归潜伏 3 天后才在下一个任务（T073）被发现。备注：本计划（P2.47/P2.48）将该案例的判定逻辑从"主 Agent 自证"改为"两次快照机械 diff"，缓解但不根治——见 0.5 节，P5 整体仍是 self-authored gate，快照文件本身理论上仍可被主 Agent 绕过（如 `--no-verify` 或手改 fail-list.txt），与 provenance 审计的已知局限同级。

---

## 落地顺序

| 优先级 | 项 | 依赖 |
|---|---|---|
| 1 | P2.47 捕获脚本 + P3/P4 挂载点 | 无 |
| 2 | P2.48 P5 diff 判定 + fail-list.txt 产出要求 | 依赖 P2.47（需要 pre-task-baseline.md 存在才能 diff） |
| 3 | LIMITATIONS.md 案例补充 | 依赖 1/2 落地后回填真实机制描述 |
| 4（不在本计划）| P5 整体 self-authored → external-output-gate 升级 | 见 0.5，建议后续独立立项 |
