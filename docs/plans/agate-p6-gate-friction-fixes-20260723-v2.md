# Plan：P6/派发链路 gate 脚本误判修复 + 文档-脚本口径统一

> 日期：2026-07-23
> 版本影响：minor bump（`agate-binary-marker-declaration-20260722.md` 已作为 PR #39 落地并核实通过，暂定本 plan 为 v0.18.0）
> **2026-07-23 更新**：`agate-binary-marker-declaration-20260722.md` 已合并（PR #39），已对照 PR #39 的实际 diff 重新核对本 plan 引用的行号——`phase-cards/P6-acceptance.md:65`（第四部分引用）未受影响，`pre-commit-gate.sh` 的多任务 phase-span 分支（第三部分）行号已漂移，具体更新见第三部分内文
> 来源：(1) 下游项目 T031+T067 迭代复盘的独立核实 (2) 用户对 P6 证据/gate 反复返工现象的追问，两次独立调查交叉指向同一类问题
> 破坏性变更：无（全部是修复误判 + 文档纠偏，不改变协议对"合规产出"的定义）

---

## 诚实标注

本 plan 里的每一条问题都用实际脚本 + 构造的最小复现验证过（非转述下游项目自述），复现命令保留在各部分「复现」小节，实施前可重跑确认未失效。**唯一未做代码验证、纯属文档层面判断的是第四部分**（md5 硬阻断与文档表述的冲突）——这条不改脚本行为，只改文档，理由见该部分说明。

**自评审时的一次自我纠正**：第一部分最初设计想去掉 `screenshots/` 优先提取分支、统一走"括号组+逗号切分"，写完后用最小复现脚本测试 `nth(1)` 嵌套括号场景时发现这版设计会让该场景完全提取不到路径（比现状更糟）。已推翻该设计，改为保留 `screenshots/` 优先提取、只改成多匹配+排除逗号，现方案已用四组输入验证。这个过程本身也是"不轻信自己第一版方案"纪律的体现，记录在此供实施者知晓这条弯路。

## 问题总览

用户观察："P6 环节的证据留痕/判定总要反复修改才能通过 gate，怀疑是 subagent 提示词指引不够好。"

逐层核实后的结论：**verifier.md / vision-analyst.md / dispatch-prompt.md 三层派发提示词已经相当详尽**（精确到 gate 用的正则原文、具体格式示例、T046 教训清单、强制自检循环），不是主要瓶颈。真正反复返工的根子在于：

1. **gate 脚本本身对某些合规写法解析失败**（provenance 多文件引用、inject-card 幂等性），subagent 写得没错，脚本判错
2. **协议文档之间、文档与脚本之间口径不一致**（md5 硬阻断 vs phase-card 仍写着"说明原因即可"），subagent 照着 A 文档做，被 B 脚本/文档的更严标准拦下
3. **少量脚本设计隐含了技术栈假设**（证据文件扩展名白名单），与 agate"协议层与技术栈无关"的定位有出入

这四类都不是"prompt 写得不够细"，是脚本/文档层面的问题，与 subagent 产出质量无关。

### 合理证据的三层模型——本 plan 能解决什么，解决不了什么

P6 证据的"合理性"可以拆成三层，讲清楚这一点是为了不让人误以为把 evidence/provenance 脚本改对了就等于"证据机制解决好了"：

| 层级 | 问题 | 谁负责 | 本 plan 能否解决 |
|------|------|--------|-----------------|
| 1. 格式有效性 | PASS 行是不是"看起来像"在引用证据文件 | `check-p6-evidence.sh` | **能**，第五部分解决 |
| 2. 存在性 | 引用的文件是不是真的存在、有没有被引用 | `check-p6-provenance.sh` | **能**，第一部分解决 |
| 3. 真实性 | 证据文件的内容是不是真的支撑了 PASS 结论（截图是不是真实 UI、不是纯色图充数） | 无脚本能做到 | **不能**，结构性限制 |

第一、二层是本 plan 实际在修的东西，修完之后这两层可以做到"对"——本 plan 已经逐条验证过。第三层不是这份 plan 的范围，也不是"还没想到办法"，而是 `LIMITATIONS.md` 里已经写明的结构性开放问题（self-authored gate：判定对象是 subagent 自己写的文件，写的人和判的人同源，脚本层面加多少格式检查都跨不过"内容是否为真"这条线）。治本方案是 `p6-gate-institutional-design-20260711.md` 方案④提出的"P6 证据由 CI 执行生成、agent 只引用"，目前只完成了"短期语义铺垫"（verifier 被要求优先引用 CI 产出，但明确标注"安全收益为零"），中期"CI 独立重新生成证据"尚未落地。**如果要真正解决第三层，下一步该评估的是下游项目有没有现成 CI 流水线可以接这个中期方案，而不是继续在 evidence/provenance 脚本上加正则**——这一点本 plan 不展开，留给后续单独评估。

---

## 第一部分：check-p6-provenance.sh 多文件引用解析

### 问题

`verifier.md:94` 明确允许"多条 PASS 可共享同一证据文件"，但反过来——**一条 PASS 引用多个证据文件**（逗号分隔）——脚本不支持。

### 复现

