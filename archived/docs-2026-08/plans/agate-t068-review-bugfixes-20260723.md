# Plan：T068 复盘 review 三个 agate gate bug 修复

> 日期：2026-07-23
> 版本影响：minor bump（v0.19.0 -> v0.20.0，T3 从 exit 1 降级为 exit 2 是行为变更）
> 破坏性变更：无。T6 修复收窄了步骤2 拦截范围（不再拦 AGATE_CARD 注入文本），但真正的声明性标记仍被步骤1 拦截。T3 和 M5 修复了计数逻辑，行为更准确。
> 来源：`docs/reviews/review-20260723-2311.md` T068 复盘报告，经逐条代码核实后确认 3 个 agate gate bug

---

## 诚实标注

1. 本 plan 的三个 bug 均经代码核实（非推测），每个都定位到具体代码行 + 运行时验证：
   - T3/M2：`check-p6-provenance.sh:131` `grep -cE '^\s*-?\s*Given\b'` -- Given 行数 != BDD 编号数
   - T6：`pre-commit-gate.sh:134` `grep -q '\[PROD_TOUCHED\]'` -- 步骤2 无行首锚点，误匹配 AGATE_CARD 注入的卡片说明文本
   - M5：`check-gate.sh:148` `grep -cE '^\s+- '` -- 统计所有缩进 bullet 行，非 gate_commands.P5 YAML 块内的命令

2. review 中其余 9 个问题（T1/T2/T4/T5/M1/M3/M4/M6）经核实**不是 agate gate bug**：
   - T1（主 Agent P6 改代码）：v0.19.0 已解决（E3 硬拦截）
   - T2（证据质量问题）：acceptor 用户行为，gate 正确拦截了 4 类不合规证据
   - T4（P3 测试覆盖不足）：test-designer 职责，非 gate 问题
   - T5（inject-card 路径）：目录结构问题，PR #46 目录改名 plan 处理中（paused）
   - M1（8 次 commit 失败）：7 次是用户错误（gate 正确拦截），1 次是 T3 bug
   - M3（回退流程不清晰）：v0.19.0 已解决
   - M4（DESIGN_GAP 格式）：v0.17.0 已解决（行首锚点）
   - M6（已知限制未跟踪）：workflow 问题，非 gate 职责

3. **T6 修复有一个需要仔细考虑的设计张力**：步骤2 的目的是拦截"不合规的 PROD_TOUCHED 格式"（句中引用而非行首声明）。如果直接加行首锚点，就等于取消了步骤2，那些真正"写了但格式不对"的声明就不会被拦。修复方向应该是排除 AGATE_CARD 注入块，而非削弱步骤2 的检测能力。详见问题三分析。

---

## 问题一：T3/M2 -- BDD 计数按 Given 行数，一个 BDD 多个 Given 块时虚增

### 根因（已核实）

`check-p6-provenance.sh:131`：
```bash
P1_BDD=$(grep -cE '^\s*-?\s*Given\b' "$P1_FILE" 2>/dev/null || echo 0)
```

这个 grep 统计 P1-requirements.md 中所有以 `Given` 开头（允许前导空白和 `-`）的行。当一条 BDD 有多个 Given 块（如"已登录"和"未登录"两个场景）时，Given 行数 > BDD 编号数，导致 `P6_TOTAL < P1_BDD` 误判"挑验不通过"。

协议文档明确声明"BDD 编号格式不固定"（P1-requirements.md:49、state-machine.md:390），所以脚本无法用固定正则按编号计数。但 Given 行数也不可靠 -- 一条 BDD 可以有多个 Given（多场景），也可以没有 Given（非 BDD 格式的验收条件）。

### 方案：将审计 3 的 exit 1 降级为 exit 2（WARNING）

协议明确声明"BDD 编号格式不固定"（P1-requirements.md:49、state-machine.md:390），所以任何试图按固定格式计数的方法都不可靠。现有测试 fixture 用的格式包括 `- Given`（fixtures.bash:111）、`AC1: Given`（tests/fixtures/full-task/P1-requirements.md）、`- ✅ Given`（analyst.md:122）--三种格式都不含 `BDD` 字样。按 BDD 标题计数会导致所有这些格式退化为 `P1_BDD=0`（exit 2），静默禁用挑验检查。

**正确做法**：既然"BDD 编号格式不固定"+"主 Agent 手动核实"已经是协议的明确立场，脚本不应该试图做精确计数并硬阻（exit 1）。改为 WARNING（exit 2）--仍然提示数量差异，但不拦截 commit。主 Agent 仍需手动核实，但这本来就是协议要求的。

