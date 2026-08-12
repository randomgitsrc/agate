# agate v0.6 实施评审（代码级，非计划文本）

> 评审对象：`main` 分支实际代码，commit `53ac2bb`（"fix: 实现评审 3 项修复"）
> 评审范围：`2ee6d53`→`53ac2bb` 共 6 个 commit，v0.6 全部 7 项从计划落地为真实代码
> 方法：**不停留在读 diff**——把仓库里真实的 `check-pruning.sh`、`check-gate.sh` 拿出来，用计划自己给的测试表构造真实文件、实际执行，记录真实 exit code；并且实际跑了仓库自带的一致性检查工具 `check-protocol-consistency.py`

---

## 总体结论

**7 项里 6 项验证通过（含真实执行，不是读代码推断），1 项发现新引入的、当前会让 CI 变红的真实 bug。** 另外验证到一处此前评审提出的"DESIGN_GAP 需要 implementer→architect 手动转抄"风险，maintainer 自己的"实现评审"已经发现并修复，但我复现了修复前的漏洞场景，并确认修复方式是纯文本约束（不是 hook 强制），残留风险仍在。

---

## 一、✅ 已实测验证：check-pruning.sh（P2 裁剪三例外口）

用计划自己的测试表，真实构造 5 个 `P1-requirements.md`，跑真实脚本：

```bash
$ bash agate/scripts/check-pruning.sh t1   # 裁剪 P2 无例外口
exit=1  ✓ (含错误："P2 不可裁剪（例外口：design_trivial / follows_existing_pattern / legacy_p2_pruned）")

$ bash agate/scripts/check-pruning.sh t2b  # design_trivial: true（+ 补全 P6/P8 声明后单独验证 P2 分支）
exit=0  ✓

$ bash agate/scripts/check-pruning.sh t3b  # follows_existing_pattern: [src/crud.py]
exit=0  ✓

$ bash agate/scripts/check-pruning.sh t4   # follows_existing_pattern: []（无参照文件）
exit=1  ✓ (P2 检查正确触发，[.+] 正则要求至少一个字符)

$ bash agate/scripts/check-pruning.sh t5b  # legacy_p2_pruned: true
exit=0  ✓
```

第一轮跑 t2/t3/t5 时全部 exit=1，一度以为有 bug——但打印错误详情发现是我的测试夹具没补全 P6/P8 的必填声明，触发了 P2 无关的其他检查。补全后单独隔离验证，P2 相关逻辑 5/5 全部符合预期。**结论：check-pruning.sh 的三例外口实现正确，`[.+]` 正则边界处理正确。**

---

## 二、✅ 已实测验证：check-gate.sh P2（多方案探索）

```bash
$ bash agate/scripts/check-gate.sh P2 g1   # 2 个候选方案
exit=2 "GATE P2: 需从 P2-design.md gate_commands 动态读取，主 Agent 自行判定"  ✓

$ bash agate/scripts/check-gate.sh P2 g2   # 只 1 个候选方案
exit=1 "GATE P2: P2-design.md 需至少 2 个候选方案 + 权衡 + 选择理由（v0.6 多方案探索）"  ✓

$ bash agate/scripts/check-gate.sh P2 g3   # 无 P2-design.md（design_trivial 裁剪场景）
exit=2（跳过候选检查，直接进入主 Agent 判定分支）  ✓
```

额外验证了一项计划测试表没覆盖的点：**实际模板产出的标题格式**（`task-files.md` 里 `### 候选方案 A：[简短标题]`）能否被 `check-gate.sh` 的正则 `^###?\s*候选方案` 正确识别——用真实模板格式构造文件实测，`exit=2`（正确通过候选数检查），**模板格式和 gate 正则完全对得上，不是"计划测试表通过、真实模板格式对不上"这种常见的两张皮问题。**

---

## 三、✅ 已实测验证：check-gate.sh P7（BLOCKER/DEVIATION-CRITICAL/DESIGN_GAP）