```bash
mkdir -p /tmp/provtest/T999/P6-evidence/screenshots
cd /tmp/provtest/T999
echo '- PASS BDD-1: something works (screenshots/file1.png, screenshots/file2.png)' > P6-acceptance.md
touch P6-evidence/screenshots/file1.png P6-evidence/screenshots/file2.png
bash {agate_root}/scripts/check-p6-provenance.sh .
# 实测输出：
# GATE PROVENANCE: P6-acceptance.md 有 1 条 PASS 引用的证据文件不存在
#   缺失路径: ./P6-evidence/screenshots/file1.png,   ← 注意尾随逗号
```

### 根因

`check-p6-provenance.sh:52` 的精确提取正则 `grep -oE 'screenshots/[^ )]+'` 排除了空格和右括号，**但没排除逗号**——遇到 `screenshots/file1.png, screenshots/file2.png` 时，`[^ )]+` 会一直匹配到下一个空格前，把逗号也吞进路径里，导致 `screenshots/file1.png,`（带尾随逗号）被当成文件路径去查，自然找不到。`:55` 的 fallback 括号提取同理，把整个括号内容当一个字符串处理，也不做逗号切分。

### 方案

**⚠️ 自评审时发现并推翻了第一版设计**：最初想把"优先提取 `screenshots/` 路径"（R1c 修复，专门为兼容 `nth(1)` 这类嵌套括号加的）整个去掉，统一改成"取行末括号组再按逗号切分"。**实测这版会让 `nth(1)` 场景完全提取不到路径**：`grep -oE '\([^)]+\)$'` 遇到 `(screenshots/b07.png — element: .katex nth(1))` 时，`[^)]+` 在碰到 `nth(1)` 内部那个 `)` 就断了，导致整体不匹配——从"能查出路径"退化成"该行完全跳过校验"，比现状更糟。已用最小复现脚本验证并推翻这版设计。

**改用下面这版**：保留 R1c 的 `screenshots/` 优先提取，只是把它从"`grep ... | head -1` 只取第一个匹配"改成"取所有匹配"，并在字符类里把逗号也排除掉（这样多个 `screenshots/` 引用之间能被逗号正确切开）；只有当一行完全没有 `screenshots/` 前缀命中时，才走 fallback 的"行末括号组 + 逗号切分"（这是原本就覆盖非截图证据的分支，未改变）。

```bash
# 改动 `check-p6-provenance.sh` 第 48-66 行（1a 检测循环）
while IFS= read -r line; do
    LINE_CLEAN=$(echo "$line" | sed 's/(vision:[^)]*)//g' | sed 's/[[:space:]]*$//')

    # 优先提取所有 screenshots/ 路径（保留 R1c 对 nth(1) 等嵌套括号的兼容；
    # 字符类新增排除逗号，使多个 screenshots/ 引用能被逗号正确分隔）
    mapfile -t REFS < <(echo "$LINE_CLEAN" | grep -oE 'screenshots/[^ ),]+' || true)

    if [ ${#REFS[@]} -eq 0 ]; then
        # fallback：无 screenshots/ 前缀命中时，取行末括号组按逗号切分（兼容非截图证据 + 多文件引用）
        REF_GROUP=$(echo "$LINE_CLEAN" | grep -oE '\([^)]+\)$' | sed 's/[()]//g' | head -1 || true)
        IFS=',' read -ra REFS <<< "$REF_GROUP"
    fi

    for REF in "${REFS[@]}"; do
        REF=$(echo "$REF" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        [ -z "$REF" ] && continue
        REF_CLEAN=$(echo "$REF" | sed 's|^P6-evidence/||' | sed 's|^p6-evidence/||' | sed 's|^evidences/||')
        REF_PATH="$EVIDENCE_DIR/$REF_CLEAN"
        if [ ! -f "$REF_PATH" ]; then
            MISSING_REFS=$((MISSING_REFS + 1))
            MISSING_DETAILS="${MISSING_DETAILS}  PASS行: ${line}\n  缺失路径: ${REF_PATH}\n"
        fi
    done
done < <(grep -E '^\s*- PASS\b' "$P6_FILE" 2>/dev/null || true)
```

**验证方式**：已用独立 bash 脚本对四种输入分别测试——`nth(1)` 单文件场景、`screenshots/` 逗号分隔多文件场景、非 `screenshots/`（如 `result1.json, result2.json`）逗号分隔多文件场景、原有单文件场景——全部提取出正确的路径列表，`nth(1)` 场景精确提取出 `screenshots/b07.png` 单个有效路径，不受影响。

### 测试

在既有 `agate/tests/unit/check-p6-provenance.bats`（已有 25 个用例）追加以下用例：

| 用例 | 描述 | 期望 |
|------|------|------|
| PROV_MULTI.1 | PASS 行引用 2 个逗号分隔的证据文件，均存在 | exit 0 |
| PROV_MULTI.2 | PASS 行引用 2 个逗号分隔的证据文件，其中 1 个不存在 | exit 1，报告缺失的那一个 |
| PROV_MULTI.3 | PASS 行含 `nth(1)` 等描述性嵌套括号 + 行末单一证据路径 | exit 0（回归：嵌套括号不影响行末提取） |
| PROV_MULTI.4 | PASS 行引用单一证据文件（原有场景） | exit 0（回归：不破坏既有行为） |

---

## 第二部分：agate-inject-card.sh 幂等注入误报修复

### 问题