```bash
# 修复前（check-p6-provenance.sh:127-146）：
# P1_BDD=$(grep -cE '^\s*-?\s*Given\b' "$P1_FILE" 2>/dev/null || echo 0)
# P1_BDD=$(echo "$P1_BDD" | tail -1)
# ...
# if [ "$P6_TOTAL" -lt "$P1_BDD" ]; then
#     echo "GATE PROVENANCE: P6 结果数(${P6_TOTAL}) < P1 BDD 条目数(${P1_BDD})，挑验不通过" >&2
#     exit 1
# fi

# 修复后：保留 Given 行计数作为启发式下界，但降级为 WARNING
P1_BDD=$(grep -cE '^\s*-?\s*Given\b' "$P1_FILE" 2>/dev/null || echo 0)
P1_BDD=$(echo "$P1_BDD" | tail -1)
# ... P6_TOTAL 计数不变 ...
if [ "$P1_BDD" -gt 0 ]; then
    if [ "$P6_TOTAL" -lt "$P1_BDD" ]; then
        echo "GATE PROVENANCE WARNING: P6 结果数(${P6_TOTAL}) < P1 Given 行数(${P1_BDD})，可能存在挑验遗漏（BDD 编号格式不固定，需主 Agent 手动核实）" >&2
        # 不 exit 1，降级为 WARNING--降为 exit 2 由外层 check-gate.sh P6 分支处理
    fi
else
    echo "GATE PROVENANCE: P1 BDD 格式非标准（无 Given 行），BDD 总数对照需主 Agent 手动核实" >&2
    exit 2
fi
```

**注意**：`check-p6-provenance.sh` 是被 `pre-commit-gate.sh` 调用的子脚本。当前 P6 审计链路是：`check-gate.sh P6 -> exit 2 -> pre-commit-gate.sh` 调 `check-p6-provenance.sh`（exit 0/1/2）。改后审计 3 不再 exit 1（除非有其他审计 1/2/4/5 拦截），只输出 WARNING 文本。WARNING 文本会出现在 gate 输出中，主 Agent 能看到。

**为什么这是正确的降级**：
1. 协议已经说"BDD 编号格式不固定，主 Agent 自行判定"--脚本做了精确计数反而与协议矛盾
2. Given 行数本身是启发式（一条 BDD 可以有多个 Given），不可作为硬阻断依据
3. 降为 WARNING 后，P7 一致性检查仍会做 P1 BDD 数 vs P6 PASS 数的交叉核对（`P7-consistency.md:30`、`P7-consistency.md:81`），不是完全无监督
4. 其他审计（1/2/4/5）仍硬阻，挑验的核心保障（证据存在性、dispatch-context 审计、vision YAML、EXIT_CODE 审计）不变

### 测试

| 用例 | 描述 | 期望 |
|------|------|------|
| PV_BDD_COUNT.1 | P1 含 3 条 Given（各 1 个），P6 有 3 条 PASS | exit 0（正常路径回归） |
| PV_BDD_COUNT.2 | P1 含 2 条 Given（1 条 BDD 多场景），P6 有 1 条 PASS | exit 0 + WARNING 含"可能存在挑验遗漏"（**核心修复**：不再 exit 1 误拦） |
| PV_BDD_COUNT.3 | P1 无 Given 行 | exit 2（兜底，回归 PV.10） |
| PV_BDD_COUNT.4 | P1 含 4 条 Given，P6 有 2 条 PASS | exit 0 + WARNING（降级后不硬拦，但仍提醒） |

**现有测试影响**：
- PV.9（4 Given vs 1 PASS -> 原 exit 1）：改为 exit 0 + WARNING。需更新断言。
- 其他 PV 测试（1 Given vs 1+ PASS）：不受影响，exit 0 不变。

---

## 问题二：M5 -- P5 gate_commands 计数统计所有缩进 bullet 行

### 根因（已核实）

`check-gate.sh:148`：
```bash
P5_CMD_COUNT=$(grep -cE '^\s+- ' "$TASK_DIR/P2-design.md" 2>/dev/null || echo 0)
```

这个 grep 统计 P2-design.md 中所有"缩进 + `- `开头的行"（即所有 bullet item）。P2-design.md 含候选方案子项、权衡列表、files_to_read、env_constraints 等大量 bullet，全部被计入。review 报告的"27 个命令"就是这样来的。

实际上 `gate_commands` 是一个 YAML 块，`P5` 是字符串值（不是列表），如 architect.md:42 所示：
```yaml
gate_commands:
  P5: "pytest -q --tb=no"
  P5_e2e: "playwright test --reporter=line tests/e2e/"
  P6: "pytest -q --tb=no tests/acceptance/"
```

