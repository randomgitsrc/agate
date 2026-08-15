---
review_date: 2026-08-08
reviewer: protocol-alignment-review
change_summary: 内联 python 抽离重构——14 个 .sh 里 46 处 `python3 -c '...'` 抽成 14 个独立 .py 工具，行为等价，不改任何协议规则/gate 语义/状态机
files_changed: [14 个新 .py, 14 个 .sh, check-protocol-consistency.py, 12 个新 .bats + 2 个改 .bats, tests/README.md, 6 个 docs/plans/]
---

# 协议-脚本对齐审查

> 留痕文件：docs/reviews/agate-alignment-20260808-01.progress.md

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | **MISALIGNED**（A3b 反向传播：AGENTS.md 依赖节 + LIMITATIONS.md 未更新） |
| A4 | 测试覆盖 | ALIGNED（bats 全量 597/0 实跑通过） |
| A5 | 下游影响 + 文档传播 | NEEDS_HUMAN_REVIEW（CHANGELOG 未记 + scripts/README.md 工具清单缺失） |
| A6 | 锚点表覆盖 | ALIGNED |
| A7 | 设计原则一致性 | ALIGNED |

## 逐项审查

### A1: 文档→脚本对齐

本次是纯行为等价重构，不改任何协议规则（状态机/重试表/裁剪表/gate 判定语义均未动）。抽查 8 个「内联→薄壳 .py」替换，逐行比对原内联逻辑与新工具逻辑，均完全等价：

| 原内联（check-tdd-red.sh 原 read_gate_commands / judge_result） | 新工具 |
|---|---|
| `GATE_FILE=$p2 python3 -c 'import re...gate_commands:[ \t]*\n...'` | `agate-read-gate-commands.py`（逐行一致，含 `chr(10)` 补结尾、同 `re.search` 正则、同 `strip('"').strip(chr(39))`） |
| `d.get("exit_code",1)` / `d.get("failed",0)` / `len(d.get("syntax_errors",[]))` | `agate-json-get.py get/len`（缺失默认一致） |
| `d["project_module"]=os.environ[...]` 打印 json | `agate-json-get.py set`（等价） |
| `sum(1 for e in import_errors if e.get("module").startswith(pm))` | `agate-json-get.py count_prefix`（`e.get(subkey,"")` 与内联 `e.get("module","")` 等价） |
| agate-capture-env-baseline 原 P5 数组输出 | `agate-read-p5-commands.py` 输出 `{"commands":[...]}` 对象，bash 侧同步改 `len commands`/`index commands`，且无 gate 块 `sys.exit(0)` 空输出、仅 formatter 键时输出非空——均与原 ORIG 行为等价 |
| check-state-transition 原 retries 判定（`max_map.get(phase,3)`，`len(attempts)>=phase_max` 打印 break） | `agate-state-get.py retries_over`（逐行等价；原死变量 `max_retry=int(MAX_RETRY)` 未使用，移除无影响） |
| agate-retreat-to 原 check_retreat（`range(cur-1,tgt-1,-1)`、`count+1>limit`）与 write_retreat | `agate-retreat-state.py check_retreat/write_retreat`（逐行等价，含 `setdefault`、`allow_unicode/sort_keys=False`） |
| check-state-yaml 原字段校验（YAMLError+exit0、空文件+exit0、task_id/phase/retries 校验） | `agate-state-yaml-check.py`（逐行等价） |
| check-p6-evidence 原 variance/ahash（PIL 缺失：variance 打 stdout、ahash 打 stderr+exit1） | `agate-image-check.py variance/ahash`（PIL 缺失走比分叉与内联一致，`2>/dev/null || echo` 兜底下行为等价） |

**结论**：ALIGNED。行为等价成立。

### A2: 脚本→文档对齐

角色文件（architect.md:50/110、consistency-reviewer.md:40、verifier.md:93/167/168）、模板（task-files.md:18/64/215/222、dispatch-prompt.md:154）均**按脚本名引用脚本行为/退出语义**，无一处描述「内联 python」实现细节。重构后脚本行为未变，这些引用仍准确，无需改动。