对同一 phase 的 dispatch-context 文件重复调用 `inject-card.sh`（常见场景：一个 phase 派发多个角色，或补派发一个新角色时目录里已有其他已注入文件），已注入文件会被再次尝试注入并**报错退出**，尽管 `AGATE_CARD_START/END` 标记实际上并未消失。

### 复现

```bash
mkdir -p /tmp/injecttest && cd /tmp/injecttest
cat > P4-dispatch-context-implementer.md << 'EOF'
<!-- AGATE_CARD_START -->
<!-- AGATE_CARD_END -->
EOF
AGATE_ROOT={agate_root} bash {agate_root}/scripts/agate-inject-card.sh P4 .
# 第一次：成功，"AGATE_CARD 已注入"
AGATE_ROOT={agate_root} bash {agate_root}/scripts/agate-inject-card.sh P4 .
# 第二次（卡片内容未变）：
# AGATE_CARD 注入失败: P4-dispatch-context-implementer.md 中未找到 AGATE_CARD_START/END 占位符
# exit 1 ← 标记明明还在文件里，直接 grep 可验证
```

### 根因（比下游项目自述的诊断更精确）

`agate-inject-card.sh` 用 Python 的 `re.sub` 做替换，成功判定逻辑是 `if new_text == text: 报错`。这个判定**把"正则没匹配到"和"正则匹配到了、但替换结果与原文本恰好相同"混为一谈**——当同一 phase 的卡片内容没有变化时（最常见的情况：同一任务里给不同角色重复调用，卡片内容取决于 phase 而非角色，天然相同），第二次注入的替换结果和已注入的内容逐字节相同，`new_text == text` 恒成立，被误判为"没找到占位符"。

**这不是"占位符消失了"的问题**（标记本身在替换时被保留，不会消失），是**判定逻辑本身有缺陷**——用"输出是否变化"代替"是否匹配成功"。

### 方案

**改 `agate-inject-card.sh`**：判定逻辑从"比较替换前后文本是否相同"改为"直接检测正则是否匹配"（`re.search` 判断存在性，与是否替换、替换结果是否变化无关）。

```python
# 替换判定逻辑（当前实现，问题所在）：
new_text = re.sub(pattern, replacement, text, flags=re.DOTALL)
if new_text == text:
    print(f'AGATE_CARD 注入失败: ... 未找到占位符', file=sys.stderr)
    sys.exit(1)

# 改为：
if not re.search(pattern, text, flags=re.DOTALL):
    print(f'AGATE_CARD 注入失败: ... 未找到 AGATE_CARD_START/END 占位符', file=sys.stderr)
    sys.exit(1)
new_text = re.sub(pattern, replacement, text, flags=re.DOTALL)
```

**顺带处理下游项目复盘里的 T1**（可选，非阻断，一并做投入产出比更高）：脚本要求占位符预先存在，若目录里某个 dispatch-context 文件是主 Agent 手写、忘了带占位符，当前直接报错退出，主 Agent 需手动加占位符再重跑。可在"未匹配到占位符"分支追加自动降级：若文件末尾没有 `AGATE_CARD_START/END`，自动追加一对空占位符再注入，而非直接报错。**这条改动改变了脚本对"异常输入"的容错行为（从报错变成自动补救），风险高于 T2 的纯判定逻辑修复，建议作为独立子项，可选实施，不影响本 plan 其余部分**。

### 测试

在既有 `agate/tests/unit/agate-inject-card.bats`（已有 8 个用例）追加：

| 用例 | 描述 | 期望 |
|------|------|------|
| IC_IDEMPOTENT.1 | 对已注入且卡片内容未变的文件重复调用 | exit 0（原为 exit 1，回归修复） |
| IC_IDEMPOTENT.2 | 对已注入但卡片内容确实变化（如 phase card 本身被改过）的文件重复调用 | exit 0，内容被更新为新卡片 |
| IC_MISSING.1 | 文件完全没有 AGATE_CARD_START/END 占位符（T2 修复不含 T1 自动降级） | exit 1（占位符不存在，脚本报错） |
| IC_MISSING.2 | 文件完全没有 AGATE_CARD_START/END 占位符（若实施 T1 自动降级） | exit 0，自动追加占位符后注入成功 |

---

## 第三部分：pre-commit-gate.sh phase 跨度 WARNING 误报

### 问题

当 P1/P2/P3（或任意跨阶段）产出文件在**同一次 commit 中被新增**（常见场景：主 Agent 在一个会话内连续推进多个阶段，最后一次性 commit），gate 按"文件名阶段号 vs 当前 `.state.yaml` phase"做比较，凡是阶段号 ≠ 当前 phase 就报 WARNING——**不检查这些文件是不是本次 commit 新增的**。新增文件被判定为"跨阶段产出"纯属误报，会产生噪音，稀释真正的 WARNING 信号（也是本项目在其他地方反复强调要避免的"WARNING 疲劳"）。

### 复现

**（已针对 PR #39 合入后的行号重新核对，见下方"PR #39 落地后的行号更新"）**对照 `pre-commit-gate.sh:79-91`（单任务分支，PR #39 未改动此区间，行号不变）与多任务分支（PR #39 落地后已从 :276-292 漂移到约 :264-298，见下方修正）逻辑：两处都只用 `git diff --cached --name-only` 拿到暂存文件名，提取阶段号后直接和 `.state.yaml` 当前 phase 比较，未调用 `--diff-filter` 或检查文件在 `HEAD` 是否已存在。构造一次"P1+P2+P3 产出与 phase=P3 一起首次 commit"的场景即可复现（三个文件都是新增，P1/P2 会被误报）。