这个 WARNING 的目的是提醒主 Agent"如果 P2 声明了多个 P5 命令，确认全部执行"。但实际格式是单字符串（一条命令），不是列表。所以这个 WARNING 的触发条件本身就有问题 -- 它应该检查的是 `P5_e2e` 是否存在（ui_affected 时），而非统计 bullet 数。

### 方案：改为检查 gate_commands 块内 P5 相关键的数量

用 python3 regex 解析 P2-design.md 中的 `gate_commands:` 块，统计 P5 开头的键数。

**G5.1 fixture 兼容**：现有 G5.1 测试（check-gate.bats:366-380）的 fixture 用 `## gate_commands`（markdown 标题）+ ```yaml 代码块格式，且 P5 是列表格式（`P5:` + `- cmd`），不是 architect.md spec 的字符串格式（`P5: "cmd"`）。需更新 G5.1 fixture 为 spec 格式（`gate_commands:` YAML 键 + `P5: "..."` 字符串值），使正则能匹配。同时在 G5_CMD.5 中标注"更新了 G5.1 fixture 格式以匹配 spec"。

```bash
# 修复前（行 148）：
P5_CMD_COUNT=$(grep -cE '^\s+- ' "$TASK_DIR/P2-design.md" 2>/dev/null || echo 0)