**结论**：ALIGNED。

### A3: 一致性连锁 + 反向传播

**A3a（连锁）**：新增 .py 依赖 pyyaml 的工具（agate-state-get/state-yaml-check/retreat-state/vision-blocker）在缺 pyyaml 时显式 stderr 提示 + exit 1，由 bash `2>/dev/null || echo` 兜底，行为不回归。14 个 .sh 中除 agate-inject-card.sh、pre-commit-gate.sh 用 `$AGATE_ROOT`（均已定义：line 10 / line 26）外，其余 12 个均各自定义 `SCRIPT_DIR` 且与被引用 .py 同目录，解析正确。ALIGNED。

**A3b（反向传播）**：应被影响但 diff 未列出的文件，逐项验证：

- **AGENTS.md（仓库根）第 22 行**：仍写「8 个 sh 脚本内联 python3：check-changelog.sh、check-p6-evidence.sh、check-p6-provenance.sh、check-pruning.sh、check-retrospective.sh、check-state-transition.sh、check-state-yaml.sh、gate-result.sh」。**此说法已失效**——重构后 46 处内联清零，这 8 个脚本不再内联 python3（且该枚举本身就不完整，实际 14 个 .sh 含内联）。**需更新**为「内联 python 已抽离为独立 .py 工具」的表述，并登记新 .py 清单。
- **agate/LIMITATIONS.md 第 92 行**：仍写「此外 8 个 gate 脚本内联 python3 调用（见 AGENTS.md 依赖节完整列表），缺 python3 时这些脚本的 YAML 解析逻辑不可用」。「内联 python3 调用」措辞已失效；且「见 AGENTS.md 完整列表」现在指向失效的 AGENTS.md 第 22 行。**需更新**（python3 仍为必需、pyyaml 仍为 state/vision 类 .py 所必需，但措辞与引用应改）。
- **agate/scripts/README.md**：第 3 行已写「`check-*.sh / .py` 是各检查脚本」，但脚本清单表未登记 14 个新 `agate-*.py` 工具。属完整性缺口（非错误声明），建议补充。
- **SELF-GATE.md 第 16 行**：触发模式已含 `agate/scripts/*.py`，新 .py 文件正确触发 self-gate。无需更新。
- **角色文件 / task-files.md / verifier.md / vision-analyst.md**：见 A2，按脚本名引用行为，行为未变，无需更新。
- **formatters/README.md:113**「内置 formatter 均使用内联 python3 解析」：formatter 用的是 `python3 <<'PYEOF'`（heredoc），**不在本次 `python3 -c` 抽离范围内**，该句仍准确，无需更新。

**结论**：MISALIGNED（A3b 反向传播缺口：AGENTS.md 第 22 行 + LIMITATIONS.md 第 92 行需更新）。
**建议**：派 implementer 更新 AGENTS.md 依赖节与 LIMITATIONS.md 第 92 行，改为描述「内联 python 已抽离为独立 .py 工具」并登记新 .py；scripts/README.md 补工具清单。

### A4: 测试覆盖

- 新增 12 个 .bats 覆盖各新工具边界（抽查 agate-json-get.bats 覆盖 get/len/index/set/count_prefix/list/escape 全部子命令含默认值/缺失分支）。
- dispatch-context-warning.bats 补 `cp` 新 .py 依赖（模拟 AGATE_ROOT 无 agate-next-card 场景），正确跟随脚本对 .py 的新依赖。
- tests/README.md 新增的 13 行工具用例数与 count-tests.sh 实跑输出逐一吻合（json-get=8、read-p5=4、state-get=6、retreat-state=3、md-field-get=6、state-yaml-check=3、changelog-unreleased=2、card-inject=2、vision-blocker=2、evidence-consistency=2、image-check=4、gate-missing-cmds=2、gate-p5-count=2），check-tdd-red.bats 32→38 与实跑一致。