### PR #39 落地后的行号更新（本 plan 起草时 PR #39 尚未合并，现已核对）

`agate-binary-marker-declaration-20260722.md`（PR #39）在 `pre-commit-gate.sh` 的 PROD_TOUCHED 检测段（原 :107 附近）插入了约 6 行三步检测逻辑，导致其后的多任务 phase-span 分支整体下移。实测核对：

- 单任务分支：warning 输出行仍在 **:91**，判断逻辑仍在 **:79-91** 区间，未受影响
- 多任务分支：`只做 WARNING，不拦截` 注释行现在在 **:270**，`for`/`while` 循环体现在约 **:279-297**（原 plan 写的 :276-292 已过期，实施前请以 `grep -n "只做 WARNING，不拦截" agate/scripts/pre-commit-gate.sh` 重新定位为准，不要直接套用下方行号）

以下方案描述保持不变（改动内容本身不受行号漂移影响，只是插入位置需要重新定位）。

### 方案（最终版：加了方向判断，修复了初版会破坏既有测试的问题）

> **本节修订说明**：初版方案是"只要是本次新增文件就跳过 WARNING"，评审时发现这会破坏既有测试 `IT.7`（`pre-commit-hook.bats:192`：P4 产出文件首次新增、但 phase 仍是 P3 时，**必须**报 WARNING——这是"提前产出、忘记推进 phase"的合法信号，不能被误删）。原因是"新增文件"不等于"合规文件"——新增文件分两种：一种是**历史阶段的产出补提交**（如 phase 已经推进到 P3，但 P1 的产出因为某种原因这次才一起新增提交），这种该跳过 WARNING；另一种是**超前阶段的产出**（如 phase 还在 P3，但 P4 的产出已经先写好新增了），这种必须继续报 WARNING。区分依据是阶段号和当前 phase 的**大小关系**，不是"是否新增"本身。

**改动两处（`:79-91` 单任务分支、多任务分支）**：在提取阶段号后，只对"阶段号 < 当前 phase 且本次新增"的文件跳过 WARNING（历史产出晚提交）；"阶段号 > 当前 phase"的新增文件（提前产出）仍然报警。

```bash
# 单任务分支修改（:79-91 区域追加判断）：
STAGED_ADDED=$(git diff --cached --diff-filter=A --name-only 2>/dev/null \
    | grep -E "^${TASK_REL}/P[0-8]-.*\.md$" || true)
...
if [ -n "$out_phase" ] && [ "$out_phase" != "$PHASE" ]; then
    out_num=${out_phase#P}
    phase_num=${PHASE#P}
    # 数字守卫：PHASE 在跳过 gate 阶段的场景下可能是 PAUSED/READY/DONE 等非数字值
    # （单任务分支的 PAUSED|READY|DONE 守卫在本检查之后才生效，见 :96-98）。
    # 若不加这层数字校验，`-lt` 遇到非数字操作数会在 stderr 打印
    # "integer expression expected" 的报错噪音（因为这段比较包在 if 条件里，
    # bash 的 set -e 对 if/while 条件命令天然豁免，不会导致整个 hook 中止，
    # 但报错信息会让人误以为出了严重问题，体验上值得避免）。
    if [[ "$out_num" =~ ^[0-9]+$ ]] && [[ "$phase_num" =~ ^[0-9]+$ ]] \
        && [ "$out_num" -lt "$phase_num" ] \
        && echo "$STAGED_ADDED" | grep -qxF "$out_file"; then
        continue
    fi
    echo "GATE WARNING: 暂存了 ${out_phase} 产出但 phase=${PHASE}（${TASK_ID}）——请确认是否需要更新 phase" >&2
fi
```

多任务分支（现约 :279-297，实施前以 `grep -n "只做 WARNING，不拦截" agate/scripts/pre-commit-gate.sh` 重新定位，变量名不同）做同类改动：

```bash
# 多任务分支修改（变量名与单任务分支不同：task_phase 非 PHASE、staged_file 非 out_file）：
STAGED_ADDED_MULTI=$(git diff --cached --diff-filter=A --name-only 2>/dev/null \
    | grep -E "^${task_dir_rel}/P[0-8]-.*\.md$" || true)
...
if [ -n "$out_phase" ] && [ "$out_phase" != "$task_phase" ]; then
    out_num=${out_phase#P}
    phase_num=${task_phase#P}
    if [[ "$out_num" =~ ^[0-9]+$ ]] && [[ "$phase_num" =~ ^[0-9]+$ ]] \
        && [ "$out_num" -lt "$phase_num" ] \
        && echo "$STAGED_ADDED_MULTI" | grep -qxF "$staged_file"; then
        continue
    fi
    echo "GATE WARNING: 暂存了 ${out_phase} 产出但 phase=${task_phase}（${task_dir_rel##*/}）——请确认是否需要更新 phase" >&2
fi
```

**已用四组场景实测验证方向判断的正确性**（独立 bash 脚本模拟，非仅推理）：