# 修复后：用 python3 解析 gate_commands YAML 块，统计 P5 开头的键
P5_CMD_COUNT=$(GATE_FILE="$TASK_DIR/P2-design.md" python3 -c "
import re, os
with open(os.environ['GATE_FILE']) as f:
    content = f.read()
# 提取 gate_commands: YAML 块（匹配 'gate_commands:' 键，到下一个同级 key 或文件末尾）
# 兼容两种格式：裸 YAML 键（gate_commands:\n  P5: ...）和 markdown 代码块内（```yaml\ngate_commands:\n  P5: ...）
m = re.search(r'^gate_commands:\s*\n((?:  .+\n|\s*\n)+)', content, re.MULTILINE)
if not m:
    print(0)
    exit()
block = m.group(1)
# 统计 P5 开头的键（P5, P5_e2e 等）
count = len(re.findall(r'^  (P5\w*):', block, re.MULTILINE))
print(count)
" 2>/dev/null || echo 0)
P5_CMD_COUNT=$(echo "$P5_CMD_COUNT" | tail -1)
```

**为什么不用 pyyaml 直接 parse 整个文件**：P2-design.md 是 markdown，不是纯 YAML。gate_commands 块嵌在 ```yaml 代码块中。先 regex 提取块内容再解析更可靠。

**已知代价**：如果 P2-design.md 的 gate_commands 格式不规范（缩进错误、键名不含 P5），计数会为 0，WARNING 不触发。这是安全的退化 -- WARNING 不触发不等于放行，P5 gate 恒 exit 2（需主 Agent 自判）。

### 测试

| 用例 | 描述 | 期望 |
|------|------|------|
| G5_CMD.1 | P2 gate_commands 声明 P5 + P5_e2e（2 个 P5 键），P2 其他节含 20 个 bullet | WARNING 含"2"而非"22" |
| G5_CMD.2 | P2 gate_commands 只声明 P5（1 个键），P2 其他节含 10 个 bullet | 无 WARNING（1 不大于 1） |
| G5_CMD.3 | P2 无 gate_commands 块 | 无 WARNING，无崩溃 |
| G5_CMD.4 | P2 gate_commands 声明 P5 + P6（1 个 P5 键） | 无 WARNING（P6 不算 P5 命令） |
| G5_CMD.5 | **更新 G5.1 fixture** 为 spec 格式（`gate_commands:` 键 + `P5: "pytest"` + `P5_e2e: "playwright"`），回归验证 WARNING 仍触发 | WARNING 含"gate_commands.P5"或"子集"或"全量" |

---

## 问题三：T6 -- PROD_TOUCHED 步骤2 误匹配 AGATE_CARD 注入的卡片说明文本

### 根因（已核实）

`pre-commit-gate.sh:134`：
```bash
if echo "$DIFF_ADDED" | grep -q '\[PROD_TOUCHED\]'; then
    echo "GATE: 不合规的 PROD_TOUCHED 标记格式..." >&2
    exit 1
fi
```

步骤2 的设计意图是：如果 `[PROD_TOUCHED]` 出现在非行首位置（句中引用），说明有人"写了标记但格式不对"，应拦截并要求用行首格式。

问题：`agate-next-card.sh` 把 phase-card 全文注入 dispatch-context 文件。P5-verification.md:48 和 P8-release.md:88 的说明文本中含 `[PROD_TOUCHED]` 字面量（如"触发写 `[PROD_TOUCHED] {描述}`"）。dispatch-context 是新建文件，所有行都是新增行（`+`），`^+[^+]` 过滤不掉这些说明文本。

步骤1（行 130）有行首锚点 `^\s*-?\s*\[PROD_TOUCHED\]`，不匹配句中引用，正确放行。但步骤2（行 134）无锚点，`grep '\[PROD_TOUCHED\]'` 匹配任意位置，误拦。

### 设计张力

步骤2 不能简单加行首锚点 -- 那等于取消步骤2，真正"写了但格式不对"的声明（如 `备注：[PROD_TOUCHED] 生产环境`）就不会被拦。

修复方向应该是**排除 AGATE_CARD 注入块**，而非削弱步骤2 的检测能力。AGATE_CARD 块有明确的边界标记（`<!-- AGATE_CARD_START -->` / `<!-- AGATE_CARD_END -->`），可以在扫描前剥离。

### 方案：扫描前剥离 AGATE_CARD 块

AGATE_CARD 块的边界格式已核实：`agate-inject-card.sh:49` 的 `pattern = r'(<!-- AGATE_CARD_START -->\n)(.*?)(<!-- AGATE_CARD_END -->)'`。`check-p6-provenance.sh:119` 已有相同模式的剥离代码（`sed '/<!-- AGATE_CARD_START -->/,/<!-- AGATE_CARD_END -->/d'`）可复用。

```bash
# 修复前（行 129）：
DIFF_ADDED=$(git diff --cached -- "$TASK_REL" | grep '^+[^+]' | sed 's/^+//' || true)

# 修复后：剥离 AGATE_CARD 块后再扫描（标记格式与 check-p6-provenance.sh:119 一致）
DIFF_ADDED=$(git diff --cached -- "$TASK_REL" \
    | grep '^+[^+]' \
    | sed 's/^+//' \
    | sed '/<!-- AGATE_CARD_START -->/,/<!-- AGATE_CARD_END -->/d' \
    || true)
```

`sed '/<!-- AGATE_CARD_START -->/,/<!-- AGATE_CARD_END -->/d'` 删除从 `<!-- AGATE_CARD_START -->` 到 `<!-- AGATE_CARD_END -->` 的所有行（含边界行）。与 `check-p6-provenance.sh:119` 的已有剥离逻辑完全一致。剥离后，步骤1 和步骤2 都不会扫描到卡片注入的说明文本。

**已验证**：`check-p6-provenance.sh:119` 已用完全相同的 sed 模式剥离 AGATE_CARD 块来避免 PASS/FAIL 预判误报，此修复只是复用已验证的模式。

### 测试

| 用例 | 描述 | 期望 |
|------|------|------|
| IT_PT_T6.1 | P8 dispatch-context 含 AGATE_CARD 注入块（内有 `[PROD_TOUCHED]` 字面量），暂存 dispatch-context + .state.yaml | exit 0（不误拦，**核心修复**） |
| IT_PT_T6.2 | P5 dispatch-context 同上 | exit 0（回归） |
| IT_PT_T6.3 | 任务产出文件含句中 `[PROD_TOUCHED]`（非 AGATE_CARD 块内） | exit 1（步骤2 仍拦截不合规格式，**不回归**） |
| IT_PT_T6.4 | 任务产出文件含行首 `[PROD_TOUCHED]` | exit 1（步骤1 拦截，回归） |
| IT_PT_T6.5 | 任务产出文件含 `[PROD_NOT_TOUCHED]` | exit 0（负向声明放行，回归） |

---

## 实施顺序

1. T6 修复（pre-commit-gate.sh 剥离 AGATE_CARD 块）+ 测试 -- 最高优先（误拦阻断合法 commit）
2. T3/M2 修复（check-p6-provenance.sh 审计 3 降级 exit 1 -> WARNING）+ 更新 PV.9 测试 + 新增 PV_BDD_COUNT 测试
3. M5 修复（check-gate.sh P5 命令计数改为 YAML 块解析）+ 更新 G5.1 fixture + 新增 G5_CMD 测试
4. 跑全量 bats + consistency + shellcheck
5. self-gate：派发 protocol-alignment-review

---

## 不做的事

- **不改步骤2 为行首锚点**：步骤2 的"句中引用拦截"是有意设计，修复方向是排除 AGATE_CARD 块而非削弱检测
- **不修 T2/M1 的错误信息质量**（md5 重复/未引用证据不列文件名）：是改进点不是 bug，且改 error message 不影响 gate 行为，优先级低于三个 bug
- **不修 M6（已知限制跟踪）**：回测任务跟踪是 workflow 问题，不是 gate 职责
- **不修 T4（P3 测试覆盖）**：test-designer 职责，非 agate 问题
- **不修 T5（inject-card 路径）**：PR #46 目录改名 plan 处理中
