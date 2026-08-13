---
phase: P7
task_id: TAG0004-env-adaptation
type: consistency
parent: P2-design.md
trace_id: TAG0004-P7-20260813
status: approved
created: 2026-08-13
agent: consistency-reviewer
# ── v2.0 机器计数 ──
blocker_count: 0
deviation_count: 0
deviation_critical_count: 0
design_gap_count: 1
design_gap_reviewed_count: 1
---

# P7 一致性审查报告 — TAG0004（agate 脚本健壮性 + 环境适配）

- **审查对象**：P1-requirements.md（37 BDD）/ P2-design.md（28 候选）/ P4 五份实现（group1/group2/group3a/group3b/m6-shell）/ P5-test-results/ / P6-acceptance.md（37/37 PASS）
- **审查结论**：跨文件一致，BLOCKER=0，CRITICAL=0，DESIGN_GAP 1 条已配对 REVIEWED，SCOPE+ 闭环，SCOPE_GAP 闭环。
- `[PROD_NOT_TOUCHED]` 本阶段仅读 worktree 内产出文件并交叉比对，未接触任何生产环境 / 主 checkout / ~/.agate。

## 1. DESIGN_GAP 配对（P4 §group2 → P7 转抄 + REVIEWED）

### 1.1 转抄 P4-implementation-group2.md §[DESIGN_GAP]

[DESIGN_GAP: P2 候选 11A 未明确"formatter 检测到 NameError 但无 project_module 前缀信息"（裸符号 / 前缀不匹配）时的归类——字面读法是"未匹配 → 仍 A 类"，但 bdd-35 测试契约的 fixture（ERROR tests/test_x.py - NameError: name 'compute' is not defined + project_module=myapp）输出中不存在 myapp 字符串，任何基于 module 前缀的严格门禁都无法命中。实现选择：前缀匹配仅影响判定消息措辞，只要 formatter 检测到 NameError 即判 B 类（"测试引用未实现符号正是 TDD 红灯正常状态"，P0-brief known_risk），非 NameError（TypeError 等）由 pytest.sh 精确解析范围 + errors>0 分支兜底仍判 A 类（BDD-37 回归绿）]

### 1.2 审查结论

[DESIGN_GAP_REVIEWED: 已确认] 该决策合理，理由三点：

- **设计契约不可满足**：P2 §1.11 候选 11A 原读法"项目模块内 NameError → B 类"依赖 `count_prefix` 前缀匹配，但 P1 BDD-35 的 Given fixture 输出中不存在 `myapp` 字符串——任何 module 前缀门禁都无法命中，实现被迫做归类决策，属 P2 设计未覆盖的空档（P2 §1.11 风险行亦未预警此形态）。
- **决策符合任务语义**：TPV0090-M4 的根因是"测试引用未实现符号抛 NameError 被 errors>0 误判为 A 类拦截 TDD 正常红灯"（P0-brief known_risk 第 6 条）。B 类定义本质是"引用未实现符号"，与是否携带前缀信息无关；前缀信息只是措辞增强，不改变归类语义。
- **防过宽由非 NameError 路径兜底**：pytest.sh 的 `name_errors` 解析只匹配精确形态 `NameError: name 'X' is not defined`（P4 §group2），TypeError 等真实测试 bug 不匹配 → name_errors 为空 → 落入 `errors > 0` 分支判 A 类。P6 BDD-37 PASS（TypeError → A 类 exit 1）证明边界守住了。

**证据锚点**：P4 §group2 实现要点、P1§BDD-35、P2§1.11、P6 验收 BDD-35/36/37 全部 PASS。

## 2. SCOPE+ 闭环

### 2.1 P4 组 1 的 [SCOPE+]（P4-implementation-group1.md §M9）