```bash
$ bash agate/scripts/check-gate.sh P7 p1   # 无任何标记
exit=0  ✓

$ bash agate/scripts/check-gate.sh P7 p2   # 含 [BLOCKER]
exit=1 "GATE P7: BLOCKER=1, DEVIATION-CRITICAL=0"  ✓

$ bash agate/scripts/check-gate.sh P7 p3   # 只含 [DEVIATION-CRITICAL]（我补的边界场景，计划测试表没覆盖）
exit=1 "GATE P7: BLOCKER=0, DEVIATION-CRITICAL=1"  ✓

$ bash agate/scripts/check-gate.sh P7 p4   # DESIGN_GAP 未配对 REVIEWED
exit=1 "GATE P7: 有 1 条 [DESIGN_GAP] 未配对 [DESIGN_GAP_REVIEWED]——主 Agent 需审查 implementer 的自主决策"  ✓

$ bash agate/scripts/check-gate.sh P7 p5   # DESIGN_GAP 已配对 REVIEWED
exit=0  ✓
```

5/5 全部符合预期，之前几轮评审反复揪出的"`$P2_FILE` 未定义""跳过分支不可达""链式 `&&/||` 改显式 if"这几项修复，落到真实代码里全部生效。

---

## 四、✅ 已用数学模拟验证：`retries[Pn] >= MAX_RETRY(Pn) - 1` 阈值

这是之前三轮评审追了很久才改对的公式（原来的 `>=3` 数学上永不可达）。这次不满足于读代码，写了个小模拟脚本，按真实重派判定逻辑（`retries < MAX_RETRY` 才重派，否则上溯）逐步推演两种 MAX_RETRY 取值：

```
=== MAX_RETRY=3（P1/P2/P4）===
  派发第2次尝试 (retries=1) -> 注入提示: False
  派发第3次尝试 (retries=2) -> 注入提示: True   ← 恰好只触发这一次
  第3次失败后 retries=3 >= MAX_RETRY -> 上溯，不再重派

=== MAX_RETRY=2（P3/P5/P6/P7/P8）===
  派发第2次尝试 (retries=1) -> 注入提示: True   ← 恰好只触发这一次
  第2次失败后 retries=2 >= MAX_RETRY -> 上溯，不再重派
```

**每个阶段恰好触发一次，触发时机正好是"最后一次允许的重派"——公式验证正确。** 而且确认 `dispatch-protocol.md:660` 现在的注释直接写了"不能用 >=3——详情见 state-machine.md 重试上限表"，把之前踩过的坑记录在代码注释里，是个好习惯。全文搜索确认 `dispatch-protocol.md` 和 `investigate.md` 里不再有任何一处残留的 `>=3`。

---

## 五、⚠️ 已复现验证：DESIGN_GAP 转抄依赖——maintainer 自己发现但只是打了个"软补丁"

maintainer 的"实现评审 3 项修复"（`53ac2bb`）里第 2 项修复的问题，我单独复现验证了一遍。

**漏洞原貌**：`check-gate.sh P7` 只扫描 `$TASK_DIR/P7-consistency.md`，但 `implementer.md` 要求 implementer 把 `[DESIGN_GAP: xxx]` 写进**自己的产出文件**（`P4-implementation.md`），不是 `P7-consistency.md`。如果 architect 写 P7 一致性检查时没有手动把这条标记转抄过去，gate 会看不到它。我实际构造了这个场景：

```bash
# P4-implementation.md 里诚实标了 DESIGN_GAP
$ cat silent/P4-implementation.md
实现完成。
[DESIGN_GAP: P2 未指定错误处理策略，实现中采用了静默降级 + 日志记录]

# P7-consistency.md 没有转抄这条标记（旧版本行为）
$ cat silent/P7-consistency.md
一致性检查完成，无 BLOCKER。

$ bash agate/scripts/check-gate.sh P7 silent
exit=0   ← 静默放过，implementer 诚实报告的 DESIGN_GAP 完全没有被 gate 看到
```

**确认漏洞真实存在。** maintainer 的修复是在 `architect.md` 里加了一句话：

> **对每条 [DESIGN_GAP: xxx]（在 P4-implementation.md 中），必须在 P7-consistency.md 中写入原始标记行 + 你的 REVIEWED 标记行**。check-gate.sh 只扫描 P7-consistency.md——不把原始 GAP 写入 P7-consistency.md 会导致 hook 静默放过