| 场景 | phase | 新增文件阶段号 | 是否本次新增 | 期望 | 实测结果 |
|------|-------|--------------|-------------|------|---------|
| 历史产出晚提交 | P3 | P1 | 是 | 跳过 WARNING | ✅ SKIP |
| 提前产出（IT.7 场景） | P3 | P4 | 是 | 报 WARNING | ✅ WARN |
| PHASE 非数字（PAUSED） | PAUSED | P4 | 是 | 不崩溃，报 WARNING（安全默认值） | ✅ WARN，无 abort |
| 历史遗留、非本次新增 | P3 | P1 | 否 | 报 WARNING（真实过期场景） | ✅ WARN |

### 测试

在既有 `agate/tests/integration/pre-commit-hook.bats`（已有 12 个用例，PR #39 落地后为 19 个）追加：

| 用例 | 描述 | 期望 |
|------|------|------|
| IT_PHASE_SPAN.1 | 一次 commit 同时新增 P1/P2 产出文件，phase=P3（阶段号 < 当前 phase，历史产出晚提交） | 不报 WARNING（回归修复） |
| IT_PHASE_SPAN.2 | P1 产出文件是先前 commit 已存在的（非本次新增），phase 已推进到 P3，本次 commit 只改了别的文件但 P1 文件仍在暂存区（如误 `git add .`） | 报 WARNING（真实过期场景，不能被修复误删） |
| IT_PHASE_SPAN.3 | 新增 P4 产出文件，phase=P3（阶段号 > 当前 phase，提前产出，即 `IT.7` 的单任务等价场景） | 报 WARNING（**提前产出是合法 WARNING，方向判断必须保留，这条测试直接防止未来重犯"一律跳过"的错误**） |
| IT_PHASE_SPAN.4 | 多任务场景重复 IT_PHASE_SPAN.1/.2/.3 | 同上 |
| IT_PHASE_SPAN.5 | `.state.yaml` 的 phase 为 `PAUSED`，暂存了阶段号不符的新增文件 | 不崩溃、报 WARNING，且 stderr 不出现 `integer expression expected` 报错噪音 |

---

## 第四部分：md5 完全重复截图——文档口径统一（纯文档修复，不改脚本行为）

### 问题

`phase-cards/P6-acceptance.md:65` 现在仍写着：

> "行为差异类 BDD 截图可能视觉相同（md5 重复），建议在 acceptance report 说明原因"

但 `check-p6-evidence.sh` 对 md5 完全重复截图是**硬阻断**（`exit 1`，v0.16.0 CHANGELOG 记录的 BREAKING 变更：从 exit 2 WARNING 升级为 exit 1），脚本里没有任何"读取 acceptance report 里的说明文字来放行"的逻辑分支——这行指引描述的退路在 v0.16.0 就已经不存在了，但文档没有跟着改，属于文档滞后一天导致的漂移（`P6-acceptance.md` 该行写于 07-21，md5 升级发生在 07-22）。

**更值得注意的是**：同一份角色文件 `verifier.md:136` 自己的表述其实是对的——"操作类 BDD 截图必须互不相同（md5 去重，**hook 强制**）"，与脚本行为一致。**这是两份协议文档在同一件事上互相矛盾**，subagent 读到哪一份就会形成不同预期，读到 phase-card 的 verifier 会认为"写个原因就能过"，实际会被拦。

### 为什么这条不改脚本（不加"说明原因就放行"的例外）

如果给 md5 硬阻断加一个"acceptance report 里写了解释就放行"的例外，等于允许 subagent 用自由文本为自己的证据造假开脱——这正是 `agate-binary-marker-declaration-20260722.md` 那份 plan 反复强调、且本项目一贯坚持的原则："协议就是协议，不能靠 agent 自证的自由文本当放行凭据"。produce=judge=editor 同体时，"我在报告里解释了"这件事本身不构成客观证据。所以这里**不该开这个口子**，该改的是文档，让文档和实际执行口径一致。

### 方案

**改 `phase-cards/P6-acceptance.md:65`**，把已经失效的"建议说明原因"表述，替换为与 `verifier.md:136` 一致、且给出可执行替代方案的指引：

```
- 操作类 BDD 截图必须互不相同（md5 完全重复会被 hook 硬阻断，无例外）。
  若某个行为差异类 BDD 天然会产出视觉相同的页面（如两个不同查询都命中同一个空状态），
  优先改用非截图证据（断言日志 / response.json）而非截图，或截图时带上能体现差异的元素
  （如带时间戳的调试面板、高亮差异区域），确保截图本身逐字节不同。
  查询类 BDD 本来就可以不截图，这类场景应优先归为查询类而非勉强用截图。
```

同时检查全仓库是否还有其他地方残留"说明原因即可"式的过时表述（`grep -rn "说明原因" agate/`），逐一核对是否与当前脚本行为一致。

### 测试

这是纯文档变更，不新增脚本测试。建议新增 `check-protocol-consistency.py` 一致性锚点：

| 锚点 | script | keywords |
|------|--------|----------|
| md5 完全重复截图阻断口径一致性 | `phase-cards/P6-acceptance.md` | 检查该文件不含"建议在 acceptance report 说明原因"这类与硬阻断矛盾的表述（反向锚点：keywords 存在则 FAIL，而非常规的"必须存在"）——若 `check-protocol-consistency.py` 当前只支持"关键词必须存在"型锚点，不支持"关键词必须不存在"型，这条需要先扩展锚点类型，或退化为人工核对，本 plan 不在此展开脚本层面的锚点机制扩展，留作独立事项 |