**实跑输出**（本审查实际执行）：
```
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
→ ok=597 not_ok=0，bats exit code=0
count-tests.sh → 总计 591（sanity 独立不计入）
python3 agate/scripts/check-protocol-consistency.py → 全部 8 类检查通过（含 CHECK 9）
shellcheck -S warning agate/scripts/*.sh → exit 0
```

**结论**：ALIGNED（有实跑输出佐证）。

### A5: 下游影响 + 文档传播

- **gate 行为**：纯重构、行为等价，对已有项目 gate 行为零改变，非 BREAKING。
- **部署**：脚本经 `~/.agate` 整目录软链部署，.py 与 .sh 同目录必然共存；check-tdd-red.sh 已加「依赖同目录 agate-read-gate-commands.py，项目复制脚本时须一并复制」注释。若项目选择性复制单个 .sh 而不复制 .py，会静默降级——已有注释提醒，但建议在文档中统一标注。
- **CHANGELOG**：仓库根 CHANGELOG.md 顶部为 0.33.0（2026-08-07），本次在 feature 分支未发版，无对应条目。按 0.32.0「内部重构」先例，此重构值得一条「内部重构」记录，但**何时落（发版时）是 maintainer 决策**。
- **scripts/README.md**：新 .py 工具未入清单（见 A3b）。

**结论**：NEEDS_HUMAN_REVIEW。
- 需人工确认：CHANGELOG 是否在本次分支落一条「内部重构」条目（与 0.32.0 先例一致），还是等发版时统一补。
- 建议（非阻断）：scripts/README.md 补 14 个 .py 工具清单；文档统一标注「复制脚本须连带复制 .py」。

### A6: 锚点表覆盖

逐条核对 CHECK 9 锚点表（check-protocol-consistency.py:448-632）：
- 本次将 check-state-yaml.sh 锚点关键词从 `["task_id"]` 改为 `["state.yaml"]`，并新增 `agate-state-yaml-check.py` 锚点（keywords `["task_id"]`）——合理重指向，把校验逻辑锚点从 .sh 移到实际承载逻辑的 .py。
- 其余锚点（check-pruning「risk_level」、check-state-transition「MAX_RETRY」、check-p6-evidence「ui_affected/AHASH_LIST/VARIANCE_WARNING」、check-p6-provenance「EVIDENCE_DIR/EXIT_CODE」、check-retrospective「retries」、check-changelog「CHANGELOG」、check-tdd-red「formatter/pytest」、check-gate 各锚点）经逐 .sh 核对，重构后关键词仍驻留对应 .sh，锚点未断裂。
- 锚点表支持 .py 脚本（ci-gate-backstop.py 已作先例，line 610），新增 .py 锚点机制无碍。

**结论**：ALIGNED。

### A7: 设计原则一致性

agate/adr.md 现含 ADR-001~006。ADR-003（最小约定，不绑定技术栈）要求 agate 自身运行时依赖可控——本次重构保留 python3/pyyaml 依赖、未新增依赖、未绑定项目技术栈，不违反。ADR-002（可判定性）——抽离为独立可测试 .py 反而提升可判定性。无任何 ADR 规定「脚本必须以内联方式构成」，故不违反。

**可选建议**：本次确立了「.sh 薄壳 + 独立 .py 工具」的脚本构成模式，值得补一条 ADR（如 ADR-007「脚本构成：检查逻辑抽离为独立 .py 工具」）记录该架构决策，供后续维护者遵循。非强制。

**结论**：ALIGNED。

## 闭环规则

| 结论 | 动作 |
|------|------|
| MISALIGNED（A3b） | **必须修复**：更新 AGENTS.md 第 22 行 + LIMITATIONS.md 第 92 行后重审 |
| NEEDS_HUMAN_REVIEW（A5） | 需人工确认 CHANGELOG 落条目时机；scripts/README.md 补工具清单（建议非阻断） |

## 需主 Agent 修复的事项清单