- **声明**：pre-commit-gate.sh L290（2n.1 分支）与 L104 为 P1 §6 M9 审计清单（L102/133/228）之外的同缺陷模式（`^${TASK_REL}` 拼入 grep -E），为防同一文件留下同类静默绕过点，一并按同方案改造。
- **纳入基线确认**：P1-requirements.md §6 M9 审计范围仅列 `pre-commit-gate.sh:102/133/228`，未列 L104/L290——本增补超出 P1 初始审计行号清单。查证 P1-requirements.md 当前无行首 `[SCOPE_RESOLVED]` 标记；`check-scope-resolved.sh` 对 SCOPE+ 的触发仅针对**行首** `[SCOPE+]` 标记，而本增补在 P4-implementation-group1.md 中以句中反引号形态出现，不触发自动化阻断。
- **闭环判定**：本增补的实现与验证证据客观存在——改动后 `pre-commit-gate.sh` 全文 5 处 `awk -v p="${TASK_REL}/" 'index($0, p) == 1'`（L111/114/144/239/301），覆盖 L102/L104/L133/L228/L290；P6 BDD-17 PASS（目录含 `[` 元字符时 PROD_TOUCHED 检测不静默绕过）。增补已实际纳入修复范围且被验收。

[SCOPE_RESOLVED: pre-commit-gate.sh L104/L290 两处 `^${TASK_REL}` grep -E 同缺陷模式已按 M9 方案（awk index 字面前缀）一并改造，P6 BDD-17 PASS 验收，增补闭环——P1 基线行号清单未更新为审计遗留，不构成阻塞（自动化 gate 不触发且验收证据充分）]

### 2.2 P4 组 1 的 [SCOPE_GAP]（bdd-14 归属）

- **声明**：P4-implementation-group1.md §范围外说明——check-gate.sh P1/P2 的 frontmatter 提取 CRLF 容错（bdd-14）不在组 1 BDD 清单，由负责 M6 的组补齐。
- **闭环确认**：P4-implementation-m6-shell.md 实现——check-gate.sh 全部 8 处 `sed -n '/^---$/,/^---$/p'` 改为 `sed -n 's/\r$//; /^---$/,/^---$/p'`（L51/56/82/102/162/167/231/236）。P6 BDD-14 PASS（CRLF 行尾 P1-review.md 经 check-gate.sh P1 提取 status 不失效）。该 SCOPE_GAP 已闭环，不阻塞。

## 3. 跨文件一致性检查（逐条引用源文件节名）

### 3.1 P1 BDD 数量 vs P6 验收数量

- P1§3 BDD-1..37 = **37 条**；P6 §BDD 逐条 PASS **37 条**、FAIL 0（P6 frontmatter `pass: 37 / fail: 0`）。数量匹配 ✓。
- 抽查内容映射：P1 BDD-35（NameError→B 类）↔ P6 BDD-35 PASS（formatter errors>0 含项目模块内 NameError 判红灯光）；P1 BDD-37（TypeError→A 类）↔ P6 BDD-37 PASS；P1 BDD-14（CRLF frontmatter）↔ P6 BDD-14 PASS。非仅数量对齐，逐条内容命中 ✓。

### 3.2 P2 packages vs P4 实际改动范围

- P2 §0 影响域 + frontmatter `packages: [agate-scripts-sh, agate-scripts-py, agate-phase-cards, agate-docs, agate-gitconfig, agate-ci, agate-tests]`（7 项）。
- P4 实际改动（git diff 03500e7..c8653b8，48 文件）：`agate-scripts-sh`（pre-commit-gate/check-gate/check-p6-evidence/check-p6-format/check-tdd-red/gate-result/install-hook/agate-next-card/agate-workspace-resolve/agate-render-dispatch-prompt）✓；`agate-scripts-py`（13 py + agate-frontmatter-check）✓；`agate-phase-cards`（P{1,2,3,4,6,7,8} 七卡）✓；`agate-docs`（SETUP.md）✓；`agate-gitconfig`（.gitignore）✓；`agate-ci`（protocol-tests.yml）✓；`agate-tests`（8 个 .bats）✓。7 项全覆盖，与 P2 声明一致 ✓。

### 3.3 P2 方案 vs P4 实现路径