---

## 第五部分：check-p6-evidence.sh 证据引用检测——结构判定 + provenance 兜底（最终版）

> **本节修订说明**：这部分经过两轮修订。第一版（本 plan 最初稿）用"扩展名白名单泛化"，被指出对"哪些扩展名算数"仍然武断。第二版（PR #40 修订）改为"结构判定"，方向正确，但推荐的正则末尾锚定 `\)$`，实测会把第一部分刚修好的逗号分隔多文件引用重新判定为"缺引用"，在 `check-p6-evidence.sh` 这一关抢先拦截，让第一部分的修复形同虚设。这里是修复了该回归后的最终版本，已用完整用例集合（含 nth(1) 嵌套括号、逗号多文件、纯版本号、纯描述文字四类边界场景）逐一实测。

### 问题

`check-p6-evidence.sh:33` 的 PASS 行证据引用检测原本用固定扩展名白名单（`png/jpg/log/json/html/txt/yaml/yml` 八种），这与 agate 协议自己声明的"证据形式不限，不绑定技术栈"（`verifier.md:41`）相矛盾。

### 根因分析

白名单正则的本质是"用扩展名像不像文件来判断括号内容是不是文件引用"——这是一个先天脆弱的启发式判断：扩展名列全约等于没列（`\.[a-zA-Z0-9]{1,6}` 这种通配等于什么扩展名都认），列不全约等于假设了技术栈。

**正确思路**：不用扩展名去猜"是不是文件"，改用"括号内容有没有路径/文件结构特征"来判断"是不是证据引用"，真假交给 `check-p6-provenance.sh` 做硬验证（它已经会检查文件是否真实存在）。两个脚本的分工：

| 脚本 | 检查什么 | 方法 |
|------|---------|------|
| `check-p6-evidence.sh:33` | PASS 行**是否含疑似文件引用**（前置软过滤） | 结构判定（只看文本模式，不判断真伪） |
| `check-p6-provenance.sh` 1a | 引用的文件**是否真实存在**（硬验证，第一部分已支持逗号多文件） | 提取路径 → `[ -f ]` |

evidence 层的误判方向应该"宁可多放，不可少放"：把"看起来像引用但其实是版本号"之类的边界情况放过去，交给 provenance 用"文件存不存在"做最终裁决（`(v2.0)` 根本不是真实路径，provenance 一样会报"文件不存在"拦下来，只是拦截点从 evidence 换成 provenance，结果一致）；但绝不能把"合法的引用格式"误判为"缺引用"，因为 evidence 层没有下一道防线兜底这种误判——一旦在这里被拦，subagent 根本走不到 provenance 那一步去自证清白。

### 方案（已修复与第一部分的冲突，最终版本）

```bash
# 改动前（:33）：
grep -qE '\([a-zA-Z0-9_/.-]+\.(png|jpg|log|json|html|txt|yaml|yml)[^)]*\)'

# 改动后（最终版，不锚定行末，末尾用 [^)]* 兼容任意描述性后缀）：
grep -qE '\([a-zA-Z0-9_/. -]*[a-zA-Z0-9_-]\.[a-zA-Z0-9]+[^)]*\)'
```

**与 PR #40 修订版的关键差异**：PR #40 版本末尾锚定 `\)$`（要求"文件名.扩展名"结构必须紧贴右括号），逗号分隔的第二个文件名会破坏这个锚定。最终版把末尾换回 `[^)]*\)`（不锚定，任意非右括号字符都可以跟在有效的"文件名.扩展名"之后，包括逗号、空格、第二个文件名、中文描述、嵌套括号里的 `nth(1)` 等）——这正是当前脚本已经在用、已被验证兼容 `nth(1)` 场景的写法，只是把"扩展名必须在白名单里"这个限定去掉，换成"只要有 `文件名.扩展名` 这个结构就算"。

**已用 10 组边界场景实测验证**（非仅推理）：

| 输入 | 判定 | 说明 |
|------|------|------|
| `(screenshots/file.png)` | 有效引用 | 常规单文件 |
| `(result.json)` | 有效引用 | 无路径前缀，纯文件名 |
| `(file1.png, file2.json)` | 有效引用 | **逗号多文件，与第一部分兼容**（PR #40 版本会误判为无效） |
| `(screenshots/file1.png, screenshots/file2.png)` | 有效引用 | 同上，`screenshots/` 前缀场景 |
| `(response.pdf)` | 有效引用 | 非白名单扩展名，泛化后可识别 |
| `(v2.0)` | 有效引用（误判，但安全） | 不是真实路径，留给 provenance 用"文件不存在"拦截 |
| `(no reference here)` | 无效（判定缺引用） | 正确排除纯描述文字 |
| `(约1.5x)` | 无效（判定缺引用） | 非 ASCII 字符不在允许字符类内，正确排除 |
| `(screenshots/b07.png — element: .katex nth(1))` | 有效引用 | **`nth(1)` 嵌套括号场景，回归测试通过** |
| `(screenshots/b07.png — element: .katex nth(1)) (vision: vision.yaml)` | 有效引用 | 同上 + vision 引用共存场景 |

### 权衡说明（为什么接受 `(v2.0)` 这类误判）