1. **（MISALIGNED，必须）** AGENTS.md（仓库根）第 22 行「8 个 sh 脚本内联 python3：…」已失效——46 处内联已清零，改为描述「内联 python 已抽离为独立 .py 工具」并登记 14 个新 .py。
2. **（MISALIGNED，必须）** agate/LIMITATIONS.md 第 92 行「8 个 gate 脚本内联 python3 调用（见 AGENTS.md 依赖节完整列表）」措辞失效且引用指向失效列表——同步改措辞与引用。
3. **（NEEDS_HUMAN_REVIEW）** 确认 CHANGELOG.md 是否在本次分支落一条「内部重构」条目（对齐 0.32.0 先例），或留待发版。
4. **（建议，非阻断）** agate/scripts/README.md 脚本清单补 14 个 `agate-*.py` 工具；文档统一标注「复制脚本须连带复制 .py」。

## 人工验收清单

- [x] 审查报告含 A1-A7 七项，每项有结论
- [x] MISALIGNED 项有差异描述 + 建议方向
- [x] script 内无遗留内联 python3（`grep -rn "python3 -c" agate/scripts/*.sh` 为空）
- [x] 审查报告落盘到 docs/reviews/agate-alignment-review-2026-08-08-py-extraction.md
---

## 修复记录（迭代 2）

> 主 Agent 已修复 MISALIGNED 项并处理 NEEDS_HUMAN_REVIEW 项，待重审确认。

### 已修复（MISALIGNED）
- **AGENTS.md（根）第 22 行**：已改为「检查逻辑抽离为独立 `.py` 工具（`agate/scripts/agate-*.py`）」并登记 pyyaml/Pillow 依赖清单。
- **agate/LIMITATIONS.md 第 92 行**：已改为「状态/vision 类检查逻辑已抽离为独立 `.py` 工具」，措辞与引用同步更新。

### 已处理（NEEDS_HUMAN_REVIEW）
- **CHANGELOG.md**：已加 `## [Unreleased]` 内部重构条目「内联 python 抽离为独立 .py 工具」，对齐 0.32.0「内部重构」先例。`[HUMAN_CONFIRMED: 2026-08-08 确认：feature 分支记录内部重构，发版时并入版本条目]`
- **scripts/README.md**：已补「检查逻辑工具」表，登记 14 个 `agate-*.py` 工具 + 依赖 + 「复制脚本须连带复制 .py」提醒。`[HUMAN_CONFIRMED: 2026-08-08 确认：工具清单随重构落地，非阻断]`

---

## 迭代 2 复审结论

> 角色：protocol-alignment-review（迭代 2 复审）。只复审上轮 4 个需修复项（MISALIGNED A3b ×2 + NEEDS_HUMAN_REVIEW A5 ×2），不重新全量审查。

### 复审项 1：AGENTS.md（根）第 22 行依赖节

**原文（AGENTS.md:22）**：
> 检查逻辑已抽离为独立 `.py` 工具（`agate/scripts/agate-*.py`），由 `.sh` 薄壳调用。其中 state/vision 类工具（agate-state-get / agate-retreat-state / agate-state-yaml-check / agate-vision-blocker）依赖 pyyaml；agate-image-check 依赖 Pillow（可选…）

**验证**：
- <del>「8 个 sh 脚本内联 python3」失效措辞</del> 已清除，改为「抽离为独立 `.py` 工具」。
- 依赖登记准确：pyyaml 依赖的 4 个工具（state-get / retreat-state / state-yaml-check / vision-blocker）与 AGENTS.md 隐藏上下文一致；Pillow（可选）依赖 agate-image-check。逐一比对 scripts/ 目录实际 .py（见下），映射正确。
- 无失效引用（不再指向旧枚举）。

**结论**：**ALIGNED**（原 MISALIGNED 已修复）。

### 复审项 2：agate/LIMITATIONS.md 第 92 行