**这个修复本身是对的，但要注意它的强度**：这是一条**纯文本指令**，靠 architect 角色记得执行，hook 本身没有任何机制强制或验证这个转抄动作真的发生了。换句话说，**这个刚被发现的漏洞，修复方式仍然是漏洞本身那一类"自写文件 gate"——architect 忘记转抄（或者偷懒不转抄），hook 依然会静默放过，和修复前一模一样。**

这正好是协议自己在 `dispatch-protocol.md`"Gate 分类"表里区分的 "外部产出 gate（不可伪造）" vs "自写文件 gate（可伪造）"——这次修复用的是后者，而这个具体场景其实有条件做成前者。

**建议**：`check-gate.sh P7` 除了扫描 `P7-consistency.md`，同时直接扫描 `$TASK_DIR/P4-implementation.md`（或 `P4-*.md`）里的 `[DESIGN_GAP:` 数量，和 `P7-consistency.md` 里的 `[DESIGN_GAP:` 数量做交叉核对——如果 P4 里的数量 > P7 里转抄的数量，直接报错"P4 声明了 N 条 DESIGN_GAP，P7 只转抄了 M 条，architect 遗漏转抄"。这样就不再依赖 architect"记得执行指令"，变成机器可判定的核对，消灭这个刚打了软补丁的漏洞的复发可能。这个改动量很小（多加一次 grep + 一次数值比较），但能把这条 gate 从"自写文件、可被遗忘"升级为"部分外部产出核对、遗忘会被抓"。

---

## 六、🔴 新发现的真实 bug：v0.6 model_tier 提交破坏了 YAML 模板，会让 CI 变红

这是本轮评审最重要的发现，**不是读代码看出来的，是跑仓库自带工具跑出来的**。

### 复现过程

`b028315`（"模型选择"提交）给 `task-files.md` 里的 `executor_env` 示例块加了 `model_tier` 字段，但连带整个块的缩进都被改坏了——`executor_env:` 前面多了一个空格，子字段从 2 空格缩进变成 3 空格缩进：

```yaml
known_risks:
  - "..."

 executor_env:              ← 多了一个前导空格
   platform: "opencode"     ← 3 空格缩进（同级的 known_risks/env_constraints 都是 2 空格）
   ...
```

用真实 YAML 解析器（`yaml.safe_load`）单独验证这一个块，去掉块首的说明性注释行（`## P0-brief.md`，本来就不是合法 YAML，是文档标题）之后，纯粹测这个缩进问题：

```
YAML 解析失败: while parsing a block mapping
  in "<unicode string>", line 1, column 1:
    task: "一句话描述任务...
    ^
expected <block end>, but found '<block mapping start>'
  in "<unicode string>", line 8, column 2:
     executor_env:
     ^
```

**确认这不是我的测试方法问题，是真实的缩进错误，会导致这个块无法被标准 YAML 解析器解析。**

### 用仓库自己的工具二次确认

这个仓库自带一个一致性检查脚本 `check-protocol-consistency.py`，第一项检查就是"所有 ` ```yaml ` 代码块可被 `yaml.safe_load` 解析"。实际跑了一下：

```bash
$ python3 agate/scripts/check-protocol-consistency.py --root .
  ❌ FAIL  CHECK 1  YAML 代码块可解析
  ...
  ERROR (1):
    ❌ YAML 代码块无法解析: while parsing a block mapping [agate/assets/templates/task-files.md:77]
```

**这个工具精确定位到了同一个文件、同一个位置。** 为了确认这是这次提交新引入的（不是历史遗留），我 checkout 了 `model_tier` 提交之前的版本单独跑了一遍：

```bash
# b028315 之前（cf6cd80）
CHECK 1  YAML 代码块可解析 → ⚠️ WARN（此前就有的其他文件的宽松警告，非本文件）

# b028315 之后（当前 main）
CHECK 1  YAML 代码块可解析 → ❌ FAIL（本文件，新增的硬错误）
```

**确认这是 `b028315` 这次提交新引入的回归，此前不存在。**

### 这个 bug 的实际影响