`(v2.0)` 被误判为"有效引用"，看起来是精度损失，但结合 `check-p6-provenance.sh` 的硬验证（第一部分已修复的版本），这个误判是**安全的**：evidence 层放行只是"过了前置格式检查"，provenance 层会去查 `v2.0` 对应的文件是否存在，查不到照样拦截——只是报错信息从"缺证据引用"变成"证据文件不存在"，对 subagent 的最终结果（gate 不通过，需要修正）没有区别。反过来，如果为了排除 `(v2.0)` 这类误判而收紧正则（比如要求"扩展名前必须有非数字字符"），代价是必须重新验证这类收紧不会像 PR #40 版本那样又意外破坏多文件场景——本 plan 评估后认为**不值得为了这点精度去冒二次引入回归的风险**，两层防御已经能兜住实际风险，不需要在 evidence 层做到完美排除。

### 为什么不选其他方案

| 方案 | 问题 |
|------|------|
| 扩展名白名单扩展到 ~20 种 | 列全约等于没列，列不全约等于假设技术栈，且每次出现新格式都要改脚本，维护成本持续存在 |
| 环境变量 `AGATE_EVIDENCE_EXTRA_EXTENSIONS` 追加扩展名 | 合规标准因运行环境的环境变量配置而异，与"协议就是协议"的原则冲突——同一份 P6-acceptance.md 在没设置这个环境变量的机器上会被判定不合规，在设置了的机器上通过，这种"环境决定合规性"的模式在本仓库其他地方（标记声明规范）已经被明确排除过一次 |
| 结构判定但锚定行末 `\)$`（排除纯版本号误判） | 实测会破坏第一部分的逗号多文件引用支持，属于本节开头说明的真实回归，已排除 |
| **结构判定 + provenance 兜底（本节最终方案）** | 不枚举扩展名，靠"文件名.扩展名"结构特征判断，边界误判（如 `v2.0`）交给 provenance 的存在性硬验证兜底，两层职责边界清晰，且已用 10 组场景实测验证不与第一部分冲突 |

### 测试

在既有 `agate/tests/unit/check-p6-evidence.bats`（已有 14 个用例）追加：

| 用例 | 描述 | 期望 |
|------|------|------|
| EVID_EXT.1 | PASS 行引用 `.pdf` 文件 | exit 0（原为判定"缺引用"，回归修复） |
| EVID_EXT.2 | PASS 行引用 `.jpeg` 文件 | exit 0（同上） |
| EVID_EXT.3 | PASS 行引用逗号分隔的 2 个证据文件（`screenshots/a.png, screenshots/b.png`） | exit 0（**与第一部分的交叉回归测试，必须保留，防止未来再次引入同类冲突**） |
| EVID_EXT.4 | PASS 行含 `nth(1)` 嵌套括号 + 单一证据路径 | exit 0（回归：`nth(1)` 场景不受影响） |
| EVID_EXT.5 | PASS 行括号内容是纯版本号 `(v2.0)`，且 `P6-evidence/` 目录下确无 `v2.0` 对应文件 | evidence 层 exit 0（放行），但整体 P6 gate 链路应在 provenance 层 exit 1（组合验证两层分工正确） |
| EVID_EXT.6 | PASS 行括号内容是纯描述文字，无路径/扩展名结构 | 判定"缺引用"，exit 1 |
| EVID_EXT.7 | 现有 png/jpg/log/json/html/txt/yaml/yml 用例 | 全部保持 exit 0（回归） |

**EVID_EXT.5 是本节最重要的一条测试**——它不是单独跑 `check-p6-evidence.sh`，而是要跑完整的 P6 gate 链路（evidence → provenance），验证"evidence 放宽 + provenance 兜底"这个两层分工组合起来确实能拦住 `(v2.0)` 这类边界输入，不是纸面论证。

---

## 第六部分：TEST_RUNNER 逃生舱可发现性（纯文档补充）

### 问题

`check-tdd-red.sh` 已经支持 `TEST_RUNNER` 环境变量接入任意测试运行器（源码注释："回退链：`$TEST_RUNNER` → `which pytest` → `exit 3`"），**这个能力本身没有 bug**。但下游项目在实践中没发现这个开关，遇到非 pytest 技术栈时选择了手动跑测试当 workaround，而不是设置 `TEST_RUNNER` 让脚本正常介入检测流程——说明这个逃生舱在协议文档层面不够醒目。

### 方案

在 `phase-cards/P3-tdd.md` 和 `phase-cards/P5-verification.md` 里各补充一行（具体行号需实施时按当前文件核对，此 plan 不做行号假设，因为这是新增内容不是替换已有内容）：

```
非 pytest 技术栈：设置 `TEST_RUNNER` 环境变量指向项目实际测试命令（如 `TEST_RUNNER="npm test"`），
check-tdd-red.sh 会使用该命令而非默认的 pytest 探测。这是 agate 协议保持技术栈无关的标准接入点，
不需要绕过脚本手动验证。
```

同时在 `verifier.md`（P5 技术验证模式）里补充同样一句提示，确保 subagent 自己也知道这个入口，而不只是主 Agent 知道。

### 测试

纯文档变更，无需新增脚本测试。若想做一致性校验，可在 `check-protocol-consistency.py` 里加一条锚点确认 `TEST_RUNNER` 关键词在 phase-cards/P3-tdd.md 或 P5-verification.md 中出现。