- S1：P2 §1.1 候选 1A（数组化）↔ P4 §group1 S1（STAGED_STATE_FILES/PROCESSED_DIRS 数组化 + is_processed_dir 辅助函数）✓
- M9：P2 §1.6 候选 6A（grep -F + awk index 行首锚定）↔ P4 §group1 M9（awk index 两级过滤，含 SCOPE+ 的 L104/L290）✓
- M4/M5：P2 §1.4 候选 4A（bracket→alternation）↔ P4 §group1（check-gate.sh L358/359 + check-p6-format.sh 4 处）✓
- RM-AG0001：P2 §1.10 候选 10A（反引号容错）↔ P4 §group1（行首正则加 `*、sed 描述提取剥反引号）✓
- S2：P2 §1.3 候选 3A（负类加宽）↔ P4 §group1（`\([^()]*[^()[:space:]]\.[a-zA-Z0-9]+[^)]*\)`）✓
- RM-AG0002+TPV0090-M4：P2 §1.11 候选 11A ↔ P4 §group2（raw_output 关键词判定 + name_errors）✓（唯一偏差即 §1.1 DESIGN_GAP，已 REVIEWED）
- S3：P2 §1.2 候选 2A（grep 断言审计 + 批量 encoding）↔ P4 §group3a ✓
- M6：P2 §1.5 候选 5A（frontmatter 提取处 CRLF 归一，不改 .gitattributes）↔ P4 §group3a（py `_read()` replace）+ §m6-shell（8 处 sed s/\r$//）✓
- Q1：P2 §1.7 候选 7A（先试直接剥离，失败归一化）↔ P4 §group3b（rel_card + lower_drive）✓
- Q2：P2 §1.8 候选 8A（参照 P5 卡补注）↔ P4 §group3b（7 卡规则 2 语义）✓
- Q5：P2 §1.9 候选 9A ↔ P4 §group3b（SETUP Windows 章节 + .gitignore 预设）✓
- 其他-a/b/c：P2 §1.13 候选 13A/14A/15A ↔ P4 §group3b / §group1 ✓
- CI：P2 §1.12 候选 12A（windows matrix）↔ P4 §group3b（4 job matrix）✓

全部修复落在 P2 选定方案上，无方案漂移 ✓。

### 3.4 P2 gate_commands.P5 vs P5-test-results 执行命令

- P2 §4 gate_commands.P5：`bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/ && python3 agate/scripts/check-protocol-consistency.py --strict && shellcheck -S warning agate/scripts/*.sh`
- P5-test-results/unit.md §gate_commands.P5 逐条执行记录：命令 1 bats 全量 exit 0（ok=714 / not ok=0）、命令 2 consistency --strict exit 0、命令 3 shellcheck exit 0。命令文本与 P2 完全一致，三命令全部 exit 0 ✓。

### 3.5 P6 evidence 文件引用 vs P6-evidence/ 目录

- P6-acceptance.md 引用 41 个唯一 `p6-bdd-*.log`（含 25-consistency/32-full/33-ci/34-shellcheck 附加文件），逐一核对 P6-evidence/ 目录 41 个文件全部存在，无悬空引用 ✓。

## 4. 未决项清零

- P1-requirements.md：无行首 `[NEED_CONFIRM]`、`[BLOCKER]`、`[DEVIATION-CRITICAL]`、`[DESIGN_GAP]` 残留（grep exit=1，0 匹配）。§4 待确认清单以 `[NO_NEED_CONFIRM]` 声明，§5 三个 `[SUGGEST]` 已全部被 P2 采纳（M6→5A、S3→2A、RM-AG0002→11A 的 compile/error 关键词方向）。未决项清零 ✓。

## 5. 结论

- **BLOCKER=0**：P4 仅 1 条 DESIGN_GAP，P7 §1 已转抄 + 配 `[DESIGN_GAP_REVIEWED: 已确认]`，无其他阻塞项。
- **CRITICAL=0**：§3 五项跨文件检查（P1§3 BDD / P2§0 packages / P2§1 方案 / P2§4 gate_commands / P6§BDD 证据）全部通过，各引用源文件节名。
- **SCOPE+ 闭环**：§2.1 列条目 + `[SCOPE_RESOLVED]`；SCOPE_GAP（bdd-14）§2.2 记录闭环事实。
- **无 [BLOCKER] / [DEVIATION-CRITICAL]**。
- **status: approved** —— 跨文件一致，可进入 P8 发布。