1. **CI 会红**：仓库有 `.github/workflows/protocol-consistency.yml`，每次 push/PR 到 main 都会跑这个检查脚本，"默认仅 ERROR 判失败"——这次的问题是 ERROR 级别，意味着**当前 main 分支的 CI 状态应该是失败的**。
2. **本地 pre-commit 没拦住**：查了 `pre-commit-gate.sh`，它不调用 `check-protocol-consistency.py`，这个一致性检查只在 CI（push 之后）跑，commit 时不会拦。这解释了为什么这个错误能落到 main 分支——本地提交这一关本来就没有这道检查。
3. **模板会把错误格式传染给未来所有任务**：`task-files.md` 是"如何写 P0-brief.md"的参考模板，如果 Agent 严格照抄这个模板的视觉格式（含缩进）去生成真实项目里的 `P0-brief.md`，会把这个缩进错误也复制过去。虽然当前 `check-pruning.sh` 等脚本用的是非锚定正则（`re.search`，不要求特定缩进），不会被这个具体缩进错误直接影响判定结果，但这是运气好，不是设计保证——万一以后有工具需要真的解析这段 YAML（协议里已经有好几个脚本在用 `yaml.safe_load`），这个错误格式被复制得越多，后续要修的地方就越多。

### 建议修复（已验证）

```diff
-executor_env:
-  platform: "opencode"          # ...
-  has_task_tool: true           # ...
-  has_local_runtime: true       # ...
-  network: "full"               # ...
-  model_tier: "standard"        # ...
+executor_env:
+  platform: "opencode"          # ...
+  has_task_tool: true           # ...
+  has_local_runtime: true       # ...
+  network: "full"               # ...
+  model_tier: "standard"        # ...
```

（把 `executor_env:` 和其 5 个子字段的缩进都退回到 2 空格，和 `known_risks:`/`env_constraints:` 保持同一缩进层级。）我在本地把这处缩进改回 2 空格后重新跑了一遍 `check-protocol-consistency.py`，`CHECK 1` 恢复为不报这条 ERROR，确认这个改法能修好。

---

## 七、修复优先级汇总

| # | 问题 | 严重度 | 验证方式 | 状态 |
|---|------|--------|---------|------|
| 1 | task-files.md `executor_env` 块缩进错误，YAML 无法解析 | 🔴 Critical | 实际跑 `yaml.safe_load` + 仓库自带一致性检查工具，双重确认，会导致 CI 变红 | **待修复** |
| 2 | DESIGN_GAP 转抄依赖纯文本指令，无 hook 强制核对 | 🟠 Important | 实际构造漏洞场景复现，确认 gate 仍会静默放过 | maintainer 已打软补丁，建议进一步做机器核对 |
| 3 | check-pruning.sh P2 三例外口 | ✅ 已验证正确 | 5 个真实场景实测，5/5 通过 | 无需改动 |
| 4 | check-gate.sh P2 多方案检查 | ✅ 已验证正确 | 3 个测试场景 + 真实模板格式兼容性，全部通过 | 无需改动 |
| 5 | check-gate.sh P7（BLOCKER/DEVCRIT/DESIGN_GAP） | ✅ 已验证正确 | 5 个场景（含 1 个自补的边界场景）全部通过 | 无需改动 |
| 6 | retries 阈值公式 | ✅ 已验证正确 | 数学模拟两种 MAX_RETRY 取值，各恰好触发一次 | 无需改动 |

---

## 八、总评

这轮实施把此前 6 轮计划评审揪出的问题基本都落实了——check-pruning.sh、check-gate.sh 的核心逻辑经过真实执行验证，行为和计划文档描述完全一致，之前反复强调的"计划里写对了，代码里未必写对"的担忧，这次实测下来没有发生。maintainer 自己的"实现评审"也抓到了一个真实的、有实际后果的问题（DESIGN_GAP 转抄依赖），说明这套"实施后自己也做一遍审查"的习惯延续了下来。

**这次唯一的新问题（YAML 缩进）性质不一样**——不是逻辑设计错误，是纯粹的编辑失误（多打了一个空格），但后果比前几轮任何一个"计划文本不一致"的问题都更直接：**它会让仓库自己的 CI 变红**。这也间接说明了一件事：`check-protocol-consistency.py` 这道检查目前只在 CI（push 之后）触发，不在本地 pre-commit 触发，导致这类问题能真的落到 main 分支上，而不是在提交前被拦下——这本身是一个流程缺口，值得作为独立改进项考虑（把 `check-protocol-consistency.py` 也接入本地 pre-commit，或者至少接入一个"push 前自查"的便捷脚本）。