---

## 第七部分：文档传播清单

| 文件 | 改动类型 | 涉及部分 |
|------|---------|---------|
| agate/scripts/check-p6-provenance.sh | 脚本修复 | 第一部分 |
| agate/scripts/agate-inject-card.sh | 脚本修复 | 第二部分 |
| agate/scripts/pre-commit-gate.sh | 脚本修复 | 第三部分（两处：单任务分支 + 多任务分支） |
| agate/scripts/check-p6-evidence.sh | 脚本修复 | 第五部分 |
| phase-cards/P6-acceptance.md | 文档修正 | 第四部分（md5 口径统一） |
| phase-cards/P3-tdd.md | 文档补充 | 第六部分 |
| phase-cards/P5-verification.md | 文档补充 | 第六部分 |
| assets/execution-roles/verifier.md | 文档补充 | 第六部分（TEST_RUNNER 提示） |

## 第八部分：与已有 plan 的关系

| 已有 plan/评审 | 关系 |
|---------|-----------|
| `docs/plans/agate-binary-marker-declaration-20260722.md` | 已合并（PR #39）。独立、互不冲突，都改动 `pre-commit-gate.sh` 和 `phase-cards/P6-acceptance.md` 的不同章节，已核对合并后行号（见第三部分） |
| `docs/reviews/agate-binary-marker-declaration-plan-review-2026-07-23.md` | 本 plan 第四部分坚持"不给自由文本开放行口子"的原则，与该评审认可的 binary-marker plan 核心哲学一致 |
| `1784771927999_T031-T067-retrospective-2026-07-23.md`（下游项目复盘，非 agate 仓库内文档） | 本 plan 第一、二、三、六部分是对该复盘 T4/T2/A5/T3 的独立核实和修复方案，复盘对 T4/A5 的诊断准确，对 T2 的根因诊断有误差（已在第二部分说明），对 T3 的建议部分已经是 agate 现有能力（文档发现性问题非代码问题） |
| 本 plan 自身的修订历史（PR #40 → 本次最终版） | PR #40 修订过本 plan 的第二、三、五部分：第二部分（IC_MISSING 拆分）和第三部分（phase 跨度方向性判断）的修订经核实是正确且必要的（第三部分修正了一处会破坏既有测试 IT.7 的真实缺陷，虽然其中"会 abort 整个 hook"的论证经实测证明有夸大，已在本版本更正措辞但保留代码修复）；第五部分的修订方向正确（扩展名白名单→结构判定）但推荐的正则与第一部分的多文件引用支持互相冲突，本版本已修复并给出可直接实施的最终正则

## 第九部分：版本与 CHANGELOG

```markdown
## [0.18.0]（版本号待实施时按实际发布序列确认）

### 修复
- check-p6-provenance.sh 支持逗号分隔的多文件证据引用（原会把逗号和空格当路径一部分导致误判缺失）
- agate-inject-card.sh 幂等注入误报修复：判定逻辑从"替换前后文本是否相同"改为"正则是否匹配"，
  消除同一 phase 卡片内容未变时重复注入被误判为"占位符缺失"的问题
- pre-commit-gate.sh phase 跨度 WARNING 误报修复：阶段号低于当前 phase 的新增文件（历史产出晚提交）
  不再被误判为"过期跨阶段产出"；阶段号高于当前 phase 的新增文件（提前产出）仍正确报 WARNING，
  修复带方向判断以避免破坏既有测试 IT.7
- check-p6-evidence.sh 证据引用检测从扩展名白名单改为结构判定（含路径分隔符或"文件名.扩展名"结构即视为
  有效引用，不再枚举扩展名；不锚定行末，与 check-p6-provenance.sh 的逗号多文件解析兼容；边界误判交给
  provenance 的文件存在性硬验证兜底）

### 变更
- phase-cards/P6-acceptance.md 更正 md5 完全重复截图的处理指引，与 verifier.md 及脚本实际行为
  （hook 硬阻断，无例外）保持一致

### 新增
- phase-cards/P3-tdd.md、P5-verification.md、verifier.md 补充 TEST_RUNNER 环境变量的可发现性提示
  （能力已存在，仅补充文档醒目度）
```

## 第十部分：实施顺序

1. `agate-binary-marker-declaration-20260722.md`（PR #39）已合并，行号已核对（见第三部分），实施前仍建议 `git pull` 确认没有更晚的改动再次导致漂移
2. 第一部分（provenance 多文件）：先写失败测试 → 改脚本 → 确认绿
3. 第二部分（inject-card 幂等性）：先写失败测试 → 改脚本 → 确认绿
4. 第三部分（phase 跨度误报）：先写失败测试 → 改脚本 → 确认绿
5. 第五部分（证据扩展名泛化）：先写失败测试 → 改脚本 → 确认绿
6. 第四、六部分（纯文档修正/补充）
7. 跑全量测试确认无回归：
   ```bash
   bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
   python3 agate/scripts/check-protocol-consistency.py
   bash agate/tests/scripts/count-tests.sh
   shellcheck -S warning agate/scripts/*.sh
   ```
8. CHANGELOG + 版本号确认（需与 binary-marker plan 的版本序列协调，避免重复占用同一版本号）
9. self-gate：派发 protocol-alignment-review