**原文（LIMITATIONS.md:92）**：
> 此外状态/vision 类检查逻辑已抽离为独立 `.py` 工具（`agate/scripts/agate-*.py`，见 AGENTS.md 依赖节），缺 python3 时这些工具的 YAML/状态解析逻辑不可用

**验证**：
- <del>「8 个 gate 脚本内联 python3 调用」</del> 措辞已清除。
- 引用「见 AGENTS.md 依赖节」现在指向有效的 AGENTS.md:22（迭代 1 已修的依赖节），引用不再失效。
- 依赖描述仍准确：python3 仍为必需、pyyaml 为 state/vision 类 .py 所必需、Pillow（LIMITATIONS.md:93）仍标注可选。

**结论**：**ALIGNED**（原 MISALIGNED 已修复）。

### 复审项 3：CHANGELOG.md「内部重构」条目

**原文（CHANGELOG.md:9-12）**：
> `## [Unreleased]` → `### 内部重构` → 「内联 python 抽离为独立 `.py` 工具：把 14 个 `.sh` 脚本里 46 处 `python3 -c '...'` 内联段…抽离为 14 个独立可测试的 `agate/scripts/agate-*.py` 工具，行为完全等价。…非 BREAKING」

**验证**：
- Unreleased 条目存在，格式对齐 0.32.0「内部重构」先例（CHANGELOG.md:29-30）。
- 内容准确（14 个 .sh / 46 处 / 14 个 .py / 非 BREAKING），与上轮审查结论一致。
- 已附 `[HUMAN_CONFIRMED: 2026-08-08]`。

**结论**：**ALIGNED**（原 NEEDS_HUMAN_REVIEW 已处理）。

### 复审项 4：agate/scripts/README.md 工具清单表

**原文（scripts/README.md:59-78）**：`### 检查逻辑工具` 表 + 复制提醒（第 61 行）。

**验证**：
- 表内 14 个工具与 `ls agate/scripts/agate-*.py` 实列 14 个文件**逐一精确匹配**（json-get / md-field-get / state-get / retreat-state / read-gate-commands / read-p5-commands / state-yaml-check / changelog-unreleased / card-inject / vision-blocker / evidence-consistency / image-check / gate-missing-cmds / gate-p5-count）。
- 依赖列准确：pyyaml⟶state-get/retreat-state/state-yaml-check/vision-blocker；Pillow（可选）⟶image-check；其余「无」。
- 复制提醒存在（README.md:61「复制单个 `.sh` 到项目时须连带复制其依赖的 `.py`（同目录）」）。
- 已附 `[HUMAN_CONFIRMED: 2026-08-08]`。

**结论**：**ALIGNED**（原 NEEDS_HUMAN_REVIEW / 建议项已落地）。

### 验证命令实跑

```
python3 agate/scripts/check-protocol-consistency.py → 8 类全部 PASS，EXIT=0（0 ERROR，文档改动未破坏一致性）
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/ → ok=597 not_ok=0，EXIT=0
（注：agate-archive-stale-outputs.bats 位于 unit/，本次全量通过，ARCH.4 未触发 flake）
```

### 最终结论汇总

| # | 审查项 | 迭代 1 | 迭代 2 |
|---|--------|--------|--------|
| A1 | 文档→脚本对齐 | ALIGNED | ALIGNED |
| A2 | 脚本→文档对齐 | ALIGNED | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | MISALIGNED | **ALIGNED** |
| A4 | 测试覆盖 | ALIGNED | ALIGNED |
| A5 | 下游影响 + 文档传播 | NEEDS_HUMAN_REVIEW | **ALIGNED**（附 HUMAN_CONFIRMED） |
| A6 | 锚点表覆盖 | ALIGNED | ALIGNED |
| A7 | 设计原则一致性 | ALIGNED | ALIGNED |

**本轮终止**：4 个修复项全部通过，A1-A7 全部 ALIGNED。无遗留 MISALIGNED，无未确认 NEEDS_HUMAN_REVIEW。达到「全 ALIGNED 终止」，可 commit。
